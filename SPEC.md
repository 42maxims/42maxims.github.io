# 42 Maxims: Product & Build Spec

**Owner:** the project owner (anonymous) · **Maintainer identity:** Max Ims (GitHub `42maxims`) · **Operator:** oo-42maxims (app operating officer bot) briefing Claude Code
**Repo:** `42maxims/42maxims.github.io` · **Live:** https://42maxims.github.io · **Status:** v0.2, rewritten to match the site as built (2026-10-14)
**Working name:** 42 Maxims. "42" is the brand and the size of the main list (The 42), not a limit on the catalogue.

Throughout this spec, **[Built]** marks what exists on the live site today and **[Planned]** marks the long-term vision. Where the built site differs from an earlier plan, the built version is described and the plan is kept as [Planned].

---

## 1. What we're building

42 Maxims is a published, sourced collection of the rules for living that humanity keeps rediscovering. Each **maxim** (a short core rule such as "Treat others as you would wish to be treated") gathers **quotes** from philosophers, thinkers, religious and wisdom texts, and popular sayings that express it. Many quotes from different traditions and periods point to the same maxim.

Each quote has:
- its exact wording (never paraphrased; a paraphrase must say so) [Built],
- a translator or translation note where needed [Built],
- a precise source (work, chapter, verse) and a URL where the wording can be read [Built],
- an honest verification label [Built],
- links to its **voice** (who said it) and **source** (which work it is from) [Built],
- a short plain-English explanation of its own [Planned].

The headline view is **The 42**: the 42 highest-ranked maxims by **Moral Rank**, a score that rewards broad, independent agreement across thinkers, traditions and time periods more than a raw count of quotes.

The long-term feel is a mix of Wikipedia (sourced, neutral, readable), Obsidian (backlinks and a local graph on every page) and a published mind map you can explore. Today the site is the sourced, neutral, readable part; the graph is [Planned].

**Why agents do the work:** an earlier attempt to do this by hand in Obsidian took too much manual effort. In this version, agents find, source, verify and cluster quotes, and the project owner stays the editor, approving new maxims, merges and scoring changes through GitHub pull requests.

### Primary user journey (SEO entry)
1. A visitor searches for a quote, e.g. *"what you do not want done to yourself, do not do to others"*.
2. [Built] They land on the **maxim page** that holds it (the Golden Rule), with the seed expression on top, all related expressions below, each with its source, label, voice and work.
3. [Built] From there they move **across** to Voice and Source pages, or **back** to The 42.
4. [Planned] Dedicated per-quote pages, Tradition pages, a graph view, and "a maxim a week" signup.

---

## 2. Goals & success metrics [Planned targets]

| Goal | Metric | Target (≈3 months after launch) |
|---|---|---|
| Trustworthy | % of published quotes `verified` with a primary-source citation | ≥ 90% (rest clearly labelled) |
| Trustworthy | Misattributions published as genuine | 0 (misattributions are labelled `misattributed`) |
| Findable | Indexed pages in Google Search Console | ≥ 150 |
| Findable | Organic clicks per month | 1,000 (directional) |
| Engaging | % of visits that open a second page | ≥ 25% |
| Audience | Newsletter subscribers | 500 |
| Low-touch | Owner review time per week | ≤ 2 h; PRs reviewable in < 10 min each |
| Pipeline quality | % of agent-proposed quote→maxim links accepted unchanged | ≥ 70% |

**Non-goals for now:** user accounts, comments, in-site submissions (contributions come as GitHub issues/PRs), mobile app, multi-language UI.

---

## 3. Pages and features

### 3.1 Built
1. **The 42** (`/`): a short introduction, then a table of the 42 highest-ranked qualifying maxims. Each row shows rank, maxim, Moral Rank and small chips (quotes, voices, traditions, periods).
   - **Qualifying** means supported by at least two distinct traditions with a quote that scores above zero, and not on hold.
   - **Hold flag:** a maxim can carry `"hold": "<reason>"` in `data/maxims.json`. It is kept out of The 42, and its page shows "On hold for The 42" with the reason (e.g. when the second tradition's quote is too loose a match and a closer source is still being sought).
   - **Emerging:** every other maxim, ranked by score: those that just missed the top 42, those with only one tradition so far, and those on hold. Each Emerging row carries a reason chip ("ranked just below the top 42", "awaiting a second tradition" or "awaiting a stronger second source").
2. **Maxim page** (`/maxims/<slug>/`):
   - the maxim;
   - the **seed** expression at the top: the quote from the oldest time period, then the best-verified one; the concept's `"seed": <index>` overrides the choice;
   - a short warm summary in our own words, and the hold note if any;
   - **Related expressions**: a scrolling list of all other quotes, each with voice, work, tradition, period, relation, verification label and source link;
   - **Score**: Moral Rank and the evidence equation with this maxim's numbers filled in, plus a link to the Method page (no long explanation on the maxim page);
   - optional further-reading links.
3. **Voices** (`/voices/` and `/voices/<slug>/`): who said it. Kind (person, collective, scripture, traditional or legendary figure), dates, tradition, period, a 2–3 sentence factual summary, references, a caution note when `confidence` is `thin` or `uncertain`, and every quote by that voice.
4. **Sources** (`/sources/<slug>/` and `/sources/`): which work it is from. One source per book whatever the chapter or translation (each Bible book, each hadith or Pali collection, each Plato dialogue is one source). Same layout as voices, plus a link to the source's voice.
5. **Method** (`/method/`): the Moral Rank equation, a plain-words bullet for each term, the time periods with dates, the verification-label legend, and the translation policy.
6. **About** (`/about/`): what the project is, how to contribute, licence.
7. 404 page; light and dark colour schemes; serif reading typography.

### 3.2 Planned
- Per-quote pages (`/quotes/<slug>/`) with original text, translation, explanation (80–250 words), siblings.
- Tradition pages (`/traditions/<slug>/`) with influence links (`derives_from`).
- Filters on The 42 (tradition, period) and sort options (most references, most traditions).
- Static search (e.g. Pagefind).
- Graph view (`/graph/`): interactive graph of maxims, quotes, voices and traditions; local graphs on maxim pages.
- **Misattributed** page (`/misattributed/`) collecting the `misattributed` quotes with their true origins.
- References beyond quotes: video clips with start/end times, songs, stories.
- Newsletter signup, RSS feed, sitemap, structured data.

---

## 4. Data model

### 4.1 Built: JSON in `data/`
Git is the database and the audit trail. Generated output (`data/generated/`, all HTML) is never hand-edited.

**`data/maxims.json`**
- `traditions`: `{"<key>": {"name": "...", "derives_from": ["<key>", ...]}}`. `derives_from` records historical influence and is used to discount non-independent evidence (§5).
- `concepts` (maxims): `{"slug", "maxim", "summary", "links": [...], "seed"?: <int>, "hold"?: "<reason>"}`.
- `quotes`:
```json
{"concept": "golden-rule", "rel": "expresses|similar|partial|contrasts", "conf": 0.95,
 "ver": "verified|probable|disputed|unverified|misattributed",
 "text": "exact wording from the source", "thinker": "Confucius", "voice": "confucius",
 "tradition": "confucianism", "era": "axial",
 "work": "Analects 15.24, tr. James Legge", "source_id": "analects",
 "translation": "optional: translator/licence, or 'AI-assisted translation'",
 "source": "URL where the exact wording can be read, or \"\""}
```

**`data/voices.json`**: `{"<slug>": {"name", "kind": "person|collective|text|legendary", "dates", "tradition", "period", "summary", "confidence": "solid|thin|uncertain", "refs": [...]}}`

**`data/sources.json`**: `{"<slug>": {"title", "voice": "<voice slug> or null", "kind": "book|scripture|talk|article|other", "dates", "tradition", "period", "summary", "confidence", "refs": [...]}}`

Tests fail on unknown slugs, missing fields, empty summaries, or voice/source entries nothing uses. Full contributor rules are in CLAUDE.md.

### 4.2 Link relation types
| Link | Relation | Meaning | Weight in score | Status |
|---|---|---|---|---|
| Quote→Maxim | `expresses` | States the maxim directly | 1.0 | Built |
| Quote→Maxim | `similar` | A similar idea in its own terms (default for cross-tradition matches) | 0.7 | Built |
| Quote→Maxim | `partial` | Covers one aspect, or a related principle | 0.4 | Built |
| Quote→Maxim | `contrasts` | Disagrees with or complicates the maxim (shown, not scored) | 0 | Built |
| Tradition→Tradition | `derives_from` | Historical influence, used for independence | n/a | Built |
| Maxim↔Maxim | `refines` / `generalises` | One is a more specific form of the other | 1.0 | Planned |
| Maxim↔Maxim | `complements` | Often found together and mutually supporting | 0.7 | Planned |
| Maxim↔Maxim | `tension` | Pulls against it (e.g. justice vs mercy); shown, no rank | 0 | Planned |

### 4.3 Planned richer model
Later fields from the original plan: original-language text with ISO language code, structured translation licence (`public-domain | cc-by | cc-by-sa | fair-dealing-short | own`), sort year, link `rationale` and `status` (proposed/approved), concept aliases and `merged_from` with redirects, Wikidata IDs for voices and traditions, `data/review-log.jsonl` of editorial decisions, and `graph.json`.

---

## 5. Moral Rank: scoring

Moral Rank answers one question: **how widely, independently and reliably has humanity arrived at this idea?** The score measures convergence, not truth or moral worth. It ranks ideas, never traditions or thinkers. Constants live in `scoring.py` and change only with the project owner's approval.

### 5.1 Evidence score E(c) [Built]
For every quote q linked to maxim c:

```
w_q = ver(q) × rel(link) × conf(link)
ver:  verified 1.0 · probable 0.6 · disputed 0.2 · unverified 0 · misattributed 0
rel:  expresses 1.0 · similar 0.7 · partial 0.4 · contrasts 0
```

| Term | Definition | Why |
|---|---|---|
| **Q** = Σ w_q | Weighted quote count | Raw support, with diminishing returns via log |
| **K** = Σ over voices k of max w_q from k | Each thinker counts once, at their strongest quote | Ten quotes from Seneca are still one Seneca |
| **T** = Σ over traditions t of indep(t) × max w_q in t | Weighted count of independent traditions | Diversity of tradition matters most |
| **R** = number of time periods with at least one quote where w_q ≥ 0.3 | Period spread | Agreement across time |

`indep(t) = 0.5` if any ancestor of t (in `derives_from`) also supports c, otherwise 1.0. The discount does not compound; for example, Christianity next to Judaism counts at half weight.

```
E(c) = ln(1+Q) + √K + 3.0·T + 1.5·R
Moral Rank(c) = 100 × E(c) / max E          # top maxim = 100
```

The site shows only this equation (with the maxim's numbers) on each maxim page and links to the Method page for the plain-words explanation.

### 5.2 Time periods [Built]
Each quote is placed in one period by when it was written or first recorded. The data key is `era`; the site shows the period name with its dates.

| `era` key | Shown as |
|---|---|
| `axial` | Ancient (before 200 BCE) |
| `classical` | Classical (200 BCE – 600 CE) |
| `medieval` | Medieval (600 – 1500) |
| `early-modern` | Early modern (1500 – 1800) |
| `modern` | Modern (1800 – 1950) |
| `contemporary` | Contemporary (1950 – today) |

### 5.3 Graph propagation [Planned]
Once Maxim↔Maxim links exist, build an undirected weighted graph (edge weight = rel × conf, `tension` excluded) and run personalised PageRank with the teleport vector set to normalised evidence:

```
e_c   = E(c) / Σ E
r     = (1 − β)·e + β·Wᵀ r        # W row-normalised edge weights
β     = 0.2                         # 80% evidence, 20% from linked maxims
dangling nodes (no links) redistribute via e
MoralRank(c) = 100 × r_c / max(r)
```

`scoring.moral_rank` already implements this; with no links it reduces to 100 × E / max E, which is what the site shows today. Ties are broken by T, then K.

### 5.4 Worked example (unit-test fixture, `tests/test_scoring.py`) [Built]
**Maxim A: Golden Rule**

| Quote | Thinker | Tradition | Period | ver | rel | conf | w_q |
|---|---|---|---|---|---|---|---|
| Analects 15.24 | Confucius | Confucianism | Ancient | 1.0 | expresses 1.0 | 0.95 | 0.95 |
| Talmud, Shabbat 31a | Hillel | Judaism | Classical | 1.0 | expresses 1.0 | 0.95 | 0.95 |
| Matthew 7:12 | Jesus | Christianity (derives_from Judaism) | Classical | 1.0 | expresses 1.0 | 0.95 | 0.95 |
| Luke 6:31 | Jesus | Christianity | Classical | 1.0 | expresses 1.0 | 0.90 | 0.90 |
| Mahabharata, Anushasana Parva 113.8 | Mahabharata (text) | Hinduism | Ancient | 1.0 | similar 0.7 | 0.90 | 0.63 |
| Isocrates, *Nicocles* 61 | Isocrates | Classical Greek | Ancient | 1.0 | similar 0.7 | 0.90 | 0.63 |
| Kant, *Groundwork* | Kant | Enlightenment (derives_from Greek, Christianity) | Early modern | 1.0 | partial 0.4 | 0.80 | 0.32 |

- Q = **5.33**, ln(6.33) = **1.845**
- K = 0.95 + 0.95 + 0.95 (Luke not counted again) + 0.63 + 0.63 + 0.32 = **4.43**, √K = **2.105**
- T = 0.95 + 0.95 + 0.95×0.5 + 0.63 + 0.63 + 0.32×0.5 = **3.795**, 3T = **11.385**
- R = {Ancient, Classical, Early modern} = **3**, 1.5R = **4.5**
- **E(A) = 19.835**

*(Kant explicitly rejected the Golden Rule as a foundation (Groundwork, footnote at 4:430), hence `partial`.)*

**Maxim B: "Time is the only thing truly ours"**, 7 verified Seneca quotes (all `expresses`, conf 0.9): ln(7.3) = 1.988 · √0.9 = 0.949 · 3T = 2.7 · 1.5R = 1.5 → **E(B) = 7.137**, about 2.8× lower than A because it rests on one voice.

**Propagation example [Planned; not yet a test]:** the A and B evidence values above are unit-tested; this part is illustrative. With C "Do no harm" at E = 12.0 and a `complements` link C↔A (conf 0.9), β = 0.2 gives Moral Rank A 100.0, C 71.8, B 30.8.

### 5.5 Guardrails
- [Built] A maxim needs at least 2 traditions with a scoring quote, and no hold flag, to enter The 42; others appear under Emerging.
- [Built] Near-duplicate sayings go under the existing maxim as `similar`/`partial` quotes, not new maxims.
- [Planned] Merge PRs show the before/after diff of The 42.

---

## 6. Respectful framing rule (religious & wisdom texts)

1. **Use "similar idea", never "the same".** Write *"Expresses a similar idea to…"*, *"Echoes…"*, *"Resonates with…"*. Never "X is the same as Y" or "all religions teach…".
2. **Use the tradition's own context first**, then mention parallels; add a "How it differs" note where the difference matters.
3. **Use neutral, descriptive voice.** "In the Gospel of Matthew, Jesus says…", "The Qur'an states…". Don't mock or debunk. Use BCE/CE consistently.
4. **Cite scripture exactly**: book, chapter and verse plus the translation; prefer public-domain translations widely accepted by the tradition.
5. **Never rank traditions or thinkers.** Moral Rank scores ideas only.
6. **Default to `similar`** for cross-tradition links; `expresses` needs a reason and the project owner's confirmation.
7. **Disputed authorship** is stated neutrally ("traditionally attributed to X") with the scholarly view (see CLAUDE.md, Voices and sources).

---

## 7. Content policy [Built]

- **English first.** Non-English sources use public-domain or credited translations. Where we translate ourselves, the quote's `translation` says "AI-assisted translation" and the site labels it. Other languages for the site itself are [Planned].
- **Modern and living authors**: short quotations only (one or two sentences), always attributed.
- **Verification labels** (`ver`): `verified` = exact wording seen at a primary text, reputable/public-domain translation, or the author's own book/site/talk; `probable` = reliable secondary source only (counts 0.6); `disputed` = credible sources disagree (0.2); `unverified` = no traceable origin (shown, scores 0); `misattributed` = attribution known to be wrong (shown with the true origin where known, scores 0). Never invent or "fix" wording or citations.
- **Licence:** our own writing and data are CC BY-SA 4.0. Quotes remain the property of their authors and translators.

---

## 8. Agent pipeline

### 8.1 Built (manual, agent-assisted)
Agents (Claude Code, briefed by oo-42maxims) follow the content workflow in CLAUDE.md and OPS.md: pick a maxim, find exact wording at a primary or reputable source, fetch the URL to confirm, set `ver`/`rel`/`conf`, add voice and source entries, run `python3 build.py && python3 -m unittest discover tests`, and open a small PR. The project owner approves new maxims, merges and scoring changes.

### 8.2 Planned (automated)
```
[1 Discover] → [2 Ingest & licence check] → [3 Verify attribution] → [4 Explain]
     → [5 Embed & cluster] → [6 LLM review] → [7 Lint & score] → [8 Open PR] → project owner
```
1. **Discover** from the project seed notes and curated lists per tradition. Wikiquote and Quote Investigator are leads only.
2. **Ingest & licence check** from public-domain sources (Wikisource, Project Gutenberg, Sacred-texts with PD check, Perseus, CText, SuttaCentral). Record the licence; modern copyrighted translations only as short credited extracts, flagged for review. KJV caveat: under Crown letters patent in the UK.
3. **Verify attribution** by fuzzy-matching against the primary text and set `ver`.
4. **Explain**: draft per-quote explanations under the framing rule; no invented locators.
5. **Embed & cluster**: propose quote→maxim links by similarity; leftovers seed new clusters.
6. **LLM review**: a sceptical second pass confirms links, sets relation/confidence, drafts new maxims, proposes merges and splits.
7. **Lint & score**: schema, banned phrases, licence, link integrity, duplicates; rebuild scores.
8. **Open PR**: 10–20 quotes per PR, with a summary table, The 42 diff and flagged items. Agents never merge content PRs that need the project owner.

---

## 9. Stack

| Layer | Built | Planned |
|---|---|---|
| Site | Plain Python static generator (`build.py`, no dependencies) writing committed HTML and `style.css` | Possibly a framework later if needed |
| Data | JSON in `data/` (maxims, voices, sources) | Richer fields (§4.3) |
| Scoring | `scoring.py` with unit tests (`tests/`) | Concept links + propagation |
| CI | GitHub Actions: runs tests and checks committed HTML matches `build.py` output | Lint stages from §8.2 |
| Hosting | GitHub Pages user site `42maxims.github.io`, branch `master`, root folder, `.nojekyll`; push to `master` deploys | Custom domain 42maxims.com (chosen, not bought; needs approval) |
| Search / graph | — | Pagefind; Cytoscape.js or Sigma.js |
| Analytics / newsletter | — | Cookieless analytics; Buttondown or Beehiiv |

**Commits:** all commits use the anonymous project identity `Max Ims <37961849+42maxims@users.noreply.github.com>`. No personal names in commits, files or pages.

Repo layout:
```
build.py  scoring.py  style.css  index.html  404.html
data/{maxims,voices,sources}.json  data/generated/scores.json
maxims/<slug>/  voices/<slug>/  sources/<slug>/  method/  about/   (generated)
tests/  .github/workflows/ci.yml
SPEC.md  ROADMAP.md  DECISIONS.md  OPS.md  CLAUDE.md  CONTRIBUTING.md  README.md  LICENSE
```

---

## 10. SEO approach [mostly Planned]

- [Built] Static HTML, fast pages, descriptive titles ("<maxim> — 42 Maxims"), exact citations near the top, dense internal linking between maxims, voices and sources.
- [Planned] Publish only pages that add value; thin pages `noindex` until they fill out; steady weekly batches rather than mass publishing; Method page discloses AI-assisted work with editorial review.
- [Planned] Structured data (`Quotation`, `Person` with `sameAs`, `DefinedTerm`, `BreadcrumbList`), sitemap, one canonical page per quote with variant wordings on the same page, redirects on merges.
- [Planned] Linkable assets: the Misattributed page, The 42, "the Golden Rule across many traditions" maxim pages.

---

## 11. Monetisation [Planned, in priority order]

1. **Newsletter "A maxim a week"**: one maxim with 3–4 quotes from different traditions, generated from the repo, each issue approved by the project owner.
2. **Book and prints**: a "42 Maxims" book (The 42, each with cross-tradition quotes), typographic prints via print-on-demand; check translation licences for print.
3. **App (later)**: maxim of the day, reflection prompts, once the newsletter shows traction.
4. **Ads last, if ever**: none on religious-text pages; affiliate links to good editions as a softer option.

---

## 12. Approvals (the project owner decides; agents never do these on their own)

| Item | Who approves |
|---|---|
| New maxims (concept definitions) | Project owner |
| Merges, splits, renames, deletions of maxims | Project owner |
| `expresses` links across traditions; publishing a `misattributed` entry | Project owner |
| Tradition `derives_from` table and scoring constants | Project owner |
| Domain purchase and DNS | Project owner |
| Any spend (paid services, LLM/embedding budget, newsletter tier, print) | Project owner |
| Quotes added to existing maxims | Maintainer may merge once CI passes |
| Code PRs (site, pipeline) | oo-42maxims reviews; project owner for anything touching data policy |

---

## 13. Milestones

| # | Milestone | Status |
|---|---|---|
| M0 | Skeleton: static site on GitHub Pages, seed data, scoring module + worked-example test, CI | Done (2026-10-14) |
| M0.1 | "The 42" naming, seed-quote maxim page with Related expressions, plain-words Method page, periods with dates, hold flag | Done (2026-10-14) |
| M0.2 | Voices and Sources: data files, pages, links from maxim pages, nav, tests | Done (2026-10-14) |
| M1 | Tradition pages, filters and sort options on The 42, search, structured data; more maxims reach 2 traditions | Planned |
| M2 | Sourcing: verification checklist, Misattributed page, references beyond quotes | Planned |
| M3 | Clustering: maxim-to-maxim links, graph propagation, merge proposals with The 42 diffs | Planned |
| M4 | Pipeline automation (§8.2) and per-quote explanations | Planned |
| M5 | Launch extras: domain, newsletter, analytics, sitemap, Search Console | Planned |

---

## 14. Questions

**Settled** (see DECISIONS.md): name "42 Maxims"; domain 42maxims.com chosen but not bought; anonymous author ("Max Ims"); GitHub Pages with simple tools; English first with labelled AI-assisted translations; modern and living thinkers with short attributed quotes; scoring weights 3.0·T, 1.5·R, `derives_from` at 0.5; warm, reflective voice; own content CC BY-SA 4.0.

**Open:**
1. Domain purchase timing and budget.
2. Seed set: export of the earlier Obsidian notes; must-include traditions or thinkers.
3. Auto-merge: may fully verified, public-domain quote batches on existing maxims merge automatically?
4. Tensions: a "debates" view for maxims in tension (e.g. justice vs mercy), now or later?
5. LLM/embedding provider and monthly budget cap for the automated pipeline.
6. Newsletter platform and sender name/address (must stay anonymous).
7. Misattributed page: when to launch it.
