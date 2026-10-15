"""Plausible analytics: owner's snippet emitted in <head> of every page; empty id emits nothing."""
import glob, os, re, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER_ID = "pa-z7AY9FcQwVk1RWlwwy4-D"
SNIPPET = """<!-- Privacy-friendly analytics by Plausible -->
<script async src="https://plausible.io/js/pa-z7AY9FcQwVk1RWlwwy4-D.js"></script>
<script>
  window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};
  plausible.init()
</script>
"""


def build(sid):
    tmp = tempfile.mkdtemp()
    for f in ("build.py", "scoring.py"):
        shutil.copy(os.path.join(ROOT, f), tmp)
    shutil.copytree(os.path.join(ROOT, "data"), os.path.join(tmp, "data"))
    p = os.path.join(tmp, "build.py")
    src = open(p).read()
    src = re.sub(r'^PLAUSIBLE_SCRIPT_ID = "[^"]*"', lambda m: f'PLAUSIBLE_SCRIPT_ID = "{sid}"', src, count=1, flags=re.M)
    open(p, "w").write(src)
    r = subprocess.run([sys.executable, p], capture_output=True, text=True)
    return tmp, r


def pages(tmp):
    return glob.glob(os.path.join(tmp, "**", "index.html"), recursive=True)


class Plausible(unittest.TestCase):
    def test_committed_pages_have_snippet(self):
        self.assertIn(f'PLAUSIBLE_SCRIPT_ID = "{OWNER_ID}"', open(os.path.join(ROOT, "build.py")).read())
        self.assertTrue(pages(ROOT))
        for f in pages(ROOT):
            h = open(f).read()
            self.assertEqual(h.count(SNIPPET), 1, f)
            self.assertLess(h.index(SNIPPET), h.index("</head>"), f)

    def test_empty_emits_nothing(self):
        tmp, r = build("")
        self.addCleanup(shutil.rmtree, tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(pages(tmp))
        for f in pages(tmp):
            self.assertNotIn("plausible", open(f).read().lower())

    def test_invalid_id_rejected(self):
        for bad in ("x.js", "pa-", "pa-a b", "pa-a/b", "PA-abc"):
            tmp, r = build(bad)
            shutil.rmtree(tmp)
            self.assertNotEqual(r.returncode, 0, bad)


if __name__ == "__main__":
    unittest.main()
