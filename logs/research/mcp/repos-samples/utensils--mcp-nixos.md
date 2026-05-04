# Sample

Mirrors of `https://github.com/utensils/mcp-nixos`. nixpkgs package-manager MCP server — exposes only 2 tools as a deliberate token-efficiency strategy despite Nix's huge surface. 597 stars, MIT, default branch `main`.

## Server runtime

### Python with FastMCP

Python (74.3%) + TypeScript (22.7%) + Nix (1.3%); Python 3.11+. FastMCP implied by env-var configuration naming `MCP_NIXOS_*` and standard FastMCP options. FastMCP major version not surfaced in pyproject.toml.

## Transport

### stdio

stdio default; `MCP_NIXOS_TRANSPORT` env var defaults select stdio.

### Streamable HTTP

HTTP transport configurable via `MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH` env vars. Stateless mode supported via `MCP_NIXOS_STATELESS_HTTP` for shared deployment behind a load balancer.

### Selection mechanism

Environment variable — `MCP_NIXOS_TRANSPORT=stdio|http`. Container-friendly because env vars are the natural Docker/Kubernetes config surface; companion env vars (`MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP`) configure host/port/path/stateless behavior.

## Capability surface

### Token-economy unified-tool surface

Two primary tools — `nix()` (unified query, ~1,030 tokens of schema) and `nix_versions()` (package version history). Deliberate compression of the tool surface to a small number of broad tools — schema text counts against the host's token budget, so fewer tools means smaller capability advertisement. Contrasts sharply with 50–250-tool servers in the same domain.

## Configuration delivery

### Environment variables

`MCP_NIXOS_TRANSPORT`, `MCP_NIXOS_HOST`, `MCP_NIXOS_PORT`, `MCP_NIXOS_PATH`, `MCP_NIXOS_STATELESS_HTTP` for HTTP transport configuration. Env-var-only configuration surface.

## Authentication

### None / implicit (local-resource gating)

No authentication — relies on public NixOS endpoints. Public unauthenticated upstream.

## Multi-tenancy

### Stateless HTTP for shared deployment

`MCP_NIXOS_STATELESS_HTTP` flag disables per-connection state so the server can sit behind a load balancer with multiple instances handling requests interchangeably. Multi-user-capable since the upstream is public.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uvx mcp-nixos` is the canonical install command. Published to PyPI as `mcp-nixos`.

### PyPI via pip / pipx

`pip install mcp-nixos` for users on plain Python.

### Docker / OCI image

Published at `ghcr.io/utensils/mcp-nixos`. `docker run ghcr.io/utensils/mcp-nixos` documented as one of the launch paths.

### Nix flake (`nix run github:...`)

`nix run github:utensils/mcp-nixos` — Nix-native install via flake reference. Pairs with `nix develop` for contributors.

### Declarative NixOS / Home Manager module via nixpkgs

Server packaged as a first-class nixpkgs entry; users add a config block to their NixOS or Home Manager config. Rare among MCP servers — unique declarative system-config-managed install path.

### Hosted endpoint (no install)

HTTP-remote variant available; users can point at a remote endpoint instead of running locally.

## Entry point and launch

### `uvx <package>`

Host config uses `"command": "uvx"` with `"mcp-nixos"` as the arg. The cleanest stdio launcher for Python servers.

### Docker container entrypoint

`docker run` against the ghcr.io image; container's entrypoint runs the stdio server with env vars pulled in via `-e`.

## Build and packaging

### Hatchling + uv (Python)

`pyproject.toml`-driven Python build. Console script `mcp-nixos` registered.

### Python version pinning

`requires-python = ">=3.11"`.

## Container artifacts

### Published Docker image

Image at `ghcr.io/utensils/mcp-nixos` — pre-built so users skip the local build.

### Nix flake / NixOS module

`flake.nix` for `nix develop` and `nix run` workflows; declarative module exposed via nixpkgs for system-level installation. Doubles as distribution and dev environment.

## Test stack

### pytest with async + coverage

pytest-based test suite. Specific fixture style not surfaced.

## CI

### GitHub Actions

GitHub Actions configured (badge referenced in README).

### CodeRabbit-style PR review bot

CodeRabbit reviews referenced — automated AI-assisted PR review.

## Host integration

### Claude Desktop

JSON `mcpServers` entry with `uvx mcp-nixos` or Docker `command`/`args` shape.

### NixOS / Home Manager module

Declarative config entry available in nixpkgs — install + activation in one place.

## Observability

### None / unspecified

Logging destination not explicitly detailed in surfaced content.

## Repository layout

### Single-package src-layout

Single Python package core with TypeScript sibling (likely docs or companion UI).

## Developer ergonomics

### Linter and type-checker stack

ruff/mypy toolchain wired in.

### Devcontainer / mise / dev-environment manifests

`nix develop` shell — reproducible dev environment more rigorous than virtualenvs.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
