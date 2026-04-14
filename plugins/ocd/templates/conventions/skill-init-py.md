---
includes: "_init.py"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/conventions/ocd/python.md
---

# Skill Init Conventions

Conventions for `_init.py` modules — skill infrastructure that implements `init()` and `status()` contract.

## Interface Contract

Every `_init.py` exports two functions returning `{"files": [...], "extra": [...]}`:

- `init(force=False)` — deploy skill infrastructure
- `status()` — report skill infrastructure state

Skill entry points take only their own skill-specific arguments. Project and plugin paths are resolved internally via the plugin framework helpers (`plugin.get_project_dir()`, `plugin.get_plugin_root()`, `plugin.get_plugin_data_dir()`) — see `python.md` *Project, Plugin, and Data Directory Resolution*. Never accept those paths as parameters.

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
| DB file absent | `not initialized` | `/{plugin}:init` |
| DB file present, schema divergent | `error — divergent schema` | `/{plugin}:init --force` |
| DB file present, schema valid | `operational — {metric summary}` | `/{plugin}:{skill-command}` |
| DB file present, SQL error | `error — {error message}` | `/{plugin}:init --force` |

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

**Noun choice is skill-specific.** Use the domain's natural unit — entities, entries, notes, events, records — rather than generic "items" or "rows".

**Metric count balances signal against noise.** Include enough metrics for the user to understand infrastructure health at a glance without querying. Stop short of enumerating every table's row count — pick the counts that answer "is this healthy and actively in use?"

### Action Needed

**Always present in status output.** Every state returns an `action needed` line, including the operational state — the value tells the user what the natural next step is, not whether there is a problem.

**Value is a copy-pastable slash command.** No prose, no "Run" prefix, no parenthetical explanations. The user pastes the value directly.

- Not initialized → `/{plugin}:init`
- Error states → `/{plugin}:init --force`
- Operational → `/{plugin}:{skill-command}` (primary skill for this infrastructure)
