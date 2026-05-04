# Sample

Mirrors of `https://github.com/apollographql/apollo-mcp-server`. Apollo GraphQL MCP server (Rust) — generates MCP tools from configured GraphQL operation definitions; tool catalog is declarative config, not code. 277 stars, MIT, default branch `main`, v1.12.0 released 2026-04-02 (63 total releases), vendor-authored (Apollo).

## Server runtime

### Rust with rmcp / rust-mcp-sdk

Rust crate (98.7% Rust). Cargo-managed via `Cargo.toml`. Apollo-aligned — Rust-forward implementation in a space dominated by TS/Python/Go. Aligns with Apollo Router's stance and gives the server Router-adjacent performance characteristics. Specific MCP SDK choice (rmcp vs rust-mcp-sdk vs other) and `Cargo.toml` dependencies not extracted within budget.

## Transport

### Selection mechanism

Configuration file (referenced as "config file reference" on Apollo docs) selects transport. Specific transports (stdio vs streamable-HTTP) not enumerated in fetched README view; standard MCP transports expected for this class.

## Capability surface

### Spec-driven dynamic tool generation

Tools derived from configured GraphQL operation definitions — each configured operation becomes an MCP tool. Tool surface is defined by the operator's GraphQL operations (not hardcoded), making the server a generic adapter over any Apollo/GraphQL endpoint. Operators shape the tool catalog by choosing which operations to expose without touching server code.

## Configuration delivery

### Sidecar config files (JSON / YAML / TOML / EDN)

Config file is the documented primary configuration mechanism, pointing at (1) a GraphQL endpoint to expose, (2) operation definitions for MCP tools, (3) the configuration file itself. Format not extracted (likely YAML or TOML given Apollo/Rust conventions).

## Distribution channel

### Cargo crate / cargo install

Cargo crate (name aligned with repo); source build via `cargo build`.

### Pre-built binary release

Binary releases on GitHub via release-binaries workflow.

### Docker / OCI image

Docker container built via release-container workflow.

## Build and packaging

### Cargo (Rust)

Standard Rust build via `Cargo.toml`.

## Container artifacts

### Published Docker image

Docker image built and published via the release-container workflow.

## Test stack

### End-to-end protocol-conformance harness

Dedicated `/e2e/mcp-server-tester` subdirectory exercises the MCP protocol surface end-to-end. Protocol-conformance testing is an explicit concern.

## CI

### GitHub Actions

GitHub Actions — separate workflows for CI, release-binaries, and release-container.

### Codecov integration

Codecov reporting wired into CI.

### Release-cut workflow on tag push

Dedicated release-binaries and release-container workflows triggered for releases.

## Host integration

### Claude Code

`.claude` directory and `CLAUDE.md` file present in repo. The `.claude` directory may be Claude Code's workspace config rather than a plugin wrapper; `.claude-plugin/` presence not explicitly confirmed.

### Inspector compatibility called out

MCP Inspector compatibility noted.

### Generic / host-agnostic snippet

README targets a generic "AI model/LLM client" without enumerating specific hosts.

## Repository layout

### Single Rust crate

Single Rust crate with `/examples`, `/e2e/mcp-server-tester`, `Cargo.toml`, `.claude` directory, `CLAUDE.md` at repo root.

## Documentation surface

### Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)

`.claude/` + `CLAUDE.md` in repo — Claude-assisted development is an authoring surface for contributors.

### README + examples/

`/examples` directory contains configuration examples.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

v1.12.0 released 2026-04-02 with 63 total releases.
