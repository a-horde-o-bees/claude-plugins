# Sample

Mirrors of `https://github.com/ChanMeng666/claude-code-audio-hooks`. Single-plugin marketplace shipping an AI-operated audio notification system for Claude Code — 26 hooks, native matcher routing, TTS, webhook fan-out, status line, focus flow, rate-limit alerts.

## Marketplace manifest layout

### Single root manifest with relative source under `plugins/<name>/`

Single `.claude-plugin/marketplace.json` at repo root with the plugin payload under `plugins/audio-hooks/`. Marketplace name `chanmeng-audio-hooks`, plugin name `audio-hooks`. Plugin entry source `"./plugins/audio-hooks"`. `metadata.{description, version}` wrapper present (`metadata.description` and `metadata.version: "5.1.2"`). `metadata.pluginRoot` absent — the single plugin uses explicit `source: "./plugins/audio-hooks"` instead. `$schema` absent on `marketplace.json`. Marketplace `name` (`chanmeng-audio-hooks`) differs from the plugin `name` (`audio-hooks`) — install command is `@chanmeng-audio-hooks` (owner-prefixed marketplace ref) while the plugin itself is addressed as `audio-hooks`.

### Top-level `metadata` wrapper variants

`metadata.{description, version}` wrapper. `metadata.version: "5.1.2"` duplicates the plugin's own `version` — if they drift, which is authoritative is not declared.

## Plugin source binding

### Relative source pointing to subdirectory

`"source": "./plugins/audio-hooks"` — plugin payload lives in a subdirectory of the marketplace repo.

### `strict` field default

`strict` field absent on the marketplace entry — implicit `true`. `skills` override absent on marketplace entry; plugin ships its own `skills/audio-hooks/` directory.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Marketplace entry carries `keywords: ["audio","notifications","hooks","tts","webhook","ai-operated","rate-limits","status-line"]`. No `category`, no `tags` on the marketplace surface.

### Repo-level GitHub topics

GitHub repository topics declared at the GitHub level (audio-notifications, automation, bash, claude-code, cli-tools, developer-tools, hooks, notification-system, productivity, wsl) — drives GitHub search but not the Claude Code marketplace UI.

## Version coordination

### Multi-site sprawl (5+ locations)

Multiple version sites held in sync by hand. `marketplace.json.metadata.version`, `marketplace.json.plugins[0].version`, and `plugins/audio-hooks/.claude-plugin/plugin.json.version` all carry `"5.1.2"`. CHANGELOG entry for 5.1.1 explicitly enumerates them: "every version reference (`HOOK_RUNNER_VERSION`, `PROJECT_VERSION`, `marketplace.json`, `plugin.json`, `config/default_preferences.json`, `CLAUDE.md` header) is now consistently `5.1.1`" — manual bumps across ~6 sites. v5.1.0 shipped inconsistent after this process failed: the tag was cut but several sites never bumped, so installs reported 5.0.3 while broken code shipped.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Only the `master` branch tracks versions; tags are the release anchors (30+ tags, zero release branches). No `stable-*` / `latest-*` marketplace split, no `release/*` branch. Users who want to pin to a stable version have to use `@v5.1.2` git-ref pinning in the marketplace add command — which `marketplace.json` does not document.

## Tag and release lifecycle

### Tag-on-main, single branch

Default branch `master` (note: `master`, not `main`). All 30+ tags sit on the single branch. No release branching. No pre-release suffixes (all tags `vX.Y.Z`, no `-rc` / `-beta` / `-alpha` in the first 30 tags sampled). No `.pre-commit-config.yaml`, no committed git hooks; CHANGELOG 5.1.1 shows version bumps are manual and a CI job (`build-plugin.sh --check`) catches sync drift after the fact but doesn't bump. v5.1.0 was cut from a feature commit that never bumped version strings — CHANGELOG 5.1.1 documents this as the specific trigger for adding CI regression gating.

## Plugin-component registration

### Default convention discovery

`plugin.json` holds only `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `userConfig`. Every component is resolved by convention from directory names: `hooks/hooks.json`, `skills/<name>/SKILL.md`, etc. No component fields in `plugin.json`.

### Hooks-json with broad event coverage

`hooks/hooks.json` carries 26 hook registrations across 24 event types. Status line is not declared in `plugin.json`; instead, the CLI's `audio-hooks statusline install` subcommand mutates the user's `~/.claude/settings.json` to point at `bin/audio-hooks-statusline`. Sidesteps the plugin manifest for a component the user has to opt into; uninstalling the plugin does not automatically remove the statusline registration.

## Component composition

### Composition shapes

Skills + hooks + bin. Skills (`plugins/audio-hooks/skills/audio-hooks/SKILL.md`, one skill); no commands, no agents; hooks (`plugins/audio-hooks/hooks/hooks.json`, 26 registrations across 24 event types); no `.mcp.json`, no `.lsp.json`, no monitors; bin (`plugins/audio-hooks/bin/` — 6 files: `audio-hooks`, `audio-hooks.py`, `audio-hooks.cmd`, `audio-hooks-statusline`, `audio-hooks-statusline.py`, `audio-hooks-statusline.cmd`); no output-styles.

## Skill authoring conventions

### Standard frontmatter

One skill at `plugins/audio-hooks/skills/audio-hooks/SKILL.md`. SKILL.md is deliberately lightweight orientation — directs Claude to call `audio-hooks manifest` whenever it is unsure, treating the runtime binary as the source of truth over SKILL.md.

## Bin entry mechanism

### Bash + `.cmd` pair for cross-platform

Bash wrapper plus Windows `.cmd` shim per entry. `bin/audio-hooks` is a bash wrapper around `audio-hooks.py`; rationale comment says "Git Bash on Windows does not interpret Python shebangs the way Linux/macOS do." `bin/audio-hooks.py` is the canonical `#!/usr/bin/env python3` entry — 60 KB single-file CLI with ~27 subcommands (`manifest`, `status`, `version`, `test`, `snooze`, `hooks list/enable/disable`, `statusline install/...`). `bin/audio-hooks.cmd` is a 109-byte Windows shim: `python "%~dp0audio-hooks.py" %*`. Same triple for `audio-hooks-statusline`. Bash wrappers do their own Python-interpreter probing (`python3` → `python` → `py`), run a smoke `python -c 'import sys'` to defeat the Microsoft Store `python3.exe` stub on Windows, then `exec` into the `.py` file with matching args. Permissions are 100644 (non-executable) — works because Claude Code adds the plugin's `bin/` to PATH and shell resolution runs through the shebang via `bash <path>` rather than via `exec()`. Users cloning the repo and running `bin/audio-hooks` directly without a `bash` prefix would see "permission denied." Hook invocations in `hooks.json` use `${CLAUDE_PLUGIN_ROOT}` to locate `runner/run.py` (a separate path); the bin wrappers themselves use `SCRIPT_DIR` derived from `BASH_SOURCE` and resolve `PYTHON_ENTRY="$SCRIPT_DIR/audio-hooks.py"`. No `.ps1` siblings.

### Bash trampoline resolving python3 → python → py

The bash wrapper performs interpreter probing — `python3` → `python` → `py` — instead of relying on the Python shebang alone. More defensive than `exec python3 "${0%.*}.py"`. Inline source comment documents the Windows Store stub problem as the rationale.

## Dependency installation

### Zero dependencies / stdlib only

Python stdlib only — no `requirements.txt`, no `pyproject.toml`, no `package.json`. `hook_runner.py` and `audio-hooks.py` import only Python stdlib. Audio playback shells out to system players (`mpg123`, `ffplay`, `paplay`, `aplay` on Linux; `afplay` on macOS; PowerShell `PresentationCore.MediaPlayer` / `WMPlayer.OCX` on Windows) — no Python venv. The "dependency" gating is a system audio-player binary; failure is nonfatal — hooks silently skip playback when no player is found. CI installs `mpg123` on Linux runners explicitly (`sudo apt-get install -y mpg123`) — this install guidance does not appear in the user-facing docs on Linux. Python 3.9+ required (CI matrix tests 3.9 / 3.12 / 3.13). The v5.1.1 fix note calls out that missing `from __future__ import annotations` caused a Python-version-sensitive crash on the `Tuple` type import.

## User configuration and authentication

### Native `userConfig` with `${user_config.KEY}` substitution

Top-level `userConfig` object in `plugins/audio-hooks/.claude-plugin/plugin.json` declares 4 fields (`audio_theme`, `webhook_url`, `webhook_format`, `tts_enabled`). Each field has `type`, `title`, `description`. No `default`, no `enum` on the enumerable fields — descriptions list valid values in prose ("`default` or `custom`"). The runtime reads via `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (the substitution channel). `hook_runner.py` overlays: `CLAUDE_PLUGIN_OPTION_AUDIO_THEME` → `audio_theme`, `CLAUDE_PLUGIN_OPTION_WEBHOOK_URL` → `webhook_settings.url`, `CLAUDE_PLUGIN_OPTION_WEBHOOK_FORMAT` → `webhook_settings.format`, `CLAUDE_PLUGIN_OPTION_TTS_ENABLED` → `tts_settings.enabled` (with lower-case truthy coercion). No `${user_config.KEY}` string substitution in the `hooks.json` command lines — substitution happens inside the Python hook runner at read time. Plugin surface has 4 userConfig fields but the underlying `user_preferences.schema.json` has ~40+ nested properties — the 4 manifest fields are a deliberately-minimal bootstrap surface; the deeper config is mutated by the `audio-hooks` CLI, not by the plugin installer.

### `sensitive: true` flag absent on secret fields

No `sensitive` flag on any field. `webhook_url` could plausibly carry a Slack/Discord webhook secret and is not marked sensitive — webhook URLs are sometimes treated as non-secret, but the field defaults to not-sensitive. Anyone reading the user's global settings sees the webhook URL in plain text.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

Hooks read userConfig values through `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (the substitution channel for `userConfig` values) rather than via `${user_config.KEY}` token substitution in command lines.

## Session context loading

### SessionStart purely for non-context side effects

`SessionStart` is used only for audio playback — 4 matchers (`startup`, `resume`, `clear`, `compact`), each dispatching to a distinct audio cue. No `additionalContext` emission. No `UserPromptSubmit` for context — UserPromptSubmit is registered as an audio hook only. `SessionStart` with `matcher: "resume"` fires on every resume; the handler plays a sound, so this is among the hooks most likely to annoy users. The plugin exposes `audio-hooks hooks disable session_start_resume` to mute it; no per-matcher default-off.

## SessionStart matcher scope

### Per-hook differentiation within one plugin

The hooks.json docstring calls this "matcher-scoped hook registration" as a v5.0 design choice — "matcher routing happens in settings.json instead of Python branching." `SessionStart` matchers split across all 4 sub-events (`startup`, `resume`, `clear`, `compact`); each `Notification` matcher and each `StopFailure` matcher gets its own registration with a synthetic handler name (e.g., `session_start_resume`, `notification_permission_prompt`). The Python runner dispatches on the handler name, not the event name.

## Tool-use enforcement

### PostToolUse-only for notification + observation

These hooks are notification hooks, not policy enforcement. `PreToolUse` has 1 entry (matcher `"Bash"`, dispatches to `pretooluse` for audio on Bash invocations; `async: true, timeout: 10`). `PostToolUse` has 1 entry (matcher `"Bash|Write|Edit"`, dispatches to `posttooluse`); a sibling `PostToolUseFailure` (same matcher) dispatches to `posttoolusefailure`. `PermissionRequest` (empty matcher `""`) and `PermissionDenied` (no matcher) both registered, dispatch to audio announcements. The `PermissionRequest` hook with empty matcher `""` is legal but unusual — contrast with explicit matcher elsewhere.

### `PermissionDenied` as event log

`PermissionDenied` is registered, but the handler is an audio announcer / event tally rather than an enforcement gate.

## Hook handler runtime

### Python stdlib runner with external probing

Hooks call `python "${CLAUDE_PLUGIN_ROOT}/runner/run.py"` — a single Python file using only stdlib. Runner shells out to system audio binaries (`mpg123`, `ffplay`, `paplay`, `aplay`, `afplay`, PowerShell players) by probing the platform. No Python venv, no third-party packages.

## Hook output contract

### JSON-only stdout, no stderr-human parallel

`audio-hooks.py` docstring states "All output is JSON to stdout. No stderr in normal operation." Hook dispatches are fire-and-forget with `async: true`.

## Hook failure posture

### Fail-open with always-exit-0

Hooks have `async: true` + `timeout: 10`; errors during audio playback don't block the tool call. The Python layer uses `subprocess.Popen` for audio players so nothing waits. The v5.1.1 bug (`NameError: name 'Tuple' is not defined` at module import crashing every subcommand) suggests no top-level exception wrapping caught it before dispatch. After the fix, CI import-smoke tests every subcommand to catch the regression class.

## Live monitoring

### Status line via user-settings mutation

The status line (`audio-hooks-statusline`) is implemented as a Claude Code status line (user setting) rather than as a `monitors.json` entry. Plugin manifest does not declare statusline capability; the CLI's `audio-hooks statusline install` subcommand mutates the user's `~/.claude/settings.json` to register the script. Uninstalling the plugin leaves the statusline registration dangling until the user runs `audio-hooks statusline uninstall`. No `monitors.json` in `plugins/audio-hooks/`.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` in `plugin.json`. Tag format is `v5.1.2` (no plugin-name prefix) — single-plugin marketplace.

## Testing

### Smoke-only Python import + subcommand exercise

Single `smoke.yml` workflow runs `python -c "import hook_runner"` against canonical (`hooks/`) and packaged (`plugins/audio-hooks/hooks/`) paths, invokes every CLI subcommand once (`audio-hooks.py version / status / diagnose`, `audio-hooks.py test all` dispatches all 26 hooks), and runs `bash scripts/build-plugin.sh --check`. Matrix `ubuntu-latest, windows-latest, macos-latest` × `3.9, 3.12, 3.13` (9 combinations, `fail-fast: false`). Catches runtime regressions; does not validate schemas. Test framework: bash scripts + in-CI Python one-liners. Single dedicated test file at `scripts/.internal-tests/test-path-utils.sh` (~8.8 KB). No `tests/` directory at repo root (confirmed via 404 on `/contents/tests`). No pytest, no test runner abstraction.

### Retroactive CI as documented regression response

CHANGELOG 5.1.1 explicitly says CI was added because of a specific crash — "CI import-smoke workflow to prevent regressions of this class of bug." The commit history reads as "no CI → broken tag → add CI gate whose failure reproduces the bug."

## CI workflow shape

### Single workflow, OS × language matrix

`.github/workflows/smoke.yml` (the only workflow, 1.5 KB) triggers on `push: branches: [master]` and `pull_request`. Matrix OS × Python — `ubuntu-latest, windows-latest, macos-latest` × `3.9, 3.12, 3.13` (9 combinations, `fail-fast: false`). Action pinning by tag (`actions/checkout@v4`, `actions/setup-python@v5`); no SHA pinning. No caching (setup-python's built-in pip cache has no dep file to cache, so effectively no caching). Test runner invocation: direct Python one-liners in workflow steps (no `scripts/test.sh`, no `pytest`).

## Pre-commit and pre-push hooks (git)

### Absent

No `.pre-commit-config.yaml`, no committed git hooks. Version bumps are manual.

## Marketplace validation

### Implicit via runtime exercise

`audio-hooks.py test all` in CI exercises every hook, which would fail if `hooks.json` pointed at nonexistent handlers. But there is no schema-level validation of the `hooks.json` shape itself, no marketplace.json schema validation, no skill frontmatter validation. The `plugin-in-sync` CI job is the only automated gate that catches "tag points at commit where plugin copy ≠ canonical source." CI leans heavily on "does it run?" rather than "does it match schema?" — catches runtime regressions but not schema drift if Claude Code changes its expected hook event set.

## Release automation

### No release automation / manual

No `release.yml` — only `smoke.yml` in workflows. 30+ tags, 10+ published releases, no workflow file to create them. Manual GitHub release creation. The `smoke.yml` runs on all pushes, implicitly including tag-commit pushes, but there is no tag-specific workflow. The `plugin-in-sync` CI job is the only automated gate that catches tag-vs-source drift. CHANGELOG.md is hand-maintained in Keep-a-Changelog format (cites keepachangelog.com in the header); release notes are hand-written per release based on length and tone. All observed releases have `draft: false`. Fully manual release process plus multi-file version sync is exactly the failure mode v5.1.0 hit.

## Documentation surface

### Substantial root README + CHANGELOG + community files + badges

Repo-root `README.md` ~40 KB — extensive with tables, install instructions, architecture diagram, troubleshooting, uninstall flow, developer section, promo video embed. Six shields (License, Version, Platform, Claude Code version floor, Plugin-install banner, five "Share" badges). No per-plugin README at `plugins/audio-hooks/`; the plugin's "docs" is the SKILL.md frontmatter description plus the root README. `CHANGELOG.md` 66 KB Keep-a-Changelog format. `docs/ARCHITECTURE.md`, `docs/INSTALLATION_GUIDE.md`, `docs/TROUBLESHOOTING.md` at repo root (not at plugin root). `CLAUDE.md` at repo root (~25 KB) — the "AI operator instruction manual" for the project, explicitly AI-facing operator docs.

## Community health files

### Community health files absent

No `.github/` community health folder at root. No `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`, no issue templates, no PR template.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` at root (SPDX `MIT`); `license` field in `plugin.json` and `marketplace.json` carries the same identifier.

## Distribution exclusion and dogfood layout

### `.claude-plugin/ignore` exclusion list

Two parallel source trees: `/bin/*`, `/hooks/*`, `/audio/*`, `/config/default_preferences.json` at repo root (canonical sources) and `/plugins/audio-hooks/...` (packaged copy). `scripts/build-plugin.sh [--check]` is the diff/sync tool that does `cp + cmp -s`; CI job `plugin-in-sync` enforces sync. Rationale documented: Claude Code's plugin caching packages the `plugins/<name>/` tree as a unit, so sources bundled there must be self-contained.

## Source layout

### Dual tree with sync gate

Authoring sources live at repo root (`/hooks/`, `/bin/`, `/audio/`, `/config/`); a packaged copy lives at `plugins/audio-hooks/...`. `scripts/build-plugin.sh` is the manual reconciliation tool; CI job enforces sync.

## Novel and cross-cutting concerns

### Graceful-degradation via fallback tool

The `audio-hooks` CLI's `manifest` subcommand returns a JSON description of every subcommand, every config key, every hook, every audio file, and every error code. SKILL.md explicitly directs Claude to call `audio-hooks manifest` whenever it is unsure — treating the runtime binary as the source of truth over SKILL.md. SKILL.md is deliberately lightweight orientation; the CLI itself carries the current-capability description.
