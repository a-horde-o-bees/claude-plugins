# Sample

Mirrors of `https://github.com/duolingo/slack-mcp`. Read-only Slack MCP server — five tools (channel messages, thread replies, search, users, channels); HTTP-only transport with per-user OAuth 2.1; containerization-first deployment. 7 stars, Apache-2.0, default branch `master`, 5 commits total on master.

## Server runtime

### Python with FastMCP

Python 3.10+ with Anthropic's Claude Agent SDK paired with MCP. FastMCP 2.x as the MCP runtime — `fastmcp>=2.13.0` declared in pyproject.toml.

## Transport

### Streamable HTTP

HTTP-only; listening on port 8001 via `http://localhost:8001/mcp`.

### Selection mechanism

Implicit single mode — HTTP-only, no stdio or SSE. Forced because OAuth 2.1 is the auth model and stdio cannot complete a browser flow.

## Capability surface

### Tools-only, hand-curated narrow surface

Five read-only tools: retrieve channel messages, thread replies, search messages, list users, enumerate channels. Advanced search filtering. No write capabilities.

## Configuration delivery

### Environment variables

`SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_MCP_BASE_URI`, `SLACK_EXTERNAL_URL`, `SLACK_MCP_PORT`.

## Authentication

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

OAuth 2.1 with browser-redirect flow: "when your MCP client first connects. Your client will open a browser window for Slack authorization." Credentials managed via `SLACK_CLIENT_ID` and `SLACK_CLIENT_SECRET`. Local development requires ngrok to expose the OAuth callback URL.

## Multi-tenancy

### Per-user / per-workspace via OAuth

Per-request tenancy via OAuth 2.1; multi-user support via separate OAuth tokens per user — single server instance serves multiple users.

## Distribution channel

### Docker / OCI image

Docker primary distribution (`docker run` with env vars). Containerization-first pattern; no PyPI publication observed.

### Source clone with editable install

`uv sync` for dependency installation; local dev via `uv sync` then `uv run python main.py`. No PyPI publication observed.

## Entry point and launch

### Bare interpreter + script path

`python main.py` launches the server. Module entry `main:main` (top-level package at repo root, no nested module path).

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `slack-mcp = "main:main"` declared but Dockerfile uses `uv run python main.py` rather than the console script — indicates entry point not the primary run path.

## Build and packaging

### Setuptools (with `setup.py` or `setup.cfg`)

Build backend: `setuptools.build_meta`. Minority choice in the Python sample (hatchling dominant).

### `uv.lock` committed

`uv.lock` present; version manager convention is `uv`.

### Python version pinning

`requires-python = ">=3.10"`. Dockerfile runs on `python:3.11-slim` base.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP auto-derives schemas. `pytest>=8.0.0` in test extras with no pytest-asyncio declared — may be sync-style tools.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present; uses `python:3.11-slim` base; environment variables `NO_COLOR=1`, `CI=true`, `TERM=dumb`; port 8001 exposed; startup via `uv run python main.py`.

## Test stack

### pytest with async + coverage

pytest framework configured (`pytest>=8.0.0` in test extras); `uv run pytest` per README. No pytest config in pyproject.toml. Specific test patterns not detailed.

### Dev extras gating test deps

pytest gated under `test` extra; ruff in dev extra. Keeps the runtime install lean.

## Deployment topology

### Self-hosted HTTP server

Docker deployment documented for production; HTTP-only operating mode.

## Host integration

### Claude Desktop

Standard MCP configuration (implied; not explicitly detailed).

## Repository layout

### Single-package flat layout

Root contains `main.py` (entry point), `Dockerfile`, `pyproject.toml`, `uv.lock`, `.gitignore`. Minimal additional files.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache License 2.0.

### Active development

Master branch active.
