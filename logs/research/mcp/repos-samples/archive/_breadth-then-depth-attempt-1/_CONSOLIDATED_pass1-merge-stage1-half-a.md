# Sample

Pass 1 Phase 1b merge of 7 partials (bins 1-7) into Half-A intermediate. See `_BINS.md` for input partials list.

## Identification

Per-repo metadata that situates each sample in the corpus — origin, popularity, license posture, lifecycle status, authorship.

### License

Licenses observed across the bins.

- MIT — most common across the corpus [`AlwaysSany--deepl-fastmcp-python-server`, `DiversioTeam--clickup-mcp`, `GLips--Figma-Context-MCP`, `DaInfernalCoder--perplexity-mcp`, `FuzzingLabs--mcp-security-hub`, `JackKuo666--PubMed-MCP-Server`, `ahmedmustahid--postgres-mcp-server`, `alexei-led--k8s-mcp-server`, `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `conikeec--mcpr`, `crystaldba--postgres-mcp`, `designcomputer--mysql_mcp_server`, `echelon-ai-labs--servicenow-mcp`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`, `jparkerweb--mcp-sqlite`, `korotovsky--slack-mcp-server`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `lanbaoshen--mcp-jenkins`, `mahdin75--gis-mcp`]
- Apache-2.0 — common, especially among vendor repos [`ClickHouse--mcp-clickhouse`, `PagerDuty--pagerduty-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `cloudflare--mcp-server-cloudflare`, `cyanheads--git-mcp-server`, `cyanheads--perplexity-mcp-server`, `docker--hub-mcp`, `duolingo--slack-mcp`, `elastic--mcp-server-elasticsearch`, `feiskyer--mcp-kubernetes-server`, `jlowin--fastmcp`]
- AGPLv3 — uncommon among MCP servers; copyleft implications for hosts embedding the server [`HenkDz--postgresql-mcp-server`]
- BSD-3-Clause [`datalayer--earthdata-mcp-server`, `datalayer--jupyter-mcp-server`]
- GPL-3.0 — called out as unusual: "ecosystem skews MIT/Apache" [`ckreiling--mcp-server-docker`]
- CC BY-NC-SA 4.0 — Creative Commons NonCommercial; rare and restricts commercial adoption [`jbeno--cursor-notebook-mcp`]

### Default branch

- `main` — dominant across both vendor and community repos [`JackKuo666--PubMed-MCP-Server`, `PagerDuty--pagerduty-mcp-server`, `ahmedmustahid--postgres-mcp-server`, `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `designcomputer--mysql_mcp_server`, `docker--hub-mcp`, `echelon-ai-labs--servicenow-mcp`, `elastic--mcp-server-elasticsearch`, `exa-labs--exa-mcp-server`, `executeautomation--mcp-playwright`, `feiskyer--mcp-kubernetes-server`, `jbeno--cursor-notebook-mcp`, `jlowin--fastmcp`, `jparkerweb--mcp-sqlite`, `ktanaka101--mcp-server-duckdb`, `labeveryday--mcp_pdf_reader`, `mahdin75--gis-mcp`]
- `master` — still in active use [`alexei-led--k8s-mcp-server`, `duolingo--slack-mcp`, `korotovsky--slack-mcp-server`, `lanbaoshen--mcp-jenkins`]

### Authorship

- Vendor-authored (official organization repo) — credibility dimension explicitly surfaced; the vendor's own MCP server carries credibility derivative servers don't [`PagerDuty--pagerduty-mcp-server`, `alpacahq--alpaca-mcp-server`, `apollographql--apollo-mcp-server`, `awslabs--aws-api-mcp-server`, `awslabs--aws-documentation-mcp-server`, `Azure--azure-mcp`, `ClickHouse--mcp-clickhouse`, `cloudflare--mcp-server-cloudflare`, `docker--hub-mcp`, `elastic--mcp-server-elasticsearch`, `exa-labs--exa-mcp-server`, `getsentry--sentry-mcp`, `github--github-mcp-server`, `googleapis--mcp-toolbox`]
- Community / individual maintainer [`JackKuo666--PubMed-MCP-Server`, `ahmedmustahid--postgres-mcp-server`, `alexei-led--k8s-mcp-server`, and many others]

### Repo lifecycle status

Active vs archived/redirected. The corpus contains both living projects and frozen-with-redirect repos that point at successor monorepos.

- Active main-branch development is the norm
- Two-stage archival pattern — code freeze months before formal GitHub archival; README body declares an earlier archival date than the org-level archived flag, signaling a "read-only maintenance" interval while a redirect target stabilizes [`Azure--azure-mcp`]
- Successor-redirect via umbrella monorepo — an org collapses per-domain MCP repos into a single company-wide MCP monorepo with shared core libraries, inverse of the per-service published-package strategy [`Azure--azure-mcp`]
- Archived repository — `conikeec--mcpr` archived as of February 8, 2026; v0.2.0 yanked due to SSE issues, v0.2.3+ recommended; ecosystem captures pre-archive Rust libs that may already be superseded [`conikeec--mcpr`]
- Lifecycle declaration in README — explicit deprecation notice; "the project is superseded by Elastic Agent Builder in ES 9.2.0+"; a deprecation-status axis most repos don't surface [`elastic--mcp-server-elasticsearch`]
- Deprecation as a versioning signal — SSE removal dated and documented in-repo (2025-05-26) rather than only in a changelog [`awslabs--mcp`]

### Star-count vs engineering-quality skew

Star count is not a proxy for engineering quality. A 3-star repo can carry 62 pytest tests and full ruff/mypy/CLI ergonomics [`DiversioTeam--clickup-mcp`], while large-community repos may leave testing/CI specifics unsurfaced. Read engineering rigor from the artifacts (test count, lint config, CI presence), not from popularity.

Star spread observed: 7-star [`duolingo--slack-mcp`] up to 5.5k [`executeautomation--mcp-playwright`], with most samples in the 100s–1000s range.
