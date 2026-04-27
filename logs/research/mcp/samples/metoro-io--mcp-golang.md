# Sample

## Identification
### url

https://github.com/metoro-io/mcp-golang

### stars

1,200

### last-commit (date or relative)

February 25, 2026

### license

MIT

### default branch

main

### one-line purpose

Alternate Go MCP SDK — framework for building MCP servers in Go.

## 1. Language and runtime
### language(s) + version constraints

Go (no explicit version constraint specified in provided content)

### framework/SDK in use

Anthropic's Model Context Protocol (MCP) specification

### pitfalls observed

none noted in this repo

## 2. Transport
### supported transports

Stdio, HTTP (stateless request-response), Gin framework integration, SSE, custom transport support, HTTPS with custom auth (experimental, in progress)

### how selected (flag, env, separate entry, auto-detect, etc.)

Selected at server initialization; patterns shown for stdlib HTTP, Gin framework, and stdio

### pitfalls observed

none noted in this repo

## 3. Distribution
### every mechanism observed

go get, source build, documentation at mcpgolang.com

### published package name(s)

github.com/metoro-io/mcp-golang (Go module)

### install commands shown in README

`go get github.com/metoro-io/mcp-golang`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch
### command(s) users/hosts run

Server registration using `RegisterTool()`, `RegisterPrompt()`, `RegisterResource()`; client initialization with `Initialize()` and `CallTool()`; HTTP endpoints via standard HTTP or Gin frameworks

### wrapper scripts, launchers, stubs

None documented

### pitfalls observed

none noted in this repo

## 5. Configuration surface
### how config reaches the server

Code-level via registration methods and framework setup; Claude Desktop integration via `~/Library/Application Support/Claude/claude_desktop_config.json` with executable path and environment variables

### pitfalls observed

none noted in this repo

## 6. Authentication
### flow

Not explicitly documented; HTTPS custom auth support noted as experimental (in progress)

### where credentials come from

HTTPS custom auth (experimental); details not fully specified

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy
### single-user / per-request tenant / workspace-keyed / not applicable / other

Not explicitly documented; HTTP stateless pattern suggests per-request handling

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed
### tools / resources / prompts / sampling / roots / logging / other

Tools, Prompts, Resources with full listing and pagination support; type-safe native Go structs as arguments; automatic schema generation; bidirectional communication via stdio transport; change notifications for tools, prompts, and resources

### pitfalls observed

none noted in this repo

## 9. Observability
### logging destination + format, metrics, tracing, debug flags

Change notifications listed as supported feature; no explicit logging/metrics documented

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo
### Claude Desktop

Yes; integration shown via `~/Library/Application Support/Claude/claude_desktop_config.json` with executable path and environment variables

### Claude Code

Not documented

### Other

Metoro Kubernetes monitoring MCP server referenced as production use case

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present; this is a library for building servers

### pitfalls observed

none noted in this repo

## 12. Tests
### presence, framework, location, notable patterns

Test files present; patterns include `server_test.go` (21.7 KB), `integration_test.go` (10.1 KB); integration testing patterns

### pitfalls observed

none noted in this repo

## 13. CI
### presence, system, triggers, what it runs

GitHub Actions configured; typical Go project structure implies test and lint workflows; `.cursorrules` file present (Cursor IDE integration)

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts
### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not documented in provided content

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics
### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Server and client examples provided; documentation at mcpgolang.com; Metoro Kubernetes server as production reference implementation

- pitfalls observed:
  - Makefile not present in provided content (no build targets documented)

## 16. Repo layout
### single-package / monorepo / vendored / other — describe what's there

Single-package library; structure: root-level `client.go`, `server.go`, `content_api.go`, `prompt_api.go`, `prompt_response_types.go`, `tool_api.go`, `tool_response_types.go`, `resource_api.go`, `resource_response_types.go`; subdirectories: `internal/`, `transport/`, `resources/`, `examples/`, `docs/`, `.github/`

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Type-safe tool definitions using native Go structs with automatic schema generation
- Customizable transports (stdio, HTTP, Gin) allow flexible deployment
- Bidirectional communication support on stdio transport
- Change notifications for resources/tools/prompts enable reactive client patterns
- Pagination support on listings suggests handling of large datasets

## 18. Unanticipated axes observed
- Integrated Gin framework support (not just stdlib HTTP) shows Django-like convenience pattern for Go
- Change notifications on resources/tools/prompts support event-driven architectures
- Explicit pagination support for listings is unusual in MCP implementations

## 20. Gaps
- HTTPS custom auth marked as experimental; implementation details not documented
- Specific Go version constraints not specified
- Makefile not present in provided content (no build targets documented)
- Full CI/CD configuration not examined
