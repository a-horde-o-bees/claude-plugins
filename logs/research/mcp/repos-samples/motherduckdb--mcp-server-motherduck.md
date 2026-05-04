# Sample

Mirrors of `https://github.com/motherduckdb/mcp-server-motherduck`. MotherDuck/DuckDB MCP server — query MotherDuck cloud and local DuckDB from one binary, with optional S3 access. 468 stars, MIT, default branch `main`, last commit March 30, 2026 (v1.0.4).

## Server runtime

### Python with FastMCP

Python (>=3.10) on FastMCP 2.x — `fastmcp>=2.14,<3` pinned in `pyproject.toml`. Anthropic MCP SDK also declared. FastMCP auto-derives schemas from type hints. FastMCP 2.14 typically supports both sync and async tool signatures; `pytest-asyncio>=0.24` in dev deps confirms async test surface.

## Transport

### stdio

Default transport for Claude Desktop / VS Code style hosts.

### Streamable HTTP

HTTP transport supported; selection via client-specific configuration.

### Selection mechanism

Configured via client-specific settings (Claude Desktop, VS Code, etc.) rather than a CLI flag.

## Capability surface

### Domain-bundled tool set

SQL query execution (read/write modes), database listing, table listing, column inspection, database switching. Supports local files, S3, MotherDuck cloud, and in-memory databases.

## Configuration delivery

### CLI flags

CLI args control behavior — `--db-path`, `--read-write`, `--allow-switch-databases`, `--motherduck-token`.

### Environment variables

Credentials via env vars — `motherduck_token`, AWS credentials for S3 access.

## Authentication

### Static API key / token via env var

MotherDuck access via static token in `motherduck_token` env var or `--motherduck-token` parameter.

### Cloud-native identity / credential chain

AWS credentials picked up for S3 access.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per process; database switching available within that single context via `--allow-switch-databases` flag.

### Mode-switched backing store

`--allow-switch-databases` flag toggles whether the user can switch between local DuckDB, MotherDuck cloud, S3-backed, and in-memory databases mid-session.

## Distribution channel

### PyPI via uvx (zero-install runner)

Published to PyPI as `mcp-server-motherduck`; canonical install is `uvx mcp-server-motherduck --db-path :memory: --read-write --allow-switch-databases`.

### MCPB bundle / Desktop Extension manifest

`.mcpb` bundle distribution for Claude Desktop drag-and-drop install, signaled by `.mcpbignore` in repo. GitHub releases publish bundles and source artifacts.

## Entry point and launch

### `uvx <package>`

Primary launch — `uvx mcp-server-motherduck` with CLI flags. README host-config snippet uses `"command": "uvx"`, `"args": ["mcp-server-motherduck", "--db-path", ":memory:", "--read-write", "--allow-switch-databases"]`.

### Console script via `[project.scripts]` / npm bin

`[project.scripts]` registers `mcp-server-motherduck = "mcp_server_motherduck:main"`.

## Build and packaging

### Hatchling + uv (Python)

Build backend `hatchling.build`; `uv` is the version manager convention.

### `uv.lock` committed

`uv.lock` present in the repo.

### Pin discipline (Python)

`fastmcp>=2.14,<3` — pinned major version with tight lower bound to bound breaking-change surface.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP auto-derives schemas from Python type hints.

## Container artifacts

### No container artifacts

No Dockerfile observed; uv-based Python packaging is the preferred distribution path.

### `.mcpbignore` for bundle packaging

`.mcpbignore` file present, governing what enters the `.mcpb` bundle.

## Test stack

### pytest with async + coverage

pytest 8.0+ with `pytest-asyncio>=0.24`; `asyncio_mode = "auto"`, `asyncio_default_fixture_loop_scope = "function"`. Custom `slow` marker for deselection. `testpaths = ["tests"]`. python-dotenv + ruff in test/dev deps.

## CI

### GitHub Actions

`.github/` directory present; specific workflow details not extracted within budget.

## Host integration

### Claude Desktop

JSON-based configuration (`claude_desktop_config.json` snippet).

### Claude Code

Dedicated CLI commands provided.

### Cursor

Supported via host-config snippet.

### VS Code / VS Code Insiders / Visual Studio family

Supported.

### Codex CLI / Copilot CLI / Gemini CLI

Codex CLI and Gemini CLI supported.

## Repository layout

### Single-package src-layout

Single-package Python project with `src/`, `tests/`, `pyproject.toml`, `uv.lock`.

## Safety and security posture

### Read-only by default with explicit write flag

`--read-write` flag explicitly toggles mutating SQL; default posture is read-only.

## Developer ergonomics

### Makefile / Makefile.toml

Makefile present.

### Sample MCP client configs in repo

Sample configurations for Claude Desktop integration shipped alongside the server.

## Documentation surface

### README as the canonical surface

README is the canonical documentation surface.

## Claude Code plugin / skill wrapper

### `.claude-plugin/` wrapper

`.claude-plugin` wrapper mentioned as present, with dedicated CLI commands for Claude Code.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Tagged release with version in changelog

v1.0.4 released March 30, 2026; semver-tagged releases.

### Active development

Active recent release activity.
