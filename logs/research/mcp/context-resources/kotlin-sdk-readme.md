# Kotlin SDK README

## Identification
- url: https://github.com/modelcontextprotocol/kotlin-sdk
- type: SDK docs
- author: Model Context Protocol project (maintained in collaboration with JetBrains)
- last-updated: active; v0.11.1 as of research date
- authority level: official

## Scope
Official Kotlin SDK. Kotlin Multiplatform — targets JVM (11+), Native, JS, and Wasm from one codebase. Published to Maven Central under `io.modelcontextprotocol`; `kotlin-sdk` is the combined artifact, `kotlin-sdk-client` / `kotlin-sdk-server` split it. Supports five transports: STDIO, Streamable HTTP, SSE, WebSocket, and `ChannelTransport` (in-process coroutines-channel transport for testing).

## Takeaway summary
Widest transport matrix of any official SDK — notably ships WebSocket (missing from most SDKs) and an in-process `ChannelTransport` that's perfect for unit tests without spawning processes or opening sockets. Example server uses Ktor's CIO engine: declare capabilities, register feature handlers, run. Multiplatform story makes it plausible to compile a single server as a native binary, a JVM service, or a JS module. JetBrains co-maintenance brings IntelliJ / Ktor ecosystem expertise.

## Use for
- How do I run an MCP server on the JVM / as a native binary / in the browser?
- What's the recommended testing transport?
- Which transports does this SDK cover that others don't (WebSocket, Channel)?
- How do I mount in Ktor?

## Relationship to other resources
Kotlin peer of the Python / TS / Go / Rust SDKs. Unique for multiplatform breadth and WebSocket support. JetBrains-maintained and therefore a natural fit for IntelliJ-based workflows.

## Quality notes
Pre-1.0 version numbering (0.11.x) but enterprise-level release cadence and dependency posture. Read the `docs/` directory in the repo for per-module depth.
