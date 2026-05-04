# Sample

Mirrors of `https://github.com/openags/paper-search-mcp`. Academic paper search MCP server — arXiv/PubMed/etc. search and download across 20+ academic providers; ships Claude Code skills in-tree alongside the MCP server. ~1,200 stars, MIT, default branch `main`, active development (37+ commits).

## Server runtime

### Python with both MCP SDK and FastMCP declared

Both `mcp[cli]>=1.6.0` and `fastmcp` declared — dual imports. FastMCP used for server surface; `mcp[cli]` kept for dev/inspector tooling. `requires-python >= 3.10` (supports 3.10–3.13). `httpx` async I/O.

## Transport

### stdio

stdio is the default transport for Claude Desktop integration.

### Selection mechanism

stdio default; no explicit transport selection mechanism surfaced in README.

## Capability surface

### Aggregator-tool catalog (many upstreams, normalized tool surface)

Unified `search_papers` and `download_with_fallback` tools dispatch across 20+ academic sources, plus platform-specific search/download/read tools per source — arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, Semantic Scholar, Crossref, OpenAlex, PMC, CORE, Europe PMC, dblp, OpenAIRE, CiteSeerX, DOAJ, BASE, Zenodo, HAL, SSRN, Unpaywall, optional Sci-Hub.

## Configuration delivery

### Environment variables

Provider API keys follow the `PAPER_SEARCH_MCP_*` prefix convention — `PAPER_SEARCH_MCP_UNPAYWALL_EMAIL`, `_CORE_API_KEY`, `_SEMANTIC_SCHOLAR_API_KEY`, `_ZENODO_ACCESS_TOKEN`, `_GOOGLE_SCHOLAR_PROXY_URL`, `_IEEE_API_KEY`, `_ACM_API_KEY`.

### Dotenv file

`.env` file supported for local dev; `.env.example` ships in repo.

### Host-side JSON config snippet

Claude Desktop JSON `env` block injects per-provider keys into the launched server.

## Authentication

### Per-source independent API keys with graceful degradation

Per-provider API keys for each upstream source; some required (Unpaywall email), others optional. Server falls back per provider. Provider-side key surface includes free-and-paid mixes (Crossref free, IEEE/ACM paid) — keys are independent per upstream.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user; per-provider credentials applied globally.

## Distribution channel

### PyPI via pip / pipx

`pip install paper-search-mcp` — package name `paper-search-mcp` on PyPI.

### PyPI via uvx (zero-install runner)

`uv tool install paper-search-mcp` and `uvx paper-search-mcp` — uvx is a recommended one-liner.

### Smithery registry

Registered install target via `npx -y @smithery/cli install @openags/paper-search-mcp --client claude`.

### Docker / OCI image

`docker build -t paper-search-mcp .` — Dockerfile present in repo.

### Source clone with editable install

Source clone + venv supported as a fallback install path.

### Multi-channel publication

Five distinct distribution channels — PyPI, uvx, Smithery, Docker, source clone — covering the major install surfaces simultaneously.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Two `[project.scripts]` entries — `paper-search-mcp` → `paper_search_mcp.server:main`; `paper-search` → `paper_search_mcp.cli:main`. Server and CLI share a core library.

### `uvx <package>`

`uvx paper-search-mcp` — primary host-config snippet shape.

## Build and packaging

### Hatchling + uv (Python)

Build backend hatchling; uv as version-manager convention.

### `uv.lock` committed

`uv.lock` implied; not explicitly confirmed.

### Optional-dependency fan-out

`httpx[socks]` for SOCKS-proxy support; `pypdf` + `lxml` + `beautifulsoup4` in core deps for in-process PDF/HTML/XML handling.

### Pin discipline (Python)

`mcp[cli]>=1.6.0` pinned; `fastmcp` no version specified — loose pin signals follow-latest posture, with fragility risk.

## Schema and types

### Pydantic v2 models

Pydantic via FastMCP / MCP SDK — schemas auto-derived from type hints.

### Async model (cross-cutting)

Async (`httpx` + `asyncio` mentioned); FastMCP-standard async tool signatures.

### FastMCP auto-derivation from type hints

FastMCP auto-derives schemas from Python type hints.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root; `.env.example` for container env injection.

## Test stack

### pytest with async + coverage

pytest (inferred) under `tests/`; end-to-end regression tests mentioned.

### End-to-end protocol-conformance harness

End-to-end regression tests mentioned for the unified tool surface across providers.

## CI

### GitHub Actions

GitHub Actions workflows in `.github/workflows/`.

## Host integration

### Claude Desktop

JSON snippet (standard `command/args/env`).

### Claude Code

Dedicated skill files under `claude-code/` directory.

### Smithery / Glama discovery

Smithery is a registered install target.

## Repository layout

### Single-package plus sibling host integrations

Single-package (`paper_search_mcp/`) plus `claude-code/` skill sibling, `tests/`, and `docs/` — Claude Code skills co-located with the server in the repo.

## Developer ergonomics

### Inspector/debug tooling references

`mcp[cli]` dev inspector available for the server.

## Documentation surface

### README as the canonical surface

README is the canonical install/setup surface.

## Claude Code plugin / skill wrapper

### `claude-code/` directory with skill files

`claude-code/` directory contains Claude Code skill files — explicit skill-layer integration shipped in-tree alongside the MCP server (rather than just host-config JSON). First-class plugin wrapper co-located with server.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

37+ commits; active development.
