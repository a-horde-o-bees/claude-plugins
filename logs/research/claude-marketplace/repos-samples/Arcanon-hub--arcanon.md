# Sample

Mirrors of `https://github.com/Arcanon-hub/arcanon`. Cross-repo service dependency scanner for Claude Code — maps architecture, detects drift, and syncs to Arcanon Hub. AGPL-3.0-only, default branch `main`, last commit 2026-04-20, 0 stars; sample origin: dep-management.

## Marketplace manifest layout

### Duplicated marketplace manifest at root and nested

Two byte-identical `marketplace.json` copies coexist — `.claude-plugin/marketplace.json` at repo root (the canonical one resolved by `claude plugin marketplace add <url>`) and a duplicate at `plugins/arcanon/.claude-plugin/marketplace.json`. A recent commit `2e46863` (2026-04-20, `fix(marketplace): bump repo-root marketplace.json to 0.1.0`) hot-fixed drift between the two — the release commit bumped some copies and missed the repo root.

### Top-level `metadata` wrapper variants

No `metadata` wrapper. Top-level `name`, `owner`, `plugins`, `version` flat fields only. No `metadata.description`, no `metadata.pluginRoot`, no `$schema` on either marketplace.json file.

## Plugin source binding

### Relative source pointing to subdirectory

Marketplace entry uses `"source": "./plugins/arcanon"` pointing into the plugin's subdirectory. The repo carries non-plugin content (planning corpus, CHANGELOG, docs) outside the plugin tree at repo root.

### `strict` field default

`strict` is absent on the marketplace entry, taking the implicit-true default. No `skills` override on the marketplace entry.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Marketplace entry carries minimal metadata (`name`, `version`, `source`, `description`); `keywords` lives exclusively in `plugin.json` with 6 entries (arcanon, service-graph, cross-repo, dependency-mapping, architecture, drift-detection). No `category` or `tags` on the marketplace surface. No `$schema` on `plugin.json`.

## Version coordination

### Multi-site sprawl (5+ locations)

Three independent `0.1.0` carriers: marketplace top-level `version`, marketplace `plugins[0].version`, and `plugins/arcanon/.claude-plugin/plugin.json` `version`. Plus `runtime-deps.json` carries a stale name `@ligamen/runtime-deps` at `version: 5.7.0` from before the rebrand. SKILL.md frontmatter carries `version: 1.0.0` (legacy ecosystem field that Claude Code ignores, but drifts independently). Commit `2e46863` is direct evidence of drift — the release commit bumped some carriers and missed the repo-root marketplace.json.

## Channel distribution

### Single channel with version-reset across rebrand

Single marketplace; users pin via git ref. Tag history shows a monolithic linear release cadence under the prior `Ligamen` name (`v1.0` through `v5.7.0`), then a version reset to `0.1.0` for the Arcanon rebrand. Users pinned at `ligamen@5.7.0` do not auto-update because the plugin name changed; the rebrand is communicated via README/CHANGELOG only, not enforced in the manifest.

## Tag and release lifecycle

### Tag-on-main, single branch

Twenty historical tags `v1.0` through `v5.7.0` (Ligamen era) plus `v0.1.0` (Arcanon era) all sit on main's linear history; no `release/*` branches. The most recent release commit `release: v0.1.0 — first Arcanon public release candidate` was followed immediately by hotfix commit `fix(marketplace): bump repo-root marketplace.json to 0.1.0` — the release commit missed the root marketplace.json.

## Plugin-component registration

### Default convention discovery

No component fields in `plugin.json`. Commands, skills, hooks, and MCP servers are picked up from conventional directories (`commands/`, `skills/`, `hooks/hooks.json`, `.mcp.json`).

### `.mcp.json` sibling file

Single stdio MCP server `arcanon` declared in `.mcp.json`, launched via `scripts/mcp-wrapper.sh` (rather than inlined in `plugin.json`).

## Component composition

### Skills (universal)

One skill: `skills/impact/SKILL.md`.

### Commands

Nine commands: cross-impact, drift, export, impact, login, map, status, sync, upload.

### Hooks

Hooks declared at `hooks/hooks.json` covering PreToolUse, PostToolUse, SessionStart, and UserPromptSubmit events.

### MCP servers

One stdio server `arcanon` via `scripts/mcp-wrapper.sh`.

## Plugin-component placement

### Inside plugin directory

All components live under `plugins/arcanon/` (commands, skills, hooks, scripts, worker, config, lib).

## Skill authoring conventions

### Standard frontmatter

`skills/impact/SKILL.md` uses standard frontmatter. Frontmatter also carries the legacy ecosystem field `version: 1.0.0` which Claude Code ignores for skill resolution.

## Server runtime (MCP)

### Local venv built by SessionStart hook

The MCP server `arcanon` is a Node.js stdio server launched via `scripts/mcp-wrapper.sh`. Dependencies (`better-sqlite3`, `fastify`, `@modelcontextprotocol/sdk`, `chromadb`, `zod`) install into `${CLAUDE_PLUGIN_ROOT}/node_modules` via the SessionStart hook `scripts/install-deps.sh` (npm install in the plugin root, not data dir). A self-healing fallback inside `mcp-wrapper.sh` re-runs `npm install` if `node_modules/better-sqlite3` is missing when the wrapper launches — covers the race where Claude Code spawns the MCP server before SessionStart finishes.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory. Executable entry points are shell scripts under `scripts/` invoked by hooks and commands, plus Node CLIs under `worker/cli/` invoked indirectly via `scripts/hub.sh` and similar dispatchers. Nothing surfaced as a user-PATH binary. Scripts use `#!/usr/bin/env bash`; Node CLIs in `worker/cli/` use `#!/usr/bin/env node`.

## Dependency installation

### SessionStart-driven Python venv with hash gating

Node-based equivalent of the hash-gated install pattern. SessionStart hook `scripts/install-deps.sh` (timeout 120) runs `npm install --prefix "${_R}"` with `--package-lock=false` (avoids writing a lock file into `CLAUDE_PLUGIN_ROOT`, but also makes installs non-reproducible — a transitive dep bump between sessions can land silently). Install location is `${CLAUDE_PLUGIN_ROOT}/node_modules`, explicitly NOT `${CLAUDE_PLUGIN_DATA}`. The choice is rationalized in planning doc `59-CONTEXT.md`: the worker entry point `worker/mcp/server.js` is pure ESM (`#!/usr/bin/env node`, top-level `import` from `@modelcontextprotocol/sdk/server/mcp.js`, `better-sqlite3`, etc.) and `package.json` declares `"type": "module"`; ESM's module-resolution algorithm walks up from the importing file's directory looking for `node_modules/`, so installing into `CLAUDE_PLUGIN_DATA` would place `node_modules` outside the walk path and ESM cannot bridge via `NODE_PATH` (deliberately ignored by ESM). `engines: { "node": ">=20.0.0" }`. CI tests against Node 20 and 22.

### Self-healing inline install at MCP launch

`scripts/mcp-wrapper.sh` independently re-runs the dep install if `node_modules/better-sqlite3` is missing when the MCP server launches. A SECOND install path (not a fallback delegate) covering the race where Claude Code spawns the MCP server before the SessionStart hook finishes.

## Install change detection

### Diff-based byte comparison of manifest

Change detection runs `diff -q "$MANIFEST" "$SENTINEL"` against `${CLAUDE_PLUGIN_DATA}/.arcanon-deps-installed.json` — literal file diff of `runtime-deps.json` (not a hash). Caveat: `runtime-deps.json` is not the manifest npm actually reads. `npm install --prefix "${_R}"` reads `${_R}/package.json`; `runtime-deps.json` serves only as the sentinel-diff source (per planning doc `59-CONTEXT.md`: "The runtime-deps.json serves as the sentinel for diffing, not as the npm manifest"). If `package.json` and `runtime-deps.json` diverge, the diff-based idempotency lies — the sentinel can match while installed deps drift.

### Three-pronged OR (path drift + manifest diff + venv health)

Diff is double-checked with `[ -d "${_R}/node_modules/better-sqlite3" ]` so a plugin update that wipes `node_modules` forces reinstall even if the sentinel is intact.

## Install trigger and lifecycle

### SessionStart direct invocation

`scripts/install-deps.sh` runs as a SessionStart hook with timeout 120.

## Install failure posture

### `rm` stamp on failure (retry next session)

On failure: `rm -rf "${_R}/node_modules"` AND `rm -f "$SENTINEL"` — explicit cleanup of both partial install and sentinel so next session retries clean.

### `set -euo pipefail` + `trap 'exit 0' ERR` — non-blocking with cleanup

`set -euo pipefail` plus `trap 'exit 0' ERR` envelope. npm stdout/stderr piped through `2>&1 | head -50 >&2` so only the first 50 lines of npm output reach the terminal, none leaks to stdout (preserving hook JSON contract). Always exits 0.

## User configuration and authentication

### Typed `userConfig` schema with rich field types

`userConfig` declares 4 fields: `api_token` (string, `sensitive: true`, description "Bearer token starting with arc_"), `hub_url` (string, default `https://api.arcanon.dev`), `auto_upload` (boolean, default false), `project_slug` (string). Each field has `title`, `type`, `description`, `required`, and where applicable `default`.

### `userConfig` declared but not wired through manifest substitution

No `${user_config.KEY}` substitution observed — `userConfig` values are NOT consumed via substitution in `.mcp.json` env block or hook commands. Runtime reads credentials from three independent sources per README: "Hub credentials can live in the plugin's `userConfig`, the `ARCANON_API_KEY` environment variable, or `~/.arcanon/config.json`."

### `sensitive: true` flag absent on secret fields

Correct usage of `sensitive: true` here — only `api_token` carries the flag (its description names it as a Bearer token); `hub_url`, `auto_upload`, `project_slug` are non-secret and correctly omit it.

### Env-var fallback alongside userConfig

Runtime accepts `ARCANON_API_KEY` env var as one of three credential sources, alongside `userConfig.api_token` and `~/.arcanon/config.json`.

## Session context loading

### `additionalContext` payload at SessionStart

`scripts/session-start.sh` injects a `hookSpecificOutput.additionalContext` JSON payload describing project type (via `lib/detect.sh`), the list of `/arcanon:*` commands, and worker status. Built with `jq -Rs .` for safe escaping. Wired to both SessionStart and UserPromptSubmit (the latter as fallback for upstream bug #10373 per script comment), with `/tmp/arcanon_session_${SESSION_ID}.initialized` flag file as once-per-session deduplication. Companion logic re-runs on every UserPromptSubmit (exempt from the dedup guard) for the version-mismatch worker-restart check at the cost of one `jq + curl` per prompt. If `/tmp` is cleared mid-session (tmpfs sweepers, OS reboot), the flag is lost and next UserPromptSubmit re-injects context.

### Per-prompt version-mismatch / worker-restart check

`scripts/session-start.sh` sources `lib/worker-restart.sh` and calls `restart_worker_if_stale` on every UserPromptSubmit, comparing the running worker's `/api/version` against the installed `plugin.json` version and killing/restarting the worker on mismatch.

## SessionStart matcher scope

### Empty matcher (all sub-events)

No matcher set on SessionStart; fires on `startup|resume|clear|compact`.

## Tool-use enforcement

### Block-list with hard deny + soft warn classes

PreToolUse hook with matcher `Write|Edit|MultiEdit` runs `scripts/file-guard.sh` (timeout 10). Hard-block patterns (`.env`, `.env.*`, `*.pem`, `*.key`, `*credentials*`, `*secret*`, `*.lock`, `package-lock.json`, `*/node_modules/*`, `*/.venv/*`, `*/target/*`) emit `exit 2` + stderr message + stdout `hookSpecificOutput.permissionDecision: "deny"`. Soft-warn patterns (`migrations/*.sql`, `migrations/*.py`, `*.pb.go`, `*_generated.*`, `*.gen.*`, `CHANGELOG.md`) emit `exit 0` + `systemMessage` JSON. User-extensible block list via `ARCANON_EXTRA_BLOCKED` env var (colon-separated; unquoted glob match with `shellcheck disable=SC2053` — a user pattern containing a colon inside a path gets silently split).

### Format-then-lint PostToolUse (non-blocking)

PostToolUse hook with matcher `Write|Edit|MultiEdit` runs `scripts/format.sh` (timeout 10) then `scripts/lint.sh` (timeout 10) sequentially. Non-blocking — warns on failure, doesn't block.

## Hook output contract

### Stderr for human display + stdout JSON for harness

`file-guard.sh` emits human message on stderr AND `hookSpecificOutput` JSON on stdout for PreToolUse deny — stderr for terminal display, stdout JSON for harness's permission-decision schema.

## Hook failure posture

### Fail-open envelope via `trap 'exit 0' ERR`

`scripts/install-deps.sh` and `scripts/session-start.sh` use `trap 'exit 0' ERR` so any unexpected failure exits 0 silently — never blocks the tool. `scripts/file-guard.sh` has no `set -e` (per its own comment "realpath can fail on files that don't exist yet; all exit codes must be explicit") and decides exit codes explicitly.

## Hook handler runtime

### Bash scripts at conventional path

Hook handlers are bash scripts under `plugins/arcanon/scripts/`.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code (scripts, worker, lib) plus `node_modules/` (the ESM-driven exception, per Dependency installation) live under `${CLAUDE_PLUGIN_ROOT}`. Sentinel `.arcanon-deps-installed.json`, worker PID/port files, and SQLite DB live under `${CLAUDE_PLUGIN_DATA}`.

## State persistence

### Plugin-chosen `$HOME/.<plugin>/` with override env var

Hub credentials and config files default to `~/.arcanon/` with `ARCANON_DATA_DIR` env var override. Resolver in `lib/data-dir.sh` falls back to `~/.ligamen/` if the new dir does not exist (legacy-name back-compat).

### Sidecar port-discovery file

Worker daemon writes PID + port files into the data dir for cross-process discovery.

## Sidecar daemon and IPC lifecycle

### Local Fastify HTTP daemon on a fixed port

Worker daemon is a Fastify background process on localhost:37888 with 9 endpoints, auto-started by `scripts/worker-start.sh` from `session-start.sh`. PID + port files in the data dir; version-mismatch auto-restart logic in `lib/worker-restart.sh`. Graph UI served from the same process. The architecture is worker + MCP server as peer processes, both reading the same SQLite via per-call DB resolution.

## Testing

### Multi-runner — `node --test` + bats

`node --test` (built-in Node test runner) for JS tests under `worker/` and `plugins/arcanon/worker/`, plus `bats-core` (submodule-pinned) for shell-integration tests under `tests/*.bats`. No pytest. Tests split across `plugins/arcanon/worker/**/*.test.js` (co-located), `plugins/arcanon/tests/fixtures/`, and `tests/` at repo root (bats + top-level JS `tests/storage/*.test.js`, `tests/ui/*.test.js`, `tests/worker/*.test.js`).

## CI workflow shape

### Single workflow, sparse coverage

`.github/workflows/ci.yml` (single workflow, 4 jobs) on `push` to main and `pull_request` targeting main. Jobs: `lint-manifests` (jq parses plugin.json, both marketplace.json files, hooks.json, package.json; asserts name fields equal `"arcanon"` across three manifest slots), `shell-lint` (shellcheck `--severity=error -e SC1091` on `scripts/*.sh` and `lib/*.sh`), `test-hub-sync` (npm ci + `node --test worker/hub-sync/` on Node 20 and 22), `test-bats` (npm ci + bats suite, gated on `[ -x tests/bats/bin/bats ]` with graceful skip if submodule binary absent). Most of the JS test suite (~70 test files under `worker/db/`, `worker/scan/`, `worker/ui/`, `worker/mcp/`, `worker/server/`) is NOT run by CI — only `worker/hub-sync/` is executed on PR. Single OS (ubuntu-latest); matrix only on the hub-sync job.

### Action-pinning conventions

Tag-pinned (`actions/checkout@v4`, `actions/setup-node@v4`); not SHA-pinned. Built-in `actions/setup-node@v4` npm cache via `cache: npm` + `cache-dependency-path: plugins/arcanon/package-lock.json`.

## Marketplace validation

### `jq` parseability + name-equality assertions

Subsumed into `ci.yml`'s `lint-manifests` job (no separate validation workflow). `jq empty` parses each manifest; name-equality assertions cover three manifests — `plugins/arcanon/.claude-plugin/plugin.json`, `plugins/arcanon/.claude-plugin/marketplace.json`, and the `plugins[0].name` field inside that same marketplace.json — but NOT the repo-root `.claude-plugin/marketplace.json`. That is exactly the manifest that drifted in commit `2e46863` and had to be hotfixed; the CI gate missed it because the check didn't cover it. SKILL.md and command-file frontmatter is not validated; `hooks.json` is parsed but not schema-validated (no check that `timeout` is a number, no check that `command` substitutes `${CLAUDE_PLUGIN_ROOT}` correctly).

## Release automation

### No release automation / manual

No `release.yml` or equivalent. Twenty git tags exist dating back through the Ligamen era; zero GitHub Releases published. Release commits go straight to main (e.g. `release: v0.1.0 — first Arcanon public release candidate` as a direct PR merge into main). `plugins/arcanon/CHANGELOG.md` follows Keep a Changelog format with an `[Unreleased]` section but no `[0.1.0]` section even though the v0.1.0 release already happened — the tag was cut without advancing the CHANGELOG.

## Documentation surface

### README + ARCHITECTURE + CLAUDE-as-pointer

`README.md` at repo root (~5.0 KB): quick start, command table, config example, ASCII architecture diagram, "Related repos" table, rebrand note. `plugins/arcanon/README.md` (~1.2 KB) directs readers back to repo-root README plus install one-liner, command list, auto-behaviors summary, package layout table. `docs/architecture.md` (repo-root `docs/`) holds system overview ASCII diagram, plugin structure table, worker process description, MCP server description (8 tools grouped by surface), hub sync description, storage, graph UI, scan pipeline, hook architecture. No per-plugin `architecture.md`. No `CLAUDE.md`.

### CHANGELOG depth as documentation

`plugins/arcanon/CHANGELOG.md` is Keep-a-Changelog format with `[Unreleased]` section plus a prose "Notes on prior versions" section covering v1.0–v5.7.0 Ligamen history and the rebrand rationale.

### Shipped planning corpus visible in public repo

Extensive `.planning/` tree (260+ files): MILESTONES, ROADMAP, STATE, per-version `v1.0-phases/` through `v5.0-phases/` each with PLAN/SUMMARY/RESEARCH/VERIFICATION sub-files, plus codebase-level ARCHITECTURE/CONCERNS/CONVENTIONS/STACK/TESTING docs. Planning docs still reference `plugins/ligamen/` paths throughout — the rebrand did not propagate into the historical record.

## License declaration

### Single repo-level license

`LICENSE` file present at repo root (AGPL-3.0). SPDX identifier `AGPL-3.0-only` declared in manifests.

### AGPL-3.0 with embedded badge

AGPL badge in repo-root README alongside CI badge.

## Community health files

### Community health files absent

No `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`.

## Novel and cross-cutting concerns

### MCP server reads hook-authored artifact

MCP server and worker daemon are peer processes both reading the same SQLite (per-call DB resolution); the worker (via `scripts/worker-start.sh` from `session-start.sh`) and the MCP server (via `scripts/mcp-wrapper.sh`) coordinate through the shared SQLite plus PID/port discovery files in the data dir. Cross-component data flow without RPC or shared-memory coupling.
