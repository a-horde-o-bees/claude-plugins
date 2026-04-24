# Smithery Registry + CLI

## Identification
- url: https://smithery.ai/ (docs at https://smithery.ai/docs)
- type: registry / hosting platform
- author: Smithery (commercial)
- last-updated: active
- authority level: community / commercial

## Scope
"Largest open marketplace of MCP servers" — registry, discovery, and operational infrastructure for MCP. Offers **Smithery Connect** (managed OAuth and credential handling when your app integrates MCP servers), an MCP-over-HTTP interface to Smithery's own docs (`https://smithery.ai/docs/mcp`), markdown-export of docs, and reference implementations for agents (basic scaffolds, ChatGPT app examples). Publishing path documented in "Publish MCP Servers" quickstart.

## Takeaway summary
Smithery occupies the "infrastructure" corner of the registry landscape: beyond listing, they offer a managed OAuth + credential layer so a consuming application doesn't have to handle per-server auth flows. Their docs are exposed as an MCP server themselves, which is a nice dogfooding pattern for agents learning to consume Smithery. If you're publishing a server and want managed hosting + auth handling without building it yourself, Smithery is a practical path; if you just want listing, the official registry costs less.

## Use for
- Is there a managed OAuth / credentials layer for MCP I can adopt?
- How do I publish an MCP server to Smithery specifically?
- Where can I consume Smithery's docs as an MCP server (agent-friendly)?
- What example agent scaffolds exist?

## Relationship to other resources
Commercial peer of Glama / PulseMCP / mcp.so. Complements the official registry (`registry-official.md`) with hosting + auth plumbing that the official registry deliberately doesn't provide.

## Quality notes
Commercial product — feature boundary between free and paid tiers changes; check pricing before assuming a feature is freely available.
