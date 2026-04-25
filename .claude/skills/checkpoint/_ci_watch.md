# CI Watch (background)

Wait for GitHub Actions CI runs to complete for a given commit SHA and return the aggregated outcome to the caller. Spawned asynchronously by /checkpoint so the foreground doesn't block on CI (typically 30–90s per run, sometimes longer). The parent checkpoint returns immediately after dispatch; this agent runs independently and the session receiving the task-completion result reports the outcome inline.

### Variables

- {sha} — commit SHA whose CI runs to watch
- {run-ids} — space-separated list of GitHub Actions databaseIds to watch
- {short-sha} — first 8 chars of {sha} for display

### Process

1. {short-sha} = first 8 characters of {sha}
2. For each {run-id} in {run-ids}:
    1. bash: `gh run watch {run-id} --exit-status` — blocks until complete; exits non-zero on failure. Timeout relaxed; this is background.
3. bash: `gh run list --branch main --limit 10 --json databaseId,headSha,conclusion,status,workflowName,url`
4. Parse JSON; select runs whose `headSha` equals {sha}
5. Aggregate conclusions:
    - All `success` → {verdict} = `pass`, {detail} = count of workflows
    - Any `failure` → {verdict} = `fail`, {detail} = first failing workflow name + run URL
    - Any `cancelled` / `timed_out` / still in progress → {verdict} = `incomplete`, {detail} = workflow names + statuses
6. Return to caller:
    - short-sha: {short-sha}
    - verdict: {verdict}
    - detail: {detail}
    - runs: full JSON of the matched runs
