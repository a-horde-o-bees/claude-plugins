# Sample

Mirrors of `https://github.com/spences10/mcp-turso-cloud`. Turso (libSQL) cloud MCP server — community-canonical (15 stars, MIT, default branch `main`); not under `tursodatabase/*`. v0.0.2 released March 20, 2025. TypeScript MCP that bridges Turso's two-tier credential model (org token mints per-database tokens) to MCP, with vector similarity search exposed as a first-class tool.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (92.4%) / JavaScript (7.6%) on Node.js. Anthropic MCP TypeScript SDK + libSQL client for Turso. Compiled output at `dist/index.js`; `npm run build` for local compile.

## Transport

### stdio

Stdio transport, standard for npx-launched servers — never explicitly named in README, inferred from the `npx -y mcp-turso-cloud` consumption pattern. Implicit single mode (no transport-selection mechanism).

## Capability surface

### Domain-bundled tool set

Tools split into two groups: organization operations (list/create/delete databases, token generation) and database operations (list tables, `execute_read_only_query`, `execute_query` (destructive), schema inspection, vector similarity search). Vector similarity search exposed as first-class tool. No resources, prompts, sampling, or roots documented.

### Read/write tool split

Explicit tool split between `execute_read_only_query` (SELECT/PRAGMA) and `execute_query` (DML/DDL) supports different approval workflows at the MCP-client layer.

## Configuration delivery

### Environment variables

`TURSO_API_TOKEN` (required), `TURSO_ORGANIZATION` (required), `TURSO_DEFAULT_DATABASE` (optional), `TOKEN_EXPIRATION` (default 7 days), `TOKEN_PERMISSION` (default full-access). Env-only configuration surface.

## Authentication

### Static API key / token via env var

`TURSO_API_TOKEN` is an org-level Turso API token supplied via env var. Single credential per process. The server uses this token to mint short-lived per-database child tokens — see `Server-managed token rotation`.

### Server-managed token rotation

Org-level `TURSO_API_TOKEN` is the long-lived secret; the server generates database-specific tokens automatically with configurable permission granularity. `TOKEN_EXPIRATION` (default 7 days) and `TOKEN_PERMISSION` (default full-access) parameterize the minted child tokens. Pushes child-token issuance into the server as a security-isolation primitive.

## Multi-tenancy

### Sub-tenancy via child-credential generation

Server holds the organization-level `TURSO_API_TOKEN` and generates per-database child credentials with bounded scope (read-only or full) and expiration. Provides isolation within a single Turso organization rather than across organizations.

### Single connection per server instance

Single organization per deployment; per-database token permissions provide isolation within that org, but the process is keyed to one `TURSO_ORGANIZATION`.

## Distribution channel

### npm via npx / bunx

Published to npm as `mcp-turso-cloud`. README install: `npx -y mcp-turso-cloud`.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx -y mcp-turso-cloud` with env vars supplied via host config. Compiled `dist/index.js` runs after build.

## Build and packaging

### npm/Node toolchain

`package.json` with `npm run build` for local compile. `dist/index.js` is the compiled output.

## CI

### Renovate / Changeset tooling

`.changeset/` (changelog management) and `renovate.json` (dependency automation) present. Explicit GitHub Actions workflows not confirmed within budget.

## Repository layout

### Single-package with `.changeset/`

Single-package TypeScript project with `.changeset/` and `renovate.json` — changeset-based release management.

## Host integration

### Claude Desktop

JSON config example shown in README.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline JSON config example shown.

### WSL configuration guidance

WSL-specific configuration guidance documented.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT licensed.

### Tagged release with version in changelog

v0.0.2 released March 20, 2025.
