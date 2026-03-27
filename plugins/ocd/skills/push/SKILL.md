---
name: ocd-push
description: >
  Push commits to remote. Runs /ocd-commit first if uncommitted changes exist,
  shows what will be pushed, and confirms with user before pushing.
---

# /ocd-push

Push local commits to remote. Ensures working tree is committed first, previews unpushed commits, and confirms before pushing.

## Trigger

User runs `/ocd-push`

## Workflow

1. Check for uncommitted changes
  1. Run `git status --short`
  2. If changes exist:
    1. Run `/ocd-commit`
    2. If commit fails or produces no commits: EXIT — report failure
2. Check for unpushed commits
  1. Run `git log --oneline @{upstream}..HEAD`
  2. If no unpushed commits:
    1. EXIT — report "Nothing to push — local and remote are in sync"
3. Present push preview to user:
  - Branch name and remote
  - Commit count and list (oneline format)
4. Confirm with user — "Push N commits to origin/branch?"
  1. If user declines: EXIT — report "Push cancelled"
5. Push to remote: `git push`
6. Report result

### Report

- Commits pushed: count and branch
- Remote URL and status

## Rules

- Never force push
- Never push to main/master without explicit user confirmation naming the branch
- If upstream is not set, prompt user for remote and branch before pushing
- Commit step is fully automated via /ocd-commit — no double-confirmation on commit content
