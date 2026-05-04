# Sample

Mirrors of `https://github.com/ppl-ai/modelcontextprotocol`. Perplexity MCP server (official Perplexity-AI org slug `ppl-ai`) — search-augmented answering across four product tiers (search, ask, research, reason). 2.1k stars, MIT, default branch `main`, 133 total commits.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (95.2%); Node.js runtime; standard MCP TypeScript SDK.

## Transport

### stdio

stdio is the default transport.

### Streamable HTTP

HTTP server deployment supported; `PORT` and `BIND_ADDRESS` env vars plus CORS support enable shared-server deployments where multiple clients hit one process.

### Selection mechanism

HTTP mode is selected by setting `PORT` and `BIND_ADDRESS` env vars; otherwise stdio default — implicit-default selection via env var presence.

## Capability surface

### Tools-only, hand-curated narrow surface

Four tools mapping 1:1 to Perplexity product tiers — `perplexity_search` (web search via Search API), `perplexity_ask` (conversational AI with sonar-pro model), `perplexity_research` (deep research via sonar-deep-research), `perplexity_reason` (advanced reasoning via sonar-reasoning-pro). Tool boundaries mirror Perplexity model variants rather than low-level API endpoints.

## Configuration delivery

### Environment variables

`PERPLEXITY_API_KEY` (required), `PERPLEXITY_TIMEOUT_MS` (default 300000ms), `PERPLEXITY_BASE_URL`, `PORT`, `BIND_ADDRESS`, plus proxy configuration. `PERPLEXITY_PROXY` takes priority over standard `HTTPS_PROXY`/`HTTP_PROXY` — Perplexity-specific proxy overrides system-wide settings, recognizing corporate/enterprise environments where a specific proxy needs to override system defaults.

### Host-side JSON config snippet

Quick-install badges in README for Cursor, VS Code, Claude Desktop, Kiro, Windsurf.

## Authentication

### Static API key / token via env var

`PERPLEXITY_API_KEY` env var; user obtains key from Perplexity API Portal.

## Multi-tenancy

### Single-user / single-tenant per process

API key is process-scoped; per-request tenancy is Perplexity-account-level.

## Distribution channel

### npm via npx / bunx

`npx -y @perplexity-ai/mcp-server` is the documented install command.

### Docker / OCI image

Dockerfile included for containerized deployment.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx -y @perplexity-ai/mcp-server`; npm bin entry. Quick-install badges for Cursor, VS Code, Claude Desktop, Kiro, Windsurf.

## Test stack

### Vitest (TypeScript / Node)

vitest configured; specific layout not extracted within budget.

## CI

### GitHub Actions

GitHub Actions workflows present; specific jobs not extracted within budget.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile included.

## Host integration

### Claude Desktop

Quick-install badge.

### Cursor

Quick-install badge.

### VS Code / VS Code Insiders / Visual Studio family

Quick-install badge.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Windsurf and Kiro quick-install badges.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not explicitly observed within extracted content.

## Documentation surface

### README as the canonical surface

README hosts per-host quick-install badges and integration guidance; HTTP mode with CORS for shared deployments documented.

## Repository layout

### Single-package src-layout

Single-package TypeScript project; source in `/src`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

133 total commits; brand-canonical (org slug differs from brand: `ppl-ai` rather than `perplexityai`).
