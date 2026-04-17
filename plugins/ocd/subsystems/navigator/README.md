# navigator

Project structure index backed by SQLite. Maintains a queryable directory of project files and directories with human-written descriptions agents use to decide whether to open a file. Complements Grep/Glob (which search content and names) by surfacing purpose.

## Setup

Deployed as part of the ocd plugin. The navigator database lives at `.claude/ocd/navigator/navigator.db` in the consuming project and is created by `/ocd:setup init`. No separate install step.

## Usage

### As a Python import

```python
import subsystems.navigator

subsystems.navigator.scan_path(".")
listing = subsystems.navigator.paths_get(".")
undescribed = subsystems.navigator.paths_undescribed()
subsystems.navigator.paths_upsert("plugins/ocd", description="ocd plugin source")
```

Functions return structured data (dicts, lists). Formatting for display is the caller's responsibility.

### As a CLI

```
ocd-run subsystems.navigator describe <path>
ocd-run subsystems.navigator list [<path>] [--pattern <glob> ...]
ocd-run subsystems.navigator search --pattern <term>
ocd-run subsystems.navigator scan [<path>]
ocd-run subsystems.navigator get-undescribed
ocd-run subsystems.navigator set <path> --description "..."
ocd-run subsystems.navigator resolve-skill <name>
ocd-run subsystems.navigator list-skills
ocd-run subsystems.navigator init [--db <path>]
```

All commands except `init` auto-scan before execution to ensure fresh data. `--help` on any subcommand shows arguments and output format.

### As an MCP server

The navigator MCP server at `subsystems/navigator/server.py` exposes `paths_*`, `skills_*`, `references_*`, and `scope_*` tools as a thin adapter over this library. Registered in `.mcp.json`; started by Claude Code on session connect.

## Dependencies

Standard-library only (`sqlite3`, `csv`, `pathlib`). No SQLAlchemy, no ORM — direct SQL against the entries table. Database uses WAL mode with a 5-second busy timeout for concurrent access.

## Maintenance

Use `/ocd:navigator` to refresh the database after filesystem changes and drive description writing for new or stale entries.

## License

MIT
