# Sample

## Identification

### url

https://github.com/Azure/azure-mcp

### stars

1.2k

### last-commit (date or relative)

ARCHIVED. Repo archival banner on GitHub page shows "archived by the owner on Feb 6, 2026." The README body itself states "This repository is archived as of August 25, 2025." The two dates disagree — the August 2025 README notice predates the official GitHub-archived flag (Feb 2026); most likely the code stopped getting updates in Aug 2025 but the repo was formally archived four months later.

### license

MIT

### default branch

main (read-only)

### one-line purpose

TBD — repo archived; technical surface redirected to microsoft/mcp.

## 1. Language and runtime

### language(s) + version constraints

C# (78.6%)

### framework/SDK in use

.NET-based MCP server (inherited by successor)

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

Not extracted — README body only shows archival notice in the raw view.

### how selected (flag, env, separate entry, auto-detect, etc.)

Not extracted (see successor).

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, or other)

Dockerfile present; other mechanisms not extractable from archival view.

### published package name(s)

Not extracted from archived surface.

### install commands shown in README

Redirects to successor.

### pitfalls observed

  - Umbrella-repo consolidation pattern — an org moving from per-service MCP repos into a single company-wide MCP monorepo with shared C# core (the inverse of awslabs/mcp's per-serv...

## 4. Entry point / launch

### command(s) users/hosts run

Not extracted — see successor microsoft/mcp Azure.Mcp.Server.

### wrapper scripts, launchers, stubs

Not extracted.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server (env vars, CLI args, config file w/ path + format, stdin prompt, OS keyring, host-passed params, combinations)

Not extracted.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow (static token, OAuth w/ description, per-request header, none, other)

Not extracted from archived repo; Azure credential chain via DefaultAzureCredential likely based on successor context — not verified here.

### where credentials come from

Not extracted.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

Not extracted.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Not extracted from archival surface.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Not extracted.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo
For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, etc.):
- Not extracted from archival surface. Successor microsoft/mcp documents VS Code, Visual Studio 2022, IntelliJ IDEA, Eclipse, VS Code Insiders.

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape (.claude-plugin/plugin.json, .mcp.json at repo root, full plugin layout, not present, other)

Not observed in directory listing of archived repo.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

Not extracted.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

Not extracted.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present.

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

Not extracted.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other — describe what's there

Not extracted from archival surface. In the successor, this code became the `Azure.Mcp.Server` component under `microsoft/mcp/servers/`.

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- Archived with redirect to microsoft/mcp. The consolidation collapsed a per-domain repo into an umbrella Microsoft MCP monorepo that also hosts Fabric.Mcp.Server and shared C# tooling.

## 18. Unanticipated axes observed
- Two-stage archival (code freeze ~Aug 2025 per README body; formal GitHub archival Feb 2026) — the gap is itself a decision signal: the repo ran in "read-only maintenance" mode for months before being archived at the org level, suggesting the redirect had to stabilize first.
- Umbrella-repo consolidation pattern — an org moving from per-service MCP repos into a single company-wide MCP monorepo with shared C# core (the inverse of awslabs/mcp's per-service PyPI package strategy).

## 20. Gaps
- Whole technical surface (transports, install commands, config, auth, tests, CI, capabilities) — archived repo's README only carries the archival notice; reconstructing technical details requires fetching successor content at github.com/microsoft/mcp/tree/main/servers/Azure.Mcp.Server.
- Exact reason for the 4+ month gap between README-declared archival (Aug 2025) and GitHub archival flag (Feb 2026) — commit history might clarify.

## Canonical successor

- `microsoft/mcp` — umbrella repo hosting Azure.Mcp.Server and Fabric.Mcp.Server under `/servers/`, shared libraries under `/core/`. ~3k stars, MIT, main branch. Distribution channels: NuGet, Docker (Dockerfile present), VS Code extensions, Visual Studio Marketplace, IntelliJ/Eclipse plugins. Transports: stdio (local), HTTP (remote). Hosts documented: VS Code, VS Code Insiders, Visual Studio 2022, IntelliJ IDEA, Eclipse. Last commit noted as 2026-04-14 (Fabric.Mcp.Server 1.0.0). Primary language C# (88%).
