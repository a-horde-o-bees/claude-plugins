# Pass 3 Refinements — Bin 12

Pass 3 (Attempt 2) refinements to `_CONSOLIDATED_breadth-then-depth.md` from a second normalize cycle on the bin 12 samples. Samples were already in role-tree format from Pass 2; this pass verified chain-key alignment, applied targeted prose updates (cross-corpus phrasing trims, inline-citation removal), and re-surfaces unresolved structural concerns from Pass 2 that the reconciler has not yet integrated.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Capability surface > Dual-API split (read vs write) tool grouping` — `thenets--ghost-mcp.md` (Content API: 10 read-only tools with query-param key auth; Admin API: 6 read/write tools with JWT) — Server splits tools into two API surfaces, each backed by an upstream API with its own credential scheme. Read-only operations live under one credential type, mutating operations under another. Distinct from `Read/write tool split` (which is a single auth surface gated by mode) — this path is forced by the upstream having two genuinely separate APIs the server has to bridge. Cross-role with `Authentication > Dual-API split credentials`. Carried forward from Pass 2 unresolved.

- `Capability surface > Output format selectable per-tool-call` — `tumf--grafana-loki-mcp.md` (text/JSON/markdown for log results), `teaguesterling--duckdb_mcp.md` (JSON/Markdown/CSV per-tool output format) — Tool accepts an output-format parameter so the agent picks human-readable, structured, or token-efficient form per call. Distinct from `Tool consolidation as design pressure` and from response-shape design choices baked at registration time. A token-efficiency/UX knob. Carried forward from Pass 2 unresolved.

- `Capability surface > User-publishable tools (SQL templates)` — `teaguesterling--duckdb_mcp.md` (`PRAGMA mcp_publish_tool` registers a SQL template as a discoverable MCP tool with name, description, properties, required fields, output format) — User-supplied templates become first-class MCP tools at runtime, registered through a meta-tool/PRAGMA call. Already referenced in `Capability surface > User-publishable tools meta-tool` but the SQL-template specialization is a distinct mechanism (templated query parameterization vs code execution). Carried forward from Pass 2 unresolved.

- `Capability surface > MCP-client mode within server (federation via ATTACH)` — `teaguesterling--duckdb_mcp.md` (DuckDB extension also acts as an MCP *client* connecting out to other MCP servers via SQL `ATTACH`; SQL queries can span multiple MCP-exposed data sources) — The artifact is both server and client: it exposes its own MCP surface and federates other servers' surfaces through the same SQL plane. Cross-role with `Transport > MCP-client mode (server connects out)` (which already covers the transport mechanism). Carried forward from Pass 2 unresolved.

- `Authentication > Server-managed JWT auto-renewal` — `thenets--ghost-mcp.md` (Admin API JWTs generated server-side from `id:secret`, expire after 5 minutes with automatic renewal and caching inside the server) — Specialization of `Server-managed token rotation` for the JWT case: the server holds the secret pair and renews short-lived JWTs transparently for every Admin API call. Distinct from upstream-managed OAuth refresh because the server, not the upstream, mints tokens. Reconciler decision: separate path or sharpening of the existing `Server-managed token rotation` description. Carried forward from Pass 2 unresolved.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Server runtime > Python with both MCP SDK and FastMCP declared` — `sooperset--mcp-atlassian.md` adds a concrete pin pattern: `mcp>=1.8.0,<2.0.0` and `fastmcp>=2.13.0,<2.15.0` simultaneously. Existing description already names this as transitional; sample evidence reinforces "predates FastMCP and migrated partially" framing and the dual-import concrete cost. Carried forward from Pass 2 unresolved.

- `Test stack > pytest with async + coverage` — `sooperset--mcp-atlassian.md` shows custom pytest markers (`integration`, `dc_e2e`, `cloud_e2e`) splitting tests by deployment topology (Cloud vs Server/Data Center). Sharpening: markers may encode deployment-mode coverage (e.g., `dc_e2e` for on-prem Data Center, `cloud_e2e` for SaaS Cloud) when the server supports multiple deployment substrates, riding alongside the conventional `integration` marker rather than replacing it. Carried forward from Pass 2 unresolved.

- `Schema and types > Async model (cross-cutting)` — `sooperset--mcp-atlassian.md` declares both `pytest-asyncio` and `pytest-anyio` in dev — likely mixing asyncio and anyio async styles. Sharpening: projects sometimes declare both `pytest-asyncio` and `pytest-anyio` in dev, suggesting mixed async-runtime test fixtures coexist. Carried forward from Pass 2 unresolved.

- `Distribution channel > Hosted endpoint (no install)` — `supabase-community--supabase-mcp.md` shows the hosted endpoint (`https://mcp.supabase.com/mcp`) coexisting with a local `supabase start` exposing `http://localhost:54321/mcp` (CLI-bundled variant) plus an npm self-host package (`@supabase/mcp-server-supabase`). Sharpening: some hosted-endpoint products triple the surface — managed cloud + CLI-bundled local + self-host npm — rather than picking one. Carried forward from Pass 2 unresolved.

- `Configuration delivery > URL query parameters on HTTP connection` — `supabase-community--supabase-mcp.md` adds concrete params: `project_ref` (project scope), `read_only` (mode gate), `features` (feature-group toggle). Sharpening: enumerate the three-axis pattern (scope + mode + feature toggle) that emerges as a coherent design when URL params replace env-var/CLI-flag config. Carried forward from Pass 2 unresolved.

- `Capability surface > Capability gating flags (per-tool, per-category, write-mode)` — `supabase-community--supabase-mcp.md` shows `features` URL param as the gating mechanism plus a noteworthy specific: Storage tools disabled by default. Sharpening: default-off subsets are sometimes used to ship sensitive tool families opt-in (e.g., storage/file-management tools off by default, branching gated by paid plan). Carried forward from Pass 2 unresolved.

- `Authentication > OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)` — `supabase-community--supabase-mcp.md` shows OAuth 2.1 via browser consent during client setup, with the host (Cursor, Claude, Windsurf) handling the prompt natively. Sharpening: streaming-HTTP-only deployments treat OAuth 2.1 as the default rather than as an opt-in HTTP bolt-on. Carried forward from Pass 2 unresolved.

- `Authentication > Dual-API split credentials` — `thenets--ghost-mcp.md` is a concrete instance of the existing description's hypothetical "read-only API with query-param key auth and a write API with JWT". Sharpening: replace the hypothetical with Ghost as the canonical example — Content API (query-param key auth, 26-char hex), Admin API (JWT auto-renewed every 5 minutes from `id:secret`). The description's example currently reads as imagined rather than observed. Carried forward from Pass 2 unresolved.

- `Repository layout > Monorepo with multiple published packages` — `stripe--agent-toolkit.md` shows a "MCP plus other agent-integration surfaces" pattern (npm: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`; PyPI: `stripe-agent-toolkit`) treating MCP as a peer to SDKs and Vercel-AI integrations rather than the whole product. Sharpening: MCP as one channel among several for an agent-integration toolkit. Carried forward from Pass 2 unresolved.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — every fact in this bin maps to an existing role)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

- `Server runtime > Python with FastMCP` — `the-momentum--fhir-mcp-server.md` and `thenets--ghost-mcp.md` both pin specific FastMCP 2.x versions (`2.12.3` is explicit for thenets) but operate quite differently: thenets is a thin tool-server, the-momentum embeds a full RAG pipeline (llama-index + huggingface + pinecone + sentence-transformers + pymupdf) inside the FastMCP server. The in-server-RAG specialization is large enough to warrant cross-linking from `Server runtime > Python with FastMCP` to `Domain logic and embedded intelligence > Embedded RAG / retrieval pipeline` (which already exists). Not strictly a split — more a cross-link concern. Carried forward from Pass 2 unresolved.

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Cross-corpus phrasing cleanup applied in Pass 3.** Five samples carried prose comparing themselves to the broader corpus rather than describing themselves. Pass 3 trimmed these per the methodology's "samples should describe themselves, not compare to other samples":
    - `the-momentum--fhir-mcp-server.md` — "Three transport modes (stdio / http / https) selected via env var, among the richest transport surfaces in the corpus." → trimmed to "Three transport modes (stdio / http / https) selected via env var."
    - `the-momentum--fhir-mcp-server.md` — "an in-server credential vault, unusual among MCP servers; driven by HIPAA/PHI handling concerns." → trimmed to "an in-server credential vault driven by HIPAA/PHI handling concerns."
    - `the-momentum--fhir-mcp-server.md` — "Common in data-ops projects but rare in MCP servers." → trimmed (sentence removed).
    - `the-momentum--fhir-mcp-server.md` — "non-standard module-name (matches the `voska/hass-mcp` pattern)." → trimmed to "non-standard module-name." (inline citation to another sample removed.)
    - `thenets--ghost-mcp.md` — "most MCP servers assume static creds; this one refreshes JWTs every 5 minutes." → trimmed to "refreshing them every 5 minutes."
    - `sooperset--mcp-atlassian.md` — "Both formatters present is unusual — modern projects typically pick one (`ruff format` typically replaces `black`)." → trimmed to "Both `ruff` and `black` formatters present."
    - `tumf--grafana-loki-mcp.md` — "both `ruff` and `black` present (redundant since modern `ruff format` covers most of what `black` did)." → trimmed to "both `ruff` and `black` present."

- **`thenets--ghost-mcp.md` Docker Compose for testing the upstream backend (Ghost+MySQL).** Placed under `Container artifacts > Docker-Compose backend for end-to-end tests`. The 1-star repo carries unusual dev-ergonomics investment (full Compose stack for upstream). At the role-path level there is no place for "investment level" as a signal. Not raising as a refinement, just noting the gap. Carried forward from Pass 2 unresolved.

- **`stripe--agent-toolkit.md` ships both `.claude-plugin/` and `.cursor-plugin/`.** The consolidated has `Claude Code plugin / skill wrapper > .claude-plugin/ wrapper` but no symmetric `Host integration > .cursor-plugin/ wrapper`. The sample's `.cursor-plugin/` is placed under `Host integration > Cursor`. The asymmetry is real — Claude Code wrappers have a top-level role, Cursor wrappers are inline under host integration — but no refinement proposed because the consolidated likely treats Claude Code as a deliberate first-class concern. Carried forward from Pass 2 unresolved.

- **`teaguesterling--duckdb_mcp.md` is hard to fit at all.** Runtime is "DuckDB extension," distribution is "make build from source," entry point is "SQL PRAGMA invocation," capability surface includes "user-publishable SQL templates" and "MCP-client mode (federation via ATTACH)." Most of these have paths in the consolidated (`Server runtime > DuckDB extension`, `Distribution channel > Source build with make / CMake`, `Entry point and launch > SQL PRAGMA invocation`) but they're scattered. The sample is a single coherent design (database-as-MCP-host) split across 8+ roles. Architectural unity is invisible at the role level. Not a refinement — just noting. Carried forward from Pass 2 unresolved.

- **`supabase-community--supabase-mcp.md` HTTP-first, no stdio path.** Sample exhibits HTTP/Streamable HTTP exclusively — no stdio mode documented. Most MCP servers offer stdio as a baseline; this one skips it. Placed `Transport > Streamable HTTP` only (no `stdio` sibling). The consolidated's `Transport > Selection mechanism > Implicit single mode` covers HTTP-only deployments; sample fits but the "no stdio at all" stance is rare and worth flagging at description level. Carried forward from Pass 2 unresolved.

- **`spences10--mcp-turso-cloud.md` transport never explicitly named.** README does not call out stdio; it's inferred from `npx -y` launch pattern. Placed under `Transport > stdio` per the corpus's "stdio is the default for npx-launched servers" convention; the existing `stdio` description already says "Often selected implicitly — README shows the launch command without naming the transport." No refinement needed. Carried forward from Pass 2 unresolved.

- **`spences10--mcp-turso-cloud.md` two-tier token model.** `TURSO_API_TOKEN` is org-level; the server mints per-database tokens with `TOKEN_EXPIRATION` and `TOKEN_PERMISSION`. Placed under `Authentication > Server-managed token rotation` and `Multi-tenancy > Sub-tenancy via child-credential generation`. Both paths fit cleanly; the sample is well-served by existing structure. Carried forward from Pass 2 unresolved.

- **`sooperset--mcp-atlassian.md` 72-tool surface.** Large enough to fit `Tools-heavy domain wrapper / domain-tool catalog` (20-60+ tools). Placed there. The sample lacks an explicit tool-group selector mechanism documented. The absence is marked implicitly by *not* placing the sample under `Capability gating flags (per-tool, per-category, write-mode)`; reconciler should treat absence as "no selector observed" rather than "selector exists, undocumented." Carried forward from Pass 2 unresolved.

- **`stripe--agent-toolkit.md` low extraction depth.** Many fields in original sample marked "not extracted within budget" (last commit, exact tool list, CI specifics, Dockerfile presence). Absence preserved by not placing the sample under those paths. Carried forward from Pass 2 unresolved.

- **`the-momentum--fhir-mcp-server.md` `uv_build` backend with module name `app`.** Placed under `Build and packaging > uv_build backend (Python)`. The non-standard module-name `app` rather than the package name is a recurring pattern in the consolidated; sample fits cleanly. Carried forward from Pass 2 unresolved.

## Convergence assessment

The bin is **almost converged**. All sample level-2 and level-3 headings exactly match consolidated role/path names — chain-key match verified by exhaustive comparison against the consolidated's `### ` set. Pass 3 applied seven targeted prose trims (six cross-corpus phrasing removals plus one inline citation removal) so each sample now describes itself without reaching across the corpus. No new roles needed. The Pass 2 refinement queue (five proposed new paths, nine description sharpenings, one cross-link concern) carries forward unchanged for the reconciler to integrate into the next consolidated revision. Pass 4 should not be required if the reconciler accepts (or rejects with rationale) the proposed paths and sharpenings.
