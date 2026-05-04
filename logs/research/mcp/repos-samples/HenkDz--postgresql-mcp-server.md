# Sample

Mirrors of `https://github.com/HenkDz/postgresql-mcp-server`. PostgreSQL MCP server — 17 consolidated meta-tools (down from 46 atomic tools) covering CRUD/SQL execution, schema analysis, and monitoring. 178 stars, AGPLv3, default branch `main`, 33 total commits.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (96.6%) on the Anthropic MCP TypeScript SDK; Node.js runtime.

## Transport

### stdio

Default; Node executable launched by host. No alternative transport documented.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

17 tools organized into 3 categories — 8 consolidated meta-tools, 4 CRUD/SQL execution tools, 5 specialized analysis/monitoring tools.

### Tool consolidation as design pressure

Originally 46 atomic tools, consolidated down to 17 meta-tools as an explicit design response to LLM discovery and parameter-validation pressure — too many narrow tools confuse model selection; broader meta-tools with more parameters work better.

### Tool catalog as data file

`POSTGRES_TOOLS_CONFIG` env var pointing at a `tools.json` config file enables per-tool enablement — explicit surface-reduction knob rather than requiring code fork.

## Configuration delivery

### CLI flags

`--connection-string` flag.

### Environment variables

`POSTGRES_CONNECTION_STRING` and `POSTGRES_TOOLS_CONFIG`.

### Per-tool enablement file

Optional `tools.json` config file (referenced by `POSTGRES_TOOLS_CONFIG` env var) toggles individual tools on/off.

### Connection URI scheme

`POSTGRES_CONNECTION_STRING` packs host, port, credentials, and TLS into one URL.

## Authentication

### Database connection string

Standard PostgreSQL authentication; credentials embedded in connection string (`user:password@host:port/database`), supplied via `--connection-string` flag or `POSTGRES_CONNECTION_STRING` env var.

## Multi-tenancy

### Single connection per server instance

Single connection per server instance; no per-request tenant switching documented.

## Distribution channel

### npm via npx / bunx

Published as `@henkey/postgres-mcp-server`. `npm install -g @henkey/postgres-mcp-server` for global install; `npx @henkey/postgres-mcp-server` for direct launch.

### Smithery registry

`npx -y @smithery/cli install @HenkDz/postgresql-mcp-server` — Smithery-mediated install.

### Docker / OCI image

`docker pull henkey/postgres-mcp:latest` from Docker Hub.

### Source clone with editable install

Git clone documented as alternative.

## Entry point and launch

### Built JS file (`node build/index.js`)

Node executable `/build/index.js` invoked via npx or docker, with connection-string argument. npm bin entry; Docker entrypoint script.

## Build and packaging

### npm/Node toolchain

`package.json` defines build and bin entries; npm registry is the publish target. TypeScript compiled to a `build/` JS output.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root with entrypoint script.

### Published Docker image

Pre-built image at Docker Hub (`henkey/postgres-mcp`).

## CI

### GitHub Actions

`.github/workflows/` present; specific workflows not extracted within budget.

## Host integration

### Claude Desktop

JSON config example provided.

### Cursor

Documented as an MCP client target.

### Smithery / Glama discovery

`@smithery/cli install` command documented for cross-host install.

## Repository layout

### Single-package source (language-conventional)

Single-package TypeScript project (`src/`, `docs/`, `.github/workflows/`, `build/`).

## Documentation surface

### README plus docs directory

`docs/` directory present alongside README.md.

## Release and lifecycle

### License — Copyleft (AGPL-3.0)

AGPLv3 license — uncommon for MCP servers (most are MIT/Apache). Carries network-copyleft implications for hosts embedding the server in a hosted product: derivative works distributed over a network must remain open. Distinct from MIT/Apache (no copyleft) and CC BY-NC-SA (forbids commercial use); AGPLv3 permits commercial adoption but ties the source-disclosure obligation to network use as well as redistribution.

## Extension points

### Per-tool enablement file

`tools.json` config file (referenced by `POSTGRES_TOOLS_CONFIG` env var) toggles individual tools without code changes — lets deployers shrink the LLM-visible surface for safety or focus, and lets the same server image serve multiple deployment profiles.
