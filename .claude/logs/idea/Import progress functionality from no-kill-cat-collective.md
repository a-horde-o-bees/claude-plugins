# Import progress functionality from no-kill-cat-collective

## Purpose

Port the `progress` skill from the `a-horde-o-bees/claude` submodule (currently deployed in `no-kill-cat-collective` and other client projects) into the claude-plugins marketplace as the first artifact of a new `adhd` plugin.

## Context

The progress skill provides task/risk/dependency tracking with assistive-cognition ergonomics. Key UX primitive is `next` — a single command that returns a four-tier prioritization (Deadline / In Progress / Actionable / Blocked) so the user doesn't need to decide what to work on. Already aligned with claude-plugins design philosophy (verb-noun CLI, SQLite-as-truth, Make-Invalid-States-Unrepresentable, Pit-of-Success).

Source location: `gitlab.com/a-horde-o-bees/claude`, `skills/progress/`
- ~950 lines of Python stdlib-only CLI code
- ~60 tests / 1003 lines of test code
- 6-table SQLite schema with CHECK-constrained enums, FK, status/severity invariants
- 35+ verb-noun CLI commands
- Bidirectional markdown ↔ DB roundtripping with computed completion counts
- "Blocked by:" word-overlap heuristic for dependency import

## Migration gaps (all mechanical)

1. Workflow prose → PFN
2. `scripts/progress_cli.py` → skill-package layout with `__main__.py` + `__init__.py` + `_db.py` etc. per current convention
3. Add MCP tool surface (keep CLI too)
4. Wire into navigator for file-purpose capture of progress artifacts
5. Replace project-specific template with a generic starter
6. Decide deployment location — its own `.claude/progress/` directory, or a sub-path
7. Fit into log-routing.md — progress is task/risk tracking, distinct from decision/friction/problem/idea. May need a new log type OR an explicit carve-out stating progress is a separate channel

## Destination decisions to make

- **Plugin or skill inside ocd?** Plugin. Progress is cognitive-assistance scope, distinct from ocd's discipline/navigation scope. Keeping separate plugins preserves identity.
- **Repo: same marketplace or separate?** Same marketplace (`a-horde-o-bees/claude-plugins`), add to `plugins/adhd/`. Follows the pattern Anthropic's official marketplace uses (one marketplace, multiple plugins).
- **First in adhd plugin or the only thing?** First. Adhd is planned to grow; progress is the seed.

## Effort

2-4 days of focused work. The Python is clean and well-tested; most effort is in the packaging/conformance layer, not the business logic.

## Sequence

Do **after** claude-plugins v0.1.0 is stable and resume is out the door. Between Anthropic application stages is the natural window. Don't let MCP server work block this — progress migration is an independent track with no dependency on `horde-mcp` or any integration MCP.
