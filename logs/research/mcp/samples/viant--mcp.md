# Sample

## Identification

### url

https://github.com/viant/mcp

### stars

4

### last-commit

March 19, 2026 (v0.14.0 release)

### license

Apache License 2.0

### default branch

main

### one-line purpose

Go MCP SDK (Viant) — framework for building MCP servers in Go.

## 1. Language and runtime

### language(s) + version constraints

Go (no explicit version constraint specified).

### framework/SDK in use

Anthropic's Model Context Protocol (MCP); JSON-RPC 2.0 communication base.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

HTTP/SSE (Server-Sent Events), Streamable HTTP, Stdio.

### how selected

Configurable via functional options: `WithStreamableURI()`, `WithSSEURI()`, `WithSSEMessageURI()`; separate entry points `stdioSrv.ListenAndServe()` and `srv.HTTP()`.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

go get, standalone bridge binary, source build.

### published package name(s)

github.com/viant/mcp (Go module).

### install commands shown in README

`go get github.com/viant/mcp`

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

Stdio: `stdioSrv.ListenAndServe()`, HTTP/SSE: `srv.HTTP(context.Background(), ":4981").ListenAndServe()`, Streamable HTTP: via `UseStreamableHTTP(true)` configuration.

### wrapper scripts, launchers, stubs

Bridge binary available as standalone alternative to embedding Go package.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Functional options pattern: transport-specific URI paths (`WithStreamableURI`, `WithSSEURI`, `WithSSEMessageURI`), root redirect routing (`WithRootRedirect`).

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

OAuth2/OIDC support with two modes: global resource protection via bearer tokens, fine-grained tool/resource control (experimental); client-side automatic token acquisition via "401 challenge, discovers protected resource metadata, acquires tokens and retries".

### where credentials come from

OAuth2/OIDC discovery; bearer tokens in Authorization header.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

Per-request via bearer token; OAuth2 discovery enables per-request tenant identification.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Server: resource management, prompting, tool invocation, subscriptions, logging, progress reporting, request cancellation. Client: roots, sampling, elicitation.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

`Logging()` method for setting log levels; Progress reporting and request cancellation capabilities.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

Not explicitly documented.

### Claude Code

Not documented.

### Other

No host-specific integration documentation.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present; this is a library/SDK for building MCP applications.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

Go stdlib testing; test files include `client.go` (client tests) and `server.go` (server tests) patterns; GitHub repository includes examples directory.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions configured; typical Go project structure implies test and lint workflows.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not documented in provided content.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Example code available in `/example` directory demonstrating server implementation, authentication/authorization, client usage, and bridge binary.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single-package library; structure: root-level `client.go`, `server.go`, `doc.go`; subdirectories for `/bridge`, `/client`, `/server`, `/internal`, `/docs`, `/example`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Bridge binary provides standalone MCP-to-tool bridging without requiring Go embedding.

OAuth2/OIDC support with automatic token discovery and refresh is built-in.

Separate client and server implementations with clear API boundaries.

Fine-grained resource/tool control is experimental but acknowledged.

## 18. Unanticipated axes observed

OAuth2 automatic token acquisition on 401 response is an unusual client-side feature for MCP servers.

Fine-grained authorization (experimental) suggests multi-user workspace scenarios being designed for.

## 20. Gaps

Specific Go version constraints not documented. CI/CD workflows not fully examined. Docker containerization patterns not documented. Language version tested in CI not confirmed.
