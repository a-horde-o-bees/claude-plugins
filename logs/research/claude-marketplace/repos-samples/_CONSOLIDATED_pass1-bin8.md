# Sample

Pass-1 Phase-1a partial for bin 8. Functional decomposition of `SankaiAI--ats-optimized-resume-agent-skill`, `ShaheerKhawaja--ProductionOS`, and `SkinnnyJay--wiki-llm`, organized by role with implementation paths as sub-sections.

## Marketplace catalog declaration

Where the plugin's marketplace entry lives and how the catalog around it is shaped.

### Single-plugin marketplace at repo root

A `.claude-plugin/marketplace.json` at the repository root declares one plugin entry. The marketplace name is a thin wrapper around the plugin name (`<plugin>-marketplace`, `<plugin>-local`) — the catalog exists only to host this one plugin. Appropriate when the repo *is* the plugin and there is no broader catalog to participate in. Constrains channel distribution because there is no separation between marketplace metadata and plugin metadata; any pinning has to come from the plugin source rather than from the catalog. The "-local" suffix variant signals "developing in place" — users see the suffix in `/plugin install <name>@<marketplace>` and may not expect it. Marketplace-level `metadata` may include `description`, `version`, `homepage`, `repository`, `license` — present as a wrapper around the plugin entry.

## Plugin source binding

How the marketplace entry locates the plugin manifest.

### `source: "github"` with `ref` pinning

The marketplace entry references a GitHub repo by `repo` and `ref`. When `ref` is set to a moving branch (e.g. `main`), every install resolves to whatever tip-of-branch is at install time — no pin story, users always get latest. Implies `strict: true` (default) so the plugin manifest must live at the canonical `.claude-plugin/plugin.json` path inside the source. Appropriate when the repo is hosted publicly on GitHub and the plugin lives at its root; ill-suited for stable-channel delivery without separate tag/release coordination.

### `source: "./"` (relative, in-place)

The marketplace entry points at the same repo it lives in via a relative path, treating the entire repo root as the plugin tree. Discovery walks default directories (`skills/`, `commands/`, `agents/`, `hooks/`) unless overridden. Pairs naturally with single-plugin marketplaces where the catalog and the plugin share one repo. Appropriate when the plugin and its hosting marketplace are co-developed and the same repo will be cloned/installed wholesale. Constrains plugin layout: the whole repo becomes the plugin payload at install time, including non-plugin assets (docs, benchmarks, tests, templates) — plugins on this path either accept the bloat or ship their own slimming utility. With `strict: false` set explicitly, the entry permits components beyond canonical roots (root-level `CLAUDE.md`, `SKILL.md`, custom directories like `prompts/`, `algorithms/`, `templates/`). With `strict` left default-true, the manifest at `.claude-plugin/plugin.json` carries the entire registration burden.

## Channel distribution and version pinning

How users target a stable point in the plugin's history.

### No channel split (tip-of-main only)

Marketplace `ref` is a moving branch with no tags, no release branches, no pre-release suffixes — the plugin has only one channel and the channel is always latest. Appropriate at pre-release maturity where stability is not yet promised. Constrains release automation to nothing: there is nothing to gate, nothing to publish. Users cannot hold a known-good version; bumping any version string only renames the moving target. Multiple long-lived `feat/*` branches may exist as parallel-timeline development without ever being released.

### npm registry as de facto channel substrate

A Node-based installer (`bin/install.cjs`) is published to npm so users can `npx <plugin>@latest` or pin `npx <plugin>@<version>`. Versioning effectively delegates to npm's package versioning rather than git tags. Appropriate when the plugin has a Node toolchain anyway; constrains the plugin to publish releases to npm manually, parallel to the marketplace install path. Creates a third install channel alongside marketplace and direct-clone paths — same plugin, different version stories per substrate.

## Version authority

Which file is the single source of truth for the version string, and how many copies exist.

### Multi-file hand-synced versions

Two-to-five copies of the same version literal hand-maintained across `plugin.json`, marketplace entry, marketplace metadata, `package.json`, `pyproject.toml`, `.codex-plugin/plugin.json`, root-level `VERSION` file, and CHANGELOG. No automation enforces equality; drift is observed in practice (CHANGELOG top entry diverging from manifests during in-flight rebrands; pyproject Python-package version diverging from plugin version). Appropriate as a transitional state when consolidating onto a single source has not yet happened. A partial migration toward a single `VERSION` file read at runtime by hooks and bin scripts is a recognizable step on the path to centralization, but with manifest copies still hardcoded the drift surface persists.

### Stale fallback constants in code

Bin scripts and hooks read the `VERSION` file with a hardcoded fallback literal for "VERSION file unreadable" — but the fallback drifts from the current version over time, so a broken install displays a number that may be many versions out of date. A symptom of the multi-source version problem: even the centralization attempt embeds a copy.

## Plugin-component registration

How `plugin.json` exposes skills, commands, agents, and hooks.

### Default discovery (no path arrays)

`plugin.json` omits `skills`/`commands`/`agents`/`hooks` fields entirely; Claude Code auto-discovers from canonical directory names (`skills/`, `commands/`, `agents/`, `hooks/hooks.json`). Appropriate when the plugin's layout matches conventions; minimizes manifest verbosity. Cross-ecosystem pairs may diverge here: a Cursor manifest at the same repo declares every slot explicitly while the Claude manifest leaves them implicit, which means the same source tree exposes different registration shapes per ecosystem.

### Explicit path string for one component

`plugin.json` declares one component's path explicitly (e.g. `"skills": "./skills/"`) even when the path matches default discovery. Redundant but valid. Often appears alongside the default-discovery pattern when only one component needs a non-default location and the author opts to be explicit about all of them.

### Explicit path arrays per agent

`plugin.json` declares each agent file by relative path in an array (80+ paths visible in one sample). Used when agent count is large and the manifest is treated as the authoritative inventory. Mismatches between the array and filesystem (e.g. one extra unreferenced agent file) become discoverable drift signals. Pairs with custom agent frontmatter conventions (`subagent_type`, `stakes`) where the author wants the inventory written down rather than discovered.

### Custom agent frontmatter extensions

Standard fields (`name`, `description`, `model`, `tools`) coexist with non-standard ones — `stakes` (low/medium/high, borrowed from the 12-Factor-Agents discipline), `subagent_type` namespaced as `<plugin>:<name>`, plus `effort`, `maxTurns`, `disallowedTools`, `color`, `memory`. The plugin's internal readers consume these; the harness ignores them. Appropriate when the plugin has internal agent-orchestration logic that needs richer per-agent classification than the harness provides. Constrains portability: validators that enforce only the canonical schema reject these, so the plugin maintains its own validators.

## Dependency installation

How runtime dependencies reach the user's machine.

### First-run pip-install in bin wrapper

The bin wrapper probes for a Python module (`python -c "import <module>"`) and on ImportError runs `pip install <pkgs> --quiet` against whatever `python`/`pip` are on PATH. No venv, no version pinning, no lockfile, no change detection beyond existence. Appropriate as the minimum viable Python-dep-install pattern. Constrains everything else: dependency isolation becomes the user's problem; PEP 668 externally-managed-environment errors surface to the user rather than being handled; `python` (vs `python3`) PATH assumptions break on Linux distros that ship only `python3`. Idempotent by retry (every invocation re-probes) but not hook-driven. The `.cmd` Windows counterpart cannot replicate `set -e` and silently swallows failed installs.

### Manual venv with documented commands

The plugin documents `python3 -m venv .venv && .venv/bin/pip install -r requirements-optional.txt` in README/CLAUDE.md and ships no auto-install mechanism. Optional deps live in `requirements-optional.txt` with a header explicitly invoking PEP 668. Appropriate when the dep surface is large, version-sensitive, and the author refuses to pollute the user's environment. Constrains user experience: "plugin installed" diverges from "plugin functional" — features silently degrade when optional deps are missing (e.g. ChromaDB falls back to grep). The plugin must tolerate every dep being absent.

### Bun install via Node packaging

`package.json` plus `bun.lock` declare Node deps; the npm-published installer runs `bun install` into the installer's working directory. Plugin-marketplace installs do NOT run `bun install` — only the npm install path does. This means features gated on `node_modules/` (Ink TUI, dashboards) silently fall back to plain text on a marketplace install. Appropriate when Node is the primary toolchain and npm is the distribution substrate; constrains the marketplace path to graceful degradation for everything Node-dependent.

### Inline `python3 -c` for ad-hoc scripting

Bash hooks pipe data through `python3 -c "..."` for JSON manipulation rather than declaring a Python dep. Relies on system Python 3 being present. Appropriate for tiny one-shot transformations in shell hooks; constrains the plugin to whatever standard library the system Python provides.

## CLI distribution via bin wrappers

How plugin code is exposed as a command-line entry point.

### POSIX shell wrapper with `${CLAUDE_PLUGIN_ROOT}` fallback

A short `bin/<plugin>` script resolves the plugin root via `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}` (or `sh`-portable equivalent using `dirname "$0"`), then `exec`s the underlying interpreter on a script inside the plugin. The fallback makes the same script work under Claude Code (env var set) and from a bare clone (env var unset) with no other changes. Canonical pattern, observed verbatim across multiple samples. Shebang varies: `#!/usr/bin/env bash` is typical; `#!/usr/bin/env sh` appears when the wrapper is intentionally bashism-free. POSIX-only — Windows requires a separate `.cmd` or `.ps1` pair. `CDPATH= cd --` guards against hostile `CDPATH` and dash-prefixed paths in the fallback branch.

### Bash + `.cmd` pair for cross-platform

POSIX `.sh`/no-extension bash wrapper plus a Windows `.cmd` batch file with the same behavior — `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..` for runtime resolution, `%PYTHONPATH%`, `%*` argument passthrough. PowerShell `.ps1` is not used as a runtime shim — only as a one-shot installer when present. Appropriate for plugins that genuinely target both platforms; constrains feature parity because `.cmd` cannot replicate `set -euo pipefail` and error handling diverges.

### Multi-script bin family

A `bin/` directory contains many small per-purpose scripts (`pos-init`, `pos-config`, `pos-analytics`, `pos-sync`, `pos-telemetry`, `pos-update-check`, plus a Node installer) rather than one entry point. Each script handles one verb; hooks invoke them via full path. Appropriate when the plugin exposes a CLI surface with many independent operations to user and to internal hooks. Constrains permissions discipline: scripts invoked by full path do not require executable bits, so chmod handling is inconsistent (the npm-`bin`-declared file gets chmod from npm; sibling scripts do not).

### Stale hardcoded paths after rebrand

A bin script targets a hardcoded path under `~/.claude/plugins/cache/<old-slug>/<old-slug>/<old-version>` rather than resolving via `CLAUDE_PLUGIN_ROOT`. After a project rebrand, the path is stale and the script silently no-ops. A refactor-rot signal: any bin script with a hardcoded cache path is a candidate for the env-var-resolution pattern.

### Single-file install + skill copy via standalone installer

`install.sh` / `install.ps1` at repo root for non-plugin install methods runs `pip install <subdir>/` and copies the canonical `SKILL.md` into the user's skills directory. Independent from the plugin-marketplace install path: same source tree, two install mechanisms, two copies of `SKILL.md` (root copy for standalone-install consumers; `skills/<name>/SKILL.md` for plugin-install consumers) maintained in parallel. Appropriate when the author wants to support both Claude-Code-plugin-installed users and standalone-skill-copy users from one repo; constrains single-source-of-truth because the same content must land in two places.

## User configuration

How user-supplied values reach the plugin at runtime.

### Native `userConfig` with `sensitive: true`

`plugin.json` declares a `userConfig` object with typed string fields, each with `title`, `description`, and `sensitive: true` for secrets. The Claude Code config UI discovers and edits these. Appropriate for API keys, tokens, and other per-user settings the harness can collect once and inject. Constrains the manifest to keep secret fields flagged correctly and the plugin code to read from the harness-provided env (e.g. `CLAUDE_PLUGIN_OPTION_*`) rather than `.env` files. Cross-ecosystem deployments may duplicate the `userConfig` block verbatim into the Cursor manifest with no sync mechanism — drift risk identical to the version-string problem.

### Plugin-managed JSON file with custom CLI

The plugin writes a settings JSON under a plugin-chosen path (`$HOME/.<plugin>/config/settings.json`) and provides a `<plugin>-config get/set/list` bin tool with an internal allowlist of legal keys. The Claude Code config UI does not see these settings. Appropriate when the plugin needs configuration semantics richer than the native `userConfig` (e.g. cross-session, cross-project, cross-tool sharing or behavior toggles like `proactive`, `auto_review`, `self_eval`). Constrains discoverability: users must learn the bin CLI; validation duplicates work the manifest schema would provide.

### No user-supplied config

The plugin takes all inputs via conversational flow or file-path arguments to the CLI. No `userConfig`, no settings file. Appropriate when the plugin is fully driven by per-invocation arguments and has no per-user secrets or preferences.

## Tool-use enforcement hooks

How the plugin gates Claude Code's tool calls.

### PreToolUse guard set with multi-matcher concurrency

`hooks/hooks.json` declares multiple matcher blocks. One matcher (broad — `Edit|Write|Bash|NotebookEdit|mcp__filesystem__*`) runs a scope-enforcement script. A second matcher (`Edit|Write|Bash`) runs three guards in parallel: repo-boundary, protected-file, pre-edit-security. A third matcher (`Bash` only) runs a secret-scanner (gitleaks). Appropriate when policy is composable across orthogonal concerns (scope vs boundary vs security vs secrets). Constrains performance: every gated tool call waits on the slowest concurrent guard; deduplication across hooks is the author's responsibility.

### PostToolUse async telemetry + eval gate

A matcher block runs four async post-edit scripts on every Edit/Write: self-learn, telemetry, review-hint, eval-gate. A separate matcher emits async post-bash telemetry. The async modifier prevents tool-call latency but leaks background processes if the user exits mid-call. Appropriate when the plugin layers on cross-session learning, analytics, and self-evaluation; constrains process hygiene because nothing reaps the async children.

### Stop-event handlers for session-end aggregation

Stop hooks (multiple, e.g. session-handoff, instinct-extraction, eval-gate finalization) run when the session ends. Each one aggregates JSONL events the PostToolUse hooks emitted during the session into summaries or longer-term stores. Appropriate when the plugin maintains durable cross-session state and needs a deterministic place to consolidate it; constrains start-of-session UX because the consolidated view is only refreshed on Stop, not on session open.

### Skill-level gating with no runtime hooks

The plugin omits hooks entirely and relies on the SKILL.md's workflow steps to enforce policy. Appropriate when the workflow is purely conversational and the gates are decisions the agent makes during step execution; constrains enforcement to whatever the agent honors voluntarily.

### Fail-open posture with explicit comment contract

Every shell hook begins with a comment declaring the contract ("Exit code MUST be 0 always — a failing hook must not interrupt Claude") and uses `set -euo pipefail` plus `|| true` on every external call, terminating with `exit 0`. Selective failure: a typo outside a command path still halts; CLI failures are swallowed. Appropriate when hook reliability matters more than hook correctness — the author would rather miss telemetry than block the user. Constrains visibility: silent swallowed failures need an out-of-band log (`hook-errors.log` written by an `_log_error` helper) to diagnose.

## Session context loading

How the plugin injects content at session boundaries.

### SessionStart banner with runtime probes

A SessionStart hook with matcher covering all four sub-events (`startup|resume|clear|compact`) emits a banner showing agent/command/hook counts, project name, version, etc. Implementation probes for a TUI framework (bun + Ink) at runtime, falling back to plain text when unavailable. Output goes to stdout as a printed banner, not via the structured `hookSpecificOutput.additionalContext` channel. Appropriate when the plugin wants a consistent visible-on-every-session presence; constrains performance (every session pays the probe cost) and may include intrusive defaults like auto-launching a GUI app when a config flag is set.

### No SessionStart, only PreCompact / PostCompact / Stop / SessionEnd

The plugin registers compact-cycle and end-of-session hooks but no SessionStart. Inbound context is instead loaded on demand via slash commands. Appropriate when the plugin's context shape is determined by user intent at session start rather than baked-in defaults; constrains first-session-after-gap UX because cross-session memory is only refreshed on Stop, not at the next session's open.

### No hooks at all

A single-skill plugin loads context via SKILL.md frontmatter description matching only — the harness reads the description and decides whether to invoke. Appropriate for narrow-purpose plugins that do not maintain cross-session state.

## Persistent state location

Where the plugin keeps cross-session data.

### Plugin-chosen `$HOME/.<plugin>/` with override env var

A plugin-named state directory under the user's home (e.g. `$HOME/.<plugin>/`) holds config, analytics, sessions, and other durable state. An override env var (`<PLUGIN>_HOME`) lets users relocate it. Appropriate when state is meant to survive across projects, across Claude Code reinstalls, and across cross-tool deployments (Claude + Codex sharing one state dir). Constrains backup and discovery: not where users expect plugin data per Claude Code conventions, so docs must call out the location explicitly.

### Plugin-managed file location, no convention

State files (JSONL telemetry, learning logs, session timelines) live under the plugin-chosen `$HOME` path rather than `${CLAUDE_PLUGIN_DATA}`. The plugin's bin tools read/write directly. Appropriate for the same cross-tool-sharing rationale; constrains visibility because the Claude Code harness has no awareness of these files.

## Telemetry and self-evaluation

How the plugin records its own operation and grades its own output.

### JSONL append-only event logs

Telemetry, analytics, learnings, review events, and timeline entries are written as JSONL append-only files under the plugin's state directory. Bin tools (`<plugin>-telemetry`, `<plugin>-learnings-log`, `<plugin>-learnings-search`) emit and query these. Appropriate for a plugin that wants durable cross-session memory; constrains rotation and retention (no auto-pruning visible) and creates a deduplication problem when multiple async hooks may write the same event.

### Eval-gate as a CI job

CI runs the plugin's own evaluation harness (`bun run eval` or equivalent), parses score and critical-finding count out of stdout via grep, and fails the build on any critical findings. The plugin grades its own artifacts against its own rubrics on every push. Appropriate when the plugin's purpose is review/judging and the author wants meta-coverage; constrains stability because grep-of-stdout is brittle to eval output format changes and shifts to structured output (JSON exit) would harden the gate.

## Live monitoring

Whether the plugin participates in the monitors feature.

### Absent

`monitors.json` is not present. Some plugins implement equivalent functionality via Stop/PostToolUse hooks emitting JSONL events; others have no live-monitoring concept. Appropriate when notification semantics are not relevant to the plugin's purpose.

## Plugin-to-plugin dependencies

Whether the plugin declares dependencies on other plugins.

### Absent

The `dependencies` field is not used. Single-plugin marketplaces with no cross-plugin coupling are the dominant shape in this bin. The `<plugin-name>--v<version>` git tag format (the cross-plugin pinning mechanism) is consequently not exercised — plugins without releases at all cannot participate in cross-plugin pinning by tag.

## Testing framework

How the plugin's deterministic tests are organized.

### pytest with sys.path manipulation

`tests/` directory holds pytest test files; tests manipulate `sys.path` via `sys.path.insert(0, str(ROOT))` to locate the source tree because no installed-package layout is assumed. Pytest config may live in a dedicated `pytest.ini` (with `testpaths`, `python_files` patterns, custom markers like `network`, `claude`, `replay`, `browser`) or be omitted entirely. Appropriate when the plugin has Python code and the author wants tests to run against source, not the installed copy. Constrains debuggability: install-path bugs (e.g. console-script vs PYTHONPATH-pointed-at-src divergence) hide because tests bypass the install path.

### bun test with TypeScript

`bun test` (Jest-compatible runner) executes `*.test.ts` files in a flat `tests/` directory. Appropriate for Node-toolchain plugins; constrains runner choice (locks the project to bun rather than node+jest or vitest).

## CI gating

What CI verifies on push and pull request.

### Single-workflow validate + lint + eval-gate + convergence

One `ci.yml` runs four jobs: validate (install + skill checks + schema-validation + full test), lint (strict `tsc --noEmit`), eval-gate (self-eval grader), convergence (custom convergence test). Triggered on `push` and `pull_request` against `main`. Single OS, single runtime version pinned. Action versions tag-pinned (no SHA pinning). Appropriate when the plugin has many in-repo validators it wants to gate centrally; constrains supply-chain hygiene because tag-pinned actions can be moved by their authors.

### Multi-workflow with pytest matrix and security scan

Tests run against a Python version matrix (`3.12`, `3.14`); a separate `security.yml` runs `gitleaks/gitleaks-action@v2` on push and PR; a tag-triggered `release.yml` re-runs tests on `v*` tag pushes. Appropriate for Python-toolchain plugins that want to catch version-specific breakage early. Constrains workflow maintenance because the same checks duplicate across files.

### No CI

`.github/workflows/` does not exist. Appropriate at pre-release maturity; constrains everything else because version drift, doc drift, and install-path drift are never caught automatically.

## Release automation

How releases are produced and gated.

### None — manual everything

No release workflow, no automated `gh release create`, no marketplace publish. The CHANGELOG (when present) is human-maintained. Appropriate when the plugin has no released versions and the author has not yet committed to a release process; constrains user trust because there is no signed/dated artifact.

### Tag-triggered test verification only

A `release.yml` workflow triggered on `push: tags: ['v*']` re-runs tests but does not build artifacts, create GitHub releases, or publish anywhere. The workflow header explicitly disclaims: "manual marketplace steps still required." Appropriate as a sanity check over manual releases; constrains the release process because tag-on-main verification, version-equality checks, and tag-format regex are absent — a tag from any commit passes if tests pass.

## Marketplace validation

Whether plugin/marketplace/hooks JSON conform to schema.

### In-CI custom validators

Validation is a job in the main CI workflow rather than a standalone workflow. Implementation is in-repo TypeScript or Python validators (`scripts/skill-check.ts`, `scripts/validate-agents.ts`, `scripts/<cli>.py check --plugin-repo`). These enforce both standard schemas and plugin-internal extensions (custom frontmatter fields). Appropriate when the plugin's manifest extensions exceed what `claude plugin validate` covers; constrains shareability because validators are not published as a reusable tool — they live and die with this repo. Passing here does not equate to passing the canonical CLI validator.

### Absent

No validation tooling. Schema problems (e.g. placeholder `owner.email: "your-email@example.com"` shipped to production) survive into published manifests because nothing checks them. Appropriate as a transitional state at pre-first-release; constrains correctness once the plugin is live.

## Documentation surface

What docs ship at the repo root for users and agents.

### `README.md` plus minimal companions

README covers install, usage, configuration; LICENSE present; PRIVACY or similar selectively included. Single-skill plugins consolidate everything into one README plus the SKILL.md. Appropriate for narrow-purpose plugins; constrains progressive disclosure because the README has to carry both consumer-onboarding and operational reference.

### Sprawling root with many entry-point markdowns

17+ top-level files including README, CHANGELOG, ARCHITECTURE, CLAUDE.md, SKILL.md, SKILL_REGISTRY.md, AGENTS.md, ETHOS.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, LICENSE, VERSION, plus tooling configs. Appropriate for plugins with substantial internal complexity that need multi-perspective entry points; constrains discoverability because the root becomes a kitchen-sink and roles overlap (CLAUDE.md vs SKILL.md at the same level signals conflated governance).

### Nested `docs/` tree with map in README

A `docs/` directory holds `QUICKSTART.md`, `INSTALL.md`, `CLI.md`, `CONFIGURATION.md`, `ENV.md`, `SLASH-COMMANDS.md`, `PUBLISHING.md`, `QAPLAYBOOK.md`, etc. The README contains a "documentation map" table that routes readers to the right doc. Appropriate when the plugin has many distinct user concerns each warranting their own page; constrains link discipline because case-mismatch bugs (`docs/architecture.md` on disk vs `docs/ARCHITECTURE.md` in a link) only surface on case-sensitive filesystems.

### Agent-targeted install preamble in README

The README opens with a blockquote-rendered "For AI Coding Agents — Read This First" section containing literal shell commands segmented by OS × scope × agent (Claude Code, Cursor, Codex, OpenClaw). When a user asks their coding agent to install the plugin, the agent fetches the README and gets an unambiguous install recipe at the top. A distinct consumer surface from the human-facing install sections elsewhere in the README — the same install intent encoded twice. Appropriate when agent-driven installs are a major install vector.

### Bilingual content

README is explicitly bilingual (English + Chinese, with anchor-linked language sections). Uncommon in Claude Code plugin READMEs; signals community reach.

## Agent-docs synchronization

How `CLAUDE.md`, `AGENTS.md`, and similar parallel agent-facing files stay in sync.

### Shared block with marker-bracketed sync

A canonical `docs/AGENTS.shared.md` is the single source; a `sync_agent_docs.py` script propagates it into `CLAUDE.md`, `AGENTS.md`, and a Cursor `.mdc` rules file between `<!-- BEGIN AGENTS_SHARED -->` / `<!-- END AGENTS_SHARED -->` markers. CI enforces with `--check` mode. Appropriate when the same agent guidance must reach multiple ecosystems verbatim. Constrains: any unique-per-tool content must live outside the markers in the destination file.

### Hand-maintained parallel files

`CLAUDE.md` and `AGENTS.md` exist at the same level with no sync mechanism. Appropriate when the two files diverge intentionally; constrains because drift is silent until a reader notices.

## Cross-ecosystem distribution

How the plugin targets multiple agent CLIs from one repo.

### Parallel manifests for Claude + Cursor + Codex

The repo ships `.claude-plugin/marketplace.json`+`plugin.json`, `.cursor-plugin/plugin.json` (richer — explicit component paths, `displayName`, `publisher`, `logo`, `category`, `tags`), `.codex-plugin/plugin.json` or `.codex/config.toml`, plus an `AGENTS.md`. Each ecosystem reads its own manifest. Appropriate when the plugin's value is portable across agent CLIs and the author commits to maintaining each surface. Constrains because configuration that should be shared (`userConfig`, version strings, skill paths) is duplicated across manifests with no sync — drift surface scales with ecosystem count. A build script (`scripts/gen-targets.ts`) may regenerate mirrored skill content into `.claude/skills/`, `skills/`, `codex-skills/`, but a hand-edited mirror is the default starting point.

### Skill content mirrored under multiple paths

The same skill files appear under `.claude/skills/`, top-level `skills/`, and `codex-skills/`. A regeneration script copies between locations. Appropriate when each ecosystem expects a different canonical path; constrains because hand-edits to one location must be regenerated to the others.

## Plugin-runtime root resolution

How bin scripts and hooks find the plugin's installed location.

### `${CLAUDE_PLUGIN_ROOT}` env var with script-relative fallback

Bash scripts use `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}`; sh scripts use `dirname "$0"`-based equivalents; cmd files use `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..`. Canonical pattern across all bin and hook scripts in a sample. The fallback enables raw-clone development without invoking through Claude Code. Appropriate as the single resolution mechanism; deviations (hardcoded cache paths) are refactor-rot.

## Pre-commit and pre-push hooks (git)

Whether git hooks enforce discipline at commit time.

### `.pre-commit-config.yaml` with linters only

Pre-commit hooks run `ruff --fix` on script directories and `python3 -m compileall` on Python source. No version manipulation, no manifest validation. Appropriate as a low-overhead floor; constrains because anything beyond syntax+style (version sync, manifest schema) is left to CI.

### Absent

No git hooks committed. Appropriate at pre-release maturity; constrains because manifest drift and version drift have no commit-time gate.
