# Sample

Pass-1 Phase-1a partial for bin 15. Functional decomposition of `jmylchreest--aide.md`, `jxw1102--flipper-claude-buddy.md`, and `lukasmalkmus--moneymoney.md`, organized by role with implementation paths as sub-sections.

## Marketplace discoverability

How a marketplace surfaces enough metadata for a consumer scanning a registry to decide whether to install — name, description, categories/tags/keywords, schema reference.

### Single root manifest with rich metadata wrapper

A single `.claude-plugin/marketplace.json` at repo root carrying a `metadata.{title, description, categories, tags}` block at the top level, in addition to per-plugin entries. Categories and tags apply at marketplace scope; per-plugin discoverability rides on `keywords` inside the plugin entry. Appropriate when the marketplace is single-plugin and the metadata wrapper is the natural place to advertise the whole repo. Constrains nothing about how the plugin source resolves, but does add a second source of truth for description/version that must be kept in lockstep with `plugin.json`.

### Single root manifest with flat top-level

A `.claude-plugin/marketplace.json` at repo root with top-level `description` and `owner` only — no `metadata.{...}` wrapper, no top-level `version`, no `pluginRoot`. Per-plugin discoverability rides on `category` plus `tags` arrays (3-element-ish) on the plugin entry, with `$schema` pointing at Anthropic's schema URL. Distinguishable from "rich metadata wrapper" by the absence of the wrapper key and from "minimal manifest" by the presence of `category`/`tags` on the entry. Common pitfall: marketplace `tags` and the GitHub repo `topics` field drift apart, so a consumer reading only the manifest sees fewer hints than the repo surface.

### Minimal manifest with no entry-level discoverability

A `.claude-plugin/marketplace.json` carrying only `name`, `owner`, and `plugins[]` — no top-level `metadata`, no `description`, no `$schema`, and no `category`/`tags`/`keywords` on the plugin entry. Discoverability metadata, if any, lives only in the plugin manifest's `keywords` field, which surfaces inside the plugin but not at marketplace scan time. Appropriate for narrow personal-use plugins where the author doesn't expect external scanning. Constrains tooling that surfaces categories — those readers see the plugin as untagged.

## Plugin source binding

How a marketplace entry locates the plugin's manifest and files from a consumer install.

### Relative source at repo root

`"source": "./"` — the plugin lives at the same path as the marketplace manifest. Single-plugin pattern; the marketplace entry doubles as the plugin's directory pointer. No remote re-fetch; install resolves entirely from whatever ref the consumer added. Appropriate when one repo equals one plugin and there's no need to point at a sibling tree. Implies the marketplace is the plugin's authoritative repo, not an aggregator.

### Git-subdir self-pointing

A `git-subdir` source whose `url` is the same repo as the marketplace manifest, with `path: <subdir>` naming a subdirectory. `plugin install` re-fetches the plugin from GitHub even when the consumer has already cloned the marketplace — a network round-trip that a `relative` source would avoid, but `git-subdir` permits standalone marketplace-add without expecting users to clone. Appropriate when the author wants users to install via `claude plugin marketplace add <owner>/<repo>` directly without cloning. Trade-off is the redundant fetch when a clone already exists locally.

### Default discovery (no explicit component fields)

`plugin.json` carries metadata only — no `skills`, `commands`, `agents`, `hooks`, or `mcpServers` fields. Components are picked up by directory convention (`skills/<name>/SKILL.md`, `hooks/hooks.json`, `bin/`, etc.). The simplest binding shape; works when convention covers everything the plugin needs.

### Inline-config plugin.json

`plugin.json` declares `mcpServers` and `hooks` as inline config objects (no external `.mcp.json`, no separate `hooks.json`). Skills and agents discovered by path convention from `skills/**/SKILL.md` and an unconventional location like `src/agents/*.md`. Appropriate when a plugin needs more declarative control than convention gives but doesn't want extra files. Constrains the manifest size — non-trivial inline `hooks` blocks with many event groupings inflate `plugin.json` significantly.

## Version authority

Where the plugin's version number is the canonical truth and what enforces consistency across copies.

### Single-source plugin.json

`plugin.json` is the only place the version is declared. Marketplace entry omits `version`; runtime scripts (binary-download shims, hook scripts) read from `plugin.json` directly. No drift risk because there's only one location. Appropriate when the marketplace entry is happy to inherit version from the plugin manifest at install time.

### Dual-source plugin.json + marketplace.json with manual lockstep

Both `plugin.json` and the marketplace entry carry `version`. Lockstep enforced manually by the author at release time, sometimes via a release-target `sed` across an explicit `VERSION_FILES` list. Drift risk if only one is updated; nothing verifies them at commit time. Appropriate when the marketplace entry needs a self-contained display version. Constraint: bumping the version requires editing N>1 files and there's no structural enforcement.

### Multi-artifact lockstep across N>2 manifests

Version mirrored across plugin manifest plus one or more sibling artifact manifests — `package.json`, `pyproject.toml`, firmware `.fam` `fap_version`, source-embedded version strings (`ui.c` constants, Go `-ldflags`-injected vars). Coordination via a release checklist or `Makefile` `release` target; no structural verification. Appropriate when the plugin is one artifact among several in a multi-product repo. Constraint: a release commit must touch every artifact's version field or one of them silently lags.

## Channel distribution

How a marketplace exposes (or chooses not to expose) parallel release channels.

### No split, single track

Users pin via `@ref` (commit, tag, branch) if they want a specific version; the only "version" surface is the latest tag on `main`. No `stable-tools`/`latest-tools` segregation, no dev-counter branch discipline. Appropriate for low-volume plugins where channel infrastructure adds ceremony without benefit. Constrains rollback to "ask users to pin an older ref."

### Floating snapshot binary alongside single-track plugin

The plugin itself is single-track, but a separate binary-distribution release tag (e.g., `snapshot`) is force-recreated on every push to main as a prerelease. Used by a binary-download wrapper as a fallback URL — not a marketplace channel, a binary channel. Appropriate when the plugin ships a downloadable native artifact with a faster cadence than the plugin's semver. Constrains binary consumers caching by tag SHA against the floating tag — they see silent moves.

## Version control and release cadence

Branching shape, tag placement, pre-release suffixes, dev-counter discipline.

### Tag-on-main, plain semver

Linear history on `main`; tags placed on `main` commits. Tag format `v<x.y.z>` (or shorter `<x.y>`); no release branches, no pre-release suffixes. Appropriate for solo-author and small-team plugins where serialized release-on-main is sufficient.

### Tag-on-main with synthesized dev version inside binary only

Plugin manifest carries plain semver tracking releases. Dev builds of an embedded binary synthesize a `-dev.N+sha` suffix at build time via `git describe --tags --match 'v*' --always --long` and `-ldflags`, never applied to git tags. Wrapper script recognizes the dev marker (`version.includes("-dev.")`) and applies looser version-comparison rules (accept base semver `>=`). Appropriate when binary builds out-pace plugin releases and the wrapper needs to discriminate locally-built vs released binaries.

### Manual multi-string release checklist

A `CLAUDE.md`-prescribed N-step manual checklist (commit clean → update CHANGELOG → bump fam version → bump source version string → bump plugin.json → bump pyproject.toml → commit → tag → push). CI reacts to tags but does not author them. Appropriate for multi-artifact repos where automation overhead outweighs the manual drift risk. Constraint: any forgotten step ships silently.

## Plugin-component registration

Whether components are inline in `plugin.json` or discovered from convention paths, and what frontmatter shapes they use.

### Convention-only discovery

`plugin.json` carries no component fields. Skills found at `skills/<name>/SKILL.md`, hooks at `hooks/hooks.json`, bin at `bin/`. Simplest pattern; surface area in the manifest is purely metadata.

### Inline manifest with high-fan-out hooks

`plugin.json` inlines `mcpServers` and `hooks` (10+ event types, 17+ total registrations all matchering `*`). Skills and agents discovered by path convention. Appropriate when the plugin wants centralized declarative control. Constrains tool-call latency — every tool invocation spawns multiple hook processes.

### Hooks-json with broad event coverage

A standalone `hooks/hooks.json` registering many event types (15+ including `Notification`, `StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`) each with empty-string matchers (fire on everything). Several may not be in the canonical Claude Code event list — the plugin anticipates or relies on emerging events. Constrains the plugin to versions of Claude Code that emit those events without a declared version floor; older hosts silently get a subset.

### Skill `triggers` array with fuzzy matching

Skills declare `triggers: [phrase1, phrase2, ...]` (a custom array of 3-10 short phrases per skill) in addition to or in place of `description`. A `UserPromptSubmit` hook fuzzy-matches the prompt against triggers (typo-tolerant) and injects up to 3 matching skills' content via `additionalContext`. Distinct from Claude Code's built-in `description`-based activation; layers on top rather than replacing. Appropriate when activation precision matters and the plugin is willing to ship its own matcher. Constrains skill authors to maintain trigger arrays in addition to descriptions.

### Skill `allowed-tools` with permission-rule syntax

Skill frontmatter carries `allowed-tools` using Claude Code's permission-rule syntax (`Bash(<cmd> <args> *)` form), explicitly enumerating safe read-only invocations and deliberately omitting write-side commands so they trigger permission prompts. Frontmatter also carries `name`, `description`, `user-invocable`, `argument-hint`. Appropriate when the plugin wants tool-level allowlisting without per-tool hooks.

### Skill `allowed-tools` with plain tool names

Skill frontmatter carries `allowed-tools: Bash` (no permission-rule brackets). Looser than the permission-rule form; relies on user-level permission gates rather than skill-declared per-command allowlists. Appropriate when the skill intends to be broadly capable and tool gating is owned elsewhere.

### Authored agents not registered as plugin agents

A directory like `src/agents/*.md` contains files with Claude-Code-style agent frontmatter (`name`, `description`, `defaultModel`, `readOnly`, `tools` array). They are not wired via `.claude-plugin/agents/` and there's no `agents` field in `plugin.json` — they're consumed by an internal swarm/orchestration skill rather than registered as Claude Code sub-agents. Constrains discoverability: a reader scanning by directory convention may misidentify them as plugin-registered agents.

## Dependency installation

How runtime dependencies (Python packages, Node modules, native binaries) reach the user's machine on first use and on update.

### Python venv with md5-of-source change detection

A SessionStart bash hook concatenates `pyproject.toml` plus all source files matching a glob (e.g. `bridge/*.py`), pipes through `md5 -q` (BSD) with fallback to `md5sum | cut -d' ' -f1` (GNU coreutils) and a final `|| echo "none"` trapdoor for minimal systems. Stored as `.installed-hash` in the venv directory; compared on each session start. Mismatch → recreate venv with `python3 -m venv` and `pip install --force-reinstall <pkg>`; running daemon with old hash is killed first. Lighter than `diff -q` (no reference tree needed), more precise than existence-only checks. Constraint: the `"none"` trapdoor on a busybox-style minimal system can pin the install forever or trigger a re-install every session. The marker is interpreter-version-blind — a system Python upgrade isn't detected.

### Node modules self-heal at every MCP launch

A bin-wrapper invoked by Claude Code as the MCP server entry detects missing `node_modules` (gitignored, lost after marketplace `autoUpdate`) and runs `bun install --frozen-lockfile` inline before delegating. Lazy `require('cross-spawn')` after install completes lets the bootstrap survive starting from empty. No SessionStart-registered install step; every MCP launch self-heals. Appropriate when the plugin can't rely on SessionStart firing before the MCP client connects. Constrains the runtime: Bun (or Node) must be on user PATH; the wrapper has no graceful-degradation path if it isn't.

### Native binary downloaded on first use with version-stamp idempotency

A SessionStart hook (or lazy bin-wrapper, or both) downloads a pre-built native binary from a GitHub release into `${CLAUDE_PLUGIN_DATA}/bin/<name>`. Change detection via a sibling `mm.version`-style stamp file written *only after* successful extraction (`tar xzf` then `chmod +x` then `xattr -d com.apple.quarantine` then write stamp). A failed download leaves no stamp; the next invocation re-attempts cleanly without explicit `rm`-on-failure. Version compared against `plugin.json`'s `version` (read with `jq -r`). Appropriate when the binary is a separately-cross-compiled artifact too large to vendor in git. Constraint: the asset URL pattern is hardcoded in the shim; release-workflow asset-name changes must be coordinated.

### Native binary with versioned-then-floating download URLs

Wrapper attempts a versioned URL (`releases/download/v<plugin-version>/<binary>`) first, then falls back to `releases/latest/download/<binary>`. Mitigates a race where the marketplace pulls the new plugin version before the release workflow has finished uploading binary artifacts. `releases/latest/...` is the floating-tag fallback, paired with a separately-maintained `snapshot` prerelease tag for dev builds. Constraint: dev/release version distinction is encoded in version-string suffix matching (e.g., `version.includes("-dev.")`) — three-state logic (release/dev/unknown) inside the wrapper.

### Cargo/Homebrew user install with plugin-managed cache fallback

The plugin's bin shim tries the user's own install first (`cargo install <pkg> --locked` or `brew install <tap>/<pkg>`), then a plugin-managed binary at `${CLAUDE_PLUGIN_DATA}/bin/<name>`, then downloads from GitHub releases as a last resort. PATH-cleaning via `grep -vFx "$self_dir"` on PATH entries prevents the shim from finding itself. User's install is authoritative even if it's a different version than `plugin.json` declares — deliberate trade for ergonomics. Appropriate when the upstream binary is published to multiple package managers and users routinely install it that way.

## Bin-wrapped CLI distribution

A `bin/<name>` shim (or wrapper) that resolves the real implementation and forwards arguments. Distinct from "binary download" — the shim is always present at install, the binary may not be.

### TypeScript bun-shebang launcher with download fallback

`bin/<name>-wrapper.ts` carrying `#!/usr/bin/env bun`. Self-heals `node_modules`, verifies the native binary exists at `bin/<name>[.exe]`, downloads/version-checks via a sibling downloader module, forwards argv to the binary via `spawnSync` with `stdio: "inherit"`. Cross-platform `.exe` suffix branching, GOOS/GOARCH-specific binary naming. Plugin-root resolution precedence: custom env var > `CLAUDE_PLUGIN_ROOT` > `realpathSync`-based script-dir fallback for symlink-via-`node_modules/.bin/` installs. Bun-specific calls (`Bun.sleepSync`) bind the wrapper to Bun even though the downloader supports Node. Constraint: Bun on user PATH is a hard prerequisite; no graceful error if missing.

### Bash three-tier resolution shim

`bin/<name>` carrying `#!/usr/bin/env bash`, mode 100755, three resolution tiers:

1. PATH cleaned of `self_dir` (canonicalized via `cd "$(dirname "$0")" && pwd`), then `command -v <name>` — exec user's install if found.
2. Plugin-managed cache at `${CLAUDE_PLUGIN_DATA}/bin/<name>` with version-stamp match — exec if version aligns.
3. Lazy download from GitHub release — curl + tar xzf + chmod +x + macOS quarantine strip + exec.

Appropriate when the upstream binary is a distinct user-installable product. Constraint: PATH-cleaning is fixed-string match; trailing slash or case differences in PATH entries would not be stripped.

### Plugin-root resolution with custom env-var precedence

Wrapper reads a plugin-specific env var (`AIDE_PLUGIN_ROOT`) before `CLAUDE_PLUGIN_ROOT`, then falls back to `realpathSync`-canonicalized script-dir. Custom-var-first rationale: the same wrapper ships to multiple AI-coding-assistant ecosystems (Claude Code, OpenCode, Codex CLI), and `CLAUDE_PLUGIN_ROOT` is treated as a Claude-Code-specific fallback rather than the primary. Constraint: a user invoking the wrapper directly without setting either env var falls through to the script-dir branch, which is wrong if they installed only `bin/` somewhere.

### Daemon launcher (no bin-wrapper)

No `bin/` directory. The plugin entry point is reached via `"$VENV_DIR/bin/python" -m <pkg>` directly from the SessionStart hook, spawned with `nohup ... &` so the daemon detaches. Lifecycle managed via `/tmp/`-based socket/PID/refcount files. Users wanting to inspect or restart the daemon do so via tail-the-log + kill-the-PID, not a CLI. Appropriate when the plugin's surface is a long-running background daemon rather than a per-invocation CLI.

## Dependency-install change detection

How a plugin decides whether to re-run install on a session that already has dependencies present.

### Source-content hash via cross-platform md5

Concatenate dep manifest plus glob of source files; pipe through `md5 -q` (BSD) → `md5sum | cut` (GNU) → literal `"none"` fallback. Stored in the venv directory; compared each session. Recomputes deterministically across edits to any included file. Constraint: the `"none"` fallback can pin install state on a minimal system.

### Existence-plus-version-compare

Existence of `node_modules` directory or `bin/<name>` binary plus `<binary> version` output parsed with regex and SemVer-compared (`versionGte`). No content hashing. Cheaper than a hash but blind to manifest edits that don't bump the binary's reported version; relies on the binary's version string being reliable.

### Version-stamp file written after success

`<binary>.version` text file containing the version string, written *only after* successful extraction or install. Compared against `plugin.json`'s `version` via `jq -r '.version'`. Failure leaves no stamp → next run retries cleanly. Compare/contrast with marker-written-before-extraction approaches that need explicit `rm`-on-failure recovery.

### `diff -q` against cached manifest copy

A SessionStart hook compares the live manifest (e.g., `pyproject.toml`) to a cached copy via `diff -q`; mismatch triggers reinstall. Not directly observed in this bin's samples but referenced as the contrast pattern to source-content-hash and existence-plus-version-compare.

## User configuration

How user-tunable settings reach the plugin's runtime — manifest-declared `userConfig`, env vars, external config files.

### `userConfig` schema with typed fields

`plugin.json` declares a `userConfig` block with field entries each carrying `title`, `type`, `description`, and `sensitive` (boolean). Three-field configs are common; `sensitive: false` is set deliberately on device-identifier fields to distinguish from omitted (anti-pattern). No `default`, no `enum` — `transport` accepts a small set of strings without typed enumeration. Appropriate when the plugin needs Claude-Code-surfaced config at install time. Constraint: free-form string fields silently fall through to default-handling if mistyped.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var forwarding

A SessionStart hook reads `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (the substitution channel for `userConfig` values) and re-exports them under plugin-specific names (e.g., `FLIPPER_<KEY>`). Decouples manifest-key naming from the daemon's env-var contract; either side can evolve independently. Appropriate when the plugin wires user config into a daemon or subprocess that has its own naming convention.

### Out-of-band env vars (no `userConfig`)

No `userConfig` in `plugin.json`. Configuration via a documented set of env vars (`AIDE_DEBUG`, `AIDE_FORCE_INIT`, etc.) plus a few hardcoded values in the manifest's `mcpServers.env` block. Users discover the knobs only by reading the README; Claude Code's marketplace UX has no way to surface them. Appropriate when the plugin has many fine-grained knobs that don't fit a flat config schema or evolve too fast for manifest churn.

### External config file owned by the binary

Configuration lives at `~/.config/<name>/config.toml`, read by the binary itself, not by the plugin surface. No `userConfig`, no `CLAUDE_PLUGIN_OPTION_*`. Appropriate when the binary is a standalone CLI with its own config conventions and the plugin is just a wrapper. Constrains the user — they configure via the binary, not via Claude Code.

## Tool-use enforcement

How the plugin participates in pre-/post-/permission decisions on tool calls.

### Multi-PreToolUse fan-out with matcher `*`

Five PreToolUse hooks all matchering `*` — per-agent tool tracking, write-protection, read-only/agent-tool-access enforcement, context-window pressure, search-input augmentation. Every tool invocation spawns multiple hook processes. Appropriate when the plugin layers several orthogonal pre-call concerns. Constrains latency: hook timeouts (2-60s per hook) compound under fan-out.

### PostToolUse-only for notification + observation

PostToolUse hooks matchering `*` for tool-event recording into a memory store, status-line refresh, comment-validation on edits, context-pruning. PreToolUse not used. Appropriate when the plugin observes rather than gates.

### PostToolUse Bash-matcher one-shot skill nudge

A single PostToolUse with matcher `"Bash"` checks the bash command for a word-boundary regex match (`(^|[^a-zA-Z0-9-])<name>($|[[:space:]])` to exclude substrings). On match, emits a one-shot per-session `<system-reminder>` via `hookSpecificOutput.additionalContext` pointing at a skill. Marker file at `${TMPDIR}/.<name>-skill-nudge-${session_id}` ensures one-shot. Rare pattern: most nudge hooks fire every time or use PreToolUse blocking; this is one-shot informational PostToolUse. Appropriate when the plugin wants to nudge agents toward a skill without blocking. Constraint: `$PPID` fallback when `session_id` is empty can stale-trigger across sessions.

### PermissionRequest delegated to hardware

A `PermissionRequest` hook routes the allow/deny decision to a physical input device (Flipper Zero) via a 60-second socket round-trip. Emits `hookSpecificOutput.decision` JSON with `{behavior: "allow"}` / `{"deny"}` / `{"ask"}`. On no-bridge or timeout the hook exits 1 to fall back to Claude's native dialog. Generalizes to any "remote approval" surface. Constraint: the timeout is non-configurable; user walks away → Claude waits a full minute.

### PermissionRequest dormant in source

A `permission-handler.ts` (or similar) exists with header comment "OPT-IN: This hook is NOT registered in plugin.json by default. To enable, add a PermissionRequest entry." Present in source, absent in manifest. Constraint: a reader grepping hook registrations won't find it; only the file header reveals it.

### Output convention: stdout-JSON-only

All hooks emit `JSON.stringify({continue: true/false, ...})` to stdout. Human-readable logs go to stderr and to file logs (e.g., `.aide/_logs/*.log`). Hook-crash invariant: even on exception, stdout still emits valid JSON via centralized `outputContinue()` helpers and global `process.on('uncaughtException')` / `unhandledRejection` handlers. Three-channel discipline: structured stdout, narrative stderr, file logs. Constraint: any hook that writes plain text to stdout breaks the harness.

### Output convention: structured-where-it-matters, silent elsewhere

PermissionRequest hook writes structured JSON (`hookSpecificOutput.decision`); sound/notification hooks exit silently with `sys.exit(0)`; failure-path scripts write to stderr. No central emit helper; each script re-implements the socket-send-with-swallow pattern. Appropriate for plugins where most hooks are side-effect-only. Constraint: the inconsistency means a reader can't infer hook output shape from the file.

### Output convention: jq-built JSON

Hook script uses `jq -n` to construct `{hookSpecificOutput: {hookEventName, additionalContext}}` JSON for stdout. No central emit helper; jq is the formatting library. Appropriate for shell hooks where embedding JSON construction in bash is unwieldy. Constraint: jq dependency on user PATH (typically present on macOS dev machines but not universal).

### Failure posture: fail-open via try-catch + continue

Every hook's `main()` is inside `try { ... } catch { outputContinue(); }`. Centralized helpers emit `{"continue": true}` and `process.exit(0)`. Pattern observed in 3/3 sampled hooks. Appropriate when an erroring hook should never block the user. Distinguishes deliberate denials (`continue: false` with `message`) from unexpected errors.

### Failure posture: pipefail with selective suppression

`set -euo pipefail` halts on errors early; later hook steps deliberately suppress with `|| true` or `2>/dev/null || true` so notification failures don't propagate. Final `exit 0` regardless. Mixes strict-by-default with explicit per-step graceful degradation. Appropriate for shell hooks that interact with optional hardware/services.

## Session context loading

Whether and how the plugin injects content into the model's context at session boundaries.

### SessionStart `additionalContext` for welcome state

Hook emits `hookSpecificOutput.additionalContext` containing a built welcome message — current state, recent memories, notices. Appropriate for plugins maintaining persistent context across sessions.

### UserPromptSubmit fuzzy-matched skill injection

UserPromptSubmit hook fuzzy-matches the user prompt against YAML-frontmatter `triggers` arrays in `skills/**/*.md` (and per-project overrides like `.<name>/skills/**/*.md`), picks up to N matching skills, and returns their content via `hookSpecificOutput.additionalContext`. Skill discovery layered across project-local > plugin-bundled > user-home. Appropriate when activation precision matters more than Claude Code's built-in description matching. Constraint: fuzzy-match tolerance allows unintended activation on typos.

### SessionStart matcher `*` (or absent)

Hook matcher set to `"*"` (or omitted, which defaults to all sub-events). Fires on startup, clear, compact, resume — same handler regardless of source. Hook may discriminate internally on a `source` field. Constraint: SessionStart fires more than once per user session, so the hook must be idempotent or guard work behind cheap checks.

### SessionStart for non-context work only

Hook is registered but never sets `additionalContext` — its job is dep install, daemon launch, stale-state cleanup, or binary download. The "context" purpose is decoupled from session boundary in this plugin.

## Live monitoring and notifications

Plugin-driven status updates, notifications, or live displays during a session.

### Hook-driven file-write status line

No `monitors.json`. A PostToolUse hook writes status to `.<name>/state/hud.txt` and a Claude Code status-line integration reads from it. A SessionStart hook installs a wrapper script (`~/.claude/bin/<name>-hud.ts`) that discovers the newest installed plugin version under `~/.claude/plugins/cache/*/` and delegates. Decouples user-facing HUD from plugin upgrades — new versions provide new HUD scripts; the wrapper always finds the newest. Constraint: side-effect on the user's home directory not declared anywhere in the plugin manifest.

### Hardware-device notification fan-out

Hook events fan out to a physical device (Flipper Zero) via a daemon socket — sounds, vibration, display text. Hook-event variety is used to discriminate notification cues at fine granularity. Includes events outside the canonical Claude Code hook list (`StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`). Constraint: events that aren't yet emitted by a given Claude Code version silently no-op; no version-floor declaration.

### Cross-hook coordination via flag files

A `${TMPDIR}/<name>.skip-stop.flag` file is written by one hook (`on-post-tool-use.py`) and read by a sibling hook (`on-stop.sh`) to suppress a duplicate notification when the user has already triggered one via a skill. Filesystem-flag coordination between hook scripts that would otherwise race on a shared output device. Appropriate when hooks share a serial output (display, sound, hardware) and need cheap mutual-exclusion.

### No live monitoring

Plugin does not register monitors, status-line writers, or notification hooks. Appropriate for read-only CLI plugins where ambient feedback is unnecessary.

## Plugin-to-plugin dependencies

Whether the plugin declares `dependencies` on other plugins, and what tag/format conventions support that.

### No declared plugin dependencies

`dependencies` field absent. Single-plugin marketplace; cross-plugin coupling not attempted. Real runtime dependencies on host-side packages, daemons, firmware, or system binaries are documented in README rather than expressed in `dependencies` (which only addresses other marketplace plugins). Tag format is plain semver (`v0.4.0`) without plugin-name prefix.

## Daemon and IPC lifecycle

Long-running background processes the plugin manages, and how it coordinates them across sessions.

### Refcount-gated daemon with /tmp/-resident state

A SessionStart bash hook is simultaneously a dep-install gate, daemon launcher, stale-state cleaner, and session registrar. The daemon (Python `python -m bridge` via the venv's interpreter, spawned with `nohup ... &`) is started once across N concurrent sessions: each session increments `/tmp/<name>.refcount` on start, decrements on end; daemon killed only at zero. Runtime files in `/tmp/`: `<name>.sock`, `<name>.pid`, `<name>.refcount`, `<name>.log`, `<name>.skip-stop.flag`, `<name>-turn-stats.json`, `<name>-bt-name.cache`. Appropriate for plugins backed by a shared resource (hardware device, service connection) that should be singleton across concurrent Claude Code windows. Constraint: hook does multi-purpose work; reading it for one concern reveals all four.

### Mkdir-based atomic install lock

`bin/.<name>-download.lock/pid` directory created via `mkdir` for atomicity (mkdir is atomic on POSIX); 60-second timeout with forced-remove fallback for stale locks from crashed processes. Used to serialize concurrent install attempts (SessionStart hook + bin-wrapper both calling the downloader). Constraint: a fast SessionStart after a crash blocks up to a minute before forcing the lock.

### No long-running process

Plugin is invoked per-call (CLI shim or MCP server started by Claude Code per tool call). No daemon, no `/tmp/` state, no refcount. Appropriate for stateless or per-invocation tools.

## Testing and CI

What the project tests, what test framework, what CI exercises.

### Multi-stack matrix CI (TS + Go + integration)

`ci.yml` with five-plus jobs: TypeScript (`bunx tsc --noEmit`, `bun run build`, `bunx vitest run`, `bun run lint`); Go (`go test -v -race -coverprofile=coverage.out ./...` per submodule, Codecov upload `continue-on-error: true`); Go-lint (`golangci-lint-action@v9`); cross-stack build verification (`--help` smoke test of compiled binaries); integration (drives hooks with piped JSON: `echo '{"hook_event_name":...}' | bun dist/hooks/<hook>.js | jq -e '.continue == true'`). Triggers on push-to-main + PR-to-main (PRs run twice if merged: once pre-merge, once post on main). Action-pinning by major tag uniformly. Caching via setup-action built-ins (`setup-go cache: true`, `setup-node cache: npm`). Matrix only for binary-build job in release workflow, not for CI proper.

### Rust matrix CI with paths-ignore for plugin surface

`ci.yaml` with fmt + clippy + test + audit + docs jobs. Test matrix `{stable, ubuntu-latest}`, `{MSRV-from-Cargo.toml, ubuntu-latest}`, `{stable, macos-latest}`. Triggers `push: branches: [main]` + `pull_request`, both with `paths-ignore: ["**.md", "LICENSE", ".claude-plugin/**", "skills/**", "hooks/**"]` — plugin-surface edits don't retrigger Rust CI. Caching via `Swatinem/rust-cache@v2`. No shellcheck or hook-script lint. Constraint: pure skill/hook iteration ships without CI signal of any kind on the shell scripts.

### Firmware-build-only CI

Single `build-fap.yml` workflow: `ufbt build` of a Flipper FAP firmware binary, artifact upload, conditional `softprops/action-gh-release@v2` when ref is a tag. Triggers `workflow_dispatch` + `push` with path filter `flipper-app/**` + `tags: '*'`. No pytest, no shellcheck, no manifest validation. Plugin code (Python bridge, hook scripts) ships green even when broken. Appropriate when CI cost is gated by hardware-test impossibility; constraint is unverified plugin shipping.

### Hook integration test via piped JSON

CI integration job pipes a synthesized hook-event JSON to the compiled hook script and asserts `jq -e '.continue == true'` on the output. Drives a real round-trip (hook reads stdin, performs work, emits stdout JSON) without spinning up Claude Code. Appropriate for verifying hook output discipline; constrains to deterministic hooks (stochastic ones would need fuzz harnesses).

### No tests at all

No `tests/` directory, no `pytest.ini`, no test framework configuration. CI exercises only build paths. Appropriate (charitably) when the surface is small and manually validated; constraint is regression detection only via user reports.

## Release automation

Workflow shape for cutting tagged releases.

### Multi-trigger workflow with single-snapshot path

One `release.yml` (28 KB) handles PR CI, main-branch snapshots, and tag releases by gating jobs on `needs.prepare.outputs.is_release` and `github.event_name == 'push'`. `prepare` job computes version (from tag or from `git describe`), then test → build (six-platform matrix, CGO + zig cross-compile, UPX compression on linux/windows-amd64) + build-web + build-grammars (per-language tree-sitter `.so`/`.dylib`/`.dll` from upstream-cloned grammar repos at pinned tags) + build-npm. Tag push → `release` job (softprops/action-gh-release@v2 with `generate_release_notes: true`) + `publish-npm` (`npm publish --provenance --access public` requiring `id-token: write`). Main push → `snapshot` job (delete + recreate `snapshot` tag + prerelease release). `prepare` includes "commit already has release tag — skip" check via `git tag --points-at HEAD` regex. Constraint: snapshot tag force-recreated on every main push; consumers caching by tag SHA see silent moves.

### Dual-workflow split (CI + release)

Separate `ci.yaml` (lint/test/audit) and `release.yaml` (cross-compile + GitHub Release). Release triggers `push: tags: ["v*"]`. Build job: matrix over arch targets, `taiki-e/upload-rust-binary-action@v1` with `dry-run: true` to produce archives, `actions/upload-artifact@v7` to stash. Release job: download artifacts, `taiki-e/create-gh-release-action@v1` with `changelog: CHANGELOG.md` (parses Keep-a-Changelog format), `gh release upload <tag> artifacts/*`. Appropriate when release machinery is non-trivial enough to warrant its own file. Constraint: asset URL pattern (`mm-<target>.tar.gz`) is hardcoded in the bin shim; release-action default-naming changes break the shim silently.

### Tag-conditional step inside build workflow

No dedicated release workflow. Build workflow has a `if: startsWith(github.ref, 'refs/tags/')` step using `softprops/action-gh-release@v2` to attach the built artifact. Default GitHub auto-generated release notes (no body provided to action). Tag pattern `*` is permissive — any tag fires. Appropriate when the release is "attach the artifact, that's it." Constraint: no tag-format gate, no version-match check; an accidental tag publishes a release.

### CHANGELOG-parsing release action

`taiki-e/create-gh-release-action@v1` reads `CHANGELOG.md` (Keep-a-Changelog format) and extracts the section matching the tag's version. Release notes derived from the changelog rather than auto-generated commit log. Appropriate when curated release notes matter and the project commits to Keep-a-Changelog discipline.

### Auto-generated release notes from commits

`generate_release_notes: true` on `softprops/action-gh-release@v2` delegates to GitHub's built-in commit-based note generator. No CHANGELOG.md in repo. Appropriate for projects with conventional-commit-style histories where the tag-to-tag commit list is sufficient. Constraint: regression investigation requires walking tags and comparing auto-generated notes; no human-curated narrative.

## Marketplace validation

CI-side or pre-commit checks on marketplace.json, plugin.json, hooks.json, or skill frontmatter.

### Custom skill-frontmatter linter, not CI-wired

A `scripts/validate-skills.ts` (or similar) implements an inline YAML-frontmatter parser and validates SKILL.md files for required fields (`name`, `description`, `triggers` non-empty array), no duplicate names, basic markdown sanity. Run manually via `bun run scripts/validate-skills.ts`. Not invoked by any CI workflow. Appropriate when the validator exists for local-author use. Constraint: a broken SKILL.md merges green; the validator only catches what authors run.

### No validation

No marketplace.json validator, no plugin.json validator, no hooks.json validator, no skill-frontmatter validator. Manifest typos surface only at `claude plugin marketplace add` time on a user's machine. Default state for plugins that don't invest in CI scaffolding.

## Documentation

What docs the repo carries and where; how the three-doc model (README/ARCHITECTURE/CLAUDE.md or AGENTS.md) is observed or violated.

### Three-doc model with consumer/dev/agent split

Repo root carries `README.md` (consumer-facing), `ARCHITECTURE.md` (developer-facing — note uppercase, less common than lowercase `architecture.md`), and may carry a `CLAUDE.md`. Substantive subsystem READMEs for contributors (e.g., `<lib>/README.md`, `adapters/README.md`). Hosted Docusaurus site mirrors much of the in-repo documentation, with `docs/versioned_docs/version-X.Y.Z/` snapshotted per release. Appropriate for plugins that want both quick-start (README) and deep-dive (ARCHITECTURE) documentation. Constraint: two sources of truth (in-repo + Docusaurus) drift; the hosted version often lags.

### CLAUDE.md as architecture-doc carrier

No dedicated `architecture.md`; architectural content (three-layer diagram, threading model, protocol, runtime files, platform notes) lives inside `CLAUDE.md` at repo root. Combines build commands, architecture, threading rules, protocol reference, runtime files, platform notes, command menu, and release procedure. Blurs the agent-ops vs architecture separation conventional in the three-doc model. Appropriate for smaller projects where one document is easier to maintain.

### CLAUDE.md and AGENTS.md duplicating each other

Both files at repo root carry near-identical content (CLI shape, output formats, exit codes, build, commit format, dependencies, skills). No declared single-source-of-truth pointer. Drift risk on refactor. Appropriate (charitably) when the project supports multiple agent ecosystems whose conventions name the file differently. Constraint: every refactor must touch both.

### CHANGELOG presence and shape

Three observed shapes:

- **Keep a Changelog (1.1.0)** — `CHANGELOG.md` at repo root, SemVer-aligned `## vX.Y.Z` sections, parsed by `taiki-e/create-gh-release-action@v1` for release notes.
- **Custom firmware-scoped CHANGELOG** — `<subsystem>/CHANGELOG.md` (not at repo root), custom `## vX.Y` section format, not parsed by automation. Plugin/host-bridge changes not tracked.
- **Absent** — no CHANGELOG.md anywhere; release notes from `generate_release_notes: true` (auto-generated commit log).

### Community health files absent or sparse

`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md` — none observed across these samples. `LICENSE` (MIT) is universally present.

## License

What license the repo declares and where.

### MIT throughout

`LICENSE` file at repo root (standard MIT text, ~1064 bytes). SPDX `MIT` declared in `plugin.json` and any sibling manifests (`pyproject.toml`, `package.json`). Universal across this bin's samples.

## Multi-consumer plugin packaging

A single codebase packaged for multiple AI-coding-assistant ecosystems.

### Tri-target same-codebase plugin

Same source packaged as (a) Claude Code marketplace plugin, (b) OpenCode npm package (`@<author>/<name>-plugin` via `packages/opencode-plugin/`), (c) Codex CLI install target (via `bunx @<author>/<name>-plugin install --platform codex`). TypeScript core under `src/core/` is shared; an `src/opencode/` adapter layer adapts it; `src/cli/` drives the npm install flow for non-Claude-Code consumers. The bin-wrapper's `<name>_PLUGIN_ROOT` env-var-first resolution exists specifically because `CLAUDE_PLUGIN_ROOT` isn't set in non-Claude-Code ecosystems. Appropriate when the author targets multiple ecosystems and wants one source of truth. Constraint: every plugin-protocol concern must be expressed across all three target conventions.

## Native artifact distribution

How a plugin distributes a compiled native binary (Go, Rust, C) to users.

### On-demand GitHub-release download

Plugin doesn't vendor the binary in git; downloaded from `releases/download/v<version>/<binary>` (with a `releases/latest/...` fallback or a separate `snapshot` floating tag for race mitigation). Versioned URLs first, floating last. macOS Gatekeeper handled by best-effort `xattr -d com.apple.quarantine` after `chmod +x`. UPX compression on a subset of platforms (linux/windows-amd64) where it works reliably; skipped on darwin and windows-arm64. Repo stays small at the cost of first-run network dependency. Appropriate when the binary is large or per-platform; constraint is the network requirement on first use.

### Per-platform asset matrix with shared-library carve-out

Release workflow builds N platform tarballs (e.g., linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64, windows/arm64) per binary. Tree-sitter grammars (or analogous shared libraries) built as separately-downloadable platform-specific shared libraries (`<name>-grammar-<lang>-<version>-<os>-<arch>.tar.gz`), dynamically loaded at runtime. Lockfile (`.<name>-grammars.lock`) tracks pinned upstream grammar repo tags. Cross-compile via Zig (downloaded from `ziglang.org/builds/...` per build step). Appropriate for plugins shipping a polyglot capability. Constraint: external CDN dependency at build time; deleted upstream grammar repos warn-and-continue silently.

### Rust cross-compile via Cargo + macOS-only runtime

Release workflow uses `taiki-e/upload-rust-binary-action@v1` with matrix over apple-darwin targets only (`x86_64`, `aarch64`); cross-platform compile elsewhere is CI-sanity only. The product itself is macOS-only (the integration target — MoneyMoney — is macOS-only). Asset URL `<name>-<target>.tar.gz` hardcoded in the bin shim. Appropriate when the underlying capability is platform-locked. Constraint: non-Darwin platforms fail at runtime in the shim, not at install.

### Firmware artifact alongside plugin

A `.fap` firmware binary built via `ufbt build` and attached to the GitHub release as a sibling artifact to plugin-relevant assets. Built on `ubuntu-latest` with `actions/setup-python@v5`. Appropriate for plugins paired with custom hardware firmware; the firmware is a separately-installed product that the plugin's daemon talks to.

## Cross-role tools

Tools that fill multiple functional roles in this bin's samples — surfaced under each role's section above:

- **Bun** — TypeScript runtime for bin-wrapper (under bin-wrapped CLI distribution); Node-modules installer in self-heal path (under dependency installation); test runner (`bunx vitest run`, under testing and CI); skill-validator host (under marketplace validation).
- **softprops/action-gh-release@v2** — release-creation mechanism in tag-conditional step (under release automation); also in dual-workflow split and snapshot path.
- **`hookSpecificOutput.additionalContext`** — context-injection channel in SessionStart welcome-state path (under session context loading); same channel in PostToolUse skill-nudge path (under tool-use enforcement); same channel in UserPromptSubmit fuzzy-match path (under session context loading).
- **GitHub Releases** — primary download source for native binaries (under native artifact distribution); same surface used by binary-download dependency-install paths (under dependency installation).
- **`/tmp/`-based filesystem state** — daemon coordination via socket/PID/refcount (under daemon and IPC lifecycle); cross-hook flag-file coordination (under live monitoring and notifications); session-scoped one-shot nudge marker (under tool-use enforcement).
- **macOS Gatekeeper handling (`xattr -d com.apple.quarantine`)** — post-download install step (under dependency installation); same step in bin-wrapper lazy-download path (under bin-wrapped CLI distribution).
- **`jq`** — `hookSpecificOutput` JSON construction in shell hooks (under tool-use enforcement); version extraction from `plugin.json` in download shims (under dependency installation).
