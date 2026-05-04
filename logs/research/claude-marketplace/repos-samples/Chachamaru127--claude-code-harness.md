# Chachamaru127/claude-code-harness

## Identification

- **URL**: https://github.com/Chachamaru127/claude-code-harness
- **Stars**: 568
- **Last commit date**: 2026-04-20 (commit `a6cb97c` on main)
- **Default branch**: main
- **License**: MIT (LICENSE.md at repo root + LICENSE.ja.md Japanese mirror)
- **Sample origin**: primary (community)
- **One-line purpose**: "A harness for solo developers (Vibecoders) to handle full-cycle contract development" — turns Claude Code into a disciplined Plan → Work → Review delivery loop with a Go-native hook engine

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: `metadata.{description}` wrapper (no `version`, no `pluginRoot`) + top-level `name`, `owner.name`, and `plugins[]`
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: keywords + category — `keywords: ["claude-code","plugin","vibecoder","workflow","plan-work-review"]`, `category: "productivity"` (no `tags`)
- **`$schema`**: absent from `marketplace.json` (but `settings.json` carries `"$schema": "https://json.schemastore.org/claude-code-settings.json"`)
- **Reserved-name collision**: no (single-plugin marketplace named `claude-code-harness`, marketplace name `claude-code-harness-marketplace`)
- **Pitfalls observed**: marketplace `description` is localized to Japanese ("配布/導入を支援する…") while per-plugin `description` is English — mixed-language surface inside one manifest

## 2. Plugin source binding

- **Source format(s) observed**: relative — `source: "./"` (plugin root is the repo root)
- **`strict` field**: `true` explicit on the single marketplace entry
- **`skills` override on marketplace entry**: absent — `skills` lives on `plugin.json` as `"./skills/"` (array with one path)
- **Version authority**: **three sources** held in sync — `VERSION` file (plain text, `4.3.3`) is the declared source of truth, `.claude-plugin/plugin.json` mirrors it, and `harness.toml` holds a third copy. `scripts/sync-version.sh check|sync|bump` reconciles all three, enforced by `.githooks/pre-commit` and CI `check-version-bump.sh`. The marketplace entry itself has no `version`, so drift risk is between VERSION/plugin.json/harness.toml only
- **Pitfalls observed**: triple version tracking is unusual — most sampled repos use `plugin.json` alone. `harness.toml` is the source consumed by the Go `harness sync` subcommand that re-emits `plugin.json` / `hooks.json` / `settings.json`, so `plugin.json` is effectively a derived artifact even though it's checked in

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via plugin `/plugin update claude-code-harness` directly from the marketplace at head. README recommends CC v2.1.111+ but no separate stable/latest marketplaces
- **Channel-pinning artifacts**: absent
- **Pitfalls observed**: none observed; CHANGELOG references minimum CC versions per-release rather than branching the marketplace

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main — all 10 inspected releases (`v4.3.3` … `v4.0.0`) have `target_commitish: main` and the tag commits are on main
- **Release branching**: `release/v{x.y.0}-arcana` long-lived branches exist (`release/v4.2.0-arcana`, `release/v4.3.0-arcana`) but they are **behind main, not ahead** — `release/v4.3.0-arcana` is 11 commits behind main and 0 ahead; `v4.3.0` tag itself is 1 commit ahead of the release branch. Prompt's framing ("release/* branches for release cuts") is partially correct but release branches do NOT own tags — they appear to be prep/historical markers that main rebases past. The actual cut lands on main. Additional `chore/v4.3.2-release-complete` and `follow-up/4.3.2-nitpicks` topic branches appear for release-prep workflow
- **Pre-release suffixes**: none observed on v4.x tags; `-arcana` appears only on the long-lived release branches (a release codename, not a semver pre-release suffix)
- **Dev-counter scheme**: absent — `VERSION` holds real semver (`4.3.3`) on main with no 0.0.z dev-counter discipline; main sits at the released version until next bump
- **Pre-commit version bump**: yes — `.githooks/pre-commit` installed by `scripts/install-git-hooks.sh` watches `VERSION` + `.claude-plugin/plugin.json`; on mismatch it runs `sync-version.sh sync` (VERSION is source of truth, plugin.json mirrors) and re-stages. It does NOT auto-bump — bump is manual via `sync-version.sh bump [patch|minor|major]` when cutting a release
- **Pitfalls observed**: release branches are a red herring for "where does the tag live" — tags live on main. The `-arcana` release branches are named release codenames (v4.0 "Hokage", v4.2 "Hokage line", v4.3 "Arcana") and appear to capture a release-prep snapshot that main later evolves past. Only repo in sample using this particular release-codename branch naming

## 5. Plugin-component registration

- **Reference style in plugin.json**: explicit path for skills (`"skills": ["./skills/"]`) and `outputStyles: "./output-styles/"`; agents/hooks/monitors rely on convention-directory auto-discovery (no fields in plugin.json, but directories exist at `agents/`, `hooks/`, `monitors/` and hooks are also explicitly written to `.claude-plugin/hooks.json`)
- **Components observed**:
  - skills: yes (32 skill directories under `skills/`, plus mirrors at `skills-codex/`, `codex/`, `opencode/` for cross-runtime distribution)
  - commands: not observed as a top-level directory (skills replace commands per README "5 Verb Skills")
  - agents: yes (5 — `worker`, `reviewer`, `scaffolder`, `advisor`, `team-composition`)
  - hooks: yes (both `.claude-plugin/hooks.json` 16.8KB comprehensive, and `hooks/hooks.json` parallel copy via `harness sync`)
  - `.mcp.json`: not observed at repo root
  - `.lsp.json`: not observed
  - monitors: yes — `monitors/monitors.json` with one entry (`harness-session-monitor`)
  - bin: yes — `bin/harness` shim plus three committed Go binaries
  - output-styles: yes — `output-styles/harness-ops.md` (single file)
- **Agent frontmatter fields used**: `name`, `description`, `tools` (list form, not permission-rule syntax), `disallowedTools`, `model` (e.g., `claude-sonnet-4-6`, `claude-opus-4-6`), `effort` (`medium`/`xhigh`), `maxTurns`, `permissionMode` (`bypassPermissions`), `color`, `memory: project`, `isolation: worktree` (worker only), `initialPrompt` (literal multi-line block), `skills` (list of skill names the agent can invoke), `hooks` (inline — reviewer has a Stop hook). Notable: uses older `claude-sonnet-4-6` / `claude-opus-4-6` (project is actively migrating to 4-7 per CHANGELOG)
- **Agent tools syntax**: plain tool names in YAML list form (`- Read`, `- Bash`) — NOT permission-rule syntax
- **Pitfalls observed**: `effort: xhigh` on reviewer/advisor requires CC v2.1.111+ — this is the only sampled repo with explicit xhigh effort. Agents mix `memory: project` + `isolation: worktree` (worker) — novel combination. Reviewer's inline `hooks:` block in frontmatter is unusual

## 6. Dependency installation

- **Applicable**: yes — Go binaries are the runtime, but they are committed rather than downloaded, so the "install" is effectively git-checkout
- **Dep manifest format**: `go/go.mod` (go 1.25.0), `go/go.sum`; scripts also use `node` for `build-opencode.js` / `validate-opencode.js` but no `package.json` was observed at root
- **Install location**: binaries live in-repo at `bin/harness-{darwin-arm64,darwin-amd64,linux-amd64}` (~11MB each, checked into git)
- **Install script location**: `go/scripts/build-all.sh` for developer-side build; no runtime install — users get binaries by cloning the plugin via the marketplace
- **Change detection**: n/a for end users (binaries shipped in-tree). CI `validate-plugin.yml` `test-go` job rebuilds on every push to check `go build` + `go test` + `go vet` pass
- **Retry-next-session invariant**: not applicable (no first-session install step)
- **Failure signaling**: `bin/harness` shim exits 0 with stderr diagnostic and empty stdout when platform binary missing ("CC hooks treat it as 'no decision' — proceed normally")  — explicit comment in shim says "Never print JSON here — we don't know which hook/command is being called and emitting the wrong schema breaks the hook protocol"
- **Runtime variant**: Go binary download — but "download" is really "committed in repo"; shim dispatches to platform-specific pre-built binary by `uname -s`/`uname -m`
- **Alternative approaches**: none needed — no Python, uv, npm, npx, uvx surface at runtime. v4.0 "Hokage" README boasts explicit removal of the Node.js dependency that v3 carried
- **Version-mismatch handling**: `go build -ldflags="-X main.version=${VERSION}"` bakes the repo's VERSION file into each binary at build time, so runtime `harness --version` reports the repo's version; Go stdlib statically-linked, `modernc.org/sqlite` pure-Go (`CGO_ENABLED=0`)
- **Pitfalls observed**: shipping 11MB × 3 binaries in the git tree (`bin/harness-*-*`) is unusual — total ~33MB per clone. Only sampled repo that commits pre-built Go binaries rather than downloading them at SessionStart. Single architecture gap: Linux ARM64 and Windows not shipped at all (shim exits silently on unsupported platform)

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes
- **`bin/` files**:
  - `harness` — POSIX shell wrapper that resolves `uname -s`/`uname -m` and `exec`s the matching binary; on mismatch exits 0 silent with stderr diagnostic
  - `harness-darwin-arm64` — compiled Go binary (11MB)
  - `harness-darwin-amd64` — compiled Go binary (12MB)
  - `harness-linux-amd64` — compiled Go binary (11MB)
- **Shebang convention**: `#!/bin/sh` (POSIX, not bash-specific) on the shim
- **Runtime resolution**: script-relative — walks `readlink` chain to find `SCRIPT_DIR`, then constructs `${SCRIPT_DIR}/harness-${OS}-${ARCH}`. Hooks always invoke via `"${CLAUDE_PLUGIN_ROOT}/bin/harness"` so the shim locates its siblings
- **Venv handling (Python)**: not applicable (no Python)
- **Platform support**: darwin-arm64 + darwin-amd64 + linux-amd64 only. Linux-arm64 and Windows not supported — shim silently no-ops (exit 0) with stderr message, so the plugin degrades gracefully to "no guardrails, no errors"
- **Permissions**: 100755 (shim is executable via `exec`); binaries also executable
- **SessionStart relationship**: static — binaries are committed, shim dispatches on every hook invocation. SessionStart hooks themselves call `bin/harness hook session-start` (i.e., consumes the binary rather than building it)
- **Pitfalls observed**: graceful-no-op on unsupported platform is an explicit design choice per comments in `bin/harness` — this is the cleanest "graceful degradation" pattern seen in the sample. But it means a Linux-ARM64 user (e.g., Raspberry Pi, AWS Graviton) silently gets no guardrails with no user-visible warning beyond first-hook stderr

## 8. User configuration

- **`userConfig` present**: no — no `userConfig` block anywhere in `plugin.json` or `marketplace.json`
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable — configuration lives in out-of-band files (`.claude-code-harness.config.yaml`, `harness.toml`) that the Go binary reads directly rather than via CC's `userConfig` substitution surface
- **Reference in config substitution**: neither `${user_config.KEY}` nor `CLAUDE_PLUGIN_OPTION_*` observed
- **Pitfalls observed**: the plugin has an extensive user-configurable surface (review mode, breezing parallelism, advisor thresholds, cleanup policies — see `.claude-code-harness.config.yaml`) but routes it all through an external YAML file rather than CC's native `userConfig`. This decouples config from CC updates but means users can't configure via CC's UI

## 9. Tool-use enforcement

- **PreToolUse hooks**: 4 entries — matcher `Write|Edit|MultiEdit|Bash|Read` (pre-tool router), matcher `AskUserQuestion` (normalize answers), matcher `Write|Edit` (inbox-check + Haiku agent hook for secret/TODO/security review), matcher `mcp__chrome-devtools__.*|mcp__playwright__.*|mcp__plugin_playwright_playwright__.*` (browser-guide). The Haiku-agent PreToolUse is a rare pattern
- **PostToolUse hooks**: 8 entries with matchers `Write|Edit|MultiEdit|Bash`, `Write|Edit` (plus a second Haiku agent), `*`, `Bash`, `Skill|Task|SlashCommand`, `Skill`, `TodoWrite`, `Write|Edit|Task`. Purposes include post-tool router, memory-bridge, commit-cleanup, async ci-status, usage-tracker, clear-pending, todo-sync, emit-trace, auto-cleanup, track-changes, async auto-test, quality-pack, plans-watcher, tdd-check, auto-broadcast
- **PermissionRequest/PermissionDenied hooks**: both observed — `PermissionRequest` matchers `Edit|Write|MultiEdit` and `Bash` (with a very long `if:` clause enumerating allowed bash patterns like `git status`, `npm test`, `pytest`, `go test`); `PermissionDenied` fires `hook permission-denied`
- **Output convention**: not applicable via structured output inspection (all hooks dispatch to the Go `harness` binary via `bin/harness hook <name>`); the shim design says "Never print JSON here — we don't know which hook/command is being called and emitting the wrong schema breaks the hook protocol", so each hook implementation owns its own schema
- **Failure posture**: fail-open by design — shim exits 0 with empty stdout on missing binary, so the CC hook sees "no decision / proceed normally". The Haiku-agent hooks on Write|Edit return JSON `permissionDecision: deny` + `permissionDecisionReason` when they detect issues (secrets/TODO/injection), fail-closed only on judgment-flag
- **Top-level try/catch wrapping**: not directly inspected (Go source not read) but the shim's explicit "exit 0 on any missing-binary path" is the project's visible failure discipline
- **Pitfalls observed**: hook surface is exceptionally broad — 18 distinct hook-events wired (including rare ones: `SubagentStart`, `SubagentStop`, `InstructionsLoaded`, `PostToolUseFailure`, `TeammateIdle`, `TaskCompleted`, `TaskCreated`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `Elicitation`, `ElicitationResult`, `StopFailure`, `ConfigChange`, `CwdChanged`, `FileChanged`). Most sampled repos wire 2-5. Also embeds `type: agent` (Haiku agent) as PreToolUse/PostToolUse/PreCompact/Stop inline prompts — parallel Claude invocation during hook evaluation. `Stop` includes a blocking Haiku agent that reads Plans.md for `cc:WIP` tasks and returns `decision: block` if found — very assertive stop-gating

## 10. Session context loading

- **SessionStart used for context**: yes — `matcher: "startup|resume"` fires three commands: `hook session-start`, `hook memory-bridge`, and `bash scripts/hook-handlers/memory-session-start.sh`. `once: true` prevents duplicate fires
- **UserPromptSubmit for context**: yes — 6 hooks chained (`hook memory-bridge`, `bash scripts/userprompt-inject-policy.sh`, `hook inject-policy`, `hook track-command`, `hook fix-proposal`, `hook breezing-signal`)
- **`hookSpecificOutput.additionalContext` observed**: not directly visible in JSON (Go source not read) but `inject-policy` / `memory-bridge` names strongly imply `additionalContext` injection
- **SessionStart matcher**: `startup|resume` (covers both fresh start and resume from disk; skips `clear` and `compact` deliberately — those are handled by `PreCompact`/`PostCompact`)
- **Pitfalls observed**: `startup|resume` matcher is narrower than the `startup|clear|compact` pattern docs suggest; this is an intentional separation so the PreCompact/PostCompact handlers do compact-context-preservation work. `once: true` on SessionStart hooks is explicit — rare in sample

## 11. Live monitoring and notifications

- **`monitors.json` present**: yes — at `monitors/monitors.json` (canonical location per CC v2.1.105 public spec, per CHANGELOG)
- **Monitor count + purposes**: 1 — `harness-session-monitor` auto-arms session monitoring for harness-mem health, advisor/reviewer state, and Plans.md drift
- **`when` values used**: `always`
- **Version-floor declaration**: README `## Requirements` states "Claude Code v2.1+" with "v2.1.105+ recommended (PreCompact hook + monitors manifest)" — version floor called out explicitly for the monitors feature
- **Pitfalls observed**: monitor command `"${CLAUDE_PLUGIN_ROOT}/bin/harness" hook session-monitor` — reuses the same `hook` subcommand surface as `hooks.json`, meaning monitors and hooks share a single Go binary and subcommand-dispatch plane. CHANGELOG v4.2 entry documents a regression where `harness sync` silently stripped declared `monitors`/`agents` blocks; now has shell + Go struct tests

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace with simple `v{x.y.z}` tag format)
- **Pitfalls observed**: README references an external companion plugin `harness-mem` that integrates via shared protocol rather than declared dependency — "Optional `harness-mem` integration: sessions remember what you worked on last time". Coupling is by runtime detection (`~/.claude-mem/` presence check in v4.3.3 hotfix) rather than by manifest

## 13. Testing and CI

- **Test framework**: multiple — Go `go test` for the core engine; bash test scripts (~60 `tests/test-*.sh` files + `tests/validate-plugin.sh`, `tests/validate-skills.sh`, `tests/validate-plugin-v3.sh`, `tests/test-codex-package.sh`); `tests/unit/`, `tests/integration/`, `tests/fixtures/` subdirectories. Also `scripts/ci/check-consistency.sh`, `scripts/ci/check-version-bump.sh`
- **Tests location**: mixed — Go tests inside `go/` alongside source (`go/pkg/...`, `go/internal/...`); bash validation tests at `tests/` at repo root
- **Pytest config location**: not applicable (no Python test runner)
- **Python dep manifest for tests**: not applicable
- **CI present**: yes
- **CI file(s)**: `.github/workflows/release.yml`, `.github/workflows/validate-plugin.yml`, `.github/workflows/benchmark.yml`, `.github/workflows/opencode-compat.yml`
- **CI triggers**: `validate-plugin.yml` on `pull_request` + `push: branches: [main]`; `release.yml` on `push: tags: ['v*']`; `benchmark.yml` on `workflow_dispatch` with task/trials/mode inputs; `opencode-compat.yml` on path-scoped `push` + `pull_request`
- **CI does**: `validate-plugin.yml` runs `bash scripts/ci/check-version-bump.sh`, installs ripgrep, `bash tests/validate-plugin.sh`, `bash scripts/ci/check-consistency.sh`, `bash tests/test-codex-package.sh` in the `validate` job; separate `test-go` job runs `go build ./cmd/harness/`, `go test ./...`, `go vet ./...` with `actions/setup-go@v5` + go.mod cache
- **Matrix**: none (single Go version from `go.mod`, single runner `ubuntu-latest`)
- **Action pinning**: tag (`actions/checkout@v4`, `actions/setup-go@v5`, `actions/setup-python@v5`, `actions/setup-node@v4`) — no SHA pinning observed
- **Caching**: built-in — `actions/setup-go@v5` with `cache-dependency-path: go/go.sum`; `actions/setup-node@v4` and `actions/setup-python@v5` use their defaults
- **Test runner invocation**: direct `bash` for shell tests, direct `go test` for Go — no wrapper script orchestrates both
- **Pitfalls observed**: ~60 `tests/test-*.sh` files not called by CI individually — `tests/validate-plugin.sh` is the single aggregator. Benchmark workflow requires `ANTHROPIC_API_KEY` secret and runs real Claude Code sessions (`npm install -g @anthropic-ai/claude-code`) with `timeout-minutes: 120` — unusual CI pattern, expensive to run

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes at `.github/workflows/release.yml`
- **Release trigger**: `push: tags: ['v*']`
- **Automation shape**: Go binary cross-build (darwin-arm64, darwin-amd64, linux-amd64) + attach to GitHub Release, with **CHANGELOG awk extraction** for release notes body. Workflow first checks `gh release view "$TAG"` — if release already exists (created by external "release-har" tool), it only uploads/refreshes binaries via `gh release upload --clobber`; if release does NOT exist, acts as "safety-net" by extracting CHANGELOG section and creating the release itself with `gh release create --verify-tag --notes-file`
- **Tag-sanity gates**: `gh release create --verify-tag` verifies the tag object points at the workflow's checked-out commit. No separate verify-tag-on-main or version-equals-tag gate in the workflow itself (the pre-commit hook + `check-version-bump.sh` in `validate-plugin.yml` catch version mismatches upstream)
- **Release creation mechanism**: `gh release create` in the fallback path; "release-har" (an external tool, not observed in this repo — referenced in `.claude/rules/v3-architecture.md`, `README.md`, `scripts/setup-codex.sh` + workflow) creates releases on the primary path
- **Draft releases**: no — inspected releases are all `draft=False`, `prerelease=False`
- **CHANGELOG parsing**: yes — awk script extracts body between `## [VERSION]` and the next `## [` heading:
  ```bash
  BODY=$(awk -v ver="$VERSION" '
    /^## \[/ {
      if (found) exit
      if (index($0, "[" ver "]")) found=1
      next
    }
    found { print }
  ' CHANGELOG.md)
  ```
  Falls back to auto-message if no CHANGELOG entry found. This is the only sampled repo doing awk-based CHANGELOG extraction inside release automation
- **Pitfalls observed**: inspected `v4.3.0`, `v4.3.3` releases have **0 assets attached** — the safety-net Go binary upload step appears not to have run (or the external release-har tool created the release but the workflow's "exists=true" branch's `--clobber` upload silently failed with `|| true`). Despite the workflow building + attaching binaries, the actual binaries consumers see live in-repo at `bin/` rather than as release assets. CHANGELOG.md is **248KB** — awk extraction scales linearly, still feasible. Release body format is prescribed in `.claude/rules/github-release.md` with a Keep-a-Changelog-like `[X.Y.Z] - YYYY-MM-DD` + Before/After table discipline, in Japanese for CHANGELOG and English for the GitHub Release body

## 15. Marketplace validation

- **Validation workflow present**: yes — `validate-plugin.yml`
- **Validator**: bash scripts + Go tests — `tests/validate-plugin.sh` (39-item structural check), `scripts/ci/check-consistency.sh` (13-section templates/refs/version/hooks consistency), `tests/test-codex-package.sh`, plus `go build + go test + go vet` in a parallel job. Not bun+zod, not `claude plugin validate` CLI
- **Trigger**: `pull_request` + `push: branches: [main]`
- **Frontmatter validation**: yes — `tests/validate-skills.sh` exists and validation chain includes frontmatter rules per `docs/agent-frontmatter-policy.md`
- **Hooks.json validation**: yes (via `check-consistency.sh`, which verifies templates/refs/version/hooks align)
- **Pitfalls observed**: `claude plugin validate` CLI is referenced in CHANGELOG as the goal ("v4.2 Plugin validation: public-spec compliant: `monitors/monitors.json` + `agents/` auto-discovery") but not invoked in CI. Project wrote its own 39-item validator prior to public validate CLI shipping and has not migrated. Sync regression history (`harness sync` silently stripping `monitors`/`agents` blocks) required adding both shell idempotency and Go-struct phantom-field tests — a two-layer guard pattern

## 16. Documentation

- **`README.md` at repo root**: present (18.4KB English) + `README_ja.md` (20.5KB Japanese mirror)
- **`README.md` per plugin**: not applicable (single-plugin marketplace — repo README IS the plugin README)
- **`CHANGELOG.md`**: present — 248KB Keep-a-Changelog-adjacent format in Japanese with explicit `[Unreleased]` section, `## [X.Y.Z] - YYYY-MM-DD` headings, and "今まで/今後" (Before/After) narrative per item. Release-body extraction uses awk to grab between `## [VERSION]` markers
- **`architecture.md`**: at `docs/ARCHITECTURE.md` (uppercase) plus `docs/architecture/` subdirectory; `go/DESIGN.md` + `go/SPEC.md` for Go engine
- **`CLAUDE.md`**: at repo root (6.7KB), English guidance with explicit "All responses must be in Japanese" rule — meta-ironic: CLAUDE.md is English about producing Japanese output
- **Community health files**: `CONTRIBUTING.md` (6.1KB), no `SECURITY.md`, no `CODE_OF_CONDUCT.md` observed
- **LICENSE**: present — MIT at both `LICENSE.md` (English, SPDX: MIT) + `LICENSE.ja.md` (Japanese translation)
- **Badges / status indicators**: observed — shields.io badges for Latest Release, License (MIT), Claude Code (v2.1+), Skills (5 Verbs), Core (Go Native), v4.2 Hokage codename
- **Pitfalls observed**: bilingual documentation (every README/CHANGELOG in English+Japanese) is a heavy maintenance surface. `docs/` has 20+ files plus nested `docs/architecture/`, `docs/plans/`, `docs/private/`, `docs/evidence/`, `docs/examples/`, `docs/images/` — documentation is itself a first-class artifact with its own sub-hierarchy

## 17. Novel axes

- **Release-codename branches without tag ownership**: `release/v4.2.0-arcana`, `release/v4.3.0-arcana` are long-lived branches named after release codenames (v4.0 "Hokage", v4.2 "Hokage line", v4.3 "Arcana") but tags land on main, not on these branches. Branches appear to snapshot release-prep state. Differs from typical `release/*` patterns that own the tag — candidate new purpose: "release-prep branching without tag ownership"
- **Committed Go binaries as distribution**: `bin/harness-{darwin-arm64,darwin-amd64,linux-amd64}` checked into the git tree (~33MB total) rather than downloaded-on-install or attached to GitHub Release assets. `bin/harness` shim dispatches by `uname` to the right binary. Graceful-no-op on unsupported platforms (Linux-ARM64, Windows → exit 0 silent with stderr). Candidate new purpose: "in-tree cross-compiled binaries with dispatch shim"
- **Triple version SSOT (`VERSION` + `plugin.json` + `harness.toml`)**: three separate files held in sync by `sync-version.sh check|sync|bump` + pre-commit hook + CI `check-version-bump.sh`. `VERSION` is the declared source of truth; `plugin.json` is a derived artifact re-emitted by `harness sync` from `harness.toml` (the Go-engine's native config). Only sampled repo with this pattern
- **`harness sync` as CC-manifest codegen**: `harness.toml` is the authored file; `.claude-plugin/{plugin.json, hooks.json, settings.json}` + `agents/*` + `monitors/monitors.json` are outputs of the Go binary's `sync` subcommand. The `check-consistency.sh` CI gate enforces that committed files match what `sync` would produce. Inverts the usual direction where plugin.json IS the source
- **Hook-type `agent` with literal Haiku prompts in `hooks.json`**: PreToolUse on `Write|Edit`, PostToolUse on `Write|Edit`, PreCompact, and Stop all embed `type: agent` entries with multi-hundred-character English prompts that invoke `model: haiku` for secondary review. Stop's agent actively blocks session termination when Plans.md has `cc:WIP` tasks, returning `{"decision": "block", "reason": ...}`. Only sampled repo using this pattern; usually agent-review is out-of-band
- **18 distinct hook events wired**: matches nearly every CC hook surface including rare ones (`InstructionsLoaded`, `TeammateIdle`, `TaskCompleted`, `TaskCreated`, `WorktreeCreate`, `WorktreeRemove`, `Elicitation`, `ElicitationResult`, `StopFailure`, `ConfigChange`, `CwdChanged`, `FileChanged`, `PostToolUseFailure`, `SubagentStart`, `SubagentStop`) — representative catalogue of "maximum hook surface" that other plugin authors could study for event availability
- **`PermissionRequest` hook with `if:` allowlist for Bash**: `PermissionRequest` on `matcher: "Bash"` uses an `if:` clause enumerating a long list of auto-allow patterns (`git status*`, `git diff*`, `npm test*`, `pytest*`, `go test*`, etc.). Fine-grained per-hook conditional gating — novel conditional-hook pattern
- **Cross-runtime skill mirrors**: `skills/` (primary, Claude Code), `skills-codex/`, `codex/.codex/skills/`, `opencode/skills/` — one authored source mirrored to three downstream runtimes via `scripts/build-opencode.js` + `scripts/sync-skill-mirrors.sh`, with `opencode-compat.yml` CI gate that fails if mirrors drift. Novel multi-runtime distribution pattern
- **Sandbox config in settings.json**: `.claude-plugin/settings.json` carries `sandbox.failIfUnavailable`, `sandbox.network.deniedDomains` (including cloud metadata endpoints `169.254.169.254`, `metadata.google.internal`, `metadata.azure.com`), and `sandbox.filesystem.{denyRead, allowRead}` blocks. Most sampled repos leave sandbox default; this is an explicit SSRF-defense posture
- **External release tool with workflow fallback**: `release.yml` explicitly branches on "has release-har already created the release?" — primary path is an external tool (`release-har`) the user invokes; workflow acts as safety-net. Inverts the usual "workflow IS the release mechanism" pattern

## 18. Gaps

- **Go engine internals** — `go/cmd/harness/`, `go/internal/`, `go/pkg/` not inspected beyond `go.mod`; specific hook schema emissions (JSON shape per hook subcommand), `harness sync` codegen logic, and guardrail rule implementations (R01–R13 referenced in CHANGELOG) require reading Go source. Source: `gh api repos/Chachamaru127/claude-code-harness/contents/go/pkg` recursive listings
- **`release-har` external tool** — referenced by name in release.yml, CHANGELOG, and setup scripts but its implementation is out-of-repo. Unknown whether it's a separate GitHub repo owned by the same user, a local shell script, or a fork of another tool. Source: searching user profile for `release-har` repo, or checking `scripts/setup-codex.sh` for installation hints
- **Agent `hooks:` inline frontmatter semantics** — reviewer.md carries a `hooks: Stop:` block in its own frontmatter. Whether CC honors per-agent hook registration from agent frontmatter, or whether this is a convention consumed by the harness Go binary, is not documented in inspected files. Source: CC docs for agent frontmatter fields + Go source search for `hooks:` YAML key
- **`validate-plugin.sh` full 39-item surface** — only the `--quick` path was read. The full validator's item list would refine the "what does CI actually check" answer. Source: full file read
- **Why release branches are behind main** — `release/v4.3.0-arcana` is 11 commits behind main, `v4.3.0` tag is 1 commit ahead of the branch. Whether the branch was cut, tag added, then main continued (normal), or whether there's an active cherry-pick/rebase discipline, is not settled by comparing refs alone. Source: `gh api repos/.../git/refs` + commit graph via `gh api repos/.../compare/<tag>...main`
- **Monitors actual runtime semantics** — `monitors.json` declares `when: always` for one monitor, but how Claude Code consumes this (polling interval, execution lifecycle, failure handling) is outside this repo's source. Source: Claude Code `docs-plugins-reference.md` already in context resources — cross-reference needed but budget-skipped
- **Opencode/Codex mirror structure** — `skills-codex/`, `codex/`, `opencode/` directories observed but not traversed. The mirror/build scripts and validation workflow were inspected, not their outputs. Source: recursive `gh api contents` for each directory
