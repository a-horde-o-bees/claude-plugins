# git pr cleanup

> Restore local base and tear down a merged head branch. Safe-by-default; idempotent.

## Variables

- `{head}` — `--head <name>`; defaults to the current branch.
- `{base}` — `--base <name>`; defaults to the repo's default branch.

## Rules

- **The PR's merged state is the authority, not git ancestry.** Squash and rebase merges leave the head's commits absent from base, so `git branch -d` wrongly reports "not merged." When the PR is `MERGED`, force-delete is safe — the work is in base under a new SHA.
- **Safe-by-default** — with no merged PR, refuse to delete a head that has commits not on base. Unmerged work is never silently dropped.
- **Idempotent** — a missing remote or local head branch is a no-op, not an error (merge may have used `--delete-branch`, or cleanup may rerun).
- Never force-push or run destructive git operations beyond the scoped branch deletion.

## Process

1. {head}: if `--head` given use it, else bash: `git branch --show-current`
2. {base}: if `--base` given use it, else bash: `git symbolic-ref --short refs/remotes/origin/HEAD | sed 's@^origin/@@'`
3. If {head} == {base}: Exit process — {head} is the base branch; nothing to clean up
4. Determine merged state:
    1. {pr-state}: bash: `gh pr view {head} --json state --jq .state 2>/dev/null` (capture exit; empty if no PR)
    2. {merged}: {pr-state} == `MERGED`

5. Safety gate (when not {merged}):
    1. bash: `git fetch origin {base} --quiet`
    2. {unmerged}: bash: `git rev-list origin/{base}..{head} --count`
    3. If {unmerged} > 0: Exit process — {head} has {unmerged} commit(s) not in {base} and no merged PR; refusing to delete. Merge or discard explicitly first.

6. Switch and sync base:
    1. {current}: bash: `git branch --show-current`
    2. If {current} == {head}: bash: `git checkout {base}`
    3. bash: `git pull --prune`

7. Delete remote head (if present):
    1. {remote-exists}: bash: `git ls-remote --exit-code --heads origin {head} >/dev/null 2>&1 && echo yes || echo no`
    2. If {remote-exists} is `yes`: bash: `git push origin --delete {head}`

8. Delete local head (if present):
    1. {local-exists}: bash: `git show-ref --verify --quiet refs/heads/{head} && echo yes || echo no`
    2. If {local-exists} is `yes`:
        1. If {merged}: bash: `git branch -D {head}` — PR-merged authority
        2. Else: bash: `git branch -d {head}` — safe delete (only reached when fully merged by ancestry)

## Report

Return to caller:

- Base: {base} restored (pulled + pruned)
- Remote head: deleted {head} | already gone
- Local head: deleted {head} | already gone | retained (unmerged — refused)
