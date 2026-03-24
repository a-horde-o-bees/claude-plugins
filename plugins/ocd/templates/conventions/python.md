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

## Post-Refactor Cleanup

After moves, renames, or structural changes:

1. Remove `__pycache__` directories outside `.venv/` — orphaned `.pyc` files from deleted/moved `.py` files persist indefinitely
2. Verify no orphaned `*.egg-info` directories outside `.venv/` and `.gitignore`
3. Run test suite — confirms no broken imports from moved modules
4. Search for old paths in documentation and comments
