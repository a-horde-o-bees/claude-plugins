# Open

Rebase a boxed system's dev branch onto main and check it out for active work.

### Variables

- {verb-arg} — positional value after the verb, expected in `<plugin>:<system>` form

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} does not match `<plugin>:<system>`: Exit to user: open requires `<plugin>:<system>` form
    2. {plugin} = plugin part of {verb-arg}
    3. {system} = system part of {verb-arg}
2. {dev-branch} = `dev/{plugin}/{system}`

> Preconditions — open requires a clean working tree; the dev branch must exist locally or on origin.

3. Verify preconditions:
    1. bash: `git status --short`
    2. If output is non-empty: Exit to user: working tree has changes — commit or stash before opening
    3. bash: `git show-ref --verify --quiet refs/heads/{dev-branch}`
    4. If exit 0: {local-dev-exists} = true
    5. Else: {local-dev-exists} = false
    6. If not {local-dev-exists}:
        1. bash: `git fetch origin {dev-branch}`
        2. bash: `git show-ref --verify --quiet refs/remotes/origin/{dev-branch}`
        3. If exit non-zero: Exit to user: {dev-branch} not found locally or on origin

> Checkout — if the branch is only on origin, create a local tracking branch; otherwise switch to the existing local branch.

4. Check out dev branch:
    1. If {local-dev-exists}: bash: `git checkout {dev-branch}`
    2. Else: bash: `git checkout -b {dev-branch} origin/{dev-branch}`

> Rebase — bring the dev branch up to date with main. The dev branch's "restore" commit replays onto main's current tip. Conflicts here mean main removed or altered something the dev branch also changed; resolution is manual.

5. Rebase onto main:
    1. bash: `git fetch origin main`
    2. bash: `git rebase origin/main`
    3. If rebase fails:
        1. Exit to user:
            - rebase conflict on {dev-branch}
            - resolve conflicts, then run `git rebase --continue`
            - or abort with `git rebase --abort`

6. Return to caller:
    - opened: {plugin}:{system}
    - checked out {dev-branch}
    - rebased onto origin/main
