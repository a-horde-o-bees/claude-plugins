# Sample

Mirrors of `https://github.com/microsoft/playwright-mcp`. Playwright browser MCP server — accessibility-tree-driven browser automation, 80+ structured tools across categories, Microsoft-authored. 31.1k stars, Apache-2.0, default branch `main`, v0.0.70 released 2026-04-01.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (62.2%) on Node.js (specific version constraint not extracted), built on the Playwright + Model Context Protocol SDK. Programmatic Node.js API exposes `createConnection()` for embedding the server inside another Node process as a library.

## Transport

### stdio

Default transport.

### SSE (Server-Sent Events)

Activated when `--port <n>` is set; uses HTTP-based SSE for streaming.

### Selection mechanism

CLI flag — presence of `--port <n>` flips to SSE/HTTP; absence defaults to stdio.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

80+ structured tools wrapping Playwright browser-automation operations. Categories: Core automation (click, type, navigate, screenshot, snapshot); Tab management; Network (mocking, state inspection, route management — opt-in); Storage (cookies, localStorage, sessionStorage — opt-in); DevTools (tracing, video, element highlight, debugging — opt-in). Emphasis on accessibility-tree snapshots over screenshots for token-efficiency.

### Capability gating via tool subsets at install time

`--caps=vision`, `--caps=pdf`, `--caps=testing` are opt-in capability groups that unlock tool subsets — vision (coordinate-based interactions), PDF (page-to-PDF conversion), testing (assertions, locator generation). Gates groups of related tools as a unit, distinct from per-tool toggles. The author explicitly frames this as a different gating axis than `--toolsets` / `--read-only` style flags.

## Configuration delivery

### CLI flags with paired env-var equivalents

50+ CLI flags, each with a matching `PLAYWRIGHT_MCP_*` env-var equivalent. Browser controls: `--browser`, `--headless`, `--executable-path`, `--user-data-dir`. Network: `--allowed-origins`, `--blocked-origins`, `--proxy-server`. Timeouts: `--timeout-action`, `--timeout-navigation`. Advanced: `--cdp-endpoint`, `--init-page`, `--init-script`, `--caps`.

### Sidecar config files (JSON / YAML / TOML / EDN)

JSON config file supplied via `--config` flag.

## Authentication

### None / implicit (local-resource gating)

No auth at the MCP layer. README explicitly states "Playwright MCP is not a security boundary" — non-auth is a stated design posture rather than an oversight. Storage-state files support browser session persistence (not auth).

## Multi-tenancy

### Single-user / single-tenant per process

Single-user per process.

## Distribution channel

### npm via npx / bunx

`npx @playwright/mcp@latest` — published as `@playwright/mcp`.

### Docker / OCI image

`mcr.microsoft.com/playwright/mcp` (multi-arch). `docker run -i --rm --init --pull=always mcr.microsoft.com/playwright/mcp`. Docker service mode exposes port 8931.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx @playwright/mcp@latest` (stdio); `npx @playwright/mcp@latest --port 8931` (SSE/HTTP).

### Programmatic embedding via library function

`createConnection()` programmatic API for embedding inside a Node process as a library, blurring server/client lines.

### Docker container entrypoint

`docker run -i --rm --init --pull=always mcr.microsoft.com/playwright/mcp`.

## Build and packaging

### npm/Node toolchain

`@playwright/mcp` published on npm.

### System-level dependencies

Browser runtime (Playwright) — server depends on a browser binary that Playwright fetches as part of its install step. Multi-GB install footprint; container distribution becomes significantly more attractive than bare npm.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present; multi-arch image on `mcr.microsoft.com/playwright/mcp`.

### Vendor-namespaced image

Image lives in Microsoft's container registry (`mcr.microsoft.com`) rather than the public `mcp/*` namespace.

### Multi-architecture image publishing

Multi-arch publication on the vendor registry.

### Published Docker image

Pre-built image at `mcr.microsoft.com/playwright/mcp`.

## Test stack

### No tests / not surfaced

`.github/workflows` present; specific test setup not deeply extracted. Playwright's own test harness likely used given project heritage.

## CI

### GitHub Actions

GitHub Actions present; 60 releases indicate an active release pipeline.

### Release-cut workflow on tag push

Active release pipeline pushing tagged releases.

## Observability

### None / unspecified

`--init-script` lets users inject instrumentation; tracing and video are capability toggles rather than observability per se. Project-level shaping not documented.

## Safety and security posture

### Explicit non-security stance

README states "Playwright MCP is not a security boundary"; `--allow-unrestricted-file-access` is documented as the escape hatch. The project opts out of enforcement and signals risky modes deliberately.

### Capability-scoped tool exposure (install-time)

Risky tool families (vision-coordinate clicks, PDF generation, testing-mode assertions) are gated behind `--caps=<group>` opt-in. Server runs without them by default.

## Host integration

### Per-host README JSON snippets

Documented support for 20+ MCP-aware hosts/agents: Claude Desktop, Claude Code, VS Code, Cursor, Windsurf, Cline, Goose, Junie, Copilot, Factory, Gemini CLI, LM Studio, Kiro, opencode, Qodo Gen, Warp, Codex, Antigravity, Amp. Same JSON snippet pattern shared across hosts (stdio command + args). No host-specific plugin wrapper in repo.

### Multi-host catalog (30+ agents)

20+ different agent platforms documented with config snippets; the server is generic enough to not depend on host-specific features.

## Repository layout

### Monorepo of independent servers

Monorepo with `/packages` directory.

## Developer ergonomics

### Programmatic embedding API

`createConnection()` enables embedding the server inside another Node process as a library. First-class non-subprocess integration path.

## Documentation surface

### README as the canonical surface

README primary; CONTRIBUTING.md and SECURITY.md alongside.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0 license.

### Active development

60 releases; active release pipeline; v0.0.70 released 2026-04-01.

### Tagged release with version in changelog

Standard semver tags (v0.0.70).

## Claude Code plugin / skill wrapper

### Bare MCP server, no Claude Code wrapper

No `.claude-plugin/` directory observed in fetched view.
