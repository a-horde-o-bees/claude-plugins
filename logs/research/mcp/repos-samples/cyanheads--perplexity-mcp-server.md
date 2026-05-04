# Sample

Mirrors of `https://github.com/cyanheads/perplexity-mcp-server`. Perplexity MCP server (TypeScript) — `perplexity_search` and `perplexity_deep_research` tools with optional JWT/OAuth on HTTP transport. 22 stars; Apache-2.0; default branch `main`; last commit July 22, 2025 (inferred from pushed_at).

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript ^5.8.3 on the official MCP SDK ^1.15.0. Node.js >=18.0.0. Hono for HTTP transport; Zod for validation.

## Transport

### stdio

stdio is the default transport.

### Streamable HTTP

HTTP transport with configurable host (127.0.0.1) and port (3010).

### Selection mechanism

Environment-config-driven selection, validated via Zod.

## Capability surface

### Tools-only, hand-curated narrow surface

Two tools: `perplexity_search` (fast search-augmented) and `perplexity_deep_research` (multi-source exhaustive). Auto-complexity detection drives tool selection between them.

## Configuration delivery

### Environment variables

Transport type and logging level configurable via env vars.

### Dotenv file

`.env` file supported as config source, validated by Zod.

### CLI flags

CLI args alongside env and `.env` for credentials.

## Authentication

### Static API key / token via env var

`PERPLEXITY_API_KEY` env var carries the upstream API credential. Sourced from environment variable, CLI args, or `.env` file.

### JWT

Optional JWT for HTTP transport — multi-client capability when HTTP is selected.

### OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)

Optional OAuth 2.1 for HTTP transport. JWT and OAuth are alternatives layered atop the upstream API key, both gated by HTTP transport.

## Multi-tenancy

### Single-user / single-tenant per process

Per-user single instance by default. JWT/OAuth in HTTP mode enables multi-client support — a typically single-user server gains multi-client posture when the auth gate is enabled.

## Distribution channel

### Source clone with editable install

Source-only distribution: `git clone`, `npm install`, `npm run build`, `npm start`. Published npm package not found on registry — the project is consumed as a source clone.

## Entry point and launch

### npm scripts (start/start:stdio/start:http)

`npm start` runs the built artifact; `npm run build` compiles TypeScript to `dist/`.

### Built JS file (`node build/index.js`)

Compiled artifact in `dist/`; npm build script handles compilation.

## Build and packaging

### npm/Node toolchain

`package.json` with build scripts; multi-stage Docker for optimized image.

## Schema and types

### Zod (TypeScript)

Zod schema validation for config; runtime validation across transport selection and `.env` parsing.

## Container artifacts

### Multi-stage Dockerfile

Dockerfile present — multi-stage Node.js 18-Alpine build for optimized image.

## Test stack

### TypeScript noEmit type-check as the test command

`npm test` runs TypeScript noEmit type checks.

## CI

### GitHub Actions

`.github/` present but CI workflows not explicitly documented in README.

## Repository layout

### Single-package, organized subdirectories

Single-package Node.js/TS. Dirs: `.github/`, `src/`, `docs/`. Config files: `package.json`, `tsconfig.json`, `Dockerfile`.

## Host integration

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline MCP client config documented.

## Observability

### File-based logging

Structured logging configurable with file rotation (centralized utilities).

### Env-var-controlled log level

Log level configurable via env var.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not present; MCP server designed for compatible clients.

## Developer ergonomics

### Sample MCP client configs in repo

Sample config in README; clone + build pattern documented.

## Release and lifecycle

### Active development

Last commit July 22, 2025 (inferred from pushed_at).

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.
