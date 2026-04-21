# echelon-ai-labs/servicenow-mcp

## Identification
- url: https://github.com/echelon-ai-labs/servicenow-mcp
- stars: 241
- last-commit (date or relative): not captured
- license: MIT
- default branch: main
- one-line purpose: ServiceNow MCP server — 60+ tools across incidents, service catalog, change requests, agile, workflows, knowledge bases; stdio and SSE ship as separate console scripts.

## 1. Language and runtime
- language(s) + version constraints: Python 99.4%; requires Python 3.11 or higher
- framework/SDK in use: raw `mcp` Python SDK; Starlette for SSE transport
- pitfalls observed:
  - Python 3.11 floor — a touch more modern than awslabs' 3.10

## 2. Transport
- supported transports: **stdio** (standard mode) and **Server-Sent Events (SSE)** via a web server
- how selected: separate console script (`servicenow-mcp-sse`) vs stdio CLI module (`python -m servicenow_mcp.cli`)
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: clone + `pip install -e .`; Docker (Dockerfile present)
- published package name(s): not captured from README
- install commands shown in README:
  - `git clone ... && python -m venv .venv && pip install -e .`
- pitfalls observed:
  - what couldn't be determined: exact pyproject dependencies, console-script vs entry-point details, CI presence, test framework specifics, Docker image publication, OAuth specifics

## 4. Entry point / launch
- command(s) users/hosts run:
  - stdio: `python -m servicenow_mcp.cli`
  - SSE: `servicenow-mcp-sse --instance-url=... --username=... --password=...`
- wrapper scripts, launchers, stubs: separate console script for SSE mode with CLI args
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: CLI args (SSE mode) or env vars (both modes) — `SERVICENOW_INSTANCE_URL`, `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD`, `SERVICENOW_AUTH_TYPE`
- pitfalls observed:
  - **Three auth mechanisms** in one server (Basic, OAuth, API Key) — selector is `SERVICENOW_AUTH_TYPE` env var

## 6. Authentication
- flow: **three methods** — Basic Auth (username/password), OAuth (client credentials), API Key
- where credentials come from: CLI args or env vars; `SERVICENOW_AUTH_TYPE` selects mechanism
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single ServiceNow instance per deployment (via env/URL)
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: **60+ tools** across:
  - Incident management
  - Service catalog
  - Change requests
  - Agile management
  - Workflows
  - Script includes
  - Changesets
  - Knowledge bases
  - User management
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not captured
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
Not captured per host
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: none
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: `tests/` directory present
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: not captured — no mention
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: CLI arg shape for SSE mode
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single-package (`servicenow_mcp/`)
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- **Two separate entry points for different transports** — `python -m servicenow_mcp.cli` (stdio) vs `servicenow-mcp-sse` (SSE); architecturally split rather than env-var-switched
- **Starlette as the SSE web framework** — an explicit choice; many other servers use FastAPI + uvicorn
- **Three auth mechanisms** in one server (Basic, OAuth, API Key) — selector is `SERVICENOW_AUTH_TYPE` env var
- **60+ tools across 9 functional areas** — very broad enterprise-ITSM surface
- Python 3.11 floor — a touch more modern than awslabs' 3.10

## 18. Unanticipated axes observed
- **Transport split across separate console scripts** — unlike servers that switch transport via env var/CLI flag, this one ships two distinct binaries. A cleaner separation but more install-time ceremony
- **Multi-auth support as a first-class feature** — enterprise SaaS servers often need it because different customer deployments mandate different auth; most community servers pick one. ServiceNow MCP leans enterprise here
- **Starlette standalone** for SSE rather than FastAPI — reveals Starlette as a viable sub-FastAPI layer for MCP servers that want HTTP transport without full REST framework overhead
- **Enterprise-tool density** — 60+ tools in 9 functional areas; enterprise platforms generate more surface area than consumer SaaS does

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: raw `mcp` Python SDK
- version pin from pyproject.toml: not captured (pyproject not read directly)
- import pattern observed: likely `from mcp.server import Server`

### Python version floor
- `requires-python` value: `>=3.11`

### Packaging
- build backend: not captured
- lock file present: not captured
- version manager convention: pip (`pip install -e .`)

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: both — `__main__`-style module invocation (`python -m servicenow_mcp.cli`) and a console script (`servicenow-mcp-sse`)
- actual console-script name(s): `servicenow-mcp-sse`
- host-config snippet shape: stdio — `python -m servicenow_mcp.cli`; SSE — `servicenow-mcp-sse` with CLI args

### Install workflow expected of end users
- install form + one-liner from README: `pip install -e .` after clone

### Async and tool signatures
- sync `def` or `async def`: not captured; Starlette suggests async for SSE path

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: not captured

### Testing
- pytest / pytest-asyncio / unittest / none: tests/ directory present
- fixture style: not captured

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: not captured

### Notable Python-specific choices
- Plain `pip install -e .` installation workflow — more conservative than the uv/uvx-heavy trend among newer servers
- Separate CLI entry for each transport — the opposite of `AlwaysSany/deepl-fastmcp-python-server`'s one-binary multi-transport model

## 20. Gaps
- what couldn't be determined: exact pyproject dependencies, console-script vs entry-point details, CI presence, test framework specifics, Docker image publication, OAuth specifics
