# Sample

## Identification

### url

https://github.com/docker/hub-mcp

### stars

137

### last-commit

Not explicitly extracted; active (7 open PRs noted)

### license

Apache-2.0

### default branch

main

### one-line purpose

Docker Hub MCP server (TypeScript) — tool catalog declared in `tools.json` for image discovery; integrates with Docker's Ask Gordon agent via `gordon-mcp.yml`.

## Language and runtime

### language(s) + version constraints

TypeScript (99.8%). Requires Node.js 22+.

### framework/SDK in use

Not explicitly extracted; likely `@modelcontextprotocol/sdk` (typical for TS MCP servers).

## Transport

### supported transports

HTTP, stdio.

### how selected

CLI flag `--transport=http|stdio`; `--port` sets HTTP port (default 3000).

## Distribution

### every mechanism observed

npm package; Dockerfile present; source clone/build.

### published package name(s)

Not explicitly extracted from README; appears published to npm based on install flow.

### install commands shown in README

`npm install && npm run build && npm start -- [--transport=http|stdio] [--port=3000]`

## Entry point / launch

### command(s) users/hosts run

`npm start -- ...` or direct execution of `dist/index.js` after build.

### wrapper scripts, launchers, stubs

`dist/index.js` as the built entry point.

## Configuration surface

### how config reaches the server

Env vars (`HUB_PAT_TOKEN`) plus CLI args (`--transport`, `--port`, `--username`). `tools.json` and `tools.txt` ship tool definitions.

## Authentication

### flow

Static Docker Hub Personal Access Token (PAT).

### where credentials come from

`HUB_PAT_TOKEN` env var; paired with `--username` CLI arg.

## Multi-tenancy

### tenancy model

Single-user per process (one PAT plus username).

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools defined in `tools.json`. Specific tool list not enumerated in fetched view. Scope: Docker Hub operations.

## Observability

### logging destination + format, metrics, tracing, debug flags

Not extracted.

## Host integrations shown in README or repo

### Claude Desktop

JSON snippet via `claude_desktop_config.json` (README section).

### VS Code

JSON snippet via User Settings JSON.

### Docker Ask Gordon

`gordon-mcp.yml` config file.

## Claude Code plugin wrapper

### presence and shape

Not observed in root listing.

## Tests

### presence, framework, location, notable patterns

Test files not explicitly called out in fetched view; ESLint config present.

## CI

### presence, system, triggers, what it runs

GitHub Actions present (`.github/`); specifics not extracted.

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile. No compose/Helm.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`tools.json` as a declarative tool manifest. Standard npm scripts.

## Repo layout

### single-package / monorepo / vendored / other

Single-package TS project. `src/`, `Dockerfile`, `package.json`, `tsconfig.json`, `tools.json`, `tools.txt`, `eslint.config.mjs`.

## Notable structural choices

Tools defined in a separate `tools.json` / `tools.txt` pair — declarative catalog rather than inline schemas in source. First-party Docker "Ask Gordon" integration (`gordon-mcp.yml`) — repo targets Docker's own agent surface alongside generic MCP hosts. Transport is a first-class CLI flag with an explicit default rather than separate entry-point commands (contrast with github-mcp-server's subcommand approach).

## Unanticipated axes observed

Vendor-specific companion integration (`gordon-mcp.yml`) — MCP server pre-shaping its config for a first-party downstream tool, distinct from generic host config. Tool catalog as data file (`tools.json`/`tools.txt`) rather than code — opens an authoring path that doesn't require TS expertise.

## Gaps

Last-commit date. Exact npm package name if published. Tool enumeration / total tool count. Test framework and coverage. Whether the HTTP transport is Streamable HTTP, SSE, or plain JSON-RPC-over-HTTP.
