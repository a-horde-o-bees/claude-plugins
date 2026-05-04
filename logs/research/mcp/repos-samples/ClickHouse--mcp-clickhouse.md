# Sample

Mirrors of `https://github.com/ClickHouse/mcp-clickhouse`. ClickHouse MCP server — runs SQL, lists databases/tables, and queries an embedded chDB engine against ClickHouse clusters. 757 stars, Apache-2.0, default branch `main`, 71 commits.

## Server runtime

### Python with FastMCP

Python (98.7%) on FastMCP 2.x — `fastmcp>=2.0.0,<3.0.0` in pyproject.toml. `fastmcp.json` present for FastMCP-native config. `requires-python = ">=3.10"`. Tool signatures appear synchronous (`def`) in README examples; FastMCP handles the async boundary.

## Transport

### stdio

Default transport.

### Streamable HTTP

Selectable via `CLICKHOUSE_MCP_SERVER_TRANSPORT=http`.

### SSE (Server-Sent Events)

Selectable via `CLICKHOUSE_MCP_SERVER_TRANSPORT=sse`.

### Selection mechanism

Environment variable — `CLICKHOUSE_MCP_SERVER_TRANSPORT=stdio|http|sse`.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Tools — `run_query` (SQL), `list_databases`, `list_tables` (paginated, filterable), `run_chdb_select_query` (against embedded chDB). Resources/prompts not listed explicitly. Paginated/filtered `list_tables` is a deliberate scalability axis.

### Capability gating flags (per-tool, per-category, write-mode)

`CLICKHOUSE_ALLOW_WRITE_ACCESS` and a separate `CLICKHOUSE_ALLOW_DROP` env var gate destructive operations in two steps. Read-only default at both MCP-layer and SQL-layer (`readonly=1` setting).

## Configuration delivery

### Environment variables

`CLICKHOUSE_HOST`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD` (required); `CLICKHOUSE_SECURE`, `CLICKHOUSE_VERIFY` (TLS); `CLICKHOUSE_MCP_SERVER_TRANSPORT`; `CLICKHOUSE_ALLOW_WRITE_ACCESS`, `CLICKHOUSE_ALLOW_DROP`; `CLICKHOUSE_MCP_AUTH_TOKEN`, `CLICKHOUSE_MCP_AUTH_DISABLED`; `CHDB_ENABLED`, `CHDB_DATA_PATH`; `MCP_MIDDLEWARE_MODULE`.

### Framework-native config file

`fastmcp.json` for FastMCP-level config alongside the env-var surface.

## Authentication

### None / implicit (local-resource gating)

stdio mode requires no auth — process boundary is the trust boundary.

### Bearer token over HTTP/SSE

HTTP/SSE require a bearer token, generated via `uuidgen` or `openssl` and supplied via `CLICKHOUSE_MCP_AUTH_TOKEN`. Dev-mode override via `CLICKHOUSE_MCP_AUTH_DISABLED=true` lets authors run unauthenticated locally without code changes.

### Database connection string

ClickHouse credentials supplied via env vars (`CLICKHOUSE_HOST`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`).

## Multi-tenancy

### Per-request tenancy via middleware

HTTP-mode server allows per-request connection overrides through middleware-managed context state — incoming request can carry connection settings via `CLIENT_CONFIG_OVERRIDES_KEY` in context state. Closest the corpus comes to true multi-tenancy among DB MCP servers.

## Distribution channel

### PyPI via pip / pipx

Published to PyPI as `mcp-clickhouse`. `pip install mcp-clickhouse`; optional `[chdb]` extra (`pip install 'mcp-clickhouse[chdb]'`) swaps in embedded analytics engine.

### PyPI via uvx (zero-install runner)

`uv run --with mcp-clickhouse --python 3.10 mcp-clickhouse` documented as the recommended one-liner with on-demand install and pinned Python.

### Docker / OCI image

Dockerfile present for containerized deployment.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `mcp-clickhouse = "mcp_clickhouse.main:main"`. README host-config snippet: `"command": "uv"`, `"args": ["run", "--with", "mcp-clickhouse", "--python", "3.10", "mcp-clickhouse"]`.

### Module invocation / `python -m <module>` fallback

`python3 -m mcp_clickhouse.main` shown as alternative invocation.

## Build and packaging

### Hatchling + uv (Python)

Build backend: `hatchling.build`. uv-managed (uv.lock likely).

### Optional-dependency fan-out

Optional `[chdb]` extra swaps in embedded chDB engine — cleanly separates the two analytics backends via Python extras.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP-style auto-derived schema from Python signatures.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile at repo root.

### Docker-Compose backend for end-to-end tests

`test-services/` Docker Compose spins up a ClickHouse instance for integration tests.

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio in dev extras. Tests under `tests/` with separate suites for ClickHouse (`test_tool.py`) and chDB (`test_chdb_tool.py`). Fixture style uses Docker Compose-backed integration services (`test-services/`) alongside unit tests.

## CI

### GitHub Actions

`.github/workflows/` present; specifics not extracted.

## Host integration

### Claude Desktop

Standard MCP `mcpServers` config snippet expected; integration details less emphasized in the README than the runtime config surface.

## Observability

### Request lifecycle hooks for telemetry

Example middleware (`example_middleware.py`) demonstrates request logging, tool-call tracking, and performance measurement — extensibility shape rather than fixed observability.

## Repository layout

### Single-package src-layout

Single-package Python — `mcp_clickhouse/`, `tests/`, `test-services/`, `.github/workflows/`, `fastmcp.json`, `pyproject.toml`.

## Safety and security posture

### Progressive trust gating

`CLICKHOUSE_ALLOW_WRITE_ACCESS` plus a separate `CLICKHOUSE_ALLOW_DROP` gate destructive operations in two steps — finer-grained than the binary read-only knob common elsewhere.

## Extension points

### Middleware module slot

`MCP_MIDDLEWARE_MODULE` env var loads a user-authored Python module that intercepts FastMCP protocol events (tool calls, resource reads, prompts, listings) and can mutate context state (e.g., per-request connection overrides) or implement cross-cutting concerns. The closest thing in the corpus to a true plugin architecture for an MCP server.

### Sample example middleware

`example_middleware.py` demonstrates how to extend the server via a configured middleware module — both documentation and a test of the middleware extension point.

## Developer ergonomics

### MCP framework dev config

`fastmcp.json` in repo for FastMCP-native dev config.

### Linter and type-checker stack

ruff configured (line-length 100). No Makefile observed.

### Sample example middleware

`example_middleware.py` demonstrates middleware extension.

## Documentation surface

### README as the canonical surface

README.md carrying purpose, install, config; host-integration examples less prominent than runtime config.
