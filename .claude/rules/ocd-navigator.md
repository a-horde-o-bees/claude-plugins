---
pattern: "*"
depends:
  - .claude/rules/ocd-design-principles.md
---

# Navigator

SQLite database (`.claude/ocd/navigator/navigator.db`) indexes project structure — files, folders, descriptions, governance relationships, and file metrics — so agents can find what they need without reading every file.

## MCP Tools

Primary agent interface. Tools follow `object_action` naming grouped by domain. All query tools auto-scan before execution to ensure fresh data.

### paths_*

| Tool | When to Use |
|------|-------------|
| `paths_describe` | Navigate project structure; directories list children with descriptions, files show description; start with `.` for top-level overview |
| `paths_list` | Enumerate non-excluded file paths; accepts `patterns` array for filtering, `excludes` for path filtering, `sizes` for line/char counts |
| `paths_search` | Find files by purpose when you know what something does but not where it lives; complements Grep/Glob which search file contents and names |
| `paths_set` | During `/ocd-navigator` skill only; write or update entry description |
| `paths_undescribed` | During `/ocd-navigator` skill only; returns deepest directory with undescribed entries |
| `paths_remove` | Remove entries from database; rarely needed — scan handles cleanup |

### governance_*

| Tool | When to Use |
|------|-------------|
| `governance_match` | Find which rules and conventions govern given files; pass array of file paths; check before creating or modifying files |
| `governance_list` | List all governance entries with patterns and loading mode (rule or convention) |
| `governance_order` | Topological ordering of governance entries for evaluation sequence |
| `governance_graph` | Governance dependency edges, roots, and leaves |
| `governance_unclassified` | Find files with no governance coverage, grouped by extension |

### skills_*

| Tool | When to Use |
|------|-------------|
| `skills_resolve` | Resolve skill name to SKILL.md path across discovery locations |
| `skills_list` | List all discoverable skills with source and path |

### references_* and scope_*

| Tool | When to Use |
|------|-------------|
| `references_map` | Follow file references recursively to build dependency DAG; works with SKILL.md backtick paths and governance depends |
| `scope_analyze` | Composite: references + sizes + governance in one call; returns file matrix with governance_index for partitioning |

## CLI

Operational commands not exposed as MCP tools. Used by hooks, init scripts, and manual maintenance.

```
python3 $(cat .claude/ocd/.plugin_root)/run.py skills.navigator <command>
```

| Command | When to Use |
|---------|-------------|
| `init --db <path>` | One-time setup; creates database with schema and seed rules |
| `scan <path>` | Explicit filesystem sync; MCP tools auto-scan so explicit scan is rarely needed |
| `governance-load` | Load governance from frontmatter in rules and conventions; called during init |

## When to Use Navigator vs Other Tools

- **Navigator `paths_describe`** — find files by what they do (scope, role, responsibility); browse structure with context
- **Navigator `paths_list`** — enumerate file paths under directory with exclusion rules applied; for tool consumption (e.g., convention checking, batch operations); `sizes=true` for scope planning
- **Navigator `paths_search`** — find files by purpose across project when you know concept but not path
- **Navigator `governance_match`** — find which rules and conventions apply to files you're about to edit
- **Navigator `governance_order`** — dependency ordering for governance evaluation
- **Navigator `scope_analyze`** — full scope discovery for evaluation skills; one call for files + sizes + governance matrix
- **Grep** — find files by content (code patterns, string literals, function names)
- **Glob** — find files by name pattern (extensions, naming conventions)

Use navigator first for orientation in unfamiliar areas, then Grep/Glob for specific code searches once you know where to look.
