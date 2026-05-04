# Sample

Mirrors of `https://github.com/GLips/Figma-Context-MCP`. Figma design-context MCP server — parses Figma URLs and extracts layout/styling metadata as structured context for code-generating AI agents. 14.4k stars, MIT, default branch `main`, latest release v0.10.1 (April 10, 2026). Effectively the canonical community Figma MCP server despite being unofficial; no first-party Figma-org repo surfaced. Marketing framing "Give your coding agent access to your Figma data" positions it as a design-to-code accelerator rather than a general Figma CRUD server.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (96.3%) on the canonical `@modelcontextprotocol/sdk`; Node.js runtime (implied — uses npx and pnpm). Build via tsup. Specific Node engines constraint not extracted within budget.

## Transport

### stdio

Selectable via `--stdio` CLI flag.

### Streamable HTTP

HTTP/SSE server mode also referenced — standalone server with `PORT` env var. Selected by omitting `--stdio` and supplying a `PORT` env var or port flag.

### Selection mechanism

CLI flag at startup — `--stdio` boolean; otherwise HTTP mode via `PORT` env var or port flag.

## Capability surface

### Tools-only, hand-curated narrow surface

Tools for parsing Figma file/frame/group URLs, extracting layout and styling metadata, and contextualizing design data for code generation. The server's job is scope-narrow — it turns Figma URLs into structured design context; it does not perform writes to Figma, sidestepping OAuth scope-escalation concerns.

## Configuration delivery

### Environment variables

`FIGMA_API_KEY`, `PORT`.

### CLI flags

`--figma-api-key`, `--stdio`, port flag.

### Host-side JSON config snippet

Host-level JSON config file for MCP clients (`.cursor/mcp.json`, Claude Desktop config) provides the launch command.

## Authentication

### Static API key / token via env var

Static Figma personal access token supplied via CLI flag (`--figma-api-key`) or environment variable (`FIGMA_API_KEY`); no OAuth flow. User generates the token via Figma's account token-management UI.

## Multi-tenancy

### Single-user / single-tenant per process

Token is process-scoped. A given launch serves one Figma identity; no per-request switching observed.

## Distribution channel

### npm via npx / bunx

Published to npm as `figma-developer-mcp`. Primary install command: `npx -y figma-developer-mcp --figma-api-key=YOUR-KEY --stdio`. Windows wraps in `cmd /c`.

## Entry point and launch

### `npx -y <package>` / `bunx`

`npx -y figma-developer-mcp --figma-api-key=YOUR-KEY --stdio` (macOS/Linux); Windows wraps in `cmd /c`. npm `bin` entry; tsup-built CLI; no separate launcher scripts.

## Build and packaging

### npm/Node toolchain

`package.json` defines build and bin entries; npm registry is the publish target. Build via tsup producing a CLI artifact. pnpm-managed.

## Test stack

### Vitest (TypeScript / Node)

vitest configured. Specific location/coverage not extracted.

## CI

### GitHub Actions

GitHub Actions workflows present; specific triggers and jobs not extracted within budget.

## Host integration

### Cursor

Primary target; featured prominently in the README.

### Claude Desktop

Referenced via MCP JSON config.

### Generic / host-agnostic snippet

General MCP-compatible clients via stdio.

## Repository layout

### Single-package source (language-conventional)

Single-package — `/src`, `/scripts`, `tsconfig.json`, `eslint.config.js` at root; pnpm-managed.

## Developer ergonomics

### Linter and type-checker stack

ESLint + Prettier signal an opinionated dev environment; consumers building plugins on top should expect pnpm workflows.

### `pre-commit` framework

lefthook for git hooks.

### Sample MCP client configs in repo

Sample Cursor and Claude Desktop configs in README; pnpm scripts for dev/build.

## Documentation surface

### README as the canonical surface

README is the canonical documentation surface; per-host integration sections inside it.

### Per-host README integration sections

README has labeled sections per supported host (Cursor primary, Claude Desktop secondary, generic stdio).
