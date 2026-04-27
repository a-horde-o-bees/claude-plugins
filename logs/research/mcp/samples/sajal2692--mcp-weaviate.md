# Sample

## Identification

### url

https://github.com/sajal2692/mcp-weaviate

### stars

~5

### last-commit

v0.2.0 (2025-09-03).

### license

MIT

### default branch

main

### one-line purpose

Weaviate vector-DB MCP server — tenancy passed as a tool argument (per-call), not server config.

## Language and runtime

### language(s) + version constraints

Python 100%; version via `.python-version`.

### framework/SDK in use

FastMCP (exact version pin not surfaced).

## Transport

### supported transports

stdio (default), streamable-http.

### how selected

CLI argument / env config.

## Distribution

### every mechanism observed

PyPI via uvx (`uvx mcp-weaviate`).

### published package name(s)

`mcp-weaviate`.

### install commands shown in README

`uvx mcp-weaviate --help`.

## Entry point / launch

### command(s) users/hosts run

`uvx mcp-weaviate`.

### wrapper scripts, launchers, stubs

entry at `src.main`.

## Configuration surface

### how config reaches the server

Environment variables for API keys and Weaviate connection parameters.

## Authentication

### flow

API keys for embedding providers and Weaviate Cloud.

### where credentials come from

OpenAI / Cohere (optional) / WCS API keys via env vars.

## Multi-tenancy

### tenancy model

Multi-tenancy supported — README explicitly calls out multi-tenancy as a feature of the search tools; tenancy becomes an argument, not a server-config dimension.

### pitfalls observed

First-class multi-tenancy in tool signatures — rare across Python MCP servers which typically treat tenancy as external config.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

11 tools — connection checks, schema info, collection listing, object retrieval, semantic/keyword/hybrid search (with per-tenant variants).

## Observability

### logging destination + format, metrics, tracing, debug flags

not surfaced

## Host integrations shown in README or repo

### Claude Desktop

implied via `uvx` command pattern.

## Claude Code plugin wrapper

### presence and shape

none observed

## Tests

### presence, framework, location, notable patterns

pytest via `uv run pytest`; `tests/` directory.

## CI

### presence, system, triggers, what it runs

GitHub Actions workflow present.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

none observed

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`uv run ruff check`, `uv run mypy`.

## Repo layout

### single-package / monorepo / vendored / other

single-package (`src/`).

## Notable structural choices

First-class multi-tenancy in tool signatures — rare across Python MCP servers which typically treat tenancy as external config. Supports two embedding providers (OpenAI, Cohere) with Cohere as optional — graceful degradation if Cohere key absent.

## Unanticipated axes observed

Exposing per-tenant search tools as a first-class MCP concept — tenancy becomes an argument, not a server-config dimension.

## Python-specific

### SDK / framework variant

FastMCP; version pin not surfaced; import pattern `from fastmcp import FastMCP`.

### Python version floor

`requires-python` value via `.python-version` (exact value not read).

### Packaging

Build backend not surfaced (uv-backed). Lock file: `uv.lock` likely. Version manager convention: uv.

### Entry point

`[project.scripts]` (name: `mcp-weaviate`) → `src.main` style; console-script name `mcp-weaviate`; host-config snippet `uvx mcp-weaviate`.

### Install workflow expected of end users

uvx primary; one-liner `uvx mcp-weaviate --help`.

### Async and tool signatures

weaviate-client has async surface; likely async.

### Type / schema strategy

Pydantic via FastMCP.

### Testing

pytest; fixture style not inspected.

### Dev ergonomics

ruff + mypy as separate `uv run` commands.

### Notable Python-specific choices

Source entry uses `src.main` style rather than a package name — suggests `src/` is an implicit package root, which requires src-layout support in the build backend.

## Gaps

Exact FastMCP version pin not read. Python floor not confirmed. No pyproject.toml content verified.
