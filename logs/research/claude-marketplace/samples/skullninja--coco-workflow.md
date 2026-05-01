# skullninja/coco-workflow

## Identification

- **URL**: https://github.com/skullninja/coco-workflow
- **Stars**: 6
- **Last commit date**: 2026-04-19 (v0.2.4 tag on default branch HEAD)
- **Default branch**: main
- **License**: MIT (LICENSE present, SPDX `MIT`)
- **Sample origin**: bin-wrapper
- **One-line purpose**: Autonomous spec-driven development plugin — from PRD through merged/reviewed code — with a dependency-aware bash/jq tracker, zero deps beyond bash + jq.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (self-hosted pattern — repo is both marketplace and plugin source).
- **Marketplace-level metadata**: top-level `name` (`coco-local`), `version` (`0.2.4`), `author`, `repository`, `owner.name`. No `metadata.{description,version,pluginRoot}` wrapper.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: none — plugin entry has only `name`, `source`, `description`. No `category`, `tags`, or `keywords` anywhere in the marketplace manifest or plugin.json. GitHub repo topics compensate (ai-coding, claude-code-plugin, spec-driven-development, etc.) but aren't surfaced in the manifest.
- **`$schema`**: absent.
- **Reserved-name collision**: no.
- **Pitfalls observed**: marketplace `version` (0.2.4) is duplicated in plugin.json (0.2.4) — two places to keep in sync; no automation observed to enforce parity. Install slug is `coco@coco-local` in the developer's own .claude/settings but users install as `coco@coco-workflow` per README and v0.2.4 release notes — slug depends on how the user named the marketplace when adding it (`/plugin marketplace add skullninja/coco-workflow` produces `coco-workflow`), so the marketplace-level `name` field ("coco-local") is effectively unused by end users and only shows up in the author's own `scripts/setup.sh` migration logic.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./"`) — plugin lives at repo root, marketplace manifest points to same repo.
- **`strict` field**: default (implicit true) — no explicit strict flag.
- **`skills` override on marketplace entry**: absent.
- **Version authority**: both — `.claude-plugin/plugin.json` carries `"version": "0.2.4"` and `.claude-plugin/marketplace.json` carries `"version": "0.2.4"` at the top level (not per-entry). Drift risk exists but both are hand-edited together in release commits (observed at v0.2.4 HEAD).
- **Pitfalls observed**: the two version fields are not validated against each other in any workflow. A patch release that forgets one field would ship inconsistent metadata.

## 3. Channel distribution

- **Channel mechanism**: no split — single main branch, users pin via `@ref` if desired but README prescribes unpinned install (`/plugin install coco@coco-workflow`).
- **Channel-pinning artifacts**: absent — no `stable-*`/`latest-*` branches or duplicated manifests.
- **Pitfalls observed**: none — single-channel is consistent with the repo's small size and tagging on main.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: on main — every tag (v0.1.0 through v0.2.4) points at a commit on main; no release branches.
- **Release branching**: none (tag-on-main).
- **Pre-release suffixes**: none observed — all tags are `vX.Y.Z` without `-rc`/`-beta`.
- **Dev-counter scheme**: absent — no `0.0.z` dev counter; versions are real semver bumped at tag time.
- **Pre-commit version bump**: no — git-hooks/pre-commit.sh is a project-side hook (build check + UI change detection via `.coco/config.yaml`) installed into host projects, not a version-bumping hook on this repo.
- **Pitfalls observed**: release cadence is rapid (v0.2.1–v0.2.4 within a single day, 2026-04-19) and each is a bugfix for the previous — suggests absence of pre-release/staging discipline. No CI means no objective gate between "tagged" and "released."

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — plugin.json contains only `name`, `version`, `description`, `author`. No explicit `commands`, `skills`, `agents`, or `hooks` arrays; Claude Code auto-discovers by directory convention. v0.2.1 release notes explicitly call out removing "invalid auto-discovery fields" after the validator was tightened.
- **Components observed**:
    - skills: yes (6 — design, execute, hotfix, import, interview, tasks — all single-file SKILL.md, no supporting files)
    - commands: yes (13 — setup, prd, roadmap, phase, loop, execute, constitution, dashboard, status, standup, sync, planning-session, planning-triage)
    - agents: yes (3 — code-reviewer, task-executor, pre-commit-tester)
    - hooks: yes (`hooks/hooks.json` + three `hooks/scripts/*.sh`)
    - .mcp.json: no
    - .lsp.json: no
    - monitors: no
    - bin: yes (`bin/coco-tracker` — the sample-origin artifact)
    - output-styles: no
- **Agent frontmatter fields used**: `name`, `description` (embedded `<example>` blocks in prose), `model` (sonnet for task-executor, opus for code-reviewer and pre-commit-tester), `color`, and — distinctively — `isolation: worktree` on task-executor. No `tools`, `skills`, `memory`, or `background` fields.
- **Agent tools syntax**: not applicable — no `tools` frontmatter on any agent; agents inherit default tool access.
- **Pitfalls observed**: `isolation: worktree` on task-executor assumes Claude Code's worktree isolation feature — if a client doesn't support it, parallel execution silently becomes serial (README treats it as fundamental to `loop.parallel`). Also, `description` fields embed XML-ish `<example>` blocks inline in YAML strings — readable but depends on the platform not stripping or parsing them.

## 6. Dependency installation

- **Applicable**: no — pure bash/jq content. README's headline sell is "Zero dependencies beyond bash + jq." No Python package installs, no npm packages, no binary downloads. The plugin requires `bash 4+`, `jq 1.6+`, `git`, and optionally `gh` — all expected to be present on the user's system.
- **Dep manifest format**: none.
- **Install location**: not applicable.
- **Install script location**: `scripts/setup.sh` exists but it configures the *host project* (creates `.coco/` directory, installs git hooks into host, merges `.claude/settings.json` permissions) — it does not install plugin dependencies. Run manually or auto-invoked via `/coco:setup` slash command.
- **Change detection**: not applicable.
- **Retry-next-session invariant**: not applicable.
- **Failure signaling**: `scripts/setup.sh` uses `set -euo pipefail`; `hooks/scripts/*.sh` use `set -u` only and always `exit 0` (never block tool execution — v0.2.2 changelog explicitly pivoted from prompt-type to command-type hooks to avoid spurious blocking).
- **Runtime variant**: not applicable.
- **Alternative approaches**: none — the zero-deps stance is the design. PEP 723 / uv / npx are not used.
- **Version-mismatch handling**: none (no deps).
- **Pitfalls observed**: system-tool requirements (bash 4+, jq 1.6+, optionally gh) are stated only in README Requirements and CONTRIBUTING prerequisites — there is no runtime probe in `bin/coco-tracker` or `lib/tracker.sh` that checks versions before use. Older macOS ships bash 3.2 by default; failure mode would be cryptic.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — `bin/coco-tracker` is the sample origin and is the linchpin of the v0.2.4 release.
- **`bin/` files**:
    - `coco-tracker` — thin bash wrapper that `exec`s `lib/tracker.sh` with all args; intended to be placed on PATH by Claude Code plugin loader and invoked as the bare command `coco-tracker` from every command, skill, and agent markdown.
- **Shebang convention**: `#!/usr/bin/env bash`.
- **Runtime resolution**: script-relative only — no `${CLAUDE_PLUGIN_ROOT}` reference, no fallback layer. The wrapper is a minimalist 6-liner:

    ```
    #!/usr/bin/env bash
    # coco-workflow tracker wrapper.
    # Resolves tracker.sh relative to itself so callers don't need CLAUDE_PLUGIN_ROOT.
    set -u
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    exec bash "$SCRIPT_DIR/../lib/tracker.sh" "$@"
    ```

    The comment explicitly frames the decision: script-relative resolution so callers (command/skill markdown) don't need the env var. v0.2.4 release notes document the motivation — `${CLAUDE_PLUGIN_ROOT}` is only exported to hook subprocesses, so the older `bash "${CLAUDE_PLUGIN_ROOT}/lib/tracker.sh"` form broke when invoked from a command/skill markdown context. The wrapper fix collapses the whole class of resolution bugs.
- **Venv handling (Python)**: not applicable — pure bash + jq.
- **Platform support**: nix-only (POSIX + bash 4+) — no `.cmd`, no `.ps1`, no OS detection. `git-hooks/*.sh` and `hooks/scripts/*.sh` are the same shape.
- **Permissions**: 100755 (executable) — confirmed via git tree mode bits.
- **SessionStart relationship**: static — `bin/coco-tracker` is committed in-tree and not populated or rewritten by any hook. `hooks/scripts/session-start.sh` only prints a resume message or an init prompt; `hooks/scripts/pre-compact.sh` uses `${CLAUDE_PLUGIN_ROOT}/lib/tracker.sh` directly (not the wrapper) because hooks run in a subprocess where the env var *is* set — so the hook scripts and the user-facing wrapper correctly use the resolution mechanism appropriate to their callsite.
- **Pitfalls observed**: the v0.2.4 release note itself is the key pitfall — before v0.2.4, the codebase called the tracker via `bash "${CLAUDE_PLUGIN_ROOT}/lib/tracker.sh"` in command/skill markdown, which silently broke because `CLAUDE_PLUGIN_ROOT` is not exported to non-hook subprocesses. The wrapper fix is a clean minimalist model: a single `exec` with `set -u` and script-relative path resolution, ~6 lines, no environment dependencies. The PreToolUse hook in `hooks/hooks.json` hard-blocks any resurrection of the old pattern (`bash "${CLAUDE_PLUGIN_ROOT}/lib/tracker.sh"`, absolute paths, variable assignment, `source`) — an enforcement layer paired with the wrapper so the pattern can't regress. `set -u` without `-eo pipefail` is deliberate — the wrapper intentionally avoids halting before `exec` so trailing args aren't lost; the `exec` itself is the terminal step.

## 8. User configuration

- **`userConfig` present**: no — plugin.json has only `name`, `version`, `description`, `author`.
- **Field count**: none (plugin-level). Host-project configuration lives in `.coco/config.yaml` (populated by `/coco:setup` or `scripts/setup.sh`), but this is the plugin's own runtime data file, not Claude Code's `userConfig` mechanism.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable at the plugin level. `config/coco.default.yaml` is a richly commented YAML template (~100 lines, typed by example comments) for `.coco/config.yaml` — but this is host-project config, not userConfig.
- **Reference in config substitution**: not applicable — no `${user_config.KEY}` or `CLAUDE_PLUGIN_OPTION_*` references anywhere.
- **Pitfalls observed**: the plugin chose project-local YAML over Claude Code's `userConfig` mechanism. Trade-off: each new project needs its own `.coco/config.yaml` walk-through (explicit, project-scoped) rather than one-time plugin-level configuration. This fits the spec-driven-development workflow but does mean config cannot be reused across projects without copying `.coco/config.yaml`.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1 — matcher `Bash`, type `prompt` (prompt-type hook whose body is a multi-hundred-word list of blocked Bash patterns and rewrites; Claude evaluates the prompt against the proposed command and responds BLOCK or ALLOW). Purposes: block `cd && compound`, `&&`/`||` chains, `$()` in echo/printf, multiline JSON args to `coco-tracker` (hard block — jq `--argjson` crashes on newlines), `for` loops, piping tracker output to Python, any non-`coco-tracker` invocation of the tracker (no env var paths, no variable assignment, no `source`, no space-separated subcommands).
- **PostToolUse hooks**: 1 — matcher `Write|Edit`, type `command`, runs `hooks/scripts/post-tool-use-quality.sh`. Reads `.coco/config.yaml` for `lint_command` / `typecheck_command` (with `{file}` substitution) and executes them against the modified file. Auto-fix on lint failure if `auto_fix: true`. Silent exit 0 if config missing or quality commands unset. Never blocks.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stderr human-readable for quality hook (lint/typecheck output passed through); silent for session-start/pre-compact when no state; no JSON output. PreToolUse prompt returns prose BLOCK/ALLOW verdict per prompt-hook convention.
- **Failure posture**: mixed per design — PreToolUse/Bash is fail-closed by design (blocking is the whole point); PostToolUse, PreCompact, SessionStart are fail-open (all three scripts exit 0 unconditionally at end, suppress sub-command failures with `|| true`). v0.2.2 and v0.2.3 release notes explicitly document the pivot to fail-open command-type hooks after the v0.2.1 prompt-type handlers caused "stopped continuation" errors in projects without `.coco/config.yaml`.
- **Top-level try/catch wrapping**: not applicable (bash) — instead, defensive `[ -f "$CONFIG_FILE" ] || exit 0` guards at the top of every non-blocking hook.
- **Pitfalls observed**: the PreToolUse prompt is the single largest piece of agent-facing documentation in the plugin (~3 KB of inlined guidance). It is authoritative about *how* to invoke the tracker (bare command `coco-tracker`, hyphenated subcommands, one call per Bash tool call, no multiline JSON args) and duplicates much of the CLAUDE.md guidance. Single source of truth is arguably violated — the CLAUDE.md and the PreToolUse prompt must be kept aligned manually. The `prompt`-type vs `command`-type split was learned expensively across v0.2.1→v0.2.3.

## 10. Session context loading

- **SessionStart used for context**: yes — `hooks/scripts/session-start.sh` prints either a first-run nag (`Coco plugin detected but not initialized. Run /coco:setup to get started.`) or the contents of `.coco/state/session-memory.md` (populated by PreCompact) when present.
- **UserPromptSubmit for context**: no — not configured in `hooks/hooks.json`.
- **`hookSpecificOutput.additionalContext` observed**: no — the script writes plain markdown to stdout (which Claude Code surfaces to the agent at session start) rather than using the structured JSON additionalContext mechanism.
- **SessionStart matcher**: none — no matcher field, so fires on all SessionStart sub-events (startup, clear, compact).
- **Pitfalls observed**: PreCompact writes session state (`.coco/state/session-memory.md`) only when `${CLAUDE_PLUGIN_ROOT}` is set and `lib/tracker.sh` exists under that root; SessionStart reads from `.coco/state/session-memory.md` without using the env var. This asymmetry is intentional (hooks run with the env var, startup may not) but means a crash mid-session can leave stale memory readable at next startup. No TTL or staleness check in session-start.sh — the file is read as-is.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: not applicable — monitors not used. Long-running state surfacing is handled instead by `/coco:dashboard`, `/coco:status`, and `/coco:standup` slash commands (agent-invoked, not Claude-Code-scheduled).

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace, tags are `v{version}` (e.g., `v0.2.4`) without plugin-name prefix.
- **Pitfalls observed**: none — single plugin, no cross-plugin deps.

## 13. Testing and CI

- **Test framework**: bash scripts — `tests/test-tracker.sh` is a hand-rolled harness with `assert_eq`, `assert_contains`, `assert_not_null` helpers; CONTRIBUTING cites "46 tests should pass."
- **Tests location**: `tests/` at repo root (single file).
- **Pytest config location**: not applicable (no Python).
- **Python dep manifest for tests**: not applicable.
- **CI present**: no — no `.github/workflows/` directory (root tree confirms only `.github/CODEOWNERS`).
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable — tests are documented as "run `bash tests/test-tracker.sh` locally, all 46 should pass."
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: direct `bash tests/test-tracker.sh` (also allowlisted as a permission in `.claude/settings.json`).
- **Pitfalls observed**: the absence of CI means the v0.2.1→v0.2.2→v0.2.3→v0.2.4 cascade of same-day bugfix releases (hook type thrashing, then the PATH wrapper fix) could have been caught by a modest smoke test running `coco-tracker list --json` in a host-project fixture. The existing test suite exercises `lib/tracker.sh` directly by sourcing it (bypasses `bin/coco-tracker` entirely), so the wrapper path that actually broke in v0.2.3 was untested.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable — releases are hand-cut via `gh release create` or web UI (v0.2.4 release was published 2026-04-19 at 20:13Z, tagged the same minute the commit landed).
- **Automation shape**: manual `gh release` — release bodies are hand-written "Fixes" / "What's Changed" markdown; body content is the only release artifact (no attached tarballs/zips beyond GitHub's auto-generated source archives).
- **Tag-sanity gates**: none — no automation verifies `plugin.json` version == tag, or that the tag is on main.
- **Release creation mechanism**: `gh release create` (or equivalent web UI) — no `softprops/action-gh-release` / `release-please` / `semantic-release`.
- **Draft releases**: no.
- **CHANGELOG parsing**: not applicable — no `CHANGELOG.md` file; release notes are written directly into the GitHub release body.
- **Pitfalls observed**: without automation, the version in `marketplace.json` and `plugin.json` and the tag name are three fields that must be edited in sync by hand. No evidence of drift at HEAD but the exposure is real; a single-line CI check would eliminate the class.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable — no manifest validator, no pre-commit hook on this repo, no `claude plugin validate` invocation in any script. The v0.2.1 release notes imply the author discovered manifest-structure requirements by failing install against the validator that ships with Claude Code itself — i.e., validation is externalized to the end-user's `/plugin install` flow.
- **Trigger**: not applicable.
- **Frontmatter validation**: no.
- **Hooks.json validation**: no.
- **Pitfalls observed**: the v0.2.1 release recovered from a plugin-structure mismatch (`plugin.json` at wrong path, `.md` hook files instead of `hooks.json`) that would have been caught pre-publish by a validator. The absence of one puts the burden on users.

## 16. Documentation

- **`README.md` at repo root**: present (~14 KB) — badges, hero image (`assets/coco.png`), installation, architecture table, commands/skills catalog, PR workflow diagram, configuration example.
- **Owner profile README at `github.com/skullninja/skullninja`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: not applicable — single-plugin repo, root README is the plugin README.
- **`CHANGELOG.md`**: absent — change history lives entirely in GitHub release bodies (which are reasonably structured — "Fixes", "What's Changed", "Upgrade" sections — but not present in the repo).
- **`architecture.md`**: absent — architectural content is embedded in `CLAUDE.md` (which doubles as project overview + agent-facing operational reference) and partly in README "How It Works". No dedicated developer-facing architecture document.
- **`CLAUDE.md`**: present at repo root (~16 KB) — mixes project overview, architecture sketch, key-files index, tracker command reference, bash-usage guidelines, and agent-facing operational rules. Dual-purpose.
- **Community health files**: `CONTRIBUTING.md` (~4 KB — prerequisites, getting started, project structure, coding style), `.github/CODEOWNERS` (single-owner: @peckda). No `SECURITY.md`, no `CODE_OF_CONDUCT.md`.
- **LICENSE**: present (MIT, SPDX `MIT`, 1074 bytes).
- **Badges / status indicators**: observed — three shields.io badges (Claude Code plugin, MIT license, "deps: bash + jq").
- **Pitfalls observed**: the CLAUDE.md / README.md / (missing) architecture.md layering overlaps — CLAUDE.md's "Architecture" section and README's "How It Works" describe the same five layers with different framings. There is also a separate `GUIDE.md` (~21 KB) — a long-form workflow guide for humans, not referenced from README prominently. Content is good but the reader has to know to open it. Release bodies are the de-facto CHANGELOG but not cross-linked from README.

## 17. Novel axes

- **Minimalist script-relative bin wrapper**: `bin/coco-tracker` is a ~6-line wrapper that deliberately avoids `${CLAUDE_PLUGIN_ROOT}`, with a comment capturing the rationale ("Resolves tracker.sh relative to itself so callers don't need CLAUDE_PLUGIN_ROOT."). This is a distinct point on the resolution-strategy axis from the common `${CLAUDE_PLUGIN_ROOT}`-with-fallback pattern: it trades one env-var dependency for one dirname-of-bash-source dereference and picks up callsite-independence in return. The decision is paired with a PreToolUse hook that hard-blocks any regression to the env-var form, making the wrapper + hook a complete enforcement unit.
- **PreToolUse prompt-as-policy-engine**: the PreToolUse/Bash hook is `prompt`-type (Claude evaluates the command against a prose rule list and returns BLOCK/ALLOW). This is a distinct pattern from command-type hooks that shell out to a script — it shifts policy enforcement from code to prompt-engineering, with the attendant trade-off (natural-language flexibility, but non-deterministic and adds per-Bash-call latency). The prompt lists not just patterns but the *rewrite* for each, turning the hook into a Bash-style-guide generator rather than a simple gate.
- **Hooks-as-hard-won-pattern history**: the release history v0.2.1→v0.2.2→v0.2.3→v0.2.4 is a concise case study of the `prompt`-type vs `command`-type hook distinction — prompt-type treats output as blocking, command-type does not. The plugin started all hooks as prompt-type, then migrated each non-blocking hook (PostToolUse, PreCompact, SessionStart) to command-type as they caused "stopped continuation" errors. PreToolUse/Bash remained prompt-type because blocking is its job. This pattern — blocking hooks stay prompt, non-blocking hooks become command — is worth codifying.
- **Self-hosted marketplace pattern**: the repo is both marketplace and single plugin (`.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` at the same root; plugin `source: "./"`). User adds the repo as a marketplace (`skullninja/coco-workflow`) and installs the one plugin. Simpler than running a separate aggregator marketplace for a single plugin author.
- **Dual-purpose CLAUDE.md**: CLAUDE.md serves as both project overview (typical README territory) and agent-facing operational reference (Key Files index, bash-usage rules, tracker command catalog, known jq gotchas). Not cleanly separated — likely merits a split into README and CLAUDE but currently functions as a single authoritative context blob.
- **Host-project scaffolding via setup script**: `scripts/setup.sh` / `/coco:setup` don't just configure the plugin — they scaffold the host project (`.coco/` dir, `.coco/config.yaml`, git hooks installed into `.git/hooks/`, permission list merged into host `.claude/settings.json`, `.claude/worktrees/` added to host `.gitignore`). Most plugins leave host-project setup to the user; Coco takes ownership. Migration logic (`coco-workflow@coco-local` → `coco@coco-local` rename) is also embedded.
- **Zero-runtime-dependency stance as brand**: "bash + jq, no daemon, no database, no node_modules" is a load-bearing README badge and readme pitch. This constrains several other axes (no PEP 723 scripts, no npm packages, no binary downloads) in service of a distinctive identity.
- **Worktree isolation declared via agent frontmatter**: `isolation: worktree` on `agents/task-executor.md` is the mechanism by which parallel execution is claimed to work. This is a relatively novel frontmatter field — worth cross-referencing against other multi-agent orchestration plugins.
- **Prompt-type PreToolUse as a lightweight rewrite engine**: the Bash block prompt doesn't just enforce — it teaches. Each blocked pattern has a paired rewrite instruction, so the hook functions as an in-context style-guide rather than a rejection gate. The agent that tries `bash "${CLAUDE_PLUGIN_ROOT}/lib/tracker.sh"` gets told to try `coco-tracker` instead, with no round-trip to the user.

## 18. Gaps

- **`lib/tracker.sh` body beyond the header** — confirmed size (~19 KB) and first 30 lines, but the full topological-sort and id-generation internals were not fetched; a deeper audit would benefit from reading the complete 480-line file.
- **All 13 command markdown files** — spot-read `execute.md`, `loop.md`, and a few others exist but their interior contents, specifically whether any still reference the legacy `bash "${CLAUDE_PLUGIN_ROOT}/lib/tracker.sh"` pattern that v0.2.4 replaced, were not audited. Resolved by `curl`ing each command file or via a ripgrep against the fetched archive.
- **`agents/*.md` interior (beyond frontmatter)** — full bodies not read. Would be resolved by fetching each agent markdown.
- **`GUIDE.md` content** — 21 KB document not fetched; may contain additional configuration or workflow details that shift findings in §8 or §16.
- **`.gitignore` `.claude/*` policy vs `.claude/settings.json`** — `.gitignore` ignores everything under `.claude/` except `settings.json`, which is itself committed. The committed `settings.json` allows permissions including `Bash(bash:*)` (broad) — worth examining whether that is plugin-author convention or test-repo leak. Resolved by reading full setup.sh and diffing it against the committed settings.
- **Commit message convention and `.claude-plugin/` migration history** — only inspected HEAD and v0.2.1 release note summary; the sequence of commits migrating to `.claude-plugin/plugin.json` was not walked. Would be resolved via `gh api repos/.../commits` log.
- **How `bin/` goes on PATH** — CLAUDE.md claims "Claude Code adds [bin/] to PATH automatically" for plugins but this is not verified in this repo's own files (the mechanism is in Claude Code itself). Cross-reference against `docs-plugins-reference.md` in the context-resources bundle would resolve.
- **Behavior of PreToolUse prompt on non-Bash agents or nested Bash calls** — the hook matches `Bash`; whether an agent's shell-outs inside `Task` invocations also trigger it was not verified.
- **Whether `scripts/setup.sh` is intended to be run directly** — the script is in-tree and allowlisted (`Bash(bash:*)`), but the README install flow only mentions `/coco:setup`. Relationship of the two paths (drop-in equivalence? or `scripts/setup.sh` is legacy?) was partially addressed by the setup.sh tail saying "If you installed Coco from the marketplace, you can use /coco:setup instead of this script. Both produce the same result" — confirms they are redundant, but the duplication itself is a finding.
