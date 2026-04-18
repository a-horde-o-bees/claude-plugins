# Close

Pause work on an open system by switching back to main. The dev branch persists with any commits made while it was open.

### Process

> Close is derived from current state — no argument. The skill closes whatever dev branch is currently checked out.

1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
2. If {current-branch} does not start with `dev/`: Exit to user: close requires checkout on a `dev/*` branch; currently on {current-branch}
3. Parse {current-branch} as `dev/{plugin}/{system}`:
    1. {plugin} = first path segment after `dev/`
    2. {system} = remainder after `dev/{plugin}/`

> Preconditions — refuse to close with uncommitted work, since `git checkout main` would either move the changes or reject the switch depending on overlap. Forcing a commit first keeps the dev branch's state authoritative.

4. Verify preconditions:
    1. bash: `git status --short`
    2. If output is non-empty: Exit to user: commit changes on {current-branch} before closing

5. Switch to main:
    1. bash: `git checkout main`

6. Return to caller:
    - closed: {plugin}:{system}
    - {current-branch} persists with its commits
    - on {plugin}:{system} again: run `/ocd:git open {plugin}:{system}`
