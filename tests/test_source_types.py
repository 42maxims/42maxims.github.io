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

    def test_chips_are_links(self):
        # type chip on every source row links to its section; no-JS falls back to the anchor
        for kind, a in (("book", "books"), ("scripture", "scripture"), ("talk", "talks")):
            sec = re.search(rf'data-type="{kind}">(.*?)</section>', self.idx, re.S).group(1)
            self.assertIn(f'class="chip chip-link" href="#{a}" data-go="{a}"', sec)
        vid = re.search(r'data-type="video">(.*?)</section>', self.idx, re.S).group(1)
        self.assertIn('href="#videos" data-go="videos"', vid)
        # voice-page channels link to the voice; the rest filter by channel with a no-JS anchor to the first row
        self.assertIn('href="../voices/andrew-huberman/">Andrew Huberman</a>', vid)
        self.assertIn('href="../voices/jordan-peterson/">Jordan B Peterson</a>', vid)
        self.assertIn('href="#channel-chris-williamson" data-chan="chris-williamson"', vid)
        self.assertEqual(vid.count('id="channel-chris-williamson"'), 1)
        for m in re.finditer(r'data-chan="([^"]+)"', vid):
            self.assertIn(f'id="channel-{m.group(1)}"', vid)

    def test_voice_links_resolve(self):
        for m in re.finditer(r'href="\.\./voices/([a-z0-9-]+)/"', self.idx):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "voices", m.group(1), "index.html")), m.group(1))

    def test_single_control_set_when_js_on(self):
        # JS hides the anchor row and keeps filter state in the hash
        self.assertIn("j.hidden=true;f.hidden=false", self.idx)
        self.assertIn("location.hash", self.idx)
        self.assertIn("aria-pressed", self.idx)


if __name__ == "__main__":
    unittest.main()
