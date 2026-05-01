# CronusL-1141/AI-company

## Identification

- **URL**: https://github.com/CronusL-1141/AI-company
- **Stars**: 160
- **Last commit date**: 2026-04-14 (pushed_at 2026-04-14T10:49:21Z; updated_at 2026-04-19)
- **Default branch**: `master` — confirmed via `gh api repos/.../`; only `refs/heads/master` present, no `main`. Legacy git-init default; the repo's own CI `branches: [master, main]` and `session_bootstrap.py` update-check try `origin/main` then fall back to `origin/master`, so the author is aware that `main` is the modern default but did not rename.
- **License**: MIT (SPDX `MIT`, `LICENSE` at repo root, 1080 bytes)
- **Sample origin**: primary + dep-management (community)
- **One-line purpose**: "AI Team OS — Multi-Agent Team Operating System for Claude Code. 40+ MCP tools, 22 agent templates, task wall, meeting system, dashboard." (GitHub `description` field). README tagline: "Turn Claude Code into a multi-agent team operating system with persistent coordination, task management, and autonomous loop execution." (Note: README and GitHub description drift — README advertises 107 MCP tools / 25 agent templates, GitHub blurb says 40+/22; plugin agents directory contains 24 `.md` files.)

## 1. Marketplace discoverability

- **Manifest layout**: two `marketplace.json` files are present — the canonical one at `.claude-plugin/marketplace.json` (repo root), and a second at `plugin/.claude-plugin/marketplace.json`. Per Claude Code plugin conventions, the root one is what the marketplace installer consumes; the plugin-scoped one appears to be left over from local-dev iteration and is ignored by the marketplace discovery path (the plugin directory only needs `plugin.json`).
- **Marketplace-level metadata**: `metadata.{version, description}` wrapper present in root manifest (`metadata.version: "1.0.0"`, `metadata.description: "Self-driving AI company OS — turn Claude Code into a persistent, self-managing dev team"`). Root manifest also has top-level `owner.{name,url}`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: root manifest plugin entry uses `category: "productivity"` only (no `tags`, no `keywords`). The redundant nested `plugin/.claude-plugin/marketplace.json` adds `tags: ["team", "agents", "automation", "project-management"]` to the same plugin entry, but since the nested manifest isn't the one discovered by the marketplace installer, those tags don't reach the marketplace UI.
- **`$schema`**: absent in both manifests.
- **Reserved-name collision**: no. Plugin `name` is `ai-team-os`.
- **Pitfalls observed**:
    - Two manifests present with drift — root entry version `0.6.0`, nested entry version `1.3.4`. The nested one matches `plugin/.claude-plugin/plugin.json` and the published pyproject `version`; the root manifest's `0.6.0` is stale. Marketplace users therefore see `0.6.0` in the listing even when the plugin itself is at 1.3.4.
    - Redundant nested marketplace.json invites future drift — one authoritative manifest is the convention.
    - `category` but no `tags` on the authoritative manifest loses discoverability.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./plugin"` in root marketplace.json; nested plugin/marketplace.json uses `"source": "./"` relative to itself).
- **`strict` field**: default (implicit true) — neither manifest sets `strict`.
- **`skills` override on marketplace entry**: absent.
- **Version authority**: both (drift risk observed). `plugin/.claude-plugin/plugin.json` version `1.3.4`, `pyproject.toml` version `1.3.4`, nested `plugin/.claude-plugin/marketplace.json` version `1.3.4`, but root `.claude-plugin/marketplace.json` plugin entry version `0.6.0`. Four places declaring the version, three agree, one is stale.
- **Pitfalls observed**: version duplicated across four locations with manual sync; root marketplace entry is behind by an entire minor+patch run.

## 3. Channel distribution

- **Channel mechanism**: no split. Users pin by git ref (tag) via Claude Code's marketplace install flow or by cloning and pointing at the `plugin/` directory locally. Repo has 6 semver tags (`v1.2.0`, `v1.3.0`, `v1.3.1`, `v1.3.2`, `v1.3.3`, `v1.3.4`) on the single `master` branch.
- **Channel-pinning artifacts**: absent. No `stable-tools`/`latest-tools` pattern, no dev-counter scheme, no release branch.
- **Pitfalls observed**: none beyond the version drift in section 2.

## 4. Version control and release cadence

- **Default branch name**: `master`. Likely legacy git-init default; the author's code acknowledges `main` as an alternative (CI triggers on both; update-checker tries `origin/main` first).
- **Tag placement**: on `master` only — 6 tags (`v1.2.0` through `v1.3.4`) on tagged commits, all reachable from `master`.
- **Release branching**: none. Single long-lived `master`.
- **Pre-release suffixes**: none observed in the 6 tags.
- **Dev-counter scheme**: absent. `plugin.json` versions are hand-bumped at release time (1.2.0 → 1.3.0 → 1.3.1 → 1.3.2 → 1.3.3 → 1.3.4).
- **Pre-commit version bump**: no.
- **Pitfalls observed**: none for the release cadence itself; the drift issue is in manifests (section 2), not tags.

## 5. Plugin-component registration

- **Reference style in plugin.json**: external file reference for MCP (`mcpServers: "./.mcp.json"`). No explicit path arrays for skills/commands/agents/hooks — those rely on default discovery under the plugin directory.
- **Components observed**:
    - skills: yes (`plugin/skills/` — `continuous-mode`, `meeting-facilitate`, `meeting-participate`, `os-register`)
    - commands: yes (`plugin/commands/` — 8 `os-*.md` files: `os-doctor`, `os-help`, `os-hooks`, `os-init`, `os-meeting`, `os-status`, `os-task`, `os-up`)
    - agents: yes (`plugin/agents/` — 24 `.md` files; templates for tech-lead, backend-architect, frontend-developer, QA, bug-fixer, debate-advocate/critic, meeting-facilitator, etc.)
    - hooks: yes (`plugin/hooks/hooks.json` plus 12 Python scripts — see section 9/10)
    - .mcp.json: yes (`plugin/.mcp.json` — one server `ai-team-os` invoked via `python -m aiteam.mcp.server`)
    - .lsp.json: no
    - monitors: no (`monitors.json` not present)
    - bin: no
    - output-styles: no
- **Agent frontmatter fields used**: `name`, `description`, `model` (uniformly `opus` across sampled templates), `color` (e.g., `violet`, `green`) on engineering templates; `team-member.md` uses `name`, `description`, `model`, `skills` (list of skill names the agent gets access to: `os-register`, `meeting-participate`). No `tools`, `memory`, `background`, `isolation`, or namespaced field usage observed.
- **Agent tools syntax**: not applicable — no `tools` field used on any sampled agent. Agents rely on default tool access.
- **Pitfalls observed**:
    - Plugin `settings.json` hard-sets `"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}` — per an in-code comment in `auto_install.py`, "Plugin settings.json env field is NOT supported by CC (only 'agent' key works)", so the hook writes the env var directly to `~/.claude/settings.json` as a workaround. This is a soft divergence from the plugin-reference contract for `settings.json`.
    - `configs.json`-style marketplace configs absent — the plugin takes config via `.env` files in its own data directory rather than via Claude Code's `userConfig`.

## 6. Dependency installation

- **Applicable**: yes — heavy Python dep footprint (FastAPI, uvicorn, fastmcp, LangGraph, LangChain-Anthropic, SQLAlchemy, Alembic, Pydantic, aiosqlite, etc.) plus a TypeScript/React dashboard.
- **Dep manifest format**: `plugin/requirements.txt` (pip, 14 pinned minimum-version deps) is the plugin-distributed manifest; the repo root also carries a full `pyproject.toml` (hatchling-built PyPI package `ai-team-os`) with a superset of dependencies including optional `bm25`, `full`, and `dev` groups.
- **Install location**: mixed and inconsistent. Three install paths coexist:
    1. SessionStart hook `plugin/hooks/auto_install.py` — runs `pip install git+https://github.com/CronusL-1141/AI-company.git` into whatever Python `sys.executable` resolves to (typically user-global or the currently-active interpreter). No venv isolation.
    2. MCP server entry `plugin/bootstrap.py` (not actually referenced by the active `.mcp.json`, but kept in tree) — creates `${CLAUDE_PLUGIN_DATA}/venv` and pip-installs requirements plus the `aiteam` package into that venv, then injects it onto `sys.path` and rewrites `sys.executable`.
    3. `plugin/scripts/install-deps.sh` — same venv-based install as bootstrap.py but as a bash script; neither hooks.json nor `.mcp.json` invokes it.
    
    The active install path on marketplace install is (1); (2) and (3) are dormant code paths.
- **Install script location**: `plugin/hooks/auto_install.py` (invoked as the first `SessionStart` hook with a 30000 ms timeout).
- **Change detection**: two mechanisms coexist.
    - `auto_install.py` uses existence-only detection — tries `import aiteam` and only installs if `ImportError`. No marker, no hash.
    - `bootstrap.py` and `install-deps.sh` use `diff -q`/byte-comparison against a copy of `requirements.txt` saved into `${CLAUDE_PLUGIN_DATA}/requirements.txt` as a marker.
- **Retry-next-session invariant**: `auto_install.py` prints the manual-fix command and returns without raising; marker file is never written on failure, so next session retries via the `import aiteam` probe. `bootstrap.py` copies the marker only after the subprocess runs, but it does not check return code — a failed install could still stamp the marker (weak invariant). `install-deps.sh` uses `set -e`, so on failure the marker copy never runs and next run retries.
- **Failure signaling**: mixed across the three scripts.
    - `auto_install.py` — prints a user-facing failure line to stderr, also writes a `hookSpecificOutput.additionalContext` JSON blob to stdout on success so CC surfaces "Please restart Claude Code to activate MCP tools." Never `exit(nonzero)` — hook failure is soft-swallowed.
    - `bootstrap.py` — `capture_output=True` on every subprocess with no `check=True`, so failures are silently swallowed; only the final `ImportError` from `aiteam` triggers `sys.exit(1)` with a stderr message.
    - `install-deps.sh` — `set -e` plus `echo "..." >&2` on progress; fail-loud.
- **Runtime variant**: Python pip. No `uv`, no `uvx` usage anywhere. The three scripts all call `pip` (or `sys.executable -m pip`) and `python -m venv`.
- **Alternative approaches**: none — no PEP 723 scripts, no `uvx` ad-hoc, no pointer-file pattern.
- **Version-mismatch handling**: none. No Python minor-version tracking; bootstrap.py recovers site-packages dir by scanning `venv/lib/python*/site-packages` at runtime, which accommodates whatever Python version created the venv but won't detect a Python-version upgrade that orphans the venv.
- **Pitfalls observed**:
    - Three overlapping install paths — only one is wired to SessionStart, but the other two (bootstrap.py, install-deps.sh) are still in tree and drift-prone. A reader has to trace hooks.json and .mcp.json to know which is live.
    - `auto_install.py` uses `pip install git+https://...` directly without `--user` or venv targeting, so it mutates the user's Python environment silently. If the user runs Claude Code under a system Python with restricted site-packages, install will fail and the hook will swallow the error.
    - Requires user to restart Claude Code after first session for MCP server to pick up the newly-installed package. This restart-loop is explicitly noted in the installer's `additionalContext` but still represents a documented first-run friction.
    - `bootstrap.py` does `sys.executable = str(venv_py)` after injecting site-packages — a subtle side effect for any caller that inspects `sys.executable` later.
    - Root `install.py` (17899 bytes) is a fourth, PyPI-style installer intended for manual `python install.py` use on the cloned repo (separate from the plugin hook path).

## 7. Bin-wrapped CLI distribution

- **Applicable**: no. No `plugin/bin/` directory; no shebang-wrapped entry points. The plugin's CLI surface is (a) slash commands under `plugin/commands/` and (b) Python console scripts `aiteam` and `ai-team-os-serve` registered in `pyproject.toml` `[project.scripts]` — those are installed into the Python environment's `bin/` by pip when the `ai-team-os` PyPI package is installed, not exposed via the Claude Code `bin/` convention.
- **`bin/` files**: not applicable.
- **Shebang convention**: not applicable.
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: not applicable for bin/; see section 6 for the MCP-server venv path.
- **Platform support**: not applicable.
- **Permissions**: not applicable.
- **SessionStart relationship**: not applicable.
- **Pitfalls observed**: none at this axis.

## 8. User configuration

- **`userConfig` present**: no. Neither `plugin/.claude-plugin/plugin.json` nor the marketplace entries declare `userConfig`.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable for `${user_config.KEY}`. However, runtime configuration is done out-of-band — the plugin reads `AITEAM_API_URL` from process env (primarily), from a `~/.claude/data/ai-team-os/api_port.txt` file written by the API server at startup (for dynamic-port discovery), and from `.env` files the user places in the cloned repo. The `.env.example` template documents `ANTHROPIC_API_KEY`, PostgreSQL creds, `REDIS_URL`, `API_PORT`, etc. — secrets live outside the Claude Code plugin config surface entirely.
- **Pitfalls observed**: secrets (`ANTHROPIC_API_KEY`) go via user-managed `.env` rather than through `userConfig` with `sensitive: true`. The trade-off is deliberate — the plugin backs a long-running server, not a one-shot invocation, so config needs to persist outside the Claude Code session — but users don't benefit from Claude Code's secret-handling affordances.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1 matcher group, matcher `Agent|Bash|Edit|Write`, 2 command entries — `workflow_reminder.py PreToolUse` and `send_event.py PreToolUse`. Purpose: `workflow_reminder.py` fires local reminders based on tool sequence (Leader-delegation-threshold counter, self-described target <100 ms, local-only file reads/writes, no HTTP); `send_event.py` forwards the event to the OS API for the dashboard.
- **PostToolUse hooks**: 1 matcher group, matcher `Agent|Bash|Edit|Write`, 2 command entries — `workflow_reminder.py PostToolUse` and `send_event.py PostToolUse`. Same split purpose.
- **PermissionRequest/PermissionDenied hooks**: `PermissionDenied` observed. `permission_denied_recovery.py` reads the denial JSON, calls `POST /api/hooks/diagnose_denial` on the OS API to classify the denial into one of four categories (`recoverable_with_retry`, `recoverable_with_workaround`, `needs_user_approval`, `permanent_denial`), then either emits retry hints, workaround guidance, Leader notifications, or logs silently. Falls back to keyword matching when API is unreachable. Retry state is persisted in `~/.claude/data/ai-team-os/permission_denied_retry.json` with 1-hour TTL to prevent retry loops.
- **Output convention**: `send_event.py` is HTTP-forwarding — silent except on HTTP error. `workflow_reminder.py` writes reminders to stdout (picked up by CC as `additionalContext`). `permission_denied_recovery.py` mixes — structured JSON via stdout for hook responses, text to stderr for operator logs. `task_completed_gate.py` is the strictest — writes a corrective string `[OS BLOCK] 任务 ... 未记录进展` to stderr and exits with code `2`, which is the documented hard-block convention for hooks.
- **Failure posture**: mixed per-hook, documented in code comments.
    - `send_event.py`, `context_tracker.py`, `pre_compact_save.py`, `cc_task_bridge.py`, `inject_subagent_context.py` — fail-open (silent try/except swallowing all errors; explicit comments "never block", "silent pass", "don't block CC").
    - `task_completed_gate.py` — fail-closed on validation failure (exit 2 when memo/result missing) but fail-open on API unreachability (silent exit 0 on malformed payload or missing task_id).
    - `permission_denied_recovery.py` — fail-open to API failures (falls back to keyword match), fail-closed on classified `permanent_denial`.
    - `auto_install.py` — fail-open (prints manual command to stderr on failure, never exits nonzero).
- **Top-level try/catch wrapping**: observed across all hooks — each `main()` wraps the stdin-parsing and main logic in try/except with explicit "silent" comments. This is a consistent convention; the centralized pattern isn't factored into a helper, but the discipline is uniform.
- **Pitfalls observed**:
    - 12-hook layout means every tool call (matcher `Agent|Bash|Edit|Write`) pays two subprocess spawns (workflow_reminder + send_event) per pre/post phase. No measurable-latency hard cap is set beyond the 3000 ms timeout.
    - `workflow_reminder.py` is 54 KB — large for a Pre/PostToolUse hook that claims <100 ms target. Worth watching for timeout drift.
    - Plugin's `hooks.json` extends beyond the documented core event set — `TaskCreated` and `TaskCompleted` are Claude Code hooks for the CC-native Task system, recently added (per CHANGELOG 1.3.0). A consumer on older Claude Code may see the hooks register as no-ops.

## 10. Session context loading

- **SessionStart used for context**: yes. `session_bootstrap.py` (23378 bytes) hits the local OS API (`http://localhost:8000` or the dynamic port from `api_port.txt`) for team status and task-wall top-5, and writes a Chinese-language briefing (Leader behavior rules 1-23, available agent templates enumerated from `~/.claude/agents/*.md`, available skills list) to stdout for injection into the Claude context. When the API is unreachable, it prints a service-start command instead. Also does an opportunistic 24-hour-cooldown git-fetch update check.
- **UserPromptSubmit for context**: yes. `context_tracker.py` reads the transcript JSONL referenced by the hook payload, sums `usage.input_tokens + cache_read + cache_creation` from the last assistant message, and emits `[CONTEXT WARNING]` at ≥80% or `[CONTEXT CRITICAL]` at ≥90% (with 1M-context-window auto-detection via model-name match or by-value fallback when token count exceeds 200 K).
- **`hookSpecificOutput.additionalContext` observed**: yes — `auto_install.py` uses it explicitly with `hookEventName: "SessionStart"` on successful first-install. Other SessionStart / UserPromptSubmit hooks write plain stdout rather than the structured wrapper.
- **SessionStart matcher**: none — no `matcher` key on the SessionStart entries, so all sub-events (`startup`, `clear`, `compact`) fire the full SessionStart chain. This means `auto_install.py`, `session_bootstrap.py`, and `send_event.py SessionStart` all run on every resume/clear too.
- **Pitfalls observed**:
    - SessionStart fans three hooks unconditionally (30 s + 5 s + 2 s timeouts). The 30 s timeout on `auto_install.py` is long enough to mask a hung pip install visibly; users report the typical first-session install as "~2 min" per bootstrap.py's own banner, which exceeds the 30 s budget. This is a known tension — the CHANGELOG notes retries.
    - `session_bootstrap.py` does a real-time git fetch (5 s timeout) against GitHub inside the startup path. With spotty connectivity or VPN interference this can chew up startup budget.
    - Briefing output is entirely Chinese — non-Chinese-reading users get 23 rules in CJK. No i18n layer.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: the plugin provides a React dashboard (`dashboard/` tree, built separately into `plugin/dashboard-dist/`) served from the FastAPI app on port 3000 — rich UI surface that sidesteps the Claude Code `monitors` mechanism entirely because it's served by the plugin's own HTTP server.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no. Neither `plugin.json` nor marketplace.json entries declare a `dependencies` array.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace; tags use `v1.3.4` shape, not the multi-plugin form).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: pytest (with `pytest-asyncio`, `pytest-cov`). `tests/` has `unit/`, `integration/` subtrees plus top-level `conftest.py`, `e2e_api_coverage.py`, `e2e_dashboard_coverage.py`, `smoke_api_comprehensive.py`, `test_wake_manager.py`, `test_workflow_reminder.py`. Dashboard has its own TypeScript compile check (no separate JS/TS test runner wired in CI).
- **Tests location**: `tests/` at repo root. No per-plugin `tests/` nesting.
- **Pytest config location**: `[tool.pytest.ini_options]` in `pyproject.toml` (`testpaths = ["tests"]`, `asyncio_mode = "auto"`).
- **Python dep manifest for tests**: `pyproject.toml` (`[project.optional-dependencies].dev` includes `pytest>=8.0`, `pytest-asyncio>=0.24.0`, `pytest-cov>=6.0`, `ruff>=0.8.0`, `mypy>=1.13.0`).
- **CI present**: yes.
- **CI file(s)**: `ci.yml` (1220 bytes) and `lint.yml` (883 bytes) — two workflows, cleanly split.
- **CI triggers**: `push` and `pull_request` on `[master, main]` for both workflows. No tag or schedule triggers.
- **CI does**:
    - `ci.yml` has two jobs. `test` — Python 3.12, ad-hoc `pip install pytest pytest-asyncio pytest-cov && pip install fastapi uvicorn sqlalchemy aiosqlite pydantic pydantic-settings pyyaml anyio && pip install fastmcp || true && pip install langgraph langchain-anthropic langchain-core || true`, then `python -m pytest tests/unit/ -v --tb=short 2>&1 || true`. Note the `|| true` on the test run — unit test failures don't fail CI. `dashboard-typecheck` — Node 22, `npm ci` in `dashboard/`, then `npx tsc -b --noEmit`.
    - `lint.yml` has two jobs. `ruff` — `ruff check src/ tests/`. `eslint` — `npm run lint` in `dashboard/`.
- **Matrix**: none. Single Python 3.12, single Node 22, single ubuntu-latest.
- **Action pinning**: by tag — `actions/checkout@v4`, `actions/setup-python@v5`, `actions/setup-node@v4`. No SHA pinning.
- **Caching**: built-in `setup-node` cache: `npm` with `cache-dependency-path: dashboard/package-lock.json`. No caching on `setup-python` despite repeated raw pip invocations.
- **Test runner invocation**: direct `python -m pytest tests/unit/ -v --tb=short 2>&1 || true`. Not wrapped in a test script.
- **Pitfalls observed**:
    - `|| true` after the pytest invocation reduces CI to a smoke check — unit-test failures don't block merge. Combined with `pip install fastmcp || true` etc., the CI tolerates environment-caused pip failures without distinguishing them from genuine regressions.
    - CI doesn't install the project itself (`pip install -e .`) — tests run against the ad-hoc dep set directly. Any import path that relies on installed console-script entry points would be untested.
    - No Python or OS matrix; Windows installer logic (auto_install.py, bootstrap.py have explicit `sys.platform == "win32"` branches) is untested in CI.
    - `ruff check src/ tests/` omits `plugin/hooks/*.py` from the lint sweep (though pyproject's ruff config does special-case these with `E501` ignore). Hook scripts don't get baseline lint.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — releases are manual. Six tags (`v1.2.0` through `v1.3.4`) exist on `master`, presumably created via `git tag` + `git push --tags`.
- **Tag-sanity gates**: none enforced by CI. `plugin.json` version and `pyproject.toml` version must be hand-matched to the tag name.
- **Release creation mechanism**: none — no GitHub Releases automation. CHANGELOG.md is curated by hand and not cross-referenced by CI to the tag.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: no — CHANGELOG.md is manual, not consumed by a release pipeline.
- **Pitfalls observed**: the stale `0.6.0` version string in root `.claude-plugin/marketplace.json` is the kind of drift that an automated tag-sanity gate would catch.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable. No `bun+zod`, no `claude plugin validate`, no pre-commit hook present.
- **Trigger**: not applicable.
- **Frontmatter validation**: no.
- **Hooks.json validation**: no.
- **Pitfalls observed**: the marketplace.json/plugin.json version drift would be caught by any validator that cross-checks the two files; absence of validation is a correlate.

## 16. Documentation

- **`README.md` at repo root**: present, 36781 bytes (substantial; English). Paired `README.zh-CN.md` (33734 bytes) with a top-of-file language switcher link. Rich — includes problem statement, architecture section, install matrix, MCP tool enumeration, agent template listing, feature table with badges.
- **Owner profile README at `github.com/CronusL-1141/CronusL-1141`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: `plugin/README.md` present (3497 bytes) — install-focused, duplicates parts of the root README. `plugin/hooks/README.md` also present (1790 bytes) — hook-specific.
- **`CHANGELOG.md`**: present at repo root (30090 bytes), Keep a Changelog format explicitly declared at top (`Format: [Keep a Changelog]`). Paired `CHANGELOG.zh-CN.md` (28931 bytes). Chronological-descending; every release block has Added/Changed/Fixed sections with prose explaining root causes (unusually detailed for a plugin repo).
- **`architecture.md`**: not present at root (`docs/` directory exists but is not introspected in depth here). The root `CLAUDE.md` references `docs/architecture.md` but that path wasn't verified.
- **`CLAUDE.md`**: at repo root (514 bytes — terse operator brief: tech stack, core constraints, Leader behavior). Not per-plugin.
- **Community health files**: none observed (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` absent from root listing). No `.github/ISSUE_TEMPLATE/` or `.github/PULL_REQUEST_TEMPLATE.md` introspected.
- **LICENSE**: present, SPDX `MIT` (via GitHub license API), `LICENSE` file at repo root.
- **Badges / status indicators**: observed in README — Python version, License MIT, FastAPI version, React 19, MCP protocol, GitHub stars. No CI status badge despite CI being present.
- **Pitfalls observed**:
    - Two CHANGELOGs (English + Chinese) with no sync-enforcement — drift possible.
    - Absent CI badge misses a trust signal despite CI being wired.
    - Root CLAUDE.md is operator-focused but doesn't mention the `auto_install.py` restart-loop that a new contributor would need to know about.

## 17. Novel axes

- **Plugin-runs-its-own-HTTP-server**. The plugin isn't a thin MCP wrapper — it expects a FastAPI server process to be running on localhost (default port 8000, with `api_port.txt` dynamic-discovery fallback). Every hook forwards events to this server over HTTP, and `session_bootstrap.py` queries it for team/task state. This trades Claude Code's tidy single-process model for a persistent-daemon architecture; hooks become event producers for a dashboard rather than in-process policy layers. Dashboard-as-plugin-UI (React on port 3000) extends this further — observability lives outside Claude Code entirely.
- **Dynamic-port coordination via sidecar file**. The API server writes the port it actually bound to into `~/.claude/data/ai-team-os/api_port.txt`, and every hook reads that file to resolve the URL before each call, with `AITEAM_API_URL` env as a override. This is a lightweight IPC contract — handy when port 8000 is taken, risky when two projects run concurrently (only one can win the file). CHANGELOG 1.3.2 flagged a related bug where `.mcp.json` hardcoded the env var and defeated this fallback.
- **Hook-as-classifier pattern**. `permission_denied_recovery.py` calls a plugin-server endpoint (`POST /api/hooks/diagnose_denial`) to classify the denial into one of four retry strategies. The hook offloads policy decisions to the sidecar server, keeping the hook script thin and allowing policy updates without redistributing the plugin.
- **Restart-required-for-MCP first-run pattern**. `auto_install.py` explicitly writes `additionalContext: "Please restart Claude Code to activate MCP tools. This is a one-time setup."` to stdout via `hookSpecificOutput`. This is one of the cleaner ways observed in the sample to handle the "MCP server needs the package on sys.path before Claude Code starts the server process" bootstrap-ordering problem — surface the required restart back into the Claude context rather than leaving the user to guess.
- **Agent-template pattern with Chinese prompts**. All 24 agent templates are written in Chinese (`description`, `身份与记忆` sections). This is a genuinely native-language-first plugin design — the prompts aren't translated from English. An English-only Claude Code user would still see the agent `description` field in Chinese in the template picker.
- **Task-completion hard-gate hook**. `task_completed_gate.py` on `TaskCompleted` exits code 2 with a stderr message if the associated task lacks memo or result in the OS task wall. This uses the documented hard-block convention but connects it to external business state (the sidecar API), not a local rule — a hook that enforces "you can't mark this done until you've logged progress".
- **Plugin settings.json env-field workaround**. `auto_install.py` notes in-code that plugin `settings.json` env fields are silently ignored by Claude Code and writes the required `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` directly into `~/.claude/settings.json` instead. Useful concrete data point on a documented-but-actually-broken plugin capability.
- **Dep install split across three redundant mechanisms**. `auto_install.py` (SessionStart, wired), `bootstrap.py` (would be used by `.mcp.json` if it pointed at it, currently dormant), and `install-deps.sh` (bash alternative, not wired). The authoritative path is (1), but (2) and (3) sit in tree as rejected-but-retained alternatives. Novel in that many repos delete unused install scripts — keeping them suggests iteration that didn't consolidate.
- **Large workflow-reminder hook**. `workflow_reminder.py` is 54 KB — large enough to represent a non-trivial rules engine in the hook layer. Warrants examination as a pattern of "thick local hook, thin sidecar server" for the subset of reminders that don't need HTTP.

## 18. Gaps

- **`docs/architecture.md` existence not verified**. Root `CLAUDE.md` references the path but `docs/` directory content was not fetched. Would resolve by listing `docs/`.
- **Complete `workflow_reminder.py` logic not read**. Only the first 60 lines sampled — covers imports and B0.9-style delegation-threshold constants but not the actual rule matching. A full read (54 KB) would reveal whether reminders are table-driven or inline.
- **Every agent template's frontmatter not enumerated**. Sampled three (`engineering-ai-engineer`, `engineering-backend-architect`, `team-member`) — all use `name`, `description`, `model`, `color` with the `team-member` variant adding `skills`. Remaining 21 templates presumed similar but not confirmed; a template could carry `tools` or namespaced frontmatter that the sample missed.
- **Plugin hooks/README.md content not inspected**. Present but not fetched — could carry installation or debugging notes that complement section 16.
- **`plugin/skills/*/SKILL.md` full structures not enumerated**. Only `meeting-facilitate` and `os-register` heads sampled. `continuous-mode` and `meeting-participate` not fetched.
- **Slash-command bodies not sampled beyond `os-status.md`**. Enough to see the frontmatter shape but not the command-body MCP invocation patterns across all 8.
- **Dashboard package.json / eslint config not fetched**. Existence confirmed via CI workflow references (`dashboard/package-lock.json`, `npm run lint`); actual contents not inspected.
- **`plugin/docs/ecosystem-guide.md` (17252 bytes) not fetched**. Could be a substantive architectural reference that the plugin exposes to users; would inform section 16's "documentation" posture.
- **Nested `plugin/.claude-plugin/marketplace.json` discovery behavior**. Assumption is that Claude Code discovers only the root manifest based on docs-plugin-marketplaces.md; if the nested one is also picked up, the tag-set and version-drift behavior differ. Verifying would require either running the plugin installer or reading the Claude Code plugin-loader source.
- **Whether `plugin/.mcp.json` is actually loaded by Claude Code**. The plugin.json has `mcpServers: "./.mcp.json"` which is the documented indirection pattern, but whether bootstrap.py ever runs (its logic suggests it's meant to be invoked via a pyproject console script or referenced from `.mcp.json`, but the active `.mcp.json` uses `python -m aiteam.mcp.server` directly) would require live trace.
