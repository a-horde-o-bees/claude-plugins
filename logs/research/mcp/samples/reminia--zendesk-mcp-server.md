# Sample

## Identification

### url

https://github.com/reminia/zendesk-mcp-server

### stars

83

### last-commit

not captured

### license

Apache-2.0

### default branch

main

### one-line purpose

Zendesk MCP server — knowledge base exposed via MCP resources primitive alongside ticket/CRM tools.

## 1. Language and runtime

### language(s) + version constraints

Python 97.3%; `requires-python = ">=3.12"`.

### framework/SDK in use

raw `mcp>=1.1.2` (no `[cli]` extra).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (standard for Claude Desktop integration); Docker containerization supported.

### how selected

default

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

clone + `uv venv && uv pip install -e .`; Docker (Dockerfile in repo, installs from `requirements.lock`); no PyPI publication mentioned.

### published package name(s)

not published to PyPI (editable install path only).

### install commands shown in README

`uv venv && uv pip install -e .`.

### pitfalls observed

No PyPI release — editable install workflow is the expected user path. Editable-install-only distribution — no PyPI, expected to be cloned; the "developer-mode-as-release" pattern.

## 4. Entry point / launch

### command(s) users/hosts run

`uv --directory /path/to/zendesk-mcp-server run zendesk`.

### wrapper scripts, launchers, stubs

console script `zendesk` → `zendesk_mcp_server:main`.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

`.env` file — credentials defined in `.env.example` (`python-dotenv` dependency).

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Zendesk API credentials via `zenpy` library (API token or username/password).

### where credentials come from

`.env` file picked up by `python-dotenv`.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single Zendesk subdomain per instance.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools: `get_tickets`, `get_ticket`, `get_ticket_comments`, `create_ticket_comment`, `create_ticket`, `update_ticket`. Resources: `zendesk://knowledge-base` — explicitly uses MCP resources primitive.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not captured

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

`uv --directory` invocation pattern shown.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

tests/ directory likely present but not captured.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions present (CI badge visible).

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile; installs from `requirements.lock` inside the image.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`.env.example`.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`zendesk_mcp_server/`).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Uses `zenpy` (community Python SDK for Zendesk) — not direct REST; leverages a mature third-party library. Resources primitive used for knowledge-base access — one of the clearer uses of MCP resources rather than overloading tools for read access. `requirements.lock` file used in Docker build — lock-file-driven container reproducibility. Console script name is minimal (`zendesk`) — unusually short for an MCP server, but unambiguous in the context. No PyPI release — editable install workflow is the expected user path.

## 18. Unanticipated axes observed

Third-party SaaS SDK as the dependency backbone — `zenpy` rather than a direct REST client; suggests a family of servers that simply wrap an existing community SDK. Lock file as the build contract for Docker — not pyproject-only; reproducible builds via lockfile. Explicit use of MCP resources for KB read access — most servers use tools for everything; this one splits read/write across resources/tools. Editable-install-only distribution — no PyPI, expected to be cloned; the "developer-mode-as-release" pattern.

## 19. Python-specific

### SDK / framework variant

raw `mcp>=1.1.2` (no `[cli]`, no `fastmcp`); pyproject pins `mcp>=1.1.2`, `python-dotenv>=1.0.1`, `zenpy>=2.0.56`; import likely `from mcp.server import Server` directly.

### Python version floor

`requires-python` value: `>=3.12`.

### Packaging

Build backend: hatchling. Lock file: `requirements.lock` (used by Dockerfile). Version manager convention: `uv`.

### Entry point

console script `zendesk`; host-config snippet shape `uv --directory /abs/path run zendesk`.

### Install workflow expected of end users

`uv venv && uv pip install -e .`.

### Async and tool signatures

`zenpy` is sync — likely sync handlers.

### Type / schema strategy

not captured; raw `mcp` SDK handlers typically take dicts.

### Testing

not captured in dev deps.

### Dev ergonomics

`.env.example` as dev-config template.

### Notable Python-specific choices

3-deps runtime stack — remarkably small. Python 3.12 floor — newer than typical but less aggressive than hass-mcp's 3.13.

## 20. Gaps

Exact pyproject license field, test framework presence, complete tool count, whether streamable-http transport is supported via any flag.
