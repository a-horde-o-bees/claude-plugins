# thecodeartificerX/codetographer

## Identification

- **URL**: https://github.com/thecodeartificerX/codetographer
- **Stars**: 0
- **Last commit date**: 2026-03-25 (most recent commit `a3d533d`, pushed_at 2026-03-25T13:22:35Z)
- **Default branch**: `main`
- **License**: MIT (SPDX `MIT`)
- **Sample origin**: dep-management
- **One-line purpose**: "Claude Code plugin that maps your codebase via tree-sitter + agentic exploration, auto-injects context into every session and subagent" (GitHub repo description; README opens "Three-tier codebase navigation via tree-sitter mapping, agentic exploration, and hook-powered auto-sync").

## 1. Marketplace discoverability

- **Manifest layout**: no marketplace manifest at all. Only `.claude-plugin/plugin.json` is present at the repo root — the repo is shipped as a single bare plugin, installed via `git clone` + `claude --plugin-dir /path/to/codetographer` per the README. Repo-wide `search/code` for `filename:marketplace.json` returns `total_count=0`.
- **Marketplace-level metadata**: not applicable — no `marketplace.json`.
- **`metadata.pluginRoot`**: not applicable — no `marketplace.json`.
- **Per-plugin discoverability**: none at the Claude plugin level. `plugin.json` carries only `name`, `version`, `description`, `author`, `mcpServers`. Discoverability fields (`keywords`, `category`, `tags`) are declared instead in `package.json` via the npm `keywords` array: `claude-code`, `claude-code-plugin`, `codebase-navigation`, `tree-sitter`, `pagerank`, `mcp`, `ai-coding`, `context-injection`.
- **`$schema`**: absent from `plugin.json`.
- **Reserved-name collision**: no.
- **Pitfalls observed**: a plugin distributed without any `marketplace.json` (not even a local one) is visible only to users who clone the repo and point Claude Code at it directly; it would need an external marketplace to register it for normal `/plugin install` discovery. Discoverability metadata is split across two manifests (Claude `plugin.json` has none; `package.json` has npm keywords), so a marketplace aggregator consuming `plugin.json` alone would see nothing searchable.

## 2. Plugin source binding

- **Source format(s) observed**: not applicable — no marketplace manifest, so no `source` entries. Install is by explicit `--plugin-dir` path.
- **`strict` field**: not applicable — no marketplace manifest.
- **`skills` override on marketplace entry**: not applicable.
- **Version authority**: `plugin.json` only. Both `plugin.json` and `package.json` declare `version: "1.0.0"` and must be kept in sync by hand (no tooling links them); the `package.json` version is only consumed by npm tooling and the hook build script.
- **Pitfalls observed**: dual version fields (`plugin.json` + `package.json`) create a silent drift risk — nothing validates that `"1.0.0"` in both files stays identical across releases.

## 3. Channel distribution

- **Channel mechanism**: no split. There is a single `main` branch, no tags, no release branches; users pin by cloning and checking out any ref themselves.
- **Channel-pinning artifacts**: absent.
- **Pitfalls observed**: without tags or a marketplace entry, consumers have no stable channel — they install whatever `main` HEAD happens to be at clone time.

## 4. Version control and release cadence

- **Default branch name**: `main`.
- **Tag placement**: none (`/repos/.../tags` returns `[]`).
- **Release branching**: none — only `main` exists (`/repos/.../branches` lists just `main`).
- **Pre-release suffixes**: none observed.
- **Dev-counter scheme**: absent. `plugin.json.version` and `package.json.version` are both a static `1.0.0` as of the `a3d533d` HEAD.
- **Pre-commit version bump**: no — no hooks directory with git hooks, no visible `husky`/`lint-staged` in `package.json`.
- **Pitfalls observed**: initial public release (repo created 2026-03-25, all commits within ~3 hours) with no tag on `v1.0.0`. Anyone wanting reproducible installs has to pin by SHA.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery for skills/agents/hooks/commands; inline config object for `mcpServers`. `plugin.json` has no explicit `skills`, `agents`, `commands`, or `hooks` field — it relies on Claude Code's convention-based directory discovery (`skills/`, `agents/`, `hooks/`). `mcpServers` is inlined as a full object (not a `"./.mcp.json"` external reference), binding the `codetographer` server to `node ${CLAUDE_PLUGIN_ROOT}/mcp/server.js` with `NODE_PATH=${CLAUDE_PLUGIN_DATA}/node_modules`.
- **Components observed**: skills yes (`skills/codetographer/`, `skills/sanity/`), commands no (the two skill entry points `/codetographer` and `/sanity` are skill slash-invocations, not a separate `commands/` tree), agents yes (`agents/domain-explorer.md`, `agents/structural-scanner.md`, `agents/sync-agent.md`), hooks yes (`hooks/hooks.json` + five `.js` files), .mcp.json no (inline in `plugin.json`), .lsp.json no, monitors no, bin no, output-styles no.
- **Agent frontmatter fields used**: `name`, `description` (observed on `domain-explorer.md`: `name: domain-explorer`, `description: "Deep-dive a single code domain and produce a complete domain documentation file. Use when mapping a codebase domain to generate or update a domain doc in docs/codetographer/domains/."`). No `model`, `tools`, `skills`, `memory`, `background`, or `isolation` fields. The two other agent files (`structural-scanner.md`, `sync-agent.md`) were not opened in this research pass — inferred to follow the same minimal `name`+`description` shape but not verified.
- **Agent tools syntax**: not applicable — no `tools` field used.
- **Pitfalls observed**: the `mcpServers` env wiring assumes `${CLAUDE_PLUGIN_DATA}/node_modules` exists at MCP server startup; if the session starts before `install-deps.js` completes (it is spawned `detached` + `unref`ed by the session-start sanity check), the first `codetographer_*` MCP calls will fail with `Cannot find module` until deps finish installing. There is no startup-gate or retry described in the code.

## 6. Dependency installation

- **Applicable**: yes — Node/npm plugin with 19 production dependencies (tree-sitter grammars, `@modelcontextprotocol/sdk`, `better-sqlite3`, `web-tree-sitter`).
- **Dep manifest format**: `package.json`. No `requirements.txt`, `pyproject.toml`, `Cargo.toml`, or `go.mod`.
- **Install location**: `${CLAUDE_PLUGIN_DATA}` — `install-deps.js` writes `node_modules` into the plugin's writable data directory, not the plugin root. `NODE_PATH=${CLAUDE_PLUGIN_DATA}/node_modules` in `plugin.json` wires the MCP server to resolve from that location.
- **Install script location**: `scripts/install-deps.js` at plugin root. Not inline in `hooks.json`. It is invoked indirectly: `session-start.js` → `runSanityCheck({ fix: true, ... })` → `checkNodeModules()` in `src/sanity.ts` → `spawn(process.execPath, [installScript], { detached: true, stdio: 'ignore' })`.
- **Change detection**: "compare `package.json` file contents byte-for-byte" between `${CLAUDE_PLUGIN_ROOT}/package.json` and `${CLAUDE_PLUGIN_DATA}/package.json`. `src/sanity.ts` reads both with `readFileSync(..., 'utf-8')` and does `if (rootContent !== dataContent)`. CLAUDE.md describes this as "checksums", but the implementation is plain string comparison of the raw file contents (the inline comment in the source even says "simplified: compare file sizes as proxy" — the code is actually comparing full contents, so the comment is out of date). No sha256/md5, no mtime, no version-field-only comparison. Also: `node_modules` existence is the first gate (check 15) — a missing directory short-circuits to "spawn install-deps" without reading either `package.json`.
- **Retry-next-session invariant**: no explicit `rm` on failure. `install-deps.js` tolerates `better-sqlite3` compile failures and still exits 0 as long as `@modelcontextprotocol` installed. If a truly critical dep fails, it exits 1 — but the hook calls it `detached` with `stdio: 'ignore'`, so the exit code is never observed. On next session, the sanity check re-fires and will re-spawn install if `node_modules/` is absent or `package.json` contents differ.
- **Failure signaling**: multi-layered. Inside `install-deps.js`: stderr human-readable warning for `better-sqlite3` with corrective command ("Visual Studio Build Tools (Windows) or build-essential (Linux)") and a fallback message ("Codetographer will fall back to JSON file cache"). Around it: the session-start hook wraps `runSanityCheck` in `try/catch` and silently swallows errors ("sanity check failure must not break session start"). Hook output format is JSON `{ hookSpecificOutput: { additionalContext } }` with a `⚠ Codetographer sanity issues:` prefix telling the user to run `/sanity` — no `continue: false`, no `stopReason`, no exit 2.
- **Runtime variant**: Node npm. `"engines": { "node": ">=20.0.0" }`, `"type": "module"`, `npm install --production --legacy-peer-deps` executed via `child_process.execSync` with `cwd: pluginData`.
- **Alternative approaches**: none observed in this plugin. No PEP 723, no `uvx`/`npx` ad-hoc fetch, no pointer file.
- **Version-mismatch handling**: implicit via `content-equality`-check on `package.json`. If the user upgrades the plugin and `package.json` changes even by whitespace, the next session start detects the mismatch and spawns `install-deps.js`. There is no Node ABI tracking for `better-sqlite3` rebuilds — if Node is upgraded between sessions, `better-sqlite3` can fail to load and the plugin falls back to a JSON cache silently (`tag-cache.ts` fallback path).
- **Pitfalls observed**: **copy-then-install ordering is unusual and asymmetric.** The canonical pattern documented in Claude Code's plugin reference is "install into `${CLAUDE_PLUGIN_DATA}`, detect change via hash of the source manifest." Codetographer instead *copies* `package.json` from `${CLAUDE_PLUGIN_ROOT}` to `${CLAUDE_PLUGIN_DATA}` *before* running `npm install` there, then on the next run uses the copy as a staleness marker — "does the copy in DATA match the source in ROOT?". Ordering detail: `copyFileSync(srcPkg, dstPkg)` happens **before** `execSync('npm install', { cwd: pluginData })`, so the copy is committed even if the subsequent install fails. Consequence: a failed install leaves a freshly-copied `package.json` in DATA that *does match* ROOT, which makes the next `checkNodeModules` see "contents equal" and fall through to the `node_modules`-existence check. If `node_modules/` partially populated before the install failed, the content-equality comparison will declare the plugin healthy despite a broken install. Also: the code comment "simplified: compare file sizes as proxy" is stale — the implementation compares full contents, not just sizes. Detached `unref`ed spawn is fire-and-forget: the hook returns within its 5s timeout regardless of whether install is still running, and there is no readiness probe before the MCP server tries to `require` modules from `${CLAUDE_PLUGIN_DATA}/node_modules`.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no. There is no `bin/` directory. The "CLI" is `scripts/sanity.js` invoked explicitly by the `/sanity` skill via `node $CLAUDE_PLUGIN_ROOT/scripts/sanity.js ...`, not a PATH-installed binary.
- **`bin/` files**: none.
- **Shebang convention**: `install-deps.js` starts with `#!/usr/bin/env node` but is invoked via `process.execPath` (not the shebang). Other scripts are `.js` invoked with `node` as the command.
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` required — every hook and script path is rooted at that env var.
- **Venv handling (Python)**: not applicable.
- **Platform support**: POSIX + Windows. README and CLAUDE.md highlight "Works on Windows and Linux. Forward slashes everywhere, LF line endings, atomic file writes with Windows EPERM handling." No `.cmd`/`.ps1` pair — pure Node scripts invoked by `node`.
- **Permissions**: not applicable (no bin/). Scripts are invoked by `node`, not directly executed.
- **SessionStart relationship**: not applicable for bin-wrapping. But note: SessionStart hook does spawn `install-deps.js` as a side channel (see purpose 6).
- **Pitfalls observed**: not applicable.

## 8. User configuration

- **`userConfig` present**: no.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable — no `userConfig`, no `${user_config.*}` substitutions. Only `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, and `${CLAUDE_PROJECT_DIR}` are referenced.
- **Pitfalls observed**: plugin relies on runtime env vars `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, and `CLAUDE_PROJECT_DIR` being set by the harness. Fallbacks are coded: `CLAUDE_PROJECT_DIR ?? process.cwd()`, `CLAUDE_PLUGIN_ROOT ?? dirname(dirname(__dirname))`, `CLAUDE_PLUGIN_DATA` has no fallback in `install-deps.js` (exits 1 if unset) but in `stop.js` it falls back to `join(projectDir, '.codetographer-data')`. The inconsistent fallback policy is noted here, not in the userConfig section.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: 2 entries in `hooks.json`. One with `matcher: "Write|Edit"` runs `post-tool-use.js` (logs edited path + matched domain to `docs/codetographer/changes.md`). One with `matcher: "Bash"` runs `post-commit.js` (parses the bash command; exits silently unless it contains `git commit`; then shells out to `git log`/`git diff-tree` to record the commit hash, subject, and affected domains). Purpose is auto-sync of the docs, not permission enforcement.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stdout JSON `{ hookSpecificOutput: { additionalContext } }` for context-injecting hooks (session-start, subagent-start, post-compact). Stderr human-readable for errors. Logging hooks (post-tool-use, post-commit, stop) produce no structured output — they mutate files in the target project.
- **Failure posture**: fail-open across the board. Every hook entry point wraps `main()` in `.catch(() => process.exit(0))`. The session-start hook explicitly comments: "sanity check failure must not break session start". No hook returns `continue: false` or a blocking exit code.
- **Top-level try/catch wrapping**: observed — `main().catch(() => process.exit(0))` is the recurring pattern.
- **Pitfalls observed**: the `PostToolUse` matcher `"Bash"` fires on every single bash tool use and then internally filters for `git commit` in the command string. Lower-cost alternative would be a more specific matcher if Claude Code supported regex over command strings, but the current hook spec matches on tool name only. The silent fail-open posture means an install-failed session will silently not have map/domain context, with the only signal being a `⚠ sanity issues` line in the additionalContext injection.

## 10. Session context loading

- **SessionStart used for context**: yes — primary mechanism. Hook reads `INDEX.md` + tail of `changes.md` via `loadContext(projectDir)` and emits `hookSpecificOutput.additionalContext`.
- **UserPromptSubmit for context**: no — not used.
- **`hookSpecificOutput.additionalContext` observed**: yes (session-start.js, post-compact.js, subagent-start.js all emit this shape).
- **SessionStart matcher**: `"startup|resume|clear"`. Note: the README says context is injected "at session start, after /clear, and after compaction" — the "after compaction" path is handled by a separate `PostCompact` hook, not by `SessionStart`, because `compact` is not in the `SessionStart` matcher.
- **Pitfalls observed**: the `timeout: 5` (seconds) on `SessionStart` with `async: true` is tight given that the hook also triggers a full sanity-check with `fix: true` and may spawn `install-deps.js`. The `skipExpensive: true` flag is passed precisely to stay under 5s, but I/O-bound cold-cache starts on slow disks may still blow through the budget. `async: true` means the session does not block on the hook, so this is a soft failure (context arrives late), not a hard one.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: not applicable — no monitors, so the only live-sync mechanism is the hook set. The MCP server does use `watchFile(MAP_PATH, ...)` with a 500ms debounce inside `mcp/server.js` for its own in-memory cache, but that's MCP-internal, not a plugin monitor surface.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — `plugin.json` has no `dependencies` key (and with no marketplace manifest, there is no marketplace-level `dependencies` either).
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — no tags at all.
- **Pitfalls observed**: not applicable.

## 13. Testing and CI

- **Test framework**: Node.js built-in `node:test` runner (confirmed via `import { test } from 'node:test'` in `tests/sanity.test.ts`) with `tsx/esm` loader to run TypeScript tests directly.
- **Tests location**: `tests/` at repo root with subdirectories `tests/hooks/`, `tests/mcp/`, `tests/fixtures/`. Tests live beside the plugin, not inside a per-plugin tree (there is only one plugin).
- **Pytest config location**: not applicable (Node).
- **Python dep manifest for tests**: not applicable.
- **CI present**: no — `/repos/.../contents/.github` returns 404. No `.github/workflows/` directory.
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: `npm test`, defined as `node --import tsx/esm --test 'tests/*.test.ts' 'tests/hooks/*.test.ts' 'tests/mcp/*.test.ts'`. CLAUDE.md warns that the glob patterns may expand to zero files on Windows bash and lists an explicit-paths workaround.
- **Pitfalls observed**: no CI means the `1.0.0` release has no automated validation; tests exist locally but only run on a contributor's machine. The "Windows bash may match zero files" caveat in CLAUDE.md is a concrete shell-portability pitfall baked into the npm script — a `tsx --test $(git ls-files ...)` style or a custom runner would be more portable.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — releases are ad-hoc `git push main`. No GitHub Releases have been cut (tags list is empty).
- **Tag-sanity gates**: not applicable.
- **Release creation mechanism**: not applicable.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable.
- **Pitfalls observed**: the claim "1.0.0" in both manifests is purely declarative — there is no tag, release, or automation enforcing it.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable — no `marketplace.json` to validate, no CI to run a validator.
- **Trigger**: not applicable.
- **Frontmatter validation**: no automated check — observed skill and agent frontmatter is hand-written and unverified by tooling in this repo.
- **Hooks.json validation**: no automated check — `hooks/hooks.json` is committed as-is.
- **Pitfalls observed**: the sanity-check skill (`/sanity`) validates installation-time artifacts (docs structure, domain freshness, node_modules, hook config on the user's machine) rather than the plugin's own manifests pre-publish. It is a runtime health check, not a manifest validator.

## 16. Documentation

- **`README.md` at repo root**: present (~4.4 KB). Opens with a value-pitch paragraph, then "How It Works", the three-tier explanation, "What Stays In Sync", install via `claude --plugin-dir`, MCP tools list, dashboard menu, language-support list, cross-platform notes, diagnostics (`/sanity`), contributing, MIT license.
- **Owner profile README at `github.com/thecodeartificerX/thecodeartificerX`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: not applicable (single plugin = the repo root README).
- **`CHANGELOG.md`**: absent.
- **`architecture.md`**: absent at repo root. `docs/DESIGN.md` (~36 KB) and `docs/SPEC.md` (~22 KB) exist and appear to carry architectural content (not opened in this pass — contents inferred from filename and size only). There is no file literally named `architecture.md`.
- **`CLAUDE.md`**: present at repo root (~6.5 KB) — well-structured with Project Overview, Build & Test Commands, Build System Gotcha (`copy-hooks.js` import patching), Architecture (data pipeline, hooks, MCP, skill/agent orchestration, sanity check system), Key Conventions, Gotchas. Not per-plugin (single plugin).
- **Community health files**: none observed — no `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` in the top-level contents listing.
- **LICENSE**: present (MIT, 1069 bytes).
- **Badges / status indicators**: none visible in the README body fetched.
- **Pitfalls observed**: `CLAUDE.md` is unusually strong for a v1.0.0 repo (detailed build gotchas, hook protocol explanation, list of supported languages, env-var contract) and would be the authoritative onboarding read. `docs/DESIGN.md` + `docs/SPEC.md` serve the architectural role `architecture.md` would in this project's own convention, but a consumer following the "`architecture.md` at root" convention will miss them.

## 17. Novel axes

- **TypeScript-compiled plugin with hand-patched import paths.** `scripts/copy-hooks.js` is a post-`tsc` distribution step that mirrors `dist/` into `hooks/dist/` + `mcp/dist/` + `scripts/` and rewrites relative imports (`'../xxx'` → `'./dist/xxx'`, `'../../xxx'` → `'../dist/xxx'`, etc.). Keeps hook entry points as plain `.js` files that can be invoked with `node` but pull their shared code from a co-located `dist/` tree. Alternative plugins tend to either ship hand-written `.js` hooks, use `tsx` at runtime, or bundle — this pattern sits between them and avoids both a runtime TS loader in hooks and a bundler. The explicit call-out "Always run `npm run build:hooks` (not just `npm run build`)" is a build-system-level gotcha novel to this plugin.
- **Hook-triggered, sanity-check-gated dep install.** The dependency install is not wired to SessionStart directly; it's wired indirectly through a diagnostic system. `session-start.js` → `runSanityCheck({ fix: true })` → `checkNodeModules` (checks 15+16) → `spawn install-deps.js detached`. Sanity check 15 gates on `node_modules/` existence; check 16 gates on `package.json`-contents equality between ROOT and DATA. This is a novel structuring of dep-install as "just another self-healing invariant" rather than a first-class SessionStart hook action. It also means the user can invoke the same repair manually via `/sanity --fix`, which would be harder with inline SessionStart logic.
- **Unconditional copy-then-install ordering.** `install-deps.js` copies `package.json` from ROOT to DATA **before** running `npm install` in DATA, then future runs use the copied file as the staleness marker. This ordering is unusual: a failed install still leaves a "fresh" copy, making the next content-equality check pass and masking the failure. Pattern-doc candidate: document copy-then-install ordering as an anti-pattern when the copy is the staleness marker and there is no post-install validation.
- **`.codetographignore` as a second-layer ignore file.** Target projects can create `.codetographignore` (same syntax as `.gitignore`) to exclude paths from the tree-sitter map without polluting `.gitignore`. Novel "plugin-private ignore file" pattern.
- **WASM-over-native with graceful fallback for the cache.** tree-sitter parsers use `web-tree-sitter` (WASM) so there's no native compilation. Only `better-sqlite3` needs native binaries; on native failure, `tag-cache.ts` falls back to a JSON file cache with identical semantics, slower for large repos. Install script exits 0 even when the native build fails.
- **Plugin-owned `.scm` query files.** `scripts/queries/` holds per-language tree-sitter query files (one per supported language), loaded at runtime by `tag-extractor.ts`. This is a unusual plugin-internal asset class — not a `skills/`, `agents/`, `hooks/` or `commands/` component, just data assets shipped alongside executable code.
- **MCP server reads an artifact authored by hooks.** `mcp/server.js` parses `docs/codetographer/map.md` (authored by `hooks/stop.js` via `generateMap` + `atomicWrite`) and `watchFile`s it with a 500ms debounce. The MCP tool surface is therefore a projection of hook-maintained state. This decouples MCP responsiveness from tree-sitter parsing cost — MCP doesn't parse source, it parses the rendered map.
- **Split discoverability metadata across manifests.** `plugin.json` carries no keywords/tags/category; `package.json` carries npm `keywords`. A marketplace aggregator that reads `plugin.json` alone sees no search metadata; one that reads `package.json` alone would not know the MCP server wiring.
- **60-second cool-off on map regeneration.** `hooks/stop.js` skips regeneration if `map.md`'s mtime is within the last 60s, to avoid redundant work when `/sanity` or a manual map refresh just ran. Explicit de-dup window for event-driven regeneration.

## 18. Gaps

- **`structural-scanner.md` and `sync-agent.md` frontmatter unread.** Only `domain-explorer.md` was fetched. Whether the other two agent specs use extra frontmatter fields (`tools`, `model`, etc.) is unverified. Resolution: one `WebFetch` each against the raw URLs for those files.
- **`docs/DESIGN.md` and `docs/SPEC.md` contents unread.** Inferred from filename/size (36 KB + 22 KB) to be architectural, but the actual layering, audience, and relationship to `CLAUDE.md` was not validated. Resolution: paginated reads of both files — 58 KB total exceeds a single WebFetch comfortably, so 2-4 fetches each.
- **`docs/superpowers/`** subdirectory contents unknown (listed as type=dir, not expanded). Resolution: one `gh api .../contents/docs/superpowers` listing.
- **`skills/codetographer/references/` contents unknown** — the SKILL.md references `wizard-flow.md`, `domain-templates.md`, `index-template.md` but none of those reference files were opened. Their structure informs whether the skill uses progressive disclosure via reference files. Resolution: list `skills/codetographer/references/` and fetch those three files.
- **`src/sanity.ts` full diagnostic list unread.** 17 checks are claimed; only check 15+16 (node_modules) were inspected. The other 15 checks may reveal additional invariants the plugin self-enforces. Resolution: page through `src/sanity.ts` in 2-3 WebFetches or blob reads.
- **`tests/fixtures/` contents unknown** — listed as dir but not expanded. Fixture shape would clarify what "healthy project" looks like per the test suite. Resolution: one listing + spot-fetch of any notable fixture files.
- **`hooks/lib/` contents unknown** — `context-loader.js` and `recent-activity.ts`/`recent-activity.js` are imported by hooks but their full contents were not fetched. Not critical for pattern-doc verification but would clarify domain-matching algorithm and changes.md tail-reading behavior. Resolution: two WebFetches.
- **`tree-sitter-c-sharp` and other grammar `.wasm` vs npm packages at runtime.** `package.json` lists the native npm packages, but the runtime uses WASM via `web-tree-sitter`. How the two are reconciled at install time (whether the native tree-sitter packages are in fact needed, or shipped only for dev-time reasons) was not traced. Resolution: examine `tag-extractor.ts` for actual parser loading logic.
- **Whether the repo is intended for eventual marketplace listing.** No `marketplace.json` at repo root today, but the README's `claude --plugin-dir /path/to/codetographer` install instructions suggest direct-clone is the intended primary channel. No issue, PR, or roadmap section indicates marketplace publication plans. Resolution: check `gh api repos/.../issues` and open `docs/SPEC.md` if it discusses distribution.
