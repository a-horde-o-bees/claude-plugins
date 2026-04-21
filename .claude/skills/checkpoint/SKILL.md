---
name: checkpoint
description: Commit, push, auto-init, refresh marketplace, update plugins, recommend restart
allowed-tools:
  - Skill
  - Bash(claude plugins *)
  - Bash(python3 scripts/auto_init.py)
---

# /checkpoint

Bundle the full development checkpoint cycle — commit, push, rectify deployed state against current templates, marketplace refresh, plugin update, restart recommendation. Ensures every step runs and reports the result.

## Route

1. Dispatch Workflow

## Workflow

1. Commit — skill: `/ocd:git commit`
2. Push — skill: `/ocd:git push --branch main`
3. Auto-init — bash: `python3 scripts/auto_init.py`
4. Marketplace refresh — bash: `claude plugins marketplace update a-horde-o-bees`
5. Update plugin — bash: `claude plugins update ocd@a-horde-o-bees`

### Report

- Commits pushed: count and branch
- Auto-init output: deployed file changes, orphans removed, DB migration flags if any
- Plugins updated: versions
- If commits were pushed: recommend session restart (`/exit` then `claude --continue`) — rules, hooks, MCP servers, and skill code all run from the cached plugin install and pick up changes only after restart
- If nothing was pushed: checkpoint complete, no restart needed
- If auto-init surfaced DB schema mismatches: flag the backup paths under `.claude/pre-sync/` and prompt the user to migrate before the next /checkpoint
