# Pass 3 Refinements — Bin 3

Pass 3 (Attempt 2) refinements to `_CONSOLIDATED_breadth-then-depth.md` from a second normalize cycle on the bin 3 samples. Samples were already in role-tree format from Pass 2; this pass verified alignment, applied targeted updates, and re-surfaces unresolved structural concerns from Pass 2 that the reconciler has not yet integrated.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Caching and rate-limiting infrastructure > In-memory TTL cache (process-lifetime)` — `awslabs--openapi-mcp-server.md` — Process-local dict-based cache with TTL eviction (e.g., `cachetools` library). Survives only as long as the process runs; lower operational complexity than SQLite-backed cache; appropriate for short-lived server processes where restart-survival isn't required. Companion to existing `SQLite TTL cache` path which captures the persistent variant.

- `Caching and rate-limiting infrastructure > Retry with backoff for transient errors` — `awslabs--openapi-mcp-server.md` — Library-driven retry on upstream HTTP failures (e.g., `tenacity`). Distinct from `Token-bucket rate limiter` (proactive throttling against quota) and `Circuit breaker for external calls` (reactive protection against degraded upstream). Retry sits between them: attempts the same request multiple times with backoff to absorb transient flakiness without triggering the circuit-breaker trip. During Pass 3 the bin had `Token-bucket rate limiter` mapping `tenacity` retry; that mapping was incorrect (retry ≠ rate limiting) and was removed in favor of this proposed path.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Caching and rate-limiting infrastructure > SQLite TTL cache` — Existing description ("In-process SQLite database holds per-call cached responses with TTL") names the storage substrate as part of the path identity, but the bin shows process-internal caching with TTL using non-SQLite substrates (`cachetools`, `awslabs--openapi-mcp-server.md`). Either rename to `In-process TTL cache (SQLite-backed)` and add the in-memory companion path proposed above, or split the path into two siblings as Pass 2 already proposed.

- `Distribution channel > Pre-built host installer / one-click install URL` — `awslabs--mcp.md` documents one-click install buttons across six hosts (Kiro, Cursor, VS Code, Cline with Amazon Bedrock, Windsurf, Claude Code) as the *primary* README surface — copy-paste JSON snippets are de-emphasized in favor of deep links. Sharpen to call out "one-click button as primary delivery surface, JSON snippets demoted" as a known pattern variant — a vendor-monorepo move worth documenting.

- `Authentication > Static API key / token via env var` — `chroma-core--chroma-mcp.md` shows a uniform `CHROMA_<PROVIDER>_API_KEY` provider-prefixed convention that bundles three cloud SDKs (openai, cohere, voyageai) in core deps for friction-free provider switching. Sharpen to note: provider-prefixed env-var conventions enable graceful provider switching when the cloud SDKs ship in core deps rather than extras (fat install vs zero-friction switch trade-off).

- `Capability surface > Tools plus prompts (no resources)` — Description should explicitly call out "research-workflow prompts shipped alongside data-fetch tools" as one canonical use case. `blazickjp--arxiv-mcp-server.md` ships 6 tools plus MCP prompts for research analysis and literature review — prompts are a first-class shipped artifact, not just tools.

- `Capability surface > Bundled "agent SOPs" / vertical skill packs` — `awslabs--mcp.md` AWS MCP Server (preview/aggregator tier) bundles SOPs alongside CloudTrail audit logging — SOP bundling sometimes co-arrives with an audit channel, signaling a "vertical skill pack with compliance posture" variant. Sharpen description to mention the audit-paired variant.

- `Capability surface > Single code-execution tool with sandbox` — `baryhuang--mcp-server-aws-resources-python.md` exemplifies the deliberate design choice "code-as-tool" as an alternative to N hand-enumerated per-API tools, with AST validation + import allowlist as the trust boundary. Sharpen description to explicitly frame the design trade-off: one tool with rich Python expressivity vs. enumerating each upstream API operation. The trust model collapses to allowlist-tightness rather than per-tool authorization.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none — bin 3 samples all map to existing roles)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

- `Caching and rate-limiting infrastructure > SQLite TTL cache` — Already raised in Pass 2; carried forward unresolved. Should split into "SQLite TTL cache (persistent across restarts)" and "In-memory TTL cache (process-lifetime)" because the storage substrate fundamentally changes the trade-off (persistence vs simplicity) and the libraries used (sqlite3 module vs `cachetools` / `functools.lru_cache`). Supporting sample for the in-memory variant: `awslabs--openapi-mcp-server.md` (`cachetools`).

- `Caching and rate-limiting infrastructure > Token-bucket rate limiter` — As written, this path is a single mechanism (proactive throttling). Pass 2 conflated retry-with-backoff (`tenacity`) into this path; Pass 3 removed that mapping. The retry pattern deserves its own path — see `Proposed new paths` above. The existing `Token-bucket rate limiter` description can stay as-is; the split is "create a sibling path" rather than "split this path internally."

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Pass 2 concerns carried forward unresolved.** The Pass 2 refinement file noted four structural observations the reconciler has not yet integrated: cross-role linkage of "Agent SOPs bundle" between `Capability surface` and `Observability > CloudTrail audit logging` (potential cross-role tools entry); coexistence of `Repository layout > Server-framework sub-package` with `Server runtime > Python with hand-rolled MCP` (acceptable dual classification, no action needed); cross-cutting nature of `Multi-tenancy > Mode-switched backing store` (mode also affects auth — Chroma Cloud needs key, ephemeral doesn't); and bhauman--clojure-mcp's `Tools-heavy domain wrapper / domain-tool catalog` exhibiting opt-in LLM-augmented subset (per-tool LLM use). These remain valid concerns after Pass 3 re-examination — the reconciler should evaluate.

- **`tenacity` mapping correction during Pass 3.** Pass 2 mapped `awslabs--openapi-mcp-server.md`'s `tenacity` retry library under `Caching and rate-limiting infrastructure > Token-bucket rate limiter`. This was incorrect — tenacity is a retry library, not a rate-limiter. Pass 3 removed the heading from the sample and surfaced the mismatch as a proposed new path (`Retry with backoff for transient errors`) above. Until that path is integrated, the openapi-mcp-server sample shows the role with only the (also misaligned) `SQLite TTL cache` heading covering `cachetools`.

- **`cachetools` under `SQLite TTL cache` is a known mismatch.** Pass 2 raised this as a sharpening; Pass 3 confirms it's not just a description-sharpening issue but a path-naming issue. The existing path's name asserts "SQLite" as part of the identity, which forces the sample to either misrepresent its content or invent a new path. The cleanest resolution is the bucket split proposed above. Until then, the openapi-mcp-server sample under that heading explicitly notes the substrate mismatch in prose so reconciliation has the evidence at hand.

- **Repository layout: `Server-framework sub-package` for `awslabs--mcp-lambda-handler`.** This sub-package is a library for *building* MCP servers, not a server itself. The path captures the structural category; the artifact still exhibits a `Server runtime > Python with hand-rolled MCP` (the framework is the hand-rolled implementation consumers build atop) and `Deployment topology > Serverless (Lambda + API Gateway)` (the deployment shape consumers target when using it). The trio of these three paths together is the diagnostic signature for "server-construction framework targeting serverless"; flagging in case the reconciler wants a cross-role linkage pattern entry to make the signature recognizable.

## Convergence assessment

The bin is **almost converged**. All sample level-2 and level-3 headings exactly match consolidated role/path names after Pass 3 cleanup. Two paths remain genuinely misaligned with their content (`SQLite TTL cache` covering `cachetools`; the now-removed `Token-bucket rate limiter` mapping for `tenacity`) — both are reconciler-side fixes (path renaming or splitting), not sample-side work. No new roles needed. Pass 4 should not be required if the reconciler integrates the proposed bucket splits.
