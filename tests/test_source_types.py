import json, os, re, unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
D = json.load(open(os.path.join(ROOT, "data", "maxims.json")))
SOURCES = json.load(open(os.path.join(ROOT, "data", "sources.json")))
TYPES = {"book", "scripture", "talk", "article", "other"}


class SourceTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.idx = open(os.path.join(ROOT, "sources", "index.html"), encoding="utf-8").read()

    def test_every_source_has_valid_type(self):
        for slug, s in SOURCES.items():
            self.assertIn(s.get("kind"), TYPES, slug)

    def test_every_source_listed_in_its_type_section(self):
        for slug, s in SOURCES.items():
            sec = re.search(rf'<section class="type-group" id="[a-z]+" data-type="{s["kind"]}">(.*?)</section>', self.idx, re.S)
            self.assertIsNotNone(sec, s["kind"])
            self.assertIn(f'href="{slug}/"', sec.group(1), slug)

    def test_every_video_listed_once(self):
        ids = {c["id"] for q in D["quotes"] for c in q.get("clips", [])}
        sec = re.search(r'data-type="video">(.*?)</section>', self.idx, re.S).group(1)
        for i in ids:
            self.assertEqual(sec.count(f"watch?v={i}"), 1, i)
        self.assertEqual(len(re.findall(r"<li>", sec)), len(ids))

    def test_filter_markup(self):
        self.assertIn('id="type-jump"', self.idx)  # no-JS anchors
        self.assertRegex(self.idx, r'<div id="type-filter"[^>]* hidden>')  # shown by JS only
        self.assertIn('aria-pressed="true"', self.idx)
        for a in ("books", "scripture", "talks", "articles", "sayings", "videos"):
            self.assertIn(f'href="#{a}"', self.idx)
            self.assertIn(f'id="{a}"', self.idx)
        self.assertNotIn("youtube.com/embed", self.idx)
        self.assertNotIn("<iframe", self.idx)


if __name__ == "__main__":
    unittest.main()
