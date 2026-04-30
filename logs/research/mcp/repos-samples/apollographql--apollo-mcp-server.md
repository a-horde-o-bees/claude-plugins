# Sample

## Identification

### url

https://github.com/apollographql/apollo-mcp-server

### stars

277

### last-commit

v1.12.0 released 2026-04-02; 63 total releases.

### license

MIT

### default branch

main

### one-line purpose

Apollo GraphQL MCP server (Rust) — generates MCP tools from configured GraphQL operation definitions; tool catalog is declarative config, not code.

## Language and runtime

### language(s) + version constraints

Rust (98.7%). Cargo-managed; `Cargo.toml` present.

### framework/SDK in use

Rust MCP implementation; Apollo GraphQL ecosystem.

## Transport

### supported transports

Not explicitly extracted in fetched view; README points to external docs for config reference. Standard MCP transport(s) expected (stdio and streamable-HTTP typical for this class).

### how selected

Via configuration file referenced as "config file reference" on Apollo docs.

## Distribution

### every mechanism observed

Source build (`cargo build`); binary releases on GitHub; Docker container; Cargo package.

### published package name(s)

Cargo crate (name aligned with repo); Docker image (per GitHub release-container workflow).

### install commands shown in README

Not directly enumerated in the fetched view (README redirects to user guide for full usage).

## Entry point / launch

### command(s) users/hosts run

Server binary pointed at a GraphQL endpoint + operation definitions + config file.

### wrapper scripts, launchers, stubs

Not extracted.

## Configuration surface

### how config reaches the server

Config file is the documented primary mechanism, pointing at (1) a GraphQL endpoint to expose, (2) operation definitions for MCP tools, (3) a configuration file itself. Format not extracted (likely YAML or TOML given Apollo/Rust conventions).

## Authentication

### flow

Not extracted; likely per-GraphQL-endpoint auth via headers configured in the config file. Apollo Router conventions apply.

### where credentials come from

Not extracted.

## Multi-tenancy

### tenancy model

Not extracted.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools generated from GraphQL operation definitions — each configured operation becomes an MCP tool. Unusual capability source: tool surface is defined by the operator's GraphQL operations, not baked into the server.

## Observability

### logging destination + format, metrics, tracing, debug flags

Not extracted.

## Host integrations shown in README or repo

### Claude

`.claude` directory and `CLAUDE.md` file present in repo — in-repo Claude surface.

### MCP Inspector

Compatibility noted.

### generic AI client

README targets generic "AI model/LLM client".

## Claude Code plugin wrapper

### presence and shape

`.claude` directory + `CLAUDE.md` at repo root — operational Claude docs. `.claude-plugin/` presence not explicitly confirmed; the `.claude` directory may be Claude Code's workspace config rather than a plugin wrapper.

## Tests

### presence, framework, location, notable patterns

End-to-end testing directory (`/e2e/mcp-server-tester`). Codecov integration.

## CI

### presence, system, triggers, what it runs

GitHub Actions — CI workflow, release-binaries workflow, release-container workflow.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Docker container built via release-container workflow.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`/examples` directory contains configuration examples. MCP Inspector compatibility called out.

## Repo layout

### single-package / monorepo / vendored / other

Single Rust crate with `/examples`, `/e2e/mcp-server-tester`, `Cargo.toml`, `.claude` directory, `CLAUDE.md`.

## Notable structural choices

Operation-driven tool surface: MCP tools are derived from GraphQL operation definitions supplied at config time, not hardcoded. The server is a generic adapter over any Apollo/GraphQL endpoint — operators shape the tool catalog by choosing which operations to expose.

Rust implementation in a space dominated by TS/Python/Go — aligns with Apollo Router's Rust-forward stance and gives the server Router-adjacent performance characteristics.

Dedicated `mcp-server-tester` e2e harness — suggests protocol-conformance testing is an explicit concern.

`.claude/` + `CLAUDE.md` in-repo — indicates Claude-assisted development is an authoring surface for contributors.

## Unanticipated axes observed

GraphQL-as-schema-source-of-truth for MCP tools: tool definitions live as GraphQL operations, not as MCP tool declarations. Reduces tool authoring to operation authoring — a rare capability-sourcing pattern.

Protocol-conformance e2e tester as a first-class component (`mcp-server-tester` subdirectory).

Rust for MCP servers — adds a distribution channel (crates.io, binaries, Docker) different from the TS/Python/Go norm.

## Gaps

Specific transport(s) supported (stdio vs streamable-HTTP) — README redirects to external docs. Config file format (YAML? TOML?). Authentication approach at the MCP layer vs upstream GraphQL. Actual install command shown to users. Whether `.claude-plugin/plugin.json` exists or whether `.claude/` is just Claude Code workspace state. `Cargo.toml` contents — dependencies and minimum Rust version.
