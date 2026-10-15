"""Plausible analytics: off by default, emitted in <head> of every page when PLAUSIBLE_DOMAIN is set."""
import glob, os, re, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAKE = "analytics-test.example.org"


def build(domain):
    tmp = tempfile.mkdtemp()
    for f in ("build.py", "scoring.py"):
        shutil.copy(os.path.join(ROOT, f), tmp)
    shutil.copytree(os.path.join(ROOT, "data"), os.path.join(tmp, "data"))
    p = os.path.join(tmp, "build.py")
    src = open(p).read()
    src = re.sub(r'^PLAUSIBLE_DOMAIN = ""', f'PLAUSIBLE_DOMAIN = "{domain}"', src, count=1, flags=re.M)
    open(p, "w").write(src)
    r = subprocess.run([sys.executable, p], capture_output=True, text=True)
    return tmp, r


def pages(tmp):
    return glob.glob(os.path.join(tmp, "**", "index.html"), recursive=True)


class Plausible(unittest.TestCase):
    def test_default_empty_and_no_script(self):
        self.assertIn('PLAUSIBLE_DOMAIN = ""', open(os.path.join(ROOT, "build.py")).read())
        for f in pages(ROOT):
            self.assertNotIn("plausible", open(f).read().lower(), f)

    def test_empty_emits_nothing(self):
        tmp, r = build("")
        self.addCleanup(shutil.rmtree, tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(pages(tmp))
        for f in pages(tmp):
            self.assertNotIn("plausible", open(f).read().lower())

    def test_set_emits_on_every_page(self):
        tmp, r = build(FAKE)
        self.addCleanup(shutil.rmtree, tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        tag = f'<script defer data-domain="{FAKE}" src="https://plausible.io/js/script.js"></script>'
        self.assertTrue(pages(tmp))
        for f in pages(tmp):
            h = open(f).read()
            self.assertEqual(h.count(tag), 1, f)
            self.assertLess(h.index(tag), h.index("</head>"), f)

    def test_invalid_domain_rejected(self):
        for bad in ('https://x.org', 'a b.org', 'nodots', '"><script>'):
            tmp, r = build(bad.replace('"', ''))
            shutil.rmtree(tmp)
            self.assertNotEqual(r.returncode, 0, bad)


if __name__ == "__main__":
    unittest.main()
