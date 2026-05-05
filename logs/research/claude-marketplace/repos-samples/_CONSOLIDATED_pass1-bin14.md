# Sample

Pass-1 Phase-1a partial for bin 14. Functional decomposition of hwuiwon/autotune, iVintik/codeharness, and includeHasan/prospect-studio, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How the plugin is presented to a marketplace aggregator and bound to its source.

### Single repo-root marketplace.json with relative source

A `.claude-plugin/marketplace.json` at repo root declares one or more plugins; the single plugin's `source` is `"./"` (relative). The repo doubles as the marketplace and the plugin. Appropriate for small one-author plugins where the marketplace and the plugin share a release cycle. Constrains version authority — `plugin.json` carries the only version; the marketplace entry has no version field, eliminating drift.

A live schema gotcha shows up here: `"source": "."` fails marketplace validation; the trailing slash (`"./"`) is required. Marketplace-level `metadata` wrapper and `metadata.pluginRoot` may both be absent for this layout.

### No in-repo marketplace; aggregator dispatched cross-repo on release

The plugin repo carries no `.claude-plugin/marketplace.json` at all. A separate, often private, marketplace-aggregator repo registers the plugin; the plugin repo's release workflow fires a `repository_dispatch` event (e.g., `plugin-release` with `{plugin, version}` payload, authenticated by a `MARKETPLACE_TOKEN` PAT scoped to the aggregator) to update the aggregator. Appropriate when the author wants the plugin repo to look like a normal source repo (npm-publishable, no marketplace concerns) and centralizes discovery in a separate aggregator they control.

Constrains forks — without the cross-repo dispatch token, a fork cannot fully release. Constrains discoverability fields — `category`/`tags`/`keywords` may live only on the aggregator side, invisible from the plugin repo.

## Per-plugin discoverability metadata

Fields a marketplace consumer uses to find, categorize, and label a plugin.

### Marketplace-entry facets (category, tags) plus duplicated keywords on plugin.json

The marketplace entry carries `category` and `tags`; `plugin.json` independently carries `keywords` with semantically identical values. Two field names for the same intent across two manifests — drift surface but no enforcement. The marketplace consumes its facets; the plugin manifest's `keywords` are decorative unless surfaced elsewhere.

### Bare-minimum plugin.json (name, version, description only)

`plugin.json` declares only `name`, `version`, `description` — no `category`, `tags`, `keywords`, `author`, or `homepage`. Discoverability is fully delegated to whichever marketplace aggregator carries the entry. Workable when an external aggregator supplies the metadata, but ships zero plugin-self-described discovery facets and depends on the aggregator being authoritative.

### `$schema` absence

No `$schema` URL on either marketplace or plugin manifests across the bin. Editor schema-completion and ahead-of-time validation are unavailable; reactive detection (install errors, CI gates) is the only feedback channel.

## Plugin source binding

How the marketplace entry points at plugin source.

### Relative same-repo (`./`)

Single-plugin marketplace where the plugin lives at the repo root; `source` is `"./"`. Trailing slash is mandatory — bare `"."` fails validation. Suits the single-plugin-at-root layout; trivial binding, no version drift surface when the marketplace entry omits its own version.

### Direct git install (no marketplace.json in source repo)

Users install via `claude plugin install github:<owner>/<repo>` — no marketplace-level binding because no marketplace.json exists in the plugin repo. The cross-repo aggregator handles binding separately.

## Version authority

Where the plugin's version of record lives.

### plugin.json as sole authority

`plugin.json` carries the version; the marketplace entry omits a version field. No drift surface. Simplest model — works for single-plugin-at-root layouts.

### Dual-manifest versioning with CI gate

`package.json` (npm) and `.claude-plugin/plugin.json` both carry the version because both ecosystems insist on owning it (npm package and Claude Code plugin). Neither derives from the other. CI enforces equality with a `Verify version sync` step that fails the build when they differ. CLAUDE.md prescribes "after bumping plugin.json, also update package.json before creating the GitHub Release." A "two sources, one gate" pattern, distinct from single-source-of-truth derivation.

### Triple-manifest versioning, ungated

Three independent files (marketplace.json, plugin.json, package.json) each declare the version with no CI gate. Drift is possible and observed in practice — declared version ahead of the latest tagged release, manual bump commits without tags. The risk materializes when users following GitHub Releases see one version while marketplace installs (HEAD) deliver another.

## Channel distribution

Whether the plugin offers stable/latest channel separation or any pinning surface.

### Single-channel from main (HEAD-only)

No stable/latest split, no release branches, no channel-pinning artifacts. Users `/plugin marketplace add` resolves to whatever `main` (or `master`) currently points at. README typically says "re-run install to update." Appropriate for small-author plugins where every release is "the latest"; constrains rollback because there is no pinnable artifact apart from raw git refs.

### Plugin-ref ↔ CLI-version coupling via SessionStart

The plugin ships a SessionStart hook that pins an external runtime tool (e.g., `npm install -g <pkg>@<plugin-version>`). The plugin-ref and the runtime tool's version are coupled at session start, not by a marketplace channel mechanism. Effectively a "channel" that lives in the hook layer rather than the marketplace.

## Release cadence and tagging

How releases on `main` are marked and triggered.

### Tag-on-main with manual GitHub Release

Tags `vX.Y.Z` live on the default branch; releases are not triggered by tag push but by a GitHub Release `published` event. The author runs `gh release create v<version> --generate-notes` to fire the release pipeline. Tag alone does not ship — the manual release step is load-bearing. Appropriate when release notes need human curation; constrains automation because forgetting `gh release create` silently skips the publish.

### Tag-on-main with automation triggered by tag push

Tags on the default branch with releases triggered by tag push. Not exhibited in this bin's samples; named here for the role's branching surface only when warranted.

### Untagged version bumps

`plugin.json` bumps land as ordinary commits ("bump version" / "chore: vX.Y.Z") with no corresponding git tag and no GitHub release. CHANGELOG may have versioned headings without git anchors. Constrains downstream pinning — there is no `git checkout vX.Y.Z` available — and creates an apparent version that disagrees with the latest tagged release.

### Pre-commit version bump

Not observed in this bin. None of the three samples runs a pre-commit hook to auto-bump `z`.

## Plugin-component registration

How plugin.json points at agents, skills, commands, hooks, and MCP servers.

### Default directory-name discovery

`plugin.json` declares no component fields. Claude Code auto-discovers `commands/`, `agents/`, `skills/`, `hooks/`, `.mcp.json` by directory convention. Cleanest for small plugins; constrains refactors — renaming a subdirectory silently breaks discovery with no manifest schema to catch the drift.

### Reference style — explicit paths

Not exhibited in this bin; default discovery is universal across the three samples.

## Agent frontmatter shape

Fields used in agent markdown frontmatter.

### Minimal (`name`, `description`, `tools`)

Bare-minimum agent declaration. `tools:` is a YAML list of plain tool names (`[Bash, Read, Write, Edit, Glob, Grep]`) or a comma-separated string — both forms accepted. No model selection, no turn budget, no permission-rule syntax (`Bash(uv run *)`).

### Extended (`model`, `effort`, `maxTurns`, `disallowedTools`)

Adds model selection (`model: sonnet`), effort budget (`effort: high`), turn cap (`maxTurns: 60`), and a denylist (`disallowedTools:`). The denylist is used in two distinct shapes:

- **Subtractive** — agent omits `tools:` (inheriting harness defaults) and uses `disallowedTools:` to subtract a few specific tools. Compact when the agent should mostly behave like a default agent minus a few capabilities
- **Belt-and-suspenders** — agent declares both an explicit `tools:` allowlist AND a `disallowedTools:` block, redundantly naming forbidden tools. Suggests authors do not uniformly trust `tools:` as a hard allowlist, or are defensively coding against ecosystem-wide enforcement-semantics ambiguity

The plain MCP tool id form (`mcp__<server>__<tool>`) appears alongside core tool names in both `tools:` and `disallowedTools:`.

## Dependency installation

How runtime dependencies that aren't bundled in the plugin source get materialized.

### Not applicable — stdlib only

Plugin code uses only language-stdlib + system tools (Python 3 stdlib, bash, git). No `requirements.txt`, no `pyproject.toml`, no `package.json` `dependencies`. Runtime prerequisites are documented in README (`Python 3.6+`, `Bash`, `Git`) but not validated at session start. Constrains: silent failures if a stdlib feature exceeds the documented floor.

### SessionStart hook → npm global install pinned to plugin version

The SessionStart hook runs `npm install -g <pkg>@<plugin-version>`, where `<plugin-version>` is grep-extracted from `plugin.json`. Installs into the user's npm prefix (global), not the plugin directory. Opt-out via env var (e.g., `<TOOL>_NO_AUTO_INSTALL=1`). The plugin "installs its own peer CLI" as a side effect of session startup. Pin is exact (`@<version>`) — fully deterministic per session.

Constraints: requires `npm` on PATH (fail-open with stderr warning otherwise); writes to a global location outside `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`, mutating the user's system state; matcher set to `*` means version check fires on `clear` and `compact` too, not just startup; 120-second hook timeout may be tight for cold installs on slow networks; opt-out env var is undiscoverable unless the user reads the hook source. Hook posture is fail-open (`set -uo pipefail`, no `-e`; always `exit 0`).

### SessionStart hook → npm install into ${CLAUDE_PLUGIN_ROOT}

The SessionStart hook runs `npm install` inside `${CLAUDE_PLUGIN_ROOT}/<server-dir>/`, populating `node_modules/` adjacent to the importing JS files. Driven by a hash sentinel (`sha256` of `package.json`, persisted to `.package-hash` next to `node_modules/`); reinstall fires when hash differs OR `node_modules/` is missing. Fallback hash chain handles missing `sha256sum` / `shasum` / last-resort `wc -c` byte count.

The install location choice is load-bearing — ESM `import` resolution walks the filesystem from the importer's location looking for `node_modules`, and `NODE_PATH` is CJS-only (silently ignored by ESM). So `${CLAUDE_PLUGIN_DATA}/node_modules` would break every `import`. Documenting this rationale inline in the install script (rather than in a separate planning doc) gives any developer reading the hook the "why" without external references.

Failure posture: silent. `exit 0` unconditionally; `npm install` stderr swallowed with `2>/dev/null`. No `rm` on failure — sentinel simply not written, so next session re-tries via hash mismatch. Partial `node_modules/` from a failed install can linger because there is no explicit cleanup; converges eventually but can hide a persistent failure mode (e.g., no network) behind the silent-exit-0.

Constraints: no lockfile committed (`--omit=dev` flag, no `package-lock.json`), so transitive deps are non-reproducible across sessions. No `set -euo pipefail`; the `cd && npm install && echo > sentinel` chain prevents sentinel write on any step's failure but not via shell strict mode.

## Bin-wrapped CLI distribution

When a plugin exposes user-invokable CLIs.

### Multi-script bash CLI with `${CLAUDE_PLUGIN_ROOT}` resolution

Multiple bash scripts under `bin/` (e.g., `<tool>`, `init-experiment.sh`, `run-experiment.sh`, `dashboard.sh`, `setup-permissions.sh`, `statusline.sh`). Uniform `#!/usr/bin/env bash` shebang. Each script computes `<TOOL>_HOME="${CLAUDE_PLUGIN_ROOT:-${<TOOL>_HOME:-$(dirname "$SCRIPT_DIR")}}"` so the scripts work under plugin install, manual clone, or ad-hoc invocation. Sources a shared library (`lib/state.sh`) for state operations. POSIX-only (no `.cmd`/`.ps1` pair); macOS-aware (e.g., warns "no `grep -P`; use `sed`/`awk`/`python3 -c`").

### Single bash wrapper exec'ing a Node bundle

`bin/<tool>` is a thin bash wrapper that resolves `PLUGIN_ROOT` from the script location and `exec node "$PLUGIN_ROOT/dist/index.js" "$@"`. Script-relative resolution only — does NOT consult `${CLAUDE_PLUGIN_ROOT}`. Fails if `dist/` isn't shipped (e.g., when `.gitignore` excludes the build output and no `prepare`/`postinstall` builds it at install time). When the bundle isn't present, downstream consumers fall through to a different CLI resolution path (e.g., the SessionStart-installed global `<tool>` on PATH), making the in-repo wrapper effectively dead code despite its comment claiming "works without global npm install" — wrapper-as-aspirational-contract rather than wrapper-as-runtime.

### Plugin-bin + npm-bin dual-target

`package.json` declares `"bin": {"<tool>": "./bin/<tool>"}` so `npm install -g <tool>` or `npx <tool>` exposes the same CLI the plugin install does. Dual-target distribution lets users drive the tool without installing Claude Code plugins at all. Adds `engines.node >= <N>` to `package.json` even if the core plugin code is bash/Python — Node is only needed for the npm consumption path.

### Not applicable — no `bin/` directory

All executable entry points are MCP servers (JS) or hook scripts (Python/bash) invoked by the harness, not user-invoked CLIs on PATH.

## User configuration surface

How configuration that users supply (secrets, paths, identifiers) is declared and consumed.

### Plugin `userConfig` block with typed fields and substitution

`plugin.json` declares a `userConfig` object; each field carries `type` (`string`, `directory`, `boolean`), `title`, `description`, and `sensitive: true | false`. Fields that hold secrets carry `sensitive: true` (stored in OS keychain); non-secret strings (URLs, identifiers, workspace paths) are explicitly `sensitive: false` or rely on a non-string type like `directory`. References flow through to consumers via `${user_config.<key>}` substitution in `.mcp.json` and as `CLAUDE_PLUGIN_OPTION_<KEY>` env vars in scripts. The `type` and `title` fields are load-bearing — current manifest-validator schema rejects entries that omit them, breaking installs reactively until the user-config block is updated. The `directory` type is a typed variant beyond bare strings.

A recurring pattern within this path: remote MCP servers receive bearer tokens by injecting `${user_config.<key>}` into a `headers.Authorization` value, with the key marked `sensitive: true`. The substitution flows from keychain → manifest → outbound HTTP header without disk persistence — distinct from local-MCP env-var injection.

### Project-local config file (no `userConfig`)

Plugin reads configuration from a project-rooted file (e.g., `<tool>.config.json`) at runtime via its own scripts, bypassing the Claude Code `userConfig` surface entirely. Appropriate when the configuration describes the active session/project (metric direction, playbook order, healing budget, etc.) rather than a global user preference. Stored alongside the session's other persistence files so the whole session travels with the project. Tradeoff: no UI surface — users edit a JSON file directly.

### Env-var opt-out without `userConfig` declaration

A single boolean opt-out (e.g., `<TOOL>_NO_AUTO_INSTALL=1`) is read from the environment by a hook script, with no corresponding `userConfig` field. Documented only in the hook source comment header. Constrains discoverability — users who want the opt-out have to read the hook to find it; a `userConfig` boolean would surface it in the plugin configuration UI.

## Tool-use enforcement (PreToolUse and PostToolUse hooks)

Hooks that gate or observe tool calls during a session.

### PreToolUse Bash matcher as executable-path enforcer

A `PreToolUse` hook with `matcher: "Bash"` parses the agent's intended command and rejects invocations that diverge from a sanctioned shape. Example: validates that a `--command` flag passed to a benchmark runner resolves to a specific known-good script (e.g., `./<tool>.sh`), after stripping a fixed set of wrapper prefixes (`env`, `time`, `nice`, `nohup`, `timeout <n>`, `VAR=val`). Blocks with `exit 2` + stderr human-readable message; pass-through `exit 0` silently.

Self-arming — the hook only activates when its target artifact exists in the workdir AND the relevant mode is active; outside that envelope, parse failures fall through with `2>/dev/null || echo ""` per-statement fallbacks. Fail-open by design on parse errors to avoid bricking legitimate Bash use.

Constraints: regex-based command parsing is best-effort; commands constructed via shell variable expansion or command substitution can be read literally and slip through; the `STRIPPED` sed pipeline strips only a fixed wrapper vocabulary, so novel wrappers (`chrt`, `taskset`, `stdbuf`) would block legitimate invocations. Distinct from a write-guard: this gates an agent's command construction, not file writes.

### PostToolUse with no matcher (universal observation)

A `PostToolUse` hook with no `matcher` field fires after every tool call (including read-only `Read`/`Grep`/`Glob`). Funnels every tool invocation into a single Python recorder that appends to a JSONL log. High-volume write path; payload truncation (e.g., 2000/4000/500 char caps per field) is a deliberate readability tradeoff, not an oversight. Appropriate when the hook serves as the ingest stage of an analytics pipeline.

### PostToolUse with selector matcher (targeted observation)

A `PostToolUse` hook with a regex matcher (e.g., `Write|Edit`, `mcp__<server>|WebFetch|WebSearch`) appends to a domain-specific log file. Multiple selector hooks compose alongside the universal one. Each writes to its own append-only file (`documents/activity-log.md`, `research/search-log.md`).

### Documentation-asserted but unwired hooks

ARCHITECTURE.md describes a richer hook surface (`pre-commit-gate.sh`, `post-write-check.sh`, `post-test-verify.sh`) than `hooks/hooks.json` actually wires. Either future work or invoked by a non-Claude-Code mechanism. Surface-asymmetry is a research-relevant signal: docs may overstate the shipped enforcement surface.

## Hook failure posture

How hooks behave on error.

### Fail-open with `exit 0` discipline

Every hook script exits 0 on any failure. Combined patterns:

- `set -uo pipefail` (no `-e`) plus per-statement `|| echo ""` fallbacks
- Inline `bash -c '… || exit 0'` trampoline at the `hooks.json` command layer
- Python scripts with top-level `try/except` and `sys.exit(0)` on failure
- `trap 'exit 0' ERR` while preserving `set -e` semantics elsewhere

Multiple layers of fail-open compose to "never block the user's session" as an explicit principle. The system can be three layers deep — trampoline + script-level + handler-level. Visible across the bin and across sibling research entries (Arcanon-hub/arcanon's `trap` form is a more ergonomic shape of the same principle).

Constraints: persistent failure modes (no network, missing tool, malformed input) are silently absorbed and produce no diagnostic surface beyond stderr lines a user is unlikely to read. Diagnosing a "the hook isn't working" report requires reading the hook source.

## Cross-platform Python invocation

How Python hook scripts cope with the absence of a uniform `python3` on every platform.

### Bash trampoline resolving python3 → python → py

`hooks/hooks.json` commands are wrapped in `bash -c 'PY=$(command -v python3 || command -v python || command -v py); [ -n "$PY" ] && "$PY" <script> <arg> || exit 0'`. The trampoline accommodates Windows / Git-Bash-on-Windows where `python3` may not exist but `python` or `py` does. Documented in CHANGELOG as a Windows-compatibility fix.

Constraints: the trampoline shape is duplicated inline across every hook entry. Any change to it (timeout flag, alternate resolution order, switching to `type -P`) requires repeating the edit at every site. No shared helper script extracted in this bin.

## Session context loading

How the plugin loads context at session boundaries.

### File-backed context written at SessionStart

A SessionStart hook runs a script that scans some workspace state and writes a daily/cycle brief to a known file location (e.g., `notes/daily/<date>-brief.md`). The model does not see the brief automatically; the user opens it or a downstream skill reads it on demand. Less intrusive than `additionalContext` injection — survives token-limit pressure, inspectable, idempotent. Tradeoff: discoverability, since the prompt has no signal that fresh context just landed.

### Agent-driven resume protocol (no SessionStart)

No SessionStart hook is registered. Resume context is loaded by the agent itself per a "Session Resume Protocol" in its agent.md (reads a session-brief markdown, append-only JSONL, current state JSON, idea log). Resume only fires when the user launches the specific agent explicitly — a normal Claude Code session opened in the same directory does not auto-load. Workable when context loading is agent-bound and not session-bound.

### `additionalContext` injection

Not exhibited in this bin. None of the samples emits structured JSON with `hookSpecificOutput.additionalContext`.

## Live monitoring and notifications

How a running session surfaces ongoing state to the user.

### Status line as primary observability surface

Instead of a `monitors.json`, the plugin integrates with Claude Code's `statusLine` setting. A bash script (`bin/statusline.sh`) reads both the harness's session JSON on stdin and walks up to a project marker (e.g., `.git`) looking for plugin state files. Emits a single colorized line with a health glyph (●/▲/◆/⚕/✖/⏸), counters, streaks, durations, cost, context %. Auto-installed into the user's `.claude/settings.local.json` by a setup script.

Composition via `--chain <prior-cmd>`: the statusline script accepts an existing statusLine command and delegates the raw session JSON to it before printing its own line, preserving prior configuration. The setup script auto-detects an existing `statusLine` in `~/.claude/settings.json` or project settings and wraps it with `--chain` rather than overwriting.

Most plugins treat statusLine as a user-owned concern; this path claims it as a plugin surface and composes with prior values rather than replacing.

### `monitors.json` system

Not exhibited in this bin. Named for the role's branching surface only — none of the three samples ships a `monitors.json`.

### Standalone terminal dashboard (out of plugin scope)

`bin/dashboard.sh --watch` runs as a user-invoked terminal dashboard in a separate shell. Not plugin-managed — the user starts and stops it; the plugin only writes the state files the dashboard tails.

## Project-scoped permission grant

How the plugin requests or applies permission entries beyond what marketplace metadata covers.

### Setup script writes scoped entries into target project's settings.local.json

A bash script under `bin/` (e.g., `setup-permissions.sh`) writes an enumerated allow-list of specific paths and command shapes into the target project's `.claude/settings.local.json`. Examples: specific script paths, project-relative glob shapes (`./<tool>.sh*`), narrow git operations (`git checkout -b <prefix>/*`, `git commit -m "<prefix>:*"`, scoped `git add`/`log`/`diff`/`status`/`rev-parse`), plus the `statusLine` block. Existing `permissions.allow` entries are preserved; duplicates skipped.

Allow-list-first (not `*`-blanket) — each grant is the narrowest pattern that lets the workflow function. Constrains: the grant set is plugin-author-curated; expanding the workflow requires editing the setup script and re-running. The grants live in the user's project, not the plugin, and persist across plugin updates until the user removes them.

## Plugin-to-plugin dependencies

Manifest-level binding to other plugins.

### Not used; content-level integration with a sibling project

`plugin.json` has no `dependencies` field. Where the plugin integrates with another project (e.g., a methodology framework like BMAD), the integration is content-level — embedded artifacts under a directory prefix and a dedicated skill that consumes them — not manifest-level. If the other project ships as a Claude Code plugin in the future, a `dependencies` entry would be a cleaner binding.

## Testing infrastructure

How the plugin's correctness is verified at the source level.

### Multi-stack test setup (vitest + BATS)

Unit tests via vitest (1650+ tests at the sampled snapshot) with config at `vitest.config.ts`; shell-script integration tests via BATS, invoked as `bats tests/*.bats`. BATS installed at CI time via git clone + install script (not an action). Tests directories at `test/` (vitest) and `tests/` (BATS) coexist. A `verification/` directory is a product artifact (per-story proof docs) not test code.

### No automated tests

Zero test framework, no `tests/` directory; CLAUDE.md may explicitly state "No test suite. The dev loop is: edit → reinstall the plugin → exercise skills manually." Manual validation steps documented as ad-hoc commands (e.g., `claude plugin validate .`, type-check via `uvx ty check <file>`). Constrains: schema regressions and frontmatter breakages ship reactively — each one detected by a user install error, then fixed in a follow-up release.

## CI pipeline

GitHub Actions workflow shape.

### Two-job workflow — build-and-test plus validate-plugin

`ci.yml` runs on push and PR to default branches. Job 1 (`build-and-test`): `npm ci` → version-sync gate → `npm run build` → vitest unit tests → install BATS → `bats tests/*.bats`. Job 2 (`validate-plugin`): `python3 -c` JSON parse of `plugin.json`, required-field check (`name`/`version`/`description`), `bash -n` syntax check on subset of shell scripts.

Pinned to `ubuntu-latest` + Node 20. No matrix. Action pinning by tag (`@v4`), not SHA. No `setup-node`-level npm cache enabled — `npm ci` pays full download cost every run. The shell-syntax glob may exclude critical directories (e.g., omits `hooks/*.sh`), creating coverage holes.

Validation surface is hand-picked — three plugin.json fields. `hooks/hooks.json` is not JSON-parse-checked; agent/skill/command frontmatter is not validated. A malformed hook config passes CI and fails silently at session start.

### No CI

No `.github/workflows/` directory. All validation is manual or reactive (install-time errors). Schema fixes appear as recurring entries in CHANGELOG (the cost signature of "no manifest-validation gate").

## Release automation

How a tagged version becomes a published artifact.

### Multi-target release pipeline (npm + cross-repo marketplace dispatch)

`release.yml` triggers on `release: [published]` (GitHub Release event) or `workflow_dispatch` with a `tag` input. Three jobs: `test` (re-runs CI flow plus `npm run lint` and size guards), `publish-npm` (`npm publish --access public --provenance` via OIDC trusted publishing — no `NPM_TOKEN`), `marketplace` (cross-repo `repository_dispatch` to the aggregator with `MARKETPLACE_TOKEN`).

Manual `gh release create` is load-bearing — tag push alone does not ship. The `publish-npm` job re-runs `npm ci` + `npm run build` rather than consuming an artifact from the `test` job; the `dist/` that tests validated is rebuilt in `publish-npm`. Reproducibility tradeoff acceptable for small CLIs but a gap for stricter pipelines. Cross-repo dispatch token coupling means a forked user cannot release without the aggregator-scoped PAT.

Split runtime: `test` on Node 20, `publish-npm` on Node 24. Engines-compatibility issues between the test and publish runtimes can slip through.

### Manual release (no automation)

No `release.yml`. Releases are bump-`plugin.json` + commit + push. `CHANGELOG.md` versioned headings without git tags or GitHub releases — no pinnable artifact. Constrains: downstream `git checkout v<version>` has no anchor, and `/plugin marketplace add` always resolves to `main`.

## Marketplace validation

Whether the plugin's manifests and component files are validated.

### CI-gated minimal validation (plugin.json fields + shell syntax)

A `validate-plugin` CI job parses `plugin.json` JSON, checks required fields (`name`, `version`, `description`), and runs `bash -n` against curated shell-script globs. No frontmatter validation, no `hooks/hooks.json` validation, no formal JSON-schema validation. Limited but better than nothing; missing surfaces ship undetected.

### Manual validation only

`claude plugin validate .` documented in CLAUDE.md as a developer's local step; not gated in CI.

### No validation

Zero manifest validation. Schema breakages are caught reactively by users at install time and fixed in follow-up releases.

## Documentation surface

Documents at the repo / plugin root.

### Three-document model (README + ARCHITECTURE + CLAUDE)

`README.md` (user-facing — install, usage, command tables, integration notes), `ARCHITECTURE.md` at repo root (entry point, module map, lib layout, hook list — may describe more than is shipped), `CLAUDE.md` at repo root (developer-facing release process, conventions, channel distribution notes). The architectural document may describe a richer hook surface than `hooks/hooks.json` actually wires — docs-implementation drift is a real signal.

### Two-document model (README + CLAUDE)

`README.md` (user-facing) plus a single `CLAUDE.md` (developer/contributor-facing — conventions, project structure, testing). No dedicated `ARCHITECTURE.md`; architecture content folded into `README.md`'s "Architecture" section (directory tree + protocol notes). Suits plugins where the architecture is small enough to live as one of README's sections.

### Dual-CLAUDE.md (developer + user-workspace)

A repo-root `CLAUDE.md` is developer-facing (architecture for the plugin author), and a `templates/CLAUDE.md` is deployed into the user's workspace by a setup skill (architecture for the user's project). Same filename, different audiences. The root file's opening warning ("don't confuse the two") is load-bearing — without it, an agent working on the plugin could easily edit the wrong one. A rename would make it structurally obvious but breaks the "deploy as `CLAUDE.md` into user workspace" workflow.

### CHANGELOG

Hybrid Keep-a-Changelog-ish format: header declares semver, entries are `## [X.Y.Z] — <date>` with narrative subsections (no strict `Added`/`Changed`/`Fixed` buckets). When automated release is absent, CHANGELOG headings may not be backed by git tags — versioned content without anchors.

### Documentation drift signals

Two specific drift shapes recur across the bin:

- **README/CLAUDE.md disagrees with the actual install script** about install location (`${CLAUDE_PLUGIN_DATA}/node_modules` vs `${CLAUDE_PLUGIN_ROOT}/<server>/node_modules`). The script is the source of truth; the doc was not updated when the install location moved
- **README cites `engines.node >= N`** but `package.json` declares `>= N+M`, or `engines.node >= 22` while CI tests on Node 20 — engines floors are sometimes aspirational and not gated

### Design-lineage attribution in README

README opens with "Inspired by <other-project>" linking to a precursor. Uncommon — most plugins do not attribute design lineage in user-facing docs.

### LICENSE absence vs declared license

`plugin.json` and README declare MIT but no `LICENSE` file is committed. GitHub's license detector returns null. Downstream consumers have no SPDX anchor; marketplace listings cannot show a license badge.

## Observability and telemetry pipelines

How plugins record session-level events for later analysis.

### Multi-hook recording pipeline → MCP server → read-only agent

A 4-hook recording pipeline (SessionStart, UserPromptSubmit, Stop, PostToolUse with selector and PostToolUse without matcher) feeds a single Python recorder that appends to a JSONL log, which is then flushed to a database (e.g., MongoDB) by a dedicated MCP server, which is then queried by a read-only agent constrained via `tools:` allowlist + `disallowedTools:` denylist. Five layers (hook → recorder → JSONL → MCP flush → agent) for workspace observability alone.

A coherent subsystem within a single plugin: every layer is plugin-shipped, every boundary is explicit, and the read-only agent is a first-class consumer. Distinct from generic hook usage; closer to "observability as a plugin product axis."

## Cost-gated MCP tool surfaces

How plugins constrain a paid or rate-limited tool's blast radius.

### Per-call rule gates plus pinned tool subset

A paid MCP integration is opt-in and rule-gated (e.g., `icp_score >= 7` or `priority: high/urgent`, always confirmation-gated, forbidden in specific stages of a workflow). The MCP server URL pins a narrow tool subset via query string (`?tools=docs,code_crafter/leads-finder,...`) so even a rule-bypass cannot reach the broader API surface. Rule enforcement is distributed across multiple agent prompts and a `templates/CLAUDE.md` that downstream sessions read; the plugin's root `CLAUDE.md` names the rule files as a coupled contract.

A defensive configuration move — pinning the tool subset at the URL is structural (cannot be widened by prompt drift), while the rule gates are normative (depend on agent compliance).

## Bounded autonomy / autoresume control

Plugin-level flow control for otherwise unbounded agent loops.

### Stop-hook with budgeted resume

A `Stop` hook decides whether to auto-relaunch an agent, capped by per-session resume count and time-since-last-resume. State persisted in a session JSON file (`resume_count`, `resume_at`). Three modes:

- `headless` — launches a new background `claude -p` process
- `prompt` — prints instructions to the user
- `off` — disables auto-resume

Plugin-level flow control distinct from in-agent loop bounds; the hook constrains the harness's session lifecycle directly.

## Session persistence layout

How a long-running plugin captures the state of a multi-cycle session.

### Three-file separation by consumer

Three files, each serving one consumer:

- A living-prose markdown document (e.g., `<tool>.md`) — human-facing and resume context for the agent
- An append-only JSONL log (e.g., `<tool>.jsonl`) — tooling consumption (dashboard, scoring, classification)
- A current-state JSON (e.g., `.<tool>.state`) — hook + statusline polling

Deliberate separation across format × access pattern. Each file's format matches its consumer's needs (markdown for narrative, JSONL for stream, JSON for poll).

## Explainable state machine surface

How the plugin exposes its internal state to the agent.

### CLI verb returning structured state explanation

A first-class CLI verb (e.g., `<tool> explain`) prints `Health / Mode / Failure / Action / Reason / Baseline / Best / Last / Streaks` from the persisted state plus a segment summary plus config. The agent is instructed to call it on resume and after any ambiguity. Makes the state machine introspectable by the agent itself, not just by the user.

## Verification artifact convention

Where evidence-of-correctness lives at the repo level.

### `verification/` directory of per-story proof documents

A dedicated `verification/` directory holds proof artifacts per story or feature. Not test code; a product artifact tracked in git. A novel answer to "how does an agent prove a feature works" sitting at the boundary of agent tooling.
