# Sample

Pass-1 Phase-1a partial for bin 7. Functional decomposition of `Lykhoyda--rn-dev-agent.md`, `NoelClay--academic-research-mcp-plugin.md`, `REPOZY--superpowers-optimized.md`, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How the plugin's identity and source binding are exposed to Claude Code's marketplace machinery — single-plugin repo vs. multi-plugin marketplace, where manifest files sit, and what wrapping object they use for metadata.

### Single-plugin marketplace at repo root with `source: "./"`

A `.claude-plugin/marketplace.json` sits next to `plugin.json` at repo root and carries one entry whose `source` is `./` — the plugin IS the repo. Metadata (description, owner, tags, keywords, category) is declared on the marketplace entry inline; some authors place a top-level `description` directly on the marketplace object, others wrap it under a `metadata.{}` object. `metadata.pluginRoot` is omitted because the plugin already lives at repo root. `$schema` may or may not be present — when absent, schema-aware editors lose autocomplete.

### Standalone repo without a marketplace

The repo ships only `.claude-plugin/plugin.json` with no `marketplace.json`. Installation is local-directory via `claude --plugin-dir <path>`. Equivalent to `source: "relative"` if someone re-packaged the repo into a marketplace later. Loses the marketplace surface entirely — no `source`, `strict`, `category`, or channel pinning to declare. Consumers must track commit SHAs themselves; "latest main" is the only pointer.

## Plugin discoverability metadata

How the plugin makes itself findable beyond raw repo identity — categorization, keywords, and tag dimensions surfaced for marketplace browsing. Distinct from manifest layout: this concerns the content of the metadata fields, not their location.

### Multi-dimensional (`category` + `keywords` + `tags`)

All three dimensions populated for a single plugin, giving overlapping facets for marketplace browsers. `keywords` is the long form (project-specific terminology, ~10 terms), `tags` shorter and ecosystem-oriented (`claude-code`, `cursor`, `codex`), `category` a single bucket. Increases discoverability surface area but also creates synchronization burden — three lists drift independently.

### Single-dimensional (keywords only)

Only `keywords` populated; no `category`, no `tags`. Minimal categorization — the plugin relies on its name and description to surface in search rather than facet-filtering. GitHub repo `topics` may also be empty, so external indexing also has nothing to grip.

### Cross-file category drift

`category` declared on both the marketplace entry and `plugin.json` with no automated sync — the two values drift (e.g. `"mobile-development"` on the marketplace entry vs. `"development"` on `plugin.json`). Unlike `version`, which is commonly guarded by sync scripts, `category` has no enforcement, so drift goes unnoticed.

## Version authority

Where the canonical version of the plugin lives and how copies stay in sync across the artifacts that need to declare it.

### Single-file authority (`plugin.json` only)

Version is declared once in `plugin.json`. Simplest invariant — no sync needed. Appropriate for plugins with no marketplace manifest, no sub-package, and no compiled artifacts. The cost is paid back when a second version source is added later.

### Two-file authority synced by script

`plugin.json` is authoritative; `marketplace.json` mirrors it. A `sync-versions.sh` script (run via pre-commit hook plus CI) compares the two and fails on drift. The script can also regex-scan source for hardcoded version literals (regression guard against re-introducing inline `version: "x.y.z"` strings the runtime is supposed to read from a manifest).

### Multi-runtime fan-out (single source compiled to N artifacts)

A single source file (`plugin.universal.yaml`) is declared the source of truth and compiled by an external tool into per-runtime manifests (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, plus the `hooks.json` family). Five-plus version copies in the tree at any time. The compiler is not vendored or pinned, so the compile step is a user-side build no CI verifies — observed drift in practice (universal yaml at one version while compiled artifacts have moved on).

### Independent semver streams (sub-package versioning)

Multiple semver tracks coexist in one repo: the plugin itself, and one or more sub-packages (Node MCP server with its own `package.json`, etc.). Each bumps independently with its own changelog discipline. CHANGELOG explicitly reconciles them ("MCP server bumped to X.Y.Z while plugin is at A.B.C"). Plugin-level sync scripts do NOT cover the sub-package — it's intentionally outside the synchronized set, with its own release cadence.

## Channel distribution

How users pin to a specific revision of the plugin — release-branch splits, tag handling, or a self-update mechanism baked into the plugin itself.

### Single-channel tag-on-main

No release branch, no stable/latest split — `main` IS the release branch. Tags live on main commits. Users pin via `@<marketplace-name>` in the install command; the marketplace pulls from main HEAD whatever was last published. Acceptable for low-cadence plugins; on high-cadence repos, on-main bumps can ship through the marketplace without producing a tag, leading to "tag count << version count" gaps.

### No pinning surface

No tags, no release branches, no marketplace channel — the only pointer is whatever main HEAD happens to be at clone time. Any consumer has to track commit SHAs out-of-band. Common in early-stage / never-released repos.

### SessionStart self-update

A SessionStart hook performs `git fetch` + `git merge --ff-only origin/main` against the plugin's own clone, with a 24 h cache and an opt-out env var. Two install modes handled by one hook: when the plugin is a git clone (Codex / OpenCode / self-hosted), the hook auto-updates; when installed via a marketplace (Claude / Cursor), the hook instead emits a "run `/plugin update`" notice. Effectively turns SessionStart into a soft auto-update channel for non-marketplace installs.

## Plugin component registration

How the plugin tells Claude Code (and sibling runtimes) where its skills, commands, agents, and hooks live — explicit path arrays vs. convention-based discovery.

### Default discovery (convention-based)

`plugin.json` carries identity/metadata only; component locations are implicit per Claude Code's directory conventions (`skills/`, `agents/`, `commands/`, `hooks/hooks.json`, `.mcp.json` at repo root). Lowest manifest-side ceremony. Fails when the plugin must satisfy a runtime that requires explicit paths (Codex, Cursor) — those runtimes need a sibling `plugin.json` with explicit `skills` and `agents` keys, so single-runtime convention discovery does not generalize.

### Explicit path arrays in plugin.json

`plugin.json` declares each component category by path (`skills`, `agents`, `commands`, `hooks` arrays; `mcpServers` as an inline object). Higher manifest cost but every component location is grep-able from one file, and the plugin can reference targets outside the default directories. MCP servers can be inlined in `plugin.json.mcpServers` rather than externalized to a `.mcp.json`.

### Mixed convention per runtime (per-runtime manifests)

Repo hosts multiple `*-plugin/` directories (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`) — each with its own `plugin.json`. Claude relies on directory convention; Codex and Cursor's manifests explicitly set `"skills": "./skills/"` (and Cursor adds `"agents": "./agents/"`) because those runtimes require explicit paths. The single source of truth (universal YAML) compiles to all three.

## Agent declaration conventions

Frontmatter fields on agent files — what gets declared, how tool permissions are scoped, and what runtime knobs are exposed.

### Rich frontmatter with embedded examples

Agents declare `name`, `description` (multi-paragraph YAML literal block with `<example>` / `<commentary>` XML blocks and "Triggers:" keyword lists), `tools` (per-agent comma-separated tool list), `model` (`sonnet` / `opus`), plus optional knobs — `effort: high` (reasoning budget), `memory: true` (cross-session memory enabled), `color`, and `skills` (in-plugin skills referenced by bare name). Description content drives the agent matcher; examples function as trigger-rich few-shot prompts at metadata level.

### Minimal frontmatter, parent-session permissions

Agents declare only `name`, `description`, `model: inherit`, and (optionally) `memory: user`. No `tools` allow-list — the agent inherits the parent session's permissions. Smaller frontmatter surface; pushes permission decisions out to the user-level Claude Code config rather than scoping per-agent.

### Worktree-isolated agent with hard turn cap

Agent frontmatter declares `isolation: worktree` plus `maxTurns: <N>`. The agent runs in a git-worktree isolation envelope (presumes the invoking session's project is a git repo) and is hard-capped at N turns. Constrains other parts: tools list mixes fully-qualified MCP names with built-in tools; the hard turn cap means long-running research can truncate mid-flow with no documented recovery.

### Bare-name in-plugin skill references

Agents reference skills by bare name (`skills: rn-testing, rn-best-practices`) rather than the qualified `plugin:skill` form. Correct for skills in the same plugin; future cross-plugin reuse would need qualification. Same field shape as agents declaring tools, but distinct semantics — references resolved against the local skill directory.

## Tool permission syntax inside agents

How the agent restricts which tools (especially MCP tools) it can call.

### Plain tool-name list

Comma-separated tool names — `Bash, Read, Write, Edit, Glob, Grep`. No permission-rule syntax (`Bash(uv run *)`-style). Simplest form; cannot scope `Bash` to specific commands at the frontmatter layer.

### Fully-qualified MCP tool names

Each MCP tool listed by full name (`mcp__academic-search__search_papers`) rather than wildcard. Tighter scoping than `mcp__academic-search__*` but high maintenance — adding a tool to the server requires updating each agent's allow-list. Compare with `allowed-tools` on commands, which often use the wildcard form even when the agent in the same plugin uses fully-qualified names — two conventions for the same kind of access scoping.

## Dependency installation

How runtime dependencies (Python packages, Node modules, system binaries) are installed when the plugin needs them, including where they live, how change is detected, and how failure is signaled.

### Zero dependencies

The plugin deliberately ships no runtime dependencies — hooks are capped at Node built-ins (`fs`, `path`, `crypto`, `child_process`). No `requirements.txt`, no `pyproject.toml`, no `package.json` at the plugin root. Install step disappears entirely. The constraint shapes everything downstream: hooks cannot use NPM ecosystem libraries, and any future dep would force the architecture to grow an install path. Trade-off is hand-rolled equivalents of common functionality (parsing, compression, etc.) inside the hook source.

### SessionStart-driven dual-runtime install (Python venv + Node modules)

A single SessionStart shell hook handles both Python venv + `pip install -r requirements.txt` and Node `npm install` in the same script. Each manager is guarded by `diff -q` between the source manifest in `$CLAUDE_PLUGIN_ROOT` and a cached copy in `$CLAUDE_PLUGIN_DATA`. On `diff` miss, install runs and cache is refreshed; on install failure, the cached copy is `rm -f`'d so next session retries. Symmetric retry semantics across both ecosystems in one script. Distinct from per-manager hooks: one hook fans out to N managers with identical diff/retry shape.

Refinements: `diff -q` is sensitive to source-vs-cache equality only — a flaky-network install that returns 0 but partially lands packages will leave an "in sync" cache that does not retry. `2>/dev/null` suppression on the install branches keeps stderr quiet to avoid corrupting the JSON channel the same hook uses for context injection, but loses corrective error messages. `python3 -m venv ... 2>/dev/null || true` makes venv-creation failure invisible — a user without `python3-venv` installed gets a silent no-op then a confusing "pip not found" downstream.

### Version-stamped persistent install with back-symlink

`node_modules` (or equivalent) installs into a stable location under `$CLAUDE_PLUGIN_DATA` (e.g. `$CLAUDE_PLUGIN_DATA/cdp-node_modules/node_modules/`) and a `ln -sfn` symlink back into `$CLAUDE_PLUGIN_ROOT/<expected-path>/node_modules` so relative `require` resolves. Solves two problems at once: the plugin cache is wiped on every Claude Code update (so installs into ROOT do not survive), and the runtime still expects modules at the in-tree path. A version stamp file (`$CLAUDE_PLUGIN_DATA/<dir>/.version-stamp` containing the sub-package's `package.json` version) is the change-detection key — reinstall triggers when stamp absent OR mismatched. Pre-scans for a dangling symlink from a previous persistent install and cleans it before falling back to a local install. Includes a stamp-flip-flop guard: skip persistent path when the runtime is unavailable (e.g. `node` missing), so an "unknown" version cannot be written.

### External CLI auto-install via vendor scripts and global package managers

System-level CLIs (e.g. `agent-device`, `maestro-runner`, `ffmpeg`) are installed during SessionStart by a family of `ensure-*.sh` scripts, each targeting one tool with its preferred install mechanism — `npm install -g` for npm globals, `curl -fsSL <url> | bash` (vendor install scripts) for standalone binaries, with `brew install` printed as a manual fallback when auto-install fails. Some scripts use `set -euo pipefail` for strict failure; others omit it to allow graceful fallback to local install. Lands tools wherever the installer puts them (`~/.maestro-runner/bin/`, npm global prefix), outside the plugin's own data directory.

### Failure-signaling spectrum

Install failure can be signaled three ways: (1) **silent** — `2>/dev/null` + `|| rm -f` cache marker; the only feedback is a downstream import error at tool-invocation time; (2) **stderr with corrective command** — `WARNING: <component> deps failed. Run: cd <path> && npm install`, printed before the session banner so users see it; (3) **stamp-mismatch retry** — no stderr, but the stamp file is the durable signal; next session re-detects mismatch and retries. The choice constrains UX: silent fails disappear into runtime errors; stderr+corrective preserves the install attempt's exit code 0 (non-blocking) while still informing.

### Plugin-upgrade awareness via tmp-file stamp

A separate stamp at `$TMPDIR/<plugin>-last-version` records the plugin's own version, compared next session to detect plugin-level upgrades (vs. dep-level). On mismatch, emits a notice ("plugin upgraded from vX to vY; restart Claude Code to reinitialize MCP servers") to surface the MCP-subprocess-doesn't-auto-restart class of bug. `$TMPDIR` resets on macOS reboot, so the stamp survives a boot cycle but not a restart — accepted trade-off.

## Bin-wrapped CLI distribution

Whether and how the plugin exposes user-invokable command-line entry points, including OS portability concerns.

### No bin layer (direct invocation)

The plugin exposes no user-facing CLI. Internal entry points are invoked by full path (e.g. `node ${CLAUDE_PLUGIN_ROOT}/src/parsers/pdf-parser.js`) from commands or hooks rather than via a `bin/` wrapper. MCP servers resolve via `.mcp.json`'s explicit `command:` path. Lowest portability burden, but no shell-discoverable entry points.

### Git-symlink bin wrappers (mode 120000)

`bin/<friendly-name>` files are committed as git symlinks (mode 120000) pointing to `../scripts/<real-name>.sh`. Provides user-friendly naming at the bin layer without duplicating script content; target scripts use `dirname "$0"`-based resolution which transparently resolves through the symlink to the real-file plugin root. Constraint: Windows-native git checkouts convert symlinks to plain text files containing the target path unless `core.symlinks=true` — silently breaks on Windows. Also depends on the target file having the executable bit set; one missing exec bit makes the bin entry broken-by-default for strict-perm consumers.

### Polyglot CMD/bash wrapper for cross-platform hook invocation

A single file (`run-hook.cmd`) interpreted differently by `cmd.exe` (Windows batch syntax) and by `bash` (via `: << 'CMDBLOCK' … CMDBLOCK` heredoc trick). Searches `C:\Program Files\Git\bin\bash.exe` and `C:\Program Files (x86)\Git\bin\bash.exe`, then `bash` on PATH; silently succeeds if none found. Hook script filenames are deliberately extensionless (`session-start`, not `session-start.sh`) to avoid Claude Code's Windows auto-detection prepending `bash` to any `.sh` command. Used internally by SessionStart, not as a user-facing CLI — but solves the same cross-platform invocation problem `bin/` would face.

## User configuration declaration

How user-supplied configuration (API keys, preferences) is declared in the manifest and consumed at runtime.

### `userConfig` with `${user_config.KEY}` substitution

`plugin.json` declares fields under `userConfig` with `description`, `sensitive: true|false`, optional `type`, `default`, etc. `.mcp.json`'s `env` block uses `${user_config.KEY}` substitution to translate user config into `CLAUDE_PLUGIN_OPTION_<KEY>` env vars consumed by the MCP server via `os.environ.get(...)`. Round-trip is observable: Claude Code prompts for the values at install time, stores them, substitutes into the env block, server reads them. `sensitive: true` flags genuine secrets (API keys); `sensitive: false` correctly applied to identifiers that are public rate-limit handles (e.g. an Unpaywall email).

### `userConfig` without explicit substitution

`userConfig` declared but no `${user_config.KEY}` references appear in the manifest. Claude Code translates user config into env vars implicitly for MCP subprocesses. Works in practice (the implicit translation is part of the plugin protocol) but a consumer expecting explicit substitution will be surprised.

### Env-var + INI-config knob pattern

No `userConfig` at all. Configuration knobs are read directly by the hooks from environment variables (`SP_NO_COMPRESS=1`, `SUPERPOWERS_AUTO_UPDATE=0|1`) and from a user-side INI file (`~/.config/superpowers/update.conf` parsed by awk). The knob surface is documented only in the README and hook source — schema-aware tooling cannot discover it. Constraint: no install-time prompt for values; users must know which env vars exist before setting them.

### Schema richness — minimal vs. validated

When `userConfig` IS declared, the schema is typically thin — `description` and (sometimes) `sensitive` only, no `type`, `default`, enum, or validation pattern. Validation is deferred to runtime: the server raises a runtime error at first tool invocation when a required field is unset (`if not email: raise ValueError(...)`). A user who skips the prompt gets a deep runtime error rather than an install-time failure. No validation that the configured value matches its semantic shape (an email field accepts any non-empty string).

## Tool-use enforcement (hooks)

What PreToolUse / PostToolUse / SubagentStart / CwdChanged / PostToolUseFailure hooks the plugin registers, and the failure posture they take.

### No enforcement (persona-only behavior shaping)

The plugin registers no PreToolUse / PostToolUse hooks. Behavior is shaped entirely through SessionStart persona injection plus skill / command instructions. No runtime gate on what tools the agent can call — relies on the model to follow the instructions. Lowest hook-maintenance burden; loses the ability to block wrong tool calls deterministically.

### Multi-pattern PreToolUse safety stack

Multiple PreToolUse hooks all matching `Bash` (or `Read|Edit|Write|Bash`) run sequentially on every matching tool call. Examples: a destructive-command blocker (~30+ patterns, 3-tier severity), a secret-protector (~50+ file patterns + ~14 content patterns for hardcoded keys / tokens / PEM / connection strings), and a Bash-output compressor that rewrites noisy commands through an optimizer (with a never-compress allow-list for diffs / reads / failed commands). Latency compounds — each Bash call passes through every matching hook before execution. Documented fail-open posture for non-safety hooks (errors result in original command running unmodified); safety hooks presumed fail-closed on pattern match, fail-open on unexpected errors.

### Post-edit health-check (PostToolUse on `Edit|MultiEdit|Write`)

A PostToolUse hook on edit / write tools runs a domain-specific check (e.g. simulator compilation / crash check via CDP) with a short timeout. Last-write-wins debounce — only the most recent edit triggers the check. Silent-skip when prerequisite state is missing (no active session, file-type mismatch, target is a test or config file). Output is plain stdout text the agent reads, not structured JSON; documented exit-code convention (0 = success, 1 = error logged non-blocking, 2 = block operation explicitly NOT used).

### `PostToolUseFailure` post-hoc diagnostic hook

A hook fires on failures of MCP tools matching a namespace (`mcp__*<plugin>*`) and emits a tailored diagnostic ("CDP session is not active. Metro is not running on port X. Try: cdp_status to reconnect.") that the agent reads as plain stdout. Effectively a "here's why your MCP call just failed" surface — rare in the ecosystem; most plugins use PreToolUse for validation rather than post-hoc explanation. The hook inspects multiple environment / process states (active flag, port availability, simulator boot state, adb device presence) to compose the diagnostic.

### `SubagentStart` context injection

A SubagentStart hook injects connection / state info ("CDP bridge is connected (platform: X, port: Y)") into every subagent spawn so the subagent does not need to re-probe. Paired with frontmatter "PARENT-SESSION-ONLY" warnings on agents that cannot run under Task-tool spawning (because MCP stdio doesn't propagate to subprocesses). Documents an MCP-inheritance gotcha at the hook layer.

### `CwdChanged` re-detection hook

Re-runs project-type detection when the user `cd`s to a new directory; emits a warning ("tools may not work here") when the new cwd doesn't satisfy plugin prerequisites. Rare across the ecosystem — most plugins do not react to cwd changes.

### PostToolUse skill telemetry / edit tracking

A PostToolUse on `Skill` records skill-invocation telemetry. A PostToolUse on `Edit|Write` logs file changes (drives TDD reminders downstream) and auto-appends working-state files (project-map.md, session-log.md, state.md) to `.gitignore` on first write. Keeps the plugin's working-state files out of git automatically — consumer never has to remember to add them.

## Session context loading

How the plugin gets domain context, persona, or routing instructions into the model at session start.

### `hookSpecificOutput.additionalContext` JSON via SessionStart

A SessionStart hook prints a JSON object on stdout with `hookSpecificOutput.hookEventName: "SessionStart"` and `additionalContext: "<long persona / routing / instructions string>"`. The string is heredoc-embedded in the shell script. Effectively turns SessionStart into a context-injection channel without modifying any system prompt.

### Plain-stdout context banner

SessionStart emits a large heredoc banner (40+ lines of prose) listing tool inventory, prerequisites, and version warnings via plain `echo` rather than structured JSON. Re-injected on every sub-event (`startup`, `clear`, `compact`) when no matcher restricts firing — significant context tax on long sessions. Hard-coded counts in the banner ("plugin is active with 51 MCP tools") drift from other hard-coded counts elsewhere (README "53 MCP tools"; source `grep -c "trackedTool("`).

### SessionStart sub-event matcher (`startup|clear|compact`)

The expensive synchronous SessionStart hook is scoped to `startup|clear|compact` and excludes `resume` (where routing is already in context). A second unscoped SessionStart entry runs the cheap async context-engine on every sub-event including `resume`. Pattern reduces wasted re-injection while preserving cheap state work. Codex equivalent uses `startup|resume` because Codex lacks the `clear`/`compact` sub-events.

### `UserPromptSubmit` skill-activator with confidence threshold

A UserPromptSubmit hook emits `hookSpecificOutput.additionalContext` with skill hints + memory recall (from a `session-log.md` style file) when a confidence threshold is met. Different trigger from SessionStart: fires per-prompt, can scope context to the current question. Sister hook to the SessionStart pair — three different context channels feeding the model.

### Persona duplication between hook and skill

The persona text injected by SessionStart is also embedded in the skill's `SKILL.md`. Two copies diverge on edit — single-source-of-truth violation. Caused by fusing dep-install and persona-injection in the same SessionStart hook; refactoring would require splitting.

### Release-notes-as-context

After a successful self-update, the SessionStart hook extracts the current release's "What's New" section from `RELEASE-NOTES.md` (a 100+ KB file) and injects it as `additionalContext`. Self-announcing upgrade pattern. Constraint: section-selection logic must be precise; an off-by-one would flood the prompt with the entire 100 KB file.

## Live monitoring

Whether the plugin uses the `monitors.json` component type for passive observation.

### No monitors

None of the sampled plugins use `monitors.json`. Equivalent functionality is delivered via hooks (PostToolUse + Stop + SubagentStop combinations) plus runtime MCP tool calls (e.g. `cdp_status`). Author awareness varies — at least one plugin has real-time diagnostic needs that a `monitors.json` could surface; the hook-based equivalent works but is not equivalent to a declarative monitor.

## Plugin-to-plugin dependencies

Whether the plugin declares dependencies on other plugins.

### No cross-plugin dependencies

None of the sampled plugins declare a `dependencies` field. Each is a self-contained monolith. Plugin-prefixed tag formats (`{plugin-name}--v{version}`) accordingly do not apply — single-plugin marketplaces use plain `vX.Y.Z` tags.

## Testing and CI

What test framework runs against the plugin and what CI infrastructure (if any) exercises it.

### No tests, no CI

No test directory, no test files, no CI workflow. The most recent commit message may reference "code review issues" implying manual review, but nothing automates continued correctness. Common in early / single-author plugins where the author tests by manual installation.

### Bash scripts under `tests/<platform>/` with no CI

Tests live as bash scripts under `tests/claude-code/`, `tests/codex/`, `tests/opencode/`, etc., plus standalone Python analyzers. Run manually by the maintainer; no GitHub Actions exercise them. Multi-platform layout signals testing intent without CI investment. Quality gap is visible — version sprawl across multiple files plus a YAML source-of-truth shows drift in practice (compiled artifacts at one version, source at an older version) that CI would catch immediately.

### Node `node:test` with multi-job CI

`node --test 'test/unit/*.test.js'` runs hundreds of tests against the in-plugin Node MCP server (located under a sub-path like `scripts/<server>/test/`, not repo root). CI runs three parallel jobs: TypeScript build, unit tests, and a separate `version-sync` job comparing manifest copies. No matrix — single Node version, single OS. Action versions pinned by tag (`@v4`), not SHA. Caching via setup-node's built-in npm cache with explicit `cache-dependency-path` to the sub-package's lockfile. CI does NOT run on tag push — release creation is fully manual. Integration tests are a thin slice of the test count; full E2E (simulator-driven) runs on the maintainer's dev box, not in CI.

## Release automation

How tags become releases and how release notes flow to users.

### Manual release creation, no workflow

Release creation is `gh release create` (manual) or the GitHub Releases UI. Notes are hand-composed; CHANGELOG.md is updated in the same commit cycle. No tag-sanity gate — no enforcement that tag format matches `v*` or that the tagged version equals `plugin.json.version`. Tag count substantially less than version count when high-cadence on-main bumps ship through the marketplace without a corresponding tag.

### CHANGELOG with non-Keep-a-Changelog custom sections

CHANGELOG.md follows the Keep a Changelog base format (`## [X.Y.Z] — date`, `### Added`, `### Fixed`) but adds custom sections (`### Verified-stale`, `### Multi-review`, `### Benchmarks validated live`, `### Backlog state`). Entries reference internal ticket IDs and external issue numbers. Hand-maintained — release notes on GitHub Releases manually duplicate a subset of CHANGELOG prose. A `release-please`-style auto-generator wouldn't handle the custom sections; the format trades automation for richness.

### `RELEASE-NOTES.md` consumed by SessionStart hook

A free-form `RELEASE-NOTES.md` (100+ KB) replaces a conventional CHANGELOG. The session-start hook reads it on update to extract the current release's "What's New" section and inject inline as context. Inline release-notes-as-context pattern — see Session context loading > Release-notes-as-context for the consumption side.

## Marketplace validation

What schema / structural validation runs against the manifests in CI.

### No validation

`plugin.json` and `marketplace.json` are structurally hand-validated only. No JSON Schema validation step. The `$schema` reference (when present) points at the canonical Anthropic schema URL but no build step fetches or validates against it. Frontmatter on agents / skills / commands is unvalidated. Hooks.json correctness is implicit (pre-commit version-sync; CI re-runs it; hook scripts get the executable bit checked by git).

### Script-based source linting (regression guard)

A maintainer-authored script (e.g. `sync-versions.sh`) regex-scans source files for forbidden patterns (hardcoded version literals, etc.) as a regression guard. Not full schema validation — targets specific known-bad patterns. Runs in pre-commit and CI for cross-checking.

## Documentation

What human-readable docs ship with the plugin and where they live.

### Single root `README.md` plus `LICENSE`

Standard minimum: a README at repo root covering install / setup / usage, plus a LICENSE file (typically MIT). Substantial READMEs include benchmarks, troubleshooting, security sections; thin READMEs cover only install + usage. Community health files (SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md) are typically absent — security guidance lives as a `## Security` section in README instead.

### Marketing-grade README (40+ KB)

README doubles as marketing and technical reference. Sections include research motivation, third-party testimonials, shields.io badges (stars, version, license, install CTA), full skill catalog, hook inventory. Drives the file past 40 KB. Trade-off: discoverability and credibility benefit; maintenance cost grows; some sections (e.g. third-party LLM quotes) are unusual for a plugin README.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` (replaced by `RELEASE-NOTES.md` or absent entirely) and no `ARCHITECTURE.md` at repo root. Architecture content lives in a `docs/architecture/` directory or in a separate Astro Starlight docs site published to GitHub Pages. Constraint: a reader looking at repo root for the standard three-document set (README / ARCHITECTURE / CLAUDE) finds only README.

### Astro Starlight docs site with auto-generated MDX

A `docs-site/` directory ships a full Astro Starlight site, with generator scripts (`docs-site/scripts/generate-bp-docs.mjs`, `generate-tool-docs.mjs`) that auto-generate MDX from in-plugin sources (best-practice rules in `skills/<skill>/references/*.md`; MCP tool registrations). Published to GitHub Pages via a separate `deploy-docs.yml` workflow with path filters. The docs site is a first-class user-facing artifact in the same repo as the plugin code — secondary build pipeline driven by the same source.

### CLAUDE.md template shipped for consumer projects

A `CLAUDE-MD-TEMPLATE.md` file ships at repo root, intended to be copied into the consumer's own project (not the plugin's own CLAUDE.md). Turns the plugin into a shipped convention: "add this to YOUR project's CLAUDE.md to tell Claude how to use us." Distinct from the plugin's own CLAUDE.md (when present) which documents the plugin's internal development.

### License-declared-but-no-LICENSE-file

README and `package.json` declare MIT, but no `LICENSE` file in the tree. GitHub's license detector returns null. Legal reuse ambiguous — automated tooling (Sourcegraph, GitHub repo card) cannot confirm the license. Common in early single-author plugins.

## Multi-runtime portability

How the plugin supports parallel runtimes (Claude Code + Cursor + Codex + OpenCode) from one repo.

### Per-runtime manifest directories

Repo hosts `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/` top-level directories, each with its own `plugin.json` (or runtime-specific equivalent). Hooks are duplicated across runtimes with naming-convention differences: Claude `hooks.json` uses PascalCase event names (`SessionStart`, `PreToolUse`); Cursor `hooks-cursor.json` uses camelCase (`sessionStart`, `preToolUse`); Codex bash launchers inline a multi-location plugin-root discovery routine because Codex lacks a `${PLUGIN_ROOT}` env var. Same source, different syntax — drives the need for a single-source-of-truth compiler upstream.

### Polyglot wrapper for cross-OS hook invocation

See Bin-wrapped CLI distribution > Polyglot CMD/bash wrapper. The wrapper itself is a portability mechanism — one file invoked by both Windows `cmd.exe` and POSIX `bash` to dispatch hooks consistently across OSes.

### POSIX-only with no Windows story

Plugin ships only nix-style paths (`venv/bin/python`, `#!/usr/bin/env bash`). No Windows path branch, no `.cmd`/`.ps1` pair. Acceptable when the plugin's target domain is itself POSIX-only (e.g. iOS / Android simulator tooling). Loud failure mode on Windows: `.mcp.json` referencing `venv/bin/python` won't resolve at all. README typically declares minimum runtime versions but not OS support.

## Cross-session memory

How the plugin persists state between sessions for the model to pick back up.

### File-based memory stack with auto-gitignore

A small set of working-state files at the project root capture cross-session state: a JSON snapshot (auto-managed, e.g. git blast radius), a structure-cache markdown file, a decision-history log, a task-snapshot file, and an error→solution map. The stack is auto-appended to `.gitignore` on first write by a PostToolUse hook so it never gets committed by accident. Read by SessionStart / UserPromptSubmit hooks to re-hydrate context. Distinct from `memory: user|true` agent frontmatter, which signals model-side memory rather than file-based state.

### Skill-side experience seeds with stateful HOME directory

Seed YAML files (e.g. `seed-experience/common-failures.yaml`, `expo-gotchas.yaml`, `platform-quirks.yaml`, `recovery-playbook.yaml`) ship with the plugin and are initialized into `$HOME/.claude/<plugin>/` by a SessionStart `ensure-*.sh` script — establishing telemetry and candidates directories plus a scratchpad markdown file. Combines plugin-shipped seed data with user-side mutable state outside the plugin's data directory.
