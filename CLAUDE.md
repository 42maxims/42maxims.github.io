# Notes for AI agents working on this repo
_Maintained by oo-42maxims. See OPS.md for gh account rules and approvals, ROADMAP.md for open issues._
- Data lives in `data/maxims.json` (concepts, quotes, traditions), `data/voices.json` and `data/sources.json`; never hand-edit generated HTML or `data/generated/`. Run `python3 build.py` and commit the output.
- Run `python3 -m unittest discover tests` before pushing. Scoring constants in `scoring.py` change only with the project owner's approval.
- Every quote needs a `source` URL and an honest `ver` label (verified = checked against primary text/reputable translation; probable = secondary source only; unverified = scores 0). Never invent or "fix" quote wording.
- Voice: warm and reflective. Never rank traditions or thinkers. Respect religious texts.
- English first; non-English sources use public-domain or credited translations, or AI-assisted ones labelled as such.
- Modern authors: short attributed quotes only.
- Commit identity for this repo: Max Ims <37961849+42maxims@users.noreply.github.com>. The project is anonymous; do not add personal names.
- The project owner approves: new concept definitions, merges of concepts, domain purchase, spend, scoring changes.

## How to add a maxim or quote (content workflow)
1. **Check for an existing concept** in `data/maxims.json` → `concepts`. If the idea is already there (even in other words), add a quote to it; don't create a near-duplicate.
2. **New concept** (needs the project owner's approval in the PR): add to `concepts`:
   `{"slug": "kebab-case", "maxim": "One-line rule, imperative or plain statement.", "summary": "2–3 warm, reflective sentences in our own words.", "links": ["optional further-reading: a URL string, or {\"url\": \"https://...\", \"label\": \"Author, Title (Open Library)\"} for a book (prefer Project Gutenberg / Sacred Texts for public-domain texts, Open Library works pages for modern books; do not repeat a quote's own source URL)"]}`
3. **Add the quote** to `quotes`:
   ```json
   {"concept": "<concept slug>", "rel": "expresses|similar|partial|contrasts", "conf": 0.0-1.0,
    "ver": "verified|probable|disputed|unverified|misattributed",
    "text": "exact wording from the source", "thinker": "Name or Anonymous", "voice": "<slug in data/voices.json>",
    "tradition": "<key in traditions>", "era": "axial|classical|medieval|early-modern|modern|contemporary"  # shown as periods: Ancient (before 200 BCE), Classical (200 BCE–600 CE), Medieval (600–1500), Early modern (1500–1800), Modern (1800–1950), Contemporary (1950–today),
    "work": "Title, chapter/verse, translator", "source_id": "<slug in data/sources.json>", "translation": "optional: translator/licence, or 'AI-assisted (labelled)'",
    "source": "URL where the exact wording can be read, or \"\" if none"}
   ```
   New tradition? Add it under `traditions` with `name` and, if it grew out of another, `derives_from`.
   Optional `"echoes": "Marcus Aurelius, Meditations V.20"`: a short note (under 120 characters) naming the older saying a modern quote restates. It shows as a small "Echoes …" line under the quote on maxim, voice and source pages. Use it only when the debt is clear (the author cites it, or the wording plainly follows it); it does not affect scoring.
   Optional `"clips": [{"id": "<11-char YouTube id>", "start": <int s>, "end": <int s>, "label": "Hear it spoken", "title": "<video title>", "channel": "<channel>", "kind": "verbatim|paraphrase|discussed"}]` on a **verified** quote: a short click-to-load YouTube clip (youtube-nocookie, nothing loads until clicked) plus a "Watch on YouTube" off-ramp link. Only add one when the speaker really says the quoted words in an official/legitimate upload; confirm the id via oEmbed and start/end against the official transcript. `kind` (optional, default verbatim): use `discussed` for third-party uploads where the speaker only talks about the line, `paraphrase` when the spoken words differ slightly. Tests fail on malformed clips. **Whole-video reference:** omit `start`/`end` (needs `id`, `label` = short link text, `title`, `channel`, and `kind: "discussed"`); renders only a compact "Watch on YouTube: <label> ↗" link plus "<thinker> discusses this idea" (optional `note` overrides that text when the video speaker is not the quote's thinker), with no embed and no Play button; allowed on verified or probable quotes (timed clips stay verified-only).
   `thinker` and `work` stay as display text (`work` holds the precise locus, e.g. "Meditations IV.24, tr. George Long"); `voice` and `source_id` link the quote to its voice and source pages.
4. **Link a voice and a source** (see "Voices and sources" below): reuse an existing slug if there is one, otherwise add an entry.
5. **Verify the source** (rules below), set `ver` honestly.
6. `python3 build.py && python3 -m unittest discover tests`, commit data + generated HTML together, open a PR (one concept or a small batch per PR). Push to `master` deploys.

### Source verification rules
- **verified**: you fetched the source URL and the exact wording appears there; source is a primary text, a reputable/public-domain translation (Gutenberg, Sacred-texts, Sefaria, Access to Insight, Bible Gateway, ctext), or the author's own book/site/recorded talk.
- **probable**: wording found only in a reliable secondary source (Wikipedia, Wikiquote with a cited work, a major newspaper). Say "checked via X, not the original" in `work`.
- **unverified**: popular saying with no traceable origin. Allowed, shown with label, scores 0. Never upgrade without a source.
- **disputed / misattributed**: credible sources disagree, or the attribution is known to be wrong (check Quote Investigator, Wikiquote "Misattributed"). Record the true origin if known.
- Never paraphrase inside `text`; a paraphrase must say so in `work`. Never invent a citation. Modern authors: one or two sentences max. AI-assisted translations must say "AI-assisted translation" in `translation`.

## Voices and sources
Each quote points to one **voice** (who said it) and one **source** (which work it is from). They get pages at `/voices/<slug>/` and `/sources/<slug>/`, and maxim pages link the thinker name and work to them.
- `data/voices.json`: `{"<slug>": {"name", "kind": "person|collective|text|legendary", "dates", "tradition": "<key in traditions>", "period": "<era key>", "summary", "confidence": "solid|thin|uncertain", "refs": ["https://..."]}}`
- `data/sources.json`: `{"<slug>": {"title", "voice": "<voice slug> or null", "kind": "book|scripture|talk|article|other", "dates", "tradition", "period", "summary", "confidence", "refs"}}`
- **Source kind** is the type label and filter on the Sources index: `book`, `scripture` (Bible, Qur'an, Pali canon, Gita, Tao Te Ching, and the Talmud and hadith collections), `talk` (speech, lecture, video, podcast), `article` (essay, paper, blog post), `other` (a saying or principle with no single text). The index also lists every YouTube video attached to a quote in a "YouTube videos" group (built from `clips`; videos are not entries in sources.json). Tests fail on an unknown kind. On the Sources index every type chip is a link to its section (`#books` etc.) and filters when JS is on; filter state lives in the URL hash (`#books`, `#all`, `#channel=<slug>`). A video's channel chip links to `/voices/<slug>/` when the channel is a voice's own (name match or `CHANNEL_ALIAS` in build.py), otherwise it filters videos by channel. With JS only the filter buttons show; without JS only the anchor row does.
- **Grouping:** one source per book, whatever the chapter or translation (all Meditations quotes share `meditations`; each Bible book is its own source: `gospel-of-matthew`, `proverbs`, ...). Each hadith collection, each Pali collection (`samyutta-nikaya`, `sutta-nipata`), each Plato dialogue is one source. The chapter/verse/translator stays in the quote's `work`.
- **Kinds of voice:** `person` (a historical individual); `collective` (many hands: `popular-saying`, `hebrew-wisdom-writers` for Proverbs, `psalmists`, `torah-writers`); `scripture` (displayed as "Scripture"; a voice that IS a text with no named human author: `qoheleth`, `author-of-job`, `author-of-joshua`, `author-of-hebrews`, `quran`); optional per-voice `label` overrides the displayed chip without changing kind or structured data (`"Scripture"` on `psalmists`, `torah-writers`, `hebrew-wisdom-writers`, `zechariah`, `micah`; named persons such as Jesus, Paul and James stay "Person"); `legendary` (a traditional figure whose historicity or dates can't be established: `laozi`, `homer`, `krishna`, `king-tang`).
- **Voices index filter:** same pattern as Sources, keyed on the DISPLAYED chip label (`voice_label()` in build.py: per-voice `label` override, else the kind label). One section per label (ids = `label_slug`, e.g. `#person`, `#scripture`, `#collective`, `#traditional-or-legendary-figure`), buttons with counts and `aria-pressed` (JS only), anchor row without JS, state in the URL hash (`#all` default). The kind chip on each row filters; on a voice page it links to `/voices/#<label-slug>`. Own small script (`VOICES_JS`), shared CSS (`.typebar`, `.chip-link`).
- **Disputed authorship:** say "traditionally attributed to X" and give the scholarly view in neutral words (e.g. Proverbs → voice `hebrew-wisdom-writers`, summary notes the traditional attribution to Solomon). Pauline letters whose authorship is disputed still use voice `paul-the-apostle`; the source summary says it is disputed.
- **Misattributed quotes** (`ver: misattributed`): `voice` is the person the saying is popularly credited to (e.g. Aristotle for Durant's "We are what we repeatedly do"); the `thinker` text and the verification pill tell the true story. A verified quote whose real author is known (e.g. Goldsmith, often credited to Confucius) uses the real author.
- **Summaries:** 2–3 sentences, warm but strictly factual (who/what, dates, tradition, period). Check every fact against reputable references (Wikipedia, Britannica, Stanford Encyclopedia of Philosophy, IEP, Quote Investigator) and list them in `refs`. Never invent. Use `confidence: "thin"` when little is known or sourcing is weak, `"uncertain"` when identity, authorship, dates or origin are seriously disputed; the page then shows a caution note.
- A voice may have no quotes of its own if it is the author of a source (e.g. `plato` for the Apology). Tests fail on unknown slugs, missing fields, empty summaries, or entries nothing uses.

## Page model (since M0.1)
- Each maxim page shows a **seed** expression at the top: the oldest-period quote, then the best verified one. Set `"seed": <index into that concept's quotes>` on the concept to override it. All other quotes follow under "Related expressions".
- Near-duplicate sayings belong under the existing maxim as `similar`/`partial` quotes. Don't create a new concept for them.
- Don't use the Guardian "digested read" as a source; it's satire. Use Wikipedia or the book for Peterson's rule titles.
