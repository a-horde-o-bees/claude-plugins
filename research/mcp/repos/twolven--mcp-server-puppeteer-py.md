# twolven/mcp-server-puppeteer-py

## Identification
- url: https://github.com/twolven/mcp-server-puppeteer-py
- stars: 17
- last-commit (date or relative): Not explicitly extracted within budget
- license: Apache-2.0
- default branch: main
- one-line purpose: Puppeteer (Python) MCP server — legacy setup.py-only packaging; Python 3.8+ floor.

## 1. Language and runtime
- language(s) + version constraints: Python (100%); Python 3.8+
- framework/SDK in use: Model Context Protocol SDK (Python); Playwright as browser engine (despite "puppeteer" in name — README notes Playwright is the Python equivalent)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio
- how selected (flag, env, separate entry, auto-detect, etc.): Stdio implicit — launched as a module via `python puppeteer.py` and wired into Claude Desktop's stdio JSON config
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: Source-only — clone and run; no PyPI package observed, no Docker artifact
- published package name(s): None observed
- install commands shown in README: `pip install -r requirements.txt` and `playwright install` for browsers
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `python puppeteer.py`
- wrapper scripts, launchers, stubs: Single-file entry — `puppeteer.py` at repo root
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: CLI args / environment not documented in detail; per-tool parameters control behavior (timeouts, screenshot targets)
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Not applicable — browser automation against public web
- where credentials come from: Not applicable
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user — one browser per process
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Five tools — `puppeteer_navigate` (URL navigation with timeouts), `puppeteer_screenshot` (full-page or element), `puppeteer_click` (DOM interaction), `puppeteer_fill` (form input), `puppeteer_evaluate` (arbitrary JS execution in page)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: "Detailed error handling and logging" claimed by README; destination not specified — likely stderr
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop (JSON config example)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: Not present — no `.claude-plugin` directory observed
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Not observed — no tests/ directory surfaced
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: Not observed — no `.github/workflows` surfaced
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not observed
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Claude Desktop sample config; `requirements.txt` for Python deps
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-file script repo — `puppeteer.py` plus `requirements.txt`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Deliberately non-headless browser mode for easier debugging — a design choice that trades production efficiency for interactive visibility during development
- In-memory base64-encoded screenshot storage — screenshots flow through MCP responses without disk intermediate
- Name ("puppeteer-py") reflects user-facing tool concept; implementation actually wraps Playwright. This is a terminology-vs-implementation asymmetry worth noting

## 18. Unanticipated axes observed
- Minimal surface — only 5 tools — contrasts with larger browser servers (executeautomation/mcp-playwright's richer surface). Useful as a reference minimum viable browser MCP
- Apache-2.0 on a single-maintainer experimental repo; permissive license choice for community adoption

## 19. Python-specific

### SDK / framework variant
- Depends on `mcp-server>=0.1.0` (per setup.py — an older / pre-1.0 MCP package name); requirements.txt lists `mcp` — ambiguous which package actually installs
- No fastmcp
- Single-file `puppeteer.py` (setup.py points at `mcp_server_puppeteer.server:main`, but the repo actually runs `python puppeteer.py` — entry point and README are inconsistent)

### Python version floor
- setup.py: `python_requires=">=3.8"` — lowest in the sample

### Packaging
- build backend: legacy setuptools via `setup.py` (no pyproject.toml)
- lock file: none
- version manager convention: plain pip + `requirements.txt`

### Entry point
- `[console_scripts]` in setup.py: `mcp-server-puppeteer=mcp_server_puppeteer.server:main`
- But README runs `python puppeteer.py` directly — entry-point path and working entry-point diverge
- Host config: `"command": "python"`, `"args": ["path/to/puppeteer.py"]` — bare `python` on system PATH

### Install workflow expected of end users
- `pip install -r requirements.txt` + `playwright install`
- Clone-from-source only; no PyPI publication
- No uv/uvx/pipx/Docker

### Async and tool signatures
- Playwright is async Python; tools likely `async def`
- No test framework to confirm

### Type / schema strategy
- Raw `mcp` SDK — hand-authored schemas likely

### Testing
- None

### Dev ergonomics
- None beyond `requirements.txt`

### Notable Python-specific choices
- Pre-modern packaging: `setup.py` + `requirements.txt` with no `pyproject.toml`
- Python 3.8+ floor is the lowest in the Python sample — reflects the older `setup.py`-era layout
- Inconsistent entry point — the README entry (`python puppeteer.py`) doesn't match setup.py's declared console script, indicating neither was tested against PyPI
- Bare `python` in Claude Desktop config — fragile (relies on system PATH, specific venv activation)

## 20. Gaps
- Last commit date not extracted
- Whether Python stdout is protected from log pollution (important for stdio JSON-RPC correctness) — not stated
- No tests reduces confidence in tool behavior across browser-engine updates
