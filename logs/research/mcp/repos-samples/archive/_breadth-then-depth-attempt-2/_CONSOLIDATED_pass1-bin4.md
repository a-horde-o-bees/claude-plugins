# Sample

Pass-1 Phase-1a partial for bin 4. Functional decomposition of ckreiling--mcp-server-docker, cloudflare--mcp-server-cloudflare, conikeec--mcpr, crystaldba--postgres-mcp, cyanheads--git-mcp-server, cyanheads--perplexity-mcp-server, datalayer--earthdata-mcp-server, datalayer--jupyter-mcp-server, organized by role with implementation paths as sub-sections.

## Server runtime

The execution environment that hosts the MCP protocol loop, dispatches tool/resource calls, and owns the process lifecycle. Choice of runtime constrains transport options, distribution channels, and dependency management.

### Python with raw MCP SDK

Uses the low-level `mcp` Python SDK (typically `mcp[cli]>=1.x`) without the FastMCP convenience layer. The author writes the protocol handlers directly against `mcp.server`, hand-authoring tool schemas rather than deriving them from type hints. Appropriate when the project needs custom hooks the FastMCP layer hides — access-mode gating, custom SQL parsing, fine-grained tool dispatch — or when the project predates FastMCP and didn't migrate. Implies more boilerplate but more control over request handling and capability registration. Often paired with strict typing tooling (pyright, mypy) since the SDK does less for you.

### TypeScript on Node.js

A Node.js process running the official `@modelcontextprotocol/sdk` (commonly `^1.x`). The runtime supports both stdio and HTTP transports, often paired with Hono for the HTTP layer, Zod for env/config validation, and Pino for structured logging. Distribution is via `npx` against an npm-published package, which makes the install one-line and avoids local Python venv friction. Appropriate when the team's primary language is TypeScript or when the server needs to run inside a JS-centric ecosystem (Cloudflare Workers, browser-adjacent tooling).

### TypeScript on Bun

The same TypeScript codebase auto-detects and runs under Bun (`>=1.2`) when the runtime is Bun, otherwise falls back to Node. Bun is invoked via `bunx`. Appropriate when the project wants startup-time and footprint advantages of Bun without forcing it on users; the dual-runtime path is a courtesy that requires the project to avoid Node-only or Bun-only APIs and to test both runtimes in CI.

### TypeScript on Cloudflare Workers (V8 isolate)

Not Node — the server runs as a Cloudflare Worker in a V8 isolate runtime, deployed via Wrangler. The same TypeScript MCP SDK is used, but the surrounding stack (Workers Bindings, KV, Durable Objects) replaces Node primitives. Appropriate for hosted/remote-only deployment where the author also operates the runtime. Constrains transport to HTTP-style (Workers don't speak stdio); constrains distribution to "remote URL" rather than "installable package."

### Rust

A Rust crate exposing both library APIs and CLI binaries via Cargo. Server scaffolding uses a builder pattern (`ServerConfig::with_name().with_version().with_tool()`) and exposes a `mcpr generate-project` scaffold for downstream authors. Appropriate when callers want native binaries, lower runtime overhead, or want to embed an MCP server in a larger Rust application. Constrains end-user install to Cargo or pre-built binaries; rules out the npx/uvx convenience flows that dominate the JS/Python ecosystem.

## Transport

How MCP protocol messages travel between client and server. Choice of transport drives multi-tenancy ceiling, deployment model, and authentication requirements.

### Stdio

JSON-RPC frames flow over the server process's stdin/stdout. The host (Claude Desktop, Cursor, Cline, etc.) launches the server as a child process and pipes messages through. Default for almost every locally-installed server. Implies single-tenant by construction (one client per process), no network exposure (no auth needed beyond what credentials the process already holds), and trivial deployment (no port, no TLS). Appropriate when the server is meant to run alongside the host on the same machine and access local resources or use locally-stored credentials.

### Streamable HTTP

Long-running HTTP endpoint (e.g., `/mcp`) that supports both request/response and streaming responses. Typically built with Hono on Node or with the Workers runtime. Lets the server run remotely, serve multiple concurrent clients, and front-end an OAuth/JWT flow. Appropriate when the server is hosted (the author runs the runtime) or when local deployments need multi-client access. Constrains the surrounding stack: requires a port, often requires TLS, requires session/auth handling that stdio sidesteps.

### SSE (Server-Sent Events)

Older HTTP-based transport with one-way server→client streaming, separate POST channel for client→server. Often offered as a deprecated/legacy alternative alongside Streamable HTTP — same Worker or process exposes `/sse` for older clients while `/mcp` serves newer ones. Appropriate as a migration aid, not as a fresh choice; flagged "deprecated" in newer projects and the SSE path in some Rust libraries was yanked due to bugs.

### Stdio-to-HTTP shim on the client side

Server speaks Streamable HTTP only; an end-user shim like `mcp-remote` (npm) translates stdio (what the host knows how to spawn) into HTTP requests against the remote URL. The host's MCP config still has a `command`/`args` shape, but the args run the shim and pass it the URL. Lets remote-only servers work with stdio-only hosts. Constrains responsibility: the shim handles auth handshake on the client side; the server never touches stdio.

## Capability surface

What the MCP server exposes to the client beyond raw tools — resources, prompts, sampling, roots, logging.

### Tools only

Server registers tools and nothing else. Common rationale: "the MCP client ecosystem has widespread support for tools but uneven support for resources/prompts." Appropriate when the project wants every supported client to use every feature without gaps. Constrains the client UX — multi-step workflows must be modeled as composable tools rather than as prompts.

### Tools + resources

Server adds resources alongside tools — typically read-only data the client can subscribe to or fetch (container stats, repository metadata). Appropriate when the underlying domain has stateful, observable data that doesn't fit a "call this and get a response" shape. Resources are still under-supported by some clients, so authors offering them often duplicate the data via a tool for compatibility.

### Tools + resources + prompts

Server adds MCP prompts on top of tools and resources, offering pre-canned natural-language workflows the user can pick from a menu (e.g., a "docker-compose workflow" prompt that walks the model through container orchestration). Appropriate when there's a complex multi-step domain workflow the author wants to surface as a first-class capability. Most cloud/infra servers skip prompts; using them is a deliberate design statement.

## Configuration delivery

How runtime configuration (credentials, modes, endpoints) reaches the server.

### Environment variables

Server reads `os.environ` (or equivalent) at startup. Common keys: `DOCKER_HOST`, `DATABASE_URI`, `EARTHDATA_USERNAME`/`PASSWORD`, `JUPYTER_TOKEN`, `PERPLEXITY_API_KEY`. Appropriate everywhere — fits stdio launch (host config sets env in the spawned process), fits container deployment (Docker `-e` flags), fits CI/secrets workflows. Often paired with Zod or Pydantic validation so misconfiguration fails loudly at startup.

### CLI flags

Server accepts `--transport`, `--access-mode`, `--port`, etc. on the command line. Often layered on top of env vars (env defaults, flags override). Appropriate for runtime modes that change per-launch rather than per-environment.

### `.env` file via dotenv

Local-development convenience: same env vars but loaded from `.env` rather than the shell. Always paired with env-var consumption; the file is a delivery mechanism, not an alternative configuration model.

### MCP host JSON config

Indirect — the host's `mcpServers` JSON block specifies the launch command, args, and env that reach the server. Every locally-installed MCP server lives downstream of this; the README's job is to provide the JSON snippet. Appropriate as the user-facing surface; the server itself never reads this file.

### Wrangler config (Cloudflare Workers)

`wrangler.toml`/`wrangler.jsonc` per Worker controls deployment-time configuration (bindings, routes, secrets). Appropriate only for Workers-deployed servers; replaces the env-var/CLI surface for the runtime config that doesn't change per-request.

## Authentication

How the server proves the caller is allowed to invoke its tools.

### None / implicit

Server runs with whatever credentials the host process has and trusts the local execution environment. Common for stdio servers — the host launched it, the OS sandboxes it, no further auth is needed. Appropriate when single-tenant local deployment is the only mode supported.

### API key / token in env var

Server reads a long-lived secret (`PERPLEXITY_API_KEY`, `EARTHDATA_PASSWORD`, `JUPYTER_TOKEN`, `MCP_TOKEN`, `DATABASE_URI` with embedded password) from the environment and uses it on every upstream call. Appropriate for stdio servers fronting a single upstream account; trivial to set up, no handshake required. Constrains tenancy to one account per process.

### JWT

HTTP-mode opt-in: client presents a JWT bearer token, server validates the signature against a configured secret (often required to be 32+ chars). Appropriate when multiple clients share a hosted server and the operator wants to gate access without running an OAuth provider.

### OAuth 2.1 / OIDC

HTTP-mode opt-in: server delegates auth to an OIDC provider (Auth0, Cloudflare's own auth, etc.) and accepts bearer tokens issued by it. Appropriate for production hosted deployments that need real per-user auth, scope-based authorization, or integration with an existing identity stack. Constrains transport (HTTP-only) and adds operational dependencies (the IdP).

### Per-request bearer token (provider-scoped)

Hosted server expects each request to carry a credential scoped to the upstream provider's account (e.g., a Cloudflare API token). The server itself is account-agnostic; tenancy is determined per-call by which token arrived. Appropriate for first-party hosted servers fronting a multi-tenant platform — the same Worker serves any account that authenticates.

### Layered auth (protocol-level + upstream-level)

Server distinguishes "auth to the MCP interface" (e.g., `MCP_TOKEN`) from "auth to the upstream system" (e.g., `JUPYTER_TOKEN`). Appropriate when the MCP server brokers access to a separate authenticated system and the operator wants independent control over who can talk to MCP versus what MCP does upstream. Often a v1.x change after starting with the upstream credential alone.

## Multi-tenancy

How many independent users/workspaces the server can serve simultaneously.

### Single-user per process

One server process serves exactly one user, bound to one set of upstream credentials. The host launches a fresh instance per user. Default for stdio servers. Appropriate when isolation by process is acceptable and the launch overhead is small.

### Multi-client sharing one process via session multiplexing

HTTP server with per-session state — multiple clients connect to the same process, each session keyed by transport-level identity (cookie, header, or token). Appropriate for HTTP servers where startup cost is non-trivial or where shared in-memory state (caches, connection pools) helps performance.

### Workspace-scoped sandboxing within a single tenant

Server constrains per-session operations to a configured base directory or working tree (e.g., git operations confined to `BASE_DIR`). Tenancy is still single-user, but file-system access is segmented per session within that user's allowed space. Appropriate when the underlying tool (git, file ops) would otherwise be free to roam the whole filesystem and the operator wants explicit boundaries.

### Per-request tenancy by inbound credential

Hosted server is account-agnostic; tenancy is determined entirely by the bearer token on each request. Same Worker serves any authenticated account; nothing in the server's state binds it to one user. Appropriate for first-party platform-as-a-service deployments where the platform's existing auth model is the source of truth.

### N/A (library, not a runtime)

Project ships scaffolding and primitives; tenancy is the consumer's concern. Appropriate for SDK/framework projects (`mcpr`) that don't operate a server themselves.

## Distribution channel

How end users get the server onto their machine (or pointer to a hosted instance).

### PyPI via pip / uv pip / pipx

Standard Python package on PyPI installable via `pip install`, `uv pip install`, or `pipx install`. Appropriate when the consumer base is Python-aware and willing to manage a venv (or trusts pipx to do it). Console script lands in `$PATH` after install.

### uvx (PyPI ephemeral)

`uvx <package>` downloads and runs the package in an ephemeral venv without explicit install. Appropriate for one-shot or zero-install user flows; the host's MCP config pins `command: "uvx"` and `args: [<package>]` and uv resolves on every launch (caching). Lower-ceremony than pipx; same package metadata.

### npm via npx / bunx

Node/Bun equivalent of uvx — `npx @scope/package@latest` or `bunx ...` resolves and runs from the npm registry. Appropriate for TypeScript servers; mirrors the uvx experience for the JS ecosystem.

### Cargo crate / cargo install

Rust packages distributed via crates.io. `cargo add` for library use, `cargo install` for CLI tools. Appropriate for Rust-hosted servers; constrains end users to having a Rust toolchain (or accepting pre-built binaries from another channel).

### Docker image (registry-hosted)

Pre-built image on Docker Hub or similar (e.g., `crystaldba/postgres-mcp`, `datalayer/jupyter-mcp-server`). User runs `docker pull` then `docker run` (often invoked via the host's MCP config with `command: "docker"`, `args: ["run", ...]`). Appropriate when the server has heavy dependencies (system libraries, JupyterLab, system tools) or when the author wants to ship a pinned environment regardless of the host OS. Often paired with build-time tweaks (e.g., auto-remap host address from `localhost` to `host.docker.internal` on macOS/Windows, `172.17.0.1` on Linux).

### Source clone + manual build

Last-resort or developer-only path: `git clone`, `npm install && npm run build`, `cargo build`, `uv sync`, etc. Appropriate when no published package exists yet, when the user wants to modify the server, or as the development-mode entry point.

### Smithery registry registration

Project ships a `smithery.yaml` so the server appears in the Smithery MCP server registry. Not a binary distribution channel — a discovery/registration channel that points back to one of the binary channels above. Appropriate when the author wants discoverability through the registry's catalog and one-click client wiring.

### Hosted URL (remote-only)

No installable artifact for the server itself — the user points a client shim (`mcp-remote`) at a URL the author operates. Appropriate when the author wants to keep operational control of the runtime, when the server depends on platform-internal data (e.g., a Cloudflare account's resources), or when patches should propagate without user redeploys.

## Entry point / launch

How the server process is invoked once distribution has put the bits in place.

### Console script

Python `[project.scripts]` or Node `bin` field installs an executable on `$PATH` (e.g., `postgres-mcp`, `earthdata-mcp-server`, `mcp-server-docker`). The host's MCP config invokes this directly. Appropriate as the standard local-install entry point.

### Module/package CLI launcher

`uvx <package>`, `npx <package>`, `bunx <package>` — the package manager itself is the launch verb. Appropriate as the zero-install user flow; works without prior install.

### npm scripts (start/start:stdio/start:http)

`npm start` or named scripts dispatch to the underlying entry. Appropriate as the dev-mode launch path; production users typically prefer the console-script form.

### Docker run

`docker run <image>` (with `-e`/`-v` flags) replaces the local console script with a containerized one. The host's MCP config invokes Docker as the command. Appropriate when the server is distributed as a Docker image and the user wants containerization.

### Generated binary from scaffolded project

Project generator emits a Rust crate; user runs `cargo build` and launches `target/debug/<name>`. Appropriate for SDK projects whose users build their own servers from a template.

### Mounted into another runtime as an extension

Server doesn't run as its own process; it loads as an extension of an existing host (e.g., as a Jupyter Server extension). Configuration lives under `jupyter-config/`. Appropriate when the underlying system already has its own process and embedding is more efficient than running side-by-side.

## Test stack

How the project verifies its own correctness during development.

### pytest + pytest-asyncio

Python test framework with async fixture support. Standard for Python servers using `mcp[cli]` whose tools are `async def`. Often configured via `pyproject.toml`'s `[tool.pytest.ini_options]` with `asyncio_default_fixture_loop_scope = "function"` and a `pythonpath` for src-layout packages. Appropriate for any Python MCP server using async handlers.

### Vitest

JS/TS test framework, often used in Turbo monorepos. Run via pnpm/npm scripts. Appropriate for TypeScript servers, particularly those that share a monorepo with a JS frontend.

### Bun test runner with Vitest compatibility

Bun's built-in test runner running Vitest-compatible specs. Pairs with the dual Node+Bun runtime — same test file works under either runner. Appropriate when the project supports both runtimes and wants to verify both.

### TypeScript noEmit type-check as the test command

`npm test` runs `tsc --noEmit` as the entire test surface. The "tests" check is purely structural (does the project type-check). Appropriate for early-stage projects with no runtime test suite yet; catches type regressions but not behavioral ones.

### Mock transport layer for protocol-level testing

Library/SDK projects ship mock transport implementations so their tests (and downstream consumers' tests) can exercise protocol message flow without a real stdio/SSE channel. Appropriate for SDK projects where the transport layer itself is part of the public API.

## Distribution-time bundling

How the project is packaged into an artifact other than a single source tarball.

### Dockerfile (single-stage)

Builds an image containing the server and its runtime dependencies. Used for both end-user distribution (Docker registry channel) and as a deployment artifact. Sometimes adds quality-of-life touches (host-address auto-remap, entry point wrapper).

### Dockerfile (multi-stage Node Alpine)

Multi-stage build separating the build environment (full Node + dev deps) from the runtime environment (Alpine + production deps). Yields smaller images. Appropriate for Node servers where image size matters.

### Hatchling (Python wheel/sdist)

Python build backend producing wheel and sdist for PyPI publication. `pyproject.toml`-based with `[build-system]` declaring `hatchling.build`. Appropriate as the modern Python packaging default; pairs with uv-managed locks.

### Wrangler bundle (Cloudflare Workers)

Wrangler bundles the TypeScript source into a Worker artifact and deploys directly to Cloudflare's edge. The "package" is the deployed Worker, not a downloadable file. Appropriate for Workers-targeted servers.

### Cargo crate

Rust source compiled and published to crates.io. Appropriate for the Rust ecosystem; consumers either install the binary or depend on the library.

## CI

Continuous-integration provider and what it runs.

### GitHub Actions

Workflows under `.github/workflows/`. Common stages: lint (ruff, eslint, mdformat), type-check (mypy, pyright, tsc), unit/integration tests, dependency audit, sometimes build-and-publish on tag. Universal across the corpus; specifics vary per project.

### Turbo (build orchestrator on top of CI)

Turborepo orchestrates per-package builds and tests across a monorepo. Run inside GitHub Actions. Appropriate for monorepos with multiple packages that share dependencies and want incremental, cached builds.

## Host integration documentation

Which MCP-hosting clients the project's README explicitly walks through configuring.

### Claude Desktop (`mcpServers` JSON block)

The most-documented host. README provides a JSON snippet with `command`/`args`/`env` for the user to paste into `claude_desktop_config.json` or its equivalent. Universal across local-deployment servers.

### Cursor

Same JSON-snippet pattern for Cursor's MCP config. Frequently documented alongside Claude Desktop.

### Windsurf, Goose, Qodo Gen, Cline

Same pattern for other emerging MCP-aware IDEs and agents. Whether they're documented depends on the author's familiarity; multi-host READMEs name them explicitly.

### Cloudflare AI Playground / OpenAI Responses API

First-party platform integrations for hosted-only servers. Documented when the server is platform-specific and the platform's own AI tooling is the natural client.

### JupyterLab as a host

Server runs as an extension inside JupyterLab and is configured via the standard Jupyter extension mechanism rather than via a separate MCP host config. Appropriate when the server brokers access to the surrounding application.

## Observability

Logging, metrics, tracing the server emits in production.

### None surfaced

Project doesn't document logging beyond default stdout/stderr. Appropriate for early-stage or single-user-stdio servers where the host's own logging is sufficient.

### Structured logging library

Pino (Node), `rich`-decorated stdlib logging (Python). Often paired with file rotation and a configurable log level via env var. Appropriate when the server runs as a long-lived process or in production where log searchability matters.

### OpenTelemetry instrumentation

OTel API + SDK as core (or optional) dependency, emitting traces and metrics to whatever collector the operator wires up. Sometimes baked into core deps so every install ships observability; sometimes optional. Appropriate for production-grade servers where the operator is expected to integrate with an observability stack.

### Worker logs (platform-native)

Cloudflare Workers' built-in log surfacing via the dashboard. Not a self-hostable layer; the platform owns it. Appropriate only for Workers-deployed servers.

### Request context tracking for audit

Per-request structured context (request ID, session, principal) attached to every log line so audit trails can reconstruct who did what. Appropriate when the server performs mutations (file writes, git commits, DB execution) and the operator needs accountability.

## Repo layout

How source and supporting files are arranged at the project root.

### Single Python package (`src/<name>/` layout)

`pyproject.toml` at root, source under `src/<package_name>/`, tests under `tests/`. Optional `examples/`, `dev/`, `docs/`. Appropriate as the modern Python default; the explicit `src/` layout prevents accidental imports from the project root during testing.

### Single Node/TS package

`package.json` at root, source under `src/`, dist under `dist/` (gitignored), tests under `tests/`. `tsconfig.json` and `Dockerfile` at root. Appropriate for single-server TypeScript projects.

### Turbo + pnpm monorepo

Multiple packages under `packages/` or domain folders, shared `@repo/<name>` workspace packages, Turbo orchestrating per-package builds and tests. Appropriate when the project ships multiple related servers (e.g., 14 domain Workers) that share scaffolding.

### Single Rust crate with examples

`Cargo.toml` at root, source under `src/`, examples under `examples/`. Appropriate for the SDK/library shape.

### Sibling-package factoring

Project depends on a separate PyPI/npm package owned by the same author that holds extracted concerns (e.g., `jupyter-mcp-tools` holds the tool definitions while `jupyter-mcp-server` holds the runtime). Appropriate when the extracted piece has independent reuse value beyond the immediate server.

## Domain-specific intelligence

Compute the server performs beyond exposing raw upstream operations.

### Pass-through tool wrappers

Tools map 1:1 onto upstream API operations (Docker SDK calls, NASA Earthdata search, Perplexity API, Jupyter kernel ops, raw SQL execution). Server's job is shape translation and credential management, not domain logic. Appropriate as the default; lowest implementation cost.

### Deterministic optimization layered on top of raw ops

Server adds analytical computation that goes beyond exposing the upstream system — workload compression, hypothetical index simulation (hypopg), Pareto-front cost-benefit selection, greedy search adapted from published algorithms. The MCP layer becomes a delivery vehicle for embedded research. Appropriate when the underlying system supports introspection (pg_stat_statements, EXPLAIN) and the author wants to encode performance expertise in tool form.

### In-process safety enforcement via parsing

Server parses inbound payloads before forwarding (e.g., parses SQL with `pglast` to reject COMMIT/ROLLBACK in restricted mode) rather than relying on the upstream system's own permissions. Appropriate when the upstream system's permission model is too coarse (e.g., DB role) and the operator wants finer gating per-tool-call. Constrains the parser's correctness — anything it misses is a security gap.

### Mode parameter for plan-vs-execute

Single tool exposes multiple output modes via a parameter (e.g., `mode: manifest|download|script` for granule downloads). Lets the model preview what would happen before committing to execution. Appropriate when the underlying operation is expensive or irreversible and the user benefits from a dry-run.

### Workflow scaffolding via MCP prompts

Server uses MCP prompts as orchestration primitives, packaging multi-step natural-language workflows (docker-compose orchestration) rather than just exposing atomic tools. Appropriate when there's a complex, repeated workflow worth canonizing.

## Project status

Lifecycle state of the upstream repository.

### Active development

Recent commits, ongoing CI runs, semver-tagged releases. Default for all in-bin samples except one.

### Archived

Repository marked archived by the maintainer (e.g., `mcpr` archived Feb 2026). Code still functions; no further fixes. Appropriate to flag because consumers should weigh adoption risk.
