# Sample

Mirrors of `https://github.com/korotovsky/slack-mcp-server`. Slack MCP server in Go — supports four distinct Slack token types (browser cookie, user OAuth, bot, "stealth-mode" cookie), exposes 14 conversation/thread/search tools, and ships a DXT bundle for Claude Desktop drag-and-drop install. 1,500 stars, MIT, default branch `master`, last commit April 16, 2026.

## Server runtime

### Go with custom MCP implementation

Custom Go MCP implementation (no standard Go web framework, no third-party MCP SDK). Go 1.21+ inferred from go.mod modern features. Single static binary; ships a custom User-Agent and TLS configuration to support enterprise-Slack environments.

## Transport

### stdio

Default transport (`SLACK_MCP_TRANSPORT=stdio`).

### Streamable HTTP

HTTP transport supported with configurable host and port.

### SSE (Server-Sent Events)

SSE transport supported.

### Selection mechanism

Environment variable `SLACK_MCP_TRANSPORT` selects transport (default `stdio`). Host/port configurable via additional env vars; API key required for SSE/HTTP modes.

## Capability surface

### Domain-bundled tool set

14 tools covering Slack domain entities — conversation history, thread replies, message search, reactions, user group management, unread tracking. 2 directory-style resources (channel list, user list) in CSV.

### Tools plus resources

Tools plus 2 directory resources (channel/user CSV listings).

### Capability gating flags (per-tool, per-category, write-mode)

Per-tool enable flags exposed via env vars to scope the surface per deployment.

## Configuration delivery

### Environment variables

Four token env vars (`SLACK_MCP_XOXC_TOKEN`, `SLACK_MCP_XOXD_TOKEN`, `SLACK_MCP_XOXP_TOKEN`, `SLACK_MCP_XOXB_TOKEN`); transport selector (`SLACK_MCP_TRANSPORT`); host, port (default 13080), API key for SSE/HTTP, proxy, log level (`SLACK_MCP_LOG_LEVEL`), per-tool enable flags.

## Authentication

### Multi-mode token selection

Four distinct Slack credential types selectable via env var: browser cookie (`XOXC`), additional cookie (`XOXD`), user OAuth token (`XOXP`), bot token (`XOXB`). The combination accepted determines operating mode — the cookie-based flow enables "stealth mode" deployment with no workspace permissions; OAuth requires workspace admin approval. Choice ranges from privilege-minimized stealth to formal OAuth.

## Multi-tenancy

### Per-workspace tenant via upstream token

Per-workspace tenancy via Slack API token; per-user isolation via DM/channel context. Server identity is fixed by the configured token.

## Distribution channel

### Docker / OCI image

Distributed as Docker (`Dockerfile` + multiple `docker-compose` variants).

### MCPB bundle / Desktop Extension manifest

Ships `manifest-dxt.json` — Claude Desktop drag-and-drop install via Desktop Extensions packaging.

### Go module via `go get` / `go install`

Source build via Go toolchain: `go run mcp/mcp-server.go --transport stdio`. Self-built Go executable distribution.

## Entry point and launch

### Native binary

Self-built Go executable; users `go run` or run the compiled binary directly.

### Docker container entrypoint

`docker run` against the published Docker image.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

`Dockerfile` (874 bytes) at repo root.

### Docker Compose for local dev

`docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.toolkit.yml` — three Compose variants for different use cases (production, dev, toolkit).

## Observability

### Env-var-controlled log level

`SLACK_MCP_LOG_LEVEL` env var sets log severity. macOS log location documented as `~/Library/Logs/Claude/mcp*.log`.

## CI

### GitHub Actions

`.github/` present (GitHub Actions). Full CI pipeline details not visible in README.

## Repository layout

### Single-package source (language-conventional)

Standard Go layout — `cmd/`, `pkg/`, `build/`, `docs/`, `.github/`, `.vscode/`, `npm/`. Config at root: `Makefile`, `go.mod`, `go.sum`, `.env.dist`, docker-compose variants. Additional artifacts: `manifest-dxt.json`, `SECURITY.md`.

## Host integration

### Claude Desktop

Primary host integration documented. DXT manifest (`manifest-dxt.json`) provides drag-and-drop install.

### MCPB / DXT bundle manifest

`manifest-dxt.json` shipped alongside the server.

### Inspector compatibility called out

`@modelcontextprotocol/inspector` referenced via npm tooling for debugging.

## Developer ergonomics

### Makefile / Makefile.toml

Makefile (5.7 KB) for cross-platform build automation.

### Sample MCP client configs in repo

docker-compose examples (dev, toolkit variants); configuration examples in README; logging examples in documentation.

### Inspector/debug tooling references

Inspector recommended for debugging.

## Release and lifecycle

### Active development

1,500 stars; last commit April 16, 2026.

### License — Permissive (MIT / Apache-2.0)

MIT.
