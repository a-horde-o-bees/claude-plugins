# Sample

Mirrors of `https://github.com/ktanaka101/mcp-server-duckdb`. DuckDB MCP server — single generic `query` tool executing arbitrary SQL against a local DuckDB file. 174 stars, MIT, default branch `main`, last commit May 5, 2025 (v1.1.0).

## Server runtime

### Python with raw MCP SDK

Python 100% server using the raw Anthropic MCP Python SDK (`mcp>=1.0.0`); no FastMCP. Low-level MCP server API (inferred). `requires-python = ">=3.10"`.

## Transport

### stdio

Implicit — stdio is the only transport documented; no transport selection mechanism.

## Capability surface

### Single generic tool

One tool — `query` — accepting arbitrary SQL. Delegates SQL generation entirely to the LLM rather than providing specialized tools. No resources, prompts, sampling, or roots.

## Configuration delivery

### CLI flags

Configuration only via CLI flags — `--db-path` (required), `--readonly`, `--keep-connection`. No env vars or config files documented.

## Authentication

### None / implicit (local-resource gating)

No authentication; local DuckDB file access only.

## Multi-tenancy

### Single-user / single-tenant per process

One DuckDB file per server instance.

### Connection-lifecycle as a knob

`--keep-connection` flag is explicit to enable TEMP objects across calls — a deliberate session-state trade-off. Persistent connections enable cross-call state but break the stateless-per-request model.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published as `mcp-server-duckdb` on PyPI; canonical README install: `uvx mcp-server-duckdb --db-path <path>`. README host-config snippet: `"command": "uvx"`, `"args": ["mcp-server-duckdb", "--db-path", "<path>"]`. No pip instructions shown.

### Smithery registry

Smithery CLI installer recipe documented: `npx -y @smithery/cli install mcp-server-duckdb --client claude`.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `mcp-server-duckdb = "mcp_server_duckdb:main"`.

### `uvx <package>`

Canonical launch via `uvx mcp-server-duckdb --db-path <path> [--readonly] [--keep-connection]`.

## Build and packaging

### Hatchling + uv (Python)

Build backend `hatchling.build`. uv/uvx ecosystem. Lock file likely `uv.lock`.

### Pin discipline (Python)

Loose pin `mcp>=1.0.0` — minimal-ceremony posture. Minimal pyproject.toml — only pytest in dev; no ruff/mypy/coverage.

## Schema and types

### Hand-authored tool schemas

Raw `mcp` SDK without FastMCP — tool handlers register an explicit input schema dict; author writes the schema directly.

## Test stack

### pytest with async + coverage

`pytest>=8.3.4` in dev deps; `tests/` directory present. No pytest config in pyproject.toml. pytest-asyncio not declared.

## CI

### GitHub Actions

`.github/workflows/` present; specific workflow contents not extracted within budget.

## Safety and security posture

### Read-only by default with explicit write flag

`--readonly` flag leverages DuckDB's native read-only protection rather than tool-layer validation. Non-readonly mode auto-creates the DB file and parent directories.

## Repository layout

### Single-package src-layout

Single-package Python project.

## Host integration

### Claude Desktop

Supported via `claude_desktop_config.json` example.

### Smithery / Glama discovery

Smithery CLI installer wires the host.

## Developer ergonomics

### Inspector/debug tooling references

README recommends MCP Inspector (`npx @modelcontextprotocol/inspector`). No Makefile/task runner observed.

## Release and lifecycle

### Active development

Last commit May 5, 2025 (v1.1.0).

### License — Permissive (MIT / Apache-2.0)

MIT.
