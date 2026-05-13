# CI Watch (background)

> Wait for GitHub Actions CI runs to complete for a commit SHA and return the final classification to the caller.

> Spawned asynchronously by `/ocd:git ci` and `/ocd:git checkpoint` — foreground returns immediately; this agent runs independently; the session receiving the task-completion result reports inline.

### Variables

- {sha} — commit SHA whose CI runs to watch
- {run-ids} — space-separated list of GitHub Actions databaseIds to watch

### Rules

- {ci-status} after watching is one of `passed`, `failed`, `incomplete` (the `dispatched` and `no-runs` states from `_ci.md` don't apply post-watch — by construction we always have a tracked in-flight set)
- `scripts/ci.py watch` blocks until each watched run completes, then re-lists all runs for the SHA and re-classifies the final state via the same `classify_runs` logic `_ci.md` uses
- Template emission matches the matching three states of `_ci.md` § Report; emit verbatim, no inventing or paraphrasing

### Process

1. {classification}: bash: `uv run <skill-base>/scripts/ci.py watch --sha {sha} --run-ids {run-ids}`
2. Parse {classification} JSON. Assigns {sha-short}, {ci-status}, plus per-status fields: {workflow-list} (passed) | {failing-workflow} + {failing-url} (failed) | {trouble-list} (incomplete).
3. Emit the template matching {ci-status} — see ### Report.

### Report

Pick the literal template for the current {ci-status} and emit verbatim.

**`passed`:**

```
SHA: {sha-short}
CI: passed
Workflows: {workflow-list}
```

**`failed`:**

```
SHA: {sha-short}
CI: FAILED
Failing workflow: {failing-workflow}
Run URL: {failing-url}
Next: open the run URL to inspect logs; fix the failure and re-push.
```

**`incomplete`:**

```
SHA: {sha-short}
CI: incomplete
Runs:
{trouble-list}
Next: rerun via `gh run rerun <id>` or inspect each run for cause.
```
