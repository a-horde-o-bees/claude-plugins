# idosal/git-mcp

## Identification
- url: https://github.com/idosal/git-mcp
- stars: 8,000
- last-commit: March 13, 2026
- license: Apache-2.0
- default branch: main
- one-line purpose: Hosted git-documentation MCP service — cloud-hosted SaaS endpoint, zero-auth; no local install.

## 1. Language and runtime
- language(s) + version constraints: TypeScript/JavaScript; Node.js runtime (npx, pnpm, npm)
- framework/SDK in use: React Router 7, Vite, MCP SDK, Cloudflare Workers (Wrangler)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: HTTP/HTTPS (cloud endpoint gitmcp.io), SSE
- how selected: auto-detected by IDE via direct HTTP URL specification
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: npm/pnpm source build; direct URL endpoint (cloud-hosted gitmcp.io); self-hosted option
- published package name(s): not on npm registry; cloud-hosted at gitmcp.io
- install commands shown in README: `pnpm install`, `npm run dev`, endpoint `https://gitmcp.io/{owner}/{repo}`
- pitfalls observed: none noted in this repo

## 4. Entry point / launch
- command(s) users/hosts run: `npm run dev`, `pnpm dev`, `npx mcp-remote https://gitmcp.io/{owner}/{repo}`
- wrapper scripts: React Router dev scripts; Wrangler for Cloudflare Workers deployment
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: IDE JSON configs (Cursor, Claude Desktop, Windsurf, VSCode, Cline); dynamic endpoint `gitmcp.io/{owner}/{repo}`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: none required
- where credentials come from: not applicable; zero-auth cloud service
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- per-repository tenant (parameterized by owner/repo); cloud-hosted single service with multi-repo support
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools: `fetch_<repo-name>_documentation`, `search_<repo-name>_documentation`, `search_<repo-name>_code`, `fetch_url_content`
- pitfalls observed: none noted in this repo

## 9. Observability
- not documented; presumed server-side
- pitfalls observed:
  - server-side logging strategy unclear

## 10. Host integrations shown in README or repo
- Claude Desktop, Cursor, Windsurf, VSCode, Cline, Highlight AI, Augment Code, Msty AI — all via JSON `mcp.json` config documented in README
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- not present; uses MCP protocol
- pitfalls observed: none noted in this repo

## 12. Tests
- present; Playwright E2E (`playwright.config.ts`), Vitest units (`vitest.config.ts`), `npm run test`
- pitfalls observed: none noted in this repo

## 13. CI
- present; GitHub Actions: `e2e-tests.yml`, `run-tests.yml`
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- no Dockerfile; Cloudflare Workers cloud-native deployment
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- dev scripts, Playwright E2E tests, README examples
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package React/TS with Cloudflare integration
- dirs: `.github/`, `.husky/`, `.react-router/`, `app/`, `src/`, `static/`, `tests/`, `dist/`
- config: `wrangler.jsonc`, `react-router.config.ts`, `vite.config.ts`, `vitest.config.ts`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- cloud-hosted SaaS MCP endpoint removes installation friction
- zero-auth model for public repos
- React Router 7 + Vite for frontend
- Biome for unified linting/formatting

## 18. Unanticipated axes observed
- MCP server delivered as a cloud-hosted service rather than self-hosted — axis: hosted vs local installation
- parameterized repository endpoints — one deployment serves every GitHub repo

## 20. Gaps
- Node.js version constraints not in README
- server-side logging strategy unclear
- self-hosting details limited; Cloudflare dependency unclear
