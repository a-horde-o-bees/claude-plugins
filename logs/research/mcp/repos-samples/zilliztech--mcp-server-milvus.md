# Sample

Mirrors of `https://github.com/zilliztech/mcp-server-milvus`. Milvus vector-DB MCP server — env-over-CLI precedence; launched from source tree via `uv run`. ~228 stars, Apache-2.0, default branch `main`. Vendor-authored (Zilliz) but distributed as source-tree `uv run` rather than via PyPI as the canonical path.

## Server runtime

### Python with FastMCP

Python with FastMCP 2.x — `fastmcp >= 2.14.1` (lower-bound, not pinned). `requires-python >= 3.10`. Import pattern `fastmcp` top-level package. Tool handlers mix sync/async per FastMCP defaults; `pymilvus` client calls generally sync.

## Transport

### stdio

stdio default for Claude Desktop integration.

### SSE (Server-Sent Events)

SSE supported as alternative HTTP-based streaming transport. README shows separate JSON configs for stdio and SSE modes.

### Selection mechanism

CLI flag / env var — README shows separate JSON configs for each mode rather than a single multi-mode launcher.

## Capability surface

### Domain-bundled tool set

~15 tools — text search, vector search, hybrid search, similarity search, query, collection CRUD (list/create/load/release/info), insert, delete. Curated multi-tool surface organized by operation class.

## Configuration delivery

### Dotenv file

`.env` file is the highest-priority configuration source — explicitly inverts the more common "CLI overrides env" order. Likely a bias toward reproducible host-config-driven deployments at the cost of overriding CLI invocations.

### CLI flags

`--milvus-uri`, `--milvus-token`, `--milvus-db` flags supported but lower-priority than `.env`.

### Environment variables

`MILVUS_URI`, `MILVUS_TOKEN`, `MILVUS_DB` env vars.

### Host-side JSON config snippet

Claude Desktop and Cursor JSON snippets shown for stdio and SSE variants.

## Authentication

### Static API key / token via env var

Optional Milvus token via `MILVUS_TOKEN` env var.

## Multi-tenancy

### Single-user / single-tenant per process

Server bound to one Milvus URI/DB per process.

## Distribution channel

### Source clone with `uv run` from source tree

Server launched from a checked-out source tree via `uv run src/mcp_server_milvus/server.py --milvus-uri http://localhost:19530`. Unusual for a vendor-official server — README leads with this rather than `uvx`. Forces consumers to clone the repository.

### PyPI via uvx (zero-install runner)

`mcp-server-milvus` PyPI package available (implied by console-script registration), but README leads with the source-tree path.

## Entry point and launch

### Source-tree `uv run`

`"command": "uv"` with `run src/mcp_server_milvus/server.py --milvus-uri ...` as args. Launches against a checked-out source path rather than an installed package.

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` declares `mcp-server-milvus` mapped to `mcp_server_milvus.server:main`. Available as alternative once installed via uvx/pip.

### Click-based CLI wrapper (Python)

Uses `click` for CLI arg parsing despite FastMCP providing its own `fastmcp` CLI — server is launched via a plain Python entry point rather than via FastMCP's launcher.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling (wheel from `src/mcp_server_milvus`). Version manager convention: uv (lock file committed).

### `uv.lock` committed

`uv.lock` present — modern uv-first reproducibility convention.

### Python version pinning

`requires-python = ">=3.10"`.

## Schema and types

### FastMCP auto-derivation from type hints

Tool function signatures with type hints become MCP tool input schemas automatically; Pydantic via FastMCP.

## Container artifacts

### No container artifacts

No Docker artifacts despite Milvus typically being consumed containerized.

## Test stack

### No tests / not surfaced

No explicit test suite visible in README; no dedicated test directory surfaced.

## CI

### None / absent

Not observed in surfaced content (presence unverified).

## Host integration

### Claude Desktop

JSON config snippets (stdio and SSE variants).

### Cursor

`.cursor/` directory present; dedicated JSON snippet shown.

## Observability

### Stderr logging (convention / SDK default)

FastMCP-standard logging; no explicit metrics/tracing.

## Repository layout

### Single-package src-layout

Single-package — `src/mcp_server_milvus/`.

## Developer ergonomics

### Linter and type-checker stack

`ruff` pinned in project-level dependencies (rather than a dev extra) — blurs lint tooling into runtime install.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0; vendor-authored (Zilliz).
