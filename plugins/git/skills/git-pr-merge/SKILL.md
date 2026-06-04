---
name: git-pr-merge
description: Use when an open PR is ready to land — "merge the PR", "merge this", "land it", "ship the PR", or the merge step of a checkpoint. Composes /git-pr-status for the merge gate, then merges per the detected path — solo (immediate once CI is green) or team (required approvals + green CI). Hard blockers (red or pending CI, merge conflicts, behind base) are never bypassed; soft blockers (review not approved, CI annotations) are confirmable-bypass on the solo path or admin-override on a protected base. Strategy is project `pr.md` ∩ repo-allowed. `--cleanup` chains /git-pr-cleanup.
argument-hint: "[--strategy squash|merge|rebase] [--cleanup]"
allowed-tools:
  - Bash(git *)
  - Bash(gh *)
  - Read
  - Skill
  - AskUserQuestion
---

# /git-pr-merge

Merge the open PR for the current branch, gating on the merge check and adapting solo vs team by branch protection. Optionally chains cleanup.

## Dependencies

- `/process-flow-notation` — this body uses PFN.
- `/git-pr-status` — the merge gate; merge reads its report, never re-deriving the classification.
- `/git-pr-cleanup` — chained by `--cleanup`.

## Variables

- `{strategy}` — `--strategy`; defaults to the methodology default ∩ repo-allowed.
- `{cleanup}` — `--cleanup` present.

## Rules

- **The gate is `/git-pr-status`.** Merge never re-computes review/CI/mergeability — it reads the status report and acts.
- **Hard blockers are never bypassed** — red or pending CI, merge conflicts, behind-base. Pending CI exits to the watch step (`/git-ci`), never `--auto`; v1 prefers an explicit watch-then-merge over fire-and-forget auto-merge.
- **Soft blockers branch by path.** Solo (no base protection): present them, confirm bypass, merge. Team (protected base): wait by default; offer an `--admin` override only when the viewer has admin rights (the solo-author-on-a-protected-repo case), and only as an explicit confirmed choice — never silent.
- **Strategy must be repo-allowed** — `{strategy}` is validated against the gate's `allowed-strategies`; an unallowed strategy exits.
- Merge only; branch deletion and base sync are `/git-pr-cleanup`'s job (chained by `--cleanup`). Keeps merge single-purpose and cleanup idempotent across squash/rebase merges.
- Never force-push or run destructive git operations.

## Process

1. Preconditions:
    1. {branch}: bash: `git branch --show-current`
    2. If {branch} is empty (detached HEAD): Exit process — detached HEAD; checkout the PR branch
2. {status}: skill: `/git-pr-status --branch {branch}`
3. Bind from the {status} report: {pr-exists}, {pr-number}, {base}, {recommended-path}, {merge-ready}, {blockers} (each with severity), {allowed-strategies}, {has-admin}
4. If {pr-exists} is false: Exit process — no open PR for {branch}; run `/git-pr-open` first

5. Hard gate:
    1. {hard}: blockers in {blockers} with severity `hard`
    2. If {hard} non-empty: Exit process — list {hard}. Red/pending CI → watch with `/git-ci`; conflicts or behind-base → `git rebase {base}` then re-push. Never bypassed.

6. Resolve {strategy}:
    1. {pr-md-path}: `.claude/git/pr.md`; if it exists: {methodology}: Read {pr-md-path}
    2. {strategy}: `--strategy` if given, else {methodology} default, else first of {allowed-strategies}
    3. If {strategy} not in {allowed-strategies}: Exit process — strategy `{strategy}` not allowed by repo settings; allowed: {allowed-strategies}

7. Soft gate (only when {merge-ready} is false):
    1. {soft}: blockers in {blockers} with severity `soft`
    2. If {recommended-path} is `solo-immediate`:
        1. AskUserQuestion — present {soft}; merge anyway / cancel. Apply /confirm-shared-intent.
        2. If cancel: Exit process — merge cancelled; soft blockers stand
        3. {admin-flag}: empty (no protection to override)
    3. If {recommended-path} is `team-gated`:
        1. If {has-admin} is false: Exit process — team path; soft blockers unmet ({soft}) and no admin rights to override. Wait for required approvals / clear annotations.
        2. AskUserQuestion — present {soft}; wait (exit) / admin-override merge. Apply /confirm-shared-intent.
        3. If wait: Exit process — waiting on {soft}
        4. {admin-flag}: `--admin`
8. Else (merge-ready): {admin-flag}: empty

9. Merge: bash: `gh pr merge {pr-number} --{strategy} {admin-flag}`
10. If {cleanup}: skill: `/git-pr-cleanup --base {base} --head {branch}`

## Report

Return to caller:

- Merged: PR #{pr-number} → {base} via {strategy}{` (admin override)` if admin-flag}
- Path: {recommended-path}; soft blockers bypassed: {soft or none}
- Cleanup: chained ({cleanup-report}) | pending — run `/git-pr-cleanup`
