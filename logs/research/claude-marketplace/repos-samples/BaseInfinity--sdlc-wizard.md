# Sample

Mirrors of `https://github.com/BaseInfinity/agentic-ai-sdlc-wizard` (the URL `BaseInfinity/sdlc-wizard` redirects to this canonical name). "A self-evolving Software Development Life Cycle (SDLC) enforcement system for AI coding agents" — plans before coding, tests before shipping, asks when uncertain, scores itself via CI. MIT licensed (declared in manifests; no LICENSE file at repo root), default branch `main`, last commit 2026-04-20, 3 stars; sample origin: primary (community).

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root, paired with co-located `.claude-plugin/plugin.json`. One plugin entry whose `source` is `"."` — the marketplace and its sole plugin share the same repo root.

### Top-level `metadata` wrapper variants

`metadata.{description, version}` wrapper, paired with `owner.{name, email}` declared at top level. No `metadata.pluginRoot`. No `$schema`. Marketplace `metadata.version` (`1.0.0`) does not track plugin version (`1.35.0`); marketplace wrapper has been frozen since v1.0.0 while the plugin moved 35 minors.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`source: "."` (no trailing slash variant) — marketplace and plugin share the repo root.

### `strict` field default

`strict` not set on the entry (implicit-true default). No `skills` override on the marketplace entry.

## Per-plugin discoverability metadata

### Marketplace-entry facets plus duplicated keywords on plugin.json

Marketplace entry declares `category: "productivity"` and `tags: ["sdlc","tdd","code-quality","testing"]`. `plugin.json` independently carries `keywords: ["sdlc","tdd","code-quality","ai-agent","developer-tools"]`. Two semantically-related but drifted lists: `testing` only on marketplace entry; `ai-agent`, `developer-tools` only in plugin.json. No `keywords` on the marketplace entry; no `$schema` on either manifest.

## Version coordination

### Triple-file version (build manifest joins)

Three carriers: `package.json` (npm), `.claude-plugin/plugin.json`, and marketplace `plugins[0].version`, all currently `1.35.0`. Plus marketplace top-level `metadata.version` frozen at `1.0.0` (independent cadence). Release CI gates only `tag == package.json.version` and tag-on-main; drift between `package.json` and either `.claude-plugin/*.json` would not be caught. Commit history shows all three plugin-version carriers are bumped together per release commit, but no structural enforcement.

## Channel distribution

### Multi-channel via parallel distribution paths

Six install paths documented in README — `npx agentic-sdlc-wizard init`, `curl | bash`, Homebrew tap, `gh extension`, `npx github:...`, global npm install. Every path fetches the latest from npm or main; no stable-vs-latest carve-out, no `@ref` pinning documented. Release cadence is aggressive (v1.31→v1.35 in a week, all on main) with no pre-release or beta track. In-product `/update-wizard` skill diffs CHANGELOG.md before applying as a partial mitigation. README references `BaseInfinity/sdlc-wizard` (Homebrew tap) and `BaseInfinity/gh-sdlc-wizard` (gh extension) as separate install paths.

## Tag and release lifecycle

### Tag-on-main with merge-base ancestry gate

Tags on main; `release.yml` gates publish with `git merge-base --is-ancestor HEAD origin/main` — if the tagged commit is not an ancestor of main, the release fails. Observed tags `v1.26.0` through `v1.35.0` all sit on main. Active feature branches use `feat/*`, `docs/*`, `auto-update/*` prefixes. Pairs with `fetch-depth: 0` on checkout for the ancestry check to have history. No patch releases observed in the last 10 tags — only minor bumps — suggesting the project treats every shippable change as a minor.

## Plugin-component registration

### Default convention discovery

`plugin.json` contains only metadata (name, version, description, author, repository, license, keywords); no component path fields. Components discovered at conventional paths.

## Component composition

### Skills (universal)

Four single-file skills under `skills/`: `sdlc`, `setup`, `update`, `feedback`.

### Hooks

`hooks/hooks.json` plus 6 bash scripts under `hooks/`.

## Plugin-component placement

### Inside plugin directory

Components under conventional paths at repo root: `skills/`, `hooks/`, `commands/` (none).

## Skill authoring conventions

### Standard frontmatter

Each `SKILL.md` carries standard frontmatter.

## Bin entry mechanism

### Node CLI launcher with `env node` shebang

`cli/bin/sdlc-wizard.js` (1710 bytes) is the npm-bin entry (registered as `package.json.bin.sdlc-wizard = "./cli/bin/sdlc-wizard.js"`). Shebang `#!/usr/bin/env node`; supports `init`, `check`, `--force`, `--dry-run`, `--json`, `--version`, `--help`. Requires Node >= 18 (enforced by `package.json.engines` and pre-flight in `install.sh`). Not tied to `${CLAUDE_PLUGIN_ROOT}`. No `.cmd` / `.ps1` shim — Windows-direct install relies on npm's auto-generated `.cmd` wrapper. Distinct from any plugin-side `bin/` directory; the plugin form has no `bin/` at all. The npm CLI is out-of-band from the plugin's hook system.

## Dependency installation

### npm CLI as the sole install surface

Plugin's npm CLI is the install surface for the consumer-side install (`npx agentic-sdlc-wizard init`). Repo-root `package.json` has no runtime dependencies (CLI is pure Node stdlib). Plugin form has no SessionStart installer; no managed install at the plugin level. `install.sh` at repo root wraps `npx -y agentic-sdlc-wizard init`; the real work is in `cli/init.js` (called via `cli/bin/sdlc-wizard.js`). `install.sh` uses `set -euo pipefail` plus a `{ ... }` download guard to prevent partial execution from a `curl | bash` pipe; explicit Node >= 18 and npm/npx precondition checks exit with specific error messages. Hooks themselves are pure bash with `jq` as a soft dep (`command -v jq` guards). No Python.

## Install change detection

### Plugin-version stamp file

`/update-wizard` skill stamps `<!-- SDLC Wizard Version: X.X.X -->` in `SDLC.md`; the skill fetches the remote CHANGELOG and diffs against the installed version stamp. `cli/init.js` runs an `OBSOLETE_PATHS` cleanup on upgrade (e.g., old `.claude/skills/testing/` from v1.17.0 is removed).

## Install trigger and lifecycle

### User-invoked one-shot installer

Installation is user-invoked via npx/CLI/curl-bash, not SessionStart. `cli/init.js` detects existing installs by filesystem path probe and JSON-merges `settings.json`.

## Install failure posture

### Strict-on-failure with typed errors and colored stderr

`install.sh` uses `set -euo pipefail` plus colored error/info helpers. `cli/init.js` throws typed errors (`err.pluginPaths` when both plugin and CLI forms coexist) and streams colored stderr guidance.

## User configuration and authentication

### No userConfig, env-var only

No `userConfig` in `plugin.json` or `marketplace.json`. Hooks read `$CLAUDE_PROJECT_DIR`, `$CLAUDE_PLUGIN_ROOT`, and `$SDLC_WIZARD_CACHE_DIR` as environment variables. User-tunable knobs (`SDLC_WIZARD_CACHE_DIR`, `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`, `effortLevel` read from `settings.json`) are surfaced via documentation and direct settings edits — sidesteps the schema but loses the built-in `sensitive: true` flag and CLI-driven UX.

## Session context loading

### Per-prompt context reminder

`sdlc-prompt-check.sh` (UserPromptSubmit) emits a ~100-token SDLC baseline reminder on every prompt.

### Per-prompt bias / signal detection

`sdlc-prompt-check.sh` also scans the prompt text for first-person distress phrases ("i'm stuck", "it keeps failing", "confidence: low") and logs timestamped hits to `$HOME/.cache/sdlc-wizard/effort-signals.log`. At ≥2 signals within a 30-minute rolling window, emits a loud `!! EFFORT BUMP REQUIRED !!` block with the exact `/effort xhigh` command. State-across-prompts implemented in a stateless hook via a pruned-log file.

### Validate-and-nudge on InstructionsLoaded

`instructions-loaded-check.sh` validates that project documentation files (e.g., `SDLC.md`, `TESTING.md`) exist, nudges on missing files, on stale plugin version (≥3 minor delta), and on open `api-review-needed` issues from a weekly cron. Available since Claude Code v2.1.69 — version floor declared inline in hook comments rather than in `plugin.json`. Also nudges when both plugin install and CLI install coexist.

### Manual-only PreCompact with self-healing seam check

`precompact-seam-check.sh` with matcher `manual` (so auto-compact is never blocked — could push context over 100% and lose everything). On manual `/compact`, reads `.reviews/handoff.json` and blocks if status is `PENDING_REVIEW`/`PENDING_RECHECK`, or if a git rebase/merge/cherry-pick is in progress. Self-heals: if the handoff has a `pr_number` and `gh pr view` reports the PR `MERGED`, the gate clears the status and lets the compact proceed. Requires Claude Code v2.1.105+.

### SessionStart purely for non-context side effects

`model-effort-check.sh` (SessionStart) drains stdin and emits a plain-text upgrade nudge to stderr/stdout. No `additionalContext`/`systemMessage` injection from SessionStart.

## SessionStart matcher scope

### Empty matcher (all sub-events)

No matcher set; fires on all sub-events.

## Tool-use enforcement

### `if:` permission-rule sub-matcher

Single PreToolUse with matcher `Write|Edit|MultiEdit` and `if: "Write(src/**) Edit(src/**) MultiEdit(src/**)"`. The `if:` carries space-separated tool/glob alternatives narrowing the hook to writes under `src/**`. Emits `hookSpecificOutput.additionalContext` with a "write a failing test first" prompt. The repo's own `.claude/settings.json` uses a different `if:` (`Write(.github/workflows/*) Edit(.github/workflows/*) MultiEdit(.github/workflows/*)`) because this repo has no `src/` and TDD applies to its workflow YAML instead. Path pattern is hard-coded per consumer (script comment: "CUSTOMIZE: Change this pattern to match YOUR source directory") rather than configurable; setup skill patches this.

### TDD reminder (PreToolUse on src/ writes)

`tdd-pretool-check.sh` is the handler for the PreToolUse `if:` clause above — emits `hookSpecificOutput.additionalContext` with the "write test first" prompt. Fail-open (no `set -e`); silent on non-matching paths.

## Hook output contract

### `additionalContext` for context injection

`tdd-pretool-check.sh` emits `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "..."}}` on stdout. Other hooks emit plain stderr human text.

## Hook failure posture

### Fail-open with always-exit-0

`instructions-loaded-check.sh` explicitly documents `no set -e — this hook must always exit 0 to not block session start`. Defensive patterns throughout: `command -v jq > /dev/null 2>&1` guards, `2>/dev/null || echo default` fallbacks on every external call.

## Hook handler runtime

### Bash scripts at conventional path

Six bash scripts under `hooks/` registered in `hooks/hooks.json`. `python3` invoked inline for YAML/markdown parsing (`python3 -c "import yaml; ..."`).

## Plugin-to-plugin coordination

### Implicit prose-only dependency

README lists three "Official Plugin Integration" recommendations (`claude-md-management`, `claude-code-setup`, `code-review`) prose-style, not as machine-readable deps. No `dependencies` field in `plugin.json`.

## Testing

### Bash scripts only

40+ `tests/test-*.sh` files plus `tests/e2e/` harness. No pytest/jest/vitest. CLAUDE.md explicitly notes "No traditional unit tests (bash scripts only)." Tests at repo root `tests/`, with `tests/e2e/` holding the SDLC simulation harness.

### CI runs Claude against scenarios — meta-dogfood

`ci.yml`'s Tier 1 "E2E Quick Check" drives the real `anthropics/claude-code-action@v1` on both baseline (main) and candidate (PR) wizards and scores the simulated SDLC compliance. Tier 2 (gated on `merge-ready` label) runs 5 evaluations each side and compares with t-distribution 95% CI computed from `tests/e2e/lib/stats.sh`, emitting a `compare_ci` verdict (`IMPROVED`/`STABLE`/`REGRESSION`). Bootstrapping mode handles the "no baseline wizard yet" case. SDP (score-divergence-from-prior) metric adjusts for external model conditions and emits a `Robustness` score (<1.0 = resilient, >1.2 = fragile). Result is posted to the PR as a sticky comment.

## CI workflow shape

### Multi-workflow split by trigger and concern

Eight workflows: `ci.yml` (80KB, 1768 lines), `release.yml` (1.3KB), `pr-review.yml`, `weekly-update.yml` (59KB), `weekly-api-update.yml`, `monthly-research.yml` (20KB), `benchmark-autocompact.yml`, `benchmark-model-comparison.yml`. `ci.yml` triggers: `pull_request [opened, synchronize, reopened, labeled]`, `push: branches: [main]`, `workflow_dispatch`. `release.yml` triggers on `push: tags: ['v*']`. `pr-review.yml` triggers on `pull_request [opened, synchronize, ready_for_review]` plus `pull_request_target [labeled]`. Three cron-scheduled workflows (weekly Mon 09:00 UTC, weekly Mon 10:00 UTC, monthly 1st 11:00 UTC). `concurrency` block on `ci.yml` with `cancel-in-progress: true` prevents stale re-runs. CI test-runner is a flat list of ~40 `./tests/test-*.sh` steps each named individually — visible step-level timing, but every new test must be registered in the workflow.

### Action-pinning conventions

Major-tag pinning (`actions/checkout@v5`, `actions/setup-node@v5`, `actions/upload-artifact@v6`, `anthropics/claude-code-action@v1`, `marocchino/sticky-pull-request-comment@v3`). No SHA pinning. State files (`.github/last-checked-version.txt`, `.github/last-checked-api-date.txt`, `.github/last-community-scan.txt`) act as persistent "where did I leave off" markers rather than build caches. No `actions/cache` step.

## Marketplace validation

### Custom in-repo validator

`tests/test-plugin.sh` (14.6 KB) is wired into `ci.yml` as the "Run plugin format tests" step. `ci.yml`'s validate job also runs an inline YAML-validity check (`python3 -c "import yaml; yaml.safe_load(...)"`) and a regex sweep for unsafe `${{ }}` interpolation patterns. CI enforces state-file existence (`last-checked-version.txt`, `last-community-scan.txt`, `last-checked-api-date.txt`) as a structural invariant, treating shepherd state as part of the repo's public contract.

### YAML safety regex sweep

Inline regex sweep against unsafe `${{ }}` interpolation patterns in workflow YAML — explicitly cited in CHANGELOG as a watch-for-regressions guard hardened from prior production breakage.

## Release automation

### Tag-triggered with sanity gates and `--generate-notes`

`release.yml` triggers on `push: tags: ['v*']`. Two sanity gates: (a) `git merge-base --is-ancestor HEAD origin/main` to assert tag is on main; (b) tag value (`${GITHUB_REF#refs/tags/v}`) must equal `package.json.version`. Failure aborts with targeted `::error::` messages. `npm publish --provenance` (sigstore via `id-token: write` permission) plus `gh release create "$TAG_NAME" --generate-notes` (release notes from PR titles since last tag, NOT from `CHANGELOG.md`). `softprops/action-gh-release` is NOT used. Gates do NOT check that tag matches `plugin.json` or `marketplace.json` versions — drift between npm and plugin metadata still possible. `fetch-depth: 0` on checkout required for the ancestry gate. Release job uses `actions/setup-node@v5` with `node-version: 22` + `registry-url: https://registry.npmjs.org` + `NODE_AUTO_TOKEN` from `NPM_TOKEN` secret. Releases publish directly (`draft: False, prerelease: False`).

## Documentation surface

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` at repo root (~11 KB): pitch + install + "What Makes This Different" + "How This Compares" + Documentation links + Community (Discord badge) + three feedback surfaces (`/feedback` skill, issue templates, discussions). `ARCHITECTURE.md` (uppercase, ~11 KB) at repo root: multi-layer diagram, hooks/skills tables, self-update flow. `CLAUDE.md` at repo root: project instructions specifically for Claude operating *on this repo*, separate from the wizard doc `CLAUDE_CODE_SDLC_WIZARD.md` which is the shipped artifact (193 KB consumed by `/update-wizard` via WebFetch).

### CHANGELOG as in-product upgrade source

`CHANGELOG.md` (~46 KB) Keep-a-Changelog-like format (`## [X.Y.Z] - YYYY-MM-DD` with `### Added`, `### Fixed`, `### Docs` sections); doubles as the source the in-product `/update-wizard` skill consumes via WebFetch and diffs against the installed version stamp.

### Sprawling root with many entry-point markdowns

~20 top-level markdown files at repo root. Beyond the standard trio plus CHANGELOG: `CONTRIBUTING.md` (7.1 KB), `AGENTS.md` (2.9 KB), `CODE_REVIEW_EXCEPTIONS.md`, `COMPETITIVE_AUDIT.md`, `ISSUES_FOUND_BY_CODEX.md`, `RESEARCH_58_CLAW_OMO_OMX.md`, `ROADMAP.md` (72 KB), `SCORE_TRENDS.md`, `SDLC.md`, `TESTING.md`, `CI_CD.md`, `AUTOCOMPACT_BENCHMARK.md`, `CODEX_ADAPTER_PLAN.md`, `CODEX_AUDIT_PROGRESS.md`. Plus `.github/ISSUE_TEMPLATE/{bug_report,feature_request,question,config}`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/FUNDING.yml`. Much is meta-project artifact (roadmap, audit, research notes); main `README.md` stays focused on the user.

### Dual-CLAUDE.md (developer + user-workspace)

`CLAUDE.md` (project instructions for contributors' Claude sessions on this repo) coexists with `CLAUDE_CODE_SDLC_WIZARD.md` (the 193 KB shipped wizard doc consumers `cat` or `WebFetch` during setup). Two CLAUDE-like files with different audiences; explicit two-hat distinction.

### Badges and status indicators

Discord "Automation Station" badge in the Community section. No CI-status or npm-version badges.

## License declaration

### LICENSE declared in manifests, no LICENSE file

Both `package.json` and `.claude-plugin/plugin.json` declare `"license": "MIT"`. No `LICENSE` file at repo root; GitHub license API returns 404; no SPDX detection by GitHub itself. npm will ship the package without a LICENSE file in the tarball unless added to `package.json.files`.

## Community health files

### Open contribution with health files

`CONTRIBUTING.md`, `AGENTS.md`, `.github/ISSUE_TEMPLATE/{bug_report,feature_request,question,config}`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/FUNDING.yml`. No `SECURITY.md`, no `CODE_OF_CONDUCT.md`, no `LICENSE` file.

## Distribution exclusion and dogfood layout

### `.claude/skills/<name>` symlinked into `skills/`

Repo-local `.claude/skills/{feedback,sdlc,setup,update}` are git symlinks (mode 120000) into the top-level `skills/` directory. Plugin form, CLI install form, and the repo's own self-use all share one source-of-truth set of SKILL.md files. The plugin's `hooks/hooks.json` references `${CLAUDE_PLUGIN_ROOT}/hooks/*.sh`; the CLI's `cli/templates/settings.json` references `"$CLAUDE_PROJECT_DIR"/.claude/hooks/*.sh` — single content, two entry forms.

## Multi-runtime portability

### Per-runtime manifest directories

Plugin form (`.claude-plugin/plugin.json` pointing at `hooks/` and `skills/` at repo root) plus the npm CLI form (`cli/init.js` copying the same `hooks/*.sh` and `skills/*/SKILL.md` into a consumer's `.claude/`) are two disjoint distribution surfaces with overlapping content; both maintained from one source. CHANGELOG references `CODEX_ADAPTER_PLAN.md` and `CODEX_AUDIT_PROGRESS.md` — Codex / OpenAI runtime is a planned third surface.

## Cross-ecosystem distribution

### Plugin + npm CLI + curl-bash with collision detection

Three install modes coexist (npm CLI, Claude plugin, manual markdown copy). `cli/init.js` explicitly detects plugin install paths (`~/.claude/plugins-local/sdlc-wizard-wrap/`, `~/.claude/plugins/cache/sdlc-wizard-local/`) and blocks with a typed error when both are present (PR #181 "dual-channel install drift guardrails"). `instructions-loaded-check.sh` also emits a non-blocking nudge when both coexist. Engineering cost of redundancy documented in CHANGELOG.

## Long-running scheduled behavior

### Outsourced to GitHub Actions cron

Three cron workflows (`weekly-update.yml`, `weekly-api-update.yml`, `monthly-research.yml`) poll external sources (Claude Code releases, Anthropic API changelog, community forums). They do cheap detection only; they open/update a single tracking GitHub issue; `instructions-loaded-check.sh` nudges the session toward those issues at next start. The API-changelog detector specifically fetches `.md` URLs (Mintlify convention) rather than scraping rendered HTML — a deliberate stability choice documented in the workflow header. Replaces what a `monitors.json` could do and extends it into durable issue tracking.

## State persistence

### State-of-watcher files in `.github/last-checked-*.txt`

Persistent shepherd state in `.github/last-checked-version.txt`, `.github/last-checked-api-date.txt`, `.github/last-community-scan.txt`. CI enforces their existence as a structural invariant.

### `${XDG_CACHE_HOME:-$HOME/.cache}/<plugin>/` for verified-version cache

`$HOME/.cache/sdlc-wizard/latest-version` (npm version cache, polled at most once per 24h with strict-semver regex validation) and `$HOME/.cache/sdlc-wizard/effort-signals.log` (rolling distress-signal log for effort-bump detection).
