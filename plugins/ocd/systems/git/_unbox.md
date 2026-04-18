# Unbox

Merge a dev branch that has already been reintegrated and verified back into main, then delete the branch. Mechanical — all integration judgment happens on the dev branch while open; unbox is the final no-op once the user has confirmed the branch works.

### Variables

- {verb-arg} — positional value after the verb, expected in `<plugin>:<system>` form

### Process

> Prerequisite — unbox is invoked only after the user has reintegrated the feature against current conventions and documentation on the dev branch (in open state), closed it to push, and verified the dev branch works. If that work hasn't happened, unbox is premature and the user should open the box first.

1. Parse {verb-arg}:
    1. If {verb-arg} does not match `<plugin>:<system>`: Exit to user: unbox requires `<plugin>:<system>` form
    2. {plugin} = plugin part of {verb-arg}
    3. {system} = system part of {verb-arg}
2. {dev-branch} = `dev/{plugin}/{system}`

> Preconditions — require clean state and confirmed dev branch existence.

3. Verify preconditions:
    1. bash: `git status --short`
    2. If output is non-empty: Exit to user: working tree has changes — commit or stash before unboxing
    3. bash: `git fetch origin`
    4. bash: `git show-ref --verify --quiet refs/heads/{dev-branch}`
    5. {local-dev-exists} = exit 0 from previous step
    6. bash: `git show-ref --verify --quiet refs/remotes/origin/{dev-branch}`
    7. {remote-dev-exists} = exit 0 from previous step
    8. If not {local-dev-exists} and not {remote-dev-exists}: Exit to user: {dev-branch} not found locally or on origin
    9. If not {local-dev-exists}: bash: `git checkout -b {dev-branch} origin/{dev-branch}`

> Main checkout and fast-forward — unbox assumes main can be advanced cleanly; a non-ff state means someone else moved main forward, which should be reconciled manually before merging.

4. Switch to main and update:
    1. bash: `git checkout main`
    2. bash: `git pull origin main --ff-only`
    3. If pull fails: Exit to user: main cannot fast-forward — reconcile manually, then re-invoke unbox

> Merge — `--no-ff` preserves the dev branch's history as a distinct topic even if main had no interleaving commits. Conflicts here indicate the dev branch wasn't reintegrated against latest main before unbox; resolution is manual.

5. Merge dev branch:
    1. bash: `git merge --no-ff {dev-branch} -m "unbox {plugin}:{system}"`
    2. If merge fails:
        1. Exit to user:
            - merge conflict unboxing {plugin}:{system}
            - dev branch hasn't been reintegrated against current main — open the box, rebase, resolve conflicts, close, then retry unbox
            - abort with `git merge --abort` if needed

6. Push and delete:
    1. bash: `git push origin main`
    2. bash: `git branch -d {dev-branch}`
    3. bash: `git push origin --delete {dev-branch}`

7. Return to caller:
    - unboxed: {plugin}:{system}
    - merged into main with `--no-ff`
    - {dev-branch} deleted local + remote
