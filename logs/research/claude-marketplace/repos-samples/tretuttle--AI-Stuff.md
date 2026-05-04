# tretuttle/AI-Stuff

## Identification

- **URL**: https://github.com/tretuttle/AI-Stuff
- **Stars**: 1
- **Last commit date**: 2026-04-14 (acfbd1d — `feat(recon-wrapper): frontend-agnostic HTTP/SSE API + repo .gitignore`)
- **Default branch**: `master`
- **License**: not applicable at repo root — no root `LICENSE` (GitHub API reports `license: null`); individual plugins declare `"license": "MIT"` in their `plugin.json` and `omarchy-theme/LICENSE` is an MIT file for that plugin only
- **Sample origin**: dep-management (browser-capture's Playwright+Chromium installer); repo is an aggregator marketplace containing five full plugins plus a Codex-only skill and a standalone Python side-project (`recon-wrapper/`)
- **One-line purpose**: From root README opening: "A Claude Code plugin marketplace by tretuttle" — aggregates unrelated plugins (personas, theme generator, browser-capture, project-recon, parkpal-content) under one marketplace name

## 1. Marketplace discoverability

- **Manifest layout**: two `.claude-plugin/marketplace.json` files. Root `/.claude-plugin/marketplace.json` lists all five full plugins. A secondary `persona/.claude-plugin/marketplace.json` lives inside the persona plugin and lists only `persona` with `"source": "."` — observed; inferred purpose is to make `persona/` independently usable as its own mini-marketplace if installed directly
- **Marketplace-level metadata**: top-level `name` + `owner.name` only. No `metadata.{description, version, pluginRoot}` wrapper. No top-level `description`
- **`metadata.pluginRoot`**: absent (both marketplaces)
- **Per-plugin discoverability**: mixed. Entries in the root marketplace have different field sets:
  - `omarchy-theme` — description only (no version, no keywords, no author)
  - `browser-capture` — description + version (`1.1.0`) + author + keywords (11 keywords)
  - `persona` — description only
  - `project-recon` — description + version + author + keywords (5 keywords)
  - `parkpal-content` — description + version + author + keywords (6 keywords)
  - None use `category`, `tags`, or `categories`
- **`$schema`**: absent (both marketplace.json and every plugin.json)
- **Reserved-name collision**: no — names are `ai-stuff`, `omarchy-theme`, `browser-capture`, `persona`, `project-recon`, `parkpal-content`
- **Pitfalls observed**: drift risk — the marketplace entries for `browser-capture`, `project-recon`, `parkpal-content` carry a `version` string that also lives in each plugin's `plugin.json`. Already mismatched on `persona`: nested marketplace has `"version": "1.0.0"`, plugin.json has `"1.1.1"`. Uneven metadata across siblings (some entries have keywords + version, others don't) suggests no enforced schema. Root `version` on the marketplace itself is absent

## 2. Plugin source binding

- **Source format(s) observed**: relative only. Every entry uses `"source": "./<dir>"` (or `"source": "."` in the nested persona marketplace)
- **`strict` field**: default (implicit true) — the `strict` key is not present on any entry
- **`skills` override on marketplace entry**: absent
- **Version authority**: both (drift risk). `plugin.json` holds the canonical version; marketplace entries duplicate it for the three plugins listed above. Persona demonstrates the drift already (`1.0.0` in marketplace vs `1.1.1` in plugin.json)
- **Pitfalls observed**: duplicating version across marketplace entry and plugin.json with no automation is a live desync source

## 3. Channel distribution

- **Channel mechanism**: no split. Users install via `/plugin install <name>@ai-stuff`; there's no stable/latest split, no ref-pinning convention documented, no separate channel marketplace
- **Channel-pinning artifacts**: absent
- **Pitfalls observed**: no mechanism for consumers to pin to a tested revision — every installer pulls HEAD of `master`

## 4. Version control and release cadence

- **Default branch name**: `master`
- **Tag placement**: no tags exist (`gh api repos/tretuttle/AI-Stuff/tags` returns `[]`)
- **Release branching**: none. Branches observed: `master`, `copilot/sub-pr-2`, `feat/persona-plugin`, `feat/persona-plugin-pr` — feature branches rather than release branches
- **Pre-release suffixes**: not applicable — no tags and no GitHub Releases
- **Dev-counter scheme**: absent — plugin.json versions are normal semver (`1.1.0`, `1.1.1`, `1.2.0`, `1.0.0`)
- **Pre-commit version bump**: no. Version changes appear as hand-edits inside feature commits (e.g. `chore(project-recon): bump to 1.2.0 for cache bust`)
- **Pitfalls observed**: "bump for cache bust" commit message indicates version is used as a cache-invalidation lever rather than a release coordinate. No tags means no consumer can pin to a known-good version

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery. None of the five plugin.json files declare a `components` object, `skills` path array, `commands` path array, `hooks` path, `agents` path, or `mcpServers` — every plugin relies on Claude Code's default layout discovery (`skills/`, `commands/`, `agents/`, `hooks/hooks.json`)
- **Components observed**:
  - skills: yes (browser-capture, parkpal-content × 5, persona × 3, project-recon × 1, omarchy-theme × 1, codex-session-export × 1)
  - commands: yes (browser-capture, project-recon, omarchy-theme)
  - agents: yes (browser-capture, omarchy-theme, persona × 14 + template, project-recon, codex-session-export carries an `openai.yaml` which is a Codex agent definition, not a Claude agent)
  - hooks: yes (browser-capture, omarchy-theme, persona, parkpal-content — see Pitfalls below)
  - `.mcp.json`: no
  - `.lsp.json`: no
  - monitors: no
  - bin: yes (omarchy-theme has `bin/.gitkeep` only; setup.sh populates it at first run — see §7)
  - output-styles: no
- **Agent frontmatter fields used**:
  - `capture-analyst` — `name`, `description`, `model: sonnet`, `effort: medium`, `maxTurns: 30`
  - `theme-generator` — `name`, `description`, `model: inherit`, `color: cyan`, `allowed-tools: Bash, Read, Write, Edit, WebFetch` (note comma-delimited string form, not YAML list)
  - `theprimeagen` (representative of persona plugin agents) — `name`, `description`, `tools: Read, Glob, Grep, Bash`, `disallowedTools: Write, Edit, NotebookEdit`, `memory: project`, `model: inherit`, `maxTurns: 10`
  - `project-scout` — `name`, `description`, `model: inherit`, `color: cyan`, `tools: ["Read", "Bash", "Grep", "Glob", "Write"]` (YAML list form)
- **Agent tools syntax**: plain tool names. No permission-rule syntax like `Bash(uv run *)` observed. Syntax inconsistent across the repo — comma-delimited string (`theme-generator`), bare comma list (`theprimeagen`), YAML list (`project-scout`)
- **Pitfalls observed**: parkpal-content's `hooks/` directory contains `hookify.require-schema-validation.local.md` and `hookify.warn-trivia-firewall.local.md` — frontmatter fields like `event: stop`, `event: file`, `conditions:`, `pattern:` — these are **not** Claude Code `hooks.json` format. They look like an unrelated tool ("hookify") the author uses; Claude Code will not execute them. The `.local.md` suffix and plugin layout imply the author intends them as plugin-shipped hooks but they won't fire. Separately, `persona/hooks/hooks.json` uses `SubagentStart`/`SubagentStop` event names — verify against current Claude Code supported events (not in the canonical list `PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Notification`, `Stop`, `SubagentStop`, `PreCompact`, `SessionStart`, `SessionEnd` — `SubagentStart` is not a documented event, so this hook may never fire)

## 6. Dependency installation

- **Applicable**: yes — browser-capture installs Node deps and Playwright Chromium; omarchy-theme builds/downloads native binaries; parkpal-content has a Node `validate.js` script but no install hook
- **Dep manifest format**: `package.json` (`plugins/browser-capture/scripts/package.json` with `playwright ^1.58.2`, `js-beautify ^1.15.4`, `better-sqlite3 ^11.7.0`). omarchy-theme has no manifest — it downloads/builds binaries in `scripts/setup.sh`. No `requirements.txt`, no `pyproject.toml`, no `Cargo.toml`, no `go.mod`
- **Install location**: `${CLAUDE_PLUGIN_DATA}` for browser-capture (both `node_modules` and the Chromium browser live there). `${CLAUDE_PLUGIN_ROOT}/bin/` for omarchy-theme native binaries — writes into the plugin directory itself, not the data dir
- **Install script location**: `plugins/browser-capture/scripts/install-deps.js` (Node, invoked by SessionStart). `omarchy-theme/scripts/setup.sh` (Bash, **invoked manually** — the SessionStart hook only reports missing binaries, it does not run setup)
- **Change detection**: sha256 on `package.json`. `install-deps.js` hashes bundled `scripts/package.json` vs cached `${CLAUDE_PLUGIN_DATA}/package.json` and short-circuits when they match. The marker file `${CLAUDE_PLUGIN_DATA}/.install-ok` must also exist — otherwise the hash check is bypassed. omarchy-theme uses existence-only: `[ ! -x "${BIN_DIR}/hellwal" ]`
- **Retry-next-session invariant**: browser-capture **deletes both the cached `package.json` and `.install-ok` marker on failure** so the next SessionStart re-hashes from a clean state and retries. The marker file is also deleted **before** install starts — only re-written after full success including browser launch verification. This means a half-finished install never looks complete
- **Failure signaling**: `set -euo pipefail` style in bash (omarchy-theme's `check-dependencies.sh` and `validate-theme-path.sh`). install-deps.js uses a top-level try/catch, writes human-readable `[browser-capture] …` lines to stderr, and exits non-zero on fatal failure. omarchy-theme's dependency hook emits `{"systemMessage": "…"}` JSON when binaries are missing (an advisory message, no exit-2 gate). `validate-theme-path.sh` returns `{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "…"}` and exits 2 to block writes
- **Runtime variant**: Node npm (browser-capture uses `npm install --production` then `npx playwright install chromium`). C compilation for omarchy-theme (`cc -Wall -Wextra -O3 hellwal.c …` in setup.sh) plus a tar.gz binary download for `tint`
- **Alternative approaches**: none observed — no `uv run --script`, no `uvx`, no `npx` of the primary CLI, no PEP 723
- **Version-mismatch handling**: the `.install-ok` marker JSON records `node: process.version` and `platform: process.platform` — observed; **but the hash-based `depsUpToDate()` check does not read these fields**, so a Node major version change or platform switch does **not** trigger reinstall. The fields are informational only. Inferred design intent: forensic record, not enforcement
- **Pitfalls observed**:
  - **The install-ok marker is the atomicity boundary.** `install-deps.js` removes `.install-ok` *before* starting and only writes it after `verifyBrowser()` succeeds. `depsUpToDate()` checks both marker presence AND hash equality, so a partial install (where package.json was copied but playwright crashed mid-install, or where chromium failed to launch) leaves `cachedPkg` present but `.install-ok` absent — next session's `depsUpToDate()` returns false and retries. The failure branch in the outer try/catch **also** deletes `cachedPkg` for redundant safety
  - Chromium is installed via `npx playwright install chromium` with `PLAYWRIGHT_BROWSERS_PATH=pluginData` — one-time ~170 MB download, skipped on subsequent sessions because the hash matches and the marker exists. `verifyBrowser()` actually launches a headless instance and closes it to catch broken downloads that would otherwise fail on first real capture
  - Verification failure is **non-fatal**: the code prints a warning but doesn't delete `.install-ok`... wait, re-reading: `verifyBrowser()` returning false skips the `writeFileSync(installMarker, …)` call, so the marker is **not written** on verification failure. That means next session will retry. Comment in the code confirms: "Don't write marker so next session retries"
  - The 300-second SessionStart timeout (`"timeout": 300`) is the hard ceiling. `npm install` has a 120 s internal timeout, `playwright install chromium` has a 240 s internal timeout — totaling 360 s in the worst case, exceeding the hook timeout. On a cold first-run with slow network, the hook will be killed before the internal timeouts fire
  - omarchy-theme's `check-dependencies.sh` merely reports missing binaries; the user must run `scripts/setup.sh` manually. No idempotent auto-install path
  - omarchy-theme's setup.sh builds hellwal from a **hardcoded version** (`HELLWAL_VERSION="1.0.7"`) — no update mechanism; users get whatever was pinned at commit time
  - Both install paths assume network access during setup. No offline fallback

## 7. Bin-wrapped CLI distribution

- **Applicable**: partial. omarchy-theme has `bin/.gitkeep` with binaries populated at setup time. browser-capture has no `bin/` directory — invocation is via `node "$bundled_or_source.js"` with env-var threading
- **`bin/` files**:
  - `omarchy-theme/bin/.gitkeep` — placeholder; `scripts/setup.sh` populates `bin/hellwal` and `bin/tint` at first run
  - browser-capture has no bin wrappers
- **Shebang convention**: not applicable for omarchy-theme (binaries, no shebang). browser-capture scripts use `#!/usr/bin/env node`
- **Runtime resolution**: omarchy-theme hardcodes `${PLUGIN_ROOT}/bin/hellwal` in `check-dependencies.sh`. browser-capture uses env-var threading (`NODE_PATH`, `PLAYWRIGHT_BROWSERS_PATH`, `CLAUDE_PLUGIN_DATA`) at every invocation point — SKILL.md, commands, and hooks all export the same trio
- **Venv handling (Python)**: not applicable — no Python venvs in any plugin
- **Platform support**: Linux-first. omarchy-theme's setup.sh downloads `tint_linux_x86_64.tar.gz` (hardcoded Linux/x86_64) and compiles hellwal with a plain `cc` invocation. Not applicable to Windows/macOS without manual porting
- **Permissions**: omarchy-theme shell scripts are executable (invoked directly via `${CLAUDE_PLUGIN_ROOT}/hooks/validate-theme-path.sh` without `bash` prefix). browser-capture scripts are `.js` files invoked via `node` so mode doesn't matter. Exact mode bits not inspected
- **SessionStart relationship**: omarchy-theme's SessionStart `check-dependencies.sh` **reports** but does not populate `bin/` — user must run `setup.sh` manually. browser-capture's SessionStart builds `${CLAUDE_PLUGIN_DATA}/node_modules` and the Chromium dir; a separate lazy build (`build.js`, triggered by the skill preamble, not a hook) produces `${CLAUDE_PLUGIN_DATA}/dist/capture.js`
- **Pitfalls observed**:
  - Split install responsibility in browser-capture: SessionStart hook installs `node_modules` + Chromium, but the skill preamble runs `scripts/build.js` which calls its own `ensureDeps()` and `ensureChromium()` if the bundle is missing. Two install paths for the same deps — duplicated logic (e.g. `ensureDeps()` in build.js mutates `package.json` to add esbuild, meaning the bundled `scripts/package.json` hash will no longer match the cached one after the bundle has been built, defeating the SessionStart short-circuit on the next session)
  - `build.js` writes `${PLUGIN_DATA}/package.json` with esbuild added to dependencies. Next SessionStart `fileHash(bundledPkg) === fileHash(cachedPkg)` will be false, triggering a full reinstall. Observed bug: the dep-change detection and the build-side esbuild injection are incompatible
  - omarchy-theme's missing-binary state is user-visible (a systemMessage is emitted) but non-recovering — no autonomous repair path

## 8. User configuration

- **`userConfig` present**: no (not in any plugin.json)
- **Field count**: not applicable
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable — but plugins do consume `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` heavily in hooks and commands
- **Pitfalls observed**: none — no user config surface exists, so no mis-configuration possible

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1. omarchy-theme matcher `Write|Edit` → `validate-theme-path.sh` — denies writes to `~/.config/omarchy/themes/` and `~/.local/share/omarchy/` with `permissionDecision: "deny"` + systemMessage, exit 2
- **PostToolUse hooks**: 1. browser-capture matcher `Bash` → `sanitize-output.js` — detects data URIs (`data:…;base64,…`), binary blobs (`[\x00-\x08\x0e-\x1f]{10,}`), or inline SVG blocks (>500 chars), and emits `{"additionalContext": "[browser-capture] Warning: capture output contains binary/image data. Do NOT pipe _metadata.json or captured files through stdout…"}` to warn the agent off poisoning the conversation context
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: stdout JSON for hook-specific output (`permissionDecision`, `additionalContext`, `systemMessage`); stderr for human-readable logs (`[browser-capture] …`). Mixed per hook
- **Failure posture**: mixed per-hook.
  - `validate-theme-path.sh` — fail-closed (exit 2 + permissionDecision deny)
  - `sanitize-output.js` — fail-open silent (top-level try/catch around JSON.parse swallows malformed input; stdin timeout exits 0 after 5 s)
  - `check-dependencies.sh` — fail-open with systemMessage (always exits 0 regardless of missing deps)
- **Top-level try/catch wrapping**: observed in sanitize-output.js (`try { const data = JSON.parse(input); … } catch { /* silent */ }`) and install-deps.js (outer try/catch with cleanup on failure)
- **Pitfalls observed**:
  - `validate-theme-path.sh` reads stdin with `input=$(cat)` and parses with `jq`. No timeout — a stalled stdin would hang the hook up to the PreToolUse default budget
  - The `sanitize-output.js` regex `/data:[^;]+;base64,[A-Za-z0-9+/=]{100,}/` matches on any tool output that happens to contain a long base64 blob, regardless of origin — low false-positive risk because the hook also requires `combined.includes('capture.js') || combined.includes('browser-capture')` first, but that string match is stringly-typed and would trigger on any Bash command mentioning those words
  - The sanitize hook emits `additionalContext` but doesn't gate or truncate the tool output itself — the binary data still lands in the model's view. The warning attempts to *instruct* the model to ignore it, which is a weaker guarantee than structural sanitization

## 10. Session context loading

- **SessionStart used for context**: no — only for dep install (browser-capture) and dependency reporting (omarchy-theme)
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: yes, in PostToolUse only (sanitize-output.js); not in SessionStart
- **SessionStart matcher**: browser-capture uses no matcher (fires on all SessionStart sub-events). omarchy-theme uses `"matcher": "*"` (same effective behavior, explicit wildcard)
- **Pitfalls observed**: none — SessionStart is narrowly used for setup, not context injection

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: not applicable

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: no — there are zero tags in the repo
- **Pitfalls observed**: the five plugins are functionally independent (no shared libraries across plugins, no cross-plugin skill calls) so the absence of a dependency graph is correct for this marketplace

## 13. Testing and CI

- **Test framework**: bats (Bash Automated Testing System) for browser-capture; pytest for the out-of-band `recon-wrapper/` side-project (not a plugin). No other plugin has tests
- **Tests location**: inside plugin directory — `plugins/browser-capture/tests/` contains `capture-cli.bats`, `e2e-capture.bats`, `health-check.bats`, `sanitize-output.bats`, `update-check.bats`, plus `fixtures/basic.html` and `test_helper.bash`
- **Pytest config location**: `recon-wrapper/pyproject.toml` (for the side project, not a plugin)
- **Python dep manifest for tests**: not applicable at plugin level; `recon-wrapper/pyproject.toml` for that side-project
- **CI present**: yes
- **CI file(s)**: `.github/workflows/browser-capture-tests.yml` (only CI workflow in the repo). No CI for the other four plugins
- **CI triggers**: `push` and `pull_request`, both scoped with `paths:` to `plugins/browser-capture/**` and the workflow file itself. No `tags`, no `schedule`, no `workflow_dispatch`
- **CI does**: four jobs chained by `needs:`:
  1. `syntax-check` — `node --check` on every JS file, `JSON.parse` validation of `hooks.json`, `plugin.json`, `scripts/package.json`
  2. `unit-tests` — `npm install -g bats` then runs the 4 unit bats files (not e2e-capture.bats)
  3. `e2e-tests` — installs bats, `npm install --production`, `npx playwright install chromium`, `npx playwright install-deps chromium`, runs `e2e-capture.bats` with `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` env vars wired to the workspace
  4. `build-test` — installs esbuild and runs `scripts/build.js`, verifies the output bundle exists and is larger than 1000 bytes (not a functional test of the bundle — only "was something written")
- **Matrix**: none — single `ubuntu-latest` runner, single Node version (`20`)
- **Action pinning**: tag-level (`actions/checkout@v4`, `actions/setup-node@v4`). Not SHA-pinned
- **Caching**: none. `actions/setup-node@v4` is not configured with `cache: 'npm'`
- **Test runner invocation**: `bats plugins/browser-capture/tests/<file>.bats` directly (no wrapper script)
- **Pitfalls observed**:
  - No CI coverage for omarchy-theme, persona, project-recon, parkpal-content, or codex-session-export. Breakages in those plugins would not be caught
  - The `build-test` job's only assertion is `test "$(wc -c < scripts/dist/capture.js)" -gt 1000` — a bundle can be >1000 bytes and still be structurally broken
  - `actions/setup-node@v4` without caching means every CI run re-downloads all npm deps. For the e2e job that's playwright + chromium (~300 MB) on every run
  - No manifest-validation CI (no `claude plugin validate` equivalent, no schema check against the marketplace schema), so a malformed marketplace.json could be merged

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable — no tags, no GitHub Releases, no release workflow
- **Automation shape**: not applicable
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable — no `CHANGELOG.md` anywhere in the repo
- **Pitfalls observed**: no release discipline. Plugin versions in `plugin.json` and marketplace entries are hand-bumped with commit messages like `chore(project-recon): bump to 1.2.0 for cache bust`, suggesting the bump is used to force consumer `/plugin update` to refetch rather than to mark an actual release

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: no
- **Hooks.json validation**: yes, but only JSON well-formedness via `node -e "JSON.parse(…)"` in CI `syntax-check` for browser-capture's files only. No schema conformance check
- **Pitfalls observed**: no marketplace-wide validation. The `persona/hooks/hooks.json` (with non-existent `SubagentStart` event) and the parkpal `hookify.*.local.md` files (not Claude Code hook format at all) would not be caught by any validator in this repo

## 16. Documentation

- **`README.md` at repo root**: present (~5.4 KB) — marketplace overview with per-plugin blurbs and install commands
- **`README.md` per plugin**: present for browser-capture (~7.3 KB), omarchy-theme (~5.4 KB), persona (~12.4 KB), project-recon (~5 KB), parkpal-content (~4 KB), codex-session-export (~3 KB), plus `recon-wrapper/README.md` (~3.6 KB, side project). Consistent presence
- **`CHANGELOG.md`**: absent everywhere
- **`architecture.md`**: mixed. persona has `persona/docs/ARCHITECTURE.md`. No root architecture.md. No per-plugin architecture.md elsewhere
- **`CLAUDE.md`**: per-plugin only. `persona/CLAUDE.md` (~11 KB, uses `<!-- GSD:… -->` markers suggesting a "Get-Stuff-Done" templating convention) and `parkpal-content/CLAUDE.md` (~4 KB). No root CLAUDE.md, none in the other plugins
- **Community health files**: only `omarchy-theme/LICENSE` (MIT). No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` anywhere
- **LICENSE**: absent at repo root; present only in omarchy-theme. Other plugins declare `"license": "MIT"` in plugin.json but ship no LICENSE file
- **Badges / status indicators**: observed — joke SVG badges `works-on-my-machine.svg` and `designed-in-ms-paint.svg` in root README and plugin READMEs. Persona README has extensive share-buttons (X, Reddit, HN) and an animated typing-SVG header
- **Pitfalls observed**:
  - GitHub API reports repo `license: null` because there's no root LICENSE file, making the repo legally ambiguous even though every plugin.json claims MIT
  - No `CHANGELOG.md` combined with no git tags means the only way to see what changed in a given `plugin.json` version bump is to read commit history
  - persona's CLAUDE.md contains `<!-- GSD:project-start source:PROJECT.md -->` markers — inferred third-party templating system ("GSD") that synthesizes CLAUDE.md from other source files; the source files (PROJECT.md, research/STACK.md) don't appear to be in the repo

## 17. Novel axes

- **sha256 + install-marker atomicity pattern** — browser-capture's combined use of (a) sha256 hash of `package.json` and (b) an `.install-ok` marker file with pre-delete/post-write semantics is more defensive than existence-only or hash-only checks. The marker is written **only after** `verifyBrowser()` (an actual headless Chromium launch), catching broken downloads that pure file-existence would miss. Separately the marker records `{version, hash, timestamp, node, platform}` JSON for forensics even though the platform/node fields aren't currently used for gating. Candidate pattern: "install idempotency = hash(manifest) ∧ marker(post-verify)"
- **Lazy bundle build outside the hook chain** — browser-capture separates install (SessionStart hook) from bundle (skill preamble bash block). The skill's "Preamble (run ONCE when skill is invoked)" runs `update-check.js` unconditionally, and "Setup (run ONCE before first capture)" runs `build.js`. This defers esbuild bundling to first use rather than paying it on every SessionStart. Interesting design but creates the manifest-drift bug noted in §7 pitfalls (build.js mutates package.json)
- **Remote update advisory via raw.githubusercontent** — `update-check.js` hits `https://raw.githubusercontent.com/tretuttle/AI-Stuff/master/plugins/browser-capture/.claude-plugin/plugin.json`, compares `.version`, caches in `~/.cache/browser-capture/update-check` with asymmetric TTLs (60 min for up-to-date, 720 min for available-update). Emits `UPDATE_AVAILABLE <old> <new>` as a stdout line that the skill's preamble parses and surfaces to the user. A lightweight self-update-notification channel that does not require marketplace infrastructure
- **Asymmetric cache TTL for update notifications** — subtle: once an update is known to exist, the cache keeps that signal for 12 h so the user sees it repeatedly; "up to date" is only cached for 1 h so a freshly-published release surfaces within the hour. Design choice worth naming
- **PostToolUse sanitization as context-poisoning defense** — `sanitize-output.js` scans Bash stdout+stderr for binary-leak indicators (long base64, low-ASCII clusters, inline SVG) and emits an `additionalContext` warning instructing the agent to not pipe the content further. Not a security mechanism — a conversation-hygiene mechanism. Novel posture: hook as advisor-to-model about downstream tool behavior
- **Co-located joke badges as brand** — `works-on-my-machine.svg` and `designed-in-ms-paint.svg` in `/assets/` and referenced via relative paths from every plugin's README. Marketplace-level branding through static assets
- **Nested mini-marketplace inside a plugin directory** — `persona/.claude-plugin/marketplace.json` listing only the persona plugin with `"source": "."`. Lets that plugin be installed either from the aggregator marketplace (`@ai-stuff`) or from its own directory as a standalone marketplace. Variant of the "plugin-that-is-also-its-own-marketplace" pattern
- **`hookify.*.local.md` artifacts** — parkpal-content ships two `.md` files with YAML frontmatter declaring `event:`, `conditions:`, `pattern:` in a format that isn't Claude Code hooks but looks like a separate tool. Either dead code, or a cross-tool plugin shared between Claude Code and "hookify". Worth flagging as an anti-pattern: plugin hooks that look authoritative but do not fire
- **Codex CLI co-distribution** — `codex-session-export/` is a sibling directory with its own SKILL.md and a `agents/openai.yaml` — the README explicitly says "For Codex-only skills, use the package README in this repo instead of `/plugin install`" and shows `cp -R ~/AI-Stuff/codex-session-export ~/.codex/skills/`. Novel distribution channel: the repo doubles as a Claude Code marketplace and a Codex skills bundle

## 18. Gaps

- The `.install-ok` marker schema is visible in code but I did not observe an actual `.install-ok` file's runtime JSON — couldn't verify whether the `hash` field stored there matches `fileHash(bundledPkg)` or some other source. Source that would resolve: running the hook once against a clean install
- Whether `check-dependencies.sh`'s systemMessage actually surfaces to the user in practice (SessionStart hooks writing JSON to stdout is documented but the emission format here is `echo "{...}"` without explicit `hookSpecificOutput` wrapping). Source that would resolve: test session with those binaries missing
- The full capture.js source (~22 KB) and cookie-import.js (~15 KB) were not inspected. Their exact behavior around CDP interception, `fromCache` detection, data-URI extraction, and browser-cookie-file parsing is inferred from SKILL.md and the capture-analyst agent — not verified. Source that would resolve: reading those two files directly
- Exact file modes (100755 vs 100644) of the bash hooks were not fetched via `git ls-tree -r`. Whether `validate-theme-path.sh` is actually executable or must be invoked via `bash` is assumed from `"command": "${CLAUDE_PLUGIN_ROOT}/hooks/validate-theme-path.sh"` (direct invocation implies executable). Source that would resolve: `gh api repos/tretuttle/AI-Stuff/git/trees/master?recursive=1` with mode field decoded
- Whether `persona/hooks/hooks.json`'s `SubagentStart` event fires in current Claude Code is not verified. `SubagentStop` is documented; `SubagentStart` may be undocumented or deprecated. Source that would resolve: docs-plugins-reference.md event list cross-check
- The persona nested marketplace behavior (what happens when a user adds `persona/` directly as a marketplace vs installing via `@ai-stuff`) is inferred, not tested. The `"version": "1.0.0"` in the nested marketplace vs `"1.1.1"` in plugin.json suggests this path is stale. Source that would resolve: attempted install via both paths
- omarchy-theme's `theme-finalize.md` and `theme-create.md` command contents not fetched — so the full PreToolUse-blocked workflow (develop in `~/omarchy-theme-workshop/`, publish via GitHub) is inferred from the validate-theme-path.sh error message. Source that would resolve: reading those command files
