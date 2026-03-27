---
name: ocd-push
description: >
  Push commits to remote. Requires explicit --branch to name the push target.
  Runs /ocd-commit first if uncommitted changes exist, previews unpushed commits,
  then pushes.
argument-hint: "--branch <branch-name>"
---

# /ocd-push

Push local commits to remote. Requires explicit branch name — no default target. Ensures working tree is committed first, previews unpushed commits, then pushes.

## Trigger

User runs `/ocd-push`

## Route

1. If not --branch: Exit to user — respond with skill description and argument-hint
2. Push target is `origin/{branch}`

## Workflow

1. Check for uncommitted changes
    1. Run `git status --short`
    2. If changes exist:
        1. Run `/ocd-commit`
        2. If commit fails or produces no commits: Exit to user — report failure
2. Check for unpushed commits
    1. Run `git log --oneline @{upstream}..HEAD`
    2. If no unpushed commits: Exit to user — report "Nothing to push — local and remote are in sync"
3. Present push preview — branch name, remote, commit count and list (oneline format)
4. Push to remote: `git push origin {branch}`
5. Report result

### Report

- Commits pushed: count and branch
- Remote URL and status

## Rules

- Never force push
- Explicit --branch is required — no default push target; naming the branch is the confirmation
- If upstream is not set, use the provided --branch to set it with `git push -u origin {branch}`
- Commit step is fully automated via /ocd-commit — no double-confirmation on commit content
