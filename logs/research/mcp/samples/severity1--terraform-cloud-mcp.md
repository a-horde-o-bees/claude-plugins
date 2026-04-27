# Sample

## Identification

### url

https://github.com/severity1/terraform-cloud-mcp

### stars

23

### last-commit

active on main (80 commits; specific date not surfaced).

### license

MIT

### default branch

main

### one-line purpose

Terraform Cloud MCP server — FastMCP + Pydantic; dual safety flags (read-only, enable-delete).

## 1. Language and runtime

### language(s) + version constraints

Python; Python 3.12+.

### framework/SDK in use

FastMCP (Python).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (standard MCP protocol).

### how selected

default transport; no explicit network mode documented.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

local install via `uv`, Docker container, Claude Code CLI integration.

### published package name(s)

`terraform-cloud-mcp`.

### install commands shown in README

via `uv` package manager; Docker container; Claude Code CLI `claude mcp add`.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`terraform-cloud-mcp` (console script).

### wrapper scripts, launchers, stubs

Dockerfile for containerized deployment.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Environment variables — `TFC_TOKEN` (required), `TFC_ADDRESS`, `ENABLE_DELETE_TOOLS`, `READ_ONLY_TOOLS`.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Terraform Cloud API token.

### where credentials come from

`TFC_TOKEN` environment variable.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user per process (single API token); workspace/organization scope handled per tool call.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

50+ tools across account, workspace, run, plan, apply, project, organization, cost estimation, assessment results, state versions, variables.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

debug logging enabled by default; format/destination not surfaced.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Code CLI

`claude mcp add` registration.

### Claude Desktop

JSON `mcpServers` entry.

### Cursor

JSON `mcpServers` entry.

### Copilot Studio

JSON `mcpServers` entry.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not observed (standard `claude mcp add` CLI usage, not a plugin marketplace wrapper).

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

not surfaced in fetched content.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions configured.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile included.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

ruff/black formatters and mypy type checking referenced; domain-specific module structure.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package; domain-per-module layout (account, workspace, run, plan, etc.).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Two-dimensional safety gating: `READ_ONLY_TOOLS` + separate `ENABLE_DELETE_TOOLS` rather than a single "write mode" flag. async/await throughout the server; FastMCP + Pydantic for schema.

## 18. Unanticipated axes observed

Orthogonal read-only and enable-delete flags (delete is more dangerous than write and gets its own toggle). Domain-per-module decomposition for a REST-API-wrapping MCP server.

## 19. Python-specific

### SDK / framework variant

FastMCP (specific major not surfaced); version pin and import pattern not surfaced.

### Python version floor

`requires-python` value: 3.12+.

### Packaging

Build backend: pyproject.toml with uv. Lock file presence: implied. Version manager convention: uv.

### Entry point

console script `terraform-cloud-mcp`; host-config snippet shape likely `uv run terraform-cloud-mcp` (README references uv workflow).

### Install workflow expected of end users

uv install; Docker; `claude mcp add`.

### Async and tool signatures

async/await patterns throughout; asyncio via FastMCP.

### Type / schema strategy

Pydantic models for structured data validation; Pydantic-backed auto-derivation via FastMCP.

### Testing

not surfaced; fixture style not surfaced.

### Dev ergonomics

ruff + black + mypy toolchain.

### Notable Python-specific choices

mypy integration suggests stricter typing discipline than most community MCP servers. Two-axis safety switching (`READ_ONLY_TOOLS` and `ENABLE_DELETE_TOOLS`).

## 20. Gaps

Test framework details, exact requires-python pin, logging destination, console script path in pyproject, last-commit date.
