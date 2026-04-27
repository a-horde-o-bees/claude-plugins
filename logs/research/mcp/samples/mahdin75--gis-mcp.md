# Sample

## Identification
### url

https://github.com/mahdin75/gis-mcp

### stars

~137

### last-commit (date or relative)

v0.14.0 (2025-12-21); active

### license

MIT

### default branch

main

### one-line purpose

GIS MCP server — 92 geospatial tools across 5 libraries (Shapely, GeoPandas, Rasterio, PyProj, GDAL) with per-library optional-extras fan-out; ships `llms.txt`.

## 1. Language and runtime
### language(s) + version constraints

Python, `requires-python >= 3.10`

### framework/SDK in use

FastMCP 2.x (`fastmcp == 2.13.1`)

### pitfalls observed

none noted in this repo

## 2. Transport
### supported transports

stdio (default for local), HTTP (`GIS_MCP_TRANSPORT=http`), SSE

### how selected

env var `GIS_MCP_TRANSPORT`

### pitfalls observed

none noted in this repo

## 3. Distribution
### every mechanism observed

PyPI (`uv pip install gis-mcp`), source editable (`uv pip install -e .`), Docker (two Dockerfiles — prod and local), Smithery (`smithery.yaml`)

### published package name(s)

`gis-mcp`

### install commands shown in README

`uv pip install gis-mcp`, `uv pip install gis-mcp[visualize]`, Docker build/run

- pitfalls observed:
  - Whether CI publishes to PyPI on tag not confirmed

## 4. Entry point / launch
### command(s) users/hosts run

`gis-mcp` console script, `python -m gis_mcp`, or HTTP on port 9010 via Docker

### wrapper scripts, launchers, stubs

Docker images handle HTTP transport setup

### pitfalls observed

none noted in this repo

## 5. Configuration surface
### how config reaches the server

environment variables (`GIS_MCP_TRANSPORT`), host-config JSON for Claude Desktop / Cursor

### pitfalls observed

none noted in this repo

## 6. Authentication
### flow

none at MCP layer

### where credentials come from

N/A; downstream API keys (e.g. Copernicus cdsapi) via dataset-specific config

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy
### single-user / per-request tenant / workspace-keyed / not applicable / other

single-user; HTTP mode exposes per-user upload/download endpoints but no tenant isolation

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed
### tools / resources / prompts / sampling / roots / logging / other

**92 tools** spanning Shapely (29), PyProj (13), GeoPandas (13), Rasterio (20), PySAL (18), visualization (2), and data-acquisition modules (climate, ecology, movement, land cover, satellite imagery). HTTP mode adds `/storage/upload`, `/storage/download`, `/storage/list` REST endpoints

### pitfalls observed

none noted in this repo

## 9. Observability
### logging destination + format, metrics, tracing, debug flags

not specified in README

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location

### Claude Desktop

`~/.config/Claude/claude_desktop_config.json` snippet

### Cursor

`.cursor/mcp.json` snippet

### Smithery

`smithery.yaml` registered

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed

### pitfalls observed

none noted in this repo

## 12. Tests
### presence, framework, location, notable patterns

pytest with coverage and async support (in `test` extra); `tests/` directory

### pitfalls observed

none noted in this repo

## 13. CI
### presence, system, triggers, what it runs

GitHub Actions in `.github/workflows/`; CI badge visible

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts
### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

`Dockerfile` (prod) and `Dockerfile.local` (dev) — two-variant container strategy

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics
### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`agents/` example directory; `llms.txt` / `llms-full.txt` for "vibe coding" context; pre-commit-style workflow

### pitfalls observed

none noted in this repo

## 16. Repo layout
### single-package / monorepo / vendored / other

single-package (`src/gis_mcp/`) with rich optional-extras fan-out

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- `fastmcp == 2.13.1` exact pin — conservative against FastMCP API drift
- 8 domain-specific optional extras (`administrative-boundaries`, `climate`, `ecology`, `movement`, `satellite-imagery`, `land-cover`, `visualize`, plus `test`) — each extra bundles a single upstream library; `all` extra composes most
- Two Dockerfiles (`Dockerfile` vs `Dockerfile.local`) — explicit separation of production image from development image
- `llms.txt` and `llms-full.txt` in repo — expose a curated context summary for LLM consumers beyond the MCP protocol itself

## 18. Unanticipated axes observed
### decision dimensions this repo reveals

wrapping *92* tools from 5+ distinct Python libraries into one MCP surface — a "GIS Swiss army knife" pattern; exposing file-transfer REST endpoints (`/storage/*`) alongside MCP tools to handle binary artifact movement that MCP isn't built for

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom — FastMCP 2.x
- version pin from pyproject.toml — `fastmcp == 2.13.1`
- import pattern observed — `fastmcp`

### Python version floor
- `requires-python` value — `>=3.10`

### Packaging
- build backend — hatchling
- lock file present — not explicitly confirmed; uv-based workflow
- version manager convention — uv

### Entry point
- `[project.scripts]` console script / `__main__.py` / bare script / other — both `gis-mcp` console script and `python -m gis_mcp` work
- actual console-script name(s) — `gis-mcp` → `gis_mcp.main:main`
- host-config snippet shape — Claude Desktop uses direct command `gis-mcp`; Docker uses HTTP URL

### Install workflow expected of end users
- pip / pipx / uv tool install / uvx run / poetry / source clone + venv / Docker / other — `uv pip install gis-mcp` (with optional extras), Docker
- one-liner the README recommends — `uv pip install gis-mcp`

### Async and tool signatures
- sync `def` or `async def` — FastMCP auto-wraps both; pytest has async support

### Type / schema strategy
- Pydantic via FastMCP
- schema auto-derived from signatures

### Testing
- pytest / pytest-asyncio / unittest / none — pytest + coverage + async plugin (in `test` extra)
- fixture style — not inspected

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other — `agents/` directory provides runnable example clients

### Notable Python-specific choices
- Optional-extra-per-library pattern — exposes an opt-in fan-out: users install only the GIS toolchain they need
- Heavy geospatial deps (rasterio, fiona, geopandas) kept as *core* deps despite large wheels — prioritizes install simplicity over minimal footprint

## 20. Gaps
- `uv.lock` presence not explicitly confirmed
- Whether CI publishes to PyPI on tag not confirmed
- Exact list of optional extras provided by `all` not fully enumerated
