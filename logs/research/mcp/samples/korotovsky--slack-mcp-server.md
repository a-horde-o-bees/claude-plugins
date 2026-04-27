# Sample

## Identification

### url

https://github.com/korotovsky/slack-mcp-server

### stars

1,500

### last-commit

April 16, 2026

### license

MIT

### default branch

master

### one-line purpose

Slack MCP server (Go) — 4 token types; stealth mode; ships DXT manifest.

## 1. Language and runtime

### language(s) + version constraints

Go; Go 1.21+ (inferred from go.mod modern features)

### framework/SDK in use

custom Go MCP implementation; no standard Go web framework

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

stdio, SSE, HTTP

### how selected

env var `SLACK_MCP_TRANSPORT` (default stdio); configurable host/port

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed

Docker (Dockerfile + docker-compose variants), npm tool for MCP Inspector, source build via Go

### published package name(s)

Docker image; Go executable (self-built)

### install commands shown in README

`go run mcp/mcp-server.go --transport stdio`, Docker build/run, npm for inspector

### pitfalls observed

none noted in this repo

## 4. Entry point / launch

### command(s) users/hosts run

`go run mcp/mcp-server.go --transport stdio`, Docker container, `@modelcontextprotocol/inspector` via npm

### wrapper scripts, launchers, stubs

Makefile (5.7 KB) for build automation; docker-compose variants for dev/toolkit

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server

env vars — `SLACK_MCP_XOXC_TOKEN` (browser), `SLACK_MCP_XOXD_TOKEN` (cookie), `SLACK_MCP_XOXP_TOKEN` (user OAuth), `SLACK_MCP_XOXB_TOKEN` (bot), port (default 13080), host, API key for SSE/HTTP, proxy, per-tool enable flags

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow

four token types (browser, cookie, user OAuth, bot); flexible choice allows stealth mode or OAuth

### where credentials come from

env vars; workspace admin approval required for OAuth

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### tenancy model

per-workspace tenant via Slack API token; per-user isolation via DM/channel context

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

14 tools — conversation history, thread replies, message search, reactions, user group management, unread tracking. 2 resources as directories (channel list, user list) in CSV.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

configurable log level (`SLACK_MCP_LOG_LEVEL`); Inspector tool for debugging; macOS log location `~/Library/Logs/Claude/mcp*.log`

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

### Claude

primary integration documented

### Enterprise Slack

custom User-Agent, TLS config for Slack environments

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

not present

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

not documented

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

present; `.github/` (GitHub Actions); `.vscode/` IDE settings

### pitfalls observed

full CI pipeline details not visible in README

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile (874 bytes); `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.toolkit.yml` (three variants); `.dockerignore`

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

docker-compose examples (dev, toolkit variants); configuration examples in README; Inspector tool for debugging; logging examples in documentation; Makefile for cross-platform build automation

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other

single-package Go project. Directories: `cmd/`, `pkg/`, `build/`, `docs/`, `.github/`, `.vscode/`, `npm/`. Config: `Makefile`, `go.mod`, `go.sum`, `.env.dist`, docker-compose variants. Additional: `manifest-dxt.json`, `SECURITY.md`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices

Go implementation (single binary, performance). Four authentication modes (flexibility for different Slack setups). Docker-compose variants for different use cases (dev, toolkit). Enterprise Slack support (custom User-Agent). Makefile for cross-platform build automation.

## 18. Unanticipated axes observed

Four distinct Slack token types — multiple authentication mechanisms within one server. "Stealth mode" operation (no workspace permissions) — privilege-minimized deployment flavor. Enterprise/GovSlack support via TLS + User-Agent customization — enterprise flavor. `manifest-dxt.json` — Desktop Extensions manifest, a Claude Desktop-specific packaging format distinct from `.mcp.json`.

## 20. Gaps

Testing strategy not documented. Full CI pipeline details not visible in README. Rate limiting and Slack API quota handling not detailed.
