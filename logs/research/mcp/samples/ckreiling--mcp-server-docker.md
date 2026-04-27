# Sample

## Identification

### url

https://github.com/ckreiling/mcp-server-docker

### stars

701

### last-commit

53 total commits on main (specific date not surfaced)

### license

GPL-3.0

### default branch

main

### one-line purpose

Docker Engine MCP server — 28+ tools for containers/images/networks/volumes plus MCP resources for stats/logs and MCP prompts for docker-compose workflows.

## Language and runtime

### language(s) + version constraints

Python; version pinned via `.python-version` file (specific value not surfaced).

### framework/SDK in use

MCP protocol via Python SDK (FastMCP not explicitly surfaced); uses Docker SDK for Python for container operations.

## Transport

### supported transports

stdio.

### how selected

default; no network transport documented.

## Distribution

### every mechanism observed

uvx (uv package manager), Docker container, source clone.

### published package name(s)

mcp-server-docker.

### install commands shown in README

`uvx mcp-server-docker`; Docker image; clone + manual.

## Entry point / launch

### command(s) users/hosts run

`mcp-server-docker` (console script).

### wrapper scripts, launchers, stubs

Dockerfile.

## Configuration surface

### how config reaches the server

environment variables — `DOCKER_HOST` for remote Docker daemons; Claude Desktop JSON config.

## Authentication

### flow

Docker SDK `from_env()` discovery; supports SSH-based auth for remote Docker daemons.

### where credentials come from

local Docker socket or `DOCKER_HOST` env (SSH url supported).

## Multi-tenancy

### tenancy model

single-user per process (one Docker daemon connection).

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

28+ tools (containers, images, networks, volumes); resources for container stats and logs; prompts for natural-language docker-compose workflow.

## Observability

### logging destination + format, metrics, tracing, debug flags

not surfaced in README.

## Host integrations shown in README or repo

### Claude Desktop

JSON `mcpServers` entry (documented as primary integration).

## Claude Code plugin wrapper

### presence and shape

not observed.

## Tests

### presence, framework, location, notable patterns

not mentioned in README.

## CI

### presence, system, triggers, what it runs

GitHub Actions referenced; specifics not surfaced.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Devbox-based dev environment.

## Repo layout

### single-package / monorepo / vendored / other

single package under `src/mcp_server_docker/`.

## Notable structural choices

Exposes MCP prompts for docker-compose workflow (natural-language → multi-step action), which is a capability most cloud/infra servers skip. Remote-daemon access over SSH is a first-class supported path, not just local socket.

## Unanticipated axes observed

Using MCP prompts as orchestration primitives rather than just tools (docker-compose workflow prompt). Devbox for reproducible dev environments (rarer than direnv/asdf).

## Python-specific

### SDK / framework variant

raw MCP Python SDK (FastMCP not explicitly referenced); version pin not surfaced; import pattern not surfaced.

### Python version floor

`requires-python` value: set via `.python-version` file; specific value not surfaced.

### Packaging

build backend: pyproject.toml present; lock file presence not surfaced; version manager convention: Devbox + uv.

### Entry point

console script `mcp-server-docker`; actual console-script name: `mcp-server-docker`; host-config snippet shape: `uvx mcp-server-docker`.

### Install workflow expected of end users

`uvx mcp-server-docker`.

### Async and tool signatures

not surfaced; asyncio/anyio usage not surfaced.

### Type / schema strategy

uses Docker SDK types; specifics not surfaced; auto vs hand-authored not surfaced.

### Testing

not mentioned; fixture style not surfaced.

### Dev ergonomics

Devbox.

### Notable Python-specific choices

GPL-3.0 license is unusual for MCP servers (ecosystem skews MIT/Apache). Advertises prompts as a first-class capability alongside tools.

## Gaps

exact Python version pin, async/sync behavior, test presence, schema strategy, last-commit date could not be determined.
