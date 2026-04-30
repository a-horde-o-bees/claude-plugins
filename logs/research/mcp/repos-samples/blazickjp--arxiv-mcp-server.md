# Sample

## Identification

### url

https://github.com/blazickjp/arxiv-mcp-server

### stars

~2,600

### last-commit

active (115+ commits)

### license

Apache-2.0

### default branch

main

### one-line purpose

arXiv research MCP server — 6 tools (search, download, read, list, semantic search, citation graph) plus research-workflow prompts; ships MCP + Codex plugin + Claude Code skills in one repo.

## Language and runtime

### language(s) + version constraints

Python 99.2%; Python 3.11+.

### framework/SDK in use

raw `mcp` Python SDK (not FastMCP).

## Transport

### supported transports

stdio (via `uv` / `uvx`).

### how selected

stdio only.

## Distribution

### every mechanism observed

PyPI via `uv tool install`, uvx, Docker, source.

### published package name(s)

`arxiv-mcp-server`; optional `arxiv-mcp-server[pdf]` extra.

### install commands shown in README

`uv tool install arxiv-mcp-server`; `uv tool install 'arxiv-mcp-server[pdf]'`.

## Entry point / launch

### command(s) users/hosts run

`arxiv-mcp-server` console script.

### wrapper scripts, launchers, stubs

none.

## Configuration surface

### how config reaches the server

CLI flags (`--storage-path`) and env vars (`ARXIV_STORAGE_PATH`).

## Authentication

### flow

none.

### where credentials come from

N/A — arXiv public API; rate limit enforced locally (3-second minimum).

## Multi-tenancy

### tenancy model

single-user; local paper storage is per-instance.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

6 tools — search, download, read, list stored, semantic search, citation graph; **prompts** for research analysis and literature review workflows.

## Observability

### logging destination + format, metrics, tracing, debug flags

not surfaced; MCP-standard logging.

## Host integrations shown in README or repo

### Claude Desktop

JSON config with uvx command.

### Codex

`.codex-plugin/` integration manifest in repo root — first-class Codex plugin shape.

### Claude Code

`skills/` directory suggests parallel skill artifacts.

## Claude Code plugin wrapper

### presence and shape

`skills/` directory present — explicit Claude Code skill wrapper co-located.

## Tests

### presence, framework, location, notable patterns

pytest (`python -m pytest`); `tests/` directory.

## CI

### presence, system, triggers, what it runs

GitHub Actions `tests.yml` workflow with badge.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop JSON; uvx-style invocation.

## Repo layout

### single-package / monorepo / vendored / other

single-package (`src/arxiv_mcp_server/`) + `skills/` + `.codex-plugin/`.

## Notable structural choices

Ships integration artifacts for three different host ecosystems in one repo: standard MCP (`src/`), Codex (`.codex-plugin/`), Claude Code skills (`skills/`). Optional `[pdf]` extra — separates core arXiv client from heavier PDF processing deps. Built-in 3-second rate-limit enforcement — reflects arXiv's rate-limit guidance at the client layer.

## Unanticipated axes observed

One server, three host-native plugin wrappers — the MCP server is the core, but Codex and Claude Code each get dedicated sibling integrations rather than expecting hosts to generically consume the MCP surface. "Research prompts" as a shipped artifact (not just tools) — leveraging MCP prompt primitives.

## Python-specific

### SDK / framework variant

raw `mcp` SDK; version pin not surfaced from README; import pattern: `mcp.server`.

### Python version floor

`requires-python` value: `>=3.11`.

### Packaging

build backend not surfaced; lock file: `uv.lock` present; version manager convention: uv.

### Entry point

`[project.scripts]` → `arxiv-mcp-server`; actual console-script name: `arxiv-mcp-server`; host-config snippet shape: `uvx arxiv-mcp-server` or `uv tool install` then `arxiv-mcp-server`.

### Install workflow expected of end users

`uv tool install` (primary), uvx, Docker; one-liner: `uv tool install arxiv-mcp-server`.

### Async and tool signatures

likely async (httpx idiom).

### Type / schema strategy

Pydantic via MCP SDK; schema auto-derived.

### Testing

pytest; fixture style not inspected.

### Dev ergonomics

not surfaced.

### Notable Python-specific choices

Python 3.11+ floor (higher than most MCP servers which target 3.10) — suggests use of newer typing / exception-group features. PDF processing gated behind an extra, not a core dep — install stays slim for users who only need metadata.

## Gaps

Exact `mcp` SDK version pin not read. Contents of `skills/` directory (Claude Code wrapper shape) not inspected. `.codex-plugin/` manifest format not inspected.
