# Sample

## Identification
- url: https://github.com/motherduckdb/mcp-server-motherduck
- stars: 468
- last-commit (date or relative): March 30, 2026 (v1.0.4 release)
- license: MIT
- default branch: main
- one-line purpose: MotherDuck/DuckDB MCP server — query MotherDuck cloud and local DuckDB from one binary.

## 1. Language and runtime
- language(s) + version constraints: Python >=3.10
- framework/SDK in use: fastmcp (>=2.14,<3), Anthropic MCP SDK
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default), HTTP
- how selected (flag, env, separate entry, auto-detect, etc.): Via configuration in client-specific settings (Claude Desktop, VS Code, etc.)
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI (mcp-server-motherduck), uvx, MCP Bundle (.mcpb), GitHub releases
- published package name(s): mcp-server-motherduck
- install commands shown in README: `uvx mcp-server-motherduck --db-path :memory: --read-write --allow-switch-databases`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `mcp-server-motherduck` with optional parameters (--db-path, --read-write, --allow-switch-databases, --motherduck-token)
- wrapper scripts, launchers, stubs: Entry point configured in pyproject.toml as CLI tool invocation
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: CLI arguments for flags, environment variables for credentials (motherduck_token, AWS credentials)
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Static token via motherduck_token environment variable or --motherduck-token parameter; AWS credentials for S3 access
- where credentials come from: Environment variables, CLI arguments
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user with ability to switch databases via --allow-switch-databases flag
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: SQL query execution (read/write modes), database listing, table listing, column inspection, database switching, support for local files, S3, MotherDuck, in-memory databases
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not explicitly documented; development includes pytest with asyncio support
- pitfalls observed:
  - Logging destination and format (requires code inspection)

## 10. Host integrations shown in README or repo
- Claude Desktop: JSON-based configuration
- Claude Code: Dedicated CLI commands provided
- Cursor: Supported
- VS Code: Supported
- Codex CLI: Supported
- Gemini CLI: Supported
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

.claude-plugin wrapper mentioned as present with dedicated CLI commands

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Present; pytest (8.0+) with pytest-asyncio (0.24+); location: tests/ directory
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: .github/ directory present; specific workflow details not extracted within budget
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not observed; uv-based Python packaging preferred
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: makefile present; sample configurations for Claude Desktop integration
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package Python project with src/, tests/, pyproject.toml, uv.lock
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Uses fastmcp framework for rapid development
- Supports local and cloud databases (MotherDuck) with S3 integration
- Read-write mode flag allows toggling safety posture
- .mcpbignore file suggests bundling mechanism

## 18. Unanticipated axes observed
- Database switching as feature flag suggests multi-database workflows
- Explicit read/write mode control separates safety postures

## 19. Python-specific

### SDK / framework variant
- FastMCP 2.x — `fastmcp>=2.14,<3` in pyproject.toml
- Import pattern: `from fastmcp import FastMCP` (inferred from 2.x usage)

### Python version floor
- `requires-python = ">=3.10"`
- CI matrix not extracted

### Packaging
- build backend: `hatchling.build`
- lock file: `uv.lock` present
- version manager convention: `uv`

### Entry point
- `[project.scripts]`: `mcp-server-motherduck = "mcp_server_motherduck:main"`
- README host-config snippet: `"command": "uvx"`, `"args": ["mcp-server-motherduck", "--db-path", ":memory:", "--read-write", "--allow-switch-databases"]` — pure uvx with CLI flags

### Install workflow expected of end users
- `uvx mcp-server-motherduck` (primary), `pip install uv` / `brew install uv` as prerequisite, `.mcpb` drag-and-drop bundle for Claude Desktop, or source-clone with `uv`
- No Docker image published

### Async and tool signatures
- FastMCP 2.14 typically supports both sync and async tool signatures; exact repo style not inspected at source level
- `pytest-asyncio>=0.24` in dev deps confirms async test surface

### Type / schema strategy
- FastMCP auto-derives schemas from type hints

### Testing
- pytest + pytest-asyncio + python-dotenv + ruff
- `asyncio_mode = "auto"`, `asyncio_default_fixture_loop_scope = "function"`
- Custom `slow` marker for deselection
- `testpaths = ["tests"]`

### Dev ergonomics
- Makefile present
- `.mcpbignore` file — suggests MCP bundle (.mcpb) packaging workflow

### Notable Python-specific choices
- `.mcpb` bundle distribution is a Python-ecosystem-specific packaging path (MCP bundles for Claude Desktop drag-and-drop), observed in only a handful of repos
- Pinned FastMCP major with tight lower bound (`>=2.14,<3`) — keeps breaking-change surface bounded

## 20. Gaps
- Exact CI/CD setup and triggers (requires .github/workflows inspection)
- Logging destination and format (requires code inspection)
- Complete test coverage strategy (requires test file inspection)
