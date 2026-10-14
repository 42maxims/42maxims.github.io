"""Builds the static site from data/maxims.json. Run: python3 build.py (no dependencies)."""
import json, os, html, math
from scoring import evidence, moral_rank, ancestors, VER, REL, W_Q, W_K, W_T, W_R

ROOT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(ROOT, "data/maxims.json")))
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
h1,h2,h3{line-height:1.25;font-weight:normal}h2{font-size:1.6rem;margin:2.5rem 0 .5rem}h3{font-size:1.2rem;margin:2rem 0 .5rem}
header{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:.5rem 1.5rem;
padding-bottom:1rem;margin-bottom:2rem;border-bottom:1px solid var(--line)}
header h1{font-size:1.5rem;margin:0;letter-spacing:.02em}header h1 a{text-decoration:none;color:inherit}
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
.maxim{font-size:2rem;line-height:1.3;margin:.25rem 0 2rem}
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
.formula{display:block;padding:.75rem 1rem;background:var(--card);border-radius:.25rem;overflow-x:auto;margin:1rem 0}
.terms{padding-left:1.2rem}.terms li{margin:.6rem 0}.val{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.85rem;color:var(--accent);white-space:nowrap}
dl.legend dt{margin-top:.9rem}dl.legend dd{margin:.2rem 0 0 0;color:var(--muted)}
footer{margin-top:4rem;padding-top:1rem;border-top:1px solid var(--line);font-size:.85rem;color:var(--muted)}"""


def page(title, body, depth):
    up = "../" * depth
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{esc(title)}</title><meta name="description" content="42 Maxims: the rules for life humanity keeps rediscovering, with sources.">
<link rel="stylesheet" href="{up}style.css"></head><body>
<header><h1><a href="{up}">42 Maxims</a></h1><nav><a href="{up}">The 42</a><a href="{up}method/">Method</a><a href="{up}about/">About</a></nav></header>
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


def row(c, i):
    b = BD[c["slug"]]; qs = quotes_by.get(c["slug"], [])
    thinkers = len({q["thinker"] for q in qs})
    plural = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return (f'<tr><td class="n">{i}</td><td class="m"><a href="maxims/{c["slug"]}/">{esc(c["maxim"])}</a>'
            f'<div class="chips"><span class="chip">{plural(len(qs), "quote")}</span><span class="chip">{plural(thinkers, "voice")}</span>'
            f'<span class="chip">{plural(b["traditions"], "tradition")}</span><span class="chip">{plural(b["R"], "period")}</span></div></td>'
            f'<td class="s">{MR[c["slug"]]:.1f}</td></tr>')


def table(cs):
    return ('<table><tr><th>#</th><th>Maxim</th><th class="s">Moral Rank</th></tr>'
            + "".join(row(c, i + 1) for i, c in enumerate(cs)) + "</table>")


qualifying = [c for c in order if BD[c["slug"]]["traditions"] >= 2 and not c.get("hold")]
main = qualifying[:TOP_N]
emerging = [c for c in order if c not in main]
body = ('<p class="lede">Some ideas keep turning up, in different centuries and different languages, from people who never met. '
        "This is a slow, careful collection of them: each maxim with its sources, ranked by how widely and independently humanity has arrived at it.</p>"
        "<h2>The 42</h2><p class=\"sub\">The 42 highest-ranked maxims</p>"
        f'<p class="note">{len(qualifying)} maxims are now shared by at least two independent traditions; these are the {len(main)} that rank highest among them. '
        "It is still an early collection, and the order will keep shifting gently as new sources are found.</p>"
        + table(main) +
        "<h2>Emerging</h2><p>Maxims that just missed The 42, plus those supported by only one tradition so far (or whose second source is still too loose a match). They can join once ranked high enough or once a second, independent tradition is sourced.</p>"
        + table(emerging))
write("index.html", page("42 Maxims — rules for life, with sources", body, 0))


def cite(q):
    src = f'<a href="{esc(q["source"])}">source</a>' if q["source"] else "no source yet"
    return f'— {esc(q["thinker"])}, <em>{esc(q["work"])}</em> · {src} {pill(q["ver"])}'


def related(q):
    parts = [esc(TR[q["tradition"]]["name"]), ERA_LABEL.get(q["era"], q["era"]), f'relation: {q["rel"]}', pill(q["ver"])]
    parts.append(f'<a href="{esc(q["source"])}">source</a>' if q["source"] else "no source yet")
    if q.get("translation"):
        parts.append(f'Translation: {esc(q["translation"])}')
    return (f'<li><blockquote>“{esc(q["text"])}”</blockquote><div class="cite">— {esc(q["thinker"])}, <em>{esc(q["work"])}</em></div>'
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
    body = f'<p class="label">Maxim</p><h2 class="maxim">{esc(c["maxim"])}</h2>'
    si = None
    if qs:
        si = seed_index(c, qs); s = qs[si]
        tr = f'<br>Translation: {esc(s["translation"])}' if s.get("translation") else ""
        body += (f'<figure class="seed"><blockquote>“{esc(s["text"])}”</blockquote>'
                 f'<figcaption class="cite">{cite(s)}<br>{esc(TR[s["tradition"]]["name"])} · {ERA_LABEL.get(s["era"], s["era"])}{tr}</figcaption></figure>')
    body += f'<p class="summary">{esc(c["summary"])}</p>'
    if c.get("hold"):
        body += f'<p class="note"><strong>On hold for The 42:</strong> {esc(c["hold"])}</p>'
    rest = [q for i, q in enumerate(qs) if i != si]
    if rest:
        body += f'<h3>Related expressions</h3><ul class="quotes">{"".join(related(q) for q in rest)}</ul>'
    body += (f'<h3>Score</h3><p>Moral Rank <strong>{MR[c["slug"]]:.1f}</strong> · Evidence E = {b["E"]:.2f}</p>'
             + f'<p class="formula"><code>E = ln(1+{b["Q"]:.2f}) + √{b["K"]:.2f} + 3·{b["T"]:.2f} + 1.5·{b["R"]} = {b["E"]:.2f}</code></p>'
             + '<p class="howto"><small><a href="../../method/">How this is scored</a></small></p>')
    links = "".join(f'<li><a href="{esc(u)}">{esc(u)}</a></li>' for u in c.get("links", []))
    if links:
        body += f"<h3>Further reading</h3><ul>{links}</ul>"
    write(f"maxims/{c['slug']}/index.html", page(f"{c['maxim']} — 42 Maxims", body, 2))

legend = "".join(f"<dt>{pill(k)}</dt><dd>{d}</dd>" for k, d in [
    ("verified", "Wording checked against a primary text, a reputable or public-domain translation, or the author's own book, site or recorded talk."),
    ("probable", "Wording found only in a reliable secondary source, such as Wikipedia or Wikiquote with a cited work. Counts at 0.6."),
    ("disputed", "Credible sources disagree about who said it or how. Counts at 0.2."),
    ("unverified", "A popular saying with no traceable origin. Shown, but scores zero."),
    ("misattributed", "The saying is real but the attribution is known to be wrong. We show it because people will look for it, "
                      "record the true origin where known, and give it no weight.")])

PERIODS = "".join(f"<li>{ERA_LABEL[e]}</li>" for e in ERA_ORDER)
write("method/index.html", page("Method — 42 Maxims", f"""<h2>How Moral Rank works</h2>
<p>Moral Rank asks one question: <strong>how widely, independently and reliably has humanity arrived at this idea?</strong></p>
<p>Breadth matters more than volume: each independent tradition adds a lot, each time period adds a good deal, while extra quotes and thinkers add less and less.</p>
{FORMULA}
{score_terms()}
<p>The score measures <em>convergence</em>, not truth or moral worth. We never rank traditions or thinkers, only ideas.
Full details are in <a href="https://github.com/42maxims/42maxims.github.io/blob/master/SPEC.md">the spec</a>.</p>
<h3>Time periods</h3><p>Each quote is placed in one period by when it was written or first recorded:</p><ul>{PERIODS}</ul>
<h3>Verification labels</h3><dl class="legend">{legend}</dl>
<p>Translations of non-English texts are public-domain or credited translations. Where we make our own, they are AI-assisted and labelled as such.</p>""", 1))

write("about/index.html", page("About — 42 Maxims", """<h2>About</h2>
<p>42 Maxims gathers the short rules for living that keep reappearing across religions, philosophies, science and popular wisdom, and links every one to its sources.</p>
<p>It is an open project. Anyone can suggest a maxim, a quote or a correction by opening an issue or pull request on
<a href="https://github.com/42maxims/42maxims.github.io">GitHub</a>. The site is in English first; other languages will follow.</p>
<p>Our own writing is licensed CC BY-SA 4.0. Short quotations from modern authors are included with attribution for commentary.</p>""", 1))
write("style.css", CSS)
write("404.html", page("Not found — 42 Maxims", "<p>That page isn't here. <a href='/'>Back to The 42</a>.</p>", 0))
print("built", len(D["concepts"]), "maxims")
