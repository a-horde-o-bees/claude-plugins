# Sample

Pass-1 Phase-1a partial for bin 12. Functional decomposition of sooperset/mcp-atlassian, spences10/mcp-turso-cloud, stripe/agent-toolkit, supabase-community/supabase-mcp, teaguesterling/duckdb_mcp, the-momentum/fhir-mcp-server, thenets/ghost-mcp, tumf/grafana-loki-mcp, organized by role with implementation paths as sub-sections.

## Server runtime

How the server process is implemented — the language, framework layer, and runtime substrate that hosts MCP request/response handling.

### Python with FastMCP framework

FastMCP is a higher-level Python wrapper over the raw MCP SDK that auto-derives tool schemas from typed function signatures. Used by Python servers that want to skip the manual JSON-Schema and dispatcher plumbing the raw `mcp` SDK requires. Servers in this bin pin specific FastMCP 2.x versions (down to patch level in some cases) signaling caution about breaking changes in the framework's still-evolving 2.x line. FastMCP implies async tool handlers and a Pydantic-derived schema strategy. Compatible with stdio, HTTP, and SSE transports.

### Python with raw MCP SDK alongside FastMCP

A transitional pattern where the project depends on both `mcp` and `fastmcp` packages simultaneously — typically because the project predates FastMCP and migrated partially, or because some lower-level capabilities only exist in the raw SDK. Pins both with bounded version ranges to control compatibility. Adds maintenance overhead (two SDKs to track) but enables incremental migration.

### TypeScript / Node with MCP TypeScript SDK

Direct use of the official Model Context Protocol TypeScript SDK on Node.js. Common for ecosystems where users already have Node installed and `npx` enables zero-install execution. Integrates naturally with TypeScript-typed Supabase, libSQL, and similar JS-native client libraries.

### DuckDB extension (C++) embedding MCP

Native DuckDB extension built with CMake that exposes MCP via SQL PRAGMAs rather than running as a standalone process. The "server" is the user's DuckDB session; tool calls and configuration originate from SQL statements (`PRAGMA mcp_server_start(...)`, `PRAGMA mcp_publish_tool(...)`). Blurs the database/tool-registry boundary — SQL templates become first-class published tools. Constrains distribution to source-build with `make` since DuckDB community-extension packaging may not yet be available.

## Transport

How the MCP protocol bytes move between client and server.

### stdio

JSON-RPC over the process's stdin/stdout. The default for command-launched servers (npx, uvx, console script) and the only mode many clients support out-of-the-box. Implies single-tenant per-process and a launching host that owns the lifecycle. Often selected implicitly — README shows the launch command without naming the transport.

### HTTP (streaming)

A long-lived HTTP endpoint serving MCP request/response. Required for managed-cloud deployment where the client cannot launch the server locally; required for OAuth-style auth flows that need a browser; supports multi-tenant routing via URL path or query parameters. Endpoints are typically `/mcp` (and `/health` for liveness in some implementations).

### SSE (Server-Sent Events)

Server-push streaming over an HTTP connection — used as a transport flavor by FastMCP-based and SDK-based servers when they need server-initiated streaming without a full bidirectional websocket. Often offered alongside stdio with selection via CLI flag.

### MCP-client mode (server connects out)

Inverted role where the same artifact connects out to other MCP servers and exposes them through its own surface. Seen in the DuckDB extension where SQL `ATTACH` semantics let queries span multiple MCP-exposed data sources. Distinct from being a server — this turns the artifact into a federation point.

### Transport selection mechanism

Sub-decision orthogonal to which transports are supported.

#### Environment variable selection

A single env var (e.g., `TRANSPORT_MODE`) chooses among supported transports at process start. Container-friendly because env vars are the natural Docker/Kubernetes config surface; doesn't require shell-level argument forwarding through wrapper scripts.

#### CLI flag selection

A flag passed to the entry-point command (e.g., `-t sse`, `--http`) selects transport. Natural for local launch via `uvx`/`npx`; less ergonomic in containerized environments where flags must be wired through entrypoint scripts.

#### SQL PRAGMA selection

Server mode and transport parameters chosen from SQL inside an embedded extension. Specific to the in-database implementation path; the user issues `PRAGMA mcp_server_start(...)` with transport options as arguments.

#### Implicit / default-only

Server supports exactly one transport (typically stdio) and never names it in the README. Documentation is the launch command; transport is whatever that command produces.

## Authentication

How the server proves a caller's right to operate on the upstream resource.

### Static API token via environment variable

A long-lived secret (API key, personal access token, bearer token) provisioned upstream and passed to the server via env var. Simplest path; assumes the host is trusted to handle the secret. Common for stdio-launched servers where the host's MCP client config is the only place the token needs to live.

### OAuth 2.0 / 2.1 with browser consent

Browser-based authorization flow where each user authorizes the server to act on their account. Required when serving multiple tenants from one endpoint; requires HTTP transport so the browser callback can land. Token lifecycle managed by the MCP client/host. An early-adopter pattern signaling that the MCP auth story is maturing past static keys.

### OAuth 2.0 client-credentials

Server-to-server OAuth using a client ID + secret pair (no user browser flow). Used when the upstream is a backend service (e.g., FHIR server with client-credentials grant). Credentials live in env vars; the server exchanges them for access tokens internally.

### Server-managed token rotation

The server holds a long-lived secret (or root-credential pair) and mints short-lived child tokens transparently — JWTs that expire every few minutes with automatic renewal, or per-database tokens minted from an org-level token with configurable expiration and permission scope. Pushes auth lifecycle work into the server rather than the client/host. Useful when the upstream API enforces short-lived tokens (Ghost Admin API JWTs) or when child-token issuance is a security-isolation primitive (Turso per-database tokens).

### Bearer token via JSON config file

The server reads a bearer token from a configuration file (rather than env var or CLI flag). Used when the embedded-extension model means env vars are awkward to thread through the host process; JSON config is loaded by the server itself.

### Dual-API split credentials

Single server fronts two upstream APIs that have separate credential schemes (e.g., a read-only API with query-param key auth and a write API with JWT). Both credentials live in env vars; tools route to whichever API surface they belong to. Constrains tenancy because a user without one credential pair simply loses access to that group of tools.

### In-server encrypted credential vault

The server stores secondary credentials encrypted with a master key, enabling on-disk persistence of sensitive material rather than relying on env-var pass-through alone. Driven by regulated-domain requirements (PHI/HIPAA in healthcare); rare elsewhere.

### Credential-scoping guidance

Documentation pattern (not a mechanism) — vendor recommends a scoped/restricted credential variant (e.g., Stripe Restricted API Keys) over the full-power root key. Security-ergonomics layer on top of whichever auth mechanism the server uses.

## Configuration delivery

How the server learns its operational parameters (URLs, feature flags, scope) at launch or per-request.

### Environment variables

The dominant pattern. Host configures env vars in its MCP client JSON; server reads them at startup. Works for any transport but is especially natural for stdio (host already passes env when launching the subprocess). Variables typically name the upstream URL, credential, and optional behavior toggles.

### CLI flags

Arguments passed to the entry-point command (`--api-key`, `-u`, `-k`). Often offered alongside env vars as an alternative. Constrained by host wrapper config — some MCP clients pass `args` cleanly, others muddle quoting.

### URL query parameters

Configuration embedded in the HTTP endpoint URL (e.g., `?project_ref=...&read_only=true&features=database,docs`). Specific to HTTP-transport managed-cloud deployments; the same server process serves many tenants and per-request scope is part of the URL the client connects to. Unusual outside HTTP managed-MCP-as-a-service deployments.

### SQL PRAGMA parameters

Configuration values passed as named arguments to PRAGMA calls inside an embedded extension. The user, via SQL, configures the server at runtime rather than at process launch.

### JSON configuration file

A file the server reads at startup containing settings (HTTP/token configs, feature toggles). Often used in embedded-extension or container-deployment contexts where a mounted config volume is more convenient than env-var sprawl.

### Feature-group toggles

Sub-decision layered on top of any of the above mechanisms. The server exposes a single config field (`features=...`, `--tools=...`) that enables/disables groups of tools at startup. Reduces surface area for clients that don't need every capability and simplifies token/permission scoping. Some feature groups default off (e.g., storage tools) for conservative posture.

## Multi-tenancy

How the server handles multiple distinct upstream accounts/instances/users.

### Single-instance per process

One set of credentials and one upstream URL per process. The host launches a separate process for each instance the user wants to access. The default for stdio-launched servers; constrains concurrent multi-account use to host-level multiplexing.

### Per-request tenant scoping via URL parameters

HTTP server multiplexes tenants in a single process; each connection's URL query parameter (e.g., `project_ref`) plus the OAuth identity defines the tenant boundary for that session. Required for managed-cloud-as-a-service deployment where one endpoint serves all customers.

### Per-user OAuth identity

Each user's OAuth consent defines their tenant scope on a hosted endpoint. Combined with URL parameters or static account binding to determine the operational scope per session. The hosted variant of a server that also offers single-instance stdio for local self-host.

### Sub-tenancy via child-credential generation

Server holds an organization-level credential and generates per-resource child credentials with bounded scope and expiration (per-database tokens from an org token). Provides isolation within a single organizational tenant rather than across tenants.

## Capability surface

The categories of MCP primitives the server exposes (tools, resources, prompts, etc.) and how they're organized internally.

### Tools-only with feature grouping

Server exposes only MCP `tools` (no resources, prompts, sampling, or roots). Tool count ranges from a handful to dozens; large surfaces (50+) are typically organized into feature groups that can be toggled at config time. Grouping reflects upstream API divisions (Account, Database, Storage, etc.) so users can scope their deployment.

### Read/write tool split

Distinct tools (or distinct tool groups) for read vs. write operations against the same upstream — `execute_read_only_query` vs. `execute_query`, Content API (read) vs. Admin API (write). Supports different approval or sandboxing workflows at the MCP-client layer; lets users grant only the read surface when write isn't needed.

### Per-tool output format selection

Tools accept an output-format parameter (text/JSON/markdown/CSV) so the caller controls representation. Token-efficiency and rendering-quality knob; rare among MCP servers.

### User-publishable tools

Server provides a meta-tool that lets the user register new tools at runtime (e.g., `mcp_publish_tool` with a parameterized SQL template). Turns the server into a tool-registry rather than a fixed surface; specific to embedded-extension architectures where the substrate (DuckDB/SQL) makes parameterization safe.

### Vendor API surface coverage

Tools mirror the upstream vendor API's resource model (Jira issues + Confluence pages; Stripe payments + customers; FHIR Patient + Observation + Condition; Ghost posts + pages + tags). Surface size scales with how much of the upstream API the server tries to cover; full-coverage surfaces (70+ tools) are common for community-canonical servers fronting large SaaS APIs.

### Embedded RAG / retrieval pipeline

Server bundles an embedding model, vector store, document parser, and retrieval logic in-process (llama-index, sentence-transformers, pinecone, pymupdf). Tool calls run inference and similarity search inside the server rather than delegating to an external RAG service. Server-boundary-blurring; sharply increases the server's footprint and dependency surface but provides domain-aware retrieval for documents the upstream doesn't pre-index.

## Distribution

How the server reaches end users.

### PyPI with uvx execution

Python package published to PyPI with a console-script entry point; users run `uvx <package>` for zero-install execution (uv resolves and runs in an ephemeral venv). The dominant Python-server distribution path; works for any user who has `uv` installed.

### PyPI with pip install

Same package available for traditional `pip install`. Sometimes paired with `uvx` as alternative install commands; sometimes the only path.

### npm with npx execution

Node package on npm with a `bin` entry; users run `npx -y <package>` for zero-install execution. The TypeScript-server analog of `uvx`. Often the canonical distribution for TS servers; some monorepos publish multiple scoped packages for different surfaces (SDK, MCP entry, framework integration).

### Source build with make / CMake

Distribution requires `git clone` and a build step. Used when no package-registry path is established (DuckDB extension awaiting community-extensions inclusion) or when the project intentionally doesn't publish (compliance-sensitive servers expecting users to audit and build).

### Docker image

Container artifact (Dockerfile present, sometimes published to a registry, sometimes build-from-source). Used as a deployment artifact for users who prefer container deployment over language-runtime-direct execution; serves dual purposes when paired with docker-compose.

### Managed cloud endpoint

Vendor hosts the server at a fixed HTTPS URL; users configure their MCP client to point at that URL with no install step. Requires HTTP transport; pairs naturally with OAuth. Distribution-as-a-service stance from vendors with existing SaaS infrastructure.

### Vendor-bundled (e.g., CLI subcommand)

Server ships inside another tool the user already has installed (Supabase CLI exposes a local MCP endpoint when `supabase start` runs). Distribution piggybacks on existing tool adoption.

### Multi-channel publication

Same server published through several channels simultaneously (PyPI + Docker + source; npm + managed endpoint + self-host package). Different user segments have different preferences; multi-channel publication maximizes reach but multiplies maintenance.

### Cross-ecosystem packaging

Single repository publishes the same conceptual artifact to multiple language ecosystems (PyPI + npm) with parallel naming conventions (`stripe-agent-toolkit` vs. `@stripe/agent-toolkit`). Enables both Python and TypeScript consumers from one source of truth; doubles publication and version-coordination work.

## Entry point

The exact command users (or their hosts) invoke to start the server.

### uvx <package>

Bare `uvx <pypi-package>` invocation. Console script declared in `[project.scripts]`; uvx fetches and runs in an ephemeral venv. The cleanest stdio launcher for Python servers.

### npx -y <package>

Bare `npx -y <package>` for Node servers. The `-y` accepts the install prompt automatically. Often passes `--api-key=...` or other CLI flags inline.

### Console script with required flags

Same pattern as the bare-launch forms but with required CLI arguments (`grafana-loki-mcp -u ... -k ...`). Host wrapper config must be careful with quoting.

### Make targets in repo

Local-dev launch via `make run`, `make dev`, `make build`, etc. Common in projects with substantial dev tooling; not the end-user launch path but the developer-iteration path.

### Docker / docker-compose run

Launch via `docker run` or `docker-compose up`. Used when the server has runtime dependencies that are easier to package as a container than to install host-side; sometimes the only documented launch path for compliance-sensitive servers.

### URL configuration (no launch)

For managed-endpoint deployments, the user's MCP client points at an HTTPS URL — no local launch step. The "entry point" is the URL itself.

### SQL PRAGMA invocation

User starts the server from inside a DuckDB session via `PRAGMA mcp_server_start()`. The host process is the DuckDB CLI/library; the MCP server is a behavior toggled within it.

## Test stack

What the project uses to verify itself, and where the tests live.

### pytest with async plugin(s)

Python servers using `pytest` plus `pytest-asyncio` and/or `pytest-anyio` for async test support. Coverage reporting via `pytest-cov` is common. Some projects layer custom markers to separate test scopes (e.g., `integration`, `dc_e2e`, `cloud_e2e` distinguishing on-prem vs. cloud deployment-mode tests).

### make test targets

Test invocation wrapped in a Makefile target — typically `make test`, sometimes also `make test-connection` for upstream-reachability smoke tests. Layered over whichever underlying framework runs the tests.

### Docker-Compose backend for end-to-end tests

Repo ships a `docker-compose.yml` that brings up the upstream service (Ghost+MySQL, etc.) for local end-to-end testing — not for deploying the MCP server itself, but as the substrate the test suite hits. Notable infrastructure investment for an MCP repo; more common in integration-test frameworks.

### Linter/formatter test gate

Project relies on lint/format/type-check tooling (`ruff`, `black`, `mypy`, `ty`, `biome`) as part of the CI gate; pre-commit hooks enforce locally. Some projects run both `ruff` and `black` (redundant since modern `ruff format` covers most of what `black` did).

### Native build-system test target

Tests run via the native build system's test target (`make test` invoking CMake/CTest for the C++ extension).

### Undocumented / not surfaced

README and visible artifacts don't establish a test framework — common for low-star early projects.

## CI

What automation runs on each commit/PR.

### GitHub Actions

The dominant CI substrate across the bin. Workflows live in `.github/workflows/`; specific job content varies (test, lint, build, publish). Some projects pair Actions with `pre-commit` hooks for local mirror-checking of CI rules.

### Pre-commit hooks

Configured locally via `.pre-commit-config.yaml`; runs lint/format checks before commit. Often overlaps with CI's lint stage.

### Renovate / Changeset tooling

Sub-tools for dependency automation (`renovate.json`) and changelog management (`.changeset/`). Common in TypeScript Node projects.

## Container artifacts

Container-format outputs the project ships or uses internally.

### Dockerfile for runtime image

Single Dockerfile producing a runnable image of the MCP server. Used as a deployment artifact for users who prefer container execution over language-runtime-direct launch.

### Docker Compose for upstream test stack

Compose file bringing up the upstream backend (database, CMS, etc.) so tests can hit a local instance. Not for deploying the MCP server itself.

### Makefile-driven Docker build

`make build` invokes Docker build under the hood. Combines container packaging with the project's broader make-target workflow.

### No container artifacts

Project ships only language-package or source distribution; users who want containerization build their own image.

## Host integration

Specific MCP-client hosts the project documents support for, and the wrapper artifacts shipped to enable that support.

### MCP-client JSON config snippet (Claude Desktop, Cursor, Cline, Windsurf)

README documents the JSON snippet a user pastes into their host's MCP config — `command`, `args`, `env`. Hosts named typically include Claude Desktop, Cursor, Cline, Windsurf. The lowest-effort host integration: same snippet works across hosts because they share the launcher config schema.

### `.claude-plugin/` directory in repo

Project ships a Claude-Code plugin wrapper directory at the repo root, encoding the plugin manifest alongside the code. Distinct from JSON-snippet host config — this packages the project as a discoverable Claude Code plugin.

### `.cursor-plugin/` directory in repo

Cursor-specific plugin wrapper shipped alongside `.claude-plugin/` — recognizing host-specific plugin formats as distinct distribution surfaces.

### `.mcp.json` in project root

A project-local MCP-config file convention (used by Claude Desktop and similar hosts that read `.mcp.json` to discover MCP servers tied to a specific project workspace).

### Vercel AI SDK native integration

Server exports a `createToolSchemas()` (or equivalent) function that lets a Vercel-AI-SDK-based app consume the same tool schemas without going through MCP transport — first-class non-Claude integration. Doubles the project as both an MCP server and an SDK.

### WSL configuration guidance

Documentation specifically addressing Windows users running the host through WSL — environment-bridging concern that some servers call out explicitly.

## Documentation surface

User-facing documentation artifacts beyond the README.

### llms.txt for AI-consumption docs

A `llms.txt` file providing a flattened, AI-friendly view of the project for agents that consume it. Pattern emerging in projects whose primary readership includes other LLM agents.

### ReadTheDocs / hosted docs site

External documentation hosted on ReadTheDocs or a similar service. Common for projects with substantial reference material beyond the README.

### Examples directory

`/examples` directory with ready-to-use config files and demonstration scripts. Often paired with the documented entry-point command — users can copy an example and adapt it.

### Devcontainer / mise / dev-environment manifests

`.devcontainer/`, `mise.toml`, or similar manifests that pin the developer's tool versions. Lowers the barrier to first-contribution by automating environment setup.

### Security audit docs

Separate documents recording security review of the project. Distinct from auth documentation; reflects deliberate compliance posture.

## Repo layout

The project's top-level structure as it relates to publishing and consumption.

### Single-package

One package, one published artifact, one entry point. The default for a server that only does one thing.

### Monorepo with multiple published packages

Multiple publishable packages coexist in one repo (`@scope/sdk`, `@scope/mcp`, `@scope/integration`, etc.). Used when the project is "MCP plus other agent-integration surfaces" and treats MCP as a peer to SDKs and framework adapters. Often pnpm-workspace or similar workspace tooling.

### Single-package with `.changeset/`

Single-package layout but with formal changeset-based release management (common in TS Node projects).

### Single-package with embedded test substrate

Single-package layout that also bundles a docker-compose stack for end-to-end testing of upstream services.

## Packaging (Python)

Python build-backend and dependency-management choices.

### hatchling backend with uv

`hatchling.build` as the wheel/sdist builder, `uv` as the dependency manager (lock file `uv.lock`). The mainstream modern Python packaging path for new projects.

### uv_build backend

`uv_build` as the build backend — uv's own native backend, less common than hatchling. Sometimes paired with non-standard module-name conventions (e.g., `module-name = "app"`). Signals adoption of uv's full toolchain rather than just its venv/lock features.

### setuptools / setup.py legacy

A `setup.py` shipped alongside `pyproject.toml` for backward compatibility; pip-compatible install path remains the primary expectation.

## Notable / unanticipated axes

Patterns observed in this bin that don't fit cleanly into any single role above and may surface as new roles after merge.

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
