# Sample

Mirrors of `https://github.com/blazickjp/arxiv-mcp-server`. arXiv research MCP server — 6 tools (search, download, read, list, semantic search, citation graph) plus research-workflow prompts; ships MCP + Codex plugin + Claude Code skills in one repo. ~2,600 stars; Apache-2.0; default branch `main`; active (115+ commits).

## Server runtime

### Python with raw MCP SDK

Python (99.2% of repo); raw `mcp` Python SDK (not FastMCP). Import pattern: `mcp.server`. Version pin not surfaced from README. Python 3.11+ floor — higher than most MCP servers which target 3.10, suggesting use of newer typing / exception-group features.

## Transport

### stdio

stdio only (via `uv` / `uvx`).

## Capability surface

### Tools plus prompts (no resources)

6 tools — search, download, read, list stored, semantic search, citation graph — paired with MCP prompts for research analysis and literature review workflows. Research prompts are a shipped artifact (not just tools).

## Configuration delivery

### CLI flags

`--storage-path` flag controls local paper storage location.

### Environment variables

`ARXIV_STORAGE_PATH` env-var equivalent for storage path.

## Authentication

### None / implicit (local-resource gating)

No authentication — arXiv public API; rate limit enforced locally (3-second minimum between requests, reflecting arXiv's published guidance at the client layer).

## Multi-tenancy

### Single-user / single-tenant per process

Single-user; local paper storage is per-instance.

## Distribution channel

### PyPI via uvx (zero-install runner)

`uv tool install arxiv-mcp-server` (primary); also runnable as `uvx arxiv-mcp-server`. PyPI package: `arxiv-mcp-server`. Optional `[pdf]` extra separates core arXiv client from heavier PDF processing dependencies.

### Docker / OCI image

Dockerfile present; Docker image as alternative install path.

### Source clone with editable install

Source install also supported.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` registers `arxiv-mcp-server` console script.

### `uvx <package>`

Host-config snippet shape: `uvx arxiv-mcp-server` or `uv tool install` then `arxiv-mcp-server`.

## Build and packaging

### Hatchling + uv (Python)

Build backend not surfaced explicitly. `uv.lock` committed; version manager convention: uv. `requires-python = ">=3.11"`.

### `uv.lock` committed

Lock file committed for reproducibility.

### Optional-dependency fan-out

`[pdf]` extra for heavier PDF dependencies.

## Schema and types

### Pydantic v2 models

Pydantic via the MCP SDK; schema auto-derived.

### Async model (cross-cutting)

Likely async (httpx idiom).

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

## Test stack

### pytest with async + coverage

pytest (`python -m pytest`); `tests/` directory. Fixture style not inspected.

## CI

### GitHub Actions

GitHub Actions `tests.yml` workflow with badge.

## Repository layout

### Single-package plus sibling host integrations

Single package (`src/arxiv_mcp_server/`) plus sibling directories shipping integrations for non-MCP hosts: `skills/` for Claude Code and `.codex-plugin/` for Codex. Three host-native plugin wrappers in one repo — the MCP server is the core, and Codex and Claude Code each get dedicated sibling integrations rather than expecting hosts to generically consume the MCP surface.

## Host integration

### Claude Desktop

JSON config with uvx command.

### Codex CLI / Copilot CLI / Gemini CLI

`.codex-plugin/` integration manifest in repo root — first-class Codex plugin shape.

### Claude Code

`skills/` directory present — explicit Claude Code skill wrapper co-located with the server.

## Observability

### None / unspecified

Not surfaced; MCP-standard logging.

## Claude Code plugin / skill wrapper

### `.claude/skills/` directory in repo

`skills/` directory in repo carries Claude Code skill definitions alongside the MCP server source. Sibling directory packaging the server as a discoverable Claude Code skill in addition to its MCP surface.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Active development

~2,600 stars; 115+ commits; active maintenance.
