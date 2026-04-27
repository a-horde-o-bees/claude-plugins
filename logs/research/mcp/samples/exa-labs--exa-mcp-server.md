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

## 1. Language and runtime

### language(s) + version constraints

TypeScript (97.9%); Node.js >=18.0.0

### framework/SDK in use

MCP SDK ^1.12.1, exa-js ^2.8.0, Zod validation, jose (JWT)

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

HTTP (remote MCP endpoint `https://mcp.exa.ai/mcp`), stdio, HTTP local

### how selected

remote endpoint default; clients select via config

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

npm (`exa-mcp-server`), remote HTTP endpoint, pre-built IDE installers (Cursor/VS Code), Docker

### published package name(s)

`exa-mcp-server` on npm

### install commands shown in README

`npm install exa-mcp-server`, remote URL `https://mcp.exa.ai/mcp`, one-click installers

### pitfalls observed

  - Smithery registry packaging

## 4. Entry point / launch

### command(s) users/hosts run

remote HTTP, local npm package, Docker

### wrapper scripts

Cursor/VS Code one-click installers

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

client config files (Cursor `~/.cursor/mcp.json`, VS Code `.vscode/mcp.json`, Claude Desktop `~/Library/Application Support/Claude/claude_desktop_config.json`), `EXA_API_KEY` env var or URL parameter

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

API key from dashboard.exa.ai

### where credentials come from

environment variable `EXA_API_KEY` or URL parameter

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

- per-client multi-tenancy via HTTP endpoint; API key scoped to user account

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools

`web_search_exa`, `web_fetch_exa`, `web_search_advanced_exa`; advanced filtering by domain, date, content type

### specialized skills directory

company research, code search, people research, financial reports, academic papers

### pitfalls observed

none noted in this repo

## 9. Observability

### logging

documentation references available but not detailed; presumed via service dashboard

### pitfalls observed

  - logging configuration details unclear

## 10. Host integrations shown in README or repo

- Claude Desktop (native connector, no manual config)
- Cursor (pre-built installer)
- VS Code (pre-built installer)
- Codex, OpenCode, Antigravity, Windsurf, Zed, Gemini CLI, v0 by Vercel, Warp, Kiro, Roo Code — 15+ clients documented

### form

JSON `mcp.json` (host-dependent paths)

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

- present; `.claude-plugin/plugin.json` with HTTP server config (type: http, url: `https://mcp.exa.ai/mcp?client=claude-code-plugin`, custom header `x-exa-source: claude-code-plugin`)

### pitfalls observed

none noted in this repo

## 12. Tests

- not explicitly documented

### pitfalls observed

none noted in this repo

## 13. CI

- not explicitly documented

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

- Dockerfile (Node.js-based); Vercel deployment config (`vercel.json`); no docker-compose

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

- pre-built installers for Cursor/VS Code (one-click)
- native Claude Desktop connector (auto-config)
- skills directory with specialized research templates
- `llm_mcp_docs.txt` (411.7 KB large documentation)
- Smithery registry config (`smithery.yaml`)

### pitfalls observed

none noted in this repo

## 16. Repo layout

- single-package

### dirs

`src/`, `api/`, `skills/`, `public/`

### config

`package.json`, `tsconfig.json`, `Dockerfile`, `.claude-plugin/`

### integration configs

`gemini-extension.json`, `smithery.yaml`, `server.json`

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

- remote HTTP endpoint as primary distribution (reduces setup friction)
- native Claude Desktop connector (no manual config needed)
- specialized skills for vertical use cases
- high client compatibility (15+ platforms)
- Smithery registry packaging

## 18. Unanticipated axes observed

- native Claude Desktop connector vs JSON config for other clients — axis: host-native integration surface (deeplink/connector) vs config snippet
- vertical-specific research skills shipped alongside the server — axis: "skills" as first-class shipping artifact
- pre-built IDE installers (Cursor/VS Code one-click) — axis: distribution beyond package managers
- `llm_mcp_docs.txt` shipped as in-repo doc designed for LLM ingestion

## 20. Gaps

- testing/CI strategy not documented
- logging configuration details unclear
- rate limiting and plan tiers not documented in README
