# Sample

Mirrors of `https://github.com/metoro-io/mcp-golang`. Alternate Go MCP SDK — framework for building MCP servers in Go; emphasizes type-safe Go-struct tool args, integrated Gin framework support, and explicit pagination. 1,200 stars, MIT, default branch `main`, last commit February 25, 2026.

## Server runtime

### Go with metoro-io/mcp-golang or alternative SDK

Go program importing `github.com/metoro-io/mcp-golang` as an alternative third-party MCP SDK. Tools/resources/prompts registered via constructor and method calls (`RegisterTool()`, `RegisterPrompt()`, `RegisterResource()`); client side initialized with `Initialize()` and `CallTool()`. Single-binary distribution; no specific Go version constraint surfaced in provided content.

## Transport

### stdio

Bidirectional communication supported on stdio transport.

### Streamable HTTP

HTTP support via Go stdlib HTTP and via Gin framework integration; stateless request-response pattern.

### SSE (Server-Sent Events)

SSE supported as one of the offered transports.

### Custom or experimental transports

Documented support for custom transports, including "HTTPS with custom auth" marked experimental (in progress).

### Selection mechanism

Selected at server initialization; patterns shown for stdlib HTTP, Gin framework, and stdio.

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

Tools, Prompts, Resources with full listing and pagination support; bidirectional communication via stdio; change notifications for tools, prompts, and resources.

### Runtime tool registration API

`RegisterTool()`, `RegisterPrompt()`, `RegisterResource()` programmatic registration API.

## Configuration delivery

### Functional options at construction (code-level)

Code-level configuration via registration methods and framework setup.

### Host-side JSON config snippet

Claude Desktop integration via `~/Library/Application Support/Claude/claude_desktop_config.json` with executable path and environment variables.

## Authentication

### Application-delegated (SDK provides nothing)

No explicit auth mechanism; delegated to transport/application layer. HTTPS custom auth marked as experimental (in progress); details not fully specified.

## Multi-tenancy

### N/A (library, not a runtime)

HTTP stateless request-response pattern; tenancy not explicitly documented and depends on application implementation.

## Distribution channel

### Go module via `go get` / `go install`

`go get github.com/metoro-io/mcp-golang`; documentation hosted at `mcpgolang.com`.

## Build and packaging

### Go modules (`go.mod` / `go.sum`)

Standard Go module — `go.mod` declares module path `github.com/metoro-io/mcp-golang` and resolves dependencies via the Go toolchain. No specific Go version constraint surfaced in the captured content. Library distribution; the build artifact is whatever the consuming application produces.

## Entry point and launch

### SDK constructor + transport-method launch

Server registration via `RegisterTool()`/`RegisterPrompt()`/`RegisterResource()`; HTTP endpoints constructed via standard HTTP or Gin framework patterns; client initialization with `Initialize()` and `CallTool()`.

## Schema and types

### Go automatic schema generation

Type-safe tool definitions using native Go structs with automatic schema generation.

## Test stack

### Go stdlib testing

Test files present: `server_test.go` (21.7 KB), `integration_test.go` (10.1 KB); patterns include integration testing.

## CI

### GitHub Actions

GitHub Actions configured; typical Go project structure implies test and lint workflows.

## Observability

### Change-notification channels / JSON-RPC notifications

Change notifications listed as a supported feature for resources/tools/prompts; supports event-driven server architectures.

## Host integration

### Claude Desktop

Integration documented via `~/Library/Application Support/Claude/claude_desktop_config.json` with executable path and environment variables.

### Production reference implementation

Metoro Kubernetes monitoring MCP server referenced as a production use case; documentation at `mcpgolang.com`.

## Repository layout

### Library with subdirectories

Single-package library; root-level `client.go`, `server.go`, `content_api.go`, `prompt_api.go`, `prompt_response_types.go`, `tool_api.go`, `tool_response_types.go`, `resource_api.go`, `resource_response_types.go`; subdirectories: `internal/`, `transport/`, `resources/`, `examples/`, `docs/`, `.github/`.

## Documentation surface

### README plus docs directory

`/docs` directory present alongside README; hosted documentation at `mcpgolang.com`.

### Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)

`.cursorrules` file present (Cursor IDE integration).

## Developer ergonomics

### Examples directory with many patterns

Server and client examples provided; integrated Gin framework support shows Django-like convenience pattern for Go.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT license.

### Active development

Last commit February 25, 2026.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

This is a library for building servers, not a server itself; no Claude Code wrapper.
