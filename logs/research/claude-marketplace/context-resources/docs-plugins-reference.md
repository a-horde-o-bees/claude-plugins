# docs-plugins-reference

**URL**: https://code.claude.com/docs/en/plugins-reference
**Type**: Official Claude Code documentation
**Authority**: Official — authoritative for plugin.json schema, component locations, hook event list, environment variables, plugin caching, and CLI commands.

## Scope

Complete plugin system reference: plugin.json schema, all component types (skills, agents, hooks, MCP, LSP, monitors, bin), path behavior, environment variables, plugin caching, installation scopes, CLI commands, debugging.

## Key prescriptions

### plugin.json schema

- **Required**: `name` only (if manifest is present at all — manifest is optional).
- **Metadata**: `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`.
- **Component paths**: `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `outputStyles`, `lspServers`, `monitors`.
- **Configuration**: `userConfig`, `channels`, `dependencies`.

### userConfig

```json
{
  "userConfig": {
    "api_endpoint": { "description": "...", "sensitive": false },
    "api_token": { "description": "...", "sensitive": true }
  }
}
```

- Prompts user at plugin enable time.
- Non-sensitive → `settings.json` under `pluginConfigs[<plugin-id>].options`.
- **Sensitive → system keychain** (or `~/.claude/.credentials.json` where keychain unavailable).
- **Keychain storage is shared with OAuth tokens and has an approximately 2 KB total limit** — keep sensitive values small.
- Available as `${user_config.KEY}` substitution in MCP/LSP/hook/monitor configs; also exported as `CLAUDE_PLUGIN_OPTION_<KEY>` env vars.

### Component locations (defaults)

| Component | Default location |
|---|---|
| Manifest | `.claude-plugin/plugin.json` |
| Skills | `skills/<name>/SKILL.md` |
| Commands | `commands/` (flat `.md` files) |
| Agents | `agents/` |
| Output styles | `output-styles/` |
| Hooks | `hooks/hooks.json` |
| MCP servers | `.mcp.json` |
| LSP servers | `.lsp.json` |
| Monitors | `monitors/monitors.json` |
| Executables | `bin/` (added to Bash tool PATH) |
| Plugin settings | `settings.json` (only `agent` + `subagentStatusLine` keys supported) |

**Components must be at plugin root, not inside `.claude-plugin/`.**

### Path behavior

- All paths relative to plugin root; must start with `./`.
- For `skills`, `commands`, `agents`, `outputStyles`, `monitors`: custom path **replaces** default. To keep default + extend, include the default: `"skills": ["./skills/", "./extras/"]`.
- Hooks, MCP, LSP: different semantics for merging multiple sources.

### Agent frontmatter

Supported fields: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`.

**Not supported for plugin-shipped agents (security)**: `hooks`, `mcpServers`, `permissionMode`. Only valid `isolation` value: `"worktree"`.

### Monitors

**Version floor**: requires Claude Code v2.1.105+.

```json
[
  {
    "name": "deploy-status",
    "command": "${CLAUDE_PLUGIN_ROOT}/scripts/poll-deploy.sh",
    "description": "Deployment status changes",
    "when": "always"
  }
]
```

- `when: "always"` (default) — starts at session boot.
- `when: "on-skill-invoke:<skill-name>"` — starts on first skill invocation.
- Each stdout line becomes a notification to Claude.
- Disabling plugin mid-session does not stop already-running monitors.

### LSP servers

- `.lsp.json` at plugin root or inline `lspServers` in plugin.json.
- Required fields: `command`, `extensionToLanguage`.
- **User must install language server binary separately** — plugin only configures the connection.

### Environment variables

- `${CLAUDE_PLUGIN_ROOT}` — absolute path to plugin install dir. **Not preserved across updates.**
- `${CLAUDE_PLUGIN_DATA}` — persistent plugin state dir; survives updates. Resolves to `~/.claude/plugins/data/{id}/`.

Both variables substituted inline in skill/agent/hook/monitor/MCP/LSP content AND exported as env vars to hook processes and MCP/LSP subprocesses.

### Docs-prescribed dependency install pattern

Worked example from plugins-reference:

```bash
diff -q "${CLAUDE_PLUGIN_ROOT}/package.json" "${CLAUDE_PLUGIN_DATA}/package.json" >/dev/null 2>&1 \
  || (cd "${CLAUDE_PLUGIN_DATA}" && cp "${CLAUDE_PLUGIN_ROOT}/package.json" . && npm install) \
  || rm -f "${CLAUDE_PLUGIN_DATA}/package.json"
```

- `diff` exits nonzero when stored copy missing or differs → triggers reinstall.
- If `npm install` fails, trailing `rm` removes copied manifest so next session retries.
- **No JSON systemMessage output.** Pattern is silent retry via the `rm` invariant.

### Plugin caching

- Marketplace plugins copied to `~/.claude/plugins/cache/` rather than used in-place.
- Each version is its own cache directory. Orphaned versions (after update/uninstall) removed 7 days later.
- Glob/Grep tools skip orphaned version directories.
- **Plugins cannot reference files outside their directory** (no `../shared-utils`). Symlinks preserved in cache — can use them to reach outside.

### Installation scopes

| Scope | Settings file | Purpose |
|---|---|---|
| `user` | `~/.claude/settings.json` | Personal (default) |
| `project` | `.claude/settings.json` | Team-shared via VCS |
| `local` | `.claude/settings.local.json` | Project-specific, gitignored |
| `managed` | Managed settings | Org-enforced (read-only, updates only) |

### Version management

- Semver required (`MAJOR.MINOR.PATCH`).
- Pre-release suffixes allowed (`2.0.0-beta.1`).
- **Claude Code uses version to decide whether to update — must bump on change or users never see updates.**

### CLI commands

- `plugin install <plugin>[@marketplace]` with `--scope`.
- `plugin uninstall` with `--keep-data` option.
- `plugin enable` / `plugin disable`.
- `plugin update`.
- `plugin list` with `--json`, `--available`.
- `plugin validate` — validates plugin.json, skill/agent/command frontmatter, hooks/hooks.json.

### Channels

Declared in plugin.json `channels` array, each binding to an MCP server in the plugin.

```json
{
  "channels": [
    {
      "server": "telegram",
      "userConfig": { "bot_token": { "description": "...", "sensitive": true } }
    }
  ]
}
```

## Use for

- Verifying plugin.json fields against the schema.
- Checking component default locations and path-behavior semantics.
- Understanding plugin cache structure and why relative paths outside plugin root don't work.
- The docs-prescribed dependency install pattern (`diff -q` + `rm` retry).
- userConfig behavior: sensitive routing to keychain, 2KB shared quota, env var export.
- Agent frontmatter constraints (which fields stripped for plugin-shipped agents).
- Monitor and LSP version floors and prerequisites.
