# Sample

Pass-1 Phase-1a partial for bin 12. Atomic knowledge chunks from sooperset--mcp-atlassian, spences10--mcp-turso-cloud, stripe--agent-toolkit, supabase-community--supabase-mcp, teaguesterling--duckdb_mcp, the-momentum--fhir-mcp-server, thenets--ghost-mcp, tumf--grafana-loki-mcp, organized by divergence axes. Phase-1b merger will unify with other partials.

## Identification

### Ownership

#### Vendor-owned

Stripe ships from `stripe/agent-toolkit` [`stripe--agent-toolkit`]. Supabase community-org under company watch — `supabase-community/supabase-mcp` is community-canonical with vendor signaling [`supabase-community--supabase-mcp`].

#### Community-canonical without vendor entry

Atlassian has no first-party MCP — `sooperset/mcp-atlassian` (5k stars) is the de facto standard [`sooperset--mcp-atlassian`]. Turso similarly: `spences10/mcp-turso-cloud` is community-built, not under `tursodatabase/*` [`spences10--mcp-turso-cloud`]. Ghost CMS [`thenets--ghost-mcp`] (1 star, very new). Grafana Loki [`tumf--grafana-loki-mcp`].

#### Domain-specific community

`teaguesterling/duckdb_mcp` — DuckDB extension built externally to the DuckDB project [`teaguesterling--duckdb_mcp`]. `the-momentum/fhir-mcp-server` — FHIR-agnostic healthcare server, not tied to any single FHIR vendor [`the-momentum--fhir-mcp-server`].

### Maturity signals

Star-count spread is enormous within a single bin: 5,000 [`sooperset--mcp-atlassian`], 2,600 [`supabase-community--supabase-mcp`], 1,500 [`stripe--agent-toolkit`], 77 [`the-momentum--fhir-mcp-server`], 47 [`teaguesterling--duckdb_mcp`], 25 [`tumf--grafana-loki-mcp`], 15 [`spences10--mcp-turso-cloud`], 1 [`thenets--ghost-mcp`]. High-star community canonicals (Atlassian) backlog-loaded — 171 issues + 91 PRs at 5k stars [`sooperset--mcp-atlassian`]. Conversely, completeness of structure does not track stars: `thenets--ghost-mcp` (1 star) has full Docker Compose dev stack, JWT renewal, dual-API split.

## Language and runtime

### Single-language repos

Python-dominant: [`sooperset--mcp-atlassian`] (99.3%), [`the-momentum--fhir-mcp-server`] (97%), [`thenets--ghost-mcp`] (92.5%), [`tumf--grafana-loki-mcp`] (93.2%). TypeScript-dominant: [`spences10--mcp-turso-cloud`] (92.4%), [`supabase-community--supabase-mcp`] (99.5%).

### Multi-language repos

[`stripe--agent-toolkit`] — TypeScript (51.9%) + Python co-primary in one monorepo, parallel PyPI + npm publishing. [`teaguesterling--duckdb_mcp`] — C++ (73.7%) + Shell (13.1%) + Python (10.6%) + minor TS/JS/HTML; built as a C++ DuckDB extension with multi-language helpers.

### Python version floors

`>=3.10` [`sooperset--mcp-atlassian`, `thenets--ghost-mcp`, `tumf--grafana-loki-mcp`]. `>=3.12` [`the-momentum--fhir-mcp-server`] — leading-edge floor.

## Transport

### Single transport

stdio only (often implicit, inferred from `npx`/`uvx` invocation): [`spences10--mcp-turso-cloud`] (stdio inferred, never named in README), [`thenets--ghost-mcp`] (stdio implied by `uvx`).

HTTP-only: [`supabase-community--supabase-mcp`] — HTTP is canonical mode, no stdio. Managed cloud endpoint primary.

### Multi-transport selection

#### Env-var-driven selection

[`the-momentum--fhir-mcp-server`] — `TRANSPORT_MODE` env var selects stdio/http/https. Fits containerized deployment.

#### CLI-flag / default selection

[`tumf--grafana-loki-mcp`] — stdio + SSE selected via CLI flag/default.

#### SQL-driven selection

[`teaguesterling--duckdb_mcp`] — `PRAGMA mcp_server_start(...)` selects stdio/HTTP from SQL. Plus MCP-client mode via SQL `ATTACH`.

#### Install-target split

[`stripe--agent-toolkit`] — stdio via `npx @stripe/mcp` (local); hosted remote at `https://mcp.stripe.com` with OAuth.

[`sooperset--mcp-atlassian`] — SSE primary; HTTP support mentioned. Likely env-var or subcommand driven.

### Transport surface breadth

Three modes (stdio/http/https) [`the-momentum--fhir-mcp-server`] is among the richest single-server transport surfaces. Servers with HTTP-only [`supabase-community--supabase-mcp`] and stdio-only [`spences10--mcp-turso-cloud`, `thenets--ghost-mcp`] bookend the spectrum.

## Distribution

### Package registries

#### npm only

[`spences10--mcp-turso-cloud`] (`mcp-turso-cloud` via npx).

[`supabase-community--supabase-mcp`] (`@supabase/mcp-server-supabase`).

#### PyPI only

[`sooperset--mcp-atlassian`] (`mcp-atlassian`), [`thenets--ghost-mcp`] (`ghost-mcp`), [`tumf--grafana-loki-mcp`] (`grafana-loki-mcp`).

#### Both PyPI and npm (cross-ecosystem)

[`stripe--agent-toolkit`] — npm: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`. PyPI: `stripe-agent-toolkit`. Parallel naming convention across ecosystems.

#### No registry — source build only

[`teaguesterling--duckdb_mcp`] — `make` build from source; not yet in DuckDB community extensions. [`the-momentum--fhir-mcp-server`] — clone-required; no PyPI publication; `make build` (Docker) or `make uv`.

### Managed/hosted endpoint as distribution

[`supabase-community--supabase-mcp`] — managed endpoint at `https://mcp.supabase.com/mcp`; cloud usage requires no install. Vendor-hosted MCP-as-a-service.

[`stripe--agent-toolkit`] — `https://mcp.stripe.com` hosted endpoint with OAuth, in addition to local stdio.

### Container as distribution

[`sooperset--mcp-atlassian`] — Docker image alongside PyPI. [`the-momentum--fhir-mcp-server`] — Dockerfile + docker-compose.yml; primary install path.

## Entry point and launch

### uvx invocation

[`sooperset--mcp-atlassian`] — `uvx mcp-atlassian`. [`thenets--ghost-mcp`] — `uvx ghost-mcp`. [`tumf--grafana-loki-mcp`] — `uvx grafana-loki-mcp -u ... -k ...`.

### npx invocation

[`spences10--mcp-turso-cloud`] — `npx -y mcp-turso-cloud`. [`stripe--agent-toolkit`] — `npx -y @stripe/mcp --api-key=...`.

### URL-only (no local invocation)

[`supabase-community--supabase-mcp`] — clients configured to hit the HTTPS URL; no command/args.

### SQL-driven entry

[`teaguesterling--duckdb_mcp`] — `PRAGMA mcp_server_start()` from inside a DuckDB session.

### Make/script-driven entry

[`the-momentum--fhir-mcp-server`] — `make build` / `make uv`; `start.py` entry script. [`thenets--ghost-mcp`] — `make run` / `make dev` for development modes.

## Configuration surface

### Env vars only

[`spences10--mcp-turso-cloud`] — `TURSO_API_TOKEN`, `TURSO_ORGANIZATION`, `TURSO_DEFAULT_DATABASE`, `TOKEN_EXPIRATION` (default 7 days), `TOKEN_PERMISSION` (default full-access).

[`sooperset--mcp-atlassian`] — Cloud (`JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`, `CONFLUENCE_*`) plus DC (`JIRA_PERSONAL_TOKEN`).

[`thenets--ghost-mcp`] — `GHOST_URL` + Ghost API keys; env-var presence drives which API surface (Content vs Admin) is active.

[`the-momentum--fhir-mcp-server`] — `TRANSPORT_MODE`, FHIR backend URL + OAuth2 client ID/secret, optional encryption master key.

### CLI flags only

[`stripe--agent-toolkit`] — `--api-key=...` is the documented entry; env-var equivalent not extracted.

### Both env vars and CLI flags

[`tumf--grafana-loki-mcp`] — `GRAFANA_URL` / `GRAFANA_API_KEY` env or `-u` / `-k` CLI flags; flexibility kept for stdio launch.

### URL query parameters

[`supabase-community--supabase-mcp`] — `project_ref`, `read_only`, `features` are URL query params on the HTTP endpoint. Unusual for MCP; fits HTTP transport. Embeds scope into the endpoint itself.

### SQL pragmas

[`teaguesterling--duckdb_mcp`] — `PRAGMA mcp_server_start()`, `PRAGMA mcp_publish_tool(...)` carry config arguments. Plus a JSON config file for HTTP/token settings.

## Authentication

### Static API key / token

[`spences10--mcp-turso-cloud`] — Turso org-level API token. [`sooperset--mcp-atlassian`] — Atlassian API tokens (Cloud) and Personal Access Tokens (Server/DC). [`tumf--grafana-loki-mcp`] — Grafana API key. [`stripe--agent-toolkit`] — Stripe secret keys; Restricted API Keys (RAK) recommended as best practice — credential-scoping guidance is elevated in docs.

### OAuth flows

#### OAuth 2.0

[`sooperset--mcp-atlassian`] — Cloud OAuth 2.0 supported per docs.

#### OAuth 2.1

[`supabase-community--supabase-mcp`] — automatic prompt during client setup; browser-based consent; tokens managed by MCP client/host. Early adopter of OAuth 2.1 in MCP space.

#### OAuth 2.0 client-credentials

[`the-momentum--fhir-mcp-server`] — against the FHIR backend (e.g. Medplum).

#### OAuth on hosted endpoint only

[`stripe--agent-toolkit`] — OAuth for `mcp.stripe.com` hosted endpoint; static keys for local stdio.

### JWT with auto-renewal

[`thenets--ghost-mcp`] — Admin API uses JWTs from `id:secret` format; tokens expire after 5 minutes with automatic renewal and caching inside the server. Server-managed token rotation.

### Bearer tokens (HTTP server mode)

[`teaguesterling--duckdb_mcp`] — Bearer-token auth in HTTP server mode; credentials from JSON config file.

### Server-internal credential vault

[`the-momentum--fhir-mcp-server`] — encrypted credential storage with optional master-key-based encryption for sensitive fields. In-server vault, unusual; HIPAA/PHI-driven.

### Generated short-lived child tokens

[`spences10--mcp-turso-cloud`] — org-level token generates database-specific tokens automatically with configurable permission granularity. `TOKEN_EXPIRATION` and `TOKEN_PERMISSION` promote short-lived child-token generation as a security primitive.

### Dual-protocol auth split

[`thenets--ghost-mcp`] — Content API uses query-parameter auth with 26-char hex API keys; Admin API uses JWT. Two credential lifecycles managed by one server.

## Multi-tenancy

### Single instance per process

[`sooperset--mcp-atlassian`] (one Atlassian site), [`spences10--mcp-turso-cloud`] (single org per deployment), [`stripe--agent-toolkit`] stdio mode (one API key → one Stripe account), [`thenets--ghost-mcp`] (one `GHOST_URL`), [`tumf--grafana-loki-mcp`] (one Grafana instance), [`the-momentum--fhir-mcp-server`] (not addressed; effectively single).

### Per-request tenancy via URL params

[`supabase-community--supabase-mcp`] — `project_ref` URL parameter scopes each connection. OAuth identity × project ref defines tenant boundary per session.

### Per-user OAuth tenancy

[`stripe--agent-toolkit`] hosted mode — each user authorizes their own Stripe account via OAuth.

### Database-scoped sub-tenancy

[`spences10--mcp-turso-cloud`] — per-database token permissions provide isolation within an organization.

### Database-instance keyed

[`teaguesterling--duckdb_mcp`] — server keyed to the DuckDB database; no per-request handling.

## Capabilities

### Tool surface size

#### Large (50+)

[`sooperset--mcp-atlassian`] — 72 tools across Jira and Confluence.

#### Medium (10-30)

[`thenets--ghost-mcp`] — 15+ across Content (10) + Admin (6) + utility. [`the-momentum--fhir-mcp-server`] — 14+ across FHIR resources, document management, LOINC terminology lookup.

#### Small or unspecified

[`spences10--mcp-turso-cloud`], [`supabase-community--supabase-mcp`], [`stripe--agent-toolkit`], [`teaguesterling--duckdb_mcp`], [`tumf--grafana-loki-mcp`].

### Tool-grouping mechanisms

#### Feature-group flag

[`supabase-community--supabase-mcp`] — `features` URL parameter enables/disables tool groups (Account, Documentation, Database, Debugging, Development, Edge Functions, Branching, Storage). Storage disabled by default; Branching is paid/experimental — explicit plan-tier gating surfaced through tool groups.

#### Read-only vs write-capable split

[`supabase-community--supabase-mcp`] — `read_only` URL param. [`spences10--mcp-turso-cloud`] — `execute_read_only_query` (SELECT/PRAGMA) vs `execute_query` (DML/DDL) supports different MCP-client approval workflows.

#### Dual-API surface split

[`thenets--ghost-mcp`] — Content API (10 read-only tools) vs Admin API (6 read/write tools); env-var presence selects which surface is active.

#### No selector observed

[`sooperset--mcp-atlassian`] — 72-tool surface with no documented tool-group selector.

### Output format selection

[`teaguesterling--duckdb_mcp`] — per-tool output format (JSON/Markdown/CSV) — explicit token-efficiency knob.

[`tumf--grafana-loki-mcp`] — output format (text/JSON/markdown) as a tool parameter, rare among MCPs surveyed.

### Custom tool definition at runtime

[`teaguesterling--duckdb_mcp`] — `mcp_publish_tool` PRAGMA makes user-defined parameterized SQL templates first-class discoverable tools.

### Vector/semantic search exposed

[`spences10--mcp-turso-cloud`] — vector similarity search as a first-class tool.

[`the-momentum--fhir-mcp-server`] — embedded RAG pipeline with llama-index + huggingface + pinecone + sentence-transformers + pymupdf inside the MCP server.

### Domain terminology integration

[`the-momentum--fhir-mcp-server`] — LOINC terminology service integration; healthcare ontology bridge.

### Prompt-injection mitigation

[`supabase-community--supabase-mcp`] — SQL results wrapped with anti-injection instructions so LLMs resist following commands embedded in returned data.

## Host integrations

### Hosts named in README

#### Claude Desktop

[`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`teaguesterling--duckdb_mcp`] (via `.mcp.json`), [`the-momentum--fhir-mcp-server`] (via `claude_desktop_config.json`), [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`], [`supabase-community--supabase-mcp`].

#### Cursor

[`sooperset--mcp-atlassian`], [`stripe--agent-toolkit`] (with shipped `.cursor-plugin/`), [`supabase-community--supabase-mcp`].

#### Cline

[`spences10--mcp-turso-cloud`].

#### WSL

[`spences10--mcp-turso-cloud`] — explicit configuration guidance.

#### Windsurf

[`supabase-community--supabase-mcp`].

#### Vercel AI SDK

[`supabase-community--supabase-mcp`] — native MCP client integration via `createToolSchemas()` SDK export. First-class non-Claude integration via shipped tool-schema generator.

[`stripe--agent-toolkit`] — `@stripe/ai-sdk` package for Vercel integration.

### Plugin wrappers shipped in-repo

#### Claude Code plugin

[`stripe--agent-toolkit`] — `.claude-plugin/` directory at repo root.

#### Cursor plugin

[`stripe--agent-toolkit`] — `.cursor-plugin/` directory at repo root.

#### Neither

[`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`supabase-community--supabase-mcp`], [`teaguesterling--duckdb_mcp`], [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`].

## Tests

### Frameworks

pytest + pytest-asyncio + pytest-cov [`the-momentum--fhir-mcp-server`]. pytest + pytest-cov + pytest-asyncio + pytest-anyio [`sooperset--mcp-atlassian`] — both async runtimes side-by-side. pytest with coverage [`tumf--grafana-loki-mcp`]. `make test` and `make test-connection` [`thenets--ghost-mcp`]. `make test` [`teaguesterling--duckdb_mcp`].

Not documented: [`spences10--mcp-turso-cloud`], [`stripe--agent-toolkit`], [`supabase-community--supabase-mcp`].

### Custom pytest markers

[`sooperset--mcp-atlassian`] — `integration`, `dc_e2e` (Data Center e2e), `cloud_e2e` (Cloud e2e). Encodes the on-prem/cloud deployment matrix into the test suite, not just CI config.

## CI

### GitHub Actions confirmed

[`sooperset--mcp-atlassian`], [`supabase-community--supabase-mcp`], [`teaguesterling--duckdb_mcp`], [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`], [`stripe--agent-toolkit`] (specifics not extracted).

### Auxiliary automation

[`spences10--mcp-turso-cloud`] — `.changeset/` (changelog management) + `renovate.json` (dependency automation); explicit Actions workflows not confirmed.

## Container and packaging artifacts

### Dockerfile present

[`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`].

### Docker Compose

[`the-momentum--fhir-mcp-server`] — for server deployment.

[`thenets--ghost-mcp`] — Docker Compose for full Ghost + MySQL test stack (target backend, not the MCP server itself); end-to-end dev-stack bundling, more typical of integration-test frameworks.

### No container artifacts

[`spences10--mcp-turso-cloud`], [`teaguesterling--duckdb_mcp`], [`supabase-community--supabase-mcp`] (managed cloud reduces need), [`tumf--grafana-loki-mcp`] (explicitly absent).

[`stripe--agent-toolkit`] — not extracted.

## Developer ergonomics

### Build and dev tooling

#### Makefile-driven

[`thenets--ghost-mcp`] (`make run`, `make dev`, `make test`, `make test-connection`). [`the-momentum--fhir-mcp-server`] (`make build`, `make uv`, `make test-connection`). [`teaguesterling--duckdb_mcp`] (`make`, `make test`). Uncommon among MCP servers; common in data-ops projects.

#### `mise.toml`

[`supabase-community--supabase-mcp`] — toolchain version pinning.

#### `.devcontainer/`

[`sooperset--mcp-atlassian`].

#### Pre-commit hooks

[`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`], [`tumf--grafana-loki-mcp`].

### Linters and formatters

[`sooperset--mcp-atlassian`] — ruff + black + mypy (double formatter, redundant). [`tumf--grafana-loki-mcp`] — ruff + black + mypy. [`the-momentum--fhir-mcp-server`] — ruff + ty (newer alternative to mypy). [`supabase-community--supabase-mcp`] — biome (TypeScript).

### AI-targeted documentation

[`sooperset--mcp-atlassian`] — `llms.txt` file present; design-for-AI-consumption documentation pattern.

## Repo layout

### Single-package

[`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`teaguesterling--duckdb_mcp`], [`the-momentum--fhir-mcp-server`] (`app/` module), [`thenets--ghost-mcp`] (`src/ghost_mcp/`), [`tumf--grafana-loki-mcp`].

### Monorepo

[`stripe--agent-toolkit`] — multiple SDK packages (Python + TS) coexist with MCP, Vercel-AI integration, and billing components. `.claude-plugin/` and `.cursor-plugin/` ship alongside code.

[`supabase-community--supabase-mcp`] — `/packages` (core packages), `/docs`, `/supabase`, pnpm-managed (`pnpm-workspace.yaml`).

## Python-specific

### SDK / framework variant

#### FastMCP standalone (`fastmcp` package)

[`the-momentum--fhir-mcp-server`] (FastMCP 2.x). [`thenets--ghost-mcp`] (FastMCP 2.12.3 — explicit precise pin). [`tumf--grafana-loki-mcp`] (FastMCP, version not surfaced).

#### Both `mcp` and `fastmcp` pinned

[`sooperset--mcp-atlassian`] — `mcp>=1.8.0,<2.0.0` and `fastmcp>=2.13.0,<2.15.0`. Likely historical: predates FastMCP, migrated partially.

### Build backend

#### `hatchling.build`

[`sooperset--mcp-atlassian`].

#### `uv_build` with non-standard module name

[`the-momentum--fhir-mcp-server`] — module-name `app`. Adoption of `uv`'s native build-backend integration; less common than hatchling.

#### Not captured

[`thenets--ghost-mcp`].

#### Mixed pyproject.toml + setup.py

[`tumf--grafana-loki-mcp`].

### Lock files and version managers

`uv` convention: [`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`]. `uv` + pip compatible: [`tumf--grafana-loki-mcp`].

### Console scripts

[`sooperset--mcp-atlassian`] — `mcp-atlassian = "mcp_atlassian:main"`.

[`the-momentum--fhir-mcp-server`] — `start = start:main` — bare module name `start` rather than `app.start`.

[`thenets--ghost-mcp`] — `ghost-mcp` console script.

[`tumf--grafana-loki-mcp`] — `grafana-loki-mcp` console script.

### Async style

asyncio + anyio side-by-side (pytest-asyncio + pytest-anyio): [`sooperset--mcp-atlassian`]. Likely async via FastMCP 2.x + httpx + FastAPI: [`the-momentum--fhir-mcp-server`]. async/await mentioned as feature: [`thenets--ghost-mcp`]. async-capable via FastMCP: [`tumf--grafana-loki-mcp`].

### Type and schema

Pydantic v2 + pydantic-settings: [`the-momentum--fhir-mcp-server`]. Type-checker: ty: [`the-momentum--fhir-mcp-server`]. mypy: [`tumf--grafana-loki-mcp`], [`sooperset--mcp-atlassian`].

## Notable structural choices

### Vendor/community canonical positioning

Community-canonical at vendor scale [`sooperset--mcp-atlassian`] — 5k stars on a non-vendor repo for Atlassian indicates the vendor has not shipped first-party. Same shape: [`spences10--mcp-turso-cloud`].

### Multi-surface agent tooling

[`stripe--agent-toolkit`] — one repo houses SDKs (Python + TS), AI-framework integrations (Vercel), billing primitives, and MCP — MCP treated as one integration channel among peers, not the whole product.

### Per-host plugin wrappers shipped in-repo

[`stripe--agent-toolkit`] — `.claude-plugin/` and `.cursor-plugin/` recognize host-specific plugin formats as a first-class distribution surface.

### Hosted-endpoint + local stdio duality

[`stripe--agent-toolkit`], [`supabase-community--supabase-mcp`]. Sentry / Cloudflare also follow this pattern (referenced in samples).

### Server-blurring architectures

#### MCP-as-SQL-extension

[`teaguesterling--duckdb_mcp`] — MCP surface reachable via SQL PRAGMAs; blurs database and tool-registry roles.

#### Dual server + client mode

[`teaguesterling--duckdb_mcp`] — server for AI assistants AND client connecting to other MCP resources via SQL `ATTACH`. Single artifact plays both protocol roles.

#### In-server RAG pipeline

[`the-momentum--fhir-mcp-server`] — embedding + vector-store + document-parsing stack inside the MCP process. Most servers expose tools that call upstream RAG; this one hosts the RAG itself.

### Compliance-driven encryption features

[`the-momentum--fhir-mcp-server`] — master-key encryption for sensitive credentials; design axis emerging from regulated domains (healthcare, finance, legal).

### Deployment-mode coverage

[`sooperset--mcp-atlassian`] — Cloud + on-prem (Confluence v6.0+, Jira v8.14+) with explicit version floors; deliberate enterprise compatibility uncommon outside first-party vendors.

### Plan-tier gating in the tool surface

[`supabase-community--supabase-mcp`] — Branching tools surfaced as paid/experimental in feature groups; commercial constraints leak into MCP capability listing.

### Dev-stack bundling vs server packaging

[`thenets--ghost-mcp`] — Docker Compose for the target CMS+DB (Ghost+MySQL), not for deploying the MCP server itself; bundles backend stack to enable end-to-end dev. Notable investment for a 1-star repo.

### Proxy-via-fronting-service architecture

[`tumf--grafana-loki-mcp`] — uses Grafana's Loki API as intermediary rather than Loki directly; piggybacks on Grafana auth instead of adding a separate Loki credential surface.

## Unanticipated axes

### Server-managed credential lifecycle

JWT auto-renewal inside the MCP server [`thenets--ghost-mcp`]. Encrypted credential vault [`the-momentum--fhir-mcp-server`]. Short-lived child-token generation [`spences10--mcp-turso-cloud`]. Most MCP servers assume static creds; these don't.

### Output-format-as-tool-parameter

[`teaguesterling--duckdb_mcp`], [`tumf--grafana-loki-mcp`] — token-efficiency / UX dimension most MCP servers skip.

### Domain-ontology bridges

[`the-momentum--fhir-mcp-server`] (LOINC) — pattern likely to recur in legal (Westlaw), education (curriculum standards), finance (ticker/ISIN) per the sample's own observation.

### Tool-registry-as-database-extension

[`teaguesterling--duckdb_mcp`] — running MCP as a DuckDB extension, exposing PRAGMAs and SQL, blurs the database-vs-tool-registry boundary.

### URL-parameter configuration

[`supabase-community--supabase-mcp`] — config via URL query params (project_ref, read_only, features) is unusual for MCP and fits HTTP transport naturally.

### Schema export as composable SDK

[`supabase-community--supabase-mcp`] — `createToolSchemas()` doubles the repo as an SDK; consumers can use Supabase tool definitions without routing through MCP.

## Gaps observed across the bin

- Tool-scoping for large surfaces (e.g. 72-tool [`sooperset--mcp-atlassian`]) often unspecified — how users reduce a large surface to a working subset is rarely documented. Contrast with [`supabase-community--supabase-mcp`]'s explicit `features` param.
- Transport names not always in README — [`spences10--mcp-turso-cloud`], [`thenets--ghost-mcp`] omit explicit transport documentation; stdio is inferred from invocation pattern.
- Observability (logs/metrics/tracing/debug flags) not surfaced in nearly every sample — pattern across the bin, not one-off.
- Last-commit dates inconsistently captured.
- Container artifact presence/absence consistently noted but content (multi-stage builds, base image choices) is not.
