# Sample

Mirrors of `https://github.com/jbeno/cursor-notebook-mcp`. Cursor notebook MCP server — operates on Jupyter notebooks (local and remote-over-SFTP) for Cursor and other MCP hosts. ~158 stars, CC BY-NC-SA 4.0 (Creative Commons NonCommercial), default branch `main`, version 0.3.2 referenced.

## Server runtime

### Python with both MCP SDK and FastMCP declared

Python 3.10+ server (`requires-python = ">=3.10"`) declaring both FastMCP 2.x (`fastmcp >= 2.7.0, < 2.11`) and raw `mcp >= 0.1.0` as dependencies. The narrow `< 2.11` upper bound explicitly guards against FastMCP 2.11 breaking changes. Pydantic pinned `>=2.0.0, <2.12.0`. Dual import pattern (`fastmcp` plus `mcp`) suggests a migration or compatibility shim. Async (FastMCP + starlette + uvicorn).

## Transport

### stdio

Supported transport; selectable via Cursor JSON config (command form).

### Streamable HTTP

Recommended transport. Selectable via `--host` and `--port` CLI flags; HTTP host-config snippet shape: `{"url": "http://127.0.0.1:8080/mcp"}` in Cursor config. Whether HTTP transport uses FastMCP's `streamable-http` or a custom Starlette mount is not confirmed.

### SSE (Server-Sent Events)

Legacy transport supported.

### SFTP / SSH for remote resource access

The MCP server speaks stdio/HTTP to the host but the data plane reaches remote Jupyter notebooks over SFTP/SSH. `paramiko >= 2.8.0` is a core dep — SFTP support is mainline, not optional. Workspace-root enforcement applies to remote paths as well as local.

### Selection mechanism

Transport inferred from Cursor JSON config (URL vs command). CLI flags `--host`, `--port` apply to HTTP mode.

## Capability surface

### Domain-bundled tool set

25+ notebook-management tools — `notebook_create`, `notebook_read`, `notebook_edit_cell`, `notebook_add_cell`, `notebook_export`, `notebook_search`, `notebook_get_outline`, `notebook_get_server_path_context`, plus SFTP-compatible variants. Notebook-domain entities (notebooks, cells, outlines) modeled as discrete callable units.

## Configuration delivery

### CLI flags

`--host`, `--port`, `--allow-root`, `--sftp-key`, `--sftp-password`, `--sftp-auth-mode` (auto/key/password/key+interactive). `--allow-root` is required for local-path access (explicit local opt-in).

### Host-side JSON config snippet

Cursor `mcp.json` files — global `~/.cursor/mcp.json` or project-scoped `.cursor/mcp.json`. Both levels documented explicitly.

## Authentication

### SFTP / SSH credentials

Credentials for the SFTP/SSH data plane supplied via `--sftp-key`, `--sftp-password`, with `--sftp-auth-mode` selector (auto/key/password/key+interactive). Interactive prompts supported.

### None / implicit (local-resource gating)

Local-mode access uses workspace-root gating via `--allow-root` rather than authentication; the trust boundary is path scope rather than identity.

## Multi-tenancy

### Workspace-scoped sandboxing within a single tenant

Workspace root restrictions enforced via `os.path.realpath`. `--allow-root` is required for local-path access. Single-user but with explicit workspace-root boundaries; path-traversal defense bounds the blast radius.

## Distribution channel

### PyPI via pip / pipx

`pip install cursor-notebook-mcp` and `uv pip install cursor-notebook-mcp`. Published package name: `cursor-notebook-mcp`.

### Source clone with editable install

`pip install -e ".[dev]"` for development.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

Console script `cursor-notebook-mcp` registered.

### Module invocation / `python -m <module>` fallback

`python -m cursor_notebook_mcp.server` available as alternate entry.

## Build and packaging

### Pin discipline (Python)

Narrow version window `fastmcp >= 2.7.0, < 2.11` (explicit guard against FastMCP 2.11 breaking changes). Pydantic pinned `>=2.0.0, <2.12.0`.

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP auto-derives schemas from signatures.

### Pydantic v2 models

Pydantic 2.x in core deps (`>=2.0.0, <2.12.0`).

## Test stack

### pytest with async + coverage

pytest + pytest-asyncio + pytest-cov + pytest-timeout. `tests/` directory with scenario-based test plan in `test_plan.md`.

## CI

### GitHub Actions

CI present in `.github/`.

## Safety and security posture

### Workspace path enforcement (canonicalization)

Workspace-root restrictions enforced via `os.path.realpath` — explicit path-traversal defense. `--allow-root` gates local-path access; SFTP mode also bounded by workspace-root realpath checks.

## Repository layout

### Single-package src-layout

Single-package (`cursor_notebook_mcp/`) with `examples/` and `tests/` siblings.

## Host integration

### Cursor

`.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) — explicit dual-level config documented.

### Claude Desktop

Implied via stdio transport.

## Developer ergonomics

### PowerShell + batch scripts

Cross-platform test runners `run_tests.sh` and `run_tests.ps1` — Windows parity is explicit, not an afterthought. `test_plan.md` with scenario-based test documentation; example notebooks in `examples/`.

## Documentation surface

### Bundled `cursor_rules.md` / AI-guidance content

`cursor_rules.md` shipped alongside the server as bundled AI-guidance content (neither MCP tool nor MCP prompt) — context for the LLM to read.

## Release and lifecycle

### Active development

Active, with version 0.3.2 referenced.

### License — Copyleft / non-commercial (CC BY-NC-SA)

CC BY-NC-SA 4.0 — non-commercial license. Limits commercial adoption.
