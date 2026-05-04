# Sample

Mirrors of `https://github.com/hugoduncan/mcp-clj`. Clojure MCP SDK — minimal-deps framework for building MCP servers in Clojure with Polylith-style modular architecture; ships built-in `clj-eval` and `ls` tools. 58 stars, EPL-2.0, default branch `master`, v0.1.66 released November 5, 2025.

## Server runtime

### Clojure with hand-rolled MCP and minimal deps

Clojure (99.7%) targeting MCP version 2024-11-05 with `org.clojure/data.json` as effectively the only dependency. Java runtime required (specific Java version constraints not mentioned). Polylith-style modular layout (bases, components, projects). Self-contained Clojure REPL evaluation surface.

## Transport

### stdio

Recommended for Claude Desktop; selected via `:stdio-server` profile.

### SSE (Server-Sent Events)

SSE/HTTP transport; default port 3001, customizable via `--port` flag. Selected via `:sse-server` profile.

### In-memory / in-process channel

In-memory transport documented for testing — unusual; non-network transport for protocol behavior tests independent of network/IO.

### Selection mechanism

CLI profile at launch — `:stdio-server`, `:sse-server`; custom port via `--port` flag (e.g., `clj -M:sse-server --port 8080`).

## Capability surface

### Tools-only, hand-curated narrow surface

Built-in tools: `clj-eval` (evaluate Clojure expressions), `ls` (list files with gitignore support, including depth/limit options). Two-tool minimal interface — distinct from larger Clojure-MCP wrappers with 50+ tools.

### Runtime tool registration API

Custom tools can be added dynamically via API — extension surface for consumers building atop the SDK.

## Configuration delivery

### Host-side JSON config snippet

Claude Desktop integration via `claude_desktop_config.json`; bash interpreter, project path, and environment variables specified in config.

## Authentication

### None / implicit (local-resource gating)

No explicit authentication mechanism documented — assumes transport-layer security and the host process boundary as the trust boundary.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user; not applicable to a REPL-driven local SDK.

## Distribution channel

### Source clone with editable install

Git dependency in `deps.edn` or direct invocation; not on Clojars — Git-based dependency only.

## Entry point and launch

### Language-tool launcher

`clj -M:stdio-server` (stdio), `clj -M:sse-server` (HTTP-based), `clj -M:sse-server --port 8080` (custom port).

### Profile-driven launcher

Each transport mode is a `deps.edn` profile (`:stdio-server`, `:sse-server`) — caller selects via `clj -M:profile`.

## Repository layout

### Polylith components (Clojure)

Polylith-style component architecture: `bases/`, `components/`, `projects/`, with supporting: `design/`, `dev/`, `development/`, `doc/`, `spec/`, `scripts/`. Configuration: `deps.edn`, `tests.edn`, `cliff.toml`, `.cljstyle`. Tooling: `.clj-kondo/`, `.github/`, `.claude/`, `.mcp-vector-search/`. Advanced modular organization for component reuse across multiple deliverables.

## Test stack

### Clojure-native testing

Test configuration via `tests.edn`; testing investigation notes present; clj-kondo linting configuration for code quality.

## CI

### GitHub Actions

GitHub Actions likely configured (`.github/` present); `cliff.toml` for release notes generation.

## Container artifacts

### No container artifacts

Not documented.

## Host integration

### Claude Desktop

Sample `claude_desktop_config.json` configuration provided.

## Documentation surface

### README as the canonical surface

README includes representative usage patterns: server creation, custom tool implementation, client connection, JSON-based tool invocation; Claude Desktop configuration example.

### Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)

`.claude/` directory present in repo.

## Release and lifecycle

### License — Weak copyleft (EPL-2.0)

EPL-2.0 (Eclipse Public License 2.0). Weak copyleft — source-disclosure obligation attaches only to modified EPL-licensed files. Commercial use permitted. The canonical license for Clojure-world projects.

### Tagged release with version in changelog

v0.1.66 released November 5, 2025; `cliff.toml` for release-notes generation.

### Active development

Recent release cadence.

## Developer ergonomics

### `scripts/` directory

`scripts/` directory holds project scripts.

### Linter and type-checker stack

`clj-kondo` linting configuration; `.cljstyle` for style.
