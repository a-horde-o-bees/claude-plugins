# BrandCast-Signage/root

## Identification

- **URL**: https://github.com/BrandCast-Signage/root
- **Stars**: 3
- **Last commit date**: 2026-04-19 (commit `fix(worktree): run dependency install after git worktree add (v2.3.2)`)
- **Default branch**: main
- **License**: MIT (SPDX: MIT)
- **Sample origin**: dep-management
- **One-line purpose**: "Development workflow framework for Claude Code and Gemini CLI" — tier-based planning, doc-aware context, RAG-powered search, multi-feature orchestration, autonomous issue-to-PR workflows (per `README.md` opening).

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root. Single-plugin marketplace named `root-plugins`. (Observed.)
- **Marketplace-level metadata**: top-level `name`, `owner`, `license` plus a `plugins` array. No `metadata.{description,version,pluginRoot}` wrapper. (Observed.)
- **`metadata.pluginRoot`**: absent. (Observed.)
- **Per-plugin discoverability**: none — plugin entry has `name`, `source`, `description`, `version` only; no `category`, no `tags`, no `keywords` at the marketplace entry level. Keywords live only on the per-plugin `plugin.json` (`"keywords": ["workflow","planning","rag","development","agents"]`). (Observed.)
- **`$schema`**: absent on both `marketplace.json` and `plugin.json`. (Observed.)
- **Reserved-name collision**: plugin and marketplace both use the literal name "root" / "root-plugins". Not a reserved Claude Code name, but "root" as a plugin name is unusually generic and could collide with any future built-in. (Observed; impact inferred.)
- **Pitfalls observed**: the marketplace description is duplicated in two places — `marketplace.json` `plugins[0].description` ("Development workflow framework — tier-based planning, doc-aware context, RAG search, session tracking, implementation plans") and `plugin.json` `description` (same theme but slightly different wording — adds "RAG-powered search … implementation plan generation"). Drift risk between the two descriptions.

## 2. Plugin source binding

- **Source format(s) observed**: relative — `"source": "./"`. The plugin and the marketplace root are the same directory. (Observed.)
- **`strict` field**: absent; implicit `true`. (Observed.)
- **`skills` override on marketplace entry**: absent. Skills are declared only on `plugin.json`. (Observed.)
- **Version authority**: both — `plugin.json` `version: "2.3.2"` and `marketplace.json` `plugins[0].version: "2.3.2"` hold the same literal. `CLAUDE.md` explicitly calls out "Three files must stay in sync on version bumps: plugin.json, marketplace.json, gemini-extension.json" — so the repo knows about drift risk and mitigates by convention rather than structure. (Observed.)
- **Pitfalls observed**: no mechanism (hook, CI, script) enforces version-field synchronization — the rule lives only in prose in `CLAUDE.md`. A dev bumping one file and forgetting the others ships a skewed release.

## 3. Channel distribution

- **Channel mechanism**: no split. Users install from `main` via `/plugin marketplace add BrandCast-Signage/root`. No stable/latest channel pair, no `@ref` pinning in README. (Observed.)
- **Channel-pinning artifacts**: absent. (Observed.)
- **Pitfalls observed**: every marketplace fetch reads whatever is on `main`, and `main` carries the version field that's been bumped with each release (2.3.2 as of snapshot). `CHANGELOG.md` entry for 2.3.1 is literally "Patch bump to force the marketplace to pull v2.3.0's bundled-MCP changes. No code changes vs 2.3.0." — so the team has already hit the "marketplace cache didn't pick up our release" class of problem once and fixed it by manual version bump rather than by distribution-mechanism change.

## 4. Version control and release cadence

- **Default branch name**: main. (Observed.)
- **Tag placement**: no git tags exist at all — `gh api repos/.../tags` returns empty, `gh api repos/.../releases` returns empty. (Observed.)
- **Release branching**: none. (Observed.)
- **Pre-release suffixes**: none observed. (Observed — no tags to check.)
- **Dev-counter scheme**: absent. Version bumps are manual, one bump per release (`2.2.0`, `2.2.1`, `2.3.0`, `2.3.1`, `2.3.2`). (Observed in commit log + CHANGELOG.)
- **Pre-commit version bump**: no. No `.git/hooks` or `pre-commit` config checked into repo. (Observed.)
- **Pitfalls observed**: Releases exist only as `plugin.json`/`marketplace.json`/`gemini-extension.json` version strings and `CHANGELOG.md` headings; no git tag anchors a release commit. There is no way to `git checkout v2.3.0` — consumers are entirely dependent on `main`'s current state. This compounds the channel-distribution issue from §3 — no immutable reference point exists for any historical release.

## 5. Plugin-component registration

- **Reference style in plugin.json**: mixed — explicit per-component paths for commands (`./commands/root`), skills (two explicit paths), agents (eight explicit file paths), plus an external file reference for MCP servers (`"mcpServers": ["./.mcp.json"]`) and hooks (`"hooks": "./.claude-plugin/hooks.json"`). No inline config objects. (Observed.)
- **Components observed**: skills yes (2 — `root`, `mcp-local-rag`), commands yes (`commands/root/` with 12 files — 6 `.toml`+`.md` pairs for `docs`, `explore`, `impl`, `init`, `prd`, `rag`), agents yes (8 `.md` files), hooks yes (`.claude-plugin/hooks.json` with `SessionStart`, `PostToolUse`, `Stop` entries), `.mcp.json` yes (2 servers — `local-rag`, `root-board`), `.lsp.json` no, monitors no, bin no, output-styles no.
- **Agent frontmatter fields used**: `name`, `description`, `model`. Sampled `team-architect.md` uses `model: opus`; `specialist-backend.md` uses `model: sonnet`. No `tools`, `skills`, `memory`, `background`, or `isolation` fields observed. (Observed on 2 of 8 agents.)
- **Agent tools syntax**: not applicable — no `tools` field present on sampled agents.
- **Pitfalls observed**: commands use a TOML+MD pair convention (`init.toml` carries `name`/`description`/`prompt` fields; the `.md` sibling presumably carries the full prompt — the TOML file already has a `prompt = '''…'''` block inline, so the role of the `.md` sibling is unclear from sampling alone). This is a harness-agnostic convention the repo maintains to share commands between Claude Code and Gemini CLI (per `CLAUDE.md`).

## 6. Dependency installation

- **Applicable**: yes. This is the flagged sample — two MCP servers (Node) with a deliberately mixed install-location pattern.
- **Dep manifest format**: `package.json` for `mcp/mcp-root-board/` (bundled MCP server, `@modelcontextprotocol/sdk ^1.0.0` as its one runtime dep). No `requirements.txt`, no `pyproject.toml`. (Observed.)
- **Install location**: mixed — **split by ownership**:
    - `mcp-local-rag` (third-party npm package): installed into `${HOME}/.root-framework/mcp/node_modules/mcp-local-rag/`. Outside the plugin tree entirely.
    - `mcp-root-board` (plugin's own MCP, bundled): binary lives at `${CLAUDE_PLUGIN_ROOT}/mcp/mcp-root-board/dist/index.js` (shipped in the plugin tarball); its npm deps are installed into `${CLAUDE_PLUGIN_DATA}/mcp-root-board/node_modules/` at first session start.
    - The `.mcp.json` `root-board` entry wires the split together by setting `NODE_PATH=${CLAUDE_PLUGIN_DATA}/mcp-root-board/node_modules` so the bundled binary resolves its imports from the data-dir cache. (Observed.)
- **Install script location**: `hooks/scripts/ensure-mcp.sh` (invoked from `.claude-plugin/hooks.json` SessionStart, timeout 300s). A legacy `hooks/scripts/ensure-rag.sh` is present but its header comment marks it superseded. (Observed.)
- **Change detection**: `diff -q "$BOARD_PKG_SOURCE" "$BOARD_PKG_DATA"` — byte-compares the bundled `package.json` against the cached copy in `${CLAUDE_PLUGIN_DATA}/mcp-root-board/package.json`; reinstalls when they differ. For `mcp-local-rag`: `npm view mcp-local-rag version` vs. `require(package.json).version` on the installed copy. (Observed.)
- **Retry-next-session invariant**: `rm -f "$BOARD_PKG_DATA"` on failure of the board `npm install`, with comment "Roll back the cached package.json so the next session retries." The RAG install path does not `rm` on failure — it prints a corrective-action message and `exit 0`s. (Observed.)
- **Failure signaling**: mixed per path. Soft failures throughout: `exit 0` when `mcp-local-rag` install fails (with stderr install-instruction message); soft-exit on `npm view` network errors (`[[ -n "$latest" ]] || return 0`); `rm` + "The next session will retry" message on board-install failure. No `set -euo pipefail`, no JSON `systemMessage`, no `continue: false`. SessionStart hook never hard-fails. (Observed.)
- **Runtime variant**: Node npm — `npm install`, `npm install @latest`, `npm install --omit=dev`. No Python, no bun, no pnpm, no yarn. (Exception: the board's `createWorktree` tool, per CHANGELOG 2.3.2, detects consumer lockfiles and runs npm/pnpm/yarn/bun — that's consumer-project install, not plugin install.)
- **Alternative approaches**: none in this repo for the plugin itself. Commands like `/root:init` shell out to `node "$RAG_BIN" … ingest …` (direct `node` invocation against the installed binary), not `npx`/`uvx` ad-hoc execution.
- **Version-mismatch handling**: `mcp-local-rag` upgrade on every session — compares installed version to `npm view …@latest` and runs `npm install mcp-local-rag@latest` if they differ. Fails soft on offline / registry errors. `mcp-root-board` has no version-tracking logic — it's bundled, so "lockstep versioning between plugin and MCP code" (per the script comment and CHANGELOG 2.3.0) is structural; upgrading the plugin upgrades the bundled MCP. (Observed.)
- **Pitfalls observed**: 
    - The split exists for a **specific, documented reason** (recorded in CHANGELOG 2.3.0 "Why" section and in `ensure-mcp.sh` comments): `mcp-local-rag` is an external third-party package whose native bindings are 5MB+ and whose release cadence is independent of this plugin, so sharing a home-dir install across Root versions amortizes the download cost and decouples lifecycles. `mcp-root-board` is first-party code whose correctness is tied to the plugin version it ships with — bundling it inside `${CLAUDE_PLUGIN_ROOT}` gives "lockstep versioning … automatically — no upgrade logic needed." This is a conscious split along the "ours vs. theirs" axis, with install-location mechanics following ownership.
    - v2.3.0 was a rewrite from the old model (both MCPs living under `~/.root-framework/mcp/`) to the current split. The commit `feat: bundle mcp-root-board inside Claude plugin (v2.3.0)` is the crossover.
    - v2.3.1 was a no-op version bump purely to force the marketplace to re-pull v2.3.0 — evidence the repo has zero control over marketplace refresh timing. The CHANGELOG entry admits it openly.
    - **Harness asymmetry**: `gemini-extension.json` still points its `root-board` MCP at `${HOME}/.root-framework/mcp/node_modules/@brandcast_app/mcp-root-board/dist/index.js` — the bundling change is Claude-only. The `ensure-mcp.sh` script detects this via `-n "${CLAUDE_PLUGIN_ROOT:-}" && -n "${CLAUDE_PLUGIN_DATA:-}"` guards; when the vars are unset (Gemini), the board-install block is skipped. CHANGELOG 2.3.0 Migration note explicitly says "Gemini's gemini-extension.json continues to use the install-dir model for the board MCP — the bundling change is Claude-only for now."
    - **Orphan on upgrade path**: consumers upgrading from ≤2.2.x retain a populated `~/.root-framework/mcp/node_modules/@brandcast_app/mcp-root-board/` that the Claude plugin no longer uses. CHANGELOG 2.3.0 Migration notes this is "harmless if left in place" — but the automation doesn't clean it up.
    - The `gh auth status` check at the end of `ensure-mcp.sh` is advisory ("⚠️" emoji + exit 0), not a hard precondition, even though the board's GitHub integration tools would fail without it.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — no `bin/` directory at the plugin root, no `bin` field in any manifest, no symlinks. The plugin exposes slash commands and MCP tools, not shell wrappers. (Observed.)
- **`bin/` files**: n/a.
- **Shebang convention**: n/a for bin/. Hook scripts themselves use `#!/bin/bash` (track-edits, track-doc-reads, context-receipt, doc-update-check) and `#!/usr/bin/env bash` (ensure-mcp). Mixed shebangs across hook scripts. (Observed.)
- **Runtime resolution**: n/a.
- **Venv handling (Python)**: n/a — no Python runtime.
- **Platform support**: n/a.
- **Permissions**: n/a.
- **SessionStart relationship**: n/a.
- **Pitfalls observed**: none — purpose not applicable.

## 8. User configuration

- **`userConfig` present**: no — neither `plugin.json` nor `marketplace.json` carries a `userConfig` block. (Observed.)
- **Field count**: none at the plugin level. The plugin instead reads per-project settings from a `root.config.json` file in the consumer's repo (see `root.config.example.json`, 2199 bytes, configVersion 2). That's application-level config, not Claude Code plugin `userConfig`. (Observed.)
- **`sensitive: true` usage**: not applicable — no `userConfig`.
- **Schema richness**: not applicable at the plugin level. The per-project `root.config.json` is its own typed schema with `configVersion`, `board.gates`, `project`, `ingest`, `docMappings`, `labelMappings`, `keywordMappings`, `docTargets`, `codingStandards`, `validation` sections — versioned and migrated in-place by `ensure-mcp.sh` (v0/v1 → v2 migration logic is inlined as a Python heredoc).
- **Reference in config substitution**: not applicable — no `${user_config.KEY}` references observed in `.mcp.json` or hooks.json. MCP env uses `${HOME}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` only.
- **Pitfalls observed**: The plugin deliberately bypasses Claude Code's `userConfig` surface and owns its own config format + migration path. For a workflow framework with many tunables (`maxParallel`, gate policies, doc mappings, validation commands), the authors chose per-project JSON over plugin-scoped user config. This puts all config authorship in the consumer's repo and version-controls it alongside the project, at the cost of not being configurable via `/plugin` UI.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none. (Observed in `.claude-plugin/hooks.json`.)
- **PostToolUse hooks**: 2 entries — matcher `Edit|Write` → `track-edits.sh` (tracks edits, warns when `.md` files in ingest directories lack frontmatter), matcher `Read|Grep` → `track-doc-reads.sh` (currently a near-no-op — doc read tracking was moved to the board MCP; the script only strips `.md` paths and exits). (Observed.)
- **PermissionRequest/PermissionDenied hooks**: absent. (Observed.)
- **Output convention**: stderr human-readable only. `track-edits.sh` prints a plain-text warning box to stderr when frontmatter is missing; no JSON stdout. (Observed.)
- **Failure posture**: fail-open throughout. Every hook script either exits 0 silently or prints an advisory message and exits 0. No `continue: false`, no `stopReason`, no exit-2 blocks. (Observed.)
- **Top-level try/catch wrapping**: not applicable — bash scripts, no exception handling. Scripts do not even set `-euo pipefail`. (Observed.)
- **Pitfalls observed**: `PostToolUse` on `Read|Grep` fires on every read in a session and does essentially nothing useful (its payload has migrated to the board MCP). The hook is dead weight now — per its header comment "retained for the frontmatter check only" but the actual frontmatter check is in `track-edits.sh`, not here. This is technical debt from the MCP migration.

## 10. Session context loading

- **SessionStart used for context**: no — only for dep install. `ensure-mcp.sh` installs/upgrades MCPs, migrates `root.config.json`, auto-ingests RAG if DB empty, checks `gh auth status`. No `hookSpecificOutput.additionalContext` emission. (Observed.)
- **UserPromptSubmit for context**: no — no `UserPromptSubmit` hook. Context injection happens inside the `/root` skill's protocol (which calls RAG via MCP tools). (Observed.)
- **`hookSpecificOutput.additionalContext` observed**: no. (Observed — all hook outputs are plain stderr text.)
- **SessionStart matcher**: none. The single SessionStart entry has no `matcher` field, so it fires on all SessionStart sub-events (startup, resume, clear, compact). (Observed.)
- **Pitfalls observed**: SessionStart with no matcher + a 300s timeout + `npm install` potentially running means every resumed session could trigger a multi-minute startup delay on the first post-release resume. The `diff -q` guard mitigates the steady state, but the first session after each plugin upgrade pays the full install cost before the user can prompt.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no. (Observed.)
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none — purpose not applicable. The nearest analogue is `Stop` hooks (`context-receipt.sh`, `doc-update-check.sh`) which print advisory ASCII-bordered boxes at turn end. Those are informational, not the `monitors.json` live-watch mechanism.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no. (Observed in `plugin.json`.)
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace, no inter-plugin deps, and no tags exist in the repo at all.
- **Pitfalls observed**: none — purpose not applicable.

## 13. Testing and CI

- **Test framework**: jest — `mcp/mcp-root-board/jest.config.js`, tests live in `mcp/mcp-root-board/src/__tests__/` (observed directory existence). (Observed.)
- **Tests location**: inside the bundled MCP package at `mcp/mcp-root-board/src/__tests__/`. No tests for the hook scripts, no tests for commands/skills/agents. (Observed.)
- **Pytest config location**: not applicable — not a Python project.
- **Python dep manifest for tests**: not applicable.
- **CI present**: no — no `.github/` directory in the repo (`gh api …/.github` returns 404). (Observed.)
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: `npm test` within `mcp/mcp-root-board/` (jest), local only. No repo-level test entry point.
- **Pitfalls observed**: no CI at all means the "three files must stay in sync" rule from CLAUDE.md is enforced by human review only. Tag/release verification, marketplace JSON validation, hook-script lint, frontmatter validation — none are automated. For a repo publishing a marketplace plugin, the absence of even a basic manifest-validation workflow is a gap.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no. (Observed — no `.github/`.)
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — releases are fully manual: bump versions in three files, update CHANGELOG, commit with message `(vX.Y.Z)`. No git tag. No GitHub release object. (Observed via commit log + empty tag/release API responses.)
- **Tag-sanity gates**: not applicable — no tags to gate.
- **Release creation mechanism**: not applicable — no GitHub releases created.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable — CHANGELOG is human-maintained in Keep a Changelog format but never parsed.
- **Pitfalls observed**: "release" here means "a commit on main that bumps version fields and adds a CHANGELOG section." There is no immutable artifact — no tag, no release asset, no GitHub release notes. Consumers cannot pin to a version; they get whatever `main` says right now. This is the same concern surfaced in §3 and §4, expressed on the distribution axis.

## 15. Marketplace validation

- **Validation workflow present**: no. (Observed.)
- **Validator**: not applicable.
- **Trigger**: not applicable.
- **Frontmatter validation**: not applicable as CI. There IS a runtime frontmatter check in `track-edits.sh` — when the user edits a `.md` file inside a directory listed in `root.config.json` `ingest.docs`, the hook warns if the first line isn't `---`. Consumer-oriented, not plugin-validation. (Observed.)
- **Hooks.json validation**: not applicable.
- **Pitfalls observed**: the repo ships a marketplace manifest and a plugin manifest with no automated check that they parse, that their version fields agree, or that the paths they reference exist. Bad commits could easily ship.

## 16. Documentation

- **`README.md` at repo root**: present, ~15KB. User-facing install + usage guide, rich, two-harness instructions (Claude Code + Gemini). (Observed.)
- **`README.md` per plugin**: not applicable — single-plugin marketplace, the repo root README is the plugin README.
- **`CHANGELOG.md`**: present, ~11.6KB, Keep a Changelog format explicitly declared ("The format is based on Keep a Changelog") + SemVer declaration. Each release entry has `Added` / `Changed` / `Fixed` / `Why` / `Migration` subsections — the `Why` section is unusually substantive (decision rationale with links to external docs). (Observed.)
- **`architecture.md`**: absent — no dedicated architecture doc at repo root or per-component. Architecture is sketched inside `CLAUDE.md`. (Observed.)
- **`CLAUDE.md`**: present at repo root, ~3KB. Dual-purpose: operational procedures ("Version Sync", "Hook Event Mapping", "Dual-Harness Rules") + light architecture ("`.claude-plugin/` — Claude Code plugin config", etc.). Also has a `GEMINI.md` sibling — harness-specific agent guidance. (Observed.)
- **Community health files**: none observed — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE`. (Observed.)
- **LICENSE**: present, MIT (1071 bytes). (Observed.)
- **Badges / status indicators**: none observed in README head. (Observed — sampled first 200 lines.)
- **Pitfalls observed**: the `CLAUDE.md`/`GEMINI.md` pair plus the dev-harness split in `dev/dual-harness/` (not shipped to consumers — called out in CLAUDE.md) shows a deliberate dual-harness architecture, but no `architecture.md` captures the cross-cutting design that the hook-event mapping table in CLAUDE.md only hints at.

## 17. Novel axes

- **Dual-harness authoring** — the repo is both a Claude Code plugin AND a Gemini CLI extension out of a single source tree. `commands/root/*.toml+.md` pairs, `hooks/scripts/*.sh` (harness-agnostic), `hooks/gemini-hooks.json` (Gemini-specific hook wiring), `.mcp.json` for Claude and `mcpServers` inline in `gemini-extension.json`. This shapes many decisions (why `ensure-mcp.sh` guards on `${CLAUDE_PLUGIN_ROOT:-}` being set; why the script is in `hooks/scripts/` not `.claude-plugin/hooks/`). Candidate for a new purpose section on "multi-harness distribution."
- **Ownership-based install-location split** — the most distinctive observation for this sample. Third-party npm MCP (`mcp-local-rag`) installed into a shared home directory `${HOME}/.root-framework/mcp/`; first-party bundled MCP (`mcp-root-board`) living in `${CLAUDE_PLUGIN_ROOT}/mcp/…` with deps written to `${CLAUDE_PLUGIN_DATA}`. The axis is "we own the code" vs. "someone else does," and the install-location mechanics follow ownership rather than runtime (both are Node). CHANGELOG 2.3.0's "Why" section articulates this rationale in its own voice. Candidate for a new purpose section on "dep-install location selection by code ownership."
- **Versioned consumer-project config with in-hook migration** — `root.config.json` carries a `configVersion` field; `ensure-mcp.sh` reads it and inlines a Python heredoc to migrate v0/v1 → v2 on session start (moves `include`/`exclude` fields under a new `ingest.docs` shape). Config migration runs on every session start and is idempotent (guarded by version compare). Distinct from `userConfig`-based patterns where Claude Code owns the schema. Candidate for a new purpose section on "consumer-project config schema evolution."
- **Schema-versioned MCP state with structural override-prevention** — per CHANGELOG 2.2.0: `StreamState.SCHEMA_VERSION` bumped to 2, `migrate.ts` backfills pre-v2 records, and a new `tierJustification` requirement makes bare tier overrides rejectable at the API boundary. Structural enforcement of agent discipline (can't fake a tier classification without committing a reason to disk) rather than prose convention. Candidate for a new purpose section on "MCP-level agent-behavior enforcement."
- **Self-describing CHANGELOG with "Why" + "Migration" sections** — nearly every release entry carries a multi-paragraph "Why" rationale and a "Migration" checklist. 2.2.1's "Why" section cites the specific bug that motivated the fix (including a stream-record file path from a live session). This is substantively more detailed than Keep a Changelog's prescription. Candidate for a new purpose section on "release-note structure."
- **Skill model rubric** — `skills/root/MODEL_RUBRIC.md` sits alongside `SKILL.md`. Not a field in any spec, but evidence of content the plugin ships in the skill directory beyond the `SKILL.md` itself. (Observed but not read — noted as a potential new component convention.)

## 18. Gaps

- `architecture.md` not found — the cross-harness architectural design is only partially documented in `CLAUDE.md`; the rest requires reading the source. Resolving would need either a WebFetch of a (possibly nonexistent) design doc or reading all of `commands/`, `skills/`, and `hooks/gemini-hooks.json` in detail.
- The `.md` half of each `commands/root/*.toml+.md` pair was not read — I sampled only `init.toml`. The role of the `.md` sibling (whether it supersedes the inline `prompt = '''…'''` block in the `.toml`, or supplements it) is unresolved. Would need `curl`s on `docs.md`, `explore.md`, `impl.md`, `prd.md`, `rag.md`, `init.md`, plus their `.toml` counterparts.
- `hooks/gemini-hooks.json` was not fetched. Would resolve "how does the Gemini harness wire the same scripts differently" beyond the summary table in `CLAUDE.md`. One WebFetch away.
- `dev/dual-harness/SKILL.md` referenced in CLAUDE.md ("BEFORE making any code change, load the dual-harness rules") was not fetched. Would resolve the exact shared-vs-harness-specific boundary enforcement. One WebFetch away.
- `mcp/mcp-root-board/src/` was enumerated (10 files: `board.ts`, `classify.ts`, `gates.ts`, `github.ts`, `graph.ts`, `index.ts`, `migrate.ts`, `types.ts`, `worktree.ts`, `__tests__/`) but no file was read. The gate mechanics, tier classifier heuristics, and schema migration details are inferable only from CHANGELOG narration — resolving would require reading at least `types.ts`, `classify.ts`, `migrate.ts`.
- `gh` CLI presence is checked by the hook but never hard-enforced as a precondition. Whether the board MCP server itself validates `gh` auth at tool-call time was not verified — would require reading `mcp/mcp-root-board/src/github.ts`.
- No git tags or releases exist, so tag-format / release-notes conventions can't be observed — only commit-message conventions (which use `feat:`/`fix:`/`chore:` Conventional Commits prefixes with `(vX.Y.Z)` version suffixes in the subject).
- The `skills/root/MODEL_RUBRIC.md` file's content was not read. Whether it's a first-class convention worth calling out in §17 depends on what it contains — one WebFetch would resolve.
- `templates/` directory was enumerated only at the top level (not descended) — the PRD and Implementation Plan templates that `/root:init` installs were not read.
- The research sampled 2 of 8 agent frontmatter blocks (`team-architect`, `specialist-backend`). Whether the remaining 6 agents declare additional frontmatter fields (`tools`, `skills`, etc.) is inferred from the sample, not verified.
