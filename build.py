"""Builds the static site from data/maxims.json. Run: python3 build.py (no dependencies)."""
import json, os, html
from scoring import evidence, moral_rank

ROOT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(ROOT, "data/maxims.json")))
TR = D["traditions"]
esc = html.escape
VER_LABEL = {"verified": "Verified against source", "probable": "Probable (secondary source)",
             "unverified": "Unverified", "disputed": "Disputed", "misattributed": "Misattributed"}

CSS = """body{font-family:Georgia,serif;max-width:46rem;margin:2rem auto;padding:0 1rem;color:#2b2b2b;background:#fbf8f2;line-height:1.6}
a{color:#7a4b1f}header a{text-decoration:none;color:inherit}nav a{margin-right:1rem}
table{width:100%;border-collapse:collapse}td,th{padding:.4rem;border-bottom:1px solid #e4dccd;text-align:left;vertical-align:top}
blockquote{margin:1rem 0;padding:.5rem 1rem;border-left:3px solid #c9a46a;background:#fff}
.chip{font-size:.8rem;background:#efe6d6;border-radius:1rem;padding:.1rem .5rem;margin-right:.3rem;white-space:nowrap}
.v-verified{color:#2e6b2e}.v-probable{color:#8a6d00}.v-unverified{color:#a33}footer{margin-top:3rem;font-size:.85rem;color:#666}"""

def page(title, body, depth):
    up = "../" * depth
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="42 Maxims: the rules for life humanity keeps rediscovering, with sources.">
<link rel="stylesheet" href="{up}style.css"></head><body>
<header><h1><a href="{up}">42 Maxims</a></h1><nav><a href="{up}">Scoreboard</a><a href="{up}method/">Method</a><a href="{up}about/">About</a></nav></header>
<main>{body}</main>
<footer>Content licensed <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. Quotes remain the property of their authors and translators.
Found an error? <a href="https://github.com/42maxims/42maxims.github.io">Open an issue or pull request</a>.</footer></body></html>"""

def write(rel, txt):
    p = os.path.join(ROOT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(txt)

quotes_by = {}
for q in D["quotes"]:
    quotes_by.setdefault(q["concept"], []).append(q)
E, BD = {}, {}
for c in D["concepts"]:
    E[c["slug"]], BD[c["slug"]] = evidence(quotes_by.get(c["slug"], []), TR)
MR, _ = moral_rank(E, [])
order = sorted(D["concepts"], key=lambda c: (-MR[c["slug"]], -BD[c["slug"]]["T"], -BD[c["slug"]]["K"]))
write("data/generated/scores.json", json.dumps({s: dict(BD[s], moral_rank=round(MR[s], 1)) for s in MR}, indent=1))

def row(c, i):
    b = BD[c["slug"]]; qs = quotes_by.get(c["slug"], [])
    return (f'<tr><td>{i}</td><td><a href="maxims/{c["slug"]}/">{esc(c["maxim"])}</a><br>'
            f'<span class="chip">{len(qs)} quote(s)</span><span class="chip">{b["traditions"]} tradition(s)</span>'
            f'<span class="chip">{b["R"]} era(s)</span></td><td>{MR[c["slug"]]:.1f}</td></tr>')

main = [c for c in order if BD[c["slug"]]["traditions"] >= 2]
emerging = [c for c in order if BD[c["slug"]]["traditions"] < 2]
body = ("<p>Some ideas keep turning up, in different centuries and different languages, from people who never met. "
        "This is a slow, careful collection of them: each maxim with its sources, ranked by how widely and independently humanity has arrived at it.</p>"
        "<p><em>This is an early seed. Rankings will move a lot as sources are added.</em></p>"
        "<h2>Scoreboard</h2><table><tr><th>#</th><th>Maxim</th><th>Moral Rank</th></tr>"
        + "".join(row(c, i + 1) for i, c in enumerate(main)) + "</table>"
        "<h2>Emerging</h2><p>Maxims supported by only one tradition so far. They join the scoreboard once a second, independent tradition is sourced.</p>"
        "<table><tr><th>#</th><th>Maxim</th><th>Moral Rank</th></tr>"
        + "".join(row(c, i + 1) for i, c in enumerate(emerging)) + "</table>")
write("index.html", page("42 Maxims — rules for life, with sources", body, 0))

for c in D["concepts"]:
    b = BD[c["slug"]]
    qh = ""
    for q in quotes_by.get(c["slug"], []):
        src = f'<a href="{esc(q["source"])}">source</a>' if q["source"] else "no source yet"
        tr = f' · Translation: {esc(q["translation"])}' if q.get("translation") else ""
        qh += (f'<blockquote>“{esc(q["text"])}”<br>— {esc(q["thinker"])}, <em>{esc(q["work"])}</em><br>'
               f'<small>{esc(TR[q["tradition"]]["name"])} · {q["era"]} · {q["rel"]} · '
               f'<span class="v-{q["ver"]}">{VER_LABEL[q["ver"]]}</span> · {src}{tr}</small></blockquote>')
    links = "".join(f'<li><a href="{esc(u)}">{esc(u)}</a></li>' for u in c.get("links", []))
    body = (f'<h2>{esc(c["maxim"])}</h2><p>{esc(c["summary"])}</p><h3>Voices</h3>{qh}'
            f'<h3>Score</h3><p>Moral Rank {MR[c["slug"]]:.1f} · Evidence {b["E"]:.2f} '
            f'(Q {b["Q"]:.2f}, K {b["K"]:.2f}, T {b["T"]:.2f}, R {b["R"]})</p>'
            + (f"<h3>Further reading</h3><ul>{links}</ul>" if links else ""))
    write(f"maxims/{c['slug']}/index.html", page(f"{c['maxim']} — 42 Maxims", body, 2))

write("method/index.html", page("Method — 42 Maxims", """<h2>How Moral Rank works</h2>
<p>Moral Rank asks one question: <strong>how widely, independently and reliably has humanity arrived at this idea?</strong></p>
<p>Each quote is weighted by how well it is verified (verified 1.0, probable 0.6, unverified 0) and how closely it expresses the maxim.
Breadth matters more than volume: each independent tradition adds a lot, each era adds a good deal, while extra quotes and thinkers add less and less.
A tradition that grew out of another already supporting the maxim (for example Christianity from Judaism) counts at half weight.</p>
<p><code>E = ln(1+Q) + √K + 3·T + 1.5·R</code>, then normalised so the top maxim scores 100.</p>
<p>The score measures <em>convergence</em>, not truth or moral worth. We never rank traditions or thinkers, only ideas.
Full details are in <a href="https://github.com/42maxims/42maxims.github.io/blob/master/SPEC.md">the spec</a>.</p>
<h3>Verification labels</h3><p><span class="v-verified">Verified</span>: wording checked against a primary text or a reputable translation.
<span class="v-probable">Probable</span>: checked against a reliable secondary source only. <span class="v-unverified">Unverified</span>: origin unknown; shown, but scores zero.</p>
<p>Translations of non-English texts are public-domain or credited translations. Where we make our own, they are AI-assisted and labelled as such.</p>""", 1))

write("about/index.html", page("About — 42 Maxims", """<h2>About</h2>
<p>42 Maxims gathers the short rules for living that keep reappearing across religions, philosophies, science and popular wisdom, and links every one to its sources.</p>
<p>It is an open project. Anyone can suggest a maxim, a quote or a correction by opening an issue or pull request on
<a href="https://github.com/42maxims/42maxims.github.io">GitHub</a>. The site is in English first; other languages will follow.</p>
<p>Our own writing is licensed CC BY-SA 4.0. Short quotations from modern authors are included with attribution for commentary.</p>""", 1))
write("style.css", CSS)
write("404.html", page("Not found — 42 Maxims", "<p>That page isn't here. <a href='/'>Back to the scoreboard</a>.</p>", 0))
print("built", len(D["concepts"]), "maxims")
