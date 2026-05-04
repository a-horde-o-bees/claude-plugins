# Sample

Mirrors of `https://github.com/designcomputer/mysql_mcp_server`. MySQL MCP server — exposes tables as MCP resources and executes SQL via tools; built-in least-privilege user guidance. 1.2k stars, MIT, default branch `main`. v0.2.2 released April 18, 2025 (date inferred from release).

## Server runtime

### Python with raw MCP SDK

Python (93.2%) on Anthropic's raw `mcp` Python SDK (`mcp>=1.0.0`); not FastMCP. Low-level MCP server API — hand-authored schemas likely. `requires-python = ">=3.11"` floor — likely driven by the MySQL connector or a typing feature.

## Transport

### stdio

Only stdio is documented; README describes the server as a "stdio-based protocol server rather than standalone application" and explicitly frames direct `python ...` invocation as incorrect usage.

### Selection mechanism

Implicit single mode — only stdio is documented; no transport-selection knob.

## Capability surface

### Tools plus resources

Resources expose MySQL tables as listings and table contents readable as resources. Tools expose SQL query execution with error handling. Tables surface as queryable URIs; SQL execution exposed as a separate tool action.

## Configuration delivery

### Environment variables

`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` for connection settings.

## Authentication

### Database connection string

MySQL username/password supplied via env vars. README emphasizes "never commit" credentials and restricting to minimum-permission DB users.

## Multi-tenancy

### Single-user / single-tenant per process

Single database connection per server; no per-request tenancy.

## Distribution channel

### PyPI via pip / pipx

`pip install mysql-mcp-server`; published as `mysql-mcp-server` on PyPI.

### Smithery registry

`npx -y @smithery/cli install mysql-mcp-server --client claude` for Smithery-mediated install.

### PyPI via uvx (zero-install runner)

README host-config snippets show `uvx --from mysql-mcp-server` (VS Code) and `uv --directory /path/to/repo run mysql_mcp_server` (dev).

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`[project.scripts]`: `mysql_mcp_server = "mysql_mcp_server:main"`. README explicitly discourages direct `python ...` invocation, framing the server strictly as an MCP-protocol bridge for hosts.

### `uv --directory` from source

Dev-mode invocation: `uv --directory /path/to/repo run mysql_mcp_server`.

### `uvx <package>`

VS Code host snippet: `uvx --from mysql-mcp-server`.

## Build and packaging

### Hatchling + uv (Python)

Build backend: `hatchling.build`. README uses uv/uvx; `pytest.ini` + `requirements-dev.txt` coexist with pyproject.toml (legacy split — pyproject does not carry dev extras). Lock file not explicitly noted in fetched content.

### Python version pinning

`requires-python = ">=3.11"` declared in pyproject.toml.

## Schema and types

### Hand-authored tool schemas

Low-level MCP SDK use without FastMCP — schemas hand-authored rather than auto-derived. Uses both tool and resource surfaces.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

## Test stack

### pytest with async + coverage

pytest-based via separate `pytest.ini` and `requirements-dev.txt` (legacy split — pyproject.toml does not carry dev extras). `tests/` directory present. pytest-asyncio not confirmed in fetched content.

## CI

### GitHub Actions

`test.yml` badge in README; specific workflow contents not extracted.

## Host integration

### Claude Desktop

`claude_desktop_config.json` example provided.

### VS Code / VS Code Insiders / Visual Studio family

`mcp.json` example provided.

## Repository layout

### Single-package src-layout

Single-package Python — `src/mysql_mcp_server/`, `tests/`, `.github/workflows/`, pyproject.toml.

## Documentation surface

### README as the canonical surface

README baked-in security guidance — least-privilege user, never commit credentials. README also frames "non-direct Python invocation" as a deliberate agent-posture choice.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Tagged release with version in changelog

v0.2.2 released April 18, 2025 (inferred from release).
