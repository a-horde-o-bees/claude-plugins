# Sample

Mirrors of `https://github.com/v-3/discordmcp`. Discord MCP server — minimal 2-tool TypeScript wrapper around discord.js for sending and reading channel messages. 197 stars, MIT, default branch `main`. Source-clone-only distribution; no npm publish despite being a TypeScript project.

## Server runtime

### Node.js / TypeScript with official MCP SDK

TypeScript (100%) Node.js server built on the Model Context Protocol TypeScript SDK; discord.js inferred for Discord API access. Node.js 16.x+ floor. Compiled to a `build/` JS output.

## Transport

### stdio

stdio default; launched via `node build/index.js` in Claude Desktop config. Discord API is the backend data plane; MCP transport to host is stdio.

### Selection mechanism

Implicit single mode — stdio only.

## Capability surface

### Tools-only, hand-curated narrow surface

Two tools — `send-message` (post to Discord channels) and `read-messages` (retrieve up to 100 recent messages). Supports channel name or channel ID lookup. Minimal surface — no moderation, role management, embeds, or voice features.

## Configuration delivery

### Environment variables

`DISCORD_TOKEN` env var supplies the bot credential.

### Host-side JSON config snippet

`claude_desktop_config.json` snippet shown in README — `command: "node"`, `args: [build/index.js]`, with `DISCORD_TOKEN` in the `env` block.

## Authentication

### Bot identity (third-party platform)

Discord bot token — user creates a Discord bot application at the Developer Portal, invites the bot to a server with Read Messages / Send Messages / Read Message History permissions. Bot's server memberships define reachable tenants; users grant access through Discord's normal invite flow rather than configuring the MCP server. Credentials originate from the Discord Developer Portal and are supplied via the `DISCORD_TOKEN` env var.

## Multi-tenancy

### Bot-scoped

One bot identity per process; the bot's server memberships define reachable tenants. Multiple users may interact with the same bot, but the server's identity is fixed. Automatic server/channel discovery from the bot's perspective reduces config ceremony — tool calls accept either names or IDs.

## Distribution channel

### Source clone with editable install

GitHub source clone only — `npm install` then `npm run build`. No npm publish. Limits distribution reach but keeps the repo simple. Distinct from typical TS MCP servers that publish to npm.

## Entry point and launch

### Built JS file (`node build/index.js`)

Host config invokes `node build/index.js`. Requires the consumer to have run `npm install && npm run build` first.

### npm scripts (start/start:stdio/start:http)

`npm run dev` for development. `npm run build` to produce the `build/` JS artifact. Production users invoke the built file directly.

## Build and packaging

### npm/Node toolchain

`package.json` with build/dev scripts; standard TypeScript-to-JS compilation producing a `build/` output.

## Container artifacts

### No container artifacts

No Dockerfile.

## Test stack

### MCP Inspector as test driver

`npx @modelcontextprotocol/inspector node build/index.js` documented as the verification path. No unit-test framework wired up.

### No tests / not surfaced

No unit test framework documented.

## CI

### None / absent

No CI documented.

## Host integration

### Claude Desktop

Primary documented host; JSON config snippet in README.

### Inspector compatibility called out

MCP Inspector command shown in README as a verification surface.

## Observability

### Stderr logging (convention / SDK default)

Explicit error handling claimed in README; destination not specified — likely stderr per stdio convention.

## Repository layout

### Single-package source (language-conventional)

Single-package — `/src`, `package.json`, `tsconfig.json`. Conventional TS layout.

## Safety and security posture

### Explicit non-security stance

README emphasizes explicit user approval before message sending — reflects the trust concern of letting an LLM post to Discord channels. No hard enforcement, just author guidance to the operator.

## Release and lifecycle

### License — Permissive (MIT / Apache-2.0)

MIT.
