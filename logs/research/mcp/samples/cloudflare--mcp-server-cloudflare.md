# Sample

## Identification

### url

https://github.com/cloudflare/mcp-server-cloudflare

### stars

3.6k

### last-commit

`@repo/mcp-common@0.20.4` released 2026-03-31

### license

Apache-2.0

### default branch

main

### one-line purpose

Cloudflare remote-MCP monorepo — 14 domain Workers (Workers Bindings, Observability, Radar, Browser Rendering, AI Gateway, AutoRAG, Audit Logs, CASB, GraphQL, etc.) deployed on Cloudflare; users point clients at hosted URLs.

## Language and runtime

### language(s) + version constraints

TypeScript (90.8%). Runs on Cloudflare Workers (V8 isolate runtime), not Node.

### framework/SDK in use

Cloudflare Workers stack; Turbo monorepo; internal `@repo/mcp-common` package abstracts shared server scaffolding.

## Transport

### supported transports

Streamable HTTP via `/mcp` endpoint (primary); SSE via `/sse` endpoint (deprecated).

### how selected

URL path — the path (`/mcp` vs `/sse`) selects the transport on the same Worker.

## Distribution

### every mechanism observed

Remote-only — all 14 servers run as Cloudflare Workers at public URLs (e.g. `https://observability.mcp.cloudflare.com/mcp`). End users install by pointing `mcp-remote` (npm) at the URL. No local binary, Docker, or npm install of the servers themselves.

### published package name(s)

`mcp-remote` is the end-user shim (npm, not published by Cloudflare). `@repo/mcp-common@0.20.4` is an internal workspace package.

### install commands shown in README

```json
{"mcpServers": {"cloudflare-observability": {"command": "npx", "args": ["mcp-remote", "https://observability.mcp.cloudflare.com/mcp"]}}}
```

## Entry point / launch

### command(s) users/hosts run

`npx mcp-remote <cloudflare-mcp-url>` — the client shim bridges stdio (host side) to streamable-HTTP (Cloudflare side).

### wrapper scripts, launchers, stubs

`mcp-remote` is the stub; no repo-side launcher.

## Configuration surface

### how config reaches the server

Server-side: Wrangler config per Worker (`wrangler.toml`/`wrangler.jsonc`) controls deployment. Client-side: the host's MCP config holds only the URL. Authentication travels inline per-request.

## Authentication

### flow

Cloudflare API tokens with per-service scopes — created via Cloudflare dashboard and passed at auth time. OAuth-like flow documented for the hosted endpoints.

### where credentials come from

Cloudflare dashboard (API tokens); the `mcp-remote` shim negotiates auth handshake with the Worker.

## Multi-tenancy

### tenancy model

Per-request tenancy. Each Worker invocation is scoped by the bearer token → authenticated Cloudflare account. The same Worker serves any account that authenticates.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools per domain server. 14 domain servers cover: Documentation, Workers Bindings, Workers Builds, Observability, Radar, Container, Browser Rendering, Logpush, AI Gateway, AutoRAG, Audit Logs, DNS Analytics, Digital Experience Monitoring, CASB, GraphQL.

## Observability

### logging destination + format, metrics, tracing, debug flags

Worker logs via Cloudflare dashboard; not a self-hostable logging layer.

## Host integrations shown in README or repo

### Cursor

documented integration.

### Claude (Desktop implied)

JSON snippet via `mcp-remote`.

### Cloudflare AI Playground

first-party integration.

### OpenAI Responses API

documented integration.

### Claude Code

not explicitly documented (vs Claude Desktop); same JSON snippet pattern applies.

## Claude Code plugin wrapper

### presence and shape

Not observed in fetched view.

## Tests

### presence, framework, location, notable patterns

Vitest across the monorepo.

## CI

### presence, system, triggers, what it runs

GitHub Actions; Turbo orchestrates builds/tests.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

N/A — servers run as Workers, not containers.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

pnpm scripts; ESLint; Prettier; README supplies `mcp-remote` JSON snippets.

## Repo layout

### single-package / monorepo / vendored / other

Turbo/pnpm monorepo. 14 domain Workers as individual packages; shared `@repo/mcp-common` package abstracts common server concerns.

## Notable structural choices

All-remote deployment model — the repo ships operational Workers, not installable binaries. Users never run the server code; they consume it as a URL. Opposite end of the spectrum from awslabs/mcp (local-only stdio). `mcp-remote` as the stdio-to-streamable-HTTP bridge is the universal client shim; the repo itself never speaks stdio. Two transport endpoints coexisting on the same Worker (`/mcp` streamable-HTTP, `/sse` deprecated) lets clients migrate at their own pace. Shared `mcp-common` package: 14 domain servers factored into a shared scaffold + per-domain logic, mirroring Cloudflare's own platform composition patterns. Paid-plan gating called out: some features require Workers paid plan — operational cost surfaces as a server capability axis.

## Unanticipated axes observed

Hosting responsibility as a design axis: the server author operates the runtime, not the end user. Changes release concerns, auth model, and observability relative to locally-run servers. Stdio emulation via shim on the client side rather than on the server — hosts still speak stdio because `mcp-remote` translates to HTTP. Context-length mitigation guidance in README: chained-tool calls against high-cardinality Cloudflare data are called out as a context-window concern the client must manage.

## Gaps

Exact last commit on `main` (release tag is known, raw commit date not). Whether the 14 domain Workers expose consistent toolset-gating flags or each defines its own surface. Specific OAuth flow details for token negotiation. Whether a self-hostable variant is deployable from this repo (source ships, but docs focus on hosted URLs).
