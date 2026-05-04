# Sample

Mirrors of `https://github.com/paypal/paypal-mcp-server`. PayPal payments MCP server — JavaScript/npx distribution; OAuth 2.0 client-credentials auth; first-party PayPal-org release. 9 stars, Apache-2.0, default branch `main`, 9 total commits as of research.

## Server runtime

### Node.js / TypeScript with official MCP SDK

JavaScript (75.7%) with TypeScript (15.8%) and Shell (8.5%); Node.js 18+. Uses the standard MCP TypeScript SDK (implied by npm package layout and MCP conventions).

## Transport

### stdio

stdio is the only documented transport — launched via `npx` and connected through host MCP config.

### Selection mechanism

stdio default; no explicit selection mechanism (single-transport binary).

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

30+ tools grouped by PayPal domain — Invoices (7), Payments & Refunds (5), Dispute Management (3), Shipment Tracking (2), Catalog Management (4), Subscription Management (8), Transaction Reporting (1).

### Capability gating flags (per-tool, per-category, write-mode)

`--tools=all` flag selects the full surface; selective subsets supported via the same flag — capability scoping at launch time, an opt-in pattern for servers with large tool catalogs.

## Configuration delivery

### Environment variables

`PAYPAL_ACCESS_TOKEN` (required) for the merchant token; `PAYPAL_ENVIRONMENT` selects `SANDBOX` or `PRODUCTION` — sandbox/production routed by env var rather than separate entry points.

### CLI flags

`--tools=all` for tool selection; `--access-token` as an alternative to env var for token override.

### Host-side JSON config snippet

Claude Desktop, Cursor, and Cline JSON `mcpServers` configuration snippets in README.

## Authentication

### OAuth 2.0 client credentials

OAuth2 client credentials flow — bearer token generated, valid 3-8 hours (sandbox) or 8 hours (production). Server holds a single merchant's token for the session. Token lifetime means long-lived sessions need refresh handling; not clear from surface whether server refreshes automatically or expects caller to rotate.

## Multi-tenancy

### Single-user / single-tenant per process

Single-merchant — token is process-scoped to one PayPal merchant account. No per-request tenancy or multi-merchant switching observed.

## Distribution channel

### npm via npx / bunx

`npx -y @paypal/mcp --tools=all` is the documented install/run path.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx -y @paypal/mcp --tools=all` (or with `--access-token`). npm `bin` entry invoked via npx; Shell files (8.5% of repo) suggest auxiliary scripts.

## Test stack

### Jest (TypeScript / Node)

Jest configured; specific test layout not extracted within budget.

## CI

### GitHub Actions

`.github/workflows` directory present; specific workflows not extracted within budget.

## Host integration

### Claude Desktop

Primary — JSON config snippets in README.

### Cursor

Supported — JSON config snippet in README.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Cline supported — JSON config snippet in README.

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin` directory observed.

## Documentation surface

### README as the canonical surface

README provides Claude Desktop and Cursor sample configs; ESLint config also present.

## Repository layout

### Single-package source (language-conventional)

Single-package Node.js project; mixed JS/TS (JS majority) with Shell auxiliary scripts.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0; first-party PayPal ownership in the paypal-org namespace makes this the canonical PayPal MCP despite modest star count (9).
