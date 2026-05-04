# Sample

Mirrors of `https://github.com/marlonluo2018/pandas-mcp-server`. Pandas DataFrame analysis MCP server — blacklist-sandboxed pandas code execution for data exploration; generates Chart.js visualizations to disk. ~40 stars, MIT, default branch `main`, moderate-activity repo.

## Server runtime

### Python with FastMCP

Python (84.6%) plus HTML (15.4%); Python 3.10+; FastMCP runtime declared as `fastmcp >= 1.0.0` — lower bound suggests FastMCP 1.x-compatible usage. Import pattern likely `from fastmcp import FastMCP` or via `mcp.server.fastmcp`. Hand-authored tool schemas likely with Pydantic via FastMCP. Pandas execution sync by nature.

## Transport

### stdio

MCP default; no alternate transport documented.

### Selection mechanism

Implicit single mode — stdio only.

## Capability surface

### Tools-only, hand-curated narrow surface

4 tools: `read_metadata_tool` (file structure), `interpret_column_data` (column value patterns), `run_pandas_code_tool` (sandboxed pandas execution), `generate_chartjs_tool` (interactive chart generation). No resources, prompts, sampling, or other primitives.

### Single code-execution tool with sandbox

`run_pandas_code_tool` accepts arbitrary pandas code and executes server-side under a string-level denylist filter. Replaces N hand-enumerated per-operation tools with one flexible primitive. Resource accounting via `psutil` for memory/CPU budgeting of user-submitted code.

## Configuration delivery

### Dotenv file

Optional `.env` file with `.env.example` template shipped in repo.

## Authentication

### None / implicit (local-resource gating)

No auth — local data exploration; trust derived from process boundary. Operates on user-supplied CSV/data paths.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user; operates on user-supplied CSV/data paths per call.

## Distribution channel

### Source clone with editable install

`pip install -r requirements.txt` after clone is the documented install path.

### PyPI via uvx (zero-install runner)

`uvx pandas-mcp-cli` hinted (whether the package is actually published to PyPI not verified).

## Entry point and launch

### Bare interpreter + script path

`python server.py` (server) and `python cli.py` (CLI) — bare scripts at repo root.

### `uvx <package>`

`uvx pandas-mcp-cli` if the package is published.

## Build and packaging

### Requirements-driven (legacy Python)

`requirements.txt` only (no `uv.lock`). Build backend not surfaced; pip-only version manager convention.

### Pin discipline (Python)

Loose pin `fastmcp >= 1.0.0` — minimal-ceremony posture. `pytest>=8.3.5` and `pillow>=11.2.1` declared in core deps; `pytest` as a runtime dep is likely an oversight (would normally be a dev extra).

## Schema and types

### FastMCP auto-derivation from type hints

Pydantic via FastMCP; tool schemas hand-authored or auto-derived from typed signatures.

### Async model (cross-cutting)

Sync throughout — pandas operations are sync by nature.

## Test stack

### pytest with async + coverage

pytest-style tests at repo root (`test_metadata.py`, `test_execution.py`, `test_generate_barchart.py`) — nonstandard location (top-level rather than `tests/`).

## Observability

### File-system artifacts as side effects

Logs written to `./logs/`; chart outputs to `./charts/` — both file-system based. Tool returns paths, not data.

## Safety and security posture

### Blacklist-filtered code execution

Server accepts user-submitted pandas code and filters dangerous operations via a string-level denylist. Resource accounting via `psutil`. A known-fragile approach (string-level denylist vs process isolation or restricted exec); the convenience of in-process execution is taken over the risk of denylist gaps.

## Container artifacts

### No container artifacts

No Dockerfile or docker-compose mentioned.

## CI

### None / absent

No CI configured.

## Host integration

### Per-OS path documentation

Claude Desktop section enumerates Windows/macOS/Linux config paths with command/args form.

### Claude Desktop

Documented integration via per-OS config-file paths.

## Repository layout

### Single-package flat layout

Flat layout — `/core` subdirectory (metadata, execution, visualization, chart_generators); scripts at repo root. "Hackable" community server layout.

## Documentation surface

### README as the canonical surface

Single README.md.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT license.

### Active development

Moderate-activity repo.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin/` directory or Claude Code wrapper.
