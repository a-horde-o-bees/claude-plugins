# Sample

Mirrors of `https://github.com/sooperset/mcp-atlassian`. Atlassian Jira/Confluence MCP server — community-canonical (5,000 stars, MIT, default branch `main`). v0.21.1 released April 10, 2026; 560+ commits, 70 releases. The de facto standard Atlassian MCP server with both Cloud and on-prem (Confluence v6.0+, Jira v8.14+) coverage; carries both `mcp` and `fastmcp` packages simultaneously.

## Server runtime

### Python with both MCP SDK and FastMCP declared

`pyproject.toml` pins `mcp>=1.8.0,<2.0.0` and `fastmcp>=2.13.0,<2.15.0` simultaneously — uses FastMCP 2.x as the runtime surface but also pins the raw `mcp` package, likely a transitional state from a project that predates FastMCP and migrated partially. `requires-python = ">=3.10"`. Python 99.3% of the source. Anthropic Claude Agent SDK conventions referenced.

## Transport

### SSE (Server-Sent Events)

SSE primary; HTTP support also mentioned. Selection mechanism not extracted in detail — likely env-var or subcommand driven given the Python+uvx pattern.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

72 tools spanning Jira (search, issue CRUD, transitions, comments) and Confluence (search, page CRUD, comments). Supports both Cloud and on-prem deployments (Confluence v6.0+, Jira v8.14+). No explicit tool-group selector flag surfaced in this research window.

## Configuration delivery

### Environment variables

Cloud: `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`, `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN`. Server/Data Center: `JIRA_PERSONAL_TOKEN`. Env-var-driven with no documented CLI flag surface.

## Authentication

### Static API key / token via env var

Cloud uses email + API token (`JIRA_API_TOKEN`, `CONFLUENCE_API_TOKEN`). Server/Data Center uses a Personal Access Token via `JIRA_PERSONAL_TOKEN`.

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

OAuth 2.0 supported per docs; flow mechanics for Cloud not fully extracted within budget.

## Multi-tenancy

### Single-user / single-tenant per process

Instance-keyed — one Atlassian site (URL + credentials) per process. No per-request tenant switching observed.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uvx mcp-atlassian` is the canonical install command shown in README. Published as `mcp-atlassian` on PyPI.

### Docker / OCI image

Dockerfile present in repo; container distribution available alongside PyPI.

### PyPI via pip / pipx

`pip` install supported as alternative.

### Source clone with editable install

Install from source supported as a fallback path.

## Entry point and launch

### `uvx <package>`

Host-config snippet: `"command": "uvx"`, `"args": ["mcp-atlassian"]` — clean uvx invocation. `[project.scripts]` declares `mcp-atlassian = "mcp_atlassian:main"`.

### Docker container entrypoint

Containerized launch via Docker as alternative to uvx.

## Build and packaging

### Hatchling + uv (Python)

Build backend: `hatchling.build`. Lock file: present (uv project). Version manager convention: `uv`.

### Pin discipline (Python)

Tight bounded ranges: `mcp>=1.8.0,<2.0.0`, `fastmcp>=2.13.0,<2.15.0`. Both upstream lines bounded against major version drift.

### Python version pinning

`requires-python = ">=3.10"` declared in `pyproject.toml`.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP-based schema auto-derivation likely (FastMCP is the primary runtime surface); raw `mcp` SDK also available for lower-level needs.

### Async model (cross-cutting)

Both `pytest-asyncio` and `pytest-anyio` declared in dev deps — likely a mix of asyncio and anyio async styles in handlers.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

## Test stack

### pytest with async + coverage

`tests/` directory with comprehensive suite. `pytest` + `pytest-cov` + `pytest-asyncio` + `pytest-anyio` in dev. Custom pytest markers separate test scopes by deployment topology: `integration`, `dc_e2e` (Data Center end-to-end), `cloud_e2e` (Cloud end-to-end) — encodes the on-prem/cloud matrix into the test suite rather than only into CI config.

### Linter/formatter test gate

`ruff` + `black` + `mypy` in dev group. Both `ruff` and `black` formatters present.

## CI

### GitHub Actions

GitHub Actions tests workflow present.

## Repository layout

### Single-package src-layout

Single-package Python project with `tests/`, `.devcontainer/`, and docs alongside source.

## Host integration

### Claude Desktop

Documented host.

### Cursor

Documented host.

## Developer ergonomics

### Devcontainer / mise / dev-environment manifests

`.devcontainer/` for dev environment.

### `pre-commit` framework

Pre-commit hooks configured.

## Documentation surface

### `llms.txt` / `llms-full.txt`

`llms.txt` shipped in repo — design-for-AI-consumption documentation pattern.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT licensed.

### Active development

v0.21.1 released April 10, 2026; 560+ commits, 70 releases. 171 open issues + 91 PRs indicates active maintenance with backlog pressure at scale.

### Tagged release with version in changelog

Standard semver tag releases (v0.21.1, etc.).
