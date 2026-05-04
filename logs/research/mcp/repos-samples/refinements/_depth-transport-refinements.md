# Depth Pass Refinements — Sample > Transport

Per-role cross-corpus refinement proposals from inspecting every sample's content under the Transport role. 16 paths total; 15 with supporting samples (CLI dispatcher to per-server stdio is the lone empty path, retained from earlier passes).

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### `Sample > Transport > stdio`

**What the existing description misses.** The current text bundles most of the right constraints but is thin on the *implicitness* dimension that dominates the corpus content. Of the 90 stdio samples, ~25 explicitly say the transport is "default," "implicit," "inferred," "not documented," or "deduced from launch command shape" (e.g., `riza-io--riza-mcp`, `rust-mcp-stack--rust-mcp-filesystem`, `JackKuo666--PubMed-MCP-Server`, `samuelgursky--davinci-resolve-mcp`, `spences10--mcp-turso-cloud`, `thenets--ghost-mcp`, `twolven--mcp-server-puppeteer-py`). The current "Often selected implicitly — README shows the launch command without naming the transport" captures this but understates how widespread the convention is. Most stdio samples are not selecting stdio — they simply launch a process and inherit it.

**Cross-corpus evidence.** The stdout/stderr-discipline detail in the current description is grounded in `sandraschi--email-mcp` ("hardened stdout/stderr isolation for JSON-RPC correctness") and the broader `awslabs--mcp` notice about transport churn — but only one sample explicitly elaborates the discipline. The Docker-wrapped-stdio pattern is real (`FuzzingLabs--mcp-security-hub` "docker run -i", `awslabs--aws-documentation-mcp-server`, `PagerDuty--pagerduty-mcp-server`, `voska--hass-mcp`, `datalayer--earthdata-mcp-server`) and the description mentions it. Outbound-only data plane is exemplified by `mukul975--cve-mcp-server` ("outbound-HTTPS only with no inbound listener ports") — a useful one-liner the description doesn't currently capture.

**Sharpened text suggestion.** Add a sentence around implicit-by-convention selection: *"For most servers, stdio is not chosen so much as inherited — README shows a launch command (`npx <pkg>`, `uvx <pkg>`, `python -m <module>`) without naming the transport, and the stdio default is implicit in the SDK/launcher. Explicit selection (`--transport stdio`, `<bin> stdio` subcommand) is the minority."* And add a brief note: *"Outbound-only data planes are common — the server has no inbound listener and only opens outbound HTTPS to the upstream API."*

### `Sample > Transport > Streamable HTTP`

**What the existing description misses.** The current description mentions HTTP runs "alongside stdio" but understates that an emerging cluster of servers ship **HTTP-only** with no stdio path at all. This isn't the same as "Hosted remote endpoint" — these are servers whose code itself only implements HTTP, regardless of who operates the deployment.

**Cross-corpus evidence.** HTTP-only servers in the corpus: `googleapis--mcp-toolbox` ("HTTP MCP server bound to port 5000 ... Stdio transport not surfaced"), `duolingo--slack-mcp` ("HTTP-only; listening on port 8001"), `supabase-community--supabase-mcp` ("HTTP is the canonical mode ... No stdio path documented"), `awslabs--mcp-lambda-handler` (its own path; HTTP-inherent), `cloudflare--mcp-server-cloudflare` (Streamable HTTP via `/mcp` is the primary; stdio side handled by the universal `mcp-remote` shim). At least 4 distinct HTTP-only servers in the corpus, with `duolingo` explicitly citing OAuth as the forcing constraint.

**Sharpened text suggestion.** Add a short paragraph: *"A growing cluster of servers ship HTTP-only with no stdio path — typically because OAuth 2.1 is the auth model (browser redirect targets need a reachable endpoint) or because the deployment substrate (Cloudflare Workers, Lambda, Supabase managed services) is inherently HTTP. These servers either expect users to point hosts directly at the URL or rely on a client-side stdio shim (see Stdio-to-HTTP shim) for hosts that only know how to spawn processes."*

### `Sample > Transport > SSE (Server-Sent Events)`

**What the existing description misses.** The description says "New work selects streamable-HTTP instead; SSE persists where backward compatibility ... matters." That's accurate for SDK-rich servers (Cloudflare, Neon, Elastic, k8s-mcp), but a non-trivial subset of corpus samples treat SSE as their *primary* HTTP path, not as legacy — `sooperset--mcp-atlassian` ("SSE primary"), `tumf--grafana-loki-mcp` ("SSE supported alongside stdio" with no Streamable HTTP), `echelon-ai-labs--servicenow-mcp` (dedicated `servicenow-mcp-sse` console script), `executeautomation--mcp-playwright` ("HTTP/SSE supported" without distinguishing). For these, SSE is the network transport, not a deprecated step on the way to Streamable HTTP.

**Cross-corpus evidence.** ~10 of 29 SSE samples treat SSE as primary or coequal-with-stdio. The deprecation framing dominates SDK-internal samples (Cloudflare Workers, Kotlin SDK, mcp-go) but is less universal in domain-server samples that adopted SSE early and haven't migrated.

**Sharpened text suggestion.** Soften the deprecation framing slightly: *"In SDK-internal samples and recent vendor servers, SSE is supported-but-deprecated — Streamable HTTP is the migration target, often coexisting on a separate path (`/sse` alongside `/mcp`). In older domain servers, SSE is still the primary HTTP transport, with no Streamable HTTP path; whether to migrate depends on the SDK they're built on."*

### `Sample > Transport > Hosted remote endpoint (vendor-operated)`

**What the existing description misses.** The description is concise and mostly accurate, but the cross-corpus evidence reveals a tighter pattern: **all** 7 hosted endpoints in the corpus follow `https://mcp.<vendor>.<tld>/mcp` URL convention. (`mcp.exa.ai/mcp`, `mcp.sentry.dev`, `api.githubcopilot.com`, `mcp.neon.tech/mcp`, `mcp.slack.com/mcp`, `mcp.stripe.com`, `mcp.context7.com/mcp`.) GitHub is the only one not using `mcp.<domain>` (it uses `api.githubcopilot.com`). The convergence on a `mcp.` subdomain is worth noting as a discoverability convention.

**Sharpened text suggestion.** Add: *"Vendor URLs converge on a `mcp.<vendor-domain>` subdomain pattern (`mcp.sentry.dev`, `mcp.neon.tech`, `mcp.slack.com`, `mcp.stripe.com`, `mcp.context7.com`, `mcp.exa.ai`); the path is typically `/mcp`. GitHub Copilot is the outlier (`api.githubcopilot.com`)."*

### `Sample > Transport > Selection mechanism`

**What the existing description misses.** The 10 sub-bullets capture the explicit mechanisms, but two patterns from the corpus aren't yet listed:

1. **Endpoint-URL-based selection** — server publishes both Streamable HTTP and SSE on the same host under different paths (`/mcp` vs `/sse`); the client "selects" by hitting the path, not by configuring a flag. Examples: `cloudflare--mcp-server-cloudflare` ("URL path selects transport on the same Worker"), `neondatabase--mcp-server-neon` ("clients hit `/mcp` for streamable HTTP or `/sse` for the legacy transport").

2. **Install-target split** — distinct distribution channels for local-stdio vs remote-hosted, treated as two separate products by the user. Examples: `getsentry--sentry-mcp` ("stdio install points `npx` at the package; remote points the host at `mcp.sentry.dev`"), `stripe--agent-toolkit` ("`npx @stripe/mcp` for stdio (local), the hosted URL for remote/OAuth — Two distinct entry points rather than runtime mode-switching within one binary"), `github--github-mcp-server` (stdio subcommand for local, `api.githubcopilot.com` for hosted). This is *not* the same as "Separate console scripts per transport" — those are local binaries; install-target split is "two completely different things, one of which you don't run yourself."

**Sharpened text suggestion.** Add two bullets to the cross-cutting list:

- *"**Endpoint-URL-based** — multi-transport HTTP server publishes `/mcp` (Streamable HTTP) and `/sse` (legacy) on the same host; client selects by URL path. Common on multi-transport hosted endpoints (Cloudflare Workers, Neon)."*
- *"**Install-target split** — same product ships as a local stdio package (npm/PyPI) for self-host and as a vendor-hosted URL for remote/OAuth use. The user picks at install time by choosing which artifact to consume — there is no in-binary mode switch. Often paired with auth model: stdio install uses API-key env var; hosted URL uses OAuth."*

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### `Sample > Transport > stdio` — Docker-wrapped stdio sub-pattern

Sub-pattern: stdio inside a Docker container (`docker run -i`) instead of bare process. ~5-6 explicit samples (`FuzzingLabs--mcp-security-hub`, `awslabs--aws-documentation-mcp-server`, `PagerDuty--pagerduty-mcp-server`, `voska--hass-mcp`, `datalayer--earthdata-mcp-server`). Already mentioned in the description ("Works equally well when the server is wrapped in a Docker container"). **Fold into description (already there) — no split needed.** This is a deployment shape, not a transport variant.

### `Sample > Transport > stdio` — Implicit vs explicit selection

Sub-pattern: most stdio samples don't select stdio — they inherit it. ~25 samples explicitly call out implicitness. **Cross-role with Selection mechanism > Implicit single mode** (which has its own coverage). Recommend folding the *frequency* observation into the stdio description rather than splitting; selection mechanism already owns the cleavage.

### `Sample > Transport > Streamable HTTP` — HTTP-only deployments (no stdio)

Sub-pattern: at least 4 servers ship HTTP without any stdio path, forced by OAuth or substrate. Already noted in the sharpening above. **Fold into description.** Not large enough or differentiated enough to warrant a split (the underlying transport is still Streamable HTTP).

### `Sample > Transport > SSE (Server-Sent Events)` — Primary-SSE vs legacy-SSE

Sub-pattern: SSE samples cluster into "SSE is our primary network transport" vs "SSE is the deprecated path while Streamable HTTP migrates in." ~10 vs ~19 split. **Fold into description (sharpening above).** Not a split — same wire protocol, different lifecycle stance.

## Proposed bucket merges

### `HTTP with JSON response mode` + `Streamable HTTP`

**Why same.** Both samples currently under `HTTP with JSON response mode` (`rohitg00--kubectl-mcp-server`, `the-momentum--fhir-mcp-server`) describe servers that *also* support Streamable HTTP and treat JSON-mode as a sub-axis of HTTP, not a distinct transport. Cross-corpus, `mongodb-js--mongodb-mcp-server`'s Streamable HTTP entry says "HTTP mode with JSON response mode supported" — same factual content placed under Streamable HTTP, not under HTTP-with-JSON. The Kotlin SDK Streamable HTTP description says "Single endpoint with optional JSON-only or SSE response modes," confirming JSON-mode is an option *within* Streamable HTTP, not a sibling.

**Supporting samples.** 2 currently under `HTTP with JSON response mode`; ~3 under Streamable HTTP that mention JSON-mode in passing.

**Recommendation.** Merge `HTTP with JSON response mode` into `Streamable HTTP` — surface JSON-only response mode as a sub-axis bullet inside the Streamable HTTP description ("Streamable HTTP supports both streamed and single-response JSON modes; some servers select via env var or flag"). Not high-confidence — `HTTP with JSON response mode` may be useful as a path if more samples surface it as the *only* HTTP mode they support, but current evidence doesn't support that distinction.

## Proposed bucket splits

None proposed. Tree shape held up across the cross-corpus inspection. Sub-axes observed are descriptive nuances rather than structural divisions.

## Mis-placed samples

### `awslabs--openapi-mcp-server` currently under `stdio`

The sample's content under stdio mentions `uvicorn` as a runtime dep "despite stdio transport — suggests an undocumented HTTP mode or internal HTTP client pool." This is speculative on the sample author's part, not a placement issue per se — but reconciler should consider whether this sample also belongs under Streamable HTTP if other evidence in the sample file points to undocumented HTTP support. Low-confidence; keep at stdio absent stronger evidence.

### `awslabs--mcp` currently under `stdio`

The sample content describes transport state of flux: SSE removed 2025-05-26, Streamable HTTP "in-development," stdio "the only shipping transport (per repo notice)." Currently correctly placed at stdio (matches current state) but the content is more about transport churn than the stdio path itself. **Not a mis-placement** — correct state-of-record under stdio. Reconciler should not move.

### No genuine mis-placements found.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Vendor URL convergence on `mcp.<domain>` subdomain

7-of-7 hosted vendor endpoints (except GitHub) use a `mcp.` subdomain. This is informal MCP-ecosystem convention, not specified anywhere — but vendors reaching for the convention voluntarily suggest discoverability is becoming the de-facto spec. Worth a one-line mention in the Hosted-remote-endpoint description (covered above).

### Auth model dictates transport more than runtime preference

`duolingo--slack-mcp` is the cleanest articulation: HTTP-only forced because OAuth 2.1 cannot complete in stdio. This pattern propagates: every OAuth-using server in the Hosted-remote sub-corpus is HTTP-only on the wire, even where the stdio path *could* exist. Authentication is not a downstream concern of transport choice — it's an upstream constraint. The role-level Transport description hints at this ("authentication options (no-auth vs bearer/OAuth)") but doesn't make the directionality explicit. Consider sharpening role-level: *"Authentication model often forces transport choice — OAuth flows require a reachable HTTP endpoint, so OAuth-using servers are HTTP-only or hosted-remote regardless of other deployment preferences."*

### "Default + only" is the dominant single-mode pattern

Many stdio entries say variants of "default and only documented transport" / "stdio is the only currently-supported transport" / "no alternate transport documented." The corpus suggests two distinct stdio postures:

- **Default-stdio-with-explicit-alternatives** — the binary supports multiple transports; stdio is the convenient default.
- **Stdio-only-no-alternative** — the binary supports nothing else; stdio is the entire surface.

These overlap with Selection mechanism's "Implicit single mode" and "CLI flag at startup" categories, so the cleavage is captured indirectly. Not actionable as a stdio-internal split, but worth knowing the proportion is roughly 50/50 in the corpus.

### `rust-mcp-stack--rust-mcp-filesystem` content is purely inferred

This sample's stdio entry says "Not explicitly documented in extracted README content; inferred to be stdio-based given standard MCP filesystem-server convention and the absence of any HTTP/network configuration." This is an honest epistemic-humility flag — the sample author couldn't verify, so they inferred. Not a mis-placement, but if the corpus is regenerated or audited, this entry is a candidate for re-extraction or removal. Surface to reconciler as low-confidence support.

### Selection mechanism is essentially a meta-role

The 77-sample `Selection mechanism` path is markedly larger than any single transport's path except stdio, and its content is genuinely cross-cutting — every sample's selection-mechanism entry could equally be filed under the underlying transport(s) it selects. The current treatment (cross-cutting sub-axis with bulleted patterns) is the right shape; the depth pass confirms that splitting it back into per-transport "How to select this transport" leaves would inflate every transport path with duplicated mechanism prose. Keep as-is.
