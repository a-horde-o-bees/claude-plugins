# FastMCP (jlowin / PrefectHQ) README

## Identification
- url: https://github.com/jlowin/fastmcp
- type: framework docs
- author: Jeremiah Lowin / PrefectHQ
- last-updated: active; v3.2.4 at research time
- authority level: semi-official — v1 was absorbed into the official MCP Python SDK in 2024, but the standalone v2/v3 is the actively maintained flagship and is significantly more full-featured

## Scope
The most popular MCP framework in any language. Three pillars: **Servers** (tools, resources, prompts via Python decorators), **Clients** (connect to any MCP server, full protocol support), and **Apps** (interactive UIs rendered in conversations). Adds automatic schema generation from type hints, transport negotiation, authentication, protocol lifecycle management, OpenAPI integration, and "best practices built in" over the low-level SDK. Metrics at research time: ~24.7k stars, 1.9k forks, ~1M daily downloads; README claims ~70% of MCP servers across all languages use it.

## Takeaway summary
If you're building an MCP server in Python, this is the default choice — far more adoption than the low-level SDK or any competitor. Decorator-based server definition is the fast path; composition, mounting, middleware, and in-process client-server testing are the advanced surfaces that earn it "framework" status rather than "decorator library." FastMCP 1.0 was upstreamed into the Python SDK, so any Python SDK code using `from mcp.server.fastmcp import FastMCP` is running what became FastMCP-lite; v2/v3 in this repo is where new capabilities land first. The client library is independently useful — you can drive any MCP server from Python without running an LLM at all, which is the basis for a lot of testing and CI patterns.

## Use for
- Which Python MCP framework should I default to?
- What patterns does FastMCP add over the low-level SDK (composition, mounting, middleware, OpenAPI)?
- How do I write tests that exercise my server in-process without spawning it?
- How do I build an MCP client (not server) in Python?
- What authentication patterns does FastMCP support out of the box?

## Relationship to other resources
Superset of what the Python SDK's embedded `FastMCP` class does (the SDK absorbed v1). Detailed docs at `fastmcp-docs.md` (gofastmcp.com). Crucially: v2/v3 diverges from the upstream-absorbed v1 — if you're reading the SDK README and this one, prefer this one for new projects.

## Quality notes
Exceptional maintenance and adoption. The "semi-official" authority rating is because Anthropic does not maintain it, but the community has effectively canonized it — and the v1-into-SDK merge signals Anthropic's endorsement of the design. When the MCP Python SDK README and FastMCP disagree, FastMCP is usually ahead.
