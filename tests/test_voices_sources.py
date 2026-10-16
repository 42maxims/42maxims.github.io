"""Voices and sources data: every quote links to both, every entry is complete, and the build emits and links their pages."""
import html, json, os, re, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load = lambda name: json.load(open(os.path.join(ROOT, "data", name)))
D, VOICES, SOURCES = load("maxims.json"), load("voices.json"), load("sources.json")
ERAS = {"axial", "classical", "medieval", "early-modern", "modern", "contemporary"}
CONFIDENCE = {"solid", "thin", "uncertain"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
COMMON = ("dates", "tradition", "period", "summary", "confidence", "refs")


class Data(unittest.TestCase):
    def test_quotes_link_to_voice_and_source(self):
        for i, q in enumerate(D["quotes"]):
            with self.subTest(quote=i, thinker=q["thinker"]):
                self.assertIn(q.get("voice"), VOICES)
                self.assertIn(q.get("source_id"), SOURCES)

    def check_common(self, e):
        for f in COMMON:
            self.assertIn(f, e)
        self.assertTrue(e["dates"].strip())
        self.assertIn(e["tradition"], D["traditions"])
        self.assertIn(e["period"], ERAS)
        self.assertIn(e["confidence"], CONFIDENCE)
        self.assertGreater(len(e["summary"].strip()), 40)
        self.assertIsInstance(e["refs"], list)
        self.assertTrue(e["refs"], "needs at least one reference")
        for u in e["refs"]:
            self.assertTrue(u.startswith("https://"), u)

    def test_voices_complete(self):
        for slug, v in VOICES.items():
            with self.subTest(voice=slug):
                self.assertRegex(slug, SLUG)
                self.assertTrue(v.get("name", "").strip())
                self.assertIn(v.get("kind"), {"person", "collective", "scripture", "legendary"})
                self.assertIn(v.get("label", "Scripture"), {"Scripture"})
                self.check_common(v)

    def test_scripture_voices_labelled(self):
        for slug in ("qoheleth", "author-of-job", "author-of-joshua", "author-of-hebrews", "quran"):
            self.assertEqual(VOICES[slug]["kind"], "scripture", slug)
        for slug in ("psalmists", "torah-writers", "hebrew-wisdom-writers", "zechariah", "micah"):
            self.assertEqual(VOICES[slug].get("label"), "Scripture", slug)
        self.assertNotIn("text", {v["kind"] for v in VOICES.values()})

    def test_sources_complete(self):
        for slug, s in SOURCES.items():
            with self.subTest(source=slug):
                self.assertRegex(slug, SLUG)
                self.assertTrue(s.get("title", "").strip())
                self.assertIn(s.get("kind"), {"book", "scripture", "talk", "article", "other"})
                self.assertIn("voice", s)
                self.assertTrue(s["voice"] is None or s["voice"] in VOICES, s["voice"])
                self.check_common(s)

    def test_every_entry_used(self):
        used_v = {q["voice"] for q in D["quotes"]} | {s["voice"] for s in SOURCES.values() if s["voice"]}
        self.assertEqual(set(VOICES) - used_v, set(), "voices with no quotes and no works")
        self.assertEqual(set(SOURCES) - {q["source_id"] for q in D["quotes"]}, set(), "sources with no quotes")


class Build(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        for f in ("build.py", "scoring.py"):
            shutil.copy(os.path.join(ROOT, f), cls.tmp)
        shutil.copytree(os.path.join(ROOT, "data"), os.path.join(cls.tmp, "data"))
        subprocess.run([sys.executable, os.path.join(cls.tmp, "build.py")], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def read(self, rel):
        return open(os.path.join(self.tmp, rel), encoding="utf-8").read()

    def test_pages_exist(self):
        idx_v, idx_s = self.read("voices/index.html"), self.read("sources/index.html")
        for slug, v in VOICES.items():
            self.assertIn(f'href="{slug}/"', idx_v)
            self.assertIn(html.escape(v["summary"]), self.read(f"voices/{slug}/index.html"))
        for slug, s in SOURCES.items():
            self.assertIn(f'href="{slug}/"', idx_s)
            self.assertIn(html.escape(s["summary"]), self.read(f"sources/{slug}/index.html"))

    def test_nav_links(self):
        home = self.read("index.html")
        self.assertIn('href="voices/"', home)
        self.assertIn('href="sources/"', home)
        self.assertIn('href="../../voices/"', self.read("voices/confucius/index.html"))

    def test_maxim_pages_link_voices_and_sources(self):
        for q in D["quotes"]:
            page = self.read(f"maxims/{q['concept']}/index.html")
            self.assertIn(f'href="../../voices/{q["voice"]}/"', page)
            self.assertIn(f'href="../../sources/{q["source_id"]}/"', page)

    def test_detail_pages_list_their_quotes(self):
        for q in D["quotes"]:
            for rel in (f"voices/{q['voice']}/index.html", f"sources/{q['source_id']}/index.html"):
                page = self.read(rel)
                self.assertIn(f'href="../../maxims/{q["concept"]}/"', page)
                self.assertIn(f'pill v-{q["ver"]}', page)


if __name__ == "__main__":
    unittest.main()
