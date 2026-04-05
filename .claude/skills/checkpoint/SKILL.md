---
name: checkpoint
description: Commit, push, refresh marketplace, update plugins, and detect restart need
allowed-tools:
  - Skill
  - Bash(git diff *)
  - Bash(claude plugins *)
---

# /checkpoint

Bundle the full development checkpoint cycle — commit, push, marketplace refresh, plugin update, restart detection. Ensures every step runs and reports the result.

## Trigger

User runs `/checkpoint`

## Route

1. Dispatch Workflow

## Workflow

1. Commit — skill: `/ocd-commit`
2. Push — skill: `/ocd-push --branch main`
3. Marketplace refresh — bash: `claude plugins marketplace update a-horde-o-bees`
4. Update plugins:

    - bash: `claude plugins update ocd@a-horde-o-bees`
    - bash: `claude plugins update blueprint@a-horde-o-bees`

5. Detect restart need:
    1. {pushed-commits} = commits pushed in step 2
    2. Check if any pushed commit modified files under `.claude/rules/` — bash: `git diff --name-only {pre-push-ref}..HEAD -- .claude/rules/`
    3. If rules changed: {restart-needed} = true
    4. Else: {restart-needed} = false

### Report

- Commits pushed: count and branch
- Plugins updated: versions
- If {restart-needed}: recommend session restart (`/exit` then `claude --continue`) — rule and convention changes take effect after restart
- If not {restart-needed}: checkpoint complete, no restart needed
