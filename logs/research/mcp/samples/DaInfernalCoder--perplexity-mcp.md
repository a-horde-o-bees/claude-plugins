# Sample

## Identification

### url

https://github.com/DaInfernalCoder/perplexity-mcp

### stars

289

### last-commit

November 1, 2025 ("Reasoning and Chat History")

### license

MIT

### default branch

main

### one-line purpose

Perplexity search MCP server — exposes `search`, `reason`, `deep_research` tools with auto-complexity routing to Sonar Pro / Sonar Reasoning / Sonar Deep Research.

## Language and runtime

### language(s) + version constraints

JavaScript (94.7%), Dockerfile (5.3%); Node.js required.

### framework/SDK in use

MCP SDK, Anthropic Claude Agent SDK.

## Transport

### supported transports

HTTP (inferred from Anthropic Agent SDK usage).

### how selected

not explicitly documented

## Distribution

### every mechanism observed

npx (recommended), source clone.

### published package name(s)

`perplexity-mcp` via `npx -y perplexity-mcp`.

### install commands shown in README

`npx -y perplexity-mcp` (recommended) or git clone + `npm install`.

## Entry point / launch

### command(s) users/hosts run

`npx -y perplexity-mcp`

### wrapper scripts, launchers, stubs

none documented; direct npx invocation.

## Configuration surface

### how config reaches the server

`.env` file, CLI args (`--api-key`), `--cwd` parameter for .env path.

## Authentication

### flow

API key (PERPLEXITY_API_KEY). Priority: CLI arg > env var > .env file.

### where credentials come from

CLI, environment, or `.env`.

## Multi-tenancy

### tenancy model

per-request context; assumes single-agent invocation.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools: `search` (Sonar Pro), `reason` (Sonar Reasoning Pro), `deep_research` (Sonar Deep Research). Optional `force_model` parameter to override auto-complexity detection.

## Observability

### logging destination + format, metrics, tracing, debug flags

not documented

## Host integrations shown in README or repo

MCP config files mentioned in generic terms; specifics not detailed.

## Claude Code plugin wrapper

### presence and shape

not present

## Tests

### presence, framework, location, notable patterns

not documented

## CI

### presence, system, triggers, what it runs

not documented

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present (multi-stage Node.js 18-Alpine).

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

npx invocation simplicity emphasized; sample configuration in README.

## Repo layout

### single-package / monorepo / vendored / other

single-package; dirs include `src/`, `examples/`, `memory-bank/`, `.roo/`; config files include `package.json`, `tsconfig.json`, `smithery.yaml`, `Dockerfile`.

## Notable structural choices

- hackathon-winning design (1st @ Cline Hackathon)
- auto-complexity detection routes requests to the appropriate model
- direct npx distribution simplifies adoption
- chat history context preservation

## Unanticipated axes observed

- tool selection by query-complexity heuristic instead of explicit tool naming (one logical action, three backend models)
- Smithery registry integration — an axis in its own right (discovery/distribution via Smithery)

## Gaps

CI/testing strategy not documented. Logging configuration not specified. Host integration details beyond MCP config unclear.
