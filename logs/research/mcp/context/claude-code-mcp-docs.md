# Claude Code MCP Docs

## Identification
- url: https://code.claude.com/docs/en/mcp
- type: host integration docs
- author: Anthropic (Claude Code team)
- last-updated: active
- authority level: official

## Scope
Claude Code's direct MCP integration (not via plugins). Documents the `claude mcp add` / `list` / `get` / `remove` CLI commands with `--transport http|sse|stdio`, `--env`, `--scope`, `--header` flags. Three scopes: **local** (current project only, stored in `~/.claude.json` under the project path; default), **project** (`.mcp.json` at project root, version-control-friendly, shared with team), **user** (all projects, private). Live-embedded registry browser pulling from `https://api.anthropic.com/mcp-registry/v0/servers` (Anthropic's own MCP registry). Documents per-server authentication patterns, the HTTP→http transport flag rename, and the `--` separator convention.

## Takeaway summary
Use the CLI, not hand-edited JSON, for Claude Code. `claude mcp add --transport http <name> <url>` for remote, `claude mcp add --transport stdio <name> -- <command> [args...]` for local (note the `--` separator and the requirement that flags come before the name). Project scope writes `.mcp.json` which is meant to be committed — this is how you share a team's MCP config via the repo. The embedded registry UI pulls from Anthropic's hosted registry and generates copy-paste `claude mcp add` commands per server; this registry is the one documented under `api.anthropic.com/mcp-registry` and is distinct from the community registries. Commands should always be executed with flags preceding the server name: `claude mcp add --transport stdio --env KEY=value myserver -- python server.py --port 8080`.

## Use for
- What CLI commands manage MCP servers in Claude Code?
- How do I share an MCP config with my team via git?
- What's the difference between local / project / user scopes in Claude Code?
- How does Claude Code's MCP registry differ from community registries?
- What's the `--` separator for in `claude mcp add`?

## Relationship to other resources
Orthogonal to `claude-code-plugins-reference.md` — plugins bundle MCP servers as part of a plugin package, while this doc covers adding MCP servers directly without the plugin wrapper. If you're shipping to multiple Claude Code users, plugins are usually a better distribution choice; if you're just wiring up your own dev environment, direct `claude mcp add` is faster.

## Quality notes
Highest-authority for Claude Code. The `--transport` flag name recently changed (`streamable-http` → `http` in the CLI) — verify against your installed version. Registry browser on the page is live, so server listings stay current without doc updates.
