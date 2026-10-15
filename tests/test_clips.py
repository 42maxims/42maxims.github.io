"""Optional quote field "clips" (YouTube clips): data validation and rendering. Run after python3 build.py."""
import html, json, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "maxims.json")))
ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
REQ = ("id", "start", "end", "label", "title", "channel")


def problems(cl):
    """Return a list of what is wrong with one clip record (empty = fine)."""
    bad = [k for k in REQ if k not in cl]
    if bad:
        return [f"missing {bad}"]
    out = []
    if not (isinstance(cl["id"], str) and ID.match(cl["id"])):
        out.append("id must be an 11-character YouTube id")
    for k in ("start", "end"):
        if not (isinstance(cl[k], int) and not isinstance(cl[k], bool) and cl[k] >= 0):
            out.append(f"{k} must be a non-negative integer (seconds)")
    if not out and cl["start"] >= cl["end"]:
        out.append("start must be before end")
    if not out and cl["end"] - cl["start"] > 120:
        out.append("clips are short: 120 seconds at most")
    if "kind" in cl and cl["kind"] not in ("verbatim", "paraphrase", "discussed"):
        out.append("kind must be verbatim, paraphrase or discussed")
    for k in ("label", "title", "channel"):
        if not (isinstance(cl[k], str) and cl[k].strip()):
            out.append(f"{k} must be non-empty text")
    return out


class Data(unittest.TestCase):
    def test_clips_valid(self):
        n = 0
        for i, q in enumerate(D["quotes"]):
            if "clips" in q:
                self.assertIsInstance(q["clips"], list); self.assertTrue(q["clips"], i)
                self.assertEqual(q["ver"], "verified", f"quote {i}: clips only on verified quotes")
                for cl in q["clips"]:
                    n += 1; self.assertEqual(problems(cl), [], f"quote {i}")
        self.assertGreaterEqual(n, 9)

    def test_discussed_clips_are_flagged(self):
        """Third-party uploads that only discuss the line must say so; verbatim clips must be the exact words."""
        for q in D["quotes"]:
            for cl in q.get("clips", []):
                if cl["channel"] in ("JBProbe", "ManOfAllCreation"):
                    self.assertEqual(cl.get("kind"), "discussed", cl["id"])

    def test_validator_rejects_malformed(self):
        good = {"id": "ljqra3BcqWM", "start": 731, "end": 737, "label": "L", "title": "T", "channel": "C"}
        self.assertEqual(problems(good), [])
        for patch in ({"id": "short"}, {"id": "bad id!!!!!!"}, {"start": 737}, {"start": 800}, {"start": "731"}, {"end": 737.5},
                      {"start": True}, {"start": -1}, {"end": 9999}, {"title": " "}, {"channel": ""}, {"kind": "official"}):
            self.assertTrue(problems({**good, **patch}), patch)
        for k in REQ:
            self.assertTrue(problems({a: b for a, b in good.items() if a != k}), k)


class Pages(unittest.TestCase):
    def test_clip_rendered_on_maxim_and_voice_pages(self):
        for q in (x for x in D["quotes"] if x.get("clips")):
            for path in (f"maxims/{q['concept']}", f"voices/{q['voice']}", f"sources/{q['source_id']}"):
                h = open(os.path.join(ROOT, path, "index.html"), encoding="utf-8").read()
                for cl in q["clips"]:
                    i, a, b = cl["id"], cl["start"], cl["end"]
                    self.assertIn(f'href="https://www.youtube.com/watch?v={i}&amp;t={a}"', h, path)
                    link = re.search(r'<a href="https://www\.youtube\.com/watch\?v=%s[^>]*>' % i, h).group(0)
                    self.assertIn('target="_blank"', link); self.assertIn('rel="noopener noreferrer"', link)
                    self.assertIn(f'data-src="https://www.youtube-nocookie.com/embed/{i}?start={a}&amp;end={b}&amp;rel=0&amp;modestbranding=1&amp;controls=1', h, path)
                    self.assertIn(f"Watch on YouTube ({a//60}:{a%60:02d}–{b//60}:{b%60:02d}) ↗", h)
                    self.assertNotIn("Hear it spoken", h)
                    self.assertNotIn("Go deeper", h); self.assertNotIn("clip-credit", h)
                    if i == "ljqra3BcqWM":
                        self.assertNotIn("Amara", h) if not path.startswith("sources/") else self.assertIn("Amara", h)

    def test_kind_labels(self):
        h = open(os.path.join(ROOT, "sources", "12-rules-for-life", "index.html"), encoding="utf-8").read()
        self.assertEqual(h.count("discusses this rule (fan upload)"), 5)
        self.assertEqual(h.count('class="clip-play"'), 5)
        w = open(os.path.join(ROOT, "maxims", "be-present", "index.html"), encoding="utf-8").read()
        self.assertIn("Spoken as a close paraphrase", w)
        g = open(os.path.join(ROOT, "maxims", "own-your-mistakes", "index.html"), encoding="utf-8").read()
        self.assertNotIn("clip-note", g.split("<style")[-1].split("</style>")[-1])

    def test_nothing_from_youtube_loads_on_page_load(self):
        for root, _, files in os.walk(ROOT):
            if ".git" in root or "tests" in root:
                continue
            for f in files:
                if f.endswith(".html"):
                    h = open(os.path.join(root, f), encoding="utf-8").read()
                    self.assertNotRegex(h, r"<iframe", f)
                    self.assertNotRegex(h, r"<(?:img|script|link)[^>]+(?:youtube\.com|ytimg\.com|youtube-nocookie\.com)", f)
                    for s in re.findall(r'<script[^>]*\ssrc="([^"]+)"', h):
                        self.assertTrue(s.startswith("https://plausible.io/"), (f, s))

    def test_pages_without_clips_have_no_clip_markup(self):
        h = open(os.path.join(ROOT, "maxims", "golden-rule", "index.html"), encoding="utf-8").read()
        self.assertNotIn('class="clip"', h); self.assertNotIn("clip-play", h)


if __name__ == "__main__":
    unittest.main()
