# Sample

## Identification

### url

https://github.com/hugoduncan/mcp-clj

### stars

58

### last-commit

November 5, 2025 (v0.1.66 release)

### license

EPL-2.0 (Eclipse Public License 2.0)

### default branch

master

### one-line purpose

Clojure MCP SDK — framework for building MCP servers in Clojure.

## Language and runtime

### language(s) + version constraints

Clojure (99.7%); Java runtime required.

### framework/SDK in use

Anthropic's Model Context Protocol (MCP) version 2024-11-05; Clojure standard library.

### pitfalls observed

Specific Java version constraints not mentioned.

## Transport

### supported transports

Stdio (recommended for Claude Desktop), SSE/HTTP (default port 3001, customizable), In-memory (testing).

### how selected

Selected at launch via CLI profile: `:stdio-server`, `:sse-server`; custom port via `--port` flag.

## Distribution

### every mechanism observed

Git dependency, direct CLI usage, source build.

### published package name(s)

Not on Clojars; Git-based dependency only.

### install commands shown in README

Via Git dependency in `deps.edn` or direct invocation: `clj -M:stdio-server`, `clj -M:sse-server`.

## Entry point / launch

### command(s) users/hosts run

`clj -M:stdio-server` (stdio transport), `clj -M:sse-server` (HTTP-based), `clj -M:sse-server --port 8080` (custom port).

### wrapper scripts, launchers, stubs

None documented.

## Configuration surface

### how config reaches the server

Claude Desktop integration via `claude_desktop_config.json`; bash interpreter, project path, and environment variables specified in config.

## Authentication

### flow

No explicit authentication mechanism documented.

### where credentials come from

Not applicable; assumes transport-layer security.

## Multi-tenancy

### tenancy model

Single-user; not applicable.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Built-in tools: `clj-eval` (evaluate Clojure expressions), `ls` (list files with gitignore support, including depth/limit options); custom tools can be added dynamically via API.

## Observability

### logging destination + format, metrics, tracing, debug flags

No explicit observability documented in provided content.

## Host integrations shown in README or repo

### Claude Desktop

Yes; sample `claude_desktop_config.json` configuration provided.

### Claude Code

Not explicitly documented.

### Other

Not documented.

## Claude Code plugin wrapper

### presence and shape

Not present; server-only implementation.

## Tests

### presence, framework, location, notable patterns

Test configuration via `tests.edn`; testing investigation notes present; clj-kondo linting configuration for code quality.

## CI

### presence, system, triggers, what it runs

GitHub Actions likely configured; cliff.toml for release notes generation.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not documented.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

README includes representative usage patterns: server creation, custom tool implementation, client connection, JSON-based tool invocation; Claude Desktop configuration example.

## Repo layout

### single-package / monorepo / vendored / other

Polylith-style component architecture: `bases/`, `components/`, `projects/`, with supporting: `design/`, `dev/`, `development/`, `doc/`, `spec/`, `scripts/`; configuration: `deps.edn`, `tests.edn`, `cliff.toml`, `.cljstyle`; tooling: `.clj-kondo/`, `.github/`, `.claude/`, `.mcp-vector-search/`.

## Notable structural choices

Minimal dependencies — only `org.clojure/data.json`. Self-contained Clojure REPL evaluation without external dependencies. Polylith-style modular architecture (bases, components, projects). Three transport modes (stdio, SSE/HTTP, in-memory). Custom tool dynamic registration via API. Vector search integration (`.mcp-vector-search/` directory).

## Unanticipated axes observed

Extremely minimal dependencies (only data.json) for a full MCP implementation. Vector search integration suggests semantic/similarity search capabilities. Polylith architecture (bases/components/projects) is advanced modular organization. Two-tool minimal interface (clj-eval, ls) vs. 50+ tools in clojure-mcp. In-memory transport for testing (unusual).

## Gaps

Specific Clojure version constraints not documented. Vector search implementation details not explained (`.mcp-vector-search/`). Custom tool registration API not fully documented. Test framework and patterns not examined (tests.edn exists but not detailed). Specific Java version constraints not mentioned. Port 3001 default not explained in provided content.
