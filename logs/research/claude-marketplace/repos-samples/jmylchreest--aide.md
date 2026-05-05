# Sample

Mirrors of `https://github.com/jmylchreest/aide`. AI Development Environment plugin: persistent memory, code intelligence, and multi-agent orchestration; same codebase ships to Claude Code, OpenCode, and Codex CLI. MIT-licensed; 6 stars at sample time; current tip is `0.0.61` on default branch `main`.

## Marketplace manifest layout

### Single root manifest with relative source under `plugins/<name>/`

Single `.claude-plugin/marketplace.json` at repo root with one plugin entry; repo root is the plugin (`source: "./"`). Top-level carries `description` and `owner`; no `metadata.{...}` wrapper, no top-level `version`, no `pluginRoot`.

### `$schema` declaration on marketplace.json

`$schema` present — `"https://anthropic.com/claude-code/marketplace.schema.json"`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry; `strict` field absent (default implicit `true`); `skills` override absent. Single plugin lives at repo root.

## Per-plugin discoverability metadata

### Category + tags pair

Marketplace entry carries `category: "productivity"` and `tags: ["multi-agent","orchestration","automation"]`. No `keywords`. Marketplace-entry tags and the GitHub repo's 17 topics (`ai`, `claude-code`, `mcp`, `skills`, etc.) are disjoint — the marketplace entry narrows heavily while the repo advertises broader discoverability.

## Version coordination

### Multi-site sprawl (5+ locations)

Four files carry the plugin version: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (plugin entry), `package.json`, `packages/opencode-plugin/package.json` — all at `0.0.61`. The `Makefile`'s `release` target does a `sed` across `VERSION_FILES` to keep them in sync; `release.yml`'s `prepare` job injects version via `-ldflags` into the Go binary. No commit-time validation.

### Pre-commit hook auto-sync (consistency, not increment)

No pre-commit hook auto-bumping or auto-syncing observed; the only enforcement is the `Makefile` `release` target invoked manually. CI does not verify cross-file version parity.

## Channel distribution

### Linear `0.0.z` dev counter

`plugin.json` tracks released semver in `0.0.z` form (`0.0.61`); each release bumps z. The Go binary's embedded version string adds a `0.0.X-dev.N+sha` suffix on main snapshots — computed via `git describe --tags --match 'v*' --always --long` in `release.yml`'s `prepare` job. The `plugin.json` `version` field does NOT dev-bump; it tracks released semver only.

### SHA pinning per external entry

The wrapper attempts the versioned binary URL (`releases/download/v<plugin-version>/<binary>`) first, then `releases/latest/download/<binary>` as fallback (race-condition mitigation per `getDownloadUrls` comment between marketplace pulls and release-action artifact uploads). The release workflow also maintains a `snapshot` tag force-deleted (`git push origin :refs/tags/snapshot`) and recreated on every push to main, then attached to a `prerelease: true` GitHub release. Wrapper distinguishes dev builds (`version.includes("-dev.")`) from release builds: dev builds accept `base >= plugin`; release builds require `>=` exact. Consumers caching by tag SHA against `snapshot` see silent moves.

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

Tags placed on main; release workflow triggers on `push: tags: ['v*']`. The `prepare` job detects "commit already has release tag" via `git tag --points-at HEAD | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$'` to skip the snapshot path on a release commit. Tags are plain `v0.0.61`, `v0.0.60`, … (no pre-release suffix on tags themselves; the only non-semver tag is the floating `snapshot`).

## Plugin-component registration

### Inline `mcpServers` definition in `plugin.json`

`plugin.json` carries inline `mcpServers` and `hooks` configuration (10 event groupings, 17 hook registrations). MCP launch command is `bun ${CLAUDE_PLUGIN_ROOT}/bin/aide-wrapper.ts mcp` with hard-coded `AIDE_CODE_WATCH=1` and `AIDE_CODE_WATCH_DELAY=30s` env values. No external `.mcp.json`.

### Default convention discovery

No `skills`, `commands`, or `agents` arrays in `plugin.json`; skills discovered from `skills/<name>/SKILL.md`, agents from `src/agents/*.md`.

## Component composition

### Skills (universal)

25 skills under `skills/<name>/SKILL.md`: `assess-findings`, `autopilot`, `build-fix`, `code-search`, `context-usage`, `debug`, `decide`, `design`, `docs`, `forget`, `git`, `implement`, `memorise`, `patterns`, `perf`, `plan-swarm`, `recall`, `review`, `semgrep`, `survey`, `swarm`, `test`, `verify`, `worktree-resolve`.

### Agents

9 agents under `src/agents/*.md` — not under `.claude-plugin/agents/`, no `agents` field in `plugin.json`. Roles: `architect`, `designer`, `executor`, `explore`, `planner`, `qa-tester`, `researcher`, `reviewer`, `writer`. These appear to be agent definitions consumed internally by the swarm skill's orchestration logic, not plugin-registered Claude Code sub-agents.

### Hooks

Inline in `plugin.json`. 10 event types, 17 total hook registrations, all invoking bun+TS scripts under `src/hooks/`.

### bin

`bin/aide-wrapper.ts` — single TypeScript wrapper launched by the MCP server command via `bun`.

## Skill authoring conventions

### Standard frontmatter

Skills carry standard `name` and `description` plus a `triggers: [...]` array (up to ~10 short phrases per skill) and sometimes `platforms: [...]`. The `triggers` array is consumed by `src/core/skill-matcher.ts` for fuzzy-matched activation. `scripts/validate-skills.ts` enforces required `name`, `description`, `triggers` and a non-empty triggers array.

## Agent declaration conventions

### Plain tool-name list

Agents declare `tools` as an array of plain tool names (no permission-rule syntax). Mixes Claude Code built-in names with aide-specific MCP tool names. Example (`executor.md`): `tools: [Read, Glob, Grep, Edit, Write, Bash, TodoWrite, lsp_diagnostics, lsp_diagnostics_directory]`.

### Standard fields plus model / color

Frontmatter on `src/agents/*.md`: `name`, `description`, `defaultModel` (values like `balanced`), `readOnly` (boolean), `tools` (array).

## Bin entry mechanism

### Lazy-install bin shim with fallback chain

`bin/aide-wrapper.ts` (TypeScript, `#!/usr/bin/env bun`) is a launcher and downloader for an out-of-tree native artifact. (1) `ensureDependencies()` detects missing `node_modules` and runs `bun install --frozen-lockfile` inline (rationale: "After a Claude Code marketplace autoUpdate (git pull), node_modules/ may be missing since it's gitignored"); `cross-spawn` is lazy-required so the install can complete before the require resolves. (2) `ensureBinary()` checks `bin/aide[.exe]` existence + parses `aide version` output through SemVer regex; downloads via `src/lib/aide-downloader.ts` if missing or stale. (3) Cross-platform `mkdir`-based lock (`bin/.aide-download.lock/pid`) with 60s timeout serializes concurrent invocations. (4) Forwards argv to the Go binary via `spawnSync` with `stdio: "inherit"`. Plugin-root resolution precedence is `AIDE_PLUGIN_ROOT` > `CLAUDE_PLUGIN_ROOT` > `realpathSync(SCRIPT_DIR/..)` — the same wrapper ships to OpenCode/Codex CLI consumers who don't set `CLAUDE_PLUGIN_ROOT`. Bun is a hard runtime prerequisite (`Bun.sleepSync` lock-poll, `bun` shebang); other `.ts` scripts in the repo use `#!/usr/bin/env bun` as well (`scripts/aide-hud.ts`, `scripts/aide-hud-wrapper.ts`, `scripts/validate-skills.ts`); `adapters/opencode/generate.ts` differs with `#!/usr/bin/env npx tsx`.

## Server runtime (MCP)

### Inline `mcpServers` definition in `plugin.json`

MCP server launched as `bun ${CLAUDE_PLUGIN_ROOT}/bin/aide-wrapper.ts mcp` from the inline `mcpServers` block in `plugin.json`. The wrapper performs the lazy install/download then forwards argv to the Go `aide` binary. Hard-coded env: `AIDE_CODE_WATCH=1`, `AIDE_CODE_WATCH_DELAY=30s`.

## Dependency installation

### SessionStart-driven dual-runtime install (Python venv + Node modules)

Two dependency chains: Node deps (TS hooks/wrapper via Bun) and Go binary (downloaded on demand). Node install happens lazily at every MCP launch via the wrapper's `ensureDependencies()`; Go binary is fetched on demand by `src/lib/aide-downloader.ts` and also pre-warmed by SessionStart's `ensureAideBinary(cwd)`. Bun is the only documented prerequisite; everything else self-heals at runtime.

### Existence-plus-version-compare

Node: existence of `node_modules` directory triggers `bun install --frozen-lockfile`. Binary: existence + `aide version` output parsed with regex + `versionGte` SemVer compare. Dev builds (`-dev.` in version) compare base semver and accept `base >= plugin`; release builds require exact-or-newer match.

## Install change detection

### Existence-plus-version-compare

`node_modules` existence for npm deps; binary existence + parsed `aide version` for the Go artifact. No hash-based detection. Wrapper unlinks stale binary before re-downloading (`Removing outdated binary before download`); `mkdir`-based lock with 60s timeout + forced-remove fallback handles concurrent invocations.

## Install failure posture

### Multi-layer fail-open with stderr advisory

Wrapper writes human-readable stderr log lines AND appends to `.aide/_logs/wrapper.log`; exits with `process.exit(1)` if downloader fails or binary missing post-download. Node install failure logs warning and continues (soft-fail). SessionStart hook catches all exceptions at the top level and always emits `{"continue": true}` to stdout — explicit fail-open posture (`uncaughtException` / `unhandledRejection` handlers call `outputContinue()` and `process.exit(0)`).

## Install trigger and lifecycle

### SessionStart direct invocation

`session-start.ts` runs `ensureAideBinary(cwd)` early in `main()`, triggering the same download path as the MCP wrapper. Two independent invocations (MCP launch + SessionStart) can both discover-missing-and-download, synchronised by the `mkdir`-based lock. Wrapper is the primary trigger; SessionStart is a secondary safety net.

### Lazy bootstrap on first hook (no SessionStart)

The wrapper's `ensureDependencies()` runs at every MCP launch — independent of SessionStart — so a marketplace `autoUpdate` that drops `node_modules` heals on the next MCP server start without waiting for a session.

## Hook handler runtime

### Node `.mjs` files invoked via `node`

Hook scripts under `src/hooks/` are TypeScript files invoked via `bun` (analogous to Node-style hook runtime — Bun specifically rather than Node). 17 hook registrations across 10 event types. Top-level `try { await readStdin(); ... } catch { outputContinue(); }` pattern observed in every hook sampled (`session-start.ts`, `skill-injector.ts`, `pre-tool-enforcer.ts`).

## Hook output contract

### JSON-only stdout, no stderr-human parallel

All hooks output `JSON.stringify({continue: true/false, ...})` to stdout. Human-readable logs go to `.aide/_logs/*.log` files (via the `Logger` class in `src/lib/logger.ts`) AND to stderr via `process.stderr.write`. Three separate channels with the invariant "hook crashes = stdout still valid JSON" — any hook that writes plain text to stdout breaks the harness.

### `additionalContext` for context injection

`session-start.ts` and `skill-injector.ts` both emit `hookSpecificOutput.additionalContext` payloads.

## Hook failure posture

### Fail-open with always-exit-0

`session-start.ts` installs global `process.on('uncaughtException')` + `process.on('unhandledRejection')` handlers that call `outputContinue()` (emits `{"continue":true}`) and `process.exit(0)`. A `try { ... } catch {}` pattern wraps `main()` in every hook inspected. `pre-tool-enforcer.ts` and `permission-handler.ts` DO return `continue: false` with a `message` when the enforcement evaluator explicitly denies — fail-open applies to unexpected errors, not to deliberate denials.

## Tool-use enforcement

### PostToolUse `*` context tracking

5 PreToolUse hooks (matcher `*`): `tool-tracker.ts` (per-agent current-tool tracking for HUD), `write-guard.ts`, `pre-tool-enforcer.ts` (read-only mode / agent tool-access rules), `context-guard.ts`, `search-enrichment.ts`. 4 PostToolUse hooks (matcher `*`): `tool-observe.ts` (record events for memory), `hud-updater.ts` (status line), `comment-checker.ts`, `context-pruning.ts`. 17 hook registrations all with matcher `*` means every tool invocation spawns multiple bun processes (timeouts 2–60s per hook).

### `if:` permission-rule sub-matcher

`src/hooks/permission-handler.ts` exists with header comment `OPT-IN: This hook is NOT registered in plugin.json by default. To enable, add a PermissionRequest entry to .claude-plugin/plugin.json. Not available in OpenCode (no equivalent event).` Present in source, dormant in manifest.

## Session context loading

### `additionalContext` payload at SessionStart

`session-start.ts` runs `coreBuildWelcomeContext(state, memories, notices)` and emits the result in `hookSpecificOutput.additionalContext`. Also performs binary check, MCP sync, HUD-wrapper install, directory init, config load, stale-state cleanup, and a session-init call to the `aide` binary that returns memories to inject. SessionStart matcher is `*` (fires on all sub-events — startup/clear/compact/resume) with no internal session-type discrimination. Hook timeout is 60s to accommodate binary-download latency on first run.

### `UserPromptSubmit` fuzzy-matched skill injection

`skill-injector.ts` fuzzy-matches the user prompt against YAML-frontmatter `triggers` arrays in `skills/**/SKILL.md` + `.aide/skills/**/*.md`, picks up to 3, and returns content in `hookSpecificOutput.additionalContext`. Skill-discovery layers ordered `.aide/skills/` > `skills/` > plugin-bundled > `~/.aide/skills/`. Fuzzy-match tolerates typos (e.g., "desgin" → "design"); skills mitigate accidental activation by scoping `triggers` arrays of 3-10 short phrases.

## SessionStart matcher scope

### Empty matcher (all sub-events)

Matcher `*`. Hook does not internally discriminate on session-type — same handler for startup, clear, compact, and resume.

## State persistence

### `${CLAUDE_PLUGIN_DATA}` for venvs and stamps

State directory created under `<cwd>/.aide/` (project-local) by SessionStart. Logs go to `.aide/_logs/*.log`; HUD state file at `.aide/state/hud.txt` is written by the `hud-updater.ts` PostToolUse hook.

### `<git-common-dir>/<plugin>/` for mission state

Project-local `.aide/` placement (rather than `${CLAUDE_PLUGIN_DATA}` or `<git-common-dir>`) is consistent with the swarm/memory features being scoped per-project.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. Live HUD/status-line behavior is implemented at a different layer: `scripts/aide-hud.ts` is installed to `~/.claude/bin/aide-hud.ts` during SessionStart, the `hud-updater.ts` PostToolUse hook writes `.aide/state/hud.txt`, and Claude Code's status-line integration reads the wrapper. A consumer looking for monitor-based live updates won't find any.

### Status line via user-settings mutation

SessionStart hook installs `~/.claude/bin/aide-hud.ts` (Bun-shebang script that discovers the newest installed plugin version under `~/.claude/plugins/cache/*/aide/*/scripts/aide-hud.ts` and delegates). This decouples user-facing HUD from plugin upgrades — new plugin versions provide new HUD scripts; the wrapper always finds the newest. A side-effect on the user's home directory not declared in `plugin.json`.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field. Single-plugin marketplace; bare semver tags (`v0.0.61`). No cross-plugin coupling.

## User configuration and authentication

### Out-of-band env vars (no `userConfig`)

No `userConfig` field in `plugin.json`. Configuration is via env vars documented in README: `AIDE_DEBUG`, `AIDE_FORCE_INIT`, `AIDE_CODE_WATCH`, `AIDE_CODE_WATCH_DELAY`, `AIDE_MEMORY_INJECT`, `AIDE_MEMORY_SCORING_DISABLED`, `AIDE_MEMORY_DECAY_DISABLED`, `AIDE_SHARE_AUTO_IMPORT`, plus `AIDE_PLUGIN_ROOT` for plugin-root override. `plugin.json` hard-codes `AIDE_CODE_WATCH=1` and `AIDE_CODE_WATCH_DELAY=30s` in the MCP `env` block.

## Testing

### Mixed `node:test` + pytest with custom runner

Multiple test frameworks: Vitest (TS, under `src/test/*.test.ts` and `tests/*.test.ts`), Go `testing` (Go, `*_test.go` throughout `aide/` and `aide-web/`). Integration tests in `ci.yml` use bash plus `jq` to drive hook scripts with stdin JSON. TypeScript tests split across `src/test/` (co-located unit) and `tests/` (root-level integration including `tests/memory-capture.test.ts` excluded from CI). `tests/memory-capture.test.ts` runs only locally.

## CI workflow shape

### Multi-job matrix with parallel test/validate/security/lint

`.github/workflows/ci.yml` has 6 jobs: (1) `typescript` — `bun install` + `bunx tsc --noEmit` + `bun run build` + `bunx vitest run --exclude='tests/memory-capture.test.ts'` + `bun run lint`; (2) `go` — `go test -v -race -coverprofile=coverage.out ./...` in `aide/`, uploads to Codecov; (3) `go-web` — same in `aide-web/`, plus builds the Astro frontend first (`bun run build` in `aide-web/web/`); (4) `go-lint` — `golangci-lint-action@v9`; (5) `build` — rebuilds TS, Go `aide`, Go `aide-web`, verifies binaries with `--help`, uploads linux-amd64 artifacts with 1-day retention; (6) `integration` — depends on `build`, drives hooks with piped JSON (`echo '{"hook_event_name":...}' | bun dist/hooks/skill-injector.js | jq -e '.continue == true'`) and runs `./bin/aide memory add/list` round-trip.

### Push + PR matrix CI

Triggers are `push: branches: [main]` + `pull_request: branches: [main]`. PRs that merge to main are tested twice (pre-merge + post-merge). `release.yml` triggers on both push (branches main, tags v*) and pull_request, but its build jobs gate on `github.event_name == 'push'` so PRs only run the test subset.

### Action-pinning conventions

Tag-pinned (`actions/checkout@v6`, `oven-sh/setup-bun@v2`, `actions/setup-go@v6`, `actions/upload-artifact@v6`, `actions/download-artifact@v8`, `actions/setup-node@v6`, `softprops/action-gh-release@v2`, `codecov/codecov-action@v5`, `golangci/golangci-lint-action@v9`, `svenstaro/upx-action@v2`, `actions/upload-pages-artifact@v4`, `actions/deploy-pages@v4`). No SHA pins. Caching via `setup-go@v6` (`cache: true`, `cache-dependency-path: aide/go.sum`), `setup-node@v6` (`cache: npm`); `setup-bun@v2` does its own caching. Codecov upload is `continue-on-error: true`.

## Marketplace validation

### Frontmatter validation by grep

`scripts/validate-skills.ts` validates SKILL.md frontmatter (required `name`, `description`, `triggers`; non-empty triggers array; no duplicate names; markdown-structure sanity). Custom inline YAML-frontmatter parser rather than depending on a YAML library. Runs as `bun run scripts/validate-skills.ts` — manual; not wired into CI in the workflows examined.

### No validation

No validation at all for `marketplace.json` / `plugin.json`; a typo in those files reaches users unless Claude Code's install-time parser catches it. No hooks.json validator, no agent-frontmatter validator.

## Release automation

### Multi-trigger workflow with single-snapshot path

Single 28KB `release.yml` handles PR CI, main-branch snapshots, and tag releases by gating jobs on `needs.prepare.outputs.is_release` and `github.event_name == 'push'`. `prepare` job detects "commit already has release tag" via `git tag --points-at HEAD | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$'` to skip the snapshot path on a release commit. Jobs (in dependency order): `prepare` → `test` → `build` (aide, 6 platforms) + `build-web` + `build-grammars` + `build-npm` → `release` (tag push only) OR `snapshot` (main push only). Release path uses `softprops/action-gh-release@v2`, `generate_release_notes: true`, `draft: false`, `prerelease: false`, attaches aide-*, npm tarball, checksums.txt. Snapshot path force-deletes and recreates the `snapshot` tag/release. `npm publish --provenance --access public` runs on tag push.

### Tag-triggered cross-compile + asset upload

Build matrix is OS × architecture for binary builds: linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64, windows/arm64 — six platforms per binary; same matrix for `aide`, `aide-web`, and grammar shared libraries. CGO + zig cross-compile; zig downloaded from `ziglang.org/builds/...` with `curl` inside each step. UPX compression via `svenstaro/upx-action@v2 --best --lzma` on Linux and Windows-amd64 only (skipping darwin and windows-arm64 where UPX doesn't work reliably).

### Auto-generated release notes from commits

`generate_release_notes: true` delegates to GitHub's auto-generator; no CHANGELOG.md in the repo.

## Documentation surface

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` at repo root (~11KB) — consumer-facing with install instructions for Claude Code / OpenCode / Codex CLI, feature table, skills table, env-var reference, CLI reference, advanced install notes, troubleshooting, and link to the hosted docs site. `ARCHITECTURE.md` at repo root (uppercase) plus `docs/docs/reference/architecture.md` for the Docusaurus site (5KB) — two architecture sources of truth. No `CHANGELOG.md` (404s at both root and plugin-root paths); release notes generated from commits at tag time.

### Nested `docs/` tree with map in README

Docusaurus site mirrors much of the in-repo documentation — two sources of truth for architecture, MCP tool list, and storage layout. `docs/versioned_docs/version-0.0.{59,60,61}/` directories per release. Subsystem READMEs for contributors: `aide/README.md` (Go CLI), `adapters/README.md` (adapter architecture), `adapters/opencode/README.md`.

### No CLAUDE.md

No `CLAUDE.md` at repo root.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` present at repo root (MIT), SPDX `MIT` in plugin manifests. Single agreement across files.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` (all 404). `LICENSE` present.

## Source layout

### Single tree (plugin equals repo)

Repo root is the plugin (`source: "./"`). Same TypeScript core under `src/core/` is packaged as (a) Claude Code marketplace plugin (this repo), (b) OpenCode npm package (`@jmylchreest/aide-plugin` via `packages/opencode-plugin/`), (c) Codex CLI install target (via `bunx @jmylchreest/aide-plugin install --platform codex`). `src/opencode/` adapts core; `src/cli/` drives the npm install flow for non-Claude-Code consumers. A single plugin root directory serving three different AI-coding-assistant ecosystems — adapters share core rather than duplicating, so the plugin and the multi-target product live in one tree.

## Cross-ecosystem distribution

### Cross-ecosystem multi-harness distribution

Plugin ships to Claude Code, OpenCode, and Codex CLI from the same source tree. The TS core is shared; per-host adapters (`src/opencode/`, npm CLI install path for Codex) wrap the core. The Bun runtime is a hard prerequisite across all three hosts (`#!/usr/bin/env bun` shebang, `Bun.sleepSync` lock-poll). README states: "**Prerequisite:** Bun — the only runtime dependency."

### Dual-distribution: marketplace + npm

`@jmylchreest/aide-plugin` is published to npm with `npm publish --provenance --access public` on tag push. The npm package is the entry point for OpenCode/Codex CLI users; Claude Code consumers use the marketplace.

## Cross-platform discipline

### Mixed shebangs partitioned by criticality

The plugin's runtime path uses `#!/usr/bin/env bun` (`bin/aide-wrapper.ts`, `scripts/aide-hud.ts`, `scripts/aide-hud-wrapper.ts`, `scripts/validate-skills.ts`); `adapters/opencode/generate.ts` uses `#!/usr/bin/env npx tsx` (different runtime). Bun shared for runtime path; not universal even within the repo.

### Documented Windows-native migration

Wrapper branches on `process.platform === "win32"` for `.exe` suffix and skips execute-bit check on Windows. Downloader builds GOOS/GOARCH-specific binary names (`aide-${goos}-${goarch}${ext}`) with `x64` → `amd64` translation. Cross-platform support across Linux/macOS/Windows.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code under `${CLAUDE_PLUGIN_ROOT}` (or `${AIDE_PLUGIN_ROOT}` when set); project-local state under `<cwd>/.aide/`. The Go binary and node_modules go into the plugin tree (`bin/aide[.exe]`, `node_modules/`); per-project memory and logs live in `.aide/`.

## Plugin-runtime root resolution

### Three-tier with hardcoded data-dir terminal fallback

`AIDE_PLUGIN_ROOT` > `CLAUDE_PLUGIN_ROOT` > `realpathSync(SCRIPT_DIR/..)`. Script-dir resolution uses `realpathSync` so a `node_modules/.bin/aide-wrapper` symlink resolves to the real package dir. The third priority is the script-relative fallback for direct invocation.

## PATH augmentation and host-project setup

### None (plugin operates standalone)

Plugin operates without modifying user `PATH` (the HUD wrapper installation at `~/.claude/bin/aide-hud.ts` is for Claude Code's status-line integration, not user shell PATH). MCP launch and hooks resolve via `${CLAUDE_PLUGIN_ROOT}` directly.

## Cross-role tools

### Bun

Bun is the runtime for the wrapper, hook scripts, and validator scripts. Hard prerequisite — `Bun.sleepSync` and `bun` shebang make Node a non-substitute even when the underlying download path supports `.js`.

### Node + npm + npx

`packages/opencode-plugin/` is published to npm; Codex CLI consumers install via `bunx @jmylchreest/aide-plugin install --platform codex`. `npm publish --provenance --access public` fires on tag push.

### `${CLAUDE_PLUGIN_ROOT}` env var

Used in `plugin.json`'s MCP server command (`bun ${CLAUDE_PLUGIN_ROOT}/bin/aide-wrapper.ts mcp`) and as the second-precedence root resolution in the wrapper.

### Git as state substrate

Tag-on-main lifecycle; `git describe --tags --match 'v*' --always --long` synthesizes the dev-build version string in `release.yml`. The `snapshot` floating tag is force-recreated on every main push.

### GitHub Releases

Release artifacts (per-platform binaries, npm tarball, checksums.txt) attached via `softprops/action-gh-release@v2`. Snapshot release rebuilt on every main push.

### `softprops/action-gh-release@v2`

Used for both tagged releases and the snapshot release.

## Source-pin maintenance

### Registration-list drift guard

Wrapper reads version from `.claude-plugin/plugin.json` first then `package.json`; downloader reads from `package.json` first. Two version sources accessed in different orders by different callers — the `Makefile` `release` target `sed`-syncs the four files at release time but no commit-time validation.
