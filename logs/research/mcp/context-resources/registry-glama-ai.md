# Glama MCP Registry

## Identification
- url: https://glama.ai/mcp
- type: registry
- author: Glama (commercial)
- last-updated: active
- authority level: community / commercial

## Scope
Commercial MCP server directory. "Indexes, scans, and ranks servers based on security, compatibility, and ease of use." Claims thousands of servers, 50k+ business users, and a ChatGPT-like UI for browsing. Provides an API gateway (paid) that can route through Glama's infrastructure rather than users connecting servers directly. Community presence on Discord (~2k) and Reddit.

## Takeaway summary
Glama is the commercial discovery + gateway play in the registry space. Beyond listing, they scan servers and rank them on security/compat/ease-of-use signals — useful when you want curated rather than exhaustive. The gateway product means a consuming app can treat Glama as the single endpoint for many MCP servers, offloading connection management. If you're publishing a server and want visibility to the Glama userbase, their listing process is separate from the official registry. If you're consuming MCP and want a ranked list rather than the full firehose, this is a good discovery surface.

## Use for
- Where can I find ranked MCP servers with security/quality signals?
- Is there a gateway service that can route to many MCP servers from one endpoint?
- Which servers are commercially-supported or enterprise-vetted?

## Relationship to other resources
Commercial alternative / complement to the official registry (`registry-official.md`). Similar role to Smithery and PulseMCP but with heavier ranking emphasis.

## Quality notes
Commercial: listings and rankings will reflect Glama's methodology rather than protocol-neutral criteria. Good for curated discovery; less suitable as a source of ground truth for "what exists."
