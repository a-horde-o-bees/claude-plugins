---
name: checkpoint
description: Bundle the development checkpoint cycle for the current branch — commit (via /git), push, and CI watch. On main, also sync user-scope skills per the `.claude/installed-skills.json` manifest.
allowed-tools:
  - Skill
  - Bash(uv run *)
  - Bash(git status *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git branch *)
---

# /checkpoint

Bundle the development checkpoint cycle for the current branch — commit, push, watch CI. When the current branch is `main`, also sync user-scope skills via `npx skills`. Sandbox and feature branches stop after the CI gate because the skills sync is main-scoped — `npx skills` pulls from the repo's main branch.

The generic commit + push + CI steps are delegated to `/git` verbs (`commit`, `push`, `ci`). The project-specific layer — the skills sync — sits on top of those calls. Other projects can use `/git checkpoint` directly when they don't need this layer.

The skills sync reads `.claude/installed-skills.json` (gitignored per-user) and reinstalls any declared skill whose source plugin version has changed since last install via `npx skills add`. The manifest is the source of truth for which user-scope skills the project author maintains; downstream users curate their own.

## Workflow

1. {branch} = bash: `git branch --show-current`

> Branch awareness — checkpoint runs the same commit/push/ci cycle on any branch. The skills sync is main-only because `npx skills` pulls from the repo's main branch.

2. Commit — skill: `/git commit`
3. Push — skill: `/git push --branch {branch}`
4. CI gate — skill: `/git ci --branch {branch}`

> /git ci handles synchronous-vs-async dispatch and returns {ci-status} ∈ {passed, failed, dispatched, no-runs}. Non-main branches typically resolve to no-runs.

5. If {branch} is `main`:
    1. {skills-sync} = bash: `uv run .claude/skills/checkpoint/scripts/sync_skills.py` — reads `.claude/installed-skills.json` and reinstalls any declared skill whose source plugin version changed; no-op when the manifest is absent or every entry is up to date

### Report

- Branch: {branch}
- Commits pushed: count and branch (from /git push)
- CI status from /git ci (passed, failed, dispatched, or no-runs)
- If {branch} is `main`:
    - Skills sync: per-skill action lines from {skills-sync} (installed / updated / up-to-date / failed); call out failures
- Else: note that the skills sync is main-only and was skipped on this branch
- If nothing was pushed: checkpoint complete
