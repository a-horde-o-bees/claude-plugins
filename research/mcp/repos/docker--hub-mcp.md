# docker/hub-mcp

## Identification
- url: https://github.com/docker/hub-mcp
- stars: 137
- last-commit (date or relative): Not explicitly extracted; active (7 open PRs noted)
- license: Apache-2.0
- default branch: main
- one-line purpose: Docker Hub MCP server (TypeScript) — tool catalog declared in `tools.json` for image discovery; integrates with Docker's Ask Gordon agent via `gordon-mcp.yml`.

## 1. Language and runtime
- language(s) + version constraints: TypeScript (99.8%). Requires Node.js 22+.
- framework/SDK in use: Not explicitly extracted; likely `@modelcontextprotocol/sdk` (typical for TS MCP servers).
- pitfalls observed: none noted in this repo

## 2. Transport
- supported transports: HTTP, stdio
- how selected (flag, env, separate entry, auto-detect, etc.): CLI flag `--transport=http|stdio`; `--port` sets HTTP port (default 3000).
- pitfalls observed: none noted in this repo

## 3. Distribution
- every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, or other): npm package; Dockerfile present; source clone/build.
- published package name(s): Not explicitly extracted from README; appears published to npm based on install flow.
- install commands shown in README:
  - `npm install && npm run build && npm start -- [--transport=http|stdio] [--port=3000]`
- pitfalls observed:
  - Exact npm package name if published.

## 4. Entry point / launch
- command(s) users/hosts run: `npm start -- ...` or direct execution of `dist/index.js` after build.
- wrapper scripts, launchers, stubs: `dist/index.js` as the built entry point.
- pitfalls observed: none noted in this repo

## 5. Configuration surface
- how config reaches the server (env vars, CLI args, config file w/ path + format, stdin prompt, OS keyring, host-passed params, combinations): Env vars (`HUB_PAT_TOKEN`) + CLI args (`--transport`, `--port`, `--username`). `tools.json` and `tools.txt` ship tool definitions.
- pitfalls observed: none noted in this repo

## 6. Authentication
- flow (static token, OAuth w/ description, per-request header, none, other): Static Docker Hub Personal Access Token (PAT).
- where credentials come from: `HUB_PAT_TOKEN` env var; paired with `--username` CLI arg.
- pitfalls observed: none noted in this repo

## 7. Multi-tenancy
- single-user / per-request tenant / workspace-keyed / not applicable / other: Single-user per process (one PAT + username).
- pitfalls observed: none noted in this repo

## 8. Capabilities exposed
- tools / resources / prompts / sampling / roots / logging / other: Tools defined in `tools.json`. Specific tool list not enumerated in fetched view. Scope: Docker Hub operations.
- pitfalls observed: none noted in this repo

## 9. Observability
- logging destination + format, metrics, tracing, debug flags: Not extracted.
- pitfalls observed: none noted in this repo

## 10. Host integrations shown in README or repo
For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, etc.):
- Claude Desktop: JSON snippet via `claude_desktop_config.json` (README section)
- VS Code: JSON snippet via User Settings JSON
- Docker Ask Gordon: `gordon-mcp.yml` config file
- pitfalls observed: none noted in this repo

## 11. Claude Code plugin wrapper
- presence and shape (.claude-plugin/plugin.json, .mcp.json at repo root, full plugin layout, not present, other): Not observed in root listing.
- pitfalls observed: none noted in this repo

## 12. Tests
- presence, framework, location, notable patterns: Test files not explicitly called out in fetched view; ESLint config present.
- pitfalls observed: none noted in this repo

## 13. CI
- presence, system, triggers, what it runs: GitHub Actions present (`.github/`); specifics not extracted.
- pitfalls observed: none noted in this repo

## 14. Container / packaging artifacts
- Dockerfile, docker-compose, Helm, systemd, brew formula, etc.: Dockerfile. No compose/Helm.
- pitfalls observed: none noted in this repo

## 15. Example client / developer ergonomics
- MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs: `tools.json` as a declarative tool manifest. Standard npm scripts.
- pitfalls observed: none noted in this repo

## 16. Repo layout
- single-package / monorepo / vendored / other — describe what's there: Single-package TS project. `src/`, `Dockerfile`, `package.json`, `tsconfig.json`, `tools.json`, `tools.txt`, `eslint.config.mjs`.
- pitfalls observed: none noted in this repo

## 17. Notable structural choices
- Tools defined in a separate `tools.json` / `tools.txt` pair — declarative catalog rather than inline schemas in source.
- First-party Docker "Ask Gordon" integration (`gordon-mcp.yml`) — repo targets Docker's own agent surface alongside generic MCP hosts.
- Transport is a first-class CLI flag with an explicit default rather than separate entry-point commands (contrast with github-mcp-server's subcommand approach).

## 18. Unanticipated axes observed
- Vendor-specific companion integration (`gordon-mcp.yml`) — MCP server pre-shaping its config for a first-party downstream tool, distinct from generic host config.
- Tool catalog as data file (`tools.json`/`tools.txt`) rather than code — opens an authoring path that doesn't require TS expertise.

## 20. Gaps
- Last-commit date.
- Exact npm package name if published.
- Tool enumeration / total tool count.
- Test framework and coverage.
- Whether the HTTP transport is Streamable HTTP, SSE, or plain JSON-RPC-over-HTTP.
