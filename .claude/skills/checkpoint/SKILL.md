---
name: checkpoint
description: Bundle the development checkpoint cycle for the current branch — /git-commit, /git-push, /git-ci. On main, also sync skill delivery per the configured mode — `marketplace` (refresh plugin cache + `claude plugins update`) or `installed` (npx user-scope reinstall via `.claude/installed-skills.json`).
allowed-tools:
  - Skill
  - Bash(uv run *)
  - Bash(claude plugins *)
  - Bash(git branch *)
  - Bash(git diff *)
---

# /checkpoint

This project's wrapper around `/git-checkpoint`. Runs the commit + push + CI cycle, then on `main` syncs skill delivery per the configured mode. Sandbox and feature branches stop after the CI gate.

## Gating

User-gated only. `/checkpoint` runs when the user invokes it explicitly. Do **not** fire `/checkpoint` — or execute its sub-steps individually (`/git-commit`, `/git-push`, `claude plugin marketplace update`, `claude plugin update`) — as a side effect of completing other work. Completing a task is an *implementation* signal; checkpointing is a separate *commit* signal that only the user can give.

When other work produces changes that warrant committing:

1. Leave the changes in the working tree
2. Surface a short summary of what changed and offer to commit
3. Wait for the user's signal ("commit", "/checkpoint", "land it", "push", or similar)

The same gate applies to bridging when `/checkpoint` itself isn't yet installed: the bridging manual run requires explicit user authorization (e.g., "run /checkpoint and bridge the gap" or "push and update the cache"). Do not bridge as cleanup after each task.

## Sync modes

- **`marketplace`** — refreshes the project's marketplace cache and runs `claude plugins update` for plugins whose code changed in the push. Requires session restart afterwards because the plugin install is cached. Use when consuming this repo's plugins via `claude plugin install`.
- **`installed`** — reinstalls any user-scope skill in `.claude/installed-skills.json` whose source plugin version has changed, via `npx skills add`. No session restart needed; new artifacts symlink into `~/.claude/skills/<name>/` and appear in the registry mid-session. Use when consuming individual skills via `npx skills add`.

`settings.json` (next to SKILL.md) declares which mode this project uses. Default committed value is `marketplace` — the plugin-install path is the primary supported channel.

The commit + push + CI steps are delegated to `/git-commit`, `/git-push`, and `/git-ci`. The skills sync layer sits on top.

## Workflow

1. {branch} = bash: `git branch --show-current`

    > Branch awareness — checkpoint runs the same commit/push/ci cycle on any branch. The skills sync is main-only because both sync modes pull from the repo's main branch.

2. Apply the project version bump — bash: `python3 scripts/bump-apply.py --fetch origin/main` — for each plugin with code changes versus a freshly-fetched `main`, set its version to `z+1` (idempotent; a manual higher bump is respected). The bump rides in this commit, so change + version land together — no server-side push-back. Running it here, against a just-fetched `main`, is the merge-time recompute: it keeps the landing version `z+1` of the latest base even if `main` advanced while the branch was open. `bump-check.yml` (required) is the belt.
3. Commit — skill: `/git-commit`
4. {pending-paths} = bash: `git diff --name-only origin/{branch}..HEAD 2>/dev/null` — empty when local is at origin/{branch} or origin/{branch} doesn't exist yet
5. Push — skill: `/git-push --branch {branch}`
6. CI gate — skill: `/git-ci --branch {branch}`
7. If {branch} is `main`:
    1. {sync-mode}: bash: `cd <THIS-FILE-DIR> && uv run python -c "import json; print(json.load(open('settings.json'))['sync_mode'])"`
    2. If {sync-mode} is `marketplace`: {sync-result}: Call: `_sync_marketplace.md` ({pending-paths}: {pending-paths})
    3. Else if {sync-mode} is `installed`: {sync-result}: Call: `_sync_installed.md`
    4. Else: Exit process: unknown sync_mode `{sync-mode}` in `<THIS-FILE-DIR>/settings.json` — expected `marketplace` or `installed`

### Report

- Branch: {branch}
- Commits pushed: count and branch (from /git-push)
- CI status from /git-ci (passed, failed, dispatched, or no-runs)
- If {branch} is `main`:
    - Sync mode: {sync-mode}
    - Sync result: per the called component's return — surface verbatim, including any restart recommendation
- Else: note that the skills sync is main-only and was skipped on this branch
- If nothing was pushed: checkpoint complete
