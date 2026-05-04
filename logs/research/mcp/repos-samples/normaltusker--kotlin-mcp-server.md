# Sample

Mirrors of `https://github.com/normaltusker/kotlin-mcp-server`. Kotlin/Android dev-assistant MCP server — Python server (despite the name) carrying both `mcp` and `fastmcp`; single-file 112 KB monolith installed via `install.py`. 28 stars, AGPL-3.0, default branch `main`, 99 commits on main.

## Server runtime

### Python with both MCP SDK and FastMCP declared

Both `mcp>=1.0.0` (labeled "Official MCP SDK") and `fastmcp>=2.0.0` declared in `requirements.txt` — mixed dependency profile. Anthropic's Claude Agent SDK referenced. Python 3.8+ floor (3.9+ recommended). Black target range `py38-py312` — broad tested range.

## Transport

### stdio

Standard MCP stdio protocol.

### REST API bridge alongside MCP

HTTP REST API bridge via `vscode_bridge.py` on port 8080 (configurable) for IDE-native integration outside the MCP client.

### Selection mechanism

Entry-point selection via installation mode — portable (direct), system (CLI), or module (`python -m`). Bridge runs as a separate process on its own port.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

32 tools across categories — Core Development (7), UI Development (4), Architecture & Patterns (6), Security & Compliance (4), AI/ML Integration (3), File Management (2), API Integration (4), Testing (2), Git Tools (4), Quality of Life (7).

## Configuration delivery

### Environment variables

`PROJECT_PATH`, `WORKSPACE_PATH`, `MCP_ENCRYPTION_PASSWORD`, plus compliance-mode env vars.

### Auto-generated host-config JSON files

Installer (`install.py`) writes ready-to-paste `mcp_config_claude.json`, `mcp_config_vscode.json`, `mcp_config.json` per supported host.

### Dotenv file

Optional `.env` file for advanced AI/security customization.

## Authentication

### Multi-scheme client auth (API key / OAuth / JWT / Basic / Bearer)

Multiple external API authentication schemes supported — API Keys, OAuth 2.0, JWT tokens, Basic HTTP, Bearer tokens. Server-side rate limiting, circuit breaker, and audit logging layered on top.

## Multi-tenancy

### Workspace-scoped sandboxing within a single tenant

Single-user per workspace; workspace-specific via `WORKSPACE_PATH` environment variable. Audit logging suggests multi-tenant awareness even within the single-user model.

## Distribution channel

### Custom Python installer script

Installation via `python3 install.py` — interactive automated installer with three modes (portable/system/module). Replaces both pip and uvx for the end user.

### Source clone with editable install

`pip install -r requirements.txt` for manual install from a clone. No PyPI publication.

## Entry point and launch

### Bare interpreter + script path

`python3 kotlin_mcp_server.py` — direct interpreter + script invocation.

### Module invocation / `python -m <module>` fallback

`python3 -m kotlin_mcp_server` — module mode.

### Console script via `[project.scripts]` / npm bin

`kotlin-android-mcp` registered as a system command after install.

### Multiple entry points per transport

Three invocation modes selectable by installation type; HTTP REST bridge via `vscode_bridge.py` runs as a separate launch path.

## Build and packaging

### Requirements-driven (legacy Python)

`requirements.txt` is the primary dependency manifest; no lock file confirmed; build backend not directly extracted from `pyproject.toml`.

### Python version pinning

Black target range `py38-py312` — broad tested range. README floor: Python 3.8+ (3.9+ recommended). `pyproject.toml` declares broad compatibility.

## Schema and types

### Hand-authored tool schemas

MyPy strict type checking enforced. Hand-authored schemas likely given the raw MCP SDK usage alongside FastMCP.

### Async model (cross-cutting)

pytest + pytest_asyncio in `pyproject.toml` tool config; async tool execution stated in README ("modular architecture with 6 specialized modules").

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Docker support mentioned for portability in overview; specific Dockerfile content not provided.

### Docker Compose for local dev

`docker-compose.yml` for containerized deployment — `docker-compose up -d kotlin-mcp-server`.

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio configured in `pyproject.toml`. `pytest.ini` at root + `pyproject.toml` config — dual-config layout. Test files excluded from coverage metrics.

### MyPy strict + Bandit security scans alongside tests

MyPy strict type checking enforced. Bandit security scans excluding tests.

### Linter/formatter test gate

Black formatting (100-char line limit), isort import sorting enforced as part of lint surface.

## CI

### GitHub Actions

GitHub Actions implied by `pyproject.toml` tool config (Black, isort, MyPy strict, Bandit).

## Host integration

### Claude Desktop

Auto-generated `mcp_config_claude.json` config file.

### VS Code / VS Code Insiders / Visual Studio family

Auto-generated `mcp_config_vscode.json` config file.

### Cursor

Uses the same auto-generated `mcp_config_vscode.json` file as VS Code.

### JetBrains IDE

Native support documented.

### Generic / host-agnostic snippet

Auto-generated `mcp_config.json` for generic MCP clients.

## Repository layout

### Single-file script / monolith

Single-package Python server centered on `kotlin_mcp_server.py` — a unified 112 KB monolith with 32 tools. Supporting files: `vscode_bridge.py` (HTTP REST bridge); `pyproject.toml`, `.env` (optional); installed via `install.py`.

## Safety and security posture

### Workspace path enforcement (canonicalization)

Workspace-specific access via `WORKSPACE_PATH` env var. Audit logging for security/compliance modes (GDPR, HIPAA mentioned).

### Audit logging for compliance modes

Audit logging for security events with GDPR and HIPAA compliance modes mentioned in the README.

## Domain logic and embedded intelligence

### Deterministic optimization layered on top of raw ops

Intelligent proxy system (v2.0 evolution) provides "complete, context-aware implementations" rather than stubs — sophisticated server architecture pattern that layers analysis on top of raw IDE ops.

## Caching and rate-limiting infrastructure

### Token-bucket rate limiter

Server-side rate limiting for external API calls.

### Circuit breaker for external calls

Circuit breaker for external API calls in MCP context — protects against upstream failures cascading into the server.

## Observability

### Audit logging for compliance modes

Audit logging for security events surfaces both as observability and as compliance posture (GDPR, HIPAA modes).

### None / unspecified

No explicit metrics or tracing documented in extract.

## Developer ergonomics

### Custom installer-orchestrator

Interactive `install.py` is the primary dev-ergonomics surface — handles environment setup, dependency install, and per-host config file generation across Claude Desktop, VS Code, Cursor, generic MCP clients.

### Sample MCP client configs in repo

Auto-generated config files (`mcp_config_claude.json`, `mcp_config_vscode.json`, `mcp_config.json`) ship as part of the install flow.

## Documentation surface

### README as the canonical surface

README documents the 32 tools and installation modes.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin/` or `.claude/skills/` wrapper. Standalone server with auto-generated IDE integration configs.

## Release and lifecycle

### License — Copyleft (AGPL-3.0)

AGPL-3.0 — strong network-copyleft license; derivatives served over a network must remain open under the same terms.

### Active development

99 commits on main; recent activity signaled by ongoing development.
