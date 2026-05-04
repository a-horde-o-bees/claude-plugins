# Sample

Mirrors of `https://github.com/bhauman/clojure-mcp`. Clojure REPL MCP server — 50+ tools via nREPL for structure-aware editing, code evaluation, and multi-REPL support (Shadow-cljs/Babashka/Basilisp/Scittle). 735 stars; EPL-2.0 (Eclipse Public License v 2.0); default branch `main`; last release v0.3.1 dated March 14, 2026.

## Server runtime

### Clojure with nREPL bridge

Clojure (99.9% of repo) on the JVM (JDK 17 or later inferred). MCP protocol bridged onto an nREPL connection — tool invocations become forms evaluated in the running REPL. Multi-environment detection switches between Clojure, ClojureScript via Shadow-cljs, Babashka, Basilisp, and Scittle.

## Transport

### nREPL connection

JSON-RPC over an nREPL connection. The MCP server is itself driven through the REPL protocol; tool calls are forms evaluated by the connected REPL.

### Selection mechanism

Profile-driven launcher — entry-point selection at launch chooses between CLI assistants, Claude Desktop, and other MCP clients with environment-specific configuration.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

50+ tools targeting Clojure ecosystem needs across categories: read-only file operations, code evaluation, structure-aware editing, shell execution, agent-based analysis. REPL-driven evaluation; Clojure syntax/formatting aware. Agent-augmented tools layered over base REPL operations call out to external LLMs (Anthropic, OpenAI, Google Gemini) when configured.

## Configuration delivery

### Sidecar config files (JSON / YAML / TOML / EDN)

Project-level `.clojure-mcp/config.edn` with a Clojure-map structure carries tool filtering, profile selection, nREPL parameters, and formatting preferences (cljfmt toggle).

### CLI flags

Command-line overrides for tool filtering, profile selection, and nREPL parameters.

### Environment variables

Optional environment variables for external LLM provider API keys (Anthropic, OpenAI, Google Gemini) used by agent tools.

## Authentication

### None / implicit (local-resource gating)

No built-in authentication on the MCP layer — local stdio/REPL-resident execution.

### Optional external LLM API keys

Optional API keys for external LLM providers (Anthropic, OpenAI, Google Gemini) supplied via env vars when present; agent-augmented tools use them when configured.

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per project/REPL instance; workspace-specific via project configuration.

## Distribution channel

### Language-native installer

`clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp` — Clojure tools installer via Maven-style coords (`io.github.bhauman/clojure-mcp`). Source build also documented.

## Entry point and launch

### Language-tool launcher

`clojure -Tmcp start` post-install. Profile variants: `clojure-mcp-light` for lightweight REPL; `:cli-assist` profile for full assistant; Claude Desktop launches via shell path and command arguments.

### Profile-driven launcher

Clojure `deps.edn` aliases / profiles (`:stdio-server`, `:sse-server`-style mechanism) select transport / mode at launch.

## Build and packaging

### Maven / Gradle (JVM)

Maven-style coords (`io.github.bhauman/clojure-mcp`); JVM runtime; `deps.edn` for dependency management. JDK 17+ inferred.

## Test stack

### Clojure-native testing

Test directory present; typical Clojure testing patterns; project structure suggests comprehensive testing.

## CI

### GitHub Actions

GitHub Actions configured in `.github/`; typical Clojure project CI.

## Container artifacts

### No container artifacts

Not documented in provided content.

## Observability

### Change-notification channels / JSON-RPC notifications

JSON-RPC notifications signal tool/resource availability changes; server logs nREPL connection details and tool initialization status during startup; notification-based change detection used to refresh client-side capability views.

## Deployment topology

### REPL-resident

Server code runs inside a long-lived REPL process; the host connects to the REPL. Native Clojure-ecosystem deployment shape.

## Repository layout

### Clojure project layout

Standard Clojure layout: `src/`, `test/`, `doc/`, `resources/`, `deps.edn`, `docs/`. Extensive root-level documentation: README, PROJECT_SUMMARY, CHANGELOG, CONFIG, FAQ, BIG_IDEAS, LLM_CODE_STYLE. `.github/` and `.claude/` directories present.

## Safety and security posture

### None / not surfaced

Sandbox-example file (`clj-sandbox-example.sb`) demonstrates safe code-evaluation patterns but no enforced sandbox documented at the server layer.

## Domain logic and embedded intelligence

### In-server LLM client

Optional external LLM integration for agent tools — server can call out to Anthropic, OpenAI, or Google Gemini when configured, layering LLM-shaped post-processing on REPL operations.

## Host integration

### Claude Desktop

Configured in `claude_desktop_config.json` with shell path and command arguments.

### nREPL host

Primary integration mechanism — server runs as a connected REPL participant.

## Documentation surface

### README plus docs directory

README.md (30KB), PROJECT_SUMMARY.md (26KB), CONFIG.md (9KB), FAQ.md (8KB), BIG_IDEAS, CHANGELOG, LLM_CODE_STYLE — substantial supplementary documentation.

### Bundled `cursor_rules.md` / AI-guidance content

`LLM_CODE_STYLE.md` shipped with the repo for AI assistant guidance — a markdown file conveying conventions the LLM should follow when using the server (rules/guidance the host's LLM is expected to read; not an MCP tool or prompt).

### Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)

`.claude/` directory present at repo root — Claude is part of the contributor experience for the repo.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Server-only implementation — no Claude Code plugin/skill wrapper present.

## Release and lifecycle

### License — Weak copyleft (EPL-2.0)

EPL-2.0 (Eclipse Public License v 2.0) — weak copyleft, requires share-alike for derivatives. Commercial use permitted. The canonical license for Clojure-world projects.

### Tagged release with version in changelog

v0.3.1 release dated 2026-03-14; CHANGELOG present.

### Active development

Active maintenance with semver-tagged releases.
