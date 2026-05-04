# Depth Pass Refinements — Sample > CI

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

`Sample > CI > GitHub Actions` — the current description reads as a feature list of activities ("unit tests, lint, type-check, release-binary cross-compilation, container image builds, PyPI/crates.io publishes, dependency audit") and a workflow inventory (`ci.yml`, `release.yml`, `release-binaries.yml`, `release-container.yml`, `pages.yml`, `golangci-lint.yml`). Cross-corpus evidence shows: of the 76 supporting samples, the overwhelming majority (~50) say only "`.github/workflows/` present" or "GitHub Actions configured" with "specifics not extracted within budget." The full activity list is reachable in only a handful of samples (awslabs--mcp, cyanheads--git-mcp-server, mark3labs--mcp-go, qdrant--mcp-server-qdrant, sandraschi--email-mcp, apollographql--apollo-mcp-server). The description currently reads as if every sample exhibited the full matrix; it should distinguish the "presence of `.github/workflows/`" baseline from the richer pipelines documented in a minority. Suggested sharpening:

> `.github/workflows/` directory with one or more workflow files — by far the dominant CI substrate across the corpus (76/90 = 84%). Most samples confirm only directory presence; a minority surface specific workflow content. Where surfaced, common job kinds include unit tests on push/PR, lint and format gates (ruff, biome, eslint, golangci-lint, clj-kondo), type-check (mypy, pyright, tsc), release-binary cross-compilation, container image build, package publish (PyPI / crates.io / npm), and dependency audit. Workflows are typically split by concern (`ci.yml`, `release.yml`, `release-binaries.yml`, `release-container.yml`, `pages.yml`, `golangci-lint.yml`). Often paired with codecov for coverage badges. Sub-flavors that earn their own paths under this role layer on top of this baseline: lint config separation, supply-chain scan, release-on-tag, multi-system, monorepo inheritance.

`Sample > CI > Pre-commit hooks` — description scopes the path as "Appropriate for monorepos where consistency across many sub-packages must be enforced." Evidence: 2 samples — awslabs--mcp (a monorepo) and tumf--grafana-loki-mcp (a single Python tool, not a monorepo). The monorepo framing is too narrow. Suggested sharpening:

> `.pre-commit-config.yaml` runs local checks (lint, format, secret scan) before commit. Mirrors CI's lint stage locally so developers catch issues without round-tripping through CI. Appears in monorepos enforcing consistency across sub-packages and in single-tool repos where the maintainer wants discipline-first hygiene. Git hooks via lefthook or similar are an alternative.

`Sample > CI > None / absent` — description names the categories ("early-stage repos, single-author tools, configs-only repos, and remote services") but the zilliztech--mcp-server-milvus entry actually says "Not observed in surfaced content (presence unverified)" — the path conflates "verified absence" with "could not verify." Suggested sharpening:

> No CI configured, or no CI surfaced in the extracted content. Common in early-stage repos, single-author tools, configs-only repos, and remote services where the vendor's hosting pipeline is invisible. Path also absorbs samples where extraction couldn't confirm presence — absence in this column is not always a positive claim.

`Sample > CI > Multi-system CI` — description says "vendors run GitHub Actions in addition to a vendor-internal CI (Buildkite)." Evidence: elastic--mcp-server-elasticsearch fits the description (Buildkite + GitHub Actions for multi-platform); googleapis--mcp-toolbox says "Both `.ci/` and `.github/workflows/` directories suggest multi-system CI orchestration" — this is weaker, "suggests" rather than confirms. Suggested sharpening:

> A second CI substrate alongside GitHub Actions — e.g., a vendor-internal Buildkite pipeline (elastic) for platform/architecture matrices the public surface doesn't cover, or a sibling `.ci/` directory holding additional configuration (googleapis). Appears when an org's internal CI handles concerns GitHub Actions can't easily address while a public surface stays available for outside contributors.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

`Sample > CI > GitHub Actions` — extraction-confidence sub-axis: roughly 50 samples report only directory presence ("`.github/workflows/` present; specifics not extracted within budget"); roughly 25 surface specific workflow names or job kinds. Fold into description (already proposed above) — not a structural split, since the underlying mechanism is identical and the variance reflects extraction depth, not implementation difference.

`Sample > CI > GitHub Actions` — workflow-split sub-axis: a meaningful minority of samples explicitly document multi-workflow splits (apollographql: CI + release-binaries + release-container; mark3labs: ci.yml + golangci-lint.yml + pages.yml + release.yml; idosal: e2e-tests.yml + run-tests.yml; alexei-led: release.yml + ci.yml). Single-workflow setups are equally documented (blazickjp: tests.yml; designcomputer: test.yml; jlowin: run-tests.yml; sooperset: tests.yml). Three or four samples each. Fold into description as an observed variance — not a split, since the mechanism is identical and sample counts are small.

`Sample > CI > GitHub Actions` — quality-pipeline sub-axis: lint+format+typecheck+test bundled into one CI matrix appears across cyanheads--git-mcp-server (npm run devcheck), datalayer--earthdata-mcp-server, qdrant--mcp-server-qdrant, sandraschi--email-mcp, normaltusker--kotlin-mcp-server, upstash--context7. ~6 samples. Fold into description as a recognized quality-pipeline pattern.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None proposed. Each non-baseline path describes a distinct mechanism layered onto GitHub Actions (lint config, supply-chain scan, codecov, secret-scan, scorecard, renovate, monorepo inheritance, turbo, multi-system, release-cut, vercel-preview, coderabbit). Mergers would lose the layered-mechanism distinction.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

`Sample > CI > Build + test + supply-chain scan` — the three samples reach this bucket through three distinct mechanisms:

- FuzzingLabs--mcp-security-hub: container image scanning (Trivy) — true SCA / supply-chain
- cyanheads--git-mcp-server: npm dependency audit alongside lint/format/typecheck — closer to baseline GitHub Actions quality pipeline plus dep audit
- sandraschi--email-mcp: Bandit (Python SAST) + MyPy + Ruff + Biome — SAST, not SCA

Bandit and dependency audit are not "supply-chain scan" in the strict sense (Trivy / OSV-scanner / npm audit vs source-code static analysis). The current path bundles three mechanisms under a label that fits one. Two options for the reconciler:

A. Tighten the path to "Container or dependency supply-chain scan" — keep FuzzingLabs and cyanheads, move sandraschi to a sibling "Static-analysis security scan (SAST)" path, or fold sandraschi into the GitHub Actions quality-pipeline sub-axis.

B. Broaden the path to "Security scan as build gate" — keep all three, with the description acknowledging the SCA / SAST distinction.

Recommendation: A — sandraschi and cyanheads's dep-audit step are arguably parts of the GitHub Actions quality pipeline that this depth pass would fold into the GitHub Actions description, leaving only FuzzingLabs as a clear supply-chain-scan-as-build-gate. With n=1, the bucket itself becomes a candidate for retirement and absorption back into a "GitHub Actions" sub-axis, but the reconciler should weigh whether any single-sample paths in this role survive.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

`cyanheads--perplexity-mcp-server.md` currently under `Sample > CI > Documented but not necessarily wired` better fits `Sample > CI > GitHub Actions` (with "specifics not extracted" qualifier) because the entry says "`.github/` present but CI workflows not explicitly documented in README" — this is the OPPOSITE of the path's stated meaning. The path's description says "README shows GitHub Actions YAML example… but the actual `.github/workflows/*.yml` may or may not exist." cyanheads--perplexity has the workflows but no README documentation; misbahsy--video-audio-mcp has README documentation but unconfirmed workflows. The two samples cluster on opposite sides of the same axis. Two corrective options:

A. Move cyanheads--perplexity-mcp-server to `GitHub Actions` and leave the path as misbahsy-only (n=1).
B. Broaden the path's description to "documentation and implementation diverge in either direction."

Recommendation: A — the path was clearly authored for the misbahsy pattern (README copy-paste seed); cyanheads--perplexity is just an extraction-budget artifact that fits GitHub Actions baseline.

`cyanheads--git-mcp-server.md` currently under `Sample > CI > Build + test + supply-chain scan` arguably better fits the GitHub Actions quality-pipeline sub-axis (or a future "GitHub Actions with lint+test+typecheck quality matrix" path). The "supply-chain scan" framing leans too heavily on the dependency-audit step. See bucket-split discussion above.

`sandraschi--email-mcp.md` currently under `Sample > CI > Build + test + supply-chain scan` arguably better fits the GitHub Actions quality-pipeline sub-axis. Bandit is SAST, not SCA. See bucket-split discussion above.

`zilliztech--mcp-server-milvus.md` currently under `Sample > CI > None / absent` is borderline — the entry says "Not observed in surfaced content (presence unverified)." Either fold the uncertainty into the path's description (as recommended above), or leave the sample where it is with the description acknowledging the conflation.

`googleapis--mcp-toolbox.md` currently under `Sample > CI > Multi-system CI` is borderline — entry says "Both `.ci/` and `.github/workflows/` directories suggest multi-system CI orchestration." "Suggest" is weak. The googleapis GitHub Actions entry already says "`.ci/` directory holds additional CI configuration" — the `.ci/` directory may just be GitHub Actions support content (custom actions / shared scripts), not a second CI system. Reconciler should decide whether to demote this sample into GitHub Actions only.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

The CI role's Pareto distribution is sharp: GitHub Actions is 84% of all samples; everything else combined is 16%. The next-largest paths are "Monorepo CI inheritance" (5, all in awslabs/) and "None / absent" (5). Most non-baseline paths are 1–4 samples each. The role's branching structure encodes "GitHub Actions plus a layered mechanism" — every non-baseline path layers something on top of the baseline (lint config, codecov, scorecard, secret-scan baseline, renovate, supply-chain scan, release-cut, multi-system, turbo, coderabbit, vercel preview). The role would benefit from an explicit role-level note: "Most non-baseline paths describe a mechanism layered onto GitHub Actions, not an alternative to it."

Extraction-budget noise dominates the role's evidence. ~50 of 76 GitHub Actions samples report only directory presence. This is not implementation variance — it's research-time variance. Future research waves could profitably target a sub-population of GitHub Actions samples for deeper extraction (job lists, trigger conditions, matrix dimensions) to populate the sub-axes that are currently under-populated.

The "Monorepo CI inheritance" bucket is entirely awslabs/ (5/5 samples). It captures a real pattern (sub-server doesn't ship its own workflow; root monorepo's CI applies) but as a corpus observation, the path is essentially "this is what awslabs does." If the corpus included more monorepos (cloudflare, modelcontextprotocol--servers, getsentry, googleapis), the inheritance pattern would either grow or stay awslabs-only. Worth flagging that sample selection drives the bucket.

The "None / absent" bucket includes early-stage tools (twolven, marlonluo2018), some configs-only / wrapper repos (v-3--discordmcp), and one extraction-uncertainty sample (zilliztech). The category is doing real work — it isolates samples whose absence of CI signals project maturity — but the description should acknowledge that "absence" here may mean "not yet checked," "not yet present," or "deliberately omitted" (configs-only).

The release-pipeline mechanisms are scattered: `Release-cut workflow on tag push` (3 samples) explicitly captures tag-driven release jobs, but multiple GitHub Actions entries also mention `release.yml` (alexei-led, mark3labs, apollographql) and the pattern is described inside the GitHub Actions baseline. The boundary between "GitHub Actions ships a release.yml" and "this sample exhibits Release-cut workflow on tag push" is fuzzy in practice — reconciler should consider whether these should consistently flag the Release-cut sub-path.

`OSSF Scorecard` (1), `Secret-scan baseline` (1), and `Build + test + supply-chain scan` (1 strict) cluster around security-CI mechanisms in awslabs--mcp + FuzzingLabs. They're each independent paths but in the consolidated view, awslabs--mcp alone exhibits 4 of the 16 paths (GitHub Actions, Pre-commit hooks, Codecov, Secret-scan baseline, OSSF Scorecard). The corpus has one extraordinary security-CI exemplar carrying multiple low-count paths. Worth noting for the reconciler — these 1-sample paths are not random distribution; they're concentrated in security-conscious repos.
