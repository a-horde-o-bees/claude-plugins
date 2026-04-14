# Logging convention drop and dead logger declarations

## Purpose

`python.md` Logging section prescribes module-level loggers for every module that does I/O, but the codebase's actual practice is the opposite — only 3 of ~70 files have a module-level logger, and even those 3 never call any log methods. The convention is stale relative to reality, and the 3 logger declarations are dead code. Direction confirmed by user on 2026-04-13: drop the Logging section from the convention; remove the dead logger declarations from the navigator files. Held pending other in-flight work.

## Affected artifacts

**Convention file (template path):**

- `plugins/ocd/templates/conventions/python.md` — `### Logging` subsection under `## Code Style` should be removed entirely. The three sub-bullets ("Use logger.info/...", "Only CLI/presentation layers use print()", "No logging.basicConfig()") are also affected — the print() guidance may be worth keeping as a separate concern (see "Open question" below).

**Code files with dead `import logging` + `logger = logging.getLogger(__name__)`:**

- `plugins/ocd/servers/navigator/__init__.py` — line 13 + line 28; logger never called
- `plugins/ocd/servers/navigator/_scanner.py` — line 11 + line 20; logger never called
- `plugins/ocd/servers/navigator/_db.py` — line 7 + line 11; logger never called

**Misleading comment to clean up:**

- `plugins/ocd/servers/navigator/cli.py:12` — `from . import *  # noqa: F403 — __all__ defines the public API` — the comment about `__all__` is wrong; the package relies on underscore prefixes per convention. (May get folded into the cli.py → __main__.py rename — see sibling problem entry.)

## Open question

The same audit surfaced `print()` calls in `plugins/ocd/plugin/_permissions.py` and `plugins/ocd/plugin/_orchestration.py` for user-facing status output. The current convention text says "Only CLI/presentation layers use print() and input() for user-facing output." User said "will need to review closer" on this — defer in this cleanup.

## Recommended order

1. Land cli.py → __main__.py cleanup first (sibling problem) — keeps cleanup pass coherent
2. Edit `python.md` to drop the Logging subsection
3. Remove `import logging` + `logger = logging.getLogger(__name__)` from the 3 navigator files
4. Drop the misleading `__all__` comment in `cli.py` (or roll into the rename)

All in one commit; small, contained.

## Background

Discovered during python convention audit on 2026-04-13. The audit also confirmed broader alignment between conventions and code (typing, paths, module decomposition, MCP server patterns, SQLite, _init.py contract all aligned). Logging was the one conspicuous misalignment.
