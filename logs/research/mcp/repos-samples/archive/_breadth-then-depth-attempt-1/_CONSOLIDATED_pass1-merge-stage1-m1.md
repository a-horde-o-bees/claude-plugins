# Sample

Pass 1 Phase 1b Stage 1 merger M1 of bins 1, 2, 7. See `_BINS.md` for input partials list.

## Identification

Per-repo metadata that situates each sample in the corpus — origin, popularity, license posture, lifecycle status, default branch, authorship.

### Repo lifecycle status

Active vs archived/redirected. The corpus contains both living projects and frozen-with-redirect repos that point at successor monorepos.

- Two-stage archival pattern — code freeze months before formal GitHub archival; README body declares an earlier archival date than the org-level archived flag, signaling a "read-only maintenance" interval while a redirect target stabilizes [`Azure--azure-mcp`]
- Successor-redirect via umbrella monorepo — an org collapses per-domain MCP repos into a single company-wide MCP monorepo with shared core libraries, inverse of the per-service published-package strategy [`Azure--azure-mcp`]

### License distribution

Licenses observed: MIT predominates, Apache-2.0 next, AGPLv3 and Creative Commons NonCommercial uncommon.

- MIT — [`ClickHouse--mcp-clickhouse` (most of bin 1)], [`JackKuo666--PubMed-MCP-Server`], [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`], [`jparkerweb--mcp-sqlite`], [`korotovsky--slack-mcp-server`], [`ktanaka101--mcp-server-duckdb`], [`labeveryday--mcp_pdf_reader`], [`lanbaoshen--mcp-jenkins`], [`mahdin75--gis-mcp`]
- Apache-2.0 — [`ClickHouse--mcp-clickhouse`], [`PagerDuty--pagerduty-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`], [`jlowin--fastmcp`]
- AGPLv3 — copyleft implications for hosts embedding the server [`HenkDz--postgresql-mcp-server`]
- Creative Commons NonCommercial (`CC BY-NC-SA 4.0`) — rare for MCP servers; restricts commercial adoption [`jbeno--cursor-notebook-mcp`]

### Default branch

- `main` — dominant [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `mahdin75--gis-mcp`]
- `master` — still in active use [`alexei-led--k8s-mcp-server`, `korotovsky--slack-mcp-server`, `lanbaoshen--mcp-jenkins`]

### Authorship

Vendor-authored vs community-authored is a trust dimension — the vendor's own MCP server carries credibility that derivative servers don't.

- Vendor-authored (official organization repo) — [`PagerDuty--pagerduty-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`], [`Azure--azure-mcp`], [`ClickHouse--mcp-clickhouse`]
- Community / individual maintainer — [`JackKuo666--PubMed-MCP-Server`], [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`], [`DiversioTeam--clickup-mcp`], [`FuzzingLabs--mcp-security-hub`], [`GLips--Figma-Context-MCP`], [`HenkDz--postgresql-mcp-server`], [`AlwaysSany--deepl-fastmcp-python-server`], [`DaInfernalCoder--perplexity-mcp`], and the bin-7 community sample set
- Dominant community server effectively canonical despite being unofficial — no first-party figma-org repo surfaced [`GLips--Figma-Context-MCP`]

### Star-count vs engineering-quality skew

Star count is not a proxy for engineering quality. A 3-star repo can carry 62 pytest tests and full ruff/mypy/CLI ergonomics [`DiversioTeam--clickup-mcp`], while large-community repos may leave testing/CI specifics unsurfaced. Read engineering rigor from the artifacts (test count, lint config, CI presence), not from popularity.

## Language and runtime

The implementation language plus the MCP SDK or framework variant. These two choices co-determine packaging, async semantics, and the surface available to consumers.

### Language

- Python — dominant [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`, `FuzzingLabs--mcp-security-hub`, `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- TypeScript / JavaScript / Node.js — [`HenkDz--postgresql-mcp-server`, `GLips--Figma-Context-MCP`, `DaInfernalCoder--perplexity-mcp`, `ahmedmustahid--postgres-mcp-server` (with secondary `pyproject.toml` of unclear purpose), `jparkerweb--mcp-sqlite`]
- Rust — [`apollographql--apollo-mcp-server`]
- Go — [`korotovsky--slack-mcp-server`]
- C# / .NET — less common in this merge; .NET-based MCP servers often live in umbrella monorepos with shared C# core libraries [`Azure--azure-mcp`]

### Python version floor

- `>=3.10` is the modal floor [`ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`, `JackKuo666--PubMed-MCP-Server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`]
- `>=3.13` — unusually high floor for April 2026 work [`alexei-led--k8s-mcp-server`]
- Aggressive specific pin — `runtime.txt` pinning Python 3.13.3 finer-grained than typical `>=3.12` constraints [`AlwaysSany--deepl-fastmcp-python-server`]
- `.python-version` file (pyenv-style) — [`JackKuo666--PubMed-MCP-Server`]
- `.python-version` present without explicit floor in pyproject [`labeveryday--mcp_pdf_reader`]
- `.tool-versions` (asdf) — rarer than uv-native or `.python-version` [`PagerDuty--pagerduty-mcp-server`]
- `requires-python` in pyproject.toml — [`alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`]
- Floor not surfaced — [`lanbaoshen--mcp-jenkins`]

### Node version floor

- `>=14.0.0` [`jparkerweb--mcp-sqlite`]

### Go version

- `1.21+` inferred from go.mod features [`korotovsky--slack-mcp-server`]

## Framework / SDK

Which MCP wrapper or SDK the server builds on, and how that choice shapes async semantics, schema derivation, and CLI surface.

### FastMCP framework (Python)

FastMCP is a higher-level Python SDK that auto-derives schemas from function signatures and handles the async boundary internally. Self-claims to power "70% of MCP servers across all languages" [`jlowin--fastmcp`].

#### FastMCP 2.x

- `fastmcp >= 2.0.0, < 3.0.0` pin and `fastmcp.json` for native config [`ClickHouse--mcp-clickhouse`]
- FastMCP standalone-package style, version pin not always captured precisely [`AlwaysSany--deepl-fastmcp-python-server`]
- FastMCP, version not pinned in README [`JackKuo666--PubMed-MCP-Server`]
- `fastmcp >= 2.0.0` [`alpacahq--alpaca-mcp-server`]
- `fastmcp >= 2.7.0, < 2.11` — narrow window guarding against FastMCP 2.11 breaking changes [`jbeno--cursor-notebook-mcp`]
- `fastmcp == 2.13.1` exact pin — conservative against API drift [`mahdin75--gis-mcp`]
- Version not pinned precisely; `pip install fastmcp` [`labeveryday--mcp_pdf_reader`]

#### FastMCP 3.x alongside raw mcp

- `fastmcp >= 3.0.1` **alongside** raw `mcp >= 1.23.0` — one server bridging two SDK generations [`awslabs--aws-api-mcp-server`]

#### Dual MCP-framework declarations (migration shim)

- Both `fastmcp >= 2.7.0, < 2.11` and `mcp >= 0.1.0` declared as deps — suggests migration / compatibility shim [`jbeno--cursor-notebook-mcp`]

#### FastMCP itself

- `jlowin--fastmcp` is the framework, not a server. Wraps and was absorbed into the official MCP Python SDK in 2024. Three-pillar model: Servers, Clients, Apps. Decorator-based API (`@mcp.tool`, etc.) is the canonical Python authoring path [`jlowin--fastmcp`]

### Raw MCP Python SDK

Direct use of the official Python `mcp` package without a higher-level wrapper.

- Very loose pin (`mcp >= 0.1.0`) — unusual; most projects pin much tighter [`DiversioTeam--clickup-mcp`]
- `mcp >= 1.0.0`; low-level server API; hand-authored schemas [`ktanaka101--mcp-server-duckdb`]
- Raw MCP SDK with no FastMCP reference [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `lanbaoshen--mcp-jenkins`]
- `mcp[cli] >= 1.23.0` [`awslabs--aws-documentation-mcp-server`]

### Hand-rolled MCP implementation

Custom MCP wire-protocol implementation, opting out of FastMCP and the official Python SDK.

- 38 servers each carrying a hand-rolled MCP implementation wrapping a security CLI tool — suggests stdin/stdout JSON-RPC was simple enough that the SDKs added no value [`FuzzingLabs--mcp-security-hub`]

### Anthropic MCP TypeScript SDK

The canonical `@modelcontextprotocol/sdk` TypeScript package.

- TypeScript 96.6%, tsup-built CLI, Anthropic MCP TypeScript SDK [`HenkDz--postgresql-mcp-server`]
- TypeScript 96.3%, tsup build, MCP SDK plus pnpm + lefthook + ESLint + Prettier opinionated dev environment [`GLips--Figma-Context-MCP`]
- `@modelcontextprotocol/sdk ^1.12.1` [`jparkerweb--mcp-sqlite`]
- `StreamableHTTPServerTransport`, `StdioServerTransport` use [`ahmedmustahid--postgres-mcp-server`]

### MCP SDK + Anthropic Claude Agent SDK combination

JavaScript with both the MCP SDK and the Anthropic Claude Agent SDK in use [`DaInfernalCoder--perplexity-mcp`].

### Rust MCP implementation

- Rust MCP implementation in the Apollo GraphQL ecosystem [`apollographql--apollo-mcp-server`]

### Go: custom implementation

- No standard Go MCP framework; custom MCP implementation [`korotovsky--slack-mcp-server`]

## Transport

How the MCP server speaks to its host. Servers diverge on which transports they support and how the transport is selected at launch.

### Single-transport — stdio only

Default for many servers; no alternative transport documented.

- [`HenkDz--postgresql-mcp-server`, `DiversioTeam--clickup-mcp`, `FuzzingLabs--mcp-security-hub`, `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`]

### stdio + HTTP variants (multi-transport)

A single binary supporting multiple transports.

- stdio + Streamable HTTP — [`alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `ahmedmustahid--postgres-mcp-server`] (HTTP is default; stdio via subcommand)
- stdio + Streamable HTTP + SSE — [`jbeno--cursor-notebook-mcp`, `mahdin75--gis-mcp`, `alexei-led--k8s-mcp-server`] (SSE deprecated in alexei-led)
- stdio + SSE + HTTP — [`korotovsky--slack-mcp-server`]
- stdio + SSE + streamable-http (default port 9887) — [`lanbaoshen--mcp-jenkins`]
- stdio + HTTP at framework level — [`jlowin--fastmcp`]

### Transport polyglot — three transports in one binary

stdio + SSE + Streamable HTTP all in one binary, CLI- or env-selectable. Transport breadth in small community servers can exceed that of vendor-authored servers [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`].

### Transport selection mechanism

#### CLI flag selection

- `--transport stdio|sse|http` plus `--host`, `--port` args [`AlwaysSany--deepl-fastmcp-python-server`]
- CLI flag selection [`alpacahq--alpaca-mcp-server`, `alexei-led--k8s-mcp-server`, `awslabs--aws-api-mcp-server`, `lanbaoshen--mcp-jenkins`]
- CLI flags (`--host`, `--port`) plus inference from host JSON config [`jbeno--cursor-notebook-mcp`]

#### Environment variable selection

- `CLICKHOUSE_MCP_SERVER_TRANSPORT=stdio|http|sse` [`ClickHouse--mcp-clickhouse`]
- `SLACK_MCP_TRANSPORT` (default stdio) [`korotovsky--slack-mcp-server`]
- `GIS_MCP_TRANSPORT` [`mahdin75--gis-mcp`]

#### Mixed flag + env

- `--stdio` flag selects stdio mode; omission plus a `PORT` env var selects HTTP mode [`GLips--Figma-Context-MCP`]

#### Positional subcommand

- `npx ... stdio` switches from default HTTP to stdio [`ahmedmustahid--postgres-mcp-server`]

#### Configuration file

- Configuration file driven [`apollographql--apollo-mcp-server`]

#### Implicit / default

- Stdio implicit / default [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`]

#### Programmatic

- Programmatic via `mcp.run()` signature in consumer code [`jlowin--fastmcp`]

### Default ports for HTTP

- 9887 [`lanbaoshen--mcp-jenkins`]
- 9010 (HTTP via Docker) [`mahdin75--gis-mcp`]
- 13080 [`korotovsky--slack-mcp-server`]
- 8080 / `127.0.0.1:8080/mcp` host-config example [`jbeno--cursor-notebook-mcp`]

## Distribution

Mechanisms by which end users obtain and run the server. Most servers offer multiple channels; the dominant choice depends on language ecosystem and target audience.

### PyPI publication

Python servers publish to PyPI as the canonical install path.

- `pip install mcp-clickhouse`; optional extras like `[chdb]` swap in alternative engines [`ClickHouse--mcp-clickhouse`]
- PyPI / `uvx` — [`PagerDuty--pagerduty-mcp-server` (`pagerduty-mcp`), `alpacahq--alpaca-mcp-server` (`alpaca-mcp-server`), `awslabs--aws-api-mcp-server` (`awslabs.aws-api-mcp-server`), `awslabs--aws-documentation-mcp-server` (`awslabs.aws-documentation-mcp-server`), `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`]

### npm / npx

Node servers distribute via npm and the npx one-shot runner.

- `npx -y figma-developer-mcp ...` as the primary install [`GLips--Figma-Context-MCP`]
- `npx -y perplexity-mcp` for zero-install run [`DaInfernalCoder--perplexity-mcp`]
- `npm install -g @henkey/postgres-mcp-server` plus `npx` invocation [`HenkDz--postgresql-mcp-server`]
- npm package; `npx -y mcp-sqlite <database-path>` direct invocation without intermediate config [`jparkerweb--mcp-sqlite`]
- npm (`npx`) — [`ahmedmustahid--postgres-mcp-server` (`@ahmedmustahid/postgres-mcp-server`)]

### `uv run` / `uvx` with on-demand install

Python servers leverage `uv` to fetch and run without explicit install.

- `uv run --with mcp-clickhouse --python 3.10 mcp-clickhouse` — uv-run with on-demand install and pinned Python [`ClickHouse--mcp-clickhouse`]
- `uvx --from git+https://github.com/...` — install-from-git URL bypasses PyPI entirely; the git URL becomes the effective package index [`DiversioTeam--clickup-mcp`]
- `uv pip install <package>` [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `mahdin75--gis-mcp`]
- `uv sync` + `uv run python <script>.py` (clone-then-run) [`labeveryday--mcp_pdf_reader`]

### Docker / container images

Docker as the primary or alternative distribution channel.

- Dockerfile + docker-compose.yml for multi-transport deployment [`AlwaysSany--deepl-fastmcp-python-server`]
- Published Docker Hub image alongside npm/Smithery [`HenkDz--postgresql-mcp-server`]
- Multi-stage Node 18-Alpine Dockerfile [`DaInfernalCoder--perplexity-mcp`]
- Docker-only distribution (no PyPI/npm) — Docker image is the unit of packaging [`FuzzingLabs--mcp-security-hub`]
- Docker / OCI image — [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alexei-led--k8s-mcp-server` (ghcr.io), `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `awslabs--aws-api-mcp-server` (AWS public ECR), `awslabs--aws-documentation-mcp-server`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- Podman (alongside Docker) [`ahmedmustahid--postgres-mcp-server`]

### Container registry

- Docker Hub or unspecified — [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-documentation-mcp-server`]
- ghcr.io (GitHub Container Registry) — [`alexei-led--k8s-mcp-server`, `lanbaoshen--mcp-jenkins`]
- AWS public ECR — [`awslabs--aws-api-mcp-server`]
- Built via release-container GitHub Actions workflow — [`apollographql--apollo-mcp-server`]

### Smithery registry

Smithery as a discovery/distribution channel, layered on top of npm.

- `npx -y @smithery/cli install @HenkDz/postgresql-mcp-server` [`HenkDz--postgresql-mcp-server`]
- `smithery.yaml` in the repo signals Smithery integration [`DaInfernalCoder--perplexity-mcp`, `mahdin75--gis-mcp`]
- Smithery installer (`npx @smithery/cli install …`) [`ktanaka101--mcp-server-duckdb`]
- Smithery-only distribution without PyPI publication — package manager path is optional when a curator like Smithery handles install [`JackKuo666--PubMed-MCP-Server`]

### Cargo / GitHub binary releases

- Cargo crate / GitHub binary releases [`apollographql--apollo-mcp-server`]

### Windows `.exe` distribution

- `uv tool run --from <pkg>@latest <pkg>.exe` [`awslabs--aws-documentation-mcp-server`]

### Source clone / clone-and-run

Always available; sometimes the only path when no package is published.

- `git clone ... && uv sync` [`AlwaysSany--deepl-fastmcp-python-server`]
- `git clone` + `pip install -r requirements.txt` / `uv sync` / `cargo build` [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `apollographql--apollo-mcp-server`]
- No PyPI publication — clone-and-run consumption [`labeveryday--mcp_pdf_reader`]
- `go run <main>.go --transport stdio` source build [`korotovsky--slack-mcp-server`]

## Entry point / launch

How the server process is started by the host.

### Console script via package metadata

The conventional path: `[project.scripts]` or npm `bin` registers a name on PATH.

- `mcp-clickhouse = "mcp_clickhouse.main:main"` [`ClickHouse--mcp-clickhouse`]
- `clickup-mcp = clickup_mcp.__main__:main` — `__main__.py`-based entry rather than a `.server:main` module [`DiversioTeam--clickup-mcp`]
- npm `bin` entry pointing at tsup-built CLI [`GLips--Figma-Context-MCP`, `HenkDz--postgresql-mcp-server`]
- `[project.scripts]` console scripts: `alpaca-mcp-server` → `alpaca_mcp_server.cli:main` [`alpacahq--alpaca-mcp-server`]; `awslabs.aws-api-mcp-server` → `awslabs.aws_api_mcp_server.server:main` [`awslabs--aws-api-mcp-server`]; `awslabs.aws-documentation-mcp-server` → `awslabs.aws_documentation_mcp_server.server:main` [`awslabs--aws-documentation-mcp-server`]
- `cursor-notebook-mcp` (also `python -m cursor_notebook_mcp.server`) [`jbeno--cursor-notebook-mcp`]
- `mcp-server-duckdb` registered to `mcp_server_duckdb:main` [`ktanaka101--mcp-server-duckdb`]
- `mcp-jenkins` console script [`lanbaoshen--mcp-jenkins`]
- `gis-mcp` (also `python -m gis_mcp`) [`mahdin75--gis-mcp`]
- `mcp-sqlite-server` (CommonJS, package.json `bin`) [`jparkerweb--mcp-sqlite`]

### Python `-m` module entry

- `python -m <pkg>` [`PagerDuty--pagerduty-mcp-server`, `awslabs--aws-api-mcp-server` (`python -m awslabs.aws_api_mcp_server.server`)]

### Bare script invoked through interpreter

No console script; user invokes the script directly. "Script as a server" simpler distribution tier.

- `uv run python main.py --transport stdio` — bare `main.py` with CLI arg handling built in (middle tier between "script + no args" and "console-script + click") [`AlwaysSany--deepl-fastmcp-python-server`]
- Bare Python scripts executed via Docker entrypoint [`FuzzingLabs--mcp-security-hub`]
- `python pubmed_server.py` [`JackKuo666--PubMed-MCP-Server`]
- `python pdf_reader_server.py` directly [`labeveryday--mcp_pdf_reader`]

### npx one-shot

Node ecosystem; package fetched and executed in one step.

- `npx -y figma-developer-mcp --figma-api-key=YOUR-KEY --stdio` [`GLips--Figma-Context-MCP`]
- `npx -y perplexity-mcp` [`DaInfernalCoder--perplexity-mcp`]
- `npx <package>` (with optional positional subcommand) [`ahmedmustahid--postgres-mcp-server`]
- `npx -y <package> <args>` direct [`jparkerweb--mcp-sqlite`]

### `uvx <package>` zero-install

- [`PagerDuty--pagerduty-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`]

### Docker run as entry point

Host config invokes `docker run ...` rather than a local binary.

- `.mcp.json` or `claude_desktop_config.json` pointing at `docker run ...` per security tool [`FuzzingLabs--mcp-security-hub`]
- Docker `run` (canonical for container-first servers) [`alexei-led--k8s-mcp-server`]
- Docker `-e` env injection for containerized runs [`awslabs--aws-api-mcp-server`]

### Compiled binary

- Compiled Rust binary [`apollographql--apollo-mcp-server`]
- `go run mcp/mcp-server.go --transport stdio` (no published Go binary) [`korotovsky--slack-mcp-server`]

### Framework-level CLI

- `fastmcp = "fastmcp.cli:app"` — `fastmcp dev`, `fastmcp run`, `fastmcp install` for dev workflow rather than serving [`jlowin--fastmcp`]

### CLI orchestration around server

- `click`-based CLI wrapper around FastMCP — richer argument handling than typical `fastmcp.run()` entry [`alpacahq--alpaca-mcp-server`]
- CLI flag `--enable-write-tools` gates mutation tools [`PagerDuty--pagerduty-mcp-server`]
- `--verbose` flag [`ahmedmustahid--postgres-mcp-server`]

### Wrapper scripts and helpers

- `run_tests.sh` + `run_tests.ps1` — explicit Windows parity [`jbeno--cursor-notebook-mcp`]
- Makefile (~5.7 KB) for cross-platform build automation [`korotovsky--slack-mcp-server`]
- Multi-platform Dockerfile under `/docker/` [`lanbaoshen--mcp-jenkins`]
- Two Dockerfiles — `Dockerfile` (prod) and `Dockerfile.local` (dev) [`mahdin75--gis-mcp`]
- 3 docker-compose variants — base, dev, toolkit [`korotovsky--slack-mcp-server`]

## Configuration surface

How runtime configuration reaches the server. Servers diverge across env vars, CLI args, files, and OS-native config dirs.

### Environment variables only

The dominant pattern. Required + optional env vars, sometimes prefixed by domain.

- `DEEPL_AUTH_KEY` (required), `DEEPL_SERVER_URL` (optional) [`AlwaysSany--deepl-fastmcp-python-server`]
- `CLICKHOUSE_HOST/USER/PASSWORD` plus `CLICKHOUSE_SECURE/VERIFY` for TLS, transport selection, write-access gates, auth tokens, chDB enablement, middleware module [`ClickHouse--mcp-clickhouse`]
- `PAGERDUTY_USER_API_KEY`, `PAGERDUTY_API_HOST` [`PagerDuty--pagerduty-mcp-server`]
- Postgres + HTTP server settings via `.env` [`ahmedmustahid--postgres-mcp-server`]
- `K8S_CONTEXT`, `K8S_NAMESPACE`, security modes, cloud creds [`alexei-led--k8s-mcp-server`]
- `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`, `ALPACA_PAPER_TRADE` [`alpacahq--alpaca-mcp-server`]
- `AWS_PROFILE`, `AWS_REGION`, transport mode, OAuth endpoints, feature flags [`awslabs--aws-api-mcp-server`]
- User-Agent override, partition selection [`awslabs--aws-documentation-mcp-server`]
- Env var driven [`korotovsky--slack-mcp-server`, `mahdin75--gis-mcp`]

### CLI flags + env vars combined

Flags override env; env overrides file in the precedence chain.

- `--api-key` CLI > `PERPLEXITY_API_KEY` env > `.env` file [`DaInfernalCoder--perplexity-mcp`]
- `--figma-api-key` flag, `FIGMA_API_KEY` env, `--stdio` mode flag, `PORT` env [`GLips--Figma-Context-MCP`]
- `--connection-string` flag, `POSTGRES_CONNECTION_STRING` env, `POSTGRES_TOOLS_CONFIG` env, optional `tools.json` file [`HenkDz--postgresql-mcp-server`]
- CLI flags (`--enable-write-tools`) [`PagerDuty--pagerduty-mcp-server`]
- CLI flags + env [`alexei-led--k8s-mcp-server`, `awslabs--aws-api-mcp-server`]

### CLI flags only

- [`ktanaka101--mcp-server-duckdb`, `jparkerweb--mcp-sqlite`]

### CLI flags + host JSON config

- [`jbeno--cursor-notebook-mcp`]

### CLI flags + HTTP headers for per-request credentials

- [`lanbaoshen--mcp-jenkins`]

### `.env` file with optional CWD override

- `.env` resolution path controllable via `--cwd` parameter [`DaInfernalCoder--perplexity-mcp`]

### Persistent OS-native config via platformdirs

API key stored in OS-appropriate config dir (`~/.config/`, `%APPDATA%`, etc.) — competes with `.env` files and env vars as a third credential-storage convention.

- `set-api-key` subcommand persists via `platformdirs`; `CLICKUP_MCP_API_KEY` env var is the alternative [`DiversioTeam--clickup-mcp`]

### Per-tool config file

A separate JSON file enables/disables individual tools without code changes.

- `POSTGRES_TOOLS_CONFIG` env points at `tools.json` for per-tool enablement — explicit surface-reduction knob [`HenkDz--postgresql-mcp-server`]

### Framework-native config files

- `fastmcp.json` for FastMCP-level config [`ClickHouse--mcp-clickhouse`]

### Configuration file (server-spec)

- Points at GraphQL endpoint, operation definitions, and the config file itself; format not extracted [`apollographql--apollo-mcp-server`]

### Claude Desktop `claude_desktop_config.json` injection

- `command`/`args` (absolute path injection) [`JackKuo666--PubMed-MCP-Server`]

### CORS configuration at the MCP layer

- `CORS_ORIGIN` env var (HTTP-transport-specific, rare) [`ahmedmustahid--postgres-mcp-server`]

### System-level dependency only

- Tesseract install — no runtime config surface [`labeveryday--mcp_pdf_reader`]

### Programmatic — framework consumers wire their own config

- [`jlowin--fastmcp`]

## Authentication

How callers prove identity to the server, and how the server obtains its own credentials for upstream services.

### No authentication

- DuckDB local file access [`ktanaka101--mcp-server-duckdb`]
- SQLite local file access [`jparkerweb--mcp-sqlite`]
- Local PDF processing [`labeveryday--mcp_pdf_reader`]
- No MCP-layer auth; downstream API keys handled per dataset [`mahdin75--gis-mcp`]
- Anonymous public-data fetching — PubMed web [`JackKuo666--PubMed-MCP-Server`]
- Public AWS docs [`awslabs--aws-documentation-mcp-server`]

### API key / personal token (single static)

Static token supplied at launch.

- DeepL API key via `DEEPL_AUTH_KEY` env var [`AlwaysSany--deepl-fastmcp-python-server`]
- ClickUp personal API token via `set-api-key` subcommand or `CLICKUP_MCP_API_KEY` env var [`DiversioTeam--clickup-mcp`]
- Perplexity API key with CLI > env > .env precedence [`DaInfernalCoder--perplexity-mcp`]
- Figma personal access token via CLI flag or env var; no OAuth flow [`GLips--Figma-Context-MCP`]
- PagerDuty User API Token via env [`PagerDuty--pagerduty-mcp-server`]
- Alpaca API key + secret pair [`alpacahq--alpaca-mcp-server`]

### Database connection string

Credentials embedded in a connection URI.

- PostgreSQL `user:password@host:port/database` via flag or env var [`HenkDz--postgresql-mcp-server`]
- Standard Postgres user/password via env [`ahmedmustahid--postgres-mcp-server`]

### Bearer-token auth on remote transports

stdio is unauthenticated; HTTP/SSE require a bearer token, with a dev-mode disable.

- `CLICKHOUSE_MCP_AUTH_TOKEN` (generated via `uuidgen`/`openssl`) on HTTP/SSE; `CLICKHOUSE_MCP_AUTH_DISABLED=true` for dev [`ClickHouse--mcp-clickhouse`]

### Inherited host credentials

- Kubeconfig + cloud provider files mounted [`alexei-led--k8s-mcp-server`]
- AWS credential chain (env / `~/.aws/credentials` / profile) [`awslabs--aws-api-mcp-server`]

### OAuth on streamable-http

- Optional OAuth on streamable-http (configurable issuer + JWKS endpoints), or no-auth [`awslabs--aws-api-mcp-server`] — the only Python sample with explicit OAuth on streamable-http; richer auth story than typical Python MCP servers, which bypass auth and rely on the stdio channel

### Per-GraphQL-endpoint auth via headers (config-file)

- Apollo Router conventions [`apollographql--apollo-mcp-server`]

### Multi-mode auth

- Four Slack token types: `XOXC` (browser), `XOXD` (cookie), `XOXP` (user OAuth), `XOXB` (bot) — flexible choice covers stealth mode and OAuth [`korotovsky--slack-mcp-server`]
- Jenkins username + password (or API token) via CLI (static) OR HTTP headers (per-request) [`lanbaoshen--mcp-jenkins`]
- SFTP/SSH key vs password vs key+interactive (`--sftp-auth-mode auto/key/password/key+interactive`) [`jbeno--cursor-notebook-mcp`]

### Per-tool auth-flow variation

Tool-suite servers carry per-tool credential needs (some tools need keys, others don't).

- API keys for Nuclei templates, none for Nmap; injected via container env [`FuzzingLabs--mcp-security-hub`]

### Framework-level

- Consumer-defined; framework supports middleware patterns for auth layering [`jlowin--fastmcp`]

## Multi-tenancy

Whether and how the server can serve multiple tenants in one process.

### Single-user / single-workspace

Process-scoped credentials; no per-request switching.

- Single API key per deployment, likely single-user [`AlwaysSany--deepl-fastmcp-python-server`]
- Token is process-scoped; one Figma identity per launch [`GLips--Figma-Context-MCP`]
- Single workspace per personal-token API key [`DiversioTeam--clickup-mcp`]
- Single connection per server instance; no per-request tenant switching [`HenkDz--postgresql-mcp-server`]
- Single user per container; one container per tool [`FuzzingLabs--mcp-security-hub`]
- Single-user per process [`JackKuo666--PubMed-MCP-Server`]
- One user token [`PagerDuty--pagerduty-mcp-server`]
- Per key pair [`alpacahq--alpaca-mcp-server`]
- One container per kubeconfig/context [`alexei-led--k8s-mcp-server`]
- README explicitly states "NOT designed for multi-tenant environments" — explicit anti-multi-tenancy statement is rare; documents the boundary rather than leaving it implicit [`awslabs--aws-api-mcp-server`]

### Single-database per server

- One DuckDB file per server instance [`ktanaka101--mcp-server-duckdb`]
- One SQLite database per instance [`jparkerweb--mcp-sqlite`]
- Single database per server, HTTP transport supports stateful sessions but not per-request tenant switching [`ahmedmustahid--postgres-mcp-server`]

### Single-user file-processing

- Single-user, file-processing only [`labeveryday--mcp_pdf_reader`]
- Single-user; HTTP mode exposes upload/download but no tenant isolation [`mahdin75--gis-mcp`]

### Workspace-keyed

- Workspace root restrictions enforced via `os.path.realpath`; `--allow-root` required for local-path access [`jbeno--cursor-notebook-mcp`]
- Per-workspace tenancy via Slack API token; per-user isolation via DM/channel context [`korotovsky--slack-mcp-server`]

### Per-request tenant override via middleware

Custom middleware can override connection settings per request via context state — closest thing to multi-tenancy among DB MCP servers.

- `CLIENT_CONFIG_OVERRIDES_KEY` in context state allows middleware to swap connection settings per request [`ClickHouse--mcp-clickhouse`]

### Per-request credentials (HTTP-mode multi-tenancy)

- `x-jenkins-url`, `x-jenkins-username`, `x-jenkins-password` headers — single deployed server can target multiple Jenkins instances per request; turns single-tenant stdio into multi-tenant HTTP service [`lanbaoshen--mcp-jenkins`]

### Stateless / N/A

- Read-only public-doc fetching [`awslabs--aws-documentation-mcp-server`]
- Not extracted [`apollographql--apollo-mcp-server`]

### Framework

- Arbitrary tenancy patterns — consumer decides; HTTP transport enables shared deployments [`jlowin--fastmcp`]

## Capabilities exposed

What the server actually exposes to the host: tools, resources, prompts, sampling, roots, logging, etc.

### Tool count and granularity

Servers diverge on whether to expose many atomic tools, fewer consolidated meta-tools, single generic delegating tools, or massive cross-library fan-out.

#### Single generic tool delegating to LLM

- Single `query` tool accepting arbitrary SQL — delegates SQL generation entirely to LLM [`ktanaka101--mcp-server-duckdb`]

#### Few tools (single-digit)

- 7 tools in a translation server (translate/rephrase/batch/document/detect/history/analytics) [`AlwaysSany--deepl-fastmcp-python-server`]
- 3 tools (search/reason/deep_research) with auto-routing to backend models [`DaInfernalCoder--perplexity-mcp`]
- 4 tools (run_query, list_databases, list_tables, run_chdb_select_query) [`ClickHouse--mcp-clickhouse`]
- 5 tools (PubMed search, metadata, PDF download, deep analysis) [`JackKuo666--PubMed-MCP-Server`]
- 3 tools (`call_aws`, `suggest_aws_commands`, experimental `get_execution_plan`) [`awslabs--aws-api-mcp-server`]
- 5 partition-scoped tools (`read_documentation`, `search_documentation` global-only, `read_sections`, `recommend`, `get_available_services` China-only) [`awslabs--aws-documentation-mcp-server`]
- Database introspection + CRUD + parameterized SQL queries [`jparkerweb--mcp-sqlite`]
- PDF text extraction + image extraction + OCR text recognition [`labeveryday--mcp_pdf_reader`]
- 1 tool (read-only SQL) + 2 resources (Database Tables, Database Schema) [`ahmedmustahid--postgres-mcp-server`]

#### Many tools (10–30)

- 28 tools spanning task CRUD, discovery, assignments, bulk ops, time tracking, analytics, user management [`DiversioTeam--clickup-mcp`]
- 14 tools — conversation history, thread replies, message search, reactions, user-group management, unread tracking; plus 2 resources as CSV directories [`korotovsky--slack-mcp-server`]
- 24 tools covering job management, build operations, queue handling, node/view queries, console output retrieval [`lanbaoshen--mcp-jenkins`]
- 25+ tools — `notebook_create`, `notebook_read`, `notebook_edit_cell`, `notebook_add_cell`, `notebook_export`, `notebook_search`, `notebook_get_outline`, `notebook_get_server_path_context`, plus SFTP-compatible variants [`jbeno--cursor-notebook-mcp`]

#### Massive tool count (50+)

- 65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, change events [`PagerDuty--pagerduty-mcp-server`]
- ~60 tools across 10 categories (Account/Trading/Positions/Watchlists/Assets/Stock/Crypto/Options/CorpActions/News) [`alpacahq--alpaca-mcp-server`]
- 92 tools across 5 libraries — Shapely (29), PyProj (13), GeoPandas (13), Rasterio (20), PySAL (18), visualization (2), plus data-acquisition modules. HTTP mode adds REST `/storage/upload`, `/storage/download`, `/storage/list` for binary artifacts MCP isn't built for [`mahdin75--gis-mcp`]

#### Consolidated meta-tools

Explicit consolidation as a design response to LLM tool-discovery and parameter-validation pressure.

- 17 meta-tools consolidated down from 46 atomic tools, organized into 8 consolidated meta-tools + 4 CRUD/SQL execution + 5 specialized analysis/monitoring [`HenkDz--postgresql-mcp-server`]

#### CLI-wrapper tools

- Tool wrappers around `kubectl`/`helm`/`istioctl`/`argocd` plus Unix piping (`jq`/`grep`/`sed`) [`alexei-led--k8s-mcp-server`]

#### Generated tool catalog

- Tools generated from configured GraphQL operation definitions [`apollographql--apollo-mcp-server`]

### Capability source

How the tool catalog gets populated.

- Hand-coded tool handlers — bulk of corpus
- Generated from OpenAPI / pre-generated from spec — "complete rewrite built with FastMCP and OpenAPI" [`alpacahq--alpaca-mcp-server`]
- Generated from GraphQL operation definitions at config time — operators shape the catalog by choosing which operations to expose; tool definitions live as GraphQL operations, not as MCP tool declarations [`apollographql--apollo-mcp-server`]
- CLI command wrapping — wraps existing CLIs [`alexei-led--k8s-mcp-server`]; wraps AWS CLI, ships pinned `awscli==1.44.81` [`awslabs--aws-api-mcp-server`]

### Resources

- `Database Tables`, `Database Schema` resources [`ahmedmustahid--postgres-mcp-server`]
- CSV channel/user lists exposed as resources [`korotovsky--slack-mcp-server`]
- Tools-only (no resources/prompts) [`alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`]

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

### Read-only vs mutation gating

- Progressive-trust gating of destructive operations — `CLICKHOUSE_ALLOW_WRITE_ACCESS` plus a separate `CLICKHOUSE_ALLOW_DROP`; SQL-layer `readonly=1` setting compounds with the MCP-layer flags. Two-flag gating is more granular than a single read-only toggle [`ClickHouse--mcp-clickhouse`]
- Read-only-by-default with mutation gated behind a CLI flag (`--enable-write-tools`) [`PagerDuty--pagerduty-mcp-server`]
- Paper-trading mode default (`ALPACA_PAPER_TRADE=true`) — mutation-capable but sandbox-by-default; safety pattern other trading/finance servers should emulate [`alpacahq--alpaca-mcp-server`]
- Read-only by design (SQL execution restricted to read-only queries) [`ahmedmustahid--postgres-mcp-server`]
- Pure read-only documentation bridge [`awslabs--aws-documentation-mcp-server`]
- Experimental tools gated by feature flag (`get_execution_plan`) [`awslabs--aws-api-mcp-server`]
- `--readonly` flag delegates to DuckDB's native protection (not tool-layer validation); non-readonly auto-creates DB file and parent dirs [`ktanaka101--mcp-server-duckdb`]
- Read-only mode flag at server level [`lanbaoshen--mcp-jenkins`]

### Capability types beyond tools

- Three-pillar framework: Servers (tools/resources/prompts), Clients, Apps (interactive UIs in conversations) [`jlowin--fastmcp`]
- REST endpoints alongside MCP tools to handle binary file transfer (`/storage/upload`, `/storage/download`, `/storage/list`) [`mahdin75--gis-mcp`]

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

### Logging library / mechanism

- Standard Python `logging` [`JackKuo666--PubMed-MCP-Server`]
- `loguru` [`awslabs--aws-documentation-mcp-server`]
- `loguru` + `python-json-logger` (dual logging paths) [`awslabs--aws-api-mcp-server`]
- `SLACK_MCP_LOG_LEVEL` env var; macOS log location `~/Library/Logs/Claude/mcp*.log`; Inspector tool for debugging [`korotovsky--slack-mcp-server`]
- Framework-level logging utilities; consumers configure destinations [`jlowin--fastmcp`]
- MCP Inspector script via `npm test` [`jparkerweb--mcp-sqlite`]
- Not surfaced [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `jbeno--cursor-notebook-mcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]

### Debug flags

- `--debug` flag on the CLI; `rich`-formatted output [`DiversioTeam--clickup-mcp`]
- `--verbose` flag [`ahmedmustahid--postgres-mcp-server`]

### Middleware-driven logging

- Example middleware demonstrates request logging and performance measurement; user-supplied [`ClickHouse--mcp-clickhouse`]

### Container-level health checks

- Health-check scripts per container; Trivy vulnerability scanning in CI as part of build pipeline [`FuzzingLabs--mcp-security-hub`]

## Host integrations

Which MCP-compatible hosts the server documents support for.

### Claude Desktop

The most-cited host target; typically a JSON `mcpServers` entry.

- [`ClickHouse--mcp-clickhouse`, `HenkDz--postgresql-mcp-server`, `FuzzingLabs--mcp-security-hub`, `GLips--Figma-Context-MCP`, `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`, `lanbaoshen--mcp-jenkins`, `korotovsky--slack-mcp-server`]
- Implied via stdio transport [`jbeno--cursor-notebook-mcp`]

### Claude Code

- Project-level `.mcp.json` with per-tool entries [`FuzzingLabs--mcp-security-hub`]

### Cursor IDE

Featured prominently in some servers' docs.

- Primary target, featured prominently with sample config in README [`GLips--Figma-Context-MCP`]
- Documented as an MCP client target [`HenkDz--postgresql-mcp-server`]
- `~/.cursor/mcp.json` [`alpacahq--alpaca-mcp-server`]
- `.cursor/mcp.json` (project-scoped) and `~/.cursor/mcp.json` (global) — explicit dual-level config documented [`jbeno--cursor-notebook-mcp`]
- `.cursor/mcp.json` snippet [`mahdin75--gis-mcp`]
- npx command [`jparkerweb--mcp-sqlite`]

### VS Code

- `.vscode/mcp.json` entry [`alpacahq--alpaca-mcp-server`, `lanbaoshen--mcp-jenkins`]
- npx command [`jparkerweb--mcp-sqlite`]

### IDE integrations beyond Claude/Cursor

Vendor-driven C# servers ship integrations for Microsoft's broader IDE ecosystem.

- VS Code, VS Code Insiders, Visual Studio 2022, IntelliJ IDEA, Eclipse [`Azure--azure-mcp` successor microsoft/mcp]
- PyCharm (Settings → Tools → MCP) — less widely advertised than Claude Desktop [`alpacahq--alpaca-mcp-server`]
- JetBrains IDE — unusual; most MCP servers focus on Claude/Cursor/VSCode [`lanbaoshen--mcp-jenkins`]
- Gemini CLI (`settings.json`) [`alpacahq--alpaca-mcp-server`]

### Cline

- Dedicated example [`JackKuo666--PubMed-MCP-Server`]

### MCP Inspector

- [`ahmedmustahid--postgres-mcp-server`, `apollographql--apollo-mcp-server`]

### Smithery registry as host integration

- `smithery.yaml` in repo root [`JackKuo666--PubMed-MCP-Server`, `mahdin75--gis-mcp`]
- Smithery installer for host registration [`ktanaka101--mcp-server-duckdb`]

### Generic AI client

- Generic JSON `mcpServers` entry [`PagerDuty--pagerduty-mcp-server`, `apollographql--apollo-mcp-server`]

### Enterprise Slack / GovSlack

- Custom User-Agent + TLS config for Slack environments [`korotovsky--slack-mcp-server`]

### DXT (Desktop Extensions) manifest

- `manifest-dxt.json` — Claude Desktop-specific packaging format distinct from `.mcp.json` [`korotovsky--slack-mcp-server`]

### Broad coverage

- 5 different MCP clients documented (Claude Desktop, Cursor, VS Code, PyCharm, Gemini CLI) — broader host-integration coverage than typical [`alpacahq--alpaca-mcp-server`]

### Claude Code plugin wrapper

A `.claude-plugin` directory is the marker of a first-party plugin wrapping the MCP server.

- Not present in any of the bin-1, bin-2, or bin-7 samples examined
- `.claude/` directory + `CLAUDE.md` at repo root (operational Claude docs; may be Claude Code workspace state, not a `.claude-plugin/plugin.json` wrapper) [`apollographql--apollo-mcp-server`]
- Not applicable — framework level [`jlowin--fastmcp`]

## Tests

Test framework, location, density. A signal of engineering rigor independent of star count.

### pytest

The dominant Python test framework.

- pytest under `tests/`, separate suites for ClickHouse and chDB; Docker Compose-backed integration services in `test-services/`; pytest-asyncio in dev extras [`ClickHouse--mcp-clickhouse`]
- 62 pytest tests with pytest-asyncio + pytest-cov on a 3-star repo [`DiversioTeam--clickup-mcp`]
- pytest with `pytest.ini`; `tests/test_mcp_servers.py` [`FuzzingLabs--mcp-security-hub`]
- pytest + pytest-asyncio [`alpacahq--alpaca-mcp-server`]
- pytest + pytest-asyncio + pytest-cov + pytest-mock [`awslabs--aws-api-mcp-server`]
- pytest with `--cov --cov-branch` and a custom `--run-live` flag for live-AWS integration tests [`awslabs--aws-documentation-mcp-server`]
- pytest + pytest-asyncio + pytest-cov + pytest-timeout; `tests/` directory; `test_plan.md` for scenario documentation; cross-platform shell-script runners [`jbeno--cursor-notebook-mcp`]
- Extreme tooling stack: pytest + pytest-asyncio + pytest-cov + pytest-env + pytest-flakefinder + pytest-httpx + pytest-report + pytest-retry + pytest-timeout + pytest-xdist + inline-snapshot + pytest-examples; `asyncio_mode = "auto"`, `timeout = 5`, `testpaths = ["tests"]` [`jlowin--fastmcp`]
- pytest with coverage and async support in `test` extra [`mahdin75--gis-mcp`]
- pytest in dev deps; no pytest config in pyproject.toml — minimal [`ktanaka101--mcp-server-duckdb`]
- `/tests/` directory present, framework details not extracted [`AlwaysSany--deepl-fastmcp-python-server`, `PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `lanbaoshen--mcp-jenkins`]

### vitest

The TypeScript counterpart.

- vitest configured; specifics not extracted [`GLips--Figma-Context-MCP`]

### MCP Inspector / npm test

- MCP Inspector framework; `npm test` script [`jparkerweb--mcp-sqlite`]

### End-to-end protocol-conformance harness

- End-to-end harness in `/e2e/mcp-server-tester` [`apollographql--apollo-mcp-server`]

### Tests not surfaced

- [`HenkDz--postgresql-mcp-server`, `DaInfernalCoder--perplexity-mcp`, `JackKuo666--PubMed-MCP-Server`, `korotovsky--slack-mcp-server`, `labeveryday--mcp_pdf_reader`]

### Notable testing patterns

- Multi-layered test suite (integrity / server-construction / paper-API integration) [`alpacahq--alpaca-mcp-server`]
- Bedrock test result files in repo (cross-platform agent validation) [`PagerDuty--pagerduty-mcp-server`]
- Live-network integration gated behind opt-in flag (`--run-live`) [`awslabs--aws-documentation-mcp-server`]
- Protocol-conformance e2e tester as a first-class component [`apollographql--apollo-mcp-server`]
- Docs are test-verified — `griffelib`, `inline-snapshot`, `pytest-examples` [`jlowin--fastmcp`]
- Flake hunting and parallelism — `pytest-flakefinder` + `pytest-retry` + `pytest-xdist` [`jlowin--fastmcp`]

## CI

Continuous-integration system, what it runs.

### GitHub Actions

Universal default in this corpus where CI is documented.

- `.github/workflows/` present; specifics not extracted [`ClickHouse--mcp-clickhouse`, `HenkDz--postgresql-mcp-server`, `DiversioTeam--clickup-mcp`, `GLips--Figma-Context-MCP`]
- Builds + security scanning (Trivy) + tests in CI [`FuzzingLabs--mcp-security-hub`]
- GitHub Actions on every PR [`alpacahq--alpaca-mcp-server`]
- GitHub Actions (`.github/`) [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server` (`release.yml`, `ci.yml`), `apollographql--apollo-mcp-server` (CI + release-binaries + release-container workflows)]
- GitHub Actions [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp` (`run-tests.yml`), `korotovsky--slack-mcp-server`, `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- codecov integration [`lanbaoshen--mcp-jenkins`]
- CI badge visible [`mahdin75--gis-mcp`]

### Parent monorepo CI

- Sub-server-specific config not extracted [`awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`]

### `.github/` present, workflow details not surfaced

- [`JackKuo666--PubMed-MCP-Server`]

### Not detailed / not documented

- [`ahmedmustahid--postgres-mcp-server`, `jparkerweb--mcp-sqlite`, `labeveryday--mcp_pdf_reader`]

## Container / packaging artifacts

Dockerfile, compose, image-publishing artifacts that ship alongside the source.

### Dockerfile only

- [`Azure--azure-mcp`, `DaInfernalCoder--perplexity-mcp`, `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server` (with stdio transport), `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `lanbaoshen--mcp-jenkins` (multi-platform under `/docker/`), `korotovsky--slack-mcp-server` (Dockerfile 874 bytes + `.dockerignore`)]

### Dockerfile + docker-compose

- Dockerfile + docker-compose.yml — SSE/HTTP transports motivate multi-container orchestration [`AlwaysSany--deepl-fastmcp-python-server`]
- Dockerfile + `test-services/` Docker Compose for local test infra [`ClickHouse--mcp-clickhouse`]
- Dockerfile + docker-compose [`ahmedmustahid--postgres-mcp-server`]

### Multiple Dockerfiles / compose variants

- 3 docker-compose variants: `docker-compose.yml` (base), `docker-compose.dev.yml`, `docker-compose.toolkit.yml` [`korotovsky--slack-mcp-server`]
- Two Dockerfiles — `Dockerfile` (prod) and `Dockerfile.local` (dev) [`mahdin75--gis-mcp`]

### Per-tool Dockerfiles + compose orchestration

- 38 per-tool Dockerfiles plus `Dockerfile.template` as scaffold; docker-compose for orchestration [`FuzzingLabs--mcp-security-hub`]

### Published Docker image

- Docker Hub image (`henkey/postgres-mcp:latest`) alongside npm and Smithery [`HenkDz--postgresql-mcp-server`]

### Container built via release workflow

- [`apollographql--apollo-mcp-server`]

### Hardened-container posture

Security-by-default container settings — non-root, capability-drop, resource limits, read-only mounts — unusual rigor for MCP servers [`FuzzingLabs--mcp-security-hub`].

### None

- [`jbeno--cursor-notebook-mcp`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`]

### Framework-level — consumer-containerized

- [`jlowin--fastmcp`]

## Repo layout

Single-package vs monorepo vs vendored, plus structural variants.

### Single-package

The dominant shape — one MCP server per repo.

- `main.py` at root, no installable console script [`AlwaysSany--deepl-fastmcp-python-server`]
- Python single-package: `mcp_clickhouse/`, `tests/`, `test-services/`, `.github/workflows/`, `fastmcp.json`, `pyproject.toml` [`ClickHouse--mcp-clickhouse`]
- TypeScript single-package: `/src`, `/scripts`, tsconfig, eslint config; pnpm-managed [`GLips--Figma-Context-MCP`]
- Python single-package with `__main__.py` entry [`DiversioTeam--clickup-mcp`]
- TypeScript single-package: `src/`, `docs/`, `.github/workflows/`, `build/` [`HenkDz--postgresql-mcp-server`]
- Single package under `<pkg>/` [`PagerDuty--pagerduty-mcp-server`, `alpacahq--alpaca-mcp-server`]
- Single package under `src/<pkg>/` (src-layout) [`alexei-led--k8s-mcp-server`, `jlowin--fastmcp`, `mahdin75--gis-mcp`]
- Single-package Python (flat layout) + `examples/` + `tests/` [`jbeno--cursor-notebook-mcp`]
- Single-package Python [`ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`]
- Single npm package with `package.json`, README, `bin` entry [`jparkerweb--mcp-sqlite`]
- Single-file server (`pdf_reader_server.py`) — no package [`labeveryday--mcp_pdf_reader`]

### Bare-script style

- Entry script + helper at repo root; `pyproject.toml` and `requirements.txt` side by side [`JackKuo666--PubMed-MCP-Server`]

### Mixed-language single-package

- Mixed single-package (TS-majority `src/` + `package.json`, sibling `pyproject.toml` and `images/` directory) [`ahmedmustahid--postgres-mcp-server`]

### Single Rust crate

- `Cargo.toml` + `/examples` + `/e2e` [`apollographql--apollo-mcp-server`]

### Single Go package

- `cmd/`, `pkg/`, `build/`, `docs/`, `.github/`, `.vscode/`, `npm/`, plus `manifest-dxt.json`, `SECURITY.md` [`korotovsky--slack-mcp-server`]

### Sub-package inside parent monorepo

- Each sub-server has its own `pyproject.toml`, console script, PyPI release — consumers install one sub-server without pulling the rest [`awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`]

### Monorepo of micro-MCP-servers

One container, one tool, one security boundary — composability at the deployment layer instead of the tool layer.

- 38 tool subdirectories, each a standalone MCP server with its own Dockerfile, Python script(s), tests [`FuzzingLabs--mcp-security-hub`]

### Umbrella monorepo with shared core

Per-domain MCP servers consolidated under one repo with shared libraries.

- `microsoft/mcp` umbrella hosting `Azure.Mcp.Server` and `Fabric.Mcp.Server` under `/servers/`, shared C# libraries under `/core/` — inverse of awslabs's per-service-PyPI-package strategy [`Azure--azure-mcp`]

### Manifest patterns

- Both `pyproject.toml` and `requirements.txt` (redundant manifests; suggests requirements-driven bootstrap) [`JackKuo666--PubMed-MCP-Server`]
- Both Poetry (`poetry.lock`) and uv workflows supported [`PagerDuty--pagerduty-mcp-server`]
- `package.json` + sibling `pyproject.toml` in TS-majority repo (purpose unexplained) [`ahmedmustahid--postgres-mcp-server`]

## Dev ergonomics

Build automation, scripts, dev opinions outside packaging.

### Dev tooling

- Makefile [`ahmedmustahid--postgres-mcp-server`, `alexei-led--k8s-mcp-server`, `korotovsky--slack-mcp-server`]
- `scripts/` directory [`PagerDuty--pagerduty-mcp-server`]
- `website/` directory (docs site alongside server) [`PagerDuty--pagerduty-mcp-server`]
- `/docs/` directory [`alexei-led--k8s-mcp-server`]
- `/examples/` directory [`apollographql--apollo-mcp-server`]
- ruff + mypy + pytest dev stack [`alpacahq--alpaca-mcp-server`]
- pre-commit + commitizen + ruff + pyright (commit-style enforcement) [`awslabs--aws-api-mcp-server`]
- `prek` (pre-commit replacement) in dev deps; ruff + `ty` (Astral's new type checker) — adopting newer tooling ahead of the ecosystem [`jlowin--fastmcp`]
- Pre-commit-style workflow [`mahdin75--gis-mcp`]
- Minimal dev tooling — only pytest in dev; no ruff/mypy/coverage [`ktanaka101--mcp-server-duckdb`]
- None explicit [`JackKuo666--PubMed-MCP-Server`]

### LLM-consumable docs

- `llms.txt` and `llms-full.txt` for AI-consumable docs ("vibe coding" context) — design-for-AI-consumption documentation format [`jlowin--fastmcp`, `mahdin75--gis-mcp`]

### Bundled AI-guidance content

- `cursor_rules.md` shipped alongside server — neither MCP tool nor prompt, just LLM-readable guidance [`jbeno--cursor-notebook-mcp`]

### Inspector / curl / make

- MCP Inspector recommended (`npx @modelcontextprotocol/inspector`) [`ktanaka101--mcp-server-duckdb`, `korotovsky--slack-mcp-server`, `jparkerweb--mcp-sqlite`]
- `agents/` directory with runnable example clients [`mahdin75--gis-mcp`]
- `.vscode/mcp.json` sample [`lanbaoshen--mcp-jenkins`]
- `examples/` + `docs/` directories; community Discord; docs at gofastmcp.com [`jlowin--fastmcp`]

## Python packaging

Build backend, lock files, version-manager conventions for Python servers.

### Build backend

- `hatchling.build` [`ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`, `jlowin--fastmcp`]
- Poetry (`poetry.lock` present) [`PagerDuty--pagerduty-mcp-server`]
- pyproject.toml (uv-based); backend not surfaced [`lanbaoshen--mcp-jenkins`]
- Not unified across per-tool Dockerfiles — Docker layer absorbs packaging [`FuzzingLabs--mcp-security-hub`]
- Not surfaced [`JackKuo666--PubMed-MCP-Server`, `alexei-led--k8s-mcp-server`]
- Not applicable — single script [`labeveryday--mcp_pdf_reader`]

### Lock file / version manager

`uv` is dominant in surfaced cases.

- `uv` / `uvx` adoption [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- `uv.lock` present [`jlowin--fastmcp`]
- `uv.lock` implied [`labeveryday--mcp_pdf_reader`, `ktanaka101--mcp-server-duckdb`]
- Not explicitly confirmed [`mahdin75--gis-mcp`, `jbeno--cursor-notebook-mcp`, `lanbaoshen--mcp-jenkins`]
- `poetry.lock` (also supports uv) [`PagerDuty--pagerduty-mcp-server`]
- `requirements.txt` (no lock) [`JackKuo666--PubMed-MCP-Server`]

### Async semantics

- FastMCP handles the async boundary; tool signatures may be sync `def` even with FastMCP 2.x [`ClickHouse--mcp-clickhouse`]
- httpx + pytest-asyncio implies async tool implementations [`DiversioTeam--clickup-mcp`]
- async (FastMCP + starlette + uvicorn) [`jbeno--cursor-notebook-mcp`]
- Both `def` and `async def` dispatched transparently; anyio/asyncio under the hood [`jlowin--fastmcp`]
- FastMCP auto-wraps both [`mahdin75--gis-mcp`]
- Sync handlers — file-processing stack (PyMuPDF, pytesseract) is CPU-bound; async offers little value [`labeveryday--mcp_pdf_reader`]
- `httpx` (network-bound work; likely async) [`alpacahq--alpaca-mcp-server`, `awslabs--aws-documentation-mcp-server`]
- Mentions `asyncio` [`JackKuo666--PubMed-MCP-Server`]
- Not surfaced [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `awslabs--aws-api-mcp-server`, `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`]

### Type / schema strategy

- FastMCP-auto-derived schema from Python signatures [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`, `JackKuo666--PubMed-MCP-Server`, `alpacahq--alpaca-mcp-server`, `labeveryday--mcp_pdf_reader`]
- Pydantic v2 + pydantic-settings for typed config [`DiversioTeam--clickup-mcp`]
- Pydantic 2.x (`>=2.0.0, <2.12.0`); FastMCP auto-derives from signatures [`jbeno--cursor-notebook-mcp`]
- Auto-derived JSON Schema from type hints + docstrings; `Annotated[type, Field(description=...)]` patterns; pydantic + jsonschema-path + jsonref [`jlowin--fastmcp`]
- Pydantic via FastMCP; auto-derived [`mahdin75--gis-mcp`]
- `pydantic >= 2.10.6` [`awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`]
- Hand-authored schema in custom MCP impl / low-level MCP SDK [`FuzzingLabs--mcp-security-hub`, `ktanaka101--mcp-server-duckdb`]
- Not surfaced [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`]

### Optional-extras strategy

- Per-library opt-in fan-out — 8 domain-specific extras (`administrative-boundaries`, `climate`, `ecology`, `movement`, `satellite-imagery`, `land-cover`, `visualize`, `test`) plus an `all` extra; users install only the toolchain they need [`mahdin75--gis-mcp`]
- Very broad optional-dependencies surface — `anthropic`, `azure`, `gemini`, `openai`, `apps`, `code-mode`, `tasks` — each opt-in, avoiding bloat on core install [`jlowin--fastmcp`]
- Optional `[chdb]` extra to swap in alternative engines [`ClickHouse--mcp-clickhouse`]

### Notable Python-specific dependencies

- `markdownify` (HTML→markdown) + `beautifulsoup4` (selective HTML parsing) [`awslabs--aws-documentation-mcp-server`]
- Pinned `awscli==1.44.81` (CLI tool distributed as a Python dep of the MCP server) [`awslabs--aws-api-mcp-server`]
- `lxml`, `requests`, `python-frontmatter`, `importlib_resources` (suggests embedded docs/assets) [`awslabs--aws-api-mcp-server`]
- `setuptools >= 69.0.0` as runtime dep (unusual for a hatchling-built package) [`awslabs--aws-api-mcp-server`]
- No vendor SDK (`alpaca-py`); hand-rolled HTTPS via `httpx` [`alpacahq--alpaca-mcp-server`]
- `click` for CLI orchestration around FastMCP [`alpacahq--alpaca-mcp-server`]
- Minimalist 6-runtime-dep set [`awslabs--aws-documentation-mcp-server`]
- `paramiko` as core dep — SFTP support is mainline, not optional [`jbeno--cursor-notebook-mcp`]
- Heavy geospatial deps (rasterio, fiona, geopandas) kept as core deps — prioritizes install simplicity over minimal wheel size [`mahdin75--gis-mcp`]

## TypeScript packaging

Build tooling, package managers, dev-environment opinions for Node/TS servers.

### Build tooling

- tsup-built CLI with npm `bin` entry [`GLips--Figma-Context-MCP`, `HenkDz--postgresql-mcp-server`]

### Package manager / dev opinions

- pnpm + lefthook + ESLint + Prettier — opinionated dev environment; consumers building plugins on top should expect pnpm workflows [`GLips--Figma-Context-MCP`]

## Dual-mode binaries — server + management CLI

A pattern where the same console script handles both the MCP server protocol and a separate CLI for setup and configuration. Richer than one-binary-one-purpose.

- `clickup-mcp` console script doubles as a config CLI: `set-api-key`, `check-config`, `test-connection` subcommands plus `--debug`; `rich` for terminal output [`DiversioTeam--clickup-mcp`]

## Notable structural choices

Design patterns surfacing across multiple bins that don't yet have a canonical home in the tree above.

### Capability sourcing axes

- CLI-wrapping (existing CLIs become tools) [`alexei-led--k8s-mcp-server`, `awslabs--aws-api-mcp-server`]
- SDK-wrapping (boto3 / vendor SDK) — sibling repos to [`awslabs--aws-api-mcp-server`] flagged this contrast
- Spec-generated (OpenAPI / GraphQL operations) [`alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`]
- Hand-coded tool handlers — bulk of corpus

### Safety posture

- Anti-multi-tenancy explicit in README [`awslabs--aws-api-mcp-server`]
- Mutation gated by CLI flag [`PagerDuty--pagerduty-mcp-server`]
- Sandbox/paper mode by default [`alpacahq--alpaca-mcp-server`]
- Read-only design [`ahmedmustahid--postgres-mcp-server`, `awslabs--aws-documentation-mcp-server`]
- Experimental-tool feature-flagging [`awslabs--aws-api-mcp-server`]
- Tool consolidation as a deliberate response to LLM discovery / parameter-validation pressure (46 atomic → 17 meta-tools) [`HenkDz--postgresql-mcp-server`]

### Operational concerns

- Corporate proxy support (User-Agent override env var) [`awslabs--aws-documentation-mcp-server`]
- Partition-scoped tool surface (same binary, different tools depending on AWS partition) [`awslabs--aws-documentation-mcp-server`]
- HTTP session statefulness as an explicit design axis [`ahmedmustahid--postgres-mcp-server`]
- Graceful shutdown / error handling highlighted [`ahmedmustahid--postgres-mcp-server`]

### Path-traversal defense

- Workspace-root enforcement via `os.path.realpath`; `--allow-root` required for local-path access [`jbeno--cursor-notebook-mcp`]

### Connection lifecycle as user-visible knob

- `--keep-connection` flag enables TEMP objects across calls — deliberate session-state trade-off [`ktanaka101--mcp-server-duckdb`]
- Session-singleton toggle reuses one client across tool calls for connection pooling [`lanbaoshen--mcp-jenkins`]

### Cross-platform parity

- Dual-platform shell scripts (`.sh` + `.ps1`) — Windows parity is explicit, not afterthought [`jbeno--cursor-notebook-mcp`]
- Makefile for cross-platform build automation [`korotovsky--slack-mcp-server`]

## Unanticipated axes (for merger to consider)

Design decisions surfaced by 1-2 bins that may emerge as load-bearing axes once more bins are merged.

### Dual SDK dependency

- One server pulling both `mcp` and `fastmcp` [`awslabs--aws-api-mcp-server`]
- Both `fastmcp >= 2.7.0, < 2.11` and `mcp >= 0.1.0` (migration shim) [`jbeno--cursor-notebook-mcp`]

### Operation-driven tool catalog

- GraphQL operations as MCP tool declarations [`apollographql--apollo-mcp-server`]

### Smithery-only distribution

- Without PyPI publication [`JackKuo666--PubMed-MCP-Server`]

### Windows `.exe` distribution via `uv tool run`

- [`awslabs--aws-documentation-mcp-server`]

### Pinned-CLI-version-as-MCP-dependency

- `awscli==1.44.81` shipped as a Python dependency [`awslabs--aws-api-mcp-server`]

### asdf-based Python version pinning

- Rare compared to uv-native or `.python-version` [`PagerDuty--pagerduty-mcp-server`]

### Python 3.13+ floor

- Unusually high floor for April 2026 work [`alexei-led--k8s-mcp-server`]

### CORS at MCP layer

- HTTP-transport-specific config; rare [`ahmedmustahid--postgres-mcp-server`]

### `.claude/` + `CLAUDE.md` in-repo

- Claude-assisted authoring surface for contributors, distinct from a Claude Code plugin wrapper [`apollographql--apollo-mcp-server`]

### Rust as an MCP-server language

- Different distribution channels: crates.io, binary releases, Docker [`apollographql--apollo-mcp-server`]

### Remote-filesystem MCP (over SFTP)

- MCP server is local but operates on remote files over SFTP — distinct from HTTP/REST remote access [`jbeno--cursor-notebook-mcp`]

### Bundled AI-guidance content as files

- `cursor_rules.md` / `llms.txt` / `llms-full.txt` shipped alongside server — neither MCP tool nor prompt, just LLM-readable guidance [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `mahdin75--gis-mcp`]

### Multi-token-type auth as flexibility

- Four Slack token types within one server — multiple auth mechanisms covering stealth mode and OAuth [`korotovsky--slack-mcp-server`]

### Per-request HTTP-header credentials

- Header-based credential passthrough turning single-tenant stdio server into multi-tenant HTTP service [`lanbaoshen--mcp-jenkins`]

### REST endpoints alongside MCP tools

- File-transfer REST endpoints (`/storage/upload`, `/storage/download`, `/storage/list`) for binary artifacts MCP isn't built for [`mahdin75--gis-mcp`]

### Massive cross-library tool fan-out

- 92 tools wrapping 5+ Python libraries into one "GIS Swiss army knife" MCP surface [`mahdin75--gis-mcp`]

### Bare-script server

- "Script as a server" pattern (`python <script>.py`) competes with console-script-PyPI as a simpler distribution tier [`labeveryday--mcp_pdf_reader`]

### System-tool dependency

- Tesseract OCR install required out-of-band on host — server cannot self-install (similar to ffmpeg servers) [`labeveryday--mcp_pdf_reader`]

### Zero-auth file-processing family

- Distinct family of MCP servers operating on local file inputs without any auth [`labeveryday--mcp_pdf_reader`]

### "Apps" pillar

- FastMCP's third pillar (Servers, Clients, Apps) extends MCP into UI territory beyond the standard tool/resource/prompt triad [`jlowin--fastmcp`]

### Self-claimed ecosystem centrality

- "Powers 70% of MCP servers across all languages" — market self-assessment worth noting as ecosystem signal [`jlowin--fastmcp`]

### Hackathon-winning auto-complexity heuristic

- Query routed to one of three backend models without explicit caller selection [`DaInfernalCoder--perplexity-mcp`]

### Marketing framing shaping tool surface

- Figma server positioned as design-to-code accelerator rather than general Figma CRUD server — shapes the tool surface (read-only, no writes) [`GLips--Figma-Context-MCP`]

### Contribution scaffolding

- `Dockerfile.template` as a first-class contribution surface for adding new servers to a monorepo [`FuzzingLabs--mcp-security-hub`]

