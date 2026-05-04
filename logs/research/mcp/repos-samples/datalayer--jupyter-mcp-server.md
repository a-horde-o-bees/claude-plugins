# Sample

Mirrors of `https://github.com/datalayer/jupyter-mcp-server`. Jupyter notebook MCP server — 16+ tools for notebook/cell CRUD and execution; runs standalone or mounts as a Jupyter Server extension. ~1,000 stars; BSD-3-Clause; default branch `main`; active (206 commits on main); v1.0.0 released.

## Server runtime

### Python with raw MCP SDK

Python (71.9% of repo), Jupyter Notebook (27.3%). Raw `mcp[cli] >= 1.10.1`; also pulls FastAPI/uvicorn for HTTP surface. Import pattern: `mcp.server` / `mcp.server.fastmcp` (via `mcp[cli]`). `requires-python >= 3.10`. Async (tornado/fastapi under the hood); pytest suite is async. Heavy web stack (`jupyter_server`, `tornado>=6.1`, `fastapi`, `uvicorn`) reflects that this server brokers a live Jupyter kernel rather than a stateless data layer.

## Transport

### Streamable HTTP

Streamable HTTP is the primary transport.

### stdio

stdio is the alternative transport.

### Selection mechanism

CLI launcher flag / config; the MCP client JSON picks the transport via the command shape.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

16+ tools — file listing, kernel listing, JupyterLab connection, notebook CRUD (use/read/restart), cell ops (execute/insert/delete/overwrite), full-notebook run, selected-cell fetch.

## Configuration delivery

### Environment variables

`JUPYTER_URL`, `JUPYTER_TOKEN`, `ALLOW_IMG_OUTPUT`, `DOCUMENT_ID`. v1.0.0+ adds `MCP_TOKEN` distinct from `JUPYTER_TOKEN`.

### Host-side JSON config snippet

Claude Desktop JSON config snippet (uvx form) and generic MCP-client snippets documented; Docker run examples included.

## Authentication

### Static API key / token via env var

Token-based auth: `JUPYTER_TOKEN` for the upstream Jupyter server; `MCP_TOKEN` for the MCP interface (v1.0.0+).

### Layered auth (protocol-level + upstream-level)

v1.0.0 introduced `MCP_TOKEN` as a dedicated MCP-level token separate from the Jupyter-level `JUPYTER_TOKEN` — auth split by protocol layer; breaking change from 0.x. Operator can independently control "who can talk to MCP" vs "what MCP does upstream against Jupyter."

## Multi-tenancy

### Single connection per server instance

Single JupyterLab instance per server process.

### Connection-lifecycle as a knob

`DOCUMENT_ID` env var plus `use_notebook` tool switches the active notebook target at runtime — per-notebook switchable session within a single Jupyter connection. Refinement proposed for an explicit "per-notebook switchable session" path.

## Distribution channel

### PyPI via pip / pipx

`pip install jupyter-mcp-server`.

### PyPI via uvx (zero-install runner)

`uvx jupyter-mcp-server@latest`.

### Docker / OCI image

`datalayer/jupyter-mcp-server:latest` on Docker Hub.

### Multi-channel publication

PyPI + uvx + Docker — multi-channel publication.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` declares `jupyter-mcp-server` mapped to `jupyter_mcp_server.CLI:server`.

### `uvx <package>`

Host-config snippet: `uvx jupyter-mcp-server@latest`.

### Mounted into another runtime as an extension

Server can run as a Jupyter Server extension (mounts inside the Jupyter process); extension scaffolding under `jupyter-config/`. Dual role: standalone MCP server or in-process extension of Jupyter.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling (~1.21). Version manager convention: standard PyPI; uvx-runnable.

### Optional-dependency fan-out

`test` extra pulls jupyter components and collab tools; `lint` and `typing` extras provided; `mcp` CLI usable via `mcp[cli]` extra.

## Schema and types

### Pydantic v2 models

Pydantic via the MCP SDK; FastAPI models for the HTTP layer; schema auto-derived.

### Async model (cross-cutting)

Async (tornado/fastapi under the hood); pytest suite is async.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

### Published Docker image

Official image on Docker Hub (`datalayer/jupyter-mcp-server`).

## Test stack

### pytest with async + coverage

pytest with `test` extra pulling jupyter components and collab tools; `tests/` directory; `pytest.ini` present.

## CI

### GitHub Actions

GitHub Actions in `.github/`.

## Repository layout

### Single-package, organized subdirectories

Single-package (`jupyter_mcp_server/`) plus `jupyter-config/` extension scaffolding plus `docs/`.

### Sibling-package factoring

Depends on companion package `jupyter-mcp-tools>=0.1.6` — tool definitions are factored out into a separate PyPI project. Splits the protocol harness from the tool catalog as an explicit reuse pattern.

## Host integration

### Claude Desktop

JSON config snippet (uvx form).

### Generic / host-agnostic snippet

Generic JSON snippet documented; Docker run examples.

### JupyterLab as a host

Installable as Jupyter Server extension (`jupyter-config/`) — JupyterLab itself is the host.

## Observability

### OpenTelemetry instrumentation

`opentelemetry-api` and `opentelemetry-sdk` (>=1.24.0) as core deps — instrumented out of the box. OTel baked into core deps rather than optional; every installation ships observability.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

None observed.

## Developer ergonomics

### Sample MCP client configs in repo

Claude Desktop and other host JSONs in README; Jupyter-lab launch with token documented.

### Linter and type-checker stack

`lint` and `typing` extras provided.

## Release and lifecycle

### Tagged release with version in changelog

v1.0.0 released; v1.0.0 introduced breaking changes (split tokens, dedicated MCP-level auth).

### Active development

206 commits on main; ongoing project.

### License — Permissive (BSD-3-Clause)

BSD-3-Clause — permissive license with explicit attribution and non-endorsement clauses. Functionally similar to MIT/Apache (commercial-friendly, no copyleft) but distinguished by the legal text, particularly the requirement that the project's name and contributors not be used to endorse derivative products without permission.
