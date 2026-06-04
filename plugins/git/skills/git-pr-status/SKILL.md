---
name: git-pr-status
description: Use when the merge-readiness of a branch's open PR needs surfacing — "is the PR ready to merge", "PR status", "can I merge yet", "what's blocking the PR", or any gate check before `/git-pr-merge`. Runs the merge gate: PR review state, CI checks plus commit-level annotations (warnings invisible in the PR summary), mergeability, and base-branch protection — whose presence selects the solo vs team path. Reports blockers by severity; emits the gate classification verbatim, never inventing.
argument-hint: "[--branch <name>]"
allowed-tools:
  - Bash(git *)
  - Bash(gh *)
  - Bash(uv run *)
---

# /git-pr-status

Report merge-readiness for the open PR on a branch. The gate classification is deterministic and lives in `scripts/pr.py`; this skill emits the matching template verbatim — no inventing, paraphrasing, or merging.

## Dependencies

- `/process-flow-notation` — this body uses PFN; a cold session needs the spec in context.

## Variables

- `{branch}` — `--branch <name>`; defaults to the current branch.

## Rules

- The gate is read-only — it inspects and reports, never merges, pushes, or mutates the PR.
- `{merge-ready}` and the blocker set come from `scripts/pr.py` and are emitted verbatim. The script is the single source of truth for review state, CI, annotations, mergeability, and the solo/team path.
- Severity is the script's call. **hard** (merge conflicts, behind base, a *required* check failing or pending) gate every path; **soft** (review unmet, protection-BLOCKED, draft) gate the team path and are confirmable-bypass on the solo path. **Advisories** (non-required checks failing/pending, and CI annotation counts) never gate — GitHub reports such a PR mergeable and never blocks on annotations; surfaced for visibility only. The script reads branch protection's `required_status_checks.contexts` to tell required from advisory, so a repo's report-only check or benign CI warnings never block the gate. This skill reports all three; bypass is `/git-pr-merge`'s call.
- No PR for the branch is a reported state, not an error.

## Process

1. If not {branch}: {branch}: bash: `git branch --show-current`
2. {gate}: bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/pr.py gate --branch {branch}`
3. Bind from {gate} JSON:
    - {pr-exists} — always present
    - When {pr-exists} is `false`: nothing further; emit the `no-pr` template
    - When `true`: {pr-number}, {base}, {url}, {is-draft}, {head-sha-short}, {protection}, {required-contexts}, {recommended-path}, {merge-ready}, {checks}, {annotation-count}, {review-decision}, {merge-state-status}, {mergeable}, {blockers}, {advisories}, {allowed-strategies}, {has-admin}
4. Emit the template matching {pr-exists} / {merge-ready} — see ### Report

## Report

**`no-pr`:**

```
Branch: {branch}
PR: none open for this branch
Next: open one with `/git-pr-open` (on a feature branch).
```

**merge-ready (`{merge-ready}` true):**

```
PR #{pr-number} → {base}   ({url})
Head: {head-sha-short}
Path: {recommended-path}   (protection: {protection})
Review: {review-decision}   Merge state: {merge-state-status}   Mergeable: {mergeable}
Required CI: {checks}   (required: {required-contexts})   Annotations: {annotation-count}
Advisories: {advisories or none — non-required checks; informational}
Merge-ready: yes
Next: `/git-pr-merge` — strategy from {allowed-strategies} / project pr.md.
```

**blocked (`{merge-ready}` false):**

```
PR #{pr-number} → {base}   ({url})
Head: {head-sha-short}
Path: {recommended-path}   (protection: {protection})
Review: {review-decision}   Merge state: {merge-state-status}   Mergeable: {mergeable}
Required CI: {checks}   (required: {required-contexts})   Annotations: {annotation-count}
Merge-ready: no
Admin: {has-admin}
Blockers:
{per blocker in {blockers}: <severity> — <detail>}
Advisories: {advisories or none — non-required checks; informational, never block}
Next: clear hard blockers before merge; soft blockers are confirmable-bypass on the solo path via `/git-pr-merge` (or an admin override on a protected base).
```
