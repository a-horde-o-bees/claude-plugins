# Sample

Mirrors of `https://github.com/voska/hass-mcp`. Home Assistant MCP server — Docker-first distribution; long-lived access token auth; aggressive Python 3.13 floor on a 287-star production server. MIT, default branch `master`, v0.1.1 (August 5, 2025).

## Server runtime

### Python with raw MCP SDK

Python 99.6%; `requires-python = ">=3.13"`. `mcp[cli]>=1.4.1` declared in pyproject.toml — older pin than awslabs sub-servers. Two-dep server (`mcp[cli]` + `httpx`) — REST client over Home Assistant's REST API, minimal abstraction. Likely async given httpx + MCP SDK. Pydantic arrives via `mcp[cli]` extra. Bare `app` module name (rather than conventional `hass_mcp`) — unusual naming suggesting template-derived structure.

## Transport

### stdio

stdio default; wrapped in Docker or uvx invocation.

### Selection mechanism

Implicit single mode — stdio only.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Tools for controlling Home Assistant entities, querying states, executing services, managing automations. Parent project (`homeassistant-ai/ha-mcp`) advertises 80+ tools; this variant is more focused — exact count not surfaced.

## Configuration delivery

### Environment variables

`HA_URL` and `HA_TOKEN` env vars supply the Home Assistant endpoint and credential.

### Host-side JSON config snippet

Claude Desktop JSON snippet shown with Docker `command`/`args`; `HA_URL` + `HA_TOKEN` env block.

## Authentication

### Static API key / token via env var

Home Assistant long-lived access token, supplied via `HA_TOKEN` env var injected into the container or uvx process.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per Home Assistant instance — one credential, one HA endpoint, one process.

## Distribution channel

### Docker / OCI image

Docker as the *primary* distribution channel — README leads with `docker pull voska/hass-mcp:latest`. Docker Hub at `voska/hass-mcp:latest`. Many Home Assistant users run HA in Docker already; bundling the MCP server in the same paradigm matches operator mental models.

### PyPI via uvx (zero-install runner)

`uvx hass-mcp` as secondary install path; published as `hass-mcp` on PyPI.

## Entry point and launch

### Docker container entrypoint

`docker run -i --rm -e HA_URL -e HA_TOKEN voska/hass-mcp` — the primary documented launch shape. The container's entrypoint runs the stdio server with env vars pulled in.

### Console script via `[project.scripts]` / npm bin

`hass-mcp` console script registered — wires to `app.run:main` (module is just `app`, not `hass_mcp`).

### `uvx <package>`

`uvx hass-mcp` as alternative to Docker.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. Version manager convention: `uv` / `uvx`. `.python-version` file referenced.

### Python version pinning

`requires-python = ">=3.13"` — aggressive version requirement; most Python MCP servers target 3.10+. Uncommon floor for a production-popular (287 stars) server.

## Schema and types

### Pydantic v2 models

Pydantic arrives via the `mcp[cli]` extra.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present; produces the runtime image used in production.

### Published Docker image

Official image `voska/hass-mcp:latest` on Docker Hub.

## Test stack

### pytest with async + coverage

pytest mentioned in README. Specifics not surfaced.

## CI

### GitHub Actions

GitHub Actions workflow directory present; details not extracted.

## Host integration

### Claude Desktop

JSON snippet shown with Docker `command`/`args` shape; `HA_URL` + `HA_TOKEN` env block.

## Observability

### None / unspecified

Logging destination/format not surfaced in extracted content.

## Repository layout

### Single-package src-layout

Single-package layout — `app/` module rather than conventional `hass_mcp/`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT (per README badges; pyproject.toml did not declare).

### Tagged release with version in changelog

v0.1.1 (August 5, 2025).
