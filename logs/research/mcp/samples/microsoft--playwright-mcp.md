# Sample

## Identification
- url: https://github.com/microsoft/playwright-mcp
- stars: 31.1k
- last-commit (date or relative): v0.0.70 released 2026-04-01
- license: Apache-2.0
- default branch: main
- one-line purpose: Playwright browser MCP server — accessibility-tree-driven browser automation; Microsoft-authored.

## 1. Language and runtime
- language(s) + version constraints: TypeScript (62.2%). Node.js runtime; version constraint not extracted.
- framework/SDK in use: Playwright + Model Context Protocol SDK. Programmatic Node.js API exposes `createConnection()`.
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default); SSE over HTTP when `--port` is set.
- how selected (flag, env, separate entry, auto-detect, etc.): CLI flag — presence of `--port <n>` flips to SSE/HTTP; absence defaults to stdio.
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, or other): npm + npx, Docker (`mcr.microsoft.com/playwright/mcp`). Docker multi-arch. No Homebrew/binary releases.
- published package name(s): `@playwright/mcp`
- install commands shown in README:
  - `npx @playwright/mcp@latest`
  - `docker run -i --rm --init --pull=always mcr.microsoft.com/playwright/mcp`
  - Docker service mode exposes port 8931.
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `npx @playwright/mcp@latest` (stdio), `npx @playwright/mcp@latest --port 8931` (SSE/HTTP).
- wrapper scripts, launchers, stubs: `createConnection()` programmatic API for embedding in Node apps.
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server (env vars, CLI args, config file w/ path + format, stdin prompt, OS keyring, host-passed params, combinations): 50+ CLI flags and matching env vars; JSON config file via `--config`.
  - Browser: `--browser`, `--headless`, `--executable-path`, `--user-data-dir`
  - Network: `--allowed-origins`, `--blocked-origins`, `--proxy-server`
  - Timeouts: `--timeout-action`, `--timeout-navigation`
  - Advanced: `--cdp-endpoint`, `--init-page`, `--init-script`, `--caps`
  - Every flag has a `PLAYWRIGHT_MCP_*` env-var equivalent.
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow (static token, OAuth w/ description, per-request header, none, other): None. README explicitly states "Playwright MCP is not a security boundary." Storage-state files support session persistence (not auth).
- where credentials come from: N/A.
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user per process.
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: 80+ structured tools with role-based permissions in categories:
  - Core automation: click, type, navigate, screenshot, snapshot
  - Tab management
  - Network: mocking, state inspection, route management (opt-in)
  - Storage: cookies, localStorage, sessionStorage (opt-in)
  - DevTools: tracing, video, element highlight, debugging (opt-in)
  - Vision: coordinate-based interactions (opt-in via `--caps=vision`)
  - PDF: page-to-PDF conversion (opt-in via `--caps=pdf`)
  - Testing: assertions, locator generation (opt-in via `--caps=testing`)
- Emphasis on accessibility-tree snapshots over screenshots for token-efficiency.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: `--init-script` lets users inject instrumentation. Tracing and video are capability toggles rather than observability per se.
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, etc.):
- Claude Desktop, Claude Code, VS Code, Cursor, Windsurf, Cline, Goose, Junie, Copilot, Factory, Gemini CLI, LM Studio, Kiro, opencode, Qodo Gen, Warp, Codex, Antigravity, Amp — listed as supported clients in README.
- Form: JSON snippet pattern shared across hosts (stdio command + args). No host-specific plugin wrapper in repo.
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not observed in fetched view.

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: `.github/workflows` present. Test setup not deeply extracted; Playwright's own test harness likely used given the project heritage.
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions. 60 releases, indicating an active release pipeline.
- pitfalls observed:
  - CI workflow specifics.

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile; multi-arch image on `mcr.microsoft.com/playwright/mcp`.
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: CONTRIBUTING.md + SECURITY.md. `createConnection()` enables programmatic embedding.
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Monorepo with `/packages`.
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Accessibility snapshots as primary perception model — token-efficient vs screenshot/vision. Vision is opt-in via `--caps=vision`, not default.
- `--caps=<cap>` as a capability-gating pattern: pdf, vision, testing are opt-in capability groups that unlock tool subsets — a different gating axis than the `--toolsets`/`--read-only` model used by github-mcp-server.
- Security posture explicitly disclaimed ("not a security boundary") rather than implemented. `--allow-unrestricted-file-access` is the escape hatch.
- Programmatic embedding as first-class: `createConnection()` means this MCP server can run inside host processes as a library, not just as an external subprocess.

## 18. Unanticipated axes observed
- Capability groups (`--caps`) as an install-time surface for trimming tool exposure — distinct from per-tool toggles. Shapes token usage and security posture.
- Storage-state persistence (browser sessions) as a non-auth state-carrying mechanism — state portability between runs.
- Embeddability: this MCP server can be a Node library inside another process, blurring server/client lines.
- Accessibility-tree-first interaction model as a design commitment, not a fallback — reverses the default assumption that browser automation needs visual models.

## 20. Gaps
- Exact Node.js version constraint.
- Whether any authentication layer can be added via the programmatic API.
- CI workflow specifics.
