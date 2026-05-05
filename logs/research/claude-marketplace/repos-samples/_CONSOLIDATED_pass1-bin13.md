# Sample

Pass-1 Phase-1a partial for bin 13. Functional decomposition of `damionrashford--trader-os.md`, `ekadetov--llm-wiki.md`, `heliohq--ship.md`, organized by role with implementation paths as sub-sections.

## Marketplace manifest shape

How the repo declares itself as a marketplace — top-level metadata richness, schema declaration, per-entry discoverability fields.

### Minimal entry — name, owner, plugins only

The marketplace.json carries only the top-level fields strictly needed to dispatch plugins. No `metadata` wrapper, no top-level description, no `$schema`, no per-entry category/tags/keywords. A consumer browsing categories will not discover this marketplace; users must arrive by direct URL or owner search. Appropriate for a single-author single-plugin repo where discoverability via marketplace categories isn't a goal — the README does the marketing.

### Richer top-level with description and owner object

The marketplace.json carries `name`, `description`, and an `owner` object (with `name` and `url`), but still no `metadata` wrapper and no marketplace-level version. Per-entry discoverability is also light — `keywords` typically live inside each plugin's own `plugin.json` rather than the marketplace entry. Mid-weight choice: enough metadata for a consumer to read what the marketplace is, but no taxonomy for category-based discovery.

### `metadata.{description, version, license}` wrapper plus per-entry tags

The marketplace.json wraps non-identity fields in a `metadata` object (description, version, license), keeps `name`/`owner` at top level, and equips each plugin entry with `category` and `tags` for taxonomic discovery. Maximally discoverable shape — surfaces in category listings, exposes a marketplace-level version distinct from plugin versions, and signals license at the marketplace surface. Tradeoff: the marketplace-level version is a third version axis (alongside marketplace-entry version and plugin.json version) with no enforced sync between any pair.

### `$schema` declaration

Across all three samples in this bin, `marketplace.json` does not declare a `$schema`. Where `$schema` does appear, it's on the unrelated `.claude/settings.json` — a different file under a different consumer. Marketplace-level schema validation is therefore not present; manifests are authored and shipped without IDE-side completion or pre-flight schema check.

## Plugin source binding

How a marketplace entry resolves to the plugin tree it should serve.

### Relative path source — single plugin co-located at repo root

The marketplace entry uses `"source": "./"` because the marketplace and the plugin are the same repo root. Simplest possible binding — no aggregation, no subdirectories, no remote references. The full repo tree is consumed as the plugin. Co-located variant reduces version drift surface (only one tree to track) but precludes shipping multiple plugins from one repo.

### Relative path source — subdirectory per plugin in monorepo

The marketplace entry uses `"source": "./plugins/<plugin-name>"` to point at one of several plugin trees under a single repo. Used when a marketplace publishes multiple plugins that share contributor docs, vendored dev toolkits, or cross-cutting build infrastructure. Each plugin tree is self-contained; the marketplace.json enumerates them. Implies a contributor convention that repo-level state (root README, CLAUDE.md, settings.json) is non-shipped infrastructure and the plugin trees are the published artifacts.

### `strict` field default

Across all three samples the `strict` field is absent on every marketplace entry, taking the implicit-true default. Whether authors intended strict mode is not documented in any sample; the absence is uniform but not deliberate.

### `skills` override on marketplace entry

Across all three samples the marketplace entry never overrides the plugin's component layout — no `skills` carving, no path remapping. Full plugin trees ship as authored. When alternate-runtime manifests (`.cursor-plugin/plugin.json`) need different paths, they declare those at the plugin-manifest level rather than the marketplace level.

## Version authority

Where the canonical version of a plugin lives, and how many parallel version streams the manifest surface admits.

### Single source — plugin.json only

Only the plugin's own `plugin.json` declares a version. Marketplace.json carries no version field at the marketplace level or the per-entry level. Consumers resolve to whatever `main` points at; the plugin.json `version` value is informational only — there is no tag, no release, no manifest-level pinning. Simplest possible shape; no drift surface.

### Dual source — marketplace entry version + plugin.json version, hand-aligned

Both the marketplace entry's `version` and the plugin's own `plugin.json` `version` are populated. Contributor convention requires the two to match, but no automation enforces it. Drift is observed in practice — one sample carries marketplace `1.9.0` against plugin `0.1.6`, where the marketplace version ran ahead during a phase of independent bumps and was not reconciled. Drift becomes invisible because either consumer (marketplace browser, plugin loader) reads only its own field and never compares.

### Triple source — marketplace metadata version + per-entry version + plugin.json version

A monorepo with marketplace-level `metadata.version` (`0.4.0`), per-plugin marketplace-entry `version` (`0.1.0`), and per-plugin `plugin.json` `version` (`0.1.0`). Contributor docs designate the latter two as the "must match" pair and the marketplace metadata version as an independent stream tracking the marketplace itself. Three-way version space with two enforced relationships and one independent axis — the most version-aware shape, and also the most drift-prone.

### Cross-runtime version multiplication

When the same plugin ships under multiple runtimes, each runtime's manifest carries its own version field. A repo supporting Claude + Cursor + Codex maintains `version` in `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, the marketplace entry, and any runtime-specific install hint. Hand-discipline alignment with no cross-manifest validation; commit history shows explicit "align cursor plugin version to match claude plugin" commits as the only enforcement mechanism.

## Channel distribution

How the plugin offers stable vs latest streams to consumers (or doesn't).

### Single channel — main HEAD only

No stable/latest split. Users pin via marketplace ref or `@owner` resolution, and resolution lands at whatever `main` HEAD is at install time. No tags, no release-branch convention, no second `marketplace-stable.json` or analogous artifact. Appropriate for hobby-grade plugins where the distinction between "tested release" and "current main" hasn't justified the maintenance overhead. Constrains downstream pinning to commit SHAs (the only stable ref a consumer can name).

## Plugin-component registration

How the plugin tells Claude Code where to find skills, agents, hooks, and other components.

### Default discovery — no explicit paths in plugin.json

`plugin.json` declares only identity fields (`name`, `version`, `description`, `author`) and relies on Claude Code's conventional layout — `skills/`, `agents/`, `commands/`, `hooks/hooks.json`, `monitors/monitors.json`, `bin/`, `.mcp.json`, `channels/`. Adding or removing a component requires no manifest edit; the directory structure IS the registration. Constrains the plugin to the conventional layout but eliminates a class of manifest-drift bugs.

### Explicit paths in alternate-runtime plugin.json

When a plugin ships a Cursor variant (`.cursor-plugin/plugin.json`), that manifest sets explicit fields like `"skills": "./skills/"` and `"hooks": "./hooks/hooks-cursor.json"` — different path conventions, different hook manifest filename. Cursor's runtime apparently doesn't inherit the Claude default-discovery behavior, so its manifest is more verbose. Same `skills/` tree on disk, two manifest views over it.

### Component-set composition observed

Across this bin: skills (all three), commands (one), agents (one — multi-plugin monorepo), hooks/hooks.json (all three), `.mcp.json` at plugin level (one), `.mcp.json` at repo root for contributor use (one), monitors.json (one), bin/ (two — one as user CLI, one as discovery utility). One sample also ships an in-plugin MCP "channel" (research-preview feature) under `channels/<name>/`, with its own server source and dep manifest.

## Dependency installation

How the plugin installs third-party runtime packages it ships.

### No managed install — pure shell/markdown plugin

The plugin assumes a baseline of system tools (`bash`, `jq`, `git`, `python3`) on `$PATH` and detects everything else at runtime via `command -v`. No install hook, no manifest, no cache directory. Constrains the plugin to be lightweight and pushes responsibility for tool installation onto the user. Failure mode: silent degradation when a missing tool is reached at runtime — a hook depending on `jq` simply behaves differently when `jq` is absent because there's no install path to fail.

### Single-language Node install via SessionStart hook

A SessionStart hook runs an `install-deps.sh` shell script that calls `npm install <pkg> <pkg>` into `${CLAUDE_PLUGIN_DATA}/node_modules/`. The package list is hard-coded inline in the install script; no `package.json` ships in the repo. The script generates a minimal `{"private":true}` `package.json` at install time so npm has a valid project to operate on. Idempotency via a sentinel file plus a repo-committed version file (`scripts/deps-version.txt`) compared with `diff -q` against a destination copy — three-gate check (sentinel exists AND dest version exists AND content matches). Failure path explicitly removes both the sentinel and the destination version file so the next session re-attempts install. Script is `set +e` with `|| exit 0` fallthrough on every failure, with the explicit comment `MUST NEVER exit non-zero — that blocks sessions`.

### Mixed Python + Node install

Two parallel dep stories coexist: Python via PEP 723 inline metadata (every `.py` script declares its own deps in a `# /// script` block and runs under `uv run --script`, no plugin-managed venv), and Node for an MCP-channel server (installed via a SessionStart hook gated by `diff -q` between source and cached `package.json`). The Node side prefers `bun` and falls back to `npm`, runtime-probed via `command -v`. Persistence retry-invariant uses stamp-on-success rather than the docs-example rm-on-failure: the cached `package.json` is only copied AFTER `node_modules` is verified present. Functionally equivalent retry behavior, structurally different idiom.

### Inline-deps-per-script pattern (PEP 723)

Every Python file (bin dispatchers, skill scripts, hooks, monitors) starts with `#!/usr/bin/env -S uv run --script` plus a `# /// script` block declaring `requires-python` and exact-version deps (e.g. `httpx==0.27.2`). No `requirements.txt`, no `pyproject.toml`, no `__init__.py`. Each script invocation creates or reuses uv's cached ephemeral env keyed by the inline-dep hash. Trade-off: cold-start cost on every subcommand because subprocess-dispatch from a bin wrapper to a skill script materializes a fresh env, but no plugin-managed venv to maintain or invalidate.

### Persistence contract — `${CLAUDE_PLUGIN_DATA}` as install destination

Across both managed-install samples in this bin, `${CLAUDE_PLUGIN_DATA}` is the install target — `node_modules/`, version stamps, sentinels, and any persistent cache live here. `${CLAUDE_PLUGIN_ROOT}` is treated as cache (wiped on plugin update) and not used for state. One sample's contributor docs warn explicitly against the inversion: "Using `${CLAUDE_PLUGIN_ROOT}` for persistent state — WRONG, it's the cache dir that gets wiped on plugin update."

### Failure signaling — fail-open silent

Both managed-install samples fail open: install errors do not block the session. One uses `set +e` with `|| exit 0` scattered throughout; the other uses `set -euo pipefail` plus targeted `|| true` on the install command and an early `exit 0` when neither `bun` nor `npm` is available. Neither emits `continue: false` or a JSON `systemMessage`. User-facing readiness reporting is delegated to a separate SessionStart script (the env-readiness reporter) that runs alongside the installer and summarizes what's available.

## Bin-directory CLI

How the plugin uses the `bin/` directory and what role its contents play.

### User-facing CLI dispatcher

`bin/<name>` files are user-invokable command-line tools the plugin distributes onto the user's PATH (Claude Code adds each plugin's `bin/` to PATH at activation). Dispatchers route subcommands to skill scripts via subprocess. Shebang convention is PEP 723 `#!/usr/bin/env -S uv run --script` for Python dispatchers; the bin script declares minimal deps in its own inline-deps block, then subprocess-dispatches to skill scripts that declare their own. Runtime resolution uses `${CLAUDE_PLUGIN_ROOT}` with a `Path(__file__).resolve().parent.parent` fallback — works in hook contexts where the env var is populated AND in interactive contexts where it isn't.

### Discovery utility — bin as context bridge

A 5-line bash script that prints the plugin's root directory. Not a user CLI; skills invoke it (e.g. `ship-plugin-root 2>/dev/null`) to locate the plugin tree when `$CLAUDE_PLUGIN_ROOT` is unavailable. The pattern exists because Claude Code populates `$CLAUDE_PLUGIN_ROOT` only in hook contexts, not in skill or agent contexts. Skill preambles use a triple-fallback chain — env var if set, bin-wrapper output, or a hard-coded install path for cross-runtime portability. Distinct role from user-CLI bin: this is bin-as-discovery, not bin-as-tool. Constrains the rest of the plugin to assume `bin/` is on PATH.

### No bin directory

Some plugins ship no `bin/` at all — they invoke third-party CLIs from npm install output by absolute path under `${CLAUDE_PLUGIN_DATA}/node_modules/.bin/<name>`, exposing them as shell variables inside skill bodies. The plugin owns no PATH-level surface; everything is path-resolved at use site. Appropriate when the plugin is purely a knowledge/skill distributor and doesn't define new user-facing commands.

### Shipped vs hook-populated

Across all three samples the `bin/` contents (where present) are shipped as committed source. No SessionStart hook writes or mutates `bin/` files. Wrappers are static; their behavior changes only by editing and committing.

## User configuration

Whether and how the plugin declares typed user-supplied configuration.

### No userConfig

The plugin declares no `userConfig` block in `plugin.json`. All per-repo state is on-disk under repo-local directories produced by setup skills. Configuration-free shape — no secrets, no toggles, no per-user preferences exposed through the manifest. Constraint: anything that varies per user must be inferred (repo-local files, env vars, runtime detection) rather than declared.

### userConfig as typed schema with stringly-typed values

The plugin declares 15-18 `userConfig` fields per plugin (in a multi-plugin repo). Every field has `type: "string"` and a default value (`""` or a concrete string). Numeric-looking values (`MAX_ORDER_USDC: "100"`, `KELLY_FRACTION: "0.25"`) are stringly-typed and parsed downstream. No enums, no numeric or boolean types. Reference into other manifests via `${user_config.<KEY>}` substitution (observed in `.mcp.json` `env` blocks); hook and monitor scripts read the same keys via `os.environ.get(...)` because Claude Code's plugin layer populates env from userConfig before spawning scripts. No `CLAUDE_PLUGIN_OPTION_<KEY>` form observed.

### `sensitive: true` flag absent on secret fields

Across the userConfig-using sample in this bin, every secret-class field (private keys, API secrets, webhook secrets) lacks the `sensitive: true` flag despite descriptions explicitly labelling them "SECRET — treat like a password." Seven of seven secret fields lack the flag; the documented mechanism for routing to OS keychain storage is consistently skipped in favor of relying on the plugin-config storage backend. Repeated three times across three plugins in the same repo — systematic authoring gap rather than a one-off.

### Hard-coded path as missing userConfig

In one sample the plugin's primary user-configurable surface — the path to the user's Obsidian vault — is hard-coded in the README as `~/ObsidianVault/03-Resources/` and enforced by the skill's directory walk. This is what a `userConfig` field would naturally hold; instead it's a prose convention. Users with vaults at other paths must symlink or change their layout. Demonstrates the absent-userConfig path's failure mode when a real config surface exists.

## Tool-use enforcement

How the plugin uses Pre/PostToolUse hooks to gate or audit agent tool calls.

### No enforcement hooks

The plugin has no PreToolUse or PostToolUse hooks; `hooks/hooks.json` carries only SessionStart entries (or doesn't exist at all). Tool use is ungated. Appropriate for plugins whose components are skills and reference docs rather than actions with side effects.

### PreToolUse as ask-first guardrail

Two distinct PreToolUse scripts on `Bash` matcher parse the Bash argv to identify trade-placement subcommands and emit JSON `permissionDecision: ask` with a trade summary so the user sees the intent before approving. `deny` is reserved for hard policy violations (cancel-all without `--yes-really`, network not in allow-list); `allow` is implied by no-op exit. Failure posture is fail-open silent — exit 0 on parse failure or unknown commands. Output convention: stdout JSON with `hookSpecificOutput.permissionDecision` and `permissionDecisionReason`; no parallel stderr-human messages.

### PreToolUse as phase-scoped artifact gate

A single PreToolUse hook (no matcher, fires on all tools) enforces artifact-access rules driven by a YAML-frontmatter state file the orchestrator writes. Four rules encoded — block reads of cross-phase artifacts, block writes outside scoped directories, protect the state file from being overwritten by anything except the orchestrator. Only gates subagent calls (non-empty `agent_id`); orchestrator calls pass through. Fast-exit case-match on raw JSON fields skips the `jq` invocation when the tool isn't Read/Write/Edit. Output is `{"decision":"block","reason":"…"}` via `jq -n` on block; exit 0 silent on allow. Failure posture is fail-open — `set -u` only, no `-e`; errors absorb into fall-through.

### PostToolUse as audit trail

A PostToolUse hook on `Bash` matcher sniffs successful Bash commands across known venues and appends to a SQLite journal. Not validating — recording. Fail-open silent: exit 0 on parse failure, no error surfaced. Constraint: the hook fires in parallel for concurrent Bash calls; SQLite WAL mode at the consumer-skill level mitigates contention but the hook script itself doesn't take an exclusive lock.

### Output convention — JSON-only, no stderr-human parallel

Across all enforcement hooks in this bin, decisions go to stdout as JSON; no stderr-human-readable parallel pattern. Failure paths are silent — the hook script prints nothing and exits 0, leaving any user-facing readiness reporting to a separate SessionStart script.

## Session context loading

How the plugin injects context into the session at start.

### SessionStart for dependency install only

A single SessionStart hook runs an install script and emits no `additionalContext`. The hook's role is dep management; context loading isn't part of its responsibility. Constraint: dep-install correctness must not depend on session-start emitting context.

### SessionStart with no matcher — fires on every sub-event

Across all three samples in this bin, the SessionStart entry omits the `matcher` field, so it fires on every sub-event (`startup`, `resume`, `clear`, `compact`). For idempotent install checks this is fine but repetitive on heavy-compaction sessions; for context emission this means the readiness block re-prints. No sample narrows the matcher.

### SessionStart with multi-script division of labor

In a plugin that combines dep install and context emission, two separate SessionStart hooks register: the install script stays silent (its only side effect is `node_modules/`), while a sibling `session-start-env.py` prints a markdown readiness block with which env vars are set/missing, data-dir status, and channel-runtime status. Separates "make the world ready" from "tell the user what's ready."

### Layered SessionStart context with conditional inclusion

A single SessionStart script composes one `additionalContext` from up to four layers, each conditional on a file existing in the repo: a hard-coded routing policy always emitted; a curated extract from a learnings file (only entries with `**Status**: verified` frontmatter, awk-filtered on `---` record separators); a whole-file inject of a docs index; a single-line pointer to a design doc when present. Each layer adds depth on demand; absent files contribute nothing. Layer-1 routing policy hard-codes the skill catalog in bash, requiring hook updates when skills are added/renamed.

### Self-emitting schema detection for cross-runtime context

The same SessionStart script produces one of two JSON schemas based on which runtime invokes it: under Claude, `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": …}}`; under Cursor (detected via `$CURSOR_PLUGIN_ROOT`), `{"additional_context": …}`. Single script, runtime-discriminated output. Avoids duplicating the layered-composition logic across two scripts.

### XML-tag emphasis wrapping

Layer-1 routing policy is wrapped in `<EXTREMELY_IMPORTANT>...</EXTREMELY_IMPORTANT>` tags as a prompt-engineering construct emitted as session context. The wrapper is a content convention, not a hook-schema field — it goes inside `additionalContext` as raw text.

## Live monitoring

Whether the plugin ships background processes that emit notifications.

### No monitors

The plugin declares no `monitors.json`. Notifications are not part of the plugin's surface. Where session-time watching is needed, it's done via the Claude Code Monitor tool from inside skills (not the declarative monitors mechanism).

### Polling daemons via monitors.json

A plugin ships 2-3 monitor entries in `monitors.json`, each pointing at a `.py` script that polls a venue API at a fixed cadence (15s-15min) and emits one line per event. Schema fields used: `name`, `command`, `description`, `when`. `when` is `always` across all monitors observed; no `on-skill-invoke:<skill>` variant. Each monitor is a long-lived daemon launched at session start. Coupling: monitors are venue-coupled (a venue plugin ships them; venue-agnostic shared-layer plugins ship none even when they're heavier).

### Version-floor declaration absent

Where monitors are used, no plugin.json or README declares a minimum Claude Code version for the monitors feature. Repo-level docs may name a Claude Code version for unrelated features (a channels-preview floor) but not specifically for monitors.

## Plugin-to-plugin dependencies

Whether the plugin declares dependence on another plugin via the manifest schema.

### `dependencies` field absent

Across all three samples in this bin, no `plugin.json` declares the schema-level `dependencies` field. Where coupling exists between plugins (a shared math/storage plugin that other plugins consume at the file-read or subprocess layer), that coupling is documentation-only — contributor docs say "consume X from your scripts" but the manifest declares nothing. Schema-supported enforcement is deliberately skipped. Failure mode: a user installing a leaf plugin without its informally-required peer gets broken scripts at runtime with no manifest-time warning.

### `{plugin-name}--v{version}` tag format absent

No sample in this bin uses the multi-plugin-monorepo tag format. Combined with the universal absence of any tags at all (see Versioning), the format's hypothetical use case doesn't surface here.

## Testing

How the plugin verifies its own behavior.

### No tests

The plugin ships no `tests/` directory, no test files, no test framework. Verification posture leans on runtime hosts surfacing errors and on contributor-invoked review agents during authoring sessions. Manifest-correctness is trust-on-commit.

### Hand-rolled bash tests

The plugin ships `tests/*.sh` files with hand-rolled PASS/FAIL counters, `mktemp -d` fixtures, and `git init -q` scratch repos for git-state-dependent tests. No top-level runner; each test file self-executes via `bash tests/<test>.sh`. Tests mock external state where needed (e.g. `origin/HEAD` for branch-comparison logic). Coverage scope: workflow scripts and end-to-end phase flows; hooks themselves are documented as "test by piping JSON into the hook script" rather than scripted into the test suite.

### Author-time validator agents instead of automated tests

A repo with no `tests/` directory documents in contributor docs a manual-validation pipeline: contributor runs `plugin-validator` and `skill-reviewer` agents (vendored from Anthropic's official plugin suite into a separate contributor-only marketplace) after any component change. Validation is interactive, runs inside a Claude Code session, and depends on contributor discipline. Repo-level `.claude/settings.json` blocks `git commit --no-verify` and `git push --force` but no commit hook invokes the validators — the blocks prevent BYPASSING hooks but no hook exists to bypass.

## CI and release automation

How push/tag events drive verification or release artifacts.

### No CI, no release automation

Across all three samples in this bin, the repo has no `.github/` directory at all (404 from the contents API). No workflow files, no scheduled checks, no tag-driven release pipelines. Version bumps are plain commits to `main`; releases are not cut. Consumers resolve to whatever HEAD is at install time — no tag-pinning to a reviewed release, no changelog, no release notes. Documented-but-unbuilt release pipelines exist (contributor docs say "Releases via GitHub Releases tagged `v<SEMVER>`") but no commit, tag, or release artifact materializes the convention.

### Hand-bumped versions on main

The release marker is a plain commit titled `chore(plugin): bump 0.1.4 -> 0.1.5` (or the local equivalent). No automation; no pre-commit hook to derive the bump. Version drift across multiple manifest surfaces is hand-aligned via separate "align cursor plugin version to match claude plugin" commits when contributors notice.

## Marketplace validation

How the marketplace.json and plugin.json shapes are checked before publish.

### No validation

No CI workflow lints manifests; no pre-merge gate validates `marketplace.json`, `plugin.json`, `hooks.json`, or skill frontmatter. Validation relies entirely on the runtime host (Claude Code, Codex, Cursor) surfacing errors at install or runtime. Manifests are hand-edited and trust-on-commit.

### Manual validator-agent invocation

A contributor runs an interactive validator agent (`plugin-validator`, vendored from Anthropic's official plugin suite) after any component change. The agent reads manifests and skill frontmatter and reports issues conversationally. Trigger is manual; correctness depends on the contributor remembering to invoke. Frontmatter validation is delegated to a separate `skill-reviewer` agent.

## Documentation surface

What governance and consumer-facing docs the plugin ships.

### README only

The plugin ships only `README.md` at the repo root. No `CHANGELOG.md`, no `architecture.md`, no `CLAUDE.md`. Architecture content (where present) lives inside the README as a narrative section. Minimal-overhead docs surface; appropriate for plugins where the README plus skill bodies cover everything. Constraint: rationale for breaking changes lives only in commit messages — a user upgrading across a major bump has no migration guide.

### README + per-plugin READMEs + per-plugin CHANGELOGs + repo-root CLAUDE.md

A monorepo ships a heavy repo-root `README.md` (architecture diagram, FAQ, badges, schema.org JSON-LD for LLM/search indexing), a per-plugin `README.md` for each plugin tree, a per-plugin `CHANGELOG.md` in Keep-a-Changelog-lite format, and a repo-root `CLAUDE.md` documenting layout, contributor pipeline, hard rules, and pitfalls. No `architecture.md` — architecture content is duplicated between the root README's diagram and the CLAUDE.md's layout section. Heavy doc footprint scaled with the multi-plugin scope.

### README + WALKTHROUGH.md as architecture-adjacent

A single-plugin repo ships a `README.md` (install, prerequisites, per-command usage) and a long-form `WALKTHROUGH.md` (~17KB) that describes the underlying methodology, schema contract, and per-command flow. The walkthrough is framed as user tutorial but carries content an `architecture.md` would otherwise hold. No `CLAUDE.md` at repo root — though notably the plugin generates a `CLAUDE.md` template inside each user-created data directory as a per-data-directory schema anchor (a distinct use of the filename: not plugin governance, but generated user data).

### AGENTS.md as cross-runtime governance unification

A repo serving Claude + Cursor + Codex consumers uses `AGENTS.md` (Codex-first convention) as the single agent-facing governance doc, in place of the Claude-native `CLAUDE.md`. Carries what would be both `CLAUDE.md` (operational procedures) and `architecture.md` (how the plugin works) in a Claude-native convention. Trade-off: per-runtime specificity for a single doc surface. Sub-architecture lives in `docs/design/<NNN>-<topic>.md` files (one observed) — numbered design notes rather than monolithic.

### Auto-generated docs index

`docs/DOCS_INDEX.md` is generated by a repo script (`scripts/generate-docs-index.sh`) and injected into sessions via SessionStart Layer 3. Live index over `docs/`, not a hand-maintained TOC. Test coverage exists for the generator script.

### Schema.org JSON-LD as LLM-indexer surface

The repo-root README.md ends with a `<script type="application/ml+json">` block declaring `@type: SoftwareApplication`. Explicit comment in source: "Machine-readable metadata for LLM + search indexers (Perplexity / ChatGPT / Claude / Google AI Overviews)." Treats the README as a distribution surface for LLM-driven discovery, not just human readers.

### Community health files absent

Across all three samples, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/`, and `PULL_REQUEST_TEMPLATE.md` are uniformly absent. Where security-relevant policy exists (secret-file deny rules), it lives inside `.claude/settings.json` rather than a standalone doc.

### Badges and status indicators

One sample's README carries Shields.io badges (license, runtime, language, dynamic stars/forks/issues/last-commit). The other two ship no badges. Optional polish, no shared pattern across the bin.

## Multi-runtime polyglot support

Whether the same plugin tree serves multiple agent runtimes (Claude Code, Cursor, Codex).

### Single-runtime — Claude Code only

Plugin manifests live exclusively under `.claude-plugin/`. No `.cursor-plugin/`, no `.codex/`. Skills, hooks, and bin wrappers assume Claude Code's env vars and hook schema. The default shape across most of the bin.

### Triple-runtime parallel manifests

The repo ships three parallel manifest trees: `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, and `.codex/` (install-by-symlink). Same `scripts/` and `skills/` trees. Hook schemas differ per runtime — Claude uses nested `{hooks:[{hooks:[{type, command}]}]}`, Cursor uses flat `sessionStart: [{command: "./hooks/session-start"}]` plus a top-level `version: 1` field, Codex adds `statusMessage` and `timeout` fields Claude lacks. A trivial bash exec wrapper bridges Cursor's relative-command schema to the shared script. Skill preambles use a triple-fallback chain (`SHIP_PLUGIN_ROOT` env, bin-discovery wrapper, hard-coded Codex install path) to locate the plugin tree under any runtime. Cross-runtime version drift is live and hand-aligned.

## Permission and contributor governance

How the repo distinguishes contributor-environment policy from end-user-environment policy.

### Plugin-root settings.json — agent pointer only

A `settings.json` at each distributed plugin's root carries `{"agent": "<router-name>"}` to activate a custom agent as the main thread when the plugin is enabled. Contributor docs note that only `agent` and `subagentStatusLine` are the supported keys — unknown keys silently ignored. Convention: point `agent` at a broad router (not a narrow specialist) so the plugin feels natural when enabled. Distinct from the repo-root `settings.json` (governs contributor sessions) — the plugin-root file governs end-user sessions with the plugin enabled.

### Repo-root .claude/settings.json — contributor-only permission matrix

A `.claude/settings.json` at the repo root declares `defaultMode: "acceptEdits"`, a ~100-entry allow/ask/deny permission matrix, and secret-file deny rules (`Read/Edit/Write` against `.env*`, `credentials*`, `*.pem`, `*private*key*`). Governs contributor Claude Code sessions against this repo only; never shipped to end users (the entire `.claude/` tree is contributor-only by convention). Replaces a `SECURITY.md` — security policy as enforced settings rather than narrative doc.

### Vendored contributor toolkit as sibling marketplace

`.claude/plugins/.claude-plugin/marketplace.json` hosts a separate marketplace (e.g. `<repo>-local`) with vendored Anthropic-official plugins (`plugin-dev`, `claude-code-setup`). Contributors activate it via `/plugin marketplace add ${CLAUDE_PROJECT_DIR}/.claude/plugins`. Repo invariant: "`.claude/` is contributor-only and never shipped to end users." Reuses the marketplace.json mechanism as a dev-toolkit bootstrap rather than for plugin distribution.

## PATH augmentation

How the plugin handles user-installed CLIs that aren't in the minimal PATH Claude Code propagates.

### PATH-bootstrap script sourced by every hook

A `scripts/path-bootstrap.sh` prepends common user bin dirs (`$HOME/.ship/bin`, `/opt/homebrew/bin`, `/usr/local/bin`, `$HOME/.local/bin`, `$HOME/go/bin`) to PATH. Sourced from the top of every hook script. Driven by the observation that "Claude Code and some CI environments inherit a minimal PATH that excludes common install dirs" — an adaptation layer for missing-PATH pathology rather than a plugin-managed install of those tools.

### Runtime-environment sanitization at invocation site

A skill wraps third-party CLI invocations in `env -u <VAR> <cli>` to defend against user-environment contamination — specifically `env -u BUN_INSTALL` to prevent Bun's bundled SQLite (which lacks extension loading) from being picked up over Node when invoking a tool that needs SQLite extensions. Plugin-side defense at the skill level rather than at install time.

## MCP server registration scope

Where `.mcp.json` lives and which audience it serves.

### Plugin-distributed MCP server

A plugin ships `.mcp.json` inside its plugin tree, registering an MCP server (e.g. a Bun/TypeScript channel server) that the plugin distributes. Substituted via `${user_config.<KEY>}` for env values. Travels with the plugin to consumers. Constraint: the plugin must also ship the server source (`channels/<name>/server.ts`) and its dep-install hook.

### Repo-root MCP server for contributor use

A `.mcp.json` lives at repo root (not under any plugin tree) registering a peer MCP server for use by skills during local development of the plugin itself. Consumers installing via `/plugin install` don't inherit this — it's not part of the plugin tree. Contributors clone the repo and get the MCP wiring as part of working on the plugin source. Distinct role: plugin-distributed MCP travels to users; repo-root MCP serves the maintainer.

## Novel cross-cutting concerns

Patterns surfaced by samples in this bin that don't fit a single role.

### MCP "channel" as inbound event bus

One sample ships an MCP-channels-as-inbound-event-bus pattern (research-preview Claude Code feature gated to v2.1.80+ and `claude.ai` login, not API-key auth). The channel server (Bun/TypeScript) declares `claude/channel` capability, exposes HMAC-gated webhook routes (`/tradingview`, `/polymarket/fill`, `/cdp`, `/commerce`, `/custom?kind=...`), and converts each inbound event into a `<channel source="..." type="..." ...>...</channel>` context tag inside the running Claude session. Distinct primitive from `monitors.json` (outbound stdout lines) and from normal MCP tool servers (stateful request/response). One-way inbound only — README claims "NO reply tool, NO permission relay."

### Generated-package.json pattern

A SessionStart install script writes a minimal `{"private":true}` `package.json` into `${CLAUDE_PLUGIN_DATA}` on first run rather than shipping one. Keeps the plugin repo free of Node-ecosystem noise (no committed lockfile, no `node_modules/` gitignore, no committed dep manifest) while still giving npm a valid project to operate on. Authoritative dep declaration lives inline in the install script's `npm install <pkg>` command.

### Plugin scaffolds CLAUDE.md as user-data schema

A plugin generates a `CLAUDE.md` template inside each user-created data directory (`~/ObsidianVault/<wiki>/CLAUDE.md`) as part of its setup operation. This `CLAUDE.md` is not the plugin's own governance doc — it's user data that becomes the schema contract for subsequent skill invocations. The skill's "active wiki detection" walks up the filesystem looking for `CLAUDE.md` + a sibling marker as co-present anchors. CLAUDE.md repurposed as per-subdirectory schema marker.

### Graceful-degradation via fallback tool

When a plugin's optional tool (installed by SessionStart) is missing, the skill falls back to a manual stdlib-only path (e.g. `wiki/index.md` read + grep instead of `qmd` query). Documented fail-soft inside the skill body, not an install retry. The plugin works in reduced mode even if dep install permanently fails. Pairs with the install script's fail-open stance.

### Three-gate idempotency

A SessionStart dep-install script checks `sentinel file existence` AND `dest version file existence` AND `diff -q version file match` before skipping. Each gate catches a different corruption mode (aborted install, partial file write, upstream version bump). Stricter than any single gate and resilient under partial-state recovery.

### PreCompact hook for state-file eviction

A PreCompact hook scans the pre-compact transcript for an interrupt-then-unrelated-user-message pattern and archives the orchestrator's state file before compact removes the evidence. Protects against post-compact false resumption when the user cancelled mid-flow. Rarely-used hook event put to specific use.
