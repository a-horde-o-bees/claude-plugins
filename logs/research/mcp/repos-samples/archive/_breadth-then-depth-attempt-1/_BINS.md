# Synthesis Bins — mcp / repos-samples (breadth-then-depth)

Orchestrator working state for the breadth-then-depth consolidation methodology. Tracks per-pass bin assignments (samples per spawn), calibration data (trailing-N work-tok/byte ratio), and convergence detection. **Not committed** — transient working file, deleted after the methodology runs to completion alongside the legacy reference files.

The compliance/diff verb skips `_*-prefixed` files (except `_CONSOLIDATED*.md`), so this file is invisible to corpus audits.

## Calibration

- Bin 1 ratio: 2.19 work-tok/byte (91,172 / 41,673)
- Bin 2 ratio: 2.20 work-tok/byte (93,231 / 42,357)
- Trailing-N=2 average: **2.20 work-tok/byte** — stable; safe to commit to ~42KB sample content per bin going forward
- Agent total context budget: ~250K tokens (per per-section-bins observation)
- Fixed overhead (instructions + methodology + consolidated reads + diff): ~30K
- Available for sample reads + tree growth + sample rewrites: ~220K
- Target utilization (per context-aware-iteration guidelines): 90% of available
- Per-spawn user-stated goal: **~100K work-token budget** (smaller than per-section-bins's ~200K to preserve quality)
- Initial byte capacity at seed ratio at 100K budget: 0.9 × 100K / 2.5 = **~36KB**
- Bin target: **~40KB** of sample content (8 samples at mean 5KB)

After each spawn, append the actual ratio (work_tokens / sum_sample_bytes) and recompute the trailing-N=3 average. Refine subsequent bin sizing.

## Pass structure

- **Pass 1 Phase 1a — Parallel partials** (completed): each agent worked in isolation on its bin, wrote to `_CONSOLIDATED_pass1-bin{N}.md`; did NOT read other partials or the unified consolidated. Mitigates first-bin precedent. 13 partials, 6,966 lines, 381KB total
- **Pass 1 Phase 1b — Staged merge** (in progress): multi-stage with context-aware-iteration sizing
    - Initial 2-half attempt stalled at write step (output too large for single Write call); merger instructions updated to require chunked-write (Edit-append per section)
    - Re-bin-packed at ~50-80KB per merger to match Pass 1 per-spawn footprint
    - Stage 1: 6 parallel mergers — `M1: bins 1, 2, 7` / `M2: bins 3, 4, 12` / `M3: bins 5, 11, 13` / `M4: bins 6, 10` / `M5: bin 8 alone` / `M6: bin 9 alone` → 6 intermediates
    - Stage 2: final merger combines 6 intermediates → `_CONSOLIDATED_breadth-then-depth.md`
- **Pass 2+ — Normalize** (pending): pass-over-pass tree convergence; rewrites samples to match unified consolidated; deepens consolidated where samples surface new branches
- **Final — Quantify** (pending): adoption tables under every branching subheading

## Note on Bin 1

Bin 1 dispatched before the parallel-then-merge restructure; its output (now `_CONSOLIDATED_pass1-bin1.md`) is structurally equivalent to a parallel-mode partial because the consolidated stub it read was essentially empty. Carrying forward as bin-1's contribution.

## Pass 1 — Gather bins

### Bin 1 — completed

- **Samples** (8, 40.7KB total): `AlwaysSany--deepl-fastmcp-python-server`, `Azure--azure-mcp`, `ClickHouse--mcp-clickhouse`, `DaInfernalCoder--perplexity-mcp`, `DiversioTeam--clickup-mcp`, `FuzzingLabs--mcp-security-hub`, `GLips--Figma-Context-MCP`, `HenkDz--postgresql-mcp-server`
- **Spawn:** `ad8098b27ccc5ab44`
- **Work tokens:** 91,172
- **Ratio:** 2.19 work-tok/byte
- **Outcome:** Consolidated grew from 7 to ~376 lines. 19 top-level `##` sections established: Identification, Language and runtime, Transport, Distribution, Entry point / launch, Configuration surface, Authentication, Multi-tenancy, Capabilities exposed, Extensibility, Observability, Host integrations, Tests, CI, Container / packaging artifacts, Repo layout, Python packaging specifics, TypeScript packaging specifics, Dual-mode binaries — server + management CLI, plus a Notable structural choices catch-all. Tree shape: divergence-axis (e.g., Language and runtime > Python > FastMCP / Raw mcp / Hand-rolled). No sample rewrites applied (all deferred to Pass 2 — too early). Categorization decisions worth flagging: dual-mode binaries promoted to top-level (may demote if rare elsewhere); language-grouped packaging-specifics subtrees may collapse into language-agnostic axes during normalization

### Bin 2 — completed

- **Samples** (8, 42.4KB): `JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`
- **Spawn:** `ae6831b4b5859c455`
- **Work tokens:** 93,231
- **Ratio:** 2.20 work-tok/byte
- **Outcome:** Wrote to `_CONSOLIDATED_pass1-bin2.md`. Tree shape diverged from Bin 1: split `Framework / SDK` from `Language and runtime`; promoted `Authorship` (vendor vs community license correlation) and `Capability source` (hand-coded vs CLI-wrap vs spec-generated vs operation-driven) as top-level axes. Notable observation: 5/8 vendor-authored samples are Apache-2.0; 3/3 community samples are MIT. Cross-cutting "safety posture" (write-flag gating / sandbox-default / feature-flag) surfaced as a candidate branch axis. Bin 2's `apollographql/apollo-mcp-server` is the corpus's only Rust server in this bin — flagged for merger to decide if Language-as-top-level taxonomy emerges
- **For merger to arbitrate:** Bin 2 split SDK choice from Language as separate axes; Bin 1 nested SDK under Language. Bin 2 created `Notable structural / cross-cutting patterns` top-level section (some redundancy with finer axes acknowledged in agent's report). Bin 2 split `Distribution channels` from `Container registry` (Docker Hub vs ghcr.io vs ECR may be too fine for merged tree)

### Bins 3-13 — completed (parallel-mode)

All 11 dispatched in parallel via `run_in_background`. Each agent isolated; no shared state. **All complete.** Combined Pass 1 Phase 1a totals: **1,181,608 work tokens / 563,835 sample bytes / ratio 2.10 average across 13 bins.**

| Bin | Samples | Bytes |
|-----|---------|-------|
| 3 | `awslabs--bedrock-kb-retrieval-mcp-server`, `awslabs--mcp-lambda-handler`, `awslabs--mcp`, `awslabs--openapi-mcp-server`, `baryhuang--mcp-server-aws-resources-python`, `bhauman--clojure-mcp`, `blazickjp--arxiv-mcp-server`, `chroma-core--chroma-mcp` | 47.7KB |
| 4 | `ckreiling--mcp-server-docker`, `cloudflare--mcp-server-cloudflare`, `conikeec--mcpr`, `crystaldba--postgres-mcp`, `cyanheads--git-mcp-server`, `cyanheads--perplexity-mcp-server`, `datalayer--earthdata-mcp-server`, `datalayer--jupyter-mcp-server` | 39.7KB |
| 5 | `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server` | 40.3KB |
| 6 | `geropl--linear-mcp-go`, `getsentry--sentry-mcp`, `github--github-mcp-server`, `googleapis--mcp-toolbox`, `hannesrudolph--sqlite-explorer-fastmcp-mcp-server`, `hugoduncan--mcp-clj`, `idosal--git-mcp`, `isaaccorley--planetary-computer-mcp` | 41.8KB |
| 7 | `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `jparkerweb--mcp-sqlite`, `korotovsky--slack-mcp-server`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp` | 40.3KB |
| 8 | `makenotion--notion-mcp-server`, `mark3labs--mcp-go`, `marlonluo2018--pandas-mcp-server`, `metoro-io--mcp-golang`, `microsoft--playwright-mcp`, `misbahsy--video-audio-mcp`, `modelcontextprotocol--kotlin-sdk`, `modelcontextprotocol--servers` | 45.7KB |
| 9 | `mongodb-js--mongodb-mcp-server`, `motherduckdb--mcp-server-motherduck`, `mukul975--cve-mcp-server`, `neondatabase--mcp-server-neon`, `normaltusker--kotlin-mcp-server`, `openags--paper-search-mcp`, `opensearch-project--opensearch-mcp-server-py`, `pathintegral-institute--mcp.science` | 48.0KB |
| 10 | `paypal--paypal-mcp-server`, `ppl-ai--modelcontextprotocol`, `pragmar--mcp-server-webcrawl`, `qdrant--mcp-server-qdrant`, `redis--mcp-redis`, `reminia--zendesk-mcp-server`, `riza-io--riza-mcp`, `rohitg00--kubectl-mcp-server` | 42.2KB |
| 11 | `rust-mcp-stack--rust-mcp-filesystem`, `sajal2692--mcp-weaviate`, `samuelgursky--davinci-resolve-mcp`, `sandraschi--email-mcp`, `severity1--terraform-cloud-mcp`, `shibuiwilliam--mcp-server-scikit-learn`, `shreyaskarnik--huggingface-mcp-server`, `slackapi--slack-mcp-plugin` | 41.9KB |
| 12 | `sooperset--mcp-atlassian`, `spences10--mcp-turso-cloud`, `stripe--agent-toolkit`, `supabase-community--supabase-mcp`, `teaguesterling--duckdb_mcp`, `the-momentum--fhir-mcp-server`, `thenets--ghost-mcp`, `tumf--grafana-loki-mcp` | 42.3KB |
| 13 | `twolven--mcp-server-puppeteer-py`, `upstash--context7`, `utensils--mcp-nixos`, `v-3--discordmcp`, `viant--mcp`, `voska--hass-mcp`, `zilliztech--mcp-server-milvus`, `zongmin-yu--semantic-scholar-fastmcp-mcp-server` | 39.4KB |
