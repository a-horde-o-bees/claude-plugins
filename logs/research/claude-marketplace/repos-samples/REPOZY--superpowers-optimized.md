# REPOZY/superpowers-optimized

## Identification

- **URL**: https://github.com/REPOZY/superpowers-optimized
- **Stars**: 63
- **Last commit date**: 2026-04-17 (main `3229d61`, "Update README.md")
- **Default branch**: main
- **License**: MIT
- **Sample origin**: primary (community)
- **One-line purpose**: "Agentic development framework for Claude Code — disciplined workflow routing, TDD enforcement, safety hooks, systematic debugging, and code review" (from `plugin.json` / README: a production-grade fork of `obra/superpowers` adding 3-tier workflow routing, safety hooks, red-team adversarial testing, and a cross-session memory stack).

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, 1 plugin entry pointing at `./`
- **Marketplace-level metadata**: `metadata.description` wrapper (no `version` or `pluginRoot` under metadata). `owner.name` is `"Jesse Vincent, forked by REPOZY"`
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `category: productivity`, 10 `keywords` (skills, tdd, debugging, code-review, workflows, agentic, token-efficiency, hooks, safety, subagent), 5 `tags` (superpowers, claude-code, cursor, codex, agent-workflow); all three dimensions populated for the single plugin
- **`$schema`**: absent
- **Reserved-name collision**: no (plugin name `superpowers-optimized` is not reserved)
- **Pitfalls observed**: single-plugin marketplace; plugin name matches the marketplace `name` (`superpowers-optimized`), so the documented install command is the repeated form `/plugin install superpowers-optimized@superpowers-optimized`. `$schema` is not referenced, so marketplace-editor tooling that relies on it will not autocomplete.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./"`) — the plugin is the repo itself
- **`strict` field**: default (implicit true) — not set explicitly
- **`skills` override on marketplace entry**: absent (no `skills` field at marketplace level)
- **Version authority**: both — `marketplace.json` entry `version: "6.6.0"`, `.claude-plugin/plugin.json` `version: "6.6.0"`, `.codex-plugin/plugin.json` `version: "6.6.0"`, `.cursor-plugin/plugin.json` `version: "6.6.0"`, and root `VERSION` file `6.6.0`. Five copies to keep in sync (drift risk). `plugin.universal.yaml` is declared as the single source of truth but was observed stamped at `6.5.2` while every other file is at `6.6.0`, so the `hookbridge compile` step has drifted from the published version.
- **Pitfalls observed**: Fork of `obra/superpowers` (GitHub API `fork: true`, parent `obra/superpowers`). The README credits `Jesse Vincent, forked by REPOZY` and the original author's name is in every `plugin.json` `author.name`. `plugin.universal.yaml` says "single source of truth" but its `meta.version` is visibly out of date relative to the compiled artifacts.

## 3. Channel distribution

- **Channel mechanism**: no split — a single marketplace entry sources `./`. Users pin by `@ref` via standard Claude Code marketplace install; Codex/OpenCode users `git pull`. The session-start hook provides a soft auto-update channel (fetch + fast-forward-only merge, 24 h cache, `SUPERPOWERS_AUTO_UPDATE=0` opt-out).
- **Channel-pinning artifacts**: no `stable-tools`/`latest-tools` pattern, no release-branch split; `main` is the release branch. Tags `v6.6.0 … v4.2.0` live on main.
- **Pitfalls observed**: no pre-release channel — users who want RC builds must `git checkout` a feature branch manually (24 non-main branches observed, including `dev`, `new-release`, `feat/*`, `wip/*`).

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main (tags `v6.6.0` … `v4.2.0` observed; `v6.6.0` points at `0a78a700` on main history, one commit before latest `3229d61` README-only update)
- **Release branching**: none — tag-on-main. `dev` exists as a working branch (unique in sample — only sampled repo with a `dev/` long-lived branch; dev-branch tree adds a `commands/` directory not present on main). Many topic/WIP branches (`feat/codex-*`, `fix/windows-*`, `wip/*`) but no `release/*` pattern.
- **Pre-release suffixes**: none observed — tags are plain `vX.Y.Z`
- **Dev-counter scheme**: absent — `main` holds real semver, no `0.0.z` counter
- **Pre-commit version bump**: no — no pre-commit hook config in the repo; `plugin.universal.yaml` is bumped manually and recompiled by `hookbridge compile`
- **Pitfalls observed**: version authority is spread across five files plus `plugin.universal.yaml`, and the universal yaml lags behind. The release cadence is high (v6.0.0 → v6.6.0 within ~1 month per release dates).

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `.claude-plugin/plugin.json` contains only metadata fields (name, description, version, author, homepage, repository, license, keywords). No explicit `skills`, `agents`, `hooks`, `commands` arrays. Claude Code discovers top-level `skills/`, `agents/`, and `hooks/hooks.json` implicitly. The Codex (`.codex-plugin/plugin.json`) and Cursor (`.cursor-plugin/plugin.json`) manifests explicitly set `"skills": "./skills/"` (and `.cursor-plugin` adds `"agents": "./agents/"`) because those runtimes require explicit paths.
- **Components observed**: skills yes (24 under `skills/`), commands no (none on main; dev branch has a `commands/` tree), agents yes (2 — `code-reviewer.md`, `red-team.md`), hooks yes (`hooks/hooks.json` with 6 events, 10 hook entries), .mcp.json no, .lsp.json no, monitors no, bin no, output-styles no
- **Agent frontmatter fields used**: `name`, `description`, `model: inherit`, `memory: user` (on both `code-reviewer.md` and `red-team.md`). No `tools`, `skills`, `background`, `isolation`, or `thinking` fields observed.
- **Agent tools syntax**: not applicable — agents do not declare a `tools` allow-list; they inherit the parent session's permissions
- **Pitfalls observed**: Claude/Codex/Cursor discover components differently — Claude relies on directory convention, Codex/Cursor require the `skills`/`agents` keys. The three `plugin.json` files plus the universal yaml must all agree on paths.

## 6. Dependency installation

- **Applicable**: no — the plugin ships zero runtime Python or Node dependencies. All hooks are Node built-ins only. The `context-engine.js` header explicitly states "Zero dependencies". `hooks/bash-compress-hook.js` uses only `path`, `fs`, `os`, and a local `./compression-rules.js`.
- **Dep manifest format**: none — no `requirements.txt`, no `pyproject.toml`, no `package.json` at the plugin root
- **Install location**: not applicable
- **Install script location**: not applicable (the `hooks/session-start` bash script performs a "self-update" — `git fetch` + `git merge --ff-only origin/main` on git-based installs, with a 24 h cache — but it only updates the plugin itself, no external deps)
- **Change detection**: not applicable for deps. For the self-update, diff detection happens through git's own HEAD comparison; the last-session HEAD is persisted to `~/.claude/hooks-logs/last-session-head-<md5-of-cwd>.txt` so the next session can diff against it
- **Retry-next-session invariant**: not applicable
- **Failure signaling**: not applicable to deps; the self-update path fails silently (`fail silently — never block session startup`)
- **Runtime variant**: Node (every hook is a `.js` invoked via `node`), plus bash for `session-start` and the polyglot CMD/bash wrapper `run-hook.cmd`
- **Alternative approaches**: the "no deps" philosophy is the alternative — the plugin deliberately constrains itself to Node built-ins to avoid any install step
- **Version-mismatch handling**: none
- **Pitfalls observed**: the plugin requires Node on the user's PATH for most hooks; on Codex, the bash wrapper sources `~/.nvm/nvm.sh` as a fallback and emits `{}` if Node is still unreachable (fail-open). Claude Code's own auto-update hook expects `git` and `curl` — if absent, the self-update is silently skipped. There is no declared Node-version floor.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — there is no `bin/` directory and no user-invokable CLI. The only cross-platform wrapper is `hooks/run-hook.cmd`, a polyglot CMD/bash file used internally by the `SessionStart` hook to locate Git-Bash on Windows.
- **`bin/` files**: none
- **Shebang convention**: `#!/usr/bin/env node` for every JS hook; `#!/usr/bin/env bash` for `hooks/session-start`. `run-hook.cmd` uses the `: << 'CMDBLOCK' … CMDBLOCK` polyglot trick (no shebang).
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` (Claude) / `${CURSOR_PLUGIN_ROOT}` (Cursor); Codex bash-launchers compute plugin root by trying `$HOME/.codex/superpowers-optimized`, `$HOME/.codex/superpowers`, `readlink` on `~/.codex/hooks.json`, then a `find` in `~/.codex/plugins/cache`
- **Venv handling (Python)**: not applicable — no Python
- **Platform support**: cross-platform via the CMD/bash polyglot wrapper. `hooks/run-hook.cmd` searches `C:\Program Files\Git\bin\bash.exe`, `C:\Program Files (x86)\Git\bin\bash.exe`, then `bash` on PATH; silently succeeds if none found. `.gitattributes` pins LF line endings for `.sh`, `.cmd`, `hooks/session-start`, and text files.
- **Permissions**: not applicable (no `bin/`). Hooks are invoked via `node <path>` from `hooks.json`, so file mode does not matter.
- **SessionStart relationship**: `run-hook.cmd session-start` is the Claude Code entry point — the wrapper forwards to `hooks/session-start` (bash) which injects `using-superpowers` routing + `project-map.md` content + update notice
- **Pitfalls observed**: hook scripts deliberately use extensionless filenames (e.g. `session-start`, not `session-start.sh`) so Claude Code's Windows auto-detection does not prepend `bash` to any command containing `.sh`. This is an observed platform workaround documented in `run-hook.cmd`'s own comments.

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable. The plugin does use env-var-based knobs — `SP_NO_COMPRESS=1` and `SUPERPOWERS_AUTO_UPDATE=0|1` and `~/.config/superpowers/update.conf` — but these are read directly by the hooks, not declared as `userConfig`
- **Pitfalls observed**: the env-var-only configuration surface means knobs are documented only in the README and hook source, not in any JSON schema; tooling cannot discover them.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 3 entries in `hooks.json`:
  - `matcher: "Bash"` → `hooks/safety/block-dangerous-commands.js` (30+ destructive-command patterns, 3-tier severity)
  - `matcher: "Read|Edit|Write|Bash"` → `hooks/safety/protect-secrets.js` (50+ file patterns + 14 content patterns for hardcoded API keys/tokens/PEM/connection strings)
  - `matcher: "Bash"` → `hooks/bash-compress-hook.js` (rewrites noisy Bash to run through the optimizer; never compresses diffs/reads/failed commands; 76 % reported token savings)
- **PostToolUse hooks**: 2 entries:
  - `matcher: "Edit|Write"` → `hooks/track-edits.js` (logs file changes for TDD reminders; auto-appends `project-map.md`, `session-log.md`, `state.md` to `.gitignore` on first write)
  - `matcher: "Skill"` → `hooks/track-session-stats.js` (skill-invocation telemetry)
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: stdout JSON only — hooks emit `{}` on non-action paths and `{ hookSpecificOutput: { additionalContext: … } }` when injecting context. No structured stderr convention observed in the files sampled.
- **Failure posture**: fail-open documented explicitly (`bash-compress-hook.js` header: "Fail-open: any error results in the original command running unmodified"). `context-engine.js` header: "Fails silently on any error — never blocks session start". The safety hooks (`block-dangerous-commands`, `protect-secrets`) presumably fail-closed when a pattern matches but fail-open on unexpected errors — not directly verified in this pass.
- **Top-level try/catch wrapping**: not directly verified beyond the documented fail-open posture
- **Pitfalls observed**: three separate PreToolUse hooks all matching `Bash` run sequentially on every Bash call, so latency/cost compounds. `hooks.json` keys are PascalCase (`SessionStart`, `PreToolUse`, …) for Claude but Cursor's `hooks-cursor.json` uses camelCase (`sessionStart`, `preToolUse`) — confirms the two runtimes have different event-name casing.

## 10. Session context loading

- **SessionStart used for context**: yes — two SessionStart hooks: the bash `session-start` (synchronous, via `run-hook.cmd`) injects routing/map/update-notice, and `context-engine.js` (async) writes `context-snapshot.json`
- **UserPromptSubmit for context**: yes — `skill-activator.js` emits `hookSpecificOutput.additionalContext` with skill hints + memory recall from `session-log.md` when confidence threshold is met
- **`hookSpecificOutput.additionalContext` observed**: yes — at `hooks/session-start:459` and `hooks/skill-activator.js:406-408` (both fetched). The bash session-start prints `{ "hookSpecificOutput": { "hookEventName": "SessionStart", "additionalContext": "..." } }` on stdout.
- **SessionStart matcher**: `startup|clear|compact` (on the primary synchronous `session-start` entry). The second SessionStart entry (`context-engine.js`, async) has **no matcher** — it fires on all sub-events including `resume`. This is the sub-event-matcher pattern called out in the task prompt. Codex uses `"matcher": "startup|resume"` instead, since Codex lacks `clear`/`compact` sub-events.
- **Pitfalls observed**: having two SessionStart entries, one matcher-scoped and one unscoped, means a `resume` event triggers only the async context-engine, not the synchronous routing injection — intentional per the architecture (resume already has routing in context). This is the only sampled repo using the `startup|clear|compact` pattern.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: "monitors" as a component type are not used here; the plugin's equivalent of passive observation is the hook set (PostToolUse + Stop + SubagentStop).

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace, so plugin-prefixed tags are not needed. Tags are plain `vX.Y.Z`.
- **Pitfalls observed**: the plugin is a self-contained monolith with no cross-plugin dependencies.

## 13. Testing and CI

- **Test framework**: bash scripts (under `tests/claude-code/`), plus a Python token-usage analyzer (`tests/claude-code/analyze-token-usage.py`). Files observed: `run-skill-tests.sh`, `test-helpers.sh`, `test-subagent-driven-development.sh`, `test-subagent-driven-development-integration.sh`, `test-subagent-hook-scope.sh`, `analyze-token-usage.py`
- **Tests location**: `tests/` at repo root, with platform-specific subdirs (`tests/claude-code/`, `tests/codex/`, `tests/opencode/`, `tests/smart-compress/`, `tests/skill-triggering/`, `tests/subagent-driven-dev/`, `tests/explicit-skill-requests/`)
- **Pytest config location**: not applicable — no pytest
- **Python dep manifest for tests**: not applicable — the single Python file is a standalone analyzer with no dependency manifest
- **CI present**: no — `.github/` has only `FUNDING.yml` and `ISSUE_TEMPLATE/`; no `.github/workflows/` directory exists
- **CI file(s)**: none
- **CI triggers**: not applicable
- **CI does**: not applicable
- **Matrix**: not applicable
- **Action pinning**: not applicable
- **Caching**: not applicable
- **Test runner invocation**: bash `tests/claude-code/run-skill-tests.sh` (read-only observation of the file listing; not executed)
- **Pitfalls observed**: no automated CI means release/validation is fully manual. The only observed "validation" is `hookbridge compile` (external tool referenced by the `plugin.universal.yaml` header) plus whatever the maintainer runs locally. Given the version sprawl across five files + yaml and the observed `plugin.universal.yaml` version drift (6.5.2 vs 6.6.0), this is a visible quality-gap.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: manual — maintainer creates GitHub releases by hand (`v6.6.0`, `v6.5.2`, … with release notes). 15 tags observed, 5 most-recent releases confirmed published 2026-04-07 through 2026-04-15 (high cadence).
- **Tag-sanity gates**: none (no CI)
- **Release creation mechanism**: `gh release create` or GitHub UI (not verifiable without write access; inferred from tag-then-release cadence)
- **Draft releases**: no — every recent release is `draft: false, prerelease: false`
- **CHANGELOG parsing**: no dedicated `CHANGELOG.md`. A top-level `RELEASE-NOTES.md` exists (116 KB — unusually large; the `session-start` hook reads it on update to surface "What's New" to the user).
- **Pitfalls observed**: `RELEASE-NOTES.md` is 116 KB. The `session-start` script extracts the current release's section and injects it as `additionalContext` on update — an inline release-notes-as-context pattern not seen elsewhere in this sample. Big file means the hook's extraction logic has to be correct or it will flood the prompt.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: no
- **Hooks.json validation**: no — `hooks.json` and `codex-hooks.json` are hand-maintained (compiled from `plugin.universal.yaml` by the external `hookbridge` tool — see README "Modifying hooks" section: "Hook files (hooks/hooks.json, hooks/codex-hooks.json, .claude-plugin/plugin.json, .codex-plugin/plugin.json) are generated — never edit them directly.")
- **Pitfalls observed**: `hookbridge` is described as the compiler, but the repo does not vendor it, does not pin a version, and does not run it in CI. A contributor editing `plugin.universal.yaml` must install the external tool manually. This places the single-source-of-truth invariant on a user-side build step with no verification.

## 16. Documentation

- **`README.md` at repo root**: present (~43 KB — unusually thorough; covers research motivation, skill catalog, hook inventory, memory stack, install/update/uninstall for Claude/Cursor/Codex/OpenCode, and "Claude Opus 4.6's honest take" testimonial)
- **`README.md` per plugin**: not applicable — single-plugin repo
- **`CHANGELOG.md`**: absent; replaced by `RELEASE-NOTES.md` (116 KB, free-form "What's New" sections consumed by the session-start hook)
- **`architecture.md`**: not at repo root; `docs/architecture/` is a directory (listing not fully traversed). `docs/architecture/smart-compress.md` is referenced from the README.
- **`CLAUDE.md`**: absent at root. README sidebars on the `claude-md-creator` skill and on minimal context files imply the plugin deliberately does not ship its own `CLAUDE.md`. `docs/AGENTS.minimal.md` is present (1.2 KB) as a template for users.
- **Community health files**: `.github/ISSUE_TEMPLATE/` directory (contents not traversed). `.github/FUNDING.yml` present (funds `REPOZY`). No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` at the top-level tree.
- **LICENSE**: present (MIT, SPDX `MIT`)
- **Badges / status indicators**: observed — README opens with shields.io badges for GitHub stars, Version, MIT License, and an Install CTA
- **Pitfalls observed**: `README.md` doubles as marketing and technical reference; some sections (research citations, Claude-Opus quote) are unusual for a plugin README and drive the file past 40 KB. `RELEASE-NOTES.md` at 116 KB is an order of magnitude larger than any sampled `CHANGELOG.md` — this is the inline-release-notes-as-SessionStart-context trade-off in §14.

## 17. Novel axes

- **Sub-event matchers on SessionStart (`"matcher": "startup|clear|compact"`)** — only sampled repo observed using Claude Code's newer SessionStart sub-event filter. Scopes the expensive routing+map injection to real new sessions (`startup`) or context-pruning events (`clear`, `compact`) and excludes `resume`, where routing is already in context. A second unscoped SessionStart entry runs the cheap async `context-engine.js` on every sub-event including `resume`. Worth a row in the pattern doc's §10 Session Context Loading section.
- **Release-notes injected into SessionStart `additionalContext`** — `RELEASE-NOTES.md` is 116 KB, and `hooks/session-start` extracts the current release's "What's New" after a successful fast-forward merge and injects it inline via `hookSpecificOutput.additionalContext`. A self-announcing upgrade pattern. Not seen in other sampled repos and worth calling out in §14.
- **Self-update-from-SessionStart hook** — the `session-start` bash script runs `git fetch` + `git merge --ff-only origin/main` when the plugin is a git clone (Codex/OpenCode/self-hosted), cached 24 h, with opt-out via `SUPERPOWERS_AUTO_UPDATE=0` or `~/.config/superpowers/update.conf`. For marketplace installs (Claude/Cursor) the same hook instead emits a visible "run `/plugin update`" notice. Two install modes handled by one hook.
- **Polyglot CMD/bash `run-hook.cmd` wrapper** — single file interpreted differently by `cmd.exe` (Windows batch) vs. `bash` (via the `: << 'CMDBLOCK' … CMDBLOCK` trick). Uses extensionless hook filenames (`session-start`, not `session-start.sh`) to dodge Claude Code's Windows auto-detect that prepends `bash` to any `.sh` command. Documented directly in the file header.
- **`plugin.universal.yaml` single-source-of-truth compiled by external `hookbridge` tool** — one YAML compiles into 4 platform-specific artifacts (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `hooks/hooks.json`, `hooks/codex-hooks.json`). Documented in the yaml header and README "Modifying hooks" section. The compiler (`REPOZY/Hookbridge`) is an external companion repo, not vendored or version-pinned. Drift already observed (universal yaml at `6.5.2`, everything else at `6.6.0`).
- **Four-file cross-session memory stack** — `context-snapshot.json` (auto, git blast radius), `project-map.md` (structure cache), `session-log.md` (decision history), `state.md` (task snapshot), `known-issues.md` (error→solution map). The stack is auto-appended to `.gitignore` on first write by `track-edits.js`. Novel user-facing design surface.
- **Multi-runtime single-repo manifest layout** — the same repo hosts `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, and `.opencode/` top-level directories with per-runtime manifests. Cursor hooks use camelCase (`sessionStart`, `preToolUse`) and `${CURSOR_PLUGIN_ROOT}`, Claude hooks use PascalCase (`SessionStart`, `PreToolUse`) and `${CLAUDE_PLUGIN_ROOT}`, Codex hooks inline a bash multi-location discovery routine (no env var). Dev branch also adds a top-level `commands/` directory — potential future component type.
- **Zero-dependency hook philosophy** — hooks are explicitly capped at Node built-ins (`fs`, `path`, `crypto`, `child_process`) to avoid any install step. Documented in `context-engine.js` ("Zero dependencies") and enforced by the absence of any `package.json`.
- **Env-var + INI-config knob pattern** — `SP_NO_COMPRESS=1`, `SUPERPOWERS_AUTO_UPDATE=0|1`, and `~/.config/superpowers/update.conf` with an `auto_update=false` key parsed by awk in the bash hook. No `userConfig` declaration — the knob surface is discoverable only via README and source.
- **Fork-provenance preserved in every author field** — every `plugin.json` / marketplace.json `author.name` reads `"Jesse Vincent, forked by REPOZY"`. Attribution convention worth noting for repos derived from well-known upstream sources.

## 18. Gaps

- **`docs/architecture/*` contents** — directory listed but not enumerated. A single read of `docs/architecture/smart-compress.md` (referenced from the README) would confirm the architecture-doc pattern and whether a proper `architecture.md` exists. Source: `gh api repos/REPOZY/superpowers-optimized/contents/docs/architecture`.
- **Top-level `docs/superpowers-optimized/` and `docs/platforms/`** — listed but not read. May contain per-platform install docs duplicating `.codex/INSTALL.md` / `.opencode/INSTALL.md`.
- **Full `RELEASE-NOTES.md` extraction format** — confirmed the hook injects "What's New" from this file, but the section-selection logic was not read. Source: `hooks/session-start` lines past ~460 (only head fetched).
- **`protect-secrets.js` and `block-dangerous-commands.js` fail-closed behavior** — documented fail-open for `bash-compress-hook.js` and `context-engine.js`, but not directly verified for the two safety hooks. Would require reading the top-level try/catch structure of each.
- **`.opencode/plugins/` contents** — OpenCode install uses a symlink to `$plugin_root/.opencode/plugins/superpowers-optimized.js`, but this JS file was not fetched. Would reveal whether OpenCode uses the same Node hooks or a bespoke plugin API.
- **Sub-event matcher behavior on `resume`** — inferred from hook structure (unscoped SessionStart fires, scoped does not) but not verified by reading Claude Code docs against the observed JSON. The context docs under `research/claude-marketplace/context-resources/docs-hooks.md` could confirm.
- **`dev` branch's `commands/` tree** — listed in the dev tree but not traversed. If it contains slash-command definitions, it signals the plugin is adding a commands component in the next release.
- **`agents/code-reviewer.md` full body** (1.4 KB) and `red-team.md` (9 KB) — frontmatter + first portion read; the red-team attack-categories section was truncated. Relevant to the "agent frontmatter conventions" pattern row.
- **`lib/` directory purpose** — listed at the root tree as `tree`, contents not fetched.
- **Windows-specific hook paths** — `fix/windows-*` branches show active Windows support work. The current `run-hook.cmd` behavior was read, but the Codex-on-Windows story (README notes "For live Codex hooks, use codex-cli 0.118.0+ … non-Windows environment") was not traced into source.
