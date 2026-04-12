# ocd

Deterministic enforcement of permissions, rules, and structural conventions for Claude Code. Provides opt-in conventions that shape agent behavior, a permission enforcement hook, and a project navigation tool.

## Setup

```
/plugin install ocd
/init
```

Restart Claude session after init to load rules. Run `/status` to verify plugin version, init state, and update availability.

`/init` deploys rules to `.claude/rules/`, convention templates, and initializes skill infrastructure. Use `--force` to overwrite existing files with plugin defaults.

## Capabilities

### Rules

Convention files deployed to `.claude/rules/` via `/init`. Auto-loaded every session. Users can inspect, edit, or delete deployed rules — they own the files.

| Capability | Rule file | Purpose |
|------------|-----------|---------|
| `design-principles` | `design-principles.md` | Foundational principles governing all artifacts and agent behavior |
| `workflow` | `workflow.md` | Execution discipline: working directory, agents, testing |
| `system-documentation` | `system-documentation.md` | README and architecture.md requirements per system, with nesting and currency rules |
| `process-flow-notation` | `process-flow-notation.md` | Structured programming notation for agent workflows |

### Hook: Permission enforcement

PreToolUse hook on Bash, Edit, and Write tools. Two evaluation layers:

1. **Hardcoded blocks** — structural constraints that do not stick as prose instructions. Blocks directory changes (`cd`, `pushd`, `popd`), compound commands (`&&`, `||`, `;`), and pipes (`|`). Returns inline guidance so the agent self-corrects without user intervention.

2. **Dynamic settings enforcement** — reads and merges global (`~/.claude/settings.json`) and project (`.claude/settings.json`) allow/deny lists. Approves operations matching allow patterns, respects deny rules with precedence, validates file paths against allowed directories.

### Skill: Navigator

`/navigator` — maintenance workflow for the project navigation database. Scans filesystem, detects changes, and guides description writing for project files and directories.

The navigator database (`.claude/ocd/navigator/navigator.db`) indexes project structure with human-written descriptions so agents can find files by purpose without reading every file. Agents use the CLI tool inline during tasks; the skill is for maintenance only.

#### Navigator CLI

Agent-facing entry point at `skills/navigator/__main__.py`. Agents call `--help` to learn usage.

| Command | Purpose |
|---------|---------|
| `describe <path>` | Navigate structure; directories list children with descriptions |
| `list [path] [--pattern "*.py"] [--exclude ".claude/*"]` | Enumerate non-excluded file paths for tool consumption |
| `search --pattern <term>` | Find files by purpose across project |
| `scan [path]` | Sync filesystem to database after changes |
| `get-undescribed` | Find entries needing descriptions (used by /navigator skill) |
| `set <path> --description` | Write description for entry (used by /navigator skill) |
| `init --db <path>` | Create database with schema and seed rules |

### MCP Servers

Agent-facing tools exposed over the Model Context Protocol. Registered in `.mcp.json`; started by Claude Code on session connect.

| Server | Tools | Purpose |
|--------|-------|---------|
| `navigator` | `paths_*`, `governance_*`, `skills_*`, `references_*`, `scope_*` | Project structure index, governance discovery, reference mapping |
| `governance` | `governance_*` | Convention and rule governance: loading, matching, ordering, dependency analysis |
| `log` | `log_*`, `type_*`, `tag_*` | Unified project log across types (decision, friction, problem, idea) with per-type tag management |

## License

MIT
