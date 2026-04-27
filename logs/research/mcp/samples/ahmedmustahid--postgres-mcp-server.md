# Sample

## Identification

### url

https://github.com/ahmedmustahid/postgres-mcp-server

### stars

30

### last-commit

Not surfaced from landing page within budget.

### license

MIT

### default branch

main

### one-line purpose

PostgreSQL read-only MCP server — exposes tables and schema as resources and runs read-only SQL queries over stdio or Streamable HTTP.

## Language and runtime

### language(s) + version constraints

TypeScript (71.8%), JavaScript, Node.js; a `pyproject.toml` is also present suggesting a secondary Python surface.

### framework/SDK in use

Anthropic MCP TypeScript SDK (StreamableHTTPServerTransport, StdioServerTransport).

## Transport

### supported transports

HTTP (streamable) and stdio.

### how selected

Positional subcommand — `npx @ahmedmustahid/postgres-mcp-server` (HTTP default) vs `npx @ahmedmustahid/postgres-mcp-server stdio`.

## Distribution

### every mechanism observed

npm (npx), Docker, Podman.

### published package name(s)

@ahmedmustahid/postgres-mcp-server

### install commands shown in README

`npx @ahmedmustahid/postgres-mcp-server`; `npx @ahmedmustahid/postgres-mcp-server stdio`.

## Entry point / launch

### command(s) users/hosts run

`npx @ahmedmustahid/postgres-mcp-server [stdio]`.

### wrapper scripts, launchers, stubs

Dockerfile and docker-compose.yml; Makefile.

## Configuration surface

### how config reaches the server

Environment variables via `.env` — `POSTGRES_USERNAME`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_DATABASE`, `POSTGRES_URL`, `PORT` (default 3000), `HOST`, `NODE_ENV`, `CORS_ORIGIN`.

## Authentication

### flow

Standard PostgreSQL authentication via credentials in env vars.

### where credentials come from

`.env` file / environment variables.

## Multi-tenancy

### tenancy model

Single database per server; HTTP transport supports stateful sessions but not per-request tenant switching.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Resources — "Database Tables" (public-schema listing), "Database Schema" (column info). Tool — read-only SQL query execution.

## Observability

### logging destination + format, metrics, tracing, debug flags

`--verbose` flag available.

## Host integrations shown in README or repo

### Claude Desktop

Supported with JSON config example.

### MCP Inspector

Explicitly referenced.

### Other editors/CLIs

Not mentioned.

## Claude Code plugin wrapper

### presence and shape

Not present.

## Tests

### presence, framework, location, notable patterns

Not detailed in README within budget.

## CI

### presence, system, triggers, what it runs

Not detailed in README within budget.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile and docker-compose.yml present; Podman also called out.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Makefile present; Claude Desktop config example; "Show sales table from last year" example query.

## Repo layout

### single-package / monorepo / vendored / other

Mixed single-package — primarily Node/TS (`src/`, `package.json`) with a sibling `pyproject.toml` and `images/` directory.

## Notable structural choices

Dual transport (HTTP streamable + stdio) in one package with subcommand selection. Graceful shutdown and error handling highlighted in README. Presence of both `package.json` and `pyproject.toml` in a TS-majority repo is unusual — possibly a parallel Python variant or docs-generation tool.

## Unanticipated axes observed

CORS origin configuration surfaces at the MCP layer, which is HTTP-transport-specific and rare. Explicit HTTP session statefulness as a design axis.

## Gaps

Last-commit date not surfaced. Tests and CI details not extracted within budget. Purpose of `pyproject.toml` in a TS-dominant repo not explained in README.
