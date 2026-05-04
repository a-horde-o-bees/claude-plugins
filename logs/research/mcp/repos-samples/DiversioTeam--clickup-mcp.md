# Sample

Mirrors of `https://github.com/DiversioTeam/clickup-mcp`. ClickUp task-management MCP server — 28 tools covering task CRUD, discovery, assignments, bulk ops, time tracking, analytics, and user management. 3 stars, MIT, default branch `main`. Test-density vs popularity skew — 62 pytest tests on a 3-star repo, well above average for its popularity tier.

## Server runtime

### Python with raw MCP SDK

Python 100% on raw `mcp>=0.1.0` (extremely loose pin) with `click` for CLI wrapping. Pin is unusual — most projects pin much tighter. Other pyproject.toml dependencies: `httpx>=0.27.0`, `pydantic>=2.0.0`, `pydantic-settings>=2.0.0`, `platformdirs>=4.0.0`, `python-dotenv>=1.0.0`, `click>=8.1.0`, `rich>=13.0.0`. Import pattern likely `from mcp.server import Server` given raw SDK. `requires-python = ">=3.10"`. Async likely (httpx + pytest-asyncio).

## Transport

### stdio

Default MCP transport; no alternative documented.

## Capability surface

### Domain-bundled tool set

28 tools organized by entity-type and operation class — task management, discovery, assignments, navigation, bulk operations, time tracking, analytics, user management.

## Configuration delivery

### Environment variables

`CLICKUP_MCP_API_KEY` env var as alternative credential path.

### Persistent OS-native config

Config persisted via `platformdirs` to a platform-appropriate directory (`~/.config/` on Linux, `%APPDATA%` on Windows) by the `set-api-key` subcommand of the same binary — unlike the dominant "env var only" pattern. Survives across launches without per-host env-var setup. Unusual in this corpus.

## Authentication

### Static API key / token via env var

ClickUp personal API token (generated from Settings → Apps → API). Supplied either via `set-api-key` subcommand (persisted via `platformdirs`) or via `CLICKUP_MCP_API_KEY` env var.

## Multi-tenancy

### Single-user / single-tenant per process

Single workspace per API key; personal-token scope.

## Distribution channel

### Install-from-git via uvx

`uvx --from git+https://github.com/DiversioTeam/clickup-mcp clickup-mcp` is the primary install path. No PyPI publication; the git URL becomes the effective package index.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `clickup-mcp` declared in `[project.scripts]` pointing to `clickup_mcp.__main__:main` rather than `clickup_mcp.server:main` — `__main__.py`-based entry. Host-config snippet shape: `uvx clickup-mcp` (after git-install).

### Subcommand verb

The binary exposes management subcommands beyond running the server: `set-api-key`, `check-config`, `test-connection`, `--debug`. Mode is verb-selectable; the same console script handles both the server protocol and a separate CLI for configuration.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. Version manager convention: `uv` / `uvx`. Lock file presence not captured.

## Schema and types

### Pydantic v2 models

`pydantic>=2.0.0` for validation; `pydantic-settings>=2.0.0` for typed config (env + file loading).

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio + pytest-cov in dev deps; 62 tests in the suite.

## CI

### GitHub Actions

GitHub Actions CI workflow present.

## Repository layout

### Single-package src-layout

Single-package (`clickup_mcp/` with `__main__.py`).

## Observability

### `--verbose` flag

`--debug` flag escalates log verbosity; `rich` used for formatted CLI output (relevant for the management subcommands rather than the MCP server protocol itself).

## Developer ergonomics

### Setup subcommands on the MCP binary

The same console script that runs the MCP server protocol exposes management subcommands (`set-api-key`, `check-config`, `test-connection`) for credential setup and connectivity verification. Doubles the binary as a config CLI; uses `rich` and `click` for human-facing output. Pattern echoes `kubectl config`-style CLIs.

### Linter and type-checker stack

ruff + mypy configured.
