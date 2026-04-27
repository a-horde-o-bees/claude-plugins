# Sample

## Identification

### url

https://github.com/bhauman/clojure-mcp

### stars

735

### last-commit

March 14, 2026 (v0.3.1 release)

### license

EPL-2.0 (Eclipse Public License v 2.0)

### default branch

main

### one-line purpose

Clojure REPL MCP server — 50+ tools via nREPL for structure-aware editing, code evaluation, and multi-REPL support (Shadow-cljs/Babashka/Basilisp/Scittle).

## 1. Language and runtime

### language(s) + version constraints

Clojure (99.9%); Java runtime (JDK 17 or later inferred).

### framework/SDK in use

Anthropic's Model Context Protocol (MCP); nREPL (REPL protocol).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

JSON-RPC protocol via nREPL connection (REPL-driven); CLI and Claude Desktop variants with different connection patterns.

### how selected

Entry point selection at launch: CLI assistants, Claude Desktop, or other MCP clients with environment-specific configuration.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

Clojure tools installer, source build.

### published package name(s)

io.github.bhauman/clojure-mcp.

### install commands shown in README

`clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp`.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`clojure -Tmcp start` (post-install); CLI profile: `clojure-mcp-light` for lightweight REPL; full with `:cli-assist` profile; Claude Desktop: configured in `claude_desktop_config.json`.

### wrapper scripts, launchers, stubs

None documented.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Project file `.clojure-mcp/config.edn` with Clojure map structure; command-line overrides for tool filtering, profile selection, nREPL parameters; optional environment variables for external LLM providers.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

No built-in authentication; optional API key configuration for external LLM providers (Anthropic, OpenAI, Google Gemini) via environment variables for agent tools.

### where credentials come from

Environment variables for optional external LLM API keys.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

Single-user per project/REPL instance; workspace-specific via project configuration.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

50+ tools across categories: read-only file operations, code evaluation, structure-aware editing, shell execution, agent-based analysis; REPL-driven evaluation; Clojure syntax/formatting aware.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

JSON-RPC notifications signal tool/resource availability changes; server logs nREPL connection details and tool initialization status during startup; notification-based change detection.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

Yes; configured in `claude_desktop_config.json` with shell path and command arguments.

### Claude Code

Not explicitly documented; MCP client wiki referenced.

### nREPL

Primary integration mechanism (REPL-driven).

### Shadow-cljs

Multi-REPL support for ClojureScript.

### Babashka/Basilisp/Scittle

Environment type detection and switching.

### Git/Shell

Bash tool for version control and system operations.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present; server-only implementation.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

Test directory present; typical Clojure testing patterns; project structure suggests comprehensive testing.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions configured in `.github/`; typical Clojure project CI.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not documented in provided content.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Substantial documentation: README.md (30KB), PROJECT_SUMMARY.md (26KB), CONFIG.md (9KB), FAQ.md (8KB); `clj-sandbox-example.sb` example file; clear Claude Desktop integration guide.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single Clojure package; structure: `src/`, `test/`, `doc/`, `resources/`, `deps.edn`, `docs/`; extensive documentation in root: README, PROJECT_SUMMARY, CHANGELOG, CONFIG, FAQ, BIG_IDEAS, LLM_CODE_STYLE; `.github/`, `.claude/` directories.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

REPL-driven development as primary paradigm (nREPL integration). Clojure-aware editing tools (structure-aware, syntax-aware formatting). Multi-REPL support (Shadow-cljs, Babashka, Basilisp, Scittle). 50+ tools targeting Clojure ecosystem needs. Configuration via Clojure maps (deps-like pattern). LLM_CODE_STYLE.md for AI assistant guidance. Sandbox example demonstrating safe code evaluation.

## 18. Unanticipated axes observed

REPL-as-transport pattern (nREPL) is unusual for MCP. Multi-environment detection (Clojure, ClojureScript, Babashka, etc.). Code formatting preferences in configuration (cljfmt toggle). Agent tools with optional external LLM integration (agent-augmented). 50+ tools unusual; suggests comprehensive Clojure ecosystem coverage. LLM_CODE_STYLE documentation for prompt optimization (unusual).

## 20. Gaps

Specific Java version constraints (JDK 17+ inferred but not confirmed). nREPL transport protocol details not fully explained. Docker/containerization not documented. Specific test framework and patterns not examined.
