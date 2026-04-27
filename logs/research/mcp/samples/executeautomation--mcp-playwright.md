# Sample

## Identification

### url

https://github.com/executeautomation/mcp-playwright

### stars

5.5k

### last-commit (date or relative)

Not explicitly extracted within budget

### license

MIT

### default branch

main

### one-line purpose

Playwright browser-automation MCP server — scripted browser actions for end-to-end testing and scraping.

## 1. Language and runtime

### language(s) + version constraints

TypeScript (93.6%); Node.js runtime (npx/npm-based distribution)

### framework/SDK in use

Model Context Protocol SDK; README describes alignment with Anthropic's Claude Agent SDK conventions. Playwright is the underlying browser-automation engine

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (recommended for Claude Desktop); HTTP/SSE (standalone server mode)

### how selected (flag, env, separate entry, auto-detect, etc.)

Stdio default when launched via `npx`; HTTP enabled by passing `--port <n>` (e.g. `--port 8931`)

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

npm, mcp-get, Smithery CLI, Docker

### published package name(s)

@executeautomation/playwright-mcp-server

### install commands shown in README

- `npm install -g @executeautomation/playwright-mcp-server`
- `npx @michaellatman/mcp-get@latest install @executeautomation/playwright-mcp-server`
- `npx @smithery/cli install @executeautomation/playwright-mcp-server --client claude`

### pitfalls observed

- Four distribution mechanisms (npm, mcp-get, Smithery, Docker) — this is one of the more broadly-distributed MCP servers; serves as a reference for "how many channels to publish ...

## 4. Entry point / launch

### command(s) users/hosts run

- Stdio: `npx -y @executeautomation/playwright-mcp-server`
- HTTP: `npx @executeautomation/playwright-mcp-server --port 8931`

### wrapper scripts, launchers, stubs

npm `bin` entry; Smithery and mcp-get wrappers for install orchestration

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

CLI flags (`--port` etc.); `mcp-config.json` for settings; automatic Playwright browser installation on first use

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Not applicable — browser automation against public web; no service-level auth. Sites that require auth rely on Playwright's own cookie/state mechanisms, not an MCP-layer auth flow

### where credentials come from

User-driven within browser session (manual login flows in Playwright contexts)

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

Single-user — one browser context per server process. Multi-session concurrency would require multiple launches or HTTP mode with session management (not explicitly documented)

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Browser automation (navigation, click, fill, etc.), screenshot capture, test code generation, web scraping, JavaScript execution in page context, device emulation with 143+ device presets

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Logs written to `~/playwright-mcp-server.log` in stdio mode — specifically to keep stdout clean for JSON-RPC framing. File-based log is the observability surface

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

- Claude Desktop (primary)
- Cline
- Cursor IDE
- VS Code (GitHub Copilot)

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not observed — no `.claude-plugin` directory surfaced in research

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

Jest; tests in `src/__tests__`; npm scripts wire up test runs

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions `.github/workflows` directory present; specific workflows not extracted within budget

### pitfalls observed

- Exact CI workflow set

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present; docker-compose.yml present

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`mcp-config.json` for settings; sample Claude Desktop JSON config in README; Smithery CLI as an install flow

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single-package TypeScript project

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Dual-transport from one binary — `--port` switches between stdio and HTTP, not separate entry points
- File-based logging (`~/playwright-mcp-server.log`) is a deliberate design response to the stdio framing constraint — the server cannot log to stdout without corrupting JSON-RPC
- Automatic browser install on first use reduces setup friction but introduces a first-run delay
- Device emulation with 143+ presets elevates the server beyond "headless browser" to "mobile and cross-device testing harness"

## 18. Unanticipated axes observed
- Four distribution mechanisms (npm, mcp-get, Smithery, Docker) — this is one of the more broadly-distributed MCP servers; serves as a reference for "how many channels to publish to" decisions
- 5.5k stars makes this a de facto canonical Playwright MCP despite unofficial (non-Microsoft) ownership. Microsoft's own `@playwright/mcp` exists as a competitor — both ship, neither is officially crowned

## 20. Gaps
- Last commit date not confirmed within extracted content
- Whether HTTP mode supports multi-client concurrency or is single-session
- Exact CI workflow set
- Interplay with Microsoft's `@playwright/mcp` — feature parity, divergent choices, migration paths — not surveyed
