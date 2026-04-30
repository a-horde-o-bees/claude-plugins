# Sample

## Identification

### url

https://github.com/stripe/agent-toolkit

### stars

1.5k

### last-commit

Not explicitly extracted from README view

### license

MIT

### default branch

main

### one-line purpose

Stripe agent toolkit — MCP server plus host-specific wrappers; ships `.claude-plugin/` and `.cursor-plugin/` side by side.

## Language and runtime

### language(s) + version constraints

TypeScript (51.9%) with substantial Python co-primary. Dual-language repo.

### framework/SDK in use

Stripe's own SDKs (Node, Python); Vercel AI SDK integration; MCP components as a third pillar.

## Transport

### supported transports

Stdio via `@stripe/mcp` (local); remote hosted endpoint at `https://mcp.stripe.com` with OAuth.

### how selected

Install-target split — `npx @stripe/mcp` for stdio, the hosted URL for remote/OAuth.

## Distribution

### every mechanism observed

npm packages: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`. PyPI: `stripe-agent-toolkit`. npx for the MCP entry.

### published package name(s)

npm: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`. PyPI: `stripe-agent-toolkit`.

### install commands shown in README

Python: `pip install stripe-agent-toolkit`. TypeScript: `npm install @stripe/agent-toolkit`. MCP: `npx -y @stripe/mcp --api-key=YOUR_STRIPE_SECRET_KEY`.

### pitfalls observed

Cross-ecosystem packaging: Python and TypeScript published from the same repo with parallel naming (`stripe-agent-toolkit` vs `@stripe/agent-toolkit`).

## Entry point / launch

### command(s) users/hosts run

`npx -y @stripe/mcp --api-key=...` for stdio; hosted URL for remote.

### wrapper scripts, launchers, stubs

`@stripe/mcp` is the stdio entry; `@stripe/agent-toolkit` is the broader SDK.

## Configuration surface

### how config reaches the server

`--api-key` CLI flag is the documented entry. Env var equivalent not fully extracted. Hosted endpoint handles config via OAuth scopes.

### pitfalls observed

Exact env-var config surface vs CLI flags not extracted.

## Authentication

### flow

Static Stripe secret keys (recommend Restricted API Keys — RAK) for stdio; OAuth for hosted `mcp.stripe.com`.

### where credentials come from

Stripe dashboard generates secret keys / RAKs; OAuth flow for hosted consumption.

## Multi-tenancy

### tenancy model

Single-account per process for stdio (one API key → one Stripe account); per-user OAuth for the hosted endpoint (each user authorizes their own Stripe account).

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools exposing Stripe API surface (payments, customers, etc.). Specific tool enumeration not extracted.

## Observability

### logging destination + format, metrics, tracing, debug flags

Not explicitly documented in README view.

## Host integrations shown in README or repo

### Claude Desktop

`.claude-plugin/` directory present — plugin wrapper shipped in-repo.

### Cursor

`.cursor-plugin/` directory present — plugin wrapper shipped in-repo.

### Other hosts

stdio via `npx @stripe/mcp` applies universally through host JSON config.

## Claude Code plugin wrapper

### presence and shape

`.claude-plugin/` directory present at repo root. No `.mcp.json` noted.

### pitfalls observed

Contents of `.claude-plugin/plugin.json` (full plugin layout vs minimal) not extracted.

## Tests

### presence, framework, location, notable patterns

Not deeply extracted. `.github/` present suggests CI-driven testing.

## CI

### presence, system, triggers, what it runs

GitHub Actions present; specifics not extracted.

### pitfalls observed

CI workflow specifics not extracted.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not explicitly documented in README view.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Dual-ecosystem SDKs (Node + Python) alongside MCP. Restricted API Key guidance is a security-ergonomics feature.

## Repo layout

### single-package / monorepo / vendored / other

Monorepo. Multiple SDK packages coexist: `@stripe/agent-toolkit` (Python + TS), `@stripe/ai-sdk` (Vercel integration), `@stripe/token-meter` (native SDK billing), and `@stripe/mcp` (MCP component). `.claude-plugin/` and `.cursor-plugin/` ship alongside code.

## Notable structural choices

MCP as one of several agent-integration surfaces: the repo is explicitly an "agent-toolkit" housing Vercel-AI, SDK-billing, and MCP side-by-side. MCP is a peer, not the product.

Cross-ecosystem packaging: Python and TypeScript published from the same repo with parallel naming (`stripe-agent-toolkit` vs `@stripe/agent-toolkit`).

Dual host-plugin wrappers shipped in-repo: `.claude-plugin/` and `.cursor-plugin/` — recognizing host-specific plugin formats as a distribution surface.

Restricted API Key guidance elevated in docs — security posture as a first-class operational concern.

Hosted remote + local stdio duality, similar pattern to sentry-mcp and cloudflare.

## Unanticipated axes observed

Multi-surface agent tooling: one repo ships SDKs, AI-framework integrations, billing primitives, and MCP — MCP treated as an integration channel among peers rather than the whole product.

Per-host plugin wrappers as shipped artifacts (`.cursor-plugin/` in addition to `.claude-plugin/`).

Credential-scoping as guidance (RAK) — vendor-specific security ergonomics documented alongside install.

## Gaps

Last-commit date not extracted. Specific tool list not extracted. CI workflow specifics not extracted. Whether Dockerfile is present not extracted. Contents of `.claude-plugin/plugin.json` (full plugin layout vs minimal) not extracted. Exact env-var config surface vs CLI flags not extracted.
