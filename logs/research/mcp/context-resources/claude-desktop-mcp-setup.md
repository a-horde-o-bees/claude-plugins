# Claude Desktop MCP Setup

## Identification
- url: https://modelcontextprotocol.io/docs/develop/connect-local-servers
- type: host integration docs
- author: Model Context Protocol project (documents Claude Desktop config)
- last-updated: active
- authority level: official

## Scope
The canonical guide for wiring a local MCP server into Claude Desktop. Covers the config file location (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, `%APPDATA%\Claude\claude_desktop_config.json` on Windows), the `mcpServers` JSON schema (`command`, `args`, `env`), the filesystem-server walkthrough as the worked example, the Developer tab → Edit Config UI affordance, restart requirements, the MCP server indicator in the UI, log file locations for debugging (`~/Library/Logs/Claude/mcp*.log` / `%APPDATA%\Claude\logs\mcp-server-*.log`), and Windows-specific `${APPDATA}` ENOENT mitigation.

## Takeaway summary
Claude Desktop is stdio-only for local servers: configure a `command` + `args` that spawns a process, and Claude Desktop runs it as a child. Paths in `args` must be absolute. You can't edit config while Claude Desktop is running and expect it to take effect — full quit + relaunch is mandatory. The logs are where server failures surface; `mcp-server-<name>.log` is per-server stderr, `mcp.log` is the connection-level log. On Windows, `npx` via Claude Desktop can hit a `${APPDATA}` expansion bug — the documented workaround is to explicitly set `APPDATA` in the per-server `env`. This doc focuses on local (stdio); remote servers have a separate page.

## Use for
- Where do I put the Claude Desktop config file?
- What JSON shape goes in `claude_desktop_config.json`?
- How do I read logs when a server silently fails to load?
- What's the Windows `APPDATA` workaround for npx-based servers?
- How do I know the server connected (UI indicator location)?

## Relationship to other resources
Local complement to the "connect remote servers" sibling doc on modelcontextprotocol.io. Referenced by every MCP server README's "Claude Desktop setup" section.

## Quality notes
Focused on stdio / local. For remote SSE or Streamable HTTP servers in Claude Desktop, follow up with the "connect-remote-servers" page. Version-stable for a long time — `claude_desktop_config.json` schema has been consistent.
