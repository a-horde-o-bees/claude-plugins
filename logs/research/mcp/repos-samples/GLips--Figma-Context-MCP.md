# Sample

## Identification

### url

https://github.com/GLips/Figma-Context-MCP

### stars

14.4k

### last-commit

Latest release v0.10.1, April 10, 2026.

### license

MIT

### default branch

main

### one-line purpose

Figma design-context MCP server — parses Figma URLs and extracts layout/styling metadata as structured context for code-generating AI agents.

## Language and runtime

### language(s) + version constraints

TypeScript (96.3%); Node.js runtime (implied — uses npx and pnpm); specific Node engines constraint not extracted within budget.

### framework/SDK in use

Model Context Protocol SDK (the canonical `@modelcontextprotocol/sdk` typescript SDK); build via tsup.

## Transport

### supported transports

stdio; HTTP/SSE server mode also referenced (standalone server with PORT env var).

### how selected

`--stdio` CLI flag selects stdio; omission plus a `PORT` env var or port flag selects HTTP mode.

## Distribution

### every mechanism observed

npm (primary), npx execution, Cursor IDE configuration snippets.

### published package name(s)

figma-developer-mcp

### install commands shown in README

`npx -y figma-developer-mcp --figma-api-key=YOUR-KEY --stdio`

## Entry point / launch

### command(s) users/hosts run

`npx -y figma-developer-mcp --figma-api-key=YOUR-KEY --stdio` (macOS/Linux); Windows wraps in `cmd /c`.

### wrapper scripts, launchers, stubs

npm `bin` entry; tsup-built CLI; no separate launcher scripts observed.

## Configuration surface

### how config reaches the server

CLI flags (`--figma-api-key`, `--stdio`, port flag); environment variables (`FIGMA_API_KEY`, `PORT`); host-level JSON config file for MCP clients.

## Authentication

### flow

Static Figma personal access token supplied via CLI flag or environment variable; no OAuth flow.

### where credentials come from

User generates token via Figma's account token-management UI and passes it at launch.

## Multi-tenancy

### tenancy model

Single-user — token is process-scoped. A given launch serves one Figma identity; no per-request switching observed.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools for parsing Figma file/frame/group URLs, extracting layout and styling metadata, and contextualizing design data for code generation. Designed as the bridge that turns a Figma link into structured design context an AI coder can consume.

## Observability

### logging destination + format, metrics, tracing, debug flags

Not explicitly extracted within budget — likely stderr logging in stdio mode, but not confirmed.

## Host integrations shown in README or repo

### Cursor IDE

Primary target, featured prominently.

### Claude Desktop

Referenced via MCP JSON config.

### General MCP-compatible clients

Via stdio.

## Claude Code plugin wrapper

### presence and shape

Not present — no `.claude-plugin` directory observed in repo layout.

## Tests

### presence, framework, location, notable patterns

Present — vitest configured; specific location/coverage not extracted within budget.

## CI

### presence, system, triggers, what it runs

Present — GitHub Actions workflows exist; specific triggers and jobs not extracted within budget.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Not observed within budget.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

pnpm scripts for dev/build; lefthook for git hooks; ESLint + Prettier; sample Cursor and Claude Desktop configs in README.

## Repo layout

### single-package / monorepo / vendored / other

Single-package — `/src`, `/scripts`, tsconfig.json, eslint.config.js at root; pnpm-managed.

## Notable structural choices

TypeScript-heavy (96%) with tsup for build — typical modern TS CLI scaffolding. pnpm + lefthook + ESLint + Prettier signals an opinionated dev environment; consumers building plugins on top should expect pnpm workflows. The server's job is scope-narrow — it turns Figma URLs into structured context; it does not perform writes to Figma, which sidesteps OAuth scope-escalation concerns.

## Unanticipated axes observed

14.4k stars and 1.1k forks make this the dominant community Figma MCP — effectively canonical despite being unofficial. No first-party figma-org repo was surfaced in this research window. Marketing framing "Give your coding agent access to your Figma data" positions it as a design-to-code accelerator rather than a general Figma CRUD server.

## Gaps

Exact Node engines constraint, precise CI workflow triggers, and logging format not confirmed within budget. Whether the repo intends a future HTTP-only mode (given PORT env var) or leaves HTTP secondary to stdio is not documented in the extracted content.
