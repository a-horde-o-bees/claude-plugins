# Sample

## Identification

### url

https://github.com/cloudflare/mcp-server-cloudflare

### stars

3.6k

### last-commit (date or relative)

`@repo/mcp-common@0.20.4` released 2026-03-31

### license

Apache-2.0

### default branch

main

### one-line purpose

Cloudflare remote-MCP monorepo — 14 domain Workers (Workers Bindings, Observability, Radar, Browser Rendering, AI Gateway, AutoRAG, Audit Logs, CASB, GraphQL, etc.) deployed on Cloudflare; users point clients at hosted URLs.

## 1. Language and runtime

### language(s) + version constraints

TypeScript (90.8%). Runs on Cloudflare Workers (V8 isolate runtime), not Node.

### framework/SDK in use

Cloudflare Workers stack; Turbo monorepo; internal `@repo/mcp-common` package abstracts shared server scaffolding.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

Streamable HTTP via `/mcp` endpoint (primary); SSE via `/sse` endpoint (deprecated).

### how selected (flag, env, separate entry, auto-detect, etc.)

URL path — the path (`/mcp` vs `/sse`) selects the transport on the same Worker.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, or other)

Remote-only — all 14 servers run as Cloudflare Workers at public URLs (e.g. `https://observability.mcp.cloudflare.com/mcp`). End users install by pointing `mcp-remote` (npm) at the URL. No local binary, Docker, or npm install of the servers themselves.

### published package name(s)

`mcp-remote` is the end-user shim (npm, not published by Cloudflare). `@repo/mcp-common@0.20.4` is an internal workspace package.

### install commands shown in README

```json
{"mcpServers": {"cloudflare-observability": {"command": "npx", "args": ["mcp-remote", "https://observability.mcp.cloudflare.com/mcp"]}}}
```

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`npx mcp-remote <cloudflare-mcp-url>` — the client shim bridges stdio (host side) to streamable-HTTP (Cloudflare side).

### wrapper scripts, launchers, stubs

`mcp-remote` is the stub; no repo-side launcher.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server (env vars, CLI args, config file w/ path + format, stdin prompt, OS keyring, host-passed params, combinations)

Server-side: Wrangler config per Worker (`wrangler.toml`/`wrangler.jsonc`) controls deployment. Client-side: the host's MCP config holds only the URL. Authentication travels inline per-request.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow (static token, OAuth w/ description, per-request header, none, other)

Cloudflare API tokens with per-service scopes — created via Cloudflare dashboard and passed at auth time. OAuth-like flow documented for the hosted endpoints.

### where credentials come from

Cloudflare dashboard (API tokens); the `mcp-remote` shim negotiates auth handshake with the Worker.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

Per-request tenancy. Each Worker invocation is scoped by the bearer token → authenticated Cloudflare account. The same Worker serves any account that authenticates.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools per domain server. 14 domain servers cover: Documentation, Workers Bindings, Workers Builds, Observability, Radar, Container, Browser Rendering, Logpush, AI Gateway, AutoRAG, Audit Logs, DNS Analytics, Digital Experience Monitoring, CASB, GraphQL.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Worker logs via Cloudflare dashboard; not a self-hostable logging layer.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, etc.):

### Cursor

documented integration

### Claude (Desktop implied)

JSON snippet via `mcp-remote`

### Cloudflare AI Playground

first-party integration

### OpenAI Responses API

documented integration

### Claude Code

not explicitly documented (vs Claude Desktop); same JSON snippet pattern applies

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape (.claude-plugin/plugin.json, .mcp.json at repo root, full plugin layout, not present, other)

Not observed in fetched view.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

Vitest across the monorepo.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

GitHub Actions; Turbo orchestrates builds/tests.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

N/A — servers run as Workers, not containers.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

pnpm scripts; ESLint; Prettier; README supplies `mcp-remote` JSON snippets.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other — describe what's there

Turbo/pnpm monorepo. 14 domain Workers as individual packages; shared `@repo/mcp-common` package abstracts common server concerns.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- All-remote deployment model — the repo ships operational Workers, not installable binaries. Users never run the server code; they consume it as a URL. Opposite end of the spectrum from awslabs/mcp (local-only stdio).
- `mcp-remote` as the stdio-to-streamable-HTTP bridge is the universal client shim; the repo itself never speaks stdio.
- Two transport endpoints coexisting on the same Worker (`/mcp` streamable-HTTP, `/sse` deprecated) lets clients migrate at their own pace.
- Shared `mcp-common` package: 14 domain servers factored into a shared scaffold + per-domain logic, mirroring Cloudflare's own platform composition patterns.
- Paid-plan gating called out: some features require Workers paid plan — operational cost surfaces as a server capability axis.

## 18. Unanticipated axes observed
- Hosting responsibility as a design axis: the server author operates the runtime, not the end user. Changes release concerns, auth model, and observability relative to locally-run servers.
- Stdio emulation via shim on the client side rather than on the server — hosts still speak stdio because `mcp-remote` translates to HTTP.
- Context-length mitigation guidance in README: chained-tool calls against high-cardinality Cloudflare data are called out as a context-window concern the client must manage.

## 20. Gaps
- Exact last commit on `main` (release tag is known, raw commit date not).
- Whether the 14 domain Workers expose consistent toolset-gating flags or each defines its own surface.
- Specific OAuth flow details for token negotiation.
- Whether a self-hostable variant is deployable from this repo (source ships, but docs focus on hosted URLs).
