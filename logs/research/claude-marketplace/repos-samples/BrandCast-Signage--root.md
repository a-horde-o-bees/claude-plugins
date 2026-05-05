# Sample

Mirrors of `https://github.com/BrandCast-Signage/root`. Single-plugin marketplace named `root-plugins` shipping a development workflow framework for Claude Code and Gemini CLI — tier-based planning, doc-aware context, RAG-powered search, multi-feature orchestration, autonomous issue-to-PR workflows.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root. Marketplace name `root-plugins`, sole plugin entry `root` with `source: "./"`. Top-level keys: `name`, `owner`, `license`, `plugins` array. No `metadata.{description,version,pluginRoot}` wrapper. `$schema` absent on `marketplace.json`. Marketplace description duplicated between `marketplace.json` `plugins[0].description` ("Development workflow framework — tier-based planning, doc-aware context, RAG search, session tracking, implementation plans") and `plugin.json` `description` (slightly different wording, adds "RAG-powered search … implementation plan generation") — drift risk between the two surfaces.

### Top-level `metadata` wrapper variants

Flat top-level fields only — `name`, `owner`, `license`, `plugins` directly on the JSON root with no `metadata` wrapper.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"`; plugin root and repo root are the same path. Trailing slash present.

### `strict` field default

`strict` field absent on the marketplace entry — implicit `true`. `skills` override on the marketplace entry absent; skills declared only on `plugin.json`.

## Per-plugin discoverability metadata

### Bare-minimum (name, version, description only)

Plugin entry on `marketplace.json` carries `name`, `source`, `description`, `version` only — no `category`, `tags`, or `keywords` at the marketplace entry level. `keywords: ["workflow","planning","rag","development","agents"]` lives only on the per-plugin `plugin.json`.

### `$schema` absence on per-plugin manifests

`$schema` absent on both `marketplace.json` and `plugin.json`.

## Version coordination

### Multi-artifact lockstep across N>2 manifests

Three sites carry the version field: `plugin.json` (`2.3.2`), `marketplace.json` `plugins[0].version` (`2.3.2`), and `gemini-extension.json`. `CLAUDE.md` declares the rule explicitly: "Three files must stay in sync on version bumps: plugin.json, marketplace.json, gemini-extension.json." No mechanism (hook, CI, script) enforces synchronization; the rule lives only in prose. A dev bumping one file and forgetting the others ships a skewed release.

## Channel distribution

### Marketplace-cache invalidation hack

Users install from `main` via `/plugin marketplace add BrandCast-Signage/root`. No stable/latest channel split, no `@ref` pinning in README. CHANGELOG entry for 2.3.1 reads literally "Patch bump to force the marketplace to pull v2.3.0's bundled-MCP changes. No code changes vs 2.3.0." — the team has hit the "marketplace cache didn't pick up our release" failure mode and fixed it by manual version bump rather than by distribution-mechanism change. Every marketplace fetch reads whatever is on `main`, and `main` carries whichever version field has been bumped most recently.

## Tag and release lifecycle

### No tags at all

`gh api repos/.../tags` returns empty; `gh api repos/.../releases` returns empty. Default branch `main`. No release branching, no pre-release suffixes, no dev-counter scheme. Version bumps are manual, one bump per release (`2.2.0`, `2.2.1`, `2.3.0`, `2.3.1`, `2.3.2`) recorded in commit log + `CHANGELOG.md` headings. No `.git/hooks` or `pre-commit` config checked into the repo. Releases exist only as `plugin.json`/`marketplace.json`/`gemini-extension.json` version strings and `CHANGELOG.md` headings; no git tag anchors a release commit. There is no way to `git checkout v2.3.0` — consumers are entirely dependent on `main`'s current state.

## Plugin-component registration

### Mixed (paths + auto-discovery)

`plugin.json` mixes explicit per-component paths and external file references. Commands declared as a directory (`./commands/root`); skills declared as two explicit paths; agents declared as eight explicit file paths; MCP servers via `"mcpServers": ["./.mcp.json"]`; hooks via `"hooks": "./.claude-plugin/hooks.json"`. No inline config objects.

### Hooks-json with broad event coverage

`.claude-plugin/hooks.json` declares `SessionStart`, `PostToolUse`, `Stop` entries.

### `.mcp.json` sibling file

`.mcp.json` declares two MCP servers: `local-rag` (third-party npm package) and `root-board` (plugin's own bundled MCP).

## Component composition

### Composition shapes

Mixed skills + commands + agents + hooks + MCP. Skills (2 — `root`, `mcp-local-rag`), commands (`commands/root/` with 12 files — 6 `.toml`+`.md` pairs for `docs`, `explore`, `impl`, `init`, `prd`, `rag`), agents (8 `.md` files), hooks (`.claude-plugin/hooks.json`), and `.mcp.json` (2 servers). No `.lsp.json`, no monitors, no `bin/`, no output-styles. Commands use a TOML+MD pair convention — `init.toml` carries `name`/`description`/`prompt` fields with a `prompt = '''…'''` block inline; the role of the `.md` sibling alongside the inline TOML prompt is not visible from sampling alone. The TOML+MD pair convention is harness-agnostic so the same commands serve Claude Code and Gemini CLI per `CLAUDE.md`.

## Agent declaration conventions

### Standard fields plus model / color

Sampled agent frontmatter (`team-architect.md`, `specialist-backend.md`) uses `name`, `description`, `model`. `team-architect.md` declares `model: opus`; `specialist-backend.md` declares `model: sonnet`. No `tools`, `skills`, `memory`, `background`, or `isolation` fields observed on the 2 of 8 agents sampled.

## Dependency installation

### Ownership-based install location split

The split is "we own the code" vs "someone else does." `mcp-local-rag` (third-party npm package) installs to `${HOME}/.root-framework/mcp/node_modules/mcp-local-rag/` — outside the plugin tree entirely. `mcp-root-board` (first-party bundled MCP) ships its binary inside `${CLAUDE_PLUGIN_ROOT}/mcp/mcp-root-board/dist/index.js`; its npm deps install into `${CLAUDE_PLUGIN_DATA}/mcp-root-board/node_modules/` at first session start. The `.mcp.json` `root-board` entry sets `NODE_PATH=${CLAUDE_PLUGIN_DATA}/mcp-root-board/node_modules` so the bundled binary resolves its imports from the data-dir cache.

CHANGELOG 2.3.0 articulates the rationale: third-party `mcp-local-rag` carries 5MB+ native bindings and releases on its own cadence, so a shared home-dir install amortizes download cost across Root versions and decouples lifecycles; first-party `mcp-root-board` is correctness-coupled to the plugin version that ships it, so bundling inside `${CLAUDE_PLUGIN_ROOT}` gives "lockstep versioning … automatically — no upgrade logic needed." v2.3.0 was a rewrite from the old model (both MCPs under `~/.root-framework/mcp/`); commit `feat: bundle mcp-root-board inside Claude plugin (v2.3.0)` is the crossover. Consumers upgrading from ≤2.2.x retain a populated `~/.root-framework/mcp/node_modules/@brandcast_app/mcp-root-board/` that the Claude plugin no longer uses; CHANGELOG 2.3.0 Migration notes this is "harmless if left in place" — but the automation does not clean it up.

Install script `hooks/scripts/ensure-mcp.sh` (invoked from `.claude-plugin/hooks.json` SessionStart, timeout 300s). Legacy `hooks/scripts/ensure-rag.sh` is present but its header comment marks it superseded. Script detects harness via `[[ -n "${CLAUDE_PLUGIN_ROOT:-}" && -n "${CLAUDE_PLUGIN_DATA:-}" ]]` guards; when the vars are unset (Gemini), the board-install block is skipped. CHANGELOG 2.3.0 Migration explicitly says "Gemini's gemini-extension.json continues to use the install-dir model for the board MCP — the bundling change is Claude-only for now."

Runtime: Node npm — `npm install`, `npm install @latest`, `npm install --omit=dev`. No Python, bun, pnpm, or yarn. Commands like `/root:init` shell out to `node "$RAG_BIN" … ingest …` (direct `node` invocation against the installed binary).

## Install change detection

### Diff-based byte comparison of manifest

`diff -q "$BOARD_PKG_SOURCE" "$BOARD_PKG_DATA"` byte-compares the bundled `package.json` against the cached copy in `${CLAUDE_PLUGIN_DATA}/mcp-root-board/package.json`; reinstalls when they differ. For `mcp-local-rag`: `npm view mcp-local-rag version` vs `require(package.json).version` on the installed copy.

## Install failure posture

### `rm` stamp on failure (retry next session)

For the board install: `rm -f "$BOARD_PKG_DATA"` on failure of `npm install`, with comment "Roll back the cached package.json so the next session retries."

### Silent fail-open (`exit 0` always, retry every hook)

For the RAG install path: no `rm` on failure — prints a corrective-action stderr message and `exit 0`. Soft-exit on `npm view` network errors (`[[ -n "$latest" ]] || return 0`). No `set -euo pipefail`, no JSON `systemMessage`, no `continue: false`. SessionStart hook never hard-fails. The `gh auth status` check at the end of `ensure-mcp.sh` is advisory ("⚠️" emoji + exit 0), not a hard precondition, even though the board's GitHub integration tools would fail without it.

## User configuration and authentication

### External config file owned by plugin

Plugin reads its own `root.config.json` in the consumer's repo (template at `root.config.example.json`, 2199 bytes, declares `configVersion: 2`). Schema is plugin-controlled: `configVersion`, `board.gates`, `project`, `ingest`, `docMappings`, `labelMappings`, `keywordMappings`, `docTargets`, `codingStandards`, `validation` sections. Per-project authorship — version-controlled with the project, configurable per repo.

Migration logic for older configs is inlined in `ensure-mcp.sh` as a Python heredoc that migrates v0/v1 → v2 in place, idempotently guarded by version compare. Bypasses Claude Code's `userConfig` surface and manages its own schema-versioned migration. Plugin uninstall does not clean up project-level config files.

`plugin.json` declares no `userConfig` block. `.mcp.json` env uses `${HOME}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` only — no `${user_config.KEY}` references.

## Session context loading

### Dependency install only (no context emission)

`SessionStart` hook fires `ensure-mcp.sh`, which installs/upgrades MCPs, migrates `root.config.json`, auto-ingests RAG if DB empty, checks `gh auth status`. No `hookSpecificOutput.additionalContext` emission. Hook output is plain stderr text. SessionStart with no matcher + 300s timeout + `npm install` potentially running means every resumed session can trigger a multi-minute startup delay on the first post-release resume; the `diff -q` guard mitigates the steady state, but the first session after each plugin upgrade pays the full install cost before the user can prompt.

### No SessionStart, only PreCompact / PostCompact / Stop / SessionEnd

UserPromptSubmit not used. Context injection happens inside the `/root` skill's protocol, which calls RAG via MCP tools.

## SessionStart matcher scope

### Empty matcher (all sub-events)

Single SessionStart entry has no `matcher` field — fires on `startup`, `resume`, `clear`, `compact` alike.

## Tool-use enforcement

### PostToolUse-only for notification + observation

`PreToolUse` hooks: none. `PostToolUse` has 2 entries — matcher `Edit|Write` → `track-edits.sh` (warns when `.md` files in ingest directories lack frontmatter), matcher `Read|Grep` → `track-doc-reads.sh` (near-no-op; doc-read tracking moved to the board MCP, the script only strips `.md` paths and exits). `PermissionRequest`/`PermissionDenied` absent. Output is stderr human-readable only — `track-edits.sh` prints a plain-text warning box to stderr when frontmatter is missing; no JSON stdout. `PostToolUse` on `Read|Grep` fires on every read in a session and does essentially nothing useful — header comment says "retained for the frontmatter check only" but the actual frontmatter check lives in `track-edits.sh`. Technical debt from the MCP migration.

## Hook handler runtime

### Bash scripts at conventional path

Hook scripts under `hooks/scripts/`. Mixed shebangs across scripts: `#!/bin/bash` (track-edits, track-doc-reads, context-receipt, doc-update-check) and `#!/usr/bin/env bash` (ensure-mcp). No `set -euo pipefail`. Soft-exits throughout.

## Hook failure posture

### Fail-open with always-exit-0

Every hook script either exits 0 silently or prints an advisory message and exits 0. No `continue: false`, no `stopReason`, no exit-2 blocks.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. The nearest analogue is `Stop` hooks (`context-receipt.sh`, `doc-update-check.sh`) which print advisory ASCII-bordered boxes at turn end — informational, not the `monitors.json` live-watch mechanism.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field declared on `plugin.json`. Single-plugin marketplace, no inter-plugin deps, no tags.

## Testing

### No tests

Outside the bundled MCP package, no tests for hook scripts, commands, skills, or agents. Within `mcp/mcp-root-board/` a jest configuration (`jest.config.js`) and tests directory (`mcp/mcp-root-board/src/__tests__/`) exist. Test runner invocation is `npm test` within `mcp/mcp-root-board/` (jest); local only.

## CI workflow shape

### No CI

No `.github/` directory in the repo (`gh api …/.github` returns 404). The "three files must stay in sync" rule from CLAUDE.md is enforced by human review only. Tag/release verification, marketplace JSON validation, hook-script lint, frontmatter validation — none are automated.

## Pre-commit and pre-push hooks (git)

### Absent

No `.pre-commit-config.yaml`, no committed git hooks. Commit shape is governed entirely by author discipline.

## Marketplace validation

### No validation

No CI step validates manifest shape, version agreement, or frontmatter conformance. Marketplace manifest, plugin manifest, and the hook-script set ship without an automated check that they parse, that their version fields agree, or that the paths they reference exist.

There is a runtime frontmatter check in `track-edits.sh`: when the user edits a `.md` file inside a directory listed in `root.config.json` `ingest.docs`, the hook warns if the first line is not `---`. That's consumer-oriented, not plugin-validation.

## Release automation

### No release automation / manual

Releases are commits on main that bump version fields and add a CHANGELOG section. No git tag, no GitHub release object, no release asset. Commit messages follow Conventional Commits (`feat:`/`fix:`/`chore:` prefixes) with `(vX.Y.Z)` version suffixes in the subject. CHANGELOG follows Keep a Changelog format ("The format is based on Keep a Changelog") + SemVer declaration but is never parsed.

## Documentation surface

### Two-document model (README + CLAUDE)

`README.md` at repo root is ~15KB — user-facing install + usage guide, two-harness instructions (Claude Code + Gemini). Single-plugin marketplace, so the repo root README is the plugin README. `CLAUDE.md` at repo root, ~3KB — operational procedures ("Version Sync", "Hook Event Mapping", "Dual-Harness Rules") plus light architecture ("`.claude-plugin/` — Claude Code plugin config", etc.). No dedicated `architecture.md`; architecture is sketched inside `CLAUDE.md`. Sibling `GEMINI.md` carries harness-specific agent guidance for the Gemini side. The dev-harness split (CLAUDE.md/GEMINI.md plus `dev/dual-harness/` not shipped to consumers) shows a deliberate dual-harness architecture.

### CHANGELOG with "Why" and "Migration" subsections

Each `CHANGELOG.md` release entry has `Added` / `Changed` / `Fixed` / `Why` / `Migration` subsections. The `Why` section is substantive multi-paragraph rationale; 2.2.1's `Why` cites the specific bug that motivated the fix (including a stream-record file path from a live session) and 2.3.0's `Why` documents the ownership-based install-location decision and links to external docs. `Migration` carries explicit consumer-side checklists. CHANGELOG functions as a design-decision log alongside release notes.

## Community health files

### Bare minimum (LICENSE only)

`LICENSE` at root (MIT, 1071 bytes). No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE`. No badges or status indicators in README head.

## License declaration

### Single repo-level license

`LICENSE` at repo root (MIT, SPDX `MIT`). Marketplace and plugin both declare `license: "MIT"` in their manifests.

## Cross-ecosystem distribution

### Dual-harness (Claude Code + Gemini CLI)

Single source tree carries `.claude-plugin/plugin.json` AND `gemini-extension.json`. Commands are `*.toml + *.md` pairs designed to be harness-agnostic. Hook scripts in `hooks/scripts/` (not `.claude-plugin/hooks/`) so both harnesses can wire them via their respective registration files (`.claude-plugin/hooks.json` for Claude vs `hooks/gemini-hooks.json` for Gemini). Hook scripts guard on `${CLAUDE_PLUGIN_ROOT:-}` to skip Claude-only logic when running under Gemini. CHANGELOG records the deliberate harness asymmetry: `gemini-extension.json` still points its `root-board` MCP at `${HOME}/.root-framework/mcp/node_modules/@brandcast_app/mcp-root-board/dist/index.js` (install-dir model) while Claude's path is bundled inside `${CLAUDE_PLUGIN_ROOT}`.

## Novel and cross-cutting concerns

### MCP server reads hook-authored artifact

`mcp-root-board`'s tool surface depends on configuration that lives in the consumer-project `root.config.json`; per CHANGELOG 2.2.0, schema migration for stream records (`StreamState.SCHEMA_VERSION` bumped to 2, `migrate.ts` backfills pre-v2 records) and a new `tierJustification` requirement makes bare tier overrides rejectable at the API boundary — structural enforcement of agent discipline at the MCP layer rather than via prose convention.
