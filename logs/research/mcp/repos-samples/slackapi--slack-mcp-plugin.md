# Sample

Mirrors of `https://github.com/slackapi/slack-mcp-plugin`. Slack MCP plugin — official first-party Slack MCP delivered as a remote HTTP service hosted at `mcp.slack.com`; the GitHub repo is configs-only (client OAuth metadata) with no server implementation. Stars not publicly available, license not specified (Slack proprietary assumed), default branch `main`. Last commit March 19, 2026.

## Server runtime

### Remote HTTP service (no local runtime)

The runtime lives on a vendor-hosted endpoint at `mcp.slack.com`; there is no local language or framework — nothing executes on the user's machine. The repo carries only client config files and OAuth metadata.

## Transport

### Hosted remote endpoint (vendor-operated)

HTTP MCP endpoint at `https://mcp.slack.com/mcp`. Vendor operates the runtime.

## Capability surface

### Tools-heavy domain wrapper / domain-tool catalog

Tools: message search, direct messaging, thread access, canvas document create/export, user profile retrieval with custom fields. Domain-shaped Slack-API wrapper with vendor-native artifact creation (canvas documents).

## Configuration delivery

### Hosted endpoint as primary delivery

Configuration is the URL (`https://mcp.slack.com/mcp`) plus client-specific OAuth metadata; nothing locally configurable beyond client-side OAuth setup.

### Host-side JSON config snippet

Per-host config files shipped in repo: `.mcp.json` for Claude Code (clientId `1601185624273.8899143856786`, callbackPort 3118); `.cursor-mcp.json` for Cursor (CLIENT_ID `3660753192626.8903469228982`).

## Authentication

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

OAuth 2.0 workspace flow; workspace admin approval required. OAuth callback handled via callback port (3118 for Claude Code). Workspace-level OAuth scope.

## Multi-tenancy

### Per-user / per-workspace via OAuth

Per-workspace OAuth token; workspace admin scope. Workspace is the tenant boundary.

## Distribution channel

### Hosted endpoint (no install)

User pastes the URL into their host's MCP config; nothing installs locally. Slack runs the runtime.

### Configs-only repo (no server artifact)

Repo ships only client config snippets and OAuth setup metadata; the actual server is hosted remotely. Distribution is "configure your client to point at our endpoint."

## Entry point and launch

### URL configuration (no local launch)

No local entry point; HTTP endpoint URL plus per-client OAuth metadata is the entire launch surface.

## Host integration

### Claude Code

OAuth config block with clientId and callbackPort documented in README; `.mcp.json` config file shipped.

### Cursor

OAuth config block with CLIENT_ID documented in README; `.cursor-mcp.json` config file shipped. Setup via deeplink (browser-based) or via Cursor's MCP settings tab.

### `.claude-plugin/` directory in repo

`.claude-plugin/` directory present in repo.

### `.mcp.json` in project root

`.mcp.json` shipped at repo root.

### First-party host extension manifest

Cursor-side `.cursor-plugin/` directory present alongside the Claude `.claude-plugin/` — multi-host plugin-wrapper layout, official first-party Slack MCP.

### Vendor-specific companion config

Configs-only repo *is* the companion config — vendor-specific OAuth setup metadata for each host.

## Observability

### None / unspecified

Server-side logging only; not documented in repo (server implementation isn't in repo).

## Repository layout

### Configs-only

Configs-only repository (not a server implementation). Files: `.mcp.json`, `.cursor-mcp.json`, `CLAUDE.md`, `README.md`, `LICENSE`. Directories: `.claude-plugin/`, `.cursor-plugin/`, `.github/`, `commands/`, `skills/`. Server implementation lives at `mcp.slack.com`.

## Documentation surface

### Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)

`CLAUDE.md` shipped in repo; `.mcp.json` and `.cursor-mcp.json` carry agent-facing metadata.

### Bundled `cursor_rules.md` / AI-guidance content

`commands/` and `skills/` directories ship client-side AI guidance content alongside the server-pointing configs.

## Claude Code plugin / skill wrapper

### `.claude-plugin/` wrapper

`.claude-plugin/` directory present in repo — first-party Slack ships the Claude Code plugin wrapper as part of the configs-only distribution.

## Release and lifecycle

### Vendor-internal release (no public pipeline)

Server runtime is vendor-operated; no public release pipeline. Repo updates track config/OAuth-metadata changes.

### Active development

Last commit March 19, 2026.
