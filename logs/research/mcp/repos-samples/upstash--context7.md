# Sample

## Identification

### url

https://github.com/upstash/context7

### stars

53,300

### last-commit

April 20, 2026 (ctx7@0.3.13)

### license

MIT

### default branch

master

### one-line purpose

Context7 documentation-context MCP server — ships `.claude-plugin/marketplace.json`; hybrid public/private backend.

## Language and runtime

### language(s) + version constraints

TypeScript (91.2%), JavaScript (8.5%); Node.js (monorepo with pnpm workspaces).

### framework/SDK in use

MCP SDK, MCP CLI, REST API backend.

## Transport

### supported transports

MCP (native), CLI + Skills (without MCP), HTTP (REST backend).

### how selected

installation via `npx ctx7 setup` handles OAuth and API-key setup; MCP mode for agents, CLI for direct use.

## Distribution

### every mechanism observed

npm (`npx ctx7 setup`), MCP HTTP endpoint (`https://mcp.context7.com/mcp`), CLI tool.

### published package name(s)

`@upstash/context7` (monorepo; individual packages in `/packages`).

### install commands shown in README

`npx ctx7 setup` (recommended, OAuth + API key); manual config via `https://mcp.context7.com/mcp`.

### pitfalls observed

one-command setup via npx with OAuth automation.

## Entry point / launch

### command(s) users/hosts run

`npx ctx7 setup`, `ctx7 library <name> <query>`, `ctx7 docs <libraryId> <query>`.

### wrapper scripts, launchers, stubs

npx setup script handles OAuth flow.

## Configuration surface

### how config reaches the server

OAuth flow via `npx ctx7 setup`; API key via `CONTEXT7_API_KEY` header (manual setup); Skills integration (client-specific).

## Authentication

### flow

OAuth (setup flow via npx); free API-key registration at context7.com/dashboard (optional, higher rate limits).

### where credentials come from

OAuth callback or API key from dashboard.

## Multi-tenancy

### tenancy model

per-user OAuth token; API key per workspace.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools: `resolve-library-id`, `query-docs` (retrieves version-specific documentation from source). resources: library index and documentation cache.

## Observability

### logging destination + format, metrics, tracing, debug flags

not explicitly documented

### pitfalls observed

logging and observability strategy not documented.

## Host integrations shown in README or repo

### Claude Code

native support documented.

### Cursor

listed as a supported agent.

### OpenAI Code

listed as a supported agent.

### Other agents

27+ other agents (30+ total). MCP config via `https://mcp.context7.com/mcp` (manual) or `npx ctx7 setup`.

## Claude Code plugin wrapper

### presence and shape

present; `.claude-plugin/marketplace.json` (marketplace metadata only, not full plugin.json).

### pitfalls observed

`.claude-plugin/marketplace.json` (not `plugin.json`) — a marketplace-style integration separate from a plugin-wrapper install.

## Tests

### presence, framework, location, notable patterns

present; monorepo test suite (`npm run test` in workspace).

## CI

### presence, system, triggers, what it runs

present; `.github/` present, `npm run lint`, `npm run format` scripts.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

no Dockerfile at root. Monorepo with pnpm workspaces and changesets (versioning).

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

single-command setup: `npx ctx7 setup`. CLI for direct documentation queries. Skills documentation for specialized tasks. MCP Inspector support. Smithery registry config.

## Repo layout

### single-package / monorepo / vendored / other

monorepo with pnpm workspaces. Dirs: `/packages`, `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n`. Config: `pnpm-workspace.yaml`, `package.json`, `tsconfig.json`, `eslint.config.js`, `prettier.config.mjs`. Additional: `.changeset/`, `.claude-plugin/` (marketplace metadata).

## Notable structural choices

monorepo supports multi-package ecosystem.

one-command setup via npx with OAuth automation.

distinction between public MCP repo and private backend (API, parsing, crawling engines).

support for 30+ client platforms.

marketplace metadata for Claude plugin discovery.

## Unanticipated axes observed

hybrid architecture: public MCP client code + private backend — axis: disclosing vs withholding server implementation.

`.claude-plugin/marketplace.json` (not `plugin.json`) — a marketplace-style integration separate from a plugin-wrapper install.

changesets-based coordinated release discipline in a monorepo.

ships both a "Skills" folder and a "rules" folder alongside the MCP server.

## Gaps

backend architecture details intentionally private (API, parsing, crawling). test/CI strategy not visible in public README. logging and observability strategy not documented. changelog/release notes not visible in README.
