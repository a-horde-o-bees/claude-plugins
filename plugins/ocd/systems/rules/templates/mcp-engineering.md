---
tagline: Engineering around MCPs — keep the agent out of bulk loops, reuse existing servers
---

# MCP Engineering

MCP servers are JSON-RPC services — any process that speaks the protocol can call their tools. The agent is one consumer among many; bulk or mechanical work routed through an MCP server is paid in agent tokens proportional to data size when the agent is the caller, but a script speaking the same protocol pays nothing per record. This rule governs the disciplines that fire when designing, consuming, or automating MCPs — separate from server-authoring conventions in `mcp-server`, which apply only when editing server source.

- The Anthropic-maintained `mcp` Python SDK (`pip install "mcp[cli]"`, Python ≥3.10) is the standard headless client: `stdio_client` launches the server as a subprocess, `ClientSession` sends `tools/call` after `initialize()`. Async API; both context managers must wrap the session
- Before driving a bulk loop over MCP tools through the agent (push N records, fetch N entities, batch-update N rows): put the loop in a Python script using the MCP SDK. Script and agent hit the same tool surface — bug fixes land once, no agent tokens paid per record
- Before rebuilding what an MCP server already wraps (auth, token refresh, error mapping, pagination, response shaping) to escape agent context: drive the existing server from a script via the SDK. The SDK bypasses agent context without duplicating infrastructure
- The same principle applies to subagents — delegating bulk MCP work to a subagent shifts where tokens are paid but does not eliminate them; a script bypasses agent context entirely
- Before integrating with an external service that already publishes an MCP server: prefer the published server over rolling a custom client; community catalogs of MCP servers grow ahead of bespoke integrations
- Server-authoring conventions (tool naming, verb shape, schema design) live in the `mcp-server` convention; this rule covers the discipline that fires before reaching for an MCP at all and the separation between agent-driven and script-driven invocation
