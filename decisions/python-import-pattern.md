# Python Import Pattern

## Context

Plugin code lives in packages — skill packages (`skills/navigator/`), plugin infrastructure (`plugin/`), and hook scripts (`hooks/`). Each plugin root has `run.py` that establishes Python package context. In production, each plugin is installed in its own isolated directory — `CLAUDE_PLUGIN_ROOT` points to one plugin root, and there's never cross-plugin contamination on `sys.path`.

## Decision

**Standard Python packages with relative imports.** `run.py` adds the plugin root to `sys.path` and uses `runpy.run_module()` to execute modules with correct `__package__` context. Plugin infrastructure loads skill `_init.py` modules via `importlib.import_module()` with full package path.

**Invocation:** `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator <args>`

**Within-package imports:** `from . import _db`, `from . import *`

**Cross-package imports:** `import plugin` (absolute from plugin root)

**Testing:** Per-plugin pytest configs with isolated `pythonpath`. Each plugin's tests run with only that plugin's root on `sys.path`, mirroring production isolation. Project-level tests run separately with no plugin paths.

## Key Insight

Cross-plugin naming collisions (e.g., multiple `_db.py` files) are a development repo artifact. In production, each plugin is isolated — `CLAUDE_PLUGIN_ROOT` points to one plugin, and `sys.path` has only that plugin's directory. The correct solution mirrors production: each plugin is its own package namespace, tests run in isolation per-plugin, and `run.py` bridges Claude Code's invocation with Python's package system.

## Rejected Alternatives

- **Bare imports with `# type: ignore`** — naming collisions when multiple plugins on `sys.path` during pytest
- **`try/except ImportError` fallback** — dead code in production, doubled every import statement
- **Per-plugin conftest.py sys.path manipulation** — all conftest files run during collection, defeating isolation
- **`pyrightconfig.json` extraPaths** — fixed static analysis but not runtime collisions
- **Renaming internal modules to unique names** — doesn't scale across plugins
- **`pip install -e .`** — unnecessary complexity, Claude Code plugins don't support package installation
