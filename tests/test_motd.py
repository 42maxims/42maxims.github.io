"""Maxim of the Day: date-seeded selection (Python + inline JS twin). Run after python3 build.py."""
import datetime, json, os, re, unittest
import build

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = datetime.date
PAGE = open(os.path.join(ROOT, "maxim-of-the-day", "index.html"), encoding="utf-8").read()


class MotdTests(unittest.TestCase):
    n = len(build.MOTD)

    def test_deterministic(self):
        self.assertEqual(build.motd_index(D(2026, 10, 15), self.n), build.motd_index(D(2026, 10, 15), self.n))

    def test_known_value(self):
        self.assertEqual(build.motd_index(D(1970, 1, 1), 7), 0)
        self.assertEqual(build.motd_index(D(1970, 1, 11), 7), 3)

    def test_consecutive_days_differ(self):
        d = D(2026, 1, 1)
        for i in range(400):
            a = build.motd_index(d + datetime.timedelta(i), self.n)
            b = build.motd_index(d + datetime.timedelta(i + 1), self.n)
            self.assertNotEqual(a, b)

    def test_wraps(self):
        d = D(2026, 3, 3)
        self.assertEqual(build.motd_index(d, self.n), build.motd_index(d + datetime.timedelta(self.n), self.n))
        self.assertEqual(build.motd_index(d + datetime.timedelta(self.n - 1), 5) in range(5), True)

    def test_full_cycle_covers_all(self):
        d = D(2026, 5, 1)
        seen = {build.motd_index(d + datetime.timedelta(i), self.n) for i in range(self.n)}
        self.assertEqual(seen, set(range(self.n)))

    def test_js_formula_matches(self):
        self.assertIn(build.MOTD_FORMULA, PAGE)
        self.assertEqual(build.MOTD_FORMULA, "Math.floor(Date.now()/86400000)%LIST.length")
        # UTC whole days since epoch, as in the Python twin
        for day in (D(2026, 10, 15), D(2027, 2, 28)):
            ms = (day - D(1970, 1, 1)).days * 86400000 + 86399999
            self.assertEqual(ms // 86400000 % self.n, build.motd_index(day, self.n))

    def test_embedded_list(self):
        m = re.search(r"var LIST=(\[.*?\]);var e=", PAGE, re.S)
        lst = json.loads(m.group(1).replace("\\u003c", "<"))
        self.assertEqual([e["slug"] for e in lst], [e["slug"] for e in build.MOTD])
        slugs = [e["slug"] for e in lst]
        self.assertEqual(slugs, sorted(slugs))

    def test_no_held_and_all_have_pages(self):
        held = {c["slug"] for c in build.D["concepts"] if c.get("hold")}
        for e in build.MOTD:
            self.assertNotIn(e["slug"], held)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "maxims", e["slug"], "index.html")))

    def test_page_basics(self):
        self.assertIn('<link rel="canonical" href="https://42maxims.com/maxim-of-the-day/">', PAGE)
        self.assertIn("<title>Maxim of the Day — 42 Maxims</title>", PAGE)
        self.assertEqual(PAGE.count("<h1"), 1)
        self.assertIn(build.MOTD[0]["maxim"].replace("'", "&#x27;"), PAGE)
        sm = open(os.path.join(ROOT, "sitemap.xml")).read()
        self.assertIn("https://42maxims.com/maxim-of-the-day/", sm)


if __name__ == "__main__":
    unittest.main()
