# Navigator

SQLite database (`.claude/ocd/navigator/navigator.db`) indexes project structure — files, folders, and descriptions — so agents can find what they need without reading every file.

## CLI

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/navigator/scripts/navigator_cli.py <command>
```

| Command | When to Use |
|---------|-------------|
| `get <path>` | Navigate project structure; directories list children with descriptions, files show description; start with `get .` for top-level overview |
| `search --pattern <keyword>` | Find files by purpose when you know what something does but not where it lives; complements Grep/Glob which search file contents and names |
| `scan <path>` | After making filesystem changes; syncs filesystem to database, reports added/removed/changed counts |
| `get-undescribed` | During `/navigator` skill only; returns deepest directory with undescribed entries |
| `set <path> --description "..."` | During `/navigator` skill only; write or update entry description |
| `init --db <path>` | One-time setup; creates database with schema and seed rules |

## When to Use Navigator vs Other Tools

- **Navigator `get`** — find files by what they do (scope, role, responsibility); browse structure with context
- **Navigator `search`** — find files by purpose across the project when you know the concept but not the path
- **Grep** — find files by content (code patterns, string literals, function names)
- **Glob** — find files by name pattern (extensions, naming conventions)

Use navigator first for orientation in unfamiliar areas, then Grep/Glob for specific code searches once you know where to look.
