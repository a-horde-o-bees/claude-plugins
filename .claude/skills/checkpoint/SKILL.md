---
name: checkpoint
description: Commit, auto-init, push current branch, and (on main) refresh marketplace, update plugins, dispatch async CI gate, recommend restart
allowed-tools:
  - Skill
  - Agent
  - Bash(claude plugins *)
  - Bash(python3 scripts/auto_init.py)
  - Bash(git status *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git rev-parse *)
  - Bash(git branch *)
  - Bash(gh run *)
---

# /checkpoint

Bundle the development checkpoint cycle for the current branch — commit, rectify deployed state against current templates, commit derivatives, push. When the current branch is `main`, also refresh marketplace, update plugins, dispatch the async CI gate, and recommend a restart so the cached plugin install picks up the new code. Sandbox and feature branches stop after the push because marketplace, cache, and CI integration only apply to main.

## Workflow

1. {branch} = bash: `git branch --show-current`

> Branch awareness — checkpoint runs the same commit/auto-init/push cycle on any branch. Only the post-push integration steps (marketplace refresh, plugin update, CI gate, restart recommendation) are scoped to main, because those steps depend on the marketplace cache fetching from main tags and on CI workflows that fire for main pushes.

2. Commit — skill: `/ocd:git commit`
3. Auto-init — bash: `python3 scripts/auto_init.py`

> Derivative commit — auto-init may rectify deployed state (template→deployed syncs, navigator DB reinstall). Commit those derivatives so a single push in the next step carries both the user work and its derivative rectifications together — one CI run instead of two. Stage specific paths parsed from auto-init output rather than `git add -A`, matching the /ocd:git commit "stage by name" rule.

4. Derivative commit:
    1. bash: `git status --short`
    2. If no changes: skip remaining sub-steps — auto-init produced no rectifications
    3. Parse auto-init output to identify the rectified paths (each line has the form `path: before → after`)
    4. Stage those specific paths: bash: `git add <path1> <path2> ...`
    5. Commit: bash: `git commit -m "Deployed — rectify <brief summary derived from rectified paths>"` — message enumerates or summarizes what changed
5. Push — skill: `/ocd:git push --branch {branch}`

> Main-only integration — marketplace refresh and plugin update fetch from main; running them after a sandbox push pulls stale main into cache while the sandbox is the active workspace. CI gate against origin/main is meaningless from a non-main push. Skip cleanly when {branch} is not main.

6. If {branch} is `main`:
    1. Marketplace refresh — bash: `claude plugins marketplace update a-horde-o-bees`
    2. Update plugin — bash: `claude plugins update ocd@a-horde-o-bees`
    3. CI gate (async):

> Dispatch a background agent to watch GitHub Actions and compose a notification message describing the outcome. Foreground checkpoint returns immediately after dispatch; the session receiving the agent's task-completion result fires `PushNotification` with the returned `notify-message` field, since `PushNotification` is foreground-session-scoped and not exposed to spawned agents. Runs already completed at dispatch time are reported synchronously so the foreground still sees stable-state results.

        1. {sha} = bash: `git rev-parse origin/main`
        2. bash: `gh run list --branch main --limit 5 --json databaseId,headSha,conclusion,status,workflowName,url`
        3. Parse the JSON output; identify runs whose `headSha` matches {sha}
        4. If no matching runs found: Set {ci-status} = `"no runs scheduled for {sha} yet — check manually via gh run list"` and proceed to Report
        5. {watch-ids} = run IDs with `status` in (`in_progress`, `queued`)
        6. If {watch-ids} is empty:
            1. {ci-status} = synchronous aggregate — all `success` → `passed`; any `failure` → `failed` (with workflow name + URL); any other conclusion → surface as-is
        7. Else:
            1. async Spawn: Call: `_ci_watch.md` ({sha} = {sha}, {run-ids} = {watch-ids})
            2. {ci-status} = `"dispatched for runs {watch-ids} — notification on completion"`

### Report

- Branch: {branch}
- Commits pushed: count and branch
- Auto-init output: deployed file changes, orphans removed, DB migration flags if any
- If {branch} is `main`:
    - Plugins updated: versions
    - CI status for {sha}:
        - **Passed** (all runs were already complete at dispatch time) — list the workflows that ran successfully
        - **Failed** (some run was already complete + failed at dispatch time) — flag prominently with workflow name + run URL; recommend investigating before further work
        - **Dispatched** (runs were still in progress at dispatch time) — report the watched run IDs; the agent's task-completion result carries a `notify-message` for the receiving session to deliver via `PushNotification`. No foreground wait.
        - **No runs scheduled** — note that no workflows were triggered (or GitHub hadn't scheduled yet; manual recheck may be needed)
    - If commits were pushed AND CI passed (synchronous): recommend session restart (`/exit` then `claude --continue`)
    - If CI was dispatched (async): recommend waiting for the task-completion result before restart — the receiving session delivers the push, so a restart before completion drops the notification. Manual `gh run list` recheck is the fallback if restart can't wait
    - If CI failed (synchronous): restart recommendation is still valid but investigating the CI failure comes first
- Else: note that marketplace refresh, plugin update, CI gate, and restart recommendation are main-only and were skipped on this branch
- If nothing was pushed: checkpoint complete, no restart needed
- If auto-init surfaced DB schema mismatches: flag the backup paths under `.claude/pre-sync/` and prompt the user to migrate before the next /checkpoint
