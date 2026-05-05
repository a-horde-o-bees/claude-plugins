# Sample

Mirrors of `https://github.com/includeHasan/prospect-studio`. Single-plugin-at-root marketplace at `1.7.0` providing a B2B lead generation, prospecting, and outreach workspace for Claude Code with optional Frappe/ERPNext CRM sync — bundles 10 skills, 7 agents, 6 MCP servers (3 bundled local Node, 3 third-party remote), and a 4-hook analytics recording pipeline.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root with one plugin entry whose source is the repo root itself (`"source": "./"`). The repo is simultaneously the marketplace and the single plugin. Marketplace name `prospect-studio-marketplace`; plugin name `prospect-studio`. Marketplace-level metadata is sparse — only `name`, `owner`, and `plugins[]`. No top-level `description`, no `metadata` wrapper, no `metadata.pluginRoot`. Commit `286602d` ("fix: marketplace source must start with ./ per schema") documents that bare `"."` fails validation; `"./"` is required.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`source: "./"` — plugin lives at repo root. Single-plugin marketplace; no mix.

### `strict` field default

`strict` field absent — implicit true.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

The marketplace entry carries only `name`, `source`, `description` — no `category`, `tags`, or `keywords`. `plugin.json` carries `keywords: ["lead-generation", "sales", "market-research", "b2b", "crm", "prd"]` — keywords on the plugin manifest, no parallel facets on the marketplace entry. `plugin.json` description and README lead paragraph disagree on scope ("lead generation, prospecting, and outreach" vs "lead generation, market research, and business document workspace") — single-source-of-truth drift.

### `$schema` absence on per-plugin manifests

Absent on both `marketplace.json` and `plugin.json`.

## Channel distribution

### No pinning surface

Users pin via `@prospect-studio-marketplace` but there is no stable/latest separation — installs always resolve to `main`. No release branches, no `stable-*` / `latest-*` marketplaces. Update instructions in README tell users to re-run `/plugin marketplace add` to pick up a new `main`.

## Tag and release lifecycle

### No tags at all

No git tags in the repo (API `/tags` returns empty). No GitHub `/releases` entries. `CHANGELOG.md` uses semver headings (`[1.7.0]`, `[1.6.0]`, …) but no git tags back them. Anyone wanting to `git checkout v1.6.0` has no anchor. Version bumps are manual commits (`chore: v1.6.0`, `feat: v1.7.0`); `plugin.json` moves straight from `1.1.0` → `1.6.0` → `1.7.0` in commit messages.

## Version coordination

### Single source of truth (`plugin.json` only)

`plugin.json` is the only version surface — `1.7.0`. Marketplace entry has no `version` field, so there is no drift surface. CHANGELOG entries are versioned by hand to match.

## Plugin-component registration

### Default convention discovery

`plugin.json` has no `skills`, `agents`, `commands`, `hooks`, or `mcpServers` fields. All components are discovered by directory convention.

### `.mcp.json` sibling file

`.mcp.json` lives at repo root (not under `.claude-plugin/`). Six servers declared: 3 bundled local Node servers (`web-scraper`, `frappe`, `analytics`) plus 3 third-party (Playwright via `npx`, SerpAPI and Apify as `type: remote` HTTP).

## Plugin-component placement

### Inside plugin directory

Single-plugin-at-root layout means everything is inside the plugin directory by definition (plugin = repo).

## Component composition

### Skills (universal)

Ten skills under `skills/`: `competitive-intel`, `csv-import`, `daily-briefing`, `lead-research`, `meeting-notes`, `pipeline-review`, `prospect-discovery`, `sales`, `setup`, `weekly-report`.

### Agents

Seven agents under `agents/`: `analyst`, `analytics`, `coach`, `discovery`, `outreach`, `research`, `sales`.

### Hooks

`hooks/hooks.json` registers a SessionStart hook plus three PostToolUse entries (one with no matcher, one with `Write|Edit`, one with `mcp__serpapi|WebFetch|WebSearch`) plus a UserPromptSubmit and Stop entry — 4-hook analytics recording pipeline.

### MCP servers

Six servers in root `.mcp.json`: three bundled local Node MCP servers in `mcp-server/` (`web-scraper`, `frappe`, `analytics`) sharing one `mcp-server/package.json`; Playwright MCP via `npx @playwright/mcp@latest`; SerpAPI and Apify as `type: remote` with bearer-token headers.

## Agent declaration conventions

### `model` + `effort` + `maxTurns` for cost control

The `sales` agent declares `model: sonnet`, `effort: high`, `maxTurns: 60` — cost-control orchestration knobs on top of the standard frontmatter.

### Tool-restricted with orchestration knobs

The `sales` agent uses `disallowedTools: Bash, scrape_url, scrape_company_intel, find_contacts, batch_scrape` (subtractive denylist) without a corresponding `tools:` allowlist — relies on default tool set minus the listed exclusions.

### Read-only agents

The `analytics` agent has both an explicit `tools:` allowlist (read-only tools: `Read, Grep, Glob, Bash, mcp__analytics__analytics_flush, mcp__analytics__analytics_query, mcp__analytics__analytics_summary, mcp__analytics__analytics_session_report, mcp__analytics__analytics_prompts, mcp__analytics__analytics_duplicates, mcp__analytics__analytics_pending`) AND a `disallowedTools:` listing `Write, Edit, mcp__frappe__frappe_push_lead_file, mcp__frappe__frappe_update_lead`. Belt-and-suspenders read-only enforcement — both an allowlist and explicit denial of mutation tools.

### Fully-qualified MCP tool names

Tool references use the `mcp__<server>__<tool>` form, e.g., `mcp__analytics__analytics_flush`, `mcp__frappe__frappe_update_lead`. No bare tool names for MCP-provided tools.

## Dependency installation

### SessionStart hook → npm install local to plugin

Three bundled local Node MCP servers (`web-scraper`, `frappe`, `analytics`) share one `mcp-server/package.json` (ESM — `"type": "module"`) declaring `@modelcontextprotocol/sdk`, `cheerio`, `mongoose`, `zod`. `scripts/install-deps.sh` is invoked from `hooks/hooks.json` on `SessionStart` as `bash "${CLAUDE_PLUGIN_ROOT}/scripts/install-deps.sh"`. Install location is `${CLAUDE_PLUGIN_ROOT}/mcp-server/node_modules` — explicitly NOT `${CLAUDE_PLUGIN_DATA}`. The script header documents the rationale: ESM module resolution walks up from the importer's filesystem location looking for `node_modules`; `NODE_PATH` is CJS-only and silently ignored by ESM `import`. Install command: `npm install --quiet --no-fund --no-audit --omit=dev`. No lockfile (`package-lock.json` not committed); transitive deps non-reproducible across sessions.

## Install change detection

### Diff-based byte comparison of manifest

sha256 hash of `mcp-server/package.json` is compared against a stored hash in `${CLAUDE_PLUGIN_ROOT}/mcp-server/node_modules/.package-hash`. Re-install fires when the saved hash differs OR `node_modules/` is missing. Fallback chain: `sha256sum` → `shasum -a 256` → last-resort `wc -c` (byte count, not a real hash — collides on same-length unrelated edits).

## Install failure posture

### Silent fail-through

Script's last meaningful statement is `cd … && npm install … && echo "${CURRENT_HASH}" > "${LOCK_MARKER}"` — if `npm install` fails, the sentinel is never written, so next session re-tries. But the partial `node_modules/` from a failed install is left in place (no explicit cleanup) — a half-installed tree can linger across sessions. `exit 0` at the end unconditionally; all stderr from `npm install` is swallowed (`2>/dev/null`). Opening comment states "Silently succeeds or fails — never interrupts the session." No JSON `systemMessage`, no `continue: false`, no exit 2. No `set -euo pipefail` — `cd "${SERVER_DIR}" && npm install …` silently continues if `cd` fails (though `&&` chain prevents sentinel write on any failure step).

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks/hooks.json` registers the install script directly on SessionStart with no matcher (fires on all sub-events).

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory. All executable entry points are MCP servers (JS) or hook scripts (Python/bash) invoked by the Claude Code harness, not user-invoked CLIs on PATH.

## Cross-platform discipline

### Polyglot wrapper for cross-OS hook invocation

The pattern `bash -c 'PY=$(command -v python3 || command -v python || command -v py); [ -n "$PY" ] && "$PY" <script> <arg> || exit 0'` is repeated five times inline across `hooks/hooks.json`. CHANGELOG 1.6.0 documents this as a Windows portability fix — `python3`-only shebangs work on macOS/Linux but silently fail on Windows/Git-Bash where `py` is the standard launcher. The trampoline resolves `python3 → python → py` and exits 0 if none are found.

## User configuration and authentication

### Native `userConfig` with `${user_config.KEY}` substitution

8 fields under `userConfig`: `serpapi_key`, `apify_token`, `frappe_url`, `frappe_api_key`, `frappe_api_secret`, `frappe_lead_owner`, `workspace_root`, `mongo_uri`. `${user_config.<key>}` observed in `.mcp.json` for `workspace_root`, `frappe_url`, `frappe_api_key`, `frappe_api_secret`, `frappe_lead_owner`, `mongo_uri`, `serpapi_key` (in remote MCP `Authorization: "Bearer ${user_config.serpapi_key}"` header), `apify_token`. `sensitive: true` correctly set on 5 secret keys (`serpapi_key`, `apify_token`, `frappe_api_key`, `frappe_api_secret`, `mongo_uri`); deliberately `sensitive: false` on the non-secret strings (`frappe_url`, `frappe_lead_owner`, `workspace_root`).

### Typed `userConfig` schema with rich field types

Every field declares `type` (`string` or `directory`), `title`, `description`. `workspace_root` uses `type: "directory"`. No `default` values. CHANGELOG 1.6.0 explicitly flags this as a fix from a prior state that lacked `type`/`title` and failed current manifest validation — the schema-validation breakage was reactive: older `userConfig` blocks silently broke installs until the schema requirement was discovered.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

`scripts/deadline-monitor.py` reads `CLAUDE_PLUGIN_OPTION_WORKSPACE_ROOT` env var as a fallback source for `WORKSPACE` — alongside the `${user_config.workspace_root}` substitution path.

## Tool-use enforcement

### PostToolUse `*` context tracking

One PostToolUse entry has no matcher — fires on every tool call (including Read/Grep/Glob reads). Calls `scripts/record-event.py tool_use` for analytics ingest. CHANGELOG 1.7.0 explicitly notes the payload is truncated (2000/4000/500 chars) "to keep JSONL readable" — deliberate coarse logging, high-volume write path into `.analytics/events.jsonl`.

### PostToolUse with selector matcher (targeted observation)

Two additional PostToolUse entries with selectors: matcher `Write|Edit` calls `scripts/track-document.py` (appends to `documents/activity-log.md`); matcher `mcp__serpapi|WebFetch|WebSearch` calls `scripts/track-search.py` (appends to `research/search-log.md`).

### PostToolUse-only for notification + observation

No PreToolUse, PermissionRequest, or PermissionDenied hooks. All tool-use enforcement is observation/recording; no blocking.

## Hook output contract

### JSON-only stdout, no stderr-human parallel

Every hook is `bash -c 'PY=$(command -v python3 || …); [ -n "$PY" ] && "$PY" <script> … || exit 0'`. No structured JSON `additionalContext`, no `systemMessage`, no stderr human text. Scripts themselves exit 0 silently on success or error — no machine-readable output to the harness.

## Hook failure posture

### Silent fail-open (`exit 0` always, retry every hook)

Three layers of fail-open: (1) the `bash -c … || exit 0` trampoline exits 0 when no Python interpreter is found; (2) each Python script wraps work in try/except → `sys.exit(0)`; (3) the install-deps.sh `exit 0` at script end. The `record-event.py` script (sampled) guards mkdir in try/except and `sys.exit(0)`s on failure, consistent with the "never block the session" posture stated in its docstring and in `install-deps.sh`. Over-determined silence — three independent layers each defaulting to non-blocking.

## Hook handler runtime

### Bash scripts at conventional path

Hooks invoke a `bash -c` trampoline that probes for `python3 → python → py` and exec's the matched interpreter on a Python script under `scripts/`. Python is the actual handler runtime; bash is the polyglot dispatcher. Hooks live at conventional `hooks/hooks.json` plus scripts at `scripts/<name>.py`.

## Session context loading

### File-backed context written at SessionStart

`scripts/deadline-monitor.py` (SessionStart) scans `documents/leads/` and writes a daily brief to `notes/daily/YYYY-MM-DD-brief.md`. Does not emit context directly into the model's prompt via `additionalContext`; writes a file the user (or a subsequent agent call) can read. The user runs `/prospect-studio:daily-briefing` or opens the brief file. UserPromptSubmit hook is pure analytics (records the prompt text to `.analytics/events.jsonl`); does not inject context into the prompt.

## SessionStart matcher scope

### Empty matcher (all sub-events)

The SessionStart entry has no `matcher` field — fires on all SessionStart sub-events (startup/resume/clear by default).

## Live monitoring

### `monitors.json` absent

No `monitors.json`. No declared minimum Claude Code version.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` has no `dependencies` key.

## Testing

### No tests

Root `CLAUDE.md` explicitly states "No test suite. The dev loop is: edit → reinstall the plugin → exercise skills manually." No `tests/` directory. The plugin ships bundled Node MCP servers, Python hooks, and 6 paid/remote integrations (SerpAPI, Apify, Frappe, MongoDB) with zero automated tests.

## CI workflow shape

### No CI

No `.github/` directory (API returns 404 on `/contents/.github`). Schema breakages (`source: "."` vs `"./"`; `userConfig` missing `type`/`title`) have shipped in prior versions and been fixed reactively — CHANGELOG 1.6.0 is almost entirely compat regression fixes.

## Release automation

### No release automation / manual

No release workflow. Releases are purely manual: bump `plugin.json`, edit `CHANGELOG.md` by hand, commit, push. GitHub `/releases` is empty. No git tags either — `/plugin marketplace add github:includeHasan/prospect-studio` always resolves to `main`.

## Marketplace validation

### No validation

No CI means `marketplace.json` / `plugin.json` / frontmatter / `hooks.json` validation all rely on reactive fixes from install-time errors reported by users. The schema fixes in 1.6.0 are the cost signature of this trade-off.

## Documentation surface

### Dual-CLAUDE.md (developer + user-workspace)

Two `CLAUDE.md` files: root `CLAUDE.md` (~8.4 KB, developer-facing) and `templates/CLAUDE.md` deployed into users' workspaces by the `setup` skill (user-workspace-facing). Root file's opening warning is load-bearing — without it, an agent working on the plugin could easily edit the wrong one. A rename would make the structural distinction obvious but breaks the "deploy as `CLAUDE.md` into user workspace" workflow.

### CLAUDE.md template shipped for consumer projects

`templates/CLAUDE.md` is a consumer-facing template the `setup` skill installs into the user's workspace, distinct from the dev-of-plugin root CLAUDE.md.

### Free-form CHANGELOG variants

`CHANGELOG.md` (~16.9 KB). Header declares "Format: [Semantic Versioning](https://semver.org)" but entries follow Keep-a-Changelog-ish conventions (`## [1.7.0] — 2026-04-11` with narrative subsections). Not strictly KAC (no `Added`/`Changed`/`Fixed` bucket headings). README at repo root (~6.7 KB) covers what the plugin does, prerequisites, install, first-time setup, skill/agent listing, data-source tiering with cost tiers, workspace layout, team usage, update, contributing, license. No `architecture.md` at root — architectural content is in root `CLAUDE.md` ("Architecture" section, five numbered layers).

## License declaration

### LICENSE declared in manifests, no LICENSE file

`plugin.json` declares `"license": "MIT"` and README ends with "## License\n\nMIT", but no `LICENSE` file at repo root. GitHub's license detector returns `license: null`. Downstream consumers have no SPDX anchor; the marketplace listing cannot show a license badge.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md`. A brief "Contributing" section is embedded in the root README. No badges or status indicators in README.

## Cross-role tools

### Node + npm + npx

Three bundled local MCP servers under `mcp-server/` install via `npm install --quiet --no-fund --no-audit --omit=dev`. Playwright MCP launches via `npx @playwright/mcp@latest` declared in `.mcp.json`. ESM (`"type": "module"`) throughout the bundled servers.

### Python (stdlib + pip + uv)

Hook scripts under `scripts/` are Python — `record-event.py`, `track-document.py`, `track-search.py`, `deadline-monitor.py`. Invoked via the bash polyglot trampoline (`python3 → python → py`). No venv; no pip install; stdlib only, plain `#!/usr/bin/env python3` shebangs.

### `${CLAUDE_PLUGIN_ROOT}` env var

Used to resolve the install location for bundled MCP server deps (`${CLAUDE_PLUGIN_ROOT}/mcp-server/node_modules`) and as the script base path in hook commands (`bash "${CLAUDE_PLUGIN_ROOT}/scripts/install-deps.sh"`).

## Server runtime (MCP)

### Local venv built by SessionStart hook

The three bundled local Node MCP servers (`web-scraper`, `frappe`, `analytics`) share one `mcp-server/package.json` with `node_modules` installed by the SessionStart hook into `${CLAUDE_PLUGIN_ROOT}/mcp-server/node_modules`. Each server is a separate process started by the harness from `.mcp.json` per-server `command`/`args` entries. ESM resolution forces in-tree `node_modules` because `import` walks the filesystem.

### Runtime-fetched server via `npx -y`

Playwright MCP declared in `.mcp.json` as `npx @playwright/mcp@latest` — fetched on demand by npx, no install step.

### Remote HTTP MCP

SerpAPI and Apify both declared as `type: remote` in `.mcp.json` with `headers.Authorization: "Bearer ${user_config.<key>}"`. Outbound HTTP servers; not local processes.

## Telemetry and self-evaluation

### Multi-hook recording pipeline → MCP server → read-only agent

Five-layer pipeline: (1) 4 hooks (SessionStart, UserPromptSubmit, Stop, PostToolUse with-and-without matchers) feed (2) a single Python recorder (`scripts/record-event.py` and friends), which appends to (3) `.analytics/events.jsonl`, which is then flushed to MongoDB by (4) a dedicated bundled `analytics` MCP server, which is then queried by (5) a dedicated read-only `analytics` agent with a hard-coded read-only tool allowlist. Workspace-observability subsystem implemented as a coherent five-layer pattern within a single plugin.

## API-cost transparency and cost-gated MCP tools

### Explicit cost-model section in README

README documents a data-source tiering with cost tiers — Apify is opt-in and strictly rule-gated (`icp_score ≥ 7` or `priority: high/urgent`, always confirmation-gated, forbidden in stage 1 of bulk discovery, exactly four Actors pinned via URL query string `?tools=docs,code_crafter/leads-finder,…`). Rule-enforcement is distributed across three files (two agent prompts plus `templates/CLAUDE.md`); root `CLAUDE.md` names them as a coupled contract. Pinning a narrow tool subset at the server URL is a defensive configuration move against cost surprises.

## State persistence

### JSONL append-only event logs

`.analytics/events.jsonl` is the analytics recorder's append-only output. Tool-use events, prompts, and session lifecycle events all funnel into the same JSONL, then flushed to MongoDB by the `analytics` MCP server.
