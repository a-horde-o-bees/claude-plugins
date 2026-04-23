# thenets/ghost-mcp

## Identification
- url: https://github.com/thenets/ghost-mcp
- stars: 1
- last-commit (date or relative): not captured
- license: MIT
- default branch: main
- one-line purpose: Ghost blog CMS MCP server — dual Content + Admin API coverage with JWT auto-renewal; Docker Compose local stack provided.

## 1. Language and runtime
- language(s) + version constraints: Python 92.5%; Python 3.10+ required
- framework/SDK in use: **FastMCP 2.12.3** (explicit version in README)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (implied by `uvx` invocation)
- how selected: default
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI `ghost-mcp` (via `uvx ghost-mcp`); clone + `make run`; Docker Compose for the full Ghost+MySQL test stack
- published package name(s): `ghost-mcp`
- install commands shown in README: `uvx ghost-mcp`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `uvx ghost-mcp`; `make run` (dev); `make dev` (auto-reload)
- wrapper scripts, launchers, stubs: `src/ghost_mcp/server.py` is the entry point
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: env vars — `GHOST_URL` and Ghost API keys (Content API and/or Admin API); env-var selection drives which API surface is active
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow:
  - **Content API**: query-parameter authentication with 26-character hex API keys
  - **Admin API**: JWT tokens generated from `id:secret` format (24-char + 64-char hex); tokens expire after 5 minutes with **automatic renewal and caching**
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single Ghost blog per instance (one `GHOST_URL`)
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 15+ tools across:
  - Content API: 10 read-only (posts, pages, tags, authors, settings, site info, search)
  - Admin API: 6 read/write (create/update/delete posts/pages/tags)
  - Utility: connection check
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not captured
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop — standard MCP client config pattern with `uvx ghost-mcp` + env vars
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: none
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: `make test`, `make test-connection`; GitHub Actions workflows directory present
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions (workflows present, details not extracted)
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: **full Docker Compose setup with Ghost 5.x + MySQL 8.0** — for end-to-end local testing, not server deployment. Includes health checks and volume persistence
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Makefile targets (`make run`, `make dev`, `make test`, `make test-connection`); Docker Compose for CMS backend
- pitfalls observed:
  - **Makefile-first workflow** — targets for run/dev/test/connection-check

## 16. Repo layout
- single-package / monorepo / vendored / other: single-package (`src/ghost_mcp/`)
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- **Dual-API design** — Content API (read-only, query-param auth) and Admin API (read/write, JWT) exposed through distinct tool groups within one server
- **JWT auto-renewal and caching inside the MCP server** — 5-minute token lifetime handled transparently; an unusual amount of auth logic for an MCP server
- **Ghost+MySQL Docker Compose for dev** — not for deploying the MCP server, but for bringing up the CMS backend to test against; a notable dev-ergonomics investment for a 1-star repo
- **Makefile-first workflow** — targets for run/dev/test/connection-check
- FastMCP version pinned explicitly to 2.12.3 — a precise pin signals version-awareness

## 18. Unanticipated axes observed
- **Server-managed token rotation** — most MCP servers assume static creds; this one refreshes JWTs every 5 minutes. Auth mechanics live in the server rather than the LLM or user
- **Companion infrastructure in the repo for end-to-end dev** — bundling the target backend's Docker stack for local testing is more common in integration-test frameworks than in MCP servers
- **Dual-API architecture split** — some SaaS platforms have read and write as separately-credentialed APIs; servers that expose both need to manage two credential lifecycles
- Very low star count (1) with a very complete repo structure — suggests a recent or under-advertised but thoughtfully-built project

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: FastMCP 2.x — specifically 2.12.3
- version pin from pyproject.toml: `fastmcp==2.12.3` (implied from README's explicit mention)
- import pattern observed: likely `from fastmcp import FastMCP`

### Python version floor
- `requires-python` value: `>=3.10`

### Packaging
- build backend: not captured
- lock file present: not captured
- version manager convention: `uv` / `uvx`

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: `ghost-mcp` console script
- actual console-script name(s): `ghost-mcp`
- host-config snippet shape: `uvx ghost-mcp`

### Install workflow expected of end users
- install form + one-liner from README: `uvx ghost-mcp` (primary, zero-install)

### Async and tool signatures
- sync `def` or `async def`: FastMCP 2.x with network I/O → likely async

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: FastMCP-derived (likely Pydantic internally)

### Testing
- pytest / pytest-asyncio / unittest / none: make test target; framework not captured
- fixture style: not captured

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: **Makefile + Docker Compose for a full CMS test stack**

### Notable Python-specific choices
- Explicit FastMCP version pin (2.12.3) — conservative
- async/await mentioned as an implementation feature in README

## 20. Gaps
- what couldn't be determined: exact pyproject content, stars-update timing, CI workflow details, test framework, license file (README says MIT)
