---
name: git-ci-doctor
description: Use when a repo's GitHub Actions CI needs auditing or hardening — "audit my CI", "harden the workflows", "is my CI secure", "pin my actions", "are my required checks wired right", "why is a required check stuck pending", or any review of `.github/workflows/` config. Audits for supply-chain and config risks (actions not pinned to commit SHAs, missing least-privilege `permissions:`, missing job timeouts, missing concurrency) and reconciles branch-protection required checks against the jobs CI defines. Diagnoses → classifies by severity → proposes scoped fixes → applies only on approval. Config hardening, not code review.
argument-hint: "[audit | harden | reconcile] [--branch <name>]"
allowed-tools:
  - Bash(git *)
  - Bash(gh *)
  - Bash(uv run *)
  - Read
  - Edit
  - AskUserQuestion
---

# /git-ci-doctor

Audit and harden a repository's GitHub Actions CI configuration. Diagnoses deterministically (the classification lives in `scripts/ci_doctor.py`), then proposes scoped edits and applies them only on approval — never rewrites a workflow wholesale.

## Dependencies

- `/git-doctor` — sibling pattern: diagnose → classify by repair risk → propose → apply on approval. This is its CI-config analogue.
- `plugin.json` declares no extra deps; the script's own `pyyaml` is resolved by `uv run` via the script's inline metadata.

## Variables

- `{verb}` — `audit` (default, report-only), `harden` (apply fixes on approval), or `reconcile` (required-check ↔ job-name only).
- `{branch}` — `--branch <name>` for `reconcile`; defaults to the repo's default branch.

## Rules

- **The script is the source of truth.** `scripts/ci_doctor.py` classifies; this skill emits its findings verbatim and proposes fixes from the `fix` hints — it does not invent findings or re-derive severity.
- **Severity is the script's call.** `high` — supply-chain / privilege (unpinned actions, broad `GITHUB_TOKEN`); `medium` — robustness (no job timeout); `low` — efficiency (no concurrency on PR-feedback workflows).
- **`audit` and `reconcile` are read-only.** Only `harden` writes, and only after explicit approval of a presented diff. Never force-push, never edit a workflow not surfaced by the audit.
- **SHA-pin fixes resolve the real commit.** For an unpinned action, resolve the tag to its commit SHA with `gh api` and pin to that exact SHA with a `# vX.Y.Z` comment — never invent a SHA.
- **Pair pins with an updater.** When proposing SHA pins, recommend (or, on approval, scaffold) `.github/dependabot.yml` with the `github-actions` ecosystem so pins stay current via reviewed PRs rather than going stale.

## Process

1. {verb}: first token of $ARGUMENTS (default `audit`); {branch}: `--branch` value, else bash: `git symbolic-ref --short refs/remotes/origin/HEAD | sed 's@^origin/@@'`
2. If {verb} is `reconcile`: Call: Reconcile; Exit process
3. {audit}: bash: `uv run --directory . ${CLAUDE_SKILL_DIR}/scripts/ci_doctor.py audit .github/workflows`
4. Bind from {audit} JSON: {clean}, {severity-counts}, {results} (per-file findings, each with check / severity / detail / fix)
5. {reconcile}: Call: Reconcile — fold its mismatches in as additional findings (a required check matching no job is a `high`: the PR can never merge)
6. Emit the ### Audit report grouped by severity
7. If {verb} is `audit`: Exit process — report only
8. If {verb} is `harden`:
    1. If {clean} AND no reconcile mismatch: Exit process — already hardened; nothing to fix
    2. For each {finding} in {results} (high → low):
        1. If {finding} is `unpinned-action`: {sha}: bash: `gh api repos/{action}/commits/{ref} --jq .sha`; propose `uses: {action}@{sha} # {ref}`
        2. Else: propose the edit from {finding}'s `fix` hint (top-level `permissions: contents: read`, `timeout-minutes`, `concurrency` block)
    3. Present all proposed edits as one batched diff. AskUserQuestion — apply all / select / cancel. Apply /confirm-shared-intent
    4. On approval: apply each via Edit
    5. If any SHA pin was applied AND no `.github/dependabot.yml`: offer to scaffold it (github-actions, weekly)
9. Emit the ### Harden report

## Reconcile

1. {rc}: bash: `uv run --directory . ${CLAUDE_SKILL_DIR}/scripts/ci_doctor.py reconcile --branch {branch}`
2. Bind: {protection}, {required-contexts}, {job-names}, {required-without-matching-job}, {jobs-not-required}
3. If {protection} is false: Return to caller: no branch protection on {branch} — nothing to reconcile
4. Return to caller:
    - {required-without-matching-job}: required checks that map to no job — these hang as "Expected — waiting" and block every PR (unless an external check supplies them); fix the name or remove from protection
    - {jobs-not-required}: jobs that gate nothing until added to protection

## Report

### Audit

```
CI audit: .github/workflows ({workflow-count} workflows)
Status: {clean ? hardened : findings by severity — high {h} / medium {m} / low {l}}
{per finding, grouped high→low: <file> — <check>: <detail>  → <fix>}
Required checks: {reconcile summary — mismatches or "all required checks map to a job"}
Next: `/git-ci-doctor harden` to apply the fixes (gated on review).
```

### Harden

```
Applied: {count} fix(es) — {per applied: <file> <check>}
Skipped: {declined or deferred}
Dependabot: {scaffolded | already present | declined}
Next: commit the workflow changes; required-check reconciliation needs branch-protection edits (admin).
```
