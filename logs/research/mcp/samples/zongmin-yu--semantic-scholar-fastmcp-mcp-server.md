# Sample

## Identification
- url: https://github.com/zongmin-yu/semantic-scholar-fastmcp-mcp-server
- stars: ~125
- last-commit (date or relative): not surfaced
- license: MIT
- default branch: main
- one-line purpose: Semantic Scholar MCP server — dual-protocol MCP (stdio) + HTTP REST in the same process; FastMCP-backed.

## 1. Language and runtime
- language(s) + version constraints: Python 3.10+
- framework/SDK in use: FastMCP
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (MCP default); **HTTP bridge** on port 8000 (bundled in-process)
- how selected: stdio primary; HTTP bridge toggled via env var (`SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE`)
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI (`pip install semantic-scholar-fastmcp`), uvx, Docker (+ docker-compose)
- published package name(s): `semantic-scholar-fastmcp`
- install commands shown in README: `pip install semantic-scholar-fastmcp`, `uvx semantic-scholar-fastmcp`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `semantic-scholar-mcp-server` console script
- wrapper scripts, launchers, stubs: docker-compose orchestration shipped
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables — `SEMANTIC_SCHOLAR_API_KEY`, `SEMANTIC_SCHOLAR_ENABLE_HTTP_BRIDGE`, `SEMANTIC_SCHOLAR_HTTP_BRIDGE_HOST`, `SEMANTIC_SCHOLAR_HTTP_BRIDGE_PORT`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: optional API key
- where credentials come from: `SEMANTIC_SCHOLAR_API_KEY` env var (higher rate limits)
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single-user
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 16 tools — 8 paper search/discovery, 2 citation analysis, 4 author info, 2 recommendation
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not surfaced
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location
- Claude Desktop: JSON config snippet (uvx command)
- HTTP bridge: serves on 0.0.0.0:8000 for non-MCP consumers
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: `tests/` directory; framework not detailed
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions in `.github/`
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile **and** docker-compose.yml present
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `[dev]` optional extra
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single-package (`semantic_scholar/` with `server.py`, `mcp.py`, `config.py`, utility modules)
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Bundles an **HTTP bridge** *alongside* the MCP protocol — the same server process exposes both MCP tools and a generic HTTP endpoint (port 8000), enabled by default
- 16 tools organized into 4 explicit functional groups — tool categorization baked into documentation structure
- Separate `mcp.py` and `server.py` files — likely splits MCP-protocol surface from HTTP/business-logic surface

## 18. Unanticipated axes observed
- decision dimensions this repo reveals: dual protocol exposure (MCP stdio + HTTP REST) in a single process, rather than picking one — the HTTP bridge is on by default, making this usable by non-MCP clients out of the box. This is a distinct pattern from "pick a transport" (which is still one protocol); this server serves two protocols simultaneously

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom — FastMCP
- version pin from pyproject.toml — not surfaced
- import pattern observed — `from fastmcp import FastMCP` likely

### Python version floor
- `requires-python` value — `>=3.10`

### Packaging
- build backend — not surfaced
- lock file present — not surfaced
- version manager convention — pip + uvx

### Entry point
- `[project.scripts]` console script / `__main__.py` / bare script / other — `[project.scripts]` → `semantic-scholar-mcp-server`
- actual console-script name(s) — `semantic-scholar-mcp-server`
- host-config snippet shape — `uvx semantic-scholar-fastmcp`

### Install workflow expected of end users
- pip / pipx / uv tool install / uvx run / poetry / source clone + venv / Docker / other — pip, uvx, Docker
- one-liner the README recommends — `pip install semantic-scholar-fastmcp`

### Async and tool signatures
- sync `def` or `async def` — likely async (FastMCP + httpx)

### Type / schema strategy
- Pydantic via FastMCP

### Testing
- pytest / pytest-asyncio / unittest / none — `[dev]` extra implies pytest but not confirmed

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other — `[dev]` extra

### Notable Python-specific choices
- In-process HTTP bridge is interesting — suggests FastMCP's `streamable-http` transport is not being used; instead, a custom bridge layer lives alongside

## 20. Gaps
- HTTP bridge internals not inspected (is it `streamable-http`, `sse`, or a custom FastAPI app?)
- Version pins for FastMCP not surfaced
- Lock file convention not confirmed
