# Claude Code Plugins Reference

## Identification
- url: https://code.claude.com/docs/en/plugins-reference
- type: host integration docs
- author: Anthropic (Claude Code team)
- last-updated: active (documents features gated behind Claude Code v2.1.105+)
- authority level: official

## Scope
Complete schema and behavioral reference for the Claude Code plugin system. Documents the `.claude-plugin/plugin.json` manifest (every field with types and examples), the file-locations convention, component types (skills, agents, hooks, MCP servers, LSP servers, monitors, output styles, commands), hook lifecycle events, installation scopes, plugin caching and path-traversal rules, `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` variable semantics, user-config / channels declarations, CLI commands (`plugin install/uninstall/enable/disable/update/list`), versioning discipline, and debugging.

## Takeaway summary
If you are shipping an MCP server bundled inside a Claude Code plugin, this is the reference. MCP server configuration lives in `.mcp.json` at plugin root (or inline in `plugin.json` under `mcpServers`), and supports `${CLAUDE_PLUGIN_ROOT}` / `${CLAUDE_PLUGIN_DATA}` variable substitution in `command`, `args`, `cwd`, and `env`. Plugins are copied into `~/.claude/plugins/cache` at install time — path traversal out of the plugin directory is blocked, so external dependencies need symlinks that are preserved (not dereferenced) by the cache. Caching is version-keyed, so the `plugin.json` `version` field must bump on every shipped change or users won't see updates. `userConfig` is the structured way to collect runtime secrets/endpoints; values are available as `${user_config.KEY}` substitutions and as `CLAUDE_PLUGIN_OPTION_<KEY>` env vars in subprocesses. Sensitive values route to keychain with a ~2 KB cap.

## Use for
- How do I bundle an MCP server inside a Claude Code plugin?
- What fields go in `plugin.json` and which are required?
- What variable substitutions are available in `.mcp.json`?
- How do plugins receive user-supplied config (API tokens, endpoints)?
- How does plugin caching affect file references and updates?
- Which hook events fire around MCP interactions (Elicitation, ElicitationResult, PreToolUse, PermissionRequest)?
- What CLI commands manage plugin lifecycle?

## Relationship to other resources
Project-native reference for this repo. Complements the generic MCP spec with Claude-Code-specific packaging conventions. Supplements `claude-code-plugin-marketplaces.md` (distribution side). The marketplace-facing side of plugin authoring.

## Quality notes
Authoritative for Claude Code; do not assume the same fields/variables/hook names apply to other MCP hosts — they do not. When cross-referenced from non-Claude-Code docs, treat as Claude-Code-specific.
