# ocd

Deterministic enforcement of permissions, rules, and structural conventions for Claude Code. Provides opt-in conventions that shape agent behavior, a permission enforcement hook, and a project navigation tool.

## Setup

```
/plugin install ocd
/ocd-init
```

Restart Claude session after init to load rules.

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

The navigator database (`docs/ocd/navigator/navigator.db`) indexes project structure with human-written descriptions so agents can find files by purpose without reading every file. Agents use the CLI tool inline during tasks; the skill is for maintenance only.

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

## Architecture

### Plugin structure

```
ocd/
  .claude-plugin/plugin.json           # Plugin manifest
  hooks/
    hooks.json                          # PreToolUse registration
  commands/
    init.md                             # /ocd-init command
  scripts/
    override_approvals.py               # Permission enforcement hook
    init.py                             # Rule deployment and DB initialization
  rules/                                # Convention templates (deployed to .claude/rules/)
    ocd-agent-authoring.md
    ocd-communication.md
    ocd-workflow.md
    ocd-navigator.md
  skills/
    navigator/
      SKILL.md                          # /ocd-navigator skill definition
      scripts/                          # Navigator tool implementation
      references/                       # Skill-specific guidance (loaded during skill)
  tests/                                # Plugin-level tests
```

### Design principles

**Deterministic operations in scripts, not agent judgment.** File copying, database initialization, permission checking — these are handled by Python scripts called via Bash. Skills contain only the non-deterministic parts: judgment calls, context-dependent decisions, natural language generation.

**Opt-in convention delivery via `.claude/rules/`.** Rules deploy to the standard auto-loading directory. Users explicitly run `/ocd-init` to adopt conventions. Existing files are never overwritten — user customizations are preserved.

**No SessionStart hooks for discoverability.** SessionStart hook messages appear as passive log lines that agents don't act on. Discoverability comes from skill list entries (visible via `/ocd`) instead.

**Agent-facing tools are first-class interfaces.** Scripts that agents call directly use the `_cli` suffix and follow agent-facing design conventions: long-form flags, agent-oriented help text (when to call, output format, what to call next), structured output with parseable markers, corrective error messages.

**Internal scripts are implementation details.** Scripts called by hooks or commands (not by agents directly) use plain names without the `_cli` suffix. They don't need agent-oriented documentation.

### Naming conventions

**Files deployed to projects** use the `ocd-` prefix for namespace isolation: `ocd-agent-authoring.md`, `ocd-navigator.md`. Prevents collision with other plugins or user files in `.claude/rules/`.

**Plugin-internal files** don't use the `ocd-` prefix — they're already namespaced by living inside the plugin directory.

**Commands and skills** use the `ocd-` prefix in their frontmatter `name` field so `/ocd` surfaces all plugin commands during search.

**Agent-facing CLIs** use `<name>_cli.py` suffix. Internal scripts use `<name>.py`.

### Convention delivery model

```
Plugin source          /ocd-init copies to         Auto-loaded by Claude
  ocd/rules/*.md  -->  .claude/rules/ocd-*.md  -->  Every session
```

Rules have CLAUDE.md-level strength once deployed. The plugin is the source of truth for convention content; the deployed files are copies the user can customize. Running `/ocd-init` again skips files that already exist (use `--force` to overwrite — not yet implemented).

### Navigator design decisions

**No dedicated navigator agent.** Agent handoff destroys traversal context. When an agent navigates a codebase, it builds a mental map of structure, relevance, and ruled-out areas. Returning a flat file list from a navigator agent discards that map, forcing re-traversal when requirements shift. Navigation stays inline with the calling agent.

**CLI `--help` as documentation.** Instead of injecting awareness via hooks or always-on skills, the `ocd-navigator.md` rule teaches agents the CLI exists. Agents call `--help` when they need usage details. Help text arrives as a tool result (compactable) rather than skill content (persistent in context).

**Skill is for maintenance only.** `/ocd-navigator` handles the scan/describe workflow — syncing filesystem changes and writing descriptions. Exploration during development tasks uses the CLI directly, guided by the rule file.

## License

MIT
