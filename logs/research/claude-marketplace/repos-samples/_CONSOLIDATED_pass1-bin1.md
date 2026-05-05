# Sample

Pass-1 Phase-1a partial for bin 1. Functional decomposition of `123jimin-vibe/plugin-prompt-engineer`, `777genius/claude-notifications-go`, and `AgentBuildersApp/eight-eyes`, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

Where the marketplace-discovery JSON lives in the repo, and how it relates to the plugin(s) it advertises.

### No marketplace manifest (single-plugin repo)

The repo publishes a plugin only — there is no `.claude-plugin/marketplace.json` anywhere. The plugin's own `.claude-plugin/plugin.json` is the only manifest present. Consumers wishing to install the plugin via marketplace tooling must add the repo with an explicit subdirectory pointer (the plugin may live under a non-root path such as `plugin/` rather than at repo root, which forces a `path` argument in the marketplace `source:` they author elsewhere). Appropriate when the author does not want to maintain a marketplace surface or expects discovery to happen through a separate aggregator marketplace; the trade-off is no self-advertised category, tags, or version metadata at the marketplace layer.

### Single root manifest pointing at "./"

A single `.claude-plugin/marketplace.json` at repo root, with one plugin entry whose `source` is `"./"` — the marketplace and its sole plugin share the same repo root. The marketplace manifest declares `metadata.{description, version}` and one entry in `plugins[]` pointing back at the same root. Appropriate when one repo ships exactly one plugin and the author wants the repo itself to be installable as a marketplace. The arrangement implies that the repo name, the marketplace name, and the plugin name often coincide, which can produce visually confusing install strings (e.g. `<name>@<name>`).

### Duplicate manifest copies (canonical + vestigial)

Two `marketplace.json` copies coexist — a canonical one at `.claude-plugin/marketplace.json` and a duplicate elsewhere in the repo (e.g. `.github/plugin/marketplace.json`) — with identical content but no sync mechanism in hooks or CI. Only the canonical path is consumed by Claude Code; the duplicate appears to be aspirational (aimed at an alternate discovery surface like GitHub Pages or a different host CLI) or vestigial. Both files may carry unofficial private keys (e.g. `_description`) outside the documented schema. Appropriate to flag as an anti-pattern: it doubles the manual-edit burden during a release with zero observable upside.

## Per-plugin discoverability metadata

Fields in `plugin.json` (and mirrored on the marketplace entry) that drive search, categorization, and listing.

### Minimal metadata only (name, description, version)

The plugin advertises only `{name, description, version}` in `plugin.json` — no `category`, `tags`, `keywords`, `author`, or `repository`. Appropriate for early-development or stub plugins where discoverability is not yet a concern; the cost is zero presence in any category-based or tag-based marketplace browsing.

### Rich metadata (category + tags + keywords + author + repository + license)

The plugin declares `category` (single string), `tags` (array), and `keywords` (array) at both the plugin layer and the marketplace-entry layer, plus `author`, `repository`, and `license`. Tags and keywords overlap heavily — `keywords` is documented elsewhere as redundant with `tags` and has been pruned from sibling configs in the past, but persists here at the marketplace level. Appropriate for plugins seeking maximum discoverability across all known surface; the cost is a duplication burden when the marketplace entry mirrors fields already in `plugin.json`.

### `$schema` declaration

Absent in all observed samples — neither marketplace.json nor plugin.json declare `$schema`, so editors do not get autocomplete or validation against a known schema. Appropriate to flag as a uniform gap.

## Plugin source binding

How a marketplace entry locates the plugin it advertises (relative path, github coords, subdirectory pointer).

### Relative source ("./")

The marketplace entry uses `"source": "./"` because the marketplace and the plugin share a repo root. Trivial to author and audit; works only when the repo hosts exactly one plugin at root.

### Subdirectory pointer (no marketplace, consumer-authored)

When the plugin lives under a non-root path (e.g. `plugin/`) and no marketplace.json exists in the same repo, any external marketplace that lists this plugin must author a `source: { source: "github", repo: "<owner>/<repo>", path: "<subdir>" }` (or equivalent) entry by hand. Appropriate when the author wants to publish a plugin from a non-conventional layout but accepts that downstream marketplaces carry the binding logic.

## Version authority and synchronization

Where the version string of record lives, and what other sites must mirror it.

### Single authoritative `plugin.json.version`

`plugin.json.version` is the only user-facing version of record. A `pyproject.toml` may carry its own `version` field that drifts (e.g. frozen at `0.0.1` while plugin.json advances) — not consumed by anything user-facing, only by pip metadata, so the drift is immaterial. Tags use plain `vX.Y.Z` matching `plugin.json`. Appropriate for repos with a single user-facing version surface.

### Triple-write across marketplace.json + plugin.json (manual lockstep)

Three separate write sites carry the same version string: `marketplace.json metadata.version`, `marketplace.json plugins[i].version`, and `plugin.json version`. No tooling enforces agreement; release discipline is "edit all three, push, tag." Drift risk is real. Appropriate only when manual checklists are reliable; otherwise a CI gate or a script that reads one site and writes the others would close the drift window.

### Multi-site drift (alpha vs stable)

Five-or-more sites advertise different versions intentionally or accidentally: `plugin.json` and `VERSION` and `pyproject.toml` and CHANGELOG and the git tag may all be at one version (e.g. `5.0.0-alpha`) while the `marketplace.json` entries lag at the previous stable (e.g. `4.2.0`). The pattern can be deliberate ("marketplace only advances at stable release") or accidental drift. Pre-release suffix handling (semver vs PEP 440 vs tag) compounds the inconsistency: `5.0.0-alpha`, `5.0.0a1`, and `v5.0.0-alpha` are three forms of the same version that downstream sorting rules may not reconcile. Appropriate to flag as a category-of-failure across plugins that lack a release-automation gate.

## Channel distribution

Whether the repo carves stable / latest / dev channels, or ships a single line.

### Single line (no channel split)

The repo publishes a single version line; users pin via marketplace `@ref` (`@main` for rolling, `@vX.Y.Z` for a specific tag, or a commit SHA for frozen). No `stable-*`/`latest-*` pair, no parallel branch maintained as a release lane. Appropriate for plugins whose author is comfortable with `@main` being the dev channel and tag pins being the stable channel; the cost is no easy "give me the last known-good" label without naming a specific tag.

### Linear `0.0.z` dev counter

The repo's only versioning scheme is a monotonic `0.0.z` counter — every tag bumps `z`, with no `0.1.0` carve-out and no parallel `x.y.z` release lane. Tags `v0.0.1`..`v0.0.z` chain linearly on `main`. Appropriate for pre-release / experimental plugins where every commit is essentially a dev snapshot; the cost is no signal of stability and no inflection point to mark "first real release."

## Tag placement and branching strategy

Whether tags sit on `main`, on release branches, or some combination.

### Tag-on-main, single branch

All version tags sit on `main`'s linear history; no `release/*` branches exist. Feature branches (`feat/*`, `fix/*`, `chore/*`) merge to `main` via PR; a tag is cut from `main`; release automation (if any) fires on tag push. Appropriate for small-team or single-maintainer repos where the simplicity of one branch outweighs the safety of release branches; the cost is no isolated lane to backport fixes against a previously-shipped version.

### Tag-on-main with stale side branch

The dominant pattern is tag-on-main, but a side branch (`vX.Y/<topic>`) exists alongside `main` without serving as a long-lived release channel — it looks like an in-flight feature branch that was pushed and not deleted. Appropriate to flag as messiness rather than a deliberate channel pattern: users on `main` get the alpha; the side branch isn't a stable fallback.

### Pre-release tag suffixes

Tags carry a `-alpha` / `-beta` / `-rc` suffix to mark pre-release status (e.g. `v5.0.0-alpha`). GitHub Releases marks the corresponding release `prerelease: true`. PEP 440 form (`5.0.0a1`) appears on `pyproject.toml` for Python tooling compatibility. Appropriate when an author wants to ship versioned snapshots without claiming stability; the cost is uncertain handling by Claude Code's plugin semver parser, which is undocumented for pre-release suffixes — `5.0.0-alpha` may sort below `4.2.0` under naive string comparison.

## Component registration in `plugin.json`

How `plugin.json` declares (or omits) the plugin's components.

### Default discovery (no arrays declared)

`plugin.json` contains only top-level metadata (`name`, `description`, `version`); components are discovered by convention from sibling directories at the plugin root (`skills/`, `commands/`, `agents/`, `hooks/`). Appropriate for plugins that follow the convention exactly; the cost is no way to exclude a file from discovery or to override discovery order without restructuring the directory.

### Explicit path arrays (commands)

`plugin.json` declares `commands: ["./commands/<name>.md", ...]` listing each command file by relative path. Other components remain discovered by convention. The explicit list creates ambiguity about whether it is authoritative or additive — orphan files in `commands/` may or may not be exposed depending on host behavior. Appropriate when an author wants to deprecate or hide a file without deleting it; the cost is the orphan-detection burden during refactors.

## Component types observed

What kinds of components appear at the plugin root, alongside `plugin.json`. Cross-listing here lets later roles reference each component type by name.

### Skills

Skill directories under `skills/<name>/` containing a `SKILL.md` plus optional supporting files (`scripts/`, `references/`, `schemas/`). Used to encapsulate workflows the agent invokes by slash command or by intent match. SKILL.md may reference plugin-venv Python scripts via `${CLAUDE_SKILL_DIR}/scripts/<name>.py` and `${CLAUDE_PLUGIN_DATA}/venv`.

### Commands

Markdown files under `commands/<name>.md` defining slash commands. May carry YAML frontmatter (`description`, `allowed-tools`) where `allowed-tools` is a plain tool name like `Bash` rather than the permission-rule syntax. Some plugins list each command file in `plugin.json`; others rely on directory-globbing discovery.

### Agents

Markdown files under `agents/<name>.md` with YAML frontmatter declaring the subagent. Frontmatter fields range from minimal (`name`, `description`, `model`) to rich (`tools` as comma-separated tool names, `background: true`, `isolation: worktree`, `effort: low|medium`, `maxTurns: <n>`). Agents that are "thin" delegate work to skills; agents that carry instructions hold the workflow inline. Some frontmatter fields (`isolation`, `background`, `effort`, `maxTurns`) are not in the public Claude Code plugin reference — whether the harness honors them is uncertain.

### Hooks

`hooks/hooks.json` registering callbacks for events: `SessionStart`, `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, `SubagentStop`, `TeammateIdle`, `UserPromptSubmit`. Each entry declares a `matcher` (event sub-type, tool-name pattern, or compound pattern) and a `command` to run. Optional fields include `timeout` (seconds), `statusMessage` (shown during execution), and `async` (run without blocking).

### Bin scripts

`bin/<name>.sh` or `bin/<name>` shell scripts shipped inside the plugin cache. Used as wrappers, installers, or validators — not exposed as plugin CLI verbs in observed samples. Some are POSIX `/bin/sh` for hot-path use; others are bash with `set -euo pipefail` for one-shot use.

### Components absent in the bin

Several component types declared by Claude Code's plugin schema do not appear in any observed sample: `.mcp.json`, `.lsp.json`, `monitors.json`, output-styles. Their absence across the bin is itself a signal — not because they are deprecated, but because the observed plugins solve their problems through hooks and skills instead.

## Agent frontmatter shape

YAML fields declared on agent markdown files, beyond the documented base.

### Minimal frontmatter (name, description, model)

Only `name`, `description`, and `model` declared. `model: inherit` is common — defers to whatever model the parent session uses. No `tools`, no scope or behavior fields. Appropriate for thin agents that exist only to be entered into a routing decision; all behavior comes from skills they invoke.

### Tools-scoped frontmatter (tools as plain comma-separated list)

`tools` declared as a comma-separated list of plain tool names (`Read, Glob, Grep, LS, Bash`). No permission-rule syntax (`Bash(uv run *)` etc.) — Bash scoping, when needed, is enforced elsewhere (PreToolUse hook). Appropriate when the agent has a clearly-scoped role and the tool list serves as documentation as much as enforcement.

### Rich behavior frontmatter (background, isolation, effort, maxTurns)

In addition to the documented fields, agents declare `background: true` (run in background), `isolation: worktree` (per-role git-worktree isolation), `effort: low|medium` (host-specific scheduling hint), and `maxTurns: <n>` (cap on agent turns). These fields are not in the public Claude Code plugin reference; whether the harness honors them or silently drops them is unverified. Appropriate as a forward-looking declaration where the author treats unknown-but-tolerated frontmatter as a future-proofing surface.

## Dependency installation

Whether and how the plugin installs runtime dependencies on first use.

### No runtime dependencies (stdlib-only policy)

The plugin declares zero runtime deps as policy — `pyproject.toml` may exist for PyPI metadata but lists no `[project.dependencies]`; all hook scripts and tooling rely on Python stdlib only. Tests are stdlib-only too (`unittest`, no pytest). Appropriate when the plugin's value proposition includes "zero setup" — sidesteps `uv`/`pip` questions, venv placement, and Python ABI tracking entirely. The cost is hand-written replacements for what libraries would provide (custom JSON-schema validation, mini YAML parsers, bespoke circuit breakers), often amounting to substantial test-code volume.

### Pip + stdlib venv (no `uv`)

Python deps are installed into `${CLAUDE_PLUGIN_DATA}/venv` via stdlib `venv` + pip during a SessionStart hook. The install script reads `pyproject.toml` for the dep list and pip-installs the plugin root itself as an editable-style package so its own `lib/` becomes importable from skill scripts. A version stamp file at `${CLAUDE_PLUGIN_DATA}/installed-version` short-circuits the install on subsequent sessions when its content matches `plugin.json.version`. Appropriate for plugins that need third-party Python packages but don't want to require `uv` on the user's system; the cost is slower first-install (~tens of seconds, sometimes synchronously blocking the SessionStart) and reliance on the host having a usable system `python3`.

### Pre-built binary download (lazy, per-hook)

Runtime is a Go (or similar compiled-language) binary downloaded from GitHub Releases on demand. Build-time deps live in `go.mod`; users never compile. The binary is materialized into `${CLAUDE_PLUGIN_ROOT}/bin/` (inside the plugin cache, not `${CLAUDE_PLUGIN_DATA}`) by an `install.sh` script invoked by a wrapper script on every hook fire — not gated behind SessionStart, so the first hook of a session effectively becomes the bootstrap moment. A version-cache file at `${XDG_CACHE_HOME}/<plugin>/verified-version` short-circuits the binary-launch cost on the happy path; cache miss falls back to executing `<binary> version` and comparing to `plugin.json.version`. Appropriate when the runtime is a compiled language whose CGO/static-link story sidesteps interpreter version drift; the cost is platform-asset matrix complexity (per-OS, per-arch artifacts plus signed/notarized macOS app bundle) and a wrapper that must self-heal across cross-platform git quirks.

### Manual install script (no host-driven install)

A standalone `install.py` (or equivalent) at repo root, invoked manually by the user with verbs (`--platform`, `--uninstall`, `--verify`, `--add-to-path`). Not tied to any hook lifecycle. Idempotent through full-wipe + re-create rather than diff. Appropriate when the plugin must wire itself up to multiple host CLIs (Claude Code, Copilot CLI, Codex CLI) where each has its own install convention — the manual script can detect host presence and stage files into the right places.

## Change-detection for re-install

How the install path decides "is the cached state up to date?"

### Plugin-version stamp file

A single text file (e.g. `${CLAUDE_PLUGIN_DATA}/installed-version` or `${XDG_CACHE_HOME}/<plugin>/verified-version`) carries the last-installed `plugin.json.version` string. On each lifecycle hit, the script reads `plugin.json.version`, compares to the stamp, and skips on match. This makes `plugin.json.version` double-duty: user-facing semver AND install-staleness signal. The trade-off is that a no-op version bump (e.g. README-only) triggers a full reinstall, which most authors accept as cheap insurance. Appropriate when the install cost is low or when reinstall idempotency is verified; the cost is over-eager reinstalls.

### Two-tier version cache (file + binary self-report)

Fast path: a cache file holds the last verified version; if the file exists and matches `plugin.json.version`, skip. Cold path: cache miss invokes `<binary> version` (a process exec costing ~tens-of-ms) and compares to `plugin.json`; mismatch triggers `install.sh --force`. Appropriate when the binary is the source of truth for what's actually deployed and the file is just a launch-cost optimization; the structure makes sense when the binary itself is downloaded (not built) and the cache could be wiped without losing correctness.

### Full-wipe (no detection)

The install script always deletes its target dir and rebuilds (`reset_directory()`). No staleness detection — every install is a fresh install. Appropriate for adapter-style plugins that wire into multiple host CLIs where each install is rare (manual user invocation) and partial state is more dangerous than redundant work.

## Retry and failure semantics during install

What happens when install fails mid-way.

### `rm` stamp on failure (retry next session)

The install script wraps install + stamp-write in a single try/except; on any exception it deletes the stamp file and re-raises. Result: a half-installed venv is not remembered as "done"; next SessionStart sees the missing stamp and retries. Exception propagates to non-zero exit so the host surfaces failure. Appropriate when the host gracefully reports failure to the user and partial state is detectable from stamp absence.

### Silent fail-open (`exit 0` always, retry every hook)

Install script and wrapper use `|| true` on every side effect and `exit 0` unconditionally. Failure leaves the binary missing; the wrapper's `binary_ok` check returns false at the end and the wrapper exits silently (Claude never sees the error). Next hook fires → same check cycle retries. The wrapper's top comment makes the trade-off explicit: never block the user, even at the cost of broken installs being invisible. Appropriate when the plugin's behavior is observational (notifications, logging) rather than gating; the cost is users with persistently-broken installs see "no notifications" and may not know why.

### `[OK]/[WARN]/[FAIL]` print + non-zero exit

Manual install script prints prefixed status lines to stdout and exits 0 on success / 1 on failure. The user sees outcomes directly because they invoked the script themselves. Appropriate for user-driven install paths where exit codes feed the user's shell rather than a hook lifecycle.

## SessionStart hook role

What the SessionStart hook does, when present.

### Dependency install only

SessionStart fires `ensure-deps.py` (or equivalent), which idempotently installs Python deps if the version stamp doesn't match. No matcher set, so it fires on all sub-events (`startup`, `resume`, `clear`, `compact`) — wasted work on no-op paths is accepted as cheap. `statusMessage: "<plugin>: Installing dependencies..."` is surfaced during exec; `{"systemMessage": "..."}` JSON on stdout reports completion to the host. Appropriate when the plugin's only lifecycle need is dep readiness.

### Mission-context injection

SessionStart reads project state (e.g. mission manifest from `<git-common-dir>/<plugin>/`) and emits `hookSpecificOutput.additionalContext` with a slim summary, plus an age warning if stale. Matcher `"startup|resume|clear|compact"` is the broad form — fires on all sub-events including resume. Appropriate when the plugin maintains durable state outside the model's context that must be re-introduced at session boundaries; the cost is the host re-injects context every resume, which may be redundant.

### Absent — lazy bootstrap on first hook

No SessionStart hook at all. Whatever bootstrap work is needed (binary download, cache priming) happens on the first non-SessionStart hook of the session. The author's stated rationale (in one sample) is that Claude Code plugins historically lacked post-install hooks, so lazy-on-every-hook is the most robust pattern; even after SessionStart became available, lazy-at-every-hook self-heals through mid-session plugin upgrades that SessionStart-only would miss. Appropriate when the bootstrap cost is small and the wrapper-per-hook overhead is acceptable.

## PreToolUse hook role

What PreToolUse hooks do, with what matcher shape.

### Auto-allow plugin's own scripts

Single PreToolUse with matcher `"Bash"` (or compound), purpose: detect when a Bash command is invoking one of this plugin's own venv-Python scripts and emit an `allow` decision so the user is not prompted. Inline bash `case` fast-path string-matches the stdin JSON; only on match does the hook pipe into a Python validator. Validator uses `Path.resolve(strict=True)` for traversal-resistance and exits with no-output ("pessimistic no-opinion") on any uncertainty, deferring to the normal permission flow. Appropriate as a UX optimization for plugins whose skills always invoke the same Python scripts; the cost is hard-coding the plugin name into the bash matcher pattern, breaking on rename.

### Scope enforcement (block out-of-scope writes)

Matcher `"Write|Edit|MultiEdit|Bash"`, purpose: enforce per-role write-scope and bash-policy for multi-agent setups. Reads role declaration from a spec file, computes allow/deny against the active subagent's scope, emits `pretool_deny` payloads as JSON on stdout. Configurable failure mode (`fail_open` / `deny`) per mission. Appropriate when the plugin runs multi-agent flows where each agent must be sandboxed to a subset of the codebase; the cost is the gate is now the trust anchor and must be carefully tested.

### Observational notification trigger

Matcher `"ExitPlanMode|AskUserQuestion"` (and similar Claude-Code-decision events), purpose: fire desktop or webhook notifications when Claude reaches a decision point. Not gating — never emits deny. `timeout: 30` to avoid hanging the host. Appropriate when the plugin's role is alerting the human, not modifying the model's flow.

## PostToolUse hook role

What PostToolUse hooks do.

### Compensating revert (defense in depth)

Matcher `"Write|Edit|MultiEdit|Bash"`, purpose: if a write slipped past PreToolUse for a role that should not write (e.g. PreToolUse fail-opened, or a custom role bypassed scope), revert the write. `git checkout` for tracked files; `rm` for untracked. Ledger records `revert_mode` and `revert_success`. Appropriate when the plugin's correctness model is "no out-of-scope writes ever, even if a gate bug fires" — pairs with PreToolUse to make scope a two-layer guarantee.

### Absent

No PostToolUse hooks. Most plugins do not register one — PreToolUse alone is the gate, and post-execution observability is left to the host.

## Failure posture for hook scripts

How hook scripts handle their own exceptions, and what they emit when they fail.

### Fail-open with top-level try/except

Every hook script wraps `_main()` in try/except and calls a `_fail_open()` helper on any exception, which writes `[<plugin>] <error>` + stack trace to stderr and emits `exit 0`. Even the fallback's own ledger-write attempt is wrapped in its own try/except. Appropriate for non-blocking observational hooks; the cost is silent partial failure unless the user reads stderr.

### Fail-closed with circuit breaker (retry with backoff)

A purpose-built `HookCircuitBreaker` wraps the hook body, retrying with backoff (e.g. 100ms, 500ms) before escalating to a per-hook configurable failure mode: `deny` for pre-tool, `block` for subagent-stop, `warn` for stop. Configurable per mission via a manifest flag. Pattern-influenced by Erlang/OTP and resilience guidance. Appropriate when correctness matters more than blast-radius — gates that must not silently fail.

### Pessimistic no-opinion (exit 0 with no output)

The hook exits 0 with no stdout output on any uncertainty rather than emitting `allow` or `deny`. Effect: Claude Code falls back to its normal permission flow and prompts the user. Distinct from fail-open-with-allow (which auto-approves on uncertainty) and from deny-on-uncertainty (which over-blocks). Appropriate for permission-augmenting hooks where over-approval is a safety problem; the cost is a slightly busier permission UX when the validator is fragile.

## Tool-use enforcement model

The conceptual stance toward what hooks enforce.

### Hook-only enforcement (frontmatter is documentation)

Agent frontmatter lists tools but does not encode permission rules; actual enforcement happens in PreToolUse, which reads a role spec and computes allow/deny. Appropriate when the plugin needs richer rules than frontmatter expresses (per-path scopes, bash-policy categories, blind-from constraints) — the spec becomes the source of truth and frontmatter is a documentation surface.

### Frontmatter-only enforcement (no PreToolUse)

Agent frontmatter declares `tools: <list>` and Claude Code's built-in scoping handles enforcement; no PreToolUse hook augments it. Appropriate for simple agents whose tool needs are static and fully expressible in the documented frontmatter schema.

## User configuration surface

How a plugin lets a user customize its behavior.

### No `userConfig`, env-var only

`plugin.json` declares no `userConfig`. Configuration is read from shell environment variables (`ANTHROPIC_API_KEY`, etc.) by the plugin's own helper at runtime. SKILL.md documents which env vars are required. Appropriate when the only configurable surface is secrets that should not pass through plugin config; the cost is invisibility to Claude Code's `/plugin` settings UI and a "must be exported" precondition for the user.

### No `userConfig`, custom JSON config + slash command

`plugin.json` declares no `userConfig`. The plugin maintains its own `config/config.json` schema (richer than `userConfig` allows — webhook presets, per-status overrides, platform flags) and exposes a slash command (e.g. `/<plugin>:settings`) to edit it. `${CLAUDE_PLUGIN_ROOT}` is referenced inside the JSON for resource paths and is expanded by the plugin's own runtime, not by Claude Code's substitution mechanism. Appropriate when the schema needs are too rich for `userConfig`; the cost is no presence in Claude Code's UI and a parallel config-edit UX for the user.

### Per-mission flags only (no install-time config)

Configuration passes as CLI flags to the plugin's own CLI verb (e.g. `<cli> init --objective ... --allowed-path ...`) for each invocation. No persistent install-time config exists. Appropriate when the configurable surface is mission-scoped rather than session-scoped.

## Live monitoring channel

`monitors.json`-based monitor declarations, if any.

### Absent

No `monitors.json` in any observed sample. Notifications, when produced, flow through the hook system (Stop, SubagentStop, Notification, TeammateIdle) directly. The samples surface this is a real gap: a plugin literally named "notifications" does not use the documented monitor channel — anyone searching for monitor examples would miss it. Appropriate to flag as a corpus-wide observation: monitors may be under-adopted relative to their advertised role.

## Test framework

What runs the tests.

### Python unittest (stdlib) under pytest discovery

Tests use stdlib `unittest` (module-level classes); the discovery/runner is pytest invoked as `python -m pytest tests/ -v`. No `pytest.ini` or `[tool.pytest.ini_options]`; pytest's default discovery suffices. Appropriate when the project values stdlib-only test code but accepts pytest as the runner for its better output and discovery; the cost is the contributor must know that pytest will pick up unittest-style classes.

### Python unittest with explicit `unittest discover` invocation

Tests run via `python -m unittest discover -s tests -p 'test_*.py' -v`. No pytest. Stdlib-only. Appropriate when stdlib-only is a hard policy; the cost is somewhat noisier output and slower test feedback compared to pytest.

### Go test (compiled-language native)

Tests run via `go test -v -race -coverprofile=coverage.txt -covermode=atomic ./...`. Colocated `*_test.go` files alongside source per Go convention. CGO-enabled tests (`malgo` for audio) exercise `-race` across all OSes. Appropriate when the runtime is Go; the cost is platform asymmetry (CGO doesn't cross-compile cleanly to all arches).

### Shell script tests (installer harness)

Bash unit tests (`bin/install_test.sh`) and end-to-end tests (`bin/install_e2e_test.sh`) for the install flow itself, with a Python stdlib mock HTTP server (`bin/mock_server.py`) standing in for GitHub Releases. Run alongside the language-native tests in CI. Appropriate when the install script is itself substantial logic that must not regress.

## CI presence and shape

Whether and how continuous integration runs.

### No CI

No `.github/workflows/` directory. Nothing verifies version-bump → tag → install path on each commit. Failures show up on user `SessionStart` only. Appropriate to flag as a real gap for any plugin past the early-prototype stage.

### Single workflow with OS × language matrix

One `.github/workflows/test.yml` runs the test suite across an OS matrix (`ubuntu-latest, macos-latest, windows-latest`) and a language-version matrix (Python 3.10/3.11/3.12 or Go 1.21/1.22). Triggers on `push` to `main` and `pull_request` to `main`. Test invocation is `python -m unittest discover` or equivalent. No linters, no type checkers, no manifest validators in this workflow. Appropriate when the test suite is cohesive and self-validating.

### Per-OS workflow files (deliberate split)

Three CI workflow files (`ci-ubuntu.yml`, `ci-macos.yml`, `ci-windows.yml`) instead of one with `matrix.os`. Per-OS steps diverge significantly enough that splitting trades DRY for readability — Linux installs `libasound2-dev`, Windows uses `pwsh` for fmt check, macOS builds platform-specific sidecar binaries. Plus auxiliary workflows for signing smoke tests (`notifier-signing-smoke.yml`) and release builds. Appropriate when per-OS divergence is irreducible; the cost is duplicated boilerplate when shared steps must change in three places.

## Release automation

Whether tag pushes trigger a release pipeline.

### Manual (no `release.yml`)

No release workflow. Releases are bare git tags on `main` (sometimes with a hand-created GitHub Release). Tag-name discipline is human: name the bump commit, push the tag. Appropriate for low-volume releases and small audiences; the cost is no automated tag-vs-version sanity gate.

### Tag-triggered binary build + GH Release

Workflow triggers on `push: tags: ['v*']` and runs a multi-job pipeline: per-platform binary build (CGO_ENABLED=1 with stripped/trimmed flags), platform-specific signing/notarization (Apple Developer ID for macOS app bundle), checksum generation, GitHub Release creation via `softprops/action-gh-release@v1` with auto-generated notes, and a post-publish smoke test that re-downloads the released asset and runs `<binary> version` on each OS. No tag-format regex gate, no tag-equals-plugin-version verification. Appropriate when the release artifact is a compiled binary with platform variants; the cost is platform-specific secrets management (Apple cert P12, password, team ID) and post-release smoke testing being a verification rather than a gate.

## Marketplace / manifest validation

Whether anything checks that `plugin.json` and `marketplace.json` are well-formed.

### Absent

No CI step validates manifest shape, version agreement, or frontmatter conformance. A bad commit corrupting these files would not fail CI — it would fail at install time on the user's machine. Type checking via pyright or similar runs only in the developer's editor with no enforcement gate. Appropriate to flag as a uniform gap; even basic `jq -e '.name'` or `claude plugin validate` would close most of it.

### Custom verify command (existence-only)

A plugin-specific CLI verb (`<cli> verify`) shells through the layout and asserts that required files exist (`.claude-plugin/plugin.json`, `hooks/hooks.json`, adapter manifests). Does not check JSON schema conformance, version agreement, or frontmatter validity. Run as a CI step alongside tests. Appropriate when the project's primary risk is "deleted file" rather than "malformed file"; the cost is the false confidence that a plugin "passes verify" might give.

## Version-mismatch enforcement gates

CI checks that ensure the version string is consistent across sites.

### Absent

No tag-name → `plugin.json.version` verification, no marketplace-vs-plugin version check, no frontmatter version check. Version drift is a manual-discipline surface for every observed sample. Appropriate to flag corpus-wide.

## Documentation footprint

What user-facing and developer-facing docs the repo carries.

### Stub README only

Repo `README.md` is small (~few hundred bytes) — headings and a "currently in active development" caution, no install/usage instructions. No per-plugin README. No CHANGELOG. No `architecture.md`. No `CLAUDE.md`. Substantive documentation, when it exists, lives in an internal `worklog/` directory with numerically-keyed specs/decisions/tasks. Appropriate for early-stage repos; the cost is a new consumer must infer install from manifests and SKILL.md files.

### Substantial root README + CHANGELOG + community files + badges

Repo `README.md` is ~15-18KB covering features, install paths (often three: bootstrap curl-pipe, manual `/plugin` slash commands, classic marketplace add), supported platforms, configuration UX, troubleshooting. Opens with a hook framing or a value-prop scare example. Includes badges (CI, license, version, deps-zero). `CHANGELOG.md` follows Keep-a-Changelog format with `### Added/Fixed/Changed` under `## [x.y.z] - YYYY-MM-DD` headers, OR a custom format with theme statements. `CONTRIBUTING.md`, `LICENSE`, optional `.github/ISSUE_TEMPLATE/`. Architecture docs at `docs/ARCHITECTURE.md` (off-root, by docs-directory convention) or as a PNG diagram only. Appropriate for plugins seeking community adoption; the cost is the docs surface itself becomes a maintenance burden across releases.

### Internal developer log as primary architecture doc

The repo carries a structured internal log directory (`worklog/spec/`, `worklog/decision/`, `worklog/archive/task/`) with numerically-keyed specs, ADRs, and archived tasks. Each decision uses TOML-fence frontmatter with `id`, `title`, `relates_to`, `supersedes` keys; tasks move through spec → task → archived-task lifecycle. Cross-linking is explicit. Appropriate as a long-form design practice that embeds decision history inside the repo rather than relying on PR/issue history; the cost is the docs are inward-facing and a new user without the convention has to map it.

## Cross-platform install considerations

Concerns specific to making the plugin work on Linux, macOS, and Windows.

### POSIX `/bin/sh` discipline in hot path

Hot-path scripts (e.g. hook wrapper invoked on every event) use `/bin/sh` shebang strict POSIX — no `[[ ]]`, no arrays, no process substitution, no `local`. Manual iteration replaces `mapfile`. Appropriate because Debian/Ubuntu point `/bin/sh` at `dash`, not `bash`, and any bashism would crash silently for those users. One-shot paths (installer, bootstrap) can be bash-rich; hot path stays POSIX.

### Mixed shebangs partitioned by criticality

Hot path: `/bin/sh` (POSIX). Installer: `/bin/bash` with `set -e`. Bootstrap one-shot: `/bin/bash` with `set -euo pipefail`. Test mock server: `#!/usr/bin/env python3`. Each role gets its own shebang appropriate to its constraints. Appropriate as a deliberate partition; the alternative is uniform `#!/bin/bash` everywhere and accepting risk on the hot path.

### Dual-fallback OS detection

`uname -s` primary; `$OS` env var (e.g. `Windows_NT`) fallback for shells without `uname`. Architecture: `uname -m` normalized to `amd64`/`arm64`. Pattern worth codifying: don't trust one probe on Windows.

### Git symlink-as-text-file detection on Windows

Git on Windows with `core.symlinks=false` (the default) materializes symlinks as plain text files containing the target string. A wrapper detects this case (file size < 1KB, contents match an expected binary-name pattern) and either resolves to the real target or synthesizes a `MISSING` path to force re-install. `.gitattributes` codifies `text eol=lf` for `*.sh` and `eol=crlf` for `*.bat`/`*.ps1`. Cross-platform workaround for a git-setting difference most plugin authors don't realize they're hitting.

### Adapter directory per host CLI

Multi-host plugins ship `adapters/<host>/` directories (e.g. `adapters/copilot_cli/`, `adapters/codex_cli/`) each with its own manifest format. Shared core in a common module (e.g. `hooks/scripts/core/`); adapters import, not duplicate. Installer detects which host CLI is present and wires up the right adapter surface. Appropriate when the plugin must support multiple Claude-adjacent CLIs; the cost is a multi-times manifest-edit burden during a refactor.

## Plugin-internal state location

Where the plugin keeps its own runtime state (caches, ledgers, manifests).

### `${CLAUDE_PLUGIN_DATA}` for venvs and stamps

Per-plugin data dir under the host's plugin-cache root. Used for the venv (`/venv`), the install-version stamp (`/installed-version`), and similar "host-managed cache that survives session boundaries" content. Appropriate as the canonical home for per-plugin write state.

### `${CLAUDE_PLUGIN_ROOT}/bin/` for downloaded binaries

Inside the plugin cache itself (next to the wrapper that downloads them). Distinct from `${CLAUDE_PLUGIN_DATA}` — keeps everything the wrapper might need adjacent to the wrapper. Appropriate when the binary should be co-located with the script that resolves its path; the cost is a binary churn lives inside the plugin cache rather than a dedicated data area.

### `${XDG_CACHE_HOME:-$HOME/.cache}/<plugin>/` for verified-version cache

User-level cache directory for fast-path verification — separate from the plugin cache so it survives plugin reinstalls/upgrades. Appropriate when the cache is purely an optimization (cold path can rebuild it) and shouldn't be invalidated by plugin reinstall.

### `<git-common-dir>/<plugin>/` for mission state

State stored under the git common directory rather than `.git/` directly — crucial when the plugin uses worktree isolation, because `.git/` differs per worktree but `git-common-dir` resolves to the same location across them. Mission manifest, ledger, per-role results all live here so coordinator + worktree-isolated subagents share one state. Appropriate when the plugin's correctness depends on cross-worktree state coherence; the cost is dependency on a git repo being present and the user not removing the dir manually.

### `${CLAUDE_CONFIG_DIR:-${CLAUDE_HOME:-$HOME/.claude}}/<plugin>/` pointer files

A pointer file at the host's config dir holding the plugin's current resolved root, written through "only on change" with atomic rename. Used so older cached paths and shim wrappers can find the current plugin root across reinstalls. Cross-session breadcrumb for binaries that might be invoked from multiple resolved paths over their lifetime. Appropriate as a fallback for shim wrappers; the cost is leakage if the plugin is uninstalled (the pointer file persists in `~/.claude`).

## Cross-role tools

Several tools fill multiple roles in the bin and are worth naming under each role's section.

### Python (stdlib) — runtime, install script, mock server, tests

Python 3.10+ appears as: the runtime for hook scripts (stdlib only when zero-dep policy in force; pip + third-party when not), the install-script language (`install.py`, `ensure-deps.py`), the mock HTTP server in install E2E tests (`mock_server.py`), and the test framework (`unittest` stdlib). Different roles use different sub-uses (stdlib only vs pip + third-party).

### `${CLAUDE_PLUGIN_ROOT}` env var — wrapper resolution, config substitution, hook commands

Used by hook wrappers to locate the plugin's bin scripts; used inside `config/config.json` for resource paths (expanded by the plugin's own runtime, not by the host); used in `hooks/hooks.json` to locate hook scripts. The same env var fills "find my own files" across three roles.

### `plugin.json.version` — semver display, install-staleness signal, binary-version pin

The same string drives user-facing version display, the install-skip predicate (matched against a stamp file), and the lazy-download URL for the matching binary asset. Triple-duty as both data and control signal.

### Bash `case` + Python validator pattern — hook fast path, allow-list reduction

Inline `case "$input" in <pattern>) python validator ;; esac` in hooks.json fast-paths 99% of unrelated calls without paying Python startup cost. The here-string `<<< "$input"` safely passes JSON with embedded quotes. Pattern is documented in at least one ADR. The pattern surfaces under "PreToolUse hook" (auto-allow scripts) and is also relevant to "Tool-use enforcement" (gating).

### Git as state substrate — branching, common-dir state, worktree isolation, install-as-clone

Git fills multiple plugin roles: tag placement and branching strategy at the release layer, `<git-common-dir>/` as a state-storage root for mission state, worktree creation as the per-role isolation mechanism, and the underlying mechanic of marketplace install (clone-or-update of a remote repo). Each role uses a different facet of git.
