# Sample

Mirrors of `https://github.com/stripe/agent-toolkit`. Stripe agent toolkit — MCP server alongside SDKs and AI-framework integrations (Vercel AI SDK, native SDK billing). 1.5k stars, MIT, default branch `main`. Cross-ecosystem monorepo publishing both Python and TypeScript packages; ships `.claude-plugin/` and `.cursor-plugin/` side by side. MCP is one of several agent-integration surfaces, not the primary product.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (51.9%) is the primary language for the MCP component (`@stripe/mcp`). Anthropic MCP SDK + Stripe's own Node SDK; Vercel AI SDK integration as a peer.

### Python with raw MCP SDK

Python co-primary in the repo; `stripe-agent-toolkit` PyPI package coexists with the TS packages. Python uses Stripe's own SDK alongside MCP components.

## Transport

### stdio

Stdio via `@stripe/mcp` (local) — `npx -y @stripe/mcp --api-key=YOUR_STRIPE_SECRET_KEY` invokes the local stdio server.

### Hosted remote endpoint (vendor-operated)

Stripe operates a hosted remote endpoint at `https://mcp.stripe.com` with OAuth — clients point at the URL rather than launching anything locally.

### Selection mechanism

Install-target split — `npx @stripe/mcp` for stdio (local), the hosted URL for remote/OAuth. Two distinct entry points rather than runtime mode-switching within one binary.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Tools exposing the Stripe API surface (payments, customers, etc.). Specific tool enumeration not extracted within budget.

## Configuration delivery

### CLI flags

`--api-key` is the documented CLI entry for the stdio server. Hosted endpoint handles config via OAuth scopes; env-var equivalent for `--api-key` not fully extracted.

## Authentication

### Static API key / token via env var

Stdio path uses static Stripe secret keys passed via `--api-key=...`. Stripe dashboard generates the keys.

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

OAuth for hosted `mcp.stripe.com` — per-user consent. Each user authorizes their own Stripe account; the hosted endpoint holds per-user tokens.

### Credential-scoping guidance

README guidance recommends Restricted API Keys (RAK) over the full-power root secret key — security-ergonomics layer atop the static-key auth mechanism. Documentation pattern, not enforcement.

## Multi-tenancy

### Single-user / single-tenant per process

Stdio mode: one `--api-key` per process maps to one Stripe account.

### Per-user / per-workspace via OAuth

Hosted endpoint: per-user OAuth determines the tenant; each authenticated user's MCP calls run under their own Stripe account.

## Distribution channel

### npm via npx / bunx

npm packages: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`. The MCP entry uses `npx -y @stripe/mcp --api-key=...`.

### PyPI via pip / pipx

PyPI package: `stripe-agent-toolkit`. Install: `pip install stripe-agent-toolkit`.

### Hosted endpoint (no install)

`https://mcp.stripe.com` is the hosted remote-only path; no install when consumers point their host at the URL.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx -y @stripe/mcp --api-key=...` for the stdio launch — `--api-key` passed inline.

### URL configuration (no local launch)

Hosted endpoint: clients configure their MCP host with the `https://mcp.stripe.com` URL — no local launch step.

## Repository layout

### Monorepo with multiple published packages

Monorepo with multiple npm packages (`@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`) plus PyPI `stripe-agent-toolkit`. `.claude-plugin/` and `.cursor-plugin/` ship alongside code. MCP is treated as a peer to SDKs and AI-framework integrations rather than as the whole product.

### Single-package with dual-ecosystem wrapper

Cross-ecosystem packaging — Python and TypeScript published from the same repo with parallel naming (`stripe-agent-toolkit` PyPI vs `@stripe/agent-toolkit` npm).

## CI

### GitHub Actions

GitHub Actions present in `.github/`. Workflow specifics not extracted.

## Host integration

### Claude Code

`.claude-plugin/` directory present at repo root — first-class Claude Code plugin wrapper alongside the raw MCP server.

### Cursor

`.cursor-plugin/` directory present at repo root — Cursor-specific plugin wrapper analogous to `.claude-plugin/`.

### Generic / host-agnostic snippet

Stdio via `npx @stripe/mcp` applies universally across MCP hosts via standard host JSON config.

## Claude Code plugin / skill wrapper

### `.claude-plugin/` wrapper

`.claude-plugin/` directory present at repo root. Contents (full plugin layout vs minimal) not extracted within budget. No `.mcp.json` noted.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT licensed.

### Active development

Active project. Last-commit date and CI specifics not extracted within budget.
