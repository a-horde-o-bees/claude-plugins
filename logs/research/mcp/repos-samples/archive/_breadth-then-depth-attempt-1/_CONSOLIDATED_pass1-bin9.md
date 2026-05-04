# Sample

Pass-1 Phase-1a partial for bin 9. Atomic knowledge chunks from 8 samples (`mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`, `mukul975--cve-mcp-server`, `neondatabase--mcp-server-neon`, `normaltusker--kotlin-mcp-server`, `openags--paper-search-mcp`, `opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science`), organized by divergence axes. Phase-1b merger will unify with other partials.

## Identification

### Governance

Authorship and license signals correlate with project shape.

- Vendor-authored servers — MongoDB, MotherDuck, Neon, AWS-style — ship under permissive licenses (Apache-2.0, MIT) and track product releases [`mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`, `neondatabase--mcp-server-neon`]
- Project-governed (not single-vendor) appears in [`opensearch-project--opensearch-mcp-server-py`] (Apache-2.0, project-maintained, formal `DEVELOPER_GUIDE.md` + `USER_GUIDE.md` split) and [`pathintegral-institute--mcp.science`] (academic monorepo, `CITATION.cff` metadata, GitHub Pages site)
- Community single-maintainer aggregator — [`mukul975--cve-mcp-server`] (MIT, 27 tools across 21 upstream APIs)
- AGPL-3.0 is uncommon in the MCP corpus — [`normaltusker--kotlin-mcp-server`] is the only one in this bin and is a single-maintainer dev-assistant project

### Star-count band

Bin spans low-tens to ~1.2K stars: 28 (`normaltusker`), 120 (`opensearch-project`), 128 (`pathintegral-institute`), 257 (`mukul975`), 468 (`motherduckdb`), 587 (`neondatabase`), ~1000 (`mongodb-js`), ~1200 (`openags`).

### Activity / freshness

- Active vendor releases — MongoDB v1.10.0 April 2026 [`mongodb-js--mongodb-mcp-server`], MotherDuck v1.0.4 March 2026 [`motherduckdb--mcp-server-motherduck`], OpenSearch v0.9.0 March 2026 [`opensearch-project--opensearch-mcp-server-py`], CVE v0.1.0 April 2026 [`mukul975--cve-mcp-server`]
- Possibly dormant — `pathintegral-institute--mcp.science` last release v0.2.0 July 2025; sample flags it may be slowly maintained
- Last-commit not surfaced — `neondatabase--mcp-server-neon`, `openags--paper-search-mcp`, `normaltusker--kotlin-mcp-server` (only commit-count or release reference available)

## Language and runtime

### Language split

- Python-only or Python-dominant — 6 of 8 [`motherduckdb`, `mukul975`, `openags`, `opensearch-project`, `pathintegral-institute`, and effectively `normaltusker` (Python core despite "Kotlin" name)]
- TypeScript / Node — 2 of 8: `mongodb-js--mongodb-mcp-server` (TS 98.6%), `neondatabase--mcp-server-neon` (TS 97.5%, JS 2.2%, CSS 0.3%)
- Mixed-language codebase — `normaltusker--kotlin-mcp-server` carries Python primary plus Kotlin (3.5%) and TypeScript (1.7%) supporting components — server is Python despite the name

### Naming-vs-implementation mismatch

[`normaltusker--kotlin-mcp-server`] — repo name suggests Kotlin but the server is a Python monolith (`kotlin_mcp_server.py`). Worth noting because filename heuristics break for this entry.

### Version floors

- Python `>=3.10` — `motherduckdb`, `mukul975` (3.10+ with 3.11/3.12 recommended), `openags` (3.10–3.13), `pathintegral-institute` (root)
- Python `>=3.8` — `normaltusker` (3.8+ with 3.9+ recommended; black `target-version = py38-py312`)
- Not surfaced — `opensearch-project` (`requires-python` value not extracted)
- Node — `mongodb-js` requires `>=20.19.0` or `22.12.0+` or `23+` (specific point releases pinned); `neondatabase` v18+ for prod, v22+ for dev

### Framework / SDK choice

This is a major divergence axis with at least 5 distinct branches in this bin.

#### FastMCP-only

- `motherduckdb--mcp-server-motherduck` — `fastmcp>=2.14,<3` pinned with tight upper bound (keeps breaking-change surface bounded)
- `mukul975--cve-mcp-server` — FastMCP, 27 `@mcp.tool()` decorators in single `server.py`

#### Raw MCP Python SDK only

- `opensearch-project--opensearch-mcp-server-py` — Anthropic Claude Agent SDK / raw MCP Python SDK; no FastMCP

#### Dual SDK (both `mcp` + `fastmcp` declared)

Notable rare pattern — most repos pick one.

- `openags--paper-search-mcp` — `mcp[cli]>=1.6.0` AND `fastmcp` (no version pin) — likely uses FastMCP for the server surface and `mcp[cli]` for dev/inspector tooling
- `normaltusker--kotlin-mcp-server` — `mcp>=1.0.0` (labeled "Official MCP SDK") AND `fastmcp>=2.0.0` in `requirements.txt`

#### TypeScript MCP SDK

- `mongodb-js--mongodb-mcp-server` — Anthropic MCP TypeScript SDK + internal argument parser
- `neondatabase--mcp-server-neon` — Next.js App Router as hosting surface; MCP tool/handler logic under `mcp-src/`

#### Dispatcher (no top-level SDK at root)

- `pathintegral-institute--mcp.science` — root `pyproject.toml` lists only `click>=8.2.1`; per-server `pyproject.toml`s under `servers/*/` each declare their own SDK choice — root is a dispatcher

### SDK-version pinning style

- Tight upper-bounded — `fastmcp>=2.14,<3` [`motherduckdb`]
- Loose / unpinned — `fastmcp` without version [`openags`]; potential fragility when upstream bumps majors
- Dual-floor — `mcp>=1.0.0` + `fastmcp>=2.0.0` [`normaltusker`]

## Transport

### Supported transports

#### stdio-only

- `mukul975--cve-mcp-server` — outbound-HTTPS only, no inbound listener ports
- `pathintegral-institute--mcp.science` — stdio primary; selected at server invocation via `uvx`

#### stdio + HTTP variants

- `mongodb-js--mongodb-mcp-server` — stdio (default), HTTP with SSE or JSON response modes
- `motherduckdb--mcp-server-motherduck` — stdio (default), HTTP
- `opensearch-project--opensearch-mcp-server-py` — stdio, SSE, streamable-http (three modes in one binary)
- `openags--paper-search-mcp` — stdio default; HTTP indirectly via academic APIs the server consumes (not first-class MCP transport)

#### Remote-hosted Streamable HTTP primary

- `neondatabase--mcp-server-neon` — Streamable HTTP (`/mcp` endpoint) primary; SSE (`/sse`) deprecated/legacy. Endpoint-URL based selection: clients hit `/mcp` for streamable HTTP or `/sse` for legacy

#### stdio + REST bridge sidecar

- `normaltusker--kotlin-mcp-server` — stdio MCP plus HTTP REST API bridge (`vscode_bridge.py`) on port 8080 (configurable). REST bridge is a separate process surface for IDE-native integration

### Transport selection mechanism

- Env var / CLI flag — `mongodb-js` (`TRANSPORT` env / `--transport`, plus `HTTP_HOST`, `HTTP_PORT` for HTTP-mode binding)
- Client config (no flag) — `motherduckdb` (transport selected via Claude Desktop / VS Code settings)
- CLI / config — `opensearch-project`
- Endpoint-URL based — `neondatabase` (different paths route to different transports)
- Installation mode — `normaltusker` (entry point selection: portable, system, or module)

## Distribution

### Distribution channels

#### npm / npx (Node ecosystem)

- `mongodb-js--mongodb-mcp-server` — npm, npx, plus Docker image `mongodb/mongodb-mcp-server:latest`
- `neondatabase--mcp-server-neon` — npm/`npx` for local server; remote-hosted at `mcp.neon.tech` is primary; `npx neonctl@latest init` for client auto-wiring; Cursor IDE install button

#### PyPI / uvx

- `motherduckdb--mcp-server-motherduck` — PyPI `mcp-server-motherduck`, uvx, MCP Bundle (`.mcpb`), GitHub releases
- `openags--paper-search-mcp` — PyPI, `uv tool install`, uvx, Smithery CLI, Docker, source clone (first-class support across all mainstream paths)
- `opensearch-project--opensearch-mcp-server-py` — PyPI via pip only
- `pathintegral-institute--mcp.science` — PyPI namespace `mcp-science`, dispatcher pattern

#### Source-only

- `mukul975--cve-mcp-server` — `pip install -e .` editable install only; not confirmed on PyPI
- `normaltusker--kotlin-mcp-server` — source distribution via interactive installer (`install.py`); not on PyPI

#### Remote hosted

- `neondatabase--mcp-server-neon` — `mcp.neon.tech` primary; OAuth flow; remote-first model rather than local-process default

### Smithery registration

- `openags--paper-search-mcp` — Smithery wrapper published; `npx -y @smithery/cli install @openags/paper-search-mcp --client claude`

### MCP Bundle (`.mcpb`)

Python-ecosystem-specific drag-and-drop bundle for Claude Desktop, observed in only a handful of repos.

- `motherduckdb--mcp-server-motherduck` — `.mcpbignore` file present, suggests MCP bundle packaging workflow

### Custom installer scripts

- `normaltusker--kotlin-mcp-server` — `python3 install.py` interactive installer with 3 modes (portable / system / module); auto-generates IDE config files. Similar in spirit to bespoke installer scripts replacing pip

### Dispatcher / namespace pattern

- `pathintegral-institute--mcp.science` — single PyPI package (`mcp-science`) routes to multiple servers via CLI subcommand (`uvx mcp-science <server-name>`). Hatch `force-include` directive pulls `mcp_science/servers` into the wheel — custom monorepo build shape rather than workspace-based approach

## Entry point / launch

### Console-script style

- `mongodb-mcp-server` — single npm bin [`mongodb-js--mongodb-mcp-server`]
- `mcp-server-motherduck` (`pyproject.toml` `[project.scripts]: mcp-server-motherduck = "mcp_server_motherduck:main"`) [`motherduckdb--mcp-server-motherduck`]
- Dual scripts — `paper-search-mcp` (server) + `paper-search` (standalone CLI) sharing a core library [`openags--paper-search-mcp`]; entries: `paper_search_mcp.server:main`, `paper_search_mcp.cli:main`
- Inferred but not surfaced [`opensearch-project--opensearch-mcp-server-py`]

### Module-only entry (`python -m`)

- `python -m cve_mcp.server` — no console script defined [`mukul975--cve-mcp-server`]

### Multi-mode entry points

- `normaltusker--kotlin-mcp-server` — three invocation modes: `python3 kotlin_mcp_server.py` (direct), `kotlin-android-mcp` (system install), `python -m kotlin_mcp_server` (module). Plus `vscode_bridge.py` for HTTP REST bridge

### Dispatcher entry

- `pathintegral-institute--mcp.science` — `mcp-science = "mcp_science:main"` is the dispatcher; users run `uvx mcp-science <server-name>`

### Wrapper scripts / launchers

- Dockerfile + `deploy/` directory for Azure deployment [`mongodb-js--mongodb-mcp-server`]
- Smithery wrapper [`openags--paper-search-mcp`]
- `vscode_bridge.py` HTTP REST bridge [`normaltusker--kotlin-mcp-server`]
- Vercel deployment pipeline plus `.claude/skills/` skill definitions [`neondatabase--mcp-server-neon`]

## Configuration surface

### Config sources

#### Env-var only

- `mukul975--cve-mcp-server` — env vars (`NVD_API_KEY`, `GITHUB_TOKEN`, `ABUSEIPDB_KEY`, `VIRUSTOTAL_KEY`, `GREYNOISE_API_KEY`, `SHODAN_KEY`, `URLSCAN_KEY`, `CIRCL_PDNS_USER`, `CIRCL_PDNS_PASS`, `REQUEST_TIMEOUT`, `MAX_RETRIES`); `.env` support
- `openags--paper-search-mcp` — `.env`, env vars, Claude Desktop JSON `env` block; provider keys follow `PAPER_SEARCH_MCP_*` prefix convention (uniform prefix across 20+ providers)

#### Multi-source (env + CLI + JSON config)

- `mongodb-js--mongodb-mcp-server` — three sources: env vars prefixed `MDB_MCP_` (e.g. `CONNECTION_STRING`, `API_CLIENT_ID`, `READ_ONLY`, `DISABLED_TOOLS`, `LOGGERS`); camelCase CLI args (`--readOnly`, `--apiClientId`); JSON config file loaded via `MDB_MCP_CONFIG`
- `motherduckdb--mcp-server-motherduck` — CLI arguments for flags, env vars for credentials (`motherduck_token`, AWS credentials)

#### YAML-first

- `opensearch-project--opensearch-mcp-server-py` — YAML config file (`example_config.yml`) plus env vars `OPENSEARCH_DISABLED_CATEGORIES` / `OPENSEARCH_ENABLED_CATEGORIES` for tool filtering; CLI args for further customization. Rarer than env-var-only in the MCP ecosystem

#### URL query params + headers (remote-hosted)

- `neondatabase--mcp-server-neon` — URL query params (`readonly`, `category` for tool filtering, `projectId` for single-project scoping); Authorization bearer header for API-key auth

#### Auto-generated IDE config files

- `normaltusker--kotlin-mcp-server` — three mechanisms: (1) interactive setup `install.py`; (2) env vars (`PROJECT_PATH`, `WORKSPACE_PATH`, `MCP_ENCRYPTION_PASSWORD`, compliance modes); (3) auto-generated IDE config files (`mcp_config_claude.json`, `mcp_config_vscode.json`, `mcp_config.json`); optional `.env`

#### Per-server (monorepo)

- `pathintegral-institute--mcp.science` — client app JSON files; per-server API keys; optional MCPM (Model Context Protocol Manager) for automated wiring

### Env-var prefix conventions

- `MDB_MCP_` [`mongodb-js`] — single uniform prefix across all keys
- `PAPER_SEARCH_MCP_` [`openags`] — single uniform prefix across 20+ provider keys (e.g. `_UNPAYWALL_EMAIL`, `_CORE_API_KEY`, `_SEMANTIC_SCHOLAR_API_KEY`, `_ZENODO_ACCESS_TOKEN`, `_GOOGLE_SCHOLAR_PROXY_URL`, `_IEEE_API_KEY`, `_ACM_API_KEY`)
- `OPENSEARCH_` [`opensearch-project`] — env var convention for category filtering
- No prefix [`mukul975`] — raw upstream-API names (`NVD_API_KEY`, `GITHUB_TOKEN`)

### CLI-flag casing

- camelCase CLI args [`mongodb-js`] — e.g. `--readOnly`, `--apiClientId` — unusual relative to dash-separated convention
- Hyphenated flags [`motherduckdb`] — `--db-path`, `--read-write`, `--allow-switch-databases`, `--motherduck-token` — standard

## Authentication

### Auth flows

#### DB connection string + cloud API credential pair

- `mongodb-js--mongodb-mcp-server` — MongoDB connection string for direct DB; Atlas Service Account (Client ID/Secret) for Atlas API; IP allowlist required for API credentials; temporary auto-generated DB users with configurable TTL (default 4h)

#### Static token

- `motherduckdb--mcp-server-motherduck` — `motherduck_token` env var or `--motherduck-token` parameter; AWS credentials for S3 access

#### OAuth + API key (remote-hosted)

- `neondatabase--mcp-server-neon` — OAuth 2.0 with scopes (`read`, `write`, `*`) primary; API key bearer token as headless alternative. Browser OAuth redirect or `Authorization: Bearer <api-key>` header

#### Multiple auth schemes in one binary

- `opensearch-project--opensearch-mcp-server-py` — basic auth, IAM roles (AWS OpenSearch Service), header-based auth, mTLS — covers self-hosted, managed AWS, and mTLS deployments
- `normaltusker--kotlin-mcp-server` — multiple external API auth schemes: API Keys, OAuth 2.0, JWT tokens, Basic HTTP, Bearer tokens; server-side rate limiting, circuit breaker, audit logging

#### Per-source key (graceful-degradation aggregator)

- `mukul975--cve-mcp-server` — 21 independent API-key authentications, each optional; server degrades gracefully when a key is absent. Keys never logged or cached in audit entries
- `openags--paper-search-mcp` — per-provider API keys, one email (Unpaywall); per-provider credentials applied globally

#### No centralized auth

- `pathintegral-institute--mcp.science` — server-specific API keys for specialized integrations; no centralized authentication mechanism

## Multi-tenancy

### Tenancy models

#### Single-credential per process

Default for most: `motherduckdb`, `mukul975` (one key-set per server instance), `opensearch-project`, `openags` (per-provider credentials applied globally), `pathintegral-institute` (each sub-server is single-user).

#### Per-session via header

- `mongodb-js--mongodb-mcp-server` — HTTP transport supports externally-managed session IDs via `mcp-session-id` header when `EXTERNALLY_MANAGED_SESSIONS=true` — per-session, not per-tenant

#### Per-request via OAuth scope (remote-hosted)

- `neondatabase--mcp-server-neon` — per-request tenancy via OAuth token scoping; supports organization and personal project access via `org_id`/`project_id` in prompts; remote hosted multi-tenant service

#### Workspace-scoped

- `normaltusker--kotlin-mcp-server` — single-user per workspace; workspace-specific via `WORKSPACE_PATH` env var; audit logging suggests multi-tenant awareness

#### Database switching as flag

- `motherduckdb--mcp-server-motherduck` — single-user with ability to switch databases via `--allow-switch-databases` — feature-flagged multi-database workflow

## Capabilities exposed

### Tool count and shape

#### Small surface (<10 tools)

Not represented in this bin.

#### Medium (10–30)

- `motherduckdb--mcp-server-motherduck` — SQL query execution (read/write), database listing, table listing, column inspection, database switching, support for local files / S3 / MotherDuck / in-memory
- `neondatabase--mcp-server-neon` — 20+ tools across Projects, Branches, SQL, Migrations, Optimization, Auth/Data API provisioning, Discovery; read-only mode exposes 13 specific tools
- `mukul975--cve-mcp-server` — 27 tools across 8 categories (vulnerability intelligence, exploits, risk reporting, network intelligence, threat intel, DevSecOps) over 21 upstream data sources

#### Large (30–60)

- `normaltusker--kotlin-mcp-server` — 32 tools across 10 categories (Core Development 7, UI 4, Architecture 6, Security & Compliance 4, AI/ML 3, File Mgmt 2, API 4, Testing 2, Git 4, QoL 7)
- `opensearch-project--opensearch-mcp-server-py` — 40+ tools — 9 core (default-enabled), 10 additional analysis (default-disabled), 21 Search Relevance Workbench (`search_relevance` category), 2 Skills tools
- `mongodb-js--mongodb-mcp-server` — ~60 tools spanning DB ops (find/aggregate/insert/update/delete/explain), metadata, DDL, Atlas management (clusters, projects, users, access lists, alerts), Atlas Stream Processing, Assistant KB search

#### Multiplexed across many backends

- `openags--paper-search-mcp` — unified `search_papers` and `download_with_fallback` tools plus platform-specific search/download/read across 20+ academic sources (arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, Semantic Scholar, Crossref, OpenAlex, PMC, CORE, Europe PMC, dblp, OpenAIRE, CiteSeerX, DOAJ, BASE, Zenodo, HAL, SSRN, Unpaywall, optional Sci-Hub)

#### Per-sub-server (monorepo)

- `pathintegral-institute--mcp.science` — specialized functions per sub-server: web content retrieval, academic searches, code execution (Python, SSH), scientific computation (DFT via GPAW), database operations (TinyDB), Jupyter kernel interaction, Wolfram Language evaluation

### Tool gating mechanisms

#### Per-tool disable list

- `mongodb-js--mongodb-mcp-server` — `DISABLED_TOOLS` env var

#### Read-only mode flag

- `mongodb-js--mongodb-mcp-server` — `--readOnly` disables mutating tool surface
- `motherduckdb--mcp-server-motherduck` — `--read-write` flag toggles safety posture
- `neondatabase--mcp-server-neon` — `readonly` URL query param; read-only mode exposes 13 specific tools

#### Index-check / safety-rejection flag

- `mongodb-js--mongodb-mcp-server` — `--indexCheck` rejects collection scans (unusual safety posture beyond simple read-only)

#### Confirmation-required tool list

- `mongodb-js--mongodb-mcp-server` — `CONFIRMATION_REQUIRED_TOOLS` triggers MCP elicitation for destructive tools like drop-database

#### Category-based on/off

- `opensearch-project--opensearch-mcp-server-py` — env vars `OPENSEARCH_ENABLED_CATEGORIES` / `OPENSEARCH_DISABLED_CATEGORIES`; category-level on/off rather than per-tool. Default-disabled categories let operators prune the 40-tool surface to just the core 9
- `neondatabase--mcp-server-neon` — `category` URL query param for tool filtering (granular scope beyond simple read-only)

#### Dry-run

- `mongodb-js--mongodb-mcp-server` — `--dryRun` dumps resolved config and exits without booting server

#### Per-request override

- `mongodb-js--mongodb-mcp-server` — `--allowRequestOverrides=true` lets per-request headers/query params override config — powerful for HTTP multi-client setups

### Resources

- `mongodb-js--mongodb-mcp-server` — `config://config` (redacted), `debug://mongodb` (diagnostics), `exported-data://{name}` (temporary exports with auto-cleanup, default 5 min)

### Prompts / sampling / roots

Most samples report no prompts/sampling/roots:

- `mongodb-js--mongodb-mcp-server` — explicitly no prompts/sampling/roots

## Observability

### Logging destinations

#### Pluggable / multi-target

- `mongodb-js--mongodb-mcp-server` — `LOGGERS` env var; targets: `disk` (default `~/.mongodb/mongodb-mcp/.app-logs`), `mcp` (to client), `stderr`. `MCP_CLIENT_LOG_LEVEL` controls severity (default `debug`)

#### Rotating JSON audit log as a capability surface

- `mukul975--cve-mcp-server` — rotating JSON audit log at `~/.cve-mcp/audit.log` (50MB, 5 backups); fields: timestamp, tool name, parameters, duration, cache-hit status; API keys and response payloads explicitly redacted. Audit-log surfaced as a capability, not just ops telemetry

#### Compliance / GDPR / HIPAA modes

- `normaltusker--kotlin-mcp-server` — audit logging for security events; GDPR, HIPAA modes mentioned

#### Vendor logging stack

- `neondatabase--mcp-server-neon` — Winston-based logging with configurable levels; Sentry integration; analytics integration

#### Not surfaced / minimal

- `motherduckdb--mcp-server-motherduck`, `openags--paper-search-mcp`, `opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science` — observability not explicitly documented

### Health endpoints

- `mongodb-js--mongodb-mcp-server` — optional monitoring-server health endpoint (HTTP transport only) — separable sidecar

## Host integrations

### Claude Desktop

JSON `mcpServers` entry standard across all 8 samples. Notable platform-specific config paths surfaced by `mukul975--cve-mcp-server` — `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS), `%APPDATA%\Claude\` (Windows).

### Claude Code

- Dedicated CLI commands [`motherduckdb--mcp-server-motherduck`]
- `claude mcp add cve-mcp --env-file .env -- python -m cve_mcp.server` [`mukul975--cve-mcp-server`]
- Supported but not explicitly documented [`openags--paper-search-mcp`, `neondatabase--mcp-server-neon`, `normaltusker--kotlin-mcp-server` (Claude Code not explicitly mentioned)]
- Not documented [`pathintegral-institute--mcp.science`]

### Cursor / VS Code / Copilot

- `mongodb-js` — VS Code (Insiders), Cursor, Claude Desktop, Copilot CLI, OpenCode (install badges)
- `motherduckdb` — Cursor, VS Code, Codex CLI, Gemini CLI
- `neondatabase` — Cursor IDE install button, VS Code + GitHub Copilot, Cline, Windsurf, Zed
- `normaltusker` — Cursor, VS Code, JetBrains IDEs (auto-generated `mcp_config_vscode.json` shared between Cursor/VS Code; native JetBrains support)
- `opensearch-project` — Claude Desktop and LangChain
- `openags` — Claude Desktop, Claude Code, Smithery

### Smithery / MCPM

- `openags--paper-search-mcp` — Smithery registered install target
- `pathintegral-institute--mcp.science` — MCPM (Model Context Protocol Manager) for automated client integration

### LangChain

- `opensearch-project--opensearch-mcp-server-py` — integration supported

## Claude Code plugin wrapper

### Presence forms

#### Skill files in-tree

- `openags--paper-search-mcp` — `claude-code/` directory contains Claude Code skill files; explicit skill-layer integration rather than just host-config JSON
- `neondatabase--mcp-server-neon` — `.claude/skills/` skill definitions present in repo; Claude Code skill wiring rather than a plugin manifest

#### Wrapper mentioned but shape ambiguous

- `motherduckdb--mcp-server-motherduck` — `.claude-plugin` wrapper mentioned with dedicated CLI commands

#### Not present

- `mongodb-js--mongodb-mcp-server`, `mukul975--cve-mcp-server`, `normaltusker--kotlin-mcp-server`, `opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science` — not present (standard registration only)

## Tests

### Test framework

- Vitest [`mongodb-js--mongodb-mcp-server`] — `vitest.config.ts`, tests under `/tests`
- pytest + pytest-asyncio [`motherduckdb`, `mukul975`, `normaltusker`, `openags` (inferred)]
- Playwright (web E2E) [`neondatabase--mcp-server-neon`]
- Not surfaced framework but `tests/` + `integration_tests/` directories present [`opensearch-project--opensearch-mcp-server-py`]
- Not documented [`pathintegral-institute--mcp.science`]

### Test stratification

#### Unit + integration only

- `motherduckdb--mcp-server-motherduck` — pytest 8.0+ with pytest-asyncio 0.24+; `asyncio_mode = "auto"`; custom `slow` marker for deselection
- `opensearch-project` — `tests/` and `integration_tests/` separate dirs (suggests against-real-OpenSearch validation)

#### Unit + integration + cache + security

- `mukul975--cve-mcp-server` — unit tests (risk scoring, CVSS parsing, validation), integration tests (tool registration, error handling), cache tests (SQLite TTL), security tests (private IP blocking, XML bomb protection — defusedxml)

#### Unit + integration + E2E + web E2E

- `neondatabase--mcp-server-neon` — pyramid: unit (pure logic), integration (tool contracts), E2E (MCP protocol with real clients), web E2E (Playwright, ephemeral DB). `pnpm run test`

#### End-to-end regression

- `openags--paper-search-mcp` — E2E regression tests mentioned

### Lint / type-check stack

- `normaltusker--kotlin-mcp-server` — Black (100-char line limit), isort, MyPy strict, Bandit security scans excluding tests
- `motherduckdb--mcp-server-motherduck` — ruff
- `mongodb-js--mongodb-mcp-server` — custom `eslint-rules/` shipped in repo (suggests codebase-scale discipline)

### Async testing

- `motherduckdb--mcp-server-motherduck` — `asyncio_default_fixture_loop_scope = "function"`, `testpaths = ["tests"]`
- `mukul975--cve-mcp-server` — fully async/await throughout; httpx-based; aiosqlite for cache
- `normaltusker--kotlin-mcp-server` — pytest_asyncio configured; dual-config layout (`pytest.ini` at root + `pyproject.toml` config)

## CI

### Presence

GitHub Actions in `.github/` is universal across samples that surfaced CI: `mongodb-js`, `motherduckdb`, `mukul975`, `neondatabase`, `openags`, `opensearch-project`, `normaltusker` (implied via pyproject tool config).

### Notable CI patterns

- `neondatabase--mcp-server-neon` — Vercel automatic deployment from branches; preview environments per PR
- `normaltusker--kotlin-mcp-server` — Black/isort/MyPy/Bandit configured in `pyproject.toml` (CI pipeline implied)

### Workflow specifics not surfaced

Most samples flag exact workflow contents as out-of-budget — common gap.

## Container / packaging artifacts

### Dockerfile presence

- Multi-stage Dockerfile + `deploy/` Azure guides [`mongodb-js--mongodb-mcp-server`]
- Dockerfile present, `.env.example` for container env injection [`openags--paper-search-mcp`]
- Docker support mentioned for portability; no specific Dockerfile content [`normaltusker--kotlin-mcp-server`] — also `docker-compose.yml` mentioned (`docker-compose up -d kotlin-mcp-server`)
- Docker image published `mongodb/mongodb-mcp-server:latest` [`mongodb-js--mongodb-mcp-server`]

### Notable absences

- No Dockerfile [`opensearch-project--opensearch-mcp-server-py`] — pip/uv-based installs preferred
- No Docker [`motherduckdb--mcp-server-motherduck`] — uv-based Python packaging preferred
- No Docker [`mukul975--cve-mcp-server`]
- No Docker [`pathintegral-institute--mcp.science`] — PyPI distribution

### Vercel / serverless

- `neondatabase--mcp-server-neon` — Vercel-hosted deployment; no Dockerfile observed

## Example client / developer ergonomics

### MCP Inspector launchers

- `mukul975--cve-mcp-server` — `npx @modelcontextprotocol/inspector python -m cve_mcp.server` at `http://localhost:6274`; `.env.example` for key config
- `openags--paper-search-mcp` — `mcp[cli]` dev inspector

### Make targets / dev scripts

- Makefile present [`motherduckdb--mcp-server-motherduck`, `openags--paper-search-mcp`]
- Custom eslint rules + `api-extractor/` for API docs [`mongodb-js--mongodb-mcp-server`]

### Sample configs

- Install badges for multiple hosts [`mongodb-js`]
- Sample configs for Claude Desktop integration [`motherduckdb`]
- `.env.example` [`mukul975`, `openags`]
- JSON config examples per host + `.claude/skills/` definitions + Cursor install button [`neondatabase`]
- Auto-generated config files for Claude Desktop, VS Code, Cursor, generic MCP clients [`normaltusker`]
- `example_config.yml`, `DEVELOPER_GUIDE.md`, `USER_GUIDE.md` [`opensearch-project`] — formal docs split into developer + user guides
- Per-server dedicated README [`pathintegral-institute`]; GitHub Pages site at mcp.science for discoverability

## Repo layout

### Single-package

- `mongodb-js--mongodb-mcp-server` — single-package with auxiliary folders: `src`, `tests`, `deploy`, `scripts`, `resources`, `eslint-rules`, `api-extractor`
- `motherduckdb--mcp-server-motherduck` — single-package Python project with `src/`, `tests/`, `pyproject.toml`, `uv.lock`
- `mukul975--cve-mcp-server` — single package under `src/cve_mcp/` with `api/` (12 client modules), `cache/sqlite_cache.py`, `utils/` (validators, risk_scorer), `models.py`, `audit.py`, `config.py`, `server.py`
- `normaltusker--kotlin-mcp-server` — single-package Python; primary `kotlin_mcp_server.py` (unified 32-tool server, ~112 KB monolith); `vscode_bridge.py` HTTP REST bridge
- `opensearch-project--opensearch-mcp-server-py` — single package under `src/`; separate `tests/` and `integration_tests/`; `docs/`
- `openags--paper-search-mcp` — single-package `paper_search_mcp/` + `claude-code/` skill sibling + `tests/` + `docs/`

### Hosted-app layout (not pure single-package)

- `neondatabase--mcp-server-neon` — `landing/` Next.js app with `app/api/` transport + OAuth endpoints; `mcp-src/` server/tools/handlers; `lib/` OAuth/config helpers; `landing/tests/` test suites; `.claude/skills/`

### Monorepo / dispatcher

- `pathintegral-institute--mcp.science` — `/servers/` subdirectories containing individual server implementations, each with dedicated README, `pyproject.toml`, source. Root has documentation (`README.md`, `CITATION.cff`), config (`pyproject.toml`, `uv.lock`), assets, web (`index.html`, `CNAME` for GitHub Pages)

### Monolith vs modular

- Monolithic single-file server — `kotlin_mcp_server.py` (~112 KB) [`normaltusker`]
- Single `server.py` with 27 decorated tools (rather than per-category module splits) [`mukul975`]

## Notable structural choices

### Safety / destructive-action gating

- `--readOnly` mode [`mongodb-js`, `motherduckdb` (`--read-write` toggles), `neondatabase` (URL param)]
- `--indexCheck` rejects collection scans [`mongodb-js`] — unusual safety posture
- `CONFIRMATION_REQUIRED_TOOLS` triggers MCP elicitation for destructive tools [`mongodb-js`]
- Start/commit migration pattern: agents prepare migrations for human review before applying [`neondatabase`]

### Credential lifecycle

- Temporary auto-generated DB users with configurable TTL (default 4h) instead of long-lived DB credentials [`mongodb-js`]
- Export-artifact resource with auto-cleanup (default 5 min) [`mongodb-js`]

### Audit / hardening

- Rotating JSON audit log with explicit redaction of API keys and response payloads [`mukul975`] — security-conscious by default
- defusedxml usage for XML-bomb hardening (explicitly tested) [`mukul975`]
- Bandit security scans excluding tests [`normaltusker`]
- Server-side rate limiting + circuit breaker + audit logging [`normaltusker`]

### Caching tier

- SQLite TTL cache layer per call (cross-cutting module inside the MCP server) [`mukul975`]
- Token-bucket rate-limiter module for NVD throttling [`mukul975`]

### Aggregator pattern

- 21 upstream APIs behind 27 MCP tools, each API key optional with graceful degradation [`mukul975`]
- 20+ academic backends multiplexed through a common tool surface with uniform env-var prefix convention [`openags`]

### Tool surface scoping

- Category-based enable/disable via env vars rather than per-tool [`opensearch-project`]
- URL query param tool filtering [`neondatabase`]
- Per-request header/query overrides (`--allowRequestOverrides=true`) [`mongodb-js`]

### Co-located Claude Code skills

- `claude-code/` skill files alongside the MCP server [`openags`]
- `.claude/skills/` checked into repo [`neondatabase`]

### Hosted-first vs local-first

- Remote-hosted with OAuth as primary auth [`neondatabase`] — Next.js bundles landing page, OAuth UI, and MCP endpoint together
- Local-process default — most other samples

### Monorepo dispatcher

- Single PyPI package routes to multiple servers via CLI subcommand [`pathintegral-institute`] — Hatch `force-include` directive pulls `mcp_science/servers` into the wheel; custom monorepo build shape rather than workspace-based approach

### Bespoke installer scripts

- `python3 install.py` interactive installer with 3 modes (portable / system / module); auto-generates IDE config files [`normaltusker`] — bespoke installer replacing pip

### Intelligent proxy / transformation systems

- v2.0 proxy architecture with intelligent transformations; "complete, context-aware implementations" rather than stubs [`normaltusker`]

### LSP-like / IDE-bridge

- HTTP REST API bridge (`vscode_bridge.py`) on port 8080 — separate process surface for IDE-native integration [`normaltusker`]
- Auto-generated IDE config files per IDE (Claude Desktop, VS Code, Cursor, JetBrains, generic) [`normaltusker`]

### KB-search / docs-retrieval embedded

- Assistant/KB search tools embed MongoDB documentation retrieval into the same server [`mongodb-js`]
- Discovery tools (search/docs fetch) [`neondatabase`]

### Stream-processing capabilities

- Atlas Stream Processing tool surface [`mongodb-js`]

### Specialized scientific compute

- DFT (GPAW), Wolfram Language, Jupyter kernel interaction [`pathintegral-institute`] — uncommon in MCP ecosystem

### Codebase-scale discipline

- Custom eslint rules shipped in repo [`mongodb-js`]
- API extractor for API docs [`mongodb-js`]
- MyPy strict + Bandit + Black + isort [`normaltusker`]

## Python-specific

### SDK choice (Python branch)

See "Framework / SDK choice" above. Branches in this bin:

- FastMCP-only: `motherduckdb`, `mukul975`
- Raw MCP SDK only: `opensearch-project`
- Dual SDK: `openags`, `normaltusker`
- Dispatcher (no top-level SDK): `pathintegral-institute`

### Build backend

- `hatchling.build` [`motherduckdb`, `openags`, `pathintegral-institute`]
- `pyproject.toml` (build backend not surfaced) [`mukul975`, `normaltusker`, `opensearch-project`]

### Lock files

- `uv.lock` present [`motherduckdb`, `opensearch-project`, `pathintegral-institute` (root)]
- `uv.lock` implied but not confirmed [`openags`]
- `requirements.txt` primary [`normaltusker`] — no lock file confirmed
- Not surfaced [`mukul975`]

### Version manager convention

- `uv` [`motherduckdb`, `opensearch-project`, `openags`, `pathintegral-institute`]
- pip / uv compatible [`mukul975`]
- plain pip + `python3 install.py` orchestrates [`normaltusker`]

### Type / schema strategy

- Pydantic v2 hand-authored models (`CVERecord`, `KEVEntry`, `EPSSScore`, etc.) with custom validators [`mukul975`]
- FastMCP auto-derives schemas from type hints [`motherduckdb`]
- Pydantic via FastMCP / MCP SDK; schema auto-derived [`openags`]
- Modern Python type hints inferred [`opensearch-project`]
- MyPy strict; hand-authored schemas likely given raw MCP SDK usage [`normaltusker`]

### Async pattern

- Fully async/await throughout; httpx-based async I/O; aiosqlite for cache [`mukul975`]
- Async (httpx + asyncio); FastMCP-standard [`openags`]
- pytest_asyncio configured; async tool execution stated in README [`normaltusker`]
- FastMCP 2.14 supports both sync and async signatures (exact repo style not inspected) [`motherduckdb`]

### Notable Python-stack choices

- `defusedxml + aiosqlite + Pydantic v2` — tighter security/typing baseline than most community MCP servers [`mukul975`]
- `httpx[socks]` for SOCKS-proxy support — reflects real-world scraping/proxy needs for Google Scholar [`openags`]
- `pypdf + lxml + beautifulsoup4` in core deps — paper ingestion does PDF parse and HTML/XML handling in-process rather than deferring to external services [`openags`]
- Tight upper-bounded SDK pin `fastmcp>=2.14,<3` — keeps breaking-change surface bounded [`motherduckdb`]
- Loose unpinned `fastmcp` — likely follows latest; potential fragility [`openags`]
- Carries both `mcp` + `fastmcp` as dependencies — unusual; most repos pick one [`normaltusker`, `openags`]
- Broad Python version range (3.8–3.12 targeted) — inclusive floor for compatibility [`normaltusker`]
- Massive single-file `kotlin_mcp_server.py` (~112 KB) — monolith architecture [`normaltusker`]
- Hatch `force-include` directive for monorepo build — non-standard Hatch configuration [`pathintegral-institute`]
- `uv.lock` committed alongside `pyproject.toml` for reproducible dev envs [`opensearch-project`]
- AGPL-3.0 license uncommon in MCP corpus (mostly MIT/Apache) [`normaltusker`]

## Unanticipated axes observed

### Co-located Claude Code skill bundles

`claude-code/` directory shipping Claude Code skills alongside a generic MCP server is a notable first-class plugin wrapper co-located with the server [`openags`, `neondatabase`]. Aligns MCP server with Claude Code skill workflows.

### Audit log as a capability surface

Rotating JSON audit log surfaced as a capability (structured fields, key redaction), not just ops telemetry [`mukul975`].

### Per-source key optionality with graceful degradation

21 independent integrations, each testable alone, each optional [`mukul975`] — a distinct design discipline for aggregator servers.

### Scope-based tool filtering via URL param

Notable alternative to env-var tool lists [`neondatabase`].

### Database switching as feature flag

Multi-database workflows via `--allow-switch-databases` [`motherduckdb`].

### Web E2E with Playwright + ephemeral DB

Contrasts with most MCP servers that test only in unit/integration [`neondatabase`].

### Dispatcher-style monorepo

Single PyPI package routes to multiple servers via CLI subcommand — unique relative to "one PyPI package per server" monorepos [`pathintegral-institute`].

### Domain specialization (rare niches)

- Android/Kotlin-specific MCP server [`normaltusker`] — most servers are language-agnostic
- Scientific computing (DFT, Wolfram, Jupyter) [`pathintegral-institute`] — academic publication focus with `CITATION.cff`
- 21 security data sources behind one server [`mukul975`] — security-research aggregator

### IDE bridge sidecar

HTTP REST bridge as a separate process surface for IDE-native integration [`normaltusker`] — pattern beyond MCP transport.

### Compliance modes baked in

GDPR, HIPAA modes mentioned [`normaltusker`] — compliance-specific operation modes encoded in the server.

### Monitoring server as separable sidecar

Health endpoint as a separable sidecar for HTTP mode [`mongodb-js`].

### Externally-managed sessions

`mcp-session-id` header support when `EXTERNALLY_MANAGED_SESSIONS=true` lets the host control session identity [`mongodb-js`].

### Citation metadata

`CITATION.cff` for academic publication focus [`pathintegral-institute`] — uncommon in MCP ecosystem.

## Gaps

Common gap patterns across the bin:

- Exact CI workflow triggers / contents — flagged by `mongodb-js`, `motherduckdb`, `mukul975`, `openags`
- Last-commit dates not surfaced [`neondatabase`, `openags`, `normaltusker`]
- Exact SDK version pins / `requires-python` floors not surfaced [`opensearch-project`, `mukul975`]
- Logging destination + format (requires code inspection) [`motherduckdb`]
- Console-script names not surfaced [`opensearch-project`]
- Dockerfile existence ambiguous [`mukul975`, `normaltusker`]
- Test framework / fixture style not surfaced [`opensearch-project`, `pathintegral-institute`]
- `.claude-plugin` wrapper shape ambiguous [`motherduckdb`]
- HTTP bridge transport implementation details [`normaltusker`]
- v2.0 proxy architecture not fully explained [`normaltusker`]
