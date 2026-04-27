# Sample

## Identification

### url

https://github.com/zilliztech/mcp-server-milvus

### stars

~228

### last-commit

active (35 commits total)

### license

Apache-2.0

### default branch

main

### one-line purpose

Milvus vector-DB MCP server — env-over-CLI precedence; launched from source tree via `uv run`.

## 1. Language and runtime

### language(s) + version constraints

Python, `requires-python >= 3.10`.

### framework/SDK in use

FastMCP 2.x (`fastmcp >= 2.14.1`).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (default), SSE.

### how selected

CLI flag / env var; README shows separate JSON configs for each mode.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

source clone + `uv run`; PyPI package available (`mcp-server-milvus` implied by script name), but README leads with `uv run src/mcp_server_milvus/server.py`.

### published package name(s)

`mcp-server-milvus`.

### install commands shown in README

`uv run src/mcp_server_milvus/server.py --milvus-uri http://localhost:19530`.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`uv run src/mcp_server_milvus/server.py --milvus-uri ...`, or console script `mcp-server-milvus`.

### wrapper scripts, launchers, stubs

none observed.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

`.env` file (takes priority over CLI args), CLI args, env vars — `MILVUS_URI`, `MILVUS_TOKEN`, `MILVUS_DB`.

### pitfalls observed

`.env` explicitly given priority over CLI args — inverse of the more common "CLI overrides env" order; likely a bias toward reproducible host-config-driven deployments.

## 6. Authentication

### flow

optional token.

### where credentials come from

`MILVUS_TOKEN` env var.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user — server bound to one Milvus URI/DB.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

~15 tools — text search, vector search, hybrid search, similarity search, query, collection CRUD (list/create/load/release/info), insert, delete.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

FastMCP-standard logging; no explicit metrics/tracing.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON config snippets (stdio and SSE variants).

### Cursor

`.cursor/` directory present; dedicated JSON snippet.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

no explicit test suite visible in README (no dedicated test directory surfaced).

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

none observed in surfaced content.

### pitfalls observed

CI workflow presence unverified.

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

none observed.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop and Cursor JSON snippets; `.env` example.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`src/mcp_server_milvus/`).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

`.env` explicitly given priority over CLI args — inverse of the more common "CLI overrides env" order; likely a bias toward reproducible host-config-driven deployments.

Uses `click` for CLI arg parsing despite FastMCP providing its own `fastmcp` CLI — server is launched via a plain Python entry point rather than via FastMCP's launcher.

## 18. Unanticipated axes observed

env-vs-CLI precedence is a real axis — most servers do CLI > env; this repo does env > CLI.

## 19. Python-specific

### SDK / framework variant

FastMCP 2.x. Version pin from pyproject.toml: `fastmcp >= 2.14.1` (lower-bound, not pinned). Import pattern: `fastmcp` top-level package.

### Python version floor

`requires-python` value: `>=3.10`.

### Packaging

build backend: hatchling (wheel from `src/mcp_server_milvus`). Lock file present: `uv.lock` present. Version manager convention: uv (lock file committed).

### Entry point

`[project.scripts]` -> `mcp_server_milvus.server:main`. Actual console-script name: `mcp-server-milvus`. Host-config snippet shape: `uv run` pointing at a checked-out source path (unusual — most servers use `uvx <package>`).

### Install workflow expected of end users

source clone + `uv run` against tree; or (implicitly) `uvx mcp-server-milvus`. One-liner: `uv run src/mcp_server_milvus/server.py --milvus-uri http://localhost:19530`.

### Async and tool signatures

FastMCP-standard (mix); `pymilvus` client calls generally sync.

### Type / schema strategy

Pydantic via FastMCP; schema auto-derived from type hints.

### Testing

none observed.

### Dev ergonomics

ruff pinned in project deps (unusual — most projects put ruff in dev-only extra).

### Notable Python-specific choices

`ruff` in project-level dependencies rather than a dev extra — blurs lint tooling into runtime install, adding weight for end users. Source-tree `uv run` is the primary launch method; unusual for a vendor-official MCP server.

## 20. Gaps

No Docker artifacts despite Milvus typically being consumed containerized. Test suite presence/absence not conclusively verified from the root. CI workflow presence unverified.
