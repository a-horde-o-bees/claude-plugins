# Sample

Mirrors of `https://github.com/opensearch-project/opensearch-mcp-server-py`. OpenSearch MCP server — YAML config, category-based tool gating; project-governed (not vendor-authored). 120 stars, Apache-2.0, default branch `main`, last commit March 24, 2026 (v0.9.0).

## Server runtime

### Python with raw MCP SDK

Python 100% on the raw MCP Python SDK (Anthropic's Claude Agent SDK reference). Python version floor not surfaced in extract. `pyproject.toml` with uv (`uv.lock` present).

## Transport

### stdio

stdio supported.

### SSE (Server-Sent Events)

SSE supported.

### Streamable HTTP

Streamable HTTP supported.

### Selection mechanism

CLI / config-file choice between stdio, SSE, and streamable HTTP.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

40+ tools — 9 core (enabled by default), 10 additional analysis (disabled by default), 21 Search Relevance Workbench (under `search_relevance` category), 2 Skills tools.

### Capability gating flags (per-tool, per-category, write-mode)

Category-based enable/disable tool gating via `OPENSEARCH_DISABLED_CATEGORIES` and `OPENSEARCH_ENABLED_CATEGORIES` env vars. Lets operators prune the 40-tool surface to just the core 9.

## Configuration delivery

### YAML manifest (declarative tool authoring)

YAML config file (`example_config.yml` shipped in repo) is the primary configuration surface.

### Environment variables

`OPENSEARCH_DISABLED_CATEGORIES` and `OPENSEARCH_ENABLED_CATEGORIES` for tool filtering layered on top of the YAML config.

### CLI flags

CLI arguments for further customization beyond the config file.

## Authentication

### Multi-scheme upstream auth (basic / IAM / header / mTLS)

Multiple auth schemes in one binary — basic auth, IAM roles (for AWS OpenSearch Service), header-based auth, mTLS. Covers self-hosted, managed AWS, and mutual-TLS deployments from the same server.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per process; multiple auth schemes select the deployment target rather than partition tenants.

## Distribution channel

### PyPI via pip / pipx

`pip install opensearch-mcp-server-py` — package name `opensearch-mcp-server-py`.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script registered via `[project.scripts]`; actual script name not surfaced in extract.

## Build and packaging

### Hatchling + uv (Python)

Build backend `pyproject.toml` with `uv`; `uv.lock` committed alongside `pyproject.toml` for reproducible dev envs.

### `uv.lock` committed

`uv.lock` present in the repo.

## Container artifacts

### No container artifacts

No Dockerfile in repo; the project distributes via pip/uv-based installs.

## Test stack

### pytest with async + coverage

`tests/` directory present; framework not surfaced in extract.

### Separate integration_tests/ directory

`tests/` and `integration_tests/` distinct directories — integration tests likely run against a real OpenSearch instance.

## CI

### GitHub Actions

GitHub Actions workflows in `.github/`.

## Host integration

### Claude Desktop

JSON `mcpServers` entry.

### LangChain integration

LangChain integration supported per README.

## Repository layout

### Single-package src-layout

Single package under `src/`; separate `tests/` and `integration_tests/` directories; `docs/` directory.

## Documentation surface

### Split USER_GUIDE / DEVELOPER_GUIDE

Formal docs split — `DEVELOPER_GUIDE.md` and `USER_GUIDE.md` shipped alongside README, with operator-facing config files (`example_config.yml`) as a deliverable artifact.

### README as the canonical surface

README is supplemented by USER_GUIDE / DEVELOPER_GUIDE.

## Developer ergonomics

### Sample MCP client configs in repo

`example_config.yml` shipped as a reference YAML config for operators.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin/` or `.claude/skills/` wrapper observed.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Tagged release with version in changelog

v0.9.0 released March 24, 2026.

### Active development

Active development — recent v0.9.0 release.
