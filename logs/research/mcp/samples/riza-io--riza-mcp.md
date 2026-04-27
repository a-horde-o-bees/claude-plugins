# Sample

## Identification
- url: https://github.com/riza-io/riza-mcp
- stars: 14
- last-commit (date or relative): Not explicitly displayed in provided content; repository appears active
- license: Not specified in provided content (likely MIT or Apache 2.0; default for Riza projects)
- default branch: main
- one-line purpose: Riza code-interpreter MCP server — sandboxed code execution tool.

## 1. Language and runtime
- language(s) + version constraints: JavaScript (72.2%), TypeScript (27.8%); Node.js runtime required
- framework/SDK in use: Anthropic's Model Context Protocol (MCP) specification
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: Not explicitly specified in provided content; inferred as stdio or HTTP based on npm distribution pattern
- how selected (flag, env, separate entry, auto-detect, etc.): Standard MCP transport selection; details not documented
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: NPM package registry, npx command
- published package name(s): @riza-io/riza-mcp (npm package)
- install commands shown in README: `npx @riza-io/riza-mcp` (assumed from npm distribution pattern)
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: Configured through Claude Desktop or adapted for other MCP clients via command-line invocation
- wrapper scripts, launchers, stubs: None documented
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: JSON configuration file (Claude Desktop format); environment variables for API credentials
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: API key authentication via environment variable
- where credentials come from: Riza API key set via `RIZA_API_KEY` environment variable; "Get a free Riza API key in your Riza Dashboard"
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user per API key; multi-user via separate API keys
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Six primary tools: `create_tool` (save code as reusable tools), `fetch_tool` (retrieve saved tools with source code), `execute_tool` (run saved tools securely), `edit_tool` (modify existing tools), `list_tools` (view available tools), `execute_code` (run arbitrary code without saving)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: No observability features documented
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop: Yes; "Configure with Claude Desktop as below, or adapt as necessary for your MCP client"
- Claude Code: Not explicitly documented
- Other: Adaptable for any MCP client
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present; configuration-based integration only

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Not documented in provided content
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: Not documented in provided content
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not documented in provided content
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Claude Desktop JSON configuration example; six documented tools with clear semantics
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Single server package with minimal structure: README.md, `/typescript/` directory containing implementation
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Wraps Riza code interpreter API as MCP tools
- Code execution patterns: `create_tool` (save), `execute_tool` (run saved), `execute_code` (run arbitrary without saving)
- Minimal repository structure suggests newer/actively developed project
- Isolated code execution emphasis (Riza's core value proposition)

## 18. Unanticipated axes observed
- Code interpreter service integration pattern (not data/tool aggregation like other MCP servers)
- Separate patterns for saved vs. arbitrary code execution
- Tool editing capability (edit_tool) unusual for MCP servers

## 20. Gaps
- Transports not explicitly documented
- License not specified in provided content
- Test patterns not documented
- CI/CD configuration not examined
- Last commit date not confirmed
- No information on TypeScript/JavaScript version constraints
