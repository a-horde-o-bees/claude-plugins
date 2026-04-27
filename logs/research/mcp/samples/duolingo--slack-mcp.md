# Sample

## Identification

### url

https://github.com/duolingo/slack-mcp

### stars

7

### last-commit (date or relative)

5 commits total on master; specific date not displayed in provided content

### license

Apache License 2.0

### default branch

master

### one-line purpose

Read-only Slack MCP server — 5 tools (messages, thread replies, search, users, channels); HTTP-only with per-user OAuth 2.1.

## 1. Language and runtime

### language(s) + version constraints

Python 3.10+

### framework/SDK in use

Anthropic's Claude Agent SDK with Model Context Protocol (MCP)

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

HTTP (via `http://localhost:8001/mcp`)

### how selected (flag, env, separate entry, auto-detect, etc.)

HTTP transport only; listening on port 8001

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

Docker containerization, uv package manager (`uv sync`)

### published package name(s)

Not published to PyPI; source-only distribution

### install commands shown in README

`uv sync` for dependency installation; Docker containerization for production

### pitfalls observed

- Containerization as primary distribution (not Homebrew, npm, Cargo)
- Docker image size optimizations not detailed

## 4. Entry point / launch

### command(s) users/hosts run

`python main.py` launches the server

### wrapper scripts, launchers, stubs

None documented

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Environment variables: `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_MCP_BASE_URI`, `SLACK_EXTERNAL_URL`, `SLACK_MCP_PORT`

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

OAuth 2.1; "when your MCP client first connects. Your client will open a browser window for Slack authorization"

### where credentials come from

Slack OAuth 2.1 flow; credentials managed via `SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET` environment variables

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

Per-request tenant via OAuth 2.1; multi-user support via separate OAuth tokens per user

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Five read-only tools: retrieve channel messages, thread replies, search messages, list users, enumerate channels; advanced search filtering

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Testing framework (pytest) included; no explicit monitoring, logging, or metrics documentation

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

Standard MCP configuration (implied; not explicitly detailed)

### Claude Code

Not documented

### Other

Docker deployment documented for production

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present; this is a standalone server

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest framework configured; test files exist but specific patterns not detailed in provided content

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

Not explicitly documented; testing framework present suggests GitHub Actions or similar

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; uses Python 3.11-slim base; environment variables: `NO_COLOR=1`, `CI=true`, `TERM=dumb`; port 8001 exposed; startup via `uv run python main.py`

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Five documented tools with clear parameters; Dockerfile example for containerized deployment; environment variable configuration

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other — describe what's there

Single-package server; root: `main.py` (entry point), `Dockerfile`, `pyproject.toml`, `uv.lock`, `.gitignore`; structure implies minimal additional files

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Read-only Slack integration (no write capabilities)
- OAuth 2.1 per-user multi-user support
- HTTP transport only (no stdio or SSE)
- Containerization-first deployment (Docker primary)
- Minimal tool set (5 tools) for focused read-only access

## 18. Unanticipated axes observed
- Read-only MCP server pattern (vs. full bidirectional servers)
- Per-user OAuth 2.1 multi-user support in single server instance
- Containerization as primary distribution (not Homebrew, npm, Cargo)

## 19. Python-specific

### SDK / framework variant
- FastMCP 2.x — `fastmcp>=2.13.0` in pyproject.toml
- Import pattern: FastMCP 2.x (inferred)

### Python version floor
- `requires-python = ">=3.10"`
- Dockerfile runs on `python:3.11-slim` base

### Packaging
- build backend: `setuptools.build_meta`
- lock file: `uv.lock` present
- version manager convention: `uv`

### Entry point
- `[project.scripts]`: `slack-mcp = "main:main"` — module `main` (top-level) with `main()` function
- Run in Dockerfile: `uv run python main.py` (not using console script; uses bare `python main.py`)

### Install workflow expected of end users
- Docker primary (`docker run` with env vars); local dev via `uv sync` then `uv run python main.py`
- No PyPI publication observed

### Async and tool signatures
- `pytest>=8.0.0` in test extras; no pytest-asyncio declared — may be sync-style tools
- Source not inspected

### Type / schema strategy
- FastMCP auto-derives

### Testing
- pytest in `test` extra; `uv run pytest` per README
- No pytest config in pyproject.toml

### Dev ergonomics
- ruff in dev extra
- Dockerfile-first workflow; ngrok required for OAuth callback during local dev

### Notable Python-specific choices
- Setuptools backend (minority in the Python sample; hatchling dominant)
- Module entry `main:main` (top-level, no package) — unusual; most servers use a nested package module path
- Docker-only distribution (no PyPI) — inverts the typical Python packaging path; container as the only artifact
- `uv run python main.py` rather than the console script — indicates entry point not the primary run path

## 20. Gaps
- Specific test patterns and coverage not documented
- CI/CD configuration not examined
- Docker image size optimizations not detailed
- Specific Slack API version constraints not mentioned
