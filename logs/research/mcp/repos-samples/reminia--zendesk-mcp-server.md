# Sample

Mirrors of `https://github.com/reminia/zendesk-mcp-server`. Zendesk MCP server — knowledge base exposed via MCP resources primitive alongside ticket/CRM tools. 83 stars, Apache-2.0, default branch `main`.

## Server runtime

### Python with raw MCP SDK

Python 97.3%; `requires-python = ">=3.12"`; raw `mcp>=1.1.2` (no `[cli]` extra, no fastmcp). pyproject pins `mcp>=1.1.2`, `python-dotenv>=1.0.1`, `zenpy>=2.0.56`. Import likely `from mcp.server import Server` directly. `zenpy` is sync — likely sync handlers. 3-deps runtime stack — remarkably small.

## Transport

### stdio

stdio is the default for Claude Desktop integration.

### Selection mechanism

Implicit single mode — stdio default; whether streamable-http is supported via any flag is not documented.

## Capability surface

### Tools plus resources

Tools: `get_tickets`, `get_ticket`, `get_ticket_comments`, `create_ticket_comment`, `create_ticket`, `update_ticket`. Resources: `zendesk://knowledge-base` — explicitly uses the MCP resources primitive for the knowledge base while keeping ticket read/write operations on the tools surface. Read-only knowledge-base content rides on resources; mutating ticket operations ride on tools.

## Configuration delivery

### Dotenv file

`.env` file with credentials defined; `.env.example` shipped in repo; `python-dotenv` dependency picks it up.

### Host-side JSON config snippet

Claude Desktop config uses `uv --directory /abs/path run zendesk` invocation pattern.

## Authentication

### Service-specific credentials via third-party SDK

Zendesk API credentials handed to `zenpy` library (community Python SDK for Zendesk) — not direct REST. zenpy supports API token or username/password. Suggests a family of servers that simply wrap an existing community SDK.

## Multi-tenancy

### Single-user / single-tenant per process

Single Zendesk subdomain per instance.

## Distribution channel

### Source clone with editable install

`git clone ... && uv venv && uv pip install -e .` is the only documented install path. No PyPI release — editable install workflow is the expected user path; the "developer-mode-as-release" pattern.

### Docker / OCI image

Dockerfile in repo; installs from `requirements.lock` inside the image — lock-file-driven container reproducibility.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

console script `zendesk` → `zendesk_mcp_server:main`. Console script name is minimal (`zendesk`) rather than the longer convention of including the `-mcp-server` suffix in the binary name.

### `uv --directory` from source

Host-config invocation: `uv --directory /path/to/zendesk-mcp-server run zendesk`.

## Build and packaging

### Hatchling + uv (Python)

Build backend: hatchling. Version manager convention: `uv`.

### `requirements.lock` committed

`requirements.lock` file used in Docker build — lock file as the build contract for Docker, not pyproject-only; reproducible builds via lockfile.


## Schema and types

### Hand-authored tool schemas

Raw `mcp` SDK handlers typically take dicts; type/schema strategy not directly captured.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile installs from `requirements.lock`.

## Test stack

### No tests / not surfaced

tests/ directory likely present but not captured; no test framework declared in dev deps.

## CI

### GitHub Actions

GitHub Actions present (CI badge visible); specific workflows not captured.

## Host integration

### Claude Desktop

`uv --directory` invocation pattern shown for `claude_desktop_config.json`.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

None observed.

## Documentation surface

### README as the canonical surface

README is canonical; `.env.example` ships as dev-config template.

## Repository layout

### Single-package source (language-conventional)

single-package (`zendesk_mcp_server/`).

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.
