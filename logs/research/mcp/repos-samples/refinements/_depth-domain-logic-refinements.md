# Depth Pass Refinements — Sample > Domain logic and embedded intelligence

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

**`Sample > Domain logic and embedded intelligence > Pass-through tool wrappers`** — current description lists upstream examples (Docker SDK, NASA Earthdata, Perplexity, Jupyter, raw SQL) that don't match the two actually-supporting samples (bedrock-kb-retrieval via boto3 and puppeteer-py via Playwright). Cross-corpus evidence: both supporting samples are SDK-shaped wrappers (boto3, Playwright) where the server does shape translation only, with the puppeteer case adding a small operational policy choice (non-headless mode, in-memory base64 screenshots flowing through MCP responses without disk intermediate). Suggested sharpening: replace the example list with a description grounded in the inspected pattern — "Tools map 1:1 onto upstream SDK or API operations (boto3 calls, Playwright operations). Server's job is shape translation, credential management, and minor operational policy (e.g., browser headlessness, in-memory artifact passing) — not domain logic. Lowest implementation cost; appropriate as the default."

**`Sample > Domain logic and embedded intelligence > Deterministic optimization layered on top of raw ops`** — current description is dominated by the postgres-mcp exemplar (workload compression, hypopg, Pareto-front, greedy search) and reads as if Postgres-specific. Cross-corpus evidence: the second supporting sample is kotlin-mcp-server's "intelligent proxy system" providing "complete, context-aware implementations rather than stubs" — same role (deterministic intelligence layered over raw ops) but a very different domain (IDE/codegen, not query optimization). Suggested sharpening: lead with the abstract pattern, then offer two concrete instantiations — "Server adds analytical computation that goes beyond exposing raw upstream ops. Two observed instantiations: (a) performance-tuning intelligence over a queryable backend (workload compression, hypothetical-index simulation, Pareto-front cost-benefit selection, greedy search adapted from published algorithms — postgres-mcp) and (b) context-aware code synthesis over IDE primitives (intelligent proxy producing complete implementations rather than stubs — kotlin-mcp-server). The MCP layer becomes a delivery vehicle for embedded research or codegen expertise. Appropriate when the underlying system supports introspection (pg_stat_statements, EXPLAIN, IDE state) and the author wants to encode domain expertise in tool form."

**`Sample > Domain logic and embedded intelligence > In-server LLM client`** — current description anchors heavily on getsentry's `EMBEDDED_AGENT_PROVIDER` env var as if it were a generic pattern; cross-corpus evidence shows clojure-mcp uses a different shape (optional external LLM integration for agent tools, no shared env var convention). Both samples agree on the *pattern* (server holds LLM credentials and invokes upstream LLM internally) but disagree on *configuration shape*. Suggested sharpening: separate the pattern from the specific naming convention — "The server holds API credentials for an LLM provider and can invoke the LLM internally during tool execution (for aggregation, summarization, or agent-shaped post-processing). Configuration shape varies — sentry-mcp uses an `EMBEDDED_AGENT_PROVIDER` selector with provider-specific keys; clojure-mcp treats LLM integration as optional per-tool rather than a single provider switch. Unusual — most MCP servers are pure tool-callers. Appropriate when post-processing of upstream data into LLM-friendly form is itself an LLM-shaped task."

**`Sample > Domain logic and embedded intelligence > Embedded RAG / retrieval pipeline`** — the sibling role *Capability surface — Embedded RAG / retrieval pipeline* (line 369–371 of the consolidated) carries a much richer description with two sub-axes ("always remote vs local-default" and "documentation-lookup-as-tool"). The Domain-logic version is thinner and only points at the Capability-surface entry as a cross-role link. Cross-corpus evidence here aligns with the richer description: mongodb-js exemplifies documentation-lookup-as-tool (assistant/KB search alongside DB ops), qdrant exemplifies local-default embedding (`fastembed` ONNX, no API key needed), fhir exemplifies fully-in-process pipeline (`llama-index` + `huggingface` + `pinecone` + `sentence-transformers` + `pymupdf`). Suggested sharpening: either fold the same sub-axis distinctions into this role's description (preferred — the role asks "what compute does the server perform"; sub-axes are part of that answer) or have this entry be a one-line pointer that explicitly names what the cross-role description carries, so a reader on this side doesn't think the cross-role link is decorative. See "Most-impactful finding" below for exact text proposal.

**`Sample > Domain logic and embedded intelligence > Visualization synthesis`** — current description is accurate but understates one specific cross-corpus signal: the planetary-computer sample additionally returns multi-format outputs (GeoTIFF, GeoParquet, Zarr) and mentions "large-file handling," which is a transport/payload implication of visualization synthesis worth flagging. Suggested sharpening: append one clause — "Frequently entails large-file or multi-format output handling (GeoTIFF, GeoParquet, Zarr) that interacts with transport-payload constraints; cross-role: see *Transport — payload sizing*."

**`Sample > Domain logic and embedded intelligence > Domain-specific terminology service integration`** — current description reads as forward-looking speculation ("a pattern likely to recur in legal, education, finance") despite n=1 supporting evidence (fhir-mcp-server / LOINC). Cross-corpus visibility confirms the speculation has no actual sample backing in this corpus. Suggested sharpening: drop the cross-domain extrapolation, keep only what was observed — "Servers fronting healthcare APIs integrate domain ontologies (LOINC) as a distinct upstream the server bridges alongside the primary API. Single-sample observation in this corpus; the same shape would naturally extend to any domain with a canonical taxonomy upstream." This matches Epistemic Humility from the design principles — n=1 in the corpus shouldn't claim recurrence in unobserved domains as if it were a pattern.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

**`Sample > Domain logic and embedded intelligence > Embedded RAG / retrieval pipeline`** — three samples cluster into three distinct sub-shapes: (a) full in-process pipeline as primary capability (fhir-mcp-server: llama-index + huggingface + pinecone + sentence-transformers + pymupdf), (b) local-default lightweight embedding to remove onboarding friction (qdrant: fastembed ONNX), (c) documentation-lookup-as-tool riding alongside non-RAG primary tools (mongodb-js: assistant/KB search alongside DB and Atlas tools). Three samples, three shapes — small N but clean axis. The Capability-surface sibling already names sub-axes (a)+(b) as "always remote vs local-default" and (c) as "documentation-lookup-as-tool"; recommend folding the same two-axis taxonomy into this role's description rather than splitting the bucket.

**`Sample > Domain logic and embedded intelligence > In-server LLM client`** — two samples differ on configuration shape (single env-var selector vs per-tool optional integration) but n=2 is too small to formalize as a sub-axis. Fold into description rather than split.

**`Sample > Domain logic and embedded intelligence > Deterministic optimization layered on top of raw ops`** — two samples come from very different domains (DB performance tuning vs IDE codegen). Could justify a future split between "performance/cost optimization" and "codegen / context-aware synthesis," but n=2 is too thin for a structural change now. Fold both instantiations into the description (see sharpening above).

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None proposed. The six populated paths each describe a genuinely distinct kind of compute (pass-through vs deterministic optimization vs LLM client vs visualization vs RAG vs terminology). No two paths blur together under cross-corpus inspection.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None proposed. Sub-axis observations above are best handled in description text given the current corpus sizes (max 3 samples per path under this role). A split needs at least 3 samples per resulting bucket; the corpus does not support that yet.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

None observed. Each supporting sample's content directly exemplifies the path it sits under:

- bedrock-kb-retrieval, puppeteer-py — both genuinely 1:1 SDK wrappers; pass-through is correct
- postgres-mcp, kotlin-mcp-server — both layer analytical/synthesis intelligence on raw ops; deterministic optimization is correct (with the caveat that "optimization" framing is Postgres-specific; see sharpening)
- clojure-mcp, sentry-mcp — both hold LLM credentials and invoke upstream LLMs internally; in-server LLM client is correct
- planetary-computer — generates images for LLM consumption; visualization synthesis is correct
- mongodb-js, qdrant, fhir-mcp-server — all bundle retrieval-pipeline machinery in-process; embedded RAG is correct
- fhir-mcp-server (terminology placement) — LOINC integration is genuinely a separate domain-ontology upstream, distinct from its RAG pipeline; both placements are correct (the same sample legitimately exhibits both kinds of compute)

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

**Cross-role description-quality asymmetry — same concept, two different prose qualities.** "Embedded RAG / retrieval pipeline" appears in both *Capability surface* (line 369) and *Domain logic and embedded intelligence* (line 2570). The Capability-surface version carries sub-axis taxonomy and concrete framework names; the Domain-logic version is a shorter restatement plus a Cross-role pointer. Same canonical shape, two prose entries — risks drift over time. Worth a reconciler decision: pick one as canonical, have the other be a one-line cross-role redirect, or keep both and accept the duplication. The same question may apply to other concepts that span roles (Workflow scaffolding via MCP prompts, User-publishable tools, Runtime tool registration API all have explicit "Cross-role: see..." pointers in this role's prose).

**Adoption-table arithmetic.** Path counts under this role total 11 (3+2+2+2+1+1) but the role-adoption line says 10 samples. The discrepancy is fhir-mcp-server appearing under both *Embedded RAG / retrieval pipeline* and *Domain-specific terminology service integration*. This is correct multi-placement (a single sample exhibits two kinds of embedded intelligence), and the role-adoption line correctly de-duplicates by sample. Worth noting for the reconciler so the role-adoption number isn't "fixed" to match the path-sum.

**Empty paths reveal the role's design boundary.** Two paths have zero supporting samples in the present corpus: `Workflow scaffolding via MCP prompts` (no sample lands here directly — the MCP-prompts pattern exists in the corpus but is captured under Capability surface, not as embedded intelligence) and `None (pure tool-caller)` (no sample explicitly self-described as having no embedded intelligence — most pure-tool-caller servers simply don't surface a section under this role at all). The "None" bucket is structurally redundant under the breadth-then-depth model where absence of a section is the default; consider whether "None" needs to be a represented path under this role at all, or whether non-presence is sufficient. (Not a depth-pass decision; flagging for the reconciler.)

**Pass-through bucket may be undercounted.** Only 2 samples explicitly self-describe as pass-through wrappers under this role, but the bin-1/bin-2/bin-3 evidence (and the consolidated's own observation that pass-through is "the standard pattern" / "the default") suggests most servers in the corpus *are* pass-through and simply don't author a section called this out. The 2/100 count under this role does not reflect the actual prevalence — it reflects how few authors thought to explicitly name the absence of embedded intelligence. Worth noting that adoption counts under this role measure "self-declaration of compute style" rather than "what the server actually does." Same caveat applies to the empty `None (pure tool-caller)` bucket.
