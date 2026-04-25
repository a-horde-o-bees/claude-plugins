# Close

Park a feature sandbox — remove the sibling worktree via `git worktree remove`, preserving the `sandbox/<feature>` branch on origin. The feature can be re-activated later with `open`. Close refuses to proceed with uncommitted or unpushed work in the sibling (protects against lost work); idempotent when the sibling is already absent.

### Variables

- {verb-arg} — positional value: feature id. If empty, infer from cwd's branch (must be `sandbox/<id>`).

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} non-empty: {feature-id} = {verb-arg}
    2. Else:
        1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
        2. If {current-branch} does not start with `sandbox/`: Exit to user: close requires a feature id (or run from inside a `sandbox/<id>` worktree)
        3. {feature-id} = {current-branch} with `sandbox/` prefix removed
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`

> Idempotent early-out — a missing sibling means close's end-state is already achieved.

5. If {sibling-path} does not exist on disk:
    1. Return to caller:
        - already closed
        - branch persists on local and origin; re-activate with `/sandbox open {feature-id}`

> Preconditions — sibling must be on the expected branch, clean, and pushed; these are the safety gates that earn the `--force` on worktree-remove.

6. Verify preconditions:
    1. {status-json} = bash: `ocd-run sandbox worktree-status {sibling-name}`
    2. If {status-json}.branch ≠ {branch}: Exit to user: sibling is on {status-json}.branch, expected {branch}
    3. If not {status-json}.clean: Exit to user: uncommitted changes in {sibling-path} — commit or stash before closing
    4. If not {status-json}.pushed: Exit to user: {branch} is ahead of origin — push before closing (`git -C {sibling-path} push origin {branch}`)

> Remove the sibling worktree. Keep the branch — close is reversible via `open`.

7. Remove sibling worktree:
    1. bash: `ocd-run sandbox worktree-remove {sibling-name}`

8. Return to caller:
    - closed: {branch}
    - branch persists on local and origin; re-activate with `/sandbox open {feature-id}`
