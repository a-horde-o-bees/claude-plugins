# Sample

Mirrors of `https://github.com/twolven/mcp-server-puppeteer-py`. Puppeteer-themed Python MCP server wrapping Playwright (Python equivalent of Puppeteer per README) for browser automation. 17 stars, Apache-2.0, default branch `main`. Single-maintainer experimental repo with legacy `setup.py`-only packaging and a Python 3.8+ floor — the lowest in the corpus.

## Server runtime

### Python with raw MCP SDK

Direct use of Anthropic's `mcp` Python SDK without a higher-level framework wrapper. `setup.py` declares `mcp-server>=0.1.0` (the legacy pre-1.0 package name); `requirements.txt` lists `mcp` — ambiguous which package actually installs. No FastMCP. Tool handlers likely `async def` since Playwright is async Python; not confirmed via tests (none ship).

## Transport

### stdio

stdio-only — launched as a script and wired into Claude Desktop's stdio JSON config.

### Selection mechanism

Implicit single mode — stdio only; transport not named in README, deduced from launch command shape.

## Capability surface

### Tools-only, hand-curated narrow surface

Five tools — `puppeteer_navigate` (URL navigation with timeouts), `puppeteer_screenshot` (full-page or element), `puppeteer_click` (DOM interaction), `puppeteer_fill` (form input), `puppeteer_evaluate` (arbitrary JS execution in page). Minimum viable browser MCP; contrasts with larger browser-automation servers.

## Configuration delivery

### Host-side JSON config snippet

Claude Desktop JSON config example shown in README — `"command": "python"` with `"args": ["path/to/puppeteer.py"]`. Per-tool parameters (timeouts, screenshot targets) handle behavior at call time; CLI args / env vars not documented in detail.

## Authentication

### None / implicit (local-resource gating)

No auth — browser automation against the public web. Playwright session state is the only "credentials" surface and lives outside the MCP server.

## Multi-tenancy

### Single-user / single-tenant per process

One browser per process; single-user by construction.

## Distribution channel

### Source clone with editable install

Source-only — clone the repo, `pip install -r requirements.txt`, then `playwright install` for browsers. No PyPI publication, no Docker artifact.

## Entry point and launch

### Bare interpreter + script path

`python puppeteer.py` directly — bare `python` on system PATH, fragile (depends on which interpreter is first found). Single-file entry at `puppeteer.py` at repo root.

### Console script via `[project.scripts]` / npm bin

`setup.py` declares a `[console_scripts]` entry `mcp-server-puppeteer = mcp_server_puppeteer.server:main`, but the README runs `python puppeteer.py` directly — entry-point path and working entry-point diverge. Sign that the package was never installed/tested as a console script.

## Build and packaging

### Setuptools (with `setup.py` or `setup.cfg`)

Legacy `setup.py` packaging only — no `pyproject.toml`. `setup.py` declares `python_requires=">=3.8"` and a `[console_scripts]` entry that diverges from how the project is actually launched.

### Requirements-driven (legacy Python)

`requirements.txt` alongside `setup.py`. No lock file. Plain pip-only workflow predating uv/pipx conventions.

### Python version pinning

`requires-python = ">=3.8"` declared in `setup.py` — the lowest Python floor observed in the Python sample.

### System-level dependencies

Playwright pulls a browser binary at install time via `playwright install`. Multi-GB install footprint typical of browser-automation servers.

## Container artifacts

### No container artifacts

No Dockerfile; users install on the host directly.

## Test stack

### No tests / not surfaced

No tests/ directory observed. Reduces confidence in tool behavior across browser-engine updates.

## CI

### None / absent

No `.github/workflows` observed.

## Host integration

### Claude Desktop

JSON config example shown in README — Claude Desktop is the primary documented host.

## Observability

### Stderr logging (convention / SDK default)

"Detailed error handling and logging" claimed by README; destination not specified — likely stderr per stdio-server convention.

## Repository layout

### Single-file script / monolith

Single-file `puppeteer.py` at repo root plus `requirements.txt` and `setup.py`. The minimum viable layout.

## Domain logic and embedded intelligence

### Pass-through tool wrappers

Tools map to Playwright operations; in-memory base64-encoded screenshot storage flows through MCP responses without disk intermediate. Deliberately non-headless browser mode — a design choice that trades production efficiency for interactive visibility during development.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0 on a single-maintainer experimental repo; permissive license choice for community adoption.
