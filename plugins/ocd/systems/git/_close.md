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

> Push — close persists the session's work to origin so the user can walk away cleanly. Rebase during `open` rewrites history, so a plain push is rejected once the branch has been rebased. `--force-with-lease` is the safe form: it rewrites origin to match local only when origin matches the local ref of the remote-tracking branch, refusing if someone else moved origin independently.

5. Push dev branch to origin:
    1. bash: `git push --force-with-lease origin {current-branch}`
    2. If push fails: Exit to user: push of {current-branch} failed — origin advanced independently; resolve manually before closing

6. Switch to main:
    1. bash: `git checkout main`

7. Return to caller:
    - closed: {plugin}:{system}
    - {current-branch} pushed to origin
    - {current-branch} persists with its commits
    - on {plugin}:{system} again: run `/ocd:git open {plugin}:{system}`
