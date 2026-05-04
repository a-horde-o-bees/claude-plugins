# Sample

Mirrors of `https://github.com/shibuiwilliam/mcp-server-scikit-learn`. scikit-learn MCP server — model lifecycle (train → eval → persist) exposed as a tool surface; raw `mcp` Python SDK (not FastMCP); host-config uses `uv --directory=` rather than `uvx`. ~13 stars, MIT, default branch `main`. Last commit not surfaced.

## Server runtime

### Python with raw MCP SDK

Raw `mcp` Python SDK (not FastMCP). Import pattern `mcp.server`. Python version floor not surfaced. Python 99.7% of repo, Makefile 0.3%.

## Transport

### stdio

stdio (MCP default); stdio-only.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Tools spanning the scikit-learn lifecycle: model training/evaluation, dataset handling, preprocessing, feature engineering, model persistence, cross-validation, hyperparameter tuning. Wraps an ML pipeline as a tool surface rather than a notebook flow.

## Configuration delivery

### Host-side JSON config snippet

MCP-server JSON config (command/args) — no env-based config documented.

## Authentication

### None / implicit (local-resource gating)

No auth — operates on local data and models.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user.

## Distribution channel

### Source clone with editable install

`pip install -e ".[dev]"` — source clone + editable install with dev tools via PEP 621 optional deps.

### Source clone with `uv run` from source tree

Host-config invocation uses `uv --directory=src/mcp_server_scikit_learn run mcp-server-scikit-learn` — path-anchored uv run from the source tree.

## Entry point and launch

### `uv --directory` from source

Host-config invocation `uv --directory=src/mcp_server_scikit_learn run mcp-server-scikit-learn` — path-anchored launch from source directory rather than `uvx <package>` zero-install runner. Implies the package isn't meant for general distribution, more for developer-installed local runs.

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` declares `mcp-server-scikit-learn` console script.

## Build and packaging

### Hatchling + uv (Python)

uv-backed packaging; build backend not surfaced. `uv.lock` present.

### `uv.lock` committed

`uv.lock` file present.

### Optional-dependency fan-out

`.[dev]` install pattern — dev tools via PEP 621 optional deps, not a separate `requirements-dev.txt`.

## Schema and types

### Pydantic v2 models

Pydantic via MCP SDK.

## Test stack

### pytest with async + coverage

pytest invoked via `pytest -s -v tests/`; `tests/` directory.

## CI

### GitHub Actions

GitHub Actions infrastructure present (specific triggers/jobs not extracted).

## Host integration

### Claude Desktop

JSON command/args snippet using `uv --directory=... run`.

## Repository layout

### Single-package src-layout

Single-package src-layout: `src/mcp_server_scikit_learn/`.

## Developer ergonomics

### Makefile / Makefile.toml

Makefile present for developer commands.

## Documentation surface

### README as the canonical surface

README is the canonical surface.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
