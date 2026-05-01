# BaseInfinity/sdlc-wizard

> Note: the URL `github.com/BaseInfinity/sdlc-wizard` redirects to the canonical name `BaseInfinity/agentic-ai-sdlc-wizard`. All observations below are from the canonical repo.

## Identification

- **URL**: https://github.com/BaseInfinity/agentic-ai-sdlc-wizard (redirected from `.../sdlc-wizard`)
- **Stars**: 3
- **Last commit date**: 2026-04-20 (`fix(docs): bump update skill example to 1.35.0`)
- **Default branch**: `main`
- **License**: MIT (declared in `package.json` and `.claude-plugin/plugin.json`); no `LICENSE` file and GitHub license API returns 404, so no SPDX detection by GitHub itself.
- **Sample origin**: primary (community)
- **One-line purpose**: "A self-evolving Software Development Life Cycle (SDLC) enforcement system for AI coding agents" — plans before coding, tests before shipping, asks when uncertain, scores itself via CI.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, paired with a co-located `.claude-plugin/plugin.json` in the same directory.
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper. `owner.{name, email}` is declared at top level. No `metadata.pluginRoot`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: single plugin entry declares `category: "productivity"` and `tags: ["sdlc","tdd","code-quality","testing"]`. (No `keywords` on the marketplace entry; `keywords` does appear in the sibling `plugin.json` as `["sdlc","tdd","code-quality","ai-agent","developer-tools"]` — two separate, drifted keyword lists.)
- **`$schema`**: absent.
- **Reserved-name collision**: no.
- **Pitfalls observed**: Tag and keyword lists diverge across `marketplace.json` (`testing`) and `plugin.json` (`ai-agent`, `developer-tools`) — two vocabularies for the same plugin and no single source of truth. Plugin marketplace version (`1.0.0`) does not track plugin version (`1.35.0`); marketplace wrapper has been frozen since v1.0.0 while plugin moved 35 minors — a maintainer could add plugins later without bumping the wrapper and nothing would notice.

## 2. Plugin source binding

- **Source format(s) observed**: relative — `source: "."` (marketplace and plugin share the repo root).
- **`strict` field**: default (implicit true). Not set on the entry.
- **`skills` override on marketplace entry**: absent.
- **Version authority**: both `plugin.json` and marketplace entry's `version` field carry `1.35.0`, and `package.json` (npm) also carries `1.35.0`. Three-way drift risk. Release workflow only gates `tag == package.json.version` — drift between `package.json` and either `.claude-plugin/*.json` would not be caught.
- **Pitfalls observed**: Version lives in three files (`package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`'s `plugins[0].version`) plus the git tag. Release CI gates one pair; the other two must be bumped by convention. Commit history shows all three *are* bumped together per release commit, but there's no structural enforcement.

## 3. Channel distribution

- **Channel mechanism**: no split. Users install via one of six methods documented in README (`npx agentic-sdlc-wizard init`, `curl | bash`, Homebrew tap, `gh extension`, `npx github:...`, global npm) — every method fetches the latest from npm or main. No stable-vs-latest carve-out, no `@ref` pinning documented.
- **Channel-pinning artifacts**: absent.
- **Pitfalls observed**: Release cadence is aggressive (v1.31→v1.35 in a week, all on main) with no pre-release or beta track — everyone is always on latest. Mitigated by in-product `/update-wizard` skill that diffs CHANGELOG.md before applying, but at the channel level there is no stable floor.

## 4. Version control and release cadence

- **Default branch name**: `main`.
- **Tag placement**: on `main`. `release.yml` gates publish with `git merge-base --is-ancestor HEAD origin/main` — if the tagged commit is not an ancestor of main, the release fails. Observed tags `v1.26.0` through `v1.35.0` all sit on main.
- **Release branching**: none. Long-lived release branches are absent; active feature branches use `feat/*`, `docs/*`, `auto-update/*` prefixes.
- **Pre-release suffixes**: none observed across the last 10 tags (all `vX.Y.0`).
- **Dev-counter scheme**: absent — version is not bumped per-commit; it moves at release time.
- **Pre-commit version bump**: no. Version is bumped manually during the release commit (observed commit message pattern: `release: v1.35.0 — ...`).
- **Pitfalls observed**: No patch releases observed in the last 10 tags — only minor bumps — which suggests the project treats every shippable change as a minor. Fast minor cadence (10 minors in ~1 month) makes the `CHANGELOG.md` (46KB) the only durable release-notes artifact.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` contains only metadata (name, version, description, author, repository, license, keywords), no component path fields. Components are discovered at conventional paths by Claude Code.
- **Components observed**: skills (yes, 4: `sdlc`, `setup`, `update`, `feedback` — all single-file `SKILL.md`), commands (no), agents (no), hooks (yes, `hooks/hooks.json` + 6 bash scripts), .mcp.json (no), .lsp.json (no), monitors (no), bin (no plugin-style `bin/`, but an npm CLI at `cli/bin/sdlc-wizard.js` — separate distribution layer), output-styles (no).
- **Agent frontmatter fields used**: not applicable — no agents.
- **Agent tools syntax**: not applicable.
- **Pitfalls observed**: Plugin layout dogfoods the CLI: the project's own `.claude/skills/` entries are git symlinks (`mode 120000`) into the top-level `skills/` directory, so a single source of skill content serves both the plugin install path and the repo's self-use. Hook scripts live at `hooks/` (not `.claude/hooks/`) and `hooks/hooks.json` references them with `${CLAUDE_PLUGIN_ROOT}/hooks/...` — so the plugin form and the CLI form share content but point at it through different roots (`$CLAUDE_PLUGIN_ROOT` vs `$CLAUDE_PROJECT_DIR`). The CLI-installed `settings.json` template duplicates the hook block with the project-dir prefix; this is a deliberate "single content, two entry forms" pattern.

## 6. Dependency installation

- **Applicable**: yes (for the npm CLI distribution layer).
- **Dep manifest format**: `package.json` at repo root (no runtime dependencies section — the CLI is pure Node stdlib). The plugin itself has no runtime deps.
- **Install location**: npm global / project node_modules for the CLI; the plugin form has no deps.
- **Install script location**: `install.sh` at repo root wraps `npx -y agentic-sdlc-wizard init`; the real work is in `cli/init.js` (called via `cli/bin/sdlc-wizard.js`). No plugin SessionStart installer.
- **Change detection**: `cli/init.js` detects existing installs by filesystem path probe and JSON-merges `settings.json`; it also runs an `OBSOLETE_PATHS` cleanup (e.g., old `.claude/skills/testing/` from v1.17.0 is removed on upgrade). For the wizard doc itself it stamps `<!-- SDLC Wizard Version: X.X.X -->` in `SDLC.md` and the `/update-wizard` skill fetches the remote CHANGELOG to diff.
- **Retry-next-session invariant**: not applicable — installation is user-invoked via npx/CLI, not SessionStart.
- **Failure signaling**: `install.sh` uses `set -euo pipefail` + a `{ ... }` download guard to prevent partial execution; colored error/info helpers; explicit Node >= 18 and npm/npx precondition checks that exit with specific error messages. `cli/init.js` throws typed errors (`err.pluginPaths` when both plugin and CLI forms coexist) and streams colored stderr guidance.
- **Runtime variant**: Node (npm CLI); no Python. Hooks themselves are pure bash (with `jq` as a soft dep — guarded with `command -v jq` checks).
- **Alternative approaches**: Six alternate install paths in README (npx, curl, Homebrew tap, gh extension, `npx github:`, `npm install -g`) — heavy investment in distribution surface area. `curl | bash` is wrapped in a `{ ... }` block specifically to make the download guard robust.
- **Version-mismatch handling**: `instructions-loaded-check.sh` polls `npm view agentic-sdlc-wizard version` at most once per 24h (cached at `$HOME/.cache/sdlc-wizard/latest-version` with strict-semver regex validation) and nudges when installed version trails latest; loud multi-line warning at ≥3 minor gap, mild one-liner otherwise.
- **Pitfalls observed**: Three install modes (npm CLI, Claude plugin, manual markdown copy) all coexist — `cli/init.js` explicitly detects plugin install paths (`~/.claude/plugins-local/sdlc-wizard-wrap/`, `~/.claude/plugins/cache/sdlc-wizard-local/`) and blocks with a typed error when both are present (referenced as PR #181 "dual-channel install drift guardrails"). `instructions-loaded-check.sh` also emits a non-blocking nudge when both coexist. The dual-install collision is a known pitfall the project has already had to engineer against.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — but as an *npm* bin (`package.json.bin.sdlc-wizard = "./cli/bin/sdlc-wizard.js"`), not as a `bin/` directory inside the plugin form.
- **`bin/` files**: `cli/bin/sdlc-wizard.js` (1710 bytes) — Node entry point delegating to `cli/init.js`. Supports `init`, `check`, `--force`, `--dry-run`, `--json`, `--version`, `--help`.
- **Shebang convention**: `#!/usr/bin/env node`.
- **Runtime resolution**: requires Node >= 18 on PATH (enforced by `package.json.engines` and pre-flight in `install.sh`). Not tied to `${CLAUDE_PLUGIN_ROOT}`.
- **Venv handling (Python)**: not applicable — Node.
- **Platform support**: POSIX shell for `install.sh`; Node runs cross-platform. No `.cmd` / `.ps1` shim observed, so Windows-direct install likely relies on npm's auto-generated `.cmd` wrapper.
- **Permissions**: `cli/bin/sdlc-wizard.js` expected to be executable on extract (standard npm behavior); `hooks/*.sh` repo-side are executable (`mode 100755` inferred from their invocation via hook runner).
- **SessionStart relationship**: not applicable — the CLI is out-of-band from the plugin's hook system. The plugin form doesn't use `bin/` at all; the CLI form is the npm distribution.
- **Pitfalls observed**: The project has two disjoint distribution surfaces with overlapping content — the plugin (`.claude-plugin/plugin.json` pointing at `hooks/` and `skills/` at repo root) and the npm CLI (`cli/init.js` copying the same `hooks/*.sh` and `skills/*/SKILL.md` into a consumer's `.claude/`). Both are maintained from one source; the symlink-based `.claude/skills/` dogfooding proves the pattern works but also shows how much plumbing it costs.

## 8. User configuration

- **`userConfig` present**: no (neither in `plugin.json` nor in `marketplace.json`).
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable. Hooks read `$CLAUDE_PROJECT_DIR`, `$CLAUDE_PLUGIN_ROOT`, and `$SDLC_WIZARD_CACHE_DIR` as environment variables but none are surfaced through Claude Code's `userConfig` system.
- **Pitfalls observed**: User-tunable knobs exist (`SDLC_WIZARD_CACHE_DIR`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `effortLevel` read from `settings.json`) but they're surfaced via documentation and direct settings edits rather than through the plugin's `userConfig` schema. This sidesteps the schema but loses the built-in "sensitive" flag and CLI-driven UX.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1 — matcher `Write|Edit|MultiEdit` with an `if:` clause `Write(src/**) Edit(src/**) MultiEdit(src/**)`. Purpose: TDD reminder (emits `hookSpecificOutput.additionalContext` with a "write test first" prompt when the edit target is under `src/`). (The in-repo `.claude/settings.json` uses a different `if:` — `Write(.github/workflows/*) Edit(.github/workflows/*) MultiEdit(.github/workflows/*)` — because this repo has no `src/` directory and TDD applies to its workflow YAML instead.)
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stdout JSON (`{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "..."}}`). Other hooks emit plain stderr human text.
- **Failure posture**: fail-open — `tdd-pretool-check.sh` has no `set -e` and emits JSON only when the path matches; otherwise silent exit. The `instructions-loaded-check.sh` explicitly documents `no set -e — this hook must always exit 0 to not block session start`.
- **Top-level try/catch wrapping**: not applicable (bash, no try/catch). Defensive patterns throughout: `command -v jq > /dev/null 2>&1` guards, `2>/dev/null || echo default` fallbacks on every external call, and non-blocking exit convention.
- **Pitfalls observed**: The `if:` condition uses the documented hook-conditional DSL (`Tool(glob) Tool(glob) ...`), which is a capability worth noting for the pattern doc — conditional hook dispatch without writing the `jq` yourself. The hook path pattern is hard-coded per consumer (comment in `tdd-pretool-check.sh`: "CUSTOMIZE: Change this pattern to match YOUR source directory") rather than configurable — so consumers must edit the script after install. Setup skill patches this.

## 10. Session context loading

- **SessionStart used for context**: no (used for effort/model nudge only — `model-effort-check.sh` drains stdin and emits a plain-text upgrade nudge to stdout).
- **UserPromptSubmit for context**: yes — `sdlc-prompt-check.sh` emits a ~100-token SDLC baseline reminder on every prompt, plus a loud `!! EFFORT BUMP REQUIRED !!` block when ≥2 low-confidence signals land within a 30-min rolling window (cache at `$SDLC_WIZARD_CACHE_DIR`).
- **`hookSpecificOutput.additionalContext` observed**: yes — in `tdd-pretool-check.sh` (PreToolUse). The other hooks emit plain stdout/stderr instead of structured JSON.
- **SessionStart matcher**: none — fires on all sub-events.
- **InstructionsLoaded**: used — `instructions-loaded-check.sh` validates SDLC.md/TESTING.md exist, nudges on missing files, stale version (≥3 minor delta), and open `api-review-needed` issues from the weekly API shepherd.
- **PreCompact**: used with matcher `manual` — `precompact-seam-check.sh` blocks `/compact` when `.reviews/handoff.json` status is `PENDING_REVIEW`/`PENDING_RECHECK` or a git rebase/merge/cherry-pick is in progress. Self-heals on stale handoffs by checking `gh pr view <pr_number>` state. Requires Claude Code v2.1.105+.
- **Pitfalls observed**: Five hook events wired at once (UserPromptSubmit, PreToolUse, InstructionsLoaded, SessionStart, PreCompact) — among the fullest use of Claude Code's hook surface seen. Version floors documented inline in hook comments (e.g., "Available since Claude Code v2.1.69" on `instructions-loaded-check.sh`, "Requires Claude Code v2.1.105+" on `precompact-seam-check.sh`).

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none (unless one counts the workflow-based shepherd as functionally equivalent: `weekly-api-update.yml` detects Claude API changelog entries and opens/updates a tracking issue; `instructions-loaded-check.sh` then nudges the session on next start).
- **`when` values used**: not applicable.
- **Version-floor declaration**: Claude Code version floors inline in hook shebang comments (`v2.1.69` for InstructionsLoaded, `v2.1.105+` for PreCompact); `SDLC.md` is said (per CHANGELOG) to carry `v2.1.111+` as a project-wide baseline. None surfaced in `plugin.json`.
- **Pitfalls observed**: Instead of monitors, this project uses GitHub-side scheduled workflows as a "shepherd" pattern (their term) — detection happens in CI on cron; the session-start hook surfaces outcomes. This is an alternative architecture to the monitors.json pattern and deserves a novel-axis bullet.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none. README lists three "Official Plugin Integration" recommendations (`claude-md-management`, `claude-code-setup`, `code-review`) prose-style, not as machine-readable deps.
- **`{plugin-name}--v{version}` tag format observed**: no — single-plugin repo, tags are plain `vX.Y.Z`.
- **Pitfalls observed**: Integration with other plugins is documented in prose only; there's no manifest-level expression of "we recommend X alongside us." The opportunity cost is that a user installing this plugin gets no automatic hint about the recommended siblings.

## 13. Testing and CI

- **Test framework**: bash scripts (40+ `tests/test-*.sh` files plus `tests/e2e/` harness). No pytest/jest/vitest. CLAUDE.md explicitly notes "No traditional unit tests (bash scripts only)."
- **Tests location**: `tests/` at repo root, with `tests/e2e/` holding the SDLC simulation harness.
- **Pytest config location**: not applicable.
- **Python dep manifest for tests**: not applicable (Python used only for YAML/markdown parsing inline in shell scripts — `python3 -c "import yaml; ..."`).
- **CI present**: yes.
- **CI file(s)**: 8 workflows — `ci.yml` (80KB, 1768 lines), `release.yml` (1.3KB), `pr-review.yml`, `weekly-update.yml` (59KB), `weekly-api-update.yml`, `monthly-research.yml` (20KB), `benchmark-autocompact.yml`, `benchmark-model-comparison.yml`.
- **CI triggers**: `ci.yml` — `pull_request [opened, synchronize, reopened, labeled]`, `push: branches: [main]`, `workflow_dispatch`. `release.yml` — `push: tags: ['v*']`. `pr-review.yml` — `pull_request [opened, synchronize, ready_for_review]` + `pull_request_target [labeled]`. Three cron-scheduled workflows (weekly Monday 09:00 UTC, weekly Monday 10:00 UTC, monthly 1st 11:00 UTC).
- **CI does**: `ci.yml` runs a validate job (40+ `tests/test-*.sh` scripts), then a Tier 1 "E2E Quick Check" that drives the real `anthropics/claude-code-action@v1` on both baseline (main) and candidate (PR) wizards and scores the simulated SDLC compliance, then Tier 2 ("merge-ready" label) which runs 5 evaluations each side and compares with t-distribution 95% CI.
- **Matrix**: none for the main validate job. `benchmark-autocompact.yml` uses a matrix over `inputs.thresholds` (comma-separated list). `benchmark-model-comparison.yml` uses `workflow_dispatch` inputs for model/effort/scenario.
- **Action pinning**: by major tag — `actions/checkout@v5`, `actions/setup-node@v5`, `actions/upload-artifact@v6`, `anthropics/claude-code-action@v1`, `marocchino/sticky-pull-request-comment@v3`. No SHA pinning observed.
- **Caching**: built-in `actions/setup-node@v5` cache would apply if enabled; no `actions/cache` observed. State files (`.github/last-checked-version.txt`, `.github/last-checked-api-date.txt`, `.github/last-community-scan.txt`) act as persistent "where did I leave off" markers rather than build caches.
- **Test runner invocation**: direct `./tests/test-*.sh` from within the workflow step list (one step per test file).
- **Pitfalls observed**: The CI test-runner is a flat list of ~40 `./tests/test-*.sh` steps, each named individually — no discovery, no wrapper — which gives visible step-level timing but forces every new test to be registered in the workflow too. CI also *itself* runs Claude against scenarios (meta-dogfood: the plugin evaluates itself by running Claude on a fixture). `concurrency` block on `ci.yml` with `cancel-in-progress: true` prevents stale re-runs. There's deliberate separation of stderr and stdout when capturing evaluator output — a recurring lesson in their CHANGELOG.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes.
- **Release trigger**: `push: tags: ['v*']`.
- **Automation shape**: tag-sanity gates (two) + npm publish with `--provenance` + GitHub Release via `gh release create --generate-notes`. Uses `permissions: id-token: write` to enable sigstore provenance.
- **Tag-sanity gates**: two — (a) `git merge-base --is-ancestor HEAD origin/main` to prove the tagged commit is on main; (b) tag value (`${GITHUB_REF#refs/tags/v}`) must equal `package.json.version`. Failure of either aborts publish with a targeted `::error::` message. No tag-format regex beyond the trigger's `v*` glob.
- **Release creation mechanism**: `gh release create "$TAG_NAME" --generate-notes` — generates release notes from PR titles since last tag rather than parsing CHANGELOG.md. `softprops/action-gh-release` is *not* used.
- **Draft releases**: no — releases publish directly; observed releases all `draft: False, prerelease: False`.
- **CHANGELOG parsing**: no — `CHANGELOG.md` is human-maintained but release notes come from `--generate-notes`. `CHANGELOG.md` is the durable artifact for in-product `/update-wizard` skill, which fetches it via WebFetch and diffs against the installed version stamp.
- **Pitfalls observed**: The deep-gating is exactly two checks (on-main-ancestor + tag=package.version). Notably, the gates do *not* check that the tag matches `plugin.json` or `marketplace.json` — so a maintainer who forgets to bump those would still publish a valid npm release with drifted plugin-side metadata. Release job uses `actions/setup-node@v5` with `node-version: 22` + `registry-url: https://registry.npmjs.org` + `NODE_AUTH_TOKEN` from `NPM_TOKEN` secret. `fetch-depth: 0` on checkout is required for the `git merge-base --is-ancestor` gate to have history.

## 15. Marketplace validation

- **Validation workflow present**: yes — `tests/test-plugin.sh` is wired into `ci.yml` ("Run plugin format tests"). Additionally, `ci.yml`'s validate job runs its own inline YAML-validity check (`python3 -c "import yaml; yaml.safe_load(...)"`) and a regex sweep for unsafe `${{ }}` interpolation patterns.
- **Validator**: custom bash + inline Python yaml.safe_load. No bun+zod, no `claude plugin validate`.
- **Trigger**: PR + push-to-main (through `ci.yml`).
- **Frontmatter validation**: not specifically observed — the validate job covers YAML workflow validity + state-file presence + plugin format; it does not scan skill frontmatter fields in-depth.
- **Hooks.json validation**: likely covered by `test-hooks.sh` (90KB test file) but scope wasn't inspected.
- **Pitfalls observed**: The inline "unsafe variable interpolation" regex is a watch-for-regressions guard specifically referenced in CHANGELOG — hardening evolved from prior production breakage. CI enforces state-file existence (`last-checked-version.txt`, `last-community-scan.txt`, `last-checked-api-date.txt`) as a structural invariant, treating shepherd state as part of the repo's public contract.

## 16. Documentation

- **`README.md` at repo root**: present (~11KB). Strong opening pitch + install + "What Makes This Different" + "How This Compares" + "Documentation" section linking out to sub-docs + Community (Discord badge) + Feedback loop (three surfaces: `/feedback` skill, issue templates, discussions).
- **Owner profile README at `github.com/BaseInfinity/BaseInfinity`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: not applicable (single-plugin repo; there's no separate plugin-scoped README).
- **`CHANGELOG.md`**: present (~46KB, heavy detail). Format is Keep-a-Changelog-like (`## [X.Y.Z] - YYYY-MM-DD` with `### Added`, `### Fixed`, `### Docs` sections) and doubles as the source the in-product `/update-wizard` skill consumes.
- **`architecture.md`**: present as `ARCHITECTURE.md` (uppercase, ~11KB) at repo root — multi-layer diagram, hooks/skills tables, self-update flow.
- **`CLAUDE.md`**: present at repo root — project instructions specifically for Claude when operating *on this repo*, separate from the wizard doc `CLAUDE_CODE_SDLC_WIZARD.md` which is the shipped artifact.
- **Community health files**: `CONTRIBUTING.md` (7.1KB), `AGENTS.md` (2.9KB), `.github/ISSUE_TEMPLATE/{bug_report,feature_request,question,config}`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/FUNDING.yml`. Also `CODE_REVIEW_EXCEPTIONS.md`, `COMPETITIVE_AUDIT.md`, `ISSUES_FOUND_BY_CODEX.md`, `RESEARCH_58_CLAW_OMO_OMX.md`, `ROADMAP.md` (72KB), `SCORE_TRENDS.md`, `SDLC.md`, `TESTING.md`, `SCORE_TRENDS.md`, `CI_CD.md`, `AUTOCOMPACT_BENCHMARK.md`, `CODEX_ADAPTER_PLAN.md`, `CODEX_AUDIT_PROGRESS.md`. No `LICENSE`, no `SECURITY.md`, no `CODE_OF_CONDUCT.md`.
- **LICENSE**: declared `"MIT"` in manifests; no SPDX-identifiable `LICENSE` file at repo root (GitHub license API returns 404). This is a documentation bug worth flagging — npm will ship the package without a LICENSE file in the tarball unless it's added to `package.json.files`.
- **Badges / status indicators**: a Discord "Automation Station" badge in the Community section. No CI-status or npm-version badges.
- **Pitfalls observed**: The repo has an unusually large documentation surface (~20 top-level markdown files). Much of it is meta-project artifact (roadmap, audit, research notes) rather than user-facing. The main `README.md` stays focused on the user; the sprawl is absorbed into sibling docs. Also: `CLAUDE.md` is the project instruction file *for contributors' Claude sessions*, while `CLAUDE_CODE_SDLC_WIZARD.md` is the wizard document *shipped to consumers* — this is a clear two-hat distinction worth adopting as a pattern. Missing `LICENSE` file despite declaring MIT is a real defect.

## 17. Novel axes

- **Statistical CI evaluation of the plugin itself.** `ci.yml` runs two tiers of "does this wizard actually make Claude better" evaluation. Tier 1 (every PR) is 1 baseline + 1 candidate simulation; Tier 2 (on `merge-ready` label) is 5+5 with t-distribution 95% CI computed from `tests/e2e/lib/stats.sh` and a `compare_ci` verdict (`IMPROVED`/`STABLE`/`REGRESSION`). Bootstrapping mode handles the "no baseline wizard yet" case. An SDP (score-divergence-from-prior) metric adjusts for external model conditions and emits a `Robustness` score (<1.0 = resilient, >1.2 = fragile). Result is posted to the PR as a sticky comment. This is a novel pattern worth its own section — self-measuring plugin CI.

- **"Shepherd" pattern for external-change watchers.** Three cron workflows (`weekly-update.yml`, `weekly-api-update.yml`, `monthly-research.yml`) poll external sources (Claude Code releases, Anthropic API changelog, community forums). They do cheap detection only; they open/update a single tracking GitHub issue; `instructions-loaded-check.sh` nudges the session toward those issues at next start. This replaces what a `monitors.json` could do and extends it into durable issue tracking. The API-changelog detector specifically fetches `.md` URLs (Mintlify convention) rather than scraping rendered HTML — a deliberate stability choice documented in the workflow header.

- **Symlinked dogfood layout.** `.claude/skills/{feedback,sdlc,setup,update}` in this repo are git symlinks (mode 120000) into the top-level `skills/` directory. The plugin form, the CLI install form, and the repo's own self-use all share one source-of-truth set of SKILL.md files.

- **Hook-level conditional dispatch via `if:` DSL.** `hooks/hooks.json` uses `"if": "Write(src/**) Edit(src/**) MultiEdit(src/**)"` on a PreToolUse entry — conditional dispatch at the harness level, not inside the hook script. This is a deferred-tool-style optimization: the hook doesn't even fire for non-matching paths.

- **Effort auto-bump via rolling log.** `sdlc-prompt-check.sh` scans each UserPromptSubmit payload for a curated list of first-person distress phrases ("i'm stuck", "it keeps failing", "confidence: low", ...) and logs timestamped hits to `$HOME/.cache/sdlc-wizard/effort-signals.log`. At ≥2 signals within 30 minutes it emits a loud `!! EFFORT BUMP REQUIRED !!` block with the exact `/effort xhigh` command. This is session-state-across-prompts, in a stateless hook, via a pruned log file.

- **PreCompact self-healing seam gate.** `precompact-seam-check.sh` blocks `/compact` when `.reviews/handoff.json` status is `PENDING_*` or when a git rebase/merge/cherry-pick is in progress — but self-heals if the handoff has a `pr_number` and `gh pr view` reports `MERGED`. Matcher is `manual` only, deliberately, because blocking auto-compact could push context over 100% and lose everything. This is a precise tradeoff worth surfacing.

- **Three-surface install (plugin + npm CLI + curl-bash).** Same content, three delivery paths, guarded against dual-install by typed-error detection in `cli/init.js` and a nudge in `instructions-loaded-check.sh`. The engineering cost of this redundancy is documented in CHANGELOG PR #181.

- **Dual independent tag/keyword vocabularies.** `marketplace.json` carries `tags: [sdlc, tdd, code-quality, testing]`; `plugin.json` carries `keywords: [sdlc, tdd, code-quality, ai-agent, developer-tools]`. Discoverability is split across two lists with no single source.

- **Meta-recursive docs.** `CLAUDE.md` governs the contributor's Claude session on this repo; `CLAUDE_CODE_SDLC_WIZARD.md` is the 193KB *shipped wizard doc* consumers `cat` or `WebFetch` during setup. Two CLAUDE-like files with clearly different audiences.

## 18. Gaps

- **Plugin-form hook invocation vs CLI-form hook invocation — actual behavior under both.** The plugin's `hooks/hooks.json` references `${CLAUDE_PLUGIN_ROOT}/hooks/*.sh`; the CLI's `cli/templates/settings.json` references `"$CLAUDE_PROJECT_DIR"/.claude/hooks/*.sh`. I verified the two configurations on disk but did not exercise either to confirm Claude Code resolves both paths consistently. Resolving this would require spinning up a Claude Code session with each install form — out of scope for this research.

- **`test-plugin.sh` contents.** The CI step "Run plugin format tests" invokes a 14.6KB shell test script I didn't fetch. It may encode additional structural invariants about the plugin manifests worth harvesting.

- **Full `cli/init.js` merge semantics.** I read the first ~200 lines; the full file is 15.7KB and the exact `OBSOLETE_PATHS` migration logic, settings.json merge guard for third-party hook entries, and gitignore updater were skimmed but not fully traced.

- **Weekly-update / monthly-research orchestration beyond heads.** Both workflows are large (59KB and 20KB) and the full analysis prompts live in `.github/prompts/analyze-release.md` and `.github/prompts/analyze-community.md` — not fetched here. Their content shape (structured JSON outputs with `relevance`, `summary`, `impact` fields, per README) would be useful for a future "shepherd pattern" writeup.

- **Homebrew tap + GitHub CLI extension repos.** README references `BaseInfinity/sdlc-wizard` (tap) and `BaseInfinity/gh-sdlc-wizard` (gh extension) as separate install paths. Whether these are real, their update cadence, and whether they pin to specific versions — all unresolved.

- **`RESEARCH_58_CLAW_OMO_OMX.md`.** 15KB research note whose title suggests a competitor/ecosystem survey — not read.

- **E2E scoring rubric source.** The "40% deterministic + 60% AI-judged, 10/11 points" rubric is implemented in `tests/e2e/evaluate.sh` and criteria fixtures under `tests/e2e/scenarios/` — not fetched. The precise criteria definitions and their implementation would illuminate how one writes an agent-scored CI check.

- **`AGENTS.md` contents.** 2.9KB file at repo root co-located with CLAUDE.md; likely a sibling instruction doc for other AI tools (OpenAI Codex, etc., referenced throughout CHANGELOG). Not read; its relationship to CLAUDE.md could clarify the "instructions per tool" pattern.
