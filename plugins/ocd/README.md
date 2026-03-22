# ocd

Deterministic enforcement of permissions, rules, and structural conventions for Claude Code. Provides opt-in conventions that shape agent behavior, a permission enforcement hook, and a project navigation tool.

## Setup

```
/plugin install ocd
/ocd-init
```

Restart Claude session after init to load rules. Run `/ocd-status` to verify plugin version, init state, and update availability.

`/ocd-init` deploys convention rules to `.claude/rules/` (auto-loaded every session with CLAUDE.md-level strength) and initializes the navigator database.

### Selective adoption

```
/ocd-init --only agent-authoring
/ocd-init --only navigator
/ocd-init --only communication,workflow
/ocd-init --rules-only
```

Each capability deploys its rule file independently. `--rules-only` skips infrastructure initialization (navigator database).

## Capabilities

### Rules

Convention files deployed to `.claude/rules/` via `/ocd-init`. Auto-loaded every session. Users can inspect, edit, or delete deployed rules — they own the files.

| Capability | Rule file | Purpose |
|------------|-----------|---------|
| `agent-authoring` | `ocd-agent-authoring.md` | Writing style, process flow notation, CLI design conventions |
| `communication` | `ocd-communication.md` | Agent-user interaction style: alignment, feedback, questions |
| `workflow` | `ocd-workflow.md` | Execution discipline: agents, testing, code practices |
| `navigator` | `ocd-navigator.md` | Navigator CLI awareness and usage guide |

### Hook: Permission enforcement

PreToolUse hook on Bash, Edit, and Write tools. Two evaluation layers:

1. **Hardcoded blocks** — structural constraints that don't stick as prose instructions. Blocks directory changes (`cd`, `pushd`, `popd`), compound commands (`&&`, `||`, `;`), and pipes (`|`). Returns inline guidance so the agent self-corrects without user intervention.

2. **Dynamic settings enforcement** — reads and merges global (`~/.claude/settings.json`) and project (`.claude/settings.json`) allow/deny lists. Approves operations matching allow patterns, respects deny rules with precedence, validates file paths against allowed directories.

### Skill: Navigator

`/ocd-navigator` — maintenance workflow for the project navigation database. Scans filesystem, detects changes, and guides description writing for project files and directories.

The navigator database (`.claude/ocd/navigator/navigator.db`) indexes project structure with human-written descriptions so agents can find files by purpose without reading every file. Agents use the CLI tool inline during tasks; the skill is for maintenance only.

#### Navigator CLI

Agent-facing entry point at `skills/navigator/scripts/navigator_cli.py`. Agents call `--help` to learn usage.

| Command | Purpose |
|---------|---------|
| `get <path>` | Navigate structure; directories list children with descriptions |
| `search --pattern <term>` | Find files by purpose across project |
| `scan [path]` | Sync filesystem to database after changes |
| `get-undescribed` | Find entries needing descriptions (used by /ocd-navigator skill) |
| `set <path> --description` | Write description for entry (used by /ocd-navigator skill) |
| `init --db <path>` | Create database with schema and seed rules |

## License

MIT
