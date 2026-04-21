# Windsurf (Cascade) MCP Docs

## Identification
- url: https://docs.windsurf.com/windsurf/cascade/mcp
- type: host integration docs
- author: Codeium / Windsurf
- last-updated: active
- authority level: official (for Windsurf/Cascade)

## Scope
Windsurf's MCP integration docs. Config lives at `~/.codeium/windsurf/mcp_config.json` with an `mcpServers` object. Supports stdio, SSE, and Streamable HTTP. For HTTP, config uses `serverUrl` pointing to an `/mcp` endpoint. Variable interpolation: `${env:VAR}` for env, `${file:/path/to/file}` for reading from disk (tilde-expansion supported). OAuth across all transports. Enforces a **100-tool limit** across all connected MCPs. Users can enable/disable individual tools through settings or raw config. Enterprise users must opt in via settings; admins can define custom registries or regex-based server allowlists.

## Takeaway summary
Two details unique to Windsurf matter: the 100-tool cap (aggregate across all servers) forces prioritization when you plug in many servers with many tools — enabling per-tool toggles from the UI is load-bearing. The `${file:...}` interpolation is a nice pattern for keeping secrets out of the config file itself. The regex server allowlist is an enterprise-friendly way to keep employees on vetted servers without maintaining an enumeration. Config format is close enough to Claude Desktop / Cursor / Cline that a server can advertise a single `mcpServers` snippet and users can paste it into any of them.

## Use for
- How do I configure an MCP server in Windsurf?
- What's the per-tool enable/disable story when total tool count bumps the 100 cap?
- How do I avoid hardcoding secrets in the config file?
- How does an organization restrict which MCP servers employees can use?

## Relationship to other resources
Peer of Cursor / VS Code / Zed / Cline / Continue docs. `mcpServers` schema is portable across most of them for stdio servers. Unique: 100-tool cap.

## Quality notes
Windsurf rebrand (from Codeium) occasionally shifts doc URLs. Tool cap is a hard limit, not advisory — plan accordingly when targeting this host.
