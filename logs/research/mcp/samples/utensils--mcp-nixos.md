# Sample

## Identification
- url: https://github.com/utensils/mcp-nixos
- stars: 597
- last-commit (date or relative): April 3, 2026 (v2.3.1 release)
- license: MIT
- default branch: main
- one-line purpose: nixpkgs package-manager MCP server — exposes only 2 tools as a deliberate token-efficiency strategy despite Nix's huge surface.

## 1. Language and runtime
- language(s) + version constraints: Python 74.3%, TypeScript 22.7%, Nix 1.3%; Python 3.11+
- framework/SDK in use: FastMCP (implied by env-var configuration naming `MCP_NIXOS_*` and standard FastMCP options)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default), HTTP, Docker-wrapped
- how selected: environment variables — `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP`
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: uvx, Nix (`nix run github:utensils/mcp-nixos`), Docker (ghcr.io), pip, HTTP remote, declarative NixOS/Home Manager via nixpkgs
- published package name(s): mcp-nixos (PyPI); `ghcr.io/utensils/mcp-nixos`
- install commands shown in README: `uvx mcp-nixos`; `nix run github:utensils/mcp-nixos`; `docker run ghcr.io/utensils/mcp-nixos`; `pip install mcp-nixos`
- pitfalls observed:
  - declarative install path via nixpkgs is rare for MCP servers

## 4. Entry point / launch
- command(s) users/hosts run: `uvx mcp-nixos`, `nix run ...`, or Docker
- wrapper scripts, launchers, stubs: Nix flake (available via `nix develop`); `nix run` via github: URL
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables for HTTP transport — `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: no explicit authentication; relies on public NixOS endpoints
- where credentials come from: N/A
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: stateless HTTP option supports shared deployment (stateless → multi-user capable)
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: two primary tools — `nix()` (unified query, ~1,030 tokens) and `nix_versions()` (package version history)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not explicitly detailed
- pitfalls observed:
  - what couldn't be determined: FastMCP major version pin, async behavior, Python entry-point path in pyproject, logging destination

## 10. Host integrations shown in README or repo
For each host: form + location
- Claude Desktop and other MCP clients: JSON `mcpServers` entry (via uvx or Docker)
- NixOS/Home Manager: declarative config entry available in nixpkgs
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not observed

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: pytest-based
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions (badge referenced); CodeRabbit reviews
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Docker image on ghcr.io; Nix flake for nix-native install; declarative NixOS/Home Manager module
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `nix develop` shell; ruff/mypy toolchain
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single package with Python core + TypeScript (likely docs or companion UI)
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- intentionally collapses the tool surface to two tools: a single unified `nix()` query (~1,030 tokens) and a `nix_versions()` helper — contrasts sharply with 50–250-tool servers in the same domain
- supports stateless HTTP mode for shared/multi-user deployments
- declarative install path via nixpkgs is rare for MCP servers

## 18. Unanticipated axes observed
- decision dimensions this repo reveals:
    - deliberate token-efficiency focus on the MCP tool surface (few, broad tools vs many narrow ones)
    - stateless-HTTP transport flag separates cacheable deployments from stateful ones
    - declarative-config distribution (nixpkgs) as a first-class install channel

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / custom: FastMCP (major version not surfaced)
- version pin from pyproject.toml: not surfaced
- import pattern observed: not surfaced

### Python version floor
- `requires-python` value: 3.11+

### Packaging
- build backend: pyproject.toml
- lock file present: not surfaced
- version manager convention: uv + nix

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: console script `mcp-nixos`
- actual console-script name(s): `mcp-nixos`
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path): `uvx mcp-nixos`

### Install workflow expected of end users
- install form + one-liner from README: `uvx mcp-nixos`

### Async and tool signatures
- sync `def` or `async def`: not surfaced
- asyncio/anyio usage: not surfaced

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: mypy-checked; specifics not surfaced
- schema auto-derived vs hand-authored: FastMCP default (auto-derived)

### Testing
- pytest / pytest-asyncio / unittest / none: pytest
- fixture style: not surfaced

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: `nix develop` reproducible shell

### Notable Python-specific choices
- open bullets:
    - two-tool API as a token-efficiency strategy
    - `nix develop` shell for dev environment is more reproducible than virtualenvs
    - declarative install via nixpkgs is unique among MCP servers

## 20. Gaps
- what couldn't be determined: FastMCP major version pin, async behavior, Python entry-point path in pyproject, logging destination
