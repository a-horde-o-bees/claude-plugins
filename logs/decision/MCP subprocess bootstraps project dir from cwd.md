# MCP subprocess bootstraps project dir from cwd

## Purpose

The path resolution refactor made `plugin.get_project_dir()` raise when `CLAUDE_PROJECT_DIR` is unset, on the principle that silent cwd fallback corrupts state when code runs from the wrong directory.

## Context

The path resolution refactor made `plugin.get_project_dir()` raise when `CLAUDE_PROJECT_DIR` is unset, on the principle that silent cwd fallback corrupts state when code runs from the wrong directory. This broke all MCP servers that migrated to `plugin.get_project_dir()` because Claude Code does not propagate `CLAUDE_PROJECT_DIR` to MCP subprocesses automatically.

## Options considered

1. **Expand `${CLAUDE_PROJECT_DIR}` in `.mcp.json` env block values.** Claude Code expands `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` in `command` and `args` fields, so the reasonable assumption was that env block values support the same expansion. Attempted as a one-line addition to each server's env block.

2. **Revert `get_project_dir()` to cwd fallback universally.** Simple, restores the old behavior, gives up the safety gained from raising.

3. **Bootstrap `CLAUDE_PROJECT_DIR` from `Path.cwd().resolve()` at MCP server import time, scoped to `servers/_helpers.py`.** Preserves the raising behavior for all non-MCP contexts; MCP servers have a Claude Code contract that their cwd is the project root, so the bootstrap is safe specifically for that context.

## Decision

Option 3.

## Verification — what worked and what didn't

Option 1 was tried first and **did not work**. Claude Code's variable expansion is scoped to `command` and `args` fields only. Inside `env` block values, `${CLAUDE_PROJECT_DIR}` passes through as a literal string. In the MCP subprocess, `os.environ["CLAUDE_PROJECT_DIR"]` then contains the literal `${CLAUDE_PROJECT_DIR}`. Downstream, `plugin.get_project_dir()` returns `Path("${CLAUDE_PROJECT_DIR}").resolve()`, which is `cwd / ${CLAUDE_PROJECT_DIR}` — a path under the real project root with a directory name literally equal to `${CLAUDE_PROJECT_DIR}`.

The `decisions` and `stash` MCP servers "succeeded" at writes during in-session verification — but the writes landed at `${project_root}/${CLAUDE_PROJECT_DIR}/.claude/ocd/decisions/decisions.db` and `${project_root}/${CLAUDE_PROJECT_DIR}/.claude/ocd/stash/stash.db`. Two real decisions that were saved via MCP in that state were lost when the garbage directory was removed; they had to be re-added via a direct Python skill call to the correct database. The failure mode was silent.

The `navigator` MCP server returned mostly-empty data because its scanner walked the garbage directory, finding only the stash/decisions databases that `decisions`/`stash` had just created there. This is what made the failure visible — the navigator MCP describe output showed `${CLAUDE_PROJECT_DIR}` as a child of the real project root.

Option 3 is verified working after restart: all four MCP servers resolve project paths correctly via the cwd-derived `CLAUDE_PROJECT_DIR`, decisions and navigator return full real-db content, and no new garbage directory is created.

## Consequences

- **Enables:** MCP servers work correctly without requiring Claude Code platform changes.
- **Enables:** `plugin.get_project_dir()` continues to raise in CLI, hook, and test contexts, preserving the silent-wrong-cwd protection for those call sites.
- **Constrains:** The exception is narrow but real — someone reading `python.md` sees "never use cwd fallback" followed by a pointer to one documented exception in `mcp-server.md`. Keeping these cross-references in sync matters.
- **Constrains:** If Claude Code ever starts propagating `CLAUDE_PROJECT_DIR` to MCP subprocesses automatically, the bootstrap becomes redundant but harmless (the guard `if "CLAUDE_PROJECT_DIR" not in os.environ` becomes a no-op).
- **Constrains:** If a new MCP server is added without importing `servers/_helpers.py`, the bootstrap will not fire and the server will raise. The convention should state that all ocd servers must import `_helpers` for this reason (in addition to `_ok`/`_err`).
