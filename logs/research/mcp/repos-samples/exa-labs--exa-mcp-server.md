# Sample

## Identification

### url

https://github.com/exa-labs/exa-mcp-server

### stars

4,300

### last-commit

April 19, 2026

### license

MIT

### default branch

main

### one-line purpose

Exa search MCP server — web search and content extraction tools; ships `.claude-plugin/` and native Claude Desktop connector.

## Language and runtime

### language(s) + version constraints

TypeScript (97.9%); Node.js >=18.0.0.

### framework/SDK in use

MCP SDK ^1.12.1, exa-js ^2.8.0, Zod validation, jose (JWT).

## Transport

### supported transports

HTTP (remote MCP endpoint `https://mcp.exa.ai/mcp`), stdio, HTTP local.

### how selected

remote endpoint default; clients select via config.

## Distribution

### every mechanism observed

npm (`exa-mcp-server`), remote HTTP endpoint, pre-built IDE installers (Cursor/VS Code), Docker.

### published package name(s)

`exa-mcp-server` on npm.

### install commands shown in README

`npm install exa-mcp-server`, remote URL `https://mcp.exa.ai/mcp`, one-click installers.

### pitfalls observed

Smithery registry packaging.

## Entry point / launch

### command(s) users/hosts run

remote HTTP, local npm package, Docker.

### wrapper scripts, launchers, stubs

Cursor/VS Code one-click installers.

## Configuration surface

### how config reaches the server

client config files (Cursor `~/.cursor/mcp.json`, VS Code `.vscode/mcp.json`, Claude Desktop `~/Library/Application Support/Claude/claude_desktop_config.json`), `EXA_API_KEY` env var or URL parameter.

## Authentication

### flow

API key from dashboard.exa.ai.

### where credentials come from

environment variable `EXA_API_KEY` or URL parameter.

## Multi-tenancy

### tenancy model

per-client multi-tenancy via HTTP endpoint; API key scoped to user account.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

`web_search_exa`, `web_fetch_exa`, `web_search_advanced_exa`; advanced filtering by domain, date, content type. Specialized skills directory: company research, code search, people research, financial reports, academic papers.

## Observability

### logging destination + format, metrics, tracing, debug flags

documentation references available but not detailed; presumed via service dashboard.

### pitfalls observed

logging configuration details unclear.

## Host integrations shown in README or repo

### Claude Desktop

native connector, no manual config.

### Cursor

pre-built installer.

### VS Code

pre-built installer.

### Codex

JSON `mcp.json` (host-dependent paths).

### OpenCode

JSON `mcp.json` (host-dependent paths).

### Antigravity

JSON `mcp.json` (host-dependent paths).

### Windsurf

JSON `mcp.json` (host-dependent paths).

### Zed

JSON `mcp.json` (host-dependent paths).

### Gemini CLI

JSON `mcp.json` (host-dependent paths).

### v0 by Vercel

JSON `mcp.json` (host-dependent paths).

### Warp

JSON `mcp.json` (host-dependent paths).

### Kiro

JSON `mcp.json` (host-dependent paths).

### Roo Code

JSON `mcp.json` (host-dependent paths).

## Claude Code plugin wrapper

### presence and shape

present; `.claude-plugin/plugin.json` with HTTP server config (type: http, url: `https://mcp.exa.ai/mcp?client=claude-code-plugin`, custom header `x-exa-source: claude-code-plugin`).

## Tests

### presence, framework, location, notable patterns

not explicitly documented.

## CI

### presence, system, triggers, what it runs

not explicitly documented.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile (Node.js-based); Vercel deployment config (`vercel.json`); no docker-compose.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

pre-built installers for Cursor/VS Code (one-click); native Claude Desktop connector (auto-config); skills directory with specialized research templates; `llm_mcp_docs.txt` (411.7 KB large documentation); Smithery registry config (`smithery.yaml`).

## Repo layout

### single-package / monorepo / vendored / other

single-package. Dirs: `src/`, `api/`, `skills/`, `public/`. Config: `package.json`, `tsconfig.json`, `Dockerfile`, `.claude-plugin/`. Integration configs: `gemini-extension.json`, `smithery.yaml`, `server.json`.

## Notable structural choices

Remote HTTP endpoint as primary distribution (reduces setup friction). Native Claude Desktop connector (no manual config needed). Specialized skills for vertical use cases. High client compatibility (15+ platforms). Smithery registry packaging.

## Unanticipated axes observed

Native Claude Desktop connector vs JSON config for other clients — axis: host-native integration surface (deeplink/connector) vs config snippet. Vertical-specific research skills shipped alongside the server — axis: "skills" as first-class shipping artifact. Pre-built IDE installers (Cursor/VS Code one-click) — axis: distribution beyond package managers. `llm_mcp_docs.txt` shipped as in-repo doc designed for LLM ingestion.

## Gaps

testing/CI strategy not documented. logging configuration details unclear. rate limiting and plan tiers not documented in README.
