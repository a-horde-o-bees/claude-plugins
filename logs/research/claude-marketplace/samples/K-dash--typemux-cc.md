# K-dash/typemux-cc

## Identification

- **URL**: https://github.com/K-dash/typemux-cc
- **Stars**: 9
- **Last commit date**: 2026-03-21 (tag v0.2.10); repo `pushed_at` 2026-04-17
- **Default branch**: main
- **License**: MIT
- **Sample origin**: bin-wrapper
- **One-line purpose**: "Claude Code plugin: Python type-checker LSP multiplexer. Auto-detects `.venv` and routes to pyright/ty/pyrefly — no Claude Code restart." Ships a Rust-built LSP proxy binary behind a plugin-declared `lspServers` entry.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: none — top-level `name` + `owner` only; no `metadata` wrapper, no top-level `description`
- **`metadata.pluginRoot`**: absent (single-plugin repo; plugin source `./` is repo root)
- **Per-plugin discoverability**: none of `category` / `tags` / `keywords`; only `description`, `version`, `homepage`, `repository` declared. (Plugin.json carries `keywords` but marketplace entry does not re-expose them.)
- **`$schema`**: present — `https://anthropic.com/claude-code/marketplace.schema.json`
- **Reserved-name collision**: no
- **Pitfalls observed**: discoverability surfaces (category/tags/keywords) all omitted at the marketplace-entry level even though `plugin.json` has relevant `keywords` — anyone browsing the marketplace by tag will not find this plugin.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./"`)
- **`strict` field**: `false` explicit (single plugin; set at marketplace entry)
- **`skills` override on marketplace entry**: absent — plugin bundles skills but they live under `.claude/skills/` (see §5) and are not carved by marketplace-entry override
- **Version authority**: both — `plugin.json` and the marketplace entry each carry `version: "0.2.10"`, kept in sync by the `/publish` skill which documents three files (Cargo.toml + plugin.json + marketplace.json) that must match. Drift risk is mitigated procedurally rather than structurally.
- **Pitfalls observed**: triple-source-of-truth (`Cargo.toml`, `plugin.json`, `marketplace.json`) kept aligned only by a skill checklist; no validation hook enforces the invariant.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via tag refs (e.g., `K-dash/typemux-cc` resolves to default branch `main`; no `stable`/`latest` pattern)
- **Channel-pinning artifacts**: absent
- **Pitfalls observed**: none — single-channel marketplace; `install.sh` always fetches `releases/latest`, so binary and cached plugin-files can drift (plugin.json at the installed commit may reference a binary version different from whatever `releases/latest` currently returns).

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main (tag-on-main — `/publish` commits to main, tags, pushes)
- **Release branching**: none — tag-on-main
- **Pre-release suffixes**: none observed (tags are plain `v0.1.10` … `v0.2.10`)
- **Dev-counter scheme**: absent
- **Pre-commit version bump**: no — manual bump through `/publish` skill (edits three version files + `cargo check` to regenerate Cargo.lock)
- **Pitfalls observed**: release pipeline requires three files to agree by hand; no CI gate verifies that `Cargo.toml`/`plugin.json`/`marketplace.json` versions match the tag.

## 5. Plugin-component registration

- **Reference style in plugin.json**: mixed — `hooks` is external file reference (`"./hooks.json"`); `lspServers` is an inline config object; skills are auto-discovered under `.claude/skills/`
- **Components observed**:
  - skills: yes (2 — `plugin-test-cycle`, `publish`, both under `.claude/skills/` for repo-local agent use; these are developer-facing, not end-user-facing, but will be exposed whenever someone installs the plugin)
  - commands: no
  - agents: no
  - hooks: yes (external `hooks.json`)
  - .mcp.json: no
  - .lsp.json: yes (also present at repo root — duplicated config; see pitfalls)
  - monitors: no
  - bin: yes (directory present; only the wrapper script committed — see §7)
  - output-styles: no
- **Agent frontmatter fields used**: not applicable (no agents)
- **Agent tools syntax**: not applicable
- **Pitfalls observed**:
  - Both `.lsp.json` at repo root and `plugin.json`'s inline `lspServers` declare the same `typemux-cc` entry verbatim — duplicate source of truth. Claude Code consumes `plugin.json`'s `lspServers`; the `.lsp.json` at root appears to be either a standalone-mode fallback or a vestige.
  - `.claude/skills/plugin-test-cycle` and `.claude/skills/publish` are repo-local developer skills exposed as plugin skills whenever the plugin is installed — end users will see "plugin test" and "publish" triggers that are meaningful only to the plugin author.

## 6. Dependency installation

- **Applicable**: yes (SessionStart hook downloads the native binary on first session)
- **Dep manifest format**: none in the plugin-install sense — `Cargo.toml` drives the Rust build that produces the binary attached to GitHub Releases, not an install-time dependency list
- **Install location**: `${CLAUDE_PLUGIN_ROOT}/bin/typemux-cc` (inside the plugin cache directory, not `${CLAUDE_PLUGIN_DATA}`)
- **Install script location**: `./install.sh` (repo root), invoked as `${CLAUDE_PLUGIN_ROOT}/install.sh`
- **Change detection**: existence only — `if [ -f "${BINARY_PATH}" ]; then echo "Binary already installed"; exit 0; fi`. No version check, no sha verification. Once present, `install.sh` never replaces it; upgrades require manual cache wipe (the README documents `rm -rf ~/.claude/plugins/cache/typemux-cc-marketplace/` as the workaround for Claude Code issue #13799).
- **Retry-next-session invariant**: no explicit `rm` on failure — `set -e` halts the script on error leaving a partial `bin/typemux-cc` only if `curl -L -o` already wrote bytes before failing (unlikely but possible). No documented cleanup.
- **Failure signaling**: stderr human-readable (`[typemux-cc] ERROR: ...` lines with corrective hints) + `exit 1` on unsupported platform / missing download URL / curl failure. `set -e` halts. No JSON `systemMessage`, no `continue: false`.
- **Runtime variant**: Go/Rust binary download (closest template fit) — prebuilt Rust binary fetched from `GET https://api.github.com/repos/K-dash/typemux-cc/releases/latest`, platform-selected from asset names (`typemux-cc-macos-arm64`, `typemux-cc-linux-x86_64`, `typemux-cc-linux-arm64`)
- **Alternative approaches**: Local-build escape hatch documented — `cargo build --release` + `/plugin marketplace add /path/to/typemux-cc` lets Intel-mac or Windows developers skip `install.sh`'s prebuilt-binary path
- **Version-mismatch handling**: none — `install.sh` pins to `releases/latest` regardless of the committed `plugin.json` version, so the binary on disk can lead or lag the plugin.json it was deployed with
- **Pitfalls observed**:
  - Existence-only change detection means `/plugin update` does not re-download the binary; users must manually clear the plugin cache. The README dedicates a troubleshooting section to this.
  - `install.sh` calls unauthenticated GitHub API (`/releases/latest`) — 60/hr rate limit per IP; a dev hitting the limit has no binary and a cryptic `Failed to find binary for ...` error.
  - No sha/signature verification on the downloaded binary — trust is implicit in HTTPS + GitHub Releases.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes (but implementation is unusual — see pitfalls)
- **`bin/` files**:
  - `bin/typemux-cc-wrapper.sh` (committed, 330 B) — sources `~/.config/typemux-cc/config` then `exec "${CLAUDE_PLUGIN_ROOT}/bin/typemux-cc" "$@"`. **Not referenced by plugin.json.**
  - `bin/typemux-cc` (gitignored, downloaded by `install.sh` at SessionStart) — the Rust LSP proxy binary; this is what plugin.json invokes.
- **Shebang convention**: `/bin/bash` (wrapper); native binary for the Rust artifact (no shebang)
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` required — `lspServers.typemux-cc.command` is `${CLAUDE_PLUGIN_ROOT}/bin/typemux-cc`. No script-relative fallback; the plugin-root variable must be set.
- **Venv handling (Python)**: not applicable — the Rust binary itself detects and spawns pyright/ty/pyrefly with `VIRTUAL_ENV` set; no Python runtime is packaged inside this plugin
- **Platform support**: OS-detecting download — `install.sh` detects macOS arm64 / Linux x86_64 / Linux arm64 and errors out on everything else (including Intel macOS and Windows, both explicitly rejected with guidance)
- **Permissions**: 100755 (wrapper committed executable; downloaded binary `chmod +x`ed by install.sh)
- **SessionStart relationship**: hook lazily downloads the binary — `hooks.json` wires `SessionStart → ${CLAUDE_PLUGIN_ROOT}/install.sh`, which curls the platform-matching artifact on first run and no-ops afterward based on file existence
- **Pitfalls observed**:
  - The committed `bin/typemux-cc-wrapper.sh` is orphaned: plugin.json's `lspServers` points directly at `${CLAUDE_PLUGIN_ROOT}/bin/typemux-cc` (the downloaded Rust binary), so the wrapper's config-sourcing logic never fires. `install.sh` even copies the wrapper into `${BIN_DIR}` as a sibling — still unreferenced. The Rust binary reads `~/.config/typemux-cc/config` natively via `src/config.rs::load_config_file()`, so the wrapper is redundant as well as unused. Classic half-refactored state where the wrapper was written first, then superseded by in-binary config loading, then left in place.
  - The "bin-commit" sample-origin classification is misleading: no committed binary lives in-tree. `.gitignore` explicitly excludes `bin/typemux-cc` and every per-platform variant. Pattern is hook-downloaded binary, not checked-in binary.
  - Intel macOS rejection is hardcoded in `install.sh`; affected users must take the Method B local-build escape (the only supported path for unsupported platforms).

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable — configuration is consumed out-of-band. The Rust binary reads `~/.config/typemux-cc/config` (`KEY=VALUE` lines, optional `export` prefix, no shell expansion per `src/config.rs`) at startup; users create and maintain this file manually. Env vars consulted: `TYPEMUX_CC_BACKEND`, `TYPEMUX_CC_LOG_FILE`, `TYPEMUX_CC_MAX_BACKENDS`, `TYPEMUX_CC_BACKEND_TTL`, `TYPEMUX_CC_FANOUT_TIMEOUT`, `TYPEMUX_CC_WARMUP_TIMEOUT`, `RUST_LOG`. Priority documented as CLI flag > env var > config file > default.
- **Pitfalls observed**:
  - No plugin-level config surface — users edit a home-directory file rather than interacting through Claude Code's plugin config mechanism. Means no Claude-Code-side discoverability or validation, but decouples config lifetime from plugin cache churn (config survives plugin uninstall/reinstall).
  - The committed wrapper's `source "$CONFIG_FILE"` supports shell semantics the Rust binary's parser explicitly rejects (`$(...)`, backticks, `$VAR`). A user who once configured via the wrapper and later upgrades could have a config file that the Rust parser rejects — in practice not exercised because the wrapper is unused in the install path.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none
- **PostToolUse hooks**: none declared in the plugin's `hooks.json` (plugin ships only `SessionStart`). There is a `PostToolUse` hook in `.claude/settings.json` matching `Write|Edit|MultiEdit` that runs `make lint 2>&1 | head -30` — but that's repo-local developer tooling, not shipped as part of the plugin. (Worth flagging because the file is committed and could leak into plugin distribution if claude-code ever started harvesting it.)
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: not applicable
- **Failure posture**: not applicable
- **Top-level try/catch wrapping**: not applicable
- **Pitfalls observed**: none — plugin is entirely LSP-surface, not tool-enforcement.

## 10. Session context loading

- **SessionStart used for context**: no — only for dep install (binary download; see §6)
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no
- **SessionStart matcher**: none (fires on all sub-events — `startup`, `resume`, `clear`, `compact` all trigger install.sh; guarded by binary-existence check so only the first install does real work)
- **Pitfalls observed**: running `install.sh` on every session sub-event is inexpensive in the steady state (one `[ -f ]` test + echo) but does mean any user-facing stdout from a future install.sh revision would emit on resume/clear/compact too.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none — though the README instructs users to `/plugin disable pyright-lsp@claude-plugins-official` before installing, a procedural conflict the plugin cannot express structurally
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace; tags are plain `v*`)
- **Pitfalls observed**: the required-disable of `pyright-lsp@claude-plugins-official` is enforced only by README prose — plugin metadata has no way to declare incompatibility; installing both leaves the user with conflicting LSP servers silently.

## 13. Testing and CI

- **Test framework**: cargo test (Rust integration tests in `tests/`)
- **Tests location**: `tests/` at repo root — Rust integration-test layout (`crash_recovery_test.rs`, `doctor_test.rs`, `multi_venv_test.rs`, `smoke_test.rs`, `venv_detection_test.rs`, with `tests/support/mod.rs` shared fixture)
- **Pytest config location**: not applicable (no Python)
- **Python dep manifest for tests**: not applicable
- **CI present**: yes
- **CI file(s)**: `.github/workflows/ci.yml`, `.github/workflows/release.yml`
- **CI triggers**: `push: branches: [main] paths-ignore: ['*.md']` + `pull_request: paths-ignore: ['*.md']` for ci.yml; `push: tags: ['v*']` for release.yml
- **CI does**: `make ci` — which is `fmt-check` + `clippy -- -D warnings` + `cargo test`
- **Matrix**: OS — `ubuntu-latest`, `macos-latest`, `ubuntu-24.04-arm` (3-OS matrix, no Rust-version matrix — toolchain is `stable` via dtolnay/rust-toolchain)
- **Action pinning**: tag (all actions pinned to major tags: `actions/checkout@v5`, `dtolnay/rust-toolchain@stable`, `Swatinem/rust-cache@v2`, `softprops/action-gh-release@v1`)
- **Caching**: `Swatinem/rust-cache@v2` for Rust target/registry caching
- **Test runner invocation**: `make ci` wrapper (which invokes `cargo test`)
- **Pitfalls observed**:
  - `paths-ignore: ['*.md']` is evaluated top-level only — a deeply-nested markdown edit (e.g., `docs/why-lsp.md`) would still skip CI as intended but pattern is `*.md` not `**/*.md`; GitHub's glob semantics mean this still matches nested paths, so the exclusion works. Worth double-checking before copying the pattern.
  - CI matrix covers OS but not Rust MSRV enforcement — `Cargo.toml` declares `rust-version = "1.75"` but CI pulls `stable`, so a regression that relies on a post-1.75 feature would not be caught.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes
- **Release trigger**: `push: tags: ['v*']`
- **Automation shape**: Rust binary build + attach — cross-compiles to 3 targets (aarch64-apple-darwin, x86_64-unknown-linux-gnu, aarch64-unknown-linux-gnu), installs `gcc-aarch64-linux-gnu` cross toolchain for the Linux arm64 build, renames outputs to `typemux-cc-macos-arm64` / `typemux-cc-linux-x86_64` / `typemux-cc-linux-arm64`, and uploads via `softprops/action-gh-release@v1` with `generate_release_notes: true`
- **Tag-sanity gates**: none — no verify-tag-on-main, no verify-tag-matches-Cargo.toml-version, no tag-format regex
- **Release creation mechanism**: `softprops/action-gh-release@v1`
- **Draft releases**: no (published immediately; latest 10 releases all `draft=false`, `prerelease=false`)
- **CHANGELOG parsing**: no — relies on `generate_release_notes: true` for auto-generated notes; no `CHANGELOG.md` in repo
- **Pitfalls observed**:
  - Absence of tag-sanity gates means a malformed tag (e.g., `v0.2.10` tag but Cargo.toml still says `0.2.9`) produces a release with a binary whose `--version` output contradicts the tag — mitigated only by the `/publish` skill's manual checklist.
  - `softprops/action-gh-release@v1` is a moving target; SHA pinning would harden supply chain.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: not applicable
- **Hooks.json validation**: not applicable
- **Pitfalls observed**: no CI gate validates `marketplace.json`, `plugin.json`, or `hooks.json` shape; regressions only surface at install time.

## 16. Documentation

- **`README.md` at repo root**: present (~16 KB — substantial; covers quickstart, problems-solved, supported backends, requirements, install (A: marketplace, B: local build), configuration, typical use cases, troubleshooting including `--doctor`, known limitations)
- **Owner profile README at `github.com/K-dash/K-dash`**: present (~29 lines, decorative — GitHub stats widgets only, no content)
- **`README.md` per plugin**: not applicable (single-plugin repo; repo README serves the plugin)
- **`CHANGELOG.md`**: absent (release notes auto-generated by GitHub)
- **`architecture.md`**: present at repo root (`ARCHITECTURE.md`, ~21 KB — design principles, mermaid diagrams, state transitions, pool/fanout/warmup sections)
- **`CLAUDE.md`**: present at repo root — minimal (2 lines); delegates to `AGENTS.md` which holds the full rule set
- **Community health files**: none (no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`)
- **LICENSE**: present (MIT)
- **Badges / status indicators**: observed — commit-activity, license, Rust-version, DeepWiki badges in README header
- **Pitfalls observed**:
  - `AGENTS.md` is the canonical agent-rules file, but `CLAUDE.md` (what Claude Code actually loads) contains only a pointer — convention inversion relative to the Claude Code convention of CLAUDE.md being the primary agent memory. Works because `CLAUDE.md` `@AGENTS.md` includes the file, but makes agent-rule ownership less obvious.
  - Documentation homepage (mintlify.app) referenced in repo description but not integrated into the repo — separate documentation site.

## 17. Novel axes

- **Orphaned bin-wrapper** — plugin.json invokes the downloaded binary directly, yet `bin/typemux-cc-wrapper.sh` (committed, copied to cache, config-sourcing) stays in the tree. Evidence of a half-completed refactor from wrapper-based config to in-binary config. Candidate for a "committed-but-unreferenced bin entry" pitfall in the pattern doc's bin-wrapper section.
- **Out-of-band user config** — no `userConfig` declared in plugin.json; configuration is a `KEY=VALUE` file at `~/.config/<plugin>/config` read by the Rust binary itself. Decouples config from plugin-cache lifecycle (survives reinstall) but sacrifices plugin-system discoverability and validation. Distinct from both the `userConfig`-field pattern and the "no config" pattern.
- **Hook-lazy binary download (not hook-dep-install)** — the SessionStart hook is neither a Python venv bootstrap nor an npm install — it's a GitHub-Releases curl-and-chmod step. Existence-only change detection means the hook is a one-shot install, not an idempotent sync. Different enough from the "dep install" pattern to be called out separately.
- **Triple-source-of-truth version field** — `Cargo.toml`, `plugin.json`, `marketplace.json` all carry the same version, synced by a `/publish` skill-as-procedural-enforcement. No structural invariant; no CI validation. Pattern: "version lives in N files, invariant enforced by a documented skill" — candidate for a discipline section on invariant enforcement mechanism (structural vs procedural vs CI).
- **Repo-local developer skills shipped with the plugin** — `.claude/skills/plugin-test-cycle` and `.claude/skills/publish` are discoverable by any user who installs the plugin, because Claude Code auto-discovers skills under `.claude/skills/`. Neither is guarded or scoped to the plugin author. Similar to seeing internal `.vscode/launch.json` entries leak into a distribution.
- **LSP-first plugin** — `lspServers` inline in `plugin.json` plus a separate (duplicate) `.lsp.json` at repo root. Pattern: LSP-plugin surface with redundant config files, possibly to support both standalone and plugin-mode invocation.
- **Duplicate-disable conflict** — the plugin requires the user to `/plugin disable pyright-lsp@claude-plugins-official` manually via README prose; plugin metadata has no mechanism to declare conflict or auto-disable. Candidate for a "plugin-conflict declaration" axis.
- **GitHub-API-at-install-time** — `install.sh` depends on GitHub's API for releases discovery, coupling first-session success to GitHub rate limits and connectivity. No pre-baked asset URL pattern is used; fetch-and-grep of the releases JSON is the lookup path.

## 18. Gaps

- Did not read `.claude/settings.json` fully beyond the `PostToolUse` lint hook — unknown whether other repo-local hooks, permissions, or env configurations leak via the published plugin path. Source: `.claude/settings.json` full contents.
- Did not inspect the Mintlify documentation site; its scope and whether it is the canonical user-doc source (vs README) is unresolved. Source: https://k-dash-typemux-cc.mintlify.app/quickstart.
- Did not verify whether `bin/typemux-cc-wrapper.sh` is ever invoked on any platform — plugin.json points at the binary directly, but a user who launches the binary manually via the wrapper path would get the config-sourcing behavior. Runtime-observed rather than source-observed. Would require tracing a live Claude Code session with strace or equivalent.
- Did not enumerate whether the repo-local `AGENTS.md` rules get surfaced to Claude Code via `@AGENTS.md` inclusion when the plugin is installed by a third party (as opposed to when the author is inside the repo). The CLAUDE.md include rules are loaded relative to the cwd, so the effective behavior depends on where claude is launched; would need a test install to confirm.
- Did not inspect `doctor.rs` in depth — the `--doctor` output structure is documented in README but whether it surfaces anything that would be relevant to plugin-system discoverability was not evaluated.
- Commit count, contributors, and issue/PR activity not pulled — would contextualize maturity and churn. Source: `gh api repos/K-dash/typemux-cc/stats/contributors` and `/issues`.
