# Sample

Mirrors of `https://github.com/feiskyer/mcp-kubernetes-server`. Kubernetes MCP server — 50+ tools across kubectl/helm execution, read-only queries, write operations, delete operations, rollout/scaling; four-way verb-disable flags (kubectl/helm/write/delete) for fine-grained capability gating. 16 stars, Apache-2.0, default branch `main`, last commit May 11, 2025 (v0.1.11).

## Server runtime

### Python with raw MCP SDK

Python (99.7%) on raw MCP Python SDK with Anthropic's Claude Agent SDK wrapper around the MCP protocol. `requires-python` value: 3.11+. Sync subprocess wrapping rather than the kubernetes-client async Python library — wraps kubectl/helm subprocess calls.

## Transport

### stdio

Default mode.

### SSE (Server-Sent Events)

Selectable transport.

### Streamable HTTP

Selectable transport.

### Selection mechanism

CLI flag at startup — `--transport`, plus `--host` and `--port` for network modes.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

50+ tools across kubectl command execution, helm command execution, read-only queries, write operations (create/apply), delete operations, rollout/scaling.

### Capability gating flags (per-tool, per-category, write-mode)

Four-way verb-disable CLI flags: `--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`. Granular per-capability toggles instead of a single read-only/full switch — per-verb enable/disable as an argument surface pattern.

## Configuration delivery

### Environment variables

`KUBECONFIG` for kubeconfig path.

### CLI flags

`--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`, `--transport`, `--host`, `--port`.

## Authentication

### Delegated to upstream toolchain credentials

Delegates to kubeconfig credentials. Permissions check via kubectl's auth subsystem (`k8s_auth_can_i`, `k8s_auth_whoami`). The server does not authenticate at all on its own — shells out to kubectl/helm which already know how to read their own credential file.

### Mounted file credentials

Credentials read from kubeconfig file at startup.

## Multi-tenancy

### Single-user / single-tenant per process

Single user per process — single kubeconfig context.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uvx mcp-kubernetes-server`; published as `mcp-kubernetes-server`.

### Docker / OCI image

ghcr.io image.

### Source clone with editable install

Source available as alternative install.

## Entry point and launch

### Module invocation / `python -m <module>` fallback

`python -m src.mcp_kubernetes_server.main`.

### Console script via `[project.scripts]` / npm bin

Console script via uvx; specific console-script name not surfaced.

## Build and packaging

### Hatchling + uv (Python)

pyproject.toml with uv. Lock file: implied (uv). Version manager convention: uv.

### Python version pinning

`requires-python` value: 3.11+.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

### Published Docker image

ghcr.io image.

## Test stack

### No tests / not surfaced

Framework not surfaced. GitHub Actions `build.yml` suggests CI-driven tests; specific framework, fixture style, and patterns not surfaced in README.

## CI

### GitHub Actions

GitHub Actions (`build.yml`).

## Safety and security posture

### Destructive-action gating flag

Four-way verb-disable flags (kubectl/helm/write/delete) supply orthogonal denial axes — finer-grained than the binary read-only knob common elsewhere. Per-verb gating is a denial-ish denominator for capability gating.

## Host integration

### Claude Desktop

JSON `mcpServers` entry.

### Cursor

JSON `mcpServers` entry.

### VS Code / VS Code Insiders / Visual Studio family

GitHub Copilot JSON `mcpServers` entry.

### Codex CLI / Copilot CLI / Gemini CLI

ChatGPT Copilot JSON `mcpServers` entry.

## Repository layout

### Single-package src-layout

Single package under `src/mcp_kubernetes_server/`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Tagged release with version in changelog

v0.1.11 released May 11, 2025.
