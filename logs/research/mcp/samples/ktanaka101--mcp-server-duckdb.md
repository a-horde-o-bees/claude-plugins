# Sample

## Identification
- url: https://github.com/ktanaka101/mcp-server-duckdb
- stars: 174
- last-commit (date or relative): May 5, 2025 (v1.1.0)
- license: MIT
- default branch: main
- one-line purpose: DuckDB MCP server — SQL query execution against DuckDB files.

## 1. Language and runtime
- language(s) + version constraints: Python (100%)
- framework/SDK in use: Anthropic MCP Python SDK
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (standard MCP)
- how selected (flag, env, separate entry, auto-detect, etc.): Implicit — stdio is the only transport documented
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI, uvx runner, Smithery registry
- published package name(s): mcp-server-duckdb
- install commands shown in README: `npx -y @smithery/cli install mcp-server-duckdb --client claude`; `uvx mcp-server-duckdb --db-path <path>`
- pitfalls observed:
  - No container or Homebrew artifacts observed

## 4. Entry point / launch
- command(s) users/hosts run: `uvx mcp-server-duckdb --db-path <path> [--readonly] [--keep-connection]`
- wrapper scripts, launchers, stubs: CLI entry point registered via package metadata; Smithery installer handles host registration
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: CLI flags only — `--db-path` (required), `--readonly`, `--keep-connection`. No env vars or config files documented.
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: None — local DuckDB file access
- where credentials come from: Not applicable
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user, single-database — one DuckDB file per server instance
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Single tool — `query` (accepts arbitrary SQL). No resources, prompts, sampling, or roots.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: None in README; MCP Inspector recommended for debugging
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop: Supported via `claude_desktop_config.json` example
- Smithery: Supported via its CLI installer
- Other editors/CLIs: Not mentioned
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: `tests/` directory present; framework not specified within fetch budget
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: `.github/workflows/` present; specific workflow contents not extracted within budget
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: None documented
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: MCP Inspector recommended; Claude Desktop JSON config shown; Smithery CLI recipe
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package Python project
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Single generic `query` tool delegates SQL generation entirely to the LLM rather than providing specialized tools
- Read-only mode leverages DuckDB's native protection, not tool-layer validation
- `--keep-connection` flag is explicit to enable TEMP objects across calls — a deliberate session-state trade-off
- Non-readonly mode auto-creates the DB file and parent directories

## 18. Unanticipated axes observed
- Connection-lifecycle flag (`--keep-connection`) as a first-class knob — a design choice most servers hide

## 19. Python-specific

### SDK / framework variant
- Raw `mcp` Python SDK — `mcp>=1.0.0`; no fastmcp
- Import pattern: low-level MCP server API (inferred)

### Python version floor
- `requires-python = ">=3.10"`

### Packaging
- build backend: `hatchling.build`
- lock file: likely uv.lock (uv/uvx ecosystem)
- version manager convention: `uv`/`uvx`

### Entry point
- `[project.scripts]`: `mcp-server-duckdb = "mcp_server_duckdb:main"`
- README host-config snippet: `"command": "uvx"`, `"args": ["mcp-server-duckdb", "--db-path", "<path>"]`

### Install workflow expected of end users
- `uvx mcp-server-duckdb` (primary), Smithery CLI installer for host setup
- No pip instructions shown

### Async and tool signatures
- `pytest>=8.3.4` in dev deps; pytest-asyncio not declared
- Source not inspected

### Type / schema strategy
- Low-level MCP SDK — hand-authored schemas

### Testing
- pytest in dev deps; `tests/` directory
- No pytest config in pyproject.toml

### Dev ergonomics
- README recommends MCP Inspector (`npx @modelcontextprotocol/inspector`)
- No Makefile/task runner observed

### Notable Python-specific choices
- Minimal pyproject.toml — only pytest in dev; no ruff/mypy/coverage
- Single-tool server, low ceremony — pragmatic Python layout

## 20. Gaps
- Test framework and CI workflow specifics not extracted within budget
- No container or Homebrew artifacts observed
