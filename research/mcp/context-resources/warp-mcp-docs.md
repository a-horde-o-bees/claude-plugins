# Warp Terminal MCP Docs

## Identification
- url: https://docs.warp.dev/agent-platform/warp-agents/agent-context/mcp
- type: host integration docs
- author: Warp
- last-updated: active
- authority level: official (for Warp)

## Scope
Warp terminal's MCP integration. Config accessible via Settings > MCP Servers, Warp Drive (Personal > MCP Servers), the Command Palette, or the AI settings tab. Two connection methods: **CLI Server (Command)** — local startup command with cwd + args + env — and **Streamable HTTP/SSE Server (URL)** — remote/local URL with optional custom headers. Supports **multi-server JSON config** and auto-detection of MCP servers from Claude Code and Codex configs. **OAuth** for one-click setup. **Server sharing** with teammates, automatically scrubbing sensitive env values. Persistent state: stopped servers stay stopped between sessions. Logs at `~/Library/Group Containers/2BBY89MBSN.dev.warp/.../mcp` (macOS), `%LOCALAPPDATA%\warp\Warp\data\logs\mcp` (Windows), `${XDG_STATE_HOME:-$HOME/.local/state}/warp-terminal/mcp` (Linux).

## Takeaway summary
Warp is unusual for aggressively interop-ing with other hosts — it auto-detects MCP servers configured for Claude Code and Codex, so users who've already set up either host get zero-config carry-over. The server-sharing feature with automatic env-var scrubbing is a nice team-collaboration affordance — send a teammate your server config without leaking your personal API tokens. Supports both stdio and HTTP-based transports.

## Use for
- How do I add an MCP server to Warp terminal?
- Does Warp reuse configs from Claude Code or Codex CLI?
- How do I share an MCP setup with a teammate without leaking secrets?
- Where are Warp's MCP logs per OS?

## Relationship to other resources
Peer of `claude-code-mcp-docs.md`, `codex-cli-mcp-docs.md`, and the IDE-based host docs. Differentiator: cross-host config auto-detection.

## Quality notes
Warp's MCP docs have moved URLs during the product's evolution; if the linked URL 404s, use the docs search or the sitemap at `docs.warp.dev/sitemap.md`.
