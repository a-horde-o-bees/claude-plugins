# Sample

Mirrors of `https://github.com/isaaccorley/planetary-computer-mcp`. Microsoft Planetary Computer / NASA STAC MCP server — Python server querying geospatial/earth data catalogs; co-located TypeScript VS Code extension as a parallel host integration. ~3 stars, Apache 2.0, default branch `main`, v1.3.3 released 2026-04-16.

## Server runtime

### Python with raw MCP SDK

Python 87.5% with raw `mcp` SDK (Anthropic MCP Python implementation). Import pattern observed: `mcp.server`. README phrasing suggests Claude Agent SDK / MCP rather than FastMCP. Many newer servers have migrated to FastMCP; this one stays on the lower-level SDK.

## Transport

### stdio

stdio (MCP default) — stdio-only.

### Selection mechanism

Implicit default — stdio-only, no transport flag.

## Capability surface

### Tools-only, hand-curated narrow surface

2 tools — `download_data` (unified raster/DEM/climate data), `download_geometries` (vector/building data). Automatic geocoding and natural-language dataset detection at the tool-handler layer.

## Configuration delivery

### Environment variables

Configuration via environment + function-call parameters; specific env var names not documented.

## Authentication

### None / implicit (local-resource gating)

None at MCP layer — Planetary Computer STAC API is publicly accessible.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user.

## Distribution channel

### Source clone with editable install

Source clone + `uv sync` (runtime), `uv sync --dev` (dev). PyPI publication not confirmed.

## Entry point and launch

### Module invocation / `python -m <module>` fallback

`python -m planetary_computer_mcp.server` — module-level invocation rather than console script. `__main__.py` packaging convention.

## Build and packaging

### Hatchling + uv (Python)

uv-based workflow; `uv sync`-managed. `uv.lock` likely (uv sync convention). Build backend not surfaced in extract.

### Python version pinning

Python version via `.python-version`; exact value not surfaced. uv + `.python-version` version manager convention.

## Schema and types

### Pydantic v2 models

Pydantic via MCP SDK; schema auto-derived. STAC clients tend to be async — likely async tool signatures.

## Host integration

### Co-located VS Code extension

Co-located VS Code extension under `vscode-extension/` directory — TypeScript subproject parallel to the Python MCP server, mixed-language repo to cover editor integration outside MCP.

### Claude Desktop

Implied via `python -m` command pattern.

## Test stack

### pytest with async + coverage

pytest via `uv run pytest`; `tests/` directory.

## CI

### GitHub Actions

GitHub Actions configured.

## Container artifacts

### No container artifacts

Not observed.

## Repository layout

### Cross-language monorepo / mixed-language layout

Monorepo-ish — `src/` with `core/`, `tools/`, `server.py`, plus parallel `vscode-extension/` (TypeScript) subproject. Mixed-language layout (Python 87.5%, TypeScript 11.3%).

## Domain logic and embedded intelligence

### Visualization synthesis

Generates visualizations for LLM analysis — server synthesizes images for the model to interpret. Multi-format outputs (GeoTIFF, GeoParquet, Zarr) — uncommon in MCP servers; implies large-file handling.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache 2.0.

### Tagged release with version in changelog

v1.3.3 released 2026-04-16; active.

### Active development

Active recent release cadence.

## Developer ergonomics

### `pre-commit` framework

`uv run pre-commit run --all-files` for checks.

### `uv run <tool>` invocations

`uv run pytest`, `uv run pre-commit` — uv-orchestrated tool invocations.
