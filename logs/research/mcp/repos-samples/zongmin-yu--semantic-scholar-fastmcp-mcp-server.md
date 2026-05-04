# Sample

Mirrors of `https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server`. Semantic Scholar MCP server — dual-protocol MCP (stdio) + HTTP REST in the same process; FastMCP-backed. ~125 stars, MIT, default branch `main`.

## Server runtime

### Python with FastMCP

Python 3.10+ with FastMCP. Import pattern `from fastmcp import FastMCP` likely; version pin not surfaced. Schema auto-derived via FastMCP. Likely async (FastMCP + httpx).

## Transport

### stdio

stdio is the MCP default transport.

### REST API bridge alongside MCP

Custom HTTP REST bridge runs in-process bound to port 8000 (configurable via `SEMANTIC_SCHOLAR_HTTP_BRIDGE_HOST`/`SEMANTIC_SCHOLAR_HTTP_BRIDGE_PORT`); both protocols serve simultaneously. Toggled via `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE` env var. Non-MCP clients consume the same tool surface through a hand-rolled REST API. Suggests FastMCP's `streamable-http` is not being used; custom bridge layer lives alongside.

### Selection mechanism

Implicit default — stdio always; HTTP bridge is opt-in via env-var enable flag and serves alongside, not instead of stdio.

## Capability surface

### Domain-bundled tool set

16 tools organized into 4 explicit functional groups — 8 paper search/discovery, 2 citation analysis, 4 author info, 2 recommendation. Tool categorization baked into documentation structure.

### REST endpoints alongside MCP tools

The HTTP bridge exposes the same tool surface to non-MCP clients. Distinct from MCP transport — a parallel REST API layered alongside.

## Configuration delivery

### Environment variables

`SEMANTIC_SCHOLAR_API_KEY`, `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE`, `SEMANTIC_SCHOLAR_HTTP_BRIDGE_HOST`, `SEMANTIC_SCHOLAR_HTTP_BRIDGE_PORT` — vendor-prefixed env-var convention.

### Host-side JSON config snippet

Claude Desktop JSON snippet uses `uvx` command shape.

## Authentication

### API key (optional, for higher rate limits)

Optional API key via `SEMANTIC_SCHOLAR_API_KEY` for higher rate limits — server works without credentials but accepts the key to lift quotas.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user; one credential set per process.

## Distribution channel

### PyPI via pip / pipx

`pip install semantic-scholar-fastmcp` documented; published as `semantic-scholar-fastmcp` on PyPI.

### PyPI via uvx (zero-install runner)

`uvx semantic-scholar-fastmcp` — canonical zero-install path.

### Docker / OCI image

Dockerfile and `docker-compose.yml` ship with the repo.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` registers `semantic-scholar-mcp-server` as the console script. Host-config snippet shape: `uvx semantic-scholar-fastmcp`.

## Build and packaging

### Hatchling + uv (Python)

Version manager convention: pip + uvx. Build backend not surfaced explicitly.

### Optional-dependency fan-out

`[dev]` optional extra gates test/dev dependencies.

### Python version pinning

`requires-python = ">=3.10"`.

## Schema and types

### FastMCP auto-derivation from type hints

Tool function signatures with type hints become MCP tool input schemas automatically; Pydantic via FastMCP.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

### Docker Compose for local dev

`docker-compose.yml` orchestrates the server for local development.

## Test stack

### pytest with async + coverage

`tests/` directory present; `[dev]` extra implies pytest. Specifics not surfaced.

### Dev extras gating test deps

`[dev]` optional extra gates test dependencies.

## CI

### GitHub Actions

`.github/` directory with GitHub Actions present.

## Host integration

### Claude Desktop

JSON config snippet using `uvx` command shown in README.

## Observability

### None / unspecified

Logging strategy not surfaced.

## Repository layout

### Single-package src-layout

Single-package — `semantic_scholar/` with `server.py`, `mcp.py`, `config.py`, utility modules. Separate `mcp.py` and `server.py` files likely split MCP-protocol surface from HTTP/business-logic surface.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
