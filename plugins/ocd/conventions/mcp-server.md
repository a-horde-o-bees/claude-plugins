---
includes: "**/servers/*/__main__.py"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/conventions/ocd/python.md
---

# MCP Server Conventions

Tool design, server architecture, and data conventions for MCP servers exposed as plugin tools via FastMCP. Each server is a Python package under `servers/`; its MCP entry point is `__main__.py`. Library code and data-layer modules (`__init__.py`, `_db.py`, `_helpers.py`, etc.) in the same package are governed by general Python conventions, not this one.

## Tool Naming

Tool names follow `object_action` format — the domain object first, then the operation. Agents discover related tools by scanning for a shared prefix. Names map to the server's internal module structure: tools backed by `_governance.py` are prefixed `governance_`, tools backed by `_skills.py` are prefixed `skills_`.

Examples: `governance_match`, `governance_list`, `paths_get`, `skills_resolve` — not `list_governance`, `describe_path`, `resolve_skill`.

## Standardized Verbs

Servers that manage collections of records use a standard verb set. Each verb has fixed semantics — agents learn the pattern once and apply it across servers.

| Verb | Operation | Returns |
|------|-----------|---------|
| `add` | Create new entry | Created entry with assigned id |
| `list` | Retrieve collection metadata | Compact entries with `has_detail` flag, without content |
| `get` | Retrieve full entry | Complete entry including `detail_md` content |
| `search` | Find entries by pattern | Matching entries (regex across summary and detail) |
| `update` | Modify existing entry | Updated entry |
| `remove` | Delete entry | Confirmation |

Metadata operations (`list`, `search`) return compact representations — enough to identify and select. Full-read operations (`get`) include complete content. This separation prevents loading detail content the agent doesn't need.

### Domain-Specific Operations

When a server's domain requires operations that don't map to the standard verbs, use descriptive names that convey the operation's purpose. The `object_action` naming convention still applies — the operation name replaces a standard verb.

Examples from navigator: `governance_match` (match files to conventions), `governance_order` (topological sort), `skills_resolve` (locate a skill by name), `scope_analyze` (composite analysis across references, sizes, and governance). These are domain operations, not CRUD — they combine data or apply domain logic that doesn't reduce to add/get/update/remove.

A server may mix standard verbs with domain-specific operations. The friction server uses all six standard verbs plus `friction_systems_list` (aggregate view by system). Standard verbs handle the individual-record lifecycle; domain operations handle cross-cutting queries.

## Markdown Detail Storage

Servers that store entries with optional rich content use a two-tier pattern: a summary for scanning, and an optional markdown blob for detail.

| Field | Purpose | Present in |
|-------|---------|------------|
| `summary` | One-line description for scanning | All responses |
| `detail_md` | Optional markdown content for extended context | `get` responses only |
| `has_detail` | Boolean flag indicating detail_md exists | `list` responses |

This separation means `list` responses stay compact — the agent sees what exists and decides whether to `get` the full content.

Update behavior for `detail_md`: pass `None` to leave unchanged, pass empty string `""` to clear to null.

## Tool Descriptions

The tool description is the primary agent interface. An agent encountering the tool for the first time selects and uses it correctly from the description alone.

A description conveys:

- **What** the tool does — the operation, not the implementation
- **When** to choose this tool — disambiguation from similar tools
- **What input means** — parameter semantics beyond what the schema type conveys
- **What output contains** — structure and interpretation of the response

Descriptions do not repeat the schema (agents see both) or document internal behavior.

## Input Design

- Typed JSON Schema with explicit `required` and `properties` — schema enforces validity, not runtime checks
- Accept structured input (arrays, objects) for batch operations — avoid multiple round-trips for data the caller already has
- Optional parameters have meaningful defaults; implicit behavior that changes output shape requires documentation in the description

## Output Design

- Structured JSON — dicts and arrays, never formatted text. The caller is always an agent; formatting for human display is the caller's responsibility, not the tool's
- Consistent response envelope within a server — success and error responses follow the same structure so agents parse uniformly
- Business logic returns structured data; CLI presentation formats it for display; MCP returns it as-is
- Process data in the tool, return only what the agent needs — filter, aggregate, and format in the tool; the agent consumes the result, not raw data
- When operations naturally co-occur, a composite tool returning combined results is preferred over requiring multiple round-trips — one call returning a files-with-metadata matrix is better than separate calls for files, sizes, and governance

## Error Handling

Two levels, following MCP protocol:

- **Protocol errors** — unknown tool, invalid arguments — handled by the framework
- **Tool execution errors** — returned in the response with `isError` semantics; include what went wrong and what to do next so the agent self-corrects without user intervention

Specific patterns:

- Prerequisite checks before operation (missing database, uninitialized state) return corrective action guidance, not just failure description
- Constraint violations return the constraint expression dynamically — not hardcoded per-field messages
- Invalid input errors describe what was expected, not just what was received

## Granularity

- **Domain tools over generic endpoints** — each tool encodes one meaningful operation on one concept; no generic query builders, raw mutation endpoints, or parameter-driven dispatch that requires the caller to know internals
- **Composite tools for common multi-step patterns** — when callers routinely need results from multiple operations together, combine into one tool that handles composition deterministically; the tool does the joining, not the agent
- **Keep the tool set navigable** — every tool in an MCP server loads into the agent's context window; the `object_action` naming convention provides natural grouping via prefix

## Discovery

The `object_action` naming convention is the primary discovery mechanism — agents scan tool prefixes to find related operations. For servers where naming alone is sufficient (roughly under 20 tools), no additional discovery infrastructure is needed.

When a server's tool count grows beyond what an agent can scan in one `tools/list` response, add a `help` discovery tool:

- No args → returns tool groups with one-line descriptions per group
- With group arg → returns tools in that group with descriptions and parameter summaries

The threshold is a judgment call, not a hard number. Signs it's needed: agents repeatedly call the wrong tool, or fail to find tools they need. The alternative to a discovery tool is restructuring into multiple focused servers — prefer this when groups have genuinely independent concerns.

## Server Instructions

The MCP server's `instructions` field provides server-level guidance that complements per-tool descriptions. Where tool descriptions cover what an individual tool does and when to choose it, server instructions cover the server's overall positioning — the category of tasks it handles, when to reach for this server's tools at all, and how the server fits alongside other tools (built-in or other servers).

A server instructions field conveys:

- **Category** — what kinds of tasks this server is for
- **Reach trigger** — situations where the agent should reach for this server's tools
- **Cross-tool positioning** — when to prefer this server's tools over alternatives (built-in tools, other servers, manual approaches)
- **High-level mental model** — the conceptual frame the agent needs to use the server effectively

Server instructions are not the place for per-tool details, parameter schemas, or implementation specifics — those live in individual tool descriptions. Server instructions are higher-altitude: they orient the agent so the agent knows which server to reach for, after which the tool descriptions take over.

Loaded by Claude Code at server connection time and available throughout the session. Truncated at 2KB, so prioritize the most important orientation information first.

Cross-tool positioning that publishes "when to reach for this server" belongs in the `instructions` field, not in a separate rule file or external document. Rules and external docs do not republish what an MCP server can self-publish through its protocol-level metadata.

## Server Architecture

- Business logic separated from server presentation — the server file dispatches to domain modules; tool handlers are thin wrappers that validate, delegate, and format
- The server is a presentation layer — the same functions are callable from CLI, tests, or other code paths
- Database paths and configuration via environment variables, not hardcoded paths
- Server module docstring states the server's domain scope and transport

## Server-Skill Composition

MCP server files are thin presentation layers; business logic lives in skill packages, not in the server file or its siblings. The skill package owns the domain (database, parsing, file I/O, decision logic); the server file owns the MCP exposure (tool decorators, structured serialization, error wrapping).

Standard structure for an MCP server:

```
plugins/<plugin>/
├── skills/
│   └── <name>/                  ← Business logic as a Python package
│       ├── __init__.py          ← Facade — public functions the server calls
│       ├── _db.py               ← Internal modules per python.md decomposition
│       ├── _store.py
│       └── (other internals)
└── servers/
    └── <name>.py                ← Thin MCP server: FastMCP setup + tool decorators
```

The server file:

- Imports the skill's public functions: `from skills.<name> import describe, list_entries, ...`
- Defines `mcp = FastMCP("<plugin>-<name>", instructions="...")` with cross-tool positioning
- Decorates thin wrappers with `@mcp.tool()` — each wrapper validates, delegates to a skill function, and serializes the result
- Handles JSON in/out and error wrapping via shared helpers (see *Shared Server Helpers* below)

**Anti-pattern:** business logic in the server file directly, or in sibling `_*.py` files inside `servers/`. This couples MCP exposure to business logic and prevents the skill from being callable from CLI, tests, or other code paths. Skills must remain independently consumable.

## Server Launching

Server files are launched via the plugin's `run.py` module launcher, which establishes proper `__package__` context via `runpy.run_module()`. The launcher handles sys.path bootstrap once, in one place — server files do not manipulate `sys.path` themselves.

`.mcp.json` invocation pattern:

```json
"<plugin>-<name>": {
  "command": "${CLAUDE_PLUGIN_DATA}/venv/bin/python3",
  "args": ["${CLAUDE_PLUGIN_ROOT}/run.py", "servers.<name>"]
}
```

For this to work:

- `servers/` must be a proper Python package (contain `__init__.py`)
- Server files use clean imports: `from . import _helpers`, `from skills.<name> import ...`
- No `sys.path` manipulation in individual server files (per `python.md`)

The launcher pattern is documented in `python.md` Import Pattern section; this convention specifies its application to MCP servers.

## Shared Server Helpers

Shared utility functions used by multiple server files in the same plugin live in `servers/_helpers.py` per `python.md`'s `_helpers.py` standard internal module type. Standard helpers:

- `_ok(result)` — serialize a successful result as a JSON string
- `_err(e)` — wrap an exception as a JSON error response

Server files import these via the package: `from . import _helpers` or `from ._helpers import _ok, _err`.

Project, plugin, and plugin-data paths resolve through the plugin framework helpers (`plugin.get_project_dir()`, `plugin.get_plugin_root()`, `plugin.get_plugin_data_dir()`) — see `python.md` *Project, Plugin, and Data Directory Resolution*. Servers do not define their own project-root helpers.

### MCP Subprocess Environment Bootstrap

Claude Code launches MCP servers with cwd set to the project root but does not propagate `CLAUDE_PROJECT_DIR` to the subprocess environment. Variable references inside `.mcp.json` env block values are not expanded — the literal string `${CLAUDE_PROJECT_DIR}` passes through unchanged, which corrupts path resolution silently (writes land in a directory literally named `${CLAUDE_PROJECT_DIR}` under cwd).

The servers package bootstraps `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at import time (in `servers/_helpers.py`) when the variable is missing. This is the only place in the codebase permitted to derive the project directory from cwd — the exception is safe because the MCP-server cwd is a Claude Code launch-time contract, not a user-influenced working directory. Code running outside the MCP subprocess (hooks, CLI, tests) must continue to set `CLAUDE_PROJECT_DIR` explicitly.

## Relational Data Storage

Servers that need persistent storage for relational data use SQLite with WAL mode for concurrent access. This is not a mandate for all servers — only those whose domain involves structured records with relationships.

### Aggregate Star Schema

Relational MCP databases follow the aggregate star schema pattern — star schema structure with ownership-based cascade behavior.

- **Root table** — central entity; other tables join to it via foreign keys
- **Satellite tables** — child records that belong to a root record
- **Junction tables** — many-to-many relationships; owned by both sides

Every foreign key implies ownership. The root record and all reachable children form an **aggregate** — a consistency boundary where no orphans may exist outside it.

### Cascade Behavior

Child-record cleanup is declared in the schema, not performed in code. Every foreign key pointing at an owning row is declared with `ON DELETE CASCADE`. A delete against a root row then walks the ownership tree automatically — the remove operation's Python code is a single `DELETE FROM root WHERE id = ?`, and SQLite removes every reachable child.

SQLite ships with foreign-key enforcement **off by default**. Every connection factory that opens a database with foreign keys must enable it explicitly:

```python
def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
```

`PRAGMA foreign_keys` is per-connection, not per-database — it must run on every connection open, not once at schema creation. Without it, `ON DELETE CASCADE` clauses are silently ignored: deletes succeed, children are orphaned, and no error surfaces until a later query trips over the dangling rows. Cascade correctness is a connection-factory property as much as a schema property.

### Schema Conventions

- Root table primary key: `TEXT` (formatted prefix + number) or `INTEGER PRIMARY KEY AUTOINCREMENT`
- Foreign keys: non-nullable, declared with `ON DELETE CASCADE` to the owning row
- Composite primary keys on satellite tables where natural key exists
- CHECK constraints enforce valid values for enum-like fields

### Aggregate-Aware Tools

Tools operate within aggregate boundaries. A tool that modifies a satellite record understands its relationship to the root — validation and consistency checks are tool responsibilities, not caller responsibilities. Cascade on delete is a schema responsibility, not a tool responsibility; tools should not walk aggregates manually to delete children.

Registration and mutation tools accept arrays for batch processing. The tool handles per-item dedup, validation, and error collection internally — the caller provides the batch, the tool returns per-item results.
