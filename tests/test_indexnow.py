"""IndexNow: key constant, key file at the site root, and the submit script's payload. Run after python3 build.py."""
import importlib.util, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("indexnow", os.path.join(ROOT, "scripts", "indexnow.py"))
indexnow = importlib.util.module_from_spec(spec); spec.loader.exec_module(indexnow)


class IndexNow(unittest.TestCase):
    def test_key_file(self):
        key, site = indexnow.build_constants()
        self.assertRegex(key, r"^[0-9a-f]{32}$")
        with open(os.path.join(ROOT, f"{key}.txt"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), key)
        others = [f for f in os.listdir(ROOT) if re.fullmatch(r"[0-9a-f]{32}\.txt", f)]
        self.assertEqual(others, [f"{key}.txt"])

    def test_payload_from_sitemap(self):
        key, site = indexnow.build_constants()
        urls = indexnow.sitemap_urls()
        self.assertIn(f"{site}/", urls)
        self.assertTrue(all(u.startswith(f"{site}/") for u in urls))
        body = indexnow.payload(key, site, urls)
        self.assertEqual(body["host"], "42maxims.com")
        self.assertEqual(body["keyLocation"], f"https://42maxims.com/{key}.txt")
        self.assertEqual(body["urlList"], urls[:10000])
        self.assertLessEqual(len(indexnow.payload(key, site, ["x"] * 10001)["urlList"]), 10000)


if __name__ == "__main__":
    unittest.main()
