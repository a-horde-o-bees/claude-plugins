# Sample

Mirrors of `https://github.com/K-dash/typemux-cc`. Single-plugin Claude Code distribution of a Rust LSP proxy that auto-detects `.venv` and routes to pyright/ty/pyrefly. Plugin declares an inline `lspServers` entry pointing at a native binary downloaded by a SessionStart hook.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root. Top-level `name` + `owner` only; no `metadata` wrapper, no top-level `description`. Single plugin entry sourcing from `./` — marketplace and plugin payload share the same repo root.

### `$schema` declaration on marketplace.json

`marketplace.json` declares `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"`. No CI step actively validates against the schema; field provides editor-time IDE assistance only.

## Plugin source binding

### Relative source pointing to repo root (`./`)

Marketplace entry `"source": "./"` — plugin payload shares the marketplace repo root.

### `strict` field default

Marketplace entry sets `strict: false` explicitly even though the plugin uses canonical paths (`hooks/hooks.json`, conventional skill discovery under `.claude/skills/`). Defensive ceremony — `strict` matters only when carving components out of a non-standard layout, and no carving happens here.

## Per-plugin discoverability metadata

### No discoverability fields on marketplace entry

Marketplace entry exposes neither `category` nor `tags` nor `keywords`; only `description`, `version`, `homepage`, `repository`. `plugin.json` carries `keywords` independently but the marketplace surface does not re-expose them. Plugin reachable only via direct install URL; browse-by-tag flows will not find it.

## Version coordination

### Triple-file version (build manifest joins)

Three sites carry the version (e.g., `0.2.10`): `plugin.json`, `marketplace.json` entry, and the language ecosystem's build manifest `Cargo.toml`. The `/publish` skill documents these three files as "must match" and uses `cargo check` to regenerate `Cargo.lock`. Drift is mitigated procedurally (skill-as-checklist) rather than structurally — no validation hook enforces the invariant, no CI gate verifies that the three files agree with the tag.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split, no `stable`/`latest` parallel marketplace. Users install via `K-dash/typemux-cc` (resolves to default branch `main` HEAD) or pin via `@vX.Y.Z` tag refs. `install.sh` always fetches `releases/latest` from the GitHub Releases API regardless of which marketplace-side ref the user pinned, so binary and cached plugin-files can drift (plugin.json at the installed commit may reference a binary version different from whatever `releases/latest` currently returns).

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

Tags `v0.1.10`..`v0.2.10` placed directly on commits merged to `main`. No long-lived `release/*` branches; no pre-release suffixes (plain `vX.Y.Z` only). Version bumps are manual through the `/publish` skill, which edits `Cargo.toml` + `plugin.json` + `marketplace.json` + regenerates `Cargo.lock` via `cargo check` before commit-tag-push. Tag-sanity is unenforced — `Cargo.toml`/`plugin.json`/`marketplace.json` versions can lag the tags indefinitely; only the skill-as-checklist catches drift.

## Plugin-component registration

### Mixed (paths + auto-discovery)

`plugin.json` declares `hooks` as external file reference (`"./hooks.json"`) and `lspServers` as an inline config object. Skills are auto-discovered under `.claude/skills/` (no explicit registration). Components: 2 skills (`plugin-test-cycle`, `publish` — both repo-local developer skills), 1 hook (external `hooks.json`), inline `lspServers`, plus a `bin/` directory containing only the wrapper script (the actual binary is gitignored, downloaded by `install.sh` at SessionStart). No commands, no agents, no `.mcp.json`, no monitors, no output-styles. A standalone `.lsp.json` at repo root duplicates the inline `lspServers` entry verbatim — Claude Code consumes the `plugin.json` form; the standalone file is either a vestige or a standalone-mode fallback.

## Bin entry mechanism

### Pre-built binary download (lazy, per-hook)

Runtime is a Rust binary downloaded from GitHub Releases by `install.sh` (invoked from `SessionStart` hook). `install.sh` calls the unauthenticated GitHub API `GET https://api.github.com/repos/K-dash/typemux-cc/releases/latest`, picks an asset by name (`typemux-cc-macos-arm64`, `typemux-cc-linux-x86_64`, `typemux-cc-linux-arm64`), `curl -L -o`s it into `${CLAUDE_PLUGIN_ROOT}/bin/typemux-cc`, and `chmod +x`s it. Existence-only change detection (`if [ -f "${BINARY_PATH}" ]; then echo "Binary already installed"; exit 0; fi`) — once present, never re-downloads. `/plugin update` does not pick up new binaries; users must manually `rm -rf ~/.claude/plugins/cache/typemux-cc-marketplace/` (README dedicates a troubleshooting section to this, citing Claude Code issue #13799). Unauthenticated GitHub API hits 60/hr rate limit per IP — limit-hit surfaces as cryptic `Failed to find binary for ...` errors. No sha or signature verification on the download. `plugin.json.lspServers.typemux-cc.command` points directly at `${CLAUDE_PLUGIN_ROOT}/bin/typemux-cc`. Local-build escape hatch documented for unsupported platforms — `cargo build --release` plus `/plugin marketplace add /path/to/typemux-cc` lets Intel-mac or Windows developers skip `install.sh`.

### Orphaned wrapper alongside downloaded binary

`bin/typemux-cc-wrapper.sh` (committed, 330 B, mode 100755, `#!/bin/bash`) sources `~/.config/typemux-cc/config` then `exec "${CLAUDE_PLUGIN_ROOT}/bin/typemux-cc" "$@"`. Plugin.json's `lspServers.typemux-cc.command` points directly at the downloaded binary, not the wrapper. `install.sh` even copies the wrapper into `${BIN_DIR}` as a sibling — still unreferenced. The Rust binary reads `~/.config/typemux-cc/config` natively via `src/config.rs::load_config_file()`, so the wrapper's config-sourcing is redundant. Half-refactored state where the wrapper was written first, then superseded by in-binary config loading, then left in place. The wrapper's `source "$CONFIG_FILE"` supports shell expansion (`$(...)`, backticks, `$VAR`) that the binary's parser explicitly rejects — a user upgrading from wrapper-era config to binary-era config could carry a syntactically valid shell file the binary refuses to parse.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

`plugin.json.lspServers.command` requires `${CLAUDE_PLUGIN_ROOT}` to be set; no script-relative fallback at the manifest layer. `install.sh` itself resolves the bin install dir via `${CLAUDE_PLUGIN_ROOT}` provided by the SessionStart hook context.

## Dependency installation

### Hook-driven prebuilt native binary

`SessionStart` hook downloads a prebuilt platform-specific Rust binary into `${CLAUDE_PLUGIN_ROOT}/bin/`, picking the right asset by detecting OS and architecture (`macos-arm64`, `linux-x86_64`, `linux-arm64`). `install.sh` (~repo root, invoked as `${CLAUDE_PLUGIN_ROOT}/install.sh`) is the install script. No `Cargo.toml`-driven install at runtime — `Cargo.toml` is the build-time manifest that produces the release artifact, not an install-time dependency list. `set -e` halts on error. Existence-only change detection means `/plugin update` does not re-download — users must manually clear the plugin cache. Calls unauthenticated GitHub API at install time (60/hr rate limit per IP). No sha or signature verification. Intel macOS and Windows explicitly rejected with corrective guidance pointing at the local-build escape hatch (`cargo build --release` + `/plugin marketplace add /path`).

## Install change detection

### Existence-only check

`if [ -f "${BINARY_PATH}" ]; then echo "Binary already installed"; exit 0; fi` — the install script never replaces the binary once present. No version check, no sha verification. Upgrades require manual cache wipe; the README documents this workaround. Pairs uneasily with `/plugin update` which does not clear the binary.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks.json` wires `SessionStart → ${CLAUDE_PLUGIN_ROOT}/install.sh`. Every SessionStart sub-event fires it (no matcher narrowing); guarded by binary-existence check so only the first install does real work. Steady-state cost is one `[ -f ]` test plus an echo.

## Install failure posture

### Human-readable stderr plus exit 1

`install.sh` uses `set -e`, prints prefixed `[typemux-cc] ERROR: ...` lines to stderr with corrective hints on unsupported platform / missing download URL / curl failure. `exit 1` on failure. No JSON `systemMessage`, no `continue: false`. No explicit `rm` on failure path — `set -e` halts the script, leaving any partial `bin/typemux-cc` only if `curl -L -o` already wrote bytes before failing. No documented cleanup.

## User configuration and authentication

### Home-directory KEY=VALUE file

The Rust binary reads `~/.config/typemux-cc/config` directly at startup — `KEY=VALUE` lines, optional `export` prefix, no shell expansion (per `src/config.rs`). Users create and maintain this file manually. `plugin.json` declares no `userConfig`. Env vars consulted by the binary: `TYPEMUX_CC_BACKEND`, `TYPEMUX_CC_LOG_FILE`, `TYPEMUX_CC_MAX_BACKENDS`, `TYPEMUX_CC_BACKEND_TTL`, `TYPEMUX_CC_FANOUT_TIMEOUT`, `TYPEMUX_CC_WARMUP_TIMEOUT`, `RUST_LOG`. Documented priority chain: `CLI flag > env var > config file > default`. Decouples config lifetime from plugin cache churn (config survives uninstall/reinstall) but sacrifices Claude-Code-side discoverability and validation.

## Session context loading

### Dependency install only (no context emission)

The single `SessionStart` hook runs `install.sh`; emits no `additionalContext`, no `systemMessage`. `UserPromptSubmit` not used. SessionStart matcher is none — fires on `startup`, `resume`, `clear`, `compact`; the binary-existence guard means only the first install does work, but any future install.sh stdout would emit on every sub-event.

## Tool-use enforcement

### No enforcement (observational only)

No `PreToolUse`, `PostToolUse`, `PermissionRequest`, or `PermissionDenied` hooks declared in the plugin's `hooks.json` (only `SessionStart`). A `PostToolUse` hook in `.claude/settings.json` matching `Write|Edit|MultiEdit` runs `make lint 2>&1 | head -30`, but that's repo-local developer tooling (in `.claude/settings.json`, not `hooks/hooks.json`) — not shipped as part of the plugin's enforcement surface.

## Live monitoring

### `monitors.json` absent

No `monitors.json` file. No update-notification mechanism inside the plugin — `install.sh` never re-runs after the binary is present. The README's recommended troubleshooting (manual cache wipe) is the only update path.

## Plugin-to-plugin coordination

### Implicit prose-only dependency

`plugin.json` has no `dependencies` field. README instructs users to `/plugin disable pyright-lsp@claude-plugins-official` before installing — a procedural conflict the plugin cannot express structurally. Plugin metadata has no mechanism to declare incompatibility; installing both leaves the user with conflicting LSP servers silently. The required-disable is enforced by README prose only.

## Testing

### cargo test

Rust integration-test layout — `tests/` at repo root holds top-level integration test files (`crash_recovery_test.rs`, `doctor_test.rs`, `multi_venv_test.rs`, `smoke_test.rs`, `venv_detection_test.rs`) with shared fixtures under `tests/support/mod.rs`. Wrapped behind `make ci` (= `fmt-check` + `clippy -- -D warnings` + `cargo test`).

## CI workflow shape

### Rust matrix CI with paths-ignore for plugin surface

`.github/workflows/ci.yml` runs `make ci` on `push: branches: [main] paths-ignore: ['*.md']` and `pull_request: paths-ignore: ['*.md']`. OS matrix: `ubuntu-latest`, `macos-latest`, `ubuntu-24.04-arm` (3-OS, no Rust-version matrix — `dtolnay/rust-toolchain@stable` pulls stable; `Cargo.toml` declares `rust-version = "1.75"` MSRV but CI does not enforce it). Action pinning by major tag uniformly: `actions/checkout@v5`, `dtolnay/rust-toolchain@stable`, `Swatinem/rust-cache@v2`, `softprops/action-gh-release@v1`. Rust target/registry caching via `Swatinem/rust-cache@v2`. CI does lint + clippy + cargo test; no manifest validation step.

## Marketplace validation

### No validation

No CI gate validates `marketplace.json`, `plugin.json`, or `hooks.json` shape. No `claude plugin validate` invocation. Regressions surface only at install time.

## Release automation

### Tag-triggered cross-compile + asset upload

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`. Builds Rust binary cross-compiled to three targets (`aarch64-apple-darwin`, `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`), installs `gcc-aarch64-linux-gnu` cross toolchain for the Linux arm64 build, renames outputs to `typemux-cc-macos-arm64` / `typemux-cc-linux-x86_64` / `typemux-cc-linux-arm64`, uploads via `softprops/action-gh-release@v1` with `generate_release_notes: true`. No tag-sanity gates — no verify-tag-on-main, no verify-tag-matches-Cargo.toml-version, no tag-format regex. Drift between `Cargo.toml`/`plugin.json`/`marketplace.json` and the tag is mitigated only by the `/publish` skill's manual checklist. Releases are published immediately (`draft: false`, `prerelease: false`); no CHANGELOG.md (release notes auto-generated). `softprops/action-gh-release@v1` is a moving target — SHA pinning would harden supply chain.

## Documentation surface

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` at repo root, ~16 KB — quickstart, problems-solved, supported backends, requirements, install (Method A: marketplace, Method B: local build), configuration, typical use cases, troubleshooting (including `--doctor`), known limitations. `ARCHITECTURE.md` at repo root, ~21 KB — design principles, mermaid diagrams, state transitions, pool/fanout/warmup sections. `CLAUDE.md` at repo root, 2 lines — `@AGENTS.md` include pointing at the canonical agent rule set in `AGENTS.md`. CHANGELOG.md absent (release notes auto-generated by GitHub). README header carries shields.io badges (commit-activity, license MIT, Rust-version, DeepWiki).

### `AGENTS.md` as ecosystem-neutral alternative to `CLAUDE.md`

`AGENTS.md` is the canonical agent-rules file at repo root; `CLAUDE.md` (the file Claude Code loads) contains only a 2-line `@AGENTS.md` pointer. Inverts the convention where `CLAUDE.md` carries the primary rule set. Works because `CLAUDE.md @AGENTS.md` includes the file at load time; cost is ownership of agent rules being non-obvious to a reader who opens `CLAUDE.md` first.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` (MIT) at repo root. `plugin.json.license: "MIT"` matches. README references the same. GitHub auto-detects and badges `MIT`. All sources agree.

## Community health files

### Community health files absent

No `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE/`, no `.github/PULL_REQUEST_TEMPLATE.md`. Mintlify documentation site (`k-dash-typemux-cc.mintlify.app/quickstart`) referenced in repo description but lives outside the repo.

## Cross-platform discipline

### POSIX with documented platform rejection

`install.sh` detects platform and explicitly errors on Intel macOS and Windows with corrective guidance pointing at the local-build escape hatch (`cargo build --release` + `/plugin marketplace add /path/to/typemux-cc`). No silent fallback, no Windows code path. Cross-platform support stops at "build it yourself if you're not on the supported list."

## Cross-ecosystem distribution

### Single-ecosystem (Claude only)

Plugin manifests live exclusively under `.claude-plugin/`. No `.cursor-plugin/`, no `.codex-plugin/`. The Rust binary itself is portable to any LSP-using IDE (Cursor, Helix), but the plugin distribution surface is Claude Code only.

## Distribution exclusion and dogfood layout

### Repo-local developer skills exposed as plugin skills

`.claude/skills/plugin-test-cycle` and `.claude/skills/publish` sit at repo root and are auto-discovered by Claude Code whenever the plugin is installed. End users see "plugin test" and "publish" triggers that are meaningful only to the plugin author. Neither is guarded or scoped to the plugin's own development. Similar to seeing internal `.vscode/launch.json` entries leak into a distribution.

## Native artifact distribution

### Per-platform asset matrix with shared-library carve-out

Release workflow cross-compiles to three Rust targets and uploads platform-named artifacts (`typemux-cc-macos-arm64`, `typemux-cc-linux-x86_64`, `typemux-cc-linux-arm64`). `install.sh` selects by `uname -s` / `uname -m`. Intel macOS and Windows have no asset and no install path (rejected at install time with corrective message).

## Cross-role tools

### `${CLAUDE_PLUGIN_ROOT}` env var

Required by `plugin.json.lspServers.typemux-cc.command` for runtime resolution of the binary path. `install.sh` also resolves the bin install dir via `${CLAUDE_PLUGIN_ROOT}` from the SessionStart hook context. No script-relative fallback at the manifest layer.

### bash

`install.sh` shebang `#!/usr/bin/env bash` + `set -e`; `bin/typemux-cc-wrapper.sh` shebang `/bin/bash`. Native binary for the Rust artifact (no shebang). Hot-path runtime is Rust; install / configuration glue is bash.

### GitHub Releases

Substrate for binary distribution — `release.yml` uploads three platform assets per tag; `install.sh` calls `https://api.github.com/repos/K-dash/typemux-cc/releases/latest` to pick the right one. Unauthenticated API call subject to 60/hr rate limit per IP.

### `softprops/action-gh-release@v2`

Used by `release.yml` (pinned to `@v1` here, not `@v2`) to publish releases with auto-generated notes. Major-tag pinning leaves the action a moving target in the supply chain.
