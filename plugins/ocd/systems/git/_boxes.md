# Boxes

List all boxed plugin systems across local and remote, showing state and last-commit info.

### Process

1. bash: `git fetch origin --prune`

> Enumerate — collect `dev/*` branches from both local refs and origin; dedupe by short name.

2. Gather dev branches:
    1. {local-dev} = bash: `git for-each-ref --format='%(refname:short)' refs/heads/dev/`
    2. {remote-dev} = bash: `git for-each-ref --format='%(refname:short)' refs/remotes/origin/dev/`
    3. Strip `origin/` prefix from {remote-dev} entries
    4. {branches} = union of {local-dev} and stripped {remote-dev}, deduplicated

3. If {branches} is empty: Exit to user: no boxed systems

4. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`

> Per-branch detail — prefer local ref for last-commit info when available; otherwise query the remote-tracking ref. State is `open` when the branch is currently checked out, otherwise `closed`.

5. For each {branch} in {branches}:
    1. Parse {branch} as `dev/{plugin}/{system}`; if parse fails, skip
    2. {local-present} = branch is in {local-dev}
    3. {remote-present} = branch is in stripped {remote-dev}
    4. {ref} = `{branch}` if {local-present} else `origin/{branch}`
    5. {last-commit} = bash: `git log -1 --format='%h %ci %s' {ref}`
    6. {location} = `local+remote` if both present, `local-only` if only local, `remote-only` if only remote
    7. {state} = `open` if {branch} == {current-branch}, else `closed`

6. Present table:
    - Columns: Plugin | System | State | Location | Last Commit
    - One row per parsed branch

7. Return to caller
