# Sample

Mirrors of `https://github.com/skullninja/coco-workflow`. Autonomous spec-driven development plugin — from PRD through merged/reviewed code — backed by a dependency-aware bash/jq tracker. MIT-licensed; 6 stars at sample time; current tip is `v0.2.4` (commit 2026-04-19) on the `main` branch with five tags `v0.1.0` through `v0.2.4`.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root with one plugin entry; repo is both marketplace and plugin source. Marketplace-level `name` (`coco-local`), `version` (`0.2.4`), `author`, `repository`, `owner.name` set at the top level. No `metadata.{description, version, pluginRoot}` wrapper. Marketplace-level `name` ("coco-local") is effectively unused by end users — `/plugin marketplace add skullninja/coco-workflow` produces install slug `coco@coco-workflow`, not `coco@coco-local`; the `coco-local` slug appears only in the author's own `scripts/setup.sh` migration logic.

## Plugin source binding

### Relative source pointing to repo root (`./`)

Marketplace entry has `"source": "./"`. Single plugin lives at repo root, marketplace manifest points to same repo.

### `strict` field default

`strict` field absent — implicit-true default. No `skills` override on the marketplace entry.

## Per-plugin discoverability metadata

### No discoverability fields on marketplace entry

Plugin entry has only `name`, `source`, `description`. No `category`, `tags`, or `keywords` anywhere in the marketplace manifest or plugin.json. GitHub repo topics compensate (ai-coding, claude-code-plugin, spec-driven-development, etc.) but are not surfaced in the manifest.

### `$schema` absence on per-plugin manifests

`$schema` is absent on both marketplace.json and plugin.json.

## Version coordination

### Dual-file version (manifest pair)

`.claude-plugin/plugin.json` carries `"version": "0.2.4"` and `.claude-plugin/marketplace.json` carries `"version": "0.2.4"` at the top level. Both are hand-edited together in release commits (observed at v0.2.4 HEAD). No automation validates the two against each other; a release that forgot one would ship inconsistent metadata.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split — single main branch. Users pin via `@ref` if desired, but README prescribes unpinned install (`/plugin install coco@coco-workflow`). No `stable-*`/`latest-*` branches or duplicated manifests. Release cadence at v0.2 was rapid: v0.2.1–v0.2.4 within a single day (2026-04-19), each a bugfix for the previous.

## Tag and release lifecycle

### Tag-on-main, single branch

Default branch `main`. Every tag (v0.1.0 through v0.2.4) points at a commit on main; no release branches.

### Tag-on-main with active cadence (semver discipline)

Tags are real `vX.Y.Z` semver bumped at tag time, no `0.0.z` dev counter. No pre-release suffixes (`-rc`/`-beta`).

## Plugin-component registration

### Default convention discovery

`plugin.json` contains only `name`, `version`, `description`, `author`. No explicit `commands`, `skills`, `agents`, or `hooks` arrays — Claude Code auto-discovers by directory convention. v0.2.1 release notes explicitly call out removing "invalid auto-discovery fields" after the validator was tightened.

## Component composition

### Skills (universal)

6 skills under `skills/` — design, execute, hotfix, import, interview, tasks — all single-file SKILL.md, no supporting files.

### Commands

13 commands under `commands/` — setup, prd, roadmap, phase, loop, execute, constitution, dashboard, status, standup, sync, planning-session, planning-triage.

### Agents

3 agents under `agents/` — code-reviewer, task-executor, pre-commit-tester.

### Hooks

`hooks/hooks.json` plus three handler scripts under `hooks/scripts/` — session-start, pre-compact, post-tool-use-quality.

### bin

`bin/coco-tracker` — the sample-origin artifact; thin bash wrapper exec'ing `lib/tracker.sh`.

### Component types absent across the corpus

No `.mcp.json`, no `.lsp.json`, no monitors, no output-styles.

## Skill authoring conventions

### Standard frontmatter

Skills carry `name`, `description`. No mass-customization of `allowed-tools` or other extended fields on these particular skills.

## Agent declaration conventions

### Standard fields plus model / color

Agent frontmatter uses `name`, `description` (with embedded `<example>` blocks in YAML strings), `model` (sonnet for task-executor, opus for code-reviewer and pre-commit-tester), `color`. No `tools` field — agents inherit default tool access. The `<example>` blocks are XML-ish prose embedded inline; depends on the platform not stripping or parsing the tags.

### `permissionMode: acceptEdits` + worktree isolation

Distinctive `isolation: worktree` field on `agents/task-executor.md`. The README treats this field as fundamental to `loop.parallel` execution; if a client doesn't support worktree isolation, parallel execution silently becomes serial.

## Bin entry mechanism

### Bash thin exec-delegate wrapper

`bin/coco-tracker` is a ~6-line bash wrapper with shebang `#!/usr/bin/env bash`, mode 100755:

```
#!/usr/bin/env bash
# coco-workflow tracker wrapper.
# Resolves tracker.sh relative to itself so callers don't need CLAUDE_PLUGIN_ROOT.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/../lib/tracker.sh" "$@"
```

The comment explicitly frames the decision: script-relative resolution so callers (command/skill markdown) don't need the env var. v0.2.4 release notes document the motivation — `${CLAUDE_PLUGIN_ROOT}` is only exported to hook subprocesses, so the older `bash "${CLAUDE_PLUGIN_ROOT}/lib/tracker.sh"` form broke when invoked from a command/skill markdown context. `set -u` without `-eo pipefail` is deliberate: the wrapper avoids halting before `exec` so trailing args aren't lost; the `exec` itself is the terminal step. The fix is paired with a PreToolUse hook that hard-blocks any resurrection of the old pattern.

### Script-relative shell wrapper

The wrapper resolves `lib/tracker.sh` purely via `cd "$(dirname "${BASH_SOURCE[0]}")" && pwd` then `exec bash "$SCRIPT_DIR/../lib/tracker.sh" "$@"`. No `${CLAUDE_PLUGIN_ROOT}` consultation, no fallback layer, no `${CLAUDE_PLUGIN_DATA}`. Hook scripts (`hooks/scripts/pre-compact.sh`) by contrast use `${CLAUDE_PLUGIN_ROOT}/lib/tracker.sh` directly because hooks run in subprocesses where the env var IS set — so the user-facing wrapper and the hook scripts use the resolution mechanism appropriate to their callsite.

## Cross-platform discipline

### POSIX-only with no Windows story

Bin wrapper is bash with shebang `#!/usr/bin/env bash`; bash 4+ assumed; no `.cmd`/`.ps1`, no OS detection. `git-hooks/*.sh` and `hooks/scripts/*.sh` are the same shape.

## Dependency installation

### Zero-dep system-tool stance (bash + jq only)

README headline: "Zero dependencies beyond bash + jq." No Python package installs, no npm packages, no binary downloads. Plugin requires `bash 4+`, `jq 1.6+`, `git`, optionally `gh` — all expected to be present on the user's system. No PEP 723 / uv / npx.

### No managed install — pure shell/markdown

No managed install path. `scripts/setup.sh` exists but configures the host project (creates `.coco/` directory, installs git hooks into host, merges `.claude/settings.json` permissions) — does not install plugin dependencies. System-tool requirements (bash 4+, jq 1.6+, gh) stated only in README "Requirements" and CONTRIBUTING prerequisites — there is no runtime probe in `bin/coco-tracker` or `lib/tracker.sh` that checks versions before use. Older macOS ships bash 3.2 by default; failure mode would be cryptic.

## Install change detection

### No change detection

Not applicable — no managed install.

## Install failure posture

### Silent failure (no install hook at all)

No managed install hook to fail. `scripts/setup.sh` (host-project scaffolder) uses `set -euo pipefail`; `hooks/scripts/*.sh` use `set -u` only and always `exit 0`.

## Install trigger and lifecycle

### No managed install — pure shell/markdown

The plugin has no SessionStart-driven install or bootstrap; bin wrapper and hooks rely on system-installed bash + jq.

## Tool-use enforcement

### Hard-blocking PreToolUse on commit-shape invariants

PreToolUse hook with matcher `Bash`, `type: prompt` — Claude evaluates the prompt against the proposed Bash command and responds BLOCK or ALLOW. The body is a multi-hundred-word list of blocked patterns and rewrites: block `cd && compound`, `&&`/`||` chains, `$()` in echo/printf, multiline JSON args to `coco-tracker` (hard block — jq `--argjson` crashes on newlines), `for` loops, piping tracker output to Python, any non-`coco-tracker` invocation of the tracker (no env var paths, no variable assignment, no `source`, no space-separated subcommands). Each blocked pattern has a paired rewrite instruction so the hook teaches as it gates.

### Format-then-lint PostToolUse (non-blocking)

PostToolUse with matcher `Write|Edit`, `type: command` — runs `hooks/scripts/post-tool-use-quality.sh`. Reads `.coco/config.yaml` for `lint_command` / `typecheck_command` (with `{file}` substitution) and executes them against the modified file. Auto-fix on lint failure if `auto_fix: true`. Silent `exit 0` if config missing or quality commands unset. Never blocks.

## Hook handler runtime

### Per-hook bash scripts with selective strict mode

PostToolUse, PreCompact, SessionStart handlers are individual bash scripts under `hooks/scripts/`. Use `set -u` only (not `-eo pipefail`) and exit 0 unconditionally; defensive `[ -f "$CONFIG_FILE" ] || exit 0` guards at script top.

## Hook output contract

### Stderr for human display + stdout JSON for harness

Quality hook passes lint/typecheck output through stderr for human display. Session-start/pre-compact run silent when no state. PreToolUse prompt returns prose BLOCK/ALLOW verdicts per prompt-hook convention. No JSON envelopes from the command-type hooks.

## Hook failure posture

### Mixed posture (fail-closed for security, fail-open for context)

PreToolUse `Bash` is fail-closed by design (blocking is the whole point); PostToolUse, PreCompact, SessionStart are fail-open (all three exit 0 unconditionally at end, suppress sub-command failures with `|| true`). v0.2.2 and v0.2.3 release notes explicitly document the pivot to fail-open command-type hooks after v0.2.1's prompt-type handlers caused "stopped continuation" errors in projects without `.coco/config.yaml`.

## Session context loading

### SessionStart prints plain markdown to stdout

`hooks/scripts/session-start.sh` prints either a first-run nag (`Coco plugin detected but not initialized. Run /coco:setup to get started.`) or the contents of `.coco/state/session-memory.md` (populated by PreCompact) when present — plain markdown to stdout that Claude Code surfaces to the agent at session start. No structured `hookSpecificOutput.additionalContext` JSON used.

### PreCompact hook for state-file eviction

PreCompact hook writes session state (`.coco/state/session-memory.md`) only when `${CLAUDE_PLUGIN_ROOT}` is set and `lib/tracker.sh` exists under that root; SessionStart reads from `.coco/state/session-memory.md` without using the env var. The asymmetry is intentional (hooks run with the env var, startup may not) but means a crash mid-session can leave stale memory readable at next startup. No TTL or staleness check in session-start.sh — the file is read as-is.

## SessionStart matcher scope

### Empty matcher (all sub-events)

No `matcher` field on the SessionStart entry — fires on all SessionStart sub-events (startup, clear, compact).

## Live monitoring

### `monitors.json` absent

No `monitors.json`. Long-running state surfacing is handled by `/coco:dashboard`, `/coco:status`, and `/coco:standup` slash commands (agent-invoked, not Claude-Code-scheduled).

## Plugin-to-plugin coordination

### `dependencies` field absent

Single-plugin marketplace, no cross-plugin deps. Tags are `v{version}` (e.g., `v0.2.4`) without plugin-name prefix.

## Testing

### Hand-rolled bash tests

Test framework is bash scripts — `tests/test-tracker.sh` is a hand-rolled harness with `assert_eq`, `assert_contains`, `assert_not_null` helpers. CONTRIBUTING cites "46 tests should pass." Tests live in `tests/` at repo root (single file). Test runner invocation: direct `bash tests/test-tracker.sh` (allowlisted as a permission in `.claude/settings.json`).

### Bash scripts only

Tests are pure bash; no Python, Node, or other runtime. Tests source `lib/tracker.sh` directly and bypass `bin/coco-tracker` — so the wrapper path that broke in v0.2.3 (the `${CLAUDE_PLUGIN_ROOT}` resolution issue) was not exercised by the suite.

## CI workflow shape

### No CI

No `.github/workflows/` directory exists (root tree confirms only `.github/CODEOWNERS`). Tests are documented as "run `bash tests/test-tracker.sh` locally, all 46 should pass." The v0.2.1→v0.2.2→v0.2.3→v0.2.4 same-day bugfix cascade (hook type thrashing, then the PATH wrapper fix) could have been caught by a modest smoke test running `coco-tracker list --json` in a host-project fixture.

## Release automation

### No release automation / manual

No release workflow. Releases are hand-cut via `gh release create` or web UI (v0.2.4 published 2026-04-19 at 20:13Z, tagged the same minute the commit landed). Release bodies are hand-written "Fixes" / "What's Changed" markdown; body content is the only release artifact (no attached tarballs/zips beyond GitHub's auto-generated source archives). No `softprops/action-gh-release` / `release-please` / `semantic-release`. No automation verifies `plugin.json` version == tag, or that the tag is on main — three fields (`marketplace.json` version, `plugin.json` version, tag) must be edited in sync by hand.

## Marketplace validation

### No validation

No validation workflow, no manifest validator, no pre-commit hook on this repo, no `claude plugin validate` invocation in any script. v0.2.1 release notes imply the author discovered manifest-structure requirements by failing install against the validator that ships with Claude Code itself — validation is externalized to the end-user's `/plugin install` flow. v0.2.1 release recovered from a plugin-structure mismatch (`plugin.json` at wrong path, `.md` hook files instead of `hooks.json`) that would have been caught pre-publish by a validator.

## Documentation surface

### Substantial root README + CHANGELOG + community files + badges

Root `README.md` (~14 KB) — badges, hero image (`assets/coco.png`), installation, architecture table, commands/skills catalog, PR workflow diagram, configuration example. Single-plugin repo so root README is the plugin README.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` — change history lives entirely in GitHub release bodies (which are reasonably structured — "Fixes", "What's Changed", "Upgrade" sections — but not present in the repo). No `architecture.md`; architectural content is embedded in `CLAUDE.md` and partly in README "How It Works".

### CLAUDE.md as project-config surface

`CLAUDE.md` at repo root (~16 KB) mixes project overview, architecture sketch, key-files index, tracker command reference, bash-usage guidelines, and agent-facing operational rules. Dual-purpose document — typical README territory plus agent-facing operational reference. CLAUDE.md's "Architecture" section and README's "How It Works" describe the same five layers with different framings.

### Heavy doc surface with meta-project artifacts

A separate `GUIDE.md` (~21 KB) is a long-form workflow guide for humans, not referenced from README prominently. Reader has to know to open it. Release bodies are the de-facto CHANGELOG but not cross-linked from README.

### Badges and status indicators

Three shields.io badges in README — Claude Code plugin, MIT license, "deps: bash + jq".

## Community health files

### LICENSE + CODE_OF_CONDUCT + issue templates

`CONTRIBUTING.md` (~4 KB — prerequisites, getting started, project structure, coding style), `.github/CODEOWNERS` (single-owner: @peckda). No `SECURITY.md`, no `CODE_OF_CONDUCT.md`.

## License declaration

### Single repo-level license

`LICENSE` file present at repo root (MIT, SPDX `MIT`, 1074 bytes).

## User configuration and authentication

### No user-supplied config

`plugin.json` has only `name`, `version`, `description`, `author`. No `userConfig` block. Host-project configuration lives in `.coco/config.yaml` (populated by `/coco:setup` or `scripts/setup.sh`) — but this is the plugin's own runtime data file, not Claude Code's `userConfig` mechanism. `config/coco.default.yaml` is a richly commented YAML template (~100 lines, typed by example comments). Trade-off: each new project needs its own `.coco/config.yaml` walk-through (project-scoped) rather than one-time plugin-level configuration.

## Pre-commit and pre-push hooks (git)

### Absent

`git-hooks/pre-commit.sh` exists but is a *project-side* hook (build check + UI change detection via `.coco/config.yaml`) installed into host projects by `scripts/setup.sh`, not a version-bumping or repo-side hook on this repo.

## Cross-role tools

### Bash

The tracker is bash; bin wrapper is bash; all hook scripts are bash; tests are bash. Bash 4+ assumed.

### `jq`

State manipulation in `lib/tracker.sh` is JSON-via-jq. PreToolUse prompt explicitly hard-blocks multiline JSON args because `jq --argjson` crashes on newlines.

### Git as state substrate

`git-hooks/pre-commit.sh` and `.coco/state/` use git for project-level state surfacing.

### `${CLAUDE_PLUGIN_ROOT}` env var

Used by hook scripts (which run with the env var present); deliberately avoided by the bin wrapper which uses script-relative resolution instead.
