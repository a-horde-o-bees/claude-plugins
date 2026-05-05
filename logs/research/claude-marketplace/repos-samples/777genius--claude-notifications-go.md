# Sample

Mirrors of `https://github.com/777genius/claude-notifications-go`. Smart desktop and webhook notifications for Claude Code with click-to-focus, git branch display, and webhook integrations — emitted from hook events, backed by a Go binary lazily downloaded from GitHub Releases by a POSIX `/bin/sh` wrapper. GPL-3.0 licensed; 558 stars at sample time.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

A single `.claude-plugin/marketplace.json` at repo root with one plugin entry whose `source` is `"./"` — the marketplace and plugin share the same repo root. Plugin `name` and marketplace `name` are identical (`claude-notifications-go`), producing the install string `claude-notifications-go@claude-notifications-go` (documented in README but visually confusing).

### Top-level `metadata` wrapper variants

Marketplace declares `metadata.{description, version}` wrapper. `metadata.pluginRoot` is absent. `metadata.version` and the single plugin's `version` both read `1.38.0` at the tip and are kept in lockstep by hand; the marketplace entry also repeats `version: 1.38.0`. Three separate write sites must stay in sync; no hook or CI check enforces it.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry; plugin root and repo root are the same path. `strict` is absent (default implicit `true`). The marketplace entry duplicates `description`, `version`, `author`, `repository`, `license`, `keywords`, `category`, `tags` from `plugin.json`.

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

All three dimensions populated: `category: "productivity"`, `tags: ["notifications","hooks","alerts","go"]`, `keywords: ["notifications","alerts","productivity","go","hooks"]`. `keywords` is redundant with `tags`. PR #75 (commit 7dc567b) titled "remove ghost `keywords` field from status config" pruned `keywords` from runtime status config, but `keywords` at marketplace level remains. The marketplace entry mirrors fields from `plugin.json`.

### `$schema` absence on per-plugin manifests

`$schema` is absent from both `marketplace.json` and `plugin.json`.

## Version coordination

### Triple-file version (build manifest joins)

Three sites carry the version: `marketplace.json metadata.version`, `marketplace.json plugins[0].version`, and `plugin.json version` — all `1.38.0` at tip. Drift mitigation is procedural — by hand-discipline. The release workflow keys only on the pushed tag (`${{ github.ref_name }}`) for asset tagging and does not verify the tag matches the three version strings, so a misaligned bump would still publish a release.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split. Users pin implicitly via marketplace `@ref`; the `plugin.json`/`marketplace.json` ship a single version at main's tip, tags `v*` mark releases. Everything ships from `main`. The lazy-download wrapper reads `plugin.json`'s `version` field as the source of truth for which binary to fetch from GitHub Releases (via `get_plugin_version` in `hook-wrapper.sh`); a stale marketplace cache pinned to an older commit drags the correspondingly older binary version. Users on `@main` get rolling updates; anyone pinning a commit SHA gets a frozen pair.

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

Tags `v1.38.0`, `v1.37.0`, `v1.36.7`, `v1.36.6`, `v1.36.5`, `v1.36.4`, `v1.36.3`, `v1.36.2` on commits reachable from main; no release branches carry tags. Feature branches (`feat/*`, `fix/*`, `chore/*`, `codex/*`) merge to main via PR; tag cut from main; release workflow fires on `push: tags: ['v*']`. CI workflows trigger on `push` to `main, develop` and `pull_request` to `main`. No pre-release suffixes observed in the eight most-recent tags. No automated pre-commit version bump.

## Plugin-component registration

### Explicit per-component path arrays

`plugin.json` declares `"commands": ["./commands/init.md", "./commands/settings.md", "./commands/notifications-init.md", "./commands/notifications-settings.md"]` (4 explicit paths). Hooks are registered by file convention (`hooks/hooks.json` at the plugin root, not referenced from `plugin.json`). Two orphan commands (`commands/notifications-sounds.md`, `commands/sounds.md`) exist in `commands/` but are not listed in `plugin.json`. The codebase exposes both `/claude-notifications-go:init` (short) and `/claude-notifications-go:notifications-init` (alias that redirects to `init`) — intentional deprecation path documented in `notifications-init.md` body.

## Component composition

### Commands

6 markdown files under `commands/`; `plugin.json` lists 4 of them. `notifications-sounds.md` and `sounds.md` are present in the directory but not referenced. Commands use `allowed-tools: Bash` frontmatter (plain tool name, not permission-rule syntax).

### Hooks

`hooks/hooks.json` wires PreToolUse (matcher `ExitPlanMode|AskUserQuestion`), Notification, Stop, SubagentStop, and TeammateIdle to `${CLAUDE_PLUGIN_ROOT}/bin/hook-wrapper.sh handle-hook <event>`.

### bin

Multiple committed scripts: `bin/hook-wrapper.sh` (POSIX wrapper), `bin/install.sh` (installer), `bin/bootstrap.sh` (one-shot installer), `bin/claude-notifications` (symlink stub), `bin/mock_server.py` + `bin/install_test.sh` + `bin/install_e2e_test.sh` (test harness). None exposed as plugin CLI; `bin/` is purely the hook-wrapper runtime.

## Server runtime (MCP)

### No bin entry / direct invocation

No MCP server registered. Hooks invoke `${CLAUDE_PLUGIN_ROOT}/bin/hook-wrapper.sh handle-hook <event>` directly.

## Bin entry mechanism

### Pre-built binary download (lazy, per-hook)

Runtime is a Go binary downloaded from GitHub Releases on demand. Build-time deps live in `go.mod`; users never compile. The binary is materialized into `${CLAUDE_PLUGIN_ROOT}/bin/` (the wrapper's `SCRIPT_DIR` resolves to `<plugin>/bin`, and `INSTALL_TARGET_DIR="$SCRIPT_DIR" "$INSTALL_SCRIPT"` forces `install.sh` to write the binary next to itself — not `${CLAUDE_PLUGIN_DATA}`). Lazy download invoked on every hook fire (PreToolUse / Notification / Stop / SubagentStop / TeammateIdle); no SessionStart hook. The wrapper's top comment states "Claude Code plugins don't have post-install hooks, so we use lazy loading" — the design choice is deliberate: lazy-at-every-hook also handles the case where the plugin was upgraded mid-session and the binary needs re-download. Wrapper resolves `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` first, then near the end sets `CLAUDE_PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"` only if empty, exports it so the binary can locate resources (`ClaudeNotifier.app`, `sounds/`, `claude_icon.png`), and writes a pointer file to `${CLAUDE_CONFIG_DIR:-${CLAUDE_HOME:-$HOME/.claude}}/claude-notifications-go/plugin-root` for "older cached paths and shim wrappers". Wrapper is `/bin/sh` POSIX (not bash) — no `[[ ]]`, arrays, process substitution, or `local`; uses `IFS= read -r VAR <file` instead of `mapfile`. `hook-wrapper.sh` is mode 100755; the `bin/claude-notifications` symlink is mode 120000. `setup.sh` explicitly `chmod +x` the wrapper and installer.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

`hook-wrapper.sh` resolves `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"`, then `CLAUDE_PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"` only if the env var is empty. Pointer file at `${CLAUDE_CONFIG_DIR:-${CLAUDE_HOME:-$HOME/.claude}}/claude-notifications-go/plugin-root` is written through "only on change".

## Dependency installation

### Native binary downloaded on first use with version-stamp idempotency

`go.mod` (+ `go.sum`) declares the Go build-time deps used when the release workflow compiles per-platform binaries; at runtime users do not run `go build` — they consume pre-built release assets (`claude-notifications-darwin-amd64`, `claude-notifications-darwin-arm64`, `claude-notifications-linux-amd64`, `claude-notifications-linux-arm64`, `claude-notifications-windows-amd64.exe`, plus sidecar binaries `sound-preview`, `list-devices`, `list-sounds`, plus macOS `ClaudeNotifier.app.zip` signed and notarized by Apple Developer ID). `bin/install.sh` (Bash, `set -e`) detects platform/arch, fetches release asset by name from `https://github.com/777genius/claude-notifications-go/releases/latest/download/`, verifies `checksums.txt`, writes binary to `$INSTALL_TARGET_DIR` or `$SCRIPT_DIR`, generates Windows `.bat` wrapper if needed. `bin/bootstrap.sh` (Bash, `set -euo pipefail`) is a standalone one-shot `curl | bash` installer that adds the marketplace, installs the plugin, runs `install.sh`. The `/claude-notifications-go:init` slash command fetches the script fresh from main each time. `INSTALL_TARGET_DIR` env var is consumed by both the wrapper and `install.sh` and `notifications-init.md` — three call sites share this convention to override `install.sh`'s default of installing relative to itself. OS detection is `uname -s` with a fallback to `${OS:-}` (which is `Windows_NT` on every Windows shell even when `uname` is absent). Architecture detection is `uname -m` normalized to `amd64`/`arm64`. Windows-specific handling: prefer downloaded `.exe`, fall back to legacy `.bat` wrapper generated by `install.sh`, call via `cmd.exe /d /s /c call` with `cygpath -w` conversion. Binaries are fully static (Go with `CGO_ENABLED=1` for `malgo` audio, `-ldflags="-s -w" -trimpath`).

## Install change detection

### Two-tier version cache (file + binary self-report)

`${XDG_CACHE_HOME:-$HOME/.cache}/claude-notifications-go/verified-version` caches the last verified binary version. On each hook invocation, the wrapper reads `plugin.json`'s version via `grep -Eo '[0-9]+\.[0-9]+\.[0-9]+'` and compares to the cache. Cache miss → run `claude-notifications version` (~150ms) and compare to `plugin.json`; mismatch → `run_install --force`. A separate `$STAMP_DIR/update-stamp` dedupes the "installed v$X" `systemMessage` (the message itself is currently commented out). Git on Windows with `core.symlinks=false` materializes `bin/claude-notifications` (a symlink pointing to `claude-notifications-darwin-arm64`) as a plain text file containing the string `claude-notifications-darwin-arm64`; the wrapper detects this case (file < 1024 bytes, contents match `claude-notifications-{darwin,linux,windows}-*`) and either resolves the stub or synthesizes a `claude-notifications-MISSING` path to force re-install.

## Install trigger and lifecycle

### Lazy bootstrap on first hook (no SessionStart)

No SessionStart hook. The first hook fired in a session (PreToolUse / Notification / Stop / SubagentStop / TeammateIdle) effectively becomes the bootstrap moment. Every subsequent hook also re-checks via the version cache fast path.

## Install failure posture

### Silent fail-open (`exit 0` always, retry every hook)

The wrapper uses `|| true` on every install call and `run_install` pipes stdout/stderr to `/dev/null`. If install fails, binary remains missing, `binary_ok` returns false at the end, wrapper exits `0` silently (Claude never sees the error). The wrapper's top comment explicitly states "RELIABILITY: All operations use `|| true` to never block Claude." The commented-out `systemMessage` JSON shows they considered surfacing install/update success but disabled it because "the system message was shown too frequently despite the stamp file." Hard fail-open; next hook fires → same check cycle retries automatically.

## User configuration and authentication

### Out-of-band env vars (no `userConfig`)

No `userConfig` block in `plugin.json` or `marketplace.json`. Configuration lives in `config/config.json` (desktop + webhook + statuses + filters) — edited through the `/claude-notifications-go:settings` slash command rather than through Claude Code's `userConfig` schema. Schema is implicit; validated by the Go binary at runtime rather than declared to Claude Code.

### Custom env-var substitution in hooks.json

`${CLAUDE_PLUGIN_ROOT}` appears in `config/config.json` for resource paths (`"appIcon": "${CLAUDE_PLUGIN_ROOT}/claude_icon.png"`, `"sound": "${CLAUDE_PLUGIN_ROOT}/sounds/task-complete.mp3"`) — expanded by the Go binary, not by Claude Code's `${user_config.KEY}` mechanism.

## Tool-use enforcement

### Observational notification trigger

One PreToolUse hook with matcher `ExitPlanMode|AskUserQuestion`, purpose: fire desktop or webhook notifications when Claude reaches a decision point. Not gating — never emits deny. `timeout: 30` to avoid hanging the host. A `Notification` hook with matcher `permission_prompt` fires on the `Notification` event type for permission prompts as one of several notification sub-types. Stop / SubagentStop / TeammateIdle hooks are observational-only (for notification delivery).

## Hook handler runtime

### Bash scripts at conventional path

Hot-path script `hook-wrapper.sh` runs under `/bin/sh` (deliberately POSIX, not bash). Shebangs partitioned by role: `/bin/sh` for `hook-wrapper.sh` (strict POSIX); `/bin/bash` with `set -e` for `install.sh`; `set -euo pipefail` for `bootstrap.sh`; `#!/usr/bin/env python3` for `mock_server.py`. The Go binary handles in-hook protocol; hook handlers stream its output through.

## Hook output contract

### `systemMessage` for human-readable summaries

Wrapper emits `{"systemMessage":"..."}` when the binary reports output (the install-completion variant is currently commented out). The Go binary itself produces hook-appropriate JSON; not inspected at source level. No stderr usage for hook signaling observed.

## Hook failure posture

### Silent fail-open (`exit 0` always, retry every hook)

`exit 0` unconditionally; `|| true` on all side effects. The wrapper's entire main body is guarded by `|| true` on every mutating call. No explicit `trap` for cleanup; the shell's POSIX semantics + defensive `|| true` + unconditional `exit 0` achieve the same effect. Go binary errors are swallowed by `run_binary "$@" || true`.

## Session context loading

### No session-context loading

No SessionStart hook. The plugin is purely reactive to hook events and injects no context into the model — notification side effects are user-facing (desktop / webhook), not model-facing. The notification design is "exit the context, alert the human" not "inform the model about state." This is why the binary exec cost is acceptable — it runs in a side-channel, not on the model's critical path.

## Live monitoring

### `monitors.json` absent

No `monitors.json` in the repo. All "notifications" are reactive, driven by Claude Code's built-in hook events (Stop, SubagentStop, Notification, TeammateIdle). The plugin's name is "notifications" but it does not use the `monitors.json` notification channel — uses the hook system directly. `TeammateIdle` as a hook event implicitly floors the plugin at a Claude Code version that supports it; not declared in README, `plugin.json`, or `marketplace.json`.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field. Single-plugin marketplace; tags are `v1.38.0` style with no plugin-name prefix. No cross-plugin coupling.

## Testing

### Go test

`go test -v -race -coverprofile=coverage.txt -covermode=atomic ./...`. Colocated `*_test.go` files alongside source per Go convention. CGO-enabled tests (`malgo` for audio) exercise `-race` across all OSes (ubuntu, macos, windows). Coverage uploaded to codecov on Go 1.21 only; coverage threshold not enforced.

### Shell script tests (installer harness)

`bin/install_test.sh` (unit tests for `install.sh`) and `bin/install_e2e_test.sh` (end-to-end with offline + mock, optional real-network) for the install flow itself, with Python stdlib mock HTTP server (`bin/mock_server.py`) standing in for GitHub Releases. Real-network E2E test is `continue-on-error: true` with a 5-minute timeout — CI won't fail on GitHub outage, but a silent regression in real GitHub Release layout could slip past.

## CI workflow shape

### Per-OS workflow files (deliberate split)

Three separate CI files (`ci-ubuntu.yml`, `ci-macos.yml`, `ci-windows.yml`) instead of one with `matrix.os` because steps diverge significantly: Ubuntu installs `libasound2-dev`; Windows uses `shell: pwsh` for `go fmt`; macOS runs extra `sound-preview` build. Plus `notifier-signing-smoke.yml` (macOS-only Developer ID signing + notarization smoke test) and `release.yml`. CI triggers: `push` to `main, develop`; `pull_request` to `main`. Release triggers `push: tags: 'v*'`. Notifier-signing-smoke triggers `push: tags: 'smoke-notary-*'` or `workflow_dispatch`. Steps include `go vet`, `go fmt` check (fails if diff), `go test -race`, `golangci-lint` (Ubuntu only as separate job), `codecov` upload (Go 1.21 only), build binary + run `help` smoke, run `install_test.sh`, run `install_e2e_test.sh`. Matrix Go × OS: Go 1.21 + 1.22 × {ubuntu-latest, macos-latest, windows-latest}; release builds use a larger matrix adding `macos-15-intel`, `ubuntu-24.04-arm`. Action pinning by tag — `actions/checkout@v4`, `actions/setup-go@v4`, `actions/upload-artifact@v4`, `codecov/codecov-action@v3`, `softprops/action-gh-release@v1`, `robinraju/release-downloader@v1.8`, `golangci/golangci-lint-action@v3`. No SHA pinning. Built-in `setup-go` caching (implicit). `Clear Go cache` step (`go clean -modcache`) explicitly invalidates. `go test -race` with `malgo` (CGO audio) on all three OSes means the matrix exercises CGO threading. Windows CI matrix drops `arm64` because CGO doesn't cross-compile there. Test runner invocation is direct `go test` / `go vet` / `go fmt`; `bash bin/install_test.sh` for installer (a `Makefile` exists for local dev but isn't used in CI).

## Marketplace validation

### No validation

No validation workflow. No `jq -e` or `claude plugin validate` step. Commands have YAML frontmatter (`description`, `allowed-tools`) but no CI step validates them. `hooks.json` shape is unchecked. The `marketplace.json` + `plugin.json` pair would corrupt at install time on a user's machine rather than fail CI.

## Release automation

### Tag-triggered binary build + GH Release with signing

Workflow triggered on `push: tags: ['v*']`, four-job pipeline: (1) `build-matrix` compiles `claude-notifications`, `sound-preview`, `list-devices`, `list-sounds` per platform×arch (5 combos) with `CGO_ENABLED=1`, `go build -ldflags="-s -w" -trimpath`, uploads as artifacts; (2) `build-notifier` (macOS-only) imports Apple `.p12` certificate into a fresh keychain, runs `swift-notifier/scripts/build-app.sh --ci` to build, sign (Developer ID), and notarize `ClaudeNotifier.app`, uploads zip; (3) `create-release` downloads all artifacts, `sha256sum * > checksums.txt`, `softprops/action-gh-release@v1` with `generate_release_notes: true`, `draft: false`, `prerelease: false`; (4) `test-binaries` downloads the just-published release, runs `./<binary> version` on each of ubuntu/macos/windows. `test-binaries` happens *after* the release is published — post-release smoke test, not a gate. Apple notarization keychain-import does platform-specific `base64 --decode` vs `base64 -D` fallback for the cert and requires `APPLE_CERTIFICATE`, `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_PASSWORD`, `APPLE_TEAM_ID` secrets. `checksums.txt` is emitted per-release but the `install.sh` checksum verification path is optional in the wrapper (`CHECKSUMS_URL` can be overridden) — no end-to-end enforcement that every installed user verifies. No tag-format regex gate — a malformed tag like `v1.38` or `v1.38.0-beta.1` would still trigger the workflow. The release workflow keys only on `${{ github.ref_name }}` for asset tagging; it does not verify the tag matches `plugin.json` version, that the tag is on main, or enforce a semver regex beyond the `v*` filter.

## Documentation surface

### Substantial root README + CHANGELOG + community files + badges

`README.md` (~17.9KB) covers features, installation, supported notification types, platform support, click-to-focus matrix of terminal apps, configuration, sounds, testing, contributing, troubleshooting. README opens with 5 badges: Ubuntu CI, macOS CI, Windows CI, Go Report Card, Codecov (shields.io-style GitHub workflow badges). README install instructions offer three paths (bootstrap curl-pipe, manual `/plugin` slash commands, classic marketplace add). `CHANGELOG.md` follows Keep a Changelog format ("The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)" — explicit declaration); entries organized as `### Added` / `### Fixed` / `### Changed` under `## [x.y.z] - YYYY-MM-DD`. `docs/ARCHITECTURE.md` (off-root, by docs-directory convention). `CONTRIBUTING.md` (4.8KB), `LICENSE` (GPL-3.0), `.github/ISSUE_TEMPLATE/` directory present. `docs/issues/` is a directory of markdown files (per-issue design notes). No `CLAUDE.md`. No `SECURITY.md` or `CODE_OF_CONDUCT.md`. `.orphaned_at` file at repo root contains a Unix millisecond timestamp (1766603417062 → 2025-12-24); purpose unclear.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` at repo root (GPL-3.0; file header `GNU GENERAL PUBLIC LICENSE / Version 3, 29 June 2007 / Copyright (C) 2025 777genius`). `plugin.json` / `marketplace.json` both declare `"license": "GPL-3.0"`. GitHub API returns `NOASSERTION` because the copyright line format differs from the standard template, but the SPDX identifier in `plugin.json` is `GPL-3.0`.

## Community health files

### Open contribution with health files

`CONTRIBUTING.md` (4.8KB), `LICENSE` (GPL-3.0), `.github/ISSUE_TEMPLATE/` directory present. No `SECURITY.md`, no `CODE_OF_CONDUCT.md`.

## Cross-platform discipline

### POSIX `/bin/sh` discipline in hot path

`hook-wrapper.sh` is `/bin/sh` (deliberately POSIX, not bash) because `/bin/sh` on Debian/Ubuntu is `dash`, and any bashism would fail silently. Avoids `[[ ]]`, arrays, process substitution, `local`. Uses `IFS= read -r VAR <file` instead of `mapfile`. Manual iteration instead of arrays. The installer (`install.sh`) and bootstrap (`bootstrap.sh`) are bash; the hot path is strict POSIX. Partitions scripts by criticality.

### Dual-fallback OS detection

`uname -s` primary, `$OS` env var (`Windows_NT`) fallback. Covers the case where a Windows user is in a non-MSYS shell without `uname` available.

### Git symlink-as-text-file detection on Windows

Git on Windows with `core.symlinks=false` materializes the `bin/claude-notifications` symlink (target `claude-notifications-darwin-arm64`) as a plain text file containing the target string. The wrapper detects this case (file < 1024 bytes, contents match `claude-notifications-{darwin,linux,windows}-*`) and either resolves the stub or synthesizes a `claude-notifications-MISSING` path to force re-install. `.gitattributes` hard-codes `text eol=lf` for `*.sh` and `*.go` and `eol=crlf` for `*.bat` / `*.ps1`.

## Cross-role tools

### bash

`bin/install.sh` (`set -e`) and `bin/bootstrap.sh` (`set -euo pipefail`) for installer paths. `hook-wrapper.sh` is `/bin/sh` POSIX (distinguished from bash for the hot path).

### `${CLAUDE_PLUGIN_ROOT}` env var

Used by `hook-wrapper.sh` (env-var first, script-relative fallback) to locate `bin/`, `ClaudeNotifier.app`, `sounds/`, `claude_icon.png`. Used inside `config/config.json` for resource paths (expanded by the Go binary, not by Claude Code).

### `softprops/action-gh-release@v2`

Used at `@v1` in this repo's `release.yml` — release-creation mechanism with `generate_release_notes: true`, `draft: false`, `prerelease: false`.

### `plugin.json.version`

Read by `hook-wrapper.sh` via `grep -Eo '[0-9]+\.[0-9]+\.[0-9]+'` as the source of truth for which binary version to fetch from GitHub Releases. Compared against the cached `verified-version` and (on cache miss) against `claude-notifications version` self-report. Plugin's `version` and `marketplace.json metadata.version` and `marketplace.json plugins[0].version` all read `1.38.0` at tip and are kept in lockstep by hand.

### Git as state substrate

Tags `v*` mark releases on main. `.gitattributes` hard-codes line-ending discipline. `core.symlinks=false` on Windows breaks the `bin/claude-notifications` symlink — the wrapper has explicit detection logic for git-as-text-file on Windows.

### GitHub Releases

Primary download source for native binaries (`https://github.com/777genius/claude-notifications-go/releases/latest/download/`). Asset matrix per platform×arch plus `ClaudeNotifier.app.zip`. `softprops/action-gh-release@v1` creates the release; `test-binaries` re-downloads from the published release for post-publish smoke.
</content>
</invoke>