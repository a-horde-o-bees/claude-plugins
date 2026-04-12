---
created: 2026-04-11T23:44:30.425047+00:00
---

# Python import pattern: Standard packages with relative imports per-plugin, mirroring production isolation in tests

# Python Import Pattern

## Context

Plugin code lives in packages — skill packages (`skills/navigator/`), plugin infrastructure (`plugin/`), and hook scripts (`hooks/`). Each plugin root has `run.py` that establishes Python package context. In production, each plugin is installed in its own isolated directory — `CLAUDE_PLUGIN_ROOT` points to one plugin root, and there is never cross-plugin contamination on `sys.path`. Cross-plugin naming collisions (e.g., multiple `_db.py` files) are a development repo artifact — in production, each plugin is isolated with only its own directory on `sys.path`.

## Options Considered

**Standard Python packages with relative imports** — `run.py` adds plugin root to `sys.path` and uses `runpy.run_module()` for correct `__package__` context. Plugin infrastructure loads skill `_init.py` via `importlib.import_module()` with full package path. Per-plugin pytest configs with isolated `pythonpath` mirror production isolation.

**Bare imports with `# type: ignore`** — naming collisions when multiple plugins on `sys.path` during pytest. Disqualified: broken in multi-plugin development environments.

**`try/except ImportError` fallback** — dead code in production, doubled every import statement. Disqualified: unnecessary complexity with no production benefit.

**Per-plugin conftest.py sys.path manipulation** — all conftest files run during collection, defeating isolation. Disqualified: pytest collection behavior prevents correct scoping.

**`pyrightconfig.json` extraPaths** — fixed static analysis but not runtime collisions. Disqualified: solves type checking but not the actual import problem.

**Renaming internal modules to unique names** — does not scale across plugins. Disqualified: naming burden grows with each plugin.

**`pip install -e .`** — unnecessary complexity; Claude Code plugins do not support package installation. Disqualified: introduces package management overhead with no benefit.

## Decision

Standard Python packages with relative imports. The correct solution mirrors production: each plugin is its own package namespace, tests run in isolation per-plugin, and `run.py` bridges Claude Code's invocation with Python's package system.

**Invocation:** `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator <args>`

**Within-package imports:** `from . import _db`, `from . import *`

**Cross-package imports:** `import plugin` (absolute from plugin root)

**Testing:** Per-plugin pytest configs with isolated `pythonpath`. Each plugin's tests run with only that plugin's root on `sys.path`, mirroring production isolation. Project-level tests run separately with no plugin paths.

## Consequences

- Enables: standard Python imports with full IDE support, no `# type: ignore` comments, no `sys.path` manipulation in individual scripts, production-mirrored test isolation
- Constrains: each plugin requires its own `pytest.ini` with `pythonpath` setting; `run.py` is the bridge between Claude Code's invocation and Python's package system
- Trade-off: development repo has multiple plugins sharing a directory structure that does not exist in production — per-plugin test isolation is the mitigation
