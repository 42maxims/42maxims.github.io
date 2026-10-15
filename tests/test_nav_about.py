import os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV_LINK = re.compile(r'<a href="[^"]*maxim-of-the-day/" aria-label="Maxim of the day" title="Maxim of the day">Daily</a>')


def pages():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("tests", "tools", "data", "__pycache__")]
        for f in files:
            if f.endswith(".html") and f != "404.html":
                yield os.path.join(base, f)


class NavAboutTests(unittest.TestCase):
    def test_daily_nav_label_on_all_pages(self):
        n = 0
        for p in pages():
            with open(p, encoding="utf-8") as fh:
                self.assertRegex(fh.read(), NAV_LINK, p)
            n += 1
        self.assertGreater(n, 100)

    def test_about_defines_maxim(self):
        with open(os.path.join(ROOT, "about", "index.html"), encoding="utf-8") as fh:
            t = fh.read()
        self.assertIn("A maxim is a short, memorable rule for how to live.", t)
        self.assertLess(t.index("A maxim is"), t.index("42 Maxims gathers"))
        m = re.search(r'<meta name="description" content="([^"]*)"', t)
        self.assertTrue(m and "maxim" in m.group(1) and len(m.group(1)) <= 155)
