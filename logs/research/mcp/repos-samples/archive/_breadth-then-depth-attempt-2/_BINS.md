# Synthesis Bins — mcp / repos-samples (breadth-then-depth, attempt 2)

Orchestrator working state for the breadth-then-depth methodology, attempt 2 with corrected qualitative approach (functional decomposition, no inline citations, descriptions refine across samples). **Not committed** — transient working file, deleted after the methodology runs to completion.

The previous attempt's outputs are at `archive/_breadth-then-depth-attempt-1/` for comparison.

## Calibration

- Calibration carries over from attempt 1: ratio ~2.10 work-tok/byte (averaged across 13 bins)
- Per-spawn target: ~100K work tokens at ~42KB sample content
- Output expected substantially smaller than attempt-1 partials (no inline citations)

## Pass structure

- **Pass 1 Phase 1a — Parallel partials** (in progress): 13 isolated agents identify functional roles + implementation paths in their bins; write to `_CONSOLIDATED_pass1-bin{N}.md`. No inline citations
- **Pass 1 Phase 1b — Merge** (pending): merger combines partials, dedupes by function+choice (not wording), strips any legacy citations, produces canonical unified consolidated
- **Pass 2+ — Normalize** (pending): mutually convergent rewriting of samples and consolidated until tree converges
- **Final — Quantify** (pending): adoption tables under each branching subheading via `references`

## Pass 1 bin assignments (same partition as attempt 1)

| Bin | Samples | Bytes |
|-----|---------|-------|
| 1 | AlwaysSany, Azure, ClickHouse, DaInfernalCoder, DiversioTeam, FuzzingLabs, GLips, HenkDz | 41.7KB |
| 2 | JackKuo666, PagerDuty, ahmedmustahid, alexei-led, alpacahq, apollographql, awslabs-aws-api, awslabs-aws-documentation | 42.4KB |
| 3 | awslabs-bedrock, awslabs-mcp-lambda, awslabs-mcp, awslabs-openapi, baryhuang, bhauman, blazickjp, chroma-core | 47.7KB |
| 4 | ckreiling, cloudflare, conikeec, crystaldba, cyanheads-git, cyanheads-perplexity, datalayer-earthdata, datalayer-jupyter | 39.7KB |
| 5 | designcomputer, docker, duolingo, echelon-ai-labs, elastic, exa-labs, executeautomation, feiskyer | 40.3KB |
| 6 | geropl, getsentry, github, googleapis, hannesrudolph, hugoduncan, idosal, isaaccorley | 41.8KB |
| 7 | jbeno, jlowin, jparkerweb, korotovsky, ktanaka101, labeveryday, lanbaoshen, mahdin75 | 40.3KB |
| 8 | makenotion, mark3labs, marlonluo2018, metoro-io, microsoft, misbahsy, modelcontextprotocol-kotlin, modelcontextprotocol-servers | 45.7KB |
| 9 | mongodb-js, motherduckdb, mukul975, neondatabase, normaltusker, openags, opensearch-project, pathintegral-institute | 48.0KB |
| 10 | paypal, ppl-ai, pragmar, qdrant, redis, reminia, riza-io, rohitg00 | 42.2KB |
| 11 | rust-mcp-stack, sajal2692, samuelgursky, sandraschi, severity1, shibuiwilliam, shreyaskarnik, slackapi | 41.9KB |
| 12 | sooperset, spences10, stripe, supabase-community, teaguesterling, the-momentum, thenets, tumf | 42.3KB |
| 13 | twolven, upstash, utensils, v-3, viant, voska, zilliztech, zongmin-yu | 39.4KB |
