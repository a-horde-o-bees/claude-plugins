# Sample

Mirrors of `https://github.com/lukasmalkmus/moneymoney`. Agent-native CLI (`mm`) and MCP server for the macOS MoneyMoney banking app — query accounts, transactions, categories, portfolios, bank statements; draft SEPA transfers, direct debits, batch transfers through MoneyMoney's GUI+TAN flow. MIT-licensed; 0 stars at sample time; current tip is `v0.4.0` on default branch `main`.

## Marketplace manifest layout

### Top-level `metadata` wrapper variants

Single `.claude-plugin/marketplace.json` at repo root with `metadata.{title, description, categories, tags}` wrapper carrying descriptive content. `metadata.pluginRoot` absent (single plugin with `"source": "./"` — pluginRoot not needed). Marketplace name (`moneymoney`) equals plugin name; install command reads `moneymoney@moneymoney`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` — single plugin lives at repo root. `strict` field absent on the marketplace entry (default implicit `true`). `skills` override absent.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Plugin entry carries `keywords: ["moneymoney", "banking", "finance", "mcp", "cli"]`. Marketplace-level `metadata.categories` (`finance`, `productivity`) and `metadata.tags` apply at marketplace scope, not per-plugin.

### `$schema` absence on per-plugin manifests

`$schema` absent on both `marketplace.json` and `plugin.json`.

## Version coordination

### Dual-file version (manifest pair)

Both `plugin.json` and `marketplace.json` carry `version: 0.4.0` — drift risk; two sources of truth. The `ensure-binary.sh` and `bin/mm` read version from `plugin.json` only, so `plugin.json` is the de-facto authority for runtime behavior; the marketplace-entry duplicate exists for manifest display but is not enforced consistent by any tooling. The marketplace entry repeats `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords` — all also present in `plugin.json`. On version bump, both must change in lockstep or the marketplace display diverges from the installed plugin.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No stable/latest split. Users pin via `@ref` (git tag) for a specific version. Single main branch with linear tag history v0.1.0 → v0.4.0.

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

Tags placed on main; linear history v0.1.0, v0.2.0, v0.3.0, v0.4.0 — all dated 2026-04-20 per CHANGELOG (rapid initial rollout). No release branches. No pre-release suffixes. Version bumped manually in release commits (e.g., `release: v0.4.0` commit message); no auto-bump pre-commit hook.

## Plugin-component registration

### Default convention discovery

`plugin.json` contains only metadata (`name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`); no explicit `skills`/`commands`/`agents`/`hooks`/`mcpServers` fields. Components discovered by convention from directory layout. `.claude-plugin/settings.json` is empty (`{}`) — kept as a placeholder.

## Component composition

### Skills (universal)

One skill: `skills/moneymoney/SKILL.md`. Skill declares `name`, `description`, `user-invocable: true`, `argument-hint: <question-or-query>`, `allowed-tools`.

### Hooks

`hooks/hooks.json` registers SessionStart (`ensure-binary.sh`) and PostToolUse (`nudge-skill.sh`).

### bin

`bin/mm` shim — three-tier resolution (user-PATH → plugin-managed → download-on-demand). 3405 bytes; mode 100755.

## Skill authoring conventions

### `allowed-tools` with permission-rule syntax

Skill `allowed-tools` uses Claude Code permission-rule syntax with `Bash(mm <subcommand> *)` form — e.g., `Bash(mm accounts *)`, `Bash(mm transactions *)`. Write-side `mm transfer`, `mm transaction add/set` deliberately omitted from allowed-tools to force permission prompt.

### `user-invocable: false`

Skill declares `user-invocable: true` (read access) and `argument-hint: <question-or-query>`.

## Bin entry mechanism

### Lazy-install bin shim with fallback chain

`bin/mm` (bash, `#!/usr/bin/env bash`) is a three-tier resolution shim:

1. **User-installed mm wins** — `PATH` is cleaned of `self_dir` (via `grep -vFx` to prevent self-re-exec), then `command -v mm` searches the cleaned path. If found, `exec "$real_mm" "$@"`.
2. **Plugin-managed cache** — if `$data_dir/bin/mm` exists and its recorded version matches `plugin.json`'s version, `exec "$installed_binary" "$@"`.
3. **Lazy download** — curl release asset (`mm-<target>.tar.gz` from GitHub releases), tar xzf, chmod +x, xattr `-d com.apple.quarantine`, exec.

Inverts the more common "plugin-managed only" pattern: a user with `cargo install moneymoney --locked` or `brew install lukasmalkmus/tap/mm` runs their own binary — the plugin never competes. PATH-cleaning via `grep -vFx "$self_dir"` is fixed-string line-anchored — works because `self_dir` is canonicalized via `cd "$(dirname "$0")" && pwd`. The same clean-path trick is duplicated in both `bin/mm` and `hooks/ensure-binary.sh`. `hooks/ensure-binary.sh` (SessionStart) forks `("$plugin_root/bin/mm" --version) & disown` and exits 0 immediately so session startup never blocks on network — the worst case (network failure at session start) is that the first real `mm` invocation pays the download cost. Download logic lives in one place (`bin/mm`); the hook merely triggers it early.

### Committed binaries in tree

`bin/mm` is committed with executable bit set (mode 100755), as are `ensure-binary.sh` and `nudge-skill.sh`. The `mm` binary itself is downloaded — only the bash shim is committed.

## Server runtime (MCP)

### No bin entry / direct invocation

MCP server is built into the `mm` binary; invoked as `mm mcp` rather than declared in a `.mcp.json`. The bin shim resolves the `mm` binary via the three-tier mechanism then forwards `mm mcp` invocations to it.

## Dependency installation

### Native binary downloaded on first use with version-stamp idempotency

Rust binary downloaded at runtime. Install location: `${CLAUDE_PLUGIN_DATA}/bin/mm` with version stamp at `${CLAUDE_PLUGIN_DATA}/bin/mm.version`; defaults to `$HOME/.claude/plugins/data/moneymoney` when `CLAUDE_PLUGIN_DATA` unset. SessionStart triggers `ensure-binary.sh` which backgrounds `bin/mm --version` (the shim's own download path runs once per session). Version-file stamp (`mm.version`) compared against `jq -r '.version' plugin.json`; equal → skip, otherwise re-download.

## Install change detection

### Version-stamp file written after success

Version file at `$data_dir/bin/mm.version` is written *only after* successful extraction — a failed download leaves no stamp; the next invocation re-attempts cleanly without explicit cleanup. Effectively idempotent via write-last.

## Install failure posture

### Set -e bash with stderr exit-1

`bin/mm` uses `set -euo pipefail`; stderr human-readable error with fallback install hints (`cargo install moneymoney --locked` or `brew install lukasmalkmus/tap/mm`); exit 127 mirrors "command not found" (used for non-Darwin platforms — only `Darwin/arm64` and `Darwin/x86_64` are supported). `ensure-binary.sh` (SessionStart) fires-and-forgets in a backgrounded subshell with `disown` — session start never blocks on network.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks/ensure-binary.sh` (bash) registered as SessionStart hook. Forks `bin/mm --version` in a backgrounded-and-disowned subshell so the shim's download logic executes once per session without blocking. Composes with the shim's lazy-download path on direct invocation.

## Hook handler runtime

### Bash scripts at conventional path

Hook handlers under `hooks/` are bash scripts (`ensure-binary.sh`, `nudge-skill.sh`). `nudge-skill.sh` does not use `set -e` — relies on plain shell exit codes. `ensure-binary.sh` does use `set -euo pipefail`.

## Hook output contract

### `additionalContext` for context injection

`nudge-skill.sh` produces stdout JSON via `jq -n` producing `{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: <nudge>}}`. `additionalContext` is the documented injection channel. No stderr used for the successful path.

## Hook failure posture

### Fail-open with always-exit-0

`nudge-skill.sh` uses plain `exit 0` on skip cases (no `mm` command detected, marker already exists, session id missing). No `set -e`. No top-level try/catch wrapping.

## Tool-use enforcement

### PostToolUse local workflow reminders

PostToolUse hook with matcher `"Bash"`. When a Bash command contains `mm` as a word (regex `(^|[^a-zA-Z0-9-])mm($|[[:space:]])` — excludes substrings like `mmdd` or `commit`), emit a one-time per-session `<system-reminder>` pointing agents at the `/moneymoney` skill. Marker file at `${TMPDIR}/.moneymoney-skill-nudge-${session_id}` ensures one-shot. `$PPID` fallback used as marker suffix when `session_id` is empty (stable within a session, not across sessions). The word-boundary regex avoids substring matches and the per-session marker prevents repeated nudges within a session — distinguishing this from PostToolUse reminders that fire on every invocation.

## Session context loading

### Dependency install only (no context emission)

SessionStart used only for dep install (the `bin/mm --version` warmup). No `additionalContext` emission from SessionStart. `additionalContext` is emitted from PostToolUse (the skill nudge), not SessionStart.

## SessionStart matcher scope

### Empty matcher (all sub-events)

No `matcher` key set. Default is all SessionStart events: startup, clear, compact, resume. The background `mm --version` warmup runs more than once per user session (idempotent via version-stamp check, so redundant runs cost at most a stamp comparison).

## Live monitoring

### `monitors.json` absent

No `monitors.json`. No live monitoring or notification work.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field. Single-plugin marketplace; tag format is plain `v0.4.0` (no plugin-name prefix needed).

## User configuration and authentication

### No userConfig, env-var only

No `userConfig` field. Config lives outside the plugin surface at `~/.config/mm/config.toml` (read by the `mm` binary itself), not via Claude-plugin `userConfig`/`CLAUDE_PLUGIN_OPTION_*` env vars. Credential isolation: `mm` itself holds no credentials; MoneyMoney owns every bank secret in its encrypted store. Authentication for write ops uses MoneyMoney's GUI+TAN flow, not plugin config.

## Testing

### cargo test

`cargo test` (Rust built-in). Inline per Rust convention — `#[cfg(test)] mod tests` within source files. No separate `tests/` directory at repo root in the top-level listing.

## CI workflow shape

### Single workflow, OS × language matrix

`.github/workflows/ci.yaml` runs fmt (`cargo fmt --all --check`), clippy (`cargo clippy --all-targets -- -D warnings`), MSRV extraction (greps `rust-version` from Cargo.toml), test (stable + MSRV on ubuntu-latest, stable on macos-latest), audit (`rustsec/audit-check@v2`), docs (`cargo doc --no-deps --all` with `RUSTDOCFLAGS: -D warnings`). Matrix: toolchain × os — `{stable, ubuntu-latest}`, `{MSRV-from-file, ubuntu-latest}`, `{stable, macos-latest}`. Test runner invocation is direct `cargo test --all`.

### Rust matrix CI with paths-ignore for plugin surface

Triggers: `push: branches: [main]` and `pull_request`, both with `paths-ignore: ["**.md", "LICENSE", ".claude-plugin/**", "skills/**", "hooks/**"]` — plugin-surface edits don't retrigger Rust CI. Pure skill/hook iteration lands without Rust CI signal (the right call for a Rust binary, but means no shellcheck on `hooks/*.sh`).

### Action-pinning conventions

Tag-pinned: `actions/checkout@v6`, `dtolnay/rust-toolchain@stable`, `Swatinem/rust-cache@v2`, `rustsec/audit-check@v2`, `taiki-e/upload-rust-binary-action@v1`, `actions/upload-artifact@v7`, `taiki-e/create-gh-release-action@v1`, `actions/download-artifact@v8`. Major-tag pinning throughout — no SHA pins. Caching via `Swatinem/rust-cache@v2` on clippy + test + docs jobs.

## Marketplace validation

### No validation

No marketplace-validation workflow. `marketplace.json` and `plugin.json` duplicate version/description/author — with no validator checking parity, drift is a silent failure mode.

## Release automation

### Tag-triggered cross-build with CHANGELOG awk extraction

`.github/workflows/release.yaml` triggers on `push: tags: ["v*"]`. Build job: matrix over `x86_64-apple-darwin` and `aarch64-apple-darwin` on `macos-latest`, uses `taiki-e/upload-rust-binary-action@v1` with `dry-run: true` to produce archives, then `actions/upload-artifact@v7` stashes them. Release job: downloads artifacts, calls `taiki-e/create-gh-release-action@v1` with `changelog: CHANGELOG.md` (extracts the relevant version section), then `gh release upload "${GITHUB_REF_NAME}" artifacts/*`. No tag-on-main verify, no tag=version check, no regex gate.

### CHANGELOG-parsing release action

`taiki-e/create-gh-release-action@v1` parses `CHANGELOG.md` to extract the per-version section as the GitHub release body. CHANGELOG follows Keep a Changelog format (1.1.0).

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

`README.md` at repo root (~5 KB) — install table with plugin/cargo/brew/manual rows, features, SEPA note, credential isolation note. No badges in the README opening. Single-plugin repo where the plugin lives at root — no per-plugin README.

### Keep-a-Changelog with root-cause prose

`CHANGELOG.md` follows Keep a Changelog format (1.1.0, SemVer-aligned); versions 0.1.0 → 0.4.0 all dated 2026-04-20.

### `AGENTS.md` as ecosystem-neutral alternative to `CLAUDE.md`

Both `CLAUDE.md` and `AGENTS.md` exist at repo root with substantially overlapping content (CLI shape, output formats, exit codes, build, commit format, dependencies, skills). No symlink, no generator — manual lockstep maintenance rather than a single canonical source plus pointer. Single source of truth would be preferable; observed state is duplicated content with high drift risk on refactor.

## License declaration

### Single repo-level license

`LICENSE` at repo root, MIT.

## Community health files

### Bare minimum (LICENSE only)

`LICENSE` only. No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` at repo root or in `.github/`.

## State persistence

### `${CLAUDE_PLUGIN_DATA}` for venvs and stamps

Plugin-managed binary cache at `${CLAUDE_PLUGIN_DATA}/bin/mm` with version stamp at `${CLAUDE_PLUGIN_DATA}/bin/mm.version`. Default fallback to `$HOME/.claude/plugins/data/moneymoney` when `CLAUDE_PLUGIN_DATA` unset.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code (bin shim, hook scripts, skill) under `${CLAUDE_PLUGIN_ROOT}`; downloaded binary under `${CLAUDE_PLUGIN_DATA}/bin/`. `mm`'s own runtime config lives at `~/.config/mm/config.toml` (independent of plugin tree, owned by the binary not the plugin).

## Cross-platform discipline

### POSIX with documented platform rejection

Plugin installs cleanly on any OS but `bin/mm` exits 127 with a specific "MoneyMoney is macOS-only" message + install-hint fallbacks (`cargo install moneymoney --locked` or `brew install lukasmalkmus/tap/mm`) on non-Darwin platforms. The capability filter is runtime, not install-time — MoneyMoney (the upstream macOS GUI app) is the AppleScript integration target. Linux invocation of the binary would only return `NotSupported`. Cross-platform compile is a CI sanity check only.

### POSIX `/bin/sh` discipline in hot path

`bin/mm` shebang is `#!/usr/bin/env bash`. Hook scripts use bash. macOS Gatekeeper handling: fresh download gets `com.apple.quarantine` attribute stripped via best-effort `xattr -d` — without that, users would hit "cannot be opened because developer cannot be verified" on first run.

## PATH augmentation and host-project setup

### None (plugin operates standalone)

Plugin operates without modifying user `PATH`. The bin shim's three-tier resolution explicitly cleans `self_dir` from `PATH` to avoid self-re-exec, but does not add anything to PATH.

## Cross-role tools

### Bash

Bash for the bin shim (`bin/mm`) and hook scripts (`ensure-binary.sh`, `nudge-skill.sh`).

### Git as state substrate

Tag-on-main lifecycle; tags v0.1.0 → v0.4.0.

### GitHub Releases

Release artifacts (`mm-<target>.tar.gz`) hosted on GitHub Releases. Shim download URL hardcodes `https://github.com/.../releases/download/v${version}/mm-${target}.tar.gz`. If the build workflow's asset naming changes, the shim's URL breaks silently until next session's download attempt.

### `${CLAUDE_PLUGIN_DATA}`

Plugin-managed binary cache directory.

### `plugin.json.version`

`bin/mm` reads version via `jq -r '.version' plugin.json` to compare against the cached binary's `mm.version` stamp.

### `jq`

Used in `bin/mm` (read plugin version) and `nudge-skill.sh` (build the JSON nudge payload via `jq -n`).

## Source-pin maintenance

### Registration-list drift guard

`bin/mm`'s download URL is hardcoded to match `taiki-e/upload-rust-binary-action`'s default asset naming (`mm-<target>.tar.gz`). No abstraction layer — any future refactor of release artifact naming must touch both `release.yaml` and `bin/mm` in lockstep. Deliberate simplicity: no pointer file, no manifest lookup, no runtime asset discovery.
