# List

Enumerate every sandbox state — durable feature boxes (`sandbox/<feature>`) and ephemeral disposables (`sandbox/tmp/<topic>`) — side by side with their worktree presence, cleanliness, and push status. Unified surface for "what sandboxes exist right now."

### Process

1. bash: `git fetch origin --prune --quiet`

> Enumerate sandbox branches — both durable and ephemeral live under `sandbox/`. Ephemeral is distinguished by the `tmp/` sub-namespace.

2. Gather branches:
    1. {local-branches} = bash: `git for-each-ref --format='%(refname:short)' refs/heads/sandbox/`
    2. {remote-branches} = bash: `git for-each-ref --format='%(refname:short)' refs/remotes/origin/sandbox/`
    3. Strip `origin/` prefix from {remote-branches} entries
    4. {branches} = union of {local-branches} and stripped {remote-branches}, deduplicated

3. If {branches} is empty: Exit to user: no sandboxes

> Worktree status — get active-worktree metadata once, then join each branch against the map.

4. {worktrees-json} = bash: `ocd-run sandbox worktree-list`
5. Parse {worktrees-json} into a map of branch → {path, clean, pushed, ahead_of_main}

> Per-branch detail — classify each branch as durable or ephemeral and determine open/closed state.

6. For each {branch} in {branches}:
    1. If {branch} starts with `sandbox/tmp/`:
        1. {kind} = ephemeral
        2. {feature-id} = branch with `sandbox/tmp/` prefix stripped
    2. Else:
        1. {kind} = durable
        2. {feature-id} = branch with `sandbox/` prefix stripped
    3. {worktree-entry} = {worktrees-json} map lookup for {branch}
    4. {state} = `open` if {worktree-entry} present, else `closed`
    5. {dirty-flag} = `dirty` if {worktree-entry} and {worktree-entry}.clean is false, else empty
    6. {unpushed-flag} = `ahead` if {worktree-entry} and {worktree-entry}.pushed is false, else empty
    7. {last-commit} = bash: `git log -1 --format='%h %ci %s' {branch}` (fallback to `origin/{branch}` if local absent)

7. Present two tables grouped by {kind}:
    - **Durable** — Feature | State | Flags | Last Commit
    - **Ephemeral** — Topic | State | Flags | Last Commit
    - State is `open` or `closed`; flags concatenate any of `dirty`, `ahead`
    - Omit a table header when its row set is empty

8. Return to caller
