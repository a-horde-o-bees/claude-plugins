# Sample

## Identification
- url: https://github.com/normaltusker/kotlin-mcp-server
- stars: 28
- last-commit (date or relative): Recent (99 commits on main branch; specific date not in provided content)
- license: AGPL-3.0
- default branch: main
- one-line purpose: Kotlin/Android dev-assistant MCP server — Python server (despite the name) carrying both `mcp` and `fastmcp`; single-file 112 KB monolith installed via `install.py`.

## 1. Language and runtime
- language(s) + version constraints: Python 3.8+ (3.9+ recommended); supporting Kotlin (3.5%), TypeScript (1.7%) components
- framework/SDK in use: Anthropic's Claude Agent SDK with Model Context Protocol (MCP); Python 3.8+ standard library
- pitfalls observed:
  - Specific Python version tested in CI not documented (pyproject.toml specifies py38-py312)

## 2. Transport
- supported transports: Stdio (standard MCP protocol), HTTP via REST API bridge (`vscode_bridge.py`), IDE-native integration (VS Code, JetBrains, Claude Desktop)
- how selected (flag, env, separate entry, auto-detect, etc.): Entry point selection via installation mode: portable (direct), system (CLI), or module (`python -m`)
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: Source distribution via interactive installer (`install.py`), direct Python execution, Python module invocation
- published package name(s): Not published to PyPI; installed from source only
- install commands shown in README: `python3 install.py` (interactive automated setup); direct execution from project directory; Python module mode
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: Primary: `kotlin_mcp_server.py` (unified server with 32 tools); callable via: direct execution, system command (`kotlin-android-mcp`), Python module (`python -m kotlin_mcp_server`)
- wrapper scripts, launchers, stubs: None documented; HTTP bridge via `vscode_bridge.py` for REST API access on port 8080 (configurable)
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Dynamic configuration via three mechanisms: (1) Interactive automated setup (`install.py`), (2) Environment variables (`PROJECT_PATH`, `WORKSPACE_PATH`, `MCP_ENCRYPTION_PASSWORD`, compliance modes), (3) Auto-generated IDE config files (`mcp_config_claude.json`, `mcp_config_vscode.json`, `mcp_config.json`); optional `.env` file for advanced AI/security customization
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Multiple external API authentication schemes: API Keys, OAuth 2.0, JWT tokens, Basic HTTP, Bearer tokens; server-side rate limiting, circuit breaker, audit logging
- where credentials come from: Environment variables, configuration files, IDE config files (auto-generated)
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user per workspace; workspace-specific via `WORKSPACE_PATH` environment variable; audit logging suggests multi-tenant awareness
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 32 comprehensive tools across categories: Core Development (7), UI Development (4), Architecture & Patterns (6), Security & Compliance (4), AI/ML Integration (3), File Management (2), API Integration (4), Testing (2), Git Tools (4), Quality of Life (7)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Audit logging for security events; no explicit metrics or tracing documented in provided content
- pitfalls observed:
  - Audit logging for security/compliance (GDPR, HIPAA modes mentioned)

## 10. Host integrations shown in README or repo
- Claude Desktop: Yes; auto-generated config file `mcp_config_claude.json`
- Claude Code: Not explicitly mentioned
- Cursor: Yes; auto-generated config file `mcp_config_vscode.json` (shared with VS Code)
- VS Code: Yes; auto-generated config file `mcp_config_vscode.json`
- JetBrains IDEs: Yes; native support documented
- Other: HTTP REST bridge for custom client integration
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present; this is a standalone server with IDE integration configs auto-generated

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Testing framework configured in `pyproject.toml` (pytest, pytest_asyncio); test files excluded from coverage metrics; MyPy strict type checking enforced
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions implied by pyproject.toml; Black formatting (100-char line limit), isort import sorting, MyPy strict type checking, Bandit security scans (excluding tests)
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Docker support mentioned for portability in overview; no specific Dockerfile content provided
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Interactive `install.py` handles configuration; auto-generated config files for Claude Desktop, VS Code, Cursor, generic MCP clients; 32 tools with clear categorization
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Single-package Python server; primary file: `kotlin_mcp_server.py` (unified 32-tool server); supporting: `vscode_bridge.py` (HTTP REST bridge); config: `pyproject.toml`, `.env` (optional); installed via: `install.py`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Unified monolithic server v2.0 architecture evolved from template-based generation; maintains backward compatibility
- Intelligent proxy system enables "complete, context-aware implementations" rather than stubs
- Interactive installer with automated IDE configuration generation (Claude Desktop, VS Code, Cursor, generic)
- LSP-like capabilities suggest advanced IDE integration patterns
- 32-tool design suggests comprehensive Kotlin/Android development support
- V2.0 introduced proxy architecture with intelligent transformations

## 18. Unanticipated axes observed
- Android/Kotlin-specific MCP server (rare specialization; most servers are language-agnostic)
- Circuit breaker and rate limiting for external API calls in MCP context
- Intelligent proxy system (v2.0 evolution) suggests sophisticated server architecture patterns
- Tool count (32) unusually high; suggests comprehensive domain coverage
- Audit logging for security/compliance (GDPR, HIPAA modes mentioned)

## 19. Python-specific

### SDK / framework variant
- Both `mcp>=1.0.0` (labeled "Official MCP SDK") AND `fastmcp>=2.0.0` in requirements.txt
- Import pattern: mixed — both SDKs pulled in

### Python version floor
- README: Python 3.8+ (3.9+ recommended)
- black target range: `py38-py312` — broad tested range
- pyproject.toml declares broad compatibility

### Packaging
- build backend: not directly extracted (pyproject.toml only exposed lint/test tool config in fetch)
- lock file: none confirmed (requirements.txt primary)
- version manager convention: plain pip; `python3 install.py` installer orchestrates

### Entry point
- Three invocation modes: `python3 kotlin_mcp_server.py`, `kotlin-android-mcp` (system install), `python3 -m kotlin_mcp_server` (module)
- HTTP REST bridge via `vscode_bridge.py`

### Install workflow expected of end users
- `python3 install.py` (interactive installer, 3 modes: portable/system/module)
- `pip install -r requirements.txt` for manual
- Docker Compose: `docker-compose up -d kotlin-mcp-server`

### Async and tool signatures
- pytest + pytest_asyncio in pyproject.toml tool config
- Async tool execution stated in README ("modular architecture with 6 specialized modules")

### Type / schema strategy
- MyPy strict type checking enforced
- Hand-authored schemas likely given raw MCP SDK usage

### Testing
- pytest + pytest-asyncio
- pytest.ini at root + pyproject.toml config — dual-config layout
- Bandit security scans excluding tests

### Dev ergonomics
- Interactive `install.py` is the primary dev ergonomics
- `docker-compose.yml` for containerized deployment
- Multiple auto-generated IDE config files (`mcp_config_claude.json`, etc.)

### Notable Python-specific choices
- Carries both mcp + fastmcp as dependencies — unusual; most repos pick one
- `python3 install.py`-driven installation — similar to samuelgursky/davinci-resolve-mcp pattern of bespoke installer scripts replacing pip
- Broad Python version range (3.8-3.12 targeted) — inclusive floor for compatibility
- AGPL-3.0 license uncommon in MCP sample (mostly MIT/Apache)
- Massive single-file `kotlin_mcp_server.py` (~112 KB) — monolith architecture

## 20. Gaps
- Specific Python version tested in CI not documented (pyproject.toml specifies py38-py312)
- Docker/Dockerfile details not provided (mentioned for portability but not detailed)
- HTTP bridge transport implementation details not specified
- V2.0 proxy architecture not fully explained in provided content
