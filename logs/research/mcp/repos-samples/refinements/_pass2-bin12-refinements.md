# Pass 2 Refinements — Bin 12

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Capability surface > Dual-API split (read vs write) tool grouping` — `thenets--ghost-mcp.md` (Content API: 10 read-only tools with query-param auth; Admin API: 6 read/write tools with JWT) — Server splits tools into two API surfaces, each backed by an upstream API with its own credential scheme. Read-only operations live under one credential type, mutating operations under another. Distinct from `Read/write tool split` (which is a single auth surface gated by mode) — this path is forced by the upstream having two genuinely separate APIs the server has to bridge. Cross-role with `Authentication > Dual-API split credentials`.

- `Capability surface > Output format selectable per-tool-call` — `tumf--grafana-loki-mcp.md` (text/JSON/markdown for log results), `teaguesterling--duckdb_mcp.md` (JSON/Markdown/CSV per-tool output format) — Tool accepts an output-format parameter so the agent picks human-readable, structured, or token-efficient form per call. Distinct from `Tool consolidation as design pressure` and from response-shape design choices baked at registration time. A token-efficiency/UX knob; rare across the corpus.

- `Capability surface > User-publishable tools (SQL templates)` — `teaguesterling--duckdb_mcp.md` (`PRAGMA mcp_publish_tool` registers a SQL template as a discoverable MCP tool with name, description, properties, required fields, output format) — User-supplied templates become first-class MCP tools at runtime, registered through a meta-tool/PRAGMA call. Already referenced in *Extension points — User-publishable tools meta-tool* but no concrete path under Capability surface; this is the SQL-template specialization.

- `Capability surface > MCP-client mode within server (federation via ATTACH)` — `teaguesterling--duckdb_mcp.md` (DuckDB extension also acts as an MCP *client* connecting out to other MCP servers via SQL `ATTACH`; SQL queries can span multiple MCP-exposed data sources) — The artifact is both server and client: it exposes its own MCP surface and federates other servers' surfaces through the same SQL plane. Cross-role with `Transport > MCP-client mode (server connects out)`.

- `Documentation surface > Bundled host backend Compose stack for E2E` — `thenets--ghost-mcp.md` (Docker Compose with Ghost 5.x + MySQL 8.0 for end-to-end local testing of the CMS backend, with health checks and volume persistence — for testing the server, not deploying it) — Repo bundles the *upstream* service's Compose stack so contributors can run end-to-end tests without provisioning a real Ghost site. Distinct from `Docker Compose for local dev` (which deploys the server); this brings up the upstream the server talks to. Cross-role with `Container artifacts > Docker-Compose backend for end-to-end tests`. (Already exists under *Container artifacts*; cross-link it from *Documentation surface* / *Developer ergonomics*.)

- `Authentication > Server-managed JWT auto-renewal` — `thenets--ghost-mcp.md` (Admin API JWTs generated server-side from `id:secret`, expire after 5 minutes with automatic renewal and caching inside the server) — Specialization of `Server-managed token rotation` for the JWT case: the server holds the secret pair and renews short-lived JWTs transparently for every Admin API call. Distinct from upstream-managed OAuth refresh because the server, not the upstream, mints tokens. May also be covered by sharpening `Server-managed token rotation` (which already names the Ghost JWT example) rather than adding a separate path — reconciler decides.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Server runtime > Python with both MCP SDK and FastMCP declared` — `sooperset--mcp-atlassian.md` adds a concrete pin pattern: `mcp>=1.8.0,<2.0.0` and `fastmcp>=2.13.0,<2.15.0` simultaneously. Existing description already names this as transitional; sample evidence reinforces "predates FastMCP and migrated partially" framing and the dual-import concrete cost.

- `Test stack > pytest with async + coverage` — `sooperset--mcp-atlassian.md` shows custom pytest markers (`integration`, `dc_e2e`, `cloud_e2e`) splitting tests by deployment topology (Cloud vs Server/Data Center). Existing description mentions custom markers like `integration` but does not surface the deployment-topology axis specifically. Could sharpen to: "markers may encode deployment-mode coverage (e.g., `dc_e2e` for on-prem Data Center, `cloud_e2e` for SaaS Cloud) when the server supports multiple deployment substrates." Already partially addressed in current description ("on-prem vs. cloud deployment-mode tests"); the sharpening could call out that the markers ride alongside `integration` rather than replacing it.

- `Schema and types > Async model (cross-cutting) > Async throughout` — `sooperset--mcp-atlassian.md` declares both `pytest-asyncio` and `pytest-anyio` in dev — likely mixing asyncio and anyio async styles. Existing description names async-throughout but does not flag the mixed-style hazard. Could note: "projects sometimes declare both pytest-asyncio and pytest-anyio in dev, suggesting mixed async-runtime test fixtures coexist."

- `Distribution channel > Hosted endpoint (no install)` — `supabase-community--supabase-mcp.md` shows the hosted endpoint (`https://mcp.supabase.com/mcp`) coexisting with a local `supabase start` exposing `http://localhost:54321/mcp` (CLI-bundled variant) plus an npm self-host package (`@supabase/mcp-server-supabase`). Existing description covers vendor-hosted endpoint as a channel; sharpening could note that some hosted-endpoint products triple the surface — managed cloud + CLI-bundled local + self-host npm — rather than picking one.

- `Configuration delivery > URL query parameters on HTTP connection` — `supabase-community--supabase-mcp.md` adds concrete params: `project_ref` (project scope), `read_only` (mode gate), `features` (feature-group toggle). Existing description names URL params as a config surface but does not enumerate the three-axis pattern (scope + mode + feature toggle) that emerges as a coherent design.

- `Capability surface > Capability gating flags (per-tool, per-category, write-mode)` — `supabase-community--supabase-mcp.md` shows `features` URL param as the gating mechanism plus a noteworthy specific: Storage tools disabled by default. Existing description covers gating broadly; could add "default-off subsets are sometimes used to ship sensitive tool families opt-in (e.g., storage/file-management tools off by default, branching gated by paid plan)."

- `Authentication > OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)` — `supabase-community--supabase-mcp.md` shows OAuth 2.1 via browser consent during client setup, with the host (Cursor, Claude, Windsurf) handling the prompt natively. Existing description already covers this; sample evidence reinforces that streaming-HTTP-only deployments treat OAuth 2.1 as the default rather than as an opt-in HTTP bolt-on.

- `Authentication > Dual-API split credentials` — `thenets--ghost-mcp.md` is a concrete instance of the existing description's hypothetical "read-only API with query-param key auth and a write API with JWT". Could replace the hypothetical with Ghost as the canonical example: Content API (query-param key auth, 26-char hex), Admin API (JWT auto-renewed every 5 minutes from `id:secret`). Currently the description's example reads as imagined rather than observed.

- `Repository layout > Monorepo of independent servers` and `Monorepo with multiple published packages` — `stripe--agent-toolkit.md` shows a "MCP plus other agent-integration surfaces" pattern (npm: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`; PyPI: `stripe-agent-toolkit`) treating MCP as a peer to SDKs and Vercel-AI integrations rather than the whole product. Existing `Monorepo with multiple published packages` description names this pattern; Stripe sample reinforces "MCP as one channel among several for an agent-integration toolkit."

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

- `Server runtime > Python with FastMCP` — `the-momentum--fhir-mcp-server.md` and `thenets--ghost-mcp.md` both pin specific FastMCP 2.x versions (`2.12.3` is explicit for thenets) but operate quite differently: thenets is a thin tool-server, the-momentum embeds a full RAG pipeline (llama-index + huggingface + pinecone + sentence-transformers + pymupdf) inside the FastMCP server. Existing description treats FastMCP as one path; the in-server-RAG specialization is large enough that it might warrant a sub-path under `Domain logic and embedded intelligence > Embedded RAG / retrieval pipeline` (which already exists) but cross-linking from `Server runtime > Python with FastMCP` to that path is missing. Not strictly a split — more a cross-link.

- `Server runtime > DuckDB extension (C++) embedding MCP` — `teaguesterling--duckdb_mcp.md` is the canonical example. Existing description already exists; sample fits. The interesting splitting question is whether `Capability surface > Single code-execution tool with sandbox` and the new proposed `User-publishable tools (SQL templates)` should be split or merged. They differ in mechanism (code execution vs templated query parameterization) but are similar in spirit (user authors content the server registers as a tool).

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **`thenets--ghost-mcp.md` Docker Compose for testing the upstream backend (Ghost+MySQL).** Placed under `Container artifacts > Docker-Compose backend for end-to-end tests`. Existing path covers it. The notable axis is that this is a 1-star repo with that level of dev-ergonomics investment — flagged in the sample's `Notable structural choices` originally but at the role-path level there's no place for "investment level" as a signal. Not raising as a refinement, just noting the gap.

- **`stripe--agent-toolkit.md` ships both `.claude-plugin/` and `.cursor-plugin/`.** The consolidated has `Claude Code plugin / skill wrapper > .claude-plugin/ wrapper` but no symmetric `Host integration > .cursor-plugin/ wrapper`. The sample's `.cursor-plugin/` was placed under `Host integration > Cursor` (which mentions `.cursor-plugin/` as one of several Cursor integration shapes). The asymmetry is real — Claude Code wrappers have a top-level role, Cursor wrappers are inline under host integration — but I did not propose a refinement because the consolidated likely treats Claude Code as a deliberate first-class concern. Reconciler may want to revisit if more `.cursor-plugin/` evidence accumulates.

- **`teaguesterling--duckdb_mcp.md` is hard to fit at all.** The runtime is "DuckDB extension," distribution is "make build from source," entry point is "SQL PRAGMA invocation," capability surface includes "user-publishable SQL templates" and "MCP-client mode (federation via ATTACH)." Most of these have paths in the consolidated (`Server runtime > DuckDB extension`, `Distribution channel > Source build with make / CMake`, `Entry point and launch > SQL PRAGMA invocation`) but they're scattered. The sample feels like a single coherent design (database-as-MCP-host) split across 8+ roles. Not a refinement — just noting the architectural unity is invisible at the role level.

- **`supabase-community--supabase-mcp.md` HTTP-first, no stdio path.** The sample exhibits HTTP/Streamable HTTP exclusively — no stdio mode documented. Most MCP servers offer stdio as a baseline; this one skips it. Placed `Transport > Streamable HTTP` only (no `stdio` sibling). The consolidated's `Transport > Selection mechanism > Implicit single mode` covers HTTP-only deployments; sample fits but the "no stdio at all" stance is rare and worth flagging at description level.

- **`spences10--mcp-turso-cloud.md` transport never explicitly named.** README does not call out stdio; it's inferred from npx-launch pattern. Placed under `Transport > stdio` per the corpus's "stdio is the default for npx-launched servers" convention; the original sample's `Gaps` section already flags this as inferred rather than documented. No refinement needed — the existing `stdio` description already says "Often selected implicitly — README shows the launch command without naming the transport."

- **`spences10--mcp-turso-cloud.md` two-tier token model.** `TURSO_API_TOKEN` is org-level; the server mints per-database tokens with `TOKEN_EXPIRATION` and `TOKEN_PERMISSION`. Placed under `Authentication > Server-managed token rotation` (which explicitly names "Turso per-database tokens minted from an org-level token") and `Multi-tenancy > Sub-tenancy via child-credential generation` (which also names this). Both paths fit cleanly; the sample is well-served by existing structure.

- **`sooperset--mcp-atlassian.md` 72-tool surface.** Large enough to fit `Tools-heavy domain wrapper / domain-tool catalog` (20-60+ tools). Placed there. The sample's `Notable structural choices` flagged the absence of an explicit tool-group selector; consolidated has `Capability gating flags (per-tool, per-category, write-mode)` which would naturally apply but the sample doesn't take that path (no gating mechanism documented for mcp-atlassian). Marked the absence implicitly by *not* placing the sample under that path; reconciler should treat absence as "no selector observed" rather than "selector exists, undocumented."

- **`stripe--agent-toolkit.md` low extraction depth.** Many fields in original sample marked "not extracted within budget" (last commit, exact tool list, CI specifics, Dockerfile presence). I preserved the absence by not placing the sample under those paths. The sample's preamble flags this so the reconciler can weigh it accordingly.

- **`the-momentum--fhir-mcp-server.md` `uv_build` backend with module name `app`.** Placed under `Build and packaging > uv_build backend (Python)` (which already names this exact pattern). The non-standard module-name `app` rather than the package name is noted in the existing description; sample fits cleanly.
