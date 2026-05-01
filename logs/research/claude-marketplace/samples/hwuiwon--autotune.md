# hwuiwon/autotune

## Identification

- **URL**: https://github.com/hwuiwon/autotune
- **Stars**: 0 (observed via `gh api repos/hwuiwon/autotune`)
- **Last commit date**: 2026-03-25 (pushed_at; repo created same day)
- **Default branch**: `main`
- **License**: MIT (SPDX `MIT`, LICENSE present at root)
- **Sample origin**: bin-wrapper
- **One-line purpose**: "Autonomous optimization loops for Claude Code: edit, benchmark, keep improvements, revert regressions, repeat" (from repo description; README opens with a matching tagline for health-aware optimization loops)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: `metadata.{description}` wrapper — `{"description": "Autonomous optimization loops for Claude Code"}`. No `version`, no `pluginRoot`
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: category (`"productivity"`) + tags (`["autotune", "optimization", "benchmarking", "autonomous"]`). Single plugin so "all same" not applicable
- **`$schema`**: absent
- **Reserved-name collision**: no (plugin name `autotune` is not a reserved slug)
- **Pitfalls observed**: marketplace entry carries `category` + `tags`; plugin.json carries `keywords` with the same four values — same semantic list duplicated under two different field names (discoverability facets live in marketplace.json, keywords repeat in plugin.json). No top-level marketplace `description` — only the nested `metadata.description`.

## 2. Plugin source binding

- **Source format(s) observed**: relative — `"source": "./"` (single plugin, repo-root plugin)
- **`strict` field**: default (implicit true — no `strict` key present in marketplace.json)
- **`skills` override on marketplace entry**: absent
- **Version authority**: both — `plugin.json` has `"version": "0.3.0"` and marketplace.json's plugin entry also has `"version": "0.3.0"`; `package.json` (for the npm `bin` registration) also duplicates `"version": "0.3.0"`. Three-way duplication with drift risk
- **Pitfalls observed**: three files encode the version independently (marketplace.json, plugin.json, package.json). README quick-start shows `/plugin install autotune@autotune` — plugin name equals marketplace name, relies on CLI disambiguation.

## 3. Channel distribution

- **Channel mechanism**: no split (users install once via `/plugin marketplace add hwuiwon/autotune` with no `@ref` pinning documented)
- **Channel-pinning artifacts**: absent
- **Pitfalls observed**: none observed; single main-line distribution.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main (only one tag: `0.1.0` at commit `92a348b`; tag exists as lightweight/annotated tag with matching GitHub release)
- **Release branching**: none (single branch `main` observed)
- **Pre-release suffixes**: none observed
- **Dev-counter scheme**: absent — `plugin.json` currently declares `0.3.0` but the only git tag is `0.1.0`; subsequent bumps (`0.2.0`, `0.3.0`) are untagged ("bump version" commits exist but no corresponding tags)
- **Pre-commit version bump**: no (no hook manifest observed; `.gitignore` contents are just `node_modules/` and `.DS_Store`)
- **Pitfalls observed**: version drift — declared `0.3.0` but only `0.1.0` is tagged/released on GitHub; two "bump version" commits (`b19d6b7`, `a08aab1`) are on `main` without tags. Users installing via marketplace receive HEAD (`0.3.0`) while the GitHub Releases page advertises `0.1.0`.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — plugin.json has no `components`, `skills`, `agents`, `hooks`, or `mcpServers` fields. Component directories (`agents/`, `skills/`, `hooks/`) are discovered by Claude Code's conventional layout under `CLAUDE_PLUGIN_ROOT`
- **Components observed**: skills (yes — `skills/autotune/SKILL.md`), commands (no), agents (yes — `agents/autotune.md`), hooks (yes — `hooks/hooks.json` wiring `Stop` + `PreToolUse:Bash`), .mcp.json (no), .lsp.json (no), monitors (no), bin (yes — 7 scripts), output-styles (no)
- **Agent frontmatter fields used**: `name`, `description`, `model` (`sonnet`), `tools` (list form: `[Bash, Read, Write, Edit, Glob, Grep]`)
- **Agent tools syntax**: plain tool names (YAML list, no permission-rule syntax like `Bash(uv run *)`)
- **Pitfalls observed**: `hooks.json` lives under `hooks/` not at plugin root; Claude Code's default discovery supports both locations. Agent `tools:` is a YAML list rather than the comma-separated string variant; both forms are accepted.

## 6. Dependency installation

- **Applicable**: no — per CLAUDE.md: "No external dependencies beyond Python 3 stdlib, git, and bash". Python files (`lib/health.py`, `lib/confidence.py`) use stdlib only; shell scripts source `lib/state.sh`. Bash is a system-provided runtime check, not a packaged dep
- **Dep manifest format**: none (no `requirements.txt`, no `pyproject.toml`, no `Cargo.toml`, no `go.mod`). `package.json` exists but only declares the npm `bin` mapping and `engines.node >= 18` — no `dependencies`/`devDependencies` blocks
- **Install location**: not applicable (no install step)
- **Install script location**: not applicable
- **Change detection**: not applicable
- **Retry-next-session invariant**: not applicable
- **Failure signaling**: not applicable (no SessionStart install hook; only `Stop` + `PreToolUse` are registered)
- **Runtime variant**: not applicable (system-provided Python 3 + bash + git)
- **Alternative approaches**: not applicable
- **Version-mismatch handling**: README lists "Python 3.6+" as a prerequisite but no runtime check script enforces it
- **Pitfalls observed**: runtime prerequisites (Python 3.6+, Git, Bash) are documented in README "Requirements" but not validated at session start or first invocation. `package.json` declares `engines.node >= 18` though no plugin code uses Node — Node is only needed if the user installs via npm and consumes the `bin/autotune` shim through `npx`/npm global.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes
- **`bin/` files**:
    - `autotune` — main CLI entry point; subcommands `start`, `stop`, `clear`, `dashboard`, `status`, `explain`, `repair`, `version`; sources `$AUTOTUNE_HOME/lib/state.sh`
    - `init-experiment.sh` — initialize a session with metric name/unit/direction
    - `run-experiment.sh` — execute benchmark, parse `METRIC name=value` stdout lines, run checks
    - `log-experiment.sh` — append to `autotune.jsonl`, auto-commit or revert, compute confidence, classify health
    - `dashboard.sh` — terminal dashboard; `--watch` live mode, `--full` all experiments
    - `setup-permissions.sh` — writes scoped entries into target project's `.claude/settings.local.json` (allow-list + statusLine)
    - `statusline.sh` — Claude Code `statusLine` command; reads session JSON on stdin + `.autotune.state`, emits colorized status line with optional `--chain <cmd>` to compose with a prior status line
- **Shebang convention**: `env bash` uniformly (`#!/usr/bin/env bash`) across all scripts inspected
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback — every script computes `AUTOTUNE_HOME="${CLAUDE_PLUGIN_ROOT:-${AUTOTUNE_HOME:-$(dirname "$SCRIPT_DIR")}}"` so the same script works under plugin install, manual clone, or ad-hoc invocation
- **Venv handling (Python)**: no venv — scripts shell out to `python3` directly; only Python 3 stdlib is used. (Benchmark scripts that the *user* writes may activate `.venv/bin` — documented in SKILL.md as user responsibility, not a plugin concern)
- **Platform support**: POSIX (bash + python3 + git). No Windows `.cmd`/`.ps1` pair. macOS-aware — SKILL.md explicitly warns "no `grep -P` (macOS lacks Perl regex). Use `sed`, `awk`, or `python3 -c`"
- **Permissions**: not directly verifiable via API, but the tree includes `bin/autotune` without `.sh` extension invoked by `npm` via `package.json`'s `"bin": {"autotune": "./bin/autotune"}` — implies 100755 (executable) at minimum for that entry; sibling `.sh` files are invoked as `bash <path>` from hooks/agent prompts so 100644 would still work
- **SessionStart relationship**: static — no `SessionStart` hook registered. `bin/` is committed content; nothing lazily populated. `hooks/hooks.json` only wires `Stop` (auto-resume) and `PreToolUse:Bash` (enforce `./autotune.sh` as benchmark target)
- **Pitfalls observed**: `bin/autotune` is both (a) a plugin bin script invoked by the CLI after `/plugin install` and (b) a shim exposed via `package.json` `bin` mapping if the user `npm install -g autotune` or `npx autotune`. Dual-purpose distribution (plugin + npm) is unusual for a plugin-only marketplace entry. `bin/autotune` calls `claude --agent autotune` from `cmd_start`, assuming the `claude` CLI is on `PATH`.

## 8. User configuration

- **`userConfig` present**: no (neither marketplace.json nor plugin.json declares a `userConfig` block)
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable — configuration is loaded from per-project `autotune.config.json` read at runtime by scripts (`read_config` in `lib/state.sh`), not the Claude Code `userConfig` surface. No `${user_config.KEY}` or `CLAUDE_PLUGIN_OPTION_*` usage observed
- **Pitfalls observed**: autotune uses a project-local JSON config file (`autotune.config.json` in the user's target repo) as its configuration surface instead of plugin `userConfig`. Fields like `autoResume`, `maxIterations`, `health.*`, `recovery.*` live there. This keeps config with the project being optimized rather than the plugin, which matches the per-project nature of a tuning session.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1; matcher `"Bash"`; purpose — intercepts Bash invocations that reference `run-experiment.sh`; when `autotune.sh` exists in the resolved workdir AND autotune mode is active, validates that the `--command` arg to `run-experiment.sh` resolves to `./autotune.sh` (after stripping `env`, `time`, `nice`, `nohup`, `timeout <n>`, `VAR=val ` prefixes). Blocks with exit 2 + stderr message otherwise
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: stderr human-readable on block (plain echoed message, no JSON). Pass-through exits 0 silently
- **Failure posture**: fail-open on parse errors — every `python3 -c` call that extracts JSON fields has `2>/dev/null || echo ""` fallback, so malformed hook input, missing `autotune.sh`, inactive autotune mode, or unparseable `--command` all proceed with `exit 0` (allow). Only explicit mismatch blocks
- **Top-level try/catch wrapping**: absent — uses `set -euo pipefail` + per-statement `|| echo ""` fallbacks rather than a trap
- **Pitfalls observed**: the `--command` regex (`--command\s+["\']...["\']` with single-quote fallback, then unquoted `\S+`) is a best-effort parse; agent constructs that compose `run-experiment.sh --command` through shell variable expansion or command substitution would be read literally and potentially allowed through. The `STRIPPED` sed pipeline strips only a fixed set of wrappers; novel wrappers (`chrt`, `taskset`, `stdbuf`) would block legitimate invocations.

## 10. Session context loading

- **SessionStart used for context**: no — SessionStart is not registered at all
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no
- **SessionStart matcher**: not applicable (no SessionStart hook)
- **Pitfalls observed**: session resume context is loaded by the agent itself (`agents/autotune.md` "Session Resume Protocol" reads `autotune.md`, `autotune.jsonl`, `.autotune.state`, `autotune.ideas.md`) rather than injected by a SessionStart/UserPromptSubmit hook. This means resume only happens when the user launches the `autotune` agent explicitly — a normal Claude Code session opened in the same directory does not auto-load the session brief.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable (no monitors; statusLine is a standard Claude Code settings.json field and does not require a version floor)
- **Pitfalls observed**: autotune's "live monitoring" uses two mechanisms that do NOT use the Claude Code monitors system:
    1. `bin/dashboard.sh --watch` — a user-invoked terminal dashboard in a separate shell, not plugin-managed
    2. `bin/statusline.sh` — Claude Code `statusLine` command installed into the user's `.claude/settings.local.json` by `setup-permissions.sh`. Reads `.autotune.state` from disk and colorizes health state (`running`/`improving`/`plateaued`/`healing`/`crashing`/`paused`) plus experiment count, streaks, duration, cost, context %.
       - `statusline.sh` supports composition via `--chain <cmd>`: delegates the raw session JSON on stdin to a prior status line command (e.g., an existing HUD), then appends autotune's line below
       - `setup-permissions.sh` auto-detects an existing `statusLine` in `~/.claude/settings.json` or project settings, and if found wraps it via `--chain`, preserving prior configuration
- **Novel pattern**: no `subagentStatusLine` usage observed (grep of repo via `gh api search/code` returned 0 hits). Only `statusLine` is configured.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace)
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: none — no `tests/` directory, no test files in repo tree. CLAUDE.md "Testing" section lists manual validation commands only: `claude plugin validate .`, a spawn-from-`/tmp` plugin-dir check, and `uvx ty check lib/health.py`
- **Tests location**: not applicable
- **Pytest config location**: not applicable
- **Python dep manifest for tests**: not applicable
- **CI present**: no (no `.github/` directory — `gh api repos/hwuiwon/autotune/contents/.github` returned 404)
- **CI file(s)**: none
- **CI triggers**: not applicable
- **CI does**: not applicable
- **Matrix**: not applicable
- **Action pinning**: not applicable
- **Caching**: not applicable
- **Test runner invocation**: not applicable
- **Pitfalls observed**: no automated test or lint pipeline. `uvx ty check` (astral-sh/ty type checker) is mentioned in CLAUDE.md as an ad-hoc validation step but not wired into a workflow. Version bumps ship without gate.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable — the sole GitHub release (`0.1.0`) appears to have been created manually; no automation artifact in the repo
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: manual `gh release create` or web UI (inferred from absence of workflows and presence of a single release at `0.1.0` while `main` is at `0.3.0`)
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable (no `CHANGELOG.md`)
- **Pitfalls observed**: release cadence has fallen out of sync with main — `0.2.0` and `0.3.0` commits are untagged and unreleased, so users following GitHub Releases see stale versions while marketplace installs pull HEAD.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable — CLAUDE.md documents `claude plugin validate .` as a manual developer step
- **Trigger**: manual (developer runs it; not gated in CI)
- **Frontmatter validation**: not applicable (manual)
- **Hooks.json validation**: not applicable (manual)
- **Pitfalls observed**: validation is documented but unenforced.

## 16. Documentation

- **`README.md` at repo root**: present (~9 KB / ~220 lines). Rich: includes ASCII loop diagram, How It Works, What's Included, Quick Start, Monitor, Stop/Resume, Session Persistence, Confidence Scoring (MAD table), Health And Recovery, Backpressure Checks, Benchmark Script, Auto-Resume, Configuration table, CLI Reference, Architecture tree, Requirements, License
- **Owner profile README at `github.com/hwuiwon/hwuiwon`**: present (~23 lines, brief landing card — experience + open source contributions)
- **`README.md` per plugin**: not applicable (single-plugin repo; root README serves the plugin)
- **`CHANGELOG.md`**: absent
- **`architecture.md`**: absent (root README includes an "Architecture" section with a directory tree; no dedicated file)
- **`CLAUDE.md`**: at repo root — 1.6 KB, lists Project Structure, Conventions (bash `set -euo pipefail`, source `$AUTOTUNE_HOME/lib/state.sh`, `${CLAUDE_PLUGIN_ROOT}` convention, JSON-to-stdout for agent consumption, health-awareness principle, Python-only-for-math/JSON/health rule, no external deps), Testing
- **Community health files**: none (no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`)
- **LICENSE**: present (MIT, SPDX `MIT`)
- **Badges / status indicators**: absent
- **Pitfalls observed**: README and CLAUDE.md both cover structure; CLAUDE.md is the contributor-facing convention reference while README is the user-facing feature reference. No separate `architecture.md` even though README has enough internal detail (lib layer, JSON stdout protocol, health state machine) to justify one. `README.md` cites [karpathy/autoresearch](https://github.com/karpathy/autoresearch) as inspiration — attribution of design lineage.

## 17. Novel axes

- **Status line as primary observability surface (not monitors)** — instead of a `monitors.json`, autotune integrates with Claude Code's `statusLine` setting. `bin/statusline.sh` reads both Claude Code's session JSON on stdin AND walks up to git root looking for `.autotune.state`, then emits a single colored line with health icon (●/▲/◆/⚕/✖/⏸), experiment count, streaks, and session metrics. Novel because most plugins treat statusLine as a user-owned concern; autotune claims it and composes with prior values via `--chain`. The plugin auto-installs this via `setup-permissions.sh` running as part of the setup skill.

- **Status line composition via `--chain`** — the script accepts `--chain '<existing command>'` and delegates stdin to the prior command, printing autotune's line above it. `setup-permissions.sh` auto-detects an existing statusLine in `~/.claude/settings.json` or project settings, wraps it when present, and when absent emits the standalone form. This is a first-party, scripted way to compose status lines instead of overwriting user configuration.

- **Per-project config surface instead of `userConfig`** — plugin configuration lives in the optimized project's `autotune.config.json`, not in plugin `userConfig`. Rationale: config describes THIS tuning session (metric direction, playbook order, healing budget) not a global user preference. Stored alongside `autotune.md`, `autotune.jsonl`, `.autotune.state` so the whole session travels with the project.

- **Project-scoped `.claude/settings.local.json` mutation** — `setup-permissions.sh` writes fifteen specific allow-list entries (autotune script paths, `./autotune.sh*`, `./autotune.checks.sh*`, `git checkout -b autotune/*`, `git commit -m "autotune:*"`, scoped `git add`/`log`/`diff`/`status`/`rev-parse`) plus the statusLine block directly into the target project. Existing `permissions.allow` entries are preserved; duplicates skipped. This is a scoped, allow-list-first permission grant rather than a blanket `*` permission.

- **Hook as executable-path enforcer, not a write-guard** — the `PreToolUse:Bash` hook doesn't guard file writes; it validates that the benchmark command passed to `run-experiment.sh --command` points at `./autotune.sh`. Prevents the agent from drifting to an ad-hoc command mid-loop ("just run `pnpm test` this once") that would bypass the METRIC-parsing contract. The hook only activates when `autotune.sh` exists AND autotune mode is active — it's self-arming around session artifacts rather than always-on.

- **CLI distribution as plugin + npm bin dual-target** — `package.json` declares `"bin": {"autotune": "./bin/autotune"}` so `npm install -g` or `npx autotune` yields the same CLI the plugin install exposes. Dual-target distribution lets users drive the loop without ever installing Claude Code plugins.

- **Bounded autonomy with budgeted resume** — `hooks/stop.sh` caps auto-resume at 20 per session with a 5-minute rate limit between resumes. Tracked via `resume_count`/`resume_at` in `.autotune.state`. Three modes (`headless` launches a new `claude -p` background process; `prompt` prints instructions; `off` disables). This is plugin-level flow control for an otherwise unbounded agent loop.

- **Attribution of design lineage** — README opens with "Inspired by karpathy/autoresearch". Attribution of design-lineage inspiration directly in README is uncommon.

- **Three-file session persistence separating concerns** — `autotune.md` (living prose document, human-facing), `autotune.jsonl` (append-only experiment log), `.autotune.state` (current operating state). Each serves one consumer: markdown for humans + resume context, JSONL for tooling (dashboard, confidence scorer, health classifier), state JSON for hook + statusline polling. Deliberate separation across format × access pattern.

- **Explainable state machine as a first-class CLI surface** — `autotune explain` pipes `.autotune.state`, segment summary, and config through `lib/health.py --explain` and prints `Health / Mode / Failure / Action / Reason / Baseline / Best / Last / Streaks`. Not just a monitoring output — the agent is instructed (in `agents/autotune.md` "Tool Protocol → Explain Loop State") to call it on resume and after any ambiguity. Makes the state machine introspectable by the agent itself.

## 18. Gaps

- **Permissions mode on `bin/*` files not directly observed** — GitHub Contents API doesn't expose POSIX mode bits. Asserted 100755 for `bin/autotune` based on `package.json` `"bin"` declaration (npm requires executable), and for `.sh` siblings assumed 100644 (invoked via `bash <path>` from hooks and agent prompts, so executable bit not required). Would need `git ls-tree main -- bin/` or a local clone to confirm.

- **`bin/dashboard.sh`, `bin/init-experiment.sh`, `bin/run-experiment.sh`, `bin/log-experiment.sh`, `lib/git-ops.sh`, `lib/parse-metrics.sh`, `lib/confidence.py`, `lib/health.py`, full `lib/state.sh`** — not fetched (only head of `state.sh` read). Internal behavior of health state transitions, MAD scoring, git auto-commit/revert, and JSONL log schema is inferred from README/CLAUDE.md/agent.md prose rather than inspected. Budget-conscious sampling; resolve by fetching these files if they become relevant to a specific pattern axis.

- **Actual statusLine usage count in the wild** — `setup-permissions.sh` installs statusLine into `.claude/settings.local.json`, but whether users adopt it (vs. declining) is not observable from the repo.

- **Why version declared `0.3.0` but only `0.1.0` is tagged/released** — inferred as release-automation gap (no workflow) rather than intentional pre-release. No CHANGELOG, no commit message rationale beyond "bump version". Could be resolved by reading the two bump commits' diffs, but the rationale itself is not captured anywhere in the repo.

- **Whether `subagentStatusLine` is used** — searched via `gh api search/code` (0 hits); assumed absent. A deeper text search across all blobs (not just indexed code) was not performed. Likely negative given `setup-permissions.sh` only writes the top-level `statusLine` key, but not exhaustively verified.

- **Whether `claude plugin validate .` actually passes on current HEAD** — CLAUDE.md documents it as a manual step; not verified in this research pass. Would require running the CLI against a clone.
