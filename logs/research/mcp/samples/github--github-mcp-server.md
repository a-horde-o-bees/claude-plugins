# github/github-mcp-server

## Identification
- url: https://github.com/github/github-mcp-server
- stars: 29.1k
- last-commit (date or relative): v1.0.0 released 2026-04-16
- license: MIT
- default branch: main
- one-line purpose: GitHub MCP server (Go) — repo/issue/PR tooling with OAuth and PAT auth modes.

## 1. Language and runtime
- language(s) + version constraints: Go (96.1%). Version in `go.mod` (not explicitly extracted).
- framework/SDK in use: Custom Go MCP implementation; `server.json` declares MCP capability.
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: stdio (local binary), HTTP (remote server at `api.githubcopilot.com`), and Docker as a packaging mode.
- how selected (flag, env, separate entry, auto-detect, etc.): Subcommand — `github-mcp-server stdio` selects stdio transport. Remote mode is a separately-hosted service consumed via its URL.
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, or other): Docker image (`ghcr.io/github/github-mcp-server`), GitHub release binaries (58 releases), `go build` from source. Official hosted remote endpoint available.
- published package name(s): GHCR image `ghcr.io/github/github-mcp-server`.
- install commands shown in README:
  - `docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN=<token> ghcr.io/github/github-mcp-server`
  - `go build -o github-mcp-server ./cmd/github-mcp-server && ./github-mcp-server stdio`
- pitfalls observed:
  - GHCR as primary distribution — `docker run` is the canonical install path, not `go install`.

## 4. Entry point / launch
- command(s) users/hosts run: `github-mcp-server stdio` (local); Docker equivalent; `api.githubcopilot.com` for hosted.
- wrapper scripts, launchers, stubs: `cmd/github-mcp-server/` main package.
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server (env vars, CLI args, config file w/ path + format, stdin prompt, OS keyring, host-passed params, combinations): Env vars and CLI flags in parallel.
  - Env: `GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_HOST` (Enterprise), `GITHUB_TOOLSETS`, `GITHUB_TOOLS`, `GITHUB_READ_ONLY`, `GITHUB_INSIDERS`
  - Flags: `--toolsets`, `--tools`, `--read-only`, `--lockdown-mode`, `--dynamic-toolsets`
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow (static token, OAuth w/ description, per-request header, none, other): GitHub Personal Access Token (PAT) for local/stdio mode; OAuth for the remote hosted server.
- where credentials come from: Env var `GITHUB_PERSONAL_ACCESS_TOKEN` for PAT; OAuth flow handled by hosts (VS Code 1.101+ has native support).
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user per process for stdio (one PAT, one identity). Remote server supports per-user OAuth so effectively per-user in hosted mode.
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: ~100+ tools across 20+ toolsets (repos, issues, pull_requests, actions, etc.). Granular toolset/tool gating via flags. Read-only mode available. Lockdown-mode filters public repo content. Dynamic toolsets allow runtime discovery.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not explicitly documented in fetched view; likely stderr per Go-binary convention.
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, etc.):
- VS Code 1.101+: native MCP support; OAuth or PAT auth — README section
- Claude Desktop: JSON snippet using Docker or local binary via `claude_desktop_config.json`
- Cursor: Docker-based config w/ PAT env injection
- Windsurf: Docker-based config w/ PAT env injection
- JetBrains IDEs: Docker-based config w/ PAT env injection
- `.vscode/` directory ships editor configuration samples
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape (.claude-plugin/plugin.json, .mcp.json at repo root, full plugin layout, not present, other): Not observed; host integration via external `claude_desktop_config.json` snippets rather than an in-repo plugin.
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: End-to-end test suite in `e2e/`. GitHub Actions CI. `.golangci.yml` for linting.
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions workflows present. Specific workflow contents not enumerated within budget.
- pitfalls observed:
  - Specific CI workflow contents.

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Multi-platform Dockerfile. No compose/Helm/brew observed.
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `.vscode/` samples; Docker is the canonical quick-start.
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Single Go module rooted at `cmd/github-mcp-server` with supporting packages. `server.json` at root.
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Dual-mode transport via subcommand (`stdio`) plus separate hosted remote service — the server binary and the remote endpoint are separate products sharing a capability surface.
- Toolset gating as a first-class feature: 20+ toolsets, independently toggleable via `--toolsets`/`GITHUB_TOOLSETS`. Dynamic toolsets allow runtime discovery, changing the tool catalog mid-session.
- Lockdown mode for content filtering on public repos — a safety envelope for agent traversal of untrusted content.
- GHCR as primary distribution — `docker run` is the canonical install path, not `go install`.

## 18. Unanticipated axes observed
- Tool-catalog mutability: `--dynamic-toolsets` exposes runtime-discoverable tools rather than a fixed catalog at startup, which affects how hosts cache tool listings.
- Per-feature "modes": `--read-only`, `--lockdown-mode`, `--insiders` act as behavior envelopes rather than capability toggles, separating policy from toolset selection.
- Hosted + local hybrid: official remote MCP endpoint operated by GitHub alongside the self-run stdio binary — distribution strategy not just code-as-download.

## 20. Gaps
- Exact Go version in `go.mod`.
- Specific CI workflow contents.
- Whether `server.json` is consumed by MCP clients beyond identifying capability, or is purely metadata.
