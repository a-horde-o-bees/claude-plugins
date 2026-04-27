# Sample

## Identification
### url

https://github.com/isaaccorley/planetary-computer-mcp

### stars

~3

### last-commit (date or relative)

v1.3.3 released 2026-04-16; active

### license

Apache 2.0

### default branch

main

### one-line purpose

Microsoft Planetary Computer / NASA STAC MCP server — queries geospatial/earth data catalogs; co-located TypeScript VS Code extension.

## 1. Language and runtime
### language(s) + version constraints

Python 87.5%, TypeScript 11.3% (VS Code extension); Python version via `.python-version`

### framework/SDK in use

raw `mcp` SDK (Anthropic MCP Python implementation) — README phrasing suggests Claude Agent SDK / MCP rather than FastMCP

### pitfalls observed

none noted in this repo

## 2. Transport
### supported transports

stdio (MCP default)

### how selected

stdio-only implicit

### pitfalls observed

none noted in this repo

## 3. Distribution
### every mechanism observed

source clone + `uv sync`; VS Code extension for editor integration

### published package name(s)

not confirmed on PyPI; repo distributed as-clone

### install commands shown in README

`uv sync` (runtime), `uv sync --dev` (dev)

- pitfalls observed:
  - Whether the repo publishes to PyPI or is distribution-as-source-only not confirmed

## 4. Entry point / launch
### command(s) users/hosts run

`python -m planetary_computer_mcp.server`

### wrapper scripts, launchers, stubs

VS Code extension under `vscode-extension/`

### pitfalls observed

none noted in this repo

## 5. Configuration surface
### how config reaches the server

function-call parameters + environment; specifics not documented

### pitfalls observed

none noted in this repo

## 6. Authentication
### flow

none at MCP layer

### where credentials come from

Planetary Computer STAC API is publicly accessible

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy
### single-user / per-request tenant / workspace-keyed / not applicable / other

single-user

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed
### tools / resources / prompts / sampling / roots / logging / other

2 tools — `download_data` (unified raster/DEM/climate data), `download_geometries` (vector/building data); automatic geocoding and natural-language dataset detection

### pitfalls observed

none noted in this repo

## 9. Observability
### logging destination + format, metrics, tracing, debug flags

not documented

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location

### VS Code

dedicated extension in `vscode-extension/` directory

### Claude Desktop

implied via `python -m` command pattern

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed; VS Code extension is a parallel host integration

### pitfalls observed

none noted in this repo

## 12. Tests
### presence, framework, location, notable patterns

pytest via `uv run pytest`; `tests/` directory

### pitfalls observed

none noted in this repo

## 13. CI
### presence, system, triggers, what it runs

GitHub Actions configured

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts
### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

not observed

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics
### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`uv run pre-commit run --all-files` for checks

### pitfalls observed

none noted in this repo

## 16. Repo layout
### single-package / monorepo / vendored / other

monorepo-ish — `src/` with `core/`, `tools/`, `server.py`, plus parallel `vscode-extension/` (TypeScript) subproject

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Ships a **VS Code extension** alongside the MCP server — parallel non-MCP integration path in the same repo
- Supports multi-format outputs (GeoTIFF, GeoParquet, Zarr) — uncommon in MCP servers; implies large-file handling
- Generates visualizations for LLM analysis — the server synthesizes images for the model to interpret

## 18. Unanticipated axes observed
### decision dimensions this repo reveals

co-located VS Code extension (TypeScript) with the Python MCP server — mixed-language repo to cover editor integration outside MCP; LLM-targeted visualization generation (not just data retrieval) as a deliberate design choice

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom — raw `mcp` SDK implied
- version pin from pyproject.toml — not surfaced
- import pattern observed — `mcp.server`

### Python version floor
- `requires-python` value — via `.python-version`; exact value not surfaced

### Packaging
- build backend — not surfaced; uv-based workflow
- lock file present — `uv.lock` likely (uv sync convention)
- version manager convention — uv + `.python-version`

### Entry point
- `[project.scripts]` console script / `__main__.py` / bare script / other — `__main__.py` (module invoked with `python -m`)
- actual console-script name(s) — none surfaced
- host-config snippet shape — `python -m planetary_computer_mcp.server`

### Install workflow expected of end users
- pip / pipx / uv tool install / uvx run / poetry / source clone + venv / Docker / other — source clone + `uv sync`
- one-liner the README recommends — `uv sync`

### Async and tool signatures
- sync `def` or `async def` — likely async (STAC clients tend to be async)

### Type / schema strategy
- Pydantic via MCP SDK
- schema auto-derived

### Testing
- pytest / pytest-asyncio / unittest / none — pytest (via `uv run pytest`)

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other — pre-commit via `uv run pre-commit run --all-files`

### Notable Python-specific choices
- `python -m module.server` launch pattern — module-level invocation rather than console script
- Raw MCP SDK in 2026 — many newer servers have migrated to FastMCP; this one stays on the lower-level SDK

## 20. Gaps
- Exact pyproject contents and version pins not read
- Whether the repo publishes to PyPI or is distribution-as-source-only not confirmed
- Auth/config specifics beyond "no auth" not surfaced
