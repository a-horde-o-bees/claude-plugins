# Sample

Mirrors of `https://github.com/tumf/grafana-loki-mcp`. Grafana Loki log-query MCP server — multi-format output (text/JSON/markdown) for LogQL queries; uses Grafana as a proxy to Loki rather than connecting to Loki directly. 25 stars, MIT, default branch `main`. Active (103 commits). Discipline-first repo with pre-commit hooks shipped alongside the tool.

## Server runtime

### Python with FastMCP

Python 93.2% (Python 3.10+); FastMCP — major version pin from pyproject.toml not surfaced. Async-capable via FastMCP defaults (asyncio/anyio).

## Transport

### stdio

Stdio transport supported.

### SSE (Server-Sent Events)

SSE supported alongside stdio.

### Selection mechanism

CLI flag at startup / default — transport selectable via CLI flag with stdio as the default mode.

## Capability surface

### Domain-bundled tool set

Loki log querying via Grafana API; label name/value retrieval; time-range-configurable log retrieval. Multi-format output (text, JSON, markdown) per tool call.

## Configuration delivery

### Environment variables

`GRAFANA_URL` and `GRAFANA_API_KEY` env vars.

### CLI flags with paired env-var equivalents

CLI flags `-u <url>` and `-k <api-key>` paired with env-var equivalents — keeps stdio-launch config flexible.

## Authentication

### Static API key / token via env var

Grafana API key supplied via `GRAFANA_API_KEY` env var or `-k` CLI arg. Single credential per process.

## Multi-tenancy

### Single-user / single-tenant per process

Single Grafana instance / API key per process.

## Distribution channel

### PyPI via pip / pipx

`pip install grafana-loki-mcp` documented as install path. Package name `grafana-loki-mcp` on PyPI.

### PyPI via uvx (zero-install runner)

`uvx grafana-loki-mcp` documented as alternative install path.

### Source clone with editable install

Editable dev install: `uv pip install -e ".[dev]"`.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `grafana-loki-mcp`. Host-config snippet shape: `uvx grafana-loki-mcp -u ... -k ...` — required CLI args inline. Quoting concerns when the host wrapper config carries inline flags.

## Build and packaging

### Hatchling + uv (Python)

`pyproject.toml`-based; `setup.py` also present per README. `uv` + `pip` compatible. Lock file presence not surfaced.

### Python version pinning

`requires-python` floor: 3.10+.

## Schema and types

### FastMCP auto-derivation from type hints

Schema auto-derived via FastMCP from typed signatures; Pydantic assumed via FastMCP.

### Async model (cross-cutting)

Async-capable via FastMCP — asyncio/anyio defaults.

## Container artifacts

### No container artifacts

No Docker support mentioned in README.

## Test stack

### pytest with async + coverage

`pytest` with coverage reporting.

### Linter/formatter test gate

`ruff` + `black` + `mypy` toolchain — both `ruff` and `black` present.

## CI

### GitHub Actions

GitHub Actions workflows present.

### Pre-commit hooks

Pre-commit hooks configured and shipped alongside the tool — discipline-first repo.

## Repository layout

### Single-package src-layout

Single-package layout.

## Host integration

### Claude Desktop

JSON `mcpServers` entry specifying command, arguments, and credentials.

## Developer ergonomics

### Linter and type-checker stack

`ruff` + `black` + `mypy` + `pre-commit` as the dev toolchain.

### `pre-commit` framework

Pre-commit hooks shipped with the project.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT licensed.

### Active development

Active project (103 commits); specific last-commit date not surfaced.
