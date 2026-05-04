# Sample

Pass-1 Phase-1a partial for bin 2. Functional decomposition of JackKuo666--PubMed-MCP-Server, PagerDuty--pagerduty-mcp-server, ahmedmustahid--postgres-mcp-server, alexei-led--k8s-mcp-server, alpacahq--alpaca-mcp-server, apollographql--apollo-mcp-server, awslabs--aws-api-mcp-server, awslabs--aws-documentation-mcp-server, organized by role with implementation paths as sub-sections.

## Server runtime

The language plus framework hosting the MCP protocol loop and tool dispatch. Choice constrains build tooling, async model, distribution channels, and which SDK idioms tools are written against.

### Python with FastMCP

High-level MCP framework that auto-derives tool schemas from Python type hints, leaving authors to write decorated functions instead of hand-registering handlers. Pairs naturally with `httpx` for async I/O and `pydantic` for schema. Appears in both pinned-major (`fastmcp>=2.0.0`) and newer-major (`fastmcp>=3.0.1`) variants; one server in the bin declares both `fastmcp` and the raw `mcp` SDK as dependencies, bridging two SDK generations within a single package. Appropriate when the tool catalog is hand-authored and the author wants minimal scaffolding around each tool function.

### Python with raw MCP SDK

Direct use of Anthropic's `mcp` Python SDK (`mcp` / `mcp[cli]`), without a framework layer above it. Tool handlers and schemas are hand-written rather than derived from signatures. Chosen when the server author wants explicit control over registration or wants to avoid an extra dependency layer; typically pairs with hand-rolled schema or `pydantic` models. Used both for vendor servers with large tool surfaces (60+ tools) and for narrow read-only servers, suggesting the choice is taste/control rather than scale-driven.

### TypeScript/Node with Anthropic MCP TypeScript SDK

Node-based runtime using Anthropic's TypeScript SDK; the SDK exposes both `StdioServerTransport` and `StreamableHTTPServerTransport` classes that the server instantiates based on a launch subcommand. Distributes naturally over npm/npx and benefits from Node's HTTP server ecosystem when running in HTTP mode. Appropriate when the target audience already has Node tooling and when an HTTP transport with browser-style concerns (CORS) is in scope.

### Rust crate

Cargo-managed Rust implementation of MCP, used here as a generic adapter that turns external schema (GraphQL operation definitions) into MCP tools at runtime. Distribution flows through crates.io, pre-built GitHub release binaries, and Docker images built from the binary. Appropriate when the server fronts a performance-sensitive upstream (here: the Apollo GraphQL ecosystem, which is itself Rust-forward) and when binary distribution is preferred over interpreter-based install.

## Transport

How the MCP wire protocol reaches clients. Constrains tenancy, auth, and where the server can run.

### stdio

Process-bound JSON-RPC over standard input/output; the host launches the server as a child process and communicates over its pipes. Implies a single-user session per process, no network exposure, and no auth layer of its own (trust derives from the host launching the binary). The dominant default across the bin — most servers ship stdio as the only or primary transport, with the host-config JSON snippet providing the launch command. Appropriate for desktop assistants (Claude Desktop, Cursor, VS Code) where the host owns the process lifecycle.

### Streamable HTTP

HTTP-based transport supporting streamed responses and stateful sessions. Requires the server to bind a port and brings HTTP-stack concerns into scope: CORS origin configuration, host/port env vars, and (where chosen) bearer-token or OAuth authentication on top. Selected via CLI flag, env var, or a positional subcommand at launch. Appropriate when the server must be reachable over the network, when multiple concurrent clients share an instance, or when the deployment is containerized behind a reverse proxy. Bin shows it offered as an alternative to stdio in the same binary, not as a replacement.

### SSE (deprecated)

Server-Sent Events transport — listed as supported-but-deprecated in one Kubernetes-tooling server, indicating an older HTTP-streaming convention being phased out in favor of streamable-HTTP. Maintained for backward compatibility with clients that haven't migrated.

## Capability surface

What the server exposes to the model — tools, resources, prompts, sampling, roots, logging — and how the catalog is shaped.

### Tools-only, hand-curated

A fixed list of tool functions authored directly in the server source. Counts vary widely: small read-only servers expose a handful (5-7), mid-size vendor servers expose dozens (60+) often grouped by domain (orders, positions, watchlists, etc.). Authoring effort scales linearly with tool count; the catalog is whatever the server compiles in. Default shape across the bin.

### Tools generated from external schema (operation-driven)

Tool catalog derived from configuration the operator provides at server start: a set of GraphQL operation definitions, each becoming an MCP tool. The server itself is a generic adapter — operators shape the catalog by choosing which operations to expose, without touching server code. Reduces tool authoring to operation authoring. Appropriate when there is a stable upstream schema (a GraphQL endpoint) that already encodes the surface.

### Resources + tools

Database-style server combining MCP "resources" (table listings, schema info, queryable as URIs) with tools (read-only SQL execution). Appropriate when the upstream domain has a natural URI/listing model (rows, schemas) distinct from imperative actions.

### Partition-scoped tool gating

Same server binary exposes a different tool set depending on a runtime-selected partition (here: AWS global vs China). Search/recommend tools surface in one partition; service-discovery tools surface in the other. Appropriate when the upstream backend itself differs by deployment region/cloud and a single binary should serve all.

### Read/write gating via flag or feature flag

Mutation-capable tools hidden by default; opt-in via a CLI flag (`--enable-write-tools`) or env-var feature flag for experimental tools. Reduces blast radius of an LLM accidentally invoking a destructive operation. Appropriate for any server fronting a system with destructive APIs (incident management, trading, infrastructure mutation).

### Capability-source patterns

The bin shows three distinct sources for the tool catalog: hand-coded functions, externally-supplied operation definitions (operator config), and OpenAPI/spec-derived generation (one trading server is a "rewrite built with FastMCP and OpenAPI"). The choice trades authoring effort against alignment with an upstream contract that may already exist.

## Configuration delivery

How the server learns its endpoints, credentials, modes, and feature flags at launch.

### Environment variables via host-config block

The MCP host's per-server JSON entry carries an `env` block that the host passes through to the spawned process. Used for API keys, region/profile, host overrides, mode toggles. Default delivery for stdio servers because the host already owns process spawn. Appropriate when secrets must not appear on the command line and when the host is the natural credential carrier.

### `.env` file at server working directory

A dotfile loaded by the server at startup (typically via `python-dotenv` or Node equivalents). Used for HTTP-mode servers where there is no host process to inject env, and for local development. Brings PORT, HOST, CORS_ORIGIN, NODE_ENV alongside upstream credentials.

### CLI flags at launch

Boolean toggles and mode selectors passed on the command line — `--enable-write-tools`, `--verbose`, transport-selection subcommand. Suited for operator-set posture (write-enable, verbosity) that should not be in client-controlled env.

### Config file referenced at startup

External configuration file (format typically YAML or TOML) pointed at the upstream endpoint, the operation definitions, and per-deployment options. Used by the operation-driven server where the catalog itself is configuration. Appropriate when the configuration shape is too rich for env vars and when ops teams already manage config files for the upstream system.

### Mounted credentials

Credentials delivered to a containerized server by host volume mounts — kubeconfig, cloud-provider credential files. Implies the container runtime is the integration point and that the operator manages credential rotation outside the MCP layer.

## Authentication

How the server verifies callers (when relevant) and how upstream credentials reach it.

### None — anonymous upstream

Server fronts a public, unauthenticated upstream (PubMed, AWS public docs); no credential surface at all. Appropriate when the upstream itself requires no auth and no rate-limiting per user is needed.

### Upstream API key/token in env

A single API key or token pair (e.g., PagerDuty user token, Alpaca key+secret, database credentials) delivered via env var. The server itself does not re-authenticate the MCP caller; trust derives from the transport (stdio) or surrounding network controls. Default for vendor-API servers.

### Cloud-provider credential chain

Server defers to the upstream SDK's standard credential resolution (AWS credential chain — env vars, `~/.aws/credentials`, instance profile). The server doesn't see the credentials directly; the upstream client library resolves them. Appropriate when the upstream has a well-established credential resolution convention.

### Mounted file credentials

Kubeconfig or cloud-provider credential files mounted into the container; the server reads them at startup. Same posture as the credential chain, but explicitly file-based and operator-controlled at deploy time.

### OAuth 2.x with issuer + JWKS (HTTP-mode only)

Optional bearer-token validation against a configured OAuth issuer and JWKS endpoint, available only on the streamable-HTTP transport. Adds genuine MCP-caller authentication on top of the transport. Configured via env vars naming the issuer and JWKS URLs. Appropriate when the server is exposed over a network and callers must be distinguished/authorized.

## Multi-tenancy

Whether one server process serves one or many users, and what enforces the boundary.

### Single-user per process

One credential set, one user context per running server. Default across the bin and made structurally inevitable by stdio transport (one process per host session). Some servers (the AWS API server) explicitly document the boundary in the README rather than leaving it implicit.

### HTTP-stateful, single-tenant

HTTP transport with stateful sessions, but still bound to one upstream credential set per server instance — sessions are MCP-protocol state, not tenant separation. Per-request tenant switching is explicitly out of scope.

### Stateless read-only (any number of instances)

No credentials, no per-user state — any number of instances can run concurrently because there is no shared mutable state. Applies to public-doc-fetching servers.

## Distribution channel

How end users obtain the server and stand it up.

### PyPI via `uvx` zero-install

Server published to PyPI; users invoke `uvx <package>@latest` and `uv` resolves, downloads, and runs in an ephemeral environment. Becomes the canonical install command in host-config snippets (`command: "uvx"`, `args: ["<package>@latest"]`). Appropriate for Python servers when the author wants the lightest possible user-side install.

### PyPI via `pip install` + console script

Traditional `pip install <package>` followed by invoking the console script registered in `[project.scripts]`. Coexists with the `uvx` path on the same PyPI release; chosen by users who prefer a managed venv over uv's ephemeral environments.

### npm package via `npx`

Node server published as a scoped npm package; users invoke `npx @scope/package` (optionally with a positional subcommand to pick transport). Same zero-install ergonomics as `uvx` for the Node ecosystem.

### Docker image

Pre-built container image as the canonical distribution. Variants in the bin: GitHub Container Registry (`ghcr.io/...`), AWS public ECR, Docker Hub, and "build locally from Dockerfile." Appropriate when the server has heavy or tricky native dependencies, when a single binary should serve multiple OSes, or when the deployment target is already containerized. Sometimes the README steers users to Docker first and treats pip/uvx as fallback.

### Source clone + bootstrap

`git clone` followed by `pip install -r requirements.txt`, `uv sync`, or `cargo build`. Used by servers without a published package and as the developer-mode path for all others. Implies the user accepts more setup overhead.

### Smithery

Third-party MCP-server install/launch tool driven by a `smithery.yaml` manifest at repo root. Lets users install a server without the upstream having to publish to PyPI or npm. Appropriate when the author wants discoverability without managing a package release pipeline.

### Pre-built binary release

Cross-compiled binaries attached to GitHub releases (used by the Rust server). Appropriate when the runtime has no interpreter on the user's machine and source build is impractical.

### Windows `.exe` variant

Explicit Windows entry via `uv tool run --from <pkg> <pkg>.exe`. Documents that the server is reachable from Windows host configs and not just Mac/Linux.

## Entry point

The concrete command users put in host configs and what the package exposes for invocation.

### Console script via `[project.scripts]` (Python)

A package-declared entry point in `pyproject.toml` mapping a script name to a `module:function` callable. Users invoke the script name directly and the package's main function runs. Default for PyPI-distributed Python servers.

### Module entry (`python -m <pkg>`)

Server is invoked by running the package as a module, dispatched via `__main__.py`. Used both as a primary entry and as a fallback alongside a console script.

### Bare script

A top-level `.py` file at repo root; users invoke `python <path-to-file>`. Common in repos that distribute by source clone rather than as a package; trades packaging effort for direct readability.

### npm bin via `npx`

Node package's `bin` field maps a command to a JS entry; `npx` resolves and runs it. Subcommand on the command line selects mode (HTTP default vs stdio).

### Container as entry

The Docker image's `ENTRYPOINT`/`CMD` is the entry; users put `docker run <image>` in their host-config command/args. Appropriate when Docker is the canonical distribution.

### Compiled binary

Pre-built binary from a release artifact; users run the binary path directly. Appropriate for Rust/Go-style compiled servers.

### Click-based CLI wrapper

Python `click` CLI as the entry point, dispatching to FastMCP's runner internally. Adds richer argument handling than calling FastMCP's runner directly — useful when the launch surface needs flag parsing, subcommands, or help text beyond what the framework provides.

## Build and packaging

How the source becomes a distributable artifact.

### Hatchling (Python)

PEP 517 build backend declared in `pyproject.toml`; produces wheel/sdist for PyPI. Used by both standalone and monorepo-sub-package layouts.

### Poetry (Python)

Poetry as build backend with `poetry.lock` for reproducibility; can coexist with `uv` workflow on the same `pyproject.toml`. One server in the bin supports both.

### `uv` for sync and lock

`uv sync` for reproducible dev environments and `uv.lock` for pinning. Often paired with hatchling-built packages.

### Cargo (Rust)

Standard Rust build via `Cargo.toml`/`Cargo.lock`; produces native binaries.

### npm/Node toolchain

`package.json` defines build and bin entries; npm registry is the publish target.

### Requirements-driven (legacy Python)

`requirements.txt` alongside or instead of `pyproject.toml`. Sometimes both coexist redundantly, suggesting the repo was bootstrapped from a requirements-first template before adding `pyproject.toml`.

## Python version pinning

How Python servers signal the required interpreter version to users and tools.

### `requires-python` in `pyproject.toml`

Declarative floor (`>=3.10`, `>=3.13`) read by pip/uv during install. Default among bin's Python servers.

### `.python-version` (pyenv-style)

Top-level dotfile read by pyenv and uv to select a local interpreter. Often paired with `requires-python` for redundancy.

### `.tool-versions` (asdf)

Multi-runtime version pin used by asdf. Rarer than pyenv-style; observed on a vendor-maintained Python server.

## Schema and types

How tool input/output schemas are produced.

### FastMCP auto-derivation from type hints

Tool function signatures (with type hints) become the MCP tool's input schema automatically; return types feed the output schema. Authoring effort is "write a typed Python function." Default when FastMCP is the runtime.

### Pydantic v2 models

Pydantic models for structured payloads, used both with raw `mcp` SDK (hand-registered) and alongside FastMCP for richer validation.

### Hand-authored schema (raw SDK)

When using the raw `mcp` SDK without FastMCP, tool handlers register an explicit input schema dict; the author writes the schema directly.

## Observability

How the server surfaces what it's doing for operators and debuggers.

### Standard library `logging`

Python's stdlib `logging` module, default handlers. Minimal but ubiquitous.

### `loguru` for structured logging

Replacement logging library favored for ergonomics and structured output. Appears on AWS-labs servers.

### `python-json-logger` alongside loguru

JSON-formatted log records via `python-json-logger`, used in concert with `loguru` — dual logging paths in one server, presumably one for human-readable dev output and one for ingest.

### `--verbose` flag

Boolean CLI flag escalating log verbosity at launch.

## Test stack

How the server's correctness is verified.

### pytest with async support

`pytest` plus `pytest-asyncio` for awaitable test functions; sometimes paired with `pytest-mock` and `pytest-cov`. Default for Python servers that run any tests at all.

### Live integration test gating

Custom pytest flag (`--run-live`) gates tests that hit real upstream services; default test runs stay offline. Lets the same suite serve both unit and live-integration roles without unconditional network calls.

### Branch coverage enforcement

`pytest --cov --cov-branch` for branch-level coverage measurement, beyond statement coverage.

### End-to-end protocol-conformance harness

Dedicated subdirectory (`/e2e/mcp-server-tester`) that exercises the MCP protocol surface end-to-end. Distinct from unit tests of business logic; tests that the server speaks MCP correctly.

### External agent validation artifacts

Test result files from validating the server against external agent platforms (Amazon Bedrock agents) committed to the repo as evidence of cross-platform compatibility.

### No tests

Some servers ship without a test suite; correctness verification is left to manual integration with a host. Common for hobbyist or single-author repos.

## CI

Automated build, test, and release infrastructure.

### GitHub Actions

The default across the bin. Used for unit tests on PRs, release-binary cross-compilation, container image builds, and PyPI/crates.io publishes. Workflows are split by concern (`ci.yml`, `release.yml`, `release-binaries.yml`, `release-container.yml`).

### Codecov integration

External coverage reporting service wired into the CI workflow.

### Monorepo CI inheritance

Sub-server packages in a monorepo inherit the parent's CI and don't ship their own workflows.

## Deployment artifact

What ops teams deploy when running the server in their environment.

### Dockerfile in repo

Source for an OCI image; either built locally by the user or built by CI and pushed to a registry. Appears in nearly every sample, even when not the primary distribution channel — Docker has become the lowest-common-denominator deployment shape.

### Published container image

Pre-built image at a known registry (ghcr.io, AWS public ECR, Docker Hub). Lets users skip the local build.

### docker-compose

`docker-compose.yml` alongside Dockerfile for multi-container local stacks (server + database). Used by HTTP-mode servers where ops want a one-command local environment.

### Podman alternative

Documentation acknowledging Podman as a Docker alternative for the same image. Reflects environments where rootless containers or Docker-Desktop-licensing concerns push users away from Docker.

## Host integration documentation

Per-host launch snippets the README provides so users can wire the server into their MCP client.

### Single-host snippet (Claude Desktop only)

README documents only `claude_desktop_config.json` for macOS/Windows, leaving other hosts to extrapolate.

### Cross-host coverage

README enumerates configs for multiple hosts (Claude Desktop, Cursor, VS Code, PyCharm, Gemini CLI). Vendor servers tend toward broader coverage.

### Host-agnostic snippet

README provides a generic `mcpServers` JSON entry without naming a specific host, presumed to be portable across MCP clients.

### Inspector compatibility called out

README notes compatibility with MCP Inspector (the protocol's reference debugger) as a separate item from any specific host integration.

### Monorepo catalog

Sub-server READMEs defer host-integration examples to the parent monorepo's catalog page.

## Repo layout

How the source is organized within its repository.

### `src/<pkg>/` package layout

Conventional Python `src` layout — package source under `src/`, tests beside it, packaging metadata at root. Default for Python servers expected to be installable.

### Bare-script layout

One or two `.py` files at repo root with `requirements.txt`/`pyproject.toml` beside them. Easy to read; awkward to package for PyPI.

### Single-package Node

`src/`, `package.json`, `tsconfig.json` at root.

### Single Rust crate

`Cargo.toml`, `src/main.rs`, with `/examples` and `/e2e` subdirectories for samples and conformance tests.

### Monorepo sub-package

`src/<sub-server>/` directory inside a parent multi-server monorepo, each sub-package with its own `pyproject.toml`, console script, and PyPI release. Consumers install one sub-server without pulling siblings.

## Capability-rights posture

Default safety stance for mutation-capable servers.

### Read-only by default, opt-in writes

Mutation tools registered but hidden behind a launch flag (`--enable-write-tools`). Author's default posture is "no surprise mutations."

### Sandbox-mode default

Server defaults to a sandbox/paper-trading mode (`ALPACA_PAPER_TRADE=true`); production mode is opt-in. Particularly relevant for finance/trading servers where misfires have monetary consequences.

### Anti-multi-tenancy disclaimer

README explicitly states "NOT designed for multi-tenant environments." Documents the boundary rather than letting users assume.

## Developer ergonomics

Tooling that supports contributors working on the server itself.

### Linter + type-checker stack

`ruff` + `mypy`/`pyright` wired in as dev dependencies and run in CI/pre-commit.

### `pre-commit` framework

Standardized hook orchestration for lint, format, and commit-message checks at commit time.

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
