# Sample

Stage-1 M4 merge of bins 6, 10.

## Vendor posture

How the project's relationship to its underlying service shapes the server.

### First-party vendor

Server is published by the same organization that owns the underlying service or product.

- PayPal publishes `@paypal/mcp` under the paypal-org npm namespace; Apache-2.0; first-party canonical despite low star count [`paypal--paypal-mcp-server`]
- Perplexity AI publishes `@perplexity-ai/mcp-server` from the `ppl-ai` GitHub org (org slug differs from brand name) [`ppl-ai--modelcontextprotocol`]
- Qdrant publishes `mcp-server-qdrant` on PyPI as official-vendor build [`qdrant--mcp-server-qdrant`]
- Redis publishes `redis-mcp-server` as official Redis MCP [`redis--mcp-redis`]
- Sentry publishes `@sentry/mcp-server` plus the hosted `mcp.sentry.dev` endpoint [`getsentry--sentry-mcp`]
- GitHub publishes `github/github-mcp-server` plus the hosted `api.githubcopilot.com` endpoint [`github--github-mcp-server`]
- Linear-adjacent first-party-style: Riza for the Riza code-interpreter service [`riza-io--riza-mcp`]
- Google publishes `googleapis/mcp-toolbox` (database toolbox) as a first-party Google build [`googleapis--mcp-toolbox`]

### Third-party / community

Server is published by an unrelated developer wrapping a vendor's API or SDK.

- `reminia--zendesk-mcp-server` is community, leverages community SDK `zenpy` rather than direct Zendesk REST — "wrap an existing community SDK" pattern [`reminia--zendesk-mcp-server`]
- `rohitg00--kubectl-mcp-server` is community-maintained for an open ecosystem (Kubernetes); CNCF Landscape listed [`rohitg00--kubectl-mcp-server`]
- `geropl--linear-mcp-go` is third-party Go wrapper for Linear API [`geropl--linear-mcp-go`]
- `hannesrudolph--sqlite-explorer-fastmcp-mcp-server` is community (no SQLite vendor relationship) [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- `hugoduncan--mcp-clj` is community Clojure implementation [`hugoduncan--mcp-clj`]
- `idosal--git-mcp` is community-built cloud SaaS over GitHub [`idosal--git-mcp`]
- `isaaccorley--planetary-computer-mcp` is community wrapper over Microsoft Planetary Computer STAC API [`isaaccorley--planetary-computer-mcp`]

### No vendor relationship

- `pragmar--mcp-server-webcrawl` operates over local archives — no vendor relationship at all (sidesteps vendor dimension) [`pragmar--mcp-server-webcrawl`]

> Observation across bins: low star count on first-party vendor releases ("official but unpromoted") — paypal-mcp at 9 stars, riza-mcp at 14 — is a recurring pattern worth flagging for downstream merger [`paypal--paypal-mcp-server`, `riza-io--riza-mcp`].

## Language and runtime

### Go

Custom Go MCP implementations dominate this corner. `github--github-mcp-server` ships a custom Go MCP implementation rooted at `cmd/github-mcp-server` with `server.json` declaring MCP capability. `googleapis--mcp-toolbox` likewise uses a custom Go implementation with `server.json`. `geropl--linear-mcp-go` uses the `mcp-go` SDK (`mark3labs/mcp-go` canonical) — Go 1.23+; Go module versioning typical.

### TypeScript / JavaScript

- `getsentry--sentry-mcp` runs on Node with TypeScript 98.3% under a pnpm workspace + Turbo monorepo, MCP TypeScript SDK inferred [`getsentry--sentry-mcp`]
- `idosal--git-mcp` runs TypeScript/JavaScript on Node.js (npx, pnpm, npm) using React Router 7, Vite, MCP SDK, and Cloudflare Workers (Wrangler) — atypical TS stack centered on edge-runtime deployment [`idosal--git-mcp`]
- `ppl-ai--modelcontextprotocol` — TypeScript 95.2%, Node.js runtime [`ppl-ai--modelcontextprotocol`]
- `paypal--paypal-mcp-server` — JS-majority with TS minor (75.7% JS / 15.8% TS) [`paypal--paypal-mcp-server`]
- `riza-io--riza-mcp` — JS-majority (72.2% JS / 27.8% TS) [`riza-io--riza-mcp`]

### Python

- `hannesrudolph--sqlite-explorer-fastmcp-mcp-server` is 100% Python on FastMCP 0.4.1 (1.x era), Python 3.6+ floor [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- `isaaccorley--planetary-computer-mcp` runs Python 87.5% (with TS 11.3% co-located VS Code extension) on raw `mcp` SDK (Anthropic MCP Python implementation), Python version pinned via `.python-version` [`isaaccorley--planetary-computer-mcp`]
- Python 3.9+ floor — `rohitg00--kubectl-mcp-server` [`rohitg00--kubectl-mcp-server`]
- Python 3.10+ floor — `pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis` [`pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`]
- Python 3.12+ floor — `reminia--zendesk-mcp-server` (newer than typical) [`reminia--zendesk-mcp-server`]

### Clojure

`hugoduncan--mcp-clj` runs Clojure 99.7% on Java runtime against MCP version `2024-11-05` using only Clojure standard library — specific Java version constraints not stated [`hugoduncan--mcp-clj`].

### Polyglot wrapper

- `rohitg00--kubectl-mcp-server` — Python core (81.2%) with TypeScript npm wrapper (17.0%) for dual-ecosystem distribution [`rohitg00--kubectl-mcp-server`]

## Framework / SDK choice

### FastMCP

- FastMCP 1.x (pre-2.x) — `fastmcp==0.4.1` pinned, Python 3.6+ floor [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- FastMCP 2.x exact-pinned `fastmcp == 2.7.0` — sensitive to FastMCP API drift [`qdrant--mcp-server-qdrant`]
- FastMCP (major version unsurfaced) — `rohitg00--kubectl-mcp-server` references FastMCP in config [`rohitg00--kubectl-mcp-server`]

### Raw `mcp` Python SDK (low-level)

- Raw `mcp` SDK (Anthropic Python implementation) — `isaaccorley--planetary-computer-mcp` notes raw MCP SDK in 2026 as a holdout — many newer servers have migrated to FastMCP [`isaaccorley--planetary-computer-mcp`]
- `mcp[cli]>=1.26.0` — `redis--mcp-redis` [`redis--mcp-redis`]
- `mcp>=1.3.0` (no `[cli]` extra) — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]
- `mcp>=1.1.2` (no `[cli]` extra) — `reminia--zendesk-mcp-server`; minimal 3-deps stack [`reminia--zendesk-mcp-server`]

### MCP TypeScript SDK

- Standard MCP TypeScript SDK — `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `getsentry--sentry-mcp` (inferred), `idosal--git-mcp` [`paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `getsentry--sentry-mcp`, `idosal--git-mcp`]

### mcp-go SDK

- `mark3labs/mcp-go` canonical — `geropl--linear-mcp-go` [`geropl--linear-mcp-go`]

### Custom / hand-rolled MCP implementation

- Custom Go MCP implementation — `github--github-mcp-server`, `googleapis--mcp-toolbox` (each ships `server.json`) [`github--github-mcp-server`, `googleapis--mcp-toolbox`]
- Hand-rolled Clojure MCP stack on `org.clojure/data.json` only — `hugoduncan--mcp-clj` [`hugoduncan--mcp-clj`]

> SDK / framework span: raw MCP Python SDK, FastMCP 1.x (pre-2.x), MCP TypeScript SDK, mcp-go (mark3labs), custom Go MCP implementations, and a hand-rolled Clojure stack on `org.clojure/data.json` only. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] anchors the FastMCP 1.x reference case for "how the FastMCP ecosystem looked before the 2.0 split".

## Transport

### stdio

Default for many local-install servers.

- [`geropl--linear-mcp-go`] selects via `serve` subcommand
- [`github--github-mcp-server`] selects via `github-mcp-server stdio` subcommand
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] is implicit — FastMCP CLI installer wires stdio with no explicit flag
- [`isaaccorley--planetary-computer-mcp`] is stdio-only implicit
- [`hugoduncan--mcp-clj`] selects via `clj -M:stdio-server` profile, recommended for Claude Desktop
- [`getsentry--sentry-mcp`] supports stdio for local self-hosted Sentry deployments
- [`paypal--paypal-mcp-server`] — stdio default via npx [`paypal--paypal-mcp-server`]
- [`pragmar--mcp-server-webcrawl`] — stdio with `--interactive` REPL flag for terminal mode [`pragmar--mcp-server-webcrawl`]
- [`redis--mcp-redis`] — stdio only; README notes "streamable-http transport will be added in the future" (planned, not shipped) [`redis--mcp-redis`]
- [`reminia--zendesk-mcp-server`] — stdio default [`reminia--zendesk-mcp-server`]

### HTTP / SSE / streamable-http

- [`googleapis--mcp-toolbox`] is HTTP-first on port 5000 at `/mcp` endpoint — diverges from the stdio-first convention
- [`hugoduncan--mcp-clj`] supports SSE/HTTP via `clj -M:sse-server` (default port 3001, customizable via `--port`)
- [`idosal--git-mcp`] is HTTP/HTTPS only via cloud endpoint `gitmcp.io`, plus SSE; auto-detected by IDE via direct HTTP URL specification
- [`getsentry--sentry-mcp`] supports HTTP via remote service `https://mcp.sentry.dev`
- [`github--github-mcp-server`] offers a separately-hosted remote service at `api.githubcopilot.com`
- [`ppl-ai--modelcontextprotocol`] — stdio default; HTTP server mode via `PORT` and `BIND_ADDRESS` env vars plus CORS support for shared deployments [`ppl-ai--modelcontextprotocol`]
- [`qdrant--mcp-server-qdrant`] — stdio (default), sse, streamable-http; FastMCP env-driven selection [`qdrant--mcp-server-qdrant`]
- [`rohitg00--kubectl-mcp-server`] — stdio (default), SSE, streamable-http, HTTP; default 0.0.0.0:8000 for HTTP modes [`rohitg00--kubectl-mcp-server`]

### In-memory

- [`hugoduncan--mcp-clj`] supports in-memory transport explicitly for testing — unusual; flagged as a notable axis

### Selection mechanism

CLI subcommand or profile is the most common pattern: `serve`, `stdio`, `:stdio-server`, `:sse-server`. [`googleapis--mcp-toolbox`] makes HTTP the default mode of the binary with no per-mode subcommand. [`idosal--git-mcp`] relies on IDE auto-detection from a URL string. [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] never exposes selection — FastMCP CLI installer hardcodes stdio. [`qdrant--mcp-server-qdrant`] uses FastMCP env-driven selection.

### Transport not documented

- `riza-io--riza-mcp` — transport not explicitly specified [`riza-io--riza-mcp`]

## Distribution

### Channels observed

| Channel | Samples |
|---------|---------|
| GitHub Releases pre-built binaries | [`geropl--linear-mcp-go`], [`github--github-mcp-server`] (58 releases), [`googleapis--mcp-toolbox`] (Linux AMD64, macOS ARM64/Intel, Windows AMD64) |
| `go install` | [`geropl--linear-mcp-go`], [`googleapis--mcp-toolbox`] |
| Docker image (GHCR / Artifact Registry / Docker Hub) | [`github--github-mcp-server`] (`ghcr.io/github/github-mcp-server`), [`googleapis--mcp-toolbox`] (`us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:$VERSION`), [`geropl--linear-mcp-go`] (Dockerfile present), [`rohitg00--kubectl-mcp-server`] (Docker Hub `rohitghumare64/kubectl-mcp-server:latest`), [`ppl-ai--modelcontextprotocol`], [`qdrant--mcp-server-qdrant`], [`redis--mcp-redis`] (`docker build -t mcp-redis .`), [`reminia--zendesk-mcp-server`] (Dockerfile installs from `requirements.lock`) |
| npm / npx | [`getsentry--sentry-mcp`] (`@sentry/mcp-server`), [`googleapis--mcp-toolbox`] (`@toolbox-sdk/server` shim), [`paypal--paypal-mcp-server`] (`@paypal/mcp` — `npx -y @paypal/mcp --tools=all`), [`ppl-ai--modelcontextprotocol`] (`@perplexity-ai/mcp-server` — `npx -y @perplexity-ai/mcp-server`), [`riza-io--riza-mcp`] (`@riza-io/riza-mcp` — `npx @riza-io/riza-mcp`), [`rohitg00--kubectl-mcp-server`] (`kubectl-mcp-server` npm wrapper invokes Python package — `npx -y kubectl-mcp-server`) |
| Homebrew | [`googleapis--mcp-toolbox`] (`brew install mcp-toolbox`) |
| PyPI (pip) | [`pragmar--mcp-server-webcrawl`] (`pip install mcp-server-webcrawl` only path; pip-only), [`rohitg00--kubectl-mcp-server`] (`pip install kubectl-mcp-server[ui]` — extras-gated UI bundle) |
| PyPI via uvx | [`qdrant--mcp-server-qdrant`] (`uvx mcp-server-qdrant`), [`redis--mcp-redis`] (`uvx --from redis-mcp-server@latest redis-mcp-server`; also `uvx --from git+https://...` for direct GitHub install) |
| Source clone + build | [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (`fastmcp install`), [`isaaccorley--planetary-computer-mcp`] (`uv sync`), [`idosal--git-mcp`] (`pnpm install`), [`hugoduncan--mcp-clj`] (Git dependency in `deps.edn`) |
| Cloud-hosted SaaS endpoint | [`idosal--git-mcp`] (`gitmcp.io/{owner}/{repo}`), [`getsentry--sentry-mcp`] (`mcp.sentry.dev`), [`github--github-mcp-server`] (`api.githubcopilot.com`) |
| Marketplace plugin (Claude Desktop) | [`getsentry--sentry-mcp`] |
| Smithery / one-click installer | [`qdrant--mcp-server-qdrant`] (one-click for Claude Desktop) |
| Shell download script | [`geropl--linear-mcp-go`] (automated download) |
| Editable-install-only ("developer-mode-as-release") | [`reminia--zendesk-mcp-server`] (no PyPI release; `uv venv && uv pip install -e .` is the user path; `uv --directory /path/to/repo run zendesk` is the host invocation) |

### Multi-channel breadth

- [`googleapis--mcp-toolbox`] surfaces 5 distribution channels (binary, Docker, go install, Homebrew, npm shim) — cross-ecosystem discoverability as a deliberate goal
- [`getsentry--sentry-mcp`] vends both an npm package and a Claude marketplace plugin distinct from the raw JSON snippet

### Cross-ecosystem glue

- NPM shim wrapping a Go binary — [`googleapis--mcp-toolbox`] ships `@toolbox-sdk/server` (npm) which wraps the Go binary so node-oriented hosts can run a Go server by name
- NPM shim wrapping a Python package — [`rohitg00--kubectl-mcp-server`] ships under both PyPI and npm (npm wrapper invokes the Python package); allows npm-only hosts to install without Python packaging knowledge — single-implementation-multiple-channels

### Hosted vs local

A clear axis. [`idosal--git-mcp`] is hosted-only (no local install, zero-auth cloud service). [`getsentry--sentry-mcp`] and [`github--github-mcp-server`] are dual-mode: official remote endpoint operated by the vendor alongside a self-run stdio binary. [`geropl--linear-mcp-go`], [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`], [`hugoduncan--mcp-clj`], [`isaaccorley--planetary-computer-mcp`], plus most bin-10 samples are local-only.

### Pre-`pyproject.toml` packaging

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] uses pre-`pyproject.toml`-era layout: `requirements.txt` + single `sqlite_explorer.py` script + no packaging. No `[project.scripts]`, no PyPI publish.

## Entry point / launch

### Subcommand-based binary

- [`geropl--linear-mcp-go`] uses `serve`, `setup --tool=cline`, `version` subcommands
- [`github--github-mcp-server`] uses `stdio` subcommand at `cmd/github-mcp-server/`

### Profile-based (Clojure deps)

- [`hugoduncan--mcp-clj`] launches via `clj -M:stdio-server` / `clj -M:sse-server` / `clj -M:sse-server --port 8080`

### npx / npm one-liners

- [`getsentry--sentry-mcp`] uses `npx @sentry/mcp-server@latest --access-token=...`
- [`paypal--paypal-mcp-server`] uses `npx -y @paypal/mcp --tools=all`
- [`ppl-ai--modelcontextprotocol`] uses `npx -y @perplexity-ai/mcp-server`
- [`riza-io--riza-mcp`] uses `npx @riza-io/riza-mcp`
- [`rohitg00--kubectl-mcp-server`] uses `npx -y kubectl-mcp-server` (wrapper invokes Python package)

### Python module / console-script invocation

- [`isaaccorley--planetary-computer-mcp`] launches via `python -m planetary_computer_mcp.server` — module-level invocation rather than console script
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] uses `fastmcp install sqlite_explorer.py` then host launches via configured MCP command, or direct run via `uv run --with fastmcp --with uvicorn fastmcp run /path/to/sqlite_explorer.py`
- `mcp-server-webcrawl = "mcp_server_webcrawl:main"` console script — [`pragmar--mcp-server-webcrawl`]
- `mcp-server-qdrant` console script → `mcp_server_qdrant.main:main` — [`qdrant--mcp-server-qdrant`]
- `redis-mcp-server = "src.main:cli"` — [`redis--mcp-redis`]; unusual `src.` prefix in module path
- `zendesk` console script → `zendesk_mcp_server:main` — [`reminia--zendesk-mcp-server`]; unusually short script name
- `kubectl-mcp-server` console script — [`rohitg00--kubectl-mcp-server`]

### Wrapper scripts and setup ergonomics

- [`geropl--linear-mcp-go`]'s `setup --tool=cline` subcommand automates host configuration — rare among MCP servers, most expect users to hand-edit JSON
- [`googleapis--mcp-toolbox`] uses `--config "tools.yaml"` flag with the same binary across Docker / npm shim / native invocations
- [`getsentry--sentry-mcp`] surfaces monorepo workspace scripts (`pnpm -w run cli`)

## Configuration surface

### Env vars

Common pattern.

- [`geropl--linear-mcp-go`]: `LINEAR_API_KEY` (required)
- [`github--github-mcp-server`]: `GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_HOST`, `GITHUB_TOOLSETS`, `GITHUB_TOOLS`, `GITHUB_READ_ONLY`, `GITHUB_INSIDERS`
- [`getsentry--sentry-mcp`]: `SENTRY_ACCESS_TOKEN`, `EMBEDDED_AGENT_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SENTRY_HOST`, `MCP_DISABLE_SKILLS`
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: `SQLITE_DB_PATH` (required; only config knob)
- [`qdrant--mcp-server-qdrant`] — env-only; CLI args explicitly deprecated [`qdrant--mcp-server-qdrant`]
- [`ppl-ai--modelcontextprotocol`] — env-dominant (`PERPLEXITY_API_KEY`, `PERPLEXITY_TIMEOUT_MS`, `PERPLEXITY_BASE_URL`, `PORT`, `BIND_ADDRESS`, proxy config) [`ppl-ai--modelcontextprotocol`]

### CLI flags

- [`geropl--linear-mcp-go`]: `--write-access`, `--auto-approve`, `--tool`
- [`github--github-mcp-server`]: `--toolsets`, `--tools`, `--read-only`, `--lockdown-mode`, `--dynamic-toolsets`
- [`googleapis--mcp-toolbox`]: `--config`, `--disable-reload`
- [`hugoduncan--mcp-clj`]: `--port`
- [`redis--mcp-redis`] — three sources: CLI flags (extensive: `--url`, `--host`, `--port`, `--username`, `--password`, `--db`, `--ssl`, granular SSL knobs), env vars + `.env` files, Redis URI scheme [`redis--mcp-redis`]
- [`pragmar--mcp-server-webcrawl`] — CLI flags (`--crawler`, `--datasrc`, `--interactive`) [`pragmar--mcp-server-webcrawl`]

### Mixed env + CLI flags

- [`paypal--paypal-mcp-server`] — env vars for credentials/environment, CLI flags for tool selection (`--tools=all`) and token override [`paypal--paypal-mcp-server`]
- [`rohitg00--kubectl-mcp-server`] — env vars (`KUBECONFIG`, `MCP_DEBUG`, `MCP_LOG_FILE`, `MCP_BROWSER_*`, `MCP_AUTH_*`) plus CLI flags (`--disable-destructive`, transport/host/port) [`rohitg00--kubectl-mcp-server`]

### YAML manifest

- [`googleapis--mcp-toolbox`] uses `tools.yaml` as primary configuration surface — declares sources, tools, toolsets, and prompts. Admins configure by editing YAML rather than writing code

### `.env` file via python-dotenv

- [`reminia--zendesk-mcp-server`] — `.env` file with `python-dotenv`; `.env.example` as dev-config template [`reminia--zendesk-mcp-server`]

### Host-managed JSON config

- [`hugoduncan--mcp-clj`] integrates via `claude_desktop_config.json` with bash interpreter, project path, and env vars in config
- [`idosal--git-mcp`] documents JSON `mcp.json` for 8 IDEs (Claude Desktop, Cursor, Windsurf, VSCode, Cline, Highlight AI, Augment Code, Msty AI)
- [`isaaccorley--planetary-computer-mcp`] uses function-call parameters + environment
- [`riza-io--riza-mcp`] — JSON configuration file (Claude Desktop format); env vars for API credentials [`riza-io--riza-mcp`]

### Hot reload

- [`googleapis--mcp-toolbox`] dynamic reloading on by default; `--disable-reload` opts out — implies state survives across configuration changes; unusual for MCP servers (most re-exec)

## Authentication

### Static API key / token (env-supplied)

- [`geropl--linear-mcp-go`] (`LINEAR_API_KEY`)
- [`github--github-mcp-server`] (`GITHUB_PERSONAL_ACCESS_TOKEN`)
- [`getsentry--sentry-mcp`] (Sentry user tokens with scopes `org:read project:read project:write team:read team:write event:write`)
- [`ppl-ai--modelcontextprotocol`] — `PERPLEXITY_API_KEY` from Perplexity API Portal
- [`qdrant--mcp-server-qdrant`] — `QDRANT_API_KEY` for Qdrant Cloud or remote
- [`riza-io--riza-mcp`] — `RIZA_API_KEY` env var

### OAuth (hosted)

- [`github--github-mcp-server`] supports OAuth for the remote hosted server (VS Code 1.101+ has native support)
- [`getsentry--sentry-mcp`] supports OAuth App for the hosted `mcp.sentry.dev` endpoint

### OAuth 2.0 client credentials

- [`paypal--paypal-mcp-server`] — bearer token, valid 3-8 hours sandbox / 8 hours production. Server holds single merchant's token for the session. Token-refresh handling is unclear from surface — long sessions may need rotation by the caller [`paypal--paypal-mcp-server`]

### OAuth 2.1 (RFC 9728) — optional bolt-on

- [`rohitg00--kubectl-mcp-server`] — optional OAuth 2.1 layer on top of stdio/HTTP via `MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE`. Underlying Kubernetes API uses kubeconfig [`rohitg00--kubectl-mcp-server`]

### Delegated to underlying source auth

- [`googleapis--mcp-toolbox`] delegates to database auth schemes — IAM for Google Cloud (ambient/ADC credentials), plus standard credentials for PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Redis, Elasticsearch, others

### Service-native credentials

- [`redis--mcp-redis`] — Redis ACL (username/password) [`redis--mcp-redis`]
- [`reminia--zendesk-mcp-server`] — Zendesk API credentials via `zenpy` (token or username/password); from `.env` [`reminia--zendesk-mcp-server`]

### Cloud-native identity (rare)

- [`redis--mcp-redis`] — Azure EntraID with three sub-flows (service principal, managed identity, default Azure credential) plus automatic token renewal with background refresh. Reflects enterprise Azure deployment pressure; rare among community MCPs [`redis--mcp-redis`]

### kubeconfig file

- [`rohitg00--kubectl-mcp-server`] — consumes `~/.kube/config` for Kubernetes API auth [`rohitg00--kubectl-mcp-server`]

### None / public

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (local SQLite, no credentials)
- [`isaaccorley--planetary-computer-mcp`] (Planetary Computer STAC API publicly accessible)
- [`idosal--git-mcp`] (zero-auth public-repo cloud service)
- [`hugoduncan--mcp-clj`] (no explicit mechanism documented; assumes transport-layer security)
- [`pragmar--mcp-server-webcrawl`] — operates entirely on local archives; no service auth at all. Demonstrates that valid MCP servers need not talk to external services [`pragmar--mcp-server-webcrawl`]

## Multi-tenancy

### Single-user per process

- [`geropl--linear-mcp-go`] (API key ties to one Linear workspace)
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (one SQLite file per server instance pinned via env var)
- [`hugoduncan--mcp-clj`]
- [`isaaccorley--planetary-computer-mcp`]
- Single-merchant per process — [`paypal--paypal-mcp-server`]
- Single-user per API key — [`ppl-ai--modelcontextprotocol`], [`riza-io--riza-mcp`]
- One Qdrant instance + one default collection — [`qdrant--mcp-server-qdrant`]
- Single Redis connection per server (cluster mode is connection topology, not per-request tenancy) — [`redis--mcp-redis`]
- Single Zendesk subdomain per instance — [`reminia--zendesk-mcp-server`]
- One data source per launch (multiple sources require multiple launches) — [`pragmar--mcp-server-webcrawl`]
- Single-user per process; OAuth bolt-on suggests tenant support but documented as single kubeconfig context per server — [`rohitg00--kubectl-mcp-server`]

### Single-user stdio + per-user OAuth on hosted

- [`getsentry--sentry-mcp`] (single-user per stdio process, per-user OAuth on hosted)
- [`github--github-mcp-server`] (one PAT one identity for stdio, per-user OAuth in hosted mode)

### Per-process / multi-source

- [`googleapis--mcp-toolbox`] is per-process; manifest can declare multiple sources (multi-database but not multi-user); HTTP endpoint serves any connected MCP client

### Per-repo parameterized tenant

- [`idosal--git-mcp`] uses per-repository tenant parameterized by owner/repo via URL — cloud-hosted single service with multi-repo support

## Capabilities exposed

Tool surface size, MCP primitives used, and how the server organizes its capabilities.

### Tool-surface size

- Tools-only minimal — [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (3 tools: `read_query`, `list_tables`, `describe_table`; no resources/prompts/sampling/roots), [`isaaccorley--planetary-computer-mcp`] (2 tools: `download_data`, `download_geometries`), [`idosal--git-mcp`] (4 tools: `fetch_<repo>_documentation`, `search_<repo>_documentation`, `search_<repo>_code`, `fetch_url_content`)
- Minimal (≤6 tools) — [`qdrant--mcp-server-qdrant`] (2: store, find), [`riza-io--riza-mcp`] (6: create_tool, fetch_tool, execute_tool, edit_tool, list_tools, execute_code), [`ppl-ai--modelcontextprotocol`] (4: search, ask, research, reason), [`reminia--zendesk-mcp-server`] (~6 ticket tools)
- Read-only default + write-gated — [`geropl--linear-mcp-go`] (read-only default `linear_search_issues`, `linear_get_user_issues`, `linear_get_issue`, `linear_get_issue_comments`, `linear_get_teams`; write-gated `linear_create_issue`, `linear_update_issue`, `linear_add_comment`, `linear_reply_to_comment`, `linear_update_issue_comment`)
- Medium (~30 tools, domain-grouped) — [`paypal--paypal-mcp-server`] (Invoices, Payments, Disputes, Shipments, Catalog, Subscriptions, Reporting)
- Large (8 categories, multi-DS) — [`redis--mcp-redis`] (strings, hashes, lists, sets, sorted sets, pub/sub, streams, JSON, plus vector search, server mgmt, docs search)
- Very large (253 tools across ~20 categories) — [`rohitg00--kubectl-mcp-server`] partitioned by Kubernetes resource kind
- Toolset-gated very large (~100+ across 20+ toolsets) — [`github--github-mcp-server`] (repos, issues, pull_requests, actions, etc.) with granular toolset/tool gating via flags
- Two-tool minimal interface — [`hugoduncan--mcp-clj`] ships `clj-eval` (evaluate Clojure expressions) and `ls` (list files with gitignore support, depth/limit options); custom tools can be added dynamically via API

### Tool-surface scoping at launch

- [`paypal--paypal-mcp-server`] exposes a `--tools=all` flag with selective subsets via the same flag — opt-in capability scoping reduces prompt-window noise for users who only need one sub-surface
- [`rohitg00--kubectl-mcp-server`] gates browser-automation feature (26 tools) on `MCP_BROWSER_ENABLED` — env-flag-gated optional bundles
- [`rohitg00--kubectl-mcp-server`] ships safety flag `--disable-destructive` to suppress destructive operations
- [`github--github-mcp-server`] surfaces `--read-only` flag, lockdown mode (filters public repo content), dynamic toolsets allowing runtime discovery
- [`geropl--linear-mcp-go`] writes gated behind explicit `--write-access` flag

### Tool semantics

- [`riza-io--riza-mcp`] separates patterns for saved-vs-arbitrary code execution: `create_tool` (save), `execute_tool` (run saved), `execute_code` (run arbitrary without saving). `edit_tool` capability for modifying saved tools is unusual among MCP servers
- [`paypal--paypal-mcp-server`] tools grouped by business domain (Invoices/Payments/Disputes…)
- [`ppl-ai--modelcontextprotocol`] four-tool surface maps 1:1 to product/model offerings (search → Search API, ask → sonar-pro, research → sonar-deep-research, reason → sonar-reasoning-pro) — tool boundaries mirror product tiers rather than low-level API endpoints
- [`redis--mcp-redis`] per-data-structure tool grouping mirrors Redis command families
- URL-aware operations — [`geropl--linear-mcp-go`] accepts Linear comment URLs directly without manual ID extraction — a UX choice rather than capability

### Tool ergonomics / output control

- [`ppl-ai--modelcontextprotocol`] has optional `strip_thinking` parameter to remove reasoning tags from output — token-saving feature giving caller control over verbosity

### Tools + first-class prompts

- [`googleapis--mcp-toolbox`] surfaces tools, toolsets, AND prompts via YAML manifest — most MCP servers concentrate on tools; this one surfaces the prompts capability too

### Tools + "Skills" abstraction

- [`getsentry--sentry-mcp`] makes "Skills" first-class — `MCP_DISABLE_SKILLS` env var toggles skill subsets (skills live under `.agents/skills/`). README positions the project as "primarily designed for human-in-the-loop coding agents." A higher-level behavioral primitive distinct from tools

### Embedded LLM invocation

- [`getsentry--sentry-mcp`] supports an embedded agent provider — `EMBEDDED_AGENT_PROVIDER` ('openai' | 'anthropic') with provider-specific API keys lets the MCP server invoke an LLM internally. Unusual; most MCP servers are pure tool-callers

### Built-in REPL evaluation

- [`hugoduncan--mcp-clj`] ships `clj-eval` and `ls`; custom tools can be added dynamically via API

### MCP primitives beyond tools

- **Resources** — [`reminia--zendesk-mcp-server`] uses the resources primitive explicitly: `zendesk://knowledge-base`. Splits read-via-resources from write-via-tools. One of the clearer uses of MCP resources rather than overloading tools for read access [`reminia--zendesk-mcp-server`]
- **Resources + prompts** — [`rohitg00--kubectl-mcp-server`] exposes 8 resources, 8 prompts alongside its 253 tools [`rohitg00--kubectl-mcp-server`]
- **"Prompt routines" (Markdown, not MCP prompts protocol)** — [`pragmar--mcp-server-webcrawl`] ships pre-authored Markdown prompts for autonomous tasks (SEO audits, 404 detection, performance analysis) under `prompts/`. Concept adjacent to skills but shipped as plain Markdown rather than as MCP prompts protocol resources [`pragmar--mcp-server-webcrawl`]

### Read-only-by-default

- [`geropl--linear-mcp-go`] writes gated behind explicit `--write-access` flag
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] enforces read-only at the tool layer (query validation + row caps), not DB-level
- [`github--github-mcp-server`] surfaces `--read-only` flag

### LLM-targeted output synthesis

- [`isaaccorley--planetary-computer-mcp`] generates visualizations for LLM analysis — server synthesizes images for the model to interpret. Multi-format outputs (GeoTIFF, GeoParquet, Zarr) — uncommon in MCP servers; implies large-file handling

### Specialty capabilities

- **In-server documentation search** — [`redis--mcp-redis`] ships a docs-search tool calling a separate HTTP endpoint via `MCP_DOCS_SEARCH_URL`; RAG-style augmentation attached to a database server [`redis--mcp-redis`]
- **Vector search alongside core data** — [`redis--mcp-redis`] first-classes vector search alongside Redis data structures [`redis--mcp-redis`]
- **Cluster mode as config axis** — [`redis--mcp-redis`] `--cluster-mode` flag [`redis--mcp-redis`]
- **Boolean fulltext + multi-extraction-mode search** — [`pragmar--mcp-server-webcrawl`] supports field-specific queries (url, content, headers, type, status, id, size); content filtering by type (html, img, pdf, video) and HTTP status; extraction modes markdown / snippet / regex / XPath; thumbnail generation for images [`pragmar--mcp-server-webcrawl`]
- **Multi-format crawler-archive compatibility** — [`pragmar--mcp-server-webcrawl`] reads ArchiveBox, HTTrack, InterroBot, Katana, SiteOne, WARC, wget archives. Unusually broad — most crawler tools target one format [`pragmar--mcp-server-webcrawl`]

## Domain decoupling

When a server allows the user to swap a cross-cutting concern via configuration.

- **Embedding model/provider decoupled from storage** — [`qdrant--mcp-server-qdrant`] exposes `EMBEDDING_MODEL` and `EMBEDDING_PROVIDER` env vars independently of the storage backend; `fastembed` (ONNX-backed Qdrant lib) gives default no-API-key install [`qdrant--mcp-server-qdrant`]
- **Local-vs-remote backend toggle** — [`qdrant--mcp-server-qdrant`] `QDRANT_LOCAL_PATH` vs `QDRANT_URL` makes local-path mode a single env switch [`qdrant--mcp-server-qdrant`]
- **Sandbox/production environment branch** — [`paypal--paypal-mcp-server`] `PAYPAL_ENVIRONMENT` selects SANDBOX or PRODUCTION via single binary; not separate entry points [`paypal--paypal-mcp-server`]

## Observability

### Conventions and gaps

Most bin-6 samples do not document logging destination/format. [`geropl--linear-mcp-go`]: not extracted; Go stdio servers typically log to stderr. [`github--github-mcp-server`]: likely stderr per Go-binary convention. [`googleapis--mcp-toolbox`]: standard Go stderr logging likely. [`isaaccorley--planetary-computer-mcp`]: not documented. [`hugoduncan--mcp-clj`]: no explicit observability documented. [`idosal--git-mcp`]: not documented; presumed server-side. [`getsentry--sentry-mcp`]: not explicitly extracted.

### Log-level via env var

- [`ppl-ai--modelcontextprotocol`] — `PERPLEXITY_LOG_LEVEL` [`ppl-ai--modelcontextprotocol`]
- [`redis--mcp-redis`] — `MCP_REDIS_LOG_LEVEL` (DEBUG/INFO/WARNING/ERROR/CRITICAL); default WARNING [`redis--mcp-redis`]
- [`rohitg00--kubectl-mcp-server`] — `MCP_DEBUG` + `MCP_LOG_FILE` [`rohitg00--kubectl-mcp-server`]

### Framework-default logging

- [`qdrant--mcp-server-qdrant`] — FastMCP-standard logging via env config [`qdrant--mcp-server-qdrant`]

### Interactive REPL doubling as debug surface

- [`pragmar--mcp-server-webcrawl`] — `--interactive` terminal mode is a custom debug surface; rare among MCP servers that typically rely on MCP Inspector [`pragmar--mcp-server-webcrawl`]

### Stdio cleanliness pressure

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] explicitly notes "progress output suppression for clean JSON responses" as a deliberate behavior — reflects stdio-protocol cleanliness pressure where any stray stdout corrupts the JSON-RPC stream

### Not documented

- [`paypal--paypal-mcp-server`], [`reminia--zendesk-mcp-server`], [`riza-io--riza-mcp`] — observability not extracted

## Host integrations

### Claude Desktop

Documented as a host config target by:

- [`geropl--linear-mcp-go`] (Cline emphasis, not Desktop directly)
- [`github--github-mcp-server`] (JSON snippet using Docker or local binary)
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (via FastMCP CLI install)
- [`hugoduncan--mcp-clj`] (sample `claude_desktop_config.json`)
- [`idosal--git-mcp`]
- [`getsentry--sentry-mcp`] (as marketplace plugin)
- [`paypal--paypal-mcp-server`] — primary host, JSON config snippets [`paypal--paypal-mcp-server`]
- [`ppl-ai--modelcontextprotocol`] — quick-install badge [`ppl-ai--modelcontextprotocol`]
- [`pragmar--mcp-server-webcrawl`] — primary; documented as a requirement [`pragmar--mcp-server-webcrawl`]
- [`qdrant--mcp-server-qdrant`] — JSON snippet for `claude_desktop_config.json` [`qdrant--mcp-server-qdrant`]
- [`redis--mcp-redis`] — JSON config example [`redis--mcp-redis`]
- [`reminia--zendesk-mcp-server`] — `uv --directory` invocation pattern [`reminia--zendesk-mcp-server`]
- [`riza-io--riza-mcp`] — primary [`riza-io--riza-mcp`]
- [`rohitg00--kubectl-mcp-server`] — JSON `mcpServers` entry [`rohitg00--kubectl-mcp-server`]

### Claude Code

- [`getsentry--sentry-mcp`] integration documented
- [`googleapis--mcp-toolbox`] listed as compatible client
- [`hugoduncan--mcp-clj`] not explicitly documented

### VS Code / VS Code MCP / GitHub Copilot

- [`github--github-mcp-server`] VS Code 1.101+ native MCP support with OAuth or PAT auth
- [`isaaccorley--planetary-computer-mcp`] ships a parallel TypeScript VS Code extension under `vscode-extension/`
- [`idosal--git-mcp`] documents JSON `mcp.json` for VSCode
- [`ppl-ai--modelcontextprotocol`] (quick-install badge) [`ppl-ai--modelcontextprotocol`]
- [`qdrant--mcp-server-qdrant`] (JSON snippet with `uvx`) [`qdrant--mcp-server-qdrant`]
- [`redis--mcp-redis`] — VS Code + GitHub Copilot, requires `chat.agent.enabled: true` [`redis--mcp-redis`]

### Cursor

- [`getsentry--sentry-mcp`], [`github--github-mcp-server`] (Docker-based config with PAT env injection), [`idosal--git-mcp`]
- [`paypal--paypal-mcp-server`], [`ppl-ai--modelcontextprotocol`], [`qdrant--mcp-server-qdrant`], [`rohitg00--kubectl-mcp-server`]

### Windsurf

- [`github--github-mcp-server`] (Docker-based with PAT env injection), [`idosal--git-mcp`]
- [`ppl-ai--modelcontextprotocol`] (badge), [`qdrant--mcp-server-qdrant`] (JSON snippet), [`rohitg00--kubectl-mcp-server`]

### JetBrains IDEs

- [`github--github-mcp-server`] (Docker-based with PAT env injection)

### Cline

- [`geropl--linear-mcp-go`] (primary; dedicated `setup --tool=cline`)
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (manual MCP configuration example with `"command": "uv"`, `"args": ["run", "--with", "fastmcp", ...]`)
- [`idosal--git-mcp`]
- [`paypal--paypal-mcp-server`] [`paypal--paypal-mcp-server`]

### Gemini CLI / Google Antigravity / Codex

- [`googleapis--mcp-toolbox`] ships in-repo `gemini-extension.json` and lists Google Antigravity, Claude Code, Codex as compatible clients

### Highlight AI / Augment Code / Msty AI

- [`idosal--git-mcp`] documents JSON `mcp.json` configs for these clients alongside the more common ones

### Kiro

- [`ppl-ai--modelcontextprotocol`] — quick-install badge [`ppl-ai--modelcontextprotocol`]

### Augment

- [`redis--mcp-redis`] — supported via Easy MCP feature [`redis--mcp-redis`]

### OpenAI Agents SDK

- [`redis--mcp-redis`] [`redis--mcp-redis`]

### "15+ other clients" / generic MCP

- [`rohitg00--kubectl-mcp-server`] — same JSON shape across all [`rohitg00--kubectl-mcp-server`]

### Smithery

- [`qdrant--mcp-server-qdrant`] — one-click install for Claude Desktop [`qdrant--mcp-server-qdrant`]

### Other extension points

- [`geropl--linear-mcp-go`] reachable via MCP Registry; `--tool` flag is a scoped extension point (currently only `cline`, but signals plan to automate other host configurations)

## Claude Code plugin wrapper

### Present in-repo

- [`getsentry--sentry-mcp`] ships both `.claude-plugin/` directory and `.mcp.json` at repo root — full Claude plugin wrapper in-repo. The server vends itself as a Claude plugin, not just a raw MCP binary. Rare; most servers leave host integration to external config

### Absent

- [`geropl--linear-mcp-go`], [`github--github-mcp-server`] (host integration via external `claude_desktop_config.json`), [`googleapis--mcp-toolbox`] (only `gemini-extension.json` shipped), [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`], [`hugoduncan--mcp-clj`], [`idosal--git-mcp`], [`isaaccorley--planetary-computer-mcp`]
- [`paypal--paypal-mcp-server`], [`ppl-ai--modelcontextprotocol`], [`pragmar--mcp-server-webcrawl`], [`qdrant--mcp-server-qdrant`], [`redis--mcp-redis`], [`reminia--zendesk-mcp-server`], [`riza-io--riza-mcp`], [`rohitg00--kubectl-mcp-server`]

## Tests

### Frameworks

| Framework | Samples |
|-----------|---------|
| go-vcr (recorded HTTP cassettes) | [`geropl--linear-mcp-go`] (cassettes in `testdata/`; live test workspace `linear.app/linear-mcp-go-test` for re-recording; flags `-record=true`, `-recordWrites=true`) |
| Go stdlib testing | [`github--github-mcp-server`] (E2E in `e2e/`), [`googleapis--mcp-toolbox`] (`/tests`) |
| pytest | [`isaaccorley--planetary-computer-mcp`] (`uv run pytest`, `tests/`) |
| pytest with async | [`qdrant--mcp-server-qdrant`] (pytest >=8.3.3, pytest-asyncio (auto mode); in-memory Qdrant fixture), [`redis--mcp-redis`] (pytest + pytest-asyncio + pytest-cov + pytest-mock; PEP 735 dependency-groups split into `dev` and `test`; `addopts = --cov=src --cov-fail-under=80` (coverage gate enforced); `asyncio_mode = "auto"`) |
| pytest, async unspecified | [`rohitg00--kubectl-mcp-server`] (234+ passing pytest tests; unit + integration + server-initialization suites) |
| Vitest + Playwright | [`idosal--git-mcp`] (`vitest.config.ts` units, `playwright.config.ts` E2E, `npm run test`) |
| pnpm test + eval harness | [`getsentry--sentry-mcp`] (`pnpm test` units, `pnpm eval` evaluations/scenario tests; MCP Inspector for local testing) |
| Jest | [`paypal--paypal-mcp-server`] |
| vitest | [`ppl-ai--modelcontextprotocol`] |
| Clojure tests.edn + clj-kondo | [`hugoduncan--mcp-clj`] (testing investigation notes; clj-kondo lint) |
| None observed | [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] |
| Not extracted | [`pragmar--mcp-server-webcrawl`], [`reminia--zendesk-mcp-server`], [`riza-io--riza-mcp`] |

### Notable patterns

- [`geropl--linear-mcp-go`] go-vcr cassette testing: full integration tests run offline against recorded fixtures — reproducible without Linear credentials
- [`getsentry--sentry-mcp`] evaluation harness alongside unit tests — distinguishes behavioral regression from code regression

## CI

### GitHub Actions present

- [`geropl--linear-mcp-go`] (automated testing on pushes/PRs, automated releases on version tags)
- [`github--github-mcp-server`] (workflows present, contents not enumerated)
- [`googleapis--mcp-toolbox`] (`.ci/` plus `.github/workflows/`, `.golangci.yaml` lint)
- [`idosal--git-mcp`] (`e2e-tests.yml`, `run-tests.yml`)
- [`isaaccorley--planetary-computer-mcp`] (configured)
- [`hugoduncan--mcp-clj`] (likely; `cliff.toml` for release notes)
- [`getsentry--sentry-mcp`] (implied by monorepo standard)
- [`paypal--paypal-mcp-server`], [`ppl-ai--modelcontextprotocol`], [`qdrant--mcp-server-qdrant`], [`redis--mcp-redis`], [`reminia--zendesk-mcp-server`], [`rohitg00--kubectl-mcp-server`] — all have `.github/workflows/`
- [`qdrant--mcp-server-qdrant`] documented jobs: lint/type-check/test + release
- [`redis--mcp-redis`] — codecov integration; specifics not extracted

### None / not documented

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (no `.github/workflows`)
- [`pragmar--mcp-server-webcrawl`], [`riza-io--riza-mcp`] — not documented

## Container / packaging artifacts

### Dockerfile present

- [`geropl--linear-mcp-go`] (Dockerfile + `.devcontainer/` for dev)
- [`github--github-mcp-server`] (multi-platform Dockerfile, no compose/Helm/brew)
- [`googleapis--mcp-toolbox`] (Dockerfile + Homebrew formula, external tap inferred)
- [`ppl-ai--modelcontextprotocol`], [`qdrant--mcp-server-qdrant`], [`redis--mcp-redis`], [`reminia--zendesk-mcp-server`], [`rohitg00--kubectl-mcp-server`] (also Docker Hub published image)
- [`reminia--zendesk-mcp-server`] — Dockerfile installs from `requirements.lock` for build reproducibility

### Cloud-native deployment

- [`idosal--git-mcp`] no Dockerfile; Cloudflare Workers cloud-native deployment

### None observed

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`], [`hugoduncan--mcp-clj`], [`isaaccorley--planetary-computer-mcp`], [`getsentry--sentry-mcp`] (not explicitly documented)
- [`paypal--paypal-mcp-server`], [`pragmar--mcp-server-webcrawl`], [`riza-io--riza-mcp`]

## Repo layout

### Single-package

- [`geropl--linear-mcp-go`] (Go: `cmd/` + `pkg/`)
- [`github--github-mcp-server`] (single Go module rooted at `cmd/github-mcp-server` with supporting packages, `server.json` at root)
- [`googleapis--mcp-toolbox`] (single Go module: `/cmd`, `/docs`, `/internal`, `/tests`, `/.ci`, `/.github`, `/.hugo`, `/.gemini`; `.gitmodules` present)
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] (single-file script `sqlite_explorer.py` with requirements + docs)
- [`idosal--git-mcp`] (single-package React/TS with Cloudflare integration: `app/`, `src/`, `static/`, `tests/`, `dist/`, `wrangler.jsonc`, `react-router.config.ts`, `vite.config.ts`, `vitest.config.ts`)

### Single-package Python

- [`pragmar--mcp-server-webcrawl`] (`docs/`, `prompts/`, `sphinx/`)
- [`qdrant--mcp-server-qdrant`] (`src/mcp_server_qdrant/`)
- [`redis--mcp-redis`] (`src/`, `tests/`, `examples/`, Dockerfile, `pyproject.toml`, `server.json`, `uv.lock`)
- [`reminia--zendesk-mcp-server`] (`zendesk_mcp_server/`)
- [`rohitg00--kubectl-mcp-server`] — single-package, modular submodules per resource kind (pods.py, deployments.py, helm.py); separate `resources/` and `prompts/` dirs

### Single-package Node.js / mixed JS+TS

- [`paypal--paypal-mcp-server`] — JS-majority with Shell auxiliary scripts
- [`ppl-ai--modelcontextprotocol`] — single-package TypeScript, source in `/src`
- [`riza-io--riza-mcp`] — minimal (README + `/typescript/` directory)

### Monorepo

- [`getsentry--sentry-mcp`] (pnpm workspaces + Turbo; multiple packages under `/packages`; `.agents/skills/` for skill definitions; `.claude-plugin/` and `.mcp.json` at root)

### Polylith-style modular (Clojure)

- [`hugoduncan--mcp-clj`] (`bases/`, `components/`, `projects/` + supporting `design/`, `dev/`, `development/`, `doc/`, `spec/`, `scripts/`; `deps.edn`, `tests.edn`, `cliff.toml`, `.cljstyle`; `.clj-kondo/`, `.github/`, `.claude/`, `.mcp-vector-search/`)

### Mixed-language monorepo

- [`isaaccorley--planetary-computer-mcp`] (monorepo-ish: Python `src/` with `core/`, `tools/`, `server.py`, plus parallel `vscode-extension/` TypeScript subproject)

## Notable structural choices

### Read-only-by-default safety posture

- [`geropl--linear-mcp-go`] gates writes behind `--write-access` flag rather than being default
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] enforces read-only at the tool layer (query validation + row caps)
- [`github--github-mcp-server`] offers `--read-only` flag

> More conservative than most MCPs which ship full capabilities unconditionally.

### Auto-approve configurability

- [`geropl--linear-mcp-go`] users can mark specific tools safe to run without per-call confirmation

### Setup ergonomics

- [`geropl--linear-mcp-go`]'s `setup` subcommand replaces manual JSON config editing — rare; most expect users to hand-edit JSON

### Dynamic reloading

- [`googleapis--mcp-toolbox`] dynamic reloading on by default; `--disable-reload` opts out — implies state survives across configuration changes

### Toolset gating + behavior modes

- [`github--github-mcp-server`] surfaces `--read-only`, `--lockdown-mode`, `--insiders` as behavior envelopes rather than capability toggles, separating policy from toolset selection. `--dynamic-toolsets` exposes runtime-discoverable tools, affecting how hosts cache tool listings

### Capability scoping at launch

- `--tools=all` opt-in tool surface — [`paypal--paypal-mcp-server`] reduces prompt-window noise [`paypal--paypal-mcp-server`]
- `MCP_BROWSER_ENABLED` env-gated bundle — [`rohitg00--kubectl-mcp-server`] browser-automation toggle [`rohitg00--kubectl-mcp-server`]
- `[ui]` extra-gated dashboards — [`rohitg00--kubectl-mcp-server`] pip extras enable dashboard feature [`rohitg00--kubectl-mcp-server`]
- `--disable-destructive` safety flag — [`rohitg00--kubectl-mcp-server`] suppresses destructive ops [`rohitg00--kubectl-mcp-server`]

### Cloud-hosted SaaS endpoint

- [`idosal--git-mcp`] removes installation friction. Zero-auth model for public repos. React Router 7 + Vite frontend, Biome unified lint/format. Parameterized repository endpoints — one deployment serves every GitHub repo

### Hosted + local hybrid

- [`getsentry--sentry-mcp`], [`github--github-mcp-server`] — official remote MCP endpoint operated by vendor alongside self-run stdio binary

### Embedded LLM invocation as architecture

- [`getsentry--sentry-mcp`] server-internal LLM invocation as architecture pattern — shifts some "agent" responsibility inside the MCP boundary

### Skills as bundled capability layer

- [`getsentry--sentry-mcp`] Skills toggleable per-deployment via `MCP_DISABLE_SKILLS`. A higher-level behavioral primitive distinct from tools. Skills live in `.agents/skills/`

### Co-located non-MCP integration

- [`isaaccorley--planetary-computer-mcp`] ships a VS Code extension alongside the MCP server — parallel non-MCP integration path in the same repo

### LLM-targeted output synthesis as architecture

- [`isaaccorley--planetary-computer-mcp`] generates visualizations for LLM analysis — server synthesizes images for the model to interpret

### Polylith-style modular architecture

- [`hugoduncan--mcp-clj`] bases/components/projects — advanced modular organization. Vector search integration (`.mcp-vector-search/`)

### Minimal dependencies

- [`hugoduncan--mcp-clj`] only `org.clojure/data.json` for full MCP implementation
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] FastMCP only
- Self-contained Clojure REPL evaluation without external deps

### Single-file server script

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] keeps surface tiny

### Two-tool minimal interface

- [`hugoduncan--mcp-clj`] — `clj-eval` + `ls` only, contrasted with 50+ tools in clojure-mcp

### Declarative tool authoring

- [`googleapis--mcp-toolbox`] YAML manifest as primary configuration surface — admins define tools without writing code, distinct from code-defined MCP servers

### Multi-database via sources abstraction

- [`googleapis--mcp-toolbox`] same binary speaks to 8+ databases via `sources` abstraction; tool authoring is declarative on top of that

### HTTP-first transport diverging from stdio convention

- [`googleapis--mcp-toolbox`] HTTP at `:5000/mcp` — explicit divergence from stdio-first convention

### Gemini-first integration shape

- [`googleapis--mcp-toolbox`] in-repo `gemini-extension.json` and `.gemini/` directory reflect project's origin at Google; other hosts consume the generic HTTP endpoint

### Output ergonomics

- `strip_thinking` optional param — [`ppl-ai--modelcontextprotocol`] removes reasoning tags from output [`ppl-ai--modelcontextprotocol`]

### Proxy configuration hierarchy

- [`ppl-ai--modelcontextprotocol`] — `PERPLEXITY_PROXY` takes priority over `HTTPS_PROXY`/`HTTP_PROXY`. Recognizes corporate/enterprise environments where a service-specific proxy must override system-wide settings [`ppl-ai--modelcontextprotocol`]

### Lock-file-driven Docker reproducibility

- [`reminia--zendesk-mcp-server`] Dockerfile installs from `requirements.lock` — lock-file-as-build-contract, not pyproject-only [`reminia--zendesk-mcp-server`]

### Read existing data, don't crawl live

- [`pragmar--mcp-server-webcrawl`] — operates on pre-captured crawler archives, sidesteps rate-limit/politeness/JS-rendering concerns. Reference for "don't crawl inside MCP, index what the user crawled" [`pragmar--mcp-server-webcrawl`]

### Prompt-routine packaging

- [`pragmar--mcp-server-webcrawl`] ships Markdown prompts as a distribution surface alongside tools — encoding "how to use the server for SEO audits" as reusable content rather than forcing users to rediscover prompting patterns [`pragmar--mcp-server-webcrawl`]

### Single-binary environment branching

- [`paypal--paypal-mcp-server`] `PAYPAL_ENVIRONMENT` env var routes between sandbox/production rather than separate entry points [`paypal--paypal-mcp-server`]

### `server.json` for MCP server registry

- [`redis--mcp-redis`] ships `server.json` for MCP registry wiring [`redis--mcp-redis`]
- [`github--github-mcp-server`], [`googleapis--mcp-toolbox`] also ship `server.json`

### Granular SSL knobs

- [`redis--mcp-redis`] exposes `--ssl-ca-path`, `--ssl-keyfile`, `--ssl-certfile` alongside URI schemes (`redis://`, `rediss://`) [`redis--mcp-redis`]

## Example client / developer ergonomics

### MCP Inspector usage

- [`getsentry--sentry-mcp`] called out in README with `pnpm -w run cli` for manual CLI testing
- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] does not; FastMCP CLI install is the primary dev ergonomic
- [`qdrant--mcp-server-qdrant`] documents `fastmcp dev` for Inspector

### Sample host configs in-repo

- [`geropl--linear-mcp-go`] `setup --tool` automates JSON config editing
- [`github--github-mcp-server`] ships `.vscode/`
- [`googleapis--mcp-toolbox`] `gemini-extension.json` + `server.json`
- [`hugoduncan--mcp-clj`] sample `claude_desktop_config.json` in README
- [`idosal--git-mcp`] dev scripts + Playwright E2E + README examples

### Pre-commit / lint

- [`isaaccorley--planetary-computer-mcp`] `uv run pre-commit run --all-files`
- [`googleapis--mcp-toolbox`] `.golangci.yaml`
- [`github--github-mcp-server`] `.golangci.yml`
- [`idosal--git-mcp`] Biome unified linting/formatting
- [`hugoduncan--mcp-clj`] clj-kondo + `.cljstyle`
- [`qdrant--mcp-server-qdrant`] pre-commit
- [`redis--mcp-redis`] mypy + black + bandit + safety + twine (security scanning as first-class; PyPI publishing pipeline)

### Embedded LLM-context docs

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] uses `fastmcp-documentation.txt` + `mcp-documentation.txt` in repo — embedded LLM-context docs

### Eval harness

- [`getsentry--sentry-mcp`] `pnpm eval` for regression testing against model outputs

### Memory-bank convention

- [`geropl--linear-mcp-go`] `memory-bank/` directory suggests author uses Cline's memory-bank convention — evidence of dogfooding

### Documentation build

- [`pragmar--mcp-server-webcrawl`] `sphinx/` for documentation build

### Custom debug surface

- [`pragmar--mcp-server-webcrawl`] `--interactive` REPL custom debug surface

## Python-specific

### SDK / framework variant

| Variant | Samples |
|---------|---------|
| FastMCP 1.x (pre-2.x) — `fastmcp==0.4.1` pinned | [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] |
| FastMCP 2.x exact-pinned `fastmcp==2.7.0` | [`qdrant--mcp-server-qdrant`] |
| FastMCP (major version unsurfaced) | [`rohitg00--kubectl-mcp-server`] |
| Raw `mcp` SDK (Anthropic Python implementation) | [`isaaccorley--planetary-computer-mcp`], [`pragmar--mcp-server-webcrawl`] (`mcp>=1.3.0`), [`reminia--zendesk-mcp-server`] (`mcp>=1.1.2`) |
| `mcp[cli]` | [`redis--mcp-redis`] (`mcp[cli]>=1.26.0`) |

### Build backend

- **hatchling** — [`qdrant--mcp-server-qdrant`], [`reminia--zendesk-mcp-server`]
- **setuptools (`setuptools.build_meta`)** — [`pragmar--mcp-server-webcrawl`] (contrarian vs hatchling-dominated sample)
- **setuptools (`setup.py`)** — [`rohitg00--kubectl-mcp-server`] (older convention vs modern pyproject-only)
- **`uv_build`** — [`redis--mcp-redis`] (`requires = ["uv_build>=0.8.3,<0.12.0"]`) — one of the very few using uv's native build backend

### Lock files

- `uv.lock` — [`redis--mcp-redis`]
- `requirements.lock` — [`reminia--zendesk-mcp-server`] (used by Dockerfile)
- `.python-version` tracked (implies uv) — [`qdrant--mcp-server-qdrant`]
- `uv.lock` likely (uv sync convention) — [`isaaccorley--planetary-computer-mcp`]
- Not observed — [`pragmar--mcp-server-webcrawl`]

### Version-manager convention

- `uv` ecosystem — [`qdrant--mcp-server-qdrant`], [`redis--mcp-redis`], [`reminia--zendesk-mcp-server`], [`isaaccorley--planetary-computer-mcp`] (`.python-version`)
- plain pip — [`pragmar--mcp-server-webcrawl`]
- pip/uv compatible — [`rohitg00--kubectl-mcp-server`]
- pre-`pyproject.toml` (pip/venv with `requirements.txt`) — [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: NO pyproject.toml — only `requirements.txt` + single `sqlite_explorer.py`. No build backend, no lock file

### Entry point

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: no `[project.scripts]`; run via `fastmcp install sqlite_explorer.py` or `fastmcp run`. Cline config: `"command": "uv"`, `"args": ["run", "--with", "fastmcp", "--with", "uvicorn", "fastmcp", "run", "/path/to/sqlite_explorer.py"]`
- [`isaaccorley--planetary-computer-mcp`]: `__main__.py` (module invoked with `python -m`), no console-script names surfaced
- `mcp-server-webcrawl = "mcp_server_webcrawl:main"` — [`pragmar--mcp-server-webcrawl`]
- `mcp-server-qdrant` console script → `mcp_server_qdrant.main:main` — [`qdrant--mcp-server-qdrant`]
- `redis-mcp-server = "src.main:cli"` — [`redis--mcp-redis`]; unusual `src.` prefix
- `zendesk` console script → `zendesk_mcp_server:main` — [`reminia--zendesk-mcp-server`]; unusually short script name
- `kubectl-mcp-server` console script — [`rohitg00--kubectl-mcp-server`]

### Install workflow expected of end users

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: `fastmcp install sqlite_explorer.py --name "..." -e SQLITE_DB_PATH=...` — uses FastMCP CLI installer; no pip-install path
- [`isaaccorley--planetary-computer-mcp`]: source clone + `uv sync`

### Async vs sync

- async (FastMCP default + pytest-asyncio auto) — [`qdrant--mcp-server-qdrant`]
- async (pytest-asyncio auto, low-level mcp[cli]) — [`redis--mcp-redis`]
- async likely (low-level mcp SDK) — [`pragmar--mcp-server-webcrawl`]
- sync likely (zenpy is sync) — [`reminia--zendesk-mcp-server`]
- not surfaced — [`rohitg00--kubectl-mcp-server`] (FastMCP default applies)
- FastMCP-decorated functions (sync and async supported in 0.4.1) — [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- async likely (STAC clients tend to be async) — [`isaaccorley--planetary-computer-mcp`]

### Type / schema strategy

- FastMCP auto-derived from type hints — [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Pydantic via MCP SDK; schema auto-derived — [`isaaccorley--planetary-computer-mcp`]
- Pydantic 2 direct dep + FastMCP auto-derives — [`qdrant--mcp-server-qdrant`]. Pydantic pinned `>=2.10.6,<2.12.0` (tight window to track FastMCP compatibility)
- FastMCP default (Pydantic-based) inferred — [`rohitg00--kubectl-mcp-server`]
- Hand-authored schemas — [`pragmar--mcp-server-webcrawl`], [`redis--mcp-redis`] (low-level MCP SDK)
- Raw dicts likely — [`reminia--zendesk-mcp-server`] (raw mcp SDK handlers typically take dicts)

### Dev tooling

- pre-commit — [`qdrant--mcp-server-qdrant`]
- mypy + black + bandit + safety + twine — [`redis--mcp-redis`] (security scanning as first-class; PyPI publishing pipeline)
- `fastmcp dev` for Inspector — [`qdrant--mcp-server-qdrant`] documented
- `sphinx/` for documentation build — [`pragmar--mcp-server-webcrawl`]
- `--interactive` REPL custom debug surface — [`pragmar--mcp-server-webcrawl`]

### Modern Python project layout

- PEP 735 `[dependency-groups]` with distinct `dev` and `test` groups — [`redis--mcp-redis`]
- Coverage fail-threshold (`--cov-fail-under=80`) in `addopts` — [`redis--mcp-redis`]

### Minimal-deps posture

- 3-deps runtime stack — [`reminia--zendesk-mcp-server`] (`mcp`, `python-dotenv`, `zenpy`)
- No dev/test extras in pyproject — [`pragmar--mcp-server-webcrawl`] (minimal packaging posture)

### Notable Python-specific choices

- [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]: `fastmcp install` registers server with Claude Desktop directly — distinct from `uvx` or manual config editing. Pre-`pyproject.toml`-era reference case for "how the FastMCP ecosystem looked before the 2.0 split"
- [`isaaccorley--planetary-computer-mcp`]: `python -m module.server` launch pattern — module-level invocation rather than console script. Raw MCP SDK in 2026 — many newer servers have migrated to FastMCP; this one stays on the lower-level SDK

## Unanticipated axes observed

- **Tool-catalog mutability** — [`github--github-mcp-server`]'s `--dynamic-toolsets` exposes runtime-discoverable tools rather than fixed catalog at startup; affects how hosts cache tool listings
- **Per-feature behavior modes** — [`github--github-mcp-server`] `--read-only`, `--lockdown-mode`, `--insiders` act as behavior envelopes rather than capability toggles, separating policy from toolset selection
- **Hosted + local hybrid as distribution strategy** — [`github--github-mcp-server`], [`getsentry--sentry-mcp`]
- **Cloud-hosted SaaS endpoint** — [`idosal--git-mcp`] axis: hosted vs local installation; parameterized repository endpoints (one deployment serves every GitHub repo)
- **Server-internal LLM invocation** — [`getsentry--sentry-mcp`] shifts "agent" responsibility inside the MCP boundary; unusual
- **Skills as bundled capability layer** — [`getsentry--sentry-mcp`] higher-level behavioral primitive distinct from tools
- **In-repo Claude plugin wrapper** — [`getsentry--sentry-mcp`] rare; most servers leave host integration to external config
- **Evaluation discipline alongside unit tests** — [`getsentry--sentry-mcp`] `pnpm eval` as peer of `pnpm test`
- **Declarative tool authoring via YAML manifest** — [`googleapis--mcp-toolbox`] different authoring surface from code-defined servers
- **Prompts as first-class manifest concept** — [`googleapis--mcp-toolbox`] alongside tools
- **Hot reloading as built-in** — [`googleapis--mcp-toolbox`] state survives across configuration changes
- **NPM shim wrapping a Go binary** — [`googleapis--mcp-toolbox`] `@toolbox-sdk/server` as cross-ecosystem glue
- **NPM shim wrapping a Python package** — [`rohitg00--kubectl-mcp-server`] dual-ecosystem distribution
- **Co-located VS Code extension with MCP server** — [`isaaccorley--planetary-computer-mcp`] mixed-language repo for editor integration outside MCP
- **LLM-targeted visualization generation** — [`isaaccorley--planetary-computer-mcp`] not just data retrieval; deliberate design choice
- **Vector search integration** — [`hugoduncan--mcp-clj`] `.mcp-vector-search/` suggests semantic/similarity search capabilities
- **Polylith architecture** — [`hugoduncan--mcp-clj`] bases/components/projects modular organization
- **In-memory transport for testing** — [`hugoduncan--mcp-clj`] unusual
- **Two-tool minimal interface vs. 50+ tools** — [`hugoduncan--mcp-clj`] outlier among Clojure MCP options
- **Setup subcommand as scoped extension point** — [`geropl--linear-mcp-go`] `--tool=cline` flag signals plan to automate other host configurations
- **go-vcr cassette testing for offline integration** — [`geropl--linear-mcp-go`] full integration tests run without live credentials
- **Memory-bank dogfooding** — [`geropl--linear-mcp-go`] `memory-bank/` evidence author uses Cline's convention themselves
- **Stdio cleanliness pressure** — [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`] explicit "progress output suppression" as design concern
- **GHCR as primary distribution channel** — [`github--github-mcp-server`] `docker run` is canonical install path, not `go install`
- **First-party-but-low-stars pattern** — vendor releases at single-digit / low-double-digit star counts ([`paypal--paypal-mcp-server`] at 9, [`riza-io--riza-mcp`] at 14) suggest a recurring "official but unpromoted" axis worth examining across the corpus
- **Capability-scoping flag/extras patterns** — `--tools=all` (paypal), `MCP_BROWSER_ENABLED` (kubectl), `[ui]` extra (kubectl), `--disable-destructive` (kubectl), `--write-access` (linear-mcp-go), `--read-only` (github-mcp-server). Multiple distinct mechanisms for "user controls which slice of the surface is loaded"
- **Lock-file as build contract** — both [`reminia--zendesk-mcp-server`] (Dockerfile installs from `requirements.lock`) and [`redis--mcp-redis`] (`uv.lock` in repo) treat lock files as authoritative
- **Editable-install-only distribution** — [`reminia--zendesk-mcp-server`] "developer-mode-as-release" is a distinct distribution mechanism
- **Prompt-routines vs MCP prompts protocol** — [`pragmar--mcp-server-webcrawl`] ships Markdown prompts as a separate surface, while [`rohitg00--kubectl-mcp-server`] exposes 8 prompts via the MCP protocol primitive. Same goal, different mechanism
- **MCP resources used vs ignored** — [`reminia--zendesk-mcp-server`] uses resources for KB read access; [`rohitg00--kubectl-mcp-server`] exposes 8 resources; most samples only use tools. The "split read/write across resources/tools" pattern is a divergence axis
- **Cloud-native auth (Azure EntraID) vs static credentials** — [`redis--mcp-redis`] is the only sample with cloud-native identity; flagging because enterprise deployment pressure may be a recurring driver
- **Domain decoupling via env vars** — [`qdrant--mcp-server-qdrant`] embedding model/provider, local-vs-remote backend; [`paypal--paypal-mcp-server`] sandbox/production environment

## Gaps observed across bin

- License content frequently not surfaced (LICENSE file not fetched in [`getsentry--sentry-mcp`], [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`])
- Logging destination/format rarely documented; most samples assume stderr by language convention
- Specific Go / Java / Node version constraints often unspecified
- CI workflow contents typically not enumerated within budget
- Whether `server.json` is consumed by MCP clients beyond identifying capability vs purely metadata — unclear ([`github--github-mcp-server`], [`googleapis--mcp-toolbox`], [`redis--mcp-redis`])
- Custom tool registration API patterns documented as "via API" but not detailed ([`hugoduncan--mcp-clj`])

## Open questions / categorization decisions

- **"Prompt routines" categorization** — placed [`pragmar--mcp-server-webcrawl`] Markdown prompt routines under "MCP primitives beyond tools" but it is explicitly NOT using the MCP prompts protocol. Alternative home: a separate "Distribution surface" or "Knowledge artifacts shipped alongside server" section. Flagged for downstream merger
- **Editable-install-only categorization** — placed [`reminia--zendesk-mcp-server`] under Distribution as its own entry but it could equally live under "Notable structural choices" as a posture statement
- **Cluster-mode under multi-tenancy** — [`redis--mcp-redis`] `--cluster-mode` is a connection topology, not per-request tenancy. Currently cited under multi-tenancy single-tenant section; downstream merger may prefer a distinct "Connection topology" subsection
- **`server.json` placement** — [`redis--mcp-redis`], [`github--github-mcp-server`], [`googleapis--mcp-toolbox`] ship `server.json`; placed under Notable Structural Choices but could live under Distribution if the registry is a distribution channel
- **Polyglot wrapper category** — [`rohitg00--kubectl-mcp-server`] has Python core + npm wrapper. Listed under Language and Runtime as "Polyglot wrapper", and again under Distribution as "Dual-ecosystem publishing"/"Cross-ecosystem glue". The two facets (implementation polyglot vs distribution polyglot) are linked but distinct — downstream merger should decide if one home is sufficient
