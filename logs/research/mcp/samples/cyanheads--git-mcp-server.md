# Sample

## Identification

### url

https://github.com/cyanheads/git-mcp-server

### stars

207

### last-commit

April 19, 2026

### license

Apache-2.0

### default branch

main

### one-line purpose

Git MCP server (TypeScript) — 28 tools across repo/commits/branches/remotes; dual Node+Bun runtime with base-directory sandboxing for multi-tenant usage.

## 1. Language and runtime

### language(s) + version constraints

TypeScript ^6.0.3; Node.js >=20.0.0, Bun >=1.2.0.

### framework/SDK in use

MCP SDK ^1.29.0, Hono (HTTP), Pino (logging), tsyringe (DI), Zod (validation), OpenTelemetry (optional).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

STDIO, Streamable HTTP (configurable port 3015, hostname).

### how selected

environment config selection.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

npm (`npx @cyanheads/git-mcp-server@latest`), Bun (`bunx @cyanheads/git-mcp-server@latest`).

### published package name(s)

`@cyanheads/git-mcp-server`.

### install commands shown in README

`npx @cyanheads/git-mcp-server@latest` or `bunx @cyanheads/git-mcp-server@latest`.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

npx or bunx invocation; also `npm run start:stdio`, `npm run start:http`.

### wrapper scripts, launchers, stubs

npm scripts for stdio vs HTTP startup modes.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

Zod-validated env vars: transport type, session mode, response format, Git identity, base-dir restriction, GPG/SSH commit signing, auth mode, logging level.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

three modes — `none` (default), `jwt` (32+ char secret), `oauth` (OIDC provider).

### where credentials come from

env vars or request headers.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

workspace-keyed via base-directory restriction; per-session working-directory management.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

28 tools across 7 categories (repo management, staging/commits, history inspection, analysis, branching/merging, remote ops, advanced workflows); 1 resource (repo metadata); 1 prompt.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

structured via Pino; request context tracking for auditing; optional OpenTelemetry for traces/metrics; log level configurable.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Cline

MCP client configs (e.g., `cline_mcp_settings.json`) documented.

### Cloudflare Workers

deployment pipeline.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not present.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

present; Bun test runner with Vitest compatibility; coverage reports.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

present; `npm run devcheck` (lint, format, typecheck); dependency audit; unit + integration test suite.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present (implied by Bun build); no docker-compose found.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

MCP client configuration examples; dev mode with file watching; session-specific working-directory management.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package, organized by concern: `src/` (tools/, resources/, transports/, services/, storage/, config/, utils/, container/), `tests/` mirrored structure; config files: `package.json`, `tsconfig.json`, `.env.example`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Dual runtime support (Node 20+, Bun 1.2+) with auto-detection. Structured logging with request context for audit trails. Optional OTel instrumentation for observability. Dependency injection (tsyringe) for testable design. Multi-tenant sandboxing via base-directory constraints.

## 18. Unanticipated axes observed

Runtime auto-detection between Node and Bun — axis: multi-runtime support. Multi-tenant sandboxing via base-directory restriction — axis: workspace isolation in a stdio server. Session-based working-directory isolation.

## 20. Gaps

Exact last-commit details (only date). Full CI pipeline details not visible in README. OTel configuration examples not provided.
