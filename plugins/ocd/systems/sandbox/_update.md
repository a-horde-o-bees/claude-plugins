# Update

Rebase an open feature sandbox onto current `origin/main` and force-push. All git operations target the named sibling via `git -C <sibling-path>`, so the verb runs correctly from main or from any sibling worktree. If rebase conflicts arise, the user is directed to `cd` into the sibling for governance-correct resolution. Idempotent: if the branch is already on top of `origin/main` and in sync with origin, update is a silent no-op.

### Variables

- {verb-arg} — positional value: feature id. If empty, infer from cwd's branch (must be `sandbox/<id>`).

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} non-empty: {feature-id} = {verb-arg}
    2. Else:
        1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
        2. If {current-branch} does not start with `sandbox/`: Exit to user: update requires a feature id (or run from inside a `sandbox/<id>` worktree)
        3. {feature-id} = {current-branch} with `sandbox/` prefix removed
2. {sibling-name} = {feature-id} with every `/` replaced by `-` — filesystem-safe flat form
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`

> Preconditions — sibling must exist on the expected branch, with no rebase already in progress and no uncommitted changes. Rebase conflicts must halt for human resolution; update refuses to start when prior interrupted state exists.

5. Verify preconditions:
    1. If {sibling-path} does not exist on disk: Exit to user: no sibling worktree at {sibling-path} — run `/sandbox open {feature-id}` first
    2. {status-json} = bash: `ocd-run sandbox worktree-status {sibling-name}`
    3. If {status-json}.branch ≠ {branch}: Exit to user: sibling is on {status-json}.branch, expected {branch} — manual reconciliation required
    4. bash: `git -C {sibling-path} rev-parse --git-path rebase-merge`
    5. bash: `git -C {sibling-path} rev-parse --git-path rebase-apply`
    6. If either directory exists: Exit to user: rebase already in progress in {sibling-path} — resolve with `git -C {sibling-path} rebase --continue` or `git -C {sibling-path} rebase --abort`, then re-invoke
    7. If not {status-json}.clean: Exit to user: uncommitted changes in {sibling-path} — commit or stash before updating

> Fetch — bring `origin/main` up to date so the ancestor check and rebase target are current.

6. bash: `git -C {sibling-path} fetch origin main --quiet`

> Idempotent early-out — skip rebase when the branch already contains `origin/main`'s tip. Push still runs in case a prior invocation failed before pushing.

7. bash: `git -C {sibling-path} merge-base --is-ancestor origin/main HEAD`
    1. {already-rebased} = exit 0
8. If not {already-rebased}:
    1. Rebase onto current `origin/main`:
        1. bash: `git -C {sibling-path} rebase origin/main`
        2. If rebase fails:
            1. Exit to user:
                - rebase conflict on {branch} in {sibling-path}
                - `cd {sibling-path}` and start a session there so governance files (rules, conventions) match the feature's deployed state, then resolve conflicts and `git rebase --continue`
                - or abort with `git -C {sibling-path} rebase --abort`
                - re-invoke `/sandbox update {feature-id}` when resolved

> Publish — if the remote branch does not yet exist, initial push with upstream tracking; otherwise force-with-lease, which rejects the push if someone else advanced origin since last fetch.

9. Check remote state:
    1. bash: `git -C {sibling-path} ls-remote --exit-code --heads origin {branch}`
    2. {remote-exists} = exit 0
10. Push:
    1. If not {remote-exists}: bash: `git -C {sibling-path} push -u origin {branch}`
    2. Else: bash: `git -C {sibling-path} push --force-with-lease origin {branch}`

11. Return to caller:
    - updated: {branch}
    - rebased onto: origin/main (or already on top — reported from {already-rebased})
    - pushed to origin
