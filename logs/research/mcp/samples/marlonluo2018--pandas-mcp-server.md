# Sample

## Identification

### url

https://github.com/marlonluo2018/pandas-mcp-server

### stars

~40

### last-commit

not explicitly surfaced; moderate-activity repo

### license

MIT

### default branch

main

### one-line purpose

Pandas DataFrame analysis MCP server — blacklist-sandboxed pandas code execution for data exploration.

## 1. Language and runtime

### language(s) + version constraints

Python (84.6%), HTML (15.4%); Python 3.10+

### framework/SDK in use

FastMCP (`fastmcp >= 1.0.0`) — suggests FastMCP 1.x era or the built-in `mcp.server.fastmcp` submodule

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (MCP default)

### how selected

stdio only (no alternate transport documented)

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

source clone + `pip install -r requirements.txt`; `uvx pandas-mcp-cli` hinted

### published package name(s)

`pandas-mcp-cli` (inferred from uvx command)

### install commands shown in README

`pip install -r requirements.txt`; `uvx pandas-mcp-cli`

### pitfalls observed

Whether `pandas-mcp-cli` is actually a published PyPI package not verified.

## 4. Entry point / launch

### command(s) users/hosts run

`python server.py` (server), `python cli.py` (CLI), `uvx pandas-mcp-cli`

### wrapper scripts, launchers, stubs

`server.py` and `cli.py` at repo root

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

optional `.env` file with `.env.example` template

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

none

### where credentials come from

N/A

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

single-user; operates on user-supplied CSV/data paths per call

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

4 tools — `read_metadata_tool` (file structure), `interpret_column_data` (column value patterns), `run_pandas_code_tool` (sandboxed pandas execution), `generate_chartjs_tool` (interactive chart generation)

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

logs written to `./logs/`; chart outputs to `./charts/` — both file-system based

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

Windows/macOS/Linux config paths documented with command/args form

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

none observed

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

`test_metadata.py`, `test_execution.py`, `test_generate_barchart.py` at root — pytest-style but located at top level

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

none mentioned

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

none mentioned

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`.env.example`; per-OS Claude Desktop paths

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

flat layout — `/core` subdirectory (metadata, execution, visualization, chart_generators); scripts at root

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Security posture: "sandboxed pandas execution" via blacklist filtering of malicious operations — string-level denylist is a known-fragile approach versus process isolation or restricted exec. Generates HTML with Chart.js and writes to `./charts/` — chart artifacts persist on disk; MCP client has to read the file path. Uses `psutil` in core deps — likely for memory/CPU budgeting of user-submitted code.

## 18. Unanticipated axes observed

Persistent file-system output as the tool return channel (return a path, not data) for visualizations. Blacklist-based sandboxing for arbitrary pandas code execution — a fundamentally different trust model than pure read-only tool servers.

## 19. Python-specific

### SDK / framework variant

FastMCP (`fastmcp >= 1.0.0`); lower bound suggests FastMCP 1.x–compatible usage. Version pin from pyproject.toml: `fastmcp >= 1.0.0`. Import pattern observed likely `from fastmcp import FastMCP` or via `mcp.server.fastmcp`.

### Python version floor

`requires-python` value: Python 3.10+ (per README)

### Packaging

Build backend not surfaced. Lock file: `requirements.txt` only (no uv.lock). Version manager convention: pip-only.

### Entry point

Bare scripts (`server.py`, `cli.py`). No console-script names locally; `pandas-mcp-cli` via uvx suggests a PyPI publication. Host-config snippet shape: `python <path>/server.py` in Claude Desktop config.

### Install workflow expected of end users

Source clone + pip. One-liner the README recommends: `pip install -r requirements.txt` after clone.

### Async and tool signatures

Not surfaced; pandas code execution is sync by nature.

### Type / schema strategy

Pydantic via FastMCP; hand-authored tool schemas likely.

### Testing

pytest (inferred from `test_*.py` naming). Fixture style not inspected.

### Dev ergonomics

not surfaced

### Notable Python-specific choices

`psutil` as a core dep — used for resource accounting around the pandas sandbox. `chardet>=5.0.0` in core — auto-detects CSV encoding, a frequent real-world pain point. Tests at repo root rather than `tests/` directory — nonstandard location.

## 20. Gaps

Whether `pandas-mcp-cli` is actually a published PyPI package not verified. License/CI/Docker absence vs just not documented not determined. Exact dependency pin list beyond pandas/fastmcp/chardet/psutil not read.
