# Sample

## Identification
- url: https://github.com/jparkerweb/mcp-sqlite
- stars: 99
- last-commit (date or relative): Not explicitly shown in GitHub UI
- license: MIT
- default branch: main
- one-line purpose: SQLite MCP server — schema exploration and SQL execution.

## 1. Language and runtime
- language(s) + version constraints: TypeScript/JavaScript, Node.js 14.0.0+
- framework/SDK in use: MCP SDK (@modelcontextprotocol/sdk ^1.12.1), sqlite3
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio
- how selected: Default, no transport selection mechanism documented
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: npm package (mcp-sqlite)
- published package name(s): mcp-sqlite
- install commands shown in README: `npx -y mcp-sqlite <database-path>`
- pitfalls observed:
  - Direct npx invocation without intermediate config

## 4. Entry point / launch
- command(s) users/hosts run: `npx -y mcp-sqlite <database-path>`
- wrapper scripts, launchers, stubs: mcp-sqlite-server (CommonJS in package.json bin field)
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Database path as CLI argument, IDE configuration via JSON
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: None specified
- where credentials come from: Not applicable
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user per database instance
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Database introspection, CRUD operations, SQL query execution with parameterized queries
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: MCP Inspector test script via npm test
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Cursor: npx command
- VSCode: npx command
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present in documentation

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Present; MCP Inspector framework; npm test script
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: Not documented
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not observed
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: MCP Inspector integrated as test; postinstall instructions
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single npm package with package.json, README, bin entry
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Minimal dependencies (sqlite3 + MCP SDK only)
- Direct npx invocation without intermediate config
- Parameterized query support for security

## 18. Unanticipated axes observed
- CRUD-first design rather than query-focused like some competitors

## 20. Gaps
- Last commit date not displayed in GitHub UI
- CI/CD system not documented
- HTTP transport alternative not documented
