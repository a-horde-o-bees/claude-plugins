# Sample

Pass-1 Phase-1a partial for bin 4. Functional decomposition of Chulf58/FORGE, CodeAlive-AI/codealive-skills, and CronusL-1141/AI-company, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How the marketplace surface is exposed to Claude Code's installer.

### Single root `.claude-plugin/marketplace.json`

Canonical layout — one manifest at repo root owns one or more plugin entries. Source of truth for what Claude Code's installer reads. Keeps marketplace metadata co-located with the plugin payload it references; convention-aligned and creates no ambiguity for the loader.

### Duplicate root + nested manifests

A second `marketplace.json` lives under `plugin/.claude-plugin/` alongside the canonical root manifest. Claude Code consumes only the root one; the nested copy is an iteration leftover that the installer ignores. Invites version and tag drift because the two diverge silently — versions, descriptions, and `tags` arrays end up out of sync, and the discoverability fields written into the nested copy never reach the marketplace UI. Appropriate when split out for local-dev iteration but not yet consolidated; the rejected-state cost is hidden drift.

## Marketplace metadata wrapper

Marketplace-level (not plugin-level) descriptive fields the manifest declares.

### `metadata.{description, version}` block, no `pluginRoot`

Top-level `metadata` object with description and version, plus often `owner.{name, url}`. Marketplace-level `version` is decoupled from any individual plugin's `version` and tracks an independent (often stale) cadence — `1.0.0` left on the marketplace block while the plugin inside ships `2.0.5` or `0.5.1`. Consumers expecting a single authoritative version see drift; the marketplace `version` is rarely surfaced to users so the drift goes unnoticed by maintainers.

## Per-plugin discoverability surface

Fields that drive listing-page filtering, search, and recognition for a single plugin entry.

### `keywords` on plugin.json

Array of free-text keywords on `plugin.json` (e.g. `["pipeline", "agents", "review", "planning"]` or `["code-search", "codebase", "semantic-search"]`). Whether Claude Code's marketplace indexes the field is undocumented in the plugin reference — the convention reads as npm-style holdover. Appropriate as a defensive declaration but uncertain payoff for marketplace discovery specifically.

### `category` on the marketplace plugin entry

Single-string category (commonly `"productivity"`) on the marketplace plugin entry. Coarse classifier intended for marketplace UI grouping. When used alone without `tags`, narrows discoverability to category browsing only.

### `tags` on the marketplace plugin entry

Array of tags (e.g. `["team", "agents", "automation", "project-management"]`). Adds search-indexable terms beyond the category. When declared on a non-authoritative nested manifest, never reaches the marketplace UI — the discoverability surface is wasted.

### Repo-level GitHub topics

GitHub repository topics (`agent-skills`, `ai-coding`, `semantic-search`) declared on the GitHub repo itself, not in any manifest. Drives GitHub search but not Claude Code's marketplace UI. Useful complement to manifest discoverability when the project also wants discoverability through GitHub's surface.

## Plugin source binding

How the marketplace entry locates the plugin payload on install.

### `relative` source pointing to subdirectory

`"source": "./plugin"` (or similar relative path) when the plugin payload lives in a subdirectory of the marketplace repo. Keeps marketplace and plugin colocated in one repo, with the manifest pointing at a child folder. Necessary when the repo carries non-plugin content (docs, dashboard source, dev scripts) outside the plugin tree.

### `relative` source pointing to repo root

`"source": "./"` when the plugin payload is the repo. Simplest single-plugin layout — manifest and `plugin.json` siblings at root with all components under conventional directories. Leaves no ambiguity about boundaries; appropriate when the repo is dedicated to one plugin and ships nothing the plugin doesn't include.

### `url` self-referencing source

`{"source": "url", "url": "https://github.com/<owner>/<repo>.git"}` where the marketplace manifest points back at the same repo it lives in. The marketplace and plugin payload ship together but the marketplace install treats the repo as a remote source. A locally-cloned-but-uninstalled checkout isn't usable as a marketplace source without `url` rewriting or switching to `relative`. Appropriate when the project plans to publish to a wider marketplace but isn't yet there.

## `strict` field handling on marketplace entries

Whether the marketplace entry sets `strict` and what carve-outs accompany it.

### Default (implicit true)

`strict` field omitted entirely — Claude Code applies its default discovery rules. Components are picked up from convention directories (`skills/`, `agents/`, `hooks/`, `commands/`, `.mcp.json`). Appropriate when the plugin uses standard layout and wants no surprises.

### Explicit `strict: false` without override array

`strict: false` set on the plugin entry without a corresponding `skills`/`agents`/etc override array. Semantically unnecessary for normal discovery — `strict` only matters when carving components out of a non-standard layout. Reads as defensive ceremony or copy-paste; a reader cannot tell from the manifest what protection it provides.

## Version authority

Where the source of truth for the plugin's version lives, and how copies stay in sync.

### `plugin.json` only

Version declared only on `plugin.json`; marketplace entry has no `version` field. Git tags match `plugin.json` one-to-one as a release-discipline convention rather than a structural enforcement. Single-source clarity; risk lives only in tag-vs-manifest drift, not in cross-file drift.

### Synchronized `plugin.json` + marketplace.json via custom bump script

Both `plugin.json` and `marketplace.json` carry a `version` field, kept in sync by a project-local script (`scripts/bump-version.mjs`) that rewrites both in one pass. The script is the enforcement mechanism — manual edits to either file alone create drift. Appropriate when the marketplace entry must carry a version for consumer pinning, but only as long as the script is used.

### Multiple declaration sites with manual sync

Version duplicated across four or more files (`plugin.json`, `pyproject.toml`, root `marketplace.json`, nested `marketplace.json`) without an automated bump. Drift is observed in practice — three sites at `1.3.4`, one stale at `0.6.0`. Marketplace listing displays the stale version while the plugin internals run a newer one. Tag-sanity gates would catch this; their absence correlates with this pattern.

## Channel distribution model

How users select between stable and pre-release versions.

### Tag-on-main with no channel split

Single long-lived branch (`main` or `master`) with semver tags (`v0.5.1`, `v2.0.5`, `v1.3.4`); users pin via `@<tag>` or take `@main`. No `stable-tools`/`latest-tools` marketplace duality, no dev-counter scheme, no release branch family. Internally consistent and minimal — appropriate when the project doesn't need to expose pre-release vs stable as distinct user-facing surfaces. The cost shows up as tag-vs-release drift when the project leans on GitHub Releases for changelog UX (10 tags published, only 7 GitHub Releases).

### Cross-host secondary channel via `npx skills`

Plugin doubles as a universal skill installable via `npx skills add <owner>/<repo>@<skill-name>` (skills.sh) in addition to the Claude Code marketplace. Two distribution channels for the same artifact, each with its own consumer base. Forces the SKILL.md description to work simultaneously for Claude Code and other agent hosts. Appropriate when the skill is intentionally multi-host and the maintainer accepts the cross-host description-tuning constraint.

## Tag and release coordination

How git tags relate to GitHub Releases and changelog publication.

### Tag-on-main, manual GitHub Releases, partial coverage

All tags on the default branch; GitHub Releases authored by hand via web UI for some-but-not-all tags. Drift accumulates — most recent tags missing Releases, occasional skipped tag numbers. Release notes are hand-written per release without `generate_release_notes`. Tolerable when changelog UX isn't load-bearing; problematic when downstream consumers rely on Release pages for "what changed".

### Tag-on-main with mixed annotated and lightweight tags

Some tags are annotated (carry tagger info, message), others are lightweight (direct commit refs). Surfaces in GitHub API responses with different object types. Inconsistency suggests releases were cut by different mechanisms over time — `git tag -a` for some, web-UI lightweight for others. Appropriate as long as consumers don't filter on tag type.

## Plugin-component registration style

How `plugin.json` references the plugin's components (skills, agents, hooks, MCP servers).

### Default discovery, minimal `plugin.json`

`plugin.json` carries only metadata (name, version, description, author, repository, license, keywords). No `mcpServers`, no component path arrays. Claude Code picks up components from convention directories (`skills/`, `agents/`, `hooks/hooks.json`, `commands/`, root `.mcp.json`). Lowest-ceremony layout; communicates "follow conventions" to readers and keeps the manifest stable across component additions. Appropriate when the project is willing to commit to convention paths.

### External `mcpServers` file reference

`plugin.json` declares `"mcpServers": "./.mcp.json"` — the indirection points at the conventional `.mcp.json` file. When the file is also at the conventional location, the indirection is functionally redundant with default discovery; the explicit reference documents intent. Common in plugins with non-trivial MCP server setup.

### Slash-command surface via skills frontmatter, not `commands/`

Slash commands are exposed through `skills/<name>/SKILL.md` files with frontmatter `name: <plugin>:<verb>`, while `commands/` holds only diagnostic stubs (`doctor.md`, `hello.md`). The skill-namespacing prefix in frontmatter is doing the work a `commands/` directory usually would. A reader expecting "commands go in `commands/`" misses most of the surface. Appropriate when the project uses skills as the primary user-facing verb but pays a discoverability cost.

## Agent frontmatter shape

Fields used in agent `.md` frontmatter to describe the agent to Claude Code.

### Plain tool-name list

`tools:` field as a YAML list of bare tool names (`Read`, `Write`, `Glob`, `Grep`, `Edit`, `Bash`). No permission-rule syntax. Minimal capability declaration that lets the agent invoke the named tools.

### `model` + `effort` + `maxTurns` for cost control

Frontmatter declares `model` (e.g. `claude-sonnet-4-6`, `haiku`, `opus`), `effort` (`high`, `medium`), and `maxTurns` for explicit cost-and-budget control per agent. Pattern surfaces in pipeline-style plugins where different waves of agents have different cost profiles. Cheaper-model selection (`haiku` for exploration agents) is an explicit token-cost optimization — offload iterative searches to a cheaper model so the caller's expensive-model conversation stays short.

### `skills:` array delegating to skill packages

Agent frontmatter lists `skills: [<skill-name>, ...]` to grant the subagent access to specific skills the parent has loaded. Composes subagent + skill into a token-cost-aware unit (cheap-model agent invokes the skill's full context). Pattern requires the named skill to exist in the agent's discovery scope.

### `name` + `description` + `model` + `color` only

Minimal frontmatter — no `tools` field; agent uses default tool access. `color` (e.g. `violet`, `green`) is purely UI cue. Native-language descriptions (Chinese in one observed case) flow through `description` directly without an i18n layer, so the template picker shows the source language to all users.

## Dependency installation mechanism

How third-party runtime dependencies become available to plugin code.

### SessionStart Node hook with mtime-driven `npm install`

Hook (`hooks/mcp-deps-install.js` or similar) registered on SessionStart iterates install targets (`mcp/`, `packages/<lib>/`) and reinstalls when `node_modules/` is absent, `package-lock.json` is absent, or `package.json` is newer than `node_modules/.package-lock.json`. Calls `execFileSync(process.execPath, [npmCli, ...args])` resolving `npmCli` from Node's bundled npm rather than bare `npm` on PATH. Prefers `npm ci` when a lockfile exists, falls back to `npm install`. On failure, removes `node_modules` so next session retries. Diff-based change detection means repeated runs converge without redoing work. Appropriate when Node is the runtime and `${CLAUDE_PLUGIN_ROOT}` is the install scope.

### SessionStart Python hook calling `pip install` against `sys.executable`

Hook (`auto_install.py`) tries `import <package>`; on `ImportError`, runs `pip install git+https://<repo>.git` against whatever `sys.executable` resolves to (typically user-global or active interpreter). No venv isolation — mutates user's Python environment silently. Restart of Claude Code is required after first install for the MCP server to pick up the new `sys.path`; this is signaled back to the user via `hookSpecificOutput.additionalContext` declaring "Please restart Claude Code to activate MCP tools." Appropriate as a low-ceremony bootstrap; risky on system-Python with restricted site-packages.

### Plugin-data venv with `diff -q` change detection

Bootstrap script (`bootstrap.py` or `install-deps.sh`) creates `${CLAUDE_PLUGIN_DATA}/venv`, pip-installs requirements plus the plugin package, then injects `site-packages` onto `sys.path` and rewrites `sys.executable`. Change detection via byte-comparison (`diff -q`) against a copy of `requirements.txt` saved into `${CLAUDE_PLUGIN_DATA}` as a marker. Strong invariant when paired with `set -e`; weaker when subprocess return codes aren't checked before stamping the marker. Isolates plugin deps from the user's Python environment at the cost of needing the venv to survive Python upgrades.

### One-time interactive setup script storing creds in OS credential store

User runs `python setup.py` once; the script stores secrets (API keys) in macOS Keychain / Linux Secret Service / Windows Credential Manager. No package install — runtime scripts use stdlib only. Distinct posture: "no deps to install" is the alternative. Cross-agent credential sharing is the explicit motivation — the credential lives in OS-wide storage, not per-plugin or per-session. Pairs with a SessionStart hook that probes for credential presence and nudges the user to run setup if absent.

### Coexisting redundant install paths

Multiple install scripts in tree (SessionStart hook + bootstrap.py + install-deps.sh) where only one is wired to lifecycle events; the rest are dormant rejected-state alternatives kept for reference. A reader has to trace `hooks.json` and `.mcp.json` to know which is live. Drift-prone — the dormant scripts can fall behind the live one without anyone noticing.

## Bin-wrapped CLI distribution

How the plugin exposes a user-facing or internally-spawned executable.

### Node CLI launcher with `env node` shebang

`bin/<verb>.js` opens with `#!/usr/bin/env node`, resolves a wrapper path script-relative (`path.resolve(__dirname, '..', 'scripts', 'forge-wrapper-proto.mjs')`), and `spawn`s `process.execPath` with the wrapper as argv. Inherits stdio, propagates child exit code/signal. Declared as the `bin` entry in root `package.json`. Cross-platform via shebang on POSIX; on Windows requires either `node bin/<verb>.js` or a sibling `.cmd` launcher. Secondary env-var overrides (`FORGE_CLAUDE_CMD`, `FORGE_WRAP_SPAWN`) provide runtime escape hatches.

### Auto-generated Windows `.cmd` launchers with absolute paths baked in

A SessionStart hook discovers `process.execPath` and the `claude` binary location, then writes `bin/*.cmd` Windows launchers with those absolute paths embedded, plus optional `set <ENV>=<path>` lines. Solves "node not on PATH" on Windows without requiring user editing. Files are committed with the author's machine's paths frozen — a reader inspecting the committed file sees one specific machine's layout. Header banners declare "auto-generated ... edits will be overwritten next session" so user customization is impossible. POSIX users rely on the `bin` field in `package.json` instead. Appropriate when the project must work on Windows shells without PATH discipline.

### No `bin/` — Python scripts invoked directly

No `bin/` directory at all. Plugin ships Python scripts the agent invokes via `python scripts/<verb>.py`. Plugin-root resolution in companion shell scripts uses defensive two-way fallback (`${CLAUDE_PLUGIN_ROOT:-$(dirname ...)}`) so scripts work whether Claude Code sets the env var or not. Appropriate when the plugin's surface is just stdlib-Python scripts and no shebang-wrapped entry points are needed.

## User configuration surface

How user-tunable settings are declared and consumed.

### No `userConfig`, OS-level secret storage

`plugin.json` declares no `userConfig`. Secrets live in OS credential store (Keychain / Secret Service / Credential Manager), accessed by Python at runtime. Justification: cross-agent sharing — the key is stored once and shared across all agents on the machine. A `userConfig` field with `sensitive: true` would fragment storage per-agent. Trade-off: users don't get install-time config-prompt UX; configuration happens via a one-time interactive wizard.

### No `userConfig`, layered file-based config

Three-tier file system replaces `userConfig`. Plugin-side defaults (`forge-config.default.json`) → user-side migrated copy at `${CLAUDE_PLUGIN_DATA}/<file>.json` → project-side state (`.pipeline/project.json`). SessionStart hook performs schema-versioned in-place migration on the user-side copy: field-level diff-merge that preserves user-owned fields (`enabled`, `envVar`) across schema bumps, writes a timestamped `.bak-<ISO>.json` backup before overwriting. More sophisticated than the typical "copy default if missing" bootstrap. Appropriate when configuration shape evolves frequently and config richness exceeds what `userConfig` ergonomics support.

### No `userConfig`, `.env` files in cloned repo

User edits a `.env` file (or `.env.example` template) in the cloned repo. Secrets (`ANTHROPIC_API_KEY`, DB creds, `REDIS_URL`) live outside Claude Code's plugin config surface entirely. Appropriate when the plugin backs a long-running server that needs config to persist outside any single Claude Code session. Cost: users don't benefit from Claude Code's secret-handling affordances.

## Schema-versioned config migration

In-place evolution of user-side config files when the plugin's schema changes.

### Field-level diff-merge with timestamped backup

Plugin-side default JSON carries a `schemaVersion` integer. SessionStart hook compares it against the live user-side copy at `${CLAUDE_PLUGIN_DATA}/<file>.json`; on mismatch performs field-level diff-merge that adds/updates plugin-owned fields (providers, models, agentMap entries) while preserving user-owned fields (`enabled`, `envVar`, user-added entries). Writes a timestamped `.bak-<ISO>.json` backup before overwriting and logs a one-line summary. Robust when config-schema evolution is a regular need; the backup preserves the pre-migration state for rollback. The migration logic ends up nearly as expressive as a `userConfig` schema would be — purpose-built for the project's specific shape.

## Tool-use enforcement

PreToolUse / PostToolUse / PermissionDenied hooks that gate or react to tool calls.

### PreToolUse `Bash` deny with belt-and-suspenders output

Hook matches `Bash` and emits both a `hookSpecificOutput.permissionDecision: "deny"` JSON envelope on stdout AND a human message on stderr, then `process.exit(2)`. Documented rationale: "exit 2 alone is silently discarded by the current runtime." Both forms are required to reliably deny a tool call. A consumer who picks just one form will have hooks that appear to work in tests but silently pass in production. Appropriate for security-sensitive matchers where deny must succeed.

### PreToolUse `Write|Edit` workflow gate

Hook matches `Write` and `Edit` and gates them against pipeline state — denies edits when the plugin's state machine is in a phase where edits aren't allowed (e.g., before a planning gate is approved). Same belt-and-suspenders output as Bash deny. Models workflow state via hooks rather than relying on skill prose to guide the agent; structural enforcement of pipeline transitions.

### PreToolUse `Agent` routing/gate enforcement

Hook matches `Agent` (subagent dispatch) and constrains which subagents can run based on pending gates. Stops dispatch of agents that shouldn't run yet (e.g. implementer before plan is approved). Pipeline-state-as-policy pattern; hook-as-policy-engine.

### PostToolUse `*` context tracking

Hook matches `*` and records every tool call to the plugin's context store; always-on observability. Distinct fail-open posture — context tracking that fails should never block the user.

### PostToolUse `Write|Edit` doc-size guard + state sync

Hook matches `Write|Edit` and enforces a doc-size cap plus syncs the plugin's gate state to reflect the just-completed write. Two responsibilities chained on the same matcher.

### PreToolUse + PostToolUse event forwarding

Hook matches `Agent|Bash|Edit|Write` and forwards the event payload to a plugin-owned HTTP server (`POST /api/hooks/<event>`). Pure observer — no policy decisions in-hook; the sidecar dashboard consumes the events. Pays a per-tool-call subprocess spawn cost (paired with a sibling reminder hook on the same matcher means two spawns per pre and post phase).

### PostToolUse local workflow reminders

Hook matches the same broad event set and emits stdout reminders based on a local rules engine (delegation-threshold counters, sequence triggers). Self-described <100ms target with local-only file I/O. Large hook script (~54KB) representing a non-trivial rules engine in the hook layer — "thick local hook, thin sidecar server" division of labor.

### PermissionDenied classification with retry-state TTL

Hook reads denial JSON, calls a sidecar API to classify into one of four buckets (`recoverable_with_retry`, `recoverable_with_workaround`, `needs_user_approval`, `permanent_denial`), then emits retry hints, workaround guidance, or logs silently per classification. Falls back to local keyword matching when API is unreachable. Retry state persisted in a JSON file with 1-hour TTL to prevent retry loops. Hook-as-classifier — offloads policy decisions to a sidecar so policy updates don't require redistributing the plugin.

### TaskCompleted hard-block on missing memo/result

Hook matches `TaskCompleted`, reads task ID from the payload, calls the sidecar API to verify the task has a memo and result recorded; on failure writes `[OS BLOCK] <reason>` to stderr and exits code 2 (the hard-block convention). Connects the hook's deny convention to external business state (sidecar API), not just local rules — a hook that enforces "you can't mark this done until you've logged progress."

### Top-level try/catch wrapping per hook

Every `main()` wraps stdin parsing and primary logic in try/except (or try/catch in JS) with explicit "silent" comments. The discipline is uniform across the hook set even when not factored into a shared helper. "Never throw from a hook function" is the underlying invariant — uncaught exceptions break the user's session.

## Hook failure posture

How hooks behave when their primary work fails.

### Fail-closed for security matchers, fail-open for context

Per-hook decision documented in code comments. Security-sensitive matchers (`bash-guard`, `workflow-guard`, `task_completed_gate`) emit deny + exit 2 on policy violation. Observability hooks (context trackers, banner printers, dep installers) swallow errors and exit 0. Mixed posture is intentional and documented per-hook.

### Universal fail-open with stderr log

All hooks `try/except` and exit 0 regardless of internal failure; stderr carries the diagnostic. Appropriate when the plugin treats hooks as best-effort augmentation rather than enforcement — a failing hook never blocks the user.

## Session context loading

SessionStart and UserPromptSubmit hooks that inject content into the model's context.

### SessionStart banner + `additionalContext`

Hook prints a banner to stderr (visual cue for the operator) and emits the same content via `hookSpecificOutput.additionalContext` (model-visible context injection). Documented evolution path through three generations of output mechanism ending at "stderr direct print + additionalContext for model awareness." Both surfaces because each serves a distinct audience.

### SessionStart conditional `additionalContext` for setup nudge

SessionStart hook (`check_auth.sh`) emits `additionalContext` only when the API key is missing; when present, no context is injected. Matcher restricted to `startup` (not `startup|clear|compact`) so the nudge is one-shot per fresh session. Appropriate as a guidance injection, not a status line. The `startup`-only matcher means user adding a credential mid-session won't see updated state until next fresh session.

### SessionStart full-briefing context

Hook (`session_bootstrap.py`) hits a local API server for team status and task data, then writes a multi-page briefing (behavior rules, available agent templates enumerated from `~/.claude/agents/*.md`, available skills) to stdout for context injection. Rich runtime-driven context — contrast with static banners. Pays a startup-time cost for the API call plus optional opportunistic git-fetch update check. SessionStart matcher absent so all sub-events (`startup`, `clear`, `compact`) trigger the full chain unconditionally.

### UserPromptSubmit anti-speculation rule injection

Hook (`anti-speculation-inject.js`) injects an epistemic-discipline rule on every user prompt — "cite a file:line from a Read/Grep done THIS turn, or say 'I don't know, checking'." Hook-based mechanism for enforcing agent epistemic discipline across a whole plugin surface, codified in `CLAUDE.md` and hooked in at runtime.

### UserPromptSubmit context-window warning

Hook (`context_tracker.py`) reads the transcript JSONL referenced by the hook payload, sums `usage.input_tokens + cache_read + cache_creation`, emits `[CONTEXT WARNING]` at ≥80% or `[CONTEXT CRITICAL]` at ≥90%. Auto-detects 1M context window via model-name match plus by-value fallback. Pure observability injected into the user-prompt path.

## Live monitoring and observability

How runtime telemetry, dashboards, or alerts are surfaced to the user.

### Plugin-owned HTTP server + React dashboard

Plugin runs its own FastAPI process on a fixed port (e.g. 8000) and ships a React dashboard built into `plugin/dashboard-dist/`. Hooks forward events over HTTP to the FastAPI app; the dashboard consumes them. Sidesteps Claude Code's `monitors.json` mechanism entirely because the UI is served by the plugin's own HTTP server. Trades the tidy single-process model for a persistent-daemon architecture.

### Sidecar terminal observer with auto-split

Plugin invokes `scripts/forge-observer.mjs` from a SessionStart hook to launch a local auto-split terminal observer alongside the Claude session. Plugin-native concept named "observer" or "dashboard" — distinct vocabulary from Claude Code's `monitors.json` mechanism. Different surface area; same intent (visibility into long-running plugin state) achieved without Claude Code's monitor primitives.

### No live monitoring

Plugin ships no `monitors.json`, no sidecar dashboard, no event forwarding. Appropriate for skill-style plugins where session-bounded interaction is the entire surface.

## IPC and inter-process coordination

How plugin processes (server, hooks, MCP) discover each other and exchange state.

### Sidecar file as port-discovery contract

Plugin's API server writes its actually-bound port into `~/.claude/data/<plugin>/api_port.txt` at startup; hooks read the file before each call to resolve the URL. An env var (e.g. `AITEAM_API_URL`) overrides. Lightweight IPC contract — handy when port 8000 is taken; risky when two projects run concurrently because only one wins the file. Concrete bug reported in changelog where a hardcoded `.mcp.json` env var defeated the fallback.

### `${CLAUDE_PLUGIN_DATA}` for migrated user state

Plugin reads/writes user-tunable state in `${CLAUDE_PLUGIN_DATA}/` (config file, retry-state JSON, permission-denial TTL state). Persists across sessions; survives plugin upgrades. Distinct from `${CLAUDE_PLUGIN_ROOT}` which holds plugin-distributed assets. Appropriate when state is per-user and must be writable.

## Plugin-to-plugin dependencies

How a plugin declares dependence on other marketplace plugins.

### No declared dependencies

`plugin.json` carries no `dependencies` field. Single-plugin marketplace, self-contained payload. Appropriate when the plugin doesn't compose with sibling marketplace plugins. Cross-plugin coordination doesn't arise.

## Test framework selection

Test runner, harness, and discovery convention used to verify plugin code.

### pytest with optional inline cov

Tests in `tests/` at repo root using pytest with `pytest-cov` and optionally `pytest-asyncio`. Pytest config either in `pyproject.toml` `[tool.pytest.ini_options]` (canonical) or absent (CI invokes pytest with inline flags). Tests cross the skill boundary — import skill scripts via `sys.path.insert` + `importlib.util.spec_from_file_location` when the skill code isn't a packaged module. Standard Python test posture.

### Custom Node `node:test`-style runner with suffix discovery

Custom runner at `scripts/run-tests.mjs` discovers tests by directory + suffix convention (`hooks/*-test.js`, `mcp/*-test.mjs`), spawns each via `node <path>` sequentially, inherits stdio, aggregates exit codes. No Jest/Vitest dependency. Tests are plain assertion scripts co-located with the code they test. Tight discovery — a contributor adding `*.test.js` (dot, not hyphen) silently skips. Appropriate when avoiding test-framework dependency is a goal.

## Test placement convention

Where test files live relative to the code under test.

### Co-located with code under test

Tests sit next to source files (`hooks/gate-sync-test.js` next to `hooks/gate-sync.js`, `mcp/router-test.mjs` next to `mcp/router.mjs`). Discovery happens via filename suffix. No central `tests/` directory. Appropriate when tests pair tightly with their immediate source and the project has no need for a global test root.

### Centralized `tests/` at repo root

All tests under a root `tests/` directory, often subdivided into `unit/`, `integration/`, `e2e/`. Plugin/code tree separate. Standard Python posture. Appropriate when tests are organized by category or scope rather than by source-file pairing.

## CI workflow shape

What CI does on push/PR and how strictly it gates merges.

### Test workflow with pinned actions, pytest run, no caching

`.github/workflows/ci.yml` triggered on push and PR to `main`. Single ubuntu-latest job, single Python version. Inline `pip install pytest pytest-cov`. Runs `python -m pytest tests -v --cov=skills --cov-report=term-missing`. Actions SHA-pinned with tag comments. No caching; no lint; no manifest validation. Coverage is `term-missing` only — no codecov upload, no trend tracking. Minimal CI scope reflects "runtime is tested, manifests are trusted" posture.

### Split test + lint workflows with `|| true` permissive runs

Two workflows — `ci.yml` (test + dashboard typecheck) and `lint.yml` (ruff + eslint). Both trigger on push and PR to multiple branches. Test job pip-installs deps with `|| true` and runs pytest with `|| true` — failures don't fail CI. CI tolerates environment-caused pip failures without distinguishing them from genuine regressions; effectively a smoke check. Action pinning by tag (not SHA). Built-in `setup-node` cache for npm; no Python cache.

### No CI

Repo has no `.github/workflows/` directory. Regressions are caught only when someone runs the test suite locally. Appropriate when the project is single-author and pre-1.0; risk grows as contributors and release cadence grow.

## Release automation

Whether tags trigger automated release-creation workflows.

### Manual GitHub UI release creation, no automation

Releases cut by hand: bump `plugin.json` → commit → annotate tag → push main + tag → write release notes in GitHub UI (sometimes). No automation, no tag-sanity gates. Drift symptoms: tags without published Releases, missing tag numbers, mismatched `plugin.json.version` and tag name. The release-notes UX is a manual step that has fallen behind the tag cadence in practice.

### Tag-driven version-bump script with no GitHub Actions

A project-local script (`scripts/bump-version.mjs`) bumps versions across `plugin.json` and `marketplace.json` in one operation, but tag creation and release publishing remain manual. The script enforces version-file sync but not tag-vs-manifest alignment. Failure mode: contributor commits feature work after a tag without bumping, leaving `plugin.json` temporarily behind reality.

## Marketplace validation

Whether manifest correctness is enforced automatically.

### No validation

No CI workflow validates `plugin.json` or `marketplace.json`. Validation relies on Claude Code's load-time checks plus manual testing. The version-drift pattern observed elsewhere is a correlate — automated validators would catch cross-file mismatches. Diagnostic skills (`/forge:doctor`, etc.) serve as installation diagnostics, not manifest validators.

## Documentation surface

What docs the repo ships and where they live.

### Root `README.md` + root `CLAUDE.md`, no per-plugin docs

Substantial root README (8KB - 36KB observed) covers install, usage, features. Root `CLAUDE.md` carries operator-facing runtime instructions (anti-speculation rules, workflow philosophy, change discipline). LICENSE present in some repos and absent in others (MIT declared in JSON manifests but no `LICENSE` file). Community health files (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`) generally absent.

### Multi-language READMEs and CHANGELOGs

Paired English and Chinese versions (`README.md` + `README.zh-CN.md`, `CHANGELOG.md` + `CHANGELOG.zh-CN.md`) with no sync-enforcement. Drift possible. Appropriate when the project is intentionally multi-lingual; cost is content-drift between locales.

### Keep-a-Changelog format with root-cause prose

`CHANGELOG.md` declares Keep-a-Changelog format at top; every release block has Added/Changed/Fixed sections with prose explaining root causes (e.g. why a hook was rewritten, what bug a new fallback addresses). Unusually detailed for a plugin repo. Appropriate when the project has substantial cross-release behavior changes that demand explanation.

### README references to docs that don't exist on disk

README links to `docs/ARCHITECTURE.md`, `docs/FORGE-OVERVIEW.md`, etc. that aren't present in the repo's `docs/` listing. Either aspirational ("we plan to write these"), removed without README update, or in a nested location not surfaced by listing. Reader clicking links 404s. Drift symptom — README and disk state diverged.

### SKILL.md as primary doc for the skill component

`skills/<name>/SKILL.md` (10KB+ in observed cases) is the deep operational doc; root README is install-focused. Appropriate when the plugin is essentially a skill — most of the substantive content describes what the skill does and how to invoke it. Description field has a hard 1024-char limit and is read by many agent hosts simultaneously when the skill is multi-host.

### Plugin-bridge cross-agent symlinker

`tools/plugin-bridge/` ships an auxiliary bash toolkit (install + launchd plist + update + uninstall + README) that maintains a symlink from another agent's skills directory (e.g. `~/.codex/skills/<name>`) to `~/.claude/plugins/cache/<marketplace>/<plugin>/<latest-version>/skills/<name>`. Auto-relinks on `claude plugin update` via launchd `WatchPaths`. Linux equivalent uses `systemd --user` path units. Converts Claude Code's versioned plugin cache into a live source for non-Claude agents. Appropriate when the skill targets multiple agent hosts and the maintainer wants a single source of truth for the skill's content.

## Cross-agent skill distribution

Mechanisms for shipping the same skill to multiple agent hosts.

### Multi-host SKILL.md with description tuning for cross-agent matching

`SKILL.md` description is authored to match trigger verbs/nouns users actually say, with a hard 1024-char limit and a 300-500-char target. Explicitly written to work simultaneously for Claude Code, Cursor, GitHub Copilot, Windsurf, Gemini CLI, Codex, Goose, Amp, Roo Code, OpenCode, OpenClaw — each with its own project-scope and user-scope skills directory conventions. Description-writing rules codified in `CLAUDE.md` ("don't bake in anti-patterns against failure modes of one session — read by many agents in many contexts"). Pattern requires the maintainer to keep the description host-neutral.

### `npx skills` distribution channel

Plugin installable via `npx skills add <owner>/<repo>@<skill-name>` (skills.sh) in addition to the Claude Code marketplace. Two distribution channels for the same artifact. The skills.sh channel resolves into the agent's skills directory directly, whichever host the user is running.

## Sidecar daemon architecture

Whether the plugin runs a long-running process beyond the Claude Code session.

### Persistent FastAPI server with dashboard UI

Plugin expects a FastAPI process to be running on localhost; hooks forward events over HTTP and a SessionStart hook queries the server for state. Dashboard (React) served from the same server on a separate port. Hooks become event producers for a daemon dashboard rather than in-process policy layers. Trades Claude Code's tidy single-process model for a persistent-daemon architecture. Appropriate when long-running coordination state must survive across sessions and user-facing observability requires more than terminal output.

### No daemon — session-bounded only

Plugin process state lives entirely within the Claude Code session. No background server, no sidecar dashboard. Appropriate for skill-shaped plugins.

## Plugin diagnostics surface

How users verify the plugin installed correctly and is working.

### `/<plugin>:doctor` slash-command diagnostic

A `commands/<plugin>/doctor.md` slash command (or skill of the same name) walks installation diagnostics: node-on-PATH, plugin root resolved, MCP launcher generation, dependencies installed, server connectivity, project init state. Designed for the user to run after install to surface configuration problems. Appropriate when the plugin has multi-step bootstrap that can fail at any of several points.

### No diagnostic surface

Plugin ships no diagnostic command. Users debug install failures by reading hook stderr or running scripts manually. Appropriate when the plugin's surface is small enough that failure modes are obvious.

## Pipeline state machine

Whether the plugin models user-facing workflow as enforced state transitions.

### Gate-enforced multi-stage pipeline

Plugin is structured as a state machine with explicit user-approval gates between agent waves (Gate #1 = plan approval, Gate #2 = implementation approval). Hooks (`gate-enforcement.js`, `gate-sync.js`) hard-enforce gate transitions on Agent/Write/Edit tool calls. Skills represent transitions between states (`/forge:plan`, `/forge:implement`, `/forge:review`); the hooks ensure illegal transitions can't happen by tool-level enforcement. Models workflow state via hooks rather than relying on skill prose to guide the agent. Appropriate when the workflow has clearly-defined approval points that must be respected.

### Risk-surface policy in operational docs

`CLAUDE.md` defines a "risk surface" (shell, child_process, fs writes outside specific dirs, auth, network, new MCP tools, schema changes, merge boundaries) that deterministically mandates specific reviewer agents regardless of pipeline mode. User-facing policy language for dispatching security reviewers; complements the hook-enforced gates with declarative policy.

## Agent-template language posture

What language agent template prompts and frontmatter are written in.

### Native-language-first templates

All agent templates written in the project's primary spoken language (Chinese observed); descriptions and full template body are not translated from English. English-only Claude Code users see the agent `description` in the source language in the template picker. Genuinely native-first design rather than translated; no i18n layer.

### English-default templates

Agent templates in English; frontmatter and prompts assume English-speaking users. Default for the corpus.

## Settings.json env-field workaround

How plugins inject environment variables Claude Code's plugin `settings.json` won't propagate.

### Direct write to user `~/.claude/settings.json` from SessionStart hook

In-code comment: "Plugin settings.json env field is NOT supported by CC (only 'agent' key works)." A SessionStart hook writes the required env var (e.g. `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) directly into `~/.claude/settings.json` as a workaround. Concrete data point on a documented-but-actually-broken plugin capability. Fragile because it modifies user-scope settings the user may have customized; appropriate only when the env var is plugin-essential and has no other delivery channel.
