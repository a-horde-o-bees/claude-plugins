---
name: git-pr-merge
description: Merge an open PR through the merge gate on the solo or team path, never bypassing hard blockers. Use for "merge the PR", "land it", "ship the PR", or the merge step of a checkpoint.
argument-hint: "[--strategy squash|merge|rebase] [--cleanup] [--auto]"
allowed-tools:
  - Bash(git *)
  - Bash(gh *)
  - Bash(uv run *)
  - Read
  - Skill
  - AskUserQuestion
---

# /git-pr-merge

Merge the open PR for the current branch, gating on the merge check and adapting solo vs team by branch protection. Optionally chains cleanup.

## Dependencies

- `/git-pr-cleanup` — chained by `--cleanup`.

## Variables

- `{strategy}` — `--strategy`; defaults to the methodology default ∩ repo-allowed.
- `{cleanup}` — `--cleanup` present.
- `{auto}` — `--auto` present: hands-off. Watch pending CI to green, bypass soft blockers without prompting, admin-override on a protected base when the viewer has rights.

## Rules

- **The gate is `scripts/pr.py`.** Merge never re-computes review/CI/mergeability — it runs `pr.py gate` and acts on the JSON verdict, rather than re-invoking the status skill. The verdict is computed fresh at merge time.
- **Hard blockers are never bypassed** — red CI, merge conflicts, and behind-base always exit, with or without `--auto`. Pending CI exits to the watch step (`/git-ci`) by default; under `--auto` the skill watches CI to completion in-process, then merges if it lands green — a blocking watch-then-merge, never GitHub's fire-and-forget queued auto-merge.
- **Soft blockers branch by path.** Solo (no base protection): present them, confirm bypass, merge. Team (protected base): wait by default; offer an `--admin` override only when the viewer has admin rights (the solo-author-on-a-protected-repo case), and only as an explicit confirmed choice — never silent. `--auto` takes that choice automatically: soft blockers bypass without a prompt, and on a protected base where the viewer has admin the override is applied and reported in full — automatic, never hidden. Without admin on a protected base, `--auto` still cannot merge and exits.
- **Strategy must be repo-allowed** — `{strategy}` is validated against the gate's `allowed-strategies`; an unallowed strategy exits.
- Merge only; branch deletion and base sync are `/git-pr-cleanup`'s job (chained by `--cleanup`). Keeps merge single-purpose and cleanup idempotent across squash/rebase merges.
- Never force-push or run destructive git operations.

## Process

1. Preconditions:
    1. {branch}: bash: `git branch --show-current`
    2. If {branch} is empty (detached HEAD): Exit process — detached HEAD; checkout the PR branch
2. {status}: bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/pr.py gate --branch {branch}` — the gate; run directly, no skill round-trip, computed fresh
3. Bind from the {status} JSON: {pr-exists}, {pr-number}, {base}, {recommended-path}, {merge-ready}, {blockers} (each with severity), {allowed-strategies}, {has-admin}
4. If {pr-exists} is false: Exit process — no open PR for {branch}; run `/git-pr-open` first

5. Hard gate:
    1. {hard}: blockers in {blockers} with severity `hard`
    2. {ci-pending}: {hard} is exactly one blocker and it is pending CI
    3. If {hard} non-empty AND NOT {ci-pending}: Exit process — list {hard}. Red CI → inspect the run; conflicts or behind-base → `git rebase {base}` then re-push. Never bypassed.
    4. If {ci-pending}:
        1. If NOT {auto}: Exit process — CI in flight; watch with `/git-ci --branch {branch}`, then re-invoke merge once green.
        2. If {auto}:
            1. bash: `gh pr checks {pr-number} --watch --interval 20` — block until every check settles
            2. Re-run steps 2–3 (a fresh gate verdict; re-bind {blockers}, {merge-ready}, {recommended-path}), then go to 5.1 — a green landing empties {hard} and the gate proceeds; a red landing falls to 5.3 and exits

6. Resolve {strategy}:
    1. {pr-md-path}: `.claude/git/pr.md`; if it exists: {methodology}: Read {pr-md-path}
    2. {strategy}: `--strategy` if given, else {methodology} default, else first of {allowed-strategies}
    3. If {strategy} not in {allowed-strategies}: Exit process — strategy `{strategy}` not allowed by repo settings; allowed: {allowed-strategies}

7. Soft gate (only when {merge-ready} is false):
    1. {soft}: blockers in {blockers} with severity `soft`
    2. If {recommended-path} is `solo-immediate`:
        1. If NOT {auto}:
            1. AskUserQuestion — present {soft}; merge anyway / cancel. Apply /confirm-shared-intent.
            2. If cancel: Exit process — merge cancelled; soft blockers stand
        2. {admin-flag}: empty (no protection to override)
    3. If {recommended-path} is `team-gated`:
        1. If {has-admin} is false: Exit process — team path; soft blockers unmet ({soft}) and no admin rights to override. Wait for required approvals / clear annotations.
        2. If {auto}: {admin-flag}: `--admin` — override applied automatically; surface it in the report
        3. If NOT {auto}:
            1. AskUserQuestion — present {soft}; wait (exit) / admin-override merge. Apply /confirm-shared-intent.
            2. If wait: Exit process — waiting on {soft}
            3. {admin-flag}: `--admin`
8. Else (merge-ready): {admin-flag}: empty

9. Merge: bash: `gh pr merge {pr-number} --{strategy} {admin-flag}`
10. If {cleanup}: skill: `/git-pr-cleanup --base {base} --head {branch}`

## Report

Return to caller:

- Merged: PR #{pr-number} → {base} via {strategy}{` (admin override)` if admin-flag}
- Mode: {`--auto` (hands-off) if auto, else interactive}{`; CI watched to green` if it was pending under --auto}
- Path: {recommended-path}; soft blockers bypassed: {soft or none}
- Cleanup: chained ({cleanup-report}) | pending — run `/git-pr-cleanup`
