# Depth Pass Refinements — Sample > Server runtime

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role. All 22 paths examined (one had zero supporting samples — none did; every path had at least one). Total sample evidence consumed: ~31 KB across 104 sample sections.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### Sample > Server runtime > Python with FastMCP

The existing description correctly covers the 1.x-via-SDK vs 2.x standalone split and varied pin discipline, but it misattributes the "FastMCP ships its own HTTP transport stack" line as universal — most of the 23 samples don't surface that explicitly, only `jlowin--fastmcp` (the framework itself) does. It also folds three distinct version-line patterns (1.x via `mcp[cli]`, 2.x standalone, 3.x emerging) into a single "two major lines" framing, when 3.x is now visibly distinct (`sandraschi--email-mcp`: `fastmcp>=3.1.0,<4`; `awslabs--openapi-mcp-server`: `fastmcp>=3.2.2,<4`; `jlowin--fastmcp`: "version 3.x").

Cross-corpus evidence:

- 1.x-via-SDK: `misbahsy--video-audio-mcp` (`mcp[cli]>=1.9.0`, "Built with FastMCP framework"), `marlonluo2018--pandas-mcp-server` (`fastmcp >= 1.0.0`).
- 2.x standalone: 14+ samples, with pin styles ranging from exact (`fastmcp == 2.7.0` qdrant, `fastmcp == 2.13.1` mahdin75, `fastmcp == 2.12.3` thenets) to bounded (`fastmcp>=2.0.0,<3.0.0` ClickHouse, `fastmcp>=2.14,<3` motherduckdb, `>=2.7.0,<2.11` jbeno) to lower-bound only (`fastmcp >= 2.14.1` zilliztech).
- 3.x: `sandraschi--email-mcp`, `awslabs--openapi-mcp-server`, `jlowin--fastmcp` itself.
- "Schema auto-derivation from type hints" surfaces in 4+ samples explicitly.

Sharpened text suggestion: split the version-line discussion into three distinct generations rather than two. Drop the "framework ships HTTP stack so consumers don't" line — it's a fact about the framework but not an observable in most consumer samples. Keep the pin-discipline observations but tag them by generation since the bounded ranges (`<3`, `<2.11`, `<4`) all signal upstream churn at major-version boundaries.

### Sample > Server runtime > Python with raw MCP SDK

Two patterns in the existing description don't survive cross-corpus inspection:

- "Authors who pick this layer typically wrap their own CLI with `click`, validate config with `pydantic-settings`, and use `rich` for non-protocol output" — this composite framing fits exactly one sample (`DiversioTeam--clickup-mcp`); most raw-SDK samples have leaner stacks (`reminia--zendesk` 3 deps, `awslabs--bedrock-kb-retrieval` 4 deps, `voska--hass-mcp` 2 deps). The description over-generalizes from a single sample.
- "Module-level entry (`python -m package.server`) is common rather than a console script" — observed in `PagerDuty--pagerduty-mcp-server` and a few others, but not "common." Several samples ship console scripts.

What is genuinely cross-corpus:

- `mcp[cli]` extra is widely used: 8 samples explicitly pin `mcp[cli]>=N` (awslabs x2, chroma, crystaldba, datalayer x2, redis, voska). The `[cli]` extra brings Inspector tooling — that's the pull for it, not raw protocol primitives.
- Lean dep surfaces are recurrent: 2-4 runtime deps observed in 5+ samples. Worth elevating from "lean dep sets observed" footnote to a primary characterization.
- "Anthropic Claude Agent SDK" phrasing surfaces in `feiskyer`, `pragmar`, `redis`, `opensearch-project`, `isaaccorley` — these are README-template phrasings rather than actual Claude Agent SDK adoption. The description should clarify this so readers don't conflate it with the dedicated `Python with Anthropic Claude Agent SDK` path.

Sharpened text suggestion: drop the click/pydantic-settings/rich composite. Replace with: "`mcp[cli]` extra is the common variant when the Inspector launcher is wanted; bare `mcp` appears when even Inspector tooling is unwanted. Dependency surfaces tend toward minimalism — 2-4 runtime packages is typical, often just `mcp[cli]` plus the upstream library being wrapped (boto3, httpx, zenpy, kubernetes client). Tool handlers are typically `async def` since the low-level SDK is async-native, but sync handlers also occur when the underlying client library is sync (boto3, zenpy, Blackmagic DaVinci scripting). Some samples reference 'Anthropic Claude Agent SDK conventions' in their READMEs as boilerplate phrasing — the actual dependency is plain `mcp` / `mcp[cli]`, not the Claude Agent SDK; see the dedicated path for actual Claude Agent SDK pairings."

### Sample > Server runtime > Python with both MCP SDK and FastMCP declared

Existing description states "Typically FastMCP runs the server surface while `mcp[cli]` provides developer tooling." Cross-corpus evidence does not support "typically" — the rationale is explicit in only 2 samples (`sooperset--mcp-atlassian` "transitional state from a project that predates FastMCP," `openags--paper-search-mcp` "FastMCP for server surface; `mcp[cli]` kept for dev/inspector tooling"). For 3 of 6 samples (`awslabs--aws-api-mcp-server`, `awslabs--mcp`, `normaltusker--kotlin-mcp-server`) the rationale is undocumented at sample level.

The current description should soften the "typically" framing to "rationale varies — observed cases include FastMCP-as-runtime + raw-mcp-for-Inspector and partial-migration transitional state; not all samples surface the rationale." Otherwise the current description is fine.

### Sample > Server runtime > Python with hand-rolled MCP

The existing description folds three quite distinct patterns under one description:

- Subprocess CLI wrapping with per-Dockerfile envs (`FuzzingLabs--mcp-security-hub`)
- Lambda HTTP shim with custom decorator ergonomics (`awslabs--mcp-lambda-handler`)
- Multi-server monorepo dispatcher with per-sub-server SDK choice (`pathintegral-institute--mcp.science`)

Only the second carries the "decorator-style ergonomics (`@mcp.tool()`) reproduced atop the custom implementation" claim — that's specific to `awslabs--mcp-lambda-handler`, not the cohort.

Sharpened text suggestion: replace the "Decorator-style ergonomics … can be reproduced atop the custom implementation" generalization with a cohort summary identifying the three sub-patterns: serverless (Lambda event-bridge), CLI subprocess wrapper (per-tool dependency islands in Dockerfiles), and dispatcher root with per-sub-server SDK choice. The unifying property is "no `mcp` or `fastmcp` runtime dep at the relevant scope," and the motivation is substrate fit (Lambda event JSON, Dockerfile-per-tool, or no SDK at root because each sub-server picks its own).

### Sample > Server runtime > Node.js / TypeScript with official MCP SDK

Existing description states the SDK "bundles its own HTTP and stdio transport plumbing — runtime choice doesn't pull in a separate web framework." Cross-corpus evidence partly contradicts this — multiple samples explicitly add a web framework on top of the SDK's transport classes:

- Hono: `cyanheads--git-mcp-server`, `cyanheads--perplexity-mcp-server` (both samples explicit)
- Express: `makenotion--notion-mcp-server` (Express 4.21.2 explicit)
- The SDK's `StreamableHTTPServerTransport` and `StdioServerTransport` are mentioned only in `ahmedmustahid--postgres-mcp-server`

The SDK provides transport classes but most non-trivial HTTP servers add Hono or Express for routing/middleware. Zod for validation is near-universal (5+ explicit references). Pino logging surfaces in 2 samples.

Sharpened text suggestion: revise "SDK bundles its own HTTP and stdio transport plumbing — runtime choice doesn't pull in a separate web framework" to "SDK provides `StdioServerTransport` and `StreamableHTTPServerTransport` classes the server instantiates, but a web framework (Hono or Express most commonly) is frequently added on top for routing, middleware, and CORS rather than wired against the bare transport class." Add Zod-as-typical-validator and Pino-as-frequent-logger as cross-corpus stack constants.

### Sample > Server runtime > Rust with rmcp / rust-mcp-sdk

Existing description bundles two genuinely distinct ecosystem patterns ("rmcp" line and "rust-mcp-sdk" line) and lists features from across the 4 samples. Most claims survive the corpus check, but a few are sample-specific over-generalizations:

- The builder pattern `ServerConfig::with_name().with_version().with_tool()` and `mcpr generate-project` scaffold are specific to `conikeec--mcpr`, not the cohort.
- "Generic-adapter shapes also exist that turn external schema (GraphQL operation definitions) into MCP tools at runtime" — this is `apollographql--apollo-mcp-server` only, and that sample says specifics aren't extracted.

Sharpened text suggestion: keep the two-ecosystem framing but attribute features to their sample line. Keep the "single static binary, no runtime deps" and "performance / memory-safety" framings — those appear in 2+ samples (elastic, rust-mcp-stack) and are the consistent pull. Remove the universal-sounding builder-pattern claim.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### Sample > Server runtime > Python with FastMCP — version-line sub-axis

Three distinct version generations in active use, each with its own pin discipline:

- 1.x-via-`mcp[cli]` extra (legacy in-SDK form): 2 samples (`misbahsy--video-audio-mcp`, `marlonluo2018--pandas-mcp-server`)
- 2.x standalone: ~14 samples
- 3.x: 2-3 samples (`sandraschi--email-mcp`, `awslabs--openapi-mcp-server`, plus the framework itself)

Sample count for the 1.x-via-SDK and 3.x sub-axes is small (2-3 each), so a bucket split is not warranted. Recommend folding the three-generation distinction into the path description as an explicit sub-axis rather than the current "two major lines" framing.

### Sample > Server runtime > Python with raw MCP SDK — `mcp[cli]` vs bare `mcp` sub-axis

`mcp[cli]` extra: 8 samples explicit (awslabs x2, chroma, crystaldba, datalayer x2, redis, voska)
Bare `mcp`: 5 samples explicit (designcomputer, ktanaka101, twolven, modelcontextprotocol--servers references, reminia)
Unspecified: ~16

The `[cli]` extra adds Inspector tooling. This is a meaningful sub-axis — fold into description rather than split.

### Sample > Server runtime > Node.js / TypeScript with official MCP SDK — HTTP framework sub-axis

When the server speaks HTTP, ~3 explicit samples add Hono or Express on top of the SDK's transport class. Most HTTP-capable Node samples don't surface what they wrap the transport with at sample level. Sample count too low to propose a split — fold into description.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None proposed. Each sibling path captures a genuinely distinct alternative — the runtime/SDK choices map to different downstream constraints (transport options, async model, distribution channel, dependency footprint).

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None proposed. The candidate splits surfaced by the depth pass (FastMCP version generations, raw-SDK `[cli]` vs bare) all have at least one sub-cluster too small (2-3 samples) to justify splitting at this stage. Description-level sub-axis treatment is the appropriate level of intervention given Pass-3 convergence.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

### `duolingo--slack-mcp.md`

Currently under: `Python with Anthropic Claude Agent SDK`
Better fits: `Python with both MCP SDK and FastMCP declared` or possibly a new "Python with FastMCP + Claude Agent SDK" path

Evidence: the sample's content under this path explicitly says "FastMCP 2.x as the MCP runtime — `fastmcp>=2.13.0` declared in pyproject.toml." The Claude Agent SDK is paired with MCP but is not the runtime substrate here — FastMCP is. The current path description ("a less common path where the agent SDK is the foundation and MCP capabilities are layered on top") doesn't fit a sample where FastMCP is the foundation and the Claude Agent SDK is one of several deps. Reconciler should consider moving this to the `both MCP SDK and FastMCP declared` path (if the project also pulls raw `mcp`) or simply to `Python with FastMCP` (if it doesn't), since the Claude Agent SDK pairing is captured at a different role (likely Capability surface or Runtime composition).

> Note for reconciler: this is the only sample under `Python with Anthropic Claude Agent SDK`. If it moves, the path becomes empty — consider removing the path or renaming it to capture the actual pattern (FastMCP runtime paired with Claude Agent SDK as a capability-layer dep).

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

- **Python ecosystem dominates by sample count (62 of 104 — 60%)** but is split four ways (raw SDK 29, FastMCP 23, dual 6, hand-rolled 3, Claude Agent SDK 1, FastMCP pre-2.x 1). This concentration matters for downstream-role analysis: any "what does the Python MCP server look like" question is really four sub-questions.
- **Node.js / TypeScript SDK is unusually monolithic at this stage** — 21 samples on one path, with single-sample tails (Bun, Cloudflare Workers, Next.js, monorepo, custom SDK composition) showing the path edges. The TS ecosystem shows less SDK fragmentation than Python.
- **Go is the most fragmented per-sample ecosystem** — 7 Go samples spread across 3 paths (mark3labs 2, metoro 1, custom 4). The "custom" plurality is unusual; Go authors tend to hand-roll JSON-RPC rather than depend on a community SDK. Worth flagging — this generalizes the "single-binary distribution → less SDK reuse pull" hypothesis.
- **Pin discipline correlates with framework maturity rather than language**. FastMCP samples show the widest spread (exact pins, narrow ranges, caret upper bounds) because the framework is still evolving major versions; raw `mcp` SDK samples show looser pins because the API surface is smaller. Rust and Go samples show toolchain pins (`rust-toolchain.toml`, `go.mod` directives) but library pins are less varied — the SDK ecosystems are simpler.
- **Single-sample paths cluster around hosted/edge/non-process runtimes** (Cloudflare Workers, Next.js, .NET, Kotlin, DuckDB extension, Bun, monorepo, custom SDK composition, FastMCP pre-2.x, Claude Agent SDK, Clojure variants). This is a meaningful corpus shape — the long tail is "where the substrate isn't a vanilla local subprocess." Possibly worth a meta-observation in the role description about why the long tail is structured this way.
- **"Anthropic Claude Agent SDK" appears as boilerplate phrasing in 5+ raw-MCP-SDK sample READMEs** without the Claude Agent SDK actually being a dependency. Authors copy template language from the official MCP scaffold. Worth flagging in the raw-SDK path description so readers don't conflate it with actual Claude Agent SDK adoption.
- **Schema derivation strategy correlates strongly with runtime path** but is described inconsistently across paths: FastMCP samples emphasize "auto-derived from type hints"; raw-SDK samples emphasize "hand-authored"; Go samples emphasize "from native struct fields"; Rust samples emphasize "compile-time-checked." This is one role consistently described per-path but might benefit from being abstracted to a sibling role at some future depth pass.
