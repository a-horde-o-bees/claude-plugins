# rohitg00/kubectl-mcp-server

## Identification
- url: https://github.com/rohitg00/kubectl-mcp-server
- stars: 870
- last-commit (date or relative): active on main (exact date not surfaced on repo page)
- license: MIT
- default branch: main
- one-line purpose: kubectl MCP server — 253 tools covering the Kubernetes surface; dual Python/npm distribution; optional OAuth 2.1.

## 1. Language and runtime
- language(s) + version constraints: Python (81.2%), TypeScript (17.0%), Shell (0.8%); Python 3.9+
- framework/SDK in use: FastMCP (references to FastMCP in configuration; also uses the underlying MCP Python SDK)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default), SSE, streamable-http, HTTP
- how selected: CLI flags / environment variables; host/port configurable (default 0.0.0.0:8000 for HTTP modes)
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI, npm (npx wrapper), Docker Hub, GitHub releases
- published package name(s): kubectl-mcp-server (PyPI), kubectl-mcp-server (npm)
- install commands shown in README: `pip install kubectl-mcp-server[ui]`; `npx -y kubectl-mcp-server`; `docker pull rohitghumare64/kubectl-mcp-server:latest`
- pitfalls observed:
  - distributed via both PyPI and npm so npm-only hosts can still install without Python packaging knowledge

## 4. Entry point / launch
- command(s) users/hosts run: `kubectl-mcp-server` (console script)
- wrapper scripts, launchers, stubs: npm wrapper that invokes the Python package; Docker image entrypoint; optional `[ui]` extra for dashboards
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables (`KUBECONFIG`, `MCP_DEBUG`, `MCP_LOG_FILE`, `MCP_BROWSER_ENABLED`, `MCP_BROWSER_PROVIDER`, `MCP_AUTH_*`) plus CLI flags (`--disable-destructive`, transport/host/port options); consumers of the kubeconfig file at `~/.kube/config`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: kubeconfig-based for Kubernetes API; optional OAuth 2.1 layer (RFC 9728) for the MCP server itself
- where credentials come from: kubeconfig file; OAuth issuer/audience/JWKS via `MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE` env vars
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single-user per process; optional OAuth layer suggests tenant support but documented as single kubeconfig context per server
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 253 tools across ~20 categories (pods, deployments, namespaces, services, storage, security, Helm, cost, browser automation); 8 resources; 8 prompts; 6 interactive dashboards (UI extra); 26 browser automation tools (optional)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: `MCP_DEBUG` + `MCP_LOG_FILE` environment toggles; no metrics/tracing documented
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location
- Claude Desktop: JSON `mcpServers` entry
- Cursor, Windsurf, GitHub Copilot, 15+ other MCP clients: JSON `mcpServers` entry (same shape)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: not observed
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: 234+ passing tests, pytest-based; unit + integration + server-initialization suites
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions workflows under `.github/`
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile and Docker Hub image published
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: JSON `mcpServers` sample configs for multiple clients; `--disable-destructive` safety flag; optional `[ui]` extra for dashboards
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single-package Python library with npm publisher wrapper; modular submodules per resource kind (pods.py, deployments.py, helm.py, etc.), separate `resources/` and `prompts/` dirs
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- exposes very large surface area (253 tools) partitioned by Kubernetes resource kind
- ships a dedicated browser-automation sub-feature gated on `MCP_BROWSER_ENABLED`
- distributed via both PyPI and npm so npm-only hosts can still install without Python packaging knowledge
- OAuth 2.1 option layered on top of stdio/HTTP transports

## 18. Unanticipated axes observed
- decision dimensions this repo reveals:
    - dual-ecosystem publishing (Python + npm) for a single Python server
    - optional-extra-gated feature bundles (`[ui]` enables dashboards; browser automation separate)
    - RFC 9728 OAuth bolt-on for an otherwise local stdio server

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / custom: FastMCP (specific major version not surfaced in README)
- version pin from pyproject.toml: not surfaced
- import pattern observed: not surfaced at README level

### Python version floor
- `requires-python` value: 3.9+

### Packaging
- build backend: setuptools (setup.py)
- lock file present: not surfaced
- version manager convention: pip/uv compatible; npm distribution pulls Python package

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: console script `kubectl-mcp-server`
- actual console-script name(s): `kubectl-mcp-server`
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path): `command: kubectl-mcp-server` or via npx in Node-first hosts

### Install workflow expected of end users
- install form + one-liner from README: `pip install kubectl-mcp-server[ui]` (Python users); `npx -y kubectl-mcp-server` (npm users); `docker pull rohitghumare64/kubectl-mcp-server:latest` (container users)

### Async and tool signatures
- sync `def` or `async def`: not surfaced at README level
- asyncio/anyio usage: FastMCP default

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: FastMCP default (Pydantic-based) inferred; specifics not surfaced
- schema auto-derived vs hand-authored: FastMCP auto-derivation

### Testing
- pytest / pytest-asyncio / unittest / none: pytest (234+ tests)
- fixture style: not surfaced

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: not surfaced

### Notable Python-specific choices
- open bullets:
    - uses setup.py (older setuptools convention) rather than modern pyproject-only layout
    - CNCF Landscape listing noted in README

## 20. Gaps
- what couldn't be determined: exact Python entry-point file path, requires-python metadata from pyproject, FastMCP major version pin, async-vs-sync tool signatures, last-commit date, Dockerfile base image
