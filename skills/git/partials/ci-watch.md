# CI Watch (background)

Wait for GitHub Actions CI runs to complete for a commit SHA and return the final classification to the caller.

> Spawned asynchronously by the `/git ci` and `/git checkpoint` verbs — foreground returns immediately; this agent runs independently; the session receiving the task-completion result reports inline.

## Variables

- `{cwd}` — the repo the runs belong to (a `watches[]` entry's `cwd`)
- `{sha}` — commit SHA whose CI runs to watch
- `{run-ids}` — space-separated GitHub Actions databaseIds to watch

## Rules

- The driver blocks until each watched run completes, then re-lists all runs for the SHA and re-classifies with the same logic `/git ci` uses. Emit the matching template verbatim — no inventing or paraphrasing.
- Post-watch `{ci-status}` is normally `passed`, `failed`, or `incomplete`. `dispatched` means new runs appeared for the SHA while watching — re-run step 1 with the new `watch_ids`. `unavailable` means gh stopped answering — report it, never guess.

## Process

1. `{classification}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py ci-watch --cwd {cwd} --sha {sha} --run-ids {run-ids}`
2. Bind from `{classification}` JSON: `{sha_short}`, `{ci-status}`, and the status's variables (`{workflow_list}` | `{failing_workflow}` + `{failing_url}` | `{trouble_list}` | `{watch_ids}`).
3. If `{ci-status}` is `dispatched`: go to step 1 with the new `{watch_ids}`.
4. Emit the template matching `{ci-status}` — see ## Report.

## Report

Pick the literal template for the current `{ci-status}` and emit verbatim.

**`passed`:**

```
SHA: {sha_short}
CI: passed
Workflows: {workflow_list}
```

**`failed`:**

```
SHA: {sha_short}
CI: FAILED
Failing workflow: {failing_workflow}
Run URL: {failing_url}
Next: open the run URL to inspect logs; fix the failure and re-push.
```

**`incomplete`:**

```
SHA: {sha_short}
CI: incomplete
Runs:
{trouble_list}
Next: rerun via `gh run rerun <id>` or inspect each run for cause.
```

**`unavailable`:**

```
SHA: {sha_short}
CI: unavailable — gh stopped answering while watching
Next: check `gh auth status`, then `/git ci` to re-check.
```
