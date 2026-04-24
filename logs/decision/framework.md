---
log-role: reference
---

# Framework

Decisions governing the plugin framework — shared Python infrastructure every plugin inherits (env-var helpers, import structure, isolation patterns).

## Plugin env vars raise vs fallback

### Context

The plugin framework helpers (`plugin.get_project_dir`, `plugin.get_plugin_root`, `plugin.get_plugin_data_dir`) had inconsistent fallback behavior. Earlier code variously used `os.getcwd()`, `Path.cwd()`, or parent walks from arbitrary anchors. During the path resolution lockdown, each variable's fallback was evaluated for legitimacy.

### Options Considered

**Uniform fallback** — every helper falls back to cwd or a derived guess when its env var is unset. Simple, never raises, preserves old behavior. Rejected: silently corrupts state when code runs from the wrong directory.

**Uniform raise** — every helper raises when its env var is unset. Consistent, but forces computable anchors (plugin root) to carry an env var unnecessarily.

**Per-variable evaluation** — each variable's fallback evaluated against whether a sensible guess exists, and whether a wrong guess silently corrupts state.

### Decision

Per-variable evaluation:

- `get_project_dir()` raises when `CLAUDE_PROJECT_DIR` is unset
- `get_plugin_root()` falls back to `Path(__file__).resolve().parent.parent` when `CLAUDE_PLUGIN_ROOT` is unset
- `get_plugin_data_dir()` raises when `CLAUDE_PLUGIN_DATA` is unset

**Project dir is intrinsically about user intent.** Not inferable from the working directory — a user running a command from the wrong directory would silently populate state in the wrong project tree. Every legitimate caller sets the variable explicitly.

**Plugin root is intrinsically about code location.** `plugin/__init__.py` lives at a fixed position relative to the plugin package root across dev, install cache, and any other install location. The `__file__` walk is a computation from a stable anchor, not a guess.

**Plugin data dir has no sensible guess.** Claude Code-managed persistent storage survives plugin version upgrades and is not derivable from any other path.

### Consequences

- **Enables:** the silent wrong-cwd failure mode is eliminated everywhere the helper is used
- **Constrains:** hooks that run outside Claude Code (for debug) now raise — acceptable
- **Constrains:** test fixtures set `CLAUDE_PROJECT_DIR` via `monkeypatch.setenv`
- **Constrains:** MCP subprocesses bootstrap `CLAUDE_PROJECT_DIR` from cwd at import time via `servers/_helpers.py` — Claude Code guarantees MCP cwd = project root but does not propagate the env var and does not expand `${CLAUDE_PROJECT_DIR}` in `.mcp.json` env blocks. See also: decision/mcp.md ## MCP subprocess bootstraps project dir from cwd

## Relative imports with per-plugin isolation

### Context

Plugin code lives in packages — skill packages (`skills/navigator/`), plugin infrastructure (`plugin/`), and hook scripts (`hooks/`). Each plugin root has `run.py` that establishes Python package context. In production, each plugin is installed in its own isolated directory — `CLAUDE_PLUGIN_ROOT` points to one plugin root, and there is never cross-plugin contamination on `sys.path`. Cross-plugin naming collisions (e.g., multiple `_db.py` files) are a development repo artifact — in production, each plugin is isolated with only its own directory on `sys.path`.

### Options Considered

**Standard Python packages with relative imports** — `run.py` adds plugin root to `sys.path` and uses `runpy.run_module()` for correct `__package__` context. Plugin infrastructure loads skill `_init.py` via `importlib.import_module()` with full package path. Per-plugin pytest configs with isolated `pythonpath` mirror production isolation.

**Bare imports with `# type: ignore`** — naming collisions when multiple plugins on `sys.path` during pytest. Disqualified: broken in multi-plugin development environments.

**`try/except ImportError` fallback** — dead code in production, doubled every import statement. Disqualified: unnecessary complexity with no production benefit.

**Per-plugin conftest.py sys.path manipulation** — all conftest files run during collection, defeating isolation. Disqualified: pytest collection behavior prevents correct scoping.

**`pyrightconfig.json` extraPaths** — fixed static analysis but not runtime collisions. Disqualified: solves type checking but not the actual import problem.

**Renaming internal modules to unique names** — does not scale across plugins. Disqualified: naming burden grows with each plugin.

**`pip install -e .`** — unnecessary complexity; Claude Code plugins do not support package installation. Disqualified: introduces package management overhead with no benefit.

### Decision

Standard Python packages with relative imports. The correct solution mirrors production: each plugin is its own package namespace, tests run in isolation per-plugin, and `run.py` bridges Claude Code's invocation with Python's package system.

- **Invocation:** `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator <args>`
- **Within-package imports:** `from . import _db`, `from . import *`
- **Cross-package imports:** `import plugin` (absolute from plugin root)
- **Testing:** per-plugin pytest configs with isolated `pythonpath`. Each plugin's tests run with only that plugin's root on `sys.path`, mirroring production isolation. Project-level tests run separately with no plugin paths.

### Consequences

- **Enables:** standard Python imports with full IDE support, no `# type: ignore` comments, no `sys.path` manipulation in individual scripts, production-mirrored test isolation
- **Constrains:** each plugin requires its own `pytest.ini` with `pythonpath` setting; `run.py` is the bridge between Claude Code's invocation and Python's package system
- **Trade-off:** development repo has multiple plugins sharing a directory structure that does not exist in production — per-plugin test isolation is the mitigation
