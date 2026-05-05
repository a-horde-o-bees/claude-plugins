# Sample

Pass-1 Phase-1a partial for bin 16. Functional decomposition of `marioGusmao/mg-plugins`, `mdproctor/cc-praxis`, and `raphaelchristi/harness-evolver`, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How the repo presents its plugin catalog to Claude Code's marketplace machinery — single root `.claude-plugin/marketplace.json` is the constant; what differs is how it's structured and how authoritatively it speaks for plugin metadata.

### Top-level minimal record

Marketplace is a flat object with `name`, `description`, `owner`, and `plugins[]` — no `metadata` wrapper, no `metadata.pluginRoot`, no `$schema`. Each plugin entry carries the minimum the consumer UI needs (name, source, description, version, sometimes keywords/category). Appropriate when the marketplace is just a directory of relative-source plugins with no shared root or pre-release surface — there is nothing for `metadata` to hold. Implies plugin-level `plugin.json` carries the authoritative metadata for relative sources.

### Wrapped via metadata object

Marketplace uses a `metadata.description` (and potentially `metadata.version`, `metadata.pluginRoot`) wrapper for catalog-level fields, while `plugins[]` carries per-plugin records. Used here in single-plugin marketplaces where the plugin itself sits at repo root (`source: "./"`) — the metadata wrapper carries catalog identity separately from the plugin entry to avoid confusion between marketplace identity and plugin identity. Constrains nothing technically, but signals an authoring convention (catalog-as-document vs. catalog-as-list).

### Custom top-level extension fields

Repo adds non-standard top-level fields to the marketplace manifest that Claude Code presumably ignores. The `bundles` field groups plugins into named user-facing collections (`quick-start-java`, `core`, etc.) with display metadata; consumed only by the repo's own out-of-band installers (`scripts/claude-skill`, `scripts/web_installer.py`), not by `/plugin install`. Appropriate when the schema lacks a primitive the author needs (here: plugin grouping for UI presentation) and the author is willing to ship their own consumer to read the extension. Constrains: users on the built-in CLI cannot access the grouping; the extension is invisible to anyone not running the custom installer.

## Plugin source binding

How `marketplace.json` entries reference their plugin manifests, and which side wins when metadata duplicates.

### Relative source, plugin.json authoritative

Every entry uses `source: "./<plugin-dir>"` (or `"./"` for single-plugin); `strict` field is implicit-true (omitted). For relative sources the docs say `plugin.json` wins on version; marketplace entry is the discovery surface. Appropriate for monorepo marketplaces where plugins live in-tree. Constrains: any per-entry duplication of `plugin.json` fields (description, version, keywords) is lossy — both sides must be kept in sync manually or one is silently shadowed.

### Parallel duplicated metadata across multiple manifests

The same plugin's `version` is carried independently in `marketplace.json`, `plugin.json`, and (for Node plugins) `package.json` — three separate copy-paste sites for the same string. Drift surfaces in characteristic shapes: `package.json` years behind `plugin.json` (npm metadata not kept in sync during upstream release), `marketplace.json` behind `plugin.json` (release skill bumps plugin manifest but not marketplace entry across multiple releases), or per-plugin `plugin.json` lagging marketplace's projection (incomplete batch promotion like "drop SNAPSHOT — all 49 skills promoted to 1.0.0" missing some files). Constrains downstream consumers: `/plugin install` reads `plugin.json` for relative sources, marketplace UIs show `marketplace.json`, and custom installers (web-installer scripts) often read whichever the script author parsed first — different consumers, different answers, same field name. The pattern is the failure mode, not the choice.

## Per-plugin discoverability metadata

What the marketplace entry tells search/listing UIs about each plugin beyond name and source.

### Keywords + category

Each plugin entry carries a `keywords` array (typically 5-7 strings) and a `category` string (commonly `"development"`). Provides search/filter surface for marketplace UIs. Appropriate when the marketplace expects browsing or search; constrains nothing on the plugin runtime. Inconsistency within a single marketplace is observed — one plugin shipping `keywords: []` while siblings carry full lists hurts discoverability for that plugin specifically.

### Minimal entry only

Each plugin object is just `{name, source, description, version}` with no `category`, `tags`, or `keywords`. Acceptable when plugin names + descriptions are themselves the discovery surface and the marketplace is small enough to scan; constrains marketplace UIs that filter by category to show every plugin under a generic bucket.

## Channel and pinning model

How users target a specific version of the marketplace or its plugins.

### HEAD-tracking single branch

No channel split, no release branches, no tags. Single `main` branch; `/plugin install` against the marketplace effectively pins to whatever commit the user added at. Appropriate for solo aggregator repos where every commit is "chore: sync upstream-vX". Constrains: no reproducible install target beyond commit SHA; consumers cannot opt out of a breaking upstream change without pinning the marketplace to a specific commit and manually re-adding to update.

### Tag-pinned with trunk-based releases

Annotated tags on main (e.g., `v1.0.0`, `v1.0.1`, `v1.1.0` with corresponding GitHub releases). Users pin via `/plugin marketplace add ...@vX.Y.Z`. Appropriate for stable-release discipline without channel separation; constrains contributors to a tag-on-main workflow with no in-flight `release/*` branches.

### Multi-channel via parallel distribution paths

The plugin is published to more than one delivery surface (marketplace + npm `npx <plugin>@latest` + direct GitHub install) without a unified pinning story. Each channel carries its own version semantics (marketplace uses git refs, npm uses standard semver tags). Appropriate when the plugin needs to support runtimes outside Claude Code (Cursor/Codex/Windsurf via npm). Constrains: consumers and channels can diverge between tags; an unreleased commit on main may already be visible to marketplace consumers while npm consumers still see the last published version.

### Pre-release suffix as channel marker

Maven-style `1.0.0-SNAPSHOT` suffix in `plugin.json` versions during development; stripped at release. Custom version comparator in the repo's installer treats SNAPSHOT as strictly older than the bare release. Not a SemVer pre-release identifier (`-rc`, `-beta`) and not recognized by Claude Code's plugin machinery. Appropriate when the author is borrowing conventions from a host-language ecosystem (here Java/Quarkus). Constrains: any consumer not running the custom installer treats `1.0.0-SNAPSHOT` and `1.0.0` as different opaque strings — naive ordering breaks.

## Release automation

How a tag-and-publish event is triggered and what it actually does.

### Manual ad-hoc

No automation. Releases are produced by editing `plugin.json`, committing, tagging annotated, pushing tags, and creating GitHub releases via UI or `gh release create` by hand. Appropriate for solo authors with low release frequency; constrains discipline to memory — no enforcement that the tag is on main, no version-conformance check, no protection against tagging a detached HEAD.

### Skill-driven release

A project-local skill (e.g., `/dev:release` under `.claude/skills/dev-release/`) bumps versions in known manifest files, generates a `CHANGELOG.md` entry from conventional-commit-prefixed log output (`feat:`, `fix:`, `refactor:`), creates an annotated tag, runs `gh release create`, and runs `npm publish` for multi-channel plugins. Appropriate when the author wants release automation but lives entirely in-editor; constrains: the skill must be kept in sync with all version-bearing files, and any file not in its bump set silently drifts (most commonly the marketplace entry's duplicated version field).

### Upstream-aggregator chore-sync

Every commit is `chore: sync <plugin-list>` produced by an upstream pipeline outside the marketplace repo. Versions bump in the upstream plugin repos, and the aggregator imports the bumped artifacts via batched commits. Appropriate when the marketplace is a fan-in aggregator from independently-released plugin repos; constrains the aggregator to having no independent release identity — its own "version" is just the commit SHA of the latest sync.

## Tag strategy

Where tags live and what they label.

### Tags on main

Tags applied directly to commits on the default branch. All recent tags resolve to main commits; feature branches merge in before tagging. Convention-only enforcement (no workflow gate). Appropriate for trunk-based development with low ceremony.

### No tags

Repo has zero tags; `gh api tags` returns empty. Releases are implicit (commit to main = release). Appropriate when the repo is a pure aggregator and the upstream repos hold the real release identity. Constrains: no reproducible install target.

### Per-plugin tag prefix

Tag format `{plugin-name}--v{version}` for marketplaces aggregating independently-versioned plugins. Not observed in this bin (zero tags or whole-repo tags); noted as a non-occurrence — when multiple plugins share a marketplace they tag the whole marketplace as one unit, not per-plugin.

## Plugin-component registration

How a plugin's `plugin.json` declares (or implies) the location of skills, agents, hooks, MCP configs, and other component artifacts.

### Implicit auto-discovery

`plugin.json` carries only top-level metadata (`name`, `description`, `version`, …) and omits all component fields. Claude Code default-discovery rules pick up `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json` from convention paths. Appropriate when the plugin follows standard layout and gains nothing from explicit declaration. Constrains: the plugin's surface is invisible without filesystem inspection — readers (and the agent itself) must assume conventions hold.

### Directory-pointer mixed with file-pointer

`plugin.json` mixes directory pointers (`"skills": "./skills/"`) with file pointers (`"mcpServers": "./mcp/mcp.json"`) and explicit arrays (`"agents": [".../foo.md", …]`) in the same manifest, often with the mixture varying plugin-to-plugin within one marketplace. Appropriate when some component locations are conventional and others are non-default. Constrains: inconsistency within a marketplace makes it harder for tooling to predict where to look — each plugin must be re-inspected.

### Custom sidecar manifest

Each plugin ships a non-standard `.claude-plugin/capabilities.json` alongside `plugin.json` carrying `{plugin, version, schema_version, capabilities[]}` with per-capability `id, name, type, applicable_phases, guidance, anti_patterns, priority`. Not in the official spec; consumed by the marketplace's own router/selector layer that picks which capability to invoke based on phase + priority. Capability versions drift independently from `plugin.json.version` (different bump pipeline). Appropriate when a marketplace ships its own routing/selection mechanism; constrains: the sidecar is meaningless to vanilla Claude Code clients and must be parsed by a co-shipped consumer.

## Plugin-component placement

Where component directories physically live relative to plugin boundaries.

### Inside plugin directory

`plugins/<name>/skills/`, `plugins/<name>/hooks/`, `plugins/<name>/bin/` — components live under the plugin they belong to. Standard model; auto-discovery and `${CLAUDE_PLUGIN_ROOT}` interpolation work as designed.

### Outside plugin directory at repo root

`bin/`, `hooks/`, or other component-shaped directories live at repo root with no owning plugin. Auto-PATH registration (which depends on `bin/` inside a plugin per the plugin model) does not happen. Appropriate when the artifact serves the marketplace as a whole (a manual installer CLI, a project-setup nudge) rather than any specific plugin. Constrains: only reachable for local-clone users who add the directory to PATH themselves; plugin-installed users must fall back to absolute paths via `${CLAUDE_PLUGIN_ROOT}/scripts/...` in skill steps. The `bin/` entry at repo root is effectively dead in the plugin-install pathway.

## Cross-platform skill publishing

How skills are exposed to non-Claude agent runtimes alongside the Claude-native form.

### Per-skill Codex sibling marker

Every `skills/<name>/` directory contains a sibling `agents/openai.yaml` file declaring Codex-platform interface metadata (`interface: {display_name, short_description}`, `policy: {allow_implicit_invocation}`). Lives alongside the Claude-native `SKILL.md` so the same skill folder publishes to both platforms. Appropriate when the author wants one skill source-of-truth feeding multiple agent ecosystems; constrains: skill folder layout becomes platform-fan-out — adding a new target runtime means another sibling file in every skill dir.

### Multi-runtime install via npm bootstrap

A Node CLI (`bin/install.js`, invoked via `npx <plugin>@latest`) copies skills/agents/tools into runtime-specific directories (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.windsurf`) with an interactive prompt selecting subset. Same source ships as a Claude Code marketplace plugin AND as a multi-runtime skill bundle through npm. Appropriate when the plugin's value proposition is portable beyond Claude Code; constrains skills to cope with two filesystem layouts at runtime — plugin mode under `${CLAUDE_PLUGIN_DATA}`, npm mode under `~/.<runtime>/` — typically via env-var fallback chains in skill steps.

## Bin-wrapped CLI distribution

How a plugin exposes a command-line entry point and where the runtime resolves its sibling files from.

### Script-relative shell wrapper

`bin/<name>` is a short bash script that resolves `PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"` and execs the actual binary (typically Python). No `${CLAUDE_PLUGIN_ROOT}` env var check, no fallback cascade — strictly script-relative, always. Works because Claude Code's cache preserves the repo's internal directory layout. Appropriate when the wrapper's only job is path math and the repo is willing to depend on cache-layout stability. Constrains: if the cache layout ever flattens or rearranges, the wrapper breaks silently with downstream ImportError; placing `bin/` outside any plugin (see Plugin-component placement) makes the wrapper unreachable through plugin install paths.

### npm bin entry without shipped binary

`package.json` declares `"bin": {"<name>": "./<path>.js"}` for npm `npx` distribution. Inside Claude Code the JS is invoked via `node "${CLAUDE_PLUGIN_ROOT}/dist/cli/index.js"` from `mcp.json` args rather than through the bin entry. Sometimes the bin path is dead — `package.json` references `./src/cli.js` but `src/` doesn't exist in the committed tree, leaving npm metadata pointing at vapor. Appropriate when the package is dual-distributed (npm + plugin) and the bin entry serves only the npm path. Constrains: drift between the two paths is invisible until an npm install fails; consumer repos using the bin field encounter dead pointers.

### Node-only with mcp.json invocation

Plugin runtime is JavaScript; the binary is invoked via `node "${CLAUDE_PLUGIN_ROOT}/dist/cli/index.js" mcp` directly from the MCP server config or hook commands. No bash wrapper, no executable bit needed (node interprets the path). Appropriate when plugin is pure Node and target platforms include Windows where bash wrappers fail. Constrains hooks that need shell features to live in separate `.sh` files invoked by `bash "$CLAUDE_PLUGIN_ROOT/hooks/foo.sh"`.

## Dependency installation runtime

What language ecosystem the plugin's runtime dependencies belong to.

### Node (npm/pnpm)

Plugin ships `package.json` with `dependencies` block; Node's package manager performs the install. Native modules (better-sqlite3, tree-sitter) require extra ABI handling (see Dependency change detection). Constrains the plugin to a Node-version range declared in `engines` and forces every plugin file using ESM `import` to resolve through whatever node_modules layout the install produces.

### Python (uv preferred, pip fallback)

Hook detects `uv` and uses it for venv creation + install (`uv venv`, `uv pip install`); falls back to stdlib `python -m venv` + `pip install` if `uv` is absent. The package manager preference is encoded in the script's branching, not in any manifest. Appropriate when the plugin needs Python tooling and wants the speed of `uv` when available without making it a hard dependency. Constrains nothing structurally — both paths produce a venv at the same location.

## Dependency manifest format

How the dependency list is expressed.

### package.json + lockfile

Standard Node manifest with a committed `package-lock.json` or `pnpm-lock.yaml`. Constrains lockfile-correctness — install must respect committed lockfile to be reproducible.

### Hard-coded in install script

No requirements.txt, no pyproject.toml, no manifest of any kind — the dep list is hard-coded in the SessionStart hook (e.g., literal `langsmith` in a shell script's install command). Appropriate when the dep set is tiny and stable (1-2 packages). Constrains: no version pin anywhere, no machine-readable dep declaration for tooling — readers must grep the install script to know what gets installed.

### Vendored node_modules in-tree

`node_modules/` (or pnpm `.pnpm/`) committed directly into the plugin tree. No install step at runtime; deps load straight from the committed copy. Appropriate when the plugin author wants zero-install determinism. Constrains: platform-specific binaries (e.g., `@esbuild/linux-x64`) inside the vendored tree lock users to whatever OS/arch was committed — Windows or Darwin users get a broken install with no automatic recovery.

## Dependency change detection

How a SessionStart hook decides whether to (re)install dependencies on each session.

### Manifest diff (`diff -q`)

Hook caches the source `package.json` (or equivalent) into `${CLAUDE_PLUGIN_DATA}` and compares each session via `diff -q "$src" "$cached"`. Mismatch triggers reinstall and updates the cache. Appropriate when reinstall is cheap relative to importing or compiling. Constrains: works only for diffable manifests; misses semantic equivalence (e.g., reordered keys produce a false-positive reinstall).

### Existence-only

Hook checks `[ ! -f "$VENV_PY" ]` and only creates the venv if missing; checks `python -c "import <pkg>"` and only installs if the import fails. No version check, no manifest hash, no diff. Appropriate for tiny stable dep sets. Constrains: misses upgrades — if the plugin later requires a higher version of the same package, the existence check passes silently and the new requirement surfaces as a runtime ImportError or AttributeError far from the install hook.

### ABI marker for native modules

Beyond manifest-diff, a separate `.node-abi` marker file holds Node's `process.versions.modules` integer. On every SessionStart the current ABI is compared against the marker; mismatch triggers `npm rebuild <native-modules-explicit-list>` (only enumerated native modules, not the whole tree). Two orthogonal change axes: package.json drift drives full reinstall, ABI drift drives native-only rebuild. Appropriate when native modules dominate install cost and Node major bumps are the common case. Constrains: the rebuild list is hard-coded — adding a new native dep requires editing the shell script.

### Runtime-probe fallback

In addition to marker-based detection, the runtime hook actually invokes the native module (`require("better-sqlite3")` in a child process) and pattern-matches `/NODE_MODULE_VERSION|was compiled against a different/` on the error to trigger inline rebuild. Belt-and-suspenders against stale or corrupted markers. Appropriate when the cost of a wrong "no rebuild needed" answer is high; constrains nothing except adding a small startup probe latency.

## Dependency install location

Where the installed dependencies physically live.

### Plugin data dir with symlink-out

Install into `${CLAUDE_PLUGIN_DATA}/<deps>` (writable user data dir) then `ln -sfn $PLUGIN_DATA/node_modules $PLUGIN_ROOT/node_modules` so ESM `import` from plugin source resolves without `NODE_PATH` hacks. Inverse of the "install into plugin root" pattern; relies on the plugin root being a managed/read-only space. Constrains nothing for the consumer; the plugin author must remember to keep the symlink fresh on every reinstall.

### Per-user venv with project-mode + npx-mode forks

Plugin mode uses `${CLAUDE_PLUGIN_DATA}/venv`; npx-bootstrap mode uses `~/.<plugin-name>/venv`. Skills resolve `$<PLUGIN>_PY` env var with shell-default fallback to the npx path. Appropriate for multi-runtime plugins. Constrains: a user who installs both ways ends up with two venvs — skill invocations are non-deterministic about which one runs unless skills always read `$<PLUGIN>_PY` first.

### In-tree vendored

Deps committed under the plugin directory (see Dependency manifest format → Vendored node_modules in-tree). No install location decision at runtime — the deps are wherever they were committed.

## Dependency-install failure recovery

How an install hook responds to a failure mid-install.

### Self-healing via marker cleanup

On any failure branch the script `rm -f` the cached manifest and ABI marker, then `exit 0`. Next SessionStart sees no cached state and retries from scratch. Constrains the script to never persist partial state — every write must be paired with cleanup-on-failure.

### Silent fail-through

Every install invocation is `>/dev/null 2>&1` and ends with `|| true`. Failures are invisible in the hook; the dep-consuming skill or tool surfaces the failure later via ImportError. Appropriate when the install-hook author would rather skill-level errors carry the diagnostic; constrains: users see a confusing downstream error with no signal pointing at the install hook as the actual failure site.

### No retry path

Install runs once; on failure the venv may exist with a half-installed package set, and the existence-only change detector skips the reinstall on subsequent sessions. Recovery only via manual venv removal. Constrains the install logic to be all-or-nothing within a single hook execution.

## Hook failure posture

What the plugin's hook scripts do when something goes wrong.

### Fail-open with always-exit-0

Every hook (`.mjs`, `.sh`) wraps its body in try/catch (or shell `|| true`) and ends with `exit 0`. No `continue: false`, no permission denial, no blocking gate. Even Pre/PostToolUse hooks documented as "blocking" are actually advisory. Appropriate when hooks are nudges and reminders, not enforcement; constrains: there is no actual gate — hooks cannot prevent an Edit, only annotate or warn after.

### Silent-on-failure SessionStart

SessionStart hook silences all install errors via `>/dev/null 2>&1` and `|| true`. No JSON `systemMessage`, no stderr message, no `stopReason`. Appropriate for hooks that should never block session start under any circumstance; constrains observability — there is no in-session signal of install failure.

## Tool-use enforcement gates

Whether and how a plugin uses Pre/PostToolUse hooks to intercept tool calls.

### No tool-use hooks

Plugin ships only SessionStart hooks (or no hooks at all). Tool-use is unintercepted. Appropriate for plugins whose value lies in skills/agents/tools rather than in tool-call gating. Constrains: any safety boundary the plugin needs must come from elsewhere (agent permission scoping, sandboxed worktrees, post-hoc human review).

### PreToolUse on Edit/Bash for advisory injection

Plugin registers `PreToolUse` matchers on `Edit`, `Bash`, `Write`. The handler injects context (e.g., "blast radius" warning showing which symbols an edit affects, or staleness check on an index) but never blocks — `exit 0` always. Output is JSON on stdout for context injection; stderr for diagnostics. Constrains: the hook runs on the critical path of every matched tool call and budget management matters (e.g., 8-second timeout on a child node process invoked from PreToolUse means edits stall up to that budget on slow queries).

### PostToolUse for index/state maintenance

Plugin registers `PostToolUse` on `Edit`, `Write`, `Bash` to update derived state — invalidate or rebuild a code index on file edit, capture event to an external spool on every tool invocation. Appropriate when the plugin maintains derived state that must follow filesystem reality; constrains: post-hooks run after the tool completes, so any error there has no preventive effect — only signals that the next read of the derived state may be stale.

### Bash matcher as proxy for git pre-push

Plugin hooks `PreToolUse` with `matcher: "Bash"` and parses the command string for `git push` patterns to fire reminder behaviors (e.g., staleness check on a governance file). Always `exit 0` — explicitly documented as a reminder, not a block. Acknowledges that terminal pushes (outside Claude's Bash tool) are uncovered. Appropriate when the repo wants Claude-Code-only nudges around git operations; constrains coverage to the Claude tool surface.

## Session context loading

How plugins inject content into the agent's prompt at session start.

### SessionStart writing status block to stdout

Hook writes a markdown summary of plugin state (index status, governance summary, git context, build status) to stdout. Claude Code includes the stdout as additional context. Multiple plugins competing for SessionStart output produce concatenated blocks in undefined order (depends on plugin-load order). Constrains the agent's startup prompt to whatever each plugin chose to emit, with no inter-plugin coordination.

### SessionStart writing env-vars to CLAUDE_ENV_FILE

Hook does not emit prompt context; instead writes shell-format env-var exports (`EVOLVER_PY=/path/to/venv/python`) into `$CLAUDE_ENV_FILE` for downstream skill steps to consume. Appropriate when the SessionStart's job is environmental, not informational. Constrains: env vars must be resolvable at every skill site, typically via shell default-fallback `${VAR:-fallback}`.

### `hookSpecificOutput.additionalContext` envelope

Structured JSON output `{hookSpecificOutput: {additionalContext: "..."}}` is the documented channel for context injection. Plain stdout JSON without the envelope (top-level fields only) is what some hooks actually emit. Mixed observed; envelope adoption is uneven. Constrains tooling that wants to detect "this hook injects context" — must look for both shapes.

### User-settings session-start hook installed by a skill

A skill writes a hook script to `~/.claude/hooks/<file>.sh` and edits `~/.claude/settings.json` to register it as a global session-start hook — outside the plugin's own `hooks.json`. The hook then prints "ACTION REQUIRED" directives to stdout that Claude reads at session start. Appropriate when the author wants always-on user-level nudges across all projects; constrains: the hook persists after `/plugin uninstall` (it lives in user config, not plugin scope), runs in every project regardless of relevance, and requires a sibling "uninstall" skill to unwind.

## SessionStart matcher scope

Which session sub-events the hook fires on.

### Empty matcher (all sub-events)

`matcher: ""` or matcher absent — fires on `startup`, `resume`, `clear`, `compact` alike. Appropriate for idempotent operations cheap to repeat; wasteful when the operation is non-trivial (e.g., running `diff -q` and `command -v` checks on every `/clear`).

### Explicit subset

`matcher: "startup|resume"` or `"startup"` only — fires on the chosen session phases. Appropriate when the hook produces side effects that should not repeat on every compaction. Constrains the author to know which phases matter for their hook's purpose.

### Per-hook differentiation within one plugin

Different hooks within the same plugin use different matchers — e.g., dep-install on empty matcher (any sub-event), context-emit on `startup|resume|compact`. Constrains coordination — one plugin's "boot work" may run on different triggers than its "context emit" work, with no shared coordination point.

## User configuration surface

How a plugin accepts user-controlled settings.

### Absent (`userConfig` not declared)

No `userConfig` block in `plugin.json`. Plugin runs without user-tunable settings. Appropriate for plugins with no per-user variables. Constrains: any future configurability requires either adopting `userConfig` or routing through alternative substrates.

### Project-file at project root

Plugin reads a project-level config file (e.g., `.kdoc.yaml`, `.evolver.json`, `CLAUDE.md` `## Project Type` section) from the project root in its session-start hook or skill steps, rather than going through `userConfig`. Config lives with the project it configures, not with the user. Appropriate when settings are per-project and the user-config UI surface is the wrong scope. Constrains: plugin uninstall does not clean up project-level config files; users must know to remove them manually.

### Vendor-CLI credential file

Plugin secrets (e.g., `LANGSMITH_API_KEY`) are stored in a third-party CLI's credential store (`~/.config/<vendor-cli>/credentials` or platform-specific equivalent), loaded by the SessionStart hook, and exported into `$CLAUDE_ENV_FILE`. Appropriate when the plugin wraps a vendor CLI that already manages credentials; constrains the plugin to a hard dependency on the vendor CLI's credential-file format remaining stable, and bypasses Claude Code's plugin-config UI entirely (users configure via `<vendor-cli> auth`).

### Env var read by script

A plugin script (not `userConfig`) reads an env var like `CLAUDE_SKILLS_DIR` or similar to relocate behavior. Appropriate for testability hooks the plugin author wants but doesn't want to expose as user config; constrains: the env var is a hidden interface — consumers won't find it without reading source.

## Plugin-to-plugin dependencies

How a plugin declares (or fails to declare) reliance on other plugins.

### `dependencies` field declared

`plugin.json` carries a `dependencies` array. May be empty (`[]`), bare strings (`["foo"]`), or objects (`{"name": "foo"}`). Custom resolver code accepts both shapes. Appropriate when the marketplace has multi-plugin dependency chains. Constrains tooling — Claude Code's native `dependencies` field is platform-version-gated (v2.1.110+ per the docs), so pre-version consumers ignore the field entirely; resolver behavior depends on consumer version.

### Implicit via filesystem convention

Plugin A reads files written by plugin B at a shared path (e.g., `~/.ai-sessions/spool/events.jsonl`) without any declared dependency. If B is not installed, A silently degrades (drift warnings stop firing, drift summary becomes empty, etc.). Appropriate when the dependency is genuinely optional. Constrains: there is no static signal of the coupling — install-time resolution can't detect that A would benefit from B.

### External-MCP install during bootstrap

The npm bootstrap CLI offers to install third-party MCP servers (Context7, LangChain Docs) via `claude mcp add` during plugin install, prompting the user interactively. The MCPs are not declared as plugin dependencies; their install is a side-effect of running the bootstrap. Appropriate when MCPs augment but do not gate the plugin's behavior; constrains: only fires through the npx path, not through `/plugin install`, so marketplace-installed users miss the augmentation entirely.

## Testing framework

What runs the test suite.

### pytest

Python tests under `tests/`; pytest config in `pytest.ini` at repo root or absent (relying on auto-discovery). Sometimes augmented with per-plugin `tests/test_cases.json` fixtures driven by a central `test_base.py` (data-driven test pattern). Appropriate for Python-heavy plugins.

### vitest

Node plugins declare `"test": "vitest run"` with `vitest` devDep. Standard Node test runner.

### node:test (node --test)

Some plugins use Node's built-in test runner (`"test": "node --test"`) instead of vitest. Appropriate for plugins minimizing devDeps; constrains test-style to node:test's API surface.

### Tests declared but absent from tree

`package.json` declares a `test` script but no test sources are committed (tests stripped before sync from upstream). Constrains validation to whatever the upstream pipeline did before sync.

## CI presence

Whether the repo has automated continuous integration.

### No CI

`.github/` directory absent or contains only issue templates. Validation is human-triggered (a `/dev:validate` skill the author runs manually). Appropriate when the author is the only contributor and disciplined about local validation; constrains contributors — anyone without the validation skill or who forgets to run it merges unchecked changes. PR-time signal is absent.

### Single workflow per concern

`.github/workflows/<name>.yml` per concern (skill validation, docs site build, marketplace validation). Triggers on push/PR to main. Major-version action pinning (`actions/checkout@v4`). Built-in caching via runner setup actions (`cache: 'pip'`, `bundler-cache: true`). Constrains the workflow author to keep distinct concerns separately invokable.

## Validation strategy

What a CI or local validator actually checks.

### Tiered validator driver

A single Python driver (`validate_all.py`) accepts `--tier {commit,push,ci}` and runs different validator subsets at each tier, with CI running all three sequentially. Drives 15+ underlying validators (frontmatter, structure, links, references, doc-structure, etc.). Appropriate when the author wants local fast-checks plus exhaustive CI checks from the same code path; constrains readers — the tier-to-validator mapping lives only in the driver source, not in the workflow YAML.

### In-editor skill (no CI)

A `/dev:validate` skill the author runs in-editor before `/dev:release`. Checks frontmatter, version sync between `package.json` and `plugin.json`, Python AST parse on tool files, executable bit on hook scripts, JSON validity of `hooks.json`, cross-references between skill `subagent_type:` and agent files. Appropriate when CI is out of scope; constrains: validation is human-triggered; contributors without the skill ship blind.

### No validator

No CI workflow, no in-editor validator. The marketplace ships unchecked; any JSON syntax error, schema drift, or version mismatch reaches consumers undetected. Constrains discipline to commit-author memory.

## Custom installer alternative

A repo-shipped distribution mechanism that side-steps `/plugin install`.

### Localhost web UI installer

`scripts/web_installer.py` runs a local HTTP server (e.g., port 8765) that reads `marketplace.json`, presents the catalog (including the custom `bundles` extension) in a browser UI, and installs selected plugins as `~/.claude/skills/<name>/` via sparse git-clone. Bypasses Claude Code's plugin caching entirely. Appropriate when the platform's install UX is insufficient for the author's feature set (here, dependency resolution and bundle grouping); constrains: behavior diverges from `/plugin install` semantics, and uninstall semantics are different.

### CLI installer with sparse-checkout

`scripts/<plugin>-skill` (or similar standalone CLI) installs into `~/.claude/skills/` via `git clone --filter=blob:none --sparse` per-plugin. Acknowledges in README that the official marketplace doesn't support automatic dependency resolution and the custom installer fills the gap. Appropriate as a transitional substrate; constrains users to maintain awareness of two install paths.

### npm bootstrap

`bin/install.js` + `npx <plugin>@latest` installs the plugin into multiple agent runtimes (`~/.claude`, `~/.cursor`, etc.) and optionally configures external MCPs. Distinct concern from "install as Claude plugin" — same source, different consumer. Constrains the install script to detect and target each supported runtime's directory layout.

## Documentation footprint

What docs the repo ships at root and per plugin.

### Standard root entry points + per-plugin variation

Root carries `README.md`, `LICENSE`, sometimes `CLAUDE.md` and `CHANGELOG.md`. Per-plugin docs vary widely within one marketplace — some plugins have `docs/ARCHITECTURE.md`, some embed architecture rationale into README ("Why X", "Why Y" sections), some have topical docs (`PROTOCOL.md`, `ADOPTION.md`, `CERTIFY.md`, `SCAFFOLD.md`), some have superpowers/specs/plans subtrees. Inconsistency within a single marketplace makes a reader unable to predict where to find architectural detail without checking each plugin separately.

### Repo-meta docs alongside user-facing docs

Root carries the repo's own workflow artifacts (`DESIGN.md`, `PHILOSOPHY.md`, `QUALITY.md`, `HANDOFF.md`, `IDEAS.md`, `RELEASE.md`) — meta-documentation about how the repo operates. Often coexists with user-facing docs in `docs/`. Appropriate when the repo dogfoods plugins it ships (e.g., the `handover` and `idea-log` plugins are themselves bootstrapped here). Constrains readers to mentally separate "how the repo runs" from "how the plugins serve users."

### Per-plugin Keep-a-Changelog only on some plugins

Within a multi-plugin marketplace, some plugins ship `docs/CHANGELOG.md` in Keep-a-Changelog format while others lack changelogs entirely despite high patch-version counts (e.g., `1.0.38` patches with no record). Constrains: release history is uneven across the marketplace.

### CHANGELOG.md driven by conventional-commit parsing

`CHANGELOG.md` updated by the release skill, which parses `feat:`, `fix:`, `refactor:` prefixes from `git log` output and inserts dated sections. Constrains commit-message discipline — non-conventional commits are silently dropped from the changelog.

### No CLAUDE.md

Plugin or marketplace ships no `CLAUDE.md` operational doc. Agents working in the repo have no project-specific procedures to follow. Constrains agents to default behavior; rules and patterns live only in skill bodies if anywhere.

### CLAUDE.md as project-config surface

`CLAUDE.md` declares a `## Project Type` field (`java | skills | blog | custom | generic`) that multiple skills read at runtime to dispatch to language-specific sub-skills. The doc doubles as agent-facing rules AND a runtime config surface. Appropriate when the author wants per-project routing without `userConfig`; constrains: skills must defensively parse the field and handle missing values, and the CLAUDE.md schema becomes part of the plugin's interface.

## Community health files

Standard open-source repo files beyond LICENSE.

### Bare minimum (LICENSE only)

Root carries `LICENSE`. No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`. Constrains contributor-onboarding to whatever the README says.

### LICENSE + CODE_OF_CONDUCT + issue templates

Root carries `LICENSE` and `CODE_OF_CONDUCT.md`; `.github/ISSUE_TEMPLATE/` has `bug_report.md` and `feature_request.md`. No `SECURITY.md` or `CONTRIBUTING.md`. Constrains: contribution flow is implicit, security-disclosure path undocumented.

## Project-convention sidecar files

Project-specific configuration files that aren't standard Git or Claude Code conventions but are read by the plugin's own logic.

### `.worktreeinclude`

A repo-root file listing files the plugin should copy into git worktrees it creates for sub-agent workflows (e.g., `.evolver.json`, `.env`, `evolution_archive/`). Read by skill steps when setting up isolated proposer worktrees. Appropriate when the plugin orchestrates multi-worktree workflows that need a curated subset of project state. Constrains: not a standard mechanism — the file is meaningful only to this plugin's skills.

## Agent permission and safety model

How sub-agent edits are gated and contained.

### Default tools, no permission escalation

Agents declare a comma-separated `tools:` scalar string (`Read, Write, Edit, Bash, Glob, Grep`). Sometimes `disallowedTools:` provides a negative list. No `permissionMode`, no permission-rule syntax (`Bash(...)` wildcards). Appropriate for agents with conservative authority. Constrains: every edit path goes through the standard permission flow.

### `permissionMode: acceptEdits` + worktree isolation

Agent runs with pre-granted edit authority (`permissionMode: acceptEdits`) inside a git worktree the orchestrating skill creates. Safety comes from worktree boundary + post-hoc human review at a `/deploy` skill, not from tool-use hooks or in-flight permission gates. Appropriate when the agent needs to iterate freely on isolated files and the cost of permission prompts would dominate the task; constrains: the orchestrating skill MUST set up the worktree first, otherwise the agent operates on the live tree with full edit authority.

### YAML array form for allowed-tools

Skills declare `allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion]` as a YAML array (vs. comma-separated scalar). The token `Agent` is the legacy name for the Task tool used to launch sub-agents. Constrains nothing — purely stylistic — but observed consistently across one plugin's skills, suggesting authoring convention.

## Marketplace validation against schema

Whether `marketplace.json` itself is checked.

### `$schema` URL

Manifest declares a `$schema` field pointing at a JSON Schema URL — editor IDEs and some validators can check the manifest at edit time. Not observed in this bin. (Noted as a non-occurrence — the schema reference is absent across all three samples.)

### No schema reference

`marketplace.json` carries no `$schema`. Editor-side validation off; CI validators (when present) check skill content rather than marketplace shape. Constrains: a typo or schema drift in `marketplace.json` ships to consumers unchecked.
