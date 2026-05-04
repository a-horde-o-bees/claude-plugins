# Sample

Mirrors of `https://github.com/ahmedmustahid/postgres-mcp-server`. PostgreSQL read-only MCP server — exposes tables and schema as resources and runs read-only SQL queries over stdio or Streamable HTTP. 30 stars, MIT, default branch `main`.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript/JavaScript server (TS 71.8% in the repo) on the Anthropic MCP TypeScript SDK — uses `StreamableHTTPServerTransport` and `StdioServerTransport` classes from the SDK. A sibling `pyproject.toml` is also present in this TS-majority repo, suggesting a secondary Python surface (purpose not explained in README).

## Transport

### stdio

stdio supported; selected by passing `stdio` as a positional subcommand (`npx @ahmedmustahid/postgres-mcp-server stdio`).

### Streamable HTTP

HTTP (streamable) supported and is the default mode. Bound to a configurable port (default 3000). Supports stateful sessions but not per-request tenant switching.

### Selection mechanism

Subcommand verb — positional `stdio` argument selects stdio mode; absence selects HTTP default.

## Capability surface

### Tools plus resources

Resources — "Database Tables" (public-schema listing), "Database Schema" (column info as queryable URIs). Tool — read-only SQL query execution. Splits read access along MCP primitive lines.

## Configuration delivery

### Environment variables

`POSTGRES_USERNAME`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DATABASE`, `POSTGRES_URL`, `PORT` (default 3000), `HOST`, `NODE_ENV`, `CORS_ORIGIN`.

### Dotenv file

`.env` is the documented configuration delivery surface — env vars loaded from `.env` at startup.

### Connection URI scheme

`POSTGRES_URL` accepted as a single-string URI alongside discrete `POSTGRES_USERNAME`/`POSTGRES_PASSWORD`/`POSTGRES_HOST`/`POSTGRES_DATABASE` flags — convenience for the standard PostgreSQL URI idiom.

## Authentication

### Database connection string

Standard PostgreSQL authentication via credentials in env vars (`POSTGRES_*`) or as a connection URI.

## Multi-tenancy

### HTTP-stateful, single-tenant

Single database per server instance; HTTP transport supports stateful sessions but not per-request tenant switching.

## Distribution channel

### npm via npx / bunx

Published as `@ahmedmustahid/postgres-mcp-server` on npm; canonical invocation `npx @ahmedmustahid/postgres-mcp-server [stdio]`.

### Docker / OCI image

Dockerfile and `docker-compose.yml` present; Podman explicitly called out as an alternative.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx @ahmedmustahid/postgres-mcp-server` (HTTP default) or `npx @ahmedmustahid/postgres-mcp-server stdio` (stdio).

### Subcommand verb

Positional `stdio` subcommand selects transport mode at launch.

## Build and packaging

### npm/Node toolchain

`package.json` defines build/bin entries; npm registry is the publish target.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile at repo root.

### Docker Compose for local dev

`docker-compose.yml` orchestrates the server alongside its backing PostgreSQL service for local development.

## Observability

### `--verbose` flag

Boolean `--verbose` CLI flag.

## Host integration

### Claude Desktop

JSON config example included.

### Inspector compatibility called out

MCP Inspector explicitly referenced.

## Example client / developer ergonomics

### Makefile / Makefile.toml

Makefile present at repo root.

### Sample MCP client configs in repo

Claude Desktop config example shipped in README; "Show sales table from last year" example query as user-facing onboarding.

## Repository layout

### Single-package source (language-conventional)

Primarily Node/TS layout (`src/`, `package.json`) with sibling `pyproject.toml` and `images/` directory — mixed-language surfacing in a TS-majority repo.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
