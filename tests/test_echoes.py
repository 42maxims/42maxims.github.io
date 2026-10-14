"""Optional quote field "echoes": a short note shown on maxim, voice and source pages."""
import html, json, os, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "maxims.json")))
PROBE = "Probe saying, Test 1:1"


class Data(unittest.TestCase):
    def test_echoes_is_short_text(self):
        for i, q in enumerate(D["quotes"]):
            if "echoes" in q:
                with self.subTest(quote=i, thinker=q["thinker"]):
                    self.assertIsInstance(q["echoes"], str)
                    self.assertTrue(q["echoes"].strip())
                    self.assertLessEqual(len(q["echoes"]), 120)


class Build(unittest.TestCase):
    """Builds a copy of the site with echoes on every quote (plus a probe on two of them) and checks each page shows them."""
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        for f in ("build.py", "scoring.py"):
            shutil.copy(os.path.join(ROOT, f), cls.tmp)
        shutil.copytree(os.path.join(ROOT, "data"), os.path.join(cls.tmp, "data"))
        data = json.loads(json.dumps(D))
        concept = data["quotes"][0]["concept"]
        same = [q for q in data["quotes"] if q["concept"] == concept]
        cls.probed = same[:2]  # the seed and a related quote are both among these
        for q in same:
            q["echoes"] = PROBE
        cls.quotes = [q for q in data["quotes"] if q.get("echoes")]
        json.dump(data, open(os.path.join(cls.tmp, "data", "maxims.json"), "w"))
        subprocess.run([sys.executable, os.path.join(cls.tmp, "build.py")], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def read(self, rel):
        return open(os.path.join(self.tmp, rel), encoding="utf-8").read()

    def test_note_on_maxim_voice_and_source_pages(self):
        for q in self.quotes:
            note = f'<div class="echoes">Echoes {html.escape(q["echoes"])}</div>'
            for rel in (f"maxims/{q['concept']}/index.html", f"voices/{q['voice']}/index.html", f"sources/{q['source_id']}/index.html"):
                with self.subTest(page=rel):
                    self.assertIn(note, self.read(rel))

    def test_seed_and_related_both_show_it(self):
        page = self.read(f"maxims/{self.probed[0]['concept']}/index.html")
        seed, rest = page.split("Related expressions", 1)
        self.assertIn(f"Echoes {PROBE}", seed)
        self.assertIn(f"Echoes {PROBE}", rest)

    def test_absent_without_field(self):
        with_note = {q["concept"] for q in self.quotes}
        plain = next(c["slug"] for c in D["concepts"] if c["slug"] not in with_note)
        self.assertNotIn('class="echoes"', self.read(f"maxims/{plain}/index.html"))


if __name__ == "__main__":
    unittest.main()
