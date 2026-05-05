# Sample

Mirrors of `https://github.com/Kanevry/session-orchestrator`. Single-plugin Claude Code distribution of a session-level orchestrator (wave planning, VCS integration, quality gates, persistence, safety hooks). Same source ships across Claude Code, Codex, and Cursor IDE through parallel manifest trees and bootstrap scripts.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root, single plugin entry (`session-orchestrator`) with `source: "./"`. Co-located with `.claude-plugin/plugin.json`. A parallel `.codex-plugin/plugin.json` exists for Codex and `.cursor/rules/*.mdc` for Cursor — three concurrent manifest systems in the same repo, but only `.claude-plugin/marketplace.json` is the Claude marketplace surface.

### Top-level `metadata` wrapper variants

Marketplace document carries both top-level `owner` info AND a nested `metadata.{description, version}` wrapper. `metadata.version` is `"2.0.0"` while `plugin.json.version` is `"3.0.0-dev"` — major-version drift between the marketplace bundle version and the plugin version. Marketplace version is decorative and rarely surfaced to users; lags by a major number with no tooling to detect or sync.

## Plugin source binding

### Relative source pointing to repo root (`./`)

Marketplace entry `"source": "./"` — plugin payload identical to repo root. `strict` field absent (default implicit true; no skill-carving). `skills` override absent on the entry. Plugin-root overlap with repo-root is total — all repo content (including `.github/`, `CHANGELOG.md`, `tests/`, `node_modules/` after install, `scripts/tests/fixtures/`) is inside the plugin filesystem boundary. `.claudeignore` at repo root has only 3 lines (excludes `.orchestrator/metrics/`, `docs/examples/`, `docs/templates/`).

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

All three discoverability dimensions populated: `category: "productivity"`, `tags: ["session-management", "wave-execution", "vcs-integration", "code-review", "agent-orchestration"]` (5 entries), `keywords: ["session", "orchestration", "waves", "gitlab", "github", "quality-gates", "subagents"]` (7 entries). Marketplace entry also sets `description`, `author`, `homepage`, `repository`, `license`. `plugin.json` mirrors fields at the plugin layer.

### `$schema` absence on per-plugin manifests

`marketplace.json` has no `$schema` field. Editor schema-completion and ahead-of-time validation unavailable.

## Version coordination

### Multi-site sprawl (5+ locations)

Version scattered across `plugin.json` (`3.0.0-dev`), `package.json` (`3.0.0-dev`), `marketplace.json metadata.version` (`2.0.0`), README badge (`3.0.0--dev`, shields.io-escaped), CHANGELOG top block (`[3.0.0] - Unreleased`), latest tag (`v3.0.0-rc.1`), and an inline `echo '...v2.0.0...'` banner hardcoded in `hooks.json` SessionStart. Six-plus representations of "pre-release 3.0.0" with three different version strings active simultaneously. No bump script, no CI gate on consistency, no pre-commit hook for version sync. Drift goes uncaught until it surfaces as a user-visible discrepancy.

## Channel distribution

### Pre-release tag suffixes on a single channel

Tags use semver pre-release suffixes — `-alpha.7`, `-alpha.14`, `-beta.1` through `-beta.6`, `-rc.1`. All marked `prerelease: true` in the GitHub Releases API; `v2.0.0` is the only `prerelease: false` stable tag. `plugin.json.version` on `main` is `3.0.0-dev` — installing from `main` lands on a `-dev` semver with no machinery to prevent it. Single marketplace channel; pre-release status communicated via tag-name semantics rather than a parallel `stable-*`/`latest-*` channel.

## Tag and release lifecycle

### Tag-on-main, single branch

Tags placed directly on commits merged to `main`; no `release/*` branches surfaced. Pre-release ladder uses `-alpha.N` / `-beta.N` / `-rc.N` suffixes on the same branch — ten releases (1 stable + 9 pre-release) all attached to `main`. No automated tag-sanity gates; releases appear manually published via `gh release create` (no release workflow file exists).

## Plugin-component registration

### Default convention discovery

`plugin.json` declares no component fields (no `skills`, `commands`, `hooks`, `agents`, `mcpServers` arrays). Components picked up from conventional directories. `hooks/hooks.json` and `.mcp.json` at conventional locations. Components observed: 13 skills under `skills/`, 7 commands under `commands/`, 6 agents under `agents/`, `hooks/hooks.json` with 5 event matchers, `.mcp.json` (1 server), 3 output-styles markdown files under `output-styles/`. No `bin/` directory, no `.lsp.json`, no `monitors.json`.

## Component composition

### Skills (universal)

13 skills under `skills/`. One skill (`vault-sync`) ships its own `package.json` with runtime deps and its own test suite (`skills/vault-sync/tests/schema-drift.test.mjs`); CI workflow includes a separate `(cd skills/vault-sync && npm install ...)` step before the main `npm test`.

### Commands

7 commands under `commands/`.

### Agents

6 agents under `agents/`. Frontmatter fields used: `name`, `description` (with inline `<example>` HTML-like blocks per CLAUDE.md convention), `model` (values: `sonnet`, `inherit`), `color`, `tools`. CLAUDE.md documents that "tools MUST be a comma-separated string, NOT a JSON array" and "description MUST be a single-line inline string, NOT a YAML block scalar" as known validation-failure pitfalls.

### Hooks

`hooks/hooks.json` with 5 event matchers — 3 PreToolUse + 1 PostToolUse + 1 SessionStart. Hook handlers are `.mjs` files invoked via `node "$CLAUDE_PLUGIN_ROOT/hooks/<name>.mjs"`.

### MCP servers

`.mcp.json` registers one server, spawned via `bash -c "exec bash ..."` against `scripts/mcp-server.sh`. Path resolved through cascading env-var fallback: `${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}` — supports invocation from Claude, Codex, or git working tree.

### output-styles, monitors

3 markdown files under `output-styles/` (`session-report.md`, `finding-report.md`, `wave-summary.md`); `monitors.json` absent.

## Agent declaration conventions

### Plain tool-name list

Agents declare `tools` as a comma-separated string of plain tool names — e.g. `tools: Read, Edit, Write, Glob, Grep, Bash`. Not permission-rule syntax (no `Bash(…)` forms). CLAUDE.md explicitly enforces this format as a known validation-failure pitfall.

### Standard fields plus model / color

Frontmatter carries `name`, `description`, `model` (values: `sonnet`, `inherit`), `color`, `tools`. Description embeds inline `<example>` HTML-like blocks; CLAUDE.md prescribes single-line inline-string format (no YAML block scalar).

## Plugin-runtime root resolution

### Cascading multi-host fallback

`.mcp.json` and shared shell launchers resolve the plugin tree via `${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}` — Claude env var first, Codex env var second, git working tree third. Same wrapper code ships into Claude, Codex, and Cursor; the cascade lets each host find the plugin without per-runtime branches.

## Dependency installation

### Manual `npm install` post-install

No `SessionStart` hook for install. README instructs users to `cd $(claude plugin dir session-orchestrator)` and run `npm install` once. `node_modules/` materializes inside the plugin root (not `${CLAUDE_PLUGIN_DATA}`). Runtime dep is `zx ^8.1.0`; dev deps include eslint, prettier, vitest, @eslint/js. `engines.node >= 20.0.0` declared in `package.json`. Change detection is the user reading `ls node_modules/zx` (README documents this as the diagnostic). Failure mode is silent — if `npm install` was never run, hook handlers fail at `import` time before any top-level `try/catch` engages, producing `Cannot use import statement outside a module` or `SyntaxError` at runtime. Manual `npm install` is the README's #1 troubleshooting item. CI additionally runs `(cd skills/vault-sync && npm install ...)` for a nested skill that has its own `package.json` with runtime deps. Deviates explicitly from the docs-prescribed `diff -q`-with-rm-on-failure retry pattern. CHANGELOG flags Node 18 as unsupported; `hardening.mjs` exports `assertNodeVersion`, but no automated check at hook invocation independently verified.

## Install change detection

### Out-of-band user check

User runs `ls node_modules/zx` to verify install. No automated detection. Failures surface as runtime import errors when hooks fire.

## Install trigger and lifecycle

### User-invoked one-shot installer

Install is not a hook. User runs `npm install` once in the plugin cache directory after `/plugin install`. Cross-IDE installs go through `scripts/codex-install.sh` and `scripts/cursor-install.sh` for non-Claude hosts.

## Install failure posture

### Silent failure (no install hook at all)

No install hook; install never runs automatically. Failure surfaces only when the missing dependency is needed at runtime — hook handler imports `zx` and crashes with `Cannot use import statement outside a module`. Documented as a troubleshooting path the user must follow manually. Trade-off: zero install-machinery cost; user-discovery burden.

## User configuration and authentication

### Markdown block in consumer's CLAUDE.md

Plugin parses a `## Session Config` block from the consumer repo's `CLAUDE.md` or `AGENTS.md` via `scripts/lib/config.mjs`. Fields: `test-command`, `typecheck-command`, `lint-command`, `persistence`, `enforcement`, `agents-per-wave`, `waves`, `allow-destructive-ops`. Validated against a homegrown JSON-Schema (`scripts/lib/config-schema.mjs`) by `scripts/validate-config.mjs`. Bypass env var (`SO_SKIP_CONFIG_VALIDATION=1`) lets users opt out for emergencies. The plugin re-implements parser + validator rather than using Claude Code's `userConfig` mechanism. Plugin runs its own orchestrator against itself — `CLAUDE.md` at repo root contains a real `## Session Config` block; `tests/integration/parse-config-validator.test.mjs` exercises this dogfooding.

### No user-supplied config

`plugin.json` has no `userConfig` block. Two configuration surfaces coexist — Claude Code's `userConfig` (unused) and the plugin's own Session Config parsed from CLAUDE.md. The platform mechanism is bypassed entirely.

## Session context loading

### Plain-stdout context banner

`hooks/hooks.json` SessionStart runs two handlers. First handler is a literal `echo '🎯 Session Orchestrator v2.0.0 — …'` — a plain-stdout banner pushed via `echo`, not structured `additionalContext` JSON. Banner version (`v2.0.0`) is hardcoded in `hooks.json` and diverges from `plugin.json.version` (`3.0.0-dev`) — yet another version-drift surface.

### Install plus session telemetry

Second SessionStart handler is `node on-session-start.mjs` (async, timeout 5s) — emits an `orchestrator.session.started` event to `.orchestrator/metrics/events.jsonl` and optionally POSTs to a Clank Event Bus webhook. Informational only; never blocks. Session-context loading proper happens through the `session-start` skill (invoked via `/session` command) which reads `STATE.md`, Session Config, git state, etc. — skill-mediated, not hook-injected.

## SessionStart matcher scope

### Explicit subset

SessionStart matcher declared as `startup|clear|compact` — explicitly excluding `resume`. All three included sub-events fire both the banner and the telemetry handler.

## Tool-use enforcement

### Fail-closed scope and command guards (belt-and-suspenders)

Three `PreToolUse` hooks fire on the `Edit|Write` and `Bash` matchers, plus one `PostToolUse` hook. `enforce-scope.mjs` (matcher `Edit|Write`, timeout 5s) blocks edits outside `wave-scope.json` allowedPaths. `pre-bash-destructive-guard.mjs` (matcher `Bash`, timeout 5s) blocks destructive ops per a 13-rule policy in `.orchestrator/policy/blocked-commands.json`. `enforce-commands.mjs` (matcher `Bash`, timeout 5s) blocks commands per `wave-scope.json.blockedCommands` (with a fallback safety list when absent). `post-edit-validate.mjs` (matcher `Edit|Write`, timeout 5s) runs incremental typecheck on edited files; informational only, fail-open `.catch(() => process.exit(0))`. Security-critical hooks wrap their bodies in `main().catch((e) => emitDeny(...))` so any unhandled error denies the call. Output convention centralized in `scripts/lib/io.mjs` with `emitAllow`/`emitDeny`/`emitWarn`/`emitSystemMessage` helpers — uniform JSON wire format on stdout (`{"permissionDecision":"deny","reason":"..."}` plus exit 2 for deny; exit 0 silent for allow); stderr `⚠ ` prefix for warn + exit 0. `emitDeny` requires a non-empty reason (throws `TypeError` if missing) — silent-deny is structurally unrepresentable. `readStdin()` applies a 1 MB byte guard plus 5s `AbortController` timeout; both rejections bubble to the top-level catch. `wave-scope.json.enforcement` field defaults to `"strict"` (fail-closed) when absent — CHANGELOG 2.0.0 Security entry documents this default. Bypass via `allow-destructive-ops: true` in Session Config opts out of `pre-bash-destructive-guard.mjs` only — user-controlled kill switch. Path normalization: `enforce-scope.mjs` coerces Windows path separators (`path.sep → '/'`) before glob matching (REQ-05) and realpath-resolves both projectRoot and target file (REQ-03, with ENOENT ancestor-walk fallback for not-yet-existing Write targets) to block symlink-escape. Dual-output contract: stdout JSON envelope + stderr human message + `process.exit(2)` — documented rationale that "exit 2 alone is silently discarded by the current runtime."

### Numbered-requirement traceability annotations

Every security-critical hook (`enforce-scope.mjs`, `enforce-commands.mjs`) opens with a top-of-file `SECURITY notes (inline refs)` block listing `REQ-01` through `REQ-08`. Every relevant function carries an inline `// SECURITY-REQ-NN:` comment citing the requirement (e.g., `// SECURITY-REQ-03: resolve symlinks ...`). Traceability from a security pre-review document into specific lines of code; reviewer can confirm coverage by grep rather than re-deriving the threat model.

### Stop-event handlers for session-end aggregation

`on-stop.mjs` handles both `Stop` and `SubagentStop` events by discriminating via `hook_event_name` with `agent_name` fallback. Single file, two hook events, exploiting the common payload shape. Fail-open posture (`exit 0` always).

## Hook handler runtime

### Node `.mjs` files invoked via `node`

All hook handlers are `.mjs` files invoked as `node "$CLAUDE_PLUGIN_ROOT/hooks/<name>.mjs"` in `hooks.json`. The handlers carry `#!/usr/bin/env node` shebangs but the shebang is vestigial — invocation is always through explicit `node`. Uses ES module `import` syntax (Node 20+ required by `engines`).

## Hook output contract

### Stderr for human display + stdout JSON for harness

Centralized helpers in `scripts/lib/io.mjs` produce a uniform wire format: stdout JSON for the harness's permission-decision schema (`{"permissionDecision":"deny","reason":"..."}` with `hookSpecificOutput` wrapper), stderr human-readable messages (with `⚠ ` glyph prefix for warnings), and `process.exit(2)` for deny / `exit 0` for allow. Both channels emit in parallel — a consumer who picks just one would have hooks that appear to work in tests but silently pass in production.

## Hook failure posture

### Mixed posture (fail-closed for security, fail-open for context)

Security hooks (`enforce-scope.mjs`, `enforce-commands.mjs`, `pre-bash-destructive-guard.mjs`) wrap top-level catch to `emitDeny` — any unhandled error denies. Informational hooks (`post-edit-validate.mjs`, `on-session-start.mjs`, `on-stop.mjs`) wrap top-level catch to `process.exit(0)` — fail-open, never blocks. Pattern is explicit (commented as `SECURITY-REQ-01 (fail-closed)`) and mirrored across the hook suite.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Hooks read code from `$CLAUDE_PLUGIN_ROOT/hooks/*.mjs`. Persistent runtime state (telemetry events, metrics) is written to `.orchestrator/metrics/events.jsonl` in the consumer's project directory rather than `${CLAUDE_PLUGIN_DATA}` — the plugin's state is project-scoped, not plugin-scoped. `node_modules/` materializes inside the plugin root after manual `npm install`.

## State persistence

### Runtime policy file tree

`.orchestrator/policy/*.json` holds runtime policies — `blocked-commands.json` with 13 rules, `ecosystem.schema.json`, `quality-gates.schema.json` plus `.example.json`. Hooks read policy plus consumer `wave-scope.json`; the gate between is a JSON-Schema contract rather than inline rules. "Pluggable policy JSON loaded per invocation" pattern — policy can change without redeploying hooks.

## Live monitoring

### `monitors.json` absent

No `monitors.json` file. Notification surface is hook-driven (skill-mediated banners and event-bus telemetry) rather than the v2.1.105+ monitors API.

### Update notification mechanism

No update poller. `/plugin update` is the only update path. CHANGELOG entries explicitly track Node version requirements and breaking-change migration notes (e.g., bash → mjs hook migration in v3.0.0).

## Telemetry and self-evaluation

### JSONL append plus optional remote POST

`scripts/lib/events.mjs` writes structured events as JSONL appends to `.orchestrator/metrics/events.jsonl`. When `CLANK_EVENT_SECRET` env var is set, events also POST to a configurable webhook via native `fetch` plus `AbortSignal.timeout(3000)`; errors are swallowed so remote failures never affect local execution. Local logging is always on; remote forwarding is opt-in by environment.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` has no `dependencies` field. Single-plugin marketplace; tags use plain `vX.Y.Z` form (no `<plugin>--v<version>` cross-plugin pinning format).

## Testing

### vitest with multi-suite layout

Vitest as the primary runner, configured via `vitest.config.mjs` to glob both top-level `tests/**/*.test.mjs` and nested skill-local `skills/*/tests/**/*.test.mjs`. Tests organized into `hooks/`, `integration/`, `lib/`, `skills/`, `unit/`, `fixtures/` subdirs at repo root. Replaces an earlier bats-based suite (retired in v3.0.0 per CHANGELOG; `scripts/test/run-all.sh` removed on 2026-04-20 in commit `d41e00e`). Direct invocation via `npm test` → `vitest --run`. Typecheck delegated to a custom `node scripts/typecheck.mjs` rather than `tsc`. Nested skill `skills/vault-sync` carries its own `package.json` and test suite (`schema-drift.test.mjs`); CI runs `(cd skills/vault-sync && npm install ...)` as a separate step before `npm test` to bootstrap the skill's runtime deps. CHANGELOG claims "546 pass, 10 skipped" total.

## CI workflow shape

### Push + PR matrix CI

`.github/workflows/test.yml` triggers on `push: branches: [main]` and `pull_request` (any target). No tag trigger. CI does: `npm ci`, nested `(cd skills/vault-sync && npm install ...)`, `npm run lint` (eslint), conditional `npm run typecheck` (only if `.mjs` files exist in `hooks/` or `scripts/lib/`), `npm test` (vitest). Plus per-OS `jq` install step (apt-get on Linux, brew on macOS). OS matrix: `ubuntu-latest`, `macos-latest`, `windows-latest` (3-OS). No Node-version matrix (pinned to Node 20 via `actions/setup-node`). `fail-fast: false`. Action pinning is SHA + tag-comment: `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5  # v4.3.1`, `actions/setup-node@39370e3970a6d050c480ffad4ff0ed4d3fdee5af  # v4.1.0`. Caching via built-in `actions/setup-node` npm cache (`cache: npm`); no separate `actions/cache` step. Concurrency group `${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true` — rapid push supersedes queued runs. `timeout-minutes: 15` per job. `permissions: contents: read` (minimum for checkout, no write). No manifest validation step. `.gitlab-ci.yml` (~4.3 KB) at repo root for the GitLab mirror referenced throughout CHANGELOG, not deeply inspected.

## Marketplace validation

### Homegrown validators not wired to CI

A `scripts/validate-plugin.sh` (~12.3 KB) exists at repo root — not surfaced via CI. `scripts/validate-wave-scope.sh` (~5.2 KB) validates runtime `wave-scope.json`. `scripts/validate-config.mjs` validates the plugin's Session Config in consumer repos. None invoke `claude plugin validate`. `scripts/lib/agent-frontmatter.mjs` plus `tests/lib/agent-frontmatter.test.mjs` (~11.7 KB tests) enforce the comma-separated-tools / single-line-description rules documented in CLAUDE.md — runs via vitest, not via dedicated CI gate. Defense in depth but no enforcement at the marketplace manifest layer.

## Release automation

### No release automation / manual

Only `.github/workflows/test.yml` exists; no release workflow. Ten GitHub releases (1 stable + 9 pre-release) all manually published. `prerelease: true` flag set correctly on pre-release semver. CHANGELOG hand-maintained (Keep-a-Changelog format, ~55.9 KB). No automated `gh release create`, no tag-sanity gates, no draft releases. Absent release automation is notable given the otherwise-heavy CI investment — version drift across `plugin.json` / `package.json` / `marketplace.json metadata.version` / README badge / `hooks.json` banner is a manual-maintenance hazard that automation would catch.

## Documentation surface

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` at repo root, ~19.5 KB (405 lines) — install instructions for 3 IDEs (Claude Code, Codex, Cursor), troubleshooting, platform-support matrix, features overview. `docs/plugin-architecture-v3.md` (~13.9 KB) plus `docs/migration-v3.md` (~6.9 KB) — placed under `docs/`, not at repo root. `CLAUDE.md` at repo root, ~4.5 KB (96 lines) — project operational procedures, agent authoring pitfalls, structure overview, destructive-command-guard documentation, v3.0 migration status, v2.0 feature list, Session Config block. CHANGELOG.md at repo root, ~55.9 KB Keep-a-Changelog format with per-session dev-trail entries during pre-release cycles, stable release blocks, migration sections; tracks GitLab issue numbers (e.g., `#131`, `#124`).

### Keep-a-Changelog with root-cause prose

CHANGELOG.md exceptionally detailed (~55.9 KB) — per-session dev-trail entries during pre-release cycles, stable release blocks, migration sections. Captures CHANGELOG-as-durable-engineering-log intensity. Tracks GitLab issue numbers explicitly.

### Heavy doc surface with meta-project artifacts

`docs/prd/` directory contains detailed PRDs (e.g. `2026-04-18-windows-native-support.md`, ~24 KB) — documentation-as-code practice for feature specs. `docs/USER-GUIDE.md` is ~59.8 KB, a substantial standalone manual. `CONTRIBUTING.md` at ~22.2 KB is longer than many projects' READMEs.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` (MIT) at repo root with SPDX `MIT`. `plugin.json` and `marketplace.json` carry matching `license` field. README references the same. GitHub auto-detects and badges MIT. All sources agree.

## Community health files

### Open contribution with health files

Full community health surface — `SECURITY.md` (~5 KB, response SLA + enforcement-architecture overview), `CONTRIBUTING.md` (~22.2 KB), `CODE_OF_CONDUCT.md` (~5.5 KB), `.github/ISSUE_TEMPLATE/bug_report.md` + `feature_request.md`, `.github/pull_request_template.md`. `SECURITY.md` still references `enforce-scope.sh` and `enforce-commands.sh` (the pre-v3 Bash file names) — stale; should read `.mjs` post-v3.

## Cross-platform discipline

### Documented Windows-native migration

CHANGELOG `[3.0.0]` entry explicitly enumerates each cross-platform concern: `os.tmpdir()` replaces `${TMPDIR:-/tmp}`, `path.parse(dir).root` replaces `/`-terminator for filesystem walks, Windows backslash normalization before glob matching, CRLF-tolerant config parsing, `.gitattributes` EOL rules. Pattern: windows-native as a documented migration. `docs/prd/<date>-windows-native-support.md` (~24 KB) drives the migration with a written PRD, not just CHANGELOG bullets.

## Multi-runtime portability

### Triple-runtime parallel manifests

Repo ships three parallel manifest trees: `.claude-plugin/marketplace.json` + `plugin.json` for Claude Code, `.codex-plugin/plugin.json` for Codex, and `.cursor/rules/*.mdc` for Cursor IDE. Same `scripts/` and `skills/` trees serve all three. Bootstrap scripts (`scripts/codex-install.sh`, `scripts/cursor-install.sh`) adapt the same skills/agents/hooks to each host. Shared `platform.mjs` exposes `SO_PLATFORM`, `SO_IS_WINDOWS`, `SO_IS_WSL` constants so library code can branch by host without duplicating logic. Cross-runtime resolution chain (`${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}`) supports invocation from any host.

## Cross-ecosystem distribution

### Triple-ecosystem (Claude + Codex + Cursor)

Single repo serves Claude Code, Codex, and Cursor IDE through three concurrent manifest systems. Bootstrap scripts adapt the shared content per host. `platform.mjs` exposes constants (`SO_PLATFORM`, `SO_IS_WINDOWS`, `SO_IS_WSL`) so shared library code can branch by host. Cascading runtime resolution chain (`${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}`) supports invocation from any host. Constrains every install-side change to be tested across three ecosystems and pushes the plugin into a "lowest common denominator" portion of each host's API surface.

## Distribution exclusion and dogfood layout

### Lockfile and node_modules inside plugin root

`package-lock.json` (~82 KB) ships inside the plugin filesystem. `node_modules/` materializes inside the plugin root after the user runs `npm install`. The `.claudeignore` filter at repo root has only 3 entries (excludes `.orchestrator/metrics/`, `docs/examples/`, `docs/templates/`) and does not gate the lockfile or future module trees. Constrains plugin update behavior — re-installing the plugin without clearing `node_modules/` produces a stale module tree the user must manually purge.

## Output styles

### Shared markdown templates under `output-styles/`

3 markdown files at `output-styles/` — `session-report.md`, `finding-report.md`, `wave-summary.md` — define the prescribed output shape for skill or agent emissions. Agents and skills reference these by path, ensuring report consistency across the plugin's surface. Layer not always documented in plugin docs but legitimately registered via convention discovery.

## Cross-role tools

### Node + npm + npx

Fills hook-handler runtime (`.mjs` files invoked via `node`), dependency installation (manual `npm install` for `zx ^8.1.0` and dev deps), test stack (vitest via `npm test`), and skill-local nested install (`(cd skills/vault-sync && npm install ...)` in CI). `engines.node >= 20.0.0`.

### bash

`scripts/mcp-server.sh` (~5.3 KB) is the MCP server entry point spawned via `bash -c "exec bash ..."` from `.mcp.json`. `scripts/codex-install.sh` and `scripts/cursor-install.sh` adapt the plugin to non-Claude hosts. `scripts/validate-plugin.sh` (~12.3 KB) and `scripts/validate-wave-scope.sh` (~5.2 KB) provide manual validation surfaces.

### `${CLAUDE_PLUGIN_ROOT}` env var

First tier of the cascading multi-host resolution chain (`${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}`). Required by `.mcp.json` command and shared shell launchers.

### `hookSpecificOutput.additionalContext`

Not used. SessionStart context is pushed via plain `echo` stdout (banner) rather than structured `additionalContext` JSON. Skill-mediated context loading uses the `session-start` skill instead.

### `plugin.json.version`

Drift surface — `plugin.json.version` (`3.0.0-dev`) does not match `marketplace.json metadata.version` (`2.0.0`), `hooks.json` SessionStart banner (`v2.0.0`), README badge (`3.0.0--dev`), or CHANGELOG top block (`[3.0.0] - Unreleased`). Latest tag is `v3.0.0-rc.1`. Six-plus representations of "pre-release 3.0.0" with three different version strings active simultaneously.

### Git as state substrate

`.orchestrator/metrics/events.jsonl` written into the consumer's project directory; `worktree.mjs` (referenced in `on-stop.mjs` and CHANGELOG) creates and cleans up worktrees for parallel agent execution. Plugin operates on git state directly via `zx`-wrapped shell-outs.
