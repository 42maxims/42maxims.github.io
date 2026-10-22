#!/usr/bin/env python3
"""Check data/maxims.json, data/voices.json and data/sources.json for schema mistakes.

Usage:  python3 scripts/validate.py            (exit 1 on errors)
        python3 scripts/validate.py --root DIR (check another checkout)

Every message names the file, the entry and how to fix it. The unit tests run this too
(tests/test_validate.py). Clip fields are checked separately in tests/test_clips.py.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
ERAS = ("axial", "classical", "medieval", "early-modern", "modern", "contemporary")
VERS = ("verified", "probable", "disputed", "unverified", "misattributed")
RELS = ("expresses", "similar", "partial", "contrasts")
VOICE_KINDS = ("person", "collective", "scripture", "legendary")
SOURCE_KINDS = ("book", "scripture", "talk", "article", "other")
CONFIDENCE = ("solid", "thin", "uncertain")
Q_REQUIRED = ("concept", "rel", "conf", "ver", "text", "thinker", "voice", "tradition", "era", "work", "source_id", "source")
Q_OPTIONAL = ("translation", "echoes", "clips")
NEEDS_URL = ("verified", "probable")  # unverified / misattributed / disputed may use "" when no source exists


def norm(text):
    return re.sub(r"\W+", " ", text.lower()).strip()


def short(text, n=50):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def validate(root=ROOT):
    """Return (errors, warnings): lists of human-readable strings."""
    errors, warnings = [], []
    data = {}
    for name in ("maxims", "voices", "sources"):
        path = os.path.join(root, "data", f"{name}.json")
        try:
            with open(path, encoding="utf-8") as f:
                data[name] = json.load(f)
        except FileNotFoundError:
            return [f"data/{name}.json: file not found"], []
        except json.JSONDecodeError as e:
            return [f"data/{name}.json: invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}"], []
    D, V, S = data["maxims"], data["voices"], data["sources"]
    err = errors.append

    for key in ("traditions", "concepts", "quotes"):
        if key not in D:
            err(f"data/maxims.json: missing top-level key '{key}'")
    if errors:
        return errors, warnings
    T = D["traditions"]

    # traditions
    for k, t in T.items():
        where = f"data/maxims.json traditions['{k}']"
        if not SLUG.match(k):
            err(f"{where}: key must be kebab-case (a-z, 0-9, hyphens)")
        if not str(t.get("name", "")).strip():
            err(f"{where}: missing 'name'")
        df = t.get("derives_from", [])
        if not isinstance(df, list):
            err(f"{where}: 'derives_from' must be a list of tradition keys")
            continue
        for p in df:
            if p == k:
                err(f"{where}: derives_from lists itself")
            elif p not in T:
                err(f"{where}: derives_from '{p}' is not a tradition key; add it under traditions or fix the spelling")
    def ancestors(k, seen):
        for p in T.get(k, {}).get("derives_from", []) or []:
            if p in seen:
                return True
            if p in T and ancestors(p, seen | {p}):
                return True
        return False
    for k in T:
        if ancestors(k, {k}):
            err(f"data/maxims.json traditions['{k}']: derives_from forms a cycle")

    # concepts
    slugs = {}
    for i, c in enumerate(D["concepts"]):
        s = c.get("slug", "")
        where = f"data/maxims.json concepts[{i}] ('{s}')"
        if not SLUG.match(str(s)):
            err(f"{where}: 'slug' must be kebab-case")
        if s in slugs:
            err(f"{where}: duplicate slug (also concepts[{slugs[s]}])")
        slugs[s] = i
        for f in ("maxim", "summary"):
            if not str(c.get(f, "")).strip():
                err(f"{where}: missing '{f}'")
        for j, l in enumerate(c.get("links", [])):
            url = l if isinstance(l, str) else (l.get("url") if isinstance(l, dict) else None)
            if not (isinstance(url, str) and url.startswith("https://")):
                err(f"{where}: links[{j}] must be an https URL string or {{\"url\": \"https://...\", \"label\": \"...\"}}")
            if isinstance(l, dict) and not str(l.get("label", "")).strip():
                err(f"{where}: links[{j}] object needs a 'label'")
        if "hold" in c and not (isinstance(c["hold"], str) and c["hold"].strip()):
            err(f"{where}: 'hold' must be a short reason string (or remove it)")

    # quotes
    per_concept = {}
    seen = {}
    for i, q in enumerate(D["quotes"]):
        where = f"data/maxims.json quotes[{i}] ({q.get('concept', '?')}: \"{short(q.get('text', ''))}\")"
        missing = [f for f in Q_REQUIRED if f not in q]
        if missing:
            err(f"{where}: missing field(s) {', '.join(missing)} (use \"source\": \"\" only for unverified/misattributed quotes with no source)")
        extra = [f for f in q if f not in Q_REQUIRED + Q_OPTIONAL]
        if extra:
            err(f"{where}: unknown field(s) {', '.join(extra)}; allowed optional fields: {', '.join(Q_OPTIONAL)}")
        if "concept" in q and q["concept"] not in slugs:
            err(f"{where}: unknown concept '{q['concept']}'; use an existing concept slug (new concepts need owner approval)")
        if "voice" in q and q["voice"] not in V:
            err(f"{where}: unknown voice '{q['voice']}'; add it to data/voices.json or use an existing slug")
        if "source_id" in q and q["source_id"] not in S:
            err(f"{where}: unknown source_id '{q['source_id']}'; add it to data/sources.json or use an existing slug")
        if "tradition" in q and q["tradition"] not in T:
            err(f"{where}: unknown tradition '{q['tradition']}'; add it under traditions (derives_from needs owner approval)")
        if "rel" in q and q["rel"] not in RELS:
            err(f"{where}: rel '{q['rel']}' must be one of {', '.join(RELS)}")
        if "ver" in q and q["ver"] not in VERS:
            err(f"{where}: ver '{q['ver']}' must be one of {', '.join(VERS)}")
        if "era" in q and q["era"] not in ERAS:
            err(f"{where}: era '{q['era']}' must be one of {', '.join(ERAS)}")
        if "conf" in q:
            c = q["conf"]
            if isinstance(c, bool) or not isinstance(c, (int, float)) or not 0 <= c <= 1:
                err(f"{where}: conf must be a number from 0 to 1, got {c!r}")
        for f in ("text", "thinker", "work"):
            if f in q and not str(q[f]).strip():
                err(f"{where}: '{f}' is empty")
        if "text" in q and q["text"] != q["text"].strip():
            err(f"{where}: 'text' has leading or trailing whitespace")
        if "source" in q:
            src = q["source"]
            if not isinstance(src, str):
                err(f"{where}: 'source' must be a URL string")
            elif q.get("ver") in NEEDS_URL and not src.startswith(("https://", "http://")):
                err(f"{where}: a {q.get('ver')} quote needs a 'source' URL where the exact wording can be read")
            elif src and not src.startswith(("https://", "http://")):
                err(f"{where}: 'source' must start with https:// (or be \"\" for a quote with no traceable source)")
            elif src.startswith("http://"):
                warnings.append(f"{where}: 'source' uses http://; prefer https:// if the site supports it")
        if "echoes" in q and len(str(q["echoes"])) >= 120:
            err(f"{where}: 'echoes' must be under 120 characters")
        if "text" in q and "concept" in q:
            key = (q["concept"], norm(q["text"]))
            if key in per_concept:
                err(f"{where}: duplicate of quotes[{per_concept[key]}] under the same concept")
            per_concept[key] = i
            t = norm(q["text"])
            if t in seen and seen[t][1] != q["concept"]:
                warnings.append(f"{where}: same wording also under '{seen[t][1]}' (quotes[{seen[t][0]}]); fine if intended")
            seen.setdefault(t, (i, q["concept"]))
    for s, i in slugs.items():
        c = D["concepts"][i]
        n = sum(1 for q in D["quotes"] if q.get("concept") == s)
        if "seed" in c and not (isinstance(c["seed"], int) and 0 <= c["seed"] < n):
            err(f"data/maxims.json concepts[{i}] ('{s}'): seed {c['seed']!r} must index one of its {n} quotes")

    # voices and sources
    def common(where, e):
        for f in ("dates", "tradition", "period", "summary", "confidence", "refs"):
            if f not in e:
                err(f"{where}: missing '{f}'")
        if e.get("tradition") not in T:
            err(f"{where}: unknown tradition '{e.get('tradition')}'")
        if e.get("period") not in ERAS:
            err(f"{where}: period must be one of {', '.join(ERAS)}")
        if e.get("confidence") not in CONFIDENCE:
            err(f"{where}: confidence must be one of {', '.join(CONFIDENCE)}")
        if len(str(e.get("summary", "")).strip()) <= 40:
            err(f"{where}: summary must be 2–3 factual sentences (over 40 characters)")
        refs = e.get("refs")
        if not isinstance(refs, list) or not refs:
            err(f"{where}: refs must list at least one https reference (Wikipedia, Britannica, SEP, ...)")
        else:
            for u in refs:
                if not str(u).startswith("https://"):
                    err(f"{where}: ref '{u}' must start with https://")
    for k, v in V.items():
        where = f"data/voices.json['{k}']"
        if not SLUG.match(k):
            err(f"{where}: slug must be kebab-case")
        if not str(v.get("name", "")).strip():
            err(f"{where}: missing 'name'")
        if v.get("kind") not in VOICE_KINDS:
            err(f"{where}: kind '{v.get('kind')}' must be one of {', '.join(VOICE_KINDS)}")
        if "label" in v and v["label"] != "Scripture":
            err(f"{where}: the only supported label override is \"Scripture\"")
        common(where, v)
    for k, s in S.items():
        where = f"data/sources.json['{k}']"
        if not SLUG.match(k):
            err(f"{where}: slug must be kebab-case")
        if not str(s.get("title", "")).strip():
            err(f"{where}: missing 'title'")
        if s.get("kind") not in SOURCE_KINDS:
            err(f"{where}: kind '{s.get('kind')}' must be one of {', '.join(SOURCE_KINDS)}")
        if "voice" not in s:
            err(f"{where}: missing 'voice' (a voice slug, or null)")
        elif s["voice"] is not None and s["voice"] not in V:
            err(f"{where}: unknown voice '{s['voice']}'")
        common(where, s)
    used_v = {q.get("voice") for q in D["quotes"]} | {s.get("voice") for s in S.values()}
    for k in sorted(set(V) - used_v):
        err(f"data/voices.json['{k}']: not used by any quote or source; remove it or link a quote to it")
    used_s = {q.get("source_id") for q in D["quotes"]}
    for k in sorted(set(S) - used_s):
        err(f"data/sources.json['{k}']: not used by any quote; remove it or link a quote to it")
    tp = os.path.join(root, "data", "themes.json")  # optional: theme landing pages (SPEC §10)
    if os.path.exists(tp):
        slugs = {c.get("slug") for c in D["concepts"]}
        for k, th in json.load(open(tp, encoding="utf-8")).items():
            where = f"data/themes.json['{k}']"
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", k):
                err(f"{where}: theme slug must be kebab-case")
            for f in ("title", "intro"):
                if not str(th.get(f, "")).strip():
                    err(f"{where}: missing '{f}'")
            ms = th.get("maxims", [])
            if len(ms) < 3:
                err(f"{where}: a theme needs at least 3 maxims, has {len(ms)}")
            if len(set(ms)) != len(ms):
                err(f"{where}: a maxim is listed twice")
            for m in ms:
                if m not in slugs:
                    err(f"{where}: unknown maxim slug '{m}'; use a slug from data/maxims.json concepts")
    return errors, warnings


def main(argv):
    root = ROOT
    if len(argv) > 2 and argv[1] == "--root":
        root = argv[2]
    errors, warnings = validate(root)
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:", e)
    if errors:
        print(f"\n{len(errors)} error(s). Fix them, then run: python3 build.py && python3 -m unittest discover -s tests")
        return 1
    print(f"data OK ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
