# Sample

Mirrors of `https://github.com/makenotion/notion-mcp-server`. Notion API wrapper MCP server — pages, databases, comments, content search; first-party Notion-authored. 4,200 stars, MIT, default branch `main`, last commit March 18, 2026.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript 5.8.2 server built on `@modelcontextprotocol/sdk` ^1.25.1, paired with Express 4.21.2 for the HTTP transport, axios 1.8.4 for outbound Notion API calls, openapi-client-axios 7.5.5 for OpenAPI-driven client generation, and Zod 3.24.1 for runtime validation. Node.js runtime (version constraint specified in `scripts` but not surfaced explicitly).

## Transport

### stdio

Default transport.

### Streamable HTTP

Configurable port (default 8080) when invoked with `--transport http [--port 8080]`.

### Selection mechanism

CLI flag at startup — `--transport http [--port 8080]` flips to HTTP mode; absence defaults to stdio.

## Capability surface

### Domain-bundled tool set

22 tools covering page create/retrieve, database query, page move, commenting, and content search — entity-organized around Notion's primary resource types (pages, databases, comments).

## Configuration delivery

### Environment variables

`NOTION_TOKEN` (recommended) or `OPENAPI_MCP_HEADERS` for credentials.

### HTTP request headers

Bearer token on HTTP transport.

### Host-side JSON config snippet

Documented configurations for Claude Desktop, Cursor, Zed, and GitHub Copilot CLI.

## Authentication

### Static API key / token via env var

Notion API integration token required, supplied via `NOTION_TOKEN` env var, CLI args, or HTTP `Authorization: Bearer` header.

### Bearer token over HTTP/SSE

HTTP-mode acceptance of Bearer tokens for transport-layer auth.

## Multi-tenancy

### Single-user / single-tenant per process

Per-integration-token; one credential, one identity.

### Multi-client sharing one process via session multiplexing

HTTP transport supports multiple clients connecting to the same process.

## Distribution channel

### npm via npx / bunx

Published as `@notionhq/notion-mcp-server`; install via `npx @notionhq/notion-mcp-server` (stdio) or `npx @notionhq/notion-mcp-server --transport http [--port 8080]`.

### Docker / OCI image

Official image `mcp/notion` on Docker Hub.

### Source clone with editable install

Local build from source via `npm build` (tsc + esbuild) and `npm link` for Cursor symlink testing.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx @notionhq/notion-mcp-server` for stdio; HTTP variant adds `--transport http`.

### Docker container entrypoint

Docker Hub `mcp/notion` image.

## Build and packaging

### npm/Node toolchain

`package.json` with build via tsc + esbuild; dev mode via `npm dev` (tsx watch).

## Schema and types

### Zod (TypeScript)

Zod 3.24.1 for runtime validation in tool inputs and configuration.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile (Node.js-based) at repo root.

### Docker Compose for local dev

`docker-compose.yml` present.

### Published Docker image

Official Docker Hub image `mcp/notion`.

## Test stack

### Vitest (TypeScript / Node)

Vitest test runner (`npm test`, `npm run test:watch`, `npm run test:coverage`); `NODE_ENV=test`; coverage reports.

## CI

### GitHub Actions

`.github/workflows/` present; pipeline runs `npm run build` and `npm test`.

## Host integration

### Per-host README JSON snippets

Configuration examples documented for four host integrations: Claude Desktop (`claude_desktop_config.json`), Cursor (`.cursor/mcp.json`), Zed (`settings.json`), GitHub Copilot CLI.

## Documentation surface

### README as the canonical surface

Single README.md with multi-host integration snippets and Docker installation guidance.

### Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)

`CLAUDE.md` shipped at repo root providing Claude-specific guidance for agents working in the codebase.

## Repository layout

### Single-package, organized subdirectories

Single-package layout. Directories: `src/`, `docs/`, `scripts/`, `.github/`. Config: `package.json`, `tsconfig.json`, `vitest.config.ts`, `Dockerfile`, `docker-compose.yml`. Documentation: `CLAUDE.md`, `README.md`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT license.

### Active development

Last commit March 18, 2026; ongoing maintenance.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin/` directory; users wire via `claude mcp add` or JSON config.
