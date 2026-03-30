# DB-MCP Conventions

Database MCP server conventions — CRUD tools over SQLite with aggregate star schema. Applies to files in `servers/` directories that implement FastMCP tool handlers backed by SQLite.

## Data Model: Aggregate Star Schema

MCP databases follow the aggregate star schema pattern — star schema structure with ownership-based cascade behavior.

### Structure

- **Root table** — central entity (e.g., `entities`); other tables join to it via foreign keys
- **Satellite tables** — child records that belong to a root record (notes, measures, URLs, metadata)
- **Junction tables** — many-to-many relationships; owned by both sides

Every foreign key implies ownership. The root record and all reachable children form an **aggregate** — a consistency boundary where no orphans may exist outside it.

### Cascade Behavior

Delete operations cascade through the ownership tree:

1. Discover child tables via `PRAGMA foreign_key_list` — find all tables with FKs pointing to the target table
2. Recursively delete children depth-first before deleting the parent
3. Junction tables cascade from either side — deleting either parent removes the junction row
4. Applies to both single-record (`id`) and bulk (`all`) deletes

The cascade logic must be **dynamic** — derived from FK metadata at runtime, not hardcoded table names. This ensures schema evolution does not break delete behavior.

### Schema Conventions

- Root table primary key: `TEXT` (formatted `e1`, `e2`, etc.) or `INTEGER PRIMARY KEY AUTOINCREMENT`
- Foreign keys: `entity_id TEXT NOT NULL REFERENCES <root>(id)` — non-nullable enforces ownership
- Composite primary keys on satellite tables where natural key exists (e.g., `PRIMARY KEY (entity_id, measure)`)
- Auto-generated IDs on satellites without natural keys (e.g., notes with `id TEXT PRIMARY KEY`)

## Tool Interface

### Standard Tools

MCP database servers expose a consistent set of CRUD tools:

| Tool | Purpose |
|------|---------|
| `create_records` | Insert one or many records; accepts single object or array |
| `read_records` | Read with conditions and star-schema joins via `include` |
| `update_records` | Update record fields by ID |
| `delete_records` | Delete by ID or clear table; cascades through ownership tree |
| `query` | Read-only SQL (SELECT-only enforced) for complex reads |
| `describe_entities` | Schema introspection — tables, columns, types, FK relationships |
| `init_database` | Create schema if database doesn't exist; idempotent |

Domain-specific tools (e.g., `merge_entities`) extend the standard set when business logic requires operations beyond CRUD.

### Conditions Syntax

`read_records` accepts Django-style `__operator` conditions for filtering:

| Suffix | SQL | Example |
|--------|-----|---------|
| (none) | `=` | `{"stage": "new"}` |
| `__gte` | `>=` | `{"relevance__gte": 7}` |
| `__gt` | `>` | `{"relevance__gt": 7}` |
| `__lte` | `<=` | `{"relevance__lte": 3}` |
| `__lt` | `<` | `{"relevance__lt": 3}` |
| `__ne` | `!=` | `{"relevance__ne": 0}` |
| `__like` | `LIKE` | `{"name__like": "Tool%"}` |
| `__null` | `IS NULL` / `IS NOT NULL` | `{"field__null": true}` |

### Star-Schema Joins

`read_records` supports an `include` parameter that resolves FK relationships and nests related records:

```json
{"table": "entities", "conditions": {"id": "e1"}, "include": ["entity_notes", "entity_measures"]}
```

Returns entity records with `entity_notes: [...]` and `entity_measures: [...]` nested arrays. Empty relationships return `[]`.

`create_records` supports the inverse — nested child arrays in the data are decomposed into parent + child inserts:

```json
{"table": "entities", "data": {"name": "Tool", "entity_notes": [{"note": "First"}]}}
```

### Error Handling

- All tools check database existence before operating; return `{"error": "Database not initialized.", "action": "..."}` if missing
- `query` tool enforces SELECT-only — rejects INSERT, UPDATE, DELETE, DROP
- Invalid table names return clear error with available tables listed
- FK constraint violations return the SQLite error message
