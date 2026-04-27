# Sample

## Identification
- url: https://github.com/samuelgursky/davinci-resolve-mcp
- stars: 833
- last-commit (date or relative): March 16, 2026 (v2.1.0)
- license: MIT
- default branch: main
- one-line purpose: DaVinci Resolve MCP server — universal installer across 10 hosts; two server modes (27 vs 342 tools) and absolute venv-Python host configs.

## 1. Language and runtime
- language(s) + version constraints: Python 99.2%; Python 3.10–3.12
- framework/SDK in use: Model Context Protocol SDK; DaVinci Resolve Scripting API (the application's own Lua/Python API)
- pitfalls observed:
  - Python 3.10-3.12

## 2. Transport
- supported transports: stdio
- how selected (flag, env, separate entry, auto-detect, etc.): Stdio implicit — launched as `python src/server.py`
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: GitHub source-only; universal Python installer (`install.py`) auto-configures 10 MCP clients
- published package name(s): None on PyPI observed — distribution is source + installer
- install commands shown in README: `python install.py`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run:
  - `python src/server.py` (compound mode, 27 tools)
  - `python src/server.py --full` (full mode, 342 tools)
- wrapper scripts, launchers, stubs: `install.py` — universal installer with flags `--clients`, `--dry-run`, `--no-venv`, `--full`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Automatic via `install.py` (generates per-client JSON); manual JSON config in client-specific directories; CLI flags for mode selection
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Not applicable — the server talks to a locally-running DaVinci Resolve instance via its scripting API; no auth layer
- where credentials come from: Not applicable; requires Resolve configured with "External scripting using" set to "Local"
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user — bound to the local user's Resolve instance
- pitfalls observed:
  - Cross-platform sandbox handling — temp paths redirected for macOS/Linux/Windows

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other:
  - 27 compound tools (context-efficient) or 342 granular tools (power user), covering 324 API methods across 13 object classes: Resolve, ProjectManager, Project, MediaStorage, MediaPool, Folder, MediaPoolItem, Timeline, TimelineItem, Gallery, GalleryStillAlbum, Graph, ColorGroup
  - No explicit resources or prompts documented
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not explicitly documented; test suite measures coverage but logging destination for the live server not extracted
- pitfalls observed:
  - Logging destination/format for the live server not documented in extracted content

## 10. Host integrations shown in README or repo
- Claude Desktop, Cursor, VS Code, Windsurf, and 6 additional MCP clients (installer supports 10 clients total)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not explicitly observed within extracted content

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: 5-phase suite — read-only, destructive, media, AI/ML, advanced. 319/324 methods live-tested (98.5%); 319/319 pass rate claimed
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions referenced; specific triggers/jobs not extracted
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not mentioned; Docker would be counterproductive since the server must run on the host with Resolve
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `install.py` orchestrates per-client configs; `examples/` directory; `docs/` directory
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package with support directories — `install.py`, `src/` (server.py, resolve_mcp_server.py, utils/), `tests/`, `docs/`, `examples/`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Dual-mode architecture — compound (27 aggregate tools) vs. full (342 granular tools) — lets users trade prompt-window efficiency against expressive power
- Lazy connection — auto-reconnects and auto-launches Resolve on first tool call, smoothing the cold-start UX
- Path-traversal protection — file-op tools validate paths stay within expected directories
- Auto-cleanup — exports are deleted after response encoding, preventing disk bloat
- Cross-platform sandbox handling — temp paths redirected for macOS/Linux/Windows
- Universal installer that writes per-client configs (10 clients) is unusually ambitious for a single-purpose MCP

## Platform requirements

### OS

macOS, Windows, Linux

- DaVinci Resolve Studio 18.5+ (free edition unsupported)
- Python 3.10-3.12
- Resolve must be running locally

## 18. Unanticipated axes observed
- Tool-surface explosion — 342 granular tools is one of the largest tool surfaces among MCPs surveyed; the dual-mode design exists specifically to counter context-window pressure
- Free-edition exclusion is a real constraint — Resolve's scripting API is Studio-only; the MCP inherits that limitation
- First-party vendor (Blackmagic Design) has no MCP; this third-party server is effectively canonical for 833-star community

## 19. Python-specific

### SDK / framework variant
- Raw `mcp` Python SDK presumed (no fastmcp observed); not confirmed at source level
- Bridges to DaVinci Resolve's own Python scripting API (Blackmagic DaVinciResolveScript module)

### Python version floor
- README states Python 3.10–3.12 (inclusive upper bound — 3.13+ explicitly unsupported due to Resolve ABI incompatibilities)

### Packaging
- NO pyproject.toml, NO setup.py, NO requirements.txt at top level
- Uses a custom `install.py` (34 KB script) that creates a venv and installs dependencies
- lock file: none
- version manager convention: plain pip inside a venv managed by `install.py`

### Entry point
- No Python packaging entry point — `python src/server.py` and `python src/server.py --full`
- README host-config snippet: `"command": "/path/to/venv/bin/python"`, `"args": ["/path/to/davinci-resolve-mcp/src/server.py"]` — absolute venv-Python path + absolute script path

### Install workflow expected of end users
- `python install.py` — custom orchestrator that finds Resolve, creates venv, installs deps, writes per-client JSON config for up to 10 MCP clients
- No PyPI, no uvx, no Docker (intentional — must run on Resolve host)

### Async and tool signatures
- Not inspected at source level; DaVinci Resolve's scripting API is synchronous (Lua-derived Python bindings)

### Type / schema strategy
- Not observed; likely hand-authored given raw SDK usage and 324 API methods surfaced

### Testing
- 5-phase live test suite (read-only, destructive, media, AI/ML, advanced); 319/324 methods live-tested
- Framework not identified (tests/ directory present but pytest not confirmed)

### Dev ergonomics
- Custom `install.py` is the dev entry point — replaces both pip and uv roles
- `--dry-run`, `--no-venv`, `--full`, `--clients` flags on installer

### Notable Python-specific choices
- No pyproject.toml at all — outlier in the sample; installation is entirely orchestrated by a bespoke script
- Absolute-venv-Python path in host config — the cost of not publishing to PyPI; hosts must know both the venv path and the script path
- Python 3.10–3.12 range (upper bound) — one of the few repos with an upper bound driven by ABI compat (Resolve's binary scripting module)
- Installer-configures-10-MCP-clients — the `install.py` writes client-specific JSON to 10 separate config locations, a Python-ecosystem alternative to relying on uvx ubiquity

## 20. Gaps
- Last commit confirmed but release cadence and precise CI triggers not extracted
- Logging destination/format for the live server not documented in extracted content
- Whether any hosted or remote variant exists (unlikely given local-Resolve dependency)
