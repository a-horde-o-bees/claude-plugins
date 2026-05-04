# Sample

Mirrors of `https://github.com/idosal/git-mcp`. Hosted git-documentation MCP service — cloud-hosted SaaS endpoint at `gitmcp.io/{owner}/{repo}`, zero-auth public service, parameterized per-repo. 8,000 stars, Apache-2.0, default branch `main`, last commit March 13, 2026.

## Server runtime

### TypeScript on Cloudflare Workers (V8 isolate)

TypeScript/JavaScript on Cloudflare Workers (Wrangler). React Router 7, Vite, MCP SDK. Edge/serverless deployment model.

## Transport

### Streamable HTTP

HTTP/HTTPS at the cloud endpoint `gitmcp.io`.

### SSE (Server-Sent Events)

SSE supported alongside Streamable HTTP.

### Selection mechanism

Implicit default — auto-detected by IDE via direct HTTP URL specification (`https://gitmcp.io/{owner}/{repo}`).

## Capability surface

### Tools-only, hand-curated narrow surface

Tools — `fetch_<repo-name>_documentation`, `search_<repo-name>_documentation`, `search_<repo-name>_code`, `fetch_url_content`. Tool names are parameterized by the repo path in the URL.

## Configuration delivery

### Host-side JSON config snippet

IDE JSON `mcp.json` configs documented for Cursor, Claude Desktop, Windsurf, VSCode, Cline, Highlight AI, Augment Code, Msty AI.

### Hosted endpoint as primary delivery

Dynamic endpoint shape `gitmcp.io/{owner}/{repo}` — the URL itself carries the per-repo configuration.

## Authentication

### None / implicit (local-resource gating)

None required; zero-auth public service for public repos.

## Multi-tenancy

### Per-request tenant via URL parameter

Per-repository tenant parameterized by `owner/repo` in the URL path. Cloud-hosted single service with multi-repo support — one deployment serves every GitHub repo.

### Stateless read-only (any number of instances)

Stateless read-only against public GitHub repos — credential-free, any number of instances can serve simultaneously.

## Distribution channel

### Hosted endpoint (no install)

Cloud-hosted at `gitmcp.io` — no install required.

### Source clone with editable install

Self-hosted option via `pnpm install`, `npm run dev` for development.

## Entry point and launch

### URL configuration (no local launch)

Hosts point at `https://gitmcp.io/{owner}/{repo}`.

### Stdio-to-HTTP shim on the client side

`npx mcp-remote https://gitmcp.io/{owner}/{repo}` — `mcp-remote` (npm) shim translates stdio (what the host knows how to spawn) into HTTP requests against the remote URL.

### Built JS file (`node build/index.js`)

Self-host path: `npm run dev` / `pnpm dev` for local Wrangler dev server.

## Build and packaging

### Wrangler bundle (Cloudflare Workers)

Built with Wrangler for Cloudflare Workers deployment; `wrangler.jsonc` config.

### npm/Node toolchain

`package.json`-based Node toolchain; no npm registry publication observed.

## Test stack

### End-to-end with browser automation

Playwright E2E (`playwright.config.ts`).

### Vitest (TypeScript / Node)

Vitest unit tests (`vitest.config.ts`); `npm run test` runs the suite.

## CI

### GitHub Actions

GitHub Actions: `e2e-tests.yml`, `run-tests.yml`.

## Container artifacts

### Cloudflare Workers config

No Dockerfile — Cloudflare Workers cloud-native deployment via `wrangler.jsonc`.

## Host integration

### Claude Desktop

JSON `mcp.json` config documented in README.

### Cursor

JSON `mcp.json` config documented in README.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Windsurf, Cline, Augment Code documented with `mcp.json` config snippets.

### VS Code / VS Code Insiders / Visual Studio family

VSCode `mcp.json` config documented in README.

### Multi-host catalog (30+ agents)

Per-host `mcp.json` snippets for: Claude Desktop, Cursor, Windsurf, VSCode, Cline, Highlight AI, Augment Code, Msty AI.

## Repository layout

### Hosted-service layout (Next.js app + mcp-src + lib)

Single-package React/TS with Cloudflare integration. Dirs: `.github/`, `.husky/`, `.react-router/`, `app/`, `src/`, `static/`, `tests/`, `dist/`. Config: `wrangler.jsonc`, `react-router.config.ts`, `vite.config.ts`, `vitest.config.ts`.

## Deployment topology

### Edge / serverless deployment (Cloudflare Workers, V8 isolate)

Hosted as a Cloudflare Workers deployment — V8-isolate edge runtime.

### Hosted SaaS endpoint

`gitmcp.io` is the canonical public endpoint.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0 license.

### Active development

Last commit March 13, 2026.

## Developer ergonomics

### Linter and type-checker stack

Biome for unified linting/formatting.

### `scripts/` directory

React Router dev scripts; Wrangler for Cloudflare Workers deployment.

## Documentation surface

### Per-host README integration sections

Per-host `mcp.json` config sections for every supported client.
