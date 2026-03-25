---
type: template
---

# Python Conventions

## Code Style

### Typing

All function signatures include type hints for parameters and return values. Use `|` union syntax over `Optional[]` (Python 3.10+).

```python
def find_record(name: str, include_deleted: bool = False) -> dict | None:
```

Forward references and cross-module types — use `from __future__ import annotations` with `TYPE_CHECKING` guard. Makes all annotations lazy strings, avoiding circular imports and forward reference issues. Never use quoted string annotations (`-> "ClassName"`) — `__future__` import handles this uniformly.

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from module_lib import ModuleAPI

def process_data(client: ModuleAPI, source: str) -> None:
```

Type aliases — define aliases when same union type appears across multiple function signatures in module. Keep aliases in module that uses them, not centralized.

Use `@dataclass` for value objects that group related fields. Prefer over plain dicts when shape is known and reused.

### Logging

Every module that does I/O, makes network calls, or has decision points worth tracing uses module-level logger:

```python
import logging
logger = logging.getLogger(__name__)
```

- Use `logger.info/warning/debug/error` — never `logging.info` (root logger) or `print()` for operational output
- Only CLI/presentation layers use `print()` and `input()` for user-facing output
- No `logging.basicConfig()` in libraries or modules — only entry point configures logging

### Path Handling

Use `pathlib.Path` throughout:

- Function parameters that represent filesystem paths accept `Path`, not `str` — push `str`-to-`Path` conversion to process boundaries (CLI argument parsing, environment variables, subprocess interfaces)
- Functions that return filesystem paths return `Path`
- Use `/` operator for path construction, not string concatenation or `os.path.join()`
- Use `Path` methods (`resolve()`, `expanduser()`, `is_absolute()`, `parents`) over `os.path` equivalents
- Exception: pattern-matching interfaces (glob patterns, regex on paths) operate on `str` representations since they match text, not filesystem objects

When user input is interpolated into file paths, validate containment with `Path.is_relative_to()` to prevent path traversal.

### Error Handling

Validation logic raises exceptions — no `print()` + `sys.exit()` in non-CLI code. CLI dispatch layer catches errors and exits cleanly with error message.

## Module Decomposition

### When to Decompose

Extract internal modules when a file contains distinct functional domains — groups of functions that serve different purposes and have minimal cross-references. Decomposition is driven by functional boundaries, not line counts. A 600-line file with one cohesive domain stays together; a 300-line file with two independent domains splits.

### Internal Module Pattern

`_{purpose}.py` — underscore prefix signals not standalone. Consumers import from parent module (`{name}.py`) or CLI (`{name}_cli.py`), not directly from underscored modules. Same-package files import via `from . import _{purpose}` or `from ._{purpose} import {function}`.

```
scripts/
  navigator.py          # Facade — public interface, imports from internal modules
  navigator_cli.py      # CLI — dispatches to navigator.py
  _scanner.py           # Internal — filesystem scanning domain
  _db.py                # Internal — database schema and connection
  skill_resolver.py     # Separate module — independent domain, own CLI subcommands
```

### Standard Internal Module Types

`_constants.py` — shared configuration values (thresholds, ordering lists, magic numbers) used across module files. Create when constants are shared between parent module and CLI or between multiple internal modules.

`_helpers.py` — pure utility functions with no dependency on module state. Functions take data in and return data out. Create when utility functions are shared across multiple files in the package.

`_init.py` — initialization and status logic. Contains `init()` for infrastructure setup and `status()` for health checks. CLI exposes these as `init` and `status` subcommands. Standard for any skill that requires infrastructure (database, deployed files, configuration).

`_{domain}.py` — focused on single functional domain. Named for what it does (`_scanner.py`, `_db.py`, `_formatter.py`). Create when a functional domain within a module has clear boundaries and its functions are primarily called by each other or by the parent facade.

### Facade Role

Parent module (`{name}.py`) stays as public interface after decomposition. Imports from internal modules and re-exports or delegates. CLI and external consumers continue importing from parent module — internal module structure is invisible to callers.

```python
# navigator.py — facade after decomposition
from ._db import get_connection, init_db, SCHEMA
from ._scanner import scan_path

def describe_path(db_path: str, target_path: str) -> str:
    """Uses get_connection from _db, stays in facade."""
    ...
```

### Separate Module vs Internal Module

Use `_{purpose}.py` (internal) when functions exist to support the parent module and have no independent consumers. Use `{name}.py` (separate module) when the domain has its own CLI subcommands, independent tests, or is consumed by multiple parent modules. Example: `skill_resolver.py` is separate because navigator CLI exposes its subcommands directly; `_scanner.py` is internal because only `navigator.py` calls its functions.

### CLI Boundary

Decomposition of `{name}.py` is invisible to `{name}_cli.py`. CLI always imports from facade (`{name}.py`), never from internal `_{purpose}.py` modules. Separate modules with own CLI subcommands are imported directly by the CLI alongside the facade.

## Post-Refactor Cleanup

After moves, renames, or structural changes:

1. Remove `__pycache__` directories outside `.venv/` — orphaned `.pyc` files from deleted/moved `.py` files persist indefinitely
2. Verify no orphaned `*.egg-info` directories outside `.venv/` and `.gitignore`
3. Run test suite — confirms no broken imports from moved modules
4. Search for old paths in documentation and comments
