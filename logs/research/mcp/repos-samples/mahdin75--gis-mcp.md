# Sample

Mirrors of `https://github.com/mahdin75/gis-mcp`. GIS MCP server — wraps 92 geospatial tools across 5+ Python libraries (Shapely, GeoPandas, Rasterio, PyProj, GDAL, PySAL) with per-library optional-extras fan-out, plus REST `/storage/*` endpoints for HTTP-mode binary artifact transfer; ships `llms.txt`. ~137 stars, MIT, default branch `main`, v0.14.0 (2025-12-21).

## Server runtime

### Python with FastMCP

Python server built on FastMCP 2.x with exact pin `fastmcp == 2.13.1` — conservative against FastMCP API drift. Import pattern: `fastmcp`. `requires-python = ">=3.10"`. FastMCP auto-wraps both sync and async tool signatures.

## Transport

### stdio

Default transport for local use.

### Streamable HTTP

HTTP transport selectable via `GIS_MCP_TRANSPORT=http`; runs on port 9010 via Docker.

### SSE (Server-Sent Events)

SSE transport supported.

### Selection mechanism

Environment variable `GIS_MCP_TRANSPORT` selects transport — container-friendly env-var-driven selection.

## Capability surface

### Library fan-out

92 tools spanning Shapely (29), PyProj (13), GeoPandas (13), Rasterio (20), PySAL (18), visualization (2), plus data-acquisition modules (climate, ecology, movement, land cover, satellite imagery). "GIS Swiss army knife" — wrapping multiple upstream Python libraries into one MCP surface.

### REST endpoints alongside MCP tools

HTTP mode adds `/storage/upload`, `/storage/download`, `/storage/list` REST endpoints for binary artifact transfer that MCP isn't designed for. MCP layer carries metadata; REST layer carries bytes.

## Configuration delivery

### Environment variables

`GIS_MCP_TRANSPORT` controls transport selection.

### Host-side JSON config snippet

Per-host JSON config snippets documented for Claude Desktop and Cursor.

## Authentication

### None / implicit (local-resource gating)

No authentication at the MCP layer. Downstream API keys (e.g. Copernicus cdsapi) handled via dataset-specific config.

### Per-source independent API keys with graceful degradation

Downstream provider credentials (e.g., Copernicus cdsapi) are dataset-specific and optional per data source.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user; HTTP mode exposes per-user upload/download endpoints but no tenant isolation.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published as `gis-mcp` on PyPI. README install: `uv pip install gis-mcp` (with optional extras). Optional extras include `[visualize]`.

### Source clone with editable install

`uv pip install -e .` for development.

### Docker / OCI image

Two Dockerfiles — `Dockerfile` (prod) and `Dockerfile.local` (dev). Docker run on port 9010 for HTTP transport.

### Smithery registry

`smithery.yaml` registered with Smithery.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `gis-mcp` registered as `gis_mcp.main:main`.

### Module invocation / `python -m <module>` fallback

`python -m gis_mcp` as alternate entry.

### Docker container entrypoint

Docker images handle HTTP transport setup on port 9010.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. uv-based workflow. `uv.lock` presence not explicitly confirmed.

### Optional-dependency fan-out

Eight domain-specific optional extras — `administrative-boundaries`, `climate`, `ecology`, `movement`, `satellite-imagery`, `land-cover`, `visualize`, plus `test`. Each extra bundles a single upstream library; `all` extra composes most. Per-library extras let users install only the toolchain slices they need. Heavy geospatial deps (rasterio, fiona, geopandas) kept as core deps despite large wheels — prioritizes install simplicity over minimal footprint.

### Pin discipline (Python)

Exact pin `fastmcp == 2.13.1` — prioritizes reproducibility over upgrade speed; conservative against FastMCP API drift.

## Schema and types

### FastMCP auto-derivation from type hints

Schema auto-derived from signatures via FastMCP. Pydantic for validation.

## Container artifacts

### Multi-Dockerfile (prod / dev split)

Two-variant container strategy — `Dockerfile` for production, `Dockerfile.local` for development. Explicit separation when the dev image needs additional tooling or different base.

## Test stack

### pytest with async + coverage

pytest with coverage and async support (in `test` extra); `tests/` directory.

### Dev extras gating test deps

Test dependencies gated behind a `test` optional-extra rather than installed by default.

## CI

### GitHub Actions

GitHub Actions in `.github/workflows/`; CI badge visible. Whether CI publishes to PyPI on tag is not confirmed.

## Repository layout

### Single-package src-layout

`src/gis_mcp/` source layout with rich optional-extras fan-out.

## Host integration

### Claude Desktop

`~/.config/Claude/claude_desktop_config.json` snippet documented.

### Cursor

`.cursor/mcp.json` snippet documented.

### Smithery / Glama discovery

`smithery.yaml` registered with Smithery.

## Developer ergonomics

### `agents/` example directory

`agents/` directory provides runnable example clients.

## Documentation surface

### `llms.txt` / `llms-full.txt`

`llms.txt` and `llms-full.txt` shipped at repo root for "vibe coding" LLM context — the two-file pattern (digestible summary + complete reference).

## Release and lifecycle

### Active development

v0.14.0 (2025-12-21); active.

### License — Permissive (MIT / Apache-2.0)

MIT.
