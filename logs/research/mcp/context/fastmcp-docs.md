# FastMCP Documentation Site (gofastmcp.com)

## Identification
- url: https://gofastmcp.com/
- type: framework docs
- author: Jeremiah Lowin / PrefectHQ
- last-updated: reflects `main` branch; features tagged with version-introduced badges
- authority level: semi-official

## Scope
Full documentation site for FastMCP. Three-pillar structure: Servers, Clients, Apps. Covers getting started (install, quickstart), server-building fundamentals, implementation patterns (tools, resources, prompts, mounting, composition, middleware), client usage (local + remote + programmatic + CLI), app development (interactive UIs in conversations), authentication, deployment (including PrefectHQ's "Prefect Horizon" hosted platform). Available as web pages, llms.txt / llms-full.txt, individual `.md` URLs, and the docs site is itself exposed as an MCP server for programmatic access.

## Takeaway summary
This is where FastMCP's depth lives — the README points here and the SDK README defers here for anything beyond decorator basics. Version badges on features mean you can trace when capabilities landed. The llms-full.txt export is the right thing to feed an agent that needs complete FastMCP context. For production Python servers, the deployment section is the one to read carefully: transport choice, auth patterns, session management, and operational guidance all live here rather than in the SDK.

## Use for
- How do I compose multiple MCP servers or mount one inside another?
- What middleware / hook points does FastMCP expose?
- How do I expose an existing OpenAPI spec as MCP tools?
- What authentication patterns are documented end-to-end?
- How do I test an MCP server in-process via the FastMCP client?
- Where's the canonical llms.txt for feeding this into an agent?

## Relationship to other resources
Detailed docs for the framework captured in `fastmcp-readme.md`. Supersedes the Python SDK docs (`python-sdk-readme.md`) for FastMCP-specific patterns — the two agree on basics but FastMCP v2/v3 extends.

## Quality notes
High production value. Version badges help calibrate "will this feature be in the version my users have." The mcp-server-over-the-docs is worth knowing about — it lets an agent consume this documentation through the same protocol it's learning to implement.
