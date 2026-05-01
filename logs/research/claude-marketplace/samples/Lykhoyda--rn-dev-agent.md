# Lykhoyda/rn-dev-agent

## Identification

- **URL**: https://github.com/Lykhoyda/rn-dev-agent
- **Stars**: 6
- **Last commit date**: 2026-04-20 (HEAD: `aa3faf2d` — "Merge pull request #46 from Lykhoyda/feat/m5-metro-events")
- **Default branch**: main
- **License**: MIT
- **Sample origin**: dep-management + bin-wrapper (observed: bin/ with 7 git-symlink wrappers; dep install into `${CLAUDE_PLUGIN_DATA}` with back-symlink into `${CLAUDE_PLUGIN_ROOT}`)
- **One-line purpose**: "AI agent that fully tests React Native features on simulator/emulator — navigates the app, verifies UI, walks user flows, and confirms internal state." (from `plugin.json.description`; README opening: "A Claude Code plugin that turns Claude into a React Native development partner")

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, alongside `plugin.json`
- **Marketplace-level metadata**: top-level `description` on the marketplace object (no `metadata.{}` wrapper); single-plugin marketplace with `owner.name` and one plugin entry
- **`metadata.pluginRoot`**: absent (single-plugin marketplace with `source: "./"` — plugin IS the repo root)
- **Per-plugin discoverability**: `category` — `"mobile-development"` (on the marketplace entry); the per-plugin `plugin.json` additionally carries `category: "development"` and `keywords: ["react-native", "expo", "testing", "debugging", "simulator", "emulator", "cdp", "maestro"]`. No `tags`. Observation: the marketplace entry's `category` ("mobile-development") and the plugin.json `category` ("development") disagree — no cross-file sync for this field
- **`$schema`**: present on marketplace.json (`https://anthropic.com/claude-code/marketplace.schema.json`); absent on plugin.json
- **Reserved-name collision**: no
- **Pitfalls observed**: `category` drift between `marketplace.json` (mobile-development) and `plugin.json` (development) — no sync script guards this, unlike `version` which is guarded by `sync-versions.sh`. Marketplace `plugins[].description` duplicates `plugin.json.description` verbatim, another hand-sync point.

## 2. Plugin source binding

- **Source format(s) observed**: relative — `source: "./"` (repo root IS the plugin)
- **`strict` field**: absent — implicit default applies
- **`skills` override on marketplace entry**: absent; skills are declared only on plugin.json
- **Version authority**: `plugin.json` is authoritative; `marketplace.json` version is mirrored from it by `scripts/sync-versions.sh` (pre-commit hook + CI check). A third version lives in `scripts/cdp-bridge/package.json` (`rn-dev-agent-cdp`) and is maintained independently (MCP server semver, currently 0.27.0 vs plugin 0.32.0)
- **Pitfalls observed**: two independent semver streams — plugin semver (0.32.0) and MCP server semver (0.27.0 in `scripts/cdp-bridge/package.json`). CHANGELOG tracks both, noting e.g. "MCP server bumped to 0.20.0". `sync-versions.sh` guards the plugin↔marketplace pair and also regex-scans `scripts/cdp-bridge/src/` for hardcoded `version: 'x.y.z'` literals (B110 regression guard) — the MCP server is required to read its version from package.json at module load, never inline.

## 3. Channel distribution

- **Channel mechanism**: no split — single marketplace on `main` with tagged releases; users pin via `@Lykhoyda-rn-dev-agent` (marketplace name). README directs `/plugin marketplace add Lykhoyda/rn-dev-agent` + `/plugin install rn-dev-agent@Lykhoyda-rn-dev-agent`
- **Channel-pinning artifacts**: absent — no stable/latest split, no dev-counter
- **Pitfalls observed**: none observed; marketplace name and plugin name are identical (`rn-dev-agent`), so the `@Lykhoyda-rn-dev-agent` suffix in install docs reads a bit tautological but is syntactically correct.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main (no release branches observed carrying tags; only feature branches `enhance/b120-screenshot-resize`, `fix/issue-40-flow-driving-fixes` plus `main`). Tags visible: `v0.25.0`, `v0.23.0`, `v0.20.0`, `v0.15.1`
- **Release branching**: none — tag-on-main. Feature work happens on short-lived `feat/*`, `fix/*`, `enhance/*` branches merged back to main
- **Pre-release suffixes**: none observed
- **Dev-counter scheme**: absent — real semver on every commit (currently 0.32.0 post-0.25.0 tag; CHANGELOG skips some intermediate versions and calls it out inline, e.g. "Skipped 0.24.0 because … jumped from 0.23.0 → 0.24.0 (PR #32) → 0.25.0 (PR #33) on main without a public release")
- **Pre-commit version bump**: no automatic bump, but a pre-commit **consistency** check runs — `.githooks/pre-commit` invokes `scripts/sync-versions.sh` whenever `plugin.json` or `marketplace.json` is in the staged diff, failing the commit on version mismatch. Version changes themselves are manual
- **Pitfalls observed**: plugin version (0.32.0) is 7 minor bumps ahead of the most recent tag (v0.25.0) — the plugin can ship via marketplace update independent of GitHub Releases. Not every on-main bump produces a release or a tag. Only 4 tags exist against ~32 plugin versions.

## 5. Plugin-component registration

- **Reference style in plugin.json**: explicit path arrays for skills/agents/commands; inline config object for `mcpServers` (single `cdp` server, not externalized to `.mcp.json`)
- **Components observed**:
    - skills: yes (7 — `using-rn-dev-agent`, `rn-feature-development`, `rn-device-control`, `rn-testing`, `rn-debugging`, `rn-best-practices`, `rn-setup`)
    - commands: yes (13)
    - agents: yes (5)
    - hooks: yes (hooks/hooks.json with 5 event types)
    - .mcp.json: no — MCP server inline in plugin.json.mcpServers
    - .lsp.json: no
    - monitors: no
    - bin: yes (7 shell wrappers, all git symlinks into ../scripts/)
    - output-styles: no
- **Agent frontmatter fields used**: `name`, `description` (multi-line with embedded `<example>` / `<commentary>` XML blocks and "Triggers:" keyword list), `tools` (per-agent list), `model` (`sonnet` / `opus`), `effort: high` (architect only), `memory: true` (tester + debugger only), `color` (green/red/yellow/magenta), `skills` (per-agent list of in-plugin skills by bare name, e.g. `rn-testing, rn-best-practices`). `user-invocable: false` is used on the `rn-best-practices` skill frontmatter
- **Agent tools syntax**: plain tool names (comma-separated — `Bash, Read, Write, Edit, Glob, Grep` or `Glob, Grep, LS, Read`). No permission-rule syntax (`Bash(uv run *)`-style) observed
- **Pitfalls observed**: agents declare `skills: rn-testing, rn-best-practices` by bare name — correct for skills in the same plugin but a future consumer from another plugin would need the qualified form. The tester + debugger descriptions contain "PARENT-SESSION-ONLY" warnings ("do NOT spawn via Task tool — MCP stdio doesn't propagate to subprocesses (GH #31)"), surfacing an MCP-inheritance gotcha as inline frontmatter guidance rather than as a schema constraint.

## 6. Dependency installation

- **Applicable**: yes
- **Dep manifest format**: `package.json` at `scripts/cdp-bridge/package.json` (Node MCP server); globally-installed npm tools (`agent-device`, `maestro-runner`) are separate external dependencies
- **Install location**: primary — `${CLAUDE_PLUGIN_DATA}/cdp-node_modules/node_modules/` with a back-symlink `${CLAUDE_PLUGIN_ROOT}/scripts/cdp-bridge/node_modules -> $CLAUDE_PLUGIN_DATA/cdp-node_modules/node_modules`. Fallback path — when `CLAUDE_PLUGIN_DATA` is unset or persistent install fails, installs directly into `${CLAUDE_PLUGIN_ROOT}/scripts/cdp-bridge/node_modules`. Global npm tools land wherever `npm install -g` puts them (e.g. `~/.maestro-runner/bin/`)
- **Install script location**: `scripts/ensure-cdp-deps.sh` (CDP bridge deps), `scripts/ensure-agent-device.sh`, `scripts/ensure-maestro-runner.sh`, `scripts/ensure-ffmpeg.sh`, `scripts/ensure-experience-engine.sh`, `scripts/ensure-android-ready.sh` — all called from `hooks/detect-rn-project.sh` (SessionStart)
- **Change detection**: **version-file stamp** — `$CLAUDE_PLUGIN_DATA/cdp-node_modules/.version-stamp` contains the CDP bridge package.json version (`CURRENT_VERSION`). Reinstall triggers when stamp absent OR stamp value ≠ current version. The stamp file is what ties `${CLAUDE_PLUGIN_DATA}` installs across plugin updates. No diff/sha/md5 checking — version-only
- **Retry-next-session invariant**: no explicit `rm` on failure; the script returns 1 and the hook swallows it with a warning. On next session, `needs_install` recomputes from stamp mismatch or missing directory. A "dangling symlink" cleanup path exists (`[ -L "$CDP_DIR/node_modules" ] && [ ! -d "$CDP_DIR/node_modules" ] && rm -f`) before falling back to local install
- **Failure signaling**: stderr human-readable with corrective command — e.g. `WARNING: CDP bridge deps failed. Run: cd ${PLUGIN_ROOT}/scripts/cdp-bridge && npm install`. Warnings are printed BEFORE the session banner ("so they're visible"). Hook exits 0 regardless (non-blocking install failure). `set -euo pipefail` is used in some ensure-* scripts (maestro-runner, agent-device) but `ensure-cdp-deps.sh` omits it to allow graceful fallback
- **Runtime variant**: Node (npm) — `node >= 22 LTS` required. `npm install --production --ignore-scripts --silent`. Two globally-installed npm CLIs (`agent-device`, `maestro-runner`) are system-level tools the hook attempts to install via `npm install -g` / `curl | bash`
- **Alternative approaches**: no `npx` / `uvx` ad-hoc, no PEP 723, no pointer file. `maestro-runner` install uses `curl -fsSL https://open.devicelab.dev/install/maestro-runner | bash` (vendor install script) as an alternative to pure npm
- **Version-mismatch handling**: MCP server version (`CURRENT_VERSION` from `scripts/cdp-bridge/package.json`) is the stamp key — any bump triggers full reinstall into the persistent dir. Plugin upgrade (different `plugin.json` version) is **separately** detected by `hooks/detect-rn-project.sh` via `$TMPDIR/rn-dev-agent-last-version`, which emits "NOTICE: rn-dev-agent upgraded from vX to vY. If MCP tools fail, restart Claude Code to reinitialize MCP servers." (B76/GH #30). Node major-version parity check also runs: odd-numbered Node (v25) warns "not an LTS release"; Node < 22 warns "below the minimum"
- **Pitfalls observed**:
    - The DATA-then-symlink pattern solves two problems at once: (a) plugin-cache resets by Claude Code wipe `${CLAUDE_PLUGIN_ROOT}/scripts/cdp-bridge/node_modules` every update, and (b) `node` at runtime still resolves modules from the expected in-tree path. Without the persistent-backing + symlink the 300+ MB node_modules would reinstall every version bump.
    - The inline comment in `ensure-cdp-deps.sh` calls out `"Skip persistent path if version is 'unknown' (node unavailable) to avoid stamp flip-flop"` — an edge case where writing the stamp when you can't verify would cause every session to re-trigger install.
    - `npm install --ignore-scripts` is deliberate (no postinstall scripts from transitive deps get to run against the user's machine).
    - Plugin upgrade detection writes to `${TMPDIR:-/tmp}/rn-dev-agent-last-version` — a per-OS tmp file, not `${CLAUDE_PLUGIN_DATA}`. It survives within a boot cycle but resets on reboot on macOS.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes
- **`bin/` files** (all git-tracked as mode 120000 symlinks pointing to `../scripts/*.sh`):
    - `rn-collect-feedback` → `../scripts/collect-feedback.sh` — sanitized env + telemetry bundle for bug reports (redacts secrets, emails, paths, bundleIds)
    - `rn-eas-artifact` → `../scripts/eas_resolve_artifact.sh` — resolve Expo EAS build artifact URLs
    - `rn-ensure-running` → `../scripts/expo_ensure_running.sh` — ensure Expo / app is running before tests
    - `rn-generate-pr-body` → `../scripts/generate_pr_body.sh` — generate PR body from proof artifacts
    - `rn-record-proof` → `../scripts/record_proof.sh` — record proof capture video/screenshots
    - `rn-snapshot` → `../scripts/snapshot_state.sh` — snapshot app state
    - `rn-verify` → `../scripts/verify.sh` — post-implementation verification harness
- **Shebang convention**: `#!/usr/bin/env bash` on the target scripts (observed on `collect-feedback.sh`). The bin/ entries themselves carry no shebangs — they are OS-level symlinks resolved by the kernel at exec time
- **Runtime resolution**: script-relative. Scripts use `PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"` — because the bin/ entry is a symlink to `../scripts/*.sh`, `$0` resolves to the real script path and `..` lands at plugin root. No `${CLAUDE_PLUGIN_ROOT}` usage in the bin wrappers themselves
- **Venv handling (Python)**: not applicable — all bash. Some scripts call `python3` inline for JSON parsing (`collect-feedback.sh` uses python3 for safe JSON escaping) but no venv management
- **Platform support**: POSIX nix-only (macOS + Linux; many paths hardcode `xcrun simctl`, `adb`, `stat -f` vs `stat -c`). Explicit `if [ "$(uname)" = "Darwin" ]` branches for macOS-specific stat syntax in hooks. No `.cmd` / `.ps1` pairs — Windows not targeted
- **Permissions**: 120000 on all 7 bin/ entries (git symlinks). Real scripts in `scripts/` are 100755 (executable) — confirmed for `collect-feedback.sh`, `eas_resolve_artifact.sh`, `ensure-agent-device.sh` etc. One exception: `scripts/snapshot_state.sh` is 100644 (not executable) while its bin/ symlink `rn-snapshot` exposes it — invoking the symlink directly may fail on systems that enforce exec bit (the script has to be run as `bash scripts/snapshot_state.sh`)
- **SessionStart relationship**: static — bin/ wrappers do not depend on SessionStart. They're user-facing convenience paths (e.g., `/rn-dev-agent:send-feedback` invokes `rn-collect-feedback` via the command markdown). SessionStart separately handles MCP deps, agent-device, maestro-runner, ffmpeg, android-ready checks via the `scripts/ensure-*.sh` family
- **Pitfalls observed**:
    - The symlink-as-bin pattern gives user-friendly `rn-*` names in `bin/` without duplicating script content. The real source of truth lives in `scripts/` where internal tooling calls them by their natural name (e.g., `hooks/detect-rn-project.sh` invokes `scripts/ensure-cdp-deps.sh` directly, not via the bin alias).
    - Git stores symlinks as mode 120000 blobs whose content is the target path — `curl raw.githubusercontent.com/.../bin/rn-collect-feedback` returns the literal string `../scripts/collect-feedback.sh` with no trailing newline, which was visible in the raw fetch.
    - `scripts/snapshot_state.sh` lacking the exec bit means `bin/rn-snapshot` as a direct exec target is broken on strict-perm setups — callers presumably invoke via `bash $(readlink bin/rn-snapshot)`. Not flagged in README.
    - Cross-platform note: Windows-native git checkouts convert symlinks to plain files containing the target path (unless `core.symlinks` is enabled), which would silently break the bin/ layer on Windows. Moot for this plugin — iOS/Android simulator tooling is nix-only anyway.

## 8. User configuration

- **`userConfig` present**: yes
- **Field count**: 3 — `RN_METRO_PORT`, `RN_PREFERRED_PLATFORM`, `RN_DEV_AGENT_LOG_LEVEL`
- **`sensitive: true` usage**: not applicable — none of the three fields carry secrets (port number, platform preference, log level)
- **Schema richness**: minimal — each field has `title`, `description`, `type: "string"`, `required: false`. No `default`, no enum, no validation. Descriptions carry the enum hints in prose ("auto, ios, or android"; "warn, info, debug, or error")
- **Reference in config substitution**: not observed in plugin.json. These are environment variables consumed by the MCP server at runtime (referenced by name in `project-config.ts` / `cdp-client.ts`, not via `${user_config.KEY}` substitution in mcpServers.args — the MCP server is invoked with only `${CLAUDE_PLUGIN_ROOT}/scripts/cdp-bridge/dist/index.js` as its arg)
- **Pitfalls observed**: userConfig keys (`RN_METRO_PORT` etc.) are declared but the substitution mechanism is implicit — Claude Code translates user config into environment variables for the MCP subprocess. No `${user_config.RN_METRO_PORT}` appears anywhere in the manifest. If a future user expected explicit substitution in the MCP args, they'd be surprised.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none
- **PostToolUse hooks**: 1 — matcher `"Edit|MultiEdit|Write"`, command `${CLAUDE_PLUGIN_ROOT}/hooks/post-edit-health-check.sh`, `timeout: 10`. Purpose: post-edit compilation/crash check on the live simulator via CDP. Last-write-wins debounce implied by comments ("only the most recent edit triggers the check"); silent-skip when no active CDP session, file type mismatch, or target file is a test/config file
- **PermissionRequest/PermissionDenied hooks**: not observed
- **Output convention**: stderr + stdout mix. Hook writes to stdout with human-readable strings ("Tool X failed. Diagnostic: Y"). Uses `jq -r '.tool_input.file_path'` to parse stdin JSON from Claude Code. No JSON output back to Claude Code — pure stdout text for the agent to read
- **Failure posture**: fail-open. Hooks comment explicitly: "`Exit codes: 0 = success (output shown to agent), 1 = error (logged, non-blocking), 2 = block operation (not used here).`" — the plugin documents that exit code 2 is available for blocking but deliberately doesn't use it
- **Top-level try/catch wrapping**: absent — bash scripts use `set -uo pipefail` (not `set -e`) and per-line `|| true` / `2>/dev/null` to suppress errors at specific sites. Each hook defines a skip-path block that exits 0 early on missing state (no CDP session, stale flag, wrong file type)
- **Pitfalls observed**:
    - There's an additional hook event — `PostToolUseFailure` with matcher `"mcp__*rn-dev-agent*"` — wired to `tool-use-failure.sh`. This is rare in the ecosystem; the hook inspects `$CDP_ACTIVE_FLAG`, Metro port, simctl boot state, adb device presence, and emits a diagnostic string tailored to the failure mode. Effectively, the plugin surfaces "here's why your MCP call just failed" to the agent after the fact.
    - `SubagentStart` hook (`subagent-start.sh`) injects CDP connection status into every subagent spawn so the subagent knows the CDP session is live. Uniquely scoped to `mcp__*rn-dev-agent*` tool namespace for PostToolUseFailure and `*` for SubagentStart/CwdChanged/SessionStart/PostToolUse.
    - `CwdChanged` hook (`cwd-changed.sh`) — re-detects whether the new working directory is an RN project. Also rare in the ecosystem; most plugins don't react to cwd changes.

## 10. Session context loading

- **SessionStart used for context**: yes — `detect-rn-project.sh` emits a large heredoc banner listing all MCP tools, commands, and prerequisites when it detects an RN project. Also warns about Node.js LTS status, runs dep-install scripts, and surfaces plugin-upgrade notices. Multi-purpose: context loader AND dep installer AND version warner
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no — all context is plain stdout text (not structured JSON with `hookSpecificOutput`)
- **SessionStart matcher**: `"*"` — fires on all sub-events (startup, clear, compact). Not restricted to `startup`
- **Pitfalls observed**: the SessionStart banner is ~40 lines of prose shown to every session start/clear/compact — significant context tax. Context loads the same on `clear` and `compact` as on `startup`, which re-injects the full banner. No `/clear` optimization. In exchange, the agent always knows which CDP tools exist and when to use them vs bash. Also, the banner includes "The rn-dev-agent plugin is active with 51 MCP tools" as a literal count — a separate source of drift vs README ("53 MCP tools") and the actual `index.ts` (count discovered via `grep -c "trackedTool(" index.ts` in `collect-feedback.sh`).

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: absent
- **Pitfalls observed**: the plugin has real-time diagnostic needs (Metro state, CDP connection liveness, simulator boot state) that a monitors.json could surface, but it instead routes this through hooks (SessionStart, PostToolUseFailure) and runtime MCP tool calls (`cdp_status`). No evidence the author considered monitors.json — publish cadence of the plugin predates or overlaps with monitors as a feature; cannot tell from observation alone.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace
- **Pitfalls observed**: not applicable.

## 13. Testing and CI

- **Test framework**: `node:test` — built-in Node test runner (`node --test 'test/unit/*.test.js'`). 272 tests as of v0.25.0 per CHANGELOG, 249 at tag time
- **Tests location**: `scripts/cdp-bridge/test/unit/` and `scripts/cdp-bridge/test/integration/` (nested under the MCP server subpackage, not repo root). Fixtures under `test/fixtures/`; helpers under `test/helpers/` (`fake-cdp-server.js`, `mock-cdp-client.js`, `result-helpers.js`)
- **Pytest config location**: not applicable (Node)
- **Python dep manifest for tests**: not applicable
- **CI present**: yes
- **CI file(s)**: `.github/workflows/ci.yml` (build + test + version-sync), `.github/workflows/deploy-docs.yml` (Astro docs build + GitHub Pages deploy)
- **CI triggers**: `push: branches: [main]` and `pull_request: branches: [main]` for ci.yml; for deploy-docs.yml, additionally path-filtered (`docs-site/**`, `scripts/cdp-bridge/src/**`, `agents/*.md`, `commands/*.md`, `skills/**`, `CHANGELOG.md`, `.github/workflows/deploy-docs.yml`). No `tags: v*` trigger
- **CI does**: TypeScript build (`npm run build`), unit tests (`node --test 'test/unit/*.test.js'`), integration tests (`node --test 'test/integration/*.test.js'`), and a separate `version-sync` job running `bash scripts/sync-versions.sh`. No linter (ruff/eslint/pyright) observed in ci.yml
- **Matrix**: none — single Node 22, ubuntu-latest
- **Action pinning**: tag — `actions/checkout@v4`, `actions/setup-node@v4`, `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4`. No SHA pinning
- **Caching**: built-in setup-node cache (`cache: npm` with explicit `cache-dependency-path: scripts/cdp-bridge/package-lock.json` for ci.yml and `cache-dependency-path: docs-site/package-lock.json` for deploy-docs.yml)
- **Test runner invocation**: direct `node --test` glob, not a wrapper script. `npm test` at `scripts/cdp-bridge/` runs `npm run build && node --test 'test/unit/*.test.js'`
- **Pitfalls observed**:
    - No release workflow — tags and GitHub Releases are created manually. `ci.yml` doesn't trigger on tags.
    - `version-sync` job is a separate job from `test` (runs in parallel) — if versions are out of sync, CI fails loudly but tests still run. Pre-commit hook catches the same on the developer's machine.
    - Integration tests currently cover only CDP client lifecycle (`test/integration/cdp-client-lifecycle.test.js`) — the "272 tests" number is dominated by unit tests. Full simulator-driven E2E runs happen on the author's dev box (CHANGELOG references "iOS (iPhone 17 Pro, iOS 26.3)" benchmarks) and are not reproduced in CI.
    - `deploy-docs.yml` uses `concurrency: { group: pages, cancel-in-progress: true }` — standard GitHub Pages pattern.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — release creation is manual via `gh release create` or the GitHub Releases UI
- **Release trigger**: not applicable (no automated release workflow)
- **Automation shape**: not applicable — only 4 tags exist (v0.15.1, v0.20.0, v0.23.0, v0.25.0) against ~32 plugin versions on main, and each tag has a corresponding manually-drafted GitHub Release. Most plugin versions ship silently (marketplace pulls from main HEAD; the plugin system doesn't require a Git tag)
- **Tag-sanity gates**: not applicable — no enforcement that tag format matches `v*` or that the tagged version equals `plugin.json.version`. CI's `version-sync` job only compares `plugin.json` ↔ `marketplace.json`, not tag
- **Release creation mechanism**: `gh release create` (manual). Release notes are hand-composed in GitHub Releases UI; CHANGELOG.md is updated in the same commit cycle
- **Draft releases**: none observed (`draft: false` on all 4 releases)
- **CHANGELOG parsing**: no automation — CHANGELOG is hand-maintained in Keep a Changelog style with additional custom sections ("Verified-stale", "Multi-review", "Upgrade notes", "Validation", "Backlog state"). Release notes on GitHub Releases duplicate subset of CHANGELOG prose manually
- **Pitfalls observed**:
    - The author is clearly aware of the gap ("Skipped 0.24.0 because … jumped from 0.23.0 → 0.24.0 (PR #32) → 0.25.0 (PR #33) on main without a public release at the intermediate step") — an automation opportunity.
    - No way for users to pin an exact version via marketplace — `/plugin install rn-dev-agent@Lykhoyda-rn-dev-agent` pulls whatever main HEAD has. GitHub Releases with tags exist but aren't consumed by the plugin system.
    - CHANGELOG format mixes Keep a Changelog (`## [0.25.0] — date`, `### Added`/`### Fixed`) with author-specific sections (`### Verified-stale`, `### Multi-review`, `### Validation`, `### Backlog state`). A `release-please`-style auto-generator wouldn't handle these.

## 15. Marketplace validation

- **Validation workflow present**: no (no dedicated validation workflow — `ci.yml` covers build + test + version-sync; there's no `claude plugin validate`, bun+zod, or equivalent)
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: no — agent/skill/command frontmatter is unvalidated in CI. `sync-versions.sh` regex-guards TypeScript source for hardcoded version literals (B110 regression test) but doesn't touch frontmatter
- **Hooks.json validation**: no — the only hook validation is implicit (pre-commit runs version-sync; CI re-runs it; hook scripts are executable-bit checked by git)
- **Pitfalls observed**: plugin.json and marketplace.json are structurally hand-validated only. No JSON Schema validation step. The `$schema` reference on marketplace.json points at `https://anthropic.com/claude-code/marketplace.schema.json` but no build step fetches it.

## 16. Documentation

- **`README.md` at repo root**: present (~9 KB, substantial — install/setup table, usage walkthrough with 8-phase pipeline, MCP tool categorization, benchmarks, troubleshooting, security section, development, license)
- **Owner profile README at `github.com/Lykhoyda/Lykhoyda`**: present (~35 lines, brief landing card — Now/Building/Before structure)
- **`README.md` per plugin**: not applicable (single-plugin marketplace, plugin IS the repo)
- **`CHANGELOG.md`**: present, Keep a Changelog base format with custom sections (`### Verified-stale`, `### Multi-review`, `### Benchmarks validated live`, `### Backlog state`). Entries are long-form with ticket IDs (B111, B76, D642, GH #31)
- **`architecture.md`**: absent at repo root. Architecture content lives in `docs-site/src/content/docs/architecture.mdx` (Astro Starlight docs site published to GitHub Pages — `has_pages: true`, URL: https://lykhoyda.github.io/rn-dev-agent/)
- **`CLAUDE.md`**: present at repo root (~7 KB+ — project overview, sibling-workspace-repo pointer, quick start, development workflow, testing notes). An additional `CLAUDE-MD-TEMPLATE.md` sits alongside — presumably a user-facing template they can drop into their own RN project
- **Community health files**: none observed (no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`). Security guidance is a `## Security` section inside README.md instead
- **LICENSE**: present (MIT, "Copyright (c) 2026 Anton Lykhoyda")
- **Badges / status indicators**: absent in README (no CI-status badge, no license badge, no version badge)
- **Pitfalls observed**:
    - `docs-site/` is a full Astro Starlight site with auto-generated MDX for all MCP tools, agents, commands, skills, best-practice rules (46 files under `best-practices/rules/`). Generator scripts live at `docs-site/scripts/generate-bp-docs.mjs` and `docs-site/scripts/generate-tool-docs.mjs`. This is a first-class user-facing docs surface on par with the plugin code itself.
    - `CLAUDE-MD-TEMPLATE.md` is unusual — a template meant to be copied into the consumer's project, not the plugin repo's own CLAUDE.md. This turns the plugin into a shipped convention: "add this to YOUR RN app's CLAUDE.md to tell Claude how to use us."
    - README claims "53 MCP tools" while `hooks/detect-rn-project.sh` banner says "51 MCP tools" — hand-drift between two hard-coded counts.

## 17. Novel axes

- **DATA-backed install with symlink back to ROOT (version-stamped)** — `scripts/ensure-cdp-deps.sh` installs `node_modules` into `${CLAUDE_PLUGIN_DATA}/cdp-node_modules/node_modules` (stamped with the MCP server's package.json version), then `ln -sfn` into `${CLAUDE_PLUGIN_ROOT}/scripts/cdp-bridge/node_modules` so relative `require` resolves. Solves the "plugin cache gets wiped on update, but 300 MB of node_modules shouldn't reinstall every time" problem. Pre-scans for a dangling symlink from a previous persistent install and cleans it before falling back to local install. Stamp-flip-flop guard: skips persistent path when Node is unavailable (so `CURRENT_VERSION === "unknown"` can't be written as a stamp).
- **Git-symlink `bin/` wrappers** — 7 files committed as mode 120000 pointing to `../scripts/*.sh`. Gives user-friendly `rn-*` naming at the bin/ layer without duplicating content. Target scripts use `dirname "$0"`-based resolution, which transparently resolves through the symlink to real-file `$PLUGIN_ROOT/..`. Novel because most plugins either ship real files in `bin/` or skip bin/ entirely. Tradeoff: breaks on Windows without `core.symlinks=true`.
- **`PostToolUseFailure` hook** — fires on failures of MCP tools matching `mcp__*rn-dev-agent*`, emits a diagnostic string ("CDP session is not active. Metro is not running on port X. Try: cdp_status to reconnect.") that the agent reads as plain stdout. Seldom seen in other plugins; most use PreToolUse for validation, not post-hoc diagnostics.
- **`SubagentStart` hook** — injects "CDP bridge is connected (platform: X, port: Y)" into every subagent spawn so the subagent doesn't need to re-probe. Paired with the tester/debugger agents' "PARENT-SESSION-ONLY" warning to document which agents do vs don't work under Task-tool spawning.
- **`CwdChanged` hook** — re-runs RN-project detection when the user `cd`s to a new directory. Emits "CDP tools may not work here" when the new cwd isn't an RN project. Rare in the ecosystem.
- **Plugin-upgrade awareness tip via tmp-file stamp** — `detect-rn-project.sh` writes `$TMPDIR/rn-dev-agent-last-version`, compares next session, and emits "NOTICE: rn-dev-agent upgraded from vX to vY. If MCP tools fail, restart Claude Code to reinitialize MCP servers." Handles the MCP-subprocess-doesn't-auto-restart class of bug (B76/GH #30).
- **Version-sync pre-commit + CI double-guard** — `.githooks/pre-commit` only fires when plugin.json or marketplace.json is staged; `sync-versions.sh` both checks drift AND regex-guards against hardcoded `version:` literals in TypeScript source (B110 regression test embedded in the sync script).
- **Three independent semver streams** — (1) `plugin.json.version` (0.32.0, user-facing), (2) `marketplace.json.plugins[0].version` (synced from 1), (3) `scripts/cdp-bridge/package.json.version` (0.27.0, MCP server internal). CHANGELOG reconciles them explicitly ("MCP server bumped to 0.20.0").
- **Sibling-workspace-repo pattern** — CLAUDE.md documents that dev scaffolding (test-app, roadmap, proof artifacts) lives in a sibling repo `../rn-dev-agent-workspace/` to keep the shipped plugin repo lean. A "symlinks removed on 2026-04-16 after confusion" note records the alternative considered and rejected.
- **`user-invocable: false` on the shared best-practices skill** — makes `rn-best-practices` agent-only (invoked via `skills:` frontmatter on agents, not surfaced as a user-facing slash command).
- **Agent `effort: high` field** — observed on rn-code-architect only, alongside `model: opus`. Signals intended reasoning budget.
- **`memory: true` field on agents** — rn-tester and rn-debugger only. Experience Engine context: seed YAML files in `seed-experience/` (`common-failures.yaml`, `expo-gotchas.yaml`, `platform-quirks.yaml`, `recovery-playbook.yaml`) plus `scripts/ensure-experience-engine.sh` initialize `$HOME/.claude/rn-agent/` with telemetry + candidates directories and an `experience.md` scratchpad.
- **Astro Starlight docs site with generator scripts** — `docs-site/scripts/generate-bp-docs.mjs` auto-generates MDX from best-practice rules in `skills/rn-best-practices/references/*.md`; `generate-tool-docs.mjs` does the same for MCP tools. Published to GitHub Pages via `deploy-docs.yml`. The docs site is a secondary artifact in the same repo, triggered by path-filter.
- **Auto-install of external CLIs via vendor-curl-pipe-bash** — `ensure-maestro-runner.sh` runs `curl -fsSL https://open.devicelab.dev/install/maestro-runner | bash` as its auto-install path. A user-facing alternative (`brew install maestro`) is printed on failure. Combined with `npm install -g agent-device`, the plugin will install external globally-rooted CLIs during SessionStart, subject to `set -euo pipefail` failure semantics.
- **Inline `<example>…<commentary>` XML in agent description frontmatter** — multi-paragraph YAML literal block scalar with 3 example blocks per agent, each with `<example>` / `<commentary>` tags. The content is treated as a trigger-rich description by Claude Code's agent matcher.

## 18. Gaps

- **Did not inspect all agent bodies in full** — sampled rn-tester / rn-debugger / rn-code-architect / rn-code-explorer / rn-code-reviewer frontmatters (first ~45 lines each). Full body content, protocol steps, and tool usage patterns were not read. To resolve: fetch each agent's full markdown.
- **Did not inspect all skills** — sampled rn-best-practices SKILL.md header only. The 7 skills (`using-rn-dev-agent`, `rn-feature-development`, `rn-device-control`, `rn-testing`, `rn-debugging`, `rn-best-practices`, `rn-setup`) and their `references/` files (60+ reference markdown files under `skills/rn-best-practices/references/`) were not read. Resolve by: per-skill SKILL.md fetch.
- **Did not inspect all hooks in full** — got full text of `hooks.json`, `detect-rn-project.sh`, `cwd-changed.sh`, `subagent-start.sh`, `tool-use-failure.sh`, and ~first 50 lines of `post-edit-health-check.sh`. The full `post-edit-health-check.sh` (CDP round-trip logic, debounce implementation) was truncated. Resolve by: full raw fetch of post-edit-health-check.sh.
- **Did not inspect any commands** — 13 command markdown files (`commands/*.md`) were not read. Expected content: frontmatter + prompt templates for slash commands like `/rn-dev-agent:rn-feature-dev`, `/rn-dev-agent:debug-screen`. Resolve by: fetching each.
- **MCP server internals** — 60+ TypeScript source files under `scripts/cdp-bridge/src/` (tools, CDP client, experience engine, nav-graph, fast-runner session) are out of scope for a marketplace-pattern survey, but if tool-registration patterns (e.g. `trackedTool()` wrapper called out in `collect-feedback.sh`'s `grep -c "trackedTool(" index.ts`) matter for §5 they would require deeper source reads.
- **Fast-runner Swift package** — `scripts/fast-runner/` ships a Swift/XCTest package (`project.yml`, `Sources/FastRunnerApp/`, `Sources/FastRunnerUITests/`). Its relationship to plugin install/build lifecycle wasn't fully traced — no workflow builds it in CI, no SessionStart script references it by name. Likely built on-demand by the MCP server when device interaction requires a signed runner. Resolve by: reading `scripts/cdp-bridge/src/fast-runner-session.ts`.
- **seed-experience YAML semantics** — the 4 YAML files under `seed-experience/` (common-failures, expo-gotchas, platform-quirks, recovery-playbook) ship with the plugin and are initialized into `$HOME/.claude/rn-agent/` by `ensure-experience-engine.sh`, but the consumption path (which agent reads them, how they feed `experience.md`) wasn't traced. Resolve by: reading the rn-best-practices / rn-debugger skill instructions.
- **CLAUDE-MD-TEMPLATE.md content** — file exists at repo root; assumed purpose ("template to copy into the user's project") inferred from the name, not verified. Resolve by: fetching the file.
- **Real `scripts/cdp-bridge/src/index.ts` tool registration** — `collect-feedback.sh` greps for `trackedTool(` to count MCP tools. The wrapper's source wasn't read to verify tool registration style (decorator vs plain call vs per-tool file). Resolve by: fetching `src/index.ts`.
- **Node version in use at release time** — README states "Node.js >= 22 LTS" and the SessionStart hook warns on odd-numbered Node. Whether the v0.25.0 tag was built/tested against a specific minor (22.x.y) is not documented. CI uses literal `22` (not a range). Resolve by: `.nvmrc` presence check (not spotted in tree listing).
