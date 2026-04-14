# Log cleanup lacks a skill to enforce lifecycle

Each log type's `_template.md` defines its lifecycle — friction/idea/problem are queues deleted when resolved; decisions are persistent records updated as direction changes. But nothing enforces or assists this cleanup. Entries accumulate unless an agent manually reviews them.

## Scope

`.claude/logs/` across all four log types. Growing entry counts over time with no systematic way to identify resolved items or stale decisions.

## Needed

A `/log` skill (or equivalent) with:

- **Review workflow** — list entries by type, show what's outstanding at a glance
- **Cleanup workflow** — surface candidates for deletion (e.g., problem entries referencing already-fixed defects), update decision entries when direction changes, enforce each type's lifecycle per its template

Without this, log-routing's lifecycle pointer to type templates is aspirational — the routing convention names the lifecycle but there's no mechanism to carry it out.
