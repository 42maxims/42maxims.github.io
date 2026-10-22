"""scripts/validate.py: real data passes; common mistakes give clear messages."""
import copy, json, os, sys, tempfile, unittest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
from validate import validate, RELS, VERS
from scoring import VER, REL


def load(name):
    with open(os.path.join(ROOT, "data", f"{name}.json"), encoding="utf-8") as f:
        return json.load(f)


class TestValidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D, cls.V, cls.S = load("maxims"), load("voices"), load("sources")

    def run_on(self, D=None, V=None, S=None):
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, "data"))
            for name, obj in (("maxims", D or self.D), ("voices", V or self.V), ("sources", S or self.S)):
                with open(os.path.join(tmp, "data", f"{name}.json"), "w", encoding="utf-8") as f:
                    json.dump(obj, f)
            return validate(tmp)[0]

    def assertError(self, errors, *needles):
        joined = "\n".join(errors)
        for n in needles:
            self.assertIn(n, joined)

    def test_repo_data_is_valid(self):
        errors, _ = validate(ROOT)
        self.assertEqual(errors, [], "\n" + "\n".join(errors))

    def test_enums_match_scoring(self):
        self.assertEqual(set(VERS), set(VER))
        self.assertEqual(set(RELS), set(REL))

    def bad_quote(self, **changes):
        D = copy.deepcopy(self.D)
        q = next(q for q in D["quotes"] if q["ver"] == "verified")
        q.update(changes)
        for k, v in changes.items():
            if v is None:
                del q[k]
        return self.run_on(D)

    def test_missing_source_url(self):
        self.assertError(self.bad_quote(source=""), "needs a 'source' URL")
        self.assertError(self.bad_quote(source=None), "missing field(s) source")

    def test_unknown_ids(self):
        self.assertError(self.bad_quote(voice="nobody-at-all"), "unknown voice 'nobody-at-all'")
        self.assertError(self.bad_quote(source_id="no-such-book"), "unknown source_id 'no-such-book'")
        self.assertError(self.bad_quote(tradition="atlantis"), "unknown tradition 'atlantis'")
        self.assertError(self.bad_quote(concept="new-idea"), "unknown concept 'new-idea'")

    def test_bad_values(self):
        self.assertError(self.bad_quote(ver="certain"), "ver 'certain' must be one of")
        self.assertError(self.bad_quote(rel="kinda"), "rel 'kinda' must be one of")
        self.assertError(self.bad_quote(conf=1.5), "conf must be a number from 0 to 1")
        self.assertError(self.bad_quote(conf="high"), "conf must be a number from 0 to 1")
        self.assertError(self.bad_quote(era="bronze"), "era 'bronze' must be one of")
        self.assertError(self.bad_quote(author="x"), "unknown field(s) author")

    def test_duplicate_quote(self):
        D = copy.deepcopy(self.D)
        dup = copy.deepcopy(D["quotes"][0])
        dup["text"] = dup["text"].upper() + "!"
        D["quotes"].append(dup)
        self.assertError(self.run_on(D), "duplicate of quotes[0] under the same concept")

    def test_bad_tradition_link(self):
        D = copy.deepcopy(self.D)
        k = next(iter(D["traditions"]))
        D["traditions"][k]["derives_from"] = ["no-such-tradition"]
        self.assertError(self.run_on(D), "derives_from 'no-such-tradition' is not a tradition key")

    def test_bad_voice_and_source(self):
        V, S = copy.deepcopy(self.V), copy.deepcopy(self.S)
        V[next(iter(V))]["kind"] = "text"
        S[next(iter(S))]["refs"] = ["http://example.com"]
        self.assertError(self.run_on(V=V, S=S), "kind 'text' must be one of", "must start with https://")

    def test_invalid_json_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.mkdir(os.path.join(tmp, "data"))
            for n in ("maxims", "voices", "sources"):
                with open(os.path.join(tmp, "data", f"{n}.json"), "w") as f:
                    f.write("{" if n == "voices" else "{}")
            self.assertError(validate(tmp)[0], "data/voices.json: invalid JSON")


if __name__ == "__main__":
    unittest.main()
