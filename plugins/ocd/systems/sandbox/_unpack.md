# Unpack

Integrate a `sandbox/<feature>` branch into main via a pull request, then delete the branch local + remote and remove the sibling worktree if present. The branch must already be rebased against current `origin/main` — unpack is mechanically dumb and does not itself reintegrate; run `/sandbox update {feature-id}` from the sibling's session first. Idempotent when the branch is already gone.

PR-based by default — `gh pr create` opens a PR, required status checks gate the merge, `gh pr merge --merge --delete-branch` lands it with a merge commit. The `--direct` flag bypasses the PR for emergency local-only merges.

### Variables

- {verb-arg} — positional value and flags: `<feature-id> [--direct]`

### Process

> Prerequisite — unpack is invoked only after `/sandbox update {feature-id}` has rebased the branch onto current `origin/main` inside the sibling's session. If the rebase is outstanding, unpack exits with guidance.

1. Parse {verb-arg}:
    1. If {verb-arg} is empty: Exit to user: unpack requires a feature id
    2. {direct} = `true` if `--direct` is present in {verb-arg}, else `false`
    3. {feature-id} = {verb-arg} with `--direct` removed
    4. If {feature-id} is empty: Exit to user: unpack requires a feature id
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
6. If {direct}: Call: Direct Merge
7. Else: Call: PR Merge

> Cleanup runs after either integration path completes.

8. Update local main: bash: `git pull origin main --ff-only`
9. If {local-exists}: bash: `git branch -d {branch}` — local branch may already be gone if it was already merged

> Close the sibling — worktree is no longer needed once the branch has been merged; sibling cleanup matches close's semantics (safe removal via `git worktree remove`, not `rm -rf`).

10. If {sibling-path} exists on disk: bash: `ocd-run sandbox worktree-remove {sibling-name}`

11. Return to caller:
    - unpacked: {feature-id}
    - integration path: PR (with PR number/URL) or direct merge
    - {branch} deleted local + remote
    - sibling removed if it existed

## PR Merge

> Open a pull request against main, wait for required status checks, merge with a merge commit, and let GitHub delete the remote branch. Required-check set is the repo's branch-protection configuration; `gh pr checks --watch --required` blocks until those checks complete. Conflicts at merge time mean origin/main advanced between the precondition check and the merge — resolution belongs on the branch via `/sandbox update {feature-id}`, not here.

1. Check for existing open PR: bash: `gh pr list --head {branch} --base main --state open --json number,url`
2. If a matching PR exists: {pr-number} = the returned number; {pr-url} = the returned url; skip to step 4
3. Else create a new PR:
    1. Draft PR title and body from the branch's commits — bash: `git log origin/main..{branch} --oneline --no-decorate` for a concise summary, `git log origin/main..{branch} --format='%B'` for full messages
    2. Title: concise end-state summary (same discipline as commit messages). If the branch has one commit, use its subject; otherwise synthesize a single line covering the branch's topic.
    3. Body: follow the project's PR template with `## Summary` (bullets covering what lands) and `## Test plan` (verification items). Do not include the commit co-author trailer — that belongs on commits, not PR bodies.
    4. bash: `gh pr create --base main --head {branch} --title "<drafted title>" --body "<drafted body>"` — pass body via HEREDOC for correct formatting
    5. {pr-url} = returned URL; {pr-number} = parse the number from the URL
4. Wait for required checks: bash: `gh pr checks {pr-number} --watch --required`
    1. If the command exits non-zero: Exit to user: required checks failed on {pr-url} — investigate and re-invoke after the branch is fixed
5. Merge the PR: bash: `gh pr merge {pr-number} --merge --delete-branch`
    1. `--merge` preserves the branch as a merge-commit sub-graph on main (matches the `--no-ff` semantics of the direct-merge path)
    2. `--delete-branch` removes the remote branch once merged
6. Return to caller: PR integration path, {pr-url}

## Direct Merge

> Emergency escape hatch — merge the branch directly on main without a PR. Skips CI gate, no reviewable artifact, no branch-protection compatibility. Only use when the PR flow is unavailable or the situation specifically demands it.

1. Update main: bash: `git pull origin main --ff-only`
    1. If pull fails: Exit to user: main cannot fast-forward — reconcile manually, then re-invoke unpack
2. Merge feature branch: bash: `git merge --no-ff {branch} -m "unpack {feature-id}"`
    1. If merge fails:
        1. Exit to user:
            - merge conflict unpacking {feature-id}
            - origin/main advanced between precondition check and merge
            - abort with `git merge --abort`, re-open the sandbox (`/sandbox open {feature-id}`), update (`/sandbox update {feature-id}` from the sibling), then retry unpack
3. Push main: bash: `git push origin main`
4. Delete remote branch: bash: `git push origin --delete {branch}`
5. Return to caller: direct merge integration path
