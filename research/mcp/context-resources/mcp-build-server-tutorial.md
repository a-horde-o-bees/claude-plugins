# MCP Build-a-Server Tutorial

## Identification
- url: https://modelcontextprotocol.io/docs/develop/build-server
- type: spec / official docs site (tutorial)
- author: Model Context Protocol project
- last-updated: active
- authority level: official

## Scope
The canonical hello-world tutorial for building an MCP server. Walks through a `weather` server exposing two tools (`get_alerts`, `get_forecast`) against the NWS API, with full code shown in Python, Node/TypeScript, Java, Kotlin, C#, and other SDK tabs. Covers prerequisites (Python 3.10+, `uv`, SDK ≥1.2.0), project init, FastMCP class usage, the `@mcp.tool()` decorator, the stdio logging gotcha, and the wiring to Claude for Desktop via `claude_desktop_config.json`. Links to `modelcontextprotocol/quickstart-resources` for complete sample repos.

## Takeaway summary
The official paved path: use FastMCP (Python) or the equivalent high-level API in other SDKs. Define tools as decorated functions with type hints and a docstring — the SDK generates the JSON schema and tool description from that. The single most important gotcha it surfaces: **never write to stdout in a stdio-based MCP server**; `print()` corrupts the JSON-RPC framing. Use a logger writing to stderr or a file. Reading this tutorial before designing a new server gives you the canonical project shape (uv project layout, `httpx.AsyncClient` pattern, tool signatures that return strings), which the rest of the ecosystem mimics.

## Use for
- What's the minimal viable MCP server in language X?
- Where does stdout logging go wrong?
- What's the idiomatic project layout for a new server?
- How do I wire a freshly built server into Claude Desktop to test it?
- What do tool signatures look like in each SDK?

## Relationship to other resources
Concretizes the concepts in `modelcontextprotocol-io-home.md` and the Python SDK README (`python-sdk-readme.md`). The FastMCP usage shown here is a subset of what `fastmcp-docs.md` covers in depth.

## Quality notes
Multi-language via tabs; some tabs are more thorough than others (Python is the richest). Tutorial is introductory — for production patterns (auth, streaming, multi-tool composition) go to the SDK docs or FastMCP docs.
