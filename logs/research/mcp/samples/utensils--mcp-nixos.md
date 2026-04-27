# Sample

## Identification

### url

https://github.com/utensils/mcp-nixos

### stars

597

### last-commit

April 3, 2026 (v2.3.1 release)

### license

MIT

### default branch

main

### one-line purpose

nixpkgs package-manager MCP server — exposes only 2 tools as a deliberate token-efficiency strategy despite Nix's huge surface.

## Language and runtime

### language(s) + version constraints

Python 74.3%, TypeScript 22.7%, Nix 1.3%; Python 3.11+.

### framework/SDK in use

FastMCP (implied by env-var configuration naming `MCP_NIXOS_*` and standard FastMCP options).

## Transport

### supported transports

stdio (default), HTTP, Docker-wrapped.

### how selected

environment variables — `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP`.

## Distribution

### every mechanism observed

uvx, Nix (`nix run github:utensils/mcp-nixos`), Docker (ghcr.io), pip, HTTP remote, declarative NixOS/Home Manager via nixpkgs.

### published package name(s)

mcp-nixos (PyPI); `ghcr.io/utensils/mcp-nixos`.

### install commands shown in README

`uvx mcp-nixos`; `nix run github:utensils/mcp-nixos`; `docker run ghcr.io/utensils/mcp-nixos`; `pip install mcp-nixos`.

### pitfalls observed

declarative install path via nixpkgs is rare for MCP servers.

## Entry point / launch

### command(s) users/hosts run

`uvx mcp-nixos`, `nix run ...`, or Docker.

### wrapper scripts, launchers, stubs

Nix flake (available via `nix develop`); `nix run` via github: URL.

## Configuration surface

### how config reaches the server

environment variables for HTTP transport — `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP`.

## Authentication

### flow

no explicit authentication; relies on public NixOS endpoints.

### where credentials come from

N/A.

## Multi-tenancy

### tenancy model

stateless HTTP option supports shared deployment (stateless → multi-user capable).

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

two primary tools — `nix()` (unified query, ~1,030 tokens) and `nix_versions()` (package version history).

## Observability

### logging destination + format, metrics, tracing, debug flags

not explicitly detailed

## Host integrations shown in README or repo

### Claude Desktop

JSON `mcpServers` entry (via uvx or Docker).

### NixOS/Home Manager

declarative config entry available in nixpkgs.

## Claude Code plugin wrapper

### presence and shape

not observed

## Tests

### presence, framework, location, notable patterns

pytest-based.

## CI

### presence, system, triggers, what it runs

GitHub Actions (badge referenced); CodeRabbit reviews.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Docker image on ghcr.io; Nix flake for nix-native install; declarative NixOS/Home Manager module.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`nix develop` shell; ruff/mypy toolchain.

## Repo layout

### single-package / monorepo / vendored / other

single package with Python core + TypeScript (likely docs or companion UI).

## Notable structural choices

intentionally collapses the tool surface to two tools: a single unified `nix()` query (~1,030 tokens) and a `nix_versions()` helper — contrasts sharply with 50–250-tool servers in the same domain.

supports stateless HTTP mode for shared/multi-user deployments.

declarative install path via nixpkgs is rare for MCP servers.

## Unanticipated axes observed

deliberate token-efficiency focus on the MCP tool surface (few, broad tools vs many narrow ones).

stateless-HTTP transport flag separates cacheable deployments from stateful ones.

declarative-config distribution (nixpkgs) as a first-class install channel.

## Python-specific

### SDK / framework variant

FastMCP (major version not surfaced). Version pin from pyproject.toml not surfaced. Import pattern not surfaced.

### Python version floor

`requires-python` value: 3.11+.

### Packaging

build backend: pyproject.toml. Lock file: not surfaced. Version manager convention: uv + nix.

### Entry point

console script `mcp-nixos`. Host-config snippet shape: `uvx mcp-nixos`.

### Install workflow expected of end users

`uvx mcp-nixos`.

### Async and tool signatures

not surfaced; asyncio/anyio usage not surfaced.

### Type / schema strategy

mypy-checked; specifics not surfaced. Schema auto-derived via FastMCP default.

### Testing

pytest. Fixture style not surfaced.

### Dev ergonomics

`nix develop` reproducible shell.

### Notable Python-specific choices

two-tool API as a token-efficiency strategy. `nix develop` shell for dev environment is more reproducible than virtualenvs. Declarative install via nixpkgs is unique among MCP servers.

## Gaps

what couldn't be determined: FastMCP major version pin, async behavior, Python entry-point path in pyproject, logging destination.
