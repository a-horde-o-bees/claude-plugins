# includeHasan/prospect-studio

## Identification

- **URL**: https://github.com/includeHasan/prospect-studio
- **Stars**: 0
- **Last commit date**: 2026-04-11 (commit `2d7bbf4`, "feat: v1.7.0 — analytics MCP + event recording pipeline + analytics")
- **Default branch**: main
- **License**: MIT (declared in `plugin.json` and README; no `LICENSE` file at repo root — `licenses` API not populated)
- **Sample origin**: dep-management
- **One-line purpose**: "B2B lead generation, prospecting, and outreach workspace for Claude Code — with optional Frappe/ERPNext CRM sync" (from `plugin.json` description; README adds "market research, and business document workspace")

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root. Plugin source is the repo root itself (`"source": "./"`), so the repo is simultaneously the marketplace and the single plugin.
- **Marketplace-level metadata**: none — no `metadata` wrapper, no top-level `description`. `marketplace.json` has only `name`, `owner`, and `plugins[]`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: none — the marketplace entry has only `name`, `source`, `description`. No `category`, `tags`, or `keywords` on the entry. `plugin.json` carries `keywords: ["lead-generation","sales","market-research","b2b","crm","prd"]`, but those live on the plugin manifest, not the marketplace entry.
- **`$schema`**: absent on both `marketplace.json` and `plugin.json`.
- **Reserved-name collision**: no. Plugin name is `prospect-studio`; marketplace name is `prospect-studio-marketplace`.
- **Pitfalls observed**:
  - Commit `286602d` ("fix: marketplace source must start with ./ per schema") documents a live schema gotcha — bare `"."` fails validation; `"./"` is required. Worth propagating as a pattern-level warning.
  - `plugin.json` description and README lead paragraph disagree on scope ("lead generation, prospecting, and outreach" vs "lead generation, market research, and business document workspace"). Minor single-source-of-truth drift for the marketplace listing.

## 2. Plugin source binding

- **Source format(s) observed**: relative — `"source": "./"` (plugin is the repo root). Single-plugin marketplace; no mix.
- **`strict` field**: not present (default implicit true).
- **`skills` override on marketplace entry**: absent.
- **Version authority**: `plugin.json` only — marketplace entry has no `version` field, so there is no drift surface. `plugin.json` is `1.7.0`.
- **Pitfalls observed**: none observed — the single-plugin-at-root layout keeps binding simple.

## 3. Channel distribution

- **Channel mechanism**: no split. Users pin via `@prospect-studio-marketplace` but there is no stable/latest separation — installs always resolve to `main`.
- **Channel-pinning artifacts**: absent. No `stable-*` / `latest-*` marketplaces, no release branches.
- **Pitfalls observed**: none — the project is small and single-channel by design. Update instructions in README tell users to re-run `/plugin marketplace add` to pick up a new `main`.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: no tags in the repo (API `/tags` returns empty). `CHANGELOG.md` uses semver headings (`[1.7.0]`, `[1.6.0]`, …) but no git tags back them.
- **Release branching**: none. Only `main` exists.
- **Pre-release suffixes**: none observed.
- **Dev-counter scheme**: absent. `plugin.json` moves straight from `1.1.0` → `1.6.0` → `1.7.0` in commit messages.
- **Pre-commit version bump**: no. Version bumps are manual commits (`chore: v1.6.0`, `feat: v1.7.0`).
- **Pitfalls observed**:
  - CHANGELOG has versioned entries but no corresponding git tags or GitHub releases — anyone wanting to `git checkout v1.6.0` has no anchor. Worth flagging as a missing-tag-discipline anti-pattern.
  - No GitHub `/releases` entries either; the "Install" instructions recommend `/plugin marketplace add github:…` which resolves to `main`, so there is no pinnable release artifact.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery only — `plugin.json` has no `skills`, `agents`, `commands`, `hooks`, or `mcpServers` fields. All components are discovered by directory convention (`skills/*/SKILL.md`, `agents/*.md`, `hooks/hooks.json`, `.mcp.json`).
- **Components observed**: skills (10 — `competitive-intel`, `csv-import`, `daily-briefing`, `lead-research`, `meeting-notes`, `pipeline-review`, `prospect-discovery`, `sales`, `setup`, `weekly-report`) / commands (no) / agents (7 — `analyst`, `analytics`, `coach`, `discovery`, `outreach`, `research`, `sales`) / hooks (yes — `hooks/hooks.json`) / .mcp.json (yes — at repo root, 6 servers) / .lsp.json (no) / monitors (no) / bin (no) / output-styles (no).
- **Agent frontmatter fields used**:
  - `sales`: `name`, `description`, `model: sonnet`, `effort: high`, `maxTurns: 60`, `disallowedTools: Bash, scrape_url, scrape_company_intel, find_contacts, batch_scrape`.
  - `analytics`: `name`, `description`, `tools: Read, Grep, Glob, Bash, mcp__analytics__analytics_flush, mcp__analytics__analytics_query, mcp__analytics__analytics_summary, mcp__analytics__analytics_session_report, mcp__analytics__analytics_prompts, mcp__analytics__analytics_duplicates, mcp__analytics__analytics_pending`, `disallowedTools: Write, Edit, mcp__frappe__frappe_push_lead_file, mcp__frappe__frappe_update_lead`.
  - Union of fields observed across the two sampled agents: `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`. Not all fields appear on every agent (e.g., `sales` omits `tools` but uses `disallowedTools` to subtract from defaults).
- **Agent tools syntax**: plain tool names / plain MCP tool ids (e.g., `mcp__analytics__analytics_flush`). No permission-rule syntax like `Bash(npm *)` observed.
- **Pitfalls observed**:
  - Mix of `tools` (allowlist) and `disallowedTools` (denylist) across agents is intentional but ad-hoc — `sales` uses denylist to subtract a few specific tools, `analytics` uses both for belt-and-suspenders. No repo-level convention document explains when to reach for which.
  - `.mcp.json` lives at repo root (not `.claude-plugin/`) — legal for Claude Code plugins but worth noting against marketplaces that put it under `.claude-plugin/`.

## 6. Dependency installation

- **Applicable**: yes — three bundled local MCP servers (`web-scraper`, `frappe`, `analytics`) share a single `mcp-server/package.json` with Node dependencies (`@modelcontextprotocol/sdk`, `cheerio`, `mongoose`, `zod`).
- **Dep manifest format**: `package.json` (`mcp-server/package.json`, ESM — `"type": "module"`).
- **Install location**: `${CLAUDE_PLUGIN_ROOT}/mcp-server/node_modules` (observed in `scripts/install-deps.sh`). Explicitly **not** `${CLAUDE_PLUGIN_DATA}`, and the script header documents the reason: ESM module resolution walks up from the importer's filesystem location looking for `node_modules`; `NODE_PATH` is CJS-only and is silently ignored by `import`. So a separate data directory would break every `import` statement in every local MCP server. (Note: root `CLAUDE.md` still claims `${CLAUDE_PLUGIN_DATA}/node_modules` — stale documentation; the script is the source of truth.)
- **Install script location**: `scripts/install-deps.sh` (referenced from `hooks/hooks.json` as `bash "${CLAUDE_PLUGIN_ROOT}/scripts/install-deps.sh"` on `SessionStart`).
- **Change detection**: **sha256** of `package.json`, persisted to `${CLAUDE_PLUGIN_ROOT}/mcp-server/node_modules/.package-hash`. Fallback chain: `sha256sum` → `shasum -a 256` → last-resort `wc -c` (byte count, not a real hash). Re-install fires when the saved hash differs OR `node_modules/` is missing.
- **Retry-next-session invariant**: no `rm` on failure. The script's last meaningful statement is a chained `cd … && npm install … && echo "${CURRENT_HASH}" > "${LOCK_MARKER}"` — if `npm install` fails, the sentinel is never written, so next session's hash-compare sees no saved hash and re-tries. But the partial `node_modules/` from a failed install is left in place (no explicit cleanup), so a half-installed tree can linger across sessions.
- **Failure signaling**: silent. `exit 0` at the end unconditionally; all stderr from `npm install` is swallowed (`2>/dev/null`). The script's opening comment states "Silently succeeds or fails — never interrupts the session." No JSON `systemMessage`, no `continue: false`, no exit 2.
- **Runtime variant**: Node npm (ESM). Deps are declared in `mcp-server/package.json`; `npm install --quiet --no-fund --no-audit --omit=dev` is the install command.
- **Alternative approaches**: none used — no `npx` for the bundled servers (Playwright MCP *is* invoked via `npx @playwright/mcp@latest` in `.mcp.json`, but that's a third-party server, not dep-management for bundled code). No pointer file, no PEP-723-style shebang metadata (Python hooks use plain `#!/usr/bin/env python3`).
- **Version-mismatch handling**: none. Script does not track Node version or ABI; does not detect `node_modules` built against a different Node major.
- **Pitfalls observed**:
  - **Stale doc vs script drift.** Root `CLAUDE.md` says deps land in `${CLAUDE_PLUGIN_DATA}/node_modules` via `NODE_PATH`; the actual script installs into `${CLAUDE_PLUGIN_ROOT}/mcp-server/node_modules` and explicitly repudiates the `NODE_PATH` approach (ESM-incompatible). The comment block in `install-deps.sh` is the authoritative rationale; the CLAUDE.md block was not updated when the install location moved.
  - **No `set -euo pipefail`.** `cd "${SERVER_DIR}" && npm install …` silently continues if `cd` somehow fails, though the `&&` chain prevents sentinel write when any step fails.
  - **No lockfile.** `package.json` has no `package-lock.json` committed and `--omit=dev` is the only npm flag controlling selection. Transitive dep changes between sessions are non-reproducible.
  - **Fallback `wc -c` when neither sha tool is present** is an integrity regression — byte count collides across unrelated edits of the same length. Unlikely in practice but real.
  - **Partial install retention** — failed `npm install` leaves a half-populated `node_modules/` behind. Symptom on next session: `[ -d "${SERVER_DIR}/node_modules" ]` is true, sha didn't match, so reinstall fires again — eventually converges, but the hysteresis can hide a persistent failure mode (e.g., no network) because the script exits 0.

Comparison to Arcanon-hub/arcanon's ESM stance: both repos pick `${CLAUDE_PLUGIN_ROOT}` over `${CLAUDE_PLUGIN_DATA}` and both cite ESM's filesystem-walk resolution as the reason. Differences:

| Aspect | prospect-studio | Arcanon-hub/arcanon |
|---|---|---|
| Rationale location | inline comment header in `install-deps.sh` (visible to anyone reading the script) | planning-doc `.planning/milestones/v5.2.0-phases/059-runtime-dependency-installation/59-CONTEXT.md` (not surfaced in script or README) |
| Change detection | sha256 of `package.json` (+ `wc -c` last-resort fallback) | `diff -q` of `runtime-deps.json` against `${CLAUDE_PLUGIN_DATA}/.arcanon-deps-installed.json`, double-checked with `[ -d node_modules/<pkg> ]` |
| Retry-next-session | no `rm` on failure — sentinel simply not written | explicit `rm -rf node_modules` + `rm -f $SENTINEL` on failure |
| Second install path | none | `mcp-wrapper.sh` re-runs `npm install` if a specific dep dir is missing at MCP launch (race-safe self-heal) |
| Failure posture | silent `exit 0`; stderr swallowed | silent via `trap 'exit 0' ERR`; preserves `set -e` semantics |
| Install flags | `--quiet --no-fund --no-audit --omit=dev` | no `--omit=dev` visible; includes `--package-lock=false` (trades reproducibility for not polluting `CLAUDE_PLUGIN_ROOT`) |
| Manifest shape | single `package.json` (npm reads it directly) | dual `package.json` + `runtime-deps.json` (latter is the sentinel-diff source) |

Shared design: install into `CLAUDE_PLUGIN_ROOT` because ESM walks the filesystem to resolve `import`. Divergent design: prospect-studio is minimal and single-path; arcanon is defensive (dual-install, explicit cleanup, drift-proof sentinel). prospect-studio makes the ESM rationale visible in the script itself, which is the better discoverability choice — a developer reading the hook sees the "why" without needing to find a planning doc.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — repo has no `bin/` directory. All executable entry points are MCP servers (JS) or hook scripts (Python/bash) invoked by the Claude Code harness, not user-invoked CLIs on PATH.

## 8. User configuration

- **`userConfig` present**: yes.
- **Field count**: 8 (`serpapi_key`, `apify_token`, `frappe_url`, `frappe_api_key`, `frappe_api_secret`, `frappe_lead_owner`, `workspace_root`, `mongo_uri`).
- **`sensitive: true` usage**: correct on 5 keys (`serpapi_key`, `apify_token`, `frappe_api_key`, `frappe_api_secret`, `mongo_uri`). Deliberately `sensitive: false` on the two non-secret configuration strings (`frappe_url`, `frappe_lead_owner`, `workspace_root` via `type: "directory"`). Anti-pattern not observed.
- **Schema richness**: typed — every field declares `type` (`string` or `directory`), `title`, `description`. No `default` values. Commit `c73ab0f`/CHANGELOG 1.6.0 explicitly flags this as a fix from a prior state that lacked `type`/`title` and failed current manifest validation.
- **Reference in config substitution**: `${user_config.<key>}` observed in `.mcp.json` for `workspace_root`, `frappe_url`, `frappe_api_key`, `frappe_api_secret`, `frappe_lead_owner`, `mongo_uri`, `serpapi_key` (remote MCP `Authorization` header), `apify_token`. `CLAUDE_PLUGIN_OPTION_WORKSPACE_ROOT` env var usage observed in `scripts/deadline-monitor.py` as a fallback source for `WORKSPACE`.
- **Pitfalls observed**:
  - `workspace_root` uses `type: "directory"`. Noted as a typed variant — not every plugin reaches for this. Useful data point for pattern-doc's userConfig taxonomy.
  - CHANGELOG 1.6.0 documents the schema-validation breakage ("every entry now has `type`/`title` required by the current plugin manifest schema") — suggests the plugin-manifest schema tightened at some point and older `userConfig` blocks silently broke installs. Pattern-doc relevance: the `type`/`title` requirement is load-bearing, not decorative.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: three entries in `hooks/hooks.json`.
  - No matcher (fires for all tools) → `scripts/record-event.py tool_use` (analytics ingest).
  - Matcher `Write|Edit` → `scripts/track-document.py` (appends to `documents/activity-log.md`).
  - Matcher `mcp__serpapi|WebFetch|WebSearch` → `scripts/track-search.py` (appends to `research/search-log.md`).
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: silent — every hook is `bash -c 'PY=$(command -v python3 || …); [ -n "$PY" ] && "$PY" <script> … || exit 0'`. No stdout JSON, no stderr human text. Scripts themselves are expected to exit 0 on error.
- **Failure posture**: fail-open across the board. The `bash -c` trampoline explicitly `exit 0`s when no Python interpreter is found, and each Python script is written to swallow exceptions and `sys.exit(0)`. CHANGELOG 1.6.0 documents this as a Windows portability fix (`python3` vs `python` vs `py`).
- **Top-level try/catch wrapping**: the one Python script sampled (`scripts/record-event.py`) guards its mkdir in `try/except` and `sys.exit(0)`s on failure, consistent with the "never block the session" posture stated in its docstring and in `install-deps.sh`.
- **Pitfalls observed**:
  - The `bash -c 'PY=$(command -v python3 || command -v python || command -v py); [ -n "$PY" ] && "$PY" <script> <arg> || exit 0'` pattern is repeated five times inline across `hooks/hooks.json`. Any change to the trampoline shape (e.g., adding a timeout flag, switching `command -v` to `type -P`) has to be replicated in every entry. No shared helper script extracted.
  - PostToolUse with no matcher fires on *every* tool call (including Read/Grep/Glob reads) — high-volume write path into `.analytics/events.jsonl`. CHANGELOG 1.7.0 explicitly notes the payload is truncated (2000/4000/500 chars) "to keep JSONL readable." The author is aware; pattern-doc readers should note this is deliberate coarse logging, not an oversight.

## 10. Session context loading

- **SessionStart used for context**: yes — `deadline-monitor.py` scans `documents/leads/` and writes a daily brief to `notes/daily/YYYY-MM-DD-brief.md`. It does not emit context directly into the model's prompt via `additionalContext`; it writes a file the user (or later agent calls) can read.
- **UserPromptSubmit for context**: no — the `UserPromptSubmit` hook is pure analytics (records the prompt text to `.analytics/events.jsonl`). It does not inject context into the prompt.
- **`hookSpecificOutput.additionalContext` observed**: no. None of the hook commands return structured JSON with `additionalContext`.
- **SessionStart matcher**: none — no `matcher` field on the SessionStart entry, so it fires on all SessionStart sub-events (startup/resume/clear by default).
- **Pitfalls observed**:
  - The "context load" is indirect — the daily brief is written to a file, not into the session prompt. This works for prospect-studio's workflow (users run `/prospect-studio:daily-briefing` or open the brief file), but a reader expecting `additionalContext` injection would miss that the context-loading happens via the *file-backed* convention, not the prompt-backed one.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — `plugin.json` has no `dependencies` key.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace.
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: none. Root `CLAUDE.md` explicitly states "No test suite. The dev loop is: edit → reinstall the plugin → exercise skills manually."
- **Tests location**: not applicable.
- **Pytest config location**: not applicable.
- **Python dep manifest for tests**: not applicable.
- **CI present**: no. Repo has no `.github/` directory (API returns 404 on `/contents/.github`).
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: none.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: not applicable.
- **Pitfalls observed**: the plugin ships bundled Node MCP servers, Python hooks, and 6 paid/remote integrations (SerpAPI, Apify, Frappe, MongoDB) with zero automated tests and zero CI. Schema breakages (`source: "."` vs `"./"`; `userConfig` missing `type`/`title`) have shipped in prior versions and been fixed reactively — CHANGELOG 1.6.0 is almost entirely compat regression fixes. A manifest-validation workflow would have caught both bugs pre-merge.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — releases are purely manual (bump `plugin.json`, commit, push).
- **Tag-sanity gates**: not applicable.
- **Release creation mechanism**: none — GitHub `/releases` is empty.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: manual — author edits `CHANGELOG.md` by hand per README step "Update CHANGELOG.md" in contributing section.
- **Pitfalls observed**: `CHANGELOG.md` version bumps are not backed by git tags or GitHub releases, so there is no way for a downstream user to pin to `v1.6.0` — `/plugin marketplace add github:includeHasan/prospect-studio` always resolves to `main`, which is whatever the author pushed most recently.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable.
- **Trigger**: not applicable.
- **Frontmatter validation**: no.
- **Hooks.json validation**: no.
- **Pitfalls observed**: see §13 — zero CI means `marketplace.json` / `plugin.json` / frontmatter / `hooks.json` validation all rely on reactive fixes from install-time errors reported by users. The schema fixes in 1.6.0 are the cost signature of this trade-off.

## 16. Documentation

- **`README.md` at repo root**: present (~6.7 KB). Covers what the plugin does, prerequisites, install, first-time setup, skill/agent listing, data-source tiering with cost tiers, workspace layout, team usage, update, contributing, license.
- **`README.md` per plugin**: not applicable — single-plugin-at-root layout means repo README *is* the plugin README.
- **`CHANGELOG.md`**: present (~16.9 KB). Format: a hybrid — header declares "Format: [Semantic Versioning](https://semver.org)" but entries follow Keep-a-Changelog-ish conventions (`## [1.7.0] — 2026-04-11` with narrative subsections). Not strictly KAC (no `Added`/`Changed`/`Fixed` bucket headings), but recognisable.
- **`architecture.md`**: absent at repo root. Architectural content is bundled into root `CLAUDE.md` (the "Architecture" section — five numbered layers with cross-reference rules).
- **`CLAUDE.md`**: present at repo root (~8.4 KB, developer-facing). A separate `templates/CLAUDE.md` is deployed into users' workspaces by the `setup` skill — that one is user-workspace-facing. Root `CLAUDE.md` opens by warning not to confuse the two audiences.
- **Community health files**: none — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`. A brief "Contributing" section is embedded in the root README instead.
- **LICENSE**: no `LICENSE` file at repo root. `plugin.json` declares `"license": "MIT"` and README ends with "## License\n\nMIT", but GitHub's license detector is empty (`license: null` on the repo API).
- **Badges / status indicators**: none observed in README.
- **Pitfalls observed**:
  - **No `LICENSE` file.** MIT is asserted in README and `plugin.json` but no actual license text is committed. Github's `licenses` field is null — downstream consumers have no SPDX anchor and the marketplace listing cannot show a license badge.
  - **Dual-CLAUDE.md naming collision.** Root `CLAUDE.md` and `templates/CLAUDE.md` share a filename across a cognitive boundary (dev-of-plugin vs user-of-plugin). Root file's opening warning is load-bearing — without it, an agent working on the plugin could easily edit the wrong one. A rename (`CLAUDE.md` + `templates/workspace-CLAUDE.md`) would make it structurally obvious, but breaks the "deploy as `CLAUDE.md` into user workspace" workflow.
  - **CLAUDE.md drift with install-deps.sh.** The CLAUDE.md "Architecture" block claims deps live at `${CLAUDE_PLUGIN_DATA}/node_modules` and that `NODE_PATH` points there. The actual script installs to `${CLAUDE_PLUGIN_ROOT}/mcp-server/node_modules` and its header block explicitly argues against the `NODE_PATH`/`CLAUDE_PLUGIN_DATA` approach. This is a classic stale-rationale symptom — the code refactored the install location; the architectural doc didn't follow.

## 17. Novel axes

- **Bundled analytics pipeline as a first-class plugin subsystem.** Most plugins either don't telemetrise at all or use ad-hoc logging. prospect-studio wires a 4-hook recording pipeline (SessionStart, UserPromptSubmit, Stop, PostToolUse with and without matchers) that feeds a single Python recorder, which appends to `.analytics/events.jsonl`, which is then flushed to MongoDB by a dedicated `analytics` MCP server, which is then queried by a dedicated read-only `analytics` agent with a hard-coded read-only tool allowlist. The architecture has five layers (hook → recorder → JSONL → MCP flush → agent) for workspace observability alone — unusual for a single-author plugin. Candidate pattern: "observability pipeline" as a coherent pattern distinct from generic hook usage.
- **Paid-service gating as codified policy.** Apify is opt-in and strictly rule-gated (`icp_score ≥ 7` or `priority: high/urgent`, always confirmation-gated, forbidden in stage 1 of bulk discovery, exactly four Actors pinned via URL query string `?tools=docs,code_crafter/leads-finder,…`). The rule-enforcement is distributed across three files (two agent prompts + `templates/CLAUDE.md`) and root `CLAUDE.md` names them as a coupled contract. Candidate pattern: "cost-gated MCP tool surface" — pinning a narrow tool subset at the server URL is a defensive configuration move that's worth factoring out.
- **Remote MCP with `sensitive: true` user config bearer-token injection.** `.mcp.json` declares SerpAPI and Apify as `type: remote` with `headers.Authorization: "Bearer ${user_config.<key>}"`. The `${user_config.…}` substitution flows through straight into an outbound HTTP header, with the keys marked `sensitive: true` so they live in the OS keychain and never hit disk. Worth noting as a pattern for "remote MCP + keychain-backed auth" distinct from local-MCP env-var injection.
- **Read-only agent via `tools` + `disallowedTools` belt-and-suspenders.** The `analytics` agent has both an explicit `tools:` allowlist (read-only tools only) and a `disallowedTools:` explicitly naming `Write`, `Edit`, and specific Frappe mutation tools. Redundant if `tools:` is a hard allowlist, but the author uses both — suggests either uncertainty about enforcement semantics or defensive coding against a future where `tools:` becomes a soft hint. Candidate pattern-doc bullet: the enforcement semantics of `tools` vs `disallowedTools` is not uniformly understood across the ecosystem.
- **File-backed SessionStart context** (vs `additionalContext`-backed). The daily pipeline brief is written to `notes/daily/YYYY-MM-DD-brief.md` rather than injected into the session prompt. The user either asks for it or the agent reads it on demand. This is a different context-loading posture from "inject a blob of text on every session start" — less intrusive, survives token limits, inspectable. Candidate as a distinct sub-pattern within §10.
- **Cross-platform Python trampoline in `hooks.json`.** The repeated `bash -c 'PY=$(command -v python3 || command -v python || command -v py); [ -n "$PY" ] && "$PY" <script> || exit 0'` pattern is explicitly documented in CHANGELOG 1.6.0 as a Windows-compatibility fix. Worth calling out in the pattern doc: Windows/Git-Bash-on-Windows installs are a real constraint, and the `python3`-only shebang assumption that works on macOS/Linux *silently* fails on Windows. The trampoline is the only observed cross-platform-Python-invocation pattern in this sample.
- **Silent-exit-0 discipline across every hook script.** Every hook script explicitly exits 0 on failure, by design stated in per-file comments. Composed with the `bash -c … || exit 0` trampoline, the total system is *three layers* of fail-open for any hook. This over-determined silence is characteristic of "never block the user's session" as an explicit principle. Contrast to Arcanon-hub/arcanon which uses `trap 'exit 0' ERR` — a more ergonomic form of the same principle.

## 18. Gaps

- **LICENSE file absence vs declared MIT.** Confirmed the file is missing at root and the GitHub licenses API is empty. Whether `LICENSE` is present in a subdirectory I did not search exhaustively would be resolved by `gh api repos/includeHasan/prospect-studio/git/trees/main?recursive=1 | jq '.tree[] | select(.path | test("(?i)licen[cs]e"))'` — the tree listing I pulled showed none, but I relied on the recursive-tree call, which caps at 100k entries (this repo is ~30 files, so no truncation risk).
- **No tags / releases** — could not observe a release-artifact workflow because none exist. Whether the author plans to start tagging, or whether releases live elsewhere (git bundle, external registry), is not discoverable from the repo itself. Would be resolved by issue tracker or author statement.
- **`track-document.py` / `track-search.py` internals** — I read `record-event.py` and `deadline-monitor.py` heads but not the full track-* scripts. Their exact write-path and idempotency discipline is inferred from CLAUDE.md's architecture description, not verified byte-by-byte. Would be resolved by `curl -s raw.githubusercontent.com/…/scripts/track-document.py` and `…/track-search.py`.
- **`.mcp.json` location convention** — prospect-studio puts `.mcp.json` at repo root, not under `.claude-plugin/`. Whether this is a docs-sanctioned location for single-plugin-at-root layouts, or something the harness tolerates but doesn't endorse, I did not resolve against `docs-plugins-reference.md` in this pass. Would be resolved by reading that context resource.
- **`effort: high`, `maxTurns: 60` agent frontmatter** — observed on the `sales` agent. Whether these are documented plugin-spec fields or model-specific extensions picked up by the Claude Code harness I did not verify against the plugins reference. Worth flagging because if they're non-standard, this is either a pattern to propagate or a harness-specific extension worth calling out as such.
- **`agents/analyst.md` vs `agents/analytics.md` naming collision.** Noted the author calls the distinction out in the `analytics` agent docstring ("You are not the analyst agent — that one does market research"), but I did not read `agents/analyst.md` directly to confirm the surface looks correctly distinct. Low-risk; resolved by one more raw.githubusercontent fetch.
- **`.claude/settings.local.json` in the repo** — observed but lightly inspected. It contains user-specific allow paths including an install-time absolute path (`//c/Users/HasanKhan/...`). This file is normally `.gitignore`'d; its presence in a public repo is probably unintended and mildly doxxes the install root. Flagged as a novel-axis candidate but I did not verify via git log whether it was added deliberately; a `gh api repos/.../commits?path=.claude/settings.local.json` call would resolve whether it's a recurring pattern or a one-time commit.
