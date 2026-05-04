# Sample

Mirrors of `https://github.com/pathintegral-institute/mcp.science`. Scientific-computing MCP monorepo — single PyPI package dispatches to multiple servers via `uvx mcp-science <server>`; Hatch `force-include` embeds nested server dirs. 128 stars, MIT, default branch `main`, last commit July 1, 2025 (v0.2.0); may be older than indicated as of April 2026.

## Server runtime

### Python with hand-rolled MCP

Top-level `pyproject.toml` lists only `click>=8.2.1` — no `mcp` or `fastmcp` at root. Root `mcp-science` CLI is a dispatcher; individual servers in `servers/*/` each have their own `pyproject.toml` with per-server SDK choice (varies per sub-server). Anthropic's Model Context Protocol specification referenced.

## Transport

### stdio

Stdio-based communication as primary transport mechanism for MCP interactions.

### Selection mechanism

Standardized MCP stdio transport selected at server invocation via `uvx`.

## Capability surface

### Domain-bundled tool set

Specialized functions per server — web content retrieval, academic searches, code execution (Python, SSH), scientific computation (DFT via GPAW), database operations (TinyDB), Jupyter kernel interaction, Wolfram Language evaluation.

## Configuration delivery

### Host-side JSON config snippet

Client application JSON files (e.g., Claude Desktop `claude_desktop_config.json`); host-config snippet `"command": "uvx"`, `"args": ["mcp-science", "web-fetch"]`.

### Environment variables

Server-specific API keys for specialized integrations (Materials Project, TXYZ Search) configured via env vars within individual server configurations.

## Authentication

### Per-tool varied (monorepo)

Authentication varies per sub-server — no centralized auth mechanism. Server-specific API keys for specialized integrations; some sub-servers need keys, others none.

## Multi-tenancy

### N/A (library, not a runtime)

Monorepo collection of independent servers; each sub-server is single-user. No shared runtime to multiplex tenants across.

## Distribution channel

### PyPI via uvx (zero-install runner)

PyPI package `mcp-science`; canonical install is `uvx mcp-science <server-name>`. PyPI namespace allows separate versioning per server.

### Source clone with editable install

Source build also available as a fallback install path.

## Entry point and launch

### CLI dispatcher subcommand

`uvx mcp-science <server-name>` — dispatcher name + subcommand selects the actual server (e.g., `uvx mcp-science web-fetch`, `uvx mcp-science python-code`). The `mcp-science` console script is a CLI dispatcher to the embedded sub-servers.

### `uvx <package>`

`uvx` handles automatic install and execution.

## Build and packaging

### Hatchling + uv (Python)

Build backend `hatchling.build`; `uv` is the version-manager convention.

### `uv.lock` committed

`uv.lock` present at root.

### Hatch force-include for monorepo wheel

Root package force-includes `mcp_science/servers` directory — non-standard Hatch configuration that pulls nested server directories into the wheel rather than relying on a workspace-based build.

### Python version pinning

Root `requires-python = ">=3.10"`; per-server floors not individually inspected.

## Container artifacts

### No container artifacts

Not mentioned; not required for PyPI distribution.

## Repository layout

### Monorepo with per-server subdirectories and one PyPI package

Monorepo where a single PyPI package (`mcp-science`) routes to multiple servers via CLI subcommand. Root: documentation (`README.md`, `CITATION.cff`), configuration (`pyproject.toml`, `uv.lock`), assets (`assets/`), web (`index.html`, `CNAME` for GitHub Pages). Per-server subdirectories under `/servers/` each contain dedicated README, `pyproject.toml`, source code.

## Host integration

### Claude Desktop

JSON snippet shown in README — `"mcpServers": { "web-fetch": { "command": "uvx", "args": ["mcp-science", "web-fetch"] } }`.

### Aggregator/installer registry

MCPM (Model Context Protocol Manager) mentioned for automated client integration.

## Documentation surface

### Per-subserver README in monorepo

Each sub-server has its own dedicated README.

### CITATION.cff

`CITATION.cff` ships at root — academic publication metadata, signaling research/citation focus.

### GitHub Pages / hosted docs site

GitHub Pages site at `mcp.science` for discoverability.

### README as the canonical surface

Top-level README at repo root.

## Developer ergonomics

### Sample MCP client configs in repo

Claude Desktop JSON configuration example provided for the dispatcher pattern.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not present; collection of independent PyPI servers.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Tagged release with version in changelog

v0.2.0 released July 1, 2025.
