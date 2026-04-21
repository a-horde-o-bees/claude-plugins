# PagerDuty/pagerduty-mcp-server

## Identification
- url: https://github.com/PagerDuty/pagerduty-mcp-server
- stars: 62
- last-commit (date or relative): active on main (288 commits; specific date not surfaced)
- license: Apache-2.0
- default branch: main
- one-line purpose: PagerDuty incident-management MCP server — 65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, and change events.

## 1. Language and runtime
- language(s) + version constraints: Python; version pinned via `.tool-versions` (asdf)
- framework/SDK in use: raw MCP Python SDK (not FastMCP per README)
- pitfalls observed:
  - what couldn't be determined: exact Python version pin, async-vs-sync tool patterns, console script name, last-commit date, test framework details

## 2. Transport
- supported transports: stdio
- how selected: default; Dockerfile exposes stdio transport
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: PyPI (uvx), local dev via uv, Docker
- published package name(s): pagerduty-mcp (per uvx invocation)
- install commands shown in README: `uvx pagerduty-mcp`; `uv sync`; Docker
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `python -m pagerduty_mcp` (module entry)
- wrapper scripts, launchers, stubs: Dockerfile; uv dev workflow
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: environment variables — `PAGERDUTY_USER_API_KEY`, `PAGERDUTY_API_HOST`; CLI flag `--enable-write-tools`
- pitfalls observed:
  - read-only-by-default — write tools gated behind `--enable-write-tools` CLI flag

## 6. Authentication
- flow: PagerDuty User API Token
- where credentials come from: `PAGERDUTY_USER_API_KEY` env; token obtained via PagerDuty account settings → API Access
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: single-user per process (one user token)
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, change events
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: not explicitly detailed
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location
- Claude Desktop: JSON `mcpServers` entry with `env` block for API key + API host
- Other MCP-enabled clients: JSON `mcpServers` entry (generic)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: not observed
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: `tests/` directory present; Bedrock test result files referenced
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions (`.github/`)
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile with stdio transport
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `scripts/` directory; `website/` directory (likely docs site)
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: single package under `pagerduty_mcp/`; `tests/`, `scripts/`, `website/`, `.github/`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- read-only-by-default — write tools gated behind `--enable-write-tools` CLI flag
- both Poetry (`poetry.lock` present) and uv workflows supported
- ships a docs website alongside the server
- Bedrock test result files suggest validation against Amazon Bedrock agents

## 18. Unanticipated axes observed
- decision dimensions this repo reveals:
    - dual packaging workflow support (Poetry + uv) in one repo
    - cross-platform agent validation (Bedrock test artifacts)
    - vendor-authored, Apache-licensed rather than individual-maintainer MIT

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / custom: raw MCP Python SDK
- version pin from pyproject.toml: not surfaced
- import pattern observed: not surfaced

### Python version floor
- `requires-python` value: via `.tool-versions`; specific value not surfaced

### Packaging
- build backend: Poetry (poetry.lock present); pyproject.toml also supports uv workflow
- lock file present: poetry.lock
- version manager convention: asdf (`.tool-versions`)

### Entry point
- `[project.scripts]` console script / `__main__.py` module / bare script / other: `__main__.py` module (`python -m pagerduty_mcp`)
- actual console-script name(s): not surfaced (pyproject scripts not shown)
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path): `uvx pagerduty-mcp`

### Install workflow expected of end users
- install form + one-liner from README: `uvx pagerduty-mcp`

### Async and tool signatures
- sync `def` or `async def`: not explicitly specified
- asyncio/anyio usage: not surfaced

### Type / schema strategy
- Pydantic / dataclasses / TypedDict / raw dict / Annotated: Python type hints assumed; specifics not surfaced
- schema auto-derived vs hand-authored: not surfaced

### Testing
- pytest / pytest-asyncio / unittest / none: not surfaced explicitly; tests directory present
- fixture style: not surfaced

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: `scripts/` directory

### Notable Python-specific choices
- open bullets:
    - asdf-based Python version pinning is rarer than uv-native or `.python-version`
    - vendor-maintained (official PagerDuty repo), giving long-term maintenance signal

## 20. Gaps
- what couldn't be determined: exact Python version pin, async-vs-sync tool patterns, console script name, last-commit date, test framework details
