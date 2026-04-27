# Sample

## Identification

### url

https://github.com/HenkDz/postgresql-mcp-server

### stars

178

### last-commit

33 total commits; exact date not surfaced from landing page.

### license

AGPLv3

### default branch

main

### one-line purpose

PostgreSQL MCP server — 17 consolidated meta-tools (down from 46 atomic tools) covering CRUD/SQL execution, schema analysis, and monitoring.

## 1. Language and runtime

### language(s) + version constraints

TypeScript (96.6%), Node.js runtime.

### framework/SDK in use

Anthropic MCP TypeScript SDK.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio (Node executable launched by host).

### how selected

Default stdio; no alternative transport documented.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

npm (global or npx), Smithery registry, Docker image (Docker Hub), Git clone.

### published package name(s)

@henkey/postgres-mcp-server

### install commands shown in README

`npm install -g @henkey/postgres-mcp-server`; `npx @henkey/postgres-mcp-server`; `npx -y @smithery/cli install @HenkDz/postgresql-mcp-server`; `docker pull henkey/postgres-mcp:latest`.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

Node executable `/build/index.js` invoked via npx or docker, with connection-string argument.

### wrapper scripts, launchers, stubs

Docker entrypoint script; npm bin entry.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

CLI flag `--connection-string`; environment variables `POSTGRES_CONNECTION_STRING` and `POSTGRES_TOOLS_CONFIG`; optional `tools.json` config file for per-tool enablement.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

Standard PostgreSQL authentication.

### where credentials come from

Embedded in connection string (`user:password@host:port/database`), supplied via flag or env var.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

Single connection per server instance; no per-request tenant switching documented.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

17 tools organized into 3 categories — 8 consolidated meta-tools, 4 CRUD/SQL execution tools, 5 specialized analysis/monitoring tools. Originally 46 tools, consolidated down.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Not surfaced in README within budget.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Desktop

JSON config example provided.

### Cursor

Documented as an MCP client target.

### Other editors/CLIs

Not explicitly mentioned.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not present.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

Not explicitly surfaced within budget.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

`.github/workflows/` present; specific workflows not extracted within budget.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present, entrypoint script, published image on Docker Hub (`henkey/postgres-mcp`).

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Claude Desktop JSON config; Smithery CLI recipe; `docs/` directory present.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

Single-package TypeScript project (`src/`, `docs/`, `.github/workflows/`, `build/`).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Tool consolidation from 46 atomic tools to 17 meta-tools as an explicit design response to LLM discovery and parameter-validation pressure. `POSTGRES_TOOLS_CONFIG` / `tools.json` enables per-tool enablement — explicit surface-reduction knob. Docker-first packaging alongside npm.

## 18. Unanticipated axes observed

Per-tool configuration via a separate JSON config is an unusual explicit axis — most servers either expose all tools or require a code fork. AGPLv3 license is uncommon for MCP servers; most are MIT/Apache — has copyleft implications for hosts embedding it.

## 20. Gaps

Exact last-commit date not surfaced. Test framework and specific CI workflows not extracted within budget. Logging/observability details not surfaced.
