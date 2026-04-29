# CI

> Report GitHub Actions run state for the latest commit on a branch. Synchronous when runs are already complete at dispatch time; dispatches a background watcher (`_ci_watch.md`) when runs are still in progress, so the foreground does not block on CI (typically 30–90s per run).

Branch defaults to current. Useful as a standalone "check the build" verb after manual pushes, and as a composition primitive that `_checkpoint.md` (and project-level checkpoint skills) call to handle CI without re-implementing the watch logic.

### Variables

- {branch} — branch name; defaults to current when not provided

### Rules

- Branch defaults to current when --branch is omitted
- No-runs-scheduled is reported, not an error — CI may not have triggered for this commit, or GitHub may not have scheduled runs yet
- Already-failed runs at dispatch time are flagged synchronously with workflow name + URL — no background watcher needed
- In-progress runs spawn an async watcher; foreground returns immediately. The session receiving the agent's task-completion result reports the outcome inline as text

### Process

1. If not {branch}: {branch} = bash: `git branch --show-current`
2. {sha} = bash: `git rev-parse origin/{branch}`
3. bash: `gh run list --branch {branch} --limit 5 --json databaseId,headSha,conclusion,status,workflowName,url`
4. Parse the JSON output; identify runs whose `headSha` matches {sha}
5. If no matching runs found: Return to caller — `{ci-status}` = `"no runs scheduled for {sha} yet — check manually via gh run list"`
6. {watch-ids} = run IDs with `status` in (`in_progress`, `queued`)
7. If {watch-ids} is empty:
    1. {ci-status} = synchronous aggregate — all `success` → `passed`; any `failure` → `failed` (with workflow name + URL); any other conclusion → surface as-is
8. Else:
    1. async Spawn: Call: `_ci_watch.md` ({sha} = {sha}, {run-ids} = {watch-ids})
    2. {ci-status} = `"dispatched for runs {watch-ids} — notification on completion"`
9. Return to caller:
    - Branch and commit SHA watched
    - {ci-status}:
        - **Passed** (synchronous) — list workflows that ran successfully
        - **Failed** (synchronous) — flag prominently with workflow name + run URL
        - **Dispatched** (async) — report watched run IDs; outcome lands as text in this session via task-completion result
        - **No runs scheduled** — note that no workflows were triggered or GitHub hadn't scheduled yet
