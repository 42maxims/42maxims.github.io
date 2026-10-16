"""Share buttons on every maxim page: encoded canonical URLs, rel attributes, no new third-party scripts. Run after python3 build.py."""
import glob, os, re, unittest
from html import unescape
from urllib.parse import quote, urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://42maxims.com"
PAGES = sorted(glob.glob(os.path.join(ROOT, "maxims", "*", "index.html")))


class TestShare(unittest.TestCase):
    def test_pages_exist(self):
        self.assertGreater(len(PAGES), 40)

    def test_every_maxim_page(self):
        for f in PAGES:
            h = open(f, encoding="utf-8").read(); slug = f.split(os.sep)[-2]
            url = f"{SITE}/maxims/{slug}/"
            maxim = unescape(re.search(r'<h1 class="maxim">(.*?)</h1>', h).group(1))
            x = re.search(r'<a href="(https://twitter\.com/intent/tweet[^"]*)"([^>]*)>', h)
            li = re.search(r'<a href="(https://www\.linkedin\.com/sharing/share-offsite/[^"]*)"([^>]*)>', h)
            self.assertTrue(x and li, slug)
            q = parse_qs(urlparse(unescape(x.group(1))).query)
            self.assertEqual(q["url"], [url], slug); self.assertEqual(q["text"], [maxim], slug)
            self.assertIn(f"url={quote(url, safe='')}", li.group(1), slug)
            self.assertIn(f"&amp;url={quote(url, safe='')}", x.group(1), slug)
            for attrs in (x.group(2), li.group(2)):
                self.assertIn('target="_blank"', attrs); self.assertIn('rel="noopener noreferrer"', attrs); self.assertIn("aria-label=", attrs)
            self.assertIn(f'id="copylink" data-url="{url}" aria-label=', h, slug)
            self.assertIn(f'<a id="plainlink" href="{url}"', h, slug)

    def test_no_external_scripts(self):
        for f in PAGES:
            h = open(f, encoding="utf-8").read()
            for src in re.findall(r'<script[^>]*\ssrc="([^"]+)"', h):
                self.assertTrue(src.startswith("https://plausible.io/"), (f, src))
