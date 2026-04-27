# Sample

## Identification

### url

https://github.com/slackapi/slack-mcp-plugin

### stars

not publicly available

### last-commit

March 19, 2026.

### license

not specified (Slack proprietary assumed)

### default branch

main

### one-line purpose

Slack MCP plugin — configs-only repo; remote MCP service hosted at `mcp.slack.com`.

## 1. Language and runtime

### language(s) + version constraints

not specified — remote HTTP service.

### framework/SDK in use

MCP (remote server).

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

HTTP (remote MCP endpoint).

### how selected

HTTP URL (`https://mcp.slack.com/mcp`).

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

remote HTTP endpoint only; GitHub repo contains client config only.

### published package name(s)

remote server at `mcp.slack.com`; no local package.

### install commands shown in README

git clone for config review; manual setup via deeplink or Cursor MCP settings tab.

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

no local entry point; HTTP endpoint only.

### wrapper scripts, launchers, stubs

none

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

client-specific configs (Claude Code: clientId `1601185624273.8899143856786`, callbackPort 3118; Cursor: CLIENT_ID `3660753192626.8903469228982`); OAuth callback handling.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

OAuth 2.0; workspace admin approval required.

### where credentials come from

workspace OAuth; OAuth callback port-based flow.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

per-workspace OAuth token; workspace admin scope.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

tools: message search, direct messaging, thread access, canvas document create/export, user profile retrieval with custom fields.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

server-side only (not documented in repo).

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude Code CLI

OAuth config with clientId and callbackPort (documented in README); MCP configuration files (`.mcp.json`).

### Cursor IDE

OAuth config with CLIENT_ID (documented in README); MCP configuration files (`.cursor-mcp.json`).

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not present; remote HTTP service (the repo is config-only).

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

not applicable (config-only repo).

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

not applicable

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

not applicable (remote service).

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

deeplink for Cursor (browser-based setup); MCP settings tab in Cursor (manual config); Claude Code CLI example with OAuth config block; `CLAUDE.md` documentation.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

config-only repository (not a server implementation); files: `.mcp.json`, `.cursor-mcp.json`, `CLAUDE.md`, `README.md`, `LICENSE`; dirs: `.claude-plugin/`, `.cursor-plugin/`, `.github/`, `commands/`, `skills/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

official first-party Slack MCP — Slack-hosted remote server. config-only GitHub repository (actual MCP server at `mcp.slack.com`). OAuth workspace integration. workspace admin approval required. ships configs for two IDEs (Claude Code, Cursor).

## 18. Unanticipated axes observed

first-party MCP server delivered as remote HTTP endpoint with a separate configs-only GitHub repo — axis: publishing configs-as-product vs server-as-product. ships commands/ and skills/ directories alongside the configs — axis: bundling client-side skills with server integration. `.cursor-plugin/` alongside `.claude-plugin/` — axis: multi-host plugin-wrapper layout.

## 20. Gaps

server implementation not in repo (remote service). license not specified. full Slack API capability surface not documented in config repo. rate limiting and quota handling not documented.
