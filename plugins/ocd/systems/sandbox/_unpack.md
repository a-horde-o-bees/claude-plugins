# Unpack

Integrate a `sandbox/<feature>` branch into main via a pull request, then delete the branch local + remote and remove the sibling worktree if present. The branch must already be rebased against current `origin/main` — unpack is mechanically dumb and does not itself reintegrate; run `/sandbox update {feature-id}` first. Idempotent when the branch is already gone.

`gh pr create` opens a PR, required status checks gate the merge, `gh pr merge --merge --delete-branch` lands it with a merge commit. All git operations target explicit paths via `git -C`, so unpack runs from main or from any sibling worktree.

### Variables

- {verb-arg} — positional value: `<feature-id>`. If empty, infer from cwd's branch (must be `sandbox/<id>`).

### Process

> Prerequisite — unpack is invoked only after `/sandbox update {feature-id}` has rebased the branch onto current `origin/main`. If the rebase is outstanding, unpack exits with guidance.

1. Parse {verb-arg}:
    1. If {verb-arg} non-empty: {feature-id} = {verb-arg}
    2. Else:
        1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
        2. If {current-branch} does not start with `sandbox/`: Exit to user: unpack requires a feature id (or run from inside a `sandbox/<id>` worktree)
        3. {feature-id} = {current-branch} with `sandbox/` prefix removed
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {branch} = `sandbox/{feature-id}`
4. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`
5. {main-path} = bash: `dirname "$(git rev-parse --path-format=absolute --git-common-dir)"` — main worktree, resolved via the shared `.git` so it works from any cwd

> Preconditions — main must be clean; branch must exist somewhere and be rebased onto current `origin/main`. All git inspections target {main-path} explicitly so the verb is invariant of cwd.

6. Verify preconditions:
    1. bash: `git -C {main-path} status --short` — must be empty
    2. If output non-empty: Exit to user: main worktree at {main-path} has changes — commit or stash before unpacking
    3. bash: `git -C {main-path} fetch origin --quiet`
    4. bash: `git -C {main-path} show-ref --verify --quiet refs/heads/{branch}`
    5. {local-exists} = exit 0
    6. bash: `git -C {main-path} show-ref --verify --quiet refs/remotes/origin/{branch}`
    7. {remote-exists} = exit 0
    8. If not {local-exists} and not {remote-exists}:
        1. Return to caller:
            - already unpacked
            - {branch} not present locally or on origin
    9. If not {local-exists}: bash: `git -C {main-path} branch --track {branch} origin/{branch}`
    10. bash: `git -C {main-path} merge-base --is-ancestor origin/main {branch}`
    11. If exit non-zero: Exit to user:
        - {branch} is not on top of current origin/main
        - run `/sandbox update {feature-id}` to rebase, then re-invoke `/sandbox unpack {feature-id}`
    12. If {sibling-path} exists on disk:
        1. {status-json} = bash: `ocd-run sandbox worktree-status {sibling-name}`
        2. If not {status-json}.clean: Exit to user: uncommitted changes in sibling {sibling-path} — commit or discard before unpacking
        3. If not {status-json}.pushed: Exit to user: {branch} is ahead of origin in sibling — push before unpacking

> Open a pull request against main, wait for required status checks, merge with a merge commit, and let GitHub delete the remote branch. Required-check set is the repo's branch-protection configuration; `gh pr checks --watch --required` blocks until those checks complete. Conflicts at merge time mean origin/main advanced between the precondition check and the merge — resolution belongs on the branch via `/sandbox update {feature-id}`, not here.

7. Check for existing open PR: bash: `gh -R "$(git -C {main-path} config --get remote.origin.url)" pr list --head {branch} --base main --state open --json number,url`
8. If a matching PR exists: {pr-number} = the returned number; {pr-url} = the returned url; skip to step 10
9. Else create a new PR:
    1. Draft PR title and body from the branch's commits — bash: `git -C {main-path} log origin/main..{branch} --oneline --no-decorate` for a concise summary, `git -C {main-path} log origin/main..{branch} --format='%B'` for full messages
    2. Title: concise end-state summary (same discipline as commit messages). If the branch has one commit, use its subject; otherwise synthesize a single line covering the branch's topic.
    3. Body: follow the project's PR template with `## Summary` (bullets covering what lands) and `## Test plan` (verification items). Do not include the commit co-author trailer — that belongs on commits, not PR bodies.
    4. bash: `gh -R "$(git -C {main-path} config --get remote.origin.url)" pr create --base main --head {branch} --title "<drafted title>" --body "<drafted body>"` — pass body via HEREDOC for correct formatting
    5. {pr-url} = returned URL; {pr-number} = parse the number from the URL
10. Wait for required checks: bash: `gh -R "$(git -C {main-path} config --get remote.origin.url)" pr checks {pr-number} --watch --required`
    1. If the command exits non-zero: Exit to user: required checks failed on {pr-url} — investigate and re-invoke after the branch is fixed
11. Merge the PR: bash: `gh -R "$(git -C {main-path} config --get remote.origin.url)" pr merge {pr-number} --merge --delete-branch`
    1. `--merge` preserves the branch as a merge-commit sub-graph on main
    2. `--delete-branch` removes the remote branch once merged

> Cleanup runs after the merge.

12. Update local main: bash: `git -C {main-path} pull origin main --ff-only`
13. If {local-exists}: bash: `git -C {main-path} branch -d {branch}` — local branch may already be gone if it was already merged

> Close the sibling — worktree is no longer needed once the branch has been merged; sibling cleanup matches close's semantics (safe removal via `git worktree remove`, not `rm -rf`).

14. If {sibling-path} exists on disk: bash: `ocd-run sandbox worktree-remove {sibling-name}`

15. Return to caller:
    - unpacked: {feature-id}
    - PR: {pr-url}
    - {branch} deleted local + remote
    - sibling removed if it existed
