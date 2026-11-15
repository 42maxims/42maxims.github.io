"""Cloudflare Web Analytics: JS beacon emitted just before </body> on every page; empty token emits nothing."""
import glob, os, re, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER_TOKEN = "651193c60bbd4449afee65f5a13cf014"
SNIPPET = "<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{\"token\": \"651193c60bbd4449afee65f5a13cf014\"}'></script><!-- End Cloudflare Web Analytics -->"


def build(token):
    tmp = tempfile.mkdtemp()
    for f in ("build.py", "scoring.py"):
        shutil.copy(os.path.join(ROOT, f), tmp)
    shutil.copytree(os.path.join(ROOT, "data"), os.path.join(tmp, "data"))
    p = os.path.join(tmp, "build.py")
    src = open(p).read()
    src = re.sub(r'^CF_BEACON_TOKEN = "[^"]*"', lambda m: f'CF_BEACON_TOKEN = "{token}"', src, count=1, flags=re.M)
    open(p, "w").write(src)
    r = subprocess.run([sys.executable, p], capture_output=True, text=True)
    return tmp, r


def pages(tmp):
    found = glob.glob(os.path.join(tmp, "**", "index.html"), recursive=True)
    four = os.path.join(tmp, "404.html")
    if os.path.isfile(four):
        found.append(four)
    return found


class CloudflareAnalytics(unittest.TestCase):
    def test_committed_pages_have_snippet(self):
        self.assertIn(f'CF_BEACON_TOKEN = "{OWNER_TOKEN}"', open(os.path.join(ROOT, "build.py")).read())
        self.assertTrue(pages(ROOT))
        for f in pages(ROOT):
            h = open(f).read()
            self.assertEqual(h.count(SNIPPET), 1, f)
            self.assertLess(h.index(SNIPPET), h.index("</body>"), f)
            self.assertGreater(h.index(SNIPPET), h.index("</footer>"), f)
            self.assertNotIn("plausible", h.lower(), f)

    def test_empty_emits_nothing(self):
        tmp, r = build("")
        self.addCleanup(shutil.rmtree, tmp)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(pages(tmp))
        for f in pages(tmp):
            h = open(f).read().lower()
            self.assertNotIn("plausible", h, f)
            self.assertNotIn("cloudflareinsights", h, f)

    def test_invalid_token_rejected(self):
        for bad in ("x.js", "651193c60bbd4449afee65f5a13cf01", "651193c60bbd4449afee65f5a13cf014a", "651193C60BBD4449AFEE65F5A13CF014", "pa-abc"):
            tmp, r = build(bad)
            shutil.rmtree(tmp)
            self.assertNotEqual(r.returncode, 0, bad)


if __name__ == "__main__":
    unittest.main()
