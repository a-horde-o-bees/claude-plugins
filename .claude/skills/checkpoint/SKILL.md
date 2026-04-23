---
name: checkpoint
description: Commit, auto-init, push, refresh marketplace, update plugins, verify CI, recommend restart
allowed-tools:
  - Skill
  - Bash(claude plugins *)
  - Bash(python3 scripts/auto_init.py)
  - Bash(git status *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git rev-parse *)
  - Bash(gh run *)
---

# /checkpoint

Bundle the full development checkpoint cycle — commit, rectify deployed state against current templates, commit derivatives, push, marketplace refresh, plugin update, CI gate, restart recommendation. Ensures every step runs and reports the result.

## Route

1. Dispatch Workflow

## Workflow

1. Commit — skill: `/ocd:git commit`
2. Auto-init — bash: `python3 scripts/auto_init.py`

> Derivative commit — auto-init may rectify deployed state (template→deployed syncs, navigator DB reinstall). Commit those derivatives so a single push in step 4 carries both the user work and its derivative rectifications together — one CI run instead of two. Stage specific paths parsed from auto-init output rather than `git add -A`, matching the /ocd:git commit "stage by name" rule.

3. Derivative commit:
    1. bash: `git status --short`
    2. If no changes: skip remaining sub-steps — auto-init produced no rectifications
    3. Parse auto-init output to identify the rectified paths (each line has the form `path: before → after`)
    4. Stage those specific paths: bash: `git add <path1> <path2> ...`
    5. Commit: bash: `git commit -m "Deployed — rectify <brief summary derived from rectified paths>"` — message enumerates or summarizes what changed
4. Push — skill: `/ocd:git push --branch main`
5. Marketplace refresh — bash: `claude plugins marketplace update a-horde-o-bees`
6. Update plugin — bash: `claude plugins update ocd@a-horde-o-bees`

> CI gate — verify GitHub Actions passed for the latest push before declaring the checkpoint clean. Uses `gh run watch` which blocks until the run completes, so a red build surfaces in the checkpoint report rather than sitting unnoticed on main.

7. CI gate:
    1. {sha} = bash: `git rev-parse origin/main`
    2. bash: `gh run list --branch main --limit 5 --json databaseId,headSha,conclusion,status,workflowName,url`
    3. Parse the JSON output; identify runs whose `headSha` matches {sha}
    4. If no matching runs found: Report CI status as "no runs scheduled for {sha} — check manually via `gh run list`" and proceed to Report
    5. For each matching run with `status` in (`in_progress`, `queued`):
        1. bash: `gh run watch <databaseId> --exit-status` — blocks until the run completes; exits non-zero on failure
    6. {ci-status} = aggregate conclusions across the matching set:
        - All `success` → `passed`
        - Any `failure` → `failed` (with workflow names and run URLs)
        - Any timeout or still-running → `still running` (with run URLs)

### Report

- Commits pushed: count and branch
- Auto-init output: deployed file changes, orphans removed, DB migration flags if any
- Plugins updated: versions
- CI status for {sha}:
  - **Passed** — list the workflows that ran successfully
  - **FAILED** — flag prominently with workflow name + run URL; recommend investigating before further work
  - **Still running** — list in-progress run URLs so the user can check later
  - **No runs scheduled** — note that no workflows were triggered (or GitHub hadn't scheduled yet; manual recheck may be needed)
- If commits were pushed AND CI passed: recommend session restart (`/exit` then `claude --continue`) — rules, hooks, MCP servers, and skill code all run from the cached plugin install and pick up changes only after restart
- If CI failed: restart recommendation is still valid but investigating the CI failure comes first
- If nothing was pushed: checkpoint complete, no restart needed
- If auto-init surfaced DB schema mismatches: flag the backup paths under `.claude/pre-sync/` and prompt the user to migrate before the next /checkpoint
