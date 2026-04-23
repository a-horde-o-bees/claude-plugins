# teaguesterling/duckdb_mcp

## Identification
- url: https://github.com/teaguesterling/duckdb_mcp
- stars: 47
- last-commit (date or relative): v2.1.0 released March 28, 2026
- license: MIT
- default branch: main
- one-line purpose: DuckDB-embedded MCP server — implemented as a DuckDB extension invoked from SQL, rather than a standalone process.

## 1. Language and runtime
- language(s) + version constraints: C++ (73.7%), Shell (13.1%), Python (10.6%), small TS/JS/HTML. Built as a DuckDB extension — runtime is DuckDB itself
- framework/SDK in use: Custom implementation of MCP as a native DuckDB extension; CMake build
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio, HTTP (server mode with token auth), MCP client (connects to external MCP servers via SQL `ATTACH`)
- how selected (flag, env, separate entry, auto-detect, etc.): `PRAGMA mcp_server_start(...)` selects server mode and transport parameters from SQL
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: Build from source with `make`; CMake-driven; no package-registry distribution observed (extension not yet in DuckDB community extensions per content fetched)
- published package name(s): None observed
- install commands shown in README: `make` (build from source)
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: Users issue SQL `PRAGMA mcp_server_start()`, `PRAGMA mcp_publish_tool(...)`, and `SELECT` functions inside DuckDB. HTTP endpoints `/health` and `/mcp` surface remote access.
- wrapper scripts, launchers, stubs: Example configs under `/examples`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: SQL PRAGMA calls with parameters (name, description, SQL template, properties, required fields, output format). JSON config file for HTTP/token settings.
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Bearer-token authentication in HTTP server mode
- where credentials come from: JSON configuration file
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-instance server keyed to the DuckDB database; no per-request tenant handling documented
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Built-in tools for query execution, table/schema description, listing, database introspection, export, DDL. Custom parameterized SQL queries publishable as tools via `mcp_publish_tool`. Output format per-tool (JSON/Markdown/CSV).
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not detailed in README within budget; HTTP `/health` endpoint provides liveness
- pitfalls observed:
  - Observability/logging specifics not surfaced

## 10. Host integrations shown in README or repo
- Claude Desktop: Configuration via `.mcp.json` in project root
- Other editors/CLIs: Not explicitly enumerated
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: Not present
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Tests under `/test`; `make test` command
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions workflows present in `.github/workflows`; specifics not extracted within budget
- pitfalls observed:
  - CI workflow details not extracted

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: None observed
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `make test` target; 6+ ready-to-use configs under `/examples`; ReadTheDocs documentation
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package DuckDB extension — `src/`, `examples/`, `test/`, CMake-based, with separate security audit docs
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Native DuckDB extension rather than a standalone process — MCP surface is reachable via SQL PRAGMAs
- Dual-mode: server for AI assistants AND client connecting to other MCP resources via `ATTACH`
- Per-tool output format is an explicit token-efficiency knob
- `PRAGMA mcp_publish_tool` makes SQL templates first-class discoverable tools

## 18. Unanticipated axes observed
- MCP-as-SQL-extension blurs database and tool-registry roles — unusual architecture
- `ATTACH`-style client semantics lets SQL queries span multiple MCP-exposed data sources

## 20. Gaps
- Observability/logging specifics not surfaced
- CI workflow details not extracted
- No container or binary distribution observed — source-only build
