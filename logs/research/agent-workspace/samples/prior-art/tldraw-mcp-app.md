# Prior art — tldraw MCP App

Official MCP App reference implementation — tldraw infinite canvas embedded in MCP host (Cursor, VS Code, Claude, ChatGPT). Three tools: create / edit / delete shapes; current canvas state pushed to chat context on each turn.

## Identity

- **URL:** [tldraw.dev/blog/tldraw-mcp-app](https://tldraw.dev/blog/tldraw-mcp-app)
- **License:** Research-cited as reference implementation; tldraw library itself is licensed (verify)
- **Stack:** MCP App (sandboxed iframe + JSON-RPC over postMessage) embedded in MCP host
- **Status:** Active reference for the MCP Apps protocol (ratified Jan 2026)

## Fit to our goal

**~25% — single panel type via MCP Apps protocol.** Reference for the protocol pattern itself, less for our workspace shape.

**Matches:**
- Agent integration via MCP Apps protocol (the standardized post-Jan 2026 way)
- Canvas state pushed to model context on change (event-driven, not poll-driven)
- MCP host renders the panel — clean separation of concerns
- Three-tool minimal surface (create / edit / delete shapes) — discipline lesson

**Differs:**
- Single panel type only
- Embedded in another tool's chat (Claude Desktop / Cursor / VS Code) rather than standalone workspace
- Relies on host-rendered iframes — host controls layout, not us
- Not tied to a Claude Code workflow specifically

## What to take, what to skip

**Take:** the MCP Apps event-driven state push pattern (panel emits state changes into model context; agent doesn't poll); the contract design for create/edit/delete operations (minimum viable mutation surface); tldraw as a canvas library option (alternative to Excalidraw).

**Skip:** the host-bound deployment (we want our own host); the canvas-only scope.

## Open questions for deep-dive

- What state granularity is pushed to model context — full canvas? Deltas? Summary?
- How do the create/edit/delete operations compose into more complex agent workflows?
- Would we want MCP Apps or a different protocol for our workspace? (tldraw uses MCP Apps; embedded-editor-for-claude-code uses MCP stdio + SSE; there's a choice to make.)
- tldraw vs Excalidraw — which fits our use case better?
- How does tldraw MCP App handle multiple instances in one host?
- Verifiable adoption signals across the four reference hosts (Cursor, VS Code, Claude, ChatGPT)?

## Sources

- [tldraw.dev/blog/tldraw-mcp-app](https://tldraw.dev/blog/tldraw-mcp-app)
- [MCP Apps spec](https://modelcontextprotocol.io/extensions/apps/overview) — ratified Jan 2026
- [MCP Apps blog post](https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/)
