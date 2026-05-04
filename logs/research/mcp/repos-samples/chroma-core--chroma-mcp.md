# Sample

Mirrors of `https://github.com/chroma-core/chroma-mcp`. Chroma vector-DB MCP server — 12 tools for collection and document CRUD/query; single binary supports ephemeral / persistent / self-hosted / Chroma Cloud backing stores. ~536 stars; Apache-2.0; default branch `main`; v0.2.6 released 2025-08-14, active.

## Server runtime

### Python with raw MCP SDK

Python `>=3.10` server using raw `mcp` SDK (`mcp[cli]==1.6.0`) — no FastMCP dependency. Exact pin `==1.6.0`. Import pattern: `mcp.server` / `mcp.server.fastmcp` (via the `mcp[cli]` extra). Pinned raw `mcp` SDK rather than FastMCP — unusual for a 2025 vector-DB server (most vendor servers have migrated to FastMCP).

## Transport

### stdio

stdio is the documented transport (default via the MCP SDK); SSE/HTTP not called out in README.

### Selection mechanism

CLI argument / env-var mode controls client type and (where relevant) transport.

## Capability surface

### Domain-bundled tool set

12 tools — collection CRUD (create/delete/modify), document operations (add/query/update), retrieval with filtering. Curated multi-tool surface organized by entity-type/operation class for vector-database semantics.

## Configuration delivery

### CLI flags

CLI args are the primary surface; flags select client mode (ephemeral | persistent | http | cloud) and tune connection.

### Environment variables

Environment variables layered alongside CLI flags. Provider API keys via the `CHROMA_<PROVIDER>_API_KEY` convention — uniform auth surface across multiple embedding back-ends (OpenAI, Cohere, VoyageAI).

### Dotenv file

Optional `.env` file via `--dotenv-path` flag layered on top of env-var resolution.

## Authentication

### Static API key / token via env var

API key for Chroma Cloud and for embedding providers, supplied via env vars / `.env` / CLI args. Provider-prefixed pattern (`CHROMA_OPENAI_API_KEY`, `CHROMA_COHERE_API_KEY`, `CHROMA_VOYAGEAI_API_KEY`) gives a uniform auth surface across multiple embedding back-ends.

### Per-source independent API keys with graceful degradation

Bundles three cloud embedding SDKs in core deps (openai, cohere, voyageai) — not extras — giving a fat install but zero-friction provider switching across embedding back-ends. Each provider key is independent; the optional `sentence-transformers` extra lets users run locally-embedded collections without any of the cloud-provider keys.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user process; collection is a per-call argument.

### Mode-switched backing store

Single binary supports four backing-store modes (ephemeral in-memory, persistent local, HTTP self-hosted, Chroma Cloud) chosen at launch via flags rather than four separate entry points. Same MCP surface adapts to radically different deployment targets through a single client-type dimension.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uvx chroma-mcp` — published as `chroma-mcp` on PyPI; runnable through uvx without prior install.

### Docker / OCI image

Dockerfile present; Docker as alternative install path.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` maps `chroma-mcp` to `chroma_mcp:main`.

### `uvx <package>`

Host-config snippet shape: `uvx chroma-mcp` with flags selecting client type — e.g., `uvx chroma-mcp --client-type persistent --data-dir ./chroma_data`.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. Lock file presence not confirmed. Version manager convention: `.python-version` likely (standard for uvx-published packages). `requires-python = ">=3.10"`.

## Schema and types

### Pydantic v2 models

Pydantic via the MCP SDK (pulled in transitively rather than declared explicitly); schemas auto-derived from signatures per MCP SDK idiom.

### Async model (cross-cutting)

Mixed; pytest-asyncio in test deps suggests async coverage in the suite.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

## Test stack

### pytest with async + coverage

pytest ≥ 8.3.5, pytest-asyncio ≥ 0.26.0, pytest-cov ≥ 4.1.0; `tests/` directory. Fixture style not inspected.

## CI

### GitHub Actions

GitHub Actions workflows in `.github/workflows/`.

## Repository layout

### Single-package src-layout

Single package under `src/chroma_mcp/`.

## Observability

### Stderr logging (convention / SDK default)

Standard MCP SDK stderr logging; no bespoke metrics / tracing.

## Host integration

### Claude Desktop

JSON config snippet provided.

### Cursor

Generic uvx-based config covers Cursor and other MCP clients.

## Developer ergonomics

### MCP framework dev config

`mcp` CLI via `mcp[cli]` extra; `.env` example committed.

### Sample MCP client configs in repo

Claude Desktop snippet plus uvx CLI flags well-documented.

## Documentation surface

### README as the canonical surface

`.env` example; Claude Desktop snippet; uvx CLI flags well documented inline.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

None observed.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Tagged release with version in changelog

v0.2.6 released 2025-08-14.

### Active development

Active maintenance with semver-tagged releases.
