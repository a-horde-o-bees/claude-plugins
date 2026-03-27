# a-horde-o-bees Claude Code Plugins

Claude Code plugin marketplace for agent discipline, workflow conventions, and project navigation tools.

## Disclaimer

This is a personal development project. It is experimental, actively evolving, and provided as-is with no stability guarantees, support commitments, or backwards compatibility promises. Plugins may be added, removed, renamed, or fundamentally restructured at any time.

Use at your own discretion. If something breaks, the LICENSE applies.

## Plugins

| Plugin | Status | Description |
|--------|--------|-------------|
| [ocd](plugins/ocd/) | Active | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation |
| [blueprint](plugins/blueprint/) | Active | Structured competitive research and implementation planning through entity-based analysis |

## Installation

### From GitHub

Add the marketplace and install plugins:

```
/plugin marketplace add https://github.com/a-horde-o-bees/claude-plugins.git
/plugin install ocd@a-horde-o-bees
/plugin install blueprint@a-horde-o-bees
```

To track a specific branch (e.g., for pre-release testing):

```
/plugin marketplace add https://github.com/a-horde-o-bees/claude-plugins.git#dev
```

Restart Claude session so hooks and commands load, then initialize in target project:

```
/ocd-init
/blueprint-init
```

Restart Claude session again so deployed rules auto-load into context.

Update plugins after upstream changes:

```
/plugin marketplace update a-horde-o-bees
```

After updating, check if deployed rules and conventions need updating:

```
/ocd-status
/blueprint-status
```

If any files show `divergent`, force-update and restart:

```
/ocd-init --force
/blueprint-init --force
/exit
claude --continue
```

Restart after init is only needed when rule files change. Convention-only updates take effect immediately.

Remove a plugin or the marketplace:

```
/plugin uninstall ocd
/plugin marketplace remove a-horde-o-bees
```

### Local development

For contributors working on plugin source. Two approaches:

#### Marketplace-based (recommended)

Develop within a clone that is also the marketplace source. Plugins load via the installed marketplace, so changes flow through git:

```
/ocd-push
```

Commits and pushes all changes. Then refresh the marketplace cache and restart:

```
/plugin marketplace update a-horde-o-bees
/exit
claude --continue
```

Step 3 (`/exit` + restart) only required when `.claude/rules/` files changed. Skill and convention changes take effect after the marketplace update.

#### Plugin-dir (session-only)

Load plugins directly from a local clone without marketplace:

```
git clone https://github.com/a-horde-o-bees/claude-plugins.git
claude --plugin-dir ./claude-plugins/plugins/ocd --plugin-dir ./claude-plugins/plugins/blueprint
```

After making source changes, reload and restart:

```
/reload-plugins
/exit
claude --continue
```

`/reload-plugins` picks up script changes. Restart is required for skill content (SKILL.md) to take effect. `--continue` resumes the conversation with fresh context.

Check if deployed rules and conventions need updating:

```
/ocd-status
/blueprint-status
```

If any files show `divergent`, force-update and restart:

```
/ocd-init --force
/blueprint-init --force
/exit
claude --continue
```

Restart after init is only needed when rule files change. Convention-only updates take effect immediately.

Notes:

- `--plugin-dir` is session-only; no persistent setting exists
- When a `--plugin-dir` plugin shares a name with an installed marketplace plugin, the local copy takes precedence for that session
- `--debug` flag shows plugin loading diagnostics
- `claude plugin validate {PATH_TO_PLUGIN}` validates manifest without a session

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

**Opt-in convention delivery via `.claude/rules/`.** Rules deploy to the standard auto-loading directory. Users explicitly run init to adopt conventions. Without `--force`, existing files are preserved — init reports `Outdated` when deployed files differ from plugin templates.

**Status command for user awareness.** `/ocd-status` displays plugin version, init status, and available updates on demand. Informational only — no automated updates or network calls. Agent discoverability comes from skill list entries.

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
