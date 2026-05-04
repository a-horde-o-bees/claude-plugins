# Sample

Mirrors of `https://github.com/severity1/terraform-cloud-mcp`. Terraform Cloud MCP server — FastMCP + Pydantic; 50+ tools across account/workspace/run/plan/apply/project/organization/cost-estimation/assessment-results/state-versions/variables; orthogonal `READ_ONLY_TOOLS` and `ENABLE_DELETE_TOOLS` env-flag safety. 23 stars, MIT, default branch `main`. 80 commits on main; specific date not surfaced.

## Server runtime

### Python with FastMCP

Python on FastMCP. FastMCP major/version pin and import pattern not surfaced in extract. async/await throughout the server.

## Transport

### stdio

Standard MCP stdio; no explicit network mode documented.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

50+ tools partitioned across upstream-API domains: account, workspace, run, plan, apply, project, organization, cost estimation, assessment results, state versions, variables. Domain-per-module decomposition matching upstream Terraform Cloud API surface.

### Capability gating flags (per-tool, per-category, write-mode)

Two orthogonal env-driven gates: `READ_ONLY_TOOLS` and `ENABLE_DELETE_TOOLS`. Two-axis safety switching — delete is more dangerous than write and gets its own toggle, distinct from read-only.

## Configuration delivery

### Environment variables

`TFC_TOKEN` (required), `TFC_ADDRESS`, `ENABLE_DELETE_TOOLS`, `READ_ONLY_TOOLS`.

## Authentication

### Static API key / token via env var

Terraform Cloud API token supplied via `TFC_TOKEN` environment variable.

## Multi-tenancy

### Single-user / single-tenant per process

Single API token per process; workspace/organization scope handled per tool call.

## Distribution channel

### PyPI via uvx (zero-install runner)

Local install via `uv` package manager; package name `terraform-cloud-mcp`.

### Docker / OCI image

Docker container build provided.

### SDK CLI installer

`claude mcp add` registration via Claude Code CLI.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `terraform-cloud-mcp`. Host-config snippet shape likely `uv run terraform-cloud-mcp` per README's uv workflow.

## Build and packaging

### Hatchling + uv (Python)

`pyproject.toml` with uv backing; lock file presence implied; version manager convention `uv`.

### Python version pinning

`requires-python` = 3.12+.

## Schema and types

### Pydantic v2 models

Pydantic models for structured data validation.

### FastMCP auto-derivation from type hints

Pydantic-backed schema auto-derivation via FastMCP.

### Async model (cross-cutting)

async/await throughout; asyncio via FastMCP.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile included for containerised deployment.

## CI

### GitHub Actions

GitHub Actions configured.

## Host integration

### Claude Code

`claude mcp add` CLI registration.

### Claude Desktop

JSON `mcpServers` entry.

### Cursor

JSON `mcpServers` entry.

### Per-host README JSON snippets

Per-host JSON config snippets in README, including a Copilot Studio entry.

## Observability

### Env-var-controlled log level

Debug logging "enabled by default" per README; format/destination not surfaced. Likely env-var-controlled (mechanism inferred, not directly observed).

## Repository layout

### Domain-per-module decomposition

Single-package with domain-per-module layout — one module per upstream-API object class (account, workspace, run, plan, apply, project, organization, cost_estimation, assessment_results, state_versions, variables).

## Safety and security posture

### Read-only by default with explicit write flag

`READ_ONLY_TOOLS` env flag toggles read-only mode.

### Destructive-action gating flag

`ENABLE_DELETE_TOOLS` orthogonal flag — delete actions gated separately from read-only/write distinction.

## Developer ergonomics

### Linter and type-checker stack

ruff + black formatters and mypy type checking.

## Documentation surface

### README as the canonical surface

README is the canonical surface.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

80 commits on main; ongoing development.
