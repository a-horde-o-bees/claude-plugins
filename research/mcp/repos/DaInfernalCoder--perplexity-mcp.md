# DaInfernalCoder/perplexity-mcp

## Identification
- url: https://github.com/DaInfernalCoder/perplexity-mcp
- stars: 289
- last-commit: November 1, 2025 ("Reasoning and Chat History")
- license: MIT
- default branch: main
- one-line purpose: Perplexity search MCP server — exposes `search`, `reason`, `deep_research` tools with auto-complexity routing to Sonar Pro / Sonar Reasoning / Sonar Deep Research.

## 1. Language and runtime
- language(s) + version constraints: JavaScript (94.7%), Dockerfile (5.3%); Node.js required
- framework/SDK in use: MCP SDK, Anthropic Claude Agent SDK
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: HTTP (inferred from Anthropic Agent SDK usage)
- how selected: not explicitly documented
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: npx (recommended), source clone
- published package name(s): `perplexity-mcp` via `npx -y perplexity-mcp`
- install commands shown in README: `npx -y perplexity-mcp` (recommended) or git clone + `npm install`
- pitfalls observed:
  - direct npx distribution simplifies adoption
  - Smithery registry integration — an axis in its own right (discovery/distribution via Smithery)

## 4. Entry point / launch
- command(s) users/hosts run: `npx -y perplexity-mcp`
- wrapper scripts: none documented; direct npx invocation
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: `.env` file, CLI args (`--api-key`), `--cwd` parameter for .env path
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: API key (PERPLEXITY_API_KEY). Priority: CLI arg > env var > .env file
- where credentials come from: CLI, environment, or `.env`
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- per-request context; assumes single-agent invocation
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools: `search` (Sonar Pro), `reason` (Sonar Reasoning Pro), `deep_research` (Sonar Deep Research)
- optional `force_model` parameter to override auto-complexity detection
- pitfalls observed: none noted in this repo

## 9. Observability
- logging: not documented
- pitfalls observed:
  - logging configuration not specified

## 10. Host integrations shown in README or repo
- MCP config files mentioned in generic terms; specifics not detailed
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- not present
- pitfalls observed: none noted in this repo

## 12. Tests
- not documented
- pitfalls observed: none noted in this repo

## 13. CI
- not documented
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile present (multi-stage Node.js 18-Alpine)
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- npx invocation simplicity emphasized; sample configuration in README
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package
- dirs: `src/`, `examples/`, `memory-bank/`, `.roo/`
- config: `package.json`, `tsconfig.json`, `smithery.yaml`, `Dockerfile`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- hackathon-winning design (1st @ Cline Hackathon)
- auto-complexity detection routes requests to the appropriate model
- direct npx distribution simplifies adoption
- chat history context preservation

## 18. Unanticipated axes observed
- tool selection by query-complexity heuristic instead of explicit tool naming (one logical action, three backend models)
- Smithery registry integration — an axis in its own right (discovery/distribution via Smithery)

## 20. Gaps
- CI/testing strategy not documented
- logging configuration not specified
- host integration details beyond MCP config unclear
