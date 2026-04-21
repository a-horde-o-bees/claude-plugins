# JordanCoin/pdf-to-text

## Identification

- **URL**: https://github.com/JordanCoin/pdf-to-text
- **Stars**: 0
- **Last commit date**: 2026-04-12 (commit `a2504a2` — "Add marketplace.json for plugin discovery")
- **Default branch**: main
- **License**: none declared at API level (no LICENSE file); `plugin.json` asserts `"license": "UNLICENSED"`; README says "Plugin wrapper: MIT. Extraction engine: proprietary." — three different answers
- **Sample origin**: dep-management + bin-wrapper
- **One-line purpose**: "Extract clean text from any PDF — even the ones Chrome mangles. Claude Code companion for the PDF to Text Chrome extension." (from `plugin.json.description` / README)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, with a single plugin entry `source: "./"` pointing at the same repo root (self-referential single-plugin marketplace)
- **Marketplace-level metadata**: top-level `name` + `owner.name` only; no `metadata.{description, version, pluginRoot}` wrapper
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `keywords` only — `["pdf", "extraction", "markdown", "text", "wasm"]`. No `category`, no `tags`. (plugin.json also has `keywords` that differ slightly: adds `"unicode"`, omits nothing — so two keyword lists that drift)
- **`$schema`**: absent
- **Reserved-name collision**: no
- **Pitfalls observed**: Marketplace-entry `keywords` and plugin.json `keywords` drift — marketplace has 5, plugin.json has 6 (`"unicode"` extra). Single source of truth violated at the keyword level. Also: marketplace-entry `description` and plugin.json `description` are *different* strings (marketplace: "Extract clean text from any PDF — even the ones Chrome mangles. Claude Code companion for the PDF to Text Chrome extension." / plugin.json: "Extract clean text from any PDF — even the ones Chrome mangles. 7-level cascade resolves broken Unicode mappings locally via WASM. Returns plain text, basic markdown, or structured markdown with TOC and headings.") — marketplace entry should reference plugin.json, not duplicate.

## 2. Plugin source binding

- **Source format(s) observed**: `source: "./"` (relative) — self-reference to the repo root
- **`strict` field**: not present (defaults to implicit true)
- **`skills` override on marketplace entry**: absent
- **Version authority**: both `plugin.json` (`"version": "0.1.0"`) and marketplace entry (`"version": "0.1.0"`) — drift risk. Additionally, a third copy lives in top-level `VERSION` (`0.1.0`), and a fourth in `mcp-server/package.json` (`"version": "0.1.0"`), and a fifth hardcoded in `mcp-server/src/index.ts` (`version: "0.1.0"`). Five-way drift surface.
- **Pitfalls observed**: Version duplicated five times with no generation/sync mechanism. `plugin.json.repository` points at `https://github.com/JordanCoin/glyph-api` (a different repo) — the plugin advertises a repo URL that does not exist (verified 404 on `gh api repos/JordanCoin/glyph-api`).

## 3. Channel distribution

- **Channel mechanism**: no split — users install via `/plugin install pdf-to-text@JordanCoin/pdf-to-text` and pin to whatever `main` resolves to at install time
- **Channel-pinning artifacts**: absent (no `stable-*` / `latest-*` pattern, no release branches, no tags)
- **Pitfalls observed**: The repo ships its own update-check mechanism (`bin/update-check`) that bypasses the marketplace channel concept entirely — it polls `github.com/JordanCoin/glyph-api/releases/latest` (a separate, currently-missing repo) rather than the plugin's own marketplace entry. So "update" means "engine update," not "plugin update." The plugin code itself is effectively whatever `main` currently holds.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: none — zero tags exist
- **Release branching**: none
- **Pre-release suffixes**: n/a — no releases of any kind
- **Dev-counter scheme**: absent — all version strings are static `0.1.0` across five locations with no counter or bump mechanism
- **Pre-commit version bump**: no
- **Pitfalls observed**: The `bin/update-check` script assumes semver releases exist on a *different* repo (`JordanCoin/glyph-api`). That repo returns 404, so `curl -sf` will fail, the script's silent-on-network-error branch fires, and no update notice ever surfaces. Effectively the update pipeline is wired to an endpoint that does not exist yet.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` declares no component paths; Claude Code auto-discovers via standard directory conventions (`skills/`, `hooks/hooks.json`, `.mcp.json` at repo root)
- **Components observed**:
    - skills — yes (`skills/extract-pdf/SKILL.md`)
    - commands — no
    - agents — no
    - hooks — yes (`hooks/hooks.json` with a single `SessionStart` command)
    - `.mcp.json` — yes (at repo root, registers one stdio server `pdf-to-text`)
    - `.lsp.json` — no
    - monitors — no
    - bin — yes (`bin/update-check`, 100755)
    - output-styles — no
- **Agent frontmatter fields used**: not applicable (no agents)
- **Agent tools syntax**: not applicable
- **Pitfalls observed**: `.mcp.json` points at `${CLAUDE_PLUGIN_ROOT}/mcp-server/dist/index.js`, but `mcp-server/dist/` is listed in `.gitignore` and no built artifact is committed. No `SessionStart`-equivalent hook builds the TypeScript either — `install-engine.sh` downloads the WASM payload but never runs `tsc` on `mcp-server/src`. So the MCP server will fail to load on fresh install unless the user manually runs `npm install && npm run build` inside `mcp-server/`. README does not mention this step.

## 6. Dependency installation

- **Applicable**: yes
- **Dep manifest format**: `mcp-server/package.json` (Node, `@modelcontextprotocol/sdk ^1.12.1`, `typescript ^5.7.0`, `@types/node ^22.0.0`). No Python manifest. Additionally, runtime-downloaded WASM payload (not a package manager — raw file download from GitHub Releases).
- **Install location**: `${CLAUDE_PLUGIN_DATA}` with fallback to `$HOME/.config/pdf-to-text` (see install-engine.sh line 4). Three-level fallback in `bin/update-check` is actually two-level: `${CLAUDE_PLUGIN_DATA:-$HOME/.config/pdf-to-text}` (note: README claim of "three-level fallback" as described in the task brief is not matched by the code — the WASM install/state directory is strictly two candidates; the three-level pattern appears only in `_PLUGIN_DIR` resolution within SKILL.md's preamble: `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." ... && pwd || echo "$HOME/.config/pdf-to-text")}` — that's the three-tier chain).
- **Install script location**: `hooks/install-engine.sh` (fired by `hooks/hooks.json` `SessionStart`). Additionally `bin/update-check` (not a hook — invoked from the skill preamble).
- **Change detection**: version file stamp — compares `${PLUGIN_DIR}/VERSION` against `${INSTALL_DIR}/.version`; exits 0 when equal. No sha256/md5 verification on downloaded WASM.
- **Retry-next-session invariant**: partial tmp files are cleaned up on failure (`rm -f "${WASM_FILE}.tmp" ...`). The committed-version file `${INSTALL_DIR}/.version` is only written on full success, so re-running `SessionStart` retries the download. Corrective guidance in stderr tells user to `delete ${INSTALL_DIR} and restart your session`.
- **Failure signaling**: `set -euo pipefail` + human-readable stderr + exit 1 on download failure; success path prints to stdout `[pdf-to-text] Engine v${TARGET_VERSION} ready`. No JSON `systemMessage`, no `continue: false`, no structured hook output — human text only.
- **Runtime variant**: WASM — binary payload is `glyph_api_bg.wasm` + `glyph_api.js` wrapper + `markdown.js` companion, downloaded from `https://github.com/JordanCoin/glyph-api/releases/download/v${VERSION}/`. Consumed from Node via `WebAssembly.Module` + `initSync({ module })`.
- **Alternative approaches**: none — no `npx`/`uvx`, no PEP 723, no pointer file. The WASM files are written directly to the install dir and imported by absolute path at MCP-server startup.
- **Version-mismatch handling**: exact-match only (`INSTALLED_VERSION = TARGET_VERSION` check); any inequality triggers full re-download of all three files. No semver-range matching. Engine and plugin share `VERSION`, so engine downgrade tied to plugin downgrade.
- **Pitfalls observed**: (1) `hooks/hooks.json` runs `install-engine.sh` on every SessionStart regardless of matcher — no `matcher: "startup"` narrowing, so sub-events like `clear` / `compact` also re-run the check (cheap since it no-ops when versions match, but unnecessary). (2) WASM download targets a release URL on a repo (`JordanCoin/glyph-api`) that currently 404s — fresh installs will fail with "Install failed. extract_pdf unavailable until engine is installed." (3) The MCP server's `wasm-extract.ts` expects `glyph_api.js` to be a JS wrapper it can `await import(paths.js)`, but `initSync({ module: new WebAssembly.Module(wasmBytes) })` reads the raw `.wasm` separately — so both files are needed and downloaded atomically. (4) No sha256 check on downloads means a compromised mirror or MITM delivers arbitrary WASM. (5) No `mcp-server/dist/` build step in any hook.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes (one bin script — `bin/update-check`)
- **`bin/` files**: `bin/update-check` — polls GitHub Releases for newer engine version, writes status cache, emits `UPGRADE_AVAILABLE <old> <new>` / `JUST_UPGRADED <old> <new>` / nothing. Invoked from `skills/extract-pdf/SKILL.md` preamble, not from `hooks.json`.
- **Shebang convention**: `#!/usr/bin/env bash` with `set -euo pipefail`
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}` — env var first, script-relative fallback (two-tier). The SKILL.md preamble adds a third tier (`|| echo "$HOME/.config/pdf-to-text"`) but that is on the *skill* side, not the bin script itself.
- **Venv handling (Python)**: not applicable (bash + Node, no Python)
- **Platform support**: POSIX-ish — uses `stat -f %m` (BSD/macOS) with `|| stat -c %Y` (GNU/Linux) fallback. `date +%s`, `awk`, `grep`, `sed`, `curl` all expected. No Windows support path. No `.cmd` / `.ps1` pair.
- **Permissions**: 100755 (git tree mode blob — executable)
- **SessionStart relationship**: none direct — `SessionStart` runs `install-engine.sh` (separate script). `bin/update-check` runs from the skill preamble, a different invocation point. They share the `CLAUDE_PLUGIN_DATA`/`$HOME/.config/pdf-to-text` state directory: `install-engine.sh` writes `${INSTALL_DIR}/.version` and `${INSTALL_DIR}/just-upgraded-from`; `update-check` reads both and also writes `last-update-check`, `update-snoozed`.
- **Pitfalls observed**: (1) The cross-platform `stat` fallback uses `echo 0` as the final fallback, which makes `CACHE_AGE` a huge number on systems where both stat forms fail — the subsequent `-lt 3600` / `-lt 43200` comparisons would always be false, defeating the cache and hitting GitHub on every session. Not a correctness bug but a silent cache disable. (2) `update-check` references a `SNOOZE_FILE` and parses a 3-field snooze record (`version level epoch`), but no code in the repo *writes* that file — the snooze feature is half-implemented (read path exists, write path does not; presumably the agent is supposed to write it after the "ask user to snooze" dialog, but the skill doesn't prescribe that). (3) Shebang says `bash`, but `update-check`'s cache check uses `grep -q "^UP_TO_DATE"` against a string with a leading newline if the file has trailing blanks — generally robust but relies on `head -1`.

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: no `${user_config.*}` references anywhere
- **Pitfalls observed**: none — the plugin has no configurable surface. Install location is controlled exclusively by `CLAUDE_PLUGIN_DATA` (set by the Claude Code harness) with a hardcoded `$HOME/.config/pdf-to-text` fallback, not through `userConfig`.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: not applicable (no tool-use hooks)
- **Failure posture**: not applicable
- **Top-level try/catch wrapping**: not applicable
- **Pitfalls observed**: The only hook is `SessionStart`. The MCP server itself does have `main().catch((err) => { console.error("Fatal:", err); process.exit(1); })` top-level, and tool executors throw typed errors (`Failed to download PDF: ${status}`, `PDF too large`, `Either 'url' or 'path' is required`) — but that's MCP-server defensive code, not Claude Code hook enforcement.

## 10. Session context loading

- **SessionStart used for context**: no — used only for dep install (see purpose 6)
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no
- **SessionStart matcher**: none (bare `hooks` array with no `matcher` field) — fires on all SessionStart sub-events (startup, clear, compact)
- **Pitfalls observed**: The skill's Preamble-run-first block is the closest analogue to session-start context loading, but it runs on *skill invocation*, not on session load. That means `UPGRADE_AVAILABLE` / `JUST_UPGRADED` messages only surface when the user triggers the skill, not proactively at session start. The `just-upgraded-from` marker, written by `install-engine.sh` during `SessionStart`, therefore sits unread until the first time the user touches a PDF-related workflow after an engine upgrade — a notification that could be stale by hours.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: absent
- **Pitfalls observed**: The update-notification pattern (check version, emit `UPGRADE_AVAILABLE`, ask user to upgrade) is implemented entirely through the skill preamble rather than through a monitor. This works for the skill's own flow but means agents not invoking `/pdf-to-text:extract-pdf` never see the notice.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin, zero tags)
- **Pitfalls observed**: none

## 13. Testing and CI

- **Test framework**: none
- **Tests location**: not applicable (no `tests/` directory, no test files)
- **Pytest config location**: not applicable
- **Python dep manifest for tests**: not applicable
- **CI present**: no (no `.github/` directory — `gh api repos/JordanCoin/pdf-to-text/contents/.github` returns 404)
- **CI file(s)**: none
- **CI triggers**: not applicable
- **CI does**: not applicable
- **Matrix**: not applicable
- **Action pinning**: not applicable
- **Caching**: not applicable
- **Test runner invocation**: not applicable
- **Pitfalls observed**: Zero automated verification. No validation that `marketplace.json` parses, no schema check on `plugin.json`, no smoke test that `install-engine.sh` succeeds, no build verification that `mcp-server/src/index.ts` compiles, no round-trip test that the MCP server registers tools and responds. The "release" process is commit-to-main with all quality assurance manual.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable — the plugin's "release" is whatever `main` points at (no tags, no GitHub Releases on this repo). The WASM engine is expected to ship releases on a *separate* repo (`JordanCoin/glyph-api`), which itself has no releases yet.
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable
- **Pitfalls observed**: The update system design (`update-check` polls `api.github.com/repos/JordanCoin/glyph-api/releases/latest`) assumes a companion repo exists and cuts semver releases. Neither condition currently holds. The plugin ships with a dangling update pipeline — code is written, infrastructure is not.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: no
- **Hooks.json validation**: no
- **Pitfalls observed**: See §13 — no automated checks on any manifest file.

## 16. Documentation

- **`README.md` at repo root**: present (2547 bytes) — install command, tool list, usage examples, format reference, privacy statement, license
- **`README.md` per plugin**: same file serves (single-plugin repo)
- **`CHANGELOG.md`**: absent
- **`architecture.md`**: absent
- **`CLAUDE.md`**: absent
- **Community health files**: none (no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`)
- **LICENSE**: absent as a file — README asserts "Plugin wrapper: MIT. Extraction engine: proprietary." but no `LICENSE` file commits the MIT text or anything else; `plugin.json` says `"UNLICENSED"`; GitHub API license field returns null
- **Badges / status indicators**: absent
- **Pitfalls observed**: License claim is asserted in prose only, without an SPDX-identifiable file — GitHub UI and tooling will report the repo as unlicensed regardless of the README claim. Three license statements across three locations all disagree (README: MIT+proprietary; plugin.json: UNLICENSED; GitHub: null). README does not document the `mcp-server/` build prerequisite (`npm install && npm run build`) that a fresh clone requires before the MCP server will load.

## 17. Novel axes

- **Self-referential single-plugin marketplace**: `source: "./"` lets one repo be both the marketplace and the plugin — user runs `/plugin install pdf-to-text@JordanCoin/pdf-to-text` which resolves the repo as a marketplace, then discovers the plugin at `./`. Not unique to this repo but a minimal-footprint pattern worth calling out.
- **WASM payload as a dep-install target**: most dep-install hooks install package-manager-managed runtimes (Python venv, Node modules). This one downloads three raw files (`.wasm` + `.js` wrapper + companion `markdown.js`) from GitHub Releases directly, no package manager. Pattern: *release-as-CDN* — GitHub Releases substituting for PyPI/npm/crates.io.
- **Cross-repo release pipeline**: plugin code and engine binaries live in different repos (this repo ships the Claude Code wrapper; `JordanCoin/glyph-api` is expected to ship engine binaries). `VERSION` in the plugin repo pins the engine version the install script will download. So plugin releases are gated by engine releases — an unusual coupling to document as a pattern variant of "plugin distributes a binary it didn't build."
- **Skill-preamble as update poller**: rather than wiring update-check into `SessionStart` or `monitors.json`, this plugin runs `bin/update-check` from a bash block embedded in the skill's SKILL.md body (`## Preamble (run first)`). The agent is instructed to shell out, read the output, and conditionally surface a notification. Novel because it embeds polling logic into documentation text that the model must parse and act on, rather than in a structured hook contract.
- **Three-tier `${CLAUDE_PLUGIN_ROOT}` fallback in skill preamble**: `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd || echo "$HOME/.config/pdf-to-text")}` — three-level resolution (env var, script-relative dirname, hardcoded user-config path). The last tier is *the data dir, not a plugin dir*, which is semantically wrong for anything that needs to read SKILL.md siblings — but works by coincidence because the skill preamble only invokes `$_PLUGIN_DIR/bin/update-check` and `$_PLUGIN_DIR/hooks/install-engine.sh`, and if those paths don't exist the `2>/dev/null || true` swallows errors. Worth flagging as a pattern that works only because failures are silent.
- **Two-phase install + notify pipeline**: `install-engine.sh` writes a one-shot `just-upgraded-from` marker file; `update-check` reads that file *exactly once* and `rm -f`s it after emission. Pattern captures "something changed since last check" without needing a persistent status flag. Clever but fragile — if the skill preamble runs and the marker is read before the user sees it, the upgrade notice is lost.
- **Snooze mechanism with escalating duration** (24h → 48h → 7d): `update-check` parses a `$SNOOZE_FILE` with `version level epoch` and uses a `case` on level to pick the duration. Read path is implemented; write path is not present in the repo. Partial feature — reading design intent, not actual functionality.

## 18. Gaps

- **`mcp-server/` build mechanism**: `.mcp.json` runs `node ${CLAUDE_PLUGIN_ROOT}/mcp-server/dist/index.js`, but `dist/` is gitignored and no hook builds it. Cannot determine from static inspection how a real install arrives at a working MCP server — possibly the author intended the marketplace to fetch a prebuilt artifact, or `install-engine.sh` is missing a `npm ci && npm run build` step, or the plugin simply doesn't work out of the box today. Would need to actually `/plugin install` it against a live Claude Code to see whether the harness auto-compiles TypeScript or whether the install silently fails. Source to resolve: run the install, or inspect any CI/release logs (none exist).
- **`glyph-api` release cadence and layout**: `install-engine.sh` expects `https://github.com/JordanCoin/glyph-api/releases/download/v${TARGET_VERSION}/glyph_api_bg.wasm` etc. That repo 404s — no evidence of what the release artifacts actually look like, whether they exist on a different name, or whether the plugin has ever successfully installed. Source to resolve: creation of the `glyph-api` repo + first release, or contacting the author.
- **Platform coverage for `bin/update-check` `stat` fallback**: the `stat -f %m || stat -c %Y || echo 0` chain is untested across FreeBSD/Alpine/busybox variants. Without a test matrix, unknown whether cache actually functions on environments other than macOS and GNU/Linux. Source to resolve: CI matrix (absent) or manual environment testing.
- **License reconciliation**: README says MIT-for-wrapper, plugin.json says UNLICENSED, no LICENSE file, GitHub reports null. Cannot determine the author's actual intent. Source to resolve: direct question or explicit `LICENSE` file.
- **Snooze write path**: `update-check` reads `$SNOOZE_FILE` but nothing in the repo writes it. Unknown whether the author intends the agent itself to write the snooze file based on user response, whether there's a planned companion script, or whether the feature was abandoned mid-implementation. Source to resolve: issue tracker (empty — `open_issues_count: 0`) or commit-message archaeology on future work.
- **Repository-field misdirection**: `plugin.json.repository: "https://github.com/JordanCoin/glyph-api"` claims a repository that does not exist. Cannot determine whether this is aspirational (planned), a stale copy from the engine repo's own plugin.json, or a mistake. Source to resolve: author confirmation or emergence of the `glyph-api` repo.
