# Sample

## Identification

### url

https://github.com/mongodb-js/mongodb-mcp-server

### stars

~1000

### last-commit

v1.10.0 released April 20, 2026

### license

Apache-2.0

### default branch

main

### one-line purpose

MongoDB MCP server — MongoDB collection/document operations.

## Language and runtime

### language(s) + version constraints

TypeScript (98.6%); Node.js `>=20.19.0` or `22.12.0+` or `23+`.

### framework/SDK in use

Anthropic MCP TypeScript SDK; internal argument parser.

## Transport

### supported transports

stdio (default), HTTP with SSE or JSON response modes.

### how selected

`TRANSPORT` env var / `--transport` flag; `HTTP_HOST`, `HTTP_PORT` for HTTP-mode binding.

## Distribution

### every mechanism observed

npm, npx, Docker image (`mongodb/mongodb-mcp-server:latest`).

### published package name(s)

`mongodb-mcp-server`

### install commands shown in README

`npx -y mongodb-mcp-server@latest`; Docker pull.

## Entry point / launch

### command(s) users/hosts run

`mongodb-mcp-server` (npm bin) or `npx -y mongodb-mcp-server@latest` with flags.

### wrapper scripts, launchers, stubs

Dockerfile for containerized launch; `deploy/` directory for Azure deployment.

## Configuration surface

### how config reaches the server

Three sources — env vars prefixed `MDB_MCP_` (e.g., `CONNECTION_STRING`, `API_CLIENT_ID`, `READ_ONLY`, `DISABLED_TOOLS`, `LOGGERS`); camelCase CLI args (e.g., `--readOnly`, `--apiClientId`); JSON config file loaded via `MDB_MCP_CONFIG` env var.

## Authentication

### flow

MongoDB connection string (direct DB) or Atlas Service Account (Client ID/Secret) for Atlas API; IP allowlist required for API credentials; temporary auto-generated DB users with configurable TTL (default 4h).

### where credentials come from

Environment variables, CLI args, or JSON config.

## Multi-tenancy

### tenancy model

Single credential set per instance; HTTP transport supports externally-managed session IDs via `mcp-session-id` header when `EXTERNALLY_MANAGED_SESSIONS=true` — per-session, not per-tenant.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

~60 tools spanning DB ops (find/aggregate/insert/update/delete/explain), metadata (list-databases/collections, schema, indexes), DDL (create/drop collection/db/index), Atlas management (clusters, projects, users, access lists, alerts), Atlas Stream Processing, and an Assistant KB search. Resources: `config://config` (redacted), `debug://mongodb` (diagnostics), `exported-data://{name}` (temporary exports). No prompts/sampling/roots.

## Observability

### logging destination + format, metrics, tracing, debug flags

Pluggable `LOGGERS` — `disk` (default `~/.mongodb/mongodb-mcp/.app-logs`), `mcp` (to client), `stderr`. `MCP_CLIENT_LOG_LEVEL` controls severity (default `debug`). Optional monitoring-server health endpoint (HTTP transport only).

## Host integrations shown in README or repo

### VS Code (Insiders)

Install badges provided.

### Cursor

Install badges provided.

### Claude Desktop

Config examples provided.

### Copilot CLI

Supported.

### OpenCode

Supported.

## Claude Code plugin wrapper

### presence and shape

Not present.

## Tests

### presence, framework, location, notable patterns

Vitest (`vitest.config.ts`); tests under `/tests`.

## CI

### presence, system, triggers, what it runs

GitHub Actions in `.github/`; specific workflow contents not extracted within budget.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Multi-stage Dockerfile; `deploy/` with Azure guides.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`eslint-rules/` custom lint, `api-extractor/` for API docs, `scripts/` utilities, install badges for multiple hosts.

## Repo layout

### single-package / monorepo / vendored / other

Single-package with auxiliary folders (`src`, `tests`, `deploy`, `scripts`, `resources`, `eslint-rules`, `api-extractor`).

## Notable structural choices

`--readOnly` disables mutating tool surface. `--indexCheck` rejects collection scans — an unusual safety posture. Tool-confirmation list (`CONFIRMATION_REQUIRED_TOOLS`) triggers MCP elicitation for destructive tools like drop-database. `--dryRun` dumps resolved config and exits without booting server. `--allowRequestOverrides=true` lets per-request headers/query params override config — powerful for HTTP multi-client setups. Temporary-user lifecycle with TTL instead of long-lived DB credentials. Export-artifact resource with auto-cleanup (default 5 min).

## Unanticipated axes observed

Assistant/KB search tools embed MongoDB documentation retrieval into the same server. Custom eslint rules shipped in repo suggest codebase-scale discipline. Monitoring server as a separable sidecar for HTTP mode.

## Gaps

Exact CI workflow triggers not extracted within budget. Specific Atlas Stream Processing tool surface not enumerated.
