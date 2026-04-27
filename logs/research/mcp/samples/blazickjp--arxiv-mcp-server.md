# Sample

## Identification

### url

https://github.com/blazickjp/arxiv-mcp-server

### stars

~2,600

### last-commit (date or relative)

active (115+ commits)

### license

Apache-2.0

### default branch

main

### one-line purpose

arXiv research MCP server — 6 tools (search, download, read, list, semantic search, citation graph) plus research-workflow prompts; ships MCP + Codex plugin + Claude Code skills in one repo.

## 1. Language and runtime

### language(s) + version constraints

Python 99.2%; Python 3.11+

### framework/SDK in use

raw `mcp` Python SDK (not FastMCP)

### pitfalls observed

  - Exact `mcp` SDK version pin not read

## 2. Transport

### supported transports

stdio (via `uv` / `uvx`)

### how selected

stdio only

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI via `uv tool install`, uvx, Docker, source

### published package name(s)

`arxiv-mcp-server`; optional `arxiv-mcp-server[pdf]` extra

### install commands shown in README

`uv tool install arxiv-mcp-server`; `uv tool install 'arxiv-mcp-server[pdf]'`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`arxiv-mcp-server` console script

### wrapper scripts, launchers, stubs

none

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

CLI flags (`--storage-path`) and env vars (`ARXIV_STORAGE_PATH`)

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

none

### where credentials come from

N/A — arXiv public API; rate limit enforced locally (3-second minimum)

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

single-user; local paper storage is per-instance

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

6 tools — search, download, read, list stored, semantic search, citation graph; **prompts** for research analysis and literature review workflows

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not surfaced; MCP-standard logging

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo
For each host: form + location

### Claude Desktop

JSON config with uvx command

### Codex

**`.codex-plugin/` integration manifest** in repo root — first-class Codex plugin shape

### Claude Code

`skills/` directory suggests parallel skill artifacts

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

`skills/` directory present — explicit Claude Code skill wrapper co-located

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest (`python -m pytest`); `tests/` directory

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions `tests.yml` workflow with badge

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop JSON; uvx-style invocation

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`src/arxiv_mcp_server/`) + `skills/` + `.codex-plugin/`

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Ships integration artifacts for **three** different host ecosystems in one repo: standard MCP (`src/`), Codex (`.codex-plugin/`), Claude Code skills (`skills/`)
- Optional `[pdf]` extra — separates core arXiv client from heavier PDF processing deps
- Built-in 3-second rate-limit enforcement — reflects arXiv's rate-limit guidance at the client layer

## 18. Unanticipated axes observed
- decision dimensions this repo reveals: one server, three host-native plugin wrappers — the MCP server is the core, but Codex and Claude Code each get dedicated sibling integrations rather than expecting hosts to generically consume the MCP surface; "research prompts" as a shipped artifact (not just tools) — leveraging MCP prompt primitives

## 19. Python-specific

### SDK / framework variant
- raw `mcp` Python SDK / FastMCP 1.x / FastMCP 2.x / custom — raw `mcp` SDK
- version pin from pyproject.toml — not surfaced from README
- import pattern observed — `mcp.server`

### Python version floor
- `requires-python` value — `>=3.11`

### Packaging
- build backend — not surfaced
- lock file present — `uv.lock` present
- version manager convention — uv

### Entry point
- `[project.scripts]` console script / `__main__.py` / bare script / other — `[project.scripts]` → `arxiv-mcp-server`
- actual console-script name(s) — `arxiv-mcp-server`
- host-config snippet shape — `uvx arxiv-mcp-server` or `uv tool install` then `arxiv-mcp-server`

### Install workflow expected of end users
- pip / pipx / uv tool install / uvx run / poetry / source clone + venv / Docker / other — `uv tool install` (primary), uvx, Docker
- one-liner the README recommends — `uv tool install arxiv-mcp-server`

### Async and tool signatures
- sync `def` or `async def` — likely async (httpx idiom)

### Type / schema strategy
- Pydantic via MCP SDK
- schema auto-derived

### Testing
- pytest / pytest-asyncio / unittest / none — pytest
- fixture style — not inspected

### Dev ergonomics
- mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other — not surfaced

### Notable Python-specific choices
- Python **3.11+** floor (higher than most MCP servers which target 3.10) — suggests use of newer typing / exception-group features
- PDF processing gated behind an extra, not a core dep — install stays slim for users who only need metadata

## 20. Gaps
- Exact `mcp` SDK version pin not read
- Contents of `skills/` directory (Claude Code wrapper shape) not inspected
- `.codex-plugin/` manifest format not inspected
