# Sample

Mirrors of `https://github.com/JordanCoin/pdf-to-text`. Single-plugin Claude Code companion that wraps a WASM PDF-extraction engine (`glyph_api`) behind an MCP server, with a bin-script update poller invoked from a SKILL.md preamble.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` co-located with `.claude-plugin/plugin.json` at repo root. Marketplace entry sets `source: "./"` (trailing slash mandatory) — marketplace and plugin payload share the same repo root. Top-level metadata is just `name` + `owner.name`; no `metadata` wrapper, no `metadata.{description, version, pluginRoot}`. `$schema` field absent.

### Custom non-schema fields on marketplace entries

Marketplace-entry `description` and `plugin.json.description` are different strings: marketplace carries `"Extract clean text from any PDF — even the ones Chrome mangles. Claude Code companion for the PDF to Text Chrome extension."`; `plugin.json` carries the longer `"Extract clean text from any PDF — even the ones Chrome mangles. 7-level cascade resolves broken Unicode mappings locally via WASM. Returns plain text, basic markdown, or structured markdown with TOC and headings."` Two declared descriptions for the same plugin with no sync.

## Plugin source binding

### Relative source pointing to repo root (`./`)

Marketplace entry `source: "./"` resolves the plugin payload at the same path as the marketplace itself. `strict` field absent (defaults to implicit true). No `skills` override on the entry. Trailing slash present (bare `"."` would fail validation).

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Marketplace entry's only discoverability surface is `keywords: ["pdf", "extraction", "markdown", "text", "wasm"]` — no `category`, no `tags`. `plugin.json` independently carries a 6-entry `keywords` array (adds `"unicode"`). Two keyword lists for the same plugin with no sync between them — drift surface where the marketplace surface and plugin.json surface advertise different terms.

### `$schema` absence on per-plugin manifests

`$schema` field absent from both `marketplace.json` and `plugin.json`. No editor schema-completion or ahead-of-time validation; reactive detection (install errors) is the only feedback channel.

## Version coordination

### Multi-site sprawl (5+ locations)

Version `0.1.0` appears in five locations: `plugin.json`, `marketplace.json` entry, top-level `VERSION` file, sub-package `mcp-server/package.json`, and a hardcoded `version: "0.1.0"` literal in `mcp-server/src/index.ts`. No bump script, no sync mechanism, no CI gate, no pre-commit hook — every location is hand-edited per release. The `plugin.json.repository` field points to `https://github.com/JordanCoin/glyph-api`, a sibling repo that returns 404 (`gh api repos/JordanCoin/glyph-api` — verified missing); manifest declares a vapor URL.

## Channel distribution

### No pinning surface

No tags exist (zero `gh api repos/JordanCoin/pdf-to-text/tags`). No release branches, no `stable-*` / `latest-*` channel manifests, no GitHub Releases on this repo. The plugin's effective version is whatever `main` HEAD currently points at; `/plugin install pdf-to-text@JordanCoin/pdf-to-text` resolves there. Consumers track HEAD with no other handle.

### Self-update advisory channel

`bin/update-check` polls `https://api.github.com/repos/JordanCoin/glyph-api/releases/latest` (a separate engine-binary repo) for engine versions, separate from the marketplace channel. The poller's target repo currently returns 404; the script's silent-on-network-error branch fires, so no update notice ever surfaces in practice. Update wiring exists in code but is bound to a non-existent endpoint.

## Tag and release lifecycle

### No tags at all

Zero tags on the repo. No `vX.Y.Z` series, no pre-release tags, no GitHub Releases. Effective release process is commit-to-main with no version increment — every version-bearing site stays frozen at `0.1.0`. CHANGELOG.md absent.

## Plugin-component registration

### Default convention discovery

`plugin.json` declares no component paths. Claude Code auto-discovers via standard directory conventions: `skills/extract-pdf/SKILL.md`, `hooks/hooks.json` (single `SessionStart` command), `.mcp.json` at repo root (registers one stdio server `pdf-to-text`), and `bin/update-check` (mode 100755). No commands, no agents, no `.lsp.json`, no monitors, no output-styles.

### `.mcp.json` sibling file

`.mcp.json` at repo root registers a single stdio MCP server `pdf-to-text`. Server entry invokes `node ${CLAUDE_PLUGIN_ROOT}/mcp-server/dist/index.js`. Build-target directory `mcp-server/dist/` is gitignored and no hook builds it; consumed at startup by name without the plugin shipping a precompiled artifact.

## Bin entry mechanism

### Skill-invoked update poller

`bin/update-check` (~bash, mode 100755, `#!/usr/bin/env bash` + `set -euo pipefail`) polls GitHub Releases for engine-version updates and emits one of `UPGRADE_AVAILABLE <old> <new>` / `JUST_UPGRADED <old> <new>` / nothing on stdout. Not registered in `plugin.json`'s component fields. Invoked from a `## Preamble (run first)` block embedded in `skills/extract-pdf/SKILL.md` — the agent reads the skill body, shells out per the prose instructions, parses output, and conditionally surfaces a notification. Polling cadence gated by a cache file with a TTL (`-lt 3600` and `-lt 43200` thresholds for two cache stages). Snooze sub-feature is half-implemented: read path parses a `$SNOOZE_FILE` carrying a 3-field record (`version level epoch`) and uses a `case` on level to pick escalating durations (24h → 48h → 7d), but no script in the repo writes the file. Two-phase install + notify pipeline: `install-engine.sh` writes a one-shot `just-upgraded-from` marker on engine upgrade; `update-check` reads that marker exactly once and `rm -f`s it after emission, so the upgrade notice is captured without a persistent status flag.

### `${CLAUDE_PLUGIN_DATA}` with HOME fallback

`update-check` resolves install dir as `${CLAUDE_PLUGIN_DATA:-$HOME/.config/pdf-to-text}` — two-tier env-var-first fallback. Cross-platform `stat` chain `stat -f %m || stat -c %Y || echo 0` (BSD-form, GNU-form, literal zero) — final `echo 0` produces an epoch in the deep past, making subsequent `-lt 3600` / `-lt 43200` cache-freshness comparisons always evaluate to false on systems where both stat forms fail (silent cache-disable rather than hard error). State directory holds `.version`, `just-upgraded-from`, `last-update-check`, `update-snoozed` files — sentinels shared with `install-engine.sh`.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

`bin/update-check` resolves plugin root as `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}` — env var first, script-relative fallback.

### Three-tier with hardcoded data-dir terminal fallback

`skills/extract-pdf/SKILL.md` preamble resolves `_PLUGIN_DIR` as `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd || echo "$HOME/.config/pdf-to-text")}` — env var, script-relative dirname, hardcoded user-config path. Last tier is the data dir, not a plugin code dir, semantically wrong for code that needs to read SKILL.md siblings — works only because the skill preamble's downstream invocations (`$_PLUGIN_DIR/bin/update-check`, `$_PLUGIN_DIR/hooks/install-engine.sh`) wrap their bodies in `2>/dev/null || true`, which swallows the resulting path errors.

## Dependency installation

### Hook-driven WASM payload

`SessionStart` hook fires `hooks/install-engine.sh` (no matcher narrowing — runs on `startup`, `clear`, `compact`). Script downloads three raw artifacts (`glyph_api_bg.wasm`, `glyph_api.js` wrapper, `markdown.js` companion) from `https://github.com/JordanCoin/glyph-api/releases/download/v${VERSION}/`, no package manager. Install dir resolves as `${CLAUDE_PLUGIN_DATA:-$HOME/.config/pdf-to-text}`. The MCP server's `wasm-extract.ts` consumes the payload via `await import(paths.js)` for the JS wrapper and `initSync({ module: new WebAssembly.Module(wasmBytes) })` for the raw `.wasm` — both files needed and downloaded atomically. No sha256 check on downloads; trust is implicit in HTTPS plus GitHub Releases. Engine repo (`JordanCoin/glyph-api`) currently 404s — fresh installs will fail with `Install failed. extract_pdf unavailable until engine is installed.` Plugin's `VERSION` file pins the engine version to download — engine release must precede plugin install success, and engine + plugin share a release cadence by construction.

## Install change detection

### Existence-plus-version-compare

`install-engine.sh` reads `${PLUGIN_DIR}/VERSION` and `${INSTALL_DIR}/.version`; exits 0 when equal. Any inequality triggers full re-download of all three artifacts. Exact-match only — no semver-range matching. Engine and plugin share `VERSION`, so engine downgrade is tied to plugin downgrade.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks/hooks.json` declares one `SessionStart` hook running `${CLAUDE_PLUGIN_ROOT}/hooks/install-engine.sh` synchronously. No matcher narrowing — fires on every SessionStart sub-event (startup, clear, compact). Cheap when versions already match (no-op exit 0); unnecessary recomputation on `clear` and `compact`.

## Install failure posture

### Implicit retry via late-write cache marker

`install-engine.sh` cleans up partial tmp files on failure (`rm -f "${WASM_FILE}.tmp" ...`); writes `${INSTALL_DIR}/.version` only on full success. Re-running `SessionStart` retries the download cleanly because no version-stamp persisted. Corrective stderr message tells user `delete ${INSTALL_DIR} and restart your session`. `set -euo pipefail` halts on any failing command. Failure signal is human-readable stderr + `exit 1` + corrective hints — no JSON `systemMessage`, no `continue: false`, no structured hook output.

## User configuration and authentication

### No userConfig, env-var only

`plugin.json` declares no `userConfig` block. Install location controlled by `CLAUDE_PLUGIN_DATA` (set by Claude Code) with hardcoded `$HOME/.config/pdf-to-text` fallback. No `${user_config.*}` substitution anywhere. No configurable surface for the user — install path is the only relevant axis and it's host-controlled.

## Session context loading

### Dependency install only (no context emission)

The single `SessionStart` hook runs `install-engine.sh`; emits nothing as `additionalContext` or `systemMessage`. The skill preamble (`bin/update-check` invocation) is the closest analogue to session-start context loading, but it runs on skill invocation, not on session load. `UPGRADE_AVAILABLE` / `JUST_UPGRADED` messages surface only when the user triggers the skill. The `just-upgraded-from` marker, written by `install-engine.sh` during `SessionStart`, sits unread until the first PDF-related skill invocation after an engine upgrade.

## SessionStart matcher scope

### Empty matcher (all sub-events)

`hooks/hooks.json` declares the SessionStart hook with no `matcher` field — fires on `startup`, `clear`, `compact`. Sub-events that could no-op (cheap version-compare exit) fire anyway.

## Tool-use enforcement

### No enforcement (observational only)

No `PreToolUse`, `PostToolUse`, `PermissionRequest`, or `PermissionDenied` hooks. Only hook is `SessionStart`. The MCP server itself wraps its top-level entry with `main().catch((err) => { console.error("Fatal:", err); process.exit(1); })` and tool executors throw typed errors (`Failed to download PDF: ${status}`, `PDF too large`, `Either 'url' or 'path' is required`) — defensive code inside the MCP server, not Claude Code hook enforcement.

## Live monitoring

### `monitors.json` absent

No `monitors.json` file. Update-notification mechanism instead lives in the skill preamble: agent shells out to `bin/update-check`, parses output, surfaces a notice. Version-floor declaration absent — README states no minimum Claude Code version.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` has no `dependencies` field. Single-plugin repo with no cross-plugin contracts. The `<plugin-name>--v<version>` tag format is not exercised — no tags exist at all.

## Testing

### No tests

No `tests/` directory, no test files, no test framework. Zero automated verification: `marketplace.json` not parsed by CI, `plugin.json` not schema-checked, `install-engine.sh` not smoke-tested, `mcp-server/src/index.ts` not compile-checked, MCP server registration not exercised. Quality assurance is manual; "release" is whatever `main` currently points at.

## CI workflow shape

### No CI

No `.github/` directory exists (`gh api repos/JordanCoin/pdf-to-text/contents/.github` returns 404). No workflows, no triggers, no matrix, no action-pinning, no caching. All quality assurance is manual.

## Marketplace validation

### No validation

No `claude plugin validate` invocation, no JSON-parse checks on `marketplace.json` or `plugin.json`, no shell-syntax checks on hook scripts, no frontmatter validation. Defects in any manifest reach consumers because no test job catches them.

## Release automation

### No release automation / manual

No `release.yml`, no tag-trigger workflow. The plugin repo cuts no releases. The expected companion repo `JordanCoin/glyph-api` (which `install-engine.sh` polls for engine artifacts) returns 404 — neither repo has a release, so the installed pipeline is wired to an endpoint that does not exist yet. Plugin code is committed but distribution infrastructure is incomplete.

## Documentation surface

### Stub README only

`README.md` at repo root, ~2.5 KB — install command, tool list, usage examples, format reference, privacy statement, license claim. Same file serves the single plugin (no per-plugin README). `CHANGELOG.md` absent. `architecture.md` absent. `CLAUDE.md` absent. README does not document the `mcp-server/` build prerequisite (`npm install && npm run build` required before the MCP server loads, since `mcp-server/dist/` is gitignored and no hook builds it). Install precondition exists but is documented nowhere — fresh installs silently fail at MCP startup.

### No CLAUDE.md

No `CLAUDE.md` at repo root or per plugin. No agent-targeted operational doc; agent context comes only from SKILL.md.

## License declaration

### Three-way disagreement

README asserts `"Plugin wrapper: MIT. Extraction engine: proprietary."` `plugin.json` declares `"license": "UNLICENSED"`. No `LICENSE` file at repo root; GitHub API returns license: null. Three sources disagreeing across README prose, manifest field, and SPDX-detectable file. GitHub UI and tooling report the repo as unlicensed regardless of the README claim.

## Community health files

### Community health files absent

`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` all absent. No `.github/` directory exists at all.

## Cross-platform discipline

### POSIX with `stat` portability fallback

`bin/update-check` uses `stat -f %m || stat -c %Y || echo 0` — BSD-form (macOS), GNU-form (Linux), literal-zero terminal fallback. Final `echo 0` is a silent cache-disable on systems where both stat forms fail (the resulting epoch is so far in the past that subsequent freshness comparisons always evaluate false). Behavior on busybox, Alpine, FreeBSD unverified.

## Cross-ecosystem distribution

### Single-ecosystem (Claude only)

Only Claude Code manifests in the tree. No `.codex-plugin/`, no `.cursor-plugin/`, no Gemini extension. Plugin manifest, hook scripts, and the MCP server scoped to Claude Code's plugin protocol.

## Native artifact distribution

### On-demand GitHub-release download

WASM payload + JS wrapper + `markdown.js` companion are downloaded from a GitHub Releases endpoint (`https://github.com/JordanCoin/glyph-api/releases/download/v${VERSION}/`) on first SessionStart. Pattern: release-as-CDN, where GitHub Releases substitutes for npm/PyPI. Cross-repo coupling — plugin's `VERSION` file pins the upstream-repo release the install script will fetch.

## Cross-role tools

### `${CLAUDE_PLUGIN_ROOT}` env var

Resolves the plugin install location for `bin/update-check` (env-var-first, script-relative fallback) and the SKILL.md preamble (env-var-first, script-relative second tier, hardcoded data dir third tier).

### `${CLAUDE_PLUGIN_DATA}`

Resolves the engine install / state directory for both `install-engine.sh` and `bin/update-check`, with `$HOME/.config/pdf-to-text` as fallback.

### `plugin.json.version`

Drives install-staleness comparison: `install-engine.sh` reads `${PLUGIN_DIR}/VERSION` (which is the same string as `plugin.json.version`) and compares to `${INSTALL_DIR}/.version`. Same string also appears in `marketplace.json` entry, top-level `VERSION` file, sub-package `mcp-server/package.json`, and a hardcoded source-code literal — five-site sprawl with no sync.

### GitHub Releases

Substrate for the on-demand WASM/JS payload distribution (`glyph-api` repo Releases endpoint) and for the engine-version polling (`bin/update-check` curls `releases/latest` from the same endpoint). Both consumers point at a repo that currently returns 404.

### bash

Hot-path runtime for `bin/update-check` and `hooks/install-engine.sh`. Both use `#!/usr/bin/env bash` + `set -euo pipefail` (or equivalent) with cross-platform `stat` fallback and POSIX `[ -f ]` existence checks. No `.cmd` / `.ps1` siblings — POSIX-only.
