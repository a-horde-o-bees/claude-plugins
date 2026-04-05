---
pattern: "servers/*.py"
depends:
  - .claude/conventions/mcp-server.md
  - .claude/rules/ocd-design-principles.md
  - .claude/conventions/python.md
---

# MCP Relational Conventions

Conventions for MCP servers backed by relational databases. Applies to files in `servers/` directories that implement FastMCP tool handlers.

## Data Model: Aggregate Star Schema

MCP databases follow the aggregate star schema pattern — star schema structure with ownership-based cascade behavior.

### Structure

- **Root table** — central entity; other tables join to it via foreign keys
- **Satellite tables** — child records that belong to a root record
- **Junction tables** — many-to-many relationships; owned by both sides

Every foreign key implies ownership. The root record and all reachable children form an **aggregate** — a consistency boundary where no orphans may exist outside it.

### Cascade Behavior

Delete operations cascade through the ownership tree. Cascade logic must be dynamic — derived from FK metadata at runtime, not hardcoded table names.

### Schema Conventions

- Root table primary key: `TEXT` (formatted prefix + number) or `INTEGER PRIMARY KEY AUTOINCREMENT`
- Foreign keys: non-nullable, enforce ownership
- Composite primary keys on satellite tables where natural key exists
- CHECK constraints enforce valid values for enum-like fields

## Tool Interface

Relational-specific tool design patterns. General tool conventions (naming, descriptions, input/output, error handling, granularity) are in the parent `mcp-server.md` convention.

### Domain Scope

Each tool encodes one operation on one property or relationship in the aggregate. Tools map to domain operations, not SQL statements — `set_description`, `link_goal_domain`, `add_notes` — not `update_row`, `insert_join`, or `execute_query`.

### Aggregate Awareness

Tools operate within aggregate boundaries. A tool that modifies a satellite record understands its relationship to the root — validation, cascade implications, and consistency checks are tool responsibilities, not caller responsibilities.

### Batch Operations

Registration and mutation tools accept arrays for batch processing. The tool handles per-item dedup, validation, and error collection internally — the caller provides the batch, the tool returns per-item results.

## Error Handling

- All tools check database existence before operating; return clear error with action guidance if missing
- CHECK constraint violations return the constraint expression dynamically
- Invalid inputs return corrective error messages guiding agent to self-correct
