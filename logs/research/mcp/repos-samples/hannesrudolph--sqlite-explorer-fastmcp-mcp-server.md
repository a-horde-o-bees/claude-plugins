# Sample

Mirrors of `https://github.com/hannesrudolph/sqlite-explorer-fastmcp-mcp-server`. SQLite explorer MCP server — single-script Python server installed via `fastmcp install`; pre-`pyproject.toml`-era layout pinned to FastMCP 0.4.1. 104 stars, default branch `main`, 9 total commits. License not surfaced.

## Server runtime

### Python with FastMCP (pre-2.x era)

Python (100% of repo). `requirements.txt` pins `fastmcp==0.4.1` — FastMCP 1.x (pre-2.x era), reference case for "how the FastMCP ecosystem looked before the 2.0 split". Import pattern: `from fastmcp import FastMCP` or `from mcp.server.fastmcp import FastMCP` (README implies in-SDK FastMCP).

## Transport

### stdio

Default for FastMCP-installed servers.

### Selection mechanism

Implicit default — FastMCP CLI installer wires stdio transport; no explicit flag documented.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools only — `read_query` (SELECT with validation and row limits), `list_tables`, `describe_table`. No resources, prompts, sampling, or roots.

## Configuration delivery

### Environment variables

`SQLITE_DB_PATH` (required) — no CLI flags or config files documented.

## Authentication

### None / implicit (local-resource gating)

None — local SQLite file access, no credentials. The host's process boundary is the trust boundary.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user, single-database — one SQLite file per server instance pinned via env var.

## Distribution channel

### Source clone with editable install

Git clone from source; no PyPI/npm/Docker artifacts observed — unpublished repo-only server.

### SDK CLI installer

`fastmcp install sqlite_explorer.py --name "SQLite Explorer" -e SQLITE_DB_PATH=/path/to/db` — uses the FastMCP CLI installer, which registers the server with Claude Desktop directly. Distinct from `uvx` or manual config-editing.

## Entry point and launch

### Bare interpreter + script path

Single-file `sqlite_explorer.py` script; no installable console script.

### Source-tree `uv run`

Cline config: `"command": "uv"`, `"args": ["run", "--with", "fastmcp", "--with", "uvicorn", "fastmcp", "run", "/path/to/sqlite_explorer.py"]`.

## Build and packaging

### Requirements-driven (legacy Python)

NO `pyproject.toml` — only `requirements.txt` + single `sqlite_explorer.py`. Build backend not applicable (no package build). No lock file. Pip/venv version manager convention (no uv-native layout). Pre-`pyproject.toml`-era layout.

### Python version pinning

README states Python 3.6+ (likely optimistic; FastMCP 0.4.1 itself probably needs 3.10).

## Schema and types

### FastMCP auto-derivation from type hints

FastMCP-decorated functions; schema auto-derived from Python type hints. fastmcp==0.4.1 supports both sync and async decorators.

## Host integration

### Claude Desktop

Supported via FastMCP CLI install (`fastmcp install` registers with Claude Desktop directly).

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline (VS Code) — manual MCP configuration example provided.

## Test stack

### No tests / not surfaced

No tests observed in repo.

## CI

### None / absent

No `.github/workflows` observed.

## Container artifacts

### No container artifacts

None observed.

## Repository layout

### Single-file script / monolith

Single-file script with requirements and docs — minimal single-package layout.

## Safety and security posture

### Tool-layer query validation

Read-only posture enforced at the tool layer (SELECT-only validation + row caps), not DB-level.

## Observability

### Suppressed stdout / discipline-only

README notes "progress output suppression for clean JSON responses" as a deliberate design behavior — stdio-protocol cleanliness pressure.

## Documentation surface

### `llms.txt` / `llms-full.txt`

Repo bundles `fastmcp-documentation.txt` + `mcp-documentation.txt` — embedded LLM-context docs.

## Developer ergonomics

### MCP framework dev config

`fastmcp install` is the only dev tool surfaced.
