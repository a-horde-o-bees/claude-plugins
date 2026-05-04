# Sample

Mirrors of `https://github.com/datalayer/earthdata-mcp-server`. NASA Earthdata MCP server — search datasets and granules with temporal/bbox filters and download granules via manifest/download/script modes. ~25 stars; BSD-3-Clause; default branch `main`; active (ongoing CI runs).

## Server runtime

### Python with raw MCP SDK

Python (85.9% of repo); raw `mcp[cli] >= 1.2.1` (not FastMCP). Import pattern: `mcp.server`. `requires-python >= 3.10`. Likely sync execution model — `earthaccess` (the upstream NASA-auth wrapper) is sync.

## Transport

### stdio

stdio is the documented MCP transport. Docker adapter shown for host-networking mode.

### Selection mechanism

Implicit single mode — stdio is the only transport observed.

## Capability surface

### Tools-only, hand-curated narrow surface

3 tools: `search_earth_datasets` (with temporal/bbox filters), `search_earth_datagranules`, `download_earth_data_granules`.

## Configuration delivery

### Environment variables

`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD` env vars for NASA credentials.

### Host-side JSON config snippet

Claude Desktop JSON `mcpServers` block with Docker command; separate variant for Linux host networking.

## Authentication

### Static API key / token via env var

NASA Earthdata Login (username/password) supplied via `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` env vars. Uses `earthaccess` library (official NASA-auth wrapper) — delegates the auth dance to a vendor-supplied client.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user — bound to one NASA account.

## Safety and security posture

### Mode parameter for plan-vs-execute

`download_earth_data_granules` exposes three execution modes via a parameter (manifest / download / script) — clean separation of "describe what you would do" from "do it." Lets the model preview what would happen before committing to execution; the underlying operation is expensive (large granule downloads), so a dry-run mode is a deliberate design choice.

## Distribution channel

### PyPI via pip / pipx

`pip install earthdata-mcp-server`. PyPI package: `earthdata-mcp-server`.

### Docker / OCI image

`datalayer/earthdata-mcp-server:latest` on Docker Hub. Pre-built image.

### Source clone with editable install

Source clone supported.

### Smithery registry

Ships `smithery.yaml` for registry registration as a first-class artifact.

### Multi-channel publication

PyPI + Docker + Smithery + source — multi-channel publication shape.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` declares `earthdata-mcp-server = earthdata_mcp_server.server:server`.

### Docker container entrypoint

Docker invocation as alternative launch via `docker run`.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling (~1.21).

### Optional-dependency fan-out

`test` extra (`pytest>=7.0`), `lint` extra (mdformat + ruff), `typing` extra (mypy) — clean PEP 621 optional-deps taxonomy.

## Schema and types

### Pydantic v2 models

Pydantic via the MCP SDK; schema auto-derived.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

### Published Docker image

Pre-built image on Docker Hub (`datalayer/earthdata-mcp-server`).

## Test stack

### pytest with async + coverage

pytest via `test` extra (`pytest>=7.0`); "Unit Tests" badge visible.

## CI

### GitHub Actions

GitHub Actions in `.github/workflows/` including lint + type-check pipeline.

## Repository layout

### Single-package src-layout

Single-package (`earthdata_mcp_server/`) plus `dev/` plus `docs/`.

## Host integration

### Claude Desktop

JSON `mcpServers` block with Docker command; separate variant for Linux host networking.

### Smithery / Glama discovery

`smithery.yaml` registers the server in the Smithery registry as a first-class artifact.

## Observability

### `rich`-decorated stdlib logging (Python)

`rich` in deps implies colorized console output. No structured observability layer documented.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

None observed.

## Developer ergonomics

### Makefile / Makefile.toml

Makefile with targets including `make pull-docker`.

### Linter and type-checker stack

`lint` extra: mdformat + mdformat-gfm + ruff. `typing` extra: mypy. `mdformat` + `mdformat-gfm` in lint extras — docs/markdown linting as part of developer workflow.

## Release and lifecycle

### Active development

Active project with ongoing CI runs.

### License — Permissive (BSD-3-Clause)

BSD-3-Clause — permissive license with explicit attribution and non-endorsement clauses. Functionally similar to MIT/Apache (commercial-friendly, no copyleft) but distinguished by the legal text, particularly the requirement that the project's name and contributors not be used to endorse derivative products without permission.
