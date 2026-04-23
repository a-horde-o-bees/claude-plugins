# cyanheads/perplexity-mcp-server

## Identification
- url: https://github.com/cyanheads/perplexity-mcp-server
- stars: 22
- last-commit: July 22, 2025
- license: Apache-2.0
- default branch: main
- one-line purpose: Perplexity MCP server (TypeScript) — `perplexity_search` and `perplexity_deep_research` tools with optional JWT/OAuth on HTTP transport.

## 1. Language and runtime
- language(s) + version constraints: TypeScript ^5.8.3; Node.js >=18.0.0
- framework/SDK in use: MCP SDK ^1.15.0, Hono (HTTP transport), Zod validation
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (default), HTTP (configurable host 127.0.0.1, port 3010)
- how selected: environment config, validated via Zod
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: npm (source clone + build)
- published package name(s): not found on npm registry
- install commands shown in README: `git clone`, `npm install`, `npm run build`, `npm start`
- pitfalls observed:
  - published npm package name not found — source-only distribution

## 4. Entry point / launch
- command(s) users/hosts run: `npm start`
- wrapper scripts: npm build script compiles TS to `dist/`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: `.env` file validated by Zod; transport type and logging level configurable
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: API key (PERPLEXITY_API_KEY) plus optional JWT or OAuth 2.1 for HTTP transport
- where credentials come from: environment variable, CLI args, or `.env` file
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- per-user single instance; JWT/OAuth enables multi-client support in HTTP mode
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools: `perplexity_search` (fast search-augmented), `perplexity_deep_research` (multi-source exhaustive)
- pitfalls observed: none noted in this repo

## 9. Observability
- logging: structured, configurable with file rotation (centralized utilities)
- pitfalls observed:
  - structured logging with file rotation for production

## 10. Host integrations shown in README or repo
- Cline (MCP client config documented)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- not present; MCP server designed for compatible clients
- pitfalls observed: none noted in this repo

## 12. Tests
- present; `npm test` runs TypeScript noEmit type checks
- pitfalls observed: none noted in this repo

## 13. CI
- not explicitly documented in README; `.github/` present
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile present (multi-stage Node.js 18-Alpine build)
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- clone + build pattern; sample config in README
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package Node.js/TS
- dirs: `.github/`, `src/`, `docs/`
- config: `package.json`, `tsconfig.json`, `Dockerfile`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- clean separation of stdio/HTTP transports via Hono
- structured logging with file rotation for production
- Zod schema validation for config
- multi-stage Docker for optimized image

## 18. Unanticipated axes observed
- optional JWT/OAuth for HTTP mode (multi-client support in a typically single-user server)
- auto-complexity detection for tool selection

## 20. Gaps
- exact last commit date inferred from pushed_at (July 22, 2025); no changelog
- CI/CD strategy not documented
- published npm package name not found — source-only distribution
