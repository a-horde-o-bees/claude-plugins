# cli.py overrides __main__.py convention

## Purpose

Some Python packages in the ocd plugin use `cli.py` as their CLI entry point instead of `__main__.py`, accidentally overriding the standard Python package convention. This breaks the `__main__.py + __init__.py` pattern that python.md prescribes for package structure and forces graceful-fallback handling in any tool that needs to find a system's CLI entry point.

## Affected files

Confirmed via grep at time of writing — re-verify when fixing:

- `plugins/ocd/lib/governance/cli.py`
- `plugins/ocd/servers/navigator/cli.py`

The second is particularly load-bearing: the navigator MCP server has both `__main__.py` (the FastMCP server entry) and `cli.py` (a debug-only CLI). They have different roles, so the rename target may need thought — possibly `_debug_cli.py` for navigator vs straight rename for governance.

## Fix scope

1. Rename `lib/governance/cli.py` → `__main__.py` (governance has no other entry; clean swap)
2. For `servers/navigator/`: the existing `__main__.py` is the MCP entry; the `cli.py` is a separate debugging CLI. Decide between renaming `cli.py` to a non-conflicting name (e.g., `_debug.py`) or merging the debug commands into a subcommand of `__main__.py`. The convention is satisfied either way — what matters is that `__main__.py` is the single Python-package entry point.
3. Update any callers — `run.py` invocations referencing `lib.governance.cli` or `servers.navigator.cli`, plus any docs / SKILL.md / convention-files that reference the old paths.
4. Verify navigator-side discovery in `update-system-docs` skill component files — they currently note "graceful fallback to cli.py" which can be removed once the cleanup lands.

## Why this comes first

The `update-system-docs` skill scaffold (committed 986ddd2) is poised to add yet another CLI module. Building it on top of the broken convention either compounds the violation (new `cli.py`) or forces it to swim against the existing files. Cleaner to fix the foundation, then build on it.

## Notes

This was discovered during the python convention audit on 2026-04-13. The user noted: "cli.py was accidentally overriding the normal convention for python packages." Prior to this surfacing, code was being added as cli.py because it matched what already existed.
