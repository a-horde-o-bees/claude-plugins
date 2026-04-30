# Sample

## Identification

### url

https://github.com/thenets/ghost-mcp

### stars

1

### last-commit

not captured

### license

MIT

### default branch

main

### one-line purpose

Ghost blog CMS MCP server — dual Content + Admin API coverage with JWT auto-renewal; Docker Compose local stack provided.

## Language and runtime

### language(s) + version constraints

Python 92.5%; Python 3.10+ required.

### framework/SDK in use

FastMCP 2.12.3 (explicit version in README).

## Transport

### supported transports

stdio (implied by `uvx` invocation).

### how selected

default

## Distribution

### every mechanism observed

PyPI `ghost-mcp` (via `uvx ghost-mcp`); clone + `make run`; Docker Compose for the full Ghost+MySQL test stack.

### published package name(s)

`ghost-mcp`

### install commands shown in README

`uvx ghost-mcp`

## Entry point / launch

### command(s) users/hosts run

`uvx ghost-mcp`; `make run` (dev); `make dev` (auto-reload).

### wrapper scripts, launchers, stubs

`src/ghost_mcp/server.py` is the entry point.

## Configuration surface

### how config reaches the server

env vars — `GHOST_URL` and Ghost API keys (Content API and/or Admin API); env-var selection drives which API surface is active.

## Authentication

### flow

Content API: query-parameter authentication with 26-character hex API keys. Admin API: JWT tokens generated from `id:secret` format (24-char + 64-char hex); tokens expire after 5 minutes with automatic renewal and caching.

### where credentials come from

Ghost API keys provisioned through Ghost admin; passed via env vars.

## Multi-tenancy

### tenancy model

single Ghost blog per instance (one `GHOST_URL`).

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

15+ tools across: Content API: 10 read-only (posts, pages, tags, authors, settings, site info, search). Admin API: 6 read/write (create/update/delete posts/pages/tags). Utility: connection check.

## Observability

### logging destination + format, metrics, tracing, debug flags

not captured

## Host integrations shown in README or repo

### Claude Desktop

standard MCP client config pattern with `uvx ghost-mcp` + env vars.

## Claude Code plugin wrapper

### presence and shape

none

## Tests

### presence, framework, location, notable patterns

`make test`, `make test-connection`; GitHub Actions workflows directory present.

## CI

### presence, system, triggers, what it runs

GitHub Actions (workflows present, details not extracted).

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

full Docker Compose setup with Ghost 5.x + MySQL 8.0 — for end-to-end local testing, not server deployment. Includes health checks and volume persistence.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Makefile targets (`make run`, `make dev`, `make test`, `make test-connection`); Docker Compose for CMS backend.

### pitfalls observed

Makefile-first workflow — targets for run/dev/test/connection-check.

## Repo layout

### single-package / monorepo / vendored / other

single-package (`src/ghost_mcp/`).

## Notable structural choices

Dual-API design — Content API (read-only, query-param auth) and Admin API (read/write, JWT) exposed through distinct tool groups within one server.

JWT auto-renewal and caching inside the MCP server — 5-minute token lifetime handled transparently; an unusual amount of auth logic for an MCP server.

Ghost+MySQL Docker Compose for dev — not for deploying the MCP server, but for bringing up the CMS backend to test against; a notable dev-ergonomics investment for a 1-star repo.

Makefile-first workflow — targets for run/dev/test/connection-check.

FastMCP version pinned explicitly to 2.12.3 — a precise pin signals version-awareness.

## Unanticipated axes observed

Server-managed token rotation — most MCP servers assume static creds; this one refreshes JWTs every 5 minutes. Auth mechanics live in the server rather than the LLM or user.

Companion infrastructure in the repo for end-to-end dev — bundling the target backend's Docker stack for local testing is more common in integration-test frameworks than in MCP servers.

Dual-API architecture split — some SaaS platforms have read and write as separately-credentialed APIs; servers that expose both need to manage two credential lifecycles.

Very low star count (1) with a very complete repo structure — suggests a recent or under-advertised but thoughtfully-built project.

## Python-specific

### SDK / framework variant

FastMCP 2.x — specifically 2.12.3. `fastmcp==2.12.3` (implied from README's explicit mention). Import pattern likely `from fastmcp import FastMCP`.

### Python version floor

`requires-python` value: `>=3.10`.

### Packaging

build backend: not captured. Lock file: not captured. Version manager convention: `uv` / `uvx`.

### Entry point

`ghost-mcp` console script. Host-config snippet shape: `uvx ghost-mcp`.

### Install workflow expected of end users

`uvx ghost-mcp` (primary, zero-install).

### Async and tool signatures

FastMCP 2.x with network I/O → likely async.

### Type / schema strategy

FastMCP-derived (likely Pydantic internally).

### Testing

`make test` target; framework not captured. Fixture style not captured.

### Dev ergonomics

Makefile + Docker Compose for a full CMS test stack.

### Notable Python-specific choices

Explicit FastMCP version pin (2.12.3) — conservative. async/await mentioned as an implementation feature in README.

## Gaps

what couldn't be determined: exact pyproject content, stars-update timing, CI workflow details, test framework, license file (README says MIT).
