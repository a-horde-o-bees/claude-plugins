# Sample

Mirrors of `https://github.com/awslabs/mcp/tree/main/src/aws-documentation-mcp-server`. AWS documentation MCP server — fetches and converts AWS docs to markdown; partition-scoped tools differ between global AWS and China partitions. Apache-2.0, default branch `main`, sub-server inside the awslabs/mcp monorepo.

## Server runtime

### Python with raw MCP SDK

Direct use of `mcp[cli]>=1.23.0` — no FastMCP dependency. Author works against `mcp.server` primitives. Import pattern likely `from mcp.server import Server` (raw SDK convention). `httpx` is sync-or-async; async likely given network-bound work. Schemas likely hand-authored on raw `mcp` SDK. Minimalist dependency set (6 runtime deps).

## Transport

### stdio

stdio is the primary transport; Docker runs stdio inside a container.

### Selection mechanism

Implicit single mode — stdio.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools — `read_documentation` (URL → markdown), `search_documentation` (global partition only), `read_sections`, `recommend`, `get_available_services` (China partition only).

### Partition-scoped tool gating

Same binary exposes a different tool set depending on AWS partition — global AWS exposes search/recommend; China partition exposes service discovery (`get_available_services`).

## Configuration delivery

### Environment variables

Minimal env-var surface — User-Agent override env var for corporate proxies; partition selection (global vs China) likely env-configured. Partition-switching mechanism not directly captured.

## Authentication

### None / implicit (local-resource gating)

No auth required — fetches public AWS documentation. Stateless read-only against public upstream.

## Multi-tenancy

### Stateless read-only (any number of instances)

Not applicable — stateless read-only fetching of public docs; any number of instances can run without conflict.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published as `awslabs.aws-documentation-mcp-server` on PyPI; canonical install `uvx awslabs.aws-documentation-mcp-server@latest`.

### Windows .exe variant

Explicit Windows entry — `uv tool run --from awslabs.aws-documentation-mcp-server@latest awslabs.aws-documentation-mcp-server.exe`.

### Docker / OCI image

Dockerfile present; `docker build -t mcp/aws-documentation .`.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `awslabs.aws-documentation-mcp-server` → `awslabs.aws_documentation_mcp_server.server:main`.

### `uvx <package>`

Host-config snippet shape: `uvx awslabs.aws-documentation-mcp-server@latest`.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. Version manager convention: uv / uvx.

### Python version pinning

`requires-python = ">=3.10"`.

## Schema and types

### Hand-authored tool schemas

Raw `mcp` SDK without FastMCP — tool handlers register explicit input schema dicts; schemas hand-authored. `pydantic>=2.10.6` declared for structured payloads.

### Pydantic v2 models

`pydantic>=2.10.6` for structured payloads.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile at sub-package root.

## Test stack

### pytest with async + coverage

pytest with `--cov --cov-branch` — branch-coverage enforcement.

### Branch coverage enforcement

`--cov --cov-branch` for branch-level coverage measurement, beyond statement coverage.

### Live integration test gating

Custom `--run-live` pytest flag gates tests that hit real AWS docs; default test runs stay offline.

## CI

### Monorepo CI inheritance

Parent monorepo runs CI; per-sub-server CI not extracted.

## Host integration

### Monorepo catalog

Host-specific configs covered in parent monorepo catalog, not sub-server README.

## Observability

### loguru (Python)

`loguru` for structured logging.

## Repository layout

### Monorepo of namespace-prefixed packages

Sub-package inside the awslabs/mcp monorepo. Each sub-package has its own `pyproject.toml` and PyPI release.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.
