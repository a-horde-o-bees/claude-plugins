# Sample

Mirrors of `https://github.com/awslabs/mcp`. AWS Labs MCP monorepo — 40+ per-service MCP servers packaged as namespace-prefixed PyPI packages (`awslabs.*`); preview aggregator bundles SOPs + CloudTrail audit. 8.8k stars; Apache-2.0; default branch `main`; 1,474 commits on main, actively maintained.

## Server runtime

### Python with both MCP SDK and FastMCP declared

Python; sampled server (`src/aws-api-mcp-server/pyproject.toml`) lists both `mcp>=1.23.0` and `fastmcp>=3.0.1` as dependencies — FastMCP 3.x runs the server surface while raw `mcp` provides developer tooling and lower-level hooks. Import pattern is FastMCP (inferred from `FASTMCP_LOG_LEVEL` env var convention referenced in README). Per-server pyproject.toml; consistency across the monorepo not exhaustively verified.

## Transport

### stdio

stdio is the only shipping transport (per repo notice). SSE was removed on 2025-05-26; "Streamable HTTP" planned replacement is listed as in-development. Not selectable.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools per service. Each sub-server presents a focused tool catalog scoped to its AWS service.

### Bundled "agent SOPs" / vertical skill packs

The preview `AWS MCP Server` (aggregated tier) additionally bundles "pre-built Agent SOPs" (structured operating procedures) alongside the raw tool surface — opinionated workflows shipped as a first-class artifact.

## Configuration delivery

### Environment variables

Env-var-centric: `AWS_PROFILE`, `AWS_REGION`, per-service vars (e.g., `BEDROCK_KB_RERANKING_ENABLED`), `FASTMCP_LOG_LEVEL`. Host config passes these via the host's `env` block.

## Authentication

### Cloud-native identity / credential chain

AWS standard credential chain — `AWS_PROFILE`, AWS SSO, instance roles, env credentials via the AWS SDK. No MCP-level auth layer. Resolves from `~/.aws/credentials`, `~/.aws/config`, env vars, or instance metadata as the SDK chain dictates.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per process; tenancy effectively equals the active AWS profile/region at launch.

## Distribution channel

### PyPI via uvx (zero-install runner)

Primary distribution: `uvx awslabs.<service>-mcp-server@latest`. Namespace-prefixed PyPI packages: `awslabs.<service>-mcp-server` naming convention (e.g., `awslabs.aws-documentation-mcp-server`). 40+ servers under this namespace.

### Docker / OCI image

Per-server Docker images; `docker run` variants documented per-server.

### Source clone with editable install

From-source via GitHub clone for development.

### Pre-built host installer / one-click install URL

One-click install buttons per host: Kiro, Cursor, VS Code, Cline with Amazon Bedrock, Windsurf, Claude Code — shifts configuration burden from copy-paste JSON to deep links.

## Entry point and launch

### `uvx <package>`

Host config: `"command": "uvx"`, `"args": ["awslabs.<service>-mcp-server@latest"]`, plus `"env": {"AWS_PROFILE": "..."}`. Per-server entry; no umbrella launcher (the preview `aws-mcp-server` is positioned as an aggregated entry point).

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `"awslabs.aws-api-mcp-server" = "awslabs.aws_api_mcp_server.server:main"` (sampled) — quoted-name script with dot-in-name lets the dotted console-script name match the dotted PyPI package name.

## Build and packaging

### Hatchling + uv (Python)

Build backend: `hatchling.build` (sampled server). Per-server pyproject.toml; each subdir is its own uv project. Lock file presumed `uv.lock` per server (not confirmed). Sampled `requires-python = ">=3.10"`.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP auto-derived schemas likely throughout; raw `mcp` available for lower-level hooks where needed.

### Async model (cross-cutting)

`pytest-asyncio` in dev deps with `asyncio_mode = "auto"` — fully async. Custom `live` marker for API-calling tests.

## Container artifacts

### Per-server Dockerfile in monorepo

Dockerfile per server (multiple) under each `src/<service>/` directory.

### Devcontainer for contributors

`.devcontainer/` configuration at repo root for contributor onboarding.

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio + pytest-cov + pytest-mock per-server. `python_files = "test_*.py"`, `python_classes = "Test*"`, `testpaths = ["tests"]`. Codecov badge across the repo. Coverage tracked.

## CI

### GitHub Actions

`.github/workflows/` configured. `.ruff.toml` (lint), `.pre-commit-config.yaml` (hooks), `.secrets.baseline` (secret scan), OSSF Scorecard integration.

### Pre-commit hooks

`.pre-commit-config.yaml` enforces local checks before commit.

### Secret-scan baseline

`.secrets.baseline` records known-allowed strings.

### OSSF Scorecard

OSSF Scorecard integration emits a security posture rating.

### Codecov integration

Codecov badge present; coverage tracked via the CI workflow.

## Deployment topology

### Local stdio process per session

Default: stdio child process launched by the MCP host.

## Host integration

### Per-host README JSON snippets

Per-host JSON config documented per sub-server.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Per-host one-click install URLs in README for Kiro, Cursor, VS Code, Cline with Amazon Bedrock, Windsurf, and Claude Code — bypass JSON copy-paste entirely for the supported hosts.

### Claude Code

One-click install button surfaces alongside the per-host buttons; JSON-snippet path implicit per sub-server.

### Cursor

One-click install button in README.

### VS Code / VS Code Insiders / Visual Studio family

One-click install button in README.

## Observability

### Env-var-controlled log level

`FASTMCP_LOG_LEVEL` env var sets log severity at startup.

### CloudTrail audit logging

Audit-tier logging called out for the preview aggregated server (`AWS MCP Server`); CloudTrail captures who called what tool when. No tracing/metrics documented at this layer.

## Repository layout

### Monorepo of namespace-prefixed packages

Many sub-packages under `src/<service>/` each with their own `pyproject.toml`, all sharing the `awslabs.*` namespace prefix. Central dev tooling at root (ruff, pre-commit, secrets baseline). Each sub-package independently published and installable via uvx. Approximately 40+ servers under this namespace.

## Developer ergonomics

### Devcontainer / mise / dev-environment manifests

`.devcontainer/` for contributor onboarding.

### Linter and type-checker stack

`.ruff.toml` at root; ruff configured as primary linter.

### `pre-commit` framework

`.pre-commit-config.yaml` orchestrates lint/format/secret-scan hooks at commit time.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No top-level Claude Code wrapper observed; integration via one-click install button text rather than a shipped plugin wrapper.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Dated deprecation in repo

SSE removal documented in-repo with a date (2025-05-26) — wholesale transport removal with a documented bridge to future Streamable HTTP, signaled clearly to consumers.

### Active development

8.8k stars; 1,474 commits on main; ongoing maintenance.
