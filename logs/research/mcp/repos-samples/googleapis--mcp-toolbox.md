# Sample

Mirrors of `https://github.com/googleapis/mcp-toolbox`. Google APIs MCP toolbox — declarative tool authoring via YAML manifest, 5 distribution channels, HTTP-first on port 5000 across 8+ databases. 14.7k stars, Apache-2.0, default branch `main`, v1.1.0 released 2026-04-13, 1,798 commits, vendor-authored (Google).

## Server runtime

### Go with custom MCP implementation

Go (96.1%) with a custom MCP implementation; `server.json` declares MCP capability metadata. Single-binary build artifact. Specific Go version constraint not extracted from `go.mod`.

## Transport

### Streamable HTTP

HTTP MCP server bound to port 5000 at `/mcp` endpoint — HTTP-first, diverging from the stdio-first convention common elsewhere. Stdio transport not surfaced in the fetched view.

### Selection mechanism

Implicit default — HTTP is the default mode when the binary runs.

## Capability surface

### Tools plus resources plus prompts (full primitive coverage)

Tools, toolsets, and prompts declared in the YAML manifest. `sources` abstract database connections. A `prompts` section surfaces first-class MCP prompt support beyond tools — most MCP servers concentrate on tools; this one surfaces the prompts capability too.

### Spec-driven dynamic tool generation

YAML manifest is the primary configuration surface — sources, tools, toolsets, and prompts all live in `tools.yaml`, so admins configure by editing YAML rather than writing code. Declarative tool authoring without writing code is a different authoring surface from code-defined MCP servers.

## Configuration delivery

### YAML manifest (declarative tool authoring)

Primary configuration via `tools.yaml` defining sources, tools, toolsets, and prompts.

### CLI flags

`--config "tools.yaml"` points at the manifest; `--disable-reload` opts out of dynamic reloading.

### Sidecar config files (JSON / YAML / TOML / EDN)

`tools.yaml` is the canonical artifact; `gemini-extension.json` ships in-repo for Gemini host integration.

### Runtime reconfiguration tool

Dynamic reloading is on by default — config changes propagate without restart, with `--disable-reload` as the opt-out. Unusual for MCP servers, which typically re-exec; implies state that survives across configuration changes, a different lifecycle assumption.

## Authentication

### Multi-scheme upstream auth (basic / IAM / header / mTLS)

Delegates to per-source database auth schemes — IAM for Google Cloud (uses ambient/ADC credentials), plus standard credentials for PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Redis, Elasticsearch, and others. Configured per-source within `tools.yaml`.

### Cloud-native identity / credential chain

Google Cloud IAM uses ambient/ADC (Application Default Credentials) chain.

## Multi-tenancy

### Multi-spec / multi-source composition

Configuration is per-process; the manifest declares multiple sources, effectively multi-database but not multi-user. HTTP endpoint serves any connected MCP client.

## Distribution channel

### Pre-built binary release

GitHub release binaries (Linux AMD64, macOS ARM64/Intel, Windows AMD64).

### Docker / OCI image

`us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:$VERSION`.

### Go module via `go get` / `go install`

`go install github.com/googleapis/mcp-toolbox@v1.1.0`.

### Homebrew formula

`brew install mcp-toolbox` — Homebrew formula available; tap source unspecified.

### npm package wrapping native binary

NPM shim `@toolbox-sdk/server` wraps the Go binary — cross-ecosystem glue letting node-oriented hosts run a Go server by name. `npx @toolbox-sdk/server --config tools.yaml`.

### Multi-channel publication

Five distribution channels (binary, Docker, go install, Homebrew, npm shim) make cross-ecosystem discoverability a deliberate goal.

## Entry point and launch

### Native binary

`./toolbox --config "tools.yaml"`. Docker and npm shim variants run the same binary.

### Docker container entrypoint

Docker variant runs the same binary inside a container.

## Build and packaging

### npm/Node toolchain

`@toolbox-sdk/server` npm shim packaged separately as Node-ecosystem distribution.

## Container artifacts

### Dockerfile (single-stage, build-from-source)

Dockerfile present at repo root.

## Test stack

### Go stdlib testing

`/tests` directory; Go testing conventions implied. `.golangci.yaml` for lint.

## CI

### GitHub Actions

`.github/workflows/` directory present; `.ci/` directory holds additional CI configuration.

### Multi-system CI

Both `.ci/` and `.github/workflows/` directories suggest multi-system CI orchestration.

## Host integration

### Codex CLI / Copilot CLI / Gemini CLI

Gemini CLI is the first-party integration; a `gemini-extension.json` ships in-repo.

### First-party host extension manifest

`gemini-extension.json` is a host-specific extension manifest reflecting the project's origin at Google.

### Claude Code

Listed as a compatible client.

### Generic / host-agnostic snippet

Other hosts (Google Antigravity, Codex) consume the generic HTTP endpoint; listed as compatible clients.

## Repository layout

### Single-package source (language-conventional)

Single Go module. Top-level: `/cmd`, `/docs`, `/internal`, `/tests`, `/.ci`, `/.github`, `/.hugo`, `/.gemini`. `.gitmodules` present (submodules used).

## Documentation surface

### GitHub Pages / hosted docs site

`.hugo/` directory suggests Hugo-driven hosted docs site infrastructure.

### README plus docs directory

`/docs` directory present alongside README.

## Release and lifecycle

### Tagged release with version in changelog

v1.1.0 released 2026-04-13; 1,798 total commits.

### License — Permissive (MIT / Apache-2.0)

Apache-2.0 license.

### Active development

Active vendor-authored development at Google.

## Deployment topology

### Self-hosted HTTP server

HTTP-first on port 5000 — operator runs the binary as a long-running HTTP server.

### Containerized local process

Docker variant supports containerized local runs.
