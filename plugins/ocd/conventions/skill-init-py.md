---
matches: "_init.py"
governed_by:
  - .claude/rules/ocd-design-principles.md
  - .claude/conventions/python.md
---

# Skill Init Conventions

Conventions for `_init.py` modules — skill infrastructure that implements `init()` and `status()` contract.

## Interface Contract

Every `_init.py` exports two functions returning `{"files": [...], "extra": [...]}`:

- `init(plugin_root, project_dir, force=False)` — deploy skill infrastructure
- `status(plugin_root, project_dir)` — report skill infrastructure state

`files` entries: `{"path": str, "before": str, "after": str}` — relative deployed path with state transitions (`absent`, `current`, `divergent`).

`extra` entries: `{"label": str, "value": str}` — additional status lines rendered as aligned columns.

## Status Labels

Two standard labels:

- `overall status` — single line summarizing infrastructure state
- `action needed` — copy-pastable slash command for next step

## Database Status Pattern

Skills with SQLite databases report status through a standard state machine. States, output format, and action commands are all deterministic.

### States

| State | `overall status` | `action needed` |
|-------|-----------------|-----------------|
| DB file absent | `not initialized` | `/{plugin}-init` |
| DB file present, schema divergent | `error — divergent schema` | `/{plugin}-init --force` |
| DB file present, schema valid | `operational — {metric summary}` | `/{skill-command}` |
| DB file present, SQL error | `error — {error message}` | `/{plugin}-init --force` |

### Schema Validation

Compare expected tables against actual tables using subset check — expected tables must all be present. Additional tables are not an error.

```python
expected_tables = {"records", "record_details", "record_tags"}
actual_tables = {row[0] for row in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'",
).fetchall()}
if not expected_tables.issubset(actual_tables):
    # divergent schema
```

### Metric Summary

Operational status includes a metric summary with counts relevant to the skill domain. Format: `operational — {count} {noun}, {count} {noun}, ...`

Counts use skill-specific nouns (entities, entries, notes). Include enough metrics for user to understand health at a glance without querying.

### Action Needed

Always present. The value is a copy-pastable slash command — no prose, no "Run" prefix, no parenthetical explanations.

- Not initialized → `/{plugin}-init`
- Error states → `/{plugin}-init --force`
- Operational → `/{skill-command}` (primary skill for this infrastructure)
