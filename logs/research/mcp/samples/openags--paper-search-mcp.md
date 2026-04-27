# Sample

## Identification

### url

https://github.com/openags/paper-search-mcp

### stars

~1,200

### last-commit

active (37+ commits)

### license

MIT

### default branch

main

### one-line purpose

Academic paper search MCP server — arXiv/PubMed search + Claude Code skills in-tree; dual FastMCP + `mcp[cli]` dependency.

## 1. Language and runtime

### language(s) + version constraints

Python, `requires-python >= 3.10` (supports 3.10–3.13).

### framework/SDK in use

Both `mcp[cli]>=1.6.0` and `fastmcp` declared — dual imports suggested; FastMCP used for server, MCP CLI kept for tooling.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (default for Claude Desktop); HTTP indirectly via academic APIs the server consumes.

### how selected

stdio default; explicit transport selection not surfaced in README.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (`pip install paper-search-mcp`), uv tool install, uvx, Smithery CLI, Docker, source clone.

### published package name(s)

`paper-search-mcp`

### install commands shown in README

`pip install paper-search-mcp`, `uv tool install paper-search-mcp`, `npx -y @smithery/cli install @openags/paper-search-mcp --client claude`, `docker build -t paper-search-mcp .`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`paper-search-mcp` (server console script) or `paper-search` (CLI).

### wrapper scripts, launchers, stubs

Smithery wrapper published.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

`.env` file, environment variables, and Claude Desktop JSON `env` block. Provider API keys follow `PAPER_SEARCH_MCP_*` prefix pattern.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Per-provider API keys, one email (Unpaywall).

### where credentials come from

env vars — `PAPER_SEARCH_MCP_UNPAYWALL_EMAIL` (required for Unpaywall), `_CORE_API_KEY`, `_SEMANTIC_SCHOLAR_API_KEY`, `_ZENODO_ACCESS_TOKEN`, `_GOOGLE_SCHOLAR_PROXY_URL`, `_IEEE_API_KEY`, `_ACM_API_KEY`.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

Single-user; per-provider credentials applied globally.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools — unified `search_papers`, `download_with_fallback`, plus platform-specific search/download/read across 20+ academic sources (arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, Semantic Scholar, Crossref, OpenAlex, PMC, CORE, Europe PMC, dblp, OpenAIRE, CiteSeerX, DOAJ, BASE, Zenodo, HAL, SSRN, Unpaywall, optional Sci-Hub).

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Standard logging; end-to-end regression testing mentioned but no metrics/tracing surfaced.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON snippet (standard `command/args/env`).

### Claude Code

Dedicated skill files under `claude-code/` directory.

### Smithery

Registered install target.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

`claude-code/` directory contains Claude Code skill files — explicit skill-layer integration rather than just host-config JSON.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

`tests/` directory; end-to-end regression tests mentioned.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions workflows in `.github/workflows/`.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; `.env.example` for container env injection.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`.env.example`, Claude Desktop JSON, Smithery config.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single-package (`paper_search_mcp/`) + `claude-code/` skill sibling + `tests/` + `docs/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Dual FastMCP + MCP[cli] declaration — likely using FastMCP for the server surface and `mcp[cli]` for dev/inspector tooling. Two console scripts (`paper-search-mcp` as server, `paper-search` as standalone CLI) — server and CLI share a core library. Distinct `claude-code/` directory ships Claude Code skills alongside the MCP server — unusual first-class plugin wrapper co-located with server.

## 18. Unanticipated axes observed

Shipping Claude Code skills in-tree with a generic MCP server. 20+ backend providers multiplex through a common tool surface with uniform env-var prefix convention. Dual runtime (MCP server for agents, CLI for humans) from same codebase.

## 19. Python-specific

### SDK / framework variant

FastMCP (version not pinned) + `mcp[cli]>=1.6.0`. Version pin from `pyproject.toml` — `mcp[cli]>=1.6.0`; `fastmcp` no version specified. Import pattern observed — `fastmcp` top-level plus `mcp.server` CLI utilities.

### Python version floor

`requires-python` value — `>=3.10`.

### Packaging

Build backend — hatchling. Lock file present — `uv.lock` implied; not explicitly confirmed. Version manager convention — uv.

### Entry point

Two `[project.scripts]` entries — `paper-search-mcp` → `paper_search_mcp.server:main`; `paper-search` → `paper_search_mcp.cli:main`. Host-config snippet shape — `uvx paper-search-mcp`, `uv tool install`, `pip`, Docker.

### Install workflow expected of end users

First-class support for all mainstream paths — pip, pipx, uv tool install, uvx, source clone + venv, Docker. One-liner the README recommends — `uv tool install paper-search-mcp` or `pip install paper-search-mcp`.

### Async and tool signatures

Async (httpx + asyncio mentioned); FastMCP-standard.

### Type / schema strategy

Pydantic via FastMCP / MCP SDK. Schema auto-derived.

### Testing

pytest (inferred); end-to-end regression tests mentioned.

### Dev ergonomics

`.env.example` + `mcp[cli]` dev inspector.

### Notable Python-specific choices

`httpx[socks]` for SOCKS-proxy support — reflects real-world scraping/proxy needs for Google Scholar. `pypdf` + `lxml` + `beautifulsoup4` in core deps — paper ingestion does PDF parse and HTML/XML handling in-process rather than deferring to external services. Loose `fastmcp` pin (no version) — likely follows latest; potential fragility.

## 20. Gaps

Exact `fastmcp` version pin (if any) not surfaced. `uv.lock` presence not explicitly confirmed. Content of `claude-code/` skills not inspected.
