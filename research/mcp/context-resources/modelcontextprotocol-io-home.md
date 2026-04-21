# modelcontextprotocol.io (home / concepts / develop / extensions)

## Identification
- url: https://modelcontextprotocol.io/
- type: spec / official docs site
- author: Model Context Protocol project
- last-updated: active (versioned against spec revision 2025-11-25)
- authority level: official

## Scope
The public documentation site for MCP. Covers the "what is MCP" explainer, conceptual overview (hosts / clients / servers, the USB-C analogy), architecture primer, "Build servers" and "Build clients" tutorials, the extensions/apps overview, a clients listing, and links through to the normative specification. Also exposes `llms.txt` for agent-friendly navigation of the docs tree.

## Takeaway summary
The entry point for anyone new to MCP. Frames MCP as a standardized integration layer between LLM hosts and external systems, with three role names (host, client, server) that are worth internalizing because every downstream doc uses them precisely. The "Build servers" path funnels to the concrete tutorial; the "Understand concepts" path funnels to the architecture primer that makes sense of the spec. When starting from zero, read the concepts and architecture pages here before opening any SDK README.

## Use for
- Where do I start if I have never seen MCP before?
- What vocabulary (host, client, server, resources, prompts, tools, sampling, roots, elicitation) does the rest of the ecosystem expect me to know?
- What does a hello-world MCP server look like end-to-end?
- Which hosts/clients currently speak MCP?
- Where is `llms.txt` so I can point an agent at the docs?

## Relationship to other resources
Parent of `mcp-specification.md` (the `/specification/latest` subtree). The home page describes the protocol conversationally; the spec page defines it normatively. Also links out to `modelcontextprotocol/servers` (reference implementations) and the inspector.

## Quality notes
Written as marketing-flavored explainer in places, but the concepts pages are precise. Always cross-reference with the spec when a detail matters.
