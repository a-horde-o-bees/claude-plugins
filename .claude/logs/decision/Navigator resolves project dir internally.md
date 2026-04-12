# Navigator resolves project dir internally

## Purpose

During the path resolution refactor, navigator's `governance_load(db_path, project_dir)`, `scan_path(db_path, target_path)`, and facade read functions were candidates for either explicit dependency injection (caller passes project root) or internal resolution (navigator resolves via `plugin.get_project_dir()`).

## Context

During the path resolution refactor, navigator's `governance_load(db_path, project_dir)`, `scan_path(db_path, target_path)`, and facade read functions were candidates for either explicit dependency injection (caller passes project root) or internal resolution (navigator resolves via `plugin.get_project_dir()`).

## Options considered

1. **Explicit injection** — callers pass `project_dir` as an argument. Explicit, testable without env vars, matches the prior signature.
2. **Internal resolution** — navigator resolves project root via `plugin.get_project_dir()` itself. Callers just say "scan this subpath" or "load governance" with no path argument.

## Decision

Internal resolution, applied universally.

Rationale: **Navigator catalogs the project it lives within — there is only ever one project per navigator instance, determined by where the database lives and where the runtime is executing.** Accepting `project_dir` as a function argument implies navigator could catalog an arbitrary directory on behalf of the caller, which is never true. The argument is cognitive noise that lets callers pass the wrong value or forget to pass it at all.

The facade also guarantees population before every read: `_ensure_scanned` is called at the top of every `paths_*` and governance query function, so callers never have to remember to scan first.

## Consequences

- **Enables:** callers invoke navigator functions without any path arguments; the contract is simpler and less error-prone.
- **Enables:** tests isolate via `monkeypatch.setenv("CLAUDE_PROJECT_DIR", ...)` instead of threading fixture paths through function calls.
- **Constrains:** every caller context must have `CLAUDE_PROJECT_DIR` set before invoking navigator — the helper raises if unset. In practice, Claude Code hooks/MCP/runtime all set it; test fixtures set it via monkeypatch; the CLI relies on the same env var.
- **Constrains:** the scanner must walk absolute paths anchored on the resolved project root (not cwd-relative), so storing project-relative paths via `relpath` is mandatory to keep the paths_table stable across working directories.
