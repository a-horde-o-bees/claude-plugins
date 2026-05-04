# Sample

Mirrors of `https://github.com/getsentry/sentry-mcp`. Sentry error-monitoring MCP server — ships both `.claude-plugin/` and `.mcp.json` in-repo; defines an internal "Skills" concept alongside tools; operates the hosted `mcp.sentry.dev` endpoint plus a self-hosted stdio install. 654 stars, default branch `main`, 963 commits on main, vendor-authored (Sentry).

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (98.3%) on the MCP TypeScript SDK (inferred from monorepo conventions); Node runtime, version constraint not extracted.

## Transport

### stdio

Local self-hosted mode via npx — primarily for self-hosted Sentry deployments.

### Hosted remote endpoint (vendor-operated)

Hosted at `https://mcp.sentry.dev`; the host is configured to point at the URL rather than launching anything locally.

### Selection mechanism

Remote vs local is a different install target — stdio install points `npx` at the package; remote points the host at `mcp.sentry.dev`.

## Capability surface

### Tools plus internal "skills" abstraction

Tools for Sentry issue/error/release workflows. "Skills" is a first-class toggleable abstraction — `MCP_DISABLE_SKILLS` env var (comma-separated) toggles skill subsets. Skills live in `.agents/skills/`. README positions the server as "primarily designed for human-in-the-loop coding agents."

## Configuration delivery

### Environment variables

`SENTRY_ACCESS_TOKEN`, `EMBEDDED_AGENT_PROVIDER` (`openai` | `anthropic`), `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SENTRY_HOST` (self-hosted override), `MCP_DISABLE_SKILLS` (comma-separated skill subset).

### CLI flags

`--access-token=...` on the npx entry.

### `.mcp.json` in project root

`.mcp.json` at repo root for MCP client configuration.

### Feature-group toggles

`MCP_DISABLE_SKILLS` toggles skill subsets per deployment, letting operators trim the behavioral surface.

## Authentication

### Static API key / token via env var

Static Sentry user auth tokens with scopes `org:read project:read project:write team:read team:write event:write`, supplied via `SENTRY_ACCESS_TOKEN` env var or `--access-token` flag. Sourced from the Sentry dashboard.

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

OAuth App support on the hosted `mcp.sentry.dev` endpoint, enabling per-user consent for the multi-tenant remote.

## Multi-tenancy

### Single-user / single-tenant per process

stdio mode runs single-user per process.

### Per-user / per-workspace via OAuth

Hosted endpoint authenticates per-user via OAuth, scoping access by user identity.

## Distribution channel

### npm via npx / bunx

Published as `@sentry/mcp-server`. Install: `npx @sentry/mcp-server@latest --access-token=sentry-user-token`.

### Hosted endpoint (no install)

`mcp.sentry.dev` operated by Sentry — no install needed for the hosted path.

### `.claude-plugin/marketplace.json`

Claude Marketplace plugin install path documented in README — server vends itself as a Claude plugin.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx @sentry/mcp-server@latest --access-token=...` for local stdio.

### URL configuration (no local launch)

Hosted endpoint URL pasted into host config for the remote path.

## Build and packaging

### npm/Node toolchain

pnpm workspace + Turbo monorepo; package.json bin and build entries.

## Repository layout

### Turbo + pnpm monorepo

Multiple packages under `/packages` orchestrated with pnpm workspaces and Turbo. `.agents/skills/` holds skill definitions; `.claude-plugin/` and `.mcp.json` live at root.

## Test stack

### Evaluation harness alongside unit tests

`pnpm test` (unit) and `pnpm eval` (evaluations/scenario tests) run as peers — distinguishes behavioral regression from code regression. MCP Inspector used for local testing.

## CI

### GitHub Actions

GitHub Actions configured (implied by monorepo standard); specific workflows not extracted.

## Host integration

### Claude Code

Documented integration.

### Cursor

Documented integration.

### Claude Desktop

Marketplace plugin (distinct from raw JSON snippet).

### `.claude-plugin/` directory in repo

`.claude-plugin/` directory shipped in-repo — server vends itself as a Claude plugin, not just a raw MCP binary.

### `.mcp.json` in project root

`.mcp.json` at repo root.

## Documentation surface

### README as the canonical surface

README plus monorepo workspace scripts (`pnpm -w run cli`).

## Domain logic and embedded intelligence

### In-server LLM client

`EMBEDDED_AGENT_PROVIDER` (`openai` | `anthropic`) plus provider-specific API keys let the MCP server invoke an LLM internally — unusual; most MCP servers are pure tool-callers. Shifts some "agent" responsibility inside the MCP boundary.

## Deployment topology

### Hosted SaaS endpoint

`mcp.sentry.dev` hosted by Sentry serves the remote path.

### Local stdio process per session

npx-launched local process serves self-hosted Sentry deployments.

## Developer ergonomics

### Inspector/debug tooling references

MCP Inspector called out for local testing. `pnpm -w run cli` for manual CLI testing. `pnpm eval` evaluation harness for regression testing against model outputs.
