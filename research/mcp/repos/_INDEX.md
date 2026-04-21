# MCP Server Repos — Research Index

Per-repo structured findings captured during Phase 2 of the cross-platform MCP pattern research. Each file fills the same template (identification, language/runtime, transport, distribution, config surface, auth, multi-tenancy, capabilities, observability, host integrations, Claude Code plugin wrapper, tests, CI, packaging, ergonomics, repo layout, notable choices, unanticipated axes, gaps). Most Python-primary files also carry a `## Python-specific` section.

These are the empirical source data for `plugins/ocd/systems/patterns/templates/mcp-repo-cross-platform.md` (to be written in Phase 3). A repo's presence here is a claim that its structure was directly inspected; the per-file content records what was observed. Gaps sections record what was not resolvable within budget.

Sample size: **104 repos** + 1 `_missing` record. Built in three passes: (1) language-agnostic cross-platform discovery (~63 repos), (2) Python-specific enrichment on existing Python files, (3) Python-focused discovery across three domains (data/ML/vector, infra/ops/security, breadth-fill + awslabs sub-server drill-down).

## How to use

- Point a reader at the per-repo file to see structural detail for that repo.
- For cross-sample adoption counts per axis, read *Per-purpose adoption matrices* below — one subsection per per-repo template section, each with its own `Path | Count | Representative repos` table and applicable denominator.
- When using a specific fact from a repo (e.g., stars, last-commit, version), verify against GitHub first — WebFetch metadata was captured quickly and may be approximate.
- Each per-repo file now carries a derived `one-line purpose:` in its Identification block, and each structured section (1-16) carries a `- pitfalls observed:` line with either observed pitfalls or an explicit `none noted in this repo`. The explicit "none" is a valid finding per the template discipline — absence must be stated, not implied.

## Sample breakdown

### Official MCP org (2)
- [modelcontextprotocol/servers](modelcontextprotocol--servers.md) — reference monorepo; Python ref servers (git, fetch, time) deliberately use raw `mcp` SDK, not FastMCP
- [modelcontextprotocol/kotlin-sdk](modelcontextprotocol--kotlin-sdk.md) — multiplatform SDK (JVM, Native, JS, Wasm)

### Cloud / infrastructure vendors (5)
- [awslabs/mcp](awslabs--mcp.md) — monorepo overview; each sub-server is its own first-class PyPI package
- [Azure/azure-mcp](Azure--azure-mcp.md) — archived; successor `microsoft/mcp` captured inline
- [cloudflare/mcp-server-cloudflare](cloudflare--mcp-server-cloudflare.md) — remote-Workers deployed; users point at hosted URLs
- [docker/hub-mcp](docker--hub-mcp.md) — Docker Hub image discovery
- [googleapis/mcp-toolbox](googleapis--mcp-toolbox.md) — 5 distribution channels; HTTP-first (port 5000)

### awslabs sub-server drill-down (5)
- [awslabs/aws-api-mcp-server](awslabs--aws-api-mcp-server.md) — wraps AWS CLI; mixes `mcp` + `fastmcp`
- [awslabs/aws-documentation-mcp-server](awslabs--aws-documentation-mcp-server.md) — no auth; partition-variant tool sets (global vs China AWS)
- [awslabs/bedrock-kb-retrieval-mcp-server](awslabs--bedrock-kb-retrieval-mcp-server.md) — boto3-direct; tag-based resource scoping as access control
- [awslabs/openapi-mcp-server](awslabs--openapi-mcp-server.md) — dynamic tool generation from OpenAPI specs
- [awslabs/mcp-lambda-handler](awslabs--mcp-lambda-handler.md) — framework for building Lambda-hosted MCP servers; implements protocol without `mcp` or `fastmcp` SDKs

### Developer platform vendors (11)
- [github/github-mcp-server](github--github-mcp-server.md) — Go; OAuth + PAT
- [getsentry/sentry-mcp](getsentry--sentry-mcp.md) — ships both `.claude-plugin/` and `.mcp.json`; internal "Skills" concept
- [stripe/agent-toolkit](stripe--agent-toolkit.md) — ships per-host wrappers: `.claude-plugin/` + `.cursor-plugin/`
- [apollographql/apollo-mcp-server](apollographql--apollo-mcp-server.md) — Rust; tool catalog derived from GraphQL operations (config, not code)
- [microsoft/playwright-mcp](microsoft--playwright-mcp.md) — browser automation via accessibility
- [makenotion/notion-mcp-server](makenotion--notion-mcp-server.md) — ships `CLAUDE.md` in the repo
- [slackapi/slack-mcp-plugin](slackapi--slack-mcp-plugin.md) — configs-only repo; remote service at `mcp.slack.com`
- [supabase-community/supabase-mcp](supabase-community--supabase-mcp.md) — HTTP-only; OAuth 2.1
- [neondatabase/mcp-server-neon](neondatabase--mcp-server-neon.md) — hosted remote service model
- [mongodb-js/mongodb-mcp-server](mongodb-js--mongodb-mcp-server.md)
- [elastic/mcp-server-elasticsearch](elastic--mcp-server-elasticsearch.md) — Rust; Docker-only; declared deprecated

### Additional vendor-owned servers (8)
- [paypal/paypal-mcp-server](paypal--paypal-mcp-server.md) — JS npx; OAuth 2.0
- [redis/mcp-redis](redis--mcp-redis.md) — uv_build backend (rare)
- [ClickHouse/mcp-clickhouse](ClickHouse--mcp-clickhouse.md) — middleware-based per-request tenancy
- [ppl-ai/modelcontextprotocol](ppl-ai--modelcontextprotocol.md) — Perplexity (org slug differs from brand)
- [exa-labs/exa-mcp-server](exa-labs--exa-mcp-server.md) — ships `.claude-plugin/`; native Claude Desktop connector
- [upstash/context7](upstash--context7.md) — ships `.claude-plugin/marketplace.json`; hybrid public/private backend
- [alpacahq/alpaca-mcp-server](alpacahq--alpaca-mcp-server.md) — finance/trading; paper-trading default; richest host-integration docs
- [PagerDuty/pagerduty-mcp-server](PagerDuty--pagerduty-mcp-server.md) — Poetry + uv dual workflow

### Frameworks / SDKs / language toolkits (7)
- [jlowin/fastmcp](jlowin--fastmcp.md) — Python framework (absorbed into official SDK); anchors Python MCP repo-layout defaults
- [mark3labs/mcp-go](mark3labs--mcp-go.md)
- [metoro-io/mcp-golang](metoro-io--mcp-golang.md)
- [viant/mcp](viant--mcp.md) — Go
- [conikeec/mcpr](conikeec--mcpr.md) — Rust (archived)
- [rust-mcp-stack/rust-mcp-filesystem](rust-mcp-stack--rust-mcp-filesystem.md) — Homebrew + Cargo + npm + Docker
- [hugoduncan/mcp-clj](hugoduncan--mcp-clj.md) — Clojure SDK

### Relational / document / KV databases (10)
- [motherduckdb/mcp-server-motherduck](motherduckdb--mcp-server-motherduck.md)
- [jparkerweb/mcp-sqlite](jparkerweb--mcp-sqlite.md)
- [hannesrudolph/sqlite-explorer-fastmcp-mcp-server](hannesrudolph--sqlite-explorer-fastmcp-mcp-server.md)
- [ktanaka101/mcp-server-duckdb](ktanaka101--mcp-server-duckdb.md)
- [teaguesterling/duckdb_mcp](teaguesterling--duckdb_mcp.md) — DuckDB **extension** embedded in SQL rather than standalone process
- [HenkDz/postgresql-mcp-server](HenkDz--postgresql-mcp-server.md)
- [ahmedmustahid/postgres-mcp-server](ahmedmustahid--postgres-mcp-server.md)
- [crystaldba/postgres-mcp](crystaldba--postgres-mcp.md) — read-only safety via pglast
- [spences10/mcp-turso-cloud](spences10--mcp-turso-cloud.md) — community canonical (not `tursodatabase/*`)
- [designcomputer/mysql_mcp_server](designcomputer--mysql_mcp_server.md)

### Vector / embedding databases (4)
- [qdrant/mcp-server-qdrant](qdrant--mcp-server-qdrant.md) — official vendor; FastMCP 2.x
- [chroma-core/chroma-mcp](chroma-core--chroma-mcp.md) — 4 backing-store modes in one binary; raw `mcp[cli]` holdout
- [zilliztech/mcp-server-milvus](zilliztech--mcp-server-milvus.md) — env > CLI precedence; source-tree `uv run` launch
- [sajal2692/mcp-weaviate](sajal2692--mcp-weaviate.md) — multi-tenancy as tool-argument, not server config

### Code / repos / dev tools (3)
- [idosal/git-mcp](idosal--git-mcp.md) — cloud-hosted SaaS endpoint, zero-auth
- [cyanheads/git-mcp-server](cyanheads--git-mcp-server.md) — dual runtime (Node + Bun); base-dir sandboxing
- [bhauman/clojure-mcp](bhauman--clojure-mcp.md) — REPL-as-transport

### AI / search / RAG / web content (5)
- [cyanheads/perplexity-mcp-server](cyanheads--perplexity-mcp-server.md)
- [DaInfernalCoder/perplexity-mcp](DaInfernalCoder--perplexity-mcp.md) — Smithery registry integration
- [pragmar/mcp-server-webcrawl](pragmar--mcp-server-webcrawl.md) — introduces "prompt routines" concept
- [shreyaskarnik/huggingface-mcp-server](shreyaskarnik--huggingface-mcp-server.md) — all three MCP surfaces + custom `hf://` URI scheme
- [riza-io/riza-mcp](riza-io--riza-mcp.md) — code interpreter

### Academic / research data (4)
- [blazickjp/arxiv-mcp-server](blazickjp--arxiv-mcp-server.md) — ships `.codex-plugin/` + `skills/` + MCP in one repo
- [openags/paper-search-mcp](openags--paper-search-mcp.md) — Claude Code skills in-tree; dual FastMCP + `mcp[cli]`
- [JackKuo666/PubMed-MCP-Server](JackKuo666--PubMed-MCP-Server.md) — Smithery-first distribution, no PyPI
- [zongmin-yu/semantic-scholar-fastmcp-mcp-server](zongmin-yu--semantic-scholar-fastmcp-mcp-server.md) — dual protocol: MCP + HTTP REST in same process

### Notebooks / data science / ML (5)
- [datalayer/jupyter-mcp-server](datalayer--jupyter-mcp-server.md) — dual-role (standalone + Jupyter extension); OpenTelemetry core dep
- [jbeno/cursor-notebook-mcp](jbeno--cursor-notebook-mcp.md) — SFTP transport for remote notebooks; CC BY-NC-SA license
- [marlonluo2018/pandas-mcp-server](marlonluo2018--pandas-mcp-server.md) — DataFrame analysis; blacklist-sandboxed pandas exec
- [shibuiwilliam/mcp-server-scikit-learn](shibuiwilliam--mcp-server-scikit-learn.md)
- [pathintegral-institute/mcp.science](pathintegral-institute--mcp.science.md) — scientific MCP monorepo; dispatcher via `uvx mcp-science <server>`

### GIS / geospatial / earth data (3)
- [mahdin75/gis-mcp](mahdin75--gis-mcp.md) — 92 GIS tools across 5 libraries; per-library optional-extras fan-out
- [isaaccorley/planetary-computer-mcp](isaaccorley--planetary-computer-mcp.md) — NASA STAC data; co-located VS Code extension (TS)
- [datalayer/earthdata-mcp-server](datalayer--earthdata-mcp-server.md) — NASA Earthdata; three download modes from single tool

### Kubernetes / container tooling (5)
- [rohitg00/kubectl-mcp-server](rohitg00--kubectl-mcp-server.md) — 253-tool k8s MCP; dual Python/npm distribution; optional OAuth 2.1
- [alexei-led/k8s-mcp-server](alexei-led--k8s-mcp-server.md) — Docker-first; k8s/helm/istioctl/argocd wrapper; Python 3.13+ floor
- [feiskyer/mcp-kubernetes-server](feiskyer--mcp-kubernetes-server.md) — four-way verb disable flags
- [ckreiling/mcp-server-docker](ckreiling--mcp-server-docker.md) — Docker management; MCP prompts for docker-compose workflow
- [utensils/mcp-nixos](utensils--mcp-nixos.md) — **two tools total** for package manager with huge surface — token-efficiency strategy

### Infrastructure / IaC / cloud ops (2)
- [severity1/terraform-cloud-mcp](severity1--terraform-cloud-mcp.md) — FastMCP + Pydantic; dual read-only/enable-delete flags
- [baryhuang/mcp-server-aws-resources-python](baryhuang--mcp-server-aws-resources-python.md) — "code-as-tool" AWS: one `exec boto3` tool with AST sandbox

### Observability / monitoring (2)
- [tumf/grafana-loki-mcp](tumf--grafana-loki-mcp.md) — Loki via Grafana; multi-format output (text/JSON/markdown)
- [opensearch-project/opensearch-mcp-server-py](opensearch-project--opensearch-mcp-server-py.md) — project-governed; YAML config; category-based tool gating

### Security (2)
- [mukul975/cve-mcp-server](mukul975--cve-mcp-server.md) — 27 tools across 21 security APIs; rotating JSON audit log
- [FuzzingLabs/mcp-security-hub](FuzzingLabs--mcp-security-hub.md) — monorepo of 38 containerized security-tool MCP servers

### CI/CD (1)
- [lanbaoshen/mcp-jenkins](lanbaoshen--mcp-jenkins.md) — per-request credential headers enable multi-tenant HTTP mode

### Enterprise ITSM / CRM (3)
- [echelon-ai-labs/servicenow-mcp](echelon-ai-labs--servicenow-mcp.md) — transport split across two separate console scripts
- [reminia/zendesk-mcp-server](reminia--zendesk-mcp-server.md) — explicit use of MCP resources primitive for KB access
- [DiversioTeam/clickup-mcp](DiversioTeam--clickup-mcp.md) — `platformdirs`-based persistent config + management subcommands

### Communications / SaaS integrations (8)
- [korotovsky/slack-mcp-server](korotovsky--slack-mcp-server.md) — Go; 4 token types; stealth mode; ships DXT manifest
- [duolingo/slack-mcp](duolingo--slack-mcp.md) — read-only; OAuth 2.1
- [geropl/linear-mcp-go](geropl--linear-mcp-go.md) — Go; pre-built binary releases
- [GLips/Figma-Context-MCP](GLips--Figma-Context-MCP.md) — community canonical Figma server
- [sandraschi/email-mcp](sandraschi--email-mcp.md) — SMTP/IMAP + transactional APIs; FastMCP 3.x
- [sooperset/mcp-atlassian](sooperset--mcp-atlassian.md) — community canonical Jira/Confluence
- [v-3/discordmcp](v-3--discordmcp.md)
- [normaltusker/kotlin-mcp-server](normaltusker--kotlin-mcp-server.md) — Python server for Kotlin/Android dev; not a Kotlin-language server

### Browsers / automation / media (5)
- [executeautomation/mcp-playwright](executeautomation--mcp-playwright.md)
- [twolven/mcp-server-puppeteer-py](twolven--mcp-server-puppeteer-py.md) — legacy setup.py only
- [samuelgursky/davinci-resolve-mcp](samuelgursky--davinci-resolve-mcp.md) — universal installer across 10 hosts; two server modes (27 vs 342 tools)
- [misbahsy/video-audio-mcp](misbahsy--video-audio-mcp.md) — 30+ ffmpeg tools
- [labeveryday/mcp_pdf_reader](labeveryday--mcp_pdf_reader.md) — PDF + OCR; bare-script server

### Home automation (1)
- [voska/hass-mcp](voska--hass-mcp.md) — Home Assistant; Docker-first; long-lived access token

### Healthcare (1)
- [the-momentum/fhir-mcp-server](the-momentum--fhir-mcp-server.md) — FHIR + embedded RAG stack (llama-index + huggingface + pinecone); in-server encrypted credential vault for PHI

### CMS / content (1)
- [thenets/ghost-mcp](thenets--ghost-mcp.md) — dual-API (Content + Admin); JWT auto-renewal; Docker Compose local stack

### Translation / localization (1)
- [AlwaysSany/deepl-fastmcp-python-server](AlwaysSany--deepl-fastmcp-python-server.md) — three transports in one binary; Python 3.13.3 pin via `runtime.txt`

### Not resolvable
- [_missing--riza-io--mcp-server.md](_missing--riza-io--mcp-server.md) — canonical repo name tried; actual Riza MCP is at `riza-io/riza-mcp`

## Per-purpose adoption matrices

Programmatic tallies across all 104 per-repo files, one subsection per section of the per-repo template. Each table answers "which paths appear, at what adoption level, and which repos are representative." Count columns sum to more than N for multi-label sections (noted inline). Cells reporting `unspecified` capture repos whose fields neither confirmed nor ruled out the axis — typically a research-budget gap, not a negative signal.

### Purpose 1 — Language and runtime

Primary language of the server implementation. Multi-language repos are classified by the dominant-language field in section 1; mixed entries note the secondary language.

| Path | Count | Representative repos |
|------|------:|----------------------|
| Python | 58 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, `JackKuo666/PubMed-MCP-Server`, +53 more |
| TypeScript / JS | 26 | `DaInfernalCoder/perplexity-mcp`, `GLips/Figma-Context-MCP`, `HenkDz/postgresql-mcp-server`, `ahmedmustahid/postgres-mcp-server`, `cloudflare/mcp-server-cloudflare`, +21 more |
| Go | 7 | `geropl/linear-mcp-go`, `github/github-mcp-server`, `googleapis/mcp-toolbox`, `korotovsky/slack-mcp-server`, `mark3labs/mcp-go`, +2 more |
| Python + TS (mixed) | 4 | `isaaccorley/planetary-computer-mcp`, `normaltusker/kotlin-mcp-server`, `rohitg00/kubectl-mcp-server`, `utensils/mcp-nixos` |
| Rust | 4 | `apollographql/apollo-mcp-server`, `conikeec/mcpr`, `elastic/mcp-server-elasticsearch`, `rust-mcp-stack/rust-mcp-filesystem` |
| Clojure | 2 | `bhauman/clojure-mcp`, `hugoduncan/mcp-clj` |
| C# / .NET | 1 | `Azure/azure-mcp` (archived) |
| Kotlin | 1 | `modelcontextprotocol/kotlin-sdk` |
| other / unspecified | 1 | `slackapi/slack-mcp-plugin` (configs-only, no server code) |

Outlier note: the only C# and Kotlin entries are an archived vendor server and an SDK, respectively — no community-authored server in these languages surfaced in this sample despite SDKs existing. Denominator: N=104.

### Purpose 2 — Transport

Multi-label: a single repo may ship more than one transport. Counts therefore sum to more than N=104.

| Path | Count | Representative repos |
|------|------:|----------------------|
| stdio | 93 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, `GLips/Figma-Context-MCP`, +88 more |
| http (plain / non-streamable) | 34 | `ClickHouse/mcp-clickhouse`, `DaInfernalCoder/perplexity-mcp`, `GLips/Figma-Context-MCP`, `awslabs/mcp-lambda-handler`, `chroma-core/chroma-mcp`, +29 more |
| sse | 32 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `GLips/Figma-Context-MCP`, `alexei-led/k8s-mcp-server`, `awslabs/mcp`, +27 more |
| streamable-http | 23 | `AlwaysSany/deepl-fastmcp-python-server`, `alexei-led/k8s-mcp-server`, `alpacahq/alpaca-mcp-server`, `apollographql/apollo-mcp-server`, `awslabs/aws-api-mcp-server`, +18 more |
| remote-hosted (service-only) | 3 | `getsentry/sentry-mcp`, `github/github-mcp-server`, `stripe/agent-toolkit` |
| nREPL | 1 | `bhauman/clojure-mcp` — REPL-as-transport |
| unspecified | 1 | `Azure/azure-mcp` (archived) |

Outlier notes: SSE is still present in a third of the sample despite its deprecation in the MCP protocol — removal is a multi-year migration. `bhauman/clojure-mcp`'s nREPL transport is unique: it reuses Clojure's REPL wire protocol instead of MCP's stdio/HTTP framings. Denominator: N=104.

### Purpose 3 — Distribution

Multi-label: most repos ship via more than one channel. Counts sum to more than N=104.

| Path | Count | Representative repos |
|------|------:|----------------------|
| PyPI / uvx | 68 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, +63 more |
| Docker | 57 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `ClickHouse/mcp-clickhouse`, `FuzzingLabs/mcp-security-hub`, `HenkDz/postgresql-mcp-server`, +52 more |
| npm / npx | 41 | `Azure/azure-mcp`, `DaInfernalCoder/perplexity-mcp`, `GLips/Figma-Context-MCP`, `HenkDz/postgresql-mcp-server`, `ahmedmustahid/postgres-mcp-server`, +36 more |
| source-only / from-clone | 28 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `DaInfernalCoder/perplexity-mcp`, `HenkDz/postgresql-mcp-server`, `alexei-led/k8s-mcp-server`, +23 more |
| GitHub release binary | 15 | `apollographql/apollo-mcp-server`, `cloudflare/mcp-server-cloudflare`, `docker/hub-mcp`, `geropl/linear-mcp-go`, `github/github-mcp-server`, +10 more |
| Cargo | 14 | `apollographql/apollo-mcp-server`, `conikeec/mcpr`, `elastic/mcp-server-elasticsearch`, `rust-mcp-stack/rust-mcp-filesystem`, +10 more |
| Go install | 14 | `geropl/linear-mcp-go`, `github/github-mcp-server`, `googleapis/mcp-toolbox`, `mark3labs/mcp-go`, `metoro-io/mcp-golang`, +9 more |
| Homebrew | 14 | `googleapis/mcp-toolbox`, `rust-mcp-stack/rust-mcp-filesystem`, +12 more |
| Smithery | 13 | `DaInfernalCoder/perplexity-mcp`, `HenkDz/postgresql-mcp-server`, `JackKuo666/PubMed-MCP-Server`, `baryhuang/mcp-server-aws-resources-python`, `datalayer/earthdata-mcp-server`, +8 more |
| remote-hosted URL | 7 | `cloudflare/mcp-server-cloudflare`, `exa-labs/exa-mcp-server`, `idosal/git-mcp`, `neondatabase/mcp-server-neon`, `slackapi/slack-mcp-plugin`, +2 more |
| unspecified | 7 | `bhauman/clojure-mcp`, `hugoduncan/mcp-clj`, `mark3labs/mcp-go`, `metoro-io/mcp-golang`, `modelcontextprotocol/kotlin-sdk`, +2 more |
| DXT / MCPB manifest | 2 | `motherduckdb/mcp-server-motherduck`, `sandraschi/email-mcp` |
| Nix flake | 1 | `utensils/mcp-nixos` |

Outlier note: 5-channel distribution (`googleapis/mcp-toolbox` ships Docker + Go install + Homebrew + source + GitHub binary) is the ceiling. DXT/MCPB manifests appear on only 2 repos; Nix flakes on 1 (`utensils/mcp-nixos`). Denominator: N=104.

### Purpose 4 — Entry point / launch

Multi-label: a single repo can ship more than one launch path (e.g., a Python server shipped as both `uvx <package>` and `docker run`). Counts sum to more than N=104.

| Path | Count | Representative repos |
|------|------:|----------------------|
| `npx -y <package>` (npm bin) | 19 | `DaInfernalCoder/perplexity-mcp`, `GLips/Figma-Context-MCP`, `HenkDz/postgresql-mcp-server`, `ahmedmustahid/postgres-mcp-server`, `cloudflare/mcp-server-cloudflare`, +14 more |
| `uvx <package>` (Python console script) | 18 | `DiversioTeam/clickup-mcp`, `alpacahq/alpaca-mcp-server`, `awslabs/aws-api-mcp-server`, `awslabs/mcp`, `chroma-core/chroma-mcp`, +13 more |
| `python -m <module>` (module entry) | 12 | `ClickHouse/mcp-clickhouse`, `JackKuo666/PubMed-MCP-Server`, `PagerDuty/pagerduty-mcp-server`, `awslabs/aws-api-mcp-server`, `echelon-ai-labs/servicenow-mcp`, +7 more |
| bare script at repo root (`python <file>.py`, `node <file>.js`) | 9 | `AlwaysSany/deepl-fastmcp-python-server`, `duolingo/slack-mcp`, `labeveryday/mcp_pdf_reader`, `marlonluo2018/pandas-mcp-server`, `misbahsy/video-audio-mcp`, +4 more |
| remote-hosted URL (no local entry) | 6 | `cloudflare/mcp-server-cloudflare`, `getsentry/sentry-mcp`, `github/github-mcp-server`, `idosal/git-mcp`, `neondatabase/mcp-server-neon`, +1 more |
| Docker container entrypoint (primary) | 5 | `FuzzingLabs/mcp-security-hub`, `awslabs/aws-api-mcp-server`, `awslabs/mcp`, `elastic/mcp-server-elasticsearch`, `voska/hass-mcp` |
| CLI wrapper with subcommands (`<tool> serve`, `<tool> setup`) | 2 | `DiversioTeam/clickup-mcp`, `geropl/linear-mcp-go` |
| pre-built binary (Go/Rust) | 2 | `conikeec/mcpr`, `geropl/linear-mcp-go` |
| library / framework (no server entry) | 2 | `awslabs/mcp-lambda-handler`, `jlowin/fastmcp` |
| other — REPL / SQL PRAGMA | 2 | `hugoduncan/mcp-clj` (nREPL), `teaguesterling/duckdb_mcp` (DuckDB PRAGMA) |
| custom `install.py` installer | 1 | `samuelgursky/davinci-resolve-mcp` |
| `fastmcp install <script>` | 1 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` |
| `nix run` | 1 | `utensils/mcp-nixos` |

Outlier note: the three classes `npx -y <pkg>` (19), `uvx <pkg>` (18), and `python -m <module>` (12) cover the overwhelming majority of host-config launch commands for installable servers — everything else is language-specific (Go/Rust binary) or deliberately non-standard (install.py, fastmcp install). A meaningful share (≈15 repos) didn't surface a clean launch command in the extracted content — Azure/azure-mcp was archived without re-capture, `apollographql/apollo-mcp-server` launches via config-driven binary, and several framework/SDK repos (`mark3labs/mcp-go`, `viant/mcp`, `metoro-io/mcp-golang`) are consumed by library embedding rather than CLI. Denominator: N=104.

### Purpose 5 — Configuration surface

Multi-label: most repos combine env vars with CLI flags or a config file. Counts sum to more than N=104.

| Path | Count | Representative repos |
|------|------:|----------------------|
| env vars only | 44 | `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, `ahmedmustahid/postgres-mcp-server`, `alpacahq/alpaca-mcp-server`, +39 more |
| env vars + CLI flags | 37 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `DaInfernalCoder/perplexity-mcp`, `GLips/Figma-Context-MCP`, `HenkDz/postgresql-mcp-server`, +32 more |
| config file (YAML / TOML / `fastmcp.json` / `.env` file) | 23 | `apollographql/apollo-mcp-server`, `ClickHouse/mcp-clickhouse` (`fastmcp.json`), `cyanheads/git-mcp-server` (`.env.example`), `googleapis/mcp-toolbox` (`tools.yaml`), `opensearch-project/opensearch-mcp-server-py`, +18 more |
| OS keyring / `platformdirs` persistent store | 1 | `DiversioTeam/clickup-mcp` |
| in-server encrypted vault | 1 | `the-momentum/fhir-mcp-server` |
| CLI flags only | 7 | `executeautomation/mcp-playwright`, `jbeno/cursor-notebook-mcp`, `jparkerweb/mcp-sqlite`, `lanbaoshen/mcp-jenkins`, `pragmar/mcp-server-webcrawl`, +2 more |
| OAuth callback flow (cloud-hosted) | 7 | `awslabs/aws-api-mcp-server`, `echelon-ai-labs/servicenow-mcp`, `korotovsky/slack-mcp-server`, `slackapi/slack-mcp-plugin`, `stripe/agent-toolkit`, +2 more |
| unspecified / other | 13 | `JackKuo666/PubMed-MCP-Server`, `conikeec/mcpr`, `idosal/git-mcp`, `isaaccorley/planetary-computer-mcp`, `jlowin/fastmcp`, +8 more |

Note: the original `DiversioTeam/clickup-mcp` `set-api-key` subcommand — which writes to a `platformdirs`-resolved path — is the only repo in the sample choosing an OS keyring-style persistent store over `.env`. The `the-momentum/fhir-mcp-server` in-server encrypted vault is a distinct pattern for PHI-handling servers. The keyring matches heuristically also triggered on 12 mentions of "platformdirs" or "keyring" in prose commentary elsewhere in section 5; only one repo actually stores credentials that way (manually verified). The lower `1/104` count is the structurally correct denominator. Denominator: N=104.

### Purpose 6 — Authentication

| Path | Count | Representative repos |
|------|------:|----------------------|
| static API key / token | 32 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `DaInfernalCoder/perplexity-mcp`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, +27 more |
| OAuth (2.0 or unspecified major) | 24 | `GLips/Figma-Context-MCP`, `apollographql/apollo-mcp-server`, `awslabs/aws-api-mcp-server`, `awslabs/mcp`, `paypal/paypal-mcp-server`, +19 more |
| unspecified | 21 | `HenkDz/postgresql-mcp-server`, `ahmedmustahid/postgres-mcp-server`, `alexei-led/k8s-mcp-server`, `awslabs/bedrock-kb-retrieval-mcp-server`, `baryhuang/mcp-server-aws-resources-python`, +16 more |
| none / zero-auth | 13 | `JackKuo666/PubMed-MCP-Server`, `awslabs/aws-documentation-mcp-server`, `blazickjp/arxiv-mcp-server`, `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `idosal/git-mcp`, +8 more |
| not applicable (framework / config-only) | 9 | `conikeec/mcpr`, `executeautomation/mcp-playwright`, `hugoduncan/mcp-clj`, `jlowin/fastmcp`, `modelcontextprotocol/kotlin-sdk`, +4 more |
| OAuth 2.1 (explicit) | 4 | `cyanheads/perplexity-mcp-server`, `duolingo/slack-mcp`, `rohitg00/kubectl-mcp-server`, `supabase-community/supabase-mcp` |
| long-lived token | 1 | `voska/hass-mcp` |

Outlier note: per-request credential headers (`lanbaoshen/mcp-jenkins`) and in-server credential vault (`the-momentum/fhir-mcp-server`) and JWT auto-renewal (`thenets/ghost-mcp`) are not yet numerous enough to form a category but appear in the "static API key / token" bucket because their primary auth credential is still token-shaped. Denominator: N=104.

### Purpose 7 — Multi-tenancy

| Path | Count | Representative repos |
|------|------:|----------------------|
| single-user / single-workspace (default) | 80 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `DaInfernalCoder/perplexity-mcp`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, +75 more |
| per-request tenant (middleware / header) | 9 | `ClickHouse/mcp-clickhouse`, `HenkDz/postgresql-mcp-server`, `ahmedmustahid/postgres-mcp-server`, `awslabs/mcp-lambda-handler`, `duolingo/slack-mcp`, `lanbaoshen/mcp-jenkins`, +3 more |
| not applicable (framework / config-only) | 8 | `awslabs/aws-documentation-mcp-server`, `conikeec/mcpr`, `hugoduncan/mcp-clj`, `labeveryday/mcp_pdf_reader`, `misbahsy/video-audio-mcp`, +3 more |
| base-directory sandbox | 5 | `alpacahq/alpaca-mcp-server`, `bhauman/clojure-mcp`, `marlonluo2018/pandas-mcp-server`, `paypal/paypal-mcp-server`, `samuelgursky/davinci-resolve-mcp` |
| workspace / OAuth-scoped | 2 | `cyanheads/git-mcp-server`, `jbeno/cursor-notebook-mcp` |

Outlier note: tenancy-as-tool-argument (`sajal2692/mcp-weaviate`) is captured under single-user in the keyword pass but is a distinct pattern worth flagging for Phase 4c vocabulary work. Denominator: N=104.

### Purpose 8 — Capabilities exposed

Two matrices — (a) primitives exposed (primary combination), and (b) tool-count buckets (for repos whose tool count was named).

#### (a) Primitives exposed

Mutually-exclusive primary combination — each repo counted in exactly one row based on the combination of primitives its section 8 body names. Sampling and roots are add-ons reported separately below.

| Combination | Count | Representative repos |
|-------------|------:|----------------------|
| tools only | 88 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `DaInfernalCoder/perplexity-mcp`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, +83 more |
| unspecified | 8 | `Azure/azure-mcp`, `executeautomation/mcp-playwright`, `geropl/linear-mcp-go`, `jparkerweb/mcp-sqlite`, `motherduckdb/mcp-server-motherduck`, +3 more |
| tools + resources | 4 | `ahmedmustahid/postgres-mcp-server`, `designcomputer/mysql_mcp_server`, `reminia/zendesk-mcp-server`, `the-momentum/fhir-mcp-server` |
| tools + prompts | 2 | `googleapis/mcp-toolbox`, `sandraschi/email-mcp` |
| tools + resources + prompts | 1 | `ckreiling/mcp-server-docker` |
| non-tool primitives only (framework case) | 1 | `pragmar/mcp-server-webcrawl` |

Additional add-ons (independent labels, counted separately):

- **Ships sampling**: 8 repos — `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `ktanaka101/mcp-server-duckdb`, `modelcontextprotocol/kotlin-sdk`, `mongodb-js/mongodb-mcp-server`, `redis/mcp-redis`, `sandraschi/email-mcp`, and 2 more.
- **Ships roots**: 9 repos — `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `ktanaka101/mcp-server-duckdb`, `modelcontextprotocol/kotlin-sdk`, `modelcontextprotocol/servers`, `mongodb-js/mongodb-mcp-server`, `redis/mcp-redis`, and 3 more.

Note: the earlier multi-label tally over-counted because it matched the template's own prompt line (`tools / resources / prompts / sampling / roots / logging / other:`) even when the body named only tools. The refined matrix above parses the value side of that line only. Denominator: N=104.

#### (b) Tool-count buckets

Applicable to repos whose section 8 explicitly stated a tool count (21 of 104 did). The remaining 83 did not name a number in the extracted content and are reported as `unspecified`.

| Bucket | Count | Representative repos |
|--------|------:|----------------------|
| 1–5 tools | 4 | `JackKuo666/PubMed-MCP-Server`, `datalayer/earthdata-mcp-server`, `isaaccorley/planetary-computer-mcp`, `marlonluo2018/pandas-mcp-server` |
| 6–20 tools | 7 | `blazickjp/arxiv-mcp-server`, `chroma-core/chroma-mcp`, `korotovsky/slack-mcp-server`, `modelcontextprotocol/servers`, `sajal2692/mcp-weaviate`, +2 more |
| 21–50 tools | 5 | `DiversioTeam/clickup-mcp`, `HenkDz/postgresql-mcp-server`, `cyanheads/git-mcp-server`, `lanbaoshen/mcp-jenkins`, `makenotion/notion-mcp-server` |
| 51–100 tools | 4 | `alpacahq/alpaca-mcp-server`, `mahdin75/gis-mcp`, `mongodb-js/mongodb-mcp-server`, `sooperset/mcp-atlassian` |
| 100+ tools | 1 | `rohitg00/kubectl-mcp-server` (253) |
| unspecified | 83 | remaining sample |

Outlier flags not captured in the buckets above:

- **Deliberate minimalism**: `utensils/mcp-nixos` ships 2 tools; `baryhuang/mcp-server-aws-resources-python` ships 1 `exec_boto3_code` tool with an AST sandbox — token-efficiency strategy, not maturity gap.
- **Extreme-count outliers**: `intuit/quickbooks-online-mcp-server` ships 143 tools per deferred-outlier notes (not in the 104-repo sample). `samuelgursky/davinci-resolve-mcp` exposes 27 tools in compact mode and 342 tools in full mode — selectable at launch.

Denominator: N=104.

### Purpose 9 — Observability

Multi-label: a single repo may combine structured logging with a debug flag and a health endpoint. Counts sum to more than N=104.

| Path | Count | Representative repos |
|------|------:|----------------------|
| not documented in section 9 | 78 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `ClickHouse/mcp-clickhouse`, `DaInfernalCoder/perplexity-mcp`, `FuzzingLabs/mcp-security-hub`, +73 more |
| debug flag / log-level env var (`FASTMCP_LOG_LEVEL`, `--debug`, `LOG_LEVEL`) | 9 | `DiversioTeam/clickup-mcp`, `ahmedmustahid/postgres-mcp-server`, `awslabs/mcp`, `cyanheads/git-mcp-server`, `korotovsky/slack-mcp-server`, +4 more |
| stderr / console only | 9 | `GLips/Figma-Context-MCP`, `chroma-core/chroma-mcp`, `elastic/mcp-server-elasticsearch`, `geropl/linear-mcp-go`, `github/github-mcp-server`, +4 more |
| health endpoint (`/health`, `/ping`) | 3 | `elastic/mcp-server-elasticsearch`, `mongodb-js/mongodb-mcp-server`, `teaguesterling/duckdb_mcp` |
| rotating / audit log | 3 | `awslabs/mcp` (CloudTrail), `mukul975/cve-mcp-server` (JSON audit), `normaltusker/kotlin-mcp-server` (GDPR/HIPAA) |
| structured logging (explicit mention) | 3 | `awslabs/aws-api-mcp-server`, `awslabs/aws-documentation-mcp-server`, `cyanheads/git-mcp-server` |
| OpenTelemetry (traces + metrics) | 2 | `cyanheads/git-mcp-server`, `datalayer/jupyter-mcp-server` |
| tracing (explicit, non-OTel) | 1 | `awslabs/mcp-lambda-handler` |
| Pino logger (Node) | 1 | `cyanheads/git-mcp-server` |
| Winston logger (Node) | 1 | `neondatabase/mcp-server-neon` |
| metrics endpoint | 1 | `awslabs/openapi-mcp-server` |

Note: 78/104 repos had no observability content extracted — this is the axis where research budget was tightest, and the vocabulary below should be read as "what's documented where documented," not a full measurement. An earlier Pass B tally reported 9/104 for "tracing" but 8 of those were false positives where the body explicitly negated tracing (`microsoft/playwright-mcp`: "Tracing and video are capability toggles rather than observability per se"; `chroma-core/chroma-mcp`: "no bespoke metrics/tracing"; `FuzzingLabs/mcp-security-hub`: Trivy scans, not tracing). Pass C corrected to respect negation context. `cyanheads/git-mcp-server` is the richest observability stack in the sample (Pino + OTel + structured logging + debug flag). `mukul975/cve-mcp-server` is distinct for treating audit logs as a first-class capability. Denominator: N=104.

### Purpose 10 — Host integrations shown in README or repo

Yes/no per host — a repo that documents Cursor and Claude Desktop is counted in both rows. Denominator: N=104.

| Host | Count | Representative repos |
|------|------:|----------------------|
| Claude Desktop | 84 | `Azure/azure-mcp`, `ClickHouse/mcp-clickhouse`, `FuzzingLabs/mcp-security-hub`, `GLips/Figma-Context-MCP`, `HenkDz/postgresql-mcp-server`, +79 more |
| Cursor | 42 | `Azure/azure-mcp`, `GLips/Figma-Context-MCP`, `HenkDz/postgresql-mcp-server`, `alpacahq/alpaca-mcp-server`, `apollographql/apollo-mcp-server`, +37 more |
| VS Code / GitHub Copilot | 33 | `Azure/azure-mcp`, `alpacahq/alpaca-mcp-server`, `apollographql/apollo-mcp-server`, `awslabs/mcp`, `cloudflare/mcp-server-cloudflare`, +28 more |
| Claude Code | 32 | `Azure/azure-mcp`, `FuzzingLabs/mcp-security-hub`, `apollographql/apollo-mcp-server`, `awslabs/mcp`, `bhauman/clojure-mcp`, +27 more |
| Windsurf | 21 | `Azure/azure-mcp`, `apollographql/apollo-mcp-server`, `awslabs/mcp`, `cloudflare/mcp-server-cloudflare`, `crystaldba/postgres-mcp`, +16 more |
| Cline | 20 | `Azure/azure-mcp`, `JackKuo666/PubMed-MCP-Server`, `apollographql/apollo-mcp-server`, `awslabs/mcp`, `cloudflare/mcp-server-cloudflare`, +15 more |
| Zed | 15 | `Azure/azure-mcp`, `apollographql/apollo-mcp-server`, `awslabs/mcp`, `cloudflare/mcp-server-cloudflare`, `docker/hub-mcp`, +10 more |
| Continue | 11 | `Azure/azure-mcp`, `apollographql/apollo-mcp-server`, `awslabs/mcp`, `cloudflare/mcp-server-cloudflare`, `docker/hub-mcp`, +6 more |
| Smithery auto-detect | 7 | `JackKuo666/PubMed-MCP-Server`, `baryhuang/mcp-server-aws-resources-python`, `ktanaka101/mcp-server-duckdb`, `mahdin75/gis-mcp`, `openags/paper-search-mcp`, +2 more |
| Codex CLI | 5 | `blazickjp/arxiv-mcp-server`, `exa-labs/exa-mcp-server`, `googleapis/mcp-toolbox`, `microsoft/playwright-mcp`, `motherduckdb/mcp-server-motherduck` |
| Gemini CLI | 5 | `alpacahq/alpaca-mcp-server`, `exa-labs/exa-mcp-server`, `googleapis/mcp-toolbox`, `microsoft/playwright-mcp`, `motherduckdb/mcp-server-motherduck` |
| Kiro | 4 | `awslabs/mcp`, `exa-labs/exa-mcp-server`, `microsoft/playwright-mcp`, `ppl-ai/modelcontextprotocol` |
| OpenAI / Codex | 3 | `cloudflare/mcp-server-cloudflare`, `redis/mcp-redis`, `upstash/context7` |
| Warp | 2 | `exa-labs/exa-mcp-server`, `microsoft/playwright-mcp` |

Distribution shape of host coverage per repo:

| Hosts documented | Repos |
|------------------|------:|
| 0 hosts (configs-only / framework / no host section) | 14 |
| 1 host (typically Claude Desktop) | 22 |
| 2–3 hosts | 44 |
| 4–5 hosts | 10 |
| 6–9 hosts | 12 |
| 10+ hosts | 2 |

Most repos (66/104) document 1–3 hosts. The long tail — 10+ hosts — is held by `samuelgursky/davinci-resolve-mcp` and `exa-labs/exa-mcp-server`, with `microsoft/playwright-mcp`, `alpacahq/alpaca-mcp-server`, `awslabs/mcp`, and `upstash/context7` close behind in the 6–9 band. Denominator: N=104.

### Purpose 11 — Claude Code plugin wrapper

Disambiguates repos that ship a verified wrapper from those that only echo the template's label prompt `(.claude-plugin/plugin.json, ...)` with a negative body ("not observed", "not present"). Each repo manually verified against the value after the `presence and shape:` prompt.

| Shape | Count | Representative repos |
|-------|------:|----------------------|
| none (no wrapper, no `.mcp.json`) | 94 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `DaInfernalCoder/perplexity-mcp`, `DiversioTeam/clickup-mcp`, `HenkDz/postgresql-mcp-server`, +89 more |
| `.claude-plugin/plugin.json` shipped (no `.mcp.json`) | 3 | `exa-labs/exa-mcp-server`, `motherduckdb/mcp-server-motherduck`, `stripe/agent-toolkit` |
| `.claude/skills/` or `skills/` directory (no plugin manifest) | 3 | `blazickjp/arxiv-mcp-server`, `neondatabase/mcp-server-neon`, `openags/paper-search-mcp` |
| `.mcp.json` only (no `.claude-plugin/`) | 2 | `FuzzingLabs/mcp-security-hub`, `modelcontextprotocol/servers` |
| `.claude-plugin/plugin.json` + `.mcp.json` both shipped | 1 | `getsentry/sentry-mcp` |
| `.claude-plugin/marketplace.json` only (marketplace metadata, no plugin.json) | 1 | `upstash/context7` |

Notes on variants and sibling ecosystems:

- `.codex-plugin/` (Codex CLI's plugin format): 1 — `blazickjp/arxiv-mcp-server`.
- `.cursor-plugin/` directory: 2 — `slackapi/slack-mcp-plugin`, `stripe/agent-toolkit` (alongside `.claude-plugin/`).
- DXT manifest (`manifest-dxt.json`, Desktop Extensions): 1 — `korotovsky/slack-mcp-server`.

The prior count ("19 repos with `.claude-plugin/` references") over-attributed because many per-repo files echo the template's label in the prose of the line they answer. The verified count of repos shipping any `.claude-plugin/` artifact (plugin.json + marketplace.json combined) is **5/104**; adding `.mcp.json`-only shipments brings the broader Claude-Code-surface count to **7/104**; adding `.claude/skills/` skill directories (which don't install as plugins but integrate with Claude Code's skill system) brings the total Claude-Code-aware count to **10/104**. Denominator: N=104.

### Purpose 12 — Tests

| Path | Count | Representative repos |
|------|------:|----------------------|
| unspecified | 59 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `DaInfernalCoder/perplexity-mcp`, `HenkDz/postgresql-mcp-server`, `PagerDuty/pagerduty-mcp-server`, +54 more |
| pytest | 30 | `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, `alpacahq/alpaca-mcp-server`, `awslabs/aws-api-mcp-server`, +25 more |
| vitest | 7 | `GLips/Figma-Context-MCP`, `cloudflare/mcp-server-cloudflare`, `cyanheads/git-mcp-server`, `idosal/git-mcp`, `makenotion/notion-mcp-server`, +2 more |
| none / not present | 5 | `JackKuo666/PubMed-MCP-Server`, `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `spences10/mcp-turso-cloud`, `twolven/mcp-server-puppeteer-py`, `v-3/discordmcp` |
| jest | 2 | `executeautomation/mcp-playwright`, `paypal/paypal-mcp-server` |
| Go testing | 1 | `googleapis/mcp-toolbox` |

Outlier note: protocol-conformance e2e harness (`apollographql/apollo-mcp-server`'s `mcp-server-tester` subdirectory) is a distinct pattern not captured by framework tally. The 59 "unspecified" count includes repos where tests exist but the framework wasn't extracted within budget — verification is a Phase 4c task. Denominator: N=104.

### Purpose 13 — CI system

| Path | Count | Representative repos |
|------|------:|----------------------|
| GitHub Actions | 73 | `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, `GLips/Figma-Context-MCP`, `PagerDuty/pagerduty-mcp-server`, +68 more |
| unspecified | 27 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `DaInfernalCoder/perplexity-mcp`, `HenkDz/postgresql-mcp-server`, `JackKuo666/PubMed-MCP-Server`, +22 more |
| none | 4 | `labeveryday/mcp_pdf_reader`, `marlonluo2018/pandas-mcp-server`, `v-3/discordmcp`, `zilliztech/mcp-server-milvus` |

Denominator: N=104. GitHub Actions is effectively the default; no GitLab CI / Buildkite / CircleCI occurrences surfaced.

### Purpose 14 — Container / packaging artifacts

Multi-label — counts sum to more than N=104.

| Path | Count | Representative repos |
|------|------:|----------------------|
| Dockerfile | 63 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `ClickHouse/mcp-clickhouse`, `DaInfernalCoder/perplexity-mcp`, `FuzzingLabs/mcp-security-hub`, +58 more |
| unspecified | 26 | `DiversioTeam/clickup-mcp`, `GLips/Figma-Context-MCP`, `apollographql/apollo-mcp-server`, `awslabs/openapi-mcp-server`, `bhauman/clojure-mcp`, +21 more |
| none / not applicable | 14 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `jbeno/cursor-notebook-mcp`, `ktanaka101/mcp-server-duckdb`, `labeveryday/mcp_pdf_reader`, `mark3labs/mcp-go`, +9 more |
| docker-compose | 12 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `FuzzingLabs/mcp-security-hub`, `ahmedmustahid/postgres-mcp-server`, `cyanheads/git-mcp-server`, +7 more |
| Helm chart | 4 | `docker/hub-mcp`, `github/github-mcp-server`, `modelcontextprotocol/servers`, `redis/mcp-redis` |
| Homebrew formula | 2 | `googleapis/mcp-toolbox`, `modelcontextprotocol/servers` |
| DXT / MCPB manifest | 1 | `sandraschi/email-mcp` |
| systemd unit | 1 | `redis/mcp-redis` |

Outlier note: `FuzzingLabs/mcp-security-hub` ships 38 hardened Dockerfiles with capability-drop / non-root / resource-limit defaults — unusual security posture for MCP. Denominator: N=104.

### Purpose 15 — Example client / developer ergonomics

Multi-label — a repo may combine a Makefile with sample configs and an Inspector launcher. Counts sum to more than N=104.

| Path | Count | Representative repos |
|------|------:|----------------------|
| none shipped / not documented | 72 | `AlwaysSany/deepl-fastmcp-python-server`, `Azure/azure-mcp`, `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, +67 more |
| sample config shipped (host snippets, `.env.example`) | 11 | `DaInfernalCoder/perplexity-mcp`, `alpacahq/alpaca-mcp-server`, `cyanheads/perplexity-mcp-server`, `marlonluo2018/pandas-mcp-server`, `motherduckdb/mcp-server-motherduck`, +6 more |
| Makefile | 10 | `ahmedmustahid/postgres-mcp-server`, `alexei-led/k8s-mcp-server`, `datalayer/earthdata-mcp-server`, `elastic/mcp-server-elasticsearch`, `korotovsky/slack-mcp-server`, +5 more |
| pre-commit hooks | 5 | `awslabs/aws-api-mcp-server`, `isaaccorley/planetary-computer-mcp`, `mahdin75/gis-mcp`, `sooperset/mcp-atlassian`, `tumf/grafana-loki-mcp` |
| `llms.txt` bundled | 3 | `jlowin/fastmcp`, `mahdin75/gis-mcp`, `sooperset/mcp-atlassian` |
| docker-compose for local dev | 3 | `elastic/mcp-server-elasticsearch`, `korotovsky/slack-mcp-server`, `thenets/ghost-mcp` |
| MCP Inspector launcher (in scripts, not `fastmcp dev`) | 2 | `getsentry/sentry-mcp`, `mukul975/cve-mcp-server` |
| `.devcontainer` | 2 | `awslabs/mcp`, `sooperset/mcp-atlassian` |
| Justfile | 1 | `sandraschi/email-mcp` |
| Devbox | 1 | `ckreiling/mcp-server-docker` |
| `fastmcp dev` | 1 | `qdrant/mcp-server-qdrant` |
| `cursor_rules.md` | 1 | `jbeno/cursor-notebook-mcp` |

Note: the 72 repos in the "none shipped" row typically only list host-config JSON snippets in the README, which section 10 counts — section 15 counts dev ergonomics (Inspector, dev launchers, Make/Just targets, dev containers, sample configs beyond host snippets). The low structural adoption of `fastmcp dev` (1/104) despite its first-class status in FastMCP docs is notable — most FastMCP-authoring repos don't document Inspector flows. Denominator: N=104.

### Purpose 16 — Repo layout

Mutually-exclusive primary shape — each repo counted in its dominant layout. Denominator: N=104.

| Path | Count | Representative repos |
|------|------:|----------------------|
| single package, flat layout (no `src/`) | 54 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `DaInfernalCoder/perplexity-mcp`, `DiversioTeam/clickup-mcp`, `GLips/Figma-Context-MCP`, +49 more |
| single package, `src/<pkg>/` layout | 15 | `alexei-led/k8s-mcp-server`, `baryhuang/mcp-server-aws-resources-python`, `blazickjp/arxiv-mcp-server`, `chroma-core/chroma-mcp`, `ckreiling/mcp-server-docker`, +10 more |
| monorepo (unspecified flavor / per-server sub-packages) | 10 | `FuzzingLabs/mcp-security-hub`, `awslabs/mcp`, `awslabs/aws-api-mcp-server`, `awslabs/aws-documentation-mcp-server`, `isaaccorley/planetary-computer-mcp`, +5 more |
| monorepo (pnpm / Turbo workspaces) | 4 | `cloudflare/mcp-server-cloudflare`, `getsentry/sentry-mcp`, `supabase-community/supabase-mcp`, `upstash/context7` |
| bare script / single file (no packaging) | 4 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `labeveryday/mcp_pdf_reader`, `misbahsy/video-audio-mcp`, `twolven/mcp-server-puppeteer-py` |
| extension of host product (DuckDB, Jupyter, VS Code) | 3 | `datalayer/jupyter-mcp-server`, `isaaccorley/planetary-computer-mcp`, `teaguesterling/duckdb_mcp` |
| monorepo (Cargo crates) | 2 | `apollographql/apollo-mcp-server`, `rust-mcp-stack/rust-mcp-filesystem` |
| dispatcher monorepo (one package → multiple servers) | 1 | `pathintegral-institute/mcp.science` |
| configs-only (no server code) | 1 | `slackapi/slack-mcp-plugin` |
| other / unclassified | 10 | `Azure/azure-mcp`, `JackKuo666/PubMed-MCP-Server`, `apollographql/apollo-mcp-server`, `awslabs/bedrock-kb-retrieval-mcp-server`, `awslabs/mcp-lambda-handler`, +5 more |

Note: flat single-package layouts (54/104) outweigh `src/`-layout single packages (15/104) roughly 3.5:1 in the sample, despite `src/` being the packaging community's recommended default. The ten "monorepo (unspecified flavor)" entries include `awslabs/*` sub-server drill-downs which are each first-class PyPI packages within the awslabs/mcp monorepo — counted individually. Dispatcher monorepo (`mcp.science`) and extension-of-host (DuckDB extension) are distinct shapes worth calling out even though each is singular in the sample. Denominator: N=104.

### Purpose 19 — Python-specific

Applies only to the Python-primary subsample. Denominator: N=62 (58 Python + 4 Python+TS mixed that still carry section 19).

#### SDK variant

| Path | Count | Representative repos |
|------|------:|----------------------|
| FastMCP 2.x | 47 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `FuzzingLabs/mcp-security-hub`, `JackKuo666/PubMed-MCP-Server`, +42 more |
| raw mcp SDK | 8 | `crystaldba/postgres-mcp`, `designcomputer/mysql_mcp_server`, `ktanaka101/mcp-server-duckdb`, `modelcontextprotocol/servers`, `pragmar/mcp-server-webcrawl`, +3 more |
| FastMCP 3.x | 5 | `awslabs/aws-api-mcp-server`, `awslabs/mcp`, `awslabs/openapi-mcp-server`, `jlowin/fastmcp`, `sandraschi/email-mcp` |
| FastMCP (unspecified major) | 1 | `pathintegral-institute/mcp.science` |
| FastMCP 1.x (in-SDK namespace) | 1 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` |

Note: FastMCP 2.x is the clear default across the Python sample. FastMCP 3.x has early adopters (awslabs sub-servers, FastMCP itself, `sandraschi/email-mcp`). The raw `mcp` SDK is deliberately chosen by `modelcontextprotocol/servers` reference servers and a few infra-database servers (`crystaldba/postgres-mcp`, `redis/mcp-redis`). A minority carry both `mcp` and `fastmcp` in dependencies simultaneously — `awslabs/mcp` sub-servers, `sooperset/mcp-atlassian`, `normaltusker/kotlin-mcp-server`. Denominator: N=62.

#### Packaging backend

| Path | Count | Representative repos |
|------|------:|----------------------|
| hatchling | 31 | `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `alpacahq/alpaca-mcp-server`, `awslabs/aws-api-mcp-server`, `awslabs/aws-documentation-mcp-server`, +26 more |
| unspecified | 17 | `AlwaysSany/deepl-fastmcp-python-server`, `FuzzingLabs/mcp-security-hub`, `alexei-led/k8s-mcp-server`, `baryhuang/mcp-server-aws-resources-python`, `ckreiling/mcp-server-docker`, +12 more |
| poetry-core | 9 | `JackKuo666/PubMed-MCP-Server`, `PagerDuty/pagerduty-mcp-server`, `blazickjp/arxiv-mcp-server`, `isaaccorley/planetary-computer-mcp`, `jbeno/cursor-notebook-mcp`, +4 more |
| no pyproject / custom installer | 2 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `samuelgursky/davinci-resolve-mcp` |
| setuptools | 2 | `rohitg00/kubectl-mcp-server`, `twolven/mcp-server-puppeteer-py` |
| uv_build | 1 | `the-momentum/fhir-mcp-server` |

Note: hatchling dominates where declared. `redis/mcp-redis` uses `uv_build` (native to uv) — a rare choice. `twolven/mcp-server-puppeteer-py` is still on legacy setup.py. Denominator: N=62.

#### Python version floor

| Path | Count | Representative repos |
|------|------:|----------------------|
| Python 3.10 | 32 | `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `JackKuo666/PubMed-MCP-Server`, `alpacahq/alpaca-mcp-server`, `awslabs/aws-api-mcp-server`, +27 more |
| unspecified | 13 | `FuzzingLabs/mcp-security-hub`, `PagerDuty/pagerduty-mcp-server`, `baryhuang/mcp-server-aws-resources-python`, `ckreiling/mcp-server-docker`, `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, +8 more |
| Python 3.11 | 5 | `blazickjp/arxiv-mcp-server`, `designcomputer/mysql_mcp_server`, `echelon-ai-labs/servicenow-mcp`, `feiskyer/mcp-kubernetes-server`, `utensils/mcp-nixos` |
| Python 3.12 | 5 | `crystaldba/postgres-mcp`, `reminia/zendesk-mcp-server`, `sandraschi/email-mcp`, `severity1/terraform-cloud-mcp`, `the-momentum/fhir-mcp-server` |
| Python 3.13 | 4 | `AlwaysSany/deepl-fastmcp-python-server`, `alexei-led/k8s-mcp-server`, `misbahsy/video-audio-mcp`, `voska/hass-mcp` |
| Python 3.8 | 2 | `normaltusker/kotlin-mcp-server`, `twolven/mcp-server-puppeteer-py` |
| Python 3.9 | 1 | `rohitg00/kubectl-mcp-server` |

Note: Python 3.10 is the clear floor across the Python sample. Python 3.13 floors are the leading edge — all four are small actively-developed community servers. Python 3.8 appears only in legacy/long-lived repos. Denominator: N=62 Python-primary.

## Cross-sample themes worth Phase 3 attention

Impressions from running the research — Phase 3 will confirm via full-file tallies.

**Transport.** `stdio` is near-universal. `HTTP+SSE` and `streamable HTTP` appear on hosted/remote vendor servers and a minority of community servers. SSE is being phased out (Elasticsearch, AWS). Dual-protocol (MCP stdio + REST HTTP simultaneously) appears in `zongmin-yu/semantic-scholar-fastmcp-mcp-server` and `gis-mcp` (REST for file transfer MCP isn't built for).

**Distribution.** `uvx <package>` is the dominant Python host-config launch; `npm/npx` dominates TypeScript; Docker widespread for databases/enterprise; Homebrew/Cargo rare; Go servers often ship pre-built binaries via GitHub releases. Five-channel distribution (`googleapis/mcp-toolbox`) and framework-level Python packaging tool variety (uv, Poetry, pipx, `install.py` bespoke) are the outliers.

**Claude Desktop config snippet in README.** Near-universal for installable servers; absent for config-only/remote repos.

**Claude Code plugin wrapper (`.claude-plugin/`).** Rare — visible in `getsentry/sentry-mcp`, `stripe/agent-toolkit`, `exa-labs/exa-mcp-server`, `slackapi/slack-mcp-plugin`, `upstash/context7` (as `marketplace.json`), `blazickjp/arxiv-mcp-server` (as `.codex-plugin/`). Community servers overwhelmingly rely on users hand-assembling `.mcp.json`.

**Other host configs.** Cursor, VS Code, Windsurf, Zed show up as the common "second+ host" pattern. Higher-integration vendors (exa, context7, davinci-resolve-mcp, alpaca-mcp) enumerate 10+ hosts.

**Authentication.** Static API keys still dominant. OAuth 2.x is emerging for remote-hosted vendors (Supabase, Sentry, Slack, Context7, k8s servers). **Per-request credential headers** (`lanbaoshen/mcp-jenkins`) and **in-server credential vaults** (`fhir-mcp-server`, `thenets/ghost-mcp` JWT auto-renewal) are emerging patterns.

**Multi-tenancy.** Mostly "one server = one user/workspace." Exceptions: per-request tenant via middleware (ClickHouse), OAuth-scoped remote hosting (Neon, Supabase), base-directory sandboxing (cyanheads/git-mcp-server), per-request header tenancy (lanbaoshen/mcp-jenkins), tenancy-as-tool-argument (sajal2692/mcp-weaviate).

**Tests + CI.** Presence correlates with vendor backing. Community servers split — some ship comprehensive Vitest/pytest + GitHub Actions, others ship none.

**Tool-surface philosophy.** Extreme variance: `rohitg00/kubectl-mcp-server` ships 253 tools; `utensils/mcp-nixos` ships 2; `baryhuang/mcp-server-aws-resources-python` ships 1 (code-as-tool with AST sandbox). Token-budget awareness is emerging as a first-class design concern.

**Notable outlier axes (candidates for Phase 3 decision table).**
- Hosted service vs local install (`idosal/git-mcp`, cloudflare, Slack, Neon, Supabase)
- `.claude-plugin/` vs `.claude-plugin/marketplace.json` vs `.codex-plugin/` vs `.cursor-plugin/` vs none
- DXT manifest (`manifest-dxt.json`) — Desktop Extensions format (`korotovsky/slack-mcp-server`)
- Tool catalog as config (Apollo GraphQL operations, awslabs/openapi-mcp-server from OpenAPI specs) vs tool catalog as code
- Server-as-extension (`teaguesterling/duckdb_mcp` embedded in DuckDB SQL)
- Server mode selection — compact vs full tool set (`samuelgursky/davinci-resolve-mcp`: 27 vs 342)
- "Skills" / "prompt routines" shipped alongside the MCP server (exa, context7, Slack plugin, pragmar, sentry, arxiv, openags)
- CLI-wrap vs SDK-wrap vs spec-driven tool generation (all three in awslabs monorepo)
- Monorepo-of-micro-servers (`FuzzingLabs/mcp-security-hub`: 38 containerized servers)
- Entry-point tier: console-script-to-`server:main` vs `__main__.py` vs bare script vs CLI wrapper w/ subcommands (`DiversioTeam/clickup-mcp`)
- Code-as-tool (one exec tool + AST sandbox) vs enumerate-every-API
- Deliberate tool-count minimalism as token-budget strategy
- Orthogonal safety flags (read-only + enable-delete + per-verb-disable)
- Audit logging as first-class capability (`mukul975/cve-mcp-server`)
- In-server credential vaults / JWT auto-renewal (`fhir-mcp-server`, `thenets/ghost-mcp`)
- Transport split across separate console scripts (`echelon-ai-labs/servicenow-mcp`: stdio + SSE binaries)
- Bundled non-MCP LLM context files (`gis-mcp` ships `llms.txt`, `cursor-notebook-mcp` ships `cursor_rules.md`)
- Framework-vs-server distinction (`awslabs/mcp-lambda-handler` is not a server)
- Workflow-driven vs API-driven tools (prompts for `docker-compose` orchestration)
- Protocol + REST bridge in same process (`zongmin-yu`, `gis-mcp`)

## Known sample caveats

- Some `stars` / `last-commit` / contributor counts captured from landing-page views; verify via GitHub before citing.
- Original Phase 2 used Explore-type sub-agents (read-only default) for five batches; four of five couldn't write files and were salvaged via general-purpose replacements. Later Python-focused passes used general-purpose agents throughout.
- `perplexityai/modelcontextprotocol` resolved to `ppl-ai/modelcontextprotocol` — Perplexity's org slug differs from brand.
- `awslabs/mcp-lambda-handler` is a Lambda MCP-building framework, not an MCP server itself. Included because it reveals a genuine sub-category (server-building libraries).
- `normaltusker/kotlin-mcp-server` is a Python server FOR Kotlin/Android development, not a Kotlin-language server.
- `teaguesterling/duckdb_mcp` is C++ primary (DuckDB extension); Python wrapper is secondary.
- Language coverage: strong for Python (~60+), TypeScript (~25+), Go (5+), Rust (3); one Clojure SDK + one Clojure server; one Kotlin SDK; **no C#/Java/Ruby/PHP servers found despite official SDKs existing**. Disclosed gap.
- The `## Python-specific patterns observed (legacy 17-repo deep dive)` section below predates the full Python sample. The new *Purpose 19 — Python-specific* matrices under *Per-purpose adoption matrices* above cover the full N=62 Python-primary sample. The legacy subsection is retained for its qualitative narrative and outlier commentary, not for its tallies.

## Python-specific patterns observed (legacy 17-repo deep dive)

**Note: predates the full Python sample.** This subsection was written during the initial deep-dive pass of 17 Python-primary repos (15 servers + 1 framework `jlowin/fastmcp` + 1 mixed monorepo `modelcontextprotocol/servers`), before the Python sample grew to 62 repos. The *Purpose 19 — Python-specific* matrices above now cover the full sample with programmatic tallies; use those for adoption counts. This subsection is retained for its qualitative observations and outlier narratives (the matrices above deliberately omit prose commentary).

The most common shape across the 17 deep-dived is hatchling + uv + Python 3.10 + a `[project.scripts]` entry + `uvx <name>` as the canonical host-config launch command. Most surprising in the 17: the raw `mcp` SDK and FastMCP are roughly tied (the full-sample matrix above shows FastMCP 2.x dominates once the sample expands). A meaningful minority (`awslabs`, `sooperset/mcp-atlassian`, `normaltusker/kotlin-mcp-server`) pull in BOTH packages simultaneously. Divergence concentrates at the edges: two repos (samuelgursky/davinci-resolve-mcp, normaltusker/kotlin-mcp-server) replace pip entirely with bespoke `install.py` scripts; one (twolven) is stuck on legacy setuptools + no pyproject.toml; one (hannesrudolph) has no packaging at all and ships a single-file script installed via FastMCP's own CLI.

### SDK/framework split

- Raw `mcp` SDK only: 6 — modelcontextprotocol/servers (git, fetch, time), crystaldba/postgres-mcp, redis/mcp-redis, pragmar/mcp-server-webcrawl, designcomputer/mysql_mcp_server, ktanaka101/mcp-server-duckdb
- FastMCP 2.x only: 4 — ClickHouse/mcp-clickhouse, motherduckdb/mcp-server-motherduck, duolingo/slack-mcp, hannesrudolph/sqlite-explorer (FastMCP 0.4.1 — pre-2.x line)
- FastMCP 3.x only: 1 — sandraschi/email-mcp
- Both raw mcp + fastmcp: 3 — awslabs/mcp (per-server mix), sooperset/mcp-atlassian, normaltusker/kotlin-mcp-server
- Framework itself: jlowin/fastmcp
- Custom/unclear: samuelgursky/davinci-resolve-mcp (no pyproject), twolven/mcp-server-puppeteer-py (`mcp-server>=0.1.0` legacy package), pathintegral-institute/mcp.science (dispatcher-only at root, per-server below)

### Host-config launch-command shape

- `uvx <package>` or `uvx <package>@latest`: 9 — ClickHouse, crystaldba, motherduckdb, sooperset, awslabs, modelcontextprotocol/servers (Python servers), ktanaka101, mcp.science, sandraschi
- `uvx --from <package>` (explicit): 1 — redis/mcp-redis
- `uv run --with <package>`: 1 — ClickHouse (alternate); also duolingo (local dev)
- `python -m <pkg>` / `python <script>`: 2 — twolven, samuelgursky (absolute venv-python path)
- `fastmcp install <script>`: 1 — hannesrudolph
- Docker-primary: 1 — duolingo/slack-mcp (no PyPI)
- `python3 install.py` driven (custom installer writes host config): 2 — samuelgursky, normaltusker
- Majority take: `uvx <package-name>` is the dominant host-config `"command"` — unambiguous winner

### Install-workflow recommendation tally

- `uvx`: 11 — the dominant recommendation (ClickHouse, crystaldba, motherduckdb, sooperset, awslabs, redis, ktanaka101, mcp.science, sandraschi, modelcontextprotocol/servers, jlowin-docs)
- `uv` (run/sync/pip): 8 — often alongside uvx for dev
- `pip install`: 9 — usually as alternative, not primary
- `pipx`: 1 — crystaldba (explicitly listed)
- Docker: 6 — awslabs, crystaldba, redis, duolingo (primary), modelcontextprotocol/servers, designcomputer
- Custom installer script: 2 — samuelgursky, normaltusker
- From-source clone only: 2 — hannesrudolph, twolven
- `fastmcp install`: 1 — hannesrudolph

### Packaging-backend tally

- `hatchling.build`: 11 — ClickHouse, crystaldba, motherduckdb, sooperset, awslabs (sampled server), modelcontextprotocol/servers (git+fetch), ktanaka101, mcp.science, designcomputer, jlowin/fastmcp, sandraschi
- `setuptools.build_meta`: 3 — pragmar, duolingo, twolven (legacy setup.py)
- `uv_build`: 1 — redis/mcp-redis (one of the few using uv's native backend)
- No pyproject.toml / no backend: 3 — samuelgursky (install.py only), hannesrudolph (requirements.txt + script), twolven (setup.py only)

### Python version floor distribution

- 3.8: 2 — twolven, normaltusker (floor; broader targeted range up to 3.12)
- 3.10: 10 — ClickHouse, motherduckdb, sooperset, awslabs, modelcontextprotocol/servers (git, fetch), ktanaka101, mcp.science, jlowin/fastmcp, pragmar, duolingo, samuelgursky (3.10–3.12 range with upper bound)
- 3.11: 1 — designcomputer/mysql_mcp_server
- 3.12: 2 — crystaldba, sandraschi
- 3.6+ (stated, probably optimistic): 1 — hannesrudolph
- Not declared: 1 — samuelgursky (no pyproject) — README states 3.10–3.12
- Majority: Python 3.10 is the clear floor; 3.12 appears at the high end and only from repos using modern typing (`TypeAliasType`) or fresh codebases
- **Update from post-deep-dive discovery**: Python 3.13 floor now appears in several actively-developed small servers (`voska/hass-mcp`, `misbahsy/video-audio-mcp`, `AlwaysSany/deepl-fastmcp-python-server`, `alexei-led/k8s-mcp-server`) — leading edge bleeding into community projects

### Notable Python outliers

- **samuelgursky/davinci-resolve-mcp** — no pyproject.toml, no setup.py; entire install is a custom `install.py` (34 KB) that creates a venv and writes per-client JSON for 10 MCP clients. Host config uses absolute venv-Python paths
- **normaltusker/kotlin-mcp-server** — similar custom-installer pattern (`python3 install.py` with 3 modes); carries both `mcp` and `fastmcp` in requirements.txt; single-file 112 KB monolith
- **redis/mcp-redis** — uses `uv_build` native backend (most Python repos use hatchling); PEP 735 `[dependency-groups]`; `src.main:cli` entry point path (unusual `src.` prefix); coverage fail-under=80 enforced in `addopts`
- **crystaldba/postgres-mcp** — Python 3.12 floor, pinned dev-tool versions (ruff==0.14.13, pyright==1.1.408); `src/` layout with explicit `pythonpath` config; uses raw `mcp` SDK despite FastMCP's popularity for PostgreSQL domain
- **sandraschi/email-mcp** — FastMCP 3.x, Cargo.toml alongside pyproject.toml (MCPB signing), console-script name (`schip-mcp-email`) differs from package name (`email-mcp`), Justfile for tasks
- **pathintegral-institute/mcp.science** — dispatcher monorepo: single PyPI package routes to multiple servers via CLI subcommand (`uvx mcp-science <server>`); Hatch `force-include` of nested server dirs
- **hannesrudolph/sqlite-explorer-fastmcp-mcp-server** — pre-`pyproject.toml`-era: `requirements.txt` + single script; pinned to FastMCP 0.4.1 (pre-2.x line); `fastmcp install` CLI-managed distribution
- **twolven/mcp-server-puppeteer-py** — legacy setup.py only, Python 3.8+ floor, entry-point-to-README inconsistency (setup.py registers `mcp_server_puppeteer.server:main` but README runs bare `python puppeteer.py`)
- **jlowin/fastmcp** — framework, not server; exceptionally rich dev deps (pytest-flakefinder, pytest-retry, pytest-xdist, pytest-examples, inline-snapshot); `ty` (new Astral type checker) + `prek` (pre-commit replacement); broad optional-deps groups (anthropic, azure, gemini, openai, apps, code-mode, tasks)
- **awslabs/mcp** — quoted-name console scripts with dots (`"awslabs.aws-api-mcp-server"`) to match dotted PyPI package names; FastMCP 3.x + raw mcp 1.23 dual-sdk
- **modelcontextprotocol/servers** — the reference Python servers (git, fetch, time) deliberately use raw `mcp` SDK with hand-authored schemas, NOT FastMCP — suggests the reference set prioritizes low-level SDK coverage over developer convenience
