# Sample

Mirrors of `https://github.com/alpacahq/alpaca-mcp-server`. Alpaca trading MCP server — ~60 tools across accounts, orders, positions, watchlists, market/crypto/options data, corporate actions, and news; paper-trading by default. 670 stars, MIT, default branch `main`, vendor-authored (Alpaca).

## Server runtime

### Python with FastMCP

Python server (96.8% Python) on FastMCP 2.x — `fastmcp>=2.0.0` declared in `pyproject.toml`. README notes the server is a "complete rewrite built with FastMCP and OpenAPI." Likely import `from fastmcp import FastMCP`. Async likely throughout given `httpx` + FastMCP 2 conventions; not directly verified. No `alpaca-py` SDK dependency — handles HTTPS + auth directly via `httpx`. Minimal runtime dep set: `fastmcp`, `httpx`, `python-dotenv`, `click`.

## Transport

### stdio

stdio default.

### Streamable HTTP

Configurable port (default `localhost:8000`).

### Selection mechanism

CLI flag / env var on launch.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

~60 tools total across 10 categories — Account & Portfolio (7), Trading/Orders (8), Positions (6), Watchlists (7), Assets & Market Info (7), Stock Data (8), Crypto Data (7), Options Data (7), Corporate Actions (2), News (1). Tools-only surface (no resources/prompts surfaced).

## Configuration delivery

### Environment variables

`ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_PAPER_TRADE` injected by the MCP client config.

## Authentication

### Static API key / token via env var

Alpaca API key + secret pair via `ALPACA_API_KEY` / `ALPACA_SECRET_KEY` env vars.

## Multi-tenancy

### Single-user / single-tenant per process

One key pair per process.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published to PyPI as `alpaca-mcp-server`; canonical install command `uvx alpaca-mcp-server`.

### Docker / OCI image

`docker build -t mcp/alpaca:latest .` from the in-repo Dockerfile.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `alpaca-mcp-server` → `alpaca_mcp_server.cli:main`.

### `uvx <package>`

Host-config snippet shape: `uvx alpaca-mcp-server`.

### Click-based CLI wrapper (Python)

Click-based CLI (`alpaca_mcp_server.cli:main`) wraps FastMCP's runner, suggesting richer argument handling than typical bare `fastmcp.run()` invocation despite FastMCP having its own runner.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. Pin discipline: `fastmcp>=2.0.0`, `httpx>=0.27.0`, `python-dotenv>=1.0.0`, `click>=8.1.0`. Version manager convention: uv / uvx.

### Python version pinning

`requires-python = ">=3.10"`.

### Pin discipline (Python)

Loose pins (`>=` floors) on `fastmcp`, `httpx`, `python-dotenv`, `click` — minimal-ceremony posture.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP-auto-derived schemas via Pydantic at registration time (per FastMCP convention).

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile at repo root.

## Test stack

### pytest with async + coverage

Multi-layered tests — integrity tests, server-construction tests, paper-API integration tests; pytest + pytest-asyncio declared as dev deps.

### Linter/formatter test gate

ruff + mypy + pytest dev stack.

## CI

### GitHub Actions

GitHub Actions on every PR.

## Host integration

### Claude Desktop

`claude_desktop_config.json` paths shown for Mac/Windows.

### Cursor

`~/.cursor/mcp.json`.

### VS Code / VS Code Insiders / Visual Studio family

`.vscode/mcp.json`.

### JetBrains IDE

PyCharm via Settings → Tools → MCP — explicitly documented integration path.

### Codex CLI / Copilot CLI / Gemini CLI

Gemini CLI via `settings.json`.

## Documentation surface

### Per-host README integration sections

Comprehensive host-specific config snippets in README — 5 distinct host integration sections (Claude Desktop, Cursor, VS Code, PyCharm, Gemini CLI).

## Repository layout

### Single-package src-layout

Single-package layout under `alpaca_mcp_server/`.

## Safety and security posture

### Sandbox-mode default

Paper-trading mode as default — `ALPACA_PAPER_TRADE=true` default. Safer posture for LLM-driven trading; production mode is opt-in.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

Version 2.0.1 at time of capture — vendor-authored (Alpaca) gives long-term maintenance signal.
