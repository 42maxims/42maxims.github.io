"""Theme and tradition landing pages, nav, llms.txt / llms-full.txt and robots.txt for AI crawlers. Run after python3 build.py."""
import html, json, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://42maxims.com"
D = json.load(open(os.path.join(ROOT, "data/maxims.json"), encoding="utf-8"))
THEMES = json.load(open(os.path.join(ROOT, "data/themes.json"), encoding="utf-8"))
SLUGS = {c["slug"]: c for c in D["concepts"]}


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


SITEMAP = set(re.findall(r"<loc>([^<]+)</loc>", read("sitemap.xml")))


class Themes(unittest.TestCase):
    def test_theme_data(self):
        self.assertGreaterEqual(len(THEMES), 6)
        for k, th in THEMES.items():
            with self.subTest(theme=k):
                self.assertRegex(k, r"^[a-z0-9]+(-[a-z0-9]+)*$")
                self.assertTrue(th["title"].strip() and th["intro"].strip())
                self.assertGreaterEqual(len(th["maxims"]), 3)
                self.assertEqual(len(set(th["maxims"])), len(th["maxims"]))
                self.assertLessEqual(set(th["maxims"]), set(SLUGS))

    def test_theme_pages(self):
        idx = read("themes/index.html")
        self.assertIn(f"{SITE}/themes/", SITEMAP)
        for k, th in THEMES.items():
            h = read(f"themes/{k}/index.html")
            with self.subTest(theme=k):
                self.assertIn(f'href="{k}/"', idx)
                self.assertIn(f"{SITE}/themes/{k}/", SITEMAP)
                self.assertIn(f"<h1>{html.escape(th['title'])}</h1>", h)
                self.assertIn(html.escape(th["intro"]), h)
                for m in th["maxims"]:
                    self.assertIn(f'<a href="../../maxims/{m}/">{html.escape(SLUGS[m]["maxim"])}</a>', h)
                    self.assertIn(f'href="../../themes/{k}/"', read(f"maxims/{m}/index.html"))  # backlink from the maxim
                self.assertEqual(h.count('<figure class="seed">'), len(th["maxims"]))  # one sample quote per maxim

    def test_tradition_pages(self):
        by = {}
        for q in D["quotes"]:
            by.setdefault(q["tradition"], set()).add(q["concept"])
        idx = read("traditions/index.html")
        for t, ms in by.items():
            h = read(f"traditions/{t}/index.html")
            with self.subTest(tradition=t):
                self.assertIn(f'href="{t}/"', idx)
                for m in ms:
                    self.assertIn(f'href="../../maxims/{m}/"', h)
                thin = len(ms) < 2
                self.assertEqual('content="noindex' in h, thin)
                self.assertEqual(f"{SITE}/traditions/{t}/" in SITEMAP, not thin)
        for t in set(D["traditions"]) - set(by):
            self.assertFalse(os.path.exists(os.path.join(ROOT, "traditions", t)), t)

    def test_nav_links_themes_and_traditions(self):
        for rel in ("index.html", "maxims/golden-rule/index.html", "themes/kindness/index.html"):
            h = read(rel)
            self.assertRegex(h, r'<a href="[^"]*sources/">Sources</a><a href="[^"]*themes/">Themes</a><a href="[^"]*traditions/">Traditions</a>')


class Geo(unittest.TestCase):
    def test_llms_txt(self):
        t = read("llms.txt")
        self.assertTrue(t.startswith("# 42 Maxims\n\n> "))
        for f in ("data/maxims.json", "data/voices.json", "data/sources.json", "data/generated/scores.json", "llms-full.txt"):
            self.assertIn(f"({SITE}/{f})", t)
            self.assertTrue(os.path.isfile(os.path.join(ROOT, f)), f)
        for k in THEMES:
            self.assertIn(f"{SITE}/themes/{k}/", t)
        self.assertEqual(len(re.findall(r"^- \[.*\]\(https://42maxims\.com/maxims/[^)]+\): .*(?<!\(Emerging\))$", t.split("## Themes")[0], re.M)), 42)
        self.assertIn("CC BY-SA 4.0", t)

    def test_llms_full_has_every_quote(self):
        t = read("llms-full.txt")
        for c in D["concepts"]:
            self.assertIn(f"## {c['maxim']}\n", t)
        for q in D["quotes"]:
            self.assertIn(f'"{q["text"]}" — {q["thinker"]}, {q["work"]}.', t)

    def test_robots_welcomes_ai_crawlers(self):
        r = read("robots.txt")
        self.assertNotIn("Disallow", r)
        for b in ("GPTBot", "OAI-SearchBot", "ClaudeBot", "PerplexityBot", "Google-Extended"):
            self.assertIn(f"User-agent: {b}\n", r)
        groups = re.split(r"\n\n", r)
        for g in groups:
            if g.startswith("User-agent") or "\nUser-agent" in g:
                self.assertIn("Allow: /", g)


if __name__ == "__main__":
    unittest.main()
