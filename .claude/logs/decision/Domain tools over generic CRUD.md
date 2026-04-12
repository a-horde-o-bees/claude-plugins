# MCP domain tools: Replace generic CRUD with domain tools encoding business logic (set/add/remove/clear)

## Purpose

Blueprint research MCP server initially exposed generic CRUD tools (`create_records`, `read_records`, `update_records`, `delete_records`) with a raw SQL escape hatch (`query`).

## Context

Blueprint research MCP server initially exposed generic CRUD tools (`create_records`, `read_records`, `update_records`, `delete_records`) with a raw SQL escape hatch (`query`). This led to progressive scope creep toward reimplementing a SQL query builder in JSON — adding operators, conditions, joins, then considering aggregation, ordering, grouping, and subquery composition. Each addition moved further from the server's purpose without matching SQL's expressiveness.

The core problem: generic CRUD tools map to database operations, not domain operations. Agents end up constructing queries instead of expressing intent. The server routes by table name and parses operator syntax instead of encoding business rules.

## Options Considered

**Query builder** — extend `read_records` with `select`, `group_by`, `having`, `order_by`, subquery support. Approaches SQL expressiveness through JSON parameters. Rejected: produces JSON-flavored SQL that is harder to read than actual SQL, adds no business logic interception, and requires ongoing feature additions to match SQL capabilities.

**Domain tools** — replace generic CRUD with purpose-built tools named for what they do. Each tool encodes one operation on one property. Business logic (validation, normalization, dedup) lives in the tool implementation. Agents express intent (`reject_entity`, `add_notes`) rather than constructing queries.

**Raw SQL only** — expose only a query executor. Agents write SQL directly. Rejected: loses all business logic interception (dedup, stage validation, URL normalization, provenance tracking) that makes write operations deterministic.

## Decision

Domain tools. Four consistent verbs operating on entity properties:

- `set` — replace a value (scalar or entire collection)
- `add` — append to a collection
- `remove` — remove specific items from a collection
- `clear` — reset to null or empty

Each tool is named `{verb}_{property}` and takes the entity ID plus only what's changing. `register_entity` is the sole tool without an entity ID (it creates one). Query tools are named `get_*` / `list_*` / `find_*` for domain-specific reads.

No generic table parameter. No operator parsing. No query building. Missing read capability = new domain query tool.

## Purpose

The MCP server provides deterministic operations for agent-facing instructions where supporting data is relational. It is not a general-purpose database interface. Business logic lives in tools so agent instructions stay focused on research decisions rather than data manipulation.

## Consequences

- Enables: agent instructions reference domain operations by name; business logic centralized in tool implementations; no drift toward query builder
- Constrains: new read patterns require new tools rather than flexible query construction
- Mitigation: purpose-built query tools cover all current phase workflows; `describe_schema` provides orientation; new tools are additive (no breaking changes to existing tools)
