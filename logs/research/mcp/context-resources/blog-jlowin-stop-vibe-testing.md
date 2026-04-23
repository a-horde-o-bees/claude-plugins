# Stop Vibe-Testing Your MCP Server (Jeremiah Lowin)

## Identification
- url: https://jlowin.dev/blog/stop-vibe-testing-mcp-servers
- type: blog post
- author: Jeremiah Lowin (FastMCP author)
- last-updated: 2025-05-21
- authority level: semi-official

## Scope
Argument that testing MCP servers via chat interface ("does Claude figure out how to call it?") is insufficient — LLM-mediated testing is nondeterministic and cannot cover regressions. Prescribes proper unit tests: atomic, behavior-focused, regression-preventing. Concrete toolchain: pytest + FastMCP 2.0's in-memory `Client` connected directly to a `FastMCP` server instance without network/subprocess overhead. Patterns: fixture for the server, instantiate `Client` within test functions (not fixtures, to avoid event-loop conflicts), call tools via `await client.call_tool("tool_name", params)`. Same `Client` class works against remote servers, Node.js scripts, and MCP config files — so the same tests can be retargeted to different environments.

## Takeaway summary
The single most useful Python-ecosystem testing guidance for MCP servers. The in-memory client-server pattern is millisecond-fast and deterministic, which means a server with hundreds of tools can have a full regression suite that runs in seconds. Key operational detail: put the server in a fixture but instantiate the client inside each test to avoid event-loop-lifecycle issues. The same `fastmcp.Client` can later drive integration tests against a deployed remote server using the same test code — so the same suite upgrades from unit → integration by swapping the target.

## Use for
- How do I test my MCP server deterministically without spawning subprocesses?
- How should I structure pytest fixtures for FastMCP?
- Can the same test code drive both local and remote target servers?

## Relationship to other resources
Rationale for the pattern documented in `fastmcp-docs.md`'s testing page. Companion to the FastMCP middleware and 3.0 posts from the same author.

## Quality notes
High-signal and still current. The pattern extends to FastMCP 3.x — Clients in 3.0 accept any `FastMCP` server, including ones composed from Providers and Transforms.
