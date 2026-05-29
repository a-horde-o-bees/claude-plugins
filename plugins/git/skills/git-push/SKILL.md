---
name: git-push
description: Use when local commits need to reach the remote — explicit signals "push", "push my branch", "push to origin", or any context where publishing committed work is the next action. Auto-commits uncommitted changes via /git-commit before pushing. Requires explicit --branch to confirm the target; refuses to push from detached HEAD.
argument-hint: "--branch <name>"
allowed-tools:
  - Bash(git *)
  - Skill
---

# /git-push

Push local commits to a named remote branch.

## Rules

- Explicit `--branch` required; naming the branch is the confirmation
- Refuse to push from detached HEAD — no branch to publish
- Branch mismatch exits with explanation — no prompt, no default action
- When the auto-commit fallback fires: stage by name (never `git add -A`); never amend; never force-push
- Never force-push or run destructive git operations

## Process

1. Preconditions:
    1. {current-branch}: bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} is `HEAD`: Exit to user: detached HEAD — checkout or create a branch before pushing
    3. If not --branch: Exit to user: push requires `--branch <name>`
    4. If {current-branch} ≠ {branch}: Exit to user — branch mismatch (current `{current-branch}`, requested `{branch}`). To push the current branch: re-invoke with `--branch {current-branch}`. To move commits to {branch} first: ask for rebase/merge help.

2. Auto-commit pending changes:
    1. {pending}: bash: `git status --short`
    2. If {pending} non-empty:
        1. skill: `/git-commit`
        2. If no commits were produced: Exit to user: commit step produced nothing — investigate and re-invoke

3. {upstream-set}: bash: `git rev-parse --abbrev-ref @{upstream} 2>/dev/null` exits 0
4. If {upstream-set}:
    1. {unpushed}: bash: `git log --oneline @{upstream}..HEAD`
    2. If {unpushed} is empty: Exit to user: nothing to push — local and remote in sync

5. Present push preview — branch, remote, commit count + oneline list
6. Push:
    1. If {upstream-set}: bash: `git push origin {branch}`
    2. Else: bash: `git push -u origin {branch}` — first push sets upstream

## Report

- Commits pushed: count and branch
- Remote URL and push status
