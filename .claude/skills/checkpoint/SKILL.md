---
name: checkpoint
description: Commit, push, refresh marketplace, update plugins, recommend restart
allowed-tools:
  - Skill
  - Bash(claude plugins *)
---

# /checkpoint

Bundle the full development checkpoint cycle — commit, push, marketplace refresh, plugin update, restart recommendation. Ensures every step runs and reports the result.

## Trigger

User runs `/checkpoint`

## Route

1. Dispatch Workflow

## Workflow

1. Commit — skill: `/ocd:commit`
2. Push — skill: `/ocd:push --branch main`
3. Marketplace refresh — bash: `claude plugins marketplace update a-horde-o-bees`
4. Update plugins:

    - bash: `claude plugins update ocd@a-horde-o-bees`
    - bash: `claude plugins update blueprint@a-horde-o-bees`

### Report

- Commits pushed: count and branch
- Plugins updated: versions
- If commits were pushed: recommend session restart (`/exit` then `claude --continue`) — rules, hooks, MCP servers, and skill code all run from the cached plugin install and pick up changes only after restart
- If nothing was pushed: checkpoint complete, no restart needed
