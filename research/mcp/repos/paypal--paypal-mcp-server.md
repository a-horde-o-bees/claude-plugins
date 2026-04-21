# paypal/paypal-mcp-server

## Identification
- url: https://github.com/paypal/paypal-mcp-server
- stars: 9
- last-commit (date or relative): Specific date not displayed; total commit count was 9 as of research
- license: Apache-2.0
- default branch: main
- one-line purpose: PayPal payments MCP server — JavaScript/npx distribution; OAuth 2.0 auth.

## 1. Language and runtime
- language(s) + version constraints: JavaScript (75.7%), TypeScript (15.8%), Shell (8.5%); Node.js 18+
- framework/SDK in use: Model Context Protocol SDK (standard MCP TypeScript SDK, implied by npm package layout and MCP conventions)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio
- how selected (flag, env, separate entry, auto-detect, etc.): Stdio is the default; launched via `npx` and connected through host MCP config
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: npm package, npx direct execution, Claude Desktop configuration-file integration
- published package name(s): @paypal/mcp
- install commands shown in README: `npx -y @paypal/mcp --tools=all`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `npx -y @paypal/mcp --tools=all` (or with `--access-token`)
- wrapper scripts, launchers, stubs: npm `bin` entry invoked via npx; Shell files present (8.5% of repo) suggest auxiliary scripts
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: Environment variables for credentials and environment selection; CLI flags for tool selection and token override
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: OAuth2 client credentials — bearer token generated, valid 3-8 hours (sandbox) or 8 hours (production). Server holds a single merchant's token for the session
- where credentials come from: `PAYPAL_ACCESS_TOKEN` env var (required); `--access-token` CLI flag alternative; `PAYPAL_ENVIRONMENT` selects SANDBOX or PRODUCTION
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-merchant — token is process-scoped to one PayPal merchant account. No per-request tenancy or multi-merchant switching observed
- pitfalls observed:
  - Token lifetimes (3-8 hours sandbox, 8 hours production) mean long-lived sessions need refresh handling; not clear from surface whether server refreshes automatically or expects ...

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 30+ tools grouped by domain — Invoices (7), Payments & Refunds (5), Dispute Management (3), Shipment Tracking (2), Catalog Management (4), Subscription Management (8), Transaction Reporting (1). `--tools=all` selects full surface; selective subsets likely supported via the same flag
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not explicitly documented within extracted content
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude Desktop (primary — JSON config snippets)
- Cursor
- Cline
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape: Not observed — no `.claude-plugin` directory surfaced in research
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Jest configured; specific test layout not extracted within budget
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions `.github/workflows` directory present; specific workflows not extracted within budget
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not observed within extracted content
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: ESLint config; Jest; Claude Desktop and Cursor sample configs in README
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package Node.js project; mixed JS/TS (JS majority) with Shell auxiliary scripts
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Modular `--tools` selection lets users opt into sub-surfaces rather than exposing 30+ tools unconditionally — reduces prompt-window noise for users who only need invoicing or subscriptions
- Sandbox/production are explicit env-var branches, not separate entry points — a single binary routes based on `PAYPAL_ENVIRONMENT`
- Token lifetimes (3-8 hours sandbox, 8 hours production) mean long-lived sessions need refresh handling; not clear from surface whether server refreshes automatically or expects caller to rotate
- First-party PayPal ownership — Apache-2.0, paypal-org namespace — makes this the canonical PayPal MCP despite modest star count

## 18. Unanticipated axes observed
- Low star count (9) for a first-party vendor release suggests either early days or limited announcement; worth monitoring as a case of "official but unpromoted" servers
- The `--tools` opt-in pattern is an example of capability scoping at launch time — a structural choice worth noting for MCPs with large tool surfaces

## 20. Gaps
- Whether token auto-refresh is implemented or delegated to caller
- CI workflow specifics and test coverage layout
- Exact list of tools within each category (only counts observed)
- Whether HTTP transport is planned or stdio-only is intentional
