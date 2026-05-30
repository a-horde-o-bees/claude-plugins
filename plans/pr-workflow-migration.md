# PR workflow migration

Finish the half-done migration from direct-to-main to PR-based main by moving the plugin-version auto-bump out of `.githooks/pre-commit` (which never fires on PR merges) and into a server-side workflow on `push: main`.

## Goal

PR-based work as the canonical path on this repo. Branch protection (already configured) gates merges on `test` + `validate` and requires a PR. Plugin patch versions bump server-side after merge, preserving the bump-as-deployment-signal pattern that `/checkpoint`'s marketplace sync depends on. Downstream consumers continue to pull `claude plugins update` against the bumped versions; nothing about the marketplace contract changes.

## What this plan lands

- `CLAUDE.md` Workflow section corrected to record PR-based as canonical (replacing the temporary direct-to-main directive committed in `6b5f699`, which mis-read the project direction).
- `.github/workflows/auto-bump.yml` — server-side analog to the local pre-commit hook. Runs on every push to `main`, detects plugins with non-manifest changes since the previous push, bumps each affected plugin's patch version, and pushes back a single `[skip-bump]`-tagged commit. The tag plus the manifest-only nature of the bump commit jointly prevent loops.
- This plan.

## Honest open items

- **Branch protection bypass for `github-actions[bot]`** — branch protection requires PRs to `main`; the auto-bump workflow pushes directly. Admins already bypass (`enforce_admins: false`); the bot needs the same. Options:
    1. Add `github-actions[bot]` as a bypass actor in the protection rule (Settings → Branches → main → bypass actors). Simplest; recommended.
    2. Use a PAT with admin scope as the workflow's token. Adds a secret to rotate.
    3. Have the workflow open a small bump PR that auto-merges (0 required approvals make this viable). Most layers; most "by-the-book."
- **Local hook retention** — `.githooks/pre-commit` keeps its bump logic for now as a belt for admin-bypass direct-to-main edge cases (hot fixes, this migration session, future emergencies). Retire after the server-side workflow has been observed to fire correctly on a real plugin PR.
- **First proof run** — the next PR that actually touches plugin code (not config like this one) is the verification: it should merge, the auto-bump workflow should fire on the resulting push to main, the affected plugin's `plugin.json` should bump, and `/checkpoint` on `main` should sync the new version. If anything misbehaves, iterate before retiring the local hook.

## Why the protection arrival decides the direction

Both the local hook (2026-03-26) and the CI workflows (2026-04-20/21) are content-neutral about path — neither *requires* direct-to-main or PR. The branch protection on `main`, configured after the workflows existed, is the only artifact in the chain that picks a side. Adding protection is a deliberate, costly act for a maintainer (it constrains their own work). The presence of protection in `2026-05` is the strongest signal that the project intended to be PR-based; the missing piece was server-side bumping, not stricter direct-to-main discipline.

## Out of scope for this plan

- Migrating the bump from patch (z) to semantic-version triage — current convention is patch-only; promote later if the marketplace ever surfaces release notes.
- The `/git-pr` skill — captured separately in `plans/git-plugin-pr-workflow.md`. Independent: that plan is about the workflow loop (open/status/merge/cleanup); this plan is about the bump signal.
