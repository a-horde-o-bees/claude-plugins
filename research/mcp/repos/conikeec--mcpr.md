# conikeec/mcpr

## Identification
- url: https://github.com/conikeec/mcpr
- stars: 350
- last-commit (date or relative): Recent on master branch (specific date not in fetch content); repository status: Archived as of February 8, 2026
- license: MIT
- default branch: master
- one-line purpose: Rust MCP implementation library (archived Feb 2026) — server/client scaffolding, CLI stub generation, mock transport for testing.

## 1. Language and runtime
- language(s) + version constraints: Rust (no explicit MSRV specified)
- framework/SDK in use: Anthropic's Model Context Protocol (MCP) specification
- pitfalls observed:
  - Specific Rust version constraints not documented (could be found in Cargo.toml)

## 2. Transport
- supported transports: Stdio, SSE (Server-Sent Events); WebSocket planned but not yet implemented
- how selected (flag, env, separate entry, auto-detect, etc.): Selected via project generator at creation time: `mcpr generate-project --transport [stdio|sse]`
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: Cargo crate registry, Cargo binary installer
- published package name(s): mcpr (crate)
- install commands shown in README: `cargo add mcpr = "0.2.3"` (library); `cargo install mcpr` (CLI tools)
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: Generated executables in `target/debug/` for both client and server; launch via compiled binaries after `cargo build`
- wrapper scripts, launchers, stubs: Project scaffolding via `mcpr generate-project --name [name]`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: ServerConfig builder pattern with methods like `.with_name()`, `.with_version()`, `.with_tool()`; tool parameter schemas defined as JSON objects with properties and required field arrays
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: No explicit authentication mechanisms documented
- where credentials come from: Not applicable; transport-layer security implied for production SSE deployments
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Not applicable; library provides schema and transport abstractions but not multi-tenancy features
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Tool registration and invocation, server initialization handshake with protocol version negotiation, client-server disconnection handling, interactive and one-shot operational modes
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: No explicit observability features documented
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop: Not documented
- Claude Code: Not documented
- Other: No host-specific integrations
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: Not present
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Mock transport implementations for testing; testing patterns for both stdio and SSE transports documented
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions configured in `.github/` directory
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not documented
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Project scaffolding via `mcpr generate-project`; example demonstrates GitHub repository interactions via complete client-server implementation
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Single Rust library package; structure: `/src/` (core library), `/examples/` (example code); comprehensive documentation: `README.md`, `MCP.md`, `CHANGELOG.md`, `CONTRIBUTING.md`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Project generation command reduces boilerplate for new MCP implementations
- Mock transport for testing enables fast, offline development
- CLI tools included for server/client stub generation

## 18. Unanticipated axes observed
- Two-phase version negotiation in server initialization handshake
- Repository archived as of Feb 2026 but still functional; unclear if superceded by newer Rust MCP implementations

## 20. Gaps
- Repository is archived; no active development
- WebSocket transport not implemented (marked as planned)
- Minimal observability features
- Specific Rust version constraints not documented (could be found in Cargo.toml)
- Critical SSE transport issues in v0.2.0 (yanked); v0.2.3+ recommended but version landscape unclear from available content
