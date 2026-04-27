# Sample

## Identification

### url

https://github.com/opensearch-project/opensearch-mcp-server-py

### stars

120

### last-commit (date or relative)

March 24, 2026 (v0.9.0)

### license

Apache-2.0

### default branch

main

### one-line purpose

OpenSearch MCP server — YAML config, category-based tool gating; project-governed (not vendor-authored).

## 1. Language and runtime

### language(s) + version constraints

Python 100%; version not explicitly surfaced

### framework/SDK in use

raw MCP Python SDK (Anthropic's Claude Agent SDK reference)

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio, SSE, streamable-http

### how selected

CLI / config choice

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI via pip

### published package name(s)

opensearch-mcp-server-py

### install commands shown in README

`pip install opensearch-mcp-server-py`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

console script (name inferred but not surfaced)

### wrapper scripts, launchers, stubs

not surfaced

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

YAML config file (`example_config.yml` present) plus environment variables `OPENSEARCH_DISABLED_CATEGORIES` and `OPENSEARCH_ENABLED_CATEGORIES` for tool filtering; CLI arguments for further customization

### pitfalls observed

- YAML config file as primary configuration surface (rarer than env-var-only in the MCP ecosystem)
- category-based enable/disable tool gating via env vars — lets operators prune the 40-tool surface to just the core 9

## 6. Authentication

### flow

basic auth, IAM roles (for AWS OpenSearch Service), header-based auth, mTLS

### where credentials come from

config file or environment

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

single-user per process; multiple auth schemes for different deployment targets

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

40+ tools — 9 core (enabled by default), 10 additional analysis (disabled by default), 21 Search Relevance Workbench (under `search_relevance` category), 2 Skills tools

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

configuration available; specifics not surfaced

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

For each host: form + location

### Claude Desktop

JSON `mcpServers` entry

### LangChain

integration supported (per README)

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not observed

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

`tests/` and `integration_tests/` directories present

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions (`.github/`)

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

no Dockerfile in repo (notable absence)

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`example_config.yml`, `DEVELOPER_GUIDE.md`, `USER_GUIDE.md`

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single package under `src/`; separate `tests/` and `integration_tests/`; `docs/`

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

- YAML config file as primary configuration surface (rarer than env-var-only in the MCP ecosystem)
- category-based enable/disable tool gating via env vars — lets operators prune the 40-tool surface to just the core 9
- multiple auth schemes (basic, IAM, header, mTLS) in one binary — covers self-hosted, managed AWS, and mutual-TLS deployments
- separate `integration_tests/` directory distinct from unit `tests/` — suggests against-real-OpenSearch validation

## 18. Unanticipated axes observed

decision dimensions this repo reveals:

- enabled vs disabled tool categories as the capability-gating unit (category-level on/off, not per-tool)
- YAML-first configuration rather than env-var-first
- vendor/project-maintained Apache-licensed server with formal docs split (DEVELOPER_GUIDE + USER_GUIDE)

## 19. Python-specific

### SDK / framework variant

- raw `mcp` Python SDK / FastMCP 1.x (via `mcp.server.fastmcp`) / FastMCP 2.x (via `fastmcp` package) / custom: raw MCP Python SDK
- version pin from pyproject.toml: not surfaced
- import pattern observed: not surfaced

### Python version floor

`requires-python` value: not surfaced

### Packaging

- build backend: pyproject.toml with uv (uv.lock present)
- lock file present: uv.lock
- version manager convention: uv

### Entry point

- `[project.scripts]` console script / `__main__.py` module / bare script / other: inferred console script
- actual console-script name(s): not surfaced in README excerpt
- host-config snippet shape (uvx / uv run / pipx / python -m / absolute venv path): not surfaced

### Install workflow expected of end users

install form + one-liner from README: `pip install opensearch-mcp-server-py`

### Async and tool signatures

- sync `def` or `async def`: not surfaced
- asyncio/anyio usage: not surfaced

### Type / schema strategy

- Pydantic / dataclasses / TypedDict / raw dict / Annotated: modern Python type hints inferred
- schema auto-derived vs hand-authored: not surfaced

### Testing

- pytest / pytest-asyncio / unittest / none: tests directory present; framework not surfaced
- fixture style: not surfaced

### Dev ergonomics

mcp dev / fastmcp dev / Inspector launcher / Makefile / Justfile / other: DEVELOPER_GUIDE.md

### Notable Python-specific choices

open bullets:

- project-governed (OpenSearch project) Python MCP server — contrasts with community single-maintainer repos
- uv.lock committed alongside pyproject for reproducible dev envs
- no Dockerfile suggests the project expects pip/uv-based installs over container distribution

## 20. Gaps

what couldn't be determined: exact console-script name, requires-python pin, async/sync behavior, test framework, last-commit date before v0.9.0, Dockerfile existence (notable if absent)
