# Sample

## Identification

### url

https://github.com/PagerDuty/pagerduty-mcp-server

### stars

62

### last-commit

active on main (288 commits; specific date not surfaced)

### license

Apache-2.0

### default branch

main

### one-line purpose

PagerDuty incident-management MCP server — 65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, and change events.

## 1. Language and runtime

### language(s) + version constraints

Python; version pinned via `.tool-versions` (asdf).

### framework/SDK in use

raw MCP Python SDK (not FastMCP per README).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio

### how selected

default; Dockerfile exposes stdio transport.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (uvx), local dev via uv, Docker.

### published package name(s)

pagerduty-mcp (per uvx invocation).

### install commands shown in README

`uvx pagerduty-mcp`; `uv sync`; Docker.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`python -m pagerduty_mcp` (module entry).

### wrapper scripts, launchers, stubs

Dockerfile; uv dev workflow.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Environment variables — `PAGERDUTY_USER_API_KEY`, `PAGERDUTY_API_HOST`; CLI flag `--enable-write-tools`.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

PagerDuty User API Token.

### where credentials come from

`PAGERDUTY_USER_API_KEY` env; token obtained via PagerDuty account settings → API Access.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user per process (one user token).

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, change events.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Not explicitly detailed.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON `mcpServers` entry with `env` block for API key + API host.

### Other MCP-enabled clients

JSON `mcpServers` entry (generic).

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not observed.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

`tests/` directory present; Bedrock test result files referenced.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions (`.github/`).

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile with stdio transport.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`scripts/` directory; `website/` directory (likely docs site).

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single package under `pagerduty_mcp/`; `tests/`, `scripts/`, `website/`, `.github/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Read-only-by-default — write tools gated behind `--enable-write-tools` CLI flag. Both Poetry (`poetry.lock` present) and uv workflows supported. Ships a docs website alongside the server. Bedrock test result files suggest validation against Amazon Bedrock agents.

## 18. Unanticipated axes observed

Decision dimensions this repo reveals: dual packaging workflow support (Poetry + uv) in one repo; cross-platform agent validation (Bedrock test artifacts); vendor-authored, Apache-licensed rather than individual-maintainer MIT.

## 19. Python-specific

### SDK / framework variant

raw MCP Python SDK. Version pin from pyproject.toml not surfaced. Import pattern not surfaced.

### Python version floor

via `.tool-versions`; specific value not surfaced.

### Packaging

Build backend: Poetry (poetry.lock present); pyproject.toml also supports uv workflow. Lock file: poetry.lock. Version manager convention: asdf (`.tool-versions`).

### Entry point

`__main__.py` module (`python -m pagerduty_mcp`). Console-script names not surfaced (pyproject scripts not shown). Host-config snippet shape: `uvx pagerduty-mcp`.

### Install workflow expected of end users

`uvx pagerduty-mcp`.

### Async and tool signatures

Not explicitly specified. asyncio/anyio usage not surfaced.

### Type / schema strategy

Python type hints assumed; specifics not surfaced. Schema auto-derived vs hand-authored not surfaced.

### Testing

Not surfaced explicitly; tests directory present. Fixture style not surfaced.

### Dev ergonomics

`scripts/` directory.

### Notable Python-specific choices

asdf-based Python version pinning is rarer than uv-native or `.python-version`. Vendor-maintained (official PagerDuty repo), giving long-term maintenance signal.

## 20. Gaps

What couldn't be determined: exact Python version pin, async-vs-sync tool patterns, console script name, last-commit date, test framework details.
