"""On-page SEO: titles, descriptions, canonicals, social tags, headings, JSON-LD, sitemap, robots. Run after python3 build.py."""
import glob, json, os, re, unittest
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://42maxims.github.io"


def pages():
    out = {}
    for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(f, ROOT)
        out[rel] = open(f, encoding="utf-8").read()
    return out


class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.h = []; self.imgs = []; self.ld = []; self._ld = False; self.meta = {}; self.links = {}; self.title = ""; self._t = False; self.lang = None; self.hd = None
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag == "html": self.lang = a.get("lang")
        if tag in ("h1", "h2", "h3", "h4"): self.h.append(int(tag[1]))
        if tag == "img": self.imgs.append(a)
        if tag == "meta": self.meta[a.get("name") or a.get("property")] = a.get("content")
        if tag == "link": self.links[a.get("rel")] = a.get("href")
        if tag == "title": self._t = True
        if tag == "script" and a.get("type") == "application/ld+json": self._ld = True; self.ld.append("")
    def handle_endtag(self, tag):
        if tag == "title": self._t = False
        if tag == "script": self._ld = False
    def handle_data(self, d):
        if self._t: self.title += d
        if self._ld: self.ld[-1] += d


def parse(h):
    p = P(); p.feed(h); return p


PAGES = {k: parse(v) for k, v in pages().items()}
INDEXABLE = {k: p for k, p in PAGES.items() if k != "404.html" and "noindex" not in (p.meta.get("robots") or "")}


def url_of(rel):
    return SITE + "/" + ("" if rel == "index.html" else rel[:-len("index.html")])


class Seo(unittest.TestCase):
    def test_lang_and_titles_unique(self):
        titles = {}
        for k, p in PAGES.items():
            with self.subTest(page=k):
                self.assertEqual(p.lang, "en")
                self.assertTrue(p.title.strip())
                titles.setdefault(p.title, []).append(k)
        for t, ks in titles.items():
            self.assertEqual(len(ks), 1, f"duplicate title {t!r}: {ks}")

    def test_descriptions(self):
        descs = {}
        for k, p in INDEXABLE.items():
            d = p.meta.get("description") or ""
            with self.subTest(page=k):
                self.assertTrue(30 <= len(d) <= 160, f"{len(d)} chars")
            descs.setdefault(d, []).append(k)
        # profile pages share no boilerplate; only allow duplicates among none
        dup = {d: ks for d, ks in descs.items() if len(ks) > 1}
        self.assertEqual(dup, {})

    def test_canonical_and_social(self):
        for k, p in INDEXABLE.items():
            u = url_of(k)
            with self.subTest(page=k):
                self.assertEqual(p.links.get("canonical"), u)
                self.assertEqual(p.meta.get("og:url"), u)
                self.assertEqual(p.meta.get("og:title"), p.title)
                self.assertEqual(p.meta.get("og:description"), p.meta["description"])
                self.assertEqual(p.meta.get("twitter:card"), "summary_large_image")
                img = SITE + "/og.png"
                self.assertEqual(p.meta.get("og:image"), img)
                self.assertEqual(p.meta.get("twitter:image"), img)
                self.assertEqual(p.meta.get("og:image:width"), "1200")
                self.assertEqual(p.meta.get("og:image:height"), "630")
                self.assertTrue(p.meta.get("og:image:alt"))
                self.assertEqual(p.meta.get("og:site_name"), "42 Maxims")

    def test_og_image_file(self):
        import struct
        f = os.path.join(ROOT, "og.png")
        self.assertTrue(os.path.isfile(f))
        self.assertLess(os.path.getsize(f), 150_000)
        d = open(f, "rb").read(24)
        self.assertEqual(d[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", d[16:24]), (1200, 630))

    def test_404_noindex_no_canonical(self):
        p = PAGES["404.html"]
        self.assertIn("noindex", p.meta.get("robots"))
        self.assertNotIn("canonical", p.links)

    def test_headings(self):
        for k, p in PAGES.items():
            with self.subTest(page=k):
                self.assertEqual(p.h.count(1), 1)
                self.assertEqual(p.h[0], 1)
                for a, b in zip(p.h, p.h[1:]):
                    self.assertLessEqual(b, a + 1, f"heading jumps {a}->{b}")

    def test_images_have_alt(self):
        for k, p in PAGES.items():
            for img in p.imgs:
                self.assertTrue(img.get("alt") is not None, k)

    def test_json_ld_valid_and_accurate(self):
        data = json.load(open(os.path.join(ROOT, "data/maxims.json")))
        texts = {q["text"] for q in data["quotes"]}
        for k, p in INDEXABLE.items():
            for raw in p.ld:
                with self.subTest(page=k):
                    o = json.loads(raw)
                    self.assertEqual(o["@context"], "https://schema.org")
                    if o["@type"] == "Quotation":
                        self.assertIn(o["text"], texts)
                    if o["@type"] == "BreadcrumbList":
                        self.assertEqual(o["itemListElement"][-1]["item"], url_of(k))
        types = [json.loads(r)["@type"] for r in INDEXABLE["index.html"].ld]
        self.assertEqual(types, ["WebSite"])

    def test_sitemap_matches_indexable_pages(self):
        sm = open(os.path.join(ROOT, "sitemap.xml")).read()
        locs = set(re.findall(r"<loc>([^<]+)</loc>", sm))
        self.assertEqual(locs, {url_of(k) for k in INDEXABLE})
        self.assertNotIn(SITE + "/404", sm)

    def test_robots(self):
        r = open(os.path.join(ROOT, "robots.txt")).read()
        self.assertIn("User-agent: *", r)
        self.assertIn(f"Sitemap: {SITE}/sitemap.xml", r)
        self.assertNotIn("Disallow: /\n", r)

    def test_project_stays_anonymous(self):
        for f in ["sitemap.xml", "robots.txt"] + list(pages()):
            self.assertNotIn("Farrell", open(os.path.join(ROOT, f), encoding="utf-8").read())
            self.assertNotIn("joe2far", open(os.path.join(ROOT, f), encoding="utf-8").read())


if __name__ == "__main__":
    unittest.main()
