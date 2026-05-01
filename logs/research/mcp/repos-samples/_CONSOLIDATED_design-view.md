---
log-role: reference
---

# MCP Server Corpus — Design-View Consolidation

A narrative consolidation of 104 MCP server samples organized around the design choices a builder actually faces, not the data-collection template's heading tree. The peer document `_CONSOLIDATED_template-view.md` reorganizes the same evidence around the template's section axes with adoption tables; this document tells the cross-cutting story those tables support.

Built by reading every sample fresh in eight parallel batches of thirteen, without referencing `_CONSOLIDATED.md` or `_INDEX.md`. Counts cited below are derived from those eight batch reports and rounded to the nearest landmark; for per-axis adoption tables see the template-view peer.

## What "an MCP server" actually means here

The corpus collapses three different things under the same label, and almost every other design choice falls out of which one a repo is.

**Local stdio servers** are the dominant shape — somewhere around 80 of the 104. The user installs the package with `uvx`, `npx`, `pip`, `go install`, or `cargo install`; a host process (Claude Desktop, Cursor, VS Code, Claude Code) launches it as a subprocess; messages flow over stdio in JSON-RPC. Almost everything else in this consolidation is a sub-pattern within that shape.

**Remote-hosted services** are a smaller but coherent class: `cloudflare/mcp-server-cloudflare` (14 Workers at hosted URLs), `idosal/git-mcp` (gitmcp.io with per-repo URL parameterization), `neondatabase/mcp-server-neon` (mcp.neon.tech), `slackapi/slack-mcp-plugin` (mcp.slack.com — a configs-only repo with no server source in tree), `supabase-community/supabase-mcp` (mcp.supabase.com/mcp, HTTP-only), `exa-labs/exa-mcp-server` (https://mcp.exa.ai/mcp as primary), `stripe/agent-toolkit` (mcp.stripe.com alongside local), `getsentry/sentry-mcp` (HTTP+stdio dual deploy), `github/github-mcp-server` (stdio + hosted HTTP). These all converge on the same shape: streamable-HTTP transport, OAuth 2.x for tenant identity, no `uvx` install command, the host points at a URL.

**Frameworks and libraries** are not servers at all but get shelved in the same corpus: `jlowin/fastmcp` (the reference Python framework absorbed into the official SDK), `mark3labs/mcp-go`, `metoro-io/mcp-golang`, `viant/mcp`, `hugoduncan/mcp-clj`, `modelcontextprotocol/kotlin-sdk`, `awslabs/mcp-lambda-handler` (a Lambda-MCP framework that re-implements the protocol on API Gateway events without taking a dep on `mcp` or `fastmcp`), `conikeec/mcpr` (archived Rust scaffolding). They show up because someone classified them as MCP repos and they shape what others build, but their template fields are mostly N/A.

**Edge shapes worth naming** because they break the typology:
- **Configs-only repos** that ship no server code — `slackapi/slack-mcp-plugin` is the canonical example (Slack publishes JSON pointing at their hosted endpoint, plus skills/ and commands/).
- **Server-as-extension** — `teaguesterling/duckdb_mcp` is a C++ DuckDB extension where the server starts via `PRAGMA mcp_server_start` inside a SQL session and `ATTACH` mounts other MCPs as data sources; `datalayer/jupyter-mcp-server` runs as either a standalone process or a Jupyter Server extension; `isaaccorley/planetary-computer-mcp` co-locates a TypeScript VS Code extension as a sibling subproject.
- **Dispatcher monorepo** — `pathintegral-institute/mcp.science` ships one PyPI package (`mcp-science`) that routes via CLI subcommand to multiple servers, using Hatch `force-include` of nested server dirs.
- **Server collection monorepo** — `awslabs/mcp` (40+ namespace-prefixed `awslabs.*` PyPI packages from one tree), `FuzzingLabs/mcp-security-hub` (38 hardened-by-default containerized security servers in one repo), `modelcontextprotocol/servers` (TS+Python reference servers as peers), `getsentry/sentry-mcp` (pnpm/Turbo), `cloudflare/mcp-server-cloudflare` (14 hosted Workers), `upstash/context7` and `supabase-community/supabase-mcp` (pnpm/changesets).

## Language and SDK

Python and TypeScript carry the corpus. Python is roughly 60% (the agents collectively saw ~58 Python primaries across 8 batches), TypeScript/JavaScript ~25% (~26 repos), Go ~7%, Rust 4-5 repos, Clojure 2, with one each of Kotlin (the SDK), C# (`Azure/azure-mcp`, archived), and C++ (`teaguesterling/duckdb_mcp` as a DuckDB extension). No C#/Java/Ruby/PHP server surfaced despite official SDKs existing — disclosed corpus gap.

Inside the Python sub-corpus, **FastMCP 2.x is the modal SDK** but the raw `mcp` SDK has a deliberate, persistent minority. Reference servers (`modelcontextprotocol/servers` git/fetch/time) explicitly use raw mcp with hand-authored schemas to model low-level coverage rather than developer convenience. The raw-mcp holdouts also include `crystaldba/postgres-mcp`, `redis/mcp-redis`, `designcomputer/mysql_mcp_server`, `ktanaka101/mcp-server-duckdb`, `pragmar/mcp-server-webcrawl`, `awslabs/aws-documentation-mcp-server`, `awslabs/bedrock-kb-retrieval-mcp-server`, `chroma-core/chroma-mcp` (pinned `mcp==1.6.0`), `feiskyer/mcp-kubernetes-server`, `samuelgursky/davinci-resolve-mcp`, `lanbaoshen/mcp-jenkins`, `echelon-ai-labs/servicenow-mcp`, `opensearch-project/opensearch-mcp-server-py`, `voska/hass-mcp` — concentrated in infra, databases, and AWS-adjacent code.

A small group **pins both `mcp` and `fastmcp` simultaneously** — `awslabs/mcp` (per-server mix, FastMCP 3.x + raw mcp 1.23), `sooperset/mcp-atlassian` (likely partial migration with custom `dc_e2e`/`cloud_e2e` pytest markers), `normaltusker/kotlin-mcp-server`, `openags/paper-search-mcp`. This is usually a migration smell rather than a deliberate dual stack.

**FastMCP version spread** is wider than expected: 0.4.1 (`hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, pre-pyproject single-script), 1.x (`marlonluo2018/pandas-mcp-server`), 2.x dominant, 3.x leading edge (`awslabs/aws-api-mcp-server`, `awslabs/mcp` umbrella, `awslabs/openapi-mcp-server`, `jlowin/fastmcp` itself, `sandraschi/email-mcp`). Several pin exactly: `qdrant/mcp-server-qdrant` at `2.7.0`, `mahdin75/gis-mcp` at `2.13.1`, `jbeno/cursor-notebook-mcp` at `<2.11`. FastMCP API drift is a real concern.

**Python version floors** cluster on 3.10 (modal), with 3.11 (`designcomputer/mysql_mcp_server`, `echelon-ai-labs/servicenow-mcp`, `feiskyer/mcp-kubernetes-server`, `utensils/mcp-nixos`, `blazickjp/arxiv-mcp-server`), 3.12 (`crystaldba/postgres-mcp`, `the-momentum/fhir-mcp-server`, `sandraschi/email-mcp`, `severity1/terraform-cloud-mcp`, `reminia/zendesk-mcp-server`), 3.13 leading edge (`AlwaysSany/deepl-fastmcp-python-server`, `alexei-led/k8s-mcp-server`, `voska/hass-mcp`, `misbahsy/video-audio-mcp`), and 3.8 only in legacy (`twolven/mcp-server-puppeteer-py`, `normaltusker/kotlin-mcp-server`).

**Note on the "kotlin" naming.** `normaltusker/kotlin-mcp-server` is a Python server *for* Kotlin/Android development, not a Kotlin-language server. Easy to miscount.

## Transport

Stdio is the universal floor (~93/104). The interesting question is what gets layered on top.

Roughly a third of repos add HTTP variants — most often streamable-HTTP, sometimes plain HTTP, occasionally SSE (which is being deprecated in the protocol but remains in deployed code). Selection mechanisms vary distinctively:
- **CLI flag** — `--transport`, `--stdio`, `--port`, `--http`. Most common for newer servers.
- **Env var** — `MCP_TRANSPORT`, `TRANSPORT_MODE`. Common for Docker-deployed servers.
- **Separate console script** — `echelon-ai-labs/servicenow-mcp` ships `servicenow-mcp-sse` as a distinct binary alongside `python -m servicenow_mcp.cli`. Unusual but explicit.
- **Positional subcommand** — `ahmedmustahid/postgres-mcp-server` uses `<mode>` as a positional arg.
- **Code-level configuration** — Go and Kotlin SDKs.
- **URL path on a hosted server** — `cloudflare` exposes `/mcp` (current) and `/sse` (deprecated).

**SSE is in retreat.** `awslabs/mcp` removed SSE on 2025-05-26. `cloudflare/mcp-server-cloudflare` keeps `/sse` as deprecated. `elastic/mcp-server-elasticsearch` carries an explicit deprecation notice (superseded by Elastic Agent Builder 9.2.0+). The deprecation is multi-year — about a third of the corpus still ships it.

**Transport oddities worth naming.** `bhauman/clojure-mcp` uses **nREPL as transport** — the Clojure REPL wire protocol replaces stdio framing. `teaguesterling/duckdb_mcp` invokes the server **via SQL `PRAGMA mcp_server_start`** inside a DuckDB session, which is a transport boundary the framework didn't anticipate. `modelcontextprotocol/kotlin-sdk` ships an **in-process `ChannelTransport`** for testing. `jbeno/cursor-notebook-mcp` exposes **SFTP transport** for remote-notebook operation. `zongmin-yu/semantic-scholar-fastmcp-mcp-server` and `mahdin75/gis-mcp` run **dual-protocol simultaneously** — MCP over stdio plus an in-process HTTP REST bridge in the same process, for use cases (file transfer, REST clients) MCP doesn't fit.

## Distribution and launch

Three host-config launch verbs cover almost every installable server: `uvx <pkg>` (Python), `npx -y <pkg>` (TS/JS), `python -m <module>` (Python where uvx isn't preferred). Beyond those:

- **Docker** is pervasive — appears as a distribution channel in well over half the corpus, often alongside PyPI/npm. `voska/hass-mcp` and `duolingo/slack-mcp` are **Docker-only**, with no PyPI publication. `FuzzingLabs/mcp-security-hub` ships **38 hardened Dockerfiles** with capability-drop, non-root, resource-limits and Trivy in CI as the primary deliverable.
- **GitHub release binaries** for Go and Rust servers (`geropl/linear-mcp-go`, `github/github-mcp-server`, `rust-mcp-stack/rust-mcp-filesystem`, `apollographql/apollo-mcp-server`, `googleapis/mcp-toolbox`).
- **Smithery** registry registration — `JackKuo666/PubMed-MCP-Server` distributes via Smithery without PyPI; `DaInfernalCoder/perplexity-mcp`, `datalayer/earthdata-mcp-server`, `executeautomation/mcp-playwright`, `shreyaskarnik/huggingface-mcp-server` register too.
- **Homebrew** is rare (`googleapis/mcp-toolbox`, `rust-mcp-stack/rust-mcp-filesystem`, `modelcontextprotocol/servers`).
- **Five-channel ceiling** — `googleapis/mcp-toolbox` ships Docker + Go install + Homebrew + source clone + GitHub binary + an npm shim that wraps the Go binary.
- **MCPB / `.mcpb` Claude Desktop bundles** appear on `motherduckdb/mcp-server-motherduck` and `sandraschi/email-mcp` (the latter ships a Cargo.toml alongside pyproject.toml purely for MCPB signing).
- **DXT manifest** (`manifest-dxt.json`, Desktop Extensions format) — `korotovsky/slack-mcp-server`.
- **Nix flake** — `utensils/mcp-nixos` (declarative install via Home Manager module).
- **Bespoke `install.py`** — `samuelgursky/davinci-resolve-mcp` ships a 34 KB Python installer that creates a venv and writes per-host JSON for ten different MCP host config locations using absolute venv-Python paths. No pyproject.toml. `normaltusker/kotlin-mcp-server` follows the same pattern with three install modes.
- **`fastmcp install <script>`** — `hannesrudolph/sqlite-explorer-fastmcp-mcp-server` distributes via FastMCP's own CLI, a pre-pyproject artifact.
- **Source-clone-only / editable-install-only** — `reminia/zendesk-mcp-server` (no PyPI), `DiversioTeam/clickup-mcp` (git URL only), `cyanheads/perplexity-mcp-server` (no npm), `v-3/discordmcp`, `shibuiwilliam/mcp-server-scikit-learn` use `uv --directory=...` path-anchored host config.
- **`uv run` against the source tree** — `zilliztech/mcp-server-milvus` lists this as the primary launch, inverting the usual "publish then `uvx`" pattern.

**Python packaging backends** lean on hatchling. Outliers: `redis/mcp-redis` and `the-momentum/fhir-mcp-server` use uv's native `uv_build` (rare); `twolven/mcp-server-puppeteer-py` is still on legacy setup.py with no pyproject; several Python servers carry Poetry+uv dual workflows (`PagerDuty/pagerduty-mcp-server` is the canonical example, with asdf version pinning and Bedrock test artifacts).

**Repo-name-vs-package-name drift** crops up: `awslabs/mcp` ships quoted-name console scripts with dots (`"awslabs.aws-api-mcp-server"`) to match dotted PyPI package names; `sandraschi/email-mcp`'s console script `schip-mcp-email` doesn't match its package name `email-mcp`; `misbahsy/video-audio-mcp` is published as `video-edit-mcp`; `voska/hass-mcp` uses bare `app` as its module name.

## Configuration and credentials

Env vars are dominant — used alone in roughly 40% of the corpus, paired with CLI flags in another third. Configuration files (YAML/TOML/`fastmcp.json`/`tools.yaml`/`tools.json`/`.env`) appear on perhaps a quarter of repos, with `googleapis/mcp-toolbox` and `apollographql/apollo-mcp-server` taking the **declarative-tool-catalog** position (tools defined in YAML or GraphQL operations rather than code).

**Channels worth naming.**
- **`platformdirs`-resolved persistent store** — `DiversioTeam/clickup-mcp` ships its server binary as a doubled management CLI with `set-api-key`, `check-config`, `test-connection` subcommands.
- **In-server encrypted credential vault with master-key encryption** — `the-momentum/fhir-mcp-server` (PHI-handling).
- **Per-request credential headers** — `lanbaoshen/mcp-jenkins` accepts `x-jenkins-*` HTTP headers per request, enabling multi-tenant operation; `mongodb-js/mongodb-mcp-server` uses `mcp-session-id` plus `--allowRequestOverrides`.
- **URL query parameters as config** — `supabase-community/supabase-mcp` accepts `project_ref`, `read_only`, `features` directly in the MCP URL; `neondatabase/mcp-server-neon` uses URL-param `category` for tool filtering.
- **`.env` precedence inverted** — `zilliztech/mcp-server-milvus` lets `.env` override CLI args, opposite of the usual convention.

**Auth flows** split roughly:
- **Static API key / token via env** — modal pattern, ~35% of corpus.
- **OAuth 2.x** — emerging at hosted services (`supabase-community/supabase-mcp` 2.1, `duolingo/slack-mcp` 2.1, `cyanheads/perplexity-mcp-server` 2.1, `rohitg00/kubectl-mcp-server` 2.1 RFC 9728 optional, `paypal/paypal-mcp-server` 2.0, hosted Cloudflare/Sentry/GitHub/Stripe/Slack/Neon).
- **AWS credential chain** — every AWS-adjacent server.
- **No auth** — public-data servers (`awslabs/aws-documentation-mcp-server`, `JackKuo666/PubMed-MCP-Server`, `idosal/git-mcp`, `blazickjp/arxiv-mcp-server`, `hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `executeautomation/mcp-playwright`, `microsoft/playwright-mcp` with explicit "not a security boundary" disclaimer).
- **Multi-mode auth selectors** — `cyanheads/git-mcp-server` (none/JWT/OIDC), `echelon-ai-labs/servicenow-mcp` (Basic/OAuth/APIKey), `opensearch-project/opensearch-mcp-server-py` (basic/IAM/header/mTLS), `redis/mcp-redis` (Redis ACL + 3 EntraID flows including managed identity), `korotovsky/slack-mcp-server` (4 token types including stealth-mode browser/cookie tokens).
- **Two-tier mint** — `spences10/mcp-turso-cloud` uses an org token to mint short-lived per-DB tokens with configurable `TOKEN_EXPIRATION` and `TOKEN_PERMISSION`.
- **In-server JWT auto-renewal** — `thenets/ghost-mcp` rotates every five minutes against the dual Content/Admin Ghost APIs.
- **Client-side OAuth2 auto-token-on-401** — `viant/mcp` SDK retries with token acquisition when challenged.

## Tenancy

Single-user, single-process is the overwhelming default. The escape hatches form distinct families:

- **Per-request middleware/header tenancy** — `ClickHouse/mcp-clickhouse` (middleware plugin slot `MCP_MIDDLEWARE_MODULE` with per-request connection overrides), `lanbaoshen/mcp-jenkins` (`x-jenkins-*` headers), `mongodb-js/mongodb-mcp-server` (session ID + override flag), `awslabs/mcp-lambda-handler` (per-request DynamoDB session backend), `HenkDz/postgresql-mcp-server`, `ahmedmustahid/postgres-mcp-server`.
- **OAuth-scoped on hosted endpoints** — Supabase, Neon, Slack, Stripe, Sentry, GitHub.
- **Base-directory sandboxing** — `cyanheads/git-mcp-server` (multi-tenant base-dir + multi-mode auth), `alpacahq/alpaca-mcp-server` (paper-trade default), `bhauman/clojure-mcp`, `marlonluo2018/pandas-mcp-server`, `paypal/paypal-mcp-server`, `samuelgursky/davinci-resolve-mcp` (path-traversal validation).
- **Tenancy as tool argument** — `sajal2692/mcp-weaviate` is the only sample treating tenancy as a per-call argument rather than server config.
- **Per-repo URL parameterization** — `idosal/git-mcp` exposes `gitmcp.io/{owner}/{repo}`.
- **AWS-tag-driven scoping** — `awslabs/bedrock-kb-retrieval-mcp-server` only surfaces KBs tagged `mcp-multirag-kb=true`.
- **Stateless HTTP toggle** — `utensils/mcp-nixos` for shared deploys.

## Capability surface

**Primitives.** Tools-only is the overwhelming default. Resources show up in `designcomputer/mysql_mcp_server` (tables-as-resources, explicitly noted as rare), `reminia/zendesk-mcp-server` (KB read), `mongodb-js/mongodb-mcp-server`, `cyanheads/git-mcp-server`, `shreyaskarnik/huggingface-mcp-server` (with custom `hf://` URI scheme), `ckreiling/mcp-server-docker`, `the-momentum/fhir-mcp-server`, and the reference-servers monorepo. Prompts as first-class artifacts surface in `googleapis/mcp-toolbox` (declarative YAML), `ckreiling/mcp-server-docker` (docker-compose orchestration), `getsentry/sentry-mcp` (the "Skills" abstraction), `awslabs/mcp` preview SOPs, `shreyaskarnik/huggingface-mcp-server`, `sandraschi/email-mcp`. Sampling and Roots remain rare add-ons (kotlin-sdk, mongodb, modelcontextprotocol/servers filesystem reference, redis).

**Tool counts span four orders of magnitude.** `baryhuang/mcp-server-aws-resources-python` ships a single `exec boto3` tool with an AST sandbox (code-as-tool philosophy). `utensils/mcp-nixos` ships 2 tools for an enormous package-manager surface as a deliberate token-efficiency strategy. `v-3/discordmcp` ships 2. At the other end, `mahdin75/gis-mcp` ships 92 tools across 5 GIS libraries with optional-extras-per-library fan-out, `mongodb-js/mongodb-mcp-server` ~60, `microsoft/playwright-mcp` 80+, `github/github-mcp-server` 100+ across 20+ toolsets with `--dynamic-toolsets` mutating the catalog at runtime, `rohitg00/kubectl-mcp-server` 253, and `samuelgursky/davinci-resolve-mcp` is dual-mode (27 tools compact, 342 tools full, selectable at launch). Token-budget awareness is emerging as a first-class design concern.

**Capability gating** is one of the strongest cross-cutting patterns. The flag combinations span:
- **Single read-only toggle** — `geropl/linear-mcp-go` (`--write-access`), `crystaldba/postgres-mcp` (read-only via pglast SQL parsing).
- **Read-only + enable-delete two-axis** — `severity1/terraform-cloud-mcp` (`READ_ONLY_TOOLS` × `ENABLE_DELETE_TOOLS`), `spences10/mcp-turso-cloud` (read-only + destructive split), `alpacahq/alpaca-mcp-server` (paper vs live trading).
- **Per-verb fan-out** — `feiskyer/mcp-kubernetes-server` (kubectl/helm/write/delete four-way), `mongodb-js/mongodb-mcp-server` (`--readOnly`/`--indexCheck`/`--dryRun`/elicitation confirmation), `motherduckdb/mcp-server-motherduck` (`--read-write`).
- **Capability flags / toolsets** — `microsoft/playwright-mcp` (`--caps=vision`), `github/github-mcp-server` (`--read-only`/`--lockdown-mode`/toolset flags), `paypal/paypal-mcp-server` (`--tools=all` opt-in), `HenkDz/postgresql-mcp-server` (per-tool enablement via `tools.json`, consolidated 46 atomic → 17 meta-tools).
- **Category-based env-var lists** — `opensearch-project/opensearch-mcp-server-py`.
- **URL-param category** — `neondatabase/mcp-server-neon`.
- **Skills disable** — `getsentry/sentry-mcp` (`MCP_DISABLE_SKILLS`).
- **Two-tier write gates** — `ClickHouse/mcp-clickhouse` (`WRITE_ACCESS` + `DROP`).
- **Tool-disabling** — `rust-mcp-stack/rust-mcp-filesystem` (read-only default plus per-tool disable).

`microsoft/playwright-mcp` ships an `--allow-unrestricted-file-access` escape hatch alongside its capability gates, with an explicit "not a security boundary" disclaimer.

## Operations: tests, CI, observability, containers

**Tests.** pytest dominates Python (where extracted), vitest dominates TS/JS, jest a small minority. Coverage gates are rare — `redis/mcp-redis` enforces 80% via addopts; `crystaldba/postgres-mcp` pins exact dev-tool versions (ruff, pyright). Distinctive shapes: `apollographql/apollo-mcp-server`'s `mcp-server-tester` protocol-conformance subdirectory; `geropl/linear-mcp-go` uses go-vcr cassettes; `sooperset/mcp-atlassian` ships custom `dc_e2e`/`cloud_e2e` markers encoding deployment topology; `getsentry/sentry-mcp` distinguishes `pnpm test` from `pnpm eval` (eval as peer of test); `jlowin/fastmcp` carries the richest test discipline in the corpus (pytest-flakefinder, pytest-retry, pytest-xdist, pytest-examples, inline-snapshot, `ty` Astral type-checker, `prek` pre-commit replacement). Many samples have tests that simply weren't extracted within research budget — "no tests" claims should be read with that caveat.

**CI is effectively a GitHub Actions monoculture.** No GitLab CI, CircleCI, or Buildkite surfaced as a primary system except `elastic/mcp-server-elasticsearch`, which uniquely runs **dual GitHub Actions + Buildkite**. `FuzzingLabs/mcp-security-hub` adds **Trivy supply-chain scanning** in CI.

**Observability is the corpus's biggest blind spot.** Roughly three-quarters of samples surfaced no observability content — partly research-budget, partly genuinely absent. The richest stack is **`cyanheads/git-mcp-server`** (Pino + OpenTelemetry + structured logging + debug flag); `datalayer/jupyter-mcp-server` carries OTel as a hard dependency; `mongodb-js/mongodb-mcp-server` ships pluggable LOGGERS targeting disk/mcp/stderr plus a monitoring health endpoint; `mukul975/cve-mcp-server` treats a **rotating JSON audit log with explicit redaction** as a first-class capability. Health endpoints (`/health`, `/ping`) appear on `elastic/mcp-server-elasticsearch`, `mongodb-js/mongodb-mcp-server`, `teaguesterling/duckdb_mcp`. Generic debug flags (`MCP_DEBUG`, `FASTMCP_LOG_LEVEL`, `--debug`, `LOG_LEVEL`, `MCP_LOG_FILE`) appear on roughly a dozen.

**Stdio-framing workaround:** `executeautomation/mcp-playwright` writes logs to `~/playwright-mcp-server.log` because writing to stdout would corrupt JSON-RPC framing — a small but recurring constraint that surfaces when servers cargo-cult `print()` debugging into stdio mode.

**Container artifacts.** Dockerfile present in well over half the corpus; docker-compose appears on a dozen for local-dev or test stacks. Helm charts on `docker/hub-mcp`, `github/github-mcp-server`, `modelcontextprotocol/servers`, `redis/mcp-redis`. Systemd unit on `redis/mcp-redis`. WiX-toolset Windows installer plus muslrust→alpine multi-stage non-root Docker on `rust-mcp-stack/rust-mcp-filesystem` (production-grade packaging for a community filesystem server).

## Host integrations

**Claude Desktop is the universal reference shape** — well over 80% of READMEs show the Claude Desktop config snippet. The next tier (Cursor, VS Code/GitHub Copilot, Claude Code, Windsurf, Cline, Zed, Continue) is the typical "second+ host" pattern.

**Long-tail integration leaders** — `samuelgursky/davinci-resolve-mcp` documents 10 hosts via its custom `install.py`, `exa-labs/exa-mcp-server` enumerates 15+ hosts, `microsoft/playwright-mcp` 19+, `awslabs/mcp` ships one-click install button URLs replacing JSON copy-paste, `alpacahq/alpaca-mcp-server` covers an unusual five hosts including PyCharm. `lanbaoshen/mcp-jenkins` documents JetBrains IDE integration (rare).

**Smithery auto-detect** is its own integration shape — registry handles host wiring without per-host JSON snippets. **Codex CLI / Gemini CLI / Kiro / Warp** appear in the very long tail. **DXT** (Desktop Extensions) appears on `korotovsky/slack-mcp-server`.

About 14 repos document zero hosts — they're configs-only (`slackapi/slack-mcp-plugin`), frameworks (`jlowin/fastmcp`, the Go SDKs), or thin samples where the section was vacuous.

## Claude Code plugin wrapper — what's actually shipped

The headline finding: **the overwhelming majority of repos ship nothing**. No `.claude-plugin/`, no `.mcp.json`, no skills directory. Roughly 90+ of 104 rely entirely on hand-assembled host JSON.

What does ship:
- **`.claude-plugin/plugin.json`** — `getsentry/sentry-mcp` (alongside `.mcp.json`), `stripe/agent-toolkit` (alongside `.cursor-plugin/`), `exa-labs/exa-mcp-server`, `motherduckdb/mcp-server-motherduck`.
- **`.claude-plugin/marketplace.json`** (marketplace metadata, not a plugin manifest) — `upstash/context7`.
- **`.mcp.json` only** — `FuzzingLabs/mcp-security-hub`, `modelcontextprotocol/servers`.
- **`.claude/skills/` or `skills/` without a plugin manifest** — `blazickjp/arxiv-mcp-server` (alongside `.codex-plugin/`), `neondatabase/mcp-server-neon`, `openags/paper-search-mcp`, `slackapi/slack-mcp-plugin`, `apollographql/apollo-mcp-server` (`.claude/` + `CLAUDE.md`).
- **`.codex-plugin/`** — `blazickjp/arxiv-mcp-server`.
- **`.cursor-plugin/`** — `slackapi/slack-mcp-plugin`, `stripe/agent-toolkit`.
- **DXT manifest (`manifest-dxt.json`)** — `korotovsky/slack-mcp-server`.
- **Co-shipped agent context files** — `makenotion/notion-mcp-server` ships `CLAUDE.md`; `bhauman/clojure-mcp` ships `LLM_CODE_STYLE.md`; `mahdin75/gis-mcp` and `jlowin/fastmcp` and `sooperset/mcp-atlassian` ship `llms.txt`; `exa-labs/exa-mcp-server` ships a 411 KB `llm_mcp_docs.txt`; `jbeno/cursor-notebook-mcp` ships `cursor_rules.md`.

The "right" plugin format is unsettled. The community is exploring multiple shapes (`.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/`, DXT, marketplace.json, raw skills/) — none has converged.

## Repo layout

Single-package, flat layout (no `src/`) is the modal shape — comfortably more than half the corpus, despite `src/` being the Python packaging community's recommended default. `src/<pkg>/` shows up in maybe 15 of 104. Bare-script-with-no-packaging persists (`hannesrudolph/sqlite-explorer-fastmcp-mcp-server`, `twolven/mcp-server-puppeteer-py`, `labeveryday/mcp_pdf_reader`, `misbahsy/video-audio-mcp`, `v-3/discordmcp`, `samuelgursky/davinci-resolve-mcp`, `shreyaskarnik/huggingface-mcp-server`).

Distinctive monorepo flavors:
- **Polylith** (bases/components/projects) — `hugoduncan/mcp-clj`.
- **pnpm + changesets / pnpm + Turbo** — `getsentry/sentry-mcp`, `supabase-community/supabase-mcp`, `upstash/context7`, `cloudflare/mcp-server-cloudflare`.
- **Cargo crates** — `apollographql/apollo-mcp-server`, `rust-mcp-stack/rust-mcp-filesystem`.
- **Cross-language reference monorepo** — `modelcontextprotocol/servers` (TS+Python peers, archived servers physically excised to a sibling repo, MIT/Apache-2.0 dual license via contribution gate).
- **One-package-many-servers dispatcher** — `pathintegral-institute/mcp.science` via Hatch `force-include`.
- **Many-packages-namespace-prefixed** — `awslabs/mcp` (`awslabs.aws-api-mcp-server`, etc.).
- **Container-server-per-tool** — `FuzzingLabs/mcp-security-hub` (38 servers).

## Emerging axes the original framework didn't anticipate

These are patterns that recur across multiple samples but didn't have a clean home in the data-collection template's section structure. Each is a candidate first-class dimension for a future research framework.

- **Token-budget-conscious tool surface.** Deliberate minimalism (`utensils/mcp-nixos` 2 tools, `baryhuang/mcp-server-aws-resources-python` 1, `v-3/discordmcp` 2) and tool consolidation (`HenkDz/postgresql-mcp-server` 46→17 meta-tools as explicit response to LLM tool-discovery pressure, `awslabs/openapi-mcp-server` claiming 70-75% token reduction from description enrichment).
- **Capability gating combinations.** Orthogonal flag matrices (read-only × enable-delete × per-verb-disable × dry-run × elicitation) appear in at least a dozen servers and form a coherent design vocabulary.
- **Tenancy as tool argument.** `sajal2692/mcp-weaviate` puts the tenant ID in every tool call rather than the server config — a distinct shape worth naming.
- **Audit logging as first-class capability.** `mukul975/cve-mcp-server` (rotating JSON audit log with redaction), `normaltusker/kotlin-mcp-server` (GDPR/HIPAA framing), `awslabs/mcp` (CloudTrail integration).
- **In-server credential vault.** `the-momentum/fhir-mcp-server` (master-key encrypted, PHI).
- **JWT auto-renewal in-server.** `thenets/ghost-mcp` (every 5 minutes, dual API).
- **Per-request credential headers for HTTP multi-tenancy.** `lanbaoshen/mcp-jenkins`, `mongodb-js/mongodb-mcp-server`.
- **"Skills" / "prompt routines" alongside the server.** `exa-labs/exa-mcp-server`, `getsentry/sentry-mcp` (the "Skills" abstraction), `slackapi/slack-mcp-plugin`, `pragmar/mcp-server-webcrawl` (Markdown "prompt routines" shipped alongside tools), `blazickjp/arxiv-mcp-server`, `openags/paper-search-mcp`, `upstash/context7`. Distinct enough to deserve a name; the agent-shaped artifact peer-published with the protocol-shaped artifact.
- **Co-shipped LLM context files.** `llms.txt`, `CLAUDE.md`, `cursor_rules.md`, `LLM_CODE_STYLE.md`, `llm_mcp_docs.txt`. The repo ships its own agent-onboarding artifacts.
- **Tool catalog as config rather than code.** `apollographql/apollo-mcp-server` (GraphQL operations), `awslabs/openapi-mcp-server` (OpenAPI specs, multi-spec composition + per-spec auth), `makenotion/notion-mcp-server` (auto-derived from OpenAPI), `googleapis/mcp-toolbox` (`tools.yaml` with hot reload), `docker/hub-mcp` (`tools.json`/`tools.txt`), `HenkDz/postgresql-mcp-server` (`tools.json` per-tool enable).
- **Code-as-tool with sandbox.** `baryhuang/mcp-server-aws-resources-python` (single `exec boto3` tool with AST allowlist), `marlonluo2018/pandas-mcp-server` (blacklist-sandboxed pandas — fundamentally weaker trust model), `microsoft/playwright-mcp` (programmatic API surface).
- **Server mode selection at launch.** `samuelgursky/davinci-resolve-mcp` (27 vs 342 tools), `alpacahq/alpaca-mcp-server` (paper vs live), `motherduckdb/mcp-server-motherduck` (read vs read-write), `chroma-core/chroma-mcp` (4 backing-store modes via flags).
- **Dynamic toolset / runtime catalog mutation.** `github/github-mcp-server` `--dynamic-toolsets` breaks the "fixed catalog at startup" assumption hosts typically cache against.
- **Embedded LLM in-server.** `getsentry/sentry-mcp` `EMBEDDED_AGENT_PROVIDER` invokes an LLM inside the MCP boundary — only sample with this.
- **Embedded RAG in-server.** `the-momentum/fhir-mcp-server` carries llama-index + pinecone + sentence-transformers + huggingface + pymupdf as core deps.
- **Local embedder for zero-key default.** `qdrant/mcp-server-qdrant` ships `fastembed` (ONNX) so the server works without an embedding API key.
- **Workflow-driven prompts as orchestration primitives.** `ckreiling/mcp-server-docker` exposes MCP prompts that drive docker-compose orchestration.
- **Dual-protocol same-process.** MCP stdio plus HTTP REST bridge (`zongmin-yu/semantic-scholar-fastmcp-mcp-server`, `mahdin75/gis-mcp` for file transfer).
- **Server-as-extension.** `teaguesterling/duckdb_mcp` (DuckDB), `datalayer/jupyter-mcp-server` (Jupyter Server extension), `isaaccorley/planetary-computer-mcp` (sibling VS Code extension).
- **REPL-as-transport.** `bhauman/clojure-mcp` reuses Clojure's nREPL wire protocol instead of stdio framing.
- **Transport split across separate console scripts.** `echelon-ai-labs/servicenow-mcp` ships `servicenow-mcp-sse` and `python -m servicenow_mcp.cli` as distinct binaries.
- **Vendor-vs-community trust as a first-class axis.** Vendor-backed (Stripe, PayPal, Slack, Sentry, Cloudflare, Supabase, Neon, Notion, GitHub, Apollo, Elastic, Redis, Google APIs, AWS Labs, MongoDB, Docker, Anthropic) versus community-canonical (`sooperset/mcp-atlassian` 5k stars, `GLips/Figma-Context-MCP` 14.4k stars, `spences10/mcp-turso-cloud`) versus unmaintained-personal-project. Adoption signal correlates poorly with commercial backing.

## Outliers worth knowing exist

Short list — repos where one or more facets sit far enough outside the modal shape that they're worth indexing for "could I do that" lookups:

- `bhauman/clojure-mcp` — nREPL-as-transport.
- `teaguesterling/duckdb_mcp` — server lives inside a SQL session as a DuckDB extension; can `ATTACH` other MCPs as data sources.
- `baryhuang/mcp-server-aws-resources-python` — single `exec boto3` tool with AST sandbox; code-as-tool philosophy.
- `utensils/mcp-nixos` — 2 tools for an enormous package-manager surface; declarative install via Nix flake.
- `mahdin75/gis-mcp` — 92 tools across 5 GIS libraries with optional-extras-per-library fan-out.
- `the-momentum/fhir-mcp-server` — embedded RAG stack plus encrypted credential vault for PHI.
- `rohitg00/kubectl-mcp-server` — 253 tools, dual PyPI+npm distribution, optional OAuth 2.1 RFC 9728 layered onto a stdio server.
- `samuelgursky/davinci-resolve-mcp` — bespoke `install.py` configures 10 hosts; dual-mode 27-vs-342 tools.
- `FuzzingLabs/mcp-security-hub` — 38 hardened containerized servers in one monorepo, Trivy in CI.
- `pathintegral-institute/mcp.science` — single-package dispatcher routing to many servers via subcommand.
- `pragmar/mcp-server-webcrawl` — "prompt routines" as Markdown shipped alongside tools; reads pre-captured archives (7 crawler formats).
- `awslabs/mcp-lambda-handler` — Lambda MCP framework with no `mcp` or `fastmcp` dep; pluggable DynamoDB session backend.
- `awslabs/openapi-mcp-server` — pyproject version literally `0.9223372036854775807.9223372036854775807` (int64 max sentinel from automated release).
- `microsoft/playwright-mcp` — accessibility-tree snapshots as primary perception model; vision opt-in via `--caps`.
- `mark3labs/mcp-go` — task-augmented async tool execution with concurrency limits and recovery middleware for handler panics.
- `cyanheads/git-mcp-server` — dual Node+Bun runtime auto-detection, multi-tenant base-directory sandbox, three auth modes.
- `apollographql/apollo-mcp-server` — Rust; tools generated declaratively from configured GraphQL operations.
- `chroma-core/chroma-mcp` — single binary supports four backing-store modes selected via flags.
- `idosal/git-mcp` — cloud-hosted SaaS at gitmcp.io with per-repo URL parameterization, zero-auth Cloudflare Workers.
- `sandraschi/email-mcp` — `Cargo.toml` alongside `pyproject.toml` for MCPB signing; 10+ backends behind a unified `send_email`.
- `getsentry/sentry-mcp` — `EMBEDDED_AGENT_PROVIDER` runs an LLM inside the MCP server.
- `Azure/azure-mcp` — archived (Aug 2025 README, Feb 2026 GitHub flag); successor lives at `microsoft/mcp` umbrella monorepo, inverting awslabs' per-package strategy.
- `conikeec/mcpr` — Rust MCP scaffolding library, archived Feb 2026.
- `elastic/mcp-server-elasticsearch` — Rust; deprecated by vendor in favor of Elastic Agent Builder 9.2.0+.

## Research gaps

What the corpus didn't surface, by axis:

- **Observability** is the largest genuine blind spot. Roughly three-quarters of samples produced no observability content. Some of that is genuinely-absent docs; some is research-budget-cap. Distinguishing the two requires a follow-up sweep that opens repo source for any sample where the section was templated rather than substantive.
- **Tests/CI specifics** — many samples confirm presence (a `tests/` directory, a CI badge) without naming framework, fixture style, coverage gates, or workflow content.
- **Last-commit dates** are missing or imprecise on a large fraction; landing-page captures are approximate. Verify against GitHub before citing.
- **Async/sync patterns** in tool signatures, schema strategies (Pydantic vs dataclasses vs raw dict), and exact entry-point paths frequently weren't extracted within budget.
- **Observability-vs-templated negation** — earlier sweeps over-counted "tracing" because some samples mention tracing only to negate it. Negation context matters.
- **Language coverage** — no C# (active), Java, Ruby, or PHP servers surfaced despite official SDKs. The two non-Python/TS/Go entries (Kotlin, C#) are an SDK and an archived vendor server respectively. Disclosed gap, not a population claim.
- **Templated-but-vacuous sections.** Several samples have sections that echo the template's prompt without substantive content (notably for thinly-documented small repos like `paypal/paypal-mcp-server`, `riza-io/riza-mcp`, `ppl-ai/modelcontextprotocol`, `pragmar/mcp-server-webcrawl` for some axes, `slackapi/slack-mcp-plugin` because the server source isn't there). Consumers should treat such "not surfaced" lines as research silence, not evidence of absence.

## Provenance

Eight general-purpose subagents read 13 alphabetically-batched per-sample files each from `logs/research/mcp/repos-samples/`, ignoring `_TEMPLATE.md`, `_INDEX.md`, and the existing `_CONSOLIDATED.md` skeleton. Each returned a per-sample one-line distinctive observation, batch-level cross-cutting patterns with within-batch counts, outliers, and a notes-on-research-gaps section. This document is the synthesis across those eight reports, organized around design decisions; the peer document `_CONSOLIDATED_template-view.md` reorganizes the same evidence around template section axes with adoption tables. Where a count is given (e.g. "well over half", "roughly a third"), it is a population estimate from summing batch-level signals — exact tallies live in the per-sample files. Specific repo citations name verified samples; distinctive claims trace back to the sample file by basename.
