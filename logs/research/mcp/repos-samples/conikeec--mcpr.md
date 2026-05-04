# Sample

Mirrors of `https://github.com/conikeec/mcpr`. Rust MCP implementation library — server/client scaffolding, CLI stub generation, mock transport for testing. Archived as of February 8, 2026. 350 stars; MIT; default branch `master`.

## Server runtime

### Rust with rmcp / rust-mcp-sdk

Rust MCP scaffolding library implementing Anthropic's Model Context Protocol specification. No explicit MSRV documented; specifics discoverable in `Cargo.toml`. Library exposes server/client builders; consumers depend on `mcpr` crate to assemble their own MCP server programs.

## Transport

### stdio

Stdio supported as one of two transport options selectable at scaffold time.

### SSE (Server-Sent Events)

SSE supported as the network-transport option. Critical SSE transport issues in v0.2.0 (yanked); v0.2.3+ recommended.

### Selection mechanism

Selected via project generator at creation time: `mcpr generate-project --transport [stdio|sse]`. WebSocket planned but not yet implemented.

## Configuration delivery

### Functional options at construction (code-level)

ServerConfig builder pattern with methods like `.with_name()`, `.with_version()`, `.with_tool()`. Tool parameter schemas defined as JSON objects with properties and required field arrays. No external config — choices are baked into the consuming program's source.

## Authentication

### None / implicit (local-resource gating)

No explicit authentication mechanisms documented in the library. Transport-layer security implied for production SSE deployments; consumers handle auth in their own server code.

## Multi-tenancy

### N/A (library, not a runtime)

Library provides schema and transport abstractions but not multi-tenancy features; tenancy is the consumer's concern.

## Distribution channel

### Cargo crate / cargo install

Published to crates.io as `mcpr`. Library consumers: `cargo add mcpr = "0.2.3"`. CLI tools: `cargo install mcpr`.

## Entry point and launch

### Generated binary from scaffolded project

Project scaffolding via `mcpr generate-project --name [name]` emits client and server source. After `cargo build`, generated executables in `target/debug/` are launched as compiled binaries.

## Build and packaging

### Cargo (Rust)

Standard Cargo crate published to crates.io. Specific Rust toolchain pinning not documented in fetched content.

## Schema and types

### Rust schema crate

JSON-object schema definitions with properties and required arrays, declared via the ServerConfig builder.

## Test stack

### Mock transport layer for protocol-level testing

Mock transport implementations for testing; testing patterns for both stdio and SSE transports documented.

## CI

### GitHub Actions

GitHub Actions configured in `.github/`.

## Repository layout

### Single Rust crate

Single Rust library package; `/src/` (core library), `/examples/` (example code, including a GitHub-repository client-server demo). Documentation: `README.md`, `MCP.md`, `CHANGELOG.md`, `CONTRIBUTING.md`.

## Documentation surface

### README + examples/

README plus `/examples/` directory; example demonstrates GitHub repository interactions via complete client-server implementation.

## Developer ergonomics

### Setup subcommands on the MCP binary

`mcpr generate-project` subcommand reduces boilerplate for new MCP implementations; CLI tools included for server/client stub generation. Mock transport for testing enables fast, offline development.

## Release and lifecycle

### Archived

Repository archived as of February 8, 2026. Code still functions; no further fixes. Status as of archive: WebSocket transport planned but not implemented; v0.2.0 SSE transport yanked due to critical issues.

### License — Permissive (MIT / Apache-2.0)

MIT.
