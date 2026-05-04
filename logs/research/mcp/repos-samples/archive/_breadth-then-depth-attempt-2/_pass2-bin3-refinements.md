# Pass 2 Refinements — Bin 3

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Distribution channel > Language-native installer (Maven coords via `clojure -Ttools`)` — `bhauman--clojure-mcp.md` — Existing `Language-native installer` path covers this; the example in the description (`clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp`) already names the Clojure case. No new path needed; kept here as a confirmation rather than a refinement.

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Caching and rate-limiting infrastructure > SQLite TTL cache` — Description says "in-process SQLite database holds per-call cached responses with TTL." `awslabs--openapi-mcp-server.md` shows `cachetools` (in-memory dict cache, not SQLite) used the same way. Suggest renaming the bucket or splitting: keep `SQLite TTL cache` as the persistent variant and add an in-memory cache path (e.g., `In-process TTL cache (cachetools)`) so both are representable without conflating storage substrate.
- `Capability surface > Tools plus prompts (no resources)` — Existing description should explicitly note that "research-workflow prompts" is one canonical use case (analysis prompts shipping alongside data-fetch tools). `blazickjp--arxiv-mcp-server.md` ships 6 tools + research prompts; sharpens the existing path with a concrete domain example.
- `Capability surface > Bundled "agent SOPs" / vertical skill packs` — `awslabs--mcp.md` AWS MCP Server (preview) bundles SOPs alongside CloudTrail audit. Description could mention that SOP bundling sometimes co-arrives with audit logging as a vertical-skill pack rather than just tools.
- `Distribution channel > Pre-built host installer / one-click install URL` — `awslabs--mcp.md` documents one-click install buttons across six hosts as the primary README surface; add it as a strong example demonstrating "URL-protocol install button as primary documentation surface."
- `Authentication > Static API key / token via env var` — `chroma-core--chroma-mcp.md` shows a `CHROMA_<PROVIDER>_API_KEY` provider-prefixed pattern that bundles three cloud SDKs in core deps for graceful provider switching — sharpens the existing description's "provider-prefixed convention" sentence with the "fat install, zero-friction switching" trade-off.
- `Capability surface > Single code-execution tool with sandbox` — `baryhuang--mcp-server-aws-resources-python.md` exemplifies the "code-as-tool" architecture as a deliberate alternative to N hand-enumerated per-API tools; description could highlight this design choice trade-off explicitly.

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

- `Caching and rate-limiting infrastructure > SQLite TTL cache` — Should split into "SQLite TTL cache (persistent across restarts)" and "In-memory TTL cache (process-lifetime)" because the storage substrate is different and the trade-offs (persistence vs simplicity) differ. Supporting sample for the in-memory variant: `awslabs--openapi-mcp-server.md` (uses `cachetools`).

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- `awslabs--mcp.md` — repo-level "umbrella monorepo" attributes (40+ servers under one namespace; consolidation pattern; central dev tooling) fit cleanly under `Repository layout > Monorepo of namespace-prefixed packages`. The "preview aggregator that bundles SOPs + CloudTrail audit" is a cross-role observation: it is simultaneously a `Capability surface > Bundled "agent SOPs" / vertical skill packs` exhibition and an `Observability > CloudTrail audit logging` exhibition. The current sample maps each fact to its role separately (intended); flagging that the consolidated may want a cross-role linkage entry under `Cross-role tools` for "Agent SOPs bundle" similar to existing `Docker` / `MCPB` cross-role entries — reconciler may judge whether this is widespread enough across the corpus to warrant a cross-role entry.
- `awslabs--mcp-lambda-handler.md` — clear example of a `Repository layout > Server-framework sub-package` (already in consolidated) coexisting with `Server runtime > Python with hand-rolled MCP`, where the framework is itself the "hand-rolled" implementation that consumers build atop. The two paths are mutually reinforcing for this artifact; no structural concern, just confirmation of the existing dual classification.
- `chroma-core--chroma-mcp.md` notable structural choice "single binary supports 4 backing-store modes chosen via flags" is well-captured by the existing `Multi-tenancy > Mode-switched backing store` path. The cross-cutting nature (mode also affects auth — Chroma Cloud needs a key, ephemeral doesn't) does not yet have a representational home; reconciler may consider whether mode-switching's authentication implications deserve mention in either the auth or multi-tenancy path descriptions.
- `bhauman--clojure-mcp.md` exhibits `Capability surface > Tools-heavy domain wrapper / domain-tool catalog` (50+ tools) AND uses external LLM API keys for some tools — a pattern not cleanly captured by `Domain logic and embedded intelligence > In-server LLM client` because the LLM use is opt-in per-tool rather than core to every tool. Could the reconciler consider a path qualifier "Optional LLM-augmented subset within a tools-heavy catalog" or note this in the existing `In-server LLM client` description as a "may be optional / per-tool" variant?
