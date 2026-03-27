---
name: ocd-push
description: >
  Push commits to remote. Runs /ocd-commit first if uncommitted changes exist,
  previews unpushed commits, then pushes.
---

# /ocd-push

Push local commits to remote. Ensures working tree is committed first, previews unpushed commits, then pushes. Invoking the skill is the push confirmation.

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
3. Present push preview — branch name, remote, commit count and list (oneline format)
4. Push to remote: `git push`
5. Report result

### Report

- Commits pushed: count and branch
- Remote URL and status

## Rules

- Never force push
- If upstream is not set, prompt user for remote and branch before pushing
- Invoking /ocd-push is sufficient confirmation to push — no additional user gate
- Commit step is fully automated via /ocd-commit — no double-confirmation on commit content
