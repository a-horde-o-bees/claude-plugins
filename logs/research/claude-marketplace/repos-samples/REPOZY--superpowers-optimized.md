# Sample

Mirrors of `https://github.com/REPOZY/superpowers-optimized`. Production-grade fork of `obra/superpowers` adding 3-tier workflow routing, safety hooks, red-team adversarial testing, and a cross-session memory stack. Single repo serves Claude Code, Codex, Cursor, and OpenCode runtimes. MIT-licensed; default branch `main`; HEAD `3229d61` at 2026-04-17.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root with one plugin entry pointing at `./`. `metadata.description` wrapper (no `version` or `pluginRoot` under metadata). `owner.name` is `"Jesse Vincent, forked by REPOZY"`. `metadata.pluginRoot` absent. Plugin name (`superpowers-optimized`) matches the marketplace name, producing the documented install command `/plugin install superpowers-optimized@superpowers-optimized`. `$schema` not referenced — marketplace-editor tooling that relies on it will not autocomplete.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`source: "./"` — the plugin is the repo. `strict` field absent (default applies). `skills` override on the marketplace entry absent.

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

All three dimensions populated for the single plugin: `category: productivity`; 10 `keywords` (skills, tdd, debugging, code-review, workflows, agentic, token-efficiency, hooks, safety, subagent); 5 `tags` (superpowers, claude-code, cursor, codex, agent-workflow).

### `$schema` absence on per-plugin manifests

`$schema` absent.

## Version coordination

### Multi-runtime fan-out (single source compiled to N artifacts)

`plugin.universal.yaml` is declared the single source of truth and compiled by an external `hookbridge` tool (`REPOZY/Hookbridge`, not vendored or pinned in this repo) into per-runtime artifacts: `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `hooks/hooks.json`, `hooks/codex-hooks.json`. Five-plus version copies coexist at any time. The compile step is a user-side build no CI verifies — observed drift in practice: `plugin.universal.yaml.meta.version` is at `6.5.2` while every compiled artifact (marketplace.json, the three plugin.json files, root `VERSION` file) is at `6.6.0`.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Single marketplace entry sources `./`. Users pin via `@ref` in standard Claude Code marketplace install. Plain `vX.Y.Z` tags (`v6.6.0` … `v4.2.0`, 15 total) live on `main`. `v6.6.0` points at `0a78a700` on main history, one commit before latest `3229d61` (README-only update). High cadence: v6.0.0 → v6.6.0 within ~1 month per release dates.

### SessionStart self-update

The bash `session-start` hook performs `git fetch` + `git merge --ff-only origin/main` against the plugin's own clone, with a 24h cache and an opt-out env var (`SUPERPOWERS_AUTO_UPDATE=0`) plus `~/.config/superpowers/update.conf` opt-out. Two install modes handled by one hook: when the plugin is a git clone (Codex / OpenCode / self-hosted), the hook auto-updates; when installed via a marketplace (Claude / Cursor), the same hook instead emits a "run `/plugin update`" notice. Effectively a soft auto-update channel for non-marketplace installs.

## Tag and release lifecycle

### Tag-on-main, single branch

Plain `vX.Y.Z` tags on main; no `release/*` branches. `dev` exists as a long-lived working branch (the dev-branch tree adds a `commands/` directory not present on main). 24 non-main branches observed including `feat/*`, `fix/*`, `wip/*`, `feat/codex-*`, `fix/windows-*`. Manual release cadence — maintainer creates GitHub releases by hand. 5 most-recent releases published 2026-04-07 through 2026-04-15 (high cadence). All recent releases are `draft: false, prerelease: false`.

## Plugin-component registration

### Mixed convention per runtime (per-runtime manifests)

`.claude-plugin/plugin.json` carries only metadata fields (name, description, version, author, homepage, repository, license, keywords) — no explicit `skills`/`agents`/`hooks`/`commands` arrays; Claude Code discovers `skills/`, `agents/`, and `hooks/hooks.json` implicitly. The Codex (`.codex-plugin/plugin.json`) and Cursor (`.cursor-plugin/plugin.json`) manifests explicitly set `"skills": "./skills/"` (and `.cursor-plugin` adds `"agents": "./agents/"`) because those runtimes require explicit paths. Same `skills/` tree on disk; multiple manifest views over it. The single source of truth (`plugin.universal.yaml`) compiles to all three.

## Component composition

### Skills (universal)

24 skills under `skills/`.

### Agents

2 agents — `agents/code-reviewer.md` (1.4 KB) and `agents/red-team.md` (9 KB).

### Hooks

`hooks/hooks.json` registers 6 events with 10 hook entries total. Detailed under *Tool-use enforcement* and *Session context loading*.

## Agent declaration conventions

### Minimal frontmatter, parent-session permissions

Both agents declare only `name`, `description`, `model: inherit`, and `memory: user`. No `tools`, `skills`, `background`, `isolation`, or `thinking` fields. Agents inherit the parent session's permissions; no `tools` allow-list.

## Server runtime (MCP)

### No bin entry / direct invocation

No MCP server in this plugin. All hooks are `.js` invoked via `node` or bash scripts; no MCP server runtime applies.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory. The only cross-platform wrapper is `hooks/run-hook.cmd`, used internally by the SessionStart hook to locate Git-Bash on Windows — not a user-facing CLI.

### Polyglot CMD/bash wrapper for cross-platform hook invocation

`hooks/run-hook.cmd` is interpreted differently by `cmd.exe` (Windows batch syntax) and by `bash` (via the `: << 'CMDBLOCK' … CMDBLOCK` heredoc trick). Searches `C:\Program Files\Git\bin\bash.exe`, `C:\Program Files (x86)\Git\bin\bash.exe`, then `bash` on PATH; silently succeeds if none found. Hook script filenames are deliberately extensionless (`session-start`, not `session-start.sh`) to avoid Claude Code's Windows auto-detection prepending `bash` to any `.sh` command. Documented in the file header. `run-hook.cmd session-start` is the Claude Code entry point. `.gitattributes` pins LF line endings for `.sh`, `.cmd`, `hooks/session-start`, and text files.

## Plugin-runtime root resolution

### Cascading multi-host fallback

Codex bash launchers compute plugin root by trying `$HOME/.codex/superpowers-optimized`, `$HOME/.codex/superpowers`, `readlink` on `~/.codex/hooks.json`, then a `find` in `~/.codex/plugins/cache`. Claude uses `${CLAUDE_PLUGIN_ROOT}`; Cursor uses `${CURSOR_PLUGIN_ROOT}`. The same hook code runs under multiple ecosystems via per-runtime resolution.

## Dependency installation

### Zero dependencies / stdlib only

The plugin ships no runtime Python or Node dependencies. All hooks are Node built-ins only. `context-engine.js` header explicitly states "Zero dependencies". `hooks/bash-compress-hook.js` uses only `path`, `fs`, `os`, and a local `./compression-rules.js`. No `requirements.txt`, no `pyproject.toml`, no `package.json` at the plugin root. The plugin requires Node on the user's PATH for most hooks; on Codex, the bash wrapper sources `~/.nvm/nvm.sh` as a fallback and emits `{}` if Node is still unreachable (fail-open). Claude Code's own auto-update hook expects `git` and `curl`; if absent, the self-update is silently skipped. No declared Node-version floor.

## User configuration and authentication

### Env-var + INI-config knob pattern

No `userConfig` declared. Configuration knobs are read directly by the hooks from environment variables (`SP_NO_COMPRESS=1`, `SUPERPOWERS_AUTO_UPDATE=0|1`) and from a user-side INI file (`~/.config/superpowers/update.conf` parsed by awk). The knob surface is documented only in the README and hook source — schema-aware tooling cannot discover it.

## Session context loading

### `additionalContext` payload at SessionStart

The bash `session-start` (synchronous, via `run-hook.cmd`) prints `{ "hookSpecificOutput": { "hookEventName": "SessionStart", "additionalContext": "..." } }` on stdout (line 459) injecting routing, project-map content, and update-notice. The async `context-engine.js` writes `context-snapshot.json` (no matcher — fires on all sub-events including `resume`).

### `UserPromptSubmit` skill-activator with confidence threshold

`skill-activator.js` (registered on `UserPromptSubmit`) emits `hookSpecificOutput.additionalContext` (lines 406-408) with skill hints + memory recall from `session-log.md` when a confidence threshold is met.

### Release-notes-as-context

`RELEASE-NOTES.md` is 116 KB — replaces a conventional `CHANGELOG.md` entirely. The `session-start` hook extracts the current release's "What's New" section after a successful fast-forward merge and injects it inline via `hookSpecificOutput.additionalContext`. Self-announcing upgrade pattern. Section-selection logic must be precise — an off-by-one would flood the prompt with the entire 116 KB file.

## SessionStart matcher scope

### SessionStart sub-event matcher (`startup|clear|compact` excluding resume)

The expensive synchronous `session-start` entry uses `matcher: "startup|clear|compact"` — excludes `resume` (where routing is already in context). A second SessionStart entry (`context-engine.js`, async) has no `matcher` — fires on all sub-events including `resume`. Codex equivalent uses `matcher: "startup|resume"` since Codex lacks `clear`/`compact` sub-events. Two SessionStart entries with different matchers in the same `hooks.json`.

## Tool-use enforcement

### Multi-pattern PreToolUse safety stack

Three PreToolUse entries: `matcher: "Bash"` → `hooks/safety/block-dangerous-commands.js` (30+ destructive-command patterns, 3-tier severity); `matcher: "Read|Edit|Write|Bash"` → `hooks/safety/protect-secrets.js` (50+ file patterns + 14 content patterns for hardcoded API keys / tokens / PEM / connection strings); `matcher: "Bash"` → `hooks/bash-compress-hook.js` (rewrites noisy Bash through an optimizer; never compresses diffs / reads / failed commands; 76% reported token savings). All three matching `Bash` run sequentially on every Bash call. Latency compounds.

### PostToolUse skill telemetry / edit tracking

`matcher: "Edit|Write"` → `hooks/track-edits.js` logs file changes for TDD reminders, auto-appends `project-map.md`, `session-log.md`, `state.md` to `.gitignore` on first write. `matcher: "Skill"` → `hooks/track-session-stats.js` records skill-invocation telemetry.

### Fail-open with always-exit-0

Documented fail-open posture: `bash-compress-hook.js` header reads "Fail-open: any error results in the original command running unmodified"; `context-engine.js` header reads "Fails silently on any error — never blocks session start." The safety hooks (`block-dangerous-commands`, `protect-secrets`) presumably fail-closed when a pattern matches but fail-open on unexpected errors — not directly verified.

## Hook handler runtime

### Node `.mjs` files invoked via `node`

Every hook is a `.js` invoked via `node`, plus bash for `session-start` and the polyglot CMD/bash wrapper `run-hook.cmd`. Every JS hook carries `#!/usr/bin/env node`; `hooks/session-start` uses `#!/usr/bin/env bash`; `run-hook.cmd` uses the polyglot trick (no shebang). Hooks are capped at Node built-ins (`fs`, `path`, `crypto`, `child_process`) by explicit policy — no shared `node_modules/`.

## Hook output contract

### `additionalContext` for context injection

Hooks emit `{}` on non-action paths and `{ hookSpecificOutput: { additionalContext: … } }` when injecting context.

## State persistence

### File-based memory stack with auto-gitignore

Five working-state files at the project root capture cross-session state: `context-snapshot.json` (auto-managed git blast radius), `project-map.md` (structure cache), `session-log.md` (decision history), `state.md` (task snapshot), `known-issues.md` (error→solution map). The stack is auto-appended to `.gitignore` on first write by `track-edits.js`. Read by SessionStart / UserPromptSubmit hooks to re-hydrate context.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. The plugin's equivalent of passive observation is the hook set (PostToolUse + Stop + SubagentStop).

## Plugin-to-plugin coordination

### `dependencies` field absent

No `plugin.json` declares the schema-level `dependencies` field. Self-contained monolith. Plain `vX.Y.Z` tags (no `<plugin-name>--v<version>` format).

## Testing

### Bash scripts under `tests/<platform>/` with no CI

Tests under `tests/claude-code/`: `run-skill-tests.sh`, `test-helpers.sh`, `test-subagent-driven-development.sh`, `test-subagent-driven-development-integration.sh`, `test-subagent-hook-scope.sh`, plus a Python token-usage analyzer `analyze-token-usage.py`. Platform-specific subdirs: `tests/claude-code/`, `tests/codex/`, `tests/opencode/`, `tests/smart-compress/`, `tests/skill-triggering/`, `tests/subagent-driven-dev/`, `tests/explicit-skill-requests/`. Run manually by the maintainer; no GitHub Actions exercise them.

## CI workflow shape

### No CI

`.github/` contains only `FUNDING.yml` and `ISSUE_TEMPLATE/`; no `.github/workflows/` directory. Release/validation is fully manual. The only observed "validation" is `hookbridge compile` (external tool referenced by the `plugin.universal.yaml` header) plus whatever the maintainer runs locally. Given the version sprawl across five files plus YAML and the observed `plugin.universal.yaml` version drift (6.5.2 vs 6.6.0), this is a visible quality gap.

## Pre-commit and pre-push hooks (git)

### Absent

No `.pre-commit-config.yaml` and no `.githooks/` config. `plugin.universal.yaml` is bumped manually and recompiled by `hookbridge compile`.

## Marketplace validation

### No validation

`hooks.json` and `codex-hooks.json` are compiled from `plugin.universal.yaml` by the external `hookbridge` tool — README "Modifying hooks" section reads: "Hook files (hooks/hooks.json, hooks/codex-hooks.json, .claude-plugin/plugin.json, .codex-plugin/plugin.json) are generated — never edit them directly." `hookbridge` is described as the compiler, but the repo does not vendor it, does not pin a version, and does not run it in CI. A contributor editing `plugin.universal.yaml` must install the external tool manually. The single-source-of-truth invariant lives on a user-side build step with no verification.

## Release automation

### No release automation / manual

No `release.yml`. Maintainer creates GitHub releases by hand (`v6.6.0`, `v6.5.2`, … with release notes). 15 tags observed. No tag-sanity gates (no CI). Release creation mechanism is `gh release create` or GitHub UI (inferred from tag-then-release cadence). Every recent release is `draft: false, prerelease: false`.

### `RELEASE-NOTES.md` consumed by SessionStart hook

`RELEASE-NOTES.md` (116 KB) replaces a conventional CHANGELOG. The `session-start` hook reads it on update to extract the current release's "What's New" section and injects it inline as context. No dedicated `CHANGELOG.md`.

## Documentation surface

### Marketing-grade README (40+ KB)

Repo-root `README.md` is ~43 KB — covers research motivation, skill catalog, hook inventory, memory stack, install/update/uninstall for Claude/Cursor/Codex/OpenCode, and "Claude Opus 4.6's honest take" testimonial. Some sections (research citations, third-party LLM quote) are unusual for a plugin README and drive the file past 40 KB. README opens with shields.io badges for GitHub stars, Version, MIT License, and an Install CTA.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` (replaced by `RELEASE-NOTES.md`). No `ARCHITECTURE.md` at repo root. `docs/architecture/` is a directory (listing not fully traversed; `docs/architecture/smart-compress.md` referenced from the README). `docs/AGENTS.minimal.md` is present (1.2 KB) as a template for users.

### No CLAUDE.md

No `CLAUDE.md` at repo root. README sidebars on the `claude-md-creator` skill imply the plugin deliberately does not ship its own `CLAUDE.md`.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` at repo root (MIT, SPDX `MIT`). `plugin.json` declares MIT.

## Community health files

### LICENSE + CODE_OF_CONDUCT + issue templates

`.github/ISSUE_TEMPLATE/` directory (contents not traversed). `.github/FUNDING.yml` present (funds `REPOZY`). No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` at the top-level tree.

## Multi-runtime portability

### Per-runtime manifest directories

Repo hosts `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, and `.opencode/` top-level directories with per-runtime manifests. Cursor hooks use camelCase (`sessionStart`, `preToolUse`) and `${CURSOR_PLUGIN_ROOT}`; Claude hooks use PascalCase (`SessionStart`, `PreToolUse`) and `${CLAUDE_PLUGIN_ROOT}`; Codex hooks inline a bash multi-location discovery routine (no env var). Dev branch also adds a top-level `commands/` directory — potential future component type.

## Cross-ecosystem distribution

### Cross-ecosystem multi-harness distribution

Same plugin payload ships via parallel manifests for Claude Code, Codex, Cursor, and OpenCode. Each runtime reads its own manifest. OpenCode install uses a symlink to `$plugin_root/.opencode/plugins/superpowers-optimized.js`.

## Cross-platform discipline

### Polyglot wrapper for cross-OS hook invocation

`hooks/run-hook.cmd` (see *Bin entry mechanism*) is the cross-platform mechanism. `.gitattributes` pins LF line endings for `.sh`, `.cmd`, `hooks/session-start`, and text files. `fix/windows-*` branches show active Windows support work.

## Author identity and provenance

### Plugin name vs repo name drift

Plugin name `superpowers-optimized` matches the marketplace name and repo name — no drift. However, the repo is a fork of `obra/superpowers` (GitHub API `fork: true`, parent `obra/superpowers`). The README credits `Jesse Vincent, forked by REPOZY`; every `plugin.json` / `marketplace.json` `author.name` reads `"Jesse Vincent, forked by REPOZY"` — fork-attribution discipline preserved across every manifest copy.
