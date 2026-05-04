# Sample

Mirrors of `https://github.com/samuelgursky/davinci-resolve-mcp`. DaVinci Resolve MCP server — wraps Resolve's scripting API; ships a universal Python installer that auto-configures 10 MCP clients; two operating modes (27 compound tools vs 342 granular tools); absolute venv-Python paths in host configs. 833 stars, MIT, default branch `main`. Last commit March 16, 2026 (v2.1.0).

## Server runtime

### Python with raw MCP SDK

Raw `mcp` Python SDK presumed (no FastMCP observed); not confirmed at source level. Bridges to DaVinci Resolve's own Python scripting API (Blackmagic `DaVinciResolveScript` module — a Lua-derived Python binding). Python 99.2% of repo.

## Transport

### stdio

stdio implicit — server launched as `python src/server.py`. No HTTP/network mode documented.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

342 granular tools cover 324 API methods across 13 object classes: Resolve, ProjectManager, Project, MediaStorage, MediaPool, Folder, MediaPoolItem, Timeline, TimelineItem, Gallery, GalleryStillAlbum, Graph, ColorGroup. Domain decomposition by upstream-API object class. No explicit resources or prompts documented.

### Tool-count modes (compound vs full)

Dual-mode architecture: compound mode exposes 27 aggregate tools; full mode (`--full` flag) exposes 342 granular tools. Lets users trade prompt-window efficiency against expressive power without re-installing. The dual-mode design exists specifically to counter context-window pressure on the 342-tool surface.

## Configuration delivery

### CLI flags

`--full` flag selects between compound (27 tools) and full (342 tools) modes at launch.

### Auto-generated host-config JSON files

`install.py` automatically writes per-client JSON configuration files into 10 different MCP-client config locations.

### Host-side JSON config snippet

Manual JSON config in client-specific directories supported as an alternative to the installer; absolute venv-Python path + absolute script path required.

## Authentication

### Locally-running application IPC

Server talks to a locally-running DaVinci Resolve instance via Resolve's scripting API; Resolve must be configured with "External scripting using" set to "Local". No credential layer.

## Multi-tenancy

### Single-user / single-tenant per process

Bound to the local user's running Resolve instance.

## Distribution channel

### Custom Python installer script

Custom `install.py` (~34 KB) is the primary distribution vector — finds Resolve, creates a venv, installs deps, writes per-client JSON config for up to 10 MCP clients. No PyPI, no uvx, no Docker (intentional — must run on the Resolve host).

## Entry point and launch

### Bare interpreter + script path

`python src/server.py` (compound mode, 27 tools) or `python src/server.py --full` (full mode, 342 tools). README host-config snippet uses `"command": "/path/to/venv/bin/python"`, `"args": ["/path/to/davinci-resolve-mcp/src/server.py"]` — absolute venv-Python path plus absolute script path. No Python packaging entry point.

## Build and packaging

### Bare script (no build)

NO `pyproject.toml`, `setup.py`, or `requirements.txt` at top level. Custom `install.py` orchestrator creates a venv and installs dependencies — Python-installer-as-build-system rather than a standard packaging manifest. No lock file. Plain pip inside an installer-managed venv.

### Python version pinning

Python 3.10–3.12 (inclusive upper bound — 3.13+ explicitly unsupported due to Resolve scripting-module ABI incompatibilities). The upper bound is driven by a binary-compat constraint on the upstream Resolve scripting module rather than a project preference.

## Test stack

### Live multi-phase suite against application

5-phase live test suite against a running Resolve instance: read-only, destructive, media, AI/ML, advanced. 319 of 324 methods live-tested (98.5%); claimed 319/319 pass rate. Test framework not identified at source level.

## CI

### GitHub Actions

GitHub Actions referenced; specific triggers/jobs not extracted.

## Host integration

### Universal installer covering many hosts

`install.py` writes client-specific JSON config to 10 separate MCP-client config locations in a single invocation; flags `--clients`, `--dry-run`, `--no-venv`, `--full`. Eliminates the per-client setup step.

### Claude Desktop

Supported via the universal installer.

### Claude Code

Supported via the universal installer.

### Cursor

Supported via the universal installer.

### VS Code / VS Code Insiders / Visual Studio family

Supported via the universal installer.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Other 6 of 10 MCP clients covered by the installer (specific list not enumerated here).

## Observability

### None / unspecified

Logging destination/format for the live server not documented in extracted content; test suite measures coverage but the live-server log path was not surfaced.

## Repository layout

### Single-package with auxiliary folders

`install.py`, `src/` (server.py, resolve_mcp_server.py, utils/), `tests/`, `docs/`, `examples/`. No standard Python package manifest at top level.

## Safety and security posture

### Workspace path enforcement (canonicalization)

Path-traversal protection — file-op tools validate paths stay within expected directories.

### Auto-cleanup of temporary export artifacts

Exports are deleted after response encoding, preventing disk bloat. (Cross-role: see *Caching and rate-limiting infrastructure — Auto-cleanup of temporary export artifacts*.)

## Caching and rate-limiting infrastructure

### Auto-cleanup of temporary export artifacts

Exports deleted after response encoding; cross-platform sandbox handling (temp paths redirected for macOS/Linux/Windows).

## Developer ergonomics

### Custom installer-orchestrator

`install.py` replaces both pip and uv roles — `--dry-run`, `--no-venv`, `--full`, `--clients` flags. Primary dev entry point.

### Examples directory with many patterns

`examples/` directory plus `docs/` ship example flows.

## Documentation surface

### README plus docs directory

README plus `docs/` and `examples/` subdirectories.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

v2.1.0 released March 16, 2026.

### Tagged release with version in changelog

Tagged releases on GitHub.
