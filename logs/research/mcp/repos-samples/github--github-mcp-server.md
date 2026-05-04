# Sample

Mirrors of `https://github.com/github/github-mcp-server`. GitHub MCP server (Go) — repo/issue/PR tooling with PAT and OAuth auth modes; ~100+ tools across 20+ toolsets with granular gating; official remote endpoint at `api.githubcopilot.com` alongside a self-run stdio binary. 29.1k stars, MIT, default branch `main`, v1.0.0 released 2026-04-16, vendor-authored (GitHub).

## Server runtime

### Go with custom MCP implementation

Go (96.1%) hand-rolling protocol handling; a `server.json` at root declares MCP capability metadata. Yields a single static binary suitable for direct distribution and Docker base-image minimization. Go version pinned in `go.mod` (specific value not extracted).

## Transport

### stdio

Local stdio transport selected via the `stdio` subcommand on the binary.

### Hosted remote endpoint (vendor-operated)

GitHub operates `api.githubcopilot.com` as the hosted MCP endpoint; hosts point at the URL rather than launching anything locally.

### Selection mechanism

Subcommand verb — `github-mcp-server stdio` for stdio; remote mode is a separately-hosted service consumed via its URL.

## Capability surface

### Tools plus toolset gating (dynamic)

~100+ tools across 20+ toolsets (repos, issues, pull_requests, actions, etc.). Granular toolset/tool gating via flags. `--dynamic-toolsets` exposes runtime-discoverable tools rather than a fixed catalog at startup, affecting how hosts cache tool listings.

### Capability gating flags (per-tool, per-category, write-mode)

`--toolsets`/`GITHUB_TOOLSETS`, `--tools`/`GITHUB_TOOLS`, `--read-only`/`GITHUB_READ_ONLY`, `--lockdown-mode`, `--insiders`/`GITHUB_INSIDERS`. Per-feature "modes" (read-only, lockdown, insiders) act as behavior envelopes rather than capability toggles, separating policy from toolset selection.

## Configuration delivery

### Environment variables

`GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_HOST` (Enterprise), `GITHUB_TOOLSETS`, `GITHUB_TOOLS`, `GITHUB_READ_ONLY`, `GITHUB_INSIDERS`.

### CLI flags

`--toolsets`, `--tools`, `--read-only`, `--lockdown-mode`, `--dynamic-toolsets` — flags run in parallel with their env-var equivalents.

### CLI flags with paired env-var equivalents

Each toolset/policy knob is reachable both as a flag and as an env var (`GITHUB_TOOLSETS` ↔ `--toolsets`, etc.) — supports both interactive launches and Docker-style env-driven deploys.

## Authentication

### Static API key / token via env var

GitHub Personal Access Token (PAT) supplied via `GITHUB_PERSONAL_ACCESS_TOKEN` env var for local/stdio mode.

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

OAuth flow handled by hosts (VS Code 1.101+ has native support) for the remote hosted server.

## Multi-tenancy

### Single-user / single-tenant per process

stdio mode is single-user per process — one PAT, one identity.

### Per-user / per-workspace via OAuth

Remote server supports per-user OAuth so effectively per-user in hosted mode.

## Distribution channel

### Docker / OCI image

Primary distribution: `ghcr.io/github/github-mcp-server`. `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN=<token> ghcr.io/github/github-mcp-server` is the canonical install path — README treats `docker run` as primary, not `go install`.

### Pre-built binary release

GitHub release binaries (58 releases observed).

### Source clone with editable install

`go build -o github-mcp-server ./cmd/github-mcp-server && ./github-mcp-server stdio` for source builds.

### Hosted endpoint (no install)

Official remote MCP endpoint operated by GitHub at `api.githubcopilot.com`.

## Entry point and launch

### Subcommand verb

`github-mcp-server stdio` (local) or Docker equivalent; `cmd/github-mcp-server/` main package.

### Docker container entrypoint

Docker is the canonical launch path; `docker run -i --rm` with PAT env injection.

### URL configuration (no local launch)

Hosted path: clients point at `api.githubcopilot.com`.

## Container artifacts

### Multi-architecture image publishing

Multi-platform Dockerfile; multi-arch image publishing implied.

## Test stack

### End-to-end protocol-conformance harness

End-to-end test suite under `e2e/`. `.golangci.yml` for linting.

### Go stdlib testing

Standard Go testing convention drives the suite.

## CI

### GitHub Actions

GitHub Actions workflows present; specific workflow contents not enumerated within budget.

## Host integration

### VS Code / VS Code Insiders / Visual Studio family

VS Code 1.101+: native MCP support; OAuth or PAT auth — README section.

### Claude Desktop

JSON snippet using Docker or local binary via `claude_desktop_config.json`.

### Cursor

Docker-based config with PAT env injection.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Windsurf documented with Docker-based config + PAT env injection.

### JetBrains IDE

Docker-based config with PAT env injection.

## Repository layout

### Single-package source (language-conventional)

Single Go module rooted at `cmd/github-mcp-server` with supporting packages. `server.json` at root.

## Safety and security posture

### Read-only by default with explicit write flag

`--read-only`/`GITHUB_READ_ONLY` mode available.

### Lockdown / content-filter mode

`--lockdown-mode` filters public repo content — a safety envelope for agent traversal of untrusted content.

## Release and lifecycle

### Tagged release with version in changelog

v1.0.0 released 2026-04-16; 58 releases observed.

### License — Permissive (MIT / Apache-2.0)

MIT license.

### Active development

Active vendor-authored development at GitHub.

## Deployment topology

### Local stdio process per session

stdio binary launched per session by the host.

### Hosted SaaS endpoint

`api.githubcopilot.com` operated by GitHub as the hosted endpoint.

### Containerized local process

Docker is the canonical local-launch path.

## Documentation surface

### Per-host README integration sections

Per-host README sections for VS Code, Claude Desktop, Cursor, Windsurf, JetBrains.

## Developer ergonomics

### Sample MCP client configs in repo

`.vscode/` samples; Docker is the canonical quick-start.
