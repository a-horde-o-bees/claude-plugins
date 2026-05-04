# Arcanon-hub/arcanon

## Identification

- **URL**: https://github.com/Arcanon-hub/arcanon
- **Stars**: 0
- **Last commit date**: 2026-04-20
- **Default branch**: main
- **License**: AGPL-3.0-only
- **Sample origin**: dep-management
- **One-line purpose**: Cross-repo service dependency scanner for Claude Code — maps architecture, detects drift, and syncs to Arcanon Hub

## 1. Marketplace discoverability

- **Manifest layout**: two `marketplace.json` files — `.claude-plugin/marketplace.json` at repo root (the canonical one, `claude plugin marketplace add <url>` resolves here) and a duplicate at `plugins/arcanon/.claude-plugin/marketplace.json`. Both files are byte-identical and a recent commit (2e46863, 2026-04-20, title `fix(marketplace): bump repo-root marketplace.json to 0.1.0`) suggests the duplication is intentional but drift-prone.
- **Marketplace-level metadata**: no `metadata` wrapper — top-level `name`, `owner`, `plugins`, `version` flat fields only. No `metadata.description`, `metadata.pluginRoot`, or `$schema`.
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: none on the marketplace entry itself (only `name`, `version`, `source`, `description`). Keywords live exclusively in `plugin.json` (6 keywords: arcanon, service-graph, cross-repo, dependency-mapping, architecture, drift-detection). No `category` or `tags`.
- **`$schema`**: absent on both marketplace.json files
- **Reserved-name collision**: no
- **Pitfalls observed**: The duplicated marketplace.json in `plugins/arcanon/.claude-plugin/` is structurally odd — a plugin source directory normally holds only `plugin.json`, not a marketplace manifest. The commit history shows they can drift (root had to be bumped to catch up). No discoverability metadata outside keywords — no category/tags means the plugin cannot be surfaced by category-based filters in any marketplace browser.

## 2. Plugin source binding

- **Source format(s) observed**: relative path (`"source": "./plugins/arcanon"`)
- **`strict` field**: absent on the marketplace entry (default, implicit true)
- **`skills` override on marketplace entry**: absent
- **Version authority**: both — `plugin.json` carries `"version": "0.1.0"` and the marketplace entry also carries `"version": "0.1.0"` (plus top-level `"version": "0.1.0"` on the marketplace manifest itself). Three places to keep in sync per release.
- **Pitfalls observed**: Three versions (marketplace top-level, marketplace.plugins[0].version, plugins/arcanon/.claude-plugin/plugin.json version) all carry `0.1.0` independently. The commit `fix(marketplace): bump repo-root marketplace.json to 0.1.0` is direct evidence of drift — the release commit bumped some of the three and missed the repo-root marketplace.json.

## 3. Channel distribution

- **Channel mechanism**: no split — single marketplace, users pin via git ref (branch or tag).
- **Channel-pinning artifacts**: absent. No separate stable/latest marketplaces, no dev-counter split. Tag history shows a monolithic linear release cadence under the prior `Ligamen` name (`v1.0` through `v5.7.0`), then a version reset to `0.1.0` for the Arcanon rebrand.
- **Pitfalls observed**: Version reset across rebrand — the plugin shipped v5.7.0 as Ligamen and is now `0.1.0` as Arcanon. Users who had `ligamen@5.7.0` pinned do not auto-update because the plugin name changed; this is communicated in README/CHANGELOG but not enforced in the manifest.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main. Historical tags `v1.0` through `v5.7.0` live on main; no release branches observed.
- **Release branching**: none — tag-on-main
- **Pre-release suffixes**: none observed in tag list (`v5.1`, `v5.2.1`, etc. — no `-rc`, `-beta`)
- **Dev-counter scheme**: absent — `plugin.json` versions match tagged release versions; no `0.0.z` dev-counter pattern
- **Pre-commit version bump**: no observable pre-commit hook for version bumping. The version reset from `5.7.0` (Ligamen) to `0.1.0` (Arcanon) was manual per the CHANGELOG rationale.
- **Pitfalls observed**: No release branches means release prep (doc regen, CHANGELOG finalization) happens directly on main; the most recent release commit (`release: v0.1.0 — first Arcanon public release candidate`) was followed by an immediate hotfix commit (`fix(marketplace): bump repo-root marketplace.json to 0.1.0`) because the release commit missed the root marketplace.json — a release-branch-with-prep workflow would have caught this before the tag.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — no component fields in `plugin.json` at all. Commands, skills, hooks, and MCP servers are picked up from conventional directories (`commands/`, `skills/`, `hooks/hooks.json`, `.mcp.json`).
- **Components observed**: skills (1 — `impact`), commands (9 — cross-impact, drift, export, impact, login, map, status, sync, upload), agents (0), hooks (yes, `hooks/hooks.json`), `.mcp.json` (yes, 1 stdio server `arcanon` via `scripts/mcp-wrapper.sh`), `.lsp.json` (no), monitors (no), bin (no), output-styles (no)
- **Agent frontmatter fields used**: not applicable (no `agents/` directory)
- **Agent tools syntax**: not applicable
- **Pitfalls observed**: The `skills/impact/SKILL.md` frontmatter uses the legacy ecosystem field `version: 1.0.0` — Claude Code ignores it for skill resolution, but it drifts against `plugin.json` (0.1.0). SKILL.md content also references `LIGAMEN_CHROMA_*` env vars in a block that claims to be current user-facing guidance — stale naming from the pre-rebrand codebase.

## 6. Dependency installation

- **Applicable**: yes — MCP server and worker daemon ship as Node.js code that needs `better-sqlite3` (native), `fastify`, `@modelcontextprotocol/sdk`, `chromadb`, `zod`.
- **Dep manifest format**: two manifests — `plugins/arcanon/package.json` (dev-full, with devDependencies + scripts + engines) and `plugins/arcanon/runtime-deps.json` (a sentinel-shaped file with runtime-only deps, named `@ligamen/runtime-deps` at `version: 5.7.0` — the name still carries the old Ligamen identity inside a v0.1.0 Arcanon release).
- **Install location**: `${CLAUDE_PLUGIN_ROOT}` — installs into `${_R}/node_modules` where `_R` is `CLAUDE_PLUGIN_ROOT` (or script-relative fallback). Explicitly NOT `${CLAUDE_PLUGIN_DATA}`.
- **Install script location**: `plugins/arcanon/scripts/install-deps.sh` (SessionStart hook, timeout 120). A second install path lives in `plugins/arcanon/scripts/mcp-wrapper.sh` as a "self-healing" inline fallback that runs `npm install` if `node_modules/better-sqlite3` is missing when the MCP wrapper launches (covers the first-session race where the MCP server starts before the SessionStart hook completes).
- **Change detection**: `diff -q "$MANIFEST" "$SENTINEL"` against `${CLAUDE_PLUGIN_DATA}/.arcanon-deps-installed.json` — literal file diff of `runtime-deps.json` (not a hash). Double-checked with `[ -d "${_R}/node_modules/better-sqlite3" ]` so a plugin update that wipes `node_modules` forces reinstall even if the sentinel is intact.
- **Retry-next-session invariant**: `rm -rf "${_R}/node_modules"` AND `rm -f "$SENTINEL"` on failure — explicit cleanup of both the partial install and the sentinel so next session retries clean.
- **Failure signaling**: `set -euo pipefail` + `trap 'exit 0' ERR` — non-blocking envelope. npm stdout/stderr piped through `2>&1 | head -50 >&2` so only the first 50 lines of npm output reach the terminal, and none leaks to stdout (hook JSON contract). Always exits 0.
- **Runtime variant**: Node npm. `engines: { "node": ">=20.0.0" }`. CI tests against Node 20 and 22.
- **Alternative approaches**: mcp-wrapper.sh's inline install is a secondary install path (not a fallback delegate — it's a full `npm install` with the same flags). No `npx` ad-hoc pattern; no pointer file; no PEP-723-style shebang metadata.
- **Version-mismatch handling**: `scripts/session-start.sh` sources `lib/worker-restart.sh` and calls `restart_worker_if_stale` on every UserPromptSubmit (not just SessionStart), comparing the running worker's `/api/version` against the installed `plugin.json` version and killing + restarting the worker on mismatch. MCP server has no equivalent — it respawns on each Claude Code session anyway. The dep sentinel is orthogonal: a runtime-deps.json change triggers reinstall independently of plugin version.
- **Pitfalls observed**: 
  - The script sets `--package-lock=false` to avoid writing a lock file into `CLAUDE_PLUGIN_ROOT`, but that also means install is non-reproducible — a transitive dep bump between sessions can silently land.
  - `runtime-deps.json` is not the manifest npm actually reads. `npm install --prefix "${_R}"` reads `${_R}/package.json`, not `runtime-deps.json`. The runtime-deps.json file serves only as the sentinel-diff source. This is confirmed by the planning docs (`.planning/milestones/v5.2.0-phases/059-runtime-dependency-installation/59-CONTEXT.md` explicitly: "The runtime-deps.json serves as the sentinel for diffing, not as the npm manifest"). If `package.json` and `runtime-deps.json` diverge, the diff-based idempotency lies — the sentinel might match while the actually-installed deps have drifted.
  - The `runtime-deps.json` still carries the name `@ligamen/runtime-deps` at version 5.7.0 — mid-rebrand artifact.
  - **ESM rationale for install-into-ROOT (the load-bearing decision):** Planning doc `59-CONTEXT.md` states verbatim: *"Install into `${CLAUDE_PLUGIN_ROOT}` via `npm install --prefix ${CLAUDE_PLUGIN_ROOT}` using `runtime-deps.json` as the package.json — ESM walks up directory tree to find node_modules — no NODE_PATH needed (NODE_PATH is silently ignored by ESM)."* The `worker/mcp/server.js` entry point is pure ESM (`#!/usr/bin/env node` with top-level `import` from `@modelcontextprotocol/sdk/server/mcp.js`, `better-sqlite3`, etc.) and `package.json` declares `"type": "module"`. ESM's module resolution algorithm walks up from the importing file's directory looking for `node_modules/`; installing into `CLAUDE_PLUGIN_DATA` would place `node_modules` outside that walk path (data dir is typically `~/.claude/plugins/data/<plugin>`, the plugin root is the unpacked source tree) and ESM would not find the deps, while CJS's `NODE_PATH` env-var fallback cannot be used to bridge the gap because Node's ESM loader deliberately does not consult `NODE_PATH`. Installing into the plugin root keeps `node_modules` adjacent to the `import` sites. The decision is root-caused to the ESM module-resolution algorithm, not to a preference.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — no `bin/` directory. The plugin's executable entry points are shell scripts under `scripts/` invoked by hooks and commands, and Node CLIs under `worker/cli/` invoked indirectly via `scripts/hub.sh` and similar dispatchers. Nothing is surfaced as a user-PATH binary.
- **`bin/` files**: not applicable
- **Shebang convention**: not applicable (no bin/). For reference, scripts use `#!/usr/bin/env bash`; Node CLIs in `worker/cli/` use `#!/usr/bin/env node`.
- **Runtime resolution**: not applicable
- **Venv handling (Python)**: not applicable (Node project, no Python)
- **Platform support**: not applicable
- **Permissions**: not applicable
- **SessionStart relationship**: not applicable
- **Pitfalls observed**: none (not applicable)

## 8. User configuration

- **`userConfig` present**: yes
- **Field count**: 4 (api_token, hub_url, auto_upload, project_slug)
- **`sensitive: true` usage**: correct — only `api_token` carries `"sensitive": true`, and its description says "Bearer token starting with arc_". `hub_url`, `auto_upload`, `project_slug` are non-secret and correctly omit the flag.
- **Schema richness**: typed — each field has `title`, `type` (string/boolean), `description`, `required`, and where applicable `default` (hub_url defaults to `https://api.arcanon.dev`; auto_upload defaults to `false`).
- **Reference in config substitution**: none observed. `userConfig` values are NOT consumed via `${user_config.KEY}` in the `.mcp.json` env block or in hook commands. Instead, the runtime reads credentials from three independent sources (README: "Hub credentials can live in the plugin's `userConfig`, the `ARCANON_API_KEY` environment variable, or `~/.arcanon/config.json`"), which means `userConfig` is set but not mechanically wired into substitution.
- **Pitfalls observed**: The three-way credential resolution is documented but not surfaced in the manifest — `userConfig.api_token` is declared, but no `env` block in `.mcp.json` injects it as `ARCANON_API_KEY`, so a user who sets `api_token` via userConfig only has it read if the worker's `hub-sync/auth.js` explicitly queries userConfig state. If that code path is absent or stale, userConfig becomes a no-op surface.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1 entry, matcher `Write|Edit|MultiEdit`, runs `scripts/file-guard.sh` (timeout 10). Classifies the target file against hard-block patterns (`.env`, `.env.*`, `*.pem`, `*.key`, `*credentials*`, `*secret*`, `*.lock`, `package-lock.json`, `*/node_modules/*`, `*/.venv/*`, `*/target/*`) with `exit 2` + stderr message + hookSpecificOutput `permissionDecision: "deny"`, and soft-warn patterns (`migrations/*.sql`, `migrations/*.py`, `*.pb.go`, `*_generated.*`, `*.gen.*`, `CHANGELOG.md`) with `exit 0` + `systemMessage` JSON.
- **PostToolUse hooks**: 1 entry, matcher `Write|Edit|MultiEdit`, runs two sequential commands — `scripts/format.sh` (timeout 10) then `scripts/lint.sh` (timeout 10). Non-blocking — warns on failure, doesn't block.
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: stderr human + stdout JSON — file-guard emits human message on stderr AND `hookSpecificOutput` JSON on stdout for PreToolUse deny (both forms because the stderr is for terminal display and the JSON is for the Claude Code harness's permission decision schema).
- **Failure posture**: fail-open. `scripts/file-guard.sh` has no `set -e` ("realpath can fail on files that don't exist yet; all exit codes must be explicit" per its own comment) and decides exit codes explicitly. `scripts/install-deps.sh` and `scripts/session-start.sh` use `trap 'exit 0' ERR` so any unexpected failure exits 0 silently — never blocks the tool.
- **Top-level try/catch wrapping**: not applicable (bash, not Python). Equivalent safety is the `trap 'exit 0' ERR` envelope where installed.
- **Pitfalls observed**: The dual-output contract (stderr + stdout JSON) is undocumented at the hook level — only surfaced via a comment in `file-guard.sh` referring to "validate-write.sh + hookify rule_engine.py (TEST-08 contract)" from somewhere else. `ARCANON_EXTRA_BLOCKED` is colon-separated and unquoted glob-matched with `shellcheck disable=SC2053` — a user-supplied pattern containing a colon inside a path gets silently split.

## 10. Session context loading

- **SessionStart used for context**: yes — `scripts/session-start.sh` injects a `hookSpecificOutput.additionalContext` JSON payload describing project type (via `lib/detect.sh`), the list of `/arcanon:*` commands, and worker status.
- **UserPromptSubmit for context**: yes — same script wired to UserPromptSubmit, with a deduplication guard via `/tmp/arcanon_session_${SESSION_ID}.initialized` flag file so context injection fires only once per session. The reason the hook is wired to both events is explicit in a script comment: "UserPromptSubmit fallback for upstream bug #10373."
- **`hookSpecificOutput.additionalContext` observed**: yes — exactly this schema, built with `jq -Rs .` for safe escaping.
- **SessionStart matcher**: none (fires on all sub-events — `startup|resume|clear|compact`)
- **Pitfalls observed**: The dedup flag lives in `/tmp/arcanon_session_${SESSION_ID}.initialized`. If `/tmp` is cleared mid-session (some OSes clear on reboot, tmpfs sweepers) the flag is lost and the next UserPromptSubmit re-injects context. The version-mismatch worker-restart check is explicitly exempt from the dedup guard (runs on every UserPromptSubmit so mid-session updates are caught), at the cost of one `jq + curl` per prompt. The legacy `LIGAMEN_*` env var aliases are still honored for every new `ARCANON_*` variable — `ARCANON_DISABLE_SESSION_START` falls through to `LIGAMEN_DISABLE_SESSION_START`, `ARCANON_WORKER_PORT` to `LIGAMEN_WORKER_PORT`, etc.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none (not applicable)

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace. Tag format is the flat `v5.7.0`, `v0.1.0` form.
- **Pitfalls observed**: none (not applicable)

## 13. Testing and CI

- **Test framework**: multiple — `node --test` (built-in Node test runner) for JS tests under `worker/` and `plugins/arcanon/worker/`, and `bats-core` (submodule-pinned) for shell-integration tests under `tests/*.bats`. No pytest or similar.
- **Tests location**: split — `plugins/arcanon/worker/**/*.test.js` (co-located with the code they test), `plugins/arcanon/tests/fixtures/` (fixture-only, not actual tests), and `tests/` at repo root (bats + top-level JS `tests/storage/*.test.js`, `tests/ui/*.test.js`, `tests/worker/*.test.js`).
- **Pytest config location**: not applicable
- **Python dep manifest for tests**: not applicable
- **CI present**: yes
- **CI file(s)**: `.github/workflows/ci.yml` (single workflow, 4 jobs)
- **CI triggers**: `push` on main and `pull_request` targeting main
- **CI does**: 4 jobs — `lint-manifests` (jq validates plugin.json, both marketplace.json files, hooks.json, package.json; asserts name fields equal `"arcanon"` across three manifest slots), `shell-lint` (shellcheck `--severity=error -e SC1091` on `scripts/*.sh` and `lib/*.sh`), `test-hub-sync` (npm ci + `node --test worker/hub-sync/` on Node 20 and 22), `test-bats` (npm ci + bats suite, graceful if bats submodule binary is absent)
- **Matrix**: Node 20 × Node 22 on the hub-sync job only. Single OS (ubuntu-latest). Other jobs are single-version.
- **Action pinning**: tag (`actions/checkout@v4`, `actions/setup-node@v4`) — not SHA-pinned.
- **Caching**: built-in `actions/setup-node@v4` npm cache via `cache: npm` + `cache-dependency-path: plugins/arcanon/package-lock.json`
- **Test runner invocation**: direct — `node --test worker/hub-sync/`, `tests/bats/bin/bats tests/*.bats`. `package.json` scripts use `find ... -print0 | xargs -0 node --test`. A `Makefile` target `make test` is the user-facing entry but CI invokes bats directly.
- **Pitfalls observed**: Most of the JS test suite (everything under `worker/db/`, `worker/scan/`, `worker/ui/`, `worker/mcp/`, `worker/server/` — at least ~70 test files visible in the tree) is NOT run by CI. Only `worker/hub-sync/` is actually executed on PR. This is a massive coverage gap — the bats suite is gated on `[ -x tests/bats/bin/bats ]` and falls back to "skipping" if the submodule isn't fetched (the job uses `submodules: recursive` so it *should* exist, but the graceful skip means a broken submodule won't fail CI either). CHANGELOG entry "Fixed broken npm test script that pointed at a non-existent tests/ directory" confirms the `npm test` path was recently unusable.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable — no release workflow. The `releases` endpoint returns an empty list (zero GitHub Releases published, though 20 tags exist dating back through the Ligamen era).
- **Automation shape**: not applicable (none)
- **Tag-sanity gates**: not applicable (none — release commits go straight to main, see commit history showing `release: v0.1.0 — first Arcanon public release candidate` as a direct PR merge into main)
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable — `plugins/arcanon/CHANGELOG.md` follows Keep a Changelog format but no automation consumes it.
- **Pitfalls observed**: 20 git tags, zero GitHub Releases — every tag was created without a corresponding release artifact or release notes. The CHANGELOG itself has an `[Unreleased]` section but no `[0.1.0]` section even though the v0.1.0 release already happened — the tag was cut without advancing the CHANGELOG.

## 15. Marketplace validation

- **Validation workflow present**: yes (subsumed into `ci.yml` `lint-manifests` job; no separate validation workflow)
- **Validator**: `jq` (inline shell, not a dedicated validator like bun+zod or `claude plugin validate`). Checks parseability and three name-equality assertions.
- **Trigger**: `push` (main) and `pull_request` targeting main
- **Frontmatter validation**: no — SKILL.md and command-file frontmatter is not validated; only the JSON manifests are parsed.
- **Hooks.json validation**: partial — `jq empty` parses it but does not validate the schema (no check that `timeout` is a number, no check that `command` substitutes `${CLAUDE_PLUGIN_ROOT}` correctly, etc.).
- **Pitfalls observed**: The name-equality checks cover three manifests — `plugins/arcanon/.claude-plugin/plugin.json`, `plugins/arcanon/.claude-plugin/marketplace.json`, and the `plugins[0].name` field inside that same marketplace.json — but NOT the repo-root `.claude-plugin/marketplace.json`. That is exactly the manifest that drifted in commit `2e46863` and had to be hotfixed; the CI gate missed it because the check didn't cover it.

## 16. Documentation

- **`README.md` at repo root**: present (~5.0 KB — quick start, command table, config example, ASCII architecture diagram, "Related repos" table, rebrand note)
- **`README.md` per plugin**: present at `plugins/arcanon/README.md` (~1.2 KB — mostly directs readers back to the repo-root README, plus install one-liner, command list, auto-behaviors summary, package layout table)
- **`CHANGELOG.md`**: present at `plugins/arcanon/CHANGELOG.md` — Keep a Changelog format with an `[Unreleased]` section and a prose "Notes on prior versions" section covering the v1.0–v5.7.0 Ligamen history and the rebrand rationale.
- **`architecture.md`**: present at `docs/architecture.md` (repo-root `docs/` folder) — system overview ASCII diagram, plugin structure table, worker process description, MCP server description (8 tools grouped by surface), hub sync description, storage, graph UI, scan pipeline, hook architecture. No per-plugin architecture.md.
- **`CLAUDE.md`**: absent. No operational-procedures file for agents working in the repo.
- **Community health files**: none observed (`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` absent)
- **LICENSE**: present, AGPL-3.0 (SPDX: `AGPL-3.0-only`)
- **Badges / status indicators**: observed — CI badge + AGPL badge in repo-root README
- **Pitfalls observed**: Extensive internal planning corpus at `.planning/` (260+ files across MILESTONES, ROADMAP, STATE, per-version `v1.0-phases/` through `v5.0-phases/` each with PLAN/SUMMARY/RESEARCH/VERIFICATION sub-files, plus codebase-level ARCHITECTURE/CONCERNS/CONVENTIONS/STACK/TESTING docs). This is shipped in the public repo — a significant volume of process artifacts published alongside the plugin. The planning docs still reference `plugins/ligamen/` paths throughout, so the rebrand did not propagate cleanly into the historical record.

## 17. Novel axes

- **Legacy-name back-compat discipline across every env var and data dir.** Every runtime surface honors both `ARCANON_*` and `LIGAMEN_*` spellings: `ARCANON_API_KEY`/`LIGAMEN_API_KEY`, `ARCANON_WORKER_PORT`/`LIGAMEN_WORKER_PORT`, `ARCANON_DATA_DIR`/`LIGAMEN_DATA_DIR`, `ARCANON_DISABLE_GUARD`/`LIGAMEN_DISABLE_GUARD`, `ARCANON_DISABLE_SESSION_START`/`LIGAMEN_DISABLE_SESSION_START`, `ARCANON_EXTRA_BLOCKED`/`LIGAMEN_EXTRA_BLOCKED`; data dirs `~/.arcanon/` preferred, `~/.ligamen/` honored if the new dir does not exist (resolver in `lib/data-dir.sh`); config files `arcanon.config.json` preferred, `ligamen.config.json` honored. This is an unusually thorough rebrand-compat layer — candidate for a "Identity Transition" axis in the pattern doc if other repos show it.
- **Self-healing MCP wrapper.** `scripts/mcp-wrapper.sh` independently re-runs the dep install if `node_modules/better-sqlite3` is missing when the MCP server launches. This is a SECOND install path (not a fallback delegate to install-deps.sh) covering the race where Claude Code spawns the MCP server before the SessionStart hook finishes. Novel compared to plugins that assume SessionStart-completion happens before MCP-spawn.
- **ESM-driven install-location decision.** The choice of `CLAUDE_PLUGIN_ROOT` over `CLAUDE_PLUGIN_DATA` is explicitly rationalized against ESM's module-resolution algorithm ("ESM walks up directory tree to find node_modules — no NODE_PATH needed (NODE_PATH is silently ignored by ESM)") in `.planning/milestones/v5.2.0-phases/059-runtime-dependency-installation/59-CONTEXT.md`. Most dep-management repos pick a location without making the root cause explicit — this one documents it.
- **Worker daemon with HTTP API.** The plugin runs a Fastify background process on localhost:37888 with 9 endpoints, auto-started by `scripts/worker-start.sh` from `session-start.sh`, with PID + port files in the data dir, version-mismatch auto-restart logic (`lib/worker-restart.sh`), and a graph UI served from the same process. This goes well beyond "plugin is a directory of markdown + scripts" — it's a full long-running service, with a separate MCP server process alongside. The architecture (worker + MCP server as peer processes, both reading the same SQLite via per-call DB resolution) is distinctive.
- **Dual manifest for dep install vs dep declaration.** `package.json` and `runtime-deps.json` coexist with different purposes — `package.json` is what npm actually reads (because `npm install --prefix` reads the prefix-directory's `package.json`), while `runtime-deps.json` is the sentinel-diff source for idempotency. They can drift; the convention is undocumented in the repo-root README and only surfaces in internal planning docs.
- **UserPromptSubmit dedup via /tmp flag file.** The pattern of `/tmp/arcanon_session_${SESSION_ID}.initialized` as a per-session once-only guard is a plausible convention for any hook wired to both SessionStart and UserPromptSubmit — a candidate "Context Injection Dedup" axis.
- **Shipped planning corpus.** The `.planning/` tree — MILESTONES.md, ROADMAP.md, STATE.md, per-version phase directories each with CONTEXT, PLAN, SUMMARY, VERIFICATION, RESEARCH files — is visible in the public repo. Some repos keep this private; Arcanon publishes its entire milestone-planning process. Candidate axis for "Development-Process Transparency" or similar.

## 18. Gaps

- **The `permissionDecision` output contract** (PreToolUse `permissionDecision: "deny"` with `permissionDecisionReason` on stdout + human message on stderr) is used by `file-guard.sh` but I could not confirm the exact schema against the plugin reference docs in this budget. Resolution: fetch https://code.claude.com/docs/en/plugins-reference#pretooluse-hook-schema and cross-reference.
- **Whether `userConfig` values are actually consumed by the worker.** The manifest declares 4 fields but no manifest-level substitution (`${user_config.KEY}` in `.mcp.json` env or hook command) pulls them through. The worker may or may not read them via some runtime API. Resolution: read `plugins/arcanon/worker/hub-sync/auth.js` and `plugins/arcanon/lib/config.sh` for the actual credential-resolution chain — I saw both referenced but did not fetch them.
- **Whether the `bats` submodule is present in CI runs.** The `test-bats` job has a graceful skip `if [ -x tests/bats/bin/bats ]; then ... else echo "bats binary not present — skipping"; fi`. With `submodules: recursive` on checkout, the submodule should be fetched — but a private/token-gated submodule URL could cause the checkout to succeed with a missing submodule. Resolution: check a recent CI run log via `gh api repos/Arcanon-hub/arcanon/actions/runs`.
- **Whether `runtime-deps.json` and `package.json` dependency sets are currently in sync.** They appeared equivalent at first glance (both list the same 7 core deps + same optional dep), but a deep comparison against version constraints was not done. Resolution: diff the two files' `dependencies` blocks explicitly.
- **What the `/arcanon:export` and `/arcanon:sync` commands invoke under the hood.** I read `map.md`, `status.md`, `impact.md` but not the other 6 command files. Resolution: fetch the remaining command files if the command-invocation patterns matter for another purpose.
- **Whether the repo-root marketplace.json vs plugins/arcanon/.claude-plugin/marketplace.json duplication has a documented reason.** The CI name-equality check only validates the plugins-subdir one, suggesting the root one is canonical for marketplace resolution but no internal doc explains why two copies exist. Resolution: search `.planning/` for commits/docs referencing "marketplace.json" duplication.
- **Whether GitHub Releases will be generated retroactively for v0.1.0.** The tag exists as of 2026-04-20 but no release is published. Could be intentional (plugin ecosystem does not consume GitHub Releases), could be an omission. Resolution: check issues/discussions on the repo.
