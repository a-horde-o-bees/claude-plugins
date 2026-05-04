# Depth Pass Refinements — Sample > Multi-tenancy

Per-role cross-corpus refinement proposals from inspecting every sample's content under the Multi-tenancy role. 24 paths total; 24 with supporting samples (no empty paths in this role).

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### `Sample > Multi-tenancy` (role-level description)

**What the existing description misses.** The role-level prose says "Tightly coupled to transport." The cross-corpus pull confirms this is far stronger than current prose admits — the role is essentially a **derived axis** of (Transport × Authentication). Of 102 samples:

- All 66 `Single-user / single-tenant per process` samples are stdio (or stdio-default) with static-credential auth.
- All 7 `Per-user / per-workspace via OAuth` samples are HTTP-transport servers (or hosted-remote) using OAuth 2.1.
- All 4 `Per-request tenancy by inbound credential / bearer token` samples are HTTP-only, with credentials carried per request.
- All `Per-request tenancy via OAuth token scoping` and `Per-request tenancy via middleware` and `Per-request tenancy with externalized session state` samples are HTTP-only with the corresponding upstream auth model.

The current "Tightly coupled to transport" is correct but understated. The role is *almost entirely determined* by the joint choice of transport + auth; only a few paths (Workspace-scoped sandboxing, Multi-spec composition, Mode-switched backing store) are independent of that joint axis.

**Cross-corpus evidence.** The transport→tenancy implication chain shows up in nearly every sample: stdio + static API key → single-tenant; HTTP + OAuth → per-user; HTTP + per-request bearer → per-request multi-tenant. Several samples explicitly articulate the chain — `cyanheads--perplexity-mcp-server` ("JWT/OAuth in HTTP mode enables multi-client support — a typically single-user server gains multi-client posture when the auth gate is enabled"), `getsentry--sentry-mcp` (stdio mode = single-user; hosted endpoint = per-user OAuth), `github--github-mcp-server` (same dual-posture), `stripe--agent-toolkit` (same), `supabase-community--supabase-mcp` (same).

**Sharpened text suggestion.** Replace the current single sentence with: *"Whether and how a single server instance can serve multiple users or workspaces, and what enforces the boundary. Multi-tenancy is largely a derived axis of transport × authentication: stdio + static credential almost always implies single-tenant; HTTP + OAuth or HTTP + per-request bearer enables per-user, per-workspace, or per-request tenancy. The same codebase often exhibits two postures depending on deployment — single-tenant in stdio mode, multi-tenant in hosted/HTTP mode. The independent paths (workspace sandboxing, multi-spec composition, mode-switched backing store) describe orthogonal isolation or addressing concerns rather than transport-driven multiplexing."*

### `Sample > Multi-tenancy > Single-user / single-tenant per process`

**What the existing description misses.** The current text covers "stdio + static API key" inevitability well, but a meaningful sub-pattern in the corpus is the **dual-mode codebase** — same server is single-tenant in stdio mode but switches to per-user/per-request mode under HTTP+OAuth. This isn't separate paths; it's one codebase exhibiting two tenancy postures keyed to deployment mode. Several samples have entries under both this path and `Per-user / per-workspace via OAuth` for exactly this reason: `getsentry--sentry-mcp`, `github--github-mcp-server`, `stripe--agent-toolkit`. The description should make clear that "single-tenant per process" is a deployment-mode posture, not a fundamental design constraint, in this subset.

**Cross-corpus evidence.** Quantitatively: 66 entries here vs 7 under OAuth — but 4-5 of the OAuth entries point at the same project as a single-tenant entry. Roughly 5% of "single-tenant" entries belong to dual-mode codebases. `cyanheads--perplexity-mcp-server` makes the dual-posture explicit ("Per-user single instance by default. JWT/OAuth in HTTP mode enables multi-client support").

**Sharpened text suggestion.** Append a sentence: *"For some servers, this is the stdio-mode posture of a dual-mode codebase whose HTTP/hosted deployment exhibits per-user OAuth tenancy instead — `getsentry--sentry-mcp`, `github--github-mcp-server`, `stripe--agent-toolkit`, `cyanheads--perplexity-mcp-server`. The single-tenant posture there is deployment-derived, not a fundamental design constraint."*

### `Sample > Multi-tenancy > HTTP-stateful, single-tenant`

**What the existing description misses.** Current description is correct but the two supporting samples are a weak pairing. `ahmedmustahid--postgres-mcp-server` is an HTTP server bound to a single DB connection — a clean fit. `metoro-io--mcp-golang` says "HTTP stateless request-response pattern; tenancy not explicitly documented and depends on application implementation" — that's actually closer to *N/A (library, not a runtime)* than to "HTTP stateful, single tenant" because it's an SDK, and its tenancy posture is "consumer's concern" not "single-tenant by design."

**Cross-corpus evidence.** `metoro-io--mcp-golang`'s sample under `N/A` would be more accurate. The path would then have only one supporter, but the description is genuinely about a real shape — HTTP transport with stateful sessions yet pinned to one upstream credential set per process.

**Sharpened text suggestion.** Keep the description as-is; surface the placement issue under "Mis-placed samples" below. If `metoro-io--mcp-golang` moves to N/A, this path drops to a single supporter and may merit folding into a parent category, but that's a reconciler call.

### `Sample > Multi-tenancy > Per-request tenancy by inbound credential / bearer token`

**What the existing description misses.** All four samples in this bucket exhibit the same shape — *the server holds no upstream identity; the inbound credential is the entire identity proof*. But the description currently centers on "first-party platform-as-a-service deployments where the platform's existing auth model is the source of truth." Two of four samples — `lanbaoshen--mcp-jenkins` (`x-jenkins-*` HTTP headers) and `viant--mcp` (bearer + OAuth2 discovery) — aren't first-party platform deployments, they are bring-your-own-credentials gateways. The "first-party platform" framing is too narrow.

**Cross-corpus evidence.**

- `cloudflare--mcp-server-cloudflare` — first-party platform (Cloudflare Worker, Cloudflare auth)
- `exa-labs--exa-mcp-server` — first-party platform (Exa SaaS, Exa API key)
- `lanbaoshen--mcp-jenkins` — third-party gateway pattern: server is generic, inbound headers point at any user's Jenkins instance
- `viant--mcp` — generic SDK exposing per-request bearer/OAuth, deployment-agnostic

The two cleavages — "first-party hosted" vs "generic gateway accepting per-request creds" — share a wire pattern (per-request credentials carry tenancy) but differ in deployment story. Currently bundled correctly because the *mechanism* is shared; just the description is too narrow.

**Sharpened text suggestion.** Replace second sentence: *"Same Worker (or generic HTTP server) serves any caller that authenticates; nothing in the server's state binds it to one user. Suited to multi-user shared deployments behind a load balancer. Two flavors: first-party hosted services where the operator's platform auth is the credential source (`cloudflare--mcp-server-cloudflare`, `exa-labs--exa-mcp-server`), and generic gateway servers where the inbound credentials point at an arbitrary upstream system the server itself doesn't operate (`lanbaoshen--mcp-jenkins`, `viant--mcp`)."*

### `Sample > Multi-tenancy > Connection-lifecycle as a knob`

**What the existing description misses.** The description frames this as "trade-off: persistent connections enable cross-call state but break the stateless-per-request model." That captures `ktanaka101--mcp-server-duckdb` (`--keep-connection`) and `lanbaoshen--mcp-jenkins` (session-singleton toggle) well, but `datalayer--jupyter-mcp-server` doesn't fit this framing — its `DOCUMENT_ID` env var plus `use_notebook` tool is **per-notebook switchable session within a single Jupyter connection**. That's not connection lifecycle; it's *active-target switching* within a held connection. The sample's own content already flags this: "Refinement proposed for an explicit 'per-notebook switchable session' path."

**Cross-corpus evidence.** Two samples (DuckDB, Jenkins) describe connection persistence; one (Jupyter) describes target switching. Different mechanism, same role.

**Sharpened text suggestion.** Either:
- Keep description as-is; surface under "Mis-placed samples" and let reconciler decide whether to split or move `datalayer--jupyter-mcp-server`, OR
- Broaden description to: *"Servers expose session-state knobs trading per-call independence for cross-call state. Two flavors: connection persistence (`--keep-connection`, session-singleton mode in `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`) and active-target switching within a held connection (`use_notebook` tool with `DOCUMENT_ID` in `datalayer--jupyter-mcp-server`). Trade-off: persistent connections or held targets enable cross-call state (TEMP tables, current notebook) but break the stateless-per-request model and complicate multi-tenant safety."*

The broader framing is more honest to the corpus.

### `Sample > Multi-tenancy > N/A (library, not a runtime)`

**What the existing description misses.** The description correctly captures SDKs (`mcpr`, `fastmcp`, `kotlin-sdk`, `viant`). But `pathintegral-institute--mcp.science` is in this bucket and it's *not* an SDK — it's a "monorepo collection of independent servers." Each sub-server is single-user. The N/A applies because there's no shared runtime to multiplex tenants across, but the reasoning is structurally different from "SDK ships scaffolding."

**Cross-corpus evidence.** 5 samples in this bucket: 4 SDKs + 1 monorepo. The monorepo case is genuinely a separate shape — the project ships runnables, but each is single-user, and tenancy across the monorepo isn't a coherent concept.

**Sharpened text suggestion.** Append: *"Also covers monorepos shipping multiple independent servers (e.g., `pathintegral-institute--mcp.science`) where each sub-server is single-user and there is no shared runtime to multiplex across."*

### `Sample > Multi-tenancy > Workspace-scoped sandboxing within a single tenant`

**What the existing description misses.** The current description is precise and accurate. The three supporting samples (`cyanheads--git-mcp-server`, `jbeno--cursor-notebook-mcp`, `normaltusker--kotlin-mcp-server`) all share workspace-root constraint via env var (`BASE_DIR`, `--allow-root`, `WORKSPACE_PATH`). One observation worth folding in: only `cyanheads--git-mcp-server` exhibits the per-session subdirectory layer — the description currently mentions it as if common. From the evidence, it's a single-sample sub-pattern.

**Sharpened text suggestion.** Adjust the description so the "per-session subdirectory tracking" detail is presented as a single-sample extension rather than a common pattern: *"Server constrains per-session operations to a configured base directory or working tree (`os.path.realpath` canonicalizing paths against an allow-listed root, `BASE_DIR`, `WORKSPACE_PATH`, `--allow-root`). A path-traversal defense that lets the server operate on local files while bounding the blast radius. Tenancy is still single-user, but file-system access is segmented per session within that user's allowed space. `cyanheads--git-mcp-server` extends this with per-session subdirectory tracking — same server process serves multiple stdio sessions each scoped to their own subdir within the allowed root. Appropriate when the underlying tool (git, file ops) would otherwise be free to roam the whole filesystem and the operator wants explicit boundaries — common for IDE-integrated developer tools where workspace = project."*

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### `Sample > Multi-tenancy > Single-user / single-tenant per process` — Dual-mode codebases

Sub-pattern: same project exhibits this path in stdio mode AND a per-user/per-request path in HTTP/hosted mode. ~5 samples (`getsentry--sentry-mcp`, `github--github-mcp-server`, `stripe--agent-toolkit`, `supabase-community--supabase-mcp`, `cyanheads--perplexity-mcp-server`). **Fold into description (sharpening above).** Not a split — single-tenant per process is genuinely the stdio posture of these codebases; the HTTP posture is captured under the OAuth/per-request paths. The reconciler should consider whether dual-mode codebases warrant a top-level cross-cutting note in the role-level description.

### `Sample > Multi-tenancy > Single-user / single-tenant per process` — Multi-source-but-single-identity

Sub-pattern: server fronts multiple upstream APIs/databases simultaneously but holds one identity. Examples: `chroma-core--chroma-mcp` (multi-provider via env-var prefix), `openags--paper-search-mcp` ("per-provider credentials applied globally"), `pragmar--mcp-server-webcrawl` ("one data source per launch"). These are single-tenant in the user-axis but multi-source in the upstream axis. **Adjacent to `Multi-spec / multi-source composition`** which captures the more explicit form. Fold lightly into description: a parenthetical noting that "single-tenant" is user-axis tenancy and multi-source single-identity servers still belong here.

### `Sample > Multi-tenancy > Per-request tenancy by inbound credential / bearer token` — First-party-hosted vs generic-gateway sub-axis

Sub-pattern: 2 first-party (Cloudflare, Exa) vs 2 generic-gateway (Jenkins, viant). Same wire mechanism, different deployment story. **Fold into description (sharpening above).** Not large enough to warrant split.

### `Sample > Multi-tenancy > Connection-lifecycle as a knob` — Connection persistence vs active-target switching

Sub-pattern: 2 connection-persistence (DuckDB, Jenkins), 1 active-target-switching (Jupyter `use_notebook`). Different mechanism (persistence vs switching) but related concern (session-state lifecycle). **Either fold into broadened description OR propose split** (see Mis-placed samples).

## Proposed bucket merges

None proposed. The single-sample paths represent genuine distinct mechanisms — Bot-scoped, Externally-managed sessions via header, Per-call tenancy argument, Per-request tenancy via OAuth token scoping, Per-request tenancy via middleware, Per-request tenancy with externalized session state, Per-session state via session registration, Per-workspace tenant via upstream token, Stateless HTTP for shared deployment, Sub-tenancy via child-credential generation, Tag-based resource scoping. Each names a discriminating mechanism that doesn't map onto another.

That said, the reconciler may want to consider whether a parent grouping like `Per-request tenancy {by bearer / via OAuth scoping / via middleware / via URL parameter / with externalized state}` would aid scanability — the corpus has ~10 supporters across these subdivisions and they share a wire pattern (each request carries tenancy). Not a merge; an organizational grouping. Defer to reconciler.

## Proposed bucket splits

### Possibly split `Connection-lifecycle as a knob`

**Why split.** As noted in description sharpening, the path bundles two mechanisms:
- Connection persistence (`--keep-connection`, session-singleton): `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`
- Active-target switching (`use_notebook` + `DOCUMENT_ID`): `datalayer--jupyter-mcp-server`

**Into what.** Either:
- Keep one path with broadened description (recommended — see sharpening above).
- Split into `Connection persistence as a knob` (2 samples) and `Active-target switching within held connection` (1 sample). The 1-sample new path may be too small to justify; the sample explicitly self-flagged ("Refinement proposed for an explicit 'per-notebook switchable session' path") which is evidence of intent but not weight.

**Recommendation.** Broaden description rather than split. 1-sample paths are common in this role's tail; another doesn't meaningfully add information.

## Mis-placed samples

### `metoro-io--mcp-golang` currently under `HTTP-stateful, single-tenant` better fits `N/A (library, not a runtime)`

**Evidence.** The sample's own content says "tenancy not explicitly documented and depends on application implementation." That's the canonical signal for N/A library posture. The sample is an SDK (`metoro-io/mcp-golang`), not a server runtime. The `HTTP-stateful, single-tenant` path is for server processes that hold one credential set across HTTP sessions (which `ahmedmustahid--postgres-mcp-server` exemplifies). An SDK whose tenancy is "consumer's concern" belongs alongside `mark3labs/mcp-go`, `jlowin/fastmcp`, and `viant/mcp` (the latter also has a per-request entry).

### `datalayer--jupyter-mcp-server` currently under `Connection-lifecycle as a knob` — placement defensible but mechanism diverges

**Evidence.** Sample content: "`DOCUMENT_ID` env var plus `use_notebook` tool switches the active notebook target at runtime — per-notebook switchable session within a single Jupyter connection." This is target switching, not connection lifecycle. The sample author noted "Refinement proposed for an explicit 'per-notebook switchable session' path." If the path description is broadened (sharpening above), this stays. If the path is kept narrow (connection-persistence only), the sample is mis-placed and there's no clean home for it — possibly fold into `Single connection per server instance` with annotation about target switching.

**Recommendation.** Broaden the path description rather than move the sample.

### `metoro-io--mcp-golang` move recommendation

Move `metoro-io--mcp-golang` from `HTTP-stateful, single-tenant` to `N/A (library, not a runtime)`. This drops `HTTP-stateful, single-tenant` to 1 sample. The path is still useful as a real shape (`ahmedmustahid--postgres-mcp-server` is genuinely a single-tenant HTTP server), so the reconciler may keep the path with one supporter.

### No other genuine mis-placements found.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Multi-tenancy is a derived axis of (Transport × Authentication)

The single most important cross-corpus pattern. The role's tree barely has any structure independent of those two roles — every per-request/per-user path is HTTP-mode + OAuth-or-bearer; every single-tenant path is stdio + static credential. Out of 24 paths, only 5-6 are genuinely transport-and-auth-independent (Workspace-scoped sandboxing, Multi-spec composition, Mode-switched backing store, Bot-scoped, Tag-based resource scoping, N/A library). The remaining 18-19 paths are deterministic implications of (Transport, Auth).

**Implication.** The role's value isn't in surfacing a tenancy choice space — it's in surfacing the *consequence* of a transport+auth choice. The role-level description should make the directionality explicit (sharpening above proposes this). Reconciler should consider whether the role merits a more compact tree organized around the two structural axes that drive it, or whether the current flat list is the right granularity for descriptive cross-referencing.

### Pure path-style multi-tenancy is rare

Only 4 samples (`Per-request tenancy by inbound credential / bearer token`) describe the cleanest "any user, one server" shape — the deployment that downstream MCP-as-a-service platforms presumably want. Even hosted-vendor endpoints (Sentry, GitHub, Stripe, Supabase, Context7) reach this through OAuth, not through pure header-based credentials. The MCP corpus is overwhelmingly single-tenant; multi-tenant production deployments are a minority pattern across the 102 samples.

### "First-class tenancy in tool signatures" is a single-sample anomaly

`sajal2692--mcp-weaviate` is the only server in the corpus where tenancy is a tool argument (`search_in_tenant(tenant, query)`). Elsewhere, tenancy lives at the credential/transport layer. The Weaviate pattern is structurally distinct because the upstream (Weaviate vector DB) is itself multi-tenant per-collection — the server pushes that into the MCP surface rather than collapsing it into a per-process tenant. This is appropriate when the upstream is multi-tenant by design and the operator wants one server to span tenants. Not a sub-axis of any existing path; correctly placed as its own.

### `Stateless HTTP for shared deployment` and `Per-request tenancy by inbound credential / bearer token` are complementary, not competing

`utensils--mcp-nixos` (Stateless HTTP) is single-tenant; the upstream is public so "multi-user-capable" doesn't mean multi-tenant. Pure stateless-HTTP without per-request credentials gives you horizontal scaling but not tenant isolation; pure per-request credentials without stateless-HTTP gives you tenant isolation but not horizontal scaling. The full multi-tenant cloud-deployable shape combines both. Worth noting that no single sample exhibits the explicit combination — the corpus has the two halves separately but not the full pattern.

### "Workspace as tenant" is conceptually distinct from "user as tenant"

Three paths use "workspace" as the boundary unit: `Per-user / per-workspace via OAuth` (workspace-as-OAuth-scope), `Per-workspace tenant via upstream token` (workspace=upstream account), `Workspace-scoped sandboxing within a single tenant` (workspace=filesystem subdirectory). These are three different uses of the word "workspace": OAuth scope (Slack), upstream account (Slack again, different angle), local filesystem (cyanheads-git, cursor-notebook). The role-level description doesn't disambiguate. Worth flagging that "workspace" in MCP servers means at least three different things depending on context. Not a refinement to act on; a vocabulary observation.

### Adoption-table tail is dominated by single-sample paths

13 of 24 paths have only 1 supporter. That's the consequence of being a derived axis: the rare combinations of transport+auth produce rare tenancy shapes, each named once. The reconciler may wish to consider whether this many singleton paths is sustainable, or whether some should be folded into nearby paths with annotation. From a research-value standpoint, the singletons document genuine real-world variation; from a tree-organization standpoint, they bloat the table. Trade-off; defer to reconciler.
