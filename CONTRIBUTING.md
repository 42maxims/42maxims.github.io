# Contributing
Thank you for helping. Humans and AI agents (Claude Code, Cursor, Codex, Copilot, ...) are both welcome; the rules are the same. Agents: [AGENTS.md](AGENTS.md) has the full data format and verification rules, and is the file your tool already reads.

## Ways to help
- **Add a quote to an existing maxim** (most useful): a better source, an older or independent tradition, or an upgrade from `probable`/`unverified` to `verified`. See [issue #4](https://github.com/42maxims/42maxims.github.io/issues/4).
- **Propose a new maxim**: open a "Propose a maxim" issue first; don't add it in a PR. See [docs/proposals.md](docs/proposals.md).
- **Fix a bug or improve the site**: open a "Bug" issue or a small PR. Keep `build.py` stdlib-only.
- **Report a wrong quote or attribution**: use the "Add or correct a quote" issue.

## The sourcing bar
1. **Exact wording.** Copy the text exactly as it appears in the source you read. Never paraphrase inside `text`, modernise spelling, or merge two lines.
2. **A readable source.** `source` is a URL where the exact wording can be read: a public-domain text (Project Gutenberg, Sacred-texts, Wikisource, Sefaria, Access to Insight, SuttaCentral, Internet Archive), the author's own site or published book page, or an official recording. Give the precise locus (chapter/verse, translator) in `work`.
3. **An honest label** (`ver`):
   - `verified`: you opened the source and the exact wording is there.
   - `probable`: you found it only in a reliable secondary source (Wikipedia, Wikiquote with a cited work, a major newspaper); say "checked via X" in `work`.
   - `disputed`: credible sources disagree on wording or attribution.
   - `unverified`: a popular saying with no traceable origin (allowed, scores 0; `source` may be `""`).
   - `misattributed`: the attribution is known to be wrong; give the real origin if known.
4. **Beware the usual suspects.** Many quotes credited online to Rumi, the Buddha, Confucius, Einstein, Lincoln, Twain or a "Native American proverb" are modern inventions or paraphrases. Check [Quote Investigator](https://quoteinvestigator.com/) and Wikiquote's "Misattributed" and "Disputed" sections before submitting.
5. **Translations** must be public domain or credited. An AI-assisted translation must say so in `translation`.
6. **Modern and living authors:** one or two attributed sentences only.
7. **Never fabricate** a quote, citation, date or attribution, and never upgrade a label without a source. A PR that does will be closed.

## How to add content
Full field reference: [AGENTS.md](AGENTS.md#how-to-add-a-maxim-or-quote-content-workflow).
- **Quote:** add an object to `quotes` in `data/maxims.json` under an existing `concept` slug, with `rel` (`similar` is the default for a new tradition; `expresses` across traditions needs owner approval), `conf` (0 to 1), `ver`, `era`, `voice`, `source_id`, `tradition`, `work` and `source`.
- **Voice** (who said it) or **source** (which work): reuse an existing slug in `data/voices.json` / `data/sources.json` if there is one; otherwise add an entry with a factual 2–3 sentence summary and `refs` (Wikipedia, Britannica, SEP, IEP). One source per book, whatever the chapter or translation.
- **Tradition:** add a key under `traditions` with a `name`. If it grew out of another tradition, propose `derives_from` in the PR description; the project owner decides it because it changes scoring (SPEC.md §12).

## Needs the project owner's approval
New maxims; merging, splitting, renaming or deleting maxims; scoring constants in `scoring.py`; tradition `derives_from` links; `expresses` links across traditions; publishing a `misattributed` entry; new dependencies, trackers or paid services. Open an issue or flag it clearly in the PR; maintainers will not merge it without that approval.

## Build and test
Python 3 only, no install step.
```
python3 scripts/validate.py              # data check with clear error messages
python3 build.py                         # regenerate the HTML
python3 -m unittest discover -s tests    # must print OK
```
Commit the regenerated files together with your data change. CI runs the same steps and fails if the committed HTML is out of date. If you hit a merge conflict in generated files, take either side and rerun `python3 build.py`.

## Pull requests
- One maxim, a small batch of quotes (up to about 10) or one code change per PR.
- Fill in the PR checklist: what you verified and how, build and tests run, and any change to The 42 (order or membership).
- **Anonymity:** the project is anonymous. Don't put maintainers' personal names, accounts or emails in files, commits or PRs. Your own commit identity is up to you.
- Outside PRs are welcome. CI must pass before anything merges. Maintainers review and merge quote-only PRs (quotes plus their voices/sources) once CI passes; code PRs after review. New maxims, scoring changes and tradition influence (`derives_from`) links wait for the project owner's approval. Merging to `master` deploys to https://42maxims.com.
- Be kind. We compare ideas; we never rank traditions or people, and we treat religious texts with respect.

## Licence
Site content and data are CC BY-SA 4.0 (see [LICENSE](LICENSE)). By contributing you agree your contributions are licensed CC BY-SA 4.0 (the same licence as the project; no DCO sign-off or CLA needed). Quotes remain the property of their authors and translators.
