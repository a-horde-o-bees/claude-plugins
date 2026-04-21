# alpacahq/alpaca-mcp-server

## Identification
- url: https://github.com/alpacahq/alpaca-mcp-server
- stars: 670
- last-commit (date or relative): not captured
- license: MIT
- default branch: main
- one-line purpose: Alpaca trading MCP server — ~60 tools across accounts, orders, positions, watchlists, market/crypto/options data, corporate actions, and news; paper-trading by default.

## 1. Language and runtime
- language(s) + version constraints: Python 96.8%; `requires-python = ">=3.10"`
- framework/SDK in use: FastMCP 2.x (`fastmcp>=2.0.0`) — README notes "complete rewrite built with FastMCP and OpenAPI"
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default); streamable-http (configurable port, default localhost:8000)
- how selected: CLI flag / env var on launch
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI (`alpaca-mcp-server`); `uvx`; Docker (`docker build -t mcp/alpaca:latest .`)
- published package name(s): `alpaca-mcp-server`
- install commands shown in README: `uvx alpaca-mcp-server`
- pitfalls observed:
  - **Official vendor-published server** — published by Alpaca itself; operates as their canonical MCP entry

## 4. Entry point / launch
- command(s) users/hosts run: `uvx alpaca-mcp-server`
- wrapper scripts, launchers, stubs: console script `alpaca-mcp-server` → `alpaca_mcp_server.cli:main`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables in MCP client config — `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_PAPER_TRADE`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Alpaca API key + secret pair
- where credentials come from: env vars injected by the MCP client
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single-user per key pair
- pitfalls observed:
  - **Paper-mode-as-default** — mutation-capable MCP server with a sandbox default; a safety pattern other trading/finance servers should emulate

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: tools only — grouped:
  - Account & Portfolio (7), Trading/Orders (8), Positions (6), Watchlists (7), Assets & Market Info (7), Stock Data (8), Crypto Data (7), Options Data (7), Corporate Actions (2), News (1)
  - **~60 tools total** across 10 categories
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not captured
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop — `claude_desktop_config.json` path for Mac/Windows
- Cursor — `~/.cursor/mcp.json`
- VS Code — `.vscode/mcp.json`
- PyCharm — Settings → Tools → MCP
- Gemini CLI — `settings.json`
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: none at this level; listed in Claude Desktop config format
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: multi-layered — integrity tests, server construction tests, paper-API integration tests; pytest + pytest-asyncio declared as dev deps
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions on every PR
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: comprehensive host-specific config snippets in README
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single-package (`alpaca_mcp_server/`)
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- **Official vendor-published server** — published by Alpaca itself; operates as their canonical MCP entry
- **Built on FastMCP + OpenAPI-derived generation** — README notes the server is a rewrite using an OpenAPI-based approach, aligning with how `awslabs.openapi-mcp-server` works but presumably pre-generated rather than dynamic
- **Paper-trading mode as default** (`ALPACA_PAPER_TRADE=true` default) — safer posture for LLM-driven trading
- **Minimal dependency set** — only `fastmcp`, `httpx`, `python-dotenv`, `click` at runtime; no Alpaca SDK dependency (likely hand-rolled HTTPS calls)
- **Host-integration coverage** — 5 different MCP clients documented in README (Claude Desktop, Cursor, VS Code, PyCharm, Gemini CLI) — broader than any other repo seen in this pass

## 18. Unanticipated axes observed
- **Vendor-authored vs community-authored MCP server** as a trust dimension — the vendor's own MCP server comes with a credibility signal that derivative servers don't
- **Paper-mode-as-default** — mutation-capable MCP server with a sandbox default; a safety pattern other trading/finance servers should emulate
- **Broad host-config documentation** — PyCharm MCP support documented, which is less widely advertised than Claude Desktop
- **Click-based CLI wrapper** around FastMCP — `alpaca_mcp_server.cli:main` suggests richer argument handling than typical `fastmcp.run()` entry

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom: FastMCP 2.x (`fastmcp>=2.0.0`)
- version pin from pyproject.toml: `fastmcp>=2.0.0`, `httpx>=0.27.0`, `python-dotenv>=1.0.0`, `click>=8.1.0`
- import pattern observed: likely `from fastmcp import FastMCP`; CLI wrapper via `click`

### Python version floor
- `requires-python` value: `>=3.10`

### Packaging
- build backend: hatchling
- lock file present: not captured
- version manager convention: `uv` / `uvx`

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: console script via click
- actual console-script name(s): `alpaca-mcp-server`
- host-config snippet shape: `uvx alpaca-mcp-server`

### Install workflow expected of end users
- install form + one-liner from README: `uvx alpaca-mcp-server`

### Async and tool signatures
- sync `def` or `async def`: `httpx` + FastMCP 2 → async likely

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: not captured directly; FastMCP-auto-derived

### Testing
- pytest / pytest-asyncio / unittest / none: pytest + pytest-asyncio
- fixture style: not captured

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: ruff + mypy + pytest dev stack

### Notable Python-specific choices
- No `alpaca-py` SDK dependency — handles HTTPS + auth directly via `httpx`
- `click` for CLI orchestration, despite FastMCP having its own runner
- Version 2.0.1 at time of capture — active maintenance

## 20. Gaps
- what couldn't be determined: exact last commit date, streamable-http auth flow (none? API key? shared secret?), whether there's a Docker Hub published image, OpenAPI spec origin (internal or published), exact async usage
