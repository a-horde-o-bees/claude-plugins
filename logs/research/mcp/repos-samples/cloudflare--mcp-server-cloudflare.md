# Sample

Mirrors of `https://github.com/cloudflare/mcp-server-cloudflare`. Cloudflare remote-MCP monorepo — 14 domain Workers (Workers Bindings, Observability, Radar, Browser Rendering, AI Gateway, AutoRAG, Audit Logs, CASB, GraphQL, etc.) deployed on Cloudflare; users point clients at hosted URLs. 3.6k stars; Apache-2.0; default branch `main`; `@repo/mcp-common@0.20.4` released 2026-03-31.

## Server runtime

### TypeScript on Cloudflare Workers (V8 isolate)

TypeScript (90.8% of repo); runs on Cloudflare Workers (V8 isolate runtime), not Node. Internal `@repo/mcp-common` package abstracts shared server scaffolding across the 14 domain Workers; Turbo monorepo orchestrates builds/tests.

## Transport

### Streamable HTTP

Streamable HTTP via `/mcp` endpoint is the primary transport; users connect to `https://<domain>.mcp.cloudflare.com/mcp`.

### SSE (Server-Sent Events)

SSE via `/sse` endpoint, deprecated. Two transport endpoints coexist on the same Worker so clients can migrate at their own pace.

### Stdio-to-HTTP shim on the client side

`mcp-remote` (npm) is the universal client shim — translates host-side stdio into streamable HTTP requests against the Worker URL. The repo itself never speaks stdio; hosts spawn `npx mcp-remote <cloudflare-mcp-url>` and the shim handles auth handshake on the client side.

### Selection mechanism

URL path selects transport on the same Worker: `/mcp` for streamable HTTP, `/sse` for the deprecated SSE path.

## Capability surface

### Domain-bundled tool set

14 domain Workers each expose a tool set scoped to their service: Documentation, Workers Bindings, Workers Builds, Observability, Radar, Container, Browser Rendering, Logpush, AI Gateway, AutoRAG, Audit Logs, DNS Analytics, Digital Experience Monitoring, CASB, GraphQL.

## Configuration delivery

### Hosted endpoint as primary delivery

Server-side configuration is Wrangler config per Worker (`wrangler.toml`/`wrangler.jsonc`) controlling deployment. Client-side config is just the host's JSON snippet pointing at the URL: `{"mcpServers": {"cloudflare-observability": {"command": "npx", "args": ["mcp-remote", "https://observability.mcp.cloudflare.com/mcp"]}}}`. Authentication travels inline per-request.

## Authentication

### Per-request bearer token (provider-scoped)

Cloudflare API tokens with per-service scopes — created via Cloudflare dashboard and passed at auth time. The same Worker serves any account that authenticates; tenancy is determined per-call by which token arrived. OAuth-like flow documented for the hosted endpoints; `mcp-remote` shim negotiates the auth handshake with the Worker.

## Multi-tenancy

### Per-request tenancy by inbound credential / bearer token

Per-request tenancy. Each Worker invocation is scoped by the bearer token → authenticated Cloudflare account. The same Worker serves any account that authenticates.

## Distribution channel

### Hosted endpoint (no install)

Remote-only — all 14 servers run as Cloudflare Workers at public URLs (e.g. `https://observability.mcp.cloudflare.com/mcp`). End users install by pointing `mcp-remote` (npm) at the URL. No local binary, Docker, or npm install of the servers themselves. The repo ships operational Workers, not installable artifacts.

## Entry point and launch

### URL configuration (no local launch)

`npx mcp-remote <cloudflare-mcp-url>` is the host's command shape; the client-side shim bridges stdio (host side) to streamable HTTP (Cloudflare side). No repo-side launcher.

## Build and packaging

### Wrangler bundle (Cloudflare Workers)

Wrangler bundles the TypeScript source per Worker package and deploys directly to Cloudflare's edge. The "package" is the deployed Worker. `@repo/mcp-common@0.20.4` is an internal workspace package; `mcp-remote` is the end-user shim (npm, not published by Cloudflare).

### npm/Node toolchain

Turbo orchestrates monorepo builds; pnpm scripts; ESLint and Prettier in the dev toolchain.

## Test stack

### Vitest (TypeScript / Node)

Vitest across the monorepo.

## CI

### GitHub Actions

GitHub Actions; Turbo orchestrates builds/tests.

### Turbo (build orchestrator)

Turbo monorepo orchestrator drives CI build/test pipeline.

## Deployment topology

### Edge / serverless deployment (Cloudflare Workers, V8 isolate)

Servers run on Cloudflare's edge runtime; deployment artifact is the deployed Worker. No persistent in-memory state, request-scoped execution. The maintainer operates the runtime; users never run server code.

## Container artifacts

### Cloudflare Workers config

Wrangler config per Worker controls deployment. Not container-based.

### No container artifacts

No Dockerfile or container-image distribution — Workers replace containers as the deployment artifact.

## Repository layout

### Turbo + pnpm monorepo

Turbo/pnpm monorepo. 14 domain Workers as individual packages; shared `@repo/mcp-common` package abstracts common server concerns. Mirrors Cloudflare's own platform composition patterns.

## Host integration

### Cursor

Documented integration.

### Claude Desktop

JSON snippet via `mcp-remote`.

### Claude Code

Same JSON snippet pattern applies (not explicitly broken out from Claude Desktop in README).

### Cloudflare AI Playground / OpenAI Responses API / OpenAI Agents SDK

Cloudflare AI Playground first-party integration; OpenAI Responses API documented integration.

## Observability

### Worker logs (platform-native)

Worker logs via Cloudflare dashboard; not a self-hostable logging layer.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

Not observed in fetched view.

## Developer ergonomics

### Sample MCP client configs in repo

README supplies `mcp-remote` JSON snippets for hosts.

## Release and lifecycle

### Active development

3.6k stars; tagged release `@repo/mcp-common@0.20.4` on 2026-03-31.

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.
