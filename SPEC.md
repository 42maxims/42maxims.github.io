# 42 Maxims: Product & Build Spec

**Owner:** the project owner · **Build lead:** Devsy (dev-manager bot) briefing Claude Code
**Repo (placeholder):** `42maxims/42maxims.github.io` · **Status:** Draft v0.1 (2026-10-14)
**Working name:** 42 Maxims. "42" is the brand, not a limit. The catalogue has no fixed size.

---

## 1. What we're building

42 Maxims is a published knowledge graph of how to live. Each **Quote** (from a philosopher, thinker or religious/wisdom text) gets:

- its exact text,
- a translation where needed,
- a precise source (work, chapter, verse),
- a verification status,
- a short plain-English explanation.

Each quote links to one or more **Concepts**. A Concept is a short core maxim such as "Treat others as you would wish to be treated". Many quotes from different traditions point to the same Concept.

The headline view is the **Scoreboard**, which ranks Concepts by **Moral Rank**. Moral Rank is a PageRank-style score. It rewards broad, independent agreement across thinkers, traditions and eras more than a raw count of quotes.

The site should feel like a mix of Wikipedia (sourced, neutral, readable), Obsidian (backlinks and a local graph on every page) and a published Roam-style mind map (an interactive graph you can explore).

**Why agents do the work:** the owner tried this by hand in Obsidian and it took too much manual effort. In this version, agents ingest, source, verify and cluster. the owner stays the editor. He approves concept definitions and merges through GitHub PRs.

### Primary user journey (SEO entry)
1. A visitor searches for a specific quote, e.g. *"what you do not want done to yourself, do not do to others"*.
2. They land on its **Quote page**, which shows the exact text, translation, source citation, verification badge and explanation.
3. The page leads them **up** to the parent **Concept** (the Golden Rule), which has its Moral Rank, definition and **sibling quotes** from other traditions.
4. From there they can move **across** to Thinker and Tradition pages or the graph, or subscribe to "a maxim a week".

---

## 2. Goals & success metrics

| Goal | Metric | MVP target (≈3 months after launch) |
|---|---|---|
| Trustworthy | % of published quotes with status `verified` and a primary-source citation | ≥ 90% (rest clearly badged) |
| Trustworthy | Misattributions published as genuine | 0 (misattributions get a "misattributed" page) |
| Findable | Indexed quote pages in Google Search Console | ≥ 150 of ~200 |
| Findable | Organic clicks per month | 1,000 (directional) |
| Climb-up journey works | % of quote-page sessions that go on to a Concept page | ≥ 25% |
| Engaging | Graph view interactions per session (among those who open it) | ≥ 3 node clicks |
| Audience | Newsletter subscribers | 500 |
| Low-touch for the owner | the owner's review time per week | ≤ 2 h; PRs reviewable in < 10 min each |
| Pipeline quality | % of agent-proposed concept links the owner accepts unchanged | ≥ 70% (tracks clustering quality) |

**Non-goals for MVP:** user accounts, comments, user-submitted quotes, mobile app, multi-language UI, and real-time editing.

---

## 3. MVP scope

**Content**
- About **200 well-sourced quotes**. Aim for breadth: at least 12 traditions and at least 5 eras. No single tradition should be more than 20% of the set.
- **First-draft Concept clusters**, roughly 30–60 Concepts. Each needs at least 2 quotes to be published. Agents draft every Concept definition and the owner approves it.
- About 60–100 **Thinker** pages and 12–20 **Tradition** pages.

**Pages and features**
1. **Scoreboard** (`/`): Concepts ranked by Moral Rank. Each row shows the rank and score plus small "breadth" chips (number of quotes, thinkers, traditions, eras). The list can be filtered by tradition and era.
2. **Concept page** (`/concepts/<slug>/`): the maxim, an approved definition (100–300 words), how the score breaks down, supporting quotes grouped by tradition, related Concepts (refines, complements, tensions), a local graph, and a "similar idea, not the same" note where it applies.
3. **Quote page** (`/quotes/<slug>/`): original text (when available), translation and translator, full citation with a link to the primary source, a verification badge, an explanation (context and meaning, 80–250 words), parent Concept(s) with the relation type, sibling quotes, the thinker and the tradition.
4. **Thinker page** (`/thinkers/<slug>/`): short bio, dates, tradition(s), their quotes, the Concepts they support, and their "reach" (how many Concepts they appear in).
5. **Tradition page** (`/traditions/<slug>/`): overview, era span, influence links (derives_from), thinkers, and the Concepts it supports.
6. **Graph view** (`/graph/`): an interactive, force-directed graph of Concepts, Quotes, Thinkers and Traditions. You can filter by node type, tradition and era. Clicking a node opens its page. Concept node size scales with Moral Rank.
7. **Search**: full-text static search over quotes (original and translation), concepts and thinkers.
8. **Misattributed** (`/misattributed/`): popular quotes that are wrongly attributed, with what we know about where each really came from. These pages are strong for SEO and build trust.
9. **About / Method** page: how sourcing, verification and Moral Rank work, plus the framing rule for religious texts.
10. Newsletter signup (embedded form), RSS feed, sitemap.

---

## 4. Data model

All content is stored as **Markdown files with YAML frontmatter** in the repo, and Git is the database. Schemas are enforced with Astro content collections (zod), and CI fails if a file is invalid. Slugs are stable IDs: never reuse one, and when content is renamed, add the old slug to `redirect_from`.

### 4.1 Quote — `content/quotes/<slug>.md`
```yaml
id: confucius-analects-15-24            # = slug, kebab-case, stable
text: "What you do not want done to yourself, do not do to others."
original:                                # optional
  text: "己所不欲，勿施於人。"
  language: lzh                          # ISO 639-3 (Classical Chinese)
translation:
  translator: James Legge
  year: 1861
  licence: public-domain                 # public-domain | cc-by | cc-by-sa | fair-dealing-short | own
  source_url: https://en.wikisource.org/wiki/...
thinker: confucius                       # Thinker id ("anonymous-<text>" allowed for texts)
traditions: [confucianism]
era: axial                               # see era buckets §5.2
date: { approx: "c. 479 BCE", sort_year: -479 }   # composition or attribution date
source:
  work: Analects
  section: "Book XV (Wei Ling Gong)"
  locator: "15.24"                       # chapter/verse/line/Stephanus/Bekker etc.
  edition: "Legge, The Chinese Classics vol. 1 (1861)"
  primary_url: https://...               # link to the full-text primary source
  secondary_refs: []                     # scholarly refs, Quote Investigator, etc. (links only)
verification:
  status: verified                       # verified | probable | disputed | misattributed | unverified
  method: primary-text-match             # primary-text-match | scholarly-ref | secondary-only
  checked_by: [agent:verifier, human:joe]
  checked_at: 2026-10-14
  notes: "Text matched in Wikisource Legge edition; also 12.2 has a near-identical line."
concepts:                                # Quote → Concept links
  - concept: golden-rule
    relation: expresses                  # see relation types §4.5
    confidence: 0.95                     # 0..1, set by agent, can be overridden by the owner
    rationale: "Negative (prohibitive) form of the reciprocity principle."
    status: approved                     # proposed | approved | rejected
tags: [reciprocity, ethics]
explanation_status: approved             # draft | approved
redirect_from: []
---
Markdown body = explanation (context, meaning, how it is read within its own tradition).
```

### 4.2 Thinker — `content/thinkers/<slug>.md`
`id, name, alt_names[], born {approx, sort_year}, died {…}, traditions[], era, kind (person | text | collective | legendary), wikidata_qid, wikipedia_url, image (PD/CC only, with credit)`. The body holds a short bio. For an anonymous or composite text, use `kind: text`, for example `mahabharata` (traditionally attributed to Vyasa).

### 4.3 Tradition — `content/traditions/<slug>.md`
`id, name, family (e.g. "Abrahamic", "Indic", "Chinese", "Hellenistic", "Modern Western"), kind (religious | philosophical | wisdom-literature | literary), era_span, derives_from[] (tradition ids), wikidata_qid`. Moral Rank uses `derives_from` to discount evidence that isn't independent (§5). the owner signs off on this table.

### 4.4 Concept — `content/concepts/<slug>.md`
```yaml
id: golden-rule
maxim: "Treat others as you would wish to be treated."   # concise core rule, ≤ 12 words ideally
aliases: ["ethic of reciprocity"]
definition_status: approved             # draft | approved (the owner only)
related:                                # Concept ↔ Concept links
  - concept: do-no-harm
    relation: complements
    confidence: 0.9
    status: approved
merged_from: []                         # slugs merged into this one (→ redirects)
---
Definition / essay (agent-drafted, the owner-approved).
```

### 4.5 Link relation types
| Link | Relation | Meaning | Weight in score |
|---|---|---|---|
| Quote→Concept | `expresses` | States the concept directly | 1.0 |
| Quote→Concept | `similar` | A similar idea in its own terms (default for cross-tradition matches) | 0.7 |
| Quote→Concept | `partial` | Covers one aspect, or a related principle | 0.4 |
| Quote→Concept | `contrasts` | Disagrees with or complicates the concept (shown on the page, not scored) | 0 |
| Concept↔Concept | `refines` / `generalises` | One is a more specific form of the other | 1.0 |
| Concept↔Concept | `complements` | Often found together and mutually supporting | 0.7 |
| Concept↔Concept | `tension` | Pulls against it (e.g. justice vs mercy). Shown, but carries no rank | 0 |
| Tradition→Tradition | `derives_from` | Historical influence, used for independence | n/a |

Every link has `confidence` (0–1), `rationale`, `status` and `proposed_by`. Only `approved` links count toward the published score. `proposed` links appear in PR previews only.

### 4.6 Generated (not hand-edited) — `data/generated/`
`scores.json` (Moral Rank and its breakdown per Concept), `graph.json` (nodes and edges for the graph view), `embeddings.parquet` (gitignored or kept in R2, used for clustering). All are rebuilt in CI.

---

## 5. Moral Rank: scoring algorithm

Moral Rank answers one question: **how widely, independently and reliably has humanity arrived at this idea?** It is computed in two stages.

### 5.1 Stage 1: Evidence score E(c)
For every approved link from quote q to concept c:

```
w_q = ver(q) × rel(link) × conf(link)
ver:  verified 1.0 · probable 0.6 · disputed 0.2 · unverified 0 · misattributed 0
rel:  expresses 1.0 · similar 0.7 · partial 0.4 · contrasts 0
```

Then:

| Term | Definition | Why |
|---|---|---|
| **Q** = Σ w_q | Weighted quote count | Raw support, with diminishing returns via log |
| **K** = Σ over thinkers k of max w_q from k | Each thinker counts once, at their strongest quote | Ten quotes from Seneca are still one Seneca |
| **T** = Σ over traditions t of indep(t) × max w_q in t | Weighted count of independent traditions | Diversity of tradition matters most |
| **R** = number of eras with at least one quote where w_q ≥ 0.3 | Era spread | Agreement across time |

`indep(t) = 0.5` if any ancestor of t (in `derives_from`) also supports c. Otherwise it is 1.0. The discount does not compound. For example, Christianity next to Judaism counts at half weight.

```
E(c) = 1.0·ln(1+Q) + 1.0·√K + 3.0·T + 1.5·R
```

Quote count sits under a log and thinkers under a square root, so piling up quotes and names gives less and less. Traditions and eras grow linearly and carry large weights. In practice, **diversity and independence outweigh raw count**.

Era buckets (`era`): `axial` (< 200 BCE), `classical` (200 BCE–600 CE), `medieval` (600–1500), `early-modern` (1500–1800), `modern` (1800–1950), `contemporary` (1950–).

### 5.2 Stage 2: Graph propagation (the "PageRank" part)
We build an undirected, weighted graph of Concepts from approved Concept↔Concept links. Edge weight = rel × conf, and `tension` is excluded. We then run personalised PageRank, with the teleport vector set to normalised evidence:

```
e_c   = E(c) / Σ E
r     = (1 − β)·e + β·Wᵀ r        # W row-normalised edge weights
β     = 0.2                         # 80% evidence, 20% from linked concepts
dangling nodes (no links) redistribute via e
MoralRank(c) = 100 × r_c / max(r)  # displayed 0–100, top concept = 100
```

Because β is low, cross-links can lift a well-connected concept but cannot replace evidence. Ties are broken by T, then K. The score breakdown is published on every Concept page for transparency. All constants live in `config/scoring.yaml` and are versioned. Any change to them needs the owner's approval, and the Method page lists the changes.

### 5.3 Worked example
**Concept A: Golden Rule** ("Treat others as you would wish to be treated")

| Quote | Thinker | Tradition | Era | ver | rel | conf | w_q |
|---|---|---|---|---|---|---|---|
| Analects 15.24 | Confucius | Confucianism | axial | 1.0 | expresses 1.0 | 0.95 | 0.95 |
| Talmud, Shabbat 31a | Hillel | Judaism | classical | 1.0 | expresses 1.0 | 0.95 | 0.95 |
| Matthew 7:12 | Jesus | Christianity (derives_from Judaism) | classical | 1.0 | expresses 1.0 | 0.95 | 0.95 |
| Luke 6:31 | Jesus | Christianity | classical | 1.0 | expresses 1.0 | 0.90 | 0.90 |
| Mahabharata, Anushasana Parva 113.8 | Mahabharata (text) | Hinduism | axial | 1.0 | similar 0.7 | 0.90 | 0.63 |
| Isocrates, *Nicocles* 61 | Isocrates | Classical Greek | axial | 1.0 | similar 0.7 | 0.90 | 0.63 |
| Kant, *Groundwork* (Categorical Imperative) | Kant | Enlightenment (derives_from Greek, Christianity) | early-modern | 1.0 | partial 0.4 | 0.80 | 0.32 |

- Q = 0.95+0.95+0.95+0.90+0.63+0.63+0.32 = **5.33**, so ln(6.33) = **1.845**
- K = Confucius 0.95 + Hillel 0.95 + Jesus 0.95 (Luke is not counted again) + Mahabharata 0.63 + Isocrates 0.63 + Kant 0.32 = **4.43**, so √K = **2.105**
- T = Confucianism 0.95 + Judaism 0.95 + Christianity 0.95×0.5 + Hinduism 0.63 + Classical Greek 0.63 + Enlightenment 0.32×0.5 = **3.795**, so 3T = **11.385**
- R = {axial, classical, early-modern} = **3**, so 1.5R = **4.5**
- **E(A) = 1.845 + 2.105 + 11.385 + 4.5 = 19.835**

*(Kant explicitly rejected the Golden Rule as a foundation (Groundwork, footnote at 4:430). That is why the link is `partial` and the page notes the distinction.)*

**Concept B: "Time is the only thing truly ours"**, supported by 7 verified Seneca quotes (all `expresses`, conf 0.9).
- Q = 6.3, so ln(7.3) = 1.988 · K = 0.9, so √K = 0.949 · T = Stoicism 0.9, so 3T = 2.7 · R = 1, so 1.5
- **E(B) = 7.137**. B has the same number of quotes as A and a slightly higher Q, but scores **about 2.8× lower** because it rests on one voice.

**Concept C: "Do no harm"**: assume E(C) = 12.0, with an approved `complements` link C↔A (conf 0.9). B has no links.

Propagation (β = 0.2):

| Concept | E | e (normalised) | r after PageRank | **Moral Rank** |
|---|---|---|---|---|
| A Golden Rule | 19.835 | 0.509 | 0.494 | **100.0** |
| C Do no harm | 12.0 | 0.308 | 0.354 | **71.8** |
| B Time is ours | 7.137 | 0.183 | 0.152 | **30.8** |

C gains from its link to the highly evidenced A, and B, which has no links, slips slightly. Claude Code should add this exact example as a unit test fixture (`tests/scoring/worked_example.test.ts`), with values matched to 3 decimal places.

### 5.4 Guardrails
- A Concept needs **at least 2 traditions** to appear on the main Scoreboard. Single-tradition Concepts go under an "Emerging" tab.
- Splitting or merging Concepts changes ranks, so each merge PR shows the before/after scoreboard diff.
- The score measures convergence, not truth or moral worth. The Method page says this plainly.

---

## 6. Respectful framing rule (religious & wisdom texts)

1. **Use "similar idea", never "the same".** When we link across traditions, the wording is: *"Expresses a similar idea to…"*, *"Echoes…"*, *"Resonates with…"*. We never write "X is the same as Y" or "all religions teach…".
2. **Use the tradition's own context first.** Every explanation begins with what the text means within its own tradition, then mentions parallels. Wherever the difference matters, we include a "How it differs" note (e.g. the Golden Rule in a covenantal vs a Confucian relational setting).
3. **Use neutral, descriptive voice.** Write "In the Gospel of Matthew, Jesus says…" or "The Qur'an states…". Don't write "God commands us…" and don't mock or debunk. Use dating conventions (BCE/CE) consistently.
4. **Cite scripture exactly.** Give book, chapter and verse plus the translation. Prefer translations widely accepted by the tradition and in the public domain.
5. **Never rank traditions.** Moral Rank scores Concepts, never traditions or thinkers. No "most moral religion" leaderboards.
6. **Default to `similar`.** Cross-tradition quote→concept links start as `similar`. An agent may only propose `expresses` with a rationale, and the owner confirms it.
7. The LLM style prompt includes this rule, and the reviewer agent checks for banned phrases ("the same as", "all religions", "proves") before opening a PR.

---

## 7. Agent pipeline

Devsy runs the pipeline. Each stage is a script in `pipeline/` (Python 3.12 with `uv`, or TypeScript; Claude Code's choice, but pick one) and can run locally or from GitHub Actions on demand. **Every content change reaches `main` only through a PR.**

```
[1 Discover] → [2 Ingest & licence check] → [3 Verify attribution] → [4 Explain]
     → [5 Embed & cluster] → [6 LLM concept review] → [7 Lint & score] → [8 Open PR] → the owner
```

1. **Discover.** Start from seed lists (the owner's old Obsidian vault if he exports it, plus curated lists per tradition) and produce candidate quotes with their claimed attribution. Wikiquote and Quote Investigator are used **for leads only**: we don't copy their text or commentary.
2. **Ingest & licence check.** Fetch the primary text from public-domain sources:
   - **Wikisource**: source texts are generally PD. Check each translation's PD status (translator death date and publication date). The wiki's own pages are CC BY-SA.
   - **Project Gutenberg**: works are PD in the US. Follow the PG licence: strip the PG header/trademark if we redistribute, and record the ebook number.
   - **Sacred-texts.com**: many old PD translations, but the site's compilation, scans and notes may not be. Confirm that the underlying translation is PD and cite the original edition.
   - Others to consider: Perseus (CC BY-SA, so attribute), CText.org (check its terms), SuttaCentral (many CC0 translations).
   - Write `translation.licence` on every quote. **Modern copyrighted translations** are only allowed as `fair-dealing-short` (one or two sentences, credited) and must be flagged for the owner. Agents translate themselves only with `licence: own` and `translator: "42 Maxims (AI-assisted, reviewed)"`, and are never a substitute where a good PD translation exists.
   - **KJV caveat:** the KJV is PD in most places, but in the UK it is under Crown letters patent. Quoting it is fine in practice, but note it.
   - Respect `robots.txt`, rate-limit to 1 request/sec or less, and cache raw pages in `data/raw/` (gitignored, or kept in R2).
3. **Verify attribution.** Match the quote against the primary text using fuzzy matching (normalised, translation-aware). Set `verification.status` as follows:
   - `verified`: found at the stated locator in a primary or scholarly edition.
   - `probable`: found in a reliable secondary source but not yet in the primary.
   - `disputed`: scholars disagree.
   - `misattributed`: there is evidence it is falsely attributed (e.g. "Insanity is doing the same thing over and over…", which is not Einstein, and many "Buddha" quotes). These become entries on the Misattributed page.
   - `unverified`: no evidence found. Not published.
   Anything below `verified` is flagged in the PR body.
4. **Explain.** The LLM drafts the 80–250 word explanation under the framing rule, grounded in the source context it retrieved. It must cite, may not invent locators, and each explanation is marked `draft`.
5. **Embed & cluster.** Embed the normalised meaning of each quote ("what rule for life does this express?" paraphrase plus text). Compare to existing Concept centroids by cosine similarity. If similarity is 0.82 or higher, propose a link to that concept. Between 0.70 and 0.82, send it to LLM review. Below that, the quote becomes a seed for a new cluster (HDBSCAN over the leftovers). Thresholds go in `config/pipeline.yaml` and are tuned on the first 200 quotes.
6. **LLM concept review.** A second LLM pass acts as a sceptical editor. It confirms or rejects each proposed link, assigns a `relation` and `confidence`, writes the `rationale`, and drafts the maxim and definition for any new Concept. It also proposes **merges** (two Concepts that are really one) and **splits**, and suggests Concept↔Concept links.
7. **Lint & score.** Schema validation, a banned-phrase check, licence check, link-integrity check, and duplicate detection (the same quote under two slugs). Then recompute `scores.json`.
8. **Open PR.** One PR per batch of about 10–20 quotes, or per proposed merge/new Concept, so each stays reviewable. The PR body includes:
   - a summary table of quotes, statuses, licences and proposed links with confidence,
   - the scoreboard diff (before/after ranks),
   - flagged items (non-verified, non-PD, low confidence, new or merged Concepts needing the owner),
   - a Cloudflare Pages preview URL.
   Labels: `needs-owner:concept`, `needs-owner:merge`, `content:quotes`, `risk:licence`.

**the owner's review loop:** the owner approves or edits in the GitHub UI and merges. Agents never merge content PRs. Concept definitions and merges require the owner's approval. Routine quote additions where every quote is `verified`, PD and linked to an already-approved Concept may later be auto-approved by Devsy, but **only if the owner opts in** (open question).

**Feedback:** the owner's edits and rejections are logged to `data/review-log.jsonl` and used as few-shot examples to improve stage 6.

---

## 8. Stack (simplest that works)

| Layer | Choice | Notes |
|---|---|---|
| Site | **Astro** (static output) + content collections (zod schemas) | One `.md` file per entity; pages generated at build |
| Graph | **Cytoscape.js** for local graphs and the MVP `/graph/` view | Switch the global view to **Sigma.js + graphology** if nodes exceed ~3k |
| Search | **Pagefind** | Static, zero-backend, indexes at build |
| Styling | Plain CSS or Tailwind; serif reading typography | Wikipedia-calm, not flashy |
| Data | Markdown/YAML in GitHub `42maxims/42maxims.github.io` | Git is the database and the audit trail |
| Pipeline | Scripts in `pipeline/`, run by Devsy and GitHub Actions (`workflow_dispatch`) | LLM and embedding provider via env vars, never committed |
| CI | GitHub Actions: lint → schema → score → build → tests | Fails on invalid data |
| Hosting | **Cloudflare Pages** (preview per PR, production on `main`) | Optional R2 for raw caches and embeddings |
| Analytics | Cloudflare Web Analytics (cookieless) | No cookie banner needed |
| Newsletter | Buttondown or Beehiiv embed | Paid tier only with the owner's approval |

Repo layout:
```
42-maxims/
  SPEC.md  README.md
  content/{quotes,concepts,thinkers,traditions}/*.md
  config/{scoring.yaml,pipeline.yaml,style-guide.md}
  data/generated/   data/review-log.jsonl
  pipeline/{discover,ingest,verify,explain,cluster,review,lint,score,pr}.*
  src/{pages,components,layouts,lib/scoring.ts}
  tests/
  .github/workflows/{ci.yml,pipeline.yml}
```

---

## 9. SEO approach (without thin, scaled content)

Google's scaled-content-abuse policy targets mass-produced pages with little value. Our rules:

- **A page is published only if it adds value:** a verified (or clearly badged) quote with an exact citation, a primary-source link, an explanation, context, and links to its Concept and siblings. Pages with `unverified` status or a `draft` explanation are not built. Thin pages (e.g. a thinker with only one quote) get `noindex` until they fill out.
- **A human stays in the loop.** Explanations and definitions are reviewed and approved through PRs, and the Method page discloses that the work is AI-assisted with editorial review.
- **Publish at a steady pace.** Batches of about 10–20 per week, not thousands at once. Quality metrics come before volume.
- **On-page:**
  - Title = the quote (truncated) + thinker + "meaning & source".
  - H1 = the quote.
  - Show the exact citation near the top: that is what searchers want ("who said…", "what does … mean", "source of …").
- **Structured data:** `Quotation` (with `creator` and `isPartOf` for the work), `Person` with `sameAs` pointing to Wikidata/Wikipedia, `DefinedTerm` for Concepts, `BreadcrumbList` (Tradition › Thinker › Quote and Concept › Quote).
- **Canonicals:** one canonical page per quote. Variant wordings and translations go on the same page as "Also rendered as…", not as separate pages. Merges get 301 redirects via `_redirects`.
- **Internal linking** is the product itself: every quote links up to its Concept, and every Concept links to its siblings, thinkers and traditions.
- **Linkable assets:** the Misattributed page, the Scoreboard, and "the Golden Rule across 12 traditions" style Concept pages. They suit outreach to educators and philosophy communities.
- **Performance:** static HTML, the graph JS loads only on graph and concept pages, and the Lighthouse SEO score is ≥ 95.

---

## 10. Monetisation (in priority order)

1. **Newsletter: "A maxim a week".** One Concept with 3–4 sibling quotes from different traditions. It is generated from the repo and the owner approves each issue. Free at first; a paid tier or sponsorship comes later.
2. **Book and prints.** A "42 Maxims" book (the top 42 by Moral Rank, each with cross-tradition quotes), plus typographic posters and prints via print-on-demand (e.g. Gelato/Prodigi). PD source texts make this clean. Check the licence of any translation used in print.
3. **App (later).** "Maxim of the day", widgets, reflection prompts, built from the same data. Only once the newsletter shows traction.
4. **Ads last, if ever.** If they happen at all: no ads on religious-text pages, and nothing intrusive. Affiliate links to good editions of source books are a softer option.

---

## 11. Approvals (the owner decides; agents never do these on their own)

| Item | Who approves |
|---|---|
| Concept maxims/definitions (`definition_status: approved`) | **the owner** |
| Concept merges, splits, renames, deletions | **the owner** |
| `expresses` links across traditions; any `misattributed` publication | **the owner** |
| Tradition `derives_from` table and scoring constants | **the owner** |
| Domain purchase and DNS | **the owner** |
| Any paid service (LLM/embedding spend above the agreed budget, newsletter paid tier, R2, POD) | **the owner** |
| Production deploy (first launch, and any deploy that changes the scoring config) | **the owner** |
| Non-PD translation use (`fair-dealing-short`) | **the owner** |
| Routine verified-quote PRs | the owner (until he opts in to Devsy auto-merge) |
| Code PRs (site, pipeline) | Devsy reviews; the owner for anything touching data policy |

---

## 12. Milestones

| # | Milestone | Deliverables | Exit criteria |
|---|---|---|---|
| M0 | Skeleton (week 1) | Repo, Astro scaffold, zod schemas, 10 hand-checked seed quotes, `scoring.ts` + worked-example test, CI, CF Pages preview | Test passes; preview deploys |
| M1 | Pages (weeks 2–3) | Quote/Concept/Thinker/Tradition templates, Scoreboard, Pagefind search, structured data | All page types render from seed data |
| M2 | Pipeline v1 (weeks 3–5) | Ingest + licence check, verify, explain, lint, PR bot | Pipeline opens a 15-quote PR that the owner can review in < 10 min |
| M3 | Clustering (weeks 5–6) | Embeddings, cluster + LLM review, merge proposals, scoreboard diff in PRs | ≥ 70% link acceptance on a test batch |
| M4 | Content to MVP (weeks 6–9) | ~200 quotes, 30–60 approved Concepts, graph view, Misattributed + Method pages | Coverage targets in §3 met |
| M5 | Launch (week 10) | Domain, newsletter signup, analytics, sitemap, Search Console; **the owner approves prod deploy** | Live; first newsletter issue sent |
| M6 | Grow (post-launch) | Weekly batches, newsletter cadence, book/print exploration | §2 metrics tracked monthly |

---

## 13. Open questions for the owner

1. **Name and domain:** keep "42 Maxims"? Which domain (e.g. 42maxims.com / .org)? And what budget?
2. **Seed set:** can you export the old Obsidian vault as seed data? Is there a list of must-include traditions or thinkers for the MVP?
3. **Scope of thinkers:** include modern and living thinkers, where quotes are copyrighted and limited to short fair-dealing extracts? Or PD only for the MVP?
4. **Translations:** PD-only (often archaic English) or also our own AI-assisted modernised translations, clearly labelled?
5. **Scoring weights:** are you happy with "diversity more than count" as set (3.0·T, 1.5·R)? Should influence (`derives_from`) discount at 0.5?
6. **Auto-merge:** may Devsy auto-merge fully verified, PD quote batches that link only to already-approved Concepts?
7. **Tensions:** should Concepts in tension (e.g. justice vs mercy) get their own "debates" view in MVP or later?
8. **LLM/embedding provider and monthly budget cap** for the pipeline.
9. **Newsletter platform** (Buttondown vs Beehiiv) and sender name/address.
10. **Brand voice:** academic-neutral (Wikipedia-like) or warmer and more reflective? That decides the explanation style guide.
11. **Misattributed page at launch:** yes or no? It is good for SEO but needs careful sourcing.
12. **Licence for our own content** (explanations, definitions, data): CC BY-SA, CC BY-NC, or all rights reserved (keeps book/app options open)?
