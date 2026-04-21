# ppl-ai/modelcontextprotocol

## Identification
- url: https://github.com/ppl-ai/modelcontextprotocol
- stars: 2.1k
- last-commit (date or relative): Not explicitly extracted; 133 total commits
- license: MIT
- default branch: main
- one-line purpose: Perplexity MCP server (official, org slug differs from brand) — search-augmented answering.
Note: The user brief referenced `perplexityai/modelcontextprotocol`. The resolved canonical repo is `ppl-ai/modelcontextprotocol` (Perplexity AI's GitHub org uses the `ppl-ai` slug).

## 1. Language and runtime
- language(s) + version constraints: TypeScript (95.2%); Node.js runtime
- framework/SDK in use: Model Context Protocol TypeScript SDK
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default); HTTP server deployment also supported
- how selected (flag, env, separate entry, auto-detect, etc.): HTTP mode uses `PORT` and `BIND_ADDRESS` env vars plus CORS support; otherwise stdio
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: npm package with quick-install badges; Dockerfile included for containerized deployment
- published package name(s): @perplexity-ai/mcp-server
- install commands shown in README: `npx -y @perplexity-ai/mcp-server`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `npx -y @perplexity-ai/mcp-server`
- wrapper scripts, launchers, stubs: npm bin entry; quick-install badges for Cursor, VS Code, Claude Desktop, Kiro, Windsurf
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Environment variables dominate — `PERPLEXITY_API_KEY` (required), `PERPLEXITY_TIMEOUT_MS` (default 300000ms), `PERPLEXITY_BASE_URL`, `PORT`, `BIND_ADDRESS`, proxy configuration
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Static API key via `PERPLEXITY_API_KEY` env var
- where credentials come from: User obtains key from Perplexity API Portal
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user — API key is process-scoped; per-request tenancy is Perplexity-account-level
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Four tools —
  - `perplexity_search` — web search via Search API
  - `perplexity_ask` — conversational AI with sonar-pro model
  - `perplexity_research` — deep research via sonar-deep-research
  - `perplexity_reason` — advanced reasoning via sonar-reasoning-pro
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Log level controlled via `PERPLEXITY_LOG_LEVEL` env var; destination not explicitly extracted
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Cursor
- VS Code
- Claude Desktop
- Kiro
- Windsurf
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: Not explicitly observed within extracted content
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: vitest configured; specific layout not extracted
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions workflows present; specific jobs not extracted
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile included
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Per-host quick-install badges in README; HTTP mode with CORS for shared deployments
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package TypeScript project; source in `/src`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Optional `strip_thinking` parameter removes reasoning tags from Perplexity output — token-saving feature that gives caller control over output verbosity
- Proxy configuration layering — `PERPLEXITY_PROXY` takes priority over standard `HTTPS_PROXY`/`HTTP_PROXY`, so the Perplexity-specific proxy overrides system-wide settings
- Four-tool surface aligns with Perplexity's product tiers (search, ask, research, reason) — tool boundaries mirror Perplexity model variants rather than low-level API endpoints
- HTTP mode plus CORS enables shared-server deployments where multiple clients hit one process

## 18. Unanticipated axes observed
- First-party vendor MCP where the tool surface maps 1:1 to product/model offerings — a cleaner pattern than low-level REST wrapping
- Proxy hierarchy recognizes corporate/enterprise environments where a specific proxy needs to override system defaults

## 20. Gaps
- Last commit date and release cadence not confirmed
- Whether HTTP mode supports authentication beyond env-var key (e.g., per-request API keys) not extracted
- Exact tool argument schemas not extracted within budget
