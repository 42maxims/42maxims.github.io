"""Structured data (schema.org JSON-LD), server-rendered quotes and intent-based titles. Run after python3 build.py."""
import html, json, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://42maxims.com"
D = json.load(open(os.path.join(ROOT, "data/maxims.json"), encoding="utf-8"))
VOICES = json.load(open(os.path.join(ROOT, "data/voices.json"), encoding="utf-8"))
SOURCES = json.load(open(os.path.join(ROOT, "data/sources.json"), encoding="utf-8"))
LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
LICENSE = "https://creativecommons.org/licenses/by-sa/4.0/"


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def blocks(rel):
    return [json.loads(x) for x in LD.findall(read(rel))]


def walk(o):
    yield o
    if isinstance(o, dict):
        for v in o.values():
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


def all_html():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("tests", "tools", "data", "__pycache__")]
        for f in files:
            if f.endswith(".html"):
                yield os.path.relpath(os.path.join(base, f), ROOT)


class StructuredData(unittest.TestCase):
    def test_every_block_is_well_formed_and_honest(self):
        n = 0
        for rel in all_html():
            for raw in LD.findall(read(rel)):
                with self.subTest(page=rel):
                    o = json.loads(raw)  # well-formed JSON
                    self.assertEqual(o["@context"], "https://schema.org")
                    self.assertTrue(o["@type"])
                    self.assertNotIn("</", raw)  # escaped, cannot close the script tag early
                    for x in walk(o):
                        if isinstance(x, dict):
                            self.assertFalse({"aggregateRating", "review", "reviewRating", "ratingValue"} & set(x), rel)
                            if "@type" in x:
                                self.assertIsInstance(x["@type"], str)
                            for k in ("url", "@id", "contentUrl"):
                                if k in x:
                                    self.assertTrue(x[k].startswith(SITE + "/"), (rel, x[k]))
                n += 1
        self.assertGreater(n, 300)

    def test_homepage_website_dataset_and_list(self):
        site, ds, lst = blocks("index.html")
        self.assertEqual(site["@type"], "WebSite")
        self.assertEqual(site["publisher"], {"@type": "Organization", "@id": SITE + "/#publisher", "name": "42 Maxims", "url": SITE + "/"})
        self.assertEqual(ds["@type"], "Dataset")
        self.assertEqual(ds["license"], LICENSE)
        self.assertTrue(50 <= len(ds["description"]) <= 5000)
        self.assertIn("quotes remain the property of their authors and translators", ds["description"])
        self.assertEqual(ds["publisher"], {"@id": SITE + "/#publisher"})
        for d in ds["distribution"]:
            self.assertEqual(d["@type"], "DataDownload")
            self.assertTrue(os.path.isfile(os.path.join(ROOT, d["contentUrl"][len(SITE) + 1:])), d["contentUrl"])
            json.loads(read(d["contentUrl"][len(SITE) + 1:]))
        self.assertEqual(lst["@type"], "ItemList")
        self.assertEqual(lst["numberOfItems"], 42)
        for x in walk([site, ds, lst]):
            if isinstance(x, dict):
                self.assertNotEqual(x.get("@type"), "Person")  # the project is anonymous

    def test_maxim_pages_carry_their_quotes(self):
        by = {}
        for q in D["quotes"]:
            by.setdefault(q["concept"], []).append(q)
        for c in D["concepts"]:
            rel = f"maxims/{c['slug']}/index.html"
            with self.subTest(maxim=c["slug"]):
                page = [b for b in blocks(rel) if b["@type"] == "ItemPage"]
                self.assertEqual(len(page), 1)
                p = page[0]
                self.assertEqual(p["url"], f"{SITE}/maxims/{c['slug']}/")
                self.assertEqual(p["license"], LICENSE)
                main = p["mainEntity"]
                self.assertEqual(main["name"], c["maxim"])
                qs = by.get(c["slug"], [])
                trusted = [q for q in qs if q["ver"] in ("verified", "probable")]
                parts = main["hasPart"]
                self.assertEqual(sorted(x["text"] for x in parts), sorted(q["text"] for q in trusted))
                for x, q in zip(sorted(parts, key=lambda x: x["text"]), sorted(trusted, key=lambda q: q["text"])):
                    self.assertEqual(x["@type"], "Quotation")
                    self.assertEqual(x["isPartOf"]["url"], f"{SITE}/sources/{q['source_id']}/")
                    self.assertIn(D["traditions"][q["tradition"]]["name"], x["keywords"])
                    if "creator" in x:
                        self.assertIn(VOICES[q["voice"]]["kind"], ("person", "legendary"))
                        self.assertEqual(x["creator"]["@type"], "Person")
                for q in qs:
                    if q["ver"] in ("unverified", "misattributed", "disputed"):
                        self.assertNotIn(q["text"], [x["text"] for x in parts])

    def test_voice_and_source_pages(self):
        for slug, v in VOICES.items():
            b = [x for x in blocks(f"voices/{slug}/index.html") if x["@type"] != "BreadcrumbList"]
            if not b:
                continue  # noindex pages carry no structured data
            with self.subTest(voice=slug):
                if v["kind"] in ("person", "legendary"):
                    self.assertEqual(b[0]["@type"], "ProfilePage")
                    self.assertEqual(b[0]["mainEntity"]["@type"], "Person")
                    self.assertEqual(b[0]["mainEntity"]["name"], v["name"])
                else:
                    self.assertEqual(b[0]["@type"], "WebPage")
                    self.assertNotIn("mainEntity", b[0])
        for slug, s in SOURCES.items():
            b = [x for x in blocks(f"sources/{slug}/index.html") if x["@type"] != "BreadcrumbList"]
            if not b:
                continue
            with self.subTest(source=slug):
                self.assertIn(b[0]["mainEntity"]["@type"], ("Book", "CreativeWork", "Article"))
                self.assertEqual(b[0]["mainEntity"]["name"], s["title"])
                for u in b[0]["mainEntity"].get("sameAs", []):
                    self.assertIn(u, s["refs"])


class ServerRendered(unittest.TestCase):
    def test_every_quote_is_in_the_static_html_of_its_maxim_page(self):
        for q in D["quotes"]:
            h = LD.sub("", read(f"maxims/{q['concept']}/index.html"))
            h = re.sub(r"<script>.*?</script>", "", h, flags=re.S)
            with self.subTest(concept=q["concept"], text=q["text"][:40]):
                self.assertIn(f"<blockquote>“{html.escape(q['text'])}”</blockquote>", h)


class Titles(unittest.TestCase):
    def test_maxim_titles_are_intent_based_without_ranks(self):
        for c in D["concepts"]:
            h = read(f"maxims/{c['slug']}/index.html")
            title = html.unescape(re.search(r"<title>(.*?)</title>", h).group(1))
            with self.subTest(maxim=c["slug"]):
                self.assertTrue(title.startswith(c["maxim"].rstrip(".")))
                self.assertRegex(title, r" — (what \d+ traditions say|quotes and sources)( \| 42 Maxims)?$|^.* \| 42 Maxims$")
                self.assertNotRegex(title, r"#\d|Moral Rank|\brank", "ranks shift; keep them out of titles")
                self.assertIn(f'<h1 class="maxim">{html.escape(c["maxim"])}</h1>', h)  # readable H1 unchanged

    def test_tradition_count_in_title_matches_scores(self):
        scores = json.loads(read("data/generated/scores.json"))
        for c in D["concepts"]:
            m = re.search(r"what (\d+) traditions say", read(f"maxims/{c['slug']}/index.html").split("</title>")[0])
            if m:
                self.assertEqual(int(m.group(1)), scores[c["slug"]]["traditions"], c["slug"])


if __name__ == "__main__":
    unittest.main()
