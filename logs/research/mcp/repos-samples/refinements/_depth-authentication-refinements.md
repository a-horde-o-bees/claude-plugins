# Depth Pass Refinements — Sample > Authentication

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role. 39 paths total; 38 with supporting samples (one path — `Delegated to upstream source` — has 0 samples). Total sample evidence consumed: ~22 KB across 132 sample sections (some samples appear under multiple paths).

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### Sample > Authentication (role-level)

The role description ("How the server verifies callers (when relevant) and how upstream credentials reach it. Where the trust boundary sits and what proves identity at it.") is accurate but doesn't surface the **transport-conditional structure** that becomes obvious only when paths are stacked: at least six paths (`Bearer token over HTTP/SSE`, `JWT`, `OAuth 2.x with issuer + JWKS`, `OAuth 2.1 / OIDC delegated`, `Per-request HTTP-header credentials`, `Per-request bearer token`) exist *only* on HTTP/SSE transport. Stdio servers in the corpus do not adopt these — auth on stdio is universally either `None / implicit` or upstream-credential delivery (static keys, connection strings, cloud chains). This is the dominant axis the role's tree implicitly encodes.

Sharpened text suggestion: extend the role description with one sentence — "Many paths apply only on HTTP/SSE transport — stdio's process boundary substitutes for caller authentication, so MCP-caller auth (JWT, OAuth 2.x JWKS, Bearer over HTTP, OAuth 2.1 OIDC, per-request header creds) is HTTP-mode-only across the corpus. Upstream-credential paths (static keys, connection strings, cloud chains) apply regardless of transport. Several samples expose both, with the MCP-caller layer engaged conditionally on transport selection."

### Sample > Authentication > None / implicit (local-resource gating)

The existing description correctly enumerates the cases (public upstream, local files, browser-automation, locally-running app, library N/A, path-restriction gating) but presents them as a flat list. Cross-corpus inspection of all 28 samples reveals four distinct sub-clusters with different design rationales — worth surfacing:

- **Public unauthenticated upstream** (9 samples): `JackKuo666--PubMed-MCP-Server`, `awslabs--aws-documentation-mcp-server`, `blazickjp--arxiv-mcp-server`, `idosal--git-mcp`, `isaaccorley--planetary-computer-mcp`, `utensils--mcp-nixos`, `microsoft--playwright-mcp`, `executeautomation--mcp-playwright`, `twolven--mcp-server-puppeteer-py`. Server fronts an upstream that doesn't require credentials (PubMed, arXiv, NixOS public endpoints, public web for browser automation).
- **Local file or data only** (10 samples): `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`, `pragmar--mcp-server-webcrawl`, `rust-mcp-stack--rust-mcp-filesystem`, `shibuiwilliam--mcp-server-scikit-learn`, `mahdin75--gis-mcp`. Operates on user-supplied local files; trust derived from local file-system access semantics.
- **Process-boundary trust** (5 samples): `ClickHouse--mcp-clickhouse` (stdio mode only), `ckreiling--mcp-server-docker` (Docker socket via `from_env()`), `bhauman--clojure-mcp` (REPL-resident), `hugoduncan--mcp-clj`, `cyanheads--git-mcp-server` (`AUTH_MODE=none` dev default). Trust derives from "the host launched this process under the user's identity."
- **Path-restriction gating** (4 samples, often overlapping above): `modelcontextprotocol--servers` (filesystem allowlist, robots.txt for fetch), `jbeno--cursor-notebook-mcp` (`--allow-root`), `microsoft--playwright-mcp` ("not a security boundary" stated posture), `rust-mcp-stack--rust-mcp-filesystem` (read-only restriction).
- **Library / framework — N/A** (2 samples): `jlowin--fastmcp`, `conikeec--mcpr` — auth is consumer's responsibility, not the framework's.

Sharpened text suggestion: keep the existing prose; add an explicit sub-axis paragraph: "Five sub-flavors observed: public unauthenticated upstream (PubMed, arXiv, public web), local file / data only (SQLite/DuckDB/PDF/CSV/filesystem), process-boundary trust (stdio-mode default, Docker socket, REPL-resident), path-restriction gating (filesystem allowlist, `--allow-root`, robots.txt), and library/framework N/A (consumer wires auth). The `microsoft--playwright-mcp` README's `"MCP is not a security boundary"` framing is the explicit-design-posture variant; most samples leave the trust model implicit."

### Sample > Authentication > Static API key / token via env var

Three issues with the existing description:

1. **`EARTHDATA_PASSWORD` is mis-listed.** The description bundles it with API tokens, but `datalayer--earthdata-mcp-server` actually uses `EARTHDATA_USERNAME` + `EARTHDATA_PASSWORD` handed to the `earthaccess` library — username+password supplied to a vendor-supplied SDK that internally handles the auth dance. Shape is closer to *Service-specific credentials via third-party SDK* than to a static API key. Surface as either a mis-placement (move the sample) or scrub the example from the description list.
2. **"Provider-prefixed convention (`CHROMA_<PROVIDER>_API_KEY`)"** generalizes from a single sample (`chroma-core--chroma-mcp`); no other sample uses provider-prefixed env vars for static keys. Drop the universalizing framing.
3. **`MCP_TOKEN` example** belongs to the layered-auth pattern (`datalayer--jupyter-mcp-server`), not the raw single-key pattern. The static-key path captures the upstream credential side; MCP_TOKEN is the protocol-level token introduced in v1.x as a *separate* concept.

Cross-corpus evidence: 31 samples; the dominant pattern is one env var → one credential → one upstream service. Variations:

- **Single key per upstream** (most samples): `DEEPL_AUTH_KEY`, `PERPLEXITY_API_KEY`, `FIGMA_API_KEY`, `EXA_API_KEY`, etc.
- **Key + secret pair** (3+ samples): `ALPACA_API_KEY` + `ALPACA_SECRET_KEY`, Atlassian email + token (`sooperset`), `--username` + `HUB_PAT_TOKEN` (`docker--hub-mcp`).
- **Multiple credential delivery channels for one server**: `cyanheads--perplexity-mcp-server`, `DaInfernalCoder--perplexity-mcp` (env / CLI / `.env`), `DiversioTeam--clickup-mcp` (`set-api-key` subcommand persisted via `platformdirs` *or* env var), `getsentry--sentry-mcp` (env or `--access-token`), `motherduckdb` (env or `--motherduck-token`), `tumf--grafana-loki-mcp` (env or `-k`).
- **Hosted-endpoint URL-parameter delivery**: `exa-labs--exa-mcp-server` notes "also supplied via URL parameter for the hosted endpoint" — env var for stdio, URL param for hosted. Cross-cutting with hosted-deployment paths.
- **Deployment-flavor split (stdio vs hosted)**: `getsentry--sentry-mcp`, `github--github-mcp-server`, `stripe--agent-toolkit`, `makenotion--notion-mcp-server`, `sooperset--mcp-atlassian` all show this duality (PAT for stdio, OAuth/Bearer for hosted) — the static-key path captures only the stdio leg of these duo-paths.

Sharpened text suggestion: drop the `MCP_TOKEN` and `EARTHDATA_PASSWORD` examples from the env-var enumeration. Drop the "provider-prefixed convention" universalizing — call it out as a single-sample pattern under chroma-core with a brief note ("one sample uses a provider-prefixed convention `CHROMA_<PROVIDER>_API_KEY` to give a uniform surface across multiple embedding back-ends — single instance"). Add: "Several samples expose multiple delivery channels for the same key (env, CLI flag, dotenv, persisted config via `platformdirs`); priority is usually CLI > env > file when documented. For servers with both stdio and hosted-endpoint deployments (Sentry, GitHub, Stripe, Notion, Atlassian), this path captures the stdio leg only — the hosted leg lives under OAuth 2.1 / OIDC."

### Sample > Authentication > Database connection string

Existing description constrains the URI shape ("postgres://user:pass@host:port/db-style URL or MongoDB URI"), but cross-corpus evidence shows the path is broader:

- True connection-string form: `crystaldba--postgres-mcp` (`DATABASE_URI`), `HenkDz--postgresql-mcp-server` (`POSTGRES_CONNECTION_STRING`), `mongodb-js--mongodb-mcp-server` (`MDB_MCP_CONNECTION_STRING`), `redis--mcp-redis` (URI form supported).
- Separate env-var pair (not a URI): `ClickHouse--mcp-clickhouse` (`CLICKHOUSE_HOST` + `CLICKHOUSE_USER` + `CLICKHOUSE_PASSWORD`), `designcomputer--mysql_mcp_server` (separate env vars), `elastic--mcp-server-elasticsearch` (`ES_USERNAME` + `ES_PASSWORD`), `ahmedmustahid--postgres-mcp-server` ("env vars (`POSTGRES_*`) or as a connection URI" — both shapes accepted).

The path is really "database-native auth (URI or env-var pair); MCP server is a relay" — the URI shape is a delivery mechanism, not the defining property. The path-name "Database connection string" is slightly misleading because half the samples deliver the credentials as separate env vars, not as a URI string.

Sharpened text suggestion: revise the opening to "Database-native auth — credentials embedded either in a URI (`postgres://user:pass@host:port/db`, `mongodb://...`) or in separate env vars (`POSTGRES_USER` + `POSTGRES_PASSWORD`, `ES_USERNAME` + `ES_PASSWORD`, `CLICKHOUSE_USER` + `CLICKHOUSE_PASSWORD`). Some servers accept both delivery shapes (`ahmedmustahid` postgres). Authentication is whatever the database speaks; the MCP server is a relay. Limited to one credential set per process. Read-only enforcement, when present, lives at the MCP layer (e.g., pglast SQL parsing in `crystaldba--postgres-mcp`) rather than at the DB privilege layer."

The "Database connection string" path-name itself could be renamed to "Database-native auth (URI or env-var pair)" — but that's a structural change beyond the depth-pass charter; surfacing as a candidate for the reconciler.

### Sample > Authentication > OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)

Existing description is dense. Cross-corpus inspection of all 5 samples shows it correctly captures most of the pattern, but two sub-claims need calibration:

1. **"Two modes observed: global resource protection ... and fine-grained per-tool/resource control (still flagged experimental)"** — only `viant--mcp` exhibits the global-vs-per-tool split. The other 4 samples (`awslabs--aws-api-mcp-server`, `cyanheads--git-mcp-server`, `cyanheads--perplexity-mcp-server`, `rohitg00--kubectl-mcp-server`) just describe a single OAuth-validation mode. Frame the dual-mode observation as "one sample (`viant--mcp`)" rather than "two modes observed."
2. **"Often appears as one branch of a tri-modal switch (`AUTH_MODE=none|jwt|oauth`)"** — supported strongly by `cyanheads--git-mcp-server` (`none|jwt|oauth`) and visibly present in `cyanheads--perplexity-mcp-server` (JWT and OAuth both gated by HTTP transport, both opt-in atop upstream API key). `awslabs--aws-api-mcp-server` shows a bi-modal switch (none vs OAuth, no JWT). Three of five samples have a switch; "often" is fair.
3. **Client-side auto-acquisition (RFC 9728)** — currently described in this path's prose but the actual sample (`viant--mcp` re. RFC 9728 / 401 retry) is placed under the OAuth 2.1 / OIDC path, not here. Cross-reference rather than describe in two places.

Sharpened text suggestion: keep the description but soften "Two modes observed" → "One sample (`viant--mcp`) splits this into global vs per-tool/resource enforcement (per-tool flagged experimental)." Move the RFC 9728 / client-side auto-acquisition prose to the OAuth 2.1 path entirely (where its sole supporting sample sits) — leave a one-line cross-reference here.

### Sample > Authentication > OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

Existing description strongly captures the pattern but has two over-generalizations from single samples:

1. **"Local development typically requires a tunneling tool (ngrok)"** — only `duolingo--slack-mcp` explicitly mentions ngrok. The "typically" framing universalizes from one sample. The dev-loop friction is real but the specific tool is not corpus-wide.
2. **"Workspace admin approval often required"** — supported by `slackapi--slack-mcp-plugin` only. "Often" doesn't fit 1/9.

Cross-corpus evidence on what *is* universal:

- Browser-redirect flow → all 9 samples
- Forces HTTP transport → 9/9 (stdio is structurally incompatible)
- Per-user identity / multi-tenancy → 9/9
- Hosted-endpoint deployments are the majority context (mcp.sentry.dev, mcp.stripe.com, hosted GitHub, hosted Supabase, etc.) — 7/9 explicitly hosted; only `duolingo--slack-mcp` and `viant--mcp` describe the flow without a vendor-hosted endpoint context.
- VS Code 1.101+ native OAuth handling explicitly noted by `github--github-mcp-server` and `supabase-community--supabase-mcp` (2 samples).

Sharpened text suggestion: rewrite "Local development typically requires a tunneling tool (ngrok) — the dev-loop friction is a paired cost distinct from the production deployment cost, surfaced enough that some authors document the tunneling requirement explicitly." → "Local development requires the OAuth callback URL to be reachable, which one sample (`duolingo--slack-mcp`) explicitly documents via ngrok. The dev-loop friction is a paired cost distinct from the production deployment cost." Soften "Workspace admin approval often required" → "Workspace admin approval may be required when the upstream service's permission model is workspace-scoped (`slackapi--slack-mcp-plugin`)." Strengthen "Hosts with native MCP OAuth support (e.g., VS Code 1.101+) handle the flow transparently" with sample attribution.

### Sample > Authentication > Service-account credential pair to cloud API

Path description currently says "MongoDB Atlas, AWS; ... Server may auto-provision short-lived database users (e.g., 4-hour TTL)." Cross-corpus evidence: only one sample (`mongodb-js--mongodb-mcp-server`). The "AWS" example is unsupported — no AWS sample is placed here (AWS samples land under *Cloud-native identity / credential chain*). The 4-hour TTL detail is real for MongoDB but is captured in the sample's *Operational concerns* role, not its Authentication role section. The current description is over-generalized from one sample.

Sharpened text suggestion: drop "AWS" from the example list. Leave the TTL note since it accurately reflects the sample's documented behavior, but mark it as the MongoDB-specific operational layer atop the credential pair.

### Sample > Authentication > Bearer token over HTTP/SSE

Existing description is solid for the corpus. Two samples (`ClickHouse--mcp-clickhouse`, `makenotion--notion-mcp-server`); the dev-mode override flag (`*_AUTH_DISABLED=true`) the description names is exclusive to ClickHouse. Notion just accepts the bearer header. The "either a coarse 'is this a known client' check, or a headless alternative to interactive OAuth" framing is fair across both.

No major sharpening needed; consider attributing the dev-mode override flag pattern explicitly to ClickHouse so readers don't expect it elsewhere.

### Sample > Authentication > Cloud-native identity / credential chain

Description is accurate but two angles surface from cross-corpus inspection:

- **AWS dominates** — 5 of 7 samples are AWS (`awslabs--aws-api-mcp-server`, `awslabs--bedrock-kb-retrieval-mcp-server`, `awslabs--mcp`, `baryhuang--mcp-server-aws-resources-python`, `motherduckdb--mcp-server-motherduck` for S3 access). Two are non-AWS: `googleapis--mcp-toolbox` (Google ADC) and `redis--mcp-redis` (Azure EntraID).
- **`redis--mcp-redis` is dual-placed** — Cloud-native identity chain (Azure EntraID with three sub-flows) + Database connection string (Redis ACL via username/password). This is a legitimate dual placement: cloud-native is the alternative path *atop* the standard ACL credential. The current description's "Co-exists with standard auth (e.g., username/password ACL) as an alternative path" line was clearly written with redis in mind.

No sharpening proposed beyond a minor attribution note: the three Azure EntraID sub-flows are exclusive to `redis--mcp-redis`; the AWS chain enumeration covers the 5 AWS samples.

### Sample > Authentication > Optional external LLM API keys

The path-name says "external LLM API keys" but only 1 of 3 samples (`bhauman--clojure-mcp`) actually fits — that sample explicitly names Anthropic, OpenAI, Google Gemini for agent-augmented tools. The other two:

- `mahdin75--gis-mcp` — "Downstream provider credentials (e.g., Copernicus cdsapi) are dataset-specific and optional per data source." Copernicus is a satellite/dataset API, not an LLM.
- `openags--paper-search-mcp` — "Provider-side key surface includes free-and-paid mixes (Crossref free, IEEE/ACM paid)." Academic-paper providers, not LLMs.

The path is currently a misnomer: the actual unifying property across the 3 samples is "optional per-source credentials for a non-required upstream — server still works without the key." That's the *Per-source independent API keys with graceful degradation* pattern at smaller scale (1-3 providers vs 21 in `mukul975--cve-mcp-server`).

This may be a candidate for either a path rename ("Optional auxiliary upstream API keys" or "Optional per-feature external API keys") or for merging into *Per-source independent API keys with graceful degradation* with a note on scale. See also the mis-placements section below.

Sharpened text suggestion: rename the path to "Optional auxiliary upstream API keys" or fold into the per-source bucket. If kept as-is, restrict scope to LLM-keys-specifically and move `mahdin75--gis-mcp` and `openags--paper-search-mcp` to the per-source bucket.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### Sample > Authentication > None / implicit (local-resource gating) — five sub-flavors

See Description sharpenings above. Sub-flavors visible only at full role visibility: public unauthenticated upstream (9 samples), local file/data only (10 samples), process-boundary trust (5 samples), path-restriction gating (4 samples, overlapping), library/framework N/A (2 samples). Recommend folding into description as an explicit sub-axis paragraph. Splitting into separate paths would explode a path with strong cohesion ("the server has no auth layer of its own") into five thin paths; fold rather than split.

### Sample > Authentication > Static API key / token via env var — multi-channel delivery sub-axis

5+ samples (`cyanheads--perplexity-mcp-server`, `DaInfernalCoder--perplexity-mcp`, `DiversioTeam--clickup-mcp`, `getsentry--sentry-mcp`, `motherduckdb--mcp-server-motherduck`, `tumf--grafana-loki-mcp`) explicitly support multiple credential delivery channels for the same key (env, CLI flag, dotenv, persisted config). The current description mentions "credential-resolution priority chain (CLI > env > file)" but doesn't pull this out as a recurrent characteristic. Fold into description as an observed sub-axis.

### Sample > Authentication > Static API key — deployment-flavor sub-axis (stdio + hosted dual)

5+ samples (`getsentry--sentry-mcp`, `github--github-mcp-server`, `stripe--agent-toolkit`, `makenotion--notion-mcp-server`, `sooperset--mcp-atlassian`) ship with both a stdio leg (PAT under static key) and a hosted leg (OAuth 2.1 / Bearer over HTTP). The two legs are described under separate paths; cross-corpus visibility makes the dual-leg pattern obvious. Fold a cross-reference note into the static-key description ("for servers also offering a hosted-endpoint deployment, the OAuth 2.1 / OIDC leg appears as a sibling path on the same sample").

### Sample > Authentication > AUTH_MODE switch sub-axis (cross-path)

A recurrent cross-path pattern: 3 samples expose a multi-mode auth-selector switch where the same server can be configured for several MCP-caller-auth modes — `cyanheads--git-mcp-server` (`AUTH_MODE=none|jwt|oauth`), `cyanheads--perplexity-mcp-server` (similar tri-modal), `awslabs--aws-api-mcp-server` (bi-modal: none|OAuth). Currently visible only by stacking `None / implicit`, `JWT`, and `OAuth 2.x JWKS` placements for these samples. Distinct from `Multi-method selector` (which is upstream-side: pick basic/OAuth/API-key for the upstream, e.g., `echelon-ai-labs--servicenow-mcp`'s `SERVICENOW_AUTH_TYPE`). Sample count too low (3) to justify a new path; consider a one-line cross-corpus note in the role description.

### Sample > Authentication > Application-delegated (SDK provides nothing) — SDK-only path

All 3 samples under this path are SDK projects, not server projects (`mark3labs--mcp-go`, `metoro-io--mcp-golang`, `modelcontextprotocol--kotlin-sdk`). The "the SDK exposes session-registration hooks but does not bundle an auth mechanism — applications wire their own at the transport layer" framing implicitly identifies the path as SDK-only. Worth surfacing in description: "This path applies exclusively to SDK/library samples that ship hooks but no opinion on auth; consumer-server samples never land here."

### Sample > Authentication > Per-source independent API keys with graceful degradation — scale variance

4 samples span a wide range: `mukul975--cve-mcp-server` (21 independent keys), `openags--paper-search-mcp` (multiple academic providers, mixed free/paid), `chroma-core--chroma-mcp` (3 embedding providers in core deps), `sajal2692--mcp-weaviate` (2 embedding providers — borderline; "graceful degradation" is degenerate at 2). The path covers a true-aggregator pattern (CVE: 21 sources) and thin-aggregator patterns (Weaviate: 1 optional). Fold into description: "scale ranges from 2-provider optional (Weaviate Cohere fallback) to 21-source aggregators (CVE intelligence); the unifying property is per-source independence with graceful degradation when keys are absent."

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

### Optional external LLM API keys + Per-source independent API keys with graceful degradation

Same underlying mechanism — optional per-source upstream credentials with graceful degradation. The "LLM" qualifier is honored by only 1 of 3 samples in the LLM path (`bhauman--clojure-mcp`); the other two (`mahdin75--gis-mcp`, `openags--paper-search-mcp`) describe non-LLM provider keys that fit the per-source path more naturally. If merged, the canonical bucket would be **"Optional per-source external API keys (graceful degradation)"** — covering 7 samples, capturing both "many providers, some optional" (CVE 21-source, weaviate 2) and "single optional auxiliary upstream" (LLM keys for agent-augmented tools).

If not merged, recommend renaming the LLM-named path to drop "LLM" — the path's actual property is "the upstream is optional," not "the upstream is an LLM."

Surfacing both options for the reconciler to weigh.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None proposed at structural-split severity. The candidate sub-axes surfaced above (None / implicit five sub-flavors, Static API key multi-channel) all have strong cohesion at the parent level — splitting would proliferate thin paths without gaining classification crispness. Fold-into-description is the right level of intervention given Pass 3 convergence.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

### `mahdin75--gis-mcp.md`

Currently under: `Optional external LLM API keys` (and also `None / implicit (local-resource gating)`)
Better fits: `Per-source independent API keys with graceful degradation`

Evidence: the sample's section under this path says "Downstream provider credentials (e.g., Copernicus cdsapi) are dataset-specific and optional per data source." Copernicus / CDS are satellite-dataset APIs, not LLMs. The "optional per data source" framing is the per-source independent-keys pattern at smaller scale. The "LLM" label fits zero of this sample's documented credentials.

### `openags--paper-search-mcp.md`

Currently under: `Optional external LLM API keys` (and also `Per-source independent API keys with graceful degradation`)
Better fits: drop the LLM placement; keep only the per-source placement

Evidence: the LLM-path section reads "Provider-side key surface includes free-and-paid mixes (Crossref free, IEEE/ACM paid) — keys are independent per upstream." Crossref / IEEE / ACM are academic-paper providers, not LLMs. The sample is already correctly placed under per-source independent keys; the LLM placement is redundant and misleading.

### `datalayer--earthdata-mcp-server.md` — soft mis-placement

Currently under: `Static API key / token via env var`
Possibly better fits: `Service-specific credentials via third-party SDK`

Evidence: the sample uses `EARTHDATA_USERNAME` + `EARTHDATA_PASSWORD` (not a token; a username/password pair) handed to `earthaccess` (the official NASA-auth wrapper library). "Delegates the auth dance to a vendor-supplied client." This shape — credentials handed to a community/vendor SDK that owns the upstream auth flow — is exactly the *Service-specific credentials via third-party SDK* description, where `reminia--zendesk-mcp-server` currently sits as the only sample. Reconciler decision: move to the SDK path, or keep here with a soft note that the credential shape (user+password) is atypical for this path. Surfacing because the per-bin lens couldn't see this — the SDK path has 1 sample and earthdata's SDK-delegation shape was lost in the 31-sample static-key bucket.

### `sajal2692--mcp-weaviate.md` — degenerate "graceful degradation"

Currently under: `Static API key / token via env var` AND `Per-source independent API keys with graceful degradation`
Issue: the per-source placement is borderline — only 2 providers (OpenAI required, Cohere optional). "Graceful degradation" with one fallback isn't really the per-source-aggregator pattern that defines the path (CVE has 21, paper-search has many).

Not strictly mis-placed; flagging for the reconciler in case the per-source path is rescoped to require N≥3 sources.

### Note on `normaltusker--kotlin-mcp-server.md`

Currently under: `Multi-scheme client auth (API key / OAuth / JWT / Basic / Bearer)`. The sample's text says "Multiple external API authentication schemes supported — API Keys, OAuth 2.0, JWT tokens, Basic HTTP, Bearer tokens. Server-side rate limiting, circuit breaker, and audit logging layered on top." The phrase "external API authentication schemes" is ambiguous — it could mean schemes the server uses to talk to upstream APIs (which would put it under *Multi-scheme upstream auth*), or schemes the server accepts from MCP clients (which is the current placement). The "rate limiting, circuit breaker, and audit logging" language is the cleanest signal — those are server-side ingress controls, fitting the client-auth interpretation. Probably correctly placed; surfacing because the cross-corpus comparison made the ambiguity visible.

### Possible missing placement: `alexei-led--k8s-mcp-server.md` under "Delegated to upstream toolchain credentials"

`alexei-led--k8s-mcp-server` is currently under `Mounted file credentials` only. The other kubectl-class samples (`feiskyer--mcp-kubernetes-server`, `rohitg00--kubectl-mcp-server`) carry both `Mounted file credentials` and `Delegated to upstream toolchain credentials`. The alexei-led sample wraps kubectl-class operations against a kubeconfig — the same dual-angle (delivery mechanism: file mount; abstraction level: delegation) should apply. The sample's content under `Mounted file credentials` describes "kubeconfig credentials inherited from a mounted file; cloud-provider credentials for managed clusters mounted as volumes" — consistent with the kubectl-class delegation pattern even though the placement is missing. Surfacing for the reconciler — may warrant adding the delegation placement.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

- **Transport-conditional auth structure dominates the role.** Six paths apply only on HTTP/SSE transport: `Bearer token over HTTP/SSE`, `JWT`, `OAuth 2.x with issuer + JWKS`, `OAuth 2.1 / OIDC delegated`, `Per-request HTTP-header credentials`, `Per-request bearer token (provider-scoped)`. Stdio servers in the corpus universally fall back to `None / implicit` for caller-auth. This is the dominant axis the role's tree implicitly encodes but the role description doesn't surface.
- **Two distinct multi-mode-selector patterns** that look similar but differ in scope. `Multi-method selector` (`echelon-ai-labs--servicenow-mcp`, `SERVICENOW_AUTH_TYPE`) picks **upstream**-auth scheme (basic/OAuth/API-key for ServiceNow). The `AUTH_MODE` switch (`cyanheads`'s git/perplexity, `awslabs--aws-api-mcp-server`) picks **MCP-caller**-auth scheme (none/jwt/oauth for the MCP server itself). Both are "selector switches" but address opposite ends of the trust boundary. Cross-corpus visibility makes the parallel obvious; per-bin work didn't co-locate them.
- **Stdio + hosted dual-leg deployments are common for vendor servers.** At least 5 samples (`getsentry--sentry-mcp`, `github--github-mcp-server`, `stripe--agent-toolkit`, `makenotion--notion-mcp-server`, `sooperset--mcp-atlassian`) ship both a static-key stdio leg and an OAuth 2.1 hosted leg. The two legs land under separate paths (`Static API key` and `OAuth 2.1 / OIDC delegated`); the dual-leg pattern is invisible without cross-path stacking. This is the kubectl-class dual-placement pattern's analog for vendor-hosted MCP services.
- **Author-pattern signal: cyanheads-style tri-modal AUTH_MODE.** Two samples (`cyanheads--git-mcp-server`, `cyanheads--perplexity-mcp-server`) share an `AUTH_MODE=none|jwt|oauth` switch as a deliberate deployment-flexibility primitive. Same author. This is the strongest "single-author convention shaping multiple samples" signal in the role; the awslabs cluster (5 cloud-chain samples) is similar but reflects an SDK pull (boto3 chain) rather than an author choice.
- **Slack tooling has the most fragmented auth patterns.** Three Slack-related samples (`duolingo--slack-mcp` OAuth 2.1, `slackapi--slack-mcp-plugin` OAuth 2.1 with workspace admin, `korotovsky--slack-mcp-server` four-mode XOX* selector) span three different paths despite all targeting one upstream. Reflects Slack's multi-credential-type permission model (cookie / user OAuth / bot) more than MCP design variance.
- **Database-native auth is uniformly stdio-mode.** All 8 `Database connection string` samples are stdio-only, single-tenant, with the URI/credentials-pair as the entire auth surface. None layer JWT or OAuth on top. The pattern is "DB credentials are the boundary; MCP transport is just stdio." Bears comparison with cloud-native chain samples (which also don't layer caller-auth on top) — both share "the upstream's auth model is the auth model, MCP adds nothing."
- **OAuth 2.1 OIDC samples cluster around hosted-endpoint deployments (7/9).** Only `duolingo--slack-mcp` and `viant--mcp` describe OAuth 2.1 without a vendor-hosted endpoint context. The remaining 7 are tied to vendor-operated mcp.* endpoints (mcp.sentry.dev, mcp.stripe.com, hosted Supabase, hosted GitHub, hosted Atlassian, hosted Neon, hosted Slack via slackapi). This corroborates the broader "hosted MCP endpoint → OAuth 2.1 default" hypothesis surfaced in the cross-role observations.
- **Kubectl-class dual-placement pattern confirmed.** As flagged in the prompt: `feiskyer` and `rohitg00` are placed under both `Mounted file credentials` (delivery mechanism) and `Delegated to upstream toolchain credentials` (abstraction level). `alexei-led` carries only the mounted-file placement and likely should also carry the toolchain-delegation placement (see Mis-placed samples). The dual-placement pattern is a structural feature, not a slip — explicitly acknowledged in both path descriptions.
- **`Delegated to upstream source` has zero supporting samples.** The path exists in the consolidated but no sample is currently placed under it. The description ("server connects to upstream sources using whatever credentials those sources expect, configured per-source in the manifest") sounds close to `Multi-scheme upstream auth` (`googleapis--mcp-toolbox` exhibits exactly this — per-source `tools.yaml` with IAM/standard creds). Reconciler decision: empty path is dormant — either remove or repopulate by re-categorizing `googleapis--mcp-toolbox` if the distinction between "per-spec auth" and "delegated to upstream source" is meaningful.
- **High-cohesion long tail of single-sample paths (16 paths with 1 sample each).** The role's long tail is structurally rich — each single-sample path captures a genuinely distinct mechanism (vault, dual-API split, bot identity, SFTP, IPC, etc.). This contrasts with `Server runtime`'s long tail, which is more about substrate variety. Authentication's variety comes from *how the trust boundary is implemented*, not the substrate — appropriate role description nuance worth elevating.
