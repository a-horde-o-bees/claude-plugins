# Sample

Pass-1 Phase-1a partial for bin 6. Functional decomposition of `JordanCoin--pdf-to-text.md`, `K-dash--typemux-cc.md`, `Kanevry--session-orchestrator.md`, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How a repository advertises itself to Claude Code's `/plugin install` resolver — where the manifest lives and how it relates to the plugin source.

### Self-referential single-plugin marketplace

A `.claude-plugin/marketplace.json` at repo root with one plugin entry whose `source` is `"./"`, making the same repository simultaneously a marketplace and the only plugin within it. Minimum-footprint pattern: one `git push` ships both the storefront and the wares. Constrains the plugin's filesystem layout to start at repo root — no `metadata.pluginRoot` indirection — so any repo content (CI configs, contributor docs, lockfiles, even `node_modules/` after install) sits inside the plugin's filesystem boundary unless filtered. Appropriate when one plugin defines the entire repository's purpose and there's no expectation of co-publishing siblings later.

## Plugin discoverability surface

Fields on the marketplace entry that let a browsing user find the plugin via tag, category, or keyword search rather than knowing its name in advance.

### Keywords-only minimal entry

The marketplace entry exposes only `description`, `version`, and `keywords`, omitting `category` and `tags` entirely. Search by category or tag will not surface the plugin; only literal keyword matches will. Often paired with `plugin.json` carrying a slightly different `keywords` list, creating a second drift surface where the two arrays disagree on count and content.

### Fully populated discoverability

Marketplace entry sets `category`, `tags`, and `keywords` together along with `description`, `author`, `homepage`, `repository`, and `license`. Plugin appears in browsing flows that filter by any of the three axes. Appropriate when the author wants the plugin to be discoverable through browsing rather than by direct install URL only; demands more curation since each axis adds maintenance surface.

### Marketplace entry with no discoverability fields

Marketplace entry exposes neither `category` nor `tags` nor `keywords`, even when `plugin.json` has its own `keywords` array. The `$schema` reference may still be present (the schema does not require these fields). Plugin is reachable only by direct install URL; browsing flows will not find it.

## Plugin source binding

How the marketplace entry references the plugin's actual files — relative path to repo content versus other source forms.

### Self-relative source

`source: "./"` on the marketplace entry; plugin root and repo root are the same path. Pairs with the self-referential single-plugin marketplace pattern. Makes `plugin.json` the de-facto version-of-record (per docs convention for relative sources), but does not prevent the marketplace entry from carrying its own `version` field that drifts.

## Version authority and drift surface

Where the plugin's version number lives and how many independent copies must stay in sync.

### Single source of truth (`plugin.json` only)

`plugin.json` carries the version; the marketplace entry omits one or treats it as decorative. Lowest drift risk. Rare in the observed bin — most samples maintain at least two independent copies.

### Dual-file version (manifest pair)

`plugin.json` and `marketplace.json` both carry `version`. The pair must be edited together on every release; a single-file edit produces a drift the install path will not catch.

### Triple-file version (build manifest joins)

The language ecosystem's build manifest (`Cargo.toml`, `package.json`) joins `plugin.json` and `marketplace.json` as a third version-bearing file. Drift is mitigated procedurally — by a documented release skill that walks the author through editing all three — rather than structurally. No CI gate verifies the invariant; the release skill is the only enforcement.

### Five-way version sprawl

Version appears in `plugin.json`, marketplace entry, a top-level `VERSION` file, the language build manifest (`package.json`), and hardcoded inside source code (e.g., MCP server's `version: "0.1.0"` literal). No generation or sync mechanism. Each release is five hand-edits; a missed edit ships a contradiction.

### Version drift with no reconciliation

The marketplace `metadata.version` field is documented as marketplace-bundle version rather than plugin version, and visibly lags `plugin.json` (e.g., marketplace says `2.0.0`, `plugin.json` says `3.0.0-dev`). Adds a hook banner version (e.g., `echo '🎯 Session Orchestrator v2.0.0'` baked into `hooks.json`) and a README badge with its own version string as further drift sites. The release process accepts the drift as cosmetic; users see five different version strings depending on which surface they look at.

## Channel distribution

Whether the plugin offers stable vs prerelease channels, how users pin to a release, and how the install path resolves a tag.

### No channel split, default-branch install

Users install via `/plugin install <plugin>@<owner>/<repo>` and pin to whatever `main` resolves to at install time. No `stable-*`/`latest-*` parallel manifests, no release branches. Plugin code on disk is whatever HEAD pointed to during install, not necessarily a tagged release. Appropriate for solo or small-scale plugins where formal release ceremony is not warranted.

### Pre-release tags on a single channel

Same single marketplace as above, but the version stream uses semver pre-release suffixes (`-alpha.N`, `-beta.N`, `-rc.N`, `-dev`) on `main`. Tags carry `prerelease: true` correctly in the GitHub Releases API. Users can pin to a specific pre-release tag, but installing from `main` always lands on whatever `plugin.json` currently says — including in-development `-dev` versions. No machinery prevents accidental pre-release installs; the suffix is informational.

## Version control and release cadence

Branching model and how releases are cut once the channel question is settled.

### Tag-on-main, manual release

Tags live on the default branch (`main`). The release flow is hand-driven: edit version files, commit, tag, push. No release branches, no `stable/*` paths. Pre-release suffixes (when used) live on the same branch. Lowest infrastructure cost; relies entirely on author discipline for cross-file version consistency.

### No tags at all

Repo has zero tags. "Release" means whatever `main` currently holds. No history of release points; rolling back to a prior version requires checking out a specific commit. Often paired with no CI and no validation — a low-ceremony, low-investment plugin.

## Component registration in plugin.json

How `plugin.json` (or its absence of declarations) tells Claude Code what files are skills, hooks, MCP servers, etc.

### Default convention discovery

`plugin.json` declares no component paths; Claude Code auto-discovers via standard directory conventions (`skills/`, `hooks/hooks.json`, `commands/`, `agents/`, `.mcp.json` at repo root, `output-styles/`). Lowest manifest weight; the directory layout is the registration. Constrains naming and placement to whatever the harness expects but eliminates a class of "registered but missing" drift.

### Mixed reference style

`plugin.json` uses external file references for some components (`hooks: "./hooks.json"`) and inline configuration objects for others (`lspServers: { … }`), while a third class is auto-discovered (skills under conventional paths). Lets the author keep large or frequently-edited config in dedicated files while inlining short structural blocks. Constrains readers to look in multiple places to enumerate what the plugin registers.

## Component types shipped

Which Claude Code component categories the plugin actually populates — the surface it presents to end users.

### Skill + hook + MCP

Plugin ships a skill (or skills) plus at least one hook (typically `SessionStart` for setup) plus an MCP server registered through `.mcp.json`. Skills define user-invocable workflows; hooks handle install/setup; MCP server exposes tool calls. Common shape for "agent-facing tooling that needs runtime infrastructure."

### Skill + hook + LSP

Plugin's surface is an LSP server registered inline via `lspServers` in `plugin.json`, accompanied by a `SessionStart` hook for binary setup and a small skill set (often developer-facing ones the author ships unintentionally — see "leaked developer skills"). LSP-first plugins constrain the user-visible interaction model: instead of slash commands, Claude Code routes editor diagnostics through the LSP transport.

### Full kitchen sink

Skills + commands + agents + hooks + MCP server + output styles, with no `bin/`. The plugin is a multi-component orchestration suite. Each category has multiple files (e.g., 13 skills, 7 commands, 6 agents, 3 output styles). Complexity is justified by the plugin's scope (session orchestration covering planning, VCS, quality gates, persistence) but multiplies the maintenance and validation surface.

## Dependency installation runtime

What language/runtime the plugin's install hook bootstraps and how it acquires the dependency.

### Hook-driven WASM payload

`SessionStart` hook downloads a raw WebAssembly binary plus its JS wrapper from GitHub Releases on a separate repo, installing into `${CLAUDE_PLUGIN_DATA}` with a hardcoded `$HOME/.config/<plugin>` fallback. No package manager — release artifacts substitute for npm/PyPI. The MCP server consumes the WASM via `WebAssembly.Module` + `initSync({ module })` at startup. Pattern: release-as-CDN, where GitHub Releases acts as a binary distribution channel without a package manager mediating. Constrains the plugin's release cadence to the engine repo's release cadence — engine release must precede plugin install success, and version pinning is exact-match (any inequality re-downloads all files).

### Hook-driven prebuilt native binary

`SessionStart` hook downloads a prebuilt platform-specific binary (Rust release artifact) into `${CLAUDE_PLUGIN_ROOT}/bin/`, picking the right asset by detecting OS and architecture (`macos-arm64`, `linux-x86_64`, `linux-arm64`). Existence-only change detection: the script no-ops if the binary exists, so `/plugin update` does not re-download — users must manually wipe the cache to pick up a new binary. Calls the unauthenticated GitHub Releases API at install time, coupling first-run success to GitHub rate limits. No sha verification; trust is implicit in HTTPS plus GitHub Releases.

### Manual `npm install` post-install

No `SessionStart` hook for install. README instructs users to `cd` into the plugin cache directory and run `npm install` once. `node_modules/` materializes inside the plugin root. Change detection is the user reading `ls node_modules/zx`. Failure mode is silent: if `npm install` was never run, hook handlers fail at `import` time before any top-level `try/catch` can engage. Deviates from the docs-prescribed `diff -q`/retry-next-session pattern; the author has accepted this friction in exchange for not maintaining an install hook. Required when hooks need an npm runtime dep (e.g., `zx`) that the plugin cannot ship pre-resolved.

## Install change detection

How the install path decides whether work is needed on the current invocation.

### Version file stamp

Compares `${PLUGIN_DIR}/VERSION` against `${INSTALL_DIR}/.version`; exits 0 when equal. Idempotent — every `SessionStart` re-runs the script but does no work in the steady state. The committed-version file is written only on full success, so a partial failure leaves `.version` absent and the next session retries. Cleanup of partial tmp files on failure preserves the retry invariant.

### Existence-only check

`if [ -f "${BINARY_PATH}" ]; then exit 0`. Once the artifact is present, the install hook never replaces it. Upgrades require manual cache wipe — the install path is not idempotent across version changes, only across no-change re-invocations. Pairs uneasily with `/plugin update`, which does not clear the binary, so users hit a documented troubleshooting path.

### Out-of-band user check

User runs `ls node_modules/zx` to verify install. No automated detection at all. Failures surface as runtime import errors when hooks fire.

## Install failure signaling

How the install hook tells the user (and the harness) that something went wrong.

### Human-readable stderr plus exit 1

`set -euo pipefail` plus prefixed stderr lines (e.g., `[plugin-name] ERROR: …`) plus `exit 1` on failure. Success path prints a single confirmation line to stdout. No JSON `systemMessage`, no `continue: false`, no structured hook output. Corrective hints embedded in error text (e.g., "delete `${INSTALL_DIR}` and restart your session"). Sufficient for users who watch the session start; opaque to agents that don't parse stderr.

### Silent failure

Hook is absent or no-ops; the install never runs. Failure surfaces only when the missing dependency is needed at runtime (e.g., `Cannot use import statement outside a module` from a hook with no `node_modules`). Documented as a troubleshooting path the user must follow manually. Trades discoverability for zero install-machinery cost.

## SessionStart hook scope

What `SessionStart` does and which sub-events trigger it.

### Install-only with no matcher

Bare `hooks` array under `SessionStart` with no `matcher` field, so the install runs on every sub-event (`startup`, `resume`, `clear`, `compact`). Cheap when guarded by an existence or version check; means any future stdout from the install script will emit on every clear/compact. Not used for context loading at all — install logic only.

### Install plus session telemetry

`SessionStart` runs two handlers in sequence: an install/banner echo, and a Node script that emits a structured session-started event to a metrics file (and optionally POSTs to a remote event bus when an env-var secret is set). Async, 5s timeout. Informational; never blocks. Adds an `on-session-start.mjs` companion to the install script. Constrains the plugin to ship telemetry plumbing alongside install plumbing.

### Banner echo as context push

A literal `echo '🎯 Plugin v2.0.0 — …'` line in `SessionStart` pushes a banner via stdout rather than via `hookSpecificOutput.additionalContext` JSON. Functions as session-start context for the user but not as structured context for the agent. Drift hazard: the banner text typically hardcodes a version that diverges from `plugin.json` over time.

## Bin entry mechanism

Whether the plugin ships executable wrappers under `bin/`, what they do, and how they relate to the binary that actually runs.

### Skill-invoked update poller

A single `bin/<plugin>-update-check` shell script, not registered in `plugin.json`'s component fields, invoked from a `## Preamble (run first)` block embedded in a SKILL.md. The agent reads the skill body, shells out per the prose instructions, parses output (`UPGRADE_AVAILABLE <old> <new>` / `JUST_UPGRADED <old> <new>` / nothing), and conditionally surfaces a notification. Polling cadence is gated by a cache file with a TTL. Novel because it embeds polling logic in documentation text the model must parse and act on, rather than in a structured hook contract. State coordination (read by skill, written by install hook) sits in shared sentinel files (`.version`, `just-upgraded-from`).

### Orphaned wrapper alongside downloaded binary

`bin/<plugin>-wrapper.sh` is committed and `chmod +x`ed but `plugin.json`'s `lspServers.command` (or equivalent) points directly at the downloaded native binary, not the wrapper. The wrapper sources a `~/.config/<plugin>/config` file before `exec`ing the binary; the binary itself reads the same config natively, making the wrapper redundant. Classic half-refactored state — wrapper was written first, then superseded by in-binary config loading, then left in place.

### No bin entry

Plugin ships no `bin/` directory and no `bin` field in `plugin.json`. All executable entry points are hooks (`.mjs` files invoked via `node` in `hooks.json`) or installer scripts under `scripts/`. The MCP server, when present, is registered through `.mcp.json` rather than as a bin entry. Reduces the discoverability surface compared to bin-wrapped CLIs but eliminates the version-of-record question for a wrapper script.

## Runtime resolution variable chain

How scripts and hooks resolve `${CLAUDE_PLUGIN_ROOT}` (or the data-dir analog) when the harness might or might not have set it.

### Two-tier env-var-first fallback

`${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}` — env var first, script-relative dirname second. Standard pattern; works whenever the script has a real path on disk.

### Three-tier with hardcoded data-dir terminal fallback

`${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd || echo "$HOME/.config/<plugin>")}` — adds a hardcoded user-config path as the third tier. Semantically wrong for code that needs to read SKILL.md siblings (the data dir is not a plugin dir), but works by coincidence because `2>/dev/null || true` swallows the resulting failures and the only callers happen to invoke paths that the data dir contains too. Pattern that works only because failures are silent.

### Cascading multi-host fallback

`${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}` — supports invocation from Claude Code (first), Codex (second), or git working tree (third). Used when the same plugin code ships into multiple agent ecosystems and needs to discover its root regardless of which host loaded it. Adds dependency on `git` being installed and the cwd being inside a git tree for the third tier.

## Out-of-band user configuration

How the plugin's runtime reads user-tunable settings when `plugin.json`'s `userConfig` is not the chosen mechanism.

### Home-directory KEY=VALUE file

The native binary reads `~/.config/<plugin>/config` directly (KEY=VALUE lines, optional `export` prefix, no shell expansion). Plugin declares no `userConfig` in `plugin.json`. Decouples config lifetime from plugin cache churn — config survives uninstall/reinstall — but sacrifices Claude-Code-side discoverability and validation. Priority chain documented as `CLI flag > env var > config file > default`. Constrains the plugin to handle config parsing and schema enforcement entirely in its own runtime code.

### Markdown block in consumer's CLAUDE.md

Plugin parses a `## Session Config` block from the consumer repo's `CLAUDE.md` or `AGENTS.md`, extracting fields (`test-command`, `typecheck-command`, `lint-command`, `enforcement`, `agents-per-wave`, `waves`, `allow-destructive-ops`, etc.). Validated against a homegrown JSON-Schema (`config-schema.mjs`); a bypass env var (`SO_SKIP_CONFIG_VALIDATION=1`) lets users opt out for emergencies. The plugin re-implements parser + validator rather than using the platform's `userConfig` mechanism. Constrains config to a markdown surface users already maintain, enabling per-project config without Claude-Code-side plumbing, at the cost of a parallel parser the plugin must keep aligned with the schema.

## Tool-use enforcement (PreToolUse)

How the plugin gates tool calls before they execute.

### Fail-closed scope and command guards

Multiple `PreToolUse` hooks (`Edit|Write` for path-scope enforcement, `Bash` for destructive-command guards and per-wave allowlist enforcement). Every security-critical hook wraps its body in `main().catch((e) => emitDeny(...))` so any unhandled error denies the call rather than allowing it through. Output convention is centralized: `emitAllow`/`emitDeny`/`emitWarn`/`emitSystemMessage` helpers in a shared `io.mjs` library produce a uniform JSON wire format (`{"permissionDecision":"deny","reason":"..."}` plus exit 2 for deny; exit 0 silent for allow). `emitDeny` requires a non-empty reason (throws if missing) — silent-deny is structurally unrepresentable. Path normalization (Windows separator, realpath symlink resolution) plus an ENOENT ancestor-walk for not-yet-existing Write targets defends against symlink escape. Stdin reads guard against runaway input via 1 MB byte cap plus 5s `AbortController` timeout.

### Numbered-requirement traceability annotations

Every security-critical hook source file opens with a `SECURITY notes (inline refs)` block listing `REQ-01` through `REQ-NN`, and every relevant function cites its REQ number inline (`// SECURITY-REQ-03: resolve symlinks ...`). Pattern: requirements in a security pre-review document trace to specific lines of code via comment annotations. Discipline that lets a reviewer confirm coverage by grep rather than by re-deriving the threat model. Notable for agent-written code where the requirement-to-line traceability would otherwise erode rapidly.

### No tool-use enforcement

Plugin ships no `PreToolUse` or `PostToolUse` hooks. Surface is install-only (`SessionStart`) plus user-facing components. The MCP server, when present, may have its own defensive code (typed errors, top-level `process.exit(1)` on fatal errors), but that's runtime defense inside the server, not Claude Code hook enforcement.

## Tool-use enforcement (PostToolUse)

What the plugin observes after tool calls complete.

### Informational fail-open post-edit hook

Single `Edit|Write` `PostToolUse` hook running an incremental typecheck on the edited file. Implemented fail-open (`.catch(() => process.exit(0))`) — never blocks tool flow. Purely informational; surfaces typecheck issues as warnings without obstructing the edit. Counterpart to fail-closed `PreToolUse` enforcement: pre-checks gate, post-checks observe.

## Plugin-conflict declaration

How the plugin tells the user it cannot coexist with another plugin.

### README prose only

Plugin requires the user to manually `/plugin disable <other-plugin>@<other-marketplace>` before installing. The conflict is declared only in README narrative; plugin metadata has no `incompatibleWith` or equivalent field. Installing both leaves the user with conflicting servers (e.g., two LSP backends) silently. Procedural-only enforcement; structural enforcement absent.

## Test framework

What runs the plugin's automated test suite.

### vitest with multi-suite layout

Vitest as the primary runner, configured via `vitest.config.mjs` to glob both top-level `tests/**/*.test.mjs` and nested skill-local `skills/*/tests/**/*.test.mjs`. Tests are organized into `hooks/`, `integration/`, `lib/`, `skills/`, `unit/`, `fixtures/` subdirs at repo root. Replaces an earlier bats-based suite. Direct invocation via `npm test` → `vitest --run`; typecheck delegated to a custom `node scripts/typecheck.mjs` rather than `tsc`.

### cargo test

Rust integration-test layout — `tests/` at repo root holds top-level integration test files (`crash_recovery_test.rs`, `doctor_test.rs`, `multi_venv_test.rs`, `smoke_test.rs`, `venv_detection_test.rs`) with shared fixtures under `tests/support/mod.rs`. Wrapped behind `make ci` (= `fmt-check` + `clippy -- -D warnings` + `cargo test`).

### No tests

Repo has no `tests/` directory and no test files. No round-trip validation of manifests, no smoke test of install scripts, no MCP-server registration test. Quality assurance is manual; release process is commit-to-main.

## CI shape

What the CI workflow does, what it gates on, and how it pins external action versions.

### Lint + typecheck + test on multi-OS matrix

`.github/workflows/test.yml` runs on `push: branches: [main]` plus `pull_request`. Steps: `npm ci`, optional nested-skill installs, `npm run lint` (eslint), conditional `npm run typecheck`, `npm test` (vitest). 3-OS matrix (`ubuntu`, `macos`, `windows`) without language-version matrix. Actions SHA-pinned with tag annotations preserved as comments. Built-in `actions/setup-node` cache keyed on `npm`. `concurrency` group with `cancel-in-progress: true` supersedes queued runs on rapid push. Per-job `timeout-minutes: 15` and minimum-`contents: read` permissions. No manifest-validation step (no `claude plugin validate` invocation).

### Format + lint + test wrapper

`make ci` wrapping `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test`. Runs on `push: branches: [main]` and `pull_request` with `paths-ignore: ['*.md']`. Matrix is OS only (`ubuntu-latest`, `macos-latest`, `ubuntu-24.04-arm`); no MSRV check despite `Cargo.toml` declaring `rust-version`. Actions tag-pinned. Rust target/registry caching via `Swatinem/rust-cache@v2`.

### No CI

No `.github/workflows/` directory. Zero automated verification on any commit. Manifests, hook scripts, and source code all rely on author-side checks before push.

## Release automation

How tags, GitHub Releases, and binary artifacts are produced once a release is cut.

### Tag-triggered cross-compile + asset upload

`.github/workflows/release.yml` triggered by `push: tags: ['v*']`. Cross-compiles the binary to multiple targets (e.g., `aarch64-apple-darwin`, `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`), installs cross toolchains for non-native targets, renames outputs to platform-tagged asset names (`<plugin>-macos-arm64`, `<plugin>-linux-x86_64`, `<plugin>-linux-arm64`), and uploads via `softprops/action-gh-release@v1` with `generate_release_notes: true`. No tag-sanity gates (no verify-tag-on-main, no verify-tag-matches-build-manifest-version, no tag-format regex). Action pinned to a major tag rather than a SHA.

### Manual release, no automation

Releases exist (sometimes a full pre-release ladder of `-alpha.N`/`-beta.N`/`-rc.N` plus stable tags) but all are produced by hand via `gh release create`. CHANGELOG is hand-maintained in Keep-a-Changelog format. `prerelease: true` flag is set correctly on pre-release semver. No tag-trigger workflow exists; the otherwise-substantial CI investment does not extend to release plumbing. Version drift across `plugin.json` / build-manifest / `marketplace.json metadata.version` / README badge / hook banner is a manual-maintenance hazard automation could catch.

### No releases

No tags, no GitHub Releases on the plugin repo. "Release" means whatever `main` currently points at. Often paired with no CI and a dangling external dependency (e.g., an update-check pipeline that polls a sister repo's releases endpoint that itself returns 404). The plugin ships with the release infrastructure code written but the supporting endpoints unbuilt.

## Marketplace manifest validation

Whether anything programmatically checks `marketplace.json`, `plugin.json`, and `hooks.json` shape.

### Homegrown validators not wired to CI

Repo-local scripts (`scripts/validate-plugin.sh`, `scripts/validate-wave-scope.sh`, `scripts/validate-config.mjs`) plus a frontmatter validator with its own test suite (`tests/lib/agent-frontmatter.test.mjs`) exist but are not invoked by CI workflows. Library-internal use only. "Defense in depth but no enforcement at the marketplace manifest layer."

### No validation

No validator scripts and no `claude plugin validate` invocation in CI. Manifest regressions surface only at install time on a real Claude Code session. Most low-investment plugins land here.

## Documentation surface

What user-facing and developer-facing docs the plugin ships beyond `README.md`.

### Single README serves all

`README.md` at repo root is the only documentation. Covers install, usage, format reference, and (sometimes) license/privacy. No `CHANGELOG.md`, no `ARCHITECTURE.md`, no `CLAUDE.md`. License claim may live only in README prose without an SPDX-identifiable `LICENSE` file, in which case GitHub UI reports the repo as unlicensed regardless of the README claim.

### README + ARCHITECTURE + CLAUDE-as-pointer

Substantial `README.md` (~16 KB) plus a sizable `ARCHITECTURE.md` at repo root with mermaid diagrams and design-principle prose. `CLAUDE.md` exists but contains only a pointer (`@AGENTS.md`-style include) — `AGENTS.md` is the canonical agent-rules file. Convention inversion: Claude Code loads `CLAUDE.md`, but the actual content lives elsewhere. Works because of the include directive. Constrains contributors to know the indirection or risk editing the wrong file.

### Full kitchen-sink docs

`README.md` plus a large `CHANGELOG.md` (Keep-a-Changelog format, dev-trail entries during pre-release cycles) plus `docs/<architecture>.md` and `docs/migration-*.md` plus `docs/USER-GUIDE.md` (~60 KB) plus `docs/prd/*.md` for feature specs plus a long `CONTRIBUTING.md` (~22 KB) plus `SECURITY.md` plus `CODE_OF_CONDUCT.md` plus issue and PR templates. Documentation-as-code practice extending to PRDs. `CLAUDE.md` is operational procedures (agent-authoring pitfalls, structure overview, destructive-command-guard documentation), not just a pointer. Drift hazard at this scale: stale references in `SECURITY.md` to pre-refactor file names linger across migrations.

## License declaration consistency

Whether the license claim agrees across `LICENSE` file, `plugin.json`, README, and the GitHub API.

### MIT, single source

`LICENSE` file present with MIT text; `plugin.json` declares MIT; README references MIT. GitHub API reports MIT. All four agree. Standard hygiene.

### Three-way disagreement

README asserts one thing ("Plugin wrapper: MIT. Extraction engine: proprietary."), `plugin.json` declares another (`"license": "UNLICENSED"`), no `LICENSE` file commits anything, GitHub API returns null. Author intent is unrecoverable from static inspection. GitHub UI and tooling report the repo as unlicensed regardless of the README claim because no SPDX-identifiable file exists.

## Cross-ecosystem plugin shipping

Whether the same repo ships plugins for multiple agent ecosystems and how it organizes parallel manifests.

### Single-ecosystem (Claude only)

`.claude-plugin/marketplace.json` is the only manifest. No Codex, no Cursor, no other agent-host configuration in the tree.

### Triple-ecosystem (Claude + Codex + Cursor)

Single repo ships `.claude-plugin/marketplace.json` for Claude Code, `.codex-plugin/plugin.json` for Codex, and `.cursor/rules/*.mdc` for Cursor IDE — three concurrent manifest systems. Bootstrap scripts (`scripts/codex-install.sh`, `scripts/cursor-install.sh`) adapt the same skills/agents/hooks to each host. A shared `platform.mjs` exposes `SO_PLATFORM`, `SO_IS_WINDOWS`, `SO_IS_WSL` so library code can branch without duplicating logic. The `${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}` resolution chain (see "runtime resolution variable chain") supports invocation from any host. Constrains every install-side change to be tested across three ecosystems and pushes the plugin into a "lowest common denominator" portion of each host's API surface.

## Update notification mechanism

How the plugin tells the user a newer version is available.

### Skill-preamble update poller

Skill body opens with a `## Preamble (run first)` block that the agent shells out on, invoking `bin/<plugin>-update-check`. The script polls a release endpoint, writes a status cache (with a TTL to avoid hitting the endpoint every invocation), and emits one of `UPGRADE_AVAILABLE`, `JUST_UPGRADED`, or nothing. The agent parses output and conditionally surfaces a notification. State coordination uses sentinel files in the data dir (`last-update-check`, `update-snoozed`, `just-upgraded-from`); the install hook writes some, the update-check reads and clears them. Pairs with a partial-feature snooze mechanism (read path implemented, write path absent — design intent visible without complete functionality). Constrains discovery to skill invocation: agents never invoking the skill never see the notification.

### No update mechanism

Plugin ships no update poller. `/plugin update` re-fetches the marketplace entry but the plugin's runtime never proactively checks for new versions. Users discover updates through external channels (release feeds, social posts, the marketplace browse UI).

## Telemetry and event emission

Whether the plugin emits structured events about its own lifecycle.

### JSONL append plus optional remote POST

A library (`scripts/lib/events.mjs`) writes structured events as JSONL appends to `.orchestrator/metrics/events.jsonl`. When an env-var secret (`CLANK_EVENT_SECRET`) is set, events also POST to a configurable webhook via native `fetch` plus `AbortSignal.timeout(3000)`; errors are swallowed so remote failures never affect local execution. Pattern: graceful optional remote telemetry. Local logging is always on; remote forwarding is opt-in by environment.

### No telemetry

Plugin does not emit structured events. Diagnostic information lives only in stderr of hook invocations and log files the user inspects manually.

## Runtime policy file tree

Where the plugin keeps user-tunable runtime rules separate from `plugin.json`.

### `.orchestrator/policy/*.json` with JSON-Schema contracts

A directory tree under `.orchestrator/policy/` holds runtime policies (`blocked-commands.json` with N rules, `quality-gates.schema.json` plus `.example.json`, `ecosystem.schema.json`). Hook reads the policy plus a per-session scope file (`wave-scope.json`); the contract between policy and hook is a JSON-Schema rather than inline rules in code. Pattern: pluggable policy JSON loaded per invocation. Lets the user (or the plugin's own session-start skill) edit rules without modifying hook source. Constrains schema evolution: any policy field rename requires updating both the schema file and every consuming hook.

## Output styles

Whether the plugin ships shared report formats agents and skills reference.

### Shared markdown templates under `output-styles/`

3+ markdown files at `output-styles/` (e.g., `session-report.md`, `finding-report.md`, `wave-summary.md`) define the prescribed output shape for skill or agent emissions. Agents and skills reference these by path, ensuring report consistency across the plugin's surface. Layer not always documented in plugin docs but legitimately registered via convention discovery. Constrains the plugin to maintain template-to-consumer coupling — a template rename requires updating every reference.

### No output styles

Plugin ships no `output-styles/` directory. Skills and agents emit free-form output, with consistency enforced (or not) at the prose level only.

## Cross-platform discipline

How the plugin's runtime code accommodates Windows, macOS, and Linux.

### Documented Windows-native migration

CHANGELOG explicitly enumerates each cross-platform concern as it lands: `os.tmpdir()` replaces `${TMPDIR:-/tmp}`, `path.parse(dir).root` replaces `/`-terminator for filesystem walks, Windows backslash normalization before glob matching, CRLF-tolerant config parsing, `.gitattributes` EOL rules. Pattern: windows-native as a documented migration. Most marketplaces implicitly assume POSIX; this one lists each accommodation as a deliberate change with rationale.

### POSIX with documented platform rejection

`install.sh` detects platform and explicitly errors on unsupported configurations (e.g., Intel macOS, Windows) with corrective guidance pointing at a local-build escape hatch. No silent fallback; no Windows code path. Cross-platform support stops at "build it yourself if you're not on the supported list."

### POSIX with `stat` portability fallback

Bash scripts wrap stat invocations as `stat -f %m || stat -c %Y || echo 0` (BSD form, then GNU form, then literal zero). Final `echo 0` is a silent cache-disable failure mode rather than a hard error: when both stat forms fail, the resulting epoch is so far in the past that subsequent freshness comparisons always return false. Works on macOS and GNU/Linux; behavior on busybox, Alpine, FreeBSD is unverified.

## Plugin substrates that can leak into distribution

Files inside the plugin filesystem boundary that are intended for the plugin author's own development workflow but ship to end users by default.

### Repo-local developer skills exposed as plugin skills

`.claude/skills/<dev-skill>/` directories (e.g., `plugin-test-cycle`, `publish`) sit at repo root and are auto-discovered by Claude Code whenever the plugin is installed. End users see `plugin-test` and `publish` triggers that are meaningful only to the plugin author. Similar to seeing internal `.vscode/launch.json` entries leak into a distribution. Fix is either to scope these skills with a guard or to move them outside the plugin filesystem boundary.

### Repo-local PostToolUse hook in `.claude/settings.json`

A `PostToolUse` hook wired in `.claude/settings.json` runs `make lint 2>&1 | head -30` on `Write|Edit|MultiEdit`. Repo-local developer tooling. File is committed and (depending on harness behavior) could leak into plugin distribution if Claude Code ever started harvesting it. Worth flagging because the plugin's own `hooks.json` does not declare this hook — the leak surface is settings, not the plugin manifest.

### Lockfile and node_modules inside plugin root

`package-lock.json` (~80 KB) ships inside the plugin filesystem; `node_modules/` materializes inside the plugin root after the user runs `npm install`. The `.claudeignore` filter at repo root has only a few entries (excluding metrics dirs and example folders) and does not gate the lockfile or future module trees. Constrains plugin update behavior: re-installing the plugin without clearing `node_modules/` produces a stale module tree the user must manually purge.
