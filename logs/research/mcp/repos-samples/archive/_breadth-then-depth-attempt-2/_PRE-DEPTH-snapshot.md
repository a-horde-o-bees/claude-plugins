# Sample

Canonical merge of three stage-1 partials (`_CONSOLIDATED_pass1-merge-stage1-a.md`, `_CONSOLIDATED_pass1-merge-stage1-b.md`, `_CONSOLIDATED_pass1-merge-stage1-c.md`) into the unified Pass 1 consolidated. Functional roles with implementation paths and qualitative descriptions; no inline citations (provenance via `ocd-run log research references "Sample > <chain>" --subject mcp`). See `_METHODOLOGY_breadth-then-depth.md` for process details.

## Server runtime

The language and SDK substrate the MCP protocol loop executes on. Constrains downstream choices: which transports are natural, which packaging conventions apply, what the async model looks like, how tool schemas get derived, what dependency surface is required, and which distribution channels reach the user.

<!-- adoption-table -->

Adoption — 104 samples exhibit `Sample > Server runtime`.

| Path                                            | Count | Coverage |
| ----------------------------------------------- | ----: | -------: |
| Python with raw MCP SDK                         |    29 |     28% |
| Python with FastMCP                             |    23 |     22% |
| Node.js / TypeScript with official MCP SDK      |    21 |     20% |
| Python with both MCP SDK and FastMCP declared   |     6 |      6% |
| Go with custom MCP implementation               |     4 |      4% |
| Rust with rmcp / rust-mcp-sdk                   |     4 |      4% |
| Python with hand-rolled MCP                     |     3 |      3% |
| Go with mark3labs/mcp-go SDK                    |     2 |      2% |
| Remote HTTP service (no local runtime)          |     2 |      2% |
| TypeScript on Cloudflare Workers (V8 isolate)   |     2 |      2% |
| .NET / C#                                       |     1 |      1% |
| Clojure with hand-rolled MCP and minimal deps   |     1 |      1% |
| Clojure with nREPL bridge                       |     1 |      1% |
| DuckDB extension (C++) embedding MCP            |     1 |      1% |
| Go with metoro-io/mcp-golang or alternative SDK |     1 |      1% |
| Kotlin Multiplatform SDK                        |     1 |      1% |
| Next.js (TypeScript) as MCP host                |     1 |      1% |
| Node.js with custom SDK composition             |     1 |      1% |
| Python with Anthropic Claude Agent SDK          |     1 |      1% |
| Python with FastMCP (pre-2.x era)               |     1 |      1% |
| TypeScript on Bun                               |     1 |      1% |
| TypeScript on Node with monorepo tooling        |     1 |      1% |

<!-- /adoption-table -->
### Python with FastMCP

Python server built on the FastMCP decorator framework — the higher-level wrapper over Anthropic's `mcp` SDK. `@mcp.tool` / `@mcp.resource` / `@mcp.prompt` declare capabilities; FastMCP auto-derives JSON Schema from typed function signatures via Pydantic 2 and dispatches both `def` and `async def` handlers. The framework ships its own HTTP transport stack (uvicorn, starlette, websockets, authlib, python-multipart) so consumers do not assemble it; compatible with stdio, HTTP, and SSE transports out of the box. Two major lines coexist: an older 1.x style imported as `from mcp.server.fastmcp import FastMCP` (bundled with the `mcp[cli]` extra), and a newer 2.x line imported as `from fastmcp import FastMCP` published as a separate `fastmcp` package. Pin discipline varies sharply: tight pins (`fastmcp == 2.7.0` / `>=3.1.0,<4`) track API drift in the still-evolving 2.x line, narrow ranges (`>=2.7.0,<2.11`) guard against minor-release breakage, exact pins prioritize reproducibility, loose pins (`>=1.0.0`) appear in minimal-ceremony servers. A `fastmcp.json` may sit alongside pyproject and a FastMCP-specific log-level convention (`FASTMCP_LOG_LEVEL`) is observed. Authors gravitate to it when the tool catalog is hand-authored, when ceremony around each tool function should be minimal, and when authoring effort scales with tool count rather than with framework boilerplate.

### Python with FastMCP (pre-2.x era)

Single-file Python script using FastMCP 1.x decorators. Tool signatures derive from type hints; the FastMCP CLI installer (`fastmcp install`) is the install mechanism rather than pip. Predates the modern `pyproject.toml`-centric layout — `requirements.txt` pins FastMCP (e.g., `fastmcp==0.4.1`) and the script is the package. Often co-occurs with *Build and packaging — Requirements-driven (legacy Python)* and *Repository layout — Single-file script / monolith* as a coherent "early FastMCP" cluster predating package-restructuring conventions. Appropriate when the goal is the smallest possible single-file MCP server and the author is comfortable being pinned to FastMCP's CLI conventions.

### Python with raw MCP SDK

Direct use of Anthropic's `mcp` Python SDK (`mcp` / `mcp[cli]`) without a higher-level framework wrapper. The author works against `mcp.server` primitives — tool handlers and schemas are hand-authored rather than auto-derived, and protocol framing is explicit. Pin discipline varies widely from exact (`mcp[cli]==1.6.0`) to very loose (`mcp>=0.1.0`); the `[cli]` extra adds inspector tooling. Surfaces both as the modern `mcp[cli]>=1.4.1` and as legacy pre-1.0 `mcp-server>=0.1.0` referenced in `setup.py`-era projects. Pydantic models commonly carry structured payloads (sometimes hand-registered, sometimes auto-derived). Authors who pick this layer typically wrap their own CLI with `click`, validate config with `pydantic-settings`, and use `rich` for non-protocol output — the framework gap is filled à la carte; module-level entry (`python -m package.server`) is common rather than a console script. Appropriate when the project predates FastMCP, when the server has a small fixed tool surface, when dependency minimalism matters (lean dep sets of 3-4 packages observed), when access-mode gating or fine-grained tool dispatch needs custom hooks the FastMCP layer hides, when wrapping a sync-only third-party library where FastMCP's async-first ergonomics add no value, or when the project has very wide tool surfaces (60+ tools) demanding custom dispatch. Tool handlers are typically `async def` since the low-level SDK is async-native, but sync handlers also occur when the underlying client library is sync.

### Python with both MCP SDK and FastMCP declared

Hybrid path where `pyproject.toml` lists both `mcp` (or `mcp[cli]`) and `fastmcp` as dependencies (e.g., `mcp>=1.8.0,<2.0.0` and `fastmcp>=2.13.0,<2.15.0`). Typically FastMCP runs the server surface while `mcp[cli]` provides developer tooling (Inspector launcher, schema dump utilities), or transitional state during a migration — projects that predate FastMCP and migrated partially, or where some lower-level capabilities only exist in the raw SDK. Pins both with bounded version ranges to control compatibility. Carries dual-import risk and larger dependency footprint but enables incremental migration.

### Python with Anthropic Claude Agent SDK

Python runtime that pairs the Claude Agent SDK with MCP — a less common path where the agent SDK is the foundation and MCP capabilities are layered on top. Appropriate when the project blurs agent and MCP-server roles or wants to reuse Claude Agent abstractions. Pulls in a heavier dependency surface than plain MCP.

### Python with hand-rolled MCP

Python server with no MCP framework dependency at all — the JSON-RPC stdio loop or HTTP request/response handling is implemented per server. Surfaces in monorepos where the MCP layer is thin (e.g., subprocess-wrapping a CLI tool), in serverless deployments where the SDK's process-loop assumptions don't fit (Lambda + API Gateway events bridge MCP framing onto HTTP event JSON), or when dependency footprint must be minimal (3-package surfaces observed: `python-dateutil`, `boto3`, `botocore`). Decorator-style ergonomics (`@mcp.tool()`) can be reproduced atop the custom implementation. Constrains the server to re-implement message framing, capability negotiation, and tool dispatch independently — trades SDK reuse for substrate fit.

### Node.js / TypeScript with official MCP SDK

TypeScript or JavaScript server built on `@modelcontextprotocol/sdk` (commonly `^1.x`), authored in TypeScript and compiled to a `build/` or `dist/` JS output via tsup, esbuild, or tsx. Distribution flows naturally over npm with a `bin` entry making `npx -y <package>` a one-liner host-config command. The SDK exposes both `StdioServerTransport` and `StreamableHTTPServerTransport` classes the server instantiates based on a launch subcommand or flag, and bundles its own HTTP and stdio transport plumbing — runtime choice doesn't pull in a separate web framework, though Hono and Express frequently appear for the HTTP layer. Standard modern-TS scaffolding pairs it with pnpm, ESLint, Prettier, vitest, Zod for env/config validation, and Pino for structured logging. Capability surface registered programmatically per-tool in code, or — less commonly — via a sidecar declarative manifest such as `tools.json`. Schema definition is hand-authored in TypeScript or auto-derived from OpenAPI when openapi-client-axios is in play. Imposes a Node version floor (typically 18+ or 20+). Appropriate for thin database/local-resource adapters, when the upstream library being wrapped is itself JS/TS (Playwright, exa-js, Supabase, libSQL, discord.js, Puppeteer, Docker Hub API), keeping the stack uniform, when hosts run a Node process directly via `npx`, when distribution needs to land in npm-only host environments, or when an HTTP transport with browser-style concerns (CORS) is in scope.

### Node.js with custom SDK composition

JavaScript/Node server combining the MCP SDK with vendor-specific SDKs (e.g., the Anthropic Claude Agent SDK) rather than using the MCP SDK alone. The compositional choice surfaces when the server is itself an agent-like layer that must call out to LLM APIs while exposing MCP tools, and the second SDK does work the MCP SDK does not.

### TypeScript on Node with monorepo tooling

A TypeScript codebase organized as a pnpm workspace + Turbo monorepo. Same code targets both an npm-distributable stdio binary (`npx @scope/server`) and a hosted HTTP service. Permits multiple packages (server, client, evals, plugin wrapper) under one repo. Appropriate when one logical product spans server + clients + first-party plugin wrappers and the author wants shared build/CI across them.

### TypeScript on Bun

Same TypeScript codebase auto-detects and runs under Bun (`>=1.2`) when the runtime is Bun, otherwise falls back to Node. Bun is invoked via `bunx`. Appropriate when the project wants Bun's startup-time and footprint advantages without forcing it on users. The dual-runtime path requires the project to avoid Node-only or Bun-only APIs and to test both runtimes in CI.

### TypeScript on Cloudflare Workers (V8 isolate)

Not Node — the server runs as a Cloudflare Worker in a V8 isolate runtime, deployed via Wrangler. The same TypeScript MCP SDK is used, but the surrounding stack (Workers Bindings, KV, Durable Objects) replaces Node primitives. Sometimes paired with React Router 7 + Vite for a co-resident web frontend. The server is the deployment, not the artifact — there is no binary or package users run. Appropriate for hosted/remote-only deployments where the author also operates the runtime; the goal is a zero-install hosted MCP service with global edge distribution. Constrains transport to HTTP-only (Workers don't speak stdio), constrains authentication to per-request bearer tokens (no env-var credentials available to a stateless worker), and constrains distribution to "remote URL" rather than "installable package."

### Next.js (TypeScript) as MCP host

A Next.js App Router application that embeds the MCP server alongside a marketing landing page, OAuth UI, and HTTP API endpoints. Tool/handler logic lives in a `mcp-src/` module called from API routes. Appropriate when the deployment is a remote hosted service rather than a local stdio process — Next.js provides routing, deployment integration (Vercel), and a unified surface for OAuth flows + the MCP endpoint + a public landing page. Constrains transport to HTTP-based variants and assumes a hosted-service model.

### Go with mark3labs/mcp-go SDK

A Go binary linked against the community `mcp-go` SDK. Native Go structs become tool arguments with automatic JSON-Schema generation; transport selection is a separate entry method (`server.ServeStdio`, `server.ServeSSE`, `server.ServeHTTP`) or registration into a higher-level web framework (Gin). Single-binary build artifact suits cross-platform release-and-download distribution and Docker packaging without language-runtime prerequisites on the host. Stdio is the natural transport for `serve`-style subcommands; Go modules act as the dependency boundary. Appropriate when single-binary deployment, performance, type-safe schemas without runtime reflection cost, and goroutine-based concurrency for streaming or task-augmented tools matter.

### Go with metoro-io/mcp-golang or alternative SDK

A Go program that imports an alternative third-party MCP SDK module (e.g., `github.com/metoro-io/mcp-golang`) and registers tools/resources/prompts via constructor and method calls. Same single-binary distribution profile and concurrency model as the mark3labs path; the SDK choice differs. Appropriate when the consumer prefers the alternative SDK's API ergonomics or transport mix.

### Go with custom MCP implementation

A Go server that hand-rolls protocol handling without depending on a third-party MCP SDK and ships a `server.json` to declare MCP capability metadata. Yields a single static binary suitable for direct distribution or Docker base-image minimization, supports stdio/SSE/HTTP from one build, and provides explicit control over TLS, custom User-Agent, and other enterprise-environment portability concerns. Some projects expose a functional-options API (`WithStreamableURI`, `WithSSEURI`, `WithSSEMessageURI`, `WithRootRedirect`), separate `client.go`/`server.go` packages, and an out-of-process bridge binary for non-Go consumers — including built-in OAuth2/OIDC support that most Python/TypeScript SDKs delegate to the host. Used as an SDK/framework target where consumers can either embed the library or run a packaged executable. Appropriate at scale (large official servers) where custom toolset gating, dynamic capability registration, or hosted-mode integration motivate owning the protocol layer rather than tracking an upstream SDK.

### Rust with rmcp / rust-mcp-sdk

Cargo-managed Rust crate exposing both library APIs and CLI binaries, atop the Tokio async runtime. Two distinct ecosystem patterns surface: an `rmcp`-based stack with `axum` providing HTTP transport (chosen for performance and memory-safety properties, typically by vendors who already ship Rust internally), and a `rust-mcp-sdk` + `rust-mcp-schema` family compiling to a static binary with no external runtime dependencies. Generic-adapter shapes also exist that turn external schema (GraphQL operation definitions) into MCP tools at runtime. Server scaffolding sometimes uses a builder pattern (`ServerConfig::with_name().with_version().with_tool()`) and exposes a project-scaffold generator (`mcpr generate-project`) for downstream authors. Pinned to a specific Rust toolchain via `rust-toolchain.toml`; types are compile-time-checked rather than reflected. Distribution flows through crates.io, pre-built GitHub release binaries, npm (native-binary wrapper), Homebrew, and Docker images built from the binary. The single-static-binary build artifact interacts well with container-only distribution but raises the bar for casual contributors and rules out the npx/uvx convenience flows that dominate JS/Python ecosystems. Appropriate when performance matters (filesystem operations at scale), when zero runtime dependencies are a deployment requirement, or when the author wants a static native binary.

### .NET / C#

C# MCP server compiled to a .NET binary. Surfaces in vendor-authored servers where the rest of the org's tooling and developer ecosystem is .NET-centric (Visual Studio, NuGet). Distribution naturally flows to NuGet packages and, secondarily, to Docker images and IDE-extension marketplaces. The runtime choice ties the server to host platforms where .NET is a first-class citizen.

### Clojure with nREPL bridge

Clojure JVM runtime exposing MCP tool calls as nREPL evaluations. The MCP protocol is bridged onto a REPL connection rather than a process-IO transport — tool invocations become forms evaluated in the running REPL. Appropriate when the target ecosystem (Clojure, ClojureScript via Shadow-cljs, Babashka, Basilisp, Scittle) is itself REPL-driven and structure-aware editing requires live access to a running runtime. Constrains the user to start an nREPL process and keep it co-resident; opens the door to multi-environment detection and switching between REPL flavors at runtime.

### Clojure with hand-rolled MCP and minimal deps

A Clojure project against MCP version 2024-11-05 with `org.clojure/data.json` as effectively the only dependency. Polylith-style modular layout (bases, components, projects). Java runtime is required; the JVM warm-up and dependency resolution cost falls on the host launching `clj -M:profile`. Appropriate when the author values a self-contained Clojure REPL evaluation surface and is willing to absorb Polylith's structural overhead in exchange for component reuse across multiple deliverables.

### Kotlin Multiplatform SDK

Kotlin SDK published as Maven artifacts (`io.modelcontextprotocol:kotlin-sdk*`) with multiplatform targets (JVM, Native, JS, Wasm). Coroutine-based APIs throughout; Ktor server is an optional companion for HTTP transports, with engines specified independently to avoid transitive bloat. Appropriate when the consumer needs JVM integration, Android, or browser/Wasm reach with a single SDK surface.

### DuckDB extension (C++) embedding MCP

Native DuckDB extension built with CMake that exposes MCP via SQL PRAGMAs rather than running as a standalone process. The "server" is the user's DuckDB session; tool calls and configuration originate from SQL statements (`PRAGMA mcp_server_start(...)`, `PRAGMA mcp_publish_tool(...)`). Blurs the database/tool-registry boundary — SQL templates become first-class published tools. Constrains distribution to source-build with `make` since DuckDB community-extension packaging may not yet be available.

### Remote HTTP service (no local runtime)

The "runtime" lives on a vendor-hosted endpoint; the GitHub repo carries only client config files and OAuth metadata. There is no local language or framework to choose because nothing executes on the user's machine. Appropriate when the vendor wants centralized control over capability evolution, rate limits, and credential rotation, and is willing to take on the operational cost of hosting.

## Transport

The wire protocol carrying MCP messages between host and server. Constrains deployment shape (in-process subprocess vs networked service), authentication options (no-auth vs bearer/OAuth), tenancy ceiling, and where the server can run.

<!-- adoption-table -->

Adoption — 103 samples exhibit `Sample > Transport`.

| Path                                     | Count | Coverage |
| ---------------------------------------- | ----: | -------: |
| stdio                                    |    90 |     87% |
| Selection mechanism                      |    77 |     75% |
| Streamable HTTP                          |    42 |     41% |
| SSE (Server-Sent Events)                 |    29 |     28% |
| Hosted remote endpoint (vendor-operated) |     7 |      7% |
| Custom or experimental transports        |     2 |      2% |
| HTTP with JSON response mode             |     2 |      2% |
| In-memory / in-process channel           |     2 |      2% |
| REST API bridge alongside MCP            |     2 |      2% |
| HTTP via API Gateway in front of Lambda  |     1 |      1% |
| MCP-client mode (server connects out)    |     1 |      1% |
| SFTP / SSH for remote resource access    |     1 |      1% |
| Stdio-to-HTTP shim on the client side    |     1 |      1% |
| WebSocket                                |     1 |      1% |
| nREPL connection                         |     1 |      1% |
| CLI dispatcher to per-server stdio       |     0 |      0% |

<!-- /adoption-table -->
### stdio

JSON-RPC over the server process's stdin/stdout, with the host launching the server as a subprocess and communicating over its pipes. Default and most-common path across runtimes — Python, Node, .NET, Docker-containerized servers all converge here. Implies single-tenant by construction (one process, one user/session), no in-protocol authentication on the wire (the host's process boundary is the trust boundary; servers inherit credentials from the host's environment), single-host (the launching app), and host-driven lifecycle. Forces strict discipline on stdout/stderr separation: any stray `print` corrupts the JSON-RPC stream, so servers either suppress prints in core handlers or route logs to stderr only — and file-based logs (e.g., `~/<server>.log`) are a common consequence. Often the only transport offered by simpler servers, and always the fallback when authors offer multiple. Often selected implicitly — README shows the launch command without naming the transport. Appropriate for desktop assistants (Claude Desktop, Cursor, VS Code) where the host owns the process lifecycle. Works equally well when the server is wrapped in a Docker container (`docker run -i`).

### Streamable HTTP

Long-running HTTP endpoint (commonly `/mcp`, optionally `/health`) supporting both request/response and streamed responses with stateful sessions; the current preferred network transport in the MCP spec. Typically built with Hono on Node, with the Workers runtime, with axum on Rust, with Starlette or FastAPI + uvicorn on Python, or with Go stdlib `net/http` or the Gin web framework on Go. Selected via env var (`<NAME>_TRANSPORT=http`), CLI flag (`--transport http`, `--port <n>`), or by binding to an HTTP entry method on the SDK; binds host/port (typical defaults `0.0.0.0:8000`, 5000, 9010, 9887, 13080). Often paired with stateless-mode flags so the same HTTP endpoint can be deployed behind a load balancer for shared multi-user use. Requires the server to bind a port and brings HTTP-stack concerns into scope: CORS origin configuration, host/port env vars, and (where chosen) bearer-token or OAuth authentication on top. Lets the server run remotely, serve multiple concurrent clients, and front an OAuth/JWT flow. Required for hosted SaaS services, browser-reachable clients, and OAuth flows where redirect targets need a reachable endpoint. Often paired with stdio for the same product — same code targets both modes, with the deployment target choosing. Frequently advertised as "coming soon" in stdio-only samples, indicating it is the next-step expansion path most authors anticipate.

### SSE (Server-Sent Events)

Older HTTP-based long-lived stream from server to client (sometimes paired with a separate POST channel for client→server) used as the streaming transport for remote MCP servers. Listed as supported-but-deprecated in newer SDKs, often offered alongside Streamable HTTP for backward compatibility — same Worker or process exposes `/sse` for older clients while `/mcp` serves newer ones. New work selects streamable-HTTP instead; SSE persists where backward compatibility for already-deployed clients matters. Some Rust libraries' SSE paths were yanked due to bugs; some projects document dated removal events (e.g., SSE removal on 2025-05-26) with planned Streamable HTTP replacements. Appropriate when the server emits change notifications (resources/tools/prompts updates) that clients subscribe to, or when host integrations have not yet migrated to streamable HTTP.

### HTTP with JSON response mode

HTTP variant where the server returns a single JSON response per request rather than a stream. Coexists with SSE in some servers as alternative HTTP modes. Appropriate for clients that don't need streaming or for simple request/response tool calls.

### HTTP via API Gateway in front of Lambda

The MCP-over-HTTP endpoint exposed as an API Gateway route that invokes a Lambda handler implementing the protocol. Inherently HTTP, no stdio path. Appropriate when the server must be reachable by remote clients, when serverless cost/scale economics fit the workload, and when authentication can be delegated upstream to API Gateway authorizers. Constrains the server to per-request statelessness (sessions externalized to DynamoDB or similar) and to Lambda response-size limits (streaming responses become a concern).

### Hosted remote endpoint (vendor-operated)

The vendor operates the server at a public URL (e.g., `https://mcp.<vendor>.ai/mcp`, `https://mcp.slack.com/mcp`, `https://mcp.context7.com/mcp`, `gitmcp.io/{owner}/{repo}`) and the host is configured to point at the URL rather than launching anything locally. Eliminates install ceremony and centralizes upgrades on the vendor, but pushes authentication, rate limiting, and tenant scoping fully to the server side. Implies OAuth-style authentication (the server can't trust environment variables that only the user's process would see), per-workspace tenancy, and operator responsibility for uptime and rate limits. Typically paired with API-key or OAuth at the HTTP boundary. Appropriate when the vendor wants to deliver MCP as a hosted service rather than a downloaded artifact.

### WebSocket

Bidirectional persistent connection. Surfaces in Kotlin/Ktor where the SDK exposes a `WebSocketTransport` alongside stdio, SSE, and Streamable HTTP. Appropriate when both sides need symmetric streaming and the host environment already speaks WebSocket (browser clients, in particular).

### nREPL connection

JSON-RPC layered over an nREPL session rather than process IO. The MCP server is itself driven through the REPL protocol. Appropriate only when the target language ecosystem already centers on nREPL; constrains every user to start a REPL.

### In-memory / in-process channel

A non-network transport used inside a single process for testing — server and client share a Kotlin channel, a Go pipe, or an in-process adapter rather than serialize JSON over IPC. Not a deployment option; only relevant in test harnesses and library-mode embedding where the server is part of the host process. Appropriate when the test goal is the server's protocol behavior independent of network/IO concerns. Cross-role: see *Test stack — In-memory transport for protocol tests*.

### Custom or experimental transports

SDKs that expose a transport interface so consumers can plug in their own (e.g., Go SDKs documenting custom transport support and "HTTPS with custom auth, experimental"). Appropriate when the deployment target needs a wire format the SDK doesn't ship.

### REST API bridge alongside MCP

Custom HTTP REST surface (separate from canonical MCP transports) exposed via an additional bridge file (e.g., `vscode_bridge.py`) on a configurable port, or an in-process HTTP server bound to a fixed port (e.g., 8000) running inside the same process as the stdio MCP server. Both protocols serve simultaneously; toggled via env var (e.g., `*_ENABLE_HTTP_BRIDGE`). Non-MCP clients consume the same tool surface through a hand-rolled REST API. Appropriate when the author needs to support clients that don't speak MCP at all, or when an IDE plugin prefers REST. Often implies a custom bridge implementation rather than the SDK's built-in HTTP transport.

### Stdio-to-HTTP shim on the client side

Server speaks Streamable HTTP only; an end-user shim like `mcp-remote` (npm) translates stdio (what the host knows how to spawn) into HTTP requests against the remote URL. The host's MCP config still has a `command`/`args` shape, but the args run the shim and pass it the URL. Lets remote-only servers work with stdio-only hosts. The shim handles auth handshake on the client side; the server never touches stdio. The server author ships zero stdio code and the shim is universally consumed across hosts (each host's `mcpServers` JSON spawns `npx mcp-remote <url>`).

### CLI dispatcher to per-server stdio

Top-level CLI binary takes a server name as a subcommand (`uvx mcp-science <server-name>`) and exec's the named child server, which then speaks stdio MCP. Appropriate for monorepos that ship many independent servers under a single PyPI package — the dispatcher unifies install/discovery while each child server retains canonical stdio semantics.

### MCP-client mode (server connects out)

Inverted role where the same artifact connects out to other MCP servers and exposes them through its own surface. Seen in the DuckDB extension where SQL `ATTACH` semantics let queries span multiple MCP-exposed data sources. Distinct from being a server — this turns the artifact into a federation point.

### SFTP / SSH for remote resource access

Not a protocol transport for MCP itself — the MCP server still speaks stdio/HTTP to the host — but the *data plane* the server reaches operates over SFTP/SSH against a remote filesystem. Brings paramiko (or equivalent) into core deps. Appropriate when target resources (notebooks, files) live on a remote host and the server runs locally near the LLM.

### Selection mechanism

Cross-cutting sub-axis observed across the corpus — how a multi-transport binary chooses which transport to bind:

- **CLI flag at startup** — `--transport stdio|sse|http`, `-t sse`, `--http`, or `--stdio` boolean, with `--port`/`--host`. Explicit, scriptable, surfaces in `--help`. Common in TS, Rust, and Python servers; lowest install ceremony, lets the same artifact serve any host. Often paired with multiple JSON config snippets in the README — one per mode.
- **Environment variable** — `*_MCP_SERVER_TRANSPORT=stdio|http|sse`, `TRANSPORT_MODE`, `MCP_NIXOS_TRANSPORT`. Container-friendly because env vars are the natural Docker/Kubernetes config surface; doesn't require shell-level argument forwarding through wrapper scripts. Often paired with companion env vars for host/port/path/stateless-mode settings.
- **Implicit default** — default to stdio; opt into HTTP by setting `PORT`. Minimal surface for the common case.
- **Separate console scripts per transport** — distinct entry points (e.g., `<server>` for stdio, `<server>-sse` for SSE). Architecturally cleaner separation but installs multiple binaries; appears where SSE/HTTP pulls in a substantial extra dependency surface (Starlette, an HTTP server) the stdio path doesn't need.
- **Functional options (in-code configuration)** — caller assembles the server with composable option functions (`WithStreamableURI()`, `WithSSEURI()`, `WithSSEMessageURI()`) before starting it. Suited to library/SDK projects where the consumer is another program rather than an end user.
- **Separate entry points per transport** — each transport mode is a distinct entry function or binary (e.g., `stdioSrv.ListenAndServe()` vs `srv.HTTP(...).ListenAndServe()`). Forces an explicit choice at code-level rather than runtime configuration.
- **Container ARG/CMD** — Docker entrypoint takes `stdio` or `http` as a positional argument, so the user picks at `docker run` time. Natural when the server is container-only.
- **SQL PRAGMA** — Server mode and transport parameters chosen from SQL inside an embedded extension. Specific to in-database implementations; user issues `PRAGMA mcp_server_start(...)` with transport options as arguments.
- **Profile-driven launcher** — Clojure's `clj -M:profile` mechanism, where `:stdio-server` and `:sse-server` are aliases in `deps.edn` selecting transport mode.
- **Implicit single mode** — server only supports one transport; nothing to select. Forces deployment shape (e.g., HTTP-only when OAuth is the auth model).

## Capability surface

What the server exposes to the LLM — tools, resources, prompts — plus how the catalog is shaped, who authors it, and how operators trim or extend it. Constrains agent capability, host rendering, and operational tuning.

<!-- adoption-table -->

Adoption — 103 samples exhibit `Sample > Capability surface`.

| Path                                                              | Count | Coverage |
| ----------------------------------------------------------------- | ----: | -------: |
| Tools-only, hand-curated narrow surface                           |    30 |     29% |
| Tools-heavy domain wrapper / domain-tool catalog                  |    29 |     28% |
| Domain-bundled tool set                                           |    18 |     17% |
| Capability gating flags (per-tool, per-category, write-mode)      |    13 |     13% |
| Tools plus resources plus prompts (full primitive coverage)       |    10 |     10% |
| Tools plus resources                                              |     6 |      6% |
| Read/write tool split                                             |     5 |      5% |
| Bundled "agent SOPs" / vertical skill packs                       |     3 |      3% |
| Embedded RAG / retrieval pipeline                                 |     3 |      3% |
| Sampling and elicitation as client primitives                     |     3 |      3% |
| Single code-execution tool with sandbox                           |     3 |      3% |
| Spec-driven dynamic tool generation                               |     3 |      3% |
| Tools plus internal "skills" abstraction                          |     3 |      3% |
| Aggregator-tool catalog (many upstreams, normalized tool surface) |     2 |      2% |
| Auto-routing across backends                                      |     2 |      2% |
| Capability gating via tool subsets at install time                |     2 |      2% |
| Library fan-out                                                   |     2 |      2% |
| MCP Roots participation                                           |     2 |      2% |
| REST endpoints alongside MCP tools                                |     2 |      2% |
| Tool catalog as data file                                         |     2 |      2% |
| Tools plus prompts (no resources)                                 |     2 |      2% |
| Tools plus toolset gating (dynamic)                               |     2 |      2% |
| Capability probing and conditional surfacing                      |     1 |      1% |
| Destructive-tool elicitation list                                 |     1 |      1% |
| Partition-scoped tool gating                                      |     1 |      1% |
| Scope-based tool filtering via URL param                          |     1 |      1% |
| Self-reflective analytics tool                                    |     1 |      1% |
| Single generic tool                                               |     1 |      1% |
| Token-economy unified-tool surface                                |     1 |      1% |
| Tool consolidation as design pressure                             |     1 |      1% |
| Tool-count modes (compound vs full)                               |     1 |      1% |
| Tools + prompt routines (out-of-band)                             |     1 |      1% |
| Tools + resources + prompts + UI dashboards                       |     1 |      1% |
| User-publishable tools                                            |     1 |      1% |
| Capability authoring style                                        |     0 |      0% |
| Per-tool output format selection                                  |     0 |      0% |
| Progressive trust gating                                          |     0 |      0% |
| Tools + sampling + prompts                                        |     0 |      0% |
| Vendor-side capability scoping                                    |     0 |      0% |

<!-- /adoption-table -->
### Tools-only, hand-curated narrow surface

Server registers a fixed list of tool functions authored directly in source — one or more tools and nothing else (no resources, prompts, sampling, roots). Dominant pattern across the corpus. The simplest and most common surface: a tool list with input schemas and a single `tools/call` dispatch path. Tool counts vary widely with no clear correlation to project popularity: small handfuls (3-7) for narrowly-scoped servers like translation or search, mid-twenties for task-management or DB servers. Authoring effort scales linearly with tool count. Common rationale: MCP client ecosystem has widespread support for tools but uneven support for resources/prompts, and the project wants every supported client to use every feature without gaps — sometimes a deliberate ecosystem-compatibility decision rather than an oversight, with authors explicitly opting out of resources/prompts citing variable host support. Hand-curated tool surfaces can use URL-template parameterization to keep the tool list small while serving many tenants — the same tool name pattern serves any tenant by virtue of URL routing (e.g., `fetch_<repo-name>_documentation` parameterized from URL path). Constrains client UX — multi-step workflows must be modeled as composable tools rather than as prompts. Appropriate when the project's value is action-oriented (query, mutate, fetch) and there is no static-resource or prompt-template content to expose.

### Domain-bundled tool set

Curated multi-tool surface organized by entity-type or operation class — job/build/queue/node tools for a CI server, conversation/thread/search/reaction tools for a chat server, notebook-create/read/edit/export tools for a notebook server, orders/positions/watchlists for trading. Tool counts typically range ~14 to ~25. Resources optionally back the tool surface as listings (e.g., channel and user CSVs as directory resources). Appropriate when the underlying domain has well-defined entities and operations the LLM benefits from seeing as discrete callable units.

### Tools-heavy domain wrapper / domain-tool catalog

Server exposes 20-60+ tools wrapping a single upstream domain exhaustively — one database, one cloud vendor, one IDE language, 30+ ffmpeg media operations, 80+ Playwright browser operations, dozens (60+) for vendor servers grouped by domain, 300+ API methods across multiple object classes for editor-platform wrappers, into 250+ for surface-area-maximizing wrappers (e.g., kubectl). Schemas hand-authored or auto-derived per tool; tools cover CRUD, metadata, DDL, and management operations. Domain-tool catalogs commonly group by upstream-API object class (one module per object class) — a recurring decomposition shape, not just "many tools." Sometimes the domain wrapper additionally exposes an in-server docs-search endpoint as a tool surface, distinct from the database/upstream operations (RAG-style documentation augmentation alongside operational tools). Often paired with capability-grouping mechanisms to let consumers trim exposure. Comprehensive catalogs demand strong filtering controls (profile selection, tool include/exclude flags) so callers can scope what surfaces. Trade-off: large prompt footprint when the host loads all tools.

### Library fan-out

Many tools (90+) wrapping multiple upstream libraries inside one MCP surface — a "Swiss army knife" of a domain (geospatial: Shapely + GeoPandas + Rasterio + PyProj + GDAL + PySAL). Pairs with optional-dependency-per-library packaging so users install only the toolchain slices they need. Appropriate when the domain has multiple authoritative libraries no single one of which is sufficient.

### Aggregator-tool catalog (many upstreams, normalized tool surface)

Server multiplexes 20+ independent upstream APIs through a smaller set of normalized tools (e.g., `search_papers` dispatching across 20 academic providers; one tool per security data source across 21 vendors). Each upstream's credentials are independent; the tool layer presents a unified interface. The aggregator pattern co-occurs with per-source key optionality — when each upstream has its own credential and the surface is unified, missing keys produce graceful tool-level degradation rather than process failure. Appropriate when the user task is upstream-agnostic ("find a paper," "look up a CVE") and per-upstream details should be hidden.

### Single generic tool

One tool that accepts arbitrary input within a domain — a `query` tool taking arbitrary SQL, a single `fetch` tool. Delegates structuring entirely to the LLM. Appropriate when the underlying engine is itself a query language and the LLM is competent at producing it; minimizes server-side surface area at the cost of giving the LLM no structural guardrails.

### Single code-execution tool with sandbox

A single tool accepts a code string (e.g., a `boto3` Python snippet) and executes it server-side under an AST validator + import allowlist. Replaces N hand-enumerated per-API tools with one flexible primitive — a deliberate alternative to the tools-heavy domain wrapper shape. Appropriate when the underlying SDK is too large to enumerate, when LLM agility (composing API calls in one call) matters more than tool-level discoverability, and when the sandboxing mechanism is trustworthy enough for the deployment context. Cross-role: see *Safety and security posture — AST validation with import allowlist*.

### Token-economy unified-tool surface

Deliberate compression of the tool surface to a small number of broad tools (e.g., one unified query tool taking a wide query parameter, ~1,030 tokens of schema, plus one auxiliary tool). Rationale: schema text counts against the host's token budget, so fewer tools means smaller capability advertisement. Affects schema strategy and even backend indexing — the broad tool needs internal routing logic that finer-grained tools wouldn't.

### Tools plus resources

Server adds MCP resources alongside tools — typically read-only data the client can subscribe to or fetch (container stats, repository metadata, database tables and schema info as queryable URIs, knowledge bases under `zendesk://knowledge-base`, model/dataset catalogs under `hf://`, debug diagnostics, exported data with TTL-based auto-cleanup). Encourages the agent to treat the dataset as browsable rather than only queryable. Splits read access from write/action access along MCP primitive lines. Appropriate when the underlying domain has stateful, observable data that doesn't fit a "call this and get a response" shape, or when there's a clear addressable content surface that benefits from URI semantics. Resources are still under-supported by some clients, so authors offering them often duplicate the data via a tool for compatibility.

### Tools plus resources plus prompts (full primitive coverage)

SDK-built servers exposing the full MCP primitive set — tools, resources, prompts, sometimes plus completion, logging, sampling, roots, elicitation. Server adds MCP prompts on top of tools and resources, offering pre-canned natural-language workflows the user can pick from a menu (a "docker-compose workflow"; research-workflow prompts for literature review and analysis; operation-specific prompts auto-generated per OpenAPI operation; "compare these models", "summarize this paper"). Prompts can serve as orchestration primitives for natural-language → multi-step action (rather than the more common research/analysis-aid framing), shipping multi-step workflows the agent can invoke. Custom URI schemes (e.g., `hf://model/...`) are a recurring pattern when resources expose a vendor-native namespace not naturally addressable by `file://` or `http://`. Appropriate when there's a complex multi-step domain workflow worth surfacing as first-class capability, when the SDK is a reference for spec coverage rather than a single-purpose wrapper, or when the application needs both data exposure (resources) and reusable prompt scaffolds in addition to actions. Most cloud/infra servers skip prompts; using them is a deliberate design statement.

### Tools plus prompts (no resources)

Server vends tools and surfaces MCP "prompts" as first-class artifacts, often declared alongside tools in a manifest. Lets the host present pre-authored prompt templates the user can invoke directly. Research-workflow prompts is a canonical use case (analysis prompts shipping alongside data-fetch tools — e.g., academic-paper servers ship 6 tools + research prompts together). Appropriate when the project includes idiomatic prompts for working with its tools and the author wants those discoverable through MCP rather than buried in docs.

### Tools + sampling + prompts

Server adds MCP's sampling surface (server-initiated LLM calls back through the host) on top of tools and prompts. Used for agentic helpers like subject-line suggestion or multi-turn assist that need the host's LLM rather than running inference locally. Appropriate when the server has small auxiliary completions to make and doesn't want to bring its own inference path.

### Tools + prompt routines (out-of-band)

The server ships pre-authored Markdown prompt files alongside the tool surface, distributed as plain content (e.g., a `prompts/` directory) rather than via the MCP `prompts` primitive. Encodes "how to use this server for task X" as reusable templates the user manually loads. Chosen when the author wants to package guided workflows but doesn't need the protocol-level prompts primitive. Appropriate for servers whose tools combine into well-understood multi-step tasks (SEO audits, 404 detection, performance analysis).

### Bundled "agent SOPs" / vertical skill packs

Pre-built structured operating procedures shipped with the server, separate from raw tools — opinionated workflows that compose underlying tool calls; or markdown/prompt artifacts shaped for specific use cases (company research, code search, financial reports) that ride alongside the tool surface. The "skills, rules, prompt routines" content family expands this beyond a single skills directory: some repos carry parallel `skills/` and `rules/` directories shipping opinionated agent context alongside server code. Distinct from MCP prompts; an additional curated operational layer often targeting Claude's skills system rather than the MCP `prompts` capability. SOP bundling sometimes co-arrives with audit logging as a vertical-skill pack rather than just tools (the SOP plus audit-trail combination targets compliance-oriented deployments). Appropriate when the server author wants to ship not just API access but opinionated playbooks on top.

### Tools plus internal "skills" abstraction

The server vends tools and additionally maintains an internal-to-the-server "Skills" concept — toggleable behavioral bundles that operators can disable per-deployment via an env var (e.g., `MCP_DISABLE_SKILLS` with comma-separated subset list; skills typically live under `.agents/skills/` or similar in-server location). Skills are a higher-level capability primitive than individual tools and can be trimmed at startup to narrow the agent's behavioral surface for specific deployments. The deployment-level toggle gives operators a way to trim the behavioral surface without code changes, distinct from per-tool gating which targets the tools list rather than the higher-level skill grouping. Appropriate when the operator audience needs deployment-specific capability profiles (e.g., disable summarization skills in a security-sensitive deployment) without forking the server.

### Tools + resources + prompts + UI dashboards

Maximal MCP surface — tools, resources, prompts via protocol primitives, plus optional GUI dashboards bundled as an install extra. Chosen by surface-maximizing wrappers around very large APIs where every primitive has clear use. Implies an opt-in install extra (e.g., `[ui]`) for the dashboard component so users who only need protocol surface can avoid heavy dependencies.

### REST endpoints alongside MCP tools

HTTP-mode servers add purpose-built REST endpoints (`/storage/upload`, `/storage/download`, `/storage/list`) for data-plane operations MCP itself is not designed for — binary artifact transfer being the canonical case. Appropriate when the server's domain involves files too large or non-text for MCP message bodies; the MCP layer carries metadata while the REST layer carries bytes.

### MCP Roots participation

A server that consumes the host-provided "roots" protocol — receiving directory boundaries from the host and adapting its file access accordingly. Distinct from servers that take filesystem paths only as launch flags. Appropriate when the server handles user filesystem content and the host wants to dynamically scope access without restarting the server.

### Sampling and elicitation as client primitives

SDK exposes the *client-side* MCP primitives (sampling = LLM completion request back to the host; elicitation = request user input via the host) for applications building agents on top of MCP. Appropriate for SDKs that target both server and client construction.

### Read/write tool split

Distinct tools (or distinct tool groups) for read vs. write operations against the same upstream — `execute_read_only_query` vs. `execute_query`, Content API (read) vs. Admin API (write). Supports different approval or sandboxing workflows at the MCP-client layer; lets users grant only the read surface when write isn't needed.

### Per-tool output format selection

Tools accept an output-format parameter (text/JSON/markdown/CSV) so the caller controls representation, or a content-reduction parameter (e.g., `strip_thinking` to remove reasoning tags from output) controlling verbosity at the per-call level. Token-efficiency and rendering-quality knob; rare among MCP servers.

### User-publishable tools

Server provides a meta-tool that lets the user register new tools at runtime (e.g., `mcp_publish_tool` with a parameterized SQL template). Turns the server into a tool-registry rather than a fixed surface; specific to embedded-extension architectures where the substrate (DuckDB/SQL) makes parameterization safe.

### Embedded RAG / retrieval pipeline

Server bundles an embedding model, vector store, document parser, and retrieval logic in-process (llama-index, sentence-transformers, pinecone, pymupdf). Tool calls run inference and similarity search inside the server rather than delegating to an external RAG service. Server-boundary-blurring; sharply increases the server's footprint and dependency surface but provides domain-aware retrieval for documents the upstream doesn't pre-index. Sub-axis: "always remote embedding (requires keys)" vs "local-default with optional remote" — some servers ship a default-on, no-API-key local embedding backend (e.g., `fastembed` ONNX-backed) eliminating onboarding friction, with an escape hatch to remote embedding services via env var. RAG can also serve as documentation-lookup-as-tool, distinct from RAG-as-primary-capability — vendor docs/KB search rides alongside operational tools so the agent can self-reference vendor documentation while operating against the database/upstream.

### Tool catalog as data file

The set of tools is declared in a sidecar manifest (`tools.json` / `tools.txt`) rather than registered inline in source. Authoring tools no longer requires editing TypeScript or Python; the manifest is the single edit point and the runtime loads it. Trades runtime flexibility (dynamic tool generation) for editability by non-developers and review-friendly diffs.

### Spec-driven dynamic tool generation

Tools, resources, and prompts materialize at server start from configuration the operator provides — one or more parsed OpenAPI specs, a set of GraphQL operation definitions, or similar schema. No hand-authored tool definitions; the spec is the source of truth, and operators shape the catalog by choosing which operations to expose without touching server code. GET-with-query-params maps to MCP tools (LLMs handle parameterized search better as tools than resources); other GETs become resources; mutating operations become tools. Auto-enriched descriptions (response codes, parameter examples) materially reduce token cost vs naive rendering. Appropriate when the upstream API has well-maintained OpenAPI/GraphQL documentation and when the server is meant to front a moving target without per-version code changes. Constrains LLM behavior to whatever description quality the spec carries; every spec change is a contract change for the agent.

### Auto-routing across backends

Single logical tool (e.g., `search`) dispatches internally to one of multiple backend models (Sonar Pro / Sonar Reasoning / Sonar Deep Research) based on a complexity heuristic. The LLM picks "what to do," the server picks "which engine." Inverts the conventional surface where each backend gets its own tool name. Override parameter (`force_model`) lets the LLM bypass the heuristic when needed.

### Partition-scoped tool gating

Same server binary exposes a different tool set depending on a runtime-selected partition (e.g., AWS global vs China). Search/recommend tools surface in one partition; service-discovery tools surface in the other. Appropriate when the upstream backend itself differs by deployment region/cloud and a single binary should serve all.

### Capability gating flags (per-tool, per-category, write-mode)

Server takes startup flags or env vars that disable subsets of its capability surface — granular per-tool (`DISABLED_TOOLS=tool1,tool2`), category-level (`OPENSEARCH_DISABLED_CATEGORIES=search_relevance`, `--disable-write`, `--disable-delete`, `--disable-kubectl`, `--disable-helm`), or coarse mode-toggles (`--enable-write-tools`, `--read-only`, `READ_ONLY=true`, `--write-access`). Lets a single binary serve "read-only kiosk" and "full admin" deployments from the same image. Granularity matters: per-verb flags compose with per-tool-family flags so operators dial in exactly what an agent should be permitted to do — sometimes manifesting as a `<tool-family> × <verb-class>` matrix (orthogonal denial axes, denial-axis-multiplication). When tool counts are high (40+), gating sometimes operates at *category* granularity rather than per-tool, with default-on-vs-default-off per category letting operators reason at a higher abstraction. Default-off subsets are sometimes used to ship sensitive tool families opt-in (e.g., storage/file-management tools off by default; branching gated by paid plan). Reduces blast radius of an LLM accidentally invoking a destructive operation. Cross-role: see *Safety and security posture*.

### Capability gating via tool subsets at install time

Operator opts in to additional tool families at install time — `--caps=vision`, `--caps=pdf`, `--caps=testing` — rather than getting all tools by default. Distinct from a per-tool toggle: gates groups of related tools as a unit. Authors using this path frequently *contrast* it against per-tool gating and present it as a different gating axis — a stylistic stance the corpus surfaces. Appropriate when the surface is large enough that selective exposure changes both the token budget and the security posture.

### Tool-count modes (compound vs full)

A single server ships two operating modes: a compact "compound" surface (tens of aggregate tools) and a "full" surface (hundreds of granular tools), selectable via CLI flag at launch. Lets the user trade context-window pressure against expressive granularity without re-installing. Appropriate when the integration target has a very wide API (hundreds of methods) and the author has measured that the full surface overwhelms typical prompt budgets.

### Tools plus toolset gating (dynamic)

Large tool catalog (100+) partitioned into toolsets that operators can independently enable/disable via flags or env vars (`--tools=all`, `features=database,docs`). Adds runtime-discoverable "dynamic toolsets" — the catalog mutates mid-session based on agent action, so hosts that cache the tool list need to refresh. Read-only and lockdown modes act as orthogonal behavior envelopes layered over toolset selection. Some feature groups default off (e.g., storage tools) for conservative posture. Appropriate at scale when a single server covers many product surfaces and operators need fine-grained control over what's exposed.

### Scope-based tool filtering via URL param

For HTTP-mode servers, query parameters on the connection URL filter the tool surface (`?readonly=true`, `?category=branches`, `?projectId=...`). Different clients hitting the same hosted server see different tool surfaces. Appropriate for multi-tenant remote services where each client (or each session) needs different scoping without separate deployments.

### Destructive-tool elicitation list

Specific tools (drop-database, drop-collection) are flagged as `CONFIRMATION_REQUIRED_TOOLS`; invoking one triggers an MCP elicitation requesting human confirmation before execution. Appropriate as a per-tool safety rail beyond a coarse read-only flag — agents can invoke destructive tools but the human is brought into the loop.

### Progressive trust gating

Destructive operations (writes, drops) gated behind separate boolean env vars rather than a single read-only toggle (`*_ALLOW_WRITE_ACCESS` plus a separate `*_ALLOW_DROP`). Two-step opt-in for destructive surface; finer-grained than the binary read-only knob common elsewhere.

### Tool consolidation as design pressure

Authors actively reduce tool counts (one repo went from 46 atomic tools to 17 meta-tools) as a deliberate response to LLM discovery and parameter-validation pressure — too many narrow tools confuse model selection; broader meta-tools with more parameters work better. Surfaces as an explicit narrative choice, not just an emergent count.

### Self-reflective analytics tool

Tool exposes aggregated observations of the server's own past calls (`analyze_usage_patterns`, `get_translation_history`) back to the LLM. Implies local persistence of call history (atypical of the otherwise-stateless MCP server pattern) and surfaces the server's own behavior as a queryable resource.

### Capability probing and conditional surfacing

Optional capabilities (e.g., reranking) only surface when probed-at-start checks pass — the right region is configured and the IAM identity has the necessary permissions. Replaces tool-call-time failure with start-time exclusion. Appropriate when capabilities are credential- or region-conditional and users benefit from never seeing what won't work.

### Vendor-side capability scoping

Remote MCP services constrain what the server will do via OAuth scope and workspace admin approval, not via flags the user sets. The server itself enforces; the user can't elevate. Appropriate when the deployment model is hosted-service-with-tenants rather than local-subprocess.

### Capability authoring style

Cross-cutting sub-axis observed across the corpus — how the project's tool implementations get written and registered, constraining who can extend the server and what skills the change requires:

- **Code-defined tools via SDK decorators or registration calls** — Python/TypeScript/Go/Clojure functions decorated or registered programmatically; signatures and schemas derive from type hints or explicit registration calls. Adding a tool requires editing source and rebuilding/restarting. Appropriate when tool logic is non-trivial and authors are also developers of the server.
- **Declarative manifest authoring (YAML)** — Tools, toolsets, sources, and prompts declared in a YAML manifest the server reads at startup; admins add tools by editing YAML rather than writing code. The server provides a fixed set of "source" abstractions the manifest composes against. Hot reload propagates manifest changes without restart. Appropriate when the goal is to let non-developer admins (DBAs, ops) define tools against pre-built primitives.
- **Dynamic registration via API** — The server exposes a programmatic registration API; consumers can add tools to a running server via that API rather than only at startup. Decouples tool-set definition from the server's source. Appropriate when the server is embedded in a larger app that wants to vend its own tools through the same MCP endpoint.

## Configuration delivery

How runtime configuration (credentials, modes, endpoints, feature flags) reaches the server process at launch and during operation. Constrains how hosts wire credentials and how operators tune behavior.

<!-- adoption-table -->

Adoption — 103 samples exhibit `Sample > Configuration delivery`.

| Path                                            | Count | Coverage |
| ----------------------------------------------- | ----: | -------: |
| Environment variables                           |    72 |     70% |
| CLI flags                                       |    37 |     36% |
| Host-side JSON config snippet                   |    33 |     32% |
| Dotenv file                                     |    11 |     11% |
| Sidecar config files (JSON / YAML / TOML / EDN) |     7 |      7% |
| Functional options at construction (code-level) |     6 |      6% |
| HTTP request headers                            |     6 |      6% |
| Connection URI scheme                           |     4 |      4% |
| Hosted endpoint as primary delivery             |     4 |      4% |
| Mounted credentials                             |     4 |      4% |
| CLI flags with paired env-var equivalents       |     3 |      3% |
| URL query parameters on HTTP connection         |     3 |      3% |
| Auto-generated host-config JSON files           |     2 |      2% |
| Framework-native config file                    |     2 |      2% |
| Runtime reconfiguration tool                    |     2 |      2% |
| YAML manifest (declarative tool authoring)      |     2 |      2% |
| Feature-group toggles                           |     1 |      1% |
| Host-supplied protocol-level config (MCP Roots) |     1 |      1% |
| Per-tool enablement file                        |     1 |      1% |
| Persistent OS-native config                     |     1 |      1% |
| SQL PRAGMA parameters                           |     0 |      0% |
| Wrangler config (Cloudflare Workers)            |     0 |      0% |

<!-- /adoption-table -->
### Environment variables

The dominant path. Required and optional settings — credentials, connection strings, ports, feature toggles, regions/profiles, host overrides, encoding hints (`PYTHONIOENCODING=utf-8` on Windows) — read from `os.environ` (or equivalent) at process start. Common keys follow vendor-prefixed conventions: `<TOOL>_API_KEY`, `<TOOL>_HOST`, `<TOOL>_MCP_SERVER_TRANSPORT`, `AWS_PROFILE`, `AWS_REGION`, `FASTMCP_LOG_LEVEL`, `DOCKER_HOST`, `DATABASE_URI`, `JUPYTER_TOKEN`, `MDB_MCP_*`, `PAPER_SEARCH_MCP_*`, `OPENSEARCH_*`. Provider-prefixed patterns like `CHROMA_<PROVIDER>_API_KEY` give uniform surfaces across embedding back-ends. Compatible with every host-config format (each host has its own way of injecting env vars at subprocess launch) and with container runtimes (Docker `-e` flags). Often paired with Zod or Pydantic validation so misconfiguration fails loudly at startup. Often the only documented surface for stdio servers because the host can inject env vars in its config block (e.g., `claude_desktop_config.json`'s `env` block merged into the child's environment). Sometimes layered with proxy-hierarchy rules — a tool-specific proxy env var takes priority over standard `HTTPS_PROXY`/`HTTP_PROXY` for corporate environments. Required for credentials that should not appear on command lines (process listings, shell history) and the natural fit for container deployments where flags would require image rebuilds.

### CLI flags

Settings passed as command-line arguments at launch (`--api-key`, `--connection-string`, `--transport`, `--port`, `--storage-path`, `--client-type`, `--api-name`, `--spec-url`, `--include-tags`, `--exclude-tags`, `--enable-write-tools`, `--read-only`, `--write-access`, `--toolsets`, `--motherduck-token`, `--db-path`, `--keep-connection`, `--allow-root`, `--verbose`). Coexists with env vars; resolution priority typically CLI > env > file when multiple sources collide. The native fit for stdio servers launched by host configs that pass `args`. The most-discoverable surface (one `--help` away). Authors use flags when they want the host-config snippet self-documenting at a glance, when the value is intrinsically per-launch (transport choice, port), when configuration is structurally part of the server's identity (which spec to mount, which backing store to use), or when operationally-meaningful switches should be visible in process lists and shell history (capability gating, transport selection).

### CLI flags with paired env-var equivalents

Each flag has a `<PROJECT>_<FLAG>` env-var twin so the same setting can be supplied either way. Appropriate when the surface grows large (50+ flags) and ops want env-var overrides without rewriting host config.

### Dotenv file

`.env` file in the project directory or server working directory, loaded at startup via `python-dotenv` or Node equivalents. Mostly a developer-convenience layer over env vars; the production path remains environment variables. Resolution lands at the bottom of the priority chain (CLI > env > .env), though one observed project explicitly inverts this and treats `.env` as the highest-priority source — biases toward reproducible host-config-driven deployments at the cost of overriding CLI invocations. A tracked `.env.example` template ships in the repo; the operator copies and edits. Used for HTTP-mode servers where there is no host process to inject env, and for self-hosted developer-mode deployments where the user clones the repo. Sometimes referenced via a `--dotenv-path` flag, layered on top of env-var resolution.

### Host-side JSON config snippet

Indirect — the host's `mcpServers` JSON block specifies the launch command, args, and env that reach the server. Every locally-installed MCP server lives downstream of this; the README's job is to provide the JSON snippet. Universal across all stdio-launched servers regardless of runtime, and the user-facing surface — humans rarely write the raw command lines themselves. Different hosts use different paths and shapes (`mcp.json`, `claude_desktop_config.json`, `.cursor/mcp.json`, `~/.cursor/mcp.json`, `.vscode/mcp.json`, `cline_mcp_settings.json`). The server itself never reads this file; the host translates user setup into the actual launch command.

### Persistent OS-native config

Settings stored in a platform-appropriate config directory via `platformdirs` (`~/.config/<app>/` on Linux, `%APPDATA%\<app>\` on Windows), written by a management subcommand of the same binary (`set-api-key`, etc.). Survives across launches without per-host env-var setup. The `platformdirs` + setup-subcommand pairing often co-occurs as a deliberate design cluster — see *Developer ergonomics — Setup subcommands on the MCP binary*. Unusual in this corpus — most MCP servers leave persistence to the host's MCP config JSON and read only from env at runtime.

### Sidecar config files (JSON / YAML / TOML / EDN)

A JSON, YAML, TOML, or language-native data-format file (`mcp-config.json`, `elastic-mcp.json5`, `gordon-mcp.yml`, `.clojure-mcp/config.edn`, `MDB_MCP_CONFIG`) sits next to the binary and supplies tool definitions, vendor-specific integration settings, operation definitions, or runtime parameters. JSON5 (allows comments and trailing commas) appears as a JSON-cousin variant when configs need inline operator notes. Referenced by `--config <path>` or env-var pointer. Used when configuration is too large or structured for env vars and needs to be checked into a repo or shared between deployments, when the configuration shape is rich (tool filters, profile selection, formatting preferences), when ops teams already manage config files for the upstream system, or when the embedded-extension model makes env vars awkward. Centralizes settings; supports complex nested configuration that flags or env vars handle awkwardly.

### YAML manifest (declarative tool authoring)

Config flows in via a structured YAML file referenced by `--config <path>` or by convention (`example_config.yml`). The manifest defines sources, tools, toolsets, prompts, and operational settings in one place. Hot reload is feasible because the manifest is a separate file the server can re-read. Cross-role: see *Capability surface — Capability authoring style*. Appropriate when configuration is large, structured, and likely to evolve, and for project-governed servers where operator-facing config files are a deliverable artifact.

### Per-tool enablement file

JSON or similar file (`tools.json`) referenced by env var (`POSTGRES_TOOLS_CONFIG`) that toggles individual tools on/off. Used to reduce the LLM-visible tool surface without forking the server. Sits orthogonal to credential config — same server, different tool subset per deployment.

### Framework-native config file

Config file consumed by the server framework itself rather than by application code (`fastmcp.json` for FastMCP). Carries framework-level settings (transport defaults, runtime options) that don't belong in env vars or CLI. Coexists with the application's env-var surface.

### Wrangler config (Cloudflare Workers)

`wrangler.toml`/`wrangler.jsonc` per Worker controls deployment-time configuration (bindings, routes, secrets). Appropriate only for Workers-deployed servers; replaces the env-var/CLI surface for runtime config that doesn't change per-request.

### Mounted credentials

Credentials delivered to a containerized server by host volume mounts — kubeconfig, cloud-provider credential files (`~/.aws/credentials`). Implies the container runtime is the integration point and that the operator manages credential rotation outside the MCP layer. Appropriate when the credential format is established and the user already manages it externally.

### Connection URI scheme

A single connection URI (e.g., `redis://`, `rediss://`, `postgres://user:pass@host:port/db`) packs host, port, credentials, and TLS selection into one string. Often accepted alongside discrete CLI flags as a convenience. Appropriate for connection-oriented services where URI is the standard idiom of the underlying client library.

### URL query parameters on HTTP connection

For HTTP-mode servers, request-time scoping happens via query params on the host's connection URL (`?project_ref=...&read_only=true&features=database,docs`). Each client connection can carry different params. A coherent three-axis design often emerges: scope (e.g., `project_ref`) + mode (e.g., `read_only`) + feature toggle (e.g., `features=...`) — these axes combine multiplicatively to shape what the connection sees. Specific to HTTP-transport managed-cloud deployments; the same server process serves many tenants and per-request scope is part of the URL.

### HTTP request headers

Per-request credentials or overrides supplied on each MCP request (`x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password`, `Authorization`). Server may accept headers that override server-wide config (`--allowRequestOverrides=true`). Required for per-request multi-tenancy under HTTP transport. Appropriate when the server is shared and each caller carries their own upstream identity, or when HTTP multi-client setups need per-request posture variation.

### SQL PRAGMA parameters

Configuration values passed as named arguments to PRAGMA calls inside an embedded extension. The user, via SQL, configures the server at runtime rather than at process launch.

### Functional options at construction (code-level)

The SDK is a library; configuration happens at compile/build time via constructor calls and option functions (`WithToolCapabilities()`, `WithStreamableURI()`, `RegisterSession()`, `RegisterTool()`). No external config — choices are baked into the consuming program's source. Appropriate when the consumer is writing the server program themselves rather than running a pre-built binary.

### Runtime reconfiguration tool

A dedicated tool (`configure_service`) lets the host swap providers or update settings during a session without restart. Used by servers with multi-provider backends where the user might want to switch from SendGrid to Mailgun mid-conversation. Appropriate when the integration target is multi-provider and the user expects to compare or rotate without process churn.

### Auto-generated host-config JSON files

Installer (`install.py`) writes ready-to-paste `mcp_config_claude.json`, `mcp_config_vscode.json` files per supported host. Operator points the host at the generated file. Often pairs with a single installer script that walks the user through host selection (Claude Desktop, VS Code, Cursor, generic MCP-client target) — the installer becomes the documentation surface, replacing per-host README JSON snippets. Appropriate for installer-first distributions where the user is walked through setup interactively rather than reading docs.

### Host-supplied protocol-level config (MCP Roots)

The server picks up directory scope from the host through MCP messages rather than from CLI/env. Appropriate when the bound concept is something the host owns dynamically (open project, user workspace) rather than a static install setting.

### Hosted endpoint as primary delivery

For hosted-endpoint distributions, "configuration" is mostly the JSON snippet that the host (Cursor, Claude Desktop, VS Code) keeps in its own config directory pointing at the URL. The server itself has near-zero local config — the host's config file is the integration point.

### Feature-group toggles

Sub-pattern layered on top of any of the above mechanisms. The server exposes a single config field (`features=...`, `--tools=...`) that enables/disables groups of tools at startup. Reduces surface area for clients that don't need every capability and simplifies token/permission scoping. Some feature groups default off for conservative posture. Cross-role: see *Capability surface — Capability gating flags*.

## Authentication

How the server verifies callers (when relevant) and how upstream credentials reach it. Where the trust boundary sits and what proves identity at it.

<!-- adoption-table -->

Adoption — 102 samples exhibit `Sample > Authentication`.

| Path                                                              | Count | Coverage |
| ----------------------------------------------------------------- | ----: | -------: |
| Static API key / token via env var                                |    31 |     30% |
| None / implicit (local-resource gating)                           |    28 |     27% |
| OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)        |     9 |      9% |
| Database connection string                                        |     8 |      8% |
| Cloud-native identity / credential chain                          |     7 |      7% |
| OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)                  |     5 |      5% |
| Mounted file credentials                                          |     4 |      4% |
| Per-source independent API keys with graceful degradation         |     4 |      4% |
| API key (optional, for higher rate limits)                        |     3 |      3% |
| Application-delegated (SDK provides nothing)                      |     3 |      3% |
| Optional external LLM API keys                                    |     3 |      3% |
| Bearer token over HTTP/SSE                                        |     2 |      2% |
| Delegated to upstream toolchain credentials                       |     2 |      2% |
| JWT                                                               |     2 |      2% |
| Multi-scheme upstream auth (basic / IAM / header / mTLS)          |     2 |      2% |
| OAuth 2.0 client credentials                                      |     2 |      2% |
| Per-request bearer token (provider-scoped)                        |     2 |      2% |
| Per-tool varied (monorepo)                                        |     2 |      2% |
| Server-managed token rotation                                     |     2 |      2% |
| Bearer token via JSON config file                                 |     1 |      1% |
| Bot identity (third-party platform)                               |     1 |      1% |
| Credential-scoping guidance                                       |     1 |      1% |
| Domain-level access gate (not auth)                               |     1 |      1% |
| Dual-API split credentials                                        |     1 |      1% |
| In-server encrypted credential vault                              |     1 |      1% |
| Layered auth (protocol-level + upstream-level)                    |     1 |      1% |
| Locally-running application IPC                                   |     1 |      1% |
| Multi-method selector                                             |     1 |      1% |
| Multi-mode token selection                                        |     1 |      1% |
| Multi-provider credential bundles                                 |     1 |      1% |
| Multi-scheme client auth (API key / OAuth / JWT / Basic / Bearer) |     1 |      1% |
| OAuth setup-wizard flow                                           |     1 |      1% |
| Per-request HTTP-header credentials                               |     1 |      1% |
| Per-spec authentication                                           |     1 |      1% |
| SFTP / SSH credentials                                            |     1 |      1% |
| Service-account credential pair to cloud API                      |     1 |      1% |
| Service-specific credentials via third-party SDK                  |     1 |      1% |
| Upstream-delegated (gateway authorizer)                           |     1 |      1% |
| Delegated to upstream source                                      |     0 |      0% |

<!-- /adoption-table -->
### None / implicit (local-resource gating)

No auth at the MCP layer. Server runs with whatever credentials the host process has and trusts the local execution environment. The host launched it, the OS sandboxes it, no further auth is needed. Trust is implicit because the host launches the server as a child process under the user's identity. Also covers servers fronting public unauthenticated upstreams (PubMed, AWS public docs, arXiv search, Microsoft Planetary Computer STAC, public GitHub repos), browser-automation servers against the public web (auth managed by Playwright session state), and servers operating on local files, archives, locally-running applications, or public unauthenticated APIs. Often paired with a path-restriction mechanism (workspace root enforcement via `os.path.realpath`, explicit `--allow-root` opt-in) to prevent traversal outside an intended directory. The Playwright server explicitly notes "MCP is not a security boundary" — making non-auth a stated design posture rather than an oversight. Appropriate when single-tenant local deployment is the only mode, the upstream is public, the data lives entirely on the host's filesystem, or the integration target is a desktop-only library.

### Static API key / token via env var

A single long-lived API key, personal access token, or bearer token supplied via environment variable (`PERPLEXITY_API_KEY`, `EARTHDATA_PASSWORD`, `JUPYTER_TOKEN`, `MCP_TOKEN`, `HUB_PAT_TOKEN`, `EXA_API_KEY`, `ES_API_KEY`, `LINEAR_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `SENTRY_ACCESS_TOKEN`, `NOTION_TOKEN`, `SLACK_MCP_XOXC_TOKEN`, `motherduck_token`, `NVD_API_KEY`, `HF_TOKEN`, `TFC_TOKEN`, `HA_TOKEN`, `DISCORD_TOKEN`, `MILVUS_URI`, `SEMANTIC_SCHOLAR_API_KEY`). Single-tenant by construction — one credential, one identity, one process. The server itself does not re-authenticate the MCP caller; trust derives from the transport (stdio) or surrounding network controls. Some servers add a credential-resolution priority chain (CLI > env > file) so multiple sources can coexist. Often uses a provider-prefixed convention (`CHROMA_<PROVIDER>_API_KEY` for OpenAI, Cohere, etc.) when the server fronts a SaaS API authenticating per-call with a static key — bundling multiple cloud SDKs in core deps for graceful provider switching is the "fat install, zero-friction switching" trade-off. README guidance commonly emphasizes least-privilege upstream accounts and "never commit" hygiene because the credential is ambient to the process. The dominant pattern for SaaS-API-wrapping servers and the path of least resistance when the upstream service supports PATs.

### API key (optional, for higher rate limits)

Server works without credentials but accepts an API key to lift rate limits or unlock additional features (private-resource access, higher quotas). Lowers friction for first use; rewards users who register. Appropriate for public-data integrations where unauthenticated use is a real flow but heavy users need a way to identify themselves.

### Database connection string

Username/password embedded in a `postgres://user:pass@host:port/db`-style URL or MongoDB URI (`DATABASE_URI`, `MYSQL_PASSWORD`). Supplied via env var or CLI flag. Authentication is whatever the database speaks; the MCP server is just a relay. Limited to one credential set per process.

### Service-account credential pair to cloud API

Server holds a Client ID + Client Secret to a cloud vendor's API (MongoDB Atlas, AWS); often paired with IP allowlist requirements. Appropriate for managed cloud services where API-key-pair is the vendor's auth norm. Server may auto-provision short-lived database users (e.g., 4-hour TTL) on top of the long-lived service-account credential to limit blast radius.

### Bearer token over HTTP/SSE

Bearer token required when the transport is HTTP or SSE; absent on stdio (where the process boundary is the trust boundary). The HTTP transport accepts `Authorization: Bearer <token>` and validates per request. Token typically generated out-of-band (`uuidgen`, `openssl rand`) and passed via env var to the server. Either a coarse "is this a known client" check, or a headless alternative to interactive OAuth (same scoping model without browser redirect). Dev-mode override flag (`*_AUTH_DISABLED=true`) lets authors run unauthenticated locally without code changes. Appropriate when one server instance serves multiple network clients, for CI, server-to-server, and environments where browser flow is infeasible.

### JWT

HTTP-mode opt-in: client presents a JWT bearer token, server validates the signature against a configured secret (often required to be 32+ chars). Appropriate when multiple clients share a hosted server and the operator wants to gate access without running an OAuth provider.

### OAuth 2.x with issuer + JWKS (HTTP-mode bolt-on)

Optional bearer-token validation against a configured OAuth issuer and JWKS endpoint, available only on streamable-HTTP transport. Configured via env vars (`MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE`, JWKS endpoint). Two modes observed: global resource protection (any request requires a valid bearer token) and fine-grained per-tool/resource control (still flagged experimental). Often appears as one branch of a tri-modal switch (`AUTH_MODE=none|jwt|oauth`) where the dev default is `none` and production deployments opt into JWT or OAuth — rather than as a sole option. Whether downstream JWT validation is real verification or a stub is not always clear from READMEs and may differ across implementations. Client-side counterpart includes automatic token acquisition on a 401 response — the client discovers the protected resource metadata, acquires tokens, and retries (RFC 9728). Adds genuine MCP-caller authentication on top of the transport. Appropriate for hosted MCP deployments where multiple clients share a server and per-client identity matters.

### OAuth 2.0 client credentials

OAuth flow producing a bearer token with a documented lifetime (e.g., 3-8 hours) using a client ID + secret pair. Token may be supplied externally (env var or CLI flag) or generated by the server from credentials. No browser/user consent step — used when the upstream is a backend service (e.g., FHIR with client-credentials grant, single-merchant payment processors). Carries token-refresh concerns for long-lived sessions; whether refresh is handled in-server or delegated to the caller varies. Appropriate when the upstream service requires OAuth and the deployment is single-tenant.

### OAuth 2.1 / OIDC delegated (browser consent, multi-tenant)

Server delegates auth to an OIDC provider (Auth0, Cloudflare's own auth, vendor-specific clientIds) and accepts bearer tokens issued by it. Per-request user identity established via OAuth 2.1 — the host opens a browser on first connect; the server holds per-user tokens and routes each MCP call under the calling user's identity. Forces HTTP transport (stdio has no concept of "this request belongs to user X" and a browser cannot redirect to a stdio process) and unlocks true multi-tenant operation on a single process. Local development typically requires a tunneling tool (ngrok) to expose the OAuth callback URL — the dev-loop friction is a paired cost distinct from the production deployment cost, surfaced enough that some authors document the tunneling requirement explicitly. Streaming-HTTP-only deployments often treat OAuth 2.1 as the default rather than as an opt-in HTTP bolt-on. Hosts with native MCP OAuth support (e.g., VS Code 1.101+) handle the flow transparently. Token presented via `Authorization: Bearer` header. The cleanest model for SaaS tools whose data is naturally per-user (Slack, GitHub) and for production hosted deployments needing real per-user auth, scope-based authorization, or integration with an existing identity stack. Workspace admin approval often required.

### OAuth setup-wizard flow

A one-shot interactive command (e.g., `npx ctx7 setup`) walks the user through OAuth and writes the resulting credentials into the host's config file. Removes manual JSON editing for users; constrains the project to ship a setup helper alongside the server. Per-user identity rather than per-process. Pairs naturally with hosted HTTP MCP endpoints where the credential is sent on each request.

### Per-request bearer token (provider-scoped)

Hosted server expects each request to carry a credential scoped to the upstream provider's account (e.g., a Cloudflare API token). The server itself is account-agnostic; tenancy is determined per-call by which token arrived. Appropriate for first-party hosted servers fronting a multi-tenant platform — the same Worker serves any account that authenticates.

### Per-request HTTP-header credentials

Credentials passed in HTTP headers on each MCP request (`x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password`) instead of being baked into the server process. Turns a normally single-tenant stdio server into a multi-tenant HTTP service: one deployed server can route different requests to different upstream instances and credentials. Requires HTTP transport. Appropriate when one server instance must serve multiple end-users or multiple upstream environments without per-tenant deployment.

### Server-managed token rotation

The server holds a long-lived secret (or root-credential pair) and mints short-lived child tokens transparently — JWTs that expire every few minutes with automatic renewal, or per-database tokens minted from an org-level token with configurable expiration and permission scope. Pushes auth lifecycle work into the server rather than the client/host. Useful when the upstream API enforces short-lived tokens (Ghost Admin API JWTs) or when child-token issuance is a security-isolation primitive (Turso per-database tokens).

### Layered auth (protocol-level + upstream-level)

Server distinguishes "auth to the MCP interface" (e.g., `MCP_TOKEN`) from "auth to the upstream system" (e.g., `JUPYTER_TOKEN`). Appropriate when the MCP server brokers access to a separate authenticated system and the operator wants independent control over who can talk to MCP versus what MCP does upstream. Often a v1.x change after starting with the upstream credential alone.

### Multi-method selector

Server supports several auth methods (Basic, OAuth client credentials, API key) and selects between them via a config switch (`SERVICENOW_AUTH_TYPE` env var). Common where the upstream system is enterprise SaaS whose customers mandate different auth shapes; the server cannot pick just one without losing deployments. Adds documentation surface but avoids forking the codebase per auth flow.

### Multi-mode token selection

The server accepts several distinct credential types for the same upstream service (e.g., browser cookie, user OAuth token, bot token) and selects behavior based on which is supplied. Enables operating modes ranging from "stealth" (no workspace permissions, browser-cookie-based) to formal OAuth with workspace admin approval. Appropriate when the upstream service's permission model varies sharply by credential type.

### Multi-scheme upstream auth (basic / IAM / header / mTLS)

Server supports multiple auth schemes for the same upstream type (basic auth, AWS IAM roles, header-based auth, mutual TLS) so one binary covers self-hosted, managed-cloud, and mTLS-secured deployments. Appropriate for project-governed servers expected to work across the upstream's full deployment matrix.

### Multi-scheme client auth (API key / OAuth / JWT / Basic / Bearer)

Server-side acceptance of multiple credential types from clients calling the server, paired with rate limiting, circuit breaker, and audit logging. Appropriate when the server is a security/compliance tool that itself must prove multi-scheme readiness; otherwise excessive complexity for a single-tenant local server.

### Cloud-native identity / credential chain

Cloud-platform-specific auth path with multiple sub-flows — service principal, managed identity, default Azure credential (DefaultAzureCredential), AWS credential chain (env vars, `~/.aws/credentials`, instance profile, AWS SSO, STS session tokens, instance roles). Includes automatic token renewal with background refresh. The server doesn't see the credentials directly; the upstream client library resolves them. Co-exists with standard auth (e.g., username/password ACL) as an alternative path. Appropriate when the deployment is on cloud infrastructure and managed identity eliminates the credential-rotation problem; constrains tenancy to whatever profile/region is active at process launch.

### Mounted file credentials

Kubeconfig or cloud-provider credential files mounted into the container; the server reads them at startup. Same posture as the credential chain, but explicitly file-based and operator-controlled at deploy time. Appropriate when the wrapped tool already has a well-established local credential file (`~/.kube/config` for kubectl-class servers). Often co-occurs with *Delegated to upstream toolchain credentials* for kubectl-class servers — this path captures the *delivery mechanism* (file mount); the delegation path captures the *abstraction level* (server doesn't auth, upstream CLI does). Both legitimately apply to the same server; placement under both reflects the dual angle.

### Per-source independent API keys with graceful degradation

Aggregator server expects N independent API keys for N upstreams; each key is optional. Tools whose upstream lacks a key report the gap rather than failing the whole process. Appropriate for aggregator surfaces where users may only care about a subset of upstreams. Keys must never be logged or cached in audit entries.

### Multi-provider credential bundles

Server accepts credentials for many simultaneous backends (10+ email providers, multiple embedding services) and selects per-call which to use. Credentials still come from environment variables, but the env surface is much wider. A `configure_service` tool can also re-point credentials at runtime without restart. Appropriate when the server is a unified front for a heterogeneous backend ecosystem.

### Dual-API split credentials

Single server fronts two upstream APIs that have separate credential schemes — Ghost is a canonical example: Content API uses a 26-char hex key passed as a query parameter (read-only operations); Admin API uses JWTs auto-renewed every 5 minutes from an `id:secret` pair (read/write operations). Both credentials live in env vars; tools route to whichever API surface they belong to. Constrains tenancy because a user without one credential pair simply loses access to that group of tools.

### Per-spec authentication

Each upstream API mounted into the server can carry its own auth config (Basic, Bearer, API key in header/query/cookie, AWS Cognito). Appropriate when the server composes many APIs and each has its own credential context.

### Service-specific credentials via third-party SDK

Credentials handed to a community SDK (e.g., `zenpy` for Zendesk) that handles the upstream auth flow internally — API token, username/password, or whatever the SDK supports. The MCP server is a thin layer; the SDK owns the credential model. Appropriate when a mature community SDK already exists and re-implementing its auth would duplicate effort.

### In-server encrypted credential vault

The server stores secondary credentials encrypted with a master key, enabling on-disk persistence of sensitive material rather than relying on env-var pass-through alone. Driven by regulated-domain requirements (PHI/HIPAA in healthcare); rare elsewhere.

### Bearer token via JSON config file

The server reads a bearer token from a configuration file rather than env var or CLI flag. Used when the embedded-extension model means env vars are awkward to thread through the host process; JSON config is loaded by the server itself.

### Upstream-delegated (gateway authorizer)

Authentication happens before the request reaches the server — a Lambda authorizer or API Gateway validates bearer tokens in the `Authorization` header and the application code never sees raw credentials. Appropriate when the deployment substrate has its own auth tier and re-implementing it inside the server adds no value.

### Delegated to upstream toolchain credentials

The server does not authenticate at all on its own — it shells out to a tool (kubectl, helm) that already knows how to read its own credential file. The MCP server's auth surface is then "whatever the upstream CLI accepts." Inherits the upstream's RBAC and identity model wholesale, which is a feature when the host machine is already the user's working environment. Often co-occurs with *Mounted file credentials* for kubectl-class servers — this path captures the *abstraction level* (delegation); the mounted-credentials path captures the *delivery mechanism* (file mount). Both legitimately apply to the same server.

### Delegated to upstream source

Authentication isn't a server concern at all — the server connects to upstream sources (databases, cloud APIs) using whatever credentials those sources expect, configured per-source in the manifest. Includes ambient credentials (Google Cloud ADC, IAM) and per-database static credentials. Appropriate when the server is a multi-source proxy and each source has its own auth story.

### Application-delegated (SDK provides nothing)

The SDK exposes session-registration hooks but does not bundle an auth mechanism — applications wire their own at the transport layer. Appropriate for SDKs that want to remain unopinionated about deployment context (cloud, on-prem, in-process).

### Locally-running application IPC

Server talks to a desktop application over its own scripting interface (e.g., DaVinci Resolve's Python scripting API). The application enforces its own access model; the MCP server has no auth layer of its own. Requires the application to be configured for external scripting access. Appropriate when the integration target is a desktop application rather than a cloud service.

### Bot identity (third-party platform)

Auth against a chat or social platform via that platform's bot model — Discord bot tokens, etc. The bot's permissions (which servers it's invited to, what scopes it has) define the reachable surface; users grant the bot access through the platform's normal invite flow rather than configuring the MCP server directly.

### SFTP / SSH credentials

Username + key or password (or interactive prompt) for the remote filesystem the server reaches over SFTP. Auth mode itself is configurable (`--sftp-auth-mode auto/key/password/key+interactive`). Appropriate when the data plane is remote-filesystem rather than HTTP-API.

### Optional external LLM API keys

Server is locally trusted but optionally calls out to external LLMs (Anthropic, OpenAI, Google Gemini) for agent-augmented tools; those keys come from env vars when present. Appropriate when the server's core function works without LLM access but optional features benefit from it.

### Domain-level access gate (not auth)

The server enforces what can be accessed (filesystem allowlist, repository path, robots.txt for fetch) without identifying the caller. A different control plane — authorization without authentication. Appropriate when the threat model is "constrain what the trusted caller can ask," not "verify who is asking."

### Per-tool varied (monorepo)

In monorepos that ship many independent servers (one per wrapped tool), authentication varies per server — some need API keys (vulnerability databases), others need none (local CLI wrappers). The container env injection mechanism is uniform; the credentials inside it are tool-specific.

### Credential-scoping guidance

Documentation pattern (not a mechanism) — vendor recommends a scoped/restricted credential variant (e.g., Stripe Restricted API Keys) over the full-power root key. Security-ergonomics layer on top of whichever auth mechanism the server uses.

## Multi-tenancy

Whether and how a single server instance can serve multiple users or workspaces, and what enforces the boundary. Tightly coupled to transport.

<!-- adoption-table -->

Adoption — 102 samples exhibit `Sample > Multi-tenancy`.

| Path                                                      | Count | Coverage |
| --------------------------------------------------------- | ----: | -------: |
| Single-user / single-tenant per process                   |    66 |     65% |
| Per-user / per-workspace via OAuth                        |     7 |      7% |
| Single connection per server instance                     |     6 |      6% |
| N/A (library, not a runtime)                              |     5 |      5% |
| Per-request tenancy by inbound credential / bearer token  |     4 |      4% |
| Connection-lifecycle as a knob                            |     3 |      3% |
| Workspace-scoped sandboxing within a single tenant        |     3 |      3% |
| HTTP-stateful, single-tenant                              |     2 |      2% |
| Mode-switched backing store                               |     2 |      2% |
| Multi-client sharing one process via session multiplexing |     2 |      2% |
| Multi-spec / multi-source composition                     |     2 |      2% |
| Per-request tenant via URL parameter                      |     2 |      2% |
| Stateless read-only (any number of instances)             |     2 |      2% |
| Bot-scoped                                                |     1 |      1% |
| Externally-managed sessions via header                    |     1 |      1% |
| Per-call tenancy argument                                 |     1 |      1% |
| Per-request tenancy via OAuth token scoping               |     1 |      1% |
| Per-request tenancy via middleware                        |     1 |      1% |
| Per-request tenancy with externalized session state       |     1 |      1% |
| Per-session state via session registration                |     1 |      1% |
| Per-workspace tenant via upstream token                   |     1 |      1% |
| Stateless HTTP for shared deployment                      |     1 |      1% |
| Sub-tenancy via child-credential generation               |     1 |      1% |
| Tag-based resource scoping                                |     1 |      1% |

<!-- /adoption-table -->
### Single-user / single-tenant per process

One credential set, one user/workspace context per running server. State global to the process. Switching users means relaunching with different credentials. Universal in the corpus for locally-launched servers and for most SaaS-API-wrapping servers (one API key, one identity). Inevitable consequence of stdio + static API key — the host launches a fresh process per user/workspace and the process boundary equals the trust boundary. Appropriate when isolation is per-process, the host already isolates per-user by spawning per-user processes, and the cost of process startup is acceptable. Some servers (e.g., AWS API server) explicitly document the boundary in the README rather than leaving it implicit.

### HTTP-stateful, single-tenant

HTTP transport with stateful sessions, but still bound to one upstream credential set per server instance — sessions are MCP-protocol state, not tenant separation. Per-request tenant switching is explicitly out of scope.

### Multi-client sharing one process via session multiplexing

HTTP server with per-session state — multiple clients connect to the same process, each session keyed by transport-level identity (cookie, header, or token). Appropriate for HTTP servers where startup cost is non-trivial or where shared in-memory state (caches, connection pools) helps performance. Makes per-tool side effects (e.g., file writes) much harder to reason about, so this path tends to coexist with read-only or stateless tool surfaces.

### Per-session state via session registration

The SDK exposes a session abstraction — `RegisterSession()`, notification channels keyed by client — so a single server process can handle multiple concurrent clients with isolated state. Appropriate when the server runs as an HTTP service and "one process per user" is too costly.

### Externally-managed sessions via header

HTTP-mode server keeps sessions distinguished by `mcp-session-id` header when `EXTERNALLY_MANAGED_SESSIONS=true`. Per-session, not per-tenant; a single credential set still serves all sessions. Appropriate when an HTTP MCP gateway in front of the server handles tenant routing and the server only needs session affinity.

### Per-request tenancy via middleware

HTTP-mode server allows per-request connection overrides through middleware-managed context state — incoming request can carry connection settings that override the process defaults for the duration of that call. Closest the corpus comes to true multi-tenancy. Requires HTTP transport (stdio has no per-request channel for this) and a middleware extension point.

### Per-request tenancy with externalized session state

Each request carries its own tenant identity; persistent session state is held in an external store (e.g., DynamoDB) keyed by session ID. Appropriate for HTTP/serverless deployments where the process is shared across users and statelessness is enforced by the substrate.

### Per-request tenancy by inbound credential / bearer token

Hosted server is account-agnostic; tenancy is determined entirely by the bearer token on each request. Same Worker serves any authenticated account; nothing in the server's state binds it to one user. Suited to multi-user shared deployments behind a load balancer. Appropriate for first-party platform-as-a-service deployments where the platform's existing auth model is the source of truth.

### Per-call tenancy argument

Tenancy lives in the tool signatures themselves — search and retrieval tools take a tenant identifier as an argument and route the underlying call into that tenant's slice. Treats tenancy as a first-class parameter rather than a process-level config. Tools take a tenant parameter consistently (e.g., `search_in_tenant(tenant, query)`); naming convention shifts because tenancy enters every tool's signature. Rare across the Python ecosystem, which usually pushes tenancy to env vars. Appropriate when the integration target is itself multi-tenant (vector DBs with tenant collections) and a single MCP process should be able to serve multiple tenants through one credential.

### Per-request tenant via URL parameter

A hosted service multiplexes tenants by parameterizing the URL path or query (e.g., `/{owner}/{repo}`, `?project_ref=...` plus the OAuth identity). One deployment serves arbitrarily many tenants without per-tenant state. Required for managed-cloud-as-a-service deployment where one endpoint serves all customers. Appropriate when the upstream resource is itself addressable by URL parameter (a public repo, a public dataset).

### Per-user / per-workspace via OAuth

Specialization of per-request tenancy where the identity-bearer is an OAuth token tied to a real upstream user account, so each request executes under that user's permissions in the upstream system. The hosted deployment of a product maintains per-connection identity via OAuth, while the same code in stdio mode is single-user-per-process. Workspace is the tenant boundary in the workspace variant. Cleanest model for SaaS tools whose data is naturally per-user (Slack, GitHub) and for vendor services where workspace is the natural unit of administration and billing.

### Per-request tenancy via OAuth token scoping

Each request carries a token whose scopes determine tenant access. Server is multi-tenant by design; tenancy lives in the token, not in the server config. Appropriate for hosted remote services serving many independent users from one deployment.

### Per-workspace tenant via upstream token

The upstream service's auth model is the tenancy boundary — one Slack workspace token equals one tenant; per-user isolation falls out of the upstream's own DM/channel scoping. Appropriate for services whose permission model is workspace- or organization-scoped natively.

### Workspace-scoped sandboxing within a single tenant

Server constrains per-session operations to a configured base directory or working tree (`os.path.realpath` canonicalizing paths against an allow-listed root, `BASE_DIR`, `WORKSPACE_PATH`). A path-traversal defense that lets the server operate on local files while bounding the blast radius. Tenancy is still single-user, but file-system access is segmented per session within that user's allowed space. The pattern can include both (a) a server-wide root constraint and (b) per-session subdirectory tracking, where the same server process serves multiple stdio sessions each scoped to their own subdir within the allowed root. Appropriate when the underlying tool (git, file ops) would otherwise be free to roam the whole filesystem and the operator wants explicit boundaries — common for IDE-integrated developer tools where workspace = project.

### Sub-tenancy via child-credential generation

Server holds an organization-level credential and generates per-resource child credentials with bounded scope and expiration (per-database tokens from an org token). Provides isolation within a single organizational tenant rather than across tenants.

### Single connection per server instance

Database servers that hold one connection (per the supplied connection string) for the process lifetime. Effectively single-tenant; the workaround for multiple connections is multiple server instances.

### Stateless read-only (any number of instances)

No credentials, no per-user state — any number of instances can run concurrently because there is no shared mutable state. Applies to public-doc-fetching servers.

### Stateless HTTP for shared deployment

Server flag (e.g., `*_STATELESS_HTTP`) disables per-connection state so the server can sit behind a load balancer with multiple instances handling requests interchangeably. Pure request/response with no session affinity; each HTTP call carries everything needed. Multi-user-capable when paired with per-request auth.

### Tag-based resource scoping

Server-side filtering of which upstream resources are visible based on a tagging convention (e.g., AWS resource tag `mcp-multirag-kb=true`, overridable via env var). Tag enforcement happens at the server, not in LLM prompts. Appropriate when the upstream account contains many resources and the user wants to limit MCP visibility without building app-level access control. Treats infrastructure tagging as the access-control boundary.

### Multi-spec / multi-source composition

Single server fronts multiple upstream APIs concurrently; each spec has its own HTTP client and auth. Tenancy isn't user-based; it's source-based — the process serves one identity but composes data from multiple back-end sources declared in its manifest. Appropriate when the server is positioned as a gateway between one MCP host and many SaaS APIs, or when one operator (DBA, platform team) operates one server against many databases.

### Mode-switched backing store

Single binary supports multiple backing-store targets (in-memory ephemeral, durable local, remote self-hosted, SaaS) chosen at launch via flags. Appropriate when the same protocol surface should adapt to radically different deployment economics without forking the server. Replaces "multiple servers per backend" with "one server, mode flag."

### Connection-lifecycle as a knob

Some servers expose connection persistence as an explicit flag (`--keep-connection`, session-singleton mode). Trade-off: persistent connections enable cross-call state (TEMP tables, pooled clients) but break the stateless-per-request model and complicate multi-tenant safety. Appropriate when the underlying engine has session-scoped state worth preserving and the deployment is single-tenant.

### Bot-scoped

One bot identity per process; the bot's platform memberships define the reachable tenants. Multiple users may interact with the same bot, but the server's identity is fixed.

### N/A (library, not a runtime)

Project ships scaffolding and primitives; tenancy is the consumer's concern. Appropriate for SDK/framework projects (`mcpr`, MCP-server-building libraries) that don't operate a server themselves.

## Distribution channel

How end users and host configs obtain a runnable server. Constrains the install command shown in host config and the friction of getting started.

<!-- adoption-table -->

Adoption — 103 samples exhibit `Sample > Distribution channel`.

| Path                                                | Count | Coverage |
| --------------------------------------------------- | ----: | -------: |
| Docker / OCI image                                  |    51 |     50% |
| Source clone with editable install                  |    41 |     40% |
| PyPI via uvx (zero-install runner)                  |    34 |     33% |
| npm via npx / bunx                                  |    23 |     22% |
| PyPI via pip / pipx                                 |    22 |     21% |
| Smithery registry                                   |    13 |     13% |
| Hosted endpoint (no install)                        |    11 |     11% |
| Multi-channel publication                           |    10 |     10% |
| Go module via `go get` / `go install`               |     6 |      6% |
| Pre-built binary release                            |     6 |      6% |
| Source clone with `uv run` from source tree         |     4 |      4% |
| Cargo crate / cargo install                         |     3 |      3% |
| MCPB bundle / Desktop Extension manifest            |     3 |      3% |
| Pre-built host installer / one-click install URL    |     3 |      3% |
| Windows .exe variant                                |     3 |      3% |
| Configs-only repo (no server artifact)              |     2 |      2% |
| Custom Python installer script                      |     2 |      2% |
| Homebrew formula                                    |     2 |      2% |
| Install-from-git via uvx                            |     2 |      2% |
| SDK CLI installer                                   |     2 |      2% |
| `.claude-plugin/marketplace.json`                   |     2 |      2% |
| npm package wrapping native binary                  |     2 |      2% |
| Aggregator/installer registry                       |     1 |      1% |
| Cross-ecosystem packaging                           |     1 |      1% |
| Declarative NixOS / Home Manager module via nixpkgs |     1 |      1% |
| Docker Hub MCP Registry                             |     1 |      1% |
| Lambda deployment package                           |     1 |      1% |
| Language-native installer                           |     1 |      1% |
| Maven Central artifacts                             |     1 |      1% |
| Nix flake (`nix run github:...`)                    |     1 |      1% |
| Source build with make / CMake                      |     1 |      1% |
| Standalone bridge binary                            |     1 |      1% |
| Vendor-bundled (CLI subcommand)                     |     1 |      1% |
| Zed extension                                       |     1 |      1% |
| docker-compose variants                             |     1 |      1% |
| Interactive installer script                        |     0 |      0% |
| NuGet                                               |     0 |      0% |

<!-- /adoption-table -->
### PyPI via uvx (zero-install runner)

Python package published to PyPI; users invoke `uvx <package>@latest`, `uvx --from <package>@latest <command>`, or `uv run --with <name>` and `uv` resolves, downloads, and runs in an ephemeral environment. Becomes the canonical install command in host-config snippets (`command: "uvx"`, `args: ["<package>@latest"]`). Optional extras swap in alternative engines (`[chdb]` for embedded analytics, `[yaml]`, `[prometheus]`, `[pdf]`). Lowest user-side install ceremony for Python; requires `uv` on the user's system. Frequently the canonical README install path. The `uv tool install <package>` form persists the binary in the user's tool dir; `uvx` form fetches per-invocation. Eliminates virtualenv ceremony for end users and avoids environment conflicts.

### PyPI via pip / pipx

Standard `pip install <package>` (or `pip install '<package>[extra]'`, `uv pip install`, `pipx install`) followed by invoking the console script registered in `[project.scripts]`. Coexists with the `uvx` path on the same PyPI release; chosen by users who prefer a managed venv over uv's ephemeral environments. Editable installs (`pip install -e .[dev]`) for development. Optional extras gate heavier dependencies behind explicit user opt-in. Older idiom than uvx; positioned for users on plain Python rather than uv. Appropriate when the consumer base is Python-aware and willing to manage a venv.

### Install-from-git via uvx

Python server distributed without any registry publication — users install via `uvx --from git+https://github.com/<owner>/<repo> <command>`. The git URL becomes the effective package index; updates require pulling fresh, and there is no version range to pin. Surfaces when authors want zero registry-publication overhead, treat the project as internal/team-scoped without a marketing release, or want pre-release/fork-tracking access.

### Source clone with editable install

No registry publication — users clone the repo and run `uv venv && uv pip install -e .`, `pip install -e ".[dev]"`, `uv sync`, `npm install && npm run build`, `cargo build`, or equivalent. The "developer-mode-as-release" pattern. Optional dev extras live under `[project.optional-dependencies]`. Always implicitly available; documented explicitly when the project lacks a registry presence or for development workflows. Path of last resort or the deliberate choice for projects that don't want to maintain registry presence — early-stage repos, repos that want to require git-clone (so users get the README, examples, and `.env.example` template), prototypes, demonstrations, projects with system-level dependencies that resist packaging, internal tools, or frameworks where consumers are expected to build atop the source.

### Source clone with `uv run` from source tree

Server is launched from a checked-out source tree via `uv run src/<package>/server.py ...`. Unusual for vendor-official servers but observed across multiple corpus instances; signals either a development-leaning posture or that the project hasn't fully embraced PyPI distribution — the source-tree `uv run` pattern can be the *primary* documented install for a vendor-authored server, not just a developer-mode posture, when the vendor wants users to clone (perhaps to access bundled examples, configs, or to verify against pinned source) rather than fetch from PyPI. Forces consumers to clone the repository before they can run the server.

### Custom Python installer script

A bespoke `install.py` (multi-KB) creates a venv, installs deps, and writes per-client JSON configs into 10+ MCP client locations. Replaces both pip and uvx for the end user; the only command they run is `python install.py`. Appropriate when the server has unusual host-side requirements (must locate a desktop application, must write configs to many client locations) that no general-purpose installer could handle.

### npm via npx / bunx

Node/Bun servers published to npm; users invoke `npx -y @scope/package@latest` or `bunx ...` directly from host config. Lowest-friction Node path — single host-config line with no install step. Bin entries in `package.json` make the package itself the executable. On Windows the same command is wrapped as `cmd /c npx ...` to navigate shell quoting. Mirrors the uvx experience for the JS ecosystem. Latest-version-on-each-call ergonomics; npm pkg metadata also enables `claude_desktop_config.json` `"command": "npx"` snippets. Often used for one-shot setup commands (e.g., an OAuth-bootstrap script) as well as the long-running server.

### npm package wrapping native binary

An npm package (`@scope/server`) that downloads or wraps a native (Go, Rust) binary so node-oriented hosts can run the server by name via `npx`. Cross-ecosystem glue — the server isn't a Node program, but the install surface is. Appropriate when the audience expects `npx` install paths regardless of the server's actual runtime, or when a native binary wants to reach the broad npm install surface without forcing users to install Cargo/Go.

### NuGet

.NET packages on NuGet for C# servers, slotting into the .NET ecosystem's standard package manager. Often co-distributed with IDE-extension marketplace publications (Visual Studio Marketplace, IntelliJ Marketplace, Eclipse Marketplace) so the server reaches users through their IDE's native install flow.

### Cargo crate / cargo install

Rust packages distributed via crates.io. `cargo add` for library use, `cargo install <crate>` for CLI tools. Constrains end users to having a Rust toolchain (or accepting pre-built binaries from another channel). Appropriate for the Rust ecosystem.

### Go module via `go get` / `go install`

Library/SDK consumed by other Go programs via `go get github.com/<owner>/<repo>`; `go install` for CLI tools. Distribution is the source-as-Go-module model; no published binaries needed for the library use case. Appropriate when the artifact is an SDK rather than a runnable server.

### Pre-built binary release

Cross-platform binaries (Linux, macOS, Windows; AMD64, ARM64) attached to GitHub release tags. Users download via a script or manually and run directly. Avoids a language-runtime prerequisite. Source tarballs and changelog often published per release as a fallback for users not on language-specific package managers. Natural fit for Go, Rust, and other compile-to-static-binary runtimes. Often paired with signed checksums. Appropriate when the audience may not have the source language's toolchain installed.

### Standalone bridge binary

Pre-built executable that wraps a library so non-Go programs can use it without embedding. Distributed alongside the Go-module library for the same project. Suited to allowing Python/Node/etc. tools to consume an MCP server backed by the library without needing a Go toolchain.

### Maven Central artifacts

Published as `<group>:<artifact>` to Maven Central, consumed via Gradle/Maven dependency declarations. Granular artifact split (umbrella + client + server) lets consumers depend on just the half they need. Appropriate for JVM-targeted SDKs.

### Homebrew formula

A `brew install` path on macOS (and Linux via brew). Wraps a binary download with a tap-managed update channel. Often paired with shell installer scripts on Unix and PowerShell installers on Windows. Appropriate as one channel among several when reaching macOS-heavy developer audiences matters; a polish channel for native binaries that warrant package-manager presence.

### Docker / OCI image

Container image distributed via a registry (Docker Hub, GitHub Container Registry `ghcr.io`, AWS public ECR, GCP Artifact Registry, vendor registries like `docker.elastic.co/mcp/...`, `mcr.microsoft.com/playwright/mcp`, `mcp/<name>`) and launched with `docker run -i --rm` (often with mounts) from host config. Self-contained — runtime, dependencies, and any wrapped CLI tools are baked in. Multi-arch publication (linux/amd64, arm64, arm/v7) extends platform reach. Surfaces both as the primary distribution channel (when the server wraps platform-specific binaries that would be painful to install per-host, has heavy native dependencies, or deliberately rejects local installs as in Elasticsearch MCP, Slack MCP) and as a secondary channel alongside PyPI/npm for users who prefer container isolation. Often paired with build-time tweaks (e.g., auto-remap host address from `localhost` to `host.docker.internal` on macOS/Windows, `172.17.0.1` on Linux). Sometimes the README steers users to Docker first and treats pip/uvx as fallback. Appropriate when the server has system-tool dependencies (ffmpeg, browsers, system libraries), when the operator wants language-agnostic distribution, when consistent runtime + dependency packaging matters more than launching a native process, or when the deployment is a long-running service via `docker-compose`. Cross-role: see *Container artifacts*, *Test stack*, *Deployment artifact*.

### Docker Hub MCP Registry

Container image published to Docker Hub's MCP-specific registry. Distinct from a generic Docker Hub push because the registry is scoped to MCP servers. Appropriate when the server has external dependencies that benefit from being containerized and the author wants the registry's MCP-aware discovery.

### docker-compose variants

Multiple compose files for distinct use cases (`docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.toolkit.yml`) — each codifies a deployment flavor. Appropriate when the server has meaningfully different operating modes (dev vs prod vs ad-hoc tooling) that benefit from distinct compose configurations.

### Source build with make / CMake

Distribution requires `git clone` and a build step. Used when no package-registry path is established (DuckDB extension awaiting community-extensions inclusion) or when the project intentionally doesn't publish (compliance-sensitive servers expecting users to audit and build).

### Nix flake (`nix run github:...`)

Nix-native install via flake reference; consumers run `nix run github:<owner>/<repo>` without registry intermediation. Reproducible by Nix's content-addressed store. Often paired with a `nix develop` shell for contributors.

### Declarative NixOS / Home Manager module via nixpkgs

Server packaged as a first-class nixpkgs entry; users add a config block to their NixOS or Home Manager config. Rare among MCP servers — gives the project a system-config-managed install path for declarative-systems users.

### Smithery registry

Discovery-and-distribution registry specific to the MCP ecosystem, integrated via `npx -y @smithery/cli install <owner>/<repo> --client <host>` or via a `smithery.yaml` manifest in the repo. Adds the server to a searchable index of MCP servers; effectively a curation layer on top of npm/git/PyPI. Often additive — the server also publishes to npm or PyPI directly — but can also be a *primary* distribution channel for servers that opt out of PyPI/npm publication entirely (Smithery + git clone + Docker as the full distribution surface). Lets users install a server without the upstream having to publish to PyPI or npm. Appropriate when the author wants discoverability through the registry's catalog and one-click client wiring.

### Aggregator/installer registry

Meta-registry that wraps language registries with an MCP-aware install command — Smithery (above), `mcp-get`, the Docker MCP catalog, Glama. Reduces the host-config edit step to a CLI invocation. Appropriate for servers that want to be discoverable from MCP-specific browsing surfaces, not just generic package indexes.

### Pre-built host installer / one-click install URL

URL-protocol install button or deeplink shown in README per host (Kiro, Cursor, VS Code, Windsurf, Cline, Claude Code). Bypasses JSON copy-paste entirely for supported hosts; often pre-pins the server to a hosted-endpoint URL. The lowest install friction observed; requires the host to have explicit support for the format. Appropriate as a primary-surface ergonomic when many hosts need to be supported and the author is willing to encode per-host install URLs.

### MCPB bundle / Desktop Extension manifest

Server packaged as an `.mcpb` bundle for Claude Desktop drag-and-drop installation, with `.mcpbignore` controlling bundle contents. A Claude Desktop-specific packaging format (DXT — `manifest-dxt.json`) distinct from `.mcp.json`. Authoring may require a Rust signing path (Cargo.toml alongside pyproject.toml) for bundle signing. Ships alongside the server as a discoverable extension manifest. Appropriate as a frictionless install path for non-developer Claude Desktop users and when the server targets Claude Desktop as a primary integration.

### Zed extension

Editor-specific extension distribution channel for users running Zed. Appropriate as a long-tail audience reach for servers whose authors want broad editor coverage.

### Hosted endpoint (no install)

User pastes a URL into their host's MCP config; nothing installs locally. The author runs the runtime; patches propagate without user redeploys; the server depends on platform-internal data (e.g., a Cloudflare account's resources) the operator must own. Operationally distinct from "channel" — there is no artifact to ship — but competes with the other channels for the user's adoption decision. Distribution-as-a-service stance from vendors with existing SaaS infrastructure. Hosted endpoints can fully replace installable distribution when the vendor owns the runtime and can iterate without user redeploys; the local server becomes a developer artifact, not a user artifact, and the README's role collapses to a single URL plus OAuth bootstrap instructions. Hosted-endpoint distribution can also be a *catalog* shape where a single monorepo deploys N domain-scoped endpoints, with the README's primary content being which URL serves which capability rather than install instructions. Sometimes coexists with substantial public repo content shipping client-side artifacts (CLI for OAuth, skills for agent integration, marketplace metadata for discovery) while the actual server backend remains private. Cross-role: see *Transport — Hosted remote endpoint*.

### Configs-only repo (no server artifact)

Repo ships only client config snippets and OAuth setup metadata; the actual server is hosted remotely by the vendor. Distribution is "configure your client to point at our endpoint." Appropriate for vendor-hosted remote MCP services.

### Lambda deployment package

Server packaged as a Lambda deployment artifact (zip), included as a library dependency in a user's Lambda package. Appropriate for the serverless-MCP framework pattern where users deploy their own infrastructure.

### Language-native installer

Language-specific tool installer for non-Python ecosystems (e.g., `clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp`). Appropriate when the language has its own canonical distribution mechanism that users in that ecosystem already understand.

### SDK CLI installer

A framework-specific installer command (`fastmcp install <script.py>`) registers the script with target hosts and wires up the runtime invocation. Appropriate within ecosystems whose SDK provides such a CLI; substitutes for hand-edited host config files.

### Interactive installer script

Server ships an `install.py` (or similar) that runs an interactive setup — picks installation mode, generates host-config files, writes credentials. Appropriate when the install requires multi-step decisions the user can't easily make from a flat CLI invocation.

### Vendor-bundled (CLI subcommand)

Server ships inside another tool the user already has installed (Supabase CLI exposes a local MCP endpoint when `supabase start` runs). Distribution piggybacks on existing tool adoption.

### Windows .exe variant

Explicit Windows entry via `uv tool run --from <pkg> <pkg>.exe`. Documents that the server is reachable from Windows host configs and not just Mac/Linux.

### `.claude-plugin/marketplace.json`

Marketplace metadata file shipped in-repo so the project surfaces in Claude's plugin marketplace. Distinct from a full `plugin.json` plugin wrapper — the marketplace file alone enables discovery without installing the project as a Claude plugin.

### Multi-channel publication

Same server published through several channels simultaneously (PyPI + Docker + source; npm + managed endpoint + self-host package). Different user segments have different preferences; multi-channel publication maximizes reach but multiplies maintenance. Scales to 5+ channels at the corpus extreme — language-native registry + zero-install runner + MCP-aware aggregator + container + clone — covering distinct install audiences with deliberate cross-ecosystem reach (e.g., binary releases + Docker + `go install` + Homebrew + npm shim wrapping native binary). When this many channels appear, multi-channel becomes a positioning/canonical-status signal beyond just maximizing reach. Distinct framing in monorepos: each independent server can be multi-channel-published in its own right rather than the aggregate being one product across channels. Hosted-endpoint products sometimes triple the surface — managed cloud + CLI-bundled local + self-host npm — rather than picking one shape.

### Cross-ecosystem packaging

Single repository publishes the same conceptual artifact to multiple language ecosystems (PyPI + npm) with parallel naming conventions (`stripe-agent-toolkit` vs. `@stripe/agent-toolkit`), or a Python implementation with a thin npm wrapper that invokes the Python entry point under the hood. Enables both Python and TypeScript consumers from one source of truth; doubles publication and version-coordination work.

## Entry point and launch

The exact command host configs run to start the server. Determined by distribution channel and runtime, but with author-level shape choices.

<!-- adoption-table -->

Adoption — 102 samples exhibit `Sample > Entry point and launch`.

| Path                                              | Count | Coverage |
| ------------------------------------------------- | ----: | -------: |
| Console script via `[project.scripts]` / npm bin  |    44 |     43% |
| `uvx <package>`                                   |    26 |     25% |
| Docker container entrypoint                       |    22 |     22% |
| `npx -y <package>` / `bunx`                       |    20 |     20% |
| Bare interpreter + script path                    |    12 |     12% |
| Module invocation / `python -m <module>` fallback |    12 |     12% |
| URL configuration (no local launch)               |    10 |     10% |
| Built JS file (`node build/index.js`)             |     5 |      5% |
| SDK constructor + transport-method launch         |     4 |      4% |
| Subcommand verb                                   |     4 |      4% |
| `uv --directory` from source                      |     4 |      4% |
| npm scripts (start/start:stdio/start:http)        |     4 |      4% |
| Library import inside a user's handler            |     3 |      3% |
| Native binary                                     |     3 |      3% |
| Source-tree `uv run`                              |     3 |      3% |
| Click-based CLI wrapper (Python)                  |     2 |      2% |
| Framework CLI run                                 |     2 |      2% |
| Language-tool launcher                            |     2 |      2% |
| Make targets in repo                              |     2 |      2% |
| Multiple entry points per transport               |     2 |      2% |
| Profile-driven launcher                           |     2 |      2% |
| Programmatic embedding via library function       |     2 |      2% |
| CLI dispatcher subcommand                         |     1 |      1% |
| Generated binary from scaffolded project          |     1 |      1% |
| Mounted into another runtime as an extension      |     1 |      1% |
| SQL PRAGMA invocation                             |     1 |      1% |
| Setup ergonomics (cross-cutting)                  |     0 |      0% |

<!-- /adoption-table -->
### Console script via `[project.scripts]` / npm bin

A package-declared entry — `pyproject.toml`'s `[project.scripts]` defines `mcp-server-<name>` mapped to `module:main` (e.g., `mcp-clickhouse`, `arxiv-mcp-server`, `chroma-mcp`, `awslabs.<service>-mcp-server`, `postgres-mcp`, `mcp-server-qdrant`, `terraform-cloud-mcp`, `hass-mcp`); npm `package.json`'s `"bin"` field defines the equivalent. The script becomes available on PATH after install. Host config invokes the name directly. Quoted dotted names (`"awslabs.aws-api-mcp-server" = "..."`) let dotted PyPI names match dotted console-script names. Default for PyPI-distributed Python servers and the standard local-install entry point. Same pattern works with required CLI arguments inline (`grafana-loki-mcp -u ... -k ...`); host wrapper config must be careful with quoting.

### `uvx <package>`

Host config uses `"command": "uvx"` and passes the package name as an arg; the package is fetched and run on demand. The cleanest stdio launcher for Python servers and the common host-config shape for modern Python servers. Eliminates the need for users to pre-install or manage a venv.

### `npx -y <package>` / `bunx`

Bare `npx -y <package>` for Node servers. The `-y` accepts the install prompt automatically. Universal launch idiom for npm-distributed servers. The host's JSON config typically lists `npx` as the command and the package name (with `-y` for auto-confirm) as the first arg. Often passes `--api-key=...` or other CLI flags inline. Subcommand on the command line selects mode (HTTP default vs stdio). Also used for one-shot bootstrap commands like OAuth setup wizards. Windows variant wraps in `cmd /c`.

### Module invocation / `python -m <module>` fallback

Server invoked by running the package as a module, dispatched via `__main__.py` (`python -m <package>`). Functionally equivalent to a console-script entry but visible at the package level. Avoids requiring a console-script entry, or available alongside a console script as an alternative for advanced users invoking from a known interpreter. Common when the same binary doubles as a management CLI (subcommands like `set-api-key`, `check-config`, `test-connection`) on top of the MCP server protocol, and in source-distributed Python servers using uv.

### Bare interpreter + script path

`python <script.py>` or `node /abs/path/to/server.js` directly with absolute paths to a venv interpreter and the script. No installable package wrapping the entry point at all. Common in container-first projects where the Dockerfile is the runtime contract and console-script registration would be ceremony for nothing, in repos that distribute by source clone, in legacy `setup.py`-era projects, in single-file "hackable" layouts, when the server intentionally avoids Python packaging (custom installer owns the venv), or as a middle ground between "script with no args" and "console script with click." Bare `python` on system PATH is fragile (depends on which interpreter is first found).

### Built JS file (`node build/index.js`)

TypeScript projects compile to a JS output directory and host config invokes Node against the built file. Requires the consumer to have run `npm install && npm run build` first.

### `uv --directory` from source

`uv --directory /abs/path run <script>` invokes a console script from a source checkout, with uv resolving the venv and dependencies. Path-anchored launch where the host config points uv at a local source checkout. The `--directory=` form is path-anchored and incompatible with `uvx`-style zero-install runners — implies the package isn't meant for general distribution, only developer-installed local runs. No console script involved; the user must know both the package directory and the script name. Appropriate for editable-install distributions where the user has cloned but not published.

### Source-tree `uv run`

`"command": "uv"` with `run src/<package>/server.py ...` as args. Launches against a checked-out source path rather than an installed package. Unusual but documented in some projects' canonical configs.

### Click-based CLI wrapper (Python)

Python `click` CLI as the entry point, dispatching to FastMCP's runner internally. Adds richer argument handling than calling FastMCP's runner directly — useful when the launch surface needs flag parsing, subcommands, or help text beyond what the framework provides.

### Subcommand verb

The binary takes a subcommand selecting mode (`server stdio`, `server serve --write-access`, `server setup --tool=cline`). Mode is an explicit verb rather than a flag, separating "run the server" from "configure a host" cleanly. Appropriate when the binary has multiple roles beyond running the server.

### npm scripts (start/start:stdio/start:http)

`npm start` or named scripts dispatch to the underlying entry. Appropriate as the dev-mode launch path; production users typically prefer the console-script form.

### Multiple entry points per transport

Two or more separately-installed binaries, one per transport (`<server>` for stdio, `<server>-sse` for SSE). Lets each transport carry its own dependency closure (the SSE binary pulls in Starlette; the stdio binary doesn't). Higher install ceremony in exchange for lighter runtime footprint per mode.

### Docker container entrypoint

`docker run -i --rm <image>` (with `-e`/`-v` flags) replaces the local console script with a containerized one. The container's `ENTRYPOINT`/`CMD` runs the server. The host's MCP config invokes Docker as the command; the entire command is what host config calls, so host-side complexity grows with mount and env requirements. The MCP transport is stdio inside the container, with the `-i` flag wiring host stdin/stdout to the container. Appropriate when the server is distributed as a Docker image and the user wants containerization.

### Native binary

Pre-built standalone executable from a release artifact (Cargo, Homebrew, npm, release download); users run the binary path directly. Appropriate for Rust/Go-style compiled servers with no runtime deps.

### Generated binary from scaffolded project

Project generator emits a Rust crate; user runs `cargo build` and launches `target/debug/<name>`. Appropriate for SDK projects whose users build their own servers from a template.

### Library import inside a user's handler

No standalone command; the package is imported into a user-authored Lambda handler that delegates to it (`mcp.handle_request(event, context)`). Appropriate when the artifact is infrastructure for building servers rather than a server itself.

### Programmatic embedding via library function

The SDK exposes `createConnection()` (or analog) that returns an in-process MCP endpoint a host process can consume directly without subprocess IPC. Appropriate when the host is itself a Node/Kotlin app and wants to embed the server's tool surface as a library, blurring the server/client boundary.

### SDK constructor + transport-method launch

The server is a program the consumer wrote — `server.NewMCPServer()` returns a server value, then `server.ServeStdio()` or `server.ServeSSE()` runs it. The launcher is the consumer's `main`. Appropriate for Go/Kotlin SDK consumers building bespoke servers.

### Framework CLI run

`fastmcp run <script>` or `fastmcp install <script>` — framework's own CLI handles the runtime invocation. Substitutes for a project-level entry point. Appropriate when committing to the framework's conventions.

### CLI dispatcher subcommand

User runs `uvx <dispatcher> <server-name>` where the dispatcher routes to a child server within a monorepo PyPI package. Appropriate for monorepos that ship many servers under one package namespace.

### Profile-driven launcher

`clj -M:profile` — Clojure's profile mechanism, where `:stdio-server` and `:sse-server` are aliases in `deps.edn` selecting transport mode. Appropriate within Clojure tooling where profiles are the idiomatic launch surface.

### Language-tool launcher

Language-native command (e.g., `clojure -Tmcp start`, `clojure-mcp-light` profile). Appropriate when the language toolchain provides the launcher idiom users in that ecosystem expect.

### URL configuration (no local launch)

For managed-endpoint / vendor-hosted deployments, the user's MCP client points at an HTTPS URL — no local launch step. The "entry point" is the URL itself.

### SQL PRAGMA invocation

User starts the server from inside a DuckDB session via `PRAGMA mcp_server_start()`. The host process is the DuckDB CLI/library; the MCP server is a behavior toggled within it.

### Make targets in repo

Local-dev launch via `make run`, `make dev`, `make build`, etc. Common in projects with substantial dev tooling; not the end-user launch path but the developer-iteration path.

### Mounted into another runtime as an extension

Server doesn't run as its own process; it loads as an extension of an existing host (e.g., as a Jupyter Server extension). Configuration lives under `jupyter-config/`. Appropriate when the underlying system already has its own process and embedding is more efficient than running side-by-side.

### Setup ergonomics (cross-cutting)

Tooling that helps users wire the server into a host without hand-editing JSON. Cross-cutting with distribution + entry point but a distinct concern:

- **`setup` subcommand on the server binary** — `<server> setup --tool=<host>` writes the right host-config snippet for a target host. Rare; most projects expect users to hand-edit JSON. Designed as an extension point — the flag's value space lists supported hosts and grows over time.
- **Framework CLI installer** — The runtime framework provides `framework install <script>` that registers the script with target hosts (e.g., `fastmcp install`). Same effect as a per-server setup verb but factored into the framework.
- **Marketplace plugin** — The server is also published as an installable plugin in a host's plugin marketplace (Claude Desktop plugin, gemini-extension, MCPB). Users install via the marketplace UI; no JSON editing.
- **README JSON snippets** — The README enumerates per-host JSON config blocks the user copies and pastes into the host's MCP config file. The default for every server that doesn't ship a setup verb. Universally supported, but high friction relative to setup verbs or marketplace installs.
- **Universal installer covering many hosts** — A single `install.py` script writes per-host configs to up to 10 MCP client locations in one invocation, eliminating per-host setup steps.
- **Setup-wizard CLI as bootstrap** — A one-shot npx/uvx command bootstraps OAuth, writes host config, and registers credentials before the user touches any JSON.

## Build and packaging

How the source becomes an installable artifact. Includes build backend, lockfile, dependency-pinning approach, and version-manager conventions.

<!-- adoption-table -->

Adoption — 91 samples exhibit `Sample > Build and packaging`.

| Path                                        | Count | Coverage |
| ------------------------------------------- | ----: | -------: |
| Hatchling + uv (Python)                     |    45 |     49% |
| Python version pinning                      |    33 |     36% |
| npm/Node toolchain                          |    20 |     22% |
| Pin discipline (Python)                     |    16 |     18% |
| `uv.lock` committed                         |    13 |     14% |
| Optional-dependency fan-out                 |    11 |     12% |
| System-level dependencies                   |     8 |      9% |
| Requirements-driven (legacy Python)         |     5 |      5% |
| Cargo (Rust)                                |     4 |      4% |
| Setuptools (with `setup.py` or `setup.cfg`) |     4 |      4% |
| Go modules (`go.mod` / `go.sum`)            |     3 |      3% |
| Bare script (no build)                      |     2 |      2% |
| Maven / Gradle (JVM)                        |     2 |      2% |
| Wrangler bundle (Cloudflare Workers)        |     2 |      2% |
| uv_build backend (Python)                   |     2 |      2% |
| Hatch force-include for monorepo wheel      |     1 |      1% |
| Native build system (CMake / make)          |     1 |      1% |
| No lock file                                |     1 |      1% |
| Poetry (Python)                             |     1 |      1% |
| `requirements.lock` committed               |     1 |      1% |

<!-- /adoption-table -->
### Hatchling + uv (Python)

`build-backend = "hatchling.build"` in `pyproject.toml`, `uv` as dependency manager with `uv.lock` for pinning, install via `uv pip install` or `uvx`. The mainstream modern Python pattern and the most common Python build backend in the corpus; produces wheel/sdist for PyPI. Pairs with `[project.scripts]` console-script declarations, `requires-python` floors, src-layout (`src/<package>/`), and often `[dev]` extras for test-only deps. Per-sub-package uv projects in monorepo layouts.

### uv_build backend (Python)

Uv's native build backend, declared via `requires = ["uv_build>=0.8.3,<0.12.0"]` in `pyproject.toml`. Less common than hatchling. Sometimes paired with non-standard module-name conventions (e.g., `module-name = "app"`). Signals adoption of uv's full toolchain rather than just its venv/lock features. Appropriate for projects that want maximal uv integration and are willing to track a newer backend.

### Setuptools (with `setup.py` or `setup.cfg`)

Older convention, still appropriate for long-lived projects predating hatchling or for projects needing setuptools-specific features. Sometimes via `setup.py` directly, sometimes via `setuptools.build_meta` declared in `pyproject.toml`. Console scripts declared in setup.py's `entry_points`, but README invocation may diverge from the declared script (a sign the package was never installed/tested as a console script). Appropriate when the project predates the modern hatchling default or has setuptools-specific build steps.

### Poetry (Python)

Poetry as build backend with `poetry.lock` for reproducibility; can coexist with `uv` workflow on the same `pyproject.toml`. Some servers support both.

### Optional-dependency fan-out

Python projects expose multiple optional-dependency groups so users install only the slices they need. Patterns range from a single `[dev]` extra to a domain-driven fan-out of one extra per upstream library (e.g., per-GIS-library extras with an `all` composer). Optional extras swap in alternative engines (`[chdb]`, `[yaml]`, `[prometheus]`, `[pdf]`, `[ui]`, `[browser]`). Appropriate when the project's dependency surface is large and heterogeneous; lets the install footprint match the use case.

### Pin discipline (Python)

Discipline for framework version pins varies meaningfully: tight pins (`fastmcp == 2.7.0` / `>=3.1.0,<4`) track API drift in still-evolving lines; narrow ranges (`>=2.7.0,<2.11`) explicitly guard against minor-release breakage; exact pins (`fastmcp == 2.13.1`, `mcp[cli]==1.6.0`) prioritize reproducibility over upgrade speed; loose pins (`>=1.0.0`, `mcp>=0.1.0`) appear in minimal-ceremony servers. Choice signals the author's tolerance for upstream churn.

### Requirements-driven (legacy Python)

`requirements.txt` alongside or instead of `pyproject.toml`. Sometimes both coexist redundantly, suggesting the repo was bootstrapped from a requirements-first template before adding `pyproject.toml`. The redundant pair is a tell that the project predated `pyproject.toml` adoption and the manifest was added later without removing the original — the `requirements.txt` is typically the install contract that's actually exercised.

### `requirements.lock` committed

A pip-style lock file (often hand-maintained or via pip-tools), used as the install contract inside Dockerfiles for reproducible image builds. Appropriate when the project ships a Docker image and wants build-time pinning independent of runtime install resolution.

### `uv.lock` committed

Project commits its uv-managed lockfile so contributors and CI install the same resolved versions. Modern convention; not universal. Pairs with `uv` as the version manager and uv_build or hatchling backends. Appropriate when the project is uv-first and reproducibility across developer/CI/Docker environments matters.

### No lock file

Plain `pyproject.toml` with version ranges, no lock committed. Appropriate for libraries (where range flexibility helps consumers) but unusual for end-user-installable servers. Typically signals minimal-packaging posture or older project conventions.

### Bare script (no build)

Single-file `.py` server with no `pyproject.toml` build backend, optionally with `uv sync` against ad-hoc dependency declarations. Appropriate for personal tools and demonstrations.

### Hatch force-include for monorepo wheel

Custom `pyproject.toml` directive pulls nested `<package>/servers/` directories into the wheel when the canonical Python packaging path doesn't recognize them. Hatch force-include is the build-system substrate that makes the `Repository layout — Monorepo with per-server subdirectories and one PyPI package` pattern work — the two paths co-occur as a design cluster. Appropriate for dispatcher-style monorepos that ship one PyPI package containing many servers.

### Python version pinning

Cross-cutting sub-axis — how Python servers signal the required interpreter version to users and tools:

- **`requires-python` in `pyproject.toml`** — Declarative floor (`>=3.10`, `>=3.13`) read by pip/uv during install. Default among Python servers in the corpus.
- **`.python-version` (pyenv-style)** — Top-level dotfile read by pyenv and uv to select a local interpreter. Often paired with `requires-python` for redundancy.
- **`.tool-versions` (asdf)** — Multi-runtime version pin used by asdf. Rarer than pyenv-style; observed on a vendor-maintained Python server.
- **`runtime.txt` (Heroku-style)** — Heroku-style runtime declaration file pinning a specific patch-level Python version. Often used alongside `.python-version`; surfaces in projects with legacy Heroku/Procfile heritage or that want a third independent pin signal.

The floor itself is a posture signal — low floors (`>=3.8`) appear in legacy-packaging repos that haven't been updated; high floors (`>=3.13`) appear when authors deliberately track modern features and accept the deployment-environment cost. Same axis appears at both extremes within the corpus.

### Cargo (Rust)

Standard Rust build via `Cargo.toml`/`Cargo.lock`; produces native binaries published to crates.io. Pinned to a specific Rust toolchain via `rust-toolchain.toml`. Appropriate for the Rust ecosystem; consumers either install the binary or depend on the library.

### Go modules (`go.mod` / `go.sum`)

Standard Go build via `go.mod` (declares module path and Go version constraint) and `go.sum` (locked dependency hashes). Resolved by the Go toolchain; produces single static binaries with no external runtime dependency. The Go peer of `Cargo (Rust)` — Go's package and version-pinning surface lives in `go.mod`/`go.sum` rather than in `pyproject.toml`/`package.json`/`Cargo.toml`. Often paired with Docker container distribution for the final artifact. Appropriate for Go SDKs and Go-implemented MCP servers.

### npm/Node toolchain

`package.json` defines build and bin entries; npm registry is the publish target. Build via tsup, esbuild, tsx, or webpack producing a `build/` or `dist/` JS artifact.

### Wrangler bundle (Cloudflare Workers)

Wrangler bundles the TypeScript source into a Worker artifact and deploys directly to Cloudflare's edge. The "package" is the deployed Worker, not a downloadable file. Appropriate for Workers-targeted servers.

### Maven / Gradle (JVM)

Maven Central artifacts for Kotlin Multiplatform SDKs and JVM consumers. Multi-module Gradle layouts split umbrella, client, server, and testing artifacts.

### Native build system (CMake / make)

Tests run via the native build system's test target (`make test` invoking CMake/CTest for the C++ extension). Appropriate when the project is a native extension or includes native components.

### System-level dependencies

Cross-cutting sub-axis — external binaries the host must install before the server can run:

- **Self-contained (registry-only)** — Server's runtime dependencies all install via the package manager — no out-of-band system tools required. Pure language ecosystem (`npm install` / `pip install` / `go get` / Gradle resolution). The default expectation; appropriate when domain libraries are pure-Python or include their own bundled binaries (PyMuPDF, sqlite3 wheels), or when the wrapped functionality is itself implementable in the host language.
- **System binary required (CLI on PATH)** — Server depends on a host-level binary (Tesseract OCR, GDAL, ffmpeg, system tool) that the package manager cannot install. README surfaces the install responsibility on the user (`apt-get install ffmpeg` for CI). Docker becomes the only self-contained distribution path.
- **Browser runtime (Playwright)** — Server depends on a browser binary that Playwright fetches as part of its install step. Multi-GB install footprint; container distribution becomes significantly more attractive than pip/npm.

## Schema and types

How tool input/output schemas are produced and validated. Tightly coupled to the runtime choice.

<!-- adoption-table -->

Adoption — 58 samples exhibit `Sample > Schema and types`.

| Path                                    | Count | Coverage |
| --------------------------------------- | ----: | -------: |
| FastMCP auto-derivation from type hints |    26 |     45% |
| Async model (cross-cutting)             |    25 |     43% |
| Pydantic v2 models                      |    19 |     33% |
| Hand-authored tool schemas              |    13 |     22% |
| Zod (TypeScript)                        |     4 |      7% |
| Go automatic schema generation          |     2 |      3% |
| Rust schema crate                       |     1 |      2% |

<!-- /adoption-table -->
### FastMCP auto-derivation from type hints

Tool function signatures with type hints become the MCP tool's input schema automatically; return types feed the output schema. Authoring effort is "write a typed Python function." Default when FastMCP is the runtime; FastMCP derives JSON schemas via Pydantic at registration time.

### Pydantic v2 models

Pydantic models for structured payloads, used both with raw `mcp` SDK (hand-registered) and alongside FastMCP for richer validation. Author writes Pydantic models explicitly and registers them with the SDK's tool registration calls. Appropriate when the author wants explicit control over schema shape (descriptions, field metadata) that decorator-magic might obscure.

### Hand-authored tool schemas

When using the raw `mcp` SDK without FastMCP, tool handlers register an explicit input schema dict; the author writes the schema directly. Used for very large tool surfaces (300+ tools) where reflective derivation would be too slow at startup, or when the source of truth is an external API spec. Also used in TypeScript servers where schemas are written directly.

### Zod (TypeScript)

Zod schemas validate tool inputs and env/config in TypeScript servers. Appropriate when the server runs on Node and the surrounding stack already uses Zod for runtime validation.

### Rust schema crate

`rust-mcp-schema` crate provides the type definitions; tools are registered with strongly-typed handlers. Types are compile-time-checked rather than reflected. Appropriate as the natural Rust idiom.

### Go automatic schema generation

Native Go structs become tool arguments with automatic JSON-Schema generation via the SDK's reflection. Type-safe schemas without runtime reflection cost matter; appropriate for the Go SDK ecosystem.

### Async model (cross-cutting)

Whether tool handlers are sync or async, and what drives the choice:

- **Async throughout** — Tool handlers are `async def`; FastMCP and the MCP SDK both accept async handlers natively. Connection pooling for outbound calls is enabled. Appropriate when the integration target has an async client library or makes network calls that benefit from non-blocking IO.
- **Sync throughout** — Tool handlers are plain `def`. Forced when the underlying library is sync-only (scikit-learn, DaVinci Resolve's scripting API). Wrapping sync work in async would add thread overhead with no concurrency win.
- **Mixed** — The MCP SDK accepts both forms in the same server; some tools are async (network calls), others sync (CPU work). Appropriate when the integration target has both kinds of operation.

## Container artifacts

Container-related files in the repo and what role each plays in build, dev, and contribution. Distinct from container-as-distribution-channel: this role tracks the build artifact regardless of whether it's published. Cross-role: see *Distribution channel — Docker image*, *Test stack*, *Deployment artifact*.

<!-- adoption-table -->

Adoption — 82 samples exhibit `Sample > Container artifacts`.

| Path                                          | Count | Coverage |
| --------------------------------------------- | ----: | -------: |
| Dockerfile (single-stage, build-from-source)  |    46 |     56% |
| No container artifacts                        |    22 |     27% |
| Published Docker image                        |    15 |     18% |
| Docker Compose for local dev                  |     8 |     10% |
| Multi-architecture image publishing           |     4 |      5% |
| Multi-stage Dockerfile                        |     4 |      5% |
| Cloudflare Workers config                     |     3 |      4% |
| Per-server Dockerfile in monorepo             |     3 |      4% |
| Vendor-namespaced image                       |     3 |      4% |
| Devcontainer for contributors                 |     2 |      2% |
| Docker-Compose backend for end-to-end tests   |     2 |      2% |
| Hardened-by-default container posture         |     2 |      2% |
| Multi-Dockerfile (prod / dev split)           |     2 |      2% |
| Vercel deployment config                      |     2 |      2% |
| `.mcpbignore` for bundle packaging            |     2 |      2% |
| Azure deployment artifacts                    |     1 |      1% |
| Docker Compose for multi-server orchestration |     1 |      1% |
| Dockerfile.template as scaffold               |     1 |      1% |
| Nix flake / NixOS module                      |     1 |      1% |
| Podman alternative                            |     1 |      1% |
| Lambda zip                                    |     0 |      0% |
| Makefile-driven Docker build                  |     0 |      0% |

<!-- /adoption-table -->
### Dockerfile (single-stage, build-from-source)

`Dockerfile` at repo root producing the runtime image used in production. Bakes in the language runtime, dependencies, and the server entry point. Universal across runtimes — present in nearly every sample even when not the primary distribution channel; Docker has become the lowest-common-denominator deployment shape. Typically pins a slim base image (`python:3.11-slim`, `node:22-alpine`). Often installs from a lock file (`uv.lock`, `requirements.lock`) for reproducibility rather than from `pyproject.toml` resolution. Sometimes adds quality-of-life touches (host-address auto-remap, entry point wrapper). Appropriate when the author wants to provide a containerization recipe without operating a registry.

### Multi-stage Dockerfile

Separate build and runtime stages; final image excludes build dependencies. Multi-stage build separating the build environment (full Node + dev deps) from the runtime environment (Alpine + production deps). Yields smaller images. For Rust: builder stage uses `clux/muslrust:stable`, final stage is `alpine:latest` with a non-root user, producing a small static-binary image. Appropriate for production-bound servers where image size and attack surface matter.

### Multi-Dockerfile (prod / dev split)

`Dockerfile` for production image plus alternates (`Dockerfile-8000` tuned for specific port conventions, `Dockerfile.local` for development). Explicit separation when the dev image needs additional tooling or different base, or when vendor-operated projects publish the same artifact to several deployment platforms (EC2, ECS, EKS).

### Per-server Dockerfile in monorepo

Each server in a monorepo has its own Dockerfile; images publish to Docker Hub under `mcp/<name>` or vendor namespace. Appropriate when the repo is a curated reference set and consumers want one-image-per-server semantics.

### Dockerfile.template as scaffold

A template Dockerfile parameterized for "new tool added to the monorepo" — enforces the security baseline (non-root, capability-drop, read-only mounts, resource limits) and base-image conventions across all per-tool servers. Contribution-surface artifact, not a runtime artifact.

### Hardened-by-default container posture

Dockerfile baseline includes non-root user, dropped Linux capabilities, read-only filesystem mounts, resource limits. Surfaces in security-focused projects where the wrapped CLI tools are themselves attack surface; uncommon in general-purpose MCP servers.

### Vendor-namespaced image

Image lives in a vendor registry (`mcr.microsoft.com/playwright/mcp`) rather than the public `mcp/*` namespace. Multi-arch builds extend reach. Appropriate when the publisher is a brand-conscious vendor with its own registry.

### Multi-architecture image publishing

Docker images published for linux/amd64, arm64, and arm/v7. Often multi-platform via Buildx. Appropriate when the user base spans Apple Silicon, Linux x86, and lower-power ARM devices.

### Published Docker image

Pre-built image at a known registry (ghcr.io, AWS public ECR, Docker Hub, vendor registries). Lets users skip the local build. Doubles as a distribution channel (consumers `docker pull`) and a deployment artifact (operators run the image directly). Often paired with `docker run -i` host configs.

### Docker Compose for local dev

`docker-compose.yml` orchestrating the server alongside its backing services for local development (e.g., spinning up a database the server connects to). Distinct role from the production Dockerfile — Compose owns the dev-loop experience, the Dockerfile owns the runtime artifact. Used by HTTP-mode servers where ops want a one-command local environment.

### Docker Compose for multi-server orchestration

In monorepo-of-servers layouts, Compose orchestrates many MCP server containers together so users can bring up the full security or domain toolchain at once.

### Docker-Compose backend for end-to-end tests

Repo ships a `docker-compose.yml` that brings up the upstream service (Ghost+MySQL, etc.) for local end-to-end testing — not for deploying the MCP server itself, but as the substrate the test suite hits. Notable infrastructure investment for an MCP repo. Sometimes serves dual purposes — production deploy plus test substrate.

### Makefile-driven Docker build

`make build` invokes Docker build under the hood. Combines container packaging with the project's broader make-target workflow.

### Podman alternative

Documentation acknowledging Podman as a Docker alternative for the same image. Reflects environments where rootless containers or Docker-Desktop-licensing concerns push users away from Docker.

### Devcontainer for contributors

`.devcontainer/` configuration at repo root provides a reproducible contributor environment. Separate concern from runtime distribution. Appropriate for monorepos and projects with non-trivial developer setup.

### Vercel deployment config

`vercel.json` for serving the HTTP-mode server as a Vercel function. The hosted-endpoint backend pattern when the vendor doesn't run their own infrastructure.

### Cloudflare Workers config

`wrangler.jsonc` declares the Workers deployment. There is no Dockerfile because the runtime substrate is the Workers platform. Appropriate when the project is itself a Workers application.

### Lambda zip

Server packaged as a Lambda deployment artifact rather than a container. Appropriate for the serverless deployment model where API Gateway is the front door.

### Nix flake / NixOS module

`flake.nix` for `nix develop` and `nix run` workflows; declarative module exposed via nixpkgs for system-level installation. Doubles as distribution (consumers `nix run`) and dev environment (`nix develop` provides a reproducible shell).

### Azure deployment artifacts

`deploy/` directory with Azure-specific guides and scripts. Appropriate for vendors who want to provide first-class managed-cloud deployment paths.

### `.mcpbignore` for bundle packaging

Glob file controlling what's excluded from the `.mcpb` bundle. Appropriate alongside MCP Bundle distribution.

### No container artifacts

Project ships only language-package or source distribution; users who want containerization build their own image. Sometimes omitted intentionally because the server must run on the host with the integration target (desktop application, local-process IPC), or because MCPB bundling replaces the container role.

## Test stack

How the project verifies correctness, and what infrastructure tests depend on. Constrains release cadence and refactor safety.

<!-- adoption-table -->

Adoption — 84 samples exhibit `Sample > Test stack`.

| Path                                                              | Count | Coverage |
| ----------------------------------------------------------------- | ----: | -------: |
| pytest with async + coverage                                      |    45 |     54% |
| No tests / not surfaced                                           |    10 |     12% |
| Linter/formatter test gate                                        |     7 |      8% |
| Go stdlib testing                                                 |     6 |      7% |
| Vitest (TypeScript / Node)                                        |     6 |      7% |
| Dev extras gating test deps                                       |     5 |      6% |
| End-to-end protocol-conformance harness                           |     4 |      5% |
| MyPy strict + Bandit security scans alongside tests               |     3 |      4% |
| Branch coverage enforcement                                       |     2 |      2% |
| Cargo test / cargo-nextest (Rust)                                 |     2 |      2% |
| Clojure-native testing                                            |     2 |      2% |
| End-to-end with browser automation                                |     2 |      2% |
| Jest (TypeScript / Node)                                          |     2 |      2% |
| MCP Inspector as test driver                                      |     2 |      2% |
| Mock transport layer for protocol-level testing                   |     2 |      2% |
| `make test` targets                                               |     2 |      2% |
| Bun test runner with Vitest compatibility                         |     1 |      1% |
| Evaluation harness alongside unit tests                           |     1 |      1% |
| External agent validation artifacts                               |     1 |      1% |
| Live integration test gating                                      |     1 |      1% |
| Live multi-phase suite against application                        |     1 |      1% |
| Native build-system test target                                   |     1 |      1% |
| Pyramid with web E2E (Playwright + ephemeral DB)                  |     1 |      1% |
| Recorded HTTP fixtures (cassettes)                                |     1 |      1% |
| Separate integration_tests/ directory                             |     1 |      1% |
| Stratified suite with unit + integration + cache + security tiers |     1 |      1% |
| TypeScript noEmit type-check as the test command                  |     1 |      1% |
| Container-based test stack                                        |     0 |      0% |
| In-memory transport for protocol tests                            |     0 |      0% |
| Multi-tier Kotlin testing                                         |     0 |      0% |
| `pytest` declared as runtime dependency                           |     0 |      0% |

<!-- /adoption-table -->
### pytest with async + coverage

Python servers consistently choose pytest with `pytest-asyncio` (`asyncio_mode = "auto"`, per-function loop scope) and/or `pytest-anyio` for async test support. Frequently paired with `pytest-cov`, `pytest-timeout`, sometimes a coverage gate (`--cov-fail-under=80` in `addopts`), and `pytest-mock`. FastMCP itself stretches this further with `pytest-flakefinder`, `pytest-retry`, `pytest-xdist`, `inline-snapshot`, `pytest-examples` — flake hunting and parallelism investments rare among consumers. Some servers ship cross-platform shell wrappers (`run_tests.sh`, `run_tests.ps1`). Test plans codified in markdown (`test_plan.md`) appear when scenarios outweigh unit cases. Configuration variously lives in `pyproject.toml`'s `[tool.pytest.ini_options]` (newer projects, with `asyncio_default_fixture_loop_scope = "function"`) or in a separate `pytest.ini` plus `requirements-dev.txt` (legacy split that survives in older repos). Tests live in `tests/` discovered by `pytest`, or `test_*.py` files alongside `server.py` in early-stage single-file repos. Test density varies widely with no clear correlation to project popularity. Some projects layer custom markers to separate test scopes — `integration`, `dc_e2e`, `cloud_e2e` distinguishing on-prem vs. cloud deployment-mode tests. Markers can encode deployment-mode coverage when the server supports multiple deployment substrates and ride alongside `integration` rather than replacing it. Projects sometimes declare both `pytest-asyncio` and `pytest-anyio` in dev, suggesting mixed async-runtime test fixtures coexist. May include in-memory backends as fixtures (e.g., in-memory Qdrant client) to avoid external service dependencies. Sometimes gated behind a `[dev]` optional extra so end users don't pull test deps.

### Live integration test gating

Custom pytest flag (`--run-live`) or marker (`live`) gates tests that hit real upstream services; default test runs stay offline. Lets the same suite serve both unit and live-integration roles without unconditional network calls.

### Branch coverage enforcement

`pytest --cov --cov-branch` for branch-level coverage measurement, beyond statement coverage.

### End-to-end protocol-conformance harness

Dedicated subdirectory (e.g., `/e2e/mcp-server-tester`) that exercises the MCP protocol surface end-to-end. Distinct from unit tests of business logic; tests that the server speaks MCP correctly.

### External agent validation artifacts

Test result files from validating the server against external agent platforms (Amazon Bedrock agents) committed to the repo as evidence of cross-platform compatibility.

### Mock transport layer for protocol-level testing

Library/SDK projects ship mock transport implementations so their tests (and downstream consumers' tests) can exercise protocol message flow without a real stdio/SSE channel. Knit-based code-snippet testing (a Kotlin-specific tooling pattern that tests documented snippets) is a documentation-as-test variant that surfaces here, distinct from explicit testing-module mocks. Appropriate for SDK projects where the transport layer itself is part of the public API.

### In-memory transport for protocol tests

Tests instantiate server and client in the same process and exchange messages via in-memory transport, skipping serialization overhead and process boundaries. Appropriate for verifying protocol-level behavior in isolation.

### MCP Inspector as test driver

`@modelcontextprotocol/inspector` invoked via `npm test` to exercise the server end-to-end through the MCP protocol itself. Common in TypeScript servers; sometimes recommended (rather than wired) for Python servers as a manual debugging aid. Often the only documented testing approach for minimal projects. Appropriate when the value is in protocol-level integration rather than unit-level coverage.

### Vitest (TypeScript / Node)

`npm test` runs Vitest with coverage configured (`npm run test:coverage`); tests under `/tests` configured via `vitest.config.ts`. Often used in Turbo monorepos. Run via pnpm/npm scripts. Standard modern-TS choice; appropriate for TypeScript servers, particularly those that share a monorepo with a JS frontend. Faster modern alternative to Jest; good async ergonomics, TypeScript-native ESM.

### Jest (TypeScript / Node)

Dominant TS choice in older projects; tests under `src/__tests__/` invoked via npm scripts. Standard JS choice. Configuration may be present without specific test-layout details extracted.

### Bun test runner with Vitest compatibility

Bun's built-in test runner running Vitest-compatible specs. Pairs with the dual Node+Bun runtime — same test file works under either runner. Appropriate when the project supports both runtimes and wants to verify both.

### TypeScript noEmit type-check as the test command

`npm test` runs `tsc --noEmit` as the entire test surface. The "tests" check is purely structural (does the project type-check). Appropriate for early-stage projects with no runtime test suite yet; catches type regressions but not behavioral ones.

### Go stdlib testing

Standard `testing` package; `*_test.go` co-located with implementation; integration tests in `e2e/` or `integration_test.go`. The default Go path; no extra framework needed.

### Cargo test / cargo-nextest (Rust)

Implicit via `cargo test`; conventional `tests/` directory under the crate root. cargo-nextest as a faster runner for larger suites, orchestrated through a `Makefile.toml` that also defines `fmt`, `clippy`, `check`, and `clippy-fix` targets.

### Multi-tier Kotlin testing

Dedicated `kotlin-sdk-testing` artifact, `integration-test/` module, `conformance-test/` module, plus snippet-test infrastructure (Knit). Appropriate when the project is a spec-conforming SDK and conformance is a deliverable in its own right.

### Clojure-native testing

Test directory with typical Clojure testing conventions, often using a test-only profile (`tests.edn`, similar) declaring the test runner config separately from the main project. Appropriate within ecosystems where alias-driven tooling is idiomatic.

### Native build-system test target

Tests run via the native build system's test target (`make test` invoking CMake/CTest for the C++ extension).

### `make test` targets

Test invocation wrapped in a Makefile target — typically `make test`, sometimes also `make test-connection` for upstream-reachability smoke tests. Layered over whichever underlying framework runs the tests.

### Recorded HTTP fixtures (cassettes)

Tests run against checked-in HTTP recordings (go-vcr cassettes, similar libraries) so the suite is reproducible offline without upstream credentials. A separate live-mode flag re-records when the upstream API changes. Appropriate when tests need to exercise real upstream API shapes but CI shouldn't pay per-run API costs or require credentials.

### Evaluation harness alongside unit tests

A separate `eval` task that runs scenario-based evaluations against model outputs, distinct from unit tests. Catches behavioral regressions that unit tests can't (e.g., a tool description change degrading model accuracy). Appropriate when the server's value depends on how well models use its tools, not just whether the tools work.

### End-to-end with browser automation

Playwright tests exercise the full stack from a real browser/host through the MCP endpoint. Higher fidelity, slower, more brittle. Appropriate when the deployment includes a web UI alongside MCP.

### Pyramid with web E2E (Playwright + ephemeral DB)

Unit + integration + protocol-level E2E + browser E2E using Playwright against an ephemeral database provisioned per test run. Appropriate for hosted MCP servers with a web UI surface (OAuth consent screens, landing pages) that traditional MCP tests don't exercise.

### Stratified suite with unit + integration + cache + security tiers

Tests split by concern — unit (pure logic, e.g., risk scoring), integration (tool registration and error handling), cache (TTL behavior against an in-process SQLite), security (private-IP blocking, XML-bomb protection). Appropriate when the server has cross-cutting infrastructure (cache, security) that warrants its own test scope.

### Live multi-phase suite against application

Bespoke test harness organized in phases (read-only → destructive → media → AI/ML → advanced) running against a real instance of the integration target. Coverage reported as percent-of-API-methods-exercised rather than line coverage. Appropriate when the server wraps a large, stateful application where mocking would be more code than the harness.

### Separate integration_tests/ directory

Unit tests under `tests/`, real-upstream integration tests under `integration_tests/`. Different invocation paths; integration tests typically gated on CI secrets. Appropriate for project-governed servers where against-real-upstream validation is a separate cost class from unit tests.

### MyPy strict + Bandit security scans alongside tests

In addition to runtime tests, pyproject.toml configures strict static type checking and Bandit security scanning. Appropriate for security-sensitive servers and projects with explicit static-analysis discipline.

### Linter/formatter test gate

Project relies on lint/format/type-check tooling (`ruff`, `black`, `mypy`, `ty`, `biome`, `pyright`) as part of the CI gate; pre-commit hooks enforce locally. Some projects run both `ruff` and `black` (redundant since modern `ruff format` covers most of what `black` did).

### Container-based test stack

Where Docker is the primary deployment artifact, the same image (or a sibling image) hosts the test environment so CI exercises the deployment shape rather than a synthetic one. Cross-role: see *Container artifacts — Docker-Compose backend for end-to-end tests*.

### Dev extras gating test deps

Test dependencies installed via `pip install -e .[dev]` (or equivalent extra). Keeps the runtime install lean.

### `pytest` declared as runtime dependency

Quirk where `pytest` lands under `[project.dependencies]` rather than `[dependency-groups]`. Almost always an oversight rather than a design choice; ships test framework to all consumers.

### No tests / not surfaced

Some servers ship without a test suite; correctness verification is left to manual integration with a host. Common for hobbyist or single-author repos, single-file experimental servers, configs-only repos, and projects whose maintainer relies on manual host testing instead. Other samples don't surface test details in their README — presence of a `tests/` directory or pytest.ini is sometimes the only signal. Absence of test discussion in documentation is itself a corpus-level signal: testing is rarely a marketed feature for MCP servers.

## CI

Automated build, test, and release infrastructure triggered on commits, PRs, or releases.

<!-- adoption-table -->

Adoption — 90 samples exhibit `Sample > CI`.

| Path                                      | Count | Coverage |
| ----------------------------------------- | ----: | -------: |
| GitHub Actions                            |    76 |     84% |
| Monorepo CI inheritance                   |     5 |      6% |
| None / absent                             |     5 |      6% |
| Codecov integration                       |     4 |      4% |
| Build + test + supply-chain scan          |     3 |      3% |
| Release-cut workflow on tag push          |     3 |      3% |
| Documented but not necessarily wired      |     2 |      2% |
| Multi-system CI                           |     2 |      2% |
| Pre-commit hooks                          |     2 |      2% |
| Renovate / Changeset tooling              |     2 |      2% |
| CodeRabbit-style PR review bot            |     1 |      1% |
| GitHub Actions plus dedicated lint config |     1 |      1% |
| OSSF Scorecard                            |     1 |      1% |
| Secret-scan baseline                      |     1 |      1% |
| Turbo (build orchestrator)                |     1 |      1% |
| Vercel preview-per-PR + main deploy       |     1 |      1% |

<!-- /adoption-table -->
### GitHub Actions

`.github/workflows/` directory with one or more workflow files. Universal across the corpus where any CI is present. Used for unit tests on PRs, lint (ruff, eslint, mdformat, biome), type-check (mypy, pyright, tsc), release-binary cross-compilation, container image builds, PyPI/crates.io publishes, dependency audit. Workflows are split by concern (`ci.yml`, `release.yml`, `release-binaries.yml`, `release-container.yml`, `pages.yml`, `golangci-lint.yml`). Per-server projects in monorepos may share workflows at root; standalone projects have their own. Some projects run a quality matrix (ruff/black, mypy, bandit, tests across Python 3.10/3.11/3.12; Biome for webapp components) or Rust toolchain targets via Makefile.toml (fmt, clippy, test, check). Often paired with codecov integration for coverage reporting and badges.

### GitHub Actions plus dedicated lint config

GitHub Actions plus a language-specific linter config checked in (`.golangci.yml`, `.cljstyle`, `clj-kondo`, `.ruff.toml`). Lint runs as a CI step, separate from tests. Appropriate when style and static-analysis enforcement matters and the project wants the lint rules versioned alongside the code.

### Build + test + supply-chain scan

CI pipeline that builds the artifact (Docker image, npm/PyPI package), runs tests, and runs supply-chain scanning (e.g., Trivy for container vulnerabilities). The scan step is treated as a build gate rather than a separate concern; surfaces in security-focused projects.

### Pre-commit hooks

`.pre-commit-config.yaml` runs local checks (lint, format, secret scan) before commit. Appropriate for monorepos where consistency across many sub-packages must be enforced. Often overlaps with CI's lint stage and serves as a local mirror of CI rules. Git hooks via lefthook or similar are an alternative.

### Codecov integration

External coverage reporting service wired into the CI workflow. Coverage tracked with a Codecov badge; PRs can fail when coverage drops.

### Secret-scan baseline

`.secrets.baseline` records known-allowed strings so the scanner doesn't flag them. Appropriate when secret-scanning is part of CI and false positives need a managed allow list.

### OSSF Scorecard

OSSF Scorecard integration emits a security posture rating. Appropriate for projects that want a public security score visible to consumers.

### Renovate / Changeset tooling

Sub-tools for dependency automation (`renovate.json`) and changelog management (`.changeset/`). Common in TypeScript Node projects.

### Monorepo CI inheritance

Sub-server packages in a monorepo inherit the parent's CI and don't ship their own workflows.

### Turbo (build orchestrator)

Turborepo orchestrates per-package builds and tests across a monorepo. Run inside GitHub Actions. Appropriate for monorepos with multiple packages that share dependencies and want incremental, cached builds.

### Multi-system CI

Some vendors run GitHub Actions in addition to a vendor-internal CI (Buildkite). Used when the project needs to test across platform/architecture matrices the vendor's internal CI handles natively while keeping a public surface for outside contributors on GitHub Actions.

### Release-cut workflow on tag push

A workflow triggered specifically by version-tag pushes that builds and uploads release artifacts (cross-platform binaries, container images, npm/PyPI/Docker fanout). Decouples release from CI's normal pass/fail gate. Appropriate when releases are a deliberate event and not every passing build should produce one.

### Vercel preview-per-PR + main deploy

Hosted-service repos use Vercel's per-PR preview deployments; merging to main auto-deploys to production. Appropriate for Next.js-hosted MCP servers where the deployable artifact is the running service.

### Documented but not necessarily wired

The README shows a GitHub Actions YAML example (often because system deps like ffmpeg need an `apt-get install` step) but the actual `.github/workflows/*.yml` may or may not exist. Appropriate as a copy-paste seed for downstream consumers.

### CodeRabbit-style PR review bot

Some projects pair Actions with an automated PR review bot. Appropriate when the project wants AI-assisted review at scale.

### None / absent

No CI configured. Common in early-stage repos, single-author tools, configs-only repos, and remote services (the vendor's hosting pipeline is invisible).

## Deployment topology

The runtime substrate the server is designed to run inside, and the shape of where the server actually runs in production. Cuts across distribution + transport but is its own concern.

<!-- adoption-table -->

Adoption — 15 samples exhibit `Sample > Deployment topology`.

| Path                                                          | Count | Coverage |
| ------------------------------------------------------------- | ----: | -------: |
| Hosted SaaS endpoint                                          |     6 |     40% |
| Local stdio process per session                               |     4 |     27% |
| Self-hosted HTTP server                                       |     4 |     27% |
| Containerized local process                                   |     3 |     20% |
| Edge / serverless deployment (Cloudflare Workers, V8 isolate) |     2 |     13% |
| Published container image (artifact = image)                  |     1 |      7% |
| REPL-resident                                                 |     1 |      7% |
| Serverless (Lambda + API Gateway)                             |     1 |      7% |
| Per-user local process (artifact = binary)                    |     0 |      0% |

<!-- /adoption-table -->
### Local stdio process per session

The server runs as a child process of the MCP host on the user's machine, one process per host session — the host launches the server, communicates over stdio, and tears it down when the session ends. Standard for stdio servers. Appropriate for single-user, local-data, or per-user-credentialed workloads.

### Containerized local process

Host launches `docker run` as the server command; the container is a transparent execution wrapper around the same stdio loop. Appropriate when language runtimes can't be assumed on the host or when bundled native deps make installation painful.

### Hosted SaaS endpoint

The maintainer operates a single (or replicated) deployment users connect to. No install on the user side. Often co-exists with a local stdio mode for self-hosted variants. Appropriate when the upstream resource is shared (public data, cloud APIs the maintainer brokers) or when zero-install ergonomics are decisive.

### Self-hosted HTTP server

Operators deploy the same code as a long-running HTTP service inside their own infrastructure. Same code as the SaaS variant in some products. Appropriate when the operator wants the deployment topology of a SaaS but inside their own perimeter.

### Edge / serverless deployment (Cloudflare Workers, V8 isolate)

The hosted SaaS runs on a serverless edge platform rather than a long-lived server. Server runs on Cloudflare's edge runtime; the deployment artifact is the deployed Worker. Constrains the runtime model — no persistent in-memory state, request-scoped execution. Appropriate when the workload fits the edge runtime's constraints and global low-latency distribution matters. Cross-role: see *Server runtime — TypeScript on Cloudflare Workers*.

### Serverless (Lambda + API Gateway)

Server code runs in Lambda, fronted by an HTTPS API Gateway endpoint. Per-request invocation; cold-start sensitivity; statelessness enforced by the substrate; session state externalized to DynamoDB. Appropriate when the server must be reachable by remote clients and serverless economics fit the workload.

### REPL-resident

Server code runs inside a long-lived REPL process; the host connects to the REPL. Appropriate only when the target ecosystem (Clojure / nREPL) already has REPL-driven development as the dominant idiom.

### Per-user local process (artifact = binary)

The artifact is the binary that runs as a subprocess of the host on the user's laptop. No separate deployment story exists; install equals deploy.

### Published container image (artifact = image)

Pre-built image at a known registry (ghcr.io, AWS public ECR, Docker Hub, vendor registries). Lets users skip the local build. The unit of deployment for projects that present themselves as deployable infrastructure rather than per-user installs; README enumerates targets where it runs (EC2, ECS, EKS, AWS Marketplace). Cross-role: see *Distribution channel — Docker image*.

## Host integration

Which MCP-consuming hosts the server documents direct support for, and how those configs are presented in the README. Constrains documentation surface and onboarding friction.

<!-- adoption-table -->

Adoption — 96 samples exhibit `Sample > Host integration`.

| Path                                                                | Count | Coverage |
| ------------------------------------------------------------------- | ----: | -------: |
| Claude Desktop                                                      |    73 |     76% |
| Cursor                                                              |    34 |     35% |
| VS Code / VS Code Insiders / Visual Studio family                   |    22 |     23% |
| Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment                |    20 |     21% |
| Claude Code                                                         |    16 |     17% |
| Smithery / Glama discovery                                          |    12 |     12% |
| Generic / host-agnostic snippet                                     |    10 |     10% |
| Codex CLI / Copilot CLI / Gemini CLI                                |     8 |      8% |
| Per-host README JSON snippets                                       |     6 |      6% |
| Inspector compatibility called out                                  |     5 |      5% |
| JetBrains IDE                                                       |     5 |      5% |
| No host integration documentation                                   |     5 |      5% |
| `.mcp.json` in project root                                         |     5 |      5% |
| First-party host extension manifest                                 |     4 |      4% |
| Monorepo catalog                                                    |     4 |      4% |
| Multi-host catalog (30+ agents)                                     |     4 |      4% |
| Production reference implementation                                 |     4 |      4% |
| Zed                                                                 |     4 |      4% |
| Cloudflare AI Playground / OpenAI Responses API / OpenAI Agents SDK |     3 |      3% |
| MCPB / DXT bundle manifest                                          |     2 |      2% |
| Vendor-specific companion config                                    |     2 |      2% |
| `.claude-plugin/` directory in repo                                 |     2 |      2% |
| Co-located VS Code extension                                        |     1 |      1% |
| JupyterLab as a host                                                |     1 |      1% |
| LangChain integration                                               |     1 |      1% |
| Native host connector                                               |     1 |      1% |
| NixOS / Home Manager module                                         |     1 |      1% |
| Per-OS path documentation                                           |     1 |      1% |
| Universal installer covering many hosts                             |     1 |      1% |
| Vercel AI SDK native integration                                    |     1 |      1% |
| WSL configuration guidance                                          |     1 |      1% |
| nREPL host                                                          |     1 |      1% |
| Framework-installer wires hosts                                     |     0 |      0% |
| Single canonical host snippet                                       |     0 |      0% |

<!-- /adoption-table -->
### Per-host README JSON snippets

The README ships copy-paste JSON config blocks for each supported host (Claude Desktop, Claude Code, Cursor, Zed, VS Code, Windsurf, Cline, Goose, Junie, Copilot, Factory, Gemini CLI, LM Studio, Kiro, opencode, Qodo Gen, Warp, Codex, Antigravity, Amp, JetBrains, etc.) showing the `command`/`args` shape with minor wrapper differences across hosts. The most common pattern; cheap to add a new host but high user friction. Appropriate when the server targets the broadest possible host audience and the maintainer is willing to maintain per-host examples.

### Single canonical host snippet

One JSON snippet — usually for `claude_desktop_config.json` — with a generic note that other MCP hosts use similar config. Appropriate when the maintainer wants the docs surface small and assumes operators can adapt.

### Per-OS path documentation

The Claude Desktop section enumerates Windows, macOS, and Linux config paths. Appropriate when the install audience is non-developer-heavy and "where is the file" is itself a documentation gap.

### Claude Desktop

JSON `mcpServers` config snippet shown in README, typically pasted into `claude_desktop_config.json` on macOS/Windows. Snippet usually shows the launch command (`npx -y <pkg>`, `uvx <pkg>`, `uv run ...`, `docker run ...`) plus the env-var block. Universal floor for sample servers; nearly every server documents at least this integration. Most-documented host across the corpus. Often paired with MCPB for drag-and-drop install.

### Claude Code

Project-level `.mcp.json` file with per-server entries; `claude mcp add <name> -- <command>` for CLI registration. Less commonly documented than Claude Desktop but appears in monorepo layouts where many servers ship together. Sometimes paired with explicit one-click install buttons or a sibling `skills/` directory shipping Claude Code skills alongside the MCP server; sometimes no first-class wrapper exists and the host is expected to consume the generic MCP surface. A `.claude-plugin/` directory shipped in the repo with a `plugin.json` lets the server distribute itself as a Claude Code plugin alongside its other channels — typically pointing at the hosted HTTP endpoint with a custom header identifying the source. Native support for the `/mcp` flow.

### Cursor

JSON config snippets specific to Cursor's MCP integration (`.cursor/mcp.json` project-scoped, `~/.cursor/mcp.json` global). Some servers explicitly document both levels; transport (stdio vs HTTP) is inferred from whether the entry specifies `command` or `url`. Sometimes documented via "quick-install badge" links that auto-configure, via `.cursor-mcp.json`, or via `.cursor-plugin/` directory at the repo root. Frequently documented alongside Claude Desktop; some vendors render one-click install buttons in the README to optimize for the Cursor user base.

### VS Code / VS Code Insiders / Visual Studio family

`.vscode/mcp.json` entry for the VSCode MCP integration / Copilot Chat consumer, plus README-rendered badges that pre-fill VS Code's MCP integration UI. Visual Studio 2022, IntelliJ IDEA, Eclipse, PyCharm — surfaces in vendor-authored servers (.NET ecosystem) where the host integration ships as an IDE extension via the platform's marketplace. Documented integration path may require a VS Code setting (`chat.agent.enabled: true`). Frequently documented in vendor servers offering broader cross-host coverage.

### JetBrains IDE

Native MCP integration documented per JetBrains product line. Appropriate when the upstream domain (database, language) has a strong JetBrains user base.

### Windsurf / Goose / Qodo Gen / Cline / Kiro / Augment

Same JSON-snippet pattern for other emerging MCP-aware IDEs and agents, or one-click install buttons via URL-protocol deep links. Whether they're documented depends on the author's familiarity; multi-host READMEs name them explicitly. Per-host one-click install URLs in README bypass JSON copy-paste entirely for supported hosts.

### Codex CLI / Copilot CLI / Gemini CLI

Non-Anthropic agent CLIs that consume MCP. `.codex-plugin/` integration manifest in repo root — first-class plugin shape distinct from the MCP server itself. Appropriate when the author wants to ship Codex-native ergonomics rather than relying on Codex's generic MCP consumption, or when the server's user base spans agent ecosystems.

### Zed

Documented as a Zed extension. Less common; sometimes the only sample in a bin to mention it. Appropriate as a long-tail editor audience.

### Multi-host catalog (30+ agents)

README documents support for 30+ different agent platforms with per-agent config snippets. Implies the server is generic enough that it doesn't depend on host-specific features.

### Smithery / Glama discovery

Server entry in the Smithery catalog; install via `@smithery/cli install <name> --client <host>`. Or registered through `glama.json` (Glama). Cross-host distribution mechanism rather than a single-host integration. Cross-role: see *Distribution channel — Smithery registry*.

### Universal installer covering many hosts

A single `install.py` script writes per-host configs to up to 10 MCP client locations in one invocation, eliminating per-host setup steps. Appropriate when the user audience is broad and the author wants to remove the "find your client's config file" step entirely.

### `.claude-plugin/` directory in repo

Project ships a Claude-Code plugin wrapper directory at the repo root, encoding the plugin manifest alongside the code. Distinct from JSON-snippet host config — this packages the project as a discoverable Claude Code plugin.

### `.mcp.json` in project root

A project-local MCP-config file convention used by Claude Desktop and similar hosts that read `.mcp.json` to discover MCP servers tied to a specific project workspace.

### MCPB / DXT bundle manifest

`manifest-dxt.json` provides Claude Desktop-specific extension packaging; `.mcpb` bundles ship as drag-and-drop installs. Appropriate as low-friction installs for non-developer Claude Desktop users.

### nREPL host

The host is itself a running REPL process; the server connects to it. Native to the Clojure ecosystem.

### JupyterLab as a host

Server runs as an extension inside JupyterLab and is configured via the standard Jupyter extension mechanism rather than via a separate MCP host config. Appropriate when the server brokers access to the surrounding application.

### NixOS / Home Manager module

Declarative config entry (an attribute set added to `configuration.nix` or `home.nix`) handles install + activation in one place. Rare among MCP servers; tied to the Nix distribution channel.

### Cloudflare AI Playground / OpenAI Responses API / OpenAI Agents SDK

First-party platform integrations for hosted-only servers, plus documented support for non-MCP-host MCP-consuming runtimes (OpenAI Agents SDK). Documented when the server is platform-specific and the platform's own AI tooling is the natural client, or when the author is positioning the server as ecosystem-agnostic rather than Claude-specific.

### Vercel AI SDK native integration

Server exports a `createToolSchemas()` (or equivalent) function that lets a Vercel-AI-SDK-based app consume the same tool schemas without going through MCP transport — first-class non-Claude integration. Doubles the project as both an MCP server and an SDK.

### LangChain integration

Server documents LangChain consumption (typically via a LangChain MCP adapter). Appropriate when the upstream domain (search, retrieval) is also a common LangChain use case.

### Vendor-specific companion config

A first-party agent surface gets its own dedicated config file shipped with the server (`gordon-mcp.yml` for Docker's Ask Gordon). Distinct from generic host-config because the vendor has shaped the integration deeper than the standard MCP host contract allows.

### First-party host extension manifest

A host-specific manifest file (e.g., `gemini-extension.json`, `.gemini/` directory) declares the integration with a specific host the project has a special relationship with. Appropriate when the project is owned by or aligned with the host's vendor.

### Native host connector

The host has built-in awareness of the server (Claude Desktop's native connector for exa); no manual config is needed. The lowest-friction host integration available, but limited to vendor partnerships that the host's authors have approved.

### Co-located VS Code extension

A parallel VS Code extension (TypeScript) ships in the same repo as the MCP server. Provides a non-MCP integration path alongside MCP. Appropriate when the audience uses VS Code heavily and wants editor integration deeper than MCP would provide.

### Framework-installer wires hosts

The framework's CLI installer registers the server with the target host transparently — no user-facing snippet, the framework knows how to talk to each supported host. Appropriate when committing to a framework that has solved this concern.

### Inspector compatibility called out

`npx @modelcontextprotocol/inspector <command>` for manual testing. Documented as a verification tool rather than a host per se, but often listed alongside hosts as part of the integration surface.

### WSL configuration guidance

Documentation specifically addressing Windows users running the host through WSL — environment-bridging concern that some servers call out explicitly.

### Production reference implementation

Instead of (or in addition to) host snippets, the README points to a real-world server built on the SDK as a reference. Appropriate for SDKs where the right "integration example" is a complete project, not a config block.

### Generic / host-agnostic snippet

Stdio-launch instructions framed for any compliant MCP host without naming specifics. Default fallback when authors don't want to enumerate hosts; provides a generic `mcpServers` JSON entry presumed portable across MCP clients.

### Monorepo catalog

Sub-server READMEs defer host-integration examples to the parent monorepo's catalog page.

### No host integration documentation

SDK-style or library projects skip host-specific docs because the consumer is another program, not a host. Examples and library docs replace host snippets.

## Observability

How the server surfaces what it's doing for operators and debuggers. Splits between agent-facing logs (visible in MCP client) and ops-facing logs (disk/stdout/external systems).

<!-- adoption-table -->

Adoption — 47 samples exhibit `Sample > Observability`.

| Path                                                  | Count | Coverage |
| ----------------------------------------------------- | ----: | -------: |
| None / unspecified                                    |    11 |     23% |
| Env-var-controlled log level                          |     7 |     15% |
| Stderr logging (convention / SDK default)             |     5 |     11% |
| Change-notification channels / JSON-RPC notifications |     4 |      9% |
| loguru (Python)                                       |     4 |      9% |
| Health endpoint                                       |     3 |      6% |
| Pluggable logger sinks                                |     3 |      6% |
| File-based logging                                    |     2 |      4% |
| OpenTelemetry instrumentation                         |     2 |      4% |
| Pino / Winston structured logging (Node)              |     2 |      4% |
| Standard library `logging` (Python)                   |     2 |      4% |
| Suppressed stdout / discipline-only                   |     2 |      4% |
| `--verbose` flag                                      |     2 |      4% |
| Audit logging for compliance modes                    |     1 |      2% |
| CloudTrail audit logging                              |     1 |      2% |
| CloudWatch via Lambda                                 |     1 |      2% |
| Companion monitoring dashboard                        |     1 |      2% |
| Container logs (stdout/stderr)                        |     1 |      2% |
| Debug toggle + log file path                          |     1 |      2% |
| File-system artifacts as side effects                 |     1 |      2% |
| Prometheus metrics                                    |     1 |      2% |
| Request context tracking for audit                    |     1 |      2% |
| Request lifecycle hooks for telemetry                 |     1 |      2% |
| Rotating JSON audit log on disk                       |     1 |      2% |
| Sentry integration                                    |     1 |      2% |
| Worker logs (platform-native)                         |     1 |      2% |
| `rich`-decorated stdlib logging (Python)              |     1 |      2% |
| `--interactive` REPL mode                             |     0 |      0% |

<!-- /adoption-table -->
### Stderr logging (convention / SDK default)

Most servers log to stderr by default — implicit in stdio transport since stdout is the protocol channel. Format and levels are typically not documented. The host captures stderr if it cares. Configurable level via `FASTMCP_LOG_LEVEL` env var when FastMCP is in use. Appropriate as the default; explicit only when the project deviates.

### Suppressed stdout / discipline-only

Stdio servers explicitly suppress progress messages and any stdout output that isn't JSON-RPC; the `print` policy is sometimes documented as zero-tolerance because a single stray print breaks the protocol. Logging is silent or routed to stderr. Appropriate (in fact required) for any stdio server.

### Standard library `logging` (Python)

Python's stdlib `logging` module, default handlers. Minimal but ubiquitous.

### loguru (Python)

Python `loguru` library used for application logging — replacement logging library favored for ergonomics, structured output, formatting, and rotation without configuring stdlib logging by hand. Common in awslabs-pattern servers. Sometimes paired with `python-json-logger` for JSON-formatted log records — dual logging paths in one server, presumably one for human-readable dev output and one for ingest.

### `rich`-decorated stdlib logging (Python)

`rich` library decorating stdlib logging output. Same posture as Pino on the Python side.

### Pino / Winston structured logging (Node)

Pino (Node) for structured logging, often paired with file rotation and a configurable log level via env var. Winston-based logging configured at hosting layer with configurable levels for Node/Next.js hosted services. Appropriate when the server runs as a long-lived process or in production where log searchability matters.

### Env-var-controlled log level

A single env var (e.g., `PERPLEXITY_LOG_LEVEL`, `MCP_REDIS_LOG_LEVEL`, `FASTMCP_LOG_LEVEL`) sets log severity at startup, with standard Python/Node logging defaults for destination and format. Most common observability surface in the corpus. Appropriate for stdio servers where logs go to stderr and the host displays them.

### Debug toggle + log file path

Pair of env vars — a boolean debug flag (`MCP_DEBUG`) plus a log file destination (`MCP_LOG_FILE`). Separates "verbose mode" from "where the verbose output goes." Appropriate when the server runs detached from an interactive host and logs need to land somewhere persistent.

### `--verbose` flag

Boolean CLI flag escalating log verbosity at launch.

### File-based logging

Logs to a file in the user's home directory (`~/<server>.log`). Forced by stdio transport, where stdout belongs to the JSON-RPC frame and any stray write corrupts the protocol. The log file is the only observability surface short of attaching a debugger.

### Pluggable logger sinks

Server picks logger destinations from a list (`disk`, `mcp`, `stderr`) controlled by env var (`LOGGERS`). `mcp` sink emits log entries to the connected client. Appropriate when the operator wants to choose between agent-visible and ops-visible logs per deployment.

### File-system artifacts as side effects

The server writes logs and outputs to local directories (`./logs/`, `./charts/`) and returns paths to the caller rather than data. Doubles as observability (the operator inspects the files post-hoc). Appropriate when outputs are large binary artifacts that don't fit in tool responses anyway.

### Container logs (stdout/stderr)

When the server runs in a container or in HTTP mode, stdout is free for log output and the container runtime captures it. Pairs naturally with cluster-level log aggregation.

### CloudWatch via Lambda

Implicit logging to CloudWatch Logs because the server runs in Lambda; X-Ray tracing can layer on. Appropriate when the deployment substrate provides a logging tier the server inherits for free.

### CloudTrail audit logging

Audit-tier logging (who called what tool when) captured in CloudTrail rather than application logs. Appropriate when the server's calls have compliance significance and a separate audit trail matters.

### Worker logs (platform-native)

Cloudflare Workers' built-in log surfacing via the dashboard. Not a self-hostable layer; the platform owns it. Appropriate only for Workers-deployed servers.

### Rotating JSON audit log on disk

Structured JSON log file with rotation (e.g., 50 MB, 5 backups) at a known location (`~/.cve-mcp/audit.log`). Fields include timestamp, tool name, parameters, duration, cache-hit status. API keys and response payloads explicitly redacted. Appropriate for security-sensitive servers where audit trail is itself a deliverable.

### Audit logging for compliance modes

Logger captures security events explicitly tied to compliance regimes (GDPR, HIPAA modes). Appropriate when the server claims compliance posture and needs to demonstrate audit retention.

### Sentry integration

Errors forwarded to Sentry for centralized triage. Appropriate for hosted services with on-call teams.

### Prometheus metrics

Optional metrics endpoint enabled via an install extra (`[prometheus]`). Appropriate when the server is deployed in observable infrastructure that already scrapes Prometheus metrics; gated behind an extra to avoid imposing on users who don't need it.

### OpenTelemetry instrumentation

OTel API + SDK as core (or optional) dependency, emitting traces and metrics to whatever collector the operator wires up. Sometimes baked into core deps so every install ships observability; sometimes optional. Appropriate for production-grade servers where the operator is expected to integrate with an observability stack.

### Health endpoint

An HTTP endpoint (e.g., `/ping` returning "pong", `/health` for liveness probes). Only meaningful in HTTP-mode deployments; appears where the server is expected to run behind a load balancer or orchestrator. May be exposed via an optional separate monitoring server (HTTP transport only).

### Request lifecycle hooks for telemetry

The SDK exposes hooks at request-start, request-complete, error so applications can wire OpenTelemetry, metrics, or logging without modifying SDK code. Pairs with recovery middleware that catches handler panics so a single bad tool call doesn't crash the process. Appropriate when the server runs as a long-lived service and the operator needs to observe across requests.

### Request context tracking for audit

Per-request structured context (request ID, session, principal) attached to every log line so audit trails can reconstruct who did what. Appropriate when the server performs mutations (file writes, git commits, DB execution) and the operator needs accountability.

### Change-notification channels / JSON-RPC notifications

Per-client notification streams for updates to tool/resource/prompt lists, surfaced via the SDK as event channels. Server emits MCP-protocol notifications when tool/resource availability changes at runtime, plus startup logs of connection details and tool initialization. Indirectly observable but primarily a feature for reactive client UIs. Appropriate when the underlying domain emits changes the client should re-render against, or when capabilities are dynamic (e.g., REPL state changes which tools are valid) and the host needs to refresh its view.

### `--interactive` REPL mode

A CLI flag that drops the server into a terminal REPL for direct query inspection, doubling as a debug surface. Unusual — most servers assume MCP Inspector is the only interactive debugging path. Appropriate when the server's domain (e.g., crawler-archive search) benefits from quick local exploration before MCP integration.

### Companion monitoring dashboard

Separate web app (Vite + Uvicorn on dedicated ports) ships in the same repo for monitoring and control. Distinct process, distinct ports, not bundled into the MCP server itself. Appropriate when the server has long-running state worth visualizing and the author wants admin tooling beyond logs.

### None / unspecified

Project doesn't document logging beyond default stdout/stderr; observability is whatever the language/SDK defaults provide, with no project-level shaping. Appropriate for early-stage or single-user-stdio servers where the host's own logging is sufficient. A widespread gap; not so much a chosen path as an absent one.

## Caching and rate-limiting infrastructure

Cross-cutting modules inside the server that aren't tools but mediate how tools interact with upstreams.

<!-- adoption-table -->

Adoption — 5 samples exhibit `Sample > Caching and rate-limiting infrastructure`.

| Path                                       | Count | Coverage |
| ------------------------------------------ | ----: | -------: |
| Auto-cleanup of temporary export artifacts |     2 |     40% |
| SQLite TTL cache                           |     2 |     40% |
| Token-bucket rate limiter                  |     2 |     40% |
| Circuit breaker for external calls         |     1 |     20% |

<!-- /adoption-table -->
### SQLite TTL cache

In-process SQLite database holds per-call cached responses with TTL. Cache-hit status surfaces in audit log. Appropriate when upstream APIs have rate limits or latency that warrant caching, and when the cache should survive process restarts.

### Token-bucket rate limiter

Explicit rate-limiter module for upstream throttling (e.g., NVD's published quota). Appropriate when one upstream's quota is the binding constraint and naive request fan-out would exhaust it.

### Circuit breaker for external calls

Circuit-breaker pattern wrapping external API calls so a degraded upstream doesn't cascade into server failure. Appropriate when the server has many upstreams and partial degradation is acceptable.

### Auto-cleanup of temporary export artifacts

Server emits resources holding exported data and deletes them after a TTL (default 5 minutes). Appropriate when the server produces transient artifacts that shouldn't accumulate.

## Repository layout

How the codebase is organized across packages and deployment artifacts. Constrains contribution patterns and what can be released independently.

<!-- adoption-table -->

Adoption — 104 samples exhibit `Sample > Repository layout`.

| Path                                                         | Count | Coverage |
| ------------------------------------------------------------ | ----: | -------: |
| Single-package src-layout                                    |    35 |     34% |
| Single-package source (language-conventional)                |    16 |     15% |
| Single-package, organized subdirectories                     |     6 |      6% |
| Single-file script / monolith                                |     5 |      5% |
| Monorepo of namespace-prefixed packages                      |     4 |      4% |
| Single Rust crate                                            |     4 |      4% |
| Single-package flat layout                                   |     4 |      4% |
| Monorepo with multiple published packages                    |     3 |      3% |
| Single-package with dual-ecosystem wrapper                   |     3 |      3% |
| Cross-language monorepo / mixed-language layout              |     2 |      2% |
| Hosted-service layout (Next.js app + mcp-src + lib)          |     2 |      2% |
| Library with subdirectories                                  |     2 |      2% |
| Monorepo of independent servers                              |     2 |      2% |
| Single-package plus sibling host integrations                |     2 |      2% |
| Single-package with auxiliary folders                        |     2 |      2% |
| Turbo + pnpm monorepo                                        |     2 |      2% |
| Bare-script layout                                           |     1 |      1% |
| Clojure project layout                                       |     1 |      1% |
| Configs-only                                                 |     1 |      1% |
| Domain-per-module decomposition                              |     1 |      1% |
| Gradle multi-module / Maven multi-artifact monorepo          |     1 |      1% |
| Monorepo sub-package                                         |     1 |      1% |
| Monorepo with per-server subdirectories and one PyPI package |     1 |      1% |
| Multi-directory single-repo (ancillary services)             |     1 |      1% |
| Polylith components (Clojure)                                |     1 |      1% |
| Server-framework sub-package                                 |     1 |      1% |
| Sibling-package factoring                                    |     1 |      1% |
| Single-package with `.changeset/`                            |     1 |      1% |
| Single-package with embedded test substrate                  |     1 |      1% |
| Umbrella consolidation                                       |     1 |      1% |

<!-- /adoption-table -->
### Single-package src-layout

`src/<package>/` for source, `tests/` for tests, single `pyproject.toml` (or `package.json`). Optionally `examples/`, `dev/`, `docs/`, `agents/`, `.github/`. Modern Python default and the FastMCP reference shape — the explicit `src/` layout prevents accidental imports from the project root during testing. Same shape across Python, TypeScript, and other runtimes. Appropriate for servers that wrap one upstream service and ship one distributable package.

### Single-package, organized subdirectories

One package manifest, code split into purpose-named subdirectories (`src/`, `core/`, `client/`, `server/`, `transport/`, `examples/`, `e2e/`). Appropriate when the codebase is one shipping unit but internally segregated by concern.

### Single-package source (language-conventional)

One module/package in conventional language layout (Go: `cmd/`, `pkg/`, `internal/`, `build/`, `docs/`; TypeScript: `app/`, `src/`; npm: `package.json`, `bin/`, optional `dist/`). The simplest organization. Appropriate when one server is one product.

### Single-package flat layout

Server file at repo root with optional `src/<helpers>/`. Common for "hackable" community servers where the entire server may fit in a few hundred lines. Appropriate for small, single-author projects where the overhead of src-layout would be ceremony.

### Single-package with auxiliary folders

One top-level package directory plus siblings for tests, deploy artifacts, scripts, custom lint rules, API docs. Appropriate when the project is one server but has substantial supporting infrastructure.

### Single-file script / monolith

The entire server is one `.py` (or `.js`, etc.) file, sometimes very large (e.g., ~112 KB), with a `requirements.txt` or no manifest. The minimum viable layout. Appropriate when the server's surface is small enough that splitting adds no value, for prototypes, demonstrations, and projects optimizing for "one file to read"; trades off against modular testability.

### Bare-script layout

One or two `.py` files at repo root with `requirements.txt`/`pyproject.toml` beside them. Easy to read; awkward to package for PyPI.

### Single Rust crate

`Cargo.toml` at root, source under `src/main.rs`, with `/examples` and `/e2e` subdirectories for samples and conformance tests.

### Clojure project layout

Standard Clojure layout with `src/`, `test/`, `doc/`, `resources/`, `deps.edn`, plus extensive root-level documentation files (README, PROJECT_SUMMARY, CHANGELOG, CONFIG, FAQ, BIG_IDEAS, LLM_CODE_STYLE).

### Domain-per-module decomposition

Source organized as modules per integration domain (account, workspace, run, plan) when the server wraps a wide REST API. Each module owns its own tools and types. Appropriate when the wrapped API has natural domain divisions and the codebase would otherwise be one large file.

### Single-package with dual-ecosystem wrapper

Python package as the canonical implementation with a thin npm wrapper that invokes the Python entry point under the hood. Two `package.json` / `pyproject.toml` roots in the same repo. Appropriate when the author wants to reach both ecosystems' install habits without maintaining two separate codebases.

### Single-package with `.changeset/`

Single-package layout but with formal changeset-based release management (common in TS Node projects).

### Single-package with embedded test substrate

Single-package layout that also bundles a docker-compose stack for end-to-end testing of upstream services.

### Multi-directory single-repo (ancillary services)

The repo holds the MCP server alongside related but distinct concerns: a web monitoring dashboard (its own build pipeline, often Vite + Uvicorn), a packaging directory, scripts, and examples. The server is one product among several in the same repo. Appropriate when the author wants ops/monitoring artifacts to ship alongside the server but with distinct build and run paths.

### Monorepo of independent servers

Many subdirectories, each a standalone MCP server with its own Dockerfile, scripts, and tests. A `Dockerfile.template` at root acts as scaffolding for adding new servers. Repo root holds shared tooling; each server lives in `src/<name>/` (or `servers/<name>/`) with its own manifest, Dockerfile, and README. Different servers may use different languages side by side (TS + Python peers). The repo as a whole is the contribution surface; individual servers are the deployment units. Appropriate when the repo is a curated reference set or a vendor's portfolio of related servers.

### Monorepo of namespace-prefixed packages

Many sub-packages under `src/<name>/` each with their own `pyproject.toml`, all sharing a namespace prefix (e.g., `awslabs.*`). Central dev tooling at root (ruff, pre-commit, secrets baseline). Each sub-package independently published and installable. Appropriate when one organization ships many related servers and wants consistent tooling without combining them into one package.

### Monorepo sub-package

`src/<sub-server>/` directory inside a parent multi-server monorepo, each sub-package with its own `pyproject.toml`, console script, and PyPI release. Consumers install one sub-server without pulling siblings.

### Monorepo with per-server subdirectories and one PyPI package

`servers/<server-name>/` subdirectories each with their own README and `pyproject.toml`, but the root publishes one PyPI package that dispatches to children via Hatch `force-include`. Appropriate for thematically-linked server collections (scientific computing) where users want one install entry but author wants per-server isolation.

### Umbrella consolidation

Originally per-service repos collapsed into a single org-level monorepo with `/servers/<name>/` subdirectories and `/core/` shared libraries. The consolidation pattern surfaces with a transitional period — original repos archived with redirect notices to the umbrella, sometimes with a multi-month gap between code-freeze and formal repo archival as the redirect stabilizes.

### Single-package plus sibling host integrations

Core MCP server in `src/<name>/` plus sibling directories shipping integrations for non-MCP hosts (`.codex-plugin/`, `skills/` for Claude Code). Appropriate when the author wants to ship native plugin formats for multiple ecosystems from one repo rather than relying on generic MCP consumption.

### Server-framework sub-package

Sub-package within an MCP-server monorepo that is itself a library for building servers, not a server. Breaks the "every sub-package is a server" assumption of the monorepo and represents a structural category for infrastructure-tier artifacts.

### Sibling-package factoring

Project depends on a separate PyPI/npm package owned by the same author that holds extracted concerns (e.g., `jupyter-mcp-tools` holds the tool definitions while `jupyter-mcp-server` holds the runtime). Appropriate when the extracted piece has independent reuse value beyond the immediate server.

### Turbo + pnpm monorepo

Multiple packages under `packages/` or domain folders, shared `@repo/<name>` workspace packages, Turbo orchestrating per-package builds and tests. Appropriate when the project ships multiple related servers (e.g., 14 domain Workers) that share scaffolding.

### Monorepo with multiple published packages

Multiple publishable packages coexist in one repo (`@scope/sdk`, `@scope/mcp`, `@scope/integration`, etc.) coordinated by pnpm-workspace.yaml or similar workspace tooling; changesets handles version bumps and changelog generation across packages. Used when the project is "MCP plus other agent-integration surfaces" and treats MCP as a peer to SDKs and framework adapters. Expanded layout includes `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n` directories alongside `/packages`.

### Library with subdirectories

Go library layout: root-level `client.go`/`server.go`/`doc.go` plus subdirectories for `/bridge`, `/client`, `/server`, `/internal`, `/docs`, `/example`. Suited to SDK-style projects where the surface is multiple consumable packages.

### Gradle multi-module / Maven multi-artifact monorepo

Repo holds multiple build modules (`kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, umbrella artifact, plus `samples/`, `integration-test/`, `conformance-test/`, `buildSrc/`). Appropriate when the SDK ships multiple consumable artifacts but shares a build pipeline.

### Cross-language monorepo / mixed-language layout

One repo holds first-class peers in different language stacks, each with its own packaging, distribution channel, and Docker image — for example, a primary-language source tree (Python under `src/`) alongside a parallel subproject in another language for editor integration (TypeScript under `vscode-extension/`). Appropriate when the project is a reference set demonstrating multiple SDKs against one spec, or when one product needs both an MCP surface and a native editor extension surface.

### Polylith components (Clojure)

Clojure's Polylith style — `bases/`, `components/`, `projects/` separating reusable components from project-specific bases. Heavyweight modular architecture. Appropriate when components are genuinely reused across multiple deliverables.

### Hosted-service layout (Next.js app + mcp-src + lib)

Top-level Next.js `landing/` (or app/), `mcp-src/` for tool/handler logic, `lib/` for shared OAuth/config helpers, `tests/` for stratified suites, `.claude/skills/` for Claude Code integration. Appropriate when the deliverable is a hosted service rather than a published package.

### Configs-only

No `src/`. The repo carries `.mcp.json`, per-host config files, and possibly companion `commands/` and `skills/` directories for client-side artifacts. Appropriate when the server is remote and the repo's job is to deliver client-side configuration.

## Safety and security posture

How the project constrains potentially-dangerous operations and defends against threats. Distinct from authentication; this is about what can be done once authenticated and what defensive measures the server applies. Cross-role: see *Capability surface — Capability gating flags*.

<!-- adoption-table -->

Adoption — 31 samples exhibit `Sample > Safety and security posture`.

| Path                                           | Count | Coverage |
| ---------------------------------------------- | ----: | -------: |
| Read-only by default with explicit write flag  |    11 |     35% |
| Destructive-action gating flag                 |     3 |     10% |
| None / not surfaced                            |     3 |     10% |
| Workspace path enforcement (canonicalization)  |     3 |     10% |
| Explicit non-security stance                   |     2 |      6% |
| Hardened-by-default container posture          |     2 |      6% |
| Lockdown / content-filter mode                 |     2 |      6% |
| AST validation with import allowlist           |     1 |      3% |
| Anti-multi-tenancy disclaimer                  |     1 |      3% |
| Blacklist-filtered code execution              |     1 |      3% |
| Capability-scoped tool exposure (install-time) |     1 |      3% |
| Destructive-tool elicitation list              |     1 |      3% |
| Dry-run config dump                            |     1 |      3% |
| In-process safety enforcement via parsing      |     1 |      3% |
| Index-scan rejection                           |     1 |      3% |
| Mode parameter for plan-vs-execute             |     1 |      3% |
| MseeP.ai security badge                        |     1 |      3% |
| Per-tool auto-approve gating                   |     1 |      3% |
| Sandbox-mode default                           |     1 |      3% |
| Temporary-user lifecycle with TTL              |     1 |      3% |
| Tool-layer query validation                    |     1 |      3% |
| defusedxml for XML hardening                   |     1 |      3% |
| MCP Roots-driven scope                         |     0 |      0% |
| Migration prepare/commit pattern               |     0 |      0% |
| Path/repo allowlist as access control          |     0 |      0% |

<!-- /adoption-table -->
### Read-only by default with explicit write flag

Mutation tools registered but hidden behind a launch flag (`--enable-write-tools`, `--write-access`) or env-var feature flag (`READ_ONLY_TOOLS`); inverse forms (`--read-only`, `READ_ONLY=true`) suppress every mutating tool. Author's default posture is "no surprise mutations." The remaining surface is the safe-by-default subset. Conservative posture; rare among MCP servers, which more commonly ship full capabilities unconditionally. Reduces blast radius of an LLM accidentally invoking a destructive operation. Appropriate when the upstream is mutation-capable (issue trackers, source control, filesystems, mutation-capable databases) and accidental writes are damaging.

### Destructive-action gating flag

A CLI flag or env var (e.g., `--disable-destructive`, `ENABLE_DELETE_TOOLS`) suppresses tools that mutate or destroy state. May be implemented as a single read-only switch or as orthogonal two-axis flags (read-only + enable-delete) recognizing that delete is more dangerous than other writes and deserves its own gate. Two-step opt-in for destructive surface; finer-grained than the binary read-only knob common elsewhere (`*_ALLOW_WRITE_ACCESS` plus a separate `*_ALLOW_DROP`). Appropriate when the server's tool surface contains a clear destructive subset (kubectl delete, scale-down operations) or when the integration target's API mixes safe writes with irreversible destructive operations.

### Sandbox-mode default

Server defaults to a sandbox/paper-trading mode (e.g., `ALPACA_PAPER_TRADE=true`); production mode is opt-in. Particularly relevant for finance/trading servers where misfires have monetary consequences.

### Per-tool auto-approve gating

Operators mark specific tools as safe to run without per-call confirmation, leaving the rest gated. Granular trust boundary at the tool level. Appropriate when the tool catalog mixes safe and dangerous operations and the operator wants asymmetric trust.

### Destructive-tool elicitation list

Specific tools (drop-database, drop-collection) are flagged as `CONFIRMATION_REQUIRED_TOOLS`; invoking one triggers an MCP elicitation requesting human confirmation before execution. Appropriate as a per-tool safety rail beyond a coarse read-only flag — agents can invoke destructive tools but the human is brought into the loop.

### Lockdown / content-filter mode

A flag that filters content from public/untrusted upstream resources before returning it to the agent. Layered over tool selection — operates regardless of which tools are enabled. Appropriate when the agent will traverse untrusted content and the project wants a safety envelope on what reaches the model.

### Tool-layer query validation

The server validates inputs at the tool layer (e.g., SELECT-only enforcement, row-count caps) rather than relying on database-level controls. Defense in depth. Appropriate when the upstream is a general-purpose data store that the project wants to constrain to a safer subset.

### AST validation with import allowlist

User-supplied Python code is parsed to AST, validated against an explicit allowlist of permitted imports (`boto3`, `operator`, `json`, `datetime`, `pytz`, `dateutil`, `re`, `time`), and only then executed. Appropriate for code-as-tool architectures where the LLM authors small snippets server-side. Trust depends entirely on the allowlist's tightness. Cross-role: see *Capability surface — Single code-execution tool with sandbox*.

### In-process safety enforcement via parsing

Server parses inbound payloads before forwarding (e.g., parses SQL with `pglast` to reject COMMIT/ROLLBACK in restricted mode) rather than relying on the upstream system's own permissions. Appropriate when the upstream system's permission model is too coarse (e.g., DB role) and the operator wants finer gating per-tool-call. Constrains the parser's correctness — anything it misses is a security gap.

### Blacklist-filtered code execution

The server accepts user-submitted code (e.g., pandas expressions) and filters dangerous operations via a string-level denylist. Resource accounting via `psutil`. A known-fragile approach acknowledged as such; the alternative (process isolation, restricted exec) is not used. Appropriate when the convenience of in-process execution outweighs the risk of denylist gaps.

### Capability-scoped tool exposure (install-time)

Risky tool families (filesystem write, vision-coordinate clicks, PDF generation) are gated behind `--caps=<group>` opt-in. The server runs without them by default. Appropriate when one server image needs to serve both restricted and unrestricted use cases without forking. Cross-role: see *Capability surface — Capability gating via tool subsets at install time*.

### Path/repo allowlist as access control

The server accepts a directory or repository path at launch and refuses operations outside it, validating that requested paths stay within configured root directories. Pairs with auto-cleanup (export files deleted after response is encoded) to prevent disk bloat and cross-tenant leakage on shared machines. No identity check, just scope clamping. Appropriate when the only meaningful restriction is "what subtree can be touched," and whenever the tool surface accepts user-controlled paths.

### Workspace path enforcement (canonicalization)

Single-user but with explicit workspace-root boundaries enforced by canonicalizing paths (`os.path.realpath`) and rejecting access outside an allow-listed root. Path-traversal defense that lets the server operate on local files while bounding the blast radius. Cross-role: see *Multi-tenancy — Workspace-scoped sandboxing within a single tenant*.

### MCP Roots-driven scope

Same allowlist idea but the scope comes from the host via MCP Roots messages, refreshable at runtime. Appropriate when the host is itself authoritative about user intent (open project, current workspace).

### defusedxml for XML hardening

Library swapped in for stdlib XML parsing to defend against XML bomb / XXE attacks. Appropriate when the server consumes XML from untrusted upstreams (security feeds, public APIs).

### Temporary-user lifecycle with TTL

Server auto-provisions short-lived database users on every connection (default 4-hour TTL) instead of using a long-lived credential. Appropriate when the upstream supports user provisioning via API and the deployment wants minimal blast radius per session.

### Hardened-by-default container posture

Dockerfile baseline includes non-root user, dropped Linux capabilities, read-only filesystem mounts, resource limits. Surfaces in security-focused projects where the wrapped CLI tools are themselves attack surface. Cross-role: see *Container artifacts — Hardened-by-default container posture*.

### Dry-run config dump

`--dryRun` flag prints resolved config and exits without booting the server. Appropriate for verifying environment-merge behavior across env / CLI / file sources before committing to a long-running process.

### Index-scan rejection

`--indexCheck` flag rejects database queries that would scan without an index. Appropriate as an unusual safety posture against agent-induced load on production databases.

### Migration prepare/commit pattern

Server exposes `prepare_migration` and `complete_migration` tools so agents can stage schema changes for human review before execution. Appropriate when the upstream supports branching (Neon-style) and humans should be the apply-step authority.

### Mode parameter for plan-vs-execute

Single tool exposes multiple output modes via a parameter (e.g., `mode: manifest|download|script` for granule downloads). Lets the model preview what would happen before committing to execution. Appropriate when the underlying operation is expensive or irreversible and the user benefits from a dry-run.

### Anti-multi-tenancy disclaimer

README explicitly states "NOT designed for multi-tenant environments." Documents the boundary rather than letting users assume.

### Explicit non-security stance

The README states the server is "not a security boundary" and provides escape hatches (`--allow-unrestricted-file-access`) rather than enforcement. Appropriate when the threat model assumes a trusted caller and the operator opts in to risky modes deliberately.

### MseeP.ai security badge

Third-party MCP-server security-assessment badge in README. Not Claude-Code-specific but signals an emerging ecosystem of MCP-server certification.

### None / not surfaced

Many projects ship full capabilities unconditionally. Appropriate when the upstream is read-only or the tool surface is genuinely safe.

## Domain logic and embedded intelligence

Compute the server performs beyond exposing raw upstream operations — analytical layers, embedded LLM calls, optimization, visualization, and curated workflow scaffolds.

<!-- adoption-table -->

Adoption — 10 samples exhibit `Sample > Domain logic and embedded intelligence`.

| Path                                                 | Count | Coverage |
| ---------------------------------------------------- | ----: | -------: |
| Embedded RAG / retrieval pipeline                    |     3 |     30% |
| Deterministic optimization layered on top of raw ops |     2 |     20% |
| In-server LLM client                                 |     2 |     20% |
| Pass-through tool wrappers                           |     2 |     20% |
| Domain-specific terminology service integration      |     1 |     10% |
| Visualization synthesis                              |     1 |     10% |
| None (pure tool-caller)                              |     0 |      0% |
| Workflow scaffolding via MCP prompts                 |     0 |      0% |

<!-- /adoption-table -->
### Pass-through tool wrappers

Tools map 1:1 onto upstream API operations (Docker SDK calls, NASA Earthdata search, Perplexity API, Jupyter kernel ops, raw SQL execution). Server's job is shape translation and credential management, not domain logic. Appropriate as the default; lowest implementation cost.

### Deterministic optimization layered on top of raw ops

Server adds analytical computation that goes beyond exposing the upstream system — workload compression, hypothetical index simulation (hypopg), Pareto-front cost-benefit selection, greedy search adapted from published algorithms. The MCP layer becomes a delivery vehicle for embedded research. Appropriate when the underlying system supports introspection (pg_stat_statements, EXPLAIN) and the author wants to encode performance expertise in tool form.

### Workflow scaffolding via MCP prompts

Server uses MCP prompts as orchestration primitives, packaging multi-step natural-language workflows (docker-compose orchestration) rather than just exposing atomic tools. Appropriate when there's a complex, repeated workflow worth canonizing. Cross-role: see *Capability surface — Tools plus resources plus prompts*.

### In-server LLM client

The server holds API credentials for an LLM provider (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) and an env var (`EMBEDDED_AGENT_PROVIDER`) selecting the provider. Tool implementations can invoke the LLM internally for aggregation or summarization. Unusual — most MCP servers are pure tool-callers. Appropriate when post-processing of upstream data into LLM-friendly form is itself an LLM-shaped task.

### Visualization synthesis

The server generates images (charts, maps) for the calling LLM to interpret rather than returning raw data. Transforms data-fetch tools into visualization-aware tools. Appropriate when the data is more useful to the model as an image than as numbers.

### Embedded RAG / retrieval pipeline

Server bundles an embedding model, vector store, document parser, and retrieval logic in-process. Tool calls run inference and similarity search inside the server rather than delegating to an external RAG service. Sharply increases the server's footprint and dependency surface but provides domain-aware retrieval for documents the upstream doesn't pre-index. Cross-role: see *Capability surface — Embedded RAG / retrieval pipeline*.

### Domain-specific terminology service integration

Servers fronting healthcare APIs integrate domain ontologies (LOINC); a pattern likely to recur in legal (Westlaw taxonomies), education (curriculum standards), finance (ticker/ISIN). The terminology service is a distinct upstream the server bridges alongside the primary API.

### None (pure tool-caller)

The server only calls upstream services and passes results back. The standard pattern. Appropriate as the default.

## Extension points

Mechanisms the server exposes for users to modify behavior without forking.

<!-- adoption-table -->

Adoption — 3 samples exhibit `Sample > Extension points`.

| Path                             | Count | Coverage |
| -------------------------------- | ----: | -------: |
| Middleware module slot           |     2 |     67% |
| Per-tool enablement file         |     1 |     33% |
| Runtime tool registration API    |     0 |      0% |
| User-publishable tools meta-tool |     0 |      0% |

<!-- /adoption-table -->
### Middleware module slot

Env var (`MCP_MIDDLEWARE_MODULE`) names a Python module that intercepts FastMCP protocol events (tool calls, resource reads, prompts, listings) and can mutate context state (e.g., per-request connection overrides) or implement cross-cutting concerns (logging, tracing, performance measurement). The closest thing in the corpus to a true plugin architecture for an MCP server.

### Per-tool enablement file

JSON config file toggles individual tools without code changes. Lets deployers shrink the LLM-visible surface for safety or focus, and lets the same server image serve multiple deployment profiles. Cross-role: see *Configuration delivery — Per-tool enablement file*.

### Runtime tool registration API

Server exposes a programmatic API for adding tools to a running server, decoupling tool-set definition from source. Cross-role: see *Capability surface — Capability authoring style*.

### User-publishable tools meta-tool

Server provides a meta-tool (`mcp_publish_tool`) that lets the user register new tools at runtime. Cross-role: see *Capability surface — User-publishable tools*.

## Developer ergonomics

In-repo tooling that supports development of the server itself (not its consumers). Affordances for users building on the SDK or iterating on the server.

<!-- adoption-table -->

Adoption — 65 samples exhibit `Sample > Developer ergonomics`.

| Path                                            | Count | Coverage |
| ----------------------------------------------- | ----: | -------: |
| Linter and type-checker stack                   |    22 |     34% |
| Sample MCP client configs in repo               |    22 |     34% |
| Inspector/debug tooling references              |     9 |     14% |
| Makefile / Makefile.toml                        |     9 |     14% |
| `pre-commit` framework                          |     9 |     14% |
| Examples directory with many patterns           |     8 |     12% |
| Devcontainer / mise / dev-environment manifests |     6 |      9% |
| `scripts/` directory                            |     5 |      8% |
| `uv run <tool>` invocations                     |     4 |      6% |
| MCP framework dev config                        |     3 |      5% |
| PowerShell + batch scripts                      |     3 |      5% |
| Programmatic embedding API                      |     3 |      5% |
| Setup subcommands on the MCP binary             |     3 |      5% |
| Custom installer-orchestrator                   |     2 |      3% |
| Health-check scripts                            |     1 |      2% |
| Justfile recipes                                |     1 |      2% |
| Sample example middleware                       |     1 |      2% |
| Sample implementations directory                |     1 |      2% |
| `commitizen`                                    |     1 |      2% |
| In-repo docs site                               |     0 |      0% |

<!-- /adoption-table -->
### Setup subcommands on the MCP binary

The same console script that runs the MCP server protocol also exposes management subcommands (`set-api-key`, `check-config`, `test-connection`) for credential setup and connectivity verification. Doubles the binary as a config CLI; uses `rich` and `click` for the human-facing output. Pattern echoes `kubectl config`-style CLIs. Setup subcommands frequently start with one host (e.g., `setup --tool=cline`) and use `--tool` (or equivalent) as the extension point for additional hosts — the flag's presence is itself a signal of intended scope expansion.

### MCP framework dev config

`fastmcp.json` for FastMCP-based projects gives the framework first-class dev configuration in the repo, separate from pyproject. Lets `fastmcp` dev tooling discover the server without arg passing.

### Sample example middleware

`example_middleware.py` or equivalent demonstrating how to extend the server via a configured middleware module. Acts as both documentation and a test of the middleware extension point.

### Health-check scripts

Per-container health-check scripts in monorepo-of-servers layouts so Docker can verify each server is responsive. Tied to container deployment patterns.

### Linter and type-checker stack

Standard runtime-appropriate tooling (`ruff` for Python, ESLint+Prettier for TypeScript, `mypy`/`pyright`/`ty` for typed Python projects, `biome` for TS, `clippy` for Rust). Wired in as dev dependencies and run in CI/pre-commit. Signals an opinionated dev environment that consumers contributing back should expect to match.

### `pre-commit` framework

Standardized hook orchestration for lint, format, and commit-message checks at commit time. Git hooks via lefthook or similar are an alternative.

### `commitizen`

Commit-message convention enforcement.

### Justfile recipes

`just <target>` for build, test, lint, package operations. Less common in MCP servers than Makefile but visible in the corpus. Appropriate when the author prefers Just's simpler syntax over Make.

### Makefile / Makefile.toml

`make <target>` for build orchestration; `Makefile.toml` (cargo-make) when the project is Rust. Shared dev targets (build, test, run) as a Makefile at repo root. Appropriate as the conventional default for build orchestration.

### PowerShell + batch scripts

Windows-first build, start, and packaging scripts (`build.ps1`, `start.ps1`, `build_mcpb.bat`) alongside Unix shell scripts. Appropriate when the author works on Windows or targets cross-platform packaging that needs platform-specific automation.

### `uv run <tool>` invocations

Dev workflow expressed as `uv run ruff check`, `uv run mypy`, `uv run pytest` rather than scripted recipes. Appropriate when the project leans on uv for environment management and avoids the indirection of a task runner.

### `scripts/` directory

Repo-local dev helpers and maintenance scripts.

### Custom installer-orchestrator

A bespoke `install.py` doubles as the dev entry point, replacing both pip and uv roles for end users and contributors. Flags include `--dry-run`, `--no-venv`, `--full`, `--clients`. Appropriate when the install workflow is so unusual that no general task runner fits.

### Sample MCP client configs in repo

`examples/` directory with ready-to-paste configs for various hosts, plus inline JSON snippets in README. Appropriate as user-facing onboarding ergonomics; reduces support burden.

### Examples directory with many patterns

`examples/` with 20+ runnable patterns covering the full surface — client, server, HTTP, SSE, OAuth, roots, sampling, structured tools, tasks. Appropriate for SDKs where adoption hinges on showing how each primitive lands in real code.

### Sample implementations directory

`samples/` directory with end-to-end mini-apps demonstrating different transports/configurations. Same idea as examples but framed as "complete miniature apps." Appropriate for SDKs where the unit of teaching is a working program rather than a snippet.

### Programmatic embedding API

A first-class `createConnection()` or equivalent that lets host processes embed the server as a library. Appropriate when the consumer base includes app developers, not just operators wiring subprocess installs.

### Inspector/debug tooling references

README points to MCP Inspector or similar debuggers for poking at the running server. Appropriate when the maintainer wants to nudge operators toward the canonical debug workflow.

### In-repo docs site

Dedicated `website/` or `docs/` directory shipping a documentation site alongside the server.

### Devcontainer / mise / dev-environment manifests

`.devcontainer/`, `mise.toml`, or similar manifests that pin the developer's tool versions. Lowers the barrier to first-contribution by automating environment setup.

## Documentation surface

How the project communicates what it is and how to use it — to users, developers, and AI consumers. Influences whether the README alone suffices or whether sibling docs are required.

<!-- adoption-table -->

Adoption — 58 samples exhibit `Sample > Documentation surface`.

| Path                                                                 | Count | Coverage |
| -------------------------------------------------------------------- | ----: | -------: |
| README as the canonical surface                                      |    27 |     47% |
| Per-host README integration sections                                 |    10 |     17% |
| README plus docs directory                                           |    10 |     17% |
| Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json) |     7 |     12% |
| README + examples/                                                   |     6 |     10% |
| GitHub Pages / hosted docs site                                      |     5 |      9% |
| Bundled `cursor_rules.md` / AI-guidance content                      |     4 |      7% |
| `llms.txt` / `llms-full.txt`                                         |     4 |      7% |
| CITATION.cff                                                         |     1 |      2% |
| Per-subserver README in monorepo                                     |     1 |      2% |
| Split USER_GUIDE / DEVELOPER_GUIDE                                   |     1 |      2% |
| `agents/` example directory                                          |     1 |      2% |
| Multi-host config samples                                            |     0 |      0% |
| Security audit docs                                                  |     0 |      0% |

<!-- /adoption-table -->
### README as the canonical surface

Single README.md carrying purpose, install, config, host integration, and tool inventory. Universal. Length and depth vary widely.

### Per-host README integration sections

README has labeled sections per supported host (Claude Desktop, Cursor, Codex, etc.) showing the canonical config snippet for each. Common where the server targets multiple host ecosystems.

### README plus docs directory

Supplementary `docs/` directory for longer-form material (architecture, per-tool deep dives) referenced from README. Surfaces in larger or more mature projects.

### README + examples/

README points at runnable examples in `examples/` for users to copy-paste. Appropriate when the integration is best learned by running a small sample.

### Split USER_GUIDE / DEVELOPER_GUIDE

Two sibling markdown files separate end-user concerns from contributor concerns. Appropriate for project-governed servers (vendor or org) where each audience has substantially different needs.

### Per-subserver README in monorepo

Each child server has its own README in its subdirectory. Appropriate for monorepos with thematically-distinct children that need independent operational documentation.

### Multi-host config samples

Repo carries `.mcp.json`, `.cursor-mcp.json`, `glama.json`, MCPB `manifest.json`, all in the root for users to consult per host. Appropriate when the author wants every host's setup to be one file copy away.

### CITATION.cff

Machine-readable citation metadata for academic publication. Appropriate when the project is published or referenced in academic literature.

### GitHub Pages / hosted docs site

Discovery-oriented site (`mcp.science`, `<project>.github.io`) or external documentation hosted on ReadTheDocs that surfaces the project to users searching outside GitHub. Common for projects with substantial reference material beyond the README.

### `llms.txt` / `llms-full.txt`

Curated context summaries shipped at repo root for LLM ingestion — a "vibe coding" surface beyond the MCP protocol itself. The two-file pattern (`llms.txt` for digestible summary, `llms-full.txt` for complete reference) is emerging convention. Some projects ship a single large LLM-ingestion doc under a different filename (e.g., `llm_mcp_docs.txt`) that fits the same role even though it doesn't follow the emerging two-file convention. Appropriate when the server's surface is large enough that the LLM benefits from a guided overview before reaching for individual tool descriptions.

### Bundled `cursor_rules.md` / AI-guidance content

A markdown file shipped alongside the server with rules or guidance the LLM should follow when using it. Neither MCP tool nor MCP prompt — just bundled context the host's LLM is expected to read. Appropriate when the server's correct usage requires conventions the per-tool descriptions cannot fully convey.

### `agents/` example directory

Runnable example clients demonstrating how an agent should drive the server. Appropriate when authorship benefits from concrete invocation patterns rather than abstract protocol description.

### Security audit docs

Separate documents recording security review of the project. Distinct from auth documentation; reflects deliberate compliance posture.

### Agent-facing meta-documentation (CLAUDE.md, .cursorrules, .mcp.json)

Documentation inside the repo that targets agents working in the repo, not human users:

- **`CLAUDE.md` shipped with the server** — Repo includes a `CLAUDE.md` at root providing Claude-specific guidance for working in the codebase itself. Distinct from a user-facing README; the audience is an agent contributing to the repo. Appropriate when maintainers want consistent agent behavior across contributors using Claude. Often paired with a top-level Claude-Code workspace config (`.claude/` directory) — indicates Claude is part of the contributor experience for the repo itself, distinct from the server being a Claude-Code plugin.
- **`.cursorrules` for Cursor IDE** — Equivalent for Cursor — repo-local instructions an AI editor reads when assisting in the codebase. Appropriate when the maintainer's IDE workflow involves Cursor and wants in-repo context steering.
- **`.mcp.json` at repo root** — Declares MCP servers the repo itself wants its agents to have available. Distinct from the server being authored — it's the dev environment's MCP wiring. Appropriate when developers iterating on the server need other MCP servers (filesystem, git, etc.) available during their work.

## Claude Code plugin / skill wrapper

Whether the server ships an in-tree Claude Code skill or plugin definition, distinguishing "MCP server only" from "MCP server + first-class Claude Code integration."

<!-- adoption-table -->

Adoption — 44 samples exhibit `Sample > Claude Code plugin / skill wrapper`.

| Path                                      | Count | Coverage |
| ----------------------------------------- | ----: | -------: |
| Bare MCP server, no Claude Code wrapper   |    36 |     82% |
| `.claude-plugin/` wrapper                 |     4 |      9% |
| `.claude/skills/` directory in repo       |     2 |      5% |
| `.claude-plugin/marketplace.json` only    |     1 |      2% |
| `claude-code/` directory with skill files |     1 |      2% |

<!-- /adoption-table -->
### Bare MCP server, no Claude Code wrapper

Server ships only the MCP surface; users wire it via `claude mcp add` or JSON config. Most common path.

### `.claude/skills/` directory in repo

Repo contains Claude Code skill definitions alongside the MCP server source. Skills wrap the MCP tool surface in Claude Code workflow patterns. Appropriate when the vendor wants the server discoverable via Claude Code skills, not just as a raw MCP endpoint.

### `claude-code/` directory with skill files

Sibling top-level directory carries Claude Code skill files; the README documents skill-file installation alongside MCP server installation. Appropriate as an explicit "first-class Claude Code support" signal beyond raw skill definition placement.

### `.claude-plugin/` wrapper

Server ships a Claude plugin manifest with dedicated CLI commands. Appropriate when the team wants Claude Code's plugin install/update lifecycle to govern the server's lifecycle.

### `.claude-plugin/marketplace.json` only

Marketplace discovery metadata without a full plugin.json. Lets the project surface in Claude's marketplace UI without becoming a full installable plugin — a discovery hook on top of the existing MCP-server distribution.

## Release and lifecycle

How versions get cut, how the project communicates change to consumers, lifecycle state, and licensing posture.

<!-- adoption-table -->

Adoption — 96 samples exhibit `Sample > Release and lifecycle`.

| Path                                              | Count | Coverage |
| ------------------------------------------------- | ----: | -------: |
| License — Permissive (MIT / Apache-2.0)           |    83 |     86% |
| Active development                                |    66 |     69% |
| Tagged release with version in changelog          |    30 |     31% |
| Archived                                          |     3 |      3% |
| Dated deprecation in repo                         |     2 |      2% |
| Dual-license relicensing gate                     |     2 |      2% |
| License — Copyleft (AGPL-3.0)                     |     2 |      2% |
| License — Copyleft / non-commercial (CC BY-NC-SA) |     2 |      2% |
| License — Permissive (BSD-3-Clause)               |     2 |      2% |
| Vendor-internal release (no public pipeline)      |     2 |      2% |
| Automated-release sentinel version                |     1 |      1% |
| License — Copyleft (GPL-3.0)                      |     1 |      1% |
| MCPB bundle signing                               |     1 |      1% |
| GitHub Actions release workflow                   |     0 |      0% |
| Manual via package manager                        |     0 |      0% |
| PyPI + lockfile-tracked                           |     0 |      0% |

<!-- /adoption-table -->
### GitHub Actions release workflow

`release.yml` triggers on tag push, runs build + test + publish. Sometimes paired with a dedicated `pages.yml` for docs site builds. Tagged releases on GitHub with semantic versions; release pipeline produces binaries, npm packages, Docker images, and Cargo crate uploads in parallel. Appropriate when releases need to fan out to multiple registries (npm + Docker, PyPI + Docker) and synchronized version bumps.

### PyPI + lockfile-tracked

`uv.lock` committed; PyPI uploads on tag. Appropriate for Python servers with PyPI as the primary distribution channel.

### Manual via package manager

The maintainer runs `npm publish`, `uv publish`, or equivalent locally. Appropriate for low-frequency releases where automation overhead exceeds the savings.

### MCPB bundle signing

Release pipeline produces an MCPB bundle, signed using a Rust-side toolchain alongside the Python codebase (Cargo.toml present alongside pyproject.toml for that purpose). Appropriate when MCPB is a distribution target and signed bundles are required.

### Vendor-internal release (no public pipeline)

For configs-only repos backed by remote services, the public repo has no release pipeline at all; the vendor's internal deploy pipeline is invisible. Appropriate for hosted remote MCP services.

### Dual-license relicensing gate

Existing code stays under the original license (MIT); new contributions land under a different license (Apache-2.0). The release process enforces the contributor agreement. Appropriate as a forward migration mechanism without rewriting prior commits.

### Tagged release with version in changelog

Standard semver tag (e.g., `v0.3.1`, `v0.2.6`) with a changelog entry. The default expectation.

### Dated deprecation in repo

Removal events (e.g., SSE removal on 2025-05-26) documented in-repo with dates rather than buried in changelogs. Appropriate when transport or capability changes have material impact on consumers and signaling them clearly is part of the maintenance contract.

### Automated-release sentinel version

Version field in `pyproject.toml` carrying a bot-generated value (observed: `0.9223372036854775807.9223372036854775807`, int64-max sentinel) rather than a human-chosen number. Suggests the canonical version comes from a release pipeline, not the source file.

### Active development

Recent commits, ongoing CI runs, semver-tagged releases. Default for all in-bin samples except outliers.

### Archived

Repository marked archived by the maintainer (e.g., `mcpr` archived Feb 2026). Code still functions; no further fixes. Appropriate to flag because consumers should weigh adoption risk.

### License — Permissive (MIT / Apache-2.0)

The dominant pattern — MIT for most, Apache-2.0 for FastMCP. Maximizes adoption; no commercial restriction.

### License — Permissive (BSD-3-Clause)

Permissive license closely related to MIT/Apache but with explicit attribution and non-endorsement clauses. Functionally similar (commercial-friendly, no copyleft) but distinguished by the legal text — particularly the requirement that the project's name and contributors not be used to endorse derivative products without permission. Appropriate when the author wants the permissive posture but cares about the attribution/endorsement language specifically.

### License — Copyleft (GPL-3.0)

Strong copyleft license. Derivative works must be distributed under the same license; commercial use is permitted but the obligations attach to redistribution. Distinct from AGPL-3.0 (no network-use clause) and CC BY-NC-SA (commercial use is allowed). Appropriate when the author wants derivatives to remain open without forbidding commercial adoption outright.

### License — Copyleft (AGPL-3.0)

Strong network-copyleft license. Like GPL-3.0 but extends source-disclosure obligations to network use — operating a modified server as a service triggers the obligation, not just redistribution. Rare in the MCP ecosystem; carries copyleft implications for hosts embedding the server in a hosted product. Distinct from GPL-3.0 (no network clause) and CC BY-NC-SA (forbids commercial use). Appropriate when the author wants to ensure derivatives stay open even when consumed as a hosted service.

### License — Copyleft / non-commercial (CC BY-NC-SA)

Rare in MCP ecosystem; appears as a deliberate restriction against commercial adoption. Trade-off: signals author's intent but limits downstream reuse in commercial settings. Appropriate when the author wants to retain commercial control over derivatives.

## Cross-role tools

Tools that surface under multiple functional roles in this merge — named in each role's section above where they appear, not duplicated as a top-level branch.

<!-- adoption-table -->

Adoption — 0 samples exhibit `Sample > Cross-role tools`.

| Path                            | Count | Coverage |
| ------------------------------- | ----: | -------: |
| Cargo / Cargo.toml              |     0 |      0% |
| Docker                          |     0 |      0% |
| Go modules / `go.mod`           |     0 |      0% |
| MCP Inspector                   |     0 |      0% |
| MCPB / Desktop Extension bundle |     0 |      0% |
| Pydantic                        |     0 |      0% |
| Smithery                        |     0 |      0% |
| `.claude-plugin/`               |     0 |      0% |
| uv                              |     0 |      0% |

<!-- /adoption-table -->
### Docker

Surfaces as *Distribution channel* (Docker image, Docker Hub MCP Registry, generic Dockerfile pulls), *Container artifacts* (Dockerfile in repo, multi-stage Alpine build, published image, Compose for dev/test/multi-server), *Test stack* (Docker-Compose backend for end-to-end tests; container-based test stack mirroring deploy shape), *Deployment topology* (containerized local process, published container image), and *Entry point and launch* (docker container entrypoint via `docker run -i --rm`).

### uv

Surfaces as *Distribution channel* (uvx execution, install-from-git via uvx, source clone with editable install), *Entry point and launch* (`uvx <package>`, `uv --directory` from source, source-tree `uv run`), *Build and packaging* (uv_build backend, uv.lock, hatchling + uv pairing), and *Developer ergonomics* (`uv run <tool>` invocations).

### MCPB / Desktop Extension bundle

Surfaces as *Distribution channel* (drag-and-drop bundle for Claude Desktop), *Release and lifecycle* (signed bundle artifact, MCPB bundle signing pipeline), *Host integration* (MCPB / DXT manifest among multi-host config samples), and *Container artifacts* (`.mcpbignore` for bundle packaging).

### Cargo / Cargo.toml

Surfaces as *Server runtime* (Rust SDK declaration, rust-toolchain.toml pin), *Build and packaging* (Cargo backend, Cargo.lock), *Distribution channel* (`cargo install`, crates.io), *Test stack* (Cargo test / cargo-nextest), and *Release and lifecycle* (signing dependency for MCPB bundles in Python projects).

### Go modules / `go.mod`

Surfaces as *Server runtime* (Go SDK declarations: mark3labs/mcp-go, metoro-io/mcp-golang, custom MCP implementation), *Build and packaging* (`go.mod` / `go.sum` for module path and dependency hashes), *Distribution channel* (`go module via go get / go install`, pre-built binary release, standalone bridge binary), and *Test stack* (Go stdlib testing).

### Smithery

Surfaces as *Distribution channel* (Smithery registry, aggregator/installer registry) and *Host integration* (Smithery / Glama discovery via `glama.json`, `smithery.yaml`, CLI installer chooses host).

### `.claude-plugin/`

Surfaces as *Distribution channel* (`.claude-plugin/marketplace.json` for marketplace discovery), *Host integration* (`.claude-plugin/` directory in repo for one-click Claude install), and *Claude Code plugin / skill wrapper* (full plugin manifest with dedicated CLI commands).

### MCP Inspector

Surfaces as *Test stack* (manual verification driver), *Host integration* (compatibility called out as a verification surface), and *Developer ergonomics* (Inspector/debug tooling references).

### Pydantic

Surfaces as *Server runtime* (transitive runtime dependency for FastMCP), *Schema and types* (Pydantic v2 models with raw or FastMCP SDK), and *Configuration delivery* (pydantic-settings for env var validation).














