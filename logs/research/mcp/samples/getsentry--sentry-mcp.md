# getsentry/sentry-mcp

## Identification
- url: https://github.com/getsentry/sentry-mcp
- stars: 654
- last-commit (date or relative): 963 commits on main; active (specific date not extracted)
- license: Specified in LICENSE.md (not extracted within budget)
- default branch: main
- one-line purpose: Sentry error-monitoring MCP server — ships both `.claude-plugin/` and `.mcp.json`; defines an internal 'Skills' concept alongside tools.

## 1. Language and runtime
- language(s) + version constraints: TypeScript (98.3%). Node runtime; constraint not extracted.
- framework/SDK in use: pnpm workspace + Turbo monorepo; MCP TypeScript SDK (inferred).
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: HTTP (remote service `https://mcp.sentry.dev`); stdio (local, primarily for self-hosted Sentry deployments).
- how selected (flag, env, separate entry, auto-detect, etc.): Remote vs local is a different install target — stdio install points `npx` at the package; remote pointed at `mcp.sentry.dev`.
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, or other): npm; Claude Desktop plugin via marketplace. No Docker/binary noted in README view.
- published package name(s): `@sentry/mcp-server`
- install commands shown in README:
  - `npx @sentry/mcp-server@latest --access-token=sentry-user-token`
  - Claude Marketplace plugin install path
- pitfalls observed:
  - Evaluation discipline baked into repo — `pnpm eval` as a peer of `pnpm test`.
  - Whether Docker image is published.

## 4. Entry point / launch
- command(s) users/hosts run: `npx @sentry/mcp-server@latest --access-token=...` for local stdio; hosted endpoint URL for remote.
- wrapper scripts, launchers, stubs: Monorepo workspace scripts (`pnpm -w run cli`).
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server (env vars, CLI args, config file w/ path + format, stdin prompt, OS keyring, host-passed params, combinations): Primarily env vars; `.mcp.json` at repo root for MCP client configuration; CLI flag `--access-token` on the npx entry.
  - Env: `SENTRY_ACCESS_TOKEN`, `EMBEDDED_AGENT_PROVIDER` ('openai' | 'anthropic'), `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SENTRY_HOST` (self-hosted override), `MCP_DISABLE_SKILLS` (comma-separated).
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow (static token, OAuth w/ description, per-request header, none, other): Static Sentry user auth tokens with scopes `org:read project:read project:write team:read team:write event:write`. OAuth App support for remote deployments.
- where credentials come from: Sentry dashboard (user tokens); OAuth for the hosted `mcp.sentry.dev` endpoint.
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user per process (stdio); per-user OAuth on hosted endpoint.
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Tools for Sentry issue/error/release workflows. "Skills" concept is first-class — `MCP_DISABLE_SKILLS` env var toggles skill subsets (skills live under `.agents/skills/`). The README positions this as "primarily designed for human-in-the-loop coding agents."
- Embedded agent provider (OpenAI or Anthropic) callable from within the server — implies the MCP server itself can invoke an LLM for aggregation/summarization beyond raw tool output.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not explicitly extracted. Unit tests and evaluation harness provided (`pnpm test`, `pnpm eval`).
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, etc.):
- Claude Code — integration documented
- Cursor — integration documented
- Claude Desktop — as a marketplace plugin (distinct from raw JSON snippet)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape (.claude-plugin/plugin.json, .mcp.json at repo root, full plugin layout, not present, other): Both present — `.claude-plugin/` directory and `.mcp.json` at repo root. Full Claude plugin wrapper shipped in-repo.
- pitfalls observed:
  - `.claude-plugin/` wrapper shipped in-repo — the server vends itself as a Claude plugin, not just a raw MCP binary.

## 12. Tests
- presence, framework, location, notable patterns: `pnpm test` (unit); `pnpm eval` (evaluations/scenario tests). MCP Inspector used for local testing.
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions (implied by monorepo standard). Specific workflows not extracted.
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not explicitly documented.
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `pnpm -w run cli` for manual CLI testing. MCP Inspector called out. Evaluation harness (`pnpm eval`) for regression testing against model outputs.
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Monorepo (pnpm workspaces + Turbo). Multiple packages under `/packages`. `.agents/skills/` for skill definitions. `.claude-plugin/` and `.mcp.json` at root.
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- "Skills" as a first-class toggleable abstraction — `MCP_DISABLE_SKILLS` lets operators trim the behavioral surface per-deployment. Skills live in `.agents/skills/`, reflecting a structured agent-capability concept distinct from tools.
- In-server LLM calls: `EMBEDDED_AGENT_PROVIDER` + provider-specific API keys let the MCP server invoke an LLM internally — unusual; most MCP servers are pure tool-callers.
- Dual deployment: same code operates the hosted `mcp.sentry.dev` endpoint and the local self-hosted stdio install; `SENTRY_HOST` env var is the self-hosted pivot.
- `.claude-plugin/` wrapper shipped in-repo — the server vends itself as a Claude plugin, not just a raw MCP binary.
- Evaluation harness alongside unit tests — distinguishes behavioral regression from code regression.

## 18. Unanticipated axes observed
- Server-internal LLM invocation as an architecture pattern — shifts some "agent" responsibility inside the MCP boundary.
- Skills as a unit of capability bundling, separate from tools — a higher-level behavioral primitive.
- In-repo Claude plugin wrapper — rare; most servers leave host integration to external config.
- Evaluation discipline baked into repo — `pnpm eval` as a peer of `pnpm test`.

## 20. Gaps
- License content (LICENSE.md not fetched).
- Last-commit date.
- Exact toolset enumeration.
- Whether Docker image is published.
- Specific OAuth App flow details for the hosted endpoint.
