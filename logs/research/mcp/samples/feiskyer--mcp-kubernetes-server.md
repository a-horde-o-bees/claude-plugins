# Sample

## Identification

### url

https://github.com/feiskyer/mcp-kubernetes-server

### stars

16

### last-commit

May 11, 2025 (v0.1.11)

### license

Apache-2.0

### default branch

main

### one-line purpose

Kubernetes MCP server — four-way verb disable flags (read/write/delete/exec) for fine-grained capability gating.

## 1. Language and runtime

### language(s) + version constraints

Python 99.7%; Python 3.11+.

### framework/SDK in use

raw MCP Python SDK (Anthropic's Claude Agent SDK wrapper around the MCP protocol).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (default), SSE, streamable-http.

### how selected

CLI flag `--transport`, plus `--host` and `--port` for network modes.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (uvx), Docker (ghcr.io), source.

### published package name(s)

mcp-kubernetes-server

### install commands shown in README

`uvx mcp-kubernetes-server`; docker from ghcr.io.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`python -m src.mcp_kubernetes_server.main` or console script via uvx.

### wrapper scripts, launchers, stubs

Dockerfile.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

environment variable `KUBECONFIG`; CLI flags `--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`, `--transport`, `--host`, `--port`.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

delegates to kubeconfig credentials; permissions check via kubectl's auth subsystem (`k8s_auth_can_i`, `k8s_auth_whoami`).

### where credentials come from

kubeconfig file.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user per process (single kubeconfig context).

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

50+ tools across command execution (kubectl, helm), read-only queries, write operations (create/apply), delete operations, rollout/scaling.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not surfaced in README.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON `mcpServers` entry.

### Cursor

JSON `mcpServers` entry.

### GitHub Copilot

JSON `mcpServers` entry.

### ChatGPT Copilot

JSON `mcpServers` entry.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not observed.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

GitHub Actions `build.yml` suggests CI-driven tests; framework not surfaced.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions (`build.yml`).

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; ghcr.io image.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

not surfaced in README excerpt.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single package under `src/mcp_kubernetes_server/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Granular per-capability CLI toggles (`--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`) instead of a single read-only/full switch. Apache-2.0 license (rarer for independent-maintainer MCP servers, which skew MIT).

## 18. Unanticipated axes observed

Per-verb enable/disable as an argument surface pattern (kubectl vs helm vs write vs delete split into four independent flags).

## 19. Python-specific

### SDK / framework variant

raw `mcp` Python SDK. Version pin from pyproject.toml: not surfaced. Import pattern observed: not surfaced.

### Python version floor

`requires-python` value: 3.11+.

### Packaging

build backend: pyproject.toml with uv. lock file present: implied (uv). version manager convention: uv.

### Entry point

module entry `src.mcp_kubernetes_server.main`. actual console-script name(s): not surfaced. host-config snippet shape: uvx.

### Install workflow expected of end users

`uvx mcp-kubernetes-server`.

### Async and tool signatures

sync — wraps kubectl/helm subprocess calls. asyncio/anyio usage: not surfaced; the underlying kubectl/helm wrapping is synchronous subprocess.

### Type / schema strategy

not surfaced. schema auto-derived vs hand-authored: not surfaced.

### Testing

not surfaced. fixture style: not surfaced.

### Dev ergonomics

not surfaced.

### Notable Python-specific choices

Sync subprocess wrapping rather than using the kubernetes-client async Python library. Four-way verb disable flags is a denial-ish denominator for capability gating.

## 20. Gaps

specific schema strategy, test framework, logging destination, async behavior, last-commit date after v0.1.11.
