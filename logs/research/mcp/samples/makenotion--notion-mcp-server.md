# Sample

## Identification

### url

https://github.com/makenotion/notion-mcp-server

### stars

4,200

### last-commit

March 18, 2026

### license

MIT

### default branch

main

### one-line purpose

Notion MCP server — Notion API wrapper; ships `CLAUDE.md` in the repo.

## 1. Language and runtime

### language(s) + version constraints

TypeScript 5.8.2; Node.js (specified in scripts)

### framework/SDK in use

MCP SDK ^1.25.1, Express 4.21.2, axios 1.8.4, openapi-client-axios 7.5.5, Zod 3.24.1

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

STDIO (default), Streamable HTTP (configurable port, default 8080)

### how selected

CLI argument `--transport http [--port 8080]`

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

npm package (`@notionhq/notion-mcp-server`), Docker (`mcp/notion`), local build from source

### published package name(s)

`@notionhq/notion-mcp-server`

### install commands shown in README

`npx @notionhq/notion-mcp-server`, `npx @notionhq/notion-mcp-server --transport http [--port 8080]`, Docker pull, local build

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`npx @notionhq/notion-mcp-server` and HTTP variant

### wrapper scripts, launchers, stubs

npm build (tsc + esbuild), npm dev (tsx watch)

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

env var `NOTION_TOKEN` (recommended) or `OPENAPI_MCP_HEADERS`; Bearer token for HTTP; client config files (Claude Desktop, Cursor, Zed, GitHub Copilot CLI)

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Notion API integration token (required)

### where credentials come from

`NOTION_TOKEN` env var, CLI args, or HTTP Bearer header

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

per-integration-token; HTTP transport supports multiple clients

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

22 tools — page create/retrieve, database query, page move, commenting, content search

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

not explicitly documented

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

`claude_desktop_config.json`

### Cursor

`.cursor/mcp.json`

### Zed

`settings.json`

### GitHub Copilot CLI

config documented

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not present

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

present; Vitest (`npm test`, `npm run test:watch`, `npm run test:coverage`); `NODE_ENV=test`; coverage reports

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

present; GitHub Actions workflows; `npm run build`, `npm test` in pipeline

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile (Node.js-based); `docker-compose.yml`; official Docker Hub image (`mcp/notion`)

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

configuration examples for 4 host integrations; Docker installation documented; local symlink testing via `npm link` for Cursor; `CLAUDE.md` file (Claude-specific guidance)

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package, organized. Directories: `src/`, `docs/`, `scripts/`, `.github/`. Config: `package.json`, `tsconfig.json`, `vitest.config.ts`, `Dockerfile`, `docker-compose.yml`. Documentation: `CLAUDE.md`, `README.md`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Official Notion-authored MCP server (first-party). Comprehensive test coverage (Vitest with coverage). Multi-host integration examples (4 platforms). Docker + docker-compose for containerized deployment. Explicit `CLAUDE.md` in repo.

## 18. Unanticipated axes observed

`CLAUDE.md` shipped in the repo itself (guidance for Claude when working in the repo) — axis: agent-facing meta-documentation inside a server repo. OpenAPI client generation (openapi-client-axios) — axis: auto-derived tools from an OpenAPI spec vs hand-authored.

## 20. Gaps

Logging/observability strategy not documented. Rate limiting and Notion API quota handling not detailed. V2.0 migration details not in README (changelog reference only).
