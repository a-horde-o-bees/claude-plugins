# Sample

Merge of 5 partials (bins 1-5) into _CONSOLIDATED_pass1-merge-stage1-a.md. Functional roles with implementation paths and qualitative descriptions; no inline citations (see `references` verb for provenance).

## Server runtime

The language and framework that hosts the MCP protocol loop and dispatches tool/resource calls. Choice of runtime constrains which transports, packaging channels, host-config shapes, async semantics, and schema-derivation strategies are natural; also dictates which interpreter or toolchain must be present on the deployment host.

### Python with FastMCP

Python server built on the FastMCP decorator framework (typically `fastmcp>=2.x` pinned with caps such as `>=2.0.0,<3.0.0`, with newer projects on `>=3.0.1` or `>=3.2.2,<4`). FastMCP auto-derives tool input schemas from typed function signatures and return types feed the output schema, letting authors write nominally-synchronous typed Python functions while it manages the async transport boundary. Provides a native config file (`fastmcp.json`) alongside pyproject and a FastMCP-specific log-level convention (`FASTMCP_LOG_LEVEL`). Compatible with all official transports out of the box, so multi-transport support drops in without runtime changes. Authors gravitate to it when the tool catalog is hand-authored, when ceremony around each tool function should be minimal, and when authoring effort scales with tool count rather than with framework boilerplate. One server in the corpus declares both `fastmcp` and the raw `mcp` SDK as dependencies, bridging two SDK generations within a single package.

### Python with raw MCP SDK

Direct use of Anthropic's `mcp` Python SDK (`mcp` / `mcp[cli]`) without a higher-level framework wrapper. The author works against `mcp.server` primitives — tool handlers and schemas are hand-authored rather than auto-derived, and protocol framing is explicit. Pin discipline varies widely from exact (`mcp[cli]==1.6.0`) to very loose (`mcp>=0.1.0`); the `[cli]` extra adds inspector tooling. Pydantic models commonly carry structured payloads (sometimes hand-registered, sometimes auto-derived via the SDK's idiom). Authors who pick this layer typically wrap their own CLI with `click`, validate config with `pydantic-settings`, and use `rich` for non-protocol output — the framework gap is filled à la carte. Appropriate when the server has a small fixed tool surface, when dependency minimalism matters (lean dep sets of 3-4 packages observed), when access-mode gating or fine-grained tool dispatch needs custom hooks the FastMCP layer hides, or when the project predates FastMCP and the migration cost outweighs the benefit. Used both for vendor servers with large tool surfaces (60+ tools) and for narrow read-only servers — the choice is taste/control rather than scale-driven. When SSE/HTTP transport is needed, often paired with Starlette since the raw SDK does not bundle a web framework.

### Python with hand-rolled MCP

Python server with no MCP framework dependency at all — the JSON-RPC stdio loop or HTTP request/response handling is implemented per server. Surfaces in monorepos where the MCP layer is thin (e.g., subprocess-wrapping a CLI tool), in serverless deployments where the SDK's process-loop assumptions don't fit (Lambda + API Gateway events bridge MCP framing onto HTTP event JSON), or when dependency footprint must be minimal (3-package surfaces observed: `python-dateutil`, `boto3`, `botocore`). Decorator-style ergonomics (`@mcp.tool()`) can be reproduced atop the custom implementation. Constrains the server to re-implement message framing, capability negotiation, and tool dispatch independently — trades SDK reuse for substrate fit. Packaging concerns get deferred to the container or Lambda layer; there is no shared pyproject when the layer is monorepo-thin.

### Node.js / TypeScript with official MCP SDK

TypeScript server built on `@modelcontextprotocol/sdk` (commonly `^1.x`), compiled with a bundler such as tsup. Distribution flows naturally over npm with a `bin` entry making `npx -y <package>` a one-liner host-config command. The SDK exposes both `StdioServerTransport` and `StreamableHTTPServerTransport` classes the server instantiates based on a launch subcommand or flag, and bundles its own HTTP and stdio transport plumbing — runtime choice doesn't pull in a separate web framework, though Hono frequently appears for the HTTP layer. Standard modern-TS scaffolding pairs it with pnpm, ESLint, Prettier, vitest, Zod for env/config validation, and Pino for structured logging. Capability surface registered programmatically per-tool in code, or — less commonly — via a sidecar declarative manifest such as `tools.json`. Appropriate when the team's primary language is TypeScript, when the upstream library being wrapped is itself JS/TS (Playwright, exa-js, Docker Hub API client) keeping the stack uniform, or when an HTTP transport with browser-style concerns (CORS) is in scope.

### Node.js with custom SDK composition

JavaScript/Node server combining the MCP SDK with vendor-specific SDKs (e.g., the Anthropic Claude Agent SDK) rather than using the MCP SDK alone. The compositional choice surfaces when the server is itself an agent-like layer that must call out to LLM APIs while exposing MCP tools, and the second SDK does work the MCP SDK does not.

### TypeScript on Bun

Same TypeScript codebase auto-detects and runs under Bun (`>=1.2`) when the runtime is Bun, otherwise falls back to Node. Bun is invoked via `bunx`. Appropriate when the project wants Bun's startup-time and footprint advantages without forcing it on users. The dual-runtime path requires the project to avoid Node-only or Bun-only APIs and to test both runtimes in CI.

### TypeScript on Cloudflare Workers (V8 isolate)

Not Node — the server runs as a Cloudflare Worker in a V8 isolate runtime, deployed via Wrangler. The same TypeScript MCP SDK is used, but the surrounding stack (Workers Bindings, KV, Durable Objects) replaces Node primitives. Appropriate for hosted/remote-only deployments where the author also operates the runtime. Constrains transport to HTTP-style (Workers don't speak stdio); constrains distribution to "remote URL" rather than "installable package."

### .NET / C#

C# MCP server compiled to a .NET binary. Surfaces in vendor-authored servers where the rest of the org's tooling and developer ecosystem is .NET-centric (Visual Studio, NuGet). Distribution naturally flows to NuGet packages and, secondarily, to Docker images and IDE-extension marketplaces. The runtime choice ties the server to host platforms where .NET is a first-class citizen.

### Rust

Cargo-managed Rust crate exposing both library APIs and CLI binaries. Two distinct ecosystem patterns surface: a `rmcp`-based stack atop the Tokio async runtime with `axum` providing HTTP transport (chosen for performance and memory-safety properties, typically by vendors who already ship Rust internally), and generic-adapter shapes that turn external schema (GraphQL operation definitions) into MCP tools at runtime. Server scaffolding sometimes uses a builder pattern (`ServerConfig::with_name().with_version().with_tool()`) and exposes a project-scaffold generator (`mcpr generate-project`) for downstream authors. Distribution flows through crates.io, pre-built GitHub release binaries, and Docker images built from the binary. Build artifact is a single static binary, which interacts well with container-only distribution but raises the bar for casual contributors and rules out the npx/uvx convenience flows that dominate JS/Python ecosystems.

### Clojure with nREPL bridge

Clojure JVM runtime exposing MCP tool calls as nREPL evaluations. The MCP protocol is bridged onto a REPL connection rather than a process-IO transport — tool invocations become forms evaluated in the running REPL. Appropriate when the target ecosystem (Clojure, ClojureScript via Shadow-cljs, Babashka, Basilisp, Scittle) is itself REPL-driven and structure-aware editing requires live access to a running runtime. Constrains the user to start an nREPL process and keep it co-resident; opens the door to multi-environment detection and switching between REPL flavors at runtime.

## Transport

The wire protocol carrying MCP messages between host and server. Constrains deployment shape (in-process subprocess vs networked service), authentication options (no-auth vs bearer/OAuth), tenancy ceiling, and where the server can run.

### stdio

JSON-RPC over the server process's stdin/stdout, with the host launching the server as a subprocess and communicating over its pipes. Default and most-common path across runtimes — Python, Node, .NET, Docker-containerized servers all converge here. Implies single-tenant by construction (one process, one user/session), no in-protocol authentication on the wire (the host's process boundary is the trust boundary; servers inherit credentials from the host's environment), and host-driven lifecycle. Forces logging off stdout to avoid corrupting the JSON-RPC frame — file-based logs (e.g., `~/<server>.log`) are a common consequence. Often the only transport offered by simpler servers, and always the fallback when authors offer multiple. Appropriate for desktop assistants (Claude Desktop, Cursor, VS Code) where the host owns the process lifecycle.

### Streamable HTTP

Long-running HTTP endpoint (e.g., `/mcp`) supporting both request/response and streamed responses with stateful sessions; the current preferred network transport. Typically built with Hono on Node, with the Workers runtime, or with axum on Rust. Requires the server to bind a port and brings HTTP-stack concerns into scope: CORS origin configuration, host/port env vars, and (where chosen) bearer-token or OAuth authentication on top. Lets the server run remotely, serve multiple concurrent clients, and front an OAuth/JWT flow. Appropriate when the server is hosted, when the deployment is containerized behind a reverse proxy, when multiple concurrent clients share an instance, or when local deployments need multi-client access. Bin shows it offered as an alternative to stdio in the same binary, not always as a replacement.

### SSE (Server-Sent Events)

Older HTTP-based long-lived stream from server to client (sometimes paired with a separate POST channel for client→server) used as the streaming transport for remote MCP servers. Listed as supported-but-deprecated in newer SDKs, often offered alongside Streamable HTTP for backward compatibility — same Worker or process exposes `/sse` for older clients while `/mcp` serves newer ones. New work selects streamable-HTTP instead; SSE persists where backward compatibility for already-deployed clients matters. Some Rust libraries' SSE paths were yanked due to bugs; some projects document dated removal events (e.g., SSE removal on 2025-05-26) with planned Streamable HTTP replacements.

### HTTP via API Gateway in front of Lambda

The MCP-over-HTTP endpoint exposed as an API Gateway route that invokes a Lambda handler implementing the protocol. Inherently HTTP, no stdio path. Appropriate when the server must be reachable by remote clients, when serverless cost/scale economics fit the workload, and when authentication can be delegated upstream to API Gateway authorizers. Constrains the server to per-request statelessness (sessions externalized to DynamoDB or similar) and to Lambda response-size limits (streaming responses become a concern).

### Hosted remote endpoint

The vendor operates the server at a public URL (e.g., `https://mcp.<vendor>.ai/mcp`) and the host is configured to point at the URL rather than launching anything locally. Eliminates install ceremony and centralizes upgrades on the vendor, but pushes authentication, rate limiting, and tenant scoping fully to the server side. Typically paired with API-key or OAuth at the HTTP boundary.

### nREPL connection

JSON-RPC layered over an nREPL session rather than process IO. The MCP server is itself driven through the REPL protocol. Appropriate only when the target language ecosystem already centers on nREPL; constrains every user to start a REPL.

### Stdio-to-HTTP shim on the client side

Server speaks Streamable HTTP only; an end-user shim like `mcp-remote` (npm) translates stdio (what the host knows how to spawn) into HTTP requests against the remote URL. The host's MCP config still has a `command`/`args` shape, but the args run the shim and pass it the URL. Lets remote-only servers work with stdio-only hosts. The shim handles auth handshake on the client side; the server never touches stdio.

### Selection mechanism

Cross-cutting sub-axis observed across the corpus — how a multi-transport binary chooses which transport to bind:

- **CLI flag at startup** — `--transport stdio|sse|http`, or `--stdio` boolean, with `--port`/`--host`. Explicit, scriptable, surfaces in `--help`. Common in TS and Rust servers; lowest install ceremony, lets the same artifact serve any host.
- **Environment variable** — `*_MCP_SERVER_TRANSPORT=stdio|http|sse`. Natural in container/Docker contexts where launching code already passes env.
- **Implicit default** — default to stdio; opt into HTTP by setting `PORT`. Minimal surface for the common case.
- **Separate console scripts per transport** — distinct entry points (e.g., `<server>` for stdio, `<server>-sse` for SSE). Architecturally cleaner separation but installs multiple binaries; appears where SSE/HTTP pulls in a substantial extra dependency surface (Starlette, an HTTP server) the stdio path doesn't need.
- **Container ARG/CMD** — Docker entrypoint takes `stdio` or `http` as a positional argument, so the user picks at `docker run` time. Natural when the server is container-only.
- **Implicit single mode** — server only supports one transport; nothing to select. Forces deployment shape (e.g., HTTP-only when OAuth is the auth model).

## Capability surface

What the server exposes to the LLM — tools, resources, prompts, and how the catalog is shaped and gated.

### Tools-only, hand-curated

Server registers a fixed list of tool functions authored directly in source — one or more tools and nothing else (no resources, prompts, sampling, roots). Dominant pattern. Tool counts vary widely with no clear correlation to project popularity: small handfuls (3-7) for narrowly-scoped servers like translation or search, mid-twenties for task-management or DB servers, dozens (60+) for vendor servers grouped by domain (orders, positions, watchlists), into 50+ for kitchen-sink integrations spanning file ops, code evaluation, structure-aware editing, shell execution, and agent-based analysis. Authoring effort scales linearly with tool count; the catalog is whatever the server compiles in. Common rationale for "tools only": MCP client ecosystem has widespread support for tools but uneven support for resources/prompts, and the project wants every supported client to use every feature without gaps. Constrains client UX — multi-step workflows must be modeled as composable tools rather than as prompts. Comprehensive catalogs demand strong filtering controls (profile selection, tool include/exclude flags) so callers can scope what surfaces.

### Tools plus resources

Server adds MCP resources alongside tools — typically read-only data the client can subscribe to or fetch (container stats, repository metadata, database tables and schema info as queryable URIs). Encourages the agent to treat the dataset as browsable rather than only queryable. Appropriate when the underlying domain has stateful, observable data that doesn't fit a "call this and get a response" shape. Resources are still under-supported by some clients, so authors offering them often duplicate the data via a tool for compatibility.

### Tools plus resources plus prompts

Server adds MCP prompts on top of tools and resources, offering pre-canned natural-language workflows the user can pick from a menu (e.g., a "docker-compose workflow" that walks the model through container orchestration; research-workflow prompts for literature review and analysis; operation-specific prompts auto-generated per OpenAPI operation). Appropriate when there's a complex multi-step domain workflow worth surfacing as first-class capability or when the server's domain has well-known recurring workflows that benefit from canonical prompt scaffolding. Most cloud/infra servers skip prompts; using them is a deliberate design statement.

### Bundled "agent SOPs" alongside tools

Pre-built structured operating procedures shipped with the server, separate from raw tools — opinionated workflows that compose underlying tool calls. Distinct from MCP prompts; an additional curated operational layer. Appropriate when the server author wants to ship not just API access but opinionated playbooks on top.

### Vertical skill packs

The repo ships pre-authored "skills" — markdown/prompt artifacts shaped for specific use cases (company research, code search, financial reports) that ride alongside the tool surface. The server is then "tools plus opinionated workflows," not just tools. Distinct from MCP prompts in that skills target Claude's skills system rather than the MCP `prompts` capability.

### Tool catalog as data file

The set of tools is declared in a sidecar manifest (`tools.json` / `tools.txt`) rather than registered inline in source. Authoring tools no longer requires editing TypeScript or Python; the manifest is the single edit point and the runtime loads it. Trades runtime flexibility (dynamic tool generation) for editability by non-developers and review-friendly diffs.

### Spec-driven dynamic tool generation

Tools, resources, and prompts materialize at server start from configuration the operator provides — one or more parsed OpenAPI specs, a set of GraphQL operation definitions, or similar schema. No hand-authored tool definitions; the spec is the source of truth, and operators shape the catalog by choosing which operations to expose without touching server code. GET-with-query-params maps to MCP tools (LLMs handle parameterized search better as tools than resources); other GETs become resources; mutating operations become tools. Auto-enriched descriptions (response codes, parameter examples) materially reduce token cost vs naive rendering. Appropriate when the upstream API has well-maintained OpenAPI/GraphQL documentation and when the server is meant to front a moving target without per-version code changes. Constrains LLM behavior to whatever description quality the spec carries; every spec change is a contract change for the agent.

### Single code-execution tool with sandbox

A single tool accepts a code string (e.g., a `boto3` Python snippet) and executes it server-side under an AST validator + import allowlist. Replaces N hand-enumerated per-API tools with one flexible primitive. Appropriate when the underlying SDK is too large to enumerate, when LLM agility (composing API calls in one call) matters more than tool-level discoverability, and when the sandboxing mechanism is trustworthy enough for the deployment context. Constrains the security surface to the sandbox quality. Cross-role: see *Sandboxing*.

### Auto-routing across backends

Single logical tool (e.g., `search`) dispatches internally to one of multiple backend models (Sonar Pro / Sonar Reasoning / Sonar Deep Research) based on a complexity heuristic. The LLM picks "what to do," the server picks "which engine." Inverts the conventional surface where each backend gets its own tool name. Override parameter (`force_model`) lets the LLM bypass the heuristic when needed.

### Partition-scoped tool gating

Same server binary exposes a different tool set depending on a runtime-selected partition (e.g., AWS global vs China). Search/recommend tools surface in one partition; service-discovery tools surface in the other. Appropriate when the upstream backend itself differs by deployment region/cloud and a single binary should serve all.

### Capability gating flags

Server takes startup flags or env vars that disable subsets of its capability surface (`--disable-write`, `--disable-delete`, `--disable-kubectl`, `--disable-helm`, `--enable-write-tools` for opt-in mutations). Lets a single binary serve "read-only kiosk" and "full admin" deployments from the same image. Granularity matters: per-verb flags compose with per-tool-family flags so operators dial in exactly what an agent should be permitted to do. Reduces blast radius of an LLM accidentally invoking a destructive operation. Cross-role: see *Default-permissions posture*.

### Progressive trust gating

Destructive operations (writes, drops) gated behind separate boolean env vars rather than a single read-only toggle (`*_ALLOW_WRITE_ACCESS` plus a separate `*_ALLOW_DROP`). Two-step opt-in for destructive surface; finer-grained than the binary read-only knob common elsewhere.

### Tool consolidation as design pressure

Authors actively reduce tool counts (one repo went from 46 atomic tools to 17 meta-tools) as a deliberate response to LLM discovery and parameter-validation pressure — too many narrow tools confuse model selection; broader meta-tools with more parameters work better. Surfaces as an explicit narrative choice, not just an emergent count.

### Self-reflective analytics tool

Tool exposes aggregated observations of the server's own past calls (`analyze_usage_patterns`, `get_translation_history`) back to the LLM. Implies local persistence of call history (atypical of the otherwise-stateless MCP server pattern) and surfaces the server's own behavior as a queryable resource.

### Capability probing and conditional surfacing

Optional capabilities (e.g., reranking) only surface when probed-at-start checks pass — the right region is configured and the IAM identity has the necessary permissions. Replaces tool-call-time failure with start-time exclusion. Appropriate when capabilities are credential- or region-conditional and users benefit from never seeing what won't work.

## Configuration delivery

How runtime configuration (credentials, modes, endpoints, feature flags) reaches the server process at launch and during operation.

### Environment variables

The dominant path. Required and optional settings — credentials, connection strings, ports, feature toggles, regions/profiles, host overrides — read from `os.environ` (or equivalent) at process start. Common keys follow vendor-prefixed conventions: `<TOOL>_API_KEY`, `<TOOL>_HOST`, `<TOOL>_MCP_SERVER_TRANSPORT`, `AWS_PROFILE`, `AWS_REGION`, `FASTMCP_LOG_LEVEL`, `DOCKER_HOST`, `DATABASE_URI`, `JUPYTER_TOKEN`. Provider-prefixed patterns like `CHROMA_<PROVIDER>_API_KEY` give uniform surfaces across embedding back-ends. Compatible with every host-config format (each host has its own way of injecting env vars at subprocess launch) and with container runtimes (Docker `-e` flags). Often paired with Zod or Pydantic validation so misconfiguration fails loudly at startup. Tends to dominate when stdio transport is the primary path because the launching host owns the environment.

### CLI flags

Settings passed as command-line arguments at launch (`--api-key`, `--connection-string`, `--transport`, `--port`, `--storage-path`, `--client-type`, `--api-name`, `--spec-url`, `--include-tags`, `--exclude-tags`, `--enable-write-tools`, `--verbose`). Coexists with env vars; resolution priority typically CLI > env > file when multiple sources collide. Used either alongside env vars or as the primary surface for the network-mode entry point. Authors use flags when they want the host-config snippet self-documenting at a glance, when the value is intrinsically per-launch (transport choice, port), when configuration is structurally part of the server's identity (which spec to mount, which backing store to use), or when operationally-meaningful switches should be visible in process lists and shell history (capability gating, transport selection).

### Dotenv file

`.env` file in the project directory or server working directory, loaded at startup via `python-dotenv` or Node equivalents. Mostly a developer-convenience layer over env vars; the production path remains environment variables. Resolution lands at the bottom of the priority chain (CLI > env > .env). Used for HTTP-mode servers where there is no host process to inject env, and for local development; brings PORT, HOST, CORS_ORIGIN, NODE_ENV alongside upstream credentials. Sometimes referenced via a `--dotenv-path` flag, layered on top of env-var resolution.

### MCP host JSON config

Indirect — the host's `mcpServers` JSON block specifies the launch command, args, and env that reach the server. Every locally-installed MCP server lives downstream of this; the README's job is to provide the JSON snippet. The user-facing surface; the server itself never reads this file.

### Persistent OS-native config

Settings stored in a platform-appropriate config directory via `platformdirs` (`~/.config/<app>/` on Linux, `%APPDATA%\<app>\` on Windows), written by a management subcommand of the same binary (`set-api-key`, etc.). Survives across launches without per-host env-var setup. Unusual in this corpus — most MCP servers leave persistence to the host's MCP config JSON and read only from env at runtime.

### Per-tool enablement file

JSON or similar file (`tools.json`) referenced by env var (`POSTGRES_TOOLS_CONFIG`) that toggles individual tools on/off. Used to reduce the LLM-visible tool surface without forking the server. Sits orthogonal to credential config — same server, different tool subset per deployment.

### Sidecar config files

A JSON, YAML, TOML, or language-native data-format file (`mcp-config.json`, `gordon-mcp.yml`, `.clojure-mcp/config.edn`) sits next to the binary and supplies tool definitions, vendor-specific integration settings, operation definitions, or runtime parameters. Used when configuration is too large or structured for env vars and needs to be checked into a repo or shared between deployments, when the configuration shape is rich (tool filters, profile selection, formatting preferences), or when ops teams already manage config files for the upstream system.

### Framework-native config file

Config file consumed by the server framework itself rather than by application code (`fastmcp.json` for FastMCP). Carries framework-level settings (transport defaults, runtime options) that don't belong in env vars or CLI. Coexists with the application's env-var surface.

### Mounted credentials

Credentials delivered to a containerized server by host volume mounts — kubeconfig, cloud-provider credential files (`~/.aws/credentials`). Implies the container runtime is the integration point and that the operator manages credential rotation outside the MCP layer. Appropriate when the credential format is established and the user already manages it externally.

### Wrangler config (Cloudflare Workers)

`wrangler.toml`/`wrangler.jsonc` per Worker controls deployment-time configuration (bindings, routes, secrets). Appropriate only for Workers-deployed servers; replaces the env-var/CLI surface for runtime config that doesn't change per-request.

### Host config file as primary delivery

For hosted-endpoint distributions, "configuration" is mostly the JSON snippet that the host (Cursor, Claude Desktop, VS Code) keeps in its own config directory pointing at the URL. The server itself has near-zero local config — the host's config file is the integration point.

## Authentication

How the server verifies callers (when relevant) and how upstream credentials reach it. Where the trust boundary sits and what proves identity at it.

### None / implicit

Server runs with whatever credentials the host process has and trusts the local execution environment. The host launched it, the OS sandboxes it, no further auth is needed. Also covers servers fronting public unauthenticated upstreams (PubMed, AWS public docs, arXiv search) that enforce only client-side rate limits, and browser-automation servers against the public web where auth is a property of the browsing session managed by the underlying engine (Playwright cookies/state) rather than of the MCP layer. Appropriate when single-tenant local deployment is the only mode supported or when the upstream itself requires no auth.

### Service API key / token in env

The server reads a long-lived API key, token, or token pair from environment variables (`PERPLEXITY_API_KEY`, `EARTHDATA_PASSWORD`, `JUPYTER_TOKEN`, `MCP_TOKEN`, `HUB_PAT_TOKEN`, `EXA_API_KEY`, `ES_API_KEY`, PagerDuty user token, Alpaca key+secret) and uses it on every upstream call. Single-tenant by construction — one credential, one identity. The server itself does not re-authenticate the MCP caller; trust derives from the transport (stdio) or surrounding network controls. Some servers add a credential-resolution priority chain (CLI > env > file) so multiple sources can coexist. Often uses a provider-prefixed convention (`CHROMA_OPENAI_API_KEY`, `CHROMA_COHERE_API_KEY`) when the server fronts a SaaS API authenticating per-call with a static key. README guidance commonly emphasizes least-privilege upstream accounts and "never commit" hygiene because the credential is ambient to the process. The dominant pattern for SaaS-API-wrapping servers.

### Database connection string

Username/password embedded in a `postgres://user:pass@host:port/db`-style URL (`DATABASE_URI`, `MYSQL_PASSWORD`). Supplied via env var or CLI flag. Authentication is whatever the database speaks; the MCP server is just a relay.

### Bearer token over HTTP/SSE

Bearer token required when the transport is HTTP or SSE; absent on stdio (where the process boundary is the trust boundary). Token typically generated out-of-band (`uuidgen`, `openssl rand`) and passed via env var to the server. Dev-mode override flag (`*_AUTH_DISABLED=true`) lets authors run unauthenticated locally without code changes.

### JWT

HTTP-mode opt-in: client presents a JWT bearer token, server validates the signature against a configured secret (often required to be 32+ chars). Appropriate when multiple clients share a hosted server and the operator wants to gate access without running an OAuth provider.

### OAuth 2.x with issuer + JWKS (HTTP-mode)

Optional bearer-token validation against a configured OAuth issuer and JWKS endpoint, available only on streamable-HTTP transport. Adds genuine MCP-caller authentication on top of the transport. Configured via env vars naming the issuer and JWKS URLs. Appropriate when the server is exposed over a network and callers must be distinguished/authorized.

### OAuth 2.1 / OIDC delegated

Server delegates auth to an OIDC provider (Auth0, Cloudflare's own auth, etc.) and accepts bearer tokens issued by it. Appropriate for production hosted deployments needing real per-user auth, scope-based authorization, or integration with an existing identity stack. Constrains transport (HTTP-only) and adds operational dependencies (the IdP).

### OAuth 2.1 per-user (upstream-bound)

Per-request user identity established via OAuth 2.1 against the upstream provider. The host opens a browser on first connect; the server holds per-user tokens and routes each MCP call under the calling user's identity. Forces HTTP transport (stdio has no concept of "this request belongs to user X") and unlocks true multi-tenant operation on a single process. Local development typically requires a tunneling tool (ngrok) to expose the OAuth callback URL. The cleanest model for SaaS tools whose data is naturally per-user (Slack, GitHub).

### Per-request bearer token (provider-scoped)

Hosted server expects each request to carry a credential scoped to the upstream provider's account (e.g., a Cloudflare API token). The server itself is account-agnostic; tenancy is determined per-call by which token arrived. Appropriate for first-party hosted servers fronting a multi-tenant platform — the same Worker serves any account that authenticates.

### Layered auth (protocol-level + upstream-level)

Server distinguishes "auth to the MCP interface" (e.g., `MCP_TOKEN`) from "auth to the upstream system" (e.g., `JUPYTER_TOKEN`). Appropriate when the MCP server brokers access to a separate authenticated system and the operator wants independent control over who can talk to MCP versus what MCP does upstream. Often a v1.x change after starting with the upstream credential alone.

### Multi-method selector

Server supports several auth methods (Basic, OAuth client credentials, API key) and selects between them via a config switch (`SERVICENOW_AUTH_TYPE` env var). Common where the upstream system is enterprise SaaS whose customers mandate different auth shapes; the server cannot pick just one without losing deployments. Adds documentation surface but avoids forking the codebase per auth flow.

### Cloud-platform credential chain

Server defers to the platform's standard credential-discovery chain (DefaultAzureCredential, AWS credential chain — env vars, `~/.aws/credentials`, instance profile, AWS SSO, STS session tokens, instance roles, managed identity). The server doesn't see the credentials directly; the upstream client library resolves them. Appropriate when the upstream has a well-established credential resolution convention and the user already manages it. Constrains tenancy to whatever profile/region is active at process launch.

### Mounted file credentials

Kubeconfig or cloud-provider credential files mounted into the container; the server reads them at startup. Same posture as the credential chain, but explicitly file-based and operator-controlled at deploy time.

### Per-spec authentication

Each upstream API mounted into the server can carry its own auth config (Basic, Bearer, API key in header/query/cookie, AWS Cognito). Appropriate when the server composes many APIs and each has its own credential context.

### Upstream-delegated (gateway authorizer)

Authentication happens before the request reaches the server — a Lambda authorizer or API Gateway validates bearer tokens in the `Authorization` header and the application code never sees raw credentials. Appropriate when the deployment substrate has its own auth tier and re-implementing it inside the server adds no value.

### Delegated to upstream toolchain credentials

The server does not authenticate at all on its own — it shells out to a tool (kubectl, helm) that already knows how to read its own credential file (kubeconfig). The MCP server's auth surface is then "whatever the upstream CLI accepts." Inherits the upstream's RBAC and identity model wholesale, which is a feature when the host machine is already the user's working environment.

### Optional external LLM API keys

Server is locally trusted but optionally calls out to external LLMs (Anthropic, OpenAI, Google Gemini) for agent-augmented tools; those keys come from env vars when present. Appropriate when the server's core function works without LLM access but optional features benefit from it.

### Per-tool varied (monorepo)

In monorepos that ship many independent servers (one per wrapped tool), authentication varies per server — some need API keys (vulnerability databases), others need none (local CLI wrappers). The container env injection mechanism is uniform; the credentials inside it are tool-specific.

## Multi-tenancy and resource scoping

Whether and how a single server instance can serve multiple users or workspaces, and what enforces the boundary.

### Single-user per process

One credential set, one user/workspace context per running server. Switching users means relaunching with different credentials. The default for stdio servers (process boundary equals trust boundary) and for most SaaS-API-wrapping servers (one API key, one identity). No code complexity; matches the host-launches-subprocess model perfectly. Made structurally inevitable by stdio transport. Some servers (e.g., AWS API server) explicitly document the boundary in the README rather than leaving it implicit.

### HTTP-stateful, single-tenant

HTTP transport with stateful sessions, but still bound to one upstream credential set per server instance — sessions are MCP-protocol state, not tenant separation. Per-request tenant switching is explicitly out of scope.

### Multi-client sharing one process via session multiplexing

HTTP server with per-session state — multiple clients connect to the same process, each session keyed by transport-level identity (cookie, header, or token). Appropriate for HTTP servers where startup cost is non-trivial or where shared in-memory state (caches, connection pools) helps performance. Makes per-tool side effects (e.g., file writes) much harder to reason about, so this path tends to coexist with read-only or stateless tool surfaces.

### Per-request tenancy via middleware

HTTP-mode server allows per-request connection overrides through middleware-managed context state — incoming request can carry connection settings that override the process defaults for the duration of that call. Closest the corpus comes to true multi-tenancy. Requires HTTP transport (stdio has no per-request channel for this) and a middleware extension point.

### Per-request tenancy with externalized session state

Each request carries its own tenant identity; persistent session state is held in an external store (e.g., DynamoDB) keyed by session ID. Appropriate for HTTP/serverless deployments where the process is shared across users and statelessness is enforced by the substrate.

### Per-request tenancy by inbound credential

Hosted server is account-agnostic; tenancy is determined entirely by the bearer token on each request. Same Worker serves any authenticated account; nothing in the server's state binds it to one user. Appropriate for first-party platform-as-a-service deployments where the platform's existing auth model is the source of truth.

### Per-user via OAuth

Specialization of per-request tenancy where the identity-bearer is an OAuth token tied to a real upstream user account, so each request executes under that user's permissions in the upstream system. Cleanest model for SaaS tools whose data is naturally per-user (Slack, GitHub).

### Workspace-scoped sandboxing within a single tenant

Server constrains per-session operations to a configured base directory or working tree (e.g., git operations confined to `BASE_DIR`). Tenancy is still single-user, but file-system access is segmented per session within that user's allowed space. Appropriate when the underlying tool (git, file ops) would otherwise be free to roam the whole filesystem and the operator wants explicit boundaries.

### Single connection per server instance

Database servers that hold one connection (per the supplied connection string) for the process lifetime. Effectively single-tenant; the workaround for multiple connections is multiple server instances.

### Stateless read-only (any number of instances)

No credentials, no per-user state — any number of instances can run concurrently because there is no shared mutable state. Applies to public-doc-fetching servers.

### Tag-based resource scoping

Server-side filtering of which upstream resources are visible based on a tagging convention (e.g., AWS resource tag `mcp-multirag-kb=true`, overridable via env var). Tag enforcement happens at the server, not in LLM prompts. Appropriate when the upstream account contains many resources and the user wants to limit MCP visibility without building app-level access control. Treats infrastructure tagging as the access-control boundary.

### Multi-spec composition

Single server fronts multiple upstream APIs concurrently; each spec has its own HTTP client and auth. Appropriate when the server is positioned as a gateway between one MCP host and many SaaS APIs.

### Mode-switched backing store

Single binary supports multiple backing-store targets (in-memory ephemeral, durable local, remote self-hosted, SaaS) chosen at launch via flags. Appropriate when the same protocol surface should adapt to radically different deployment economics without forking the server. Replaces "multiple servers per backend" with "one server, mode flag."

### N/A (library, not a runtime)

Project ships scaffolding and primitives; tenancy is the consumer's concern. Appropriate for SDK/framework projects (`mcpr`, MCP-server-building libraries) that don't operate a server themselves.

## Distribution channel

How end users and host configs obtain a runnable server. Constrains the install command shown in host config and the friction of getting started.

### PyPI via uvx (zero-install)

Python package published to PyPI; users invoke `uvx <package>@latest` or `uv run --with <name>` and `uv` resolves, downloads, and runs in an ephemeral environment. Becomes the canonical install command in host-config snippets (`command: "uvx"`, `args: ["<package>@latest"]`). Optional extras swap in alternative engines (`[chdb]` for embedded analytics, `[yaml]`, `[prometheus]`, `[pdf]`). Lowest user-side install ceremony for Python; requires `uv` on the user's system. Frequently the canonical README install path. The `uv tool install <package>` form persists the binary in the user's tool dir; `uvx` form fetches per-invocation.

### PyPI via pip / pipx

Standard `pip install <package>` (or `pip install '<package>[extra]'`, `uv pip install`, `pipx install`) followed by invoking the console script registered in `[project.scripts]`. Coexists with the `uvx` path on the same PyPI release; chosen by users who prefer a managed venv over uv's ephemeral environments. Editable installs (`pip install -e .[dev]`) for development. Optional extras gate heavier dependencies behind explicit user opt-in. Appropriate when the consumer base is Python-aware and willing to manage a venv.

### Install-from-git via uvx

Python server distributed without any registry publication — users install via `uvx --from git+https://github.com/<owner>/<repo> <command>`. The git URL becomes the effective package index; updates require pulling fresh, and there is no version range to pin. Surfaces when authors want zero registry-publication overhead, or treat the project as internal/team-scoped without a marketing release.

### npm via npx / bunx

Node/Bun servers published to npm; users invoke `npx -y @scope/package@latest` or `bunx ...` directly from host config. Lowest-friction Node path — single host-config line with no install step. Bin entries in `package.json` make the package itself the executable. On Windows the same command is wrapped as `cmd /c npx ...` to navigate shell quoting. Mirrors the uvx experience for the JS ecosystem.

### NuGet

.NET packages on NuGet for C# servers, slotting into the .NET ecosystem's standard package manager. Often co-distributed with IDE-extension marketplace publications (Visual Studio Marketplace, IntelliJ Marketplace, Eclipse Marketplace) so the server reaches users through their IDE's native install flow.

### Cargo crate / cargo install

Rust packages distributed via crates.io. `cargo add` for library use, `cargo install` for CLI tools. Constrains end users to having a Rust toolchain (or accepting pre-built binaries from another channel). Appropriate for the Rust ecosystem.

### Pre-built binary release

Cross-compiled binaries attached to GitHub releases (used by Rust servers). Appropriate when the runtime has no interpreter on the user's machine and source build is impractical.

### Docker image

Container image distributed via a registry (Docker Hub, GitHub Container Registry `ghcr.io`, AWS public ECR, vendor registries like `docker.elastic.co/mcp/...`) and launched with `docker run` from host config. Self-contained — runtime, dependencies, and any wrapped CLI tools are baked in. Multi-arch publication (linux/amd64, arm64, arm/v7) extends platform reach. Surfaces both as the primary distribution channel (when the server wraps platform-specific binaries that would be painful to install per-host, has heavy native dependencies, or deliberately rejects local installs as in Elasticsearch MCP, Slack MCP) and as a secondary channel alongside PyPI/npm for users who prefer container isolation. Often paired with build-time tweaks (e.g., auto-remap host address from `localhost` to `host.docker.internal` on macOS/Windows, `172.17.0.1` on Linux). Sometimes the README steers users to Docker first and treats pip/uvx as fallback. Cross-role: see *Container and packaging artifacts*, *Test stack*, *Deployment artifact*.

### Smithery registry

Discovery-and-distribution registry specific to the MCP ecosystem, integrated via `npx -y @smithery/cli install <owner>/<repo> --client <host>` or via a `smithery.yaml` manifest in the repo. Adds the server to a searchable index of MCP servers; effectively a curation layer on top of npm/git. Optional, additive — the server typically also publishes to npm or PyPI directly. Lets users install a server without the upstream having to publish to PyPI or npm. Appropriate when the author wants discoverability through the registry's catalog and one-click client wiring.

### Aggregator/installer registry

Meta-registry that wraps language registries with an MCP-aware install command — Smithery (above), `mcp-get`, the Docker MCP catalog. Reduces the host-config edit step to a CLI invocation. Appropriate for servers that want to be discoverable from MCP-specific browsing surfaces, not just generic package indexes.

### Pre-built host installer / one-click install URL

URL-protocol install button or deeplink shown in README per host (Kiro, Cursor, VS Code, Windsurf, Cline, Claude Code). Bypasses JSON copy-paste entirely for supported hosts; often pre-pins the server to a hosted-endpoint URL. The lowest install friction observed; requires the host to have explicit support for the format. Appropriate as a primary-surface ergonomic when many hosts need to be supported and the author is willing to encode per-host install URLs.

### Hosted endpoint (no install)

User pastes a URL into their host's MCP config; nothing installs locally. The author runs the runtime; patches propagate without user redeploys; the server depends on platform-internal data (e.g., a Cloudflare account's resources) the operator must own. Operationally distinct from "channel" — there is no artifact to ship — but competes with the other channels for the user's adoption decision. Cross-role: see *Transport — Hosted remote endpoint*.

### Lambda deployment package

Server packaged as a Lambda deployment artifact (zip), included as a library dependency in a user's Lambda package. Appropriate for the serverless-MCP framework pattern where users deploy their own infrastructure.

### Language-native installer

Language-specific tool installer for non-Python ecosystems (e.g., `clojure -Ttools install-latest :lib io.github.bhauman/clojure-mcp :as mcp`). Appropriate when the language has its own canonical distribution mechanism that users in that ecosystem already understand.

### Windows .exe variant

Explicit Windows entry via `uv tool run --from <pkg> <pkg>.exe`. Documents that the server is reachable from Windows host configs and not just Mac/Linux.

### Source clone + bootstrap

`git clone` followed by `uv sync`, `pip install -r requirements.txt`, `npm install && npm run build`, `cargo build`, or equivalent. Always implicitly available; documented explicitly when the project lacks a registry presence or for development workflows. Path of last resort or the deliberate choice for projects that don't want to maintain registry presence. Common for newer Python projects using `uv sync` from a freshly-cloned tree. Implies the user accepts more setup overhead.

## Entry point and launch

The exact command host configs run to start the server. Determined by distribution channel and runtime, but with author-level shape choices.

### Console script via `[project.scripts]`

Python package declares `[project.scripts]` mapping a name to `module:main` (e.g., `mcp-clickhouse`, `arxiv-mcp-server`, `chroma-mcp`, `awslabs.<service>-mcp-server`, `postgres-mcp`, `earthdata-mcp-server`, `mcp-server-docker`). The script becomes available on PATH after install. Host config invokes the name directly (`uv run --with <pkg> <name>`) or via package-manager launchers. Quoted dotted names (`"awslabs.aws-api-mcp-server" = "..."`) let dotted PyPI names match dotted console-script names. Default for PyPI-distributed Python servers and the standard local-install entry point.

### npm bin via `npx`/`bunx`

Node/Bun package's `bin` field maps a command to a JS entry; `npx` or `bunx` resolves and runs it. Subcommand on the command line selects mode (HTTP default vs stdio). Universal among Node servers; the Windows variant wraps in `cmd /c`.

### Module / package CLI launcher (`python -m`, `uvx`, `npx`)

Server invoked by running the package as a module, dispatched via `__main__.py` (`python -m <package>`); or the package manager itself is the launch verb (`uvx <package>`, `npx <package>`, `bunx <package>`). Functionally equivalent to a console-script entry but visible at the package level. Common when the same binary doubles as a management CLI (subcommands like `set-api-key`, `check-config`, `test-connection`) on top of the MCP server protocol; works as the zero-install user flow without prior install.

### Bare script

A single Python (or other-runtime) file at repo root, invoked as `uv run python main.py [args]` or `python main.py`. No installable package wrapping the entry point at all. Common in container-first projects where the Dockerfile is the runtime contract and console-script registration would be ceremony for nothing, in repos that distribute by source clone rather than as a package, or as a middle ground between "script with no args" and "console script with click" — gives the author transport-selection and host/port flags without committing to a packaging surface.

### Click-based CLI wrapper (Python)

Python `click` CLI as the entry point, dispatching to FastMCP's runner internally. Adds richer argument handling than calling FastMCP's runner directly — useful when the launch surface needs flag parsing, subcommands, or help text beyond what the framework provides.

### npm scripts (start/start:stdio/start:http)

`npm start` or named scripts dispatch to the underlying entry. Appropriate as the dev-mode launch path; production users typically prefer the console-script form.

### Multiple entry points per transport

Two or more separately-installed binaries, one per transport (`<server>` for stdio, `<server>-sse` for SSE). Lets each transport carry its own dependency closure (the SSE binary pulls in Starlette; the stdio binary doesn't). Higher install ceremony in exchange for lighter runtime footprint per mode.

### Docker run / container entry

`docker run <image>` (with `-e`/`-v` flags) replaces the local console script with a containerized one. The container's `ENTRYPOINT`/`CMD` runs the server. The host's MCP config invokes Docker as the command; the entire command is what host config calls, so host-side complexity grows with mount and env requirements. Appropriate when the server is distributed as a Docker image and the user wants containerization.

### Compiled binary

Pre-built binary from a release artifact; users run the binary path directly. Appropriate for Rust/Go-style compiled servers.

### Generated binary from scaffolded project

Project generator emits a Rust crate; user runs `cargo build` and launches `target/debug/<name>`. Appropriate for SDK projects whose users build their own servers from a template.

### Library import inside a user's handler

No standalone command; the package is imported into a user-authored Lambda handler that delegates to it (`mcp.handle_request(event, context)`). Appropriate when the artifact is infrastructure for building servers rather than a server itself.

### Language-tool launcher

Language-native command (e.g., `clojure -Tmcp start`, `clojure-mcp-light` profile). Appropriate when the language toolchain provides the launcher idiom users in that ecosystem expect.

### Mounted into another runtime as an extension

Server doesn't run as its own process; it loads as an extension of an existing host (e.g., as a Jupyter Server extension). Configuration lives under `jupyter-config/`. Appropriate when the underlying system already has its own process and embedding is more efficient than running side-by-side.

## Build and packaging

How the source becomes an installable artifact.

### Hatchling (Python)

`build-backend = "hatchling.build"` in `pyproject.toml`. The most common Python build backend in the corpus; produces wheel/sdist for PyPI. Used by both standalone and monorepo-sub-package layouts; pairs with uv-managed locks.

### Poetry (Python)

Poetry as build backend with `poetry.lock` for reproducibility; can coexist with `uv` workflow on the same `pyproject.toml`. Some servers support both.

### `uv` for sync and lock

`uv sync` for reproducible dev environments and `uv.lock` for pinning. Often paired with hatchling-built packages. Per-sub-package uv projects in monorepo layouts.

### Cargo (Rust)

Standard Rust build via `Cargo.toml`/`Cargo.lock`; produces native binaries published to crates.io. Appropriate for the Rust ecosystem; consumers either install the binary or depend on the library.

### npm/Node toolchain

`package.json` defines build and bin entries; npm registry is the publish target.

### Wrangler bundle (Cloudflare Workers)

Wrangler bundles the TypeScript source into a Worker artifact and deploys directly to Cloudflare's edge. The "package" is the deployed Worker, not a downloadable file. Appropriate for Workers-targeted servers.

### Requirements-driven (legacy Python)

`requirements.txt` alongside or instead of `pyproject.toml`. Sometimes both coexist redundantly, suggesting the repo was bootstrapped from a requirements-first template before adding `pyproject.toml`.

## Python version pinning

How Python servers signal the required interpreter version to users and tools.

### `requires-python` in `pyproject.toml`

Declarative floor (`>=3.10`, `>=3.13`) read by pip/uv during install. Default among Python servers in the corpus.

### `.python-version` (pyenv-style)

Top-level dotfile read by pyenv and uv to select a local interpreter. Often paired with `requires-python` for redundancy.

### `.tool-versions` (asdf)

Multi-runtime version pin used by asdf. Rarer than pyenv-style; observed on a vendor-maintained Python server.

## Schema and types

How tool input/output schemas are produced.

### FastMCP auto-derivation from type hints

Tool function signatures with type hints become the MCP tool's input schema automatically; return types feed the output schema. Authoring effort is "write a typed Python function." Default when FastMCP is the runtime.

### Pydantic v2 models

Pydantic models for structured payloads, used both with raw `mcp` SDK (hand-registered) and alongside FastMCP for richer validation.

### Hand-authored schema (raw SDK)

When using the raw `mcp` SDK without FastMCP, tool handlers register an explicit input schema dict; the author writes the schema directly.

### Zod (TypeScript)

Zod schemas validate tool inputs and env/config in TypeScript servers. Appropriate when the server runs on Node and the surrounding stack already uses Zod for runtime validation.

## Container and packaging artifacts

Container-related files in the repo and what role each plays in build, dev, and contribution. Cross-role: see *Distribution channel — Docker image*, *Test stack*, *Deployment artifact*.

### Dockerfile (single-stage)

`Dockerfile` at repo root producing the runtime image used in production. Bakes in the language runtime, dependencies, and the server entry point. Universal across runtimes — present in nearly every sample even when not the primary distribution channel; Docker has become the lowest-common-denominator deployment shape. Typically pins a slim base image (`python:3.11-slim`, `node:22-alpine`). Sometimes adds quality-of-life touches (host-address auto-remap, entry point wrapper).

### Dockerfile (multi-stage)

Multi-stage build separating the build environment (full Node + dev deps) from the runtime environment (Alpine + production deps). Yields smaller images. Appropriate for Node servers where image size matters; Node 18-Alpine final stage is a common pattern.

### Multiple Dockerfiles

A primary `Dockerfile` plus alternates (e.g., `Dockerfile-8000`) tuned for specific deployment targets or port conventions. Appears in vendor-operated projects that publish the same artifact to several deployment platforms (EC2, ECS, EKS).

### Dockerfile.template as scaffold

A template Dockerfile parameterized for "new tool added to the monorepo" — enforces the security baseline (non-root, capability-drop, read-only mounts, resource limits) and base-image conventions across all per-tool servers. Contribution-surface artifact, not a runtime artifact.

### Hardened-by-default container posture

Dockerfile baseline includes non-root user, dropped Linux capabilities, read-only filesystem mounts, resource limits. Surfaces in security-focused projects where the wrapped CLI tools are themselves attack surface; uncommon in general-purpose MCP servers.

### Docker Compose for local dev

`docker-compose.yml` orchestrating the server alongside its backing services for local development (e.g., spinning up a database the server connects to). Distinct role from the production Dockerfile — Compose owns the dev-loop experience, the Dockerfile owns the runtime artifact. Used by HTTP-mode servers where ops want a one-command local environment.

### Docker Compose for multi-server orchestration

In monorepo-of-servers layouts, Compose orchestrates many MCP server containers together so users can bring up the full security or domain toolchain at once.

### Multi-architecture image publishing

Docker images published for linux/amd64, arm64, and arm/v7. Appropriate when the user base spans Apple Silicon, Linux x86, and lower-power ARM devices.

### Podman alternative

Documentation acknowledging Podman as a Docker alternative for the same image. Reflects environments where rootless containers or Docker-Desktop-licensing concerns push users away from Docker.

### Lambda zip

Server packaged as a Lambda deployment artifact rather than a container. Appropriate for the serverless deployment model where API Gateway is the front door.

### Devcontainer for contributors

`.devcontainer/` configuration at repo root provides a reproducible contributor environment. Appropriate for monorepos and projects with non-trivial developer setup.

### Vercel deployment config

`vercel.json` for serving the HTTP-mode server as a Vercel function. The hosted-endpoint backend pattern when the vendor doesn't run their own infrastructure.

## Test stack

How the project verifies correctness, and what infrastructure tests depend on.

### pytest with async support

`pytest` plus `pytest-asyncio` (and optionally `pytest-mock`, `pytest-cov`) for Python projects. Standard for Python servers that run any tests at all and for FastMCP-style async tools; sometimes left synchronous when tools wrap subprocess calls. Configuration variously lives in `pyproject.toml`'s `[tool.pytest.ini_options]` (newer projects, with `asyncio_mode = "auto"` and `asyncio_default_fixture_loop_scope = "function"`) or in a separate `pytest.ini` plus `requirements-dev.txt` (legacy split that survives in older repos). Tests under `tests/`. Standard discovery (`python_files = "test_*.py"`, `python_classes = "Test*"`, `testpaths = ["tests"]`). Test density varies widely with no clear correlation to project popularity.

### Live integration test gating

Custom pytest flag (`--run-live`) or marker (`live`) gates tests that hit real upstream services; default test runs stay offline. Lets the same suite serve both unit and live-integration roles without unconditional network calls.

### Branch coverage enforcement

`pytest --cov --cov-branch` for branch-level coverage measurement, beyond statement coverage.

### End-to-end protocol-conformance harness

Dedicated subdirectory (e.g., `/e2e/mcp-server-tester`) that exercises the MCP protocol surface end-to-end. Distinct from unit tests of business logic; tests that the server speaks MCP correctly.

### External agent validation artifacts

Test result files from validating the server against external agent platforms (Amazon Bedrock agents) committed to the repo as evidence of cross-platform compatibility.

### Mock transport layer for protocol-level testing

Library/SDK projects ship mock transport implementations so their tests (and downstream consumers' tests) can exercise protocol message flow without a real stdio/SSE channel. Appropriate for SDK projects where the transport layer itself is part of the public API.

### Vitest (TypeScript)

JS/TS test framework, often used in Turbo monorepos. Run via pnpm/npm scripts. Standard modern-TS choice; appropriate for TypeScript servers, particularly those that share a monorepo with a JS frontend.

### Jest (TypeScript)

Dominant TS choice in older projects; tests under `src/__tests__/` invoked via npm scripts.

### Bun test runner with Vitest compatibility

Bun's built-in test runner running Vitest-compatible specs. Pairs with the dual Node+Bun runtime — same test file works under either runner. Appropriate when the project supports both runtimes and wants to verify both.

### TypeScript noEmit type-check as the test command

`npm test` runs `tsc --noEmit` as the entire test surface. The "tests" check is purely structural (does the project type-check). Appropriate for early-stage projects with no runtime test suite yet; catches type regressions but not behavioral ones.

### Cargo test (Rust)

Implicit via `cargo test`; conventional `tests/` directory under the crate root.

### Clojure-native testing

Test directory with typical Clojure testing conventions. Appropriate when the project lives in the Clojure ecosystem and follows its idioms.

### Docker Compose for integration test infra

`test-services/` directory with a Docker Compose file spinning up real backing services (databases, etc.) for integration tests, alongside unit tests in the same `tests/` tree. Lets pytest exercise real protocol-level behavior without mocking the upstream service.

### Container-based test stack

Where Docker is the primary deployment artifact, the same image (or a sibling image) hosts the test environment so CI exercises the deployment shape rather than a synthetic one.

### Dev extras gating test deps

Test dependencies installed via `pip install -e .[dev]` (or equivalent extra). Keeps the runtime install lean.

### No tests / not surfaced

Some servers ship without a test suite; correctness verification is left to manual integration with a host. Common for hobbyist or single-author repos. Other samples don't surface test details in their README — presence of a `tests/` directory or pytest.ini is sometimes the only signal. Absence of test discussion in documentation is itself a corpus-level signal: testing is rarely a marketed feature for MCP servers.

## CI

Automated build, test, and release infrastructure triggered on commits, PRs, or releases.

### GitHub Actions

`.github/workflows/` directory with one or more workflow files. Universal across the corpus where any CI is present. Used for unit tests on PRs, lint (ruff, eslint, mdformat), type-check (mypy, pyright, tsc), release-binary cross-compilation, container image builds, PyPI/crates.io publishes, dependency audit. Workflows are split by concern (`ci.yml`, `release.yml`, `release-binaries.yml`, `release-container.yml`). Per-server projects in monorepos may share workflows at root; standalone projects have their own.

### Build + test + supply-chain scan

CI pipeline that builds the artifact (Docker image, npm/PyPI package), runs tests, and runs supply-chain scanning (e.g., Trivy for container vulnerabilities). The scan step is treated as a build gate rather than a separate concern; surfaces in security-focused projects.

### Pre-commit hooks

`.pre-commit-config.yaml` runs local checks (lint, format, secret scan) before commit. Appropriate for monorepos where consistency across many sub-packages must be enforced.

### Codecov integration

External coverage reporting service wired into the CI workflow. Coverage tracked with a Codecov badge; PRs can fail when coverage drops.

### Ruff lint config

`.ruff.toml` at root configures the Ruff linter as the project's lint authority. Common in modern Python projects.

### Secret-scan baseline

`.secrets.baseline` records known-allowed strings so the scanner doesn't flag them. Appropriate when secret-scanning is part of CI and false positives need a managed allow list.

### OSSF Scorecard

OSSF Scorecard integration emits a security posture rating. Appropriate for projects that want a public security score visible to consumers.

### Monorepo CI inheritance

Sub-server packages in a monorepo inherit the parent's CI and don't ship their own workflows.

### Turbo (build orchestrator)

Turborepo orchestrates per-package builds and tests across a monorepo. Run inside GitHub Actions. Appropriate for monorepos with multiple packages that share dependencies and want incremental, cached builds.

### Multi-system CI

Some vendors run GitHub Actions in addition to a vendor-internal CI (Buildkite). Used when the project needs to test across platform/architecture matrices the vendor's internal CI handles natively while keeping a public surface for outside contributors on GitHub Actions.

## Deployment artifact

What ops teams deploy when running the server in their environment. Distinct from *Container and packaging artifacts* (which describes what's in the repo) — this is what's shipped and run.

### Published container image

Pre-built image at a known registry (ghcr.io, AWS public ECR, Docker Hub, vendor registries). Lets users skip the local build. The unit of deployment for projects that present themselves as deployable infrastructure rather than per-user installs; README enumerates targets where it runs (EC2, ECS, EKS, AWS Marketplace). The artifact exists in a vendor registry rather than a developer's local cache. Cross-role: see *Distribution channel — Docker image*.

### Per-user local process

The opposite end of the spectrum — the artifact is the binary that runs as a subprocess of the host on the user's laptop. No separate deployment story exists; install equals deploy.

## Deployment / execution model

The runtime substrate the server is designed to run inside. Distinct from the deployment artifact — describes what runs the artifact, not what is shipped.

### Local process spawned by host

Host process launches the server as a child process, communicates over stdio, and tears it down when the session ends. Default model for stdio servers.

### Containerized local process

Host launches `docker run` as the server command; the container is a transparent execution wrapper around the same stdio loop. Appropriate when language runtimes can't be assumed on the host or when bundled native deps make installation painful.

### Serverless (Lambda + API Gateway)

Server code runs in Lambda, fronted by an HTTPS API Gateway endpoint. Per-request invocation; cold-start sensitivity; statelessness enforced by the substrate; session state externalized to DynamoDB. Appropriate when the server must be reachable by remote clients and serverless economics fit the workload.

### REPL-resident

Server code runs inside a long-lived REPL process; the host connects to the REPL. Appropriate only when the target ecosystem (Clojure / nREPL) already has REPL-driven development as the dominant idiom.

### Cloudflare Workers (V8 isolate)

Server runs on Cloudflare's edge runtime; the deployment artifact is the deployed Worker. Cross-role: see *Server runtime — TypeScript on Cloudflare Workers*.

## Host integration

Which MCP-consuming hosts the server documents direct support for, and how those configs are presented in the README.

### Claude Desktop

JSON `mcpServers` config snippet shown in README, typically pasted into `claude_desktop_config.json` on macOS/Windows. Snippet usually shows the launch command (`npx -y <pkg>`, `uvx <pkg>`, `uv run ...`, `docker run ...`) plus the env-var block. Universal floor for sample servers; nearly every server documents at least this integration. Most-documented host across the corpus.

### Claude Code

Project-level `.mcp.json` file with per-server entries. Less commonly documented than Claude Desktop but appears in monorepo layouts where many servers ship together. Sometimes paired with explicit one-click install buttons or a sibling `skills/` directory shipping Claude Code skills alongside the MCP server; sometimes no first-class wrapper exists and the host is expected to consume the generic MCP surface. A `.claude-plugin/` directory shipped in the repo with a `plugin.json` lets the server distribute itself as a Claude Code plugin alongside its other channels — typically pointing at the hosted HTTP endpoint with a custom header identifying the source.

### Cursor

JSON config snippets specific to Cursor's MCP integration (`~/.cursor/mcp.json`). Featured prominently in design-tool-integration servers and as a co-equal target in dev-oriented servers. Frequently documented alongside Claude Desktop.

### VS Code / VS Code Insiders / Visual Studio family

Visual Studio 2022, VS Code, IntelliJ IDEA, Eclipse, PyCharm — surfaces in vendor-authored servers (.NET ecosystem) where the host integration ships as an IDE extension via the platform's marketplace. JSON-snippet pattern for VS Code's `mcp.json`. Frequently documented in vendor servers offering broader cross-host coverage.

### Codex

`.codex-plugin/` integration manifest in repo root — first-class plugin shape distinct from the MCP server itself. Appropriate when the author wants to ship Codex-native ergonomics rather than relying on Codex's generic MCP consumption.

### Windsurf / Goose / Qodo Gen / Cline / Kiro

Same JSON-snippet pattern for other emerging MCP-aware IDEs and agents, or one-click install buttons via URL-protocol deep links. Whether they're documented depends on the author's familiarity; multi-host READMEs name them explicitly. Per-host one-click install URLs in README bypass JSON copy-paste entirely for supported hosts.

### Smithery registry

Server entry in the Smithery catalog; install via `@smithery/cli install <name> --client <host>`. Cross-host distribution mechanism rather than a single-host integration. Cross-role: see *Distribution channel — Smithery registry*.

### nREPL host

The host is itself a running REPL process; the server connects to it. Native to the Clojure ecosystem.

### JupyterLab as a host

Server runs as an extension inside JupyterLab and is configured via the standard Jupyter extension mechanism rather than via a separate MCP host config. Appropriate when the server brokers access to the surrounding application.

### Cloudflare AI Playground / OpenAI Responses API

First-party platform integrations for hosted-only servers. Documented when the server is platform-specific and the platform's own AI tooling is the natural client.

### Vendor-specific companion config

A first-party agent surface gets its own dedicated config file shipped with the server (`gordon-mcp.yml` for Docker's Ask Gordon). Distinct from generic host-config because the vendor has shaped the integration deeper than the standard MCP host contract allows.

### Native host connector

The host has built-in awareness of the server (Claude Desktop's native connector for exa); no manual config is needed. The lowest-friction host integration available, but limited to vendor partnerships that the host's authors have approved.

### Inspector compatibility called out

README notes compatibility with MCP Inspector (the protocol's reference debugger) as a separate item from any specific host integration.

### Generic / host-agnostic snippet

Stdio-launch instructions framed for any compliant MCP host without naming specifics. Default fallback when authors don't want to enumerate hosts; provides a generic `mcpServers` JSON entry presumed portable across MCP clients.

### Single-host snippet (Claude Desktop only)

README documents only `claude_desktop_config.json` for macOS/Windows, leaving other hosts to extrapolate.

### Cross-host coverage

README enumerates configs for multiple hosts (Claude Desktop, Cursor, VS Code, PyCharm, Gemini CLI). Vendor servers tend toward broader coverage.

### Monorepo catalog

Sub-server READMEs defer host-integration examples to the parent monorepo's catalog page.

## Observability

How the server surfaces what it's doing for operators and debuggers.

### Standard library `logging` (Python)

Python's stdlib `logging` module, default handlers. Minimal but ubiquitous.

### loguru

Python `loguru` library used for application logging — replacement logging library favored for ergonomics, structured output, formatting, and rotation without configuring stdlib logging by hand. Common in awslabs-pattern servers.

### `python-json-logger` alongside loguru

JSON-formatted log records via `python-json-logger`, used in concert with `loguru` — dual logging paths in one server, presumably one for human-readable dev output and one for ingest.

### Structured logging library (Node)

Pino (Node) for structured logging. Often paired with file rotation and a configurable log level via env var. Appropriate when the server runs as a long-lived process or in production where log searchability matters.

### `rich`-decorated stdlib logging (Python)

`rich` library decorating stdlib logging output. Same posture as Pino on the Python side.

### MCP SDK stderr logging

Default logging path provided by the MCP SDK; messages appear on stderr where the host can capture them. Configurable level via `FASTMCP_LOG_LEVEL` env var when FastMCP is in use.

### File-based logging

Logs to a file in the user's home directory (`~/<server>.log`). Forced by stdio transport, where stdout belongs to the JSON-RPC frame and any stray write corrupts the protocol. The log file is the only observability surface short of attaching a debugger.

### Container logs (stdout/stderr)

When the server runs in a container or in HTTP mode, stdout is free for log output and the container runtime captures it. Pairs naturally with cluster-level log aggregation.

### `--verbose` flag

Boolean CLI flag escalating log verbosity at launch.

### CloudWatch via Lambda

Implicit logging to CloudWatch Logs because the server runs in Lambda; X-Ray tracing can layer on. Appropriate when the deployment substrate provides a logging tier the server inherits for free.

### CloudTrail audit logging

Audit-tier logging (who called what tool when) captured in CloudTrail rather than application logs. Appropriate when the server's calls have compliance significance and a separate audit trail matters.

### Worker logs (platform-native)

Cloudflare Workers' built-in log surfacing via the dashboard. Not a self-hostable layer; the platform owns it. Appropriate only for Workers-deployed servers.

### Prometheus metrics

Optional metrics endpoint enabled via an install extra (`[prometheus]`). Appropriate when the server is deployed in observable infrastructure that already scrapes Prometheus metrics; gated behind an extra to avoid imposing on users who don't need it.

### OpenTelemetry instrumentation

OTel API + SDK as core (or optional) dependency, emitting traces and metrics to whatever collector the operator wires up. Sometimes baked into core deps so every install ships observability; sometimes optional. Appropriate for production-grade servers where the operator is expected to integrate with an observability stack.

### Health endpoint

An HTTP endpoint (e.g., `/ping` returning "pong") for liveness probes. Only meaningful in HTTP-mode deployments; appears where the server is expected to run behind a load balancer or orchestrator.

### Request context tracking for audit

Per-request structured context (request ID, session, principal) attached to every log line so audit trails can reconstruct who did what. Appropriate when the server performs mutations (file writes, git commits, DB execution) and the operator needs accountability.

### JSON-RPC notifications for capability changes

Server emits MCP-protocol notifications when tool/resource availability changes at runtime, plus startup logs of connection details and tool initialization. Appropriate when capabilities are dynamic (e.g., REPL state changes which tools are valid) and the host needs to refresh its view.

### None / unspecified

Project doesn't document logging beyond default stdout/stderr; observability is whatever the language/SDK defaults provide, with no project-level shaping. Appropriate for early-stage or single-user-stdio servers where the host's own logging is sufficient.

## Repository layout

How the codebase is organized across packages and deployment artifacts.

### Single-package (`src/<pkg>/`)

One package, one entry point — `src/<package_name>/`, tests under `tests/`, manifest at root. Default for servers that wrap one upstream service. Modern Python default; the explicit `src/` layout prevents accidental imports from the project root during testing. Optional `examples/`, `dev/`, `docs/` siblings. Same shape across Python, TypeScript, and other runtimes.

### Bare-script layout

One or two `.py` files at repo root with `requirements.txt`/`pyproject.toml` beside them. Easy to read; awkward to package for PyPI.

### Single-package Node/TS

`package.json` at root, source under `src/`, dist under `dist/` (gitignored), tests under `tests/`. `tsconfig.json` and `Dockerfile` at root. Appropriate for single-server TypeScript projects.

### Single Rust crate

`Cargo.toml` at root, source under `src/main.rs`, with `/examples` and `/e2e` subdirectories for samples and conformance tests.

### Clojure project layout

Standard Clojure layout with `src/`, `test/`, `doc/`, `resources/`, `deps.edn`, plus extensive root-level documentation files (README, PROJECT_SUMMARY, CHANGELOG, CONFIG, FAQ, BIG_IDEAS, LLM_CODE_STYLE).

### Monorepo of independent servers

Many subdirectories, each a standalone MCP server with its own Dockerfile, scripts, and tests. A `Dockerfile.template` at root acts as scaffolding for adding new servers. The repo as a whole is the contribution surface; individual servers are the deployment units.

### Monorepo of namespace-prefixed packages

Many sub-packages under `src/<name>/` each with their own `pyproject.toml`, all sharing a namespace prefix (e.g., `awslabs.*`). Central dev tooling at root (ruff, pre-commit, secrets baseline). Each sub-package independently published and installable. Appropriate when one organization ships many related servers and wants consistent tooling without combining them into one package.

### Monorepo sub-package

`src/<sub-server>/` directory inside a parent multi-server monorepo, each sub-package with its own `pyproject.toml`, console script, and PyPI release. Consumers install one sub-server without pulling siblings.

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

## Default-permissions posture

Default safety stance for mutation-capable servers — what behavior surfaces by default versus by explicit opt-in.

### Read-only by default, opt-in writes

Mutation tools registered but hidden behind a launch flag (`--enable-write-tools`) or env-var feature flag. Author's default posture is "no surprise mutations." Reduces blast radius of an LLM accidentally invoking a destructive operation. Cross-role: see *Capability surface — Capability gating flags*.

### Sandbox-mode default

Server defaults to a sandbox/paper-trading mode (e.g., `ALPACA_PAPER_TRADE=true`); production mode is opt-in. Particularly relevant for finance/trading servers where misfires have monetary consequences.

### Anti-multi-tenancy disclaimer

README explicitly states "NOT designed for multi-tenant environments." Documents the boundary rather than letting users assume.

## Sandboxing

How the server constrains what code can do when it executes user-influenced operations.

### AST validation with import allowlist

User-supplied Python code is parsed to AST, validated against an explicit allowlist of permitted imports (`boto3`, `operator`, `json`, `datetime`, `pytz`, `dateutil`, `re`, `time`), and only then executed. Appropriate for code-as-tool architectures where the LLM authors small snippets server-side. Trust depends entirely on the allowlist's tightness. Cross-role: see *Capability surface — Single code-execution tool with sandbox*.

### In-process safety enforcement via parsing

Server parses inbound payloads before forwarding (e.g., parses SQL with `pglast` to reject COMMIT/ROLLBACK in restricted mode) rather than relying on the upstream system's own permissions. Appropriate when the upstream system's permission model is too coarse (e.g., DB role) and the operator wants finer gating per-tool-call. Constrains the parser's correctness — anything it misses is a security gap.

### No sandboxing (trusted code path)

Server code runs whatever the developer wrote; user inputs are parameters, not code. Default for the hand-authored fixed tool set pattern.

## Domain-specific intelligence

Compute the server performs beyond exposing raw upstream operations.

### Pass-through tool wrappers

Tools map 1:1 onto upstream API operations (Docker SDK calls, NASA Earthdata search, Perplexity API, Jupyter kernel ops, raw SQL execution). Server's job is shape translation and credential management, not domain logic. Appropriate as the default; lowest implementation cost.

### Deterministic optimization layered on top of raw ops

Server adds analytical computation that goes beyond exposing the upstream system — workload compression, hypothetical index simulation (hypopg), Pareto-front cost-benefit selection, greedy search adapted from published algorithms. The MCP layer becomes a delivery vehicle for embedded research. Appropriate when the underlying system supports introspection (pg_stat_statements, EXPLAIN) and the author wants to encode performance expertise in tool form.

### Mode parameter for plan-vs-execute

Single tool exposes multiple output modes via a parameter (e.g., `mode: manifest|download|script` for granule downloads). Lets the model preview what would happen before committing to execution. Appropriate when the underlying operation is expensive or irreversible and the user benefits from a dry-run.

### Workflow scaffolding via MCP prompts

Server uses MCP prompts as orchestration primitives, packaging multi-step natural-language workflows (docker-compose orchestration) rather than just exposing atomic tools. Appropriate when there's a complex, repeated workflow worth canonizing. Cross-role: see *Capability surface — Tools plus resources plus prompts*.

## Extension points

Mechanisms the server exposes for users to modify behavior without forking.

### Middleware module slot

Env var (`MCP_MIDDLEWARE_MODULE`) names a Python module that intercepts FastMCP protocol events (tool calls, resource reads, prompts, listings) and can mutate context state (e.g., per-request connection overrides) or implement cross-cutting concerns (logging, tracing, performance measurement). The closest thing in the corpus to a true plugin architecture for an MCP server.

### Per-tool enablement file

JSON config file toggles individual tools without code changes. Lets deployers shrink the LLM-visible surface for safety or focus, and lets the same server image serve multiple deployment profiles. Cross-role: see *Configuration delivery — Per-tool enablement file*.

## Developer ergonomics

In-repo tooling that supports development of the server itself (not its consumers).

### Setup subcommands on the MCP binary

The same console script that runs the MCP server protocol also exposes management subcommands (`set-api-key`, `check-config`, `test-connection`) for credential setup and connectivity verification. Doubles the binary as a config CLI; uses `rich` and `click` for the human-facing output. Pattern echoes `kubectl config`-style CLIs.

### MCP framework dev config

`fastmcp.json` for FastMCP-based projects gives the framework first-class dev configuration in the repo, separate from pyproject. Lets `fastmcp` dev tooling discover the server without arg passing.

### Sample example middleware

`example_middleware.py` or equivalent demonstrating how to extend the server via a configured middleware module. Acts as both documentation and a test of the middleware extension point.

### Health-check scripts

Per-container health-check scripts in monorepo-of-servers layouts so Docker can verify each server is responsive. Tied to container deployment patterns.

### Linter and type-checker stack

Standard runtime-appropriate tooling (`ruff` for Python, ESLint+Prettier for TypeScript, `mypy`/`pyright` for typed Python projects). Wired in as dev dependencies and run in CI/pre-commit. Signals an opinionated dev environment that consumers contributing back should expect to match.

### `pre-commit` framework

Standardized hook orchestration for lint, format, and commit-message checks at commit time. Git hooks via lefthook or similar are an alternative.

### `commitizen`

Commit-message convention enforcement.

### Makefile

Shared dev targets (build, test, run) as a Makefile at repo root.

### `scripts/` directory

Repo-local dev helpers and maintenance scripts.

### In-repo docs site

Dedicated `website/` or `docs/` directory shipping a documentation site alongside the server.

## Companion in-repo Claude surface

Repo-local artifacts that signal Claude-assisted authoring or in-repo Claude tooling.

### `.claude/` directory + `CLAUDE.md`

Top-level Claude-Code workspace config plus an operational `CLAUDE.md`. Indicates Claude is part of the contributor experience for the repo itself, distinct from the server being a Claude-Code plugin.

### MseeP.ai security badge

Third-party MCP-server security-assessment badge in README. Not Claude-Code-specific but signals an emerging ecosystem of MCP-server certification.

## Versioning signals

How the project communicates change to consumers.

### Tagged release with version in changelog

Standard semver tag (e.g., `v0.3.1`, `v0.2.6`) with a changelog entry. The default expectation.

### Dated deprecation in repo

Removal events (e.g., SSE removal on 2025-05-26) documented in-repo with dates rather than buried in changelogs. Appropriate when transport or capability changes have material impact on consumers and signaling them clearly is part of the maintenance contract.

### Automated-release sentinel version

Version field in `pyproject.toml` carrying a bot-generated value (observed: `0.9223372036854775807.9223372036854775807`, int64-max sentinel) rather than a human-chosen number. Suggests the canonical version comes from a release pipeline, not the source file.

## Project status

Lifecycle state of the upstream repository.

### Active development

Recent commits, ongoing CI runs, semver-tagged releases. Default for all in-bin samples except outliers.

### Archived

Repository marked archived by the maintainer (e.g., `mcpr` archived Feb 2026). Code still functions; no further fixes. Appropriate to flag because consumers should weigh adoption risk.

## Documentation surface

How the project communicates what it is and how to use it.

### README as the canonical surface

Single README.md carrying purpose, install, config, host integration, and tool inventory. Universal. Length and depth vary widely.

### Per-host README integration sections

README has labeled sections per supported host (Claude Desktop, Cursor, Codex, etc.) showing the canonical config snippet for each. Common where the server targets multiple host ecosystems.

### README plus docs directory

Supplementary `docs/` directory for longer-form material (architecture, per-tool deep dives) referenced from README. Surfaces in larger or more mature projects.

### Multi-document deep documentation

Beyond README, the project ships PROJECT_SUMMARY, CONFIG, FAQ, BIG_IDEAS, LLM_CODE_STYLE, and similar long-form documentation. Appropriate for projects with substantial conceptual surface (50+ tools, multi-environment support) where a single README cannot cover everything.

### LLM-style guidance file

Documentation specifically aimed at LLM assistants editing the codebase (e.g., `LLM_CODE_STYLE.md`). Appropriate when contributors include AI assistants and the project wants to influence their code style.

### LLM-targeted docs file

A large in-repo file (`llm_mcp_docs.txt`, hundreds of KB) explicitly designed to be ingested by an LLM rather than read by a human. Lets agents that consume the server learn its contracts in one shot. Distinct from the LLM-style guidance file: this targets LLM consumers of the server, not LLM contributors to the codebase.

### Skills directory

A `skills/` directory with pre-authored vertical workflows (research templates, etc.). Doubles as a documentation artifact showing how the server is intended to be used in concrete domains. Cross-role: see *Capability surface — Vertical skill packs*.

### Token-cost annotations

README quantifies token impact of design choices (e.g., 70-75% token reduction from description enrichment in OpenAPI tool generation). Appropriate when token cost is part of the user's purchase decision.

### Lifecycle disclosure in README

An explicit deprecation/EOL notice at the top of the README, naming the successor product. Rarer than expected — most projects let staleness signal end-of-life implicitly; deliberate disclosure is its own quality choice.

### Archival redirect README

When a repo is superseded, the README is replaced by an archival notice pointing at the successor. Two-stage archival is a recurring shape — README declares archival on one date, the GitHub repo flag flips months later as the redirect's stability gets confirmed.
