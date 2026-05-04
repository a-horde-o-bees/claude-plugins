# Sample

Mirrors of `https://github.com/qdrant/mcp-server-qdrant`. Qdrant vector-DB MCP server — official-vendor FastMCP 2.x build; collection management and semantic search. ~1,400 stars, Apache-2.0, default branch `master`, active through 2025 (74 commits on master).

## Server runtime

### Python with FastMCP

FastMCP 2.x via `fastmcp` top-level package; pyproject pin is exact at `fastmcp == 2.7.0`. Python `requires-python >= 3.10`. Async (FastMCP default). Exact pin (`==2.7.0`) rather than range — suggests sensitivity to FastMCP API drift.

## Transport

### stdio

stdio is default.

### SSE (Server-Sent Events)

SSE transport supported via FastMCP.

### Streamable HTTP

streamable-http transport supported via FastMCP.

### Selection mechanism

FastMCP environment variables / command invocation; README documents picking transport explicitly.

## Capability surface

### Tools-only, hand-curated narrow surface

Two tools — `qdrant-store` (persist with optional metadata/collection), `qdrant-find` (semantic retrieval).

## Configuration delivery

### Environment variables

CLI args deprecated; env-var-only configuration. `QDRANT_URL`, `QDRANT_LOCAL_PATH`, `QDRANT_API_KEY`, `COLLECTION_NAME`, `EMBEDDING_MODEL`, `EMBEDDING_PROVIDER`, plus FastMCP host/port/log envs. Embedding model/provider decoupled from storage backend via two envs (`EMBEDDING_MODEL`, `EMBEDDING_PROVIDER`); local-path mode vs remote Qdrant as a single env toggle.

### Host-side JSON config snippet

Claude Desktop, VS Code/Cursor/Windsurf JSON snippets in README; Smithery one-click install for Claude Desktop.

## Authentication

### Static API key / token via env var

`QDRANT_API_KEY` env var (used by qdrant-client against Qdrant Cloud or remote).

## Multi-tenancy

### Single-user / single-tenant per process

Server bound to one Qdrant instance and one default collection per process.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uvx mcp-server-qdrant`; package name `mcp-server-qdrant` on PyPI.

### Docker / OCI image

Dockerfile present; Docker build documented.

### Smithery registry

Smithery one-click install for Claude Desktop.

### Multi-channel publication

PyPI (uvx), Docker image, Smithery one-click, manual host config — multiple parallel channels.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` -> `mcp_server_qdrant.main:main`; console-script name `mcp-server-qdrant`.

### `uvx <package>`

`uvx mcp-server-qdrant` — primary host-config snippet shape.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. `.python-version` file tracked (implies uv); lock file presence not confirmed from README. Pydantic 2 range pinned `>=2.10.6,<2.12.0` — tight version window to track FastMCP compatibility.

### Pin discipline (Python)

Exact pin on FastMCP (`fastmcp == 2.7.0`) and tight Pydantic range (`>=2.10.6,<2.12.0`) — defensive pinning to track FastMCP compatibility.

## Schema and types

### Pydantic v2 models

Pydantic 2 (direct dep); FastMCP auto-derives schemas from type hints.

### FastMCP auto-derivation from type hints

FastMCP auto-derives schemas from Python type hints.

### Async model (cross-cutting)

Async (FastMCP default); pytest-asyncio auto mode in tests.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

## Test stack

### pytest with async + coverage

pytest >=8.3.3 with pytest-asyncio (auto mode); tests under `tests/`; default test collection uses in-memory Qdrant client fixture.

## CI

### GitHub Actions

GitHub Actions in `.github/workflows/` (lint/type-check/test + release).

## Host integration

### Claude Desktop

JSON snippet for `claude_desktop_config.json`.

### VS Code / VS Code Insiders / Visual Studio family

JSON snippet with `uvx` command.

### Cursor

JSON snippet with `uvx` command.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Windsurf JSON snippet with `uvx` command.

### Smithery / Glama discovery

One-click install for Claude Desktop via Smithery.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

None observed.

## Developer ergonomics

### Inspector/debug tooling references

`fastmcp dev src/mcp_server_qdrant/server.py` for Inspector documented.

### `pre-commit` framework

pre-commit configured.

### Sample MCP client configs in repo

Claude/Cursor/Windsurf sample JSON configs.

## Documentation surface

### README as the canonical surface

Install/setup documented in README.

## Repository layout

### Single-package src-layout

single-package (`src/mcp_server_qdrant/`).

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0; official-vendor (Qdrant org).

### Active development

74 commits on master; active through 2025.

## Domain logic and embedded intelligence

### Embedded RAG / retrieval pipeline

`fastembed` (ONNX-backed embedding lib from Qdrant) used for local-default embeddings, eliminating need for an embedding API key to get started.
