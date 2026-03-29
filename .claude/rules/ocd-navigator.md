# Navigator

SQLite database (`.claude/ocd/navigator/navigator.db`) indexes project structure — files, folders, and descriptions — so agents can find what they need without reading every file.

## CLI

```
python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator <command>
```

All commands except `init` and `scan` auto-scan before execution to ensure fresh data.

| Command | When to Use |
|---------|-------------|
| `describe <path>` | Navigate project structure; directories list children with descriptions, files show description; start with `describe .` for top-level overview |
| `list [path] [--pattern "*.py"] [--exclude ".claude/*"]` | Enumerate non-excluded file paths for tool consumption; supports repeatable `--pattern` for basename filtering and `--exclude` for full-path exclusion; one path per line, no descriptions |
| `search --pattern <keyword>` | Find files by purpose when you know what something does but not where it lives; complements Grep/Glob which search file contents and names |
| `scan <path>` | Explicit filesystem sync; other commands auto-scan so explicit scan is rarely needed; use when you want to see scan report |
| `get-undescribed` | During `/navigator` skill only; returns deepest directory with undescribed entries |
| `set <path> --description "..."` | During `/navigator` skill only; write or update entry description |
| `init --db <path>` | One-time setup; creates database with schema and seed rules |

## When to Use Navigator vs Other Tools

- **Navigator `describe`** — find files by what they do (scope, role, responsibility); browse structure with context
- **Navigator `list`** — enumerate file paths under directory with exclusion rules applied; for tool consumption (e.g., convention checking, batch operations)
- **Navigator `search`** — find files by purpose across project when you know concept but not path
- **Grep** — find files by content (code patterns, string literals, function names)
- **Glob** — find files by name pattern (extensions, naming conventions)

Use navigator first for orientation in unfamiliar areas, then Grep/Glob for specific code searches once you know where to look.
