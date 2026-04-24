# Cline MCP Docs

## Identification
- url: https://docs.cline.bot/mcp/configuring-mcp-servers
- type: host integration docs
- author: Cline
- last-updated: active
- authority level: official (for Cline)

## Scope
Cline's MCP configuration docs. Config stored in `cline_mcp_settings.json`, accessed via the MCP Servers icon → Configure tab. Supports stdio (local, command + args + env) and SSE (remote, HTTPS URL + headers). Per-server settings: `alwaysAllow` (pre-approve specific tools), `disabled`, network timeout (30s–1h, default 1 minute). Built-in MCP marketplace for browsing and installing. Automated setup workflow where you point Cline at a GitHub URL and it clones / builds / configures the server.

## Takeaway summary
Cline's differentiator is the auto-install-from-GitHub-URL flow: for servers that follow a standard layout, users don't need to clone or run `npm install` manually. The `alwaysAllow` array is a per-server tool allowlist that skips the approval prompt for specific tools — useful for trusted read-only tools, dangerous for write tools. Timeout knob (30s–1h) is coarser than what some backends want but covers long-running tool invocations. SSE-only for remote at research time (no Streamable HTTP documented), which means servers advertising only Streamable HTTP may need to expose an SSE endpoint for Cline compatibility.

## Use for
- How do I configure an MCP server in Cline?
- What's the `alwaysAllow` pattern for pre-approving tools?
- How do I raise the per-server timeout for slow tools?
- Does Cline support Streamable HTTP yet (vs just SSE)?

## Relationship to other resources
Peer of the other host docs. Config shape is close to Claude Desktop / Cursor / Continue for stdio. SSE-only remote transport is the key limitation vs Cursor / VS Code / Windsurf.

## Quality notes
Verify current transport support before relying on Streamable HTTP — this has been evolving.
