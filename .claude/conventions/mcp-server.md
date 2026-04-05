---
pattern: "servers/*.py"
depends:
  - .claude/rules/ocd-design-principles.md
  - .claude/conventions/python.md
---

# MCP Server Conventions

Tool design and server architecture conventions for MCP servers exposed as plugin tools via FastMCP. Applies to Python server files in `servers/` directories.

## Tool Naming

Tool names are verb-first and self-describing — the name alone conveys the operation without requiring the description. Names are scoped to their domain concept: `register_entity`, `get_coverage`, `map_references` — not `entity`, `data`, or `process`.

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

- Structured JSON responses — never unstructured prose the agent must parse
- Consistent response envelope within a server — success and error responses follow the same structure so agents parse uniformly
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
- **Keep the tool set navigable** — every tool in an MCP server loads into the agent's context window; if tool count grows beyond what an agent can scan, introduce a discovery mechanism or restructure into multiple focused servers

## Server Architecture

- Business logic separated from server presentation — the server file dispatches to domain modules; tool handlers are thin wrappers that validate, delegate, and format
- The server is a presentation layer — the same functions are callable from CLI, tests, or other code paths
- Database paths and configuration via environment variables, not hardcoded paths
- Server module docstring states the server's domain scope and transport
