# Sample

Mirrors of `https://github.com/ShaheerKhawaja/ProductionOS`. Dual-target AI engineering OS for Claude Code and Codex carrying 80 agents, 41 commands, 51 skills, and 15 hooks; deploys specialized agents that review, score, and improve a codebase with smart routing, recursive convergence, and self-evaluation. Default branch `main`; MIT license; 6 stars; last commit 2026-04-16. Sample origin: bin-wrapper.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` co-located with `.claude-plugin/plugin.json` at repo root, advertising one plugin entry whose `source` is `"./"`. The plugin and the marketplace share the same repo root. `metadata.{description, version, homepage, repository, license}` wrapper present; no `pluginRoot` field. `$schema` absent.

### Top-level `metadata` wrapper variants

Marketplace top-level metadata uses the `metadata.{description, version, homepage, repository, license}` shape — license at the marketplace surface, surfacing marketplace identity separately from plugin identity. `owner` is declared at the marketplace top level (outside `metadata`), duplicating author info also supplied under each plugin entry — a minor redundancy risk if edited in one place and not the other.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry; plugin root and repo root coincide.

### `strict` field default

`strict: false` is set explicit on the marketplace entry but no narrowing override (`skills`, `commands`, `agents`) is supplied. The relaxed `strict: false` simply permits components beyond the canonical roots — root-level `CLAUDE.md`, `SKILL.md`, `SKILL_REGISTRY.md`, custom `prompts/`, `algorithms/`, `templates/`, `codex-overrides/`, `codex-skills/` directories. The plugin relies entirely on `plugin.json`'s explicit `agents` array (80 paths) plus `skills`/`commands` directory references.

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

Marketplace entry carries `category: "workflow"` plus eight `keywords` (`productionos`, `production-upgrade`, `omni-plan`, `auto-swarm`, `code-review`, `security-audit`, `codex`, `claude-code`) and six `tags` (`productionos`, `claude-code-plugin`, `codex-plugin`, `multi-agent`, `recursive-improvement`, `self-evaluation`). All three dimensions populated.

## Version coordination

### Multi-site sprawl (5+ locations)

Five separate version sites maintained in parallel: a `VERSION` file (authoritative — read at runtime by `bin/install.cjs`, `bin/pos-init`, `bin/pos-update-check`, `hooks/session-start.sh`), `plugin.json`, `.claude-plugin/marketplace.json`, `package.json`, and `.codex-plugin/plugin.json`. All four JSON manifests hardcode the same string (`2.0.0-beta.1`) separately. PR #115 (commit message: "fix(cli): pos-init reads version from VERSION file instead of hardcoding") indicates a recent partial move toward VERSION-file authority without yet centralizing all references.

### Stale fallback constants in code

`hooks/session-start.sh` hardcodes `1.2.0-beta.1` as a fallback when VERSION cannot be read — a stale historical number that would mislabel a broken install if ever surfaced.

### Multi-site drift accepted as cosmetic

`CHANGELOG.md` top entry is `[8.0.0-alpha.2]` (2026-03-22), inconsistent with every other authoritative version source at `2.0.0-beta.1`. Indicates an in-flight rebrand/renumber where the CHANGELOG was not reset; the `feat/v2.1`, `feat/v3`, `feat/v5.1`, `feat/v5.3`, `feat/v7`, `feat/v8` long-lived branches represent parallel-timeline development that the current `2.0.0-beta.1` cannot reconcile.

## Channel distribution

### npm registry as de facto channel substrate

The repo has zero git tags and zero GitHub releases despite shipping a `2.0.0-beta.1` marker. Users installing via `claude plugin marketplace add ShaheerKhawaja/ProductionOS` track whatever is on `main` at install time, with no pin mechanism other than a raw commit SHA. Combined with `npx productionos@latest`, the npm registry is the de facto versioning substrate rather than git tags.

## Tag and release lifecycle

### Hand-bumped versions on main (untagged)

Default branch `main`. Zero tags, zero releases. Long-lived `feat/*` branches exist (30+ visible — `feat/v2.1-autonomous-pipeline`, `feat/v5.1-production-ready`, `feat/v7-audit-fixes-research`, `feat/v8-sprint1-guardrails-retro`, `feat/v8-sprint5-worktree-isolation`) but these are WIP/feature branches merged back to main, not release branches. Pre-release `-beta.1` and `-alpha.2` suffixes appear in version strings; no dev-counter scheme. Version is manually edited across VERSION + 4 JSON manifests + CHANGELOG at each release.

## Plugin-component registration

### Mixed (paths + auto-discovery)

`plugin.json` uses explicit path arrays for agents (80 relative paths, one per file) alongside directory references for commands (`"./.claude/commands/"`) and skills (`"./.claude/skills/"`). No `hooks` field in `plugin.json` — hooks live in a top-level `hooks/hooks.json` discovered by convention.

### Component types absent across the corpus

`.mcp.json` no, `.lsp.json` no, monitors no, `output-styles` no.

## Component composition

### Skills (universal)

Three locations: `.claude/skills/` (4 entries), top-level `skills/`, and `codex-skills/` — Codex-parity shipping of the same skill content under multiple paths. `scripts/gen-targets.ts` regenerates the mirrored copies.

### Commands

41 files in `.claude/commands/`.

### Agents

80 files referenced by explicit paths in `plugin.json`'s `agents` array; the filesystem reports 81 files in `agents/`, a one-file mismatch where one agent file is present but unreferenced.

### Hooks

18 shell/python scripts in `hooks/` referenced by `hooks/hooks.json`.

### bin

11 shell tools in `bin/` (`pos-init`, `pos-config`, `pos-analytics`, `pos-sync`, `pos-telemetry`, `pos-update-check`, `pos-review-log`, `pos-learnings-log`, `pos-learnings-search`, `pos-timeline-log`, plus the shared library) plus `bin/install.cjs` (Node-only zero-dep installer).

## Plugin-component placement

### Inside plugin directory

Components live under the plugin root: `.claude/skills/`, `.claude/commands/`, `agents/`, `hooks/`, `bin/`. Auto-discovery and `${CLAUDE_PLUGIN_ROOT}` interpolation work as designed.

## Agent declaration conventions

### Custom agent frontmatter extensions

Standard fields (`name`, `description`, `color` optional, `model` sonnet/haiku, `tools` Read/Glob/Grep) coexist with non-standard ones — `subagent_type` namespaced as `productionos:<name>` and `stakes` (low/medium/high) borrowed from HumanLayer / 12-Factor-Agents discipline. The plugin's internal readers consume these; the harness ignores them.

### Plain tool-name list

`tools:` carries plain tool names (`Read`, `Glob`, `Grep`) — no permission-rule syntax like `Bash(uv run *)`.

## Cross-platform skill publishing

### Multi-runtime skill mirrors

Skill content mirrors into `.claude/skills/`, top-level `skills/`, and `codex-skills/` — the same skill content under multiple paths for Claude and Codex parity. `scripts/gen-targets.ts` regenerates the mirrored copies; running it is the only way to keep mirrors aligned.

## Server runtime (MCP)

### No bin entry / direct invocation

Plugin does not ship an MCP server. Bin scripts and hooks are the executable surface; no `.mcp.json` exists.

## Bin entry mechanism

### Multi-script bin family / CLI dispatcher

A `bin/` directory contains many small per-purpose scripts (`pos-init`, `pos-config`, `pos-analytics`, `pos-sync`, `pos-telemetry`, `pos-update-check`, plus four log-related verbs and `install.cjs`) rather than one entry point. Each script handles one verb; hooks invoke them via full path. Uniform `#!/usr/bin/env bash` shebang on pos-* scripts; `#!/usr/bin/env node` on `install.cjs`. Scripts compute `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}` so they work under plugin install, manual clone, or ad-hoc invocation. `pos-config` uses Python3-based JSON mutation against an allowlist of keys (`proactive`, `telemetry`, `auto_review`, `auto_learn`, `self_eval`, `review_on_edit`, `max_agents_per_wave`, `max_iterations`).

### Stale hardcoded paths after rebrand

`bin/pos-sync` hardcodes `$HOME/.claude/plugins/cache/productupgrade/productupgrade/1.0.0-beta.1` — a stale path from the pre-rebrand product slug. After the rebrand to ProductionOS, the path should be `.../productionos/productionos/2.0.0-beta.1`. Script silently exits on the now-missing path rather than resolving via `CLAUDE_PLUGIN_ROOT`.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Pos-* scripts and `hooks/session-start.sh` use the canonical `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}` pattern — env-var preferred, script-relative fallback. The fallback makes every bin script also runnable after a raw `git clone` outside the plugin harness.

## Dependency installation

### Manual `npm install` post-install

`bun install` writes to `node_modules/` inside the plugin root (`${CLAUDE_PLUGIN_ROOT}/node_modules/`), but no SessionStart-based dep-install hook runs it. `hooks/session-start.sh` does setup (state dirs, config detection) but not dependency installation. `claude plugin install productionos` will NOT populate `node_modules` — every `bun run`/Ink-dependent code path silently falls back to plain-text. CI runs `bun install`; end-user installs do not.

### npm CLI as the sole install surface

`bin/install.cjs` (14465 bytes, Node-only zero-dep installer) is published via npm and run via `npx productionos@latest`. Handles `--codex`, `--all-targets`, `--uninstall`, `--update` flags against `CLAUDE_CONFIG_DIR`/`CODEX_HOME`. Primary distribution channel parallel to the marketplace install path; `pos-sync` is the manual repo-to-plugin-cache sync.

### Mixed Python + Node install

`package.json` + `bun.lock` (Bun/Node runtime for scripts, Ink TUI, TypeScript build) plus inline `python3 -c "..."` calls in bash hooks for JSON parsing — Python is used ad-hoc against system Python with no `requirements.txt`/`pyproject.toml`. CI pins `bun: 1.3.10`; Python 3 system-installed; `jq` probed at runtime.

## Install change detection

### No change detection

No hook-level change detection. `npx productionos@latest` versioning is delegated to npm. `pos-update-check` displays "ProductionOS v$CURRENT" from VERSION with a snooze file at `~/.productionos/cache/update-snoozed`.

## Install trigger and lifecycle

### User-invoked one-shot installer

`npx productionos@latest` is the install trigger; users run it manually. No SessionStart install hook fires `bun install` during plugin load — bun-dependent paths fall back when the plugin is installed via the marketplace.

## Install failure posture

### Multi-layer fail-open with stderr advisory

Hooks use `set -euo pipefail` and write to `$STATE_DIR/logs/hook-errors.log` via an `_log_error` helper, degrading gracefully (checks for `bun`, `python3`, `jq` binaries; falls back to plain-text when TUI unavailable). `command -v X >/dev/null 2>&1 || true` patterns and `|| echo "0"` defaults on every inline `python3 -c` call.

## User configuration and authentication

### Plugin-managed JSON file with custom CLI

`userConfig` not declared in `plugin.json` (GitHub code search: 0 results). Configuration instead flows through a plugin-managed `~/.productionos/config/settings.json` file mutated by the `pos-config` bin tool. Configuration keys are enforced via an allowlist in `pos-config` (`proactive`, `telemetry`, `auto_review`, `auto_learn`, `self_eval`, `review_on_edit`, `max_agents_per_wave`, `max_iterations`). Skipping the native `userConfig` surface means the Claude Code config UI cannot discover or edit these settings; users must use the `pos-config get/set/list` CLI.

## Session context loading

### Plain-stdout context banner

SessionStart fires on `startup|resume|clear|compact` (all four sub-events via pipe-separated regex). Emits an ASCII or Ink-rendered banner with agent/command/hook counts, project name, sessions count, DevTools status. Output is printed to stdout as a banner, not injected via the structured `hookSpecificOutput.additionalContext` envelope. The banner reads `PLUGIN_ROOT/VERSION` with a fallback of `1.2.0-beta.1` — a broken/unreadable VERSION file displays a stale historical number. The banner unconditionally calls `open "$DEVTOOLS_APP"` to launch a macOS GUI app when `devtools_autolaunch` is true, writing `FIRST_RUN: true` on a fresh install for ONBOARDING.md triggering.

## SessionStart matcher scope

### Empty matcher (all sub-events)

SessionStart matcher uses `startup|resume|clear|compact` (pipe-separated regex covering all four sub-events), with full re-execution every time including `/clear` and `/compact`. The banner-emit work is non-trivial — agent/command/hook counts, project name lookup, DevTools probe — and runs on every sub-event.

## Tool-use enforcement

### PreToolUse guard set with multi-matcher concurrency

Three PreToolUse matcher blocks. (1) Matcher `Edit|Write|Bash|NotebookEdit|mcp__filesystem__write_file|mcp__filesystem__edit_file|mcp__filesystem__move_file` runs `hooks/scope-enforcement.sh`. (2) Matcher `Edit|Write|Bash` runs three guards in parallel: `repo-boundary-guard.sh`, `protected-file-guard.sh`, `pre-edit-security.sh`. (3) Matcher `Bash` runs `pre-commit-gitleaks.sh` for secret scanning. Five hook invocations across the three blocks.

### PostToolUse async telemetry + eval gate

Two PostToolUse matcher blocks. (1) Matcher `Edit|Write` runs `self-learn.sh`, `post-edit-telemetry.sh`, `post-edit-review-hint.sh`, `eval-gate.sh` — all async. (2) Matcher `Bash` runs `post-bash-telemetry.sh` async. The concurrent block runs four async hooks on every Edit/Write — heavy overhead per tool call, no deduplication if multiple scripts append to the same JSONL file. `eval-gate.sh` running async on PostToolUse can leak background processes if the user exits mid-call.

### Stop-event handlers for session-end aggregation

Three Stop hooks (`stop-session-handoff.sh`, `stop-extract-instincts.sh`, `stop-eval-gate.sh`) aggregate analytics and produce session handoff summaries.

## Hook handler runtime

### Per-hook bash scripts with selective strict mode

Each hook is a small bash script invoked directly from `hooks.json`. `set -euo pipefail` is used; errors go to `$STATE_DIR/logs/hook-errors.log` via an `_log_error` helper. `command -v X >/dev/null 2>&1 || true` probes guard binary availability (`_HAS_BUN`, `_HAS_PYTHON`, `_HAS_JQ`). No JSON `systemMessage` / `continue: false` / `stopReason` observed; `statusMessage` fields in `hooks.json` (e.g., "ProductionOS: Scope check...", "ProductionOS: Security scan...") drive UI display.

## Hook output contract

### `systemMessage` for human-readable summaries

Hooks emit `statusMessage` fields in `hooks.json` for UI display ("ProductionOS: Scope check...", "ProductionOS: Security scan..."). stderr carries human-readable error messages; errors go to `$STATE_DIR/logs/hook-errors.log` via an `_log_error` helper.

## Hook failure posture

### Fail-open posture with explicit comment contract

Each hook guards its own binary availability with `_HAS_BUN`/`_HAS_PYTHON`/`_HAS_JQ` probes and `|| true` suppressors on optional steps; `set -euo pipefail` only halts on truly uncaught errors in the critical path. Bash-equivalent of try/catch via `_log_error` helper plus `command -v X >/dev/null 2>&1 || true` patterns plus `|| echo "0"` defaults on every inline `python3 -c` call. Fail-open in practice.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code (bin scripts, hooks) lives under `${CLAUDE_PLUGIN_ROOT}`. State (config, analytics, sessions, instincts) lives under `${PRODUCTIONOS_HOME:-$HOME/.productionos}/` — a plugin-chosen path with override env var.

## State persistence

### Plugin-chosen `$HOME/.<plugin>/` with override env var

Persistent config/analytics/sessions/instincts live under `$HOME/.productionos/` respecting an override env var (`PRODUCTIONOS_HOME`) rather than the Claude Code conventional `${CLAUDE_PLUGIN_DATA}`. Cross-session, cross-project, cross-tool (Claude + Codex) state sharing is the deliberate design.

### JSONL append-only event logs

Telemetry and learning events written as JSONL to `$HOME/.productionos/analytics/` (e.g., `skill-usage.jsonl`). `pos-telemetry`, `pos-review-log`, `pos-learnings-log`, `pos-learnings-search`, `pos-timeline-log` are the bin-tool surface for append/search.

## Live monitoring

### `monitors.json` absent

No `monitors.json` (code search: 0 hits). Plugin does not participate in the monitors feature, consistent with its self-owned telemetry approach (JSONL files under `~/.productionos/analytics/`).

## Telemetry and self-evaluation

### Multi-hook recording pipeline → MCP server → read-only agent

Telemetry pipeline spans PostToolUse hooks (`self-learn.sh`, `post-edit-telemetry.sh`), Stop hooks (`stop-extract-instincts.sh`), and append-only JSONL stores (`skill-usage.jsonl`, instinct/learning logs) consumed by `pos-learnings-search` for cross-session pattern propagation. Durable persistent-memory pattern outside of native Claude Code memory.

### Eval-gate as a CI job

`ci.yml` runs `bun run eval` and parses score + critical-finding count as a gate — a meta-layer where the plugin evaluates its own artifacts against its own rubrics as part of CI, using an "LLM judge" agent pattern.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field declared. Single-plugin marketplace.

## Testing

### bun test with TypeScript

`bun test` (Bun's built-in Jest-compatible runner) executes 29 `*.test.ts` files in flat `tests/` at repo root. One `tests/test_dashboard.py` present for Python script testing (framework unclear — likely unittest from filename convention).

## CI workflow shape

### Single-workflow validate + lint + eval-gate + convergence

`.github/workflows/ci.yml` (3045 bytes, single workflow file). Triggers: `push: branches: [main]` and `pull_request: branches: [main]`. Four jobs — `validate` (bun install + `bun run skill:check` + `bun run validate` + schema-validation tests + full `bun test`), `lint` (strict `tsc --noEmit`, 0-errors gate), `eval-gate` (runs `bun run eval`, parses score and critical-count, fails on any critical findings), `convergence-check` (`bun run scripts/convergence.ts --test`). Single `ubuntu-latest` runner, single Bun version (`1.3.10` pinned). Tag pinning — `actions/checkout@v5`, `oven-sh/setup-bun@v2`, `actions/cache@v5`. Caching via `actions/cache@v5` on `~/.bun/install/cache` keyed by `hashFiles('**/package.json')` — no lockfile hashing despite `bun.lock` being present. The eval-gate job greps `bun run eval` stdout for `"OVERALL"` and `"Total:"` strings to extract score/critical counts — brittle to any output format change.

## Marketplace validation

### In-CI custom validators

Validation built into `ci.yml`'s `validate` job rather than a separate workflow. Custom Bun/TypeScript validators in `scripts/` — `skill-check.ts`, `validate-agents.ts`, plus a dedicated `tests/schema-validation.test.ts` (invoked as `bun test tests/schema-validation.test.ts`). No `claude plugin validate` CLI invocation. Trigger: `push` + `pull_request` on main. Frontmatter validation: `bun run validate` runs `scripts/validate-agents.ts` validating agent YAML frontmatter. Schema-validation test covers marketplace.json, plugin.json, hooks.json. Validators enforce ProductionOS-internal schemas (including custom `stakes`, `subagent_type: productionos:*`) alongside standard ones — passing here does not equate to passing `claude plugin validate`.

## Release automation

### No release automation / manual

No `release.yml` or equivalent (code search for release workflows in `.github`: 0 hits beyond ci.yml). Versioning done manually across VERSION + 4 JSON manifests + CHANGELOG; distribution via `npm publish` (presumably manual) plus the marketplace-by-URL mechanism. The absence of any release automation combined with five separate version-string locations (VERSION, plugin.json, marketplace.json, package.json, .codex-plugin/plugin.json) is the primary drift vector — already manifested in the CHANGELOG which lists `[8.0.0-alpha.2]` at the top despite every manifest saying `2.0.0-beta.1`.

## Documentation surface

### Sprawling root with many entry-point markdowns

17+ top-level files including README, CHANGELOG, ARCHITECTURE, CLAUDE.md, SKILL.md, SKILL_REGISTRY.md, AGENTS.md, ETHOS.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, LICENSE, VERSION, package.json, tsconfig.json, bun.lock, .markdownlint.json. README ~18.6 KB (quick start, core loop, workflow catalog, install matrix for Claude Code + Codex + npx). ARCHITECTURE.md at repo root (~22.8 KB). CLAUDE.md at repo root (~18 KB). Root-level SKILL.md (3 KB) and SKILL_REGISTRY.md (3.3 KB). AGENTS.md (5.9 KB, Codex-style). ETHOS.md (7.1 KB). The kitchen-sink root signals conflated roles (CLAUDE.md vs SKILL.md at the same level signals conflated governance).

### Keep-a-Changelog with root-cause prose

`CHANGELOG.md` (~13.6 KB) declares Keep-a-Changelog format with dated semver sections. Top entry `[8.0.0-alpha.2]` (2026-03-22) is stale relative to current `2.0.0-beta.1` — divergence indicates the in-flight rebrand left CHANGELOG unreset.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

MIT license. `LICENSE` file present at repo root.

## Community health files

### LICENSE + CODE_OF_CONDUCT + issue templates

`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md` — all three present. README header carries a CI badge linking to ci.yml.

## Cross-platform discipline

### POSIX-only with no Windows story

bin scripts are nix-only — no `.cmd` or `.ps1` pairs. `pos-analytics` probes `/Applications/claude-devtools.app` (macOS only) in the session-start hook for auto-launch; `open` command is macOS-specific.

## Multi-runtime portability

### Per-runtime manifest directories

Ships `.claude-plugin/marketplace.json`+`plugin.json` for Claude and `.codex-plugin/plugin.json` for Codex — two per-runtime manifest directories at repo root. Skills are mirrored into `.claude/skills/`, top-level `skills/`, and `codex-skills/`. The hook schemas overlap; Claude uses `hooks/hooks.json` while Codex configuration lives in `.codex-plugin/`. The installer `bin/install.cjs` handles `--codex`, `--all-targets`, `--uninstall`, `--update` flags against `CLAUDE_CONFIG_DIR`/`CODEX_HOME`. A build step (`scripts/gen-targets.ts`) regenerates the mirrored skill copies.

### Skill content mirrored under multiple paths

Same skill files appear under `.claude/skills/`, top-level `skills/`, and `codex-skills/`. The `scripts/gen-targets.ts` regeneration script copies between locations. Hand-edits to one location must be regenerated to the others.

## Cross-ecosystem distribution

### Cross-ecosystem multi-harness distribution

Three parallel install channels driven by parallel manifests: Claude Code marketplace (`.claude-plugin/marketplace.json`), Codex plugin (`.codex-plugin/plugin.json`), and npm (`package.json` with `bin: { productionos: "bin/install.cjs" }`). `bin/install.cjs` is a zero-dep Node installer published via npm (`npx productionos@latest`) running parallel to the marketplace install path. The five version-string locations (VERSION + 4 manifests) are the version-locked surface across the three channels; manual sync rather than a release script.

## Novel and cross-cutting concerns

- **Dual-target plugin distribution (Claude Code + Codex from one repo).** Ships `.claude-plugin/marketplace.json` for Claude and `.codex-plugin/plugin.json` for Codex with overlapping skill content mirrored into three skill directories. The first observed plugin treating Claude Code and Codex as parallel install targets driven by the same source.
- **`stakes` field on agent frontmatter (HIGH/MEDIUM/LOW).** Borrowed from HumanLayer / 12-Factor-Agents; classifies the risk level of each agent and is used by the `approval-gate` agent to gate HIGH-stakes operations.
- **`subagent_type` namespace convention — `productionos:<name>`.** Used on every agent to avoid collisions with other plugins' agents, anticipating multi-plugin installs.
- **npm as secondary distribution substrate.** `bin/install.cjs` is a zero-dep Node installer published via npm; three parallel install channels coexist.
- **State directory at `$HOME/.productionos/` rather than `${CLAUDE_PLUGIN_DATA}`.** Persistent config/analytics/sessions/instincts under a plugin-chosen path with override env var (`PRODUCTIONOS_HOME`) for cross-session, cross-project, cross-tool state sharing.
- **Ink/React TUI with plain-text fallback for CLI tools.** `pos-analytics` and the session banner probe for `bun` + Ink scripts + a real TTY before invoking React; fall back to plain text otherwise.
- **Stop-event handlers for session-end processing.** Three Stop hooks aggregate analytics and produce session handoff summaries — multi-hook usage of Stop events beyond the single cleanup pattern.
- **Eval-gate as a CI job.** `ci.yml` runs `bun run eval` and parses score + critical-finding count as a gate; the plugin evaluates its own artifacts against its own rubrics in CI, using an "LLM judge" agent pattern.
- **Cross-session instinct/learning extraction.** `self-learn.sh` (PostToolUse) and `stop-extract-instincts.sh` (Stop) write JSONL learning events used by `pos-learnings-search` for cross-session pattern propagation — a durable persistent-memory pattern outside of native Claude Code memory.

## Cross-role tools

### Bun

Bun runtime pinned at 1.3.10 in CI. `bun test` for the test suite, `bun run` for build/eval/validate/lint/convergence-check scripts, `bun.lock` for dependency manifest. Bun + React/Ink for CLI TUI rendering.

### Node + npm + npx

`bin/install.cjs` (zero-dep Node installer) is published to npm and run via `npx productionos@latest`. `package.json` declares `bin: { productionos: "bin/install.cjs" }`.

### Python (stdlib + pip + uv)

System `python3` for inline JSON parsing in bash hooks (no `requirements.txt`/`pyproject.toml`). One `tests/test_dashboard.py` present for Python script testing.

### `${CLAUDE_PLUGIN_ROOT}` env var

Pos-* scripts and hooks consult `${CLAUDE_PLUGIN_ROOT}` first, falling back to script-relative computation.

### `plugin.json.version`

Hardcoded version string in `plugin.json` plus four other manifests (marketplace.json, package.json, .codex-plugin/plugin.json) and the authoritative `VERSION` file.
