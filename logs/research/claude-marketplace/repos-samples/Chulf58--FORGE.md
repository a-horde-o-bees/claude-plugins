# Chulf58/FORGE

## Identification

- **URL**: https://github.com/Chulf58/FORGE
- **Stars**: 0
- **Last commit date**: 2026-04-21 (commit `107be55`)
- **Default branch**: main
- **License**: MIT (declared in `plugin.json`, `marketplace.json`, and README — no SPDX via GitHub license API, no `LICENSE` file observed at repo root)
- **Sample origin**: dep-management + bin-wrapper
- **One-line purpose**: "FORGE — AI-powered development pipeline manager for Claude Code" — plans, implements, reviews, and applies features through a structured agent pipeline with planning/implementation gates (observed in `.claude-plugin/marketplace.json` and README).

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (owns one plugin, "forge")
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper — marketplace-level `version: "1.0.0"` and `description` are set; no `pluginRoot`
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `keywords` + `category` — `keywords: ["pipeline","agents","review","planning","development","workflow"]`, `category: "productivity"`; no `tags` field observed
- **`$schema`**: absent
- **Reserved-name collision**: no — plugin name `forge` and marketplace name `forge-tools` are not reserved
- **Pitfalls observed**: marketplace-level `version: "1.0.0"` is *higher* than the plugin's own `version: "0.5.1"` and they track independent cadences — a consumer who expects a single authoritative version is wrong here. The marketplace wrapper `name: "forge-tools"` is also distinct from the plugin `name: "forge"`, so the marketplace-install command is `forge@forge-tools` (README confirms).

## 2. Plugin source binding

- **Source format(s) observed**: `url` — `{ "source": "url", "url": "https://github.com/Chulf58/FORGE.git" }` (single-plugin self-hosting; not `github` short form, not `relative`)
- **`strict` field**: default (implicit true) — `strict` not present on the marketplace entry
- **`skills` override on marketplace entry**: absent
- **Version authority**: both — `plugin.json` and `marketplace.json` both carry `version: "0.5.1"`, kept in sync by `scripts/bump-version.mjs` (which writes both targets in one pass). Drift risk exists if contributors bump one and forget the other; the bump script is the enforcement mechanism.
- **Pitfalls observed**: the self-referencing `url` source means the marketplace manifest and the plugin payload ship in the same repo; a cloned-but-uninstalled local checkout isn't usable as a marketplace source without `url` rewriting or switching to `relative`. README confirms "Marketplace distribution is in progress — use local path for now" alongside the URL source.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via tags (`v0.3.0`, `v0.4.0`, `v0.5.0`, `v0.5.1`) or take `@main`; no stable/latest channel duality
- **Channel-pinning artifacts**: absent — no second marketplace manifest, no `stable-tools`/`latest-tools` naming, no dev-counter scheme
- **Pitfalls observed**: none observed — the single-channel model is internally consistent.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main — all four tags (`v0.3.0`, `v0.4.0`, `v0.5.0`, `v0.5.1`) resolve to commits on main (v0.3.0 and v0.4.0 are annotated tags; v0.5.0 and v0.5.1 are lightweight tag objects pointing directly to commits)
- **Release branching**: none (tag-on-main) — no `release/*` branches observed; `gh api branches` returns only `main`
- **Pre-release suffixes**: none observed
- **Dev-counter scheme**: absent — `plugin.json` holds real semver (`0.5.1`) directly on main, no `0.0.z` or similar dev build counter
- **Pre-commit version bump**: no — version bumps are manual via `node scripts/bump-version.mjs <semver>`, which rewrites `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` in one operation. No git hook observed.
- **Pitfalls observed**: tag-on-main with manual version bumps means a contributor can commit feature work after a tag without bumping, leaving `plugin.json` temporarily behind reality until the next release is cut. The bump script doesn't read git history, so "what version am I working toward" is implicit.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` contains only `name`, `version`, `description`, `author`, `repository`, `license`, `keywords`. No `mcpServers`, no component path arrays. Components are discovered from convention directories (`agents/`, `skills/`, `hooks/`, etc.) and the `.mcp.json` at repo root.
- **Components observed**: skills yes (23 under `skills/` — one dir per `/forge:<name>` command), commands yes (2 files under `commands/forge/` — `doctor.md`, `hello.md`), agents yes (31 files under `agents/`), hooks yes (13 lifecycle hooks wired by `hooks/hooks.json` across 11 events: SessionStart, UserPromptSubmit, PostToolUse, Stop, PostCompact, SessionEnd, FileChanged, SubagentStart, SubagentStop, PreToolUse), `.mcp.json` yes (at repo root — single server "forge-pipeline"), `.lsp.json` no, monitors no, bin yes (5 files under `bin/`), output-styles no
- **Agent frontmatter fields used**: `name`, `description`, `model` (e.g. `claude-sonnet-4-6`), `tools` (array), `maxTurns`, `effort` (e.g. `high`, `medium`). Observed on `planner.md`, `coder.md`, `implementer.md`, `supervisor.md`.
- **Agent tools syntax**: plain tool names — `tools: - Read / - Write / - Glob / - Grep / - Edit / - Bash` (YAML list), never the `Bash(uv run *)` permission-rule syntax
- **Pitfalls observed**: the `commands/forge/` directory holds only `doctor.md` + `hello.md` (a 36-byte stub) — the "real" slash-command surface lives under `skills/` with frontmatter `name: forge:init`, `name: forge:plan`, etc. So a reader who expects "commands go in `commands/`" will miss 21 slash commands. The skill-namespacing via `forge:` prefix in frontmatter is doing the work a commands directory usually would. README "21 skills" count matches `skills/` subdir count (23 visible; 2 likely overlap with commands or are sub-skills).

## 6. Dependency installation

- **Applicable**: yes
- **Dep manifest format**: `package.json` — one at repo root (hosts the `forge` bin and test script only, no runtime deps), one at `mcp/package.json` (declares `@modelcontextprotocol/sdk ^1.29.0` and `zod ^3.25.0`; `"type": "module"`), one at `packages/forge-core/package.json`
- **Install location**: `${CLAUDE_PLUGIN_ROOT}` — both `mcp/node_modules/` and `packages/forge-core/node_modules/` install under the plugin root. `$CLAUDE_PLUGIN_DATA` is used only for the runtime `forge-config.json` file (bootstrap-copied from `forge-config.default.json`), not for Node dependencies.
- **Install script location**: `hooks/mcp-deps-install.js` — a SessionStart hook (first entry in the SessionStart array of `hooks/hooks.json`)
- **Change detection**: mtime — the hook iterates install targets (`mcp/`, `packages/forge-core/`) and triggers a reinstall when either (a) `node_modules/` is absent, or (b) `node_modules/.package-lock.json` is absent, or (c) `statSync(package.json).mtimeMs > statSync(node_modules/.package-lock.json).mtimeMs`. Comment on the check reads "Runs npm install only when node_modules is missing or package.json is newer than the lockfile."
- **Retry-next-session invariant**: `rm` on failure — on npm failure the hook calls `fs.rmSync(nodeModules, { recursive: true, force: true })` (best-effort) so the next session's hook run sees `node_modules` absent and re-triggers install. Comment: "best effort cleanup — next session retries".
- **Failure signaling**: stderr human-readable + fail-open — the hook prints `[forge-mcp] Failed to install <label> dependencies: <err>` to stderr but still `exitOk()`s at the end of `main()`. No `continue: false`, no exit 2, no JSON `systemMessage`. A 5-second stdin-read timer also calls `main('{}')` if the payload never arrives, so the hook is self-healing against a stalled pipe.
- **Runtime variant**: Node npm — specifically `execFileSync(process.execPath, [npmCli, ...args])` where `npmCli` is resolved from `path.dirname(process.execPath) + '/node_modules/npm/bin/npm-cli.js'` rather than bare `npm` on PATH ("npm-cli.js not found ... falling back to bare npm" when missing). `npm ci` is preferred when `package-lock.json` exists; `npm install` is the fallback.
- **Alternative approaches**: pointer-file pattern — the hook also *writes* `.cmd` launchers (`bin/forge-mcp-server.cmd`, `bin/forge.cmd`, `bin/forge-observer.cmd`) with absolute paths to `process.execPath` baked in, so the MCP spawner and user-facing launchers don't need `node` on system PATH. Plus an optional `FORGE_CLAUDE_CMD=<path>` env line baked into `forge.cmd` when `discoverClaudePath()` succeeds. `forge-config.json` bootstrap and schema-version diff-migration (with timestamped `.bak-<ISO>.json` backup) also run in the same hook.
- **Version-mismatch handling**: none for Node ABI — the hook never compares the Node minor version of `process.execPath` against `node_modules`. It does run a `schemaVersion`-driven diff-migration of `forge-config.json` (adds/updates providers, models, agent map entries; preserves user-owned fields like `enabled`/`envVar`; writes timestamped backup before overwriting). That's a config-schema migration, not a dep/runtime-version migration.
- **Pitfalls observed**: the `.cmd` wrappers are overwritten every SessionStart (`forge-observer.cmd` header literally reads "Edits will be overwritten next session"), so any user customization there is lost. `process.execPath` is embedded as-is — if the user's Node install moves between sessions, the wrapper becomes stale until the next session regenerates it. The hook is Windows-focused (only `.cmd` variants written; no `.sh`/POSIX counterpart observed), which means macOS/Linux users rely on `node` being in PATH for the MCP server.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes
- **`bin/` files**:
    - `forge.js` — Node CLI launcher; `spawn(process.execPath, [WRAPPER, ...argv])` where `WRAPPER` resolves to `scripts/forge-wrapper-proto.mjs`; inherits stdio; propagates child exit code/signal. Declared as the `forge` bin in root `package.json`.
    - `forge-status.js` — Node CLI (~11 KB) — status reporting surface (content not inspected beyond size; same directory convention).
    - `forge-worktree.js` — Node CLI (~11 KB) — worktree management surface.
    - `forge-mcp-server.cmd` — Windows launcher for the MCP server; baked to an absolute Node path and `<plugin>/mcp/server.js`; auto-rewritten on every SessionStart by `hooks/mcp-deps-install.js`.
    - `forge-observer.cmd` — Windows launcher for `scripts/forge-observer.mjs`; same auto-generation pattern; header banner: "auto-generated by hooks/mcp-deps-install.js on SessionStart. Edits will be overwritten next session."
    - A third `.cmd` (`bin/forge.cmd`) is *generated* by the same hook at runtime but is not committed — the install hook writes it next to `bin/forge.js` so a Windows user can launch the wrapper TUI without `node` on PATH.
- **Shebang convention**: `env node` — `bin/forge.js` starts with `#!/usr/bin/env node`. The `.cmd` files open with `@echo off` (batch, no shebang). Mixed shebang + batch-header.
- **Runtime resolution**: script-relative with env-var override — `bin/forge.js` resolves `WRAPPER = path.resolve(__dirname, '..', 'scripts', 'forge-wrapper-proto.mjs')`. The `.cmd` files embed absolute paths to `process.execPath` and to the script target at hook-generation time (the hook sees them as `${pluginRoot}/mcp/server.js` etc.). Secondary env-var overrides (`FORGE_CLAUDE_CMD`, `FORGE_WRAP_SPAWN`) are consulted by the wrapper itself at launch — a two-layer resolution: hook first, wrapper fallback. No `$CLAUDE_PLUGIN_ROOT` reference at runtime in `bin/forge.js` (the hook bakes the resolved path into `.cmd` wrappers).
- **Venv handling (Python)**: not applicable (pure Node)
- **Platform support**: bash + .cmd pair — `bin/forge.js` is the Node entry (cross-platform via shebang on POSIX, invoked as `node bin/forge.js` or via `forge.cmd` on Windows); `bin/forge-mcp-server.cmd` and `bin/forge-observer.cmd` are Windows-specific launchers. No `.ps1` variants. No POSIX `.sh` wrappers observed — POSIX users presumably rely on the root `package.json` `bin` field (`forge: "bin/forge.js"`) being picked up via `npm link` or similar.
- **Permissions**: not directly inspected — the GitHub API `contents` endpoint does not return file mode; the `.js` files carry `env node` shebangs which implies they should be 0755 when checked out on POSIX, but the raw API output does not confirm. Listed as unconfirmed.
- **SessionStart relationship**: hook writes pointer file consumed by bin/ — `hooks/mcp-deps-install.js` writes the three `.cmd` launchers (`forge-mcp-server.cmd`, `forge.cmd`, `forge-observer.cmd`) each session with absolute `process.execPath` + resolved `claude` binary baked in. The `.mcp.json` then references the `.cmd` indirectly by spawning `node ${CLAUDE_PLUGIN_ROOT}/mcp/server.js` directly (the `.cmd` launcher is for user-run invocations, not for Claude Code's MCP spawner). The wrapper JS file (`bin/forge.js`) is static; only the `.cmd` pair is session-regenerated.
- **Pitfalls observed**: the .cmd regeneration pattern means a contributor inspecting the committed `forge-mcp-server.cmd` will see one user's paths (`C:\Users\cuj\OneDrive - Nemlig.com\Skrivebord\node-v24.14.0-win-x64\node.exe` and `C:\Users\cuj\forge-plugin\mcp\server.js`) frozen at the author's machine. These are *not* generic placeholders — they were committed from the author's dev environment and are only "correct" for another Windows user *after* the SessionStart hook rewrites them. `forge.cmd` is auto-generated and not committed, but `forge-mcp-server.cmd` and `forge-observer.cmd` are both committed with author-local absolute paths. This also means anyone studying the pattern sees a sample that's effectively wrong for their own machine until a session regenerates it.

## 8. User configuration

- **`userConfig` present**: no — `plugin.json` contains no `userConfig` block. Configuration is done via `forge-config.default.json` (a 9.4 KB plugin-owned default) copied to `${CLAUDE_PLUGIN_DATA}/forge-config.json` on first SessionStart and subsequently schema-migrated by the deps-install hook. Project-level state is in `.pipeline/project.json` (a per-project file written by `/forge:init`).
- **Field count**: none (no `userConfig`)
- **`sensitive: true` usage**: not applicable (no `userConfig`). However, `forge-config.default.json` declares provider `envVar` slots (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`) with provider-level `enabled` booleans — so secrets flow via env vars the user sets externally, not through a plugin-declared sensitive field.
- **Schema richness**: not applicable (no `userConfig`) — but the companion `forge-config.default.json` is richly typed (providers, models with `capabilities`/`costTier`/`pricing`/`contextWindow`, `agentModelMap` with `requiredCapabilities`, `quotaTracking`, `schemaVersion`).
- **Reference in config substitution**: not applicable — no `${user_config.KEY}` observed. `${CLAUDE_PLUGIN_ROOT}` is used in `.mcp.json` (`"args": ["${CLAUDE_PLUGIN_ROOT}/mcp/server.js"]`) and throughout `hooks/hooks.json`.
- **Pitfalls observed**: FORGE has configuration needs that a `userConfig` could surface (pipeline mode, enabled providers, model routing), but instead uses a layered file system (`forge-config.default.json` plugin-side → `${CLAUDE_PLUGIN_DATA}/forge-config.json` user-side → `.pipeline/project.json` per-project). Users won't see config-prompt dialogs at install time; the `/forge:init` skill handles project-side setup imperatively. The migration logic in `mcp-deps-install.js` is nearly as sophisticated as a userConfig schema — purpose-built to preserve `enabled`/`envVar` fields across schema bumps while updating everything else.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 6 entries — matcher `Bash` → `bash-guard.js`, matcher `Write` → `workflow-guard.js`, matcher `Edit` → `workflow-guard.js`, matcher `Write` → `ctx-pre-tool.js`, matcher `Edit` → `ctx-pre-tool.js`, matcher `Agent` → `routing-enforcement.js`, matcher `Agent` → `gate-enforcement.js`. Purposes: `bash-guard` denies shell invocations that should route through dedicated tools; `workflow-guard` gates Write/Edit against FORGE pipeline state; `routing-enforcement` and `gate-enforcement` constrain subagent dispatch based on pending gates.
- **PostToolUse hooks**: 3 entries — matcher `*` → `ctx-post-tool.js` (always-on post-tool context tracking); matcher `Write|Edit` → `gate-sync.js` + `doc-size-guard.js`. Purposes: context tracking for all tool calls; gate state sync and doc-size cap on writes/edits.
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: stderr human + stdout JSON — `bash-guard.js` emits a `hookSpecificOutput.permissionDecision: "deny"` JSON envelope on stdout *and* a human `console.error(msg)` on stderr, then `process.exit(2)`. Commented as "belt-and-suspenders" because "exit 2 alone is silently discarded by the current runtime". `workflow-guard.js` uses the same pattern.
- **Failure posture**: fail-closed for security-sensitive matchers (`bash-guard`, `workflow-guard`), fail-open with stderr log elsewhere (the `ctx-*` context hooks, `forge-banner`, `mcp-deps-install`). Mixed per-hook with documented reasoning.
- **Top-level try/catch wrapping**: observed — `mcp-deps-install.js` `migrateForgeConfig` has an outermost "safety net" try/catch ("never throw from a hook function"). Context hooks similarly return early on fs/parse failures.
- **Pitfalls observed**: the "exit 2 alone is silently discarded" note documents a genuine Claude Code runtime limitation — a downstream consumer of this pattern needs *both* the JSON envelope and stderr+exit 2 to reliably deny a tool call. A reader who picks just one form will have hooks that appear to work in tests but silently pass in production.

## 10. Session context loading

- **SessionStart used for context**: yes — `ctx-session-start.js` (context-window accounting for the transcript), `forge-banner.js` (prints banner to stderr + emits `hookSpecificOutput.additionalContext` with same banner content to the model), `routing-log-clear.js`, `usage-clear-quota-flags.js`, `observer-autosplit.js`, and `mcp-deps-install.js` (see purpose 6). Six SessionStart hooks in total, all unconditional (no matcher on any of them).
- **UserPromptSubmit for context**: yes — `anti-speculation-inject.js` and `approval-token.js` run on every UserPromptSubmit. The anti-speculation hook injects the "cite a file:line from a Read/Grep done THIS turn" rule that CLAUDE.md also surfaces.
- **`hookSpecificOutput.additionalContext` observed**: yes — `forge-banner.js` documents the three-generation history of its output mechanism ending at "v3 (current): stderr direct print + additionalContext for model awareness".
- **SessionStart matcher**: none — all six SessionStart entries fire on every sub-event (`startup`, `clear`, `compact`). No `"matcher"` field is present on any SessionStart entry in `hooks.json`.
- **Pitfalls observed**: running six unconditional SessionStart hooks — including npm install gated by mtime check, a sidecar observer auto-split, and banner rendering — makes first-session start non-trivial. The documented "first session may not have MCP tools" limitation in the v0.3.0 release notes is a direct consequence: the deps install fires on SessionStart but MCP server discovery happens in parallel, so the MCP client may connect before `npm ci` finishes on session 1.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none — FORGE uses a sidecar web dashboard (mentioned in v0.3.0 release notes; `commands/forge/dashboard`-style skill) invoked via `/forge:dashboard`, not the claude-code `monitors.json` mechanism. A separate `observer-autosplit.js` SessionStart hook wires a local auto-split terminal observer, not a plugin monitor.
- **`when` values used**: not applicable
- **Version-floor declaration**: absent — no README note on minimum Claude Code version
- **Pitfalls observed**: the observer feature is a plugin-native concept here, not a claude-code monitor — the vocabulary in the codebase ("observer", "dashboard") will not pattern-match against a template looking for `monitors.json`.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none — single-plugin marketplace, self-contained
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin)
- **Pitfalls observed**: none observed — the marketplace owns one plugin, so cross-plugin coordination doesn't arise.

## 13. Testing and CI

- **Test framework**: bash scripts / node:test-style — a custom lightweight runner at `scripts/run-tests.mjs` discovers tests by convention (`hooks/*-test.js`, `mcp/*-test.mjs`, `scripts/*-test.mjs`), spawns each via `node <path>` sequentially, and inherits stdio. No Jest/Vitest/pytest/mocha. Tests are plain assertion scripts.
- **Tests location**: inside plugin directory — co-located with the code they test (e.g. `hooks/gate-sync-test.js`, `mcp/router-test.mjs`, `scripts/lean-risk-classify.test.mjs`). No `tests/` directory at repo root; no nested `tests/plugins/<name>/` structure.
- **Pytest config location**: not applicable (Node, no Python)
- **Python dep manifest for tests**: not applicable
- **CI present**: no — repo `gh api contents/.github` returns 404, no workflows directory exists
- **CI file(s)**: none
- **CI triggers**: not applicable
- **CI does**: not applicable
- **Matrix**: not applicable
- **Action pinning**: not applicable
- **Caching**: not applicable
- **Test runner invocation**: `npm test` → `node scripts/run-tests.mjs` (declared in root `package.json` `"scripts": { "test": "node scripts/run-tests.mjs" }`)
- **Pitfalls observed**: the test convention is tight — tests live next to the source files they exercise, discovered by suffix (`-test.js` / `-test.mjs`). A contributor who adds a `*.test.js` file (dot, not hyphen) will have it silently skipped. No CI means regressions are caught only when someone runs `npm test` locally.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — no CI, no release workflow
- **Release trigger**: not applicable (no workflow)
- **Automation shape**: not applicable — releases are created manually via the GitHub web UI; four releases observed (v0.3.0, v0.4.0, v0.5.0, v0.5.1), each with hand-authored release notes in markdown. v0.3.0 and v0.4.0 are annotated tags; v0.5.0 and v0.5.1 are lightweight (direct commit refs). None are drafts.
- **Tag-sanity gates**: none automated — `scripts/bump-version.mjs` takes a semver arg and rewrites `plugin.json` + `marketplace.json`; it does not validate tag-on-main, does not compare against git state, does not check semver monotonicity.
- **Release creation mechanism**: `gh release create`-style manual (or web UI) — based on the absence of `softprops/action-gh-release` references and the varied tag object types (annotated vs lightweight)
- **Draft releases**: no — all four releases are `draft: false, prerelease: false`
- **CHANGELOG parsing**: not applicable — no `CHANGELOG.md` at repo root (`gh api contents/CHANGELOG.md` returns 404). Release notes appear to be hand-written per release; README references `docs/CHANGELOG.md` but that's inside the docs tree, not discoverable at root; the v0.3.0 release body text refers to "Full changelog: docs/CHANGELOG.md" so it may exist at that nested path (not inspected).
- **Pitfalls observed**: manual release notes + manual tag creation + no sanity gates means the pattern doesn't enforce `plugin.json.version === tag name`. In this repo the check happens to pass at v0.5.1 (current head), but nothing prevents a future tag-ahead-of-plugin.json drift.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable — no CI, no pre-commit hook, no `claude plugin validate` invocation observed
- **Trigger**: not applicable
- **Frontmatter validation**: no automated — skills and agents carry YAML frontmatter (`name`, `description`, `model`, `tools`, `maxTurns`, `effort` for agents; `name`, `description`, `argument-hint`, `allowed-tools`, `model` for skills) but no schema validator enforces shape
- **Hooks.json validation**: no automated
- **Pitfalls observed**: validation relies entirely on Claude Code's load-time checks + manual testing. The `/forge:doctor` skill serves as an *installation* diagnostic (node-in-PATH, plugin-root, MCP launcher, deps, server connectivity, project init) but not as a *manifest* validator.

## 16. Documentation

- **`README.md` at repo root**: present (~8 KB, detailed — includes glass-wall metaphor, pipeline modes table, gates description, quick-start commands, install instructions, feature list)
- **`README.md` per plugin**: not applicable — single-plugin repo
- **`CHANGELOG.md`**: absent at repo root; release notes live on GitHub Releases (four entries). README mentions `docs/CHANGELOG.md` but that path was not directly inspected.
- **`architecture.md`**: referenced in README as `docs/ARCHITECTURE.md` — but `docs/` top-level only has `archive/`, `context/`, `gotchas/` (GENERAL.md), which means `docs/ARCHITECTURE.md` is *promised in README but absent on disk at the time of inspection*. The README also references `docs/FORGE-OVERVIEW.md` and `docs/FORGE-REFERENCE.md`, neither of which is in the `docs/` listing either.
- **`CLAUDE.md`**: at repo root (~8.5 KB — "FORGE Pipeline — Runtime Instructions"; change philosophy, anti-speculation rule, pipeline types/modes tables, risk-surface definition, LEAN-lite skip rule)
- **Community health files**: none at repo root (no SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md)
- **LICENSE**: absent as a file — declared in JSON manifests and README ("## License\n\nMIT") but no `LICENSE` or `LICENSE.md` file at repo root. GitHub license API returns `null` for `license.spdx_id`.
- **Badges / status indicators**: absent — no shields.io badges in README
- **Pitfalls observed**: README references three doc files under `docs/` (`ARCHITECTURE.md`, `FORGE-OVERVIEW.md`, `FORGE-REFERENCE.md`) that do not appear in the `docs/` root listing. Either they live deeper, were removed without README update, or are aspirational. A reader clicking those links will 404. Also no `LICENSE` file despite the MIT declaration — for strict legal compliance that's a gap (the declaration is in plugin metadata, not in a SPDX-recognised LICENSE file).

## 17. Novel axes

- **Agent pipeline with human gates as first-class structure.** The plugin is not a collection of independent skills — it's a *pipeline state machine* with explicit Gate #1 (plan approval) and Gate #2 (implementation approval) checkpoints between agent waves. `hooks/gate-enforcement.js` and `hooks/gate-sync.js` hard-enforce gate transitions on Agent/Write/Edit tool calls. This is a structural idea the pattern doc doesn't currently capture: claude-code plugins that model workflow state via hooks rather than relying on skill prose to guide the agent.
- **Schema-versioned plugin config with in-place migration.** `forge-config.default.json` carries `schemaVersion: 2`. On SessionStart, `mcp-deps-install.js` compares it against the live copy at `${CLAUDE_PLUGIN_DATA}/forge-config.json`; on mismatch, it performs a field-level diff-merge (add/remove/update providers, models, agentMap) while preserving user-owned fields (`enabled`, `envVar`, user-added entries), writes a timestamped `.bak-<ISO>.json` backup before overwriting, and logs a one-line summary. This is more sophisticated than the typical "copy default if missing" bootstrap pattern.
- **Risk-surface rule in operational docs.** `CLAUDE.md` defines a "risk surface" (shell / child_process / fs writes outside .pipeline / auth / network / new MCP tools / schema changes / merge boundaries) that deterministically mandates specific reviewer agents regardless of pipeline mode. This is a user-facing policy language for dispatching security reviewers, not a hook pattern.
- **Auto-generated Windows `.cmd` launchers embedded with absolute paths.** The `bin/*.cmd` files are rewritten every SessionStart by a hook that discovers `process.execPath` and `claude` binary location and bakes them into the batch files. Includes an optional `set FORGE_CLAUDE_CMD=...` env-var line when Claude is discovered. Solves the "node not on PATH" problem on Windows without requiring users to edit files, at the cost of committed `.cmd` files containing one specific machine's paths.
- **Three-tier configuration.** Plugin-side `forge-config.default.json` (authoritative for shape) → user-side `${CLAUDE_PLUGIN_DATA}/forge-config.json` (migrated in place) → project-side `.pipeline/project.json` (init-scaffolded, holds `pipelineMode`). Each tier has distinct lifecycle semantics.
- **Co-located `-test.js` / `-test.mjs` convention with custom runner.** `scripts/run-tests.mjs` discovers tests by directory+suffix (hooks: `-test.js`, mcp/scripts: `-test.mjs`), inherits stdio, aggregates exit codes. No framework dependency. Interesting lightweight alternative to Jest for plugin test suites.
- **Anti-speculation rule injected on every UserPromptSubmit.** `hooks/anti-speculation-inject.js` enforces "cite a file:line from Read/Grep done THIS turn, or say 'I don't know, checking'" on every user prompt. A hook-based mechanism for enforcing agent epistemic discipline across a whole plugin surface, codified in `CLAUDE.md` and hooked in at runtime.

## 18. Gaps

- **Binary file permissions.** The GitHub `contents` API does not return unix mode bits, so whether `bin/forge.js`, `bin/forge-status.js`, `bin/forge-worktree.js` are actually executable (0755) on POSIX could not be confirmed. Resolution: `git ls-tree -r main bin/` on a fresh clone would surface the mode.
- **`docs/ARCHITECTURE.md` / `docs/FORGE-OVERVIEW.md` / `docs/FORGE-REFERENCE.md` existence.** README references these three paths but the top-level `docs/` listing only shows `archive/`, `context/`, `gotchas/`. Either they're under a nested subdirectory not listed here (unlikely — GitHub contents API lists immediate children), or they're referenced but absent. Resolution: `gh api repos/Chulf58/FORGE/git/trees/main?recursive=1 | jq '.tree[] | select(.path | contains("docs/"))'` would enumerate the full docs tree.
- **Actual behavior of the 13 hook scripts.** Only `mcp-deps-install.js`, `bash-guard.js`, `forge-banner.js`, `hook-utils.js`, `ctx-session-start.js`, and `workflow-guard.js` heads were read. The remaining 7 hook scripts (`ctx-post-tool`, `ctx-pre-tool`, `ctx-post-compact`, `ctx-stop`, `session-end`, `subagent-start`, `subagent-stop`, `file-changed`, `routing-enforcement`, `gate-enforcement`, `gate-sync`, `anti-speculation-inject`, `approval-token`, `observer-autosplit`, `doc-size-guard`, `routing-log-clear`, `usage-clear-quota-flags`, `apply-context-inject`) were only observed by name + line count. Their exact output conventions and matchers beyond `hooks.json` are inferred.
- **`mcp/server.js` internals.** 79 KB file declaring 24 MCP tools was not inspected beyond name. Tool schemas, error conventions, quota-tracking specifics are unknown at this depth.
- **Skill frontmatter uniformity.** Only `init`, `plan` skills and three agent files had frontmatter inspected. Whether all 23 skills and 31 agents use consistent field sets is assumed, not verified.
- **Whether `bin/forge-status.js` and `bin/forge-worktree.js` are Node CLI launchers or something else.** Sizes (~11 KB each) suggest substantive programs, not launchers — but the distinction between "launcher-shaped wrapper for another script" and "standalone CLI" wasn't resolved.
- **`CHANGELOG.md` location.** Referenced from a release body as `docs/CHANGELOG.md`, never directly fetched. Whether it's Keep-a-Changelog format, custom, or just a concatenation of release notes is unknown.
