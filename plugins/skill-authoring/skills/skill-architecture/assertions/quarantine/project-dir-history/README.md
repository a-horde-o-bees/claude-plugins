# project-dir-history — quarantined reference

Historical artifacts of how this project resolved project/plugin root before the
skill-architecture rebuild. Reference only — mine for ideas, do not cite as fact.
Temporary; delete once the methods are re-derived in `../../project-root-discovery/`.

| File | Origin | What it shows |
|---|---|---|
| `session_start.py` | `plugins/ocd/hooks/` @ 6b1723b^ | SessionStart hook persisting `CLAUDE_PLUGIN_ROOT` to a `.claude/ocd/.plugin_root` file so Bash subprocesses could read it. Removed in 6b1723b as vestigial. |
| `hooks.json` | alongside it | How the SessionStart + PreToolUse hooks were wired. |
| `plugin__init__.py` | `plugins/ocd/plugin/` @ 6b1723b^ | The resolver chain: `get_plugin_root()` (env → `__file__` walk fallback), `get_project_dir()` (env, **raises** if unset — no cwd fallback). |
| `run-plugin.sh` | `scripts/` @ 8619484^ | CLI wrapper that did `export CLAUDE_PROJECT_DIR="$(pwd)"` — the "trust cwd at entry" lever. |
| `friction--CLAUDE_PROJECT_DIR-not-propagated.md` | logs/friction | Evidence the env var is NOT in Bash subprocesses; cwd fallback landed in `~/.claude` from plugin cache. |
| `decision--mcp-bootstraps-from-cwd.md` | logs/decision | MCP subprocess bootstrap from cwd; the silent `${CLAUDE_PROJECT_DIR}`-literal data-loss incident. |
