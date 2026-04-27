# Sample

## Identification

### url

https://github.com/qdrant/mcp-server-qdrant

### stars

~1,400

### last-commit

active through 2025 (74 commits on master)

### license

Apache-2.0

### default branch

master

### one-line purpose

Qdrant vector-DB MCP server — collection management and semantic search; official-vendor FastMCP 2.x build.

## 1. Language and runtime

### language(s) + version constraints

Python, `requires-python >= 3.10`.

### framework/SDK in use

FastMCP 2.x (pinned at `fastmcp == 2.7.0`).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (default), sse, streamable-http.

### how selected

FastMCP environment variables / command invocation; README documents picking transport explicitly.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (uvx), Docker image, Smithery one-click, manual host config.

### published package name(s)

`mcp-server-qdrant` on PyPI.

### install commands shown in README

`uvx mcp-server-qdrant`, Docker build, Smithery.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`uvx mcp-server-qdrant`, `mcp-server-qdrant` (console script).

### wrapper scripts, launchers, stubs

None observed; FastMCP `fastmcp dev src/mcp_server_qdrant/server.py` for Inspector.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Environment variables only (CLI args deprecated). `QDRANT_URL`, `QDRANT_LOCAL_PATH`, `QDRANT_API_KEY`, `COLLECTION_NAME`, `EMBEDDING_MODEL`, `EMBEDDING_PROVIDER`, plus FastMCP host/port/log envs.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

API key.

### where credentials come from

`QDRANT_API_KEY` env var (used by qdrant-client against Qdrant Cloud or remote).

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

Single-user — server bound to one Qdrant instance and one default collection per process.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Two tools — `qdrant-store` (persist with optional metadata/collection), `qdrant-find` (semantic retrieval).

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

FastMCP-standard logging via env config; no bespoke metrics/tracing observed.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON snippet for `claude_desktop_config.json`.

### VS Code / Cursor / Windsurf

JSON snippet with `uvx` command.

### Smithery

One-click install for Claude Desktop.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest >=8.3.3 with pytest-asyncio (auto mode); tests under `tests/`; default test collection uses in-memory Qdrant.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions in `.github/workflows/` (lint/type-check/test + release).

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`fastmcp dev` invocation documented; Claude/Cursor/Windsurf sample JSON configs.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`src/mcp_server_qdrant/`).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Pydantic 2 range pinned `>=2.10.6,<2.12.0` — tight version window to track FastMCP compatibility. `fastembed` used for local-default embeddings, eliminating need for an embedding API key to get started.

## 18. Unanticipated axes observed

Embedding model/provider decoupled from storage backend via two envs (`EMBEDDING_MODEL`, `EMBEDDING_PROVIDER`); local-path mode vs remote Qdrant as a single env toggle.

## 19. Python-specific

### SDK / framework variant

FastMCP 2.x via `fastmcp` top-level package; pyproject pin is exact at `fastmcp == 2.7.0`.

### Python version floor

`requires-python` value — `>=3.10`.

### Packaging

Build backend: hatchling. `.python-version` file tracked (implies uv); lock file presence not confirmed from README.

### Entry point

`[project.scripts]` -> `mcp_server_qdrant.main:main`; console-script name `mcp-server-qdrant`; host-config snippet uses `uvx mcp-server-qdrant`.

### Install workflow expected of end users

uvx run (default), Docker, Smithery; one-liner `uvx mcp-server-qdrant`.

### Async and tool signatures

async (FastMCP default); pytest-asyncio auto mode in tests.

### Type / schema strategy

Pydantic 2 (direct dep); FastMCP auto-derives schemas from type hints.

### Testing

pytest + pytest-asyncio; in-memory Qdrant client fixture.

### Dev ergonomics

`fastmcp dev` documented; pre-commit configured.

### Notable Python-specific choices

Uses `fastembed` (ONNX-backed embedding lib from Qdrant) so default install has no API-key requirement. Exact-pin on FastMCP (`==2.7.0`) rather than range — suggests sensitivity to FastMCP API drift.

## 20. Gaps

Exact `.python-version` content (e.g. 3.11 vs 3.12) not read. Whether `uv.lock` is committed not confirmed. Specific GitHub Actions workflow names not inspected.
