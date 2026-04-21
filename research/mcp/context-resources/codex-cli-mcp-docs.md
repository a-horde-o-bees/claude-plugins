# Codex CLI MCP Docs

## Identification
- url: https://developers.openai.com/codex/mcp/
- type: host integration docs
- author: OpenAI
- last-updated: active
- authority level: official (for Codex CLI)

## Scope
OpenAI's Codex CLI MCP configuration. Config lives in `config.toml` at two levels: `~/.codex/config.toml` (global) and `.codex/config.toml` (project-scoped, trusted projects only). CLI and IDE extension share this config. TOML format with `[mcp_servers.<server-name>]` tables per server. Optional top-level `mcp_oauth_callback_port` / `mcp_oauth_callback_url`. Supports **stdio** (local process via command + env + working dir) and **Streamable HTTP** (remote URL with bearer token or OAuth via `codex mcp login <server-name>`). CLI commands: `codex mcp add <name> -- <command>`, `codex mcp --help`, `/mcp` inside the TUI to list active servers, `codex mcp login <server-name>` for OAuth.

## Takeaway summary
Codex CLI is the most notable non-Anthropic terminal agent that speaks MCP. Key differences from Claude Code: TOML (not JSON), `.codex/config.toml` at project root (vs Claude Code's `.mcp.json`), and built-in `codex mcp login` for OAuth servers. Shares config between CLI and IDE extension — opt-in authorship once, use everywhere OpenAI's Codex runs. Supports only stdio and Streamable HTTP (no SSE listed); servers that are SSE-only may not work. Writing a server that targets both Claude Code and Codex CLI means keeping the transport and auth patterns portable — happily, OAuth 2.1 over Streamable HTTP works for both.

## Use for
- How do I wire an MCP server into Codex CLI?
- What's the TOML format (vs JSON used by most other hosts)?
- How do I authenticate with an OAuth-protected remote server from Codex?
- What's the command to list active servers in the TUI?

## Relationship to other resources
Non-Anthropic peer of `claude-code-mcp-docs.md`. Supports OAuth 2.1 flow documented in `mcp-authorization-tutorial.md`. TOML format is the closest thing to a "different file format" gotcha among mainstream hosts — most others use JSON variants.

## Quality notes
Uses TOML, not JSON — don't copy-paste from Claude-Desktop-style docs. `mcp_oauth_callback_port` is worth setting to a stable port for OAuth flows in dev.
