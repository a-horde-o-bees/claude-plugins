# HiH-DimaN/idea-to-deploy

> **Owner redirect observed.** `github.com/HiH-DimaN/idea-to-deploy` resolves to `github.com/hihol-labs/idea-to-deploy` (the owner renamed from user `HiH-DimaN` to organisation `hihol-labs` on 2026-04-20, per the most recent commit `chore: migrate repo URLs HiH-DimaN → hihol-labs across docs and promo (#52)`). The `marketplace.json` / `plugin.json` still carry `"owner": { "name": "HiH-DimaN", ... }` and `"author": { "name": "HiH-DimaN", ... }`, and the user's install command in the README is `/plugin install hihol-labs/idea-to-deploy` (uses the new org path). Both owner paths resolve to the same repo id via GitHub's redirect — research sample captured at the canonical `hihol-labs/idea-to-deploy`. Filename retains the requested `HiH-DimaN--idea-to-deploy.md` form.

## Identification

- **URL**: https://github.com/hihol-labs/idea-to-deploy (formerly https://github.com/HiH-DimaN/idea-to-deploy; GitHub redirect active)
- **Stars**: 16 (observed 2026-04-20)
- **Last commit date**: 2026-04-20 (commit `chore: migrate repo URLs HiH-DimaN → hihol-labs across docs and promo (#52)`)
- **Default branch**: main
- **License**: MIT
- **Sample origin**: primary (community)
- **One-line purpose**: Complete project lifecycle methodology for Claude Code — 25 skills + 7 specialised subagents + 13 enforcement hooks spanning discovery, planning, scaffolding, coding, testing, security/deps audit, migration, deployment, hardening, and session persistence (per `plugin.json` description).

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (1.8 KB). No multi-plugin aggregator shape — one plugin entry, and that plugin is the same repo (`source.source: "github"`, `repo: "hihol-labs/idea-to-deploy"`).
- **Marketplace-level metadata**: no `metadata` wrapper. Top-level fields are flat: `$schema`, `name`, `description`, `owner`, `plugins[]`. Marketplace-level `description` is present (`"Complete project lifecycle methodology — 25 skills + 7 specialized subagents + 13 hooks from idea to deployed product."`).
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: `category` + `keywords` + `tags`. `category: "development"`. `keywords` array carries 16 entries (`claude-code`, `methodology`, `project-lifecycle`, `developer-tools`, `ai-coding`, `testing`, `deployment`, `code-review`, `security-audit`, `session-persistence`, `self-review`, `meta-review`, `daily-work-router`, `methodology-validation`, `product-discovery`, `safety-guardrails`). `tags: ["community-managed"]` — single-element signalling flag.
- **`$schema`**: present — `"https://anthropic.com/claude-code/marketplace.schema.json"`. Outlier — the majority of researched repos omit `$schema` on marketplace.json.
- **Reserved-name collision**: no. `idea-to-deploy` is not a Claude Code reserved plugin/skill name.
- **Pitfalls observed**:
  - **Owner-string drift after org rename** — `marketplace.json.owner.name` and every plugin `author.name` still say `HiH-DimaN`, while `source.repo` and `homepage` already point at `hihol-labs/...`. A consumer reading `owner.name` alone would be misled. No schema-level check catches the inconsistency.
  - **Non-schema `images: [url]` field** on the plugin entry (value: `https://raw.githubusercontent.com/hihol-labs/idea-to-deploy/main/docs/demo.svg`). Not documented in the Claude Code marketplace reference surveyed in `research/claude-marketplace/context-resources/docs-plugin-marketplaces.md`; permissive JSON consumers ignore it, but a strict validator would reject it. Acts as a de-facto custom "marketing asset" carrier.
  - **Custom `tags: ["community-managed"]` signal flag** used to mark the plugin as a community contribution (no authoritative schema entry seen in the context docs). Inference: `tags` here is distinct from `keywords` and carries provenance signal rather than discoverability intent.

## 2. Plugin source binding

- **Source format(s) observed**: `github` — `{ "source": "github", "repo": "hihol-labs/idea-to-deploy" }`. Single format, no aggregation.
- **`strict` field**: not present on the plugin entry (default implicit). No `skills` override or per-component carving on the marketplace entry.
- **`skills` override on marketplace entry**: absent. Plugin components are discovered from `plugin.json` pointing at `./skills/` and `./agents/`.
- **Version authority**: both `plugin.json.version` and `marketplace.json.plugins[0].version` carry `1.20.3`. Drift risk present by construction; the repo's own meta-review rubric enforces parity via check `M-C5/M-C6` and the CHANGELOG v1.20.3 lessons-learned explicitly cites an instance where pre-merge `/review` missed the drift because the bump happened after review.
- **Pitfalls observed**:
  - **Dual-location version requires explicit gate** — the project's answer to inherent drift is a machine-checked rubric, not a single-source-of-truth rearrangement; the CHANGELOG lessons-learned section documents the gate catching the drift after local review missed it.
  - **`author` vs `owner` duplication** — marketplace.json carries both `owner` (top-level) and plugin-level `author`; both are set to the same person, but the pre-rename strings in both are a second copy of the drift described under §1.

## 3. Channel distribution

- **Channel mechanism**: no split. Users consume from `main` via `/plugin install hihol-labs/idea-to-deploy`. Semver tags (`v1.20.3`, `v1.20.2`, ...) exist on `main` commits; there is no separate `stable-*` or `latest-*` marketplace.
- **Channel-pinning artifacts**: absent. No `stable-tools`/`latest-tools`-style paired manifests; no dev-counter split. Consumers who want a pinned version would do so with a `@v1.20.x` ref, not via a channel switch.
- **Pitfalls observed**:
  - `plugin.json` version follows real semver on the `main` line itself (not dev-counter), so every commit to `main` that bumps version would change the version seen by `HEAD` consumers — a release branch buffer does not exist. Release branches `release/*` do exist (see §4) but they are short-lived gates for the fixture-smoke workflow, not published channels.

## 4. Version control and release cadence

- **Default branch name**: `main`.
- **Tag placement**: on `main`. Tags observed span `v1.2.0 → v1.20.2` (20+ tags listed, including `v1.3.0`, `v1.3.1`, then a jump to `v1.13.2` with subsequent monotonic bumps — the jump reflects internal version-scheme change, not orphan commits). `v1.20.3` is the current `plugin.json` version but not yet in the API's tag list at inspection — inference: tag may not yet be pushed for the 2026-04-20 commit, or the commit is patch-prep-in-flight.
- **Release branching**: short-lived `release/*` branches exist (e.g., `feat/v1.19-phase2-3`, many `feat/v1.x.x-*` topic branches, plus `audit/*` branches). Releases are cut by creating a `release/v1.x.y` branch, running the `fixture-smoke.yml` workflow on that branch (which is otherwise disabled on main — see §13), then merging back and tagging on `main`. Pattern: PR-gated releases, not long-lived release branches.
- **Pre-release suffixes**: none observed in published tags.
- **Dev-counter scheme**: absent. All commits on `main` use real semver directly.
- **Pre-commit version bump**: no automation observed — version bumps are part of the release-prep PRs (manual discipline in CHANGELOG Ops section). The meta-review rubric (`tests/meta_review.py`) validates post-hoc that `plugin.json`, `marketplace.json`, `README.md` badge, `README.ru.md`, and `CHANGELOG.md` all agree on version — catches drift but does not prevent it.
- **Pitfalls observed**:
  - **5 version-carrying files** (plugin.json, marketplace.json, README badge, README.ru badge, per-skill `metadata.version` in any SKILL.md edited that release cycle) require simultaneous bumps. The CHANGELOG v1.20.3 Ops section explicitly enumerates all five as a manual checklist.
  - **`v1.20.3` in manifests without a matching git tag** at inspection time — either tag push lagged the commit or a patch release is in progress. A drift-sensitive validator would flag this.

## 5. Plugin-component registration

- **Reference style in plugin.json**: explicit path arrays. `plugin.json` contains:

  ```json
  "skills": ["./skills/"],
  "agents": ["./agents/"]
  ```

  No `commands`, `hooks`, `mcpServers`, `monitors` fields. Discovery is directory-based from the listed roots.
- **Components observed**:
  - skills — **yes** (25 skills in `skills/<name>/SKILL.md`, organised by category: entry points, project creation, QA, daily work, supply-chain QA, operations, workflow).
  - commands — **no** (skills act as the command surface via the `Skill` tool).
  - agents — **yes** (7 in `agents/*.md`: architect, business-analyst, code-reviewer, devils-advocate, doc-writer, perf-analyzer, test-generator).
  - hooks — **yes** but **not registered via plugin.json**. Shell/Python scripts live in `hooks/*.sh` (13 files). Registration is by out-of-band mechanism — either `scripts/sync-to-active.sh` patches the user's `~/.claude/settings.json`, or `/adopt` writes `$PROJECT_ROOT/.claude/settings.json` from `skills/adopt/references/project-settings-template.json`. See §9 and §17.
  - .mcp.json — **no**.
  - .lsp.json — **no**.
  - monitors — **no** (no `monitors.json`).
  - bin — **no**.
  - output-styles — **no**.
- **Agent frontmatter fields used**: `name`, `description`, `model` (`opus` or `sonnet`), `effort` (`high`), `maxTurns` (integer — 15 or 20 observed), `allowed-tools`. No `skills`, `memory`, `background`, `isolation`, or `tools` in the sense of object-form permission rules. Example (devils-advocate): `model: opus`, `effort: high`, `maxTurns: 15`, `allowed-tools: Read Grep Glob`.
- **Agent tools syntax**: plain tool names separated by spaces (`Read Grep Glob`) — NOT permission-rule syntax. All 7 agents are read-only by design (no `Write`/`Edit` in their `allowed-tools`); agents return structured markdown that the caller skill writes.
- **Skill frontmatter fields**: `name`, `description`, `argument-hint`, `allowed-tools`, `license`, `metadata.{author, version, category, tags}`. Some skills carry `disable-model-invocation: true` (observed on `/autopilot`, `/deploy`, `/migrate`, `/migrate-prod` — explicit-invoke-only for high-blast-radius operations, per CHANGELOG v1.20.1). One skill (`/autopilot`) carries `context: fork` — inferred meaning: subagent-like forked-context invocation.
- **Skill `allowed-tools` syntax**: mixed — plain tool names (`Read Write Edit Glob Grep`) AND permission-rule syntax (`Bash(git:*) Bash(npm:*) Bash(pnpm:*) Bash(docker:*) Bash(pytest:*) Bash(go:*) Bash(cargo:*)` observed in `/kickstart`; `Bash(ssh:*) Bash(scp:*) Bash(rsync:*) Bash(docker:*) Bash(pg_dump:*) Bash(dig:*) Bash(curl:*)` in `/migrate-prod`). Same file can mix both forms.
- **Pitfalls observed**:
  - **Hooks are plugin-functional but not plugin-declared** — the 13 shell scripts under `hooks/` are first-class enforcement, but `plugin.json` has no `hooks` field. This splits the contract: `/plugin install` gives you skills + agents, but the hook layer requires a manual `bash scripts/sync-to-active.sh` or `/adopt` run (see §9). CHANGELOG v1.20.1 documents a regression (`check-review-before-commit.sh` existed in the repo but was never added to `DESIRED_HOOKS` in sync-to-active.sh, so users following the README got 12/13 hooks) — the gap was closed by adding a second drift verifier script `scripts/verify-sync-to-active.sh` run in CI.
  - **Template token `{{PLUGIN_HOOKS_DIR}}` in the /adopt settings template** resolves to `~/.claude/plugins/idea-to-deploy/hooks` (post-install path) with legacy fallback to `~/.claude/hooks` (sync-to-active.sh path). Two coexisting install roots imply the user has to know which path is active.

## 6. Dependency installation

- **Applicable**: no. The plugin ships as markdown skills/agents + shell-or-Python hook scripts with **zero runtime dependencies** — all Python tooling uses Python 3.11 stdlib only (explicit design choice documented in `docs/CI.md`: "both scripts are intentionally zero-dependency").
- **Dep manifest format**: none.
- **Install location**: not applicable — nothing is installed at runtime. Claude Code's own `/plugin install` copies the repo into `~/.claude/plugins/idea-to-deploy/`; no `SessionStart` hook runs pip/uv/npm/bun.
- **Install script location**: not applicable (no package-installation script). The `scripts/sync-to-active.sh` script is a sync-to-`~/.claude/` copy utility, not a dep installer.
- **Change detection**: not applicable for deps. For the sync utility: `diff -rq` for skills (content compare), `cmp -s` for hooks/agents (byte-exact compare) — this is the change-detection style used for the skill/hook mirror, not for dep install.
- **Retry-next-session invariant**: not applicable.
- **Failure signaling**: not applicable.
- **Runtime variant**: not applicable (pure markdown + stdlib Python + bash).
- **Alternative approaches**: not applicable.
- **Version-mismatch handling**: not applicable.
- **Pitfalls observed**:
  - The README lists **Requirements** as Python 3 (for hooks) + Bash (for scripts) + `claude` CLI v2.1+ (for the headless fixture runner). These are assumed available on the host — there is no `SessionStart` verification (compare to this project's marketplace which verifies `uv` at runtime).

## 7. Bin-wrapped CLI distribution

- **Applicable**: no (no `bin/` directory). The plugin has no user-facing CLI shipped with it.
- **`bin/` files**: none.
- **Shebang convention**: not applicable for bin. For hooks: Python hooks use `#!/usr/bin/env python3`; shell hooks use `#!/usr/bin/env bash` (observed in `run-fixture-headless.sh`, `sync-to-active.sh`).
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: not applicable (no venv — Python stdlib only).
- **Platform support**: not applicable for bin.
- **Permissions**: not applicable for bin. Hook scripts become executable at sync time via `chmod +x "$dst"` in `sync-to-active.sh`.
- **SessionStart relationship**: not applicable.
- **Pitfalls observed**:
  - Not applicable — no bin.

## 8. User configuration

- **`userConfig` present**: no. Neither `marketplace.json` nor `plugin.json` declares `userConfig`.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable (no `userConfig`).
- **Schema richness**: not applicable.
- **Reference in config substitution**: no `${user_config.KEY}` observed. The plugin has no tunable parameters — methodology behaviour is fixed. The only "secret" in the ecosystem is `ANTHROPIC_API_KEY` for the headless fixture-smoke CI job, and that is provisioned as a GitHub Actions repository secret (not a user config field).
- **Pitfalls observed**:
  - Not applicable — no user config surface.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 4 hooks registered across 3 matcher groups, per `skills/adopt/references/project-settings-template.json`:
  1. matcher `Bash|Edit|Write|NotebookEdit` → `check-tool-skill.sh` (reminds Claude to route via a skill before ad-hoc tool use; rate-limited; escalates to blocking after 3 consecutive ignores per `hooks/README.md`).
  2. matcher `Bash` → `check-commit-completeness.sh` (blocks `git commit` when staged SKILL.md lacks referenced `references/`, triggers, or fixtures).
  3. matcher `Bash` → `check-review-before-commit.sh` (requires `/review` invocation before commits touching >2 files).
  4. matcher `Write|Edit|MultiEdit` → `check-skill-completeness.sh` (blocks writes to skills/<name>/SKILL.md when completeness invariants fail).
  
  Opt-in (not in `DESIRED_HOOKS`, not auto-synced): `careful.sh` (destructive-command warner for `rm -rf`/`DROP TABLE`/`git push --force`), `freeze.sh` (scope-restriction gate), `context-aware.sh`, `cost-tracker.sh`, `crash-recovery.sh`, `stuck-detection.sh`.
- **PostToolUse hooks**: none. CHANGELOG v1.20.3 explicitly defers `PostToolUse` test-first enforcement ("Test-first enforcement hook — a `PostToolUse` hook that would warn when `/bugfix` edits code without a preceding new test. Rejected per ROADMAP_v1.21 criteria — n=0 signal, solo-maintainer surface cost").
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: all hooks read JSON on stdin, write `hookSpecificOutput.additionalContext` JSON on stdout (observed in `check-skills.sh` module docstring). Hooks are silent (exit 0, no output) when no triggers match — keeps normal turns noise-free.
- **Failure posture**: soft-first-then-escalating. Most hooks fail-open (soft reminders injected as additionalContext); the four in `DESIRED_HOOKS` are documented in `hooks/README.md` as "Hard Enforcement (Blocking)" for commit-completeness and skill-completeness checks. Specific escalation: `check-tool-skill.sh` is soft for the first 3 ignores, then blocks.
- **Top-level try/catch wrapping**: not explicitly verified in the snippets read, but `check-skills.sh` docstring says "Silent (exit 0, no output) if no triggers match" — suggests hooks are written to not crash on malformed input, though the exact guard discipline wasn't confirmed for all 13 scripts within budget.
- **Pitfalls observed**:
  - **Override backdoor** — `hooks/README.md` documents a `.methodology-self-extend-override` file that bypasses hard enforcement. Mentioned in the defense-in-depth table in `docs/CI.md` as "Only via documented `.methodology-self-extend-override` file".
  - **Repo-scope lock** — hooks detect `.claude-plugin/plugin.json` at repo root and restrict enforcement to methodology repositories only; running Claude in an unrelated repo sees no blocking behaviour. Prevents the plugin's hooks from interfering with unrelated projects but also means the hooks never fire outside the plugin's own context unless `/adopt` has written a project `.claude/settings.json`.

## 10. Session context loading

- **SessionStart used for context**: no. No `SessionStart` hook event registered.
- **UserPromptSubmit for context**: yes. Three hooks fire on every `UserPromptSubmit`:
  1. `session-open-diagnostic.sh` (first-turn diagnostics).
  2. `pre-flight-check.sh` (injects recent git history, active-session lockfiles, memory-index state — per script docstring).
  3. `check-skills.sh` (regex-scans the prompt, emits routing reminders for matched triggers).
- **`hookSpecificOutput.additionalContext` observed**: yes — explicit in `check-skills.sh` docstring.
- **SessionStart matcher**: not applicable (no SessionStart hook).
- **Pitfalls observed**:
  - **UserPromptSubmit-only strategy** — context is injected per-turn rather than once per session. For plugins adopting this pattern, per-turn cost (both token cost and latency) is the trade-off versus the simplicity of not having to manage per-session state.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable (no monitors).
- **Pitfalls observed**:
  - Not applicable.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — single-plugin marketplace, no cross-plugin coupling.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin repo). Tags use plain `v1.x.y` form.
- **Pitfalls observed**:
  - Not applicable.

## 13. Testing and CI

- **Test framework**: zero-dependency Python 3.11 stdlib scripts (`tests/meta_review.py`, `tests/verify_snapshot.py`, `tests/verify_triggers.py`) plus bash fixture-runner (`tests/run-fixtures.sh`, `tests/run-fixture-headless.sh`). No pytest, unittest, jest, etc. — the test model is "structural-rubric + golden snapshots", not code unit tests.
- **Tests location**: `tests/` at repo root. 17 fixture directories under `tests/fixtures/fixture-NN-<name>/` (each with `idea.md`, `notes.md`, `expected-files.txt`, `expected-snapshot.json`; 3 have `stream.jsonl` — these are the active fixtures 01/02/03, the rest are `status: pending` stubs).
- **Pytest config location**: not applicable (no pytest).
- **Python dep manifest for tests**: none (stdlib-only is an explicit design choice — see `docs/CI.md`).
- **CI present**: yes.
- **CI file(s)**: `.github/workflows/meta-review.yml`, `.github/workflows/fixture-smoke.yml`.
- **CI triggers**:
  - `meta-review.yml`: `push: branches: [main]` + `pull_request: branches: [main]`.
  - `fixture-smoke.yml`: `push: branches: ['release/*']` + `workflow_dispatch` (with `fixtures`, `model`, `budget` inputs). **Job-level `if: false` guard** disables automatic execution until a maintainer both provisions `ANTHROPIC_API_KEY` and removes the guard. Header comment: "v1.16.0 initial state — skeleton only, not yet activated."
- **CI does**:
  - `meta-review.yml` runs 3 steps: `python3 tests/meta_review.py --verbose`, `python3 tests/verify_triggers.py`, `bash scripts/verify-sync-to-active.sh`. Three-layer meta-rubric: version-badge parity, skill-count parity, SKILL.md frontmatter validity, marketplace.json consistency, subagent-contract disclaimers, trigger-phrase drift (between `skills/*/SKILL.md ## Trigger phrases` and `hooks/check-skills.sh` regex tables), fixture-snapshot schemas, hook-sync drift (no canonical hook added without being registered).
  - `fixture-smoke.yml` (when enabled) runs the `claude -p` CLI in non-interactive stream-json mode against 3 active fixtures, enforces per-fixture USD budget via `--max-budget-usd` (fixture-01: $10, fixture-02: $5, fixture-03: $5; total ~$8–$12 per release), validates output with `verify_snapshot.py`, uploads outputs as 14-day artifacts.
- **Matrix**: none. Single Ubuntu runner, single Python (3.11).
- **Action pinning**: tag (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`). No SHA pinning.
- **Caching**: none declared (stdlib-only Python removes the motivation).
- **Test runner invocation**: direct `python3 tests/<script>.py` (not wrapped in `scripts/test.sh` or `uv run`). Fixture-smoke uses `bash tests/run-fixture-headless.sh <fixture> --model <m> --budget <b>` wrapper.
- **Pitfalls observed**:
  - **Disabled-by-default expensive workflow** — `fixture-smoke.yml` is fully committed but gated by `if: false` AND absence of `ANTHROPIC_API_KEY`. The stated cost (~$8–$12/release) justified the skeleton-and-guard pattern. This is a novel "ship-the-workflow-but-don't-spend" distribution strategy — see §17.
  - **Branch-protection blocking requires manual UI setup** — `docs/CI.md` has a 7-step walkthrough for enabling the `meta-review` status check as a required check on `main` ("this cannot be provisioned from code").
  - **CI trigger for adding CI in the first place** — CHANGELOG v1.8.0 documents that CI was added specifically because the repo got "3 GitHub stars within 24h of publishing", flipping the "wait for first PR" cost/benefit.
  - **Zero-dep Python as CI design axiom** — stated rationale: fast runs (<30 s), removes supply-chain risk from CI itself, makes meta-review runnable locally without setup. `docs/CI.md` treats this as a first-class design constraint.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no. Releases are created via the GitHub UI (20 releases observed, all non-draft, titled `v1.x.y — <summary>`). No `softprops/action-gh-release`, no `release-please`, no `semantic-release`.
- **Release trigger**: not applicable (manual).
- **Automation shape**: not applicable.
- **Tag-sanity gates**: not applicable (manual tag creation). The meta-review rubric validates version-string parity as a commit-time/CI gate but does not gate tag creation itself.
- **Release creation mechanism**: manual (`gh release create` or GitHub UI — not committed automation).
- **Draft releases**: no (all 20 observed releases are `draft=False`).
- **CHANGELOG parsing**: not applicable (no automation parses it). CHANGELOG.md is Keep a Changelog 1.1.0 format with rich per-release sections (`Added`, `Changed`, `Fixed`, `Ops`, `Context`, `Rationale`, `Lessons learned`, `Deliberately not done (deferred)`).
- **Pitfalls observed**:
  - **Full release automation deferred** — `fixture-smoke.yml` is the release-gate skeleton (runs only on `release/*` branches); actually cutting a release from the passing branch is manual. When `ANTHROPIC_API_KEY` eventually lands, the `release/*` branch → smoke-passes → manual merge + manual tag pattern will become the cadence — still not `release:[published]`-triggered automation.
  - **CHANGELOG Ops sections** manually enumerate every version-bumped file per release (5+ files), acting as a self-imposed checklist rather than machine-driven single-source-of-truth.

## 15. Marketplace validation

- **Validation workflow present**: yes — **but the validator targets methodology invariants rather than the marketplace schema specifically**. `meta-review.yml`'s `tests/meta_review.py` validates:
  - Version parity across `plugin.json`, `marketplace.json`, README badges.
  - Skill-count parity (25 skills).
  - SKILL.md frontmatter fields (`name`, `description`, `license`, `allowed-tools`, `metadata.version`).
  - `marketplace.json` internal consistency.
  - Trigger-phrase drift between each skill's `## Trigger phrases` section and the regex table in `hooks/check-skills.sh` (via `tests/verify_triggers.py`, enforced as gate M-C11).
  - Fixture snapshot schema validity.
  - Sync-to-active hook registration drift (via `scripts/verify-sync-to-active.sh`).
- **Validator**: Python+stdlib (custom). Not bun+zod, not `claude plugin validate`, not a pre-commit hook.
- **Trigger**: `push` to main, `pull_request` to main (same as §13).
- **Frontmatter validation**: yes — SKILL.md frontmatter fields are explicitly checked.
- **Hooks.json validation**: not applicable (plugin has no `hooks` field in plugin.json; hook registration lives in external `settings.json` templates).
- **Pitfalls observed**:
  - **Validator exists but marketplace-schema validity is not its primary concern** — the validator is methodology-focused. External `$schema`-based validation (via the `https://anthropic.com/claude-code/marketplace.schema.json` reference present in marketplace.json) is not wired into CI; the schema link is declarative only.

## 16. Documentation

- **`README.md` at repo root**: present (substantial — 24 top-level headings: Problem, Solution, Quick Start, How It Works, End-to-End Example, Skills (7 categories), Subagents, Skill Contracts, Call Graph, Recommended Setup, Quality Gates, What Gets Generated, Seamless Route Switching, Recommended Models, Who Is This For, Project Types, What This Does NOT Do, Troubleshooting/FAQ, Contributing, Requirements, Changelog, License, Author). Also `README.ru.md` — full Russian translation.
- **Owner profile README at `github.com/HiH-DimaN/HiH-DimaN`**: present (~90 lines, marketing collateral — services menu, product prices, in Russian)
- **`README.md` per plugin**: not applicable (single-plugin repo; per-plugin README would be per-skill, which is not the convention).
- **`CHANGELOG.md`**: present — Keep a Changelog 1.1.0 format with per-release `Added`/`Fixed`/`Changed`/`Ops`/`Context`/`Rationale`/`Lessons learned`/`Deliberately not done` sections. Unusual depth: entries include external-source attribution (e.g., v1.20.3 cites Karpathy analysis).
- **`architecture.md`**: absent. Architecture content lives inline in README (Call Graph, Skill Contracts, How It Works sections) — not separated.
- **`CLAUDE.md`**: absent at repo root. A CLAUDE.md template is shipped inside `/adopt` at `skills/adopt/references/claude-md-template.md` — that template is what `/adopt` writes into a legacy project's root when it onboards the methodology. The methodology repo itself does not carry a CLAUDE.md.
- **Community health files**: `CONTRIBUTING.md` present (extensive — includes meta-review gate, `## Trigger phrases` canonicity rule, three-file requirement for new skills: SKILL.md + references/ + fixture). `.github/ISSUE_TEMPLATE/bug_report.md` and `feature_request.md` present. No `SECURITY.md`, no `CODE_OF_CONDUCT.md`.
- **LICENSE**: present (MIT).
- **Badges / status indicators**: observed — License, Skills count (25), Agents count (7), Version (1.20.3), meta-review CI badge (live workflow status), Status (Stable), Type (Claude Code Plugin). README.md also links to Russian README and to Changelog/Contributing/CI docs.
- **Supplementary docs**: `docs/CI.md` (CI design + branch-protection walkthrough), `docs/CONTENT-PLAN.md`, `docs/competitive-analysis.md` (compares methodology to other repos — this is where external-ecosystem analysis is captured, informing CHANGELOG rationale), `docs/cast-to-svg.js` + `docs/demo.cast` + `docs/demo.svg` (asciinema demo pipeline), `docs/promotion/drafts/*` (HN, devto, habr, reddit, twitter promo drafts). Three roadmap files: `ROADMAP_v1.19.md`, `ROADMAP_v1.20.md`, `ROADMAP_v1.21.md`.
- **Pitfalls observed**:
  - **Roadmaps-as-artifacts** — ROADMAP_v1.xx.md files accumulate (one per planned minor version); no pruning convention observed beyond what's implicit in the release cycle.
  - **Promotion drafts live in the repo** — `docs/promotion/drafts/` contains marketing copy for six channels; the CHANGELOG v1.20.2 entry calls out "content correctness in promo drafts" and "demonstrative-bug quoting patterns" as a validator concern, meaning the meta-rubric also scans promo drafts for drift (stale version/count references). Promo content being in-tree has the side effect of requiring doc-drift validation over it.

## 17. Novel axes

Observed design choices that do not fit cleanly into purposes 1–16:

- **Disabled-by-default committed CI workflow.** `fixture-smoke.yml` is fully written and committed but gated by both `if: false` AND absence of `ANTHROPIC_API_KEY`. Header comment explicitly frames it as a "ready-to-enable skeleton so the methodology has a complete v1.16.0 story on disk, but it does NOT run automatically." This is a distribution pattern: ship the infrastructure, do not pay the cost, let the maintainer flip it when ready. Candidate pattern-doc axis: "infrastructure-as-code with explicit cost gate" — ship the workflow but include a hard structural disable that requires two-hand activation (secret provision + guard removal).
- **`claude -p` in CI as release gate.** The fixture-smoke runner invokes the Claude Code CLI itself in non-interactive `--input-format stream-json --output-format stream-json --no-session-persistence --dangerously-skip-permissions --max-budget-usd <N>` mode, feeding a pre-seeded `stream.jsonl` of user turns and validating output against `expected-snapshot.json`. Per-fixture USD budget cap is enforced by the CLI's own `--max-budget-usd`. This is a novel "golden snapshot via headless Claude" testing axis: treat the plugin's output under fixed model + fixed prompt stream as a snapshot that must match. Cost profile documented in-tree (fixture-01: $5–$8, fixture-02: $1.50–$2, fixture-03: $1–$1.50 on Sonnet; Opus multipliers 4x).
- **Trigger-phrase drift detector as CI gate.** `tests/verify_triggers.py` cross-checks every `## Trigger phrases` list in `skills/*/SKILL.md` against the regex patterns in `hooks/check-skills.sh`. This treats the regex-driven skill router as a derived artifact of the SKILL.md bodies and enforces authoritative direction (SKILL.md is source of truth per `CONTRIBUTING.md`). Candidate axis: "derived-artifact drift gate" — when one file auto-completes from another by hand, add a validator that fails CI on the drift.
- **Sync-to-active drift guard.** `scripts/verify-sync-to-active.sh` cross-checks every `hooks/*.sh` against a `DESIRED_HOOKS` allowlist in `sync-to-active.sh`, with an explicit `EXEMPT` list for opt-in-only hooks. Added in v1.20.1 after a hook (`check-review-before-commit.sh`) shipped to the repo but never landed in the sync script — users following the README got 12/13 hooks for two minor versions. Pattern: validate the registration list against the filesystem inventory, with a documented exempt list for files that should NOT be registered.
- **Methodology meta-gates named like git commit check IDs** — `M-C1` … `M-C16` (Critical) and `M-I1` … `M-I9` (Important) are stable IDs for individual checks in `tests/meta_review.py`. CHANGELOG entries reference these IDs across releases ("M-C12 regex now catches Markdown-bold counts", "CI Gate 1 caught the drift correctly confirming the gate's value"). Candidate axis: "CI check as first-class named entity" — giving each structural rubric check a stable ID turns CI output into a navigable contract.
- **`disable-model-invocation: true` for high-blast-radius skills.** Applied to `/deploy`, `/migrate`, `/migrate-prod`, `/autopilot`. Semantics (inferred from CHANGELOG v1.20.1): the skill won't be auto-invoked via embedding-match on vaguely similar prompts; users must call it by name, or a router skill must explicitly delegate to it. Candidate axis: "opt-out auto-routing for destructive operations" as a skill-frontmatter convention.
- **`context: fork` on a skill.** Present on `/autopilot`. Inferred meaning: subagent-like forked-context invocation for the auto-pipeline. Not in the frontmatter surfaces of researched context docs surveyed — could be a custom extension or an undocumented Claude Code feature.
- **Custom `tags: ["community-managed"]` provenance flag.** Separate from discoverability-oriented `keywords`. Marks the plugin as community-contributed. Candidate axis: "provenance-signalling tags distinct from search-keyword tags" as a marketplace convention.
- **Non-schema `images: [url]` on a marketplace plugin entry.** Carries a README-referenced `docs/demo.svg` URL as structured metadata. Candidate axis: "marketing-asset metadata on marketplace entries" — permissive consumers ignore; strict consumers reject; useful for consumer UIs that want a hero image.
- **`$schema` declaration on marketplace.json.** URL `https://anthropic.com/claude-code/marketplace.schema.json`. Declarative only — no CI step validates against this schema — but enables IDE-level validation for anyone editing the file. Outlier in the population sampled.
- **Repo-scope hook self-restriction.** Hooks `cd` to cwd and detect `.claude-plugin/plugin.json`; if absent, they exit silently. Prevents the plugin's enforcement from interfering with unrelated user projects. Candidate axis: "in-repo self-scoping hooks" — a hook installed at the user level that gates its own activation on a repo-root sentinel file.
- **Dual hook-install paths coexisting** — `sync-to-active.sh` installs into `~/.claude/hooks/` (legacy); `/plugin install` installs into `~/.claude/plugins/idea-to-deploy/hooks/`. The `/adopt` template uses `{{PLUGIN_HOOKS_DIR}}` as a substitution token that is replaced at adopt time with whichever path is active. Candidate axis: "migration-tolerant hook-path resolution via template substitution."
- **`.methodology-self-extend-override` bypass file** — a documented escape hatch for hard enforcement, not a hidden one. Users who legitimately need to bypass a blocking hook (e.g., extending the methodology itself, where the hook's invariant doesn't apply) create this file. Candidate axis: "documented bypass mechanism" — invariant of the hook is not "always block" but "block unless escape hatch is explicitly present."
- **CHANGELOG "Deliberately not done" sections** — every release explicitly enumerates deferred work with rationale (e.g., v1.20.3: "Test-first enforcement hook — rejected per ROADMAP_v1.21 criteria (n=0 signal, solo-maintainer surface cost)"). Captures negative-space decisions as first-class changelog entries. Candidate axis: "changelog negative-space" — deferral decisions are release artifacts, not hidden in commit history.
- **CHANGELOG "Lessons learned (meta-review gap)" sections** — post-mortem of which gate caught what the author missed, feeding back into rubric improvements. Connects CI output to documentation in a tight loop.
- **Owner-rename observed in-flight.** Most recent commit (2026-04-20) migrates repo URLs from `HiH-DimaN` to `hihol-labs`, but `marketplace.json.owner.name` and plugin `author.name` still say `HiH-DimaN`. This is either intentional (person remains author even after org takeover) or a drift the meta-rubric doesn't check. Candidate axis: "owner-identity drift" as a rename-migration pitfall — consumers reading `owner.name` get the pre-rename identity.
- **Bilingual methodology** — Russian + English trigger phrases in every skill's `## Trigger phrases` section and in every `check-skills.sh` regex. SKILL.md descriptions also bilingual (code-reviewer agent description explicitly lists Russian trigger phrases: `'проверь код', 'code review', 'ревью', 'проверь PR', 'найди косяки'`). Candidate axis: "multilingual trigger surface" — a plugin serving two linguistic populations needs regex/trigger discipline per language.

## 18. Gaps

Items that could not be fully resolved within the WebFetch + `gh api` budget:

- **`tests/meta_review.py` full gate list** — only the first 30 lines of the script were read. The complete M-C1..M-C16 + M-I1..M-I9 rubric would require reading the full file (~500+ lines inferred from the content depth) or the `skills/review/references/meta-review-checklist.md` it implements.
- **Hook script bodies beyond `check-skills.sh` head** — individual Python logic for the 12 other hooks (escalation counter in `check-tool-skill.sh`, skill-completeness invariants in `check-skill-completeness.sh`, exact rules for `careful.sh` and `freeze.sh`) would each require a separate fetch. Would resolve: exact failure posture per hook, exact stderr/stdout conventions, whether try/catch wrapping is present.
- **`stream.jsonl` format for fixture-smoke** — referenced but not read; the precise format of pre-seeded clarifications (`{"type":"user","message":{"role":"user","content":"..."}}`) and whether tool-use turns can be pre-seeded would clarify the scope of the headless-testing pattern.
- **`disable-model-invocation: true` semantics** — inferred from CHANGELOG v1.20.1, not verified against authoritative Claude Code docs. Would resolve: whether this is a documented frontmatter field or an undocumented extension.
- **`context: fork` on `/autopilot`** — observed, semantics inferred. Not cross-checked against the researched Claude Code context docs. Would resolve: whether this is a documented Claude Code skill frontmatter field or a methodology-specific custom field that Claude Code ignores.
- **`plugin.json` carries `skills: ["./skills/"]` and `agents: ["./agents/"]`** — whether Claude Code discovers the full `skills/<name>/SKILL.md` tree from a trailing-slash directory glob, or whether each skill must be listed individually, was not cross-verified against the docs. Observed behaviour: the plugin ships this shape and claims 25 skills registered, so discovery must work from the directory root, but whether this is the preferred form or a shortcut was not determined.
- **Whether `images:` field is actually consumed by any UI** — observed in marketplace.json, but the downstream consumer (web marketplace UI, CLI `/plugin list`, other) was not identified.
- **Owner-rename provenance** — the commit message documents the rename but not the reason (personal-to-org migration? organization takeover? rebranding?). Would resolve the drift analysis under §1/§2.
- **Tag `v1.20.3` push state** — API listed tags up to `v1.20.2`; `plugin.json` and CHANGELOG reference `1.20.3` dated 2026-04-18. Whether the tag is unpushed, whether 1.20.3 is mid-release, or whether the tag list endpoint truncated was not verified with a dedicated `gh api repos/.../git/refs/tags/v1.20.3` call.
- **`fixture-smoke.yml` actual activation state** — `if: false` is committed; whether a maintainer has locally flipped it in a branch or whether `ANTHROPIC_API_KEY` is provisioned (which would make removing `if: false` sufficient to activate) is not visible from the public API.
- **Full `scripts/sync-to-active.sh` Step 4/4 (settings.json patch logic)** — only head + middle read; the exact JSON-merge strategy (jq? Python? `cat > settings.json`?) and how it preserves user-defined `env`/`permissions`/`statusLine`/`model` was not fully captured. The comment block claims non-hooks keys are preserved; mechanism not verified.
