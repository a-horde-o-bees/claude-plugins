# Rust SDK README

## Identification
- url: https://github.com/modelcontextprotocol/rust-sdk
- type: SDK docs
- author: Model Context Protocol project
- last-updated: v1.5.0 released April 2026
- authority level: official

## Scope
Official Rust SDK published as the `rmcp` crate (plus `rmcp-macros` for proc macros). Built on tokio async. Ships `TokioChildProcess` for stdio and a custom-transport extension point. Covers tools, resources, prompts, sampling, logging, and completions — full MCP feature surface.

## Takeaway summary
Procedural macros (`#[tool]`, `#[prompt]`, `#[tool_router(server_handler)]`) eliminate the MCP boilerplate — declare a struct, annotate methods, and the SDK wires JSON-RPC dispatch. Production-ready (v1.5.0, 74 releases, 3.3k stars). Async-first via tokio; the SDK itself is `await`-based. Good fit when you want type-safe tool signatures and zero-cost abstractions, or when you're embedding an MCP server in an existing Rust service.

## Use for
- What's the idiomatic Rust MCP server shape?
- Which macros remove boilerplate and what do they expand to?
- Is the Rust SDK production-ready?
- How do I add a custom transport?

## Relationship to other resources
Rust peer of the Python / TypeScript / Go / Kotlin SDKs. All consume the same spec and support the same capability surface.

## Quality notes
Active and mature for a non-Anthropic-primary-language SDK. If you're new to tokio, budget time for the async ergonomics alongside the MCP learning curve.
