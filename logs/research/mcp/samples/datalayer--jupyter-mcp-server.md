# Sample

## Identification

### url

https://github.com/datalayer/jupyter-mcp-server

### stars

~1,000

### last-commit

active (206 commits on main); v1.0.0 released

### license

BSD-3-Clause

### default branch

main

### one-line purpose

Jupyter notebook MCP server — 16+ tools for notebook/cell CRUD and execution; runs standalone or mounts as a Jupyter Server extension.

## 1. Language and runtime

### language(s) + version constraints

Python (71.9%), Jupyter Notebook (27.3%); `requires-python >= 3.10`.

### framework/SDK in use

raw `mcp[cli] >= 1.10.1`; also pulls FastAPI/uvicorn for HTTP surface.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

Streamable HTTP (primary), STDIO (alternative).

### how selected

CLI launcher flag / config; MCP client JSON picks the transport via the command shape.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (`pip install jupyter-mcp-server`), uvx (`uvx jupyter-mcp-server@latest`), Docker (`datalayer/jupyter-mcp-server:latest`).

### published package name(s)

`jupyter-mcp-server`.

### install commands shown in README

`pip install jupyter-mcp-server`; `uvx jupyter-mcp-server@latest`; Docker pull.

### pitfalls observed

Depends on a companion package `jupyter-mcp-tools>=0.1.6` — tool definitions are factored out into a separate PyPI project.

## 4. Entry point / launch

### command(s) users/hosts run

`jupyter-mcp-server` console script, or `uvx jupyter-mcp-server@latest`.

### wrapper scripts, launchers, stubs

Jupyter Server extension config under `jupyter-config/`; server can run standalone or as Jupyter extension.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

environment variables — `JUPYTER_URL`, `JUPYTER_TOKEN`, `ALLOW_IMG_OUTPUT`, `DOCUMENT_ID`, plus `MCP_TOKEN` in v1.0.0+.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

token-based.

### where credentials come from

`JUPYTER_TOKEN` (for the upstream Jupyter server) and `MCP_TOKEN` (for the MCP interface, v1.0.0+); breaking change from 0.x.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

per-notebook — `DOCUMENT_ID` and `use_notebook` tool switch targets at runtime; single JupyterLab instance per server process.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

16+ tools — file listing, kernel listing, JupyterLab connection, notebook CRUD (use/read/restart), cell ops (execute/insert/delete/overwrite), full-notebook run, selected-cell fetch.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

OpenTelemetry api+sdk (>=1.24.0) as core deps — instrumented out of the box.

### pitfalls observed

OpenTelemetry baked into core deps rather than optional — every installation ships observability.

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON config snippet (uvx form).

### Other MCP clients

generic JSON snippet; Docker run examples.

### JupyterLab

installable as Jupyter Server extension (jupyter-config/).

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest with `test` extra pulling jupyter components and collab tools; `tests/` directory; `pytest.ini` present.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions in `.github/`.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile + official image on Docker Hub (`datalayer/jupyter-mcp-server`).

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop and other host JSONs; Jupyter-lab launch with token documented.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`jupyter_mcp_server/`) + `jupyter-config/` extension scaffolding + `docs/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Dual role: runs as standalone MCP server or as Jupyter Server extension (mounts inside Jupyter process). OpenTelemetry baked into core deps rather than optional — every installation ships observability. Depends on a companion package `jupyter-mcp-tools>=0.1.6` — tool definitions are factored out into a separate PyPI project.

## 18. Unanticipated axes observed

Server-as-extension vs server-as-standalone is a deployment axis. Sibling-package factoring of tool definitions (jupyter-mcp-tools) is an unusual reuse pattern in MCP land. v1.0.0 introduced a dedicated MCP-level token separate from the Jupyter-level token (auth split by protocol layer).

## 19. Python-specific

### SDK / framework variant

raw `mcp[cli]` SDK; version pin: `mcp[cli] >= 1.10.1`; import pattern: `mcp.server` / `mcp.server.fastmcp` (via `mcp[cli]`).

### Python version floor

`requires-python` value: `>=3.10`.

### Packaging

build backend: hatchling (~1.21); lock file presence not confirmed; version manager convention: standard PyPI; uvx-runnable.

### Entry point

`[project.scripts]` → `jupyter_mcp_server.CLI:server`; actual console-script name: `jupyter-mcp-server`; host-config snippet shape: `uvx jupyter-mcp-server@latest`.

### Install workflow expected of end users

pip, uvx, Docker all first-class; one-liner: `pip install jupyter-mcp-server`; `uvx jupyter-mcp-server@latest`.

### Async and tool signatures

async (tornado/fastapi under the hood); pytest suite is async.

### Type / schema strategy

Pydantic via MCP SDK; FastAPI models for HTTP layer; schema auto-derived.

### Testing

pytest (via `test` extra); fixture style not inspected.

### Dev ergonomics

`lint` and `typing` extras provided; `mcp` CLI usable via `mcp[cli]` extra.

### Notable Python-specific choices

Heavy web stack in deps (`jupyter_server`, `tornado>=6.1`, `fastapi`, `uvicorn`) — reflects that this server brokers a live Jupyter kernel rather than a stateless data layer. `opentelemetry-api/sdk` are hard deps — server is designed for production observability out of the box.

## 20. Gaps

`uv.lock` presence not confirmed (repo uses hatchling but unclear on uv use). Exact content of `jupyter-mcp-tools` helper package not inspected. Full list of 16+ tools beyond categories not enumerated.
