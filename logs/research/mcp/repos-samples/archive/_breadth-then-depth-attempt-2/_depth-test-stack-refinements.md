# Depth Pass Refinements — Sample > Test stack

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role. 31 paths total in the consolidated tree, of which 27 have at least one supporting sample (4 zero-count: `Container-based test stack`, `In-memory transport for protocol tests`, `Multi-tier Kotlin testing`, `pytest declared as runtime dependency`). Total sample evidence consumed: ~10 KB across 84 sample sections under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

### Sample > Test stack (role-level)

The current role description — "How the project verifies correctness, and what infrastructure tests depend on. Constrains release cadence and refactor safety." — is accurate but flat. Cross-corpus inspection reveals that the role mixes two orthogonal axes within its 31 paths: **framework choice** (pytest, Vitest, Jest, Go testing, Cargo, Bun, etc.) and **test discipline overlays** (coverage gates, lint/format gates, security-scan adjacency, live-test gating, layered organization, fixture strategy). A sample is typically described by one framework path plus 0-3 discipline overlays — `redis--mcp-redis` exhibits four (pytest + branch-coverage threshold + mypy/bandit, with lint mentioned in the same evidence). The role description should hint at this layering so readers don't expect each path to be mutually exclusive.

Sharpened text suggestion: "How the project verifies correctness, and what infrastructure tests depend on. Splits along two axes — the framework or test runner the project runs (pytest, Vitest, Go's `testing`, Cargo, etc.), and discipline overlays layered on top (coverage gates, lint/format/type-check enforcement, security scans, live-test gating, recorded-fixture replay, multi-tier organization). A given sample typically picks one framework path and zero or more overlays. Constrains release cadence and refactor safety."

### Sample > Test stack > pytest with async + coverage

The existing description is comprehensive but homogenizes 45 samples whose evidence quality varies dramatically. A substantial fraction of supporting samples have evidence amounting only to "`tests/` directory present; framework not directly verified" or "pytest mentioned in README. Specifics not surfaced" — placement is by inference rather than confirmation. Worth signaling so the reconciler knows the count is partly soft.

Cross-corpus evidence on confirmed-vs-presumed:

- Confirmed-from-config (explicit `pytest-asyncio`, `asyncio_mode`, etc.): ~20 samples — `awslabs/aws-api`, `awslabs/aws-doc`, `awslabs/mcp`, `chroma-core`, `crystaldba`, `DiversioTeam`, `jbeno`, `jlowin/fastmcp`, `motherduckdb`, `mukul975`, `normaltusker`, `qdrant`, `redis`, `sandraschi`, `sooperset`, `the-momentum`, `alpacahq`, `modelcontextprotocol/servers`, `mahdin75`, `datalayer/jupyter`.
- Presumed-from-presence (just `tests/` dir or vague README mention): ~15 samples — `AlwaysSany`, `alexei-led`, `blazickjp`, `echelon-ai-labs`, `FuzzingLabs`, `lanbaoshen`, `misbahsy`, `openags`, `opensearch-project`, `PagerDuty`, `JackKuo666`, `voska`, `tumf`, `utensils`, `zongmin-yu`.
- Sync-pytest only (no async declared): `ktanaka101/duckdb`, `designcomputer/mysql`, `marlonluo2018/pandas`.

Sub-axes within the path that the description folds together but the corpus separates:

- "Coverage gate" (`--cov-fail-under=80`): `redis` only — but redis is also placed under `Branch coverage enforcement` for the same content (see Mis-placed samples below). A standalone sub-axis of "coverage threshold gate" is observable but only in 1 sample.
- "Async-mode auto" (`asyncio_mode = "auto"`): `jlowin`, `motherduckdb`, `qdrant`, `redis` — 4 samples explicitly. Many others declare `pytest-asyncio` without `asyncio_mode = "auto"`.
- "Cross-deployment markers" (`integration` / `dc_e2e` / `cloud_e2e`): `sooperset` only — encodes deployment matrix into pytest markers. The role description currently mentions this; cross-corpus evidence confirms it remains a one-sample idiosyncrasy.
- "Dual `pytest.ini` + `pyproject.toml` legacy split": `designcomputer`, `normaltusker`, `sandraschi`, `datalayer/jupyter` — 4 samples. Worth keeping as a noted variant.
- "Test plan in markdown": `jbeno` only — single sample.
- "Top-level test files outside `tests/`": `marlonluo2018` only.

Sharpened text suggestion: keep the bulk of the existing prose but tighten the framing — "This is the dominant Python test stack (45 of 84 samples), though about a third of those placements rest on a directory-presence signal rather than confirmed config. Within the path, three sub-patterns recur: explicit `asyncio_mode = "auto"` config (4 samples) versus `pytest-asyncio` declared without auto-mode (most samples) versus sync-only pytest (3 samples — `ktanaka101`, `designcomputer`, `marlonluo2018`). Coverage tooling is usually `pytest-cov` for measurement only; coverage thresholds (`--cov-fail-under=80` in `redis`) and branch-coverage flags (`--cov-branch` in `awslabs/aws-doc`) appear only in 1-2 samples each. ..." — and drop the implicit "everyone uses asyncio_mode auto" framing.

### Sample > Test stack > Linter/formatter test gate

The path name says "test gate" but most supporting samples describe lint/format/type-check tooling as **alongside** tests in the dev stack, not as a hard gate that fails the build. Only 2 of 7 samples (`normaltusker`, `rust-mcp-stack`) describe enforcement explicitly — normaltusker via "Black formatting (100-char line limit), isort import sorting enforced as part of lint surface" and rust-mcp-stack via `Makefile.toml` defining `fmt` / `clippy` / `test` / `check` as a composite. The other 5 (`alpacahq`, `awslabs/aws-api`, `sooperset`, `the-momentum`, `tumf`) just declare ruff/mypy/black in dev deps without surfacing CI-gating evidence. The "test gate" framing implies stronger enforcement than the corpus supports.

Cross-corpus evidence on tooling combinations:

- `ruff` only: 1 sample (`awslabs/aws-api-mcp` — ruff + pyright)
- `ruff` + `black` (redundant): 2 samples (`sooperset`, `tumf`)
- `ruff` + `mypy`: 1 sample (`alpacahq`)
- `ruff` + `ty` (mypy alternative): 1 sample (`the-momentum`)
- `black` + `isort` only: 1 sample (`normaltusker`)
- `rustfmt` + `clippy`: 1 sample (`rust-mcp-stack`)

Sharpened text suggestion: rename the conceptual framing from "gate" to "stack" since the evidence supports the latter — most samples describe the lint/format/type-check toolchain as dev-time tooling, with CI integration implicit but rarely the gate-at-the-PR-line that "gate" implies. Suggested rewrite: "Lint/format/type-check tooling declared as a dev-time stack alongside the test framework. Runs in CI for most samples but explicit failure-gating is rarely surfaced. Toolchain choices: `ruff` is dominant (5 of 7 samples), often paired with `mypy` or its alternatives (`pyright`, `ty`); `black` still co-appears with `ruff` in 2 samples (redundant since modern `ruff format` covers most of what `black` did); pre-commit hooks enforce locally. Rust projects use `rustfmt` + `clippy` orchestrated through `Makefile.toml`."

If the rename feels heavier than warranted, an alternative is to keep the path name and tighten the description's verb to "declared" rather than "gates."

### Sample > Test stack > Branch coverage enforcement

The current description correctly identifies `--cov --cov-branch` as branch-coverage, but the path holds 2 samples and one of them (`redis`) actually exhibits a different mechanism — a coverage threshold gate (`--cov-fail-under=80`), which measures statement coverage and fails below threshold, not branch coverage. The path is one mechanism with one supporter (`awslabs/aws-doc`); the second supporter is mis-placed.

See Mis-placed samples below for the proposed move.

If `redis` is moved out, the path returns to a clean 1-sample idiosyncrasy. The description text itself does not need sharpening — it correctly describes the mechanism as observed in `awslabs/aws-doc`.

### Sample > Test stack > MyPy strict + Bandit security scans alongside tests

The path bundles two distinct concerns — strict static typing (mypy) and security scanning (bandit/safety). All 3 supporting samples have at least one of each, but the framing as a single path implies they always co-occur. Cross-corpus evidence:

- `normaltusker`: MyPy strict + Bandit (both)
- `redis`: mypy + black + bandit + safety (both, plus extras)
- `sandraschi`: Ruff + MyPy + Bandit (both, plus lint)

In all 3, both mypy and bandit appear together. The path holds. But the description should note that these projects characteristically run a 3-way stack (lint + type + security) — in 2 of 3, ruff is also present, putting them in overlap with `Linter/formatter test gate`. The boundary between the two paths is whether the project foregrounds security scanning as a first-class CI step.

Sharpened text suggestion: "In addition to runtime tests, pyproject.toml configures strict static type checking (`mypy` strict, sometimes paired with `pyright` or `ty`) AND security scanning (`bandit` for SAST, sometimes `safety` for dependency-vulnerability checks). All 3 supporting samples run both alongside lint (`ruff`/`black`) — the overlap with `Linter/formatter test gate` is genuine; this path foregrounds the security tier specifically. Appropriate for security-sensitive servers and projects where a public `bandit` clean signal matters."

### Sample > Test stack > End-to-end protocol-conformance harness

The current description focuses on "dedicated subdirectory" testing the MCP protocol surface end-to-end. Cross-corpus evidence reveals two distinct sub-shapes inside this path:

- Project-rooted `e2e/` directory testing the MCP server's wire compliance: `apollographql/apollo-mcp-server` (`/e2e/mcp-server-tester`), `github/github-mcp-server` (`e2e/`).
- SDK-rooted `conformance-test/` module testing spec compliance for an SDK that downstream consumers rely on: `modelcontextprotocol/kotlin-sdk` (`conformance-test/`).
- README-asserted "end-to-end regression tests" without dedicated directory shape: `openags/paper-search-mcp`.

The 3 shapes share intent (verify protocol behavior) but differ in posture: server-author proves their server speaks MCP, vs. SDK-author proves their SDK passes conformance. The current description leans toward the server case; the kotlin-sdk inclusion is an asymmetric fit.

Sharpened text suggestion: "Dedicated subdirectory exercising MCP protocol behavior end-to-end. Two postures: (1) server projects ship `e2e/` directories (`apollo-mcp-server`, `github-mcp-server`) testing that their server speaks MCP correctly; (2) SDK projects ship `conformance-test/` modules (`kotlin-sdk`) testing that their SDK passes spec conformance — a deliverable in its own right since downstream servers depend on the SDK's correctness. Distinct from unit tests of business logic. The path collapses both postures since the harness shape is the same; readers should weigh the posture from the project type."

### Sample > Test stack > Mock transport layer for protocol-level testing

Description is accurate for the 2 supporting samples (`conikeec/mcpr`, `kotlin-sdk`) but the framing — "Library/SDK projects ship mock transport implementations so their tests (and downstream consumers' tests) can exercise protocol message flow" — fits both. Cross-corpus inspection reveals the kotlin-sdk evidence also explicitly mentions Knit-based code-snippet testing as a documentation-as-test variant, which the current description treats as a parenthetical. This is a single sample, so a sub-axis split isn't warranted, but Knit deserves a sentence rather than a parenthetical.

Sharpened text suggestion: keep the existing prose; promote the Knit mention from parenthetical to a sentence: "Knit-based code-snippet testing in `kotlin-sdk` is a related but distinct discipline — documentation snippets execute as tests, ensuring README examples don't drift from the API. Surfaces only in spec-conforming SDKs where docs are part of the deliverable." Or fold it into the `End-to-end protocol-conformance harness` description since the kotlin-sdk evidence appears in both paths.

### Sample > Test stack > MCP Inspector as test driver

Description is accurate. Both supporting samples (`jparkerweb/mcp-sqlite`, `v-3/discordmcp`) match: `npm test` wired to inspector OR `npx @modelcontextprotocol/inspector` documented as the verification path. The "sometimes recommended (rather than wired) for Python servers as a manual debugging aid" line is generally accurate but no Python sample currently sits under this path. Suggest dropping or scoping that line — the cross-corpus signal is "TS/Node-only path."

Sharpened text suggestion: "`@modelcontextprotocol/inspector` invoked via `npm test` (`jparkerweb/mcp-sqlite`) or documented as the manual verification path (`v-3/discordmcp`). Both supporting samples are TypeScript/Node — Python servers occasionally mention Inspector for debugging in `Inspector compatibility called out` under host integration, but not as an `npm test` substitute. Often the only documented testing approach for minimal projects. Appropriate when the value is in protocol-level integration rather than unit-level coverage."

### Sample > Test stack > Vitest (TypeScript / Node)

Description is accurate but tilts toward "Turbo monorepo" framing that fits 1 of 6 supporting samples (`cloudflare/mcp-server-cloudflare`). Most are standalone single-package TS projects (`GLips`, `idosal`, `makenotion`, `mongodb-js`, `ppl-ai`). Suggest demoting Turbo to a noted variant rather than a featured pairing.

Sharpened text suggestion: "`npm test` (or `pnpm test`) runs Vitest with coverage configured (`npm run test:coverage`); tests under `/tests` configured via `vitest.config.ts`. Standard modern-TS choice; appropriate for TypeScript servers, particularly those that want async ergonomics, TypeScript-native ESM, and faster runs than Jest. Sometimes used inside Turbo monorepos (`cloudflare/mcp-server-cloudflare`)."

### Sample > Test stack > Go stdlib testing

Description is accurate. Cross-corpus evidence is consistent across all 6 samples — `*_test.go` co-located with implementation, `e2e/` or `integration_test.go` for higher tiers, `golangci.yaml` for lint when present. The path needs no sharpening.

### Sample > Test stack > Dev extras gating test deps

Description is accurate but the supporting evidence reveals an inverted case: `misbahsy/video-audio-mcp` is placed under this path with the note "Test deps NOT properly gated — `pytest` lands under `[project.dependencies]`." That sample's content describes an anti-pattern, not the pattern the path defines. It should be moved out (see Mis-placed samples), and the zero-count `pytest declared as runtime dependency` path should receive it.

Sharpened text suggestion (for the path itself, after the move): existing prose is fine. "Test dependencies installed via `pip install -e .[dev]` or equivalent (e.g., `[test]` extra, dependency-groups). Keeps the runtime install lean by isolating pytest and friends from end-user installs."

### Sample > Test stack > No tests / not surfaced

Path bundles two genuinely distinct populations:

- **Confirmed absence** (no tests directory, no test framework declared): `JackKuo666`, `hannesrudolph`, `twolven`, `v-3` (note: `v-3` is also under `MCP Inspector as test driver` — both apply since Inspector replaces unit tests but the framework absence holds), `zilliztech`.
- **Not surfaced in extract** (test framework details not extracted, but tests/ may exist): `baryhuang`, `feiskyer` (CI suggests tests run), `microsoft/playwright-mcp` (Playwright's own test harness implied), `reminia`, `upstash` (private monorepo).

The first group is informative — testing is genuinely absent. The second group is an artifact of the data extraction limit, not the project's discipline. Bundling the two understates how many MCP servers actually ship with no tests vs. how many merely have undocumented tests.

Sharpened text suggestion: keep the path single but make the bifurcation explicit — "Two sub-populations are folded here: (a) confirmed-absent test infrastructure (no `tests/` directory, no test framework declared in dependencies) — common for hobbyist or single-author repos, single-file experimental servers, and configs-only repos; (b) undocumented in extract — README is silent on tests, but a `tests/` directory or CI workflow may exist (`microsoft/playwright-mcp`, `feiskyer/mcp-kubernetes`, `upstash/context7`). The first sub-population reflects project discipline; the second reflects extraction depth. Absence of test discussion in documentation is itself a corpus-level signal — testing is rarely a marketed feature for MCP servers."

Or, if the reconciler prefers, split into two sibling paths: `No tests — confirmed absent` and `Tests not surfaced — extraction-limited`. The split is concrete and the populations are roughly even. See Proposed bucket splits.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

### Sample > Test stack > pytest with async + coverage — confirmed-from-config vs presumed-from-presence

About 20 samples have explicit `pytest-asyncio` / `asyncio_mode` / `pytest-cov` config in evidence; about 15 have only "tests/ directory present" or "pytest mentioned in README." Fold into the description as a confidence note — does not warrant a split. The path is still "pytest-flavored Python testing."

### Sample > Test stack > pytest with async + coverage — sync-pytest variant

3 samples (`ktanaka101`, `designcomputer`, `marlonluo2018`) declare pytest without async support. The path name implies async; these don't fit cleanly. Either: (a) rename the path to "pytest" (broader); (b) fold the sync variant into the description with a note; (c) split out a "pytest sync-only" path with 3 supporters.

Recommendation: fold into description, note that "a minority of samples (3) declare pytest without async support — typically older or single-script projects." Splitting for 3 samples doesn't justify a new path.

### Sample > Test stack > Linter/formatter test gate — security-scan adjacency

2 of 7 supporting samples (`sooperset`, `tumf`) declare ruff+black+mypy without bandit/safety; 1 (`normaltusker`) overlaps with `MyPy strict + Bandit`. The path's boundary against `MyPy strict + Bandit` is whether security scanning is foregrounded. Currently 1 sample sits in both paths — that's the right placement for it.

### Sample > Test stack > End-to-end protocol-conformance harness — server vs SDK posture

See description sharpening above. 3 server samples vs 1 SDK sample. Fold into description; not a split candidate at current sample count.

### Sample > Test stack — multi-tier organization signals

Three paths describe layered test organization: `Pyramid with web E2E` (1 sample), `Stratified suite with unit + integration + cache + security tiers` (1 sample), `Separate integration_tests/ directory` (1 sample). Each surfaces from a single sample with bespoke labeling. Consolidating into a single "Layered test organization" parent with sub-axes would risk over-merging — the three describe genuinely different concerns (web-UI E2E + DB ephemerality vs. unit/integration/cache/security tier list vs. simple two-directory split). Suggest noting in the role-level description that "layered test organization is observed in 3 samples with bespoke shapes — `Pyramid with web E2E`, `Stratified suite ...`, `Separate integration_tests/`" so readers see the pattern even though no merge is warranted.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None. Each path describes a distinct framework, mechanism, or discipline. The role's tree converged well across Pass 1/2/3 — no merges surfaced from cross-corpus inspection.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

### Sample > Test stack > No tests / not surfaced

Currently 10 samples, but 2 distinct populations: confirmed-absent (5 samples) vs not-surfaced-in-extract (5 samples). The discipline signal is different — confirmed-absent reflects project choice, not-surfaced reflects extraction limit. A reader interpreting "10 samples have no tests" overstates the rate of intentional test-absence.

Proposed split:

- `No tests — confirmed absent`: `JackKuo666`, `hannesrudolph`, `twolven`, `v-3`, `zilliztech` (5 samples)
- `Tests not surfaced — extraction-limited`: `baryhuang`, `feiskyer`, `microsoft/playwright-mcp`, `reminia`, `upstash` (5 samples)

Recommendation: defer to reconciler. The split is clean but adds another path to a role that already has 27 active paths. Folding the bifurcation into a single description (per Description sharpening above) is the lighter-weight option.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

### redis--mcp-redis under `Branch coverage enforcement` better fits a coverage-threshold path

The redis evidence under `Branch coverage enforcement` is: "Coverage fail-threshold (`--cov-fail-under=80`) configured in `addopts`." That's a coverage-threshold gate (statement coverage with a fail-below-N threshold), not branch-coverage measurement (`--cov-branch`). The other supporter of `Branch coverage enforcement` (`awslabs/aws-doc`) genuinely runs `--cov --cov-branch`. The two mechanisms are orthogonal — branch-coverage is a measurement granularity, threshold is a fail-gate.

Options for the reconciler:

- **Move + new path.** Create `Coverage threshold gate` and place `redis` there alone. `Branch coverage enforcement` returns to 1 supporter (`awslabs/aws-doc`).
- **Move + fold.** Move `redis` to a "Coverage threshold gate" sub-axis under `pytest with async + coverage` (where redis is also placed) and drop `Branch coverage enforcement` as redundant — but then the awslabs/aws-doc evidence loses its home unless it gets a similar sub-axis.
- **Keep with description fix.** Broaden `Branch coverage enforcement` to "Coverage discipline (branch and/or threshold)" — but this loses Trigger Specificity since the two mechanisms differ.

Recommendation: Move + new path. The coverage-threshold-gate mechanism is observable in 1 sample and worth representing distinctly. Even with 1 supporter, the path captures the discipline cleanly.

### misbahsy--video-audio-mcp under `Dev extras gating test deps` better fits the zero-count `pytest declared as runtime dependency` path

The misbahsy evidence is: "Test deps NOT properly gated — `pytest` lands under `[project.dependencies]` rather than `[dependency-groups]`. Likely oversight rather than design choice." That's the textbook description of the existing `pytest declared as runtime dependency` path, which currently has 0 supporters because misbahsy was placed under the inverse path. The placement appears to invert the path's meaning — `Dev extras gating test deps` describes a project that **does** gate test deps, but misbahsy is described as **not** gating them.

Recommendation: Move misbahsy to `pytest declared as runtime dependency`. That path goes from 0 to 1 supporter; `Dev extras gating test deps` goes from 5 to 4 supporters.

### v-3--discordmcp under `No tests / not surfaced` and `MCP Inspector as test driver` — joint placement is correct but worth noting

`v-3` is placed under both paths. The evidence under `No tests`: "No unit test framework documented." Evidence under `MCP Inspector`: "`npx @modelcontextprotocol/inspector node build/index.js` documented as the verification path. No unit-test framework wired up." Both are accurate — the project has no unit tests AND uses Inspector as its sole verification path. This is a legitimate dual-placement, not a mis-placement, but the reconciler might want to deduplicate by moving v-3 fully into `MCP Inspector as test driver` (since Inspector IS the test driver, even if not unit tests). Surfacing for judgment, not as a clear move.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

### Test discipline correlates strongly with project type, not popularity

Across the 84 samples in this role, test depth tracks more strongly with project-type (vendor-published vs. hobbyist; SDK vs. server; database-wrapper vs. random-tool-wrapper) than with stargazer count. The richest test stacks (`jlowin/fastmcp`, `redis/mcp-redis`, `mukul975/cve-mcp-server`, `neondatabase/mcp-server-neon`, `getsentry/sentry-mcp`) come from frameworks-themselves, vendor-engineering teams, and security-domain projects. Hobbyist-and-single-author servers with significant star counts (`v-3/discordmcp`, `twolven/mcp-server-puppeteer-py`, `JackKuo666/PubMed-MCP-Server`) often ship with no tests at all. The role-level description's "Constrains release cadence and refactor safety" framing is accurate but understates: in this corpus, test stack also signals **project provenance** (vendor-built, framework-built, or hobbyist-built).

### "Tests not surfaced" is itself a discipline signal

5 samples land under `No tests / not surfaced` with the second sub-population's framing — README says nothing about tests, even when CI workflows or `tests/` directories exist. That silence itself is a discipline signal: testing is rarely a marketed feature for MCP servers, in contrast to (e.g.) security scanning, which is foregrounded in security-focused projects' READMEs. Could fold into the role-level description: "Test discipline is rarely marketed — even projects with substantial test suites often surface them only as a CI badge, not as a section in the README."

### Coverage gates are vanishingly rare

Across 84 samples, coverage thresholds (`--cov-fail-under=N`) appear in exactly 1 (`redis`, at 80%) and branch-coverage measurement (`--cov-branch`) appears in exactly 1 (`awslabs/aws-doc`). Codecov badges appear in CI integration but rarely tie to a fail-gate. The cross-corpus signal is that coverage discipline is mostly performative (a badge in the README) rather than enforced (a gate in CI). Worth surfacing in the consolidated commentary on coverage discipline if the reader is sizing the gap between "projects do coverage" and "projects enforce coverage."

### TypeScript test stack is more fragmented than Python

Python servers cluster overwhelmingly on pytest (45 of 53 Python samples). TypeScript servers split across Vitest (6), Jest (2), Bun + Vitest (1), TypeScript noEmit-as-test (1), and MCP Inspector as test driver (2 of which are TS). 9 TS samples versus 6 different framework patterns. The role-level description and the consolidated's commentary could note this asymmetry — pytest is a default in Python, but TS lacks an equivalent default and the choice is more visible per project.

### Static-analysis-as-test is a Python-specific phenomenon

`Linter/formatter test gate` (7 samples), `MyPy strict + Bandit security scans alongside tests` (3 samples), and `TypeScript noEmit type-check as the test command` (1 sample) all live at the boundary between "test" and "static analysis." All Python samples in those paths declare ruff+mypy+bandit as dev tooling rather than as discrete `mypy.yml` jobs; TypeScript samples integrate `tsc --noEmit` as the only test surface in 1 case. The pattern of "static analysis is part of the test stack" is more a Python idiom than a cross-language one.

### Mockable transport is concentrated in framework/SDK projects

Both `Mock transport layer for protocol-level testing` samples (`conikeec/mcpr`, `kotlin-sdk`) and the zero-count `In-memory transport for protocol tests` describe testing patterns specific to framework/SDK projects rather than server projects. The pattern is "the transport layer is a public API; we ship mocks so consumers can test against us." Server projects don't surface this because their transport is not the consumer-facing concern. Worth noting in the role description: "Mock-transport and in-memory-transport patterns are framework/SDK concerns; servers consume one transport and don't ship mocks."

### Multi-tier Kotlin testing is dead bucket

The path has 0 supporters. The kotlin-sdk evidence that originally seeded it (`kotlin-sdk-testing` module + `integration-test/` + `conformance-test/` + Knit) was redistributed across `Mock transport layer for protocol-level testing` (`kotlin-sdk-testing` + Knit) and `End-to-end protocol-conformance harness` (`conformance-test/`) during Pass 2/3. The Multi-tier Kotlin path is now an orphan. Recommend deletion.
