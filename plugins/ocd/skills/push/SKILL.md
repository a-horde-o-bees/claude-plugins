---
name: push
allowed-tools:
  - Skill
  - Bash(git *)
description: >
  Push commits to remote. Requires explicit --branch to name the push target.
  Runs /commit first if uncommitted changes exist, previews unpushed commits,
  then pushes.
argument-hint: "--branch <branch-name>"
---

# /push

Push local commits to remote. Requires explicit branch name — no default target. Ensures working tree is committed first, previews unpushed commits, then pushes.

## Trigger

User runs `/push`

## Route

1. If not --branch: Exit to user — respond with skill description and argument-hint
2. {current-branch} = current git branch
3. If {current-branch} does not match {branch}:
    1. Exit to user — report mismatch, explain options:
        - To push the current branch: re-invoke with `--branch {current-branch}`
        - To move commits to {branch} first: ask for help with rebase/merge
4. Push target is `origin/{branch}`

## Workflow

1. Check for uncommitted changes
    1. Run `git status --short`
    2. If changes exist:
        1. Run `/commit`
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
- Branch mismatch exits with explanation — no prompt, no default action; user re-invokes with correct intent or asks for help
- If upstream is not set, use the provided --branch to set it with `git push -u origin {branch}`
- Commit step is fully automated via /commit — no double-confirmation on commit content
