# appcypher/awesome-mcp-servers

## Identification
- url: https://github.com/appcypher/awesome-mcp-servers
- type: awesome list
- author: appcypher (community)
- last-updated: active
- authority level: community

## Scope
~30+ categories with emoji-tagged section headers covering File Systems, Databases, Cloud Storage, Version Control, Communication, Gaming, Finance, Research & Data, etc. 200+ listed servers. Marks official implementations with a star. Numbers multiple implementations of the same service. Each entry has a description and GitHub link. Includes a supported-clients table (Claude Desktop, Zed, Cursor, and others). 5.4k stars, 1.3k forks.

## Takeaway summary
Differentiator: explicit security warning about unsandboxed MCP servers executing arbitrary code, with a linked best-practices section (use official, review code, limit permissions). Numbering multiple implementations per service is a nice affordance when four different people have built a Postgres server. If you want a list that also tries to educate readers on the security model, this is the one to send new users to.

## Use for
- Which MCP servers exist by functional category (emoji-indexed)?
- What's the plain-English security warning to show new users?
- When multiple implementations exist for the same target system, which ones are there?

## Relationship to other resources
Peer of punkpeye and wong2. Distinguishing features: category depth, numbered duplicates, and the explicit security posture.

## Quality notes
Security warning is editorial — not a substitute for per-server audit — but more than the other lists offer. Category emojis help scanning but are not machine-parseable if you're building tooling on top of the list.
