# Sample

## Identification

### url

https://github.com/rohitg00/kubectl-mcp-server

### stars

870

### last-commit

active on main (exact date not surfaced on repo page).

### license

MIT

### default branch

main

### one-line purpose

kubectl MCP server — 253 tools covering the Kubernetes surface; dual Python/npm distribution; optional OAuth 2.1.

## Language and runtime

### language(s) + version constraints

Python (81.2%), TypeScript (17.0%), Shell (0.8%); Python 3.9+.

### framework/SDK in use

FastMCP (references to FastMCP in configuration; also uses the underlying MCP Python SDK).

## Transport

### supported transports

stdio (default), SSE, streamable-http, HTTP.

### how selected

CLI flags / environment variables; host/port configurable (default 0.0.0.0:8000 for HTTP modes).

## Distribution

### every mechanism observed

PyPI, npm (npx wrapper), Docker Hub, GitHub releases.

### published package name(s)

kubectl-mcp-server (PyPI), kubectl-mcp-server (npm).

### install commands shown in README

`pip install kubectl-mcp-server[ui]`; `npx -y kubectl-mcp-server`; `docker pull rohitghumare64/kubectl-mcp-server:latest`.

### pitfalls observed

Distributed via both PyPI and npm so npm-only hosts can still install without Python packaging knowledge.

## Entry point / launch

### command(s) users/hosts run

`kubectl-mcp-server` (console script).

### wrapper scripts, launchers, stubs

npm wrapper that invokes the Python package; Docker image entrypoint; optional `[ui]` extra for dashboards.

## Configuration surface

### how config reaches the server

Environment variables (`KUBECONFIG`, `MCP_DEBUG`, `MCP_LOG_FILE`, `MCP_BROWSER_ENABLED`, `MCP_BROWSER_PROVIDER`, `MCP_AUTH_*`) plus CLI flags (`--disable-destructive`, transport/host/port options); consumes the kubeconfig file at `~/.kube/config`.

## Authentication

### flow

kubeconfig-based for Kubernetes API; optional OAuth 2.1 layer (RFC 9728) for the MCP server itself.

### where credentials come from

kubeconfig file; OAuth issuer/audience/JWKS via `MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE` env vars.

## Multi-tenancy

### tenancy model

Single-user per process; optional OAuth layer suggests tenant support but documented as single kubeconfig context per server.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

253 tools across ~20 categories (pods, deployments, namespaces, services, storage, security, Helm, cost, browser automation); 8 resources; 8 prompts; 6 interactive dashboards (UI extra); 26 browser automation tools (optional).

## Observability

### logging destination + format, metrics, tracing, debug flags

`MCP_DEBUG` + `MCP_LOG_FILE` environment toggles; no metrics/tracing documented.

## Host integrations shown in README or repo

### Claude Desktop

JSON `mcpServers` entry.

### Cursor, Windsurf, GitHub Copilot, 15+ other MCP clients

JSON `mcpServers` entry (same shape).

## Claude Code plugin wrapper

### presence and shape

not observed

## Tests

### presence, framework, location, notable patterns

234+ passing tests, pytest-based; unit + integration + server-initialization suites.

## CI

### presence, system, triggers, what it runs

GitHub Actions workflows under `.github/`.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile and Docker Hub image published.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

JSON `mcpServers` sample configs for multiple clients; `--disable-destructive` safety flag; optional `[ui]` extra for dashboards.

## Repo layout

### single-package / monorepo / vendored / other

Single-package Python library with npm publisher wrapper; modular submodules per resource kind (pods.py, deployments.py, helm.py, etc.), separate `resources/` and `prompts/` dirs.

## Notable structural choices

Exposes very large surface area (253 tools) partitioned by Kubernetes resource kind. Ships a dedicated browser-automation sub-feature gated on `MCP_BROWSER_ENABLED`. Distributed via both PyPI and npm so npm-only hosts can still install without Python packaging knowledge. OAuth 2.1 option layered on top of stdio/HTTP transports.

## Unanticipated axes observed

Dual-ecosystem publishing (Python + npm) for a single Python server. Optional-extra-gated feature bundles (`[ui]` enables dashboards; browser automation separate). RFC 9728 OAuth bolt-on for an otherwise local stdio server.

## Python-specific

### SDK / framework variant

FastMCP (specific major version not surfaced in README); version pin and import pattern not surfaced.

### Python version floor

`requires-python` value: 3.9+.

### Packaging

Build backend: setuptools (setup.py). Lock file presence not surfaced. Version manager convention: pip/uv compatible; npm distribution pulls Python package.

### Entry point

console script `kubectl-mcp-server`; host-config snippet shape `command: kubectl-mcp-server` or via npx in Node-first hosts.

### Install workflow expected of end users

`pip install kubectl-mcp-server[ui]` (Python users); `npx -y kubectl-mcp-server` (npm users); `docker pull rohitghumare64/kubectl-mcp-server:latest` (container users).

### Async and tool signatures

Sync-vs-async not surfaced at README level; FastMCP default applies.

### Type / schema strategy

FastMCP default (Pydantic-based) inferred; specifics not surfaced. Schema auto-derivation via FastMCP.

### Testing

pytest (234+ tests); fixture style not surfaced.

### Dev ergonomics

not surfaced

### Notable Python-specific choices

Uses `setup.py` (older setuptools convention) rather than modern pyproject-only layout. CNCF Landscape listing noted in README.

## Gaps

Exact Python entry-point file path, requires-python metadata from pyproject, FastMCP major version pin, async-vs-sync tool signatures, last-commit date, Dockerfile base image.
