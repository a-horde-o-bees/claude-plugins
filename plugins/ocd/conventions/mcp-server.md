---
pattern: "servers/*.py"
depends:
  - .claude/rules/ocd-design-principles.md
  - .claude/conventions/python.md
---

# MCP Server Conventions

Tool design and server architecture conventions for MCP servers exposed as plugin tools via FastMCP. Applies to Python server files in `servers/` directories.

## Tool Naming

Tool names follow `object_action` format — the domain object first, then the operation. Agents discover related tools by scanning for a shared prefix. Names map to the server's internal module structure: tools backed by `_governance.py` are prefixed `governance_`, tools backed by `_skills.py` are prefixed `skills_`.

Examples: `governance_match`, `governance_list`, `paths_get`, `skills_resolve` — not `list_governance`, `describe_path`, `resolve_skill`.

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

Project-root resolution helpers (e.g., `_project_root()` reading `CLAUDE_PROJECT_DIR` with fallback to cwd) live in `_helpers.py` when used by more than one server.
