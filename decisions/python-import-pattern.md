# Python Import Pattern

## Context

Plugin scripts live in directories like `plugins/ocd/skills/navigator/scripts/` and are invoked three ways:

1. **Direct execution** — `python3 plugins/.../scripts/navigator_cli.py` (Claude Code hooks, agent bash calls). Python adds the script's directory to `sys.path[0]` automatically.
2. **Dynamic loading** — `plugin.py`'s `_load_module()` loads `_init.py` files by path, explicitly adding the parent directory to `sys.path`.
3. **Pytest** — `pyproject.toml` `pythonpath` config adds script directories to `sys.path`.

All three paths result in the same thing: the scripts directory is on `sys.path`, and bare imports (`import _db`, `import research`) resolve correctly.

## Decision

**Use bare imports with `# type: ignore[import-not-found]`.** No relative imports, no `try/except ImportError` fallback pattern. Naming collisions between plugins with same-named internal modules (`_db.py`) are prevented by test infrastructure: per-plugin `conftest.py` files add only that plugin's scripts directory to `sys.path`, and the global `pythonpath` in `pyproject.toml` excludes directories that would collide.

## Options Considered

### Bare imports with `# type: ignore` (original)

```python
import _db as db  # type: ignore[import-not-found]
```

Works at runtime in all three invocation paths. Pyright can't resolve the imports because it doesn't know about runtime `sys.path` state. The `# type: ignore` comments suppress warnings but also suppress legitimate type errors on those lines.

**Result:** Functional but noisy. Self-evaluation conformity agents flagged pyright warnings as issues and attempted fixes.

### `try/except ImportError` with relative imports (attempted)

```python
try:
    from . import _db as db
except ImportError:
    import _db as db  # type: ignore[import-not-found]
```

Added to match navigator's existing pattern. Relative imports (`from .`) work when the module is loaded as part of a package with `__init__.py`. Falls back to bare imports for direct execution.

**Result:** Added complexity without benefit. Relative imports only work when loaded as a package (which never happens in production — no code runs `from plugins.ocd.skills.navigator.scripts import navigator`). Direct execution and `_load_module` both use bare imports via `sys.path`. The try block always falls through to the except block in production, making the relative import dead code. Pyright still couldn't resolve star imports (`from ._entities import *`) in facade modules.

### Star imports in facade with `try/except` (attempted)

```python
try:
    from ._entities import *  # noqa: F401,F403
    from ._measures import *  # noqa: F401,F403
except ImportError:
    from _entities import *  # noqa: F401,F403  # type: ignore[import-not-found]
    from _measures import *  # noqa: F401,F403  # type: ignore[import-not-found]
```

Added to `research.py` as facade re-exports after splitting `_db.py` into domain modules. CLI imports from `research` (the facade) instead of `_db` directly.

**Result:** Maximum complexity, still broken for pyright. Star imports are opaque to static analysis regardless of `try/except`. Pyright couldn't resolve `research.register_entity()` because it can't see through `from _entities import *`. The facade pattern is correct architecturally but the import mechanism doesn't help pyright.

### `pip install -e .` (evaluated, rejected)

Install the scripts directory as a proper Python package so imports resolve natively without `sys.path` manipulation.

**Result:** Rejected. No external dependencies exist (all imports are stdlib). Would add installation complexity for zero runtime benefit. Claude Code's plugin system doesn't support package installation. Would require changes to how `_load_module` works.

### `PYTHONPATH` environment variable (evaluated, rejected)

Set `PYTHONPATH` to include script directories before invocation.

**Result:** Rejected. Claude Code hooks don't pass custom environment variables. Would need wrapper scripts. Doesn't help `_load_module` which computes paths at runtime. Adds fragile external configuration.

### `pyrightconfig.json` with `extraPaths` (evaluated, insufficient alone)

```json
{
    "extraPaths": [
        "plugins/ocd/scripts",
        "plugins/ocd",
        "plugins/blueprint/skills/research/scripts"
    ]
}
```

Tells pyright the same directories as pytest's `pythonpath`. Would resolve bare imports for pyright.

**Result:** Would fix pyright, but bare imports have a deeper problem — naming collisions. Multiple plugins have `_db.py`, and when both directories are on `sys.path` (which `extraPaths` and `pythonpath` both do), `import _db` finds the wrong one. See "Bare imports" entry above.

### Per-plugin `conftest.py` with `sys.path` setup (evaluated, rejected)

Each plugin's test directory gets a `conftest.py` that adds only its scripts directory to `sys.path`. Removes the global `pythonpath` from `pyproject.toml`.

**Result:** Rejected. Pytest collects ALL conftest files during test collection before running any tests. All plugins' script directories end up on `sys.path` simultaneously, recreating the naming collision. Insertion order (`sys.path.insert(0, ...)`) doesn't help because `--import-mode=importlib` may resolve through the package hierarchy before checking `sys.path` order.

### Renaming `_db.py` to unique names (evaluated, deferred)

Rename to `_navigator_db.py` and `_research_db.py` to eliminate the collision at the source.

**Result:** Would work but changes all import statements across both plugins. Deferred — the try/except pattern works and the rename blast radius is large for a test-only issue.

## Key Insight

The import problem is a static analysis gap AND a test infrastructure concern. Pyright cannot see runtime `sys.path` — `# type: ignore` handles this. Multiple plugins with same-named internal modules (`_db.py`) collide when their directories coexist on `sys.path` — per-plugin `conftest.py` handles this by isolating each plugin's test path.

## Guard Against Recurrence

If import issues arise:

1. Do NOT add `try/except ImportError` with relative imports — tried and rejected; adds dead code in production where bare imports always work
2. If a naming collision surfaces in tests, check that the colliding directory is NOT in `pyproject.toml` `pythonpath` — use per-plugin `conftest.py` instead
3. Self-evaluation conformity agents should NOT flag `# type: ignore[import-not-found]` on bare imports as a violation — it is the documented standard
4. If collisions become unmanageable, rename internal modules to be unique per plugin (e.g., `_navigator_db.py`, `_research_db.py`) as a permanent fix
