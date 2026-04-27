# Sample

## Identification

### url

https://github.com/idosal/git-mcp

### stars

8,000

### last-commit

March 13, 2026

### license

Apache-2.0

### default branch

main

### one-line purpose

Hosted git-documentation MCP service — cloud-hosted SaaS endpoint, zero-auth; no local install.

## Language and runtime

### language(s) + version constraints

TypeScript/JavaScript; Node.js runtime (npx, pnpm, npm).

### framework/SDK in use

React Router 7, Vite, MCP SDK, Cloudflare Workers (Wrangler).

## Transport

### supported transports

HTTP/HTTPS (cloud endpoint gitmcp.io), SSE.

### how selected

auto-detected by IDE via direct HTTP URL specification.

## Distribution

### every mechanism observed

npm/pnpm source build; direct URL endpoint (cloud-hosted gitmcp.io); self-hosted option.

### published package name(s)

not on npm registry; cloud-hosted at gitmcp.io.

### install commands shown in README

`pnpm install`, `npm run dev`, endpoint `https://gitmcp.io/{owner}/{repo}`.

## Entry point / launch

### command(s) users/hosts run

`npm run dev`, `pnpm dev`, `npx mcp-remote https://gitmcp.io/{owner}/{repo}`.

### wrapper scripts, launchers, stubs

React Router dev scripts; Wrangler for Cloudflare Workers deployment.

## Configuration surface

### how config reaches the server

IDE JSON configs (Cursor, Claude Desktop, Windsurf, VSCode, Cline); dynamic endpoint `gitmcp.io/{owner}/{repo}`.

## Authentication

### flow

none required.

### where credentials come from

not applicable; zero-auth cloud service.

## Multi-tenancy

### tenancy model

per-repository tenant (parameterized by owner/repo); cloud-hosted single service with multi-repo support.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

`fetch_<repo-name>_documentation`, `search_<repo-name>_documentation`, `search_<repo-name>_code`, `fetch_url_content`.

## Observability

### logging destination + format, metrics, tracing, debug flags

not documented; presumed server-side.

### pitfalls observed

server-side logging strategy unclear.

## Host integrations shown in README or repo

### Claude Desktop

JSON `mcp.json` config documented in README.

### Cursor

JSON `mcp.json` config documented in README.

### Windsurf

JSON `mcp.json` config documented in README.

### VSCode

JSON `mcp.json` config documented in README.

### Cline

JSON `mcp.json` config documented in README.

### Highlight AI

JSON `mcp.json` config documented in README.

### Augment Code

JSON `mcp.json` config documented in README.

### Msty AI

JSON `mcp.json` config documented in README.

## Claude Code plugin wrapper

### presence and shape

not present; uses MCP protocol.

## Tests

### presence, framework, location, notable patterns

present; Playwright E2E (`playwright.config.ts`), Vitest units (`vitest.config.ts`), `npm run test`.

## CI

### presence, system, triggers, what it runs

present; GitHub Actions: `e2e-tests.yml`, `run-tests.yml`.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

no Dockerfile; Cloudflare Workers cloud-native deployment.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

dev scripts, Playwright E2E tests, README examples.

## Repo layout

### single-package / monorepo / vendored / other

single-package React/TS with Cloudflare integration. Dirs: `.github/`, `.husky/`, `.react-router/`, `app/`, `src/`, `static/`, `tests/`, `dist/`. Config: `wrangler.jsonc`, `react-router.config.ts`, `vite.config.ts`, `vitest.config.ts`.

## Notable structural choices

Cloud-hosted SaaS MCP endpoint removes installation friction. Zero-auth model for public repos. React Router 7 + Vite for frontend. Biome for unified linting/formatting.

## Unanticipated axes observed

MCP server delivered as a cloud-hosted service rather than self-hosted — axis: hosted vs local installation. Parameterized repository endpoints — one deployment serves every GitHub repo.

## Gaps

Node.js version constraints not in README. server-side logging strategy unclear. self-hosting details limited; Cloudflare dependency unclear.
