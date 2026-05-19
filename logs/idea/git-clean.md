# /git-clean skill seed — cleanup + problem analysis

A future skill for git plugin: cleanup operations and post-mortem problem analysis when the normal verbs (`/git-commit`, `/git-push`, `/git-ci`, `/git-release`) hit a wall.

## Seed

Anthropic's `/clean_gone` (in `commit-commands` plugin) deletes local branches whose remote is gone. Useful but narrow. The broader cognitive moment is "the working state has accumulated cruft or hit a confusing failure, and I want git to surface what's actually going on or sweep it clean."

## Candidate scope

**Cleanup operations:**

- Delete local branches whose remote tracking is gone (`git-clean-gone` style)
- Prune orphan tags (local-only, no remote)
- Surface dangling refs / unreachable commits
- Detect large files in history (suggest filter-repo / BFG when appropriate)
- Clear stale `git stash` entries

**Problem analysis:**

- "Why is this push being rejected?" — diagnose non-fast-forward, branch protection, missing upstream, force-push refusal
- "Why is this merge failing?" — surface conflict files with the conflict lines highlighted
- "Why is CI not triggering?" — check the path filters in workflows against the diff
- "What's the state of my checkout?" — detached HEAD, mid-rebase, mid-cherry-pick, merge conflict pending

## Scope rule for the eventual skill

Operations are diagnostic-first: surface what's wrong + the safe option to fix, never auto-destroy. Destructive verbs (delete branch, prune tag, remove stash) gate on explicit user approval.

## Related

- `plugins/git/skills/git-push/SKILL.md` — push refuses from detached HEAD; that's a guard, not analysis. A `/git-clean diagnose` would explain *why* HEAD is detached and the recovery options.
- `plugins/git/skills/git-ci/SKILL.md` — surfaces CI status; doesn't diagnose why a workflow didn't trigger. Belongs in `/git-clean` if added.
- Anthropic `commit-commands` plugin's `/clean_gone` — the narrow seed.
