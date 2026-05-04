# Sample

Mirrors of `https://github.com/supabase-community/supabase-mcp`. Supabase MCP server — HTTP-only transport with OAuth 2.1, managed-cloud endpoint as primary distribution. 2.6k stars, Apache-2.0, default branch `main`. v0.7.0 released March 2, 2026. URL-query-parameter configuration surface and feature-grouped tool gating distinguish it from the stdio+env-var norm.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript 99.5% on Node.js. Anthropic MCP TypeScript SDK + Supabase JS/management SDKs.

## Transport

### Streamable HTTP

HTTP is the canonical mode — primary streaming HTTP MCP endpoint. Managed endpoint: `https://mcp.supabase.com/mcp`. Local: `http://localhost:54321/mcp` (via Supabase CLI). Self-hosted supported. No stdio path documented.

### Selection mechanism

Implicit single mode — HTTP-only deployment. Configuration via URL query parameters rather than CLI flags or env vars.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Tools grouped by feature category: account management (projects, organizations); documentation search; database operations (SQL, migrations, schema); debugging (logs, advisors); development (URLs, API keys, TypeScript generation); Edge Functions (list, deploy); branching (experimental, paid-plan feature); storage (disabled by default).

### Capability gating flags (per-tool, per-category, write-mode)

`features` URL parameter enables/disables tool groups for granular surface control. `read_only` URL parameter restricts to read-only operations. Storage tools disabled by default (conservative posture on file-management powers); branching gated by paid-plan tier.

## Configuration delivery

### URL query parameters on HTTP connection

Three-axis pattern: `project_ref` (scope to a specific Supabase project), `read_only` (restrict to read-only operations), `features` (enable/disable tool groups). Query params fit HTTP transport naturally and embed scope, mode, and feature-toggle into the endpoint itself rather than into env vars or CLI flags.

## Authentication

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

OAuth 2.1 — automatic prompt during client setup. Browser-based OAuth consent; tokens managed by MCP client/host. Hosts with native MCP OAuth support handle the flow transparently.

## Multi-tenancy

### Per-request tenant via URL parameter

Workspace/project-keyed via `project_ref` URL parameter — one deployment serves arbitrarily many Supabase projects. OAuth identity × project_ref combination defines the tenant boundary per session.

### Per-user / per-workspace via OAuth

OAuth identity tied to a real upstream Supabase user account; each request executes under that user's permissions in the upstream system.

## Distribution channel

### npm via npx / bunx

Self-host via npm: `@supabase/mcp-server-supabase` package.

### Hosted endpoint (no install)

For cloud usage clients just point to `https://mcp.supabase.com/mcp` — no install required.

### Vendor-bundled (CLI subcommand)

Supabase CLI bundled variant — `supabase start` exposes a local MCP endpoint at `http://localhost:54321/mcp`. Distribution piggybacks on existing Supabase CLI adoption.

## Entry point and launch

### URL configuration (no local launch)

Cloud: configure MCP client to hit `https://mcp.supabase.com/mcp?project_ref=...`. URL-configuration driven rather than CLI-flag driven.

### `npx -y <package>` / `bunx`

Self-hosted launch via npm package; details not fully extracted within budget.

## CI

### GitHub Actions

`.github/workflows` present; 32 releases on GitHub Releases.

## Container artifacts

### No container artifacts

No Dockerfile in main repo. Self-hosted Supabase deployment documented separately. Managed cloud endpoint reduces need for containerization.

## Host integration

### Cursor

Listed as a supported host.

### Claude Desktop

Listed as a supported host.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Windsurf listed as a supported host.

### Vercel AI SDK native integration

Native MCP client integration via `createToolSchemas()` SDK export — first-class non-Claude integration. Doubles the repo as both an MCP server and an SDK; consumers can use Supabase's schema definitions without routing through MCP.

## Repository layout

### Monorepo with multiple published packages

Monorepo: `/packages` (core packages), `/docs`, `/supabase` (Supabase config), `.github/workflows`, `mise.toml`, `pnpm-workspace.yaml`. pnpm-managed.

## Safety and security posture

### Read-only by default with explicit write flag

`read_only` URL parameter as the gating mechanism for write operations.

### Lockdown / content-filter mode

Prompt-injection mitigation — SQL results are wrapped with anti-injection instructions so LLMs resist following commands in returned data.

## Deployment topology

### Hosted SaaS endpoint

Managed-cloud-first — Supabase operates `https://mcp.supabase.com/mcp` as a hosted MCP service. Primary deployment topology. Self-hosted HTTP server supported as alternative.

### Self-hosted HTTP server

Self-host via npm package; same code as the SaaS variant.

## Developer ergonomics

### Devcontainer / mise / dev-environment manifests

`mise.toml` for dev environment.

### Programmatic embedding API

`createToolSchemas()` SDK export lets Vercel-AI-SDK consumers use Supabase's tool schemas with TypeScript type inference, without routing through the MCP transport.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0 licensed.

### Active development

v0.7.0 released March 2, 2026; 32 releases on GitHub.

### Tagged release with version in changelog

Standard semver-tagged releases.
