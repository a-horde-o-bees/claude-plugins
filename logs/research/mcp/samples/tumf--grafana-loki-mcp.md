# Sample

## Identification

### url

https://github.com/tumf/grafana-loki-mcp

### stars

25

### last-commit

active (103 commits; specific date not surfaced)

### license

MIT

### default branch

main

### one-line purpose

Grafana Loki log-query MCP server — multi-format output (text/JSON/markdown) for LogQL queries.

## 1. Language and runtime

### language(s) + version constraints

Python 93.2%; Python 3.10+.

### framework/SDK in use

FastMCP.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio, SSE.

### how selected

CLI flag / default.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (pip), uvx, editable dev install via `uv pip install -e ".[dev]"`.

### published package name(s)

grafana-loki-mcp.

### install commands shown in README

`pip install grafana-loki-mcp`; `uvx grafana-loki-mcp`.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`grafana-loki-mcp` with `-u <url>` and `-k <api-key>` flags.

### wrapper scripts, launchers, stubs

pre-commit hooks configured.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

environment variables `GRAFANA_URL` and `GRAFANA_API_KEY`, or CLI flags `-u` and `-k`.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Grafana API key.

### where credentials come from

`GRAFANA_API_KEY` env or `-k` CLI arg.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user per process (one Grafana instance / API key).

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Loki log querying via Grafana API; label name/value retrieval; time-range-configurable log retrieval; multi-format output (text, JSON, markdown).

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not surfaced

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop / MCP clients

JSON `mcpServers` entry specifying command, arguments, credentials.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not observed

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest with coverage reporting.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions workflows + pre-commit hooks.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

no Docker support mentioned.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

ruff + black + mypy toolchain; pre-commit hooks.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single package.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Takes Grafana's Loki API as an intermediary rather than Loki directly, making the MCP server usable for anyone with Grafana Cloud or a Grafana-fronted Loki without dealing with Loki auth separately.

Multi-format output (text / JSON / markdown) for log results — rarer among MCP servers.

Accepts both CLI flags and env vars for URL/API-key, which keeps stdio-launch config flexible.

## 18. Unanticipated axes observed

Output format as a tool parameter (text/JSON/markdown) — a documentation/UX dimension most MCP servers skip.

Grafana-as-proxy architecture for Loki access (piggybacks on existing auth).

## 19. Python-specific

### SDK / framework variant

FastMCP (major version not surfaced). Version pin from pyproject.toml not surfaced. Import pattern not surfaced.

### Python version floor

`requires-python` value: 3.10+.

### Packaging

build backend: pyproject.toml (setup.py also present per README). Lock file: not surfaced. Version manager convention: uv + pip compatible.

### Entry point

console script `grafana-loki-mcp`. Host-config snippet shape: `uvx grafana-loki-mcp -u ... -k ...`.

### Install workflow expected of end users

`pip install grafana-loki-mcp` or `uvx grafana-loki-mcp`.

### Async and tool signatures

async-capable via FastMCP; FastMCP default for asyncio/anyio.

### Type / schema strategy

mypy-checked; Pydantic assumed via FastMCP. Schema auto-derived via FastMCP.

### Testing

pytest with coverage. Fixture style not surfaced.

### Dev ergonomics

ruff + black + mypy + pre-commit.

### Notable Python-specific choices

pre-commit hook configuration shipped alongside tool — discipline-first repo. Coverage reporting in pytest config.

## 20. Gaps

what couldn't be determined: FastMCP major version pin, exact async patterns, logging destination, last-commit date, Docker support (absent per README).
