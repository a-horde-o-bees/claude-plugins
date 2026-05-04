# Sample

Mirrors of `https://github.com/executeautomation/mcp-playwright`. Playwright browser-automation MCP server — scripted browser actions for end-to-end testing and scraping; 143+ device emulation presets; published across four channels (npm, mcp-get, Smithery, Docker). 5.5k stars, MIT, default branch `main`.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (93.6%) on Node.js (npx/npm-based distribution). README describes alignment with Anthropic's Claude Agent SDK conventions; Playwright is the underlying browser-automation engine.

## Transport

### stdio

Recommended for Claude Desktop. Default when launched via `npx`.

### Streamable HTTP

Standalone server mode.

### SSE (Server-Sent Events)

HTTP/SSE supported in standalone server mode.

### Selection mechanism

CLI flag at startup — stdio default; HTTP enabled by passing `--port <n>` (e.g. `--port 8931`). Dual-transport from one binary — `--port` switches between stdio and HTTP, not separate entry points.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Browser automation: navigation, click, fill, screenshot capture, test code generation, web scraping, JavaScript execution in page context, device emulation with 143+ device presets. Elevates the server beyond "headless browser" to "mobile and cross-device testing harness".

## Configuration delivery

### CLI flags

`--port` and similar CLI flags.

### Sidecar config files (JSON / YAML / TOML / EDN)

`mcp-config.json` for settings.

## Authentication

### None / implicit (local-resource gating)

Browser automation against public web — no service-level MCP-layer auth. Sites that require auth rely on Playwright's own cookie/state mechanisms in browser sessions, not an MCP-layer auth flow. User-driven within browser session (manual login flows in Playwright contexts).

## Multi-tenancy

### Single-user / single-tenant per process

One browser context per server process. Multi-session concurrency would require multiple launches or HTTP mode with session management (not explicitly documented).

## Distribution channel

### npm via npx / bunx

`npm install -g @executeautomation/playwright-mcp-server`. Published as `@executeautomation/playwright-mcp-server`.

### Aggregator/installer registry

`npx @michaellatman/mcp-get@latest install @executeautomation/playwright-mcp-server` (mcp-get).

### Smithery registry

`npx @smithery/cli install @executeautomation/playwright-mcp-server --client claude`.

### Docker / OCI image

Dockerfile present alongside docker-compose.yml.

### Multi-channel publication

Four parallel distribution mechanisms: npm, mcp-get aggregator, Smithery, and Docker.

## Entry point and launch

### `npx -y <package>` / `bunx`

Stdio: `npx -y @executeautomation/playwright-mcp-server`. HTTP: `npx @executeautomation/playwright-mcp-server --port 8931`.

### Console script via `[project.scripts]` / npm bin

npm `bin` entry; Smithery and mcp-get wrappers for install orchestration.

## Build and packaging

### npm/Node toolchain

`package.json` defines build and bin entries; npm registry is the publish target.

### System-level dependencies

Browser runtime (Playwright) — automatic browser installation on first use reduces setup friction but introduces a first-run delay.

## Test stack

### Jest (TypeScript / Node)

Jest; tests in `src/__tests__`; npm scripts wire up test runs.

## CI

### GitHub Actions

`.github/workflows` directory present; specific workflows not extracted within budget.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

### Docker Compose for local dev

`docker-compose.yml` present.

## Observability

### File-based logging

Logs written to `~/playwright-mcp-server.log` in stdio mode — a deliberate design response to the stdio framing constraint. The server cannot log to stdout without corrupting JSON-RPC; file-based log is the observability surface.

## Host integration

### Claude Desktop

Primary host integration; sample Claude Desktop JSON config in README.

### Cursor

Documented host integration (Cursor IDE).

### VS Code / VS Code Insiders / Visual Studio family

Documented integration via GitHub Copilot.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline documented as a host integration.

## Repository layout

### Single-package source (language-conventional)

Single-package TypeScript project.

## Documentation surface

### Per-host README integration sections

Per-host config snippets in README (Claude Desktop, Cline, Cursor IDE, VS Code via Copilot).

### Sidecar config files (JSON / YAML / TOML / EDN)

`mcp-config.json` for settings; sample Claude Desktop JSON config in README.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
