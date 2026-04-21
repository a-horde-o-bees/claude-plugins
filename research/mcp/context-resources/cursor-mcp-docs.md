# Cursor MCP Docs

## Identification
- url: https://cursor.com/docs/context/mcp
- type: host integration docs
- author: Anysphere (Cursor)
- last-updated: active
- authority level: official (for Cursor)

## Scope
Cursor's MCP configuration and behavior docs. Config lives in `.cursor/mcp.json` (project-scoped) or `~/.cursor/mcp.json` (global). Supports stdio (Cursor-managed child process), SSE, and Streamable HTTP transports. Variable interpolation in values: `${env:NAME}`, `${workspaceFolder}`, `${userHome}`. OAuth support for remote servers with a fixed redirect URL `cursor://anysphere.cursor-mcp/oauth/callback`. `envFile` option is stdio-only.

## Takeaway summary
Cursor's model: project-scoped `.cursor/mcp.json` can be committed to share server configs with a team; global `~/.cursor/mcp.json` is per-user. Unlike Claude Desktop (stdio-only locally), Cursor supports remote servers natively via SSE/Streamable HTTP. OAuth has a fixed redirect URL baked into the client's URL scheme — servers using Cursor as an OAuth client must allowlist that callback. Server failures are isolated — one misbehaving server doesn't kill the others — and servers can be toggled via settings without removal. For CI or scripted setups, the `.cursor/mcp.json` format is near-identical to Claude Desktop's and Cline's, which makes vendoring/sharing straightforward.

## Use for
- Where does Cursor look for MCP config and how are project vs global scoped?
- What transports does Cursor support?
- What OAuth redirect URL do I allowlist for remote servers?
- How do I use environment variable interpolation?

## Relationship to other resources
Peer of `claude-desktop-mcp-setup.md` but richer (remote transports, scoped config, OAuth). The `mcpServers` JSON schema is compatible with Claude Desktop's for stdio servers — you can often reuse a config across both.

## Quality notes
Cursor URLs redirect frequently as their docs site reorganizes; canonical anchor is `/docs/context/mcp`. OAuth specifics are the part most likely to change.
