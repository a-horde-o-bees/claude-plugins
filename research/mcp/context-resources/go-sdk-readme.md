# Go SDK README

## Identification
- url: https://github.com/modelcontextprotocol/go-sdk
- type: SDK docs
- author: Model Context Protocol project (maintained collaboratively by Anthropic and Google)
- last-updated: active; GA
- authority level: official

## Scope
Official Go SDK for MCP. Packages: `mcp` (client and server API), `jsonrpc` (custom transport hook), `auth` + `oauthex` (OAuth). Ships `StdioTransport` and `CommandTransport`. API is idiomatic Go — struct-typed tool inputs/outputs with JSON schema annotations, handlers registered via `mcp.AddTool`. Licensed Apache 2.0 for new code (MIT for pre-existing).

## Takeaway summary
GA and production-ready. The Go SDK leans hard into struct-first tool definitions: declare input and output structs with JSON tags and schema annotations, register a handler with `mcp.AddTool`, and run the server over whichever transport you wired up. This maps well to Go's standard-library idioms — no codegen, no build-time schema files. The `CommandTransport` is useful for running an MCP server as a child process of another Go program, e.g. for testing.

## Use for
- What does a production-ready Go MCP server look like?
- How do I expose OAuth validation from Go?
- What is the transport abstraction I implement for a custom protocol?
- Who maintains this SDK?

## Relationship to other resources
Go counterpart to the Python and TypeScript SDKs. Co-maintained with Google — largest non-Anthropic upstream collaboration among the SDKs.

## Quality notes
Shorter README than Python/TS equivalents; depth is in GoDoc. Reach for `pkg.go.dev/github.com/modelcontextprotocol/go-sdk` for per-symbol docs.
