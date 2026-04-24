# MCP-Native Middleware with FastMCP 2.9 (Jeremiah Lowin)

## Identification
- url: https://jlowin.dev/blog/fastmcp-2-9-middleware
- type: blog post
- author: Jeremiah Lowin (FastMCP author)
- last-updated: 2025-06-23
- authority level: semi-official — author maintains FastMCP

## Scope
Design-rationale blog post from FastMCP's creator on the 2.9 middleware system. Rather than wrapping raw JSON-RPC messages, FastMCP middleware wraps the high-level, semantic handlers (tools, resources, prompts). Developers subclass `Middleware` and override hooks like `on_message` or `on_call_tool` to work with high-level Tool and Resource objects. Example: a `PrivateMiddleware` that blocks access to tools tagged `private` by inspecting the FastMCP Tool object directly.

## Takeaway summary
The key design move: middleware at the semantic layer, not the protocol layer. This means auth/logging/caching/rate-limiting is expressed in terms of "tool being called with this signature" rather than "JSON-RPC message with this method name." Idiomatic Python inheritance + method overrides, not decorators, because middleware compose in pipelines. The post also flags 2.9's auto-conversion of prompt arguments (native Python types in, JSON out of the wire). Read this when designing cross-cutting concerns for a FastMCP server — the mental model shapes how you structure auth and observability.

## Use for
- How should I structure cross-cutting concerns (auth, logging, caching, rate-limiting) in a FastMCP server?
- What's the difference between protocol-layer and semantic-layer middleware and why does it matter?
- Which hooks does FastMCP middleware expose?

## Relationship to other resources
Companion to `fastmcp-docs.md` (the full reference) with design rationale the docs don't explain. Overtaken in scope by the 3.0 post (`blog-jlowin-fastmcp-3.md`) but still the cleanest explanation of the middleware model.

## Quality notes
High-signal. Author-maintained blog; content is stable for the 2.9 model. Some of the pre-built middleware templates the post mentions have since expanded — check `gofastmcp.com` for the current catalog.
