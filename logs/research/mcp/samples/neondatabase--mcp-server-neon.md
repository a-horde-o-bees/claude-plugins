# Sample

## Identification
- url: https://github.com/neondatabase/mcp-server-neon
- stars: 587
- last-commit (date or relative): Not surfaced directly; repo is actively deployed via Vercel
- license: MIT
- default branch: main
- one-line purpose: Neon Postgres MCP — hosted remote service model for managing Neon branches/databases.

## 1. Language and runtime
- language(s) + version constraints: TypeScript (97.5%), JavaScript (2.2%), CSS (0.3%); Node.js v18+ (development v22+); pnpm + Corepack
- framework/SDK in use: Next.js App Router as hosting surface; MCP tool/handler logic under `mcp-src/`
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: Streamable HTTP (primary, `/mcp` endpoint), Server-Sent Events (`/sse`, deprecated/legacy)
- how selected (flag, env, separate entry, auto-detect, etc.): Endpoint-URL based — clients hit `/mcp` for streamable HTTP or `/sse` for legacy transport
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: Remote-hosted server at `mcp.neon.tech` (primary); npm/`npx` for local server; `npx neonctl@latest init` for client auto-wiring; Cursor IDE install button
- published package name(s): Distributed primarily as a hosted service; npm package referenced for local development
- install commands shown in README: `npx neonctl@latest init`; manual JSON config pointing at `https://mcp.neon.tech/mcp`
- pitfalls observed:
  - Exact npm package name/version not extracted within budget

## 4. Entry point / launch
- command(s) users/hosts run: Remote — hosts configure `mcp.neon.tech/mcp` with OAuth; local — Next.js dev server (`pnpm dev`)
- wrapper scripts, launchers, stubs: Vercel deployment pipeline; `.claude/skills/` skill definitions present in repo
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: URL query params (`readonly`, `category` for tool filtering, `projectId` for single-project scoping); Authorization bearer header for API-key auth
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: OAuth 2.0 with scopes (`read`, `write`, `*`) as primary; API key bearer token as headless alternative
- where credentials come from: Browser OAuth redirect or `Authorization: Bearer <api-key>` header
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Per-request tenancy via OAuth token scoping — supports organization and personal project access via `org_id`/`project_id` in prompts; remote hosted multi-tenant service
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 20+ tools — Projects (create/list/describe/delete), Branches (create/delete/describe/compare schema/reset), SQL (queries/transactions/list-tables/describe-schemas), Migrations (prepare/complete), Optimization (slow-query analysis, query tuning), Auth/Data API provisioning, Discovery (search/docs fetch). Read-only mode exposes 13 specific tools.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Winston-based logging with configurable levels; Sentry integration; analytics integration
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Cursor IDE: Install button
- VS Code + GitHub Copilot: Supported
- Claude Code / Claude Desktop: Supported
- Cline, Windsurf, Zed: Supported
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

`.claude/skills/` skill definitions present in the repo — Claude Code skill wiring rather than a plugin manifest

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Pyramid — unit (pure logic), integration (tool contracts), E2E (MCP protocol with real clients), web E2E (Playwright, ephemeral DB). `pnpm run test`
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions in `.github/`; Vercel automatic deployment from branches; preview environments per PR
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: None observed — Vercel-hosted deployment model
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: JSON config examples per host; `.claude/skills/` definitions; Cursor install button
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: `landing/` Next.js app with `app/api/` transport + OAuth endpoints, `mcp-src/` server/tools/handlers, `lib/` OAuth/config helpers, `landing/tests/` test suites, `.claude/skills/`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Remote-first hosted MCP server rather than local-process default — OAuth flow is primary auth
- Tool filtering via `category` query param — granular scope beyond simple read-only
- Start/commit migration pattern lets agents prepare migrations for human review before applying
- Project-scoped mode pins all operations to a single project via URL param
- Next.js chosen over a plain Node server — bundles landing page, OAuth UI, and MCP endpoint together

## 18. Unanticipated axes observed
- `.claude/skills/` checked in to the repo — aligns MCP server with Claude Code skill workflows
- Playwright-driven web E2E against ephemeral database — contrasts with most MCP servers that test only in unit/integration
- Scope-based tool filtering via URL param is a notable alternative to env-var tool lists

## 20. Gaps
- Last commit date not surfaced from landing page
- Exact npm package name/version not extracted within budget
- Specific Sentry/analytics configuration not surfaced
