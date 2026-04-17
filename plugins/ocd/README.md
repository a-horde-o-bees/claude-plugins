# ocd

Deterministic enforcement of permissions, rules, and structural conventions for Claude Code. Provides opt-in conventions that shape agent behavior, a permission enforcement hook, and a project navigation tool.

## Setup

```
/plugin install ocd
/ocd:setup init
```

Restart Claude session after install to load rules. Run `/ocd:setup status` to verify plugin version, deployment state, and update availability.

`/ocd:setup init` deploys rules to `.claude/rules/`, convention templates, and initializes skill infrastructure. Use `--force` to overwrite existing files with plugin defaults.

## Automated Behavior

The following runs without user action once the plugin is installed. Each entry names the trigger, what happens, and why.

### Session start: dependency installation

Installs Python packages from the plugin's `requirements.txt` into an isolated virtual environment using `uv`. Required for MCP servers and hook scripts to function. Skips if dependencies haven't changed since last install. Prerequisite: `uv` must be installed on the user's system.

### Session start: rules auto-loading

Claude Code loads all markdown files from `.claude/rules/` into agent context at session start. The plugin deploys rule files to `.claude/rules/ocd/` during install — once deployed, they shape agent behavior every session without further action. Users own the deployed files and can edit or delete them.

### Session start: MCP server activation

The navigator MCP server starts automatically on session connect, making project structure tools (`paths_*`, `skills_*`, `references_*`, `scope_*`) available to the agent. Requires the navigator database to be initialized (happens during install).

### PreToolUse: permission enforcement

Fires before every Bash, Edit, and Write operation. Two layers: hardcoded blocks (directory changes, compound commands) that return corrective guidance, and dynamic settings enforcement that reads merged allow/deny patterns from project and user `settings.json`. Approved operations proceed without user prompt. See the Hook: Permission enforcement section under Capabilities for details.

### PreToolUse: convention gate

Fires before every Read, Edit, and Write operation. Non-blocking — always allows the tool call. Injects applicable conventions from `.claude/conventions/` into the agent's context based on the target file's path and the convention's `includes` pattern. On Read: conventions are surfaced for awareness. On Edit/Write: the agent is directed to conform and refactor if non-conformant.

### Install: git hookspath wiring

During `/ocd:setup init`, if the project contains a `.githooks/` directory, the plugin sets `core.hookspath=.githooks` in the local git config. This connects version-controlled git hooks (pre-commit, etc.) maintained by the project. Does nothing if `.githooks/` does not exist. The plugin does not create or modify hook files — it only wires the directory if one is already present.

## Capabilities

### Rules

Always-on agent behavior guidance deployed to `.claude/rules/ocd/` via `/ocd:setup init`. Auto-loaded every session. Users own the deployed files.

| Rule | Purpose |
|------|---------|
| `design-principles.md` | Foundational principles governing all artifacts and agent behavior |
| `workflow.md` | Execution discipline: working directory, agents, testing |
| `system-documentation.md` | README and architecture.md requirements per system |
| `process-flow-notation.md` | Structured programming notation for agent workflows |
| `log-routing.md` | When and how to capture decisions, friction, problems, and ideas as log entries |

### Conventions

File-type-specific content standards deployed to `.claude/conventions/ocd/` via `/ocd:setup init`. Surfaced automatically by the convention gate hook (see Automated Behavior) when the agent touches a matching file.

Each convention has YAML frontmatter declaring which files it applies to:

```yaml
---
includes: "*.py"
governed_by:
  - .claude/conventions/ocd/python.md
---
```

- **`includes`** — file patterns this convention applies to
- **`excludes`** — (optional) patterns to exclude from matching
- **`governed_by`** — (optional) governance entries this convention builds on, defining evaluation ordering

Rules govern agent behavior (always loaded, universal). Conventions govern file content (loaded on demand, pattern-matched). Both share the same frontmatter format and governance infrastructure.

### Hook: Permission enforcement

PreToolUse hook on Bash, Edit, and Write tools (see Automated Behavior for trigger details). Two evaluation layers:

1. **Hardcoded blocks** — structural constraints that do not stick as prose instructions. Blocks directory changes (`cd`, `pushd`, `popd`), compound commands (`&&`, `||`, `;`), and pipes (`|`). Returns inline guidance so the agent self-corrects without user intervention.

2. **Dynamic settings enforcement** — reads and merges global (`~/.claude/settings.json`) and project (`.claude/settings.json`) allow/deny lists. Approves operations matching allow patterns, respects deny rules with precedence, validates file paths against allowed directories.

### Skill: Navigator

`/ocd:navigator` — maintenance workflow for the project navigation database. Scans filesystem, detects changes, and guides description writing for project files and directories.

The navigator database (`.claude/ocd/navigator/navigator.db`) indexes project structure with human-written descriptions so agents can find files by purpose without reading every file. Agents use the CLI tool inline during tasks; the skill is for maintenance only.

#### Navigator CLI

Agent-facing entry point at `subsystems/navigator/__main__.py`. Agents call `--help` to learn usage.

| Command | Purpose |
|---------|---------|
| `describe <path>` | Navigate structure; directories list children with descriptions |
| `list [path] [--pattern "*.py"] [--exclude ".claude/*"]` | Enumerate non-excluded file paths for tool consumption |
| `search --pattern <term>` | Find files by purpose across project |
| `scan [path]` | Sync filesystem to database after changes |
| `get-undescribed` | Find entries needing descriptions (used by /ocd:navigator skill) |
| `set <path> --description` | Write description for entry (used by /ocd:navigator skill) |
| `init --db <path>` | Create database with schema and seed rules |

### Other Skills

Released skills (stable, available via `/ocd:` slash commands):

| Skill | Purpose |
|-------|---------|
| `/ocd:commit` | Topic-grouped commits with end-state descriptions |
| `/ocd:push` | Push to remote with pre-push commit check |
| `/ocd:setup init` | Deploy rules, conventions, and skill infrastructure |
| `/ocd:setup status` | Report plugin version, deployment state, skill status |
| `/ocd:log` | Capture decisions, friction, problems, ideas as log entries |
| `/ocd:pdf` | Export markdown to PDF via WeasyPrint with configurable CSS |

In-development skills (present on `main` for dev work, not yet included in the released `v0.1.0` branch):

| Skill | Purpose |
|-------|---------|
| `/ocd:audit-governance` | Audit governance chain conformity, followability, coherence |
| `/ocd:audit-static` | Audit any path against governance, best practices, and prior art |
| `/ocd:update-system-docs` | Maintain project documentation by deriving it from code reality (design only; implementation pending) |

### MCP Servers

Agent-facing tools exposed over the Model Context Protocol. Registered in `.mcp.json`; started by Claude Code on session connect.

| Server | Tools | Purpose |
|--------|-------|---------|
| `navigator` | `paths_*`, `skills_*`, `references_*`, `scope_*` | Project structure index, reference mapping, governance matching, scope analysis |

## Libraries

Python packages consumed as imports. Each has its own README and architecture.

| Library | Package | Purpose |
|---------|---------|---------|
| `governance` | [`subsystems/governance/`](subsystems/governance/) | Convention and rule governance: match files to applicable entries, list entries, compute dependency ordering. Disk-only. |
| `navigator` | [`subsystems/navigator/`](subsystems/navigator/) | Project structure index backed by SQLite: path indexing, filesystem scan, descriptions, reference mapping, skill resolution. |

## License

MIT
