# Sample

Mirrors of `https://github.com/rust-mcp-stack/rust-mcp-filesystem`. Rust filesystem MCP server — high-performance FS operations including glob search and ZIP archive create/extract; distributed across Homebrew, Cargo, npm, and Docker; rewrite of the JS `@modelcontextprotocol/server-filesystem` for performance. 144 stars, MIT, default branch `main`. Last commit March 15, 2026 (v0.4.1).

## Server runtime

### Rust with rmcp / rust-mcp-sdk

Standalone Rust binary built on `rust-mcp-sdk` and `rust-mcp-schema` libraries. Rust toolchain version pinned via `rust-toolchain.toml` (exact version not extracted). Standalone binary with zero external runtime dependencies — no Node.js, Python, or system libs beyond an alpine base image when containerised.

## Transport

### stdio

Not explicitly documented in extracted README content; inferred to be stdio-based given standard MCP filesystem-server convention and the absence of any HTTP/network configuration. Selection mechanism not surfaced.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Filesystem operations exposed as tools — glob pattern file searching (`*.rs`, `src/**/*.txt`, `logs/error-???.log`), ZIP archive creation and extraction, general filesystem ops management. Read-only by default; CLI tool-disabling capability lets operators reduce the surface to lower token usage for specific workflows.

### MCP Roots participation

MCP Roots functionality available, opt-in (disabled by default).

## Configuration delivery

### CLI flags

Read-only by default; optional write-access configuration at startup; tool-disabling flags to reduce functionality and token usage; MCP Roots flag (off by default).

## Authentication

### None / implicit (local-resource gating)

No auth layer — filesystem access is gated by the read-only restriction and the tool-disabling capability rather than any credential mechanism.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user filesystem server; one local user's filesystem per process.

## Distribution channel

### Cargo crate / cargo install

Published as the `rust-mcp-filesystem` Cargo crate; installable via `cargo install`.

### Homebrew formula

Homebrew formula available for macOS users.

### npm package wrapping native binary

Published as `@rustmcp/rust-mcp-filesystem` — npm package wrapping the native Rust binary so Node-ecosystem hosts can `npx`-install.

### Docker / OCI image

Docker image hosted at `hub.docker.com/mcp/server/rust-mcp-filesystem`.

### Docker Hub MCP Registry

Vendor-namespaced image on the Docker Hub MCP Registry under `mcp/server/...`.

### Pre-built binary release

Binary releases published on GitHub for direct download.

### Multi-channel publication

Published simultaneously across Cargo, Homebrew, npm, Docker Hub, and GitHub releases — broad cross-ecosystem distribution from a single Rust source.

### Windows .exe variant

Windows installer built with the WiX toolset (`wix/` directory in the repo); commits to cross-platform distribution.

## Entry point and launch

### Native binary

Standalone binary execution — exact invocation not extracted from README. Wrapper installer scripts (POSIX shell + PowerShell) fetch the pre-built binary release.

## Build and packaging

### Cargo (Rust)

`Cargo.toml` and `Cargo.lock` present — standard Rust build pipeline. Rust toolchain version pinned via `rust-toolchain.toml`.

## Container artifacts

### Multi-stage Dockerfile

Multi-stage build using `clux/muslrust:stable` as the builder stage and `alpine:latest` as the final image — yields a static binary in a minimal container.

### Hardened-by-default container posture

Final image runs as a non-root user (`rust-mcp-user`).

### Published Docker image

Image is publicly available; users `docker pull` rather than build.

## Test stack

### Cargo test / cargo-nextest (Rust)

Test framework configured via `cargo-nextest`; tests located in `tests/` directory.

### Linter/formatter test gate

Makefile.toml defines `fmt` (rustfmt), `clippy` (linting), `test` (cargo-nextest), `check` (composite), and `clippy-fix` (auto-correction) — lint and format gates run alongside tests.

## CI

### GitHub Actions

GitHub Actions configured.

## Repository layout

### Single Rust crate

Single-crate layout: `/src/` (source), `/tests/` (tests), `/docs/` (documentation), `/wix/` (Windows installer config), `Dockerfile`, `Makefile.toml`, `Cargo.toml`/`Cargo.lock`.

## Safety and security posture

### Read-only by default with explicit write flag

Default posture is read-only; write access is opt-in via configuration. Pairs with tool-disabling capability to further reduce attack surface.

### Hardened-by-default container posture

Multi-stage Docker build produces a static binary running as a non-root user inside an alpine final image — minimises base-image attack surface and avoids root-running container.

## Developer ergonomics

### Makefile / Makefile.toml

`Makefile.toml` orchestrates fmt/clippy/test/check/clippy-fix targets — primary developer workflow entry point.

### PowerShell + batch scripts

PowerShell installer for Windows; POSIX shell installer for Unix — paired platform-native installers.

## Documentation surface

### README plus docs directory

README plus a `/docs/` subdirectory.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT license.

### Active development

v0.4.1 released March 15, 2026; ongoing maintenance.

### Tagged release with version in changelog

Tagged releases on GitHub corresponding to versioned binary releases.
