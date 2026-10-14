"""Worked example from SPEC.md 5.3."""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scoring import evidence

TR = {"christianity": {"derives_from": ["judaism"]},
      "enlightenment": {"derives_from": ["greek", "christianity"]}}

def q(th, tr, era, rel, conf):
    return dict(thinker=th, tradition=tr, era=era, rel=rel, conf=conf, ver="verified")

A = [q("Confucius", "confucianism", "axial", "expresses", .95),
     q("Hillel", "judaism", "classical", "expresses", .95),
     q("Jesus", "christianity", "classical", "expresses", .95),
     q("Jesus", "christianity", "classical", "expresses", .90),
     q("Mahabharata", "hinduism", "axial", "similar", .90),
     q("Isocrates", "greek", "axial", "similar", .90),
     q("Kant", "enlightenment", "early-modern", "partial", .80)]
B = [q("Seneca", "stoicism", "classical", "expresses", .9)] * 7

class WorkedExample(unittest.TestCase):
    def test_golden_rule(self):
        E, b = evidence(A, TR)
        self.assertAlmostEqual(b["Q"], 5.33, 2)
        self.assertAlmostEqual(b["K"], 4.43, 2)
        self.assertAlmostEqual(b["T"], 3.795, 3)
        self.assertEqual(b["R"], 3)
        self.assertAlmostEqual(E, 19.835, 2)

    def test_single_voice(self):
        E, _ = evidence(B, {})
        self.assertAlmostEqual(E, 7.137, 2)

if __name__ == "__main__":
    unittest.main()
