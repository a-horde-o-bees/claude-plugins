# Sample

## Identification
- url: https://github.com/lanbaoshen/mcp-jenkins
- stars: 115
- last-commit (date or relative): April 14, 2026 (v3.1.3)
- license: MIT
- default branch: master
- one-line purpose: Jenkins CI MCP server — per-request credential headers enable multi-tenant HTTP mode.

## 1. Language and runtime
- language(s) + version constraints: Python 82.4%; Python version not explicitly surfaced
- framework/SDK in use: raw MCP Python SDK (FastMCP not explicitly referenced)
- pitfalls observed:
  - what couldn't be determined: Python version floor, async/sync tool pattern, test framework, schema strategy, logging destination

## 2. Transport
- supported transports: stdio (default), sse, streamable-http (default port 9887)
- how selected: CLI flag; host/port configurable
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: uvx, pip, Docker (ghcr.io)
- published package name(s): mcp-jenkins
- install commands shown in README: `uvx mcp-jenkins`; `pip install mcp-jenkins`; `docker run ghcr.io/lanbaoshen/mcp-jenkins:latest`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `mcp-jenkins` (console script)
- wrapper scripts, launchers, stubs: Dockerfile under `/docker` (multi-platform)
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: CLI arguments for Jenkins URL, username, password, SSL verification, session singleton mode, read-only mode, transport selection with host/port; HTTP headers (`x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password`) for per-request credential passthrough
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Jenkins username + password (or API token)
- where credentials come from: CLI flags (static) or HTTP headers (per-request)
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: per-request tenant supported — `x-jenkins-*` HTTP headers allow each MCP request to target a different Jenkins
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 24 tools covering job management, build operations, queue handling, node/view queries, console output retrieval
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not explicitly surfaced
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location
- JetBrains IDE: documented integration
- VSCode Copilot Chat: `.vscode/mcp.json` entry
- Claude Desktop: JSON `mcpServers` entry
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not observed

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: `/tests/` directory present; framework not surfaced
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions (`.github/`); codecov integration
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile under `/docker` with multi-platform builds
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `.vscode/mcp.json` sample
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single package; `/docker/`, `/tests/`, `.github/` directories
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- per-request credentials via HTTP headers — enables a single deployed server to serve multiple Jenkins instances from different tenants
- session-singleton toggle — reuses one Jenkins client across tool calls for connection pooling
- streamable-http default port (9887) is published, suggesting HTTP deployment is a first-class path

## 18. Unanticipated axes observed
- decision dimensions this repo reveals:
    - per-request header-based credential passthrough (`x-jenkins-*`) turning what's usually a single-tenant stdio server into a multi-tenant HTTP service
    - session singleton vs per-request session as a deliberate switch

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / custom: raw MCP Python SDK (FastMCP not explicitly referenced)
- version pin from pyproject.toml: not surfaced
- import pattern observed: not surfaced

### Python version floor
- `requires-python` value: not explicitly surfaced

### Packaging
- build backend: pyproject.toml (uv-based)
- lock file present: not surfaced
- version manager convention: uv

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: console script `mcp-jenkins`
- actual console-script name(s): `mcp-jenkins`
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path): `uvx mcp-jenkins` or Docker

### Install workflow expected of end users
- install form + one-liner from README: `uvx mcp-jenkins` or `pip install mcp-jenkins`

### Async and tool signatures
- sync `def` or `async def`: not explicitly surfaced
- asyncio/anyio usage: not surfaced

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: not surfaced
- schema auto-derived vs hand-authored: not surfaced

### Testing
- pytest / pytest-asyncio / unittest / none: tests directory present; framework not surfaced
- fixture style: not surfaced

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: codecov integration in CI

### Notable Python-specific choices
- open bullets:
    - dedicated `/docker/` subdirectory with multi-platform build artifacts
    - JetBrains IDE integration is unusual — most MCP servers focus on Claude Desktop / Code / Cursor

## 20. Gaps
- what couldn't be determined: Python version floor, async/sync tool pattern, test framework, schema strategy, logging destination
