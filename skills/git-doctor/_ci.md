# git-doctor — CI domain

> The GitHub Actions CI-config domain of `/git-doctor`. On demand (`/git-doctor ci [audit|harden|reconcile]`) or when `detect.sh` flags workflow files in the change. Diagnoses deterministically (classification lives in `scripts/ci_doctor.py`), proposes scoped edits, applies only on approval — never rewrites a workflow wholesale. Config hardening, not code review.

## Variables

- `{ci-verb}` — first token of {ci-args}: `audit` (default, report-only), `harden` (apply fixes on approval), or `reconcile` (required-check ↔ job-name only).
- `{branch}` — `--branch <name>` for `reconcile`; else the repo default.

## Rules

- **The script is the source of truth.** `scripts/ci_doctor.py` classifies; this domain emits its findings verbatim and proposes fixes from the `fix` hints — never inventing findings or severity.
- **Severity is the script's call.** `high` — supply-chain / privilege (unpinned actions, broad `GITHUB_TOKEN`); `medium` — robustness (no job timeout); `low` — efficiency (no concurrency on PR-feedback workflows).
- **`audit` and `reconcile` are read-only.** Only `harden` writes, and only after explicit approval of a presented diff. Never edit a workflow not surfaced by the audit.
- **SHA-pin fixes resolve the real commit.** For an unpinned action, resolve the tag to its commit SHA with `gh api` and pin to that exact SHA with a `# vX.Y.Z` comment — never invent a SHA.
- **Pair pins with an updater.** When proposing SHA pins, recommend (or, on approval, scaffold) `.github/dependabot.yml` with the `github-actions` ecosystem so pins stay current via reviewed PRs.

## Process

1. {ci-verb}: first token of {ci-args} (default `audit`); {branch}: `--branch` value, else bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@' | grep . || gh api repos/{owner}/{repo} --jq .default_branch 2>/dev/null || echo main`
2. If {ci-verb} is `reconcile`: Call: Reconcile; Return to caller
3. {audit}: bash: `uv run --directory . ${CLAUDE_SKILL_DIR}/scripts/ci_doctor.py audit .github/workflows`
4. Bind from {audit} JSON: {clean}, {severity-counts}, {results} (per-file findings, each with check / severity / detail / fix)
5. {reconcile}: Call: Reconcile — fold its mismatches in as additional findings (a required check matching no job is a `high`: the PR can never merge)
6. Emit the ### Audit report grouped by severity
7. If {ci-verb} is `audit`: Return to caller — report only
8. If {ci-verb} is `harden`:
    1. If {clean} AND no reconcile mismatch: Return to caller — already hardened; nothing to fix
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
Next: `/git-doctor ci harden` to apply the fixes (gated on review).
```

### Harden

```
Applied: {count} fix(es) — {per applied: <file> <check>}
Skipped: {declined or deferred}
Dependabot: {scaffolded | already present | declined}
Next: commit the workflow changes; required-check reconciliation needs branch-protection edits (admin).
```
