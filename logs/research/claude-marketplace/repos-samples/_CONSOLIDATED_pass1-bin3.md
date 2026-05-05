# Sample

Pass-1 Phase-1a partial for bin 3. Functional decomposition of `BrandCast-Signage--root.md`, `Chachamaru127--claude-code-harness.md`, and `ChanMeng666--claude-code-audio-hooks.md`, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

The shape of `marketplace.json` and how it relates to `plugin.json`.

### Single-plugin marketplace at repo root

One `.claude-plugin/marketplace.json` lists exactly one plugin entry whose `source` is the repo root or a sibling directory. The repo IS the plugin. This collapses the "marketplace vs plugin" abstraction to a single deliverable; the marketplace manifest exists only to satisfy the registration protocol. Drift between marketplace-level and plugin-level fields (description, version) becomes the dominant maintenance hazard since identical metadata is held in two places. Some samples additionally introduce `metadata.{description,version}` wrapper fields, multiplying the surface; others omit the wrapper entirely.

### Sibling plugin under `plugins/<name>/`

Marketplace at repo root with `source: "./plugins/<name>"` pointing into a subdirectory holding the actual plugin. Used when the repo also carries a canonical authoring tree at root and a packaged copy at `plugins/<name>/` — Claude Code's plugin cache copies the `plugins/<name>/` subtree as a unit, so anything the plugin needs at runtime must live inside it. Forces a dual-source-tree discipline (see *Source layout* below).

## Source layout

How files the plugin needs at runtime are organized in the repo.

### Single tree, plugin == repo

Plugin manifest at `.claude-plugin/`, components (skills, commands, hooks, agents, bin) at conventional top-level directories. Simplest layout; no synchronization burden. Appropriate when the repo's only purpose is the plugin and there is no separate authoring/distribution distinction.

### Dual tree with sync gate

Authoring sources live at repo root (`/hooks/`, `/bin/`, `/audio/`, `/config/`) and a packaged copy lives at `plugins/<name>/...`. A reconciler script (`build-plugin.sh [--check]`) does `cp + cmp -s` to keep them in sync; CI runs the same script with `--check` to fail PRs that drift. Justified when Claude Code's plugin cache treats `plugins/<name>/` as a self-contained unit but the author wants a cleaner top-level surface for non-plugin tooling, tests, or cross-target packaging. Cost: every change to a hook, bin, or config file is a two-place edit unless the author runs the reconciler.

### Generated manifests from upstream config

Plugin manifests (`plugin.json`, `hooks.json`, `settings.json`, `agents/*`, `monitors/monitors.json`) are emitted by a `sync` subcommand of an in-repo binary that reads a single authored source (`harness.toml`). The committed manifests are derived artifacts; a CI consistency check verifies the working tree matches what `sync` would produce. Inverts the usual "manifest is hand-authored" assumption; appropriate when the plugin's surface is too large or schema-fragile for hand maintenance and when a custom binary already exists to interpret the upstream config.

## Plugin component declaration

How `plugin.json` references skills, commands, agents, hooks, and other components.

### Convention-directory auto-discovery

`plugin.json` carries identity fields only (`name`, `version`, `description`, `userConfig`). Components are resolved by Claude Code from conventional directory names (`hooks/hooks.json`, `skills/<name>/SKILL.md`, `agents/`, `commands/`). Minimum manifest surface; relies entirely on Claude Code's discovery rules. Appropriate when every component sits where the plugin spec expects.

### Explicit per-component paths

Every component declared by path: `"skills": ["./skills/audio-hooks/"]`, `"agents": ["./agents/foo.md", ...]`, `"hooks": "./.claude-plugin/hooks.json"`, `"mcpServers": ["./.mcp.json"]`. Used when components live outside convention paths (e.g., `.claude-plugin/hooks.json` for hooks, sibling `.mcp.json` for MCP) or when the author wants the manifest itself to enumerate the surface. More verbose than auto-discovery but makes the component inventory readable from the manifest alone.

### Mixed (paths + auto-discovery)

Some components declared by path, others left to convention. E.g., skills listed by path but agents discovered from `agents/` directory. Often arises when the plugin gradually adopted explicit declarations only for components that didn't fit conventions.

## User configuration surface

How the plugin exposes user-tunable options.

### `userConfig` block in `plugin.json`

Top-level `userConfig` object declares typed fields (`type`, `title`, `description`); Claude Code surfaces these in the install/configure UI. Values reach the plugin via `CLAUDE_PLUGIN_OPTION_<KEY>` environment variables which the plugin reads at runtime and overlays onto an internal preferences object. Schema richness varies — `title`/`description` always present; `default`, `enum`, `sensitive` optional and frequently omitted (enum values may appear only in prose descriptions, leaving install-time validation gap). Appropriate for a small bootstrap surface (≤5 fields) with a deeper config schema mutated out-of-band by the plugin's CLI.

### External config file owned by plugin

Plugin reads its own JSON/YAML file (`root.config.json`, `.claude-code-harness.config.yaml`) from the consumer's repo or a known location. Schema is plugin-controlled, often versioned (`configVersion: 2`) with in-plugin migration logic to upgrade older versions on session start. Bypasses Claude Code's config UI entirely — config authorship is in the consumer's repo, version-controlled with the project. Appropriate when the surface is large enough that `userConfig`'s flat schema would be unwieldy or when config needs to evolve through schema migrations the plugin itself owns.

### No user-tunable surface

`plugin.json` has no `userConfig`; behavior is fixed. Appropriate for plugins whose value proposition has no meaningful axes of variation.

## Version authority

Where the canonical version string lives and how it propagates.

### `plugin.json` only

Single source. No sync burden. Often co-occurs with single-plugin marketplace where the marketplace entry has no `version` field of its own.

### `plugin.json` + `marketplace.json` (manual sync)

Both manifests carry the same version literal; sync is by convention. Drift is detected by humans or by a CI consistency script. The CHANGELOG narration in one sample explicitly documents shipping a release where some sites updated and others didn't, motivating retroactive addition of CI version-bump checks.

### Triple+ sync via dedicated tooling

A `VERSION` text file is declared the source of truth; `plugin.json` and an upstream config file (`harness.toml`) mirror it. A `sync-version.sh check|sync|bump` script reconciles all three; pre-commit git hook enforces sync before commit; CI re-runs the check on push. Appropriate when generated manifests (`harness sync`) introduce a third version site that must agree with the authored sources.

### Multi-harness mirrored versions

Same version literal carried in `plugin.json`, `marketplace.json`, and a sibling harness's manifest (`gemini-extension.json`). Three-file sync rule lives in prose in `CLAUDE.md`; no tooling enforces it. The presence of the sibling-harness manifest reflects the *Multi-harness distribution* role below.

## Distribution channel

How users get a specific version of the plugin.

### Single channel from default branch HEAD

Users install via `/plugin marketplace add <owner>/<repo>` and always receive whatever `main`/`master` carries right now. No stable/latest split. Pinning, when desired, relies on `@<ref>` git syntax not documented in the marketplace metadata. Constrains the version-control story: every commit to default branch is a potential release, so version field updates and CHANGELOG entries are the only release boundary marker.

### In-tree binary distribution

Pre-built platform-specific binaries are committed to the repo (`bin/harness-darwin-arm64`, `bin/harness-linux-amd64`, etc.) and dispatched at runtime by a shim that detects `uname`. Users get binaries by cloning. Trades repo size (~33MB of binaries per clone) for zero runtime install latency and zero dependency on GitHub Release artifacts being present. Single-architecture gaps are handled by graceful no-op (see *Failure posture* below).

### Marketplace-cache invalidation hack

Patch-level version bump committed with no functional change, intended solely to force the marketplace cache to re-pull a prior release. Documented openly in CHANGELOG ("Patch bump to force the marketplace to pull v2.3.0's bundled-MCP changes. No code changes vs 2.3.0."). Symptom of having no control over marketplace refresh timing and no immutable release artifact (no git tag, no GitHub Release).

## Release anchoring

How a specific release is made addressable.

### Git tag on default branch

`v<x.y.z>` annotated tags placed on the default branch's release commit. Tag is the immutable reference; consumers can checkout tag for a stable view. Common pattern.

### Release-codename branches without tag ownership

Long-lived branches named after release codenames (`release/v4.3.0-arcana`) exist but tags land on `main`, not on these branches. The branches snapshot release-prep state and may be behind main by the time the tag is cut. Differs from the typical `release/*` pattern that owns tags. Branches function as historical/preparation markers rather than as authoritative release pointers.

### No anchoring

No git tags, no GitHub Releases, no archives. "Release" exists only as a commit on the default branch that bumps version fields and adds a CHANGELOG section. Consumers cannot pin to a version. Compounds the channel-from-HEAD problem: there is no way to recover any prior release state.

## Version bump mechanism

What triggers a version increment.

### Manual bump per release

Author edits the version field(s) by hand when cutting a release. Drift is the failure mode (one file edited, others forgotten). Documented post-mortem regressions when this fails motivate adding CI consistency gates after the fact.

### Pre-commit hook auto-sync

Git pre-commit hook (`.githooks/pre-commit` installed by `scripts/install-git-hooks.sh`) detects mismatch between `VERSION` and `plugin.json` and runs `sync-version.sh sync` to mirror, re-staging the corrected files. Does not auto-bump; bump itself is manual via `sync-version.sh bump [patch|minor|major]`. The hook only enforces consistency, not increment.

## Release automation

What happens when a release tag is pushed.

### None — fully manual

No release workflow. Version bumps land on default branch; humans optionally create GitHub Releases by hand or omit them. The CHANGELOG is the only release artifact.

### Tag-triggered cross-build with CHANGELOG awk extraction

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`, cross-builds platform binaries (Go), and attaches them to the GitHub Release. Release notes body is extracted from `CHANGELOG.md` by an awk script that grabs the section between `## [VERSION]` and the next `## [` heading. Workflow first checks whether an external tool already created the release — if so, only refreshes binaries via `gh release upload --clobber`; otherwise creates the release itself as a safety-net. Inverts the usual "workflow IS the release mechanism" pattern.

## Hook event surface

Which hook events the plugin wires.

### Minimal notification-only set

A handful of events (PreToolUse, PostToolUse, SessionStart, UserPromptSubmit, Stop) used for side-effects (audio cues, edit tracking) without policy enforcement. Hooks are `async: true` with short timeouts; failures are silent. Appropriate when the plugin's job is observation/feedback, not gating.

### Comprehensive event coverage with matcher-scoped routing

26+ hook registrations across 24+ event types, including rare events (`SubagentStart`, `SubagentStop`, `InstructionsLoaded`, `TeammateIdle`, `TaskCompleted`, `WorktreeCreate`, `Elicitation`, `ConfigChange`, `CwdChanged`, `FileChanged`, `PostToolUseFailure`). Matcher routing is pushed into `hooks.json` rather than into handler code — each `SessionStart` sub-event (`startup`, `resume`, `clear`, `compact`) gets its own registration with a synthetic handler name. Makes the hook manifest the source of truth for "which variant triggers which handler." Useful as a representative catalogue when authors need to know which events Claude Code exposes.

### Inline `type: agent` hooks invoking secondary models

PreToolUse / PostToolUse / PreCompact / Stop hooks declared with `type: agent` and a literal multi-hundred-character prompt that invokes a secondary model (Haiku) for review. Stop's agent reads workspace state files and returns `{"decision": "block"}` to gate session termination. Parallel model invocation during hook evaluation; differs from the usual "hook calls a binary" pattern.

### `PermissionRequest` with `if:` allowlist

`PermissionRequest` hook on `matcher: "Bash"` uses an `if:` clause enumerating auto-allow patterns (`git status*`, `git diff*`, `npm test*`, `pytest*`, `go test*`). Fine-grained per-hook conditional gating without dispatching to a binary. Replaces the "binary returns permissionDecision" round-trip with declarative conditions in the manifest itself.

## Hook handler runtime

What language/binary the hook handlers run on.

### Bash scripts at conventional path

Hook commands point at `.sh` files in `hooks/scripts/`. Mixed shebangs across scripts (`#!/bin/bash`, `#!/usr/bin/env bash`). No `set -euo pipefail`. Handlers print stderr human text only; never JSON. Soft-exits throughout. Appropriate for low-complexity side-effects (frontmatter checks, edit logging) where bash is sufficient and the failure mode should never block tool calls.

### Single Go binary with subcommand dispatch

Every hook entry calls `${CLAUDE_PLUGIN_ROOT}/bin/harness hook <event-name>`. The binary owns hook protocol, JSON schema emission, decision logic, and per-event handlers. One executable, many entry points. Appropriate when the plugin's logic is large enough to warrant a compiled engine and when consistent JSON output across all hooks matters (the binary alone knows the full schema).

### Python stdlib runner with external player probing

Hooks call `python "${CLAUDE_PLUGIN_ROOT}/runner/run.py"` (a single Python file using only stdlib). Runner shells out to system audio binaries (`mpg123`, `ffplay`, `paplay`, `aplay`, `afplay`, PowerShell players) by probing the platform. No Python venv, no third-party packages. Appropriate when the only "dependencies" are system tools the user already has, the failure mode should be silent skip, and zero-install is the design goal.

## Hook failure posture

How hook failures relate to tool execution.

### Fail-open by default

Hooks exit 0 on missing binary, missing dependency, or handler error. Stderr may carry an advisory message; stdout is empty. Claude Code receives "no decision / proceed normally." Explicitly documented in shim comments ("Never print JSON here — we don't know which hook/command is being called and emitting the wrong schema breaks the hook protocol"). Appropriate when the plugin is observational (audio, tracking, ingestion) and should never block the user.

### Fail-closed on judgment flag

Specific hooks return `{"permissionDecision": "deny", "permissionDecisionReason": ...}` when an embedded agent or rule detects a violation (secrets in commit, TODO markers, injection patterns). Fail-open is the baseline; fail-closed is opt-in per-hook based on what the handler observed. Combines well with inline `type: agent` hooks (above) where the agent's judgment is the gating signal.

## Bin distribution and platform handling

How user-facing CLI binaries are shipped and resolved.

### Cross-platform shim dispatching to pre-built binaries

`bin/<name>` POSIX shell wrapper resolves `uname -s`/`uname -m` and `exec`s the matching pre-built binary (`bin/<name>-darwin-arm64`, `bin/<name>-linux-amd64`). Platforms not built receive silent no-op (exit 0, stderr diagnostic). Zero-install at runtime; constrained by which architectures the author cross-compiles. Linux ARM64 and Windows often gaps; graceful degradation means users get no error, just no functionality.

### Bash wrapper with interpreter probing

`bin/<name>` bash script probes `python3 → python → py`, runs a smoke `python -c "import sys"` to defeat the Microsoft Store `python3.exe` stub on Windows, then `exec`s the sibling `<name>.py`. Sibling `<name>.cmd` provides a Windows batch entry. More defensive than relying on the Python shebang alone; addresses Git Bash on Windows specifically. Files often have non-exec permission (100644) on the assumption Claude Code's plugin cache adds `bin/` to `PATH` and shell resolution honors the shebang via `bash <path>`.

## Dependency installation

How the plugin gets its runtime code on the user's machine.

### Zero-install — stdlib + system binaries only

Plugin uses only the runtime's standard library plus probes for system tools (audio players, `gh`). No `requirements.txt`, no `package.json`, no install step. Failure mode is silent skip if a system tool is missing. Constrains the plugin to features achievable in stdlib; trades capability breadth for install simplicity.

### Committed binaries — clone is install

Pre-built binaries live in the git tree. Cloning the plugin is the install. Repo size is the cost (~33MB of cross-compiled Go binaries per clone). Eliminates network calls at install/session-start; ineligible for plugins whose code can't be statically compiled into a single binary.

### SessionStart-driven npm install with diff-based change detection

A `SessionStart` hook script (`ensure-mcp.sh`) runs on every fresh/resumed session, byte-compares (`diff -q`) a committed `package.json` against a cached copy in `${CLAUDE_PLUGIN_DATA}/...`, and runs `npm install` only when they differ. On install failure, removes the cached copy so the next session retries; never hard-fails the hook. Combines with split install locations (below) to handle ownership-driven storage decisions.

### Ownership-based install location split

Third-party MCPs install to a shared user-home directory (`${HOME}/.<framework>/mcp/`) — amortizes download across plugin versions, decouples lifecycle from plugin updates. First-party bundled MCPs ship inside `${CLAUDE_PLUGIN_ROOT}/mcp/<name>/dist/` with their dependencies installed to `${CLAUDE_PLUGIN_DATA}/<name>/node_modules/` at first session start, wired together via `NODE_PATH` in `.mcp.json`. The axis is "we own the code" vs. "someone else does"; the install-location mechanic follows ownership rather than runtime.

## Session context loading

How the plugin contributes to the model's context at session start.

### SessionStart hook for setup, no context emission

`SessionStart` runs install/migrate/validate work but emits no `hookSpecificOutput.additionalContext`. Context is contributed indirectly when slash commands or skills run (e.g., RAG queries via MCP tools). Appropriate when context is request-driven, not session-startup-driven.

### SessionStart + UserPromptSubmit hook chain for context injection

`SessionStart` fires `memory-bridge` and similar handlers; `UserPromptSubmit` chains 5-6 hooks (`memory-bridge`, `inject-policy`, `track-command`, `fix-proposal`, `breezing-signal`) that inject context into every prompt. Matchers narrowed (`startup|resume`, skipping `clear`/`compact`) so PreCompact/PostCompact handlers can do compact-aware context preservation separately. `once: true` prevents duplicate fires within a session.

### SessionStart purely for side-effects

SessionStart matchers (`startup`, `resume`, `clear`, `compact`) each play a distinct audio cue. No context injection, no install logic. Each sub-event gets its own registration with a synthetic handler name; matcher routing lives in `hooks.json` rather than handler code.

## Live monitoring

Whether the plugin runs background watchers separate from hook events.

### `monitors.json` with single watcher

`monitors/monitors.json` declares one monitor (`harness-session-monitor`) with `when: always` that polls workspace state for drift signals. Reuses the same hook-binary subcommand surface (`bin/harness hook session-monitor`) so monitors and hooks share one binary and one dispatch plane. Version-floor declared in README ("v2.1.105+ recommended (PreCompact hook + monitors manifest)").

### Status line via user-settings mutation

The plugin ships a status-line script and provides a CLI subcommand (`<plugin> statusline install`) that mutates the user's `~/.claude/settings.json` to register the script. Plugin manifest does not declare statusline capability. Pros: explicit user opt-in. Cons: uninstall does not automatically reverse the mutation; statusline registration outlives plugin removal unless the user runs `<plugin> statusline uninstall`.

### None

No background watchers, no status line. Plugin operates purely through hook events and slash commands.

## Documentation set

Which docs the repo ships at root.

### Full triad — README + CHANGELOG + ARCHITECTURE + CLAUDE.md

`README.md` user-facing, `CHANGELOG.md` (often Keep-a-Changelog format), `docs/ARCHITECTURE.md` developer-facing, `CLAUDE.md` agent-facing. Sometimes paired with localized mirrors (`README_ja.md`, `LICENSE.ja.md`) when the project is bilingual. Multiple `docs/` subdirectories (`docs/architecture/`, `docs/plans/`, `docs/private/`, `docs/evidence/`) accumulate over the project's life.

### README + CHANGELOG + agent doc only

No standalone `ARCHITECTURE.md`. Architecture is sketched inside `CLAUDE.md` next to operational procedures. Appropriate when the project is small enough that architecture discussion fits in a section of the agent doc.

### CHANGELOG with "Why" and "Migration" subsections

Beyond Keep-a-Changelog's prescription, each release entry adds a `Why` section (decision rationale, sometimes citing external docs) and a `Migration` checklist for consumers. CHANGELOG functions as design-decision log, not just release notes. Significantly more substantive than typical CHANGELOGs.

## Testing strategy

What the project tests and how.

### Bash-test aggregator + parallel language-native tests

A single `tests/validate-plugin.sh` orchestrates ~60 individual `tests/test-*.sh` files; CI does not call them individually. Parallel job runs language-native tests (`go test ./...`, `go vet`, `go build`). Bash tests cover plugin structure, frontmatter, manifest consistency; language tests cover the engine.

### Smoke-only Python import + subcommand exercise

Single `smoke.yml` workflow runs `python -c "import hook_runner"` against canonical and packaged paths, invokes every CLI subcommand once (`audio-hooks.py test all` dispatches all 26 hooks), and runs a `--check` plugin-sync verification. Matrix across OS × Python versions (`ubuntu × windows × macos × 3.9 × 3.12 × 3.13`, fail-fast: false). Catches runtime regressions; does not validate schemas.

### None

No test files, no CI workflow. Bug-detection burden falls entirely on consumers and human review.

### Retroactive CI as documented regression response

CI added in direct response to a specific shipped bug; CHANGELOG entry explicitly cites the regression that motivated each gate. Commit history reads as "no CI → broken tag → add CI gate that reproduces the bug" — clean case study of post-incident gate accumulation.

## Marketplace validation

Whether the marketplace and plugin manifests are validated automatically.

### Custom in-repo validator

`tests/validate-plugin.sh` (39-item structural check) plus `scripts/ci/check-consistency.sh` (templates/refs/version/hooks) run on every PR and push. Predates the public `claude plugin validate` CLI; project has not migrated. Validators are project-specific assertions, not schema validation against the public spec.

### Implicit via runtime exercise

CI invokes the plugin's CLI test surface (`<plugin> test all`) which dispatches every registered hook. If `hooks.json` points at a nonexistent handler, the test fails. Catches reference integrity but not schema drift.

### None

No automated validation. Bad commits ship; consumer failures are the discovery mechanism.

## Multi-harness distribution

Whether the plugin targets more than one agent harness from the same source.

### Single-harness (Claude Code only)

Plugin manifest, hook scripts, components scoped to Claude Code's plugin protocol. No siblings.

### Dual-harness (Claude Code + Gemini CLI)

Single source tree carries `.claude-plugin/plugin.json` AND `gemini-extension.json`; commands are `*.toml + *.md` pairs designed to be harness-agnostic; hook scripts in `hooks/scripts/` (not `.claude-plugin/hooks/`) so both harnesses can wire them via their respective registration files (`.claude-plugin/hooks.json` vs `hooks/gemini-hooks.json`). Hook scripts guard on `${CLAUDE_PLUGIN_ROOT:-}` presence to skip Claude-only logic when running under Gemini. Three-file version sync rule (`plugin.json`, `marketplace.json`, `gemini-extension.json`) lives in prose. Deliberate decision recorded in CHANGELOG that the plugin's distribution model differs per harness (e.g., bundled MCP for Claude, install-dir model for Gemini).

### Multi-runtime skill mirrors

Skills authored once in `skills/`, then mirrored to sibling directories for other runtimes (`skills-codex/`, `codex/.codex/skills/`, `opencode/skills/`) by build scripts (`scripts/build-opencode.js`, `scripts/sync-skill-mirrors.sh`). A dedicated CI workflow (`opencode-compat.yml`) fails if mirrors drift. Differs from dual-harness distribution above by mirroring derivative copies rather than running the same files through divergent registration manifests.

## Sandbox and security posture

Whether the plugin declares network/filesystem boundaries.

### Default — no sandbox declaration

`settings.json` has no `sandbox` block; plugin runs with whatever permissions Claude Code grants by default.

### Explicit deny lists for cloud metadata and filesystem paths

`.claude-plugin/settings.json` declares `sandbox.failIfUnavailable`, `sandbox.network.deniedDomains` (including `169.254.169.254`, `metadata.google.internal`, `metadata.azure.com`), and `sandbox.filesystem.{denyRead, allowRead}` blocks. Explicit SSRF-defense posture; makes the plugin's threat model legible from the manifest.
