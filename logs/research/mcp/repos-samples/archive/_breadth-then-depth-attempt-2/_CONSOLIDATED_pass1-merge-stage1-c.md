# Sample

Merge of 4 partials (bins 10, 11, 12, 13) into `_CONSOLIDATED_pass1-merge-stage1-c.md`. Functional roles with implementation paths and qualitative descriptions; no inline citations (see `references` verb for provenance).

## Server runtime

The host process that loads the MCP protocol implementation, registers handlers, and serves requests. The runtime choice constrains language-ecosystem decisions downstream — packaging, async model, type-schema strategy, dependency surface, and distribution channels available.

### Python with FastMCP

A Python server built on the FastMCP framework, the higher-level wrapper over the raw MCP SDK that auto-derives JSON schemas from typed function signatures via Pydantic. Author writes `@mcp.tool` decorated functions; FastMCP handles JSON-RPC plumbing, schema generation, and transport selection. Two major lines coexist: an older 1.x style imported as `from mcp.server.fastmcp import FastMCP` (bundled with the `mcp[cli]` extra), and a newer 2.x line imported as `from fastmcp import FastMCP` published as a separate `fastmcp` package. Pinning is often tight (down to patch level, e.g., `fastmcp == 2.7.0` or `>=3.1.0,<4`) to track API drift in the still-evolving 2.x line. Implies async tool handlers by default and pulls Pydantic 2 as a transitive runtime dependency. Compatible with stdio, HTTP, and SSE transports out of the box. Appropriate when the server's tool surface maps cleanly to typed Python functions and the author wants transport/observability concerns handled by the framework.

### Python with raw mcp SDK

A Python server built directly against the `mcp` package (sometimes `mcp[cli]`) without FastMCP. The author handles tool registration, schema authoring (typically by hand as JSON Schema dicts or explicit Pydantic models), and transport wiring at the lower-level Server API. Surfaces both as the modern `mcp[cli]>=1.4.1` and as legacy pre-1.0 `mcp-server>=0.1.0` referenced in `setup.py`-era projects. Chosen when the project predates FastMCP, when authors need finer control over the server lifecycle (very wide tool surfaces with custom dispatch, full use of resources + prompts), when wrapping a sync-only third-party library where FastMCP's async-first ergonomics add no value, or when minimizing the dependency surface matters. Tool handlers are typically `async def` since the low-level SDK is async-native, but sync handlers also occur when the underlying client library is sync.

### Python with raw MCP SDK alongside FastMCP

A transitional pattern where the project depends on both `mcp` and `fastmcp` packages simultaneously — typically because the project predates FastMCP and migrated partially, or because some lower-level capabilities only exist in the raw SDK. Pins both with bounded version ranges to control compatibility. Adds maintenance overhead (two SDKs to track) but enables incremental migration.

### Node.js with MCP TypeScript SDK

A Node-runtime server built on Anthropic's official MCP TypeScript SDK, typically authored in TypeScript and compiled to a `build/` JS output as the launched artifact. Schema definition is hand-authored in TypeScript. Chosen when the upstream API client (the SaaS SDK or proprietary library being wrapped) is JS-native (Supabase, libSQL, discord.js, Puppeteer), when distribution needs to land in npm-only host environments without requiring users to install Python tooling, or when the author's existing codebase is JS. Pulls in npm as the distribution channel by default and aligns with `npx` as the launch idiom. Server runtime requires Node 16+ for older projects, Node 18+ as a typical modern floor.

### Rust with rust-mcp-sdk + rust-mcp-schema

Rust runtime built on the rust-mcp-stack family of crates. Compiles to a static binary with no external runtime dependencies, enabling distribution as a single executable across Homebrew, Cargo, npm (native-binary wrapper), and Docker channels. Pinned to a specific Rust toolchain via `rust-toolchain.toml`. Types are compile-time-checked rather than reflected. Appropriate when performance matters (filesystem operations at scale), when zero runtime dependencies are a deployment requirement, or when the author wants to ship as a static native binary instead of depending on Python/Node ubiquity.

### Go with custom MCP SDK

Compiled-binary host with a hand-built Go implementation of the MCP protocol on top of JSON-RPC 2.0. Exposes a functional-options API (`WithStreamableURI`, `WithSSEURI`, `WithSSEMessageURI`, `WithRootRedirect`) for configuring servers, separate `client.go`/`server.go` packages, and an out-of-process bridge binary for non-Go consumers. Includes built-in OAuth2/OIDC support that most Python/TypeScript SDKs delegate to the host. Used here as an SDK/framework target rather than a single application — the Go entry exposes both server-embedding and a standalone bridge so consumers can either embed the library or run a packaged executable. Pairs with `go get` consumption as a library and standalone-binary distribution.

### DuckDB extension (C++) embedding MCP

Native DuckDB extension built with CMake that exposes MCP via SQL PRAGMAs rather than running as a standalone process. The "server" is the user's DuckDB session; tool calls and configuration originate from SQL statements (`PRAGMA mcp_server_start(...)`, `PRAGMA mcp_publish_tool(...)`). Blurs the database/tool-registry boundary — SQL templates become first-class published tools. Constrains distribution to source-build with `make` since DuckDB community-extension packaging may not yet be available.

### Remote HTTP service (no local runtime)

The "runtime" lives on a vendor-hosted endpoint; the GitHub repo carries only client config files and OAuth metadata. There is no local language or framework to choose because nothing executes on the user's machine. Appropriate when the vendor wants centralized control over capability evolution, rate limits, and credential rotation, and is willing to take on the operational cost of hosting.

## Transport

The wire protocol the server listens on for MCP frames. Transport choice constrains tenancy, deployment shape, and authentication options — stdio is single-process per client and uses host-managed credentials; HTTP-class transports support shared deployments and per-request authentication.

### stdio

JSON-RPC frames over stdin/stdout. Default for nearly every locally-launched server in the corpus because Claude Desktop, Cursor, and other host integrations launch the server as a subprocess and communicate over its pipes. Implies one server process per host connection, single-tenancy per process, and credentials sourced from the host launcher's environment (not from the MCP request). Forces strict discipline on stdout/stderr separation: any stray `print` corrupts the JSON-RPC stream, so servers either suppress prints in core handlers or route logs to stderr only. Often selected implicitly — README shows the launch command without naming the transport. Works equally well when the server is wrapped in a Docker container that runs the stdio server inside (`docker run -i`).

### Streamable HTTP

HTTP transport with streaming response support, the modern HTTP-class option in the MCP spec. Supports request/response streaming without SSE's connection-lifetime constraints. Selected via env var or CLI flag; binds host/port (typical default `0.0.0.0:8000`). Often paired with stateless-mode flags so the same HTTP endpoint can be deployed behind a load balancer for shared multi-user use. Enables shared-server deployments where multiple clients connect to one process and per-request authentication is meaningful. Required for managed-cloud deployment where the client cannot launch the server locally; required for OAuth-style auth flows that need a browser callback. Endpoints are typically `/mcp` (and `/health` for liveness in some implementations). Often advertised as "coming soon" in samples that currently ship stdio-only, indicating it is the next-step expansion path most authors anticipate.

### SSE

HTTP server-sent events transport. Server-push streaming over an HTTP connection, used as a transport flavor when the server needs server-initiated streaming without a full bidirectional websocket. Co-exists with streamable-http in samples that support multiple HTTP-class transports; chosen by users on hosts that prefer SSE compatibility. Same shared-deployment posture as streamable-http; often offered alongside stdio with selection via CLI flag.

### HTTP mode with CORS

HTTP transport with CORS configuration, enabling browser-based or cross-origin shared deployments. `PORT` and `BIND_ADDRESS` env vars configure binding. Chosen when the server is expected to back a hosted multi-tenant service or when browser clients need direct access. Carries the same per-request authentication implications as other HTTP-class transports.

### Remote HTTP endpoint (vendor-hosted)

The transport is HTTPS to a vendor-hosted URL like `https://mcp.slack.com/mcp` or `https://mcp.context7.com/mcp`. There is no local subprocess at all; the client connects directly to the vendor's service. Implies OAuth-style authentication (the server can't trust environment variables that only the user's process would see), per-workspace tenancy, and operator responsibility for uptime and rate limits. Appropriate when the vendor wants to deliver MCP as a hosted service rather than a downloaded artifact.

### MCP-client mode (server connects out)

Inverted role where the same artifact connects out to other MCP servers and exposes them through its own surface. Seen in the DuckDB extension where SQL `ATTACH` semantics let queries span multiple MCP-exposed data sources. Distinct from being a server — this turns the artifact into a federation point.

### In-process HTTP bridge alongside stdio

A custom HTTP server bound to a fixed port (e.g., 8000) running inside the same process as the stdio MCP server, exposing equivalent functionality to non-MCP clients. Distinct from "pick a transport" — both protocols serve simultaneously. Toggled via env var (e.g., `*_ENABLE_HTTP_BRIDGE`). Suited to projects that want to be consumable by both MCP-aware agents and arbitrary HTTP clients without duplicating business logic. Often implies a custom bridge implementation rather than the SDK's built-in HTTP transport.

## Transport selection mechanism

How the user or host tells the server which transport to use when more than one is supported. Distinct from the transports themselves — this is the configuration affordance.

### Environment variable

A single env var (e.g., `TRANSPORT_MODE`, `MCP_NIXOS_TRANSPORT`) chooses among supported transports at process start, often paired with companion env vars for host/port/path/stateless-mode settings. Container-friendly because env vars are the natural Docker/Kubernetes config surface; doesn't require shell-level argument forwarding through wrapper scripts.

### CLI flag

A flag passed to the entry-point command (e.g., `-t sse`, `--http`, `--transport http`) selects transport. Natural for local launch via `uvx`/`npx`; less ergonomic in containerized environments where flags must be wired through entrypoint scripts. Often paired with multiple JSON config snippets in the README — one per mode — that show users how to wire the host to each transport.

### Functional options (in-code configuration)

Caller assembles the server with composable option functions (`WithStreamableURI()`, `WithSSEURI()`, `WithSSEMessageURI()`) before starting it. Suited to library/SDK projects where the consumer is another program rather than an end user invoking from a host config.

### Separate entry points per transport

Each transport mode is a distinct entry function or binary (e.g., `stdioSrv.ListenAndServe()` vs `srv.HTTP(...).ListenAndServe()`). Forces an explicit choice at code-level rather than runtime configuration.

### SQL PRAGMA

Server mode and transport parameters chosen from SQL inside an embedded extension. Specific to the in-database implementation path; the user issues `PRAGMA mcp_server_start(...)` with transport options as arguments.

### Implicit / default-only

Server supports exactly one transport (typically stdio) and never names it in the README. Documentation is the launch command; transport is whatever that command produces.

## Capability surface

The MCP primitives the server exposes — tools, resources, prompts, sampling — and how they're partitioned. Choice of primitive shapes how callers discover and invoke functionality.

### Tools-only

The server exposes only the `tools` primitive — every operation is a tool call, including read operations. The most common pattern across the corpus. Appropriate when all operations have clear input parameters and the agent should explicitly invoke each one. Tool counts range from a handful (4-6) for vendor servers with product-tier tool boundaries up to 250+ for surface-area-maximizing wrappers around large APIs (e.g., a kubectl wrapper). Large surfaces (50+) are typically organized into feature groups that can be toggled at config time, with grouping reflecting upstream API divisions (Account, Database, Storage).

### Tools + resources

The server exposes both `tools` (for actions and queries with parameters) and `resources` (for read-oriented content addressable by URI, e.g., `zendesk://knowledge-base`, `hf://`). Splits read access from write/action access along MCP primitive lines. Chosen when there's a clear addressable content surface (a knowledge base, a document collection, a model/dataset/space catalog) that benefits from URI semantics and resource-list discovery rather than tool-call ceremony. Less common — most servers use tools for everything.

### Tools + resources + prompts (full MCP surface)

Server uses all three surfaces in one process: tools for actions, resources exposed under a custom URI scheme for browsable content, and prompts as named templates the host can offer to users. Demonstrates MCP features that most servers ignore. Appropriate when the integration target has rich hierarchical content worth exposing as resources and when there are reusable prompt patterns specific to the domain ("compare these models", "summarize this paper").

### Tools + sampling + prompts

Server adds MCP's sampling surface (server-initiated LLM calls back through the host) on top of tools and prompts. Used for agentic helpers like subject-line suggestion or multi-turn assist that need the host's LLM rather than running inference locally. Appropriate when the server has small auxiliary completions to make and doesn't want to bring its own inference path.

### Tools + prompt routines (out-of-band)

The server ships pre-authored Markdown prompt files alongside the tool surface, distributed as plain content (e.g., a `prompts/` directory) rather than via the MCP `prompts` primitive. Encodes "how to use this server for task X" as reusable templates the user manually loads. Chosen when the author wants to package guided workflows but doesn't need the protocol-level prompts primitive. Appropriate for servers whose tools combine into well-understood multi-step tasks (SEO audits, 404 detection, performance analysis).

### Tools + resources + prompts + UI dashboards

Maximal MCP surface — tools, resources, prompts via protocol primitives, plus optional GUI dashboards bundled as an install extra. Chosen by surface-maximizing wrappers around very large APIs where every primitive has clear use. Implies an opt-in install extra (e.g., `[ui]`) for the dashboard component so users who only need protocol surface can avoid heavy dependencies.

### Read/write tool split

Distinct tools (or distinct tool groups) for read vs. write operations against the same upstream — `execute_read_only_query` vs. `execute_query`, Content API (read) vs. Admin API (write). Supports different approval or sandboxing workflows at the MCP-client layer; lets users grant only the read surface when write isn't needed.

### Per-tool output format selection

Tools accept an output-format parameter (text/JSON/markdown/CSV) so the caller controls representation. Token-efficiency and rendering-quality knob; rare among MCP servers.

### User-publishable tools

Server provides a meta-tool that lets the user register new tools at runtime (e.g., `mcp_publish_tool` with a parameterized SQL template). Turns the server into a tool-registry rather than a fixed surface; specific to embedded-extension architectures where the substrate (DuckDB/SQL) makes parameterization safe.

### Embedded RAG / retrieval pipeline

Server bundles an embedding model, vector store, document parser, and retrieval logic in-process (llama-index, sentence-transformers, pinecone, pymupdf). Tool calls run inference and similarity search inside the server rather than delegating to an external RAG service. Server-boundary-blurring; sharply increases the server's footprint and dependency surface but provides domain-aware retrieval for documents the upstream doesn't pre-index.

### Token-economy unified-tool surface

Deliberate compression of the tool surface to a small number of broad tools (e.g., one unified query tool taking a wide query parameter, ~1,030 tokens of schema, plus one auxiliary tool). Rationale: schema text counts against the host's token budget, so fewer tools means smaller capability advertisement. Affects schema strategy and even backend indexing — the broad tool needs internal routing logic that finer-grained tools wouldn't.

### Tool-count modes (compound vs full)

A single server ships two operating modes: a compact "compound" surface (tens of aggregate tools) and a "full" surface (hundreds of granular tools), selectable via CLI flag at launch. Lets the user trade context-window pressure against expressive granularity without re-installing. Appropriate when the integration target has a very wide API (hundreds of methods) and the author has measured that the full surface overwhelms typical prompt budgets.

## Capability scoping

How the server lets callers narrow the active capability surface at launch time or during a session. Distinct from capability-surface choice itself: scoping is about which subset of the offered capabilities is actually loaded or active.

### Modular tool selection flag

A CLI flag (e.g., `--tools=all` with named subset support, `features=database,docs`) lets the user opt into specific tool categories rather than exposing the full surface. Reduces prompt-window noise for users who only need one sub-domain (e.g., invoicing but not subscriptions). Some feature groups default off (e.g., storage tools) for conservative posture. Appropriate when the server has a large categorized tool surface (30+ tools across functional families).

### Destructive-action gating flag

A CLI flag or env var (e.g., `--disable-destructive`, `READ_ONLY_TOOLS`, `ENABLE_DELETE_TOOLS`) suppresses tools that mutate or destroy state, leaving read-only tools active. Safety knob for environments where the agent should observe but not change. May be implemented as a single read-only switch or as orthogonal two-axis flags (read-only + enable-delete) recognizing that delete is more dangerous than other writes and deserves its own gate. Appropriate when the server's tool surface contains a clear destructive subset (kubectl delete, scale-down operations) or when the integration target's API mixes safe writes with irreversible destructive operations.

### Read-only-by-default

The server runs in read-only mode unless explicitly opted into write access. Implemented either as a runtime flag (`READ_ONLY_TOOLS` env var) or as the only mode the server ever offers (no write tools shipped at all). Appropriate for filesystem and read-heavy data servers where the destructive blast radius of a mistaken tool call is high.

### Per-tool disabling at launch

Single-mode server but with a launch-time mechanism to disable individual tools, reducing capability surface and token usage for token-sensitive deployments. Distinct from a write-mode flag — this is per-tool subtraction, not category-level gating. Appropriate when different deployments need different subsets of the server's capability and token cost is a measured concern.

### Optional install extras for feature bundles

Install-extras gate optional feature bundles at install time (e.g., `pip install <pkg>[ui]` adds dashboard dependencies; a separate env-var toggle enables browser-automation tools). Chosen to keep the base install lean while letting power users opt into heavier feature sets. Appropriate when feature bundles have heavy transitive dependencies that most users don't need.

### Path-traversal protection

For servers exposing file operations, tool implementations validate that requested paths stay within configured root directories. Pairs with auto-cleanup (export files deleted after response is encoded) to prevent disk bloat and cross-tenant leakage on shared machines. Appropriate whenever the tool surface accepts user-controlled paths.

### Vendor-side capability scoping

Remote MCP services constrain what the server will do via OAuth scope and workspace admin approval, not via flags the user sets. The server itself enforces; the user can't elevate. Appropriate when the deployment model is hosted-service-with-tenants rather than local-subprocess.

## Authentication

How the server proves identity to the upstream service it wraps, or (less commonly) to its own MCP callers.

### None (local-only operation)

No authentication because the server doesn't talk to a remote service — it operates on local files, archives, a locally-running application, or a public unauthenticated API. Appropriate when the server's role is to expose existing local data (crawler archives, local databases, on-disk indexes), wrap a desktop-only library (scikit-learn), or query a public backend (browser automation against the open web, public package indexes). Demonstrates that valid MCP servers need not require credentials at all.

### Static API key / token via environment variable

A single API key, personal access token, or bearer token supplied via environment variable (`HF_TOKEN`, `TFC_TOKEN`, `HA_TOKEN`, `DISCORD_TOKEN`, `MILVUS_URI`, `SEMANTIC_SCHOLAR_API_KEY`). Process-scoped to one account; per-request tenancy is at the upstream account level. The most common and lowest-ceremony auth pattern in the corpus. Single-tenant by construction — one process, one credential set, one identity. Appropriate when the upstream service uses bearer tokens and the deployment is single-user; common for stdio-launched servers where the host's MCP client config is the only place the token needs to live.

### API key (optional, for higher rate limits)

Server works without credentials but accepts an API key to lift rate limits or unlock additional features (private-resource access, higher quotas). Lowers friction for first use; rewards users who register. Appropriate for public-data integrations where unauthenticated use is a real flow but heavy users need a way to identify themselves.

### OAuth 2.0 client credentials

OAuth flow producing a bearer token with a documented lifetime (e.g., 3-8 hours) using a client ID + secret pair. Token may be supplied externally (env var or CLI flag) or generated by the server from credentials. No browser/user consent step — used when the upstream is a backend service (e.g., FHIR with client-credentials grant, single-merchant payment processors). Carries token-refresh concerns for long-lived sessions; whether refresh is handled in-server or delegated to the caller varies. Appropriate when the upstream service requires OAuth and the deployment is single-tenant.

### OAuth 2.0 / 2.1 with browser consent

Browser-based authorization flow where each user authorizes the server to act on their account. Required when serving multiple tenants from one endpoint; requires HTTP transport so the browser callback can land. Vendor-specific clientIds per host with workspace admin approval and a callback port for the OAuth handshake. Token lifecycle managed by the MCP client/host. An early-adopter pattern signaling that the MCP auth story is maturing past static keys.

### OAuth 2.1 (RFC 9728) bolt-on / server-side enforcement

Optional OAuth 2.1 layer protecting the MCP server itself (not the upstream). Configured via env vars (`MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE`, JWKS endpoint). Two modes observed: global resource protection (any request requires a valid bearer token) and fine-grained per-tool/resource control (still flagged experimental). Client-side counterpart includes automatic token acquisition on a 401 response — the client discovers the protected resource metadata, acquires tokens, and retries. Layered on top of any transport — adds authentication to HTTP-class deployments primarily. Appropriate for hosted MCP deployments where multiple clients share a server and per-client identity matters.

### OAuth setup-wizard flow

A one-shot interactive command (e.g., `npx ctx7 setup`) walks the user through OAuth and writes the resulting credentials into the host's config file. Removes manual JSON editing for users; constrains the project to ship a setup helper alongside the server. Per-user identity rather than per-process. Pairs naturally with hosted HTTP MCP endpoints where the credential is sent on each request.

### Server-managed token rotation

The server holds a long-lived secret (or root-credential pair) and mints short-lived child tokens transparently — JWTs that expire every few minutes with automatic renewal, or per-database tokens minted from an org-level token with configurable expiration and permission scope. Pushes auth lifecycle work into the server rather than the client/host. Useful when the upstream API enforces short-lived tokens (Ghost Admin API JWTs) or when child-token issuance is a security-isolation primitive (Turso per-database tokens).

### Cloud-native identity (Azure EntraID and similar)

Cloud-platform-specific auth path with multiple sub-flows — service principal, managed identity, default Azure credential. Includes automatic token renewal with background refresh. Co-exists with standard auth (e.g., username/password ACL) as an alternative path. Appropriate when the deployment is on cloud infrastructure and managed identity eliminates the credential-rotation problem.

### Service-specific credentials via third-party SDK

Credentials handed to a community SDK (e.g., `zenpy` for Zendesk) that handles the upstream auth flow internally — API token, username/password, or whatever the SDK supports. The MCP server is a thin layer; the SDK owns the credential model. Appropriate when a mature community SDK already exists and re-implementing its auth would duplicate effort.

### Multi-provider credential bundles

Server accepts credentials for many simultaneous backends (10+ email providers, multiple embedding services) and selects per-call which to use. Credentials still come from environment variables, but the env surface is much wider. A `configure_service` tool can also re-point credentials at runtime without restart. Appropriate when the server is a unified front for a heterogeneous backend ecosystem and users want to swap or compare providers without process churn.

### Dual-API split credentials

Single server fronts two upstream APIs that have separate credential schemes (e.g., a read-only API with query-param key auth and a write API with JWT). Both credentials live in env vars; tools route to whichever API surface they belong to. Constrains tenancy because a user without one credential pair simply loses access to that group of tools.

### In-server encrypted credential vault

The server stores secondary credentials encrypted with a master key, enabling on-disk persistence of sensitive material rather than relying on env-var pass-through alone. Driven by regulated-domain requirements (PHI/HIPAA in healthcare); rare elsewhere.

### Bearer token via JSON config file

The server reads a bearer token from a configuration file rather than env var or CLI flag. Used when the embedded-extension model means env vars are awkward to thread through the host process; JSON config is loaded by the server itself.

### Host-managed kubeconfig

Authentication delegated to a standard config file the host environment already manages (`~/.kube/config` for kubectl-class servers). The server reads the file, no in-MCP credential delivery. Appropriate when the wrapped tool already has a well-established local credential file and users have configured it for other purposes.

### Locally-running application IPC

Server talks to a desktop application over its own scripting interface (e.g., DaVinci Resolve's Python scripting API). The application enforces its own access model; the MCP server has no auth layer of its own. Requires the application to be configured for external scripting access. Appropriate when the integration target is a desktop application rather than a cloud service.

### Bot identity (third-party platform)

Auth against a chat or social platform via that platform's bot model — Discord bot tokens, etc. The bot's permissions (which servers it's invited to, what scopes it has) define the reachable surface; users grant the bot access through the platform's normal invite flow rather than configuring the MCP server directly.

### Credential-scoping guidance

Documentation pattern (not a mechanism) — vendor recommends a scoped/restricted credential variant (e.g., Stripe Restricted API Keys) over the full-power root key. Security-ergonomics layer on top of whichever auth mechanism the server uses.

## Multi-tenancy

Whether one server process can serve multiple distinct upstream accounts/instances/users or only one.

### Single-user / single-tenant per process

The server is bound at launch to one upstream account, one connection, or one merchant. Per-request tenancy is whatever the upstream account naturally supports. Universal in the corpus for locally-launched servers. Implied by stdio transport (one process per host connection) and by env-var-sourced credentials (process-scoped). Multiple tenants require multiple server processes.

### Per-call tenancy argument

Tenancy lives in the tool signatures themselves — search and retrieval tools take a tenant identifier as an argument and route the underlying call into that tenant's slice. Treats tenancy as a first-class parameter rather than a process-level config. Rare across the Python ecosystem, which usually pushes tenancy to env vars. Appropriate when the integration target is itself multi-tenant (vector DBs with tenant collections) and a single MCP process should be able to serve multiple tenants through one credential.

### Per-request tenant scoping via URL parameters

HTTP server multiplexes tenants in a single process; each connection's URL query parameter (e.g., `project_ref`) plus the OAuth identity defines the tenant boundary for that session. Required for managed-cloud-as-a-service deployment where one endpoint serves all customers.

### Per-user OAuth token / per-workspace OAuth token

Each user (or each workspace) has their own OAuth credential; the server uses the credential on the user's behalf. Workspace is the tenant boundary in the workspace variant; the token implies which workspace's data the call sees. Pairs naturally with hosted HTTP endpoints serving many users and with vendor services where workspace is the natural unit of administration and billing.

### Per-request bearer token

Each HTTP request carries its own token; the server identifies the tenant from the token. Suited to multi-user shared deployments behind a load balancer.

### Sub-tenancy via child-credential generation

Server holds an organization-level credential and generates per-resource child credentials with bounded scope and expiration (per-database tokens from an org token). Provides isolation within a single organizational tenant rather than across tenants.

### Stateless HTTP for shared deployment

Server flag (e.g., `*_STATELESS_HTTP`) disables per-connection state so the server can sit behind a load balancer with multiple instances handling requests interchangeably. Multi-user-capable when paired with per-request auth.

### Bot-scoped

One bot identity per process; the bot's platform memberships define the reachable tenants. Multiple users may interact with the same bot, but the server's identity is fixed.

## Configuration delivery

How the server receives runtime configuration — credentials, endpoints, behavior toggles. Often combines multiple sources with documented precedence.

### Environment variables

The dominant pattern across the corpus, sometimes loaded from a `.env` file via `python-dotenv` or equivalent. Universal fallback and typically the primary surface for credentials. The MCP host config (per-client JSON) is responsible for setting them before launching the subprocess. Appropriate for credentials that should never appear in process listings or shell history. Often layered with proxy-hierarchy rules — a tool-specific proxy env var takes priority over standard `HTTPS_PROXY`/`HTTP_PROXY` for corporate/enterprise environments. Pairs cleanly with Docker (`-e VAR`), uvx (env inheritance), and host-config JSON (which has explicit `env` blocks).

### CLI arguments

Arguments passed to the entry-point command (`--api-key`, `-u`, `-k`, `--full`, `--transport http`). Often offered alongside env vars as an alternative or as the primary surface for connection parameters (URL, host, port, SSL paths) when the author wants explicit, inspectable config. Mode flags and transport selection commonly arrive here. Some servers position CLI as primary with env-var fallback; others deprecate CLI in favor of env-only. Constrained by host wrapper config — some MCP clients pass `args` cleanly, others muddle quoting.

### URI scheme

A single connection URI (e.g., `redis://`, `rediss://`) packs host, port, credentials, and TLS selection into one string. Often accepted alongside discrete CLI flags as a convenience. Appropriate for connection-oriented services where URI is the standard idiom of the underlying client library.

### URL query parameters

Configuration embedded in the HTTP endpoint URL (e.g., `?project_ref=...&read_only=true&features=database,docs`). Specific to HTTP-transport managed-cloud deployments; the same server process serves many tenants and per-request scope is part of the URL the client connects to. Unusual outside HTTP managed-MCP-as-a-service deployments.

### `.env` file

A local `.env` file is read at startup via `python-dotenv` or equivalent. Often paired with a tracked `.env.example` template that lists required keys without values. May take precedence over CLI args or env vars (one observed project explicitly inverts the common ordering, treating `.env` as the highest-priority source) — biases toward reproducible host-config-driven deployments at the cost of overriding CLI invocations. Appropriate for self-hosted developer-mode deployments where the user clones the repo and configures locally rather than installing from a registry.

### JSON configuration file

A file the server reads at startup containing settings (HTTP/token configs, feature toggles). Often used in embedded-extension or container-deployment contexts where a mounted config volume is more convenient than env-var sprawl.

### SQL PRAGMA parameters

Configuration values passed as named arguments to PRAGMA calls inside an embedded extension. The user, via SQL, configures the server at runtime rather than at process launch.

### Functional options at construction

In library/SDK projects, the consumer passes option functions when building the server (`WithStreamableURI(...)`). No external config — choices are baked into the consuming program's source.

### Runtime reconfiguration tool

A dedicated tool (`configure_service`) lets the host swap providers or update settings during a session without restart. Used by servers with multi-provider backends where the user might want to switch from SendGrid to Mailgun mid-conversation. Appropriate when the integration target is multi-provider and the user expects to compare or rotate without process churn.

### Host-managed JSON config

Configuration delivered via the host's config file (e.g., Claude Desktop's `claude_desktop_config.json`, Cursor's config, Cline's `mcp.json`), where the host inserts an `mcpServers` entry naming the server's command, args, and environment. Universal in the corpus as the user-facing entry point even when the server itself reads env vars or flags — the host config translates user setup into the actual launch command. Different hosts use different paths and shapes. The visible configuration surface for end users; everything else (env vars, CLI flags) is consumed via this layer.

### Feature-group toggles

Sub-pattern layered on top of any of the above mechanisms. The server exposes a single config field (`features=...`, `--tools=...`) that enables/disables groups of tools at startup. Reduces surface area for clients that don't need every capability and simplifies token/permission scoping. Some feature groups default off (e.g., storage tools) for conservative posture.

## Distribution channel

How the server's executable artifact reaches end users. A single project usually ships through several channels in parallel.

### PyPI with uvx execution

Published as a PyPI package consumable via `uvx <package>` or `uvx --from <package>@latest <command>`. uv resolves and runs in an ephemeral venv without an explicit install step. The `--from` form lets the package name differ from the console script name. The dominant Python-server distribution path for modern host-config snippets where one-line invocation matters more than reproducible installs. Requires `uv` on the user's machine but eliminates venv management.

### PyPI with pip install

Published as a PyPI package installed via `pip install <package>` into the user's environment, then run via the installed console script. Older idiom than uvx; positioned for users on plain Python rather than uv. Sometimes paired with `uvx` as alternative install commands; sometimes the only path. Appropriate when the author wants broad compatibility and isn't requiring users to adopt uv.

### Source clone with editable install

No registry publication — users clone the repo and run `uv venv && uv pip install -e .`, `pip install -e ".[dev]"`, or `uv sync`. The "developer-mode-as-release" pattern. Optional dev extras live under `[project.optional-dependencies]`. Appropriate when the project is early-stage, when the author wants to require git-clone (so users get the README, examples, and `.env.example` template), or when releasing to a registry isn't yet justified.

### Source clone with `uv run`

Server is launched from a checked-out source tree via `uv run src/<package>/server.py ...`. Unusual for vendor-official servers; signals either a development-leaning posture or that the project hasn't fully embraced PyPI distribution. Forces consumers to clone the repository before they can run the server.

### Source-only clone (no published package)

Distribution is `git clone` plus build/install instructions. No npm or PyPI publication. Limits reach to users willing to clone but keeps repo simple and avoids registry/account ceremony. Surfaces in both Node projects (`npm install && npm run build`, then `node build/index.js`) and Python projects (`pip install -r requirements.txt`).

### Custom Python installer script

A bespoke `install.py` (multi-KB) creates a venv, installs deps, and writes per-client JSON configs into 10+ MCP client locations. Replaces both pip and uvx for the end user; the only command they run is `python install.py`. Appropriate when the server has unusual host-side requirements (must locate a desktop application, must write configs to many client locations) that no general-purpose installer could handle.

### npm registry with npx execution

Published as an npm package consumable via `npx -y <package>`. The user never explicitly installs; npx fetches and runs in one step. Standard idiom for Node-runtime servers and the path of least resistance for hosts that already integrate with the npm ecosystem. Often used for one-shot setup commands (e.g., an OAuth-bootstrap script) as well as for the long-running server itself.

### npm package wrapping native binary

Native binary published as an `@scope/package` npm package so Node-ecosystem users can pull it with the tooling they already have. Appropriate when a Rust or other native binary wants to reach the broad npm install surface without forcing users to install Cargo.

### Cargo

`cargo install <crate>` for Rust servers; the user gets a compiled binary on their PATH. Appropriate when the server is Rust and the audience already has a Rust toolchain.

### Homebrew

`brew install <formula>` distribution, paired with shell installer scripts on Unix and PowerShell installers on Windows. Appropriate as a polish channel for native binaries that warrant package-manager presence.

### Go module (`go get`)

Library/SDK consumed by other Go programs via `go get github.com/<owner>/<repo>`. Distribution is the source-as-Go-module model; no published binaries needed for the library use case.

### Standalone bridge binary

Pre-built executable that wraps the library so non-Go programs can use it without embedding. Distributed alongside the Go-module library for the same project. Suited to allowing Python/Node/etc. tools to consume an MCP server backed by the library without needing a Go toolchain.

### Source build with make / CMake

Distribution requires `git clone` and a build step. Used when no package-registry path is established (DuckDB extension awaiting community-extensions inclusion) or when the project intentionally doesn't publish (compliance-sensitive servers expecting users to audit and build).

### Docker image

Published or build-from-source Docker image. May be published to Docker Hub, ghcr.io, or shipped as a Dockerfile only. Consumers pull and run with `docker run -i --rm -e <ENV>... <image>`. The host config uses `"command": "docker"` with the image and env passthrough as args. Suited to environments where Docker is already part of the operator's mental model (e.g., Home Assistant deployments) or when the dependency stack is heavy enough that image isolation pays off. Often paired with PyPI/uvx as a secondary install method.

### Docker Hub MCP Registry

Container image published to Docker Hub's MCP-specific registry. Distinct from a generic Docker Hub push because the registry is scoped to MCP servers. Appropriate when the server has external dependencies that benefit from being containerized and the author wants the registry's MCP-aware discovery.

### docker-compose

Compose file shipped in the repo to orchestrate the server alongside its dependencies. Suited to projects bundling multiple services (e.g., a server plus a database it needs).

### Nix flake (`nix run github:...`)

Nix-native install via flake reference; consumers run `nix run github:<owner>/<repo>` without registry intermediation. Reproducible by Nix's content-addressed store. Often paired with a `nix develop` shell for contributors.

### Declarative NixOS / Home Manager module via nixpkgs

Server packaged as a first-class nixpkgs entry; users add a config block to their NixOS or Home Manager config. Rare among MCP servers — gives the project a system-config-managed install path for declarative-systems users.

### Smithery one-click / registry via npx

Published to Smithery for one-click installation into supported hosts (primarily Claude Desktop), or registered through `npx -y @smithery/cli install <name> --client claude`. Layers on top of an underlying registry (PyPI/npm) — Smithery generates the host config and triggers install. Complementary to source/PyPI/Docker — the registry surfaces the project to discovery, the underlying install still happens via one of the other channels. Appropriate when the author wants registry-level discoverability and is willing to depend on Smithery as the install path even for non-JS servers.

### Git source via uvx

Installation directly from a git URL via `uvx --from git+https://...`. Combines source-install ergonomics with uvx's ephemeral-venv execution. Appropriate for pre-release, fork-tracking, or when the user wants a specific commit without registry intermediation.

### GitHub releases with binary attachments

Tagged GitHub releases as a distribution surface, often alongside registry publication. Pre-compiled binaries attached for users who don't want to use any package manager. Appropriate for binary attachments, signed checksums, or when the release artifact differs from the registry artifact.

### MCPB bundle

Pre-packaged bundle for drag-and-drop install into Claude Desktop. Authoring may require a Rust signing path (Cargo.toml alongside pyproject.toml) for bundle signing. Appropriate when the target audience is desktop-host users who shouldn't have to use a command line.

### Zed extension

Editor-specific extension distribution channel for users running Zed. Appropriate as a long-tail audience reach for servers whose authors want broad editor coverage.

### Managed cloud endpoint / hosted HTTP

Vendor hosts the server at a fixed HTTPS URL; users configure their MCP client to point at that URL with no install step. Requires HTTP transport; pairs naturally with OAuth or API-key auth. Distribution-as-a-service stance from vendors with existing SaaS infrastructure.

### Configs-only repo (no server artifact)

Repo ships only client config snippets and OAuth setup metadata; the actual server is hosted remotely by the vendor. Distribution is "configure your client to point at our endpoint." Appropriate for vendor-hosted remote MCP services.

### Vendor-bundled (CLI subcommand)

Server ships inside another tool the user already has installed (Supabase CLI exposes a local MCP endpoint when `supabase start` runs). Distribution piggybacks on existing tool adoption.

### Multi-channel publication

Same server published through several channels simultaneously (PyPI + Docker + source; npm + managed endpoint + self-host package). Different user segments have different preferences; multi-channel publication maximizes reach but multiplies maintenance.

### Cross-ecosystem packaging

Single repository publishes the same conceptual artifact to multiple language ecosystems (PyPI + npm) with parallel naming conventions (`stripe-agent-toolkit` vs. `@stripe/agent-toolkit`), or a Python implementation with a thin npm wrapper that invokes the Python entry point under the hood. Enables both Python and TypeScript consumers from one source of truth; doubles publication and version-coordination work.

### `.claude-plugin/marketplace.json`

Marketplace metadata file shipped in-repo so the project surfaces in Claude's plugin marketplace. Distinct from a full `plugin.json` plugin wrapper — the marketplace file alone enables discovery without installing the project as a Claude plugin.

## Entry point / launch

The actual command users or hosts invoke to start the server, after distribution has placed the artifact.

### Console script

`[project.scripts]` (Python) or `bin` field (Node) declares a named executable (e.g., `mcp-server-qdrant`, `mcp-weaviate`, `terraform-cloud-mcp`, `hass-mcp`) that wraps the package's main function. Host config uses the bare command name. Standard idiom for PyPI/npm-installed servers. Same pattern with required CLI arguments when the server needs them inline (`grafana-loki-mcp -u ... -k ...`); host wrapper config must be careful with quoting.

### `uvx <package>`

Host config uses `"command": "uvx"` and passes the package name as an arg; the package is fetched and run on demand. The cleanest stdio launcher for Python servers and the common host-config shape for modern Python servers. Eliminates the need for users to pre-install or manage a venv.

### `npx -y <package>`

Bare `npx -y <package>` for Node servers. The `-y` accepts the install prompt automatically. Universal launch idiom for npm-distributed servers. The host's JSON config typically lists `npx` as the command and the package name (with `-y` for auto-confirm) as the first arg. Often passes `--api-key=...` or other CLI flags inline. Also used for one-shot bootstrap commands like OAuth setup wizards.

### `uv --directory` from source

`uv --directory /abs/path run <script>` invokes a console script from a source checkout, with uv resolving the venv and dependencies. Path-anchored launch where the host config points uv at a local source checkout. No console script involved; the user must know both the package directory and the script name. Appropriate for editable-install distributions where the user has cloned but not published.

### Source-tree `uv run`

`"command": "uv"` with `run src/<package>/server.py ...` as args. Launches against a checked-out source path rather than an installed package. Unusual but documented in some projects' canonical configs.

### Bare Python script

Host launches `python <script.py>` directly with absolute paths to a venv interpreter and the script. No packaging entry point at all. Bare `python` on system PATH is fragile (depends on which interpreter is first found). Common in legacy `setup.py`-era projects, in single-file "hackable" layouts, and when the server intentionally avoids Python packaging (custom installer owns the venv).

### Built JS file (`node build/index.js`)

TypeScript projects compile to a JS output directory and host config invokes Node against the built file. Requires the consumer to have run `npm install && npm run build` first.

### Native binary

Standalone executable installed via Cargo, Homebrew, npm, or release download. Host invokes the binary by name. Appropriate for Rust and other compiled-language servers with no runtime deps.

### Standalone bridge binary

Pre-compiled executable that wraps a library so non-language-native consumers can launch a working server without writing any code. The Go bridge form ships alongside the Go-module library for the same project.

### Docker container entrypoint

The Docker image's `ENTRYPOINT` or `CMD` runs the server. Host config maps `docker run -i --rm -e <ENV> <image>` (or compose) to the MCP launch command. The MCP transport is stdio inside the container, with the `-i` flag wiring host stdin/stdout to the container. Appropriate when the user has standardized on container-based tool isolation.

### Make targets in repo

Local-dev launch via `make run`, `make dev`, `make build`, etc. Common in projects with substantial dev tooling; not the end-user launch path but the developer-iteration path.

### URL configuration (no local launch)

For managed-endpoint / vendor-hosted deployments, the user's MCP client points at an HTTPS URL — no local launch step. The "entry point" is the URL itself.

### SQL PRAGMA invocation

User starts the server from inside a DuckDB session via `PRAGMA mcp_server_start()`. The host process is the DuckDB CLI/library; the MCP server is a behavior toggled within it.

### Library embedding (no entry point)

The project is consumed as a library/SDK; the consumer writes their own `main` and embeds the server. Used by Go SDK projects that expose `srv.HTTP(...)` and `stdioSrv.ListenAndServe()` for callers to invoke.

## Type and schema strategy

How tool input/output types are declared and validated.

### Pydantic via FastMCP auto-derivation

Tool function signatures use Python type hints; FastMCP derives JSON schemas via Pydantic at registration time. Appropriate as the path of least resistance for FastMCP servers.

### Pydantic via raw MCP SDK

Author writes Pydantic models explicitly and registers them with the SDK's tool registration calls. Appropriate when the author wants explicit control over schema shape (descriptions, field metadata) that decorator-magic might obscure.

### Hand-authored tool schemas

For very large tool surfaces (300+ tools), schemas are hand-authored or generated from external API specs rather than reflected from Python signatures. Also used in TypeScript servers where schemas are written directly. Appropriate when reflective derivation would be too slow at startup or when the source of truth is an external API spec.

### Rust schema crate

`rust-mcp-schema` crate provides the type definitions; tools are registered with strongly-typed handlers. Types are compile-time-checked rather than reflected. Appropriate as the natural Rust idiom.

## Async model

Whether tool handlers are sync or async, and what drives the choice.

### Async throughout

Tool handlers are `async def`; FastMCP and the MCP SDK both accept async handlers natively. Connection pooling for outbound calls is enabled. Appropriate when the integration target has an async client library or makes network calls that benefit from non-blocking IO.

### Sync throughout

Tool handlers are plain `def`. Forced when the underlying library is sync-only (scikit-learn, DaVinci Resolve's scripting API). Wrapping sync work in async would add thread overhead with no concurrency win. Appropriate when the integration target is sync by nature.

### Mixed

The MCP SDK accepts both forms in the same server; some tools are async (network calls), others sync (CPU work). Appropriate when the integration target has both kinds of operation.

## Test stack

How the server's deterministic logic is verified.

### pytest with async plugins

Python servers using pytest as the runner with `pytest-asyncio` (often `asyncio_mode = "auto"`) and/or `pytest-anyio` for async test support. Frequently paired with pytest-cov and a coverage gate (e.g., `--cov-fail-under=80` in `addopts`). May include in-memory backends as fixtures (e.g., in-memory Qdrant client) to avoid external service dependencies during test. Some projects layer custom markers to separate test scopes (e.g., `integration`, `dc_e2e`, `cloud_e2e` distinguishing on-prem vs. cloud deployment-mode tests). Sometimes gated behind a `[dev]` optional extra so end users don't pull test deps. Standard choice for FastMCP-based and async-native raw-mcp servers.

### Jest

Node servers using Jest. Standard JS choice. Configuration may be present without specific test-layout details extracted.

### vitest

Node servers using vitest as the runner. Faster modern alternative to Jest in TypeScript projects. Configuration may be present without specific test-layout details extracted.

### npm test (monorepo workspace)

`npm run test` invoked across pnpm workspaces in monorepos; specific framework not always surfaced.

### Go stdlib testing

Standard `testing` package; test files live alongside source as `client.go`/`server.go` patterns. Common to all Go projects.

### cargo-nextest

Rust test runner orchestrated through a `Makefile.toml` that also defines `fmt`, `clippy`, `check`, and `clippy-fix` targets. Faster than `cargo test` for larger suites. Appropriate for Rust servers that warrant a test runner upgrade.

### Native build-system test target

Tests run via the native build system's test target (`make test` invoking CMake/CTest for the C++ extension).

### Live multi-phase suite against application

Bespoke test harness organized in phases (read-only → destructive → media → AI/ML → advanced) running against a real instance of the integration target. Coverage reported as percent-of-API-methods-exercised rather than line coverage. Appropriate when the server wraps a large, stateful application where mocking would be more code than the harness.

### make test targets

Test invocation wrapped in a Makefile target — typically `make test`, sometimes also `make test-connection` for upstream-reachability smoke tests. Layered over whichever underlying framework runs the tests.

### Docker-Compose backend for end-to-end tests

Repo ships a `docker-compose.yml` that brings up the upstream service (Ghost+MySQL, etc.) for local end-to-end testing — not for deploying the MCP server itself, but as the substrate the test suite hits. Notable infrastructure investment for an MCP repo; more common in integration-test frameworks.

### Linter/formatter test gate

Project relies on lint/format/type-check tooling (`ruff`, `black`, `mypy`, `ty`, `biome`) as part of the CI gate; pre-commit hooks enforce locally. Some projects run both `ruff` and `black` (redundant since modern `ruff format` covers most of what `black` did).

### MCP Inspector (manual verification)

`npx @modelcontextprotocol/inspector <command>` for manual testing. Documented as the recommended way to verify the server before wiring it into a host. Not a unit/integration test, but an authoring-time interactive verification step. Often the only documented testing approach for minimal projects.

### None observed

Some samples ship without surfaced tests at all. Common in single-file experimental servers, configs-only repos, and projects whose maintainer relies on manual host testing instead. Appropriate signal of small audience or early stage; not a recommendation.

## CI

Automated build/test/release pipelines.

### GitHub Actions

The dominant CI substrate across the corpus. Workflows live in `.github/workflows/`; specifics vary — typically lint/type-check/test plus release publishing. Some projects run a quality matrix (ruff/black, mypy, bandit, tests across Python 3.10/3.11/3.12; Biome for webapp components); some run Rust toolchain targets via Makefile.toml (fmt, clippy, test, check); some pair Actions with a CodeRabbit-style PR review bot. Often paired with codecov integration for coverage reporting and badges in README.

### Pre-commit hooks

Configured locally via `.pre-commit-config.yaml`; runs lint/format checks before commit. Often overlaps with CI's lint stage and serves as a local mirror of CI rules.

### Renovate / Changeset tooling

Sub-tools for dependency automation (`renovate.json`) and changelog management (`.changeset/`). Common in TypeScript Node projects.

### None / not applicable

No `.github/workflows/` surfaced. Common in single-file or experimental projects. Configs-only repos and remote services have no CI surface to speak of in the public repo — the vendor's hosting pipeline is invisible.

## Container artifact

Container-format outputs the project ships or uses internally. Distinct from container-as-distribution-channel: this role tracks the build artifact regardless of whether it's published.

### Dockerfile (build-from-source)

A `Dockerfile` in the repo root for users to build locally. Often installs from a lock file (`uv.lock`, `requirements.lock`) for reproducibility rather than from `pyproject.toml` resolution. Appropriate when the author wants to provide a containerization recipe without operating a registry.

### Published Docker image

Pre-built image published to Docker Hub, ghcr.io, or a similar registry. Removes the build step for end users. Doubles as a distribution channel (consumers `docker pull`) and a deployment artifact (operators run the image directly). Often paired with `docker run -i` host configs.

### Multi-stage Rust to Alpine

Builder stage uses `clux/muslrust:stable`, final stage is `alpine:latest` with a non-root user. Produces a small static-binary image. Appropriate when the server is Rust and the author wants minimal image size.

### docker-compose

`docker-compose.yml` orchestrating the server with related services (e.g., a database, a CMS). Suited to dev setup, end-to-end testing infrastructure, and to deployments needing multiple coordinated containers. Sometimes serves dual purposes — production deploy plus test substrate.

### Makefile-driven Docker build

`make build` invokes Docker build under the hood. Combines container packaging with the project's broader make-target workflow.

### Nix flake / NixOS module

`flake.nix` for `nix develop` and `nix run` workflows; declarative module exposed via nixpkgs for system-level installation. Doubles as distribution (consumers `nix run`) and dev environment (`nix develop` provides a reproducible shell).

### No container artifacts

Project ships only language-package or source distribution; users who want containerization build their own image. Sometimes omitted intentionally because the server must run on the host with the integration target (desktop application, local-process IPC), or because MCPB bundling replaces the container role.

## Repo layout

Filesystem organization of the project.

### Single-package src-layout

`src/<pkg>/` for source, `tests/` for tests, single `pyproject.toml` (or `package.json`). The Python convention for cleanly-packaged servers and the dominant shape across the corpus. Possibly includes `examples/`, `Dockerfile`. Appropriate when the project ships exactly one server and doesn't need workspace management.

### Single-package flat layout

Server file at repo root with optional `src/<helpers>/`. Common for "hackable" community servers where the entire server may fit in a few hundred lines. Appropriate for small, single-author projects where the overhead of src-layout would be ceremony.

### Single-file script

One `.py` or `.ts` file at repo root plus a manifest (`requirements.txt` / `package.json`). Suited to minimal experimental servers; reflects a "demonstration" rather than "long-lived project" posture.

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

### Monorepo with multiple published packages

Multiple publishable packages coexist in one repo (`@scope/sdk`, `@scope/mcp`, `@scope/integration`, etc.) coordinated by pnpm-workspace.yaml or similar workspace tooling; changesets handles version bumps and changelog generation across packages. Used when the project is "MCP plus other agent-integration surfaces" and treats MCP as a peer to SDKs and framework adapters. Expanded layout includes `/docs`, `/plugins`, `/skills`, `/rules`, `/public`, `/i18n` directories alongside `/packages`.

### Library with subdirectories

Go library layout: root-level `client.go`/`server.go`/`doc.go` plus subdirectories for `/bridge`, `/client`, `/server`, `/internal`, `/docs`, `/example`. Suited to SDK-style projects where the surface is multiple consumable packages.

### Configs-only

No `src/`. The repo carries `.mcp.json`, per-host config files, and possibly companion `commands/` and `skills/` directories for client-side artifacts. Appropriate when the server is remote and the repo's job is to deliver client-side configuration.

## Host integration

The set of MCP-capable host applications the server documents support for, typically via JSON config snippets and per-host wrapper artifacts.

### Claude Desktop

Universal in the corpus — every locally-launched server documents Claude Desktop integration. The host's `claude_desktop_config.json` `mcpServers` entry is the canonical onboarding artifact and often the only example shown. Configuration is JSON with `command` and `args`. Often paired with MCPB for drag-and-drop install.

### Cursor

Common second-tier integration. Same JSON `mcpServers` shape as Claude Desktop in most cases. Sometimes documented via "quick-install badge" links that auto-configure, via `.cursor-mcp.json`, or via `.cursor-plugin/` directory at the repo root. Sometimes accompanied by deeplink-based browser setup for OAuth.

### Claude Code CLI

Documented via `claude mcp add` registration or via a `.mcp.json` in the repo. Some configs-only repos publish a clientId for OAuth-based remote MCP integration. Native support for the `/mcp` flow. Appropriate when the audience includes CLI/agent users.

### VS Code with GitHub Copilot / Copilot Studio

Documented integration path, typically requiring a VS Code setting (`chat.agent.enabled: true`) to be enabled. Same JSON config shape as Claude Desktop.

### Windsurf, Kiro, Cline, Augment

Additional supported hosts surfaced via quick-install badges or short documentation snippets. The corpus shows broad host-list expansion as a documentation pattern — author lists every host with a known integration path even when the config shape is identical.

### Zed

Documented as a Zed extension. Less common; sometimes the only sample in a bin to mention it. Appropriate as a long-tail editor audience.

### Multi-host catalog (30+ agents)

README documents support for 30+ different agent platforms with per-agent config snippets. Implies the server is generic enough that it doesn't depend on host-specific features.

### Smithery / Glama discovery

Registered with discovery hubs via `glama.json` (Glama) or by being installable through Smithery's `npx`. Appropriate when the author wants registry-level visibility beyond per-host configs.

### Universal installer covering many hosts

A single `install.py` script writes per-host configs to up to 10 MCP client locations in one invocation, eliminating per-host setup steps. Appropriate when the user audience is broad and the author wants to remove the "find your client's config file" step entirely.

### `.claude-plugin/` directory in repo

Project ships a Claude-Code plugin wrapper directory at the repo root, encoding the plugin manifest alongside the code. Distinct from JSON-snippet host config — this packages the project as a discoverable Claude Code plugin.

### `.mcp.json` in project root

A project-local MCP-config file convention used by Claude Desktop and similar hosts that read `.mcp.json` to discover MCP servers tied to a specific project workspace.

### NixOS / Home Manager module

Declarative config entry (an attribute set added to `configuration.nix` or `home.nix`) handles install + activation in one place. Rare among MCP servers; tied to the Nix distribution channel.

### OpenAI Agents SDK

Documented support as a non-MCP-host MCP-consuming runtime. Indicates the author is positioning the server as ecosystem-agnostic rather than Claude-specific.

### Vercel AI SDK native integration

Server exports a `createToolSchemas()` (or equivalent) function that lets a Vercel-AI-SDK-based app consume the same tool schemas without going through MCP transport — first-class non-Claude integration. Doubles the project as both an MCP server and an SDK.

### MCP Inspector

`npx @modelcontextprotocol/inspector <command>` for manual testing. Documented as a verification tool rather than a host per se, but often listed alongside hosts as part of the integration surface.

### WSL configuration guidance

Documentation specifically addressing Windows users running the host through WSL — environment-bridging concern that some servers call out explicitly.

### No host integration documentation

SDK-style or library projects skip host-specific docs because the consumer is another program, not a host. Examples and library docs replace host snippets.

## Observability

How the server reports its own behavior — logs, metrics, debug surfaces.

### Env-var-controlled log level

A single env var (e.g., `PERPLEXITY_LOG_LEVEL`, `MCP_REDIS_LOG_LEVEL`) sets log severity at startup, with standard Python/Node logging defaults for destination and format. Most common observability surface in the corpus. Appropriate for stdio servers where logs go to stderr and the host displays them.

### Debug toggle + log file path

Pair of env vars — a boolean debug flag (`MCP_DEBUG`) plus a log file destination (`MCP_LOG_FILE`). Separates "verbose mode" from "where the verbose output goes." Appropriate when the server runs detached from an interactive host and logs need to land somewhere persistent.

### stdout/stderr discipline only

Server avoids any stdout output that isn't JSON-RPC; logging is silent or routed to stderr. The `print` policy is sometimes documented as zero-tolerance because a single stray print breaks the protocol. Appropriate for stdio servers where stdout is the wire.

### `--interactive` REPL mode

A CLI flag that drops the server into a terminal REPL for direct query inspection, doubling as a debug surface. Unusual — most servers assume MCP Inspector is the only interactive debugging path. Appropriate when the server's domain (e.g., crawler-archive search) benefits from quick local exploration before MCP integration.

### Companion monitoring dashboard

Separate web app (Vite + Uvicorn on dedicated ports) ships in the same repo for monitoring and control. Distinct process, distinct ports, not bundled into the MCP server itself. Appropriate when the server has long-running state worth visualizing and the author wants admin tooling beyond logs.

### Not surfaced

Many samples don't document observability at all. Appropriate signal that the server runs short-lived per request and observability hasn't become a need.

## Python build system

For Python servers, the PEP 517 build backend, packaging convention, and dependency-pinning approach.

### hatchling backend with uv

`hatchling.build` as the wheel/sdist builder, `uv` as the dependency manager (lock file `uv.lock`). The mainstream modern Python packaging path for new projects. Pairs with `[project.scripts]` console-script declarations and `requires-python` floors. Often combined with optional `[dev]` extras for test-only deps.

### setuptools (with `setup.py` or `setup.cfg`)

Older convention, still appropriate for long-lived projects predating hatchling or for projects needing setuptools-specific features. Sometimes via `setup.py` directly, sometimes via `setuptools.build_meta` declared in `pyproject.toml`. Console scripts declared in setup.py's `entry_points`, but README invocation may diverge from the declared script (a sign the package was never installed/tested as a console script). Appropriate when the project predates the modern hatchling default or has setuptools-specific build steps.

### uv_build backend

Uv's native build backend, declared via `requires = ["uv_build>=0.8.3,<0.12.0"]` in `pyproject.toml`. Less common than hatchling. Sometimes paired with non-standard module-name conventions (e.g., `module-name = "app"`). Signals adoption of uv's full toolchain rather than just its venv/lock features. Appropriate for projects that want maximal uv integration and are willing to track a newer backend.

### `uv.lock` committed

Project commits its uv-managed lockfile so contributors and CI install the same resolved versions. Modern convention; not universal. Pairs with `uv` as the version manager and uv_build or hatchling backends. Appropriate when the project is uv-first and reproducibility across developer/CI/Docker environments matters.

### `requirements.lock` committed

A pip-style lock file (often hand-maintained or via pip-tools), used as the install contract inside Dockerfiles for reproducible image builds. Appropriate when the project ships a Docker image and wants build-time pinning independent of runtime install resolution.

### `.python-version` file

Project pins the local interpreter version via pyenv-style file. Often combined with uv to enforce the floor.

### No lock file

Plain `pyproject.toml` with version ranges, no lock committed. Appropriate for libraries (where range flexibility helps consumers) but unusual for end-user-installable servers. Typically signals minimal-packaging posture or older project conventions.

## Documentation surface

User-facing documentation artifacts beyond the README.

### README + docs/ directory

README provides one-line purpose, install commands, and host configs; deeper material lives under `docs/`. Appropriate when the project has more than a quickstart's worth of explanation.

### README + examples/

README points at runnable examples in `examples/` for users to copy-paste. Appropriate when the integration is best learned by running a small sample.

### CLAUDE.md alongside README

Repo carries a `CLAUDE.md` file with agent-facing operational notes distinct from the user-facing README. Appropriate when the project anticipates being driven by Claude Code or similar agents and wants to encode procedural knowledge in a place agents will read.

### Multi-host config samples

Repo carries `.mcp.json`, `.cursor-mcp.json`, `glama.json`, MCPB `manifest.json`, all in the root for users to consult per host. Appropriate when the author wants every host's setup to be one file copy away.

### llms.txt for AI-consumption docs

A `llms.txt` file providing a flattened, AI-friendly view of the project for agents that consume it. Pattern emerging in projects whose primary readership includes other LLM agents.

### ReadTheDocs / hosted docs site

External documentation hosted on ReadTheDocs or a similar service. Common for projects with substantial reference material beyond the README.

### Devcontainer / mise / dev-environment manifests

`.devcontainer/`, `mise.toml`, or similar manifests that pin the developer's tool versions. Lowers the barrier to first-contribution by automating environment setup.

### Security audit docs

Separate documents recording security review of the project. Distinct from auth documentation; reflects deliberate compliance posture.

## Developer ergonomics

Tools and scripts the author provides to themselves and contributors.

### Justfile recipes

`just <target>` for build, test, lint, package operations. Less common in MCP servers than Makefile but visible in the corpus. Appropriate when the author prefers Just's simpler syntax over Make.

### Makefile / Makefile.toml

`make <target>` for the same role. `Makefile.toml` (cargo-make) when the project is Rust. Appropriate as the conventional default for build orchestration.

### PowerShell + batch scripts

Windows-first build, start, and packaging scripts (`build.ps1`, `start.ps1`, `build_mcpb.bat`) alongside Unix shell scripts. Appropriate when the author works on Windows or targets cross-platform packaging that needs platform-specific automation.

### `uv run <tool>` invocations

Dev workflow expressed as `uv run ruff check`, `uv run mypy`, `uv run pytest` rather than scripted recipes. Appropriate when the project leans on uv for environment management and avoids the indirection of a task runner.

### Custom installer-orchestrator

A bespoke `install.py` doubles as the dev entry point, replacing both pip and uv roles for end users and contributors. Flags include `--dry-run`, `--no-venv`, `--full`, `--clients`. Appropriate when the install workflow is so unusual that no general task runner fits.

### Sample MCP client configs in repo

`examples/` directory with ready-to-paste configs for various hosts, plus inline JSON snippets in README. Appropriate as user-facing onboarding ergonomics; reduces support burden.

### Setup-wizard CLI as bootstrap

A one-shot npx/uvx command that bootstraps OAuth, writes host config, and registers credentials before the user touches any JSON. Reduces install friction at the cost of shipping an additional CLI artifact alongside the server.

## Release pipeline

How the project moves from source to published artifact.

### Versioned releases (vN.N.N)

Tagged releases on GitHub with semantic versions; release pipeline produces binaries, npm packages, Docker images, and Cargo crate uploads in parallel. Appropriate for projects with multiple distribution channels that need synchronized version bumps.

### PyPI + lockfile-tracked

`uv.lock` committed; PyPI uploads on tag. Appropriate for Python servers with PyPI as the primary distribution channel.

### MCPB bundle signing

Release pipeline produces an MCPB bundle, signed using a Rust-side toolchain alongside the Python codebase (Cargo.toml present alongside pyproject.toml for that purpose). Appropriate when MCPB is a distribution target and signed bundles are required.

### Vendor-internal release (no public pipeline)

For configs-only repos backed by remote services, the public repo has no release pipeline at all; the vendor's internal deploy pipeline is invisible. Appropriate for hosted remote MCP services.

## Plugin wrapper

Whether the project ships Claude-plugin-system metadata in addition to (or instead of) being a plain MCP server.

### `.claude-plugin/marketplace.json` only

Marketplace discovery metadata without a full plugin.json. Lets the project surface in Claude's marketplace UI without becoming a full installable plugin — a discovery hook on top of the existing MCP-server distribution.

### None

No `.claude-plugin/` directory; the project is consumed only via host MCP configs and not through the plugin system. Most servers in the corpus sit here.

## Notable cross-cutting axes

Patterns observed across the corpus that don't fit cleanly under a single role and may surface as new roles after the cross-bin merge.

### Server-boundary blurring through embedded data/retrieval engines

Some servers embed substantial in-process infrastructure beyond the MCP plumbing — a full RAG stack (embeddings + vector store + document parsing), or the database engine itself (DuckDB extension). The boundary between "MCP server fronting a service" and "MCP server that IS the service" softens.

### Vendor-bundled MCP-as-a-service

Vendors with existing SaaS infrastructure offer the MCP endpoint as part of their cloud product (`https://mcp.<vendor>.com`). Distinct distribution stance from stdio-only servers; reshapes the auth model toward OAuth and the config model toward URL parameters.

### MCP as one of several agent-integration surfaces

Projects where MCP is shipped alongside SDKs, AI-framework adapters, and billing primitives in one repo — MCP is treated as a peer integration channel rather than the product. Monorepo layout follows.

### Compliance-driven encryption / audit features

Projects from regulated domains (healthcare, finance, legal) ship in-server encrypted credential vaults, security audit docs, or dual-deployment matrices (cloud + on-prem) that aren't seen elsewhere.

### Dual-deployment-topology testing

Servers supporting both cloud and on-prem deployment of the upstream encode that matrix into the test suite via custom markers (`cloud_e2e`, `dc_e2e`) — not just CI config but pytest-marker-level partitioning of test scopes.

### Domain-specific terminology service integration

Servers fronting healthcare APIs integrate domain ontologies (LOINC); a pattern likely to recur in legal (Westlaw taxonomies), education (curriculum standards), finance (ticker/ISIN). The terminology service is a distinct upstream the server bridges alongside the primary API.

### Public-vs-private architectural split

Project's MCP client/wrapper code is open-source while the backend (parsing, crawling, query-resolution engines) is private and run as a hosted service. The OSS repo is consumable but doesn't reveal the full implementation. Pairs naturally with the hosted-HTTP-endpoint distribution and OAuth/API-key auth.

## Cross-role tools

Tools that surface under multiple functional roles in this merge — named in each role's section above where they appear, not duplicated as a top-level branch.

### Docker

Surfaces as Distribution channel (Docker image, Docker Hub MCP Registry, generic Dockerfile pulls), Container artifact (Dockerfile in repo, multi-stage Alpine build, published image), Test stack (Docker-Compose backend for end-to-end tests; in-image build verification via lock file), and Entry point / launch (docker container entrypoint via `docker run -i --rm`).

### uv

Surfaces as Distribution channel (uvx execution, git source via uvx), Entry point / launch (`uvx <package>`, `uv --directory` from source, source-tree `uv run`), Python build system (uv_build backend, uv.lock), and Developer ergonomics (`uv run <tool>` invocations).

### MCPB

Surfaces as Distribution channel (drag-and-drop bundle for Claude Desktop), Release pipeline (signed bundle artifact), and Host integration (MCPB manifest.json among multi-host config samples).

### Cargo / Cargo.toml

Surfaces as Server runtime (Rust SDK declaration), Distribution channel (`cargo install`), and Release pipeline (signing dependency for MCPB bundles in Python projects).

### GitHub Actions

Surfaces as CI (lint/test/typecheck on PR, quality matrix, Rust toolchain runs) and Release pipeline (binary builds, package publishes on tag).

### `.env` file

Surfaces as Configuration delivery (runtime config) and Developer ergonomics (`.env.example` template).

### Host-managed JSON config

Surfaces as Configuration delivery (the user-facing config layer) and Host integration (the per-host onboarding artifact that names the launch command, args, and env block).

### Nix flake

Surfaces as Distribution channel (`nix run`), Container artifact (declarative system-packaging artifact), and Developer ergonomics (`nix develop` reproducible shell).

### `npx`

Surfaces as Distribution channel (npm registry execution), Entry point / launch (`npx -y <package>`), and Developer ergonomics (one-shot bootstrap commands like OAuth setup wizards).

### MCP Inspector

Surfaces as Test stack (manual interactive verification) and Host integration (a verification path documented alongside hosts).

### Smithery

Surfaces as Distribution channel (Smithery one-click / registry) and Host integration (Smithery / Glama discovery).
