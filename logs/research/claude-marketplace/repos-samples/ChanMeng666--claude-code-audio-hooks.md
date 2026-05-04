# ChanMeng666/claude-code-audio-hooks

## Identification

- **URL**: https://github.com/ChanMeng666/claude-code-audio-hooks
- **Stars**: 46 (observed)
- **Last commit date**: 2026-04-20 (observed, commit on master)
- **Default branch**: `master` (observed)
- **License**: MIT (observed — `LICENSE` + `license` fields in plugin.json / marketplace.json)
- **Sample origin**: bin-wrapper
- **One-line purpose**: "AI-operated audio notification system for Claude Code. 26 hooks, native matcher routing, TTS, webhook fan-out, status line, focus flow, rate-limit alerts." (verbatim from marketplace metadata.description)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (observed)
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper (observed — `metadata.description` and `metadata.version: "5.1.2"`, both present; no `metadata.pluginRoot`)
- **`metadata.pluginRoot`**: absent (observed — the single plugin uses explicit `source: "./plugins/audio-hooks"` instead)
- **Per-plugin discoverability**: keywords only (observed — `keywords: ["audio","notifications","hooks","tts","webhook","ai-operated","rate-limits","status-line"]` on the marketplace entry; no `category`, no `tags`). Repo `topics` also present on GitHub (audio-notifications, automation, bash, claude-code, cli-tools, developer-tools, hooks, notification-system, productivity, wsl) but those are GitHub-level, not marketplace-level.
- **`$schema`**: absent (observed — no `$schema` key in marketplace.json)
- **Reserved-name collision**: no (observed — marketplace name `chanmeng-audio-hooks`, plugin name `audio-hooks`; neither is a reserved Claude Code namespace)
- **Pitfalls observed**: Marketplace `name` (`chanmeng-audio-hooks`) differs from the plugin `name` (`audio-hooks`) — install command is `@chanmeng-audio-hooks` (owner-prefixed marketplace ref) while the plugin itself is addressed as `audio-hooks`. This is a deliberate namespacing pattern but creates a mental-model split for users unfamiliar with it. Also `metadata.version` on the marketplace duplicates the plugin's own `version` — if they drift, which is authoritative is not declared.

## 2. Plugin source binding

- **Source format(s) observed**: relative string — `"source": "./plugins/audio-hooks"` (observed, single plugin)
- **`strict` field**: default (implicit true) — no `strict` key in the marketplace entry (observed)
- **`skills` override on marketplace entry**: absent (observed — no `skills` override; plugin ships its own `skills/audio-hooks/` directory instead)
- **Version authority**: both (drift risk) — `marketplace.json.metadata.version`, `marketplace.json.plugins[0].version`, and `plugins/audio-hooks/.claude-plugin/plugin.json.version` all carry `"5.1.2"` (observed). CHANGELOG entry for 5.1.1 explicitly calls this out: "every version reference (`HOOK_RUNNER_VERSION`, `PROJECT_VERSION`, `marketplace.json`, `plugin.json`, `config/default_preferences.json`, `CLAUDE.md` header) is now consistently `5.1.1`" — i.e. manual bumps across ~6 sites, and v5.1.0 shipped inconsistent after this process failed.
- **Pitfalls observed**: Three version strings held in sync by hand. v5.1.0 is a historical example of the drift failure mode — the tag was cut but several sites never bumped, so installs reported 5.0.3 while broken code shipped.

## 3. Channel distribution

- **Channel mechanism**: no split (users pin via `@ref` if needed). Only the `master` branch tracks versions; tags are the release anchors (observed — 30+ tags, zero release branches)
- **Channel-pinning artifacts**: absent (observed — no `stable-*` / `latest-*` marketplace split, no `release/*` branch)
- **Pitfalls observed**: Without a channel split, users who want to pin to a stable version have to use `@v5.1.2` git-ref pinning in the marketplace add command — which `marketplace.json` doesn't document.

## 4. Version control and release cadence

- **Default branch name**: master (observed — note: `master` not `main`, older GitHub convention)
- **Tag placement**: on master (observed — all 30+ tags sit on the single branch)
- **Release branching**: none (tag-on-master, observed)
- **Pre-release suffixes**: none observed (all tags `vX.Y.Z`, no `-rc` / `-beta` / `-alpha` in the first 30 tags sampled)
- **Dev-counter scheme**: absent (observed — normal semver with no separate dev-build incrementer)
- **Pre-commit version bump**: no (observed — no `.pre-commit-config.yaml`, no git hooks committed; CHANGELOG 5.1.1 shows version bumps are manual and a CI job (`build-plugin.sh --check`) catches sync drift after the fact but doesn't bump)
- **Pitfalls observed**: v5.1.0 was cut from a feature commit that never bumped version strings — CHANGELOG 5.1.1 documents this as the specific trigger for adding CI regression gating. Tag-on-master with manual multi-file bumps is fragile.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery (no component fields) — observed. The plugin.json holds only `name`, `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`, `userConfig`. Every component is resolved by convention from directory names: `hooks/hooks.json`, `skills/<name>/SKILL.md`, etc.
- **Components observed**:
  - skills: yes (`plugins/audio-hooks/skills/audio-hooks/SKILL.md`, one skill)
  - commands: no
  - agents: no
  - hooks: yes (`plugins/audio-hooks/hooks/hooks.json`, 26 hook registrations across 24 event types)
  - `.mcp.json`: no
  - `.lsp.json`: no
  - monitors: no
  - bin: yes (`plugins/audio-hooks/bin/` — 6 files: `audio-hooks`, `audio-hooks.py`, `audio-hooks.cmd`, `audio-hooks-statusline`, `audio-hooks-statusline.py`, `audio-hooks-statusline.cmd`)
  - output-styles: no
- **Agent frontmatter fields used**: not applicable (no agents)
- **Agent tools syntax**: not applicable
- **Pitfalls observed**: Status line is not declared in plugin.json; instead, the CLI's `audio-hooks statusline install` subcommand mutates the user's `~/.claude/settings.json` to point at `bin/audio-hooks-statusline`. This is novel — it sidesteps the plugin manifest for a component the user has to opt into, but means uninstalling the plugin does not automatically remove the statusline registration.

## 6. Dependency installation

- **Applicable**: yes (Python stdlib only, but still worth documenting as the anti-case)
- **Dep manifest format**: none (observed — no `requirements.txt`, no `pyproject.toml`, no `package.json`; hook_runner.py and audio-hooks.py import only Python stdlib)
- **Install location**: not applicable (no install target because no deps)
- **Install script location**: not applicable
- **Change detection**: not applicable
- **Retry-next-session invariant**: not applicable
- **Failure signaling**: not applicable
- **Runtime variant**: Python stdlib-only; audio playback shells out to system players (`mpg123`, `ffplay`, `paplay`, `aplay` on Linux; `afplay` on macOS; PowerShell `PresentationCore.MediaPlayer` / `WMPlayer.OCX` on Windows). No Python venv.
- **Alternative approaches**: None — deliberately zero-dep-to-install. The author chose system-binary probing over bundling an audio library.
- **Version-mismatch handling**: Python 3.9+ required (observed — CI matrix tests 3.9 / 3.12 / 3.13). The v5.1.1 fix note calls out that missing `from __future__ import annotations` caused a Python-version-sensitive crash on the `Tuple` type import.
- **Pitfalls observed**: The only "dependency" gating is a system audio-player binary, and failure is nonfatal — hooks just silently skip playback. But CI installs `mpg123` on Linux runners explicitly (`sudo apt-get install -y mpg123`), hinting that no such install guidance appears in the user-facing docs on Linux.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes
- **`bin/` files** (`plugins/audio-hooks/bin/`, 6 files):
  - `audio-hooks` — bash wrapper around `audio-hooks.py`; rationale comment says "Git Bash on Windows does not interpret Python shebangs the way Linux/macOS do"
  - `audio-hooks.py` — canonical `#!/usr/bin/env python3` entry; 60 KB single-file CLI with ~27 subcommands (`manifest`, `status`, `version`, `test`, `snooze`, `hooks list/enable/disable`, `statusline install/...`, etc.)
  - `audio-hooks.cmd` — 109-byte Windows shim: `python "%~dp0audio-hooks.py" %*`
  - `audio-hooks-statusline` — bash wrapper, same shape as above
  - `audio-hooks-statusline.py` — standalone Python entry for the status line
  - `audio-hooks-statusline.cmd` — Windows shim
- **Shebang convention**: mixed — bash wrappers (`env bash`), Python entries (`env python3`), Windows `.cmd` shims (batch). The `env bash` wrappers do their own Python-interpreter probing (`python3` → `python` → `py`) and `exec` into the `.py` file with matching args.
- **Runtime resolution**: script-relative only (observed — `SCRIPT_DIR` derived from `BASH_SOURCE`, then `PYTHON_ENTRY="$SCRIPT_DIR/audio-hooks.py"`; no `${CLAUDE_PLUGIN_ROOT}` involvement in the bin wrappers themselves). Hook invocations in `hooks.json` do use `${CLAUDE_PLUGIN_ROOT}` to locate `runner/run.py`, but that's a separate path.
- **Venv handling (Python)**: no venv (system python3) — observed. The bash wrapper probes `python3 → python → py`, runs a "does it actually work" smoke (`-c 'import sys'`) to defeat the Windows Store `python3.exe` stub, then execs.
- **Platform support**: bash + .cmd pair for each entry (POSIX shell wrapper + Windows batch shim). No `.ps1` siblings. Comments call out Git Bash on Windows as the specific motivator for the wrapper approach.
- **Permissions**: 100644 (non-executable) — observed for every file in `plugins/audio-hooks/bin/`. Root `/bin/` copies are also 100644. The root `hooks/*.sh` scripts are 100755, so the project knows how to set the exec bit — the 100644 choice for `bin/` appears deliberate, presumably because `hooks.json` invokes them via `python "${CLAUDE_PLUGIN_ROOT}/runner/run.py"` (a wrapper Python script) rather than running the bin files directly. The bin files are the *user-facing* CLI reachable via `bash <path>` / `python <path>` / the PATH-wrapping that Claude Code's plugin cache sets up.
- **SessionStart relationship**: static (no SessionStart hook, observed). The `bin/` files are shipped as-is; no hook-driven build or pointer-file write. CI does exercise `bash scripts/build-plugin.sh --check` which keeps the `plugins/audio-hooks/bin/` copies in sync with the root `bin/` sources.
- **Pitfalls observed**:
  - Non-exec bit (100644) without a symlink or explicit chmod is unusual for a bin directory — works because Claude Code adds the plugin's `bin/` to PATH and shell resolution runs through the shebang via `bash <path>` rather than via exec(). Users cloning the repo and running `bin/audio-hooks` directly without `bash` prefix would see "permission denied".
  - Two parallel source trees: `/bin/*` and `/plugins/audio-hooks/bin/*` must stay in sync. `scripts/build-plugin.sh` is the manual reconciliation tool; CI job `plugin-in-sync` enforces it. The duplication exists because Claude Code's plugin caching copies the `plugins/<name>/` directory as a unit.
  - User-provided hint said "Standalone `#!/usr/bin/env python3` script (not a wrapper)" — this is only true for `audio-hooks.py`. The file literally named `audio-hooks` (no extension) is a bash wrapper. The *logical* bin-wrapper pattern here is: bash-wrapper with sibling `.py` + `.cmd`, where the bash wrapper itself performs interpreter-probing instead of relying on a shebang alone.

## 8. User configuration

- **`userConfig` present**: yes (observed — top-level `userConfig` object in `plugins/audio-hooks/.claude-plugin/plugin.json`)
- **Field count**: 4 (`audio_theme`, `webhook_url`, `webhook_format`, `tts_enabled`)
- **`sensitive: true` usage**: not applicable (no `sensitive` flag on any field — but `webhook_url` could plausibly carry a Slack/Discord webhook secret, and it's not marked sensitive. Not a clear violation since webhook URLs are sometimes treated as non-secret, but worth flagging as "defaults to not-sensitive")
- **Schema richness**: typed (`type`, `title`, `description`) for all 4 fields. No `default`, no `enum` on the enumerable fields (`audio_theme`, `webhook_format`) — the description text lists valid values in prose instead.
- **Reference in config substitution**: `CLAUDE_PLUGIN_OPTION_<KEY>` env var usage (observed in `hook_runner.py`). Specifically the runner overlays: `CLAUDE_PLUGIN_OPTION_AUDIO_THEME` → `audio_theme`, `CLAUDE_PLUGIN_OPTION_WEBHOOK_URL` → `webhook_settings.url`, `CLAUDE_PLUGIN_OPTION_WEBHOOK_FORMAT` → `webhook_settings.format`, `CLAUDE_PLUGIN_OPTION_TTS_ENABLED` → `tts_settings.enabled` (with a lower-case truthy coercion). No `${user_config.KEY}` string-substitution in the hooks.json command lines — the substitution happens inside the Python hook runner at read time.
- **Pitfalls observed**:
  - Enums declared only in prose descriptions (`"default" or "custom"`) — the installer UI gets no validation hook, so typos silently fall through to the hook runner's defaults.
  - Plugin surface has 4 userConfig fields but the underlying `user_preferences.schema.json` has ~40+ nested properties. The 4 manifest fields are a deliberately-minimal bootstrap surface; the deeper config is mutated by the `audio-hooks` CLI, not by the plugin installer.
  - No `sensitive: true` on webhook_url. Plugin.json doesn't expose a secret-flagged field type, so anyone reading the user's global settings will see the webhook URL in plain text.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1 (matcher `"Bash"`, purpose: matcher-scoped dispatch to `pretooluse` handler — plays audio for Bash tool invocations; observed `async: true, timeout: 10`)
- **PostToolUse hooks**: 1 (matcher `"Bash|Write|Edit"`, dispatches to `posttooluse`). A sibling `PostToolUseFailure` hook (same matcher) dispatches to `posttoolusefailure`.
- **PermissionRequest/PermissionDenied hooks**: observed — `PermissionRequest` (empty matcher) and `PermissionDenied` (no matcher) both registered, dispatch to audio announcements
- **Output convention**: stdout-only JSON (observed — `audio-hooks.py` docstring states "All output is JSON to stdout. No stderr in normal operation"); hook dispatches are fire-and-forget with `async: true`
- **Failure posture**: fail-open — hooks have `async: true` + `timeout: 10`, errors during audio playback don't block the tool call. The Python layer uses `subprocess.Popen` for audio players so nothing waits.
- **Top-level try/catch wrapping**: not inspected line-by-line, but the v5.1.1 bug (`NameError: name 'Tuple' is not defined` at module import crashing every subcommand) suggests no top-level exception wrapping caught it before dispatch. After the fix, CI import-smoke tests every subcommand to catch the regression class.
- **Pitfalls observed**: These hooks are *not* policy enforcement — they are notification hooks. The plugin uses PreToolUse/PostToolUse for audio, not for permission gating. The `PermissionRequest` hook with empty matcher `""` is legal but unusual — contrast with the explicit matcher elsewhere.

## 10. Session context loading

- **SessionStart used for context**: no — used only for audio playback (4 matchers: `startup`, `resume`, `clear`, `compact`, each dispatching to a distinct audio cue)
- **UserPromptSubmit for context**: no — UserPromptSubmit is registered as an audio hook only
- **`hookSpecificOutput.additionalContext` observed**: no (observed — the hooks don't emit additional context back to Claude; they side-effect audio/webhook/TTS)
- **SessionStart matcher**: splits across all 4 sub-events (`startup`, `resume`, `clear`, `compact`). The hooks.json docstring calls this "matcher-scoped hook registration" as a v5.0 design choice — "matcher routing happens in settings.json instead of Python branching."
- **Pitfalls observed**: `SessionStart` with `matcher: "resume"` fires on every resume — since the handler plays a sound, this is one of the hooks most likely to annoy users. The plugin exposes `audio-hooks hooks disable session_start_resume` to mute it, but there's no per-matcher default-off.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no (observed — no `monitors.json` in `plugins/audio-hooks/`)
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: The status line (`audio-hooks-statusline`) is semantically a live monitor — it refreshes and shows context/quota usage — but it's implemented as a Claude Code **status line** (user setting) rather than a plugin monitor. The distinction matters because uninstalling the plugin leaves the statusline registration dangling until the user runs `audio-hooks statusline uninstall`.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no (observed — no `dependencies` in plugin.json)
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: no — tag format is `v5.1.2` (no plugin-name prefix). Not applicable since this is a single-plugin marketplace.
- **Pitfalls observed**: none

## 13. Testing and CI

- **Test framework**: bash scripts + in-CI Python one-liners (observed — `scripts/.internal-tests/test-path-utils.sh` is the only dedicated test file; CI uses ad-hoc `python -c "..."` imports and `audio-hooks.py test all` as the smoke surface)
- **Tests location**: `scripts/.internal-tests/` (single bash test; no `tests/` directory at repo root, confirmed via 404 on `/contents/tests`)
- **Pytest config location**: not applicable (no pytest)
- **Python dep manifest for tests**: not applicable (no test deps)
- **CI present**: yes
- **CI file(s)**: `.github/workflows/smoke.yml` (the only workflow, 1.5 KB)
- **CI triggers**: `push: branches: [master]` and `pull_request` (observed)
- **CI does**:
  - Import-smoke: `python -c "import hook_runner"` against both canonical (`hooks/`) and plugin-copy (`plugins/audio-hooks/hooks/`) paths
  - `audio-hooks.py version / status / diagnose` end-to-end
  - `audio-hooks.py test all` — dispatches every one of 26 hooks
  - `bash scripts/build-plugin.sh --check` — verifies plugin/ is in sync with canonical sources
- **Matrix**: OS × Python — `ubuntu-latest, windows-latest, macos-latest` × `3.9, 3.12, 3.13` (9 combinations, `fail-fast: false`)
- **Action pinning**: tag (observed — `actions/checkout@v4`, `actions/setup-python@v5`; no SHA pinning)
- **Caching**: none (observed — `actions/setup-python@v5` has built-in pip cache but no dep file to cache, so effectively no caching)
- **Test runner invocation**: direct Python one-liners in the workflow steps (no `scripts/test.sh`, no `pytest`, no test runner abstraction)
- **Pitfalls observed**: CI was added *in response to* the v5.1.1 regression — per CHANGELOG 5.1.1: "CI import-smoke workflow to prevent regressions of this class of bug." This is a textbook case of "missing test → ship broken → add test → document why" that the pattern doc could call out explicitly.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no (observed — only `smoke.yml` in workflows)
- **Release trigger**: not applicable (manual)
- **Automation shape**: manual GitHub release creation (observed — 30+ tags, 10+ published releases, no workflow file to create them)
- **Tag-sanity gates**: none automated (the CI `smoke.yml` runs on all pushes, implicitly including tag-commit pushes, but there is no tag-specific workflow). The `plugin-in-sync` CI job is the only automated gate that catches "tag points at commit where plugin copy ≠ canonical source."
- **Release creation mechanism**: manual (inferred — no automation file observed)
- **Draft releases**: all observed releases have `draft: false`
- **CHANGELOG parsing**: no — CHANGELOG.md is maintained by hand in Keep-a-Changelog format, and release notes appear to be hand-written per release based on length and tone
- **Pitfalls observed**: Fully manual release process plus multi-file version sync is exactly the failure mode v5.1.0 hit. No tag-sanity-check, no "refuse to tag if CHANGELOG wasn't updated" guard.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable (no workflow validates marketplace.json schema)
- **Trigger**: not applicable
- **Frontmatter validation**: no (the SKILL.md frontmatter is not validated in CI)
- **Hooks.json validation**: implicit — `audio-hooks.py test all` in CI exercises every hook, which would fail if `hooks.json` pointed at nonexistent handlers. But there is no schema-level validation of the hooks.json shape itself.
- **Pitfalls observed**: CI leans heavily on "does it run?" rather than "does it match schema?" — this catches runtime regressions but not schema drift if Claude Code changes its expected hook event set.

## 16. Documentation

- **`README.md` at repo root**: present (~40 KB — extensive with tables, install instructions, architecture diagram, troubleshooting, uninstall flow, developer section, promo video embed)
- **`README.md` per plugin**: absent (no `plugins/audio-hooks/README.md`; the plugin dir has only plugin.json + hooks/bin/skills/audio/config. Plugin's "docs" is the SKILL.md frontmatter description + the root README.)
- **`CHANGELOG.md`**: present (Keep a Changelog format, 66 KB, explicitly cites keepachangelog.com in the header)
- **`architecture.md`**: present at `docs/ARCHITECTURE.md` (observed — also `docs/INSTALLATION_GUIDE.md` and `docs/TROUBLESHOOTING.md`). Not at plugin root; the repo root owns it.
- **`CLAUDE.md`**: at repo root (~25 KB — the "AI operator instruction manual" for the project; not at plugin root)
- **Community health files**: none observed (no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` at root or in `.github/`)
- **LICENSE**: present (`LICENSE` at root, SPDX `MIT`)
- **Badges / status indicators**: observed (README opens with six shields: License, Version, Platform, Claude Code version floor, Plugin-install banner, five "Share" badges)
- **Pitfalls observed**: No `.github/` community health folder — no issue templates, no PR template, no SECURITY.md. The CLAUDE.md at the repo root is explicitly AI-facing operator docs, not developer onboarding docs.

## 17. Novel axes

- **AI-first operational surface + "manifest" subcommand as self-describing contract.** The `audio-hooks` CLI's `manifest` subcommand returns a JSON description of every subcommand, every config key, every hook, every audio file, and every error code. The SKILL.md explicitly directs Claude to call `audio-hooks manifest` whenever it is unsure — treating the runtime binary as the source of truth over SKILL.md. This is a novel pattern: SKILL.md is deliberately lightweight orientation; the CLI itself carries the current-capability description. Pattern doc could call out "manifest-subcommand self-describing CLI" as a worthwhile design for any plugin that exposes more than a trivial surface.
- **Statusline installed by CLI mutation of user settings, not by plugin manifest.** `audio-hooks statusline install` writes into the user's `~/.claude/settings.json`. This is distinct from the observed patterns in the pattern doc so far — the plugin does not declare statusline capability in plugin.json; it provides a CLI that does the declaration on the user's behalf. Pros: user chooses to opt in explicitly, no surprise UI. Cons: uninstall/upgrade must remember to reverse the mutation or leaves dangling references.
- **Dual-source-tree with `--check` CI gate.** Canonical sources live at `/hooks/`, `/bin/`, `/audio/`, `/config/default_preferences.json`. A second copy lives at `/plugins/audio-hooks/...`. `scripts/build-plugin.sh [--check]` is the diff/sync tool; CI enforces sync. The author explicitly documents the rationale: Claude Code's plugin caching packages the `plugins/<name>/` tree as a unit, so sources bundled there must be self-contained. This is the "monorepo root contains both the authoring tree and the packaged tree" pattern, with a deterministic `cp + cmp -s` reconciler and a `--check` mode for CI.
- **Bash-wrapper-over-Python with interpreter probing instead of shebang-rely.** The `bin/audio-hooks` bash wrapper doesn't rely on the Python shebang; it probes `python3 → python → py`, runs a smoke `python -c "import sys"` to defeat the Microsoft Store `python3.exe` stub on Windows, then execs. This is more defensive than the common `exec python3 "${0%.*}.py"` pattern — and the comment in the source walks through exactly why. Pattern doc could contrast this approach against the "just use `env -S uv run --script` PEP 723" alternative.
- **26 hooks with matcher-scoped routing in hooks.json rather than Python branching.** The `hooks.json` docstring calls out a v5.0 refactor: "matcher routing happens in settings.json instead of Python branching." Each `SessionStart` matcher, each `Notification` matcher, each `StopFailure` matcher gets its own registration with a synthetic handler name (e.g. `session_start_resume`, `notification_permission_prompt`). The Python runner dispatches on the handler name, not the event name. This is a legibility pattern — the hook manifest itself is the source of truth for "which variant triggers which handler" rather than buried in switch statements.
- **Retroactive CI as documented regression response.** The CHANGELOG 5.1.1 explicitly says CI was added because of a specific crash. This makes the repo an unusually clean case study: the commit history shows the exact gap (no CI → broken tag → add CI gate whose failure reproduces the bug). Pattern doc might cite this as a canonical "why you want smoke-level CI even for a plugin with no external deps" example.

## 18. Gaps

- **Did not read all 30 CHANGELOG entries.** Sampled v5.0.0 through v5.1.2 for the pattern evolution. Earlier entries (v1-v4) might reveal design pivots (e.g., when matcher-routing was added, when the `manifest` subcommand was introduced) that would refine the "novel axes" section. Resolvable by reading `CHANGELOG.md` end-to-end.
- **Did not inspect the 60 KB `bin/audio-hooks.py` in full.** I confirmed the shebang, the docstring hard rules, and the `_find_project_root` walker. I did not enumerate all ~27 subcommands or check error-code discipline. Resolvable by reading the full file.
- **Did not inspect `hooks/hook_runner.py` (88 KB).** I confirmed the `CLAUDE_PLUGIN_OPTION_<KEY>` overlay table and saw the Windows audio-duration fix callout. I did not enumerate the full handler set, the NDJSON logging schema, or the rate-limit alert logic. Resolvable by reading the full file.
- **Did not verify platform-specific audio-player fallback chain.** CHANGELOG mentions `mpg123 / ffplay / paplay / aplay` on Linux, `afplay` on macOS, and PowerShell `PresentationCore` / `WMPlayer.OCX` on Windows, but I did not check the exact probing order or the fallback error handling. Resolvable by reading `play_audio_*` functions in `hook_runner.py`.
- **Did not observe actual plugin cache behavior.** Claims that Claude Code's cache adds `bin/` to PATH are inferred from the plugin design (100644 perms + CLI naming) and the README ("bin/ — audio-hooks + statusline"). I did not consult Claude Code internals or the plugin reference docs to confirm the exact PATH-surfacing mechanism for `bin/`. Resolvable by reading `code.claude.com/docs/en/plugins-reference` on bin directories specifically.
- **Did not check the `scripts/.internal-tests/test-path-utils.sh` contents.** The file exists (~8.8 KB) but I did not read it. Resolvable by fetching the file.
- **Did not inspect release-asset layout on GitHub releases.** I confirmed 10+ non-draft releases exist on the API but did not check whether they attach binary artifacts, skill zips, or only source tarballs. Resolvable via `gh api /repos/.../releases/.../assets`.
