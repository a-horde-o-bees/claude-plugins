# Sample

Pass-1 Phase-1a partial for bin 5. Atomic knowledge chunks from `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server`, organized by divergence axes. Phase-1b merger will unify with other partials.

## Language and runtime

Implementation language is the first-order divergence; everything else (SDK choice, packaging, distribution) follows.

### Python

Python is the dominant language across the bin. Within Python, version floors split:

- Python 3.10+ floor — `duolingo--slack-mcp` (`requires-python = ">=3.10"`, Dockerfile uses `python:3.11-slim` base)
- Python 3.11+ floor — `designcomputer--mysql_mcp_server`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server` (all declare `requires-python = ">=3.11"`)

The 3.11 floor is observed as "a touch more modern than awslabs' 3.10" [`echelon-ai-labs--servicenow-mcp`]. No Python <3.10 observed in bin.

### TypeScript / Node.js

- Node.js >=18.0.0 — `exa-labs--exa-mcp-server` (TypeScript 97.9%)
- Node.js 22+ — `docker--hub-mcp` (TypeScript 99.8%)
- Node.js (npx/npm-based) — `executeautomation--mcp-playwright` (TypeScript 93.6%); specific Node version not pinned in README

### Rust

- Rust 2024 edition — `elastic--mcp-server-elasticsearch` (Rust 94.3%); exact Rust version not specified in `Cargo.toml`, only edition. A rare axis value across the corpus.

## SDK / framework variant

Framework choice diverges within each language family.

### Python SDKs

- Raw `mcp` Python SDK (low-level, hand-authored schemas) — `designcomputer--mysql_mcp_server` (`mcp>=1.0.0`), `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`
- FastMCP 2.x — `duolingo--slack-mcp` (`fastmcp>=2.13.0`); auto-derives schemas

For SSE transport in raw-SDK servers, Starlette is used directly rather than FastAPI [`echelon-ai-labs--servicenow-mcp`] — observed as a viable sub-FastAPI layer for MCP servers wanting HTTP transport without full REST framework overhead.

### TypeScript SDKs

- `@modelcontextprotocol/sdk` (typical for TS MCP) — `docker--hub-mcp` (likely; not explicitly extracted), `executeautomation--mcp-playwright`
- MCP SDK ^1.12.1 with Zod validation and `jose` (JWT) — `exa-labs--exa-mcp-server`; also pulls in `exa-js ^2.8.0` for the underlying API

### Rust SDKs

- `rmcp ^0.2.1` (Rust MCP SDK), `tokio` (async), `axum` (HTTP) — `elastic--mcp-server-elasticsearch`

## Transport

Transport surface is a key divergence axis. Two orthogonal questions: which transports supported, and how the choice is exposed.

### Supported transports

- stdio only — `designcomputer--mysql_mcp_server` (README explicitly frames as "stdio-based protocol server rather than standalone application")
- HTTP only — `duolingo--slack-mcp` (`http://localhost:8001/mcp`, port 8001)
- HTTP + stdio — `docker--hub-mcp` (CLI `--transport=http|stdio`)
- HTTP (remote endpoint) + stdio + HTTP local — `exa-labs--exa-mcp-server` (default remote `https://mcp.exa.ai/mcp`)
- stdio + SSE — `echelon-ai-labs--servicenow-mcp` (separate console scripts per transport)
- stdio + streamable-HTTP (SSE deprecated) — `elastic--mcp-server-elasticsearch`
- stdio + SSE + streamable-http — `feiskyer--mcp-kubernetes-server` (CLI `--transport`)
- stdio (recommended) + HTTP/SSE — `executeautomation--mcp-playwright` (single binary; `--port` switches mode)

### Transport selection mechanism

How the user picks a transport diverges sharply:

- Implicit / single-transport — `designcomputer--mysql_mcp_server` (stdio only), `duolingo--slack-mcp` (HTTP only)
- CLI flag (`--transport`) — `docker--hub-mcp`, `feiskyer--mcp-kubernetes-server`
- CLI flag (`--port` switches stdio→HTTP) — `executeautomation--mcp-playwright` ("Dual-transport from one binary — `--port` switches between stdio and HTTP, not separate entry points" [`executeautomation--mcp-playwright`])
- Docker arg / CLI positional (`stdio` vs `http`) — `elastic--mcp-server-elasticsearch`
- Separate console scripts per transport — `echelon-ai-labs--servicenow-mcp`: `python -m servicenow_mcp.cli` (stdio) vs `servicenow-mcp-sse` (SSE). "Architecturally split rather than env-var-switched" — opposite of the one-binary multi-transport model
- Client config selects (default remote endpoint) — `exa-labs--exa-mcp-server`

> The transport-selection split (one binary with flag vs separate binaries per transport) is itself a design axis worth tracking.

## Distribution

How the server reaches end users. Multiple mechanisms commonly stack.

### Package managers

- PyPI — `designcomputer--mysql_mcp_server` (`mysql-mcp-server`), `feiskyer--mcp-kubernetes-server` (`mcp-kubernetes-server`)
- npm — `docker--hub-mcp` (npm-installable), `exa-labs--exa-mcp-server` (`exa-mcp-server`), `executeautomation--mcp-playwright` (`@executeautomation/playwright-mcp-server`)
- Source-only / no package registry — `duolingo--slack-mcp` ("Not published to PyPI; source-only distribution"), `echelon-ai-labs--servicenow-mcp` (`pip install -e .` from clone)

### Container registries

- Generic Dockerfile in repo — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `executeautomation--mcp-playwright`
- ghcr.io image published — `feiskyer--mcp-kubernetes-server`
- Vendor-specific registry — `elastic--mcp-server-elasticsearch` (`docker.elastic.co/mcp/elasticsearch`, distributed via AWS Marketplace and Elastic's container registry)

### Container-only distribution

- `elastic--mcp-server-elasticsearch` — Docker is the only shipping channel ("Container-first distribution — Docker is the only shipping channel")
- `duolingo--slack-mcp` — Docker primary (no PyPI); "Containerization as primary distribution (not Homebrew, npm, Cargo)". "Inverts the typical Python packaging path; container as the only artifact"

### Aggregator / installer registries

- Smithery CLI install — `designcomputer--mysql_mcp_server` (`npx -y @smithery/cli install mysql-mcp-server --client claude`), `executeautomation--mcp-playwright`, `exa-labs--exa-mcp-server` (Smithery registry config `smithery.yaml`)
- mcp-get — `executeautomation--mcp-playwright`
- Pre-built IDE installers (one-click for Cursor / VS Code) — `exa-labs--exa-mcp-server`
- Native Claude Desktop connector (no manual config) — `exa-labs--exa-mcp-server`

> `executeautomation--mcp-playwright` ships across four mechanisms (npm, mcp-get, Smithery, Docker) — flagged in-sample as "a reference for 'how many channels to publish to' decisions".

### Remote-hosted endpoint

- `exa-labs--exa-mcp-server` — operates a remote MCP endpoint at `https://mcp.exa.ai/mcp`; clients connect to that URL rather than running a local process. Reduces setup friction. Vercel deployment config (`vercel.json`) supports the hosted variant.

## Entry point / launch

How the running process is started, after distribution lands the bits.

### Console script vs `python -m` vs `npx`

- Console script via `[project.scripts]` — `designcomputer--mysql_mcp_server` (`mysql_mcp_server = "mysql_mcp_server:main"`), `duolingo--slack-mcp` (`slack-mcp = "main:main"` — module `main` at top level, no package, unusual)
- `python -m <module>` — `feiskyer--mcp-kubernetes-server` (`python -m src.mcp_kubernetes_server.main`)
- `python -m <module>` AND console script — `echelon-ai-labs--servicenow-mcp`: `python -m servicenow_mcp.cli` (stdio) plus `servicenow-mcp-sse` (SSE)
- `uvx <package>` — `feiskyer--mcp-kubernetes-server`, `designcomputer--mysql_mcp_server` (VS Code config example uses `uvx --from mysql-mcp-server`)
- `npx -y <package>` — `executeautomation--mcp-playwright`
- `npm start -- ...` or direct `dist/index.js` — `docker--hub-mcp`
- `docker run` (entrypoint implicit) — `elastic--mcp-server-elasticsearch`
- Bare `python main.py` (no package, no console script) — `duolingo--slack-mcp` Dockerfile uses `uv run python main.py` rather than the declared console script. "Entry point not the primary run path"

### Discouraged direct invocation

`designcomputer--mysql_mcp_server` README "explicitly discourages `python ...` direct invocation, framing the server strictly as an MCP-protocol bridge for hosts." Unique enforcement of agent-posture mental model in this bin.

## Configuration surface

How config reaches the server.

### Environment variables

- All-env-var config — `designcomputer--mysql_mcp_server` (`MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`), `duolingo--slack-mcp` (`SLACK_CLIENT_ID`, `SLACK_CLIENT_SECRET`, `SLACK_MCP_BASE_URI`, `SLACK_EXTERNAL_URL`, `SLACK_MCP_PORT`), `elastic--mcp-server-elasticsearch` (`ES_URL`, `ES_API_KEY` or `ES_USERNAME`/`ES_PASSWORD`, `ES_SSL_SKIP_VERIFY`)
- Env var (single) — `feiskyer--mcp-kubernetes-server` (`KUBECONFIG`), `exa-labs--exa-mcp-server` (`EXA_API_KEY`)

### CLI args

- CLI args (transport-specific) — `echelon-ai-labs--servicenow-mcp` SSE mode accepts `--instance-url=`, `--username=`, `--password=`; stdio mode uses env vars
- CLI args + env vars (mixed) — `docker--hub-mcp` (`HUB_PAT_TOKEN` env, `--transport`/`--port`/`--username` CLI)
- Capability gating CLI flags — `feiskyer--mcp-kubernetes-server`: `--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`. Per-verb enable/disable as an argument surface pattern (kubectl vs helm vs write vs delete split into four independent flags)

### Config files

- Tool catalog as data file — `docker--hub-mcp` (`tools.json`/`tools.txt` ship tool definitions; "Declarative catalog rather than inline schemas in source. Opens an authoring path that doesn't require TS expertise.")
- `mcp-config.json` for settings — `executeautomation--mcp-playwright`
- URL parameter as config (alternative to env var) — `exa-labs--exa-mcp-server` (`EXA_API_KEY` either env var or URL parameter)

## Authentication

Auth mechanism, where credentials originate, and whether the server itself implements an auth flow.

### Static credentials in env

- DB username/password — `designcomputer--mysql_mcp_server`. README emphasizes "never commit" credentials and restricting to minimum-permission DB users. Security guidance baked into README
- API key — `exa-labs--exa-mcp-server` (`EXA_API_KEY` from dashboard.exa.ai), `elastic--mcp-server-elasticsearch` (`ES_API_KEY`) or username/password against the cluster
- Personal Access Token — `docker--hub-mcp` (Docker Hub PAT in `HUB_PAT_TOKEN`)

### Credential delegation to local context

- kubeconfig — `feiskyer--mcp-kubernetes-server` delegates entirely to kubeconfig credentials; permissions check via kubectl's auth subsystem (`k8s_auth_can_i`, `k8s_auth_whoami`)

### Multi-mechanism with env-var selector

- `echelon-ai-labs--servicenow-mcp` — three methods (Basic Auth, OAuth client credentials, API Key); `SERVICENOW_AUTH_TYPE` env var selects mechanism. "Multi-auth support as a first-class feature — enterprise SaaS servers often need it because different customer deployments mandate different auth; most community servers pick one"

### OAuth flow implemented in server

- `duolingo--slack-mcp` — OAuth 2.1 per-user; "when your MCP client first connects. Your client will open a browser window for Slack authorization". Server itself drives a browser-based OAuth handshake. Local dev requires ngrok for OAuth callback

### No auth (browser-context delegated)

- `executeautomation--mcp-playwright` — "Not applicable — browser automation against public web; no service-level auth. Sites that require auth rely on Playwright's own cookie/state mechanisms, not an MCP-layer auth flow." User-driven within browser session

## Multi-tenancy

How many tenants share a process.

### Single-tenant per process

- Single DB connection per server, no per-request tenancy — `designcomputer--mysql_mcp_server`
- Single ServiceNow instance per deployment — `echelon-ai-labs--servicenow-mcp`
- Single Elasticsearch cluster — `elastic--mcp-server-elasticsearch` (per-client MCP connection in HTTP mode but single ES backend)
- Single user per process (one PAT plus username) — `docker--hub-mcp`
- Single kubeconfig context — `feiskyer--mcp-kubernetes-server`
- Single browser context per server process — `executeautomation--mcp-playwright`

### Per-request multi-tenancy

- OAuth 2.1 per-user, multi-user via separate tokens per user — `duolingo--slack-mcp`. Per-request tenant is a rare value across the bin
- Per-client multi-tenancy via HTTP endpoint, API key scoped to user account — `exa-labs--exa-mcp-server`

## Capabilities exposed

Tools / resources / prompts surface area; tool count is one observable axis of breadth.

### Tools-only

- 5 read-only Slack tools — `duolingo--slack-mcp` (channel messages, thread replies, search messages, list users, enumerate channels). "Read-only Slack integration (no write capabilities)" — Read-only MCP server pattern as an axis value
- 5 ES tools — `elastic--mcp-server-elasticsearch` (`list_indices`, `get_mappings`, `search`, `esql`, `get_shards`)
- 3 web-search tools + advanced filtering — `exa-labs--exa-mcp-server` (`web_search_exa`, `web_fetch_exa`, `web_search_advanced_exa`)
- Tools defined in `tools.json` — `docker--hub-mcp` (specific tool list not enumerated)
- Browser automation surface — `executeautomation--mcp-playwright` (navigation, click, fill, screenshot, test code generation, web scraping, JavaScript execution, device emulation with 143+ device presets). Not enumerated as discrete tools but a rich functional surface
- 50+ tools — `feiskyer--mcp-kubernetes-server` (kubectl/helm command execution, read-only queries, write, delete, rollout/scaling)
- 60+ tools across 9 functional areas — `echelon-ai-labs--servicenow-mcp` (Incident, Service catalog, Change requests, Agile, Workflows, Script includes, Changesets, Knowledge bases, User management). "Enterprise-tool density — 60+ tools in 9 functional areas; enterprise platforms generate more surface area than consumer SaaS does"

### Tools + resources

- Tables-as-resources — `designcomputer--mysql_mcp_server`. "MySQL tables listed as resources, table contents readable. Tools — SQL query execution with error handling. Exposes tables as MCP resources (not only tools) — one of the few DB MCP servers to use the resource surface" / "Resources-as-tables pattern is rare — most DB MCP servers expose everything through tools"

### Vertical / specialized skills shipped alongside

- `exa-labs--exa-mcp-server` skills directory — company research, code search, people research, financial reports, academic papers. "Vertical-specific research skills shipped alongside the server — axis: 'skills' as first-class shipping artifact"

## Observability

Logging, metrics, tracing, debug surface.

### File-based logging (stdio framing constraint)

- `executeautomation--mcp-playwright` — logs written to `~/playwright-mcp-server.log` in stdio mode "specifically to keep stdout clean for JSON-RPC framing. File-based log is the observability surface". A deliberate design response to the stdio framing constraint — the server cannot log to stdout without corrupting JSON-RPC

### Container stdout/stderr + health endpoint

- `elastic--mcp-server-elasticsearch` — container logs (stdout/stderr); health check at `/ping` returning "pong"

### Underspecified

- `designcomputer--mysql_mcp_server` ("comprehensive logging" mentioned, no specifics)
- `duolingo--slack-mcp` ("no explicit monitoring, logging, or metrics documentation")
- `docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `exa-labs--exa-mcp-server` — not surfaced

## Host integrations

Which MCP host configs the README documents.

### Claude Desktop

`claude_desktop_config.json` example — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `executeautomation--mcp-playwright` (primary host integration). `duolingo--slack-mcp` implies standard MCP configuration without explicit detail. `feiskyer--mcp-kubernetes-server` JSON `mcpServers` entry. `exa-labs--exa-mcp-server` ships a native Claude Desktop connector (no manual config needed) — distinct from JSON-snippet hosts. `elastic--mcp-server-elasticsearch` listed as MCP-compatible (assumed).

### VS Code

`mcp.json` example — `designcomputer--mysql_mcp_server`, `docker--hub-mcp` (User Settings JSON), `exa-labs--exa-mcp-server` (pre-built installer). `executeautomation--mcp-playwright` documented via GitHub Copilot integration.

### Cursor

`feiskyer--mcp-kubernetes-server` JSON `mcpServers` entry. `exa-labs--exa-mcp-server` pre-built installer. `executeautomation--mcp-playwright` documented host integration. `elastic--mcp-server-elasticsearch` listed (assumed).

### Vendor-specific companion integration

- `docker--hub-mcp` ships `gordon-mcp.yml` for Docker's Ask Gordon agent. "MCP server pre-shaping its config for a first-party downstream tool, distinct from generic host config"

### Many-host enumeration

`exa-labs--exa-mcp-server` documents JSON `mcp.json` configs for Codex, OpenCode, Antigravity, Windsurf, Zed, Gemini CLI, v0 by Vercel, Warp, Kiro, Roo Code — 15+ platforms. "High client compatibility (15+ platforms)"

### GitHub Copilot / ChatGPT Copilot

- `feiskyer--mcp-kubernetes-server` documents JSON `mcpServers` entry for both

### Cline

- `executeautomation--mcp-playwright` documented host integration

## Claude Code plugin wrapper

Whether the repo ships `.claude-plugin/`.

- Present — `exa-labs--exa-mcp-server`: `.claude-plugin/plugin.json` with HTTP server config (type: http, url: `https://mcp.exa.ai/mcp?client=claude-code-plugin`, custom header `x-exa-source: claude-code-plugin`)
- Not present — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server`

## Tests

### Framework

- pytest — `designcomputer--mysql_mcp_server` (`pytest.ini`, `requirements-dev.txt`, `tests/` directory), `duolingo--slack-mcp` (`pytest>=8.0.0` in test extras, `uv run pytest`)
- Jest — `executeautomation--mcp-playwright` (`src/__tests__`)
- Framework not surfaced — `echelon-ai-labs--servicenow-mcp` (`tests/` directory present), `elastic--mcp-server-elasticsearch` (`tests/` directory), `feiskyer--mcp-kubernetes-server` (CI `build.yml` suggests CI-driven tests), `docker--hub-mcp` (ESLint config present, no test files explicitly called out), `exa-labs--exa-mcp-server` (not documented)

### Async test support

- pytest-asyncio not declared — `duolingo--slack-mcp` ("may be sync-style tools")
- pytest-asyncio not confirmed — `designcomputer--mysql_mcp_server`

## CI

### GitHub Actions

- Present — `designcomputer--mysql_mcp_server` (test.yml badge), `docker--hub-mcp` (`.github/`), `feiskyer--mcp-kubernetes-server` (`build.yml`), `executeautomation--mcp-playwright` (`.github/workflows`)

### Multi-system CI

- `elastic--mcp-server-elasticsearch` — both `.github/` (GitHub Actions) and `.buildkite/` (Buildkite pipeline) — multi-platform testing across two CI systems. "CI system diversity beyond the GitHub-only assumption"

### Unspecified / not extracted

- `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `exa-labs--exa-mcp-server`

## Container / packaging artifacts

### Dockerfile only

- `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`, `exa-labs--exa-mcp-server` (Dockerfile + Vercel `vercel.json`)

### Dockerfile + docker-compose

- `executeautomation--mcp-playwright`

### Multiple Dockerfiles / multi-target

- `elastic--mcp-server-elasticsearch` — `Dockerfile` (main), `Dockerfile-8000` (alternative), `.dockerignore`. Multi-container deployment ready (EC2, ECS, EKS deployment targets)

### Container as primary distribution

- `duolingo--slack-mcp` — Dockerfile uses `python:3.11-slim` base, env vars `NO_COLOR=1`, `CI=true`, `TERM=dumb`, port 8001 exposed, startup `uv run python main.py`

## Repo layout

### Single-package

- All eight samples are single-package — `designcomputer--mysql_mcp_server` (`src/mysql_mcp_server/`), `docker--hub-mcp` (`src/`), `duolingo--slack-mcp` (root `main.py` only), `echelon-ai-labs--servicenow-mcp` (`servicenow_mcp/`), `elastic--mcp-server-elasticsearch` (Rust `src/`), `exa-labs--exa-mcp-server` (`src/`, `api/`, `skills/`, `public/`), `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server` (`src/mcp_kubernetes_server/`)

### `src/`-layout vs flat

- `src/`-layout — `designcomputer--mysql_mcp_server`, `feiskyer--mcp-kubernetes-server`
- Flat package — `echelon-ai-labs--servicenow-mcp` (top-level `servicenow_mcp/`)
- No package, top-level `main.py` only — `duolingo--slack-mcp`. "Module entry `main:main` (top-level, no package) — unusual; most servers use a nested package module path"

## Python-specific

### Build backend

- `hatchling.build` — `designcomputer--mysql_mcp_server`
- `setuptools.build_meta` — `duolingo--slack-mcp`. "Setuptools backend (minority in the Python sample; hatchling dominant)"
- pyproject.toml with uv (build backend not surfaced) — `feiskyer--mcp-kubernetes-server`
- Not captured — `echelon-ai-labs--servicenow-mcp`

### Lock file / version manager

- `uv.lock` present, uv convention — `duolingo--slack-mcp`, `feiskyer--mcp-kubernetes-server` (implied)
- pip (`pip install -e .`) — `echelon-ai-labs--servicenow-mcp` ("more conservative than the uv/uvx-heavy trend among newer servers")
- Lock file not noted; uses uv/uvx — `designcomputer--mysql_mcp_server` (also has legacy `pytest.ini` + `requirements-dev.txt` coexisting with pyproject.toml — "Requirements split across `pyproject.toml` + `pytest.ini` + `requirements-dev.txt` — older Python project layout; most newer projects in the corpus consolidate into pyproject.toml")

### Schema strategy

- FastMCP auto-derives — `duolingo--slack-mcp`
- Hand-authored schemas (low-level SDK) — `designcomputer--mysql_mcp_server` (likely)
- Not surfaced — `echelon-ai-labs--servicenow-mcp`, `feiskyer--mcp-kubernetes-server`

### Async/sync style

- Sync subprocess wrapping — `feiskyer--mcp-kubernetes-server` ("wraps kubectl/helm subprocess calls. The underlying kubectl/helm wrapping is synchronous subprocess. Sync subprocess wrapping rather than using the kubernetes-client async Python library")
- Starlette suggests async — `echelon-ai-labs--servicenow-mcp` (SSE path)
- Not surfaced — `duolingo--slack-mcp`, `designcomputer--mysql_mcp_server`

### Dev ergonomics

- ruff in dev extra — `duolingo--slack-mcp`
- ngrok required for OAuth callback during local dev — `duolingo--slack-mcp`
- MCP Inspector debugging support referenced — `designcomputer--mysql_mcp_server`

## Notable structural choices

Cross-cutting design decisions worth elevating.

### Per-verb capability gating

- `feiskyer--mcp-kubernetes-server` — granular per-capability CLI toggles (`--disable-kubectl`, `--disable-helm`, `--disable-write`, `--disable-delete`) instead of a single read-only/full switch. Per-verb enable/disable as an argument surface pattern. "Four-way verb disable flags is a denial-ish denominator for capability gating"

### Tool catalog as data file

- `docker--hub-mcp` — `tools.json`/`tools.txt` ship tool definitions outside source. "Declarative catalog rather than inline schemas in source — opens an authoring path that doesn't require TS expertise"

### Architectural transport split

- `echelon-ai-labs--servicenow-mcp` — separate console scripts per transport rather than env-var-switched. "A cleaner separation but more install-time ceremony"

### Single-binary multi-transport

- `executeautomation--mcp-playwright` — `--port` switches between stdio and HTTP from one binary. Direct contrast with the architectural split pattern above

### Container as the only artifact

- `elastic--mcp-server-elasticsearch`, `duolingo--slack-mcp` — both ship Docker as the only/primary distribution channel; for `duolingo`, this "inverts the typical Python packaging path"

### LLM-targeted in-repo documentation

- `exa-labs--exa-mcp-server` — `llm_mcp_docs.txt` (411.7 KB) shipped as in-repo doc designed for LLM ingestion

### Read-only server pattern

- `duolingo--slack-mcp` — explicit read-only design (5 tools, no write capabilities)

### Vertical / domain-specific skills as first-class shipping artifact

- `exa-labs--exa-mcp-server` — skills directory with company research, code search, people research, financial reports, academic papers shipped alongside the server

### Vendor-specific companion config

- `docker--hub-mcp` — `gordon-mcp.yml` pre-shaping config for Docker's Ask Gordon agent

### Built-in security guidance in README

- `designcomputer--mysql_mcp_server` — "least-privilege user, never commit credentials" baked into README. Security guidance as a first-class README element

### Remote-hosted endpoint as primary

- `exa-labs--exa-mcp-server` — `https://mcp.exa.ai/mcp` as primary distribution; reduces setup friction. Native Claude Desktop connector eliminates manual config

### Lifecycle declaration in README

- `elastic--mcp-server-elasticsearch` — explicit deprecation notice in README; "the project is superseded by Elastic Agent Builder in ES 9.2.0+". A deprecation-status axis most repos don't surface

### High distribution-channel count

- `executeautomation--mcp-playwright` — npm + mcp-get + Smithery + Docker — four distribution mechanisms; flagged as "a reference for 'how many channels to publish to' decisions"

### Unofficial vs official competing implementations

- `executeautomation--mcp-playwright` (5.5k stars, unofficial) coexists with Microsoft's `@playwright/mcp`. "Both ship, neither is officially crowned" — competitive landscape axis

## License

- MIT — `designcomputer--mysql_mcp_server`, `echelon-ai-labs--servicenow-mcp`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`
- Apache-2.0 — `docker--hub-mcp`, `duolingo--slack-mcp`, `elastic--mcp-server-elasticsearch`, `feiskyer--mcp-kubernetes-server` ("Apache-2.0 license — rarer for independent-maintainer MCP servers, which skew MIT")

## Default branch

- `main` — `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server`
- `master` — `duolingo--slack-mcp`

## Star counts (popularity)

For the bin: 7 (`duolingo--slack-mcp`), 16 (`feiskyer--mcp-kubernetes-server`), 137 (`docker--hub-mcp`), 241 (`echelon-ai-labs--servicenow-mcp`), 646 (`elastic--mcp-server-elasticsearch`), 1.2k (`designcomputer--mysql_mcp_server`), 4.3k (`exa-labs--exa-mcp-server`), 5.5k (`executeautomation--mcp-playwright`).
