# Open

Activate an existing `sandbox/<feature>` branch in a sibling worktree. Pure create-if-missing — no rebase. If the worktree already exists on the expected branch, open is a silent no-op. Sync the branch with current `origin/main` by running `/sandbox update {feature-id}` from the sibling's session after open.

### Variables

- {verb-arg} — positional value: feature id (the id used with `new` or `pack`)

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} is empty: Exit to user: open requires a feature id
    2. {feature-id} = {verb-arg}
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`

> Idempotent early-out — an already-present sibling on the expected branch is the open state. Wrong-branch collision still exits; that requires human judgment.

5. If {sibling-path} exists on disk:
    1. {status-json} = bash: `ocd-run sandbox worktree-status {sibling-name}`
    2. If {status-json}.branch ≠ {branch}: Exit to user: sibling at {sibling-path} exists on branch {status-json}.branch, expected {branch} — manual reconciliation required
    3. Return to caller:
        - already open
        - worktree: {sibling-path}
        - next: `cd {sibling-path} && claude`; run `/sandbox update {feature-id}` from that session to sync with origin/main

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

8. Return to caller:
    - opened: {branch}
    - worktree: {sibling-path}
    - next: `cd {sibling-path} && claude`; run `/sandbox update {feature-id}` from that session to sync with origin/main
