# Sample

Mirrors of `https://github.com/Lykhoyda/rn-dev-agent`. Single-plugin Claude Code marketplace turning Claude into a React Native development partner that drives iOS/Android simulators via CDP — testing app navigation, UI verification, and internal state. MIT-licensed; default branch `main`; HEAD `aa3faf2d` at 2026-04-20.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` co-located with `.claude-plugin/plugin.json` at repo root. Marketplace name and plugin name are both `rn-dev-agent`, producing the install command `/plugin install rn-dev-agent@Lykhoyda-rn-dev-agent`. Top-level `description` field on the marketplace object (no `metadata.{}` wrapper); `metadata.pluginRoot` absent because the plugin lives at repo root with `source: "./"`. `$schema` declared on `marketplace.json` (`https://anthropic.com/claude-code/marketplace.schema.json`); absent on `plugin.json`. Marketplace `plugins[].description` duplicates `plugin.json.description` verbatim — a hand-sync point.

### `$schema` declaration on marketplace.json

`marketplace.json` declares `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"`. No CI step actively validates against it.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`source: "./"` on the marketplace entry; the plugin is the repo. `strict` field absent (default applies). `skills` override on the marketplace entry absent — skills are declared only via `plugin.json` discovery.

## Per-plugin discoverability metadata

### Cross-file category drift

Marketplace entry's `category` is `"mobile-development"` while `plugin.json.category` is `"development"` — no sync mechanism guards this. `plugin.json` carries `keywords: ["react-native", "expo", "testing", "debugging", "simulator", "emulator", "cdp", "maestro"]`. No `tags`. Unlike `version` (guarded by `sync-versions.sh`), `category` has no enforcement and the drift is undetected.

### `$schema` absence on per-plugin manifests

`plugin.json` carries no `$schema` URL.

## Version coordination

### Independent semver streams (sub-package versioning)

Three semver tracks coexist: (1) `plugin.json.version` (currently `0.32.0`, user-facing), (2) `marketplace.json.plugins[0].version` (synced from 1 by `scripts/sync-versions.sh`), (3) `scripts/cdp-bridge/package.json.version` (currently `0.27.0`, MCP server internal, intentionally outside the synchronized set). CHANGELOG reconciles them explicitly ("MCP server bumped to 0.20.0"). The MCP server is required to read its version from `package.json` at module load — `sync-versions.sh` regex-scans `scripts/cdp-bridge/src/` for hardcoded `version: 'x.y.z'` literals as a B110 regression guard.

### Pre-commit hook auto-sync (consistency, not increment)

`.githooks/pre-commit` invokes `scripts/sync-versions.sh` whenever `plugin.json` or `marketplace.json` is in the staged diff, failing the commit on version mismatch. Version changes themselves are manual; the hook only enforces consistency.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Single marketplace on `main` with tagged releases. Users install via `/plugin marketplace add Lykhoyda/rn-dev-agent` + `/plugin install rn-dev-agent@Lykhoyda-rn-dev-agent`. No stable/latest split, no dev-counter. The plugin can ship via marketplace update independent of GitHub Releases — `plugin.json.version` (0.32.0) is 7 minor bumps ahead of the most recent tag (`v0.25.0`); only 4 tags exist (`v0.15.1`, `v0.20.0`, `v0.23.0`, `v0.25.0`) against ~32 plugin versions.

## Tag and release lifecycle

### Tag-on-main, single branch

Tags `v0.15.1`, `v0.20.0`, `v0.23.0`, `v0.25.0` sit on `main`'s linear history. Feature work happens on short-lived `feat/*`, `fix/*`, `enhance/*` branches merged back to main. No `release/*` branches. CHANGELOG documents "Skipped 0.24.0 because … jumped from 0.23.0 → 0.24.0 (PR #32) → 0.25.0 (PR #33) on main without a public release at the intermediate step" — not every on-main bump produces a release or a tag.

## Plugin-component registration

### Explicit per-component path arrays

`plugin.json` declares skills, agents, commands by explicit paths. `mcpServers` is inline — a single `cdp` server defined in `plugin.json.mcpServers` rather than in a sibling `.mcp.json`. `hooks` registered via `hooks/hooks.json` covering 5 event types (PostToolUse, PostToolUseFailure, SubagentStart, CwdChanged, SessionStart).

### Inline `mcpServers` definition in `plugin.json`

The single `cdp` MCP server lives inline in `plugin.json.mcpServers`. The launch command is `${CLAUDE_PLUGIN_ROOT}/scripts/cdp-bridge/dist/index.js` — no `${user_config.KEY}` substitution; userConfig values reach the server as `CLAUDE_PLUGIN_OPTION_<KEY>` env vars implicitly.

## Component composition

### Skills (universal)

7 skills at `skills/<name>/SKILL.md`: `using-rn-dev-agent`, `rn-feature-development`, `rn-device-control`, `rn-testing`, `rn-debugging`, `rn-best-practices`, `rn-setup`. The `rn-best-practices` skill ships `references/` with 60+ reference markdown files.

### Commands

13 command markdown files under `commands/`.

### Agents

5 agents under `agents/` — `rn-tester`, `rn-debugger`, `rn-code-architect`, `rn-code-explorer`, `rn-code-reviewer`.

### Hooks

`hooks/hooks.json` registers 5 event types. Detailed under *Tool-use enforcement* and *Session context loading*.

### MCP servers

Single `cdp` MCP server registered inline in `plugin.json.mcpServers` (not via sibling `.mcp.json`). Server source under `scripts/cdp-bridge/`.

### bin

7 shell wrappers committed as git symlinks (mode 120000) into `../scripts/`. Detailed under *Bin entry mechanism*.

## Skill authoring conventions

### `user-invocable: false`

The `rn-best-practices` skill carries `user-invocable: false` in its frontmatter — agent-only, invoked via `skills:` frontmatter on agents (`rn-testing, rn-best-practices`), not surfaced as a user-facing slash command.

### Standard frontmatter

Other skills (using-rn-dev-agent, rn-feature-development, rn-device-control, rn-testing, rn-debugging, rn-setup) carry standard `name`, `description`, `argument-hint`, `allowed-tools` frontmatter.

## Agent declaration conventions

### Standard fields plus model / color

Agents declare `name`, `description` (multi-line YAML literal block scalar with embedded `<example>` / `<commentary>` XML blocks and "Triggers:" keyword list), `tools` (per-agent comma-separated list), `model` (`sonnet` for most; `opus` for `rn-code-architect`), and `color` (green/red/yellow/magenta).

### `model` + `effort` + `maxTurns` for cost control

`rn-code-architect` declares `effort: high` alongside `model: opus`. Other agents do not set `effort`. `maxTurns` is not used.

### Rich behavior fields (background, isolation, memory)

`rn-tester` and `rn-debugger` declare `memory: true`. The "memory" surface is implemented by an Experience Engine — initialized into `$HOME/.claude/rn-agent/` by `ensure-experience-engine.sh` (telemetry directories, candidates directories, an `experience.md` scratchpad). Other agents do not carry `memory`. No `background` or `isolation` declared on any agent.

### Plain tool-name list

`tools:` is comma-separated plain tool names (`Bash, Read, Write, Edit, Glob, Grep` or `Glob, Grep, LS, Read`). No permission-rule syntax (`Bash(uv run *)`-style).

### `skills:` array delegating to skill packages

Agents declare `skills: rn-testing, rn-best-practices` by bare in-plugin name. Cross-plugin reuse would need qualification.

### Defensive prompt directives in agent body

The `rn-tester` and `rn-debugger` agent descriptions contain "PARENT-SESSION-ONLY" warnings: "do NOT spawn via Task tool — MCP stdio doesn't propagate to subprocesses (GH #31)." Surfaces an MCP-inheritance gotcha as inline frontmatter guidance rather than as a schema constraint.

### Custom agent frontmatter extensions

Agents combine standard fields with non-canonical extensions (`memory: true`, `effort: high`) in addition to `model` / `color` / `skills`.

## Server runtime (MCP)

### Local venv built by SessionStart hook

The MCP server is the in-repo Node code at `scripts/cdp-bridge/dist/index.js`, launched by Claude Code via the inline `mcpServers` definition in `plugin.json`. SessionStart's `detect-rn-project.sh` calls `scripts/ensure-cdp-deps.sh` to install the Node deps that the MCP server requires before launch. Node `>= 22 LTS` required.

## Bin entry mechanism

### Git-symlink bin wrappers (mode 120000)

7 files committed as git symlinks pointing to `../scripts/*.sh`: `rn-collect-feedback` → `collect-feedback.sh` (sanitized env + telemetry bundle for bug reports), `rn-eas-artifact` → `eas_resolve_artifact.sh`, `rn-ensure-running` → `expo_ensure_running.sh`, `rn-generate-pr-body` → `generate_pr_body.sh`, `rn-record-proof` → `record_proof.sh`, `rn-snapshot` → `snapshot_state.sh`, `rn-verify` → `verify.sh`. Target scripts use `PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"` — `dirname "$0"` resolves through the symlink to the real script path. `bin/` entries themselves carry no shebangs (resolved by the kernel at exec time); target scripts use `#!/usr/bin/env bash`. Real scripts in `scripts/` are mostly 100755, with one observed exception: `scripts/snapshot_state.sh` is 100644 (not executable), so direct exec via `bin/rn-snapshot` fails on systems that enforce the exec bit. Internal callers (`hooks/detect-rn-project.sh`) invoke the real script names directly (`scripts/ensure-cdp-deps.sh`), not via the bin alias. Windows-native git checkouts without `core.symlinks=true` materialize symlinks as plain text files containing `../scripts/<name>.sh`, silently breaking the bin layer — moot here because the iOS/Android simulator tooling is nix-only.

## Dependency installation

### Version-stamped persistent install with back-symlink

`scripts/cdp-bridge/` ships a Node MCP server. `node_modules` installs into `${CLAUDE_PLUGIN_DATA}/cdp-node_modules/node_modules/` with `ln -sfn $CLAUDE_PLUGIN_DATA/cdp-node_modules/node_modules` symlinked back into `${CLAUDE_PLUGIN_ROOT}/scripts/cdp-bridge/node_modules` so relative `require` resolves at the in-tree path. Stamp at `$CLAUDE_PLUGIN_DATA/cdp-node_modules/.version-stamp` carries the CDP bridge `package.json` version (`CURRENT_VERSION`); reinstall fires when stamp absent OR stamp ≠ current version. Pre-scans for a dangling symlink from a previous persistent install (`[ -L "$CDP_DIR/node_modules" ] && [ ! -d "$CDP_DIR/node_modules" ] && rm -f`) and cleans it before falling back to local install. Stamp-flip-flop guard: skip the persistent path when Node is unavailable (so `CURRENT_VERSION === "unknown"` cannot be written as a stamp). Solves "plugin cache wiped on update, 300+ MB node_modules shouldn't reinstall every version bump." Fallback when `CLAUDE_PLUGIN_DATA` is unset or persistent install fails: install directly into `${CLAUDE_PLUGIN_ROOT}/scripts/cdp-bridge/node_modules`. Install command is `npm install --production --ignore-scripts --silent` (no postinstall scripts from transitive deps).

### External CLI auto-install via vendor scripts

System-level CLIs are installed by `ensure-*.sh` script family from SessionStart: `ensure-agent-device.sh` (`npm install -g agent-device` global), `ensure-maestro-runner.sh` (`curl -fsSL https://open.devicelab.dev/install/maestro-runner | bash` vendor install script, with `brew install maestro` printed as fallback), `ensure-ffmpeg.sh`, `ensure-android-ready.sh`, `ensure-experience-engine.sh`. Tools land where their installers put them (`~/.maestro-runner/bin/`, npm global prefix). `set -euo pipefail` is used in some ensure-* scripts (maestro-runner, agent-device); `ensure-cdp-deps.sh` omits it to allow graceful fallback. Node major-version parity check runs separately: odd-numbered Node (v25) warns "not an LTS release"; Node < 22 warns "below the minimum."

### Plugin-upgrade awareness via tmp-file stamp

`hooks/detect-rn-project.sh` writes `${TMPDIR:-/tmp}/rn-dev-agent-last-version`, compares next session, and emits "NOTICE: rn-dev-agent upgraded from vX to vY. If MCP tools fail, restart Claude Code to reinitialize MCP servers" (B76/GH #30). Survives a boot cycle but resets on macOS reboot — accepted trade-off.

## Install change detection

### Plugin-version stamp file

The CDP-bridge `package.json` version (`CURRENT_VERSION`) is the stamp key for the persistent `node_modules` install. Any sub-package version bump triggers full reinstall.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks/detect-rn-project.sh` (registered as the SessionStart hook with matcher `*`) calls `scripts/ensure-cdp-deps.sh` and the other `ensure-*.sh` scripts synchronously on each session start.

## Install failure posture

### Multi-layer fail-open with stderr advisory

`ensure-cdp-deps.sh` returns 1 on failure; the calling hook swallows it with a stderr human-readable warning (`WARNING: CDP bridge deps failed. Run: cd ${PLUGIN_ROOT}/scripts/cdp-bridge && npm install`) and exits 0. Warnings are printed before the session banner ("so they're visible"). No `rm` on failure — the next session's `needs_install` recomputes from stamp mismatch or missing directory.

## User configuration and authentication

### Native `userConfig` with `${user_config.KEY}` substitution

`userConfig` declares 3 fields in `plugin.json`: `RN_METRO_PORT`, `RN_PREFERRED_PLATFORM`, `RN_DEV_AGENT_LOG_LEVEL`. Each carries `title`, `description`, `type: "string"`, `required: false`. No `default`, no `enum`, no validation pattern — descriptions carry enum hints in prose ("auto, ios, or android"; "warn, info, debug, or error"). None carry `sensitive: true` (none are secrets — port, platform, log level). No `${user_config.KEY}` substitution appears in `plugin.json` — values reach the MCP server through Claude Code's implicit translation into `CLAUDE_PLUGIN_OPTION_<KEY>` env vars consumed by `os.environ.get(...)`-equivalent reads in the server's TypeScript (`project-config.ts` / `cdp-client.ts`).

### Schema richness — minimal vs. validated

The 3 `userConfig` fields carry `title`, `description`, `type: "string"`, `required: false` only. No `default`, no `enum`, no validation regex.

## Session context loading

### Plain-stdout context banner

`detect-rn-project.sh` emits a ~40-line heredoc banner via plain `echo` listing all MCP tools, commands, and prerequisites when it detects an RN project. Also warns about Node.js LTS status, runs dep-install scripts, and surfaces plugin-upgrade notices. Multi-purpose: context loader, dep installer, version warner. The banner hard-codes "The rn-dev-agent plugin is active with 51 MCP tools" — drifts from README's "53 MCP tools" claim and from `collect-feedback.sh`'s `grep -c "trackedTool(" index.ts` over the actual TypeScript source.

## SessionStart matcher scope

### Empty matcher (all sub-events)

SessionStart matcher is `"*"` — fires on `startup`, `clear`, `compact`, `resume`. The ~40-line banner re-injects on every sub-event. No matcher narrowing.

## Tool-use enforcement

### Post-edit health-check (PostToolUse on `Edit|MultiEdit|Write`)

Single PostToolUse matcher `"Edit|MultiEdit|Write"` runs `${CLAUDE_PLUGIN_ROOT}/hooks/post-edit-health-check.sh` with `timeout: 10`. Performs a post-edit compilation/crash check on the live simulator via CDP. Last-write-wins debounce ("only the most recent edit triggers the check"). Silent-skip when no active CDP session, file type mismatch, or target file is a test/config file. Documented exit-code convention: `0 = success, 1 = error logged non-blocking, 2 = block operation (not used here)`. Output is plain stdout text the agent reads, not structured JSON. Stdin parsed via `jq -r '.tool_input.file_path'`. `set -uo pipefail` is used (not `-e`); per-line `|| true` / `2>/dev/null` suppress errors at specific sites; each hook has skip-path block exiting 0 early on missing state.

### `PostToolUseFailure` post-hoc diagnostic hook

`tool-use-failure.sh` registered with matcher `"mcp__*rn-dev-agent*"` — fires on failures of MCP tools in the rn-dev-agent namespace. Inspects active-flag file, Metro port, simctl boot state, adb device presence, and emits a tailored diagnostic ("CDP session is not active. Metro is not running on port X. Try: cdp_status to reconnect.") that the agent reads as plain stdout.

### `SubagentStart` context injection

`subagent-start.sh` (matcher `*`) injects "CDP bridge is connected (platform: X, port: Y)" into every subagent spawn so the subagent does not need to re-probe. Paired with the `rn-tester` / `rn-debugger` "PARENT-SESSION-ONLY" frontmatter warnings — documents which agents do vs don't work under Task-tool spawning.

### `CwdChanged` re-detection hook

`cwd-changed.sh` re-runs RN-project detection when the user changes working directory. Emits "CDP tools may not work here" when the new cwd isn't an RN project.

## State persistence

### Skill-side experience seeds with stateful HOME directory

Seed YAML files ship in `seed-experience/`: `common-failures.yaml`, `expo-gotchas.yaml`, `platform-quirks.yaml`, `recovery-playbook.yaml`. SessionStart's `ensure-experience-engine.sh` initializes `$HOME/.claude/rn-agent/` with telemetry + candidates directories and an `experience.md` scratchpad. Combines plugin-shipped seed data with user-side mutable state outside `${CLAUDE_PLUGIN_DATA}`.

## Testing

### Node `node:test` with multi-job CI

Test framework is built-in `node --test`. 272 tests as of v0.25.0 per CHANGELOG (249 at tag time). Tests under `scripts/cdp-bridge/test/unit/` and `scripts/cdp-bridge/test/integration/` (nested under the MCP server subpackage, not repo root). Fixtures under `test/fixtures/`; helpers under `test/helpers/` (`fake-cdp-server.js`, `mock-cdp-client.js`, `result-helpers.js`). Tests run as `node --test 'test/unit/*.test.js'`. `npm test` runs `npm run build && node --test 'test/unit/*.test.js'`. Integration tests cover only CDP client lifecycle (`test/integration/cdp-client-lifecycle.test.js`); full simulator-driven E2E runs on the maintainer's dev box, not in CI.

## CI workflow shape

### Two-job workflow — build-and-test plus validate-plugin

`.github/workflows/ci.yml` triggers on `push: branches: [main]` and `pull_request: branches: [main]` (no `tags: v*`). Runs TypeScript build (`npm run build`), unit tests, integration tests, and a separate parallel `version-sync` job running `bash scripts/sync-versions.sh`. Single Node 22, ubuntu-latest — no matrix. Action pinning by tag (`actions/checkout@v4`, `actions/setup-node@v4`, `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4`); no SHA pinning. Caching via `setup-node`'s built-in npm cache with `cache-dependency-path: scripts/cdp-bridge/package-lock.json`. A separate `.github/workflows/deploy-docs.yml` builds the Astro docs site on path-filtered triggers (`docs-site/**`, `scripts/cdp-bridge/src/**`, `agents/*.md`, `commands/*.md`, `skills/**`, `CHANGELOG.md`, `.github/workflows/deploy-docs.yml`) and deploys to GitHub Pages with `concurrency: { group: pages, cancel-in-progress: true }`.

## Marketplace validation

### Cross-manifest version-sync as validation

`scripts/sync-versions.sh` is the sole validator. Compares `plugin.json` ↔ `marketplace.json` versions and regex-scans `scripts/cdp-bridge/src/` for hardcoded `version: 'x.y.z'` literals (B110 regression guard — the MCP server is required to read its version from `package.json` at module load). No JSON Schema validation step. Frontmatter is unvalidated. The `$schema` reference on `marketplace.json` points at the canonical Anthropic schema URL but no build step fetches it.

## Release automation

### No release automation / manual

No `release.yml`. Releases are created manually via `gh release create` or the GitHub Releases UI. 4 tags (`v0.15.1`, `v0.20.0`, `v0.23.0`, `v0.25.0`) against ~32 plugin versions on main — most plugin versions ship silently via the marketplace pulling from main HEAD. CI does not trigger on tags. Tag-format and tag-equals-plugin-version checks absent. CHANGELOG.md is hand-maintained; release notes hand-composed in the GitHub Releases UI.

### CHANGELOG with non-Keep-a-Changelog custom sections

`CHANGELOG.md` mixes Keep-a-Changelog base format (`## [0.25.0] — date`, `### Added`, `### Fixed`) with author-specific sections (`### Verified-stale`, `### Multi-review`, `### Benchmarks validated live`, `### Backlog state`, `### Validation`, `### Upgrade notes`). Entries reference internal ticket IDs (B111, B76, D642) and external issue numbers (GH #31). A `release-please`-style auto-generator wouldn't handle these custom sections.

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

Repo-root `README.md` is ~9 KB — install/setup table, usage walkthrough with 8-phase pipeline, MCP tool categorization, benchmarks, troubleshooting, security section, development, license. `CLAUDE.md` is ~7 KB+ — project overview, sibling-workspace-repo pointer (`../rn-dev-agent-workspace/`), quick start, development workflow, testing notes. No `architecture.md` at repo root (architecture content lives in `docs-site/src/content/docs/architecture.mdx`). README claims "53 MCP tools" while `hooks/detect-rn-project.sh` banner says "51 MCP tools" — hand-drift between two hard-coded counts. No CI-status badge, no license badge, no version badge in README.

### Astro Starlight docs site with auto-generated MDX

`docs-site/` ships a full Astro Starlight site, generator scripts at `docs-site/scripts/generate-bp-docs.mjs` (auto-generates MDX from `skills/rn-best-practices/references/*.md` — 46 best-practice rule files) and `docs-site/scripts/generate-tool-docs.mjs` (auto-generates from MCP tool registrations). Published to GitHub Pages via `deploy-docs.yml` with path filters (`has_pages: true`, URL: https://lykhoyda.github.io/rn-dev-agent/). The docs site is a first-class user-facing artifact in the same repo as the plugin code.

### CLAUDE.md template shipped for consumer projects

A `CLAUDE-MD-TEMPLATE.md` ships at repo root, intended to be copied into the consumer's RN project (not the plugin repo's own `CLAUDE.md`). Turns the plugin into a shipped convention: "add this to YOUR RN app's CLAUDE.md to tell Claude how to use us."

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

Repo-root `LICENSE` (MIT, "Copyright (c) 2026 Anton Lykhoyda"). `plugin.json` declares `license: "MIT"`. README references MIT. GitHub auto-detects.

## Community health files

### Bare minimum (LICENSE only)

Root carries `LICENSE` only. No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`. Security guidance lives as a `## Security` section inside `README.md`.

## Cross-platform discipline

### POSIX-only with no Windows story

Plugin ships only nix-style paths and shell scripts (`#!/usr/bin/env bash`). Many paths hardcode `xcrun simctl`, `adb`, `stat -f` vs `stat -c` with macOS-specific `if [ "$(uname)" = "Darwin" ]` branches. No `.cmd` / `.ps1` pairs. Windows-native git checkouts without `core.symlinks=true` would convert the `bin/` symlinks to plain text — moot because the iOS/Android simulator tooling targets macOS + Linux only.

## Multi-runtime portability

### Single-runtime — Claude Code only

Plugin manifests live exclusively under `.claude-plugin/`. No `.cursor-plugin/`, no `.codex/`. Skills, hooks, and scripts assume Claude Code's env vars and hook schema.
