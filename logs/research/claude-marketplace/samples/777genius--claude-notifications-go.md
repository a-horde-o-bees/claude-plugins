# 777genius/claude-notifications-go

## Identification

- **URL**: https://github.com/777genius/claude-notifications-go
- **Stars**: 558
- **Last commit date**: 2026-04-19
- **Default branch**: main
- **License**: GPL-3.0 (SPDX `GPL-3.0`; GitHub API reports `NOASSERTION` because the LICENSE header is `GNU GENERAL PUBLIC LICENSE / Version 3, 29 June 2007` with a handwritten copyright line — the `plugin.json` / `marketplace.json` both declare `"license": "GPL-3.0"`)
- **Sample origin**: bin-wrapper
- **One-line purpose**: "Smart notifications for Claude Code with click-to-focus, git branch display, and webhook integrations" — cross-platform desktop + webhook notifications emitted from hook events, backed by a Go binary lazily downloaded from GitHub Releases by a POSIX `/bin/sh` wrapper

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (single-plugin marketplace; the one plugin entry points at `"source": "./"` so the marketplace and plugin share the same root)
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper — no `pluginRoot`
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `category` + `tags` + `keywords` — all three (category `productivity`; tags `["notifications","hooks","alerts","go"]`; keywords `["notifications","alerts","productivity","go","hooks"]`). Note: `keywords` is redundant with `tags` and was pruned from `statuses` config in commit 7dc567b (PR #75, "remove ghost `keywords` field from status config") — that PR targeted runtime status config, not marketplace.json, so `keywords` at marketplace level remains
- **`$schema`**: absent from both marketplace.json and plugin.json
- **Reserved-name collision**: no (`name` is `claude-notifications-go`)
- **Pitfalls observed**: marketplace `metadata.version` and the single plugin's `version` must be kept in lockstep by hand — both read `1.38.0` at the tip and are updated together per release; no tooling enforces it. The plugin's `name` and the marketplace's `name` are identical (`claude-notifications-go`), which means the install string is `claude-notifications-go@claude-notifications-go` — documented in README but visually confusing

## 2. Plugin source binding

- **Source format(s) observed**: relative — `"source": "./"` (the marketplace is the plugin)
- **`strict` field**: absent (default implicit `true`)
- **`skills` override on marketplace entry**: absent (no skills in this plugin; only commands + hooks + bin)
- **Version authority**: both `marketplace.json metadata.version` and `plugin.json version` carry `1.38.0` — the marketplace entry also repeats `version: 1.38.0`. Three separate write sites must stay in sync; no hook or CI check enforces agreement (drift risk is real)
- **Pitfalls observed**: the marketplace entry duplicates `description`, `version`, `author`, `repository`, `license`, `keywords`, `category`, `tags` from plugin.json. If any of these change in plugin.json and not in marketplace.json (or vice versa), the marketplace listing diverges from the installed plugin metadata

## 3. Channel distribution

- **Channel mechanism**: no split — users pin implicitly via marketplace `@ref` (the plugin.json / marketplace.json ship a single version at main's tip; tags `v*` mark releases)
- **Channel-pinning artifacts**: absent — no `stable-tools`/`latest-tools` split, no dev-counter, no release branches. Everything ships from main
- **Pitfalls observed**: the lazy-download wrapper reads plugin.json's `version` field as the source of truth for which binary to fetch from GitHub Releases (see `get_plugin_version` in `hook-wrapper.sh`). A stale marketplace cache pinned to an older commit would still drag the correspondingly older binary version — coherent per commit, but users on `@main` get rolling updates whereas anyone pinning a commit SHA gets a frozen pair

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main (tags `v1.38.0`, `v1.37.0`, `v1.36.7` … are on commits reachable from main; no release branches carry tags). Confirmed by the `ci-ubuntu.yml` / `ci-windows.yml` / `ci-macos.yml` triggers including `main` and `develop` (develop exists? — not listed among branches surveyed, only feature branches) and `release.yml` triggering on `push: tags: ['v*']`
- **Release branching**: none — tag-on-main pattern. Feature branches (`feat/*`, `fix/*`, `chore/*`, `codex/*`) merge to main via PR; tag cut from main; release workflow fires
- **Pre-release suffixes**: none observed in the eight most-recent tags (v1.38.0, v1.37.0, v1.36.7, v1.36.6, v1.36.5, v1.36.4, v1.36.3, v1.36.2)
- **Dev-counter scheme**: absent
- **Pre-commit version bump**: no (no hook detected; CHANGELOG is hand-maintained in Keep-a-Changelog format)
- **Pitfalls observed**: three places carry the version string (`marketplace.json` `metadata.version`, `marketplace.json` `plugins[0].version`, `plugin.json` `version`). The release workflow keys only on the pushed tag (`${{ github.ref_name }}`) for asset tagging — it does not verify the tag matches the three version strings, so a misaligned bump would still publish a release

## 5. Plugin-component registration

- **Reference style in plugin.json**: explicit path arrays for commands (`"commands": ["./commands/init.md", "./commands/settings.md", "./commands/notifications-init.md", "./commands/notifications-settings.md"]`). Hooks are registered by file convention (`hooks/hooks.json` at the plugin root — not referenced from plugin.json). No skills, agents, MCP servers, monitors, or output-styles registered
- **Components observed**:
    - skills — no
    - commands — yes (6 markdown files under `commands/`; plugin.json lists 4 of them; `notifications-sounds.md` and `sounds.md` are present in the directory but not referenced — inferred unused or discoverable by default)
    - agents — no
    - hooks — yes (`hooks/hooks.json` wires PreToolUse/Notification/Stop/SubagentStop/TeammateIdle to `${CLAUDE_PLUGIN_ROOT}/bin/hook-wrapper.sh handle-hook <event>`)
    - .mcp.json — no
    - .lsp.json — no
    - monitors — no
    - bin — yes (`bin/hook-wrapper.sh` POSIX wrapper, `bin/install.sh` installer, `bin/bootstrap.sh` one-shot installer, `bin/claude-notifications` symlink stub, `bin/mock_server.py` + `bin/install_test.sh` + `bin/install_e2e_test.sh` test harness — none of these are exposed as plugin CLI; the `bin/` directory is purely for the hook-wrapper runtime)
    - output-styles — no
- **Agent frontmatter fields used**: not applicable (no agents)
- **Agent tools syntax**: not applicable (no agents). Commands do use `allowed-tools: Bash` frontmatter (plain tool name, not permission-rule syntax)
- **Pitfalls observed**: two orphan commands (`notifications-sounds.md`, `sounds.md`) exist in `commands/` but are not listed in plugin.json's `commands` array. Claude Code's command discovery typically globs the directory, so they may still be exposed — but the explicit-list pattern in plugin.json creates ambiguity about whether the list is authoritative or additive. The codebase uses both `/claude-notifications-go:init` (short) and `/claude-notifications-go:notifications-init` (alias that redirects to `init`) — intentional deprecation path, documented in `notifications-init.md` body

## 6. Dependency installation

- **Applicable**: yes
- **Dep manifest format**: `go.mod` (+ `go.sum`) declares the Go build-time deps used when the release workflow compiles per-platform binaries; at runtime users do **not** run `go build` — they consume pre-built release assets. No requirements.txt / package.json / etc.
- **Install location**: `${CLAUDE_PLUGIN_ROOT}/bin/` — the hook-wrapper's `SCRIPT_DIR` resolves to `<plugin>/bin`, and `INSTALL_TARGET_DIR="$SCRIPT_DIR" "$INSTALL_SCRIPT"` forces `install.sh` to write the binary next to itself. Not `${CLAUDE_PLUGIN_DATA}` — binaries live inside the plugin cache directory
- **Install script location**: `bin/install.sh` (invoked from `bin/hook-wrapper.sh` via `run_install`; also downloadable standalone via `curl … | bash` against `raw.githubusercontent.com`; and exposed through `/claude-notifications-go:init` slash command which fetches the script fresh from main each time)
- **Change detection**: version-file stamp — `${XDG_CACHE_HOME:-$HOME/.cache}/claude-notifications-go/verified-version` caches the last verified binary version; on each hook invocation, the wrapper reads `plugin.json`'s version via `grep -Eo '[0-9]+\.[0-9]+\.[0-9]+'` and compares to the cache. Cache miss → run `claude-notifications version` (costs ~150ms) and compare to plugin.json; mismatch → `run_install --force`. This is a two-tier check: cache file for fast path, binary exec for cold path. A separate `$STAMP_DIR/update-stamp` dedupes the "installed v$X" `systemMessage` (though the message is currently commented out)
- **Retry-next-session invariant**: no `rm` on failure — the wrapper uses `|| true` on every install call and `run_install` pipes stdout/stderr to `/dev/null`. If install fails, binary remains missing, `binary_ok` returns false at the end, wrapper exits `0` silently (Claude never sees the error). Next hook fires → same check cycle retries automatically. Implicit "try every hook until it works" model
- **Failure signaling**: silent by design — `exit 0` unconditionally, `|| true` on every side effect. The wrapper's top comment explicitly states "RELIABILITY: All operations use `|| true` to never block Claude." The commented-out `systemMessage` JSON at the end shows they considered surfacing install/update success to the user but disabled it because "the system message was shown too frequently despite the stamp file." So: no stderr, no stdout JSON, no `continue: false`, no exit 2 — hard fail-open
- **Runtime variant**: Go binary download (per-platform pre-built assets from GitHub Releases — darwin-amd64, darwin-arm64, linux-amd64, linux-arm64, windows-amd64.exe; plus sidecar binaries `sound-preview`, `list-devices`, `list-sounds`; plus macOS `ClaudeNotifier.app.zip` signed and notarized by Apple Developer ID via a keychain import step in `release.yml`)
- **Alternative approaches**: `bootstrap.sh` — separate one-shot installer that `curl | bash`s from raw.githubusercontent.com, populates `~/.claude/plugins/marketplaces/<name>/`, runs `install.sh` directly, and sidesteps the `/plugin` CLI. Exists for users whose Claude Code CLI cannot run `/plugin install` cleanly or who want a single terminal command
- **Version-mismatch handling**: plugin.json version is the source of truth; binary version is read by invoking the binary itself; mismatch triggers `install.sh --force`. No Python/Node ABI tracking — binaries are fully static (Go with `CGO_ENABLED=1` for `malgo` audio, `-ldflags="-s -w" -trimpath`). OS detection is `uname -s` with a fallback to `${OS:-}` (which is `Windows_NT` on every Windows shell even when `uname` is absent). Architecture detection is `uname -m` normalized to `amd64`/`arm64`. Windows-specific handling: prefer downloaded `.exe`, fall back to legacy `.bat` wrapper generated by `install.sh`, call via `cmd.exe /d /s /c call` with `cygpath -w` conversion
- **Pitfalls observed**:
    - Git on Windows with `core.symlinks=false` materializes `bin/claude-notifications` (a symlink pointing to `claude-notifications-darwin-arm64`) as a plain text file containing the string `claude-notifications-darwin-arm64`. The wrapper detects this case (file < 1024 bytes, contents match `claude-notifications-{darwin,linux,windows}-*`) and either resolves the stub or synthesizes a `claude-notifications-MISSING` path to force re-install. This is an explicit cross-platform workaround, not optional
    - The `.gitattributes` file hard-codes `text eol=lf` for `*.sh` and `*.go` and `eol=crlf` for `*.bat` / `*.ps1` — essential for `/bin/sh` wrappers checked in from any OS
    - The symlink target happens to be `claude-notifications-darwin-arm64`, so a Linux user who cloned the repo directly (bypassing the `/plugin install` path) would have a broken symlink — but the hook-wrapper's stub-detection logic self-corrects
    - `INSTALL_TARGET_DIR` env var is passed through the wrapper and also consumed by `install.sh` and `notifications-init.md` — three different call sites share this convention, which is the only mechanism the wrapper uses to override `install.sh`'s default of installing relative to itself

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — primary sample origin for this repo
- **`bin/` files** (actually committed, not the downloaded release assets):
    - `hook-wrapper.sh` — POSIX `/bin/sh` wrapper invoked by every hook; lazy-downloads the binary, dispatches to it, exits 0 unconditionally
    - `install.sh` — Bash installer; detects platform/arch, fetches release asset by name from `https://github.com/777genius/claude-notifications-go/releases/latest/download/`, verifies checksums.txt, writes binary to `$INSTALL_TARGET_DIR` or `$SCRIPT_DIR`, generates Windows `.bat` wrapper if needed
    - `bootstrap.sh` — standalone one-shot `curl | bash` installer; adds marketplace, installs plugin, runs install.sh
    - `claude-notifications` — symlink (stored as symlink in git but materializes as text stub on Windows) pointing to `claude-notifications-darwin-arm64`. Serves as a known filename the wrapper can check first on non-Windows
    - `install_test.sh` — unit tests for install.sh
    - `install_e2e_test.sh` — end-to-end tests for install.sh (offline + mock, optional real-network)
    - `mock_server.py` — Python mock HTTP server used by the E2E test harness to simulate GitHub Releases
- **Shebang convention**: `/bin/sh` for `hook-wrapper.sh` (strict POSIX — they deliberately avoid bashisms in the hot path); `/bin/bash` with `set -e` for `install.sh`, `set -euo pipefail` for `bootstrap.sh`; `#!/usr/bin/env python3` for `mock_server.py`. Mixed shebangs partitioned by role: the hook hot path is POSIX; heavier installer / bootstrap / test tooling uses bash
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback — the wrapper resolves `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` first, then near the end sets `CLAUDE_PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"` only if empty, exports it so the binary can locate resources (`ClaudeNotifier.app`, `sounds/`, `claude_icon.png`), and additionally writes a pointer file to `${CLAUDE_CONFIG_DIR:-${CLAUDE_HOME:-$HOME/.claude}}/claude-notifications-go/plugin-root` for "older cached paths and shim wrappers"
- **Venv handling (Python)**: not applicable — no Python at runtime; `mock_server.py` is a test-only file invoked from the CI harness, not from the hot path
- **Platform support**: OS-detecting runtime — `uname -s` matches `MINGW*|MSYS*|CYGWIN*` and falls back to `$OS` being `Windows_NT`; `uname -m` normalizes arch. POSIX `/bin/sh` wrapper serves all three OS families; Windows branch additionally invokes `cmd.exe /d /s /c call` for `.bat` fallback and prefers a native `.exe` if present. No separate `.cmd` / `.ps1` shim — one script, multi-OS branches inside
- **Permissions**: `hook-wrapper.sh` is 100755 (executable; confirmed by the fact it's invoked directly via `${CLAUDE_PLUGIN_ROOT}/bin/hook-wrapper.sh` without a `bash` prefix in hooks.json). The `bin/claude-notifications` symlink is 120000 (symlink mode). Other scripts follow their shebangs. Pre-install, `setup.sh` explicitly `chmod +x` the wrapper and installer — a defense against checkouts that lost executable bits
- **SessionStart relationship**: not applicable — this plugin does not use a SessionStart hook at all. Lazy download is invoked on every hook fire (PreToolUse / Notification / Stop / SubagentStop / TeammateIdle), so the first hook of a session effectively becomes the bootstrap moment. The design choice is deliberate: the repo's top comment in `hook-wrapper.sh` says "Claude Code plugins don't have post-install hooks, so we use lazy loading." (Note: Claude Code does now have a `SessionStart` hook, but they chose not to migrate — inferred: lazy-at-every-hook is more robust because it also handles the case where the plugin was upgraded mid-session and the binary needs re-download)
- **Pitfalls observed**:
    - The wrapper is POSIX `/bin/sh`, not bash. Authors cannot use `[[ ]]`, arrays, process substitution, or `local`. They use `IFS= read -r VAR <file` instead of `mapfile`, and do manual iteration instead of arrays. This is load-bearing: Debian/Ubuntu point `/bin/sh` at `dash`, not `bash`, and any bashism would crash silently on Linux users
    - The wrapper exits 0 unconditionally. Even if the binary download fails, the hook is a no-op from Claude's perspective. This is a deliberate "never block the user" stance but it means a persistently-broken install is invisible to the user unless they check `$STAMP_DIR/verified-version` or notice the absence of notifications
    - Git symlinks-as-text-files on Windows (core.symlinks=false by default) required the stub-detection code. Anyone copying this pattern needs that code or a different asset-layout scheme
    - The wrapper persists a pointer file at `~/.claude/claude-notifications-go/plugin-root` purely as a fallback for "shim wrappers" — undocumented purpose except via the inline comment; the pattern is brittle if the plugin is uninstalled (the pointer file leaks into `~/.claude`)
    - `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` relies on `cd` working in POSIX sh; if the plugin is installed under a path with special chars this could fail

## 8. User configuration

- **`userConfig` present**: no (no `userConfig` block in plugin.json or marketplace.json)
- **Field count**: none at the Claude Code plugin layer. However, the plugin has a rich user-configurable surface via `config/config.json` (desktop + webhook + statuses + filters) — configuration is edited through the `/claude-notifications-go:settings` slash command rather than through Claude Code's `userConfig` schema
- **`sensitive: true` usage**: not applicable (no `userConfig`)
- **Schema richness**: not applicable (no `userConfig`). Config schema is implicit — validated by the Go binary at runtime rather than declared to Claude Code
- **Reference in config substitution**: `${CLAUDE_PLUGIN_ROOT}` appears in `config/config.json` for resource paths (`"appIcon": "${CLAUDE_PLUGIN_ROOT}/claude_icon.png"`, `"sound": "${CLAUDE_PLUGIN_ROOT}/sounds/task-complete.mp3"`) — expanded by the Go binary, not by Claude Code's `${user_config.KEY}` mechanism
- **Pitfalls observed**: plugin deliberately opts out of `userConfig` in favor of a custom JSON config file. This means Claude Code's built-in UI for plugin settings cannot discover or edit these values — users must run the plugin's own `/claude-notifications-go:settings` command (28KB markdown) to configure. Trade-off: richer schema (webhook presets, per-status overrides, platform-specific flags) vs. not being visible in Claude Code's `/plugin` manager

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1 entry with matcher `ExitPlanMode|AskUserQuestion`, purpose is to fire notifications when Claude asks the user a question or presents a plan (not gating/blocking tool use — purely observational). `timeout: 30` seconds
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent. A `Notification` hook with matcher `permission_prompt` fires on the `Notification` event type — this is not the same as `PermissionRequest` (the `Notification` hook fires for permission prompts as one of several notification sub-types)
- **Output convention**: stdout JSON (the wrapper emits `{"systemMessage":"..."}` when the binary reports output — though the install-completion variant is currently commented out). The Go binary itself presumably produces hook-appropriate JSON; not inspected at source level. No stderr usage for hook signaling observed
- **Failure posture**: fail-open at the wrapper layer (`exit 0` always, `|| true` on all side effects). The Go binary's posture is inferred fail-open too (binary errors are swallowed by `run_binary "$@" || true`)
- **Top-level try/catch wrapping**: the wrapper's entire main body is guarded by `|| true` on every mutating call; there is no explicit `trap` for cleanup, but the shell's POSIX semantics + defensive `|| true` + unconditional `exit 0` achieve the same effect. Go binary source not inspected
- **Pitfalls observed**: because Stop/SubagentStop/TeammateIdle hooks are observational-only (for notification delivery), fail-open is the right posture — but the same wrapper path is used for PreToolUse, where a stricter posture might sometimes be warranted. The author chose uniformity + reliability over conditional enforcement

## 10. Session context loading

- **SessionStart used for context**: no (no SessionStart hook at all)
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no (not emitted by any hook in this plugin — inferred from hook types used and purpose)
- **SessionStart matcher**: not applicable (no SessionStart hook)
- **Pitfalls observed**: the plugin is purely reactive to hook events and injects no context into the model — the notification side effects are user-facing (desktop / webhook), not model-facing. Inferred design choice: notifications are "exit the context, alert the human" not "inform the model about state." This explains why the binary exec cost is acceptable — it runs in a side-channel, not on the model's critical path

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none — this plugin predates or eschews the `monitors.json` schema. All "notifications" are reactive, driven by Claude Code's built-in hook events (Stop, SubagentStop, Notification, TeammateIdle)
- **`when` values used**: not applicable
- **Version-floor declaration**: absent — neither README nor plugin.json nor marketplace.json declares a minimum Claude Code version; the use of `TeammateIdle` (a newer hook event) implicitly floors the plugin at a Claude Code version that supports it, but this is not documented
- **Pitfalls observed**: the plugin's name is "notifications" but it does not use the `monitors.json` notification channel — it uses the hook system directly. Anyone searching for "notifications" as a monitor pattern example would miss this, whereas anyone searching for "how to emit a desktop alert from a hook" would find it. `TeammateIdle` as a hook event is undocumented in the Claude Code plugin reference pages bundled in this research repo — inferred as a newer event added after the public docs were last captured

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — this is a single-plugin marketplace; tags are `v1.38.0` style, plain-semver (no plugin-name prefix)
- **Pitfalls observed**: none — single-plugin marketplace with no cross-plugin coupling

## 13. Testing and CI

- **Test framework**: multiple — `go test` for the Go codebase (`go test -v -race -coverprofile=coverage.txt -covermode=atomic ./...`), bash scripts for installer (`bin/install_test.sh` unit + `bin/install_e2e_test.sh` E2E with Python mock server)
- **Tests location**: inside the Go package tree (colocated `*_test.go` files — standard Go convention); `bin/install_{test,e2e_test}.sh` for installer tests at the plugin root
- **Pytest config location**: not applicable (no pytest)
- **Python dep manifest for tests**: not applicable (no Python at test time — `mock_server.py` uses only stdlib)
- **CI present**: yes
- **CI file(s)**: `ci-ubuntu.yml`, `ci-macos.yml`, `ci-windows.yml` (per-OS matrix instead of one file with an OS matrix), plus `notifier-signing-smoke.yml` (macOS-only Developer ID signing + notarization smoke test) and `release.yml`
- **CI triggers**: `push` to `main, develop`; `pull_request` to `main`. Release triggers on `push: tags: 'v*'`. Notifier-signing-smoke on `push: tags: 'smoke-notary-*'` or `workflow_dispatch`
- **CI does**: `go vet`, `go fmt` check (fails if diff), `go test -race`, `golangci-lint` (Ubuntu only as a separate job), `codecov` upload (Go 1.21 only), build binary + run `help` smoke, run `install_test.sh`, run `install_e2e_test.sh` (offline + mock, then optional real-network with `continue-on-error`)
- **Matrix**: Go × OS (Go 1.21 + 1.22 × {ubuntu-latest, macos-latest, windows-latest}; release builds use a larger matrix adding `macos-15-intel`, `ubuntu-24.04-arm` to cover Apple Silicon + Intel macOS and amd64 + arm64 Linux)
- **Action pinning**: tag — `actions/checkout@v4`, `actions/setup-go@v4`, `actions/upload-artifact@v4`, `codecov/codecov-action@v3`, `softprops/action-gh-release@v1`, `robinraju/release-downloader@v1.8`, `golangci/golangci-lint-action@v3`. No SHA pinning observed
- **Caching**: built-in `setup-go` caching (implicit — `setup-go@v4` ships with module cache support enabled by default; no explicit `cache: true` needed). No `actions/cache` blocks for Go modules; the `Clear Go cache` step (`go clean -modcache`) explicitly invalidates, suggesting they want deterministic builds over cache speedup
- **Test runner invocation**: direct `go test` / `go vet` / `go fmt`; `bash bin/install_test.sh` for installer. No Make-style wrapper in CI (though `Makefile` exists for local dev)
- **Pitfalls observed**:
    - Three separate OS CI files is a deliberate choice vs. one with matrix `os: [ubuntu, macos, windows]` — likely because steps diverge significantly (Ubuntu installs `libasound2-dev`, Windows uses `shell: pwsh` for go-fmt, macOS runs extra sound-preview build). Per-OS files trade DRY for readability
    - `go test -race` with `malgo` (CGO audio) on all three OSes means the matrix exercises CGO threading — race detection is meaningful. Windows CI matrix drops `arm64` because CGO doesn't cross-compile there
    - Real-network E2E test is `continue-on-error: true` with a 5-minute timeout — CI won't fail on GitHub outage, but a silent regression in real GitHub Release layout could slip past

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes
- **Release trigger**: `push: tags: ['v*']`
- **Automation shape**: Go/Rust binary build + attach — specifically a four-job pipeline:
    1. `build-matrix` — compiles `claude-notifications`, `sound-preview`, `list-devices`, `list-sounds` per platform×arch (5 combos) with `CGO_ENABLED=1`, `go build -ldflags="-s -w" -trimpath`, uploads as artifacts
    2. `build-notifier` — macOS-only; imports Apple `.p12` certificate into a fresh keychain, runs `swift-notifier/scripts/build-app.sh --ci` to build, sign (Developer ID), and notarize `ClaudeNotifier.app`, uploads zip
    3. `create-release` — downloads all artifacts, `sha256sum * > checksums.txt`, `softprops/action-gh-release@v1` with `generate_release_notes: true`
    4. `test-binaries` — downloads the just-published release, runs `./<binary> version` on each of ubuntu/macos/windows
- **Tag-sanity gates**: none explicit — the workflow does not verify the tag matches `plugin.json` version, does not check it's on main, does not enforce a semver regex beyond the `v*` filter. Tag discipline is manual (or enforced by a local pre-commit / CHANGELOG-review process not surfaced in CI)
- **Release creation mechanism**: `softprops/action-gh-release@v1` with `generate_release_notes: true`, `draft: false`, `prerelease: false`
- **Draft releases**: no — released immediately on tag push
- **CHANGELOG parsing**: no — relies on `generate_release_notes: true` (GitHub auto-generates from commit messages / PRs). CHANGELOG.md is maintained by hand but is not parsed by the release workflow
- **Pitfalls observed**:
    - `test-binaries` happens *after* the release is published. If a platform's binary is broken, it's already live in the release. This is a post-release smoke test, not a gate
    - Apple notarization is fragile — the keychain-import step does platform-specific `base64 --decode` vs `base64 -D` fallback for the cert, and requires `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_PASSWORD`, `APPLE_TEAM_ID` secrets
    - `checksums.txt` is emitted per-release but the `install.sh` checksum verification path is optional in the wrapper (`CHECKSUMS_URL` can be overridden) — no end-to-end enforcement that every installed user verifies
    - No tag-format regex gate — a malformed tag like `v1.38` (two-component) or `v1.38.0-beta.1` would still trigger the workflow

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: no (commands have YAML frontmatter — `description`, `allowed-tools` — but no CI step validates it)
- **Hooks.json validation**: no (no JSON schema check or structural validator)
- **Pitfalls observed**: the marketplace.json + plugin.json pair is not validated by CI. A bad commit that corrupts these would not fail CI — it would fail at install time on a user's machine. Given the repo has 558 stars + broad user base, this is a meaningful gap (easy to patch with `jq -e` or `claude plugin validate`)

## 16. Documentation

- **`README.md` at repo root**: present (~17.9KB — covers features, installation, supported notification types, platform support, click-to-focus matrix of terminal apps, configuration, sounds, testing, contributing, troubleshooting)
- **`README.md` per plugin**: not applicable — single-plugin marketplace, the repo README serves the plugin
- **`CHANGELOG.md`**: present, Keep a Changelog format ("The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)" — explicit declaration in the file; entries organized as `### Added` / `### Fixed` / `### Changed` under `## [x.y.z] - YYYY-MM-DD` headers)
- **`architecture.md`**: at `docs/ARCHITECTURE.md` (not at repo root; the docs/ directory carries it). Inferred: the repo follows a `docs/` convention for all non-README documentation
- **`CLAUDE.md`**: absent
- **Community health files**: `CONTRIBUTING.md` (4.8KB), `LICENSE` (GPL-3.0), `.github/ISSUE_TEMPLATE/` directory present. No `SECURITY.md` or `CODE_OF_CONDUCT.md` observed
- **LICENSE**: present (GPL-3.0 — confirmed by file header `GNU GENERAL PUBLIC LICENSE / Version 3, 29 June 2007 / Copyright (C) 2025 777genius`; GitHub API returns `NOASSERTION` because the copyright line format differs from the standard template, but the SPDX identifier in plugin.json is `GPL-3.0`)
- **Badges / status indicators**: observed — README opens with 5 badges: Ubuntu CI, macOS CI, Windows CI, Go Report Card, Codecov. Uses `shields.io`-style GitHub workflow badges
- **Pitfalls observed**:
    - `docs/issues/` is a directory of markdown files (inferred per-issue design notes) — unusual pattern; most repos use GitHub Issues for this, keeping markdown in `docs/` for stable docs
    - The README's install instructions offer three paths (bootstrap curl-pipe, manual `/plugin` slash commands, and the classic marketplace add) which is user-friendly but creates maintenance surface — the bootstrap script + install.sh + `/claude-notifications-go:init` command all implement similar logic and must stay in lockstep
    - `.orphaned_at` file at repo root contains a Unix millisecond timestamp (1766603417062 → 2025-12-24) — purpose unclear; possibly a marker left by some tooling and not meaningful to current ops. Inferred (not confirmed)

## 17. Novel axes

- **Lazy-binary-download from POSIX `/bin/sh` wrapper on every hook** — the wrapper is the sole binary-availability gate; there is no SessionStart hook, no post-install hook, no background job. Every one of the five hook events (PreToolUse, Notification, Stop, SubagentStop, TeammateIdle) triggers the same `hook-wrapper.sh`, and the wrapper decides whether to download/update/skip. Version-cache file short-circuits the binary-launch cost to ~0ms on the happy path after first warmup. This trades "slightly more work on cold start" for "self-healing on every hook + no dependency on any one lifecycle event firing." Distinctive because most bin-wrapper plugins gate download behind SessionStart
- **POSIX `/bin/sh` enforcement (not bash) in the hot path** — deliberate anti-bash discipline in `hook-wrapper.sh` because `/bin/sh` on Debian/Ubuntu is `dash`, and any bashism would fail silently. The installer (`install.sh`) and bootstrap (`bootstrap.sh`) are bash, but the hot path is strict POSIX. Partitions scripts by criticality: hot path = POSIX portable, one-shot paths = bash-rich
- **OS detection dual-fallback** — `uname -s` primary, `$OS` env var (`Windows_NT`) fallback. Covers the case where a Windows user is in a non-MSYS shell without `uname` available. Pattern worth codifying: don't trust one probe on Windows
- **Git text-symlink stub detection** — Git on Windows with `core.symlinks=false` creates plain text files containing the symlink target string. The wrapper detects these (size < 1KB, contents match a known binary-name pattern) and either resolves to the real target or synthesizes a `MISSING` path to force re-install. Unique cross-platform workaround for a git-setting difference that most plugin authors don't realize can happen
- **Dual version cache** — separate cache for "plugin.json version matches cached known-good version" (fast path, skip binary launch) vs. "install-completion stamp keyed on version+force flag" (dedupe systemMessages). Two-layer cache explicitly named and managed. More sophisticated than most installer scripts
- **Plugin-root pointer file outside the plugin cache** — `${CLAUDE_CONFIG_DIR:-~/.claude}/claude-notifications-go/plugin-root` carries the current resolved path for "shim wrappers" and "older cached paths." Write-through only on change (prev-pointer comparison + atomic rename). Novel cross-session breadcrumb for a binary that might be invoked from multiple plugin-root paths over its lifetime
- **Apple Developer ID signing + notarization in the release workflow** — few Claude Code plugins need this, but the macOS Notification Center click-to-focus feature requires an `.app` bundle signed with a Developer ID certificate to function reliably. The `release.yml` imports a P12 cert, creates a fresh keychain, runs `security set-key-partition-list`, and invokes `build-app.sh --ci`. Dedicated smoke-test workflow (`notifier-signing-smoke.yml`) triggered by `smoke-notary-*` tags lets maintainers validate signing pipeline changes without cutting a real release
- **Per-OS CI file split instead of matrix** — `ci-ubuntu.yml` / `ci-macos.yml` / `ci-windows.yml` as three separate files with significantly different steps (Linux installs libasound2-dev; Windows uses pwsh for fmt check; macOS builds sound-preview sidecar). Trade-off against a single `ci.yml` with `matrix.os` — readability wins when per-OS steps are genuinely different

## 18. Gaps

- **Go binary hook output format** — not inspected. The wrapper emits a commented-out `{"systemMessage":"..."}` JSON envelope and then the binary's stdout/stderr is passed through. Whether the Go binary emits `hookSpecificOutput.additionalContext` or returns `continue: false` is unknown without reading `cmd/claude-notifications/main.go` and the internal hook-dispatch package (`internal/hooks/` presumably). Would require fetching at least `cmd/claude-notifications/main.go` (5.8KB) and exploring `internal/`
- **`.orphaned_at` file purpose** — contains `1766603417062` (Unix ms timestamp; resolves to 2025-12-24). Possibly a marker from some tooling (plugin-garbage-collection? orphan-marketplace tracker?). Not referenced in any file I inspected. Would need to grep across the full repo to find any consumer of this file, or ask the maintainer
- **`develop` branch presence and role** — CI workflows trigger on `push` to `main, develop`, but the branch list I queried showed no `develop` branch. Either it's been deleted and the workflow is stale, or the branch list was truncated by the API default pagination. Would need an explicit `gh api repos/.../branches --paginate` to confirm
- **Orphan commands** — `commands/notifications-sounds.md` and `commands/sounds.md` exist but are not in `plugin.json`'s `commands` array. Whether Claude Code's command discovery picks them up anyway (globbing the dir) or whether the explicit array is authoritative requires reading the plugin-reference docs more carefully than I did in this pass
- **Marketplace-level vs plugin-level version drift history** — three sites carry the version string and no tooling enforces agreement. Whether this has caused bugs in the past (or whether there's informal discipline around a release checklist) is not surfaced in the visible commit messages; would require scanning all 38 recent tags' commit diffs to see
- **`internal/` package structure** — not inspected (would add 5-10 API calls to enumerate). Likely organized as `internal/{config,hooks,notifier,webhook,terminal,...}` based on the feature surface, but the specific layout choices (and whether there's a plugin-Code-facing API layer separate from the Go domain) are unknown
- **Whether `bin/claude-notifications` (the symlink) is actually invoked** — the wrapper logic prefers platform-suffixed binaries (`claude-notifications-linux-amd64` etc.) and only falls back to the plain `claude-notifications` name implicitly. The symlink's role seems to be: on a macOS-arm64 clone (where the symlink resolves), the plain name happens to point at the right binary so setup-from-source works. On other platforms, it resolves to nothing and the platform-suffixed name is used instead. Not verified by reading install.sh end-to-end
