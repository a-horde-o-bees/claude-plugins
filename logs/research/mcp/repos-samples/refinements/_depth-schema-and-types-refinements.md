# Depth Pass Refinements — Sample > Schema and types

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role. 7 paths total, all 7 with supporting samples. Total sample evidence consumed: ~14.8 KB across 90 sample sections (FastMCP 26, Pydantic 19, Hand-authored 13, Async 25, Zod 4, Go 2, Rust 1).

The role is unusual in two ways visible only at cross-corpus scale: (1) the path family is not mutually exclusive — a sample can simultaneously sit under `FastMCP auto-derivation`, `Pydantic v2 models`, and `Async model (cross-cutting)`, and most Python samples do; (2) the supporting evidence on most paths leans heavily on inference rather than direct observation. Phrases like "FastMCP-style auto-derived schema (inferred)", "schemas hand-authored likely", "FastMCP default (Pydantic-based) inferred", "specifics not surfaced" recur across 12+ samples. The depth-pass cannot fix that — it can only flag where the existing description's confident framing exceeds the corpus's actual signal strength.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### Sample > Schema and types (role-level)

The role-level prose currently reads: "How tool input/output schemas are produced and validated. Tightly coupled to the runtime choice." This conflates two genuinely orthogonal concerns:

- **Schema source mechanism** — auto-derivation from type hints, hand-authored schema dicts, declarative manifest, etc. The path siblings under this role are all about this dimension.
- **Validation library** — Pydantic, Zod, dataclasses, native struct reflection. This dimension is correlated with runtime choice but carries independent information (Pydantic v1 vs v2, Zod 3 vs 4, etc.).

The current paths mix the two: `FastMCP auto-derivation from type hints` and `Hand-authored tool schemas` describe the **mechanism**, while `Pydantic v2 models` and `Zod (TypeScript)` describe the **library**. A FastMCP server using auto-derivation typically also uses Pydantic — it lands under both paths, not because it's making two choices but because the paths are along different axes. Cross-corpus evidence: 5 samples (`awslabs--aws-api-mcp-server`, `jbeno--cursor-notebook-mcp`, `openags--paper-search-mcp`, `qdrant--mcp-server-qdrant`, `severity1--terraform-cloud-mcp`) sit under both `FastMCP auto-derivation` and `Pydantic v2 models` because the description of each path captures a different facet of the same truth.

Sharpened text suggestion: revise the role prose to acknowledge two axes — "How tool input/output schemas are produced and validated. Two orthogonal axes characterize a server's choice: (1) **schema source mechanism** — how the JSON Schema advertised to the host is produced (auto-derived from typed function signatures, hand-authored as explicit schema dicts, generated from external specs, or compile-time-checked via type system); (2) **validation library** — what runtime validation type system, if any, sits behind the schema (Pydantic v2 in Python, Zod in TypeScript, native struct reflection in Go, type system itself in Rust). The two axes are correlated — FastMCP+Pydantic, raw-mcp-SDK+hand-authored-dicts, TS-SDK+Zod recur as packages — but a sample's choice on each axis carries independent information, so most samples appear under multiple paths in this role." This makes explicit what is currently implicit and explains the cross-path overlap a reader sees in the adoption table.

### Sample > Schema and types > FastMCP auto-derivation from type hints

The existing description states FastMCP "derives JSON schemas via Pydantic at registration time" and that this is the "default when FastMCP is the runtime." Cross-corpus evidence both confirms and exceeds the description, but also exposes how thin the actual sample evidence is:

- **Inference-heavy supporting set.** Of 26 supporting samples, only 4 actually surface the `Annotated[type, Field(description=...)]` pattern, docstring use, or specific schema-derivation mechanics: `jlowin--fastmcp` (the framework itself), `zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server`, `mahdin75--gis-mcp`. The remaining 22 say "FastMCP auto-derives schemas" or similar — restating the framework's behavior rather than evidence it's used in this sample. Several samples are explicit about the inference: `AlwaysSany--deepl-fastmcp-python-server` ("inferred from FastMCP usage, not directly captured"), `rohitg00--kubectl-mcp-server` ("FastMCP default ... inferred; specifics not surfaced"), `sandraschi--email-mcp` ("Annotated patterns likely (not directly verified)").
- **`Annotated[type, Field(description=...)]` pattern.** Mentioned only in `jlowin--fastmcp` itself. The current description doesn't claim this is universal but reads as if the pattern is observable corpus-wide.
- **Docstrings as schema source.** `jlowin--fastmcp` notes auto-derivation uses both type hints AND docstrings. No other sample surfaces this.

Sharpened text suggestion: keep the current description but acknowledge the inference: "Tool function signatures with type hints become the MCP tool's input schema automatically; return types feed the output schema. Authoring effort is 'write a typed Python function.' Default when FastMCP is the runtime; FastMCP derives JSON schemas via Pydantic at registration time and can additionally consume docstrings for descriptions and `Annotated[type, Field(description=...)]` for richer field metadata. Cross-corpus, this path is largely inferred from runtime choice rather than directly observed — most repositories declare FastMCP as a dependency without surfacing the schema-derivation mechanics in their public docs."

### Sample > Schema and types > Pydantic v2 models

The current description anchors on "explicit hand-authored Pydantic models for richer validation" — author writes models and registers them with the SDK. Cross-corpus evidence shows three quite different ways Pydantic v2 enters a sample, only one of which fits the description's framing:

- **Cluster A — Pydantic as transitive dep, schemas auto-derived (pure FastMCP idiom)** — 5 samples sit under both FastMCP auto-derivation and Pydantic v2: `qdrant--mcp-server-qdrant` ("Pydantic 2 (direct dep); FastMCP auto-derives schemas from type hints"), `openags--paper-search-mcp` ("Pydantic via FastMCP / MCP SDK — schemas auto-derived from type hints"), `severity1--terraform-cloud-mcp`, `jbeno--cursor-notebook-mcp`. Pydantic is present but author isn't writing models explicitly; it's the registration-time validation library FastMCP uses.
- **Cluster B — Pydantic models hand-authored alongside FastMCP for richer payload shaping** — `mukul975--cve-mcp-server` is the cleanest exemplar: "Hand-authored Pydantic v2 models (`CVERecord`, `KEVEntry`, `EPSSScore`, etc.) with custom validators paired alongside FastMCP tool signatures." This is what the current description describes — an explicit author choice for explicit control.
- **Cluster C — Pydantic via the raw `mcp` SDK / `mcp[cli]` extra (not FastMCP)** — 14 samples, including `awslabs--bedrock-kb-retrieval-mcp-server`, `awslabs--openapi-mcp-server`, `chroma-core--chroma-mcp`, `datalayer--earthdata-mcp-server`, `datalayer--jupyter-mcp-server`, `voska--hass-mcp` ("Pydantic arrives via the `mcp[cli]` extra"). Several samples are explicit Pydantic comes "via the MCP SDK (pulled in transitively rather than declared explicitly)" — `chroma-core--chroma-mcp`. Schemas may be auto-derived (raw MCP SDK can derive too) or hand-registered.
- **Cluster D — Pydantic-settings for typed config** — distinct concern but cohabits the role: `DiversioTeam--clickup-mcp` ("`pydantic>=2.0.0` for validation; `pydantic-settings>=2.0.0` for typed config"), `the-momentum--fhir-mcp-server` ("Pydantic v2 (explicit dep) with `pydantic-settings` for config").

Sharpened text suggestion: reframe to acknowledge the four observed clusters. Suggested text: "Pydantic v2 surfaces in four distinct ways across the corpus: (a) as the transitive validation library FastMCP uses for auto-derivation, with no author-written models — Pydantic is just present as a direct or transitive dep; (b) as hand-authored Pydantic models the author explicitly writes for richer payload shaping (named record types with custom validators) alongside FastMCP or raw-SDK tool signatures; (c) as a transitive dep of the `mcp[cli]` extra, used by the raw MCP SDK for both auto-derivation and hand-registered schemas; (d) `pydantic-settings` paired alongside Pydantic for typed env-var config loading, distinct from tool-schema duties. The path captures presence of Pydantic v2 in any of these forms; the schema-source-mechanism is described by the sibling auto-derivation and hand-authored paths."

### Sample > Schema and types > Hand-authored tool schemas

The current description correctly identifies the raw-SDK-without-FastMCP cohort and the very-large-tool-surface (300+) and TypeScript cases. Cross-corpus evidence affirms most of this but reveals the description undersells the inference problem AND understates an important auxiliary case:

- **Inference dominates** — 8 of 13 samples say "hand-authored schemas likely" or "specifics not surfaced": `ckreiling--mcp-server-docker`, `crystaldba--postgres-mcp`, `designcomputer--mysql_mcp_server`, `normaltusker--kotlin-mcp-server`, `pragmar--mcp-server-webcrawl`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`. The corpus signal supporting this path is largely "uses raw `mcp` SDK without FastMCP" — schemas are inferred to be hand-authored because the alternative is FastMCP auto-derivation.
- **TypeScript SDK case is unrepresented in supporting samples** — the description mentions "TypeScript servers where schemas are written directly," but the four TS samples sit under `Zod (TypeScript)`, not here. The TS-with-hand-authored-schemas claim is unsupported by the supporting samples — the TS samples that surface schema info all surface Zod.
- **Special exemplar: `awslabs--openapi-mcp-server`** — appears under BOTH `Pydantic v2 models` AND `Hand-authored tool schemas` because schemas are auto-derived from external OpenAPI specs at runtime. This isn't "hand-authored" in the typical sense — the operator hand-authors nothing; the author of the server hand-built the schema-from-spec adapter. It fits the path only by stretching the definition. See Mis-placed samples.
- **Special exemplar: `awslabs--mcp-lambda-handler`** — "No Pydantic dependency — tool schema strategy likely dataclasses or TypedDict; schemas hand-authored without an SDK to derive them." This is a distinct sub-pattern: hand-rolled MCP runtime + dataclass/TypedDict schemas + no Pydantic at all. The description's "raw `mcp` SDK without FastMCP" framing doesn't fit.

Sharpened text suggestion: "Tool handlers register an explicit input schema dict; the author writes the schema directly rather than having a framework derive it. Two source patterns: (a) raw `mcp` Python SDK without FastMCP — handler functions register schemas hand-built as dict literals; (b) hand-rolled MCP runtimes (no `mcp` or `fastmcp` dep at all) where the author chooses dataclasses, TypedDict, or bare dict schemas. Used for very large tool surfaces (300+ tools) where reflective derivation cost matters at startup, when source-of-truth is an external API spec adapted at runtime, and when the runtime ergonomics around explicit schema dicts are preferred to decorator magic. The corpus signal here is largely circumstantial — most supporting samples don't surface schema specifics directly; the path is inferred from runtime choice and absence of FastMCP."

### Sample > Schema and types > Zod (TypeScript)

The current description is short and accurate. Cross-corpus evidence on 4 supporting samples is consistent: Zod is used for **both** tool input validation AND env/config validation in TS samples, never just one. Per-sample:

- `cyanheads--git-mcp-server` — "Zod for env-var and runtime validation"
- `cyanheads--perplexity-mcp-server` — "Zod schema validation for config; runtime validation across transport selection and `.env` parsing"
- `exa-labs--exa-mcp-server` — "Zod for validation" (unspecified but small surface)
- `makenotion--notion-mcp-server` — "Zod 3.24.1 for runtime validation in tool inputs and configuration"

The "tool input schema" duty isn't always explicit in samples — `cyanheads` samples emphasize env-var validation, while `makenotion` covers both. The description currently leads with "tool inputs and env/config" which fits the corpus signal accurately.

Sharpened text suggestion: minor only — "Zod schemas validate tool inputs and env/config in TypeScript servers. Across the corpus Zod consistently does double duty — runtime validation of both the agent-facing tool input shape and the operator-facing environment variable / `.env` parsing. Appropriate when the server runs on Node and the surrounding stack already uses Zod for runtime validation. Pinned versions observed in the 3.x line."

### Sample > Schema and types > Rust schema crate

Single supporting sample (`conikeec--mcpr`). The current description captures the mechanism but generalizes a single-sample observation to "the natural Rust idiom":

- The supporting sample's content: "JSON-object schema definitions with properties and required arrays, declared via the ServerConfig builder." That's a very specific builder-pattern style that's already noted in `Sample > Server runtime > Rust with rmcp / rust-mcp-sdk` as `conikeec--mcpr`-specific (per the existing server-runtime depth-pass refinement).
- Other Rust samples in the corpus (`elastic`, `apollographql`, `rust-mcp-stack`) don't surface schema specifics, so we can't generalize.

Sharpened text suggestion: tighten to the single sample's actual evidence: "`rust-mcp-schema` crate provides the type definitions; tools are registered with strongly-typed handlers via builder-pattern APIs (e.g., `ServerConfig::with_name().with_version().with_tool()`). Types are compile-time-checked rather than reflected. Observed in the rust-mcp-sdk family; other Rust samples in the corpus (rmcp-based) don't surface schema specifics so this path describes the rust-mcp-sdk idiom rather than 'all Rust MCP servers.'"

### Sample > Schema and types > Go automatic schema generation

Two supporting samples (`mark3labs--mcp-go`, `metoro-io--mcp-golang`). Both surface essentially the same content: "Native Go structs become tool arguments with automatic JSON-Schema generation via the SDK's reflection." The current description matches.

Sharpened text suggestion: the description is fine. Optional minor tightening: drop "Type-safe schemas without runtime reflection cost matter" — the second sample doesn't surface this rationale; it's the value proposition only `mark3labs` actually states. The path is well-covered as is.

### Sample > Schema and types > Async model (cross-cutting)

The current description splits async into three sub-patterns (Async throughout / Sync throughout / Mixed) and gives accurate framing for each. Cross-corpus evidence affirms the three sub-patterns and reveals their distribution and rationales clearly:

- **Async throughout (~16 samples)** — `awslabs--mcp`, `awslabs--openapi-mcp-server`, `blazickjp--arxiv-mcp-server`, `crystaldba--postgres-mcp`, `datalayer--jupyter-mcp-server`, `mukul975--cve-mcp-server`, `normaltusker--kotlin-mcp-server`, `openags--paper-search-mcp`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `sajal2692--mcp-weaviate`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `the-momentum--fhir-mcp-server`, `tumf--grafana-loki-mcp`. Common rationale: httpx + async upstream client (postgres async via psycopg3, redis-py async, weaviate-client async, FHIR via httpx, etc.). Test signal: `pytest-asyncio` with `asyncio_mode = "auto"`. Several FastMCP-based samples cite "FastMCP default" rather than per-tool justification.
- **Sync throughout (5 samples)** — `awslabs--mcp-lambda-handler` (Lambda is sync per AWS event model), `baryhuang--mcp-server-aws-resources-python` (sync code-execution wrapper), `labeveryday--mcp_pdf_reader` (PyMuPDF + pytesseract sync), `marlonluo2018--pandas-mcp-server` (pandas sync), `misbahsy--video-audio-mcp` (`ffmpeg-python` sync). Rationale is consistently "underlying library is sync; wrapping in async would add thread overhead with no concurrency win" — exactly what the current description says.
- **Mixed (5 samples)** — `chroma-core--chroma-mcp`, `jlowin--fastmcp` (the framework itself accepts both forms), `modelcontextprotocol--servers` (different sub-packages — fetch async, git not), `shreyaskarnik--huggingface-mcp-server`, `sooperset--mcp-atlassian` (asyncio + anyio coexist).
- **Bridging deps observed** — `the-momentum--fhir-mcp-server` mentions `greenlet` for "sync/async bridging for SQLAlchemy-style upstream patterns" — a rare but real pattern.

The description is essentially accurate; the corpus visibility just confirms the three buckets aren't even — async throughout is dominant (~64% of supporting samples), sync ~20%, mixed ~16%. Worth folding the distribution observation into the description.

Sharpened text suggestion: "Whether tool handlers are sync or async, and what drives the choice. Cross-cutting because both FastMCP and the raw `mcp` Python SDK accept either form transparently:

- **Async throughout (dominant, ~16/25 supporting samples)** — Tool handlers are `async def`. Driven by async upstream client libraries (httpx, psycopg3 async, redis-py async, weaviate-client async, etc.) or FastMCP-default conventions. Test signal: `pytest-asyncio` with `asyncio_mode = 'auto'`.
- **Sync throughout (~5/25)** — Tool handlers are plain `def`. Forced when the underlying library is sync-only (`ffmpeg-python`, `PyMuPDF` + `pytesseract`, pandas, scikit-learn, DaVinci scripting API, Lambda's sync event model). Wrapping sync work in async would add thread overhead with no concurrency win.
- **Mixed (~5/25)** — The MCP SDK accepts both forms in the same server; some tools async (network calls), others sync (CPU work). Also occurs when asyncio and anyio styles coexist (`pytest-asyncio` + `pytest-anyio` declared together). Bridging libraries like `greenlet` surface when SQLAlchemy-style upstream patterns require sync/async glue."

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### Sample > Schema and types (role-level) — orthogonal-axes structure

The role contains paths along two distinct axes (mechanism vs library). 5 samples appear simultaneously under FastMCP-auto-derivation AND Pydantic-v2-models because the paths describe different aspects of one runtime choice. Sample count: 90 path-attachments across 7 paths but only ~58 unique samples. Recommendation: **fold the axis structure into role-level prose** (covered in description sharpening above). Do not propose splitting the role.

### Sample > Schema and types > Pydantic v2 models — four distribution clusters

Pydantic-v2 supporting samples cluster into four sub-patterns (transitive via FastMCP / hand-authored alongside FastMCP / transitive via raw SDK / pydantic-settings for config). 5 + 1 + 14 + 2 sample distribution. Fold into description (covered above). Do not propose split — the path captures "Pydantic v2 is present" which is a valid coarse-grain observation; finer-grain mechanism is captured by sibling paths.

### Sample > Schema and types > FastMCP auto-derivation from type hints — inference-vs-evidence sub-axis

Of 26 supporting samples, only ~4 surface direct evidence of `Annotated[Field(description=...)]` patterns or docstring-as-schema-source. The remaining 22 are inferred from "uses FastMCP." This is not a sub-pattern that warrants a path split, but **the corpus's confident framing exceeds the actual signal strength**, and the consolidated should acknowledge this. Fold caveat into description (covered above).

### Sample > Schema and types > Async model (cross-cutting) — distribution skew

Async-throughout dominates (~64%); sync-throughout is the minority (~20%); mixed sits between (~16%). The current path-level description gives equal billing to all three, but the corpus signal heavily favors async. Fold distribution into description (covered above), do not propose split — three sub-patterns are coherent, not three separate paths.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None proposed. The current 7 paths describe genuinely distinct things along the two axes (mechanism + library). The cross-axis overlap is a feature of the role's structure, not a sign of duplicated paths.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None proposed. The sub-axes within paths (Pydantic's four clusters, async's three sub-patterns) are better folded into descriptions than promoted to siblings. Splitting Pydantic-v2 into four sub-paths would force every Python sample to be re-classified across an axis the existing tree doesn't currently use, and the structural payoff is small versus the cost of restructuring at this stage.

A weaker case exists for splitting `Hand-authored tool schemas` into `(a) raw mcp SDK + hand-authored dicts` vs `(b) hand-rolled MCP runtime + dataclasses/TypedDict` — only `awslabs--mcp-lambda-handler` cleanly fits (b), so a split would be 12-vs-1, not worth the structural change. Description acknowledgment of the (b) sub-pattern is sufficient (covered above).

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

### `awslabs--openapi-mcp-server` currently under `Hand-authored tool schemas` better fits a (currently nonexistent) "spec-derived schema" framing

The sample's content under `Hand-authored tool schemas`: "Schemas auto-derived from external OpenAPI specs via `openapi-spec-validator` + `prance` — the most extreme 'schema is data' design in the corpus, registering tools with hand-built schema dicts at runtime rather than from Python type hints." This is operationally hand-authored at runtime (the server hand-builds the schema dicts the SDK then accepts) but conceptually spec-derived (no human writes the schemas; they materialize from upstream OpenAPI documents).

Cross-reference: under `Capability surface`, `awslabs--openapi-mcp-server` is correctly placed under `Spec-driven dynamic tool generation`. The same sample under `Schema and types` could either (a) stay where it is with a description-level acknowledgment that "hand-authored" includes "hand-built-from-spec at runtime," or (b) move to a new sibling path — but the depth pass should not propose new paths absent stronger cross-sample support, and only one sample fits this distinction in `Schema and types`.

Recommendation: keep the placement; have the consolidated reconciler decide whether the description on `Hand-authored tool schemas` should mention this case explicitly, vs surfacing it only at the `Capability surface > Spec-driven dynamic tool generation` path.

### `chroma-core--chroma-mcp` currently under `Pydantic v2 models` is a borderline placement

The sample's content: "Pydantic via the MCP SDK (pulled in transitively rather than declared explicitly); schemas auto-derived from signatures per MCP SDK idiom." Pydantic isn't a direct or even declared dep — it's only present because `mcp[cli]` pulls it. This is the same evidence pattern as `voska--hass-mcp` ("Pydantic arrives via the `mcp[cli]` extra"). Both are genuinely under the path's umbrella per the current description ("via raw `mcp` SDK") but they barely qualify — the path's framing of "explicit hand-authored Pydantic models" doesn't fit either sample. Description sharpening (Cluster A in the Pydantic refinement above) addresses this without requiring a sample move.

Recommendation: keep the placements; description sharpening to acknowledge "transitive-only" cluster covers the framing gap.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Inference vs observation gap

Across all 7 paths, the corpus signal is conspicuously thin — sample after sample says "FastMCP auto-derives schemas," "schemas hand-authored likely," "schema strategy not surfaced," "Pydantic via the SDK; specifics not captured." The Schema-and-types role is a domain where the truth lives in the framework or SDK, not the consumer repo, so a sample analyst examining a typical FastMCP-based MCP server has only the framework's behavior to report. **This isn't a defect of the consolidation — it's a property of the domain.** The depth-pass refinements should acknowledge this so consolidated readers know that path placements largely reflect runtime-choice inference, not direct schema-mechanism observation.

This is the most important cross-corpus observation visible only at full role scope: the role's evidence quality is markedly thinner than (e.g.) Server runtime, where samples surface specific dep-pin styles and import patterns directly. Reconcilers should weigh this when deciding whether to invest more depth-pass cycles on this role versus higher-signal roles.

### Two-axis structure (mechanism × library) recurs cross-corpus

The 5-sample overlap between FastMCP-auto-derivation and Pydantic-v2-models, the way `awslabs--openapi-mcp-server` straddles spec-derived/hand-authored/Pydantic, and the way Zod fills both schema and config-validation duties in TS samples — all point to the role being structured along two orthogonal axes (schema source mechanism × validation library). This is the single most impactful structural finding from the depth pass and warrants a role-level prose revision (see Description sharpenings, role-level entry).

### Path-vs-runtime tight coupling reaffirmed

Every sample's choice on `Schema and types` paths is fully predicted by its `Server runtime` choice:

- FastMCP runtime → FastMCP auto-derivation + Pydantic v2 (transitive)
- Raw MCP SDK runtime → Pydantic v2 (transitive via `mcp[cli]`) + hand-authored OR auto-derived from typed signatures
- TypeScript SDK runtime → Zod
- Go SDK runtime → Go automatic schema generation
- Rust SDK runtime → Rust schema crate (or unsurfaced)
- Hand-rolled runtime → Hand-authored tool schemas (dataclasses/TypedDict)

The current role-level description states this ("Tightly coupled to the runtime choice") but the cross-corpus visibility makes it concrete: **knowing the runtime predicts the schema-and-types path with high accuracy**. The role's information value is mostly in the validation-library axis (Pydantic vs Pydantic-settings vs Zod), the async/sync choice, and the few exceptions where schema is spec-derived rather than language-derived. Reconciler may consider whether paths whose presence is fully predicted by runtime should be folded into the runtime role's description, leaving Schema-and-types for the orthogonal information (validation library, async model, spec-derived corner cases). This is a structural change beyond the depth pass's scope, but worth flagging.
