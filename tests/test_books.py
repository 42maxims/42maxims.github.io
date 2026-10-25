"""Go deeper books on maxims: schema checks in scripts/validate.py, rendering on maxim pages, Book JSON-LD, and no effect on scores.
Run after python3 build.py."""
import copy, html, json, os, re, sys, tempfile, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from validate import validate
from scoring import evidence, moral_rank

LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def load(name):
    with open(os.path.join(ROOT, "data", f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


def page(slug):
    with open(os.path.join(ROOT, "maxims", slug, "index.html"), encoding="utf-8") as f:
        return f.read()


D, V, S = load("maxims"), load("voices"), load("sources")
BOOKS = [(c, b) for c in D["concepts"] for b in c.get("books", [])]


class BookValidation(unittest.TestCase):
    GOOD = {"title": "Meditations", "author": "Marcus Aurelius", "voice": "marcus-aurelius", "source_id": "meditations",
            "where": "Book IV", "why": "Short notes to himself.", "rel": "core", "access": "free",
            "url": "https://www.gutenberg.org/ebooks/15877", "translation": "public-domain translation (George Long)", "year": 180}

    def errors_for(self, **changes):
        Dc = copy.deepcopy(D)
        b = dict(self.GOOD, **changes)
        for k, v in changes.items():
            if v is None:
                del b[k]
        Dc["concepts"][0]["books"] = [b]
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, "data"))
            for name, obj in (("maxims", Dc), ("voices", V), ("sources", S)):
                with open(os.path.join(tmp, "data", f"{name}.json"), "w", encoding="utf-8") as f:
                    json.dump(obj, f)
            return "\n".join(validate(tmp)[0])

    def test_good_book_passes(self):
        self.assertEqual(self.errors_for(), "")
        self.assertEqual(self.errors_for(voice=None, source_id=None, where=None, why=None, rel=None, translation=None, year=None), "")
        self.assertEqual(self.errors_for(url=None, access=None), "")  # a book with no link is fine
        self.assertEqual(self.errors_for(access="buy", url="https://openlibrary.org/search?q=Meditations"), "")

    def test_required_fields(self):
        self.assertIn("missing 'title'", self.errors_for(title=None))
        self.assertIn("missing 'author'", self.errors_for(author=" "))

    def test_enums_and_types(self):
        self.assertIn("rel 'must-read' must be one of core, practice, background", self.errors_for(rel="must-read"))
        self.assertIn("access 'paid' must be one of free, buy", self.errors_for(access="paid"))
        self.assertIn("year must be a whole number", self.errors_for(year="c. 180"))
        self.assertIn("unknown field(s) isbn", self.errors_for(isbn="123"))
        self.assertIn("'where' must be a non-empty string", self.errors_for(where=""))

    def test_ids_must_exist(self):
        self.assertIn("unknown voice 'nobody'", self.errors_for(voice="nobody"))
        self.assertIn("unknown source_id 'no-such-book'", self.errors_for(source_id="no-such-book"))

    def test_url_domains(self):
        self.assertIn("no Amazon", self.errors_for(access="buy", url="https://www.amazon.com/dp/0140449337"))
        self.assertIn("no Amazon", self.errors_for(access="buy", url="https://amzn.to/abc"))
        self.assertIn("a free book must link a public-domain text host", self.errors_for(url="https://example.com/meditations"))
        self.assertIn("a free book must link a public-domain text host", self.errors_for(url="https://openlibrary.org/works/OL1W"))
        self.assertIn("a modern book must link Open Library", self.errors_for(access="buy"))
        self.assertIn("url must start with https://", self.errors_for(url="http://www.gutenberg.org/ebooks/15877"))
        self.assertIn("needs 'access'", self.errors_for(access=None))
        self.assertIn("'access' needs a 'url'", self.errors_for(url=None))
        self.assertEqual(self.errors_for(url="https://en.wikisource.org/wiki/Tirukural/Chapter_11"), "")

    def test_book_left_in_links_is_flagged(self):
        Dc = copy.deepcopy(D)
        Dc["concepts"][0]["links"] = [{"url": "https://openlibrary.org/works/OL1W", "label": "Some Book (Open Library)"}]
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, "data"))
            for name, obj in (("maxims", Dc), ("voices", V), ("sources", S)):
                with open(os.path.join(tmp, "data", f"{name}.json"), "w", encoding="utf-8") as f:
                    json.dump(obj, f)
            self.assertIn("is a book; move it to 'books'", "\n".join(validate(tmp)[0]))


class BookData(unittest.TestCase):
    def test_migrated_and_filled(self):
        self.assertGreaterEqual(len(BOOKS), 28)  # every former book link, plus new entries
        for c in D["concepts"]:
            for l in c.get("links", []):
                self.assertIsInstance(l, str, f"{c['slug']}: book-style link objects belong in books")

    def test_why_is_short_and_free_books_say_how(self):
        for c, b in BOOKS:
            self.assertTrue(b.get("why"), (c["slug"], b["title"]))
            self.assertLessEqual(len(b["why"]), 220, (c["slug"], b["title"]))
            self.assertIn("url", b, (c["slug"], b["title"]))
        seen = {}
        for c, b in BOOKS:
            key = (c["slug"], b["title"], b.get("where"))
            self.assertNotIn(key, seen, "same book and place listed twice on one maxim"); seen[key] = 1


class BookRendering(unittest.TestCase):
    def test_go_deeper_section(self):
        for c in D["concepts"]:
            h = page(c["slug"])
            self.assertNotIn("Further reading", h)
            if not (c.get("books") or c.get("links")):
                self.assertNotIn("Go deeper", h)
                continue
            self.assertIn("<h2>Go deeper</h2>", h)
            # Go deeper sits after the score, where Further reading used to be
            self.assertLess(h.index("<h2>Score</h2>"), h.index("<h2>Go deeper</h2>"))
            for b in c.get("books", []):
                self.assertIn(f"<cite>{html.escape(b['title'])}</cite>", h)
                self.assertIn(html.escape(b["author"]), h)
                if b.get("where"):
                    self.assertIn(f'<p class="book-where">{html.escape(b["where"])}</p>', h)
                if b.get("why"):
                    self.assertIn(html.escape(b["why"]), h)
                label = {"free": "Read free ↗", "buy": "More info ↗"}[b["access"]]
                self.assertIn(f'href="{html.escape(b["url"])}" target="_blank" rel="noopener noreferrer"', h)
                self.assertIn(label, h)
                if b.get("source_id"):
                    self.assertIn(f'href="../../sources/{b["source_id"]}/"><cite>', h)
            for l in c.get("links", []):
                self.assertIn(f'<a href="{html.escape(l)}">', h)
                self.assertIn('<p class="label">Links</p>', h)

    def test_labels(self):
        h = page("be-present")  # Open Library book
        self.assertIn("More info ↗", h)
        self.assertNotIn("Read free ↗", h)
        h = page("master-your-anger")  # public-domain texts
        self.assertIn("Read free ↗", h)

    def test_book_structured_data(self):
        n = 0
        for c in D["concepts"]:
            if not c.get("books"):
                continue
            item = next(o for o in map(json.loads, LD.findall(page(c["slug"]))) if o["@type"] == "ItemPage")
            cites = item["mainEntity"]["citation"]
            self.assertEqual([x["name"] for x in cites], [b["title"] for b in c["books"]])
            for x, b in zip(cites, c["books"]):
                self.assertEqual(x["@type"], "Book")
                self.assertTrue("author" in x or x.get("creditText") == b["author"])
                if "/search" in b.get("url", ""):
                    self.assertNotIn("sameAs", x)
                n += 1
        self.assertEqual(n, len(BOOKS))

    def test_llms_full_lists_books(self):
        txt = open(os.path.join(ROOT, "llms-full.txt"), encoding="utf-8").read()
        self.assertIn("Go deeper (further reading, not evidence):", txt)


class BooksNeverScore(unittest.TestCase):
    def test_scores_ignore_books(self):
        """Moral Rank is computed from quotes only: stripping every book gives the same scores the build wrote."""
        qs = {}
        for q in D["quotes"]:
            qs.setdefault(q["concept"], []).append(q)
        E = {c["slug"]: evidence(qs.get(c["slug"], []), D["traditions"])[0] for c in D["concepts"]}
        mr, _ = moral_rank(E, [])
        built = load("generated/scores")
        for s, v in mr.items():
            self.assertAlmostEqual(built[s]["moral_rank"], round(v, 1), places=6)
        import scoring
        src = open(scoring.__file__, encoding="utf-8").read()
        self.assertNotIn("books", src)


if __name__ == "__main__":
    unittest.main()
