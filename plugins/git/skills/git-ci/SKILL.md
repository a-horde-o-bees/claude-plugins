---
name: git-ci
description: Use when GitHub Actions state for a branch needs surfacing — "check CI", "is the build green", "did CI pass", "watch the build", or any context after a push where the build outcome decides next steps. Returns one of `passed`, `failed`, `dispatched`, `incomplete`, `no-runs`; in-flight runs trigger a background watcher that reports completion inline as a task-completion event.
argument-hint: "[--branch <name>]"
allowed-tools:
  - Bash(git *)
  - Bash(gh *)
  - Bash(uv run *)
---

# /git-ci

Report GitHub Actions run state for the latest commit on a branch. Async background watcher when runs are in flight; foreground returns immediately.

## Rules

- Branch defaults to current when `--branch` is omitted
- No-runs-scheduled is reported, not an error — CI may not have triggered for this commit or GitHub may not have scheduled runs yet
- Failed runs report synchronously with workflow name + URL; no background watcher
- In-flight runs spawn the async watcher; foreground returns immediately. Task-completion text reports the outcome inline
- `{ci-status}` is a 5-value enum (`passed`, `failed`, `dispatched`, `incomplete`, `no-runs`). Classification is deterministic and lives in `scripts/ci.py`; the workflow consumes its JSON output and emits the matching template verbatim — no inventing, paraphrasing, or merging

## Process

1. If not {branch}: {branch}: bash: `git branch --show-current`
2. {classification}: bash: `uv run <THIS-FILE-DIR>/scripts/ci.py classify --branch {branch}`
3. Bind from {classification} JSON:
    - {sha}, {sha-short}, {ci-status} — always present
    - {workflow-list} — when {ci-status} is `passed`
    - {failing-workflow}, {failing-url} — when `failed`
    - {watch-ids} — when `dispatched`
    - {trouble-list} — when `incomplete`

4. If {ci-status} is `dispatched`: async Spawn: Call: `_watch.md` ({sha}: {sha}, {run-ids}: {watch-ids})
5. Emit the template matching {ci-status} — see ### Report

## Report

Emit the literal template for the current {ci-status} verbatim. Templates close with `Next:` corrective guidance where action is implied.

**`passed`:**

```
Branch: {branch}
SHA: {sha-short}
CI: passed
Workflows: {workflow-list}
```

**`failed`:**

```
Branch: {branch}
SHA: {sha-short}
CI: FAILED
Failing workflow: {failing-workflow}
Run URL: {failing-url}
Next: open the run URL to inspect logs; fix the failure and re-push.
```

**`dispatched`:**

```
Branch: {branch}
SHA: {sha-short}
CI: dispatched (async watch in flight)
Watching run IDs: {watch-ids}
Next: result lands as task-completion text in this session; no action required now.
```

**`incomplete`:**

```
Branch: {branch}
SHA: {sha-short}
CI: incomplete (cancelled / timed-out / non-success conclusion)
Runs:
{trouble-list}
Next: rerun via `gh run rerun <id>` or inspect each run for cause.
```

**`no-runs`:**

```
Branch: {branch}
SHA: {sha-short}
CI: no runs scheduled
Next: check manually via `gh run list --branch {branch}` — GitHub may not have triggered yet, or no workflows match this branch.
```
