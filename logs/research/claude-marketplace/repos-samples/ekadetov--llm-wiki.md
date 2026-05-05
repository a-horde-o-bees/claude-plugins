# Sample

Mirrors `https://github.com/ekadetov/llm-wiki`. Single-plugin marketplace — Claude Code plugin for persistent, compounding knowledge bases in Obsidian, applying Karpathy's LLM Wiki pattern. MIT license. Last commit 2026-04-06 (`5e49545a` — docs fix to WALKTHROUGH.md); default branch `main`; 53 stars. Sample origin: dep-management.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root with one plugin entry (`llm-wiki`) whose source is `"./"` — marketplace and plugin share the same repo root. Manifest has only top-level `name`, `owner`, `plugins`; no `metadata` wrapper, no top-level `description`.

### Top-level `metadata` wrapper variants

Flat top-level fields only — `name`, `owner`, `plugins`. No `metadata` wrapper, no `metadata.description`, no `metadata.pluginRoot`, no `$schema`. Minimal scaffolding.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` — marketplace and plugin are the same repo root. Co-located root is the simplest possible binding.

### `strict` field default

No `strict` key present; default (implicit true) applies. No `skills` override on marketplace entry.

## Source layout

### Single tree (plugin equals repo)

Plugin manifest at `.claude-plugin/`; components at conventional top-level directories (`commands/`, `skills/wiki/SKILL.md`, `hooks/hooks.json`).

## Per-plugin discoverability metadata

### No discoverability fields on marketplace entry

Marketplace plugin entry has only `name`, `source`, `description`; no `category`, `tags`, or `keywords`. Marketplace consumer scanning categories would not see this plugin at all.

### `$schema` absence on per-plugin manifests

`$schema` absent on `marketplace.json` and `plugin.json`.

## Version coordination

### Single source of truth (`plugin.json` only)

`"version": "2.0.0"` lives in `plugin.json`; `marketplace.json` declares no version. Eliminates drift risk by construction.

## Channel distribution

### No pinning surface

No tags exist (`gh api .../tags` returns `[]`); no GitHub releases. Single main branch. No multiple marketplace files, no tag-based channels. The only ref to pin against is a commit SHA or `main`.

## Tag and release lifecycle

### No tags at all

`gh api repos/ekadetov/llm-wiki/tags` returns `[]`. Default branch `main`; only `main` exists. No release branching, no pre-release suffixes. Commit history shows a manual `chore: bump version to 2.0.0` (e810af03) — human bump, not automation. Repo has version-jump history (`feat!:` breaking commits followed by manual version bumps) but zero tags and zero releases. The version in `plugin.json` is the only signal and moves with main. No `.pre-commit-config.yaml`, no `.husky/`, no `.github/` directory.

## Plugin-component registration

### Default convention discovery

`plugin.json` has no component path fields (only `name`, `version`, `description`, `author`). Components located by Claude Code's conventional layout: `commands/*.md`, `skills/*/SKILL.md`, `hooks/hooks.json`.

## Component composition

### Skills (universal)

`skills/wiki/SKILL.md` with `references/` subdir holding `compilation-guide.md` (1898 bytes) and `frontmatter-schemas.md` (1102 bytes).

### Commands

`commands/wiki.md` present.

### Hooks

`hooks/hooks.json` — single SessionStart entry for dep install. No `.mcp.json`, no `.lsp.json`, no agents, no monitors, no bin, no output-styles.

## Dependency installation

### SessionStart hook → npm install local to plugin

Plugin ships a SessionStart hook running `bash "${CLAUDE_PLUGIN_ROOT}/scripts/install-deps.sh"` (1590 bytes, registered in `hooks/hooks.json`). Installs `@tobilu/qmd` and `@marp-team/marp-cli` via `npm install`. Packages land in `${CLAUDE_PLUGIN_DATA}/node_modules/`. The skill references `${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd` and `.bin/marp`. No committed `package.json`, `package-lock.json`, or `requirements.txt` — the install script writes a minimal `{"private":true}` package.json into `${CLAUDE_PLUGIN_DATA}` on first run. Authoritative declaration of the two dependencies lives inline in the install script (`npm install @tobilu/qmd @marp-team/marp-cli`).

## Install change detection

### Three-gate idempotency

`scripts/deps-version.txt` (repo-committed, value `1.0.0`) is compared to `${CLAUDE_PLUGIN_DATA}/deps-version.txt` using `diff -q`. A sentinel file `${CLAUDE_PLUGIN_DATA}/.deps-ok` gates success. Only when all three conditions hold (sentinel exists, destination version file exists, `diff -q` reports no difference) does the script skip install. Any mismatch re-triggers npm install. Each gate is cheap and catches a different corruption mode (aborted install, partial file write, upstream version bump). Together they form a stricter check than any single mechanism.

## Install trigger and lifecycle

### SessionStart direct invocation

The `hooks.json` SessionStart entry has no `matcher` key, so it fires on all sub-events (startup, clear, compact). Since `diff -q` is idempotent this is fine, but every `/clear` re-runs the install check.

## Install failure posture

### `rm` stamp on failure (retry next session)

Explicit `rm -f "${SENTINEL}" "${VERSION_DST}"` on npm failure guarantees the next session retries. The repo-committed version file (`VERSION_SRC`) is never removed. Removing only the sentinel would still detect a corrupted-install state on next session (sentinel absence forces re-install); the script deletes both to be safe.

### Silent fail-open (`exit 0` always, retry every hook)

`set +e` explicitly disables exit-on-error; script header comment documents `MUST NEVER exit non-zero — that blocks sessions`. All `|| exit 0` fallthroughs and a final unconditional `exit 0`. Human-readable progress and error messages go to stderr via `echo ... >&2`. The graceful-degradation message `"Wiki will work without qmd/marp."` is the explicit fail-open contract to the user. `set +e` plus `|| exit 0` scattered throughout means any mkdir, cd, or cp failure silently degrades — a read-only `${CLAUDE_PLUGIN_DATA}` would exit 0 with no trace, leaving the skill to fall back to `index.md`-only mode without surfacing why.

## User configuration and authentication

### Hard-coded path as missing userConfig

`plugin.json` declares no `userConfig`. The README hard-codes `~/ObsidianVault/03-Resources/` as the vault path. The skill's directory walk enforces this prose convention. Users with a vault at any other path must symlink or change their layout. This is what a `userConfig` field would naturally hold.

## Session context loading

### Dependency install only (no context emission)

The single SessionStart hook runs `install-deps.sh` for dep management only; it does not emit `hookSpecificOutput.additionalContext`, `systemMessage`, or any context payload. No `UserPromptSubmit`.

## SessionStart matcher scope

### Empty matcher (all sub-events)

The `hooks.json` SessionStart entry has no `matcher` key, so it fires on all sub-events (startup, clear, compact). Idempotency check runs more often than strictly necessary; each invocation is cheap (three `test -f` + one `diff -q`) so it's not a correctness problem, just redundant work.

## Tool-use enforcement

### No enforcement (observational only)

`hooks/hooks.json` contains only a SessionStart entry. No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks. Plugin consciously does not gate tool use.

## Hook handler runtime

### Bash scripts at conventional path

`scripts/install-deps.sh` uses `#!/usr/bin/env bash`. `scripts/lint-wiki.py` (a content linter for the wiki, not a hook) uses `#!/usr/bin/env python3` and is stdlib-only.

## Hook failure posture

### Silent fail-open (`exit 0` always, retry every hook)

`install-deps.sh` opens with `set +e` and ends with unconditional `exit 0`. Header comment documents the contract `MUST NEVER exit non-zero — that blocks sessions`.

## Live monitoring

### `monitors.json` absent

No `monitors.json` present.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` has no `dependencies` key. Single-plugin marketplace with no tags at all.

## Testing

### No tests

Repo contains no `tests/`, no `*_test.py`, no `test_*.py`, no `spec.*` files. No test framework, no linting, no manifest validation, no CI. `scripts/lint-wiki.py` is a user-facing content linter for the wiki data, not a self-test of the plugin. A broken `marketplace.json` or `hooks.json` would only surface at user install time.

## CI workflow shape

### No CI

`gh api .../contents/.github` returns 404; no `.github/` directory of any kind.

## Marketplace validation

### No validation

No CI step validates manifest shape, version agreement, or frontmatter conformance. Marketplace and plugin manifests are hand-edited and trust-on-commit.

## Release automation

### No release automation / manual

No `release.yml`, no automation. Version bumps are manual commits. `chore: bump version to 2.0.0` (e810af03 commit) is the only release marker. There is no way to pin to `v2.0.0` as a ref — only commit SHA. No CHANGELOG.md.

## Documentation surface

### README + WALKTHROUGH.md as architecture-adjacent

`README.md` at repo root (3390 bytes) — installation, prerequisites, per-command usage with examples, wiki structure diagram, Obsidian/qmd integration notes, uninstall. `WALKTHROUGH.md` (17052 bytes) — long-form tutorial covering the Karpathy pattern, wiki structure, active-wiki detection, schema contract, per-command walkthroughs. Substantial enough to be architecture-adjacent, but framed as user tutorial rather than internal design. No `architecture.md`. No CHANGELOG.

### No CLAUDE.md

No `CLAUDE.md` at repo root. The plugin generates a `CLAUDE.md` template inside each created wiki's root at `~/ObsidianVault/03-Resources/<name>/CLAUDE.md` (documented in WALKTHROUGH.md as the wiki schema contract) — user-data scaffolding, not a plugin-level governance doc.

### Plugin scaffolds CLAUDE.md as user-data schema

The plugin scaffolds a `CLAUDE.md` inside each created wiki directory as part of `wiki init`. This `CLAUDE.md` is not the plugin's own governance doc — it is user data that becomes the schema contract for subsequent skill invocations. The skill's "active wiki detection" walks up looking for `CLAUDE.md` + `wiki/` as co-present markers. CLAUDE.md functioning as per-subdirectory schema anchor.

## License declaration

### Single repo-level license

LICENSE present at repo root (MIT, 1065 bytes; SPDX `MIT` from GitHub).

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE`. README has no Shields.io badges.

## Novel and cross-cutting concerns

### Generated-package.json pattern

The SessionStart install script writes a minimal `{"private":true}` `package.json` into `${CLAUDE_PLUGIN_DATA}` on first run rather than shipping one. Keeps the plugin repo free of Node-ecosystem noise (no committed lockfile, no `node_modules/` gitignore, no committed dep manifest) while still giving npm a valid project to operate on. Authoritative dep declaration lives inline in the install script's `npm install <pkg>` command.

### Graceful-degradation via fallback tool

When `${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd` is not executable (because SessionStart install failed), the skill falls back to manual `wiki/index.md` read + grep. Documented fail-soft path inside the skill itself, not an install retry — the plugin works (in reduced mode) even if dependency install permanently fails. Aligns with the install script's fail-open stance.

## Cross-role tools

### `${CLAUDE_PLUGIN_DATA}`

Install destination for npm-managed deps. The skill references `${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd` and `.bin/marp` directly from npm's install output. Bun-avoidance runtime guard wraps the qmd invocation in `env -u BUN_INSTALL ${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd` — Bun's bundled SQLite lacks extension loading, so when `BUN_INSTALL` is set, qmd fails to load its vector index.

## PATH augmentation and host-project setup

### Runtime-environment sanitization at invocation site

The skill's qmd invocation wraps every call in `env -u BUN_INSTALL ${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd`. Runtime environment sanitization specifically for a sqlite-vec incompatibility — Bun's bundled SQLite lacks extension loading.
