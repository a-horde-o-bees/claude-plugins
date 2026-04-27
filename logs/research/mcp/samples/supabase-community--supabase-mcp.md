# Sample

## Identification

### url

https://github.com/supabase-community/supabase-mcp

### stars

2.6k

### last-commit

v0.7.0, March 2, 2026

### license

Apache-2.0

### default branch

main

### one-line purpose

Supabase MCP server — HTTP-only transport with OAuth 2.1.

## Language and runtime

### language(s) + version constraints

TypeScript (99.5%); Node.js runtime.

### framework/SDK in use

Model Context Protocol TypeScript SDK; Supabase JS/management SDKs.

## Transport

### supported transports

HTTP (primary — streaming HTTP MCP endpoint).

### how selected

HTTP is the canonical mode. Managed endpoint: `https://mcp.supabase.com/mcp`. Local: `http://localhost:54321/mcp` (via Supabase CLI). Self-hosted supported. Configuration via URL query parameters rather than CLI flags.

## Distribution

### every mechanism observed

npm package; managed HTTP endpoint (no install required for cloud usage); Supabase CLI bundled variant.

### published package name(s)

`@supabase/mcp-server-supabase`

### install commands shown in README

For self-host via npm; for cloud usage, clients just point to the HTTPS URL.

## Entry point / launch

### command(s) users/hosts run

Cloud: configure MCP client to hit `https://mcp.supabase.com/mcp?project_ref=...`. Local: rely on `supabase start` to expose `http://localhost:54321/mcp`. Self-host: npm package launch (details not fully extracted).

### wrapper scripts, launchers, stubs

URL-configuration driven rather than CLI-flag driven.

## Configuration surface

### how config reaches the server

URL query parameters — `project_ref` (scope to a specific Supabase project), `read_only` (restrict to read-only operations), `features` (enable/disable tool groups).

## Authentication

### flow

OAuth 2.1 — automatic prompt during client setup.

### where credentials come from

Browser-based OAuth consent; tokens managed by MCP client/host.

## Multi-tenancy

### tenancy model

Workspace/project-keyed — `project_ref` URL parameter scopes each connection. OAuth identity × project ref combination defines the tenant boundary per session.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools grouped by feature category: 1) Account management (projects, organizations); 2) Documentation search; 3) Database operations (SQL, migrations, schema); 4) Debugging (logs, advisors); 5) Development (URLs, API keys, TypeScript generation); 6) Edge Functions (list, deploy); 7) Branching (experimental, paid-plan feature); 8) Storage (disabled by default).

## Observability

### logging destination + format, metrics, tracing, debug flags

Not explicitly extracted within budget.

## Host integrations shown in README or repo

### Cursor

Listed as a supported host.

### Claude

Listed as a supported host.

### Windsurf

Listed as a supported host.

### Vercel AI SDK

Native MCP client integration via `createToolSchemas()` export.

## Claude Code plugin wrapper

### presence and shape

Not explicitly observed; "Claude" is referenced as a host but wrapper layout not extracted.

## Tests

### presence, framework, location, notable patterns

Not fully extracted — biome.json config implies linting toolchain; specific test framework not identified in extracted content.

## CI

### presence, system, triggers, what it runs

GitHub Actions `.github/workflows` present; 32 releases on GitHub Releases.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

No Dockerfile in main repo; self-hosted Supabase deployment documented separately. Managed cloud endpoint reduces need for containerization.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`mise.toml` for dev environment; `createToolSchemas()` SDK export for Vercel AI SDK integration with TypeScript type inference.

## Repo layout

### single-package / monorepo / vendored / other

Monorepo — `/packages` (core packages), `/docs`, `/supabase` (Supabase config), `.github/workflows`, `mise.toml`, `pnpm-workspace.yaml`, pnpm-managed.

## Notable structural choices

HTTP-first, managed-cloud-first — defaults to a hosted endpoint rather than local stdio process. Users can run locally or self-host but the primary path is cloud-managed.

OAuth 2.1 rather than static API key — reflects Supabase's identity model; automatic consent prompt in client setup avoids manual token handling.

URL query parameters as config surface — unusual for MCP; most servers use env vars or CLI flags. Query params fit HTTP transport naturally and embed scope (project, read-only, features) into the endpoint itself.

Prompt-injection mitigation — SQL results are wrapped with anti-injection instructions so LLMs resist following commands in returned data.

Feature-grouped tools with granular enable/disable via `features` param — reduces tool surface exposure per deployment.

Storage tools disabled by default — conservative posture on file-management powers.

Vercel AI SDK native hook via exported tool schemas — first-class non-Claude integration, rare among MCPs surveyed.

Branching as paid/experimental — explicit plan-tier gating surfaced through tool groups.

## Unanticipated axes observed

Managed-MCP-as-a-service model — Supabase offers the MCP endpoint as part of their cloud product; this is a different distribution stance from stdio-only servers. Structural reference for any vendor with existing SaaS infrastructure.

OAuth 2.1 suggests the MCP protocol's auth story is maturing past static keys; Supabase is an early adopter.

`createToolSchemas()` export doubles the repo as an SDK — consumers can use Supabase's schema definitions without routing through MCP, a composability choice.

## Gaps

Self-hosted launch command and entry point not fully extracted. Exact test framework not identified. Last commit beyond v0.7.0 release date not confirmed. Dockerfile absence is explicit; container strategy relies on Supabase's own infra.
