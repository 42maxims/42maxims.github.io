"""Google Search Console and Yandex Webmaster HTML-tag verification: on every generated page, once, inside <head>."""
import glob, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = "KciBKHM1FLesIdzjoS5AjOy1-xuLPMgKGVx2BBv3w9s"
TAG = f'<meta name="google-site-verification" content="{TOKEN}" />'
YANDEX_TOKEN = "b8e229513ca91bd4"
YANDEX_TAG = '<meta name="yandex-verification" content="b8e229513ca91bd4" />'


class Verification(unittest.TestCase):
    def test_constant_shape(self):
        src = open(os.path.join(ROOT, "build.py")).read()
        self.assertIn(f'GOOGLE_SITE_VERIFICATION = "{TOKEN}"', src)
        self.assertRegex(TOKEN, r"^[A-Za-z0-9_-]+$")
        self.assertIn(f'YANDEX_SITE_VERIFICATION = "{YANDEX_TOKEN}"', src)
        self.assertRegex(YANDEX_TOKEN, r"^[A-Za-z0-9_-]+$")

    def test_home_has_tag(self):
        h = open(os.path.join(ROOT, "index.html")).read()
        self.assertEqual(h.count(TAG), 1)
        self.assertLess(h.index(TAG), h.index("</head>"))
        self.assertEqual(h.count(YANDEX_TAG), 1)
        self.assertLess(h.index(YANDEX_TAG), h.index("</head>"))

    def test_every_page_has_tag_once_in_head(self):
        files = [f for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)
                 if "/.git/" not in f and "/node_modules/" not in f]
        self.assertTrue(files)
        for f in files:
            h = open(f).read()
            self.assertEqual(h.count("google-site-verification"), 1, f)
            self.assertEqual(h.count(TAG), 1, f)
            self.assertLess(h.index(TAG), h.index("</head>"), f)
            self.assertEqual(h.count("yandex-verification"), 1, f)
            self.assertEqual(h.count(YANDEX_TAG), 1, f)
            self.assertLess(h.index(YANDEX_TAG), h.index("</head>"), f)


if __name__ == "__main__":
    unittest.main()
