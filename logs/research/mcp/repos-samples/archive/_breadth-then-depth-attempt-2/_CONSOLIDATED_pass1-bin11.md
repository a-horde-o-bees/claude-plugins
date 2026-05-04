# Sample

Pass-1 Phase-1a partial for bin 11. Functional decomposition of `rust-mcp-stack--rust-mcp-filesystem.md`, `sajal2692--mcp-weaviate.md`, `samuelgursky--davinci-resolve-mcp.md`, `sandraschi--email-mcp.md`, `severity1--terraform-cloud-mcp.md`, `shibuiwilliam--mcp-server-scikit-learn.md`, `shreyaskarnik--huggingface-mcp-server.md`, `slackapi--slack-mcp-plugin.md`, organized by role with implementation paths as sub-sections.

## Server runtime

The language and library that hosts the MCP protocol loop and dispatches tool/resource/prompt calls. The runtime determines async model, type derivation, and what packaging conventions are available downstream.

### FastMCP (Python)

High-level Python framework that wraps the MCP SDK with decorator-based tool registration and Pydantic-backed schema auto-derivation. Author writes `@mcp.tool` decorated functions; FastMCP handles JSON-RPC plumbing, schema generation from type hints, and transport selection via CLI arguments. Floor versions observed range from unspecified pins up through `>=3.1.0,<4` (the highest in this bin), with later majors changing import patterns. Appropriate when the author wants minimal protocol boilerplate and is working in a Python ecosystem where Pydantic types are the natural schema source. Constrains the runtime to Python's async surface and pins the schema strategy to Pydantic.

### Raw `mcp` Python SDK

Lower-level Python entry where the author imports `from mcp.server import Server` (or similar) and wires JSON-RPC handlers more directly. Schema is still Pydantic-backed but tool registration is hand-rolled rather than decorator-driven. Appropriate when the server exposes a wide tool surface that benefits from custom dispatch (hundreds of tools), uses MCP's full surface (resources + prompts in addition to tools), or wraps a sync-only third-party library where FastMCP's async-first ergonomics add no value.

### Rust with rust-mcp-sdk + rust-mcp-schema

Rust runtime built on the rust-mcp-stack family of crates. Compiles to a static binary with no external runtime dependencies, enabling distribution as a single executable across Homebrew, Cargo, npm, and Docker channels. Pinned to a specific Rust toolchain via `rust-toolchain.toml`. Appropriate when performance matters (filesystem operations at scale), when zero runtime dependencies are a deployment requirement, or when the author wants to ship as a static native binary instead of depending on Python/Node ubiquity.

### Remote HTTP service (no local runtime)

The "runtime" lives on a vendor-hosted endpoint; the GitHub repo carries only client config files and OAuth metadata. There is no local language or framework to choose because nothing executes on the user's machine. Appropriate when the vendor wants centralized control over capability evolution, rate limits, and credential rotation, and is willing to take on the operational cost of hosting.

## Transport

How the MCP protocol bytes flow between client and server. Transport choice is downstream of runtime locality (local vs remote) and upstream of authentication options.

### stdio

JSON-RPC over the launched subprocess's stdin/stdout. Default for every locally-launched server in the bin; the host spawns the server as a child process and frames are read line-by-line. Implies single-tenant, single-process operation — one client per launched server. Forces strict discipline on stdout/stderr separation: any stray `print` corrupts the JSON-RPC stream, so servers either suppress prints in core handlers or route logs to stderr only. Selected by default when nothing else is configured; sometimes only inferred (not even documented) because it is the universal MCP baseline.

### streamable-http

HTTP transport with streaming responses, optional alongside stdio. Selected via CLI argument or environment variable at launch. Enables remote/network deployment, multi-client connection patterns, and integration paths that don't fit a forked-subprocess model. Appropriate when the server may be accessed by clients on different machines or when the author wants to keep stdio for desktop-host configs while still enabling network access.

### Remote HTTP endpoint

The transport is HTTPS to a vendor-hosted URL like `https://mcp.slack.com/mcp`. There is no local subprocess at all; the client connects directly to the vendor's service. Implies OAuth-style authentication (the server can't trust environment variables that only the user's process would see), per-workspace tenancy, and operator responsibility for uptime and rate limits. Appropriate when the vendor wants to deliver MCP as a hosted service rather than a downloaded artifact.

## Capability surface

Which of MCP's three feature surfaces — tools, resources, prompts — the server exposes, and how that surface is sized.

### Tools-only

The server exposes only the tool surface; no resources, no prompts, no sampling. The most common shape across the bin. Tool counts vary from 6 (curated, single-domain) to 50+ (broad REST API wrapping). Appropriate when the integration target is naturally action-oriented (send email, query database, mutate cloud resource) and when authors want to minimize MCP-feature surface area.

### Tools + resources + prompts (full MCP surface)

Server uses all three surfaces in one process: tools for actions, resources exposed under a custom URI scheme (e.g. `hf://`) for browsable content, and prompts as named templates the host can offer to users. Demonstrates MCP features that most servers ignore. Appropriate when the integration target has rich hierarchical content worth exposing as resources (model/dataset/space catalogs) and when there are reusable prompt patterns specific to the domain ("compare these models", "summarize this paper").

### Tools + sampling + prompts

Server adds MCP's sampling surface (server-initiated LLM calls back through the host) on top of tools and prompts. Used for agentic helpers like subject-line suggestion or multi-turn assist that need the host's LLM rather than running inference locally. Appropriate when the server has small auxiliary completions to make and doesn't want to bring its own inference path.

### Tool-count modes (compound vs full)

A single server ships two operating modes: a compact "compound" surface (tens of aggregate tools) and a "full" surface (hundreds of granular tools), selectable via CLI flag at launch. Lets the user trade context-window pressure against expressive granularity without re-installing. Appropriate when the integration target has a very wide API (hundreds of methods) and the author has measured that the full surface overwhelms typical prompt budgets.

### Tool-disabling at launch

Single-mode server but with a launch-time mechanism to disable individual tools, reducing capability surface and token usage for token-sensitive deployments. Distinct from a write-mode flag — this is per-tool subtraction, not category-level gating. Appropriate when different deployments need different subsets of the server's capability and token cost is a measured concern.

## Safety gating

Mechanisms the server uses to prevent destructive or sensitive operations from being invoked accidentally. Gating sits between the tool surface and the underlying integration.

### Read-only-by-default

The server runs in read-only mode unless explicitly opted into write access. Implemented either as a runtime flag (`READ_ONLY_TOOLS` env var) or as the only mode the server ever offers (no write tools shipped at all). Appropriate for filesystem and read-heavy data servers where the destructive blast radius of a mistaken tool call is high.

### Two-axis flags (read-only + enable-delete)

Orthogonal switches for write and delete: a server may be writable but still refuse delete unless a separate flag is set. Recognizes that delete is more dangerous than other writes and deserves its own gate. Implemented as separate env vars (`READ_ONLY_TOOLS`, `ENABLE_DELETE_TOOLS`). Appropriate when the integration target's API mixes safe writes with irreversible destructive operations and a single "write mode" toggle would conflate them.

### Path-traversal protection

For servers exposing file operations, tool implementations validate that requested paths stay within configured root directories. Pairs with auto-cleanup (export files deleted after response is encoded) to prevent disk bloat and cross-tenant leakage on shared machines. Appropriate whenever the tool surface accepts user-controlled paths.

### Vendor-side capability scoping

Remote MCP services constrain what the server will do via OAuth scope and workspace admin approval, not via flags the user sets. The server itself enforces; the user can't elevate. Appropriate when the deployment model is hosted-service-with-tenants rather than local-subprocess.

## Authentication

How the server obtains the credentials it uses to call the underlying integration target.

### None (local-only operations)

Server operates on local filesystem, local data, or a locally-running application; no credentials needed. Filesystem servers and local-ML servers fit here. The "auth" question collapses into per-tool path or scope validation. Appropriate when the integration target lives on the same host as the server.

### Locally-running application's IPC

Server talks to a desktop application over its own scripting interface (e.g. DaVinci Resolve's Python scripting API). The application enforces its own access model; the MCP server has no auth layer of its own. Requires the application to be configured for external scripting access. Appropriate when the integration target is a desktop application rather than a cloud service.

### Single API token via env var

The server takes one API token (`HF_TOKEN`, `TFC_TOKEN`, etc.) from environment variables and uses it for every outbound call. Single-tenant by construction — one process, one credential set, one identity. Appropriate when the integration is a single-account SaaS with token-based auth and tenancy lives entirely outside the server.

### Multi-provider credential bundles

Server accepts credentials for many simultaneous backends (10+ email providers, multiple embedding services) and selects per-call which to use. Credentials still come from environment variables, but the env surface is much wider. A `configure_service` tool can also re-point credentials at runtime without restart. Appropriate when the server is a unified front for a heterogeneous backend ecosystem and users want to swap or compare providers without process churn.

### Optional bearer for elevated access

Server runs unauthenticated by default for public read access; an optional token unlocks higher rate limits or private-resource access. Appropriate for public-data integrations where unauthenticated use is a real flow but heavy users need a way to identify themselves.

### OAuth 2.0 with workspace approval

Remote MCP service requires OAuth flow with vendor-specific clientId per host, workspace admin approval, and a callback port for the OAuth handshake. The configs-only repo provides the per-host clientIds and callback ports rather than running the OAuth dance itself. Appropriate for hosted multi-tenant services where each tenant is an organization with its own admin policies.

## Multi-tenancy

How the server handles multiple distinct identities or scopes within one deployment.

### Single-user per process

One process, one identity, one set of credentials. The default for every locally-launched server in the bin. Tenancy questions are pushed to the host (run separate processes for separate identities). Appropriate when tenancy is naturally scoped to the user running the host application.

### Per-call tenancy argument

Tenancy lives in the tool signatures themselves — search and retrieval tools take a tenant identifier as an argument and route the underlying call into that tenant's slice. Treats tenancy as a first-class parameter rather than a process-level config. Rare across the Python ecosystem, which usually pushes tenancy to env vars. Appropriate when the integration target is itself multi-tenant (vector DBs with tenant collections) and a single MCP process should be able to serve multiple tenants through one credential.

### Per-workspace OAuth token

Remote service issues one token per workspace via OAuth flow. Workspace is the tenant boundary; the token implies which workspace's data the call sees. Appropriate for hosted vendor services where workspace is the natural unit of administration and billing.

## Configuration delivery

How the server learns its operating parameters at startup or runtime.

### Environment variables

Dominant pattern across the bin. API tokens, connection parameters, feature flags, and provider credentials all arrive as env vars. The MCP host config (per-client JSON) is responsible for setting them before launching the subprocess. Appropriate for any local-process server where credentials shouldn't be in command lines or files.

### CLI arguments

Mode flags and transport selection arrive as command-line arguments at launch (`--full` for capability mode, `--transport http`). Appropriate for choices that change the server's structural behavior rather than its credentials.

### Runtime reconfiguration tool

A dedicated tool (`configure_service`) lets the host swap providers or update settings during a session without restart. Used by servers with multi-provider backends where the user might want to switch from SendGrid to Mailgun mid-conversation. Appropriate when the integration target is multi-provider and the user expects to compare or rotate without process churn.

### Per-client JSON config (host-side)

Configuration that the MCP host (Claude Desktop, Cursor, Claude Code) reads to know how to launch the server. Different hosts use different paths and shapes — `claude_desktop_config.json`, `mcp.json`, `.cursor-mcp.json`, `glama.json`. Generated either by hand, by an installer script, or shipped as ready-to-use samples in the repo. Appropriate as the universal user-facing surface; everything else (env vars, CLI flags) is consumed via this layer.

## Distribution channel

How end users obtain the server. A single project usually ships through several channels in parallel.

### PyPI via uvx

`uvx <package>` is the user's primary install command — uv resolves and runs the package without an explicit install step. Requires `uv` on the user's machine but eliminates venv management. Appropriate for Python servers targeting host configs where one-line invocation matters more than reproducible installs.

### PyPI editable + uv source

Source clone followed by `pip install -e ".[dev]"` or `uv sync`. Optional dev extras live under `[project.optional-dependencies]`. Appropriate for developer-facing distribution and for servers where the author hasn't (or won't) push to PyPI but still wants Python's standard tooling.

### Custom Python installer script

A bespoke `install.py` (multi-KB) creates a venv, installs deps, and writes per-client JSON configs into 10+ MCP client locations. Replaces both pip and uvx for the end user; the only command they run is `python install.py`. Appropriate when the server has unusual host-side requirements (must locate a desktop application, must write configs to many client locations) that no general-purpose installer could handle.

### MCPB bundle

Pre-packaged bundle for drag-and-drop install into Claude Desktop. Authoring may require a Rust signing path (Cargo.toml alongside pyproject.toml) for bundle signing. Appropriate when the target audience is desktop-host users who shouldn't have to use a command line.

### Smithery registry via npx

`npx -y @smithery/cli install <name> --client claude` registers the server through the Smithery hub. Appropriate when the author wants registry-level discoverability and is willing to depend on Smithery as the install path even for non-JS servers.

### Cargo

`cargo install <crate>` for Rust servers; the user gets a compiled binary on their PATH. Appropriate when the server is Rust and the audience already has a Rust toolchain.

### Homebrew

`brew install <formula>` distribution, paired with shell installer scripts on Unix and PowerShell installers on Windows. Appropriate as a polish channel for native binaries that warrant package-manager presence.

### npm package wrapping native binary

Native binary published as an `@scope/package` npm package so Node-ecosystem users can pull it with the tooling they already have. Appropriate when a Rust or other native binary wants to reach the broad npm install surface without forcing users to install Cargo.

### Docker Hub MCP Registry

Container image published to Docker Hub's MCP-specific registry. Distinct from a generic Docker Hub push because the registry is scoped to MCP servers. Appropriate when the server has external dependencies that benefit from being containerized and the author wants the registry's MCP-aware discovery.

### Generic Docker image

Dockerfile in repo, image built and pulled by users. Provides a uniform launch shape across operating systems. Appropriate when the server has system-level dependencies that benefit from containerization and the user is comfortable composing their own deploy.

### GitHub release binary downloads

Pre-compiled binaries attached to GitHub releases, fetched directly by users. Appropriate as a fallback for users who don't want to use any package manager.

### Source-only

No published artifact; users clone the repo and run from source. Appropriate when distribution scale is small (single-digit stars), when the author hasn't invested in a release pipeline, or when the install workflow is necessarily custom.

### Configs-only repo (no server artifact)

Repo ships only client config snippets and OAuth setup metadata; the actual server is hosted remotely by the vendor. Distribution is "configure your client to point at our endpoint." Appropriate for vendor-hosted remote MCP services.

### Zed extension

Editor-specific extension distribution channel for users running Zed. Appropriate as a long-tail audience reach for servers whose authors want broad editor coverage.

## Entry point shape

What the user (or host config) actually invokes to start the server.

### Console script via PyPI

`[project.scripts]` declares a name (e.g. `mcp-weaviate`, `terraform-cloud-mcp`) that uvx or pip installs onto the user's PATH. Host configs invoke the bare name. Appropriate as the cleanest user-facing shape for Python servers with PyPI presence.

### `uv --directory=<path> run <script>`

Path-anchored invocation where the host config points uv at a local source checkout. No console script involved; the user must know both the package directory and the script name. Appropriate for developer-installed servers that don't aim for pip-install-everywhere distribution.

### Bare Python script

Host launches `python <script.py>` directly with absolute paths to a venv interpreter and the script. No packaging entry point at all. Appropriate when the server intentionally avoids Python packaging (custom installer owns the venv) or when a single-file "hackable" layout is the author's convention.

### Native binary

Standalone executable installed via Cargo, Homebrew, npm, or release download. Host invokes the binary by name. Appropriate for Rust and other compiled-language servers with no runtime deps.

### Vendor URL (no local entry)

Host config points at an HTTPS URL; no local launch. Appropriate for remote-hosted MCP services.

## Repo layout

How source, tests, and supporting concerns are arranged in the repository.

### Single-package src-layout

`src/<pkg>/` for source, `tests/` for tests, single pyproject.toml. The Python convention for cleanly-packaged servers. Appropriate when the project is one server with no auxiliary services.

### Single-package flat layout

Server file at repo root with optional `src/<helpers>/`. Common for "hackable" community servers where the entire server may fit in a few hundred lines. Appropriate for small, single-author projects where the overhead of src-layout would be ceremony.

### Domain-per-module decomposition

Source organized as modules per integration domain (account, workspace, run, plan, …) when the server wraps a wide REST API. Each module owns its own tools and types. Appropriate when the wrapped API has natural domain divisions and the codebase would otherwise be one large file.

### Multi-directory single-repo (ancillary services)

The repo holds the MCP server alongside related but distinct concerns: a web monitoring dashboard (its own build pipeline, often Vite + Uvicorn), a packaging directory, scripts, and examples. The server is one product among several in the same repo. Appropriate when the author wants ops/monitoring artifacts to ship alongside the server but with distinct build and run paths.

### Configs-only

No `src/`. The repo carries `.mcp.json`, per-host config files, and possibly companion `commands/` and `skills/` directories for client-side artifacts. Appropriate when the server is remote and the repo's job is to deliver client-side configuration.

## Test stack

How the server is verified during development and CI.

### pytest

Standard for Python servers. Tests in `tests/`, sometimes with `pytest.ini` at root for legacy reasons or `pyproject.toml` `[tool.pytest.ini_options]` config. Async paths use `pytest-asyncio`. Coverage via `pytest-cov`. Appropriate as the default for Python.

### cargo-nextest

Rust test runner orchestrated through a `Makefile.toml` that also defines `fmt`, `clippy`, `check`, and `clippy-fix` targets. Faster than `cargo test` for larger suites. Appropriate for Rust servers that warrant a test runner upgrade.

### Live multi-phase suite against application

Bespoke test harness organized in phases (read-only → destructive → media → AI/ML → advanced) running against a real instance of the integration target. Coverage reported as percent-of-API-methods-exercised rather than line coverage. Appropriate when the server wraps a large, stateful application where mocking would be more code than the harness.

### None observed

Some samples ship without surfaced tests at all. Appropriate signal of small audience or early stage; not a recommendation.

## CI

What runs on push or pull request.

### GitHub Actions with quality matrix

Workflow runs lint (ruff), formatter (ruff/black), type check (mypy), security scan (bandit), and tests across a Python version matrix (3.10/3.11/3.12). Webapp components may add Biome. Appropriate when the project warrants strict typing and security discipline.

### GitHub Actions with Rust toolchain

Workflow runs the Makefile.toml targets — fmt, clippy, test, check — under the pinned Rust toolchain. Appropriate for Rust servers.

### GitHub Actions present (details unspecified)

Workflow file exists but the bin's evidence didn't surface specific jobs. Appropriate baseline.

### Not applicable

Configs-only repos and remote services have no CI surface to speak of in the public repo. The vendor's hosting pipeline is invisible.

## Container artifact

Whether and how the server ships as a container image.

### Multi-stage Rust to Alpine

Builder stage uses `clux/muslrust:stable`, final stage is `alpine:latest` with a non-root user. Produces a small static-binary image. Appropriate when the server is Rust and the author wants minimal image size.

### Generic Dockerfile

Single-stage or simple multi-stage Dockerfile in repo. Appropriate as a general-purpose containerization channel for users who prefer Docker.

### No container

Container omitted intentionally because the server must run on the host with the integration target (desktop application, local-process IPC), or because MCPB bundling replaces the container role. Appropriate when containerization would break the integration model.

## Host integration surface

Which client hosts the server explicitly supports through documentation, configs, or installers.

### Claude Desktop

Universal — every locally-launched server in the bin documents Claude Desktop. Configuration is JSON in `claude_desktop_config.json` with `command` and `args`. Often paired with MCPB for drag-and-drop install. Appropriate as the baseline desktop integration.

### Claude Code CLI

Documented via `claude mcp add` registration or via a `.mcp.json` in the repo. Some configs-only repos publish a clientId for OAuth-based remote MCP integration. Appropriate when the audience includes CLI/agent users.

### Cursor IDE

Documented via JSON `mcpServers` entry, `.cursor-mcp.json`, or `.cursor-plugin/` directory. Sometimes with deeplink-based browser setup for OAuth. Appropriate as the second-most-targeted IDE host.

### VS Code, Windsurf, Copilot Studio

Documented in the same JSON `mcpServers` shape; sometimes via a universal installer that writes per-host configs. Appropriate when the author wants reach across all major MCP-capable hosts.

### Zed

Documented as a Zed extension. Less common; sometimes the only sample in a bin to mention it. Appropriate as a long-tail editor audience.

### Smithery / Glama discovery

Registered with discovery hubs via `glama.json` (Glama) or by being installable through Smithery's `npx`. Appropriate when the author wants registry-level visibility beyond per-host configs.

### Universal installer covering many hosts

A single `install.py` script writes per-host configs to up to 10 MCP client locations in one invocation, eliminating per-host setup steps. Appropriate when the user audience is broad and the author wants to remove the "find your client's config file" step entirely.

## Observability

How the running server reports its health and behavior.

### stdout/stderr discipline only

Server avoids any stdout output that isn't JSON-RPC; logging is silent or routed to stderr. The `print` policy is sometimes documented as zero-tolerance because a single stray print breaks the protocol. Appropriate for stdio servers where stdout is the wire.

### Companion monitoring dashboard

Separate web app (Vite + Uvicorn on dedicated ports) ships in the same repo for monitoring and control. Distinct process, distinct ports, not bundled into the MCP server itself. Appropriate when the server has long-running state worth visualizing and the author wants admin tooling beyond logs.

### Debug logging flag

Server emits debug-level logs when an env flag is set; format and destination often unspecified. Appropriate as a minimal observability surface for servers without dedicated dashboards.

### Not surfaced

Many samples don't document observability at all. Appropriate signal that the server runs short-lived per request and observability hasn't become a need.

## Developer ergonomics

Tools and scripts the author provides to themselves and contributors.

### Justfile recipes

`just <target>` for build, test, lint, package operations. Less common in MCP servers than Makefile but visible in this bin. Appropriate when the author prefers Just's simpler syntax over Make.

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

## Type and schema strategy

How tool input/output types are declared and validated.

### Pydantic via FastMCP auto-derivation

Tool function signatures use Python type hints; FastMCP derives JSON schemas via Pydantic at registration time. Appropriate as the path of least resistance for FastMCP servers.

### Pydantic via raw MCP SDK

Author writes Pydantic models explicitly and registers them with the SDK's tool registration calls. Appropriate when the author wants explicit control over schema shape (descriptions, field metadata) that decorator-magic might obscure.

### Hand-authored tool schemas

For very large tool surfaces (300+ tools), schemas are hand-authored or generated rather than reflected from Python signatures. Appropriate when reflective derivation would be too slow at startup or when the source of truth is an external API spec.

### Rust schema crate

`rust-mcp-schema` crate provides the type definitions; tools are registered with strongly-typed handlers. Appropriate as the natural Rust idiom — types are compile-time-checked rather than reflected.

## Async model

Whether tool handlers are sync or async, and what drives the choice.

### Async throughout

Tool handlers are `async def`; FastMCP and the MCP SDK both accept async handlers natively. Connection pooling for outbound calls is enabled. Appropriate when the integration target has an async client library or makes network calls that benefit from non-blocking IO.

### Sync throughout

Tool handlers are plain `def`. Forced when the underlying library is sync-only (scikit-learn, DaVinci Resolve's scripting API). Wrapping sync work in async would add thread overhead with no concurrency win. Appropriate when the integration target is sync by nature.

### Mixed

The MCP SDK accepts both forms in the same server; some tools are async (network calls), others sync (CPU work). Appropriate when the integration target has both kinds of operation.

## Documentation surface

How the project explains itself to users and contributors.

### README + docs/ directory

README provides one-line purpose, install commands, and host configs; deeper material lives under `docs/`. Appropriate when the project has more than a quickstart's worth of explanation.

### README + examples/

README points at runnable examples in `examples/` for users to copy-paste. Appropriate when the integration is best learned by running a small sample.

### CLAUDE.md alongside README

Repo carries a `CLAUDE.md` file with agent-facing operational notes distinct from the user-facing README. Appropriate when the project anticipates being driven by Claude Code or similar agents and wants to encode procedural knowledge in a place agents will read.

### Multi-host config samples

Repo carries `.mcp.json`, `.cursor-mcp.json`, `glama.json`, MCPB `manifest.json`, all in the root for users to consult per host. Appropriate when the author wants every host's setup to be one file copy away.

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

## Cross-role tools

Tools that surface under multiple functional roles in this bin.

### Docker

Surfaces as both a distribution channel (Docker Hub MCP Registry, generic Dockerfile pulls) and a container artifact (Dockerfile in repo, multi-stage Alpine build). The build artifact and the distribution path are distinct decisions even when they use the same tool.

### uv

Surfaces as distribution channel (`uvx <package>` for end users), as entry point shape (`uv --directory=<path> run <script>` for path-anchored launch), and as developer ergonomics (`uv run ruff`, `uv run pytest` for dev tasks). Same tool, three roles.

### MCPB

Surfaces as a distribution channel (drag-and-drop bundle for Claude Desktop) and as a release pipeline output (signed bundle artifact). Same tool, two roles.

### Cargo.toml

Surfaces as a Rust runtime declaration (for Rust servers) and as a release-pipeline signing dependency (for Python servers using MCPB bundle signing). Same file, different roles depending on whether the project is Rust or Python.

### GitHub Actions

Surfaces as CI (lint/test/typecheck on PR) and as release pipeline (binary builds, package publishes on tag). Same workflow system, two operational roles.
