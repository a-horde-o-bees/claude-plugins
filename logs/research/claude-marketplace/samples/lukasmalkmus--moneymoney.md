# lukasmalkmus/moneymoney

## Identification

- **URL**: https://github.com/lukasmalkmus/moneymoney
- **Stars**: 0
- **Last commit date**: 2026-04-20 (tag v0.4.0, sha 63cbfdb)
- **Default branch**: main
- **License**: MIT
- **Sample origin**: bin-wrapper
- **One-line purpose**: Agent-native CLI (`mm`) and MCP server for MoneyMoney — query accounts, transactions, categories, portfolios, and bank statements; draft SEPA transfers, direct debits, batch transfers through MoneyMoney's GUI+TAN flow.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: `metadata.{title, description, categories, tags}` wrapper — carries descriptive content; `metadata.pluginRoot` absent (not needed — single plugin with `"source": "./"`)
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `keywords` only on the plugin entry (`moneymoney`, `banking`, `finance`, `mcp`, `cli`). Marketplace-level `metadata.categories` (`finance`, `productivity`) and `metadata.tags` apply at marketplace scope, not per-plugin.
- **`$schema`**: absent on both `marketplace.json` and `plugin.json`
- **Reserved-name collision**: no — single plugin `moneymoney` does not clash with reserved names
- **Pitfalls observed**: marketplace name (`moneymoney`) equals plugin name; install command reads `moneymoney@moneymoney`, which looks redundant but is correct (`<plugin>@<marketplace>`). Repo name also `moneymoney`, so `lukasmalkmus/moneymoney` → `moneymoney@moneymoney` triples the token across three namespaces.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./"`) — single plugin lives at repo root
- **`strict` field**: default (implicit true) — field absent on the marketplace entry
- **`skills` override on marketplace entry**: absent
- **Version authority**: both `plugin.json` and `marketplace.json` carry `version: 0.4.0` (drift risk — two sources of truth). The `ensure-binary.sh` and `bin/mm` read version from `plugin.json` only, so `plugin.json` is the de-facto authority for runtime behavior; the marketplace-entry duplicate exists for manifest display but is not enforced consistent by any observed tooling.
- **Pitfalls observed**: the marketplace entry repeats `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords` — all also present in `plugin.json`. On version bump, both must change in lockstep or the marketplace display diverges from the installed plugin.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via `@ref` (git tag) if they want a specific version. Single main branch, linear tag history v0.1.0 → v0.4.0.
- **Channel-pinning artifacts**: absent
- **Pitfalls observed**: none — low-volume single-author plugin, no stable/latest split warranted

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main (linear — no release branches)
- **Release branching**: none (tag-on-main)
- **Pre-release suffixes**: none observed
- **Dev-counter scheme**: absent — main carries real semver, not `0.0.z` dev counter
- **Pre-commit version bump**: no — version bumped manually in release commits (e.g., `release: v0.4.0` commit message)
- **Pitfalls observed**: v0.1.0, v0.2.0, v0.3.0, v0.4.0 all dated 2026-04-20 per CHANGELOG — rapid initial rollout; no sustained cadence signal yet

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` contains only metadata (`name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`); no explicit `skills`/`commands`/`agents`/`hooks`/`mcpServers` fields. Components discovered by convention from directory layout.
- **Components observed**: skills yes (`skills/moneymoney/SKILL.md`) / commands no / agents no / hooks yes (`hooks/hooks.json`) / .mcp.json no (MCP server is built into the `mm` binary; invoked as `mm mcp` — not declared in Claude-plugin-style `.mcp.json`) / .lsp.json no / monitors no / bin yes (`bin/mm` shim) / output-styles no
- **Agent frontmatter fields used**: not applicable — skill frontmatter only. Skill declares `name`, `description`, `user-invocable: true`, `argument-hint: <question-or-query>`, `allowed-tools`
- **Agent tools syntax**: not applicable (no agents). Skill `allowed-tools` uses Claude Code permission-rule syntax with `Bash(mm <subcommand> *)` form — e.g., `Bash(mm accounts *)`, `Bash(mm transactions *)`. Write-side `mm transfer`, `mm transaction add/set` deliberately omitted from allowed-tools to force permission prompt.
- **Pitfalls observed**: `.claude-plugin/settings.json` is empty (`{}`) — kept as a placeholder rather than omitted; harmless but unused

## 6. Dependency installation

- **Applicable**: yes — Rust binary download at runtime
- **Dep manifest format**: Cargo.toml (for source build), but plugin consumers receive pre-built release binaries; no Python/Node dep manifest
- **Install location**: `${CLAUDE_PLUGIN_DATA}/bin/mm` (with version file at `${CLAUDE_PLUGIN_DATA}/bin/mm.version`); defaults to `$HOME/.claude/plugins/data/moneymoney` when `CLAUDE_PLUGIN_DATA` unset
- **Install script location**: `hooks/ensure-binary.sh` (SessionStart) plus `bin/mm` (lazy fallback at first invocation)
- **Change detection**: version-file stamp — `$data_dir/bin/mm.version` compared against `jq -r '.version' plugin.json`. If equal, skip; otherwise re-download.
- **Retry-next-session invariant**: no explicit `rm` on failure, but version file is only written *after* successful extraction — so a failed download leaves no stale version stamp, and the next invocation re-attempts the download. Effectively idempotent via write-last.
- **Failure signaling**: `set -euo pipefail`; stderr human-readable error with fallback install hints (`cargo install moneymoney --locked` or `brew install lukasmalkmus/tap/mm`); exit 127 mirrors "command not found". `ensure-binary.sh` (SessionStart) fires-and-forgets in a backgrounded subshell with `disown` — session start never blocks on network.
- **Runtime variant**: Go binary download-style (though the binary is Rust). Release assets are `mm-<target>.tar.gz` from GitHub releases; curl + tar xzf + chmod +x + xattr quarantine-strip.
- **Alternative approaches**: user-install paths explicitly supported — `cargo install moneymoney --locked` or `brew install lukasmalkmus/tap/mm`. Shim prefers those when present on PATH (see §7).
- **Version-mismatch handling**: shim re-downloads if `mm.version` stamp doesn't match `plugin.json`'s `version`. Platform check: only `Darwin/arm64` and `Darwin/x86_64` supported — other platforms exit 127 with macOS-only message (AppleScript is the MoneyMoney integration surface, so Linux `mm` would only return `NotSupported`).
- **Pitfalls observed**: macOS Gatekeeper — fresh download gets `com.apple.quarantine` attribute stripped via best-effort `xattr -d`. Without that, users would hit "cannot be opened because developer cannot be verified" on first run.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — this is the headline pattern
- **`bin/` files**: `bin/mm` — three-tier resolution shim (user-PATH → plugin-managed → download-on-demand); 3405 bytes; mode 100755
- **Shebang convention**: `#!/usr/bin/env bash`
- **Runtime resolution**: **user-PATH first then plugin-managed then download** — distinctive three-tier pattern:
  1. **User-installed mm wins** — `PATH` is cleaned of `self_dir` (via `grep -vFx` to prevent self-re-exec), then `command -v mm` searches the cleaned path. If found, `exec "$real_mm" "$@"`.
  2. **Plugin-managed cache** — if `$data_dir/bin/mm` exists and its recorded version matches `plugin.json`'s version, `exec "$installed_binary" "$@"`.
  3. **Lazy download** — curl release asset, tar xzf, chmod +x, xattr strip, exec.
- **Venv handling (Python)**: not applicable — Rust binary
- **Platform support**: macOS-only runtime (arm64 + x86_64 Darwin); cross-platform compile as CI sanity check only. Non-Darwin exits 127 with explicit "MoneyMoney is macOS-only" message plus install hints.
- **Permissions**: 100755 — committed with executable bit set (bin/mm, ensure-binary.sh, nudge-skill.sh)
- **SessionStart relationship**: hook lazily downloads binary via `ensure-binary.sh` — backgrounded-and-disowned subshell invoking `bin/mm --version` so the shim's own download logic executes once per session. Download logic lives in one place (bin/mm); the SessionStart hook just triggers it proactively. If SessionStart fails (no network), first real `mm` invocation pays the download cost instead.
- **Pitfalls observed**: PATH-cleaning discipline is subtle — `grep -vFx "$self_dir"` matches entire lines fixed-string, so a PATH entry that differs by trailing slash or case would not be stripped. Works because the shim constructs `self_dir` via `cd "$(dirname "$0")" && pwd` which canonicalizes. Worth noting: the same clean-path trick is duplicated in both `bin/mm` and `hooks/ensure-binary.sh` — any future change to the self-location logic must touch both.

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable. Config lives outside the plugin surface at `~/.config/mm/config.toml` (read by the `mm` binary itself), not via Claude-plugin `userConfig`/`CLAUDE_PLUGIN_OPTION_*` env vars. Credential isolation: "mm itself holds no credentials. MoneyMoney owns every bank secret in its encrypted store."
- **Pitfalls observed**: authentication gap for agents is bridged by MoneyMoney's own GUI+TAN flow for write ops, not by plugin config — no Claude-plugin surface for it.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none
- **PostToolUse hooks**: 1 — matcher `"Bash"`, purpose: skill nudge. When a Bash command contains `mm` as a word (regex `(^|[^a-zA-Z0-9-])mm($|[[:space:]])` — excludes substrings like `mmdd` or `commit`), emit a one-time per-session `<system-reminder>` pointing agents at `/moneymoney` skill. Marker file at `${TMPDIR}/.moneymoney-skill-nudge-${session_id}` ensures one-shot.
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: stdout JSON via `jq -n` producing `{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: <nudge>}}` — the `additionalContext` path is the documented injection channel. No stderr used for successful path.
- **Failure posture**: fail-open — script uses plain exit 0 on skip cases (no mm command detected, marker already exists, session id missing). No `set -e`.
- **Top-level try/catch wrapping**: absent — relies on plain shell exit codes
- **Pitfalls observed**: session-scoped one-shot nudge uses `$PPID` as fallback marker suffix when `session_id` is empty — `$PPID` is stable within a session but not across sessions, so if Claude Code doesn't emit a session_id the marker could be stale from a prior session. Acceptable trade-off for a purely informational nudge.

## 10. Session context loading

- **SessionStart used for context**: no — used only for dep install (see §6)
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: yes — in PostToolUse (§9), not in SessionStart. The PostToolUse handler injects a nudge as `additionalContext`.
- **SessionStart matcher**: none (fires on all sub-events — no `matcher` key set, so default is all SessionStart events: startup, clear, compact, resume)
- **Pitfalls observed**: SessionStart fires on every sub-event (clear/compact/resume), so the background `mm --version` warmup runs more than once per user session. Idempotent via version-stamp check, so redundant runs cost at most a stamp comparison.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable (no monitors)
- **Pitfalls observed**: none

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace, tag format is plain `v0.4.0` (no plugin-name prefix needed)
- **Pitfalls observed**: none

## 13. Testing and CI

- **Test framework**: `cargo test` (Rust built-in)
- **Tests location**: inline per Rust convention — `#[cfg(test)] mod tests` within source files. No separate `tests/` directory at repo root observed in the top-level listing.
- **Pytest config location**: not applicable
- **Python dep manifest for tests**: not applicable
- **CI present**: yes — `.github/workflows/ci.yaml` (+ `release.yaml`)
- **CI file(s)**: `ci.yaml`, `release.yaml`
- **CI triggers**: `push: branches: [main]` and `pull_request`, both with `paths-ignore: ["**.md", "LICENSE", ".claude-plugin/**", "skills/**", "hooks/**"]` — plugin-surface edits don't retrigger Rust CI
- **CI does**: fmt (`cargo fmt --all --check`), clippy (`cargo clippy --all-targets -- -D warnings`), MSRV extraction (greps `rust-version` from Cargo.toml), test (stable + MSRV on ubuntu-latest, stable on macos-latest), audit (`rustsec/audit-check@v2`), docs (`cargo doc --no-deps --all` with `RUSTDOCFLAGS: -D warnings`)
- **Matrix**: toolchain × os — `{stable, ubuntu-latest}`, `{MSRV-from-file, ubuntu-latest}`, `{stable, macos-latest}`
- **Action pinning**: tag-pinned (`actions/checkout@v6`, `dtolnay/rust-toolchain@stable`, `Swatinem/rust-cache@v2`, `rustsec/audit-check@v2`, `taiki-e/upload-rust-binary-action@v1`, `actions/upload-artifact@v7`, `taiki-e/create-gh-release-action@v1`, `actions/download-artifact@v8`) — major-tag pinning throughout, no SHA pinning
- **Caching**: `Swatinem/rust-cache@v2` on clippy + test + docs jobs
- **Test runner invocation**: direct `cargo test --all` in CI; local use `cargo build && cargo test && cargo clippy -- -D warnings && cargo fmt --check`
- **Pitfalls observed**: `paths-ignore` blocks CI on plugin-surface-only edits — pure skill/hook iteration lands without Rust CI signal, which is the right call (skill changes don't affect the binary) but means no lint/format pass on `hooks/*.sh` shell scripts. No shellcheck in CI.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes — `.github/workflows/release.yaml`
- **Release trigger**: `push: tags: ["v*"]`
- **Automation shape**: Rust cross-compile + GitHub Release with binary tarballs. Build job: matrix over `x86_64-apple-darwin` and `aarch64-apple-darwin` on `macos-latest`, uses `taiki-e/upload-rust-binary-action@v1` with `dry-run: true` to produce archives, then `actions/upload-artifact@v7` stashes them. Release job: downloads artifacts, calls `taiki-e/create-gh-release-action@v1` with `changelog: CHANGELOG.md`, then `gh release upload "${GITHUB_REF_NAME}" artifacts/*`.
- **Tag-sanity gates**: none (no verify-tag-on-main, no tag=version check, no regex gate)
- **Release creation mechanism**: `taiki-e/create-gh-release-action@v1` (parses CHANGELOG.md) + `gh release upload` for assets
- **Draft releases**: no — published directly
- **CHANGELOG parsing**: yes — `taiki-e/create-gh-release-action@v1` extracts the relevant version section from CHANGELOG.md
- **Pitfalls observed**: release artifacts contract is `mm-<target>.tar.gz` — `bin/mm` download URL hard-codes this shape (`https://github.com/.../releases/download/v${version}/mm-${target}.tar.gz`). If the build workflow's asset naming ever changes (e.g., via a `taiki-e/upload-rust-binary-action` option), the shim's URL breaks silently until the next session's download attempt.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: no
- **Hooks.json validation**: no
- **Pitfalls observed**: marketplace.json and plugin.json duplicate version/description/author/etc. — with no validator checking parity, drift is a silent failure mode (see §2)

## 16. Documentation

- **`README.md` at repo root**: present (~5 KB — install table with plugin/cargo/brew/manual rows, features, SEPA note, credential isolation note)
- **Owner profile README at `github.com/lukasmalkmus/lukasmalkmus`**: present (~38 lines, resume-tier portfolio — auto-generated activity feed via markscribe)
- **`README.md` per plugin**: not applicable — single-plugin repo where plugin lives at root
- **`CHANGELOG.md`**: present, Keep a Changelog format (1.1.0, SemVer-aligned); versions 0.1.0 → 0.4.0 all dated 2026-04-20
- **`architecture.md`**: absent
- **`CLAUDE.md`**: present at repo root — duplicate content with `AGENTS.md` (both are agent-facing design references covering CLI shape, output formats, exit codes, build, commit format, dependencies, skills)
- **Community health files**: none observed (no SECURITY.md, CONTRIBUTING.md, or CODE_OF_CONDUCT.md at repo root or in `.github/`)
- **LICENSE**: present (MIT)
- **Badges / status indicators**: not inspected directly, but README opening lines do not carry badge markdown
- **Pitfalls observed**: `CLAUDE.md` and `AGENTS.md` overlap substantially — both describe the CLI shape and dev conventions. Single source of truth would be preferable, with one pointing to the other. Observed state: duplicated content, high drift risk on refactor.

## 17. Novel axes

- **User-PATH-first three-tier binary resolution.** The distinctive pattern: shim at `bin/mm` tries the user's own `mm` install first (cargo / brew / manual), falls back to a plugin-managed cached binary at `${CLAUDE_PLUGIN_DATA}/bin/mm`, and only downloads from GitHub releases as a last resort. PATH-cleaning via `grep -vFx "$self_dir"` prevents self-re-exec when the shim itself is on PATH. This inverts the more common "plugin-managed only" approach — a user who already has `cargo install moneymoney` or `brew install lukasmalkmus/tap/mm` runs their own binary, and the plugin never competes with them. Natural corollary: the user's install is authoritative even if it's a different version than `plugin.json` declares, which is a deliberate trade (user ergonomics over version precision).

- **Background-disowned SessionStart warmup with lazy fallback.** `ensure-binary.sh` never blocks session startup on network — it forks a `( "$plugin_root/bin/mm" --version ) & disown` subshell and exits 0 immediately. The worst case (network failure at session start) is that the first real `mm` invocation pays the download cost. Composes with the shim's own lazy-download path — download logic lives in exactly one place (`bin/mm`), and the hook merely triggers it early.

- **Version-stamp file as idempotency ratchet.** `$data_dir/bin/mm.version` is written *only after* successful extraction, so a failed download leaves no stamp and the next run re-attempts cleanly without explicit cleanup. Compare/contrast with approaches that write markers before extraction and need `rm-on-failure` recovery.

- **Gatekeeper quarantine strip as part of the install path.** Best-effort `xattr -d com.apple.quarantine` after chmod +x — macOS-specific prerequisite that other bin-wrapper patterns don't need because they don't download unsigned binaries from GitHub.

- **PostToolUse skill-nudge with word-boundary regex.** The `mm` command substring is common (`mmdd`, `commit`, `common`, etc.), so the nudge hook uses `(^|[^a-zA-Z0-9-])mm($|[[:space:]])` to match `mm` only as a whole token. One-shot per session via `${TMPDIR}/.moneymoney-skill-nudge-${session_id}` marker file — subsequent `mm` invocations in the same session skip the reminder. Rare pattern: most nudge hooks fire every time or use PreToolUse blocking; this one is a one-shot informational PostToolUse nudge.

- **Asset-path hard-coupling between release workflow and shim.** The shim's download URL (`mm-<target>.tar.gz`) is literally hardcoded and assumes `taiki-e/upload-rust-binary-action`'s default naming. No abstraction layer — any future refactor of release artifact naming must touch both `release.yaml` and `bin/mm` in lockstep. Deliberate simplicity: no pointer file, no manifest lookup, no runtime asset discovery.

- **CI `paths-ignore` covering the entire plugin surface.** `.github/workflows/ci.yaml` skips runs for edits under `.claude-plugin/**`, `skills/**`, `hooks/**`, plus `**.md` and `LICENSE`. The Rust CI is scoped to Rust changes only; plugin-surface iteration is CI-free. Side effect: no linting of shell hooks in CI.

- **Platform filter enforced in the shim, not at install time.** Non-Darwin platforms fail loudly at `bin/mm` invocation with a specific error ("MoneyMoney is macOS-only") plus install-hint fallbacks. The plugin itself installs cleanly on any OS — the capability filter is runtime, not install-time.

## 18. Gaps

- **Interactive install path not exercised.** The WebFetch-based research can read static artifacts but cannot observe what Claude Code actually does on `/plugin install moneymoney@moneymoney` — specifically whether the empty `.claude-plugin/settings.json` causes any warning or whether the missing `settings` field is inferred as "use defaults". Resolving: `claude plugin install` trace from a real session.

- **SessionStart `matcher` implicit-default behavior.** The hook entry omits `matcher`. Template leaves this as "none (fires on all sub-events)" per the plugin reference docs, but this was inferred from docs-hooks.md context rather than observed in a live session. Resolving: session log showing SessionStart firing on `clear` or `compact` and confirming the hook runs.

- **Cross-install-method version-drift behavior.** When a user has `cargo install moneymoney` at one version and `plugin.json` declares a different version, the shim silently runs the user's version. Whether the skill instructions still apply correctly across versions, and whether the MCP server shape is compatible, is unverified. Resolving: multi-version compatibility test or explicit version-compatibility matrix in README.

- **`$PPID` session-id fallback for nudge marker.** In `nudge-skill.sh`, if `session_id` is empty the marker falls back to `$PPID`. Whether Claude Code always supplies `session_id` in the Bash PostToolUse JSON input was not verified. Resolving: live hook invocation dump showing the actual JSON.

- **`settings.json` purpose.** `.claude-plugin/settings.json` is literally `{}` — whether this is a deliberate placeholder to permit future settings or a leftover scaffolding artifact is unclear. Resolving: git blame / commit history on the file.

- **AGENTS.md vs CLAUDE.md divergence policy.** Both files carry near-identical content. Whether the project maintains these in sync manually, via a symlink (which would show as a different tree mode), or via generator is unresolved. Resolving: diff the files byte-for-byte (not done here — content samples overlapped heavily but not all sections were compared).

- **Release artifact naming verification.** The shim's URL pattern (`mm-<target>.tar.gz`) is assumed to match what `taiki-e/upload-rust-binary-action@v1` uploads. Confirming would require inspecting an actual release's asset list via `gh api repos/lukasmalkmus/moneymoney/releases/tags/v0.4.0` — not performed within this budget.

- **Shell lint absence.** CI does not run shellcheck or similar on `hooks/*.sh` or `bin/mm`. Whether this is an intentional choice or oversight is unresolved. Resolving: ask maintainer or check discussion threads.
