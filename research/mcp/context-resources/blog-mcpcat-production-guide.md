# MCP Server Best Practices — Production-Grade Development Guide (MCPcat)

## Identification
- url: https://mcpcat.io/blog/mcp-server-best-practices/
- type: blog post
- author: Kashish Hora (co-founder, MCPcat)
- last-updated: 2025-07-10
- authority level: community

## Scope
Practical guide covering: tool design philosophy (workflow-oriented, not API-call-per-tool), organization at scale (namespace conventions like `category/tool`, dynamic toolsets, multi-server decomposition for large deployments), transport protocol migration from SSE to Streamable HTTP, primitive selection (tools vs resources vs prompts — state-change vs read-only vs reusable templates), and production monitoring.

## Takeaway summary
The strongest insight is the workflow-bundling point: design tools around what users are trying to accomplish, not around the underlying API surface. This reduces approval friction (one user-facing action = one tool prompt) and gives the LLM a cleaner decision surface. The namespace convention (`category/tool`) becomes necessary once you cross ~30 tools in a single server. Article references official GitHub and AWS examples for credibility. Monitoring section is promotional for MCPcat's product — take that as marketing while keeping the upstream design advice.

## Use for
- How should I shape tool granularity for good LLM decision-making?
- What naming convention works for larger tool inventories?
- When should I split one server into multiple vs adopting dynamic toolsets?
- What's the SSE → Streamable HTTP migration path?

## Relationship to other resources
Overlaps substantially with `blog-15-best-practices-mcp-production.md` on tool design + transport; complements it with more emphasis on workflow-level tool shape.

## Quality notes
Mixed: design advice is solid and grounded; monitoring section functions as a MCPcat product pitch. Skim selectively.
