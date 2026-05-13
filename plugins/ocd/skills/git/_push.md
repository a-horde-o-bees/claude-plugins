# Push

> Push local commits to a named remote branch. Requires explicit `--branch`; commits any uncommitted changes via `_commit.md` first.

### Variables

- {branch} — the branch name passed via `--branch <name>`

### Rules

- Explicit `--branch` required; naming the branch is the confirmation
- Branch mismatch exits with explanation — no prompt, no default action
- Commit step is fully automated via `_commit.md` — no double-confirmation on commit content
- Never force-push

### Process

1. If not {branch}: Exit to user: push requires `--branch <branch-name>`

2. {current-branch}: bash: `git rev-parse --abbrev-ref HEAD`

3. If {current-branch} ≠ {branch}: Exit to user:
    - branch mismatch — current is {current-branch}, requested {branch}
    - To push the current branch: re-invoke with `--branch {current-branch}`
    - To move commits to {branch} first: ask for help with rebase/merge

4. Check for uncommitted changes:
    1. {pending}: bash: `git status --short`
    2. If {pending} non-empty:
        1. Call: `_commit.md`
        2. If commit produces no commits: Exit to user: commit failed — investigate and re-invoke

5. {upstream-set}: bash: `git rev-parse --abbrev-ref @{upstream} 2>/dev/null` exits 0

6. If {upstream-set}:
    1. {unpushed}: bash: `git log --oneline @{upstream}..HEAD`
    2. If {unpushed} is empty: Exit to user: nothing to push — local and remote in sync

7. Present push preview — branch, remote, commit count + oneline list

8. Push:
    1. If {upstream-set}: bash: `git push origin {branch}`
    2. Else: bash: `git push -u origin {branch}` — first push, sets upstream

### Report

Return to caller:

- Commits pushed: count and branch
- Remote URL and push status
