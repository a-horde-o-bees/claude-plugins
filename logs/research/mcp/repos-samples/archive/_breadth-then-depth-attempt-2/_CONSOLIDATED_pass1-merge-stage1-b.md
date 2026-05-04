# Sample

Merge of 4 partials (bins 6-9) into `_CONSOLIDATED_pass1-merge-stage1-b.md`. Functional roles with implementation paths and qualitative descriptions; no inline citations (see `references` verb for provenance).

## Server runtime

The language and SDK substrate the MCP server process executes on. Constrains packaging conventions, dependency-management style, async model, type-derivation strategy, and the available transport and distribution channels downstream.

### Python with FastMCP

Decorator-driven Python framework wrapping the official MCP Python SDK. `@mcp.tool` / `@mcp.resource` / `@mcp.prompt` declare capabilities; the framework auto-derives JSON Schema from type hints with Pydantic and dispatches both `def` and `async def` handlers. The framework ships its own HTTP transport stack (uvicorn, starlette, websockets, authlib, python-multipart) so consumers do not assemble it. Pin discipline varies sharply: narrow-range pins (`>=2.7.0,<2.11`) explicitly guard against minor-release breakage; exact pins (`fastmcp == 2.13.1`) prioritize reproducibility; loose pins (`>=1.0.0`) appear in minimal-ceremony servers. Appropriate when tool count is moderate-to-large, type-annotated handlers carry the schema burden, and authors want low-ceremony decorator declarations.

### Python with FastMCP (pre-2.x era)

Single-file Python script using FastMCP 1.x decorators. Tool signatures derive from type hints; the FastMCP CLI installer (`fastmcp install`) is the install mechanism rather than pip. Predates the modern `pyproject.toml`-centric layout — `requirements.txt` pins FastMCP and the script is the package. Appropriate when the goal is the smallest possible single-file MCP server and the author is comfortable being pinned to FastMCP's CLI conventions.

### Python with raw MCP SDK

Direct use of the lower-level `mcp` Python SDK without FastMCP. Hand-authored JSON Schemas, manual server lifecycle management, often paired with `hatchling` build backend, `uv` packaging, `pyright` typing, `ruff` lint, and `pytest` (+ `pytest-asyncio` for HTTP-touching servers). Module-level entry (`python -m package.server`) is common rather than a console script; `uv sync` installs from source. Appropriate for minimal single-tool servers where decorator overhead is unnecessary, when the project predates FastMCP, when fine control over protocol surface is required, or when project governance prefers minimal dependency stacks. The canonical "pre-FastMCP" authoring style chosen by the official Python reference servers.

### Python with both MCP SDK and FastMCP declared

Hybrid path where `pyproject.toml` lists both `mcp` (or `mcp[cli]`) and `fastmcp` as dependencies. Typically FastMCP runs the server surface while `mcp[cli]` provides developer tooling (Inspector launcher, schema dump utilities), or transitional state during a migration. Appropriate when devs want both the auto-schema ergonomics of FastMCP and the official CLI tooling. Carries dual-import risk and larger dependency footprint.

### Python with Anthropic Claude Agent SDK

Python runtime that pairs the Claude Agent SDK with MCP — a less common path where the agent SDK is the foundation and MCP capabilities are layered on top. Appropriate when the project blurs agent and MCP-server roles or wants to reuse Claude Agent abstractions. Pulls in a heavier dependency surface than plain MCP.

### TypeScript on Node with official MCP SDK

Node-hosted TypeScript using the official `@modelcontextprotocol/sdk` consumed via npm; CommonJS bin entry registered in `package.json`. Authors compose Express or stdlib HTTP around the SDK when an HTTP transport is needed. Common alongside Zod for tool argument validation and openapi-client-axios when the tool surface is auto-derived from an OpenAPI spec rather than hand-authored. Single-file servers with minimal dependencies (e.g., SDK + a domain library like `sqlite3`) ship as npx-runnable npm packages. Imposes a Node version floor (typically 18+ or 20+). Appropriate for thin database/local-resource adapters, when the JS ecosystem already has the canonical client library, when hosts run a Node process directly via `npx`, and when front-end tooling (esbuild, tsx, Vitest) is already familiar.

### TypeScript on Node with monorepo tooling

A TypeScript codebase organized as a pnpm workspace + Turbo monorepo. Same code targets both an npm-distributable stdio binary (`npx @scope/server`) and a hosted HTTP service. Permits multiple packages (server, client, evals, plugin wrapper) under one repo. Appropriate when one logical product spans server + clients + first-party plugin wrappers and the author wants shared build/CI across them.

### TypeScript on Cloudflare Workers

A TypeScript codebase deployed as a Cloudflare Workers application via Wrangler, with React Router 7 + Vite for a co-resident web frontend. The server is the deployment, not the artifact — there is no binary or package users run. Constrains the runtime to whatever the Workers platform supports (HTTP/SSE only, no stdio, ephemeral execution model). Appropriate when the goal is a zero-install hosted MCP service with global edge distribution and the workload fits Workers' execution constraints.

### Next.js (TypeScript) as MCP host

A Next.js App Router application that embeds the MCP server alongside a marketing landing page, OAuth UI, and HTTP API endpoints. Tool/handler logic lives in a `mcp-src/` module called from API routes. Appropriate when the deployment is a remote hosted service rather than a local stdio process — Next.js provides routing, deployment integration (Vercel), and a unified surface for OAuth flows + the MCP endpoint + a public landing page. Constrains transport to HTTP-based variants and assumes a hosted-service model.

### Go with mark3labs/mcp-go SDK

A Go binary linked against the community `mcp-go` SDK. Native Go structs become tool arguments with automatic JSON-Schema generation; transport selection is a separate entry method (`server.ServeStdio`, `server.ServeSSE`, `server.ServeHTTP`) or registration into a higher-level web framework (Gin). Single-binary build artifact suits cross-platform release-and-download distribution and Docker packaging without language-runtime prerequisites on the host. Stdio is the natural transport for `serve`-style subcommands; Go modules act as the dependency boundary. Appropriate when single-binary deployment, performance, type-safe schemas without runtime reflection cost, and goroutine-based concurrency for streaming or task-augmented tools matter.

### Go with metoro-io/mcp-golang or alternative SDK

A Go program that imports an alternative third-party MCP SDK module (e.g., `github.com/metoro-io/mcp-golang`) and registers tools/resources/prompts via constructor and method calls. Same single-binary distribution profile and concurrency model as the mark3labs path; the SDK choice differs. Appropriate when the consumer prefers the alternative SDK's API ergonomics or transport mix.

### Go with custom MCP implementation

A Go server that hand-rolls protocol handling without depending on a third-party MCP SDK and ships a `server.json` to declare MCP capability metadata. Yields a single static binary suitable for direct distribution or Docker base-image minimization, supports stdio/SSE/HTTP from one build, and provides explicit control over TLS, custom User-Agent, and other enterprise-environment portability concerns. Appropriate at scale (large official servers) where custom toolset gating, dynamic capability registration, or hosted-mode integration motivate owning the protocol layer rather than tracking an upstream SDK.

### Clojure with hand-rolled MCP and minimal deps

A Clojure project against MCP version 2024-11-05 with `org.clojure/data.json` as effectively the only dependency. Polylith-style modular layout (bases, components, projects). Java runtime is required; the JVM warm-up and dependency resolution cost falls on the host launching `clj -M:profile`. Appropriate when the author values a self-contained Clojure REPL evaluation surface and is willing to absorb Polylith's structural overhead in exchange for component reuse across multiple deliverables.

### Kotlin Multiplatform SDK

Kotlin SDK published as Maven artifacts (`io.modelcontextprotocol:kotlin-sdk*`) with multiplatform targets (JVM, Native, JS, Wasm). Coroutine-based APIs throughout; Ktor server is an optional companion for HTTP transports, with engines specified independently to avoid transitive bloat. Appropriate when the consumer needs JVM integration, Android, or browser/Wasm reach with a single SDK surface.

## Transport

The wire on which MCP messages travel between host and server. Constrains tenancy, authentication, distribution, and lifecycle (long-lived process vs request/response).

### stdio

Bidirectional JSON-RPC over the server process's stdin/stdout, with stderr reserved for logging. The host launches the server as a child process per connection. Implies single-tenant (one process == one identity), single-host (the launching app), and pushes auth into env vars or CLI flags read at startup. Default for locally-installed servers across all runtimes. Often selected implicitly by the SDK's CLI installer, sometimes explicitly via a `stdio` subcommand or profile alias. Tightens stdout-cleanliness pressure — any non-protocol writes corrupt the channel, so servers suppress progress output and route logs to stderr. Entry-command snippets in `claude_desktop_config.json` and analogous host-config files are the canonical install surface.

### Streamable HTTP

A single HTTP endpoint (commonly `/mcp` or `/mcp` on port 5000, 9010, 9887, 13080 etc.) handling streaming JSON-RPC, optionally upgrading to SSE for streaming. Selected via env var (`<NAME>_TRANSPORT=http`), CLI flag (`--transport http`, `--port <n>`), or by binding to an HTTP entry method on the SDK. Permits multi-user access, OAuth-style auth, and decoupling the server lifecycle from the host process. Required for hosted SaaS services, browser-reachable clients (which then triggers explicit CORS configuration), and OAuth flows where redirect targets need a reachable endpoint. Often paired with stdio for the same product — same code targets both modes, with the deployment target choosing.

### SSE (Server-Sent Events)

HTTP transport using SSE for server-to-client streaming, paired with a separate POST endpoint for client-to-server messages. A common variant of HTTP transport for hosted MCP services and locally-launched HTTP servers. Often a distinct entry method on the SDK and sometimes the streaming flavor of Streamable HTTP. May exist as a legacy compatibility endpoint (`/sse`) preserved alongside a newer streamable-HTTP endpoint to avoid breaking older clients. Selected via a CLI profile (e.g., `:sse-server`) or shared env var/flag with HTTP. Appropriate when the server emits change notifications (resources/tools/prompts updates) that clients subscribe to, or when host integrations have not yet migrated to streamable HTTP.

### HTTP with JSON response mode

HTTP variant where the server returns a single JSON response per request rather than a stream. Coexists with SSE in some servers as alternative HTTP modes. Appropriate for clients that don't need streaming or for simple request/response tool calls.

### WebSocket

Bidirectional persistent connection. Surfaces in Kotlin/Ktor where the SDK exposes a `WebSocketTransport` alongside stdio, SSE, and Streamable HTTP. Appropriate when both sides need symmetric streaming and the host environment already speaks WebSocket (browser clients, in particular).

### In-memory / in-process channel

A non-network transport used inside a single process for testing — server and client share a Kotlin channel, a Go pipe, or an in-process adapter rather than serialize JSON over IPC. Not a deployment option; only relevant in test harnesses and library-mode embedding where the server is part of the host process. Appropriate when the test goal is the server's protocol behavior independent of network/IO concerns.

### Custom or experimental transports

SDKs that expose a transport interface so consumers can plug in their own (e.g., Go SDKs documenting custom transport support and "HTTPS with custom auth, experimental"). Appropriate when the deployment target needs a wire format the SDK doesn't ship.

### REST API bridge

Custom HTTP REST surface (separate from canonical MCP transports) exposed via an additional bridge file (e.g., `vscode_bridge.py`) on a configurable port. Non-MCP clients consume the same tool surface through a hand-rolled REST API. Appropriate when the author needs to support clients that don't speak MCP at all, or when an IDE plugin prefers REST.

### CLI dispatcher to per-server stdio

Top-level CLI binary takes a server name as a subcommand (`uvx mcp-science <server-name>`) and exec's the named child server, which then speaks stdio MCP. Appropriate for monorepos that ship many independent servers under a single PyPI package — the dispatcher unifies install/discovery while each child server retains canonical stdio semantics.

### SFTP / SSH for remote resource access

Not a protocol transport for MCP itself — the MCP server still speaks stdio/HTTP to the host — but the *data plane* the server reaches operates over SFTP/SSH against a remote filesystem. Brings paramiko (or equivalent) into core deps. Appropriate when target resources (notebooks, files) live on a remote host and the server runs locally near the LLM.

## Capability surface

The set of MCP entities the server exposes — tools, resources, prompts — plus cross-cutting filtering, gating, and host-side primitives. Constrains what an agent can do, how the host renders the catalog, and how operators tune exposure.

### Single generic tool

One tool that accepts arbitrary input within a domain (e.g., a `query` tool taking arbitrary SQL, a single `fetch` tool). Delegates structuring entirely to the LLM. Appropriate when the underlying engine is itself a query language and the LLM is competent at producing it; minimizes server-side surface area at the cost of giving the LLM no structural guardrails.

### Tools-only narrow surface

A small, focused set of tools (a handful, ~4 to ~14) targeting one domain. No resources, prompts, sampling, or roots. The simplest and most common surface — a tool list with input schemas and a single `tools/call` dispatch path. Appropriate when the project's value is action-oriented (query, mutate, fetch) and there is no static-resource or prompt-template content to expose; ergonomics favor low cognitive load over breadth.

### Domain-bundled tool set

Curated multi-tool surface organized by entity-type or operation class — e.g., job/build/queue/node tools for a CI server, conversation/thread/search/reaction tools for a chat server, notebook-create/read/edit/export tools for a notebook server. Tool counts typically range ~14 to ~25. Resources optionally back the tool surface as listings (e.g., channel and user CSVs as directory resources). Appropriate when the underlying domain has well-defined entities and operations the LLM benefits from seeing as discrete callable units.

### Tools-heavy domain wrapper / domain-tool catalog

Server exposes 20-60+ tools wrapping a single upstream domain exhaustively (one database, one cloud vendor, one IDE language, 30+ ffmpeg media operations, 80+ Playwright browser operations). Schemas hand-authored or auto-derived per tool; tools cover CRUD, metadata, DDL, and management operations. Often paired with capability-grouping mechanisms to let consumers trim exposure. Appropriate when the wrapped binary or domain has a large API the consumer wants accessible end-to-end. Trade-off: large prompt footprint when the host loads all tools.

### Library fan-out

Many tools (90+) wrapping multiple upstream libraries inside one MCP surface — a "Swiss army knife" of a domain (geospatial: Shapely + GeoPandas + Rasterio + PyProj + GDAL + PySAL). Pairs with optional-dependency-per-library packaging so users install only the toolchain slices they need. Appropriate when the domain has multiple authoritative libraries no single one of which is sufficient, and the LLM benefits from one MCP server covering the entire stack.

### Aggregator-tool catalog (many upstreams, normalized tool surface)

Server multiplexes 20+ independent upstream APIs through a smaller set of normalized tools (e.g., `search_papers` dispatching across 20 academic providers; one tool per security data source across 21 vendors). Each upstream's credentials are independent; the tool layer presents a unified interface. Appropriate when the user task is upstream-agnostic ("find a paper," "look up a CVE") and per-upstream details should be hidden.

### Tools plus prompts

The server vends tools and also surfaces MCP "prompts" as first-class artifacts, often declared alongside tools in a manifest. Lets the host present pre-authored prompt templates the user can invoke directly. Appropriate when the project includes idiomatic prompts for working with its tools and the author wants those discoverable through MCP rather than buried in docs.

### Tools + resources + prompts (full primitive coverage)

SDK-built servers exposing the full MCP primitive set — tools, resources, prompts, sometimes plus completion, logging, sampling, roots, elicitation. Appropriate when the SDK is a reference for spec coverage rather than a single-purpose wrapper, or when the application needs both data exposure (resources) and reusable prompt scaffolds in addition to actions.

### Resources alongside tools

In addition to tools, server exposes MCP resources for inspectable state — config dumps (often redacted), debug diagnostics, exported data with TTL-based auto-cleanup. Resources are the read-side surface for state the agent should be able to inspect without invoking a tool. Appropriate when operational transparency matters and the server holds derived artifacts (exports, diagnostics) the agent needs to reference.

### REST endpoints alongside MCP tools

HTTP-mode servers add purpose-built REST endpoints (`/storage/upload`, `/storage/download`, `/storage/list`) for data-plane operations MCP itself is not designed for — binary artifact transfer being the canonical case. Appropriate when the server's domain involves files too large or non-text for MCP message bodies; the MCP layer carries metadata while the REST layer carries bytes.

### MCP Roots participation

A server that consumes the host-provided "roots" protocol — receiving directory boundaries from the host and adapting its file access accordingly. Distinct from servers that take filesystem paths only as launch flags. Appropriate when the server handles user filesystem content and the host wants to dynamically scope access without restarting the server.

### Sampling and elicitation as client primitives

SDK exposes the *client-side* MCP primitives (sampling = LLM completion request back to the host; elicitation = request user input via the host) for applications building agents on top of MCP. Appropriate for SDKs that target both server and client construction.

### Tools plus internal "skills" abstraction

The server vends tools and additionally maintains an internal-to-the-server "Skills" concept — toggleable behavioral bundles that operators can disable per-deployment via an env var. Skills are a higher-level capability primitive than individual tools and can be trimmed at startup to narrow the agent's behavioral surface for specific deployments. Appropriate when the operator audience needs deployment-specific capability profiles (e.g., disable summarization skills in a security-sensitive deployment) without forking the server.

### Tools plus toolset gating

The server vends a large tool catalog (100+) partitioned into toolsets that operators can independently enable/disable via flags or env vars. Adds runtime-discoverable "dynamic toolsets" — the catalog mutates mid-session based on agent action, so hosts that cache the tool list need to refresh. Read-only and lockdown modes act as orthogonal behavior envelopes layered over toolset selection. Appropriate at scale when a single server covers many product surfaces and operators need fine-grained control over what's exposed.

### Tool-level capability gating

Operator can disable individual tools via env var lists (e.g., `DISABLED_TOOLS=tool1,tool2`). Granular but verbose; suitable when a small specific subset needs hiding.

### Category-level capability gating

Operator can enable/disable groups of tools by category (e.g., `OPENSEARCH_DISABLED_CATEGORIES=search_relevance`). Coarser than per-tool gating but matches how operators think about the surface (analytics tools, write tools, admin tools). Appropriate when the tool set is large and naturally clusters into operator-meaningful groups.

### Capability gating via tool subsets at install time

Operator opts in to additional tool families at install time — `--caps=vision`, `--caps=pdf`, `--caps=testing` — rather than getting all tools by default. Distinct from a per-tool toggle: gates groups of related tools as a unit. Appropriate when the surface is large enough that selective exposure changes both the token budget and the security posture.

### Read-only mode flag

Single boolean flag (`--read-only`, `READ_ONLY=true`) suppresses every mutating tool. The remaining surface is the safe-by-default subset. Appropriate as a coarse safety posture — defends against agent-induced data loss without requiring per-tool curation.

### Scope-based tool filtering via URL param

For HTTP-mode servers, query parameters on the connection URL filter the tool surface (`?readonly=true`, `?category=branches`, `?projectId=...`). Different clients hitting the same hosted server see different tool surfaces. Appropriate for multi-tenant remote services where each client (or each session) needs different scoping without separate deployments.

### Destructive-tool elicitation list

Specific tools (drop-database, drop-collection) are flagged as `CONFIRMATION_REQUIRED_TOOLS`; invoking one triggers an MCP elicitation requesting human confirmation before execution. Appropriate as a per-tool safety rail beyond a coarse read-only flag — agents can invoke destructive tools but the human is brought into the loop.

## Capability authoring style

How the project's tool implementations get written and registered. Constrains who can extend the server and what skills the change requires.

### Code-defined tools via SDK decorators

Tools are Python/TypeScript/Go/Clojure functions decorated or registered programmatically; signatures and schemas derive from type hints or explicit registration calls. Adding a tool requires editing source and rebuilding/restarting. The SDK handles MCP-protocol marshalling. Appropriate when tool logic is non-trivial (custom data fetching, transformation, validation) and authors are also developers of the server.

### Declarative manifest authoring (YAML)

Tools, toolsets, sources, and prompts are declared in a YAML manifest the server reads at startup; admins add tools by editing YAML rather than writing code. The server provides a fixed set of "source" abstractions (database connectors, API clients) the manifest composes against. Hot reload propagates manifest changes without restart. Appropriate when the goal is to let non-developer admins (DBAs, ops) define tools against pre-built primitives, especially across many database back-ends.

### Dynamic registration via API

The server exposes a programmatic registration API; consumers can add tools to a running server via that API rather than only at startup. Decouples tool-set definition from the server's source. Appropriate when the server is embedded in a larger app that wants to vend its own tools through the same MCP endpoint.

## Configuration delivery

How operational configuration reaches the server at startup or runtime. Constrains how hosts wire credentials and how operators tune behavior.

### Environment variables

Config flows in via env vars set by the host before launching the server child process — credentials, behavior toggles, encoding hints (`PYTHONIOENCODING=utf-8` on Windows). Often the only documented surface for stdio servers because the host can inject env vars in its config block (e.g., `claude_desktop_config.json`'s `env` block merged into the child's environment). Project-prefix conventions (`MDB_MCP_*`, `PAPER_SEARCH_MCP_*`, `OPENSEARCH_*`) prevent collision in shared environments; a `.env` file is commonly supported as a developer-friendly source. Required for credentials that should not appear on command lines (process listings, shell history) and the natural fit for container deployments where flags would require image rebuilds. Appropriate for credentials, transport selection, deployment-specific endpoints, and any runtime knob that varies per environment.

### CLI flags

Flags parsed at process start (`--db-path`, `--readonly`, `--keep-connection`, `--host`, `--port`, `--allow-root`, `--read-only`, `--write-access`, `--toolsets`, `--motherduck-token`). The native fit for stdio servers launched by host configs that pass `args`. Common alongside env vars — flags override or supplement env values, and flag presence may select subcommands or modes. The most-discoverable surface (one `--help` away). Appropriate for static, per-instance configuration where re-launch is acceptable and the operator wants visible, declarative configuration over implicit env var inheritance.

### CLI flags with paired env-var equivalents

Each flag has a `<PROJECT>_<FLAG>` env-var twin so the same setting can be supplied either way. Appropriate when the surface grows large (50+ flags) and ops want env-var overrides without rewriting host config.

### `.env` file at server CWD

A `.env.example` template ships in the repo; the operator copies and edits. Appropriate for development-only or single-machine deployments where env var injection through the host is awkward.

### YAML manifest

Config flows in via a structured YAML file referenced by `--config <path>` or by convention (`example_config.yml`). The manifest defines sources, tools, toolsets, prompts, and operational settings in one place. Hot reload is feasible because the manifest is a separate file the server can re-read. Appropriate when configuration is large, structured, and likely to evolve — too much for env vars or flags — and for project-governed servers where operator-facing config files are a deliverable artifact.

### JSON config file via `--config <path>` or env-var pointer

A separate JSON file holds the full settings block, referenced by a single CLI flag or env var (e.g., `MDB_MCP_CONFIG`). Centralizes settings; supports complex nested configuration that flags or env vars handle awkwardly. Appropriate when the surface is too large for per-flag CLI ergonomics (Playwright's 50+ knobs) and the operator wants to version-control their settings independently from the install command.

### Code-level configuration (functional options pattern)

The SDK is a library; configuration happens at compile/build time via constructor calls and option functions (`WithToolCapabilities()`, `RegisterSession()`, `RegisterTool()`). Appropriate when the consumer is writing the server program themselves rather than running a pre-built binary.

### Host-side JSON config snippet

The repo doesn't deliver config to the server; instead the README documents a JSON snippet users paste into per-host config files (`mcp.json`, `claude_desktop_config.json`, `.cursor/mcp.json`, `~/.cursor/mcp.json`, `.vscode/mcp.json`, `cline_mcp_settings.json`). The same content that would appear as CLI flags is encoded as JSON the host translates into a child-process invocation. The host owns config delivery; the server only reads what arrives. Universal across all stdio-launched servers regardless of runtime, and the user-facing surface — humans rarely write the raw command lines themselves.

### HTTP request headers

Per-request credentials or overrides supplied on each MCP request (`x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password`, `Authorization`). Required for per-request multi-tenancy under HTTP transport. Appropriate when the server is shared and each caller carries their own upstream identity.

### URL query params on HTTP connection

For HTTP-mode servers, request-time scoping happens via query params on the host's connection URL. Different from env/CLI/file because each client connection can carry different params. Appropriate for hosted multi-tenant services that need per-connection scoping without per-tenant deployments.

### Per-request header overrides

Server accepts headers on each MCP request that override server-wide config (`--allowRequestOverrides=true`). Powerful for HTTP multi-client setups where each client's request needs a slightly different posture. Appropriate when one server instance serves many clients with overlapping but not identical needs.

### Auto-generated host-config JSON files

Installer (`install.py`) writes ready-to-paste `mcp_config_claude.json`, `mcp_config_vscode.json` files per supported host. Operator points the host at the generated file. Appropriate for installer-first distributions where the user is walked through setup interactively rather than reading docs.

### Host-supplied protocol-level config (MCP Roots)

The server picks up directory scope from the host through MCP messages rather than from CLI/env. Appropriate when the bound concept is something the host owns dynamically (open project, user workspace) rather than a static install setting.

## Authentication

How the server proves the operator/agent has the right to call upstream APIs and how clients prove themselves to the server. Constrains the deployment model — single-tenant local processes vs multi-tenant hosted services.

### None (local-resource gating)

No auth at the MCP layer. The server operates on a local file or process the host already has access to, or the upstream service is genuinely public (Microsoft Planetary Computer STAC, public GitHub repos via cloud documentation service). Trust is implicit because the host launches the server as a child process under the user's identity. Often paired with a path-restriction mechanism (workspace root enforcement via `os.path.realpath`, explicit `--allow-root` opt-in) to prevent traversal outside an intended directory. The Playwright server explicitly notes "MCP is not a security boundary" — making non-auth a stated design posture rather than an oversight. Appropriate when the server is a child process of the host, the upstream is public, or the data lives entirely on the host's filesystem.

### Static API key / token via env var

A single long-lived secret read from an env var at startup (`LINEAR_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `SENTRY_ACCESS_TOKEN`, `NOTION_TOKEN`, `SLACK_MCP_XOXC_TOKEN`, `motherduck_token`, `NVD_API_KEY`). Ties the server process to one identity for its lifetime. Simplest credential model; universal across stdio servers, the path of least resistance when the upstream service supports PATs, and suitable for single-vendor servers and dev environments. Appropriate when one user's credentials are correct for the entire process and rotation can happen by restarting with a new env var; no expiry or rotation mechanism in the server itself.

### Connection-string auth to upstream database

Server holds a credential in a single connection string (MongoDB URI, Postgres DSN). Suitable when the upstream is a database accessed through a driver that natively consumes a string credential. Limited to one credential set per process.

### Service-account credential pair to cloud API

Server holds a Client ID + Client Secret to a cloud vendor's API (MongoDB Atlas, AWS); often paired with IP allowlist requirements. Appropriate for managed cloud services where API-key-pair is the vendor's auth norm. Server may auto-provision short-lived database users (e.g., 4-hour TTL) on top of the long-lived service-account credential to limit blast radius.

### Multi-mode token selection

The server accepts several distinct credential types for the same upstream service (e.g., browser cookie, user OAuth token, bot token) and selects behavior based on which is supplied. Enables operating modes ranging from "stealth" (no workspace permissions, browser-cookie-based) to formal OAuth with workspace admin approval. Appropriate when the upstream service's permission model varies sharply by credential type and the server needs to support all of them.

### Multi-scheme upstream auth (basic / IAM / header / mTLS)

Server supports multiple auth schemes for the same upstream type (basic auth, AWS IAM roles, header-based auth, mutual TLS) so one binary covers self-hosted, managed-cloud, and mTLS-secured deployments. Appropriate for project-governed servers expected to work across the upstream's full deployment matrix.

### Per-source independent API keys with graceful degradation

Aggregator server expects N independent API keys for N upstreams; each key is optional. Tools whose upstream lacks a key report the gap rather than failing the whole process. Appropriate for aggregator surfaces where users may only care about a subset of upstreams. Keys must never be logged or cached in audit entries.

### OAuth on hosted endpoint

OAuth 2.0 / 2.1 flow with scope-based permissioning (`read`, `write`, `*`) handled by the hosted-service deployment of the same product; per-user identity is established at connection time rather than at process startup. Token presented via `Authorization: Bearer` header. Per-request tenancy possible because each token carries its own scope. Local stdio mode falls back to PAT/static-key. Hosts with native MCP OAuth support (e.g., VS Code 1.101+) handle the flow transparently. Requires HTTP transport (browser cannot redirect to a stdio process). Appropriate when the same code is operated both as a per-user local install and a multi-tenant SaaS — the auth path branches on transport.

### HTTP bearer token / API-key bearer header

The HTTP transport accepts `Authorization: Bearer <token>` and validates per request. Either a coarse "is this a known client" check, or a headless alternative to interactive OAuth (same scoping model without browser redirect). Token supplied to the server via env or config. Appropriate when one server instance serves multiple network clients, for CI, server-to-server, and environments where browser flow is infeasible.

### Per-request HTTP-header credentials

Credentials passed in HTTP headers on each MCP request (`x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password`) instead of being baked into the server process. Turns a normally single-tenant stdio server into a multi-tenant HTTP service: one deployed server can route different requests to different upstream instances and credentials. Requires HTTP transport. Appropriate when one server instance must serve multiple end-users or multiple upstream environments without per-tenant deployment.

### Multi-scheme client auth (API key / OAuth / JWT / Basic / Bearer)

Server-side acceptance of multiple credential types from clients calling the server, paired with rate limiting, circuit breaker, and audit logging. Appropriate when the server is a security/compliance tool that itself must prove multi-scheme readiness; otherwise excessive complexity for a single-tenant local server.

### SFTP / SSH credentials

Username + key or password (or interactive prompt) for the remote filesystem the server reaches over SFTP. Auth mode itself is configurable (`--sftp-auth-mode auto/key/password/key+interactive`). Appropriate when the data plane is remote-filesystem rather than HTTP-API.

### Application-delegated (SDK provides nothing)

The SDK exposes session-registration hooks but does not bundle an auth mechanism — applications wire their own at the transport layer. Appropriate for SDKs that want to remain unopinionated about deployment context (cloud, on-prem, in-process).

### Delegated to upstream source

Authentication isn't a server concern at all — the server connects to upstream sources (databases, cloud APIs) using whatever credentials those sources expect, configured per-source in the manifest. Includes ambient credentials (Google Cloud ADC, IAM) and per-database static credentials. Appropriate when the server is a multi-source proxy and each source has its own auth story.

### Domain-level access gate (not auth)

The server enforces what can be accessed (filesystem allowlist, repository path, robots.txt for fetch) without identifying the caller. A different control plane — authorization without authentication. Appropriate when the threat model is "constrain what the trusted caller can ask," not "verify who is asking."

## Multi-tenancy

How identities are partitioned within a single server instance. Tightly coupled to transport.

### Single-user single-process

One process serves one identity for its lifetime, state global to the process. Inevitable consequence of stdio + static API key. The host launches a fresh process per user/workspace. Appropriate when isolation is per-process, the host already isolates per-user by spawning per-user processes, and the cost of process startup is acceptable.

### Workspace-keyed with path enforcement

Single-user but with explicit workspace-root boundaries enforced by canonicalizing paths (`os.path.realpath`) and rejecting access outside an allow-listed root. A path-traversal defense that lets the server operate on local files while bounding the blast radius. Appropriate when the server has filesystem access and the host's working directory is treated as the security boundary.

### Single-user-per-workspace

Server is single-user but workspace-scoped via `WORKSPACE_PATH` env var; running multiple instances against multiple workspaces is the multi-tenancy story. Appropriate for IDE-integrated developer tools where workspace = project.

### Per-user OAuth on hosted endpoint

The hosted deployment of a product maintains per-connection identity via OAuth, while the same code in stdio mode is single-user-per-process. The two modes share a capability surface but differ in tenancy. Appropriate when one product needs both deployment shapes.

### Per-request tenancy via OAuth token scoping

Each request carries a token whose scopes determine tenant access. Server is multi-tenant by design; tenancy lives in the token, not in the server config. Appropriate for hosted remote services serving many independent users from one deployment.

### Per-tenant via URL parameter

A hosted service multiplexes tenants by parameterizing the URL path (e.g., `/{owner}/{repo}`). One deployment serves arbitrarily many tenants without per-tenant state. Appropriate when the upstream resource is itself addressable by URL parameter (a public repo, a public dataset).

### Per-request HTTP tenant via headers

HTTP-header credentials let each MCP request specify its own upstream target and identity, so one deployed server multiplexes many tenants. Pairs with HTTP transport and stateless request handling. Appropriate when the server is a shared deployment serving heterogeneous upstream targets.

### Per-workspace tenant via upstream token

The upstream service's auth model is the tenancy boundary — one Slack workspace token equals one tenant; per-user isolation falls out of the upstream's own DM/channel scoping. Appropriate for services whose permission model is workspace- or organization-scoped natively.

### Per-process multi-source

The process serves one identity but composes data from multiple back-end sources declared in its manifest. Tenancy isn't user-based; it's source-based. Appropriate when one operator (DBA, platform team) operates one server against many databases.

### Per-session state via session registration

The SDK exposes a session abstraction — `RegisterSession()`, notification channels keyed by client — so a single server process can handle multiple concurrent clients with isolated state. Appropriate when the server runs as an HTTP service and "one process per user" is too costly.

### Externally-managed sessions via header

HTTP-mode server keeps sessions distinguished by `mcp-session-id` header when `EXTERNALLY_MANAGED_SESSIONS=true`. Per-session, not per-tenant; a single credential set still serves all sessions. Appropriate when an HTTP MCP gateway in front of the server handles tenant routing and the server only needs session affinity.

### Stateless per request

Pure request/response with no session affinity; each HTTP call carries everything needed. Appropriate when the wrapped operation has no per-client state to track.

### Connection-lifecycle as a knob

Some servers expose connection persistence as an explicit flag (`--keep-connection`, `session-singleton mode`). Trade-off: persistent connections enable cross-call state (TEMP tables, pooled clients) but break the stateless-per-request model and complicate multi-tenant safety. Appropriate when the underlying engine has session-scoped state worth preserving and the deployment is single-tenant.

## Distribution channel

How the server reaches the user's machine or how users address the running service. Constrains install ergonomics and platform reach.

### PyPI package via pip

Server published to PyPI; users install with `pip install <package>`. Standard Python distribution. Package name often mirrors the server's domain (`mcp-server-duckdb`, `gis-mcp`, `mcp-jenkins`, `cursor-notebook-mcp`). Appropriate when target users have a Python environment ready and the server has a meaningful identity beyond a single script.

### PyPI via uvx (zero-install runner)

`uvx <package>` runs the package without persistent installation, fetching from PyPI on demand and provisioning an isolated venv per invocation. Often the README's recommended invocation for Python servers because it sidesteps virtualenv ceremony for end users and eliminates environment conflicts. Appropriate as the recommended path for FastMCP/Python servers and when end-users want to avoid maintenance of a Python environment.

### PyPI via uv tool install

Server published to PyPI; users install via `uv tool install <package>` for a persistent isolated environment. Appropriate for daily-use servers where per-invocation provisioning would be wasteful.

### npm package via npx

JavaScript/TypeScript servers publish to npm; `npx -y <package>` is the typical invocation. CommonJS bin entry registered in `package.json`. Latest-version-on-each-call ergonomics; npm pkg metadata also enables `claude_desktop_config.json` `"command": "npx"` snippets. Appropriate for Node servers, aligns with how host MCP configs already invoke other npm tools, and zero-install ergonomics because npx fetches on first run.

### Pre-built binaries via GitHub Releases

Cross-platform binaries (Linux, macOS, Windows; AMD64, ARM64) attached to GitHub release tags. Users download via a script or manually and run directly. Avoids a language-runtime prerequisite. Source tarballs and changelog often published per release as a fallback for users not on language-specific package managers. Natural fit for Go and other compile-to-static-binary runtimes. Appropriate when the audience may not have the source language's toolchain installed.

### Docker / OCI images

Image published to a registry (Docker Hub, GHCR, GCP Artifact Registry, `mcp/<name>` namespace, or vendor registry like `mcr.microsoft.com/<vendor>/<server>`); users `docker run -i --rm` (often with mounts) or wire the image into a host config snippet. Provides zero-install dependency isolation; the canonical install path for several large official servers. Multi-platform builds (amd64/arm64) are common, and sometimes paired with multiple Dockerfiles (`Dockerfile` for prod, `Dockerfile.local` for dev). Constrains transport choices (volume mounts for stdio interop) but provides reproducible deployment. Cross-role: also serves as the test stack and the deployment artifact for some samples. Appropriate when the server has system-tool dependencies (ffmpeg, browsers, system libraries), when the operator wants language-agnostic distribution, when consistent runtime + dependency packaging matters more than launching a native process, or when the deployment is a long-running service via `docker-compose`.

### docker-compose variants

Multiple compose files for distinct use cases (`docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.toolkit.yml`) — each codifies a deployment flavor. Appropriate when the server has meaningfully different operating modes (dev vs prod vs ad-hoc tooling) that benefit from distinct compose configurations.

### Source language package manager

`go install` for Go modules; `pnpm install` / `npm install` for TypeScript; `uv sync` for Python; Git dependency in `deps.edn` for Clojure; Maven Central for Kotlin/JVM SDKs. Each requires the audience to have the language toolchain installed. Appropriate as a developer-targeted distribution alongside binary or Docker for end users.

### Maven Central artifacts

Published as `<group>:<artifact>` to Maven Central, consumed via Gradle/Maven dependency declarations. Granular artifact split (umbrella + client + server) lets consumers depend on just the half they need. Appropriate for JVM-targeted SDKs.

### Go module via `go get`

Users add the import path to their `go.mod`. The "distribution" is the source code itself; consumers compile their own binary. Appropriate when the artifact is an SDK rather than a runnable server.

### Homebrew formula

A `brew install` path on macOS (and Linux via brew). Wraps a binary download with a tap-managed update channel. Appropriate as one channel among several when reaching macOS-heavy developer audiences matters.

### NPM shim wrapping a non-Node binary

An npm package (`@scope/server`) that downloads or wraps a native (Go, etc.) binary so node-oriented hosts can run the server by name via `npx`. Cross-ecosystem glue — the server isn't a Node program, but the install surface is. Appropriate when the audience expects `npx` install paths regardless of the server's actual runtime.

### Hosted endpoint (no install)

Users address a running URL (`gitmcp.io/{owner}/{repo}`, `mcp.sentry.dev`, `api.githubcopilot.com`, `https://mcp.neon.tech/mcp`); no install on the user's side. The maintainer operates the deployment and controls rollout, version pinning, and auth model (typically OAuth). Appropriate when a single hosted instance can serve many users (public-data services, official cloud-backed products) or when the vendor wants control over deployment.

### Smithery registry

`smithery.yaml` registers the server with the Smithery host-installer ecosystem; users install via `npx -y @smithery/cli install <name>` or `npx -y @smithery/cli install @<owner>/<repo> --client claude`. Smithery acts as a discovery + auto-config layer over the underlying npm/PyPI package. Appropriate as an additional channel for hosts that consume the Smithery directory or for visibility in the Smithery marketplace.

### MCP Bundle (.mcpb) / Desktop Extension manifest

Server packaged as an `.mcpb` bundle for Claude Desktop drag-and-drop installation, with `.mcpbignore` controlling bundle contents. A Claude Desktop-specific packaging format (DXT — `manifest-dxt.json`) distinct from `.mcp.json`. Ships alongside the server as a discoverable extension manifest. Appropriate as a frictionless install path for non-developer Claude Desktop users and when the server targets Claude Desktop as a primary integration.

### Source clone

The repo is cloned and run from source (`uv sync` then `uv run python <script>.py`, `pip install -e .`, `npm install`) — no published artifact. The minimum viable distribution. Appropriate for early-stage repos that haven't published, personal tools, demonstrations, projects with system-level dependencies that resist packaging, internal tools, or frameworks where consumers are expected to build atop the source.

### SDK CLI installer

A framework-specific installer command (`fastmcp install <script.py>`) registers the script with target hosts and wires up the runtime invocation. Appropriate within ecosystems whose SDK provides such a CLI; substitutes for hand-edited host config files.

### Interactive installer script

Server ships an `install.py` (or similar) that runs an interactive setup — picks installation mode, generates host-config files, writes credentials. Appropriate when the install requires multi-step decisions the user can't easily make from a flat CLI invocation.

## Entry point

The literal command shape users or hosts type to launch the server. Constrains how host-config snippets are written and how upgrades propagate.

### Console script

A package-declared entry — `pyproject.toml`'s `[project.scripts]` defines `mcp-server-<name>` mapped to a `:main` entry point; npm `package.json`'s `"bin"` field defines the equivalent. Installs a binary on the user's PATH. Host config simply names the command. Appropriate as the canonical, name-collision-safe Python and npm pattern when the package is registry-distributed.

### Module invocation / `python -m <module>` fallback

`python -m package.server` — Python's module entry point. Avoids requiring a console-script entry, or available alongside a console script as an alternative for advanced users invoking from a known interpreter. Appropriate when the project is happy to expose its package path to users; common in source-distributed Python servers using uv.

### Bare interpreter + script path

`python /abs/path/to/server.py` or `node /abs/path/to/server.js` — a single `.py` or `.js` file with no installable entry point. The host config snippet embeds the absolute path. Appropriate for source-clone distribution, single-file servers, demonstrations, and minimum-ceremony servers; the cost is that the operator has to know where the file lives.

### Subcommand verb

The binary takes a subcommand selecting mode (`server stdio`, `server serve --write-access`, `server setup --tool=cline`). Mode is an explicit verb rather than a flag, separating "run the server" from "configure a host" cleanly. Appropriate when the binary has multiple roles beyond running the server.

### Hosted URL endpoint

Not a command at all — users put a URL in their host config (`https://mcp.neon.tech/mcp`, `gitmcp.io/{owner}/{repo}`). The host opens an HTTP/SSE connection. Appropriate for hosted-deployment products.

### `npx` package invocation

`npx @scope/server@latest --flag value` or `npx -y <pkg>` — node ecosystem's pull-and-run convention. Often paired with the npm distribution channel. Appropriate when the audience has Node and benefits from no-explicit-install ergonomics.

### Ephemeral runner (`uvx`, `uv run`)

The command resolves the package on demand and invokes its entry point: `uvx <pkg>`, `uv run server.py`. Appropriate when the operator wants no persistent install state and is happy to re-fetch on cache miss.

### Profile-driven launcher

`clj -M:profile` — Clojure's profile mechanism, where `:stdio-server` and `:sse-server` are aliases in `deps.edn` selecting transport mode. Appropriate within Clojure tooling where profiles are the idiomatic launch surface.

### Framework CLI run

`fastmcp run <script>` or `fastmcp install <script>` — framework's own CLI handles the runtime invocation. Substitutes for a project-level entry point. Appropriate when committing to the framework's conventions.

### CLI dispatcher subcommand

User runs `uvx <dispatcher> <server-name>` where the dispatcher routes to a child server within a monorepo PyPI package. Appropriate for monorepos that ship many servers under one package namespace.

### SDK constructor + transport-method launch

The server is a program the consumer wrote — `server.NewMCPServer()` returns a server value, then `server.ServeStdio()` or `server.ServeSSE()` runs it. The launcher is the consumer's `main`. Appropriate for Go/Kotlin SDK consumers building bespoke servers.

### Programmatic embedding via library function

The SDK exposes `createConnection()` (or analog) that returns an in-process MCP endpoint a host process can consume directly without subprocess IPC. Appropriate when the host is itself a Node/Kotlin app and wants to embed the server's tool surface as a library, blurring the server/client boundary.

### Container as launcher / Docker run

The host config command is `docker run -i --rm --mount ...` rather than the server's native binary. The image's ENTRYPOINT is the actual launcher. Appropriate when the server is HTTP-mode-only, when system dependencies make non-container launch fragile, or when multi-arch concerns make Docker the most reliable attach surface.

## Setup ergonomics

Tooling that helps users wire the server into a host without hand-editing JSON. Cross-cutting with distribution + entry point but a distinct concern.

### `setup` subcommand

The server binary itself ships a `setup --tool=<host>` subcommand that writes the right host-config snippet for a target host. Rare; most projects expect users to hand-edit JSON. Designed as an extension point — the flag's value space lists supported hosts and grows over time. Appropriate when the audience is non-technical or the host-config format is non-obvious.

### Framework CLI installer

The runtime framework provides `framework install <script>` that registers the script with target hosts. Same effect as a per-server setup verb but factored into the framework. Appropriate when the framework owns this concern across many servers.

### Marketplace plugin

The server is also published as an installable plugin in a host's plugin marketplace (Claude Desktop plugin, gemini-extension). Users install via the marketplace UI; no JSON editing. Appropriate when the audience is mainstream users of a specific host and the host has a plugin marketplace.

### README JSON snippets

The README enumerates per-host JSON config blocks the user copies and pastes into the host's MCP config file. The default for every server that doesn't ship a setup verb. Universally supported, but high friction relative to setup verbs or marketplace installs.

## Host integration

How the server gets wired into specific MCP-host applications. Constrains documentation surface and onboarding friction.

### Per-host README JSON snippets

The README ships copy-paste JSON config blocks for each supported host (Claude Desktop, Claude Code, Cursor, Zed, VS Code, Windsurf, Cline, Goose, Junie, Copilot, Factory, Gemini CLI, LM Studio, Kiro, opencode, Qodo Gen, Warp, Codex, Antigravity, Amp, JetBrains, etc.) showing the `command`/`args` shape with minor wrapper differences across hosts. The most common pattern; cheap to add a new host but high user friction. Appropriate when the server targets the broadest possible host audience and the maintainer is willing to maintain per-host examples.

### Single canonical host snippet

One JSON snippet — usually for `claude_desktop_config.json` — with a generic note that other MCP hosts use similar config. Appropriate when the maintainer wants the docs surface small and assumes operators can adapt.

### Per-OS path documentation

The Claude Desktop section enumerates Windows, macOS, and Linux config paths. Appropriate when the install audience is non-developer-heavy and "where is the file" is itself a documentation gap.

### Claude Code via `claude mcp add`

CLI registration via `claude mcp add <name> -- <command>`. Appropriate as the native Claude Code path — no JSON file editing.

### Cursor IDE config / install button

`.cursor/mcp.json` (project-scoped) or `~/.cursor/mcp.json` (global). Some servers explicitly document both levels; transport (stdio vs HTTP) is inferred from whether the entry specifies `command` or `url`. Some vendors render one-click install buttons in the README to optimize for the Cursor user base. Appropriate when Cursor is a primary host.

### VSCode / Insiders config and install badges

`.vscode/mcp.json` entry for the VSCode MCP integration / Copilot Chat consumer, plus README-rendered badges that pre-fill VS Code's MCP integration UI. Appropriate when VS Code is a primary host and the badge system is preferable to copy-paste snippets.

### JetBrains IDE

Native MCP integration documented per JetBrains product line. Appropriate when the upstream domain (database, language) has a strong JetBrains user base.

### Smithery registration

`smithery.yaml` registration plus the Smithery CLI installer chooses the right host-config block for the user's chosen client.

### DXT / MCP Bundle manifest

`manifest-dxt.json` provides Claude Desktop-specific extension packaging; `.mcpb` bundles ship as drag-and-drop installs. Appropriate as low-friction installs for non-developer Claude Desktop users.

### In-repo Claude plugin wrapper

The repo ships a `.claude-plugin/` directory and `.mcp.json` so the server installs as a Claude plugin without any additional wrapping by the user. Rare; the server vends itself as a plugin, not just a raw MCP binary. Appropriate when the maintainer wants Claude users to have a one-click install rather than a config-file edit.

### Co-located VS Code extension

A parallel VS Code extension (TypeScript) ships in the same repo as the MCP server. Provides a non-MCP integration path alongside MCP. Appropriate when the audience uses VS Code heavily and wants editor integration deeper than MCP would provide.

### First-party host extension manifest

A host-specific manifest file (e.g., `gemini-extension.json`, `.gemini/` directory) declares the integration with a specific host the project has a special relationship with. Appropriate when the project is owned by or aligned with the host's vendor.

### Framework-installer wires hosts

The framework's CLI installer registers the server with the target host transparently — no user-facing snippet, the framework knows how to talk to each supported host. Appropriate when committing to a framework that has solved this concern.

### Codex CLI / Copilot CLI / Gemini CLI

Non-Anthropic agent CLIs that consume MCP. Appropriate when the server's user base spans agent ecosystems.

### LangChain integration

Server documents LangChain consumption (typically via a LangChain MCP adapter). Appropriate when the upstream domain (search, retrieval) is also a common LangChain use case.

### Production reference implementation

Instead of (or in addition to) host snippets, the README points to a real-world server built on the SDK as a reference. Appropriate for SDKs where the right "integration example" is a complete project, not a config block.

## Test stack

How the project verifies its own behavior. Constrains release cadence and refactor safety.

### pytest with async + coverage

Python servers consistently choose pytest with `pytest-asyncio` (`asyncio_mode = "auto"`, per-function loop scope), `pytest-cov`, and frequently `pytest-timeout`. FastMCP itself stretches this further with `pytest-flakefinder`, `pytest-retry`, `pytest-xdist`, `inline-snapshot`, `pytest-examples` — flake hunting and parallelism investments rare among consumers. Some servers ship cross-platform shell wrappers (`run_tests.sh`, `run_tests.ps1`). Test plans codified in markdown (`test_plan.md`) appear when scenarios outweigh unit cases. Tests live in `tests/` discovered by `pytest`, or `test_*.py` files alongside `server.py` in early-stage single-file repos. Appropriate for any Python server; investment level scales with surface area.

### Vitest (Node)

`npm test` runs Vitest with coverage configured (`npm run test:coverage`); tests under `/tests` configured via `vitest.config.ts`. Appropriate for Node servers; good async ergonomics, TypeScript-native ESM.

### Go stdlib testing

`*_test.go` co-located with implementation; integration tests in `e2e/` or `integration_test.go`. The default Go path; no extra framework needed.

### Multi-tier Kotlin testing

Dedicated `kotlin-sdk-testing` artifact, `integration-test/` module, `conformance-test/` module, plus snippet-test infrastructure (Knit). Appropriate when the project is a spec-conforming SDK and conformance is a deliverable in its own right.

### MCP Inspector as test driver

`@modelcontextprotocol/inspector` invoked via `npm test` to exercise the server end-to-end through the MCP protocol itself. Common in TypeScript servers; sometimes recommended (rather than wired) for Python servers as a manual debugging aid. Appropriate when the value is in protocol-level integration rather than unit-level coverage.

### Recorded HTTP fixtures (cassettes)

Tests run against checked-in HTTP recordings (go-vcr cassettes, similar libraries) so the suite is reproducible offline without upstream credentials. A separate live-mode flag re-records when the upstream API changes. Appropriate when tests need to exercise real upstream API shapes but CI shouldn't pay per-run API costs or require credentials.

### Evaluation harness alongside unit tests

A separate `eval` task that runs scenario-based evaluations against model outputs, distinct from unit tests. Catches behavioral regressions that unit tests can't (e.g., a tool description change degrading model accuracy). Appropriate when the server's value depends on how well models use its tools, not just whether the tools work.

### End-to-end with browser automation

Playwright tests exercise the full stack from a real browser/host through the MCP endpoint. Higher fidelity, slower, more brittle. Appropriate when the deployment includes a web UI alongside MCP.

### Test configuration via project alias

A test-only profile (`tests.edn`, similar) declares the test runner config separately from the main project. Appropriate within ecosystems where alias-driven tooling is idiomatic (Clojure).

### In-memory transport for protocol tests

Tests instantiate server and client in the same process and exchange messages via in-memory transport, skipping serialization overhead and process boundaries. Appropriate for verifying protocol-level behavior in isolation.

### Stratified suite with unit + integration + cache + security tiers

Tests split by concern — unit (pure logic, e.g., risk scoring), integration (tool registration and error handling), cache (TTL behavior against an in-process SQLite), security (private-IP blocking, XML-bomb protection). Appropriate when the server has cross-cutting infrastructure (cache, security) that warrants its own test scope.

### Pyramid with web E2E (Playwright + ephemeral DB)

Unit + integration + protocol-level E2E + browser E2E using Playwright against an ephemeral database provisioned per test run. Appropriate for hosted MCP servers with a web UI surface (OAuth consent screens, landing pages) that traditional MCP tests don't exercise.

### Separate integration_tests/ directory

Unit tests under `tests/`, real-upstream integration tests under `integration_tests/`. Different invocation paths; integration tests typically gated on CI secrets. Appropriate for project-governed servers where against-real-upstream validation is a separate cost class from unit tests.

### MyPy strict + Bandit security scans alongside tests

In addition to runtime tests, pyproject.toml configures strict static type checking and Bandit security scanning. Appropriate for security-sensitive servers and projects with explicit static-analysis discipline.

### `pytest` declared as runtime dependency

Quirk where `pytest` lands under `[project.dependencies]` rather than `[dependency-groups]`. Almost always an oversight rather than a design choice; ships test framework to all consumers.

### Undocumented / minimal / none

Some servers ship without tests — particularly minimal single-file scripts where the value lies in being demonstrative, personal-tool-tier servers, or early-stage repos. Appropriate only when the surface is small enough that manual verification suffices; raises bus-factor risk for anything broader.

## CI

Automated build/test gating on pushes and PRs. Constrains release safety and contribution velocity.

### GitHub Actions

The dominant choice across the corpus — workflows under `.github/workflows/` triggered on push, PR, and version tags. Multiple workflows commonly cover test (`ci.yml`), lint (`golangci-lint.yml`, ruff/pyright equivalents), docs (`pages.yml`), release automation (`release.yml`). Often paired with codecov integration and automated release artifacts (binary builds, container pushes). Appropriate as the default for any GitHub-hosted project.

### GitHub Actions plus dedicated lint config

GitHub Actions plus a language-specific linter config checked in (`.golangci.yml`, `.cljstyle`, `clj-kondo`). Lint runs as a CI step, separate from tests. Appropriate when style and static-analysis enforcement matters and the project wants the lint rules versioned alongside the code.

### Release-cut workflow on tag push

A workflow triggered specifically by version-tag pushes that builds and uploads release artifacts (cross-platform binaries, container images, npm/PyPI/Docker fanout). Decouples release from CI's normal pass/fail gate. Appropriate when releases are a deliberate event and not every passing build should produce one.

### Vercel preview-per-PR + main deploy

Hosted-service repos use Vercel's per-PR preview deployments; merging to main auto-deploys to production. Appropriate for Next.js-hosted MCP servers where the deployable artifact is the running service.

### Documented but not necessarily wired

The README shows a GitHub Actions YAML example (often because system deps like ffmpeg need an `apt-get install` step) but the actual `.github/workflows/*.yml` may or may not exist. Appropriate as a copy-paste seed for downstream consumers.

### None / absent

No CI configured. Common in early-stage repos and small single-author tools.

## Container / packaging artifacts

Files in the repo that define how the server gets containerized or otherwise deployment-packaged. Distinct from the distribution channel — these are the artifacts that produce the channels.

### Single Dockerfile

One Dockerfile in the repo root or `/docker/` subdirectory that produces the image published to a registry. Often multi-platform via Buildx. Appropriate as the minimum viable container artifact when distributing via Docker and the server has one canonical container shape.

### Multi-Dockerfile (prod / dev split)

`Dockerfile` for production image plus `Dockerfile.local` for development. Explicit separation when the dev image needs additional tooling or different base. Appropriate when development needs diverge meaningfully from production.

### Multi-stage Dockerfile

Separate build and runtime stages; final image excludes build dependencies. Appropriate for production-bound servers where image size and attack surface matter.

### Per-server Dockerfile in monorepo

Each server in a monorepo has its own Dockerfile; images publish to Docker Hub under `mcp/<name>` or vendor namespace. Appropriate when the repo is a curated reference set and consumers want one-image-per-server semantics.

### Vendor-namespaced image

Image lives in a vendor registry (`mcr.microsoft.com/playwright/mcp`) rather than the public `mcp/*` namespace. Multi-arch builds extend reach. Appropriate when the publisher is a brand-conscious vendor with its own registry.

### Dockerfile + docker-compose

Repo ships both a `Dockerfile` (single-container build) and a `docker-compose.yml` (orchestrated service definition), sometimes with mode-specific variants (`.dev.yml`, `.toolkit.yml`). Appropriate when the operator wants a one-command launch including any sidecars or distinct compose orchestrations encode distinct operating flavors.

### Dev container

A `.devcontainer/` directory defining a development environment in a container. Separate concern from runtime distribution. Appropriate when the author wants contributors to spin up an identical dev environment without local toolchain installation.

### Cloudflare Workers config

`wrangler.jsonc` declares the Workers deployment. There is no Dockerfile because the runtime substrate is the Workers platform. Appropriate when the project is itself a Workers application.

### Hatch force-include for monorepo wheel

Custom `pyproject.toml` directive pulls nested `<package>/servers/` directories into the wheel when the canonical Python packaging path doesn't recognize them. Appropriate for dispatcher-style monorepos that ship one PyPI package containing many servers.

### `.mcpbignore` for bundle packaging

Glob file controlling what's excluded from the `.mcpb` bundle. Appropriate alongside MCP Bundle distribution.

### Azure deployment artifacts

`deploy/` directory with Azure-specific guides and scripts. Appropriate for vendors who want to provide first-class managed-cloud deployment paths.

### None observed

Some samples ship no container artifacts — distribution is via source clone, source-language package manager, or framework installer only. Appropriate when the audience is comfortable with native runtime installs and the server has no system deps that Docker would help with.

## Build and packaging tooling

Build backends, lockfiles, and version-manager conventions for the language ecosystem.

### hatchling + uv

Build backend `hatchling.build`, lockfile `uv.lock`, install via `uv pip install` or `uvx`. The dominant modern Python pattern. Often paired with src-layout (`src/<package>/`).

### Optional-dependency fan-out

Python projects expose multiple optional-dependency groups so users install only the slices they need. Patterns range from a single `[dev]` extra to a domain-driven fan-out of one extra per upstream library (e.g., per-GIS-library extras with an `all` composer). Appropriate when the project's dependency surface is large and heterogeneous; lets the install footprint match the use case.

### Bare script (no build)

Single-file `.py` server with no `pyproject.toml` build backend, optionally with `uv sync` against ad-hoc dependency declarations. Appropriate for personal tools.

### Pin discipline

Discipline for framework version pins varies meaningfully: narrow-range pins (`>=2.7.0,<2.11`) explicitly guard against minor-release breakage; exact pins (`fastmcp == 2.13.1`) prioritize reproducibility over upgrade speed; loose pins (`>=1.0.0`) appear in minimal-ceremony servers. Choice signals the author's tolerance for upstream churn.

## System-level dependencies

External binaries the host must install before the server can run.

### Self-contained (registry-only)

Server's runtime dependencies all install via the package manager — no out-of-band system tools required. Pure language ecosystem (`npm install` / `pip install` / `go get` / Gradle resolution). The default expectation; appropriate when domain libraries are pure-Python or include their own bundled binaries (PyMuPDF, sqlite3 wheels), or when the wrapped functionality is itself implementable in the host language.

### System binary required (CLI on PATH)

Server depends on a host-level binary (Tesseract OCR, GDAL, ffmpeg, system tool) that the package manager cannot install. README surfaces the install responsibility on the user (`apt-get install ffmpeg` for CI). Docker becomes the only self-contained distribution path. Appropriate when no Python wheel or Node module wraps the underlying tool and reimplementing the mature CLI would be foolish; trade-off is friction against bundling complexity.

### Browser runtime (Playwright)

Server depends on a browser binary that Playwright fetches as part of its install step. Multi-GB install footprint; container distribution becomes significantly more attractive than pip/npm.

## Observability

How the server emits operational signal. Splits between agent-facing logs (visible in MCP client) and ops-facing logs (disk/stdout/external systems).

### Stderr logging (convention / SDK default)

Most servers log to stderr by default — implicit in stdio transport since stdout is the protocol channel. Format and levels are typically not documented. The host captures stderr if it cares. Appropriate as the default; explicit only when the project deviates.

### Suppressed progress output

Stdio servers explicitly suppress progress messages to keep stdout clean of non-protocol bytes. A documented design concern in some projects. Appropriate (in fact required) for any stdio server.

### Pluggable logger sinks

Server picks logger destinations from a list (`disk`, `mcp`, `stderr`) controlled by env var (`LOGGERS`). `mcp` sink emits log entries to the connected client. Appropriate when the operator wants to choose between agent-visible and ops-visible logs per deployment.

### File-system artifacts as side effects

The server writes logs and outputs to local directories (`./logs/`, `./charts/`) and returns paths to the caller rather than data. Doubles as observability (the operator inspects the files post-hoc). Appropriate when outputs are large binary artifacts that don't fit in tool responses anyway.

### Rotating JSON audit log on disk

Structured JSON log file with rotation (e.g., 50 MB, 5 backups) at a known location (`~/.cve-mcp/audit.log`). Fields include timestamp, tool name, parameters, duration, cache-hit status. API keys and response payloads explicitly redacted. Appropriate for security-sensitive servers where audit trail is itself a deliverable.

### Audit logging for compliance modes

Logger captures security events explicitly tied to compliance regimes (GDPR, HIPAA modes). Appropriate when the server claims compliance posture and needs to demonstrate audit retention.

### Winston-based logging

Node-ecosystem structured-logging library configured at hosting layer with configurable levels. Appropriate for Node/Next.js hosted services.

### Sentry integration

Errors forwarded to Sentry for centralized triage. Appropriate for hosted services with on-call teams.

### Health endpoint sidecar

Optional separate monitoring server exposing health endpoints (HTTP transport only). Appropriate when the deployment runs behind a load balancer that needs liveness probes.

### Request lifecycle hooks for telemetry

The SDK exposes hooks at request-start, request-complete, error so applications can wire OpenTelemetry, metrics, or logging without modifying SDK code. Pairs with recovery middleware that catches handler panics so a single bad tool call doesn't crash the process. Appropriate when the server runs as a long-lived service and the operator needs to observe across requests.

### Change-notification channels

Per-client notification streams for updates to tool/resource/prompt lists, surfaced via the SDK as event channels. Indirectly observable but primarily a feature for reactive client UIs. Appropriate when the underlying domain emits changes the client should re-render against.

### Not documented

Most projects do not document logging destination, format, metrics, or tracing. Operators are left to infer from runtime behavior. A widespread gap; not so much a chosen path as an absent one.

## Repository layout

How the project organizes its source tree. Constrains contribution patterns and what can be released independently.

### Single-package src-layout

`src/<package>/`, `tests/`, optionally `examples/`, `docs/`, `agents/`, `.github/`. The modern Python default and the FastMCP reference shape. Appropriate for servers with a single distributable package.

### Single-package source (language-conventional)

One module/package in conventional language layout (Go: `cmd/`, `pkg/`, `internal/`, `build/`, `docs/`; TypeScript: `app/`, `src/`; npm: `package.json`, `bin/`, optional `dist/`). The simplest organization. Appropriate when one server is one product.

### Single-package, organized subdirectories

One package manifest, code split into purpose-named subdirectories (`src/`, `core/`, `client/`, `server/`, `transport/`, `examples/`, `e2e/`). Appropriate when the codebase is one shipping unit but internally segregated by concern.

### Single-package with auxiliary folders

One top-level package directory plus siblings for tests, deploy artifacts, scripts, custom lint rules, API docs. Appropriate when the project is one server but has substantial supporting infrastructure.

### Single-file script / monolith

The entire server is one `.py` (or `.js`, etc.) file, sometimes very large (e.g., ~112 KB), with a `requirements.txt` or no manifest. The minimum viable layout. Appropriate when the server's surface is small enough that splitting adds no value, for prototypes, and for projects optimizing for "one file to read"; trades off against modular testability.

### Monorepo (workspace)

Multiple packages under a workspace tool (pnpm + Turbo, similar). Server, clients, evals, plugin wrappers, and docs as sibling packages. Appropriate when the product spans multiple deliverables that share build infra.

### Monorepo with per-server subdirectories

Repo root holds shared tooling; each server lives in `src/<name>/` (or `servers/<name>/`) with its own manifest, Dockerfile, and README. Different servers may use different languages side by side (TS + Python peers). Appropriate when the repo is a curated reference set or a vendor's portfolio of related servers.

### Monorepo with per-server subdirectories and one PyPI package

`servers/<server-name>/` subdirectories each with their own README and `pyproject.toml`, but the root publishes one PyPI package that dispatches to children via Hatch `force-include`. Appropriate for thematically-linked server collections (scientific computing) where users want one install entry but author wants per-server isolation.

### Gradle multi-module / Maven multi-artifact monorepo

Repo holds multiple build modules (`kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, umbrella artifact, plus `samples/`, `integration-test/`, `conformance-test/`, `buildSrc/`). Appropriate when the SDK ships multiple consumable artifacts but shares a build pipeline.

### Cross-language monorepo / mixed-language layout

One repo holds first-class peers in different language stacks, each with its own packaging, distribution channel, and Docker image — for example, a primary-language source tree (Python under `src/`) alongside a parallel subproject in another language for editor integration (TypeScript under `vscode-extension/`). Appropriate when the project is a reference set demonstrating multiple SDKs against one spec, or when one product needs both an MCP surface and a native editor extension surface.

### Polylith components

Clojure's Polylith style — `bases/`, `components/`, `projects/` separating reusable components from project-specific bases. Heavyweight modular architecture. Appropriate when components are genuinely reused across multiple deliverables.

### Hosted-service layout (Next.js app + mcp-src + lib)

Top-level Next.js `landing/` (or app/), `mcp-src/` for tool/handler logic, `lib/` for shared OAuth/config helpers, `tests/` for stratified suites, `.claude/skills/` for Claude Code integration. Appropriate when the deliverable is a hosted service rather than a published package.

## Safety and security posture

How the project constrains potentially-dangerous operations and defends against threats. Distinct from authentication; this is about what can be done once authenticated and what defensive measures the server applies.

### Read-only by default with explicit write flag

Write operations are gated behind a `--write-access` (or `--read-only` inverse) flag. The default is the safer mode. Conservative posture; rare among MCP servers, which more commonly ship full capabilities unconditionally. Appropriate when the upstream is mutation-capable (issue trackers, source control) and accidental writes are damaging.

### Per-tool auto-approve gating

Operators mark specific tools as safe to run without per-call confirmation, leaving the rest gated. Granular trust boundary at the tool level. Appropriate when the tool catalog mixes safe and dangerous operations and the operator wants asymmetric trust.

### Lockdown / content-filter mode

A flag that filters content from public/untrusted upstream resources before returning it to the agent. Layered over tool selection — operates regardless of which tools are enabled. Appropriate when the agent will traverse untrusted content and the project wants a safety envelope on what reaches the model.

### Tool-layer query validation

The server validates inputs at the tool layer (e.g., SELECT-only enforcement, row-count caps) rather than relying on database-level controls. Defense in depth. Appropriate when the upstream is a general-purpose data store that the project wants to constrain to a safer subset.

### No sandbox; explicit non-security stance

The README states the server is "not a security boundary" and provides escape hatches (`--allow-unrestricted-file-access`) rather than enforcement. Appropriate when the threat model assumes a trusted caller and the operator opts in to risky modes deliberately.

### Blacklist-filtered code execution

The server accepts user-submitted code (e.g., pandas expressions) and filters dangerous operations via a string-level denylist. Resource accounting via `psutil`. A known-fragile approach acknowledged as such; the alternative (process isolation, restricted exec) is not used. Appropriate when the convenience of in-process execution outweighs the risk of denylist gaps.

### Capability-scoped tool exposure

Risky tool families (filesystem write, vision-coordinate clicks, PDF generation) are gated behind `--caps=<group>` opt-in. The server runs without them by default. Appropriate when one server image needs to serve both restricted and unrestricted use cases without forking.

### Path/repo allowlist as access control

The server accepts a directory or repository path at launch and refuses operations outside it. No identity check, just scope clamping. Appropriate when the only meaningful restriction is "what subtree can be touched."

### MCP Roots-driven scope

Same allowlist idea but the scope comes from the host via MCP Roots messages, refreshable at runtime. Appropriate when the host is itself authoritative about user intent (open project, current workspace).

### defusedxml for XML hardening

Library swapped in for stdlib XML parsing to defend against XML bomb / XXE attacks. Appropriate when the server consumes XML from untrusted upstreams (security feeds, public APIs).

### Temporary-user lifecycle with TTL

Server auto-provisions short-lived database users on every connection (default 4-hour TTL) instead of using a long-lived credential. Appropriate when the upstream supports user provisioning via API and the deployment wants minimal blast radius per session.

### Auto-cleanup of temporary export artifacts

Server emits resources holding exported data and deletes them after a TTL (default 5 minutes). Appropriate when the server produces transient artifacts that shouldn't accumulate.

### Dry-run config dump

`--dryRun` flag prints resolved config and exits without booting the server. Appropriate for verifying environment-merge behavior across env / CLI / file sources before committing to a long-running process.

### Index-scan rejection

`--indexCheck` flag rejects database queries that would scan without an index. Appropriate as an unusual safety posture against agent-induced load on production databases.

### Migration prepare/commit pattern

Server exposes `prepare_migration` and `complete_migration` tools so agents can stage schema changes for human review before execution. Appropriate when the upstream supports branching (Neon-style) and humans should be the apply-step authority.

### None / not surfaced

Many projects ship full capabilities unconditionally. Appropriate when the upstream is read-only or the tool surface is genuinely safe.

## Embedded LLM invocation

Whether the server itself calls an LLM internally as part of fulfilling tool calls. Distinct from the host's invocations.

### In-server LLM client

The server holds API credentials for an LLM provider (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) and an env var (`EMBEDDED_AGENT_PROVIDER`) selecting the provider. Tool implementations can invoke the LLM internally for aggregation or summarization. Unusual — most MCP servers are pure tool-callers. Appropriate when post-processing of upstream data into LLM-friendly form is itself an LLM-shaped task.

### Visualization synthesis

The server generates images (charts, maps) for the calling LLM to interpret rather than returning raw data. Transforms data-fetch tools into visualization-aware tools. Appropriate when the data is more useful to the model as an image than as numbers.

### None (pure tool-caller)

The server only calls upstream services and passes results back. The standard pattern. Appropriate as the default.

## Deployment topology

The shape of where the server actually runs in production. Cuts across distribution + transport but is its own concern.

### Local stdio process per session

The server runs as a child process of the MCP host on the user's machine, one process per host session. Standard for stdio servers. Appropriate for single-user, local-data, or per-user-credentialed workloads.

### Hosted SaaS endpoint

The maintainer operates a single (or replicated) deployment users connect to. No install on the user side. Often co-exists with a local stdio mode for self-hosted variants. Appropriate when the upstream resource is shared (public data, cloud APIs the maintainer brokers) or when zero-install ergonomics are decisive.

### Edge / serverless deployment

The hosted SaaS runs on a serverless edge platform (Cloudflare Workers) rather than a long-lived server. Constrains the runtime model — no persistent in-memory state, request-scoped execution. Appropriate when the workload fits the edge runtime's constraints and global low-latency distribution matters.

### Self-hosted HTTP server

Operators deploy the same code as a long-running HTTP service inside their own infrastructure. Same code as the SaaS variant in some products. Appropriate when the operator wants the deployment topology of a SaaS but inside their own perimeter.

## Caching and rate-limiting infrastructure

Cross-cutting modules inside the server that aren't tools but mediate how tools interact with upstreams.

### SQLite TTL cache

In-process SQLite database holds per-call cached responses with TTL. Cache-hit status surfaces in audit log. Appropriate when upstream APIs have rate limits or latency that warrant caching, and when the cache should survive process restarts.

### Token-bucket rate limiter

Explicit rate-limiter module for upstream throttling (e.g., NVD's published quota). Appropriate when one upstream's quota is the binding constraint and naive request fan-out would exhaust it.

### Circuit breaker for external calls

Circuit-breaker pattern wrapping external API calls so a degraded upstream doesn't cascade into server failure. Appropriate when the server has many upstreams and partial degradation is acceptable.

## Documentation surfaces

How the project communicates intent and operational details to users, developers, and AI consumers. Influences whether the README alone suffices or whether sibling docs are required.

### README-only

Single README covers install, usage, host integrations, configuration. Appropriate when the project is small enough that one document scales.

### Split USER_GUIDE / DEVELOPER_GUIDE

Two sibling markdown files separate end-user concerns from contributor concerns. Appropriate for project-governed servers (vendor or org) where each audience has substantially different needs.

### Per-subserver README in monorepo

Each child server has its own README in its subdirectory. Appropriate for monorepos with thematically-distinct children that need independent operational documentation.

### CITATION.cff

Machine-readable citation metadata for academic publication. Appropriate when the project is published or referenced in academic literature.

### GitHub Pages site

Discovery-oriented site (`mcp.science`, `<project>.github.io`) that surfaces the project to users searching outside GitHub. Appropriate for projects targeting a user base that doesn't browse GitHub directly.

### `llms.txt` / `llms-full.txt`

Curated context summaries shipped at repo root for LLM ingestion — a "vibe coding" surface beyond the MCP protocol itself. The two-file pattern (`llms.txt` for digestible summary, `llms-full.txt` for complete reference) is emerging convention. Appropriate when the server's surface is large enough that the LLM benefits from a guided overview before reaching for individual tool descriptions.

### Bundled `cursor_rules.md` / AI-guidance content

A markdown file shipped alongside the server with rules or guidance the LLM should follow when using it. Neither MCP tool nor MCP prompt — just bundled context the host's LLM is expected to read. Appropriate when the server's correct usage requires conventions the per-tool descriptions cannot fully convey.

### `agents/` example directory

Runnable example clients demonstrating how an agent should drive the server. Appropriate when authorship benefits from concrete invocation patterns rather than abstract protocol description.

## Agent-facing meta-documentation

Documentation inside the repo that targets agents working in the repo, not human users.

### `CLAUDE.md` shipped with the server

Repo includes a `CLAUDE.md` at root providing Claude-specific guidance for working in the codebase itself. Distinct from a user-facing README; the audience is an agent contributing to the repo. Appropriate when maintainers want consistent agent behavior across contributors using Claude.

### `.cursorrules` for Cursor IDE

Equivalent for Cursor — repo-local instructions an AI editor reads when assisting in the codebase. Appropriate when the maintainer's IDE workflow involves Cursor and wants in-repo context steering.

### `.mcp.json` at repo root

Declares MCP servers the repo itself wants its agents to have available. Distinct from the server being authored — it's the dev environment's MCP wiring. Appropriate when developers iterating on the server need other MCP servers (filesystem, git, etc.) available during their work.

## Claude Code plugin / skill wrapper

Whether the server ships an in-tree Claude Code skill or plugin definition. Distinguishes "MCP server only" from "MCP server + first-class Claude Code integration."

### Bare MCP server, no Claude Code wrapper

Server ships only the MCP surface; users wire it via `claude mcp add` or JSON config. Most common path.

### `.claude/skills/` directory in repo

Repo contains Claude Code skill definitions alongside the MCP server source. Skills wrap the MCP tool surface in Claude Code workflow patterns. Appropriate when the vendor wants the server discoverable via Claude Code skills, not just as a raw MCP endpoint.

### `claude-code/` directory with skill files

Sibling top-level directory carries Claude Code skill files; the README documents skill-file installation alongside MCP server installation. Appropriate as an explicit "first-class Claude Code support" signal beyond raw skill definition placement.

### `.claude-plugin` wrapper

Server ships a Claude plugin manifest with dedicated CLI commands. Appropriate when the team wants Claude Code's plugin install/update lifecycle to govern the server's lifecycle.

## Developer ergonomics

Affordances for users building on the SDK or iterating on the server.

### Examples directory with many patterns

`examples/` with 20+ runnable patterns covering the full surface — client, server, HTTP, SSE, OAuth, roots, sampling, structured tools, tasks. Appropriate for SDKs where adoption hinges on showing how each primitive lands in real code.

### Programmatic embedding API

A first-class `createConnection()` or equivalent that lets host processes embed the server as a library. Appropriate when the consumer base includes app developers, not just operators wiring subprocess installs.

### Sample implementations directory

`samples/` directory with end-to-end mini-apps demonstrating different transports/configurations. Same idea as examples but framed as "complete miniature apps." Appropriate for SDKs where the unit of teaching is a working program rather than a snippet.

### Inspector/debug tooling references

README points to MCP Inspector or similar debuggers for poking at the running server. Appropriate when the maintainer wants to nudge operators toward the canonical debug workflow.

## Release engineering

How versions get cut.

### GitHub Actions release workflow

`release.yml` triggers on tag push, runs build + test + publish. Sometimes paired with a dedicated `pages.yml` for docs site builds. Appropriate when releases need to fan out to multiple registries (npm + Docker, PyPI + Docker).

### Manual via package manager

The maintainer runs `npm publish`, `uv publish`, or equivalent locally. Appropriate for low-frequency releases where automation overhead exceeds the savings.

### Dual-license relicensing gate

Existing code stays under the original license (MIT); new contributions land under a different license (Apache-2.0). The release process enforces the contributor agreement. Appropriate as a forward migration mechanism without rewriting prior commits.

## License

Licensing posture of the published server.

### Permissive (MIT / Apache-2.0)

The dominant pattern — MIT for most, Apache-2.0 for FastMCP. Maximizes adoption; no commercial restriction.

### Copyleft / non-commercial (CC BY-NC-SA)

Rare in MCP ecosystem; appears as a deliberate restriction against commercial adoption. Trade-off: signals author's intent but limits downstream reuse in commercial settings. Appropriate when the author wants to retain commercial control over derivatives.
