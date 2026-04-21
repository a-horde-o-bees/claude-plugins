# rust-mcp-stack/rust-mcp-filesystem

## Identification
- url: https://github.com/rust-mcp-stack/rust-mcp-filesystem
- stars: 144
- last-commit (date or relative): March 15, 2026 (v0.4.1 release)
- license: MIT
- default branch: main
- one-line purpose: Rust filesystem MCP server — high-performance FS operations; distributed via Homebrew, Cargo, npm, and Docker.

## 1. Language and runtime
- language(s) + version constraints: Rust (version specified in rust-toolchain.toml)
- framework/SDK in use: rust-mcp-sdk, rust-mcp-schema libraries
- pitfalls observed:
  - Specific Rust version constraints (rust-toolchain.toml exists but content not fetched)

## 2. Transport
- supported transports: Not explicitly documented in provided content; inferred to be stdio-based (standard for MCP filesystem servers)
- how selected (flag, env, separate entry, auto-detect, etc.): Not explicitly documented; likely auto-detect or default
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: Shell script installer, PowerShell installer, Homebrew, Cargo, NPM package (@rustmcp/rust-mcp-filesystem), Docker Hub MCP Registry, GitHub release binary downloads, source build
- published package name(s): rust-mcp-filesystem (Cargo crate), @rustmcp/rust-mcp-filesystem (npm), Docker image at hub.docker.com/mcp/server/rust-mcp-filesystem
- install commands shown in README: Shell script installer (Unix), PowerShell installer (Windows), Homebrew, `cargo install`, npm install, Docker pull
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: Standalone binary execution (no version specified in provided content; inferred from architecture)
- wrapper scripts, launchers, stubs: Shell and PowerShell installer scripts
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Read-only by default with optional write access configuration; MCP Roots support (disabled by default); tool disabling capability to reduce functionality and token usage
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Not applicable; filesystem access controlled by read-only restriction and tool disabling
- where credentials come from: Not applicable
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Not applicable; single-user filesystem server
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Glob pattern file searching (e.g., `*.rs`, `src/**/*.txt`), ZIP archive creation and extraction, filesystem operations management, MCP Roots functionality
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not documented in provided content
- pitfalls observed:
  - Logging/observability details not documented

## 10. Host integrations shown in README or repo
- Claude Desktop: Standard MCP configuration (assumed, not explicitly detailed in provided content)
- Claude Code: Not documented
- Other: Not documented
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: Not present; this is a standalone server, not a plugin
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Test framework present; testing configured via `cargo-nextest`; located in `tests/` directory
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions; Makefile.toml defines: `fmt` (rustfmt), `clippy` (linting), `test` (cargo-nextest), `check` (composite), `clippy-fix` (auto-correction)
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile present; multi-stage build using `clux/muslrust:stable` builder and `alpine:latest` final image; static binary with non-root user (`rust-mcp-user`); available on Docker Hub MCP Registry
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Glob pattern examples: `*.rs`, `src/**/*.txt`, `logs/error-???.log`; Makefile.toml targets for build, test, lint
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Single-package server; structure: `/src/` (source), `/tests/` (tests), `/docs/` (documentation), `/wix/` (Windows installer), `Dockerfile`, `Makefile.toml`, `Cargo.toml/Cargo.lock`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Rewrite of JavaScript `@modelcontextprotocol/server-filesystem` in Rust for performance
- Multi-stage Docker build for minimal image size (alpine final image, non-root user)
- CLI tool disabling to reduce token usage for specific workflows
- MCP Roots support with opt-in (disabled by default)
- Read-only by default security model

## 18. Unanticipated axes observed
- Standalone binary with zero external runtime dependencies (no Node.js, Python, or system libs beyond alpine base)
- Windows installer via WiX toolset shows commitment to cross-platform distribution
- CLI tool disabling (not just feature flags) suggests token-aware deployments

## 20. Gaps
- Transports not explicitly documented (inferred as stdio-only)
- Specific Rust version constraints (rust-toolchain.toml exists but content not fetched)
- Logging/observability details not documented
- Specific invocation command examples not provided (assumed standard MCP launch)
