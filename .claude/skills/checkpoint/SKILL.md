---
name: checkpoint
description: Bundle the development checkpoint cycle for the current branch — commit (via /git), push, and CI watch. On main, also sync skill delivery per the mode in `.claude/skills/checkpoint/settings.json` — `installed` (npx user-scope) or `marketplace` (plugin cache update).
allowed-tools:
  - Skill
  - Bash(uv run *)
  - Bash(claude plugins *)
  - Bash(git branch *)
  - Bash(git diff *)
---

# /checkpoint

Bundle the development checkpoint cycle for the current branch — commit, push, watch CI. When the current branch is `main`, also sync skill delivery per the mode declared in `settings.json`. Sandbox and feature branches stop after the CI gate because the skills sync is main-scoped.

Two sync modes are bundled:

- **`installed`** — reinstalls any user-scope skill in `.claude/installed-skills.json` whose source plugin version has changed, via `npx skills add`. No session restart needed; new artifacts symlink into `~/.claude/skills/<name>/` and appear in the registry mid-session
- **`marketplace`** — refreshes the project's marketplace cache and runs `claude plugins update` for plugins whose code changed in the push. Requires session restart afterwards because the plugin install is cached

`settings.json` declares which mode this project uses. Default committed value is `installed`. Downstream users who prefer the traditional plugin path can change it to `marketplace` (and arrange their own marketplace + plugin installs accordingly).

The generic commit + push + CI steps are delegated to `/git` verbs. The skills sync layer sits on top.

## Workflow

1. {branch} = bash: `git branch --show-current`

> Branch awareness — checkpoint runs the same commit/push/ci cycle on any branch. The skills sync is main-only because both sync modes pull from the repo's main branch.

2. Commit — skill: `/git commit`
3. {pending-paths} = bash: `git diff --name-only origin/{branch}..HEAD 2>/dev/null` — empty when local is at origin/{branch} or origin/{branch} doesn't exist yet
4. Push — skill: `/git push --branch {branch}`
5. CI gate — skill: `/git ci --branch {branch}`

6. If {branch} is `main`:
    1. {sync-mode}: bash: `uv run python -c "import json; print(json.load(open('.claude/skills/checkpoint/settings.json'))['sync_mode'])"`
    2. If {sync-mode} is `installed`: {sync-result}: Call: `_sync_installed.md`
    3. Else if {sync-mode} is `marketplace`: {sync-result}: Call: `_sync_marketplace.md` ({pending-paths}: {pending-paths})
    4. Else: Exit to user: unknown sync_mode `{sync-mode}` in `.claude/skills/checkpoint/settings.json` — expected `installed` or `marketplace`

### Report

- Branch: {branch}
- Commits pushed: count and branch (from /git push)
- CI status from /git ci (passed, failed, dispatched, or no-runs)
- If {branch} is `main`:
    - Sync mode: {sync-mode}
    - Sync result: per the called component's return — surface verbatim, including any restart recommendation
- Else: note that the skills sync is main-only and was skipped on this branch
- If nothing was pushed: checkpoint complete
