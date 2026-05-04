# Sample

Mirrors of `https://github.com/sajal2692/mcp-weaviate`. Weaviate vector-DB MCP server — exposes connection checks, schema info, collection listing, object retrieval, and semantic/keyword/hybrid search; multi-tenancy is a per-call argument rather than server config. ~5 stars, MIT, default branch `main`. Last release v0.2.0 (2025-09-03).

## Server runtime

### Python with FastMCP

Python (100% of repo) on FastMCP. Import pattern `from fastmcp import FastMCP`. Exact FastMCP version pin not surfaced; weaviate-client async surface implies tools are likely async.

## Transport

### stdio

Default transport.

### Streamable HTTP

Supported alongside stdio.

### Selection mechanism

CLI argument or env config selects between stdio and streamable-http.

## Capability surface

### Tools-only, hand-curated narrow surface

11 tools: connection checks, schema info, collection listing, object retrieval, plus semantic/keyword/hybrid search variants (each with a per-tenant variant).

## Configuration delivery

### Environment variables

Environment variables carry API keys (OpenAI, Cohere optional, WCS) and Weaviate connection parameters.

## Authentication

### Per-source independent API keys with graceful degradation

Two embedding providers supported (OpenAI, Cohere); Cohere is optional — server degrades gracefully when the Cohere key is absent.

### Static API key / token via env var

WCS / OpenAI / Cohere keys supplied via environment variables; standard env-var credential pattern.

## Multi-tenancy

### Per-call tenancy argument

Multi-tenancy is a first-class feature of the search tools — tenant identifier is a tool argument, not a server-config dimension. README explicitly calls out multi-tenancy as a feature; tool signatures expose per-tenant search variants — every search/retrieval tool takes a `tenant` parameter consistently rather than relying on an env-var-pinned tenant.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published to PyPI as `mcp-weaviate`; installed via `uvx mcp-weaviate` — README shows `uvx mcp-weaviate --help` as the install command.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` declares `mcp-weaviate` → `src.main` (src-layout style); host-config snippet shape `uvx mcp-weaviate`.

### `uvx <package>`

Primary user invocation is `uvx mcp-weaviate`.

## Build and packaging

### Hatchling + uv (Python)

uv-backed packaging; `uv.lock` likely present (not directly verified). Build backend not surfaced in extract.

### Python version pinning

`.python-version` file present; exact value not extracted.

## Schema and types

### FastMCP auto-derivation from type hints

Pydantic-backed schema auto-derived from Python signatures via FastMCP.

### Async model (cross-cutting)

Tools likely async — weaviate-client exposes an async surface.

## Test stack

### pytest with async + coverage

`pytest` via `uv run pytest`; `tests/` directory.

## CI

### GitHub Actions

GitHub Actions workflow present.

## Host integration

### Claude Desktop

Implied via `uvx` command pattern — README does not show explicit host snippets but `uvx mcp-weaviate` plugs into any host with a JSON command/args slot.

## Repository layout

### Single-package src-layout

`src/`-layout single-package; `[project.scripts]` entry uses `src.main` style (implicit src-package root requiring src-layout build-backend support).

## Developer ergonomics

### Linter and type-checker stack

`uv run ruff check` and `uv run mypy` as separate developer commands.

### `uv run <tool>` invocations

Each developer tool invoked via `uv run <tool>` rather than a Makefile or task runner.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

v0.2.0 released 2025-09-03.
