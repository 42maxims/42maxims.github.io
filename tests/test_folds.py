"""Tradition folds under "Related expressions" on maxim pages: one visible quote per tradition, the rest in a <details>
"More from X (N)", the seed never repeated, every quote still in the HTML and JSON-LD. Run after python3 build.py."""
import html, json, os, re, shutil, subprocess, sys, tempfile, unittest
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from scoring import VER, REL

with open(os.path.join(ROOT, "data", "maxims.json"), encoding="utf-8") as f:
    D = json.load(f)
TR = D["traditions"]
ERA_ORDER = ["axial", "classical", "medieval", "early-modern", "modern", "contemporary"]
VER_ORDER = ["verified", "probable", "disputed", "unverified", "misattributed"]
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
ITEM = re.compile(r'<li class="fold"><details><summary>(.*?)</summary>|</details></li>|<li><blockquote>“(.*?)”</blockquote>.*?'
                  r'<div class="meta"><span><a href="\.\./\.\./traditions/([^/]+)/">', re.S)


def quotes_of(data, slug):
    return [q for q in data["quotes"] if q["concept"] == slug]


def key(q, i):
    return (-VER[q["ver"]] * REL[q["rel"]] * q["conf"], ERA_ORDER.index(q["era"]), i)


def seed_index(c, qs):
    s = c.get("seed")
    if isinstance(s, int) and 0 <= s < len(qs):
        return s
    return min(range(len(qs)), key=lambda i: (ERA_ORDER.index(qs[i]["era"]), VER_ORDER.index(qs[i]["ver"]), i))


def expected(c, qs):
    """[(tradition, visible text or None, [folded texts])] in page order, derived from the data alone."""
    si = seed_index(c, qs); groups = {}
    for i, q in enumerate(qs):
        if i != si:
            groups.setdefault(q["tradition"], []).append((key(q, i), q["text"]))
    out = []
    for t, g in sorted(groups.items(), key=lambda x: min(x[1])):
        texts = [x for _, x in sorted(g)]
        if len(texts) == 1:
            out.append((t, texts[0], []))
        elif t == qs[si]["tradition"]:
            out.append((t, None, texts))
        else:
            out.append((t, texts[0], texts[1:]))
    return out


def related(h):
    """Parse the Related expressions list into [(tradition, visible text or None, [folded texts], summary or None)]."""
    sec = h.split("<h2>Related expressions</h2>", 1)[1].split("<h2>Score</h2>", 1)[0]
    out, fold = [], None
    for m in ITEM.finditer(sec):
        if m.group(1) is not None:
            fold = [html.unescape(m.group(1)), []]
        elif m.group(0) == "</details></li>":
            name = re.match(r"More from (.*) \(\d+\)$", fold[0]).group(1)
            t = next(k for k, v in TR.items() if v["name"] == name)
            if out and out[-1][0] == t and not out[-1][2]:
                out[-1] = (t, out[-1][1], fold[1], fold[0])
            else:
                out.append((t, None, fold[1], fold[0]))
            fold = None
        else:
            txt, t = html.unescape(m.group(2)), m.group(3)
            if fold is not None:
                fold[1].append(txt)
            else:
                out.append((t, txt, [], None))
    return out


def read(root, slug):
    with open(os.path.join(root, "maxims", slug, "index.html"), encoding="utf-8") as f:
        return f.read()


MAXIMS = [(c, quotes_of(D, c["slug"])) for c in D["concepts"]]
MAXIMS = [(c, qs) for c, qs in MAXIMS if len(qs) > 1]


class Folds(unittest.TestCase):
    def test_layout_matches_rule(self):
        for c, qs in MAXIMS:
            with self.subTest(maxim=c["slug"]):
                got = related(read(ROOT, c["slug"]))
                self.assertEqual([g[:3] for g in got], expected(c, qs))

    def test_one_visible_quote_per_tradition(self):
        for c, qs in MAXIMS:
            with self.subTest(maxim=c["slug"]):
                got = related(read(ROOT, c["slug"]))
                ts = [t for t, *_ in got]
                self.assertEqual(len(ts), len(set(ts)))
                seed_t = qs[seed_index(c, qs)]["tradition"]
                for t, vis, fold, _ in got:
                    if t == seed_t and fold:
                        self.assertIsNone(vis)  # the seed is that tradition's visible quote
                    elif t != seed_t:
                        self.assertIsNotNone(vis)

    def test_summary_text_and_count(self):
        seen = 0
        for c, qs in MAXIMS:
            for t, vis, fold, summary in related(read(ROOT, c["slug"])):
                if fold:
                    seen += 1
                    self.assertEqual(summary, f'More from {TR[t]["name"]} ({len(fold)})')
                    self.assertGreaterEqual(len(fold) + (vis is not None), 2)
        self.assertGreater(seen, 0)
        h = read(ROOT, "golden-rule")
        self.assertIn("<summary>More from Christianity (1)</summary>", h)

    def test_single_quote_traditions_have_no_fold(self):
        for c, qs in MAXIMS:
            si = seed_index(c, qs)
            n = Counter(q["tradition"] for i, q in enumerate(qs) if i != si)
            with self.subTest(maxim=c["slug"]):
                for t, vis, fold, summary in related(read(ROOT, c["slug"])):
                    if n[t] == 1:
                        self.assertEqual((fold, summary), ([], None))
                        self.assertIsNotNone(vis)
                h = read(ROOT, c["slug"])
                self.assertEqual(h.count("<details>"), sum(1 for k in n.values() if k > 1))

    def test_seed_not_duplicated(self):
        for c, qs in MAXIMS:
            with self.subTest(maxim=c["slug"]):
                si = seed_index(c, qs)
                shown = [x for _, vis, fold, _ in related(read(ROOT, c["slug"])) for x in ([vis] if vis else []) + fold]
                self.assertEqual(Counter(shown), Counter(q["text"] for i, q in enumerate(qs) if i != si))

    def test_every_quote_in_html_and_jsonld(self):
        for c in D["concepts"]:
            qs = quotes_of(D, c["slug"])
            with self.subTest(maxim=c["slug"]):
                h = read(ROOT, c["slug"])
                texts = Counter(html.unescape(t) for t in re.findall(r"<blockquote>“(.*?)”</blockquote>", h, re.S))
                self.assertEqual(texts, Counter(q["text"] for q in qs))
                item = next(b for b in map(json.loads, LD.findall(h)) if b.get("@type") == "ItemPage")
                parts = [p["text"] for p in item["mainEntity"]["hasPart"]]
                self.assertEqual(Counter(parts), Counter(q["text"] for q in qs if q["ver"] in ("verified", "probable")))
                page_order = [t for t in (html.unescape(t) for t in re.findall(r"<blockquote>“(.*?)”</blockquote>", h, re.S)) if t in parts]
                self.assertEqual(parts, page_order)

    def test_no_javascript_in_folds(self):
        for c, _ in MAXIMS:
            for d in re.findall(r"<details>.*?</details>", read(ROOT, c["slug"]), re.S):
                self.assertNotIn("onclick", d); self.assertNotIn(" open", d)


class Deterministic(unittest.TestCase):
    """Builds two copies: same data twice (identical maxim pages), and with every concept's quotes in reverse file order
    (selection still follows the rule, so ties fall to the new file order)."""
    @classmethod
    def setUpClass(cls):
        cls.dirs = []
        rev = json.loads(json.dumps(D))
        rev["quotes"] = rev["quotes"][::-1]
        for c in rev["concepts"]:
            c.pop("seed", None)  # seed indices point into file order
        cls.rev = rev
        for data in (D, rev):
            tmp = tempfile.mkdtemp(); cls.dirs.append(tmp)
            for f in ("build.py", "scoring.py"):
                shutil.copy(os.path.join(ROOT, f), tmp)
            shutil.copytree(os.path.join(ROOT, "data"), os.path.join(tmp, "data"))
            with open(os.path.join(tmp, "data", "maxims.json"), "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            subprocess.run([sys.executable, os.path.join(tmp, "build.py")], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        for d in cls.dirs:
            shutil.rmtree(d)

    def test_rebuild_is_identical(self):
        for c, _ in MAXIMS:
            with self.subTest(maxim=c["slug"]):
                self.assertEqual(read(self.dirs[0], c["slug"]), read(ROOT, c["slug"]))

    def test_ties_follow_file_order(self):
        for c in self.rev["concepts"]:
            qs = quotes_of(self.rev, c["slug"])
            if len(qs) > 1:
                with self.subTest(maxim=c["slug"]):
                    self.assertEqual([g[:3] for g in related(read(self.dirs[1], c["slug"]))], expected(c, qs))


if __name__ == "__main__":
    unittest.main()
