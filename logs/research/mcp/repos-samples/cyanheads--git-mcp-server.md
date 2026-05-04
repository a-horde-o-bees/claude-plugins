# Sample

Mirrors of `https://github.com/cyanheads/git-mcp-server`. Git MCP server (TypeScript) — 28 tools across repo/commits/branches/remotes; dual Node+Bun runtime with base-directory sandboxing for multi-tenant usage. 207 stars; Apache-2.0; default branch `main`; last commit April 19, 2026.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript ^6.0.3 on the official MCP SDK ^1.29.0. Hono for HTTP, Pino for logging, tsyringe for DI, Zod for validation, OpenTelemetry (optional). Node.js >=20.0.0.

### TypeScript on Bun

Bun >=1.2.0 also supported as runtime; runtime auto-detection between Node and Bun.

## Transport

### stdio

stdio transport (default).

### Streamable HTTP

Streamable HTTP with configurable port 3015 and hostname.

### Selection mechanism

Environment-config driven selection (validated via Zod); separate npm scripts (`npm run start:stdio`, `npm run start:http`) for explicit mode entry.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

28 tools across 7 categories (repo management, staging/commits, history inspection, analysis, branching/merging, remote ops, advanced workflows).

### Tools plus resources plus prompts (full primitive coverage)

28 tools plus 1 resource (repo metadata) plus 1 prompt — full primitive coverage.

## Configuration delivery

### Environment variables

Zod-validated env vars: transport type, session mode, response format, Git identity, base-dir restriction, GPG/SSH commit signing, auth mode, logging level.

### CLI flags

npm scripts (`start:stdio`, `start:http`) act as transport-mode-selecting entry points.

## Authentication

### None / implicit (local-resource gating)

Default `none` mode — trust derives from transport (stdio) and base-dir restriction. `AUTH_MODE=none` for dev.

### JWT

`jwt` mode — 32+ char secret required. HTTP-mode opt-in.

### OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)

`oauth` mode with OIDC provider. One of three modes selectable via `AUTH_MODE` switch (`none|jwt|oauth`).

## Multi-tenancy

### Workspace-scoped sandboxing within a single tenant

Workspace-keyed via base-directory restriction (`BASE_DIR` env var). Server constrains per-session operations to the configured base directory. Per-session working-directory management lets one server process serve multiple stdio sessions, each scoped to its own subdirectory within the allowlisted base — adds a per-session layer atop the server-wide root constraint.

## Distribution channel

### npm via npx / bunx

npm: `npx @cyanheads/git-mcp-server@latest`. Bun: `bunx @cyanheads/git-mcp-server@latest`. Published package: `@cyanheads/git-mcp-server`.

## Entry point and launch

### `npx -y <package>` / `bunx`

Primary host-config snippet: `npx @cyanheads/git-mcp-server@latest` or `bunx @cyanheads/git-mcp-server@latest`.

### npm scripts (start/start:stdio/start:http)

`npm run start:stdio` and `npm run start:http` are the explicit transport-mode launchers.

## Build and packaging

### npm/Node toolchain

`package.json` with build scripts for both Node and Bun targets.

## Schema and types

### Zod (TypeScript)

Zod for env-var and runtime validation.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present (implied by Bun build path); no docker-compose found.

### Cloudflare Workers config

Cloudflare Workers deployment pipeline documented as an additional deploy target alongside the Dockerfile.

## Test stack

### Bun test runner with Vitest compatibility

Bun test runner with Vitest compatibility; coverage reports.

## CI

### GitHub Actions

CI present; `npm run devcheck` runs lint, format, typecheck; dependency audit; unit + integration test suite.

### Build + test + supply-chain scan

Dependency audit alongside lint/format/typecheck and test suite.

## Deployment topology

### Local stdio process per session

Default deployment as a local stdio process per session.

### Self-hosted HTTP server

HTTP transport supports self-hosted deployment shape (configurable port 3015, hostname).

### Edge / serverless deployment (Cloudflare Workers, V8 isolate)

Cloudflare Workers documented as an additional deploy target alongside the Dockerfile — `wrangler.toml`/`wrangler.jsonc` available.

## Repository layout

### Single-package, organized subdirectories

Single-package, organized by concern: `src/` (tools/, resources/, transports/, services/, storage/, config/, utils/, container/), `tests/` mirroring source structure. Config files: `package.json`, `tsconfig.json`, `.env.example`.

## Host integration

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline MCP client configs (e.g., `cline_mcp_settings.json`) documented.

## Observability

### Pino / Winston structured logging (Node)

Structured logging via Pino; log level configurable via env var.

### Request context tracking for audit

Request context tracking for auditing.

### OpenTelemetry instrumentation

Optional OpenTelemetry for traces and metrics (instrumentation off by default).

### Env-var-controlled log level

Log level configured via env var.

## Developer ergonomics

### Linter and type-checker stack

`npm run devcheck` aggregates lint, format, and typecheck.

### Sample MCP client configs in repo

MCP client configuration examples in repo; dev mode with file watching; session-specific working-directory management.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not present.

## Release and lifecycle

### Active development

Last commit April 19, 2026; 207 stars.

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.
