"""Further-reading media: whole-video references across maxims, and book links (str or {url,label}) on concepts."""
import html, json, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "maxims.json")))
ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
# The only concept that has no good video yet (nothing found that fits). Remove it from here when one is added.
NO_VIDEO = set()


def page(*parts):
    return open(os.path.join(ROOT, *parts, "index.html"), encoding="utf-8").read()


class Refs(unittest.TestCase):
    def test_every_concept_has_a_video(self):
        have = {q["concept"] for q in D["quotes"] if q.get("clips")}
        missing = {c["slug"] for c in D["concepts"]} - have
        self.assertEqual(missing, NO_VIDEO)

    def test_video_rules(self):
        for q in D["quotes"]:
            cl = q.get("clips", [])
            self.assertLessEqual(len(cl), 2, q["text"][:40])
            self.assertEqual(len({c["id"] for c in cl}), len(cl), "same video twice on one quote")
            for c in cl:
                self.assertRegex(c["id"], ID)
                if "start" not in c:
                    self.assertEqual(c["kind"], "discussed")
                    self.assertTrue(c.get("note") or q.get("thinker"))
                    if c.get("note"):
                        self.assertLessEqual(len(c["note"]), 90, c["id"])
                    self.assertLessEqual(len(c["label"]), 80, c["id"])
                    h = page("maxims", q["concept"])
                    self.assertIn("watch?v=" + c["id"], h)

    def test_fan_uploads_are_flagged(self):
        fan = {"jpxLWF65jIM", "awTgtA3BuRY", "xY48e1oDXSU"}  # whole-video links to third-party Peterson uploads
        seen = set()
        for q in D["quotes"]:
            for c in q.get("clips", []):
                if c["id"] in fan and "start" not in c:
                    seen.add(c["id"]); self.assertIn("fan upload", (c.get("note", "") + " " + c["label"]).lower(), c["id"])
        self.assertEqual(seen, fan)

    def test_concept_links_well_formed(self):
        n_books = 0
        for c in D["concepts"]:
            seen = set()
            for l in c.get("links", []):
                u, label = (l["url"], l["label"]) if isinstance(l, dict) else (l, None)
                self.assertTrue(u.startswith("https://"), u)
                self.assertNotIn(u, seen, f"{c['slug']}: duplicate link"); seen.add(u)
                if label is not None:
                    n_books += 1
                    self.assertTrue(label.strip() and len(label) <= 110, u)
                    self.assertEqual(set(l), {"url", "label"})
            h = page("maxims", c["slug"])
            for l in c.get("links", []):
                if isinstance(l, dict):
                    self.assertIn(f'<a href="{l["url"]}">', h)
                    self.assertIn(html.escape(l["label"]), h)
        self.assertGreaterEqual(n_books, 25)

    def test_book_links_not_already_a_quote_source(self):
        for c in D["concepts"]:
            srcs = {q["source"] for q in D["quotes"] if q["concept"] == c["slug"]}
            for l in c.get("links", []):
                if isinstance(l, dict):
                    self.assertNotIn(l["url"], srcs, c["slug"])


if __name__ == "__main__":
    unittest.main()
