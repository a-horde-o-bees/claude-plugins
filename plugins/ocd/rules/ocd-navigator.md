# Navigator

SQLite database (`.claude/ocd/navigator/navigator.db`) indexes project structure — files, folders, descriptions, governance relationships, and file metrics — so agents can find what they need without reading every file.

## CLI

```
python3 $(cat .claude/ocd/.plugin_root)/run.py skills.navigator <command>
```

All commands except `init`, `scan`, `governance-load`, `resolve-skill`, and `list-skills` auto-scan before execution to ensure fresh data.

| Command | When to Use |
|---------|-------------|
| `describe <path>` | Navigate project structure; directories list children with descriptions, files show description; start with `describe .` for top-level overview |
| `list [path] [--pattern "*.py"] [--exclude ".claude/*"] [--sizes]` | Enumerate non-excluded file paths for tool consumption; `--sizes` appends line_count and char_count columns for scope planning |
| `search --pattern <keyword>` | Find files by purpose when you know what something does but not where it lives; complements Grep/Glob which search file contents and names |
| `scan <path>` | Explicit filesystem sync; other commands auto-scan so explicit scan is rarely needed; use when you want to see scan report |
| `governance` | List all governance entries (rules and conventions) with patterns and loading mode |
| `governance-for <file> [<file> ...]` | Find which rules and conventions govern given files; check before creating or modifying files |
| `governance-order` | Topological ordering of governance entries for evaluation sequence |
| `governance-load --manifest <path>` | Seed governance data from manifest.yaml; called automatically during init |
| `get-undescribed` | During `/navigator` skill only; returns deepest directory with undescribed entries |
| `set <path> --description "..."` | During `/navigator` skill only; write or update entry description |
| `init --db <path>` | One-time setup; creates database with schema and seed rules |

## When to Use Navigator vs Other Tools

- **Navigator `describe`** — find files by what they do (scope, role, responsibility); browse structure with context
- **Navigator `list`** — enumerate file paths under directory with exclusion rules applied; for tool consumption (e.g., convention checking, batch operations); `--sizes` for scope planning
- **Navigator `search`** — find files by purpose across project when you know concept but not path
- **Navigator `governance-for`** — find which rules and conventions apply to files you're about to edit; replaces conventions `list-matching`
- **Navigator `governance-order`** — dependency ordering for governance evaluation; replaces conventions `list-self`
- **Grep** — find files by content (code patterns, string literals, function names)
- **Glob** — find files by name pattern (extensions, naming conventions)

Use navigator first for orientation in unfamiliar areas, then Grep/Glob for specific code searches once you know where to look.
