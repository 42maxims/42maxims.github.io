# Operations
_Owner: oo-42maxims. Accounts listed by name only; no secrets in this repo._

## Services and costs
- **Hosting:** GitHub Pages user site `42maxims.github.io`, branch `master`, repo root (legacy build, `.nojekyll`). Free.
- **CI:** GitHub Actions `.github/workflows/ci.yml`: runs tests and checks committed HTML matches `build.py` output. Free.
- **Domain:** 42maxims.com chosen, not bought (issue #5). Cost: €0 today.
- **Data sources:** public texts (Gutenberg, Sacred-texts, Sefaria, Access to Insight, Wikisource), Wikiquote/Wikipedia for probable labels, Quote Investigator for misattributions. No scheduled refresh; content is added in batches.

## Accounts and identity
- GitHub account `42maxims` (anonymous project account), commit identity **Max Ims** `<37961849+42maxims@users.noreply.github.com>`.
- The box is shared and its `gh` CLI holds two accounts. The default must stay on the other (portfolio) account. For this repo only: `gh auth switch -u 42maxims` right before a push or issue/PR action, then switch back to the default account immediately after.
- Never commit with any other identity, and never add personal names to the repo.

## Build, test, deploy
```
python3 build.py                        # regenerate HTML + data/generated/
python3 -m unittest discover -s tests   # must print OK
git -c user.name="Max Ims" -c user.email=37961849+42maxims@users.noreply.github.com commit -am "..."
gh auth switch -u 42maxims && git push origin master && gh auth switch -u <default account>
```
Pushing to `master` deploys; check `gh api repos/42maxims/42maxims.github.io/pages/builds/latest` reads `built`, then curl the home page and one maxim page for 200.

## Claude Code
- `~/.local/bin/claude -p "<brief>"` (always the full path). Node 22 via nvm: `unset NPM_CONFIG_PREFIX` first.
- Brief it as the expert curator; it must follow CLAUDE.md (never fabricate, honest labels, short attributed modern quotes). Work in small batches; build, test, commit and verify after each.

## Approvals
- **oo-42maxims may:** add/relabel quotes, add voices/sources, fix bugs, merge roadmap-aligned PRs (including outside contributors' after review), close duplicates, open issues.
- **Needs the project owner:** spend of any kind, domains, outreach/newsletters/social posts, new bots, sharing user data, scoring-constant changes, new concepts that change The 42 materially, and any history rewrite or force-push.

## Content pipeline
1. Pick an open issue or a weak maxim (Emerging, or quotes labelled probable).
2. Source exact wording at a primary or reputable source; fetch the URL and confirm the text.
3. Label `ver`, `rel`, `conf` per CLAUDE.md. Attach voice and source slugs.
4. Build and test; one small batch per commit or PR; note ranking changes to The 42.
