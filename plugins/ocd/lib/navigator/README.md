# navigator

Project structure index backed by SQLite. Maintains a queryable directory of project files and directories with human-written descriptions agents use to decide whether to open a file. Complements Grep/Glob (which search content and names) by surfacing purpose.

## Setup

Deployed as part of the ocd plugin. The navigator database lives at `.claude/ocd/navigator/navigator.db` in the consuming project and is created by `/ocd:init`. No separate install step.

## Usage

### As a Python import

```python
import lib.navigator

lib.navigator.scan_path(".")
listing = lib.navigator.paths_get(".")
undescribed = lib.navigator.paths_undescribed()
lib.navigator.paths_upsert("plugins/ocd", description="ocd plugin source")
```

Functions return structured data (dicts, lists). Formatting for display is the caller's responsibility.

### As a CLI

```
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator describe <path>
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator list [<path>] [--pattern <glob> ...]
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator search --pattern <term>
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator scan [<path>]
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator get-undescribed
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator set <path> --description "..."
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator resolve-skill <name>
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator list-skills
python3 ${CLAUDE_PLUGIN_ROOT}/run.py lib.navigator init [--db <path>]
```

All commands except `init` auto-scan before execution to ensure fresh data. `--help` on any subcommand shows arguments and output format.

### As an MCP server

The navigator MCP server at `servers/navigator.py` exposes `paths_*`, `skills_*`, `references_*`, and `scope_*` tools as a thin adapter over this library. Registered in `.mcp.json`; started by Claude Code on session connect.

## Dependencies

Standard-library only (`sqlite3`, `csv`, `pathlib`). No SQLAlchemy, no ORM — direct SQL against the entries table. Database uses WAL mode with a 5-second busy timeout for concurrent access.

## Maintenance

Use `/ocd:navigator` to refresh the database after filesystem changes and drive description writing for new or stale entries.

## License

MIT
