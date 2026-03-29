# Python Import Pattern

## Context

Plugin scripts live in skill packages like `plugins/ocd/skills/navigator/` and are invoked via a launcher (`run.py`) that establishes Python package context. In production, each plugin is installed in its own isolated directory — `CLAUDE_PLUGIN_ROOT` points to one plugin root, and there's never cross-plugin contamination on `sys.path`.

## Decision

**Proper Python packages with relative imports.** Each plugin root has `run.py` that adds the plugin root to `sys.path` and uses `runpy.run_module()` to execute modules with correct `__package__` context. All scripts use relative imports within their package.

**Invocation:** `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator <args>`

**Within-package imports:** `from . import _db`, `from ._db import get_connection`

**Cross-package imports:** `from scripts import plugin` (absolute from plugin root)

**Testing:** Per-plugin pytest configs with isolated `pythonpath`. Each plugin's tests run with only that plugin's root on `sys.path`, mirroring production isolation. Project-level tests run separately with no plugin paths.

## Options Evaluated and Rejected

### Bare imports with `# type: ignore` (original)

`import _db as db  # type: ignore[import-not-found]`

Worked at runtime but caused naming collisions when multiple plugins had same-named modules (`_db.py`) on `sys.path` simultaneously during pytest. Pyright couldn't resolve imports.

### `try/except ImportError` with relative imports

```python
try:
    from . import _db as db
except ImportError:
    import _db as db  # type: ignore[import-not-found]
```

Added dead code in production (bare imports always work via `sys.path[0]`). Doubled every import statement. Pyright still couldn't resolve star imports.

### Per-plugin conftest.py sys.path isolation

Each test directory got `conftest.py` adding its plugin's scripts dir to `sys.path`. Failed because ALL conftest files run during pytest collection — multiple directories end up on `sys.path` simultaneously.

### `pyrightconfig.json` extraPaths (evaluated for use with bare imports)

Would fix pyright but didn't address the test collision. Naming collisions are a runtime problem, not just a static analysis gap.

### Renaming `_db.py` to unique names

Would eliminate collisions but commits to a system where no two plugins can share internal module names. Doesn't scale.

### `pip install -e .`

No external dependencies exist. Would add installation complexity for zero runtime benefit. Claude Code plugins don't support package installation.

## Key Insight

The collision is a development repo artifact. In production, each plugin is isolated — `CLAUDE_PLUGIN_ROOT` points to one plugin, and `sys.path[0]` has only that plugin's directory. The correct solution mirrors production: each plugin is its own package namespace, tests run in isolation per-plugin, and `run.py` bridges Claude Code's `python3 path/to/script` invocation with Python's package system.
