# Sample

Mirrors of `https://github.com/crystaldba/postgres-mcp`. PostgreSQL performance-tuning MCP server — SQL execution plus deterministic index optimization (hypopg simulation, Pareto selection, workload compression) and health analysis. 2.6k stars; MIT; default branch `main`; v0.3.0 released May 16, 2025.

## Server runtime

### Python with raw MCP SDK

Python (98.4% of repo); raw `mcp` Python SDK (`mcp[cli]>=1.25.0`); FastMCP not in deps. Import pattern: low-level MCP server API (inferred). Uses psycopg3 (async), pglast (SQL parsing), hypopg (index simulation), pg_stat_statements. Raw SDK chosen over FastMCP despite FastMCP's convenience — suggests deliberate use of low-level hooks for custom tool gating (access modes, SQL parsing via pglast).

## Transport

### stdio

stdio is the default transport.

### SSE (Server-Sent Events)

SSE available as alternative.

### Selection mechanism

CLI flag at startup: `--transport=sse` selects SSE; default is stdio.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools-only by deliberate design choice — README states "no resources/prompts because the MCP client ecosystem has widespread support for MCP tools." 9 tools: `list_schemas`, `list_objects`, `get_object_details`, `execute_sql`, `explain_query`, `get_top_queries`, `analyze_workload_indexes`, `analyze_query_indexes`, `analyze_db_health`.

### Capability gating flags (per-tool, per-category, write-mode)

`--access-mode` flag (`unrestricted` / `restricted`) gates write operations. Read-only enforcement happens via SQL parsing (pglast) — rejects COMMIT/ROLLBACK in restricted mode.

## Configuration delivery

### Environment variables

`DATABASE_URI` env var carries the PostgreSQL connection string.

### CLI flags

`--access-mode` (unrestricted/restricted) and `--transport` flags.

### Connection URI scheme

`DATABASE_URI` packs host, port, credentials, and TLS selection into one PostgreSQL URI.

### Host-side JSON config snippet

MCP client JSON configs documented for Claude Desktop, Cursor, Windsurf, Goose, Qodo Gen.

## Authentication

### Database connection string

PostgreSQL URI credentials embedded in `DATABASE_URI` env var; no additional auth layer at the MCP boundary. Read-only mode enforced in-process via SQL parsing (pglast), not via DB-level permissions — a parser-level safety net rather than a privilege constraint.

## Multi-tenancy

### Single connection per server instance

Single database connection per server instance. SSE transport lets multiple clients share one process but does not separate tenancies.

## Distribution channel

### PyPI via pip / pipx

`pipx install postgres-mcp`; `uv pip install postgres-mcp`. PyPI package: `postgres-mcp`.

### PyPI via uvx (zero-install runner)

`uvx postgres-mcp` runnable form.

### Source clone with `uv run` from source tree

`uv run postgres-mcp <connection-string>` from source.

### Docker / OCI image

Docker Hub: `crystaldba/postgres-mcp`; `docker pull crystaldba/postgres-mcp`.

### Multi-channel publication

Same server published via PyPI + Docker + source — different user segments served simultaneously.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` declares `postgres-mcp = "postgres_mcp:main"`.

### `uvx <package>`

Host-config snippet `uvx postgres-mcp` is one of four documented launch modes.

### Source-tree `uv run`

`uv run postgres-mcp` from source tree.

### Docker container entrypoint

`docker run crystaldba/postgres-mcp` is a documented launch mode.

## Build and packaging

### Hatchling + uv (Python)

Build backend: `hatchling.build`. Lock file: `uv.lock` (uv-managed per README `uv sync`). Version manager convention: `uv`.

### `uv.lock` committed

`uv.lock` committed for reproducibility.

### Pin discipline (Python)

Exact version pinning of dev tooling: ruff==0.14.13, pyright==1.1.408 — unusually strict for this corpus, applies discipline at the developer-environment layer.

### Python version pinning

`requires-python = ">=3.12"` — highest floor in the Python sample. Ruff target-version intentionally lags at `py39` (style target), separate from runtime floor. Python 3.12 floor allows `TypeAliasType` and other 3.12 typing features.

## Schema and types

### Hand-authored tool schemas

Low-level MCP SDK requires hand-authored schemas (vs FastMCP auto-derivation).

### Async model (cross-cutting)

`pytest-asyncio>=1.3.0` in dev deps confirms async test surface; psycopg3 async is the database client. Tool handlers typically `async def` in this SDK variant.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile auto-remaps host address (localhost → host.docker.internal on macOS/Windows, 172.17.0.1 on Linux) — quality-of-life packaging that bridges the cross-platform "connect from container to host service" gap.

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio. `asyncio_default_fixture_loop_scope = "function"` in pyproject pytest config. `pythonpath = ["./src"]` — src-layout package. README notes use of "AI-generated adversarial workloads."

## CI

### GitHub Actions

GitHub Actions workflows in `.github/workflows/`; specifics not extracted.

## Repository layout

### Single-package src-layout

`src/postgres_mcp/`, `tests/`, `examples/`, `.github/workflows/`, Dockerfile, pyproject.toml.

## Host integration

### Claude Desktop

Config example provided.

### Cursor

Config example provided.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Windsurf, Goose, Qodo Gen config examples provided.

## Safety and security posture

### Read-only by default with explicit write flag

`--access-mode=restricted` is the safety mode — pglast parses incoming SQL and rejects COMMIT/ROLLBACK. Unrestricted mode required for writes; deliberate opt-in.

### In-process safety enforcement via parsing

SQL parsing via pglast enforces read-only mode at the server, not at the database. Server-side parser-based gate rather than DB-level permission gate.

## Domain logic and embedded intelligence

### Deterministic optimization layered on top of raw ops

Embedded performance-tuning intelligence — workload analysis, hypothetical indexing via hypopg extension (simulates index impact without creating real indexes), greedy-search optimization adapted from Microsoft Anytime, Pareto-front cost-benefit balancing between performance gains and storage overhead, workload compression normalizing queries to shrink index-search space. Goes far beyond typical SQL-execution MCP servers. Optional OpenAI API integration for experimental LLM-based index tuning is offered as a complement, not the core.

## Developer ergonomics

### Devcontainer / mise / dev-environment manifests

devenv files mentioned in README for reproducible environments.

### Linter and type-checker stack

ruff + pyright pinned to exact versions (ruff==0.14.13, pyright==1.1.408).

## Documentation surface

### README + examples/

`examples/` directory with `movie-app.md` and similar.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not present.

## Release and lifecycle

### Tagged release with version in changelog

v0.3.0 released May 16, 2025.

### Active development

Active maintenance; 2.6k stars.

### License — Permissive (MIT / Apache-2.0)

MIT.
