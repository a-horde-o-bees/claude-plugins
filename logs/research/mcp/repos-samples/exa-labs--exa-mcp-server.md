# Sample

Mirrors of `https://github.com/exa-labs/exa-mcp-server`. Exa search MCP server — web search and content extraction; ships native Claude Desktop connector, `.claude-plugin/` wrapper, pre-built IDE installers, and vertical "skills" packs alongside the server. 4,300 stars, MIT, default branch `main`, last commit April 19, 2026.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (97.9%) on Node.js >=18.0.0 with MCP SDK ^1.12.1, exa-js ^2.8.0, Zod for validation, jose for JWT.

## Transport

### Hosted remote endpoint (vendor-operated)

Primary endpoint is a vendor-hosted HTTPS service: `https://mcp.exa.ai/mcp`.

### Streamable HTTP

Local HTTP supported.

### stdio

Local stdio supported via the npm package.

### Selection mechanism

Implicit default to remote endpoint; clients select via config — host points at the URL directly or runs the npm package locally.

## Capability surface

### Tools-only, hand-curated narrow surface

`web_search_exa`, `web_fetch_exa`, `web_search_advanced_exa` — three search/fetch tools with advanced filtering by domain, date, content type.

### Bundled "agent SOPs" / vertical skill packs

Specialized skills directory: company research, code search, people research, financial reports, academic papers — vertical-specific research skills shipped alongside the server as first-class artifacts.

## Configuration delivery

### Host-side JSON config snippet

Client config files: Cursor `~/.cursor/mcp.json`, VS Code `.vscode/mcp.json`, Claude Desktop `~/Library/Application Support/Claude/claude_desktop_config.json`.

### Environment variables

`EXA_API_KEY`.

## Authentication

### Static API key / token via env var

`EXA_API_KEY` env var; key obtained from dashboard.exa.ai. Also supplied via URL parameter for the hosted endpoint.

## Multi-tenancy

### Per-request tenancy by inbound credential / bearer token

Per-client multi-tenancy via the HTTP endpoint; API key scoped to the user's account on each request.

## Distribution channel

### npm via npx / bunx

`npm install exa-mcp-server` — published as `exa-mcp-server` on npm.

### Hosted endpoint (no install)

Remote URL `https://mcp.exa.ai/mcp` — primary distribution, reduces setup friction.

### Pre-built host installer / one-click install URL

Pre-built one-click installers for Cursor and VS Code.

### Docker / OCI image

Dockerfile (Node.js-based) present.

### Smithery registry

Smithery registry packaging via `smithery.yaml`.

## Entry point and launch

### `npx -y <package>` / `bunx`

Local npm package launch; `npx` flow for stdio.

### URL configuration (no local launch)

Remote HTTP endpoint launch — host config carries the URL; nothing executes locally.

### Docker container entrypoint

Docker as alternative launch path.

## Build and packaging

### npm/Node toolchain

`package.json`, `tsconfig.json` — standard TS/Node tooling.

## Schema and types

### Zod (TypeScript)

Zod for validation.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present.

### Vercel deployment config

`vercel.json` deployment config — hosted-endpoint backend pattern.

## Deployment topology

### Hosted SaaS endpoint

Primary deployment is a vendor-operated SaaS endpoint at `https://mcp.exa.ai/mcp`.

## Host integration

### Claude Desktop

Native connector — no manual config needed. The lowest-friction host integration available; limited to vendor partnerships approved by host authors.

### Native host connector

Claude Desktop's built-in awareness of the server eliminates manual config — first-party native connector pattern.

### Cursor

Pre-built one-click installer.

### VS Code / VS Code Insiders / Visual Studio family

Pre-built one-click installer.

### Codex CLI / Copilot CLI / Gemini CLI

Codex JSON `mcp.json` (host-dependent paths). Gemini CLI JSON `mcp.json`.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

JSON `mcp.json` integrations for Windsurf, Kiro, Roo Code (host-dependent paths).

### Zed

JSON `mcp.json` integration.

### Cloudflare AI Playground / OpenAI Responses API / OpenAI Agents SDK

Documented integration with v0 by Vercel, OpenCode, Antigravity, Warp.

### First-party host extension manifest

`gemini-extension.json` declares first-class Gemini integration. `server.json` for additional host-integration metadata.

## Claude Code plugin / skill wrapper

### `.claude-plugin/` wrapper

`.claude-plugin/plugin.json` with HTTP server config (type: http, url: `https://mcp.exa.ai/mcp?client=claude-code-plugin`, custom header `x-exa-source: claude-code-plugin`).

## Repository layout

### Single-package source (language-conventional)

Single-package layout. Dirs: `src/`, `api/`, `skills/`, `public/`. Config: `package.json`, `tsconfig.json`, `Dockerfile`, `.claude-plugin/`. Integration configs: `gemini-extension.json`, `smithery.yaml`, `server.json`.

## Documentation surface

### Per-host README integration sections

15+ host platforms with config snippets per host.

### `llms.txt` / `llms-full.txt`

`llm_mcp_docs.txt` shipped (411.7 KB) as in-repo doc designed for LLM ingestion.

### `agents/` example directory

Skills directory with specialized research templates.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

Active — last commit April 19, 2026.
