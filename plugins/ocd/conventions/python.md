---
includes: "*.py"
governed_by:
  - .claude/rules/ocd/design-principles.md
---

# Python Conventions

Code style, module structure, and import patterns for Python files in this project.

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
- When user input is interpolated into file paths, validate containment with `Path.is_relative_to()` to prevent path traversal

### Project, Plugin, and Data Directory Resolution

Three absolute paths always resolve through the plugin framework helpers in `plugin/__init__.py` — never through direct environment reads, never from `os.getcwd()`, never through parent walks from arbitrary paths:

- `plugin.get_project_dir()` — resolves `CLAUDE_PROJECT_DIR`; raises when unset because project identity is not inferable from working directory
- `plugin.get_plugin_root()` — resolves `CLAUDE_PLUGIN_ROOT`; falls back to a deterministic walk from `plugin/__init__.py`'s own `__file__` position, which is intrinsic to the code layout
- `plugin.get_plugin_data_dir()` — resolves `CLAUDE_PLUGIN_DATA`; raises when unset because per-plugin persistent storage is Claude Code–managed and inferable from nothing

All three return absolute canonical paths (`Path.resolve()`). Absolute is required for disk I/O — callers that need display-friendly paths compute `relative_to()` at the point of use. The project's relative-path convention is preserved: database entries, tool output, and embedded command paths remain project-relative; the absolute root is local plumbing for reading files.

Never:

- `os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())` — silent cwd fallback corrupts state when run from the wrong directory
- `path.parents[N]` walks from arbitrary paths (e.g., a database path) to derive project or plugin root — fragile and breaks when layout changes
- Accept `project_dir` or `plugin_root` as a function argument when the caller would only be re-resolving it — the helpers are the single source of truth. Skill entry points (`init`, `status`) take only their own skill-specific arguments (e.g., `force`); they resolve shared paths internally

One documented exception: MCP server subprocesses launched by Claude Code bootstrap `CLAUDE_PROJECT_DIR` from cwd at import time via `servers/_helpers.py`, because Claude Code guarantees the MCP server cwd matches the project directory but does not propagate the env var automatically and does not expand variable references in `.mcp.json` env blocks. See `mcp-server.md` *MCP Subprocess Environment Bootstrap*. This is the only place cwd is permitted as a project-directory source.

### Error Handling

Validation logic raises exceptions — no `print()` + `sys.exit()` in non-CLI code. CLI dispatch layer catches errors and exits cleanly with error message.

## Module Decomposition

### When to Decompose

Extract internal modules when a file contains distinct functional domains — groups of functions that serve different purposes and have minimal cross-references. Decomposition is driven by functional boundaries, not line counts. A 600-line file with one cohesive domain stays together; a 300-line file with two independent domains splits.

### Internal Module Pattern

`_{purpose}.py` — underscore prefix signals not standalone. Consumers import from the package (`from . import *`) or specific names (`from . import get_connection`), not directly from underscored modules. Same-package files use relative imports (`from . import _db`, `from ._db import get_connection`).

```
skill-name/
  __init__.py           # Facade — public interface, imports from internal modules
  __main__.py           # CLI — dispatches to facade via `from . import *`
  _parser.py            # Internal — input parsing domain
  _storage.py           # Internal — database schema and connection
  client.py             # Separate module — independent domain, own CLI subcommands
```

### Standard Internal Module Types

- `_constants.py` — shared configuration values (thresholds, ordering lists, magic numbers) used across module files; create when constants are shared between parent module and CLI or between multiple internal modules
- `_helpers.py` — pure utility functions with no dependency on module state; functions take data in and return data out; create when utility functions are shared across multiple files in the package
- `_init.py` — initialization and status logic; contains `init()` for infrastructure setup and `status()` for health checks; CLI exposes these as `init` and `status` subcommands; standard for any skill that requires infrastructure (database, deployed files, configuration)
- `_{domain}.py` — focused on single functional domain; named for what it does (`_parser.py`, `_storage.py`, `_formatter.py`); create when a functional domain within a module has clear boundaries and its functions are primarily called by each other or by the parent facade

### Facade Role

Package `__init__.py` stays as public interface after decomposition. Imports from internal modules and re-exports or delegates. CLI (`__main__.py`) imports from the package via `from . import *` — internal module structure is invisible to callers.

```python
# __init__.py — facade after decomposition
from ._storage import get_connection, init_db, SCHEMA
from ._parser import parse_input

def process_path(db_path: str, target_path: str) -> str:
    """Uses get_connection from _storage, stays in facade."""
    ...
```

### Hook Scripts

Hook scripts are standalone modules invoked directly by `hooks.json` configuration — no package wrapping, no `__init__.py` or `__main__.py` facade. Each hook script is a single `.py` file with its own entry point (e.g., `auto_approval.py`, `convention_gate.py`) that Claude Code invokes via interpreter prefix.

### Script Invocation

Python scripts are invoked via interpreter prefix (`python3 script.py`), not via shebangs with execute permissions. No `#!/usr/bin/env python3` headers. No `chmod +x` on `.py` files.

### Separate Module vs Internal Module

Use `_{purpose}.py` (internal) when functions exist to support the package and have no independent consumers. Use `{name}.py` (separate module) when the domain has its own CLI subcommands, independent tests, or is consumed by multiple packages. Example: `client.py` is separate because the CLI exposes its subcommands directly; `_parser.py` is internal because only the facade calls its functions.

### CLI Boundary

Decomposition of `__init__.py` is invisible to `__main__.py`. CLI always imports from the package (`from . import *`), never from internal `_{purpose}.py` modules. Separate modules with their own CLI subcommands are imported directly by the CLI alongside the facade.

### Import Pattern

Skill packages use relative imports. Each plugin's `run.py` launcher establishes proper `__package__` context via `runpy.run_module()`. Plugin infrastructure (`plugin.py`) loads skill `_init.py` modules via `importlib.import_module()` with full package path.

Within-package:

```python
from . import _db
from ._db import get_connection
from . import *  # __main__.py importing facade
```

Cross-package (e.g., skill `_init.py` referencing plugin framework):

```python
import plugin
```

- No `sys.path` manipulation in individual scripts
- No `# type: ignore` comments

## Testing

### File Naming

Test files use `test_` prefix: `test_module.py`, `test_client.py`. Pytest discovers `test_*.py` by default. Do not use `*_test.py` suffix convention.

Test directories contain `__init__.py` for proper package structure. Shared fixtures live in `conftest.py` at appropriate directory level.

### Test Structure

Group related tests by class when testing a single function or module boundary. Use descriptive test method names that state what is being verified: `test_prefix_attack_blocked`, `test_cycle_detection_raises`.

Fixtures provide isolated test state (temp directories, databases, environment variables). Prefer `tmp_path` and `monkeypatch` builtins over manual setup/teardown.

### Git Worktree Fixtures

Integration tests requiring git worktree isolation (see testing convention) use a session-scoped pytest fixture:

- Session-scoped fixture in `conftest.py` creates a detached worktree from HEAD via `git worktree add <path> HEAD --detach`
- Fixture yields the worktree path; teardown removes it via `git worktree remove --force`
- Per-test setup/teardown handles test-specific state (temp directories, staged files) within the worktree
- `conftest.py` in the integration test directory owns the fixture

## Post-Refactor Cleanup

After moves, renames, or structural changes:

1. Remove `__pycache__` directories outside `.venv/` — orphaned `.pyc` files from deleted/moved `.py` files persist indefinitely
2. Verify no orphaned `*.egg-info` directories outside `.venv/` and `.gitignore`
3. Run test suite — confirms no broken imports from moved modules
4. Search for old paths in documentation and comments
