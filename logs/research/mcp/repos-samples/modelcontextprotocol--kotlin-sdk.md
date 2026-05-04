# Sample

Mirrors of `https://github.com/modelcontextprotocol/kotlin-sdk`. Official MCP Kotlin SDK — Kotlin Multiplatform (JVM, Native, JS, Wasm). 1,300 stars, Apache-2.0 (new contributions) / MIT (existing code), default branch `main`, v0.11.1 released April 10, 2026.

## Server runtime

### Kotlin Multiplatform SDK

Official Kotlin SDK published as Maven artifacts (`io.modelcontextprotocol:kotlin-sdk*`); multiplatform targets JVM, Native, JS, and Wasm. Kotlin 2.2+ with Java 11+ for the JVM target. Coroutine-based APIs throughout. Ktor server is an optional companion for HTTP transports — engines specified independently to avoid transitive bloat. Maintained with JetBrains collaboration. Conformance testing ensures spec compliance.

## Transport

### stdio

Stdio transport.

### Streamable HTTP

Single endpoint with optional JSON-only or SSE response modes.

### SSE (Server-Sent Events)

SSE supported.

### WebSocket

`WebSocketTransport` — bidirectional persistent connection alongside stdio, SSE, and Streamable HTTP. Appropriate when both sides need symmetric streaming and the host environment already speaks WebSocket.

### In-memory / in-process channel

`ChannelTransport` for local testing — server and client share a Kotlin channel rather than serialize JSON over IPC.

### Selection mechanism

Configured at server initialization; embedded Ktor server for HTTP deployments; separate transport implementations.

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

Server side: Prompts, Resources, Tools, Completion, Logging, plus experimental features. Client side: Sampling (LLM requests), Roots (filesystem declaration), Elicitation. Pagination supported on list operations.

### Sampling and elicitation as client primitives

SDK exposes the client-side MCP primitives — sampling (LLM completion request back to the host) and elicitation (request user input via the host) — for applications building agents on top of MCP.

## Configuration delivery

### Functional options at construction (code-level)

CORS configuration for browser clients; configurable endpoint paths (default `/mcp`); transport-specific options. SDK is consumed as a library; configuration happens in the consuming program.

## Authentication

### Application-delegated (SDK provides nothing)

Auth not in SDK; delegated to transport/application layer.

## Multi-tenancy

### N/A (library, not a runtime)

SDK provides transport and protocol abstraction; multi-tenancy handled by the consuming application.

## Distribution channel

### Maven Central artifacts

`io.modelcontextprotocol:kotlin-sdk` (umbrella), `io.modelcontextprotocol:kotlin-sdk-client` (client), `io.modelcontextprotocol:kotlin-sdk-server` (server). Granular artifact split lets consumers depend on just the half they need. Install via `implementation("io.modelcontextprotocol:kotlin-sdk:x.x.x")` in Gradle.

### Source clone with editable install

Source build via Gradle.

## Entry point and launch

### SDK constructor + transport-method launch

Ktor server integration for HTTP deployments; STDIO transport for CLI tools; application-specific initialization. Sample implementations live in `./samples/`.

### Library import inside a user's handler

The SDK is a library; consumers import it into their own Kotlin/JVM applications.

## Build and packaging

### Maven / Gradle (JVM)

Maven Central artifacts via Gradle multi-module project — `kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, `kotlin-sdk` umbrella. No transitive Ktor dependencies — developers specify Ktor engines independently.

## Test stack

### End-to-end protocol-conformance harness

Conformance tests under `conformance-test/` ensure spec compliance.

### Mock transport layer for protocol-level testing

`kotlin-sdk-testing` module plus integration tests; `test-utils/` provides utilities. Knit properties used for code-snippet testing in documentation.

## CI

### GitHub Actions

GitHub Actions configured; typical Gradle/Kotlin project structure.

## Observability

### None / unspecified

No explicit observability documented; Kotlin/Ktor standard logging available to consumers.

## Host integration

### No host integration documentation

SDK is for building servers/clients, not a runnable server. Multiplatform targets (JS, Wasm) enable browser-based clients with Ktor CORS support; specific host integrations are the consuming application's responsibility.

### Production reference implementation

Sample implementations under `./samples/` cover various transport configurations.

## Repository layout

### Gradle multi-module / Maven multi-artifact monorepo

Gradle multi-module project: `kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, `kotlin-sdk` (umbrella); supporting directories: `samples/`, `docs/`, `config/`, `integration-test/`, `conformance-test/`, `.github/`, `buildSrc/`. Modular artifact structure allows client/server-only dependencies.

## Documentation surface

### README plus docs directory

`docs/` directory present alongside README; Knit-based code-snippet testing in documentation.

## Developer ergonomics

### Sample implementations directory

`samples/` directory with end-to-end mini-apps covering various transports/configurations.

## Release and lifecycle

### Dual-license relicensing gate

Apache-2.0 license for new contributions; MIT for existing code. The release process enforces the contributor agreement — a forward migration mechanism without rewriting prior commits.

### Active development

v0.11.1 released April 10, 2026; ongoing.

### Tagged release with version in changelog

Standard semver tags; v0.11.1.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

This is an SDK for building servers/clients, not a server itself.
