# Sample

Mirrors of `https://github.com/neondatabase/mcp-server-neon`. Neon Postgres MCP — hosted remote service model for managing Neon branches/databases. 587 stars, MIT, default branch `main`; actively deployed via Vercel.

## Server runtime

### Next.js (TypeScript) as MCP host

TypeScript (97.5%), JavaScript (2.2%), CSS (0.3%); Node.js v18+ (development v22+); pnpm + Corepack. Next.js App Router as hosting surface; MCP tool/handler logic under `mcp-src/`. The Next.js app bundles the landing page, OAuth UI, and MCP endpoint together.

## Transport

### Streamable HTTP

Primary transport — `/mcp` endpoint serves Streamable HTTP.

### SSE (Server-Sent Events)

Legacy `/sse` endpoint marked deprecated; remains for backward compatibility.

### Hosted remote endpoint (vendor-operated)

Vendor-operated endpoint at `mcp.neon.tech`; clients hit `https://mcp.neon.tech/mcp` rather than running a local process.

### Selection mechanism

Endpoint-URL based — clients hit `/mcp` for streamable HTTP or `/sse` for the legacy transport.

## Capability surface

### Domain-bundled tool set

20+ tools across Projects (create/list/describe/delete), Branches (create/delete/describe/compare schema/reset), SQL (queries/transactions/list-tables/describe-schemas), Migrations (prepare/complete), Optimization (slow-query analysis, query tuning), Auth/Data API provisioning, Discovery (search/docs fetch).

### Read/write tool split

Read-only mode exposes 13 specific tools; full mode exposes the larger 20+ tool surface.

### Scope-based tool filtering via URL param

Tool filtering via `category` query param on the connection URL — granular scope beyond simple read-only.

### Migration prepare/commit pattern

Start/commit migration pattern lets agents prepare migrations for human review before applying.

## Configuration delivery

### URL query parameters on HTTP connection

Per-connection scoping via URL query params — `readonly`, `category` for tool filtering, `projectId` for single-project scoping.

### HTTP request headers

`Authorization` bearer header for API-key auth on each request.

## Authentication

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

OAuth 2.0 with scopes (`read`, `write`, `*`) as the primary auth path — browser-redirect flow, multi-tenant. Supports organization and personal project access via `org_id`/`project_id` in prompts.

### Per-request bearer token (provider-scoped)

API key bearer token as a headless alternative — `Authorization: Bearer <api-key>` header on each request.

## Multi-tenancy

### Per-request tenancy via OAuth token scoping

Per-request tenancy via OAuth token scoping — supports organization and personal project access; remote hosted multi-tenant service serving many users from one runtime.

## Distribution channel

### Hosted endpoint (no install)

Primary delivery is `mcp.neon.tech` as a hosted service — users paste the URL into their host's MCP config; nothing installs locally.

### npm via npx / bunx

`npx neonctl@latest init` for client auto-wiring; npm-distributed for local development.

### Pre-built host installer / one-click install URL

Cursor IDE install button bypasses JSON copy-paste.

## Entry point and launch

### URL configuration (no local launch)

Hosts configure `mcp.neon.tech/mcp` with OAuth — there is no local process to launch.

### Framework CLI run

Local development runs `pnpm dev` (Next.js dev server) for contributors.

## Build and packaging

### npm/Node toolchain

Node ecosystem — `package.json`, pnpm + Corepack for dependency management.

## Container artifacts

### No container artifacts

No Dockerfile; deployment is Vercel-hosted instead of containerized.

### Vercel deployment config

Vercel-hosted deployment with automatic preview environments per PR.

## Test stack

### Pyramid with web E2E (Playwright + ephemeral DB)

Pyramid testing strategy — unit (pure logic), integration (tool contracts), E2E (MCP protocol with real clients), web E2E (Playwright, ephemeral DB). Run via `pnpm run test`.

### End-to-end with browser automation

Playwright drives web E2E tests against an ephemeral database — exercises browser-driven flows alongside the MCP protocol surface.

## CI

### GitHub Actions

GitHub Actions in `.github/`.

### Vercel preview-per-PR + main deploy

Vercel automatic deployment from branches; preview environments per PR.

## Deployment topology

### Hosted SaaS endpoint

Remote-hosted multi-tenant service running on Vercel; users connect to the operator-run endpoint.

## Host integration

### Cursor

Cursor IDE install button.

### VS Code / VS Code Insiders / Visual Studio family

VS Code + GitHub Copilot supported.

### Claude Code

Supported.

### Claude Desktop

Supported.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline and Windsurf supported.

### Zed

Supported.

## Repository layout

### Hosted-service layout (Next.js app + mcp-src + lib)

`landing/` Next.js app with `app/api/` (transport + OAuth endpoints), `mcp-src/` (server/tools/handlers), `lib/` (OAuth/config helpers), `landing/tests/` (test suites), `.claude/skills/` directory.

## Observability

### Pino / Winston structured logging (Node)

Winston-based logging with configurable log levels.

### Sentry integration

Sentry integration for error tracking.

### Env-var-controlled log level

Configurable log levels via configuration.

## Developer ergonomics

### Sample MCP client configs in repo

JSON config examples per host shipped alongside the server.

## Documentation surface

### Per-host README integration sections

Per-host README sections; Cursor install button.

## Claude Code plugin / skill wrapper

### `.claude/skills/` directory in repo

`.claude/skills/` skill definitions checked into the repo — Claude Code skill wiring rather than a plugin manifest. Aligns the MCP server with Claude Code skill workflows.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.

### Active development

Active development — actively deployed via Vercel; preview environments per PR.
