"""Optional quote field "clips" (YouTube clips): data validation and rendering. Run after python3 build.py."""
import html, json, os, re, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(ROOT, "data", "maxims.json")))
ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
REQ = ("id", "start", "end", "label", "title", "channel")


def problems(cl):
    """Return a list of what is wrong with one clip record (empty = fine)."""
    whole = "start" not in cl and "end" not in cl
    req = ("id", "label", "title", "channel") if whole else REQ
    bad = [k for k in req if k not in cl]
    if bad:
        return [f"missing {bad}"]
    out = []
    if not (isinstance(cl["id"], str) and ID.match(cl["id"])):
        out.append("id must be an 11-character YouTube id")
    if whole and cl.get("kind") != "discussed":
        out.append("whole-video references must be kind discussed")
    for k in () if whole else ("start", "end"):
        if not (isinstance(cl[k], int) and not isinstance(cl[k], bool) and cl[k] >= 0):
            out.append(f"{k} must be a non-negative integer (seconds)")
    if whole:
        pass
    elif not out and cl["start"] >= cl["end"]:
        out.append("start must be before end")
    if not whole and not out and cl["end"] - cl["start"] > 120:
        out.append("clips are short: 120 seconds at most")
    if "kind" in cl and cl["kind"] not in ("verbatim", "paraphrase", "discussed"):
        out.append("kind must be verbatim, paraphrase or discussed")
    for k in ("label", "title", "channel"):
        if not (isinstance(cl[k], str) and cl[k].strip()):
            out.append(f"{k} must be non-empty text")
    return out


class Data(unittest.TestCase):
    def test_clips_valid(self):
        n = 0
        for i, q in enumerate(D["quotes"]):
            if "clips" in q:
                self.assertIsInstance(q["clips"], list); self.assertTrue(q["clips"], i)
                whole = all("start" not in c for c in q["clips"])
                self.assertIn(q["ver"], ("verified", "probable") if whole else ("verified",), f"quote {i}: timed clips only on verified quotes")
                for cl in q["clips"]:
                    n += 1; self.assertEqual(problems(cl), [], f"quote {i}")
        self.assertGreaterEqual(n, 9)

    def test_discussed_clips_are_flagged(self):
        """Third-party uploads that only discuss the line must say so; verbatim clips must be the exact words."""
        for q in D["quotes"]:
            for cl in q.get("clips", []):
                if cl["channel"] in ("JBProbe", "ManOfAllCreation"):
                    self.assertEqual(cl.get("kind"), "discussed", cl["id"])

    def test_validator_rejects_malformed(self):
        good = {"id": "ljqra3BcqWM", "start": 731, "end": 737, "label": "L", "title": "T", "channel": "C"}
        self.assertEqual(problems(good), [])
        for patch in ({"id": "short"}, {"id": "bad id!!!!!!"}, {"start": 737}, {"start": 800}, {"start": "731"}, {"end": 737.5},
                      {"start": True}, {"start": -1}, {"end": 9999}, {"title": " "}, {"channel": ""}, {"kind": "official"}):
            self.assertTrue(problems({**good, **patch}), patch)
        for k in REQ:
            self.assertTrue(problems({a: b for a, b in good.items() if a != k}), k)


class Pages(unittest.TestCase):
    def test_clip_rendered_on_maxim_and_voice_pages(self):
        for q in (x for x in D["quotes"] if any("start" in c for c in x.get("clips", []))):
            for path in (f"maxims/{q['concept']}", f"voices/{q['voice']}", f"sources/{q['source_id']}"):
                h = open(os.path.join(ROOT, path, "index.html"), encoding="utf-8").read()
                for cl in (c for c in q["clips"] if "start" in c):
                    i, a, b = cl["id"], cl["start"], cl["end"]
                    self.assertIn(f'href="https://www.youtube.com/watch?v={i}&amp;t={a}"', h, path)
                    link = re.search(r'<a href="https://www\.youtube\.com/watch\?v=%s[^>]*>' % i, h).group(0)
                    self.assertIn('target="_blank"', link); self.assertIn('rel="noopener noreferrer"', link)
                    self.assertIn(f'data-src="https://www.youtube-nocookie.com/embed/{i}?start={a}&amp;end={b}&amp;rel=0&amp;modestbranding=1&amp;controls=1', h, path)
                    self.assertIn(f"Watch on YouTube ({a//60}:{a%60:02d}–{b//60}:{b%60:02d}) ↗", h)
                    self.assertNotIn("Hear it spoken", h)
                    self.assertNotIn("Go deeper", h); self.assertNotIn("clip-credit", h)
                    if i == "ljqra3BcqWM":
                        self.assertNotIn("Amara", h) if not path.startswith("sources/") else self.assertIn("Amara", h)

    def test_kind_labels(self):
        h = open(os.path.join(ROOT, "sources", "12-rules-for-life", "index.html"), encoding="utf-8").read()
        self.assertEqual(h.count("discusses this rule (fan upload)"), 5)
        self.assertEqual(h.count('class="clip-play"'), 5)
        w = open(os.path.join(ROOT, "maxims", "be-present", "index.html"), encoding="utf-8").read()
        self.assertIn("Spoken as a close paraphrase", w)
        g = open(os.path.join(ROOT, "maxims", "own-your-mistakes", "index.html"), encoding="utf-8").read()
        self.assertNotIn("clip-note", g.split("<style")[-1].split("</style>")[-1])

    def test_whole_video_references(self):
        good = {"id": "VO6XEQIsCoM", "label": "L", "title": "T", "channel": "C", "kind": "discussed"}
        self.assertEqual(problems(good), [])
        self.assertTrue(problems({**good, "kind": "verbatim"}))
        self.assertTrue(problems({**good, "start": 5}))
        for k in ("id", "label", "title", "channel"):
            self.assertTrue(problems({a: b for a, b in good.items() if a != k}), k)
        want = {"VO6XEQIsCoM": ("The paradox of choice", "Barry Schwartz"), "ffEGzX-qwz0": ("Desire Is a Contract", "Naval Ravikant"),
                "iCvmsMzlF7o": ("The Power of Vulnerability", "Brené Brown")}
        seen = set()
        for q in D["quotes"]:
            for cl in q.get("clips", []):
                if cl["id"] in want:
                    seen.add(cl["id"]); self.assertNotIn("start", cl); self.assertEqual(cl["kind"], "discussed")
                    for path in (f"maxims/{q['concept']}", f"voices/{q['voice']}", f"sources/{q['source_id']}"):
                        h = open(os.path.join(ROOT, path, "index.html"), encoding="utf-8").read()
                        m = re.search(r'<a href="https://www\.youtube\.com/watch\?v=%s"[^>]*>(.*?)</a>' % cl["id"], h)
                        self.assertIsNotNone(m, path); self.assertIn('rel="noopener noreferrer"', m.group(0))
                        self.assertTrue(m.group(1).startswith("Watch on YouTube: ") and m.group(1).endswith(" ↗"))
                        self.assertIn(f"{q['thinker']} discusses this idea", h)
                        self.assertNotIn("fan upload", h.split(m.group(0))[1][:200])
        self.assertEqual(seen, set(want))

    def test_batch2_whole_video_refs(self):
        want = {"39wzku9KIEM", "UF8uR6Z6KLc", "ORp3q1Oaezw", "tGdsOXZpyWE", "AdKUJxjn-R8", "5MgBikgcWnY", "qzR62JJCMBQ",
                "c2tOp7OxyQ8", "1Evwgu369Jw", "SJMm4RAwVLo", "eIho2S0ZahI", "YyXRYgjQXX0", "lUKhMUZnLuw", "RBK5KLA5Jjg",
                "Ug414e-PCn4", "136nLhwBoSQ", "_X0mgOOSpLU", "awTgtA3BuRY", "ji5_MqicxSo"}
        seen = set()
        for q in D["quotes"]:
            self.assertLessEqual(len(q.get("clips", [])), 2, q["text"][:40])
            for cl in q.get("clips", []):
                if cl["id"] in want:
                    seen.add(cl["id"]); self.assertNotIn("start", cl); self.assertEqual(cl["kind"], "discussed")
                    self.assertTrue(cl.get("note"))
                    h = open(os.path.join(ROOT, "maxims", q["concept"], "index.html"), encoding="utf-8").read()
                    self.assertIn("watch?v=" + cl["id"], h); self.assertIn(cl["note"], h)
        self.assertEqual(seen, want)

    def test_nothing_from_youtube_loads_on_page_load(self):
        for root, _, files in os.walk(ROOT):
            if ".git" in root or "tests" in root:
                continue
            for f in files:
                if f.endswith(".html"):
                    h = open(os.path.join(root, f), encoding="utf-8").read()
                    self.assertNotRegex(h, r"<iframe", f)
                    self.assertNotRegex(h, r"<(?:img|script|link)[^>]+(?:youtube\.com|ytimg\.com|youtube-nocookie\.com)", f)
                    for s in re.findall(r'<script[^>]*\ssrc="([^"]+)"', h):
                        self.assertTrue(s.startswith("https://plausible.io/"), (f, s))

    def test_pages_without_clips_have_no_clip_markup(self):
        h = open(os.path.join(ROOT, "maxims", "moderation", "index.html"), encoding="utf-8").read()
        self.assertNotIn('class="clip"', h); self.assertNotIn("clip-play", h)


if __name__ == "__main__":
    unittest.main()
