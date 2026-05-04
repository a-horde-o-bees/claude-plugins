# Sample

Stage-2 T2 merge of m2 (bins 3+4+12) + m5 (bin 8), 32 samples total.

## Identification

### License

- MIT — most samples; [`conikeec--mcpr`], [`crystaldba--postgres-mcp`], plus the bin-8 majority
- Apache-2.0 — [`cloudflare--mcp-server-cloudflare`], [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`microsoft--playwright-mcp`]
- BSD-3-Clause — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- GPL-3.0 — [`ckreiling--mcp-server-docker`] (called out as unusual: ecosystem skews MIT/Apache)
- Dual-license Apache-2.0 (new) / MIT (existing) — [`modelcontextprotocol--kotlin-sdk`], [`modelcontextprotocol--servers`]; contribution-time gate migrates the repo forward without touching prior commits — relicensing-forward strategy rather than relicensing existing material

### Ownership / authorship class

#### First-party vendor server

Vendor of the underlying API ships its own MCP server: Stripe ships from `stripe/agent-toolkit` [`stripe--agent-toolkit`]; Notion publishes `@notionhq/notion-mcp-server` (ships `CLAUDE.md` in repo) [`makenotion--notion-mcp-server`]; Microsoft publishes `@playwright/mcp` [`microsoft--playwright-mcp`]. Supabase community-org under company watch — `supabase-community/supabase-mcp` is community-canonical with vendor signaling [`supabase-community--supabase-mcp`].

#### Official protocol-org reference

Maintained by the MCP organization. `modelcontextprotocol/servers` is the canonical reference-server monorepo [`modelcontextprotocol--servers`]; `modelcontextprotocol/kotlin-sdk` is the official Kotlin SDK maintained with JetBrains collaboration [`modelcontextprotocol--kotlin-sdk`].

#### Community-canonical without vendor entry

Atlassian has no first-party MCP — `sooperset/mcp-atlassian` (5k stars) is the de facto standard [`sooperset--mcp-atlassian`]. Turso similarly: `spences10/mcp-turso-cloud` is community-built, not under `tursodatabase/*` [`spences10--mcp-turso-cloud`]. Ghost CMS [`thenets--ghost-mcp`] (1 star, very new). Grafana Loki [`tumf--grafana-loki-mcp`].

#### Domain-specific community

`teaguesterling/duckdb_mcp` — DuckDB extension built externally to the DuckDB project [`teaguesterling--duckdb_mcp`]. `the-momentum/fhir-mcp-server` — FHIR-agnostic healthcare server, not tied to any single FHIR vendor [`the-momentum--fhir-mcp-server`].

#### Third-party SDK / framework author

Independent maintainers building MCP plumbing on top of the spec. `mark3labs/mcp-go` and `metoro-io/mcp-golang` are competing Go SDKs from independent authors [`mark3labs--mcp-go`, `metoro-io--mcp-golang`].

#### Hobbyist / single-developer server

Small repos by individual authors targeting niche workflows. `pandas-mcp-server` (~40 stars) [`marlonluo2018--pandas-mcp-server`], `video-audio-mcp` (71 stars, "6 Commits" on main, possibly early-stage) [`misbahsy--video-audio-mcp`].

### Repository status

- Active main-branch development is the norm
- Archived repository — [`conikeec--mcpr`] archived as of February 8, 2026; v0.2.0 yanked due to SSE issues, v0.2.3+ recommended; pre-archive Rust libs may already be superseded
- Archived servers physically moved to a sibling `servers-archived` repo rather than flagged in-place — keeps the demonstration set curated [`modelcontextprotocol--servers`]

### Maturity signals

Star-count spread is enormous within the corpus: 31k+ [`microsoft--playwright-mcp`], 8.6k [`mark3labs--mcp-go`], 5,000 [`sooperset--mcp-atlassian`], 3,600 [`cloudflare--mcp-server-cloudflare`], 2,600 [`crystaldba--postgres-mcp`], 2,600 [`supabase-community--supabase-mcp`], 1,500 [`stripe--agent-toolkit`], 1,200 [`metoro-io--mcp-golang`], ~1,000 [`datalayer--jupyter-mcp-server`], 701 [`ckreiling--mcp-server-docker`], 350 [`conikeec--mcpr`], 207 [`cyanheads--git-mcp-server`], 77 [`the-momentum--fhir-mcp-server`], 71 [`misbahsy--video-audio-mcp`], 47 [`teaguesterling--duckdb_mcp`], ~40 [`marlonluo2018--pandas-mcp-server`], ~25 [`datalayer--earthdata-mcp-server`], 25 [`tumf--grafana-loki-mcp`], 22 [`cyanheads--perplexity-mcp-server`], 15 [`spences10--mcp-turso-cloud`], 1 [`thenets--ghost-mcp`].

Star count vs engineering quality: high-star community canonicals are backlog-loaded (171 issues + 91 PRs at 5k stars [`sooperset--mcp-atlassian`]); completeness of structure does not track stars — [`thenets--ghost-mcp`] (1 star) has full Docker Compose dev stack, JWT renewal, dual-API split; a 71-star, 6-commit repo can carry 30+ pytest-tested tools [`misbahsy--video-audio-mcp`]; very large-community repos may leave testing/CI specifics unsurfaced even at 31k+ stars [`microsoft--playwright-mcp`]. Read engineering rigor from the artifacts (test count, lint config, CI presence), not from popularity.

Release velocity is a stronger signal than commit count — `microsoft--playwright-mcp` has 60 releases at 31k stars; `mark3labs--mcp-go` released v0.48.0 indicating sustained iteration.

## Artifact category

The corpus is not uniform — several variants are worth distinguishing beyond "an MCP server".

### Single-purpose MCP server

The default shape — one server fronting one domain. Examples: [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`baryhuang--mcp-server-aws-resources-python`], [`makenotion--notion-mcp-server`] (Notion API), [`microsoft--playwright-mcp`] (browser automation), [`marlonluo2018--pandas-mcp-server`] (DataFrame analysis), [`misbahsy--video-audio-mcp`] (ffmpeg wrapper), plus most other samples.

### Server-framework / SDK (library, not server)

A library *for* building MCP servers, not itself a server. No host-config integration documented at the SDK level — applications using the SDK handle that.

- [`awslabs--mcp-lambda-handler`] — library for building Lambda-hosted MCP servers; re-implements MCP wire format on Lambda events; user writes their own server using its `@mcp.tool()` decorator and `mcp.handle_request(event, context)` dispatch
- [`conikeec--mcpr`] — Rust library; this repo *is* the SDK; ships `mcpr generate-project` CLI to scaffold new implementations and reduce boilerplate; ships mock transport for offline testing; ServerConfig builder pattern
- [`mark3labs--mcp-go`] — Go SDK
- [`metoro-io--mcp-golang`] — alternate Go SDK
- [`modelcontextprotocol--kotlin-sdk`] — Kotlin Multiplatform SDK

#### Competing SDKs in the same language

Two independent Go SDKs (`mark3labs/mcp-go` at 8.6k stars; `metoro-io/mcp-golang` at 1.2k stars) coexist with overlapping but non-identical feature sets — Go ecosystem has not consolidated on a canonical SDK [`mark3labs--mcp-go`, `metoro-io--mcp-golang`].

### Spec-driven server (tools materialize from external schema)

[`awslabs--openapi-mcp-server`] generates tools, resources, and prompts at server start by parsing one or more OpenAPI specs. No hand-authored tool definitions. Major design axis vs code-driven servers — implications for docs drift (spec is source of truth), testing (every spec change is a contract change), and LLM behavior (tool descriptions inherit spec quality).

### Code-as-tool server (one tool wraps an interpreter)

[`baryhuang--mcp-server-aws-resources-python`] exposes a single `exec boto3` tool with AST-validation sandbox + import allowlist (boto3, operator, json, datetime, pytz, dateutil, re, time). Inverts the per-API enumeration default — one flexible code-execution tool versus N hand-enumerated tools.

### Multi-server monorepo (umbrella)

- [`awslabs--mcp`] — 40+ server monorepo with `src/<service>/` per server, namespace-prefixed PyPI packages (`awslabs.<service>-mcp-server`), and central dev tooling at root. Preview "aggregated" server (`aws-mcp-server`) bundles SOPs + CloudTrail audit
- [`cloudflare--mcp-server-cloudflare`] — Turbo monorepo with 14 domain Workers + shared `@repo/mcp-common` scaffolding
- [`stripe--agent-toolkit`] — multi-package monorepo: SDKs (Python + TS), AI-framework integrations (Vercel), billing primitives, and MCP — MCP treated as one integration channel among peers, not the whole product
- [`modelcontextprotocol--servers`] — multi-server reference monorepo: seven reference servers (Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time) under `src/<server>/`, with TS and Python peers each using their own distribution channel (npm vs PyPI) and their own Docker image. Reference vs hosted positioning forces visible curation discipline (license posture, archival, per-server Dockerfile uniformity)

### MCP-as-database-extension

[`teaguesterling--duckdb_mcp`] — running MCP as a DuckDB C++ extension; PRAGMAs and SQL drive both server and client modes. Blurs database-vs-tool-registry boundary.

### Server-as-extension vs server-as-standalone

[`datalayer--jupyter-mcp-server`] — dual deployment: standalone MCP server OR Jupyter Server extension mounted inside Jupyter process. Deployment axis distinct from the artifact-category split above.

## Language and runtime

### Python

The dominant language: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`marlonluo2018--pandas-mcp-server`], [`misbahsy--video-audio-mcp`], [`modelcontextprotocol--servers`] (Python half), [`sooperset--mcp-atlassian`] (99.3%), [`the-momentum--fhir-mcp-server`] (97%), [`thenets--ghost-mcp`] (92.5%), [`tumf--grafana-loki-mcp`] (93.2%).

#### Python version floors

- `>=3.10` — [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`chroma-core--chroma-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`marlonluo2018--pandas-mcp-server`], [`modelcontextprotocol--servers`] (git, fetch, time), [`sooperset--mcp-atlassian`], [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`]
- `>=3.11` — [`blazickjp--arxiv-mcp-server`] (suggests use of newer typing / exception-group features)
- `>=3.12` — [`crystaldba--postgres-mcp`] (ruff target-version intentionally lags at `py39` as style target separate from runtime floor), [`the-momentum--fhir-mcp-server`]
- `>=3.13` — aggressive; [`misbahsy--video-audio-mcp`] despite being a 6-commit repo
- Pinned via `.python-version` file, value not surfaced — [`ckreiling--mcp-server-docker`]
- Not surfaced — [`baryhuang--mcp-server-aws-resources-python`]

### TypeScript / JavaScript

- Node.js — [`cyanheads--git-mcp-server`] (Node >=20 + Bun >=1.2 dual runtime), [`cyanheads--perplexity-mcp-server`] (Node >=18), [`makenotion--notion-mcp-server`] (TS 5.8.2), [`microsoft--playwright-mcp`] (TypeScript 62.2%), [`modelcontextprotocol--servers`] (~69% of repo is TS), [`spences10--mcp-turso-cloud`] (92.4%), [`supabase-community--supabase-mcp`] (99.5%)
- Cloudflare Workers (V8 isolate runtime, not Node) — [`cloudflare--mcp-server-cloudflare`]

### Go

- Go 1.25.5+ specified in `go.mod` — [`mark3labs--mcp-go`]
- Go version constraint not surfaced in README; runtime floor less explicit — [`metoro-io--mcp-golang`]

### Rust

[`conikeec--mcpr`].

### Kotlin / JVM Multiplatform

[`modelcontextprotocol--kotlin-sdk`] — Kotlin 2.2+, Java 11+ (JVM target); multiplatform: JVM, Native, JS, Wasm. Optional Ktor server. Coroutine-friendly APIs throughout.

### Clojure / JVM

[`bhauman--clojure-mcp`] runs on JDK 17+ (inferred), Clojure 99.9% of source. Distributed as a Clojure tools install (`clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp`).

### C++ (DuckDB extension)

[`teaguesterling--duckdb_mcp`] — C++ (73.7%) + Shell (13.1%) + Python (10.6%) + minor TS/JS/HTML; built as a C++ DuckDB extension with multi-language helpers.

### Multi-language repos

- TypeScript (51.9%) + Python co-primary in one monorepo, parallel PyPI + npm publishing — [`stripe--agent-toolkit`]
- TS + Python as first-class peers in one repo — [`modelcontextprotocol--servers`]
- See [`teaguesterling--duckdb_mcp`] above

### Multi-runtime support

Dual-runtime auto-detection (Node + Bun) — [`cyanheads--git-mcp-server`] is the only sample running on more than one runtime; treats Node ≥20 and Bun ≥1.2 as first-class peers.

### System-binary dependency

A class of servers depends on an out-of-band system binary not installable through PyPI/npm. Forms a server class where Docker distribution is the only self-contained option.

- ffmpeg required on PATH — README documents an `apt-get install ffmpeg` step in its GitHub Actions YAML example [`misbahsy--video-audio-mcp`]
- Same shape exists for Tesseract in PDF OCR servers (referenced by `misbahsy--video-audio-mcp` as a peer pattern)

## SDK / framework

The Python ecosystem splits along "raw `mcp`", "FastMCP", or "custom (no SDK)"; TypeScript samples concentrate on `@modelcontextprotocol/sdk` plus auxiliary HTTP/validation libraries.

### Python — raw `mcp` SDK

- `mcp[cli]>=1.23.0` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `mcp[cli]==1.6.0` (exact pin, unusually tight for a 2025 vendor server) — [`chroma-core--chroma-mcp`]
- `mcp[cli]>=1.25.0` — [`crystaldba--postgres-mcp`] ("deliberate use of low-level hooks for custom tool gating")
- `mcp[cli]>=1.2.1` — [`datalayer--earthdata-mcp-server`]
- `mcp[cli]>=1.10.1` — [`datalayer--jupyter-mcp-server`] (also pulls `mcp.server.fastmcp` via the extra)
- `mcp` (raw, version not surfaced) — [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`]
- Raw MCP Python SDK (FastMCP not surfaced) — [`ckreiling--mcp-server-docker`]
- `mcp>=1.0.0` (git), `mcp>=1.1.3` (fetch); low-level `Server` class. Reference Python servers (git, fetch, time) use raw `mcp` SDK exclusively — no FastMCP. Reference set deliberately prioritizes low-level SDK coverage over developer convenience [`modelcontextprotocol--servers`]

### Python — FastMCP

- `fastmcp>=3.2.2,<4` — [`awslabs--openapi-mcp-server`]
- Dual `mcp>=1.23.0` AND `fastmcp>=3.0.1` — [`awslabs--mcp`] (sampled `aws-api-mcp-server/pyproject.toml`); inferred via `FASTMCP_LOG_LEVEL` env-var convention
- FastMCP 2.x — [`the-momentum--fhir-mcp-server`]
- FastMCP 2.12.3 (explicit precise pin) — [`thenets--ghost-mcp`]
- FastMCP, version not surfaced — [`tumf--grafana-loki-mcp`]
- `mcp>=1.8.0,<2.0.0` and `fastmcp>=2.13.0,<2.15.0` (likely historical: predates FastMCP, migrated partially) — [`sooperset--mcp-atlassian`]
- FastMCP 1.x via `fastmcp >= 1.0.0` lower-bound pin (looser than 2.x-pinning servers) — [`marlonluo2018--pandas-mcp-server`]
- FastMCP-style usage via `mcp[cli]>=1.9.0` — `[cli]` extra installs FastMCP-style helpers; README declares "Built with FastMCP framework"; likely the FastMCP-1.x-via-SDK path (`from mcp.server.fastmcp import FastMCP`) rather than standalone FastMCP 2.x [`misbahsy--video-audio-mcp`]

### Python — custom (no MCP SDK)

[`awslabs--mcp-lambda-handler`] depends on neither `mcp` nor `fastmcp` — re-implements protocol wire format directly against Lambda events. Smallest dependency footprint of any awslabs sub-server (3 deps: python-dateutil, boto3, botocore).

### TypeScript SDK + supporting libraries

- `@modelcontextprotocol/sdk` versions: ^1.29.0 [`cyanheads--git-mcp-server`], ^1.15.0 [`cyanheads--perplexity-mcp-server`], ^1.25.1 [`makenotion--notion-mcp-server`]
- Hono for HTTP layer — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- Express 4.21.2 + axios 1.8.4 + openapi-client-axios 7.5.5 + Zod 3.24.1; tsc + esbuild build — [`makenotion--notion-mcp-server`]
- Pino structured logging + tsyringe DI + optional OpenTelemetry — [`cyanheads--git-mcp-server`]
- TS reference servers use the official SDK — [`modelcontextprotocol--servers`]
- MCP SDK + Playwright; `createConnection()` programmatic API — [`microsoft--playwright-mcp`]

### Cloudflare Workers stack

Workers-native (no Node SDK) with Turbo monorepo + internal `@repo/mcp-common` shared scaffolding — [`cloudflare--mcp-server-cloudflare`]; 14 domain Workers factor common server concerns into a shared package.

### Go SDKs

- `mark3labs/mcp-go` — functional options pattern (`WithToolCapabilities()`, `WithTaskCapabilities()`, `WithMaxConcurrentTasks()`, `RegisterSession()`) [`mark3labs--mcp-go`]
- `metoro-io/mcp-golang` — registration methods (`RegisterTool()`, `RegisterPrompt()`, `RegisterResource()`) [`metoro-io--mcp-golang`]

Two Go SDKs choose different idioms for the same language — different ergonomic choices coexist.

### Kotlin SDK

[`modelcontextprotocol--kotlin-sdk`] — modular artifact structure: `kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, `kotlin-sdk` (umbrella). No transitive Ktor dependencies — developers specify Ktor engines independently. Coroutine-friendly APIs.

### Rust SDK

Custom MCP library (this repo *is* the SDK) — [`conikeec--mcpr`].

### Non-Python protocols

[`bhauman--clojure-mcp`] uses Anthropic's MCP plus nREPL for REPL-driven evaluation transport — JSON-RPC framing inside an nREPL connection.

## Transport

### stdio

Dominant default: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`ckreiling--mcp-server-docker`], [`datalayer--earthdata-mcp-server`], [`marlonluo2018--pandas-mcp-server`], [`misbahsy--video-audio-mcp`], [`modelcontextprotocol--servers`] (all reference servers), [`spences10--mcp-turso-cloud`] (stdio inferred, never named in README), [`thenets--ghost-mcp`] (stdio implied by `uvx`).

[`awslabs--mcp`] explicitly notes SSE was removed on 2025-05-26; "Streamable HTTP" planned replacement is in-development. Wholesale SSE removal with a documented date — deliberate transport-narrowing rather than maintaining both during transition.

### HTTP (API Gateway → Lambda)

[`awslabs--mcp-lambda-handler`] — inherently HTTP, no stdio path. The MCP-over-HTTP endpoint (`/mcp`) is an API Gateway route.

### HTTP-only (managed cloud endpoint)

[`supabase-community--supabase-mcp`] — HTTP is canonical mode, no stdio. Managed cloud endpoint primary.

### nREPL (REPL-as-transport)

[`bhauman--clojure-mcp`] — JSON-RPC inside nREPL connection. REPL-as-transport is unusual for MCP; entry point selection at launch lets the same artifact serve CLI, Claude Desktop, or other MCP clients with environment-specific connection patterns.

### stdio + SSE

- [`crystaldba--postgres-mcp`] — default stdio, `--transport=sse` flag
- [`conikeec--mcpr`] — both in same library (WebSocket planned but unimplemented)
- [`tumf--grafana-loki-mcp`] — stdio + SSE selected via CLI flag/default
- [`sooperset--mcp-atlassian`] — SSE primary; HTTP support mentioned. Likely env-var or subcommand driven
- [`microsoft--playwright-mcp`] — stdio default + SSE/HTTP when `--port` is set

### stdio + Streamable HTTP

- [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`datalayer--jupyter-mcp-server`]
- [`makenotion--notion-mcp-server`] — stdio (default) + Streamable HTTP (configurable port, default 8080)

### Three-transport servers (stdio + SSE + HTTP)

- [`mark3labs--mcp-go`] — Stdio + SSE + Streamable HTTP

### Four+-transport SDKs

- [`metoro-io--mcp-golang`] — Stdio + HTTP (stateless request-response) + Gin framework integration + SSE + custom transport support + HTTPS with custom auth (experimental, in progress)
- [`modelcontextprotocol--kotlin-sdk`] — Stdio + Streamable HTTP (single endpoint, optional JSON-only or SSE) + SSE + WebSocket + ChannelTransport (local testing)

### Streamable HTTP + SSE on same artifact

[`cloudflare--mcp-server-cloudflare`] — `/mcp` primary, `/sse` deprecated; "lets clients migrate at their own pace". URL path on the server side selects.

### stdio / HTTP / HTTPS triple-mode

[`the-momentum--fhir-mcp-server`] — `TRANSPORT_MODE` env var selects; among the richest single-server transport surfaces.

### SQL-driven selection

[`teaguesterling--duckdb_mcp`] — `PRAGMA mcp_server_start(...)` selects stdio/HTTP from SQL. Plus MCP-client mode via SQL `ATTACH`.

### Install-target split (local stdio + hosted remote)

[`stripe--agent-toolkit`] — stdio via `npx @stripe/mcp` (local); hosted remote at `https://mcp.stripe.com` with OAuth.

### Configurable client mode (launch-time runtime selection)

[`chroma-core--chroma-mcp`] — single binary picks ephemeral / persistent / http / cloud backing store via CLI flags / env at launch. Not transport switching, but a parallel "one binary, many runtime modes" axis.

### Special-purpose transports

#### Web framework integration

Transport that ties to a specific web framework rather than stdlib HTTP — Gin framework integration [`metoro-io--mcp-golang`], embedded Ktor server [`modelcontextprotocol--kotlin-sdk`].

#### WebSocket as a first-class transport

Kotlin SDK exposes WebSocket as a peer to SSE and Streamable HTTP — uncommon among MCP implementations sampled [`modelcontextprotocol--kotlin-sdk`].

#### In-process / channel transports

- `ChannelTransport` for local testing without networking [`modelcontextprotocol--kotlin-sdk`]
- `createConnection()` programmatic API enables embedding the server inside a host Node process — blurs server/client boundaries [`microsoft--playwright-mcp`]

#### Bidirectional stdio

Stdio transport supports bidirectional communication, not just request-response [`metoro-io--mcp-golang`].

### Transport-selection mechanism

- Default; no flag — [`ckreiling--mcp-server-docker`], [`datalayer--earthdata-mcp-server`]
- CLI flag (explicit transport name) — `--transport=sse` [`crystaldba--postgres-mcp`]; `mcpr generate-project --transport [stdio|sse]` selects at scaffold time [`conikeec--mcpr`]; `--transport` [`tumf--grafana-loki-mcp`]; `--transport http [--port 8080]` [`makenotion--notion-mcp-server`]
- CLI flag (port-presence implicit) — `--port <n>` flips to SSE/HTTP; absence defaults to stdio [`microsoft--playwright-mcp`]
- Environment-config selection (Zod-validated) — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- Env-var driven — [`the-momentum--fhir-mcp-server`] (`TRANSPORT_MODE`)
- URL path on the server side — [`cloudflare--mcp-server-cloudflare`]
- npm script — `npm run start:stdio` vs `npm run start:http` [`cyanheads--git-mcp-server`]
- CLI launcher flag / config — [`datalayer--jupyter-mcp-server`]
- SQL pragma — [`teaguesterling--duckdb_mcp`]
- SDK-level: separate entry-point methods — `server.ServeStdio()`, `server.ServeSSE()`, `server.ServeHTTP()` [`mark3labs--mcp-go`]
- SDK-level: initialization-time configuration — transport selected at server initialization; SDK provides patterns for stdlib HTTP, Gin framework, and stdio [`metoro-io--mcp-golang`]; configured at server init with embedded Ktor for HTTP [`modelcontextprotocol--kotlin-sdk`]

### HTTP host/port defaults

- 127.0.0.1:3010 [`cyanheads--perplexity-mcp-server`]
- configurable hostname, port 3015 [`cyanheads--git-mcp-server`]
- 8080 default [`makenotion--notion-mcp-server`]
- 8931 (Playwright service mode) [`microsoft--playwright-mcp`]

## Distribution

### PyPI + uvx

- `uvx awslabs.bedrock-kb-retrieval-mcp-server@latest` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `uv tool install arxiv-mcp-server` — [`blazickjp--arxiv-mcp-server`]
- `uvx chroma-mcp` — [`chroma-core--chroma-mcp`]
- `uvx mcp-server-docker` — [`ckreiling--mcp-server-docker`]
- `uvx postgres-mcp` (also `uv pip install` / `uv run`) — [`crystaldba--postgres-mcp`]
- `uvx jupyter-mcp-server@latest` — [`datalayer--jupyter-mcp-server`]
- `uvx mcp-atlassian` — [`sooperset--mcp-atlassian`]
- `uvx ghost-mcp` — [`thenets--ghost-mcp`]
- `uvx grafana-loki-mcp -u ... -k ...` — [`tumf--grafana-loki-mcp`]
- `uvx mcp-server-git` (canonical pattern across Python reference servers) — [`modelcontextprotocol--servers`]
- `uvx pandas-mcp-cli` hinted in README, but PyPI publication not verified — [`marlonluo2018--pandas-mcp-server`]
- Also pip-installable via `pip install` — [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`modelcontextprotocol--servers`] (`pip install mcp-server-git`, `pip install mcp-server-fetch`)
- pipx — [`crystaldba--postgres-mcp`]

### PyPI via pip (no uvx)

- [`awslabs--openapi-mcp-server`] uses `pip install` with extras (`[yaml]`, `[prometheus]`, `[all]`). Exception to the uvx convention; CLI args are heavy (`--api-name`, `--api-url`, `--spec-url`) so `pip install` + direct invocation makes sense
- [`awslabs--mcp-lambda-handler`] uses `pip install -e .[dev]` (library, not invoked standalone)

### npm / npx

- `npx @cyanheads/git-mcp-server@latest` — [`cyanheads--git-mcp-server`]
- `npx -y mcp-turso-cloud` — [`spences10--mcp-turso-cloud`]
- `npx -y @stripe/mcp --api-key=...` — [`stripe--agent-toolkit`]
- `npx -y @notionhq/notion-mcp-server` — [`makenotion--notion-mcp-server`]
- `npx @playwright/mcp@latest` — [`microsoft--playwright-mcp`]
- `npx -y @modelcontextprotocol/server-memory`, `npx -y @modelcontextprotocol/server-filesystem` (filesystem takes positional directory paths) — [`modelcontextprotocol--servers`]

### Bun via bunx

- `bunx @cyanheads/git-mcp-server@latest` — [`cyanheads--git-mcp-server`]

### Source clone (no published package)

- [`cyanheads--perplexity-mcp-server`] — no npm package found, README walks through `git clone` → build → run
- [`teaguesterling--duckdb_mcp`] — `make` build from source; not yet in DuckDB community extensions
- [`the-momentum--fhir-mcp-server`] — clone-required; no PyPI publication; `make build` (Docker) or `make uv`
- `git clone ... && uv sync` or `pip install -r requirements.txt` — [`marlonluo2018--pandas-mcp-server`], [`misbahsy--video-audio-mcp`]

pyproject project-name vs repo-name drift: `video-edit-mcp` (pyproject) versus `video-audio-mcp` (repo) — surfaces "what is the authoritative identifier?" question (PyPI name, repo name, console-script name can all diverge) [`misbahsy--video-audio-mcp`].

### Cargo (Rust)

[`conikeec--mcpr`] — Cargo crate registry + `cargo install` for CLI.

### Go module

`go get github.com/<org>/<repo>` — both Go SDKs distribute as Go modules; no binary releases, no Homebrew [`mark3labs--mcp-go`, `metoro-io--mcp-golang`].

### JVM artifact registries

Maven Central (Gradle/Maven); granular artifacts per concern: `io.modelcontextprotocol:kotlin-sdk` (full), `io.modelcontextprotocol:kotlin-sdk-client`, `io.modelcontextprotocol:kotlin-sdk-server` [`modelcontextprotocol--kotlin-sdk`].

### Both PyPI and npm (cross-ecosystem)

[`stripe--agent-toolkit`] — npm: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`. PyPI: `stripe-agent-toolkit`. Parallel naming convention across ecosystems.

### Docker

Most samples ship Dockerfiles or pre-built images: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`] (multi-arch linux/amd64, arm64, arm/v7), [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`] (`crystaldba/postgres-mcp`), [`cyanheads--perplexity-mcp-server`] (multi-stage Node 18-Alpine), [`datalayer--earthdata-mcp-server`] (`datalayer/earthdata-mcp-server:latest`), [`datalayer--jupyter-mcp-server`] (`datalayer/jupyter-mcp-server:latest`), [`makenotion--notion-mcp-server`] (Dockerfile + `docker-compose.yml`; `mcp/notion`), [`microsoft--playwright-mcp`] (multi-arch on `mcr.microsoft.com/playwright/mcp`), [`modelcontextprotocol--servers`] (per-server Dockerfile, images published as `mcp/<server-name>` — consistent convention across servers in the reference monorepo even though language stack differs), [`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`].

### Smithery

- [`baryhuang--mcp-server-aws-resources-python`] — `npx -y @smithery/cli install mcp-server-aws-resources-python --client claude`. Distribution vector alongside Docker and source
- [`datalayer--earthdata-mcp-server`] — `smithery.yaml` flagged as a "first-class artifact"

### Windows .exe

[`awslabs--bedrock-kb-retrieval-mcp-server`] — `uv tool run --from awslabs.bedrock-kb-retrieval-mcp-server@latest awslabs.bedrock-kb-retrieval-mcp-server.exe`.

### JVM tools-installer

[`bhauman--clojure-mcp`] — `clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp`.

### Managed/hosted endpoint as distribution

- [`supabase-community--supabase-mcp`] — managed endpoint at `https://mcp.supabase.com/mcp`; cloud usage requires no install. Vendor-hosted MCP-as-a-service
- [`stripe--agent-toolkit`] — `https://mcp.stripe.com` hosted endpoint with OAuth, in addition to local stdio

### Remote-hosted (no local install)

[`cloudflare--mcp-server-cloudflare`] — Cloudflare Workers; server author operates the runtime, end users only consume URLs; users install via `mcp-remote` shim that bridges stdio (host side) to streamable-HTTP (Worker side).

### Optional install extras

- `[pdf]` — [`blazickjp--arxiv-mcp-server`]: separates core arXiv client from heavier PDF processing deps
- `[yaml]`, `[prometheus]`, `[all]` — [`awslabs--openapi-mcp-server`]
- `[sentence-transformers]` — [`chroma-core--chroma-mcp`]: locally-embedded collections without OpenAI/Cohere/Voyage keys

### Heterogeneous distribution within one repo

Cross-language monorepo convention — TS and Python as first-class peers in one repo, each with its own distribution channel (npm vs PyPI) and its own Docker image. Forces readers/hosts to handle multiple runtime stacks [`modelcontextprotocol--servers`].

## Naming convention

### Namespace-prefixed PyPI

[`awslabs--mcp`] uses `awslabs.<service>-mcp-server` — prevents collision with other AWS-adjacent packages and makes provenance scannable from the package name alone. Quoted dotted console-script name (`"awslabs.aws-api-mcp-server" = "awslabs.aws_api_mcp_server.server:main"`) is valid pyproject syntax but rare; enables a dotted console-script name to match the PyPI package name.

### Plain package name

`chroma-mcp`, `arxiv-mcp-server`, `mcp-server-aws-resources`, `mcp-atlassian`, `ghost-mcp`, `grafana-loki-mcp`, `mcp-turso-cloud`, `postgres-mcp`, `mcp-server-docker` — typical short slug convention.

### Parallel naming across ecosystems

[`stripe--agent-toolkit`] — `@stripe/agent-toolkit` (npm) and `stripe-agent-toolkit` (PyPI) in parallel.

## Entry point and launch

### Console script (PyPI dotted)

[`awslabs--mcp`] — `"awslabs.aws-api-mcp-server" = "awslabs.aws_api_mcp_server.server:main"` — quoted-name script with dot-in-name; valid pyproject syntax but rare.

### Console script (plain)

- `awslabs.bedrock-kb-retrieval-mcp-server` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `awslabs.openapi-mcp-server` (with positional args) — [`awslabs--openapi-mcp-server`]
- `arxiv-mcp-server` — [`blazickjp--arxiv-mcp-server`]
- `chroma-mcp` (`chroma_mcp:main`) — [`chroma-core--chroma-mcp`]
- `mcp-server-docker` — [`ckreiling--mcp-server-docker`]
- `postgres-mcp = "postgres_mcp:main"` — [`crystaldba--postgres-mcp`]
- `earthdata-mcp-server` → `earthdata_mcp_server.server:server` — [`datalayer--earthdata-mcp-server`]
- `jupyter-mcp-server` → `jupyter_mcp_server.CLI:server` — [`datalayer--jupyter-mcp-server`]
- `mcp-atlassian = "mcp_atlassian:main"` — [`sooperset--mcp-atlassian`]
- `start = start:main` (bare module name `start` rather than `app.start`) — [`the-momentum--fhir-mcp-server`]
- `ghost-mcp` — [`thenets--ghost-mcp`]
- `grafana-loki-mcp` — [`tumf--grafana-loki-mcp`]
- `mcp-server-git = "mcp_server_git:main"`, `mcp-server-fetch = "mcp_server_fetch:main"` — [`modelcontextprotocol--servers`]
- npm `bin` entry pointing at tsc+esbuild-built CLI — [`makenotion--notion-mcp-server`]

### Bare script

- `python server.py`, `python cli.py`, `uv run server.py` — bare scripts at repo root [`marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`]
- [`baryhuang--mcp-server-aws-resources-python`] — `src/mcp_server_aws_resources/server.py` or containerized equivalent

### `python -m <module>` invocation

Alternative to console-script for Python servers — works without installation if the package is on PYTHONPATH. `python -m mcp_server_<name>` documented as an alternative to `uvx mcp-server-<name>` [`modelcontextprotocol--servers`].

### Docker run as entry point

- `docker run -i --rm --mount type=bind,src=/path,dst=/projects mcp/filesystem /projects` — mount the host directory to grant filesystem access [`modelcontextprotocol--servers`]
- `docker run -i --rm --init --pull=always mcr.microsoft.com/playwright/mcp` [`microsoft--playwright-mcp`]

### Library import (no standalone)

[`awslabs--mcp-lambda-handler`] — `def lambda_handler(event, context): return mcp.handle_request(event, context)`. Console script declared but primary usage is library import.

### Programmatic embedding (library mode)

Server runs inside a host process as a library, not just as an external subprocess. `createConnection()` enables embedding in Node apps [`microsoft--playwright-mcp`].

### Programmatic builder (SDK-only)

SDK exposes a builder API; no runnable binary. Construction is the entry point.

- Functional options: `server.NewMCPServer()` constructor; `WithToolCapabilities()`, `WithTaskCapabilities()`, `WithMaxConcurrentTasks()`, `RegisterSession()` [`mark3labs--mcp-go`]
- Registration methods: `RegisterTool()`, `RegisterPrompt()`, `RegisterResource()` [`metoro-io--mcp-golang`]
- Application-specific initialization with optional Ktor server integration for HTTP [`modelcontextprotocol--kotlin-sdk`]

### Tools-installer launch

[`bhauman--clojure-mcp`] — `clojure -Tmcp start` post-install; profiles like `clojure-mcp-light` for lightweight REPL, `:cli-assist` for full.

### Wrapper / launcher patterns

- Dockerfile as launcher artifact — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- npm scripts split by transport — `npm run start:stdio` vs `npm run start:http` [`cyanheads--git-mcp-server`]
- npm build script compiles TS to `dist/` — [`cyanheads--perplexity-mcp-server`]
- `mcpr generate-project --name [name]` scaffolds a fresh project — [`conikeec--mcpr`]
- Jupyter Server extension config under `jupyter-config/` so the server can mount inside Jupyter rather than running standalone — [`datalayer--jupyter-mcp-server`]
- `mcp-remote` (npm) as a host-side shim translating stdio↔streamable-HTTP for remote servers — [`cloudflare--mcp-server-cloudflare`]
- Make/script-driven entry — [`the-momentum--fhir-mcp-server`] (`make build` / `make uv`; `start.py` entry script), [`thenets--ghost-mcp`] (`make run` / `make dev`), [`teaguesterling--duckdb_mcp`] (`make`)

### URL-only (no local invocation)

[`supabase-community--supabase-mcp`] — clients configured to hit the HTTPS URL; no command/args.

### SQL-driven entry

[`teaguesterling--duckdb_mcp`] — `PRAGMA mcp_server_start()` from inside a DuckDB session.

## Configuration surface

### Environment variables

- AWS credentials chain — [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`]
- `KB_INCLUSION_TAG_KEY` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `FASTMCP_LOG_LEVEL` — [`awslabs--mcp`]
- `BEDROCK_KB_RERANKING_ENABLED` (per-service) — [`awslabs--mcp`]
- `ARXIV_STORAGE_PATH` — [`blazickjp--arxiv-mcp-server`]
- `CHROMA_<PROVIDER>_API_KEY` provider-prefixed convention — [`chroma-core--chroma-mcp`]
- `DOCKER_HOST` — [`ckreiling--mcp-server-docker`]
- `DATABASE_URI` — [`crystaldba--postgres-mcp`]
- `EARTHDATA_USERNAME` / `PASSWORD` — [`datalayer--earthdata-mcp-server`]
- `JUPYTER_URL`, `JUPYTER_TOKEN`, `ALLOW_IMG_OUTPUT`, `DOCUMENT_ID`, `MCP_TOKEN` — [`datalayer--jupyter-mcp-server`]
- Zod-validated env-var bundle (transport, session, response format, Git identity, base-dir, GPG/SSH signing, auth, log level) — [`cyanheads--git-mcp-server`]
- `.env` file validated by Zod — [`cyanheads--perplexity-mcp-server`]
- `TURSO_API_TOKEN`, `TURSO_ORGANIZATION`, `TURSO_DEFAULT_DATABASE`, `TOKEN_EXPIRATION` (default 7 days), `TOKEN_PERMISSION` (default full-access) — [`spences10--mcp-turso-cloud`]
- Cloud (`JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN`, `CONFLUENCE_*`) plus DC (`JIRA_PERSONAL_TOKEN`) — [`sooperset--mcp-atlassian`]
- `GHOST_URL` + Ghost API keys; env-var presence drives which API surface (Content vs Admin) is active — [`thenets--ghost-mcp`]
- `TRANSPORT_MODE`, FHIR backend URL + OAuth2 client ID/secret, optional encryption master key — [`the-momentum--fhir-mcp-server`]
- `NOTION_TOKEN` (recommended) or `OPENAPI_MCP_HEADERS` — [`makenotion--notion-mcp-server`]
- `PYTHONIOENCODING=utf-8` noted for Windows in fetch — narrow runtime-environment correction — [`modelcontextprotocol--servers`]

### CLI flags

- `--api-name`, `--api-url`, `--spec-url`, `--additional-specs`, `--include-tags`, `--exclude-tags` — [`awslabs--openapi-mcp-server`]
- `--storage-path` — [`blazickjp--arxiv-mcp-server`]
- Backend-mode flags (`--client-type ephemeral|persistent|http|cloud`) — [`chroma-core--chroma-mcp`]
- `--dotenv-path` for `.env` — [`chroma-core--chroma-mcp`]
- `--access-mode unrestricted/restricted`, `--transport` — [`crystaldba--postgres-mcp`]
- `--api-key=...` (entry; env-var equivalent not extracted) — [`stripe--agent-toolkit`]
- Both env vars and CLI flags (`GRAFANA_URL` / `GRAFANA_API_KEY` env or `-u` / `-k` flags) — [`tumf--grafana-loki-mcp`]
- 50+ CLI flags and matching env vars; every flag has a `PLAYWRIGHT_MCP_*` env-var equivalent — [`microsoft--playwright-mcp`]

### Positional CLI arguments

Required runtime config passed positionally rather than as flags. Filesystem server takes directory paths as positional args (e.g., `/projects`); Git uses `--repository` flag instead [`modelcontextprotocol--servers`].

### Optional `.env` file

`.env` file with `.env.example` template — convention for local dev defaults [`marlonluo2018--pandas-mcp-server`].

### MCP client JSON config

`mcpServers` block — [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`].

### URL query parameters

[`supabase-community--supabase-mcp`] — `project_ref`, `read_only`, `features` are URL query params on the HTTP endpoint. Unusual for MCP; fits HTTP transport. Embeds scope into the endpoint itself.

### SQL pragmas

[`teaguesterling--duckdb_mcp`] — `PRAGMA mcp_server_start()`, `PRAGMA mcp_publish_tool(...)` carry config arguments. Plus a JSON config file for HTTP/token settings.

### Project file (declarative)

[`bhauman--clojure-mcp`] — `.clojure-mcp/config.edn` with Clojure map structure; CLI overrides for tool filtering, profile selection, nREPL parameters.

### Lambda env (deployment-bound)

[`awslabs--mcp-lambda-handler`] — Lambda environment variables; session backend selected (NoOp / DynamoDB / custom class) at construction.

### Builder pattern (Rust)

[`conikeec--mcpr`] — `ServerConfig` builder (`.with_name()`, `.with_version()`, `.with_tool()`; tool parameter schemas as JSON objects).

### JSON config file (single-flag)

[`microsoft--playwright-mcp`] — `--config <path>` loads a JSON file of settings, alternative to flag-by-flag CLI.

### Capability gating via flags

Tool surface itself is configurable, not just credentials.

- `--caps=<cap>` groups (pdf, vision, testing) unlock tool subsets — install-time surface for trimming tool exposure [`microsoft--playwright-mcp`]
- Per-host network policy: `--allowed-origins`, `--blocked-origins`, `--proxy-server` limit network access at the server boundary [`microsoft--playwright-mcp`]
- Storage and timeout flags: `--timeout-action`, `--timeout-navigation` for behavior tuning; `--init-page`, `--init-script` for startup hooks; `--cdp-endpoint` for browser remote attach; `--user-data-dir` for session persistence [`microsoft--playwright-mcp`]

### Code-level configuration (SDK)

SDKs configure at construction-time rather than via env / CLI; the application embedding the SDK chooses how to surface config.

- Functional options pattern: `WithToolCapabilities()`, `WithTaskCapabilities()`, `WithMaxConcurrentTasks()`, middleware registration [`mark3labs--mcp-go`]
- Registration methods + framework setup [`metoro-io--mcp-golang`]
- CORS configuration for browser clients; configurable endpoint paths (default `/mcp`); transport-specific options [`modelcontextprotocol--kotlin-sdk`]

### Wrangler config (per Worker)

[`cloudflare--mcp-server-cloudflare`] — `wrangler.toml` / `wrangler.jsonc` per Worker for server-side deployment; client side carries only the URL.

### Schema / validation strategy on env

Zod for env-var validation is the TS pattern in this corpus — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`].

## Authentication

### AWS credential chain

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`] — `AWS_PROFILE`, AWS SSO, instance roles, env credentials, STS session tokens. No MCP-level auth layer; standard AWS resolution.

### Static API key / token

- Provider-prefixed (`CHROMA_OPENAI_API_KEY` etc.) for Chroma Cloud and embedding providers — [`chroma-core--chroma-mcp`]
- Optional API keys for external LLM providers (Anthropic, OpenAI, Google Gemini) for *agent tools*, not server auth — [`bhauman--clojure-mcp`]
- Turso org-level API token — [`spences10--mcp-turso-cloud`]
- Atlassian API tokens (Cloud) and Personal Access Tokens (Server/DC) — [`sooperset--mcp-atlassian`]
- Grafana API key — [`tumf--grafana-loki-mcp`]
- Stripe secret keys; Restricted API Keys (RAK) recommended as best practice — credential-scoping guidance is elevated in docs — [`stripe--agent-toolkit`]
- API key + optional JWT/OAuth on HTTP transport (`PERPLEXITY_API_KEY` + optional JWT or OAuth 2.1) — [`cyanheads--perplexity-mcp-server`]
- Notion API integration token via `NOTION_TOKEN` env var, CLI args, or HTTP Bearer header — [`makenotion--notion-mcp-server`]

### Connection-string / URI-embedded credentials

[`crystaldba--postgres-mcp`] — `DATABASE_URI`.

### Username/password env vars

[`datalayer--earthdata-mcp-server`] — NASA Earthdata Login via `earthaccess` library, which "delegates the auth dance".

### Local OS / SDK credentials discovery

[`ckreiling--mcp-server-docker`] — Docker SDK `from_env()` discovery. Also flagged: SSH-based auth for remote Docker daemons via `DOCKER_HOST=ssh://...` — first-class supported path, not just local socket.

### Per-API auth (multi-spec)

[`awslabs--openapi-mcp-server`] — Basic, Bearer Token, API Key (header/query/cookie), AWS Cognito; each mounted spec has its own credential context. Auth as per-spec, not per-server, supports "one gateway to many SaaS APIs" use case.

### Infrastructure-delegated auth

[`awslabs--mcp-lambda-handler`] — bearer tokens validated by API Gateway Lambda Authorizer upstream; the application never sees raw tokens. Authentication is architecturally outside the server, not inside.

### HTTP Bearer for remote transports

stdio is unauthenticated; HTTP/SSE require a Bearer token in HTTP headers. Notion MCP follows this pattern when running in HTTP mode [`makenotion--notion-mcp-server`].

### OAuth flows

#### OAuth 2.0

[`sooperset--mcp-atlassian`] — Cloud OAuth 2.0 supported per docs.

#### OAuth 2.1

[`supabase-community--supabase-mcp`] — automatic prompt during client setup; browser-based consent; tokens managed by MCP client/host. Early adopter of OAuth 2.1 in MCP space.

#### OAuth 2.0 client-credentials

[`the-momentum--fhir-mcp-server`] — against the FHIR backend (e.g. Medplum).

#### OAuth on hosted endpoint only

[`stripe--agent-toolkit`] — OAuth for `mcp.stripe.com` hosted endpoint; static keys for local stdio.

### Three-mode auth (none / jwt / oauth)

[`cyanheads--git-mcp-server`] — selected via env config (`jwt` requires 32+ char secret; `oauth` uses OIDC provider).

### Token env vars (single layer)

[`datalayer--jupyter-mcp-server`] 0.x had only `JUPYTER_TOKEN`.

### Layered tokens (auth split by protocol layer)

[`datalayer--jupyter-mcp-server`] v1.0.0+ split into `JUPYTER_TOKEN` (upstream Jupyter) + `MCP_TOKEN` (MCP interface) — called out as a breaking change. Two credential lifecycles managed by one server is also seen in [`thenets--ghost-mcp`] (Content API uses query-parameter auth with 26-char hex API keys; Admin API uses JWT).

### JWT with auto-renewal

[`thenets--ghost-mcp`] — Admin API uses JWTs from `id:secret` format; tokens expire after 5 minutes with automatic renewal and caching inside the server. Server-managed token rotation.

### Bearer tokens (HTTP server mode)

[`teaguesterling--duckdb_mcp`] — Bearer-token auth in HTTP server mode; credentials from JSON config file.

### Cloudflare API tokens with per-service scopes

[`cloudflare--mcp-server-cloudflare`] — OAuth-like handshake negotiated by the `mcp-remote` shim.

### Server-internal credential vault

[`the-momentum--fhir-mcp-server`] — encrypted credential storage with optional master-key-based encryption for sensitive fields. In-server vault, unusual; HIPAA/PHI-driven.

### Generated short-lived child tokens

[`spences10--mcp-turso-cloud`] — org-level token generates database-specific tokens automatically with configurable permission granularity. `TOKEN_EXPIRATION` and `TOKEN_PERMISSION` promote short-lived child-token generation as a security primitive.

### SDK delegates to transport / application layer

SDK provides no built-in auth; the embedding application or transport handles credentials.

- Session registration via `RegisterSession()`; no explicit auth in SDK [`mark3labs--mcp-go`]
- HTTPS custom auth marked experimental (in progress) [`metoro-io--mcp-golang`]
- Auth delegated to transport / application layer [`modelcontextprotocol--kotlin-sdk`]

### Boundary enforcement via path allowlist

Filesystem reference server gates file access by an allowlist of root directories provided positionally on launch (and updated dynamically via MCP Roots) — replaces auth with a structural permission boundary [`modelcontextprotocol--servers`].

### None / public / disclaimed

- arXiv public API; rate limit enforced locally (3-second minimum) — [`blazickjp--arxiv-mcp-server`]
- No built-in authentication — [`bhauman--clojure-mcp`]
- N/A library — [`conikeec--mcpr`] ("transport-layer security implied for production SSE deployments")
- "Playwright MCP is not a security boundary" — README explicit; `--allow-unrestricted-file-access` is the escape hatch. Storage-state files persist sessions but are state, not auth [`microsoft--playwright-mcp`]
- None — local file processing only; no credentials [`marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`]
- None across reference servers; access gated by directory allowlist (filesystem) or repo path (git); fetch respects robots.txt by default [`modelcontextprotocol--servers`]

### Read-only / restricted-access enforcement

In-process SQL parsing rejects writes (not DB-level permissions) — [`crystaldba--postgres-mcp`] uses `pglast` to reject COMMIT/ROLLBACK in restricted mode.

## Multi-tenancy

### Single-user per process

Common shape: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`], [`ckreiling--mcp-server-docker`] (one Docker daemon connection), [`datalayer--earthdata-mcp-server`] (bound to one NASA account), [`crystaldba--postgres-mcp`] (single DB connection per instance; SSE multiplexes clients but not tenants), [`makenotion--notion-mcp-server`] (per-integration-token; HTTP transport supports multiple clients but each speaks for one Notion identity at a time), [`marlonluo2018--pandas-mcp-server`] (operates on user-supplied CSV/data paths per call), [`microsoft--playwright-mcp`], [`modelcontextprotocol--servers`] (single-user local process per host session), [`sooperset--mcp-atlassian`] (one Atlassian site), [`spences10--mcp-turso-cloud`] (single org per deployment), [`stripe--agent-toolkit`] stdio mode (one API key → one Stripe account), [`thenets--ghost-mcp`] (one `GHOST_URL`), [`tumf--grafana-loki-mcp`] (one Grafana instance), [`the-momentum--fhir-mcp-server`] (not addressed; effectively single).

### Tag-driven scoping (server-enforced)

[`awslabs--bedrock-kb-retrieval-mcp-server`] — knowledge bases tagged `mcp-multirag-kb=true` (overridable via `KB_INCLUSION_TAG_KEY`) are surfaced; AWS tag filters are the access-control boundary, enforced server-side, not by the LLM. A novel solution to "too many resources in the account" without building app-level access control.

### Per-request (serverless)

[`awslabs--mcp-lambda-handler`] — Lambda invocations naturally isolated; DynamoDB session backend keyed by session ID for persistent state per tenant across requests. Pluggable session management (NoOp / DynamoDB / custom).

### Per-spec composition

[`awslabs--openapi-mcp-server`] — `--additional-specs` mounts multiple OpenAPI specs in one server, each with its own HTTP client and auth context.

### Per-notebook scoped at runtime

[`datalayer--jupyter-mcp-server`] — `DOCUMENT_ID`, `use_notebook` switches target; one JupyterLab instance per server process.

### Per-user single instance with multi-client option in HTTP mode

[`cyanheads--perplexity-mcp-server`] — multi-client option in HTTP mode via JWT/OAuth.

### Workspace-keyed (tenant sandboxing in stdio)

[`cyanheads--git-mcp-server`] — base-directory restriction; per-session working-directory management. Multi-tenant sandboxing within a stdio server.

### Per-request tenancy (Workers)

[`cloudflare--mcp-server-cloudflare`] — each Worker invocation scoped by bearer token → authenticated Cloudflare account; one Worker serves any account.

### Per-request tenancy via URL params

[`supabase-community--supabase-mcp`] — `project_ref` URL parameter scopes each connection. OAuth identity × project ref defines tenant boundary per session.

### Per-user OAuth tenancy

[`stripe--agent-toolkit`] hosted mode — each user authorizes their own Stripe account via OAuth.

### Database-scoped sub-tenancy

[`spences10--mcp-turso-cloud`] — per-database token permissions provide isolation within an organization.

### Database-instance keyed

[`teaguesterling--duckdb_mcp`] — server keyed to the DuckDB database; no per-request handling.

### Per-request session state (SDK-level)

SDK enables multi-tenancy by registering sessions and routing notifications per-client.

- Per-request via session registration; notification channels support per-client state management [`mark3labs--mcp-go`]
- HTTP stateless pattern suggests per-request handling; per-tool tenant routing not centrally documented [`metoro-io--mcp-golang`]
- SDK provides transport and protocol abstraction; multi-tenancy handled by application using the SDK [`modelcontextprotocol--kotlin-sdk`]

### Not applicable

Library, no tenancy concerns — [`conikeec--mcpr`].

## Capabilities exposed

### Tools

- Knowledge-base discovery, data-source listing, NL KB querying, result filtering, conditional reranking — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- Per-service tools per AWS service — [`awslabs--mcp`]
- Dynamically generated tools from OpenAPI ops — [`awslabs--openapi-mcp-server`]
- Single `exec boto3` tool — [`baryhuang--mcp-server-aws-resources-python`]
- 50+ tools across read-only file ops, code evaluation, structure-aware editing, shell execution, agent-based analysis — [`bhauman--clojure-mcp`]
- 6 tools (search, download, read, list, semantic search, citation graph) — [`blazickjp--arxiv-mcp-server`]
- 12 tools (collection CRUD, document ops, retrieval) — [`chroma-core--chroma-mcp`]
- Tools via `@mcp.tool()` decorator (user-authored) — [`awslabs--mcp-lambda-handler`]
- 28+ tools, container stats/logs resources, docker-compose workflow prompt — [`ckreiling--mcp-server-docker`]
- 28 tools across 7 categories, 1 resource for repo metadata, 1 prompt — [`cyanheads--git-mcp-server`]
- 9 tools — [`crystaldba--postgres-mcp`] (deliberate "tools only"; "the MCP client ecosystem has widespread support for MCP tools" cited as rationale for skipping resources/prompts)
- 3 tools — [`datalayer--earthdata-mcp-server`]
- 16+ tools (file/kernel listing, notebook CRUD, cell ops, full-notebook run, selected-cell fetch) — [`datalayer--jupyter-mcp-server`]
- 2 tools — [`cyanheads--perplexity-mcp-server`]
- Tools only across many domain servers — [`cloudflare--mcp-server-cloudflare`] (14 domain Workers each exposing tools per domain)
- Tools + library scaffolding only — [`conikeec--mcpr`] (tool registration/invocation, handshake with version negotiation, disconnection handling, interactive vs one-shot modes)
- 72 tools across Jira and Confluence — [`sooperset--mcp-atlassian`]
- 15+ across Content (10) + Admin (6) + utility — [`thenets--ghost-mcp`]
- 14+ across FHIR resources, document management, LOINC terminology lookup — [`the-momentum--fhir-mcp-server`]
- 22 tools — page create/retrieve, database query, page move, commenting, content search [`makenotion--notion-mcp-server`]
- 4 tools (`read_metadata_tool`, `interpret_column_data`, `run_pandas_code_tool`, `generate_chartjs_tool`) [`marlonluo2018--pandas-mcp-server`]
- 30+ tools — video format conversion, trimming, scaling, codec changes, overlays; audio format/bitrate/sample-rate adjustment, channel config; creative (text overlays, watermarks, subtitles, transitions); advanced (concatenation, B-roll insertion, silence removal). 30+ tools from a 6-commit repo, demonstrating how quickly an FFmpeg wrapper scales via codegen-like uniformity [`misbahsy--video-audio-mcp`]
- 80+ structured tools across categories — Core automation (click, type, navigate, screenshot, snapshot); Tab management; Network (mocking, state inspection, route management); Storage (cookies, localStorage, sessionStorage); DevTools (tracing, video, element highlight, debugging); Vision (coordinate-based interactions); PDF; Testing (assertions, locator generation) [`microsoft--playwright-mcp`]
- 1 `fetch` tool — [`modelcontextprotocol--servers`] (fetch reference)
- 13 filesystem tools (9 read + 4 write); 12 git tools — [`modelcontextprotocol--servers`]

### Tool count bands

- 1 — [`baryhuang--mcp-server-aws-resources-python`], [`modelcontextprotocol--servers`] (fetch)
- 2 — [`cyanheads--perplexity-mcp-server`]
- 3 — [`datalayer--earthdata-mcp-server`]
- 4 — [`marlonluo2018--pandas-mcp-server`]
- 6 — [`blazickjp--arxiv-mcp-server`]
- 9 — [`crystaldba--postgres-mcp`]
- 12 — [`chroma-core--chroma-mcp`], [`modelcontextprotocol--servers`] (git)
- 13 — [`modelcontextprotocol--servers`] (filesystem)
- 14+ — [`the-momentum--fhir-mcp-server`]
- 15+ — [`thenets--ghost-mcp`]
- 16+ — [`datalayer--jupyter-mcp-server`]
- 22 — [`makenotion--notion-mcp-server`]
- 28 / 28+ — [`cyanheads--git-mcp-server`], [`ckreiling--mcp-server-docker`]
- 30+ — [`misbahsy--video-audio-mcp`]
- 50+ — [`bhauman--clojure-mcp`]
- 72 — [`sooperset--mcp-atlassian`]
- 80+ — [`microsoft--playwright-mcp`]
- Small or unspecified — [`spences10--mcp-turso-cloud`], [`supabase-community--supabase-mcp`], [`stripe--agent-toolkit`], [`teaguesterling--duckdb_mcp`], [`tumf--grafana-loki-mcp`]

### Resources

- Dynamic AWS-resources resource — [`baryhuang--mcp-server-aws-resources-python`]
- GETs other than parameterized search — [`awslabs--openapi-mcp-server`]
- Container stats / logs — [`ckreiling--mcp-server-docker`]
- Repo metadata — [`cyanheads--git-mcp-server`]

### Prompts

- Research analysis and literature review workflow prompts — [`blazickjp--arxiv-mcp-server`]
- Operation-specific prompts and API doc prompts auto-generated — [`awslabs--openapi-mcp-server`]
- Pre-built Agent SOPs (preview aggregator) — [`awslabs--mcp`]
- Docker-compose natural-language → multi-step workflow prompt — [`ckreiling--mcp-server-docker`] flagged "MCP prompts as orchestration primitives rather than just tools"
- One prompt — [`cyanheads--git-mcp-server`]

### MCP protocol features (SDK-level)

Beyond tools, what protocol features the server/SDK actually supports.

- Tools, Resources, Prompts, Sessions, Notifications — [`mark3labs--mcp-go`]
- Tools, Prompts, Resources with full listing and pagination support — [`metoro-io--mcp-golang`]
- Server side: Prompts, Resources, Tools, Completion, Logging, experimental features. Client side: Sampling (LLM requests), Roots (filesystem declaration), Elicitation — [`modelcontextprotocol--kotlin-sdk`]

#### MCP Roots protocol

Filesystem reference server implements MCP Roots — the only reference server that interacts with the protocol's client-provided root-directory mechanism, enabling dynamic directory updates from the host [`modelcontextprotocol--servers`].

#### Sampling and Elicitation (client-side capabilities)

Kotlin SDK is the only sample explicitly surfacing client-side Sampling (LLM requests) and Elicitation alongside Roots [`modelcontextprotocol--kotlin-sdk`].

#### Pagination on listings

Pagination support for list operations, suggesting handling of large result sets — uncommon among MCP implementations sampled. [`metoro-io--mcp-golang`], [`modelcontextprotocol--kotlin-sdk`].

#### Change notifications

Server pushes notifications to clients when resource/tool/prompt sets change, enabling reactive client patterns and event-driven server architectures [`metoro-io--mcp-golang`].

#### Bidirectional stdio communication

Stdio transport supports bidirectional communication, not just request-response [`metoro-io--mcp-golang`].

#### Async task execution with concurrency limits

Task-augmented tool execution (asynchronous with concurrency limits) — `WithMaxConcurrentTasks()` lets the server bound parallel tool work; differentiates from basic tool registries [`mark3labs--mcp-go`].

### Capability probing / feature gates

Reranking only exposed when region + IAM perms allow, rather than failing at tool-call time — [`awslabs--bedrock-kb-retrieval-mcp-server`].

### Tool-grouping mechanisms

#### Feature-group flag

[`supabase-community--supabase-mcp`] — `features` URL parameter enables/disables tool groups (Account, Documentation, Database, Debugging, Development, Edge Functions, Branching, Storage). Storage disabled by default; Branching is paid/experimental — explicit plan-tier gating surfaced through tool groups.

#### Read-only vs write-capable split

- [`supabase-community--supabase-mcp`] — `read_only` URL param
- [`spences10--mcp-turso-cloud`] — `execute_read_only_query` (SELECT/PRAGMA) vs `execute_query` (DML/DDL) supports different MCP-client approval workflows

#### Dual-API surface split

[`thenets--ghost-mcp`] — Content API (10 read-only tools) vs Admin API (6 read/write tools); env-var presence selects which surface is active.

#### Capability groups (`--caps`)

Install-time surface for trimming tool exposure: pdf, vision, testing as opt-in capability groups [`microsoft--playwright-mcp`].

#### Network/Storage/DevTools opt-in

Several Playwright tool categories (Network, Storage, DevTools) are opt-in toggles rather than default-on [`microsoft--playwright-mcp`].

#### Path allowlist as capability scoping

Filesystem server's allowlist gates which directories tools can touch; functions as both auth and capability scoping [`modelcontextprotocol--servers`].

#### No selector observed

[`sooperset--mcp-atlassian`] — 72-tool surface with no documented tool-group selector.

### Single-tool, multi-mode parameter

- Three download modes (manifest, download, script) on one tool — [`datalayer--earthdata-mcp-server`] called out as "clean separation of 'describe what you would do' from 'do it'"
- See also [`baryhuang--mcp-server-aws-resources-python`] (single `exec boto3` tool)

### Output format selection

- [`teaguesterling--duckdb_mcp`] — per-tool output format (JSON/Markdown/CSV) — explicit token-efficiency knob
- [`tumf--grafana-loki-mcp`] — output format (text/JSON/markdown) as a tool parameter, rare among MCPs surveyed

### Custom tool definition at runtime

[`teaguesterling--duckdb_mcp`] — `mcp_publish_tool` PRAGMA makes user-defined parameterized SQL templates first-class discoverable tools.

### Vector / semantic search exposed

- [`spences10--mcp-turso-cloud`] — vector similarity search as a first-class tool
- [`the-momentum--fhir-mcp-server`] — embedded RAG pipeline with llama-index + huggingface + pinecone + sentence-transformers + pymupdf inside the MCP server

### Domain terminology integration

[`the-momentum--fhir-mcp-server`] — LOINC terminology service integration; healthcare ontology bridge.

### Prompt-injection mitigation

[`supabase-community--supabase-mcp`] — SQL results wrapped with anti-injection instructions so LLMs resist following commands embedded in returned data.

### Domain-specific tool surface patterns

#### Browser automation — accessibility-first perception

Accessibility-tree snapshots as primary perception model — token-efficient versus screenshot/vision. Vision is opt-in via `--caps=vision`, not default. Reverses the default assumption that browser automation needs visual models [`microsoft--playwright-mcp`].

#### Server-stateful side channels

Most MCP servers are stateless; some persist data locally across calls. Storage-state files for browser sessions — non-auth state-carrying mechanism, supports state portability between runs [`microsoft--playwright-mcp`].

#### Filesystem with on-disk artifact return

Tool returns a file path to a generated artifact rather than the artifact's bytes — chart artifacts persist on disk; MCP client has to read the file path. Persistent file-system output as the tool return channel [`marlonluo2018--pandas-mcp-server`].

#### Sandboxed code execution

Tool wraps a runtime that executes user-supplied code. Trust model differs fundamentally from pure read-only tool servers.

- Blacklist-filtered pandas code execution — string-level denylist is a known-fragile approach versus process isolation or restricted exec [`marlonluo2018--pandas-mcp-server`]
- AST validator + import allowlist (boto3, operator, json, datetime, pytz, dateutil, re, time) — [`baryhuang--mcp-server-aws-resources-python`]

## Tool-surface design

### Hand-enumerated per-API tools

Default shape across most samples: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`].

### Spec-generated tools

[`awslabs--openapi-mcp-server`] — tools materialize at server start from parsed OpenAPI spec. GET-with-query-params mapped to *tools* not *resources* — explicit deviation from MCP convention because LLMs use tools better than resources for parameterized search. Tag filtering via `--include-tags` / `--exclude-tags` reduces tool surface at mount time. Auto-enriched tool descriptions with response codes + parameter examples → claimed 70-75% token reduction vs naive rendering.

### OpenAPI-derived tool surface (server-level)

Auto-derived tools from an OpenAPI spec rather than hand-authored — uses `openapi-client-axios` 7.5.5 [`makenotion--notion-mcp-server`].

### Code-as-tool (single sandboxed interpreter)

[`baryhuang--mcp-server-aws-resources-python`] — single tool accepts a Python code string; AST validator + import allowlist is the sandboxing mechanism.

### Decorator-driven (user-authored)

[`awslabs--mcp-lambda-handler`] — familiar FastMCP `@mcp.tool()` pattern but reimplemented on top of Lambda request/response shapes rather than `fastmcp`.

## Extensibility (SDK-level)

### Middleware

#### Request lifecycle hooks

Request hooks for telemetry across all functionality — custom observability without modifying core code. Recovery middleware for panics in tool handlers — operational safety feature [`mark3labs--mcp-go`].

#### Per-request middleware registration

`server.NewMCPServer()` supports middleware registration for tools, prompts, recovery [`mark3labs--mcp-go`].

### Init scripts / startup hooks

`--init-script` lets users inject instrumentation at server start; `--init-page` runs scripted setup before the first tool call [`microsoft--playwright-mcp`].

### Custom transports

Transport pluggability for environments where the built-ins don't fit.

- Custom transport support [`metoro-io--mcp-golang`]
- ChannelTransport for local testing [`modelcontextprotocol--kotlin-sdk`]
- Independent engine selection — Kotlin SDK has no transitive Ktor dependencies; developers specify Ktor engines independently [`modelcontextprotocol--kotlin-sdk`]

## Schema / type strategy

### Pydantic v2 (auto-derived)

- `pydantic>=2.11.1` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- Pydantic via MCP SDK (auto-derived from signatures) — [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`] (also FastAPI models for HTTP layer; schema auto-derived)
- Pydantic v2 with schemas derived from OpenAPI specs via `openapi-spec-validator` + `prance` — [`awslabs--openapi-mcp-server`] (the most extreme "schema is data" design in the corpus)
- Pydantic v2 + pydantic-settings — [`the-momentum--fhir-mcp-server`]
- FastMCP-1.x-auto-derived from type hints via the SDK — [`marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`]

### Hand-authored / minimal

- Hand-authored single-tool schema (Python code string as input) — [`baryhuang--mcp-server-aws-resources-python`]
- Hand-authored JSON schemas (low-level MCP SDK) — [`crystaldba--postgres-mcp`]; project also pins pyright (`pyright==1.1.408` exact) for strict typing
- Hand-authored JSON Schema (low-level `mcp` SDK) in Python reference servers; pyright for typing — [`modelcontextprotocol--servers`]

### Stdlib / unspecified

- No Pydantic dependency listed — likely dataclasses or TypedDict — [`awslabs--mcp-lambda-handler`]

### Auto-derived from native type signatures (Go)

Type-safe tool definitions using native Go structs with automatic schema generation — [`metoro-io--mcp-golang`].

### Type-checker variants

- mypy — [`tumf--grafana-loki-mcp`], [`sooperset--mcp-atlassian`]
- ty (newer alternative to mypy) — [`the-momentum--fhir-mcp-server`]
- pyright (exact-pinned) — [`crystaldba--postgres-mcp`]
- pyright>=1.1.389 — [`modelcontextprotocol--servers`]

### Zod (TypeScript)

[`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`makenotion--notion-mcp-server`] (Zod 3.24.1 — implies runtime-validated schemas).

### Coroutine-friendly Kotlin idioms

Kotlin SDK exposes coroutine-friendly APIs throughout [`modelcontextprotocol--kotlin-sdk`].

## Async vs sync

### Async throughout

- `httpx` + FastMCP 2 — [`awslabs--openapi-mcp-server`]
- pytest-asyncio + `asyncio_mode = "auto"` — [`awslabs--mcp`]
- Likely async (httpx idiom) — [`blazickjp--arxiv-mcp-server`]
- async tool surface; `pytest-asyncio>=1.3.0` in dev deps — [`crystaldba--postgres-mcp`]
- async tornado/fastapi under the hood; pytest suite is async — [`datalayer--jupyter-mcp-server`]
- Likely async via FastMCP 2.x + httpx + FastAPI — [`the-momentum--fhir-mcp-server`]
- async/await mentioned as feature — [`thenets--ghost-mcp`]
- async-capable via FastMCP — [`tumf--grafana-loki-mcp`]

### asyncio + anyio side-by-side

[`sooperset--mcp-atlassian`] — pytest-asyncio + pytest-anyio.

### Sync (boto3 idiom)

- boto3 sync by nature — [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`baryhuang--mcp-server-aws-resources-python`]
- Likely sync (`earthaccess` is sync) — [`datalayer--earthdata-mcp-server`]

### Mixed

pytest-asyncio suggests async coverage but mixed — [`chroma-core--chroma-mcp`].

### Not surfaced

- async/sync behavior not surfaced — [`ckreiling--mcp-server-docker`]

## Observability

### `loguru`

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--openapi-mcp-server`].

### Standard MCP stderr

[`chroma-core--chroma-mcp`], [`blazickjp--arxiv-mcp-server`], [`modelcontextprotocol--servers`] (each server logs to stderr per SDK default).

### `FASTMCP_LOG_LEVEL` env

[`awslabs--mcp`].

### CloudWatch + X-Ray (Lambda implicit)

[`awslabs--mcp-lambda-handler`].

### nREPL JSON-RPC notifications

[`bhauman--clojure-mcp`] — notifications signal tool/resource availability changes; server logs nREPL connection details and tool initialization status during startup.

### Optional Prometheus

[`awslabs--openapi-mcp-server`] — via `[prometheus]` extra.

### CloudTrail audit

[`awslabs--mcp`] — preview aggregated server bundles CloudTrail audit logging.

### Pino structured logging + audit trails + optional OpenTelemetry

[`cyanheads--git-mcp-server`] — request-context audit trails for auditing.

### Structured logging with file rotation

[`cyanheads--perplexity-mcp-server`] — centralized utilities.

### OpenTelemetry as hard dep

[`datalayer--jupyter-mcp-server`] — OpenTelemetry api+sdk (>=1.24.0) baked into core deps, not optional. "Every installation ships observability."

### `rich` library (colorized console)

[`datalayer--earthdata-mcp-server`] — implies colorized console output, no structured observability.

### Worker logs via Cloudflare dashboard

[`cloudflare--mcp-server-cloudflare`] — host-side; not self-hostable.

### File-system based output

Logs written to `./logs/`; chart outputs to `./charts/` — both file-system based [`marlonluo2018--pandas-mcp-server`].

### Hooks-driven (SDK)

- Request hooks for telemetry; Recovery middleware for panics; Session tracking with notification channels for per-client events [`mark3labs--mcp-go`]
- Change notifications listed as supported feature; no explicit logging/metrics [`metoro-io--mcp-golang`]

### Capability toggles as proto-observability

`--init-script` for instrumentation injection; tracing and video are capability toggles rather than observability per se [`microsoft--playwright-mcp`].

### Standard logging frameworks

Kotlin/Ktor standard logging available; no MCP-level observability documented [`modelcontextprotocol--kotlin-sdk`].

### Not surfaced

- [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`] (not in budget), [`conikeec--mcpr`]
- Observability (logs/metrics/tracing/debug flags) not surfaced in nearly every sample of bin 12 — pattern across that bin, not one-off

## Host integrations

### One-click install buttons (URL protocol)

[`awslabs--mcp`] surfaces one-click install URLs for: Kiro, Cursor, VS Code, Cline with Amazon Bedrock, Windsurf, Claude Code. Shifts configuration burden from copy-paste JSON to deep links.

### Claude Desktop JSON

Most samples document a JSON `mcpServers` snippet. Examples (non-exhaustive): [`awslabs--bedrock-kb-retrieval-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`], [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`cloudflare--mcp-server-cloudflare`], [`makenotion--notion-mcp-server`] (`claude_desktop_config.json`), [`marlonluo2018--pandas-mcp-server`] (Windows/macOS/Linux config paths), [`metoro-io--mcp-golang`] (`~/Library/Application Support/Claude/claude_desktop_config.json` with executable path and env vars), [`microsoft--playwright-mcp`], [`modelcontextprotocol--servers`] (top-level snippet plus per-server READMEs), [`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`stripe--agent-toolkit`], [`teaguesterling--duckdb_mcp`] (via `.mcp.json`), [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`], [`supabase-community--supabase-mcp`].

### Cursor

[`crystaldba--postgres-mcp`], [`cloudflare--mcp-server-cloudflare`], [`sooperset--mcp-atlassian`], [`stripe--agent-toolkit`] (with shipped `.cursor-plugin/`), [`supabase-community--supabase-mcp`], [`makenotion--notion-mcp-server`] (`.cursor/mcp.json`), [`microsoft--playwright-mcp`], [`metoro-io--mcp-golang`] (`.cursorrules` file present).

### Windsurf

[`crystaldba--postgres-mcp`], [`supabase-community--supabase-mcp`].

### Goose

[`crystaldba--postgres-mcp`].

### Qodo Gen

[`crystaldba--postgres-mcp`].

### Cline (with config files like `cline_mcp_settings.json`)

[`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`spences10--mcp-turso-cloud`].

### Zed

[`makenotion--notion-mcp-server`] (`settings.json`), [`modelcontextprotocol--servers`] (`settings.json` snippet in per-server README for git).

### VS Code

[`modelcontextprotocol--servers`] (`mcp.json` workspace/user config snippets in per-server READMEs for git), [`microsoft--playwright-mcp`].

### Claude Code

Listed for [`microsoft--playwright-mcp`].

### GitHub Copilot CLI

Documented for [`makenotion--notion-mcp-server`].

### WSL

[`spences10--mcp-turso-cloud`] — explicit configuration guidance.

### Cloudflare AI Playground (first-party)

[`cloudflare--mcp-server-cloudflare`].

### OpenAI Responses API

[`cloudflare--mcp-server-cloudflare`].

### JupyterLab as host

[`datalayer--jupyter-mcp-server`] — server mounts as Jupyter Server extension.

### Cloud-DB targets

AWS RDS, Azure SQL, Google Cloud SQL — [`crystaldba--postgres-mcp`].

### Vercel AI SDK

- [`supabase-community--supabase-mcp`] — native MCP client integration via `createToolSchemas()` SDK export. First-class non-Claude integration via shipped tool-schema generator
- [`stripe--agent-toolkit`] — `@stripe/ai-sdk` package for Vercel integration

### Codex plugin

[`blazickjp--arxiv-mcp-server`] — `.codex-plugin/` integration manifest in repo root; first-class Codex plugin shape.

### Claude Code skills (in-repo)

[`blazickjp--arxiv-mcp-server`] — `skills/` directory; explicit Claude Code skill wrapper co-located with the MCP server. Ships integration artifacts for three different host ecosystems in one repo: standard MCP (`src/`), Codex (`.codex-plugin/`), Claude Code skills (`skills/`).

### Claude Code plugin wrapper

- [`stripe--agent-toolkit`] — `.claude-plugin/` directory at repo root
- None observed across all 8 samples in bin 4 — [`ckreiling--mcp-server-docker`], [`cloudflare--mcp-server-cloudflare`], [`conikeec--mcpr`], [`crystaldba--postgres-mcp`], [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- Neither plugin format shipped — [`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`supabase-community--supabase-mcp`], [`teaguesterling--duckdb_mcp`], [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`]
- None observed in bin 8 — [`makenotion--notion-mcp-server`], [`microsoft--playwright-mcp`], [`marlonluo2018--pandas-mcp-server`], [`misbahsy--video-audio-mcp`], [`mark3labs--mcp-go`], [`metoro-io--mcp-golang`], [`modelcontextprotocol--kotlin-sdk`], [`modelcontextprotocol--servers`]

#### `.mcp.json` at repo root

[`modelcontextprotocol--servers`] has `.mcp.json` at repo root (no `.claude-plugin/` directory).

### Smithery

- [`baryhuang--mcp-server-aws-resources-python`] — registry entry, install via `@smithery/cli`
- [`datalayer--earthdata-mcp-server`] — `smithery.yaml` first-class artifact

### Multi-REPL (Clojure ecosystem)

[`bhauman--clojure-mcp`] — Shadow-cljs (ClojureScript), Babashka, Basilisp, Scittle environment detection and switching. Multi-REPL support is a Clojure-ecosystem-specific axis.

### Long-tail host listings

Playwright explicitly lists ≥20 supported clients — a marketing-shaped breadth play that exceeds typical MCP server host coverage. Clients listed: Claude Desktop, Claude Code, VS Code, Cursor, Windsurf, Cline, Goose, Junie, Copilot, Factory, Gemini CLI, LM Studio, Kiro, opencode, Qodo Gen, Warp, Codex, Antigravity, Amp [`microsoft--playwright-mcp`]. Zencoder also mentioned in one git README [`modelcontextprotocol--servers`].

### Browser-clients via CORS

Kotlin SDK supports browser-based clients via Ktor CORS configuration — uncommon for MCP servers [`modelcontextprotocol--kotlin-sdk`].

### SDK-level: no host integrations documented

SDKs do not document host-config snippets — applications using the SDK handle that [`mark3labs--mcp-go`, `modelcontextprotocol--kotlin-sdk`].

### Agent-facing meta-documentation in repo

`CLAUDE.md` shipped in the server repo itself — guidance for Claude when working on the repo. Distinct from host-config snippets; this is documentation for the agent acting as a developer on the repo, not as a runtime tool user [`makenotion--notion-mcp-server`].

### Generic JSON snippet pattern (not host-specific)

[`datalayer--jupyter-mcp-server`], [`conikeec--mcpr`].

## Tests

### pytest stack

- pytest + pytest-asyncio + pytest-cov + pytest-mock — [`awslabs--mcp`] (per-server config: `python_files = "test_*.py"`, `python_classes = "Test*"`, `testpaths = ["tests"]`)
- pytest ≥8.3.5, pytest-asyncio ≥0.26.0, pytest-cov ≥4.1.0 — [`chroma-core--chroma-mcp`]
- pytest, `tests/` directory — [`blazickjp--arxiv-mcp-server`]
- pytest + pytest-asyncio (`asyncio_default_fixture_loop_scope = "function"`, `pythonpath = ["./src"]` src-layout) — [`crystaldba--postgres-mcp`]
- pytest with `test` extra (`pytest>=7.0`) — [`datalayer--earthdata-mcp-server`]
- pytest (pulls jupyter components and collab tools; `pytest.ini` present) — [`datalayer--jupyter-mcp-server`]
- pytest + pytest-asyncio + pytest-cov — [`the-momentum--fhir-mcp-server`]
- pytest + pytest-cov + pytest-asyncio + pytest-anyio (both async runtimes side-by-side) — [`sooperset--mcp-atlassian`]
- pytest with coverage — [`tumf--grafana-loki-mcp`]
- 30+ pytest functions in `tests/`; pytest declared as a runtime dep (unusual — should be a dev dep) — [`misbahsy--video-audio-mcp`]
- `test_metadata.py`, `test_execution.py`, `test_generate_barchart.py` at repo root rather than `tests/` directory — nonstandard location [`marlonluo2018--pandas-mcp-server`]
- Per-server `tests/` directories. fetch: pytest + pytest-asyncio with `asyncio_mode = "auto"`; git: pytest only (no asyncio); `testpaths = ["tests"]`, `python_files = "test_*.py"` — [`modelcontextprotocol--servers`]

### Make-driven

[`thenets--ghost-mcp`] — `make test` and `make test-connection`. [`teaguesterling--duckdb_mcp`] — `make test`.

### TS test runners

- Bun test runner with Vitest compatibility, coverage reports — [`cyanheads--git-mcp-server`]
- Vitest across the monorepo — [`cloudflare--mcp-server-cloudflare`]
- TypeScript noEmit type check via `npm test` (type-check as test) — [`cyanheads--perplexity-mcp-server`]
- Vitest with `npm test`, `npm run test:watch`, `npm run test:coverage`; `NODE_ENV=test`; coverage reports — [`makenotion--notion-mcp-server`]

### Go stdlib testing

- `*_test.go` files plus `e2e/` directory; unit + end-to-end tests — [`mark3labs--mcp-go`]
- `server_test.go` (21.7 KB), `integration_test.go` (10.1 KB); integration testing patterns — [`metoro-io--mcp-golang`]

### Multiplatform Kotlin testing

[`modelcontextprotocol--kotlin-sdk`] — `kotlin-sdk-testing` module, `integration-test/`, `conformance-test/` directories, `test-utils/` shared utilities; Knit properties for code-snippet testing — testing infrastructure split into separately-versioned components.

### Test infrastructure shape

#### Conformance vs functional tests

Kotlin SDK splits tests into integration + conformance against the MCP spec — explicit conformance category beyond pass/fail unit tests [`modelcontextprotocol--kotlin-sdk`].

#### Test-fixture as published artifact

`kotlin-sdk-testing` is a distinct artifact (`io.modelcontextprotocol:kotlin-sdk-testing`) — testing utilities packaged for downstream consumption [`modelcontextprotocol--kotlin-sdk`].

#### Mock transport implementations

[`conikeec--mcpr`] — across stdio and SSE.

### Custom marker

- `live` for API-calling tests — [`awslabs--mcp`]
- `integration`, `dc_e2e` (Data Center e2e), `cloud_e2e` (Cloud e2e) — [`sooperset--mcp-atlassian`]. Encodes the on-prem/cloud deployment matrix into the test suite, not just CI config

### Test data strategy

AI-generated adversarial workloads — [`crystaldba--postgres-mcp`].

### Dev extras

[`awslabs--mcp-lambda-handler`] — `pip install -e .[dev]`; framework not extracted.

### Native test framework

[`bhauman--clojure-mcp`] — typical Clojure testing patterns; `test/` directory.

### Not surfaced

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`], [`ckreiling--mcp-server-docker`], [`spences10--mcp-turso-cloud`], [`stripe--agent-toolkit`], [`supabase-community--supabase-mcp`].

## CI

### GitHub Actions

- Workflows + `tests.yml` with badge — [`blazickjp--arxiv-mcp-server`]
- `.github/workflows/` — [`chroma-core--chroma-mcp`], [`baryhuang--mcp-server-aws-resources-python`]
- `.github/workflows`, `.ruff.toml`, `.pre-commit-config.yaml`, `.secrets.baseline`, OSSF Scorecard, Codecov badge — [`awslabs--mcp`]
- Configured in `.github/` — [`bhauman--clojure-mcp`]
- Present (specifics not surfaced) — [`ckreiling--mcp-server-docker`]
- [`conikeec--mcpr`], [`crystaldba--postgres-mcp`], [`cyanheads--perplexity-mcp-server`] (`.github/` present, README does not document)
- Lint + type-check pipeline — [`datalayer--earthdata-mcp-server`]
- [`datalayer--jupyter-mcp-server`]
- [`sooperset--mcp-atlassian`], [`supabase-community--supabase-mcp`], [`teaguesterling--duckdb_mcp`], [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`], [`stripe--agent-toolkit`] (specifics not extracted)
- GitHub Actions + Turbo monorepo orchestration — [`cloudflare--mcp-server-cloudflare`]
- `npm run devcheck` (lint, format, typecheck) + dependency audit + unit + integration suite — [`cyanheads--git-mcp-server`]
- Workflows present in `.github/workflows`; build + test in pipeline — [`makenotion--notion-mcp-server`]
- `ci.yml` (main testing), `golangci-lint.yml` (linting), `pages.yml` (documentation), `release.yml` (release automation); triggers on push/PR — [`mark3labs--mcp-go`]
- Configured; typical Go project structure implies test+lint workflows — [`metoro-io--mcp-golang`]
- Configured; typical Gradle/Kotlin project structure — [`modelcontextprotocol--kotlin-sdk`]
- Active release pipeline (60 releases for Playwright) — [`microsoft--playwright-mcp`]

### Per-server in monorepo

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--openapi-mcp-server`] inherit from the parent monorepo's CI. [`modelcontextprotocol--servers`] has `.github/workflows` at top level; per-server test infrastructure not prominent in individual READMEs.

### Documented vs configured

CI workflow files may be documented as a pattern but not actually configured — `video-audio-mcp` shows a GitHub Actions YAML example in README; actual `.github/workflows/*.yml` presence not confirmed [`misbahsy--video-audio-mcp`].

### Auxiliary automation

[`spences10--mcp-turso-cloud`] — `.changeset/` (changelog management) + `renovate.json` (dependency automation); explicit Actions workflows not confirmed.

### Beyond test+lint workflows

- Documentation-site builds — `pages.yml` for documentation publishing [`mark3labs--mcp-go`]
- Release automation as separate workflow — `release.yml` [`mark3labs--mcp-go`]

## Container / packaging artifacts

### Dockerfile

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`] (per server), [`baryhuang--mcp-server-aws-resources-python`] (multi-arch linux/amd64, arm64, arm/v7), [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`cyanheads--perplexity-mcp-server`] (multi-stage Node 18-Alpine), [`cyanheads--git-mcp-server`] (implied by Bun build), [`datalayer--earthdata-mcp-server`] (also pre-built image on Docker Hub), [`datalayer--jupyter-mcp-server`], [`makenotion--notion-mcp-server`] (Node.js-based + `docker-compose.yml` + `mcp/notion`), [`microsoft--playwright-mcp`] (multi-arch on `mcr.microsoft.com/playwright/mcp`), [`modelcontextprotocol--servers`] (per-server Dockerfile e.g. `src/filesystem/Dockerfile`, `src/git/Dockerfile`, `src/fetch/Dockerfile`; images published as `mcp/<server-name>`), [`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`].

### Docker Compose

- [`the-momentum--fhir-mcp-server`] — for server deployment
- [`thenets--ghost-mcp`] — Docker Compose for full Ghost + MySQL test stack (target backend, not the MCP server itself); end-to-end dev-stack bundling, more typical of integration-test frameworks
- [`makenotion--notion-mcp-server`] — `docker-compose.yml` alongside Dockerfile

### Lambda zip (no Dockerfile)

[`awslabs--mcp-lambda-handler`] — Lambda is the packaging target.

### Devcontainer

[`awslabs--mcp`] — `.devcontainer/` configuration at root for dev workflow. [`sooperset--mcp-atlassian`].

### Container quality-of-life

- Docker host-address auto-remap (localhost → host.docker.internal on macOS/Windows, 172.17.0.1 on Linux) — [`crystaldba--postgres-mcp`] flagged "rarely seen"
- Multi-stage Docker build — [`cyanheads--perplexity-mcp-server`]

### N/A — Workers (not containers)

[`cloudflare--mcp-server-cloudflare`].

### No container artifacts

[`spences10--mcp-turso-cloud`], [`teaguesterling--duckdb_mcp`], [`supabase-community--supabase-mcp`] (managed cloud reduces need), [`tumf--grafana-loki-mcp`] (explicitly absent), [`marlonluo2018--pandas-mcp-server`], [`misbahsy--video-audio-mcp`].

### SDK without container artifacts

[`mark3labs--mcp-go`], [`metoro-io--mcp-golang`], [`modelcontextprotocol--kotlin-sdk`] — examples may include containerization.

### Not documented

[`conikeec--mcpr`], [`stripe--agent-toolkit`].

### Registry registration

`smithery.yaml` for Smithery registry — [`datalayer--earthdata-mcp-server`] (first-class repo artifact).

## Repo layout

### Single package (Python)

- `src/<package_name>/` — [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`crystaldba--postgres-mcp`] (src-layout with `pythonpath = ["./src"]`), [`ckreiling--mcp-server-docker`] (`src/mcp_server_docker/`), [`thenets--ghost-mcp`] (`src/ghost_mcp/`)
- Without explicit src-layout — [`datalayer--earthdata-mcp-server`] (`earthdata_mcp_server/` + `dev/` + `docs/`), [`datalayer--jupyter-mcp-server`] (`jupyter_mcp_server/` + `jupyter-config/` + `docs/`), [`the-momentum--fhir-mcp-server`] (`app/` module)
- [`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`teaguesterling--duckdb_mcp`], [`tumf--grafana-loki-mcp`]
- Single-file server (`server.py`) — [`misbahsy--video-audio-mcp`]
- Flat layout — `/core` subdirectory (metadata, execution, visualization, chart_generators); scripts at root [`marlonluo2018--pandas-mcp-server`]

### Single package (TS Node)

- [`cyanheads--perplexity-mcp-server`] (`.github/`, `src/`, `docs/`)
- [`cyanheads--git-mcp-server`] (organized by concern: tools/, resources/, transports/, services/, storage/, config/, utils/, container/; tests mirror structure)
- [`makenotion--notion-mcp-server`] — `src/`, `docs/`, `scripts/`, `.github/`; config: `package.json`, `tsconfig.json`, `vitest.config.ts`, `Dockerfile`, `docker-compose.yml`; documentation: `CLAUDE.md`, `README.md`

### Single Clojure package

[`bhauman--clojure-mcp`] — `src/`, `test/`, `doc/`, `resources/`, `deps.edn`, `docs/`.

### Single Rust library + `/examples/`

[`conikeec--mcpr`].

### SDK with functional subdirectories (Go)

- `mcp/` (protocol), `client/`, `server/`, `util/`, `mcptest/`, `examples/`, `e2e/`, `.github/` — [`mark3labs--mcp-go`]
- Root-level `client.go`, `server.go`, `content_api.go`, `prompt_api.go`, `prompt_response_types.go`, `tool_api.go`, `tool_response_types.go`, `resource_api.go`, `resource_response_types.go`; subdirectories: `internal/`, `transport/`, `resources/`, `examples/`, `docs/`, `.github/` — [`metoro-io--mcp-golang`]

### Sub-package in monorepo

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--openapi-mcp-server`] all live under `awslabs/mcp/src/<service>/`.

### Monorepo-of-packages

- [`awslabs--mcp`] — 40+ servers, central dev tooling at root with per-server pyproject.toml. Classic uv workspace layout (though `[tool.uv.workspace]` not confirmed)
- [`cloudflare--mcp-server-cloudflare`] — Turbo/pnpm monorepo with 14 domain Workers + shared `@repo/mcp-common`
- [`stripe--agent-toolkit`] — multiple SDK packages (Python + TS) coexist with MCP, Vercel-AI integration, and billing components. `.claude-plugin/` and `.cursor-plugin/` ship alongside code
- [`supabase-community--supabase-mcp`] — `/packages` (core packages), `/docs`, `/supabase`, pnpm-managed (`pnpm-workspace.yaml`)
- [`microsoft--playwright-mcp`] — monorepo with `/packages` directory
- [`modelcontextprotocol--servers`] — `src/<server>/` per reference server, root has shared `package.json`, `tsconfig.json`, `.npmrc`; Python servers self-contained inside the same directory tree

### Monorepo (multi-module SDK, Gradle)

[`modelcontextprotocol--kotlin-sdk`] — `kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, `kotlin-sdk` (umbrella); supporting: `samples/`, `docs/`, `config/`, `integration-test/`, `conformance-test/`, `.github/`, `buildSrc/`.

### Multi-host artifact bundle

[`blazickjp--arxiv-mcp-server`] — single repo bundles standard MCP (`src/`), Codex (`.codex-plugin/`), Claude Code skills (`skills/`).

### Docs sets

- README + MCP.md + CHANGELOG + CONTRIBUTING — [`conikeec--mcpr`]
- README + `docs/` — [`cyanheads--perplexity-mcp-server`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]

## Build backend / packaging

### hatchling

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`chroma-core--chroma-mcp`], [`crystaldba--postgres-mcp`] (`hatchling.build`), [`datalayer--earthdata-mcp-server`] (~1.21), [`datalayer--jupyter-mcp-server`] (~1.21), [`sooperset--mcp-atlassian`], [`modelcontextprotocol--servers`] (across sampled Python reference servers; standalone uv package per subdir).

### `uv_build` with non-standard module name

[`the-momentum--fhir-mcp-server`] — module-name `app`. Adoption of `uv`'s native build-backend integration; less common than hatchling.

### Mixed pyproject.toml + setup.py

[`tumf--grafana-loki-mcp`].

### Backend present, not surfaced

[`ckreiling--mcp-server-docker`], [`thenets--ghost-mcp`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`].

### Lock file conventions

- `uv.lock` committed — [`blazickjp--arxiv-mcp-server`]; uv.lock + uv-managed (`uv sync`) — [`crystaldba--postgres-mcp`]
- Devbox + uv combo — [`ckreiling--mcp-server-docker`]
- `uv` convention — [`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`]
- `uv` + pip compatible — [`tumf--grafana-loki-mcp`]
- Standard PyPI publication via hatchling, lock not confirmed — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- `uv.lock` implied — [`misbahsy--video-audio-mcp`]
- `requirements.txt` only (no uv.lock), pip-only — [`marlonluo2018--pandas-mcp-server`]
- Not confirmed — [`awslabs--mcp`], [`chroma-core--chroma-mcp`], others

### Version manager convention

- `uv` — most Python samples
- pip — [`awslabs--mcp-lambda-handler`] (uv not emphasized), [`marlonluo2018--pandas-mcp-server`] (pip-only the exception)

### Lint and typecheck pinned across servers

`pyright>=1.1.389`, `ruff>=0.7.3` pinned across all sampled Python reference servers — per-server consistency in dev tooling [`modelcontextprotocol--servers`].

### `pytest` accidentally in runtime deps

`pytest` declared as a runtime dep — likely an oversight; tests shouldn't require installing pytest for users running the server [`misbahsy--video-audio-mcp`].

## Developer ergonomics

### Makefile-driven

- [`thenets--ghost-mcp`] (`make run`, `make dev`, `make test`, `make test-connection`)
- [`the-momentum--fhir-mcp-server`] (`make build`, `make uv`, `make test-connection`)
- [`teaguesterling--duckdb_mcp`] (`make`, `make test`)

> Uncommon among MCP servers; common in data-ops projects.

### `mise.toml`

[`supabase-community--supabase-mcp`] — toolchain version pinning.

### Devbox (reproducible dev environment)

[`ckreiling--mcp-server-docker`] — rarer than direnv/asdf.

### `devenv.*` files

[`crystaldba--postgres-mcp`] — for reproducible environments.

### Pre-commit hooks

[`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`], [`tumf--grafana-loki-mcp`].

### Linters and formatters

- ruff + black + mypy (double formatter, redundant) — [`sooperset--mcp-atlassian`], [`tumf--grafana-loki-mcp`]
- ruff + ty (newer alternative to mypy) — [`the-momentum--fhir-mcp-server`]
- biome (TypeScript) — [`supabase-community--supabase-mcp`]
- Exact-version pinning of dev tooling (`ruff==0.14.13`, `pyright==1.1.408`) — [`crystaldba--postgres-mcp`] (flagged "unusually strict")

### AI-targeted documentation

- `llms.txt` file present; design-for-AI-consumption documentation pattern — [`sooperset--mcp-atlassian`]
- `CLAUDE.md` shipped in the server repo itself — [`makenotion--notion-mcp-server`]
- `LLM_CODE_STYLE.md` for AI assistant prompt guidance (unusual) — [`bhauman--clojure-mcp`]

### Documentation-heavy repo

[`bhauman--clojure-mcp`] — README.md (30KB), PROJECT_SUMMARY.md (26KB), CONFIG.md (9KB), FAQ.md (8KB), CHANGELOG, BIG_IDEAS, LLM_CODE_STYLE; substantial for a single-package repo.

### Optional-deps taxonomy

Clean PEP 621 grouping into `test` / `lint` / `typing` extras — [`datalayer--earthdata-mcp-server`] (also `mdformat` + `mdformat-gfm` in lint extras for markdown-as-CI), [`datalayer--jupyter-mcp-server`] (`lint`, `typing`, `mcp[cli]` extras).

### Sample/example directories

- 20 example implementations included covering client, server, HTTP, SSE, OAuth, roots, sampling, structured tools, tasks; patterns for in-process integration and custom transports — [`mark3labs--mcp-go`]
- Server and client examples; documentation at mcpgolang.com; Metoro Kubernetes server as production reference implementation — [`metoro-io--mcp-golang`]
- Sample implementations in `./samples/` covering various transport configurations — [`modelcontextprotocol--kotlin-sdk`]

### Companion documentation site

- Documentation at mcpgolang.com — [`metoro-io--mcp-golang`]
- `pages.yml` workflow for doc-site publishing — [`mark3labs--mcp-go`]

### Multi-host config snippets in README

- Configuration examples for 4 host integrations; Docker installation documented; local symlink testing via `npm link` for Cursor — [`makenotion--notion-mcp-server`]
- Each server README includes copy-paste JSON snippets for Claude Desktop and often VS Code — [`modelcontextprotocol--servers`]

### Live-reload dev mode

`npm run dev` (tsx watch) for hot reload during development — [`makenotion--notion-mcp-server`].

## Notable structural choices

Cross-cutting design commitments worth elevating beyond their categorization-tree position. Patterns already fully expressed in the categorized sections above are noted here only when their corpus-level significance warrants emphasis; specifics are not duplicated.

### Dependency footprint extremes

- Lean: 4 deps (boto3, loguru, mcp, pydantic) [`awslabs--bedrock-kb-retrieval-mcp-server`]; 3 deps with pure-stdlib protocol handling [`awslabs--mcp-lambda-handler`]
- Fat: bundles three cloud embedding SDKs (openai, cohere, voyageai) in core deps for zero-friction provider switching [`chroma-core--chroma-mcp`]

### Auto-release sentinel version

[`awslabs--openapi-mcp-server`] — pyproject.toml version was `0.9223372036854775807.9223372036854775807` (int64 max); appears to be an automated-release sentinel, not a human-chosen version.

### Multi-spec API gateway pattern

[`awslabs--openapi-mcp-server`] — single server fronts many APIs via `--additional-specs`, each with independent auth and HTTP clients; "one gateway to many SaaS APIs".

### Server-framework distinction

[`awslabs--mcp-lambda-handler`] is a sub-package in an MCP-server monorepo that is itself not a server but a library — reveals a structural category the per-server schema does not anticipate. Session management as a pluggable extension point (NoOp/DynamoDB/custom). [`conikeec--mcpr`], [`mark3labs--mcp-go`], [`metoro-io--mcp-golang`], [`modelcontextprotocol--kotlin-sdk`] are similar library-not-server artifacts.

### Agent-augmented tools (server's tools call out to LLMs)

[`bhauman--clojure-mcp`] — agent tools with optional external LLM integration (Anthropic, OpenAI, Google Gemini); the server's tools are themselves LLM-orchestrated.

### Built-in client-side rate limit

[`blazickjp--arxiv-mcp-server`] — 3-second minimum rate-limit enforcement at the client layer; reflects arXiv's rate-limit guidance.

### Hosting responsibility as a design axis

- Server author operates the runtime, end users only consume URLs — [`cloudflare--mcp-server-cloudflare`] flags "hosting responsibility" with downstream effects on release, auth, and observability. Opposite end of the spectrum from local stdio servers
- Stdio emulation via shim on the client side rather than on the server — `mcp-remote` translates stdio↔HTTP so hosts still speak stdio while server speaks HTTP [`cloudflare--mcp-server-cloudflare`]
- Paid-plan gating: some Cloudflare features require Workers paid plan; "operational cost surfaces as a server capability axis" [`cloudflare--mcp-server-cloudflare`]

### Hosted-endpoint + local stdio duality

[`stripe--agent-toolkit`], [`supabase-community--supabase-mcp`] — Sentry / Cloudflare also follow this pattern.

### Domain knowledge embedded in server

- Deterministic optimization algorithms (greedy search adapted from Microsoft Anytime), workload compression, hypothetical indexing via `hypopg`, Pareto-front cost-benefit balancing — [`crystaldba--postgres-mcp`] "embedded performance-tuning intelligence goes far beyond typical SQL-execution MCP servers"; optional OpenAI integration for experimental LLM-based index tuning
- Auto-complexity detection to switch between fast search and deep research tools — [`cyanheads--perplexity-mcp-server`]
- Two-phase version negotiation in server initialization handshake — [`conikeec--mcpr`]

### Sibling-package factoring

Tool definitions factored into a separate PyPI project (`jupyter-mcp-tools>=0.1.6`) — [`datalayer--jupyter-mcp-server`]; unusual reuse pattern in MCP land.

### Shared monorepo scaffolding

Internal `@repo/mcp-common` workspace package abstracts shared server scaffolding across 14 domain Workers — [`cloudflare--mcp-server-cloudflare`] mirrors Cloudflare's own platform composition patterns.

### Vendor/community canonical positioning

Community-canonical at vendor scale — [`sooperset--mcp-atlassian`] (5k stars on a non-vendor repo for Atlassian indicates the vendor has not shipped first-party). Same shape: [`spences10--mcp-turso-cloud`].

### Multi-surface agent tooling

[`stripe--agent-toolkit`] — one repo houses SDKs (Python + TS), AI-framework integrations (Vercel), billing primitives, and MCP — MCP treated as one integration channel among peers, not the whole product.

### Server-blurring architectures

- MCP-as-SQL-extension — MCP surface reachable via SQL PRAGMAs; blurs database and tool-registry roles [`teaguesterling--duckdb_mcp`]
- Dual server + client mode — server for AI assistants AND client connecting to other MCP resources via SQL `ATTACH`; single artifact plays both protocol roles [`teaguesterling--duckdb_mcp`]
- In-server RAG pipeline — embedding + vector-store + document-parsing stack inside the MCP process; most servers expose tools that call upstream RAG; this one hosts the RAG itself [`the-momentum--fhir-mcp-server`]

### Compliance-driven encryption features

[`the-momentum--fhir-mcp-server`] — master-key encryption for sensitive credentials; design axis emerging from regulated domains (healthcare, finance, legal).

### Deployment-mode coverage

[`sooperset--mcp-atlassian`] — Cloud + on-prem (Confluence v6.0+, Jira v8.14+) with explicit version floors; deliberate enterprise compatibility uncommon outside first-party vendors.

### Plan-tier gating in the tool surface

[`supabase-community--supabase-mcp`] — Branching tools surfaced as paid/experimental in feature groups; commercial constraints leak into MCP capability listing.

### Dev-stack bundling vs server packaging

[`thenets--ghost-mcp`] — Docker Compose for the target CMS+DB (Ghost+MySQL), not for deploying the MCP server itself; bundles backend stack to enable end-to-end dev. Notable investment for a 1-star repo.

### Proxy-via-fronting-service architecture

[`tumf--grafana-loki-mcp`] — uses Grafana's Loki API as intermediary rather than Loki directly; piggybacks on Grafana auth instead of adding a separate Loki credential surface.

### Server-managed credential lifecycle

JWT auto-renewal [`thenets--ghost-mcp`], encrypted credential vault [`the-momentum--fhir-mcp-server`], short-lived child-token generation [`spences10--mcp-turso-cloud`]. Most MCP servers assume static creds; these don't.

### Domain-ontology bridges

[`the-momentum--fhir-mcp-server`] (LOINC) — pattern likely to recur in legal (Westlaw), education (curriculum standards), finance (ticker/ISIN) per the sample's own observation.

### Schema export as composable SDK

[`supabase-community--supabase-mcp`] — `createToolSchemas()` doubles the repo as an SDK; consumers can use Supabase tool definitions without routing through MCP.

### Multi-host artifact bundling in one repo

[`blazickjp--arxiv-mcp-server`] — one MCP server, three host-native plugin wrappers (MCP `src/`, Codex `.codex-plugin/`, Claude Code `skills/`). Each host ecosystem gets dedicated sibling integrations rather than expecting hosts to generically consume the MCP surface.

### Token-cost awareness as first-class concern

[`awslabs--openapi-mcp-server`] — README quantifies token reduction (claimed 70-75%) from auto-enriched tool descriptions.

### Deprecation as a versioning signal

[`awslabs--mcp`] — SSE removal dated and documented in-repo (2025-05-26) rather than only in a changelog.

### Agent SOPs as a first-class shipped artifact

[`awslabs--mcp`] — preview aggregator bundles "pre-built Agent SOPs" alongside tools; not just raw API surface, but opinionated workflows.

### One-click install URL protocol as primary surface

[`awslabs--mcp`] — integration surface that bypasses JSON entirely for supported hosts.

### Spec-driven vs code-driven tool surface

[`awslabs--openapi-mcp-server`] vs the rest of the corpus — major design axis. Spec-driven implications: docs drift (spec is source of truth), testing (every spec change is a contract change), LLM behavior (tool descriptions inherit spec quality).

### Code-as-tool as architecture choice

[`baryhuang--mcp-server-aws-resources-python`] — one flexible code-execution tool with AST sandbox versus N hand-enumerated per-API tools. Inverts the per-API enumeration default.

### Reproducible-env tooling spread

- Devbox — [`ckreiling--mcp-server-docker`]
- devenv — [`crystaldba--postgres-mcp`]
- mise — [`supabase-community--supabase-mcp`]

### Accessibility-first browser perception

Accessibility-tree snapshots over screenshots/vision as the primary perception model. Vision opt-in via `--caps=vision`. Reverses the default assumption that browser automation needs visual models [`microsoft--playwright-mcp`].

### Programmatic embedding (library mode) as first-class

`createConnection()` means the MCP server can run inside host processes as a library, not just as an external subprocess. Blurs server/client lines [`microsoft--playwright-mcp`].

### Recovery middleware for tool-handler panics

Operational safety feature: panic in a tool handler doesn't take down the server [`mark3labs--mcp-go`].

### Heterogeneous monorepo

TS and Python live side-by-side with independent package manifests — no forced uniformity. Each server README documents its own install path (npx vs uvx vs pip vs Docker). Per-server Dockerfile with `mcp/<name>` image is the only consistent convention across servers [`modelcontextprotocol--servers`].

### Reference set deliberately avoids FastMCP

Python reference servers (git, fetch, time) use raw `mcp` SDK exclusively — no FastMCP. Suggests the reference set prioritizes low-level SDK coverage over developer convenience [`modelcontextprotocol--servers`].

### "Not a security boundary" disclaimer

Security posture explicitly disclaimed in README rather than implemented. `--allow-unrestricted-file-access` is the escape hatch [`microsoft--playwright-mcp`].

### Two-stage capability gating: install-time + runtime

`--caps=<cap>` groups (pdf, vision, testing) are install-time tool-surface gates; per-tool-category opt-ins (Network, Storage, DevTools) are runtime gates. Distinct from per-tool toggles or single read-only modes [`microsoft--playwright-mcp`].

### Conformance testing as a first-class category

Kotlin SDK includes `conformance-test/` distinct from integration tests — explicit spec-conformance discipline [`modelcontextprotocol--kotlin-sdk`].

### Multiplatform Kotlin enabling MCP outside JVM

Multiplatform support (JVM, Native, JS, Wasm) enables MCP implementations outside JVM. Modular artifact structure allows client/server-only dependencies. No transitive Ktor dependencies — developers specify engines independently [`modelcontextprotocol--kotlin-sdk`].

### Context-length mitigation

README guidance flagging chained-tool calls against high-cardinality data as a context-window concern the client must manage — [`cloudflare--mcp-server-cloudflare`].

## Notable Python-specific dependencies

### `prance` + `openapi-spec-validator`

[`awslabs--openapi-mcp-server`] — OpenAPI parsing; non-trivial deps rarely seen in MCP servers. Validation toggle for non-compliant specs.

### `tenacity`

[`awslabs--openapi-mcp-server`] — retry logic on upstream HTTP calls.

### `cachetools`

[`awslabs--openapi-mcp-server`] — in-process caching of spec/responses.

### `uvicorn` despite stdio transport

[`awslabs--openapi-mcp-server`] — suggests optional HTTP mode or internal HTTP client pool.

### `bcrypt`

[`awslabs--openapi-mcp-server`] — runtime dep; likely Basic Auth credential hashing/storage.

### `python-dateutil` only (besides AWS SDK)

[`awslabs--mcp-lambda-handler`] — suggests time-sensitive session token handling.

### `boto3` outside AWS-specific servers

[`awslabs--openapi-mcp-server`] depends on both `fastmcp` and `boto3` (for Cognito auth) — boto3 used beyond pure AWS-API servers.

### `pglast` (SQL parser for restricted-mode write rejection)

[`crystaldba--postgres-mcp`].

### `hypopg` (hypothetical indexing)

[`crystaldba--postgres-mcp`].

### Heavy Jupyter stack baked in

[`datalayer--jupyter-mcp-server`] — `jupyter_server`, `tornado>=6.1`, `fastapi`, `uvicorn` baked in; reflects "this server brokers a live Jupyter kernel rather than a stateless data layer". `opentelemetry-api/sdk` as hard deps — designed for production observability out of the box.

### RAG stack baked in

[`the-momentum--fhir-mcp-server`] — llama-index + huggingface + pinecone + sentence-transformers + pymupdf inside the MCP server.

### Caret-pinned upper bounds

[`awslabs--openapi-mcp-server`] — `,<4`, `,<1` throughout; stricter compatibility stance than typical Python projects.

### Exact-pin SDK

[`chroma-core--chroma-mcp`] — `mcp[cli]==1.6.0` exact pin; unusually tight for a 2025 vendor server.

### `earthaccess`

[`datalayer--earthdata-mcp-server`] — delegates the NASA auth dance.

### `rich`

[`datalayer--earthdata-mcp-server`] — colorized console output.

## Gaps

- Whether the `uvicorn` dep in [`awslabs--openapi-mcp-server`] indicates undocumented HTTP transport
- Test coverage details for [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`]
- How `@mcp.tool()` decorator maps to MCP protocol without `fastmcp` in [`awslabs--mcp-lambda-handler`]
- Whether streaming responses are supported in [`awslabs--mcp-lambda-handler`] given Lambda response-size constraints
- Exact `mcp` SDK version pin in [`blazickjp--arxiv-mcp-server`]
- Contents of `skills/` and `.codex-plugin/` manifest formats in [`blazickjp--arxiv-mcp-server`]
- Whether [`awslabs--mcp`] root pyproject.toml declares `[tool.uv.workspace]`
- Specific Java version constraints (JDK 17+ inferred but not confirmed) in [`bhauman--clojure-mcp`]
- nREPL transport protocol details in [`bhauman--clojure-mcp`]
- Python version floor, test presence, last-commit date for [`baryhuang--mcp-server-aws-resources-python`]
- Exact last-commit dates often inferred from release tags or pushed_at timestamps rather than raw commit dates — [`cloudflare--mcp-server-cloudflare`], [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`ckreiling--mcp-server-docker`]
- Async/sync behavior, schema strategy, and test presence sometimes not surfaced in READMEs — [`ckreiling--mcp-server-docker`]
- Lock-file conventions not always confirmed — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- Whether CI publishes to PyPI on tag not always confirmed — [`datalayer--earthdata-mcp-server`]
- Logging/observability specifics not always documented — [`crystaldba--postgres-mcp`]
- Toolset-gating consistency across domain servers in monorepos not always documented — [`cloudflare--mcp-server-cloudflare`]
- Self-hostable variant deployability for hosted-only repos sometimes unclear — [`cloudflare--mcp-server-cloudflare`] (source ships, docs focus on hosted URLs)
- For archived libs, supersession status often unclear — [`conikeec--mcpr`]
- Tool-scoping for large surfaces (e.g. 72-tool [`sooperset--mcp-atlassian`]) often unspecified — how users reduce a large surface to a working subset is rarely documented; contrast with [`supabase-community--supabase-mcp`]'s explicit `features` param
- Transport names not always in README — [`spences10--mcp-turso-cloud`], [`thenets--ghost-mcp`] omit explicit transport documentation; stdio is inferred from invocation pattern
- Observability (logs/metrics/tracing/debug flags) not surfaced in nearly every sample of bin 12
- Last-commit dates inconsistently captured
- Container artifact presence/absence consistently noted but content (multi-stage builds, base image choices) is not
- Notion MCP: logging/observability, rate limiting, Notion API quota handling, V2.0 migration not in README — [`makenotion--notion-mcp-server`]
- mcp-go: explicit language version tested in CI not confirmed; Docker production patterns not documented in SDK; full CI workflow contents not enumerated — [`mark3labs--mcp-go`]
- pandas: `pandas-mcp-cli` PyPI publication not verified; License/CI/Docker absence vs not documented unclear; exact dependency pin list beyond pandas/fastmcp/chardet/psutil not read — [`marlonluo2018--pandas-mcp-server`]
- mcp-golang: HTTPS custom auth marked experimental — implementation details not documented; specific Go version not specified; Makefile not present; full CI/CD configuration not examined — [`metoro-io--mcp-golang`]
- Playwright: exact Node.js version constraint; whether auth can be added via programmatic API; CI workflow specifics — [`microsoft--playwright-mcp`]
- video-audio: console-script presence (pyproject omitted `[project.scripts]`); actual build backend; whether CI is real or only documented as pattern; FastMCP-in-SDK vs standalone confirmation — [`misbahsy--video-audio-mcp`]
- Kotlin SDK: specific Ktor version constraints; observability/logging patterns; Docker/containerization guidance; complete transport-selection pattern — [`modelcontextprotocol--kotlin-sdk`]
- mcp/servers: exact last-commit date (only release tag visible); specific CI workflow contents per server; whether any server supports non-stdio transports; full enumeration of published packages for all seven servers (only three sampled in depth) — [`modelcontextprotocol--servers`]
