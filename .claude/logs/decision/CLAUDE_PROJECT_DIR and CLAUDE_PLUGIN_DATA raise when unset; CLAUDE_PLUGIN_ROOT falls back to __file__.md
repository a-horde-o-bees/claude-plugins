# CLAUDE_PROJECT_DIR and CLAUDE_PLUGIN_DATA raise when unset; CLAUDE_PLUGIN_ROOT falls back to __file__

## Purpose

The plugin framework helpers (`plugin.get_project_dir`, `plugin.get_plugin_root`, `plugin.get_plugin_data_dir`) had inconsistent fallback behavior.

## Context

The plugin framework helpers (`plugin.get_project_dir`, `plugin.get_plugin_root`, `plugin.get_plugin_data_dir`) had inconsistent fallback behavior. Earlier code variously used `os.getcwd()`, `Path.cwd()`, or parent walks from arbitrary anchors. During the path resolution lockdown, each variable's fallback was evaluated for legitimacy.

## Decision

- `get_project_dir()` raises when `CLAUDE_PROJECT_DIR` is unset.
- `get_plugin_root()` falls back to `Path(__file__).resolve().parent.parent` when `CLAUDE_PLUGIN_ROOT` is unset.
- `get_plugin_data_dir()` raises when `CLAUDE_PLUGIN_DATA` is unset.

## Rationale

**Project dir is intrinsically about user intent.** Not inferable from the working directory — a user running a command from the wrong directory would silently populate state in the wrong project tree. Every legitimate caller sets the variable explicitly.

**Plugin root is intrinsically about code location.** `plugin/__init__.py` lives at a fixed position relative to the plugin package root across dev, install cache, and any other install location. The `__file__` walk is a computation from a stable anchor, not a guess.

**Plugin data dir has no sensible guess.** Claude Code-managed persistent storage survives plugin version upgrades and is not derivable from any other path.

## Consequences

- Hooks that run outside Claude Code (for debug) now raise — acceptable.
- Test fixtures set `CLAUDE_PROJECT_DIR` via `monkeypatch.setenv`.
- MCP subprocesses bootstrap `CLAUDE_PROJECT_DIR` from cwd at import time via `servers/_helpers.py` — Claude Code guarantees MCP cwd = project root but does not propagate the env var and does not expand `${CLAUDE_PROJECT_DIR}` in `.mcp.json` env blocks. Documented as a scope-limited exception in `mcp-server.md`.
- The silent wrong-cwd failure mode is eliminated everywhere the helper is used.
