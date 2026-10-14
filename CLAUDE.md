# Notes for AI agents working on this repo
- Data lives in `data/maxims.json`; never hand-edit generated HTML or `data/generated/`. Run `python3 build.py` and commit the output.
- Run `python3 -m unittest discover tests` before pushing. Scoring constants in `scoring.py` change only with the owner's approval.
- Every quote needs a `source` URL and an honest `ver` label (verified = checked against primary text/reputable translation; probable = secondary source only; unverified = scores 0). Never invent or "fix" quote wording.
- Voice: warm and reflective. Never rank traditions or thinkers. Respect religious texts.
- English first; non-English sources use public-domain or credited translations, or AI-assisted ones labelled as such.
- Modern authors: short attributed quotes only.
- Commit identity for this repo: Max Ims <37961849+42maxims@users.noreply.github.com>. The project is anonymous; do not add personal names.
- the owner approves: new concept definitions, merges of concepts, domain purchase, spend, scoring changes.
