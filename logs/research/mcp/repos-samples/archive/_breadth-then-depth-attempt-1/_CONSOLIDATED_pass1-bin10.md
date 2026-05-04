# Sample

Pass-1 Phase-1a partial for bin 10. Atomic knowledge chunks from `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp`, `rohitg00--kubectl-mcp-server`, organized by divergence axes. Phase-1b merger will unify with other partials.

## Vendor posture

How the project's relationship to its underlying service shapes the server.

### First-party vendor

Server is published by the same organization that owns the underlying service or product.

- PayPal publishes `@paypal/mcp` under the paypal-org npm namespace; Apache-2.0; first-party canonical despite low star count [`paypal--paypal-mcp-server`]
- Perplexity AI publishes `@perplexity-ai/mcp-server` from the `ppl-ai` GitHub org (org slug differs from brand name) [`ppl-ai--modelcontextprotocol`]
- Qdrant publishes `mcp-server-qdrant` on PyPI as official-vendor build [`qdrant--mcp-server-qdrant`]
- Redis publishes `redis-mcp-server` as official Redis MCP [`redis--mcp-redis`]

### Third-party / community

Server is published by an unrelated developer wrapping a vendor's API or SDK.

- `reminia--zendesk-mcp-server` is community, leverages community SDK `zenpy` rather than direct Zendesk REST — "wrap an existing community SDK" pattern [`reminia--zendesk-mcp-server`]
- `rohitg00--kubectl-mcp-server` is community-maintained for an open ecosystem (Kubernetes); CNCF Landscape listed [`rohitg00--kubectl-mcp-server`]
- `riza-io--riza-mcp` is first-party for the Riza code-interpreter service [`riza-io--riza-mcp`]
- `pragmar--mcp-server-webcrawl` operates over local archives — no vendor relationship at all (sidesteps vendor dimension) [`pragmar--mcp-server-webcrawl`]

> Observation across bin: low star count on first-party vendor releases ("official but unpromoted") — paypal-mcp at 9 stars, riza-mcp at 14 — is a recurring pattern worth flagging for merger [`paypal--paypal-mcp-server`, `riza-io--riza-mcp`].

## Language and runtime

### Python

- Python 3.9+ floor — `rohitg00--kubectl-mcp-server` [`rohitg00--kubectl-mcp-server`]
- Python 3.10+ floor — `pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis` [`pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`]
- Python 3.12+ floor — `reminia--zendesk-mcp-server` (newer than typical) [`reminia--zendesk-mcp-server`]

### Node.js / TypeScript

- TypeScript 95.2% — `ppl-ai--modelcontextprotocol`, Node.js runtime [`ppl-ai--modelcontextprotocol`]
- JS-majority with TS minor — `paypal--paypal-mcp-server` (75.7% JS / 15.8% TS); `riza-io--riza-mcp` (72.2% JS / 27.8% TS) [`paypal--paypal-mcp-server`, `riza-io--riza-mcp`]

### Polyglot wrapper

- `rohitg00--kubectl-mcp-server` — Python core (81.2%) with TypeScript npm wrapper (17.0%) for dual-ecosystem distribution [`rohitg00--kubectl-mcp-server`]

## Framework / SDK choice

### FastMCP

- FastMCP 2.x exact-pinned `fastmcp == 2.7.0` — sensitive to FastMCP API drift [`qdrant--mcp-server-qdrant`]
- FastMCP (major version unsurfaced) — `rohitg00--kubectl-mcp-server` references FastMCP in config [`rohitg00--kubectl-mcp-server`]

### Raw `mcp` Python SDK (low-level)

- `mcp[cli]>=1.26.0` — `redis--mcp-redis` [`redis--mcp-redis`]
- `mcp>=1.3.0` (no `[cli]` extra) — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]
- `mcp>=1.1.2` (no `[cli]` extra) — `reminia--zendesk-mcp-server`; minimal 3-deps stack [`reminia--zendesk-mcp-server`]

### MCP TypeScript SDK

- Standard MCP TypeScript SDK — `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol` [`paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`]

## Transport

### stdio-only (current)

- `paypal--paypal-mcp-server` — stdio default via npx [`paypal--paypal-mcp-server`]
- `pragmar--mcp-server-webcrawl` — stdio with `--interactive` REPL flag for terminal mode [`pragmar--mcp-server-webcrawl`]
- `redis--mcp-redis` — stdio only; README notes "streamable-http transport will be added in the future" (planned, not shipped) [`redis--mcp-redis`]
- `reminia--zendesk-mcp-server` — stdio default [`reminia--zendesk-mcp-server`]

### stdio + HTTP variants

- `ppl-ai--modelcontextprotocol` — stdio default; HTTP server mode via `PORT` and `BIND_ADDRESS` env vars plus CORS support for shared deployments [`ppl-ai--modelcontextprotocol`]
- `qdrant--mcp-server-qdrant` — stdio (default), sse, streamable-http; FastMCP env-driven selection [`qdrant--mcp-server-qdrant`]
- `rohitg00--kubectl-mcp-server` — stdio (default), SSE, streamable-http, HTTP; default 0.0.0.0:8000 for HTTP modes [`rohitg00--kubectl-mcp-server`]

### Transport-not-documented

- `riza-io--riza-mcp` — transport not explicitly specified [`riza-io--riza-mcp`]

## Distribution

### npm / npx

- `@paypal/mcp` — `npx -y @paypal/mcp --tools=all` [`paypal--paypal-mcp-server`]
- `@perplexity-ai/mcp-server` — `npx -y @perplexity-ai/mcp-server`; quick-install badges [`ppl-ai--modelcontextprotocol`]
- `@riza-io/riza-mcp` — `npx @riza-io/riza-mcp` [`riza-io--riza-mcp`]
- `kubectl-mcp-server` (npm wrapper invokes Python package) — `npx -y kubectl-mcp-server` [`rohitg00--kubectl-mcp-server`]

### PyPI (pip)

- `mcp-server-webcrawl` — `pip install mcp-server-webcrawl` (only path shown, no uv/uvx mentioned — pip-only) [`pragmar--mcp-server-webcrawl`]
- `kubectl-mcp-server` — `pip install kubectl-mcp-server[ui]` (extras-gated UI bundle) [`rohitg00--kubectl-mcp-server`]

### PyPI via uvx

- `mcp-server-qdrant` — `uvx mcp-server-qdrant` (default install pattern) [`qdrant--mcp-server-qdrant`]
- `redis-mcp-server` — `uvx --from redis-mcp-server@latest redis-mcp-server` (`uvx --from` with explicit package reference) [`redis--mcp-redis`]
- `redis--mcp-redis` also supports `uvx --from git+https://...` for direct GitHub install [`redis--mcp-redis`]

### Docker

- `qdrant--mcp-server-qdrant` — Dockerfile present [`qdrant--mcp-server-qdrant`]
- `ppl-ai--modelcontextprotocol` — Dockerfile included [`ppl-ai--modelcontextprotocol`]
- `redis--mcp-redis` — `docker build -t mcp-redis .` [`redis--mcp-redis`]
- `reminia--zendesk-mcp-server` — Dockerfile installs from `requirements.lock` for build reproducibility [`reminia--zendesk-mcp-server`]
- `rohitg00--kubectl-mcp-server` — Docker Hub image `rohitghumare64/kubectl-mcp-server:latest` [`rohitg00--kubectl-mcp-server`]

### Editable-install-only ("developer-mode-as-release")

- `reminia--zendesk-mcp-server` — no PyPI release; `uv venv && uv pip install -e .` is the user path; `uv --directory /path/to/repo run zendesk` is the host invocation [`reminia--zendesk-mcp-server`]

### Smithery / one-click installers

- `qdrant--mcp-server-qdrant` — Smithery one-click install for Claude Desktop [`qdrant--mcp-server-qdrant`]

### Dual-ecosystem publishing

- `rohitg00--kubectl-mcp-server` ships under both PyPI and npm (npm wrapper invokes the Python package); allows npm-only hosts to install without Python packaging knowledge — single-implementation-multiple-channels [`rohitg00--kubectl-mcp-server`]

## Configuration surface

### Environment-variable-only

- `qdrant--mcp-server-qdrant` — env-only; CLI args explicitly deprecated [`qdrant--mcp-server-qdrant`]
- `ppl-ai--modelcontextprotocol` — env-dominant (`PERPLEXITY_API_KEY`, `PERPLEXITY_TIMEOUT_MS`, `PERPLEXITY_BASE_URL`, `PORT`, `BIND_ADDRESS`, proxy config) [`ppl-ai--modelcontextprotocol`]

### CLI-flag-first with env fallback

- `redis--mcp-redis` — three sources: CLI flags (extensive: `--url`, `--host`, `--port`, `--username`, `--password`, `--db`, `--ssl`, granular SSL knobs), env vars + `.env` files, Redis URI scheme [`redis--mcp-redis`]
- `pragmar--mcp-server-webcrawl` — CLI flags (`--crawler`, `--datasrc`, `--interactive`) [`pragmar--mcp-server-webcrawl`]

### Mixed env + CLI flags

- `paypal--paypal-mcp-server` — env vars for credentials/environment, CLI flags for tool selection (`--tools=all`) and token override [`paypal--paypal-mcp-server`]
- `rohitg00--kubectl-mcp-server` — env vars (`KUBECONFIG`, `MCP_DEBUG`, `MCP_LOG_FILE`, `MCP_BROWSER_*`, `MCP_AUTH_*`) plus CLI flags (`--disable-destructive`, transport/host/port) [`rohitg00--kubectl-mcp-server`]

### `.env` file via python-dotenv

- `reminia--zendesk-mcp-server` — `.env` file with `python-dotenv`; `.env.example` as dev-config template [`reminia--zendesk-mcp-server`]

### Host-managed JSON config

- `riza-io--riza-mcp` — JSON configuration file (Claude Desktop format); env vars for API credentials [`riza-io--riza-mcp`]

## Authentication

### OAuth 2.0 client credentials

- `paypal--paypal-mcp-server` — bearer token, valid 3-8 hours sandbox / 8 hours production. Server holds single merchant's token for the session. Token-refresh handling is unclear from surface — long sessions may need rotation by the caller [`paypal--paypal-mcp-server`]

### OAuth 2.1 (RFC 9728) — optional bolt-on

- `rohitg00--kubectl-mcp-server` — optional OAuth 2.1 layer on top of stdio/HTTP via `MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE`. Underlying Kubernetes API uses kubeconfig [`rohitg00--kubectl-mcp-server`]

### Static API key (env var)

- `ppl-ai--modelcontextprotocol` — `PERPLEXITY_API_KEY` from Perplexity API Portal [`ppl-ai--modelcontextprotocol`]
- `qdrant--mcp-server-qdrant` — `QDRANT_API_KEY` for Qdrant Cloud or remote [`qdrant--mcp-server-qdrant`]
- `riza-io--riza-mcp` — `RIZA_API_KEY` env var [`riza-io--riza-mcp`]

### Service-native credentials

- `redis--mcp-redis` — Redis ACL (username/password) [`redis--mcp-redis`]
- `reminia--zendesk-mcp-server` — Zendesk API credentials via `zenpy` (token or username/password); from `.env` [`reminia--zendesk-mcp-server`]

### Cloud-native identity (rare)

- `redis--mcp-redis` — Azure EntraID with three sub-flows (service principal, managed identity, default Azure credential) plus automatic token renewal with background refresh. Reflects enterprise Azure deployment pressure; rare among community MCPs [`redis--mcp-redis`]

### kubeconfig file

- `rohitg00--kubectl-mcp-server` — consumes `~/.kube/config` for Kubernetes API auth [`rohitg00--kubectl-mcp-server`]

### No auth (local-archive operation)

- `pragmar--mcp-server-webcrawl` — operates entirely on local archives; no service auth at all. Demonstrates that valid MCP servers need not talk to external services [`pragmar--mcp-server-webcrawl`]

## Multi-tenancy

### Single-tenant per process

All bin samples are single-tenant — token/key/connection is process-scoped:

- Single-merchant per process — `paypal--paypal-mcp-server` [`paypal--paypal-mcp-server`]
- Single-user per API key — `ppl-ai--modelcontextprotocol`, `riza-io--riza-mcp` [`ppl-ai--modelcontextprotocol`, `riza-io--riza-mcp`]
- One Qdrant instance + one default collection — `qdrant--mcp-server-qdrant` [`qdrant--mcp-server-qdrant`]
- Single Redis connection per server (cluster mode is connection topology, not per-request tenancy) — `redis--mcp-redis` [`redis--mcp-redis`]
- Single Zendesk subdomain per instance — `reminia--zendesk-mcp-server` [`reminia--zendesk-mcp-server`]
- One data source per launch (multiple sources require multiple launches) — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]
- Single-user per process; OAuth bolt-on suggests tenant support but documented as single kubeconfig context per server — `rohitg00--kubectl-mcp-server` [`rohitg00--kubectl-mcp-server`]

## Capabilities exposed

Tool surface size, MCP primitives used, and how the server organizes its capabilities.

### Tool-surface size

- Minimal (≤6 tools) — `qdrant--mcp-server-qdrant` (2: store, find), `riza-io--riza-mcp` (6: create_tool, fetch_tool, execute_tool, edit_tool, list_tools, execute_code), `ppl-ai--modelcontextprotocol` (4: search, ask, research, reason), `reminia--zendesk-mcp-server` (~6 ticket tools) [`qdrant--mcp-server-qdrant`, `riza-io--riza-mcp`, `ppl-ai--modelcontextprotocol`, `reminia--zendesk-mcp-server`]
- Medium (~30 tools, domain-grouped) — `paypal--paypal-mcp-server` (Invoices, Payments, Disputes, Shipments, Catalog, Subscriptions, Reporting) [`paypal--paypal-mcp-server`]
- Large (8 categories, multi-DS) — `redis--mcp-redis` (strings, hashes, lists, sets, sorted sets, pub/sub, streams, JSON, plus vector search, server mgmt, docs search) [`redis--mcp-redis`]
- Very large (253 tools across ~20 categories) — `rohitg00--kubectl-mcp-server` partitioned by Kubernetes resource kind [`rohitg00--kubectl-mcp-server`]

### Tool-surface scoping at launch

- `paypal--paypal-mcp-server` exposes a `--tools=all` flag with selective subsets via the same flag — opt-in capability scoping reduces prompt-window noise for users who only need one sub-surface [`paypal--paypal-mcp-server`]
- `rohitg00--kubectl-mcp-server` gates browser-automation feature (26 tools) on `MCP_BROWSER_ENABLED` — env-flag-gated optional bundles [`rohitg00--kubectl-mcp-server`]
- `rohitg00--kubectl-mcp-server` ships safety flag `--disable-destructive` to suppress destructive operations [`rohitg00--kubectl-mcp-server`]

### Tool semantics

- `riza-io--riza-mcp` separates patterns for saved-vs-arbitrary code execution: `create_tool` (save), `execute_tool` (run saved), `execute_code` (run arbitrary without saving). `edit_tool` capability for modifying saved tools is unusual among MCP servers [`riza-io--riza-mcp`]
- `paypal--paypal-mcp-server` tools grouped by business domain (Invoices/Payments/Disputes…) [`paypal--paypal-mcp-server`]
- `ppl-ai--modelcontextprotocol` four-tool surface maps 1:1 to product/model offerings (search → Search API, ask → sonar-pro, research → sonar-deep-research, reason → sonar-reasoning-pro) — tool boundaries mirror product tiers rather than low-level API endpoints [`ppl-ai--modelcontextprotocol`]
- `redis--mcp-redis` per-data-structure tool grouping mirrors Redis command families [`redis--mcp-redis`]

### Tool ergonomics / output control

- `ppl-ai--modelcontextprotocol` has optional `strip_thinking` parameter to remove reasoning tags from output — token-saving feature giving caller control over verbosity [`ppl-ai--modelcontextprotocol`]

### MCP primitives beyond tools

- **Resources** — `reminia--zendesk-mcp-server` uses the resources primitive explicitly: `zendesk://knowledge-base`. Splits read-via-resources from write-via-tools. One of the clearer uses of MCP resources rather than overloading tools for read access [`reminia--zendesk-mcp-server`]
- **Resources + prompts** — `rohitg00--kubectl-mcp-server` exposes 8 resources, 8 prompts alongside its 253 tools [`rohitg00--kubectl-mcp-server`]
- **"Prompt routines" (Markdown, not MCP prompts protocol)** — `pragmar--mcp-server-webcrawl` ships pre-authored Markdown prompts for autonomous tasks (SEO audits, 404 detection, performance analysis) under `prompts/`. Concept adjacent to skills but shipped as plain Markdown rather than as MCP prompts protocol resources [`pragmar--mcp-server-webcrawl`]

### Specialty capabilities

- **In-server documentation search** — `redis--mcp-redis` ships a docs-search tool calling a separate HTTP endpoint via `MCP_DOCS_SEARCH_URL`; RAG-style augmentation attached to a database server [`redis--mcp-redis`]
- **Vector search alongside core data** — `redis--mcp-redis` first-classes vector search alongside Redis data structures [`redis--mcp-redis`]
- **Cluster mode as config axis** — `redis--mcp-redis` `--cluster-mode` flag [`redis--mcp-redis`]
- **Boolean fulltext + multi-extraction-mode search** — `pragmar--mcp-server-webcrawl` supports field-specific queries (url, content, headers, type, status, id, size); content filtering by type (html, img, pdf, video) and HTTP status; extraction modes markdown / snippet / regex / XPath; thumbnail generation for images [`pragmar--mcp-server-webcrawl`]
- **Multi-format crawler-archive compatibility** — `pragmar--mcp-server-webcrawl` reads ArchiveBox, HTTrack, InterroBot, Katana, SiteOne, WARC, wget archives. Unusually broad — most crawler tools target one format [`pragmar--mcp-server-webcrawl`]

## Domain decoupling

When a server allows the user to swap a cross-cutting concern via configuration.

- **Embedding model/provider decoupled from storage** — `qdrant--mcp-server-qdrant` exposes `EMBEDDING_MODEL` and `EMBEDDING_PROVIDER` env vars independently of the storage backend; `fastembed` (ONNX-backed Qdrant lib) gives default no-API-key install [`qdrant--mcp-server-qdrant`]
- **Local-vs-remote backend toggle** — `qdrant--mcp-server-qdrant` `QDRANT_LOCAL_PATH` vs `QDRANT_URL` makes local-path mode a single env switch [`qdrant--mcp-server-qdrant`]
- **Sandbox/production environment branch** — `paypal--paypal-mcp-server` `PAYPAL_ENVIRONMENT` selects SANDBOX or PRODUCTION via single binary; not separate entry points [`paypal--paypal-mcp-server`]

## Observability

### Log-level via env var

- `ppl-ai--modelcontextprotocol` — `PERPLEXITY_LOG_LEVEL` [`ppl-ai--modelcontextprotocol`]
- `redis--mcp-redis` — `MCP_REDIS_LOG_LEVEL` (DEBUG/INFO/WARNING/ERROR/CRITICAL); default WARNING [`redis--mcp-redis`]
- `rohitg00--kubectl-mcp-server` — `MCP_DEBUG` + `MCP_LOG_FILE` [`rohitg00--kubectl-mcp-server`]

### Framework-default logging

- `qdrant--mcp-server-qdrant` — FastMCP-standard logging via env config [`qdrant--mcp-server-qdrant`]

### Interactive REPL doubling as debug surface

- `pragmar--mcp-server-webcrawl` — `--interactive` terminal mode is a custom debug surface; rare among MCP servers that typically rely on MCP Inspector [`pragmar--mcp-server-webcrawl`]

### Not documented

- `paypal--paypal-mcp-server`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp` — observability not extracted [`paypal--paypal-mcp-server`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp`]

## Host integrations

### Claude Desktop

Universal in this bin — every sample documents Claude Desktop integration via JSON snippet:

- `paypal--paypal-mcp-server` — primary host, JSON config snippets [`paypal--paypal-mcp-server`]
- `ppl-ai--modelcontextprotocol` — quick-install badge [`ppl-ai--modelcontextprotocol`]
- `pragmar--mcp-server-webcrawl` — primary; documented as a requirement [`pragmar--mcp-server-webcrawl`]
- `qdrant--mcp-server-qdrant` — JSON snippet for `claude_desktop_config.json` [`qdrant--mcp-server-qdrant`]
- `redis--mcp-redis` — JSON config example [`redis--mcp-redis`]
- `reminia--zendesk-mcp-server` — `uv --directory` invocation pattern [`reminia--zendesk-mcp-server`]
- `riza-io--riza-mcp` — primary [`riza-io--riza-mcp`]
- `rohitg00--kubectl-mcp-server` — JSON `mcpServers` entry [`rohitg00--kubectl-mcp-server`]

### Cursor

- `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `rohitg00--kubectl-mcp-server` [`paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `rohitg00--kubectl-mcp-server`]

### Cline

- `paypal--paypal-mcp-server` [`paypal--paypal-mcp-server`]

### VS Code (Copilot)

- `ppl-ai--modelcontextprotocol` (quick-install badge) [`ppl-ai--modelcontextprotocol`]
- `qdrant--mcp-server-qdrant` (JSON snippet with `uvx`) [`qdrant--mcp-server-qdrant`]
- `redis--mcp-redis` — VS Code + GitHub Copilot, requires `chat.agent.enabled: true` [`redis--mcp-redis`]

### Windsurf

- `ppl-ai--modelcontextprotocol` (badge), `qdrant--mcp-server-qdrant` (JSON snippet), `rohitg00--kubectl-mcp-server` [`ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `rohitg00--kubectl-mcp-server`]

### Kiro

- `ppl-ai--modelcontextprotocol` — quick-install badge [`ppl-ai--modelcontextprotocol`]

### Augment

- `redis--mcp-redis` — supported via Easy MCP feature [`redis--mcp-redis`]

### OpenAI Agents SDK

- `redis--mcp-redis` [`redis--mcp-redis`]

### "15+ other clients" / generic MCP

- `rohitg00--kubectl-mcp-server` — same JSON shape across all [`rohitg00--kubectl-mcp-server`]

### Smithery

- `qdrant--mcp-server-qdrant` — one-click install for Claude Desktop [`qdrant--mcp-server-qdrant`]

## Claude Code plugin wrapper

None of the bin samples ship a `.claude-plugin` directory — uniformly absent across all 8.

- Not present / not observed — `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp`, `rohitg00--kubectl-mcp-server`

## Tests

### pytest with async

- `qdrant--mcp-server-qdrant` — pytest >=8.3.3, pytest-asyncio (auto mode); in-memory Qdrant fixture [`qdrant--mcp-server-qdrant`]
- `redis--mcp-redis` — pytest + pytest-asyncio + pytest-cov + pytest-mock; PEP 735 dependency-groups split into `dev` and `test`; `addopts = --cov=src --cov-fail-under=80` (coverage gate enforced); `asyncio_mode = "auto"` [`redis--mcp-redis`]

### pytest, async unspecified

- `rohitg00--kubectl-mcp-server` — 234+ passing pytest tests; unit + integration + server-initialization suites [`rohitg00--kubectl-mcp-server`]

### Other JS frameworks

- `paypal--paypal-mcp-server` — Jest configured [`paypal--paypal-mcp-server`]
- `ppl-ai--modelcontextprotocol` — vitest configured [`ppl-ai--modelcontextprotocol`]

### Not extracted

- `pragmar--mcp-server-webcrawl`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp` — test framework not surfaced [`pragmar--mcp-server-webcrawl`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp`]

## CI

### GitHub Actions present

- `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `rohitg00--kubectl-mcp-server` — all have `.github/workflows/` [`paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `rohitg00--kubectl-mcp-server`]
- `qdrant--mcp-server-qdrant` documented jobs: lint/type-check/test + release [`qdrant--mcp-server-qdrant`]
- `redis--mcp-redis` — codecov integration; specifics not extracted [`redis--mcp-redis`]

### Not documented

- `pragmar--mcp-server-webcrawl`, `riza-io--riza-mcp` [`pragmar--mcp-server-webcrawl`, `riza-io--riza-mcp`]

## Container / packaging artifacts

### Dockerfile only

- `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `rohitg00--kubectl-mcp-server` (also Docker Hub published image) [`ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `rohitg00--kubectl-mcp-server`]
- `reminia--zendesk-mcp-server` — Dockerfile installs from `requirements.lock` for build reproducibility [`reminia--zendesk-mcp-server`]

### None observed

- `paypal--paypal-mcp-server`, `pragmar--mcp-server-webcrawl`, `riza-io--riza-mcp` [`paypal--paypal-mcp-server`, `pragmar--mcp-server-webcrawl`, `riza-io--riza-mcp`]

## Repo layout

### Single-package Python

- `pragmar--mcp-server-webcrawl` (`docs/`, `prompts/`, `sphinx/`) [`pragmar--mcp-server-webcrawl`]
- `qdrant--mcp-server-qdrant` (`src/mcp_server_qdrant/`) [`qdrant--mcp-server-qdrant`]
- `redis--mcp-redis` (`src/`, `tests/`, `examples/`, Dockerfile, `pyproject.toml`, `server.json`, `uv.lock`) [`redis--mcp-redis`]
- `reminia--zendesk-mcp-server` (`zendesk_mcp_server/`) [`reminia--zendesk-mcp-server`]
- `rohitg00--kubectl-mcp-server` — single-package, modular submodules per resource kind (pods.py, deployments.py, helm.py); separate `resources/` and `prompts/` dirs [`rohitg00--kubectl-mcp-server`]

### Single-package Node.js / mixed JS+TS

- `paypal--paypal-mcp-server` — JS-majority with Shell auxiliary scripts [`paypal--paypal-mcp-server`]
- `ppl-ai--modelcontextprotocol` — single-package TypeScript, source in `/src` [`ppl-ai--modelcontextprotocol`]
- `riza-io--riza-mcp` — minimal (README + `/typescript/` directory) [`riza-io--riza-mcp`]

## Notable structural choices

### Capability scoping at launch

- `--tools=all` opt-in tool surface — `paypal--paypal-mcp-server` reduces prompt-window noise [`paypal--paypal-mcp-server`]
- `MCP_BROWSER_ENABLED` env-gated bundle — `rohitg00--kubectl-mcp-server` browser-automation toggle [`rohitg00--kubectl-mcp-server`]
- `[ui]` extra-gated dashboards — `rohitg00--kubectl-mcp-server` pip extras enable dashboard feature [`rohitg00--kubectl-mcp-server`]
- `--disable-destructive` safety flag — `rohitg00--kubectl-mcp-server` suppresses destructive ops [`rohitg00--kubectl-mcp-server`]

### Output ergonomics

- `strip_thinking` optional param — `ppl-ai--modelcontextprotocol` removes reasoning tags from output [`ppl-ai--modelcontextprotocol`]

### Proxy configuration hierarchy

- `ppl-ai--modelcontextprotocol` — `PERPLEXITY_PROXY` takes priority over `HTTPS_PROXY`/`HTTP_PROXY`. Recognizes corporate/enterprise environments where a service-specific proxy must override system-wide settings [`ppl-ai--modelcontextprotocol`]

### Lock-file-driven Docker reproducibility

- `reminia--zendesk-mcp-server` Dockerfile installs from `requirements.lock` — lock-file-as-build-contract, not pyproject-only [`reminia--zendesk-mcp-server`]

### Read existing data, don't crawl live

- `pragmar--mcp-server-webcrawl` — operates on pre-captured crawler archives, sidesteps rate-limit/politeness/JS-rendering concerns. Reference for "don't crawl inside MCP, index what the user crawled" [`pragmar--mcp-server-webcrawl`]

### Prompt-routine packaging

- `pragmar--mcp-server-webcrawl` ships Markdown prompts as a distribution surface alongside tools — encoding "how to use the server for SEO audits" as reusable content rather than forcing users to rediscover prompting patterns [`pragmar--mcp-server-webcrawl`]

### Single-binary environment branching

- `paypal--paypal-mcp-server` `PAYPAL_ENVIRONMENT` env var routes between sandbox/production rather than separate entry points [`paypal--paypal-mcp-server`]

### `server.json` for MCP server registry

- `redis--mcp-redis` ships `server.json` for MCP server registry wiring [`redis--mcp-redis`]

### Granular SSL knobs

- `redis--mcp-redis` exposes `--ssl-ca-path`, `--ssl-keyfile`, `--ssl-certfile` alongside URI schemes (`redis://`, `rediss://`) [`redis--mcp-redis`]

## Python-specific

### Build backend

- **hatchling** — `qdrant--mcp-server-qdrant`, `reminia--zendesk-mcp-server` [`qdrant--mcp-server-qdrant`, `reminia--zendesk-mcp-server`]
- **setuptools (`setuptools.build_meta`)** — `pragmar--mcp-server-webcrawl` (contrarian vs hatchling-dominated sample) [`pragmar--mcp-server-webcrawl`]
- **setuptools (`setup.py`)** — `rohitg00--kubectl-mcp-server` (older convention vs modern pyproject-only) [`rohitg00--kubectl-mcp-server`]
- **`uv_build`** — `redis--mcp-redis` (`requires = ["uv_build>=0.8.3,<0.12.0"]`) — one of the very few using uv's native build backend [`redis--mcp-redis`]

### Lock files

- `uv.lock` — `redis--mcp-redis` [`redis--mcp-redis`]
- `requirements.lock` — `reminia--zendesk-mcp-server` (used by Dockerfile) [`reminia--zendesk-mcp-server`]
- `.python-version` tracked (implies uv) — `qdrant--mcp-server-qdrant` [`qdrant--mcp-server-qdrant`]
- Not observed — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]

### Version-manager convention

- `uv` ecosystem — `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server` [`qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`]
- plain pip — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]
- pip/uv compatible — `rohitg00--kubectl-mcp-server` [`rohitg00--kubectl-mcp-server`]

### Entry points

- `mcp-server-webcrawl = "mcp_server_webcrawl:main"` — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]
- `mcp-server-qdrant` console script → `mcp_server_qdrant.main:main` — `qdrant--mcp-server-qdrant` [`qdrant--mcp-server-qdrant`]
- `redis-mcp-server = "src.main:cli"` — `redis--mcp-redis`. Note unusual `src.` prefix in module path; most projects use top-level module path [`redis--mcp-redis`]
- `zendesk` console script → `zendesk_mcp_server:main` — `reminia--zendesk-mcp-server`. Unusually short script name but unambiguous in context [`reminia--zendesk-mcp-server`]
- `kubectl-mcp-server` console script — `rohitg00--kubectl-mcp-server` [`rohitg00--kubectl-mcp-server`]

### Async vs sync

- async (FastMCP default + pytest-asyncio auto) — `qdrant--mcp-server-qdrant` [`qdrant--mcp-server-qdrant`]
- async (pytest-asyncio auto, low-level mcp[cli]) — `redis--mcp-redis` [`redis--mcp-redis`]
- async likely (low-level mcp SDK) — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]
- sync likely (zenpy is sync) — `reminia--zendesk-mcp-server` [`reminia--zendesk-mcp-server`]
- not surfaced — `rohitg00--kubectl-mcp-server` (FastMCP default applies) [`rohitg00--kubectl-mcp-server`]

### Schema strategy

- Pydantic 2 direct dep + FastMCP auto-derives — `qdrant--mcp-server-qdrant`. Pydantic pinned `>=2.10.6,<2.12.0` (tight window to track FastMCP compatibility) [`qdrant--mcp-server-qdrant`]
- FastMCP default (Pydantic-based) inferred — `rohitg00--kubectl-mcp-server` [`rohitg00--kubectl-mcp-server`]
- Hand-authored schemas — `pragmar--mcp-server-webcrawl`, `redis--mcp-redis` (low-level MCP SDK) [`pragmar--mcp-server-webcrawl`, `redis--mcp-redis`]
- Raw dicts likely — `reminia--zendesk-mcp-server` (raw mcp SDK handlers typically take dicts) [`reminia--zendesk-mcp-server`]

### Dev tooling

- pre-commit — `qdrant--mcp-server-qdrant` [`qdrant--mcp-server-qdrant`]
- mypy + black + bandit + safety + twine — `redis--mcp-redis` (security scanning as first-class; PyPI publishing pipeline) [`redis--mcp-redis`]
- `fastmcp dev` for Inspector — `qdrant--mcp-server-qdrant` documented [`qdrant--mcp-server-qdrant`]
- `sphinx/` for documentation build — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]
- `--interactive` REPL custom debug surface — `pragmar--mcp-server-webcrawl` [`pragmar--mcp-server-webcrawl`]

### Modern Python project layout

- PEP 735 `[dependency-groups]` with distinct `dev` and `test` groups — `redis--mcp-redis` [`redis--mcp-redis`]
- Coverage fail-threshold (`--cov-fail-under=80`) in `addopts` — `redis--mcp-redis` [`redis--mcp-redis`]

### Minimal-deps posture

- 3-deps runtime stack — `reminia--zendesk-mcp-server` (`mcp`, `python-dotenv`, `zenpy`) [`reminia--zendesk-mcp-server`]
- No dev/test extras in pyproject — `pragmar--mcp-server-webcrawl` (minimal packaging posture) [`pragmar--mcp-server-webcrawl`]

## Cross-bin patterns worth flagging for the merger

- **First-party-but-low-stars pattern** — vendor releases at single-digit / low-double-digit star counts (`paypal--paypal-mcp-server` at 9, `riza-io--riza-mcp` at 14) suggest a recurring "official but unpromoted" axis worth examining across the corpus
- **Capability-scoping flag/extras patterns** — `--tools=all` (paypal), `MCP_BROWSER_ENABLED` (kubectl), `[ui]` extra (kubectl), `--disable-destructive` (kubectl) — multiple distinct mechanisms for "user controls which slice of the surface is loaded". Worth a unified categorization in the merger
- **Lock-file as build contract** — both `reminia--zendesk-mcp-server` (Dockerfile installs from `requirements.lock`) and `redis--mcp-redis` (`uv.lock` in repo) treat lock files as authoritative. May be a divergence axis vs samples that pyproject-only build
- **Editable-install-only distribution** — `reminia--zendesk-mcp-server` "developer-mode-as-release" is a distinct distribution mechanism; worth separating from "PyPI but uses local clone in host config" patterns other samples may surface
- **Prompt-routines vs MCP prompts protocol** — `pragmar--mcp-server-webcrawl` ships Markdown prompts as a separate surface, while `rohitg00--kubectl-mcp-server` exposes 8 prompts via the MCP protocol primitive. Same goal, different mechanism — divergence axis worth tracking
- **MCP resources used vs ignored** — `reminia--zendesk-mcp-server` uses resources for KB read access; `rohitg00--kubectl-mcp-server` exposes 8 resources; most samples in this bin only use tools. The "split read/write across resources/tools" pattern is a divergence axis
- **Cloud-native auth (Azure EntraID) vs static credentials** — `redis--mcp-redis` is the only bin sample with cloud-native identity; flagging because enterprise deployment pressure may be a recurring driver

## Open questions / categorization decisions

- **"Prompt routines" categorization** — placed `pragmar--mcp-server-webcrawl` Markdown prompt routines under "MCP primitives beyond tools" but it is explicitly NOT using the MCP prompts protocol. Alternative home: a separate "Distribution surface" or "Knowledge artifacts shipped alongside server" section. Flagged for merger
- **Editable-install-only categorization** — placed `reminia--zendesk-mcp-server` under Distribution as its own entry but it could equally live under "Notable structural choices" as a posture statement. Flagged
- **Cluster-mode under multi-tenancy** — `redis--mcp-redis` `--cluster-mode` is a connection topology, not per-request tenancy. Currently cited under multi-tenancy single-tenant section as clarification; merger may prefer a distinct "Connection topology" subsection
- **`server.json` placement** — `redis--mcp-redis` ships `server.json` for MCP registry wiring; placed under Notable Structural Choices but could live under Distribution if the registry is a distribution channel
- **Polyglot wrapper category** — `rohitg00--kubectl-mcp-server` has Python core + npm wrapper. Listed under Language and Runtime as "Polyglot wrapper", and again under Distribution as "Dual-ecosystem publishing". The two facets (implementation polyglot vs distribution polyglot) are linked but distinct — merger should decide if one home is sufficient
