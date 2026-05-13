# CI

> Report GitHub Actions run state for the latest commit on a branch. Dispatches a background watcher when runs are in flight so the foreground doesn't block.

> Branch defaults to current. Standalone "check the build" verb; composition primitive for checkpoint skills.

### Variables

- {branch} — branch name; defaults to current when omitted

### Rules

- Branch defaults to current when `--branch` is omitted
- No-runs-scheduled is reported, not an error — CI may not have triggered for this commit, or GitHub may not have scheduled runs yet
- Already-failed runs at dispatch are flagged synchronously with workflow name + URL — no background watcher
- In-progress runs spawn an async watcher; foreground returns immediately. Task-completion text reports the outcome inline
- {ci-status} is a 5-value enum: `passed`, `failed`, `dispatched`, `incomplete`, `no-runs`. Classification is deterministic and lives in `<skill-base>/scripts/ci.py`; the workflow consumes its JSON output and emits the template matching {ci-status} — see ### Report. Emit verbatim, no inventing or paraphrasing

### Process

1. If not {branch}: {branch}: bash: `git branch --show-current`

2. {classification}: bash: `uv run <skill-base>/scripts/ci.py classify --branch {branch}`

3. From {classification} JSON, bind:
    - {sha}, {sha-short}, {ci-status} — always present
    - {workflow-list} — when {ci-status} is `passed`
    - {failing-workflow}, {failing-url} — when `failed`
    - {watch-ids} — when `dispatched`
    - {trouble-list} — when `incomplete`

4. If {ci-status} is `dispatched`: async Spawn: Call: `_ci_watch.md` ({sha}: {sha}, {run-ids}: {watch-ids})

5. Emit the template matching {ci-status} — see ### Report.

### Report

Pick the literal template for the current {ci-status} and emit verbatim. Templates use `key: value` lines and close with `Next:` corrective guidance where action is implied.

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
