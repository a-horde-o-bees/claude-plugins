# Sample

## Identification
- url: https://github.com/stripe/agent-toolkit
- stars: 1.5k
- last-commit (date or relative): Not explicitly extracted from README view
- license: MIT
- default branch: main
- one-line purpose: Stripe agent toolkit — MCP server plus host-specific wrappers; ships `.claude-plugin/` and `.cursor-plugin/` side by side.

## 1. Language and runtime
- language(s) + version constraints: TypeScript (51.9%) with substantial Python co-primary. Dual-language repo.
- framework/SDK in use: Stripe's own SDKs (Node, Python); Vercel AI SDK integration; MCP components as a third pillar.
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: Stdio via `@stripe/mcp` (local); remote hosted endpoint at `https://mcp.stripe.com` with OAuth.
- how selected (flag, env, separate entry, auto-detect, etc.): Install-target split — `npx @stripe/mcp` for stdio, the hosted URL for remote/OAuth.
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, or other):
  - npm: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`
  - PyPI: `stripe-agent-toolkit`
  - npx for the MCP entry
- published package name(s): see above
- install commands shown in README:
  - Python: `pip install stripe-agent-toolkit`
  - TypeScript: `npm install @stripe/agent-toolkit`
  - MCP: `npx -y @stripe/mcp --api-key=YOUR_STRIPE_SECRET_KEY`
- pitfalls observed:
  - Cross-ecosystem packaging: Python and TypeScript published from the same repo with parallel naming (`stripe-agent-toolkit` vs `@stripe/agent-toolkit`).

## 4. Entry point / launch
- command(s) users/hosts run: `npx -y @stripe/mcp --api-key=...` for stdio; hosted URL for remote.
- wrapper scripts, launchers, stubs: `@stripe/mcp` is the stdio entry; `@stripe/agent-toolkit` is the broader SDK.
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server (env vars, CLI args, config file w/ path + format, stdin prompt, OS keyring, host-passed params, combinations): `--api-key` CLI flag is the documented entry. Env var equivalent not fully extracted. Hosted endpoint handles config via OAuth scopes.
- pitfalls observed:
  - Exact env-var config surface vs CLI flags.

## 6. Authentication
- flow (static token, OAuth w/ description, per-request header, none, other): Static Stripe secret keys (recommend Restricted API Keys — RAK) for stdio; OAuth for hosted `mcp.stripe.com`.
- where credentials come from: Stripe dashboard generates secret keys / RAKs; OAuth flow for hosted consumption.
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-account per process for stdio (one API key → one Stripe account); per-user OAuth for the hosted endpoint (each user authorizes their own Stripe account).
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Tools exposing Stripe API surface (payments, customers, etc.). Specific tool enumeration not extracted.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not explicitly documented in README view.
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, etc.):
- Claude (Desktop): `.claude-plugin/` directory present — plugin wrapper shipped in-repo
- Cursor: `.cursor-plugin/` directory present — plugin wrapper shipped in-repo
- Other hosts: stdio via `npx @stripe/mcp` applies universally through host JSON config
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

`.claude-plugin/` directory present at repo root. No `.mcp.json` noted.

### pitfalls observed

- Contents of `.claude-plugin/plugin.json` (full plugin layout vs minimal).

## 12. Tests
- presence, framework, location, notable patterns: Not deeply extracted. `.github/` present suggests CI-driven testing.
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions present; specifics not extracted.
- pitfalls observed:
  - CI workflow specifics.

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not explicitly documented in README view.
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: Dual-ecosystem SDKs (Node + Python) alongside MCP. Restricted API Key guidance is a security-ergonomics feature.
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Monorepo. Multiple SDK packages coexist: `@stripe/agent-toolkit` (Python + TS), `@stripe/ai-sdk` (Vercel integration), `@stripe/token-meter` (native SDK billing), and `@stripe/mcp` (MCP component). `.claude-plugin/` and `.cursor-plugin/` ship alongside code.
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- MCP as one of several agent-integration surfaces: the repo is explicitly an "agent-toolkit" housing Vercel-AI, SDK-billing, and MCP side-by-side. MCP is a peer, not the product.
- Cross-ecosystem packaging: Python and TypeScript published from the same repo with parallel naming (`stripe-agent-toolkit` vs `@stripe/agent-toolkit`).
- Dual host-plugin wrappers shipped in-repo: `.claude-plugin/` and `.cursor-plugin/` — recognizing host-specific plugin formats as a distribution surface.
- Restricted API Key guidance elevated in docs — security posture as a first-class operational concern.
- Hosted remote + local stdio duality, similar pattern to sentry-mcp and cloudflare.

## 18. Unanticipated axes observed
- Multi-surface agent tooling: one repo ships SDKs, AI-framework integrations, billing primitives, and MCP — MCP treated as an integration channel among peers rather than the whole product.
- Per-host plugin wrappers as shipped artifacts (`.cursor-plugin/` in addition to `.claude-plugin/`).
- Credential-scoping as guidance (RAK) — vendor-specific security ergonomics documented alongside install.

## 20. Gaps
- Last-commit date.
- Specific tool list.
- CI workflow specifics.
- Whether Dockerfile is present.
- Contents of `.claude-plugin/plugin.json` (full plugin layout vs minimal).
- Exact env-var config surface vs CLI flags.
