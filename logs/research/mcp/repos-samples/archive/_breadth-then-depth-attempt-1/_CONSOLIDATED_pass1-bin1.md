# Sample

Atomic knowledge chunks across the 104 MCP server samples in `repos-samples/`. Built via the breadth-then-depth methodology: bottom-up categorization-tree growth driven by sample evidence; multi-pass normalization until the tree converges; final per-branch quantification adding adoption tables under each branching subheading.

The level-1 heading `# Sample` matches the convention every sample file uses — chain keys for `sections`, `references`, and `diff` therefore align across samples and consolidated.

This document is initially empty. Pass 1 agents populate the categorization tree as they encounter implementation paths in the samples; Pass 2+ normalizes; the final pass quantifies. See `_METHODOLOGY_breadth-then-depth.md` for process details (authored alongside the first pass).

## Identification

Per-repo metadata that situates each sample in the corpus — origin, popularity, license posture, lifecycle status.

### Repo lifecycle status

Active vs archived/redirected. The corpus contains both living projects and frozen-with-redirect repos that point at successor monorepos.

- Two-stage archival pattern — code freeze months before formal GitHub archival; README body declares an earlier archival date than the org-level archived flag, signaling a "read-only maintenance" interval while a redirect target stabilizes [`Azure--azure-mcp`]
- Successor-redirect via umbrella monorepo — an org collapses per-domain MCP repos into a single company-wide MCP monorepo with shared core libraries, inverse of the per-service published-package strategy [`Azure--azure-mcp`]

### License distribution

Licenses observed in this bin: MIT (most), Apache-2.0 [`ClickHouse--mcp-clickhouse`], AGPLv3 [`HenkDz--postgresql-mcp-server`]. AGPLv3 is uncommon among MCP servers and has copyleft implications for hosts embedding the server.

### Star-count vs engineering-quality skew

Star count is not a proxy for engineering quality. A 3-star repo can carry 62 pytest tests and full ruff/mypy/CLI ergonomics [`DiversioTeam--clickup-mcp`], while large-community repos may leave testing/CI specifics unsurfaced. Read engineering rigor from the artifacts (test count, lint config, CI presence), not from popularity.

## Language and runtime

The implementation language plus the MCP SDK or framework variant. These two choices co-determine packaging, async semantics, and the surface available to consumers.

### Python servers

Dominant in the bin — most observed servers are Python-based, distributed via PyPI/uvx/Docker.

#### FastMCP framework

FastMCP is a higher-level Python SDK that auto-derives schemas from function signatures and handles the async boundary internally.

- FastMCP 2.x with `fastmcp>=2.0.0,<3.0.0` pin and `fastmcp.json` for native config [`ClickHouse--mcp-clickhouse`]
- FastMCP standalone-package style, version pin not always captured precisely [`AlwaysSany--deepl-fastmcp-python-server`]

#### Raw `mcp` SDK

Direct use of the official Python `mcp` package without a higher-level wrapper.

- Very loose pin (`mcp>=0.1.0`) — unusual; most projects pin much tighter [`DiversioTeam--clickup-mcp`]

#### Hand-rolled MCP implementation

Custom MCP wire-protocol implementation, opting out of FastMCP and the official Python SDK.

- 38 servers each carrying a hand-rolled MCP implementation wrapping a security CLI tool — suggests stdin/stdout JSON-RPC was simple enough that the SDKs added no value [`FuzzingLabs--mcp-security-hub`]

### TypeScript/JavaScript servers

Node.js runtime, distributed via npm/npx.

#### Anthropic MCP TypeScript SDK

The canonical `@modelcontextprotocol/sdk` TypeScript package.

- TypeScript 96.6%, tsup-built CLI, Anthropic MCP TypeScript SDK [`HenkDz--postgresql-mcp-server`]
- TypeScript 96.3%, tsup build, MCP SDK plus pnpm + lefthook + ESLint + Prettier opinionated dev environment [`GLips--Figma-Context-MCP`]

#### MCP SDK + Anthropic Claude Agent SDK combination

JavaScript with both the MCP SDK and the Anthropic Claude Agent SDK in use [`DaInfernalCoder--perplexity-mcp`].

### C# / .NET servers

Less common in this bin; .NET-based MCP servers often live in umbrella monorepos with shared C# core libraries [`Azure--azure-mcp`].

### Python version floor

Where surfaced: `>=3.10` is common [`ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`]. Aggressive pins exist — `runtime.txt` pinning Python 3.13.3 is finer-grained than typical `>=3.12` constraints [`AlwaysSany--deepl-fastmcp-python-server`].

## Transport

How the MCP server speaks to its host. Servers diverge on which transports they support and how the transport is selected at launch.

### Single-transport — stdio only

Default for many servers; no alternative transport documented [`HenkDz--postgresql-mcp-server`, `DiversioTeam--clickup-mcp`, `FuzzingLabs--mcp-security-hub`].

### Multi-transport in one binary

A single binary supporting multiple transports, selected at launch.

#### CLI flag selection

`--transport stdio|sse|http` plus `--host`, `--port` args [`AlwaysSany--deepl-fastmcp-python-server`].

#### Environment variable selection

`CLICKHOUSE_MCP_SERVER_TRANSPORT=stdio|http|sse` env var [`ClickHouse--mcp-clickhouse`].

#### Mixed flag + env

`--stdio` flag selects stdio mode; omission plus a `PORT` env var selects HTTP mode [`GLips--Figma-Context-MCP`].

### Transport polyglot — three transports in one binary

stdio + SSE + Streamable HTTP all in one binary, CLI- or env-selectable. Transport breadth in small community servers can exceed that of vendor-authored servers [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`].

## Distribution

Mechanisms by which end users obtain and run the server. Most servers offer multiple channels; the dominant choice depends on language ecosystem and target audience.

### PyPI publication

Python servers publish to PyPI as the canonical install path.

- `pip install mcp-clickhouse`; optional extras like `[chdb]` swap in alternative engines [`ClickHouse--mcp-clickhouse`]

### npm / npx

Node servers distribute via npm and the npx one-shot runner.

- `npx -y figma-developer-mcp ...` as the primary install [`GLips--Figma-Context-MCP`]
- `npx -y perplexity-mcp` for zero-install run [`DaInfernalCoder--perplexity-mcp`]
- `npm install -g @henkey/postgres-mcp-server` plus `npx` invocation [`HenkDz--postgresql-mcp-server`]

### `uv run` / `uvx` with on-demand install

Python servers leverage `uv` to fetch and run without explicit install.

- `uv run --with mcp-clickhouse --python 3.10 mcp-clickhouse` — uv-run with on-demand install and pinned Python [`ClickHouse--mcp-clickhouse`]
- `uvx --from git+https://github.com/...` — install-from-git URL bypasses PyPI entirely; the git URL becomes the effective package index [`DiversioTeam--clickup-mcp`]

### Docker / container images

Docker as the primary or alternative distribution channel.

- Dockerfile + docker-compose.yml for multi-transport deployment [`AlwaysSany--deepl-fastmcp-python-server`]
- Published Docker Hub image alongside npm/Smithery [`HenkDz--postgresql-mcp-server`]
- Multi-stage Node 18-Alpine Dockerfile [`DaInfernalCoder--perplexity-mcp`]
- Docker-only distribution (no PyPI/npm) — Docker image is the unit of packaging [`FuzzingLabs--mcp-security-hub`]

### Smithery registry

Smithery as a discovery/distribution channel, layered on top of npm.

- `npx -y @smithery/cli install @HenkDz/postgresql-mcp-server` [`HenkDz--postgresql-mcp-server`]
- `smithery.yaml` in the repo signals Smithery integration [`DaInfernalCoder--perplexity-mcp`]

### Source clone

Always available; sometimes the only path when no package is published.

- `git clone ... && uv sync` [`AlwaysSany--deepl-fastmcp-python-server`]

## Entry point / launch

How the server process is started by the host.

### Console script via package metadata

The conventional path: `[project.scripts]` or npm `bin` registers a name on PATH.

- `mcp-clickhouse = "mcp_clickhouse.main:main"` [`ClickHouse--mcp-clickhouse`]
- `clickup-mcp = clickup_mcp.__main__:main` — `__main__.py`-based entry rather than a `.server:main` module [`DiversioTeam--clickup-mcp`]
- npm `bin` entry pointing at tsup-built CLI [`GLips--Figma-Context-MCP`, `HenkDz--postgresql-mcp-server`]

### Bare script invoked through interpreter

No console script; user invokes the script directly.

- `uv run python main.py --transport stdio` — bare `main.py` with CLI arg handling built in (middle tier between "script + no args" and "console-script + click") [`AlwaysSany--deepl-fastmcp-python-server`]
- Bare Python scripts executed via Docker entrypoint [`FuzzingLabs--mcp-security-hub`]

### npx one-shot

Node ecosystem; package fetched and executed in one step.

- `npx -y figma-developer-mcp --figma-api-key=YOUR-KEY --stdio` [`GLips--Figma-Context-MCP`]
- `npx -y perplexity-mcp` [`DaInfernalCoder--perplexity-mcp`]

### Docker run as entry point

Host config invokes `docker run ...` rather than a local binary.

- `.mcp.json` or `claude_desktop_config.json` pointing at `docker run ...` per security tool [`FuzzingLabs--mcp-security-hub`]

## Configuration surface

How runtime configuration reaches the server. Servers diverge across env vars, CLI args, files, and OS-native config dirs.

### Environment variables only

The dominant pattern. Required + optional env vars, sometimes prefixed by domain.

- `DEEPL_AUTH_KEY` (required), `DEEPL_SERVER_URL` (optional) [`AlwaysSany--deepl-fastmcp-python-server`]
- `CLICKHOUSE_HOST/USER/PASSWORD` plus `CLICKHOUSE_SECURE/VERIFY` for TLS, transport selection, write-access gates, auth tokens, chDB enablement, middleware module [`ClickHouse--mcp-clickhouse`]

### CLI flags + env vars combined

Flags override env; env overrides file in the precedence chain.

- `--api-key` CLI > `PERPLEXITY_API_KEY` env > `.env` file [`DaInfernalCoder--perplexity-mcp`]
- `--figma-api-key` flag, `FIGMA_API_KEY` env, `--stdio` mode flag, `PORT` env [`GLips--Figma-Context-MCP`]
- `--connection-string` flag, `POSTGRES_CONNECTION_STRING` env, `POSTGRES_TOOLS_CONFIG` env, optional `tools.json` file [`HenkDz--postgresql-mcp-server`]

### `.env` file with optional CWD override

`.env` resolution path controllable via `--cwd` parameter [`DaInfernalCoder--perplexity-mcp`].

### Persistent OS-native config via platformdirs

API key stored in OS-appropriate config dir (`~/.config/`, `%APPDATA%`, etc.) — competes with `.env` files and env vars as a third credential-storage convention.

- `set-api-key` subcommand persists via `platformdirs`; `CLICKUP_MCP_API_KEY` env var is the alternative [`DiversioTeam--clickup-mcp`]

### Per-tool config file

A separate JSON file enables/disables individual tools without code changes.

- `POSTGRES_TOOLS_CONFIG` env points at `tools.json` for per-tool enablement — explicit surface-reduction knob [`HenkDz--postgresql-mcp-server`]

### Framework-native config files

- `fastmcp.json` for FastMCP-level config [`ClickHouse--mcp-clickhouse`]

## Authentication

How callers prove identity to the server, and how the server obtains its own credentials for upstream services.

### API key / personal token

Static token supplied at launch.

- DeepL API key via `DEEPL_AUTH_KEY` env var [`AlwaysSany--deepl-fastmcp-python-server`]
- ClickUp personal API token via `set-api-key` subcommand or `CLICKUP_MCP_API_KEY` env var [`DiversioTeam--clickup-mcp`]
- Perplexity API key with CLI > env > .env precedence [`DaInfernalCoder--perplexity-mcp`]
- Figma personal access token via CLI flag or env var; no OAuth flow [`GLips--Figma-Context-MCP`]

### Database connection string

Credentials embedded in a connection URI.

- PostgreSQL `user:password@host:port/database` via flag or env var [`HenkDz--postgresql-mcp-server`]

### Bearer-token auth on remote transports

stdio is unauthenticated; HTTP/SSE require a bearer token, with a dev-mode disable.

- `CLICKHOUSE_MCP_AUTH_TOKEN` (generated via `uuidgen`/`openssl`) on HTTP/SSE; `CLICKHOUSE_MCP_AUTH_DISABLED=true` for dev [`ClickHouse--mcp-clickhouse`]

### Per-tool auth-flow variation

Tool-suite servers carry per-tool credential needs (some tools need keys, others don't).

- API keys for Nuclei templates, none for Nmap; injected via container env [`FuzzingLabs--mcp-security-hub`]

## Multi-tenancy

Whether and how the server can serve multiple tenants in one process.

### Single-user / single-workspace

Process-scoped credentials; no per-request switching.

- Single API key per deployment, likely single-user [`AlwaysSany--deepl-fastmcp-python-server`]
- Token is process-scoped; one Figma identity per launch [`GLips--Figma-Context-MCP`]
- Single workspace per personal-token API key [`DiversioTeam--clickup-mcp`]
- Single connection per server instance; no per-request tenant switching [`HenkDz--postgresql-mcp-server`]
- Single user per container; one container per tool [`FuzzingLabs--mcp-security-hub`]

### Per-request tenant override via middleware

Custom middleware can override connection settings per request via context state — closest thing to multi-tenancy among DB MCP servers in this bin.

- `CLIENT_CONFIG_OVERRIDES_KEY` in context state allows middleware to swap connection settings per request [`ClickHouse--mcp-clickhouse`]

## Capabilities exposed

What the server actually exposes to the host: tools, resources, prompts, sampling, roots, logging, etc.

### Tool count and granularity

Servers diverge on whether to expose many atomic tools or fewer consolidated meta-tools.

#### Few tools (single-digit)

- 7 tools in a translation server (translate/rephrase/batch/document/detect/history/analytics) [`AlwaysSany--deepl-fastmcp-python-server`]
- 3 tools (search/reason/deep_research) with auto-routing to backend models [`DaInfernalCoder--perplexity-mcp`]
- 4 tools (run_query, list_databases, list_tables, run_chdb_select_query) [`ClickHouse--mcp-clickhouse`]

#### Many tools (tens)

- 28 tools spanning task CRUD, discovery, assignments, bulk ops, time tracking, analytics, user management [`DiversioTeam--clickup-mcp`]

#### Consolidated meta-tools

Explicit consolidation as a design response to LLM tool-discovery and parameter-validation pressure.

- 17 meta-tools consolidated down from 46 atomic tools, organized into 8 consolidated meta-tools + 4 CRUD/SQL execution + 5 specialized analysis/monitoring [`HenkDz--postgresql-mcp-server`]

### Auto-routing within a single tool

One logical tool action multiplexes across multiple backend models or modes via heuristic routing.

- `search` / `reason` / `deep_research` route to Sonar Pro / Sonar Reasoning Pro / Sonar Deep Research with optional `force_model` override [`DaInfernalCoder--perplexity-mcp`]

### Server stateful side-channels

Most MCP servers are stateless; some persist data locally across calls.

- Translation history + usage analytics persisted locally; `get_translation_history`, `analyze_usage_patterns` expose aggregated self-observations back to the LLM (reflection-style capability) [`AlwaysSany--deepl-fastmcp-python-server`]

### Domain-specific tool surfaces

- SQL execution + schema/table discovery + dual-engine (server ClickHouse + embedded chDB) [`ClickHouse--mcp-clickhouse`]
- Figma URL parsing into structured layout/styling metadata for code-gen consumption (read-only; sidesteps OAuth scope-escalation by not writing) [`GLips--Figma-Context-MCP`]
- 38 separate MCP servers, each wrapping one security CLI tool (Nmap, Ghidra, Nuclei, SQLMap, Hashcat, Shodan, etc.) [`FuzzingLabs--mcp-security-hub`]

### Pagination and filtering on list endpoints

A scalability axis absent from smaller servers.

- Paginated, filterable `list_tables` [`ClickHouse--mcp-clickhouse`]

### Progressive-trust gating of destructive operations

Two-flag gating (write-access + drop) is more granular than a single read-only toggle.

- `CLICKHOUSE_ALLOW_WRITE_ACCESS` plus a separate `CLICKHOUSE_ALLOW_DROP`; SQL-layer `readonly=1` setting compounds with the MCP-layer flags [`ClickHouse--mcp-clickhouse`]

## Extensibility

How users extend or customize a deployed server without forking.

### Middleware plugin slot

An env var loads a user-authored Python module that intercepts MCP protocol events (tool calls, resource reads, prompts, listings).

- `MCP_MIDDLEWARE_MODULE` loads middleware; example middleware shows request logging, tool-call tracking, performance measurement [`ClickHouse--mcp-clickhouse`]

### Per-tool enablement config

External JSON config selectively disables tools without changing code.

- `POSTGRES_TOOLS_CONFIG` / `tools.json` [`HenkDz--postgresql-mcp-server`]

## Observability

Logging, metrics, tracing, debug flags. Often under-documented in READMEs.

### Debug flags

- `--debug` flag on the CLI; `rich`-formatted output [`DiversioTeam--clickup-mcp`]

### Middleware-driven logging

Example middleware demonstrates request logging and performance measurement; user-supplied [`ClickHouse--mcp-clickhouse`].

### Container-level health checks

- Health-check scripts per container; Trivy vulnerability scanning in CI as part of build pipeline [`FuzzingLabs--mcp-security-hub`]

## Host integrations

Which MCP-compatible hosts the server documents support for.

### Claude Desktop

The most-cited host target; typically a JSON `mcpServers` entry [`ClickHouse--mcp-clickhouse`, `HenkDz--postgresql-mcp-server`, `FuzzingLabs--mcp-security-hub`, `GLips--Figma-Context-MCP`].

### Claude Code

Project-level `.mcp.json` with per-tool entries [`FuzzingLabs--mcp-security-hub`].

### Cursor IDE

Featured prominently in some servers' docs.

- Primary target, featured prominently with sample config in README [`GLips--Figma-Context-MCP`]
- Documented as an MCP client target [`HenkDz--postgresql-mcp-server`]

### IDE integrations beyond Claude/Cursor

Vendor-driven C# servers ship integrations for Microsoft's broader IDE ecosystem.

- VS Code, VS Code Insiders, Visual Studio 2022, IntelliJ IDEA, Eclipse [`Azure--azure-mcp` successor microsoft/mcp]

### Claude Code plugin wrapper

A `.claude-plugin` directory is the marker of a first-party plugin wrapping the MCP server. Not present in any of the bin-1 samples examined.

## Tests

Test framework, location, density. A signal of engineering rigor independent of star count.

### pytest

The dominant Python test framework.

- pytest under `tests/`, separate suites for ClickHouse and chDB; Docker Compose-backed integration services in `test-services/`; pytest-asyncio in dev extras [`ClickHouse--mcp-clickhouse`]
- 62 pytest tests with pytest-asyncio + pytest-cov on a 3-star repo [`DiversioTeam--clickup-mcp`]
- pytest with `pytest.ini`; `tests/test_mcp_servers.py` [`FuzzingLabs--mcp-security-hub`]
- `/tests/` directory present, framework details not extracted [`AlwaysSany--deepl-fastmcp-python-server`]

### vitest

The TypeScript counterpart.

- vitest configured; specifics not extracted [`GLips--Figma-Context-MCP`]

### Tests not surfaced

- Test framework not surfaced in README [`HenkDz--postgresql-mcp-server`, `DaInfernalCoder--perplexity-mcp`]

## CI

Continuous-integration system, what it runs.

### GitHub Actions

Universal default in this bin where CI is documented.

- `.github/workflows/` present; specifics not extracted [`ClickHouse--mcp-clickhouse`, `HenkDz--postgresql-mcp-server`, `DiversioTeam--clickup-mcp`, `GLips--Figma-Context-MCP`]
- Builds + security scanning (Trivy) + tests in CI [`FuzzingLabs--mcp-security-hub`]

## Container / packaging artifacts

Dockerfile, compose, image-publishing artifacts that ship alongside the source.

### Dockerfile only

- Dockerfile present, no compose or published image documented [`Azure--azure-mcp`, `DaInfernalCoder--perplexity-mcp`]

### Dockerfile + docker-compose

- Dockerfile + docker-compose.yml — SSE/HTTP transports motivate multi-container orchestration [`AlwaysSany--deepl-fastmcp-python-server`]
- Dockerfile + `test-services/` Docker Compose for local test infra [`ClickHouse--mcp-clickhouse`]

### Per-tool Dockerfiles + compose orchestration

- 38 per-tool Dockerfiles plus `Dockerfile.template` as scaffold; docker-compose for orchestration [`FuzzingLabs--mcp-security-hub`]

### Published Docker image

- Docker Hub image (`henkey/postgres-mcp:latest`) alongside npm and Smithery [`HenkDz--postgresql-mcp-server`]

### Hardened-container posture

Security-by-default container settings — non-root, capability-drop, resource limits, read-only mounts — unusual rigor for MCP servers [`FuzzingLabs--mcp-security-hub`].

## Repo layout

Single-package vs monorepo vs vendored, plus structural variants.

### Single-package

The dominant shape — one MCP server per repo.

- `main.py` at root, no installable console script [`AlwaysSany--deepl-fastmcp-python-server`]
- Python single-package: `mcp_clickhouse/`, `tests/`, `test-services/`, `.github/workflows/`, `fastmcp.json`, `pyproject.toml` [`ClickHouse--mcp-clickhouse`]
- TypeScript single-package: `/src`, `/scripts`, tsconfig, eslint config; pnpm-managed [`GLips--Figma-Context-MCP`]
- Python single-package with `__main__.py` entry [`DiversioTeam--clickup-mcp`]
- TypeScript single-package: `src/`, `docs/`, `.github/workflows/`, `build/` [`HenkDz--postgresql-mcp-server`]

### Monorepo of micro-MCP-servers

One container, one tool, one security boundary — composability at the deployment layer instead of the tool layer.

- 38 tool subdirectories, each a standalone MCP server with its own Dockerfile, Python script(s), tests [`FuzzingLabs--mcp-security-hub`]

### Umbrella monorepo with shared core

Per-domain MCP servers consolidated under one repo with shared libraries.

- `microsoft/mcp` umbrella hosting `Azure.Mcp.Server` and `Fabric.Mcp.Server` under `/servers/`, shared C# libraries under `/core/` — inverse of awslabs's per-service-PyPI-package strategy [`Azure--azure-mcp`]

## Python packaging specifics

Build backend, lock files, version-manager conventions for Python servers.

### Build backend

- `hatchling.build` [`ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`]
- Not unified across per-tool Dockerfiles — Docker layer absorbs packaging [`FuzzingLabs--mcp-security-hub`]

### Version-manager convention

`uv` is dominant in surfaced cases [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`].

### Async semantics

- FastMCP handles the async boundary; tool signatures may be sync `def` even with FastMCP 2.x [`ClickHouse--mcp-clickhouse`]
- httpx + pytest-asyncio implies async tool implementations [`DiversioTeam--clickup-mcp`]

### Type / schema strategy

- FastMCP-auto-derived schema from Python signatures [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`]
- Pydantic v2 + pydantic-settings for typed config [`DiversioTeam--clickup-mcp`]
- Hand-authored schema in custom MCP impl [`FuzzingLabs--mcp-security-hub`]

## TypeScript packaging specifics

Build tooling, package managers, dev-environment opinions for Node/TS servers.

### Build tooling

- tsup-built CLI with npm `bin` entry [`GLips--Figma-Context-MCP`, `HenkDz--postgresql-mcp-server`]

### Package manager / dev opinions

- pnpm + lefthook + ESLint + Prettier — opinionated dev environment; consumers building plugins on top should expect pnpm workflows [`GLips--Figma-Context-MCP`]

## Dual-mode binaries — server + management CLI

A pattern where the same console script handles both the MCP server protocol and a separate CLI for setup and configuration. Richer than one-binary-one-purpose.

- `clickup-mcp` console script doubles as a config CLI: `set-api-key`, `check-config`, `test-connection` subcommands plus `--debug`; `rich` for terminal output [`DiversioTeam--clickup-mcp`]

## Notable structural choices and unanticipated axes

Catch-all for design decisions that don't yet have a canonical home in the tree above. Future passes should normalize these into the proper categorization branches.

- Tool consolidation as a deliberate response to LLM discovery / parameter-validation pressure (46 atomic → 17 meta-tools) [`HenkDz--postgresql-mcp-server`]
- Hackathon-winning auto-complexity heuristic — query routed to one of three backend models without explicit caller selection [`DaInfernalCoder--perplexity-mcp`]
- Marketing framing positioning a Figma server as a design-to-code accelerator rather than a general Figma CRUD server — shapes the tool surface (read-only, no writes) [`GLips--Figma-Context-MCP`]
- Dominant community server effectively canonical despite being unofficial — no first-party figma-org repo surfaced [`GLips--Figma-Context-MCP`]
- `Dockerfile.template` as a first-class contribution surface for adding new servers to a monorepo [`FuzzingLabs--mcp-security-hub`]
