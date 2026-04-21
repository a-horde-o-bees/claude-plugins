# Python SDK README

## Identification
- url: https://github.com/modelcontextprotocol/python-sdk
- type: SDK docs
- author: Model Context Protocol project (Anthropic-maintained)
- last-updated: active
- authority level: official

## Scope
The official Python SDK for MCP. The README is the primary reference for transports (stdio, SSE, Streamable HTTP), the FastMCP high-level API (`@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()` decorators), auto-schema generation from Python type hints and Pydantic models, OAuth 2.1 resource-server authentication (RFC 9728 Protected Resource Metadata, `TokenVerifier` protocol), development ergonomics (`uv run mcp dev server.py` for hot reload, MCP Inspector), structured vs unstructured tool output, and stateful vs stateless streaming HTTP modes.

## Takeaway summary
The Python SDK is organized in two layers: a low-level protocol-faithful API and **FastMCP**, a decorator-based high-level API that produces the same wire protocol with far less ceremony. For production, prefer Streamable HTTP (the recommended transport — SSE is being superseded); stdio remains right for local-only integrations. Type annotations on tool functions are load-bearing: return type annotations determine whether output is structured (validated against schema) or plain string. OAuth support treats the MCP server as a resource server; a separate authorization server issues tokens and the SDK verifies them via a `TokenVerifier`. The Inspector (`npx -y @modelcontextprotocol/inspector`) is the canonical debugging tool and is referenced throughout.

## Use for
- Which transports does the Python SDK support and which should I use in production?
- What's the relationship between the low-level API and FastMCP?
- How do I wire OAuth into an MCP server?
- How does schema generation work from type hints?
- How do I run the dev loop with hot reload?

## Relationship to other resources
FastMCP in this SDK is the upstream-absorbed version of jlowin/fastmcp. For advanced FastMCP patterns, see `fastmcp-docs.md`. Tutorial-level usage is at `mcp-build-server-tutorial.md`.

## Quality notes
GitHub README is long and example-heavy; skim the table of contents. Always cross-check against the spec revision in `mcp-specification.md` when wire-level details matter.
