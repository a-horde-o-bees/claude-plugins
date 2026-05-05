# Sample

Mirrors of `https://github.com/Chulf58/FORGE`. AI-powered development pipeline manager for Claude Code: plans, implements, reviews, and applies features through a structured agent pipeline with planning/implementation gates. MIT-licensed; 0 stars at sample time; current tip is `v0.5.1` (commit `107be55`, 2026-04-21) on the `main` branch.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root with one plugin entry (`forge`) and marketplace name `forge-tools`. The `name`s differ between marketplace and plugin (`forge-tools` vs `forge`), producing the install command `forge@forge-tools` documented in README.

### Top-level `metadata` wrapper variants

`metadata.{description, version}` wrapper — `metadata.version: "1.0.0"` and a `description` are set; no `metadata.pluginRoot`.

## Plugin source binding

### `url` self-referencing source

`{ "source": "url", "url": "https://github.com/Chulf58/FORGE.git" }` on the marketplace entry — single-plugin self-hosting (not `github` short form, not `relative`). The marketplace manifest and plugin payload ship in the same repo but the install treats it as a remote source. README confirms "Marketplace distribution is in progress — use local path for now" alongside the URL source. A locally-cloned-but-uninstalled checkout isn't usable as a marketplace source without `url` rewriting or switching to `relative`.

### `strict` field default

`strict` not present on the marketplace entry — implicit-true default. No `skills` override on the entry.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

`plugin.json` carries `keywords: ["pipeline","agents","review","planning","development","workflow"]` and `category: "productivity"`, plus name/description/version/author/repository/license. Marketplace entry doesn't independently carry these. No `tags` field on either entry.

### `$schema` absence on per-plugin manifests

`$schema` absent on both marketplace.json and plugin.json.

## Version coordination

### Dual-file version (manifest pair)

Both `plugin.json` and `marketplace.json` carry `version: "0.5.1"`, kept in sync by `scripts/bump-version.mjs` which rewrites both targets in one pass. Drift risk exists if contributors bump one and forget the other; the bump script is the enforcement mechanism. Marketplace-level `metadata.version: "1.0.0"` is *higher* than the plugin's own `version: "0.5.1"` and tracks an independent cadence.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split. Users pin via tags (`v0.3.0`, `v0.4.0`, `v0.5.0`, `v0.5.1`) or take `@main`; no stable/latest channel duality. No second marketplace manifest, no `stable-tools`/`latest-tools` naming, no dev-counter scheme.

## Tag and release lifecycle

### Tag-on-main, single branch

Default branch `main`. All four tags (`v0.3.0`, `v0.4.0`, `v0.5.0`, `v0.5.1`) resolve to commits on main. No `release/*` branches; `gh api branches` returns only `main`.

### Mixed annotated and lightweight tags

`v0.3.0` and `v0.4.0` are annotated tags; `v0.5.0` and `v0.5.1` are lightweight tag objects pointing directly to commits. Inconsistent tag mechanism over time.

## Plugin-component registration

### Default convention discovery

`plugin.json` contains only `name`, `version`, `description`, `author`, `repository`, `license`, `keywords`. No `mcpServers`, no component path arrays. Components are discovered from convention directories (`agents/`, `skills/`, `hooks/`, etc.) and the `.mcp.json` at repo root.

### Slash-command surface via skill frontmatter

`commands/forge/` directory holds only `doctor.md` + `hello.md` (a 36-byte stub) — the "real" slash-command surface lives under `skills/` with frontmatter `name: forge:init`, `name: forge:plan`, etc. A reader who expects "commands go in `commands/`" misses 21 slash commands. The `forge:` prefix in skill frontmatter does the work a commands directory usually would.

## Component composition

### Skills (universal)

23 skill subdirectories under `skills/` — one per `/forge:<name>` command.

### Commands

2 markdown files under `commands/forge/` (`doctor.md`, `hello.md`); the latter is a 36-byte stub. The substantial slash-command surface lives under `skills/` via skill frontmatter.

### Agents

31 agent files under `agents/`.

### Hooks

13 lifecycle hooks wired by `hooks/hooks.json` across 11 events: SessionStart, UserPromptSubmit, PostToolUse, Stop, PostCompact, SessionEnd, FileChanged, SubagentStart, SubagentStop, PreToolUse.

### MCP servers

`.mcp.json` at repo root declares one server `forge-pipeline` invoked via `node ${CLAUDE_PLUGIN_ROOT}/mcp/server.js`. The server is a 79 KB file declaring 24 MCP tools.

### bin

5 files under `bin/` — `forge.js`, `forge-status.js`, `forge-worktree.js`, `forge-mcp-server.cmd`, `forge-observer.cmd`.

## Skill authoring conventions

### Standard frontmatter

Skills carry `name` (with `forge:` namespacing), `description`, `argument-hint`, `allowed-tools`, `model`.

## Agent declaration conventions

### `model` + `effort` + `maxTurns` for cost control

Agents declare `name`, `description`, `model` (e.g. `claude-sonnet-4-6`), `tools` (array), `maxTurns`, `effort` (e.g. `high`, `medium`). Observed on `planner.md`, `coder.md`, `implementer.md`, `supervisor.md`. Pipeline-style cost control per agent role.

### Plain tool-name list

Agent `tools:` is a YAML list of plain tool names (`- Read / - Write / - Glob / - Grep / - Edit / - Bash`), never the `Bash(uv run *)` permission-rule syntax.

## Server runtime (MCP)

### Inline `mcpServers` definition in `plugin.json`

`.mcp.json` at repo root declares a single `forge-pipeline` MCP server invoked via `node` with `${CLAUDE_PLUGIN_ROOT}/mcp/server.js`. The server is loaded by Claude Code from the well-known `.mcp.json` path.

## Bin entry mechanism

### Node CLI launcher with `env node` shebang

`bin/forge.js` opens with `#!/usr/bin/env node`; `spawn(process.execPath, [WRAPPER, ...argv])` where `WRAPPER` resolves to `scripts/forge-wrapper-proto.mjs` via `path.resolve(__dirname, '..', 'scripts', 'forge-wrapper-proto.mjs')`. Inherits stdio; propagates child exit code/signal. Declared as the `forge` bin in root `package.json`. Secondary env-var overrides (`FORGE_CLAUDE_CMD`, `FORGE_WRAP_SPAWN`) are consulted by the wrapper at launch — a two-layer resolution: hook first, wrapper fallback. No `$CLAUDE_PLUGIN_ROOT` reference at runtime in `bin/forge.js`.

### Auto-generated Windows `.cmd` launchers with absolute paths

`hooks/mcp-deps-install.js` (a SessionStart hook) writes `bin/forge-mcp-server.cmd`, `bin/forge.cmd`, and `bin/forge-observer.cmd` each session with absolute `process.execPath` + resolved `claude` binary baked in (an optional `set FORGE_CLAUDE_CMD=<path>` line is added when `discoverClaudePath()` succeeds). Header banner: "auto-generated by hooks/mcp-deps-install.js on SessionStart. Edits will be overwritten next session." `forge-mcp-server.cmd` and `forge-observer.cmd` are committed with the author's machine paths frozen (`C:\Users\cuj\OneDrive - Nemlig.com\Skrivebord\node-v24.14.0-win-x64\node.exe` and `C:\Users\cuj\forge-plugin\mcp\server.js`); `forge.cmd` is generated and not committed. The `.cmd` launcher is for user-run invocations, not for Claude Code's MCP spawner — `.mcp.json` spawns `node ${CLAUDE_PLUGIN_ROOT}/mcp/server.js` directly.

## Dependency installation

### SessionStart Node hook with mtime-driven `npm install`

`hooks/mcp-deps-install.js` (first entry in `hooks/hooks.json`'s SessionStart array) iterates install targets `mcp/` and `packages/forge-core/` and triggers a reinstall when (a) `node_modules/` is absent, (b) `node_modules/.package-lock.json` is absent, or (c) `statSync(package.json).mtimeMs > statSync(node_modules/.package-lock.json).mtimeMs`. Comment: "Runs npm install only when node_modules is missing or package.json is newer than the lockfile." Both `mcp/node_modules/` and `packages/forge-core/node_modules/` install under the plugin root. `${CLAUDE_PLUGIN_DATA}` is used only for the runtime `forge-config.json` file (bootstrap-copied from `forge-config.default.json`), not for Node dependencies.

`mcp/package.json` declares `@modelcontextprotocol/sdk ^1.29.0` and `zod ^3.25.0` (`"type": "module"`); root `package.json` hosts the `forge` bin and test script only. The hook uses `execFileSync(process.execPath, [npmCli, ...args])` with `npmCli` resolved from `path.dirname(process.execPath) + '/node_modules/npm/bin/npm-cli.js'` rather than bare `npm` on PATH (falls back to bare `npm` when missing). `npm ci` is preferred when `package-lock.json` exists; `npm install` is the fallback.

### Layered file-based config with schema-versioned migration

`forge-config.default.json` (a 9.4 KB plugin-owned default) carries `schemaVersion: 2`. On SessionStart, `mcp-deps-install.js` compares it against the live copy at `${CLAUDE_PLUGIN_DATA}/forge-config.json`; on mismatch, it performs a field-level diff-merge (add/remove/update providers, models, agentMap) while preserving user-owned fields (`enabled`, `envVar`, user-added entries), writes a timestamped `.bak-<ISO>.json` backup before overwriting, and logs a one-line summary. Three configuration tiers: plugin-side `forge-config.default.json` (authoritative for shape) → user-side `${CLAUDE_PLUGIN_DATA}/forge-config.json` (migrated in place) → project-side `.pipeline/project.json` (init-scaffolded by `/forge:init`, holds `pipelineMode`).

## Install change detection

### Diff-based byte comparison of manifest

`mcp-deps-install.js` uses mtime — `package.json` mtime versus `node_modules/.package-lock.json` mtime. Triggers reinstall on absence or newer manifest.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks/mcp-deps-install.js` is the first entry in the SessionStart array of `hooks/hooks.json`.

## Install failure posture

### `rm` stamp on failure (retry next session)

On npm failure the hook calls `fs.rmSync(nodeModules, { recursive: true, force: true })` (best-effort) so the next session's hook run sees `node_modules` absent and re-triggers install. Comment: "best effort cleanup — next session retries".

### Multi-layer fail-open with stderr advisory

The hook prints `[forge-mcp] Failed to install <label> dependencies: <err>` to stderr but still `exitOk()`s at the end of `main()`. No `continue: false`, no exit 2, no JSON `systemMessage`. A 5-second stdin-read timer also calls `main('{}')` if the payload never arrives, so the hook is self-healing against a stalled pipe.

## User configuration and authentication

### Layered file-based config with schema-versioned migration

`plugin.json` contains no `userConfig` block. Configuration is via `forge-config.default.json` (plugin-owned default, ~9.4 KB) copied to `${CLAUDE_PLUGIN_DATA}/forge-config.json` on first SessionStart and subsequently schema-migrated by the deps-install hook (see *Dependency installation*). Project-level state is in `.pipeline/project.json` (a per-project file written by `/forge:init`). The companion `forge-config.default.json` is richly typed (providers, models with `capabilities`/`costTier`/`pricing`/`contextWindow`, `agentModelMap` with `requiredCapabilities`, `quotaTracking`, `schemaVersion`).

### Out-of-band env vars (no `userConfig`)

`forge-config.default.json` declares provider `envVar` slots (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`) with provider-level `enabled` booleans — secrets flow via env vars the user sets externally, not through a plugin-declared sensitive field. No `${user_config.KEY}` substitution observed; `${CLAUDE_PLUGIN_ROOT}` is used in `.mcp.json` and throughout `hooks/hooks.json`.

## Tool-use enforcement

### Multi-pattern PreToolUse safety stack

7 PreToolUse entries: matcher `Bash` → `bash-guard.js`, matcher `Write` → `workflow-guard.js`, matcher `Edit` → `workflow-guard.js`, matcher `Write` → `ctx-pre-tool.js`, matcher `Edit` → `ctx-pre-tool.js`, matcher `Agent` → `routing-enforcement.js`, matcher `Agent` → `gate-enforcement.js`. `bash-guard` denies shell invocations that should route through dedicated tools; `workflow-guard` gates Write/Edit against FORGE pipeline state; `routing-enforcement` and `gate-enforcement` constrain subagent dispatch based on pending gates.

### Workflow-state gate (PreToolUse `Write|Edit`)

`workflow-guard.js` (registered on both `Write` and `Edit` matchers) gates writes/edits against FORGE pipeline state; refuses tool calls when the pipeline is in an unauthorized phase.

### PreToolUse `Agent` routing/gate enforcement

`routing-enforcement.js` and `gate-enforcement.js` (both matcher `Agent`) constrain subagent dispatch based on pending Gate #1 (plan approval) and Gate #2 (implementation approval) checkpoints. The pipeline state machine's hard-enforcement layer.

### PostToolUse `*` context tracking

PostToolUse matcher `*` runs `ctx-post-tool.js` for always-on post-tool context tracking.

### PostToolUse doc-size guard + state sync

PostToolUse matcher `Write|Edit` runs `gate-sync.js` + `doc-size-guard.js`. Gate state sync and doc-size cap on writes/edits.

### Fail-closed scope and command guards (belt-and-suspenders)

`bash-guard.js` emits a `hookSpecificOutput.permissionDecision: "deny"` JSON envelope on stdout *and* a human `console.error(msg)` on stderr, then `process.exit(2)`. Commented as "belt-and-suspenders" because "exit 2 alone is silently discarded by the current runtime". `workflow-guard.js` uses the same pattern. The "exit 2 alone is silently discarded" note documents a Claude Code runtime limitation — a downstream consumer of this pattern needs *both* the JSON envelope and stderr+exit 2 to reliably deny a tool call.

## Hook handler runtime

### Node `.mjs` files invoked via `node`

All 13 hook scripts are Node JS under `hooks/`. Top-level try/catch wrapping observed: `mcp-deps-install.js` `migrateForgeConfig` has an outermost "safety net" try/catch ("never throw from a hook function"). Context hooks similarly return early on fs/parse failures.

## Hook output contract

### Stderr for human display + stdout JSON for harness

Security-sensitive hooks (`bash-guard`, `workflow-guard`) emit a `hookSpecificOutput.permissionDecision: "deny"` JSON envelope on stdout AND a human `console.error(msg)` on stderr, then `process.exit(2)` — belt-and-suspenders to defeat the runtime quirk that "exit 2 alone is silently discarded".

## Hook failure posture

### Mixed posture (fail-closed for security, fail-open for context)

Fail-closed for security-sensitive matchers (`bash-guard`, `workflow-guard`); fail-open with stderr log elsewhere (the `ctx-*` context hooks, `forge-banner`, `mcp-deps-install`). Per-hook documented reasoning.

## Session context loading

### `additionalContext` payload at SessionStart

`forge-banner.js` documents the three-generation history of its output mechanism ending at "v3 (current): stderr direct print + additionalContext for model awareness" — emits `hookSpecificOutput.additionalContext` with the same banner content the user sees on stderr.

### Conditional `additionalContext` for setup nudge

`mcp-deps-install.js` writes `hookSpecificOutput.additionalContext` JSON on stdout on successful install/config migration so Claude Code surfaces the change to the model.

### Per-prompt anti-speculation rule injection

`hooks/anti-speculation-inject.js` runs on every UserPromptSubmit, injecting the "cite a file:line from a Read/Grep done THIS turn, or say 'I don't know, checking'" rule that `CLAUDE.md` also surfaces. A hook-based mechanism for enforcing agent epistemic discipline across the whole plugin surface.

### SessionStart banner with runtime probes

Six SessionStart hooks fire unconditionally: `mcp-deps-install.js`, `ctx-session-start.js` (context-window accounting for the transcript), `forge-banner.js` (banner + additionalContext), `routing-log-clear.js`, `usage-clear-quota-flags.js`, `observer-autosplit.js`. Running six unconditional SessionStart hooks makes first-session start non-trivial: the v0.3.0 release notes document "first session may not have MCP tools" — the deps install fires on SessionStart but MCP server discovery happens in parallel, so the MCP client may connect before `npm ci` finishes on session 1.

## SessionStart matcher scope

### Empty matcher (all sub-events)

No `"matcher"` field is present on any SessionStart entry in `hooks.json`. All six SessionStart entries fire on every sub-event (`startup`, `clear`, `compact`).

## Live monitoring

### `monitors.json` absent

No `monitors.json`. FORGE uses a sidecar web dashboard (mentioned in v0.3.0 release notes; `commands/forge/dashboard`-style skill) invoked via `/forge:dashboard`, not the claude-code `monitors.json` mechanism. A separate `observer-autosplit.js` SessionStart hook wires a local auto-split terminal observer, not a plugin monitor.

## Sidecar daemon and IPC lifecycle

### Sidecar terminal observer with auto-split

`observer-autosplit.js` (SessionStart) wires a local auto-split terminal observer for the FORGE pipeline. The observer is plugin-native vocabulary ("observer", "dashboard"), not a claude-code monitor.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field on `plugin.json`. Single-plugin marketplace, self-contained.

## Testing

### Custom Node `node:test`-style runner with suffix discovery

A custom lightweight runner at `scripts/run-tests.mjs` discovers tests by convention (`hooks/*-test.js`, `mcp/*-test.mjs`, `scripts/*-test.mjs`), spawns each via `node <path>` sequentially, and inherits stdio. No Jest/Vitest/pytest/mocha. Tests are plain assertion scripts.

### Co-located test placement

Tests live next to the source files they exercise — `hooks/gate-sync-test.js`, `mcp/router-test.mjs`, `scripts/lean-risk-classify.test.mjs`. No `tests/` directory at repo root; no nested `tests/plugins/<name>/` structure. A contributor who adds a `*.test.js` file (dot, not hyphen) will have it silently skipped by the runner's suffix discovery.

## CI workflow shape

### No CI

Repo `gh api contents/.github` returns 404; no workflows directory exists. Test runner invocation is local: `npm test` → `node scripts/run-tests.mjs` (declared in root `package.json` `"scripts": { "test": "node scripts/run-tests.mjs" }`). Regressions are caught only when someone runs `npm test` locally.

## Marketplace validation

### No validation

No CI, no pre-commit hook, no `claude plugin validate` invocation. Skills and agents carry YAML frontmatter (`name`, `description`, `model`, `tools`, `maxTurns`, `effort` for agents; `name`, `description`, `argument-hint`, `allowed-tools`, `model` for skills) but no schema validator enforces shape. Validation relies entirely on Claude Code's load-time checks + manual testing. The `/forge:doctor` skill serves as an *installation* diagnostic (node-in-PATH, plugin-root, MCP launcher, deps, server connectivity, project init) but not as a *manifest* validator.

## Release automation

### No release automation / manual

No `release.yml`, no CI, no release workflow. Four releases (v0.3.0, v0.4.0, v0.5.0, v0.5.1) created manually via the GitHub web UI with hand-authored release notes. None are drafts. `scripts/bump-version.mjs` takes a semver arg and rewrites `plugin.json` + `marketplace.json`; it does not validate tag-on-main, does not compare against git state, does not check semver monotonicity. Manual release notes + manual tag creation + no sanity gates means the pattern doesn't enforce `plugin.json.version === tag name`.

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

`README.md` at repo root (~8 KB) — glass-wall metaphor, pipeline modes table, gates description, quick-start commands, install instructions, feature list. `CLAUDE.md` at repo root (~8.5 KB — "FORGE Pipeline — Runtime Instructions"; change philosophy, anti-speculation rule, pipeline types/modes tables, risk-surface definition, LEAN-lite skip rule). No `architecture.md` at root (`docs/` only has `archive/`, `context/`, `gotchas/GENERAL.md`).

### README references to docs that don't exist

README references `docs/ARCHITECTURE.md`, `docs/FORGE-OVERVIEW.md`, `docs/FORGE-REFERENCE.md` — none appear in the `docs/` listing. Either they live deeper, were removed without README update, or are aspirational. A reader clicking those links will 404.

## License declaration

### LICENSE declared in manifests, no LICENSE file

MIT declared in `plugin.json`, `marketplace.json`, and README ("## License\n\nMIT") but no `LICENSE` or `LICENSE.md` file at repo root. GitHub license API returns `null` for `license.spdx_id`. For strict legal compliance the declaration is in plugin metadata, not in a SPDX-recognised LICENSE file.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, or `.github/PULL_REQUEST_TEMPLATE.md` at repo root.

## Cross-platform discipline

### POSIX with documented platform rejection

The plugin's hook is Windows-focused (only `.cmd` variants written; no `.sh`/POSIX counterpart observed) — macOS/Linux users rely on `node` being in PATH for the MCP server. The `.cmd` regeneration pattern means a contributor inspecting the committed `forge-mcp-server.cmd` will see the author's user/path frozen at the author's machine, only "correct" for another Windows user *after* the SessionStart hook rewrites them.

## Cross-role tools

### Node + npm + npx

Pure Node plugin — Node is the runtime for hook scripts (13 `.js`/`.mjs` files), the MCP server (`mcp/server.js`), the bin entry (`bin/forge.js`), the test runner (`scripts/run-tests.mjs`), and dep management (npm with `npm-cli.js` resolution). Node 24.x specifically baked into committed `.cmd` launchers.

### `${CLAUDE_PLUGIN_ROOT}` env var

Used in `.mcp.json` (`"args": ["${CLAUDE_PLUGIN_ROOT}/mcp/server.js"]`) and throughout `hooks/hooks.json` for hook command resolution.

### `${CLAUDE_PLUGIN_DATA}`

Used for the runtime `forge-config.json` location (bootstrap-copied from `forge-config.default.json`). Not used for Node dependencies (those live under plugin root).

### `hookSpecificOutput.additionalContext`

`forge-banner.js` (SessionStart) and `mcp-deps-install.js` (on successful install/migration) both emit `hookSpecificOutput.additionalContext` to surface state into the model's context.

