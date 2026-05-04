# Sample

Pass-1 Phase-1a partial for bin 8. Atomic knowledge chunks from `makenotion--notion-mcp-server`, `mark3labs--mcp-go`, `marlonluo2018--pandas-mcp-server`, `metoro-io--mcp-golang`, `microsoft--playwright-mcp`, `misbahsy--video-audio-mcp`, `modelcontextprotocol--kotlin-sdk`, `modelcontextprotocol--servers`, organized by divergence axes. Phase-1b merger will unify with other partials.

## Identification

Per-repo metadata that situates each sample in the corpus — origin, popularity, license posture, lifecycle status, authorship.

### Authorship class

Three distinct authorship postures observed in this bin, each shaping the artifact's role.

#### First-party vendor server

Vendor of the underlying API ships its own MCP server. Notion publishes `@notionhq/notion-mcp-server` (Notion-authored, ships `CLAUDE.md` in repo) [`makenotion--notion-mcp-server`]. Microsoft publishes `@playwright/mcp` (Microsoft-authored Playwright wrapper) [`microsoft--playwright-mcp`].

#### Official protocol-org reference

Maintained by the MCP organization itself rather than an integrated vendor. `modelcontextprotocol/servers` is the canonical reference-server monorepo [`modelcontextprotocol--servers`]; `modelcontextprotocol/kotlin-sdk` is the official Kotlin SDK maintained with JetBrains collaboration [`modelcontextprotocol--kotlin-sdk`].

#### Third-party SDK / framework author

Independent maintainers building MCP plumbing on top of the spec. `mark3labs/mcp-go` and `metoro-io/mcp-golang` are competing Go SDKs from independent authors [`mark3labs--mcp-go`, `metoro-io--mcp-golang`].

#### Hobbyist / single-developer server

Small repos by individual authors targeting niche workflows. `pandas-mcp-server` (~40 stars) [`marlonluo2018--pandas-mcp-server`], `video-audio-mcp` (71 stars, "6 Commits" on main, possibly early-stage) [`misbahsy--video-audio-mcp`].

### License distribution

Licenses observed in this bin: MIT (most), Apache-2.0 [`microsoft--playwright-mcp`], dual-license Apache-2.0 (new) / MIT (existing) [`modelcontextprotocol--kotlin-sdk`, `modelcontextprotocol--servers`].

#### Dual-license relicensing strategy

Mixed-license repos use a contribution-time gate to migrate forward without touching prior commits — existing code stays MIT, new contributions land under Apache-2.0. A relicensing-forward strategy rather than a relicense of existing material [`modelcontextprotocol--servers`, `modelcontextprotocol--kotlin-sdk`].

### Star count vs engineering quality

A 71-star, 6-commit repo can carry 30+ pytest-tested tools [`misbahsy--video-audio-mcp`]; a ~40-star repo can carry pytest test files at root for three core capability surfaces [`marlonluo2018--pandas-mcp-server`]. Conversely, very large-community repos may leave testing/CI specifics unsurfaced even at 31k+ stars [`microsoft--playwright-mcp`]. Read engineering rigor from the artifacts (test count, lint config, CI presence), not from popularity.

### Repo activity signals

Release velocity is a stronger signal than commit count. `microsoft--playwright-mcp` has 60 releases at 31k stars [`microsoft--playwright-mcp`]; `mark3labs--mcp-go` released v0.48.0 indicating sustained iteration [`mark3labs--mcp-go`]; small-commit repos may still ship usable tooling [`misbahsy--video-audio-mcp`].

## Artifact role

What the repository actually delivers. The corpus splits across server, SDK, and reference-set roles — they consume different evaluation criteria.

### Single MCP server

A deployable MCP server wrapping one upstream API or local capability surface. Examples: Notion (Notion API) [`makenotion--notion-mcp-server`], Playwright (browser automation) [`microsoft--playwright-mcp`], pandas (DataFrame analysis) [`marlonluo2018--pandas-mcp-server`], video/audio (ffmpeg wrapper) [`misbahsy--video-audio-mcp`].

### Multi-server reference monorepo

One repo hosting many independent reference servers in a sibling-directory layout, each with its own package manifest and Dockerfile. `modelcontextprotocol/servers` carries seven reference servers (Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time) under `src/<server>/`, with TS and Python peers each using their own distribution channel (npm vs PyPI) and their own Docker image [`modelcontextprotocol--servers`].

#### Active vs archived split

Archived servers are physically moved to a sibling `servers-archived` repo rather than flagged in-place — keeps the demonstration set curated and the monorepo reference-quality [`modelcontextprotocol--servers`].

#### Reference vs hosted positioning

Repo is positioned as a showcase/reference set, not a product. Forces visible curation discipline (license posture, archival, per-server Dockerfile uniformity) [`modelcontextprotocol--servers`].

### MCP SDK / framework

Library for building MCP servers (and sometimes clients), not a server itself. No host-config integration documented at the SDK level — applications using the SDK handle that. Examples: `mark3labs/mcp-go` (Go) [`mark3labs--mcp-go`], `metoro-io/mcp-golang` (Go, alternate) [`metoro-io--mcp-golang`], `modelcontextprotocol/kotlin-sdk` (Kotlin Multiplatform) [`modelcontextprotocol--kotlin-sdk`].

#### Competing SDKs in the same language

Two independent Go SDKs (`mark3labs/mcp-go` at 8.6k stars; `metoro-io/mcp-golang` at 1.2k stars) coexist with overlapping but non-identical feature sets — Go ecosystem has not consolidated on a canonical SDK [`mark3labs--mcp-go`, `metoro-io--mcp-golang`].

## Language and runtime

The implementation language plus the MCP SDK or framework variant. These two choices co-determine packaging, async semantics, and the surface available to consumers.

### Python servers

Used by tool-wrapping servers in this bin and by the Python half of `modelcontextprotocol/servers`.

#### FastMCP framework

Higher-level Python SDK that auto-derives schemas from function signatures.

- FastMCP 1.x via `fastmcp >= 1.0.0` lower-bound pin — looser than 2.x-pinning servers; suggests FastMCP 1.x-compatible usage; likely import path `from fastmcp import FastMCP` or via `mcp.server.fastmcp` [`marlonluo2018--pandas-mcp-server`]
- FastMCP-style usage via `mcp[cli]>=1.9.0` — `[cli]` extra installs FastMCP-style helpers; README declares "Built with FastMCP framework"; likely the FastMCP-1.x-via-SDK path (`from mcp.server.fastmcp import FastMCP`) rather than standalone FastMCP 2.x [`misbahsy--video-audio-mcp`]

#### Raw `mcp` SDK

Direct use of the official Python `mcp` package without a higher-level wrapper.

- Reference Python servers (git, fetch, time) use raw `mcp` SDK exclusively — no FastMCP. Pins: `mcp>=1.0.0` (git), `mcp>=1.1.3` (fetch). Import pattern: low-level `Server` class from `mcp` package. The reference set deliberately prioritizes low-level SDK coverage over developer convenience [`modelcontextprotocol--servers`]

### TypeScript / JavaScript servers

Node.js runtime, distributed via npm/npx.

#### Anthropic MCP TypeScript SDK

The canonical `@modelcontextprotocol/sdk` TypeScript package.

- TS 5.8.2, MCP SDK ^1.25.1, Express 4.21.2, axios 1.8.4, openapi-client-axios 7.5.5, Zod 3.24.1; tsc + esbuild build [`makenotion--notion-mcp-server`]
- TypeScript 62.2%, MCP SDK + Playwright; `createConnection()` programmatic API [`microsoft--playwright-mcp`]
- TS reference servers in `modelcontextprotocol/servers` use the official SDK; ~69% of repo is TS [`modelcontextprotocol--servers`]

### Go SDKs and runtime constraints

- Go 1.25.5+ specified in `go.mod` [`mark3labs--mcp-go`]
- Go version constraint not surfaced in README of `metoro-io/mcp-golang`; the alternate Go SDK is less explicit about runtime floor [`metoro-io--mcp-golang`]

### Kotlin / JVM Multiplatform

- Kotlin 2.2+, Java 11+ (JVM target); multiplatform: JVM, Native, JS, Wasm. Optional Ktor server. Coroutine-friendly APIs [`modelcontextprotocol--kotlin-sdk`]

### Python version floor

Python floors observed in this bin span the full range:

- `>=3.10` — common; declared by `pandas-mcp-server` and all three sampled Python reference servers (git, fetch, time) [`marlonluo2018--pandas-mcp-server`, `modelcontextprotocol--servers`]
- `>=3.13` — aggressive; declared by `video-audio-mcp` despite being a 6-commit repo. Comparable to hass-mcp-class servers tracking bleeding-edge Python [`misbahsy--video-audio-mcp`]

### System-binary dependency

A class of servers depends on an out-of-band system binary not installable through PyPI/npm. Forms a server class where Docker distribution is the only self-contained option.

- ffmpeg required on PATH — README documents an `apt-get install ffmpeg` step in its GitHub Actions YAML example [`misbahsy--video-audio-mcp`]
- Same shape exists for Tesseract in PDF OCR servers (referenced by `misbahsy--video-audio-mcp` as a peer pattern)

## Transport

How the MCP server speaks to its host. Servers diverge on which transports they support and how the transport is selected at launch.

### Single-transport — stdio only

Default for many servers; no alternative transport documented.

- All reference servers in `modelcontextprotocol/servers`; each starts in stdio mode when launched by its entry command; no transport flag exposed [`modelcontextprotocol--servers`]
- Pandas server: stdio default, no alternate transport documented [`marlonluo2018--pandas-mcp-server`]
- Video/audio server: stdio default [`misbahsy--video-audio-mcp`]

### Multi-transport in one binary

A single binary supporting multiple transports, selected at launch.

#### CLI flag selection — explicit transport name

`--transport http [--port 8080]` argument on the CLI [`makenotion--notion-mcp-server`].

#### CLI flag selection — port-presence implicit

`--port <n>` flips to SSE/HTTP; absence defaults to stdio [`microsoft--playwright-mcp`].

#### Separate entry point methods (SDK-level)

SDK exposes distinct functions per transport rather than a runtime flag — `server.ServeStdio()`, `server.ServeSSE()`, `server.ServeHTTP()` [`mark3labs--mcp-go`].

#### Initialization-time configuration (SDK-level)

Transport selected at server initialization; SDK provides patterns for stdlib HTTP, Gin framework, and stdio [`metoro-io--mcp-golang`]. Kotlin SDK: configured at server init; embedded Ktor server for HTTP deployments; separate transport implementations [`modelcontextprotocol--kotlin-sdk`].

### Transport breadth

#### Three-transport servers (stdio + SSE + HTTP)

- Notion MCP: stdio (default) + Streamable HTTP (configurable port, default 8080) [`makenotion--notion-mcp-server`]
- mcp-go: Stdio + SSE + Streamable HTTP [`mark3labs--mcp-go`]

#### Four+-transport SDKs

- mcp-golang: Stdio + HTTP (stateless request-response) + Gin framework integration + SSE + custom transport support + HTTPS with custom auth (experimental, in progress) [`metoro-io--mcp-golang`]
- Kotlin SDK: Stdio + Streamable HTTP (single endpoint, optional JSON-only or SSE) + SSE + WebSocket + ChannelTransport (local testing) [`modelcontextprotocol--kotlin-sdk`]

#### Two-transport server — stdio + SSE-via-port

stdio (default) + SSE over HTTP when `--port` is set [`microsoft--playwright-mcp`].

### Special-purpose transports

#### Web framework integration

Transport that ties to a specific web framework rather than stdlib HTTP — Gin framework integration [`metoro-io--mcp-golang`], embedded Ktor server [`modelcontextprotocol--kotlin-sdk`].

#### WebSocket as a first-class transport

Kotlin SDK exposes WebSocket as a peer to SSE and Streamable HTTP — uncommon among MCP implementations sampled [`modelcontextprotocol--kotlin-sdk`].

#### In-process / channel transports

`ChannelTransport` for local testing without networking [`modelcontextprotocol--kotlin-sdk`]. `createConnection()` programmatic API enables embedding the server inside a host Node process — blurs server/client boundaries [`microsoft--playwright-mcp`].

#### Bidirectional stdio

Stdio transport supports bidirectional communication, not just request-response [`metoro-io--mcp-golang`].

## Distribution

Mechanisms by which end users obtain and run the server. Most servers offer multiple channels; the dominant choice depends on language ecosystem and target audience.

### npm / npx

Node servers distribute via npm and the npx one-shot runner.

- `npx @notionhq/notion-mcp-server` plus HTTP variant [`makenotion--notion-mcp-server`]
- `npx @playwright/mcp@latest` [`microsoft--playwright-mcp`]
- `npx -y @modelcontextprotocol/server-memory`, `npx -y @modelcontextprotocol/server-filesystem` etc., positional args (filesystem takes directory paths) [`modelcontextprotocol--servers`]

### PyPI

- `pip install mcp-server-git`, `pip install mcp-server-fetch` [`modelcontextprotocol--servers`]

### `uv run` / `uvx` with on-demand install

Python servers leverage `uv` to fetch and run without explicit install.

- `uvx mcp-server-git` (canonical pattern across Python reference servers) [`modelcontextprotocol--servers`]
- `uvx pandas-mcp-cli` hinted in README, but PyPI publication not verified [`marlonluo2018--pandas-mcp-server`]

### Source clone

Always available; sometimes the only path when no package is published.

- `git clone ... && uv sync` or `pip install -r requirements.txt` [`marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`]
- pyproject project-name vs repo-name drift: `video-edit-mcp` (pyproject) versus `video-audio-mcp` (repo) — surfaces "what is the authoritative identifier?" question (PyPI name, repo name, console-script name can all diverge) [`misbahsy--video-audio-mcp`]

### Docker / container images

Docker as the primary or alternative distribution channel.

- Dockerfile + docker-compose.yml; published Docker Hub image (`mcp/notion`) [`makenotion--notion-mcp-server`]
- Multi-arch image on `mcr.microsoft.com/playwright/mcp`; service mode exposes port 8931 [`microsoft--playwright-mcp`]
- Per-server Dockerfile under `src/<server>/Dockerfile`, images published to Docker Hub as `mcp/<server-name>` — consistent convention across servers in the reference monorepo even though language stack differs [`modelcontextprotocol--servers`]

### JVM artifact registries

- Maven Central (Gradle/Maven); granular artifacts per concern: `io.modelcontextprotocol:kotlin-sdk` (full), `io.modelcontextprotocol:kotlin-sdk-client`, `io.modelcontextprotocol:kotlin-sdk-server` [`modelcontextprotocol--kotlin-sdk`]

### Go module

- `go get github.com/<org>/<repo>` — both Go SDKs distribute as Go modules; no binary releases, no Homebrew [`mark3labs--mcp-go`, `metoro-io--mcp-golang`]

### Heterogeneous distribution within one repo

Cross-language monorepo convention: TS and Python as first-class peers in one repo, each with its own distribution channel (npm vs PyPI) and its own Docker image, rather than a single-language monorepo. Forces readers/hosts to handle multiple runtime stacks [`modelcontextprotocol--servers`].

## Entry point / launch

How the server process is started by the host.

### Console script via package metadata

The conventional path: `[project.scripts]` or npm `bin` registers a name on PATH.

- `mcp-server-git = "mcp_server_git:main"`, `mcp-server-fetch = "mcp_server_fetch:main"` (Python reference servers) [`modelcontextprotocol--servers`]
- npm `bin` entry pointing at tsc+esbuild-built CLI [`makenotion--notion-mcp-server`]

### Bare script invoked through interpreter

No console script; user invokes the script directly.

- `python server.py`, `python cli.py`, `uv run server.py` — bare scripts at repo root [`marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`]

### npx one-shot

Node ecosystem; package fetched and executed in one step.

- `npx @playwright/mcp@latest` (stdio), `npx @playwright/mcp@latest --port 8931` (SSE/HTTP) [`microsoft--playwright-mcp`]
- `npx -y @notionhq/notion-mcp-server` [`makenotion--notion-mcp-server`]

### `python -m <module>` invocation

Alternative to console-script for Python servers — works without installation if the package is on PYTHONPATH.

- `python -m mcp_server_<name>` documented as an alternative to `uvx mcp-server-<name>` [`modelcontextprotocol--servers`]

### Docker run as entry point

Host config invokes `docker run ...` rather than a local binary.

- `docker run -i --rm --mount type=bind,src=/path,dst=/projects mcp/filesystem /projects` — mount the host directory to grant filesystem access [`modelcontextprotocol--servers`]
- `docker run -i --rm --init --pull=always mcr.microsoft.com/playwright/mcp` [`microsoft--playwright-mcp`]

### Programmatic embedding (library mode)

Server runs inside a host process as a library, not just as an external subprocess. `createConnection()` enables embedding in Node apps [`microsoft--playwright-mcp`]. SDK-as-library: applications embed the SDK directly via `server.NewMCPServer()` constructor [`mark3labs--mcp-go`], or via `RegisterTool() / RegisterPrompt() / RegisterResource()` registration methods [`metoro-io--mcp-golang`].

### Programmatic builder (SDK-only)

SDK exposes a builder API; no runnable binary. Construction is the entry point.

- Functional options pattern: `WithToolCapabilities()`, `WithTaskCapabilities()`, `WithMaxConcurrentTasks()`, `RegisterSession()` [`mark3labs--mcp-go`]
- Registration methods: `RegisterTool()`, `RegisterPrompt()`, `RegisterResource()` [`metoro-io--mcp-golang`]
- Application-specific initialization with optional Ktor server integration for HTTP [`modelcontextprotocol--kotlin-sdk`]

## Configuration surface

How runtime configuration reaches the server. Servers diverge across env vars, CLI args, files, and OS-native config dirs.

### Environment variables only

The dominant pattern for credential surfaces.

- `NOTION_TOKEN` (recommended) or `OPENAPI_MCP_HEADERS` [`makenotion--notion-mcp-server`]
- `PYTHONIOENCODING=utf-8` noted for Windows in fetch — narrow runtime-environment correction rather than primary config [`modelcontextprotocol--servers`]

### CLI flags + env vars combined

Flags and env vars coexist; each flag has a matching env var.

- 50+ CLI flags and matching env vars; every flag has a `PLAYWRIGHT_MCP_*` env-var equivalent [`microsoft--playwright-mcp`]

### Positional CLI arguments

Required runtime config passed positionally rather than as flags.

- Filesystem server takes directory paths as positional args (e.g., `/projects`); Git uses `--repository` flag instead [`modelcontextprotocol--servers`]

### Optional `.env` file

`.env` file with `.env.example` template — convention for local dev defaults [`marlonluo2018--pandas-mcp-server`].

### Capability gating via flags

Tool surface itself is configurable, not just credentials. Distinct from credential config.

#### `--caps` capability groups

`--caps=<cap>` groups (pdf, vision, testing) unlock tool subsets — install-time surface for trimming tool exposure [`microsoft--playwright-mcp`].

#### Per-host network policy

`--allowed-origins`, `--blocked-origins`, `--proxy-server` limit network access at the server boundary [`microsoft--playwright-mcp`].

#### Storage and timeout flags

`--timeout-action`, `--timeout-navigation` for behavior tuning; `--init-page`, `--init-script` for startup hooks; `--cdp-endpoint` for browser remote attach; `--user-data-dir` for session persistence [`microsoft--playwright-mcp`].

### JSON config file

Single `--config <path>` loads a JSON file of settings — alternative to flag-by-flag CLI [`microsoft--playwright-mcp`].

### Code-level configuration (SDK)

SDKs configure at construction-time rather than via env / CLI; the application embedding the SDK chooses how to surface config.

- Functional options pattern: `WithToolCapabilities()`, `WithTaskCapabilities()`, `WithMaxConcurrentTasks()`, middleware registration [`mark3labs--mcp-go`]
- Registration methods + framework setup [`metoro-io--mcp-golang`]
- CORS configuration for browser clients; configurable endpoint paths (default `/mcp`); transport-specific options [`modelcontextprotocol--kotlin-sdk`]

### Configurable endpoint paths (HTTP)

HTTP-transport servers expose the MCP path as configurable; default `/mcp` [`modelcontextprotocol--kotlin-sdk`].

## Authentication

How callers prove identity to the server, and how the server obtains its own credentials for upstream services.

### API key / personal token

Static token supplied at launch.

- Notion API integration token via `NOTION_TOKEN` env var, CLI args, or HTTP Bearer header [`makenotion--notion-mcp-server`]

### HTTP Bearer for remote transports

stdio is unauthenticated; HTTP/SSE require a Bearer token in HTTP headers. Notion MCP follows this pattern when running in HTTP mode [`makenotion--notion-mcp-server`].

### None / disclaimed

Some servers explicitly disclaim a security boundary or have no auth at all.

- "Playwright MCP is not a security boundary" — README explicit; `--allow-unrestricted-file-access` is the escape hatch. Storage-state files persist sessions but are state, not auth [`microsoft--playwright-mcp`]
- None — local file processing only; no credentials [`marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`]
- None across reference servers; access gated by directory allowlist (filesystem) or repo path (git); fetch respects robots.txt by default [`modelcontextprotocol--servers`]

### SDK delegates to transport / application layer

SDK provides no built-in auth; the embedding application or transport handles credentials.

- Session registration via `RegisterSession()`; no explicit auth in SDK [`mark3labs--mcp-go`]
- HTTPS custom auth marked experimental (in progress) [`metoro-io--mcp-golang`]
- Auth delegated to transport / application layer [`modelcontextprotocol--kotlin-sdk`]

### Boundary enforcement via path allowlist

Filesystem reference server gates file access by an allowlist of root directories provided positionally on launch (and updated dynamically via MCP Roots) — replaces auth with a structural permission boundary [`modelcontextprotocol--servers`].

## Multi-tenancy

Whether and how the server can serve multiple tenants in one process.

### Single-user / single-workspace

Process-scoped credentials or local-machine scope.

- Per-integration-token; HTTP transport supports multiple clients but each speaks for one Notion identity at a time [`makenotion--notion-mcp-server`]
- Single-user per process [`microsoft--playwright-mcp`]
- Single-user; operates on user-supplied CSV/data paths per call [`marlonluo2018--pandas-mcp-server`]
- Single-user local process per host session [`modelcontextprotocol--servers`]

### Per-request session state (SDK-level)

SDK enables multi-tenancy by registering sessions and routing notifications per-client.

- Per-request via session registration; notification channels support per-client state management [`mark3labs--mcp-go`]
- HTTP stateless pattern suggests per-request handling; per-tool tenant routing not centrally documented [`metoro-io--mcp-golang`]
- SDK provides transport and protocol abstraction; multi-tenancy handled by application using the SDK [`modelcontextprotocol--kotlin-sdk`]

## Capabilities exposed

What the server actually exposes to the host: tools, resources, prompts, sampling, roots, logging, etc.

### Tool count and granularity

Servers diverge on whether to expose many atomic tools or fewer consolidated meta-tools.

#### Single tool

- Fetch reference server: 1 `fetch` tool [`modelcontextprotocol--servers`]

#### Few tools (single-digit)

- Pandas server: 4 tools (`read_metadata_tool`, `interpret_column_data`, `run_pandas_code_tool`, `generate_chartjs_tool`) [`marlonluo2018--pandas-mcp-server`]

#### Mid range (10–25 tools)

- Filesystem reference server: 13 tools (9 read + 4 write) [`modelcontextprotocol--servers`]
- Git reference server: 12 tools [`modelcontextprotocol--servers`]
- Notion server: 22 tools — page create/retrieve, database query, page move, commenting, content search [`makenotion--notion-mcp-server`]

#### Many tools (30+)

- Video/audio server: 30+ tools — video format conversion, trimming, scaling, codec changes, overlays; audio format/bitrate/sample-rate adjustment, channel config; creative (text overlays, watermarks, subtitles, transitions); advanced (concatenation, B-roll insertion, silence removal). Tool-count density: 30+ tools from a 6-commit repo, demonstrating how quickly an FFmpeg wrapper scales via codegen-like uniformity [`misbahsy--video-audio-mcp`]
- Playwright server: 80+ structured tools across categories — Core automation (click, type, navigate, screenshot, snapshot); Tab management; Network (mocking, state inspection, route management); Storage (cookies, localStorage, sessionStorage); DevTools (tracing, video, element highlight, debugging); Vision (coordinate-based interactions); PDF; Testing (assertions, locator generation) [`microsoft--playwright-mcp`]

### MCP protocol features

Beyond tools, what protocol features the server/SDK actually supports.

#### Tools-only servers

Most servers expose tools and nothing else.

- Reference servers: tools across the board; resources and prompts not prominent in individual READMEs [`modelcontextprotocol--servers`]

#### Tools + Resources + Prompts

- Notion server's 22-tool surface is tools-only; resources/prompts not surfaced [`makenotion--notion-mcp-server`]
- mcp-go SDK: Tools, Resources, Prompts, Sessions, Notifications [`mark3labs--mcp-go`]
- mcp-golang SDK: Tools, Prompts, Resources with full listing and pagination support [`metoro-io--mcp-golang`]
- Kotlin SDK server side: Prompts, Resources, Tools, Completion, Logging, experimental features. Client side: Sampling (LLM requests), Roots (filesystem declaration), Elicitation [`modelcontextprotocol--kotlin-sdk`]

#### MCP Roots protocol

Filesystem reference server implements MCP Roots — the only reference server that interacts with the protocol's client-provided root-directory mechanism, enabling dynamic directory updates from the host [`modelcontextprotocol--servers`].

#### Sampling and Elicitation (client-side capabilities)

Kotlin SDK is the only sample explicitly surfacing client-side Sampling (LLM requests) and Elicitation alongside Roots [`modelcontextprotocol--kotlin-sdk`].

#### Pagination on listings

Pagination support for list operations, suggesting handling of large result sets — uncommon among MCP implementations sampled.

- Pagination support on listings [`metoro-io--mcp-golang`]
- Pagination support for list operations [`modelcontextprotocol--kotlin-sdk`]

#### Change notifications

Server pushes notifications to clients when resource/tool/prompt sets change, enabling reactive client patterns and event-driven server architectures.

- Change notifications for tools, prompts, and resources [`metoro-io--mcp-golang`]

#### Bidirectional stdio communication

Stdio transport supports bidirectional communication, not just request-response [`metoro-io--mcp-golang`].

#### Async task execution with concurrency limits

Task-augmented tool execution (asynchronous with concurrency limits) — `WithMaxConcurrentTasks()` lets the server bound parallel tool work; differentiates from basic tool registries [`mark3labs--mcp-go`].

### Domain-specific tool surfaces

#### Browser automation

Accessibility-tree snapshots as primary perception model — token-efficient versus screenshot/vision. Vision is opt-in via `--caps=vision`, not default. Reverses the default assumption that browser automation needs visual models [`microsoft--playwright-mcp`].

#### Server-stateful side channels

Most MCP servers are stateless; some persist data locally across calls.

- Storage-state files for browser sessions — non-auth state-carrying mechanism, supports state portability between runs [`microsoft--playwright-mcp`]

#### Filesystem with on-disk artifact return

Tool returns a file path to a generated artifact rather than the artifact's bytes — chart artifacts persist on disk; MCP client has to read the file path. Persistent file-system output as the tool return channel [`marlonluo2018--pandas-mcp-server`].

#### Sandboxed code execution

Tool wraps a runtime that executes user-supplied code. Trust model differs fundamentally from pure read-only tool servers.

- Blacklist-filtered pandas code execution — string-level denylist is a known-fragile approach versus process isolation or restricted exec [`marlonluo2018--pandas-mcp-server`]

### Per-tool surface gating

#### Capability groups (`--caps`)

Install-time surface for trimming tool exposure: pdf, vision, testing as opt-in capability groups [`microsoft--playwright-mcp`].

#### Network/Storage/DevTools opt-in

Several Playwright tool categories (Network, Storage, DevTools) are opt-in toggles rather than default-on [`microsoft--playwright-mcp`].

#### Path allowlist

Filesystem server's allowlist gates which directories tools can touch; functions as both auth and capability scoping [`modelcontextprotocol--servers`].

## Extensibility

How users extend or customize a deployed server without forking.

### Middleware (SDK)

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

### OpenAPI-derived tool surface

Auto-derived tools from an OpenAPI spec rather than hand-authored — uses `openapi-client-axios` 7.5.5. Axis: auto-derived tools from an OpenAPI spec vs hand-authored [`makenotion--notion-mcp-server`].

## Type and schema strategy

How tool schemas are derived and what type system the SDK uses.

### Auto-derived from type signatures

- Type-safe tool definitions using native Go structs with automatic schema generation [`metoro-io--mcp-golang`]
- FastMCP-1.x-auto-derived from type hints via the SDK; Pydantic via FastMCP [`marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`]
- Zod 3.24.1 declared in deps — implies runtime-validated schemas [`makenotion--notion-mcp-server`]

### Hand-authored JSON Schema

Low-level `mcp` SDK in Python reference servers — hand-authored JSON schemas for tools; pyright for typing [`modelcontextprotocol--servers`].

### Coroutine-friendly Kotlin idioms

Kotlin SDK exposes coroutine-friendly APIs throughout [`modelcontextprotocol--kotlin-sdk`].

## Observability

Logging, metrics, tracing, debug flags. Often under-documented in READMEs.

### File-system based output

- Logs written to `./logs/`; chart outputs to `./charts/` — both file-system based [`marlonluo2018--pandas-mcp-server`]

### Stderr default

- Each server logs to stderr per SDK default [`modelcontextprotocol--servers`]

### Hooks-driven (SDK)

- Request hooks for telemetry; Recovery middleware for panics; Session tracking with notification channels for per-client events [`mark3labs--mcp-go`]
- Change notifications listed as supported feature; no explicit logging/metrics [`metoro-io--mcp-golang`]

### Capability toggles as proto-observability

- `--init-script` for instrumentation injection; tracing and video are capability toggles rather than observability per se [`microsoft--playwright-mcp`]

### Standard logging frameworks

- Kotlin/Ktor standard logging available; no MCP-level observability documented [`modelcontextprotocol--kotlin-sdk`]

## Host integrations

Which MCP-compatible hosts the server documents support for.

### Claude Desktop

The most-cited host target; typically a JSON `mcpServers` entry with `command`/`args` shape.

- Notion: `claude_desktop_config.json` [`makenotion--notion-mcp-server`]
- Pandas: Windows/macOS/Linux config paths documented; command/args form [`marlonluo2018--pandas-mcp-server`]
- mcp-golang: `~/Library/Application Support/Claude/claude_desktop_config.json` with executable path and env vars [`metoro-io--mcp-golang`]
- Top-level snippet across reference servers, plus per-server READMEs [`modelcontextprotocol--servers`]
- Listed for Playwright [`microsoft--playwright-mcp`]

### Claude Code

- Listed for Playwright [`microsoft--playwright-mcp`]

### Cursor

- `.cursor/mcp.json` [`makenotion--notion-mcp-server`]
- Listed for Playwright [`microsoft--playwright-mcp`]
- `.cursorrules` file present [`metoro-io--mcp-golang`]

### Zed

- `settings.json` [`makenotion--notion-mcp-server`]
- `settings.json` snippet in per-server README (git) [`modelcontextprotocol--servers`]

### VS Code

- `mcp.json` workspace/user config snippets in per-server READMEs (git) [`modelcontextprotocol--servers`]
- Listed for Playwright [`microsoft--playwright-mcp`]

### GitHub Copilot CLI

- Documented [`makenotion--notion-mcp-server`]

### Long-tail host listings

Playwright explicitly lists ≥20 supported clients — a marketing-shaped breadth play that exceeds typical MCP server host coverage. Clients listed: Claude Desktop, Claude Code, VS Code, Cursor, Windsurf, Cline, Goose, Junie, Copilot, Factory, Gemini CLI, LM Studio, Kiro, opencode, Qodo Gen, Warp, Codex, Antigravity, Amp [`microsoft--playwright-mcp`]. Zencoder also mentioned in one git README [`modelcontextprotocol--servers`].

### Browser-clients via CORS

Kotlin SDK supports browser-based clients via Ktor CORS configuration — uncommon for MCP servers [`modelcontextprotocol--kotlin-sdk`].

### SDK-level: no host integrations documented

SDKs do not document host-config snippets — applications using the SDK handle that [`mark3labs--mcp-go`, `modelcontextprotocol--kotlin-sdk`].

### Claude Code plugin wrapper

A `.claude-plugin` directory marks a first-party plugin wrapping the MCP server. None observed across this bin's samples [`makenotion--notion-mcp-server`, `microsoft--playwright-mcp`, `marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`, `mark3labs--mcp-go`, `metoro-io--mcp-golang`, `modelcontextprotocol--kotlin-sdk`, `modelcontextprotocol--servers`].

#### `.mcp.json` at repo root

`modelcontextprotocol/servers` has `.mcp.json` at repo root (no `.claude-plugin/` directory) [`modelcontextprotocol--servers`].

### Agent-facing meta-documentation in repo

`CLAUDE.md` shipped in the server repo itself — guidance for Claude when working on the repo. Distinct from host-config snippets; this is documentation for the agent acting as a developer on the repo, not as a runtime tool user [`makenotion--notion-mcp-server`].

## Tests

Test framework, location, density. A signal of engineering rigor independent of star count.

### pytest

Dominant Python test framework.

- 30+ pytest functions in `tests/`; pytest declared as a runtime dep (unusual — should be a dev dep) [`misbahsy--video-audio-mcp`]
- `test_metadata.py`, `test_execution.py`, `test_generate_barchart.py` at repo root rather than `tests/` directory — nonstandard location [`marlonluo2018--pandas-mcp-server`]
- Per-server `tests/` directories. fetch: pytest + pytest-asyncio with `asyncio_mode = "auto"`; git: pytest only (no asyncio). `testpaths = ["tests"]`, `python_files = "test_*.py"` [`modelcontextprotocol--servers`]

### Vitest (TypeScript)

- `npm test`, `npm run test:watch`, `npm run test:coverage`; `NODE_ENV=test`; coverage reports [`makenotion--notion-mcp-server`]

### Go stdlib testing

- `*_test.go` files plus `e2e/` directory; unit + end-to-end tests [`mark3labs--mcp-go`]
- `server_test.go` (21.7 KB), `integration_test.go` (10.1 KB); integration testing patterns [`metoro-io--mcp-golang`]

### Multiplatform Kotlin testing

- `kotlin-sdk-testing` module, `integration-test/`, `conformance-test/` directories, `test-utils/` shared utilities; Knit properties for code-snippet testing — testing infrastructure split into separately-versioned components [`modelcontextprotocol--kotlin-sdk`]

### Test infrastructure shape

#### Conformance vs functional tests

Kotlin SDK splits tests into integration + conformance against the MCP spec — explicit conformance category beyond pass/fail unit tests [`modelcontextprotocol--kotlin-sdk`].

#### Test-fixture as published artifact

`kotlin-sdk-testing` is a distinct artifact (`io.modelcontextprotocol:kotlin-sdk-testing`) — testing utilities packaged for downstream consumption [`modelcontextprotocol--kotlin-sdk`].

## CI

### GitHub Actions

The dominant CI substrate.

- Workflows present in `.github/workflows`; build + test in pipeline [`makenotion--notion-mcp-server`]
- `ci.yml` (main testing), `golangci-lint.yml` (linting), `pages.yml` (documentation), `release.yml` (release automation); triggers on push/PR [`mark3labs--mcp-go`]
- Configured; typical Go project structure implies test+lint workflows [`metoro-io--mcp-golang`]
- Configured; typical Gradle/Kotlin project structure [`modelcontextprotocol--kotlin-sdk`]
- Active release pipeline (60 releases for Playwright) [`microsoft--playwright-mcp`]

### Documented vs configured

CI workflow files may be documented as a pattern but not actually configured — `video-audio-mcp` shows a GitHub Actions YAML example in README; actual `.github/workflows/*.yml` presence not confirmed [`misbahsy--video-audio-mcp`].

### Per-server CI in monorepos

`modelcontextprotocol/servers` has `.github/workflows` at top level; per-server test infrastructure not prominent in individual READMEs — each server is small enough that test infrastructure is minimal/per-package [`modelcontextprotocol--servers`].

### Documentation site as a CI workflow

Some workflows extend beyond test+lint to include doc-site builds — `pages.yml` for documentation publishing [`mark3labs--mcp-go`].

### Release automation as CI workflow

Release workflows separate from test workflows — `release.yml` for release automation [`mark3labs--mcp-go`].

## Container / packaging artifacts

### Dockerfile + docker-compose

- Dockerfile (Node.js-based) + `docker-compose.yml` + official Docker Hub image (`mcp/notion`) [`makenotion--notion-mcp-server`]

### Multi-arch Dockerfile

- Dockerfile, multi-arch image on `mcr.microsoft.com/playwright/mcp` [`microsoft--playwright-mcp`]

### Per-server Dockerfile (monorepo)

- Per-server Dockerfile (e.g. `src/filesystem/Dockerfile`, `src/git/Dockerfile`, `src/fetch/Dockerfile`); images published as `mcp/<server-name>` [`modelcontextprotocol--servers`]

### No container artifacts

- SDK itself has no container artifacts; examples may include containerization [`mark3labs--mcp-go`, `metoro-io--mcp-golang`, `modelcontextprotocol--kotlin-sdk`]
- None captured for hobbyist Python servers [`marlonluo2018--pandas-mcp-server`, `misbahsy--video-audio-mcp`]

## Packaging conventions (Python)

Build backend, lock file, version manager.

- Build backend: `hatchling.build` across sampled Python reference servers; standalone uv package per subdir [`modelcontextprotocol--servers`]
- Lock file: `uv.lock` implied [`misbahsy--video-audio-mcp`]; `requirements.txt` only (no uv.lock), pip-only [`marlonluo2018--pandas-mcp-server`]
- Version manager: `uv` predominant; pip-only the exception [`misbahsy--video-audio-mcp`, `modelcontextprotocol--servers`, `marlonluo2018--pandas-mcp-server`]

### Lint and typecheck pinned across servers

- pyright>=1.1.389, ruff>=0.7.3 pinned across all sampled Python reference servers — per-server consistency in dev tooling [`modelcontextprotocol--servers`]

### `pytest` accidentally in runtime deps

- `pytest` declared as a runtime dep — likely an oversight; tests shouldn't require installing pytest for users running the server [`misbahsy--video-audio-mcp`]

## Repo layout

How code is organized within a single repo.

### Single-package

- `src/`, `docs/`, `scripts/`, `.github/`; config: `package.json`, `tsconfig.json`, `vitest.config.ts`, `Dockerfile`, `docker-compose.yml`; documentation: `CLAUDE.md`, `README.md` [`makenotion--notion-mcp-server`]
- Single-file server (`server.py`) [`misbahsy--video-audio-mcp`]
- Flat layout — `/core` subdirectory (metadata, execution, visualization, chart_generators); scripts at root [`marlonluo2018--pandas-mcp-server`]

### SDK with functional subdirectories

- `mcp/` (protocol), `client/`, `server/`, `util/`, `mcptest/`, `examples/`, `e2e/`, `.github/` [`mark3labs--mcp-go`]
- Root-level `client.go`, `server.go`, `content_api.go`, `prompt_api.go`, `prompt_response_types.go`, `tool_api.go`, `tool_response_types.go`, `resource_api.go`, `resource_response_types.go`; subdirectories: `internal/`, `transport/`, `resources/`, `examples/`, `docs/`, `.github/` [`metoro-io--mcp-golang`]

### Monorepo (multi-server)

- `src/<server>/` per reference server (Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time); root has shared `package.json`, `tsconfig.json`, `.npmrc`; Python servers self-contained inside the same directory tree [`modelcontextprotocol--servers`]

### Monorepo (multi-module SDK)

- Gradle multi-module: `kotlin-sdk-core`, `kotlin-sdk-client`, `kotlin-sdk-server`, `kotlin-sdk-testing`, `kotlin-sdk` (umbrella); supporting: `samples/`, `docs/`, `config/`, `integration-test/`, `conformance-test/`, `.github/`, `buildSrc/` [`modelcontextprotocol--kotlin-sdk`]

### Single-package monorepo

- Monorepo with `/packages` directory [`microsoft--playwright-mcp`]

## Developer ergonomics and examples

### Sample/example directories

- 20 example implementations included covering client, server, HTTP, SSE, OAuth, roots, sampling, structured tools, tasks; patterns for in-process integration and custom transports [`mark3labs--mcp-go`]
- Server and client examples; documentation at mcpgolang.com; Metoro Kubernetes server as production reference implementation [`metoro-io--mcp-golang`]
- Sample implementations in `./samples/` covering various transport configurations [`modelcontextprotocol--kotlin-sdk`]

### Companion documentation site

- Documentation at mcpgolang.com [`metoro-io--mcp-golang`]
- `pages.yml` workflow for doc-site publishing [`mark3labs--mcp-go`]

### Multi-host config snippets in README

- Configuration examples for 4 host integrations; Docker installation documented; local symlink testing via `npm link` for Cursor [`makenotion--notion-mcp-server`]
- Each server README includes copy-paste JSON snippets for Claude Desktop and often VS Code [`modelcontextprotocol--servers`]

### Programmatic API as developer ergonomic

`createConnection()` enables programmatic embedding — server can run inside another Node process [`microsoft--playwright-mcp`].

### Live-reload dev mode

- `npm run dev` (tsx watch) for hot reload during development [`makenotion--notion-mcp-server`]

## Notable structural choices

Cross-cutting design commitments observed across the bin.

### Accessibility-first browser perception

Token-efficient by design: accessibility-tree snapshots over screenshots/vision as the primary perception model. Vision opt-in via `--caps=vision`. Reverses the default assumption that browser automation needs visual models [`microsoft--playwright-mcp`].

### Programmatic embedding (library mode) as first-class

`createConnection()` means the MCP server can run inside host processes as a library, not just as an external subprocess. Blurs server/client lines [`microsoft--playwright-mcp`].

### Functional options vs registration methods (Go SDK divergence)

Two Go SDKs choose different idioms: `mark3labs/mcp-go` uses functional-options pattern (`WithToolCapabilities()`) while `metoro-io/mcp-golang` uses registration methods (`RegisterTool()`). Different ergonomic choices in the same language [`mark3labs--mcp-go`, `metoro-io--mcp-golang`].

### Multiplatform Kotlin enabling MCP outside JVM

Multiplatform support (JVM, Native, JS, Wasm) enables MCP implementations outside JVM. Modular artifact structure allows client/server-only dependencies. No transitive Ktor dependencies — developers specify engines independently [`modelcontextprotocol--kotlin-sdk`].

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

### Cross-language reference monorepo

TS and Python as first-class peers in one repo, each with its own distribution channel and Docker image — forces hosts to handle multiple runtime stacks [`modelcontextprotocol--servers`].

## Gaps and unknowns observed

Per-sample gaps that limit cross-corpus comparison.

- Notion MCP: logging/observability, rate limiting, Notion API quota handling, V2.0 migration not in README [`makenotion--notion-mcp-server`]
- mcp-go: explicit language version tested in CI not confirmed; Docker production patterns not documented in SDK; full CI workflow contents not enumerated [`mark3labs--mcp-go`]
- pandas: `pandas-mcp-cli` PyPI publication not verified; License/CI/Docker absence vs not documented unclear; exact dependency pin list beyond pandas/fastmcp/chardet/psutil not read [`marlonluo2018--pandas-mcp-server`]
- mcp-golang: HTTPS custom auth marked experimental — implementation details not documented; specific Go version not specified; Makefile not present; full CI/CD configuration not examined [`metoro-io--mcp-golang`]
- Playwright: exact Node.js version constraint; whether auth can be added via programmatic API; CI workflow specifics [`microsoft--playwright-mcp`]
- video-audio: console-script presence (pyproject omitted `[project.scripts]`); actual build backend; whether CI is real or only documented as pattern; FastMCP-in-SDK vs standalone confirmation [`misbahsy--video-audio-mcp`]
- Kotlin SDK: specific Ktor version constraints; observability/logging patterns; Docker/containerization guidance; complete transport-selection pattern [`modelcontextprotocol--kotlin-sdk`]
- mcp/servers: exact last-commit date (only release tag visible); specific CI workflow contents per server; whether any server supports non-stdio transports; full enumeration of published packages for all seven servers (only three sampled in depth) [`modelcontextprotocol--servers`]
