import os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUR = r'(?: aria-current="(?:page|true)")?'
NAV_LINK = re.compile(r'<a href="[^"]*maxim-of-the-day/"' + CUR + r' aria-label="Maxim of the day" title="Maxim of the day">Daily</a>')


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

    def test_home_nav_and_brand_link(self):
        for p in pages():
            with open(p, encoding="utf-8") as fh:
                h = fh.read()
            self.assertRegex(h, r'<p class="brand"><a href="[^"]*">42 Maxims</a></p>', p)
            self.assertRegex(h, r'<nav aria-label="Main"><a href="[^"]*"' + CUR + r' aria-label="Home">Home</a><a href="[^"]*voices/"' + CUR + '>', p)
            self.assertNotIn('">The 42</a><a href', h, p)

    def test_nav_marks_current_section(self):
        cases = {"index.html": ("Home", "page"), "maxims/golden-rule/index.html": ("Home", "true"),
                 "voices/index.html": ("Voices", "page"), "voices/confucius/index.html": ("Voices", "true"),
                 "sources/index.html": ("Sources", "page"), "themes/kindness/index.html": ("Themes", "true"),
                 "traditions/index.html": ("Traditions", "page"), "traditions/stoicism/index.html": ("Traditions", "true"),
                 "maxim-of-the-day/index.html": ("Daily", "page"), "method/index.html": ("Method", "page"),
                 "about/index.html": ("About", "page")}
        for rel, (label, kind) in cases.items():
            with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
                nav = re.search(r'<nav aria-label="Main">(.*?)</nav>', fh.read()).group(1)
            cur = re.findall(r'aria-current="(page|true)"[^>]*>([^<]+)</a>', nav)
            self.assertEqual(cur, [(kind, label)], rel)
        with open(os.path.join(ROOT, "404.html"), encoding="utf-8") as fh:
            self.assertNotIn("aria-current", fh.read())

    def test_about_defines_maxim(self):
        with open(os.path.join(ROOT, "about", "index.html"), encoding="utf-8") as fh:
            t = fh.read()
        self.assertIn("A maxim is a short, memorable rule for how to live.", t)
        self.assertLess(t.index("A maxim is"), t.index("42 Maxims gathers"))
        m = re.search(r'<meta name="description" content="([^"]*)"', t)
        self.assertTrue(m and "maxim" in m.group(1) and len(m.group(1)) <= 155)
