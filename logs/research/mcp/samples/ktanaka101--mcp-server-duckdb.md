# Sample

## Identification

### url

https://github.com/ktanaka101/mcp-server-duckdb

### stars

174

### last-commit

May 5, 2025 (v1.1.0)

### license

MIT

### default branch

main

### one-line purpose

DuckDB MCP server — SQL query execution against DuckDB files.

## Language and runtime

### language(s) + version constraints

Python (100%)

### framework/SDK in use

Anthropic MCP Python SDK

## Transport

### supported transports

stdio (standard MCP)

### how selected

Implicit — stdio is the only transport documented

## Distribution

### every mechanism observed

PyPI, uvx runner, Smithery registry

### published package name(s)

mcp-server-duckdb

### install commands shown in README

`npx -y @smithery/cli install mcp-server-duckdb --client claude`; `uvx mcp-server-duckdb --db-path <path>`

### pitfalls observed

No container or Homebrew artifacts observed

## Entry point / launch

### command(s) users/hosts run

`uvx mcp-server-duckdb --db-path <path> [--readonly] [--keep-connection]`

### wrapper scripts, launchers, stubs

CLI entry point registered via package metadata; Smithery installer handles host registration

## Configuration surface

### how config reaches the server

CLI flags only — `--db-path` (required), `--readonly`, `--keep-connection`. No env vars or config files documented.

## Authentication

### flow

None — local DuckDB file access

### where credentials come from

Not applicable

## Multi-tenancy

### tenancy model

Single-user, single-database — one DuckDB file per server instance

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Single tool — `query` (accepts arbitrary SQL). No resources, prompts, sampling, or roots.

## Observability

### logging destination + format, metrics, tracing, debug flags

None in README; MCP Inspector recommended for debugging

## Host integrations shown in README or repo

### Claude Desktop

Supported via `claude_desktop_config.json` example

### Smithery

Supported via its CLI installer

## Claude Code plugin wrapper

### presence and shape

Not present

## Tests

### presence, framework, location, notable patterns

`tests/` directory present; framework not specified within fetch budget

## CI

### presence, system, triggers, what it runs

`.github/workflows/` present; specific workflow contents not extracted within budget

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

None documented

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

MCP Inspector recommended; Claude Desktop JSON config shown; Smithery CLI recipe

## Repo layout

### single-package / monorepo / vendored / other

Single-package Python project

## Notable structural choices

Single generic `query` tool delegates SQL generation entirely to the LLM rather than providing specialized tools. Read-only mode leverages DuckDB's native protection, not tool-layer validation. `--keep-connection` flag is explicit to enable TEMP objects across calls — a deliberate session-state trade-off. Non-readonly mode auto-creates the DB file and parent directories.

## Unanticipated axes observed

Connection-lifecycle flag (`--keep-connection`) as a first-class knob — a design choice most servers hide.

## Python-specific

### SDK / framework variant

Raw `mcp` Python SDK — `mcp>=1.0.0`; no fastmcp. Import pattern: low-level MCP server API (inferred).

### Python version floor

`requires-python = ">=3.10"`

### Packaging

Build backend: `hatchling.build`. Lock file: likely uv.lock (uv/uvx ecosystem). Version manager convention: `uv`/`uvx`.

### Entry point

`[project.scripts]`: `mcp-server-duckdb = "mcp_server_duckdb:main"`. README host-config snippet: `"command": "uvx"`, `"args": ["mcp-server-duckdb", "--db-path", "<path>"]`.

### Install workflow expected of end users

`uvx mcp-server-duckdb` (primary), Smithery CLI installer for host setup. No pip instructions shown.

### Async and tool signatures

`pytest>=8.3.4` in dev deps; pytest-asyncio not declared. Source not inspected.

### Type / schema strategy

Low-level MCP SDK — hand-authored schemas

### Testing

pytest in dev deps; `tests/` directory. No pytest config in pyproject.toml.

### Dev ergonomics

README recommends MCP Inspector (`npx @modelcontextprotocol/inspector`). No Makefile/task runner observed.

### Notable Python-specific choices

Minimal pyproject.toml — only pytest in dev; no ruff/mypy/coverage. Single-tool server, low ceremony — pragmatic Python layout.

## Gaps

Test framework and CI workflow specifics not extracted within budget. No container or Homebrew artifacts observed.
