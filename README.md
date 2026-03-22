# a-horde-o-bees Claude Code Plugins

Claude Code plugin marketplace for agent discipline, workflow conventions, and project navigation tools.

## Disclaimer

This is a personal development project. It is experimental, actively evolving, and provided as-is with no stability guarantees, support commitments, or backwards compatibility promises. Plugins may be added, removed, renamed, or fundamentally restructured at any time.

Use at your own discretion. If something breaks, the LICENSE applies.

## Plugins

| Plugin | Status | Description |
|--------|--------|-------------|
| [ocd](plugins/ocd/) | Active | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation |

## Installation

### Local development

Clone the repo and add the marketplace from your local path:

```
/plugin marketplace add a-horde-o-bees --path /path/to/claude-plugins
/plugin install ocd
```

After making changes to plugin source, sync and reinstall, then restart Claude session:

```
/plugin marketplace update a-horde-o-bees
/plugin uninstall ocd
/plugin install ocd
```

Remove a plugin or the marketplace:

```
/plugin uninstall ocd
/plugin marketplace remove a-horde-o-bees
```

### External users

Add this marketplace by URL (requires access to the repository):

```
/plugin marketplace add a-horde-o-bees --url https://github.com/a-horde-o-bees/claude-plugins.git
```

Then install individual plugins:

```
/plugin install ocd
```

> **Note:** This repo is currently private. External installation requires repository access.

## Architecture

### Plugin structure

```
<plugin>/
  .claude-plugin/plugin.json           # Plugin manifest
  hooks/
    hooks.json                          # Hook registrations (SessionStart, PreToolUse, etc.)
  commands/                             # Slash commands (e.g., /ocd-init)
  scripts/                              # Hook implementations and internal scripts
  references/                           # Reference data (manifests, configs)
  rules/                                # Convention templates (deployed to .claude/rules/)
  skills/
    <skill>/
      SKILL.md                          # Skill definition
      scripts/                          # Skill tool implementation
      references/                       # Skill-specific guidance
  templates/                            # Templates deployed to user projects
  tests/                                # Plugin-level tests
```

### Design principles

**Deterministic operations in scripts, not agent judgment.** File copying, database initialization, permission checking — handled by scripts called via Bash. Skills contain only non-deterministic parts: judgment calls, context-dependent decisions, natural language generation.

**Opt-in convention delivery via `.claude/rules/`.** Rules deploy to the standard auto-loading directory. Users explicitly run init to adopt conventions. Existing files are never overwritten — user customizations are preserved.

**SessionStart hook for user awareness.** Displays plugin version, init status, and available updates at session start. Informational only — no automated updates or network calls. Agent discoverability comes from skill list entries.

**Plugin data lives in `.claude/<plugin>/`.** Files that support plugin operation (databases, caches, conventions) are stored under `.claude/<plugin>/` in the project directory, not in the user's project tree. Rule files deploy to `.claude/rules/` per the standard convention.

**Agent-facing tools are first-class interfaces.** Scripts that agents call directly use the `_cli` suffix and follow agent-facing design conventions: long-form flags, agent-oriented help text, structured output with parseable markers, corrective error messages.

**Internal scripts are implementation details.** Scripts called by hooks or commands (not by agents directly) use plain names without the `_cli` suffix.

### Naming conventions

**Rule files deployed to `.claude/rules/`** use a plugin-name prefix for namespace isolation (e.g., `ocd-agent-authoring.md`). Prevents collision with other plugins or user files.

**Supporting files deployed to projects** live under `.claude/<plugin>/`, with skill-specific files under `.claude/<plugin>/<skill>/`. Directory nesting provides namespace isolation — no prefix needed.

**Plugin-internal files** don't use the prefix — already namespaced by living inside the plugin directory.

**Commands and skills** use the plugin-name prefix in their frontmatter `name` field so the plugin name surfaces all commands during search.

**Agent-facing CLIs** use `<name>_cli.py` suffix. Internal scripts use `<name>.py`.

### Convention delivery model

```
Plugin source              Init copies to              Auto-loaded by Claude
  <plugin>/rules/*.md  -->  .claude/rules/<prefix>-*.md  -->  Every session
```

Rules have CLAUDE.md-level strength once deployed. The plugin is source of truth for convention content; deployed files are copies users can customize.

### Navigator design decisions

**No dedicated navigator agent.** Agent handoff destroys traversal context. Navigation stays inline with the calling agent.

**CLI `--help` as documentation.** Rule file teaches agents the CLI exists. Agents call `--help` when they need usage details. Help text arrives as a tool result (compactable) rather than skill content (persistent in context).

**Skill is for maintenance only.** The skill handles the scan/describe workflow. Exploration during development tasks uses the CLI directly.

## Versioning

Plugin versions follow `x.y.z` format:

- `x` — major version; starts at `0` until a change breaks previous setups
- `y` — increments on public release (cohesive, ready for consumers); resets `z` to `0`
- `z` — increments on every development commit; required for local plugin reload to detect changes

## License

MIT. See [LICENSE](LICENSE).
