# Sample

Pass-1 Phase-1a partial for bin 7. Functional decomposition of jbeno--cursor-notebook-mcp, jlowin--fastmcp, jparkerweb--mcp-sqlite, korotovsky--slack-mcp-server, ktanaka101--mcp-server-duckdb, labeveryday--mcp_pdf_reader, lanbaoshen--mcp-jenkins, mahdin75--gis-mcp, organized by role with implementation paths as sub-sections.

## Server runtime

The language and framework that hosts MCP protocol handling and dispatches tool calls. Determines the dependency surface, async model, type-derivation strategy, and what install workflows are possible downstream.

### Python with FastMCP

Decorator-driven Python framework that wraps the official MCP Python SDK. `@mcp.tool` / `@mcp.resource` / `@mcp.prompt` declare capabilities; the framework auto-derives JSON Schema from type hints (with Pydantic) and dispatches both `def` and `async def` handlers transparently. The framework ships its own HTTP-transport stack (uvicorn, starlette, websockets, authlib, python-multipart) so consumers do not assemble it. FastMCP also exposes `Servers / Clients / Apps` pillars — "Apps" extends the framework into interactive UI territory beyond standard tools/resources/prompts. Pin discipline varies sharply across consumers: some pin to a narrow window (`>=2.7.0,<2.11`) explicitly to guard against breaking minor releases, others pin to an exact version (`fastmcp == 2.13.1`). Co-installation of raw `mcp` SDK alongside `fastmcp` shows up as a transitional pattern when projects straddle the framework boundary or use lower-level primitives. Appropriate when the server's tool count is moderate-to-large, type-annotated handlers carry the schema burden, and authors want low-ceremony decorator declarations.

### Python with raw MCP SDK

Direct use of the lower-level `mcp` Python SDK without FastMCP. Hand-authored JSON Schemas, manual server lifecycle management. Appropriate for minimal single-tool servers where decorator overhead and FastMCP's transport stack are unnecessary, or when the server intentionally exposes a single generic surface (e.g., a single `query` tool that delegates schema to the LLM). Lower dependency footprint but higher per-tool authoring cost.

### TypeScript / Node.js with `@modelcontextprotocol/sdk`

Official TypeScript SDK consumed via npm; CommonJS bin entry registered in `package.json`. Single-file servers with minimal dependencies (e.g., SDK + a domain library like `sqlite3`) shipped as npx-runnable npm packages. Appropriate for thin database or local-resource adapters where the JS ecosystem already has the canonical client library and the host's npx-based config story is the path of least friction.

### Go with custom MCP implementation

Hand-rolled Go MCP protocol implementation, no standard web framework. Yields a single static binary suitable for direct distribution or Docker base-image minimization, and supports stdio/SSE/HTTP from one build. Appropriate when single-binary deployment, performance, or enterprise-environment portability (TLS, custom User-Agent, no runtime dependency) is a priority over framework-driven authoring speed.

## Transport

How the MCP protocol bytes flow between host and server. The transport choice cascades into deployment shape, multi-tenancy possibilities, and authentication mechanism.

### stdio

JSON-RPC over stdin/stdout. The host launches the server as a child process and pipes over its standard streams. Implies single-tenant: each host instance owns one server process. Default and often only transport for local-resource servers (database files, local PDFs, local notebooks). Selected implicitly when the server is launched via host config that specifies `command` + `args`. Appropriate when the server operates on local state, when one user equals one process, and when no network surface is wanted.

### Streamable HTTP

HTTP-based transport (FastMCP's `streamable-http` or equivalent) intended for multi-client deployments. Requires host/port configuration (defaults vary: 9010, 9887, 13080 in the bin). Enables a deployed server to accept multiple host sessions, opens the door to per-request authentication via headers, and is typically the preferred path when the server is containerized. Selected via env var (`<NAME>_TRANSPORT=http`), CLI flag (`--transport`), or inferred from host config (URL vs command). Appropriate when the server should run as a long-lived service rather than a per-host child process.

### SSE (Server-Sent Events)

Legacy HTTP transport, often preserved as a compatibility option alongside Streamable HTTP. Selection mechanism is shared with HTTP (env var or CLI flag). Appropriate when host integrations have not yet migrated to streamable HTTP; preserved to avoid breaking older clients.

### SFTP / SSH for remote resource access

Not a protocol transport for MCP itself — the MCP server still speaks stdio/HTTP to the host — but the *data plane* the server reaches operates over SFTP/SSH against a remote filesystem. Listed here because authors document it as a transport-shaped axis of the server. Brings paramiko (or equivalent) into core deps. Appropriate when target resources (notebooks, files) live on a remote host and the server runs locally near the LLM.

## Capability surface

What the server exposes to the host: tools, resources, prompts, plus auxiliary HTTP endpoints. Counts and shapes vary by domain breadth.

### Single generic tool

One tool that accepts arbitrary input within a domain (e.g., a `query` tool taking arbitrary SQL). Delegates structuring entirely to the LLM. Appropriate when the underlying engine is itself a query language and the LLM is competent at producing it; minimizes server-side surface area at the cost of giving the LLM no structural guardrails.

### Domain-bundled tool set

Curated multi-tool surface organized by entity-type or operation class — e.g., job/build/queue/node tools for a CI server, conversation/thread/search/reaction tools for a chat server, notebook-create/read/edit/export tools for a notebook server. Tool counts in this bin range from ~14 to ~25. Resources optionally back the tool surface as listings (e.g., channel and user CSVs as directory resources). Appropriate when the underlying domain has well-defined entities and operations the LLM benefits from seeing as discrete callable units.

### Library fan-out

Many tools (90+) wrapping multiple upstream libraries inside one MCP surface — a "Swiss army knife" of a domain (geospatial: Shapely + GeoPandas + Rasterio + PyProj + GDAL + PySAL). Pairs with optional-dependency-per-library packaging so users install only the toolchain slices they need. Appropriate when the domain has multiple authoritative libraries no single one of which is sufficient, and the LLM benefits from one MCP server covering the entire stack.

### REST endpoints alongside MCP tools

HTTP-mode servers add purpose-built REST endpoints (`/storage/upload`, `/storage/download`, `/storage/list`) for data-plane operations MCP itself is not designed for — binary artifact transfer being the canonical case. Appropriate when the server's domain involves files too large or non-text for MCP message bodies; the MCP layer carries metadata while the REST layer carries bytes.

## Authentication

How the server identifies the caller and validates access to the underlying resource.

### None (local-resource gating)

No auth at the MCP layer. The server operates on a local file or process the host already has access to. Often paired with a path-restriction mechanism (workspace root enforcement via `os.path.realpath`, explicit `--allow-root` opt-in for local paths) to prevent traversal outside an intended directory. Appropriate when the server is a child process of the host and the security boundary is whatever the host already enforces.

### API token / credential via env vars

Static credentials provided through environment variables (`SLACK_MCP_XOXC_TOKEN`, etc.) or CLI flags read at process start. The server runs as a single tenant of the upstream service it represents. Appropriate when the server is single-user and the upstream credential model is simple (one token, one identity).

### Multi-mode token selection

The server accepts several distinct credential types for the same upstream service (e.g., browser cookie, user OAuth token, bot token) and selects behavior based on which is supplied. Enables operating modes ranging from "stealth" (no workspace permissions, browser-cookie-based) to formal OAuth with workspace admin approval. Appropriate when the upstream service's permission model varies sharply by credential type and the server needs to support all of them.

### SFTP/SSH credentials

Username + key or password (or interactive prompt) for the remote filesystem the server reaches over SFTP. Auth mode itself is configurable (`--sftp-auth-mode auto/key/password/key+interactive`). Appropriate when the data plane is remote-filesystem rather than HTTP-API.

### Per-request HTTP-header credentials

Credentials passed in HTTP headers on each MCP request (`x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password`) instead of being baked into the server process. Turns a normally single-tenant stdio server into a multi-tenant HTTP service: one deployed server can route different requests to different upstream instances and credentials. Requires HTTP transport. Appropriate when one server instance must serve multiple end-users or multiple upstream environments without per-tenant deployment.

## Multi-tenancy

How the server scopes state and identity across callers.

### Single-user single-process

One host instance, one server process, one upstream identity. The default for stdio servers. Implied by stdio transport.

### Workspace-keyed with path enforcement

Single-user but with explicit workspace-root boundaries enforced by canonicalizing paths (`os.path.realpath`) and rejecting access outside an allow-listed root. A path-traversal defense that lets the server operate on local files while bounding the blast radius. Appropriate when the server has filesystem access and the host's working directory is treated as the security boundary.

### Per-workspace tenant via upstream token

The upstream service's auth model is the tenancy boundary — one Slack workspace token equals one tenant; per-user isolation falls out of the upstream's own DM/channel scoping. Appropriate for services whose permission model is workspace- or organization-scoped natively.

### Per-request HTTP tenant

HTTP-header credentials let each MCP request specify its own upstream target and identity, so one deployed server multiplexes many tenants. Pairs with HTTP transport and stateless request handling. Appropriate when the server is a shared deployment serving heterogeneous upstream targets.

### Connection-lifecycle as a knob

Some servers expose connection persistence as an explicit flag (`--keep-connection`, `session-singleton mode`). Trade-off: persistent connections enable cross-call state (TEMP tables, pooled clients) but break the stateless-per-request model and complicate multi-tenant safety. Appropriate when the underlying engine has session-scoped state worth preserving and the deployment is single-tenant.

## Distribution channel

How the server reaches end-users for installation.

### PyPI package

Python servers publish to PyPI; consumers install with `pip` or `uv pip`. Package name often mirrors the server's domain (`mcp-server-duckdb`, `gis-mcp`, `mcp-jenkins`, `cursor-notebook-mcp`). Appropriate for Python servers that have a meaningful identity beyond a single script.

### uvx zero-install runner

`uvx <package>` runs the package without persistent installation, fetching from PyPI on demand. Often the README's recommended invocation for Python servers because it sidesteps virtualenv ceremony for end-users. Appropriate when the server has minimal startup cost and end-users want to avoid maintenance of a Python environment.

### npm package via npx

JavaScript servers publish to npm; `npx -y <package>` is the typical invocation. CommonJS bin entry registered in `package.json`. Appropriate for TypeScript/Node servers; aligns with how host MCP configs already invoke other npm tools.

### Docker / OCI image

Container image (often on `ghcr.io`) for HTTP-mode deployment or as a portable run-anywhere artifact. Multi-platform builds (amd64/arm64) are common. Sometimes paired with multiple Dockerfiles (`Dockerfile` for prod, `Dockerfile.local` for dev). Appropriate when the server is intended to run as a long-lived HTTP service or when system dependencies (binary libraries, OCR engines) make local install painful.

### docker-compose variants

Multiple compose files for distinct use cases (`docker-compose.yml`, `docker-compose.dev.yml`, `docker-compose.toolkit.yml`) — each codifies a deployment flavor. Appropriate when the server has meaningfully different operating modes (dev vs prod vs ad-hoc tooling) that benefit from distinct compose configurations.

### Smithery registry

`smithery.yaml` registers the server with the Smithery host-installer ecosystem; users install via `npx -y @smithery/cli install <name>`. Appropriate as an additional channel for hosts that consume the Smithery directory.

### Source-only (clone-and-run)

No registry publication; users clone the repository and run the server in place (`uv sync` then `uv run python <script>.py`). Appropriate for personal tools, demonstrations, or servers with system-level dependencies that resist packaging.

### Desktop Extension manifest (`manifest-dxt.json`)

A Claude Desktop-specific packaging format (DXT) distinct from `.mcp.json`. Ships alongside the server as a discoverable extension manifest. Appropriate when the server targets Claude Desktop as a primary integration and wants the DXT-level integration story rather than raw JSON config.

## Entry point

How the server is invoked once installed.

### Console script

A package-declared entry (`[project.scripts]: <name> = "<module>:main"`) installs a binary on the user's PATH. The host config simply names the command. Appropriate as the canonical Python and npm pattern.

### `python -m <module>` fallback

Module-execution form available alongside the console script. Useful when the user wants to invoke from a known interpreter (specific venv) rather than rely on PATH discovery. Often documented as an alternative for advanced users.

### Bare script

A single `.py` file with no installable entry point; users run `python <script>.py` or `uv run python <script>.py` directly. Appropriate for demonstrations and minimum-ceremony servers; competes with the console-script-PyPI pattern as the simpler tier.

### Container as launcher

Docker run is the entry — `docker run <image>` launches the server with HTTP transport pre-configured. Appropriate when the server is HTTP-mode-only or when system dependencies make non-container launch fragile.

## Configuration delivery

How runtime configuration reaches the server process.

### CLI flags

Flags parsed at process start (`--db-path`, `--readonly`, `--keep-connection`, `--host`, `--port`, `--allow-root`, `--sftp-*`). The native fit for stdio servers launched by host configs that pass `args`. Appropriate for static, per-instance configuration where re-launch is acceptable to change settings.

### Environment variables

`<NAME>_TRANSPORT`, `<NAME>_LOG_LEVEL`, credential tokens. Required for credentials that should not appear on command lines (process listings, shell history). Also the natural fit for container deployments where flags would require image rebuilds. Appropriate for credentials, transport selection, and any runtime knob that varies per deployment environment.

### Host-config JSON

Configuration files the host reads to launch and configure the server: `.cursor/mcp.json` (project) and `~/.cursor/mcp.json` (global) for Cursor; `claude_desktop_config.json` for Claude Desktop; `.vscode/mcp.json` for VSCode. The same content that would appear as CLI flags is encoded as JSON the host translates into a child-process invocation. Appropriate as the user-facing surface — humans rarely write the raw command lines themselves.

### HTTP request headers

Per-request credentials (`x-jenkins-*`) supplied on each MCP request. Required for per-request multi-tenancy under HTTP transport. Appropriate when the server is shared and each caller carries their own upstream identity.

## Host integration

How the server registers with each MCP-aware host.

### Claude Desktop config

JSON entry under `mcpServers` in `claude_desktop_config.json` specifying command/args or URL. The most-documented integration across the bin.

### Cursor config

`.cursor/mcp.json` (project-scoped) or `~/.cursor/mcp.json` (global). Some servers explicitly document both levels; transport (stdio vs HTTP) is inferred from whether the entry specifies `command` or `url`.

### VSCode `mcp.json`

`.vscode/mcp.json` entry for the VSCode MCP integration / Copilot Chat consumer.

### JetBrains IDE

Documented as an integration target for some servers, less common than the Cursor/Claude/VSCode trio.

### Smithery

`smithery.yaml` registration plus the Smithery CLI installer chooses the right host-config block for the user's chosen client.

### DXT manifest

`manifest-dxt.json` provides Claude Desktop-specific extension packaging.

## Testing

Test framework, fixtures, and tooling around the server's verification.

### pytest with async + coverage

Python servers consistently choose pytest with `pytest-asyncio`, `pytest-cov`, and frequently `pytest-timeout`. FastMCP itself stretches this further with `pytest-flakefinder`, `pytest-retry`, `pytest-xdist`, `inline-snapshot`, `pytest-examples` — flake hunting and parallelism investments rare among consumers. Some servers ship cross-platform shell wrappers (`run_tests.sh`, `run_tests.ps1`). Test plans codified in markdown (`test_plan.md`) appear when scenarios outweigh unit cases. Appropriate for any Python server; investment level scales with surface area.

### MCP Inspector as test driver

`@modelcontextprotocol/inspector` invoked via `npm test` to exercise the server end-to-end through the MCP protocol itself. Common in TypeScript servers; sometimes recommended (rather than wired) for Python servers as a manual debugging aid. Appropriate when the value is in protocol-level integration rather than unit-level coverage.

### Undocumented / minimal

Some servers ship with no documented test suite. Appropriate for personal tools and bare-script servers; raises bus-factor risk for anything broader.

## CI

Automated build/test pipelines.

### GitHub Actions

The dominant choice across the bin — `.github/workflows/` directory with workflows for tests, sometimes with codecov integration. Specific workflow contents vary; some servers do not surface details in README.

### None documented

Personal-tool-tier servers ship without CI.

## Container / packaging artifacts

Deployment-time artifacts beyond the registry package.

### Single Dockerfile

One Dockerfile in the repo root or `/docker/` subdirectory. Often multi-platform via Buildx. Appropriate for servers with one canonical container shape.

### Multi-Dockerfile (prod / dev split)

`Dockerfile` for production image plus `Dockerfile.local` for development. Explicit separation when the dev image needs additional tooling or different base. Appropriate when development needs diverge meaningfully from production.

### docker-compose variants

`docker-compose.yml` plus mode-specific variants (`.dev.yml`, `.toolkit.yml`). Appropriate when distinct compose orchestrations encode distinct operating flavors.

### None

No container artifacts; install is pip/npm/source-only. Appropriate for stdio-only single-tenant servers that have no meaningful service-deployment story.

## Build and packaging tooling

Python build backends, lockfiles, version-manager conventions.

### hatchling + uv

Build backend `hatchling.build`, lockfile `uv.lock`, install via `uv pip install` or `uvx`. The dominant modern Python pattern in this bin. Often paired with src-layout (`src/<package>/`).

### Optional-dependency fan-out

Python projects expose multiple optional-dependency groups so users install only the slices they need. Patterns range from a single `[dev]` extra to a domain-driven fan-out of one extra per upstream library (e.g., per-GIS-library extras with an `all` composer). Appropriate when the project's dependency surface is large and heterogeneous; lets the install footprint match the use case.

### Bare script (no build)

Single-file `.py` server with no `pyproject.toml` build backend, optionally with `uv sync` against ad-hoc dependency declarations. Appropriate for personal tools.

### Pin discipline

Discipline for framework version pins varies meaningfully: narrow-range pins (`>=2.7.0,<2.11`) explicitly guard against minor-release breakage; exact pins (`fastmcp == 2.13.1`) prioritize reproducibility over upgrade speed; loose pins (`>=1.0.0`) appear in minimal-ceremony servers. Choice signals the author's tolerance for upstream churn.

## System-level dependencies

External binaries the host must install before the server can run.

### Self-contained (registry-only)

Server's runtime dependencies all install via the package manager — no out-of-band system tools required. The default expectation; appropriate when domain libraries are pure-Python or include their own bundled binaries (PyMuPDF, sqlite3 wheels).

### System binary required

Server depends on a host-level binary (Tesseract OCR, GDAL, ffmpeg) that the package manager cannot install. README surfaces the install responsibility on the user. Appropriate when no Python wheel or Node module wraps the underlying tool; trade-off is friction against bundling complexity.

## Documentation for AI consumers

Docs designed to be consumed by LLMs operating the server, not just humans.

### `llms.txt` / `llms-full.txt`

Curated context summaries shipped at repo root for LLM ingestion — a "vibe coding" surface beyond the MCP protocol itself. The two-file pattern (`llms.txt` for digestible summary, `llms-full.txt` for complete reference) is emerging convention. Appropriate when the server's surface is large enough that the LLM benefits from a guided overview before reaching for individual tool descriptions.

### Bundled `cursor_rules.md` / AI-guidance content

A markdown file shipped alongside the server with rules or guidance the LLM should follow when using it. Neither MCP tool nor MCP prompt — just bundled context the host's LLM is expected to read. Appropriate when the server's correct usage requires conventions the per-tool descriptions cannot fully convey.

### `agents/` example directory

Runnable example clients demonstrating how an agent should drive the server. Appropriate when authorship benefits from concrete invocation patterns rather than abstract protocol description.

## License

Licensing posture of the published server.

### Permissive (MIT / Apache-2.0)

The dominant pattern in the bin — MIT for most, Apache-2.0 for FastMCP. Maximizes adoption; no commercial restriction.

### Copyleft / non-commercial (CC BY-NC-SA)

Rare in MCP ecosystem; appears as a deliberate restriction against commercial adoption. Trade-off: signals author's intent but limits downstream reuse in commercial settings. Appropriate when the author wants to retain commercial control over derivatives.

## Repo layout

How source, tests, examples, and infrastructure are organized.

### Single-package src-layout

`src/<package>/`, `tests/`, optionally `examples/`, `docs/`, `agents/`, `.github/`. The modern Python default and the FastMCP reference shape. Appropriate for servers with a single distributable package.

### Single-file server

One `.py` script at repo root with no package structure. Appropriate for bare-script demonstrations.

### Go single-package layout

`cmd/`, `pkg/`, `build/`, `docs/`, plus container and config artifacts. The conventional Go layout adapted to MCP server scope. Appropriate for Go single-binary servers.

### npm single-package

`package.json`, README, `bin/` entry, optional `dist/`. The conventional npm layout for a published CLI tool. Appropriate for thin Node servers.
