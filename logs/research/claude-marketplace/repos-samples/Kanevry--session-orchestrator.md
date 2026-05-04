# Kanevry/session-orchestrator

## Identification

- **URL**: https://github.com/Kanevry/session-orchestrator
- **Stars**: 55 (observed 2026-04-20)
- **Last commit date**: 2026-04-20 (commit `b8c5446`, "fix(ci): install nested skills/vault-sync deps before tests")
- **Default branch**: `main`
- **License**: MIT (SPDX `MIT`, `LICENSE` present)
- **Sample origin**: primary (community)
- **One-line purpose**: "Session-level orchestration for Claude Code — wave planning, VCS integration, quality gates, persistence, and safety checks" (from `marketplace.json` metadata.description; plugin.json description is a near-duplicate).

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root; one plugin (`session-orchestrator`) sourced from `./` (self-publishing single-plugin marketplace). A parallel `.codex-plugin/plugin.json` exists for Codex but is not part of the Claude marketplace.
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper — both top-level owner info AND nested `metadata` block present. `metadata.version` is `"2.0.0"` (lags the plugin's `3.0.0-dev` in `plugin.json` — see version authority).
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: all three — `category` (`productivity`), `tags` (5 entries: session-management, wave-execution, vcs-integration, code-review, agent-orchestration), and `keywords` (7 entries: session, orchestration, waves, gitlab, github, quality-gates, subagents). Also sets `description`, `author`, `homepage`, `repository`, `license` on the marketplace entry.
- **`$schema`**: absent.
- **Reserved-name collision**: no. Marketplace name `kanevry` is vendor-branded; not a reserved word.
- **Pitfalls observed**:
    - Marketplace version (`2.0.0` in metadata) diverges from plugin version (`3.0.0-dev` in `plugin.json`). Docs treat relative sources as "plugin.json is authoritative"; marketplace version appears decorative here but creates a drift surface.
    - Repo also contains `.codex-plugin/plugin.json` and `.cursor/rules/*.mdc` — cross-ecosystem support means the marketplace.json is only one of three concurrent manifest systems in the same repo.

## 2. Plugin source binding

- **Source format(s) observed**: relative only — `"source": "./"`.
- **`strict` field**: not present on the entry (default implicit true per docs; no evidence of `strict: false` carving).
- **`skills` override on marketplace entry**: absent.
- **Version authority**: `plugin.json` only when binding is relative (per docs); `marketplace.json` carries a separate `metadata.version` field that does not match and appears to be treated as marketplace-bundle version rather than plugin version.
- **Pitfalls observed**:
    - Plugin-root overlap with repo-root is total (`source: "./"`) — all repo content is inside the plugin, including `.github/`, `CHANGELOG.md`, `tests/`, `node_modules/` (after install), `scripts/tests/fixtures/`. No `.claudeignore` filter at plugin boundary beyond `.claudeignore`'s 3 lines at repo root (excludes `.orchestrator/metrics/`, `docs/examples/`, `docs/templates/`).
    - `package-lock.json` (82 KB) ships inside the plugin; `npm install` must be run post-install, widening the pre-condition surface.

## 3. Channel distribution

- **Channel mechanism**: no split — single marketplace. Pre-release channel is implicit via pre-release tags (`v3.0.0-rc.1`, `v2.0.0-beta.*`, `v2.0.0-alpha.*`) on the same marketplace; users pin via `@ref`.
- **Channel-pinning artifacts**: absent (no `stable-tools`/`latest-tools`-style separate manifests). Only one `marketplace.json`.
- **Pitfalls observed**:
    - `plugin.json` version is `3.0.0-dev` on `main` — a plugin installed from `main` ships with a -dev semver; no indication this is gated behind a channel. Docs permit dev suffixes but there's no machinery here to prevent installing prerelease from HEAD.

## 4. Version control and release cadence

- **Default branch name**: `main`.
- **Tag placement**: observed tags on the default branch (GitHub releases attached to tagged commits on `main`). No `release/*` branches surfaced through `gh api`.
- **Release branching**: none — tag-on-main.
- **Pre-release suffixes**: yes — extensive. Observed: `-alpha.7`, `-alpha.14`, `-beta.1` through `-beta.6`, `-rc.1`. All marked `prerelease: true` in the GitHub Releases API. `v2.0.0` is the only `prerelease: false` stable tag.
- **Dev-counter scheme**: absent in the claude-plugins `0.0.z` sense. Uses pre-release semver suffixes (`3.0.0-dev` in `plugin.json` on main, `3.0.0-rc.1` as the latest tag) rather than a monotonically-incrementing dev-build counter.
- **Pre-commit version bump**: no pre-commit hook for version bumps observed. Version is hand-maintained in `plugin.json`, `package.json`, marketplace.json (3 sources).
- **Pitfalls observed**:
    - Three version-bearing files (`plugin.json` = `3.0.0-dev`, `package.json` = `3.0.0-dev`, `marketplace.json metadata.version` = `2.0.0`) drift manually. No CI gate on consistency observed.
    - README badge text is `3.0.0--dev` (shields.io-escaped); CHANGELOG top block is `[3.0.0] - Unreleased`; latest tag is `v3.0.0-rc.1`. Three different representations of "pre-release 3.0.0".

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` declares no component fields (no `skills`, `commands`, `hooks`, `agents`, `mcpServers` arrays). Components are picked up from conventional directories. `hooks/hooks.json` is present at the conventional location; `.mcp.json` is at the conventional location.
- **Components observed**: skills YES (13 skills under `skills/`), commands YES (7 under `commands/`), agents YES (6 under `agents/`), hooks YES (`hooks/hooks.json` with 5 event matchers), `.mcp.json` YES (1 server), `.lsp.json` no, monitors no (`monitors.json` absent), `bin/` no, output-styles YES (3 under `output-styles/`).
- **Agent frontmatter fields used**: `name`, `description` (with inline `<example>` blocks), `model` (values: `sonnet`, `inherit`), `color`, `tools`. CLAUDE.md documents the exact constraints (see pitfalls).
- **Agent tools syntax**: plain comma-separated tool names in a string — e.g. `tools: Read, Edit, Write, Glob, Grep, Bash`. Not permission-rule syntax (no `Bash(…)` forms). CLAUDE.md calls out that "tools MUST be a comma-separated string, NOT a JSON array" as a known validation-failure pitfall.
- **Pitfalls observed**:
    - `description` frontmatter contains inline `<example>` HTML-like blocks — a specific convention noted in CLAUDE.md: "description MUST be a single-line inline string, NOT a YAML block scalar".
    - `.mcp.json` spawns a bash script (`scripts/mcp-server.sh`) via `bash -c "exec bash ..."` using `${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}`. Cascading env-var fallback supports Codex + git-only invocations; undermines the "pure Node, no bash" v3 claim.
    - Output-styles exist (3 markdown files) despite being undocumented in the plugin docs captured; they encode report formats for skills to reference.

## 6. Dependency installation

- **Applicable**: yes — Node runtime deps (`zx`) are required for hooks; user must run `npm install` once in the plugin dir after install.
- **Dep manifest format**: `package.json` at plugin root. Runtime dep: `zx ^8.1.0`. Dev deps: eslint, prettier, vitest, @eslint/js. `engines.node >= 20.0.0`.
- **Install location**: `$(claude plugin dir session-orchestrator)` — i.e., the plugin cache dir, NOT `${CLAUDE_PLUGIN_DATA}`. README documents this. `node_modules` materializes inside the plugin root after user action.
- **Install script location**: no SessionStart-hook-driven install. Manual: README instructs user to `cd` to plugin dir and run `npm install`. No `diff -q`-style drift detection, no `rm-on-failure` retry-next-session invariant, no pointer file.
- **Change detection**: existence only — README diagnostic is `ls node_modules/zx`. No sha256 or diff.
- **Retry-next-session invariant**: not applicable — no install hook. Failure mode is "hooks silently no-op", diagnosed from `Cannot use import statement outside a module` at runtime.
- **Failure signaling**: if `npm install` was never run, hooks fail at `import` time. Docs call this "silent no-op" — user sees nothing until they hit `SyntaxError` or `Cannot use import statement` on a real Bash command. Enforcement hooks' top-level `try/catch` catches the import error? No — import failures happen before `main()` is defined, so `emitDeny` fallback does not fire. Actual observed behavior per README: silent.
- **Runtime variant**: Node via `npm` / `npm ci`. No uv, no uvx, no bun.
- **Alternative approaches**: none — single-path `npm install` manual bootstrap.
- **Version-mismatch handling**: `engines.node >= 20.0.0` declared in `package.json`; CHANGELOG flags Node 18 as unsupported. No automated check at hook invocation; `hardening.mjs` exports `assertNodeVersion` per CHANGELOG but wiring not independently verified.
- **Pitfalls observed**:
    - Manual `npm install` requirement is the #1 troubleshooting item in README. Breaks the "plugin install = ready" expectation docs set for other patterns.
    - The docs-prescribed `diff -q` + `rm`-on-failure retry pattern is NOT used here. This is a clear deviation from the docs-worked-example for dep install.
    - CI workflow (`test.yml`) additionally runs `(cd skills/vault-sync && npm install ...)` — a nested second `package.json` inside a skill that itself has runtime deps. Nested dep trees complicate the "one npm install" story.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — no `bin/` directory at plugin root. `.claude-plugin/plugin.json` declares no `bin` field. Executable entry points are all hooks (`.mjs` invoked via `node` in `hooks.json`) and installer scripts (`scripts/codex-install.sh`, `scripts/cursor-install.sh` for cross-IDE bootstrap — not Claude bins).
- **`bin/` files**: none.
- **Shebang convention**: not applicable (no bin/). Hook files carry `#!/usr/bin/env node` but are invoked as `node "$CLAUDE_PLUGIN_ROOT/hooks/..."` in `hooks.json`, so the shebang is vestigial.
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: not applicable — no Python.
- **Platform support**: not applicable.
- **Permissions**: not applicable.
- **SessionStart relationship**: not applicable.
- **Pitfalls observed**:
    - `.mcp.json` spawns `scripts/mcp-server.sh` via bash `-c` — not a plugin `bin/` entry, but functionally equivalent to a wrapper. Uses `${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}` triple fallback.

## 8. User configuration

- **`userConfig` present**: no — `plugin.json` has no `userConfig` block.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable for plugin-level config. However, the plugin defines a project-level "Session Config" (parsed from the consumer repo's `CLAUDE.md` / `AGENTS.md` by `scripts/lib/config.mjs`) with 7+ fields (`test-command`, `typecheck-command`, `lint-command`, `persistence`, `enforcement`, `agents-per-wave`, `waves`, `allow-destructive-ops`). This is orthogonal to the Claude Code `userConfig` mechanism — it's a plugin-level convention riding on top of `CLAUDE.md`.
- **Pitfalls observed**:
    - Two separate configuration surfaces — Claude Code's `userConfig` (unused) vs the plugin's own "Session Config" parsed from `CLAUDE.md`. The plugin re-implements a parser + validator (`config-schema.mjs` + `validate-config.mjs`) rather than using the platform mechanism. Candidate novel axis — see §17.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 3 entries in `hooks/hooks.json`:
    - matcher `Edit|Write` → `node hooks/enforce-scope.mjs` (timeout 5s). Blocks edits outside `wave-scope.json` allowedPaths.
    - matcher `Bash` → `node hooks/pre-bash-destructive-guard.mjs` (timeout 5s). Blocks destructive ops per 13-rule policy in `.orchestrator/policy/blocked-commands.json`.
    - matcher `Bash` → `node hooks/enforce-commands.mjs` (timeout 5s). Blocks commands per `wave-scope.json.blockedCommands` (fallback safety list when absent).
- **PostToolUse hooks**: 1 entry:
    - matcher `Edit|Write` → `node hooks/post-edit-validate.mjs` (timeout 5s). Incremental typecheck on edited file; informational only, never blocks.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stdout JSON for decisions (`{"permissionDecision":"deny","reason":"..."}`) + exit 2 for deny; exit 0 silent for allow; stderr `⚠ ` prefix for warn + exit 0. Implemented uniformly through `scripts/lib/io.mjs` helpers `emitAllow` / `emitDeny` / `emitWarn` / `emitSystemMessage`.
- **Failure posture**: fail-closed on security-critical hooks. `enforce-scope.mjs` explicit REQ-01: `main().catch((e) => emitDeny(...))` — any unhandled error denies the call. `enforce-commands.mjs` matches. `post-edit-validate.mjs` is informational and fail-open (`.catch(() => process.exit(0))`). `on-session-start.mjs` and `on-stop.mjs` also fail-open — always exit 0.
- **Top-level try/catch wrapping**: observed on every hook. Security hooks wrap to `emitDeny`; informational hooks wrap to `exit 0`. Pattern is explicit (commented as `SECURITY-REQ-01 (fail-closed)` in `enforce-scope.mjs`) and mirrored across the hook suite.
- **Pitfalls observed**:
    - Enforcement level read from `wave-scope.json.enforcement` with default `"strict"` when absent (CHANGELOG 2.0.0 Security: "Scope enforcement defaults to fail-closed (`strict`) when the `enforcement` field is absent"). Explicit docs-call-out of default.
    - Bypass: `allow-destructive-ops: true` in Session Config opts out of `pre-bash-destructive-guard.mjs`. User-controlled kill switch.
    - `hooks.json` also embeds an inline `echo '...v2.0.0...'` banner as the first SessionStart hook. Banner version (`v2.0.0`) is stale vs `plugin.json` (`3.0.0-dev`) — 4th version-drift surface.
    - Path normalization: `enforce-scope.mjs` normalizes Windows path separators (`path.sep → '/'`) before glob matching (REQ-05). Also realpath-resolves symlinks on both projectRoot and target file (REQ-03, with ENOENT ancestor-walk fallback for not-yet-existing Write targets) to block symlink-escape.
    - Centralized `emitAllow/emitDeny/emitWarn/emitSystemMessage` helpers in `scripts/lib/io.mjs` enforce a single wire format across hooks. `emitDeny` requires a non-empty reason (throws `TypeError` if missing) — makes "silent deny" unrepresentable.
    - `readStdin()` in `io.mjs` applies 1 MB byte guard + 5s AbortController timeout on stdin; both rejections bubble to the top-level catch → `emitDeny`.

## 10. Session context loading

- **SessionStart used for context**: only partially. `hooks.json` SessionStart runs two handlers:
    1. `echo '🎯 Session Orchestrator v2.0.0 — …'` — a literal banner via `echo`. Not `additionalContext` JSON.
    2. `node on-session-start.mjs` (async, timeout 5s) — emits `orchestrator.session.started` event to `.orchestrator/metrics/events.jsonl` + optional POST to Clank Event Bus. Informational only.
- **UserPromptSubmit for context**: no — no UserPromptSubmit hook in `hooks.json`.
- **`hookSpecificOutput.additionalContext` observed**: no. Context is pushed via `echo` stdout, not structured `additionalContext` JSON.
- **SessionStart matcher**: `startup|clear|compact` — all three sub-events.
- **Pitfalls observed**:
    - Banner version (`v2.0.0`) hardcoded in `hooks.json` — diverges from `plugin.json` (`3.0.0-dev`). Fifth version-drift surface.
    - The session-start context is instead loaded by the `session-start` skill (invoked via `/session` command) which reads `STATE.md`, Session Config, git state, etc. This is skill-mediated, not hook-injected, so the user experience starts with a slash command rather than auto-populated context.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**:
    - Plugin emits telemetry via `scripts/lib/events.mjs` (JSONL append to `.orchestrator/metrics/events.jsonl`, optional `fetch` POST to a Clank Event Bus when `CLANK_EVENT_SECRET` is set). This is a hook-driven notification system, not the v2.1.105+ monitors API — a parallel concern.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — `plugin.json` has no `dependencies` field.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — not a multi-plugin marketplace (only `session-orchestrator`). Tags use plain `v{version}` form (e.g. `v3.0.0-rc.1`, `v2.0.0-beta.6`).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: vitest (primary). Previously bats (retired in v3.0.0 per CHANGELOG; `scripts/test/run-all.sh` removed on 2026-04-20 in commit `d41e00e`). Nested skill-local tests (`skills/vault-sync/tests/schema-drift.test.mjs`) also run via vitest through the `include: ['tests/**/*.test.mjs', 'skills/*/tests/**/*.test.mjs']` glob in `vitest.config.mjs`.
- **Tests location**: `tests/` at repo root with subdirs `hooks/`, `integration/`, `lib/`, `skills/`, `unit/`, `fixtures/`. Plus nested `skills/vault-sync/tests/` for a skill with its own `package.json`.
- **Pytest config location**: not applicable (not Python).
- **Python dep manifest for tests**: not applicable.
- **CI present**: yes.
- **CI file(s)**: one — `.github/workflows/test.yml`. Plus `.gitlab-ci.yml` (4.3 KB) for the GitLab mirror at `gitlab.gotzendorfer.at/infrastructure/session-orchestrator` referenced throughout CHANGELOG.
- **CI triggers**: `push: branches: [main]` and `pull_request` (any target). No tag trigger.
- **CI does**: `npm ci`, nested `(cd skills/vault-sync && npm install …)`, `npm run lint` (eslint), conditional `npm run typecheck` (only if `.mjs` files exist in `hooks/` or `scripts/lib/`), `npm test` (vitest). Plus per-OS `jq` install step (apt-get on Linux, brew on macOS).
- **Matrix**: OS — `ubuntu-latest`, `macos-latest`, `windows-latest` (3-OS matrix). No Node-version matrix (pinned to Node 20 via `actions/setup-node@…`). `fail-fast: false`.
- **Action pinning**: SHA-pinned — `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5  # v4.3.1`, `actions/setup-node@39370e3970a6d050c480ffad4ff0ed4d3fdee5af  # v4.1.0`. Comment annotations preserve the tag for human readability. Good hygiene.
- **Caching**: built-in `actions/setup-node` npm cache (`cache: npm`). No separate `actions/cache` step.
- **Test runner invocation**: direct `npm test` → `vitest --run`. Typecheck via `node scripts/typecheck.mjs` (custom node-based typecheck, not `tsc`).
- **Pitfalls observed**:
    - Typecheck step is conditional on `.mjs` presence via a pre-check `ls | grep -q .` — a legacy from the Wave 3 migration. Now that .mjs files are landed, the `else` branch never fires; the guard is dead code but harmless.
    - No tag-trigger workflow; no release automation on tag push. All releases appear to be manual `gh release create` per CHANGELOG narrative.
    - Concurrency group `${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true` — rapid push supersedes queued runs.
    - `timeout-minutes: 15` per job. `permissions: contents: read` (minimum for checkout, no write). Good security hygiene.
    - CI does lint + typecheck + test; no manifest validation step (no `claude plugin validate` invocation).

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — the only workflow in `.github/workflows/` is `test.yml`.
- **Release trigger**: not applicable (no release workflow).
- **Automation shape**: none — 10 GitHub releases exist (including `v3.0.0-rc.1`, `v2.0.0`, 6 beta tags, 2 alpha tags) but all appear manually published. `prerelease: true` flag set correctly on pre-release semver.
- **Tag-sanity gates**: none automated. CHANGELOG is hand-maintained.
- **Release creation mechanism**: manual `gh release create` (inferred from lack of workflow).
- **Draft releases**: none observed (`draft: false` on all 10 releases via API).
- **CHANGELOG parsing**: no automation — CHANGELOG is Keep-a-Changelog format (55.8 KB), entries hand-written.
- **Pitfalls observed**:
    - Absent release automation is notable given the otherwise-heavy CI investment. Version-drift across `plugin.json` / `package.json` / `marketplace.json metadata.version` / README badge / `hooks.json` banner is a manual-maintenance hazard that automation would catch.

## 15. Marketplace validation

- **Validation workflow present**: no — no separate marketplace-validation workflow.
- **Validator**: a `scripts/validate-plugin.sh` (12.3 KB) exists at repo root — not surfaced via CI. A `scripts/validate-wave-scope.sh` (5.2 KB) validates runtime `wave-scope.json`. A `scripts/validate-config.mjs` validates the plugin's "Session Config" in consumer repos. None invoke `claude plugin validate`.
- **Trigger**: not wired to CI; manual invocation only.
- **Frontmatter validation**: yes — `scripts/lib/agent-frontmatter.mjs` + `tests/lib/agent-frontmatter.test.mjs` (11.7 KB tests) enforce the comma-separated-tools / single-line-description rules documented in CLAUDE.md. Not wired to CI; runs via vitest.
- **Hooks.json validation**: no dedicated validator observed.
- **Pitfalls observed**:
    - Homegrown validators exist but are not wired to CI gates; they are library/skill-invoked. "Defense in depth but no enforcement at the marketplace manifest layer."

## 16. Documentation

- **`README.md` at repo root**: present, 405 lines (19.5 KB). Install instructions for 3 IDEs (Claude Code, Codex, Cursor), troubleshooting, platform-support matrix, features overview.
- **`README.md` per plugin**: not applicable (single plugin, plugin root = repo root).
- **`CHANGELOG.md`**: present, Keep-a-Changelog format, 55.9 KB. Exceptionally detailed — per-session dev-trail entries during pre-release cycles, stable release blocks, migration sections. Tracks GitLab issue numbers (e.g., `#131`, `#124`).
- **`architecture.md`**: present at `docs/plugin-architecture-v3.md` (13.9 KB) plus `docs/migration-v3.md` (6.9 KB). Not at repo root; placed under `docs/`.
- **`CLAUDE.md`**: present at repo root, 96 lines (4.5 KB). Project operational procedures: agent authoring pitfalls, structure overview, destructive-command-guard documentation, v3.0 migration status, v2.0 feature list, Session Config block. Also used as the plugin's own Session Config test-subject.
- **Community health files**: `SECURITY.md` (5 KB, response SLA + enforcement-architecture overview), `CONTRIBUTING.md` (22.2 KB — unusually large), `CODE_OF_CONDUCT.md` (5.5 KB), `.github/ISSUE_TEMPLATE/bug_report.md` + `feature_request.md`, `.github/pull_request_template.md`. Full set.
- **LICENSE**: present (`MIT`, SPDX `MIT`).
- **Badges / status indicators**: observed — 4 shields.io badges at README top (License: MIT, Version: 3.0.0-dev, Claude Code Plugin, Codex Compatible, Cursor IDE Compatible). No CI-status badge.
- **Pitfalls observed**:
    - `SECURITY.md` still refers to `enforce-scope.sh` and `enforce-commands.sh` (the pre-v3 Bash file names). Stale; should read `.mjs` post-v3.
    - `docs/prd/` directory contains detailed PRDs (e.g. `2026-04-18-windows-native-support.md`, 24 KB) — documentation-as-code practice for feature specs.
    - `docs/USER-GUIDE.md` is 59.8 KB — a substantial standalone manual.
    - `CONTRIBUTING.md` at 22 KB is longer than many projects' README; likely includes extensive workflow prescriptions for the orchestrator-assisted development loop this plugin itself runs.

## 17. Novel axes

Open design choices that don't fit cleanly into purposes 1-16:

- **Cross-IDE plugin triple**: Single repo ships Claude Code plugin (`.claude-plugin/`), Codex plugin (`.codex-plugin/`), and Cursor IDE rules (`.cursor/rules/*.mdc`) with aligned semantics. Install scripts (`scripts/codex-install.sh`, `scripts/cursor-install.sh`) adapt the same skills/agents/hooks to each host. `platform.mjs` exposes `SO_PLATFORM`, `SO_IS_WINDOWS`, `SO_IS_WSL` to let shared libs branch. This is a cross-ecosystem pattern not captured in the current pattern doc.
- **Two-tier config surface**: Plugin does NOT use Claude Code's `userConfig`; instead it parses a Markdown `## Session Config` block from the consumer repo's `CLAUDE.md`/`AGENTS.md` via `scripts/lib/config.mjs`. This becomes a first-class artifact with its own JSON-Schema (`scripts/lib/config-schema.mjs`) and bypass env var (`SO_SKIP_CONFIG_VALIDATION=1`). Candidate for a separate "project-level config parsing" axis — the plugin sources its runtime behavior from prose in a user-editable Markdown block.
- **Runtime policy-file tree**: `.orchestrator/policy/*.json` holds runtime policies (`blocked-commands.json` with 13 rules, `ecosystem.schema.json`, `quality-gates.schema.json` + `.example.json`). Hook reads policy + consumer `wave-scope.json`; the gate between is a JSON-Schema contract rather than inline rules. "Pluggable policy JSON loaded per invocation" pattern.
- **Security-requirement numbered annotations in hook source**: Every security-critical hook (`enforce-scope.mjs`, `enforce-commands.mjs`) has a top-of-file `SECURITY notes (inline refs)` block listing `REQ-01` through `REQ-08`, and every relevant function cites the REQ number inline (`// SECURITY-REQ-03: resolve symlinks …`). Traceability from a security pre-review document into code. This is a pattern-level discipline — "security requirements traceable from spec to line of code" — notable for agent-written code.
- **Consolidated Stop + SubagentStop hook via event discrimination**: `on-stop.mjs` handles both Stop and SubagentStop by discriminating via `hook_event_name` → `agent_name` fallback. Single file for both hook events, exploiting the common payload shape.
- **zx as a plugin runtime dependency**: Hooks import zx (via `scripts/lib/worktree.mjs`). Adds an npm runtime dep to hook execution. The `npm install` requirement is documented as Troubleshooting Item #1 — a foreseeable friction the authors chose to accept for zx's shell-ergonomics inside Node.
- **Events subsystem with optional remote POST**: `events.mjs` writes JSONL to `.orchestrator/metrics/events.jsonl` AND optionally POSTs to a webhook when `CLANK_EVENT_SECRET` is set. Native `fetch` + `AbortSignal.timeout(3000)`, errors swallowed. A "graceful optional remote telemetry" pattern.
- **Cross-platform tmpdir discipline in CHANGELOG**: `[3.0.0]` CHANGELOG entry explicitly lists each cross-platform concern: `os.tmpdir()` replaces `${TMPDIR:-/tmp}`, `path.parse(dir).root` replaces `/`-terminator for filesystem walks, Windows backslash normalization before glob, CRLF-tolerant config parsing, `.gitattributes` EOL rules. A "windows-native as a documented migration" pattern — most marketplaces implicitly assume POSIX.
- **Pre-release tag diversity**: Uses `-alpha.N`, `-beta.N`, `-rc.N` on the same branch without release branches. Ten releases (all attached to `main`) show a full pre-release ladder. Tag-only, no long-lived release branches.
- **Manual `npm install` post-install with existence-only drift check**: The only "change detection" is user running `ls node_modules/zx`. No diff, no sha, no hook-driven install. A minimalist answer to the dependency-install pattern that deliberately skips the docs-worked-example machinery.
- **Plugin running its own orchestrator against itself**: `CLAUDE.md` at repo root contains a real `## Session Config` block the plugin parses when working on itself — dogfooding at the config layer. Test suite (`tests/integration/parse-config-validator.test.mjs`) exercises this.
- **Output styles as first-class reusable formats**: 3 markdown files under `output-styles/` (`session-report.md`, `finding-report.md`, `wave-summary.md`) define report templates. Agents + skills reference these as the prescribed output shape. A "shared presentation templates" layer not captured in the current components list.

## 18. Gaps

Open bullets — what couldn't be determined within the budget + what source would resolve it.

- **Byte-exact `marketplace.json` schema validation**: did not run `claude plugin validate` or any schema validator; relied on the docs-captured schema. A pre-commit or CI-run validator would confirm compliance; none exists here.
- **Release workflow existence**: no workflow file observed, but `.gitlab-ci.yml` (4.3 KB) was not read in detail — it may contain release automation for the GitLab mirror that does not replicate to GitHub. Reading `.gitlab-ci.yml` would resolve whether releases are fully manual or automated only on GitLab side.
- **`.mcp.json` runtime behavior**: `scripts/mcp-server.sh` (5.3 KB) was not read beyond knowing it exists. Unknown whether it implements an MCP server in bash or delegates to a Node process. Relevant for understanding the MCP surface this plugin exposes.
- **Agent-mapping Session Config semantics**: CLAUDE.md mentions "Agent-mapping Session Config for explicit role-to-agent binding" but the binding schema was not captured. Would need to read `skills/session-start/SKILL.md` or similar to verify how role→agent names bind.
- **Pre-commit hooks**: no `.pre-commit-config.yaml` observed, but not confirmed absent. Would resolve the "no pre-commit version bump" assertion definitively.
- **Codex and Cursor plugin structures**: `.codex-plugin/plugin.json` and `.cursor/rules/*.mdc` were listed but not deeply read. Contents may include parallel novel axes (e.g., Codex-specific hooks, Cursor rule trigger syntax) not captured here.
- **Quality-gate schema details**: `.orchestrator/policy/quality-gates.schema.json` (1.4 KB) was listed but not read. Relevant for understanding the "policy JSON loaded per invocation" pattern in §17.
- **Actual installed-plugin cache layout**: did not install the plugin to observe Claude Code's materialization of it. Unknown whether `node_modules/` is preserved across plugin updates or re-materialized each time; this is a practical consumer concern.
- **`scripts/lib/worktree.mjs` invocation paths**: listed + partially referenced in `on-stop.mjs` and CHANGELOG, but the callers of `createWorktree` / `cleanupAllWorktrees` were not traced. Resolving this would sharpen the "parallel agent execution" claim.
- **Testcase count**: CHANGELOG claims "546 pass, 10 skipped" total. Not independently reproduced; vitest wasn't run. Claim is CHANGELOG-sourced, not observation-sourced.
- **`scripts/validate-plugin.sh` contents**: 12.3 KB validator script listed but not read. Could resolve whether homegrown marketplace-manifest validation is present and what it enforces.
