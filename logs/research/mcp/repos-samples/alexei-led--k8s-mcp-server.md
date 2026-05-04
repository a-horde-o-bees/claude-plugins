# Sample

Mirrors of `https://github.com/alexei-led/k8s-mcp-server`. Kubernetes tooling MCP server — wraps `kubectl`, `helm`, `istioctl`, `argocd` with Unix-pipe support (jq/grep/sed) for result filtering. 207 stars, MIT, default branch `master`, last release v1.4.2 on 2026-02-27.

## Server runtime

### Python with raw MCP SDK

Direct use of Anthropic's `mcp` Python SDK (raw, not FastMCP per README). Python 3.13+ floor — an unusually high floor for April 2026. Python is 96.2% of the repo (Dockerfile 2.9%, Makefile 0.9%).

## Transport

### stdio

Default transport for Claude Desktop integration.

### Streamable HTTP

Recommended for remote deployment.

### SSE (Server-Sent Events)

Supported but documented as deprecated.

### Selection mechanism

CLI flags / environment configuration.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Tool wrappers around `kubectl`, `helm`, `istioctl`, `argocd` plus Unix piping support (`jq`, `grep`, `sed`) for result filtering — multiple cluster-tooling CLIs bundled behind a single MCP surface.

## Configuration delivery

### Environment variables

`K8S_CONTEXT`, `K8S_NAMESPACE`, `K8S_MCP_TIMEOUT`; security modes; cloud provider credentials (AWS/GCP/Azure). Security-mode configuration delivered as an environment variable rather than a CLI flag.

### Mounted credentials

kubeconfig and cloud-provider credential files mounted into the container as volumes — host-managed credentials reach the containerized server through the volume mount surface.

## Authentication

### Mounted file credentials

kubeconfig credentials inherited from a mounted file; cloud-provider credentials for managed clusters mounted as volumes.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user; one container per kubeconfig/context.

## Distribution channel

### Docker / OCI image

GitHub Container Registry (`ghcr.io/alexei-led/k8s-mcp-server:latest`) is the canonical distribution channel. Docker-first README — README steers users toward the container over a pip install.

### Source clone with editable install

Source clone documented as a secondary path.

## Entry point and launch

### Docker container entrypoint

Docker container is the primary launch surface — host-config snippet shape: `docker run` invocation passed via Claude Desktop's `command`/`args`.

## Build and packaging

### Hatchling + uv (Python)

`pyproject.toml` with the `uv` package manager. Lock file implied via the uv-based workflow.

### Python version pinning

`requires-python` floor is 3.13+ — an aggressive modern-Python target.

### System-level dependencies

System binary required (CLI on PATH) — server depends on `kubectl`, `helm`, `istioctl`, `argocd` at the host level. Docker becomes the only self-contained distribution path; the package manager cannot install these.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile at repo root; ghcr.io image is the canonical distribution form.

### Published Docker image

`ghcr.io/alexei-led/k8s-mcp-server:latest` — pre-built image at a known registry.

## Test stack

### pytest with async + coverage

`/tests/` directory present; pytest framework not directly verified.

## CI

### GitHub Actions

`.github/workflows/` with `release.yml` and `ci.yml`.

## Host integration

### Claude Desktop

JSON `mcpServers` entry via `claude_desktop_config.json`.

## Repository layout

### Single-package src-layout

Single package under `src/k8s_mcp_server/` with sibling `/tests/`, `/docs/`, `.github/workflows/`.

## Documentation surface

### README plus docs directory

Supplementary `/docs/` directory alongside README.

## Developer ergonomics

### Makefile / Makefile.toml

Makefile at repo root.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

v1.4.2 released 2026-02-27; single-maintainer with recent activity.
