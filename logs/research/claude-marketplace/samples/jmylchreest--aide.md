# jmylchreest/aide

## Identification

- **URL**: https://github.com/jmylchreest/aide
- **Stars**: 6
- **Last commit date**: 2026-04-20 (default branch `main`, commit `b66fe3b`)
- **Default branch**: main
- **License**: MIT
- **Sample origin**: bin-wrapper (observed shebang `#!/usr/bin/env bun` at `bin/aide-wrapper.ts`; also carries primary plugin payload, dep-install logic, SessionStart binary-download behaviour, and CI/release automation)
- **One-line purpose**: "AI Development Environment — Multi-agent orchestration for Claude Code" (from `plugin.json` / marketplace description; README calls it "Persistent memory, code intelligence, and multi-agent orchestration for AI coding assistants. Works with Claude Code, OpenCode, and Codex CLI.")

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: top-level `description` and `owner` (no `metadata.{...}` wrapper). No top-level `version` or `pluginRoot`.
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `category` (`productivity`) + `tags` (`["multi-agent","orchestration","automation"]`). No `keywords`. Single plugin.
- **`$schema`**: present — `"https://anthropic.com/claude-code/marketplace.schema.json"`
- **Reserved-name collision**: no — plugin name is `aide` (not a reserved term)
- **Pitfalls observed**: marketplace-entry `tags` and the `topics` set on the GitHub repo (17 topics: `ai`, `claude-code`, `mcp`, `skills`, etc.) are disjoint. The marketplace entry narrows heavily while the repo advertises broader discoverability; a consumer reading only `marketplace.json` sees far fewer hints than the repo surface.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./"`) — single plugin lives at repo root
- **`strict` field**: absent (default — implicit true)
- **`skills` override on marketplace entry**: absent
- **Version authority**: both `plugin.json` and the marketplace entry carry `"version": "0.0.61"` verbatim — drift risk if only one is updated. `Makefile`'s `release` target does a `sed` across a `VERSION_FILES` list (`package.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `packages/opencode-plugin/package.json`) to keep them in sync, and `release.yml`'s `prepare` job injects version via `-ldflags` into the Go binary — so the discipline to keep the duplicates aligned is Makefile-driven, not structural.
- **Pitfalls observed**: four separate files carry the plugin version number (two plugin manifests + two package.json files); nothing verifies them against each other at commit time (only the Makefile target enforces it, and only when invoked).

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via `@ref` if they want a specific commit; the only "channel" artifact is a floating `snapshot` GitHub release that the release workflow rewrites on every push to `main` (`gh release delete snapshot --yes` → recreate with `prerelease: true`). That's a binary-distribution channel (used by the wrapper's fallback URL), not a marketplace/plugin channel — plugin itself is single-track.
- **Channel-pinning artifacts**: absent at the marketplace level. At the binary-artifact level: versioned URL (`releases/download/v<plugin-version>/<binary>`) is tried first, then `releases/latest/download/<binary>` as fallback (race-condition mitigation per `getDownloadUrls` comment).
- **Pitfalls observed**: none specific to plugin channeling — but the "dev build vs release build" version distinction (`0.0.X-dev.N+sha` on main snapshots vs `0.0.X` on tags) only surfaces inside the binary wrapper's version-compare logic, not at the marketplace layer. Marketplace consumers always see the same `0.0.61`.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main (release workflow triggers on `push: tags: ['v*']`, and the `prepare` job explicitly detects "commit already has release tag" to skip the snapshot build). `git tag --points-at HEAD` is how releases are distinguished from snapshots on the same commit.
- **Release branching**: none — tag-on-main pattern
- **Pre-release suffixes**: none on tags themselves (tags are plain `v0.0.61`, `v0.0.60`, ...). Dev builds on `main` synthesize a `-dev.N+sha` suffix for the Go binary version string only, never applied as a git tag (the only non-semver tag is the floating `snapshot`).
- **Dev-counter scheme**: present but only inside the Go binary's embedded version string via ldflags. Shape is `{major}.{minor}.{next_patch}-dev.{commits-since-tag}+{sha7}` — computed on the fly by `git describe --tags --match 'v*' --always --long` in `release.yml`'s `prepare` job. The `plugin.json` `version` field does NOT dev-bump; it tracks release semver only.
- **Pre-commit version bump**: no (no pre-commit hook observed; version bumps are explicit via `make release` which bumps → commits → tags in one target)
- **Pitfalls observed**: the `snapshot` tag is force-recreated on every push to main (`git push origin :refs/tags/snapshot` then push). Any consumer caching by tag SHA against `snapshot` will see silent moves. Also, `plugin.json`'s version drifts behind the Go binary's reported version between releases — the wrapper handles this with an `isDevBuild` branch that accepts `base >= plugin` as "use local build."

## 5. Plugin-component registration

- **Reference style in plugin.json**: inline config objects. `mcpServers` is an inline object (no external `.mcp.json`), and `hooks` is an inline object with ten event groupings. No `skills`, `commands`, or `agents` fields (those are discovered by path convention — `skills/**/SKILL.md`, `src/agents/*.md`).
- **Components observed**:
  - skills: yes (25 built-in under `skills/<name>/SKILL.md`: `assess-findings`, `autopilot`, `build-fix`, `code-search`, `context-usage`, `debug`, `decide`, `design`, `docs`, `forget`, `git`, `implement`, `memorise`, `patterns`, `perf`, `plan-swarm`, `recall`, `review`, `semgrep`, `survey`, `swarm`, `test`, `verify`, `worktree-resolve`, `memorise`)
  - commands: no (none observed)
  - agents: yes, but not via `.claude-plugin/agents/` — authored under `src/agents/*.md` (9 files: `architect`, `designer`, `executor`, `explore`, `planner`, `qa-tester`, `researcher`, `reviewer`, `writer`). These appear to be agent definitions consumed by the swarm skill rather than plugin-registered sub-agents.
  - hooks: yes (inline in `plugin.json` — 10 event types, 17 total hook registrations, all invoking bun+TS scripts under `src/hooks/`)
  - .mcp.json: no (MCP config inline in `plugin.json`)
  - .lsp.json: no
  - monitors: no (no `monitors.json`)
  - bin: yes (`bin/aide-wrapper.ts` — single wrapper, launched by the MCP server command)
  - output-styles: no
- **Agent frontmatter fields used**: on `src/agents/*.md` — `name`, `description`, `defaultModel` (values like `balanced`), `readOnly` (boolean), `tools` (array of plain tool names). Example (`executor.md`): `tools: [Read, Glob, Grep, Edit, Write, Bash, TodoWrite, lsp_diagnostics, lsp_diagnostics_directory]`. These are agent definitions consumed internally by the swarm skill's orchestration logic — NOT plugin-registered Claude Code sub-agents (no `.claude-plugin/agents/` directory, no `agents` field in `plugin.json`).
- **Agent tools syntax**: plain tool names (not permission-rule syntax). Mixes Claude Code built-in names with aide-specific MCP tool names (`lsp_diagnostics*`).
- **Pitfalls observed**: the `src/agents/` files look like Claude Code agent definitions (same frontmatter shape) but aren't wired as plugin agents. A reader scanning directories for agent definitions could mistake them for plugin-registered agents; the actual consumer is the swarm skill's workflow code. Skill frontmatter also diverges from Claude's convention — skills use a `triggers: [...]` array (fuzzy-matched by `src/core/skill-matcher.ts`), not solely `description` — and some add `platforms: [...]`.

## 6. Dependency installation

- **Applicable**: yes — non-trivial, two parallel dependency chains (npm via Bun for TS hooks, GitHub-release binary download for the Go core)
- **Dep manifest format**: `package.json` (root) with Bun as declared engine (`"engines": {"bun": ">=1.0.0"}`); `bun.lock` checked in. Also `aide/go.mod` + `aide-web/go.mod` (Go workspace via `go.work`) — but these are build-time for contributors, not consumer-install deps.
- **Install location**:
  - Node deps: `${CLAUDE_PLUGIN_ROOT}/node_modules` (self-healed by the wrapper — see below)
  - Go binary: `${CLAUDE_PLUGIN_ROOT}/bin/aide[.exe]` (downloaded on demand from GitHub releases)
  - Project-local project state: `<cwd>/.aide/` (created by SessionStart hook)
- **Install script location**: no SessionStart-registered installer. Install logic is split:
  - `bin/aide-wrapper.ts` runs `ensureDependencies()` at every MCP launch — detects missing `node_modules` and runs `bun install --frozen-lockfile` inline (rationale in the code comment: "After a Claude Code marketplace autoUpdate (git pull), node_modules/ may be missing since it's gitignored"). Lazy `require('cross-spawn')` is used for the download step to survive the bootstrap case where node_modules is still empty.
  - `src/lib/aide-downloader.ts` handles the Go binary — invoked by the wrapper when `binaryExists()` is false or `versionGte(binary, plugin)` fails.
- **Change detection**: existence + version comparison (not hash-based):
  - Node: existence of `node_modules` directory
  - Binary: existence + `aide version` output parsed with regex + `versionGte` SemVer compare. Dev builds (`-dev.` in version) compare base semver; release builds require exact-or-newer match.
- **Retry-next-session invariant**: wrapper unlinks stale binary before re-downloading (`Removing outdated binary before download`); cross-platform `mkdir`-based lock (`bin/.aide-download.lock/pid`) with 60s timeout + forced-remove fallback on timeout. Node install failures log warning but don't hard-fail.
- **Failure signaling**: mixed. Wrapper writes human-readable `stderr` log lines AND appends to `.aide/_logs/wrapper.log`; exits with `process.exit(1)` if downloader fails or binary missing post-download. Node install failure logs warning and continues (soft-fail). SessionStart hook catches all exceptions at the top level and always emits `{"continue": true}` to stdout — explicit fail-open posture (`uncaughtException` / `unhandledRejection` handlers call `outputContinue()` and `process.exit(0)`).
- **Runtime variant**: mixed — Node bun (TS compilation + hook runtime) + Go binary download. Bun is the only documented prerequisite; README: "**Prerequisite:** Bun — the only runtime dependency. The Go binary downloads automatically."
- **Alternative approaches**: none used internally (no `uvx`, no PEP 723, no pointer-file pattern). The wrapper-plus-downloader is the pattern.
- **Version-mismatch handling**: explicit. The wrapper distinguishes dev builds (`version.includes("-dev.")`) from release builds: dev builds are accepted if their base semver is `>=` plugin version; release builds must be `>=` plugin version exactly or trigger redownload. Plugin-version source is `.claude-plugin/plugin.json` (primary) with `package.json` fallback. `getDownloadUrls()` returns two URLs (versioned, then `latest`) specifically to mitigate the race where the marketplace pulls the new plugin version before the release action has finished uploading binary artifacts.
- **Pitfalls observed**: multiple. (1) `node_modules` is gitignored so a fresh clone (or Claude Code's `autoUpdate` pull) leaves the plugin unable to import its own npm deps; the wrapper's `ensureDependencies()` self-heal depends on Bun being installed and on the `bun.lock` being current. (2) The MCP server command in `plugin.json` is `bun ${CLAUDE_PLUGIN_ROOT}/bin/aide-wrapper.ts mcp` — Bun on user PATH is a hard prerequisite; no availability check with a graceful error message if Bun is missing. (3) Binary-download lock uses `mkdir` for atomicity and relies on `Bun.sleepSync` (not `node:`), binding the wrapper to Bun. (4) The wrapper falls back to `dist/lib/aide-downloader.js` when `src/lib/aide-downloader.ts` is absent — this is for npm-installed consumers of the `@jmylchreest/aide-plugin` package, not the marketplace plugin path.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — single `bin/` file acting as a launcher and downloader
- **`bin/` files**: `bin/aide-wrapper.ts` — a TypeScript launcher invoked via `bun` that (1) self-heals `node_modules` if missing, (2) verifies a Go `aide` binary exists at `bin/aide[.exe]`, (3) downloads/version-checks via `src/lib/aide-downloader.ts`, (4) forwards argv to the Go binary via `spawnSync` with `stdio: "inherit"` and exits with its status
- **Shebang convention**: `#!/usr/bin/env bun` — the only observed Bun shebang in the sample. Other `.ts` scripts in the repo: `scripts/aide-hud.ts` and `scripts/aide-hud-wrapper.ts` also use `#!/usr/bin/env bun`; `scripts/validate-skills.ts` uses `#!/usr/bin/env bun`; `adapters/opencode/generate.ts` uses `#!/usr/bin/env npx tsx` (different runtime). So Bun is the shared runtime for the plugin's runtime path but not universal even within the repo.
- **Runtime resolution**: precedence `AIDE_PLUGIN_ROOT` > `CLAUDE_PLUGIN_ROOT` > `SCRIPT_DIR/..` (script-relative fallback). Script-dir resolution uses `realpathSync` so a `node_modules/.bin/aide-wrapper` symlink resolves to the real package dir. The `AIDE_PLUGIN_ROOT` fallback is "canonical, platform-agnostic" per the wrapper's header comment — it exists because this same wrapper also ships to OpenCode/Codex CLI consumers who don't set `CLAUDE_PLUGIN_ROOT`.
- **Venv handling (Python)**: not applicable — no Python surface
- **Platform support**: cross-platform (Linux/macOS/Windows). Branches on `process.platform === "win32"` for `.exe` suffix and skips execute-bit check on Windows. Downloader builds GOOS/GOARCH-specific binary names (`aide-${goos}-${goarch}${ext}`) with `x64` → `amd64` translation.
- **Permissions**: not directly observed (no blob-mode query done), but the wrapper relies on `execFileSync(BINARY, ["version"])` for executability checking post-download, with Windows skipping the exec check. The wrapper script itself is invoked via `bun <path>` in `plugin.json`, so its exec bit is irrelevant. Downloader chmods the binary after writing (seen in the `chmodSync` import in `aide-downloader.ts` — full body elided but the `chmodSync` is part of the download path).
- **SessionStart relationship**: hook lazily ensures binary before use — SessionStart hook (`src/hooks/session-start.ts`) calls `ensureAideBinary(cwd)` early in its `main()`, which triggers the same download path as the MCP wrapper. So two independent invocations can both discover-missing-and-download, synchronised by the `mkdir`-based lock. The wrapper is the primary trigger (MCP launch); SessionStart is a secondary safety net.
- **Pitfalls observed**: (1) The wrapper has to assume Bun is installed since its own shebang is `#!/usr/bin/env bun`; no graceful-degradation path. (2) Script-dir fallback (`SCRIPT_DIR/..`) is the third priority — if a user invokes the wrapper directly, `PLUGIN_ROOT` resolves to `bin/..` which is the plugin root for an in-tree install but wrong if someone installed just `bin/` somewhere. (3) The `bin/.aide-download.lock` directory relies on `rmdirSync` after `unlinkSync` of the PID file — stale locks from crashed processes are only force-removed after the 60s timeout, so a fast SessionStart invocation after a crash can block up to a minute.

## 8. User configuration

- **`userConfig` present**: no (no `userConfig` field in `plugin.json`)
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not observed. Configuration is via environment variables (documented in README — `AIDE_DEBUG`, `AIDE_FORCE_INIT`, `AIDE_CODE_WATCH`, `AIDE_CODE_WATCH_DELAY`, `AIDE_MEMORY_INJECT`, `AIDE_MEMORY_SCORING_DISABLED`, `AIDE_MEMORY_DECAY_DISABLED`, `AIDE_SHARE_AUTO_IMPORT`, plus `AIDE_PLUGIN_ROOT` for plugin-root override). `plugin.json` hard-codes `AIDE_CODE_WATCH=1` and `AIDE_CODE_WATCH_DELAY=30s` in the MCP `env` block — not user-configurable through the plugin manifest.
- **Pitfalls observed**: user-facing configuration is entirely out-of-band (env vars), not registered in `plugin.json`. A user discovering the plugin via `claude plugin install` cannot learn the knobs without reading the README. Claude Code's marketplace UX has no way to surface any of it.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 5 hooks, matcher `*` on all. `tool-tracker.ts` (per-agent current-tool tracking for HUD), `write-guard.ts` (write protection), `pre-tool-enforcer.ts` (read-only mode / agent tool-access rules), `context-guard.ts` (context-window pressure), `search-enrichment.ts` (augment search tool inputs).
- **PostToolUse hooks**: 4 hooks, matcher `*`. `tool-observe.ts` (record tool events for memory), `hud-updater.ts` (status line refresh), `comment-checker.ts` (validate that edits don't strip comments), `context-pruning.ts`.
- **PermissionRequest/PermissionDenied hooks**: `src/hooks/permission-handler.ts` exists with a header comment `OPT-IN: This hook is NOT registered in plugin.json by default. To enable, add a PermissionRequest entry to .claude-plugin/plugin.json. Not available in OpenCode (no equivalent event).` So: present in source, absent in manifest.
- **Output convention**: stdout JSON (all hooks output `JSON.stringify({continue: true/false, ...})` to stdout). Human-readable logs go to `.aide/_logs/*.log` files (via the `Logger` class in `src/lib/logger.ts`) AND to stderr via `process.stderr.write`. `debug(SOURCE, msg)` from `../lib/logger.js` is the standard trace call.
- **Failure posture**: fail-open, documented via centralized helpers. `session-start.ts` installs global `process.on('uncaughtException')` + `process.on('unhandledRejection')` handlers that call `outputContinue()` (emits `{"continue":true}`) and `process.exit(0)`. A `try { ... } catch {}` pattern wraps the main logic in every hook inspected (`session-start.ts`, `skill-injector.ts`, `pre-tool-enforcer.ts`). `pre-tool-enforcer.ts` and `permission-handler.ts` DO return `continue: false` with a `message` when the enforcement evaluator explicitly denies, so fail-open applies to unexpected errors, not to deliberate denials.
- **Top-level try/catch wrapping**: observed in every hook sampled (3/3). `main()` is inside a `try { await readStdin(); ... } catch { outputContinue(); }` pattern in `session-start.ts`; similar in `skill-injector.ts` and `pre-tool-enforcer.ts`.
- **Pitfalls observed**: (1) 17 hook registrations all with matcher `"*"` means every tool invocation spawns multiple bun processes — latency cost is real (timeouts set at 2–60s per hook). (2) `permission-handler.ts` is in source but dormant — a consumer looking for permission enforcement by grepping hook registrations won't find it unless they also read the file header comment. (3) Hooks write JSON to stdout AND log to stderr AND to `.aide/_logs/` files — three separate channels, with "hook crashes = stdout still valid JSON" being the invariant. Any hook that writes plain text to stdout will break the harness.

## 10. Session context loading

- **SessionStart used for context**: yes (primary). `session-start.ts` runs `coreBuildWelcomeContext(state, memories, notices)` and emits it in `hookSpecificOutput.additionalContext`. Also does binary check, MCP sync, HUD-wrapper install, directory init, config load, stale-state cleanup, and session-init call to the `aide` binary (which returns memories to inject).
- **UserPromptSubmit for context**: yes. `skill-injector.ts` fuzzy-matches the user prompt against YAML-frontmatter `triggers` in `skills/**/SKILL.md` + `.aide/skills/**/*.md`, picks up to 3, and returns content in `hookSpecificOutput.additionalContext`. Emphatically UserPromptSubmit-gated, not SessionStart.
- **`hookSpecificOutput.additionalContext` observed**: yes, in both SessionStart and UserPromptSubmit paths (visible in the `HookOutput` interfaces for both hook files)
- **SessionStart matcher**: `"*"` (fires on all SessionStart sub-events — startup/clear/compact/resume all share the same handler). The hook does not internally discriminate on a session-type field.
- **Pitfalls observed**: (1) The SessionStart hook's 60-second timeout exists because the binary-download path can hit network latency, UPX decompression on first run, etc. (2) Skill-discovery layers are ordered `.aide/skills/` > `skills/` > plugin-bundled > `~/.aide/skills/` — per README. Fuzzy-match tolerates typos, so unintended skill activation is possible; skills attempt to mitigate by scoping triggers (arrays of 3-10 short phrases). (3) The hook installs a HUD wrapper into `~/.claude/bin/aide-hud.ts` during SessionStart — a side-effect on the user's home directory that isn't mentioned anywhere in `plugin.json` or marketplace metadata.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: AIDE does run a live HUD/status-line system (`scripts/aide-hud.ts` → `~/.claude/bin/aide-hud.ts` + `hud-updater.ts` PostToolUse hook writes to `.aide/state/hud.txt`), but this is implemented via hook-driven file writes + a Claude Code status-line integration, not via `monitors.json`. A consumer looking for monitor-based live updates won't find any; the equivalent is implemented at a different layer.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace with bare semver tags (`v0.0.61`)
- **Pitfalls observed**: none — no cross-plugin coupling attempted

## 13. Testing and CI

- **Test framework**: multiple. Vitest (TS, under `src/test/*.test.ts` and `tests/*.test.ts`), Go `testing` (Go, `*_test.go` throughout `aide/` and `aide-web/`). The integration-test section in `ci.yml` uses bash plus `jq` to drive hook scripts with stdin JSON.
- **Tests location**: mixed. TypeScript tests split across `src/test/` (unit tests, co-located with source) and `tests/` (at repo root — contains `tests/memory-capture.test.ts`). Go tests inline next to sources (`aide/pkg/.../foo_test.go`).
- **Pytest config location**: not applicable (no Python)
- **Python dep manifest for tests**: not applicable
- **CI present**: yes
- **CI file(s)**: `.github/workflows/ci.yml` (5KB), `.github/workflows/release.yml` (28KB), `.github/workflows/docs.yml` (1.8KB), `.github/workflows/docs-version.yml` (3.5KB)
- **CI triggers**: `ci.yml` — `push: branches: [main]` + `pull_request: branches: [main]`. `release.yml` — `push: branches: [main], tags: ['v*']` + `pull_request: branches: [main]`. `docs.yml` — `push: branches: [main], paths: [docs/**, .github/workflows/docs.yml]` + `workflow_dispatch` + `workflow_call`. `docs-version.yml` — `workflow_dispatch` only.
- **CI does**: much. `ci.yml` has five jobs: (1) `typescript` — `bun install` + `bunx tsc --noEmit` + `bun run build` + `bunx vitest run --exclude='tests/memory-capture.test.ts'` + `bun run lint`; (2) `go` — `go test -v -race -coverprofile=coverage.out ./...` in `aide/`, uploads to Codecov; (3) `go-web` — same in `aide-web/`, plus builds the Astro frontend first (`bun install --frozen-lockfile && bun run build` in `aide-web/web/`); (4) `go-lint` — `golangci-lint-action@v9`; (5) `build` — rebuilds TS, Go `aide`, Go `aide-web`, verifies binaries with `--help`, uploads linux-amd64 artifacts with 1-day retention; (6) `integration` — depends on `build`, drives hooks with piped JSON (`echo '{"hook_event_name":..."}' | bun dist/hooks/skill-injector.js | jq -e '.continue == true'`) and runs a real `./bin/aide memory add/list` round-trip.
- **Matrix**: OS × architecture for binary builds in `release.yml` (linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64, windows/arm64 — six platforms per binary; same matrix for `aide`, `aide-web`, and grammar shared libraries). CI proper (`ci.yml`) does not matrix — Ubuntu-only.
- **Action pinning**: tag-pinned (`actions/checkout@v6`, `oven-sh/setup-bun@v2`, `actions/setup-go@v6`, `actions/upload-artifact@v6`, `actions/download-artifact@v8`, `actions/setup-node@v6`, `softprops/action-gh-release@v2`, `codecov/codecov-action@v5`, `golangci/golangci-lint-action@v9`, `svenstaro/upx-action@v2`, `actions/upload-pages-artifact@v4`, `actions/deploy-pages@v4`). No SHA pins. Uses current major versions uniformly — recent upgrade lineage visible (`@v6` is the current actions/checkout major).
- **Caching**: built-in `setup-go@v6` with `cache: true` and `cache-dependency-path: aide/go.sum`; `setup-node@v6` with `cache: npm`. `setup-bun@v2` does its own caching. No explicit `actions/cache` usage.
- **Test runner invocation**: direct — `bunx vitest run --reporter=verbose --exclude='tests/memory-capture.test.ts'` for TS; `go test -v -race ./...` for Go. Integration tests use inline bash. The `memory-capture.test.ts` file is explicitly excluded from CI (runs only locally).
- **Pitfalls observed**: (1) `tests/memory-capture.test.ts` excluded without an inline reason — readers have to infer it's an "interactive or real-system" test. (2) CI runs on push-to-main AND pull-requests-to-main, meaning PRs that merge to main get tested twice (pre-merge + post-merge on main). (3) `release.yml` also triggers on `pull_request` but its build jobs gate on `github.event_name == 'push'`, so PRs only run the `test` subset — subtle but intentional. (4) Codecov upload is `continue-on-error: true`, so rate-limit failures don't break CI.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes
- **Release trigger**: multi-trigger — `push: branches: [main], tags: ['v*']` + `pull_request: branches: [main]`. The single workflow handles PR CI, main-branch snapshots, and tag releases by gating jobs on `needs.prepare.outputs.is_release` and `github.event_name == 'push'`.
- **Automation shape**: Go + npm dual-publish, plus grammar shared-library build + OpenCode plugin npm package. Jobs (in dependency order): `prepare` (computes version) → `test` → `build` (aide, 6 platforms, CGO+zig cross-compile, UPX compression except darwin/windows-arm64) + `build-web` (aide-web, same 6 platforms) + `build-grammars` (tree-sitter grammars per-language .so/.dylib/.dll, 6 platforms, clones upstream grammar repos at pinned tags via `scripts/generate-grammar-matrix.sh --print`) + `build-npm` (OpenCode plugin tarball) → `release` (tag push only — `softprops/action-gh-release@v2`, `generate_release_notes: true`, draft: false, prerelease: false, attaches aide-*, npm tarball, checksums.txt) + `publish-npm` (tag push only — `npm publish --provenance --access public`) OR `snapshot` (main push only — deletes + recreates the `snapshot` tag + prerelease: true).
- **Tag-sanity gates**: `prepare` job includes a "commit already has release tag — skip" check (`git tag --points-at HEAD | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$'`) that prevents running the snapshot path on a commit that's being released. Tag-format regex is checked implicitly by the trigger (`tags: ['v*']`). No explicit "tag matches package.json version" check — version comes from the tag when releasing (`VERSION="${GITHUB_REF_NAME#v}"`). The `Makefile`'s `check-release-needed` target enforces clean tree and HEAD != latest tag at `make release` time (local, not CI).
- **Release creation mechanism**: `softprops/action-gh-release@v2` for both tagged releases and snapshots
- **Draft releases**: no (`draft: false` explicit in both release and snapshot paths)
- **CHANGELOG parsing**: no — `generate_release_notes: true` delegates to GitHub's auto-generator. No CHANGELOG.md in the repo.
- **Pitfalls observed**: (1) The release workflow is 28KB of YAML across 7+ jobs; reasoning about paths requires careful reading. (2) Zig is downloaded from `ziglang.org/builds/...` with `curl` inside each cross-compile step — external dependency on the Zig CDN at build time. (3) `npm publish --provenance` requires `id-token: write` permission (present) and `NPM_TOKEN` secret. (4) Snapshot release force-deletes and recreates the `snapshot` tag + release on every main push — consumers referencing the tag see it move. (5) Grammar build step clones upstream tree-sitter grammars from GitHub at pinned tags; a deleted/renamed grammar repo upstream silently warns-and-continues (`WARNING: Failed to clone ... skipping`).

## 15. Marketplace validation

- **Validation workflow present**: no dedicated marketplace-validation workflow. `scripts/validate-skills.ts` exists as a skill linter (run via `bun run scripts/validate-skills.ts`) that validates SKILL.md frontmatter (required `name`, `description`, `triggers`; non-empty triggers array; no duplicate names; markdown-structure sanity). Not wired into CI on the surface I sampled.
- **Validator**: bun+custom (no zod, no Claude Code CLI validation). The validator has its own inline YAML-frontmatter parser rather than depending on a YAML library.
- **Trigger**: manual (`bun run scripts/validate-skills.ts`) — no CI job invokes it
- **Frontmatter validation**: yes (for skills only; not for agents, not for marketplace.json or plugin.json)
- **Hooks.json validation**: no
- **Pitfalls observed**: (1) The skill validator is manual — nothing prevents merging a broken SKILL.md. (2) No validation at all for marketplace.json / plugin.json; a typo in those files reaches users unless Claude Code's install-time parser catches it.

## 16. Documentation

- **`README.md` at repo root**: present — 11KB, consumer-facing, with install instructions for Claude Code / OpenCode / Codex CLI, feature table, skills table, env-var reference, CLI reference, advanced install notes, troubleshooting, and link to the hosted docs site
- **Owner profile README at `github.com/jmylchreest/jmylchreest`**: present (~67 lines, resume-tier portfolio — auto-generated repo list with stars/downloads)
- **`README.md` per plugin**: not applicable — single plugin, same README. Subsystem READMEs exist for contributors: `aide/README.md` (Go CLI), `adapters/README.md` (adapter architecture), `adapters/opencode/README.md`.
- **`CHANGELOG.md`**: absent — 404s at both root and plugin-root paths. Release notes generated from commits at tag time (GitHub auto-notes).
- **`architecture.md`**: present as `ARCHITECTURE.md` at repo root (uppercase — unusual). Also `docs/docs/reference/architecture.md` for the Docusaurus site.
- **`CLAUDE.md`**: absent
- **Community health files**: none observed (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` all 404). `LICENSE` present.
- **LICENSE**: present (MIT, SPDX: `MIT`)
- **Badges / status indicators**: not observed in README (first 11KB scan showed none)
- **Pitfalls observed**: (1) `ARCHITECTURE.md` uppercase isn't the common convention (most projects use `architecture.md` lowercase). (2) Docusaurus site mirrors much of the in-repo documentation — two sources of truth for architecture, MCP tool list, and storage layout. The Docusaurus version lags behind (`docs/docs/reference/architecture.md` is 5KB vs the 5.9KB root `ARCHITECTURE.md`), with snapshotted `docs/versioned_docs/version-0.0.{59,60,61}/` directories per release. (3) No CHANGELOG forces anyone investigating a regression to walk tags and compare auto-generated release notes.

## 17. Novel axes

- **Multi-consumer plugin surface** — same codebase is packaged as (a) Claude Code marketplace plugin (this repo), (b) OpenCode npm package (`@jmylchreest/aide-plugin` via `packages/opencode-plugin/`), (c) Codex CLI install target (via `bunx @jmylchreest/aide-plugin install --platform codex`). The TypeScript core under `src/core/` is shared; `src/opencode/` adapts it; `src/cli/` drives the npm install flow for non-Claude-Code consumers. A single plugin root directory serving three different AI-coding-assistant ecosystems.
- **Go binary as separate artifact, not bundled** — The Go-compiled `aide` CLI is downloaded on demand from GitHub releases rather than included in the git tree (only the TS wrapper ships in the plugin). This keeps the marketplace plugin small (~2.6MB repo) at the cost of a first-run network dependency. Compared to plugins that vendor binaries or ship pure scripts, this is a distinct third pattern: "plugin is a thin wrapper that fetches its own native bits."
- **Cross-platform binary compression via UPX** — `release.yml` runs `svenstaro/upx-action@v2 --best --lzma` on Linux and Windows-amd64 binaries (skipping darwin and windows-arm64 where UPX doesn't work reliably). Reduces download size for the first-run fetch.
- **Tree-sitter grammars as separately-downloadable release artifacts** — Each supported language's tree-sitter grammar is compiled into a platform-specific shared library (`aide-grammar-<name>-<version>-<os>-<arch>.tar.gz`) as a separate GitHub release artifact. The Go binary dynamically loads these at runtime via `aide/pkg/grammar/dynamic.go`. Grammar build matrix clones upstream grammar repos at pinned tags; a lockfile (`.aide-grammars.lock`) tracks the pins.
- **Skill trigger-array with fuzzy matching** — Skills declare `triggers: [phrase1, phrase2, ...]` (up to ~10 short phrases each). The `UserPromptSubmit` hook fuzzy-matches (typo-tolerant: "desgin" → "design") and injects up to 3 matching skills' content into `additionalContext`. This is a skill-activation pattern distinct from Claude Code's built-in `description`-based activation; it layers on top rather than replacing.
- **HUD wrapper installation pattern** — SessionStart hook installs `~/.claude/bin/aide-hud.ts` (a Bun-shebang script that discovers the newest installed plugin version under `~/.claude/plugins/cache/*/aide/*/scripts/aide-hud.ts` and delegates). This decouples user-facing HUD from plugin upgrades — new plugin versions provide new HUD scripts, the wrapper always finds the newest. A side-effect on the user's home directory performed by the plugin at session-start, not a declared component.
- **`AIDE_PLUGIN_ROOT` env var as canonical root** — The wrapper reads `AIDE_PLUGIN_ROOT` FIRST, before `CLAUDE_PLUGIN_ROOT`. Rationale in the header comment: "canonical, platform-agnostic" — the same wrapper ships to OpenCode/Codex CLI where `CLAUDE_PLUGIN_ROOT` is not set. This is the plugin treating `CLAUDE_PLUGIN_ROOT` as a Claude-Code-specific fallback rather than the primary.
- **Dual-source version inference** — Wrapper reads version from `.claude-plugin/plugin.json` first, then falls back to `package.json`. Downloader reads from `package.json` first. Two version sources in play, accessed in different orders by different callers.
- **Self-healing Node dependencies at runtime** — `ensureDependencies()` in the wrapper detects missing `node_modules` (post-`autoUpdate` scenario) and runs `bun install --frozen-lockfile` inline, on every MCP launch where the check fires. The `cross-spawn` import is lazy (`const crossSpawn = require("cross-spawn")`) so the install itself can complete before the package it needs is loaded.
- **Bun.sleepSync dependency** — the lock-acquire loop uses `Bun.sleepSync(pollMs)` rather than a cross-runtime equivalent, so the wrapper is Bun-specific even though the downloader path supports Node (`.js` vs `.ts` branch). A Node-only runtime could not execute the wrapper as written.
- **Binary version has three states** — release (`0.0.61`), dev build from main (`0.0.62-dev.5+a1b2c3d`), and unknown (wrapper handles all three with different version-compare logic). Dev builds accept `base >= plugin`, release builds require `>=`, unknown falls through to use-what-we-have. This nuanced fallback exists because the snapshot release tag's binary will often have a newer base version than the plugin.json the consumer checked out.

## 18. Gaps

- **Exact file-mode (executable bit) of `bin/aide-wrapper.ts`** — not queried via `git ls-tree`; would need `gh api repos/jmylchreest/aide/git/trees/HEAD` with sub-path to inspect `mode` field for `bin/` entries. The invocation path in `plugin.json` uses `bun ${CLAUDE_PLUGIN_ROOT}/bin/aide-wrapper.ts` so exec bit is not load-bearing for Claude Code usage, but matters for direct/symlink invocation.
- **Content of `aide-dev-toggle.sh`** — 20KB root script, not inspected; likely a contributor utility for toggling between released and locally-built binaries during development. Resolution: fetch raw file.
- **Full content of `release.yml`** — only ~900 lines sampled; jobs after `snapshot` (if any) not confirmed. Resolution: fetch remaining lines.
- **Whether `scripts/validate-skills.ts` is invoked anywhere in CI** — greped the visible `ci.yml` content; not called there. May be invoked via a pre-commit hook or via `npm run`/`bun run` script not in `package.json`. Resolution: fetch `.git/hooks/` refs and search for `validate-skills` across all CI/automation files.
- **TODO.md content beyond the head** — only first 40 lines read; may contain plugin-facing plans. Not load-bearing for the research template; skipped.
- **All SKILL.md frontmatter shape uniformity** — sampled 3 of 25 skills (`assess-findings`, `autopilot`, `swarm`). Saw `name`, `description`, `triggers`. One skill (`assess-findings`) noted `platforms:` in the validator's type definition. Whether all skills use identical fields not verified. Resolution: fetch remaining 22 SKILL.md files and diff frontmatter shapes, or trust the validator's schema.
- **Whether any Python or Rust runtime deps exist** — `package.json` shows only Bun/Node deps; `go.mod` shows Go deps; no `requirements.txt`, no `Cargo.toml` observed. Safe to say "no Python/Rust" but not verified exhaustively.
- **Whether `userConfig` is intentionally omitted or planned** — no explicit statement in README or `plugin.json`; inferred from absence. A consumer hoping to customize aide behavior without editing shell rc files has no plugin-surface way to do so.
- **Whether Claude Code's `autoUpdate` actually rm's `node_modules`** — the wrapper's comment claims it does, but I haven't independently verified; the behavior might be "git pull preserves node_modules if it existed before update but fresh installs don't populate it." Resolution: Claude Code plugin-install source.
- **Runtime behavior of `permission-handler.ts` when enabled** — only the first 60 lines read; SAFE_COMMANDS list is truncated. Full behavior not documented in README (since it's opt-in and undocumented at the user surface). Resolution: fetch remainder of `src/hooks/permission-handler.ts`.
