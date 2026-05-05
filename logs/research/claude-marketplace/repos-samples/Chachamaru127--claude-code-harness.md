# Sample

Mirrors of `https://github.com/Chachamaru127/claude-code-harness`. Single-plugin marketplace shipping a Claude Code harness for solo developers (Vibecoders) that turns Claude Code into a Plan → Work → Review delivery loop with a Go-native hook engine.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root. Marketplace name `claude-code-harness-marketplace`, sole plugin entry `claude-code-harness` with `source: "./"`, explicit `strict: true`. Top-level keys plus `metadata.{description}` wrapper (no `metadata.version`, no `metadata.pluginRoot`). Marketplace `description` is localized to Japanese ("配布/導入を支援する…") while the per-plugin `description` is English — mixed-language surface inside one manifest. `$schema` absent on `marketplace.json`; `settings.json` carries `"$schema": "https://json.schemastore.org/claude-code-settings.json"`.

### Top-level `metadata` wrapper variants

`metadata.{description}` wrapper plus top-level `name`, `owner.{name}`, and `plugins[]`. No `metadata.version`, no `metadata.pluginRoot`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"`; plugin root and repo root are the same path.

### `strict` field default

`strict: true` declared explicitly on the single marketplace entry. `skills` override absent on the marketplace entry — `skills` lives on `plugin.json` as `"./skills/"`.

## Source layout

### Generated manifests from upstream config

`.claude-plugin/{plugin.json, hooks.json, settings.json}`, `agents/*`, `monitors/monitors.json` are emitted by the Go binary's `harness sync` subcommand reading a single authored source (`harness.toml`). The committed manifests are derived artifacts; CI consistency check (`scripts/ci/check-consistency.sh`) verifies the working tree matches what `sync` would produce. Inverts the usual "manifest is hand-authored" assumption.

## Per-plugin discoverability metadata

### Marketplace-entry facets plus duplicated keywords on plugin.json

Marketplace entry declares `keywords: ["claude-code","plugin","vibecoder","workflow","plan-work-review"]` plus `category: "productivity"` (no `tags`). `plugin.json` carries its own `keywords` mirroring the marketplace surface.

## Version coordination

### Triple-file version (build manifest joins)

Three sites carry the version: `VERSION` (plain text, `4.3.3`) is the declared source of truth, `.claude-plugin/plugin.json` mirrors it, and `harness.toml` holds a third copy. `scripts/sync-version.sh check|sync|bump` reconciles all three; enforced by `.githooks/pre-commit` and CI `check-version-bump.sh`. `harness.toml` is the source consumed by the Go `harness sync` subcommand that re-emits `plugin.json` / `hooks.json` / `settings.json`, so `plugin.json` is effectively a derived artifact even though it's checked in. The marketplace entry itself has no `version` field — drift risk is between VERSION/plugin.json/harness.toml only.

### Pre-commit hook auto-sync (consistency, not increment)

`.githooks/pre-commit` (installed by `scripts/install-git-hooks.sh`) watches `VERSION` + `.claude-plugin/plugin.json`; on mismatch runs `sync-version.sh sync` (VERSION is source of truth, plugin.json mirrors) and re-stages. Does not auto-bump — bump is manual via `sync-version.sh bump [patch|minor|major]` when cutting a release.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Users pin via `/plugin update claude-code-harness` directly from the marketplace at head. README recommends Claude Code v2.1.111+ but no separate stable/latest marketplaces. CHANGELOG references minimum CC versions per-release rather than branching the marketplace.

## Tag and release lifecycle

### Release-codename branches without tag ownership

Default branch `main`. All 10 inspected releases (`v4.3.3` … `v4.0.0`) have `target_commitish: main` and the tag commits sit on main. Long-lived branches `release/v{x.y.0}-arcana` exist (`release/v4.2.0-arcana`, `release/v4.3.0-arcana`) named after release codenames (v4.0 "Hokage", v4.2 "Hokage line", v4.3 "Arcana"), but they are behind main, not ahead — `release/v4.3.0-arcana` is 11 commits behind main and 0 ahead; the `v4.3.0` tag is 1 commit ahead of the release branch. Tags land on main, not on these branches; the release branches snapshot release-prep state and main rebases past. Additional `chore/v4.3.2-release-complete` and `follow-up/4.3.2-nitpicks` topic branches appear for release-prep workflow. No pre-release suffixes on v4.x tags; `-arcana` appears only as a release-codename suffix on the long-lived branches, not as a semver pre-release marker. `VERSION` holds real semver (`4.3.3`) on main with no 0.0.z dev-counter discipline; main sits at the released version until next bump.

## Plugin-component registration

### Mixed (paths + auto-discovery)

`plugin.json` declares explicit paths for skills (`"skills": ["./skills/"]`) and `outputStyles: "./output-styles/"`; agents/hooks/monitors rely on convention-directory auto-discovery (no fields in `plugin.json`, but directories exist at `agents/`, `hooks/`, `monitors/`). Hooks are also explicitly written to `.claude-plugin/hooks.json` (16.8KB comprehensive) and a parallel copy at `hooks/hooks.json` via `harness sync`.

### Hooks-json with broad event coverage

`.claude-plugin/hooks.json` wires 18 distinct hook events including rare ones — `SubagentStart`, `SubagentStop`, `InstructionsLoaded`, `PostToolUseFailure`, `TeammateIdle`, `TaskCompleted`, `TaskCreated`, `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`, `Elicitation`, `ElicitationResult`, `StopFailure`, `ConfigChange`, `CwdChanged`, `FileChanged` — alongside common ones.

## Component composition

### Composition shapes

Broadest palette. Skills (32 skill directories under `skills/`, plus mirrors at `skills-codex/`, `codex/`, `opencode/` for cross-runtime distribution); agents (5 — `worker`, `reviewer`, `scaffolder`, `advisor`, `team-composition`); hooks; monitors (`monitors/monitors.json` with `harness-session-monitor`); bin (`bin/harness` shim plus three committed Go binaries); output-styles (`output-styles/harness-ops.md`, single file). No top-level `commands/` directory (skills replace commands per README "5 Verb Skills"). No `.mcp.json` at repo root, no `.lsp.json`.

## Skill authoring conventions

### Standard frontmatter

Skills under `skills/<name>/SKILL.md` (32 directories), with mirrors at `skills-codex/`, `codex/.codex/skills/`, `opencode/skills/`.

## Agent declaration conventions

### Rich behavior fields (background, isolation, memory)

Agent frontmatter uses `name`, `description`, `tools` (list form, not permission-rule syntax), `disallowedTools`, `model` (e.g., `claude-sonnet-4-6`, `claude-opus-4-6`), `effort` (`medium`/`xhigh`), `maxTurns`, `permissionMode` (`bypassPermissions`), `color`, `memory: project`, `isolation: worktree` (worker only), `initialPrompt` (literal multi-line block), `skills` (list of skill names the agent can invoke), and `hooks` (inline — reviewer carries a Stop hook in its frontmatter). Agents mix `memory: project` + `isolation: worktree` (worker) — novel combination. Reviewer's inline `hooks:` block in frontmatter is unusual. Project is actively migrating models 4-6 → 4-7 per CHANGELOG.

### `model` + `effort` + `maxTurns` for cost control

`effort: xhigh` on reviewer/advisor requires Claude Code v2.1.111+. `model` selects between `claude-sonnet-4-6`/`claude-opus-4-6`/etc per agent role with `maxTurns` and `effort` as per-agent cost controls.

### Plain tool-name list

`tools:` field as a YAML list of plain tool names (`- Read`, `- Bash`) — NOT permission-rule syntax. `disallowedTools` block runs alongside `tools` for explicit denial.

## Cross-platform skill publishing

### Multi-runtime skill mirrors

`skills/` (primary, Claude Code), `skills-codex/`, `codex/.codex/skills/`, `opencode/skills/` — one authored source mirrored to three downstream runtimes via `scripts/build-opencode.js` + `scripts/sync-skill-mirrors.sh`, with `opencode-compat.yml` CI gate that fails if mirrors drift.

## Bin entry mechanism

### Cross-platform shim dispatching to pre-built binaries

`bin/harness` is a POSIX shell wrapper that resolves `uname -s`/`uname -m` and `exec`s the matching pre-built binary. Mode 100755. Three binaries shipped: `bin/harness-darwin-arm64` (11MB), `bin/harness-darwin-amd64` (12MB), `bin/harness-linux-amd64` (11MB). Shebang `#!/bin/sh` (POSIX, not bash-specific). Walks `readlink` chain to find `SCRIPT_DIR`, then constructs `${SCRIPT_DIR}/harness-${OS}-${ARCH}`. Hooks always invoke via `"${CLAUDE_PLUGIN_ROOT}/bin/harness"` so the shim locates its siblings. Linux-arm64 and Windows not supported — shim silently no-ops (exit 0) with stderr message, so the plugin degrades gracefully to "no guardrails, no errors." Comment in shim says "Never print JSON here — we don't know which hook/command is being called and emitting the wrong schema breaks the hook protocol."

### Committed binaries in tree

`bin/harness-{darwin-arm64,darwin-amd64,linux-amd64}` checked into the git tree (~33MB total per clone) rather than downloaded-on-install or attached to GitHub Release assets. SessionStart hooks themselves call `bin/harness hook session-start` — they consume the binary rather than building it.

## Dependency installation

### No managed install (user prerequisite)

Go binaries are committed in-tree, so the "install" is effectively `git clone`. `go/go.mod` (go 1.25.0), `go/go.sum`. Scripts also use `node` for `build-opencode.js` / `validate-opencode.js`. No `package.json` observed at root. CI `validate-plugin.yml` `test-go` job rebuilds on every push to check `go build` + `go test` + `go vet`. `go build -ldflags="-X main.version=${VERSION}"` bakes the VERSION file into each binary at build time, so runtime `harness --version` reports the repo's version. Go stdlib statically-linked, `modernc.org/sqlite` pure-Go (`CGO_ENABLED=0`). v4.0 "Hokage" README boasts explicit removal of the Node.js dependency that v3 carried.

## Install change detection

### No change detection

End users get binaries by cloning the plugin via the marketplace; no first-session install step, no retry-next-session invariant. `bin/harness` shim exits 0 with stderr diagnostic and empty stdout when the platform binary is missing.

## Install failure posture

### Silent fail-open (`exit 0` always, retry every hook)

`bin/harness` shim exits 0 silently with stderr diagnostic when no platform binary is found — "CC hooks treat it as 'no decision' — proceed normally."

## User configuration and authentication

### External config file owned by plugin

The plugin has an extensive user-configurable surface (review mode, breezing parallelism, advisor thresholds, cleanup policies) routed through `.claude-code-harness.config.yaml` and `harness.toml`, which the Go binary reads directly rather than via Claude Code's `userConfig` substitution surface. Decouples config from CC updates but means users can't configure via CC's UI. No `userConfig` in `plugin.json` or `marketplace.json`. No `${user_config.KEY}` or `CLAUDE_PLUGIN_OPTION_*` references.

## Session context loading

### SessionStart + UserPromptSubmit chain for context injection

`SessionStart` matcher `startup|resume` (covers fresh start and resume from disk; deliberately skips `clear` and `compact`, which are handled by `PreCompact`/`PostCompact`). Three commands fire: `hook session-start`, `hook memory-bridge`, and `bash scripts/hook-handlers/memory-session-start.sh`. `once: true` prevents duplicate fires.

`UserPromptSubmit` chains 6 hooks — `hook memory-bridge`, `bash scripts/userprompt-inject-policy.sh`, `hook inject-policy`, `hook track-command`, `hook fix-proposal`, `hook breezing-signal`. The `inject-policy` / `memory-bridge` names imply `additionalContext` injection, but Go source not directly inspected.

## SessionStart matcher scope

### Explicit subset

`startup|resume` matcher narrower than the `startup|clear|compact` pattern docs suggest; intentional separation so the PreCompact/PostCompact handlers do compact-context-preservation work. `once: true` on SessionStart hooks is explicit.

## Tool-use enforcement

### Multi-pattern PreToolUse safety stack

Four `PreToolUse` matchers: `Write|Edit|MultiEdit|Bash|Read` (pre-tool router); `AskUserQuestion` (normalize answers); `Write|Edit` (inbox-check + Haiku agent hook for secret/TODO/security review); `mcp__chrome-devtools__.*|mcp__playwright__.*|mcp__plugin_playwright_playwright__.*` (browser-guide).

### Inline `type: agent` hooks invoking secondary models

Stop, PreToolUse on `Write|Edit`, PostToolUse on `Write|Edit`, and PreCompact embed `type: agent` entries with multi-hundred-character English prompts that invoke `model: haiku` for secondary review. Stop's agent reads `Plans.md` for `cc:WIP` tasks and returns `{"decision": "block", "reason": ...}` if found — very assertive stop-gating. Specific hooks return `{"permissionDecision": "deny"}` plus `permissionDecisionReason` when issues are detected (secrets/TODO/injection).

### `if:` permission-rule sub-matcher

`PermissionRequest` registered with `matcher: "Edit|Write|MultiEdit"` and `matcher: "Bash"`. The Bash matcher carries a long `if:` clause enumerating allowed bash patterns (`git status`, `npm test`, `pytest`, `go test`, etc.).

### `PermissionRequest` with `if:` allowlist

The `PermissionRequest` Bash matcher uses an `if:` clause with auto-allow patterns enumerated declaratively rather than dispatching to a binary.

### PostToolUse async telemetry + eval gate

8 `PostToolUse` entries with matchers `Write|Edit|MultiEdit|Bash`, `Write|Edit` (plus a second Haiku agent), `*`, `Bash`, `Skill|Task|SlashCommand`, `Skill`, `TodoWrite`, `Write|Edit|Task`. Purposes include post-tool router, memory-bridge, commit-cleanup, async ci-status, usage-tracker, clear-pending, todo-sync, emit-trace, auto-cleanup, track-changes, async auto-test, quality-pack, plans-watcher, tdd-check, auto-broadcast.

## Hook handler runtime

### Single Go binary with subcommand dispatch

Every hook entry calls `${CLAUDE_PLUGIN_ROOT}/bin/harness hook <event-name>`. The Go binary owns hook protocol, JSON schema emission, decision logic, and per-event handlers. One executable, many entry points. Monitors reuse the same surface (`bin/harness hook session-monitor`).

## Hook output contract

### JSON-only stdout, no stderr-human parallel

Hook output convention is centrally managed: each hook implementation owns its own schema since the shim explicitly says "Never print JSON here — we don't know which hook/command is being called." The Haiku-agent hooks on Write|Edit return JSON `permissionDecision: deny` + `permissionDecisionReason` when they detect issues; non-deciding paths exit silently.

## Hook failure posture

### Fail-open with always-exit-0

Shim exits 0 with empty stdout on missing binary, so the CC hook sees "no decision / proceed normally." Haiku-agent hooks fail-closed only on judgment-flag (deny when secrets/TODO/injection detected); otherwise fail-open.

## Live monitoring

### `monitors.json` with single watcher

`monitors/monitors.json` at the canonical location (per CC v2.1.105 public spec, per CHANGELOG). One entry — `harness-session-monitor`, `when: always` — auto-arms session monitoring for harness-mem health, advisor/reviewer state, and Plans.md drift. Monitor command `"${CLAUDE_PLUGIN_ROOT}/bin/harness" hook session-monitor` reuses the same `hook` subcommand surface as `hooks.json`, so monitors and hooks share one Go binary and one dispatch plane. CHANGELOG v4.2 documents a regression where `harness sync` silently stripped declared `monitors`/`agents` blocks; now has shell + Go struct tests.

### Version-floor declaration absent

README `## Requirements` states "Claude Code v2.1+" with "v2.1.105+ recommended (PreCompact hook + monitors manifest)" — version floor declared in prose, no machine-readable field.

## Plugin-to-plugin coordination

### Implicit prose-only dependency

No `dependencies` field declared in `plugin.json`. README references an external companion plugin `harness-mem` that integrates via shared protocol rather than declared dependency: "Optional `harness-mem` integration: sessions remember what you worked on last time." Coupling is by runtime detection (`~/.claude-mem/` presence check in v4.3.3 hotfix) rather than by manifest. Single-plugin marketplace with simple `v{x.y.z}` tag format — not the `{plugin-name}--v{version}` cross-plugin format.

## Testing

### Multi-runner — `node --test` + bats

Multiple test substrates: Go `go test` for the core engine; ~60 `tests/test-*.sh` files plus `tests/validate-plugin.sh`, `tests/validate-skills.sh`, `tests/validate-plugin-v3.sh`, `tests/test-codex-package.sh`; `tests/unit/`, `tests/integration/`, `tests/fixtures/` subdirectories; `scripts/ci/check-consistency.sh`, `scripts/ci/check-version-bump.sh`. Go tests inside `go/` alongside source (`go/pkg/...`, `go/internal/...`); bash validation tests at `tests/` at repo root. Test runner invocation: direct `bash` for shell tests, direct `go test` for Go — no wrapper script orchestrates both. `tests/validate-plugin.sh` is the single aggregator over the ~60 individual `tests/test-*.sh` files (CI doesn't call them individually).

## CI workflow shape

### Multi-workflow split by trigger and concern

Four workflow files: `.github/workflows/release.yml`, `validate-plugin.yml`, `benchmark.yml`, `opencode-compat.yml`.

- `validate-plugin.yml` triggers on `pull_request` + `push: branches: [main]`; runs `bash scripts/ci/check-version-bump.sh`, installs ripgrep, `bash tests/validate-plugin.sh`, `bash scripts/ci/check-consistency.sh`, `bash tests/test-codex-package.sh` in the `validate` job; separate `test-go` job runs `go build ./cmd/harness/`, `go test ./...`, `go vet ./...` with `actions/setup-go@v5` + go.mod cache.
- `release.yml` triggers on `push: tags: ['v*']`.
- `benchmark.yml` triggers on `workflow_dispatch` with task/trials/mode inputs; requires `ANTHROPIC_API_KEY` secret and runs real Claude Code sessions (`npm install -g @anthropic-ai/claude-code`) with `timeout-minutes: 120`.
- `opencode-compat.yml` triggers on path-scoped `push` + `pull_request`.

No matrix (single Go version from `go.mod`, single runner `ubuntu-latest`). Action pinning by tag (`actions/checkout@v4`, `actions/setup-go@v5`, `actions/setup-python@v5`, `actions/setup-node@v4`) — no SHA pinning. Caching: `actions/setup-go@v5` with `cache-dependency-path: go/go.sum`; `actions/setup-node@v4` and `actions/setup-python@v5` use defaults.

## Pre-commit and pre-push hooks (git)

### `.pre-commit-config.yaml` with linters only

`.githooks/pre-commit` (installed by `scripts/install-git-hooks.sh`) watches `VERSION` + `.claude-plugin/plugin.json`; on mismatch runs `sync-version.sh sync` and re-stages. Does not auto-bump. Bump is manual via `sync-version.sh bump [patch|minor|major]`.

## Marketplace validation

### Custom in-repo validator

`tests/validate-plugin.sh` (39-item structural check) plus `scripts/ci/check-consistency.sh` (13-section templates/refs/version/hooks consistency) run on every PR and push. Plus `tests/test-codex-package.sh`. Plus `go build + go test + go vet` in a parallel job. Not bun+zod, not the public `claude plugin validate` CLI — though that CLI is referenced in CHANGELOG as the goal. Project wrote its own 39-item validator prior to public validate CLI shipping and has not migrated. `tests/validate-skills.sh` exists and validation chain includes frontmatter rules per `docs/agent-frontmatter-policy.md`. `hooks.json` validation via `check-consistency.sh`. Sync regression history (`harness sync` silently stripping `monitors`/`agents` blocks) required adding both shell idempotency and Go-struct phantom-field tests — a two-layer guard pattern.

## Release automation

### Tag-triggered cross-build with CHANGELOG awk extraction

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`; cross-builds Go binaries (darwin-arm64, darwin-amd64, linux-amd64) and attaches them to the GitHub Release. Workflow first checks `gh release view "$TAG"` — if a release already exists (created by external "release-har" tool), it only uploads/refreshes binaries via `gh release upload --clobber`; if release does NOT exist, acts as "safety-net" by extracting the CHANGELOG section via awk and creating the release itself with `gh release create --verify-tag --notes-file`. Tag-sanity gate: `gh release create --verify-tag` verifies the tag object points at the workflow's checked-out commit. No separate verify-tag-on-main or version-equals-tag gate in the workflow itself (the pre-commit hook + `check-version-bump.sh` in `validate-plugin.yml` catch version mismatches upstream).

CHANGELOG awk script extracts body between `## [VERSION]` and the next `## [` heading:

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

Falls back to auto-message if no CHANGELOG entry found. Inspected `v4.3.0`, `v4.3.3` releases have 0 assets attached — the safety-net Go binary upload step appears not to have run (or the external release-har tool created the release but the workflow's "exists=true" branch's `--clobber` upload silently failed with `|| true`). Despite the workflow building + attaching binaries, the actual binaries consumers see live in-repo at `bin/` rather than as release assets. CHANGELOG.md is 248KB — awk extraction scales linearly. Release body format prescribed in `.claude/rules/github-release.md` with a Keep-a-Changelog-like `[X.Y.Z] - YYYY-MM-DD` + Before/After table discipline, in Japanese for CHANGELOG and English for the GitHub Release body. Inspected releases are all `draft=False`, `prerelease=False`.

## Documentation surface

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` at repo root (18.4KB English) plus `README_ja.md` (20.5KB Japanese mirror). `CHANGELOG.md` is 248KB Keep-a-Changelog-adjacent format in Japanese with explicit `[Unreleased]` section, `## [X.Y.Z] - YYYY-MM-DD` headings, and "今まで/今後" (Before/After) narrative per item. `docs/ARCHITECTURE.md` (uppercase) plus `docs/architecture/` subdirectory; `go/DESIGN.md` + `go/SPEC.md` for Go engine. `CLAUDE.md` at repo root (6.7KB), English guidance with explicit "All responses must be in Japanese" rule (CLAUDE.md is English about producing Japanese output). `docs/` has 20+ files plus nested `docs/architecture/`, `docs/plans/`, `docs/private/`, `docs/evidence/`, `docs/examples/`, `docs/images/`. Shields.io badges for Latest Release, License (MIT), Claude Code (v2.1+), Skills (5 Verbs), Core (Go Native), v4.2 Hokage codename.

### Multi-language READMEs

Bilingual documentation (every README/CHANGELOG in English+Japanese). `LICENSE.md` (English, SPDX `MIT`) + `LICENSE.ja.md` (Japanese translation).

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

LICENSE present at both `LICENSE.md` (English, SPDX `MIT`) and `LICENSE.ja.md` (Japanese translation). `license: "MIT"` in plugin and marketplace manifests.

## Community health files

### Bare minimum (LICENSE only)

`CONTRIBUTING.md` (6.1KB) at root, no `SECURITY.md`, no `CODE_OF_CONDUCT.md`.

## Sandbox and security posture

### Explicit deny lists for cloud metadata and filesystem paths

`.claude-plugin/settings.json` carries `sandbox.failIfUnavailable`, `sandbox.network.deniedDomains` (including cloud metadata endpoints `169.254.169.254`, `metadata.google.internal`, `metadata.azure.com`), and `sandbox.filesystem.{denyRead, allowRead}` blocks. Explicit SSRF-defense posture.

## Output styles

### Shared markdown templates under `output-styles/`

Single file at `output-styles/harness-ops.md`. Declared in `plugin.json` as `outputStyles: "./output-styles/"`.

## Cross-ecosystem distribution

### Multi-adapter single-package shape

Skill content mirrored to four runtimes from one source: Claude Code (`skills/`), Codex (`skills-codex/`, `codex/.codex/skills/`), and OpenCode (`opencode/skills/`). `scripts/build-opencode.js` + `scripts/sync-skill-mirrors.sh` compile from primary; `opencode-compat.yml` CI gate fails on drift.

## Novel and cross-cutting concerns

### Generated-package.json pattern

`harness sync` is CC-manifest codegen — `harness.toml` is the authored file; `.claude-plugin/{plugin.json, hooks.json, settings.json}` + `agents/*` + `monitors/monitors.json` are outputs of the Go binary's `sync` subcommand. The `check-consistency.sh` CI gate enforces that committed files match what `sync` would produce. Inverts the usual direction where `plugin.json` IS the source.
