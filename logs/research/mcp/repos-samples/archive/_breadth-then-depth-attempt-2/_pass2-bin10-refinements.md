# Pass 2 Refinements — Bin 10

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Configuration delivery > Provider-specific proxy override hierarchy` — `ppl-ai--modelcontextprotocol.md` (`PERPLEXITY_PROXY` takes priority over standard `HTTPS_PROXY`/`HTTP_PROXY`) — Provider-prefixed proxy env var that overrides system-wide `HTTP_PROXY`/`HTTPS_PROXY` settings, recognizing corporate/enterprise environments where a specific proxy needs to override system defaults. Distinct from generic env-var configuration because the override hierarchy is itself a structural choice — server intentionally documents that its own proxy var wins over the standard ones. May surface elsewhere as a sub-axis of `Environment variables`.

- `Capability surface > Tool with output-shaping parameters (token economy)` — `ppl-ai--modelcontextprotocol.md` (optional `strip_thinking` parameter removes reasoning tags from Perplexity output for token savings) — Tool exposes a parameter that lets the caller control output verbosity/format at the per-call level (separate from per-tool output format selection which is about format choice; this is about content reduction). Token-saving feature pattern. Possibly fits `Per-tool output format selection` with sharpening, but the verbosity-reduction angle is structurally distinct from format choice.

- `Capability surface > Embedded RAG with local-default backend` — `qdrant--mcp-server-qdrant.md` (`fastembed` ONNX-backed embedding lib used for local-default embeddings, eliminating need for an embedding API key to get started) — Server bundles an embedding/retrieval backend that runs locally without external API keys, with optional escape hatch to remote service. Distinct from generic `Embedded RAG / retrieval pipeline` (which spans both local and remote retrieval) because the "no API key required" stance is a specific design choice that lowers onboarding friction for vector-DB MCPs. The local-default-with-remote-escape pattern.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Configuration delivery > Environment variables` — `ppl-ai--modelcontextprotocol.md` exhibits the proxy-override hierarchy pattern (`PERPLEXITY_PROXY` > `HTTPS_PROXY`/`HTTP_PROXY`). Existing description doesn't surface intentional precedence chains where provider-prefixed env vars override standard names. Sharpening: note that some servers document precedence ordering between provider-prefixed env vars and conventional ones (corporate proxy override scenarios).

- `Capability surface > Embedded RAG / retrieval pipeline` — `qdrant--mcp-server-qdrant.md` ships `fastembed` as a default-on, no-API-key local embedding backend. Existing description names embedded retrieval but doesn't surface the local-default-with-no-credentials onboarding stance as a structurally distinct choice (server runs out of the box without any embedding credential setup; remote embedding services are opt-in via `EMBEDDING_PROVIDER`). Sharpening: distinguish "always remote embedding (requires keys)" from "local-default with optional remote" as a sub-axis.

- `Authentication > Cloud-native identity / credential chain` — `redis--mcp-redis.md` exhibits Azure EntraID with explicit three sub-flows (service principal, managed identity, default Azure credential) plus automatic token renewal with background refresh, layered as an *alternative* to the standard Redis ACL credential path. Existing description names "service principal, managed identity, default Azure credential" but doesn't surface the dual-path coexistence (cloud-native AND traditional credential side-by-side). Sharpening: note that cloud-native identity is often offered as an *alternative* path to the upstream's native auth, not a replacement — same server speaks both.

- `Capability surface > Tools-heavy domain wrapper / domain-tool catalog` — `redis--mcp-redis.md` adds an unusual sub-pattern: in-server documentation-search tool via separate HTTP endpoint configured by `MCP_DOCS_SEARCH_URL` — RAG-style documentation augmentation attached to a database server. Existing description captures large tool catalogs but doesn't surface the "domain wrapper plus docs-search-as-tool" cluster. Sharpening: note when the domain-wrapper additionally exposes an in-server docs-search endpoint as a tool surface, distinct from the database operations.

- `Entry point and launch > Console script via [project.scripts] / npm bin` — `redis--mcp-redis.md` carries an unusual `[project.scripts]: redis-mcp-server = "src.main:cli"` with `src.` prefix in the module path. Existing description captures `pyproject.toml`'s `[project.scripts]` form but most projects use top-level module path without the `src.` prefix; the `src.main:cli` shape is unusual. Sharpening: note that some projects use `src.<module>:func` paths in `[project.scripts]` rather than a top-level module name — implies the project's `src/` directory is itself imported as a top-level package rather than serving as a layout container.

- `Capability surface > User-publishable tools` — `riza-io--riza-mcp.md` exhibits an `edit_tool` operation that modifies existing saved tools at runtime (not just `create_tool` and `execute_tool`). Existing description likely captures the publish-and-execute pattern; the edit-after-publish capability is rarer. Sharpening: note that tool-editing capability (`edit_tool`) is structurally distinct from publish-once-and-immutable patterns; mutable saved-tool surface is unusual among MCP servers.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — every sample mapped onto existing roles)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **paypal/paypal-mcp-server's `--tools=all` flag for capability gating.** I placed this under `Capability surface > Capability gating flags (per-tool, per-category, write-mode)`, but the `--tools=all` shape is genuinely closer to `Capability gating via tool subsets at install time` (the README pattern is "you opt in to all or selective subsets via the same flag at launch"). The boundary between "install-time capability flag" and "launch-time capability flag" is fuzzy when the `--tools` flag is on the launcher invocation (`npx -y @paypal/mcp --tools=all`); npx invocation is essentially launch-time but described as install in some samples. Reconciler may want to clarify the boundary or merge the two paths.

- **paypal sandbox/production environment branch.** PayPal's `PAYPAL_ENVIRONMENT=SANDBOX|PRODUCTION` is a single-binary environment selector — sandbox/production routed by env var rather than separate entry points. This is a structural choice (single artifact serving multiple deployment shapes via env var) but doesn't fit cleanly under any role. Captured under `Environment variables` configuration delivery without escalating; reconciler may want to surface "environment-mode selector" as a sub-pattern of configuration delivery or multi-tenancy.

- **ppl-ai HTTP mode CORS support.** The Perplexity server supports CORS on its HTTP transport for shared-server deployments. Currently absorbed into `Streamable HTTP` description with a mention of CORS. Reconciler may want a separate path or sharpening for "HTTP mode with CORS for shared client access" since this is the operational forcing function for multi-client browser-reachable HTTP MCP servers.

- **pragmar `--interactive` REPL.** pragmar's `--interactive` flag selects a terminal REPL mode rather than a transport. The existing path `Observability > --interactive REPL mode` exists but is filed under Observability (debug surface). Currently I placed this under `Transport > Selection mechanism` (noting that `--interactive` is not actually a transport) and under `Developer ergonomics > Inspector/debug tooling references`. Reconciler may want the Selection-mechanism description to acknowledge non-transport modes that bypass MCP entirely (REPL mode skips the protocol).

- **qdrant CLI args deprecated.** README states "CLI args deprecated" — the env-var-only config posture is itself a deliberate choice (away from CLI flags toward env vars). Currently absorbed under `Configuration delivery > Environment variables`. Reconciler may want a sharpening: env-var-only as a deliberate posture distinct from accidentally-env-var-only when the project drifted that way.

- **redis SSL granular knobs.** Redis MCP exposes `--ssl-ca-path`, `--ssl-keyfile`, `--ssl-certfile` alongside the URI scheme — granular SSL knobs as separate CLI flags. Currently captured under `CLI flags` without escalation; the granularity is a structural sub-choice (URI carries some info, SSL flags carry the rest). Reconciler may want to note the dual-channel configuration pattern (URI + sidecar flags) where some config layers above the connection string.

- **reminia editable-install-only distribution.** Currently captured under `Source clone with editable install` with the "developer-mode-as-release" annotation. The pattern is real (no PyPI release; expected user path is clone + editable install) but the existing path's framing is generic source-clone. Reconciler may want a description sharpening on `Source clone with editable install` to call out the case where it's the *only* install path (no PyPI parallel publication) — that's a deliberate distribution-strategy choice, not an oversight.

- **redis `Anthropic Claude Agent SDK` mention.** Redis MCP README references "Anthropic Claude Agent SDK" but the actual SDK in dependencies is `mcp[cli]` (raw MCP SDK), not Claude Agent SDK. The README phrasing is misleading — it's a marketing-style attribution rather than a technical dependency. Reconciler should not double-count this; I placed redis under `Server runtime > Python with raw MCP SDK` based on the actual `mcp[cli]>=1.26.0` dependency rather than the README phrasing. The Anthropic SDK reference is captured in the runtime description prose but not as a separate path.

- **rohitg00 OAuth 2.1 mention vs. existing path framing.** rohitg00's README says "optional OAuth 2.1 (RFC 9728)" which exactly matches the existing `OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)` path including the RFC 9728 detail. Good fit; flagging that the existing path's description is well-tuned to capture this case.

- **rohitg00 dual `Mounted file credentials` and `Delegated to upstream toolchain credentials`.** Same observation as the bin5 reconciler note about feiskyer/mcp-kubernetes-server — kubectl reads `~/.kube/config`, server doesn't auth on its own. I placed rohitg00 under both paths because both fit. Reconciler may want a convention here (one canonical path with two facets) since the same pattern recurs across kubectl-class MCP servers.
