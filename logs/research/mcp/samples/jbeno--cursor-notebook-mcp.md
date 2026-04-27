# Sample

## Identification

### url

https://github.com/jbeno/cursor-notebook-mcp

### stars

~158

### last-commit

active; version 0.3.2 referenced

### license

CC BY-NC-SA 4.0 (Creative Commons, NonCommercial)

### default branch

main

### one-line purpose

Cursor notebook MCP server — SFTP transport for operating on remote Jupyter notebooks; CC BY-NC-SA license.

## 1. Language and runtime

### language(s) + version constraints

Python 3.10+

### framework/SDK in use

FastMCP 2.x (`fastmcp >= 2.7.0, < 2.11`) plus raw `mcp >= 0.1.0` as fallback

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

Streamable HTTP (recommended), SSE (legacy), stdio

### how selected

CLI flags `--host`, `--port`; transport inferred from Cursor JSON config (URL vs command)

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

PyPI (`pip install`, `uv pip install`), editable dev install

### published package name(s)

`cursor-notebook-mcp`

### install commands shown in README

`pip install cursor-notebook-mcp`, `uv pip install cursor-notebook-mcp`, `pip install -e ".[dev]"`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`cursor-notebook-mcp` console script or `python -m cursor_notebook_mcp.server`

### wrapper scripts, launchers, stubs

`run_tests.sh` / `run_tests.ps1` test wrappers

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

CLI flags (`--host`, `--port`, `--allow-root`, `--sftp-*`); Cursor `mcp.json` files (global `~/.cursor/mcp.json` or project-scoped `.cursor/mcp.json`)

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

SFTP/SSH for remote notebook access

### where credentials come from

`--sftp-key`, `--sftp-password`, `--sftp-auth-mode` (auto/key/password/key+interactive); interactive prompts supported

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

workspace-keyed — workspace root restrictions enforced via `os.path.realpath`; `--allow-root` required for local-path access

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

25+ tools — `notebook_create`, `notebook_read`, `notebook_edit_cell`, `notebook_add_cell`, `notebook_export`, `notebook_search`, `notebook_get_outline`, `notebook_get_server_path_context`, plus SFTP-compatible variants

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not surfaced

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Cursor

`.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global) — explicit dual-level config documented

### Claude Desktop

implied via stdio transport

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed; optimized for Cursor specifically

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

pytest + pytest-asyncio + pytest-cov + pytest-timeout; `tests/` directory; `test_plan.md` with scenario-based test documentation; cross-platform test runners

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions in `.github/`

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

none observed

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`cursor_rules.md` (AI guidance rules), `test_plan.md`, example notebooks in `examples/`

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package (`cursor_notebook_mcp/`) + `examples/` + `tests/`

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Non-commercial license (CC BY-NC-SA 4.0) is rare for MCP servers, which overwhelmingly pick permissive licenses; this limits commercial adoption. Dual MCP framework deps — both `fastmcp` and raw `mcp` — suggest a migration or compatibility shim. SFTP transport for notebook files operates on remote notebooks over SSH, not just local; this brings `paramiko>=2.8.0` into core deps. Workspace-root enforcement via `os.path.realpath` is an explicit path-traversal defense.

## 18. Unanticipated axes observed

MCP server accessing remote filesystem over SFTP (not HTTP/REST) — the server itself is a local process but files live remotely; workspace-root boundary as a security primitive; a `cursor_rules.md` file shipped *alongside* the MCP server as AI-guidance content (neither MCP tool nor MCP prompt — just bundled documentation for the LLM to read).

## 19. Python-specific

### SDK / framework variant

FastMCP 2.x (`>=2.7.0, <2.11`) with `mcp>=0.1.0` also declared. Version pins from pyproject.toml — `fastmcp>=2.7.0,<2.11`, `pydantic>=2.0.0,<2.12.0`. Import pattern observed: `fastmcp` + `mcp`.

### Python version floor

`requires-python` value — `>=3.10`

### Packaging

Build backend not surfaced. Lock file not surfaced. Version manager convention: pip / uv pip compatible.

### Entry point

Both `cursor-notebook-mcp` console script and `python -m cursor_notebook_mcp.server`. Console-script name: `cursor-notebook-mcp`. Host-config snippet shape for HTTP transport: `{"url": "http://127.0.0.1:8080/mcp"}` in Cursor config.

### Install workflow expected of end users

pip + uv pip. One-liner the README recommends — `pip install cursor-notebook-mcp`.

### Async and tool signatures

async (FastMCP + starlette + uvicorn)

### Type / schema strategy

Pydantic 2.x (`>=2.0.0, <2.12.0`); FastMCP auto-derives from signatures.

### Testing

pytest + pytest-asyncio + pytest-cov + pytest-timeout. Fixture style: scenario-based test plan in `test_plan.md`.

### Dev ergonomics

`run_tests.sh` and `run_tests.ps1` for cross-platform test wrappers.

### Notable Python-specific choices

Pinned FastMCP to a narrow `>=2.7.0,<2.11` window, explicitly guarding against FastMCP 2.11 breaking changes. `paramiko` as a core dep — SFTP support is mainline, not optional. Dual-platform shell scripts (`.sh`/`.ps1`) for test invocation — Windows parity is explicit, not an afterthought.

## 20. Gaps

Whether HTTP transport is FastMCP's `streamable-http` or a custom Starlette mount is not confirmed. Lock file convention not verified. Whether SFTP backend is mandatory or falls back to local when no SFTP args given is unclear — the `--allow-root` gating suggests explicit local opt-in.
