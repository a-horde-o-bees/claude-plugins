# Sample

Mirrors of `https://github.com/docker/hub-mcp`. Docker Hub MCP server — TypeScript with declarative tool catalog (`tools.json` / `tools.txt`); integrates with Docker's Ask Gordon agent via `gordon-mcp.yml`. 137 stars, Apache-2.0, default branch `main`, active (7 open PRs noted; last-commit not explicitly extracted).

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (99.8%) on Node.js 22+. Specific framework not directly confirmed but typical `@modelcontextprotocol/sdk` for TS MCP servers.

## Transport

### Streamable HTTP

`--transport=http` selectable; `--port` sets HTTP port (default 3000).

### stdio

`--transport=stdio` selectable.

### Selection mechanism

CLI flag at startup — `--transport=http|stdio`, `--port=3000`. Transport is a first-class CLI flag with an explicit default rather than separate entry-point commands per transport.

## Capability surface

### Tool catalog as data file

Tools defined in `tools.json` / `tools.txt` — declarative catalog rather than inline schemas in source. Opens an authoring path that doesn't require TS expertise. Specific tool list not enumerated in fetched view; scope is Docker Hub operations.

## Configuration delivery

### Environment variables

`HUB_PAT_TOKEN` for authentication credential.

### CLI flags

`--transport`, `--port`, `--username`. Plus `tools.json`/`tools.txt` shipping tool definitions.

## Authentication

### Static API key / token via env var

Static Docker Hub Personal Access Token (PAT) supplied via `HUB_PAT_TOKEN` env var; paired with `--username` CLI arg.

## Multi-tenancy

### Single-user / single-tenant per process

One PAT plus username — single user per process.

## Distribution channel

### npm via npx / bunx

Appears published to npm based on install flow (specific package name not extracted from README). `npm install && npm run build && npm start -- ...` for source clone build flow.

### Docker / OCI image

Dockerfile present.

### Source clone with editable install

`npm install && npm run build && npm start -- [--transport=http|stdio] [--port=3000]`.

## Entry point and launch

### Built JS file (`node build/index.js`)

`dist/index.js` as the built entry point; `npm start -- ...` or direct execution after build.

### npm scripts (start/start:stdio/start:http)

`npm start -- ...` with transport flags forwarded.

## Build and packaging

### npm/Node toolchain

`package.json`, `tsconfig.json`, ESLint config (`eslint.config.mjs`). TypeScript compiled to a built JS output.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present. No compose/Helm.

## CI

### GitHub Actions

`.github/` present; specific workflow contents not extracted.

## Host integration

### Claude Desktop

JSON snippet via `claude_desktop_config.json`.

### VS Code / VS Code Insiders / Visual Studio family

JSON snippet via User Settings JSON.

### Vendor-specific companion config

`gordon-mcp.yml` — first-party Docker "Ask Gordon" integration. The MCP server pre-shapes its config for a first-party downstream tool, distinct from generic host config.

## Repository layout

### Single-package source (language-conventional)

Single-package TS project: `src/`, `Dockerfile`, `package.json`, `tsconfig.json`, `tools.json`, `tools.txt`, `eslint.config.mjs`.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

Apache-2.0.

### Active development

Active — 7 open PRs noted.
