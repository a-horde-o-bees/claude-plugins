# Sample

Mirrors of `https://github.com/brunoborges/ghx`. GitHub CLI cache proxy — caching daemon for the `gh` CLI to prevent API rate limiting; the Claude plugin under `agent-plugin/` distributes lazy-installing wrappers that route `gh` and `ghx` calls through the Go `ghx`/`ghxd` binaries. 4 stars; default branch `main`; MIT license; latest commit 2026-04-17 (`434a676` "Update SECURITY.md"). The marketplace lives in a sibling repo `brunoborges/agent-plugins`.

## Marketplace manifest layout

### Duplicated marketplace manifest at root and nested

The aggregator repo `brunoborges/agent-plugins` publishes byte-identical `marketplace.json` at two paths: `.claude-plugin/marketplace.json` (Claude Code) and `.github/plugin/marketplace.json` (GitHub Copilot CLI). Dual-publishing one manifest to target two agentic CLIs. No automation ties them together; a bump to one must be mirrored by hand. The plugin source repo (`brunoborges/ghx`) carries no `marketplace.json` — only the plugin payload at `agent-plugin/`.

### Top-level `metadata` wrapper variants

Aggregator marketplace.json carries `metadata.{description, version}` wrapper (`version: "1.0.0"`); no `metadata.pluginRoot`.

## Plugin source binding

### `source: github` with explicit coords or `ref` pinning

Single entry uses `github` source format with `path: "agent-plugin"` subdir binding into `brunoborges/ghx`. Single-plugin marketplace.

### `strict` field default

Default (implicit `true`) — not set on the marketplace entry.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Marketplace entry carries `keywords` only (`["github", "cli", "cache", "proxy", "rate-limit", "performance", "agentic"]`). No `category`, no `tags`. plugin.json carries `name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords` only.

### `$schema` absence on per-plugin manifests

`$schema` absent in both marketplace.json copies and in plugin.json.

## Version coordination

### Multi-site sprawl (5+ locations)

Version is declared in three places (plugin.json, aggregator `.claude-plugin/marketplace.json`, aggregator `.github/plugin/marketplace.json`) that have no linker — manual coordination required. The release-plugin CI workflow stamps plugin.json from the `plugin-v*` tag name (see release automation), but does not update the aggregator entry. Observed drift: upstream Go binaries are at `v1.5.1` while both plugin.json and marketplace entry still say `1.5.0`. The aggregator has to be bumped by a separate commit ("Bump ghx plugin version to 1.5.0" 2026-04-16).

### Deliberate divergence: wrapper vs underlying binary

Plugin.json tracks the wrapper release; the binary floats to HEAD. `install.sh` resolves the binary version at install time by hitting `https://api.github.com/repos/brunoborges/ghx/releases` (unauthenticated), filtering out `plugin-*` tags, and picking the first remaining tag. No pinning — the plugin always installs the freshest upstream binary regardless of what plugin.json version says. The `plugin-v*` vs `v*` tag namespaces let plugin and binary versions diverge intentionally.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split. Users pin via `@agent-plugins` to the marketplace; install docs use `/plugin install ghx@agent-plugins` with no channel suffix. There is no stable/latest pair.

## Tag and release lifecycle

### Dual tag namespaces on a single trunk

Two distinct tag namespaces coexist on main: `v*` for the Go binary releases (10 observed, `v0.0.1` → `v1.5.1`) and `plugin-v*` for plugin releases (1 observed, `plugin-v1.0.0`). Lets the binary iterate rapidly without forcing plugin.json bumps and lets the plugin iterate without triggering a binary rebuild. Separate workflows dispatched by tag prefix.

### Single lifetime tag with drift

The `plugin-v*` tag has been cut once (`plugin-v1.0.0`) despite plugin.json advancing to `1.5.0`. The `release-plugin.yml` workflow only fires on `plugin-v*` tags, so intermediate plugin bumps ship without going through the release-plugin validator.

## Plugin-component registration

### Default convention discovery

No component fields in plugin.json. Carries only `name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`. `bin/` and `skills/` are picked up by convention.

## Component composition

### Skills (universal)

`skills/ghx/SKILL.md`. SKILL.md frontmatter uses `allowed-tools: Bash` (single scalar, not list). Description uses mandatory-phrased prose to bias auto-load.

### Commands

None.

### Agents

None.

### Hooks

None.

### MCP servers

None — no `.mcp.json`.

### bin

`bin/gh`, `bin/gh.cmd`, `bin/ghx`, `bin/ghxd`.

### LSP config

None.

### output-styles, monitors

None.

## Skill authoring conventions

### `allowed-tools` as YAML array

SKILL.md frontmatter declares `allowed-tools: Bash` as a single scalar value (not YAML list).

## Server runtime (MCP)

### In-place stdlib script (no installer)

Not applicable — no MCP server in this plugin. The plugin distributes Go binaries via the bin shim layer rather than running an MCP server.

## Bin entry mechanism

### Lazy-install bin shim with fallback chain

Four shims totaling ~2.7 KB (smallest 560 B, largest 824 B). `bin/ghx` (740 bytes, bash) checks `$BIN_DIR/ghx` exists and is executable; if so `exec`s it, otherwise runs `install.sh`, re-checks, execs. Fallback: `exec gh "$@"` — `ghx` is a drop-in replacement. `bin/ghxd` (597 bytes, bash) same shape but for the daemon, no `gh` fallback (exits 1 if install fails). `bin/gh` (824 bytes, bash) "routes all gh commands through ghx for caching" — prefers co-located `./ghx`, then `ghx` on PATH, then real `gh` anywhere on PATH except itself (path-comparison self-avoidance to prevent infinite recursion); emits stderr warning when falling back. `bin/gh.cmd` (560 bytes, Windows batch) — counterpart for Windows, delegates to `ghx.cmd`. Shebang is `#!/usr/bin/env bash` on POSIX shims with `set -euo pipefail`; `@echo off` for `.cmd`. Every shim layers a fallback so the plugin gracefully degrades to "vanilla gh, no caching" if anything breaks.

The `bin/gh` self-avoidance loop compares realpath of the candidate against `SCRIPT_DIR/gh`. Conditional shim installation uses a marker scan: `install.sh` scans `$PATH` for any `gh` that does *not* contain the literal string `ghx-shim` in its first bytes (`has_real_gh`), and only installs the `gh` shim if no real `gh` was found. The `ghx-shim` marker is placed by both `install.sh` (when falling back to generating a shim) and `release.yml` (when packaging the tarball), preventing shadowing of a real `gh` users already have.

### Bash + `.cmd` pair for cross-platform

POSIX shell wrappers paired with Windows `.cmd` counterparts. Only `gh` has a Windows `.cmd` shim in-repo (`bin/gh.cmd`) — `ghx.cmd` and `ghxd.cmd` are expected to be provided by the Windows installer (via the release zip's `gh.cmd` generation).

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Script-relative resolution via `SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` and `PLUGIN_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"`. `${CLAUDE_PLUGIN_ROOT}` is never referenced — wrappers do not depend on that env var existing. The data path reads `${CLAUDE_PLUGIN_DATA}` with `~/.ghx-plugin` fallback.

## Dependency installation

### Native binary downloaded on first use with version-stamp idempotency

Install location is `${CLAUDE_PLUGIN_DATA}/bin` (with `$HOME/.ghx-plugin/bin` fallback if unset). Binaries and an installed-version stamp (`.ghx-version`) all land there. Install scripts: `agent-plugin/scripts/install.sh` (POSIX) and `agent-plugin/scripts/install.cmd` (Windows). Not invoked by a `hooks.json` — invoked lazily by the bin/ wrappers. Existence-only short-circuit: `if [ -x "$INSTALL_DIR/ghx" ] && [ -x "$INSTALL_DIR/ghxd" ]; then exit 0; fi`. The `.ghx-version` stamp is written but never consulted for upgrade decisions. Existence-check gating means a partially-populated `$BIN_DIR` (one of the two binaries missing) re-enters install; a corrupt-but-present binary does not. No explicit `rm` on failure — installer uses `mktemp -d` staging dir with `trap 'rm -rf "$TMPDIR"' EXIT`, so a failed download cleans the tmp, leaves the target dir untouched, and the next invocation retries.

Runtime variant: Go binary download (no Python/Node/Rust). Set `set -euo pipefail`; halts on error with human-readable stderr (`ghxd-install: download failed`, etc.). Propagates exit code. No JSON/`systemMessage` because it's not a hook — the bin/ wrapper falls through to a `gh` fallback when install fails.

Platform support is narrow: `install.sh` hard-fails on any OS other than linux/darwin and on any arch other than amd64/arm64; Windows goes through `install.cmd` (PowerShell-driven). The tarball layout assumed by `install.sh` (flat `ghx`/`ghxd`/`gh` at the top of the archive) must match what `release.yml` packages — they do today, but no shared source of truth.

Version resolved at install time by hitting unauthenticated `https://api.github.com/repos/brunoborges/ghx/releases`, filtering out `plugin-*` tags client-side, and picking the first remaining tag. Self-referential — a rate-limit-prevention plugin that invokes the rate-limited API to install itself; durability risk for users behind low-IP-quota NATs.

### No deps (pure manifest aggregator)

The plugin itself has no Python/Node/Ruby deps — no `requirements.txt`, no `package.json`. The Go binary's `go.mod` lives at the repo root for the binaries; the plugin only ships the shim scripts and the installer.

## Install change detection

### Existence-only check

`install.sh` short-circuits on existence of both binaries (`if [ -x "$INSTALL_DIR/ghx" ] && [ -x "$INSTALL_DIR/ghxd" ]; then exit 0; fi`). No hash check, no version-stamp comparison, no manifest diff — purely existence-based.

## Install trigger and lifecycle

### Lazy bootstrap on first hook (no SessionStart)

The dependency install runs entirely from `bin/` shims — no `SessionStart`, no `hooks.json`. Instead of install-at-startup, the plugin installs-on-first-use and caches by existence check. Trade-off: zero session-start overhead, but the first `ghx` call pays a ~1s download. Claude Code auto-adds `agent-plugin/bin/` to PATH by convention; the lazy download happens the first time the agent invokes `ghx` or `ghxd` (or `gh` via its shim).

## Install failure posture

### Human-readable stderr plus exit 1

`set -euo pipefail` halts on error with human-readable stderr. Propagates exit code. No JSON/`systemMessage` envelope. The bin/ wrapper falls through to a `gh` fallback (drop-in vanilla gh) when install fails — graceful degradation rather than hard failure.

## User configuration and authentication

### No user-supplied config

`userConfig` absent from plugin.json. No hooks, no MCP, no monitors to substitute into. `gh auth login` authentication is explicitly deferred to the user (called out in the plugin README) — not re-implemented inside the plugin.

## Tool-use enforcement

### Skill-description prose as enforcement surrogate

No PreToolUse hook exists to enforce `ghx` over `gh`. SKILL.md description contains capitalized "MANDATORY" / "Never invoke `gh` directly" phrasing to bias the agent and to get auto-loaded. There is no hook that rejects a raw `gh` Bash invocation. A PreToolUse matcher on `Bash` checking the first token for `gh ` (and rewriting to `ghx`) would be the enforcement counterpart; absent.

## Session context loading

### No session-context loading

No hooks at all. Context is injected by the skill's `description` field (auto-loaded) and by the skill body when invoked.

## Live monitoring

### `monitors.json` absent

No `monitors.json`.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field; single-plugin marketplace.

## Testing

### Go test

`go test -race -coverprofile coverage.out ./...` for the Go binaries. Go tests live alongside Go sources under `cmd/` and `internal/`. No Claude-plugin-specific tests; no `tests/` directory for the plugin shims. Plugin shims are validated by `bash -n` parse checks in the release-plugin workflow.

## CI workflow shape

### Multi-OS Go test matrix plus daily cross-version run

Three workflows: `.github/workflows/ci.yml`, `release.yml`, `release-plugin.yml`. Triggers: `ci.yml` runs on `pull_request: [main]`, `schedule: '0 8 * * *'` daily, `workflow_dispatch`. `release.yml` on `push: tags: v*`; `release-plugin.yml` on `push: tags: plugin-v*`. CI does Go build, `go test -race -coverprofile`, `go vet`, `gofmt -l .` (fails if non-empty), plus a daily cross-matrix test run. The plugin-release workflow runs `python3 -m json.tool` on `plugin.json`, `bash -n` on each shim, and filesystem existence/executable checks on the expected paths. PR matrix is `{ubuntu-latest, windows-latest}`. Daily matrix adds macOS and crosses with `{stable, oldstable}` Go versions. Release workflow crosses six Go `GOOS/GOARCH` targets (darwin/linux/windows × amd64/arm64). Action pinning by major tag (`actions/checkout@v4`, `actions/setup-go@v5`, `softprops/action-gh-release@v2`, `actions/upload-artifact@v4`); no SHA pins. Caching via built-in `actions/setup-go@v5` with `go-version-file: go.mod` (implicit module cache); no explicit `actions/cache`.

CI matrix never exercises the plugin wrappers end-to-end on macOS — plugin shim coverage comes only from the release-plugin workflow's static checks. No test runs `install.sh` against a real release; a broken release asset layout would only surface at user install time.

## Marketplace validation

### Ad-hoc shell + JSON-lint at release time

No dedicated validation workflow. `release-plugin.yml` bundles validation into the release pipeline: ad-hoc shell + `python3 -m json.tool` + `bash -n`. No `zod`, no `claude plugin validate` CLI, no pre-commit hook. Trigger is `push: tags: plugin-v*` only — no `pull_request` or `push: main` validation. Frontmatter is not schema-checked. Validation fires only at release time; structural drift (e.g., the `skills/ghxd/` vs `skills/ghx/` mismatch — `release-plugin.yml` validator checks `agent-plugin/skills/ghxd/SKILL.md` but the actual path is `agent-plugin/skills/ghx/SKILL.md` post-rebrand) sits latent on `main` until a tag is pushed. Pre-merge validation coverage is zero.

## Release automation

### Tag-triggered release with multi-gate sanity (npm)

`release.yml` cross-compiles ghx/ghxd for six GOOS/GOARCH pairs, packages tar.gz (POSIX) / zip (Windows) including a generated `gh` or `gh.cmd` shim inside the archive, uploads via `softprops/action-gh-release@v2` with `generate_release_notes: true`, computes sha256 checksums, then generates and pushes a Homebrew formula to `brunoborges/homebrew-tap` (Formula/ghx.rb). Triggered on `push: tags: v*`.

`release-plugin.yml` validates the plugin tree (file existence, JSON lint, `bash -n`, executable bit), stamps plugin.json `version` from the `plugin-v*` tag using a Python one-liner, packages `ghxd-plugin-${VERSION}.tar.gz` from `agent-plugin/`, computes sha256, creates a GitHub Release. Triggered on `push: tags: plugin-v*`.

Tag-sanity gates: release-plugin stamps plugin.json from the tag (enforcing tag→plugin.json equality at release time, one-way); no explicit verify-tag-on-main. release.yml takes `VERSION=${GITHUB_REF#refs/tags/}` directly with no tag-format regex. Both use `softprops/action-gh-release@v2`. Both publish immediately (no draft). Both use `generate_release_notes: true`; no CHANGELOG.md in the repo. The release-plugin validator references a stale skill path (`skills/ghxd/SKILL.md`, actual is `skills/ghx/SKILL.md`) — a real `plugin-v*` tag push would fail validation today. The aggregator repo has no release automation; marketplace.json version bumps are hand commits. `release.yml` also synthesizes a Homebrew formula and pushes to a tap repo (see Cross-ecosystem distribution).

## Documentation surface

### Architecture / design docs

Repo root carries `SPEC.md` (23037 bytes) and `ADR.md` (6831 bytes) covering the Go binary's architecture — not mirrored into the plugin tree.

### Layered repo / plugin / skill READMEs (uneven)

`README.md` at repo root (15422 bytes, substantial). Per-plugin `agent-plugin/README.md` (3175 bytes). No `CHANGELOG.md` — GitHub Releases `generate_release_notes` is the de facto changelog. No `CLAUDE.md` at repo root or under `agent-plugin/`. No `AGENTS.md`.

### Badges and status indicators

Not observed in the plugin README; repo root README likely has badges (not fully inspected).

## License declaration

### Single repo-level license

`LICENSE` (MIT) at repo root. SPDX identifier `MIT` declared in plugin.json.

## Community health files

### Bare minimum (LICENSE only)

`LICENSE` (MIT) and `SECURITY.md` (518 bytes) at repo root. No `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`. The aggregator repo (`brunoborges/agent-plugins`) has only `README.md` — no community health files.

## Cross-platform discipline

### Mixed shebangs partitioned by criticality

`#!/usr/bin/env bash` on all POSIX shims with `set -euo pipefail`; `@echo off` for the `.cmd`. The `bin/gh.cmd` (Windows batch) is partitioned from the bash shims by file extension; only `gh` has a Windows counterpart in-repo.

## Cross-ecosystem distribution

### Dual-harness (Claude Code + Gemini CLI)

One plugin source binds to two agentic CLIs via byte-identical marketplace.json published under two paths in the aggregator repo: `.claude-plugin/marketplace.json` (Claude Code) and `.github/plugin/marketplace.json` (GitHub Copilot CLI). The plugin README mentions "GitHub Copilot CLI Plugin format" compatibility; the observed plugin.json has only Claude-compatible fields.

### Homebrew formula generated by release workflow

`release.yml` synthesizes and pushes a Homebrew formula to `brunoborges/homebrew-tap` for users who want `ghx` system-wide — orthogonal to the plugin distribution channel.

## Distribution exclusion and dogfood layout

### Lockfile and node_modules inside plugin root

A large one-off tarball sits in the repo root (`copilot-debug-logs-e1643f64-592c-46d5-b016-f515818c1184.tgz`, 66 KB) and the pre-built `ghxd` binary (~10 MB) is committed at repo root — committed debug artifacts that should probably be gitignored. The `.gitignore` is 100 bytes and evidently does not cover them.
