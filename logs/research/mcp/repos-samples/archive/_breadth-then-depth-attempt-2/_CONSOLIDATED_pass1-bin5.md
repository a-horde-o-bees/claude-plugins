# Sample

Pass-1 Phase-1a partial for bin 5. Functional decomposition of designcomputer/mysql_mcp_server, docker/hub-mcp, duolingo/slack-mcp, echelon-ai-labs/servicenow-mcp, elastic/mcp-server-elasticsearch, exa-labs/exa-mcp-server, executeautomation/mcp-playwright, feiskyer/mcp-kubernetes-server — organized by role with implementation paths as sub-sections.

## Server runtime

The host language and SDK choice that owns the MCP protocol loop and the tool/resource handlers.

### Python with raw `mcp` SDK

The low-level Anthropic MCP Python SDK (`mcp>=1.0.0`). The author works directly against the protocol primitives — schemas are hand-authored, server lifecycle is explicit. Suits projects that need tight control over capability shape (e.g., exposing both resource and tool surfaces from one server), or that pre-date the FastMCP convenience layer and have not migrated. Common companion choice: a separate web framework (Starlette) when SSE/HTTP transport is needed, since the raw SDK does not bundle one.

### Python with FastMCP

`fastmcp>=2.13.0` as the high-level decorator-based wrapper over the MCP SDK. Schemas auto-derive from Python type hints, dramatically reducing boilerplate at the cost of fine control over the wire shape. Appropriate when the server's capabilities map cleanly onto typed Python functions and the author wants tools to read like ordinary code. Tends to coexist with `uv` packaging and pyproject-only configuration.

### TypeScript with `@modelcontextprotocol/sdk`

The official TS MCP SDK on Node.js. Capability surface is registered programmatically (per-tool registrations in code) or, less commonly, via a sidecar declarative manifest such as `tools.json`. Appropriate for ecosystems where the upstream library being wrapped is itself JS/TS (Playwright, exa-js, Docker Hub API client) — keeps the dependency stack uniform. Bundles its own HTTP and stdio transport plumbing, so the runtime choice does not pull in a separate web framework.

### Rust with `rmcp`

The Rust MCP SDK (`rmcp ^0.2.1`) atop the Tokio async runtime, with `axum` providing HTTP transport. Chosen for performance and memory-safety properties, typically by vendors who already ship Rust internally. The build artifact is a single static binary, which interacts well with container-only distribution but raises the bar for casual contributors.

## Transport

How JSON-RPC messages move between the host and the server process.

### stdio

JSON-RPC over the process's standard input and output. The host launches the server as a subprocess and frames messages on the pipe. Implies single-tenant by construction (one process, one client) and forces logging off stdout to avoid corrupting the frame — file-based logs (e.g., `~/<server>.log`) are a common consequence. Suits desktop hosts that already manage subprocess lifecycle and credential injection via environment variables.

### Streamable HTTP

JSON-RPC over HTTP using the streamable-HTTP profile, the current preferred network transport. Allows multiple clients to share a single long-running server process, opens the door to per-request authentication (OAuth, header-scoped tokens), and is the prerequisite for hosted/remote endpoints. Configured either by a CLI flag selecting the transport at startup, by a separate console script, or — for vendors operating a hosted endpoint — as the default with no local process at all.

### SSE (Server-Sent Events)

The earlier HTTP-streaming profile, now deprecated in newer SDKs but still shipping in some servers, occasionally exposed as a separately-named binary (e.g., `<server>-sse`). New work selects streamable-HTTP instead; SSE persists where backward compatibility for already-deployed clients matters.

### Hosted remote endpoint

The vendor operates the server at a public URL (e.g., `https://mcp.<vendor>.ai/mcp`) and the host is configured to point at the URL rather than launching anything locally. Eliminates install ceremony and centralizes upgrades on the vendor, but pushes authentication, rate limiting, and tenant scoping fully to the server side. Typically paired with API-key or OAuth at the HTTP boundary.

### Transport selection mechanism

Cross-cutting sub-axis observed in this bin:

- **CLI flag at startup** — one binary with `--transport stdio|http` (and `--port`/`--host`). Common in TS and Rust servers; lowest install ceremony, lets the same artifact serve any host.
- **Separate console scripts per transport** — distinct entry points (e.g., `<server>` for stdio, `<server>-sse` for SSE). Architecturally cleaner separation but installs multiple binaries; appears where the SSE/HTTP path pulls in a substantial extra dependency surface (Starlette, an HTTP server) that the stdio path doesn't need.
- **Container ARG/CMD** — the docker entrypoint takes `stdio` or `http` as a positional argument, so the user picks at `docker run` time. Natural when the server is container-only.
- **Implicit single mode** — the server only supports one transport, so there is nothing to select. Forces the deployment shape (e.g., HTTP-only when OAuth is the auth model).

## Authentication

How the server proves the caller is allowed to invoke its tools, and how it presents itself to the upstream system being wrapped.

### Static credential in environment

The server reads a username/password, API key, or personal access token from environment variables (`MYSQL_PASSWORD`, `EXA_API_KEY`, `HUB_PAT_TOKEN`, `ES_API_KEY`). Single-tenant by construction — one credential per process. Trivially compatible with stdio transport, since the host injects env vars when spawning. README guidance commonly emphasizes least-privilege upstream accounts and "never commit" hygiene because the credential is ambient to the process.

### Multi-method selector

The server supports several auth methods (Basic, OAuth client credentials, API key) and selects between them via a config switch (`SERVICENOW_AUTH_TYPE` env var). Common where the upstream system is enterprise SaaS whose customers mandate different auth shapes; the server cannot pick just one without losing deployments. Adds documentation surface but avoids forking the codebase per auth flow.

### OAuth 2.1 per-user

Per-request user identity established via OAuth 2.1 against the upstream provider. The host opens a browser on first connect; the server holds per-user tokens and routes each MCP call under the calling user's identity. Forces HTTP transport (stdio has no concept of "this request belongs to user X") and unlocks true multi-tenant operation on a single process. Local development typically requires a tunneling tool (ngrok) to expose the OAuth callback URL.

### Delegated to upstream toolchain credentials

The server does not authenticate at all on its own — it shells out to a tool (kubectl, helm) that already knows how to read its own credential file (kubeconfig). The MCP server's auth surface is then "whatever the upstream CLI accepts." Inherits the upstream's RBAC and identity model wholesale, which is a feature when the host machine is already the user's working environment.

### None (public-data scope)

Browser automation against the public web has no service-level identity to assert; auth is a property of the browsing session managed by the underlying engine (Playwright cookies/state), not of the MCP layer. Common for scraping/testing servers.

## Multi-tenancy

How the server scopes one process across one or many simultaneous users.

### Single-user-per-process

One credential, one upstream connection, one effective user. The host runs a fresh server per user (or per workspace). Default for stdio transport and for static-credential auth. Simplest mental model; scales by spawning more processes.

### Per-client-via-HTTP

The HTTP server distinguishes clients by transport-level identity (header, URL parameter, OAuth token) and isolates state per call. Prerequisite for hosted endpoints serving many users from one process. Makes per-tool side effects (e.g., file writes) much harder to reason about, so this path tends to coexist with read-only or stateless tool surfaces.

### Per-user-via-OAuth

A specialization of per-client where the identity-bearer is an OAuth token tied to a real upstream user account, so each request executes under that user's permissions in the upstream system. The cleanest model for SaaS tools whose data is naturally per-user (Slack, GitHub).

## Capability surface

The shape of what the server exposes to the agent — tools, resources, prompts.

### Tools-only (procedure-centric)

Every capability is a callable tool with parameters. The agent reasons "which tool do I call." Default and dominant pattern; matches well to action-oriented integrations (run a query, post a message, take a screenshot).

### Tools plus resources

In addition to tools, the server exposes addressable read-only resources (e.g., MySQL tables as resources, where the agent can list them and read their contents without invoking a tool). Encourages the agent to treat the dataset as browsable rather than only queryable. Rare among the bin's database servers and called out as a deliberate choice when it appears.

### Tool catalog as data file

The set of tools is declared in a sidecar manifest (`tools.json` / `tools.txt`) rather than registered inline in source. Authoring tools no longer requires editing TypeScript; the manifest is the single edit point and the runtime loads it. Trades some runtime flexibility (dynamic tool generation) for editability by non-developers and review-friendly diffs.

### Capability gating flags

Independent of how tools are declared, the server takes startup flags that disable subsets of its capability surface (`--disable-write`, `--disable-delete`, `--disable-kubectl`, `--disable-helm`). Lets a single binary serve "read-only kiosk" and "full admin" deployments from the same image. Granularity matters: per-verb flags (write/delete) compose with per-tool-family flags (kubectl/helm) so operators dial in exactly what an agent should be permitted to do.

### Vertical skill packs

The repo ships pre-authored "skills" — markdown/prompt artifacts shaped for specific use cases (company research, code search, financial reports) that ride alongside the tool surface. The server is then "tools plus opinionated workflows," not just tools. Distinct from MCP prompts in that skills target Claude's skills system rather than the MCP `prompts` capability.

## Configuration delivery

How the server learns what to connect to and how to behave.

### Environment variables

The dominant path. Connection strings, credentials, ports, and feature toggles are all env vars, read at process start. Compatible with every host-config format (each host has its own way of injecting env vars at subprocess launch) and with container runtimes. Tends to dominate when stdio transport is the primary path.

### CLI flags

Used either alongside env vars (`--port`, `--host`, `--transport` for transport selection) or as the primary surface for the network-mode entry point (`servicenow-mcp-sse --instance-url=... --username=...`). Preferred for operationally-meaningful switches that should be visible in process lists and shell history (capability gating, transport selection).

### Sidecar config files

A JSON or YAML file (`mcp-config.json`, `gordon-mcp.yml`) sits next to the binary and supplies tool definitions, vendor-specific integration settings, or runtime parameters. Used when the configuration is too large or structured for env vars and needs to be checked into a repo or shared between deployments.

### Host config file as primary delivery

For hosted-endpoint distributions, "configuration" is mostly the JSON snippet that the host (Cursor, Claude Desktop, VS Code) keeps in its own config directory pointing at the URL. The server itself has near-zero local config — the host's config file is the integration point.

## Distribution channel

How the server gets onto the user's machine (or doesn't).

### Language package registry

PyPI for Python (`pip install`, `uvx`), npm for TypeScript (`npm install -g`, `npx -y`). The native channel for each language ecosystem; lowest-friction install for users already in that ecosystem. Often the canonical channel that other channels (Smithery, Docker) wrap.

### Container image

A Docker image — vendor registry (`docker.elastic.co/mcp/...`), GitHub Container Registry (`ghcr.io/...`), or Docker Hub. Everything is bundled including the runtime, eliminating "wrong Python version" classes of install failure. May be the only channel when the project deliberately rejects local installs (Elasticsearch MCP, Slack MCP), or one channel of several. Cross-role: see *Test stack* and *Deployment artifact*.

### Aggregator/installer registry

A meta-registry that wraps language registries with an MCP-aware install command — Smithery (`npx @smithery/cli install ... --client claude`), mcp-get, the Docker MCP catalog. Reduces the host-config edit step to a CLI invocation. Appropriate for servers that want to be discoverable from MCP-specific browsing surfaces, not just generic package indexes.

### Pre-built host installer

A one-click button or deeplink that the host (Cursor, VS Code) consumes to install and configure the server in one step, often with the server pre-pinned to a hosted-endpoint URL. The lowest install friction observed; requires the host to have explicit support for the format.

### Hosted endpoint (no install)

The user pastes a URL into their host's MCP config; nothing installs locally. Operationally distinct from "channel" — there is no artifact to ship — but it competes with the other channels for the user's adoption decision. See *Transport — Hosted remote endpoint*.

### Source-only

`git clone && pip install -e .` or `npm install && npm run build`. The path of last resort or the deliberate choice for projects that don't want to maintain registry presence. Common for newer Python projects using `uv sync` from a freshly-cloned tree.

## Entry point shape

What the user (or host config) actually invokes after install.

### Console script

A single named binary registered via `[project.scripts]` (Python) or `bin` (npm). Idiomatic and short to type in host configs (`mysql_mcp_server`, `mcp-kubernetes-server`). Clean separation from the package's importable module.

### Module invocation

`python -m <package>.<module>` or equivalent. Bypasses the console-script ceremony; useful when the project ships multiple entry-point modules or wants the import path to be visible. Some servers use it as their stdio default while reserving console scripts for additional transports.

### Bare script

`python main.py` — no installable package wrapping the entry point at all. Appears in container-first projects where the Dockerfile is the runtime contract and console-script registration would be ceremony for nothing.

### Multiple entry points per transport

Two or more separately-installed binaries, one per transport (`<server>` for stdio, `<server>-sse` for SSE). Lets each transport carry its own dependency closure (the SSE binary pulls in Starlette; the stdio binary doesn't). Higher install ceremony in exchange for lighter runtime footprint per mode.

## Test stack

How the project verifies itself before shipping.

### pytest (Python)

The default Python choice across the bin. Sometimes paired with `pytest-asyncio` for FastMCP-style async tools; sometimes left synchronous when tools wrap subprocess calls. Configuration variously lives in `pyproject.toml` (newer projects) or in a separate `pytest.ini` plus `requirements-dev.txt` (legacy split that survives in older repos).

### Jest (TypeScript)

The dominant TS choice; tests under `src/__tests__/` invoked via npm scripts.

### Cargo test (Rust)

Implicit via `cargo test`; conventional `tests/` directory under the crate root.

### Container-based test stack

Where Docker is the primary deployment artifact, the same image (or a sibling image) hosts the test environment so CI exercises the deployment shape rather than a synthetic one. Cross-role: see *Distribution channel — Container image*.

## CI

How tests are run automatically on changes.

### GitHub Actions

The default. Workflows under `.github/workflows/` triggered on pushes/PRs.

### Multi-system CI

Some vendors run GitHub Actions in addition to a vendor-internal CI (Buildkite). Used when the project needs to test across platform/architecture matrices the vendor's internal CI handles natively while keeping a public surface for outside contributors on GitHub Actions.

## Container / packaging artifacts

What the project ships beyond the language-native package.

### Dockerfile

Near-universal in this bin — present even when the primary distribution is npm or PyPI, used as a fallback path for users who can't or won't install via the language ecosystem. The Dockerfile typically pins a slim base image (`python:3.11-slim`, `node:22-alpine`) and runs the server through whichever of *Entry point shape*'s options the project picked.

### Multiple Dockerfiles

A primary `Dockerfile` plus alternates (`Dockerfile-8000`) tuned for specific deployment targets or port conventions. Appears in vendor-operated projects that publish the same artifact to several deployment platforms (EC2, ECS, EKS).

### docker-compose

Used to orchestrate local multi-process setups (server plus its upstream dependency, or server plus a debugging client). Far less common than a bare Dockerfile.

### Vercel deployment config

`vercel.json` for serving the HTTP-mode server as a Vercel function. The hosted-endpoint backend pattern when the vendor doesn't run their own infrastructure.

## Host integration surface

How the server tells different MCP hosts how to consume it.

### JSON config snippet per host

The README shows a JSON object the user pastes into Claude Desktop's `claude_desktop_config.json`, Cursor's `~/.cursor/mcp.json`, VS Code's `mcp.json`, and so on. Most servers list two or three; some (notably hosted endpoints) list a dozen-plus. The snippets differ in path conventions and key names but all reduce to "command + args + env" for stdio servers or "URL + headers" for HTTP/hosted servers.

### Vendor-specific companion config

A first-party agent surface gets its own dedicated config file shipped with the server (`gordon-mcp.yml` for Docker's Ask Gordon). Distinct from generic host-config because the vendor has shaped the integration deeper than the standard MCP host contract allows.

### Native host connector

The host has built-in awareness of the server (Claude Desktop's native connector for exa); no manual config is needed. The lowest-friction host integration available, but limited to vendor partnerships that the host's authors have approved.

### Claude Code plugin wrapper

A `.claude-plugin/` directory shipped in the repo with a `plugin.json` that wires the server into the Claude Code plugin system — typically pointing at the hosted HTTP endpoint with a custom header identifying the source. Lets the server distribute itself as a Claude Code plugin alongside its other channels.

## Observability

How the running server reports what it's doing.

### File-based logging

Logs to a file in the user's home directory (`~/<server>.log`). Forced by stdio transport, where stdout belongs to the JSON-RPC frame and any stray write corrupts the protocol. The log file is the only observability surface short of attaching a debugger.

### Container logs (stdout/stderr)

When the server runs in a container or in HTTP mode, stdout is free for log output and the container runtime captures it. Pairs naturally with cluster-level log aggregation.

### Health endpoint

An HTTP endpoint (`/ping` returning "pong") for liveness probes. Only meaningful in HTTP-mode deployments; appears where the server is expected to run behind a load balancer or orchestrator.

### Unspecified / passthrough

Many servers note "comprehensive logging" or simply don't document the destination — observability is whatever the language/SDK defaults provide, with no project-level shaping.

## Deployment artifact

For projects that present themselves as deployable infrastructure rather than per-user installs.

### Container image as artifact

The Docker image is the unit of deployment, and the README enumerates targets where it runs (EC2, ECS, EKS, AWS Marketplace). Cross-role: also the primary *Distribution channel* for these projects. The artifact exists in a vendor registry rather than a developer's local cache.

### Per-user local process

The opposite end of the spectrum — the artifact is the binary that runs as a subprocess of the host on the user's laptop. No separate deployment story exists; install equals deploy.

## Documentation surface

Beyond the README, what the project ships for downstream consumption.

### LLM-targeted docs file

A large in-repo file (`llm_mcp_docs.txt`, hundreds of KB) explicitly designed to be ingested by an LLM rather than read by a human. Lets agents that consume the server learn its contracts in one shot. Rare and notable when present.

### Skills directory

A `skills/` directory with pre-authored vertical workflows (research templates, etc.). See *Capability surface — Vertical skill packs*; mentioned here because it doubles as a documentation artifact showing how the server is intended to be used in concrete domains.

### Lifecycle disclosure in README

An explicit deprecation/EOL notice at the top of the README, naming the successor product. Rarer than expected — most projects let staleness signal end-of-life implicitly; deliberate disclosure is its own quality choice.
