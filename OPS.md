# Operations
- **Hosting:** GitHub Pages, user site `42maxims.github.io`, branch `master`, root folder (legacy build, `.nojekyll`). Free.
- **Accounts (names only, no secrets here):** GitHub `42maxims` (owner, anonymous project account); Google account for the same identity. Credentials are held by the project owner, not in this repo.
- **CI:** GitHub Actions (`.github/workflows/ci.yml`): runs tests and checks the committed HTML matches `build.py` output. Free for public repos.
- **Domain:** 42maxims.com chosen, not bought. Needs the project owner's approval.
- **Deploy:** push to `master`; Pages publishes within a few minutes.
- **Approvals needed from the project owner:** spend, domain, concept definitions/merges, scoring constants.

## Content pipeline
Owner: COO-42maxims (after handover); until then the portfolio agent. The project owner approves new concepts, concept merges and scoring changes.
1. **Discover**: pick a concept from ROADMAP/seed notes (`SEED-NOTES` themes: Peterson, Watts, Confucius, Buddhism, Christianity, Descartes, popular sayings) or an open issue.
2. **Source**: find exact wording at a primary or reputable source; fetch the URL and confirm text.
3. **Label**: set `ver`, `rel`, `conf` per CLAUDE.md rules.
4. **Build & test**: `python3 build.py && python3 -m unittest discover tests`.
5. **PR**: small batches; PR description lists each quote, its source URL and label, and change to The 42 rankings. CI must pass.
6. **Approve & merge**: the project owner for new concepts; quotes on existing concepts may be merged by the owner. Merge to `master` deploys.
Priority now: get more maxims to 2+ independent traditions so they leave "Emerging"; upgrade `probable` quotes by checking primary texts.
