---
name: checkpoint
description: Bundle the development checkpoint cycle for the current branch — commit (via /ocd:git), push, and CI watch. On main, also refresh marketplace, update plugins, and recommend a session restart so the cached plugin install picks up the new code.
allowed-tools:
  - Skill
  - Bash(python3 -c *)
  - Bash(claude plugins *)
  - Bash(git status *)
  - Bash(git add *)
  - Bash(git commit *)
  - Bash(git branch *)
---

# /checkpoint

Bundle the development checkpoint cycle for the current branch — commit, push, watch CI. When the current branch is `main`, also refresh marketplace, update plugins, and recommend a restart so the cached plugin install picks up the new code. Sandbox and feature branches stop after the CI gate because marketplace, cache, and restart integration only apply to main.

The generic commit + push + CI steps are delegated to `/ocd:git` verbs (`commit`, `push`, `ci`). Project-specific layers — marketplace refresh, plugin update, restart recommendation — sit on top of those calls. Other projects can use `/ocd:git checkpoint` directly when they don't need these layers.

> Auto-init is paused — `scripts/auto_init.py` no longer runs as part of /checkpoint while the new opt-in install machinery (per-system, per-scope) is settled. After the new model lands, rectification will move into the system-level install handlers and this skill may regain (or retire) an auto-init step depending on what's needed.

## Workflow

1. {branch} = bash: `git branch --show-current`

> Branch awareness — checkpoint runs the same commit/push/ci cycle on any branch. Only the post-push integration steps (marketplace refresh, plugin update, restart recommendation) are scoped to main, because those steps depend on the marketplace cache fetching from main tags and on the local plugin cache being a copy of what main publishes.

2. Commit — skill: `/ocd:git commit`
3. Push — skill: `/ocd:git push --branch {branch}`
4. CI gate — skill: `/ocd:git ci --branch {branch}`

> /ocd:git ci handles synchronous-vs-async dispatch and returns {ci-status} ∈ {passed, failed, dispatched, no-runs}. Non-main branches typically resolve to no-runs (CI workflows scoped to main); the gate runs uniformly so the user gets the answer when CI does fire on a sandbox branch.

> Main-only integration — marketplace refresh and plugin update fetch from main; running them after a sandbox push pulls stale main into cache while the sandbox is the active workspace. Restart recommendation only makes sense when the cached plugin actually changed (i.e. main was pushed). Skip cleanly when {branch} is not main.

5. If {branch} is `main`:
    1. {marketplace-name} = bash: `python3 -c "import json; print(json.load(open('.claude-plugin/marketplace.json'))['name'])"`
    2. {plugin-names} = bash: `python3 -c "import json; print(' '.join(p['name'] for p in json.load(open('.claude-plugin/marketplace.json'))['plugins']))"`
    3. Marketplace refresh — bash: `claude plugins marketplace update {marketplace-name}`
    4. For each {plugin} in {plugin-names}:
        1. Update plugin — bash: `claude plugins update {plugin}@{marketplace-name}`

### Report

- Branch: {branch}
- Commits pushed: count and branch (from /ocd:git push)
- CI status from /ocd:git ci (passed, failed, dispatched, or no-runs)
- If {branch} is `main`:
    - Plugins updated: versions
    - If commits were pushed AND CI passed (synchronous): recommend session restart (`/exit` then `claude --continue`)
    - If CI was dispatched (async): recommend waiting for the task-completion result before restart — the outcome lands as text in this session, so a restart before completion means manual `gh run list` recheck instead
    - If CI failed (synchronous): restart recommendation is still valid but investigating the CI failure comes first
- Else: note that marketplace refresh, plugin update, and restart recommendation are main-only and were skipped on this branch
- If nothing was pushed: checkpoint complete, no restart needed
