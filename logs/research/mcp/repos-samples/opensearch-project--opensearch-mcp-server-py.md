# Sample

## Identification

### url

https://github.com/opensearch-project/opensearch-mcp-server-py

### stars

120

### last-commit

March 24, 2026 (v0.9.0)

### license

Apache-2.0

### default branch

main

### one-line purpose

OpenSearch MCP server — YAML config, category-based tool gating; project-governed (not vendor-authored).

## Language and runtime

### language(s) + version constraints

Python 100%; version not explicitly surfaced.

### framework/SDK in use

Raw MCP Python SDK (Anthropic's Claude Agent SDK reference).

## Transport

### supported transports

stdio, SSE, streamable-http.

### how selected

CLI / config choice.

## Distribution

### every mechanism observed

PyPI via pip.

### published package name(s)

`opensearch-mcp-server-py`

### install commands shown in README

`pip install opensearch-mcp-server-py`

## Entry point / launch

### command(s) users/hosts run

Console script (name inferred but not surfaced).

### wrapper scripts, launchers, stubs

Not surfaced.

## Configuration surface

### how config reaches the server

YAML config file (`example_config.yml` present) plus environment variables `OPENSEARCH_DISABLED_CATEGORIES` and `OPENSEARCH_ENABLED_CATEGORIES` for tool filtering; CLI arguments for further customization.

## Authentication

### flow

Basic auth, IAM roles (for AWS OpenSearch Service), header-based auth, mTLS.

### where credentials come from

Config file or environment.

## Multi-tenancy

### tenancy model

Single-user per process; multiple auth schemes for different deployment targets.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

40+ tools — 9 core (enabled by default), 10 additional analysis (disabled by default), 21 Search Relevance Workbench (under `search_relevance` category), 2 Skills tools.

## Observability

### logging destination + format, metrics, tracing, debug flags

Configuration available; specifics not surfaced.

## Host integrations shown in README or repo

### Claude Desktop

JSON `mcpServers` entry.

### LangChain

Integration supported (per README).

## Claude Code plugin wrapper

### presence and shape

Not observed.

## Tests

### presence, framework, location, notable patterns

`tests/` and `integration_tests/` directories present.

## CI

### presence, system, triggers, what it runs

GitHub Actions (`.github/`).

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

No Dockerfile in repo (notable absence).

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`example_config.yml`, `DEVELOPER_GUIDE.md`, `USER_GUIDE.md`.

## Repo layout

### single-package / monorepo / vendored / other

Single package under `src/`; separate `tests/` and `integration_tests/`; `docs/`.

## Notable structural choices

YAML config file as primary configuration surface (rarer than env-var-only in the MCP ecosystem). Category-based enable/disable tool gating via env vars — lets operators prune the 40-tool surface to just the core 9. Multiple auth schemes (basic, IAM, header, mTLS) in one binary — covers self-hosted, managed AWS, and mutual-TLS deployments. Separate `integration_tests/` directory distinct from unit `tests/` — suggests against-real-OpenSearch validation.

## Unanticipated axes observed

Enabled vs disabled tool categories as the capability-gating unit (category-level on/off, not per-tool). YAML-first configuration rather than env-var-first. Vendor/project-maintained Apache-licensed server with formal docs split (DEVELOPER_GUIDE + USER_GUIDE).

## Python-specific

### SDK / framework variant

Raw MCP Python SDK. Version pin from `pyproject.toml`: not surfaced. Import pattern observed: not surfaced.

### Python version floor

`requires-python` value: not surfaced.

### Packaging

Build backend: `pyproject.toml` with uv (`uv.lock` present). Lock file present: `uv.lock`. Version manager convention: uv.

### Entry point

Inferred console script. Actual console-script name(s): not surfaced in README excerpt. Host-config snippet shape: not surfaced.

### Install workflow expected of end users

`pip install opensearch-mcp-server-py`

### Async and tool signatures

Not surfaced.

### Type / schema strategy

Modern Python type hints inferred. Schema auto-derived vs hand-authored: not surfaced.

### Testing

`tests/` directory present; framework not surfaced. Fixture style: not surfaced.

### Dev ergonomics

`DEVELOPER_GUIDE.md`.

### Notable Python-specific choices

Project-governed (OpenSearch project) Python MCP server — contrasts with community single-maintainer repos. `uv.lock` committed alongside pyproject for reproducible dev envs. No Dockerfile suggests the project expects pip/uv-based installs over container distribution.

## Gaps

Exact console-script name, `requires-python` pin, async/sync behavior, test framework, last-commit date before v0.9.0, Dockerfile existence (notable if absent).
