# Continue MCP Docs

## Identification
- url: https://docs.continue.dev/customize/deep-dives/mcp
- type: host integration docs
- author: Continue
- last-updated: active
- authority level: official (for Continue)

## Scope
Continue's MCP integration docs. Two ways to configure: inline `mcpServers` in Continue's main config, or standalone JSON files dropped in `.continue/mcpServers/` at workspace root. The standalone-file mode explicitly accepts configs in the same shape as Claude Desktop, Cursor, and Cline — paste-compatible. Supports stdio, SSE, and Streamable HTTP. MCP functionality is restricted to **agent mode** (not chat/edit modes). Secrets via env vars, with `${{ secrets.SECRET_NAME }}` syntax for local secrets or hosted secrets from Continue Mission Control.

## Takeaway summary
Continue's `.continue/mcpServers/` drop-folder is the most cross-host-friendly packaging pattern in the ecosystem: a server can ship a single `mcp.json` file and it works as-is in Claude Desktop, Cursor, Cline, and Continue (via the folder). Secrets flow through a hosted store (Mission Control) when present, or local env fallback — this is worth modeling your own config guidance around. The agent-mode-only restriction matters: if your users are primarily in chat or edit mode, MCP tools won't fire, so user instructions need to call out agent mode explicitly.

## Use for
- How do I configure an MCP server in Continue specifically?
- Does Continue accept Claude Desktop / Cursor-compatible config blocks?
- How do I manage secrets across local and hosted environments?
- Which Continue modes can use MCP tools?

## Relationship to other resources
Peer of the other host docs; notable for its explicit cross-host-format acceptance. Pairs well with `claude-desktop-mcp-setup.md` since a Continue user can often just reuse that config.

## Quality notes
Agent-mode-only restriction is the most common source of "MCP server installed but tools don't appear" support questions for Continue users.
