# Sample

Mirrors of `https://github.com/thecodeartificerX/codetographer`. Single bare plugin distributed via `git clone` + `claude --plugin-dir`, mapping the user's codebase via tree-sitter plus agentic exploration and auto-injecting context into every session and subagent. Default branch `main`, 0 stars, last commit 2026-03-25 (`a3d533d`); sample origin: dep-management. README opens "Three-tier codebase navigation via tree-sitter mapping, agentic exploration, and hook-powered auto-sync."

## Marketplace manifest layout

### No marketplace manifest (plugin source repo only)

The repo carries only `.claude-plugin/plugin.json` at the root; no `marketplace.json` exists anywhere in the tree. Repo-wide `search/code` for `filename:marketplace.json` returns `total_count=0`. Installation is local-directory via `claude --plugin-dir <path>` or `git clone`. Discoverability metadata is split: `plugin.json` carries no keywords/category/tags; `package.json` carries npm `keywords` (`claude-code`, `claude-code-plugin`, `codebase-navigation`, `tree-sitter`, `pagerank`, `mcp`, `ai-coding`, `context-injection`).

## Plugin source binding

### Direct git install (no marketplace.json in source repo)

Users install via `claude --plugin-dir /path/to/codetographer` after `git clone` — no marketplace-level binding because no `marketplace.json` exists in the plugin repo. No external aggregator is documented as listing this plugin.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

`plugin.json` carries only `name`, `version`, `description`, `author`, `mcpServers`. No `keywords`, `category`, or `tags` on `plugin.json` itself. Discoverability fields are declared instead in `package.json` via the npm `keywords` array (`claude-code`, `claude-code-plugin`, `codebase-navigation`, `tree-sitter`, `pagerank`, `mcp`, `ai-coding`, `context-injection`).

### `$schema` absence on per-plugin manifests

`$schema` is absent from `plugin.json`.

## Version coordination

### Dual-file version (manifest pair)

Both `plugin.json` and `package.json` declare `version: "1.0.0"` and must be kept in sync by hand (no tooling links them). The `package.json` version is consumed only by npm tooling and the hook build script. Nothing validates that the two files stay identical across releases.

## Channel distribution

### No pinning surface

No tags, no release branches, no marketplace channel. The only pointer is whatever main HEAD happens to be at clone time. Consumers who want reproducible installs have to pin by SHA.

## Tag and release lifecycle

### No tags at all

Repo has zero tags (`/repos/.../tags` returns `[]`). All commits within ~3 hours of repo creation (2026-03-25). `plugin.json.version` is frozen at `1.0.0` declaratively — there is no tag, release, or automation enforcing it.

## Plugin-component registration

### Default convention discovery

`plugin.json` has no explicit `skills`, `agents`, `commands`, or `hooks` field — Claude Code's convention-based directory discovery finds `skills/`, `agents/`, `hooks/`.

### Inline `mcpServers` definition in `plugin.json`

`plugin.json` inlines `mcpServers` as a full object (not a `"./.mcp.json"` external reference), binding the `codetographer` server to `node ${CLAUDE_PLUGIN_ROOT}/mcp/server.js` with `NODE_PATH=${CLAUDE_PLUGIN_DATA}/node_modules`. The env wiring assumes `${CLAUDE_PLUGIN_DATA}/node_modules` exists at MCP server startup; the install side-channel runs `install-deps.js` `detached` + `unref`ed by the session-start sanity check, with no startup-gate or retry — first `codetographer_*` MCP calls before deps finish installing fail with `Cannot find module`.

## Component composition

### Skills (universal)

`skills/codetographer/`, `skills/sanity/`. The two skill entry points `/codetographer` and `/sanity` are skill slash-invocations.

### Agents

`agents/domain-explorer.md`, `agents/structural-scanner.md`, `agents/sync-agent.md`.

### Hooks

`hooks/hooks.json` plus five `.js` files.

### MCP servers

One inline-declared `codetographer` MCP server; no `.mcp.json`.

### Composition shapes

Hooks + MCP server (no commands; skills are minimal — primarily orchestration) — entire product surface is one MCP server (with several `codetographer_*` tools), three subagents, and five hook scripts. Claude reaches the tools via MCP, not via slash commands or skill invocations; hooks handle context injection and auto-sync.

## Skill authoring conventions

### Standard frontmatter

Two skills (`codetographer/SKILL.md`, `sanity/SKILL.md`). The SKILL.md references `wizard-flow.md`, `domain-templates.md`, `index-template.md` under `references/` (per-skill reference files used for progressive disclosure).

## Agent declaration conventions

### Minimal frontmatter (name, description)

`domain-explorer.md` declares `name: domain-explorer`, `description: "Deep-dive a single code domain and produce a complete domain documentation file. Use when mapping a codebase domain to generate or update a domain doc in docs/codetographer/domains/."`. No `model`, `tools`, `skills`, `memory`, `background`, or `isolation` fields. The other two agent files (`structural-scanner.md`, `sync-agent.md`) were not opened in this research pass.

## Server runtime (MCP)

### In-place stdlib script (no installer)

The MCP server runs as `node ${CLAUDE_PLUGIN_ROOT}/mcp/server.js` with `NODE_PATH=${CLAUDE_PLUGIN_DATA}/node_modules`. Server source lives in the plugin tree; deps install into the data dir at session start. The MCP server `watchFile`s `docs/codetographer/map.md` (authored by `hooks/stop.js`) with a 500ms debounce — it parses the rendered map, not the source, decoupling MCP responsiveness from tree-sitter parsing cost.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory. The "CLI" is `scripts/sanity.js` invoked explicitly by the `/sanity` skill via `node $CLAUDE_PLUGIN_ROOT/scripts/sanity.js ...`, not a PATH-installed binary. `install-deps.js` starts with `#!/usr/bin/env node` but is invoked via `process.execPath` (not the shebang). All scripts are `.js` invoked with `node` as the command.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Scripts use `${CLAUDE_PLUGIN_ROOT}` with script-dir fallbacks (e.g., `CLAUDE_PLUGIN_ROOT ?? dirname(dirname(__dirname))`). `install-deps.js` exits 1 if `CLAUDE_PLUGIN_DATA` is unset; `stop.js` falls back to `join(projectDir, '.codetographer-data')`. `CLAUDE_PROJECT_DIR ?? process.cwd()` is the project-root fallback. Inconsistent fallback policy across scripts.

## Dependency installation

### SessionStart hook → npm install local to plugin

`scripts/install-deps.js` writes `node_modules` into `${CLAUDE_PLUGIN_DATA}` (the plugin's writable data directory), not the plugin root. `NODE_PATH=${CLAUDE_PLUGIN_DATA}/node_modules` in `plugin.json`'s inline `mcpServers` env wires the MCP server to resolve from that location. `npm install --production --legacy-peer-deps` runs via `child_process.execSync` with `cwd: pluginData`. Uses `"engines": { "node": ">=20.0.0" }`, `"type": "module"`. 19 production dependencies including tree-sitter grammars, `@modelcontextprotocol/sdk`, `better-sqlite3`, `web-tree-sitter`. Manifest is `package.json` only — no `requirements.txt`, `pyproject.toml`, `Cargo.toml`, or `go.mod`. Version-mismatch handling is implicit via content-equality check on `package.json` (see *Install change detection*). No Node ABI tracking for `better-sqlite3` rebuilds — if Node is upgraded between sessions, `better-sqlite3` can fail to load and the plugin falls back to a JSON cache silently (`tag-cache.ts` fallback path). Install script tolerates `better-sqlite3` compile failures and exits 0 as long as `@modelcontextprotocol` installed; emits stderr human-readable warnings for `better-sqlite3` with corrective install commands ("Visual Studio Build Tools (Windows) or build-essential (Linux)") plus a fallback message ("Codetographer will fall back to JSON file cache").

## Install change detection

### Diff-based byte comparison of manifest

`src/sanity.ts`'s `checkNodeModules` reads both `${CLAUDE_PLUGIN_ROOT}/package.json` and `${CLAUDE_PLUGIN_DATA}/package.json` with `readFileSync(..., 'utf-8')` and does `if (rootContent !== dataContent)`. CLAUDE.md describes this as "checksums" but the implementation is plain string comparison of the raw file contents (the inline comment in the source even says "simplified: compare file sizes as proxy" — code is actually comparing full contents, so the comment is out of date). No sha256/md5, no mtime, no version-field-only comparison. `node_modules` existence is the first gate (check 15) — a missing directory short-circuits to "spawn install-deps" without reading either `package.json`. Copy-then-install ordering pitfall: `install-deps.js` copies `package.json` from `${CLAUDE_PLUGIN_ROOT}` to `${CLAUDE_PLUGIN_DATA}` BEFORE running `npm install` there. `copyFileSync(srcPkg, dstPkg)` happens before `execSync('npm install', { cwd: pluginData })`, so the copy is committed even if the subsequent install fails. A failed install leaves a freshly-copied `package.json` in DATA that does match ROOT, which makes the next `checkNodeModules` see "contents equal" and fall through to the `node_modules`-existence check. If `node_modules/` partially populated before the install failed, the content-equality comparison declares the plugin healthy despite a broken install.

## Install trigger and lifecycle

### Sanity-check-gated indirect invocation

`SessionStart` hook → `runSanityCheck({ fix: true, skipExpensive: true })` → `checkNodeModules` (checks 15+16) → `spawn install-deps.js detached`. Sanity check 15 gates on `node_modules/` existence; check 16 gates on `package.json`-contents equality between ROOT and DATA. The user can invoke the same repair manually via `/sanity --fix`.

## Install failure posture

### Multi-layer fail-open with stderr advisory

`install-deps.js` writes human-readable `[plugin-name]`-prefixed stderr lines with corrective install commands ("install build-essential" / "install Visual Studio Build Tools"). Top-level catch swallows errors so session start never fails. Hook output is a JSON `hookSpecificOutput.additionalContext` warning prefixed with a glyph (`⚠`) telling the user to run `/sanity`. No `continue: false`, no exit-2 — model gets degraded context but session lives. If a truly critical dep fails, the script exits 1 — but the hook calls it `detached` with `stdio: 'ignore'`, so the exit code is never observed. On next session, the sanity check re-fires and re-spawns install if `node_modules/` is absent or `package.json` contents differ.

## User configuration and authentication

### No userConfig, env-var only

`plugin.json` has no `userConfig`. Configuration is read from runtime env vars `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PROJECT_DIR` set by the harness, with coded fallbacks per script. No `${user_config.*}` substitutions; only `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}` are referenced.

## Tool-use enforcement

### PostToolUse for index/state maintenance

Two `PostToolUse` matchers. `Write|Edit` runs `post-tool-use.js` (logs edited path + matched domain to `docs/codetographer/changes.md`). The matcher fires on every `Write`/`Edit`; logging hooks produce no structured output and mutate files in the target project.

### PostToolUse git-commit detector

`PostToolUse` matcher `Bash` runs `post-commit.js` — fires on every bash tool use and internally filters for `git commit` substring before doing anything. On match, shells out to `git log`/`git diff-tree` to record the commit hash, subject, and affected domains to a docs file. Lower-cost alternative would be a regex-over-command-string matcher if Claude Code supported it; current spec matches on tool name only.

## Hook output contract

### `hookSpecificOutput.additionalContext` envelope versus bare top-level

Stdout JSON `{ hookSpecificOutput: { additionalContext } }` for context-injecting hooks (session-start, subagent-start, post-compact). Stderr human-readable for errors. Logging hooks (post-tool-use, post-commit, stop) produce no structured output — they mutate files in the target project.

## Hook failure posture

### Fail-open with always-exit-0

`main().catch(() => process.exit(0))` is the recurring pattern across every hook entry point.

## Session context loading

### `additionalContext` payload at SessionStart

`session-start.js` reads `INDEX.md` plus the tail of `changes.md` via `loadContext(projectDir)` and emits `hookSpecificOutput.additionalContext`. Matcher `"startup|resume|clear"`. `subagent-start.js` and `post-compact.js` emit the same shape. `timeout: 5` (seconds) with `async: true`; `skipExpensive: true` flag is passed precisely to stay under 5s. I/O-bound cold-cache starts on slow disks may still blow the budget; `async: true` means the session does not block — context arrives late on slow disks rather than failing the session.

### PreCompact hook for state-file eviction

A separate `PostCompact` hook handles re-injection after compaction (`compact` is not in the `SessionStart` matcher, so the README's "after compaction" path is the `PostCompact` hook, not `SessionStart`).

## SessionStart matcher scope

### Explicit subset

`session-start.js` matcher is `"startup|resume|clear"` (excludes `compact`). The compact path is owned by a separate `PostCompact` hook.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. The MCP server uses `watchFile(MAP_PATH, ...)` with a 500ms debounce inside `mcp/server.js` for its own in-memory cache, but that's MCP-internal, not a plugin monitor surface.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` has no `dependencies` key, and with no marketplace manifest there is no marketplace-level `dependencies` either. No tags exist, so the `{plugin-name}--v{version}` form is moot.

## Testing

### node:test with tsx loader

Node.js built-in `node:test` runner (confirmed via `import { test } from 'node:test'` in `tests/sanity.test.ts`) with `tsx/esm` loader to run TypeScript tests directly. `npm test` runs `node --import tsx/esm --test 'tests/*.test.ts' 'tests/hooks/*.test.ts' 'tests/mcp/*.test.ts'`. CLAUDE.md warns that the glob patterns may expand to zero files on Windows bash and lists an explicit-paths workaround.

### Centralized `tests/` placement

`tests/` at repo root with subdirectories `tests/hooks/`, `tests/mcp/`, `tests/fixtures/`. Single plugin = single test root.

## CI workflow shape

### No CI

`.github/workflows/` directory does not exist (`/repos/.../contents/.github` returns 404). The `1.0.0` declared release has no automated validation; tests exist locally but only run on a contributor's machine.

## Marketplace validation

### No validation

No `marketplace.json` to validate, no CI to run a validator. Skill and agent frontmatter is hand-written and unverified by tooling. `hooks/hooks.json` is committed as-is. The sanity-check skill (`/sanity`) validates installation-time artifacts (docs structure, domain freshness, node_modules, hook config on the user's machine) rather than the plugin's own manifests pre-publish — it's a runtime health check, not a manifest validator.

## Release automation

### No release automation / manual

No `release.yml`, no GitHub Releases cut, no tags. Releases are ad-hoc `git push main`. The "1.0.0" claim in both manifests is purely declarative.

## Documentation surface

### README + LICENSE (minimal)

Repo-root `README.md` (~4.4 KB) opens with a value-pitch paragraph, then "How It Works", the three-tier explanation, "What Stays In Sync", install via `claude --plugin-dir`, MCP tools list, dashboard menu, language-support list, cross-platform notes, diagnostics (`/sanity`), contributing, MIT license. No badges in README body.

### docs/DESIGN.md and docs/SPEC.md

Architectural content lives in `docs/DESIGN.md` (~36 KB) and `docs/SPEC.md` (~22 KB) rather than a root `architecture.md`. A consumer following the "architecture.md at root" convention misses them.

### CLAUDE.md as architecture-doc carrier

Repo-root `CLAUDE.md` (~6.5 KB) carries Project Overview, Build & Test Commands, Build System Gotcha (`copy-hooks.js` import patching), Architecture (data pipeline, hooks, MCP, skill/agent orchestration, sanity check system), Key Conventions, Gotchas. Detailed for a v1.0.0 repo.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md`. No top-level `architecture.md` — architectural content lives in `docs/DESIGN.md` and `docs/SPEC.md` instead.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` at repo root (MIT, 1069 bytes); SPDX `MIT` in `plugin.json` and `package.json`. README references the same.

## Community health files

### Bare minimum (LICENSE only)

Root carries `LICENSE`. No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`.

## Cross-platform discipline

### Documented Windows-native migration

README and CLAUDE.md highlight cross-platform discipline: "Works on Windows and Linux. Forward slashes everywhere, LF line endings, atomic file writes with Windows EPERM handling." No `.cmd`/`.ps1` pair — pure Node scripts invoked by `node`.

## Project-convention sidecar files

### `.codetographignore` plugin-private ignore file

Target projects can create `.codetographignore` (same syntax as `.gitignore`) to exclude paths from the tree-sitter map without polluting `.gitignore`. Plugin-private ignore namespace.

### Plugin-internal `.scm` query asset class

`scripts/queries/` holds per-language tree-sitter `.scm` query files loaded at runtime by `tag-extractor.ts`. Not a `skills/`, `agents/`, `hooks/`, or `commands/` component — an unconventional plugin-internal asset class shipping as data alongside executable code.

## Native artifact distribution

### WASM-over-native with graceful fallback

Tree-sitter parsers loaded via `web-tree-sitter` (WASM) so no native compilation needed for grammars. Only `better-sqlite3` requires native; on native failure, `tag-cache.ts` falls back to a JSON file cache with identical semantics (slower for large repos). Install script exits 0 even when the native build fails, treating native as an optimization rather than a requirement.

## Novel and cross-cutting concerns

### MCP server reads hook-authored artifact

`hooks/stop.js` writes `docs/codetographer/map.md` via `generateMap` + `atomicWrite`; `mcp/server.js` parses that map and `watchFile`s it with a 500ms debounce. MCP tool surface is a projection of hook-maintained state. Decouples MCP responsiveness from tree-sitter parsing cost — MCP doesn't parse source, it parses the rendered map.

### Cool-off window on event-driven regeneration

`hooks/stop.js` skips map regeneration if `map.md`'s mtime is within the last 60s, to avoid redundant work when `/sanity` or a manual map refresh just ran. Explicit de-dup window for event-driven artifact regeneration.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code (skills, agents, hooks, MCP server source, scripts, tree-sitter `.scm` queries) lives under `${CLAUDE_PLUGIN_ROOT}`. State (`node_modules`, `package.json` copy used as staleness marker, `.codetographer-data` fallback) lives under `${CLAUDE_PLUGIN_DATA}` — read-write, mutable, durable across upgrades.

## Cross-role tools

### Node + npm + npx

Node fills the MCP server runtime (`mcp/server.js`), the dependency installer (`install-deps.js`), all hook handlers (`.js`), and the test runner (`node:test` via `tsx/esm`). `npm install --production --legacy-peer-deps` is the install primitive.

### `${CLAUDE_PLUGIN_ROOT}` env var

Used by `mcpServers.codetographer.command` (`node ${CLAUDE_PLUGIN_ROOT}/mcp/server.js`) and as the source of truth for `package.json` content-equality comparison; required by `install-deps.js`, `session-start.js`, and other scripts (with script-relative fallbacks).

### `${CLAUDE_PLUGIN_DATA}`

Install destination for `node_modules`; `NODE_PATH=${CLAUDE_PLUGIN_DATA}/node_modules` in inline MCP env block. Required by `install-deps.js` (exits 1 if unset); `stop.js` falls back to `join(projectDir, '.codetographer-data')` when unset.

### `hookSpecificOutput.additionalContext`

Context-injection channel used by `session-start.js`, `subagent-start.js`, `post-compact.js`; also used by `session-start.js` to surface a `⚠ Codetographer sanity issues` advisory when the install side-channel is in a degraded state.

## Hook handler runtime

### TypeScript-compiled hooks with hand-patched imports

`scripts/copy-hooks.js` is a post-`tsc` distribution step that mirrors `dist/` into `hooks/dist/` + `mcp/dist/` + `scripts/` and rewrites relative imports (`'../xxx'` → `'./dist/xxx'`, `'../../xxx'` → `'../dist/xxx'`, etc.). Keeps hook entry points as plain `.js` files invokable with `node` while pulling shared code from a co-located `dist/` tree. Avoids both a runtime TS loader in hooks and a bundler. CLAUDE.md explicitly calls out "Always run `npm run build:hooks` (not just `npm run build`)" — a build-system gotcha the plugin requires the contributor to know.
