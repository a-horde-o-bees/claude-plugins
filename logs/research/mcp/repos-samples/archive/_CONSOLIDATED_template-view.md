---
log-role: reference
---

# MCP Server Corpus — Template-View Consolidation

A section-by-section adoption survey across 104 MCP server samples, mirroring the canonical heading tree from `_TEMPLATE.md`. Each section reports dominant patterns, adoption counts, representative repos, and outliers. The peer document `_CONSOLIDATED_design-view.md` reorganizes the same evidence around the design decisions a builder faces; this document reorganizes it around the data-collection axes the template defines.

**On counts.** Numbers in this document are population estimates summed from the eight batch reports that consolidated the corpus (each batch read 13 alphabetically-grouped samples and returned per-batch tallies). They are reliable for relative magnitude — "dominant", "minority", "rare" — but are not exact tallies. Where a count is critical, regenerate against per-sample files directly. Denominator is N=104 unless otherwise noted.

## Identification

Per-sample identity facts (URL, stars, last-commit, license, default branch, one-line purpose) don't aggregate as adoption signals — they're properties of each repo. A few cross-cutting observations:

- **License distribution** — MIT and Apache-2.0 dominate. Notable outliers: AGPL-3.0 (`HenkDz/postgresql-mcp-server`, `normaltusker/kotlin-mcp-server`), GPL-3.0 (`ckreiling/mcp-server-docker`), CC BY-NC-SA 4.0 (`jbeno/cursor-notebook-mcp` — non-commercial restriction is rare in the ecosystem). `slackapi/slack-mcp-plugin` and `stripe/agent-toolkit` ship dual-licensed structures.
- **Lifecycle signals** — at least four repos are EOL'd: `Azure/azure-mcp` archived (Aug 2025 README, Feb 2026 GitHub flag), `conikeec/mcpr` archived (Feb 2026), `elastic/mcp-server-elasticsearch` carries explicit deprecation (superseded by Elastic Agent Builder 9.2.0+). `paypal/paypal-mcp-server` has 9 stars on a first-party Apache-licensed vendor release — "official but unpromoted" lifecycle signal.
- **Star-count adoption** — `GLips/Figma-Context-MCP` (14.4k) is de facto canonical Figma MCP despite being unofficial; `sooperset/mcp-atlassian` ~5k as community canonical Jira/Confluence. Some vendor-published servers have very low stars (`paypal/paypal-mcp-server` at 9, `sandraschi/email-mcp` at 1) — adoption signal correlates poorly with commercial backing.
- **Default branch** — `main` overwhelmingly; `master` only in legacy holdovers.

## Language and runtime

### language(s) + version constraints

| Language | Count | Representative repos |
|---|---:|---|
| Python | ~58 | most of the corpus |
| TypeScript / JavaScript | ~26 | `GLips/Figma-Context-MCP`, `cloudflare/mcp-server-cloudflare`, `makenotion/notion-mcp-server`, `microsoft/playwright-mcp`, `cyanheads/git-mcp-server`, +many |
| Go | 7 | `mark3labs/mcp-go`, `metoro-io/mcp-golang`, `viant/mcp`, `github/github-mcp-server`, `geropl/linear-mcp-go`, `googleapis/mcp-toolbox`, `korotovsky/slack-mcp-server` |
| Rust | 4–5 | `apollographql/apollo-mcp-server`, `conikeec/mcpr` (archived), `elastic/mcp-server-elasticsearch` (deprecated), `rust-mcp-stack/rust-mcp-filesystem` |
| Clojure | 2 | `bhauman/clojure-mcp`, `hugoduncan/mcp-clj` |
| Kotlin | 1 | `modelcontextprotocol/kotlin-sdk` (SDK, not server) |
| C# / .NET | 1 | `Azure/azure-mcp` (archived) |
| C++ | 1 | `teaguesterling/duckdb_mcp` (DuckDB extension) |
| mixed / configs-only | 2 | `slackapi/slack-mcp-plugin` (configs only), `stripe/agent-toolkit` (TS+Python parallel packages) |

**Python version floor distribution** (n≈58 Python primaries):
- 3.10 — modal floor (~30+)
- 3.11 — `designcomputer/mysql_mcp_server`, `echelon-ai-labs/servicenow-mcp`, `feiskyer/mcp-kubernetes-server`, `utensils/mcp-nixos`, `blazickjp/arxiv-mcp-server`
- 3.12 — `crystaldba/postgres-mcp`, `the-momentum/fhir-mcp-server`, `sandraschi/email-mcp`, `severity1/terraform-cloud-mcp`, `reminia/zendesk-mcp-server`
- 3.13 (leading edge) — `AlwaysSany/deepl-fastmcp-python-server`, `alexei-led/k8s-mcp-server`, `voska/hass-mcp`, `misbahsy/video-audio-mcp`
- 3.8 (legacy) — `twolven/mcp-server-puppeteer-py`, `normaltusker/kotlin-mcp-server`

**Disclosed gap.** No C# (active), Java, Ruby, or PHP servers surfaced despite official SDKs — language coverage is not a population claim.

### framework/SDK in use

Among Python primaries (~58), the FastMCP-vs-raw-mcp split:

| Variant | Count | Representative repos |
|---|---:|---|
| FastMCP 2.x | ~30 | `ClickHouse/mcp-clickhouse`, `alpacahq/alpaca-mcp-server`, `qdrant/mcp-server-qdrant` (pin `2.7.0`), `mahdin75/gis-mcp` (pin `2.13.1`), `jbeno/cursor-notebook-mcp` (pin `<2.11`), +many |
| raw `mcp` SDK | ~12–15 | `modelcontextprotocol/servers` (reference), `crystaldba/postgres-mcp`, `redis/mcp-redis`, `designcomputer/mysql_mcp_server`, `ktanaka101/mcp-server-duckdb`, `pragmar/mcp-server-webcrawl`, `awslabs/aws-documentation-mcp-server`, `awslabs/bedrock-kb-retrieval-mcp-server`, `chroma-core/chroma-mcp` (pin `1.6.0`), `feiskyer/mcp-kubernetes-server`, `samuelgursky/davinci-resolve-mcp`, `lanbaoshen/mcp-jenkins`, `echelon-ai-labs/servicenow-mcp`, `opensearch-project/opensearch-mcp-server-py`, `voska/hass-mcp` |
| FastMCP 3.x (early adopters) | 5 | `awslabs/aws-api-mcp-server`, `awslabs/mcp` umbrella, `awslabs/openapi-mcp-server`, `jlowin/fastmcp` (the framework itself), `sandraschi/email-mcp` |
| FastMCP 1.x | 1 | `marlonluo2018/pandas-mcp-server` |
| FastMCP pre-2.x (0.4.1) | 1 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` |
| Both `mcp` + `fastmcp` simultaneously | 4 | `awslabs/mcp` (per-server mix), `sooperset/mcp-atlassian`, `normaltusker/kotlin-mcp-server`, `openags/paper-search-mcp` |
| Custom hand-rolled (no SDK) | 1 | `awslabs/mcp-lambda-handler` (re-implements protocol on Lambda events) |

For non-Python repos: TS uses `@modelcontextprotocol/sdk` predominantly (with custom or vendor-internal variants in some cases); Go has multiple SDKs (`mark3labs/mcp-go`, `metoro-io/mcp-golang`, `viant/mcp`, plus custom in `github/github-mcp-server`, `googleapis/mcp-toolbox`, `korotovsky/slack-mcp-server`); Rust splits across `rmcp`, `rust-mcp-sdk`.

### pitfalls observed

- FastMCP API drift is real — multiple repos pin exact versions or upper-bound ranges. Builders adopting FastMCP should expect minor-version churn.
- The "kotlin-mcp-server" naming trap: `normaltusker/kotlin-mcp-server` is a Python server *for* Kotlin/Android development, not a Kotlin-language server.
- Dual-pinning `mcp` + `fastmcp` is usually a partial-migration smell rather than deliberate dual stack.

## Transport

### supported transports

Multi-label — a single repo may ship more than one transport.

| Transport | Count | Representative repos |
|---|---:|---|
| stdio | ~93 | universal floor |
| streamable-HTTP | ~25–30 | `cyanheads/git-mcp-server`, `cloudflare/mcp-server-cloudflare`, `apollographql/apollo-mcp-server`, `awslabs/aws-api-mcp-server`, +many |
| SSE (legacy) | ~30 | still present despite protocol-level deprecation |
| plain HTTP | ~30 | various |
| nREPL | 1 | `bhauman/clojure-mcp` (Clojure REPL wire protocol replaces stdio framing) |
| WebSocket | rare | `modelcontextprotocol/kotlin-sdk` |
| in-process / ChannelTransport | rare | `modelcontextprotocol/kotlin-sdk` (testing) |
| SQL PRAGMA | 1 | `teaguesterling/duckdb_mcp` (server starts via `PRAGMA mcp_server_start` inside DuckDB) |
| SFTP | 1 | `jbeno/cursor-notebook-mcp` (remote-notebook operation) |
| dual-protocol (MCP + REST simultaneously) | 2 | `zongmin-yu/semantic-scholar-fastmcp-mcp-server`, `mahdin75/gis-mcp` |

About a third of the corpus is stdio-only; the other two-thirds add at least one HTTP variant.

### how selected

| Mechanism | Count | Notes |
|---|---:|---|
| CLI flag (`--transport`, `--stdio`, `--port`, `--http`) | most multi-transport servers | Modal pattern |
| Env var (`MCP_TRANSPORT`, `TRANSPORT_MODE`) | ~10–15 | Common in Docker-deployed servers |
| Separate console scripts | 1 | `echelon-ai-labs/servicenow-mcp` (`servicenow-mcp-sse` distinct from `python -m servicenow_mcp.cli`) |
| Positional subcommand | 1 | `ahmedmustahid/postgres-mcp-server` |
| Code-level (library/SDK) | Go and Kotlin SDKs |
| URL path on hosted server | `cloudflare/mcp-server-cloudflare` (`/mcp` current, `/sse` deprecated) |

### pitfalls observed

- **SSE is in retreat.** `awslabs/mcp` removed SSE on 2025-05-26. `cloudflare/mcp-server-cloudflare` keeps `/sse` as deprecated. Multi-year migration in progress; current code still ships it.
- **Stdout pollution.** stdio transport requires JSON-RPC framing on stdout; `print()` or `console.log()` debugging corrupts framing. `executeautomation/mcp-playwright` writes logs to `~/playwright-mcp-server.log` specifically as a workaround.

## Distribution

### every mechanism observed

Multi-label.

| Channel | Count | Representative repos |
|---|---:|---|
| PyPI / `uvx` | ~50 | dominant Python channel |
| Docker (Hub / GHCR / vendor) | ~60 | pervasive |
| npm / `npx` | ~26 | dominant TS/JS channel |
| source-only / from-clone | ~20+ | `reminia/zendesk-mcp-server` (no PyPI), `DiversioTeam/clickup-mcp` (git URL), `cyanheads/perplexity-mcp-server`, `v-3/discordmcp`, `shibuiwilliam/mcp-server-scikit-learn` |
| GitHub release binary | ~10–15 | `geropl/linear-mcp-go`, `github/github-mcp-server`, `apollographql/apollo-mcp-server`, `googleapis/mcp-toolbox`, `rust-mcp-stack/rust-mcp-filesystem` |
| Cargo | ~4–5 | Rust servers |
| `go install` | ~7 | Go servers |
| Homebrew | 3 | `googleapis/mcp-toolbox`, `rust-mcp-stack/rust-mcp-filesystem`, `modelcontextprotocol/servers` |
| Smithery | ~7–10 | `JackKuo666/PubMed-MCP-Server` (Smithery without PyPI), `DaInfernalCoder/perplexity-mcp`, `datalayer/earthdata-mcp-server`, `executeautomation/mcp-playwright`, `shreyaskarnik/huggingface-mcp-server` |
| MCPB / `.mcpb` Claude Desktop bundle | 2 | `motherduckdb/mcp-server-motherduck`, `sandraschi/email-mcp` (latter ships Cargo.toml purely for MCPB signing) |
| DXT manifest | 1 | `korotovsky/slack-mcp-server` |
| Nix flake | 1 | `utensils/mcp-nixos` |
| Bespoke `install.py` | 2 | `samuelgursky/davinci-resolve-mcp` (34 KB installer configures 10 hosts), `normaltusker/kotlin-mcp-server` |
| `fastmcp install <script>` | 1 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` |
| `uv run` against source tree | 1 | `zilliztech/mcp-server-milvus` (primary launch, inverts publish-then-uvx convention) |
| remote-hosted URL only | ~7 | `cloudflare/mcp-server-cloudflare`, `idosal/git-mcp`, `neondatabase/mcp-server-neon`, `slackapi/slack-mcp-plugin`, `supabase-community/supabase-mcp`, `getsentry/sentry-mcp` (alongside local) |
| Docker-only (no language registry) | 2 | `voska/hass-mcp`, `duolingo/slack-mcp` |

**Ceiling.** `googleapis/mcp-toolbox` ships 5 channels (Docker + Go install + Homebrew + source + GitHub binary, plus an npm shim that wraps the Go binary).

### published package name(s)

Mostly the obvious projection of the repo name. Notable drift:
- `awslabs/mcp` ships quoted-name console scripts with dots (`"awslabs.aws-api-mcp-server"`) to match dotted PyPI package names.
- `sandraschi/email-mcp`'s console script `schip-mcp-email` doesn't match its package name `email-mcp`.
- `misbahsy/video-audio-mcp` is published as `video-edit-mcp`.
- `voska/hass-mcp` uses bare `app` as its module name.
- `the-momentum/fhir-mcp-server` uses bare `app` as its module name.

### install commands shown in README

The launch verb taxonomy:

| Verb | Count | Notes |
|---|---:|---|
| `uvx <pkg>` | ~18 | Dominant Python host-config launch |
| `npx -y <pkg>` | ~20 | Dominant TS/JS host-config launch |
| `python -m <module>` | ~12 | Python alternative |
| bare script (`python file.py`, `node file.js`) | ~9 | Legacy / minimal |
| Docker container as primary entrypoint | ~5 | `voska/hass-mcp`, `duolingo/slack-mcp`, `awslabs/aws-api-mcp-server`, `elastic/mcp-server-elasticsearch`, `FuzzingLabs/mcp-security-hub` |
| pre-built Go/Rust binary | 2–3 | `geropl/linear-mcp-go`, `conikeec/mcpr` |
| `fastmcp install <script>` | 1 | `hannesrudolph` |
| custom `install.py` | 1 | `samuelgursky/davinci-resolve-mcp` |
| `nix run` | 1 | `utensils/mcp-nixos` |
| remote URL (no local entry) | ~7 | hosted services |

### pitfalls observed

- **Dual PyPI+npm publishing for one Python codebase** — `rohitg00/kubectl-mcp-server` is a notable instance.
- **Pre-pyproject legacy** — `twolven/mcp-server-puppeteer-py` ships only `setup.py`; `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` ships only `requirements.txt` + script.

## Entry point / launch

See *Distribution → install commands* above. Distinctive shapes worth restating:

### wrapper scripts, launchers, stubs

- `samuelgursky/davinci-resolve-mcp` — bespoke 34 KB `install.py` writes per-host JSON for 10 separate MCP host config locations using absolute venv-Python paths.
- `normaltusker/kotlin-mcp-server` — interactive `python3 install.py` with three modes.
- `googleapis/mcp-toolbox` — npm shim wraps a Go binary.

## Configuration surface

### how config reaches the server

Multi-label.

| Channel | Count | Representative repos |
|---|---:|---|
| env vars only | ~40 | `ClickHouse/mcp-clickhouse`, `alpacahq/alpaca-mcp-server`, +many |
| env vars + CLI flags | ~35 | typical multi-mode Python servers |
| config file (YAML / TOML / `fastmcp.json` / `tools.yaml` / `tools.json` / `.env`) | ~20+ | `apollographql/apollo-mcp-server`, `googleapis/mcp-toolbox` (`tools.yaml`), `cyanheads/git-mcp-server` (`.env.example`), `opensearch-project/opensearch-mcp-server-py`, `docker/hub-mcp` (`tools.json`/`tools.txt`), `HenkDz/postgresql-mcp-server` (`tools.json` per-tool enable) |
| CLI flags only | ~5–7 | `executeautomation/mcp-playwright`, `jbeno/cursor-notebook-mcp`, `jparkerweb/mcp-sqlite`, `lanbaoshen/mcp-jenkins`, `pragmar/mcp-server-webcrawl` |
| `platformdirs` / OS-native persistent store | 1 | `DiversioTeam/clickup-mcp` (`set-api-key`/`check-config`/`test-connection` subcommands) |
| in-server encrypted credential vault | 1 | `the-momentum/fhir-mcp-server` (master-key encrypted, PHI) |
| per-request HTTP headers | 2 | `lanbaoshen/mcp-jenkins` (`x-jenkins-*`), `mongodb-js/mongodb-mcp-server` (`mcp-session-id` + `--allowRequestOverrides`) |
| URL query parameters | 2 | `supabase-community/supabase-mcp` (`project_ref`, `read_only`, `features`), `neondatabase/mcp-server-neon` (`category`) |
| OAuth callback flow | ~7 | hosted-service repos |

### pitfalls observed

- **`.env` precedence inverted** — `zilliztech/mcp-server-milvus` lets `.env` override CLI args, opposite of the usual convention. Easy footgun if a deploy assumes CLI-wins.
- **CORS at MCP layer** — `ahmedmustahid/postgres-mcp-server` configures CORS at the MCP boundary, rare and worth knowing if exposing HTTP transport.

## Authentication

### flow

| Path | Count | Representative repos |
|---|---:|---|
| static API key / token | ~32 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `alpacahq/alpaca-mcp-server`, +many |
| OAuth (2.0 or unspecified major) | ~24 | `paypal/paypal-mcp-server`, `apollographql/apollo-mcp-server`, hosted-service repos |
| OAuth 2.1 (explicit) | 4 | `cyanheads/perplexity-mcp-server`, `duolingo/slack-mcp`, `rohitg00/kubectl-mcp-server`, `supabase-community/supabase-mcp` |
| AWS credential chain | ~5–7 | every AWS-adjacent server |
| no auth / zero-auth | ~13 | public-data servers (`awslabs/aws-documentation-mcp-server`, `JackKuo666/PubMed-MCP-Server`, `idosal/git-mcp`, `blazickjp/arxiv-mcp-server`, `microsoft/playwright-mcp` with explicit "not a security boundary" disclaimer) |
| not applicable (framework / config-only) | ~9 | `jlowin/fastmcp`, `mark3labs/mcp-go`, etc. |
| multi-mode auth selectors | ~6–8 | `cyanheads/git-mcp-server` (none/JWT/OIDC), `echelon-ai-labs/servicenow-mcp` (Basic/OAuth/APIKey), `opensearch-project/opensearch-mcp-server-py` (basic/IAM/header/mTLS), `redis/mcp-redis` (Redis ACL + 3 EntraID flows including managed identity), `korotovsky/slack-mcp-server` (4 token types including stealth-mode browser/cookie tokens) |
| long-lived token | 1 | `voska/hass-mcp` |
| two-tier mint (org token mints scoped tokens) | 1 | `spences10/mcp-turso-cloud` (configurable `TOKEN_EXPIRATION` and `TOKEN_PERMISSION`) |
| in-server JWT auto-renewal | 1 | `thenets/ghost-mcp` (every 5 minutes) |
| client-side OAuth2 auto-token-on-401 | 1 | `viant/mcp` SDK |

### where credentials come from

Env var dominant. Notable alternatives:
- **OS-native persistent store** — `DiversioTeam/clickup-mcp` (`platformdirs`).
- **In-server encrypted vault** — `the-momentum/fhir-mcp-server`.
- **Per-request HTTP headers** — `lanbaoshen/mcp-jenkins`, `mongodb-js/mongodb-mcp-server`.
- **kubeconfig / AWS instance role / managed identity** — for cloud-credential-chain servers.
- **OAuth provider callback** — for hosted-service repos.

### pitfalls observed

- **EntraID with managed identity** as one of multiple auth modes (`redis/mcp-redis`) — represents a non-trivial Azure-ecosystem path.

## Multi-tenancy

### tenancy model

| Model | Count | Representative repos |
|---|---:|---|
| single-user / single-process | ~80 | overwhelming default |
| per-request tenant via middleware/header | ~9 | `ClickHouse/mcp-clickhouse` (middleware plugin slot), `lanbaoshen/mcp-jenkins`, `mongodb-js/mongodb-mcp-server`, `awslabs/mcp-lambda-handler` (DynamoDB session backend), `HenkDz/postgresql-mcp-server`, `ahmedmustahid/postgres-mcp-server` |
| OAuth-scoped on hosted endpoint | ~8 | Supabase, Neon, Slack, Stripe, Sentry, GitHub, Cloudflare, Context7 |
| base-directory sandbox | ~5 | `cyanheads/git-mcp-server`, `alpacahq/alpaca-mcp-server`, `bhauman/clojure-mcp`, `marlonluo2018/pandas-mcp-server`, `paypal/paypal-mcp-server`, `samuelgursky/davinci-resolve-mcp` (path-traversal validation) |
| tenancy-as-tool-argument | 1 | `sajal2692/mcp-weaviate` (per-call argument, not server config) |
| URL-param parameterization | 1 | `idosal/git-mcp` (`gitmcp.io/{owner}/{repo}`) |
| AWS-tag-driven scoping | 1 | `awslabs/bedrock-kb-retrieval-mcp-server` (only KBs tagged `mcp-multirag-kb=true`) |
| stateless HTTP toggle | 1 | `utensils/mcp-nixos` (for shared deploys) |
| not applicable | ~9 | frameworks, config-only |

### pitfalls observed

- **Tenancy-as-tool-argument** (`sajal2692/mcp-weaviate`) sidesteps server-side tenancy isolation entirely — every call carries the tenant ID. Distinct enough to warrant its own row in future template revisions.

## Capabilities exposed

### tools / resources / prompts / sampling / roots / logging / other

**Primary primitive combination** (mutually exclusive — each repo counted once):

| Combination | Count | Representative repos |
|---|---:|---|
| tools only | ~88 | overwhelming default |
| tools + resources | ~5–6 | `designcomputer/mysql_mcp_server` (tables-as-resources, explicitly noted as rare), `reminia/zendesk-mcp-server` (KB read), `mongodb-js/mongodb-mcp-server`, `cyanheads/git-mcp-server`, `the-momentum/fhir-mcp-server` |
| tools + prompts | ~4–5 | `googleapis/mcp-toolbox`, `sandraschi/email-mcp`, others |
| tools + resources + prompts | ~3 | `ckreiling/mcp-server-docker`, `awslabs/openapi-mcp-server` (dynamic), `shreyaskarnik/huggingface-mcp-server` (with custom `hf://` URI scheme) |
| non-tool primitives only | 1 | `pragmar/mcp-server-webcrawl` (framework-style with prompt routines) |
| unspecified | ~8 | various |

**Add-on primitives** (independent labels):

- **Sampling**: ~6–8 repos including `modelcontextprotocol/kotlin-sdk`, `mongodb-js/mongodb-mcp-server`, `redis/mcp-redis`, `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `ktanaka101/mcp-server-duckdb`, `sandraschi/email-mcp`.
- **Roots**: ~5–9 repos including `modelcontextprotocol/servers` (filesystem reference), `modelcontextprotocol/kotlin-sdk`, `mongodb-js/mongodb-mcp-server`, `redis/mcp-redis`.
- **Elicitation**: 1 — `mongodb-js/mongodb-mcp-server` for tool confirmation.

**Tool count distribution.** Spans four orders of magnitude — see also `_CONSOLIDATED_design-view.md` for the narrative discussion.

| Bucket | Count | Representative repos |
|---|---:|---|
| 1 tool | 1 | `baryhuang/mcp-server-aws-resources-python` (single `exec boto3` with AST sandbox) |
| 2 tools | ~3 | `utensils/mcp-nixos` (deliberate token-efficiency), `v-3/discordmcp`, `qdrant/mcp-server-qdrant` |
| 3–10 tools | ~12 | typical small servers |
| 11–30 tools | ~12 | `cyanheads/git-mcp-server` (28+1+1), `notion` (22), `lanbaoshen/mcp-jenkins` (24), `cve-mcp-server` (27 across 21 APIs), `clickup-mcp` (28+) |
| 31–60 tools | ~6 | `mahdin75/gis-mcp` (92, exceptional within bucket), `mongodb-js/mongodb-mcp-server` (~60), `alpacahq/alpaca-mcp-server` (~60), `paypal/paypal-mcp-server` (30+), `echelon-ai-labs/servicenow-mcp` (60+), `pagerduty-mcp-server` (65+) |
| 61–100 tools | ~3 | `microsoft/playwright-mcp` (80+), `sooperset/mcp-atlassian` (72) |
| 100+ tools | 2 | `github/github-mcp-server` (100+ across 20+ toolsets), `rohitg00/kubectl-mcp-server` (253) |
| dual-mode (selectable at launch) | 1 | `samuelgursky/davinci-resolve-mcp` (27 vs 342) |
| unspecified | ~60+ | many samples didn't surface a count |

**Capability gating** (cross-cutting design pattern):
- Single read-only toggle — `geropl/linear-mcp-go`, `crystaldba/postgres-mcp` (read-only via pglast SQL parsing).
- Read-only + enable-delete two-axis — `severity1/terraform-cloud-mcp`, `spences10/mcp-turso-cloud`, `alpacahq/alpaca-mcp-server` (paper vs live).
- Per-verb fan-out — `feiskyer/mcp-kubernetes-server` (kubectl/helm/write/delete four-way), `mongodb-js/mongodb-mcp-server` (`--readOnly`/`--indexCheck`/`--dryRun`/elicitation), `motherduckdb/mcp-server-motherduck` (`--read-write`).
- Capability flags / toolsets — `microsoft/playwright-mcp` (`--caps=vision`), `github/github-mcp-server` (`--read-only`/`--lockdown-mode`/toolset flags), `paypal/paypal-mcp-server` (`--tools=all` opt-in), `HenkDz/postgresql-mcp-server` (per-tool enablement, consolidated 46→17 meta-tools).
- Category-based env-var lists — `opensearch-project/opensearch-mcp-server-py`.
- URL-param category — `neondatabase/mcp-server-neon`.
- Skills disable — `getsentry/sentry-mcp` (`MCP_DISABLE_SKILLS`).
- Two-tier write gates — `ClickHouse/mcp-clickhouse` (`WRITE_ACCESS` + `DROP`).
- Tool-disabling — `rust-mcp-stack/rust-mcp-filesystem` (read-only default + per-tool disable).
- Escape hatch — `microsoft/playwright-mcp` (`--allow-unrestricted-file-access`).

### pitfalls observed

- **Dynamic toolsets** — `github/github-mcp-server` `--dynamic-toolsets` mutates the catalog at runtime, breaking the "fixed catalog at startup" assumption hosts typically cache against.

## Observability

### logging destination + format, metrics, tracing, debug flags

The corpus's biggest blind spot — roughly three-quarters of samples surfaced no observability content. Distribution of what was found:

| Path | Count | Representative repos |
|---|---:|---|
| not documented in section | ~78 | majority |
| debug flag / log-level env | ~10 | `MCP_DEBUG`, `FASTMCP_LOG_LEVEL`, `--debug`, `LOG_LEVEL`, `MCP_LOG_FILE` — `DiversioTeam/clickup-mcp`, `ahmedmustahid/postgres-mcp-server`, `awslabs/mcp`, `cyanheads/git-mcp-server`, `korotovsky/slack-mcp-server`, `rohitg00/kubectl-mcp-server` |
| stderr / console only | ~9 | `GLips/Figma-Context-MCP`, `chroma-core/chroma-mcp`, `elastic/mcp-server-elasticsearch`, `geropl/linear-mcp-go`, `github/github-mcp-server` |
| structured logging (explicit) | 3–5 | `cyanheads/git-mcp-server`, `awslabs/aws-api-mcp-server`, `awslabs/aws-documentation-mcp-server` |
| OpenTelemetry (traces + metrics) | 2 | `cyanheads/git-mcp-server`, `datalayer/jupyter-mcp-server` (hard dep) |
| Pino logger (Node) | 1 | `cyanheads/git-mcp-server` |
| Winston logger (Node) | 1 | `neondatabase/mcp-server-neon` |
| `loguru` (Python) | ~5 | `awslabs/*` |
| health endpoint (`/health`, `/ping`) | 3 | `elastic/mcp-server-elasticsearch`, `mongodb-js/mongodb-mcp-server`, `teaguesterling/duckdb_mcp` |
| rotating / audit log | 3 | `awslabs/mcp` (CloudTrail), `mukul975/cve-mcp-server` (JSON audit), `normaltusker/kotlin-mcp-server` (GDPR/HIPAA) |
| metrics endpoint | 1 | `awslabs/openapi-mcp-server` |
| tracing (explicit, non-OTel) | 1 | `awslabs/mcp-lambda-handler` |
| pluggable LOGGERS targeting disk/mcp/stderr | 1 | `mongodb-js/mongodb-mcp-server` |

**Richest observability stack in the corpus**: `cyanheads/git-mcp-server` — Pino + OpenTelemetry + structured logging + debug flag.

### pitfalls observed

- **Stdio-framing constraint** — `executeautomation/mcp-playwright` writes logs to `~/playwright-mcp-server.log` because writing to stdout would corrupt JSON-RPC framing.
- **Negation overcounts** — earlier mechanical sweeps over-counted "tracing" because some samples mention tracing only to negate it. Negation context matters.

## Host integrations shown in README or repo

Yes/no per host — a repo that documents Cursor and Claude Desktop is counted in both rows.

| Host | Count | Notes |
|---|---:|---|
| Claude Desktop | ~84 | universal reference shape |
| Cursor | ~42 | typical "second host" |
| VS Code / GitHub Copilot | ~33 | |
| Claude Code | ~32 | |
| Windsurf | ~21 | |
| Cline | ~20 | |
| Zed | ~15 | |
| Continue | ~11 | |
| Smithery (auto-detect) | ~7 | registry handles host wiring |
| Codex CLI | 5 | `blazickjp/arxiv-mcp-server`, `exa-labs/exa-mcp-server`, `googleapis/mcp-toolbox`, `microsoft/playwright-mcp`, `motherduckdb/mcp-server-motherduck` |
| Gemini CLI | 5 | overlapping set |
| Kiro | 4 | `awslabs/mcp`, `exa-labs/exa-mcp-server`, `microsoft/playwright-mcp`, `ppl-ai/modelcontextprotocol` |
| OpenAI / Codex | 3 | `cloudflare/mcp-server-cloudflare`, `redis/mcp-redis`, `upstash/context7` |
| JetBrains IDEs | 2 | `lanbaoshen/mcp-jenkins`, `alpacahq/alpaca-mcp-server` (PyCharm) |
| Warp | 2 | `exa-labs/exa-mcp-server`, `microsoft/playwright-mcp` |

**Distribution shape** — most repos document 1–3 hosts. Long-tail leaders:
- `samuelgursky/davinci-resolve-mcp` — 10 hosts via custom `install.py`.
- `exa-labs/exa-mcp-server` — 15+ hosts.
- `microsoft/playwright-mcp` — 19+ hosts.
- `awslabs/mcp` — one-click install button URLs replacing JSON copy-paste.
- `alpacahq/alpaca-mcp-server` — 5 hosts including PyCharm.

About 14 repos document **zero hosts** — configs-only, frameworks, or thinly-documented samples.

### pitfalls observed

- Many README "host" sections are flat lists without integration form details — count signals presence in README, not depth of integration.

## Claude Code plugin wrapper

### presence and shape

| Shape | Count | Representative repos |
|---|---:|---|
| none (no wrapper, no `.mcp.json`) | ~94 | overwhelming default |
| `.claude-plugin/plugin.json` shipped | ~3–4 | `getsentry/sentry-mcp` (alongside `.mcp.json`), `stripe/agent-toolkit` (alongside `.cursor-plugin/`), `exa-labs/exa-mcp-server`, `motherduckdb/mcp-server-motherduck` |
| `.claude-plugin/marketplace.json` only | 1 | `upstash/context7` |
| `.mcp.json` only | 2 | `FuzzingLabs/mcp-security-hub`, `modelcontextprotocol/servers` |
| `.claude/skills/` or `skills/` (no plugin manifest) | ~4 | `blazickjp/arxiv-mcp-server` (alongside `.codex-plugin/`), `neondatabase/mcp-server-neon`, `openags/paper-search-mcp`, `slackapi/slack-mcp-plugin`, `apollographql/apollo-mcp-server` (`.claude/` + `CLAUDE.md`) |

**Sibling ecosystems:**
- `.codex-plugin/` (Codex CLI) — 1 (`blazickjp/arxiv-mcp-server`)
- `.cursor-plugin/` — 2 (`slackapi/slack-mcp-plugin`, `stripe/agent-toolkit`)
- DXT manifest — 1 (`korotovsky/slack-mcp-server`)

**Co-shipped agent context files** (related but distinct from plugin wrappers):
- `CLAUDE.md` — `makenotion/notion-mcp-server`, `apollographql/apollo-mcp-server`
- `LLM_CODE_STYLE.md` — `bhauman/clojure-mcp`
- `llms.txt` / `llms-full.txt` — `mahdin75/gis-mcp`, `jlowin/fastmcp`, `sooperset/mcp-atlassian`
- `llm_mcp_docs.txt` (411 KB) — `exa-labs/exa-mcp-server`
- `cursor_rules.md` — `jbeno/cursor-notebook-mcp`

### pitfalls observed

- **Format hasn't converged.** The community is exploring multiple shapes (`.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`, DXT, marketplace.json, raw skills/). None has won.

## Tests

### presence, framework, location, notable patterns

| Path | Count | Representative repos |
|---|---:|---|
| pytest | ~30 | `ClickHouse/mcp-clickhouse`, `DiversioTeam/clickup-mcp`, `alpacahq/alpaca-mcp-server`, `awslabs/aws-api-mcp-server`, +many |
| vitest | ~7 | `GLips/Figma-Context-MCP`, `cloudflare/mcp-server-cloudflare`, `cyanheads/git-mcp-server`, `idosal/git-mcp`, `makenotion/notion-mcp-server` |
| jest | 2 | `executeautomation/mcp-playwright`, `paypal/paypal-mcp-server` |
| Go testing | 3–5 | Go SDKs |
| cargo / nextest | 3–4 | Rust servers |
| Kotlin conformance suite | 1 | `modelcontextprotocol/kotlin-sdk` |
| none / not present | ~5 | `JackKuo666/PubMed-MCP-Server`, `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `spences10/mcp-turso-cloud`, `twolven/mcp-server-puppeteer-py`, `v-3/discordmcp` |
| unspecified (framework not extracted) | ~50+ | research-budget gap |

**Distinctive shapes:**
- Protocol-conformance e2e harness — `apollographql/apollo-mcp-server` (`mcp-server-tester` subdirectory).
- Cassette recording — `geropl/linear-mcp-go` uses go-vcr.
- Custom topology markers — `sooperset/mcp-atlassian` (`dc_e2e`/`cloud_e2e`).
- Eval as peer of test — `getsentry/sentry-mcp` distinguishes `pnpm test` from `pnpm eval`.
- Coverage gate — `redis/mcp-redis` (80% via addopts), `crystaldba/postgres-mcp` pins exact dev-tool versions.
- Doc tests — `jlowin/fastmcp` (pytest-flakefinder, pytest-retry, pytest-xdist, pytest-examples, inline-snapshot, `ty` Astral type-checker, `prek` pre-commit replacement) — richest test discipline in corpus.

### pitfalls observed

- "No tests" claims should be read with the research-budget caveat — many samples confirm a `tests/` directory but framework wasn't extracted.

## CI

### presence, system, triggers, what it runs

| System | Count | Representative repos |
|---|---:|---|
| GitHub Actions | ~73 | effectively monoculture |
| Buildkite (alongside GHA) | 1 | `elastic/mcp-server-elasticsearch` (only non-GHA primary CI surfaced) |
| none | 4–5 | `labeveryday/mcp_pdf_reader`, `marlonluo2018/pandas-mcp-server`, `v-3/discordmcp`, `zilliztech/mcp-server-milvus` |
| unspecified (workflow content not extracted) | ~25 | research-budget gap |

**Distinctive supply-chain and security CI:**
- `FuzzingLabs/mcp-security-hub` — Trivy supply-chain scanning.
- Pre-commit hooks — 5 repos (`awslabs/aws-api-mcp-server`, `isaaccorley/planetary-computer-mcp`, `mahdin75/gis-mcp`, `sooperset/mcp-atlassian`, `tumf/grafana-loki-mcp`).

### pitfalls observed

- No GitLab CI, CircleCI, or other CI systems surfaced as primary — possible undersample (the corpus is GitHub-skewed).

## Container / packaging artifacts

### Dockerfile, docker-compose, Helm, systemd, brew formula, etc.

| Artifact | Count | Representative repos |
|---|---:|---|
| Dockerfile | ~63 | over half the corpus |
| docker-compose | ~12 | `AlwaysSany/deepl-fastmcp-python-server`, `ClickHouse/mcp-clickhouse`, `FuzzingLabs/mcp-security-hub`, `ahmedmustahid/postgres-mcp-server`, `cyanheads/git-mcp-server`, `thenets/ghost-mcp` (full Ghost+MySQL stack) |
| Helm chart | 4 | `docker/hub-mcp`, `github/github-mcp-server`, `modelcontextprotocol/servers`, `redis/mcp-redis` |
| Homebrew formula | 2 | `googleapis/mcp-toolbox`, `modelcontextprotocol/servers` |
| DXT / MCPB manifest | 1 | `sandraschi/email-mcp` |
| systemd unit | 1 | `redis/mcp-redis` |
| WiX-toolset Windows installer | 1 | `rust-mcp-stack/rust-mcp-filesystem` |
| multi-stage muslrust→alpine non-root Docker | 1 | `rust-mcp-stack/rust-mcp-filesystem` |
| 38 hardened Dockerfiles in one repo | 1 | `FuzzingLabs/mcp-security-hub` (capability-drop, non-root, resource-limit defaults, Trivy in CI) |
| none / not applicable | ~14 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `jbeno/cursor-notebook-mcp`, `ktanaka101/mcp-server-duckdb`, `labeveryday/mcp_pdf_reader`, `mark3labs/mcp-go` |

### pitfalls observed

- `FuzzingLabs/mcp-security-hub`'s 38-hardened-Dockerfile pattern is unusual — most MCP servers don't carry container-level hardening discipline.

## Example client / developer ergonomics

### MCP Inspector launcher, curl stubs, make targets, dev scripts, sample configs

| Affordance | Count | Representative repos |
|---|---:|---|
| none shipped / not documented | ~72 | majority |
| sample config (host snippets, `.env.example`) | ~11 | `DaInfernalCoder/perplexity-mcp`, `alpacahq/alpaca-mcp-server`, `cyanheads/perplexity-mcp-server`, `marlonluo2018/pandas-mcp-server`, `motherduckdb/mcp-server-motherduck` |
| Makefile | ~10 | `ahmedmustahid/postgres-mcp-server`, `alexei-led/k8s-mcp-server`, `datalayer/earthdata-mcp-server`, `elastic/mcp-server-elasticsearch`, `korotovsky/slack-mcp-server` |
| pre-commit hooks | 5 | (see CI section) |
| `llms.txt` bundled | 3 | `jlowin/fastmcp`, `mahdin75/gis-mcp`, `sooperset/mcp-atlassian` |
| docker-compose for local dev | 3 | `elastic/mcp-server-elasticsearch`, `korotovsky/slack-mcp-server`, `thenets/ghost-mcp` |
| MCP Inspector launcher (in scripts) | 2 | `getsentry/sentry-mcp`, `mukul975/cve-mcp-server` |
| `.devcontainer` | 2 | `awslabs/mcp`, `sooperset/mcp-atlassian` |
| Justfile | 1 | `sandraschi/email-mcp` |
| Devbox | 1 | `ckreiling/mcp-server-docker` |
| `fastmcp dev` documented | 1 | `qdrant/mcp-server-qdrant` |
| `cursor_rules.md` | 1 | `jbeno/cursor-notebook-mcp` |

### pitfalls observed

- **Low adoption of `fastmcp dev`** (1/104) despite first-class FastMCP status. Most FastMCP-authoring repos don't document Inspector flows.

## Repo layout

### single-package / monorepo / vendored / other

| Path | Count | Representative repos |
|---|---:|---|
| single package, flat layout (no `src/`) | ~54 | majority |
| single package, `src/<pkg>/` layout | ~15 | `alexei-led/k8s-mcp-server`, `baryhuang/mcp-server-aws-resources-python`, `blazickjp/arxiv-mcp-server`, `chroma-core/chroma-mcp`, `ckreiling/mcp-server-docker` |
| monorepo (unspecified flavor / per-server sub-packages) | ~10 | `FuzzingLabs/mcp-security-hub` (38 servers), `awslabs/mcp` (40+ namespace-prefixed packages), `awslabs/aws-api-mcp-server`, `isaaccorley/planetary-computer-mcp` |
| monorepo (pnpm / Turbo / changesets) | 4 | `cloudflare/mcp-server-cloudflare`, `getsentry/sentry-mcp`, `supabase-community/supabase-mcp`, `upstash/context7` |
| bare script / single file (no packaging) | ~7 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `labeveryday/mcp_pdf_reader`, `misbahsy/video-audio-mcp`, `twolven/mcp-server-puppeteer-py`, `v-3/discordmcp`, `samuelgursky/davinci-resolve-mcp`, `shreyaskarnik/huggingface-mcp-server` |
| extension of host product | 3 | `datalayer/jupyter-mcp-server` (Jupyter Server extension), `isaaccorley/planetary-computer-mcp` (sibling VS Code extension), `teaguesterling/duckdb_mcp` (DuckDB extension via SQL PRAGMA) |
| monorepo (Cargo crates) | 2 | `apollographql/apollo-mcp-server`, `rust-mcp-stack/rust-mcp-filesystem` |
| Polylith (bases/components/projects) | 1 | `hugoduncan/mcp-clj` |
| dispatcher monorepo (one package → multiple servers) | 1 | `pathintegral-institute/mcp.science` (Hatch `force-include`) |
| configs-only (no server code) | 1 | `slackapi/slack-mcp-plugin` |
| cross-language reference monorepo | 1 | `modelcontextprotocol/servers` (TS+Python peers, archived servers excised to sibling repo, MIT/Apache-2.0 dual license via contribution gate) |

### pitfalls observed

- Flat single-package layouts (~54) outweigh `src/`-layout single packages (~15) roughly 3.5:1 in the sample, despite `src/` being the Python packaging community's recommended default.

## Notable structural choices

Cross-cutting facts that recur across multiple samples and don't fit a labeled section:

- **Token-budget-conscious tool surface.** Deliberate minimalism (`utensils/mcp-nixos` 2 tools, `baryhuang/mcp-server-aws-resources-python` 1, `v-3/discordmcp` 2). Tool consolidation as response to LLM tool-discovery pressure (`HenkDz/postgresql-mcp-server` 46→17 meta-tools, `awslabs/openapi-mcp-server` claiming 70-75% token reduction from description enrichment).
- **Capability gating combinations** as a coherent design vocabulary — see Capabilities section above.
- **Audit logging as first-class capability** — `mukul975/cve-mcp-server` (rotating JSON audit log with redaction), `normaltusker/kotlin-mcp-server` (GDPR/HIPAA framing), `awslabs/mcp` (CloudTrail integration).
- **In-server credential vault** — `the-momentum/fhir-mcp-server` (master-key encrypted, PHI).
- **JWT auto-renewal in-server** — `thenets/ghost-mcp` (every 5 minutes, dual API).
- **"Skills" / "prompt routines" alongside the server** — `exa-labs/exa-mcp-server`, `getsentry/sentry-mcp` (the "Skills" abstraction), `slackapi/slack-mcp-plugin`, `pragmar/mcp-server-webcrawl` (Markdown "prompt routines"), `blazickjp/arxiv-mcp-server`, `openags/paper-search-mcp`, `upstash/context7`. Agent-shaped artifacts peer-published with the protocol-shaped artifact.
- **Co-shipped LLM context files** — `llms.txt`, `CLAUDE.md`, `cursor_rules.md`, `LLM_CODE_STYLE.md`, `llm_mcp_docs.txt`. The repo ships its own agent-onboarding artifacts.
- **Tool catalog as config** — `apollographql/apollo-mcp-server` (GraphQL operations), `awslabs/openapi-mcp-server` (OpenAPI specs, multi-spec composition), `makenotion/notion-mcp-server` (auto-derived from OpenAPI), `googleapis/mcp-toolbox` (`tools.yaml` with hot reload), `docker/hub-mcp` (`tools.json`/`tools.txt`), `HenkDz/postgresql-mcp-server` (`tools.json` per-tool enable).
- **Code-as-tool with sandbox** — `baryhuang/mcp-server-aws-resources-python` (single `exec boto3` with AST allowlist), `marlonluo2018/pandas-mcp-server` (blacklist-sandboxed pandas — fundamentally weaker trust model).
- **Server mode selection at launch** — `samuelgursky/davinci-resolve-mcp` (27 vs 342), `alpacahq/alpaca-mcp-server` (paper vs live), `motherduckdb/mcp-server-motherduck` (read vs read-write), `chroma-core/chroma-mcp` (4 backing-store modes).
- **Embedded LLM in-server** — `getsentry/sentry-mcp` `EMBEDDED_AGENT_PROVIDER`. Only sample with this.
- **Embedded RAG in-server** — `the-momentum/fhir-mcp-server` (llama-index + pinecone + sentence-transformers + huggingface + pymupdf).
- **Local embedder for zero-key default** — `qdrant/mcp-server-qdrant` (fastembed/ONNX).
- **Workflow-driven prompts as orchestration primitives** — `ckreiling/mcp-server-docker` (docker-compose orchestration).
- **Dual-protocol same-process** — MCP stdio + HTTP REST bridge (`zongmin-yu/semantic-scholar-fastmcp-mcp-server`, `mahdin75/gis-mcp`).
- **Server-as-extension** — `teaguesterling/duckdb_mcp` (DuckDB), `datalayer/jupyter-mcp-server` (Jupyter), `isaaccorley/planetary-computer-mcp` (sibling VS Code extension).
- **REPL-as-transport** — `bhauman/clojure-mcp` (nREPL).
- **Transport split across separate console scripts** — `echelon-ai-labs/servicenow-mcp` (`servicenow-mcp-sse` + `python -m servicenow_mcp.cli`).
- **Stealth-mode tokens** — `korotovsky/slack-mcp-server` (browser/cookie tokens as auth path).
- **Dynamic toolset / runtime catalog mutation** — `github/github-mcp-server` `--dynamic-toolsets`.
- **One-click install button URLs** — `awslabs/mcp` replaces JSON copy-paste with deeplinks.
- **In-server LLM invocation embedded in MCP boundary** — `getsentry/sentry-mcp`.

## Unanticipated axes observed

Design dimensions that recur across samples but the original research framework didn't anticipate as named axes. Candidates for future template revisions:

- **Vendor-vs-community trust** as a first-class axis (vendor-backed / community-canonical / unmaintained-personal). Adoption signal correlates poorly with commercial backing.
- **Paper-mode safety patterns** — `alpacahq/alpaca-mcp-server` paper-trade default for a mutation-capable trading server.
- **Tenancy as tool argument** vs server config — `sajal2692/mcp-weaviate`.
- **Per-request credential headers** for HTTP multi-tenancy.
- **In-server credential vaults / JWT auto-renewal**.
- **"Skills" / "prompt routines"** shipped alongside the MCP server.
- **Co-shipped LLM context files**.
- **Tool catalog as config rather than code**.
- **Code-as-tool with sandbox**.
- **Deliberate tool-count minimalism as token-budget strategy**.
- **Orthogonal safety flag matrices** (read-only × enable-delete × per-verb-disable × dry-run × elicitation).
- **Audit logging as first-class capability**.
- **Server mode selection at launch**.
- **Dynamic toolset / runtime catalog mutation**.
- **Embedded LLM / RAG in-server**.
- **Local embedder for zero-key default**.
- **Workflow-driven prompts as orchestration primitives**.
- **Dual-protocol same-process** (MCP + REST bridge).
- **Server-as-extension** (host-product-embedded).
- **REPL-as-transport**.
- **Transport split across separate console scripts**.

## Python-specific

Applies to the ~58 Python-primary repos.

### SDK / framework variant

See *Language and runtime → framework/SDK in use* above.

### Python version floor

See *Language and runtime → language(s) + version constraints* above.

### Packaging

| Backend | Count | Representative repos |
|---|---:|---|
| hatchling | ~30 | dominant |
| poetry-core | ~9 | `JackKuo666/PubMed-MCP-Server`, `PagerDuty/pagerduty-mcp-server`, `blazickjp/arxiv-mcp-server`, `isaaccorley/planetary-computer-mcp`, `jbeno/cursor-notebook-mcp` |
| uv_build (uv native) | 1–2 | `redis/mcp-redis`, `the-momentum/fhir-mcp-server` |
| setuptools (legacy) | 2 | `rohitg00/kubectl-mcp-server`, `twolven/mcp-server-puppeteer-py` |
| no pyproject / custom installer | 2 | `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `samuelgursky/davinci-resolve-mcp` |
| unspecified | ~17 | research-budget gap |

### Entry point

- Modal: `[project.scripts]` registers a console script that points at `<package>:main` or similar.
- `awslabs/mcp` ships quoted-name console scripts with dots (`"awslabs.aws-api-mcp-server"`) to match dotted PyPI package names.
- `redis/mcp-redis` uses `src.main:cli` (unusual `src.` prefix).
- `sandraschi/email-mcp` console script `schip-mcp-email` doesn't match package name `email-mcp`.

### Install workflow expected of end users

`uvx <package>` is the dominant Python host-config launch (`uv tool install` for persistent install). Alternatives: `pip install`, `pipx`, Docker, custom installer scripts, `fastmcp install`.

### Async and tool signatures

Sparse — most samples didn't surface async vs sync explicitly. Where stated: FastMCP encourages `async def` decorated tools; raw `mcp` SDK has both patterns. Explicit asyncio/anyio usage uncommon.

### Type / schema strategy

- Pydantic dominant for FastMCP-using repos (auto-derived schemas).
- Hand-authored schemas (raw `mcp` SDK) — `modelcontextprotocol/servers` reference, `crystaldba/postgres-mcp`, `redis/mcp-redis`.
- Dataclasses / TypedDict / raw dict — minority.

### Testing

pytest dominant where Python tests exist. pytest-asyncio when async. See *Tests* section.

### Dev ergonomics

- `mcp dev` / `fastmcp dev` — surfaced in only 1 sample (`qdrant/mcp-server-qdrant`).
- MCP Inspector launchers — 2 (`getsentry/sentry-mcp`, `mukul975/cve-mcp-server`).
- Hot-reload — `googleapis/mcp-toolbox` (Go) for tool-config reload.
- Type-check/lint toolchain — `crystaldba/postgres-mcp` pins exact ruff/pyright versions.

### Notable Python-specific choices

- **`uv_build` as native backend** — `redis/mcp-redis`, `the-momentum/fhir-mcp-server`. Rare in ecosystem.
- **PEP 735 dependency-groups** — `redis/mcp-redis`.
- **Coverage fail-under threshold** — `redis/mcp-redis` (80% in addopts).
- **Pinned dev-tool versions** — `crystaldba/postgres-mcp` (ruff==0.14.13, pyright==1.1.408).
- **`requirements.txt` + script (pre-pyproject)** — `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`.
- **Legacy `setup.py` only** — `twolven/mcp-server-puppeteer-py`.
- **No pyproject at all** — `samuelgursky/davinci-resolve-mcp` (custom `install.py`).
- **`Cargo.toml` alongside `pyproject.toml`** — `sandraschi/email-mcp` (Rust used for MCPB signing).
- **Bare `app` module name** — `voska/hass-mcp`, `the-momentum/fhir-mcp-server`.

## Gaps

What couldn't be determined within research budget:

- **Observability** is the largest blind spot. ~78/104 surfaced no observability content. Distinguishing "absent in repo" from "present but not extracted" requires opening repo source for each templated-but-vacuous sample.
- **Tests/CI specifics** — ~50+ samples confirm presence (a `tests/` directory, a CI badge) without naming framework, fixture style, coverage gates, or workflow content.
- **Last-commit dates** are missing or imprecise on a large fraction; landing-page captures are approximate. Verify against GitHub before citing.
- **Async/sync patterns** in tool signatures, schema strategies, and exact entry-point paths frequently weren't extracted within budget.
- **Templated-but-vacuous sections** — several samples have sections that echo the template's prompt without substantive content (notably for thinly-documented small repos like `paypal/paypal-mcp-server`, `riza-io/riza-mcp`, `ppl-ai/modelcontextprotocol`, `slackapi/slack-mcp-plugin` because the server source isn't there). Treat such "not surfaced" lines as research silence, not evidence of absence.
- **Language coverage** — no C# (active), Java, Ruby, or PHP servers surfaced despite official SDKs. The two non-Python/TS/Go entries (Kotlin, C#) are an SDK and an archived vendor server respectively. Disclosed gap, not a population claim.
- **Per-server Docker tagging schemes**, sub-server CI configs, and exact OAuth flow specifics frequently underspecified.
- **CI system diversity** — no GitLab CI, CircleCI, or Buildkite (other than `elastic`'s) surfaced as primary. Possible undersample given the corpus is GitHub-skewed.

## Provenance

Built fresh from the 104 per-sample files in this directory, ignoring `_TEMPLATE.md`, `_INDEX.md`, and the existing `_CONSOLIDATED.md` skeleton. Source: 8 general-purpose subagents reading 13 alphabetically-batched samples each, returning per-sample distinctive observations and per-batch cross-cutting tallies. Counts are summed across batches and reported as estimates; specific repo citations name verified samples. The peer document `_CONSOLIDATED_design-view.md` reorganizes the same evidence around design decisions rather than template axes.
