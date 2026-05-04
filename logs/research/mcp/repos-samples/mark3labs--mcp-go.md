# Sample

Mirrors of `https://github.com/mark3labs/mcp-go`. Go MCP SDK — framework for building MCP servers in Go; widely-adopted community SDK. 8,600 stars, MIT, default branch `main`, last commit April 14, 2026 (v0.48.0).

## Server runtime

### Go with mark3labs/mcp-go SDK

Go 1.25.5+ library exposing constructors, registration calls (`server.NewMCPServer()`, `RegisterSession()`), and transport-method launch points. Uses Go stdlib `net/http` for HTTP-tier needs. Native Go structs become tool arguments with automatic JSON-Schema generation. Distributed as `github.com/mark3labs/mcp-go`. Library, not a runnable server itself — applications embed the SDK.

## Transport

### stdio

`server.ServeStdio()` entry method.

### SSE (Server-Sent Events)

`server.ServeSSE()` entry method.

### Streamable HTTP

`server.ServeHTTP()` entry method.

### Selection mechanism

Separate entry points per transport — caller picks `ServeStdio()` / `ServeSSE()` / `ServeHTTP()` at code level rather than via runtime config.

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

SDK supports Tools, Resources, Prompts, plus Sessions (per-client state), Notifications, request hooks for telemetry, and Recovery middleware that catches panics in tool handlers.

### Runtime tool registration API

Server exposes a programmatic API for registering tools/resources/prompts via constructor and method calls.

## Configuration delivery

### Functional options at construction (code-level)

Configuration via functional options pattern — `WithToolCapabilities()`, `WithTaskCapabilities()`, `WithMaxConcurrentTasks()`, `RegisterSession()`, plus middleware registration for tools/prompts/recovery. Choices baked into the consuming program's source.

## Authentication

### Application-delegated (SDK provides nothing)

No auth in the SDK itself. `RegisterSession()` provides session abstraction; application wires its own auth at the transport layer.

## Multi-tenancy

### Per-session state via session registration

`RegisterSession()` plus per-client notification channels enable multi-client scenarios; the SDK supports per-session state isolation.

## Distribution channel

### Go module via `go get` / `go install`

`go get github.com/mark3labs/mcp-go`. Library use case — no published binary needed.

## Build and packaging

### Go modules (`go.mod` / `go.sum`)

`go.mod` declares module path `github.com/mark3labs/mcp-go` with Go 1.25.5+ toolchain constraint; the Go toolchain resolves dependencies and builds without a separate package manager. No published binary — consumers add the module via `go get` and the build is the application's `go build`.

## Entry point and launch

### SDK constructor + transport-method launch

Consumer's `main` calls `server.NewMCPServer()`, then dispatches via `ServeStdio()` / `ServeSSE()` / `ServeHTTP()`. The launcher is application code, not an SDK-provided binary.

## Schema and types

### Go automatic schema generation

Native Go structs become tool arguments with automatic JSON-Schema generation via the SDK's reflection. Type-safe schemas without runtime reflection cost.

## Test stack

### Go stdlib testing

Test files in `*_test.go` files plus an `e2e/` directory; patterns include end-to-end and unit tests for core functionality.

## CI

### GitHub Actions

`.github/workflows/`: `ci.yml` (main testing), `golangci-lint.yml` (linting), `pages.yml` (documentation), `release.yml` (release automation); triggers on push/PR.

### GitHub Actions plus dedicated lint config

`.golangci.yml` separately versioned; lint runs as a CI step.

### Release-cut workflow on tag push

`release.yml` for release automation triggered on tag push.

## Observability

### Request lifecycle hooks for telemetry

SDK exposes request hooks across all functionality so applications can wire OpenTelemetry, metrics, or logging without modifying SDK code. Recovery middleware captures tool execution panics so a bad tool call doesn't crash the process.

### Change-notification channels / JSON-RPC notifications

Per-client notification channels for tool/resource/prompt updates and per-client events.

## Host integration

### No host integration documentation

SDK targets application authors — host-specific integrations are the consuming application's responsibility, not the SDK's.

### Production reference implementation

20 example implementations cover client, server, HTTP, SSE, OAuth, roots, sampling, structured tools, tasks; patterns for in-process integration and custom transports demonstrate real-world wiring.

## Repository layout

### Single-package, organized subdirectories

Single-package SDK organized by functionality: `mcp/` (protocol), `client/`, `server/`, `util/`, `mcptest/`, `examples/`, `e2e/`, `.github/`.

## Developer ergonomics

### Examples directory with many patterns

20+ runnable patterns covering the full surface — client, server, HTTP, SSE, OAuth, roots, sampling, structured tools, tasks; in-process integration patterns and custom transport patterns.

### Linter and type-checker stack

`golangci-lint` configured via `.golangci.yml`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT license.

### Active development

v0.48.0 released April 14, 2026; ongoing maintenance.

### Tagged release with version in changelog

Standard semver tag (v0.48.0); release pipeline produces tagged releases.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

This is an SDK for building servers, not a server itself; no Claude Code wrapper.
