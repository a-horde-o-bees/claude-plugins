# ClickHouse/mcp-clickhouse

## Identification
- url: https://github.com/ClickHouse/mcp-clickhouse
- stars: 757
- last-commit (date or relative): 71 commits on main; specific date not surfaced
- license: Apache-2.0
- default branch: main
- one-line purpose: ClickHouse MCP server — run SQL, list databases/tables, and query an embedded chDB engine against ClickHouse clusters.

## 1. Language and runtime
- language(s) + version constraints: Python (98.7%); uv-managed
- framework/SDK in use: FastMCP (MCP Server SDK)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default), HTTP, SSE
- how selected (flag, env, separate entry, auto-detect, etc.): `CLICKHOUSE_MCP_SERVER_TRANSPORT` env var (stdio/http/sse)
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI (`mcp-clickhouse`, `mcp-clickhouse[chdb]` extra), Docker
- published package name(s): mcp-clickhouse
- install commands shown in README: `pip install mcp-clickhouse`; `pip install 'mcp-clickhouse[chdb]'`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `mcp-clickhouse` script or `python3 -m mcp_clickhouse.main`
- wrapper scripts, launchers, stubs: Dockerfile; `test-services/` Docker Compose for local dev
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Environment variables — `CLICKHOUSE_HOST`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD` (required); `CLICKHOUSE_SECURE`, `CLICKHOUSE_VERIFY` (TLS); `CLICKHOUSE_MCP_SERVER_TRANSPORT`; `CLICKHOUSE_ALLOW_WRITE_ACCESS`, `CLICKHOUSE_ALLOW_DROP`; `CLICKHOUSE_MCP_AUTH_TOKEN`, `CLICKHOUSE_MCP_AUTH_DISABLED`; `CHDB_ENABLED`, `CHDB_DATA_PATH`; `MCP_MIDDLEWARE_MODULE`. `fastmcp.json` for FastMCP-level config.
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: stdio — none. HTTP/SSE — bearer token required (generated via `uuidgen` or `openssl`). Dev override via `CLICKHOUSE_MCP_AUTH_DISABLED=true`.
- where credentials come from: `CLICKHOUSE_MCP_AUTH_TOKEN` env var; ClickHouse credentials also via env vars
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Per-request tenant possible — custom middleware can override connection settings per request via `CLIENT_CONFIG_OVERRIDES_KEY` in context state
- pitfalls observed:
  - Per-request connection overrides via middleware-managed context state — closest thing to multi-tenancy among DB MCP servers

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Tools — `run_query` (SQL), `list_databases`, `list_tables` (paginated, filterable), `run_chdb_select_query` (against embedded chDB). Resources/prompts not listed explicitly.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Example middleware (`example_middleware.py`) demonstrates request logging, tool-call tracking, performance measurement
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop: Standard MCP config expected
- Other editors/CLIs: Not enumerated in fetched content
- Integration details less emphasized than the runtime config surface
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: Not present
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: pytest; tests under `tests/` with separate suites for ClickHouse (`test_tool.py`) and chDB (`test_chdb_tool.py`); `test-services/` Docker Compose spins up a ClickHouse instance for integration tests
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions in `.github/workflows/`; specifics not extracted
- pitfalls observed:
  - CI workflow specifics not extracted

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile; `test-services/` Docker Compose for local test infra
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `example_middleware.py`, `test-services/`, `fastmcp.json`
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package Python — `mcp_clickhouse/`, `tests/`, `test-services/`, `.github/workflows/`, `fastmcp.json`, `pyproject.toml`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Dual-engine — standalone ClickHouse client and embedded chDB engine can run together
- Progressive trust: `CLICKHOUSE_ALLOW_WRITE_ACCESS` plus a separate `CLICKHOUSE_ALLOW_DROP` gate destructive operations in two steps
- Read-only default at both MCP-layer and SQL-layer (`readonly=1` setting)
- Middleware-first extensibility — `MCP_MIDDLEWARE_MODULE` lets users inject interceptors for tool calls, resource reads, prompts, listings without forking
- Per-request connection overrides via middleware-managed context state — closest thing to multi-tenancy among DB MCP servers
- Paginated/filtered `list_tables` — deliberate scalability axis absent from smaller servers

## 18. Unanticipated axes observed
- Middleware plugin system intercepting MCP protocol events is an unusual architectural axis — most MCP servers expose no such extension point
- Two-flag destructive-operation gating (`WRITE_ACCESS` + `DROP`) is more granular than typical read-only toggles
- Dual-engine chDB integration collapses "embedded analytics" and "server-backed analytics" into one MCP surface

## 19. Python-specific

### SDK / framework variant
- FastMCP 2.x — `fastmcp>=2.0.0,<3.0.0` in pyproject.toml
- Import pattern observed: via FastMCP server idiom (`fastmcp.json` also present for FastMCP-native config)

### Python version floor
- `requires-python = ">=3.10"`
- CI matrix not extracted

### Packaging
- build backend: `hatchling.build`
- lock file: uv.lock likely (uv-managed per Language section)
- version manager convention: `uv`

### Entry point
- `[project.scripts]`: `mcp-clickhouse = "mcp_clickhouse.main:main"`
- Console script: `mcp-clickhouse`
- README host-config snippet: `"command": "uv"`, `"args": ["run", "--with", "mcp-clickhouse", "--python", "3.10", "mcp-clickhouse"]` — uv-run with on-demand install, pinned Python; alternative `python3 -m mcp_clickhouse.main` also shown

### Install workflow expected of end users
- `uv run` (recommended), `pip install mcp-clickhouse`, optional `[chdb]` extra; Docker image
- One-liner: `uv run --with mcp-clickhouse --python 3.10 mcp-clickhouse`

### Async and tool signatures
- Tool signatures appear synchronous (`def`) in README examples; FastMCP handles the async boundary
- No explicit asyncio usage surfaced

### Type / schema strategy
- FastMCP-style auto-derived schema from Python signatures (inferred from FastMCP 2.x usage)

### Testing
- pytest + pytest-asyncio in dev extras
- Fixture style uses Docker Compose-backed integration services (`test-services/`) alongside unit tests

### Dev ergonomics
- `fastmcp.json` in repo for FastMCP-native dev config; `example_middleware.py` demonstrates middleware extension
- No Makefile observed; ruff configured (line-length 100)

### Notable Python-specific choices
- Middleware plugin slot — `MCP_MIDDLEWARE_MODULE` env var loads a user-authored Python module that intercepts FastMCP protocol events
- Optional extra `[chdb]` swaps in embedded chDB engine — cleanly separates the two analytics backends via Python extras

## 20. Gaps
- Last commit date not directly surfaced
- CI workflow specifics not extracted
- Host-integration (Claude Desktop/Cursor/VS Code) examples less prominent than runtime config in the README
