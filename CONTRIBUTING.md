# Contributing
Thank you for helping. Suggestions are welcome as issues or pull requests.
1. Add or edit entries in `data/maxims.json`. Each quote needs: exact text, thinker (or "Anonymous"), tradition, era, work/citation, a `source` URL where the wording can be checked, and a verification label.
2. Run `python3 build.py` and `python3 -m unittest discover tests`, and commit the regenerated files.
3. Verification labels: `verified` = exact wording seen at a primary/reputable source URL; `probable` = only seen in a reliable secondary source; `unverified` = no traceable origin (scores 0); `misattributed` = known wrong attribution.
4. Be honest about verification. A well-loved quote with no traceable source is welcome, labelled `unverified`.
5. Keep modern quotations short and attributed. Use public-domain or credited translations.
6. Write warmly and respectfully; we compare ideas, never rank traditions or people.
Step-by-step workflow, data format and full source-verification rules: see the "How to add a maxim or quote" section of [CLAUDE.md](CLAUDE.md).

By contributing you agree your contributions are licensed CC BY-SA 4.0.
