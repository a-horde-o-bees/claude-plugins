# chroma-core/chroma-mcp

## Identification
- url: https://github.com/chroma-core/chroma-mcp
- stars: ~536
- last-commit (date or relative): v0.2.6 released 2025-08-14; active
- license: Apache-2.0
- default branch: main
- one-line purpose: Chroma vector-DB MCP server — 12 tools for collection and document CRUD/query; single binary supports ephemeral / persistent / self-hosted / Chroma Cloud backing stores.

## 1. Language and runtime
- language(s) + version constraints: Python, `requires-python >= 3.10`
- framework/SDK in use: raw `mcp` Python SDK (`mcp[cli]==1.6.0`) — no FastMCP dependency
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default via MCP SDK); SSE/HTTP not called out in README
- how selected: CLI argument / env var mode controlling client type and transport
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI via uvx, Docker
- published package name(s): `chroma-mcp`
- install commands shown in README: `uvx chroma-mcp`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `uvx chroma-mcp` with flags selecting client mode (ephemeral | persistent | http | cloud)
- wrapper scripts, launchers, stubs: none
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: CLI args (primary), environment variables, optional `.env` file via `--dotenv-path`. Provider API keys via `CHROMA_<PROVIDER>_API_KEY` convention
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: API key (for Chroma Cloud and for embedding providers)
- where credentials come from: env vars / `.env` / CLI args; provider-prefixed pattern (`CHROMA_OPENAI_API_KEY`, etc.)
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single-user process; collection is per-call argument
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 12 tools — collection CRUD (create/delete/modify), document ops (add/query/update), retrieval with filtering
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: standard MCP SDK stderr logging; no bespoke metrics/tracing
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location
- Claude Desktop: JSON config snippet
- Cursor / other MCP clients: generic uvx-based config
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: none observed
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: pytest ≥8.3.5, pytest-asyncio ≥0.26.0, pytest-cov ≥4.1.0; `tests/` directory
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions workflows in `.github/workflows/`
- pitfalls observed:
  - Specific GH Actions jobs / release automation not inspected

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile present
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `.env` example; Claude Desktop snippet; uvx CLI flags well documented
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single-package (`src/chroma_mcp/`)
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Single binary supports 4 backing-store modes (ephemeral, persistent, HTTP self-hosted, Chroma Cloud) chosen at launch via flags rather than four separate entry points
- Pinned raw `mcp` SDK rather than FastMCP, which is unusual for a 2025 vector-DB server (most vendor servers have migrated to FastMCP)

## 18. Unanticipated axes observed
- decision dimensions this repo reveals: same MCP server package adapts to radically different deployment targets (in-memory vs durable local vs remote vs SaaS) through a single "client type" dimension; provider-prefixed env convention (`CHROMA_<PROVIDER>_API_KEY`) gives a uniform auth surface across multiple embedding back-ends (OpenAI, Cohere, VoyageAI)

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / custom — raw `mcp` SDK (`mcp[cli]==1.6.0`)
- version pin from pyproject.toml — exact `==1.6.0`
- import pattern observed — from `mcp.server` / `mcp.server.fastmcp` (via `mcp[cli]` extra)

### Python version floor
- `requires-python` value — `>=3.10`

### Packaging
- build backend (hatchling / setuptools / uv build / poetry-core / flit / pdm / other) — hatchling
- lock file present (uv.lock / poetry.lock / pdm.lock / none) — not confirmed
- version manager convention — `.python-version` likely (standard for uvx-published packages)

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other — `[project.scripts]` -> `chroma_mcp:main`
- actual console-script name(s) — `chroma-mcp`
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path) — `uvx chroma-mcp`

### Install workflow expected of end users
- pip / pipx / uv tool install / uvx run / poetry / source clone + venv / Docker / other — uvx (primary), Docker
- one-liner the README recommends — `uvx chroma-mcp --client-type persistent --data-dir ./chroma_data`

### Async and tool signatures
- sync `def` or `async def` — mixed; pytest-asyncio suggests async coverage

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated — Pydantic via MCP SDK; explicit `pydantic` not in deps but pulled in by mcp
- schema auto-derived vs hand-authored — auto-derived from signatures per MCP SDK idiom

### Testing
- pytest / pytest-asyncio / unittest / none — pytest + pytest-asyncio + pytest-cov
- fixture style — not inspected

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other — `mcp` CLI via `mcp[cli]`; `.env` convention

### Notable Python-specific choices
- Optional `sentence-transformers` extra lets users run locally-embedded collections without OpenAI/Cohere/Voyage keys
- Bundles *three* cloud embedding SDKs in core deps (openai, cohere, voyageai) — not extras — giving a fat install but zero-friction provider switching

## 20. Gaps
- Whether `uv.lock` is committed not confirmed
- Exact list of 12 tools beyond categories not enumerated
- Specific GH Actions jobs / release automation not inspected
