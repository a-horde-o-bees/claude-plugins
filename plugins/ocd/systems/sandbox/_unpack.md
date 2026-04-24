# Unpack

Merge a `sandbox/<feature>` branch into main, remove the sibling worktree, and delete the branch local + remote. The branch must already be rebased against current `origin/main` — unpack is mechanically dumb and does not itself reintegrate; run `/sandbox update {feature-id}` from the sibling's session first. Idempotent when the branch is already gone.

### Variables

- {verb-arg} — positional value: feature id

### Process

> Prerequisite — unpack is invoked only after `/sandbox update {feature-id}` has rebased the branch onto current `origin/main` inside the sibling's session. If the rebase is outstanding, unpack exits with guidance.

1. Parse {verb-arg}:
    1. If {verb-arg} is empty: Exit to user: unpack requires a feature id
    2. {feature-id} = {verb-arg}
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`

> Preconditions — main must be clean; branch must exist somewhere and be rebased onto current `origin/main`.

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
    10. If not {local-exists} and not {remote-exists}:
        1. Return to caller:
            - already unpacked
            - {branch} not present locally or on origin
    11. If not {local-exists}: bash: `git branch --track {branch} origin/{branch}`
    12. bash: `git merge-base --is-ancestor origin/main {branch}`
    13. If exit non-zero: Exit to user:
        - {branch} is not on top of current origin/main
        - switch to the sibling's session (`cd {sibling-path} && claude`) and run `/sandbox update {feature-id}`
        - then re-invoke `/sandbox unpack {feature-id}` from main
    14. If {sibling-path} exists on disk:
        1. {status-json} = bash: `ocd-run sandbox worktree-status {sibling-name}`
        2. If not {status-json}.clean: Exit to user: uncommitted changes in sibling {sibling-path} — commit or discard before unpacking
        3. If not {status-json}.pushed: Exit to user: {branch} is ahead of origin in sibling — push before unpacking

> Fast-forward main — a non-ff state means someone else moved main forward; reconcile manually before merging.

6. Update main:
    1. bash: `git pull origin main --ff-only`
    2. If pull fails: Exit to user: main cannot fast-forward — reconcile manually, then re-invoke unpack

> Close the sibling before the merge — worktree is no longer needed once the branch is rebased and pushed; sibling cleanup matches close's semantics (safe removal via `git worktree remove`, not `rm -rf`).

7. Remove sibling worktree if present:
    1. If {sibling-path} exists on disk: bash: `ocd-run sandbox worktree-remove {sibling-name}`

> Merge — `--no-ff` preserves the feature branch's history as a distinct topic. Conflicts at this point mean origin/main advanced between the precondition check and the merge; resolution belongs on the branch, not here.

8. Merge feature branch:
    1. bash: `git merge --no-ff {branch} -m "unpack {feature-id}"`
    2. If merge fails:
        1. Exit to user:
            - merge conflict unpacking {feature-id}
            - origin/main advanced between precondition check and merge
            - abort with `git merge --abort`, re-open the sandbox (`/sandbox open {feature-id}`), update (`/sandbox update {feature-id}` from the sibling), then retry unpack

> Publish and delete the branch.

9. Push main:
    1. bash: `git push origin main`

10. Delete branch:
    1. bash: `git branch -d {branch}`
    2. bash: `git push origin --delete {branch}`

11. Return to caller:
    - unpacked: {feature-id}
    - merged into main with `--no-ff`
    - {branch} deleted local + remote
    - sibling removed if it existed
