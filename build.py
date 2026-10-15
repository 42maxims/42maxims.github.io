"""Builds the static site from data/maxims.json. Run: python3 build.py (no dependencies)."""
import json, os, html, math, re
from scoring import evidence, moral_rank, ancestors, VER, REL, W_Q, W_K, W_T, W_R

ROOT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(ROOT, "data/maxims.json")))
VOICES = json.load(open(os.path.join(ROOT, "data/voices.json")))
SOURCES = json.load(open(os.path.join(ROOT, "data/sources.json")))
TR = D["traditions"]
esc = html.escape
TOP_N = 42
ERA_ORDER = ["axial", "classical", "medieval", "early-modern", "modern", "contemporary"]
VER_ORDER = ["verified", "probable", "disputed", "unverified", "misattributed"]
VER_LABEL = {"verified": "Verified", "probable": "Probable", "disputed": "Disputed",
             "unverified": "Unverified", "misattributed": "Misattributed"}
VER_TITLE = {"verified": "Checked against a primary text or reputable translation",
             "probable": "Checked against a reliable secondary source only",
             "disputed": "Credible sources disagree about this attribution",
             "unverified": "No traceable origin yet; scores zero",
             "misattributed": "Attribution known to be wrong; scores zero"}
# Display name for the data field "era": shown as a "period" with explicit dates (SPEC §5.1 buckets).
ERA_LABEL = {"axial": "Ancient (before 200 BCE)", "classical": "Classical (200 BCE – 600 CE)",
             "medieval": "Medieval (600 – 1500)", "early-modern": "Early modern (1500 – 1800)",
             "modern": "Modern (1800 – 1950)", "contemporary": "Contemporary (1950 – today)"}
VOICE_KIND = {"person": "Person", "collective": "Collective", "text": "Known through the text", "legendary": "Traditional or legendary figure"}
SOURCE_KIND = {"book": "Book", "scripture": "Scripture", "collection": "Collection", "speech": "Speech or talk",
               "proverb": "Proverb or saying", "other": "Other"}
CONFIDENCE_NOTE = {"thin": "Little is known for certain here; this background is thin and may be revised.",
                   "uncertain": "Authorship, dates or origin are uncertain or disputed; read this background with care."}

CSS = """:root{--bg:#fbf7ef;--card:#fffdf8;--fg:#2e2a25;--muted:#6f655a;--accent:#8a5a2b;--accent-soft:#c9a46a;
--line:#e7ddcc;--chip:#f1e8d8;
--ok-bg:#e3f0de;--ok-fg:#2f6b2a;--warn-bg:#f8ecc9;--warn-fg:#7d5a00;--grey-bg:#ebe7e1;--grey-fg:#5d5750;--bad-bg:#f6dcd7;--bad-fg:#9a2f22}
@media (prefers-color-scheme:dark){:root{--bg:#1f1a16;--card:#29221c;--fg:#ece3d6;--muted:#b3a693;--accent:#e0b07a;--accent-soft:#9c7444;
--line:#3d332a;--chip:#352c24;
--ok-bg:#2a3a26;--ok-fg:#a9d69c;--warn-bg:#41361c;--warn-fg:#ebc970;--grey-bg:#38322c;--grey-fg:#c4bab0;--bad-bg:#4a2823;--bad-fg:#f0a597}}
*{box-sizing:border-box}
html{font-size:18px;-webkit-text-size-adjust:100%}
body{font-family:"Iowan Old Style","Palatino Linotype",Palatino,Charter,"Bitstream Charter",Georgia,serif;
max-width:42rem;margin:0 auto;padding:2rem 1.25rem 3rem;color:var(--fg);background:var(--bg);line-height:1.65;overflow-wrap:break-word}
a{color:var(--accent);text-underline-offset:.15em}a:hover{text-decoration-thickness:2px}
h1,h2,h3{line-height:1.25;font-weight:normal}main h1,h2.big{font-size:1.6rem;margin:2.5rem 0 .5rem}main h1:first-child{margin-top:0}main h2{font-size:1.2rem;margin:2rem 0 .5rem}h2.big{margin:2.5rem 0 .5rem}
header{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:.5rem 1.5rem;
padding-bottom:1rem;margin-bottom:2rem;border-bottom:1px solid var(--line)}
.brand{font-size:1.5rem;line-height:1.25;margin:0;letter-spacing:.02em}.brand a{text-decoration:none;color:inherit}
nav{display:flex;flex-wrap:wrap;gap:.25rem 1.25rem}nav a{text-decoration:none;color:var(--muted)}nav a:hover{color:var(--accent)}
.lede{font-size:1.1rem}.note{color:var(--muted);font-size:.9rem}.sub{color:var(--muted);margin-top:-.25rem}
table{width:100%;border-collapse:collapse;margin:1rem 0}
th{font-weight:normal;font-variant:small-caps;letter-spacing:.05em;color:var(--muted);text-align:left;padding:.4rem .5rem;border-bottom:1px solid var(--line)}
td{padding:.75rem .5rem;border-bottom:1px solid var(--line);vertical-align:top}
td.n{color:var(--muted);width:2.5rem}td.s{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}th.s{text-align:right}
td.m a{text-decoration:none;color:var(--fg);font-size:1.05rem}td.m a:hover{color:var(--accent)}
.chips{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.35rem}
.chip{font-size:.75rem;background:var(--chip);color:var(--muted);border-radius:1rem;padding:.05rem .55rem;white-space:nowrap}
@media (max-width:30rem){html{font-size:17px}body{padding:1.25rem 1rem 2rem}
table,tbody,tr,td{display:block}tr:first-child{display:none}tr{position:relative;padding:.75rem 0;border-bottom:1px solid var(--line)}
td{border:0;padding:0}td.n{position:absolute;left:0;top:.75rem}td.m{padding-left:2rem}td.s{text-align:left;padding-left:2rem;color:var(--muted);font-size:.9rem}
td.s::before{content:"Moral Rank "}}
.label{font-variant:small-caps;letter-spacing:.08em;color:var(--muted);font-size:.95rem;margin:0}
.maxim,main h1.maxim{font-size:2rem;line-height:1.3;margin:.25rem 0 2rem}
.seed{margin:0 0 1.5rem;padding:1.5rem 1.5rem 1.25rem;background:var(--card);border-left:4px solid var(--accent-soft);border-radius:.25rem}
.seed blockquote{margin:0;font-size:1.35rem;line-height:1.5}
.cite{margin-top:.75rem;font-size:.9rem;color:var(--muted)}.cite em{color:var(--fg)}
.summary{font-size:1.05rem}
.quotes{list-style:none;padding:0;margin:1rem 0;max-height:36rem;overflow-y:auto;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.quotes li{padding:1.1rem .25rem;border-bottom:1px solid var(--line)}.quotes li:last-child{border-bottom:0}
.quotes blockquote{margin:0 0 .4rem}
.meta{font-size:.85rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:.25rem .6rem;align-items:center}
.pill{display:inline-block;font-size:.72rem;line-height:1.5;padding:.05rem .6rem;border-radius:1rem;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:.02em;white-space:nowrap;vertical-align:.1em}
.v-verified{background:var(--ok-bg);color:var(--ok-fg)}.v-probable{background:var(--warn-bg);color:var(--warn-fg)}
.v-unverified{background:var(--grey-bg);color:var(--grey-fg)}.v-disputed,.v-misattributed{background:var(--bad-bg);color:var(--bad-fg)}
code,.formula{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.88rem}
.echoes{font-size:.85rem;color:var(--muted);font-style:italic;margin:.2rem 0 .3rem}
.formula{display:block;padding:.75rem 1rem;background:var(--card);border-radius:.25rem;overflow-x:auto;margin:1rem 0}
.terms{padding-left:1.2rem}.terms li{margin:.6rem 0}.val{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.85rem;color:var(--accent);white-space:nowrap}
dl.legend dt{margin-top:.9rem}dl.legend dd{margin:.2rem 0 0 0;color:var(--muted)}
.profile{margin:0 0 1.5rem;padding:1.25rem 1.5rem;background:var(--card);border-left:4px solid var(--accent-soft);border-radius:.25rem}
.profile h1{margin:.1rem 0 .4rem}.profile p{margin:.5rem 0}.profile ul{margin:.25rem 0;padding-left:1.2rem;font-size:.85rem}
.index{list-style:none;padding:0;margin:1rem 0;border-top:1px solid var(--line)}.index li{padding:.6rem .25rem;border-bottom:1px solid var(--line)}
.index li>a{text-decoration:none;font-size:1.05rem}.index .chips{margin-top:.2rem}
footer{margin-top:4rem;padding-top:1rem;border-top:1px solid var(--line);font-size:.85rem;color:var(--muted)}"""


SITE_URL = "https://42maxims.github.io"  # canonical origin; change to https://42maxims.com only after the domain is bought (issue #5)
SITE_NAME = "42 Maxims"
DEFAULT_DESC = "42 Maxims: the rules for life humanity keeps rediscovering, with sources."
SITEMAP = []  # canonical paths of indexable pages, collected as pages are written
PLAUSIBLE_SCRIPT_ID = "pa-z7AY9FcQwVk1RWlwwy4-D"  # owner's Plausible script id; empty = no analytics script
SCRIPT_ID = re.compile(r"^pa-[A-Za-z0-9_-]+$")


def analytics_snippet():
    """Owner's Plausible snippet for <head>, or "" when PLAUSIBLE_SCRIPT_ID is empty."""
    if not PLAUSIBLE_SCRIPT_ID:
        return ""
    if not SCRIPT_ID.match(PLAUSIBLE_SCRIPT_ID):
        raise ValueError(f"PLAUSIBLE_SCRIPT_ID must match ^pa-[A-Za-z0-9_-]+$, got {PLAUSIBLE_SCRIPT_ID!r}")
    return (
        "<!-- Privacy-friendly analytics by Plausible -->\n"
        f'<script async src="https://plausible.io/js/{PLAUSIBLE_SCRIPT_ID}.js"></script>\n'
        "<script>\n"
        "  window.plausible=window.plausible||function(){(plausible.q=plausible.q||[]).push(arguments)},plausible.init=plausible.init||function(i){plausible.o=i||{}};\n"
        "  plausible.init()\n"
        "</script>\n"
    )


def blurb(text, n=155):
    """Plain-text meta description: whitespace collapsed, cut at a word boundary with an ellipsis if over n chars."""
    t = " ".join(re.sub(r"<[^>]+>", " ", html.unescape(text)).split())
    if len(t) <= n:
        return t
    return t[:n - 1].rsplit(" ", 1)[0].rstrip(" ,;:.—-") + "…"


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c") + "</script>"


def page(title, body, depth, path=None, desc=None, kind="website", noindex=False, jsonld=(), crumbs=None):
    """path: canonical path ("" = home, "voices/x/"); None means no canonical or sitemap entry (e.g. 404)."""
    up = "../" * depth
    desc = blurb(desc or DEFAULT_DESC)
    head = f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">'
    if noindex or path is None:
        head += '<meta name="robots" content="noindex,follow">'
    if path is not None:
        url = f"{SITE_URL}/{path}"
        head += (f'<link rel="canonical" href="{url}">'
                 f'<meta property="og:site_name" content="{SITE_NAME}"><meta property="og:locale" content="en_IE">'
                 f'<meta property="og:type" content="{kind}"><meta property="og:title" content="{esc(title)}">'
                 f'<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">'
                 f'<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(title)}">'
                 f'<meta name="twitter:description" content="{esc(desc)}">')
        if not noindex:
            SITEMAP.append(path)
            graph = list(jsonld)
            if crumbs is not None:
                items = [("Home", "")] + list(crumbs) + [(title.split(" — ")[0], path)]
                graph.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": n + 1, "name": nm, "item": f"{SITE_URL}/{p}"} for n, (nm, p) in enumerate(items)]})
            head += "".join(ld(g) for g in graph)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
{head}
<link rel="stylesheet" href="{up}style.css">{analytics_snippet()}</head><body>
<header><p class="brand"><a href="{up}">42 Maxims</a></p><nav aria-label="Main"><a href="{up}">The 42</a><a href="{up}voices/">Voices</a><a href="{up}sources/">Sources</a><a href="{up}method/">Method</a><a href="{up}about/">About</a></nav></header>
<main>{body}</main>
<footer>Content licensed <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Quotes remain the property of their authors and translators.
Found an error? <a href="https://github.com/42maxims/42maxims.github.io">Open an issue or pull request</a>.</footer></body></html>"""


def write(rel, txt):
    p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(txt)


def pill(ver):
    return f'<span class="pill v-{ver}" title="{esc(VER_TITLE[ver])}">{VER_LABEL[ver]}</span>'


def weight(q):
    return VER[q["ver"]] * REL[q["rel"]] * q["conf"]


def seed_index(c, qs):
    """Oldest era first, then strongest verification, then file order; concept "seed" overrides."""
    s = c.get("seed")
    if isinstance(s, int) and 0 <= s < len(qs):
        return s
    return min(range(len(qs)), key=lambda i: (ERA_ORDER.index(qs[i]["era"]), VER_ORDER.index(qs[i]["ver"]), i))


quotes_by = {}
for q in D["quotes"]:
    quotes_by.setdefault(q["concept"], []).append(q)
E, BD = {}, {}
for c in D["concepts"]:
    E[c["slug"]], BD[c["slug"]] = evidence(quotes_by.get(c["slug"], []), TR)
MR, _ = moral_rank(E, [])
MAX_E = max(E.values()) if E else 0
order = sorted(D["concepts"], key=lambda c: (-MR[c["slug"]], -BD[c["slug"]]["T"], -BD[c["slug"]]["K"]))
write("data/generated/scores.json", json.dumps({s: dict(BD[s], moral_rank=round(MR[s], 1)) for s in MR}, indent=1))


def reason(c):
    if c.get("hold"):
        return "awaiting a stronger second source"
    if BD[c["slug"]]["traditions"] < 2:
        return "awaiting a second tradition"
    return f"ranked just below the top {TOP_N}"


def row(c, i, why=False):
    b = BD[c["slug"]]; qs = quotes_by.get(c["slug"], [])
    thinkers = len({q["thinker"] for q in qs})
    plural = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return (f'<tr><td class="n">{i}</td><td class="m"><a href="maxims/{c["slug"]}/">{esc(c["maxim"])}</a>'
            f'<div class="chips"><span class="chip">{plural(len(qs), "quote")}</span><span class="chip">{plural(thinkers, "voice")}</span>'
            f'<span class="chip">{plural(b["traditions"], "tradition")}</span><span class="chip">{plural(b["R"], "period")}</span>'
            + (f'<span class="chip why">{reason(c)}</span>' if why else '') + '</div></td>'
            f'<td class="s">{MR[c["slug"]]:.1f}</td></tr>')


def table(cs, why=False):
    return ('<table><tr><th>#</th><th>Maxim</th><th class="s">Moral Rank</th></tr>'
            + "".join(row(c, i + 1, why) for i, c in enumerate(cs)) + "</table>")


qualifying = [c for c in order if BD[c["slug"]]["traditions"] >= 2 and not c.get("hold")]
main = qualifying[:TOP_N]
emerging = [c for c in order if c not in main]
body = ('<p class="lede">Some ideas keep turning up, in different centuries and different languages, from people who never met. '
        "This is a slow, careful collection of them: each maxim with its sources, ranked by how widely and independently humanity has arrived at it.</p>"
        "<h1>The 42</h1><p class=\"sub\">The 42 highest-ranked maxims</p>"
        f'<p class="note">{len(qualifying)} maxims are now shared by at least two independent traditions; these are the {len(main)} that rank highest among them. '
        "It is still an early collection, and the order will keep shifting gently as new sources are found.</p>"
        + table(main) +
        "<h2 class=\"big\">Emerging</h2><p>Maxims just outside The 42. Some rank just below the top; others are waiting for stronger backing from a second tradition. Each is marked with its reason, and any of them can join as new sources are found.</p>"
        + table(emerging, True))
write("index.html", page("42 Maxims — rules for life, with sources", body, 0, "",
                         "Some ideas keep turning up in different centuries and languages. 42 Maxims ranks them by how widely and independently humanity arrived at them, with sources.",
                         jsonld=[{"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/",
                                  "description": DEFAULT_DESC, "inLanguage": "en"}]))


def voice_link(q, up):
    return f'<a href="{up}voices/{q["voice"]}/">{esc(q["thinker"])}</a>'


def work_link(q, up):
    return f'<a href="{up}sources/{q["source_id"]}/"><em>{esc(q["work"])}</em></a>'


def source_link(q):
    return f'<a href="{esc(q["source"])}">source</a>' if q["source"] else "no source yet"


def echoes(q):
    """Optional note naming the older saying a quote restates, e.g. "Epictetus, Enchiridion 5"."""
    e = q.get("echoes", "").strip()
    return f'<div class="echoes">Echoes {esc(e)}</div>' if e else ""


def cite(q, up="../../"):
    return f'— {voice_link(q, up)}, {work_link(q, up)} · {source_link(q)} {pill(q["ver"])}'


def related(q, up="../../"):
    parts = [esc(TR[q["tradition"]]["name"]), ERA_LABEL.get(q["era"], q["era"]), f'relation: {q["rel"]}', pill(q["ver"]), source_link(q)]
    if q.get("translation"):
        parts.append(f'Translation: {esc(q["translation"])}')
    return (f'<li><blockquote>“{esc(q["text"])}”</blockquote><div class="cite">— {voice_link(q, up)}, {work_link(q, up)}</div>{echoes(q)}'
            f'<div class="meta">{"".join(f"<span>{p}</span>" for p in parts)}</div></li>')


FORMULA = (f'<code class="formula">E = ln(1+Q) + √K + {W_T:g}·T + {W_R:g}·R'
           "<br>Moral Rank = 100 × E / max E</code>")


def score_terms(b=None, slug=None, qs=()):
    """Plain-words explanation of each term; with b given, show this maxim's values beside each bullet."""
    v = (lambda s: f' <span class="val">{s}</span>') if b else (lambda s: "")
    tdetail = ""
    if b:
        best = {}
        for q in qs:
            best[q["tradition"]] = max(best.get(q["tradition"], 0), weight(q))
        supporting = {t for t, w in best.items() if w > 0}
        items = []
        for t, w in sorted(best.items(), key=lambda x: -x[1]):
            half = bool(ancestors(t, TR) & supporting)
            items.append(f'{esc(TR[t]["name"])} {w:.2f}' + (" × 0.5 (derived)" if half else ""))
        tdetail = f'<br><small class="note">{"; ".join(items)}</small>' if items else ""
    lis = [
        "<strong>Quote weight w</strong> = verification (verified 1.0, probable 0.6, disputed 0.2, unverified 0, misattributed 0) "
        "× relation (expresses 1.0, similar 0.7, partial 0.4, contrasts 0) × our confidence that the quote fits the maxim.",
        "<strong>Q</strong> is the sum of all quote weights. It sits under a logarithm, so each extra quote adds a little less than the last."
        + (v(f"Q = {b['Q']:.2f} → ln(1+Q) = {W_Q * math.log(1 + b['Q']):.2f}") if b else ""),
        "<strong>K</strong> counts each thinker once, at their strongest quote, under a square root: many voices matter, but with diminishing returns."
        + (v(f"K = {b['K']:.2f} → √K = {W_K * math.sqrt(b['K']):.2f}") if b else ""),
        f"<strong>T</strong> adds up the distinct traditions, each counted at its strongest quote, with weight {W_T:g}. "
        "A tradition that grew out of another tradition already supporting the maxim (for example Christianity from Judaism) counts half (0.5)."
        + (v(f"T = {b['T']:.2f} → {W_T:g}·T = {W_T * b['T']:.2f}") + tdetail if b else ""),
        f"<strong>R</strong> is the number of distinct time periods (listed below) with at least one quote weighing 0.3 or more, with weight {W_R:g}."
        + (v(f"R = {b['R']} → {W_R:g}·R = {W_R * b['R']:.2f}") if b else ""),
        "<strong>Moral Rank</strong> divides E by the highest E on the site and scales to 100, so the best-supported maxim scores 100. "
        "Concepts are not linked to one another yet, so nothing propagates between them."
        + (v(f"E = {b['E']:.2f}, max E = {MAX_E:.2f} → {MR[slug]:.1f}") if b else ""),
    ]
    return '<ul class="terms">' + "".join(f"<li>{x}</li>" for x in lis) + "</ul>"


for c in D["concepts"]:
    b = BD[c["slug"]]; qs = quotes_by.get(c["slug"], [])
    body = f'<p class="label">Maxim</p><h1 class="maxim">{esc(c["maxim"])}</h1>'
    si = None
    if qs:
        si = seed_index(c, qs); s = qs[si]
        tr = f'<br>Translation: {esc(s["translation"])}' if s.get("translation") else ""
        body += (f'<figure class="seed"><blockquote>“{esc(s["text"])}”</blockquote>'
                 f'<figcaption class="cite">{cite(s)}<br>{esc(TR[s["tradition"]]["name"])} · {ERA_LABEL.get(s["era"], s["era"])}{tr}{echoes(s)}</figcaption></figure>')
    body += f'<p class="summary">{esc(c["summary"])}</p>'
    if c.get("hold"):
        body += f'<p class="note"><strong>On hold for The 42:</strong> {esc(c["hold"])}</p>'
    rest = [q for i, q in enumerate(qs) if i != si]
    if rest:
        body += f'<h2>Related expressions</h2><ul class="quotes">{"".join(related(q) for q in rest)}</ul>'
    body += (f'<h2>Score</h2><p>Moral Rank <strong>{MR[c["slug"]]:.1f}</strong> · Evidence E = {b["E"]:.2f}</p>'
             + f'<p class="formula"><code>E = ln(1+{b["Q"]:.2f}) + √{b["K"]:.2f} + 3·{b["T"]:.2f} + 1.5·{b["R"]} = {b["E"]:.2f}</code></p>'
             + '<p class="howto"><small><a href="../../method/">How this is scored</a></small></p>')
    links = "".join(f'<li><a href="{esc(u)}">{esc(u)}</a></li>' for u in c.get("links", []))
    if links:
        body += f"<h2>Further reading</h2><ul>{links}</ul>"
    ldq = []
    if qs:
        ldq = [{"@context": "https://schema.org", "@type": "Quotation", "text": s["text"], "creator": {"@type": "Person", "name": s["thinker"]},
                "isPartOf": {"@type": "CreativeWork", "name": s["work"]}, "inLanguage": "en"}] if VOICES[s["voice"]]["kind"] == "person" else []
    write(f"maxims/{c['slug']}/index.html", page(f"{c['maxim']} — 42 Maxims", body, 2, f"maxims/{c['slug']}/",
          c["summary"], "article", jsonld=ldq, crumbs=[]))

CONCEPT = {c["slug"]: c for c in D["concepts"]}


def profile(e, heading, extra=()):
    """Summary block at the top of a voice or source page."""
    facts = [esc(e["dates"]), esc(TR[e["tradition"]]["name"]), ERA_LABEL[e["period"]], *extra]
    refs = "".join(f'<li><a href="{esc(u)}">{esc(u)}</a></li>' for u in e["refs"])
    note = f'<p class="note">{CONFIDENCE_NOTE[e["confidence"]]}</p>' if e["confidence"] in CONFIDENCE_NOTE else ""
    return (f'<section class="profile"><h1>{esc(heading)}</h1><div class="meta">{"".join(f"<span>{f}</span>" for f in facts)}</div>'
            f'<p>{esc(e["summary"])}</p>{note}' + (f'<p class="label">References</p><ul>{refs}</ul>' if refs else "") + "</section>")


def entry_quote(q, show_voice, show_work):
    """One quote on a voice or source page (depth 2): who/where it is from, verification, locus and its maxim."""
    who = voice_link(q, "../../") if show_voice else esc(q["thinker"])
    where = work_link(q, "../../") if show_work else f'<em>{esc(q["work"])}</em>'
    c = CONCEPT[q["concept"]]
    parts = [pill(q["ver"]), source_link(q), f'Maxim: <a href="../../maxims/{c["slug"]}/">{esc(c["maxim"])}</a>']
    if q.get("translation"):
        parts.append(f'Translation: {esc(q["translation"])}')
    return (f'<li><blockquote>“{esc(q["text"])}”</blockquote><div class="cite">— {who}, {where}</div>{echoes(q)}'
            f'<div class="meta">{"".join(f"<span>{p}</span>" for p in parts)}</div></li>')


def sort_key(name):
    n = name.lower()
    return n[4:] if n.startswith("the ") else n


def plural(n, w):
    return f"{n} {w}{'' if n == 1 else 's'}"


def index_page(entries, label, kinds, counts, base, title, intro):
    items = []
    for slug, e in sorted(entries.items(), key=lambda x: sort_key(x[1][label])):
        chips = [kinds[e["kind"]], plural(len(counts.get(slug, [])), "quote"), esc(e["dates"])]
        items.append(f'<li><a href="{slug}/">{esc(e[label])}</a><div class="chips">'
                     + "".join(f'<span class="chip">{x}</span>' for x in chips) + "</div></li>")
    write(f"{base}/index.html", page(f"{title} — 42 Maxims", f'<h1>{title}</h1><p>{intro}</p><ul class="index">{"".join(items)}</ul>', 1,
                                          f"{base}/", intro, crumbs=[]))


quotes_by_voice, quotes_by_source = {}, {}
for q in D["quotes"]:
    quotes_by_voice.setdefault(q["voice"], []).append(q)
    quotes_by_source.setdefault(q["source_id"], []).append(q)

for slug, v in VOICES.items():
    qs = quotes_by_voice.get(slug, [])
    works = sorted((k for k, s in SOURCES.items() if s["voice"] == slug), key=lambda k: sort_key(SOURCES[k]["title"]))
    body = '<p class="label">Voice</p>' + profile(v, v["name"], [VOICE_KIND[v["kind"]]])
    if works:
        body += "<h2>Works</h2><ul>" + "".join(f'<li><a href="../../sources/{k}/"><em>{esc(SOURCES[k]["title"])}</em></a></li>' for k in works) + "</ul>"
    if qs:
        body += f'<h2>Quotes ({len(qs)})</h2><ul class="quotes">{"".join(entry_quote(q, False, True) for q in qs)}</ul>'
    else:
        body += '<p class="note">No quotes are credited directly to this voice yet; see the works above.</p>'
    ldv = [{"@context": "https://schema.org", "@type": "Person", "name": v["name"], "description": v["summary"]}] if v["kind"] == "person" else []
    write(f"voices/{slug}/index.html", page(f"{v['name']} — 42 Maxims", body, 2, f"voices/{slug}/", v["summary"],
          "profile", noindex=not (qs or works), jsonld=ldv, crumbs=[("Voices", "voices/")]))

for slug, s in SOURCES.items():
    qs = quotes_by_source.get(slug, [])
    extra = [SOURCE_KIND[s["kind"]]]
    if s["voice"]:
        extra.insert(0, f'<a href="../../voices/{s["voice"]}/">{esc(VOICES[s["voice"]]["name"])}</a>')
    body = '<p class="label">Source</p>' + profile(s, s["title"], extra)
    body += f'<h2>Quotes ({len(qs)})</h2><ul class="quotes">{"".join(entry_quote(q, True, False) for q in qs)}</ul>'
    write(f"sources/{slug}/index.html", page(f"{s['title']} (source) — 42 Maxims", body, 2, f"sources/{slug}/", s["summary"],
          noindex=not qs, crumbs=[("Sources", "sources/")]))

index_page(VOICES, "name", VOICE_KIND, quotes_by_voice, "voices", "Voices",
           "The people, communities and texts behind the quotes, from named thinkers to anonymous sayings. "
           "Where authorship is disputed or a saying is misattributed, the voice page says so.")
index_page(SOURCES, "title", SOURCE_KIND, quotes_by_source, "sources", "Sources",
           "The books, scriptures, collections and talks the quotes come from. Each quote's exact chapter, verse and translation are shown beside it.")

legend = "".join(f"<dt>{pill(k)}</dt><dd>{d}</dd>" for k, d in [
    ("verified", "Wording checked against a primary text, a reputable or public-domain translation, or the author's own book, site or recorded talk."),
    ("probable", "Wording found only in a reliable secondary source, such as Wikipedia or Wikiquote with a cited work. Counts at 0.6."),
    ("disputed", "Credible sources disagree about who said it or how. Counts at 0.2."),
    ("unverified", "A popular saying with no traceable origin. Shown, but scores zero."),
    ("misattributed", "The saying is real but the attribution is known to be wrong. We show it because people will look for it, "
                      "record the true origin where known, and give it no weight.")])

PERIODS = "".join(f"<li>{ERA_LABEL[e]}</li>" for e in ERA_ORDER)
write("method/index.html", page("Method — 42 Maxims", f"""<h1>How Moral Rank works</h1>
<p>Moral Rank asks one question: <strong>how widely, independently and reliably has humanity arrived at this idea?</strong></p>
<p>Breadth matters more than volume: each independent tradition adds a lot, each time period adds a good deal, while extra quotes and thinkers add less and less.</p>
{FORMULA}
{score_terms()}
<p>The score measures <em>convergence</em>, not truth or moral worth. We never rank traditions or thinkers, only ideas.
Full details are in <a href="https://github.com/42maxims/42maxims.github.io/blob/master/SPEC.md">the spec</a>.</p>
<h2>Time periods</h2><p>Each quote is placed in one period by when it was written or first recorded:</p><ul>{PERIODS}</ul>
<h2>Verification labels</h2><dl class="legend">{legend}</dl>
<p>Translations of non-English texts are public-domain or credited translations. Where we make our own, they are AI-assisted and labelled as such.</p>""", 1,
 "method/", "How Moral Rank works: each maxim is scored on how many quotes, thinkers, independent traditions and time periods express it, with verification labels explained.",
 crumbs=[]))

write("about/index.html", page("About — 42 Maxims", """<h1>About</h1>
<p>42 Maxims gathers the short rules for living that keep reappearing across religions, philosophies, science and popular wisdom, and links every one to its sources.</p>
<p>It is an open project. Anyone can suggest a maxim, a quote or a correction by opening an issue or pull request on
<a href="https://github.com/42maxims/42maxims.github.io">GitHub</a>. The site is in English first; other languages will follow.</p>
<p>Our own writing is licensed CC BY-SA 4.0. Short quotations from modern authors are included with attribution for commentary.</p>""", 1,
 "about/", "42 Maxims gathers the short rules for living that keep reappearing across religions, philosophies, science and popular wisdom, and links every one to its sources.", crumbs=[]))
write("style.css", CSS)
write("404.html", page("Not found — 42 Maxims", "<h1>Page not found</h1><p>That page isn't here. <a href='/'>Back to The 42</a>.</p>", 0))
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"<url><loc>{SITE_URL}/{p}</loc></url>\n" for p in sorted(SITEMAP)) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
print("built", len(D["concepts"]), "maxims,", len(VOICES), "voices,", len(SOURCES), "sources")
