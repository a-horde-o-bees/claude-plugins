# Sample

## Identification

### url

https://github.com/googleapis/mcp-toolbox

### stars

14.7k

### last-commit (date or relative)

v1.1.0 released 2026-04-13; 1,798 total commits

### license

Apache-2.0

### default branch

main

### one-line purpose

Google APIs MCP toolbox — 5 distribution channels (Docker, Go install, source, Homebrew, binary); HTTP-first on port 5000.

## 1. Language and runtime

### language(s) + version constraints

Go (96.1%). Go module versioning; specific Go version not extracted.

### framework/SDK in use

Custom Go implementation for the MCP toolbox; `server.json` for MCP capability declaration.

### pitfalls observed

none noted in this repo

## 2. Transport

### supported transports

HTTP MCP server on port 5000 at `/mcp` endpoint. Stdio not explicitly documented in the fetched view — server appears HTTP-first.

### how selected (flag, env, separate entry, auto-detect, etc.)

HTTP is the default mode when the binary runs.

### pitfalls observed

none noted in this repo

## 3. Distribution

### every mechanism observed (PyPI, npm, uvx, npx, Docker, Homebrew, Cargo, Go install, GitHub release binary, source-only, or other)

- GitHub release binaries (Linux AMD64, macOS ARM64/Intel, Windows AMD64)
- Docker (`us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:$VERSION`)
- `go install github.com/googleapis/mcp-toolbox@v1.1.0`
- Homebrew (`brew install mcp-toolbox`)
- NPM shim: `npx @toolbox-sdk/server --config tools.yaml`

### published package name(s)

`mcp-toolbox` Go module; `@toolbox-sdk/server` npm shim; Homebrew formula `mcp-toolbox`.

### install commands shown in README

Each of the five above.

### pitfalls observed

- Five distribution channels (binary, Docker, go install, Homebrew, npm shim) — unusually broad; implies cross-ecosystem discoverability is a deliberate goal.
- NPM shim (`@toolbox-sdk/server`) wrapping a Go binary — cross-ecosystem glue that lets node-oriented hosts run a Go server by name.
- Homebrew formula source (tap or core).

## 4. Entry point / launch

### command(s) users/hosts run

`./toolbox --config "tools.yaml"`. Docker and npm shim variants run the same binary.

### wrapper scripts, launchers, stubs

`@toolbox-sdk/server` (npm) wraps the Go binary.

### pitfalls observed

none noted in this repo

## 5. Configuration surface

### how config reaches the server (env vars, CLI args, config file w/ path + format, stdin prompt, OS keyring, host-passed params, combinations)

Primary: YAML manifest (`tools.yaml`) defining sources, tools, toolsets, and prompts. Dynamic reloading on by default (`--disable-reload` opts out). CLI flag `--config` points at the manifest.

### pitfalls observed

none noted in this repo

## 6. Authentication

### flow (static token, OAuth w/ description, per-request header, none, other)

Delegates to database auth schemes. Integrated authentication including IAM for Google Cloud, plus standard credentials for PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Redis, Elasticsearch, and others.

### where credentials come from

Configured within `tools.yaml` per-source; Google Cloud IAM uses ambient/ADC credentials.

### pitfalls observed

none noted in this repo

## 7. Multi-tenancy

### single-user / per-request tenant / workspace-keyed / not applicable / other

Configuration is per-process; the manifest can declare multiple sources, effectively multi-database but not multi-user. HTTP endpoint serves any connected MCP client.

### pitfalls observed

none noted in this repo

## 8. Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

Tools, toolsets, and prompts declared in the YAML manifest. `sources` abstract database connections. A `prompts` section suggests first-class MCP prompt support beyond tools.

### pitfalls observed

none noted in this repo

## 9. Observability

### logging destination + format, metrics, tracing, debug flags

Not explicitly extracted; standard Go stderr logging likely.

### pitfalls observed

none noted in this repo

## 10. Host integrations shown in README or repo

For each host encountered — Claude Desktop, Claude Code, Cursor, Windsurf, Cline, Continue, Zed, VS Code, custom, any other — record form (JSON snippet, config path, shell command, plugin wrapper in-repo, docs link) and location (README section, separate docs file, shipped config file, etc.):
- Gemini CLI — first-party; a `gemini-extension.json` ships in-repo
- Google Antigravity — listed as compatible client
- Claude Code — listed as compatible client
- Codex — listed as compatible client
- README framing: "MCP-compatible IDE or client (e.g., Gemini CLI, Google Antigravity, Claude Code, Codex, etc.)"

### pitfalls observed

none noted in this repo

## 11. Claude Code plugin wrapper

### presence and shape

Not observed. `gemini-extension.json` is the only host-specific config file shipped.

### pitfalls observed

none noted in this repo

## 12. Tests

### presence, framework, location, notable patterns

`/tests` directory. Go testing conventions implied.

### pitfalls observed

none noted in this repo

## 13. CI

### presence, system, triggers, what it runs

`.ci/` + `.github/workflows/` directories. `.golangci.yaml` for lint.

### pitfalls observed

none noted in this repo

## 14. Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

Dockerfile present. Homebrew formula available (external tap inferred from `brew install mcp-toolbox`).

### pitfalls observed

none noted in this repo

## 15. Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

`tools.yaml` is the canonical artifact. `server.json` describes MCP capabilities. `.hugo/` directory suggests docs site infrastructure.

### pitfalls observed

none noted in this repo

## 16. Repo layout

### single-package / monorepo / vendored / other — describe what's there

Single Go module. Top-level: `/cmd`, `/docs`, `/internal`, `/tests`, `/.ci`, `/.github`, `/.hugo`, `/.gemini`. `.gitmodules` present (submodules used).

### pitfalls observed

none noted in this repo

## 17. Notable structural choices
- YAML manifest as the primary configuration surface. Sources, tools, toolsets, and prompts all live in `tools.yaml` — admin configures by editing YAML rather than by writing code.
- Dynamic reloading by default — config changes propagate without restart; `--disable-reload` opts out. Unusual for MCP servers, which typically re-exec.
- Multi-database abstraction: the same binary speaks to 8+ databases via `sources`. Tool authoring is declarative on top of that abstraction.
- Five distribution channels (binary, Docker, go install, Homebrew, npm shim) — unusually broad; implies cross-ecosystem discoverability is a deliberate goal.
- HTTP-first transport at `:5000/mcp` — diverges from the stdio-first convention common elsewhere.
- Gemini-first integration: `gemini-extension.json` and `.gemini/` directory reflect the origin at Google; other hosts consume the generic HTTP endpoint.

## 18. Unanticipated axes observed
- Declarative tool authoring via YAML manifest — admins define tools without writing code, a different authoring surface from code-defined MCP servers.
- Prompts as a first-class manifest concept alongside tools — most MCP servers concentrate on tools; this one surfaces the prompts capability too.
- Hot reloading as a built-in — implies state that survives across configuration changes, a different lifecycle assumption.
- NPM shim (`@toolbox-sdk/server`) wrapping a Go binary — cross-ecosystem glue that lets node-oriented hosts run a Go server by name.

## 20. Gaps
- Exact Go version constraint in go.mod.
- Whether stdio transport is supported (only HTTP at port 5000 was surfaced).
- Full list of supported database sources beyond those named.
- Homebrew formula source (tap or core).
- Specific contents of `server.json`.
