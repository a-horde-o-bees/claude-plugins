# Sample

## Identification

### url

https://github.com/metoro-io/mcp-golang

### stars

1,200

### last-commit

February 25, 2026

### license

MIT

### default branch

main

### one-line purpose

Alternate Go MCP SDK — framework for building MCP servers in Go.

## Language and runtime

### language(s) + version constraints

Go (no explicit version constraint specified in provided content)

### framework/SDK in use

Anthropic's Model Context Protocol (MCP) specification

## Transport

### supported transports

Stdio, HTTP (stateless request-response), Gin framework integration, SSE, custom transport support, HTTPS with custom auth (experimental, in progress)

### how selected

Selected at server initialization; patterns shown for stdlib HTTP, Gin framework, and stdio

## Distribution

### every mechanism observed

go get, source build, documentation at mcpgolang.com

### published package name(s)

github.com/metoro-io/mcp-golang (Go module)

### install commands shown in README

`go get github.com/metoro-io/mcp-golang`

## Entry point / launch

### command(s) users/hosts run

Server registration using `RegisterTool()`, `RegisterPrompt()`, `RegisterResource()`; client initialization with `Initialize()` and `CallTool()`; HTTP endpoints via standard HTTP or Gin frameworks

### wrapper scripts, launchers, stubs

None documented

## Configuration surface

### how config reaches the server

Code-level via registration methods and framework setup; Claude Desktop integration via `~/Library/Application Support/Claude/claude_desktop_config.json` with executable path and environment variables

## Authentication

### flow

Not explicitly documented; HTTPS custom auth support noted as experimental (in progress)

### where credentials come from

HTTPS custom auth (experimental); details not fully specified

## Multi-tenancy

### tenancy model

Not explicitly documented; HTTP stateless pattern suggests per-request handling

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools, Prompts, Resources with full listing and pagination support; type-safe native Go structs as arguments; automatic schema generation; bidirectional communication via stdio transport; change notifications for tools, prompts, and resources

## Observability

### logging destination + format, metrics, tracing, debug flags

Change notifications listed as supported feature; no explicit logging/metrics documented

## Host integrations shown in README or repo

### Claude Desktop

Yes; integration shown via `~/Library/Application Support/Claude/claude_desktop_config.json` with executable path and environment variables

### Claude Code

Not documented

### Metoro Kubernetes monitoring MCP server

Referenced as production use case

## Claude Code plugin wrapper

### presence and shape

Not present; this is a library for building servers

## Tests

### presence, framework, location, notable patterns

Test files present; patterns include `server_test.go` (21.7 KB), `integration_test.go` (10.1 KB); integration testing patterns

## CI

### presence, system, triggers, what it runs

GitHub Actions configured; typical Go project structure implies test and lint workflows; `.cursorrules` file present (Cursor IDE integration)

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not documented in provided content

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Server and client examples provided; documentation at mcpgolang.com; Metoro Kubernetes server as production reference implementation

### pitfalls observed

Makefile not present in provided content (no build targets documented).

## Repo layout

### single-package / monorepo / vendored / other

Single-package library; structure: root-level `client.go`, `server.go`, `content_api.go`, `prompt_api.go`, `prompt_response_types.go`, `tool_api.go`, `tool_response_types.go`, `resource_api.go`, `resource_response_types.go`; subdirectories: `internal/`, `transport/`, `resources/`, `examples/`, `docs/`, `.github/`

## Notable structural choices

Type-safe tool definitions using native Go structs with automatic schema generation. Customizable transports (stdio, HTTP, Gin) allow flexible deployment. Bidirectional communication support on stdio transport. Change notifications for resources/tools/prompts enable reactive client patterns. Pagination support on listings suggests handling of large datasets.

## Unanticipated axes observed

Integrated Gin framework support (not just stdlib HTTP) shows Django-like convenience pattern for Go. Change notifications on resources/tools/prompts support event-driven architectures. Explicit pagination support for listings is unusual in MCP implementations.

## Gaps

HTTPS custom auth marked as experimental; implementation details not documented. Specific Go version constraints not specified. Makefile not present in provided content (no build targets documented). Full CI/CD configuration not examined.
