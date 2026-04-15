# ocd

Deterministic enforcement of permissions, rules, and structural conventions for Claude Code. Provides opt-in conventions that shape agent behavior, a permission enforcement hook, and a project navigation tool.

## Setup

```
/plugin install ocd
/ocd:init
```

Restart the Claude session after init so rules auto-load. Run `/ocd:status` to verify plugin version, deployment state, and update availability.

`/ocd:init` deploys rules, conventions, patterns, and log templates into `.claude/` and initializes the navigator database. Use `--force` to overwrite existing files with plugin defaults.

## Capabilities

### Rules

Always-on agent behavior guidance deployed to `.claude/rules/ocd/` via `/ocd:init`. Auto-loaded every session. Users own the deployed files.

| Rule | Purpose |
|------|---------|
| `design-principles.md` | Foundational principles governing all artifacts and agent behavior |
| `workflow.md` | Execution discipline: working directory, agents, testing |
| `system-documentation.md` | README and architecture.md requirements per system |
| `process-flow-notation.md` | Structured programming notation for agent workflows |
| `log-routing.md` | When and how to capture decisions, friction, problems, and ideas as log entries |
| `markdown.md` | Base content standards for markdown files |

### Conventions

File-type-specific content standards deployed to `.claude/conventions/ocd/` via `/ocd:init`. Loaded on demand — a convention gate hook surfaces applicable conventions when the agent touches a matching file.

Each convention has YAML frontmatter declaring which files it applies to:

```yaml
---
includes: "*.py"
governed_by:
  - .claude/rules/ocd/design-principles.md
---
```

- **`includes`** — file patterns this convention applies to
- **`excludes`** — (optional) patterns to exclude from matching
- **`governed_by`** — (optional) governance entries this convention builds on, defining evaluation ordering

Rules govern agent behavior (always loaded, universal). Conventions govern file content (loaded on demand, pattern-matched). Both share the same frontmatter format and governance infrastructure.

### Hook: Permission enforcement

PreToolUse hook on Bash, Edit, and Write tools. Two evaluation layers:

1. **Hardcoded blocks** — structural constraints that do not stick as prose instructions. Blocks directory changes (`cd`, `pushd`, `popd`), compound commands (`&&`, `||`, `;`), and pipes (`|`). Returns inline guidance so the agent self-corrects without user intervention.
2. **Dynamic settings enforcement** — reads and merges global (`~/.claude/settings.json`) and project (`.claude/settings.json`) allow/deny lists. Approves operations matching allow patterns, respects deny rules with precedence, validates file paths against allowed directories.

### Skill: Navigator

`/ocd:navigator` — maintenance workflow for the project navigation database. Scans filesystem, detects changes, and drives description writing for project files and directories.

The navigator database (`.claude/ocd/navigator/navigator.db`) indexes project structure with human-written descriptions so agents can find files by purpose without reading every file. Agents use the navigator MCP server or CLI inline during tasks; the skill is for maintenance only.

### Skills

| Skill | Purpose |
|-------|---------|
| `/ocd:init` | Deploy rules, conventions, patterns, log templates, and navigator database |
| `/ocd:status` | Report plugin version, deployment state, navigator status, skills, permissions |
| `/ocd:navigator` | Maintain navigator database — scan filesystem and write descriptions |
| `/ocd:commit` | Topic-grouped commits with end-state messages and per-commit version bumps |
| `/ocd:push` | Push local commits to a named branch on the remote; commits first if needed |
| `/ocd:log` | Capture or manage project log entries — decisions, friction, problems, ideas |
| `/ocd:md-to-pdf` | Export markdown files to PDF styled with GitHub-flavored CSS |

### MCP Servers

Agent-facing tools exposed over the Model Context Protocol. Registered in `.mcp.json`; started by Claude Code on session connect.

| Server | Tools | Purpose |
|--------|-------|---------|
| `navigator` | `paths_*`, `skills_*`, `references_*`, `scope_*` | Project structure index, reference mapping, governance matching, scope analysis |

## License

MIT
