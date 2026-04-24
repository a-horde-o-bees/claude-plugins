# MCP Inspector

## Identification
- url: https://github.com/modelcontextprotocol/inspector
- type: SDK docs / tool README
- author: Model Context Protocol project
- last-updated: active
- authority level: official

## Scope
The canonical debugging / testing tool for MCP servers. A React UI (MCPI) paired with a Node.js proxy (MCPP) that bridges browser to server. Supports stdio, SSE, and Streamable HTTP transports. Exposes form-based tool parameter input, real-time response visualization, request history, resource browsing, prompt evaluation, and config export to other clients. Ships both an interactive UI mode and a CLI mode for automation / CI.

## Takeaway summary
Run it with `npx @modelcontextprotocol/inspector` (UI on :6274, proxy on :6277). You can pass a server command directly — `npx @modelcontextprotocol/inspector node build/index.js` — to spawn your server as a child process and drive it from the UI. CLI mode makes it scriptable: call tools, list resources, evaluate prompts from the command line, suitable for CI smoke tests. Every SDK tutorial references Inspector as the recommended verify-it-works step before wiring a server into a host. If your server fails in a host but works in Inspector, the problem is the host's config or transport; if it fails in Inspector too, the problem is your server.

## Use for
- How do I quickly smoke-test a newly built MCP server?
- How can I exercise a server in CI without wiring up a full client?
- How do I get a ready-to-paste config snippet for Claude Desktop / Cursor / etc.?
- Which transports can I test?

## Relationship to other resources
Referenced by every SDK tutorial. If a host integration doc says "test the server works first," this is what it means.

## Quality notes
Active and well-maintained. The CLI mode is under-advertised — worth reading that section of the README if you intend to automate.
