# Sample

Pass-1 Phase-1a partial for bin 10. Functional decomposition of paypal--paypal-mcp-server, ppl-ai--modelcontextprotocol, pragmar--mcp-server-webcrawl, qdrant--mcp-server-qdrant, redis--mcp-redis, reminia--zendesk-mcp-server, riza-io--riza-mcp, rohitg00--kubectl-mcp-server, organized by role with implementation paths as sub-sections.

## Server runtime

The host process that loads the MCP protocol implementation, registers handlers, and serves requests. The runtime choice constrains language-ecosystem decisions downstream — packaging, async model, type-schema strategy, dependency surface.

### Python with FastMCP

A Python server built on the FastMCP framework (typically the 2.x line). FastMCP provides decorator-based tool registration, automatic schema derivation from Python type hints (via Pydantic), built-in transport selection plumbing for stdio/SSE/streamable-http, and standard logging configuration via env vars. Authors choose this when they want minimal boilerplate, type-driven schemas, and out-of-the-box multi-transport support. Often pinned tightly (e.g., `fastmcp == 2.7.0`) to track API drift in the framework. Implies async tool handlers by default and pulls Pydantic 2 as a transitive runtime dependency. Appropriate when the server's tool surface maps cleanly to typed Python functions and the author wants transport/observability concerns handled by the framework.

### Python with raw mcp SDK

A Python server built directly against the `mcp` package (sometimes `mcp[cli]`) without FastMCP. The author handles tool registration, schema authoring (typically by hand as JSON Schema dicts), and transport wiring at the lower-level Server API. Chosen when the project predates FastMCP, when authors need finer control over the server lifecycle, when they want to minimize the dependency surface, or when they prefer to ship hand-tuned schemas rather than auto-derived ones. Tool handlers are typically `async def` since the low-level SDK is async-native, but sync handlers also occur when the underlying client library is sync (e.g., when wrapping a sync third-party SaaS SDK). Often paired with hand-authored mypy/typing discipline rather than schema-from-types.

### Node.js with MCP TypeScript SDK

A Node-runtime server built on Anthropic's MCP TypeScript SDK. Implementation is typically TypeScript (compiled to JS for distribution) or mixed JS/TS. Chosen when the upstream API client (the SaaS SDK or proprietary library being wrapped) is JS-native, when distribution needs to land in npm-only host environments without requiring users to install Python tooling, or when the author's existing codebase is JS. Pulls in npm as the distribution channel by default and aligns with `npx` as the launch idiom. Server runtime requires Node 18+ as a typical floor.

## Transport

The wire protocol the server listens on for MCP frames. Transport choice constrains tenancy, deployment shape, and authentication options — stdio is single-process per client and uses host-managed credentials; HTTP-class transports support shared deployments and standalone authentication.

### stdio

JSON-RPC frames over stdin/stdout. Default for nearly every sample because Claude Desktop, Cursor, and other host integrations launch the server as a subprocess and communicate over its pipes. Implies one server process per host connection, single-tenancy per process, and credentials sourced from the host launcher's environment (not from the MCP request). Always present in the corpus as either the only transport or the default among multiple.

### Streamable HTTP

HTTP transport with streaming response support, the modern HTTP-class option in the MCP spec. Selected via env var or CLI flag; binds host/port (typical default `0.0.0.0:8000`). Enables shared-server deployments where multiple clients connect to one process and per-request authentication is meaningful. Often advertised as "coming soon" in samples that currently ship stdio-only, indicating it is the next-step expansion path most authors anticipate.

### SSE

HTTP server-sent events transport. Co-exists with streamable-http in samples that support multiple HTTP-class transports; chosen by users on hosts that prefer SSE compatibility. Same shared-deployment posture as streamable-http.

### HTTP mode with CORS

HTTP transport with CORS configuration, enabling browser-based or cross-origin shared deployments. `PORT` and `BIND_ADDRESS` env vars configure binding. Chosen when the server is expected to back a hosted multi-tenant service or when browser clients need direct access. Carries the same per-request authentication implications as other HTTP-class transports.

## Capability surface

The MCP primitives the server exposes — tools, resources, prompts — and how they're partitioned. Choice of primitive shapes how callers discover and invoke functionality.

### Tools-only

The server exposes only the `tools` primitive — every operation is a tool call, including read operations. Most common pattern in the corpus. Appropriate when all operations have clear input parameters and the agent should explicitly invoke each one. Tool counts in the corpus range from a handful (4-6) for vendor servers with product-tier tool boundaries up to 250+ for surface-area-maximizing wrappers around large APIs (e.g., a kubectl wrapper).

### Tools + resources

The server exposes both `tools` (for actions and queries with parameters) and `resources` (for read-oriented content addressable by URI, e.g., `zendesk://knowledge-base`). Splits read access from write/action access along MCP primitive lines. Chosen when there's a clear addressable content surface (a knowledge base, a document collection) that benefits from URI semantics and resource-list discovery rather than tool-call ceremony. Less common — most servers use tools for everything.

### Tools + prompt routines (out-of-band)

The server ships pre-authored Markdown prompt files alongside the tool surface, distributed as plain content (e.g., a `prompts/` directory) rather than via the MCP `prompts` primitive. Encodes "how to use this server for task X" as reusable templates the user manually loads. Chosen when the author wants to package guided workflows but doesn't need the protocol-level prompts primitive. Appropriate for servers whose tools combine into well-understood multi-step tasks (SEO audits, 404 detection, performance analysis).

### Tools + resources + prompts + UI dashboards

Maximal MCP surface — tools, resources, prompts via protocol primitives, plus optional GUI dashboards bundled as an install extra. Chosen by surface-maximizing wrappers around very large APIs where every primitive has clear use. Implies an opt-in install extra (e.g., `[ui]`) for the dashboard component so users who only need protocol surface can avoid heavy dependencies.

## Capability scoping

How the server lets callers narrow the active capability surface at launch time. Distinct from capability-surface choice itself: scoping is about which subset of capabilities is loaded.

### Modular tool selection flag

A CLI flag (e.g., `--tools=all` with named subset support) lets the user opt into specific tool categories rather than exposing the full surface. Reduces prompt-window noise for users who only need one sub-domain (e.g., invoicing but not subscriptions). Appropriate when the server has a large categorized tool surface (30+ tools across functional families).

### Destructive-action gating flag

A CLI flag (e.g., `--disable-destructive`) suppresses tools that mutate or destroy state, leaving read-only tools active. Safety knob for environments where the agent should observe but not change. Appropriate when the server's tool surface contains a clear destructive subset (kubectl delete, scale-down operations).

### Optional install extras for feature bundles

Install-extras gate optional feature bundles at install time (e.g., `pip install <pkg>[ui]` adds dashboard dependencies; a separate env-var toggle enables browser-automation tools). Chosen to keep the base install lean while letting power users opt into heavier feature sets. Appropriate when feature bundles have heavy transitive dependencies that most users don't need.

## Configuration delivery

How the server receives runtime configuration — credentials, endpoints, behavior toggles. Often combines multiple sources with documented precedence.

### Environment variables

Configuration via process environment, sometimes loaded from a `.env` file via `python-dotenv` or equivalent. Universal fallback in the corpus and typically the primary surface for credentials. Appropriate for credentials that should never appear in process listings or shell history. Often layered with proxy-hierarchy rules — a tool-specific proxy env var takes priority over standard `HTTPS_PROXY`/`HTTP_PROXY` for corporate/enterprise environments.

### CLI flags

Configuration via command-line arguments to the entry-point binary. Often the primary surface for connection parameters (URL, host, port, SSL paths) when the author wants explicit, inspectable config. Some servers position CLI as primary with env-var fallback; others deprecate CLI in favor of env-only. Appropriate when the host launcher is constructing the command anyway and visibility of the parameters is preferred over hidden env state.

### URI scheme

A single connection URI (e.g., `redis://`, `rediss://`) packs host, port, credentials, and TLS selection into one string. Often accepted alongside discrete CLI flags as a convenience. Appropriate for connection-oriented services where URI is the standard idiom of the underlying client library.

### JSON configuration file (host-managed)

Configuration delivered via the host's config file (e.g., Claude Desktop's `claude_desktop_config.json`), where the host inserts an `mcpServers` entry naming the server's command, args, and environment. Universal in the corpus as the user-facing entry point even when the server itself reads env vars or flags — the host config translates user setup into the actual launch command.

### `.env` file

A local `.env` file is read at startup via `python-dotenv` or equivalent. Often paired with a tracked `.env.example` template that lists required keys without values. Appropriate for self-hosted developer-mode deployments where the user clones the repo and configures locally rather than installing from a registry.

## Authentication

How the server proves identity to the upstream service it wraps, or (rarely) to its own MCP callers.

### OAuth 2.0 client credentials

OAuth flow producing a bearer token with a documented lifetime (e.g., 3-8 hours). Token may be supplied externally (env var or CLI flag) or generated by the server from client ID/secret. Single-merchant or single-tenant scope per process. Carries token-refresh concerns for long-lived sessions; whether refresh is handled in-server or delegated to the caller varies. Appropriate when the upstream service requires OAuth and the deployment is single-tenant.

### OAuth 2.1 (RFC 9728) bolt-on

Optional OAuth 2.1 layer protecting the MCP server itself (not the upstream). Configured via env vars (`MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE`, JWKS endpoint). Layered on top of any transport — adds authentication to HTTP-class deployments primarily. Appropriate for hosted MCP deployments where multiple clients share a server and per-client identity matters.

### Static API key

Single API key supplied via environment variable. Process-scoped to one account; per-request tenancy is at the upstream account level. Most common and lowest-ceremony auth pattern in the corpus. Appropriate when the upstream service uses bearer tokens and the deployment is single-user.

### Cloud-native identity (Azure EntraID)

Azure-specific auth path with multiple sub-flows — service principal, managed identity, default Azure credential. Includes automatic token renewal with background refresh. Co-exists with standard auth (e.g., username/password ACL) as an alternative path. Appropriate when the deployment is on Azure infrastructure and managed identity eliminates the credential-rotation problem.

### Service-specific credentials via third-party SDK

Credentials handed to a community Python SDK (e.g., `zenpy` for Zendesk) that handles the upstream auth flow internally — API token, username/password, or whatever the SDK supports. The MCP server is a thin layer; the SDK owns the credential model. Appropriate when a mature community SDK already exists and re-implementing its auth would duplicate effort.

### Host-managed kubeconfig

Authentication delegated to a standard config file the host environment already manages (`~/.kube/config` for kubectl-class servers). The server reads the file, no in-MCP credential delivery. Appropriate when the wrapped tool already has a well-established local credential file and users have configured it for other purposes.

### None (local-only operation)

No authentication because the server doesn't talk to a remote service — it operates on local files or archives. Appropriate when the server's role is to expose existing local data (crawler archives, local databases, on-disk indexes). Demonstrates that valid MCP servers need not require credentials at all.

## Multi-tenancy model

Whether one server process can serve multiple distinct upstream accounts or only one.

### Single-user / single-tenant per process

The server is bound at launch to one upstream account, one connection, or one merchant. Per-request tenancy is whatever the upstream account naturally supports. Universal in the corpus. Implied by stdio transport (one process per host connection) and by env-var-sourced credentials (process-scoped). Multiple tenants require multiple server processes.

## Distribution channel

How the server's executable artifact reaches end users.

### npm registry with npx execution

Published as an npm package consumable via `npx -y <package>`. The user never explicitly installs; npx fetches and runs in one step. Standard idiom for Node-runtime servers and the path of least resistance for hosts that already integrate with the npm ecosystem. Appropriate when the runtime is Node and the target audience includes npm-native tooling environments.

### PyPI with uvx execution

Published as a PyPI package consumable via `uvx <package>` or `uvx --from <package>@latest <command>`. Similar one-step idiom to npx — uvx fetches into an ephemeral venv and runs. The `--from` form lets the package name differ from the console script name. Appropriate for Python servers targeting users who have `uv` installed (increasingly common as uv adoption grows).

### PyPI with pip install

Published as a PyPI package installed via `pip install <package>` into the user's environment, then run via the installed console script. Older idiom than uvx; positioned for users on plain Python rather than uv. Appropriate when the author wants broad compatibility and isn't requiring users to adopt uv.

### Editable install from source

No registry publication — users clone the repo and run `uv venv && uv pip install -e .` (or pip equivalent). The "developer-mode-as-release" pattern. Appropriate when the project is early-stage, when the author wants to require git-clone (so users get the README, examples, and `.env.example` template), or when releasing to a registry isn't yet justified.

### Docker image

Published or build-from-source Docker image. May be published to Docker Hub or shipped as a Dockerfile only. Appropriate when the deployment target is containerized infrastructure, when the dependency stack is heavy enough that image isolation pays off, or when the server is one component of a larger compose/k8s deployment.

### Smithery one-click

Published to Smithery for one-click installation into supported hosts (primarily Claude Desktop). Layers on top of an underlying registry (PyPI/npm) — Smithery generates the host config and triggers install. Appropriate when the author wants to maximize installation ease for non-technical users.

### Git source via uvx

Installation directly from a git URL via `uvx --from git+https://...`. Combines source-install ergonomics with uvx's ephemeral-venv execution. Appropriate for pre-release, fork-tracking, or when the user wants a specific commit without registry intermediation.

### GitHub releases

Tagged GitHub releases as a distribution surface, often alongside registry publication. Appropriate for binary attachments, signed checksums, or when the release artifact differs from the registry artifact.

## Entry point / launch

The actual command users or hosts invoke to start the server, after distribution has placed the artifact.

### npx package invocation

`npx -y <@org/package>` form, often with flags appended. The npm `bin` entry maps the package to a launchable command. Universal launch idiom for npm-distributed servers. The host's JSON config typically lists `npx` as the command and the package name (with `-y` for auto-confirm) as the first arg.

### Console script (PyPI-installed)

A `[project.scripts]` entry defines a console script (e.g., `mcp-server-qdrant`) that the user invokes after install. Standard Python idiom. Host config lists the script name as the command directly when installed system-wide, or under `uvx` when using ephemeral install.

### `uv --directory` from source

`uv --directory /abs/path run <script>` invokes a console script from a source checkout, with uv resolving the venv and dependencies. Appropriate for editable-install distributions where the user has cloned but not published. Host config encodes the absolute path to the checkout.

### Docker container entrypoint

The Docker image's `ENTRYPOINT` or `CMD` runs the server. Host config maps `docker run` (or compose) to the MCP launch command. Appropriate when the user has standardized on container-based tool isolation.

## Server-side capability scoping signals

Not a primary role; cross-references the capability-scoping section. Servers expose surface-area knobs differently:

- A `--tools=<subset>` flag for opt-in capability loading
- A `--disable-destructive` flag for safety gating
- An install extra (`[ui]`) for optional feature bundles
- An env-var toggle (e.g., `MCP_BROWSER_ENABLED`) for runtime feature gating

## Observability

How the server reports its own behavior — logs, metrics, debug surfaces.

### Env-var-controlled log level

A single env var (e.g., `PERPLEXITY_LOG_LEVEL`, `MCP_REDIS_LOG_LEVEL`) sets log severity at startup, with standard Python/Node logging defaults for destination and format. Most common observability surface in the corpus. Appropriate for stdio servers where logs go to stderr and the host displays them.

### Debug toggle + log file path

Pair of env vars — a boolean debug flag (`MCP_DEBUG`) plus a log file destination (`MCP_LOG_FILE`). Separates "verbose mode" from "where the verbose output goes." Appropriate when the server runs detached from an interactive host and logs need to land somewhere persistent.

### `--interactive` REPL mode

A CLI flag that drops the server into a terminal REPL for direct query inspection, doubling as a debug surface. Unusual — most servers assume MCP Inspector is the only interactive debugging path. Appropriate when the server's domain (e.g., crawler-archive search) benefits from quick local exploration before MCP integration.

## Test stack

How the server's deterministic logic is verified.

### pytest with pytest-asyncio

Python servers using pytest as the runner with pytest-asyncio (often `asyncio_mode = "auto"`) for async tool handlers. Frequently paired with pytest-cov and a coverage gate (e.g., `--cov-fail-under=80` in `addopts`). May include in-memory backends as fixtures (e.g., in-memory Qdrant client) to avoid external service dependencies during test. Standard choice for FastMCP-based and async-native raw-mcp servers.

### Jest

Node servers using Jest. Standard JS choice. Configuration may be present without specific test-layout details extracted.

### vitest

Node servers using vitest as the runner. Faster modern alternative to Jest in TypeScript projects. Configuration may be present without specific test-layout details extracted.

## CI

Automated build/test/release pipelines.

### GitHub Actions

Universal CI choice in the corpus. Workflow specifics vary — typically lint/type-check/test plus release publishing. Often paired with codecov integration for coverage reporting and badges in README.

## Container artifact

When the project ships a containerized deployment artifact.

### Dockerfile (build-from-source)

A `Dockerfile` in the repo root for users to build locally. Often installs from a lock file (`uv.lock`, `requirements.lock`) for reproducibility rather than from `pyproject.toml` resolution. Appropriate when the author wants to provide a containerization recipe without operating a registry.

### Published Docker Hub image

Pre-built image published to Docker Hub (e.g., `<author>/<image>:latest`). Removes the build step for end users. Appropriate when the project has an audience large enough to justify image hosting and the author can manage the publish pipeline.

## Repo layout

Filesystem organization of the project.

### Single-package

One package, `src/<name>/` or `<name>/` at repo root, with `pyproject.toml` (or `package.json`), `tests/`, possibly `examples/`, possibly `Dockerfile`. Universal in the corpus — no monorepos surfaced in this bin. Appropriate when the project ships exactly one server and doesn't need workspace management.

### Single-package with dual-ecosystem wrapper

Python package as the canonical implementation with a thin npm wrapper that invokes the Python entry point under the hood. Two `package.json` / `pyproject.toml` roots in the same repo. Appropriate when the author wants to reach both ecosystems' install habits without maintaining two separate codebases.

## Host integration

The set of MCP-capable host applications the server documents support for, typically via JSON config snippets.

### Claude Desktop

Universal in the corpus — every sample documents Claude Desktop integration. The host's `claude_desktop_config.json` `mcpServers` entry is the canonical onboarding artifact and often the only example shown.

### Cursor

Common second-tier integration. Same JSON `mcpServers` shape as Claude Desktop in most cases. Sometimes documented via "quick-install badge" links that auto-configure.

### VS Code with GitHub Copilot

Documented integration path, typically requiring a VS Code setting (`chat.agent.enabled: true`) to be enabled. Same JSON config shape.

### Windsurf, Kiro, Cline, Augment

Additional supported hosts surfaced via quick-install badges or short documentation snippets. The corpus shows broad host-list expansion as a documentation pattern — author lists every host with a known integration path even when the config shape is identical.

### OpenAI Agents SDK

Documented support as a non-MCP-host MCP-consuming runtime. Indicates the author is positioning the server as ecosystem-agnostic rather than Claude-specific.

## Python build backend

For Python servers, the PEP 517 build backend that produces the wheel.

### hatchling

Modern Python build backend, the dominant choice in the corpus. Pairs naturally with uv-based development workflows. Appropriate as the default modern choice when there's no specific reason to deviate.

### setuptools (with `setup.py` or `setup.cfg`)

Older convention, still appropriate for long-lived projects predating hatchling or for projects needing setuptools-specific features. Sometimes via `setup.py` directly, sometimes via `setuptools.build_meta` declared in `pyproject.toml`. Appropriate when the project predates the modern hatchling default or has setuptools-specific build steps.

### uv_build

Uv's native build backend, declared via `requires = ["uv_build>=0.8.3,<0.12.0"]` in `pyproject.toml`. Rare in the corpus — adoption is limited even among uv-first projects. Appropriate for projects that want maximal uv integration and are willing to track a newer backend.

## Lock file convention

Whether and how the project pins its dependency tree.

### `uv.lock`

Committed `uv.lock` produced by uv. Pairs with `uv` as the version manager and uv_build or hatchling backends. Appropriate when the project is uv-first and reproducibility across developer/CI/Docker environments matters.

### `requirements.lock`

A pip-style lock file (often hand-maintained or via pip-tools), used as the install contract inside Dockerfiles for reproducible image builds. Appropriate when the project ships a Docker image and wants build-time pinning independent of runtime install resolution.

### No lock file

Plain `pyproject.toml` with version ranges, no lock committed. Appropriate for libraries (where range flexibility helps consumers) but unusual for end-user-installable servers. Typically signals minimal-packaging posture or older project conventions.

## Cross-role tools

Tools that surface under multiple roles in this bin:

- **Docker** — fills *Container artifact* (Dockerfile / Docker Hub image), *Distribution channel* (Docker as install path), and *Test stack* (in-image build verification via lock file)
- **uv** — fills *Distribution channel* (uvx execution), *Entry point* (`uv --directory run`), *Lock file convention* (uv.lock), and *Python build backend* (uv_build)
- **`.env` file** — fills *Configuration delivery* (runtime config) and *Example client / developer ergonomics* (`.env.example` template)
- **GitHub Actions** — fills *CI* and *Distribution channel* (release publishing)
- **JSON `mcpServers` config** — fills *Configuration delivery* (host-side) and *Host integration* (the per-host onboarding artifact)
