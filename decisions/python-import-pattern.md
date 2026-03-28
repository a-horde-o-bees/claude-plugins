# Python Import Pattern

## Context

Plugin scripts live in directories like `plugins/ocd/skills/navigator/scripts/` and are invoked three ways:

1. **Direct execution** — `python3 plugins/.../scripts/navigator_cli.py` (Claude Code hooks, agent bash calls). Python adds the script's directory to `sys.path[0]` automatically.
2. **Dynamic loading** — `plugin.py`'s `_load_module()` loads `_init.py` files by path, explicitly adding the parent directory to `sys.path`.
3. **Pytest** — `pyproject.toml` `pythonpath` config adds script directories to `sys.path`.

All three paths result in the same thing: the scripts directory is on `sys.path`, and bare imports (`import _db`, `import research`) resolve correctly.

## Decision

**Use bare imports.** No relative imports, no `try/except ImportError` fallback pattern. Pyright warnings about unresolved imports are suppressed via `pyrightconfig.json` `extraPaths` (same directories as pytest's `pythonpath`).

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

### `pyrightconfig.json` with `extraPaths` (selected)

```json
{
    "extraPaths": [
        "plugins/ocd/scripts",
        "plugins/ocd",
        "plugins/blueprint/skills/research/scripts"
    ]
}
```

Tells pyright the same thing `pyproject.toml` tells pytest: these directories are on the import path. Bare imports resolve without `# type: ignore`.

**Result:** Correct solution. Matches reality (these directories ARE on `sys.path` at runtime). No code changes needed. Pyright resolves bare imports. No `try/except` complexity. No `# type: ignore` noise. Self-evaluation conformity agents won't flag resolved imports as issues.

## Key Insight

All three invocation paths (direct execution, `_load_module`, pytest) add the scripts directory to `sys.path`. The import "problem" was only a static analysis gap — pyright didn't know what the runtime knows. The fix belongs in pyright configuration, not in import patterns.

## Guard Against Recurrence

If pyright warnings about unresolved imports reappear:

1. Check `pyrightconfig.json` `extraPaths` — the directory may be missing
2. Do NOT add `try/except ImportError` with relative imports — this was tried and adds dead code
3. Do NOT add `# type: ignore[import-not-found]` — this suppresses legitimate errors too
4. If a new scripts directory is added, add it to both `pyproject.toml` `pythonpath` AND `pyrightconfig.json` `extraPaths`
