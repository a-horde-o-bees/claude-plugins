# Sample

## Identification

### url

https://github.com/modelcontextprotocol/kotlin-sdk

### stars

1,300

### last-commit

April 10, 2026 (v0.11.1 release)

### license

Apache 2.0 (new contributions) / MIT (existing code)

### default branch

main

### one-line purpose

Official MCP Kotlin SDK — multiplatform (JVM, Native, JS, Wasm).

## Language and runtime

### language(s) + version constraints

Kotlin 2.2+, Java 11+ (JVM target); multiplatform: JVM, Native, JS, Wasm.

### framework/SDK in use

Anthropic's Model Context Protocol (MCP) specification; Kotlin coroutines; Ktor server (optional).

## Transport

### supported transports

Stdio, Streamable HTTP (single endpoint with optional JSON-only or SSE), Server-Sent Events (SSE), WebSocket, ChannelTransport (local testing).

### how selected

Configured at server initialization; embedded Ktor server for HTTP deployments; separate transport implementations.

## Distribution

### every mechanism observed

Maven Central (Gradle/Maven), source build.

### published package name(s)

`io.modelcontextprotocol:kotlin-sdk` (full), `io.modelcontextprotocol:kotlin-sdk-client` (client), `io.modelcontextprotocol:kotlin-sdk-server` (server).

### install commands shown in README

`implementation("io.modelcontextprotocol:kotlin-sdk:x.x.x")` or granular client/server artifacts.

## Entry point / launch

### command(s) users/hosts run

Ktor server integration for HTTP deployments; STDIO transport for CLI tools; application-specific initialization.

### wrapper scripts, launchers, stubs

Sample implementations in `./samples/` directory.

## Configuration surface

### how config reaches the server

CORS configuration for browser clients; configurable endpoint paths (default `/mcp`); transport-specific options.

## Authentication

### flow

Not explicitly documented; delegated to transport/application layer.

### where credentials come from

Not applicable; SDK provides infrastructure, not auth.

## Multi-tenancy

### tenancy model

Not applicable; SDK provides transport and protocol abstraction, multi-tenancy handled by application.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Server: Prompts, Resources, Tools, Completion, Logging, experimental features. Client: Sampling (LLM requests), Roots (filesystem declaration), Elicitation.

## Observability

### logging destination + format, metrics, tracing, debug flags

No explicit observability documented in provided content; Kotlin/Ktor standard logging available.

## Host integrations shown in README or repo

### Claude Desktop

Inferred support via MCP standard; not explicitly detailed.

### Claude Code

Not documented.

### Other

Ktor CORS support enables browser-based clients.

## Claude Code plugin wrapper

### presence and shape

Not present; this is an SDK for building servers/clients, not a server itself.

## Tests

### presence, framework, location, notable patterns

Comprehensive testing infrastructure: `kotlin-sdk-testing` module, integration tests, conformance tests, test utilities in `test-utils/`; Knit properties for code snippet testing.

## CI

### presence, system, triggers, what it runs

GitHub Actions configured; typical Gradle/Kotlin project structure.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not documented; depends on application using the SDK.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Sample implementations in `./samples/` directory covering various transport configurations; Gradle build system for automation.

## Repo layout

### single-package / monorepo / vendored / other

Monorepo structure with Gradle multi-module project: `kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, `kotlin-sdk` (umbrella); supporting directories: `samples/`, `docs/`, `config/`, `integration-test/`, `conformance-test/`, `.github/`, `buildSrc/`.

## Notable structural choices

Official Kotlin SDK maintained with JetBrains collaboration. Multiplatform support (JVM, Native, JS, Wasm) enables diverse deployment scenarios. Modular artifact structure allows client/server-only dependencies. Coroutine-friendly APIs throughout (Kotlin idiom). No transitive Ktor dependencies; developers specify engines independently. Conformance testing ensures spec compliance. Keep-human-in-loop guidance for sensitive operations.

## Unanticipated axes observed

Multiplatform Kotlin (Native, JS, Wasm) enables MCP implementations outside JVM. ChannelTransport for local testing without networking. Pagination support for list operations suggests handling of large result sets. Explicit CORS configuration for browser-based clients (unusual for MCP).

## Gaps

Specific Ktor version constraints not documented. Observability/logging patterns not detailed. Full Docker/containerization guidance not provided. Complete transport selection pattern not documented.
