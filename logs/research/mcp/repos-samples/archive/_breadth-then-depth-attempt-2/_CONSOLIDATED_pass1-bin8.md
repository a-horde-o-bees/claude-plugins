# Sample

Pass-1 Phase-1a partial for bin 8. Functional decomposition of `makenotion--notion-mcp-server.md`, `mark3labs--mcp-go.md`, `marlonluo2018--pandas-mcp-server.md`, `metoro-io--mcp-golang.md`, `microsoft--playwright-mcp.md`, `misbahsy--video-audio-mcp.md`, `modelcontextprotocol--kotlin-sdk.md`, `modelcontextprotocol--servers.md`, organized by role with implementation paths as sub-sections.

## Server runtime

The language and protocol library a sample chooses to host the MCP server inside. Constrains packaging, async style, type-derivation strategy, and where the server can be embedded.

### TypeScript on Node with the official MCP SDK

Node-hosted TypeScript using the official `@modelcontextprotocol/sdk`. Authors compose Express or stdlib HTTP around the SDK when an HTTP transport is needed. Common alongside Zod for tool argument validation and openapi-client-axios when the tool surface is auto-derived from an OpenAPI spec rather than hand-authored. Appropriate when the target ecosystem is npm-distributable, hosts run a Node process directly via `npx`, and front-end tooling (esbuild, tsx, Vitest) is already familiar to the maintainer.

### Go SDK as an in-process library

The MCP server is a Go program that imports an SDK module (e.g., `github.com/mark3labs/mcp-go`, `github.com/metoro-io/mcp-golang`) and registers tools/resources/prompts via constructor and method calls. Native Go structs become tool arguments with automatic JSON-Schema generation; transport selection is a separate entry method (`server.ServeStdio`, `server.ServeSSE`, `server.ServeHTTP`) or a registration into a higher-level web framework (Gin). Appropriate when the consumer wants a single static binary, type-safe schemas without runtime reflection cost, and goroutine-based concurrency for streaming or task-augmented tools.

### Python with raw low-level MCP SDK

Python program that imports the low-level `Server` class from the `mcp` package and registers handlers explicitly, hand-authoring JSON schemas for each tool. Pairs with `hatchling` build backend, `uv` packaging, `pyright` for typing, `ruff` for lint, `pytest` (+ `pytest-asyncio` for HTTP-touching servers). Appropriate when the maintainer prioritizes spec coverage and explicit control over schema/handler shape — the canonical "pre-FastMCP" authoring style chosen by the official Python reference servers.

### Python with FastMCP-style decorators

Python program that uses FastMCP — either the standalone `fastmcp` package or `mcp[cli]>=1.x`'s embedded `mcp.server.fastmcp`. Type hints become tool argument schemas automatically; decorator-registered functions become tools. Appropriate when the maintainer prefers minimal ceremony and Pydantic-derived schemas over hand-authored JSON; common in single-file `server.py` projects with a small number of tools.

### Kotlin Multiplatform SDK

Kotlin SDK published as Maven artifacts (`io.modelcontextprotocol:kotlin-sdk*`) with multiplatform targets (JVM, Native, JS, Wasm). Coroutine-based APIs throughout; Ktor server is an optional companion for HTTP transports, with engines specified independently to avoid transitive bloat. Appropriate when the consumer needs JVM integration, Android, or browser/Wasm reach with a single SDK surface.

## Transport

The wire mechanism by which a host process exchanges MCP messages with the server. The choice ripples into multi-tenancy posture, authentication need, and whether the server can run as a co-located subprocess or a remote service.

### stdio

JSON-RPC over the server's stdin/stdout, with stderr reserved for logging. The default mode for nearly every sample; often the only mode for local single-user tools that have no networking story. Implies single-tenant per-process and no transport-level auth. The host launches the server as a child process and reads/writes pipes; entry-command snippets in `claude_desktop_config.json` and analogous host-config files are the canonical install surface for stdio servers.

### Streamable HTTP

A single HTTP endpoint (often `/mcp`) that handles request/response, optionally upgrading to SSE for streaming. Selected via CLI flag (`--transport http`, `--port <n>`) or by binding to an HTTP entry method on the SDK. Enables multiple concurrent clients against one server process and opens the door to bearer-token or OAuth authentication. Appropriate when the server is a hosted service, a sidecar, or needs to be reachable from browser clients (which then triggers explicit CORS configuration).

### Server-Sent Events (SSE)

One-way streaming over HTTP from server to client, paired with a separate POST endpoint for client→server messages. Sometimes a distinct entry method on the SDK and sometimes the streaming flavor of Streamable HTTP. Appropriate when the server emits change notifications (resources/tools/prompts updates) that clients subscribe to.

### WebSocket

Bidirectional persistent connection. Surfaces in Kotlin/Ktor where the SDK exposes a `WebSocketTransport` alongside stdio, SSE, and Streamable HTTP. Appropriate when both sides need symmetric streaming and the host environment already speaks WebSocket (browser clients, in particular).

### In-process channel

A non-network transport for local testing — the client and server share a Kotlin channel or a Go pipe rather than serialize JSON over IPC. Appropriate for unit tests and library-mode embedding where the server is part of the host process.

### Custom or experimental transports

SDKs that expose a transport interface so consumers can plug in their own (e.g., Go SDKs that document `custom transport support` and "HTTPS with custom auth, experimental"). Appropriate when the deployment target needs a wire format the SDK doesn't ship.

## Capability surface

What the server actually exposes through MCP. Different from the server runtime — two servers in the same language can expose vastly different capability shapes.

### Tools-only narrow surface

A small, focused set of tools targeting one domain — `1` `fetch` tool, four pandas-analysis tools, 12 git tools. No resources, prompts, sampling, or roots. Appropriate when the server wraps a specific external capability and the host's job is to call it; ergonomics favor low cognitive load over breadth.

### Tools-heavy domain wrapper

Dozens of tools (30+ ffmpeg media operations, 80+ Playwright browser operations) covering a single underlying tool/library exhaustively. Often paired with capability-grouping mechanisms to let consumers trim exposure. Appropriate when the wrapped binary has a large API the consumer wants accessible end-to-end.

### Tools + resources + prompts (full primitive coverage)

SDK-built servers that expose the full MCP primitive set — tools, resources, prompts, sometimes plus completion, logging, sampling, roots, elicitation. Appropriate when the SDK is a reference for spec coverage rather than a single-purpose wrapper, or when the application needs both data exposure (resources) and reusable prompt scaffolds in addition to actions.

### MCP Roots participation

A server that consumes the host-provided "roots" protocol — receiving directory boundaries from the host and adapting its file access accordingly. Distinct from servers that take filesystem paths only as launch flags. Appropriate when the server handles user filesystem content and the host wants to dynamically scope access without restarting the server.

### Sampling and elicitation as client primitives

SDK exposes the *client-side* MCP primitives (sampling = LLM completion request back to the host; elicitation = request user input via the host) for applications building agents on top of MCP. Appropriate for SDKs that target both server and client construction.

### Capability gating via tool subsets

A pattern where the operator opts in to additional tool families at install time — `--caps=vision`, `--caps=pdf`, `--caps=testing` — rather than getting all tools by default. Distinct from a per-tool toggle: gates groups of related tools as a unit. Appropriate when the surface is large enough that selective exposure changes both the token budget and the security posture.

## Configuration delivery

How runtime parameters reach the server process.

### Environment variables

Server reads `os.environ` (or language equivalent) for credentials, behavior toggles, encoding hints (`PYTHONIOENCODING=utf-8` on Windows). Often the only documented surface for stdio servers because the host can inject env vars in its config block. Common for credentials (`NOTION_TOKEN`) where flag-on-CLI would leak via process listings.

### CLI flags / positional args

The launcher accepts flags at startup — repository paths, allowed origins, browser binaries, port numbers — and the host's config snippet bakes them into the spawn command. The most-discoverable surface (one `--help` away). Appropriate when settings rarely change at runtime and the host's config-block model maps cleanly to argv.

### CLI flags with paired env-var equivalents

Each flag has a `<PROJECT>_<FLAG>` env-var twin so the same setting can be supplied either way. Appropriate when the surface grows large (50+ flags) and ops want env-var overrides without rewriting host config.

### `.env` file at server CWD

A `.env.example` template ships in the repo; the operator copies and edits. Appropriate for development-only or single-machine deployments where env var injection through the host is awkward.

### JSON config file via `--config <path>`

A separate file holds the full settings block, referenced by a single CLI flag. Appropriate when the surface is too large for per-flag CLI ergonomics (Playwright's 50+ knobs) and the operator wants to version-control their settings independently from the install command.

### Code-level configuration (functional options pattern)

The SDK is a library; configuration happens at compile/build time via constructor calls and option functions (`WithToolCapabilities()`, `RegisterSession()`, `RegisterTool()`). Appropriate when the consumer is writing the server program themselves rather than running a pre-built binary.

### Host-supplied protocol-level config (MCP Roots)

The server picks up directory scope from the host through MCP messages rather than from CLI/env. Appropriate when the bound concept is something the host owns dynamically (open project, user workspace) rather than a static install setting.

## Authentication

How the server identifies and authorizes the caller.

### None (local single-user)

The server has no authentication layer. Trust is implicit because the host launches the server as a child process under the user's identity. Most stdio servers fall here. The Playwright server explicitly notes "MCP is not a security boundary" — making non-auth a stated design posture rather than an oversight.

### API token in env var

Service-specific token (Notion integration token, etc.) read from `NOTION_TOKEN` or similar. The token authenticates the server *to its upstream service*, not the caller to the server. Appropriate when the server wraps an external authenticated API and assumes a single trusted caller.

### HTTP bearer token

The HTTP transport accepts an `Authorization: Bearer <token>` header. The token is supplied to the server via env or config and validated per request. Appropriate when one server instance serves multiple network clients and at least a coarse "is this a known client" check is needed.

### Application-delegated (SDK provides nothing)

The SDK exposes session-registration hooks but does not bundle an auth mechanism — applications wire their own at the transport layer. Appropriate for SDKs that want to remain unopinionated about deployment context (cloud, on-prem, in-process).

### Domain-level access gate (not auth)

The server enforces what can be accessed (filesystem allowlist, repository path, robots.txt for fetch) without identifying the caller. A different control plane — authorization without authentication. Appropriate when the threat model is "constrain what the trusted caller can ask," not "verify who is asking."

## Multi-tenancy

How concurrent clients are isolated within a single server process.

### Single-user per process

One process, one client; state is global to the process. The default for stdio servers and most local subprocess deployments. Appropriate when the host already isolates per-user by spawning per-user processes.

### Per-session state via session registration

The SDK exposes a session abstraction — `RegisterSession()`, notification channels keyed by client — so a single server process can handle multiple concurrent clients with isolated state. Appropriate when the server runs as an HTTP service and "one process per user" is too costly.

### Stateless per request

Pure request/response with no session affinity; each HTTP call carries everything needed. Appropriate when the wrapped operation has no per-client state to track.

## Observability

What the server emits about its own behavior.

### Stderr-only via SDK default

The SDK writes to stderr; nothing structured beyond that. The host captures stderr if it cares. Appropriate when the server is short-lived and per-request behavior is the host's concern.

### File-system artifacts as side effects

The server writes logs and outputs to local directories (`./logs/`, `./charts/`) and returns paths to the caller rather than data. Doubles as observability (the operator inspects the files post-hoc). Appropriate when outputs are large binary artifacts that don't fit in tool responses anyway.

### Request lifecycle hooks for telemetry

The SDK exposes hooks at request-start, request-complete, error so applications can wire OpenTelemetry, metrics, or logging without modifying SDK code. Pairs with recovery middleware that catches handler panics so a single bad tool call doesn't crash the process. Appropriate when the server runs as a long-lived service and the operator needs to observe across requests.

### Change-notification channels

Per-client notification streams for updates to tool/resource/prompt lists, surfaced via the SDK as event channels. Indirectly observable but primarily a feature for reactive client UIs. Appropriate when the underlying domain emits changes the client should re-render against.

## Distribution channel

How the server reaches end users' machines.

### npm package via `npx`

Published to npm; users invoke `npx -y @scope/package` and the host's config block embeds that command. Appropriate for Node-runtime servers; zero-install ergonomics because npx fetches on first run.

### PyPI package via `uvx` or `pip`

Published to PyPI; users run `uvx mcp-server-<name>` (preferred, ephemeral install) or `pip install mcp-server-<name>` (persistent). Console-script entry point in `pyproject.toml` is the launcher. Appropriate for Python servers; uvx mirrors npx's zero-install ergonomics.

### Source clone + dependency install

Users `git clone` and run `uv sync`, `pip install -r requirements.txt`, or `npm install`. Appropriate for early-stage repos that haven't published, for servers with system-binary dependencies (ffmpeg) where a registry install can't satisfy them anyway, or when the consumer is expected to fork.

### Docker image

Published as `mcp/<name>` on Docker Hub or `mcr.microsoft.com/<vendor>/<server>` on a vendor registry; users `docker run -i --rm` to attach via stdio. Appropriate when the server has system-tool dependencies (ffmpeg, browsers, system libraries), when the operator wants language-agnostic distribution, or when the deployment is a long-running service via `docker-compose`. Multi-arch images extend reach across CPU families.

### Go module via `go get`

Users add the import path to their `go.mod`. The "distribution" is the source code itself; consumers compile their own binary. Appropriate when the artifact is an SDK rather than a runnable server.

### Maven Central artifacts

Published as `<group>:<artifact>` to Maven Central, consumed via Gradle/Maven dependency declarations. Appropriate for JVM-targeted SDKs; granular artifact split (umbrella + client + server) lets consumers depend on just the half they need.

## Entry point and launcher

What the host actually invokes.

### Bare interpreter + script path

`python /abs/path/to/server.py` or `node /abs/path/to/server.js`. The host config snippet embeds the absolute path. Appropriate for source-clone distribution and single-file servers; the cost is that the operator has to know where the file lives.

### Package console-script

`pyproject.toml`'s `[project.scripts]` defines `mcp-server-<name>` mapped to a `:main` entry point; npm `package.json`'s `"bin"` field defines the equivalent. Appropriate when the package is registry-distributed; the host config snippet calls the script name without paths.

### Ephemeral runner (`npx`, `uvx`, `uv run`)

The command resolves the package on demand and invokes its entry point. `npx -y <pkg>`, `uvx <pkg>`, `uv run server.py`. Appropriate when the operator wants no persistent install state and is happy to re-fetch on cache miss.

### SDK constructor + transport-method launch

The server is a program the consumer wrote — `server.NewMCPServer()` returns a server value, then `server.ServeStdio()` or `server.ServeSSE()` runs it. The launcher is the consumer's `main`. Appropriate for Go/Kotlin SDK consumers building bespoke servers.

### Programmatic embedding via library function

The SDK exposes `createConnection()` (or analog) that returns an in-process MCP endpoint a host process can consume directly without subprocess IPC. Appropriate when the host is itself a Node/Kotlin app and wants to embed the server's tool surface as a library, blurring the server/client boundary.

### Docker run as launcher

The host config command is `docker run -i --rm --mount ...` rather than the server's native binary. The image's ENTRYPOINT is the actual launcher. Appropriate when system dependencies or multi-arch concerns make Docker the most reliable attach surface.

## Host integration documentation

How a sample tells operators to wire it into MCP-aware clients.

### Per-host JSON snippets

The README ships copy-paste blocks for each host (Claude Desktop, Claude Code, Cursor, Zed, VS Code, Windsurf, Cline, Goose, Junie, Copilot, Factory, Gemini CLI, LM Studio, Kiro, opencode, Qodo Gen, Warp, Codex, Antigravity, Amp, etc.) showing the `command`/`args` shape. The same JSON pattern with minor wrapper differences across hosts. Appropriate when the server targets the broadest possible host audience and the maintainer is willing to maintain per-host examples.

### Single canonical host snippet

One JSON snippet — usually for `claude_desktop_config.json` — with a generic note that other MCP hosts use similar config. Appropriate when the maintainer wants the docs surface small and assumes operators can adapt.

### Per-OS path documentation

The Claude Desktop section enumerates Windows, macOS, and Linux config paths. Appropriate when the install audience is non-developer-heavy and "where is the file" is itself a documentation gap.

### Production reference implementation

Instead of (or in addition to) host snippets, the README points to a real-world server built on the SDK as a reference. Appropriate for SDKs where the right "integration example" is a complete project, not a config block.

## Repository layout

How the source tree is organized.

### Single-package, scripts at root

One `pyproject.toml`/`package.json`/`go.mod`, source files at root or in a flat subdirectory. Appropriate for small servers (a `server.py`) and library SDKs without sub-modules.

### Single-package, organized subdirectories

One package manifest, code split into purpose-named subdirectories (`src/`, `core/`, `client/`, `server/`, `transport/`, `examples/`, `e2e/`). Appropriate when the codebase is one shipping unit but internally segregated by concern.

### Monorepo with per-server subdirectories

Repo root holds shared tooling; each server lives in `src/<name>/` with its own manifest, Dockerfile, and README. Different servers may use different languages side by side (TS + Python peers). Appropriate when the repo is a curated reference set or a vendor's portfolio of related servers.

### Gradle multi-module / Maven multi-artifact monorepo

Repo holds multiple build modules (`kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, umbrella artifact, plus `samples/`, `integration-test/`, `conformance-test/`, `buildSrc/`). Appropriate when the SDK ships multiple consumable artifacts but shares a build pipeline.

### Cross-language monorepo

One repo holds first-class peers in different language stacks, each with its own packaging, distribution channel, and Docker image. Appropriate when the project is a reference set demonstrating multiple SDKs against one spec.

## Testing

What the sample uses to verify behavior.

### Vitest (Node)

`npm test` runs Vitest with coverage configured (`npm run test:coverage`). Appropriate for Node servers; good async ergonomics and TypeScript-native.

### pytest at conventional location

Tests live in `tests/` discovered by `pytest`, sometimes paired with `pytest-asyncio` (`asyncio_mode = "auto"`) for HTTP-touching servers. The conventional layout the Python reference servers adopt.

### pytest at repo root

`test_*.py` files alongside `server.py` rather than in a `tests/` directory. Same framework, nonstandard placement; common in early-stage single-file repos.

### Go stdlib testing

`*_test.go` co-located with implementation; integration tests in `e2e/` or `integration_test.go`. The default Go path; no extra framework needed.

### Multi-tier Kotlin testing

Dedicated `kotlin-sdk-testing` artifact, `integration-test/` module, `conformance-test/` module, plus snippet-test infrastructure (Knit). Appropriate when the project is a spec-conforming SDK and conformance is a deliverable in its own right.

### `pytest` declared as runtime dependency

Quirk where `pytest` lands under `[project.dependencies]` rather than `[dependency-groups]`. Almost always an oversight rather than a design choice; ships test framework to all consumers.

## Continuous integration

How commits are validated automatically.

### GitHub Actions workflows

Multiple workflows in `.github/workflows/` covering test (`ci.yml`), lint (`golangci-lint.yml`, ruff/pyright equivalents), docs (`pages.yml`), release automation (`release.yml`). Triggered on push and PR. Appropriate for any GitHub-hosted repo; the de-facto default across the corpus.

### Documented but not necessarily wired

The README shows a GitHub Actions YAML example (often because system deps like ffmpeg need an `apt-get install` step) but the actual `.github/workflows/*.yml` may or may not exist. Appropriate as a copy-paste seed for downstream consumers.

### Absent

No CI configured. Common in early-stage repos and small single-author tools.

## Container artifact

Containers as a deliverable, distinct from container as a distribution channel.

### Per-server Dockerfile published as `mcp/<name>`

Each server in a monorepo has its own Dockerfile; images publish to Docker Hub under `mcp/<name>`. Appropriate when the repo is a curated reference set and consumers want one-image-per-server semantics.

### Vendor-namespaced image

Image lives in a vendor registry (`mcr.microsoft.com/playwright/mcp`) rather than the public `mcp/*` namespace. Multi-arch builds extend reach. Appropriate when the publisher is a brand-conscious vendor with its own registry.

### Dockerfile + docker-compose

Repo ships both a `Dockerfile` (single-container build) and a `docker-compose.yml` (orchestrated service definition). Appropriate when the operator wants a one-command launch including any sidecars.

### No container artifact

The server documents only source/registry installs; consumers who want containers build their own. Appropriate when the server has no system deps and Docker would just wrap a `pip install` — minimal benefit for the maintenance cost.

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

## Sandboxing and trust posture

Whether the server constrains what it executes.

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

## System dependencies

External binaries the server requires beyond its language runtime.

### None (pure language ecosystem)

The server's deps live entirely inside `npm install` / `pip install` / `go get` / Gradle resolution. Appropriate when the wrapped functionality is itself implementable in the host language.

### Browser runtime (Playwright)

Server depends on a browser binary that Playwright fetches as part of its install step. Multi-GB install footprint; container distribution becomes significantly more attractive than pip/npm.

### CLI binary on PATH (ffmpeg, system tool)

Server shells out to a system binary that must be installed out of band. README documents `apt-get install ffmpeg` for CI; Docker becomes the only self-contained distribution path. Appropriate when the wrapped tool is a mature CLI that would be foolish to reimplement.

## Agent-facing meta-documentation

Documentation inside the repo that targets agents working in the repo, not human users.

### `CLAUDE.md` shipped with the server

Repo includes a `CLAUDE.md` at root providing Claude-specific guidance for working in the codebase itself. Distinct from a user-facing README; the audience is an agent contributing to the repo. Appropriate when maintainers want consistent agent behavior across contributors using Claude.

### `.cursorrules` for Cursor IDE

Equivalent for Cursor — repo-local instructions an AI editor reads when assisting in the codebase. Appropriate when the maintainer's IDE workflow involves Cursor and wants in-repo context steering.

### `.mcp.json` at repo root

Declares MCP servers the repo itself wants its agents to have available. Distinct from the server being authored — it's the dev environment's MCP wiring. Appropriate when developers iterating on the server need other MCP servers (filesystem, git, etc.) available during their work.
