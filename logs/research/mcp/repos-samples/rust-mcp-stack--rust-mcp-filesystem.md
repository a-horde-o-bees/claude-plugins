# Sample

## Identification

### url

https://github.com/rust-mcp-stack/rust-mcp-filesystem

### stars

144

### last-commit

March 15, 2026 (v0.4.1 release).

### license

MIT

### default branch

main

### one-line purpose

Rust filesystem MCP server — high-performance FS operations; distributed via Homebrew, Cargo, npm, and Docker.

## Language and runtime

### language(s) + version constraints

Rust (version specified in rust-toolchain.toml).

### framework/SDK in use

rust-mcp-sdk, rust-mcp-schema libraries.

### pitfalls observed

Specific Rust version constraints (rust-toolchain.toml exists but content not fetched).

## Transport

### supported transports

Not explicitly documented in provided content; inferred to be stdio-based (standard for MCP filesystem servers).

### how selected

Not explicitly documented; likely auto-detect or default.

## Distribution

### every mechanism observed

Shell script installer, PowerShell installer, Homebrew, Cargo, NPM package (`@rustmcp/rust-mcp-filesystem`), Docker Hub MCP Registry, GitHub release binary downloads, source build.

### published package name(s)

`rust-mcp-filesystem` (Cargo crate), `@rustmcp/rust-mcp-filesystem` (npm), Docker image at `hub.docker.com/mcp/server/rust-mcp-filesystem`.

### install commands shown in README

Shell script installer (Unix), PowerShell installer (Windows), Homebrew, `cargo install`, npm install, Docker pull.

## Entry point / launch

### command(s) users/hosts run

Standalone binary execution (no version specified in provided content; inferred from architecture).

### wrapper scripts, launchers, stubs

Shell and PowerShell installer scripts.

## Configuration surface

### how config reaches the server

Read-only by default with optional write access configuration; MCP Roots support (disabled by default); tool disabling capability to reduce functionality and token usage.

## Authentication

### flow

Not applicable; filesystem access controlled by read-only restriction and tool disabling.

### where credentials come from

Not applicable.

## Multi-tenancy

### tenancy model

Not applicable; single-user filesystem server.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Glob pattern file searching (e.g., `*.rs`, `src/**/*.txt`), ZIP archive creation and extraction, filesystem operations management, MCP Roots functionality.

## Observability

### logging destination + format, metrics, tracing, debug flags

Not documented in provided content.

### pitfalls observed

Logging/observability details not documented.

## Host integrations shown in README or repo

### Claude Desktop

Standard MCP configuration (assumed, not explicitly detailed in provided content).

### Claude Code

Not documented.

### Other

Not documented.

## Claude Code plugin wrapper

### presence and shape

Not present; this is a standalone server, not a plugin.

## Tests

### presence, framework, location, notable patterns

Test framework present; testing configured via `cargo-nextest`; located in `tests/` directory.

## CI

### presence, system, triggers, what it runs

GitHub Actions; Makefile.toml defines: `fmt` (rustfmt), `clippy` (linting), `test` (cargo-nextest), `check` (composite), `clippy-fix` (auto-correction).

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; multi-stage build using `clux/muslrust:stable` builder and `alpine:latest` final image; static binary with non-root user (`rust-mcp-user`); available on Docker Hub MCP Registry.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Glob pattern examples: `*.rs`, `src/**/*.txt`, `logs/error-???.log`; Makefile.toml targets for build, test, lint.

## Repo layout

### single-package / monorepo / vendored / other

Single-package server; structure: `/src/` (source), `/tests/` (tests), `/docs/` (documentation), `/wix/` (Windows installer), `Dockerfile`, `Makefile.toml`, `Cargo.toml/Cargo.lock`.

## Notable structural choices

Rewrite of JavaScript `@modelcontextprotocol/server-filesystem` in Rust for performance. Multi-stage Docker build for minimal image size (alpine final image, non-root user). CLI tool disabling to reduce token usage for specific workflows. MCP Roots support with opt-in (disabled by default). Read-only by default security model.

## Unanticipated axes observed

Standalone binary with zero external runtime dependencies (no Node.js, Python, or system libs beyond alpine base). Windows installer via WiX toolset shows commitment to cross-platform distribution. CLI tool disabling (not just feature flags) suggests token-aware deployments.

## Gaps

Transports not explicitly documented (inferred as stdio-only). Specific Rust version constraints (rust-toolchain.toml exists but content not fetched). Logging/observability details not documented. Specific invocation command examples not provided (assumed standard MCP launch).
