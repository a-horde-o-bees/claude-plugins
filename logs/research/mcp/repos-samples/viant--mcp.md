# Sample

Mirrors of `https://github.com/viant/mcp`. Viant Go MCP SDK — framework/library for building MCP servers in Go with built-in OAuth2/OIDC support and a standalone bridge binary alternative for non-Go consumers. 4 stars, Apache-2.0, default branch `main`, v0.14.0 (March 19, 2026).

## Server runtime

### Go with custom MCP implementation

Go SDK that hand-rolls protocol handling against JSON-RPC 2.0 base; consumers can either embed the library (`go get github.com/viant/mcp`) or run a packaged executable. Functional-options API (`WithStreamableURI`, `WithSSEURI`, `WithSSEMessageURI`, `WithRootRedirect`); separate `client.go`/`server.go` packages; out-of-process bridge binary for non-Go consumers; built-in OAuth2/OIDC support that most Python/TypeScript SDKs delegate to the host.

## Transport

### Streamable HTTP

Streamable HTTP supported via `UseStreamableHTTP(true)` configuration; URI configured via `WithStreamableURI()`.

### SSE (Server-Sent Events)

HTTP/SSE transport — server entry point `srv.HTTP(context.Background(), ":4981").ListenAndServe()`. Configured via `WithSSEURI()` and `WithSSEMessageURI()` for the response and message endpoints.

### stdio

stdio entry point `stdioSrv.ListenAndServe()`.

### Selection mechanism

Functional options (in-code configuration) — caller assembles the server with composable option functions (`WithStreamableURI()`, `WithSSEURI()`, `WithSSEMessageURI()`) before starting it. Suited to library/SDK projects where the consumer is another program rather than an end user.

### Custom or experimental transports

SDK exposes a transport interface so consumers can plug in their own.

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

Server-side: resource management, prompting, tool invocation, subscriptions, logging, progress reporting, request cancellation. Client-side: roots, sampling, elicitation. Full spec coverage for both sides.

### Sampling and elicitation as client primitives

SDK exposes the client-side MCP primitives (sampling, elicitation, roots) for applications building agents on top of MCP.

## Configuration delivery

### Functional options at construction (code-level)

The SDK is a library; configuration happens at compile/build time via constructor calls and option functions (`WithStreamableURI()`, `WithSSEURI()`, `WithSSEMessageURI()`, `WithRootRedirect()`). No external config — choices baked into the consuming program's source.

## Authentication

### OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)

Two modes: global resource protection via bearer tokens (any request requires a valid bearer token), and fine-grained per-tool/resource control (still flagged experimental). Bearer tokens validated against a configured OAuth issuer/JWKS. Built-in OAuth2/OIDC support unusual for an MCP SDK — most delegate auth to the host.

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

Client-side automatic token acquisition on a 401 response — the client discovers the protected resource metadata, acquires tokens, and retries (RFC 9728). Token presented via `Authorization: Bearer` header.

## Multi-tenancy

### Per-request tenancy by inbound credential / bearer token

Per-request via bearer token; OAuth2 discovery enables per-request tenant identification. Fine-grained authorization (experimental) suggests multi-user workspace scenarios are part of the design intent.

### N/A (library, not a runtime)

Project ships scaffolding and primitives; tenancy is the consumer's concern. Library/SDK posture.

## Distribution channel

### Go module via `go get` / `go install`

`go get github.com/viant/mcp` for library consumption by other Go programs.

### Standalone bridge binary

Pre-built executable that wraps the library so non-Go programs can use it without embedding. Distributed alongside the Go-module library — non-Go tools (Python, Node, etc.) consume MCP servers backed by the library without needing a Go toolchain.

## Entry point and launch

### SDK constructor + transport-method launch

The server is a program the consumer wrote — `server.NewMCPServer()` returns a server value, then `stdioSrv.ListenAndServe()` (stdio), `srv.HTTP(context.Background(), ":4981").ListenAndServe()` (HTTP/SSE), or Streamable HTTP via `UseStreamableHTTP(true)`. The launcher is the consumer's `main`.

### Library import inside a user's handler

Consumers embed the library; for non-Go consumers, the bridge binary substitutes.

## Build and packaging

### Go modules (`go.mod` / `go.sum`)

Go module distribution — `go.mod` and `go.sum` declare and lock dependencies; consumers run `go get github.com/viant/mcp` or build from source. Bridge binary built from the same module for non-Go consumers.

## Container artifacts

### No container artifacts

Docker/containerization patterns not documented.

## Test stack

### Go stdlib testing

Standard `testing` package; test files include `client.go` (client tests) and `server.go` (server tests) patterns. Examples directory (`/example`) demonstrates server implementation, authentication/authorization, client usage, and bridge binary.

## CI

### GitHub Actions

GitHub Actions configured; typical Go project structure implies test and lint workflows.

## Host integration

### No host integration documentation

SDK-style library project — consumer is another program, not a host. No host-specific docs.

### Production reference implementation

`/example` directory points to real server implementations as references.

## Observability

### Pluggable logger sinks

`Logging()` method for setting log levels; progress reporting and request cancellation capabilities exposed as SDK primitives.

### Change-notification channels / JSON-RPC notifications

Subscription primitives and progress reporting surface server-emitted notifications.

## Repository layout

### Library with subdirectories

Go library layout: root-level `client.go`/`server.go`/`doc.go` plus subdirectories for `/bridge`, `/client`, `/server`, `/internal`, `/docs`, `/example`.

## Developer ergonomics

### Examples directory with many patterns

`/example` directory demonstrating server implementation, authentication/authorization, client usage, and bridge binary — multiple runnable patterns covering the SDK's surface.

### Programmatic embedding API

The SDK is itself the embedding surface — consumers wire `server.NewMCPServer()` into their own programs.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache License 2.0.

### Tagged release with version in changelog

Standard semver tag (v0.14.0, March 19, 2026).
