# Operations
_Run by the maintainers (the maintainer bot, under the project account). Public notes for contributors; no secrets or private account details in this repo._

## Services and costs
- **Hosting:** GitHub Pages user site `42maxims.github.io`, branch `master`, repo root (legacy build, `.nojekyll`). Free.
- **CI:** GitHub Actions `.github/workflows/ci.yml`: runs `scripts/validate.py`, the build and the tests on every PR and push to master, and fails if committed HTML differs from `build.py` output or generated files are uncommitted. Required to pass before a PR can merge (branch protection on `master`). Free.
- **Domain:** 42maxims.com (DNS only, WHOIS privacy on), GitHub Pages custom domain with HTTPS enforced. `build.py` writes `CNAME`. `42maxims.github.io` redirects to it. Analytics: Plausible (no cookies).
- **Data sources:** public texts (Gutenberg, Sacred-texts, Sefaria, Access to Insight, Wikisource), Wikiquote/Wikipedia for probable labels, Quote Investigator for misattributions. No scheduled refresh; content is added in batches.

## Identity
- Project GitHub account `42maxims`; maintainer commit identity **Max Ims** `<37961849+42maxims@users.noreply.github.com>`. Contributors commit under their own identity.
- The project is anonymous: never add personal names, accounts or emails of the owner or maintainers to the repo.

## Build, test, deploy
```
python3 scripts/validate.py             # data check
python3 build.py                        # regenerate HTML + data/generated/
python3 -m unittest discover -s tests   # must print OK
git status --porcelain                  # empty once everything is committed
```
Merging or pushing to `master` deploys via GitHub Pages. Contributors open PRs; maintainers may still push small changes directly to `master` for now. After a deploy, maintainers check the Pages build reads `built` and that the home page and a maxim page return 200.

**IndexNow (after each deploy).** `build.py` publishes the public key file `/<INDEXNOW_KEY>.txt`. The `indexnow` workflow (`.github/workflows/indexnow.yml`) runs when the Pages deploy finishes successfully: it waits for the key file to be live, then submits the pages whose HTML changed in the deployed commit (`scripts/indexnow.py --since HEAD~1`). It can also be started by hand from the Actions tab (full sitemap). If it fails or a deploy covered several commits, run it locally after the deploy: `python3 scripts/indexnow.py` (all sitemap URLs) or `python3 scripts/indexnow.py --since <last submitted commit>`; HTTP 200 or 202 means accepted. One submission reaches Bing, Yandex, Seznam, Naver and the other IndexNow engines. No account is needed. Rotate the key by changing `INDEXNOW_KEY` (32 hex) and rebuilding; the old key file disappears with the rebuild.

## Approvals
- **Maintainers may:** add/relabel quotes, add voices/sources, fix bugs, review and merge outside PRs that only add or correct quotes (and their voices/sources) once CI passes, merge roadmap-aligned code PRs after review, close duplicates, open issues.
- **Needs the project owner:** new maxims (concepts) and merges/splits/renames, scoring-constant changes, tradition `derives_from` (influence) links, spend of any kind, domains, outreach/newsletters/social posts, new bots, sharing user data, and any history rewrite or force-push. Full table: SPEC.md §12.

## Content pipeline
1. Pick an open issue or a weak maxim (Emerging, or quotes labelled probable).
2. Source exact wording at a primary or reputable source; fetch the URL and confirm the text.
3. Label `ver`, `rel`, `conf` per AGENTS.md. Attach voice and source slugs.
4. Validate, build and test; one small batch per commit or PR; note ranking changes to The 42.
