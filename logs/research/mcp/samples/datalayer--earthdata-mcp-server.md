# Sample

## Identification

### url

https://github.com/datalayer/earthdata-mcp-server

### stars

~25

### last-commit

active (has ongoing CI runs)

### license

BSD-3-Clause

### default branch

main

### one-line purpose

NASA Earthdata MCP server — search datasets and granules with temporal/bbox filters and download granules via manifest/download/script modes.

## 1. Language and runtime

### language(s) + version constraints

Python 85.9%; `requires-python >= 3.10`.

### framework/SDK in use

raw `mcp[cli] >= 1.2.1` (not FastMCP).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (MCP default); Docker adapter shown for host-networking mode.

### how selected

stdio-only observed.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (`pip install earthdata-mcp-server`), Docker (`datalayer/earthdata-mcp-server:latest`), source clone.

### published package name(s)

`earthdata-mcp-server`.

### install commands shown in README

`pip install earthdata-mcp-server`; `docker run datalayer/earthdata-mcp-server:latest`.

### pitfalls observed

Ships `smithery.yaml` for registry registration as a first-class artifact.

## 4. Entry point / launch

### command(s) users/hosts run

`earthdata-mcp-server` console script; Docker invocation for container use.

### wrapper scripts, launchers, stubs

Makefile targets including `make pull-docker`.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Claude Desktop JSON `mcpServers` block; environment variables for NASA credentials.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

NASA Earthdata Login (username/password).

### where credentials come from

`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD` env vars.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user — bound to one NASA account.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

3 tools — `search_earth_datasets` (temporal/bbox filters), `search_earth_datagranules`, `download_earth_data_granules` (3-mode: manifest/download/script).

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

`rich` in deps implies colorized console output; no structured observability surfaced.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON `mcpServers` block with Docker command; separate variant for Linux host networking.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest (via `test` extra `pytest>=7.0`); "Unit Tests" badge visible.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions `.github/workflows/` including lint + type-check pipeline.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; pre-built image on Docker Hub; Smithery registration (`smithery.yaml`).

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Makefile with `pull-docker`, `dev/` directory.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`earthdata_mcp_server/`) + `dev/` + `docs/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Three download modes (manifest, download, script) rather than one — clearly separating "planning" from "execution" artifacts. Ships `smithery.yaml` for registry registration as a first-class artifact. Uses `earthaccess` library (official NASA-auth wrapper) — delegates the auth dance.

## 18. Unanticipated axes observed

Single tool exposes three output modes via a parameter (manifest vs script vs actual download) — clean separation of "describe what you would do" from "do it".

## 19. Python-specific

### SDK / framework variant

raw `mcp[cli] >= 1.2.1`; version pin: `mcp[cli] >= 1.2.1`; import pattern: `mcp.server`.

### Python version floor

`requires-python` value: `>=3.10`.

### Packaging

build backend: hatchling (~1.21); lock file presence not confirmed; version manager convention: hatchling-based PyPI publication.

### Entry point

`[project.scripts]` → `earthdata-mcp-server` → `earthdata_mcp_server.server:server`; actual console-script name: `earthdata-mcp-server`; host-config snippet shape: Docker run; pip-installed console script.

### Install workflow expected of end users

pip, Docker first-class; one-liner: `pip install earthdata-mcp-server`.

### Async and tool signatures

likely sync (`earthaccess` is sync).

### Type / schema strategy

Pydantic via MCP SDK.

### Testing

pytest (`>=7.0` in `test` extra); fixture style not inspected.

### Dev ergonomics

Makefile with `pull-docker`; `lint` extra (mdformat + ruff) and `typing` extra (mypy).

### Notable Python-specific choices

`mdformat` + `mdformat-gfm` in lint extras — docs/markdown linting as part of developer workflow. Scoping optional deps into `test` / `lint` / `typing` groups — clean PEP 621 optional-deps taxonomy.

## 20. Gaps

Exact Docker command/args for host-networking mode not captured. Whether CI publishes to PyPI on tag not confirmed. Lock-file convention not read.
