# Sample

Pass-1 Phase-1a partial for bin 2. Functional decomposition of Arcanon-hub--arcanon, BULDEE--ai-craftsman-superpowers, BaseInfinity--sdlc-wizard, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How and where the marketplace manifest sits in the repo — the file(s) Claude Code's `marketplace add` resolves against.

### Single root manifest

`.claude-plugin/marketplace.json` at repo root, paired with a sibling `.claude-plugin/plugin.json`. The marketplace.json's `plugins[0].source` is `"./"`, so the marketplace and the single plugin share the same root. Lowest-overhead layout for single-plugin repos; manifest and plugin metadata are co-located, easier to keep in sync. Some plugins additionally place a `.claude-plugin/ignore` file alongside the manifest pair to curate which tree paths ship to consumers (excluding `tests/`, `scripts/`, in-repo dev docs, heavy `node_modules/` trees under packs).

### Single root manifest with relative source under `plugins/<name>/`

`.claude-plugin/marketplace.json` at repo root with `plugins[0].source: "./plugins/<name>"`. The plugin lives in a subdirectory; the marketplace is the door to it. Suits repos that anticipate hosting more plugins or that separate plugin source from repo-level scaffolding.

### Duplicated marketplace manifest at root and under `plugins/<name>/`

Two byte-identical `marketplace.json` files coexist: the canonical one at repo root (which `claude plugin marketplace add <url>` resolves) and a duplicate inside the plugin source tree's `.claude-plugin/`. The duplication is drift-prone — release commits routinely bump one and miss the other, surfacing as hot-fix commits ("bump repo-root marketplace.json to <version>"). No documented rationale; CI manifest-equality checks may cover only one of the two copies, leaving the canonical one unguarded.

## Marketplace-level metadata wrapper

How marketplace.json carries description / version / pluginRoot — flat top-level fields versus a `metadata` object.

### Flat top-level fields only

Top-level `name`, `owner`, `plugins`, `version` directly on the JSON root. No `metadata` wrapper, no `metadata.description`, no `metadata.pluginRoot`, no `$schema`. Minimal scaffolding; works but provides no structured place for marketplace-wide description or root-relative plugin-tree base.

### `metadata` wrapper carrying description (and optionally version)

A `metadata: {description, version?}` object at the top of marketplace.json alongside `name`, `owner`, `plugins`. `metadata.pluginRoot` is generally absent — single-plugin manifests bind via `source` instead. The `metadata.version` field can drift independently of the per-plugin `plugins[0].version` since neither validator nor runtime cross-checks them; observed cases of marketplace `version: 1.0.0` frozen while plugin `version: 1.35.0` advances 35 minors.

## Per-plugin discoverability metadata

How a marketplace entry is surfaced to users browsing or filtering plugins — keywords, tags, categories.

### Keywords only on plugin.json

The marketplace entry carries minimal metadata (`name`, `version`, `source`, `description`); `keywords` lives exclusively in `plugin.json`. No `category` or `tags` on the marketplace surface, so category-based browser filters cannot surface the plugin. Authoring overhead is low (one list, one location), at the cost of marketplace-side filterability.

### Category + tags on marketplace entry plus keywords on plugin.json

Marketplace entry declares `category: "<area>"` and `tags: [...]`; plugin.json separately carries a `keywords` array. Both surfaces are populated, but the two lists drift independently — tags meaningful at the marketplace level (e.g., `rule-engine`, `ci`) and keywords meaningful at the plugin level (e.g., individual technologies, methodology names) overlap partially. Two discovery vocabularies with no single source.

### Tags on marketplace, keywords on plugin.json — drifted vocabularies

Marketplace `tags` and plugin.json `keywords` describe the same plugin but differ in entries (e.g., marketplace lists `testing`; plugin.json lists `ai-agent`, `developer-tools`). Risk: a search via one surface misses tokens only present in the other. No tooling reconciles them.

## Version-string source-of-truth count

Number of files where the plugin's version string lives, and what enforces sync.

### Three-location version (marketplace top-level + marketplace entry + plugin.json)

Version string duplicated in `marketplace.json` top-level `version`, `marketplace.json.plugins[0].version`, and `plugins/<name>/.claude-plugin/plugin.json.version`. All three must be bumped per release. Drift evidence: hot-fix commits explicitly titled "bump repo-root marketplace.json to <version>" after a release commit missed it. CI may enforce equality across some subset (e.g., name fields across three manifests) but version equality is often unguarded.

### Three-location version with npm package.json as the third site

Version lives in `plugin.json`, `marketplace.json` (one or two slots), and `package.json` for projects that ship as both a plugin and an npm CLI. Release CI may gate `tag == package.json.version` only — drift between `package.json` and the plugin-side manifests is not caught structurally. Observed cases bump all three together by convention but enforcement is human discipline.

### Six-location version sync via project-local script

Version string scattered across `plugin.json`, two slots in `marketplace.json`, a `VERSION=` in a CI/dispatch shell script, the README badge, and a "Current version: " line in CLAUDE.md (and sometimes a mock-output version inside test fixtures). A `scripts/bump-version.sh <new>` patches all sites in one invocation; CLAUDE.md additionally maintains a "Version Sync Checklist" so contributors and the script stay aligned. Solves the multi-file problem with project-local tooling rather than runtime indirection. The script itself can be substrate-fragile (e.g., `sed -i ''` BSD-syntax fails on GNU Linux sed) — author's local platform leaks into a shared release tool.

## Channel distribution model

Whether the plugin offers stable / latest splits or a single channel users pin via git ref.

### Single channel — users pin via git ref

No stable/latest split, no separate dev-counter marketplace. Users install at default branch (HEAD) or pin a specific tag (`@vX.Y.Z`). Release cadence is whatever lands on main — every push to main is a potential user-visible release. Adequate for most plugins; aggressive cadence (multiple patches per day, many minors per month) makes "latest" volatile but the in-product update-skill or a session-start version-check hook can soften this.

### Single channel with version-reset across rebrand

Plugin moves through major versions under one name, then resets to `0.1.0` under a new name. Users pinned at `<old-name>@vX.Y.Z` do not auto-update because the plugin name changed; the rebrand is communicated via README/CHANGELOG only, not enforced in the manifest. Identity transition is a soft event — the marketplace cannot bridge it.

### Application-level channel system distinct from distribution channels

Some plugins ship a `channels.sh` library inside `hooks/lib/` for the plugin's own feature routing (which rules apply to which projects), independent of marketplace channel distribution. Worth distinguishing — the term "channel" overloads at the plugin and marketplace layers.

## Tag placement and release cadence

Where release tags sit in git history and how often they're cut.

### Tag-on-main, no release branches

Tags live directly on main; no long-lived `release/*` branches. Release prep (CHANGELOG finalization, version bumps) happens on the main branch via the same commit that triggers the release, sometimes followed by hot-fix commits when prep was incomplete. Suits aggressive iteration; loses the "release branch as quality gate" affordance — incomplete prep merges directly to main and is fixed in flight.

### Tag-on-main with merge-base ancestry gate

Tag on main, but the release workflow's first step asserts `git merge-base --is-ancestor HEAD origin/main` — failing the publish if the tagged commit is not actually on main. Cheap structural guard against tagging a feature branch by mistake. Pairs naturally with `fetch-depth: 0` in the CI checkout step.

### Aggressive minor-only cadence

Every shippable change cuts a minor (10 minors in ~1 month observed); no patch releases, no pre-release suffixes. Implies the project treats every visible change as user-facing. CHANGELOG.md becomes the only durable release-notes artifact since GitHub Releases (when present) are auto-generated from PR titles via `--generate-notes`.

### Reactive patch bursts

Multiple patch releases within hours (e.g., v3.4.1 → v3.4.4 in 36 hours) reacting to user-found issues. Indicates absence of a buffer between development and release; every push reaches users immediately. Forces tight feedback loops in CI to compensate.

## Pre-commit version bump

Whether a hook auto-bumps the patch version per commit or version moves manually at release time.

### Manual bump at release commit

No pre-commit hook; the contributor edits version files (often via a project-local `scripts/bump-version.sh`) before the release commit, then tags by hand. Suits low-frequency release cadence. Burden falls on the human to bump every site; tooling like a bump script with a checklist is the typical mitigation.

### Manual bump only — no hidden dev-counter

Version reflects intentional releases only; commits between releases share the prior version string. Users who track `main` see "the same version" across many commits. Plugins relying on `plugin.json` version as a reload-detection signal would not benefit from a dev-counter scheme — must pair manual bumps with explicit reload triggers.

## Plugin-component registration style

How plugin.json declares (or doesn't declare) commands, agents, skills, hooks, MCP servers.

### Default discovery from conventional directories

`plugin.json` carries metadata only; commands/skills/agents/hooks are auto-discovered from `commands/`, `skills/`, `agents/`, `hooks/hooks.json`. Lowest-overhead path; aligns with the official plugin reference. Inline component definitions in `plugin.json` (e.g., `skills: [{name, description, ...}]`) were valid in older Claude Code schemas but break newer versions — projects that started with inline definitions had to migrate to default discovery (CHANGELOG explicitly: "skills/agents in plugin.json used inline objects incompatible with Claude Code v2.1.92 schema; removed inline; auto-discovery now").

### Default discovery for most components, inline `mcpServers` in plugin.json

Skills/commands/agents/hooks via auto-discovery; `mcpServers` defined inline in plugin.json rather than in a sibling `.mcp.json`. Mixed style — inline keeps the MCP server bundled with the manifest (single source for plugin metadata + MCP wiring) but loses the composability `.mcp.json` offers.

### Default discovery with non-standard component directories

In addition to standard `commands/`, `skills/`, `agents/`, `hooks/`, the plugin includes directories that don't correspond to any documented component type — e.g., `teams/` (orchestration definitions), `setup/templates/` (config scaffolding), `output-styles/` (response-formatting markdown). Some are consumed only by the plugin's own commands; others may be experimental forward-looking surfaces. No structural validation — users learn the convention from the plugin's own code.

## Agent definition format

How `agents/*.md` declares model, tools, and capabilities.

### Frontmatter with model + effort + tool array

Agent markdown with YAML frontmatter declaring `name`, `description`, `model` (e.g., `sonnet`), `effort` (`high`), and `allowedTools` as an array of plain tool names (`Bash`, `Read`, `Glob`, `Grep`, `Write`, `Agent`). May additionally declare `memory: project|user`, `isolation: worktree`, `maxTurns: <N>`, and a `skills: [<plugin>:<skill-name>]` cross-reference array. Field-name regressions are common (CHANGELOG: `tools:` → `allowedTools:` correction across multiple agent files in a single patch). Permission-rule syntax (`Bash(<pattern>)`) was not observed in agent frontmatter — only plain tool names.

### Agent frontmatter with experimental orchestration tool names

Agent `allowedTools` arrays include tool names not documented in the plugin reference (e.g., `TeamCreate`, `TaskCreate`, `TaskList`, `TaskUpdate`, `SendMessage`) for agents that orchestrate sub-agents or manage shared state. Implies bespoke runtime support inside the plugin rather than the standard tool set. No validator checks tool-name validity — typos or reference-mismatches surface only at runtime.

## Bin-wrapped CLI distribution

When a plugin exposes thin shell-script entry points to make internals invokable from the agent's Bash tool.

### No bin/ — internals invoked via hooks and commands only

The plugin's executable surface is hook scripts under `scripts/` invoked by hook events, plus markdown command files. Nothing is surfaced as a user-PATH binary. Suits plugins where everything goes through Claude Code's hook/command dispatch rather than direct bash invocation.

### bin/ wrappers as thin exec-delegates

`bin/<plugin>-<verb>` shell scripts that `exec bash "$(cd "$(dirname "$0")/.." && pwd)/<internal>.sh" "$@"` — resolving the plugin root via `$(dirname "$0")` rather than `${CLAUDE_PLUGIN_ROOT}`, so the script works whether invoked directly from a terminal or from a Claude Code Bash-tool context where `CLAUDE_PLUGIN_ROOT` may be absent. Lets one implementation serve both the hook-event invocation and a CLI invocation. CI may not enforce executability on `bin/*` (the validator's allowlist commonly covers `hooks/*.sh` but not `bin/*`), so the +x bit must be set deliberately.

### bin/ wrapper that synthesizes a hook input envelope

`bin/<plugin>-validate` reconstructs the PostToolUse JSON input envelope (`{tool_input: {file_path: $fp}}`) via `jq -n` and pipes it into the hook script — letting a user run the same hook validator from a terminal as Claude Code runs at PostToolUse. "One implementation, two surfaces." The reconstructed envelope is brittle against hook-input schema changes; if Claude Code adds required fields, the CLI surface silently breaks while the hook-event surface still works.

### npm bin (not plugin bin) for separate distribution lane

`package.json.bin.<name> = "./cli/bin/<name>.js"` exposes a Node CLI separate from any plugin-side `bin/`. Used when the same project ships as both a Claude plugin and an npm package — the npm form distributes the CLI for one-shot init/update; the plugin form is enabled inside Claude Code. The two distribution surfaces share content via copying or symlinks.

## SessionStart-generated runtime artifacts at well-known paths

Files the plugin writes outside its own data directory on every session, to bridge the Bash-tool-context environment-variable gap.

### Bridge file at `~/.claude/<plugin>-session-state-path`

A path-bridge file containing the resolved `CLAUDE_PLUGIN_DATA` location. Skills running in Bash-tool context don't receive `CLAUDE_PLUGIN_ROOT` or `CLAUDE_PLUGIN_DATA` from the harness, so they cannot locate sibling resources (DBs, state files) by env var. SessionStart resolves the path and writes it to a stable absolute location every session. Side-effect-at-startup pattern; vulnerable to test pollution (test runs that exercise SessionStart can overwrite the real bridge file with temp paths) — tests need backup/restore guards.

### Generated executable wrapper at `~/.claude/<plugin>-<verb>.sh`

SessionStart writes a per-session executable shell wrapper with the plugin's resolved lib path baked in, so commands invoked from Bash-tool context can locate plugin-internal scripts without env vars. Rebuilt every session; stale wrappers from old plugin versions are silently overwritten — clean by design but fragile against tests running SessionStart in isolation.

## SessionStart hook context injection

Whether SessionStart emits structured JSON to bias the next session.

### `hookSpecificOutput.additionalContext` payload

SessionStart hook emits a JSON object with `hookSpecificOutput.additionalContext` containing project-detection results, available command list, and worker/system status. Built with `jq -Rs .` for safe escaping. Wired to both SessionStart and UserPromptSubmit (the latter as fallback for upstream issues), with a `/tmp/<plugin>_session_${SESSION_ID}.initialized` flag file for once-per-session deduplication. The dedup file lives in `/tmp` and is vulnerable to OS-level tmpfs sweeps.

### `systemMessage` payload (broader form)

SessionStart emits `{systemMessage: "..."}` JSON containing a multi-line profile summary (active stack, strictness, enabled rules, learning trends from prior sessions, healthcheck, command routing table). Less structured than `additionalContext` but renders verbatim in the session's system context. Used when the surface is many concise lines rather than a single rich payload.

### SessionStart used only for non-context side effects

SessionStart hook fires but emits no `additionalContext` / `systemMessage`; instead it performs side-effecting setup (writes bridge files, generates wrappers, prints effort/model nudges to stderr). Context loading is shifted to UserPromptSubmit or InstructionsLoaded. Suits plugins where "context" is delivered per-prompt rather than per-session.

## UserPromptSubmit observation

What the plugin does on every user prompt.

### Per-prompt context reminder

`UserPromptSubmit` hook emits a small (~100-token) baseline reminder of the methodology's core rules on every prompt. Reinforces context as the conversation moves; cost is one hook invocation per prompt.

### Per-prompt bias / signal detection

The hook scans the prompt text for cognitive biases (acceleration, scope creep, over-optimization) or first-person distress phrases ("i'm stuck", "confidence: low"), logs hits to a rolling cache, and emits warnings or stronger nudges when threshold counts are reached within a time window. State-across-prompts implemented in a stateless hook via a pruned-log file at a stable cache path.

### Per-prompt version-mismatch / worker-restart check

The hook calls a local worker daemon's `/api/version` endpoint and compares against the installed `plugin.json` version, killing and restarting the worker on mismatch. Runs on every prompt (intentionally exempt from any once-per-session dedup) so mid-session updates are caught immediately. Cost: one HTTP call per prompt.

## Conditional hook matchers

Mechanisms to narrow when a hook fires beyond the basic `matcher: "<event-pattern>"`.

### `if:` permission-rule sub-matcher on PreToolUse

PreToolUse entry registered with `matcher: "Bash"` and an additional `"if": "Bash(git push*)"` field that further narrows the hook to git-push-shaped commands only, using the same permission-rule glob syntax as `permissions.allow/deny`. Far more precise than matching all Bash invocations and re-parsing inside the hook. Brittle against future Claude Code changes to `if:` parsing — silent regression possible.

### `if:` with multiple alternatives across tools

PreToolUse entry with `matcher: "Write|Edit|MultiEdit"` and `"if": "Write(src/**) Edit(src/**) MultiEdit(src/**)"` — the `if:` field carries space-separated tool/glob alternatives, narrowing the hook to writes under a specific path prefix. Avoids running the hook for non-matching paths at all; the hook script doesn't even fire. The path pattern is hard-coded per-consumer (a comment instructs the user to "customize this pattern to match your source directory") — installation requires post-install customization.

## File-write protection hook

A PreToolUse hook for `Write|Edit|MultiEdit` that blocks or warns on sensitive paths.

### Block-list with hard deny + soft warn classes

`scripts/file-guard.sh` classifies the target path against two pattern groups: hard-block (`.env`, `*.pem`, `*.key`, `*credentials*`, `*secret*`, `*.lock`, `package-lock.json`, `*/node_modules/*`, `*/.venv/*`, `*/target/*`) emits `exit 2` + stderr human message + stdout `hookSpecificOutput.permissionDecision: "deny"`; soft-warn (`migrations/*.sql`, `*.pb.go`, `*_generated.*`, `CHANGELOG.md`) emits `exit 0` + `systemMessage` JSON. Dual-output contract — stderr for the terminal display + stdout JSON for the harness's permission-decision schema. User-extensible block list via `<PLUGIN>_EXTRA_BLOCKED` env var (colon-separated globs).

### Layer-import / architecture rule validation

PreToolUse for `Write|Edit` runs an architecture-rule engine before the write commits — checks layer-import boundaries on PHP/TS/TSX (e.g., LAYER001-003, PHP001) and `exit 2` blocks the write. Same engine source as the PostToolUse rules (see "Rule engine across hook + CI" axis).

## File-write post-validation hook

A PostToolUse hook for `Write|Edit|MultiEdit` that lints, formats, or fully validates after the write lands.

### Format-then-lint, non-blocking

PostToolUse runs `scripts/format.sh` then `scripts/lint.sh` sequentially, both non-blocking — warns on failure, doesn't block. Dual command in a single hook entry. Lightweight; assumes the formatter/linter are installed on the host.

### Full rule engine with cross-file pattern aggregation

PostToolUse runs a 13.5KB+ rules engine that consults a session-state DB (SQLite) after recording a violation. If the same rule has fired in 3+ files this session, the hook appends a "PROJECT-WIDE PATTERN: {rule} found in {N} files — consider a project-wide fix or global ignore" banner to the block/warn message. Session-aware violation aggregation delivered through hook output. Per-rule inline suppression supported via `<plugin>-ignore: <RULE_ID>` comments inside source files.

## TDD reminder hook

A hook that prompts the user toward writing tests first.

### PreToolUse on src/ writes emits TDD additionalContext

PreToolUse with an `if:` clause narrowing to writes under `src/**`. On match, emits `hookSpecificOutput.additionalContext` with a "write a failing test first" prompt. Fail-open (no `set -e`); silent on non-matching paths.

## Test-success unlocks subsequent action

A hook pattern where successful test runs flip session state to allow downstream gates to pass.

### PostToolUse on Bash watches for test runners

`PostToolUse` matcher `Bash` (with `async: true`) inspects the tool result's exit code and command line; if exit is 0 and the command matches a regex of common test runners (`run-tests.sh|phpunit|jest|vitest|pytest|cargo test|go test|npm test|pnpm test|yarn test`), the hook flips a session-state `verified=true` flag. A separate PreToolUse on `git push` (via `if: "Bash(git push*)"`) reads that flag and allows the push without further friction. Emergent workflow: "test-then-push unlocks push automatically." State-machine semantics implemented across two stateless hooks via shared session state.

## PreCompact gating

Whether the plugin blocks `/compact` under unsafe conditions.

### Manual-only PreCompact with self-healing seam check

`PreCompact` hook with `matcher: manual` (so auto-compact is never blocked — it could push context over 100% and lose everything). On manual `/compact`, the hook reads `.reviews/handoff.json` and blocks if status is `PENDING_REVIEW` or `PENDING_RECHECK`, or if a git rebase/merge/cherry-pick is in progress. Self-heals: if the handoff has a `pr_number` and `gh pr view` reports the PR `MERGED`, the gate clears the status and lets the compact proceed. Requires Claude Code v2.1.105+.

## InstructionsLoaded hook

A hook that fires when project instructions load.

### Validate-and-nudge on instructions load

`InstructionsLoaded` hook validates that project documentation files (e.g., `SDLC.md`, `TESTING.md`) exist, nudges on missing files, on stale plugin version (≥3 minor delta), and on open API-shepherd issues from a weekly cron. Cheap one-shot check at session start. Available since Claude Code v2.1.69 — version floor declared inline in hook comments rather than in `plugin.json`.

## Hook output contract

How a hook signals decisions to the harness and surfaces them to the user.

### Stderr for human display + stdout JSON for harness

Hook emits a human-readable message on stderr (terminal display) AND a `hookSpecificOutput` JSON object on stdout (harness's permission-decision schema). Both surfaces are written for blocking exits; warning-only exits emit only `{systemMessage: "..."}` on stdout. Without stderr, the user sees only "No stderr output" and no actionable message — the dual contract is required for usable UX. CHANGELOG entries explicitly call out fixes for this regression.

### Fail-open envelope via `trap 'exit 0' ERR`

Every hook script opens with `set -uo pipefail` (note: `-u` and `-o pipefail`, NOT `-e`) plus `trap 'echo "WARNING: <hook> failed at line $LINENO" >&2; exit 0' ERR` — on crash, the hook emits a warning to stderr but exits 0 so writes/pushes are never blocked by hook bugs. Codified at the project level: "all hook scripts MUST use `exit 0` (pass) or `exit 2` (block); NEVER `exit 1`." Pairs with explicit-exit-code discipline inside the hook body — `realpath` and other commands that may fail on not-yet-existing files cannot use bare `set -e`.

## User configuration schema

Whether the plugin declares a `userConfig` block and how it's wired.

### No userConfig — env vars only

Plugin reads tunables (`<PLUGIN>_CACHE_DIR`, `EFFORT_LEVEL`, etc.) directly from environment variables or `settings.json` rather than declaring them in `userConfig`. Sidesteps the schema but loses Claude Code's `sensitive: true` flag and built-in CLI-driven UX for the secret fields.

### Rich userConfig with sensitive flag and defaults

Multi-field `userConfig` with `title`, `type`, `description`, `required`, `default`, and `sensitive: true` on the secret fields. Numeric/boolean fields declare defaults; the secret field carries the description "stored securely in keychain". Aligns with Claude Code's secure-storage UX. Manifest-level substitution via `${user_config.<KEY>}` in `.mcp.json` env blocks or hook commands is a separate concern — declaring fields and wiring them are independent steps.

### userConfig declared but not wired through manifest substitution

Fields declared (with `sensitive: true` etc.) but no `${user_config.<KEY>}` references in `.mcp.json` env block or hook commands. The runtime reads credentials from a chain of fallbacks (userConfig → env var → on-disk config file at `~/.<plugin>/config.json`). Documented in README but not enforced in the manifest — if the runtime code path that queries userConfig is absent or stale, the userConfig surface is a no-op.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

Hooks read userConfig values through Claude Code's `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (e.g., `CLAUDE_PLUGIN_OPTION_agent_hooks` for early-exit on a boolean toggle). No `${user_config.KEY}` token substitution in hook commands — values flow through env vars instead. Coexists with a parallel project-level YAML config file (`.craft-config.yml`); SessionStart warns when the two surfaces diverge, but neither is canonical.

## Dependency installation strategy

How the plugin's runtime dependencies (Node modules, Python packages) reach the user's machine.

### No dependency installer — graceful degradation

Plugin assumes `python3`, `jq`, `bash 3.2+`, and feature-tier external tools (PHPStan, ESLint, deptrac, dependency-cruiser, shellcheck) are already on the host. Features light up when their required tool is present; absent tools mean degraded but still-functional behavior. Documented as a degradation ladder rather than a caveat. Suits pure-bash plugins; foregoes any auto-install footprint at the cost of users needing to provision tools themselves.

### Node `npm install --prefix ${CLAUDE_PLUGIN_ROOT}` from SessionStart

SessionStart hook runs `npm install --prefix "${CLAUDE_PLUGIN_ROOT}"` reading `${CLAUDE_PLUGIN_ROOT}/package.json`. Installs land in `${CLAUDE_PLUGIN_ROOT}/node_modules`. Choice of ROOT over DATA is rooted in ESM module resolution: ESM walks up from the importing file looking for `node_modules/`; installing into `CLAUDE_PLUGIN_DATA` would place node_modules outside that walk path, and ESM deliberately ignores `NODE_PATH`, so the CJS env-var workaround cannot bridge the gap. Pure-ESM workers (`"type": "module"` + top-level `import`) require the install path to be adjacent to the import sites.

### Diff-based change detection with separate sentinel and manifest

Two manifests coexist with different roles: `package.json` is what npm actually reads (`npm install --prefix` reads the prefix dir's `package.json`), while a sibling `runtime-deps.json` (or similar) is the sentinel-diff source for idempotency. SessionStart runs `diff -q $MANIFEST $SENTINEL` against `${CLAUDE_PLUGIN_DATA}/.<plugin>-deps-installed.json`; on mismatch, reinstall + update sentinel. Double-checked with `[ -d "${ROOT}/node_modules/<probe-pkg>" ]` so an external `node_modules` wipe forces reinstall even with intact sentinel. The two manifests can drift — undocumented constraint that the sentinel must mirror the npm-read manifest, or the diff lies. Failure path: `rm -rf node_modules` + `rm -f $SENTINEL` so next session retries clean.

### Self-healing inline install at MCP launch

`scripts/mcp-wrapper.sh` independently runs `npm install` if a probe directory under `node_modules/` is missing when the MCP server launches. A second install path — not a fallback delegate, a full duplicate — covering the race where Claude Code spawns the MCP server before the SessionStart hook completes. Suits plugins where the MCP server may launch parallel to or before SessionStart. Makes the install idempotent across two entry surfaces.

### npm CLI as the sole install surface

The plugin form has no installer; the project's npm package (`package.json.bin.<name>`) carries an `install.sh` that wraps `npx -y <package> init` to copy hooks/skills into the user's `.claude/`. The plugin form is then self-sufficient because everything is markdown + bash with no runtime deps. Used when the same project ships as both a plugin and an npm CLI, with the CLI doing one-time install work the plugin form doesn't need.

## Failure-signaling envelope

How install / setup scripts report failure without breaking the session.

### `set -euo pipefail` + `trap 'exit 0' ERR` — non-blocking with cleanup

Strict-on-failure inside the script body, but a top-level ERR trap converts any unhandled failure to `exit 0`. npm output piped through `2>&1 | head -50 >&2` so only the first 50 lines reach the terminal and nothing leaks to stdout (hook JSON contract). Always exits 0; never blocks the tool. Failure path explicitly cleans up partial state (`rm -rf node_modules; rm -f $SENTINEL`) so next session retries clean.

### Strict-on-failure with typed errors and colored stderr

`set -euo pipefail` plus a `{ ... }` download-guard block (specifically defending against partial-execution under `curl | bash`). Throws typed errors (e.g., `err.pluginPaths` when both plugin and CLI install forms coexist) and streams colored stderr guidance. Used in user-invoked install scripts where a hard error is the right outcome.

## Worker daemon

Whether the plugin runs a long-lived background process.

### No worker — stateless hooks only

Hooks are short-lived shell scripts; no background process. State persists via files on disk (session-state.json, JSON caches). Lowest operational footprint.

### Local Fastify HTTP daemon on a fixed port

The plugin runs a Node Fastify worker on `localhost:<port>` with multiple endpoints (e.g., `/api/version`, ingestion endpoints, query endpoints), auto-started by `scripts/worker-start.sh` from `session-start.sh`. PID + port files in the data dir. UserPromptSubmit hook checks the worker's `/api/version` against the installed plugin version on every prompt and kills+restarts on mismatch. A separate MCP server process runs alongside, both reading the same SQLite via per-call DB resolution. Goes well beyond "plugin is a directory of markdown + scripts" — it's a full long-running service. Architecture (worker + MCP server as peer processes sharing SQLite) is distinctive; significant operational complexity.

## State persistence

Where the plugin keeps state that survives across sessions.

### JSON files under `${CLAUDE_PLUGIN_DATA}`

State files (e.g., `session-state.json`, version-stamp markers, last-checked timestamps) under the plugin's managed data dir. Inspectable, simple format. Standard idiom; aligns with the plugin reference.

### SQLite under `${CLAUDE_PLUGIN_DATA}` for behavioral metrics

`metrics.db` SQLite database tracks rule-violation events and corrections across sessions. Atomic writes; SessionStart queries trends and surfaces them as `Learning: <rule> fix rate <pct>%` in the session context payload. Persistence is local per-machine — no cloud sync. "Behavioral feedback loop" framed as a unique-in-the-ecosystem capability by the project's README.

### Bridge files at `~/.claude/<plugin>-*` for Bash-tool-context access

Skills running in Bash-tool context don't receive `CLAUDE_PLUGIN_DATA`, so the plugin writes a path-bridge file at a stable location every SessionStart that resolves to the data dir. See "SessionStart-generated runtime artifacts" axis.

### State-of-watcher files in `.github/last-checked-*.txt`

Repository-tracked state files (`.github/last-checked-version.txt`, `.github/last-community-scan.txt`, `.github/last-checked-api-date.txt`) act as durable cron-watcher checkpoints — "where did I leave off?" — committed back to the repo so the next cron run resumes correctly. CI enforces their existence as a structural invariant.

## External-change watcher (shepherd pattern)

How the plugin observes external sources for relevant changes (Claude Code releases, API changelog, community signals).

### Per-prompt or per-session npm-version probe

Hook (`InstructionsLoaded` or similar) polls `npm view <package> version` at most once per 24h (cached at `$HOME/.cache/<plugin>/latest-version`, regex-validated as semver). On lag, emits a non-blocking warning to the next session — loud multi-line block at ≥3-minor lag, mild one-liner otherwise. State-of-watcher in a strict-format cache file with a TTL.

### GitHub-side cron workflows opening tracking issues

Cron-scheduled GitHub Actions workflows poll external sources (release pages, API changelogs, community forums) on a schedule (weekly Monday 09:00 UTC, monthly 1st 11:00 UTC). They do cheap detection only and open or update a single tracking GitHub issue per source; an `InstructionsLoaded` hook nudges the next session toward those issues. Replaces what `monitors.json` would do at the plugin level and extends it with durable issue tracking. The Anthropic API changelog detector specifically fetches `.md` URLs (Mintlify convention) rather than scraping rendered HTML — deliberate stability choice.

## Distribution exclusion

How the project decides what ships to consumers vs what stays in the repo.

### `.claude-plugin/ignore` exclusion list

A 14-line ignore file alongside `marketplace.json` listing heavy dependencies (`packs/*/mcp/*/node_modules/`, `packs/*/mcp/*/dist/`), dev-only directories (`tests/`, `scripts/`, `examples/`), CI artifacts, and selected docs (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`). The plugin archive served to users is a curated subset of the repo. Distribution-shaping mechanism distinct from `.gitignore`.

## Multi-mode distribution

When the same project ships through multiple delivery surfaces.

### Plugin + npm CLI + curl-bash with collision detection

Same content shipped via three install paths: Claude plugin (enabled inside Claude Code), npm CLI (installable via `npx`, `npm install -g`, or Homebrew tap), and `curl | bash` script. The CLI's init code explicitly probes for the plugin install paths and blocks with a typed error when both coexist; a session-start hook also nudges on dual-install. Six documented install paths (npx, curl-bash, Homebrew tap, gh extension, `npx github:`, global npm) — heavy investment in distribution surface area. The engineering cost is documented in CHANGELOG with a referenced PR.

### Plugin + monolithic repo with rebrand legacy

Plugin shipped under a current name, with extensive backward-compatibility for a legacy name across every runtime surface — env var pairs (`<NEW>_API_KEY`/`<OLD>_API_KEY`, `<NEW>_WORKER_PORT`/`<OLD>_WORKER_PORT`, etc.), data dirs (`~/.<new>/` preferred, `~/.<old>/` honored if new dir doesn't exist), config files (`<new>.config.json` preferred, `<old>.config.json` honored). Identity-transition discipline far thicker than typical rebrand-compat — every observable surface honors both spellings. Intermediate artifacts may still carry the old name (e.g., a `runtime-deps.json` with `name: "@<old>/runtime-deps"` at version 5.7.0 inside a v0.1.0 release of the new identity).

## Test stack

What the plugin uses to test itself.

### Bash scripts only

`tests/run-tests.sh` (or per-area `tests/*-test.sh`) as the entry point, with bash test files dispatching into subdirectories (`tests/hooks/`, `tests/ci/`, `tests/core/`, etc.). No pytest/jest/vitest. Pure-bash discipline; CLAUDE.md may explicitly note "No traditional unit tests (bash scripts only)." Suits plugins whose own runtime is shell-scripts; weak when test logic gets complex.

### Multi-runner — Node `node --test` + bats

`node --test` (built-in Node test runner) for JS test files co-located with code (`worker/**/*.test.js`), plus `bats-core` (submodule-pinned) for shell-integration tests under `tests/*.bats`. Mixed runner per language. Submodule pinning the bats binary aims for reproducibility but introduces a "submodule not fetched" graceful-skip path that can mask CI gaps.

### Bash + Python helpers (no Python test framework)

Bash scripts as the test runner with Python used inline for YAML/markdown parsing within shell scripts (`python3 -c "import yaml; yaml.safe_load(...)"`). No pytest. Suits plugins that already require `python3` for runtime helpers — same dependency.

### CI runs Claude against scenarios — meta-dogfood

The CI pipeline runs the real `anthropics/claude-code-action@v1` against a baseline (main) wizard and a candidate (PR) wizard, executing simulated SDLC scenarios and scoring compliance. Tier 1 (every PR): 1+1 simulation. Tier 2 (on `merge-ready` label): 5+5 evaluations with t-distribution 95% CI computed via `tests/e2e/lib/stats.sh`, emitting `IMPROVED`/`STABLE`/`REGRESSION` verdicts and a Robustness score. The plugin evaluates itself by running an agent against fixtures. Bootstrap mode handles the "no baseline yet" case.

## CI-job structure

How the project organizes CI jobs.

### Single-workflow with multiple jobs in a DAG

`.github/workflows/ci.yml` containing all validation jobs in a `needs:` dependency graph. A seed job (e.g., secrets-scan) gates all downstream work. Jobs cover: JSON parseability, hooks.json schema validation, plugin manifest schema, shell script syntax + executability + shellcheck lint, skill frontmatter, agent frontmatter, knowledge-base presence, test-runner, and a final summary job that fails if any upstream did. One file, full visibility, fragile against adding new components (new hooks require editing the script allowlist in CI too).

### Multi-workflow split by trigger and concern

Multiple workflow files split by trigger: `ci.yml` for PR validation, `release.yml` for tag pushes, `pr-review.yml` for ready-for-review automation, `weekly-update.yml`/`weekly-api-update.yml`/`monthly-research.yml` for cron shepherds, `benchmark-*.yml` for performance work. `concurrency` block on `ci.yml` with `cancel-in-progress: true` to prevent stale re-runs. Eight or more workflows total in an ambitious project.

### Single workflow, sparse coverage

CI runs a few jobs: manifest lint, shell-lint, a partial test job that only exercises a subset of test files. Most of the test suite is not run by CI (e.g., 70+ JS test files visible in tree but only one subdirectory is actually executed). Massive coverage gap — typically the result of evolution outpacing CI updates.

## Manifest and schema validation in CI

What CI checks about the plugin's manifests and component definitions.

### `jq` parseability + name-equality assertions

CI runs `jq empty` against every JSON manifest (parseability) and `jq` queries asserting `name` fields are equal across plugin.json, marketplace.json's plugins entry, and any other manifest slot. Cheap; doesn't validate schema (no check that `timeout` is a number, no check that `command` correctly substitutes `${CLAUDE_PLUGIN_ROOT}`). Notable failure mode: name-equality may not cover every manifest in a multi-manifest layout; the unguarded one is precisely the one that drifts.

### Inline Python validators in CI YAML

Heredoc Python scripts inside `ci.yml` step bodies validating: hook event names against an allowlist set, hook types in `["command", "agent"]`, agent `model` in `["haiku", "sonnet", "opus"]`, plugin manifest required fields, semver regex on version. Most thorough hooks validator surface observed. Drawback: validator changes appear as ci.yml diffs, which is worse for review than tracked Python files. The validator itself can lag the runtime — a patch release was specifically needed to add 4 new hook events to the allowlist after the runtime accepted them.

### Frontmatter validation by grep

`grep -q "^name:"` / `grep "^model:"` against `skills/*/SKILL.md` and `agents/*.md`. Catches missing fields; misses YAML quoting issues, multi-line descriptions, partial matches. Cheap; partial.

### YAML safety regex sweep

CI greps workflow YAML files for unsafe `${{ }}` interpolation patterns, blocking specific shapes that have caused production breakage. Watch-for-regressions guard that evolved from prior incidents; documented in CHANGELOG. Defense-in-depth around shell-injection through GitHub Actions expressions.

## Release automation

What happens when a tag is pushed.

### No release workflow

Tags push directly to main; no `release.yml`. GitHub Releases are not created (or created manually via UI). Many tags accumulate without corresponding release artifacts or release notes. CHANGELOG.md is the only narrative, but no automation consumes it.

### Tag-triggered workflow with sanity gates and `--generate-notes`

Workflow on `push: tags: ['v*']`. Two sanity gates: (a) `git merge-base --is-ancestor HEAD origin/main` to assert the tag is on main; (b) tag value (`${GITHUB_REF#refs/tags/v}`) must equal `package.json.version`. Failure aborts publish with targeted `::error::` messages. Then runs `npm publish --provenance` (sigstore via `id-token: write` permission) and `gh release create "$TAG_NAME" --generate-notes` (release notes from PR titles since last tag, NOT from CHANGELOG.md). Gates do not check that tag matches `plugin.json` or `marketplace.json` versions — drift between npm and plugin metadata still possible. `fetch-depth: 0` on checkout required for the ancestry gate.

### Manual release commit with bump script

No release workflow; the contributor runs `scripts/bump-version.sh <new>` (which patches version across many files), commits, manually `git tag`, and `git push origin main && git push origin <tag>`. The script's tail prints the next-step instructions. GitHub Releases (when present) are created via the GitHub UI, manually copy-pasting from CHANGELOG. 30 tags with no automation to guarantee tag == plugin.json version — silent failure mode.

## Documentation set

What documentation files the project ships.

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` (user-facing pitch + install + commands), `ARCHITECTURE.md` (multi-layer diagram, hooks/skills tables, design flows), `CLAUDE.md` (project instructions for Claude operating *on* this repo, separate from any shipped wizard doc the plugin may carry), and `CHANGELOG.md` in Keep-a-Changelog format. Aligns with the system-docs convention.

### Heavy doc surface with meta-project artifacts

20+ top-level markdown files: README, ARCHITECTURE, CLAUDE, CHANGELOG plus competitor audits, research notes, roadmap, score-trend logs, audit-progress logs. README stays focused on the user; sprawl is absorbed into siblings. Can include "two CLAUDE-like files with different audiences" — `CLAUDE.md` for contributors, `<PLUGIN>_WIZARD.md` shipped as the wizard artifact consumers `cat` or WebFetch during setup.

### CLAUDE.md without ARCHITECTURE.md, ADRs as decision capture

CLAUDE.md carries an "Architecture" section with directory tree + role annotations, plus 15+ ADRs under `docs/adr/` in Nygard format (Status/Date/Context/Decision/Consequences). CHANGELOG entries cross-reference specific ADRs. Decision capture is strong; structural overview is split between CLAUDE.md and the ADR tree, requiring readers to reconcile both.

### README + CHANGELOG only, ARCHITECTURE absent

User-facing README + Keep-a-Changelog CHANGELOG. No ARCHITECTURE.md, no CLAUDE.md. Structural information lives entirely in code and inline comments. Suits small projects; weak for plugins with substantial internal structure.

### Shipped planning corpus visible in public repo

`.planning/` tree with MILESTONES.md, ROADMAP.md, STATE.md, per-version phase directories each holding CONTEXT/PLAN/SUMMARY/VERIFICATION/RESEARCH files. 260+ planning files visible in the public repo. Some projects keep this private; others publish their entire milestone-planning process. Candidate "development-process transparency" surface — risk: planning docs can carry stale references (e.g., legacy plugin name paths after a rebrand).

### CHANGELOG as in-product upgrade source

`CHANGELOG.md` doubles as the source the in-product update skill consumes — fetched via WebFetch and diffed against the installed version stamp embedded in a shipped doc. Not just a release-notes artifact; an active runtime input for the plugin's self-update flow.

## License presence

How the LICENSE is declared and whether a `LICENSE` file ships.

### LICENSE file present + SPDX identifier in manifests

A full LICENSE file at repo root (e.g., 10.5 KB Apache-2.0 text) plus `license` field in `plugin.json` and `package.json` carrying the SPDX identifier. GitHub auto-detects and badges the license.

### LICENSE declared in manifests, no LICENSE file

`license: "MIT"` in `package.json` and `plugin.json` but no `LICENSE` file at repo root. GitHub license API returns 404; no SPDX detection. npm publishes the package without a LICENSE file in the tarball unless added to `package.json.files`. Real defect — propagates "MIT" via metadata only.

### AGPL-3.0 with embedded badge

LICENSE present, SPDX `AGPL-3.0-only`, README carries the AGPL badge alongside CI/version badges.

## Symlinked dogfood layout

When the project's own self-use shares content with the plugin install via symlinks.

### `.claude/skills/<name>` as symlinks into top-level `skills/`

Repo's own `.claude/skills/<name>` are git symlinks (mode 120000) into the top-level `skills/<name>/`. The plugin form (via `plugin.json` discovering `skills/`), the CLI install form (which copies `skills/*` into a consumer's `.claude/`), and the repo's self-use all share one source-of-truth set of SKILL.md files. Single content, multiple entry forms. Symlink fragility surfaces as regressions when an absolute symlink slips in (CHANGELOG: "absolute symlink restored to relative — broken on other machines").

## Non-standard component surfaces

Component-shaped directories that don't correspond to documented plugin types.

### `teams/` (orchestration definitions)

A `teams/<name>.md` directory with markdown files that appear to define multi-agent team compositions. Not in the plugin reference. Likely consumed only by the plugin's own commands.

### `setup/templates/`

A `setup/templates/` directory holding configuration scaffolding the plugin's setup command emits. Not a Claude Code component type; an internal asset directory the project surfaces alongside standard component directories.

### `output-styles/`

`output-styles/<name>.md` files — markdown configurations for response formatting, e.g., terse vs reviewer modes. Not in the plugin reference; possibly experimental forward-looking surface.

## Distribution-channel-internal feature flags

How the plugin lets users tune behavior at runtime beyond `userConfig`.

### Per-rule inline suppression

`<plugin>-ignore: <RULE_ID>` comments inside source files disable specific rules on that line or file. Multi-rule form `<plugin>-ignore: PHP001, TS001, LAYER001` supported. Helpers `line_has_ignore` and `file_has_ignore` in the rule engine. Metrics record both "blocked violations" and "ignored violations" — partial suppression is first-class, not a workaround.

### Inline file-mode modifier comments

Source-file comments declare the active stack/layer for the ruleset (e.g., `<plugin>-stack: symfony`), enabling per-file rule tuning without external configuration. Same channel as inline suppression.

### Rolling-log effort-bump trigger

The plugin watches user-prompt text for first-person distress phrases ("i'm stuck", "it keeps failing", "confidence: low") and timestamps them in `$HOME/.cache/<plugin>/effort-signals.log`. At ≥2 signals within 30 minutes, emits a `!! EFFORT BUMP REQUIRED !!` block with the exact `/effort xhigh` command. Log is pruned by time window. Cross-prompt state in a stateless hook.

## API-cost transparency

Whether the plugin discloses runtime cost to users.

### Explicit cost-model section in README

README's "API Cost Model" section quantifies the agent-hook cost at ~$0.15-0.30 per session with a per-hook breakdown table, and provides an explicit opt-out (`agent_hooks: false` in `userConfig`). Rare for plugins to publish cost transparency; novel surface.

## Validation surface coverage

How the plugin self-checks invariants during development.

### Hardcoded script allowlists in CI

CI's `validate-shell-scripts` job and the ShellCheck step list specific scripts by path (`hooks/<name>.sh`, `tests/run-tests.sh`). Adding a new hook requires editing `ci.yml` too. Fragile; surfaces as CI no-ops for new files.

### Schema validators that lag the runtime

The hooks-event-name allowlist in CI predates the runtime's acceptance of new events (PostToolUseFailure, SubagentStop, PreCompact, PostCompact). A patch release of the plugin added these to the allowlist after the runtime started accepting them — validator-as-second-source-of-truth lagging the actual runtime.

### Knowledge-base presence checks with subtle bugs

`validate-knowledge-base` job checks for directory presence and counts files but never compares the count to a minimum, so an empty knowledge directory still passes the existence check. Latent gap that looks like coverage.

## Rule engine across hook + CI lanes

When the same correctness logic runs in both real-time (hook) and pipeline (CI) modes.

### Single rule engine, two invocation lanes

Both `ci/<plugin>-ci.sh` (pipeline-mode CI) and `hooks/post-write-check.sh` (real-time-mode hook) source the same `hooks/lib/pack-loader.sh` and `hooks/lib/rules-engine.sh`. README markets this as "zero drift" — same engine invoked at two different lifecycle points. Adapter pattern (`adapter_detect/run/annotate/comment/exit`) provides four CI-provider implementations (GitHub Actions, GitLab CI, Bitbucket Pipelines, Jenkins). One engine; two surfaces; pluggable CI substrate.

## Cross-role tools

Tools that surfaced under multiple roles in this bin's samples.

### Node + npm

Fills *runtime* (worker daemon, MCP server, npm CLI), *dependency installation* (`npm install --prefix`), *bin-wrapped CLI distribution* (npm bin entry point), and *test stack* (`node --test` test runner) roles.

### bash

Fills *bin-wrapped CLI distribution* (thin exec-wrappers), *hook scripts* (file-guard, post-write-check, session-start), *install scripts* (install-deps.sh), *test stack* (run-tests.sh hierarchical bash test suites), and *failure-signaling envelope* (the `set -uo pipefail` + `trap ERR` pattern).

### SQLite

Fills *state persistence* (`metrics.db` for behavioral metrics) and is consumed by both the worker daemon and the MCP server in a peer-process architecture (per-call DB resolution, atomic writes).

### `jq`

Fills *hook output construction* (building `hookSpecificOutput` JSON, escaping context with `jq -Rs .`), *CI manifest validation* (`jq empty` parseability and `jq` queries for name-equality), and *bin-wrapped CLI input synthesis* (reconstructing the PostToolUse envelope via `jq -n`).

### Python

Fills *helper-script runtime* (session_state.py, metrics-query.py, yaml-parser.py invoked via `python3` on system PATH), *CI inline validation* (heredoc Python in ci.yml steps), and *YAML/markdown parsing in shell scripts* (inline `python3 -c "import yaml; ..."`).

### GitHub Actions cron

Fills *external-change watcher* (weekly/monthly cron workflows polling release pages, API changelogs, community signals) and *CI* (PR validation, release publish on tag).
