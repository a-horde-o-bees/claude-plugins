# Sample

Stage-2 T1 merge of m1 (bins 1+2+7) + m4 (bins 6+10), 40 samples total.

## Identification

Per-repo metadata that situates each sample in the corpus — origin, popularity, license posture, lifecycle status, default branch, authorship, vendor relationship.

### Vendor posture

How the project's relationship to its underlying service shapes the server.

#### First-party vendor

Server is published by the same organization that owns the underlying service or product.

- PayPal `@paypal/mcp` under paypal-org npm namespace, Apache-2.0; first-party canonical despite low star count [`paypal--paypal-mcp-server`]
- Perplexity AI `@perplexity-ai/mcp-server` from `ppl-ai` GitHub org (org slug differs from brand name) [`ppl-ai--modelcontextprotocol`]
- Qdrant `mcp-server-qdrant` on PyPI as official-vendor build [`qdrant--mcp-server-qdrant`]
- Redis `redis-mcp-server` as official Redis MCP [`redis--mcp-redis`]
- Sentry `@sentry/mcp-server` plus hosted `mcp.sentry.dev` endpoint [`getsentry--sentry-mcp`]
- GitHub `github/github-mcp-server` plus hosted `api.githubcopilot.com` endpoint [`github--github-mcp-server`]
- Riza for Riza code-interpreter service [`riza-io--riza-mcp`]
- Google `googleapis/mcp-toolbox` (database toolbox) [`googleapis--mcp-toolbox`]
- Vendor-authored official organization repos — [`PagerDuty--pagerduty-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`], [`Azure--azure-mcp`], [`ClickHouse--mcp-clickhouse`]

#### Third-party / community

Server is published by an unrelated developer wrapping a vendor's API or SDK.

- "Wrap an existing community SDK" pattern — uses `zenpy` rather than direct Zendesk REST [`reminia--zendesk-mcp-server`]
- Community-maintained for an open ecosystem (Kubernetes); CNCF Landscape listed [`rohitg00--kubectl-mcp-server`]
- Third-party Go wrapper for Linear API [`geropl--linear-mcp-go`]
- Community (no SQLite vendor relationship) [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Community Clojure implementation [`hugoduncan--mcp-clj`]
- Community-built cloud SaaS over GitHub [`idosal--git-mcp`]
- Community wrapper over Microsoft Planetary Computer STAC API [`isaaccorley--planetary-computer-mcp`]
- Community / individual maintainer — [`JackKuo666--PubMed-MCP-Server`], [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`], [`DiversioTeam--clickup-mcp`], [`FuzzingLabs--mcp-security-hub`], [`GLips--Figma-Context-MCP`], [`HenkDz--postgresql-mcp-server`], [`AlwaysSany--deepl-fastmcp-python-server`], [`DaInfernalCoder--perplexity-mcp`]
- Dominant community server effectively canonical despite being unofficial — no first-party figma-org repo surfaced [`GLips--Figma-Context-MCP`]

#### No vendor relationship

- Operates over local archives — no vendor relationship at all (sidesteps vendor dimension) [`pragmar--mcp-server-webcrawl`]

> Cross-bin observation: low star count on first-party vendor releases ("official but unpromoted") — paypal-mcp at 9 stars, riza-mcp at 14 — is a recurring pattern [`paypal--paypal-mcp-server`, `riza-io--riza-mcp`].

### Repo lifecycle status

Active vs archived/redirected. The corpus contains living projects and frozen-with-redirect repos that point at successor monorepos.

- Two-stage archival pattern — code freeze months before formal GitHub archival; README declares earlier archival date than the org-level archived flag [`Azure--azure-mcp`]
- Successor-redirect via umbrella monorepo — org collapses per-domain MCP repos into a single company-wide MCP monorepo with shared core libraries, inverse of the per-service published-package strategy [`Azure--azure-mcp`]

### License distribution

Licenses observed: MIT predominates, Apache-2.0 next, AGPLv3 and Creative Commons NonCommercial uncommon.

- MIT — [`ClickHouse--mcp-clickhouse`], [`JackKuo666--PubMed-MCP-Server`], [`ahmedmustahid--postgres-mcp-server`], [`alexei-led--k8s-mcp-server`], [`alpacahq--alpaca-mcp-server`], [`apollographql--apollo-mcp-server`], [`jparkerweb--mcp-sqlite`], [`korotovsky--slack-mcp-server`], [`ktanaka101--mcp-server-duckdb`], [`labeveryday--mcp_pdf_reader`], [`lanbaoshen--mcp-jenkins`], [`mahdin75--gis-mcp`]
- Apache-2.0 — [`ClickHouse--mcp-clickhouse`], [`PagerDuty--pagerduty-mcp-server`], [`awslabs--aws-api-mcp-server`], [`awslabs--aws-documentation-mcp-server`], [`jlowin--fastmcp`], [`paypal--paypal-mcp-server`]
- AGPLv3 — copyleft implications for hosts embedding the server [`HenkDz--postgresql-mcp-server`]
- Creative Commons NonCommercial (`CC BY-NC-SA 4.0`) — restricts commercial adoption [`jbeno--cursor-notebook-mcp`]
- License content frequently not surfaced ([`getsentry--sentry-mcp`], [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`])

### Default branch

- `main` — dominant [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `mahdin75--gis-mcp`]
- `master` — still in active use [`alexei-led--k8s-mcp-server`, `korotovsky--slack-mcp-server`, `lanbaoshen--mcp-jenkins`]

### Star-count vs engineering-quality skew

Star count is not a proxy for engineering quality. A 3-star repo can carry 62 pytest tests and full ruff/mypy/CLI ergonomics [`DiversioTeam--clickup-mcp`], while large-community repos may leave testing/CI specifics unsurfaced. Read engineering rigor from artifacts (test count, lint config, CI presence), not popularity.

## Language and runtime

The implementation language plus the MCP SDK or framework variant. These two choices co-determine packaging, async semantics, and the surface available to consumers.

### Language

- Python — dominant [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`, `FuzzingLabs--mcp-security-hub`, `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`, `isaaccorley--planetary-computer-mcp`, `pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `rohitg00--kubectl-mcp-server`]
- TypeScript / JavaScript / Node.js — [`HenkDz--postgresql-mcp-server`, `GLips--Figma-Context-MCP`, `DaInfernalCoder--perplexity-mcp`, `ahmedmustahid--postgres-mcp-server` (with secondary `pyproject.toml` of unclear purpose), `jparkerweb--mcp-sqlite`, `getsentry--sentry-mcp` (TS 98.3% pnpm + Turbo), `idosal--git-mcp` (TS/JS Cloudflare Workers + React Router 7), `ppl-ai--modelcontextprotocol` (TS 95.2%), `paypal--paypal-mcp-server` (75.7% JS / 15.8% TS), `riza-io--riza-mcp` (72.2% JS / 27.8% TS)]
- Rust — [`apollographql--apollo-mcp-server`]
- Go — [`korotovsky--slack-mcp-server`, `github--github-mcp-server` (custom Go MCP impl), `googleapis--mcp-toolbox` (custom Go), `geropl--linear-mcp-go` (mark3labs/mcp-go SDK; Go 1.23+)]
- C# / .NET — uncommon; .NET-based MCP servers often live in umbrella monorepos with shared C# core libraries [`Azure--azure-mcp`]
- Clojure — 99.7% Clojure on Java runtime against MCP version `2024-11-05` using only Clojure standard library [`hugoduncan--mcp-clj`]

### Polyglot wrapper

- Python core (81.2%) with TypeScript npm wrapper (17.0%) for dual-ecosystem distribution [`rohitg00--kubectl-mcp-server`]
- Co-located VS Code extension (TS 11.3%) parallel to Python MCP server [`isaaccorley--planetary-computer-mcp`]

### Python version floor

- `>=3.6` — pre-`pyproject.toml`-era project, unusually low [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- `>=3.9` — [`rohitg00--kubectl-mcp-server`]
- `>=3.10` is the modal floor [`ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`, `JackKuo666--PubMed-MCP-Server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`, `pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`]
- `>=3.12` — [`reminia--zendesk-mcp-server`]
- `>=3.13` — unusually high floor [`alexei-led--k8s-mcp-server`]
- Aggressive specific pin — `runtime.txt` pinning Python 3.13.3 finer-grained than typical [`AlwaysSany--deepl-fastmcp-python-server`]
- `.python-version` file (pyenv-style) — [`JackKuo666--PubMed-MCP-Server`, `isaaccorley--planetary-computer-mcp`, `qdrant--mcp-server-qdrant`]
- `.python-version` present without explicit floor in pyproject [`labeveryday--mcp_pdf_reader`]
- `.tool-versions` (asdf) — rarer than uv-native or `.python-version` [`PagerDuty--pagerduty-mcp-server`]
- `requires-python` in pyproject.toml — [`alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`]
- Floor not surfaced — [`lanbaoshen--mcp-jenkins`]

### Node version floor

- `>=14.0.0` [`jparkerweb--mcp-sqlite`]
- Specific Node version constraints often unspecified across other Node samples

### Go version

- `1.21+` inferred from go.mod features [`korotovsky--slack-mcp-server`]
- Go 1.23+ via `mcp-go` SDK [`geropl--linear-mcp-go`]

## Framework / SDK

Which MCP wrapper or SDK the server builds on, and how that choice shapes async semantics, schema derivation, and CLI surface.

### FastMCP framework (Python)

FastMCP is a higher-level Python SDK that auto-derives schemas from function signatures and handles the async boundary internally. Self-claims to power "70% of MCP servers across all languages" [`jlowin--fastmcp`].

#### FastMCP 1.x (pre-2.x)

- `fastmcp == 0.4.1` pinned, Python 3.6+ floor — pre-`pyproject.toml`-era reference case for "how the FastMCP ecosystem looked before the 2.0 split" [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]

#### FastMCP 2.x

- `fastmcp >= 2.0.0, < 3.0.0` pin and `fastmcp.json` for native config [`ClickHouse--mcp-clickhouse`]
- `fastmcp == 2.7.0` exact pin — sensitive to FastMCP API drift [`qdrant--mcp-server-qdrant`]
- FastMCP standalone-package style, version not pinned precisely [`AlwaysSany--deepl-fastmcp-python-server`, `JackKuo666--PubMed-MCP-Server`]
- `fastmcp >= 2.0.0` [`alpacahq--alpaca-mcp-server`]
- `fastmcp >= 2.7.0, < 2.11` — narrow window guarding against FastMCP 2.11 breaking changes [`jbeno--cursor-notebook-mcp`]
- `fastmcp == 2.13.1` exact pin — conservative against API drift [`mahdin75--gis-mcp`]
- Version not pinned precisely; `pip install fastmcp` [`labeveryday--mcp_pdf_reader`]
- FastMCP (major version unsurfaced) [`rohitg00--kubectl-mcp-server`]

#### FastMCP 3.x alongside raw mcp

- `fastmcp >= 3.0.1` **alongside** raw `mcp >= 1.23.0` — one server bridging two SDK generations [`awslabs--aws-api-mcp-server`]

#### Dual MCP-framework declarations (migration shim)

- Both `fastmcp >= 2.7.0, < 2.11` and `mcp >= 0.1.0` declared as deps — migration / compatibility shim [`jbeno--cursor-notebook-mcp`]

#### FastMCP itself

- `jlowin--fastmcp` is the framework, not a server. Wraps and was absorbed into the official MCP Python SDK in 2024. Three-pillar model: Servers, Clients, Apps. Decorator-based API (`@mcp.tool`, etc.) is the canonical Python authoring path [`jlowin--fastmcp`]

### Raw MCP Python SDK

Direct use of the official Python `mcp` package without a higher-level wrapper.

- Very loose pin (`mcp >= 0.1.0`) — unusual; most projects pin much tighter [`DiversioTeam--clickup-mcp`]
- `mcp >= 1.0.0`; low-level server API; hand-authored schemas [`ktanaka101--mcp-server-duckdb`]
- Raw MCP SDK with no FastMCP reference [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `lanbaoshen--mcp-jenkins`]
- `mcp[cli] >= 1.23.0` [`awslabs--aws-documentation-mcp-server`]
- `mcp[cli] >= 1.26.0` [`redis--mcp-redis`]
- `mcp >= 1.3.0` (no `[cli]` extra) [`pragmar--mcp-server-webcrawl`]
- `mcp >= 1.1.2` (no `[cli]` extra); minimal 3-deps stack [`reminia--zendesk-mcp-server`]
- Raw `mcp` SDK as 2026 holdout — many newer servers have migrated to FastMCP [`isaaccorley--planetary-computer-mcp`]

### Hand-rolled MCP implementation

Custom MCP wire-protocol implementation, opting out of FastMCP and the official Python SDK.

- 38 servers each carrying a hand-rolled MCP implementation wrapping a security CLI tool — stdin/stdout JSON-RPC was simple enough that the SDKs added no value [`FuzzingLabs--mcp-security-hub`]
- Hand-rolled Clojure MCP stack on `org.clojure/data.json` only [`hugoduncan--mcp-clj`]

### Anthropic MCP TypeScript SDK

The canonical `@modelcontextprotocol/sdk` TypeScript package.

- TypeScript 96.6%, tsup-built CLI, Anthropic MCP TypeScript SDK [`HenkDz--postgresql-mcp-server`]
- TypeScript 96.3%, tsup build, MCP SDK plus pnpm + lefthook + ESLint + Prettier opinionated dev environment [`GLips--Figma-Context-MCP`]
- `@modelcontextprotocol/sdk ^1.12.1` [`jparkerweb--mcp-sqlite`]
- `StreamableHTTPServerTransport`, `StdioServerTransport` use [`ahmedmustahid--postgres-mcp-server`]
- Standard MCP TypeScript SDK — [`paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `getsentry--sentry-mcp` (inferred), `idosal--git-mcp`]

### MCP SDK + Anthropic Claude Agent SDK combination

JavaScript with both the MCP SDK and the Anthropic Claude Agent SDK in use [`DaInfernalCoder--perplexity-mcp`].

### Rust MCP implementation

- Rust MCP implementation in the Apollo GraphQL ecosystem [`apollographql--apollo-mcp-server`]

### Go MCP implementations

- `mark3labs/mcp-go` canonical [`geropl--linear-mcp-go`]
- Custom Go MCP implementation, `server.json` declares MCP capability [`github--github-mcp-server`, `googleapis--mcp-toolbox`]
- No standard Go MCP framework; custom MCP implementation [`korotovsky--slack-mcp-server`]

## Transport

How the MCP server speaks to its host. Servers diverge on which transports they support and how the transport is selected at launch.

### Single-transport — stdio only

Default for many servers; no alternative transport documented.

- [`HenkDz--postgresql-mcp-server`, `DiversioTeam--clickup-mcp`, `FuzzingLabs--mcp-security-hub`, `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server` (FastMCP CLI installer wires stdio with no flag), `isaaccorley--planetary-computer-mcp`, `paypal--paypal-mcp-server` (default via npx), `redis--mcp-redis` (README notes "streamable-http transport will be added in the future"), `reminia--zendesk-mcp-server`, `geropl--linear-mcp-go` (via `serve` subcommand), `github--github-mcp-server` (via `stdio` subcommand)]

### stdio + HTTP variants (multi-transport)

A single binary supporting multiple transports.

- stdio + Streamable HTTP — [`alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `ahmedmustahid--postgres-mcp-server`] (HTTP is default; stdio via subcommand)
- stdio + Streamable HTTP + SSE — [`jbeno--cursor-notebook-mcp`, `mahdin75--gis-mcp`, `alexei-led--k8s-mcp-server`] (SSE deprecated in alexei-led)
- stdio + SSE + HTTP — [`korotovsky--slack-mcp-server`]
- stdio + SSE + streamable-http (default port 9887) — [`lanbaoshen--mcp-jenkins`]
- stdio + HTTP at framework level — [`jlowin--fastmcp`]
- stdio (default) + sse + streamable-http via FastMCP env-driven selection — [`qdrant--mcp-server-qdrant`]
- stdio (default) + SSE + streamable-http + HTTP, default `0.0.0.0:8000` for HTTP modes — [`rohitg00--kubectl-mcp-server`]
- stdio default + HTTP server mode via `PORT` and `BIND_ADDRESS` env vars plus CORS — [`ppl-ai--modelcontextprotocol`]
- stdio + SSE/HTTP via `clj -M:sse-server` profile (default port 3001) — [`hugoduncan--mcp-clj`]
- stdio + `--interactive` REPL flag for terminal mode — [`pragmar--mcp-server-webcrawl`]

### HTTP-first transport (diverging from stdio convention)

- HTTP-first on port 5000 at `/mcp` endpoint — [`googleapis--mcp-toolbox`]
- HTTP/HTTPS only via cloud endpoint `gitmcp.io`, plus SSE; auto-detected by IDE via direct HTTP URL specification — [`idosal--git-mcp`]
- HTTP via remote service `https://mcp.sentry.dev` — [`getsentry--sentry-mcp`]
- Separately-hosted remote service at `api.githubcopilot.com` — [`github--github-mcp-server`]

### Transport polyglot — three transports in one binary

stdio + SSE + Streamable HTTP all in one binary, CLI- or env-selectable. Transport breadth in small community servers can exceed that of vendor-authored servers [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`].

### In-memory transport

Unusual; flagged as a notable axis.

- In-memory transport explicitly for testing — [`hugoduncan--mcp-clj`]

### Transport selection mechanism

#### CLI flag selection

- `--transport stdio|sse|http` plus `--host`, `--port` args [`AlwaysSany--deepl-fastmcp-python-server`]
- CLI flag selection [`alpacahq--alpaca-mcp-server`, `alexei-led--k8s-mcp-server`, `awslabs--aws-api-mcp-server`, `lanbaoshen--mcp-jenkins`]
- CLI flags (`--host`, `--port`) plus inference from host JSON config [`jbeno--cursor-notebook-mcp`]

#### CLI subcommand or profile selection

- `serve` / `setup --tool=cline` / `version` subcommands [`geropl--linear-mcp-go`]
- `github-mcp-server stdio` subcommand [`github--github-mcp-server`]
- `clj -M:stdio-server` / `clj -M:sse-server [--port 8080]` profiles [`hugoduncan--mcp-clj`]

#### Environment variable selection

- `CLICKHOUSE_MCP_SERVER_TRANSPORT=stdio|http|sse` [`ClickHouse--mcp-clickhouse`]
- `SLACK_MCP_TRANSPORT` (default stdio) [`korotovsky--slack-mcp-server`]
- `GIS_MCP_TRANSPORT` [`mahdin75--gis-mcp`]
- FastMCP env-driven selection [`qdrant--mcp-server-qdrant`]

#### Mixed flag + env

- `--stdio` flag selects stdio mode; omission plus a `PORT` env var selects HTTP mode [`GLips--Figma-Context-MCP`]

#### Positional subcommand

- `npx ... stdio` switches from default HTTP to stdio [`ahmedmustahid--postgres-mcp-server`]

#### Configuration file

- Configuration file driven [`apollographql--apollo-mcp-server`]

#### Implicit / default

- Stdio implicit / default [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- IDE auto-detection from URL string [`idosal--git-mcp`]
- HTTP default with no per-mode subcommand [`googleapis--mcp-toolbox`]

#### Programmatic

- Programmatic via `mcp.run()` signature in consumer code [`jlowin--fastmcp`]

### Default ports for HTTP

- 9887 [`lanbaoshen--mcp-jenkins`]
- 9010 (HTTP via Docker) [`mahdin75--gis-mcp`]
- 13080 [`korotovsky--slack-mcp-server`]
- 8080 / `127.0.0.1:8080/mcp` host-config example [`jbeno--cursor-notebook-mcp`]
- 5000 at `/mcp` [`googleapis--mcp-toolbox`]
- 3001 default (customizable via `--port`) [`hugoduncan--mcp-clj`]
- 8000 default for HTTP modes (`0.0.0.0:8000`) [`rohitg00--kubectl-mcp-server`]

### Transport not documented

- [`riza-io--riza-mcp`]

## Distribution

Mechanisms by which end users obtain and run the server. Most servers offer multiple channels; the dominant choice depends on language ecosystem and target audience.

### PyPI publication

Python servers publish to PyPI as the canonical install path.

- `pip install mcp-clickhouse`; optional extras like `[chdb]` swap in alternative engines [`ClickHouse--mcp-clickhouse`]
- `pip install mcp-server-webcrawl` only path; pip-only [`pragmar--mcp-server-webcrawl`]
- `pip install kubectl-mcp-server[ui]` — extras-gated UI bundle [`rohitg00--kubectl-mcp-server`]
- PyPI / `uvx` — [`PagerDuty--pagerduty-mcp-server` (`pagerduty-mcp`), `alpacahq--alpaca-mcp-server` (`alpaca-mcp-server`), `awslabs--aws-api-mcp-server` (`awslabs.aws-api-mcp-server`), `awslabs--aws-documentation-mcp-server` (`awslabs.aws-documentation-mcp-server`), `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`]
- `uvx mcp-server-qdrant` [`qdrant--mcp-server-qdrant`]
- `uvx --from redis-mcp-server@latest redis-mcp-server`; also `uvx --from git+https://...` for direct GitHub install [`redis--mcp-redis`]

### npm / npx

Node servers distribute via npm and the npx one-shot runner.

- `npx -y figma-developer-mcp ...` [`GLips--Figma-Context-MCP`]
- `npx -y perplexity-mcp` [`DaInfernalCoder--perplexity-mcp`]
- `npm install -g @henkey/postgres-mcp-server` plus `npx` [`HenkDz--postgresql-mcp-server`]
- `npx -y mcp-sqlite <database-path>` direct invocation without intermediate config [`jparkerweb--mcp-sqlite`]
- npm (`npx`) [`ahmedmustahid--postgres-mcp-server` (`@ahmedmustahid/postgres-mcp-server`)]
- `@sentry/mcp-server` via `npx @sentry/mcp-server@latest` [`getsentry--sentry-mcp`]
- `npx -y @paypal/mcp --tools=all` [`paypal--paypal-mcp-server`]
- `npx -y @perplexity-ai/mcp-server` [`ppl-ai--modelcontextprotocol`]
- `npx @riza-io/riza-mcp` [`riza-io--riza-mcp`]
- `npx -y kubectl-mcp-server` (npm wrapper invokes Python package) [`rohitg00--kubectl-mcp-server`]

### `uv run` / `uvx` with on-demand install

Python servers leverage `uv` to fetch and run without explicit install.

- `uv run --with mcp-clickhouse --python 3.10 mcp-clickhouse` — uv-run with on-demand install and pinned Python [`ClickHouse--mcp-clickhouse`]
- `uvx --from git+https://github.com/...` — install-from-git URL bypasses PyPI entirely [`DiversioTeam--clickup-mcp`]
- `uv pip install <package>` [`jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `mahdin75--gis-mcp`]
- `uv sync` + `uv run python <script>.py` (clone-then-run) [`labeveryday--mcp_pdf_reader`, `isaaccorley--planetary-computer-mcp`]
- `uv --directory /path/to/repo run zendesk` (host invocation against editable install) [`reminia--zendesk-mcp-server`]

### Docker / container images

Docker as the primary or alternative distribution channel.

- Dockerfile + docker-compose.yml — SSE/HTTP transports motivate multi-container orchestration [`AlwaysSany--deepl-fastmcp-python-server`]
- Published Docker Hub image alongside npm/Smithery [`HenkDz--postgresql-mcp-server`]
- Multi-stage Node 18-Alpine Dockerfile [`DaInfernalCoder--perplexity-mcp`]
- Docker-only distribution (no PyPI/npm) — Docker image is the unit of packaging [`FuzzingLabs--mcp-security-hub`]
- Docker / OCI image — [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alexei-led--k8s-mcp-server` (ghcr.io), `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `awslabs--aws-api-mcp-server` (AWS public ECR), `awslabs--aws-documentation-mcp-server`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- Podman (alongside Docker) [`ahmedmustahid--postgres-mcp-server`]
- GHCR `ghcr.io/github/github-mcp-server` — `docker run` is canonical install path, not `go install` [`github--github-mcp-server`]
- Artifact Registry `us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:$VERSION` [`googleapis--mcp-toolbox`]
- Docker Hub `rohitghumare64/kubectl-mcp-server:latest` [`rohitg00--kubectl-mcp-server`]
- Dockerfile present [`geropl--linear-mcp-go`, `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`]
- Dockerfile installs from `requirements.lock` for build reproducibility [`reminia--zendesk-mcp-server`]
- `docker build -t mcp-redis .` [`redis--mcp-redis`]

### Container registry

- Docker Hub or unspecified — [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-documentation-mcp-server`, `rohitg00--kubectl-mcp-server`]
- ghcr.io (GitHub Container Registry) — [`alexei-led--k8s-mcp-server`, `lanbaoshen--mcp-jenkins`, `github--github-mcp-server`]
- AWS public ECR — [`awslabs--aws-api-mcp-server`]
- Google Artifact Registry — [`googleapis--mcp-toolbox`]
- Built via release-container GitHub Actions workflow — [`apollographql--apollo-mcp-server`]

### Smithery registry

Smithery as a discovery/distribution channel, layered on top of npm.

- `npx -y @smithery/cli install @HenkDz/postgresql-mcp-server` [`HenkDz--postgresql-mcp-server`]
- `smithery.yaml` in repo root signals Smithery integration [`DaInfernalCoder--perplexity-mcp`, `mahdin75--gis-mcp`, `JackKuo666--PubMed-MCP-Server`]
- Smithery installer (`npx @smithery/cli install …`) [`ktanaka101--mcp-server-duckdb`]
- Smithery-only distribution without PyPI publication — package manager path is optional when a curator like Smithery handles install [`JackKuo666--PubMed-MCP-Server`]
- One-click install for Claude Desktop [`qdrant--mcp-server-qdrant`]

### Cargo / GitHub binary releases

- Cargo crate / GitHub binary releases [`apollographql--apollo-mcp-server`]
- GitHub Releases pre-built binaries — [`geropl--linear-mcp-go`], [`github--github-mcp-server`] (58 releases), [`googleapis--mcp-toolbox`] (Linux AMD64, macOS ARM64/Intel, Windows AMD64)
- `go install` — [`geropl--linear-mcp-go`, `googleapis--mcp-toolbox`]
- Shell download script (automated download) — [`geropl--linear-mcp-go`]

### Homebrew

- `brew install mcp-toolbox` [`googleapis--mcp-toolbox`]

### Windows `.exe` distribution

- `uv tool run --from <pkg>@latest <pkg>.exe` [`awslabs--aws-documentation-mcp-server`]

### Cloud-hosted SaaS endpoint

- `gitmcp.io/{owner}/{repo}` — parameterized repository endpoints, one deployment serves every GitHub repo [`idosal--git-mcp`]
- `mcp.sentry.dev` [`getsentry--sentry-mcp`]
- `api.githubcopilot.com` [`github--github-mcp-server`]

### Source clone / clone-and-run

Always available; sometimes the only path when no package is published.

- `git clone ... && uv sync` [`AlwaysSany--deepl-fastmcp-python-server`]
- `git clone` + `pip install -r requirements.txt` / `uv sync` / `cargo build` [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `apollographql--apollo-mcp-server`]
- No PyPI publication — clone-and-run consumption [`labeveryday--mcp_pdf_reader`]
- `go run <main>.go --transport stdio` source build [`korotovsky--slack-mcp-server`]
- `fastmcp install sqlite_explorer.py` source-script install [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- `pnpm install` source build [`idosal--git-mcp`]
- Git dependency in `deps.edn` [`hugoduncan--mcp-clj`]

### Editable-install-only ("developer-mode-as-release")

- No PyPI release; `uv venv && uv pip install -e .` is the user path [`reminia--zendesk-mcp-server`]

### Pre-`pyproject.toml` packaging

- `requirements.txt` + single `sqlite_explorer.py` script + no packaging. No `[project.scripts]`, no PyPI publish [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]

### Marketplace plugin (Claude Desktop)

- [`getsentry--sentry-mcp`] vends both an npm package and a Claude marketplace plugin distinct from the raw JSON snippet

### Multi-channel breadth

- 5 distribution channels (binary, Docker, go install, Homebrew, npm shim) — cross-ecosystem discoverability as a deliberate goal [`googleapis--mcp-toolbox`]
- Both npm package and Claude marketplace plugin [`getsentry--sentry-mcp`]

### Cross-ecosystem glue

- NPM shim wrapping a Go binary — `@toolbox-sdk/server` (npm) wraps the Go binary so node-oriented hosts can run a Go server by name [`googleapis--mcp-toolbox`]
- NPM shim wrapping a Python package — kubectl-mcp-server ships under both PyPI and npm; allows npm-only hosts to install without Python packaging knowledge [`rohitg00--kubectl-mcp-server`]

### Hosted vs local

A clear axis. [`idosal--git-mcp`] is hosted-only (no local install, zero-auth cloud service). [`getsentry--sentry-mcp`] and [`github--github-mcp-server`] are dual-mode: official remote endpoint operated by the vendor alongside a self-run stdio binary. [`geropl--linear-mcp-go`], [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`], [`hugoduncan--mcp-clj`], [`isaaccorley--planetary-computer-mcp`], plus most local-install samples are local-only.

## Entry point / launch

How the server process is started by the host.

### Console script via package metadata

The conventional path: `[project.scripts]` or npm `bin` registers a name on PATH.

- `mcp-clickhouse = "mcp_clickhouse.main:main"` [`ClickHouse--mcp-clickhouse`]
- `clickup-mcp = clickup_mcp.__main__:main` — `__main__.py`-based entry [`DiversioTeam--clickup-mcp`]
- npm `bin` entry pointing at tsup-built CLI [`GLips--Figma-Context-MCP`, `HenkDz--postgresql-mcp-server`]
- `[project.scripts]` console scripts: `alpaca-mcp-server` → `alpaca_mcp_server.cli:main` [`alpacahq--alpaca-mcp-server`]; `awslabs.aws-api-mcp-server` → `awslabs.aws_api_mcp_server.server:main` [`awslabs--aws-api-mcp-server`]; `awslabs.aws-documentation-mcp-server` → `awslabs.aws_documentation_mcp_server.server:main` [`awslabs--aws-documentation-mcp-server`]
- `cursor-notebook-mcp` (also `python -m cursor_notebook_mcp.server`) [`jbeno--cursor-notebook-mcp`]
- `mcp-server-duckdb` registered to `mcp_server_duckdb:main` [`ktanaka101--mcp-server-duckdb`]
- `mcp-jenkins` console script [`lanbaoshen--mcp-jenkins`]
- `gis-mcp` (also `python -m gis_mcp`) [`mahdin75--gis-mcp`]
- `mcp-sqlite-server` (CommonJS, package.json `bin`) [`jparkerweb--mcp-sqlite`]
- `mcp-server-webcrawl = "mcp_server_webcrawl:main"` [`pragmar--mcp-server-webcrawl`]
- `mcp-server-qdrant` console script → `mcp_server_qdrant.main:main` [`qdrant--mcp-server-qdrant`]
- `redis-mcp-server = "src.main:cli"`; unusual `src.` prefix in module path [`redis--mcp-redis`]
- `zendesk` console script → `zendesk_mcp_server:main`; unusually short script name [`reminia--zendesk-mcp-server`]
- `kubectl-mcp-server` console script [`rohitg00--kubectl-mcp-server`]

### Subcommand-based binary

- `serve`, `setup --tool=cline`, `version` subcommands [`geropl--linear-mcp-go`]
- `stdio` subcommand at `cmd/github-mcp-server/` [`github--github-mcp-server`]

### Profile-based (Clojure deps)

- `clj -M:stdio-server` / `clj -M:sse-server` / `clj -M:sse-server --port 8080` [`hugoduncan--mcp-clj`]

### Python `-m` module entry

- `python -m <pkg>` [`PagerDuty--pagerduty-mcp-server`, `awslabs--aws-api-mcp-server` (`python -m awslabs.aws_api_mcp_server.server`), `isaaccorley--planetary-computer-mcp` (`python -m planetary_computer_mcp.server`)]

### Bare script invoked through interpreter

No console script; user invokes the script directly. "Script as a server" simpler distribution tier.

- `uv run python main.py --transport stdio` — bare `main.py` with CLI arg handling built in [`AlwaysSany--deepl-fastmcp-python-server`]
- Bare Python scripts executed via Docker entrypoint [`FuzzingLabs--mcp-security-hub`]
- `python pubmed_server.py` [`JackKuo666--PubMed-MCP-Server`]
- `python pdf_reader_server.py` directly [`labeveryday--mcp_pdf_reader`]
- `fastmcp install sqlite_explorer.py` then host-launches via configured MCP command, or direct run via `uv run --with fastmcp --with uvicorn fastmcp run /path/to/sqlite_explorer.py` [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]

### npx one-shot

Node ecosystem; package fetched and executed in one step.

- `npx -y figma-developer-mcp --figma-api-key=YOUR-KEY --stdio` [`GLips--Figma-Context-MCP`]
- `npx -y perplexity-mcp` [`DaInfernalCoder--perplexity-mcp`]
- `npx <package>` (with optional positional subcommand) [`ahmedmustahid--postgres-mcp-server`]
- `npx -y <package> <args>` direct [`jparkerweb--mcp-sqlite`]
- `npx @sentry/mcp-server@latest --access-token=...` [`getsentry--sentry-mcp`]
- `npx -y @paypal/mcp --tools=all` [`paypal--paypal-mcp-server`]
- `npx -y @perplexity-ai/mcp-server` [`ppl-ai--modelcontextprotocol`]
- `npx @riza-io/riza-mcp` [`riza-io--riza-mcp`]
- `npx -y kubectl-mcp-server` (wrapper invokes Python package) [`rohitg00--kubectl-mcp-server`]

### `uvx <package>` zero-install

- [`PagerDuty--pagerduty-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`]

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

### Wrapper scripts and setup ergonomics

- `run_tests.sh` + `run_tests.ps1` — explicit Windows parity [`jbeno--cursor-notebook-mcp`]
- Makefile (~5.7 KB) for cross-platform build automation [`korotovsky--slack-mcp-server`]
- Multi-platform Dockerfile under `/docker/` [`lanbaoshen--mcp-jenkins`]
- Two Dockerfiles — `Dockerfile` (prod) and `Dockerfile.local` (dev) [`mahdin75--gis-mcp`]
- 3 docker-compose variants — base, dev, toolkit [`korotovsky--slack-mcp-server`]
- `setup --tool=cline` subcommand automates host configuration — rare among MCP servers, most expect users to hand-edit JSON [`geropl--linear-mcp-go`]
- `--config "tools.yaml"` flag with the same binary across Docker / npm shim / native invocations [`googleapis--mcp-toolbox`]
- Monorepo workspace scripts (`pnpm -w run cli`) [`getsentry--sentry-mcp`]

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
- `LINEAR_API_KEY` (required) [`geropl--linear-mcp-go`]
- `GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_HOST`, `GITHUB_TOOLSETS`, `GITHUB_TOOLS`, `GITHUB_READ_ONLY`, `GITHUB_INSIDERS` [`github--github-mcp-server`]
- `SENTRY_ACCESS_TOKEN`, `EMBEDDED_AGENT_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SENTRY_HOST`, `MCP_DISABLE_SKILLS` [`getsentry--sentry-mcp`]
- `SQLITE_DB_PATH` (required; only config knob) [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- env-only; CLI args explicitly deprecated [`qdrant--mcp-server-qdrant`]
- env-dominant (`PERPLEXITY_API_KEY`, `PERPLEXITY_TIMEOUT_MS`, `PERPLEXITY_BASE_URL`, `PORT`, `BIND_ADDRESS`, proxy config) [`ppl-ai--modelcontextprotocol`]

### CLI flags + env vars combined

Flags override env; env overrides file in the precedence chain.

- `--api-key` CLI > `PERPLEXITY_API_KEY` env > `.env` file [`DaInfernalCoder--perplexity-mcp`]
- `--figma-api-key` flag, `FIGMA_API_KEY` env, `--stdio` mode flag, `PORT` env [`GLips--Figma-Context-MCP`]
- `--connection-string` flag, `POSTGRES_CONNECTION_STRING` env, `POSTGRES_TOOLS_CONFIG` env, optional `tools.json` file [`HenkDz--postgresql-mcp-server`]
- `--enable-write-tools` CLI flag [`PagerDuty--pagerduty-mcp-server`]
- CLI flags + env [`alexei-led--k8s-mcp-server`, `awslabs--aws-api-mcp-server`]
- env vars for credentials/environment, CLI flags for tool selection (`--tools=all`) and token override [`paypal--paypal-mcp-server`]
- env vars (`KUBECONFIG`, `MCP_DEBUG`, `MCP_LOG_FILE`, `MCP_BROWSER_*`, `MCP_AUTH_*`) plus CLI flags (`--disable-destructive`, transport/host/port) [`rohitg00--kubectl-mcp-server`]
- Three sources: CLI flags (extensive: `--url`, `--host`, `--port`, `--username`, `--password`, `--db`, `--ssl`, granular SSL knobs), env vars + `.env` files, Redis URI scheme [`redis--mcp-redis`]

### CLI flags only

- [`ktanaka101--mcp-server-duckdb`, `jparkerweb--mcp-sqlite`]
- `--write-access`, `--auto-approve`, `--tool` [`geropl--linear-mcp-go`]
- `--toolsets`, `--tools`, `--read-only`, `--lockdown-mode`, `--dynamic-toolsets` [`github--github-mcp-server`]
- `--config`, `--disable-reload` [`googleapis--mcp-toolbox`]
- `--port` [`hugoduncan--mcp-clj`]
- `--crawler`, `--datasrc`, `--interactive` [`pragmar--mcp-server-webcrawl`]

### CLI flags + host JSON config

- [`jbeno--cursor-notebook-mcp`]

### CLI flags + HTTP headers for per-request credentials

- [`lanbaoshen--mcp-jenkins`]

### `.env` file

- `.env` resolution path controllable via `--cwd` parameter [`DaInfernalCoder--perplexity-mcp`]
- `.env` file with `python-dotenv`; `.env.example` as dev-config template [`reminia--zendesk-mcp-server`]

### Persistent OS-native config via platformdirs

API key stored in OS-appropriate config dir (`~/.config/`, `%APPDATA%`, etc.) — competes with `.env` files and env vars as a third credential-storage convention.

- `set-api-key` subcommand persists via `platformdirs`; `CLICKUP_MCP_API_KEY` env var is the alternative [`DiversioTeam--clickup-mcp`]

### Per-tool config file

A separate JSON file enables/disables individual tools without code changes.

- `POSTGRES_TOOLS_CONFIG` env points at `tools.json` for per-tool enablement — explicit surface-reduction knob [`HenkDz--postgresql-mcp-server`]

### Framework-native config files

- `fastmcp.json` for FastMCP-level config [`ClickHouse--mcp-clickhouse`]

### YAML manifest

- `tools.yaml` as primary configuration surface — declares sources, tools, toolsets, and prompts. Admins configure by editing YAML rather than writing code [`googleapis--mcp-toolbox`]

### Configuration file (server-spec)

- Points at GraphQL endpoint, operation definitions, and the config file itself [`apollographql--apollo-mcp-server`]

### Host-managed JSON config

- `claude_desktop_config.json` injection (`command`/`args` absolute path) [`JackKuo666--PubMed-MCP-Server`]
- `claude_desktop_config.json` with bash interpreter, project path, and env vars in config [`hugoduncan--mcp-clj`]
- JSON `mcp.json` for 8 IDEs (Claude Desktop, Cursor, Windsurf, VSCode, Cline, Highlight AI, Augment Code, Msty AI) [`idosal--git-mcp`]
- Function-call parameters + environment [`isaaccorley--planetary-computer-mcp`]
- JSON configuration file (Claude Desktop format); env vars for API credentials [`riza-io--riza-mcp`]

### CORS configuration at the MCP layer

- `CORS_ORIGIN` env var (HTTP-transport-specific, rare) [`ahmedmustahid--postgres-mcp-server`]

### Hot reload

- Dynamic reloading on by default; `--disable-reload` opts out — implies state survives across configuration changes; unusual for MCP servers (most re-exec) [`googleapis--mcp-toolbox`]

### System-level dependency only

- Tesseract install — no runtime config surface [`labeveryday--mcp_pdf_reader`]

### Programmatic — framework consumers wire their own config

- [`jlowin--fastmcp`]

## Authentication

How callers prove identity to the server, and how the server obtains its own credentials for upstream services.

### No authentication

- DuckDB local file access [`ktanaka101--mcp-server-duckdb`]
- SQLite local file access [`jparkerweb--mcp-sqlite`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Local PDF processing [`labeveryday--mcp_pdf_reader`]
- No MCP-layer auth; downstream API keys handled per dataset [`mahdin75--gis-mcp`]
- Anonymous public-data fetching — PubMed web [`JackKuo666--PubMed-MCP-Server`]
- Public AWS docs [`awslabs--aws-documentation-mcp-server`]
- Planetary Computer STAC API publicly accessible [`isaaccorley--planetary-computer-mcp`]
- Zero-auth public-repo cloud service [`idosal--git-mcp`]
- No explicit mechanism documented; assumes transport-layer security [`hugoduncan--mcp-clj`]
- Operates entirely on local archives; no service auth at all. Demonstrates that valid MCP servers need not talk to external services [`pragmar--mcp-server-webcrawl`]

### API key / personal token (single static)

Static token supplied at launch.

- DeepL API key via `DEEPL_AUTH_KEY` env var [`AlwaysSany--deepl-fastmcp-python-server`]
- ClickUp personal API token via `set-api-key` subcommand or `CLICKUP_MCP_API_KEY` env var [`DiversioTeam--clickup-mcp`]
- Perplexity API key with CLI > env > .env precedence [`DaInfernalCoder--perplexity-mcp`]
- Figma personal access token via CLI flag or env var; no OAuth flow [`GLips--Figma-Context-MCP`]
- PagerDuty User API Token via env [`PagerDuty--pagerduty-mcp-server`]
- Alpaca API key + secret pair [`alpacahq--alpaca-mcp-server`]
- `LINEAR_API_KEY` [`geropl--linear-mcp-go`]
- `GITHUB_PERSONAL_ACCESS_TOKEN` [`github--github-mcp-server`]
- Sentry user tokens with scopes `org:read project:read project:write team:read team:write event:write` [`getsentry--sentry-mcp`]
- `PERPLEXITY_API_KEY` [`ppl-ai--modelcontextprotocol`]
- `QDRANT_API_KEY` for Qdrant Cloud or remote [`qdrant--mcp-server-qdrant`]
- `RIZA_API_KEY` env var [`riza-io--riza-mcp`]

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
- `~/.kube/config` for Kubernetes API auth [`rohitg00--kubectl-mcp-server`]

### OAuth (hosted)

- Optional OAuth on streamable-http (configurable issuer + JWKS endpoints) — only Python sample with explicit OAuth on streamable-http [`awslabs--aws-api-mcp-server`]
- OAuth for the remote hosted server (VS Code 1.101+ has native support) [`github--github-mcp-server`]
- OAuth App for the hosted `mcp.sentry.dev` endpoint [`getsentry--sentry-mcp`]

### OAuth 2.0 client credentials

- Bearer token, valid 3-8 hours sandbox / 8 hours production. Server holds single merchant's token for the session. Token-refresh handling unclear from surface — long sessions may need rotation by caller [`paypal--paypal-mcp-server`]

### OAuth 2.1 (RFC 9728) — optional bolt-on

- Optional OAuth 2.1 layer on top of stdio/HTTP via `MCP_AUTH_ENABLED`, `MCP_AUTH_ISSUER`, `MCP_AUTH_AUDIENCE` [`rohitg00--kubectl-mcp-server`]

### Per-GraphQL-endpoint auth via headers (config-file)

- Apollo Router conventions [`apollographql--apollo-mcp-server`]

### Multi-mode auth

- Four Slack token types: `XOXC` (browser), `XOXD` (cookie), `XOXP` (user OAuth), `XOXB` (bot) — flexible choice covers stealth mode and OAuth [`korotovsky--slack-mcp-server`]
- Jenkins username + password (or API token) via CLI (static) OR HTTP headers (per-request) [`lanbaoshen--mcp-jenkins`]
- SFTP/SSH key vs password vs key+interactive (`--sftp-auth-mode auto/key/password/key+interactive`) [`jbeno--cursor-notebook-mcp`]

### Per-tool auth-flow variation

Tool-suite servers carry per-tool credential needs (some tools need keys, others don't).

- API keys for Nuclei templates, none for Nmap; injected via container env [`FuzzingLabs--mcp-security-hub`]

### Delegated to underlying source auth

- Database auth schemes — IAM for Google Cloud (ambient/ADC credentials), plus standard credentials for PostgreSQL, MySQL, SQL Server, Oracle, MongoDB, Redis, Elasticsearch, others [`googleapis--mcp-toolbox`]

### Service-native credentials

- Redis ACL (username/password) [`redis--mcp-redis`]
- Zendesk API credentials via `zenpy` (token or username/password); from `.env` [`reminia--zendesk-mcp-server`]

### Cloud-native identity (rare)

- Azure EntraID with three sub-flows (service principal, managed identity, default Azure credential) plus automatic token renewal with background refresh. Reflects enterprise Azure deployment pressure; rare among community MCPs [`redis--mcp-redis`]

### Framework-level

- Consumer-defined; framework supports middleware patterns for auth layering [`jlowin--fastmcp`]

## Multi-tenancy

Whether and how the server can serve multiple tenants in one process.

### Single-user / single-workspace per process

Process-scoped credentials; no per-request switching.

- Single API key per deployment, likely single-user [`AlwaysSany--deepl-fastmcp-python-server`]
- Token is process-scoped; one Figma identity per launch [`GLips--Figma-Context-MCP`]
- Single workspace per personal-token API key [`DiversioTeam--clickup-mcp`]
- Single connection per server instance; no per-request tenant switching [`HenkDz--postgresql-mcp-server`]
- Single user per container; one container per tool [`FuzzingLabs--mcp-security-hub`]
- Single-user per process [`JackKuo666--PubMed-MCP-Server`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`, `hugoduncan--mcp-clj`, `isaaccorley--planetary-computer-mcp`]
- One user token [`PagerDuty--pagerduty-mcp-server`]
- Per key pair [`alpacahq--alpaca-mcp-server`]
- One container per kubeconfig/context [`alexei-led--k8s-mcp-server`]
- README explicitly states "NOT designed for multi-tenant environments" — explicit anti-multi-tenancy statement is rare [`awslabs--aws-api-mcp-server`]
- API key ties to one Linear workspace [`geropl--linear-mcp-go`]
- Single-merchant per process [`paypal--paypal-mcp-server`]
- Single-user per API key [`ppl-ai--modelcontextprotocol`, `riza-io--riza-mcp`]
- One Qdrant instance + one default collection [`qdrant--mcp-server-qdrant`]
- Single Redis connection per server (cluster mode is connection topology, not per-request tenancy) [`redis--mcp-redis`]
- Single Zendesk subdomain per instance [`reminia--zendesk-mcp-server`]
- One data source per launch (multiple sources require multiple launches) [`pragmar--mcp-server-webcrawl`]
- Single-user per process; OAuth bolt-on suggests tenant support but documented as single kubeconfig context per server [`rohitg00--kubectl-mcp-server`]

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

### Single-user stdio + per-user OAuth on hosted

- Single-user per stdio process, per-user OAuth on hosted [`getsentry--sentry-mcp`]
- One PAT one identity for stdio, per-user OAuth in hosted mode [`github--github-mcp-server`]

### Per-process / multi-source

- Per-process; manifest can declare multiple sources (multi-database but not multi-user); HTTP endpoint serves any connected MCP client [`googleapis--mcp-toolbox`]

### Per-repo parameterized tenant

- Per-repository tenant parameterized by owner/repo via URL — cloud-hosted single service with multi-repo support [`idosal--git-mcp`]

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

#### Two-tool minimal interface

- `clj-eval` (evaluate Clojure expressions) and `ls`; custom tools can be added dynamically via API; contrasted with 50+ tools in clojure-mcp [`hugoduncan--mcp-clj`]
- 2 tools: `download_data`, `download_geometries` [`isaaccorley--planetary-computer-mcp`]
- 2 tools: store, find [`qdrant--mcp-server-qdrant`]

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
- 3 tools: `read_query`, `list_tables`, `describe_table`; no resources/prompts/sampling/roots [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- 4 tools: `fetch_<repo>_documentation`, `search_<repo>_documentation`, `search_<repo>_code`, `fetch_url_content` [`idosal--git-mcp`]
- 6 tools: create_tool, fetch_tool, execute_tool, edit_tool, list_tools, execute_code [`riza-io--riza-mcp`]
- 4 tools: search, ask, research, reason [`ppl-ai--modelcontextprotocol`]
- ~6 ticket tools [`reminia--zendesk-mcp-server`]
- Read-only default + write-gated: 5 read tools (`linear_search_issues`, `linear_get_user_issues`, `linear_get_issue`, `linear_get_issue_comments`, `linear_get_teams`); 5 write-gated [`geropl--linear-mcp-go`]

#### Many tools (10–30)

- 28 tools spanning task CRUD, discovery, assignments, bulk ops, time tracking, analytics, user management [`DiversioTeam--clickup-mcp`]
- 14 tools — conversation history, thread replies, message search, reactions, user-group management, unread tracking; plus 2 resources as CSV directories [`korotovsky--slack-mcp-server`]
- 24 tools covering job management, build operations, queue handling, node/view queries, console output retrieval [`lanbaoshen--mcp-jenkins`]
- 25+ tools — `notebook_create`, `notebook_read`, `notebook_edit_cell`, `notebook_add_cell`, `notebook_export`, `notebook_search`, `notebook_get_outline`, `notebook_get_server_path_context`, plus SFTP-compatible variants [`jbeno--cursor-notebook-mcp`]
- ~30 tools grouped by business domain (Invoices, Payments, Disputes, Shipments, Catalog, Subscriptions, Reporting) [`paypal--paypal-mcp-server`]

#### Massive tool count (50+)

- 65+ tools across incidents, schedules, services, event orchestrations, teams, status pages, change events [`PagerDuty--pagerduty-mcp-server`]
- ~60 tools across 10 categories (Account/Trading/Positions/Watchlists/Assets/Stock/Crypto/Options/CorpActions/News) [`alpacahq--alpaca-mcp-server`]
- 92 tools across 5 libraries — Shapely (29), PyProj (13), GeoPandas (13), Rasterio (20), PySAL (18), visualization (2), plus data-acquisition modules. HTTP mode adds REST `/storage/upload`, `/storage/download`, `/storage/list` for binary artifacts MCP isn't built for [`mahdin75--gis-mcp`]
- 8 categories, multi-data-structure (strings, hashes, lists, sets, sorted sets, pub/sub, streams, JSON, plus vector search, server mgmt, docs search) [`redis--mcp-redis`]
- 253 tools across ~20 categories partitioned by Kubernetes resource kind [`rohitg00--kubectl-mcp-server`]
- ~100+ tools across 20+ toolsets (repos, issues, pull_requests, actions, etc.) with granular toolset/tool gating via flags [`github--github-mcp-server`]

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
- Declarative tool authoring via YAML manifest — admins define tools without writing code [`googleapis--mcp-toolbox`]

### Tool-surface scoping at launch

- `--tools=all` opt-in capability scoping reduces prompt-window noise for users who only need one sub-surface [`paypal--paypal-mcp-server`]
- `MCP_BROWSER_ENABLED` env-flag-gated optional bundles (browser-automation 26 tools) [`rohitg00--kubectl-mcp-server`]
- `--disable-destructive` safety flag suppresses destructive ops [`rohitg00--kubectl-mcp-server`]
- `[ui]` extra-gated dashboards [`rohitg00--kubectl-mcp-server`]
- `--read-only` flag, lockdown mode (filters public repo content), dynamic toolsets allowing runtime discovery [`github--github-mcp-server`]
- Writes gated behind explicit `--write-access` flag [`geropl--linear-mcp-go`]

### Tool semantics

- Saved-vs-arbitrary code execution: `create_tool` (save), `execute_tool` (run saved), `execute_code` (run arbitrary without saving). `edit_tool` capability for modifying saved tools is unusual among MCP servers [`riza-io--riza-mcp`]
- Tools grouped by business domain (Invoices/Payments/Disputes…) [`paypal--paypal-mcp-server`]
- Four-tool surface maps 1:1 to product/model offerings (search → Search API, ask → sonar-pro, research → sonar-deep-research, reason → sonar-reasoning-pro) — tool boundaries mirror product tiers rather than low-level API endpoints [`ppl-ai--modelcontextprotocol`]
- Per-data-structure tool grouping mirrors Redis command families [`redis--mcp-redis`]
- URL-aware operations — accepts Linear comment URLs directly without manual ID extraction [`geropl--linear-mcp-go`]

### Tool ergonomics / output control

- Optional `strip_thinking` parameter to remove reasoning tags from output — token-saving feature giving caller control over verbosity [`ppl-ai--modelcontextprotocol`]

### Resources

- `Database Tables`, `Database Schema` resources [`ahmedmustahid--postgres-mcp-server`]
- CSV channel/user lists exposed as resources [`korotovsky--slack-mcp-server`]
- `zendesk://knowledge-base` — splits read-via-resources from write-via-tools. One of the clearer uses of MCP resources rather than overloading tools for read access [`reminia--zendesk-mcp-server`]
- 8 resources alongside 253 tools [`rohitg00--kubectl-mcp-server`]
- Tools-only (no resources/prompts) [`alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`]

### Prompts

- Tools, toolsets, AND prompts via YAML manifest — most MCP servers concentrate on tools [`googleapis--mcp-toolbox`]
- 8 prompts via the MCP protocol primitive [`rohitg00--kubectl-mcp-server`]
- "Prompt routines" (Markdown, not MCP prompts protocol) — pre-authored Markdown prompts for autonomous tasks (SEO audits, 404 detection, performance analysis) under `prompts/`. Concept adjacent to skills but shipped as plain Markdown [`pragmar--mcp-server-webcrawl`]

### Skills (higher-level abstraction)

- "Skills" first-class — `MCP_DISABLE_SKILLS` env var toggles skill subsets (skills live under `.agents/skills/`). README positions the project as "primarily designed for human-in-the-loop coding agents." A higher-level behavioral primitive distinct from tools [`getsentry--sentry-mcp`]

### Embedded LLM invocation

- Embedded agent provider — `EMBEDDED_AGENT_PROVIDER` ('openai' | 'anthropic') with provider-specific API keys lets the MCP server invoke an LLM internally. Unusual; most MCP servers are pure tool-callers [`getsentry--sentry-mcp`]

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

- Progressive-trust gating of destructive operations — `CLICKHOUSE_ALLOW_WRITE_ACCESS` plus a separate `CLICKHOUSE_ALLOW_DROP`; SQL-layer `readonly=1` setting compounds with the MCP-layer flags [`ClickHouse--mcp-clickhouse`]
- Read-only-by-default with mutation gated behind `--enable-write-tools` [`PagerDuty--pagerduty-mcp-server`]
- Paper-trading mode default (`ALPACA_PAPER_TRADE=true`) — mutation-capable but sandbox-by-default [`alpacahq--alpaca-mcp-server`]
- Read-only by design (SQL execution restricted to read-only queries) [`ahmedmustahid--postgres-mcp-server`]
- Pure read-only documentation bridge [`awslabs--aws-documentation-mcp-server`]
- Experimental tools gated by feature flag (`get_execution_plan`) [`awslabs--aws-api-mcp-server`]
- `--readonly` flag delegates to DuckDB's native protection (not tool-layer validation); non-readonly auto-creates DB file and parent dirs [`ktanaka101--mcp-server-duckdb`]
- Read-only mode flag at server level [`lanbaoshen--mcp-jenkins`]
- Writes gated behind explicit `--write-access` flag [`geropl--linear-mcp-go`]
- Read-only enforced at the tool layer (query validation + row caps), not DB-level [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- `--read-only` flag [`github--github-mcp-server`]

### LLM-targeted output synthesis

- Generates visualizations for LLM analysis — server synthesizes images for the model to interpret. Multi-format outputs (GeoTIFF, GeoParquet, Zarr) — uncommon in MCP servers; implies large-file handling [`isaaccorley--planetary-computer-mcp`]

### Specialty capabilities

- **In-server documentation search** — ships a docs-search tool calling a separate HTTP endpoint via `MCP_DOCS_SEARCH_URL`; RAG-style augmentation attached to a database server [`redis--mcp-redis`]
- **Vector search alongside core data** — first-classes vector search alongside Redis data structures [`redis--mcp-redis`]
- **Cluster mode as config axis** — `--cluster-mode` flag [`redis--mcp-redis`]
- **Boolean fulltext + multi-extraction-mode search** — field-specific queries (url, content, headers, type, status, id, size); content filtering by type (html, img, pdf, video) and HTTP status; extraction modes markdown / snippet / regex / XPath; thumbnail generation for images [`pragmar--mcp-server-webcrawl`]
- **Multi-format crawler-archive compatibility** — reads ArchiveBox, HTTrack, InterroBot, Katana, SiteOne, WARC, wget archives. Unusually broad — most crawler tools target one format [`pragmar--mcp-server-webcrawl`]

### Capability types beyond tools

- Three-pillar framework: Servers (tools/resources/prompts), Clients, Apps (interactive UIs in conversations) [`jlowin--fastmcp`]
- REST endpoints alongside MCP tools to handle binary file transfer (`/storage/upload`, `/storage/download`, `/storage/list`) [`mahdin75--gis-mcp`]

## Domain decoupling

When a server allows the user to swap a cross-cutting concern via configuration.

- **Embedding model/provider decoupled from storage** — `EMBEDDING_MODEL` and `EMBEDDING_PROVIDER` env vars independently of the storage backend; `fastembed` (ONNX-backed Qdrant lib) gives default no-API-key install [`qdrant--mcp-server-qdrant`]
- **Local-vs-remote backend toggle** — `QDRANT_LOCAL_PATH` vs `QDRANT_URL` makes local-path mode a single env switch [`qdrant--mcp-server-qdrant`]
- **Sandbox/production environment branch** — `PAYPAL_ENVIRONMENT` selects SANDBOX or PRODUCTION via single binary; not separate entry points [`paypal--paypal-mcp-server`]

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
- FastMCP-standard logging via env config [`qdrant--mcp-server-qdrant`]

### Log-level via env var

- `PERPLEXITY_LOG_LEVEL` [`ppl-ai--modelcontextprotocol`]
- `MCP_REDIS_LOG_LEVEL` (DEBUG/INFO/WARNING/ERROR/CRITICAL); default WARNING [`redis--mcp-redis`]
- `MCP_DEBUG` + `MCP_LOG_FILE` [`rohitg00--kubectl-mcp-server`]

### Debug flags

- `--debug` flag on the CLI; `rich`-formatted output [`DiversioTeam--clickup-mcp`]
- `--verbose` flag [`ahmedmustahid--postgres-mcp-server`]

### Middleware-driven logging

- Example middleware demonstrates request logging and performance measurement; user-supplied [`ClickHouse--mcp-clickhouse`]

### Container-level health checks

- Health-check scripts per container; Trivy vulnerability scanning in CI as part of build pipeline [`FuzzingLabs--mcp-security-hub`]

### Interactive REPL doubling as debug surface

- `--interactive` terminal mode is a custom debug surface; rare among MCP servers that typically rely on MCP Inspector [`pragmar--mcp-server-webcrawl`]

### Stdio cleanliness pressure

- Explicitly notes "progress output suppression for clean JSON responses" as a deliberate behavior — reflects stdio-protocol cleanliness pressure where any stray stdout corrupts the JSON-RPC stream [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]

### Conventions and gaps

Most samples do not document logging destination/format. Go stdio servers typically log to stderr ([`geropl--linear-mcp-go`, `github--github-mcp-server`, `googleapis--mcp-toolbox`]). [`isaaccorley--planetary-computer-mcp`, `hugoduncan--mcp-clj`, `idosal--git-mcp`, `getsentry--sentry-mcp`, `paypal--paypal-mcp-server`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp`] not documented.

### Not surfaced

- [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `jbeno--cursor-notebook-mcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]

## Host integrations

Which MCP-compatible hosts the server documents support for.

### Claude Desktop

The most-cited host target; typically a JSON `mcpServers` entry.

- [`ClickHouse--mcp-clickhouse`, `HenkDz--postgresql-mcp-server`, `FuzzingLabs--mcp-security-hub`, `GLips--Figma-Context-MCP`, `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`, `lanbaoshen--mcp-jenkins`, `korotovsky--slack-mcp-server`]
- Implied via stdio transport [`jbeno--cursor-notebook-mcp`]
- Cline emphasis, not Desktop directly [`geropl--linear-mcp-go`]
- JSON snippet using Docker or local binary [`github--github-mcp-server`]
- Via FastMCP CLI install [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Sample `claude_desktop_config.json` [`hugoduncan--mcp-clj`]
- [`idosal--git-mcp`]
- As marketplace plugin [`getsentry--sentry-mcp`]
- Primary host, JSON config snippets [`paypal--paypal-mcp-server`]
- Quick-install badge [`ppl-ai--modelcontextprotocol`]
- Primary; documented as a requirement [`pragmar--mcp-server-webcrawl`]
- JSON snippet for `claude_desktop_config.json` [`qdrant--mcp-server-qdrant`]
- JSON config example [`redis--mcp-redis`]
- `uv --directory` invocation pattern [`reminia--zendesk-mcp-server`]
- Primary [`riza-io--riza-mcp`]
- JSON `mcpServers` entry [`rohitg00--kubectl-mcp-server`]

### Claude Code

- Project-level `.mcp.json` with per-tool entries [`FuzzingLabs--mcp-security-hub`]
- Integration documented [`getsentry--sentry-mcp`]
- Listed as compatible client [`googleapis--mcp-toolbox`]

### Cursor IDE

Featured prominently in some servers' docs.

- Primary target, featured prominently with sample config in README [`GLips--Figma-Context-MCP`]
- Documented as an MCP client target [`HenkDz--postgresql-mcp-server`]
- `~/.cursor/mcp.json` [`alpacahq--alpaca-mcp-server`]
- `.cursor/mcp.json` (project-scoped) and `~/.cursor/mcp.json` (global) — explicit dual-level config documented [`jbeno--cursor-notebook-mcp`]
- `.cursor/mcp.json` snippet [`mahdin75--gis-mcp`]
- npx command [`jparkerweb--mcp-sqlite`]
- [`getsentry--sentry-mcp`, `github--github-mcp-server` (Docker-based config with PAT env injection), `idosal--git-mcp`, `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `rohitg00--kubectl-mcp-server`]

### VS Code / VS Code MCP / GitHub Copilot

- `.vscode/mcp.json` entry [`alpacahq--alpaca-mcp-server`, `lanbaoshen--mcp-jenkins`]
- npx command [`jparkerweb--mcp-sqlite`]
- VS Code 1.101+ native MCP support with OAuth or PAT auth [`github--github-mcp-server`]
- Parallel TypeScript VS Code extension under `vscode-extension/` [`isaaccorley--planetary-computer-mcp`]
- JSON `mcp.json` for VSCode [`idosal--git-mcp`]
- Quick-install badge [`ppl-ai--modelcontextprotocol`]
- JSON snippet with `uvx` [`qdrant--mcp-server-qdrant`]
- VS Code + GitHub Copilot, requires `chat.agent.enabled: true` [`redis--mcp-redis`]

### Windsurf

- Docker-based with PAT env injection [`github--github-mcp-server`]
- [`idosal--git-mcp`, `ppl-ai--modelcontextprotocol` (badge), `qdrant--mcp-server-qdrant` (JSON snippet), `rohitg00--kubectl-mcp-server`]

### IDE integrations beyond Claude/Cursor/VSCode/Windsurf

Vendor-driven C# servers ship integrations for Microsoft's broader IDE ecosystem.

- VS Code, VS Code Insiders, Visual Studio 2022, IntelliJ IDEA, Eclipse [`Azure--azure-mcp` successor microsoft/mcp]
- PyCharm (Settings → Tools → MCP) — less widely advertised than Claude Desktop [`alpacahq--alpaca-mcp-server`]
- JetBrains IDE — unusual; most MCP servers focus on Claude/Cursor/VSCode [`lanbaoshen--mcp-jenkins`]
- JetBrains IDEs (Docker-based with PAT env injection) [`github--github-mcp-server`]
- Gemini CLI (`settings.json`) [`alpacahq--alpaca-mcp-server`]

### Cline

- Dedicated example [`JackKuo666--PubMed-MCP-Server`]
- Primary; dedicated `setup --tool=cline` [`geropl--linear-mcp-go`]
- Manual MCP configuration example with `"command": "uv"`, `"args": ["run", "--with", "fastmcp", ...]` [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- [`idosal--git-mcp`, `paypal--paypal-mcp-server`]

### Gemini CLI / Google Antigravity / Codex

- In-repo `gemini-extension.json` and lists Google Antigravity, Claude Code, Codex as compatible clients [`googleapis--mcp-toolbox`]

### Highlight AI / Augment Code / Msty AI

- JSON `mcp.json` configs alongside common ones [`idosal--git-mcp`]

### Kiro

- Quick-install badge [`ppl-ai--modelcontextprotocol`]

### Augment

- Supported via Easy MCP feature [`redis--mcp-redis`]

### OpenAI Agents SDK

- [`redis--mcp-redis`]

### "15+ other clients" / generic MCP

- Same JSON shape across all [`rohitg00--kubectl-mcp-server`]

### MCP Inspector

- [`ahmedmustahid--postgres-mcp-server`, `apollographql--apollo-mcp-server`]

### Smithery registry as host integration

- `smithery.yaml` in repo root [`JackKuo666--PubMed-MCP-Server`, `mahdin75--gis-mcp`]
- Smithery installer for host registration [`ktanaka101--mcp-server-duckdb`]
- One-click install for Claude Desktop [`qdrant--mcp-server-qdrant`]

### Generic AI client

- Generic JSON `mcpServers` entry [`PagerDuty--pagerduty-mcp-server`, `apollographql--apollo-mcp-server`]

### Enterprise Slack / GovSlack

- Custom User-Agent + TLS config for Slack environments [`korotovsky--slack-mcp-server`]

### DXT (Desktop Extensions) manifest

- `manifest-dxt.json` — Claude Desktop-specific packaging format distinct from `.mcp.json` [`korotovsky--slack-mcp-server`]

### Broad coverage

- 5 different MCP clients documented (Claude Desktop, Cursor, VS Code, PyCharm, Gemini CLI) — broader host-integration coverage than typical [`alpacahq--alpaca-mcp-server`]

### Other extension points

- Reachable via MCP Registry; `--tool` flag is a scoped extension point (currently only `cline`, but signals plan to automate other host configurations) [`geropl--linear-mcp-go`]

## Claude Code plugin wrapper

A `.claude-plugin` directory is the marker of a first-party plugin wrapping the MCP server.

### Present in-repo

- Ships both `.claude-plugin/` directory and `.mcp.json` at repo root — full Claude plugin wrapper in-repo. The server vends itself as a Claude plugin, not just a raw MCP binary. Rare; most servers leave host integration to external config [`getsentry--sentry-mcp`]

### Adjacent (Claude-assisted authoring, not a plugin wrapper)

- `.claude/` directory + `CLAUDE.md` at repo root (operational Claude docs; may be Claude Code workspace state, not a `.claude-plugin/plugin.json` wrapper) [`apollographql--apollo-mcp-server`]

### Absent

- Not present in any of the bin-1, bin-2, or bin-7 samples examined
- [`geropl--linear-mcp-go`, `github--github-mcp-server` (host integration via external `claude_desktop_config.json`), `googleapis--mcp-toolbox` (only `gemini-extension.json` shipped), `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`, `hugoduncan--mcp-clj`, `idosal--git-mcp`, `isaaccorley--planetary-computer-mcp`, `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp`, `rohitg00--kubectl-mcp-server`]
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
- `uv run pytest`, `tests/` [`isaaccorley--planetary-computer-mcp`]
- pytest >= 8.3.3, pytest-asyncio (auto mode); in-memory Qdrant fixture [`qdrant--mcp-server-qdrant`]
- pytest + pytest-asyncio + pytest-cov + pytest-mock; PEP 735 dependency-groups split into `dev` and `test`; `addopts = --cov=src --cov-fail-under=80` (coverage gate enforced); `asyncio_mode = "auto"` [`redis--mcp-redis`]
- 234+ passing pytest tests; unit + integration + server-initialization suites [`rohitg00--kubectl-mcp-server`]
- `/tests/` directory present, framework details not extracted [`AlwaysSany--deepl-fastmcp-python-server`, `PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `lanbaoshen--mcp-jenkins`]

### vitest / Jest

- vitest configured; specifics not extracted [`GLips--Figma-Context-MCP`]
- vitest [`ppl-ai--modelcontextprotocol`]
- Vitest + Playwright (`vitest.config.ts` units, `playwright.config.ts` E2E, `npm run test`) [`idosal--git-mcp`]
- Jest [`paypal--paypal-mcp-server`]

### pnpm test + eval harness

- `pnpm test` units, `pnpm eval` evaluations/scenario tests; MCP Inspector for local testing [`getsentry--sentry-mcp`]

### Go testing

- go-vcr cassettes in `testdata/`; live test workspace `linear.app/linear-mcp-go-test` for re-recording; flags `-record=true`, `-recordWrites=true`. Full integration tests run offline against recorded fixtures — reproducible without Linear credentials [`geropl--linear-mcp-go`]
- Go stdlib testing, E2E in `e2e/` [`github--github-mcp-server`]
- Go stdlib testing, `/tests` [`googleapis--mcp-toolbox`]

### Clojure tests.edn + clj-kondo

- testing investigation notes; clj-kondo lint [`hugoduncan--mcp-clj`]

### MCP Inspector / npm test

- MCP Inspector framework; `npm test` script [`jparkerweb--mcp-sqlite`]

### End-to-end protocol-conformance harness

- End-to-end harness in `/e2e/mcp-server-tester` [`apollographql--apollo-mcp-server`]

### Tests not surfaced

- [`HenkDz--postgresql-mcp-server`, `DaInfernalCoder--perplexity-mcp`, `JackKuo666--PubMed-MCP-Server`, `korotovsky--slack-mcp-server`, `labeveryday--mcp_pdf_reader`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`, `pragmar--mcp-server-webcrawl`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp`]

### Notable testing patterns

- Multi-layered test suite (integrity / server-construction / paper-API integration) [`alpacahq--alpaca-mcp-server`]
- Bedrock test result files in repo (cross-platform agent validation) [`PagerDuty--pagerduty-mcp-server`]
- Live-network integration gated behind opt-in flag (`--run-live`) [`awslabs--aws-documentation-mcp-server`]
- Protocol-conformance e2e tester as a first-class component [`apollographql--apollo-mcp-server`]
- Docs are test-verified — `griffelib`, `inline-snapshot`, `pytest-examples` [`jlowin--fastmcp`]
- Flake hunting and parallelism — `pytest-flakefinder` + `pytest-retry` + `pytest-xdist` [`jlowin--fastmcp`]
- go-vcr cassette testing for offline integration [`geropl--linear-mcp-go`]
- Evaluation harness alongside unit tests — distinguishes behavioral regression from code regression [`getsentry--sentry-mcp`]

## CI

Continuous-integration system, what it runs.

### GitHub Actions

Universal default in this corpus where CI is documented.

- `.github/workflows/` present; specifics not extracted [`ClickHouse--mcp-clickhouse`, `HenkDz--postgresql-mcp-server`, `DiversioTeam--clickup-mcp`, `GLips--Figma-Context-MCP`]
- Builds + security scanning (Trivy) + tests in CI [`FuzzingLabs--mcp-security-hub`]
- GitHub Actions on every PR [`alpacahq--alpaca-mcp-server`]
- GitHub Actions [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server` (`release.yml`, `ci.yml`), `apollographql--apollo-mcp-server` (CI + release-binaries + release-container workflows), `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp` (`run-tests.yml`), `korotovsky--slack-mcp-server`, `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- codecov integration [`lanbaoshen--mcp-jenkins`, `redis--mcp-redis`]
- CI badge visible [`mahdin75--gis-mcp`]
- Automated testing on pushes/PRs, automated releases on version tags [`geropl--linear-mcp-go`]
- Workflows present, contents not enumerated [`github--github-mcp-server`]
- `.ci/` plus `.github/workflows/`, `.golangci.yaml` lint [`googleapis--mcp-toolbox`]
- `e2e-tests.yml`, `run-tests.yml` [`idosal--git-mcp`]
- Configured [`isaaccorley--planetary-computer-mcp`]
- Likely; `cliff.toml` for release notes [`hugoduncan--mcp-clj`]
- Implied by monorepo standard [`getsentry--sentry-mcp`]
- `.github/workflows/` present [`paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `reminia--zendesk-mcp-server`, `rohitg00--kubectl-mcp-server`]
- Documented jobs: lint/type-check/test + release [`qdrant--mcp-server-qdrant`]

### Parent monorepo CI

- Sub-server-specific config not extracted [`awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`]

### `.github/` present, workflow details not surfaced

- [`JackKuo666--PubMed-MCP-Server`]

### Not detailed / not documented

- [`ahmedmustahid--postgres-mcp-server`, `jparkerweb--mcp-sqlite`, `labeveryday--mcp_pdf_reader`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server` (no workflows), `pragmar--mcp-server-webcrawl`, `riza-io--riza-mcp`]

## Container / packaging artifacts

Dockerfile, compose, image-publishing artifacts that ship alongside the source.

### Dockerfile only

- [`Azure--azure-mcp`, `DaInfernalCoder--perplexity-mcp`, `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server` (with stdio transport), `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `lanbaoshen--mcp-jenkins` (multi-platform under `/docker/`), `korotovsky--slack-mcp-server` (Dockerfile 874 bytes + `.dockerignore`)]
- [`geropl--linear-mcp-go` (Dockerfile + `.devcontainer/` for dev), `github--github-mcp-server` (multi-platform Dockerfile, no compose/Helm/brew), `ppl-ai--modelcontextprotocol`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `rohitg00--kubectl-mcp-server` (also Docker Hub published image)]
- Dockerfile installs from `requirements.lock` for build reproducibility [`reminia--zendesk-mcp-server`]
- Dockerfile + Homebrew formula [`googleapis--mcp-toolbox`]

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

### Cloud-native deployment

- No Dockerfile; Cloudflare Workers cloud-native deployment [`idosal--git-mcp`]

### Hardened-container posture

Security-by-default container settings — non-root, capability-drop, resource limits, read-only mounts — unusual rigor for MCP servers [`FuzzingLabs--mcp-security-hub`].

### None

- [`jbeno--cursor-notebook-mcp`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`, `hugoduncan--mcp-clj`, `isaaccorley--planetary-computer-mcp`, `getsentry--sentry-mcp` (not explicitly documented), `paypal--paypal-mcp-server`, `pragmar--mcp-server-webcrawl`, `riza-io--riza-mcp`]

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
- Go: `cmd/` + `pkg/` [`geropl--linear-mcp-go`]
- Single Go module rooted at `cmd/github-mcp-server` with supporting packages, `server.json` at root [`github--github-mcp-server`]
- Single Go module: `/cmd`, `/docs`, `/internal`, `/tests`, `/.ci`, `/.github`, `/.hugo`, `/.gemini`; `.gitmodules` present [`googleapis--mcp-toolbox`]
- Single-file script `sqlite_explorer.py` with requirements + docs [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Single-package React/TS with Cloudflare integration: `app/`, `src/`, `static/`, `tests/`, `dist/`, `wrangler.jsonc`, `react-router.config.ts`, `vite.config.ts`, `vitest.config.ts` [`idosal--git-mcp`]
- `docs/`, `prompts/`, `sphinx/` [`pragmar--mcp-server-webcrawl`]
- `src/mcp_server_qdrant/` [`qdrant--mcp-server-qdrant`]
- `src/`, `tests/`, `examples/`, Dockerfile, `pyproject.toml`, `server.json`, `uv.lock` [`redis--mcp-redis`]
- `zendesk_mcp_server/` [`reminia--zendesk-mcp-server`]
- Single-package, modular submodules per resource kind (pods.py, deployments.py, helm.py); separate `resources/` and `prompts/` dirs [`rohitg00--kubectl-mcp-server`]

### Single-package Node.js / mixed JS+TS

- JS-majority with Shell auxiliary scripts [`paypal--paypal-mcp-server`]
- Single-package TypeScript, source in `/src` [`ppl-ai--modelcontextprotocol`]
- Minimal (README + `/typescript/` directory) [`riza-io--riza-mcp`]

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

### Monorepo (pnpm + Turbo)

- pnpm workspaces + Turbo; multiple packages under `/packages`; `.agents/skills/` for skill definitions; `.claude-plugin/` and `.mcp.json` at root [`getsentry--sentry-mcp`]

### Polylith-style modular (Clojure)

- `bases/`, `components/`, `projects/` + supporting `design/`, `dev/`, `development/`, `doc/`, `spec/`, `scripts/`; `deps.edn`, `tests.edn`, `cliff.toml`, `.cljstyle`; `.clj-kondo/`, `.github/`, `.claude/`, `.mcp-vector-search/` [`hugoduncan--mcp-clj`]

### Mixed-language monorepo

- Monorepo-ish: Python `src/` with `core/`, `tools/`, `server.py`, plus parallel `vscode-extension/` TypeScript subproject [`isaaccorley--planetary-computer-mcp`]

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

### Pre-commit / lint

- `uv run pre-commit run --all-files` [`isaaccorley--planetary-computer-mcp`]
- `.golangci.yaml` [`googleapis--mcp-toolbox`]
- `.golangci.yml` [`github--github-mcp-server`]
- Biome unified linting/formatting [`idosal--git-mcp`]
- clj-kondo + `.cljstyle` [`hugoduncan--mcp-clj`]
- pre-commit [`qdrant--mcp-server-qdrant`]
- mypy + black + bandit + safety + twine — security scanning as first-class; PyPI publishing pipeline [`redis--mcp-redis`]

### LLM-consumable docs / Bundled AI-guidance content

- `llms.txt` and `llms-full.txt` for AI-consumable docs ("vibe coding" context) — design-for-AI-consumption documentation format [`jlowin--fastmcp`, `mahdin75--gis-mcp`]
- `cursor_rules.md` shipped alongside server — neither MCP tool nor prompt, just LLM-readable guidance [`jbeno--cursor-notebook-mcp`]
- `fastmcp-documentation.txt` + `mcp-documentation.txt` in repo — embedded LLM-context docs [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]

### Inspector / curl / make

- MCP Inspector recommended (`npx @modelcontextprotocol/inspector`) [`ktanaka101--mcp-server-duckdb`, `korotovsky--slack-mcp-server`, `jparkerweb--mcp-sqlite`]
- `agents/` directory with runnable example clients [`mahdin75--gis-mcp`]
- `.vscode/mcp.json` sample [`lanbaoshen--mcp-jenkins`]
- `examples/` + `docs/` directories; community Discord; docs at gofastmcp.com [`jlowin--fastmcp`]
- `pnpm -w run cli` for manual CLI testing [`getsentry--sentry-mcp`]
- `fastmcp dev` for Inspector documented [`qdrant--mcp-server-qdrant`]

### Sample host configs in-repo

- `setup --tool` automates JSON config editing [`geropl--linear-mcp-go`]
- Ships `.vscode/` [`github--github-mcp-server`]
- `gemini-extension.json` + `server.json` [`googleapis--mcp-toolbox`]
- Sample `claude_desktop_config.json` in README [`hugoduncan--mcp-clj`]
- Dev scripts + Playwright E2E + README examples [`idosal--git-mcp`]

### Eval harness

- `pnpm eval` for regression testing against model outputs [`getsentry--sentry-mcp`]

### Memory-bank convention

- `memory-bank/` directory suggests author uses Cline's memory-bank convention — evidence of dogfooding [`geropl--linear-mcp-go`]

### Documentation build

- `sphinx/` for documentation build [`pragmar--mcp-server-webcrawl`]

### Custom debug surface

- `--interactive` REPL custom debug surface [`pragmar--mcp-server-webcrawl`]

## Python-specific

Build backend, lock files, version-manager conventions, async semantics, schema strategy for Python servers.

### Build backend

- `hatchling.build` [`ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `ktanaka101--mcp-server-duckdb`, `mahdin75--gis-mcp`, `jlowin--fastmcp`, `qdrant--mcp-server-qdrant`, `reminia--zendesk-mcp-server`]
- Poetry (`poetry.lock` present) [`PagerDuty--pagerduty-mcp-server`]
- pyproject.toml (uv-based); backend not surfaced [`lanbaoshen--mcp-jenkins`]
- setuptools (`setuptools.build_meta`) — contrarian vs hatchling-dominated sample [`pragmar--mcp-server-webcrawl`]
- setuptools (`setup.py`) — older convention vs modern pyproject-only [`rohitg00--kubectl-mcp-server`]
- `uv_build` (`requires = ["uv_build>=0.8.3,<0.12.0"]`) — one of the very few using uv's native build backend [`redis--mcp-redis`]
- Not unified across per-tool Dockerfiles — Docker layer absorbs packaging [`FuzzingLabs--mcp-security-hub`]
- Not surfaced [`JackKuo666--PubMed-MCP-Server`, `alexei-led--k8s-mcp-server`]
- Not applicable — single script [`labeveryday--mcp_pdf_reader`]

### Lock file / version manager

`uv` is dominant in surfaced cases.

- `uv` / `uvx` adoption [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`, `DiversioTeam--clickup-mcp`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`, `qdrant--mcp-server-qdrant` (`.python-version`), `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `isaaccorley--planetary-computer-mcp` (`.python-version`)]
- `uv.lock` present [`jlowin--fastmcp`, `redis--mcp-redis`]
- `uv.lock` implied [`labeveryday--mcp_pdf_reader`, `ktanaka101--mcp-server-duckdb`, `isaaccorley--planetary-computer-mcp`]
- Not explicitly confirmed [`mahdin75--gis-mcp`, `jbeno--cursor-notebook-mcp`, `lanbaoshen--mcp-jenkins`]
- `requirements.lock` (used by Dockerfile) [`reminia--zendesk-mcp-server`]
- `poetry.lock` (also supports uv) [`PagerDuty--pagerduty-mcp-server`]
- `requirements.txt` (no lock) [`JackKuo666--PubMed-MCP-Server`]
- plain pip [`pragmar--mcp-server-webcrawl`]
- pip/uv compatible [`rohitg00--kubectl-mcp-server`]
- pre-`pyproject.toml` (pip/venv with `requirements.txt`) — NO pyproject.toml, only `requirements.txt` + single `sqlite_explorer.py`. No build backend, no lock file [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]

### Async semantics

- FastMCP handles the async boundary; tool signatures may be sync `def` even with FastMCP 2.x [`ClickHouse--mcp-clickhouse`]
- httpx + pytest-asyncio implies async tool implementations [`DiversioTeam--clickup-mcp`]
- async (FastMCP + starlette + uvicorn) [`jbeno--cursor-notebook-mcp`]
- Both `def` and `async def` dispatched transparently; anyio/asyncio under the hood [`jlowin--fastmcp`]
- FastMCP auto-wraps both [`mahdin75--gis-mcp`]
- Sync handlers — file-processing stack (PyMuPDF, pytesseract) is CPU-bound; async offers little value [`labeveryday--mcp_pdf_reader`]
- `httpx` (network-bound work; likely async) [`alpacahq--alpaca-mcp-server`, `awslabs--aws-documentation-mcp-server`]
- Mentions `asyncio` [`JackKuo666--PubMed-MCP-Server`]
- async (FastMCP default + pytest-asyncio auto) [`qdrant--mcp-server-qdrant`]
- async (pytest-asyncio auto, low-level mcp[cli]) [`redis--mcp-redis`]
- async likely (low-level mcp SDK) [`pragmar--mcp-server-webcrawl`]
- sync likely (zenpy is sync) [`reminia--zendesk-mcp-server`]
- not surfaced (FastMCP default applies) [`rohitg00--kubectl-mcp-server`]
- FastMCP-decorated functions (sync and async supported in 0.4.1) [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- async likely (STAC clients tend to be async) [`isaaccorley--planetary-computer-mcp`]
- Not surfaced [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`, `awslabs--aws-api-mcp-server`, `ktanaka101--mcp-server-duckdb`, `lanbaoshen--mcp-jenkins`]

### Type / schema strategy

- FastMCP-auto-derived schema from Python signatures [`AlwaysSany--deepl-fastmcp-python-server`, `ClickHouse--mcp-clickhouse`, `JackKuo666--PubMed-MCP-Server`, `alpacahq--alpaca-mcp-server`, `labeveryday--mcp_pdf_reader`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Pydantic v2 + pydantic-settings for typed config [`DiversioTeam--clickup-mcp`]
- Pydantic 2.x (`>=2.0.0, <2.12.0`); FastMCP auto-derives from signatures [`jbeno--cursor-notebook-mcp`]
- Auto-derived JSON Schema from type hints + docstrings; `Annotated[type, Field(description=...)]` patterns; pydantic + jsonschema-path + jsonref [`jlowin--fastmcp`]
- Pydantic via FastMCP; auto-derived [`mahdin75--gis-mcp`]
- `pydantic >= 2.10.6` [`awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`]
- Pydantic via MCP SDK; schema auto-derived [`isaaccorley--planetary-computer-mcp`]
- Pydantic 2 direct dep + FastMCP auto-derives. Pydantic pinned `>=2.10.6,<2.12.0` (tight window to track FastMCP compatibility) [`qdrant--mcp-server-qdrant`]
- FastMCP default (Pydantic-based) inferred [`rohitg00--kubectl-mcp-server`]
- Hand-authored schemas [`pragmar--mcp-server-webcrawl`, `redis--mcp-redis` (low-level MCP SDK), `FuzzingLabs--mcp-security-hub`, `ktanaka101--mcp-server-duckdb`]
- Raw dicts likely (raw mcp SDK handlers typically take dicts) [`reminia--zendesk-mcp-server`]
- Not surfaced [`PagerDuty--pagerduty-mcp-server`, `alexei-led--k8s-mcp-server`]

### Optional-extras strategy

- Per-library opt-in fan-out — 8 domain-specific extras (`administrative-boundaries`, `climate`, `ecology`, `movement`, `satellite-imagery`, `land-cover`, `visualize`, `test`) plus an `all` extra; users install only the toolchain they need [`mahdin75--gis-mcp`]
- Very broad optional-dependencies surface — `anthropic`, `azure`, `gemini`, `openai`, `apps`, `code-mode`, `tasks` — each opt-in, avoiding bloat on core install [`jlowin--fastmcp`]
- Optional `[chdb]` extra to swap in alternative engines [`ClickHouse--mcp-clickhouse`]
- `[ui]` extra-gated dashboards [`rohitg00--kubectl-mcp-server`]

### Modern Python project layout

- PEP 735 `[dependency-groups]` with distinct `dev` and `test` groups [`redis--mcp-redis`]
- Coverage fail-threshold (`--cov-fail-under=80`) in `addopts` [`redis--mcp-redis`]

### Minimal-deps posture

- 3-deps runtime stack (`mcp`, `python-dotenv`, `zenpy`) [`reminia--zendesk-mcp-server`]
- No dev/test extras in pyproject — minimal packaging posture [`pragmar--mcp-server-webcrawl`]
- FastMCP only [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]

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

### Install workflow expected of end users (Python)

- `fastmcp install sqlite_explorer.py --name "..." -e SQLITE_DB_PATH=...` — uses FastMCP CLI installer; no pip-install path. `fastmcp install` registers server with Claude Desktop directly — distinct from `uvx` or manual config editing [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Source clone + `uv sync` [`isaaccorley--planetary-computer-mcp`]

## TypeScript packaging

Build tooling, package managers, dev-environment opinions for Node/TS servers.

### Build tooling

- tsup-built CLI with npm `bin` entry [`GLips--Figma-Context-MCP`, `HenkDz--postgresql-mcp-server`]

### Package manager / dev opinions

- pnpm + lefthook + ESLint + Prettier — opinionated dev environment; consumers building plugins on top should expect pnpm workflows [`GLips--Figma-Context-MCP`]
- pnpm + Turbo monorepo [`getsentry--sentry-mcp`]
- React Router 7 + Vite + Cloudflare Workers (Wrangler) — atypical TS stack centered on edge-runtime deployment [`idosal--git-mcp`]

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
- Declarative tool authoring via YAML manifest [`googleapis--mcp-toolbox`]

### Safety posture

- Anti-multi-tenancy explicit in README [`awslabs--aws-api-mcp-server`]
- Mutation gated by CLI flag [`PagerDuty--pagerduty-mcp-server`, `geropl--linear-mcp-go`, `github--github-mcp-server`]
- Sandbox/paper mode by default [`alpacahq--alpaca-mcp-server`]
- Read-only design [`ahmedmustahid--postgres-mcp-server`, `awslabs--aws-documentation-mcp-server`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Experimental-tool feature-flagging [`awslabs--aws-api-mcp-server`]
- Tool consolidation as a deliberate response to LLM discovery / parameter-validation pressure (46 atomic → 17 meta-tools) [`HenkDz--postgresql-mcp-server`]
- `--disable-destructive` safety flag [`rohitg00--kubectl-mcp-server`]

### Auto-approve configurability

- Users can mark specific tools safe to run without per-call confirmation [`geropl--linear-mcp-go`]

### Setup ergonomics

- `setup` subcommand replaces manual JSON config editing — rare; most expect users to hand-edit JSON [`geropl--linear-mcp-go`]

### Toolset gating + behavior modes

- `--read-only`, `--lockdown-mode`, `--insiders` as behavior envelopes rather than capability toggles, separating policy from toolset selection. `--dynamic-toolsets` exposes runtime-discoverable tools, affecting how hosts cache tool listings [`github--github-mcp-server`]

### Capability scoping at launch (consolidated)

Multiple distinct mechanisms for "user controls which slice of the surface is loaded":

- `--tools=all` opt-in [`paypal--paypal-mcp-server`]
- `MCP_BROWSER_ENABLED` env-flag-gated bundle [`rohitg00--kubectl-mcp-server`]
- `[ui]` pip-extra-gated dashboards [`rohitg00--kubectl-mcp-server`]
- `--disable-destructive` safety flag [`rohitg00--kubectl-mcp-server`]
- `--write-access` flag [`geropl--linear-mcp-go`]
- `--read-only` flag [`github--github-mcp-server`]

### Cloud-hosted SaaS endpoint

- Removes installation friction. Zero-auth model for public repos. React Router 7 + Vite frontend, Biome unified lint/format. Parameterized repository endpoints — one deployment serves every GitHub repo [`idosal--git-mcp`]

### Hosted + local hybrid

- Official remote MCP endpoint operated by vendor alongside self-run stdio binary [`getsentry--sentry-mcp`, `github--github-mcp-server`]

### Embedded LLM invocation as architecture

- Server-internal LLM invocation as architecture pattern — shifts some "agent" responsibility inside the MCP boundary [`getsentry--sentry-mcp`]

### Skills as bundled capability layer

- Skills toggleable per-deployment via `MCP_DISABLE_SKILLS`. A higher-level behavioral primitive distinct from tools. Skills live in `.agents/skills/` [`getsentry--sentry-mcp`]

### Co-located non-MCP integration

- Ships a VS Code extension alongside the MCP server — parallel non-MCP integration path in the same repo [`isaaccorley--planetary-computer-mcp`]

### LLM-targeted output synthesis as architecture

- Generates visualizations for LLM analysis — server synthesizes images for the model to interpret [`isaaccorley--planetary-computer-mcp`]

### Polylith-style modular architecture

- bases/components/projects — advanced modular organization. Vector search integration (`.mcp-vector-search/`) [`hugoduncan--mcp-clj`]

### Minimal dependencies

- Only `org.clojure/data.json` for full MCP implementation [`hugoduncan--mcp-clj`]
- FastMCP only [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]
- Self-contained Clojure REPL evaluation without external deps

### Single-file server script

- Keeps surface tiny [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`]

### Multi-database via sources abstraction

- Same binary speaks to 8+ databases via `sources` abstraction; tool authoring is declarative on top of that [`googleapis--mcp-toolbox`]

### HTTP-first transport diverging from stdio convention

- HTTP at `:5000/mcp` — explicit divergence from stdio-first convention [`googleapis--mcp-toolbox`]

### Gemini-first integration shape

- In-repo `gemini-extension.json` and `.gemini/` directory reflect project's origin at Google; other hosts consume the generic HTTP endpoint [`googleapis--mcp-toolbox`]

### Output ergonomics

- `strip_thinking` optional param removes reasoning tags from output [`ppl-ai--modelcontextprotocol`]

### Proxy configuration hierarchy

- `PERPLEXITY_PROXY` takes priority over `HTTPS_PROXY`/`HTTP_PROXY`. Recognizes corporate/enterprise environments where a service-specific proxy must override system-wide settings [`ppl-ai--modelcontextprotocol`]

### Lock-file-driven Docker reproducibility

- Dockerfile installs from `requirements.lock` — lock-file-as-build-contract, not pyproject-only [`reminia--zendesk-mcp-server`]
- `uv.lock` in repo as authoritative [`redis--mcp-redis`]

### Read existing data, don't crawl live

- Operates on pre-captured crawler archives, sidesteps rate-limit/politeness/JS-rendering concerns. Reference for "don't crawl inside MCP, index what the user crawled" [`pragmar--mcp-server-webcrawl`]

### Prompt-routine packaging

- Ships Markdown prompts as a distribution surface alongside tools — encoding "how to use the server for SEO audits" as reusable content rather than forcing users to rediscover prompting patterns [`pragmar--mcp-server-webcrawl`]

### Single-binary environment branching

- `PAYPAL_ENVIRONMENT` env var routes between sandbox/production rather than separate entry points [`paypal--paypal-mcp-server`]

### `server.json` for MCP server registry

- Ships `server.json` for MCP registry wiring [`redis--mcp-redis`, `github--github-mcp-server`, `googleapis--mcp-toolbox`]

### Granular SSL knobs

- Exposes `--ssl-ca-path`, `--ssl-keyfile`, `--ssl-certfile` alongside URI schemes (`redis://`, `rediss://`) [`redis--mcp-redis`]

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

## Unanticipated axes

Design decisions surfaced by 1-2 bins that may emerge as load-bearing axes once more bins are merged. Pruned to entries not already represented in the canonical tree above.

### Dual SDK dependency

- One server pulling both `mcp` and `fastmcp` [`awslabs--aws-api-mcp-server`, `jbeno--cursor-notebook-mcp` (migration shim)]

### Operation-driven tool catalog

- GraphQL operations as MCP tool declarations [`apollographql--apollo-mcp-server`]

### Tool-catalog mutability

- `--dynamic-toolsets` exposes runtime-discoverable tools rather than fixed catalog at startup; affects how hosts cache tool listings [`github--github-mcp-server`]

### Smithery-only distribution without PyPI

- [`JackKuo666--PubMed-MCP-Server`]

### asdf-based Python version pinning

- Rare compared to uv-native or `.python-version` [`PagerDuty--pagerduty-mcp-server`]

### CORS at MCP layer

- HTTP-transport-specific config; rare [`ahmedmustahid--postgres-mcp-server`]

### Remote-filesystem MCP (over SFTP)

- MCP server is local but operates on remote files over SFTP — distinct from HTTP/REST remote access [`jbeno--cursor-notebook-mcp`]

### Multi-token-type auth as flexibility

- Four Slack token types within one server — multiple auth mechanisms covering stealth mode and OAuth [`korotovsky--slack-mcp-server`]

### Per-request HTTP-header credentials

- Header-based credential passthrough turning single-tenant stdio server into multi-tenant HTTP service [`lanbaoshen--mcp-jenkins`]

### REST endpoints alongside MCP tools

- File-transfer REST endpoints (`/storage/upload`, `/storage/download`, `/storage/list`) for binary artifacts MCP isn't built for [`mahdin75--gis-mcp`]

### Massive cross-library tool fan-out

- 92 tools wrapping 5+ Python libraries into one "GIS Swiss army knife" MCP surface [`mahdin75--gis-mcp`]

### Bare-script server / Script as a server

- "Script as a server" pattern (`python <script>.py`) competes with console-script-PyPI as a simpler distribution tier [`labeveryday--mcp_pdf_reader`]

### System-tool dependency

- Tesseract OCR install required out-of-band on host — server cannot self-install (similar to ffmpeg servers) [`labeveryday--mcp_pdf_reader`]

### Zero-auth file-processing family

- Distinct family of MCP servers operating on local file inputs without any auth [`labeveryday--mcp_pdf_reader`]

### "Apps" pillar

- FastMCP's third pillar (Servers, Clients, Apps) extends MCP into UI territory beyond the standard tool/resource/prompt triad [`jlowin--fastmcp`]

### Self-claimed ecosystem centrality

- "Powers 70% of MCP servers across all languages" — market self-assessment worth noting [`jlowin--fastmcp`]

### Hackathon-winning auto-complexity heuristic

- Query routed to one of three backend models without explicit caller selection [`DaInfernalCoder--perplexity-mcp`]

### Marketing framing shaping tool surface

- Figma server positioned as design-to-code accelerator rather than general Figma CRUD server — shapes the tool surface (read-only, no writes) [`GLips--Figma-Context-MCP`]

### Contribution scaffolding

- `Dockerfile.template` as a first-class contribution surface for adding new servers to a monorepo [`FuzzingLabs--mcp-security-hub`]

### First-party-but-low-stars pattern

- Vendor releases at single-digit / low-double-digit star counts ([`paypal--paypal-mcp-server`] at 9, [`riza-io--riza-mcp`] at 14) suggest a recurring "official but unpromoted" axis worth examining

### Vector search integration (project-level)

- `.mcp-vector-search/` suggests semantic/similarity search capabilities [`hugoduncan--mcp-clj`]

### MCP resources used vs ignored

- Uses resources for KB read access [`reminia--zendesk-mcp-server`]; exposes 8 resources [`rohitg00--kubectl-mcp-server`]; most samples only use tools. The "split read/write across resources/tools" pattern is a divergence axis

### Prompt-routines vs MCP prompts protocol

- Ships Markdown prompts as a separate surface [`pragmar--mcp-server-webcrawl`]; exposes prompts via the MCP protocol primitive [`rohitg00--kubectl-mcp-server`]. Same goal, different mechanism

### Cloud-native auth (Azure EntraID) vs static credentials

- Only sample with cloud-native identity; flagging because enterprise deployment pressure may be a recurring driver [`redis--mcp-redis`]

### Editable-install-only distribution

- "Developer-mode-as-release" is a distinct distribution mechanism [`reminia--zendesk-mcp-server`]

### Polyglot wrapper

- Python core + npm wrapper. Implementation polyglot vs distribution polyglot are linked but distinct facets [`rohitg00--kubectl-mcp-server`]

## Gaps observed across corpus

- License content frequently not surfaced (LICENSE file not fetched in [`getsentry--sentry-mcp`], [`hannesrudolph--sqlite-explorer-fastmcp-mcp-server`])
- Logging destination/format rarely documented; most samples assume stderr by language convention
- Specific Go / Java / Node version constraints often unspecified
- CI workflow contents typically not enumerated within budget
- Whether `server.json` is consumed by MCP clients beyond identifying capability vs purely metadata — unclear ([`github--github-mcp-server`], [`googleapis--mcp-toolbox`], [`redis--mcp-redis`])
- Custom tool registration API patterns documented as "via API" but not detailed ([`hugoduncan--mcp-clj`])

## Open questions / categorization decisions

- **"Prompt routines" categorization** — placed [`pragmar--mcp-server-webcrawl`] Markdown prompt routines under "Prompts" subsection within Capabilities exposed but it is explicitly NOT using the MCP prompts protocol. Alternative home: a separate "Knowledge artifacts shipped alongside server" section
- **Editable-install-only categorization** — placed [`reminia--zendesk-mcp-server`] under Distribution but it could equally live under Notable Structural Choices as a posture statement
- **Cluster-mode under multi-tenancy** — [`redis--mcp-redis`] `--cluster-mode` is a connection topology, not per-request tenancy. Currently cited under Capabilities exposed; downstream merger may prefer a distinct "Connection topology" subsection
- **`server.json` placement** — placed under Notable Structural Choices but could live under Distribution if the registry is a distribution channel
- **Polyglot wrapper category** — implementation polyglot (Language and runtime) and distribution polyglot (Distribution / Cross-ecosystem glue) are linked but distinct facets — downstream merger should decide if one home is sufficient
