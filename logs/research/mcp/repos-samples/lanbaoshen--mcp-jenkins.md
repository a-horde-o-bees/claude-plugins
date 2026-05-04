# Sample

Mirrors of `https://github.com/lanbaoshen/mcp-jenkins`. Jenkins CI MCP server — exposes 24 Jenkins job/build/queue/node tools, supports per-request HTTP-header credentials enabling multi-tenant HTTP mode. 115 stars, MIT, default branch `master`, last commit April 14, 2026 (v3.1.3).

## Server runtime

### Python with raw MCP SDK

Python 82.4% server using the raw MCP Python SDK (FastMCP not explicitly referenced). Version pin from pyproject.toml not surfaced; Python version floor not surfaced. uv-based packaging.

## Transport

### stdio

Default transport.

### Streamable HTTP

`streamable-http` transport supported (default port 9887 — published, suggesting HTTP deployment is a first-class path).

### SSE (Server-Sent Events)

SSE transport supported.

### Selection mechanism

CLI flag selects transport; host/port configurable.

## Capability surface

### Domain-bundled tool set

24 tools covering Jenkins domain entities — job management, build operations, queue handling, node/view queries, console output retrieval.

## Configuration delivery

### CLI flags

CLI arguments for Jenkins URL, username, password, SSL verification, session-singleton mode, read-only mode, transport selection with host/port.

### HTTP request headers

Per-request credentials supplied on each MCP request via `x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password` headers — instead of being baked into the server process. Turns the normally single-tenant stdio server into a multi-tenant HTTP service.

## Authentication

### Static API key / token via env var

Static-mode auth: Jenkins username + password (or API token) supplied via CLI flags at launch.

### Per-request HTTP-header credentials

Per-request mode: `x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password` headers carry credentials per MCP request. Requires HTTP transport. Lets one deployed server route different requests to different Jenkins instances.

## Multi-tenancy

### Per-request tenancy by inbound credential / bearer token

`x-jenkins-*` HTTP headers carry credentials per request, so the same deployed server serves multiple tenants from different Jenkins instances. Server is account-agnostic; tenancy is determined entirely by the credential headers on each request.

### Connection-lifecycle as a knob

Session-singleton toggle reuses one Jenkins client across tool calls for connection pooling — explicit knob trading session-state preservation against stateless-per-request safety.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published as `mcp-jenkins` on PyPI; canonical install: `uvx mcp-jenkins`.

### PyPI via pip / pipx

Also `pip install mcp-jenkins`.

### Docker / OCI image

Docker image published to `ghcr.io/lanbaoshen/mcp-jenkins:latest`. README install: `docker run ghcr.io/lanbaoshen/mcp-jenkins:latest`.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `mcp-jenkins` registered.

### `uvx <package>`

`uvx mcp-jenkins` is the canonical zero-install runner form.

### Docker container entrypoint

Dockerfile under `/docker` with multi-platform builds.

## Build and packaging

### Hatchling + uv (Python)

uv-based pyproject.toml. Lock file presence not surfaced.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile under `/docker` directory.

### Multi-architecture image publishing

Multi-platform builds in the Docker artifact path.

### Published Docker image

Pre-built image at `ghcr.io/lanbaoshen/mcp-jenkins:latest` doubles as distribution channel and deployment artifact.

## Test stack

### pytest with async + coverage

`/tests/` directory present; framework not surfaced explicitly.

## CI

### GitHub Actions

`.github/` present (GitHub Actions).

### Codecov integration

Codecov integration in CI.

## Repository layout

### Single-package src-layout

Single package layout with `/docker/`, `/tests/`, `.github/` directories.

## Host integration

### Claude Desktop

Documented JSON `mcpServers` entry.

### VS Code / VS Code Insiders / Visual Studio family

`.vscode/mcp.json` entry documented for VSCode Copilot Chat.

### JetBrains IDE

Documented JetBrains IDE integration.

## Developer ergonomics

### Sample MCP client configs in repo

`.vscode/mcp.json` sample.

## Release and lifecycle

### Active development

Last commit April 14, 2026 (v3.1.3).

### License — Permissive (MIT / Apache-2.0)

MIT.
