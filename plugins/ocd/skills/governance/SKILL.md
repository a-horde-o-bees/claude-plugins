---
name: ocd-governance
description: |
  Governance skill — loads rules and conventions from frontmatter, matches files to applicable conventions, and computes the level-grouped dependency order. Invoked via MCP tools and the internal CLI, not as a user-facing slash command.
disable-model-invocation: true
user-invocable: false
---

# /ocd-governance

Governance infrastructure — the rules and conventions database that backs convention matching, dependency traversal, and the evaluate-governance skill. This skill has no user-facing workflow. It is initialized alongside the rest of the ocd plugin via `/ocd-init`, and its operations are consumed through:

- The `ocd-governance` MCP server (`governance_match`, `governance_list`, `governance_order`)
- The `skills.governance` CLI for scripted access
- The `convention_gate` hook, which reads the governance database on Read/Edit/Write

## Trigger

Not user-invocable. This skill exists as a package home for governance business logic and its init hook.

## Rules

- No user-facing workflow — all governance operations are consumed through MCP tools, the CLI, or the convention_gate hook
- The governance database is independent from the navigator database; each has its own schema and its own lifecycle
- Conventions are deployed by this skill's init hook, not navigator's
