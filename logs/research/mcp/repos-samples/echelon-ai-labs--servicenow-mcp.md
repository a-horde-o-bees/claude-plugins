# Sample

Mirrors of `https://github.com/echelon-ai-labs/servicenow-mcp`. ServiceNow MCP server — 60+ tools across incidents, service catalog, change requests, agile, workflows, knowledge bases, user management; stdio and SSE ship as separate console scripts. 241 stars, MIT, default branch `main`.

## Server runtime

### Python with raw MCP SDK

Python (99.4%) on raw `mcp` Python SDK; Starlette as the SSE web framework. `requires-python >=3.11`. Likely import pattern `from mcp.server import Server`.

## Transport

### stdio

Default mode, invoked as `python -m servicenow_mcp.cli`.

### SSE (Server-Sent Events)

SSE mode via Starlette web server, invoked as `servicenow-mcp-sse --instance-url=... --username=... --password=...`.

### Selection mechanism

Separate console scripts per transport — distinct binaries for stdio (`python -m servicenow_mcp.cli`) vs SSE (`servicenow-mcp-sse`). Architecturally split rather than env-var-switched.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

60+ tools across nine functional areas: Incident management, Service catalog, Change requests, Agile management, Workflows, Script includes, Changesets, Knowledge bases, User management. Very broad enterprise-ITSM surface.

## Configuration delivery

### CLI flags

SSE mode takes `--instance-url`, `--username`, `--password` and similar.

### Environment variables

`SERVICENOW_INSTANCE_URL`, `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD`, `SERVICENOW_AUTH_TYPE`. Both stdio and SSE modes accept env vars.

## Authentication

### Multi-method selector

Three auth methods — Basic Auth (username/password), OAuth client credentials, API Key — with `SERVICENOW_AUTH_TYPE` env var as the selector. Common where the upstream is enterprise SaaS whose customers mandate different auth shapes.

## Multi-tenancy

### Single-user / single-tenant per process

Single ServiceNow instance per deployment (via env/URL).

## Distribution channel

### Source clone with editable install

`git clone ... && python -m venv .venv && pip install -e .` is the documented install. Plain `pip install -e .` workflow with stdlib `venv`; no uv/uvx workflow declared.

### Docker / OCI image

Dockerfile present. Specific image publication not captured.

## Entry point and launch

### Module invocation / `python -m <module>` fallback

stdio mode: `python -m servicenow_mcp.cli`.

### Console script via `[project.scripts]` / npm bin

SSE mode: `servicenow-mcp-sse` console script with CLI args.

### Multiple entry points per transport

Two separate entry points for different transports — `python -m servicenow_mcp.cli` (stdio) vs `servicenow-mcp-sse` (SSE) — architecturally split rather than env-var-switched.

## Build and packaging

### Python version pinning

`requires-python >=3.11`.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

## Test stack

### pytest with async + coverage

`tests/` directory present. Framework specifics not captured beyond presence. Starlette suggests async for the SSE path.

## Repository layout

### Single-package src-layout

Single-package layout under `servicenow_mcp/`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
