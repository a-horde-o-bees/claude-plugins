# Push

> Push local commits to remote. Requires explicit branch name — no default target. Ensures working tree is committed first, previews unpushed commits, then pushes.

### Variables

- {branch} — the branch name passed via `--branch <name>`

### Rules

- Never force push
- Explicit --branch is required — no default push target; naming the branch is the confirmation
- Branch mismatch exits with explanation — no prompt, no default action; user re-invokes with correct intent or asks for help
- Commit step is fully automated via the Commit sub-flow — no double-confirmation on commit content

### Process

1. If not {branch}: Exit to user: push requires `--branch <branch-name>`
2. {current-branch} = current git branch
3. If {current-branch} does not match {branch}:
    1. Exit to user:
        - branch mismatch — current branch is {current-branch}, requested {branch}
        - To push the current branch: re-invoke with `--branch {current-branch}`
        - To move commits to {branch} first: ask for help with rebase/merge
4. Check for uncommitted changes
    1. Run `git status --short`
    2. If changes exist:
        1. Call: `_commit.md`
        2. If commit fails or produces no commits: Exit to user: commit failed
5. {upstream-set} = bash: `git rev-parse --abbrev-ref @{upstream}` exits 0
6. If {upstream-set}:
    1. Run `git log --oneline @{upstream}..HEAD`
    2. If no unpushed commits: Exit to user: Nothing to push — local and remote are in sync
7. Present push preview — branch name, remote, commit count and list (oneline format)
8. Push to remote:
    1. If {upstream-set}: bash: `git push origin {branch}`
    2. Else: bash: `git push -u origin {branch}` — first push, set upstream
9. Return to caller:
    - Commits pushed: count and branch
    - Remote URL and status
