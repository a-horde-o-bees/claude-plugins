# VS Code / GitHub Copilot MCP Docs

## Identification
- url: https://code.visualstudio.com/docs/copilot/chat/mcp-servers
- type: host integration docs
- author: Microsoft / GitHub
- last-updated: active
- authority level: official (for VS Code + GitHub Copilot)

## Scope
VS Code's MCP integration guide. Servers are added via the Extensions view (search `@mcp`), the `MCP: Add Server` command, or the `--add-mcp` CLI flag. Config file locations: workspace (`.vscode/mcp.json`, meant for source control) and user profile (global, accessed via `MCP: Open User Configuration`). Supports HTTP (remote) and stdio (local) transports. Includes macOS/Linux sandboxing for servers — an isolated environment restricted to explicitly-permitted file paths and network domains. Trust verification gate at first startup. Dev Container integration via `devcontainer.json` under `customizations.vscode.mcp`. Settings Sync propagates configs across devices.

## Takeaway summary
VS Code's MCP story is richer than most hosts': it uniquely ships **sandboxing** on macOS/Linux — an MCP server can be launched with explicit allowlisted paths and domains, reducing the blast radius of a compromised or misbehaving server. The `.vscode/mcp.json` file is git-friendly; user config lives elsewhere and follows Settings Sync across machines. Extensions-view discovery means you can install MCP servers with one click rather than editing JSON. Dev Container integration means a project can declare its MCP servers as part of its container definition, making them available automatically to anyone opening the project in Codespaces or a Dev Container.

## Use for
- How do I share an MCP server config with teammates via the repo?
- What sandboxing does VS Code offer for MCP servers?
- How do I ship an MCP server as part of a Dev Container definition?
- Can I install MCP servers via the extensions marketplace?

## Relationship to other resources
Peer of Cursor, Windsurf, Zed docs. The sandboxing feature is the clearest differentiator in the 2026 host landscape. `mcp.json` shape is compatible enough with other hosts that cross-vendoring usually works.

## Quality notes
Microsoft actively iterates; verify sandboxing availability on your OS before relying on it. The sandboxed behavior is not available on Windows at research time.
