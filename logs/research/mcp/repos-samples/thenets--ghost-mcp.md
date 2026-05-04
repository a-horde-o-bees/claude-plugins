# Sample

Mirrors of `https://github.com/thenets/ghost-mcp`. Ghost blog CMS MCP server — dual Content + Admin API coverage with JWT auto-renewal; Docker Compose local stack provided for end-to-end testing of the CMS backend. 1 star, MIT, default branch `main`. A very low-star repo with a thoughtfully-built structure: explicit FastMCP version pin, server-managed JWT lifecycle, and bundled Ghost+MySQL Compose stack for testing.

## Server runtime

### Python with FastMCP

Python 92.5%; FastMCP 2.x explicitly pinned to `2.12.3` (precise pin signals version-awareness against upstream churn). Import pattern likely `from fastmcp import FastMCP`. async/await mentioned as an implementation feature in README.

## Transport

### stdio

Stdio transport, implied by `uvx` invocation. Default mode; no transport-selection mechanism documented.

## Capability surface

### Domain-bundled tool set

15+ tools split across: Content API (10 read-only tools — posts, pages, tags, authors, settings, site info, search), Admin API (6 read/write tools — create/update/delete posts/pages/tags), and a connection-check utility tool.

### Read/write tool split

Dual-API design — Content API tools (read-only) and Admin API tools (read/write) exposed through distinct tool groups within one server. The split is forced by Ghost's two upstream APIs each having its own credential scheme.

## Configuration delivery

### Environment variables

Env vars — `GHOST_URL` and Ghost API keys (Content API and/or Admin API); env-var presence drives which API surface is active.

## Authentication

### Static API key / token via env var

Content API: query-parameter authentication with 26-character hex API keys, supplied via env var; provisioned through Ghost admin.

### Server-managed token rotation

Admin API: JWT tokens generated server-side from `id:secret` format (24-char + 64-char hex). Tokens expire after 5 minutes with automatic renewal and caching inside the server. Server holds the long-lived `id:secret` and mints short-lived JWTs transparently for every Admin API call, refreshing them every 5 minutes.

### Dual-API split credentials

Server fronts two upstream APIs that have separate credential schemes simultaneously: Content API (query-param key auth) and Admin API (JWT). Both credentials supplied via env vars; tools route to whichever API surface they belong to. A user without one credential pair simply loses access to that group of tools.

## Multi-tenancy

### Single-user / single-tenant per process

Single Ghost blog per instance (one `GHOST_URL`).

## Distribution channel

### PyPI via uvx (zero-install runner)

PyPI `ghost-mcp` package; `uvx ghost-mcp` is the primary install/launch.

### Source clone with editable install

`make run` (dev) and `make dev` (auto-reload) for local source development.

## Entry point and launch

### `uvx <package>`

`uvx ghost-mcp` is the host-config launch shape. Console script `ghost-mcp` declared in pyproject.

### Make targets in repo

`make run`, `make dev`, `make test`, `make test-connection` for local-dev and verification workflows.

## Build and packaging

### Pin discipline (Python)

Explicit FastMCP version pin (`fastmcp == 2.12.3`) — conservative tight pin tracking API drift.

### Python version pinning

`requires-python = ">=3.10"`.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP 2.x derives schemas from typed Python signatures (Pydantic internally).

## Container artifacts

### Docker-Compose backend for end-to-end tests

Full Docker Compose setup with Ghost 5.x + MySQL 8.0 — for end-to-end local testing of the CMS backend, not for deploying the MCP server. Includes health checks and volume persistence. Notable infrastructure investment: bundles the target backend's Docker stack for local testing rather than deploying the server itself.

## Test stack

### pytest with async + coverage

`make test` and `make test-connection` targets; pytest framework implied (specific config not captured).

### `make test` targets

Test invocation wrapped in Makefile targets — `make test`, `make test-connection` for upstream-reachability smoke test.

## CI

### GitHub Actions

GitHub Actions workflows directory present; specifics not extracted.

## Repository layout

### Single-package src-layout

Single-package (`src/ghost_mcp/`).

### Single-package with embedded test substrate

Bundles a Docker Compose stack (Ghost+MySQL) for end-to-end testing of the upstream service.

## Host integration

### Claude Desktop

Standard MCP client config pattern with `uvx ghost-mcp` + env vars.

## Developer ergonomics

### Makefile / Makefile.toml

Makefile-first workflow — targets for `run` / `dev` / `test` / `test-connection` (connection-check). Make-driven dev iteration.

### `uv run <tool>` invocations

`uv` / `uvx` as the version manager convention.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT licensed (per README; license file presence not confirmed).

### Active development

Recent thoughtfully-built repo despite very low star count (1) — suggests a recent or under-advertised project.
