# Sample

Pass-1 Phase-1a partial for bin 9. Functional decomposition of mongodb-js/mongodb-mcp-server, motherduckdb/mcp-server-motherduck, mukul975/cve-mcp-server, neondatabase/mcp-server-neon, normaltusker/kotlin-mcp-server, openags/paper-search-mcp, opensearch-project/opensearch-mcp-server-py, pathintegral-institute/mcp.science, organized by role with implementation paths as sub-sections.

## Server runtime

The language and SDK that hosts the MCP protocol loop and dispatches tool calls. Determines async model, type-derivation strategy, and which transport adapters are available out of the box.

### TypeScript with Anthropic MCP SDK

Node-based runtime built on the official Anthropic MCP TypeScript SDK. Uses Node's event loop for concurrency and a Node-resolved module ecosystem; the SDK supplies transport adapters and protocol framing. Appropriate when the upstream domain (database driver, hosting framework) already has a mature TypeScript client and the team wants single-language control across runtime, schema, and tests. Imposes a Node version floor (typically 18+ or 20+) and pulls in TypeScript build tooling.

### Python with FastMCP

Python runtime where FastMCP wraps the raw MCP SDK and auto-derives tool schemas from type hints + docstrings. Author writes `@mcp.tool()`-decorated functions; FastMCP handles JSON-Schema generation, marshalling, and the protocol loop. Appropriate when domain SDKs are Python-first (data science, security tooling, scientific computing) and the author wants minimal boilerplate per tool. Tight version pinning (e.g., `>=2.14,<3`) is common to bound breaking-change exposure as FastMCP is a fast-moving wrapper.

### Python with raw MCP SDK

Python runtime that imports `mcp` directly (no FastMCP wrapper). Author hand-authors schemas or uses Pydantic models passed to lower-level decorators. Appropriate when the project predates FastMCP, when fine control over protocol surface is required, or when project governance prefers minimal dependency stacks. More boilerplate per tool but no third-party wrapper drift.

### Python with both MCP SDK and FastMCP declared

Hybrid path where `pyproject.toml` lists both `mcp` (or `mcp[cli]`) and `fastmcp` as dependencies. Typically FastMCP runs the server surface while `mcp[cli]` provides developer tooling (Inspector launcher, schema dump utilities), or transitional state during a migration. Appropriate when devs want both the auto-schema ergonomics of FastMCP and the official CLI tooling. Carries dual-import risk and larger dependency footprint.

### Anthropic Claude Agent SDK on Python

Python runtime that pairs the Claude Agent SDK with MCP — a less common path where the agent SDK is the foundation and MCP capabilities are layered on top. Appropriate when the project blurs agent and MCP-server roles or wants to reuse Claude Agent abstractions. Pulls in a heavier dependency surface than plain MCP.

### Next.js (TypeScript) as MCP host

A Next.js App Router application that embeds the MCP server alongside a marketing landing page, OAuth UI, and HTTP API endpoints. Tool/handler logic lives in a `mcp-src/` module called from API routes. Appropriate when the deployment is a remote hosted service rather than a local stdio process — the Next.js framework provides routing, deployment integration (Vercel), and a unified surface for OAuth flows + the MCP endpoint + a public landing page. Constrains transport to HTTP-based variants and assumes a hosted-service model.

## Transport

How the MCP protocol bytes flow between the host process and the server. Choice cascades into deployment shape, authentication options, and tenancy model.

### stdio

Default transport — host process spawns the server as a child and pipes JSON-RPC over stdin/stdout. No network listener; outbound HTTPS to upstream APIs is independent. Implies single-tenant per process and credentials sourced from the spawned process's environment. Appropriate for local-developer-only deployments and the canonical Claude Desktop integration model.

### Streamable HTTP

Server exposes an HTTP endpoint (commonly `/mcp`) accepting streaming JSON-RPC. Required for remote-hosted deployments, multi-client serving, and OAuth-based auth where redirect flows need a reachable endpoint. Constrains to a hosting framework (Next.js, FastAPI, etc.) and an HTTPS-terminating frontend.

### HTTP with SSE (Server-Sent Events)

HTTP variant where the server pushes updates over an SSE stream. Often co-exists with stdio in the same binary, selected by env var or CLI flag (e.g., `TRANSPORT=http`, `--transport http`). May exist as a legacy compatibility endpoint (`/sse`) alongside a newer streamable-HTTP endpoint. Appropriate for browser-adjacent clients and for hosts that haven't adopted streamable HTTP yet.

### HTTP with JSON response mode

HTTP variant where the server returns a single JSON response per request rather than a stream. Coexists with SSE in some servers as alternative HTTP modes. Appropriate for clients that don't need streaming or for simple request/response tool calls.

### REST API bridge

Custom HTTP REST surface (separate from canonical MCP transports) exposed via an additional bridge file (e.g., `vscode_bridge.py`) on a configurable port. Non-MCP clients consume the same tool surface through a hand-rolled REST API. Appropriate when the author needs to support clients that don't speak MCP at all, or when an IDE plugin prefers REST.

### CLI dispatcher to per-server stdio

Top-level CLI binary takes a server name as a subcommand (`uvx mcp-science <server-name>`) and exec's the named child server, which then speaks stdio MCP. Appropriate for monorepos that ship many independent servers under a single PyPI package — the dispatcher unifies install/discovery while each child server retains canonical stdio semantics.

## Capability surface

The MCP entities a server exposes — tools, resources, prompts — plus any cross-cutting filtering or gating mechanisms. Differentiates servers by the upstream domain they wrap and the granularity at which they let operators trim the surface.

### Domain-tool catalog (single domain, dozens of tools)

Server exposes 20-60 tools all wrapping a single upstream domain (one database, one cloud vendor, one IDE language). Schemas are hand-authored or auto-derived per tool; tools cover CRUD, metadata, DDL, and management operations. Appropriate when the upstream API is rich and the host benefits from named, self-documenting verbs rather than a generic "execute query" tool. Trade-off: large prompt footprint when the host loads all tools.

### Aggregator-tool catalog (many upstreams, normalized tool surface)

Server multiplexes 20+ independent upstream APIs through a smaller set of normalized tools (e.g., `search_papers` dispatching across 20 academic providers; one tool per security data source across 21 vendors). Each upstream's credentials are independent; the tool layer presents a unified interface. Appropriate when the user task is upstream-agnostic ("find a paper," "look up a CVE") and per-upstream details should be hidden.

### Resources alongside tools

In addition to tools, server exposes MCP resources for inspectable state — config dumps (often redacted), debug diagnostics, exported data with TTL-based auto-cleanup. Resources are the read-side surface for state the agent should be able to inspect without invoking a tool. Appropriate when operational transparency matters and when the server holds derived artifacts (exports, diagnostics) the agent needs to reference.

### Tool-level capability gating

Operator can disable individual tools via env var lists (e.g., `DISABLED_TOOLS=tool1,tool2`). Granular but verbose; suitable when a small specific subset needs hiding.

### Category-level capability gating

Operator can enable/disable groups of tools by category (e.g., `OPENSEARCH_DISABLED_CATEGORIES=search_relevance`). Coarser than per-tool gating but matches how operators think about the surface (analytics tools, write tools, admin tools). Appropriate when the tool set is large and naturally clusters into operator-meaningful groups.

### Read-only mode flag

Single boolean flag (`--read-only`, `READ_ONLY=true`) suppresses every mutating tool. The remaining surface is the safe-by-default subset. Appropriate as a coarse safety posture — defends against agent-induced data loss without requiring per-tool curation.

### Scope-based tool filtering via URL param

For HTTP-mode servers, query parameters on the connection URL filter the tool surface (`?readonly=true`, `?category=branches`, `?projectId=...`). Different clients hitting the same hosted server see different tool surfaces. Appropriate for multi-tenant remote services where each client (or each session) needs different scoping without separate deployments.

### Destructive-tool elicitation list

Specific tools (drop-database, drop-collection) are flagged as `CONFIRMATION_REQUIRED_TOOLS`; invoking one triggers an MCP elicitation requesting human confirmation before execution. Appropriate as a per-tool safety rail beyond a coarse read-only flag — agents can invoke destructive tools but the human is brought into the loop.

## Configuration delivery

How operational settings reach the server process. Different mechanisms have different security, ergonomics, and reproducibility properties.

### Environment variables with project-prefix convention

Server reads env vars sharing a project-specific prefix (`MDB_MCP_*`, `PAPER_SEARCH_MCP_*`, `OPENSEARCH_*`). Convention prevents collision in shared environments; a `.env` file is commonly supported as a developer-friendly source. Appropriate as the canonical default — composes with Docker, systemd, host-config JSON `env` blocks, and CI secrets stores.

### CLI arguments

Server accepts flags (`--read-only`, `--db-path`, `--motherduck-token`) parsed at startup. Often coexists with env vars; flags typically override env. Appropriate for one-off invocations and ergonomic for `uvx`/`npx` usage where the host-config snippet is the primary user-facing surface.

### JSON config file

Server reads a JSON config file pointed at by an env var (e.g., `MDB_MCP_CONFIG`). Centralizes settings; supports complex nested configuration that flags or env vars handle awkwardly. Appropriate for production deployments with many settings and for templating across environments.

### YAML config file

Server reads a YAML file as the primary configuration surface (`example_config.yml`). Rarer than env-var-only in the MCP ecosystem; provides the same centralization as JSON config with comments and richer typing affordances. Appropriate for project-governed servers where operator-facing config files are a deliverable artifact.

### Auto-generated host-config JSON files

Installer (`install.py`) writes ready-to-paste `mcp_config_claude.json`, `mcp_config_vscode.json` files per supported host. Operator points the host at the generated file. Appropriate for installer-first distributions where the user is walked through setup interactively rather than reading docs.

### URL query params on HTTP connection

For HTTP-mode servers, request-time scoping happens via query params on the host's connection URL. Different from env/CLI/file because each client connection can carry different params. Appropriate for hosted multi-tenant services that need per-connection scoping without per-tenant deployments.

### Per-request header overrides

Server accepts headers on each MCP request that override server-wide config (`--allowRequestOverrides=true`). Powerful for HTTP multi-client setups where each client's request needs a slightly different posture. Appropriate when one server instance serves many clients with overlapping but not identical needs.

## Authentication

How the server proves to upstream services and how clients prove to the server. Splits along two axes: who's authenticating (client-to-server vs server-to-upstream) and what credential type.

### Connection-string auth to upstream database

Server holds a credential in a single connection string (MongoDB URI, Postgres DSN). Suitable when the upstream is a database accessed through a driver that natively consumes a string credential. Limited to one credential set per process.

### Service-account credential pair to cloud API

Server holds a Client ID + Client Secret to a cloud vendor's API (MongoDB Atlas, AWS); often paired with IP allowlist requirements. Appropriate for managed cloud services where API-key-pair is the vendor's auth norm. Server may auto-provision short-lived database users (e.g., 4-hour TTL) on top of the long-lived service-account credential to limit blast radius.

### Static API token via env

Single static token (`motherduck_token`, `NVD_API_KEY`) provided via env var or CLI flag. Simplest credential model; suitable for single-vendor servers and dev environments. No expiry or rotation mechanism in the server itself.

### Per-source independent API keys with graceful degradation

Aggregator server expects N independent API keys for N upstreams; each key is optional. Tools whose upstream lacks a key report the gap rather than failing the whole process. Appropriate for aggregator surfaces where users may only care about a subset of upstreams. Keys must never be logged or cached in audit entries.

### OAuth 2.0 / 2.1 with scopes

Browser-redirect OAuth flow with scope-based permissioning (`read`, `write`, `*`). Token presented to server via `Authorization: Bearer` header. Per-request tenancy possible because each token carries its own scope. Requires HTTP transport (browser cannot redirect to a stdio process). Appropriate for hosted multi-tenant remote services.

### API-key bearer header (headless alternative to OAuth)

For HTTP-mode servers, accepts `Authorization: Bearer <api-key>` as a headless alternative to interactive OAuth. Same scoping model as the OAuth token but without browser redirect. Appropriate for CI, server-to-server, and environments where browser flow is infeasible.

### Multi-scheme upstream auth (basic / IAM / header / mTLS)

Server supports multiple auth schemes for the same upstream type (basic auth, AWS IAM roles, header-based auth, mutual TLS) so one binary covers self-hosted, managed-cloud, and mTLS-secured deployments. Appropriate for project-governed servers expected to work across the upstream's full deployment matrix.

### Multi-scheme client auth (API key / OAuth / JWT / Basic / Bearer)

Server-side acceptance of multiple credential types from clients calling the server, paired with rate limiting, circuit breaker, and audit logging. Appropriate when the server is a security/compliance tool that itself must prove multi-scheme readiness; otherwise excessive complexity for a single-tenant local server.

## Multi-tenancy

How the server isolates state and credentials across users or sessions. Strongly coupled to transport choice.

### Single-credential single-process

One credential set per process, one user per process. Implicit when stdio is the transport. Appropriate for local-developer use; the simplest mental model.

### Externally-managed sessions via header

HTTP-mode server keeps sessions distinguished by `mcp-session-id` header when `EXTERNALLY_MANAGED_SESSIONS=true`. Per-session, not per-tenant; a single credential set still serves all sessions. Appropriate when an HTTP MCP gateway in front of the server handles tenant routing and the server only needs session affinity.

### Per-request tenancy via OAuth token scoping

Each request carries a token whose scopes determine tenant access. Server is multi-tenant by design; tenancy lives in the token, not in the server config. Appropriate for hosted remote services serving many independent users from one deployment.

### Single-user-per-workspace

Server is single-user but workspace-scoped via `WORKSPACE_PATH` env var; running multiple instances against multiple workspaces is the multi-tenancy story. Appropriate for IDE-integrated developer tools where workspace = project.

## Distribution channel

How users obtain the server. Multiple channels often coexist; choice affects update model, sandboxing, and version pinning.

### npm / npx

Server is published to npm; users invoke via `npx -y <package>@latest`. Latest-version-on-each-call ergonomics; npm pkg metadata also enables `claude_desktop_config.json` `"command": "npx"` snippets. Appropriate for TypeScript/Node servers and for users who already have Node installed.

### PyPI with pip

Server is published to PyPI; users install via `pip install <package>`. Standard Python distribution; appropriate when target users have a Python environment ready.

### PyPI via uvx

Server is published to PyPI; users invoke via `uvx <package>`. uvx provisions an isolated venv per invocation, eliminating environment conflicts. Appropriate as the recommended path for FastMCP/Python servers because it avoids the venv management burden on end users.

### PyPI via uv tool install

Server is published to PyPI; users install via `uv tool install <package>` for a persistent isolated environment. Appropriate for daily-use servers where per-invocation provisioning would be wasteful.

### Docker image

Server is published as a Docker image (e.g., `mongodb/mongodb-mcp-server:latest`). Constrains transport choices (volume mounts for stdio interop) but provides reproducible deployment. Appropriate for production deployments and for users who prefer container isolation over local interpreter management.

### MCP Bundle (.mcpb)

Server is packaged as an `.mcpb` bundle for Claude Desktop drag-and-drop installation. `.mcpbignore` file controls bundle contents. Appropriate as a frictionless install path for non-developer Claude Desktop users.

### Smithery CLI registration

Server is registered with Smithery; users install via `npx -y @smithery/cli install @<owner>/<repo> --client claude`. Smithery acts as a discovery + auto-config layer over the underlying npm/PyPI package. Appropriate for visibility in the Smithery marketplace.

### Source-only distribution

Server is not published to a registry; users clone and run `pip install -e .` or invoke via `python -m <module>`. Appropriate for early-stage projects, internal tools, or projects that intentionally avoid registry distribution.

### Interactive installer script

Server ships an `install.py` (or similar) that runs an interactive setup — picks installation mode, generates host-config files, writes credentials. Appropriate when the install requires multi-step decisions the user can't easily make from a flat CLI invocation.

### Remote-hosted service

Server is not distributed at all; vendor hosts it at a stable URL (`https://mcp.neon.tech/mcp`). Users configure the host with the URL and OAuth flow. Appropriate when the vendor wants control over deployment, rollout, and version pinning, and when the server's auth model assumes browser-redirect OAuth.

### GitHub Releases

Source tarballs and changelog published per release on GitHub. Often supplements PyPI/npm with binary or bundle artifacts. Appropriate as a release-notes home and as a fallback for users not on language-specific package managers.

## Entry point

The command users (or hosts) actually invoke to start the server. Affects the host-config snippet shape and the install workflow.

### Console script via package manifest

`pyproject.toml` `[project.scripts]` or `package.json` `"bin"` declares a named entry point installed onto PATH. Host-config snippet says `"command": "<script-name>"`. Appropriate as the canonical, name-collision-safe entry point.

### Module-form invocation

User runs `python -m <module>` with no console script declared. Appropriate for source-only installs, internal tools, or when the package author chose not to commit to a console-script name.

### CLI dispatcher subcommand

User runs `uvx <dispatcher> <server-name>` where the dispatcher routes to a child server within a monorepo PyPI package. Appropriate for monorepos that ship many servers under one package namespace.

### Direct script execution

User runs `python <script>.py` against a single-file server. Appropriate for monolithic single-file servers and rough-edge prototypes.

### Hosted URL endpoint

No local command — user points the host at a remote URL (`https://mcp.neon.tech/mcp`). The "entry point" is the URL plus an auth handshake. Appropriate for remote-hosted services.

## Test stack

The framework, scope, and isolation strategy for tests. Project-governed servers typically have stratified test suites; community single-maintainer servers typically have one suite.

### pytest with pytest-asyncio

Standard async-Python test setup; `asyncio_mode = "auto"` and per-function loop scope are common settings. Appropriate for FastMCP servers (async tools throughout) and for servers built on async upstream SDKs.

### vitest

TypeScript test framework configured via `vitest.config.ts`; tests under `/tests`. Appropriate for TypeScript MCP servers; fast, native ESM.

### Stratified suite with unit + integration + cache + security tiers

Tests split by concern — unit (pure logic, e.g., risk scoring), integration (tool registration and error handling), cache (TTL behavior against an in-process SQLite), security (private-IP blocking, XML-bomb protection). Appropriate when the server has cross-cutting infrastructure (cache, security) that warrants its own test scope.

### Pyramid with web E2E (Playwright + ephemeral DB)

Unit + integration + protocol-level E2E + browser E2E using Playwright against an ephemeral database provisioned per test run. Appropriate for hosted MCP servers with a web UI surface (OAuth consent screens, landing pages) that traditional MCP tests don't exercise.

### Separate integration_tests/ directory

Unit tests under `tests/`, real-upstream integration tests under `integration_tests/`. Different invocation paths; integration tests typically gated on CI secrets. Appropriate for project-governed servers where against-real-upstream validation is a separate cost class from unit tests.

### MyPy strict + Bandit security scans alongside tests

In addition to runtime tests, pyproject.toml configures strict static type checking and Bandit security scanning. Appropriate for security-sensitive servers and projects with explicit static-analysis discipline.

## CI / Release

How code reaches users after a commit. Splits between "push tags get artifacts" and "push to main gets a deployment."

### GitHub Actions for build/test/release

`.github/workflows/` triggers on push/PR for tests; release workflows publish to PyPI/npm/Docker on tag. Standard for both TypeScript and Python servers in this corpus.

### Vercel preview-per-PR + main deploy

Hosted-service repos use Vercel's per-PR preview deployments; merging to main auto-deploys to production. Appropriate for Next.js-hosted MCP servers where the deployable artifact is the running service.

## Container / packaging artifacts

Files that define how the server is built into deployable form beyond the language's native package format.

### Multi-stage Dockerfile

Separate build and runtime stages; final image excludes build dependencies. Appropriate for production-bound servers where image size and attack surface matter.

### docker-compose

YAML descriptor for local multi-service runs (server + companion services for development). Appropriate for projects where the server has standard companion services in dev.

### Hatch force-include for monorepo wheel

Custom `pyproject.toml` directive pulls nested `<package>/servers/` directories into the wheel when the canonical Python packaging path doesn't recognize them. Appropriate for dispatcher-style monorepos that ship one PyPI package containing many servers.

### .mcpbignore for bundle packaging

Glob file controlling what's excluded from the `.mcpb` bundle. Appropriate alongside MCP Bundle distribution.

### Azure deployment artifacts

`deploy/` directory with Azure-specific guides and scripts. Appropriate for vendors who want to provide first-class managed-cloud deployment paths.

### No container artifacts

Project-governed Python server intentionally ships only via pip/uv with no Dockerfile. Signals "managed Python environment is the deployment model."

## Host integration

The MCP-host clients the README documents support for. Affects which install snippets and badges appear in the README.

### Claude Desktop JSON snippet

Standard `mcpServers` entry (`command`, `args`, `env`) for `claude_desktop_config.json`. Universal — every server in the corpus documents this form. Appropriate as the baseline integration surface.

### Claude Code via `claude mcp add`

CLI registration via `claude mcp add <name> -- <command>`. Appropriate as the native Claude Code path — no JSON file editing.

### Cursor IDE install button

One-click install button rendered in the README. Appropriate when the vendor wants to optimize for the Cursor user base and Cursor's button infrastructure supports the deployment model.

### VS Code (and Insiders) install badges

README-rendered badges that pre-fill VS Code's MCP integration UI. Appropriate when VS Code is a primary host and the badge system is preferable to copy-paste snippets.

### JetBrains IDEs

Native MCP integration documented per JetBrains product line. Appropriate when the upstream domain (database, language) has a strong JetBrains user base.

### Cline / Windsurf / Zed

Other MCP hosts the README documents. Appropriate as low-cost extensions of the host matrix once the core stdio entry works.

### Codex CLI / Copilot CLI / Gemini CLI

Non-Anthropic agent CLIs that consume MCP. Appropriate when the server's user base spans agent ecosystems.

### LangChain integration

Server documents LangChain consumption (typically via a LangChain MCP adapter). Appropriate when the upstream domain (search, retrieval) is also a common LangChain use case.

## Claude Code plugin / skill wrapper

Whether the server ships an in-tree Claude Code skill or plugin definition. Distinguishes "MCP server only" from "MCP server + first-class Claude Code integration."

### Bare MCP server, no Claude Code wrapper

Server ships only the MCP surface; users wire it via `claude mcp add` or JSON config. Most common path.

### `.claude/skills/` directory in repo

Repo contains Claude Code skill definitions alongside the MCP server source. Skills wrap the MCP tool surface in Claude Code workflow patterns. Appropriate when the vendor wants the server discoverable via Claude Code skills, not just as a raw MCP endpoint.

### `claude-code/` directory with skill files

Sibling top-level directory carries Claude Code skill files; the README documents skill-file installation alongside MCP server installation. Appropriate as an explicit "first-class Claude Code support" signal beyond raw skill definition placement.

### `.claude-plugin` wrapper

Server ships a Claude plugin manifest with dedicated CLI commands. Appropriate when the team wants Claude Code's plugin install/update lifecycle to govern the server's lifecycle.

## Observability

How the server emits operational signal. Splits between "agent-facing logs" (visible in MCP client) and "ops-facing logs" (disk/stdout/external systems).

### Pluggable logger sinks

Server picks logger destinations from a list (`disk`, `mcp`, `stderr`) controlled by env var (`LOGGERS`). `mcp` sink emits log entries to the connected client. Appropriate when the operator wants to choose between agent-visible and ops-visible logs per deployment.

### Rotating JSON audit log on disk

Structured JSON log file with rotation (e.g., 50 MB, 5 backups) at a known location (`~/.cve-mcp/audit.log`). Fields include timestamp, tool name, parameters, duration, cache-hit status. API keys and response payloads explicitly redacted. Appropriate for security-sensitive servers where audit trail is itself a deliverable, not a side effect.

### Winston-based logging

Node-ecosystem structured-logging library configured at hosting layer with configurable levels. Appropriate for Node/Next.js hosted services.

### Sentry integration

Errors forwarded to Sentry for centralized triage. Appropriate for hosted services with on-call teams.

### Health endpoint sidecar

Optional separate monitoring server exposing health endpoints (HTTP transport only). Appropriate when the deployment runs behind a load balancer that needs liveness probes.

### Audit logging for compliance modes

Logger captures security events explicitly tied to compliance regimes (GDPR, HIPAA modes). Appropriate when the server claims compliance posture and needs to demonstrate audit retention.

## Repo layout

Structural shape of the source tree. Influences how multiple servers / multiple capability classes coexist in one repo.

### Single-package with auxiliary folders

One top-level package directory plus siblings for tests, deploy artifacts, scripts, custom lint rules, API docs. Appropriate when the project is one server but has substantial supporting infrastructure.

### Single-file monolith

One large file (e.g., `kotlin_mcp_server.py` at ~112 KB) holding all tools and the server loop. Appropriate for prototypes and for projects optimizing for "one file to read"; trades off against modular testability.

### Monorepo with per-server subdirectories and one PyPI package

`servers/<server-name>/` subdirectories each with their own README and `pyproject.toml`, but the root publishes one PyPI package that dispatches to children. Hatch `force-include` pulls children into the wheel. Appropriate for thematically-linked server collections (scientific computing) where users want one install entry but author wants per-server isolation.

### Hosted-service layout (Next.js app + mcp-src + lib)

Top-level Next.js `landing/` (or app/), `mcp-src/` for tool/handler logic, `lib/` for shared OAuth/config helpers, `tests/` for stratified suites, `.claude/skills/` for Claude Code integration. Appropriate when the deliverable is a hosted service rather than a published package.

## Documentation

How the project communicates intent and operational details to users and developers. Influences whether the README alone suffices or whether sibling docs are required.

### README-only

Single README covers install, usage, host integrations, configuration. Appropriate when the project is small enough that one document scales.

### Split USER_GUIDE / DEVELOPER_GUIDE

Two sibling markdown files separate end-user concerns from contributor concerns. Appropriate for project-governed servers (vendor or org) where each audience has substantially different needs.

### Per-subserver README in monorepo

Each child server has its own README in its subdirectory. Appropriate for monorepos with thematically-distinct children that need independent operational documentation.

### CITATION.cff

Machine-readable citation metadata for academic publication. Appropriate when the project is published or referenced in academic literature.

### GitHub Pages site

Discovery-oriented site (`mcp.science`, `<project>.github.io`) that surfaces the project to users searching outside GitHub. Appropriate for projects targeting a user base that doesn't browse GitHub directly.

## Caching and rate-limiting infrastructure

Cross-cutting modules inside the server that aren't tools but mediate how tools interact with upstreams.

### SQLite TTL cache

In-process SQLite database holds per-call cached responses with TTL. Cache-hit status surfaces in audit log. Appropriate when upstream APIs have rate limits or latency that warrant caching, and when the cache should survive process restarts.

### Token-bucket rate limiter

Explicit rate-limiter module for upstream throttling (e.g., NVD's published quota). Appropriate when one upstream's quota is the binding constraint and naive request fan-out would exhaust it.

### Circuit breaker for external calls

Circuit-breaker pattern wrapping external API calls so a degraded upstream doesn't cascade into server failure. Appropriate when the server has many upstreams and partial degradation is acceptable.

## Safety and security posture

Cross-cutting design choices that shape the server's defensive position beyond auth and tool gating.

### defusedxml for XML hardening

Library swapped in for stdlib XML parsing to defend against XML bomb / XXE attacks. Appropriate when the server consumes XML from untrusted upstreams (security feeds, public APIs).

### Temporary-user lifecycle with TTL

Server auto-provisions short-lived database users on every connection (default 4-hour TTL) instead of using a long-lived credential. Appropriate when the upstream supports user provisioning via API and the deployment wants minimal blast radius per session.

### Auto-cleanup of temporary export artifacts

Server emits resources holding exported data and deletes them after a TTL (default 5 minutes). Appropriate when the server produces transient artifacts that shouldn't accumulate.

### Dry-run config dump

`--dryRun` flag prints resolved config and exits without booting the server. Appropriate for verifying environment-merge behavior across env / CLI / file sources before committing to a long-running process.

### Index-scan rejection

`--indexCheck` flag rejects database queries that would scan without an index. Appropriate as an unusual safety posture against agent-induced load on production databases.

### Migration prepare/commit pattern

Server exposes `prepare_migration` and `complete_migration` tools so agents can stage schema changes for human review before execution. Appropriate when the upstream supports branching (Neon-style) and humans should be the apply-step authority.
