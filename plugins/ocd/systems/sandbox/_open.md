# Open

Activate an existing `sandbox/<feature>` branch in a sibling worktree. If the worktree already exists, `open` just surfaces the path. If it does not, `open` creates the worktree, rebases the dev branch onto current `origin/main` inside it (so the feature starts from today's main), and hands back the path. Main tree is never checked out; rebase conflicts are resolved in the sibling.

### Variables

- {verb-arg} — positional value: feature id (the id used with `new` or `pack`)

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} is empty: Exit to user: open requires a feature id
    2. {feature-id} = {verb-arg}
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`

> Short-circuit — an already-created sibling worktree is the open state; `open` then reduces to emitting the path.

5. If {sibling-path} exists on disk:
    1. {status-json} = bash: `ocd-run sandbox worktree-status {sibling-name}`
    2. If {status-json}.branch ≠ {branch}: Exit to user: sibling at {sibling-path} exists on branch {status-json}.branch, expected {branch} — manual reconciliation required
    3. Return to caller:
        - already open
        - worktree: {sibling-path}
        - next: `cd {sibling-path} && claude`

> Preconditions — branch must exist locally or on origin.

6. Verify branch exists:
    1. bash: `git show-ref --verify --quiet refs/heads/{branch}`
    2. {local-exists} = exit 0
    3. If not {local-exists}:
        1. bash: `git fetch origin {branch} --quiet`
        2. bash: `git show-ref --verify --quiet refs/remotes/origin/{branch}`
        3. If exit non-zero: Exit to user: {branch} not found locally or on origin

> Create worktree — attach to the existing branch via worktree-add without base-ref.

7. Create sibling worktree on existing branch:
    1. bash: `ocd-run sandbox worktree-add {sibling-name} --branch {branch}`

> Rebase inside the sibling — brings the feature up to today's main. Conflicts belong to the user to resolve in the sibling, not on main.

8. Rebase onto current main:
    1. bash: `git -C {sibling-path} fetch origin main --quiet`
    2. bash: `git -C {sibling-path} rebase origin/main`
    3. If rebase fails:
        1. Exit to user:
            - rebase conflict on {branch} in {sibling-path}
            - resolve conflicts inside the sibling; then `git -C {sibling-path} rebase --continue`
            - or abort with `git -C {sibling-path} rebase --abort` and close the worktree

9. Return to caller:
    - opened: {branch}
    - worktree: {sibling-path}
    - rebased onto current origin/main
    - next: `cd {sibling-path} && claude`
