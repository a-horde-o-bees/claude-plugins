# Official MCP Registry

## Identification
- url: https://registry.modelcontextprotocol.io/ (repo: https://github.com/modelcontextprotocol/registry)
- type: registry
- author: Model Context Protocol project (maintainers include Anthropic, PulseMCP, GitHub, Stacklok)
- last-updated: API v0.1 frozen on 2025-10-24; preview launched 2025-09-08
- authority level: official

## Scope
The community-governed official registry for MCP servers. REST API with live docs at `/docs`; production at registry.modelcontextprotocol.io, staging at staging.registry.modelcontextprotocol.io, plus a `localhost:8080` dev endpoint. Publishing via `mcp-publisher` CLI. Server registration format is a `server.json` with structured metadata. Supports GitHub OAuth, GitHub OIDC (for GitHub Actions publishing), and DNS/HTTP verification for domain ownership.

## Takeaway summary
This is the neutral, cross-vendor registry — distinct from Anthropic's own `api.anthropic.com/mcp-registry` and from commercial registries (Smithery, Glama, PulseMCP, mcp.so). API is frozen at v0.1 as of late 2025, making it safe for integrators to build against, though the project itself is still preview and "breaking changes or data resets may occur" in principle. Publishing is via the `mcp-publisher` CLI with multiple auth paths — GitHub OIDC means a GitHub Actions workflow can publish without stored secrets. If you're publishing a server and want one canonical home, this is the one with the strongest governance claim.

## Use for
- Where should I publish a new MCP server to reach the broadest audience?
- What's the machine-readable format for server metadata?
- How do I publish via GitHub Actions (OIDC, no stored secrets)?
- What's the API surface for a client that wants to list or query servers?

## Relationship to other resources
Upstream of the commercial registries (many mirror or seed from this). Distinct from Anthropic's internal `api.anthropic.com/mcp-registry` used by Claude Code's embedded registry UI. Community-governed, multi-vendor.

## Quality notes
Preview status means API contracts are stable in practice but not formally guaranteed. The `server.json` schema is worth reading before you design metadata for your server.
