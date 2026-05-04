# Sample

Stage-1 M2 merge of bins 3, 4, 12.

## Identification

### License

- MIT — [`conikeec--mcpr`], [`crystaldba--postgres-mcp`]
- Apache-2.0 — [`cloudflare--mcp-server-cloudflare`], [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- BSD-3-Clause — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- GPL-3.0 — [`ckreiling--mcp-server-docker`] (called out as unusual: ecosystem skews MIT/Apache)

### Ownership

#### Vendor-owned

Stripe ships from `stripe/agent-toolkit` [`stripe--agent-toolkit`]. Supabase community-org under company watch — `supabase-community/supabase-mcp` is community-canonical with vendor signaling [`supabase-community--supabase-mcp`].

#### Community-canonical without vendor entry

Atlassian has no first-party MCP — `sooperset/mcp-atlassian` (5k stars) is the de facto standard [`sooperset--mcp-atlassian`]. Turso similarly: `spences10/mcp-turso-cloud` is community-built, not under `tursodatabase/*` [`spences10--mcp-turso-cloud`]. Ghost CMS [`thenets--ghost-mcp`] (1 star, very new). Grafana Loki [`tumf--grafana-loki-mcp`].

#### Domain-specific community

`teaguesterling/duckdb_mcp` — DuckDB extension built externally to the DuckDB project [`teaguesterling--duckdb_mcp`]. `the-momentum/fhir-mcp-server` — FHIR-agnostic healthcare server, not tied to any single FHIR vendor [`the-momentum--fhir-mcp-server`].

### Repository status

- Active main-branch development is the norm.
- Archived repository — [`conikeec--mcpr`] archived as of February 8, 2026; v0.2.0 yanked due to SSE issues, v0.2.3+ recommended. Pre-archive Rust libs may already be superseded.

### Maturity signals

Star-count spread is enormous within the corpus: 5,000 [`sooperset--mcp-atlassian`], 3,600 [`cloudflare--mcp-server-cloudflare`], 2,600 [`crystaldba--postgres-mcp`], 2,600 [`supabase-community--supabase-mcp`], 1,500 [`stripe--agent-toolkit`], ~1,000 [`datalayer--jupyter-mcp-server`], 701 [`ckreiling--mcp-server-docker`], 350 [`conikeec--mcpr`], 207 [`cyanheads--git-mcp-server`], 77 [`the-momentum--fhir-mcp-server`], 47 [`teaguesterling--duckdb_mcp`], ~25 [`datalayer--earthdata-mcp-server`], 25 [`tumf--grafana-loki-mcp`], 22 [`cyanheads--perplexity-mcp-server`], 15 [`spences10--mcp-turso-cloud`], 1 [`thenets--ghost-mcp`]. High-star community canonicals backlog-loaded — 171 issues + 91 PRs at 5k stars [`sooperset--mcp-atlassian`]. Conversely, completeness of structure does not track stars: [`thenets--ghost-mcp`] (1 star) has full Docker Compose dev stack, JWT renewal, dual-API split.

## Artifact category

The corpus is not uniform — beyond "an MCP server", several variants are worth distinguishing.

### Single-purpose MCP server

The default shape — one server fronting one domain. Examples: [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`baryhuang--mcp-server-aws-resources-python`], plus most other samples in bins 4 and 12.

### Server-framework (library, not server)

[`awslabs--mcp-lambda-handler`] is a library for *building* Lambda-hosted MCP servers, not itself an MCP server. Re-implements MCP wire format on Lambda events; user writes their own server using its `@mcp.tool()` decorator and `mcp.handle_request(event, context)` dispatch. Reveals a structural category the per-server schema does not anticipate.

[`conikeec--mcpr`] — a Rust library *for* building MCP servers (this repo *is* the SDK), not a server itself. Ships `mcpr generate-project` CLI to scaffold new implementations and reduce boilerplate; ships mock transport for offline testing. ServerConfig builder pattern (`.with_name()`, `.with_version()`, `.with_tool()`).

### Spec-driven server (tools materialize from external schema)

[`awslabs--openapi-mcp-server`] generates tools, resources, and prompts at server start by parsing one or more OpenAPI specs. No hand-authored tool definitions. Major design axis vs. code-driven servers — implications for docs drift (spec is source of truth), testing (every spec change is a contract change), and LLM behavior (tool descriptions inherit spec quality).

### Code-as-tool server (one tool wraps an interpreter)

[`baryhuang--mcp-server-aws-resources-python`] exposes a single `exec boto3` tool with AST-validation sandbox + import allowlist (boto3, operator, json, datetime, pytz, dateutil, re, time). Inverts the per-API enumeration default — one flexible code-execution tool versus N hand-enumerated tools.

### Multi-server monorepo (umbrella)

[`awslabs--mcp`] is a 40+ server monorepo with `src/<service>/` per server, namespace-prefixed PyPI packages (`awslabs.<service>-mcp-server`), and central dev tooling at root. A preview "aggregated" server (`aws-mcp-server`) bundles SOPs + CloudTrail audit, suggesting a future where per-service servers become composable primitives under a curated orchestrator.

[`cloudflare--mcp-server-cloudflare`] — Turbo monorepo with 14 domain Workers + shared `@repo/mcp-common` scaffolding.

[`stripe--agent-toolkit`] — multi-package monorepo: SDKs (Python + TS), AI-framework integrations (Vercel), billing primitives, and MCP — MCP treated as one integration channel among peers, not the whole product.

### MCP-as-database-extension

[`teaguesterling--duckdb_mcp`] — running MCP as a DuckDB C++ extension; PRAGMAs and SQL drive both server and client modes. Blurs database-vs-tool-registry boundary.

### Server-as-extension vs server-as-standalone

[`datalayer--jupyter-mcp-server`] — dual deployment: standalone MCP server OR Jupyter Server extension mounted inside Jupyter process. Deployment axis distinct from the artifact-category split above.

## Language and runtime

### Python

The dominant language across bins 3, 4, and 12: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`sooperset--mcp-atlassian`] (99.3%), [`the-momentum--fhir-mcp-server`] (97%), [`thenets--ghost-mcp`] (92.5%), [`tumf--grafana-loki-mcp`] (93.2%).

#### Python version floors

- `>=3.10` — [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`chroma-core--chroma-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`sooperset--mcp-atlassian`], [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`]
- `>=3.11` — [`blazickjp--arxiv-mcp-server`] (suggests use of newer typing / exception-group features)
- `>=3.12` — [`crystaldba--postgres-mcp`] (ruff target-version intentionally lags at `py39` as style target separate from runtime floor), [`the-momentum--fhir-mcp-server`] (leading-edge floor)
- Pinned via `.python-version` file, value not surfaced — [`ckreiling--mcp-server-docker`]
- Not surfaced — [`baryhuang--mcp-server-aws-resources-python`]

### TypeScript / JavaScript

- Node.js — [`cyanheads--git-mcp-server`] (Node >=20 + Bun >=1.2 dual runtime), [`cyanheads--perplexity-mcp-server`] (Node >=18), [`spences10--mcp-turso-cloud`] (92.4%), [`supabase-community--supabase-mcp`] (99.5%)
- Cloudflare Workers (V8 isolate runtime, not Node) — [`cloudflare--mcp-server-cloudflare`]

### Rust

[`conikeec--mcpr`].

### Clojure / JVM

[`bhauman--clojure-mcp`] runs on JDK 17+ (inferred), Clojure 99.9% of source. Distributed as a Clojure tools install (`clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp`).

### C++ (DuckDB extension)

[`teaguesterling--duckdb_mcp`] — C++ (73.7%) + Shell (13.1%) + Python (10.6%) + minor TS/JS/HTML; built as a C++ DuckDB extension with multi-language helpers.

### Multi-language repos

- TypeScript (51.9%) + Python co-primary in one monorepo, parallel PyPI + npm publishing — [`stripe--agent-toolkit`]
- See [`teaguesterling--duckdb_mcp`] above.

### Multi-runtime support

Dual-runtime auto-detection (Node + Bun) — [`cyanheads--git-mcp-server`] is the only sample running on more than one runtime; treats Node ≥20 and Bun ≥1.2 as first-class peers.

## SDK / framework

The Python ecosystem splits along "raw `mcp`", "FastMCP", or "custom (no SDK)"; TypeScript samples concentrate on `@modelcontextprotocol/sdk` plus auxiliary HTTP/validation libraries.

### Python — raw `mcp` SDK

- `mcp[cli]>=1.23.0` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- `mcp[cli]==1.6.0` (exact pin) — [`chroma-core--chroma-mcp`]
- `mcp[cli]>=1.25.0` — [`crystaldba--postgres-mcp`] ("deliberate use of low-level hooks for custom tool gating")
- `mcp[cli]>=1.2.1` — [`datalayer--earthdata-mcp-server`]
- `mcp[cli]>=1.10.1` — [`datalayer--jupyter-mcp-server`] (also pulls `mcp.server.fastmcp` via the extra)
- `mcp` (raw, version not surfaced) — [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`]
- Raw MCP Python SDK (FastMCP not surfaced) — [`ckreiling--mcp-server-docker`]

Notable: [`chroma-core--chroma-mcp`] pins exactly `==1.6.0`, an unusually tight pin for a 2025 vendor server.

### Python — FastMCP

- `fastmcp>=3.2.2,<4` — [`awslabs--openapi-mcp-server`]
- Dual `mcp>=1.23.0` AND `fastmcp>=3.0.1` — [`awslabs--mcp`] (sampled `aws-api-mcp-server/pyproject.toml`)
- Inferred via `FASTMCP_LOG_LEVEL` env-var convention — [`awslabs--mcp`]
- FastMCP 2.x — [`the-momentum--fhir-mcp-server`]
- FastMCP 2.12.3 (explicit precise pin) — [`thenets--ghost-mcp`]
- FastMCP, version not surfaced — [`tumf--grafana-loki-mcp`]
- `mcp>=1.8.0,<2.0.0` and `fastmcp>=2.13.0,<2.15.0` (likely historical: predates FastMCP, migrated partially) — [`sooperset--mcp-atlassian`]

### Python — custom (no MCP SDK)

[`awslabs--mcp-lambda-handler`] depends on neither `mcp` nor `fastmcp` — re-implements protocol wire format directly against Lambda events. Smallest dependency footprint of any awslabs sub-server (3 deps: python-dateutil, boto3, botocore).

### TypeScript SDK + supporting libraries

- `@modelcontextprotocol/sdk` versions: ^1.29.0 [`cyanheads--git-mcp-server`], ^1.15.0 [`cyanheads--perplexity-mcp-server`]
- Hono for HTTP layer — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- Zod validation — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- Pino structured logging + tsyringe DI + optional OpenTelemetry — [`cyanheads--git-mcp-server`]

### Cloudflare Workers stack

Workers-native (no Node SDK) with Turbo monorepo + internal `@repo/mcp-common` shared scaffolding — [`cloudflare--mcp-server-cloudflare`]; 14 domain Workers factor common server concerns into a shared package.

### Rust SDK

Custom MCP library (this repo *is* the SDK) — [`conikeec--mcpr`].

### Non-Python protocols

[`bhauman--clojure-mcp`] uses Anthropic's MCP plus nREPL for REPL-driven evaluation transport — JSON-RPC framing inside an nREPL connection.

## Transport

### stdio

Dominant: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`ckreiling--mcp-server-docker`], [`datalayer--earthdata-mcp-server`], [`spences10--mcp-turso-cloud`] (stdio inferred, never named in README), [`thenets--ghost-mcp`] (stdio implied by `uvx`).

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
- [`sooperset--mcp-atlassian`] — SSE primary; HTTP support mentioned. Likely env-var or subcommand driven.

### stdio + Streamable HTTP

- [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`datalayer--jupyter-mcp-server`].

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

### Transport-selection mechanism

- Default; no flag — [`ckreiling--mcp-server-docker`], [`datalayer--earthdata-mcp-server`]
- CLI flag — `--transport=sse` [`crystaldba--postgres-mcp`]; `mcpr generate-project --transport [stdio|sse]` selects at scaffold time [`conikeec--mcpr`]; `--transport` [`tumf--grafana-loki-mcp`]
- Environment-config selection (Zod-validated) — [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`]
- Env-var driven — [`the-momentum--fhir-mcp-server`] (`TRANSPORT_MODE`)
- URL path on the server side — [`cloudflare--mcp-server-cloudflare`]
- npm script — `npm run start:stdio` vs `npm run start:http` [`cyanheads--git-mcp-server`]
- CLI launcher flag / config — [`datalayer--jupyter-mcp-server`]
- SQL pragma — [`teaguesterling--duckdb_mcp`]

### HTTP host/port defaults

- 127.0.0.1:3010 [`cyanheads--perplexity-mcp-server`]
- configurable hostname, port 3015 [`cyanheads--git-mcp-server`]

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
- Also pip-installable via `pip install` — [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- pipx — [`crystaldba--postgres-mcp`]

### PyPI via pip (no uvx)

- [`awslabs--openapi-mcp-server`] uses `pip install` with extras (`[yaml]`, `[prometheus]`, `[all]`). Exception to the uvx convention; CLI args are heavy (`--api-name`, `--api-url`, `--spec-url`) so `pip install` + direct invocation makes sense.
- [`awslabs--mcp-lambda-handler`] uses `pip install -e .[dev]` (library, not invoked standalone).

### npm via npx

- [`cyanheads--git-mcp-server`] — `npx @cyanheads/git-mcp-server@latest`
- [`spences10--mcp-turso-cloud`] — `npx -y mcp-turso-cloud`
- [`stripe--agent-toolkit`] — `npx -y @stripe/mcp --api-key=...`

### Bun via bunx

- [`cyanheads--git-mcp-server`] — `bunx @cyanheads/git-mcp-server@latest`

### Source clone (no published package)

- [`cyanheads--perplexity-mcp-server`] — no npm package found, README walks through `git clone` → build → run.
- [`teaguesterling--duckdb_mcp`] — `make` build from source; not yet in DuckDB community extensions.
- [`the-momentum--fhir-mcp-server`] — clone-required; no PyPI publication; `make build` (Docker) or `make uv`.

### Cargo (Rust)

[`conikeec--mcpr`] — Cargo crate registry + `cargo install` for CLI.

### Both PyPI and npm (cross-ecosystem)

[`stripe--agent-toolkit`] — npm: `@stripe/agent-toolkit`, `@stripe/ai-sdk`, `@stripe/token-meter`, `@stripe/mcp`. PyPI: `stripe-agent-toolkit`. Parallel naming convention across ecosystems.

### Docker

Most samples ship Dockerfiles or pre-built images: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`] (multi-arch linux/amd64, arm64, arm/v7 — broader platform coverage than typical), [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`] (`crystaldba/postgres-mcp`), [`cyanheads--perplexity-mcp-server`] (multi-stage Node 18-Alpine), [`datalayer--earthdata-mcp-server`] (`datalayer/earthdata-mcp-server:latest`), [`datalayer--jupyter-mcp-server`] (`datalayer/jupyter-mcp-server:latest`), [`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`].

### Smithery

- [`baryhuang--mcp-server-aws-resources-python`] — `npx -y @smithery/cli install mcp-server-aws-resources-python --client claude`. Distribution vector alongside Docker and source.
- [`datalayer--earthdata-mcp-server`] — `smithery.yaml` flagged as a "first-class artifact".

### Windows .exe

[`awslabs--bedrock-kb-retrieval-mcp-server`] — `uv tool run --from awslabs.bedrock-kb-retrieval-mcp-server@latest awslabs.bedrock-kb-retrieval-mcp-server.exe`.

### JVM tools-installer

[`bhauman--clojure-mcp`] — `clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp`.

### Managed/hosted endpoint as distribution

- [`supabase-community--supabase-mcp`] — managed endpoint at `https://mcp.supabase.com/mcp`; cloud usage requires no install. Vendor-hosted MCP-as-a-service.
- [`stripe--agent-toolkit`] — `https://mcp.stripe.com` hosted endpoint with OAuth, in addition to local stdio.

### Remote-hosted (no local install)

[`cloudflare--mcp-server-cloudflare`] — Cloudflare Workers; server author operates the runtime, end users only consume URLs; users install via `mcp-remote` shim that bridges stdio (host side) to streamable-HTTP (Worker side).

### Optional install extras

- `[pdf]` — [`blazickjp--arxiv-mcp-server`]: separates core arXiv client from heavier PDF processing deps
- `[yaml]`, `[prometheus]`, `[all]` — [`awslabs--openapi-mcp-server`]
- `[sentence-transformers]` — [`chroma-core--chroma-mcp`]: locally-embedded collections without OpenAI/Cohere/Voyage keys

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

### Bare script

[`baryhuang--mcp-server-aws-resources-python`] — `src/mcp_server_aws_resources/server.py` or containerized equivalent.

### Library import (no standalone)

[`awslabs--mcp-lambda-handler`] — `def lambda_handler(event, context): return mcp.handle_request(event, context)`. Console script declared but primary usage is library import.

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

### CLI flags

- `--api-name`, `--api-url`, `--spec-url`, `--additional-specs`, `--include-tags`, `--exclude-tags` — [`awslabs--openapi-mcp-server`]
- `--storage-path` — [`blazickjp--arxiv-mcp-server`]
- Backend-mode flags (`--client-type ephemeral|persistent|http|cloud`) — [`chroma-core--chroma-mcp`]
- `--dotenv-path` for `.env` — [`chroma-core--chroma-mcp`]
- `--access-mode unrestricted/restricted`, `--transport` — [`crystaldba--postgres-mcp`]
- `--api-key=...` (entry; env-var equivalent not extracted) — [`stripe--agent-toolkit`]
- Both env vars and CLI flags (`GRAFANA_URL` / `GRAFANA_API_KEY` env or `-u` / `-k` flags) — [`tumf--grafana-loki-mcp`]

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

### None / public

- arXiv public API; rate limit enforced locally (3-second minimum) — [`blazickjp--arxiv-mcp-server`]
- No built-in authentication — [`bhauman--clojure-mcp`]
- N/A library — [`conikeec--mcpr`] ("transport-layer security implied for production SSE deployments")

### Read-only / restricted-access enforcement

In-process SQL parsing rejects writes (not DB-level permissions) — [`crystaldba--postgres-mcp`] uses `pglast` to reject COMMIT/ROLLBACK in restricted mode.

## Multi-tenancy

### Single-user per process

Common shape: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`], [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`], [`ckreiling--mcp-server-docker`] (one Docker daemon connection), [`datalayer--earthdata-mcp-server`] (bound to one NASA account), [`crystaldba--postgres-mcp`] (single DB connection per instance; SSE multiplexes clients but not tenants), [`sooperset--mcp-atlassian`] (one Atlassian site), [`spences10--mcp-turso-cloud`] (single org per deployment), [`stripe--agent-toolkit`] stdio mode (one API key → one Stripe account), [`thenets--ghost-mcp`] (one `GHOST_URL`), [`tumf--grafana-loki-mcp`] (one Grafana instance), [`the-momentum--fhir-mcp-server`] (not addressed; effectively single).

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

### Tool count bands

- 1 — [`baryhuang--mcp-server-aws-resources-python`]
- 2 — [`cyanheads--perplexity-mcp-server`]
- 3 — [`datalayer--earthdata-mcp-server`]
- 6 — [`blazickjp--arxiv-mcp-server`]
- 9 — [`crystaldba--postgres-mcp`]
- 12 — [`chroma-core--chroma-mcp`]
- 14+ — [`the-momentum--fhir-mcp-server`]
- 15+ — [`thenets--ghost-mcp`]
- 16+ — [`datalayer--jupyter-mcp-server`]
- 28 / 28+ — [`cyanheads--git-mcp-server`], [`ckreiling--mcp-server-docker`]
- 50+ — [`bhauman--clojure-mcp`]
- 72 — [`sooperset--mcp-atlassian`]
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

### Capability probing / feature gates

Reranking only exposed when region + IAM perms allow, rather than failing at tool-call time — [`awslabs--bedrock-kb-retrieval-mcp-server`].

### Tool-grouping mechanisms

#### Feature-group flag

[`supabase-community--supabase-mcp`] — `features` URL parameter enables/disables tool groups (Account, Documentation, Database, Debugging, Development, Edge Functions, Branching, Storage). Storage disabled by default; Branching is paid/experimental — explicit plan-tier gating surfaced through tool groups.

#### Read-only vs write-capable split

- [`supabase-community--supabase-mcp`] — `read_only` URL param.
- [`spences10--mcp-turso-cloud`] — `execute_read_only_query` (SELECT/PRAGMA) vs `execute_query` (DML/DDL) supports different MCP-client approval workflows.

#### Dual-API surface split

[`thenets--ghost-mcp`] — Content API (10 read-only tools) vs Admin API (6 read/write tools); env-var presence selects which surface is active.

#### No selector observed

[`sooperset--mcp-atlassian`] — 72-tool surface with no documented tool-group selector.

### Single-tool, multi-mode parameter

- Three download modes (manifest, download, script) on one tool — [`datalayer--earthdata-mcp-server`] called out as "clean separation of 'describe what you would do' from 'do it'"
- See also [`baryhuang--mcp-server-aws-resources-python`] (single `exec boto3` tool).

### Output format selection

- [`teaguesterling--duckdb_mcp`] — per-tool output format (JSON/Markdown/CSV) — explicit token-efficiency knob.
- [`tumf--grafana-loki-mcp`] — output format (text/JSON/markdown) as a tool parameter, rare among MCPs surveyed.

### Custom tool definition at runtime

[`teaguesterling--duckdb_mcp`] — `mcp_publish_tool` PRAGMA makes user-defined parameterized SQL templates first-class discoverable tools.

### Vector / semantic search exposed

- [`spences10--mcp-turso-cloud`] — vector similarity search as a first-class tool.
- [`the-momentum--fhir-mcp-server`] — embedded RAG pipeline with llama-index + huggingface + pinecone + sentence-transformers + pymupdf inside the MCP server.

### Domain terminology integration

[`the-momentum--fhir-mcp-server`] — LOINC terminology service integration; healthcare ontology bridge.

### Prompt-injection mitigation

[`supabase-community--supabase-mcp`] — SQL results wrapped with anti-injection instructions so LLMs resist following commands embedded in returned data.

## Tool-surface design

### Hand-enumerated per-API tools

Default shape across most samples: [`awslabs--bedrock-kb-retrieval-mcp-server`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`].

### Spec-generated tools

[`awslabs--openapi-mcp-server`] — tools materialize at server start from parsed OpenAPI spec. GET-with-query-params mapped to *tools* not *resources* — explicit deviation from MCP convention because LLMs use tools better than resources for parameterized search. Tag filtering via `--include-tags` / `--exclude-tags` reduces tool surface at mount time. Auto-enriched tool descriptions with response codes + parameter examples → claimed 70-75% token reduction vs naive rendering.

### Code-as-tool (single sandboxed interpreter)

[`baryhuang--mcp-server-aws-resources-python`] — single tool accepts a Python code string; AST validator + import allowlist (boto3, operator, json, datetime, pytz, dateutil, re, time) is the sandboxing mechanism.

### Decorator-driven (user-authored)

[`awslabs--mcp-lambda-handler`] — familiar FastMCP `@mcp.tool()` pattern but reimplemented on top of Lambda request/response shapes rather than `fastmcp`.

## Schema / type strategy

### Pydantic v2 (auto-derived)

- `pydantic>=2.11.1` — [`awslabs--bedrock-kb-retrieval-mcp-server`]
- Pydantic via MCP SDK (auto-derived from signatures) — [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`] (also FastAPI models for HTTP layer; schema auto-derived)
- Pydantic v2 with schemas derived from OpenAPI specs via `openapi-spec-validator` + `prance` — [`awslabs--openapi-mcp-server`] (the most extreme "schema is data" design in the corpus)
- Pydantic v2 + pydantic-settings — [`the-momentum--fhir-mcp-server`]

### Hand-authored / minimal

- Hand-authored single-tool schema (Python code string as input) — [`baryhuang--mcp-server-aws-resources-python`]
- Hand-authored JSON schemas (low-level MCP SDK) — [`crystaldba--postgres-mcp`]; project also pins pyright (`pyright==1.1.408` exact) for strict typing

### Stdlib / unspecified

- No Pydantic dependency listed — likely dataclasses or TypedDict — [`awslabs--mcp-lambda-handler`]

### Type-checker variants

- mypy — [`tumf--grafana-loki-mcp`], [`sooperset--mcp-atlassian`]
- ty (newer alternative to mypy) — [`the-momentum--fhir-mcp-server`]
- pyright (exact-pinned) — [`crystaldba--postgres-mcp`]

### Zod (TypeScript)

- [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`].

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

- [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--openapi-mcp-server`]

### Standard MCP stderr

- [`chroma-core--chroma-mcp`], [`blazickjp--arxiv-mcp-server`]

### `FASTMCP_LOG_LEVEL` env

- [`awslabs--mcp`]

### CloudWatch + X-Ray (Lambda implicit)

- [`awslabs--mcp-lambda-handler`]

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

### Not surfaced

- [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`] (not in budget), [`conikeec--mcpr`]
- Observability (logs/metrics/tracing/debug flags) not surfaced in nearly every sample of bin 12 — pattern across that bin, not one-off

## Host integrations

### One-click install buttons (URL protocol)

[`awslabs--mcp`] surfaces one-click install URLs for: Kiro, Cursor, VS Code, Cline with Amazon Bedrock, Windsurf, Claude Code. Shifts configuration burden from copy-paste JSON to deep links.

### Claude Desktop JSON

Most samples document a JSON `mcpServers` snippet: [`awslabs--bedrock-kb-retrieval-mcp-server`] (implicit in monorepo), [`baryhuang--mcp-server-aws-resources-python`] (Docker command + env injection or AWS profile mount), [`blazickjp--arxiv-mcp-server`] (uvx command), [`chroma-core--chroma-mcp`], [`bhauman--clojure-mcp`] (`claude_desktop_config.json` with shell path), [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`], [`cloudflare--mcp-server-cloudflare`] (implied), [`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`teaguesterling--duckdb_mcp`] (via `.mcp.json`), [`the-momentum--fhir-mcp-server`] (via `claude_desktop_config.json`), [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`], [`supabase-community--supabase-mcp`].

### Cursor

[`crystaldba--postgres-mcp`], [`cloudflare--mcp-server-cloudflare`], [`sooperset--mcp-atlassian`], [`stripe--agent-toolkit`] (with shipped `.cursor-plugin/`), [`supabase-community--supabase-mcp`].

### Windsurf

[`crystaldba--postgres-mcp`], [`supabase-community--supabase-mcp`].

### Goose

[`crystaldba--postgres-mcp`].

### Qodo Gen

[`crystaldba--postgres-mcp`].

### Cline (with config files like `cline_mcp_settings.json`)

[`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`spences10--mcp-turso-cloud`].

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

- [`supabase-community--supabase-mcp`] — native MCP client integration via `createToolSchemas()` SDK export. First-class non-Claude integration via shipped tool-schema generator.
- [`stripe--agent-toolkit`] — `@stripe/ai-sdk` package for Vercel integration.

### Codex plugin

[`blazickjp--arxiv-mcp-server`] — `.codex-plugin/` integration manifest in repo root; first-class Codex plugin shape.

### Claude Code skills (in-repo)

[`blazickjp--arxiv-mcp-server`] — `skills/` directory; explicit Claude Code skill wrapper co-located with the MCP server. Ships integration artifacts for three different host ecosystems in one repo: standard MCP (`src/`), Codex (`.codex-plugin/`), Claude Code skills (`skills/`).

### Claude Code plugin wrapper

- [`stripe--agent-toolkit`] — `.claude-plugin/` directory at repo root.
- None observed across all 8 samples in bin 4 — [`ckreiling--mcp-server-docker`], [`cloudflare--mcp-server-cloudflare`], [`conikeec--mcpr`], [`crystaldba--postgres-mcp`], [`cyanheads--git-mcp-server`], [`cyanheads--perplexity-mcp-server`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`].
- Neither plugin format shipped — [`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`supabase-community--supabase-mcp`], [`teaguesterling--duckdb_mcp`], [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`], [`tumf--grafana-loki-mcp`].

### Smithery

- [`baryhuang--mcp-server-aws-resources-python`] — registry entry, install via `@smithery/cli`.
- [`datalayer--earthdata-mcp-server`] — `smithery.yaml` first-class artifact.

### Multi-REPL (Clojure ecosystem)

[`bhauman--clojure-mcp`] — Shadow-cljs (ClojureScript), Babashka, Basilisp, Scittle environment detection and switching. Multi-REPL support is a Clojure-ecosystem-specific axis.

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

### Make-driven

[`thenets--ghost-mcp`] — `make test` and `make test-connection`. [`teaguesterling--duckdb_mcp`] — `make test`.

### TS test runners

- Bun test runner with Vitest compatibility, coverage reports — [`cyanheads--git-mcp-server`]
- Vitest across the monorepo — [`cloudflare--mcp-server-cloudflare`]
- TypeScript noEmit type check via `npm test` (type-check as test) — [`cyanheads--perplexity-mcp-server`]

### Mock transport implementations

[`conikeec--mcpr`] — across stdio and SSE.

### Custom marker

- `live` for API-calling tests — [`awslabs--mcp`].
- `integration`, `dc_e2e` (Data Center e2e), `cloud_e2e` (Cloud e2e) — [`sooperset--mcp-atlassian`]. Encodes the on-prem/cloud deployment matrix into the test suite, not just CI config.

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

### Per-server in monorepo

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--openapi-mcp-server`] inherit from the parent monorepo's CI.

### Auxiliary automation

[`spences10--mcp-turso-cloud`] — `.changeset/` (changelog management) + `renovate.json` (dependency automation); explicit Actions workflows not confirmed.

## Container / packaging artifacts

### Dockerfile

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp`] (per server), [`baryhuang--mcp-server-aws-resources-python`] (multi-arch linux/amd64, arm64, arm/v7), [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`ckreiling--mcp-server-docker`], [`crystaldba--postgres-mcp`], [`cyanheads--perplexity-mcp-server`] (multi-stage Node 18-Alpine), [`cyanheads--git-mcp-server`] (implied by Bun build), [`datalayer--earthdata-mcp-server`] (also pre-built image on Docker Hub), [`datalayer--jupyter-mcp-server`], [`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`].

### Docker Compose

- [`the-momentum--fhir-mcp-server`] — for server deployment.
- [`thenets--ghost-mcp`] — Docker Compose for full Ghost + MySQL test stack (target backend, not the MCP server itself); end-to-end dev-stack bundling, more typical of integration-test frameworks.

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

[`spences10--mcp-turso-cloud`], [`teaguesterling--duckdb_mcp`], [`supabase-community--supabase-mcp`] (managed cloud reduces need), [`tumf--grafana-loki-mcp`] (explicitly absent).

### Not documented

[`conikeec--mcpr`], [`stripe--agent-toolkit`].

### Registry registration

`smithery.yaml` for Smithery registry — [`datalayer--earthdata-mcp-server`] (first-class repo artifact).

## Repo layout

### Single package (Python)

- `src/<package_name>/` — [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`], [`chroma-core--chroma-mcp`], [`crystaldba--postgres-mcp`] (src-layout with `pythonpath = ["./src"]`), [`ckreiling--mcp-server-docker`] (`src/mcp_server_docker/`), [`thenets--ghost-mcp`] (`src/ghost_mcp/`)
- Without explicit src-layout — [`datalayer--earthdata-mcp-server`] (`earthdata_mcp_server/` + `dev/` + `docs/`), [`datalayer--jupyter-mcp-server`] (`jupyter_mcp_server/` + `jupyter-config/` + `docs/`), [`the-momentum--fhir-mcp-server`] (`app/` module)
- [`sooperset--mcp-atlassian`], [`spences10--mcp-turso-cloud`], [`teaguesterling--duckdb_mcp`], [`tumf--grafana-loki-mcp`]

### Single package (TS Node)

- [`cyanheads--perplexity-mcp-server`] (`.github/`, `src/`, `docs/`)
- [`cyanheads--git-mcp-server`] (organized by concern: tools/, resources/, transports/, services/, storage/, config/, utils/, container/; tests mirror structure)

### Single Clojure package

[`bhauman--clojure-mcp`] — `src/`, `test/`, `doc/`, `resources/`, `deps.edn`, `docs/`.

### Single Rust library + `/examples/`

[`conikeec--mcpr`].

### Sub-package in monorepo

[`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--openapi-mcp-server`] all live under `awslabs/mcp/src/<service>/`.

### Monorepo-of-packages

- [`awslabs--mcp`] — 40+ servers, central dev tooling at root with per-server pyproject.toml. Classic uv workspace layout (though `[tool.uv.workspace]` not confirmed).
- [`cloudflare--mcp-server-cloudflare`] — Turbo/pnpm monorepo with 14 domain Workers + shared `@repo/mcp-common`.
- [`stripe--agent-toolkit`] — multiple SDK packages (Python + TS) coexist with MCP, Vercel-AI integration, and billing components. `.claude-plugin/` and `.cursor-plugin/` ship alongside code.
- [`supabase-community--supabase-mcp`] — `/packages` (core packages), `/docs`, `/supabase`, pnpm-managed (`pnpm-workspace.yaml`).

### Multi-host artifact bundle

[`blazickjp--arxiv-mcp-server`] — single repo bundles standard MCP (`src/`), Codex (`.codex-plugin/`), Claude Code skills (`skills/`).

### Docs sets

- README + MCP.md + CHANGELOG + CONTRIBUTING — [`conikeec--mcpr`]
- README + `docs/` — [`cyanheads--perplexity-mcp-server`], [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]

## Build backend / packaging

### hatchling

- [`awslabs--bedrock-kb-retrieval-mcp-server`], [`awslabs--mcp-lambda-handler`], [`awslabs--mcp`], [`awslabs--openapi-mcp-server`], [`chroma-core--chroma-mcp`], [`crystaldba--postgres-mcp`] (`hatchling.build`), [`datalayer--earthdata-mcp-server`] (~1.21), [`datalayer--jupyter-mcp-server`] (~1.21), [`sooperset--mcp-atlassian`]

### `uv_build` with non-standard module name

[`the-momentum--fhir-mcp-server`] — module-name `app`. Adoption of `uv`'s native build-backend integration; less common than hatchling.

### Mixed pyproject.toml + setup.py

[`tumf--grafana-loki-mcp`].

### Backend present, not surfaced

- [`ckreiling--mcp-server-docker`], [`thenets--ghost-mcp`]
- [`baryhuang--mcp-server-aws-resources-python`], [`blazickjp--arxiv-mcp-server`]

### `uv.lock` committed

- [`blazickjp--arxiv-mcp-server`] — present
- uv.lock + uv-managed (`uv sync`) — [`crystaldba--postgres-mcp`]
- Devbox + uv combo — [`ckreiling--mcp-server-docker`]
- `uv` convention — [`sooperset--mcp-atlassian`], [`the-momentum--fhir-mcp-server`], [`thenets--ghost-mcp`]
- `uv` + pip compatible — [`tumf--grafana-loki-mcp`]
- Standard PyPI publication via hatchling, lock not confirmed — [`datalayer--earthdata-mcp-server`], [`datalayer--jupyter-mcp-server`]
- Not confirmed — [`awslabs--mcp`], [`chroma-core--chroma-mcp`], others

### Version manager convention

- `uv` — most Python samples
- pip — [`awslabs--mcp-lambda-handler`] (uv not emphasized)

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

[`sooperset--mcp-atlassian`] — `llms.txt` file present; design-for-AI-consumption documentation pattern.

### Documentation-heavy repo

[`bhauman--clojure-mcp`] — README.md (30KB), PROJECT_SUMMARY.md (26KB), CONFIG.md (9KB), FAQ.md (8KB), CHANGELOG, BIG_IDEAS, LLM_CODE_STYLE; substantial for a single-package repo.

### Optional-deps taxonomy

Clean PEP 621 grouping into `test` / `lint` / `typing` extras — [`datalayer--earthdata-mcp-server`] (also `mdformat` + `mdformat-gfm` in lint extras for markdown-as-CI), [`datalayer--jupyter-mcp-server`] (`lint`, `typing`, `mcp[cli]` extras).

## Notable structural choices

### Capability probing at startup

[`awslabs--bedrock-kb-retrieval-mcp-server`] — reranking tool only registered when region + IAM perms allow; capability gate at start, rather than failing at tool-call time.

### Lean dependency footprint

- [`awslabs--bedrock-kb-retrieval-mcp-server`] — 4 runtime deps (boto3, loguru, mcp, pydantic); no httpx (boto3 owns network I/O)
- [`awslabs--mcp-lambda-handler`] — 3 deps (python-dateutil, boto3, botocore); pure-stdlib protocol handling, no Pydantic, no mcp-sdk, no fastmcp

### Heavy / "fat" install

[`chroma-core--chroma-mcp`] — bundles three cloud embedding SDKs (openai, cohere, voyageai) in core deps (not extras); fat install, zero-friction provider switching.

### Auto-release sentinel version

[`awslabs--openapi-mcp-server`] — pyproject.toml version was `0.9223372036854775807.9223372036854775807` (int64 max); looks like an automated-release sentinel, not a human-chosen version.

### Tag-driven resource access control

[`awslabs--bedrock-kb-retrieval-mcp-server`] — AWS tags become the access-control boundary for which KBs the server can see; novel solution to "too many resources in the account" without building app-level access control.

### One binary, many runtime modes

[`chroma-core--chroma-mcp`] — single binary supports 4 backing-store modes (ephemeral, persistent, HTTP self-hosted, Chroma Cloud) selected at launch via flags rather than four separate entry points.

### Multi-spec API gateway pattern

[`awslabs--openapi-mcp-server`] — single server fronts many APIs via `--additional-specs`, each with independent auth and HTTP clients; "one gateway to many SaaS APIs".

### Server-framework distinction

[`awslabs--mcp-lambda-handler`] — sub-package in an MCP-server monorepo that is itself not a server but a library for building servers; reveals a structural category the per-server schema does not anticipate. Session management as a pluggable extension point (NoOp/DynamoDB/custom). Infrastructure-dependent auth (API Gateway Authorizer) — auth is architecturally outside the server.

### REPL-driven paradigm

[`bhauman--clojure-mcp`] — REPL-driven development as primary paradigm (nREPL); 50+ tools targeting Clojure ecosystem needs. Configuration via Clojure maps (deps-like pattern). LLM_CODE_STYLE.md for AI assistant prompt guidance — unusual.

### Built-in client-side rate limit

[`blazickjp--arxiv-mcp-server`] — 3-second minimum rate-limit enforcement at the client layer; reflects arXiv's rate-limit guidance.

### Multi-arch Docker

[`baryhuang--mcp-server-aws-resources-python`] — linux/amd64, arm64, arm/v7; broader platform coverage than typical.

### Hosting responsibility as a design axis

- Server author operates the runtime, end users only consume URLs — [`cloudflare--mcp-server-cloudflare`] flags "hosting responsibility" with downstream effects on release, auth, and observability concerns. Opposite end of the spectrum from local stdio servers like [`ckreiling--mcp-server-docker`] / [`datalayer--earthdata-mcp-server`].
- Stdio emulation via shim on the client side rather than on the server — `mcp-remote` translates stdio↔HTTP so hosts still speak stdio while server speaks HTTP — [`cloudflare--mcp-server-cloudflare`].
- Paid-plan gating: some Cloudflare features require Workers paid plan; "operational cost surfaces as a server capability axis" — [`cloudflare--mcp-server-cloudflare`].

### Hosted-endpoint + local stdio duality

[`stripe--agent-toolkit`], [`supabase-community--supabase-mcp`]. Sentry / Cloudflare also follow this pattern (referenced in samples).

### Server-as-extension vs server-as-standalone

Dual deployment: standalone MCP server OR Jupyter Server extension mounted inside Jupyter process — [`datalayer--jupyter-mcp-server`] called out "deployment axis".

### Runtime auto-detection

Runtime auto-detection between Node and Bun — [`cyanheads--git-mcp-server`] flagged "axis: multi-runtime support".

### Tenant sandboxing in stdio

Multi-tenant sandboxing via base-directory restriction in a stdio server — [`cyanheads--git-mcp-server`] flagged "axis: workspace isolation in a stdio server"; pairs with session-based working-directory isolation.

### Domain knowledge embedded in server

- Deterministic optimization algorithms (greedy search adapted from Microsoft Anytime), workload compression, hypothetical indexing via `hypopg`, Pareto-front cost-benefit balancing — [`crystaldba--postgres-mcp`] flagged "embedded performance-tuning intelligence goes far beyond typical SQL-execution MCP servers". Optional OpenAI integration for experimental LLM-based index tuning.
- Auto-complexity detection to switch between fast search and deep research tools — [`cyanheads--perplexity-mcp-server`].
- Two-phase version negotiation in server initialization handshake — [`conikeec--mcpr`].

### Sibling-package factoring

Tool definitions factored into a separate PyPI project (`jupyter-mcp-tools>=0.1.6`) — [`datalayer--jupyter-mcp-server`] flagged "unusual reuse pattern in MCP land".

### Shared monorepo scaffolding

Internal `@repo/mcp-common` workspace package abstracts shared server scaffolding across 14 domain Workers — [`cloudflare--mcp-server-cloudflare`] mirrors Cloudflare's own platform composition patterns.

### Auth split by protocol layer

Dedicated MCP-level token (`MCP_TOKEN`) introduced separate from upstream Jupyter token (`JUPYTER_TOKEN`) in v1.0.0 — [`datalayer--jupyter-mcp-server`].

### Three-mode tool design

A single tool exposing manifest/download/script modes via parameter — [`datalayer--earthdata-mcp-server`] separating planning from execution.

### Library vs server (distinct from server-framework)

A Rust library *for* building MCP servers (this repo *is* the SDK), not a server itself — [`conikeec--mcpr`]; ships `mcpr generate-project` CLI to scaffold new implementations and reduce boilerplate; ships mock transport for offline testing.

### Vendor/community canonical positioning

Community-canonical at vendor scale — [`sooperset--mcp-atlassian`] (5k stars on a non-vendor repo for Atlassian indicates the vendor has not shipped first-party). Same shape: [`spences10--mcp-turso-cloud`].

### Multi-surface agent tooling

[`stripe--agent-toolkit`] — one repo houses SDKs (Python + TS), AI-framework integrations (Vercel), billing primitives, and MCP — MCP treated as one integration channel among peers, not the whole product.

### Per-host plugin wrappers shipped in-repo

[`stripe--agent-toolkit`] — `.claude-plugin/` and `.cursor-plugin/` recognize host-specific plugin formats as a first-class distribution surface.

### Server-blurring architectures

#### MCP-as-SQL-extension

[`teaguesterling--duckdb_mcp`] — MCP surface reachable via SQL PRAGMAs; blurs database and tool-registry roles.

#### Dual server + client mode

[`teaguesterling--duckdb_mcp`] — server for AI assistants AND client connecting to other MCP resources via SQL `ATTACH`. Single artifact plays both protocol roles.

#### In-server RAG pipeline

[`the-momentum--fhir-mcp-server`] — embedding + vector-store + document-parsing stack inside the MCP process. Most servers expose tools that call upstream RAG; this one hosts the RAG itself.

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

## Unanticipated axes / observations

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

[`baryhuang--mcp-server-aws-resources-python`] — one flexible code-execution tool with AST sandbox versus N hand-enumerated per-API tools.

### Capability-probing at start

[`awslabs--bedrock-kb-retrieval-mcp-server`] — features only registered when env supports them, rather than failing at tool-call time.

### REPL-as-transport (nREPL)

[`bhauman--clojure-mcp`] — unusual for MCP; the JSON-RPC framing flows through an existing REPL connection.

### Agent-augmented tools (server's tools call out to LLMs)

[`bhauman--clojure-mcp`] — agent tools with optional external LLM integration (Anthropic, OpenAI, Google Gemini); the server's tools are themselves LLM-orchestrated.

### Provider-prefixed env var convention

[`chroma-core--chroma-mcp`] — `CHROMA_<PROVIDER>_API_KEY` gives a uniform auth surface across multiple embedding back-ends.

### Tag-based resource scoping

[`awslabs--bedrock-kb-retrieval-mcp-server`] — AWS tags as MCP access-control boundary; alternative to app-level access control.

### Server-framework category

[`awslabs--mcp-lambda-handler`], [`conikeec--mcpr`] — "server" vs "server-framework" distinction not anticipated by the per-sample schema.

### Serverless deployment as first-class target

[`awslabs--mcp-lambda-handler`] — cold-start sensitivity, statelessness, external session stores all become design concerns.

### LLM_CODE_STYLE.md for prompt optimization

[`bhauman--clojure-mcp`] — explicit AI-assistant guidance file; unusual.

### Hosting model

Hosting responsibility (operator-runs vs user-runs) — [`cloudflare--mcp-server-cloudflare`].

### Stdio-on-client emulation

Stdio bridge on the host side via `mcp-remote` so the server can speak HTTP — [`cloudflare--mcp-server-cloudflare`].

### Context-length mitigation

README guidance flagging chained-tool calls against high-cardinality data as a context-window concern the client must manage — [`cloudflare--mcp-server-cloudflare`].

### Capability declaration

Advertising prompts as a first-class capability alongside tools — [`ckreiling--mcp-server-docker`].

### Workspace isolation in stdio

Multi-tenant sandboxing via base-directory restriction — [`cyanheads--git-mcp-server`].

### Multi-runtime auto-detection

Auto-detection between Node and Bun — [`cyanheads--git-mcp-server`].

### Auth layering

MCP-level token distinct from upstream-service token — [`datalayer--jupyter-mcp-server`].

### Sibling-package tool factoring

Tools published as a separate PyPI project — [`datalayer--jupyter-mcp-server`].

### Multi-mode single tool

Manifest / download / script modes on one tool — [`datalayer--earthdata-mcp-server`].

### Reproducible-env tooling spread

- Devbox — [`ckreiling--mcp-server-docker`]
- devenv — [`crystaldba--postgres-mcp`]
- mise — [`supabase-community--supabase-mcp`]

### Server-managed credential lifecycle

JWT auto-renewal inside the MCP server — [`thenets--ghost-mcp`]. Encrypted credential vault — [`the-momentum--fhir-mcp-server`]. Short-lived child-token generation — [`spences10--mcp-turso-cloud`]. Most MCP servers assume static creds; these don't.

### Output-format-as-tool-parameter

[`teaguesterling--duckdb_mcp`], [`tumf--grafana-loki-mcp`] — token-efficiency / UX dimension most MCP servers skip.

### Domain-ontology bridges

[`the-momentum--fhir-mcp-server`] (LOINC) — pattern likely to recur in legal (Westlaw), education (curriculum standards), finance (ticker/ISIN) per the sample's own observation.

### Tool-registry-as-database-extension

[`teaguesterling--duckdb_mcp`] — running MCP as a DuckDB extension, exposing PRAGMAs and SQL, blurs the database-vs-tool-registry boundary.

### URL-parameter configuration

[`supabase-community--supabase-mcp`] — config via URL query params (project_ref, read_only, features) is unusual for MCP and fits HTTP transport naturally.

### Schema export as composable SDK

[`supabase-community--supabase-mcp`] — `createToolSchemas()` doubles the repo as an SDK; consumers can use Supabase tool definitions without routing through MCP.

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
- Tool-scoping for large surfaces (e.g. 72-tool [`sooperset--mcp-atlassian`]) often unspecified — how users reduce a large surface to a working subset is rarely documented. Contrast with [`supabase-community--supabase-mcp`]'s explicit `features` param
- Transport names not always in README — [`spences10--mcp-turso-cloud`], [`thenets--ghost-mcp`] omit explicit transport documentation; stdio is inferred from invocation pattern
- Observability (logs/metrics/tracing/debug flags) not surfaced in nearly every sample of bin 12
- Last-commit dates inconsistently captured
- Container artifact presence/absence consistently noted but content (multi-stage builds, base image choices) is not
