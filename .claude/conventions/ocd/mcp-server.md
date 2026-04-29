---
includes: "**/systems/*/server.py"
governed_by:
  - .claude/rules/ocd/design-principles.md
  - .claude/conventions/ocd/python.md
---

# MCP Server Conventions

Tool design, server architecture, and data conventions for MCP servers exposed as plugin tools via FastMCP. Each server is a single module under `systems/<name>/server.py` that imports a domain library from `systems/<name>/` and exposes its functions as MCP tools. Library code (e.g., facades, internal modules, CLIs) under `systems/<name>/` is governed by general Python conventions, not this one.

## Tool Naming

Tool names follow `object_action` format — the domain object first, then the operation. Agents discover related tools by scanning for a shared prefix. Names map to the server's internal module structure: tools backed by `_skills.py` are prefixed `skills_`, tools backed by `_references.py` are prefixed `references_`.

Examples: `paths_query`, `paths_upsert`, `skills_query`, `governance_match`.

The CLI counterpart for each MCP tool uses the same name with the underscore replaced by a space (e.g. `paths_query` ↔ `paths query`). See `cli.md` for the noun-verb hierarchy that flows from this alignment.

## Standardized Verbs

Reads use a single verb per concept. Writes split by operation semantics. Each verb has fixed semantics — agents learn the pattern once and apply it across servers.

### Read verb

| Verb | Operation |
|------|-----------|
| `query` | All retrieval — primary key lookup, enumeration, structural filter, text/keyword search. Input mode is selected by parameters; the tool dispatches internally. See *Input Mode Parameters*. |

One read tool per concept covers every retrieval shape. Splitting reads into separate tools per input mode (`get`, `list`, `search`) fragments the agent's tool surface without semantic gain — the input distinction is an implementation concern, not a tool-selection concern.

### Write verbs

| Verb | Operation | Returns |
|------|-----------|---------|
| `upsert` | Create or update an entry by primary key | Created/updated entry |
| `set` | Replace a value (scalar or whole collection) | Stored value |
| `update` | Mutate fields on existing entry; supports multiple changes per call (e.g. set + clear in one transaction) | Per-field results |
| `clear` | Null out a value while preserving the row (for annotation columns) | List of cleared keys |
| `remove` | Delete an entry | Confirmation |

Multiple write verbs per concept are normal — different mutation semantics deserve different tools. `set` replaces; `update` mutates; `clear` nulls; `remove` deletes; `upsert` creates-or-updates. Collapsing these into a single tool with a `mode=` flag is a footgun — the agent loses the clear semantic boundary between "I'm changing this" and "I'm deleting this," and review/safety differ across these intents.

### Domain-specific operations

When a concept's domain requires operations that don't reduce to query/upsert/set/update/clear/remove, use descriptive names that convey the operation's purpose. The `object_action` naming convention still applies — the operation name replaces a standard verb.

Examples: `paths_undescribed` (deepest dir with undescribed children), `references_map` (build reference DAG from input paths), `scope_analyze` (composite of references + sizes + governance), `governance_order` (topological sort), `schema_describe` (live schema introspection). These are domain operations encoding business logic that doesn't fit standard CRUD.

A server may mix standard verbs with domain-specific operations. Standard verbs handle the individual-record lifecycle; domain operations handle composites and cross-cutting queries.

## Input Mode Parameters

The unified `_query` tool absorbs multiple retrieval modes via optional parameters. The convention:

| Input | Purpose | Example |
|-------|---------|---------|
| Primary key list | PK lookup (1 or more) | `paths=["a/b", "c/d"]` |
| Scope + structural filters | Enumeration restricted to scope | `target_path=".", patterns=["*.py"]` |
| Filter criteria | Structural query by typed fields | `project="X", from_ts="2026-01-01"` |
| Text/keyword | Substring or fuzzy match | `text="authentication"` |

Multiple inputs may combine within one call. The tool description must specify precedence when modes overlap (e.g. does `paths=[...]` filter the named paths or override a `text=...` match?). Mutex inputs that don't compose meaningfully should error rather than silently pick one.

Output verbosity is controlled via a `show` parameter — a list of opt-in field buckets. Default output is lean (small, fast, common case); the agent opts into heavier or domain-specific fields when needed.

| Pattern | Example |
|---------|---------|
| Default lean output | `sessions_query()` returns `{project, session, n_exchanges, n_purposed}` |
| Opt-in detail | `sessions_query(show=["timeframes", "bytes"])` adds `first_ts`, `last_ts`, `bytes` |
| Multiple buckets union | `exchanges_query(show=["messages", "metrics"])` adds chat content + full metric hierarchy |
| Hierarchical buckets | `exchanges_query(show=["breakdown"])` adds `active_s` + `user_s` + `agent_s`; `["metrics"]` is the superset adding `total_s` + `idle_s` |

Bucket names are validated against an allowed set; unknown values raise a validation error. The bucket vocabulary is documented in the tool description and discoverable via tool introspection. See `transcripts/server.py` for the canonical example.

## Markdown Detail Storage

Servers that store entries with optional rich content use a two-tier pattern: a summary for scanning, and an optional markdown blob for detail. Delivered through the unified `_query` tool with an opt-in `show` bucket — not through separate read tools.

| Field | Purpose | Present in |
|-------|---------|------------|
| `summary` | One-line description for scanning | All `_query` responses |
| `detail_md` | Optional markdown content for extended context | `_query` responses when `show=["detail"]` |
| `has_detail` | Boolean flag indicating `detail_md` exists | All `_query` responses (so the agent knows when to opt in) |

This separation means default `_query` responses stay compact — the agent sees what exists and `has_detail` signals when to add `show=["detail"]` for the full content.

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
- Optional parameters carry meaningful defaults — callers should be able to invoke without the parameter and get sensible behavior
- When an optional parameter changes output shape or behavior, document the change in the tool description — agents cannot infer shape-shifting defaults from the schema alone

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

Domain libraries live under `systems/<name>/`; MCP servers live under `systems/<name>/server.py` as thin adapter modules that import from `systems/<name>/` and expose functions as MCP tools. One library can be consumed by its own CLI, by test suites, by other packages, and by an MCP server — the server is one presentation among several, not the home of the domain logic.

- Library owns business logic; server module dispatches tool wrappers to library functions
- Server module is a presentation layer — no business logic, no database schema, no file I/O beyond what tool serialization requires
- Database paths and configuration via environment variables, not hardcoded paths
- Server module docstring states the server's domain scope and transport

### Library and Tool Naming Are Independent

Library function names do not need to mirror MCP tool names 1:1. The mapping is many-to-many:

- One library function may back multiple MCP tools (e.g. a single `_scope.exchanges()` consumed by both a curated `exchanges_query` tool and a future analytics tool)
- One MCP tool may compose multiple library functions (e.g. `scope_analyze` calls `references_map`, file-size helpers, and `governance_match` and assembles the result)

Library function names follow Python ergonomics — the names that read naturally inside the package and at call sites. MCP tool names follow `object_action` for agent-facing discoverability. The two conventions are independent because they serve different consumers (Python callers vs agent tool selection).

When reading per-target rectification work, treat the library and MCP surfaces as parallel renames to evaluate, not a single coupled rename. Caller fan-in (who else calls this library function?) governs whether a library rename is even needed when the MCP tool renames.

## Server and Library Layout

Each MCP server is a single Python module under `systems/<name>/server.py`. The domain library it exposes is a separate package under `systems/<name>/`.

Standard structure:

```
plugins/<plugin>/
└── systems/
    └── <name>/                  ← System directory — library + MCP server + skill colocated
        ├── __init__.py          ← Facade — public functions (business logic)
        ├── __main__.py          ← Operational CLI
        ├── server.py            ← Thin MCP adapter — FastMCP setup + tool decorators
        ├── _server_helpers.py   ← Shared MCP response helpers and subprocess env bootstrap
        ├── _db.py               ← Internal modules per python.md decomposition
        └── (SKILL.md, other internals, tests)
```

The MCP adapter module (`systems/<name>/server.py`):

- Imports the library as a namespace: `import systems.<name> as _<short>` — the underscore-prefixed alias signals a private reference and avoids name collisions between tool wrapper functions and library functions (both share names because FastMCP derives the tool name from the function name)
- Imports shared helpers: `from ._server_helpers import _ok, _err`
- Defines `mcp = FastMCP("<name>", instructions="...")` with cross-tool positioning
- Decorates thin wrappers with `@mcp.tool()` — each wrapper validates, delegates to a library function, and serializes the result
- Ends with `if __name__ == "__main__": mcp.run()` so the module is launchable

The library (`systems/<name>/__init__.py`) owns all business logic — database operations, parsing, file I/O, decision logic. The MCP adapter is a thin presentation layer. The same functions are callable from the library's CLI (`systems/<name>/__main__.py`), tests, or any other code path.

## Server Launching

Server modules are launched via the plugin's `run.py` module launcher, which establishes proper `__package__` context via `runpy.run_module()`. The launcher handles sys.path bootstrap once, in one place — server modules do not manipulate `sys.path` themselves.

`.mcp.json` invocation pattern:

```json
"<name>": {
  "command": "${CLAUDE_PLUGIN_DATA}/venv/bin/python3",
  "args": ["${CLAUDE_PLUGIN_ROOT}/run.py", "systems.<name>.server"]
}
```

For this to work:

- `systems/<name>/` must be a proper Python package (contain `__init__.py`)
- Server modules use clean imports: `import systems.<name> as _<short>`, `from ._server_helpers import _ok, _err`
- No `sys.path` manipulation in individual server modules (per `python.md`)

The launcher pattern is documented in `python.md` Import Pattern section; this convention specifies its application to MCP servers.

## Shared Server Helpers

Shared utility functions used by multiple server modules in the same plugin live in `systems/navigator/_server_helpers.py` per `python.md`'s `_helpers.py` standard internal module type. Standard helpers:

- `_ok(result)` — serialize a successful result as a JSON string
- `_err(e)` — wrap an exception as a JSON error response

Server modules import these from the system package: `from ._server_helpers import _ok, _err`.

Project, plugin, and plugin-data paths resolve through the plugin framework helpers (`plugin.get_project_dir()`, `plugin.get_plugin_root()`, `plugin.get_plugin_data_dir()`) — see `python.md` *Project, Plugin, and Data Directory Resolution*. Servers do not define their own project-root helpers.

### MCP Subprocess Environment Bootstrap

**Problem.** Claude Code launches MCP servers with cwd set to the project root but does not propagate `CLAUDE_PROJECT_DIR` to the subprocess environment. Variable references inside `.mcp.json` env block values are not expanded — the literal string `${CLAUDE_PROJECT_DIR}` passes through unchanged, which corrupts path resolution silently (writes land in a directory literally named `${CLAUDE_PROJECT_DIR}` under cwd).

**Bootstrap location.** The servers package bootstraps `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at import time in `systems/navigator/_server_helpers.py` when the variable is missing. Every server module imports `_helpers` (for `_ok`/`_err`), so the bootstrap fires at process start.

**Cwd-derived fallback is MCP-subprocess-only.** `systems/navigator/_server_helpers.py` is the only place in the codebase permitted to derive the project directory from cwd. The exception is safe because MCP-server cwd is a Claude Code launch-time contract, not a user-influenced working directory.

**Non-MCP contexts set `CLAUDE_PROJECT_DIR` explicitly.** Hooks, CLI invocations, and tests must set the variable through their own entry points (e.g., test fixtures, hook wrapper scripts, shell environment). No cwd fallback applies outside the MCP subprocess.

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

**Scope — tools operate within aggregate boundaries.** A tool that modifies a satellite record knows which aggregate it belongs to; cross-aggregate operations are distinct tools, not parameters.

**Validation is a tool responsibility.** A tool that writes a satellite record checks relationship constraints (foreign key exists, values pass CHECK constraints, aggregate invariants hold) before the write. Callers provide data; they do not pre-validate.

**Cascade-delete is a schema responsibility.** Tools do not walk aggregates to delete children — `ON DELETE CASCADE` in the schema owns that. A delete tool issues `DELETE FROM root WHERE id = ?` and lets SQLite remove reachable children.

**Batch-aware tool surface.** Registration and mutation tools accept arrays for batch processing. The tool handles per-item dedup, validation, and error collection internally — the caller provides the batch, the tool returns per-item results.
