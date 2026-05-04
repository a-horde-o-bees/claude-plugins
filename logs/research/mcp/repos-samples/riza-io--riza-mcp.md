# Sample

Mirrors of `https://github.com/riza-io/riza-mcp`. Riza code-interpreter MCP server — sandboxed code execution exposed as MCP tools, with separate save/run/edit/list patterns. 14 stars, default branch `main`.

## Server runtime

### Node.js / TypeScript with official MCP SDK

JavaScript (72.2%), TypeScript (27.8%); Node.js runtime; Anthropic's Model Context Protocol (MCP) specification.

## Transport

### stdio

Inferred as stdio based on npm distribution pattern; transports not explicitly specified in provided content.

### Selection mechanism

Standard MCP transport selection; details not documented.

## Capability surface

### Single code-execution tool with sandbox

Six tools centered on sandboxed code execution: `create_tool` (save code as reusable tools), `fetch_tool` (retrieve saved tools with source code), `execute_tool` (run saved tools securely), `edit_tool` (modify existing tools), `list_tools` (view available tools), `execute_code` (run arbitrary code without saving). Isolated code execution is Riza's core value proposition.

### User-publishable tools

`create_tool` saves arbitrary code as reusable tools with `edit_tool` capability — separate patterns for saved vs. arbitrary code execution. The `edit_tool` operation modifies existing saved tools at runtime, making the saved-tool surface mutable rather than publish-once-and-immutable.

## Configuration delivery

### Environment variables

`RIZA_API_KEY` environment variable for credentials.

### Host-side JSON config snippet

Claude Desktop JSON configuration example.

## Authentication

### Static API key / token via env var

Riza API key set via `RIZA_API_KEY` environment variable; "Get a free Riza API key in your Riza Dashboard".

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per API key; multi-user via separate API keys.

## Distribution channel

### npm via npx / bunx

NPM package registry via npx; package name `@riza-io/riza-mcp`. `npx @riza-io/riza-mcp` (assumed from npm distribution pattern).

## Entry point and launch

### `npx -y <package>` / `bunx`

Configured through Claude Desktop or adapted for other MCP clients via command-line invocation; npm distribution pattern implies `npx`.

## Host integration

### Claude Desktop

Yes; "Configure with Claude Desktop as below, or adapt as necessary for your MCP client".

### Generic / host-agnostic snippet

Adaptable for any MCP client.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not present; configuration-based integration only.

## Documentation surface

### README as the canonical surface

README contains Claude Desktop JSON configuration example; six documented tools with clear semantics.

## Repository layout

### Single-package src-layout

Single server package with minimal structure: README.md, `/typescript/` directory containing implementation. Minimal repository structure suggests newer/actively developed project.

## Release and lifecycle

### Active development

Repository appears active; license not specified in provided content (likely MIT or Apache 2.0; default for Riza projects).
