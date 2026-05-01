# brunoborges/ghx

## Identification

- **URL**: https://github.com/brunoborges/ghx
- **Stars**: 4
- **Last commit date**: 2026-04-17 (pushed 2026-04-17T01:42:14Z; latest commit `434a676` "Update SECURITY.md" 2026-04-17T01:34:32Z)
- **Default branch**: main
- **License**: MIT
- **Sample origin**: dep-management + bin-wrapper
- **One-line purpose**: "GitHub CLI Cache Proxy. Caching daemon for the gh CLI to prevent API rate limiting." The Claude plugin under `agent-plugin/` distributes lazy-installing wrappers that route `gh` and `ghx` calls through the Go `ghx`/`ghxd` binaries.

## 1. Marketplace discoverability

- **Manifest layout**: no marketplace manifest in this repo — `brunoborges/ghx` is the plugin source (at subpath `agent-plugin/`). The marketplace lives in a sibling repo `brunoborges/agent-plugins` which publishes the same `marketplace.json` at two locations: `.claude-plugin/marketplace.json` (Claude Code) and `.github/plugin/marketplace.json` (GitHub Copilot CLI). Dual-publishing one manifest to target two agentic CLIs.
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper (`version: "1.0.0"`, no `pluginRoot`).
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: `keywords` only (`["github", "cli", "cache", "proxy", "rate-limit", "performance", "agentic"]`). No `category` or `tags`. Single-plugin marketplace.
- **`$schema`**: absent in both marketplace.json copies and plugin.json.
- **Reserved-name collision**: no.
- **Pitfalls observed**: two-file marketplace manifest duplication (aggregator ships byte-identical JSON under `.claude-plugin/` and `.github/plugin/`) is a drift risk — no automation ties them together; a bump to one must be mirrored by hand. Plugin version `1.5.0` in marketplace entry is already behind the latest upstream Go release (`v1.5.1`) — see purpose 2 drift note.

## 2. Plugin source binding

- **Source format(s) observed**: `github` with `path: "agent-plugin"` subdir binding. Single entry.
- **`strict` field**: default (implicit `true`) — not set.
- **`skills` override on marketplace entry**: absent.
- **Version authority**: both `plugin.json` (in the plugin repo) and the marketplace entry (in aggregator) carry `version: "1.5.0"`. Independently hand-bumped — the release-plugin CI workflow stamps plugin.json from the `plugin-v*` tag name (see purpose 14), but does not update the aggregator entry. Observed drift: upstream Go binaries are at `v1.5.1` while both plugin.json and marketplace entry still say `1.5.0`. The aggregator has to be bumped by a separate commit ("Bump ghx plugin version to 1.5.0" 2026-04-16).
- **Pitfalls observed**: version is declared in three places (plugin.json, aggregator `.claude-plugin/marketplace.json`, aggregator `.github/plugin/marketplace.json`) that have no linker — manual coordination. The `plugin-v*` vs `v*` tag namespaces let plugin and binary versions diverge intentionally, but there's no guard against forgetting to cut a plugin release after a binary release.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via `@agent-plugins` to the marketplace; there is no stable/latest pair.
- **Channel-pinning artifacts**: absent. Install docs use `/plugin install ghx@agent-plugins` with no channel suffix.
- **Pitfalls observed**: none observed.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: on main. Two distinct tag namespaces coexist on the same branch — `v*` for the Go binary (e.g. `v1.5.1`, `v1.5.0`, …, back to `v0.0.1`) and `plugin-v*` for the plugin (only `plugin-v1.0.0` observed).
- **Release branching**: none — single-trunk with dual tag namespaces.
- **Pre-release suffixes**: none observed.
- **Dev-counter scheme**: absent.
- **Pre-commit version bump**: no.
- **Pitfalls observed**: the `plugin-v*` tag has only been cut once (`plugin-v1.0.0`) despite plugin.json advancing to `1.5.0` — the `release-plugin.yml` workflow only fires on `plugin-v*` tags, so intermediate plugin bumps ship without going through the release-plugin validator.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — no component fields at all. plugin.json carries `name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords` only. bin/ and skills/ are picked up by convention.
- **Components observed**: skills yes (`skills/ghx/SKILL.md`), commands no, agents no, hooks no, .mcp.json no, .lsp.json no, monitors no, bin yes (`bin/gh`, `bin/gh.cmd`, `bin/ghx`, `bin/ghxd`), output-styles no.
- **Agent frontmatter fields used**: not applicable (no agents).
- **Agent tools syntax**: not applicable.
- **Pitfalls observed**: `release-plugin.yml` validator checks for `agent-plugin/skills/ghxd/SKILL.md` but the actual path is `agent-plugin/skills/ghx/SKILL.md` (post-rebrand from `ghcd → ghx`). The validator would fail a real `plugin-v*` release cut — stale reference from pre-rename workflow. The SKILL.md frontmatter uses `allowed-tools: Bash` (single scalar, not list), and describes the skill with a mandatory-phrased description to get the skill auto-loaded by relevance.

## 6. Dependency installation

- **Applicable**: yes.
- **Dep manifest format**: none in the plugin. Go module (`go.mod`) lives at the repo root for the binaries; the plugin only ships the shim scripts and the installer. No `requirements.txt`, `package.json`, etc.
- **Install location**: `${CLAUDE_PLUGIN_DATA}/bin` (falls back to `$HOME/.ghx-plugin/bin` if unset). Binaries and installed version stamp (`.ghx-version`) all land there.
- **Install script location**: `agent-plugin/scripts/install.sh` (POSIX) and `agent-plugin/scripts/install.cmd` (Windows). Not invoked by a `hooks.json` — invoked lazily by the bin/ wrappers (see purpose 7).
- **Change detection**: existence only — `install.sh` short-circuits with `if [ -x "$INSTALL_DIR/ghx" ] && [ -x "$INSTALL_DIR/ghxd" ]; then exit 0; fi`. The `.ghx-version` stamp is written but never consulted for upgrade decisions.
- **Retry-next-session invariant**: existence-check gating means a partially-populated `$BIN_DIR` (one of the two binaries missing) would re-enter install; a corrupt-but-present binary would not. No explicit `rm` on failure — the installer uses a `mktemp -d` staging dir with `trap 'rm -rf "$TMPDIR"' EXIT`, so a failed download cleans the tmp, leaves the target dir untouched, and the next invocation retries.
- **Failure signaling**: `set -euo pipefail` halts; human-readable stderr (`ghxd-install: download failed`, etc.). Propagates exit code. No JSON/`systemMessage` because it's not a hook — it's invoked by the bin/ wrapper, which falls through to a `gh` fallback when install fails.
- **Runtime variant**: Go binary download. No Python/Node/Rust involvement.
- **Alternative approaches**: none in-repo. Note that the project *also* ships a Homebrew formula (generated by `release.yml` via a tap at `brunoborges/homebrew-tap`) for users who want `ghx` system-wide — orthogonal to the plugin.
- **Version-mismatch handling**: version is resolved at install time by hitting `https://api.github.com/repos/brunoborges/ghx/releases` (unauthenticated), filtering out `plugin-*` tags, and picking the first remaining tag. No pinning — the plugin always installs the freshest upstream binary regardless of what plugin.json version says. This is an explicit design choice: plugin.json tracks the wrapper release; the binary floats to HEAD.
- **Pitfalls observed**: unauthenticated GitHub API call to list releases is rate-limit-exposed (60 req/hour per IP) — ironic for a plugin whose purpose is preventing rate limiting. Platform support is narrow: `install.sh` hard-fails on any OS other than linux/darwin, and on any arch other than amd64/arm64. Windows goes through `install.cmd` (PowerShell-driven). The tarball layout assumed by `install.sh` (flat `ghx`/`ghxd`/`gh` at the top of the archive) must match what `release.yml` packages — they do today, but there's no shared source of truth.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes.
- **`bin/` files**:
  - `bin/ghx` (740 bytes, bash) — checks `$BIN_DIR/ghx` exists and is executable; if so `exec`s it; otherwise runs `install.sh`, then re-checks and execs. Fallback: `exec gh "$@"` (`ghx` is a drop-in replacement). This is the core lazy-download pattern.
  - `bin/ghxd` (597 bytes, bash) — same shape as `bin/ghx` but for the daemon. No `gh` fallback (if install fails it exits 1).
  - `bin/gh` (824 bytes, bash) — "routes all gh commands through ghx for caching." Prefers co-located `./ghx` shim, then `ghx` on PATH, then the real `gh` anywhere on PATH *except* itself (detected by path comparison to avoid infinite recursion). Emits a stderr warning when falling back.
  - `bin/gh.cmd` (560 bytes, Windows batch) — counterpart to `bin/gh` for Windows, delegating to `ghx.cmd`.
- **Shebang convention**: `#!/usr/bin/env bash` on all POSIX shims with `set -euo pipefail`; `@echo off` for the `.cmd`.
- **Runtime resolution**: script-relative via `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` and `PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"`. `${CLAUDE_PLUGIN_ROOT}` is never referenced — the wrappers do not depend on that env var existing. The data path reads `${CLAUDE_PLUGIN_DATA}` with `~/.ghx-plugin` fallback.
- **Venv handling (Python)**: not applicable (Go binary).
- **Platform support**: POSIX (Linux/darwin) + Windows `.cmd` pair. Source notes "macOS or Windows/Linux (amd64 or arm64)". Only `gh` has a Windows `.cmd` shim in-repo — `ghx.cmd` and `ghxd.cmd` are expected to be provided by the Windows installer (via the release zip's `gh.cmd` generation).
- **Permissions**: Git tree mode reported as `file` for each — from the release-plugin workflow's `[ -x agent-plugin/bin/ghx ]` check, the committed shims are mode 100755. The four-file set (~2.7KB total; smallest 560B, largest 824B) confirms the "small shim" part of the pattern.
- **SessionStart relationship**: no hook relationship — there is no `hooks.json` in the plugin. Claude Code auto-adds `agent-plugin/bin/` to PATH by convention, and the lazy download happens the first time the agent invokes `ghx` or `ghxd` (or `gh` via its shim). This is the "small shim + lazy download on first use" pattern the task called out.
- **Pitfalls observed**: the `bin/gh` self-avoidance loop compares realpath of the candidate against `SCRIPT_DIR/gh`, which works only if the user has not created their own `gh` symlink that happens to canonicalize to the plugin's `gh`. On PATH environments where the plugin's `bin/` comes before `gh` but the user has *also* installed the plugin's shim into `$BIN_DIR` (so `install.sh`'s `has_real_gh` thought no real gh was present), a double-layer of shims can occur; the `ghx-shim` marker grep in `has_real_gh` mitigates but only for the exact shim text pattern.

## 8. User configuration

- **`userConfig` present**: no.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable — no hooks, no MCP, no monitors to substitute into.
- **Pitfalls observed**: none observed. `gh auth login` authentication is explicitly deferred to the user (called out in the plugin README) — not re-implemented inside the plugin.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none — no hooks.json.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable.
- **Failure posture**: not applicable.
- **Top-level try/catch wrapping**: not applicable.
- **Pitfalls observed**: enforcement is entirely prose-based — the SKILL.md description contains "MANDATORY" and "Never invoke `gh` directly" phrasing to bias the agent. There is no hook that rejects a raw `gh` Bash invocation. A PreToolUse matcher on `Bash` checking the first token for `gh ` (and rewriting to `ghx`) would be the enforcement counterpart; it's absent.

## 10. Session context loading

- **SessionStart used for context**: no — no hooks at all.
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: not applicable.
- **SessionStart matcher**: not applicable.
- **Pitfalls observed**: none observed. Context is injected by the skill's `description` field (auto-loaded) and by the skill body when invoked.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: absent (no monitors.json to gate).
- **Pitfalls observed**: none observed.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace).
- **Pitfalls observed**: none observed.

## 13. Testing and CI

- **Test framework**: `go test` for the Go binaries. No Claude-plugin-specific tests.
- **Tests location**: not applicable for plugin — Go tests live alongside Go sources under `cmd/` and `internal/`. No `tests/` directory for the plugin shims. Plugin shims are validated by `bash -n` parse checks in the release-plugin workflow.
- **Pytest config location**: not applicable.
- **Python dep manifest for tests**: not applicable.
- **CI present**: yes.
- **CI file(s)**: `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `.github/workflows/release-plugin.yml`.
- **CI triggers**: `ci.yml` — `pull_request: [main]`, `schedule: '0 8 * * *'` daily, `workflow_dispatch`. `release.yml` — `push: tags: v*`. `release-plugin.yml` — `push: tags: plugin-v*`.
- **CI does**: Go build, `go test -race -coverprofile`, `go vet`, `gofmt -l .` (fails if non-empty), plus a daily cross-matrix test run. The plugin-release workflow runs `python3 -m json.tool` on `plugin.json`, `bash -n` on each shim, and filesystem existence/executable checks on the expected paths.
- **Matrix**: PR matrix is `{ubuntu-latest, windows-latest}`. Daily matrix adds macOS and crosses with `{stable, oldstable}` Go versions. Release workflow crosses six Go `GOOS/GOARCH` targets (darwin/linux/windows × amd64/arm64).
- **Action pinning**: major tag (`actions/checkout@v4`, `actions/setup-go@v5`, `softprops/action-gh-release@v2`, `actions/upload-artifact@v4`). No SHA pins.
- **Caching**: built-in `actions/setup-go@v5` with `go-version-file: go.mod` (implicit module cache). No explicit `actions/cache`.
- **Test runner invocation**: `go test -race -coverprofile coverage.out ./...` direct.
- **Pitfalls observed**: the CI matrix never exercises the plugin wrappers end-to-end on macOS (plugin shim coverage comes only from the release-plugin workflow's static checks). No test runs `install.sh` against a real release — a broken release asset layout would only surface at user install time.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes — two of them (`release.yml` for the Go binary, `release-plugin.yml` for the Claude plugin).
- **Release trigger**: `release.yml` on `push: tags: v*`; `release-plugin.yml` on `push: tags: plugin-v*`.
- **Automation shape**:
  - `release.yml`: cross-compiles ghx/ghxd for six GOOS/GOARCH pairs, packages tar.gz (POSIX) / zip (Windows) including a generated `gh` or `gh.cmd` shim inside the archive, uploads via `softprops/action-gh-release@v2` with `generate_release_notes: true`, computes sha256 checksums, then generates and pushes a Homebrew formula to `brunoborges/homebrew-tap` (Formula/ghx.rb).
  - `release-plugin.yml`: validates the plugin tree (file existence, JSON lint, `bash -n`, executable bit), stamps plugin.json `version` from the `plugin-v*` tag using a Python one-liner, packages `ghxd-plugin-${VERSION}.tar.gz` from `agent-plugin/`, computes sha256, creates a GitHub Release.
- **Tag-sanity gates**: release-plugin stamps plugin.json from the tag (enforcing tag→plugin.json equality at release time, though only one-way); no explicit verify-tag-on-main. release.yml takes `VERSION=${GITHUB_REF#refs/tags/}` directly with no tag-format regex.
- **Release creation mechanism**: `softprops/action-gh-release@v2` in both.
- **Draft releases**: no — immediate publish.
- **CHANGELOG parsing**: no — both use `generate_release_notes: true` and there is no CHANGELOG.md in the repo.
- **Pitfalls observed**: the release-plugin validator references a stale skill path (`skills/ghxd/SKILL.md`, actual is `skills/ghx/SKILL.md`) — a real `plugin-v*` tag push would fail validation today. The aggregator repo `brunoborges/agent-plugins` has no release automation — marketplace.json version bumps are hand commits.

## 15. Marketplace validation

- **Validation workflow present**: no dedicated validation workflow. `release-plugin.yml` bundles validation into the release pipeline.
- **Validator**: ad-hoc shell + `python3 -m json.tool` + `bash -n`. No `zod`, no `claude plugin validate` CLI, no pre-commit hook.
- **Trigger**: `push: tags: plugin-v*` only — no `pull_request` or `push: main` validation.
- **Frontmatter validation**: no — SKILL.md frontmatter is not schema-checked.
- **Hooks.json validation**: not applicable (no hooks.json).
- **Pitfalls observed**: validation fires only at release time, not on PR, so structural drift (e.g. the `skills/ghxd/` vs `skills/ghx/` mismatch) sits latent on `main` until a tag is pushed. Pre-merge validation coverage is zero for the plugin.

## 16. Documentation

- **`README.md` at repo root**: present (15422 bytes, substantial).
- **Owner profile README at `github.com/brunoborges/brunoborges`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: present (`agent-plugin/README.md`, 3175 bytes).
- **`CHANGELOG.md`**: absent. GitHub Releases `generate_release_notes` is the de facto changelog.
- **`architecture.md`**: absent. `SPEC.md` (23037 bytes) and `ADR.md` (6831 bytes) at repo root cover the Go binary's architecture — not mirrored into the plugin.
- **`CLAUDE.md`**: absent — neither at repo root nor under `agent-plugin/`. Also no `AGENTS.md`.
- **Community health files**: `LICENSE` (MIT), `SECURITY.md` (518 bytes) at repo root. No `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`. The aggregator repo (brunoborges/agent-plugins) has only `README.md`, no community health files.
- **LICENSE**: present (MIT, SPDX `MIT`).
- **Badges / status indicators**: not observed in the plugin README; repo root README likely has badges (not fully inspected).
- **Pitfalls observed**: a large one-off tarball sits in the repo root (`copilot-debug-logs-e1643f64-592c-46d5-b016-f515818c1184.tgz`, 66KB) and the pre-built `ghxd` binary (~10MB) is committed at repo root — committed debug artifacts that should probably be gitignored. The `.gitignore` is 100 bytes and evidently does not cover them.

## 17. Novel axes

- **Dual-CLI marketplace manifest publishing**: one JSON object served from two paths (`.claude-plugin/marketplace.json` for Claude Code, `.github/plugin/marketplace.json` for GitHub Copilot CLI) in the aggregator repo. Both files are byte-identical — a deliberate choice to make one plugin source discoverable by two agentic runtimes without maintaining parallel manifests. No shared-source tooling; they diverge by hand.
- **Dual tag namespace on a single trunk**: `v*` governs the Go binary releases (10 observed, `v0.0.1` → `v1.5.1`), `plugin-v*` governs the plugin releases (1 observed, `plugin-v1.0.0`). This lets the binary iterate rapidly without forcing plugin.json bumps, and lets the plugin iterate without triggering a binary rebuild. Separate workflows dispatched by tag prefix.
- **Non-hook lazy install pattern**: the dependency install runs entirely from `bin/` shims — no `SessionStart`, no `hooks.json`. Instead of install-at-startup, the plugin installs-on-first-use and caches by existence check. Trade-off: zero session-start overhead, but the first `ghx` call pays a ~1s download (mostly unnoticed because it's a one-shot).
- **Drop-in fallback chain**: every shim layers a fallback — `bin/ghx` falls back to system `gh` if install fails; `bin/gh` falls back through (1) co-located `ghx`, (2) PATH `ghx`, (3) PATH `gh` (skipping itself). This makes the plugin gracefully degrade to "vanilla gh, no caching" if anything breaks, which is a different posture from most bin-wrappers that hard-fail.
- **Unauthenticated release-list call to resolve version at install time**: `install.sh` asks `api.github.com/repos/brunoborges/ghx/releases` without a token and filters out `plugin-*` tags client-side. Self-referential irony (a rate-limit-prevention plugin that invokes the rate-limited API to install itself) and a durability risk for users behind low-IP-quota NATs.
- **Conditional shim installation with marker-based self-detection**: `install.sh` scans `$PATH` for any `gh` that does *not* contain the literal string `ghx-shim` in its first bytes (`has_real_gh`), and only installs the `gh` shim if no real `gh` was found. The `ghx-shim` marker is placed by both `install.sh` (when falling back to generating a shim) and `release.yml` (when packaging the tarball). Prevents shadowing a real `gh` users already have.
- **Homebrew tap generation inside the GitHub Release workflow**: `release.yml` ends with 100+ lines that synthesize a Homebrew formula (with per-platform URLs and sha256) via heredoc, clones `brunoborges/homebrew-tap` with a PAT, commits `Formula/ghx.rb`, pushes. Orthogonal to the plugin but unusual enough to note: the plugin itself is not the only distribution channel.
- **Skill description as enforcement surrogate**: no PreToolUse hook exists to enforce `ghx` over `gh`; the SKILL.md description uses capitalized "MANDATORY" / "Never invoke `gh` directly" phrasing to get auto-loaded and to bias the model. Prose-only enforcement, relying on skill auto-load.

## 18. Gaps

- Whether Claude Code actually auto-adds `agent-plugin/bin/` to PATH without any plugin.json field was not verified against the plugins-reference doc in this pass — this is *observed* behavior (implied by the install docs claiming "PATH works") but *inferred* as convention-based discovery.
- The mode bits on committed `bin/` files (100755 vs 100644) were inferred from `release-plugin.yml`'s `[ -x ... ]` gate presupposing executable bits in-tree; actual git tree mode would need `git ls-tree HEAD agent-plugin/bin/` on a clone.
- Whether the aggregator `brunoborges/agent-plugins` has any CI (validation on PR, marketplace.json schema check) was only partially checked — only `.github/plugin/` was listed; a full `.github/workflows/` traversal was not done.
- `copilot-instructions.md` at `.github/copilot-instructions.md` was listed but not fetched — its content might encode agent-facing rules overlapping with SKILL.md.
- `SPEC.md` and `ADR.md` at repo root were inventoried but not read — they may contain further novel pattern material (e.g., cache invalidation design) that is orthogonal to the plugin but noted for completeness.
- The plugin README mentions "GitHub Copilot CLI Plugin format" compatibility but it was not verified whether that format has additional fields in `plugin.json` that Claude Code would ignore — the observed plugin.json has only Claude-compatible fields.
- The aggregator's two marketplace.json paths are byte-identical today — it was not verified whether a CI job enforces that, or whether drift would go undetected.
