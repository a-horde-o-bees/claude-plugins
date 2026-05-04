# Depth Pass Refinements — Sample > Release and lifecycle

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

Inspected 16 paths (12 with supporting samples, 4 with zero). Pulled content for 200 sample sections — heaviest reads under `License — Permissive (MIT / Apache-2.0)` (83 samples), `Active development` (66), and `Tagged release with version in changelog` (30); single-digit reads on the remaining 9 active paths. Zero-supporting paths skipped: `GitHub Actions release workflow`, `Manual via package manager`, `PyPI + lockfile-tracked` (and the role-level note that these channels surface elsewhere).

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

`Sample > Release and lifecycle > License — Permissive (MIT / Apache-2.0)` — The path bundles MIT and Apache-2.0 as if interchangeable. Cross-corpus evidence shows a meaningful split: vendor-authored repos (PagerDuty, AWS Labs, Cloudflare, Microsoft, MongoDB, Qdrant, Zilliz, Apollo, GitHub, Google, Stripe, Notion, Elastic, Supabase, PayPal) heavily favor Apache-2.0; community/individual repos heavily favor MIT. Sample notes call this out explicitly ("Apache-2.0; vendor-authored", "MIT — vendor-authored (Upstash) project optimized for adoption", "first-party PayPal ownership"). EPL-2.0 also currently shelters here (hugoduncan--mcp-clj.md) which is a mis-placement (see Mis-placed samples). Suggested sharpening:

```
The dominant pattern — MIT for community/individual repos, Apache-2.0 for vendor-authored repos (where the patent grant matters more for corporate adoption). Both maximize downstream reuse with no copyleft obligations. EPL-2.0 and other permissive variants do not belong here — they have distinct legal text and trigger different obligations.
```

`Sample > Release and lifecycle > Active development` — Description currently reads "Recent commits, ongoing CI runs, semver-tagged releases. Default for all in-bin samples except outliers." Cross-corpus evidence shows two distinct sub-patterns clustering inside this one path: (a) *date-anchored* signal — last commit date, recent release date (idosal--git-mcp.md "Last commit March 13, 2026"; ktanaka101--mcp-server-duckdb.md "Last commit May 5, 2025"); (b) *cadence-anchored* signal — release count or commit count without a specific date (apollographql "v1.12.0 released 2026-04-02 with 63 total releases"; pathintegral-institute "133 total commits"; tumf--grafana-loki-mcp.md "Active project (103 commits); specific last-commit date not surfaced"). The path is also the catch-all for "low-activity but not abandoned" repos (misbahsy--video-audio-mcp.md "Small repo, ~6 commits"; thenets--ghost-mcp.md "Recent thoughtfully-built repo despite very low star count (1)"). Suggested sharpening:

```
Lifecycle stage — repository receives ongoing maintenance, with at least one of: recent commit date, recent release tag, or sustained commit count. Default for in-bin samples that aren't archived or deprecated. Distinct from Tagged release with version in changelog, which describes how releases are cut rather than whether the project is alive.
```

`Sample > Release and lifecycle > Tagged release with version in changelog` — Description says "Standard semver tag... with a changelog entry. The default expectation." Cross-corpus evidence shows the path is actually heterogeneous on whether a CHANGELOG is present. Several samples explicitly note CHANGELOG (`bhauman--clojure-mcp.md` — "v0.3.1 release dated 2026-03-14; CHANGELOG present"; `hugoduncan--mcp-clj.md` — "cliff.toml for release-notes generation"); most do not mention a changelog at all, just the tag (geropl, mark3labs, microsoft, kotlin-sdk, samuelgursky, supabase-community). The "in changelog" portion of the path name overstates what most samples actually exhibit. Two options: (a) drop "in changelog" from the path name and treat changelog as a within-path observation, or (b) split out a sub-path. Recommendation: drop from the name. Suggested sharpening:

```
Standard semver tag (e.g., `v0.3.1`, `v0.2.6`, `v1.10.0`) on the release commit. A subset additionally maintain a CHANGELOG file or auto-generated release notes (e.g., cliff.toml). Describes the release-cutting process; orthogonal to lifecycle stage (a tagged release pattern can persist in archived repos).
```

`Sample > Release and lifecycle > Archived` — Description correctly captures "marked archived; code still functions; no further fixes." Cross-corpus inspection adds two distinct archival sub-patterns worth folding in: (a) *single-stage archival* — repo flag flipped (`conikeec--mcpr.md`, archived Feb 2026; status frozen with WebSocket transport unimplemented and v0.2.0 SSE transport yanked); (b) *two-stage archival* — README declares archival before the GitHub flag (Azure--azure-mcp.md, README archival ~Aug 2025 ahead of formal flag Feb 2026); (c) *physical excision* — `modelcontextprotocol--servers.md` doesn't archive in place but maintains a sibling `servers-archived` repo. Suggested sharpening:

```
Repository's maintenance has ended. Three observed patterns: (a) single-stage flag flip — GitHub-archived with no in-repo signal beforehand; (b) two-stage archival — README declares read-only maintenance months before the org-level flag fires; (c) physical excision — archived content moved to a sibling repo so the active repo stays sharp (modelcontextprotocol/servers → servers-archived). Code still functions; flag adoption risk for consumers.
```

`Sample > Release and lifecycle > Dated deprecation in repo` — Description currently focuses on transport removal as the typical case. Cross-corpus evidence shows two distinct deprecation kinds: (a) *feature deprecation* (`awslabs--mcp.md` — SSE removal 2025-05-26 with bridge to Streamable HTTP); (b) *whole-project deprecation* (`elastic--mcp-server-elasticsearch.md` — README declares EOL, superseded by Elastic Agent Builder in ES 9.2.0+, security updates only). The "transport or capability changes" framing in the existing description fits (a) but mis-fits (b), where the entire project is sunsetted. Suggested sharpening:

```
Removal or end-of-life signaled in-repo with explicit dates rather than buried in changelogs. Two observed kinds: (a) feature deprecation — a transport, capability, or API removed on a stated date with a documented migration path (e.g., SSE removed 2025-05-26 → Streamable HTTP); (b) whole-project deprecation — README declares EOL with security-updates-only posture, often pointing to a successor product. Distinct from Archived (a finer-grained mid-life signal that consumers can act on while the repo is still alive).
```

`Sample > Release and lifecycle > License — Permissive (BSD-3-Clause)` — Both supporting samples (`datalayer--earthdata-mcp-server.md`, `datalayer--jupyter-mcp-server.md`) carry verbatim-identical descriptions. Both come from the same org (datalayer), so the BSD-3 adoption is org-wide rather than two independent choices. The current path description is solid; suggest adding the org-uniformity observation:

```
Permissive license closely related to MIT/Apache but with explicit attribution and non-endorsement clauses. Functionally similar (commercial-friendly, no copyleft) but distinguished by the legal text — particularly the requirement that the project's name and contributors not be used to endorse derivative products without permission. Appropriate when the author wants the permissive posture but cares about the attribution/endorsement language specifically. In the corpus both supporting samples are datalayer-org repos, suggesting BSD-3 is an org-level posture rather than a per-project choice.
```

`Sample > Release and lifecycle > License — Copyleft (GPL-3.0)` — Single-supporting (`ckreiling--mcp-server-docker.md`). Description is accurate. No sharpening proposed; flagging only that single-sample paths warrant the existing adoption-risk caveat (n=1).

`Sample > Release and lifecycle > License — Copyleft (AGPL-3.0)` — Description correctly distinguishes from GPL-3 and CC BY-NC-SA. Cross-corpus evidence shows both samples (`HenkDz--postgresql-mcp-server.md`, `normaltusker--kotlin-mcp-server.md`) explicitly call out the network-use trigger; the description's framing matches. No sharpening required.

`Sample > Release and lifecycle > License — Copyleft / non-commercial (CC BY-NC-SA)` — The path name bundles two functionally distinct license families: (a) *non-commercial* CC BY-NC-SA 4.0 (`jbeno--cursor-notebook-mcp.md`); (b) *Eclipse Public License 2.0* (`bhauman--clojure-mcp.md` — currently mis-placed here). EPL-2.0 *is* copyleft but commercial use is permitted; it has nothing to do with non-commercial licensing. The bhauman sample's own description openly contradicts the path name ("EPL-2.0 ... copyleft license, requires share-alike"). See Mis-placed samples for the move; description after the move should specialize to:

```
Non-commercial copyleft license (CC BY-NC-SA 4.0). Limits downstream commercial adoption — distinct from GPL/AGPL (commercial use permitted under copyleft) and from EPL-2.0 (commercial use permitted; weaker share-alike scope). Rare in the MCP ecosystem; signals authorial intent over reusability.
```

`Sample > Release and lifecycle > Vendor-internal release (no public pipeline)` — Description says "the public repo has no release pipeline at all" which is accurate for `slackapi--slack-mcp-plugin.md` but partially mis-fits `upstash--context7.md`, where the public repo *does* have an npm CLI release pipeline; only the MCP server's deploy pipeline is vendor-internal. Two sub-patterns: (a) *fully vendor-internal* — the entire artifact is hosted, public repo holds only configs/metadata; (b) *split pipeline* — public repo ships a client/CLI artifact via standard channels, but the actual server runtime deploys through invisible vendor infrastructure. Suggested sharpening:

```
The actual MCP server runtime ships through the vendor's invisible deploy pipeline rather than a public release process. Two observed shapes: (a) fully vendor-internal — the public repo holds only configs/OAuth metadata and has no release pipeline (`slackapi--slack-mcp-plugin.md`); (b) split pipeline — the public repo ships a client/CLI helper via npm or similar while the server deploys behind closed doors (`upstash--context7.md`). Appropriate for hosted remote MCP services where the runtime never executes on a consumer's machine.
```

`Sample > Release and lifecycle > Dual-license relicensing gate` — Description is accurate. Both supporting samples are modelcontextprotocol-org repos (`modelcontextprotocol--kotlin-sdk.md`, `modelcontextprotocol--servers.md`) — same forward-migration mechanism applied across the org's reference projects. Suggest adding the org-uniformity observation:

```
Existing code stays under the original license (MIT); new contributions land under a different license (Apache-2.0). The release process enforces the contributor agreement. Appropriate as a forward migration mechanism without rewriting prior commits. Both observed samples are modelcontextprotocol-org reference projects — suggests an org-level relicensing strategy rolling across the canonical MCP repos.
```

`Sample > Release and lifecycle > MCPB bundle signing` — Single-supporting (`sandraschi--email-mcp.md`); description accurate. Note that the consolidated also surfaces this as a Cross-role tool entry; the n=1 here suggests MCPB signing in MCP-server repos is genuinely rare today (most MCPB consumers are downstream of these repos, not in them).

`Sample > Release and lifecycle > Automated-release sentinel version` — Single-supporting (`awslabs--openapi-mcp-server.md`). Description accurately captures the pattern. The int64-max sentinel value is a strong signal — flag for the reconciler that this might be a wider awslabs-monorepo pattern worth re-checking other awslabs samples against.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

`Sample > Release and lifecycle > License — Permissive (MIT / Apache-2.0)` — Vendor-vs-community license split. Apache-2.0 dominates vendor-authored repos (~30+ samples explicitly note vendor authorship: AWS Labs, Cloudflare, Microsoft, MongoDB, Qdrant, Apollo, GitHub, Google, Stripe, Notion, Elastic, Supabase, PayPal, IBM-style orgs); MIT dominates community/individual repos (~50+ samples). Patent-grant of Apache-2.0 is the typical motivator for corporate-authored projects. Recommend folding into description rather than splitting the path — the underlying mechanism (permissive, commercial-friendly, no copyleft) is the same; the choice signal is upstream of the path.

`Sample > Release and lifecycle > Active development` — Date-anchored vs cadence-anchored evidence (described above). Recommend folding into description; both shapes indicate the same lifecycle stage, the difference is whether the surveyor captured a date or a count.

`Sample > Release and lifecycle > Tagged release with version in changelog` — Pre-1.0 vs post-1.0 release versions. Roughly 22 of 30 samples are still pre-1.0 (`v0.x.y`); only 8 have crossed v1.0 (`github`, `googleapis`, `mongodb-js`, `motherduckdb`, `datalayer--jupyter`, `geropl--linear-mcp-go`, `teaguesterling--duckdb_mcp` v2.x, `modelcontextprotocol--servers` calendar-versioned 2026.1.26). Not actionable as a split — the 1.0 vs pre-1.0 line correlates with vendor-authoredness more than release-process style. Surface as a corpus observation: the MCP ecosystem is mostly pre-1.0 by version number.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None proposed. The license paths each describe genuinely distinct legal regimes; lifecycle paths (Active/Archived/Dated deprecation) describe distinct stages; release-process paths (Tagged release, Vendor-internal, MCPB bundle signing, Automated-release sentinel) describe distinct mechanisms. The closest merge candidate is `Active development` + `Tagged release with version in changelog`, but cross-corpus evidence shows they are orthogonal axes (lifecycle vs release-process) — many samples carry only one. Keep them split and sharpen the description boundary (see sharpenings above).

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

None proposed. The strongest candidate would be splitting `License — Permissive (MIT / Apache-2.0)` along the vendor/community axis, but: (a) the underlying license terms are not identical (Apache adds the patent grant), so labeling them MIT/Apache understates the difference but the path *is* recognizing them as one bucket; (b) splitting MIT and Apache produces two large paths whose distinction is cleanly captured by a within-path sub-axis observation. Recommend the description-sharpening route over a split.

The other strong candidate would be splitting `Tagged release with version in changelog` into "Tagged with CHANGELOG" vs "Tagged without CHANGELOG", but only ~5 samples (out of 30) explicitly mention a CHANGELOG; the other 25 are silent on CHANGELOG presence — silence may mean "no CHANGELOG" or "CHANGELOG present but not surfaced in the depth-pass capture." Insufficient evidence; recommend dropping "in changelog" from the path name instead (description sharpening above).

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

`hugoduncan--mcp-clj.md` currently under `Sample > Release and lifecycle > License — Permissive (MIT / Apache-2.0)` better fits a copyleft / share-alike path because the sample's own description reads "EPL-2.0 (Eclipse Public License 2.0)." EPL-2.0 is a *weak copyleft* license that requires source disclosure for modifications to EPL-licensed files — fundamentally different from MIT/Apache, which impose no copyleft obligation. The license entry was binned into MIT/Apache during Pass 1/2 likely because no EPL bin existed.

`bhauman--clojure-mcp.md` currently under `Sample > Release and lifecycle > License — Copyleft / non-commercial (CC BY-NC-SA)` better fits a copyleft / share-alike path because the sample's own description reads "EPL-2.0 (Eclipse Public License v 2.0) — copyleft license, requires share-alike for derivatives." EPL-2.0 *is* copyleft but it is *not* non-commercial — commercial use is fully permitted. Bundling EPL with CC BY-NC-SA conflates the share-alike obligation (shared) with the commercial restriction (only CC BY-NC-SA carries this).

**Recommended reconciler action.** The two EPL-2.0 samples currently land in two different paths despite carrying the identical license. Both Clojure-ecosystem MCP servers, both copyleft-but-commercial-friendly. Strongly suggest the reconciler add a new path:

```
### License — Weak copyleft (EPL-2.0)

Eclipse Public License 2.0 — weak copyleft. Source-disclosure obligation attaches to EPL-licensed files modified by a downstream consumer; surrounding files in a derivative work are not pulled under the EPL. Commercial use is permitted. Distinct from GPL/AGPL (stronger copyleft scope), CC BY-NC-SA (forbids commercial), and BSD-3/MIT/Apache (no copyleft). Both supporting samples are Clojure-ecosystem MCP servers; EPL is the canonical license for Clojure-world projects.
```

Then move both samples to it.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

**License monoculture skews vendor.** Of 96 samples in this role, 83 carry MIT or Apache-2.0 — 86% concentration. The remaining 13% spread across BSD-3 (2), AGPL (2), CC BY-NC-SA (1, after correcting bhauman), GPL (1), EPL (2, after correcting bhauman+hugoduncan), and unspecified. The MCP ecosystem is overwhelmingly permissive-licensed; copyleft choices are deliberate and rare.

**Vendor authorship correlates with Apache-2.0.** Across the 83 permissive samples, vendor-authored projects (including AWS Labs, Microsoft, Google, GitHub, MongoDB, Cloudflare, Supabase, PayPal, Apollo, Notion, Stripe, Qdrant, Elastic) overwhelmingly choose Apache-2.0; community/individual projects overwhelmingly choose MIT. The differentiator is the explicit patent grant — Apache-2.0 protects corporate adopters in a way MIT does not. This is a project-management signal, not a license-mechanism signal.

**Release-process maturity diverges from runtime maturity.** 30/96 samples have explicit tagged releases with versions; 66/96 are flagged Active development. The overlap is partial — many "active" repos have no formal versioning beyond a moving HEAD. The MCP ecosystem skews toward continuous-deployment from main rather than versioned releases, which has real implications for downstream consumers (no version pinning means exposure to upstream breakage).

**Deprecation signaling is informal.** Only 5 samples (3 archived + 2 dated deprecation) carry any structured lifecycle-end signal. The remaining 91 samples either are alive or are dead-but-undeclared — there is no observed convention for "stale but not abandoned" mid-states. This is an ecosystem-wide deficiency rather than a per-sample defect; future research could probe last-commit-date distributions to estimate the dark-matter fraction.

**MCP version lifecycle is pre-1.0.** ~22 of 30 samples that carry tagged versions are still on `v0.x.y`. The ecosystem is overwhelmingly pre-stable by SemVer convention. Calendar versioning (`modelcontextprotocol--servers.md` at 2026.1.26) appears once, suggesting it's not a widespread pattern.

**Transport-removal as deprecation lever.** Both `awslabs--mcp.md` (SSE removed) and the SSE transport bedrock more broadly point to a corpus pattern: as the MCP transport spec evolves, projects use dated transport removals as a signaling mechanism. This isn't captured in the role's path set as a distinct concept but might emerge as a research question for the next-pass analysis (and surfaces in *Transport* role too).

**Org-level license posture.** Three org-level patterns emerged: (a) datalayer-org → BSD-3 across both samples; (b) modelcontextprotocol-org → MIT-to-Apache relicensing gate across both samples; (c) awslabs-org → Apache-2.0 + automated-release sentinel version. License choice clusters by org, not by individual project — orgs make the call once and propagate.
