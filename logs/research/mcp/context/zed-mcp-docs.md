# Zed MCP Docs

## Identification
- url: https://zed.dev/docs/ai/mcp
- type: host integration docs
- author: Zed Industries
- last-updated: active
- authority level: official (for Zed)

## Scope
Zed's Agent Panel MCP docs. Two installation methods: extension-based (install pre-built MCP server extensions from the Zed website, Command Palette, or Agent Panel menu) and custom (add to Zed's settings file under the `"context_servers"` key, with command / args / env or a remote URL, or via the Agent Panel's settings modal). Implements MCP's Tools and Prompts features. Handles `notifications/tools/list_changed` — servers can update their tool list at runtime and Zed picks it up without restart. Tool names appear as `mcp:<server>:<tool_name>`. Per-tool approval modes: `confirm`, `allow`, `deny`.

## Takeaway summary
Zed uses a distinct config key (`context_servers`, not `mcpServers`) — configs are not drop-in compatible with Claude Desktop / Cursor / Cline. Zed does support live tool-list updates via the spec's `notifications/tools/list_changed`, which matters if your server's capability set changes based on user context (e.g., auth-gated tools appearing after sign-in). Resources support is not listed — if your server leans on resources, check before targeting Zed. Per-tool permission modes let users allowlist individual tools per-workspace without approving the full server.

## Use for
- How do I wire an MCP server into Zed specifically (config key differs)?
- Does Zed support runtime tool-list updates?
- What's the per-tool approval model?
- What subset of MCP does Zed currently implement (no resources?)?

## Relationship to other resources
Peer of Cursor / Windsurf / VS Code / Cline / Continue docs. Key-naming divergence is the most likely gotcha when porting configs from another host.

## Quality notes
Zed's MCP support has been expanding; double-check the currently-supported feature set against the docs if targeting a rarely-used capability (resources, sampling, elicitation).
