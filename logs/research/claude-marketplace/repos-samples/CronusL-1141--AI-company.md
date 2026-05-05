# Sample

Mirrors of `https://github.com/CronusL-1141/AI-company`. AI Team OS — Multi-Agent Team Operating System for Claude Code with persistent FastAPI server, React dashboard, MCP tools, agent templates, task wall, and meeting system. MIT-licensed; 160 stars at sample time; current tip is `v1.3.4` (pushed 2026-04-14) on the legacy default branch `master` (no `main`; CI triggers and code accommodate both names).

## Marketplace manifest layout

### Duplicated marketplace manifest at root and nested

Two `marketplace.json` copies coexist — canonical at `.claude-plugin/marketplace.json` (repo root) and a duplicate at `plugin/.claude-plugin/marketplace.json`. Per Claude Code conventions, the root one is what the marketplace installer consumes; the nested manifest appears to be left over from local-dev iteration and is ignored by the marketplace discovery path. Drift: root entry version is `0.6.0`, nested entry version is `1.3.4`. The nested one matches `plugin/.claude-plugin/plugin.json` and the published `pyproject.toml` `version`; the root manifest's `0.6.0` is stale. Marketplace users see `0.6.0` in the listing even when the plugin itself is at `1.3.4`. Redundant nested marketplace.json invites future drift.

### Top-level `metadata` wrapper variants

`metadata.{version, description}` wrapper present in root manifest (`metadata.version: "1.0.0"`, `metadata.description: "Self-driving AI company OS — turn Claude Code into a persistent, self-managing dev team"`). Root manifest also has top-level `owner.{name, url}`. `metadata.pluginRoot` absent.

## Plugin source binding

### Relative source pointing to subdirectory

Root `marketplace.json` uses `"source": "./plugin"` pointing at the subdirectory holding the actual plugin. Nested `plugin/.claude-plugin/marketplace.json` uses `"source": "./"` relative to itself.

### `strict` field default

Neither manifest sets `strict` — implicit-true default. No `skills` override on the marketplace entry.

## Per-plugin discoverability metadata

### Marketplace-entry facets plus duplicated keywords on plugin.json

Root manifest plugin entry uses `category: "productivity"` only (no `tags`, no `keywords`). The redundant nested `plugin/.claude-plugin/marketplace.json` adds `tags: ["team", "agents", "automation", "project-management"]` to the same plugin entry, but since the nested manifest isn't the one discovered by the marketplace installer, those tags don't reach the marketplace UI. `plugin.json` is not the keywords source either — the discoverability split is between two marketplace manifest copies.

### `$schema` absence on per-plugin manifests

`$schema` absent in both manifests.

## Version coordination

### Triple-file version (build manifest joins)

Four sites declare the version: `plugin/.claude-plugin/plugin.json` → `1.3.4`; `pyproject.toml` (Python build manifest) → `1.3.4`; nested `plugin/.claude-plugin/marketplace.json` → `1.3.4`; root `.claude-plugin/marketplace.json` plugin entry → `0.6.0` (stale). Three agree, one is behind by an entire minor+patch run. No automated sync; manual hand-edit per release. The stale `0.6.0` string is the kind of drift that any cross-manifest version-sync validator would catch — none is wired here. The duplicated marketplace manifest (root + nested) creates a fourth version slot beyond the plugin.json/marketplace.json/pyproject.toml triplet.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split. Six semver tags (`v1.2.0`, `v1.3.0`, `v1.3.1`, `v1.3.2`, `v1.3.3`, `v1.3.4`) on the single `master` branch. Users pin by git ref via Claude Code's marketplace install flow or by cloning and pointing at the `plugin/` directory locally. No `stable-tools`/`latest-tools` pattern, no dev-counter scheme, no release branch.

## Tag and release lifecycle

### Tag-on-main, single branch

Six tags (`v1.2.0` through `v1.3.4`) on tagged commits, all reachable from `master`. Single long-lived `master` branch. Default branch is `master` (legacy git-init default); the author's code acknowledges `main` as an alternative — CI triggers on both (`branches: [master, main]`); `session_bootstrap.py` update-checker tries `origin/main` first, falls back to `origin/master`.

## Plugin-component registration

### Inline `mcpServers` definition in `plugin.json`

`plugin.json` references MCP via external file (`mcpServers: "./.mcp.json"`). The `.mcp.json` at `plugin/.mcp.json` declares one server `ai-team-os` invoked via `python -m aiteam.mcp.server`. No explicit path arrays for skills/commands/agents/hooks — those rely on default discovery under the plugin directory.

### Settings.json env-field workaround

Plugin `settings.json` hard-sets `"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}` — but per an in-code comment in `auto_install.py`, "Plugin settings.json env field is NOT supported by CC (only 'agent' key works)", so the hook writes the env var directly to `~/.claude/settings.json` as a workaround. A documented divergence from the plugin-reference contract for `settings.json`.

## Component composition

### Skills (universal)

Four skills under `plugin/skills/`: `continuous-mode`, `meeting-facilitate`, `meeting-participate`, `os-register`.

### Commands

Eight `os-*.md` files under `plugin/commands/`: `os-doctor`, `os-help`, `os-hooks`, `os-init`, `os-meeting`, `os-status`, `os-task`, `os-up`.

### Agents

24 `.md` files under `plugin/agents/` — templates for tech-lead, backend-architect, frontend-developer, QA, bug-fixer, debate-advocate/critic, meeting-facilitator, etc.

### Hooks

`plugin/hooks/hooks.json` plus 12 Python scripts (`auto_install.py`, `session_bootstrap.py`, `workflow_reminder.py`, `send_event.py`, `task_completed_gate.py`, `permission_denied_recovery.py`, `context_tracker.py`, `pre_compact_save.py`, `cc_task_bridge.py`, `inject_subagent_context.py`, plus more).

### MCP servers

`plugin/.mcp.json` — one server `ai-team-os` invoked via `python -m aiteam.mcp.server`.

## Agent declaration conventions

### Standard fields plus model / color

Agent frontmatter uses `name`, `description`, `model` (uniformly `opus` across sampled templates), `color` (e.g., `violet`, `green`) on engineering templates. No `tools`, `memory`, `background`, `isolation`, or namespaced field usage observed. Agents inherit default tool access; no `tools` field.

### `skills:` array delegating to skill packages

`team-member.md` uses `name`, `description`, `model`, plus `skills` (list of skill names the agent gets access to: `os-register`, `meeting-participate`).

### Native-language-first templates

All 24 agent templates are written in Chinese (`description`, `身份与记忆` sections). Genuinely native-language-first plugin design — the prompts aren't translated from English. An English-only Claude Code user would still see the agent `description` field in Chinese in the template picker.

## Server runtime (MCP)

### Local venv built by SessionStart hook

The plugin needs a heavy Python dep footprint (FastAPI, uvicorn, fastmcp, LangGraph, LangChain-Anthropic, SQLAlchemy, Alembic, Pydantic, aiosqlite, etc.) to run the `ai-team-os` MCP server. The active install path is `plugin/hooks/auto_install.py` (SessionStart hook): `pip install git+https://github.com/CronusL-1141/AI-company.git` against whatever Python `sys.executable` resolves to. The MCP server itself is invoked via `python -m aiteam.mcp.server` from `plugin/.mcp.json`.

## Bin entry mechanism

### No bin entry / direct invocation

No `plugin/bin/` directory; no shebang-wrapped entry points. The plugin's CLI surface is (a) slash commands under `plugin/commands/` and (b) Python console scripts `aiteam` and `ai-team-os-serve` registered in `pyproject.toml` `[project.scripts]` — those are installed into the Python environment's `bin/` by pip when the `ai-team-os` PyPI package is installed, not exposed via the Claude Code `bin/` convention.

## Dependency installation

### `pip install` against `sys.executable` (no venv isolation)

`plugin/hooks/auto_install.py` (SessionStart hook with 30000 ms timeout) tries `import aiteam`; on `ImportError`, runs `pip install git+https://github.com/CronusL-1141/AI-company.git` against whatever Python `sys.executable` resolves to (typically user-global or active interpreter). No venv isolation — mutates user's Python environment silently. If the user runs Claude Code under a system Python with restricted site-packages, install will fail and the hook will swallow the error. Restart of Claude Code is required after first install for the MCP server to pick up the new `sys.path`; signaled back via `hookSpecificOutput.additionalContext` declaring "Please restart Claude Code to activate MCP tools."

### Coexisting redundant install paths

Three install paths coexist in the tree:
1. `plugin/hooks/auto_install.py` — the active SessionStart hook (path 1 above).
2. `plugin/bootstrap.py` — creates `${CLAUDE_PLUGIN_DATA}/venv`, runs pip-install of requirements + the `aiteam` package into the venv, then injects `site-packages` onto `sys.path` and rewrites `sys.executable`. Not actually referenced by the active `.mcp.json`, but kept in tree.
3. `plugin/scripts/install-deps.sh` — same venv-based install as `bootstrap.py` but as a bash script with `set -e`; neither hooks.json nor `.mcp.json` invokes it.

A reader has to trace `hooks.json` and `.mcp.json` to know which is live. Many repos delete unused install scripts — keeping them suggests iteration that didn't consolidate.

### Plugin-data venv with `diff -q` change detection

`bootstrap.py` and `install-deps.sh` use `diff -q`/byte-comparison against a copy of `requirements.txt` saved into `${CLAUDE_PLUGIN_DATA}/requirements.txt` as a marker. This detection mechanism is dormant — wired only on the unused install paths.

## Install change detection

### Existence-only check

`auto_install.py` uses existence-only detection — tries `import aiteam` and only installs if `ImportError`. No marker file, no hash. The active path's only invariant.

## Install trigger and lifecycle

### SessionStart direct invocation

`auto_install.py` registered as the first SessionStart hook with a 30000 ms timeout.

## Install failure posture

### Multi-layer fail-open with stderr advisory

`auto_install.py` prints a user-facing failure line to stderr, also writes a `hookSpecificOutput.additionalContext` JSON blob to stdout on success so CC surfaces "Please restart Claude Code to activate MCP tools." Never `exit(nonzero)` — hook failure is soft-swallowed. Marker file is never written on failure (since there is no marker), so next session retries via the `import aiteam` probe.

## User configuration and authentication

### `.env` files in cloned repo

`plugin.json` declares no `userConfig`. Runtime configuration is done out-of-band — the plugin reads `AITEAM_API_URL` from process env (primarily), from a `~/.claude/data/ai-team-os/api_port.txt` file (for dynamic-port discovery, written by the API server at startup), and from `.env` files the user places in the cloned repo. The `.env.example` template documents `ANTHROPIC_API_KEY`, PostgreSQL creds, `REDIS_URL`, `API_PORT`, etc. Secrets (`ANTHROPIC_API_KEY`) go via user-managed `.env` rather than through `userConfig` with `sensitive: true`. The trade-off is deliberate — the plugin backs a long-running server, not a one-shot invocation, so config persists outside Claude Code session.

### Out-of-band env vars (no `userConfig`)

`AITEAM_API_URL` env var with `api_port.txt` sidecar fallback for dynamic port discovery. `ANTHROPIC_API_KEY`, `REDIS_URL`, `API_PORT` from user-managed `.env`. No `${user_config.KEY}` substitution.

## Tool-use enforcement

### Multi-pattern PreToolUse safety stack

PreToolUse: 1 matcher group, matcher `Agent|Bash|Edit|Write`, 2 command entries — `workflow_reminder.py PreToolUse` (local reminders, target <100 ms, no HTTP) and `send_event.py PreToolUse` (forwards to OS API for the dashboard).

### Event forwarding to sidecar (PreToolUse + PostToolUse)

`send_event.py` is wired on PreToolUse and PostToolUse with matcher `Agent|Bash|Edit|Write`; HTTP-forwards each event to the local OS API (`http://localhost:8000` or dynamic-port-file). Silent except on HTTP error.

### PostToolUse local workflow reminders

`workflow_reminder.py` (54 KB, runs on PostToolUse with matcher `Agent|Bash|Edit|Write`) fires local reminders based on tool sequence (Leader-delegation-threshold counter). Self-described target <100 ms. Local-only file reads/writes, no HTTP.

### `PermissionDenied` classification with retry-state TTL

`permission_denied_recovery.py` reads the denial JSON, calls `POST /api/hooks/diagnose_denial` on the OS API to classify the denial into one of four categories (`recoverable_with_retry`, `recoverable_with_workaround`, `needs_user_approval`, `permanent_denial`), then either emits retry hints, workaround guidance, Leader notifications, or logs silently. Falls back to keyword matching when API is unreachable. Retry state persisted in `~/.claude/data/ai-team-os/permission_denied_retry.json` with 1-hour TTL to prevent retry loops.

### TaskCompleted hard-block on missing memo/result

`task_completed_gate.py` on `TaskCompleted` exits code 2 with stderr message `[OS BLOCK] 任务 ... 未记录进展` if the associated task lacks memo or result in the OS task wall. Uses the documented hard-block convention but connects it to external business state (the sidecar API), not a local rule — "you can't mark this done until you've logged progress." Fail-open on API unreachability (silent exit 0 on malformed payload or missing task_id).

## Hook handler runtime

### Python stdlib runner with external probing

12 Python hook scripts under `plugin/hooks/`. Each `main()` wraps stdin-parsing and main logic in try/except with explicit "silent" comments. The discipline is uniform across scripts but the centralized pattern isn't factored into a helper.

## Hook output contract

### Mixed posture (fail-closed for security, fail-open for context)

`send_event.py` is HTTP-forwarding — silent except on HTTP error. `workflow_reminder.py` writes reminders to stdout (picked up by CC as `additionalContext`). `permission_denied_recovery.py` mixes — structured JSON via stdout for hook responses, text to stderr for operator logs. `task_completed_gate.py` is the strictest — corrective string to stderr and `exit 2`.

## Hook failure posture

### Mixed posture (fail-closed for security, fail-open for context)

Documented in code comments per-hook. `send_event.py`, `context_tracker.py`, `pre_compact_save.py`, `cc_task_bridge.py`, `inject_subagent_context.py` — fail-open (silent try/except swallowing all errors; explicit comments "never block", "silent pass", "don't block CC"). `task_completed_gate.py` — fail-closed on validation failure (exit 2 when memo/result missing) but fail-open on API unreachability. `permission_denied_recovery.py` — fail-open to API failures, fail-closed on classified `permanent_denial`. `auto_install.py` — fail-open (prints manual command to stderr on failure, never exits nonzero).

### Differentiated per-hook timeouts

Per-hook timeouts visible in `hooks.json` — 30 s on `auto_install.py`, 5 s on `session_bootstrap.py`, 2 s on `send_event.py`, 3000 ms (3 s) on PreToolUse/PostToolUse fan-out. The 30 s timeout on `auto_install.py` is long enough to mask a hung pip install visibly; users report typical first-session install as "~2 min" per `bootstrap.py`'s own banner, which exceeds the 30 s budget.

## Session context loading

### Full-briefing context with API call

`session_bootstrap.py` (23378 bytes; SessionStart) hits the local OS API (`http://localhost:8000` or dynamic port from `api_port.txt`) for team status and task-wall top-5, and writes a Chinese-language briefing (Leader behavior rules 1-23, available agent templates enumerated from `~/.claude/agents/*.md`, available skills list) to stdout for injection into the Claude context. When the API is unreachable, it prints a service-start command instead. Also performs an opportunistic 24-hour-cooldown git-fetch update check (5 s timeout). Briefing output is entirely Chinese — no i18n layer.

### Conditional `additionalContext` for setup nudge

`auto_install.py` uses `hookSpecificOutput.additionalContext` with `hookEventName: "SessionStart"` on successful first-install: "Please restart Claude Code to activate MCP tools. This is a one-time setup." One of the cleaner ways to handle the "MCP server needs the package on sys.path before Claude Code starts the server process" bootstrap-ordering problem.

### Per-prompt context-window warning

`context_tracker.py` (UserPromptSubmit) reads the transcript JSONL referenced by the hook payload, sums `usage.input_tokens + cache_read + cache_creation` from the last assistant message, and emits `[CONTEXT WARNING]` at ≥80% or `[CONTEXT CRITICAL]` at ≥90% (with 1M-context-window auto-detection via model-name match or by-value fallback when token count exceeds 200K).

## SessionStart matcher scope

### Empty matcher (all sub-events)

No `matcher` key on the SessionStart entries, so all sub-events (`startup`, `clear`, `compact`) fire the full SessionStart chain. `auto_install.py`, `session_bootstrap.py`, and `send_event.py SessionStart` all run on every resume/clear.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. The plugin provides a React dashboard (`dashboard/` tree, built separately into `plugin/dashboard-dist/`) served from the FastAPI app on port 3000 — rich UI surface that sidesteps the Claude Code `monitors` mechanism entirely because it's served by the plugin's own HTTP server.

## Sidecar daemon and IPC lifecycle

### Persistent FastAPI server with React dashboard UI

The plugin isn't a thin MCP wrapper — it expects a FastAPI server process to be running on localhost (default port 8000, with `api_port.txt` dynamic-discovery fallback). Every hook forwards events to this server over HTTP, and `session_bootstrap.py` queries it for team/task state. Trades Claude Code's tidy single-process model for a persistent-daemon architecture; hooks become event producers for a dashboard rather than in-process policy layers. React dashboard on port 3000 served by FastAPI extends the surface — observability lives outside Claude Code entirely.

## State persistence

### Sidecar port-discovery file

The API server writes the port it actually bound to into `~/.claude/data/ai-team-os/api_port.txt`, and every hook reads that file to resolve the URL before each call (with `AITEAM_API_URL` env var override). Lightweight IPC contract — handy when port 8000 is taken; risky when two projects run concurrently (only one can win the file). CHANGELOG 1.3.2 flagged a related bug where `.mcp.json` hardcoded the env var and defeated this fallback.

### `${CLAUDE_CONFIG_DIR:-${CLAUDE_HOME:-$HOME/.claude}}/<plugin>/` pointer files

Mission state lives under `~/.claude/data/ai-team-os/` (not `${CLAUDE_PLUGIN_DATA}`): `api_port.txt` (dynamic port discovery), `permission_denied_retry.json` (1-hour TTL for retry-state).

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field on `plugin.json`. Single-plugin marketplace; tag format is plain `vX.Y.Z`.

## Testing

### Pytest with asyncio support

pytest with `pytest-asyncio` and `pytest-cov`. `tests/` at repo root has `unit/`, `integration/` subtrees plus top-level `conftest.py`, `e2e_api_coverage.py`, `e2e_dashboard_coverage.py`, `smoke_api_comprehensive.py`, `test_wake_manager.py`, `test_workflow_reminder.py`. `[tool.pytest.ini_options]` in `pyproject.toml`: `testpaths = ["tests"]`, `asyncio_mode = "auto"`. Test deps in `pyproject.toml` `[project.optional-dependencies].dev`.

### Centralized `tests/` placement

Tests at `tests/` repo root. No per-plugin `tests/` nesting.

## CI workflow shape

### Split test + lint workflows with `|| true` permissive runs

Two workflows: `ci.yml` (1220 bytes, two jobs `test` + `dashboard-typecheck`) and `lint.yml` (883 bytes, two jobs `ruff` + `eslint`). Triggers `push` and `pull_request` on `[master, main]`. No tag or schedule triggers. Single Python 3.12, single Node 22, single ubuntu-latest. Action pinning by tag (`actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`) — no SHA pinning. Built-in `setup-node` cache: `npm` with `cache-dependency-path: dashboard/package-lock.json`. No caching on `setup-python` despite repeated raw pip invocations.

`ci.yml.test`: ad-hoc `pip install pytest pytest-asyncio pytest-cov && pip install fastapi uvicorn sqlalchemy aiosqlite pydantic pydantic-settings pyyaml anyio && pip install fastmcp || true && pip install langgraph langchain-anthropic langchain-core || true`, then `python -m pytest tests/unit/ -v --tb=short 2>&1 || true`. The `|| true` on the test run reduces CI to a smoke check — unit-test failures don't fail CI. Combined with `pip install fastmcp || true` etc., CI tolerates environment-caused pip failures without distinguishing them from genuine regressions. CI doesn't install the project itself (`pip install -e .`); tests run against the ad-hoc dep set directly. No Python or OS matrix; Windows installer logic (`auto_install.py`, `bootstrap.py` have explicit `sys.platform == "win32"` branches) is untested in CI.

`lint.yml.ruff`: `ruff check src/ tests/` — omits `plugin/hooks/*.py` from the lint sweep (though `pyproject`'s ruff config does special-case these with `E501` ignore). Hook scripts don't get baseline lint. `lint.yml.eslint`: `npm run lint` in `dashboard/`.

## Marketplace validation

### No validation

No validation workflow, no `bun+zod`, no `claude plugin validate`, no pre-commit hook. The marketplace.json/plugin.json version drift would be caught by any validator that cross-checks the two files; absence of validation correlates.

## Release automation

### No release automation / manual

No `release.yml`, no GitHub Releases automation. Six tags (`v1.2.0` through `v1.3.4`) on `master`, presumably created via `git tag` + `git push --tags`. `plugin.json` version and `pyproject.toml` version must be hand-matched to the tag name; CI does not enforce. CHANGELOG.md is manual, not consumed by a release pipeline.

## Documentation surface

### Substantial root README + CHANGELOG + community files + badges

`README.md` at repo root (36781 bytes, English; substantial). `README.zh-CN.md` (33734 bytes) paired with a top-of-file language switcher link. Rich — problem statement, architecture section, install matrix, MCP tool enumeration, agent template listing, feature table with badges. `plugin/README.md` (3497 bytes) — install-focused, duplicates parts of root README. `plugin/hooks/README.md` (1790 bytes) — hook-specific. `CLAUDE.md` at repo root (514 bytes — terse operator brief: tech stack, core constraints, Leader behavior). Not per-plugin. Doesn't mention the `auto_install.py` restart-loop. `docs/architecture.md` referenced from root `CLAUDE.md` but the path wasn't directly verified.

### Multi-language READMEs

`README.md` (English) + `README.zh-CN.md` (Chinese) with language-switcher link. `CHANGELOG.md` (English) + `CHANGELOG.zh-CN.md` (Chinese). Two CHANGELOGs with no sync-enforcement — drift possible.

### Keep-a-Changelog with root-cause prose

`CHANGELOG.md` at repo root (30090 bytes), Keep a Changelog format explicitly declared at top (`Format: [Keep a Changelog]`). Chronological-descending; every release block has Added/Changed/Fixed sections with prose explaining root causes (unusually detailed for a plugin repo).

### Badges and status indicators

Badges in README: Python version, License MIT, FastAPI version, React 19, MCP protocol, GitHub stars. No CI status badge despite CI being present.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` file at repo root (1080 bytes); SPDX `MIT` via GitHub license API.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` at repo root. No `.github/ISSUE_TEMPLATE/` or `.github/PULL_REQUEST_TEMPLATE.md`.

## Cross-platform discipline

### POSIX with documented platform rejection

Plugin Windows-aware: `auto_install.py` and `bootstrap.py` have explicit `sys.platform == "win32"` branches. CI does not test Windows path.

## Cross-role tools

### Python (stdlib + pip + uv)

Python is the runtime for hooks (12 scripts under `plugin/hooks/`), the MCP server (`aiteam.mcp.server`), the install scripts, and tests. CI uses Python 3.12. No `uv`, no `uvx` usage anywhere. Pip is the dep installer. `pyproject.toml` is hatchling-built PyPI package `ai-team-os`.

### Node + npm + npx

Node 22 for the React dashboard (`dashboard/` tree, TypeScript + Vite). `dashboard/package-lock.json` cached in CI. `npx tsc -b --noEmit` for typecheck.

### Bash

`plugin/scripts/install-deps.sh` (dormant alternative install path).

### `${CLAUDE_PLUGIN_ROOT}` env var

Used by hooks for path resolution (e.g. when locating `plugin.json`).

### `${CLAUDE_PLUGIN_DATA}`

`bootstrap.py` (dormant) creates `${CLAUDE_PLUGIN_DATA}/venv` — not on the active install path.

### `hookSpecificOutput.additionalContext`

`auto_install.py` emits via this envelope on first-install success ("Please restart Claude Code to activate MCP tools").

