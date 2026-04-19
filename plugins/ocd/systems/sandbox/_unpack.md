# Unpack

Merge a `sandbox/<feature>` branch that has already been reintegrated and verified back into main, then delete the branch local + remote and remove the sibling worktree if present. Mechanical — all integration judgment happens on the dev branch while open; unpack is the final no-op once the branch is confirmed ready.

### Variables

- {verb-arg} — positional value: feature id

### Process

> Prerequisite — unpack is invoked only after the feature branch has been reintegrated against current main and verified on its sibling. If that work has not happened, unpack is premature — open the sandbox and reintegrate first.

1. Parse {verb-arg}:
    1. If {verb-arg} is empty: Exit to user: unpack requires a feature id
    2. {feature-id} = {verb-arg}
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`

> Preconditions — main must be clean and fast-forwardable; branch must exist.

5. Verify preconditions:
    1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
    2. If {current-branch} is not `main`: Exit to user: unpack runs from main; currently on {current-branch}
    3. bash: `git status --short` — must be empty
    4. If output non-empty: Exit to user: working tree has changes — commit or stash before unpacking
    5. bash: `git fetch origin --quiet`
    6. bash: `git show-ref --verify --quiet refs/heads/{branch}`
    7. {local-exists} = exit 0
    8. bash: `git show-ref --verify --quiet refs/remotes/origin/{branch}`
    9. {remote-exists} = exit 0
    10. If not {local-exists} and not {remote-exists}: Exit to user: {branch} not found locally or on origin
    11. If not {local-exists}: bash: `git branch --track {branch} origin/{branch}`
    12. If {sibling-path} exists on disk:
        1. {status-json} = bash: `ocd-run sandbox worktree-status {sibling-name}`
        2. If not {status-json}.clean: Exit to user: uncommitted changes in sibling {sibling-path} — commit or discard before unpacking
        3. If not {status-json}.pushed: Exit to user: {branch} is ahead of origin in sibling — push before unpacking

> Fast-forward main — a non-ff state means someone else moved main forward; reconcile manually before merging.

6. Update main:
    1. bash: `git pull origin main --ff-only`
    2. If pull fails: Exit to user: main cannot fast-forward — reconcile manually, then re-invoke unpack

> Merge — `--no-ff` preserves the feature branch's history as a distinct topic. Conflicts indicate the branch was not reintegrated against current main; resolution belongs on the branch, not here.

7. Merge feature branch:
    1. bash: `git merge --no-ff {branch} -m "unpack {feature-id}"`
    2. If merge fails:
        1. Exit to user:
            - merge conflict unpacking {feature-id}
            - branch was not reintegrated against current main — open the sandbox, rebase, resolve, close, then retry unpack
            - abort with `git merge --abort` if needed

> Publish and clean up.

8. Push main:
    1. bash: `git push origin main`

9. Remove sibling worktree (if present) and branch:
    1. If {sibling-path} exists on disk: bash: `ocd-run sandbox worktree-remove {sibling-name}`
    2. bash: `git branch -d {branch}`
    3. bash: `git push origin --delete {branch}`

10. Return to caller:
    - unpacked: {feature-id}
    - merged into main with `--no-ff`
    - {branch} deleted local + remote
    - sibling removed if it existed
