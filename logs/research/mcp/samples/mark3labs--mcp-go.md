# Sample

## Identification

### url

https://github.com/mark3labs/mcp-go

### stars

8,600

### last-commit

April 14, 2026 (v0.48.0 release)

### license

MIT

### default branch

main

### one-line purpose

Go MCP SDK — framework for building MCP servers in Go.

## Language and runtime

### language(s) + version constraints

Go 1.25.5+

### framework/SDK in use

Anthropic's Model Context Protocol (MCP) specification; Go stdlib net/http

## Transport

### supported transports

Stdio, SSE (Server-Sent Events), Streamable HTTP

### how selected

Separate entry point methods: `server.ServeStdio()`, `server.ServeSSE()`, `server.ServeHTTP()`

## Distribution

### every mechanism observed

go get, source build

### published package name(s)

github.com/mark3labs/mcp-go (Go module)

### install commands shown in README

`go get github.com/mark3labs/mcp-go`

## Entry point / launch

### command(s) users/hosts run

Server initialization via `server.NewMCPServer()` constructor; transport method determines launch (stdio, SSE, or HTTP listener)

### wrapper scripts, launchers, stubs

None documented; applications embed the SDK directly

## Configuration surface

### how config reaches the server

Code-level configuration via functional options pattern: `WithToolCapabilities()`, `WithTaskCapabilities()`, `WithMaxConcurrentTasks()`, `RegisterSession()`, middleware registration for tools/prompts/recovery

## Authentication

### flow

Session registration via `RegisterSession()` method; no explicit auth mechanism documented — delegated to transport layer

### where credentials come from

Application-specific, not centralized in SDK

## Multi-tenancy

### tenancy model

Per-request via session registration; notification channels support per-client state management

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools, Resources, Prompts, Sessions (per-client state), Notifications, Request hooks for telemetry, Recovery middleware for panics

## Observability

### logging destination + format, metrics, tracing, debug flags

Request hooks for telemetry across all functionality; Recovery middleware captures tool execution panics; Session tracking with notification channels for per-client events

## Host integrations shown in README or repo

### Claude Desktop

Not explicitly documented in provided content

### Claude Code

Not documented

### pitfalls observed

No host-specific integrations documented; SDK expects applications to handle host integration

## Claude Code plugin wrapper

### presence and shape

Not present; this is an SDK for building servers, not a server itself

## Tests

### presence, framework, location, notable patterns

Test framework present (Go stdlib testing); located in `*_test.go` files and `e2e/` directory; patterns include end-to-end tests and unit tests for core functionality

## CI

### presence, system, triggers, what it runs

GitHub Actions; workflows present: `ci.yml` (main testing), `golangci-lint.yml` (linting), `pages.yml` (documentation), `release.yml` (release automation); triggers on push/PR

### pitfalls observed

Explicit language version tested in CI not confirmed (go.mod specifies 1.25.5 but CI workflow content not fully detailed).

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not present for the SDK itself; examples may include containerization

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

20 example implementations included covering client, server, HTTP, SSE, OAuth, roots, sampling, structured tools, tasks; patterns for in-process integration and custom transports

## Repo layout

### single-package / monorepo / vendored / other

Single-package SDK; organized by functionality: `mcp/` (protocol), `client/`, `server/`, `util/`, `mcptest/`, `examples/`, `e2e/`, `.github/`

## Notable structural choices

Request lifecycle hooks enable custom observability without modifying core code. Session-based per-client state management allows multi-user scenarios. Separate entry methods for different transports avoid configuration complexity. 20+ examples covering diverse patterns suggest strong developer onboarding focus. No built-in authentication in SDK; delegates to transport/application layer.

## Unanticipated axes observed

Task-augmented tool execution (asynchronous with concurrency limits) differentiates this SDK from basic tool registries. Recovery middleware for panics in tool handlers is an unusual operational safety feature. Notification channels for client-specific events support event-driven server architectures.

## Gaps

Explicit language version tested in CI not confirmed (go.mod specifies 1.25.5 but CI workflow content not fully detailed). Docker containerization patterns for production deployment not documented in SDK itself. CI workflow files in `.github/workflows/ci.yml` could be examined for test framework confirmation.
