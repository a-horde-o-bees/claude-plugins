# ShaheerKhawaja/ProductionOS

## Identification

- **URL**: https://github.com/ShaheerKhawaja/ProductionOS
- **Stars**: 6
- **Last commit date**: 2026-04-16 (sha 30396875, "feat: ProductionOS v2.0.0-beta.1 — universal Claude Code harness (#115)")
- **Default branch**: main
- **License**: MIT
- **Sample origin**: bin-wrapper
- **One-line purpose**: Dual-target AI engineering OS for Claude Code and Codex — 80 agents, 41 commands, 51 skills, 15 hooks; deploys specialized agents that review, score, and improve an entire codebase with smart routing, recursive convergence, and self-evaluation.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root; single-plugin marketplace that also happens to be the plugin (plugin sits at repo root via `source: "./"`).
- **Marketplace-level metadata**: `metadata.{description, version, homepage, repository, license}` wrapper; no `pluginRoot` field.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: category + tags + keywords — all three present. `category: "workflow"`, eight `keywords` (`productionos`, `production-upgrade`, `omni-plan`, `auto-swarm`, `code-review`, `security-audit`, `codex`, `claude-code`), six `tags` (`productionos`, `claude-code-plugin`, `codex-plugin`, `multi-agent`, `recursive-improvement`, `self-evaluation`).
- **`$schema`**: absent.
- **Reserved-name collision**: no.
- **Pitfalls observed**: `owner` is declared at the marketplace top level (outside `metadata`), which matches the marketplaces reference but duplicates author info already supplied under each plugin — a minor redundancy risk if edited in one place and not the other.

## 2. Plugin source binding

- **Source format(s) observed**: relative — single entry `"source": "./"` (plugin is the repo root).
- **`strict` field**: `false` explicit.
- **`skills` override on marketplace entry**: absent. The relaxed `strict: false` is declared but no narrowing override is used to carve a subset — the marketplace simply permits components beyond the canonical roots (e.g., root-level `CLAUDE.md`, `SKILL.md`, `SKILL_REGISTRY.md`, custom `prompts/`, `algorithms/`, `templates/`, `codex-overrides/`, `codex-skills/`).
- **Version authority**: both. `VERSION` file (`2.0.0-beta.1`) is the authoritative source read at runtime by `bin/install.cjs`, `bin/pos-init`, `bin/pos-update-check`, and `hooks/session-start.sh`; `plugin.json`, `.claude-plugin/marketplace.json`, `package.json`, and `.codex-plugin/plugin.json` all hardcode the same string separately — four copies to keep in sync plus the VERSION file (five points of drift).
- **Pitfalls observed**: `strict: false` is set but no explicit `skills`/`commands`/`agents` override appears on the marketplace entry to narrow what gets discovered — the plugin relies entirely on `plugin.json`'s explicit `agents` array (80 paths) plus `skills`/`commands` directory references. Fallback `1.2.0-beta.1` is hardcoded inside `hooks/session-start.sh` when VERSION cannot be read, which would mislabel a broken install. CHANGELOG top entry is `8.0.0-alpha.2` (2026-03-22), inconsistent with every other authoritative version source at `2.0.0-beta.1` — indicates an in-flight rebrand/renumber where the CHANGELOG was not reset.

## 3. Channel distribution

- **Channel mechanism**: no split — single marketplace, users pin via commit ref (no tags exist; `@ref` on the install URL is the only lever).
- **Channel-pinning artifacts**: absent. No `stable-*`/`latest-*` split, no release-branch split.
- **Pitfalls observed**: the repo has zero git tags and zero GitHub releases despite shipping a `2.0.0-beta.1` marker — users installing via `claude plugin marketplace add ShaheerKhawaja/ProductionOS` track whatever is on `main` at install time, with no pin mechanism other than a raw commit SHA. Combined with `npx productionos@latest`, the npm registry is the de facto versioning substrate rather than git tags.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: none — no tags exist on the repo.
- **Release branching**: none. Long-lived `feat/*` branches exist (30+ visible — `feat/v2.1-autonomous-pipeline`, `feat/v5.1-production-ready`, `feat/v7-audit-fixes-research`, `feat/v8-sprint1-guardrails-retro`, `feat/v8-sprint5-worktree-isolation`, etc.) but these are WIP/feature branches merged back into main, not release branches.
- **Pre-release suffixes**: `-beta.1` in use (`2.0.0-beta.1`). CHANGELOG also references `-alpha.2` for prior version.
- **Dev-counter scheme**: absent.
- **Pre-commit version bump**: no. Version is manually edited across VERSION file + 4 JSON manifests + CHANGELOG at each release (PR #115 commit message includes "fix(tests): update hardcoded version expectations to 2.0.0-beta.1" and "fix(cli): pos-init reads version from VERSION file instead of hardcoding" — indicating a recent partial move toward VERSION-file authority without yet centralizing all references).
- **Pitfalls observed**: no tags, no releases, and multiple long-lived feature branches (`v2.1`, `v3`, `v5.1`, `v5.3`, `v7`, `v8`) represent parallel-timeline development that the current `2.0.0-beta.1` semver cannot reconcile — the CHANGELOG already lists `[8.0.0-alpha.2]` as the latest entry. The observed "rebrand from productupgrade → ProductionOS" that PR #115 completed is the likely cause: version numbering was reset to 2.x for the new product line while branches carrying 7.x/8.x work remain open.

## 5. Plugin-component registration

- **Reference style in plugin.json**: explicit path arrays for agents (80 relative paths, one per file); directory references for commands (`"./.claude/commands/"`) and skills (`"./.claude/skills/"`); no `hooks` field in `plugin.json` — hooks live in a top-level `hooks/hooks.json` discovered by convention.
- **Components observed**: skills yes (`.claude/skills/` with 4 entries plus a separate `skills/` top-level dir and `codex-skills/` dir), commands yes (41 files in `.claude/commands/`), agents yes (80 files in `agents/`, plus 81st possible — `gh api` returned length 81 vs the 80 enumerated in plugin.json; one unreferenced file exists), hooks yes (18 shell/python scripts in `hooks/` referenced by `hooks/hooks.json`), `.mcp.json` no, `.lsp.json` no, monitors no, bin yes (11 shell scripts + 1 Node installer in `bin/`), output-styles no.
- **Agent frontmatter fields used**: `name`, `description`, `color` (optional), `model` (sonnet/haiku observed), `tools` (Read, Glob, Grep, etc.), `subagent_type` (e.g., `productionos:code-reviewer`), `stakes` (low/medium/high — custom field borrowed from HumanLayer).
- **Agent tools syntax**: plain tool names (`Read`, `Glob`, `Grep`) — no permission-rule syntax like `Bash(uv run *)` observed.
- **Pitfalls observed**: mismatch between plugin.json's explicit 80-path agents array and the filesystem count of 81 — one agent file is present but unreferenced. Custom `subagent_type` namespace (`productionos:<name>`) and `stakes` field are non-standard Claude Code agent frontmatter; they rely on plugin-internal readers rather than the harness. The dual locations for skills (`.claude/skills/` and top-level `skills/` and `codex-skills/`) indicate Codex-parity shipping of the same skill content under multiple paths — a source of drift unless `scripts/gen-targets.ts` is run to regenerate.

## 6. Dependency installation

- **Applicable**: yes.
- **Dep manifest format**: `package.json` + `bun.lock` (Bun/Node runtime for scripts, Ink TUI, TypeScript build); no `requirements.txt` / `pyproject.toml` — Python is used ad-hoc via `python3 -c "..."` in bash hooks, relying on system Python.
- **Install location**: `bun install` writes to `node_modules/` inside the plugin root (`${CLAUDE_PLUGIN_ROOT}/node_modules/`); no Python venv; `${PRODUCTIONOS_HOME:-$HOME/.productionos}/` is the persistent state dir for config/analytics/sessions/instincts.
- **Install script location**: `bin/install.cjs` (14465 bytes, Node-only zero-dep installer used via `npx productionos@latest`). No SessionStart-based dep-install hook — `hooks/session-start.sh` does setup (state dirs, config detection) but not dependency installation.
- **Change detection**: none at hook level. `npx productionos@latest` versioning is delegated to npm; `pos-update-check` displays "ProductionOS v$CURRENT" from VERSION with a snooze file mechanism at `~/.productionos/cache/update-snoozed`.
- **Retry-next-session invariant**: not applicable — no SessionStart install hook that could fail mid-install.
- **Failure signaling**: hooks use `set -euo pipefail`, write to `$STATE_DIR/logs/hook-errors.log` via an `_log_error` helper, and degrade gracefully (checks for `bun`, `python3`, `jq` binaries, falls back to plain-text when TUI unavailable).
- **Runtime variant**: Node/Bun for scripts, TypeScript build artifacts, React/Ink for TUI; bash for hooks; Python 3 system-installed for inline JSON parsing in hooks.
- **Alternative approaches**: `npx productionos@latest` as the primary distribution channel (alternative to plugin-marketplace), with a `pos-sync` script for manual repo-to-plugin-cache sync.
- **Version-mismatch handling**: none documented — assumes system Python 3 and bun ≥1.3.10 per CI, but no runtime version pin or ABI tracking.
- **Pitfalls observed**: the plugin conflates three installation substrates — Claude Code plugin marketplace (`.claude-plugin/marketplace.json`), Codex plugin (`.codex-plugin/plugin.json`), and npm (`package.json` with `bin: { productionos: "bin/install.cjs" }`). `bin/pos-sync` hardcodes `$HOME/.claude/plugins/cache/productupgrade/productupgrade/1.0.0-beta.1` — a stale path from the pre-rebrand product slug that will silently skip everything on a current install. `node_modules/` is neither gitignored here for bun.lock commits nor cleanly separated from plugin content, so an end-user install via `claude plugin install` will NOT populate `node_modules` — every `bun run`/Ink-dependent code path silently falls back to plain-text. This is the canonical case of "bun install required but no hook runs it."

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — 11 shell tools in `bin/` (pos-* family) plus `install.cjs` Node installer.
- **`bin/` files**:
  - `install.cjs` — Node-only zero-dep installer for `npx productionos@latest`; handles `--codex`, `--all-targets`, `--uninstall`, `--update`.
  - `pos-init` — initialize `~/.productionos/` state dir and write default `settings.json`.
  - `pos-config` — get/set/list config with a validated key allowlist, Python3-based JSON mutation via `sys.argv`.
  - `pos-analytics` — analytics dashboard; tries Ink (bun + React TUI) first, falls back to plain text.
  - `pos-sync` — copy repo files into a hardcoded (stale) plugin-cache path.
  - `pos-telemetry` — append JSONL event to `$STATE_DIR/analytics/skill-usage.jsonl`.
  - `pos-update-check` — VERSION check with snooze-file cache.
  - `pos-review-log`, `pos-learnings-log`, `pos-learnings-search`, `pos-timeline-log` — append/search various JSONL logs under `~/.productionos/`.
- **Shebang convention**: `#!/usr/bin/env bash` on all pos-* scripts; `#!/usr/bin/env node` on `install.cjs`. Mixed, but consistent per language.
- **Runtime resolution**: canonical `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}` env-var-with-fallback pattern (observed in `pos-init`, `pos-analytics`, `pos-update-check`, `hooks/session-start.sh`). The fallback makes every bin script also runnable after a raw `git clone` outside the plugin harness.
- **Venv handling (Python)**: not applicable — Python is used inline only (`python3 -c "..."`) against system Python; no venv managed by this plugin.
- **Platform support**: nix-only. No `.cmd` or `.ps1` pairs. `pos-analytics` probes `/Applications/claude-devtools.app` (macOS only) in the session-start hook for auto-launch; `open` command is macOS-specific.
- **Permissions**: not explicitly observed — files downloaded via raw.githubusercontent.com lose mode bits. README does not mention `chmod +x`, and `bin/` scripts have bash shebangs (consistent with either 100755 executable or 100644 invoked as `bash <path>`). The `bin` field in `package.json` declares `productionos: "bin/install.cjs"`, so npm handles chmod on install for that one file; the pos-* scripts are invoked internally via full paths from hooks, not via PATH, so executable bit is not strictly required.
- **SessionStart relationship**: static — bin scripts are standalone tools the user or hooks invoke manually. No hook populates or rewrites them.
- **Pitfalls observed**: the env-var-with-fallback shebang+path pattern is canonical (matches the target claude-marketplace pattern exactly). But `pos-sync`'s hardcoded destination path (`~/.claude/plugins/cache/productupgrade/productupgrade/1.0.0-beta.1`) is a refactor-rot artifact — after the rebrand to ProductionOS, the path should be `.../productionos/productionos/2.0.0-beta.1`. Script silently exits on the now-missing path rather than resolving via `CLAUDE_PLUGIN_ROOT`. Also: `pos-analytics` assumes `bun` is on PATH and the plugin's `node_modules` contains Ink — neither is guaranteed after a plain plugin install.

## 8. User configuration

- **`userConfig` present**: no (GitHub code search for `userConfig` in repo: 0 results).
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable — no `${user_config.KEY}` or `CLAUDE_PLUGIN_OPTION_*` observed. Configuration instead flows through a plugin-managed `~/.productionos/config/settings.json` file mutated by the `pos-config` bin tool.
- **Pitfalls observed**: skipping the native `userConfig` surface in favor of a custom JSON file at `$HOME/.productionos/config/settings.json` means the Claude Code config UI cannot discover or edit these settings; the user must use the `pos-config get/set/list` CLI. Configuration keys are enforced via an allowlist in `pos-config` (`proactive`, `telemetry`, `auto_review`, `auto_learn`, `self_eval`, `review_on_edit`, `max_agents_per_wave`, `max_iterations`) — this doubles up validation work the plugin schema would provide natively.

## 9. Tool-use enforcement

- **PreToolUse hooks**: three matcher blocks totalling five hook invocations. (1) matcher `Edit|Write|Bash|NotebookEdit|mcp__filesystem__write_file|mcp__filesystem__edit_file|mcp__filesystem__move_file` runs `hooks/scope-enforcement.sh`. (2) matcher `Edit|Write|Bash` runs three in parallel: `repo-boundary-guard.sh`, `protected-file-guard.sh`, `pre-edit-security.sh`. (3) matcher `Bash` runs `pre-commit-gitleaks.sh` for secret scanning. Purposes: scope enforcement, repo-boundary guard, protected-file guard, pre-edit security scan, secrets (gitleaks) scan.
- **PostToolUse hooks**: two matcher blocks totalling five invocations. (1) matcher `Edit|Write` runs `self-learn.sh`, `post-edit-telemetry.sh`, `post-edit-review-hint.sh`, `eval-gate.sh` — all async. (2) matcher `Bash` runs `post-bash-telemetry.sh` async. Plus Stop-event handlers (`stop-session-handoff.sh`, `stop-extract-instincts.sh`, `stop-eval-gate.sh`) for session-end processing.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: `statusMessage` fields in hooks.json (e.g., "ProductionOS: Scope check...", "ProductionOS: Security scan...") for UI; errors go to `$STATE_DIR/logs/hook-errors.log` via an `_log_error` helper. stderr human-readable; `set -euo pipefail` halts on uncaught errors. No JSON `systemMessage` / `continue: false` / `stopReason` observed.
- **Failure posture**: fail-open in practice — each hook guards its own binary availability with `_HAS_BUN`/`_HAS_PYTHON`/`_HAS_JQ` probes and `|| true` suppressors on optional steps; `set -euo pipefail` only halts on truly uncaught errors in the critical path.
- **Top-level try/catch wrapping**: observed as a convention — `_log_error` helper plus `command -v X >/dev/null 2>&1 || true` patterns plus `|| echo "0"` defaults on every inline `python3 -c` call. Not language-level try/catch (bash doesn't have it) but equivalent defensive structure.
- **Pitfalls observed**: the concurrent PostToolUse block runs four async hooks on every Edit/Write — heavy overhead per tool call, and no deduplication if the same event fires multiple scripts appending to the same JSONL file. `eval-gate.sh` running async on PostToolUse can leak background processes if the user exits mid-call.

## 10. Session context loading

- **SessionStart used for context**: yes. Matcher `startup|resume|clear|compact` — fires on all four sub-events. Emits an ASCII or Ink-rendered banner with agent/command/hook counts, project name, sessions count, DevTools status, etc. Also writes `FIRST_RUN: true` on a fresh install for ONBOARDING.md triggering.
- **UserPromptSubmit for context**: no — not in `hooks/hooks.json`.
- **`hookSpecificOutput.additionalContext` observed**: no — SessionStart output is printed to stdout as a banner, not injected as additional context via the structured hook output format.
- **SessionStart matcher**: `startup|resume|clear|compact` (all four sub-events, via pipe-separated regex).
- **Pitfalls observed**: the banner mechanism reads `PLUGIN_ROOT/VERSION` with a fallback of `1.2.0-beta.1` (stale historical number) — a broken/unreadable VERSION will display a number from months ago. The banner also unconditionally calls `open "$DEVTOOLS_APP"` to launch a macOS GUI app when `devtools_autolaunch` is true — intrusive default behavior for a code-review plugin.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no (code search for monitors+json in repo: 0 hits).
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none — the plugin does not participate in the monitors feature, consistent with its self-owned telemetry approach (JSONL files under `~/.productionos/analytics/`).

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — no git tags at all on the repo, single-plugin marketplace.
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: `bun test` (bun's built-in Jest-compatible runner) for 29 `.ts` test files; one `tests/test_dashboard.py` present for Python script testing (framework unclear — likely unittest from filename convention).
- **Tests location**: `tests/` at repo root — flat layout, 29 `*.test.ts` files plus `test_dashboard.py`.
- **Pytest config location**: not applicable — no pytest; the one Python test is a standalone file.
- **Python dep manifest for tests**: not applicable.
- **CI present**: yes.
- **CI file(s)**: `.github/workflows/ci.yml` (single workflow file, 3045 bytes).
- **CI triggers**: `push: branches: [main]` and `pull_request: branches: [main]`.
- **CI does**: four jobs — `validate` (bun install + `bun run skill:check` + `bun run validate` + schema-validation tests + full `bun test`), `lint` (strict `tsc --noEmit`, 0-errors gate), `eval-gate` (runs `bun run eval`, parses score and critical-count, fails on any critical findings), `convergence-check` (`bun run scripts/convergence.ts --test`).
- **Matrix**: none — single `ubuntu-latest` runner, single Bun version (`1.3.10` pinned).
- **Action pinning**: tag pinning — `actions/checkout@v5`, `oven-sh/setup-bun@v2`, `actions/cache@v5`. No SHA pinning.
- **Caching**: `actions/cache@v5` on `~/.bun/install/cache` keyed by `hashFiles('**/package.json')` — no lockfile hashing despite `bun.lock` being present (cache could be more precise).
- **Test runner invocation**: `bun test` directly; plus `bun run skill:check` and `bun run validate` as gate scripts; `bun run eval` as the eval-gate entry point.
- **Pitfalls observed**: the eval-gate job greps `bun run eval` stdout for `"OVERALL"` and `"Total:"` strings to extract score/critical counts — brittle to any output format change. The tests are trust-me rather than run-with-exit-code; the workflow explicitly calls out "Use bun test's exit code directly — more reliable than parsing grep output" for the main test job (the eval-gate job didn't get the same treatment). No dependabot/renovate bot configuration for action bumps.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no (code search for release workflows in `.github`: 0 hits beyond ci.yml).
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — no automated release pipeline; versioning is done manually across VERSION + 4 JSON manifests + CHANGELOG, and distribution is via `npm publish` (presumably manual) plus the marketplace-by-URL mechanism.
- **Tag-sanity gates**: not applicable — there are no tags to gate.
- **Release creation mechanism**: none automated. No GitHub releases exist on this repo.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable.
- **Pitfalls observed**: the absence of any release automation combined with five separate version-string locations (VERSION, plugin.json, marketplace.json, package.json, .codex-plugin/plugin.json) is the primary drift vector — observed already in the CHANGELOG which lists `[8.0.0-alpha.2]` at the top despite every manifest saying `2.0.0-beta.1`. A pre-commit hook or release script would prevent this.

## 15. Marketplace validation

- **Validation workflow present**: yes — built into `ci.yml`'s `validate` job rather than a separate workflow.
- **Validator**: custom Bun/TypeScript validators in `scripts/` — `skill-check.ts`, `validate-agents.ts`, plus a dedicated `tests/schema-validation.test.ts` (invoked as `bun test tests/schema-validation.test.ts`). No `claude plugin validate` CLI invocation.
- **Trigger**: `push` + `pull_request` on main.
- **Frontmatter validation**: yes — `bun run validate` runs `scripts/validate-agents.ts` which validates agent YAML frontmatter.
- **Hooks.json validation**: yes — schema-validation test covers marketplace.json, plugin.json, hooks.json per the CI step label "Validate schemas (marketplace, plugin, hooks)".
- **Pitfalls observed**: validators are in-repo TypeScript scripts rather than shared/published validators — they enforce ProductionOS-internal schemas (including custom `stakes`, `subagent_type: productionos:*`) alongside the standard ones, so passing here does not equate to passing `claude plugin validate`.

## 16. Documentation

- **`README.md` at repo root**: present (~18.6 KB, substantial — covers quick start, core loop, workflow catalog, install matrix for Claude Code + Codex + npx).
- **`README.md` per plugin**: not applicable (single-plugin repo).
- **`CHANGELOG.md`**: present, 13.6 KB, Keep-a-Changelog-style format with dated semver sections — but top entry is stale (`[8.0.0-alpha.2]` — 2026-03-22) relative to current `2.0.0-beta.1`.
- **`architecture.md`**: present — `ARCHITECTURE.md` at repo root (22.8 KB, substantial).
- **`CLAUDE.md`**: present at repo root (18 KB). Also a root-level `SKILL.md` (3 KB) and `SKILL_REGISTRY.md` (3.3 KB), plus `AGENTS.md` (5.9 KB, Codex-style), plus `ETHOS.md` (7.1 KB).
- **Community health files**: `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md` — all three present.
- **LICENSE**: present (MIT).
- **Badges / status indicators**: CI badge linking to the ci.yml workflow — observed in README header.
- **Pitfalls observed**: the root-level `CLAUDE.md`, `SKILL.md`, `SKILL_REGISTRY.md`, `AGENTS.md`, `ETHOS.md`, `ARCHITECTURE.md`, `CHANGELOG.md`, `README.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE`, `VERSION`, `package.json`, `tsconfig.json`, `bun.lock`, `.markdownlint.json` combination is 17+ top-level files — a busy repo root that signals "kitchen sink" rather than progressive disclosure. `CLAUDE.md` and `SKILL.md` both present at the root suggests conflated roles (project memory vs skill definition). `AGENTS.md` is a Codex convention, mixed in with Claude-specific files.

## 17. Novel axes

- **Dual-target plugin distribution (Claude Code + Codex from one repo).** Ships `.claude-plugin/marketplace.json` for Claude and `.codex-plugin/plugin.json` for Codex, with overlapping skill content mirrored into `.claude/skills/`, `skills/`, and `codex-skills/`. A build step (`scripts/gen-targets.ts`) regenerates the mirrored copies. The installer `bin/install.cjs` handles `--codex`, `--all-targets`, `--uninstall` flags against `CLAUDE_CONFIG_DIR`/`CODEX_HOME`. This is the first observed plugin that treats Claude Code and Codex as parallel install targets driven by the same source.
- **`stakes` field on agent frontmatter (HIGH/MEDIUM/LOW).** Borrowed from HumanLayer / 12-Factor-Agents; classifies the risk level of each agent and is used by the `approval-gate` agent to gate HIGH-stakes operations. Non-standard frontmatter extension.
- **`subagent_type` namespace convention — `productionos:<name>`.** Used on every agent to avoid collisions with other plugins' agents, anticipating multi-plugin installs.
- **npm as secondary distribution substrate.** `bin/install.cjs` is a zero-dep Node installer published via npm (`npx productionos@latest`) that runs in parallel to the marketplace install path. The plugin has three parallel install channels (marketplace, npm, manual git clone) — most other plugins have only one.
- **State directory at `$HOME/.productionos/` rather than `$CLAUDE_PLUGIN_DATA/`.** Persistent config/analytics/sessions/instincts live under a plugin-chosen dollar-sign path respecting an override env var (`PRODUCTIONOS_HOME`) rather than the Claude Code conventional data dir. Cross-session, cross-project, cross-tool (Claude + Codex) state sharing is the deliberate design.
- **Ink/React TUI with plain-text fallback for CLI tools.** `pos-analytics` and the session banner probe for bun + the Ink scripts + a real TTY before invoking React; fall back to plain text otherwise. Graceful-degradation pattern worth cataloging.
- **Stop-event handlers for session-end processing.** Three Stop hooks (`stop-session-handoff.sh`, `stop-extract-instincts.sh`, `stop-eval-gate.sh`) aggregate analytics and produce session handoff summaries on Stop — a multi-hook usage of Stop events beyond the single cleanup pattern.
- **Eval-gate as a CI job.** `ci.yml` runs `bun run eval` and parses score + critical-finding count as a gate — a meta-layer where the plugin evaluates its own artifacts against its own rubrics as part of CI, using an "LLM judge" agent pattern.
- **Cross-session instinct/learning extraction.** `self-learn.sh` (PostToolUse) and `stop-extract-instincts.sh` (Stop) write JSONL learning events used by `pos-learnings-search` for cross-session pattern propagation — a durable persistent-memory pattern outside of native Claude Code memory.

## 18. Gaps

- **Executable-bit status on `bin/` and `hooks/` scripts.** Raw raw.githubusercontent.com fetches do not expose Unix file modes. Resolution: `gh api repos/.../contents/bin/pos-init` with `--jq .content` returns base64 content but not mode; a full `git clone` or `gh api repos/.../git/trees/main?recursive=1` with mode inspection would reveal whether shebangs are backed by 100755 or 100644.
- **Full content of `CLAUDE.md`, `SKILL.md`, `ARCHITECTURE.md`, `README.md` beyond first pages.** Fetched only openings. Full reads would confirm whether user-facing install instructions match the observed manifest reality (e.g., whether README calls out the `pos-sync` stale-path bug).
- **Per-skill frontmatter and `filePattern`/`bashPattern` auto-activation metadata.** Only one agent frontmatter (`code-reviewer`, `approval-gate`) was spot-checked. CHANGELOG mentions "4 skills with filePattern/bashPattern metadata" — those skill files (in `.claude/skills/`) were not opened to confirm the auto-activation pattern exact shape.
- **Contents of `tests/schema-validation.test.ts`.** Its existence confirms schema validation is performed in CI, but the exact schemas (whether they match the claude-code plugins-reference schema or a superset with ProductionOS extensions) were not read.
- **Whether `node_modules/` is actually installed at user plugin-install time.** CI runs `bun install`; `claude plugin install productionos` would NOT run bun. Absence of a SessionStart hook step for `bun install` strongly suggests every `bun run`-gated code path (Ink banner, dashboards) silently falls back for real users. This is inferred from hook code and package.json, not directly observed on an installed instance.
- **Relationship between the 81-file agents directory and the 80-path plugin.json `agents` array.** Exact identity of the one extra file (unreferenced in plugin.json) not determined; listing a diff would require enumerating all 81 filenames against the manifest.
- **Whether any git tags exist beyond the main-branch view.** `gh api .../tags` returned empty; `.../releases` returned empty; but `gh api .../git/refs/tags` returned 404 (no refs namespace) — consistent with "zero tags" rather than "tag list truncated".
