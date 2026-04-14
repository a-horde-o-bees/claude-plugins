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

Annotations resolve at import time by default. Three disciplines apply when the default does not fit:

- **Conditional `__future__` import.** Add `from __future__ import annotations` only when forward references or circular imports require it. Files with no forward refs or cross-module type dependencies carry no future import — it is not a default.
- **`TYPE_CHECKING` pairing.** When the file has `from __future__ import annotations` and needs to import a module solely for annotations, put that import under `if TYPE_CHECKING:`. Keeps type-only imports out of the runtime import graph.
- **No quoted annotations.** Never use `-> "ClassName"` string form. When a forward reference needs lazy resolution, `from __future__ import annotations` handles it uniformly; the conditional rule above still applies.

```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from module_lib import ModuleAPI

def process_data(client: ModuleAPI, source: str) -> None:
```

Boolean parameters default to `False`. A `True` default requires callers to include the parameter only to turn it off — name the parameter so the opt-in meaning reads naturally when set to `True` (e.g. `keep_orphans=False` not `clear_orphans=True`).

**Type aliases — defined locally.** Define an alias when the same union type appears across multiple function signatures in the same module. Do not centralize aliases in a shared types module — keep them in the module that uses them, so consumers of one module do not pull in type definitions from another.

Use `@dataclass` for value objects that group related fields. Prefer over plain dicts when shape is known and reused.

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

- `plugin.get_project_dir()` — resolves `CLAUDE_PROJECT_DIR`; falls back to `git rev-parse --show-toplevel` when unset, which is deterministic within any checkout or worktree of the same repo; raises when neither the env var is set nor git root is discoverable
- `plugin.get_plugin_root()` — resolves `CLAUDE_PLUGIN_ROOT`; falls back to a deterministic walk from `plugin/__init__.py`'s own `__file__` position, which is intrinsic to the code layout
- `plugin.get_plugin_data_dir()` — resolves `CLAUDE_PLUGIN_DATA`; raises when unset because per-plugin persistent storage is Claude Code–managed and inferable from nothing

All three return absolute canonical paths (`Path.resolve()`). Absolute is required for disk I/O — callers that need display-friendly paths compute `relative_to()` at the point of use. The project's relative-path convention is preserved: database entries, tool output, and embedded command paths remain project-relative; the absolute root is local plumbing for reading files.

Do not:

- Fall back to `os.getcwd()` when `CLAUDE_PROJECT_DIR` is unset — silent cwd fallback corrupts state when run from the wrong directory
- Walk `path.parents[N]` from arbitrary paths to derive project or plugin root — fragile and breaks when layout changes
- Accept `project_dir` or `plugin_root` as a function argument when the caller would only be re-resolving it — resolve shared paths internally via the helpers

One documented exception: MCP server subprocesses launched by Claude Code bootstrap `CLAUDE_PROJECT_DIR` from cwd at import time via `servers/_helpers.py`, because Claude Code guarantees the MCP server cwd matches the project directory but does not propagate the env var automatically and does not expand variable references in `.mcp.json` env blocks. See `mcp-server.md` *MCP Subprocess Environment Bootstrap*. This is the only place cwd is permitted as a project-directory source.

### Error Handling

- **Validation raises exceptions.** Non-CLI code signals invalid state by raising — never by calling `print()` + `sys.exit()`. Library and facade code throws; the caller decides what to do with the exception.
- **CLI catches only to add agent-actionable context.** Per design-principles *Agent-First Interfaces*, error output includes corrective guidance. The CLI layer wraps facade calls where it can add value — a corrective next-step command, domain-specific context, or translation from a generic error into domain terms. Where the raised message is already actionable, let the exception propagate — Python tracebacks are diagnostic and should not be suppressed for cosmetic reasons.

## Module Decomposition

### When to Decompose

Extract internal modules when a file contains distinct functional domains — groups of functions that serve different purposes and have minimal cross-references. Decomposition is driven by functional boundaries, not line counts. A 600-line file with one cohesive domain stays together; a 300-line file with two independent domains splits.

### Internal Module Pattern

- **Underscore prefix signals not standalone.** A file named `_{purpose}.py` is internal to its package — not imported by external consumers, not exposed as a separate entry point. The prefix is load-bearing, not a stylistic choice.
- **Consumers import from the package, not from internals.** External code reaches for `from pkg import get_connection` or `from pkg import *`, never `from pkg._db import get_connection`. The package's `__init__.py` facade re-exports internal names. Exception: unit tests that exercise underscore-prefixed helpers (`_compute_hash`, `_parse_frontmatter`) import directly from the defining internal module — the facade does not re-export private names, so there is no other path to them. Public names used in tests still come through the facade.
- **Same-package files use relative imports.** Within a package, sibling modules use `from . import _db` or `from ._db import get_connection`. Absolute imports from sibling modules break when the package is relocated or the import graph is rearranged.

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
- `_init.py` — initialization and status logic; contains `init()` for infrastructure setup and `status()` for health checks; CLI exposes these as `init` and `status` subcommands; standard for any package that requires infrastructure (database, deployed files, configuration). Full interface contract below in *Init/Status Contract*
- `_{domain}.py` — focused on single functional domain; named for what it does (`_parser.py`, `_storage.py`, `_formatter.py`); create when a functional domain within a module has clear boundaries and its functions are primarily called by each other or by the parent facade

### Init/Status Contract

Packages that declare infrastructure (database, deployed files, configuration) implement `init()` and `status()` in a `_init.py` internal module. The functions follow a deterministic contract so the plugin framework can aggregate outputs across every init/status-capable package in the plugin.

**Interface.**

Both functions return `{"files": [...], "extra": [...]}`:

- `init(force=False)` — deploy infrastructure; `force=True` rebuilds from scratch
- `status()` — report infrastructure state

Entry points take only their own domain-specific arguments. Project and plugin paths are resolved internally via the plugin framework helpers (`plugin.get_project_dir()`, `plugin.get_plugin_root()`, `plugin.get_plugin_data_dir()`) — see *Project, Plugin, and Data Directory Resolution*. Never accept those paths as parameters.

`files` entries: `{"path": str, "before": str, "after": str}` — relative deployed path with state transitions (`absent`, `current`, `divergent`).

`extra` entries: `{"label": str, "value": str}` — additional status lines rendered as aligned columns.

**Status labels.**

Two standard labels cover every state:

- `overall status` — single line summarizing infrastructure state
- `action needed` — copy-pastable slash command for next step

**Database status pattern.**

Packages with SQLite databases report through a deterministic state machine:

| State | `overall status` | `action needed` |
|-------|-----------------|-----------------|
| DB file absent | `not initialized` | `/{plugin}:init` |
| DB file present, schema divergent | `error — divergent schema` | `/{plugin}:init --force` |
| DB file present, schema valid | `operational — {metric summary}` | `/{plugin}:{skill-command}` |
| DB file present, SQL error | `error — {error message}` | `/{plugin}:init --force` |

Schema validation uses subset check — expected tables must all be present; additional tables are not an error:

```python
expected_tables = {"records", "record_details", "record_tags"}
actual_tables = {row[0] for row in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table'",
).fetchall()}
if not expected_tables.issubset(actual_tables):
    # divergent schema
```

**Metric summary.**

Operational status includes a metric summary with counts relevant to the domain. Format: `operational — {count} {noun}, {count} {noun}, ...`

- **Noun choice is domain-specific.** Use the domain's natural unit — entities, entries, notes, events, records — rather than generic "items" or "rows"
- **Metric count balances signal against noise.** Include enough metrics for the user to understand infrastructure health at a glance without querying. Stop short of enumerating every table's row count — pick the counts that answer "is this healthy and actively in use?"

**Action needed format.**

- **Always present in status output.** Every state returns an `action needed` line, including the operational state — the value tells the user what the natural next step is, not whether there is a problem
- **Value is a copy-pastable slash command.** No prose, no "Run" prefix, no parenthetical explanations. The user pastes the value directly
- Not initialized → `/{plugin}:init`
- Error states → `/{plugin}:init --force`
- Operational → `/{plugin}:{skill-command}` (primary skill for this infrastructure)

### Facade Role

- **`__init__.py` is the public interface.** After a package is decomposed into internal modules, `__init__.py` remains the sole entry point external code imports from. Decomposition is an implementation detail — the facade shape does not change.
- **Facade assembles via star imports.** `__init__.py` uses `from ._internal import *` to fold each internal module's public names into the package namespace. Moving a function between internal modules does not require caller updates.
- **Underscore prefix controls what star imports export.** Functions starting with `_` do not cross star imports; public functions do. This replaces `__all__` — the underscore convention is the single source of truth for public/private.
- **CLI imports from the package, not from internals.** `__main__.py` uses `from . import *` to consume the facade. CLI code never imports from `_internal.py` modules — internal structure is invisible to CLI just as it is to external callers.

```python
# __init__.py — facade after decomposition
from ._storage import *  # noqa: F403
from ._parser import *  # noqa: F403

def process_path(db_path: str, target_path: str) -> str:
    """Uses get_connection from _storage, stays in facade."""
    ...
```

### Hook Scripts

Hook scripts are standalone modules invoked directly by `hooks.json` configuration — no package wrapping, no `__init__.py` or `__main__.py` facade. Each hook script is a single `.py` file with its own entry point (e.g., `auto_approval.py`, `convention_gate.py`) that Claude Code invokes via interpreter prefix.

### Script Invocation

Python scripts are invoked via interpreter prefix (`python3 script.py`), not via shebangs with execute permissions.

### Separate Module vs Internal Module

Use `_{purpose}.py` (internal) when functions exist to support the package and have no independent consumers. Use `{name}.py` (separate module) when the domain has its own CLI subcommands, independent tests, or is consumed by multiple packages. Example: `client.py` is separate because the CLI exposes its subcommands directly; `_parser.py` is internal because only the facade calls its functions.

### CLI Boundary

- **Decomposition is invisible to CLI.** `__main__.py` sees `__init__.py` as the package interface. Internal decomposition under the facade (`_db.py`, `_parser.py`, etc.) does not change how CLI code imports or calls facade functions.
- **CLI imports the facade via star import.** Use `from . import *` to pull in all public names in one line. Never import from internal `_{purpose}.py` modules — the underscore prefix is the boundary, and CLI is an external consumer.
- **Separate modules imported directly.** A separate module (`{name}.py`, no underscore) that contributes its own CLI subcommands is imported directly by the CLI alongside the facade, because its public surface is independent of the facade's.

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

- Resolve import paths through package structure, not `sys.path` manipulation
- Resolve type errors rather than suppressing with `# type: ignore`

## Testing

### File Naming

Test files use `test_` prefix: `test_module.py`, `test_client.py`. Pytest discovers `test_*.py` by default. Do not use `*_test.py` suffix convention.

Test directories contain `__init__.py` so pytest discovers them as packages — discovery relies on importability.

Shared fixtures live in `conftest.py` at the appropriate directory level — the closest directory containing all tests that use the fixture. Fixtures declared too high leak into unrelated tests; declared too low duplicate across test directories.

### Test Structure

**Group related tests by class.** When a set of tests exercises a single function or module boundary, wrap them in a `TestX` class. Shared fixtures, setup, and naming context apply uniformly across the class.

**Test method names state what is verified.** Use descriptive names like `test_prefix_attack_blocked`, `test_cycle_detection_raises`, `test_empty_input_returns_zero`. The reader of a failure output should understand what broke from the test name alone.

Fixtures provide isolated test state (temp directories, databases, environment variables). Prefer `tmp_path` and `monkeypatch` builtins over manual setup/teardown.

### Git Worktree Fixtures

Integration tests requiring git worktree isolation (see testing convention) use a session-scoped pytest fixture:

- Session-scoped fixture in `conftest.py` creates and tears down the worktree
- Fixture yields the worktree path
- Per-test setup/teardown handles test-specific state (temp directories, staged files) within the worktree
- `conftest.py` in the integration test directory owns the fixture

## Post-Refactor Cleanup

After moves, renames, or structural changes:

1. Remove `__pycache__` directories outside `.venv/` — orphaned `.pyc` files from deleted/moved `.py` files persist indefinitely
2. Verify no orphaned `*.egg-info` directories outside `.venv/` and `.gitignore`
3. Run test suite — confirms no broken imports from moved modules
4. Search for old paths in documentation and comments
