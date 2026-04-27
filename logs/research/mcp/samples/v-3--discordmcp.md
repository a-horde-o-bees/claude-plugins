# Sample

## Identification
- url: https://github.com/v-3/discordmcp
- stars: 197
- last-commit (date or relative): Not explicitly stated in extracted content
- license: MIT
- default branch: main
- one-line purpose: Discord MCP server — Discord API wrapper.

## 1. Language and runtime
- language(s) + version constraints: TypeScript 100%; Node.js 16.x+
- framework/SDK in use: Model Context Protocol TypeScript SDK; discord.js (inferred from typical Discord bot patterns)
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (Claude Desktop integration pattern — Discord API is the backend, but MCP transport to host is stdio)
- how selected (flag, env, separate entry, auto-detect, etc.): Stdio default; launched via node build output
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed: GitHub source clone only — no npm package mentioned
- published package name(s): None observed
- install commands shown in README: `npm install` then `npm run build`
- pitfalls observed:
  - No npm publish — clone-and-build is the only path; limits distribution reach but keeps the repo simple
  - No npm package despite being a TypeScript project — distribution posture is source-only; compare to other TS MCPs that publish to npm as the primary path

## 4. Entry point / launch
- command(s) users/hosts run: `node build/index.js` (production); `npm run dev` (development)
- wrapper scripts, launchers, stubs: npm scripts; entry at `build/index.js`
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server: `DISCORD_TOKEN` environment variable; `claude_desktop_config.json` for host-side
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow: Discord bot token — user creates a Discord bot application, invites the bot to a server with Read Messages / Send Messages / Read Message History permissions
- where credentials come from: Discord Developer Portal bot credentials
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Bot-scoped — one bot identity per process; bot's server memberships define reachable tenants. Automatic server/channel discovery from bot's perspective
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Two tools —
  - `send-message` — post to Discord channels
  - `read-messages` — retrieve up to 100 recent messages
  - Supports channel name or channel ID lookup
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Explicit error handling claimed; destination not specified
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
- Claude for Desktop (primary)
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not observed

### pitfalls observed

none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Not observed — no test framework documented
- MCP Inspector usage: `npx @modelcontextprotocol/inspector node build/index.js`
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: Not observed — no CI documented
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Not present
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: MCP Inspector command in README; Claude Desktop JSON config sample
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other: Single-package — `/src`, `package.json`, `tsconfig.json`
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Minimal tool surface (2 tools) — send and read only; no moderation, role management, embed-creation, or voice features
- User-approval emphasis — README calls out explicit user approval before message sending, reflecting the trust concern of letting an LLM post to Discord channels
- No npm publish — clone-and-build is the only path; limits distribution reach but keeps the repo simple
- Automatic server/channel discovery — reduces config ceremony; tool calls accept either names or IDs

## 18. Unanticipated axes observed
- No npm package despite being a TypeScript project — distribution posture is source-only; compare to other TS MCPs that publish to npm as the primary path
- User-approval framing in README suggests awareness of agent-action-on-external-service risk; a structural choice worth noting for any MCP that acts on shared/public surfaces

## 20. Gaps
- Last commit date not extracted
- Whether the project supports slash commands, threads, voice, embeds, or moderation
- No CI or tests — quality signal is weaker than higher-star alternatives
- Whether a canonical Discord-org first-party MCP exists (none surfaced in this research)
