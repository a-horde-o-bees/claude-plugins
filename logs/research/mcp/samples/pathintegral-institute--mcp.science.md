# Sample

## Identification

### url

https://github.com/pathintegral-institute/mcp.science

### stars

128

### last-commit

July 1, 2025 (v0.2.0 release); as of April 2026, may be older than indicated.

### license

MIT

### default branch

main

### one-line purpose

Scientific-computing MCP monorepo — single PyPI package dispatches to multiple servers via `uvx mcp-science <server>`; Hatch `force-include` embeds nested server dirs.

## Language and runtime

### language(s) + version constraints

Python (version not specified in provided content).

### framework/SDK in use

Anthropic's Model Context Protocol (MCP) specification.

## Transport

### supported transports

Stdio-based communication as primary transport mechanism for MCP interactions.

### how selected

Standardized MCP stdio transport; selected at server invocation via `uvx`.

## Distribution

### every mechanism observed

PyPI via `mcp-science` namespace, uv package manager, source build.

### published package name(s)

`mcp-science` (PyPI package namespace).

### install commands shown in README

`uvx mcp-science <server-name>` (recommended); source installation also available.

### pitfalls observed

PyPI package namespace (`mcp-science`) allows separate versioning per server. `uvx` dependency handling avoids manual Python environment setup.

## Entry point / launch

### command(s) users/hosts run

`uvx mcp-science <server-name>` (e.g., `uvx mcp-science web-fetch`, `uvx mcp-science python-code`, etc.).

### wrapper scripts, launchers, stubs

None required; `uvx` tool handles automatic installation and execution.

## Configuration surface

### how config reaches the server

Client application JSON files (e.g., Claude Desktop `claude_desktop_config.json`); server-specific API keys required for certain integrations (Materials Project, TXYZ Search) configured within individual server configurations; optional MCPM (Model Context Protocol Manager) for automated server wiring.

## Authentication

### flow

Server-specific API keys for specialized integrations; no centralized authentication mechanism.

### where credentials come from

Environment variables or configuration files (server-specific).

## Multi-tenancy

### tenancy model

Not applicable; monorepo collection of independent servers; each server is single-user.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Specialized functions per server: web content retrieval, academic searches, code execution (Python, SSH), scientific computation (DFT via GPAW), database operations (TinyDB), Jupyter kernel interaction, Wolfram Language evaluation.

## Observability

### logging destination + format, metrics, tracing, debug flags

No explicit observability features documented.

## Host integrations shown in README or repo

### Claude Desktop

Yes; configuration shown in README with JSON snippet: `"mcpServers": { "web-fetch": { "command": "uvx", "args": ["mcp-science", "web-fetch"] } }`.

### Claude Code

Not explicitly documented.

### Other

MCPM (Model Context Protocol Manager) mentioned for automated client integration.

## Claude Code plugin wrapper

### presence and shape

Not present; collection of independent PyPI servers.

## Tests

### presence, framework, location, notable patterns

Not documented in provided content.

## CI

### presence, system, triggers, what it runs

Not documented in provided content; typical Python project structure implies testing infrastructure.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not mentioned; not required for PyPI distribution.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop JSON configuration example provided; uvx automatic installation and execution handles DevEx; each server has dedicated README.

## Repo layout

### single-package / monorepo / vendored / other

Monorepo organization; `/servers/` subdirectories containing individual server implementations, each with: dedicated README, `pyproject.toml`, source code; root: documentation (`README.md`, `CITATION.cff`), configuration (`pyproject.toml`, `uv.lock`), assets (`assets/`), web (`index.html`, `CNAME` for GitHub Pages).

## Notable structural choices

Monorepo structure enables centralized governance with independent per-server deployments. PyPI package namespace (`mcp-science`) allows separate versioning per server. `uvx` dependency handling avoids manual Python environment setup. Scientific focus (materials, DFT, Jupyter, Wolfram) targets academic/research community. GitHub Pages site at mcp.science for discoverability.

## Unanticipated axes observed

Monorepo of thematically-linked servers (scientific focus) vs. single-server repos. Citation metadata (`CITATION.cff`) suggests academic publication focus. Integration with scientific tools (GPAW, Wolfram Language, Jupyter) uncommon in MCP ecosystem. Multi-language support within monorepo (Python primary, but Wolfram Language backend).

## Python-specific

### SDK / framework variant

Top-level `pyproject.toml` lists only `click>=8.2.1` — no `mcp` or `fastmcp` at root. Root `mcp-science` CLI is a dispatcher; individual servers in `servers/*/` each have their own `pyproject.toml` with per-server SDK choice (not individually inspected here). Import pattern varies per sub-server.

### Python version floor

Root: `requires-python = ">=3.10"`. Per-server floors not individually inspected.

### Packaging

Build backend: `hatchling.build`. Lock file: `uv.lock` present (root). Version manager convention: `uv`. Monorepo structure: root package force-includes `mcp_science/servers` directory (non-standard Hatch configuration).

### Entry point

`[project.scripts]`: `mcp-science = "mcp_science:main"` — the dispatcher. README host-config snippet: `"command": "uvx"`, `"args": ["mcp-science", "web-fetch"]` — dispatcher name + subcommand selects server.

### Install workflow expected of end users

`uvx mcp-science <server-name>` (primary). `uv` install via `curl -sSf https://astral.sh/uv/install.sh | bash`. Optional MCPM tool for convenience.

### Async and tool signatures

Not inspected; per-server.

### Type / schema strategy

Per-server.

### Testing

Not documented at root.

### Dev ergonomics

GitHub Pages site at mcp.science for discovery. `CITATION.cff` — academic publication metadata.

### Notable Python-specific choices

Dispatcher-style monorepo where a single PyPI package (`mcp-science`) routes to multiple servers via CLI subcommand — unique in the sample. Other monorepos (awslabs, mcp.science) ship one PyPI package per server; this one ships one package and dispatches internally. Hatch `force-include` directive pulls `mcp_science/servers` into the wheel — custom monorepo build shape rather than workspace-based approach.

## Gaps

Test framework and patterns not examined. CI/CD configuration not detailed. Individual server dependencies and compatibility not enumerated. Last release (v0.2.0) from July 2025; repo may be dormant or slowly maintained.
