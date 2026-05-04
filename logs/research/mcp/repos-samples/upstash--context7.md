# Sample

Mirrors of `https://github.com/upstash/context7`. Context7 documentation-context MCP server — vendor-hosted endpoint at `https://mcp.context7.com/mcp` backed by a private API/parsing/crawling pipeline; the public repo carries a Node monorepo for the CLI, plugin metadata, skills, and rules. 53,300 stars, MIT, default branch `master`.

## Server runtime

### TypeScript on Node with monorepo tooling

TypeScript (91.2%) + JavaScript (8.5%) Node.js monorepo built on pnpm workspaces. Multiple packages (CLI, plugins, skills, rules, docs) coexist under one repo. The MCP server itself is hosted; the public repo ships the npm CLI and integration metadata.

### Remote HTTP service (no local runtime)

The runtime lives on a vendor-hosted endpoint (`https://mcp.context7.com/mcp`) — no local language or framework executes on the user's machine. Backend architecture (API, parsing, crawling) is intentionally private; the public repo carries only client-side code and configs.

## Transport

### Hosted remote endpoint (vendor-operated)

`https://mcp.context7.com/mcp` is the canonical MCP endpoint; the host is configured to point at the URL rather than launching anything locally. OAuth at the HTTP boundary; rate limits and tenant scoping enforced server-side.

### Selection mechanism

Implicit single mode — hosted HTTP endpoint only.

## Capability surface

### Tools plus resources

Tools include `resolve-library-id` and `query-docs` (retrieves version-specific documentation from source). Resources back the surface as a library index and documentation cache.

### Bundled "agent SOPs" / vertical skill packs

A `skills/` folder ships alongside the MCP server, providing opinionated workflow content beyond raw tools. A `rules/` folder ships parallel rule content.

## Configuration delivery

### Hosted endpoint as primary delivery

Configuration is the host's JSON snippet pointing at `https://mcp.context7.com/mcp`. The server itself has near-zero local config.

### Host-side JSON config snippet

Manual setup uses a generic `mcpServers` JSON entry pointing at the endpoint URL with `CONTEXT7_API_KEY` header.

## Authentication

### OAuth setup-wizard flow

`npx ctx7 setup` walks the user through OAuth and writes the resulting credentials into the host's config file. Removes manual JSON editing for users; per-user identity rather than per-process.

### API key (optional, for higher rate limits)

Free API-key registration at `context7.com/dashboard` is optional and lifts rate limits. Key passed via `CONTEXT7_API_KEY` header for manual setup paths.

## Multi-tenancy

### Per-user / per-workspace via OAuth

Per-user OAuth token tied to upstream account; API key per workspace. Hosted deployment maintains per-connection identity via OAuth.

## Distribution channel

### npm via npx / bunx

`npx ctx7 setup` is the canonical install/setup path — single one-liner that handles OAuth and credential bootstrap. Published as `@upstash/context7` (monorepo).

### Hosted endpoint (no install)

`https://mcp.context7.com/mcp` — manual config path where the user pastes the URL into their host's MCP config without npm involvement. Vendor runs the runtime; patches propagate without user redeploys.

### Configs-only repo (no server artifact)

The public repo's distribution role is shipping client config snippets, OAuth bootstrap, plugins, skills, and rules — the actual server is hosted remotely by the vendor.

### `.claude-plugin/marketplace.json`

Marketplace metadata file shipped in-repo so the project surfaces in Claude's plugin marketplace. Distinct from a full plugin.json — marketplace discovery without installing as a plugin.

## Entry point and launch

### URL configuration (no local launch)

For end users using the hosted endpoint, the entry point is the URL itself — no local launch.

### `npx -y <package>` / `bunx`

`npx ctx7 setup`, `ctx7 library <name> <query>`, `ctx7 docs <libraryId> <query>` — npm-distributed CLI commands for OAuth setup and direct documentation queries.

## Build and packaging

### npm/Node toolchain

`package.json` defines build/publish; pnpm workspaces orchestrate the monorepo. Configuration via `pnpm-workspace.yaml`, `tsconfig.json`, `eslint.config.js`, `prettier.config.mjs`. Changesets handle coordinated release versioning.

## Container artifacts

### No container artifacts

No Dockerfile at root — runtime is hosted; users don't run a local server.

## Test stack

### No tests / not surfaced

Test framework details not extracted from public README; monorepo `npm run test` referenced but specifics private.

## CI

### GitHub Actions

`.github/` directory present; lint and format scripts (`npm run lint`, `npm run format`) run as CI steps.

## Host integration

### Claude Code

Native support documented; hosted MCP endpoint configurable via standard `.mcp.json` or via `npx ctx7 setup`.

### Cursor

Listed as a supported agent.

### Codex CLI / Copilot CLI / Gemini CLI

OpenAI Code listed as a supported agent — non-Anthropic agent CLIs that consume MCP.

### Multi-host catalog (30+ agents)

README documents support for 30+ different agent platforms with per-agent config snippets — the server is generic enough not to depend on host-specific features.

### Smithery / Glama discovery

Smithery registry config supported.

### Inspector compatibility called out

MCP Inspector support documented as a verification surface.

## Observability

### None / unspecified

Logging and observability strategy not documented in public README.

## Repository layout

### Monorepo with multiple published packages

Multiple publishable packages coexist in one repo coordinated by `pnpm-workspace.yaml`; changesets handles version bumps and changelog generation. Expanded layout includes `/packages`, `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n` directories. The "MCP plus other agent-integration surfaces" pattern.

## Claude Code plugin / skill wrapper

### `.claude-plugin/marketplace.json` only

Marketplace discovery metadata in `.claude-plugin/marketplace.json` without a full plugin.json. Lets the project surface in Claude's marketplace UI without becoming a full installable plugin — discovery hook on top of the existing hosted MCP server.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT — vendor-authored (Upstash) project optimized for adoption.

### Vendor-internal release (no public pipeline)

The public repo has the npm CLI release pipeline; the actual MCP server's deploy pipeline is invisible — vendor's internal infrastructure handles backend evolution.
