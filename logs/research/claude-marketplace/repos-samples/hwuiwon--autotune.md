# Sample

Mirrors of `https://github.com/hwuiwon/autotune`. Single-plugin repo at `0.3.0` (tagged `0.1.0`) shipping a CLI plus Claude Code agent for autonomous benchmark-driven optimization loops — edit, benchmark, keep improvements, revert regressions, repeat.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root with one plugin entry pointing back at the same repo. Plugin name `autotune` matches the marketplace install command `/plugin install autotune@autotune`.

### Top-level `metadata` wrapper variants

`marketplace.json` carries metadata only inside `metadata.{description}` — `{"description": "Autonomous optimization loops for Claude Code"}`. No top-level `description`, no `version`, no `pluginRoot`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`source: "./"` — single plugin at repo root. README quick-start documents `/plugin install autotune@autotune`; the plugin name equals the marketplace name and relies on CLI disambiguation.

### `strict` field default

No `strict` key present in marketplace.json — implicit true.

## Per-plugin discoverability metadata

### Marketplace-entry facets plus duplicated keywords on plugin.json

Marketplace entry carries `category: "productivity"` plus `tags: ["autotune", "optimization", "benchmarking", "autonomous"]`. `plugin.json` carries the identical four-element `keywords: ["autotune", "optimization", "benchmarking", "autonomous"]` — same semantic list duplicated under two different field names across two files.

### `$schema` absence on per-plugin manifests

`$schema` is absent from both `marketplace.json` and `plugin.json`.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Users install via `/plugin marketplace add hwuiwon/autotune` with no `@ref` pinning documented. Single main-line distribution; no channel-pinning artifacts.

## Tag and release lifecycle

### Single lifetime tag with drift

`plugin.json` declares `0.3.0` but the only git tag is `0.1.0` at commit `92a348b` (with matching GitHub release). Subsequent bumps to `0.2.0` and `0.3.0` ship as untagged "bump version" commits (`b19d6b7`, `a08aab1`) on `main`. Marketplace installs pull HEAD (`0.3.0`); the GitHub Releases page advertises `0.1.0`.

## Version coordination

### Multi-artifact lockstep across N>2 manifests

Three files independently encode `"version": "0.3.0"` — `marketplace.json` plugin entry, `.claude-plugin/plugin.json`, and `package.json` (the latter for npm `bin` registration). No single source of truth, no derived secondary field, no enforcement gate; drift is possible across all three.

## Plugin-component registration

### Default convention discovery

`plugin.json` has no `components`, `skills`, `agents`, `hooks`, or `mcpServers` fields. Component directories (`agents/`, `skills/`, `hooks/`) are discovered by Claude Code's conventional layout under `CLAUDE_PLUGIN_ROOT`. `hooks.json` lives under `hooks/` not at plugin root.

### Hooks-json with broad event coverage

`hooks/hooks.json` wires `Stop` (auto-resume) plus `PreToolUse:Bash` (enforce `./autotune.sh` as benchmark target). No SessionStart hook is registered.

## Plugin-component placement

### Inside plugin directory

Plugin is a single tree at repo root; component dirs (`agents/`, `skills/`, `hooks/`, `bin/`, `lib/`) are inside the plugin directory.

## Component composition

### Skills (universal)

`skills/autotune/SKILL.md` — single skill providing the agent's playbook context.

### Agents

`agents/autotune.md` — single agent driving the optimization loop. Fields: `name`, `description`, `model: sonnet`, `tools: [Bash, Read, Write, Edit, Glob, Grep]` (YAML list form).

### Hooks

`hooks/hooks.json` registers a `Stop` hook (auto-resume budgeting) and a `PreToolUse:Bash` hook (benchmark-target validation).

### bin

Seven scripts: `autotune` (main CLI dispatcher with subcommands `start`, `stop`, `clear`, `dashboard`, `status`, `explain`, `repair`, `version`), `init-experiment.sh`, `run-experiment.sh`, `log-experiment.sh`, `dashboard.sh`, `setup-permissions.sh`, `statusline.sh`.

## Agent declaration conventions

### Standard fields plus model / color

The `autotune` agent declares `name`, `description`, `model: sonnet`, `tools` — model present but no `color` field. No orchestration knobs (`background`, `isolation`, `effort`, `maxTurns`).

### Plain tool-name list

`tools: [Bash, Read, Write, Edit, Glob, Grep]` as a YAML list — no permission-rule syntax like `Bash(uv run *)`.

## Dependency installation

### Zero dependencies / stdlib only

Per CLAUDE.md: "No external dependencies beyond Python 3 stdlib, git, and bash". Python files (`lib/health.py`, `lib/confidence.py`) use stdlib only. No `requirements.txt`, `pyproject.toml`, `Cargo.toml`, or `go.mod`. `package.json` exists but only declares the npm `bin` mapping plus `engines.node >= 18` — no `dependencies` or `devDependencies`. No SessionStart install hook. README "Requirements" lists Python 3.6+, Git, Bash but no runtime check enforces them.

## Install trigger and lifecycle

### No managed install — pure shell/markdown

No SessionStart-driven install. Runtime prerequisites (Python 3.6+, Git, Bash) are documented in README but not validated at session start or first invocation.

## Bin entry mechanism

### Multi-script bin family / CLI dispatcher

`bin/autotune` is the main entry point with subcommands `start`, `stop`, `clear`, `dashboard`, `status`, `explain`, `repair`, `version`; sources `$AUTOTUNE_HOME/lib/state.sh`. Sibling scripts: `init-experiment.sh` (initialize a session with metric name/unit/direction), `run-experiment.sh` (execute benchmark, parse `METRIC name=value` stdout lines, run checks), `log-experiment.sh` (append to `autotune.jsonl`, auto-commit or revert, compute confidence, classify health), `dashboard.sh` (terminal dashboard; `--watch` live mode, `--full` all experiments), `setup-permissions.sh` (writes scoped entries into target project's `.claude/settings.local.json`), `statusline.sh` (Claude Code `statusLine` command).

### POSIX shell wrapper with `${CLAUDE_PLUGIN_ROOT}` fallback

Shebang is `#!/usr/bin/env bash` uniformly. Every script computes `AUTOTUNE_HOME="${CLAUDE_PLUGIN_ROOT:-${AUTOTUNE_HOME:-$(dirname "$SCRIPT_DIR")}}"` so the same script works under plugin install, manual clone, or ad-hoc invocation. Scripts shell out to `python3` directly (no venv); only Python 3 stdlib is used.

### Plugin-bin + npm-bin dual-target

`package.json` declares `"bin": {"autotune": "./bin/autotune"}` so `npm install -g autotune` or `npx autotune` yields the same CLI exposed by `/plugin install`. `bin/autotune` calls `claude --agent autotune` from `cmd_start`, assuming `claude` is on `PATH`.

## Cross-platform discipline

### POSIX-only with no Windows story

Bash + python3 + git only. No `.cmd`/`.ps1` counterpart. macOS-aware: SKILL.md warns "no `grep -P` (macOS lacks Perl regex). Use `sed`, `awk`, or `python3 -c`".

## User configuration and authentication

### External config file owned by plugin

No `userConfig` block in marketplace.json or plugin.json. Configuration lives in a per-project `autotune.config.json` read at runtime by `lib/state.sh`'s `read_config`. Fields like `autoResume`, `maxIterations`, `health.*`, `recovery.*` live there. No `${user_config.KEY}` or `CLAUDE_PLUGIN_OPTION_*` usage. Stored alongside `autotune.md`, `autotune.jsonl`, `.autotune.state` so the whole session travels with the project.

## Tool-use enforcement

### PreToolUse as phase-scoped artifact gate

Single PreToolUse hook with matcher `"Bash"`. Intercepts Bash invocations referencing `run-experiment.sh`; when `autotune.sh` exists in the resolved workdir AND autotune mode is active, validates that the `--command` arg resolves to `./autotune.sh` after stripping `env`, `time`, `nice`, `nohup`, `timeout <n>`, `VAR=val ` prefixes. Self-arming around session artifacts rather than always-on. Blocks with exit 2 + stderr message on mismatch; passes through silently otherwise. The hook's purpose is benchmark-target enforcement — preventing the agent from drifting to ad-hoc commands mid-loop ("just run `pnpm test` this once") that would bypass the METRIC-parsing contract.

## Hook output contract

### Stderr for human display + stdout JSON for harness

Stderr human-readable on block (plain echoed message, no JSON); pass-through exits 0 silently. No structured JSON output emitted.

## Hook failure posture

### Fail-open with always-exit-0

Fail-open on parse errors — every `python3 -c` call that extracts JSON fields has `2>/dev/null || echo ""` fallback, so malformed hook input, missing `autotune.sh`, inactive autotune mode, or unparseable `--command` all proceed with `exit 0` (allow). Only explicit mismatch blocks. Uses `set -euo pipefail` plus per-statement `|| echo ""` fallbacks rather than a trap. The `--command` regex (`--command\s+["\']...["\']` with single-quote fallback, then unquoted `\S+`) is a best-effort parse; novel wrappers (`chrt`, `taskset`, `stdbuf`) would block legitimate invocations.

## Hook handler runtime

### Bash scripts at conventional path

Hook scripts under `hooks/` (e.g., `hooks/stop.sh` for auto-resume). Bash + `python3 -c` for JSON extraction.

## Session context loading

### No session-context loading

SessionStart is not registered at all. No `additionalContext`, no `systemMessage`, no `UserPromptSubmit`. Session resume context is loaded by the agent itself (`agents/autotune.md` "Session Resume Protocol" reads `autotune.md`, `autotune.jsonl`, `.autotune.state`, `autotune.ideas.md`) — resume only happens when the user launches the `autotune` agent explicitly.

## Live monitoring

### `monitors.json` absent

No `monitors.json`; no use of the Claude Code monitors system.

### Status line via user-settings mutation

`bin/statusline.sh` is a Claude Code `statusLine` command installed into the user's `.claude/settings.local.json` by `setup-permissions.sh`. Reads `.autotune.state` from disk and colorizes health state (`running`/`improving`/`plateaued`/`healing`/`crashing`/`paused`) with health icons (●/▲/◆/⚕/✖/⏸), experiment count, streaks, duration, cost, context %. Supports composition via `--chain <cmd>`: delegates the raw session JSON on stdin to a prior status line command (e.g., an existing HUD), then appends autotune's line. `setup-permissions.sh` auto-detects an existing `statusLine` in `~/.claude/settings.json` or project settings, wraps it via `--chain` when present, and emits the standalone form when absent — preserving prior configuration. No `subagentStatusLine` usage observed.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field on `plugin.json`. Single-plugin marketplace; no `{plugin-name}--v{version}` tag namespace.

## Testing

### No tests

No `tests/` directory, no test files in repo tree. CLAUDE.md "Testing" section lists manual validation commands only: `claude plugin validate .`, a spawn-from-`/tmp` plugin-dir check, and `uvx ty check lib/health.py` (astral-sh/ty type checker mentioned as ad-hoc validation, not wired into a workflow).

## CI workflow shape

### No CI

No `.github/` directory — `gh api repos/hwuiwon/autotune/contents/.github` returned 404. Nothing verifies version-bump → tag → install-pathway integration; failures show up on user `SessionStart` only. Version bumps ship without gate.

## Release automation

### No release automation / manual

No `release.yml` or equivalent. The sole GitHub release (`0.1.0`) appears to have been created manually; no automation artifact in the repo. Release cadence has fallen out of sync with main — `0.2.0` and `0.3.0` commits are untagged and unreleased, so users following GitHub Releases see stale versions while marketplace installs pull HEAD. No CHANGELOG.

## Marketplace validation

### Manual validation only

CLAUDE.md documents `claude plugin validate .` as a manual developer step; not gated in CI. Validation is documented but unenforced.

## Documentation surface

### Two-document model (README + CLAUDE)

`README.md` at repo root (~9 KB / ~220 lines) covers ASCII loop diagram, How It Works, What's Included, Quick Start, Monitor, Stop/Resume, Session Persistence, Confidence Scoring (MAD table), Health And Recovery, Backpressure Checks, Benchmark Script, Auto-Resume, Configuration table, CLI Reference, Architecture tree, Requirements, License. `CLAUDE.md` at repo root (1.6 KB) lists Project Structure, Conventions (bash `set -euo pipefail`, source `$AUTOTUNE_HOME/lib/state.sh`, `${CLAUDE_PLUGIN_ROOT}` convention, JSON-to-stdout for agent consumption, health-awareness principle, Python-only-for-math/JSON/health rule, no external deps), Testing. CLAUDE.md is the contributor-facing convention reference; README is the user-facing feature reference.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md`. No dedicated `architecture.md` even though README has enough internal detail (lib layer, JSON stdout protocol, health state machine) to justify one — README's "Architecture" section is a directory tree only.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

LICENSE present at repo root (MIT). SPDX `MIT` declared in `plugin.json`. Single source agreement across LICENSE file and manifest declaration.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md`. No badges or status indicators in README.

## Cross-ecosystem distribution

### Dual-distribution: marketplace + npm

Distributed both as a Claude Code plugin (via `/plugin marketplace add hwuiwon/autotune`) and as an npm CLI (via `npm install -g autotune` or `npx autotune` consuming `package.json`'s `"bin": {"autotune": "./bin/autotune"}` mapping). Same `bin/autotune` script serves both surfaces.

## Cross-role tools

### `${CLAUDE_PLUGIN_ROOT}` env var

Every bin script computes `AUTOTUNE_HOME="${CLAUDE_PLUGIN_ROOT:-${AUTOTUNE_HOME:-$(dirname "$SCRIPT_DIR")}}"`. The variable is the primary plugin-root resolution source.

### `plugin.json.version`

Declared at `0.3.0`; mirrored in `marketplace.json` plugin entry and `package.json`. No tooling reads it for staleness detection — only used for display.

### Python (stdlib + pip + uv)

Python 3 stdlib only — no venv, no pip, no uv at runtime. `uvx ty check lib/health.py` is mentioned in CLAUDE.md as an ad-hoc developer validation step.

### bash

Bash is the primary scripting runtime; all bin scripts and hooks use `#!/usr/bin/env bash` with `set -euo pipefail`.

## State persistence

### JSONL append-only event logs

`autotune.jsonl` is an append-only experiment log written by `log-experiment.sh`. Consumed by the dashboard, confidence scorer, and health classifier. Companion files: `autotune.md` (living prose document, human-facing), `.autotune.state` (current operating state JSON, polled by hook + statusline). Three-file separation across format × access pattern.

## Permission and contributor governance

### Repo-root .claude/settings.json — contributor-only permission matrix

`setup-permissions.sh` writes fifteen specific allow-list entries directly into the target project's `.claude/settings.local.json` — autotune script paths, `./autotune.sh*`, `./autotune.checks.sh*`, `git checkout -b autotune/*`, `git commit -m "autotune:*"`, scoped `git add`/`log`/`diff`/`status`/`rev-parse` — plus the statusLine block. Existing `permissions.allow` entries are preserved; duplicates skipped. Scoped allow-list-first permission grant rather than blanket `*` permission.

