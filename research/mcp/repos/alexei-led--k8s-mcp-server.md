# alexei-led/k8s-mcp-server

## Identification
- url: https://github.com/alexei-led/k8s-mcp-server
- stars: 207
- last-commit (date or relative): Feb 27, 2026 (v1.4.2)
- license: MIT
- default branch: master
- one-line purpose: Kubernetes tooling MCP server — wraps `kubectl`, `helm`, `istioctl`, `argocd` with Unix-pipe support (jq/grep/sed) for result filtering.

## 1. Language and runtime
- language(s) + version constraints: Python (96.2%), Dockerfile (2.9%), Makefile (0.9); Python 3.13+
- framework/SDK in use: raw MCP Python SDK (Anthropic's Model Context Protocol SDK, not FastMCP)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default for Claude Desktop), streamable-http (recommended for remote), sse (deprecated)
- how selected: CLI flags / environment configuration
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: GitHub Container Registry (ghcr.io), source clone
- published package name(s): ghcr.io/alexei-led/k8s-mcp-server
- install commands shown in README: Docker-first — `ghcr.io/alexei-led/k8s-mcp-server:latest`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: Docker container
- wrapper scripts, launchers, stubs: Dockerfile as the primary launcher; Makefile present
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables — `K8S_CONTEXT`, `K8S_NAMESPACE`, `K8S_MCP_TIMEOUT`, security modes, cloud provider credentials (AWS/GCP/Azure); kubeconfig and cloud credentials mounted into the container
- pitfalls observed:
  - decision dimensions this repo reveals: - pinning to a very recent Python (3.13+) as a floor - security-mode configuration as an environment variable rather than a CLI flag - bun...

## 6. Authentication
- flow: kubeconfig credentials inherited from mounted file; cloud provider credentials for managed clusters mounted as volumes
- where credentials come from: host-mounted kubeconfig + cloud provider credential files
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single-user; one container per kubeconfig/context
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: tool wrappers around `kubectl`, `helm`, `istioctl`, `argocd` plus Unix piping support (`jq`, `grep`, `sed`)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not surfaced in README
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location
- Claude Desktop: JSON `mcpServers` entry via `claude_desktop_config.json`
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: not observed
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: `/tests/` directory present; framework not surfaced
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions (`release.yml`, `ci.yml`)
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile present; ghcr.io image is the canonical distribution
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Makefile; documentation under `/docs/`
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single package under `src/k8s_mcp_server/`; `/tests/`, `/docs/`, `.github/workflows/`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Docker-first distribution — README steers users toward container over pip install
- wraps CLI tools rather than calling the Kubernetes API directly; supports shell piping with `jq`/`grep`/`sed` for result filtering
- single maintainer with recent activity

## 18. Unanticipated axes observed
- decision dimensions this repo reveals:
    - pinning to a very recent Python (3.13+) as a floor
    - security-mode configuration as an environment variable rather than a CLI flag
    - bundling multiple cluster tooling (`kubectl`/`helm`/`istioctl`/`argocd`) behind a single MCP surface

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / custom: raw `mcp` Python SDK
- version pin from pyproject.toml: not surfaced
- import pattern observed: not surfaced

### Python version floor
- `requires-python` value: 3.13+

### Packaging
- build backend: pyproject.toml with uv package manager
- lock file present: implied (uv-based workflow)
- version manager convention: uv

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: not surfaced — primary entry is the Docker container
- actual console-script name(s): not surfaced
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path): Docker run in `command`/`args` of Claude Desktop JSON

### Install workflow expected of end users
- install form + one-liner from README: `docker run ghcr.io/alexei-led/k8s-mcp-server:latest`

### Async and tool signatures
- sync `def` or `async def`: not surfaced
- asyncio/anyio usage: not surfaced

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: not surfaced
- schema auto-derived vs hand-authored: not surfaced

### Testing
- pytest / pytest-asyncio / unittest / none: tests/ directory present; framework not surfaced
- fixture style: not surfaced

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: Makefile present

### Notable Python-specific choices
- open bullets:
    - Python 3.13+ is an unusually high floor for April 2026 MCP server work
    - uv lock file implies reproducible dev env; still ships primarily via Docker

## 20. Gaps
- what couldn't be determined: exact async-vs-sync tool signatures, schema strategy, test framework specifics, console script name, logging mechanism
