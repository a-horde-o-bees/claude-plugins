# 15 Best Practices for Building MCP Servers in Production (The New Stack)

## Identification
- url: https://thenewstack.io/15-best-practices-for-building-mcp-servers-in-production/
- type: blog post
- author: Janakiram MSV
- last-updated: 2025-09-15
- authority level: community

## Scope
Long-form article enumerating 15 production-grade practices for MCP servers. Topics covered: bounded-context design, stateless/idempotent operations (with pagination), transport selection (stdio baseline + Streamable HTTP for remote), elicitation for human-in-the-loop, OAuth 2.1 for HTTP, structured content UX (LLM-parsable + human-readable), observability (structured logs with correlation IDs, latency metrics, rate-limit hints), semantic versioning + capability discovery at handshake, decoupled prompts/resources, streaming large payloads via URI/handle (not inlining), multi-client testing with fault injection, container packaging + minimal runtime images, graceful degradation with feature flags, clean microservice API fundamentals, and consent gating for impactful actions (dry-run, diff preview).

## Takeaway summary
One of the better synthesis pieces on the topic. The 15 items are concrete enough to use as a design checklist, and the framing — balancing agent efficiency with human oversight, stateless design, security, observability — matches the direction the official spec is pushing. Two specific items that stand out: (#10) return URIs or handles for large payloads rather than inlining megabytes in tool responses, and (#13) feature-flag new capabilities (OAuth 2.1, structured content) so servers can talk to both new-spec and legacy clients without branching deployment. Safe reading for anyone doing a production readiness review of an MCP server.

## Use for
- Production-readiness checklist for an MCP server
- Handling large payloads without inlining
- Versioning and capability-discovery guidance
- Rationale for OAuth 2.1 as mandatory (not just recommended) for HTTP transports

## Relationship to other resources
Synthesizes points that are scattered across the official spec, the authorization tutorial, and several SDK docs. Complements `mcp-authorization-tutorial.md` on the security items and `mcp-specification.md` on the capability-negotiation items.

## Quality notes
Trade-publication article; polished but occasionally leans general. Use as a checklist rather than a reference — individual items reference the spec or specific tools where depth is needed.
