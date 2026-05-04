# Sample

Mirrors of `https://github.com/ckreiling/mcp-server-docker`. Docker Engine MCP server — 28+ tools for containers/images/networks/volumes plus MCP resources for stats/logs and MCP prompts for docker-compose workflows. 701 stars; GPL-3.0; default branch `main`; 53 total commits on main.

## Server runtime

### Python with raw MCP SDK

Python via the raw `mcp` Python SDK (FastMCP not explicitly surfaced). Uses the Docker SDK for Python for container operations. Python version pinned via `.python-version` file (specific value not surfaced). Import pattern not surfaced; async/sync behavior not documented.

## Transport

### stdio

stdio is the default and only documented transport; no network transport documented.

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

28+ tools covering containers, images, networks, and volumes. Resources expose container stats and logs. Prompts cover docker-compose workflow as orchestration primitives — natural-language → multi-step action. Advertises prompts as a first-class capability alongside tools, atypical for cloud/infra servers.

## Configuration delivery

### Environment variables

`DOCKER_HOST` env var for remote Docker daemons (SSH URL form supported).

### Host-side JSON config snippet

Claude Desktop JSON `mcpServers` entry documented as the primary integration shape.

## Authentication

### None / implicit (local-resource gating)

No MCP-layer auth. Docker SDK `from_env()` discovery uses ambient Docker credentials; trust derives from local socket access or `DOCKER_HOST` env (SSH URL supported as a first-class remote-daemon path, not just local socket).

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per process; one Docker daemon connection. The process boundary equals the trust boundary; switching identities means relaunching with different `DOCKER_HOST` config.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uvx mcp-server-docker` is the documented one-liner. PyPI package name: `mcp-server-docker`.

### Docker / OCI image

Docker container available; Dockerfile in repo.

### Source clone with editable install

Clone + manual install supported.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `mcp-server-docker`; `[project.scripts]` declared in `pyproject.toml`.

### `uvx <package>`

Host-config snippet shape: `uvx mcp-server-docker`.

### Docker container entrypoint

Dockerfile present; container invocation as alternative launch.

## Build and packaging

### Hatchling + uv (Python)

`pyproject.toml` present (build backend not surfaced explicitly); version manager convention is Devbox + uv.

### Python version pinning

`.python-version` file used (pyenv-style); specific value not surfaced.

## Schema and types

### Hand-authored tool schemas

Uses Docker SDK types; raw MCP SDK requires hand-authored schemas (FastMCP auto-derivation not in play). Specifics not surfaced.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present (single-stage, build-from-source pattern).

## Repository layout

### Single-package src-layout

Single package under `src/mcp_server_docker/`.

## Host integration

### Claude Desktop

JSON `mcpServers` entry documented as primary integration.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not present.

## Developer ergonomics

### Devcontainer / mise / dev-environment manifests

Devbox-based dev environment for reproducibility (rarer than direnv/asdf in this corpus).

## CI

### GitHub Actions

GitHub Actions referenced; specifics not surfaced.

## Release and lifecycle

### Active development

53 total commits on main; ongoing project. Last-commit date not surfaced.

### License — Copyleft (GPL-3.0)

GPL-3.0 — strong copyleft. Derivative works carry the same license; commercial use is permitted but obligations attach to redistribution. Unusual for this corpus, which skews MIT/Apache.
