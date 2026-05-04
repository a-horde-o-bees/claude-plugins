# Sample

Pass-1 Phase-1a partial for bin 6. Functional decomposition of geropl--linear-mcp-go, getsentry--sentry-mcp, github--github-mcp-server, googleapis--mcp-toolbox, hannesrudolph--sqlite-explorer-fastmcp-mcp-server, hugoduncan--mcp-clj, idosal--git-mcp, isaaccorley--planetary-computer-mcp, organized by role with implementation paths as sub-sections.

## Server runtime

The language and SDK substrate the MCP server process executes on. Constrains packaging conventions, dependency-management style, async model, and the available distribution channels downstream.

### Go with mark3labs mcp-go SDK

A Go binary linked against the community `mcp-go` SDK. Single-binary build artifact suits cross-platform release-and-download distribution and Docker packaging without language-runtime prerequisites on the host. Stdio is the natural transport for `serve`-style subcommands; Go modules act as the dependency boundary. Appropriate when the server should run anywhere a static binary lands and the author wants minimal runtime dependencies.

### Go with custom MCP implementation

A Go server that does not depend on a third-party MCP SDK — the project hand-rolls protocol handling and ships a `server.json` to declare MCP capability metadata. Same Go-binary distribution profile as the SDK-based variant, but the project owns its protocol surface end-to-end. Appropriate at scale (large official servers) where custom toolset gating, dynamic capability registration, or hosted-mode integration motivate owning the protocol layer rather than tracking an upstream SDK.

### TypeScript on Node with monorepo tooling

A TypeScript codebase organized as a pnpm workspace + Turbo monorepo. Same code targets both an npm-distributable stdio binary (`npx @scope/server`) and a hosted HTTP service. Permits multiple packages (server, client, evals, plugin wrapper) under one repo. Appropriate when one logical product spans server + clients + first-party plugin wrappers and the author wants shared build/CI across them.

### TypeScript on Cloudflare Workers

A TypeScript codebase deployed as a Cloudflare Workers application via Wrangler, with React Router 7 + Vite for a co-resident web frontend. The server is the deployment, not the artifact — there is no binary or package users run. Constrains the runtime to whatever the Workers platform supports (HTTP/SSE only, no stdio, ephemeral execution model). Appropriate when the goal is a zero-install hosted MCP service with global edge distribution and the workload fits Workers' execution constraints.

### Python with FastMCP (pre-2.x era)

A Python single-file script using FastMCP 1.x decorators. Tool signatures derive from type hints; the FastMCP CLI installer (`fastmcp install`) is the install mechanism rather than pip. Predates the modern `pyproject.toml`-centric layout — `requirements.txt` pins FastMCP and the script is the package. Appropriate when the goal is the smallest possible single-file MCP server and the author is comfortable being pinned to FastMCP's CLI conventions.

### Python with raw MCP SDK and uv

A Python project using the lower-level Anthropic `mcp` SDK directly (not FastMCP), packaged with uv and a `pyproject.toml`. Module-level entry (`python -m package.server`) rather than a console script; `uv sync` installs from source. Appropriate when the author wants explicit control over MCP server construction and dependency management via uv's lockfile-driven workflow, accepting more boilerplate than FastMCP would impose.

### Clojure with hand-rolled MCP and minimal deps

A Clojure project against MCP version 2024-11-05 with `org.clojure/data.json` as effectively the only dependency. Polylith-style modular layout (bases, components, projects). Java runtime is required; the JVM warm-up and dependency resolution cost falls on the host launching `clj -M:profile`. Appropriate when the author values a self-contained Clojure REPL evaluation surface and is willing to absorb Polylith's structural overhead in exchange for component reuse across multiple deliverables.

## Transport

The wire on which MCP messages travel between host and server. Constrains tenancy, authentication, distribution, and lifecycle (long-lived process vs request/response).

### stdio

Bidirectional JSON-RPC over the server process's stdin/stdout. The host launches the server as a child process per connection. Implies single-tenant (one process == one identity), single-host (the launching app), and pushes auth into env vars or CLI flags read at startup. Default for locally-installed servers across all runtimes. Often selected implicitly by the SDK's CLI installer, sometimes explicitly via a `stdio` subcommand or profile alias. Tightens stdout-cleanliness pressure — any non-protocol writes corrupt the channel, so servers suppress progress output and route logs to stderr.

### HTTP

A long-running HTTP service exposing MCP at a well-known path (e.g., `/mcp` on port 5000) or as a hosted endpoint (e.g., `mcp.sentry.dev`, `api.githubcopilot.com`, `gitmcp.io`). Permits multi-user access, OAuth-style auth, and decoupling the server lifecycle from the host process. Required when the server is operated as a SaaS or shared service. Often paired with stdio for the same product — same code targets both modes, with the deployment target choosing.

### SSE (Server-Sent Events)

HTTP transport using SSE for server-to-client streaming, paired with HTTP POST for client-to-server messages. A common variant of HTTP transport for hosted MCP services and locally-launched HTTP servers. Selected via a CLI profile (e.g., `:sse-server`) or as the only mode the hosted service exposes.

### In-memory

A non-network transport used inside a single process for testing — server and client share memory and exchange messages without serialization. Not a deployment option; only relevant in test harnesses. Appropriate when the test goal is the server's protocol behavior independent of network/IO concerns.

## Capability surface

The set of operations the server vends to the host. Constrains what an agent can do and how the host renders the catalog.

### Tools only

The server registers JSON-RPC tools and nothing else. The simplest and most common surface — a tool list with input schemas and a single `tools/call` dispatch path. Appropriate when the project's value is action-oriented (query, mutate, fetch) and there is no static-resource or prompt-template content to expose.

### Tools plus prompts

The server vends tools and also surfaces MCP "prompts" as first-class artifacts, often declared alongside tools in a manifest. Lets the host present pre-authored prompt templates the user can invoke directly. Appropriate when the project includes idiomatic prompts for working with its tools and the author wants those discoverable through MCP rather than buried in docs.

### Tools plus internal "skills" abstraction

The server vends tools and additionally maintains an internal-to-the-server "Skills" concept — toggleable behavioral bundles that operators can disable per-deployment via an env var. Skills are a higher-level capability primitive than individual tools and can be trimmed at startup to narrow the agent's behavioral surface for specific deployments. Appropriate when the operator audience needs deployment-specific capability profiles (e.g., disable summarization skills in a security-sensitive deployment) without forking the server.

### Tools plus toolset gating

The server vends a large tool catalog (100+) partitioned into toolsets that operators can independently enable/disable via flags or env vars. Adds runtime-discoverable "dynamic toolsets" — the catalog mutates mid-session based on agent action, so hosts that cache the tool list need to refresh. Read-only and lockdown modes act as orthogonal behavior envelopes layered over toolset selection. Appropriate at scale when a single server covers many product surfaces and operators need fine-grained control over what's exposed.

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

Config flows in via env vars set by the host before launching the server child process. The standard pattern for stdio-launched servers — host config files (e.g., `claude_desktop_config.json`) carry an `env` block that gets merged into the child's environment. Appropriate when config is mostly secrets and deployment-specific endpoints; fits stdio's per-process model naturally.

### CLI flags

Config flows in via flags on the server command. Common alongside env vars — flags override or supplement env values, and flag presence may select subcommands or modes (`--read-only`, `--write-access`, `--toolsets`, `--port`). Appropriate when the host config can express command-line args (most hosts do) and the operator wants visible, declarative configuration over implicit env var inheritance.

### YAML manifest

Config flows in via a structured YAML file referenced by `--config <path>`. The manifest defines sources, tools, toolsets, prompts, and operational settings in one place. Hot reload is feasible because the manifest is a separate file the server can re-read. Appropriate when configuration is large, structured, and likely to evolve — too much for env vars or flags.

### Host-side JSON config snippet

The repo doesn't deliver config to the server; instead the README documents a JSON snippet users paste into per-host config files (`mcp.json`, `claude_desktop_config.json`, `cline_mcp_settings.json`). The host owns config delivery; the server only reads what arrives. Universal across all stdio-launched servers regardless of runtime.

## Authentication

How the server proves the operator/agent has the right to call upstream APIs. Constrains the deployment model — single-tenant local processes vs multi-tenant hosted services.

### Static API key via env var

A single long-lived secret read from an env var at startup (`LINEAR_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN`, `SENTRY_ACCESS_TOKEN`). Ties the server process to one identity for its lifetime. Simple, universal across stdio servers, and the path of least resistance when the upstream service supports PATs. Appropriate when one user's credentials are correct for the entire process and rotation can happen by restarting with a new env var.

### OAuth on hosted endpoint

OAuth flow handled by the hosted-service deployment of the same product; per-user identity is established at connection time rather than at process startup. Local stdio mode falls back to PAT/static-key. Hosts with native MCP OAuth support (e.g., VS Code 1.101+) handle the flow transparently. Appropriate when the same code is operated both as a per-user local install and a multi-tenant SaaS — the auth path branches on transport.

### Delegated to upstream source

Authentication isn't a server concern at all — the server connects to upstream sources (databases, cloud APIs) using whatever credentials those sources expect, configured per-source in the manifest. Includes ambient credentials (Google Cloud ADC, IAM) and per-database static credentials. Appropriate when the server is a multi-source proxy and each source has its own auth story.

### None

No authentication — the upstream service is public (Microsoft Planetary Computer STAC, public GitHub repos via cloud documentation service) or the data is local (SQLite file). The server has nothing to authenticate against. Appropriate when the upstream is genuinely open or the data lives entirely on the host's filesystem.

## Multi-tenancy

How identities are partitioned within a single server instance. Tightly coupled to transport.

### Single-user per process

One process serves one identity for its lifetime. Inevitable consequence of stdio + static API key. The host launches a fresh process per user/workspace. Appropriate when isolation is per-process and the cost of process startup is acceptable.

### Per-user OAuth on hosted endpoint

The hosted deployment of a product maintains per-connection identity via OAuth, while the same code in stdio mode is single-user-per-process. The two modes share a capability surface but differ in tenancy. Appropriate when one product needs both deployment shapes.

### Per-tenant via URL parameter

A hosted service multiplexes tenants by parameterizing the URL path (e.g., `/{owner}/{repo}`). One deployment serves arbitrarily many tenants without per-tenant state. Appropriate when the upstream resource is itself addressable by URL parameter (a public repo, a public dataset).

### Per-process multi-source

The process serves one identity but composes data from multiple back-end sources declared in its manifest. Tenancy isn't user-based; it's source-based. Appropriate when one operator (DBA, platform team) operates one server against many databases.

## Distribution channel

How the server reaches the user's machine or how users address the running service. Constrains install ergonomics and platform reach.

### Pre-built binaries via GitHub Releases

Cross-platform binaries (Linux, macOS, Windows; AMD64, ARM64) attached to GitHub release tags. Users download via a script or manually and run directly. Avoids a language-runtime prerequisite. Natural fit for Go and other compile-to-static-binary runtimes. Appropriate when the audience may not have the source language's toolchain installed.

### Docker / OCI images

Image published to a registry (Docker Hub, GHCR, GCP Artifact Registry); users `docker run` or wire the image into a host config snippet. Provides zero-install dependency isolation; the canonical install path for several large official servers. Cross-role: also serves as the test stack and the deployment artifact for some samples. Appropriate when consistent runtime + dependency packaging matters more than launching a native process.

### Source language package manager

`go install` for Go modules; `pnpm install` / `npm install` for TypeScript; `uv sync` for Python; Git dependency in `deps.edn` for Clojure; `pip install` (notably absent in this bin in favor of `uv sync` or `fastmcp install`). Each requires the audience to have the language toolchain installed. Appropriate as a developer-targeted distribution alongside binary or Docker for end users.

### Homebrew formula

A `brew install` path on macOS (and Linux via brew). Wraps a binary download with a tap-managed update channel. Appropriate as one channel among several when reaching macOS-heavy developer audiences matters.

### NPM shim wrapping a non-Node binary

An npm package (`@scope/server`) that downloads or wraps a native (Go, etc.) binary so node-oriented hosts can run the server by name via `npx`. Cross-ecosystem glue — the server isn't a Node program, but the install surface is. Appropriate when the audience expects `npx` install paths regardless of the server's actual runtime.

### Hosted endpoint (no install)

Users address a running URL (`gitmcp.io/{owner}/{repo}`, `mcp.sentry.dev`, `api.githubcopilot.com`); no install on the user's side. The maintainer operates the deployment. Appropriate when a single hosted instance can serve many users (public-data services, official cloud-backed products).

### Source clone

The repo is cloned and run from source — no published artifact. The minimum viable distribution. Appropriate for projects that haven't yet published, internal tools, or frameworks where consumers are expected to build atop the source.

### SDK CLI installer

A framework-specific installer command (`fastmcp install <script.py>`) registers the script with target hosts and wires up the runtime invocation. Appropriate within ecosystems whose SDK provides such a CLI; substitutes for hand-edited host config files.

## Entry point

The literal command shape users or hosts type to launch the server. Constrains how host-config snippets are written and how upgrades propagate.

### Subcommand verb

The binary takes a subcommand selecting mode (`server stdio`, `server serve --write-access`, `server setup --tool=cline`). Mode is an explicit verb rather than a flag, separating "run the server" from "configure a host" cleanly. Appropriate when the binary has multiple roles beyond running the server.

### Hosted URL endpoint

Not a command at all — users put a URL in their host config. The host opens an HTTP/SSE connection. Appropriate for hosted-deployment products.

### Module invocation

`python -m package.server` — Python's module entry point. Avoids requiring a console-script entry in `pyproject.toml`. Appropriate when the project is happy to expose its package path to users; common in source-distributed Python servers using uv.

### `npx` package invocation

`npx @scope/server@latest --flag value` — node ecosystem's pull-and-run convention. Often paired with the npm distribution channel. Appropriate when the audience has Node and benefits from no-explicit-install ergonomics.

### Profile-driven launcher

`clj -M:profile` — Clojure's profile mechanism, where `:stdio-server` and `:sse-server` are aliases in `deps.edn` selecting transport mode. Appropriate within Clojure tooling where profiles are the idiomatic launch surface.

### Framework CLI run

`fastmcp run <script>` or `fastmcp install <script>` — framework's own CLI handles the runtime invocation. Substitutes for a project-level entry point. Appropriate when committing to the framework's conventions.

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

## Test stack

How the project verifies its own behavior. Constrains release cadence and refactor safety.

### Recorded HTTP fixtures (cassettes)

Tests run against checked-in HTTP recordings (go-vcr cassettes, similar libraries) so the suite is reproducible offline without upstream credentials. A separate live-mode flag re-records when the upstream API changes. Appropriate when tests need to exercise real upstream API shapes but CI shouldn't pay per-run API costs or require credentials.

### Unit tests in language-native framework

Standard `pytest`, `vitest`, `go test`, or Clojure's testing convention. Run via the project's task runner. Appropriate as the baseline for any project; needed to make refactors safe.

### Evaluation harness alongside unit tests

A separate `eval` task that runs scenario-based evaluations against model outputs, distinct from unit tests. Catches behavioral regressions that unit tests can't (e.g., a tool description change degrading model accuracy). Appropriate when the server's value depends on how well models use its tools, not just whether the tools work.

### End-to-end with browser automation

Playwright tests exercise the full stack from a real browser/host through the MCP endpoint. Higher fidelity, slower, more brittle. Appropriate when the deployment includes a web UI alongside MCP.

### Test configuration via project alias

A test-only profile (`tests.edn`, similar) declares the test runner config separately from the main project. Appropriate within ecosystems where alias-driven tooling is idiomatic (Clojure).

### In-memory transport for protocol tests

Tests instantiate server and client in the same process and exchange messages via in-memory transport, skipping serialization overhead and process boundaries. Appropriate for verifying protocol-level behavior in isolation.

### None

Some samples ship without tests — particularly minimal single-file scripts where the value lies in being demonstrative. Appropriate only when the surface is small enough that manual verification suffices.

## CI

Automated build/test gating on pushes and PRs. Constrains release safety and contribution velocity.

### GitHub Actions

The dominant choice across this bin — workflows under `.github/workflows/` triggered on push, PR, and version tags. Often paired with automated release artifacts (binary builds, container pushes). Appropriate as the default for any GitHub-hosted project.

### GitHub Actions plus dedicated lint config

GitHub Actions plus a language-specific linter config checked in (`.golangci.yml`, `.cljstyle`, `clj-kondo`). Lint runs as a CI step, separate from tests. Appropriate when style and static-analysis enforcement matters and the project wants the lint rules versioned alongside the code.

### Release-cut workflow on tag push

A workflow triggered specifically by version-tag pushes that builds and uploads release artifacts (cross-platform binaries, container images). Decouples release from CI's normal pass/fail gate. Appropriate when releases are a deliberate event and not every passing build should produce one.

## Container/packaging artifacts

Files in the repo that define how the server gets containerized or otherwise deployment-packaged. Distinct from the distribution channel — these are the artifacts that produce the channels.

### Dockerfile

A single Dockerfile at repo root that produces the image published to a registry. Often multi-platform via buildx. Appropriate as the minimum viable container artifact when distributing via Docker.

### Dev container

A `.devcontainer/` directory defining a development environment in a container. Separate concern from runtime distribution. Appropriate when the author wants contributors to spin up an identical dev environment without local toolchain installation.

### Cloudflare Workers config

`wrangler.jsonc` declares the Workers deployment. There is no Dockerfile because the runtime substrate is the Workers platform. Appropriate when the project is itself a Workers application.

### None observed

Some samples ship no container artifacts — distribution is via source clone, source-language package manager, or framework installer only. Appropriate when the audience is comfortable with native runtime installs.

## Host integration

How the server gets wired into specific MCP-host applications (Claude Desktop, Claude Code, Cursor, VS Code, Cline, etc.). Constrains documentation surface and onboarding friction.

### README snippets per host

The README documents the JSON config block for each supported host (often 5-8 hosts). The most common pattern. Appropriate as the baseline; cheap to add a new host but high user friction.

### In-repo Claude plugin wrapper

The repo ships a `.claude-plugin/` directory and `.mcp.json` so the server installs as a Claude plugin without any additional wrapping by the user. Rare; the server vends itself as a plugin, not just a raw MCP binary. Appropriate when the maintainer wants Claude users to have a one-click install rather than a config-file edit.

### Co-located VS Code extension

A parallel VS Code extension (TypeScript) ships in the same repo as the MCP server. Provides a non-MCP integration path alongside MCP. Appropriate when the audience uses VS Code heavily and wants editor integration deeper than MCP would provide.

### First-party host extension manifest

A host-specific manifest file (e.g., `gemini-extension.json`, `.gemini/` directory) declares the integration with a specific host the project has a special relationship with. Appropriate when the project is owned by or aligned with the host's vendor.

### Framework-installer wires hosts

The framework's CLI installer registers the server with the target host transparently — no user-facing snippet, the framework knows how to talk to each supported host. Appropriate when committing to a framework that has solved this concern.

### Marketplace plugin distribution

The server is distributed through a host's plugin marketplace and installs via the marketplace UI. Bypasses config-file editing entirely. Appropriate when the audience uses a mainstream host with a plugin marketplace and the maintainer wants minimum-friction install.

## Observability

How the server exposes its operational state. Across this bin, observability is consistently underdocumented; the patterns below are mostly absences and conventions.

### stderr logging (convention)

Most servers log to stderr by default — implicit in stdio transport since stdout is the protocol channel. Format and levels are typically not documented. Appropriate as the default; explicit only when the project deviates.

### Suppressed progress output

Stdio servers explicitly suppress progress messages to keep stdout clean of non-protocol bytes. A documented design concern in some projects. Appropriate (in fact required) for any stdio server.

### Not documented

Most projects in the bin do not document logging destination, format, metrics, or tracing. Operators are left to infer from runtime behavior. A widespread gap; not so much a chosen path as an absent one.

## Repository layout

How the project organizes its source tree. Constrains contribution patterns and what can be released independently.

### Single-package source

One module/package in conventional language layout (Go: `cmd/`, `pkg/`, `internal/`; Python: `src/`; TypeScript: `app/`, `src/`). The simplest organization. Appropriate when one server is one product.

### Single-file script

The entire server is one `.py` file with a `requirements.txt`. The minimum viable layout. Appropriate when the server's surface is small enough that splitting adds no value.

### Monorepo (workspace)

Multiple packages under a workspace tool (pnpm + Turbo, similar). Server, clients, evals, plugin wrappers, and docs as sibling packages. Appropriate when the product spans multiple deliverables that share build infra.

### Polylith components

Clojure's Polylith style — `bases/`, `components/`, `projects/` separating reusable components from project-specific bases. Heavyweight modular architecture. Appropriate when components are genuinely reused across multiple deliverables.

### Mixed-language monorepo

A primary-language source tree (e.g., Python under `src/`) alongside a parallel subproject in a different language for editor integration (e.g., TypeScript under `vscode-extension/`). Appropriate when one product needs both an MCP surface and a native editor extension surface.

## Safety posture

How the project constrains potentially-dangerous operations. Distinct from authentication; this is about what can be done once authenticated.

### Read-only by default with explicit write flag

Write operations are gated behind a `--write-access` (or `--read-only` inverse) flag. The default is the safer mode. Conservative posture; rare among MCP servers, which more commonly ship full capabilities unconditionally. Appropriate when the upstream is mutation-capable (issue trackers, source control) and accidental writes are damaging.

### Per-tool auto-approve gating

Operators mark specific tools as safe to run without per-call confirmation, leaving the rest gated. Granular trust boundary at the tool level. Appropriate when the tool catalog mixes safe and dangerous operations and the operator wants asymmetric trust.

### Lockdown / content-filter mode

A flag that filters content from public/untrusted upstream resources before returning it to the agent. Layered over tool selection — operates regardless of which tools are enabled. Appropriate when the agent will traverse untrusted content and the project wants a safety envelope on what reaches the model.

### Tool-layer query validation

The server validates inputs at the tool layer (e.g., SELECT-only enforcement, row-count caps) rather than relying on database-level controls. Defense in depth. Appropriate when the upstream is a general-purpose data store that the project wants to constrain to a safer subset.

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
