# Sample

## Identification

### url

https://github.com/crystaldba/postgres-mcp

### stars

2.6k

### last-commit (date or relative)

v0.3.0 released May 16, 2025

### license

MIT

### default branch

main

### one-line purpose

PostgreSQL performance-tuning MCP server — SQL execution plus deterministic index optimization (hypopg simulation, Pareto selection, workload compression) and health analysis.

## 1. Language and runtime

### language(s) + version constraints

Python (98.4%); uv-managed

### framework/SDK in use

Anthropic MCP Python tooling; psycopg3 (async), pglast (SQL parsing), hypopg (index simulation), pg_stat_statements

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (default), SSE

### how selected (flag, env, separate entry, auto-detect, etc.)

`--transport=sse` flag

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI, Docker Hub (`crystaldba/postgres-mcp`), `uv run` from source, pipx

### published package name(s)

postgres-mcp

### install commands shown in README

`pipx install postgres-mcp`; `uv pip install postgres-mcp`; `docker pull crystaldba/postgres-mcp`; `uv run postgres-mcp <connection-string>`

### pitfalls observed

- Host-address auto-remapping in Docker image — quality-of-life packaging rarely seen

## 4. Entry point / launch

### command(s) users/hosts run

`postgres-mcp` with `DATABASE_URI` env var and optional `--access-mode` / `--transport` flags

### wrapper scripts, launchers, stubs

Dockerfile; devenv.* files for reproducible env

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

`DATABASE_URI` environment variable; CLI flags `--access-mode` (unrestricted/restricted) and `--transport`; MCP client JSON configs (Claude Desktop, Cursor, Windsurf, Goose, Qodo Gen)

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

PostgreSQL URI credentials; no additional auth layer; read-only mode enforced in-process via SQL parsing, not via DB-level permissions

### where credentials come from

`DATABASE_URI` env var

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

Single database connection per server instance; SSE transport lets multiple clients share one process but not separate tenancies

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools only (deliberate design choice per README) — `list_schemas`, `list_objects`, `get_object_details`, `execute_sql`, `explain_query`, `get_top_queries`, `analyze_workload_indexes`, `analyze_query_indexes`, `analyze_db_health`. No resources/prompts because "the MCP client ecosystem has widespread support for MCP tools."

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Not explicitly documented within budget

### pitfalls observed

- Logging/observability specifics not surfaced

## 10. Host integrations shown in README or repo

### Claude Desktop, Cursor, Windsurf, Goose, Qodo Gen

Config examples provided

### Cloud Postgres

AWS RDS, Azure SQL, Google Cloud SQL explicitly supported

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

Tests under `/tests`; README notes use of "AI-generated adversarial workloads"

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions workflows in `.github/workflows/`; specifics not extracted

### pitfalls observed

- Exact CI workflows not enumerated

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile auto-remaps host address (localhost → host.docker.internal on macOS/Windows, 172.17.0.1 on Linux)

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`examples/` directory (e.g., movie-app.md); devenv files for reproducible environments

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single-package Python — `src/postgres_mcp/`, `tests/`, `examples/`, `.github/workflows/`, Dockerfile, pyproject.toml

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Deterministic optimization algorithms (greedy search, adapted from Microsoft Anytime) rather than LLM-driven index recommendation
- Read-only enforcement via SQL parsing with pglast — rejects COMMIT/ROLLBACK in restricted mode
- Hypothetical indexing via hypopg extension — simulates index impact without creating real indexes
- Workload compression normalizes queries to shrink index-search space
- Pareto-front cost-benefit balancing between performance gains and storage overhead
- Optional OpenAI API integration for experimental LLM-based index tuning

## 18. Unanticipated axes observed
- Embedded performance-tuning intelligence (workload analysis, hypothetical indexing, Pareto selection) goes far beyond typical SQL-execution MCP servers
- Host-address auto-remapping in Docker image — quality-of-life packaging rarely seen
- Explicit rationale for "tools only, no resources/prompts" based on client ecosystem observations

## 19. Python-specific

### SDK / framework variant
- Raw `mcp` Python SDK — `mcp[cli]>=1.25.0` in dependencies; no fastmcp
- Import pattern: low-level MCP server API (inferred; not FastMCP-style)

### Python version floor
- `requires-python = ">=3.12"` — highest floor in the Python sample
- Ruff target-version intentionally lags at `py39` (style target), separate from runtime floor

### Packaging
- build backend: `hatchling.build`
- lock file: uv.lock (uv-managed per README `uv sync`)
- version manager convention: `uv`

### Entry point
- `[project.scripts]`: `postgres-mcp = "postgres_mcp:main"`
- README host-config snippets shown for four launch modes: `uvx postgres-mcp`, bare `postgres-mcp` (after pipx install), `uv run postgres-mcp`, and `docker run crystaldba/postgres-mcp`

### Install workflow expected of end users
- `pipx install postgres-mcp`, `uv pip install postgres-mcp`, `uvx postgres-mcp`, Docker `crystaldba/postgres-mcp`, or from-source `uv sync`

### Async and tool signatures
- Uses `mcp[cli]` low-level SDK; tool handlers are typically `async def` in this SDK variant (not confirmed at source level)
- `pytest-asyncio>=1.3.0` in dev deps confirms async test surface

### Type / schema strategy
- Low-level MCP SDK requires hand-authored schemas (vs FastMCP auto-derivation)
- Project uses pyright for strict typing (`pyright==1.1.408` pinned)

### Testing
- pytest + pytest-asyncio
- `asyncio_default_fixture_loop_scope = "function"` in pyproject pytest config
- `pythonpath = ["./src"]` — src-layout package

### Dev ergonomics
- devenv files mentioned in README for reproducible environments
- ruff + pyright pinned to exact versions (ruff==0.14.13, pyright==1.1.408)

### Notable Python-specific choices
- Chooses raw `mcp` SDK over FastMCP despite FastMCP's convenience — suggests deliberate use of low-level hooks for custom tool gating (access modes, SQL parsing via pglast)
- `src/` layout with explicit `pythonpath` — less common in MCP-server sample
- Python 3.12 floor — allows `TypeAliasType` and other 3.12 typing features
- Exact version pinning of dev tooling (pyright, ruff) is unusually strict for this sample

## 20. Gaps
- Logging/observability specifics not surfaced
- Exact CI workflows not enumerated
- Relationship to commercial Crystal DBA offering not explored
