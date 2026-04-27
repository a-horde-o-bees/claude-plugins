# Sample

## Identification

### url

https://github.com/awslabs/mcp

### stars

8.8k

### last-commit

Not explicitly dated in fetched view; 1,474 commits on main, actively maintained.

### license

Apache-2.0

### default branch

main

### one-line purpose

AWS Labs MCP monorepo — 40+ per-service MCP servers packaged as namespace-prefixed PyPI packages (`awslabs.*`); preview aggregator bundles SOPs + CloudTrail audit.

## 1. Language and runtime

### language(s) + version constraints

Python. Version constraints not extracted within budget; `pyproject.toml` per server.

### framework/SDK in use

FastMCP (inferred from `FASTMCP_LOG_LEVEL` env var convention).

## 2. Transport

### supported transports

stdio only (per repo notice). SSE was removed on 2025-05-26; "Streamable HTTP" planned replacement is listed as in-development.

### how selected

Not selectable — stdio is the single shipping mode.

## 3. Distribution

### every mechanism observed

PyPI + uvx; Docker images; source install from GitHub. No npm/Homebrew/binary releases noted.

### published package name(s)

`awslabs.<service>-mcp-server` naming convention on PyPI (e.g. `awslabs.aws-documentation-mcp-server`). 40+ servers under this namespace.

### install commands shown in README

`uvx awslabs.aws-documentation-mcp-server@latest` (canonical shown example); Docker variants per-server.

## 4. Entry point / launch

### command(s) users/hosts run

`uvx awslabs.<service>-mcp-server@latest` for most servers; Docker `docker run` variants per server.

### wrapper scripts, launchers, stubs

Per-server entry; no umbrella launcher. `aws-mcp-server` (in preview) positioned as an aggregated entry point.

## 5. Configuration surface

### how config reaches the server

Env-var-centric: `AWS_PROFILE`, `AWS_REGION`, per-service vars (e.g., `BEDROCK_KB_RERANKING_ENABLED`), and `FASTMCP_LOG_LEVEL`. Host config passes these via the host's `env` block.

## 6. Authentication

### flow

AWS standard credential chain — delegates to `AWS_PROFILE`, AWS SSO, instance roles, env credentials via the AWS SDK. No MCP-level auth layer.

### where credentials come from

`~/.aws/credentials`, `~/.aws/config`, env vars, or instance metadata — whatever the AWS SDK chain resolves.

## 7. Multi-tenancy

### tenancy model

Single-user per process; tenancy effectively equals the active AWS profile/region at launch.

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools per service. The preview `AWS MCP Server` additionally bundles "pre-built Agent SOPs" (structured operating procedures) and CloudTrail audit integration.

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

`FASTMCP_LOG_LEVEL` env var; CloudTrail audit logging called out for the preview aggregated server. No tracing/metrics documented at this layer.

## 10. Host integrations shown in README or repo

### Kiro

One-click install button in README.

### Cursor

One-click install button.

### VS Code

One-click install button.

### Cline with Amazon Bedrock

One-click install button.

### Windsurf

One-click install button.

### Claude Code

One-click install button.

### Claude Desktop

Not surfaced as a named integration target in the overview, though stdio JSON snippets are implicit per-server.

## 11. Claude Code plugin wrapper

### presence and shape

Not observed in top-level listing. Host integration is via one-click button text rather than a shipped plugin wrapper.

## 12. Tests

### presence, framework, location, notable patterns

Tests present per-server. Codecov badge present → coverage tracked. Specific framework not extracted.

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions (`.github/workflows`). `.ruff.toml` (lint), `.pre-commit-config.yaml` (hooks), `.secrets.baseline` (secret scan), OSSF Scorecard present.

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile per server (multiple). `.devcontainer/` configuration at root for dev workflow.

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Per-server READMEs; one-click install URLs are the canonical ergonomic path. Devcontainer for contributors.

## 16. Repo layout

### single-package / monorepo / vendored / other

Monorepo. `src/<service>/` directory per server, 40+ servers. Central dev config at repo root.

## 17. Notable structural choices

Wholesale SSE removal with a bridge to future Streamable HTTP — deliberate transport-narrowing rather than maintaining both during transition.

Namespace-prefixed PyPI packages (`awslabs.*`) — prevents collision with other AWS-adjacent packages and makes provenance scannable from the package name alone.

One-click install buttons per host as a primary README surface — shifts the configuration burden from copy-paste JSON to deep links.

Preview-tier "aggregated" server (AWS MCP Server) bundling SOPs — suggests a direction where per-service servers become composable primitives under a curated orchestrator.

## 18. Unanticipated axes observed

Deprecation and removal as a versioning signal: SSE removal dated and documented in-repo rather than behind a changelog.

"Agent SOPs" as a first-class concept shipped alongside tools — not just raw API surface, but opinionated workflows.

One-click install URL protocol — integration surface that bypasses JSON entirely for supported hosts.

## 19. Python-specific

### SDK / framework variant

Dual: raw `mcp>=1.23.0` AND `fastmcp>=3.0.1` (sampled from `src/aws-api-mcp-server/pyproject.toml`). FastMCP 3.x. Import pattern: FastMCP (inferred from `FASTMCP_LOG_LEVEL` env var convention referenced in README).

### Python version floor

Sampled server: `requires-python = ">=3.10"`. Per-server pyproject.toml; likely consistent across the monorepo.

### Packaging

Build backend: `hatchling.build` (sampled server). Lock file presumed `uv.lock` per server or at root (not confirmed). Version manager convention: `uv` — each subdir is its own uv project.

### Entry point

`[project.scripts]`: `"awslabs.aws-api-mcp-server" = "awslabs.aws_api_mcp_server.server:main"` (sampled) — quoted-name script with dot-in-name. Namespace-prefixed: `awslabs.<service>-mcp-server`. README canonical host-config: `"command": "uvx"`, `"args": ["awslabs.<service>-mcp-server@latest"]` + `"env": {"AWS_PROFILE": "..."}`.

### Install workflow expected of end users

`uvx awslabs.<service>-mcp-server@latest` (primary); Docker images per server; from-source via GitHub clone. One-click install buttons per host (Kiro, Cursor, VS Code, Windsurf, Cline, Claude Code).

### Async and tool signatures

pytest-asyncio in dev deps; `asyncio_mode = "auto"` — fully async. Custom `live` marker for API-calling tests.

### Type / schema strategy

FastMCP auto-derived likely; raw `mcp` for lower-level hooks.

### Testing

pytest + pytest-asyncio + pytest-cov + pytest-mock (per-server). `python_files = "test_*.py"`, `python_classes = "Test*"`, `testpaths = ["tests"]`. Codecov badge across repo.

### Dev ergonomics

`.devcontainer/` for contributor onboarding. `.pre-commit-config.yaml`, `.secrets.baseline`, `.ruff.toml` at root. OSSF Scorecard integration.

### Notable Python-specific choices

Monorepo with per-server pyproject.toml — each server is its own uv-managed Python package.

Quoted script name with dots (`"awslabs.aws-api-mcp-server"`) is valid pyproject syntax but rare — enables a dotted console-script name to match the PyPI package name.

Namespace-prefixed PyPI packages (`awslabs.*`) and matching dotted console scripts — structural convention for monorepo-of-packages.

Central dev tooling at root (ruff, pre-commit, secrets-baseline) with per-server pyproject for deps — classic uv workspace layout (though not confirmed as `[tool.uv.workspace]`).

## 20. Gaps

Exact last-commit date — not surfaced in fetched view. Whether any single server opts out of stdio-only (e.g. a hosted variant). Full enumeration of the 40+ servers with domain tags. Whether root pyproject.toml declares `[tool.uv.workspace]` (not inspected).
