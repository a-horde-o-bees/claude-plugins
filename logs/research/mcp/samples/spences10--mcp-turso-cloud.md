# Sample

## Identification

### url

https://github.com/spences10/mcp-turso-cloud

### stars

15

### last-commit

v0.0.2 released March 20, 2025.

### license

MIT

### default branch

main

### one-line purpose

Turso (libsql) cloud MCP server — community-canonical (not under `tursodatabase/*`).

## 1. Language and runtime

### language(s) + version constraints

TypeScript (92.4%), JavaScript (7.6%); Node.js (version not stated).

### framework/SDK in use

Anthropic MCP TypeScript SDK; libSQL client for Turso.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (standard for npx-launched servers; not called out in README, inferred from consumption pattern).

### how selected

Implicit — only stdio via npx.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

npm (via npx).

### published package name(s)

`mcp-turso-cloud`.

### install commands shown in README

`npx -y mcp-turso-cloud`.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`npx -y mcp-turso-cloud` with env vars.

### wrapper scripts, launchers, stubs

Compiled `dist/index.js`; `npm run build` for local compile.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Env vars only — `TURSO_API_TOKEN` (required), `TURSO_ORGANIZATION` (required), `TURSO_DEFAULT_DATABASE` (optional), `TOKEN_EXPIRATION` (default 7 days), `TOKEN_PERMISSION` (default full-access).

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Two-tier — org-level API token generates database-specific tokens automatically with configurable permission granularity.

### where credentials come from

Environment variables supplied by host configuration.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

Single organization per deployment; per-database token permissions provide isolation within that org.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools split into org operations (list/create/delete databases, token generation) and database operations (list tables, `execute_read_only_query`, `execute_query` (destructive), schema inspection, vector similarity search). No resources/prompts/sampling/roots documented.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Not documented.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON config example.

### Cline

JSON config example.

### WSL

Configuration guidance.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

Not documented; no test framework visible in content fetched.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

`.changeset/` (for changelog management) and `renovate.json` (dependency automation) present; explicit GitHub Actions workflows not confirmed within budget.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

None observed.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

MCP client JSON config examples (Claude Desktop, Cline, WSL).

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single-package TypeScript project with `.changeset/` and `renovate.json`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Explicit tool split between `execute_read_only_query` (SELECT/PRAGMA) and `execute_query` (DML/DDL) supports different approval workflows at the MCP-client layer. Automatic database-token generation from org token delegates short-lived-credential creation into the server. Vector similarity search exposed as first-class tool.

## 18. Unanticipated axes observed

`TOKEN_EXPIRATION` and `TOKEN_PERMISSION` promote short-lived child-token generation as a security primitive, uncommon among DB MCP servers.

## 20. Gaps

Transport never explicitly named in README — inferred stdio. Tests and CI details not confirmed. No container artifacts observed. Ownership/canonicality relative to Turso's corp repo not established within budget.
