# Sample

## Identification

### url

https://github.com/hannesrudolph/sqlite-explorer-fastmcp-mcp-server

### stars

104

### last-commit (date or relative)

Not surfaced from landing page; repo reports 9 total commits on main

### license

Not surfaced on landing page fetch; file LICENSE not confirmed within budget

### default branch

main

### one-line purpose

SQLite explorer MCP server — single script installed via `fastmcp install`; pre-`pyproject.toml`-era layout pinned to FastMCP 0.4.1.

## 1. Language and runtime

### language(s) + version constraints

Python (100% of repo), Python 3.6+

### framework/SDK in use

FastMCP

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (default for FastMCP-installed servers)

### how selected (flag, env, separate entry, auto-detect, etc.)

Implicit — FastMCP CLI installer wires stdio transport; no explicit flag documented

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

Git clone from source; FastMCP CLI install (`fastmcp install`); UV-based environment execution; no PyPI/npm/Docker artifacts observed

### published package name(s)

None — unpublished repo-only server

### install commands shown in README

`fastmcp install sqlite_explorer.py --name "SQLite Explorer" -e SQLITE_DB_PATH=/path/to/db`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`fastmcp install sqlite_explorer.py` then host launches via its configured MCP command; direct run also possible via `uv` with fastmcp + uvicorn

### wrapper scripts, launchers, stubs

Single-file `sqlite_explorer.py` script; no additional launcher

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Environment variable `SQLITE_DB_PATH` (required); no CLI flags or config files documented

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

None — local SQLite file access, no credentials

### where credentials come from

Not applicable for local SQLite

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

Single-user, single-database — one SQLite file per server instance pinned via env var

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools only — `read_query` (SELECT with validation and row limits), `list_tables`, `describe_table`. No resources, prompts, sampling, or roots.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

None documented; README notes "progress output suppression for clean JSON responses" as a deliberate behavior

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

Supported via FastMCP CLI install

### Cline (VS Code)

Manual MCP configuration example provided

### Other editors/CLIs

Not mentioned

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present — no `.claude-plugin` directory or Claude Code specific wiring observed

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

No tests observed in repo

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

No `.github/workflows` observed

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

None observed

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Sample Cline VSCode JSON config shown; FastMCP CLI install as the primary dev ergonomic

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single-file script with requirements and docs — minimal single-package layout

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Single-file server script (`sqlite_explorer.py`) keeps the surface tiny
- Read-only posture enforced at the tool layer (query validation + row caps), not DB-level
- Minimal dependency: FastMCP only

## 18. Unanticipated axes observed
- Docs explicitly flag "progress output suppression" as a design concern, reflecting stdio-protocol cleanliness pressure

## 19. Python-specific

### SDK / framework variant
- FastMCP 1.x (pre-2.x era) — `requirements.txt` pins `fastmcp==0.4.1`
- Import pattern: FastMCP 1.x (`from fastmcp import FastMCP` or `from mcp.server.fastmcp import FastMCP`) — README implies in-SDK FastMCP

### Python version floor
- README states Python 3.6+ (likely optimistic; FastMCP 0.4.1 itself probably needs 3.10)

### Packaging
- NO pyproject.toml — only `requirements.txt` + single `sqlite_explorer.py`
- build backend: not applicable (no package build)
- lock file: none
- version manager convention: pip/venv (no uv-native layout)

### Entry point
- No `[project.scripts]` — script is run directly via `fastmcp install sqlite_explorer.py` or `fastmcp run`
- README's Cline config: `"command": "uv"`, `"args": ["run", "--with", "fastmcp", "--with", "uvicorn", "fastmcp", "run", "/path/to/sqlite_explorer.py"]`

### Install workflow expected of end users
- `fastmcp install sqlite_explorer.py --name "SQLite Explorer" -e SQLITE_DB_PATH=/path/to/db` — uses the FastMCP CLI installer
- No pip-install path; repo is clone + FastMCP-CLI-managed

### Async and tool signatures
- FastMCP-decorated functions; source not inspected
- fastmcp==0.4.1 supports both sync and async decorators

### Type / schema strategy
- FastMCP auto-derived from type hints

### Testing
- None

### Dev ergonomics
- `fastmcp install` is the only dev tool surfaced
- Uses `fastmcp-documentation.txt` + `mcp-documentation.txt` in repo — embedded LLM-context docs

### Notable Python-specific choices
- Pre-`pyproject.toml`-era layout: `requirements.txt` + single script + no packaging
- Pinned to FastMCP 0.4.1 — significantly behind the 2.x/3.x current frontier; reference case for "how the FastMCP ecosystem looked before the 2.0 split"
- `fastmcp install` registers the server with Claude Desktop directly — demonstrates FastMCP's own CLI install mechanism, distinct from `uvx` or manual config-editing

## 20. Gaps
- Exact license file contents not confirmed within budget
- Commit date/last-commit metadata not surfaced from landing page
- No CI, tests, or container artifacts to inspect
