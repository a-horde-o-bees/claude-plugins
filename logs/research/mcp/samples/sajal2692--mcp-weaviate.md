# sajal2692/mcp-weaviate

## Identification
- url: https://github.com/sajal2692/mcp-weaviate
- stars: ~5
- last-commit (date or relative): v0.2.0 (2025-09-03)
- license: MIT
- default branch: main
- one-line purpose: Weaviate vector-DB MCP server — tenancy passed as a tool argument (per-call), not server config.

## 1. Language and runtime
- language(s) + version constraints: Python 100%; version via `.python-version`
- framework/SDK in use: FastMCP (exact version pin not surfaced)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default), streamable-http
- how selected: CLI argument / env config
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI via uvx (`uvx mcp-weaviate`)
- published package name(s): `mcp-weaviate`
- install commands shown in README: `uvx mcp-weaviate --help`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `uvx mcp-weaviate`
- wrapper scripts, launchers, stubs: entry at `src.main`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables for API keys and Weaviate connection parameters
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: API keys for embedding providers and Weaviate Cloud
- where credentials come from: OpenAI / Cohere (optional) / WCS API keys via env vars
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: **multi-tenancy supported** — README explicitly calls out multi-tenancy as a feature of the search tools
- pitfalls observed:
  - First-class multi-tenancy in tool signatures — rare across Python MCP servers which typically treat tenancy as external config
  - decision dimensions this repo reveals: exposing *per-tenant* search tools as a first-class MCP concept — tenancy becomes an argument, not a server-config dimension

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 11 tools — connection checks, schema info, collection listing, object retrieval, semantic/keyword/hybrid search (with per-tenant variants)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not surfaced
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location
- Claude Desktop: implied via `uvx` command pattern
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: none observed
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: pytest via `uv run pytest`; `tests/` directory
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions workflow present
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: none observed
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `uv run ruff check`, `uv run mypy`
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single-package (`src/`)
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- First-class multi-tenancy in tool signatures — rare across Python MCP servers which typically treat tenancy as external config
- Supports two embedding providers (OpenAI, Cohere) with Cohere as optional — graceful degradation if Cohere key absent

## 18. Unanticipated axes observed
- decision dimensions this repo reveals: exposing *per-tenant* search tools as a first-class MCP concept — tenancy becomes an argument, not a server-config dimension

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom — FastMCP
- version pin from pyproject.toml — not surfaced
- import pattern observed — `from fastmcp import FastMCP`

### Python version floor
- `requires-python` value — via `.python-version` (exact value not read)

### Packaging
- build backend — not surfaced (uv-backed)
- lock file present — `uv.lock` likely
- version manager convention — uv

### Entry point
- `[project.scripts]` console script / `__main__.py` / bare script / other — `[project.scripts]` (name: `mcp-weaviate`) → `src.main` style
- actual console-script name(s) — `mcp-weaviate`
- host-config snippet shape — `uvx mcp-weaviate`

### Install workflow expected of end users
- pip / pipx / uv tool install / uvx run / poetry / source clone + venv / Docker / other — uvx primary
- one-liner the README recommends — `uvx mcp-weaviate --help`

### Async and tool signatures
- sync `def` or `async def` — weaviate-client has async surface; likely async

### Type / schema strategy
- Pydantic via FastMCP

### Testing
- pytest / pytest-asyncio / unittest / none — pytest
- fixture style — not inspected

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other — ruff + mypy as separate `uv run` commands

### Notable Python-specific choices
- Source entry uses `src.main` style rather than a package name — suggests `src/` is an implicit package root, which requires src-layout support in the build backend

## 20. Gaps
- Exact FastMCP version pin not read
- Python floor not confirmed
- No pyproject.toml content verified
