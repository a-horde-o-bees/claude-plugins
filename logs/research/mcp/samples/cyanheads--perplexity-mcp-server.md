# Sample

## Identification

### url

https://github.com/cyanheads/perplexity-mcp-server

### stars

22

### last-commit

July 22, 2025

### license

Apache-2.0

### default branch

main

### one-line purpose

Perplexity MCP server (TypeScript) — `perplexity_search` and `perplexity_deep_research` tools with optional JWT/OAuth on HTTP transport.

## Language and runtime

### language(s) + version constraints

TypeScript ^5.8.3; Node.js >=18.0.0.

### framework/SDK in use

MCP SDK ^1.15.0, Hono (HTTP transport), Zod validation.

## Transport

### supported transports

stdio (default), HTTP (configurable host 127.0.0.1, port 3010).

### how selected

environment config, validated via Zod.

## Distribution

### every mechanism observed

npm (source clone + build).

### published package name(s)

not found on npm registry.

### install commands shown in README

`git clone`, `npm install`, `npm run build`, `npm start`.

## Entry point / launch

### command(s) users/hosts run

`npm start`.

### wrapper scripts, launchers, stubs

npm build script compiles TS to `dist/`.

## Configuration surface

### how config reaches the server

`.env` file validated by Zod; transport type and logging level configurable.

## Authentication

### flow

API key (PERPLEXITY_API_KEY) plus optional JWT or OAuth 2.1 for HTTP transport.

### where credentials come from

environment variable, CLI args, or `.env` file.

## Multi-tenancy

### tenancy model

per-user single instance; JWT/OAuth enables multi-client support in HTTP mode.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

`perplexity_search` (fast search-augmented), `perplexity_deep_research` (multi-source exhaustive).

## Observability

### logging destination + format, metrics, tracing, debug flags

structured, configurable with file rotation (centralized utilities).

## Host integrations shown in README or repo

### Cline

MCP client config documented.

## Claude Code plugin wrapper

### presence and shape

not present; MCP server designed for compatible clients.

## Tests

### presence, framework, location, notable patterns

present; `npm test` runs TypeScript noEmit type checks.

## CI

### presence, system, triggers, what it runs

not explicitly documented in README; `.github/` present.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present (multi-stage Node.js 18-Alpine build).

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

clone + build pattern; sample config in README.

## Repo layout

### single-package / monorepo / vendored / other

single-package Node.js/TS; dirs: `.github/`, `src/`, `docs/`; config files: `package.json`, `tsconfig.json`, `Dockerfile`.

## Notable structural choices

Clean separation of stdio/HTTP transports via Hono. Structured logging with file rotation for production. Zod schema validation for config. Multi-stage Docker for optimized image.

## Unanticipated axes observed

Optional JWT/OAuth for HTTP mode (multi-client support in a typically single-user server). Auto-complexity detection for tool selection.

## Gaps

Exact last commit date inferred from pushed_at (July 22, 2025); no changelog. CI/CD strategy not documented. Published npm package name not found — source-only distribution.
