# Sample

Mirrors of `https://github.com/rohitg00/kubectl-mcp-server`. kubectl MCP server — 253 tools across ~20 Kubernetes resource categories; dual Python/npm distribution; optional OAuth 2.1 (RFC 9728) bolt-on. 870 stars, MIT, default branch `main`, active on main; CNCF Landscape listing noted in README.

## Server runtime

### Python with FastMCP

Python (81.2%), TypeScript (17.0%), Shell (0.8%); Python 3.9+. FastMCP (specific major version not surfaced in README); also uses the underlying MCP Python SDK. FastMCP default applies for sync-vs-async (not surfaced at README level).

## Transport

### stdio

stdio is the default.

### SSE (Server-Sent Events)

SSE supported.

### Streamable HTTP

streamable-http supported.

### HTTP with JSON response mode

HTTP supported alongside streamable-http.

### Selection mechanism

CLI flags / environment variables; host/port configurable (default 0.0.0.0:8000 for HTTP modes).

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

253 tools across ~20 categories (pods, deployments, namespaces, services, storage, security, Helm, cost, browser automation); 8 resources; 8 prompts.

### Tools + resources + prompts + UI dashboards

Maximal MCP surface — 253 tools, 8 resources, 8 prompts, plus 6 interactive dashboards (gated on `[ui]` install extra). 26 browser automation tools (optional).

### Capability gating flags (per-tool, per-category, write-mode)

`--disable-destructive` safety flag suppresses destructive operations; `MCP_BROWSER_ENABLED` / `MCP_BROWSER_PROVIDER` env vars gate browser-automation sub-feature; optional `[ui]` extra gates dashboards.

### Capability gating via tool subsets at install time

Optional-extra-gated feature bundles — `[ui]` extra enables dashboards; browser automation separate. Operator opts in to feature groups at install time.

## Configuration delivery

### Environment variables

`KUBECONFIG`, `MCP_DEBUG`, `MCP_LOG_FILE`, `MCP_BROWSER_ENABLED`, `MCP_BROWSER_PROVIDER`, `MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE`.

### CLI flags

`--disable-destructive`, transport/host/port options.

### Mounted credentials

Consumes the kubeconfig file at `~/.kube/config`.

## Authentication

### Delegated to upstream toolchain credentials

kubeconfig-based for Kubernetes API — server delegates to the kubectl-class credential model (`~/.kube/config`).

### Mounted file credentials

Kubeconfig mounted/read from `~/.kube/config` at startup.

### OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)

Optional OAuth 2.1 layer (RFC 9728) for the MCP server itself, configured via env vars (`MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE`). Layered on top of stdio/HTTP transports.

## Multi-tenancy

### Single-user / single-tenant per process

Single kubeconfig context per server; optional OAuth layer suggests tenant support but documented as single kubeconfig per process.

## Distribution channel

### PyPI via pip / pipx

`pip install kubectl-mcp-server[ui]` documented; package name `kubectl-mcp-server` on PyPI.

### npm via npx / bunx

`npx -y kubectl-mcp-server` — npm wrapper that invokes the Python package; package name `kubectl-mcp-server` on npm.

### Docker / OCI image

`docker pull rohitghumare64/kubectl-mcp-server:latest` from Docker Hub.

### Pre-built binary release

GitHub releases artifacts.

### Cross-ecosystem packaging

Distributed via both PyPI and npm so npm-only hosts can install without Python packaging knowledge — same conceptual artifact in two ecosystems.

### Multi-channel publication

Four parallel channels — PyPI, npm, Docker Hub, GitHub releases.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

console script `kubectl-mcp-server`; host-config snippet shape `command: kubectl-mcp-server` or via npx in Node-first hosts.

### `npx -y <package>` / `bunx`

`npx -y kubectl-mcp-server` for Node-first hosts; npm wrapper invokes the Python package.

### Docker container entrypoint

Docker image entrypoint via `docker pull rohitghumare64/kubectl-mcp-server:latest`.

## Build and packaging

### Setuptools (with `setup.py` or `setup.cfg`)

Build backend: setuptools (`setup.py`) — older setuptools convention rather than modern pyproject-only layout.

### Optional-dependency fan-out

`[ui]` extra for dashboards — install-time opt-in.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP default (Pydantic-based) inferred; specifics not surfaced. Schema auto-derivation via FastMCP.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present; Docker Hub image published.

### Published Docker image

`rohitghumare64/kubectl-mcp-server:latest` published to Docker Hub.

## Test stack

### pytest with async + coverage

234+ passing tests, pytest-based; unit + integration + server-initialization suites; fixture style not surfaced.

## CI

### GitHub Actions

GitHub Actions workflows under `.github/`.

## Host integration

### Claude Desktop

JSON `mcpServers` entry.

### Cursor

JSON `mcpServers` entry (same shape).

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Windsurf supported via JSON `mcpServers` entry.

### VS Code / VS Code Insiders / Visual Studio family

GitHub Copilot supported via JSON `mcpServers` entry.

### Multi-host catalog (30+ agents)

15+ other MCP clients supported via the same JSON `mcpServers` shape.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not observed.

## Observability

### Debug toggle + log file path

`MCP_DEBUG` + `MCP_LOG_FILE` environment toggles; no metrics/tracing documented.

## Documentation surface

### README as the canonical surface

README hosts JSON `mcpServers` sample configs for multiple clients; CNCF Landscape listing noted.

## Developer ergonomics

### Sample MCP client configs in repo

JSON `mcpServers` sample configs for multiple clients in README.

## Repository layout

### Single-package with dual-ecosystem wrapper

Single-package Python library with npm publisher wrapper that invokes the Python entry point; modular submodules per resource kind (pods.py, deployments.py, helm.py, etc.), separate `resources/` and `prompts/` dirs.

## Safety and security posture

### Destructive-action gating flag

`--disable-destructive` CLI flag suppresses destructive operations across the kubectl/Helm tool surface.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

Active on main (exact date not surfaced); CNCF Landscape listing noted in README.
