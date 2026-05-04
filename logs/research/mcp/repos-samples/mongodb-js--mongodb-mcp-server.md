# Sample

Mirrors of `https://github.com/mongodb-js/mongodb-mcp-server`. MongoDB MCP server — wraps ~60 tools across DB ops, metadata, DDL, Atlas management, Atlas Stream Processing, and an Assistant KB search. ~1000 stars, Apache-2.0, default branch `main`, last commit v1.10.0 released April 20, 2026.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (98.6%) on Anthropic's MCP TypeScript SDK; Node.js `>=20.19.0` or `22.12.0+` or `23+`. Uses an internal argument parser rather than a third-party CLI library.

## Transport

### stdio

Default transport.

### Streamable HTTP

HTTP mode with JSON response mode supported. Bound via `HTTP_HOST`, `HTTP_PORT` env vars.

### SSE (Server-Sent Events)

HTTP mode also supports SSE response mode.

### Selection mechanism

`TRANSPORT` env var or `--transport` flag selects stdio vs HTTP at startup.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

~60 tools spanning DB ops (find/aggregate/insert/update/delete/explain), metadata (list-databases/collections, schema, indexes), DDL (create/drop collection/db/index), Atlas management (clusters, projects, users, access lists, alerts), Atlas Stream Processing, and an Assistant KB search.

### Tools plus resources

Resources include `config://config` (redacted), `debug://mongodb` (diagnostics), and `exported-data://{name}` (temporary exports). No prompts/sampling/roots.

### Capability gating flags (per-tool, per-category, write-mode)

`--readOnly` disables mutating tool surface. `DISABLED_TOOLS` env var also lets operators trim individual tools out of the catalog.

### Destructive-tool elicitation list

`CONFIRMATION_REQUIRED_TOOLS` lists tools (e.g., drop-database) that trigger MCP elicitation before destructive execution.

## Configuration delivery

### Environment variables

Env vars prefixed `MDB_MCP_` — `CONNECTION_STRING`, `API_CLIENT_ID`, `READ_ONLY`, `DISABLED_TOOLS`, `LOGGERS`, etc.

### CLI flags

camelCase CLI args — `--readOnly`, `--apiClientId`, `--indexCheck`, `--dryRun`, `--allowRequestOverrides`.

### Sidecar config files (JSON / YAML / TOML / EDN)

JSON config file referenced by `MDB_MCP_CONFIG` env var as a third configuration source alongside env and CLI.

### HTTP request headers

`--allowRequestOverrides=true` lets per-request headers and query params override server-wide config — powerful for HTTP multi-client setups.

## Authentication

### Database connection string

Direct DB access via MongoDB connection string in `MDB_MCP_CONNECTION_STRING`.

### Service-account credential pair to cloud API

Atlas Service Account using Client ID / Client Secret (`API_CLIENT_ID`, etc.) for Atlas API calls; IP allowlist required for the API credentials.

## Multi-tenancy

### Single-user / single-tenant per process

Single credential set per server instance.

### Externally-managed sessions via header

HTTP transport supports externally-managed session IDs via the `mcp-session-id` header when `EXTERNALLY_MANAGED_SESSIONS=true` — per-session, not per-tenant.

## Distribution channel

### npm via npx / bunx

Published as `mongodb-mcp-server` on npm; install via `npx -y mongodb-mcp-server@latest`.

### Docker / OCI image

Published Docker image at `mongodb/mongodb-mcp-server:latest`.

## Entry point and launch

### Console script via `[project.scripts]` / npm bin

`mongodb-mcp-server` registered as the npm bin; users run it directly after install.

### `npx -y <package>` / `bunx`

`npx -y mongodb-mcp-server@latest` with flags is the documented launch command.

### Docker container entrypoint

Docker image entrypoint launches the server inside a container.

## Build and packaging

### npm/Node toolchain

Node ecosystem build — `package.json` plus TypeScript build step that produces a published npm package.

## Container artifacts

### Multi-stage Dockerfile

Multi-stage Dockerfile in repo. `deploy/` directory holds Azure deployment guides.

### Azure deployment artifacts

`deploy/` directory with Azure deployment guides for hosting the server on Azure.

## Test stack

### Vitest (TypeScript / Node)

Vitest configured via `vitest.config.ts`; tests live under `/tests`.

## CI

### GitHub Actions

`.github/` directory present; specific workflow contents not extracted within budget.

## Host integration

### VS Code / VS Code Insiders / Visual Studio family

Install badges provided for VS Code (Insiders).

### Cursor

Install badges provided.

### Claude Desktop

Config examples provided.

### Codex CLI / Copilot CLI / Gemini CLI

Copilot CLI supported via documented config.

### Per-host README JSON snippets

Per-host README sections; OpenCode also documented.

## Repository layout

### Single-package with auxiliary folders

Single-package layout with auxiliary folders — `src`, `tests`, `deploy`, `scripts`, `resources`, `eslint-rules`, `api-extractor`.

## Safety and security posture

### Read-only by default with explicit write flag

`--readOnly` flag disables the mutating tool surface so operators can run the server with no write surface exposed.

### Destructive-tool elicitation list

`CONFIRMATION_REQUIRED_TOOLS` triggers MCP elicitation for destructive tools like drop-database before they execute.

### Index-scan rejection

`--indexCheck` rejects queries that would trigger collection scans — an unusual safety posture that gates an entire query class on index availability.

### Temporary-user lifecycle with TTL

Temporary auto-generated DB users with configurable TTL (default 4h) instead of long-lived DB credentials.

### Dry-run config dump

`--dryRun` dumps resolved config and exits without booting the server.

## Domain logic and embedded intelligence

### Embedded RAG / retrieval pipeline

Assistant/KB search tools embed MongoDB documentation retrieval into the same server, alongside the DB and Atlas tool surface.

## Caching and rate-limiting infrastructure

### Auto-cleanup of temporary export artifacts

Export-artifact resource (`exported-data://{name}`) with auto-cleanup (default 5 min) so temporary exports do not accumulate.

## Observability

### Pluggable logger sinks

Pluggable `LOGGERS` config — `disk` (default `~/.mongodb/mongodb-mcp/.app-logs`), `mcp` (to client), `stderr`. Multiple sinks can be combined.

### Env-var-controlled log level

`MCP_CLIENT_LOG_LEVEL` controls severity (default `debug`).

### Health endpoint

Optional monitoring-server health endpoint, available only in HTTP transport mode — surfaces as a separable sidecar.

## Developer ergonomics

### Linter and type-checker stack

Custom `eslint-rules/` shipped in repo suggest codebase-scale lint discipline. `api-extractor/` for API docs.

### `scripts/` directory

`scripts/` utilities folder for repo-internal tooling.

## Documentation surface

### Per-host README integration sections

Install badges and per-host config examples for multiple hosts (VS Code Insiders, Cursor, Claude Desktop, Copilot CLI, OpenCode).

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin/` or `.claude/skills/` wrapper present — standard MCP server.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Tagged release with version in changelog

v1.10.0 released April 20, 2026; semver-tagged releases.

### Active development

Ongoing development with recent v1.10.0 release.
