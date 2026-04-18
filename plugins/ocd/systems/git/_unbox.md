# Unbox

Merge a boxed system's dev branch back into main, then delete the dev branch locally and on origin. Ends the system's in-flight status.

### Variables

- {verb-arg} — positional value after the verb, expected in `<plugin>:<system>` form

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} does not match `<plugin>:<system>`: Exit to user: unbox requires `<plugin>:<system>` form
    2. {plugin} = plugin part of {verb-arg}
    3. {system} = system part of {verb-arg}
2. {dev-branch} = `dev/{plugin}/{system}`

> Preconditions — unbox brings the system back to main in one merge; require clean state and confirmed dev branch existence.

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

> Merge — `--no-ff` preserves the dev branch's history as a distinct topic even if main had no interleaving commits. Conflicts here reflect genuine divergence; resolution is manual.

5. Merge dev branch:
    1. bash: `git merge --no-ff {dev-branch} -m "unbox {plugin}:{system}"`
    2. If merge fails:
        1. Exit to user:
            - merge conflict unboxing {plugin}:{system}
            - resolve conflicts and commit; dev branch remains for retry
            - abort with `git merge --abort` if needed

6. Push and delete:
    1. bash: `git push origin main`
    2. bash: `git branch -d {dev-branch}`
    3. bash: `git push origin --delete {dev-branch}`

> Reintegration checklist — surface only external references cut on box. The system's own directory is excluded since the merge restored it; including it here is noise that looks alarming (e.g., "SKILL.md: 12 deletions") even though nothing was lost. Full diff (not just --stat) so the user can decide per-file without running `git show` themselves.

7. Emit reintegration checklist:
    1. {box-commit} = bash: `git log --grep="^box {plugin}:{system}$" -n 1 --format=%H`
    2. If {box-commit} is empty: Exit to user: unboxed — box commit not found in history, no reintegration checklist
    3. {system-path} = `plugins/{plugin}/systems/{system}`
    4. {changed-files} = bash: `git diff-tree --no-commit-id --name-only -r {box-commit}`
    5. {external-files} = {changed-files} with entries under {system-path} filtered out
    6. If {external-files} is empty:
        1. Present to user: "Unboxed {plugin}:{system}. No external references were cut on box — nothing to reintegrate."
    7. Else:
        1. {stat} = bash: `git show {box-commit} --stat -- {external-files}`
        2. {patch} = bash: `git show {box-commit} --patch -- {external-files}`
        3. Present to user:
            - unboxed: {plugin}:{system}
            - external references cut on box — review each and decide whether to restore in the current design:
            - {stat}
            - full diff:
            - {patch}

8. Return to caller:
    - unboxed: {plugin}:{system}
    - merged into main with `--no-ff`
    - {dev-branch} deleted local + remote
    - external tendrils in checklist: count (0 means nothing to reintegrate)
