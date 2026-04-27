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

### wrapper scripts

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
- per-workspace tenant via Slack API token; per-user isolation via DM/channel context

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed
### tools

14 tools — conversation history, thread replies, message search, reactions, user group management, unread tracking

### resources

2 directories (channel list, user list) as CSV

### pitfalls observed

none noted in this repo

## 9. Observability
### logging

configurable log level (`SLACK_MCP_LOG_LEVEL`); Inspector tool for debugging; macOS log location `~/Library/Logs/Claude/mcp*.log`

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo
- Claude (primary integration documented)
- enterprise Slack support (custom User-Agent, TLS config for Slack environments)

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper
- not present

### pitfalls observed

none noted in this repo

## 12. Tests
- not documented

### pitfalls observed

none noted in this repo

## 13. CI
- present; `.github/` (GitHub Actions); `.vscode/` IDE settings

### pitfalls observed

- full CI pipeline details not visible in README

## 14. Container / packaging artifacts
- Dockerfile (874 bytes)
- `docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.toolkit.yml` (three variants)
- `.dockerignore`

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics
- docker-compose examples (dev, toolkit variants)
- configuration examples in README
- Inspector tool for debugging
- logging examples in documentation

### pitfalls observed

- Makefile for cross-platform build automation

## 16. Repo layout
- single-package Go project

### dirs

`cmd/`, `pkg/`, `build/`, `docs/`, `.github/`, `.vscode/`, `npm/`

### config

`Makefile`, `go.mod`, `go.sum`, `.env.dist`, docker-compose variants

### additional

`manifest-dxt.json`, `SECURITY.md`

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Go implementation (single binary, performance)
- four authentication modes (flexibility for different Slack setups)
- docker-compose variants for different use cases (dev, toolkit)
- enterprise Slack support (custom User-Agent)
- Makefile for cross-platform build automation

## 18. Unanticipated axes observed
### four distinct Slack token types — axis

multiple authentication mechanisms within one server

### "stealth mode" operation (no workspace permissions) — axis

privilege-minimized deployment flavor

### Enterprise/GovSlack support via TLS + User-Agent customization — axis

enterprise flavor

- `manifest-dxt.json` — Desktop Extensions manifest, a Claude Desktop-specific packaging format distinct from `.mcp.json`

## 20. Gaps
- testing strategy not documented
- full CI pipeline details not visible in README
- rate limiting and Slack API quota handling not detailed
