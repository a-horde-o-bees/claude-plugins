# Sample

Pass-1 Phase-1a partial for bin 18. Functional decomposition of stellarlinkco/myclaude, thecodeartificerX/codetographer, and tretuttle/AI-Stuff, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

Where the marketplace inventory is declared and how many manifests coexist in one repo.

### Single root marketplace.json

One `.claude-plugin/marketplace.json` at repo root listing every plugin entry as a relative `./<dir>` source. Standard claude-code aggregator shape. Plugin entries are keyed by `name` and bound by relative `source` paths so the manifest and the plugin trees travel together in one git repo.

### Nested mini-marketplace inside a plugin directory

A second `marketplace.json` lives one level deep (e.g. `persona/.claude-plugin/marketplace.json`) listing only the enclosing plugin with `"source": "."`. Lets the plugin be installed either via the aggregator marketplace or as its own standalone marketplace pointing at its own directory. Drift hazard: the nested entry's version field is hand-maintained and observed lagging the plugin's own `plugin.json`.

### No marketplace manifest at all

Repo ships a single bare plugin via `.claude-plugin/plugin.json` only; install is by `git clone` + `claude --plugin-dir <path>`. Plugin is invisible to `/plugin install` discovery without an external marketplace registering it. Discoverability metadata (keywords, tags) instead lives in a sibling `package.json` for npm-style aggregators, leaving any marketplace consumer that reads only `plugin.json` blind.

### Parallel non-marketplace inventory

Same repo carries `marketplace.json` AND a separate `config.json` enumerating a strictly larger set of modules + a "skills" axis for an alternate installer (npx self-installer). The two inventories are intentionally disjoint: slash-command flow gets the marketplace subset; npx flow gets the richer config.json menu with its own operations DSL (`copy_file`, `copy_dir`, `merge_dir`, `run_command`).

## Marketplace-entry metadata richness

What fields each entry carries beyond `name` + `source`.

### Description-only minimal entry

Entry carries `description` and nothing else (no `version`, no `keywords`, no `category`, no `author`). Lowest-effort listing — works for slash-command install but offers nothing to a marketplace UI doing search or filtering.

### Description + version + author + keywords

Mid-richness entry: human-readable description, semver `version` (duplicating the plugin's own `plugin.json` version), `author` block, and a `keywords` array of 5-11 terms. No `category`, `tags`, or `categories` fields used. Sibling entries in the same marketplace can drift between this richness and description-only — no enforced schema across siblings.

### Category as the only discoverability field

Every entry carries `category` (values like `development`, `productivity`) but no `tags` and no `keywords`. Single-axis classification for a small fixed taxonomy.

### `$schema` reference

Top-level `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"` declared on the marketplace document. Enables editor IntelliSense but is not validated in CI here — remote schema is fetched at edit time only.

## Plugin source binding

How marketplace entries point at their plugin trees.

### Relative path source

Every `source` is `./<dir>` (or `"."` for self-source in nested marketplaces). Plugin tree lives in the same git repo as the marketplace; cloning the marketplace repo gets every plugin. `strict` field defaulted (implicit true) on every entry — no entry overrides.

## Version authority

Where the canonical version of a plugin lives and what the drift surface is.

### plugin.json only

`plugin.json.version` is the single source of truth. No marketplace.json (bare plugin shape) or marketplace entry omits version. Sibling `package.json.version` may exist for npm tooling and is hand-kept in sync — a silent drift risk because nothing validates equality.

### Marketplace entry duplicates plugin.json

Marketplace entry's `version` field and the plugin's `plugin.json.version` both hold the same string, hand-maintained on every release. Drift is observed in practice when only one is bumped (nested persona marketplace at `1.0.0` while plugin.json moved to `1.1.1`). The marketplace path uses whichever the consumer's installer reads first.

### Three-way version split (marketplace vs npm vs git tags)

Marketplace + plugin.json (5.6.1), `package.json` consumed by npx installer (6.7.0), and git tags on master (v6.8.2) all carry independent version numbers that drift independently. Each is meaningful in its own context but not reconciled. The npx installer asks GitHub's releases API for `tag_name` at runtime and bypasses the checked-in version fields entirely, so installed artifacts match the tag while a consumer reading the source files sees stale fields.

## Channel distribution

How consumers pin to a stable revision versus tracking HEAD.

### Tags-on-default-branch single channel

No stable/latest split in the manifest; users pin via `@ref` syntax or default to GitHub's latest-release endpoint. Tags live on the default branch directly. `rc/*` branch pattern may exist for pre-merge CI validation but produces no release artifact. The `--tag <tag>` flag on a self-installer CLI is the explicit pinning mechanism.

### No channel mechanism at all

No tags, no releases, no branch pinning convention — every install pulls HEAD of the default branch. Bare-plugin `claude --plugin-dir` installs are pinned only by the consumer's checkout SHA. Version bumps in plugin.json appear as hand-edits in feature commits with messages like `chore: bump for cache bust`, indicating the version is being used as a cache-invalidation lever for `/plugin update` rather than as a stable channel coordinate.

## Release cadence and tagging

The discipline (or absence) around marking specific commits as releases.

### Manual semver tagging on master

Tags accumulate on master as the author bumps version (78 tags across years observed). All clean semver, no pre-release suffixes, no dev-counter scheme. CHANGELOG generated by `git-cliff` (configured via `cliff.toml`), invoked manually via a `make changelog` target. No pre-commit hook auto-bumps the patch level. Tag-sanity is unenforced — package.json or marketplace.json version can lag the tags indefinitely.

### Untagged 1.0.0 declarative version

`plugin.json.version` declares `1.0.0` but no git tag exists, no GitHub Release has been cut. Reproducible install requires the consumer to pin by SHA. Initial public-release shape — repo created and version declared in the same week.

### Hand-bumped version-as-cache-bust

No tags at all; plugin.json version is bumped within feature commits explicitly for cache invalidation (`bump to 1.2.0 for cache bust`). The version field is operating as a refetch trigger for downstream `/plugin update` rather than as a release coordinate. Sibling plugins in the same marketplace can each have independent versions that get bumped at unrelated times.

## Plugin-component registration

How `plugin.json` declares (or relies on convention to discover) the skills, agents, hooks, commands, and MCP servers it ships.

### Default convention-based discovery

`plugin.json` carries only `name`, `description`, `version`, `author` — no `components`, `skills`, `commands`, `hooks`, or `agents` fields. Claude Code discovers components by directory layout (`skills/`, `commands/`, `agents/`, `hooks/hooks.json` under the plugin root). Lowest ceremony; relies on consumer staying within the canonical directory names.

### Inline mcpServers object

`plugin.json` declares an `mcpServers` object inline (rather than referencing an external `.mcp.json`), binding a server name to `command`, `args`, and `env`. Env block typically threads `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` so the server resolves its own runtime location. Pitfall: env-thread paths assume the dependency-install side-channel has populated `${CLAUDE_PLUGIN_DATA}/node_modules` before MCP server startup, with no startup gate.

### Three-channel parallel registration

Components are registered three ways in the same repo: (a) marketplace.json plugin entries for the slash-command flow (relies on directory conventions), (b) `config.json` modules for the npx flow (enumerates per-module operations explicitly: `copy_file`, `copy_dir`, `merge_dir`, `run_command`), (c) legacy Makefile targets like `deploy-bmad`. Each channel registers components differently; the npx path also merges per-module agent presets into `~/.codeagent/models.json` and tags every merged hook entry with `__module__: <name>` for surgical unmerge on uninstall.

## Agent frontmatter shape

The fields plugin agents declare in their YAML frontmatter.

### Minimal name + description

Agents declare `name` and `description` only. No `model`, `tools`, `allowed-tools`, `disallowedTools`, `memory`, `maxTurns`, `color`, `effort`, `background`, or `isolation`. Relies on Claude Code defaults for everything else.

### Tool-restricted agent

Frontmatter includes `tools` (allowed) and optionally `disallowedTools` listing tool names like `Read, Glob, Grep, Bash` and `Write, Edit, NotebookEdit`. Plus orchestration knobs: `memory: project`, `model: inherit`, `maxTurns: <int>`. Three syntactic variants of the tools list observed across one repo: comma-delimited string (`Read, Glob, Grep, Bash`), bare comma list, and YAML array (`["Read", "Bash"]`) — inconsistency within sibling agents indicates no enforced schema.

### Effort-tier model selection

Frontmatter declares `model: sonnet` (specific model name, not `inherit`) plus `effort: medium` and `maxTurns: 30`. Pins compute envelope per agent rather than inheriting from the session.

## Dependency installation — manifest format

The on-disk format declaring runtime deps the plugin needs at install time.

### package.json (Node/npm)

`package.json` lists production dependencies (tree-sitter grammars, `@modelcontextprotocol/sdk`, `better-sqlite3`, `web-tree-sitter`, `playwright`, `js-beautify`). `engines.node` declares minimum runtime; `type: "module"` forces ESM. Install is invoked via `npm install --production` (sometimes with `--legacy-peer-deps`) inside the data dir.

### go.mod for a bundled binary

`codeagent-wrapper/go.mod` describes a Go binary bundled in the plugin source tree, rebuilt by CI for six target OS/arch combinations and attached to GitHub Releases as prebuilt artifacts. The plugin's runtime install fetches the prebuilt binary by uname-derived URL rather than rebuilding from source on the user's machine.

### No manifest — script-driven hardcoded versions

`scripts/setup.sh` downloads or compiles binaries with versions hardcoded in the script itself (`HELLWAL_VERSION="1.0.7"`). No declarative manifest, no update mechanism — users get whatever was pinned at the commit time of the setup script.

## Dependency installation — install location

Where the materialized dependencies land on disk.

### `${CLAUDE_PLUGIN_DATA}/node_modules`

Plugin's writable data directory. `NODE_PATH` env in plugin.json's `mcpServers` block (or in skill/command preambles) resolves modules from this location. Survives plugin upgrades because plugin root is read-only by convention; data dir is the only writable location. Typical for Node plugins that install transitively heavy deps.

### `${CLAUDE_PLUGIN_DATA}` plus a sibling browser bundle

Browser-capture plugins place `node_modules` plus a Chromium download (~170 MB) under `${CLAUDE_PLUGIN_DATA}` via `PLAYWRIGHT_BROWSERS_PATH=<data>`. One-time download skipped on subsequent sessions when the staleness check passes. Verifies by launching a headless instance and closing it before declaring success — catches broken downloads that pure file-existence would miss.

### `${CLAUDE_PLUGIN_ROOT}/bin/`

Native binaries written into the plugin's own root directory rather than the data dir. Crosses the convention that plugin root should stay read-only — the binary disappears on plugin reinstall and must be repopulated by the setup script. Used when a setup script populates a `bin/.gitkeep` placeholder at first run.

### `~/.claude/bin/` outside the plugin tree

Pre-plugin-era installer writes its bin directory to `~/.claude/bin/` regardless of which plugin invoked the install, plus appends that path to user shell rc files via auto-detection (`bashrc`, `zshrc`). Cuts against the plugin-era convention of containing artifacts under `${CLAUDE_PLUGIN_ROOT}` and lets the binary outlive plugin uninstall. Visible as an artifact of installers that predate the plugin model.

## Dependency installation — change detection

How the installer decides whether to rerun on subsequent sessions.

### sha256 of manifest + post-verify marker

Hash of the bundled `package.json` is compared against a hash of the cached copy in `${CLAUDE_PLUGIN_DATA}`. AND an `.install-ok` marker file must exist; the marker is deleted before install starts and only rewritten after a verification step (e.g. headless browser launch) succeeds. Marker JSON also records `{version, hash, timestamp, node, platform}` for forensics. A partial install (manifest copied but install crashed) leaves the cached manifest matching but the marker missing — next session retries cleanly.

### Byte-for-byte content equality on manifest

Reads `${CLAUDE_PLUGIN_ROOT}/package.json` and `${CLAUDE_PLUGIN_DATA}/package.json` and compares full string contents. No hash, no mtime, no version-only check. Pitfall: copy-then-install ordering is asymmetric — the manifest is copied to the data dir BEFORE `npm install` runs there, so a failed install leaves a "fresh" copy that makes the next equality check pass and masks the failure. `node_modules/` existence is a separate prior gate but a partially-populated `node_modules` after a crash defeats both gates.

### Existence-only check

`[ ! -x "${BIN_DIR}/<binary>" ]` test gates install. No version comparison, no rebuild on upstream change. Updating the bundled binary version requires the user to manually delete the file or rerun the setup script with a force flag.

### No change detection

Marketplace entry `version` is bumped manually as a cache-bust signal so consumer `/plugin update` refetches the whole plugin tree. The "change detection" lives in the marketplace consumer, not in the plugin itself — there's no install-time hook that compares manifests or hashes.

## Dependency installation — install trigger

The mechanism that fires the install at the right moment.

### SessionStart hook direct invocation

Plugin registers a `SessionStart` hook that runs the installer script synchronously (or via `child_process.spawn`) on every session start, with the change-detection layer short-circuiting fast on no-op. Timeout budget (e.g. `"timeout": 300`) bounds the worst-case install. Pitfall: aggregate internal timeouts of the install pipeline (npm + browser download) can exceed the hook timeout on cold first-run.

### Sanity-check-gated indirect invocation

`SessionStart` hook calls a generic sanity-check function (`runSanityCheck({ fix: true })`) that owns ~17 invariants of which deps are two; the sanity routine spawns the install detached + unref'd when its `node_modules`/manifest checks fail. Same code path is reachable via a manual `/sanity` skill invocation. Decouples "install dependency" from "this plugin starts up" by treating it as just another self-healing invariant. Pitfall: detached fire-and-forget means the hook returns before install finishes; MCP server startup races against `node_modules` materialization.

### User-invoked one-shot installer

Install is not a hook at all — user runs `npx github:<owner>/<repo>` or `bash setup.sh` manually. The installer is a CLI app that handles tarball download, interactive multiselect, copy operations, and merging into `~/.claude/settings.json`. Plugin install via `/plugin marketplace add` is the secondary channel that gets a smaller subset.

### Skill preamble lazy build

Skill preamble (the bash block at the top of a SKILL.md) runs an `update-check.js` and a `build.js` lazily on first skill use, separate from any hook. Defers heavy work (esbuild bundling) from session start to skill activation. Pitfall: the lazy builder mutates `package.json` in the data dir to add esbuild, which then defeats the sha256 staleness check the SessionStart installer relies on — observed bug from the interaction of two install paths managing the same manifest.

## Dependency installation — failure signaling and recovery

What the installer emits on failure and how the next session recovers.

### Multi-layer fail-open with stderr advisory

Installer writes human-readable `[plugin-name] <message>` lines to stderr with corrective install commands ("install build-essential" / "install Visual Studio Build Tools"). Top-level catch swallows errors so session start never fails. Hook output is a JSON `hookSpecificOutput.additionalContext` warning prefixed with a glyph (`⚠`) that tells the user to run `/sanity` or similar. No `continue: false`, no exit-2 — the model gets degraded context but the session lives.

### Fail-closed permission deny

Hook script outputs `{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "..."}` and exits 2 to block the offending tool call entirely. Used for invariants like "do not write to this protected path" rather than for missing deps. Stdin parsed with `jq` against the tool-call payload.

### Pre-delete the marker so failure is structurally visible

`.install-ok` marker is deleted before any install work begins and only rewritten after end-to-end verification (e.g. headless browser launch) succeeds. A crashed install leaves the cached manifest in place but the marker absent; the next-session check sees marker missing and retries from a clean state. The failure branch in the outer try/catch also wipes the cached manifest for redundant safety. Strongest atomicity posture observed.

### Set -e bash with stderr exit-1

Bash installer uses `set -euo pipefail`; first failed step terminates with stderr message and exit 1. Caller (Node CLI) rejects its install promise with `install script failed (exit ${code})`. Top-level `.catch` writes `ERROR: <msg>` to stderr and `process.exit(1)` — user-facing CLI output, not hook JSON.

## Bin-wrapped CLI distribution

The shape (or absence) of a `bin/` directory shipping a runnable entry point.

### Zero-dependency Node self-installer at `bin/cli.js`

Single-file Node.js CLI (~1,300 lines) using only stdlib (`https`, `zlib`, `fs`, `crypto`, `child_process`, `readline`). Hand-rolled implementations of: GitHub API client, https downloader, in-memory `tar.gz` extractor with path-safety validation, interactive `readline`-raw-mode multiselect, hook-config merger with surgical-unmerge tagging. Invoked via `npx github:<owner>/<repo>` (no npm registry publish needed). The marketplace.json is the secondary channel; README leads with the npx form. Cross-platform via `process.platform === "win32"` checks (`cmd.exe /c install.bat` vs `bash install.sh`, `where` vs `which`). Maintenance burden is high (TAR parsing from scratch) but supply-chain surface is zero.

### `bin/.gitkeep` placeholder populated by setup

`bin/` directory checked in with only a `.gitkeep` placeholder; `scripts/setup.sh` populates `bin/<binary>` at first run by compiling C source (`cc -Wall -Wextra -O3 hellwal.c -o bin/hellwal`) and downloading prebuilt tarballs (`tint_linux_x86_64.tar.gz`). Linux/x86_64 hardcoded — porting to other platforms requires script edits. Hooks reference `${CLAUDE_PLUGIN_ROOT}/bin/<binary>` directly (no PATH discovery).

### No bin directory; node-invoked scripts

No `bin/`. Scripts live under `scripts/` and are invoked as `node ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.js` from skill commands and hook entries. Shebangs (`#!/usr/bin/env node`) are present on installer scripts but the scripts are launched via `process.execPath` rather than the shebang, so executable mode bits don't matter. Cross-platform without `.cmd`/`.ps1` pair.

## Tool-use enforcement (hooks)

Claude Code hook events used for permission, advisory, or interception of tool calls.

### PreToolUse Bash dangerous-command blocker

`hooks.json` matcher `Bash` runs a Python script that inspects the bash command, optionally rewrites or blocks based on a denylist. Companion `inject-spec.py` on the same matcher likely rewrites the command rather than emitting `additionalContext` (placement on PreToolUse:Bash is unusual for context injection).

### PreToolUse Edit/Write path validator

Matcher `Write|Edit` runs a bash script that reads the tool-call payload via stdin + `jq`, denies writes to a protected path glob (`~/.config/<tool>/themes/`), and exits 2 with `permissionDecision: "deny"` + a `systemMessage` telling the user where to develop instead. Fail-closed posture. Pitfall: `input=$(cat)` has no timeout, so a stalled stdin can hang up to the PreToolUse default budget.

### PreToolUse Edit/Write risk advisor

Matcher `Edit|Write` runs a check script (`check-ehrb.sh --diff --dry-run`) gated on a state file's existence (`[ -f .sparv/state.yaml ] && ...`). The `|| true` suffix makes non-zero exits fail-open — the advisor never blocks, only annotates. Used for risk-of-modification surfacing without interrupting work.

### PostToolUse logging

Matcher `Write|Edit` (or broader `Edit|Write|Bash|Read|Glob|Grep`) logs the tool call to a journal file (`docs/<plugin>/changes.md` or per-session log). Hook produces no structured stdout; mutates files in the target project. Pitfall: broad matchers fire on every tool call and grow journals linearly with session work.

### PostToolUse git-commit detector

Matcher `Bash` fires on every bash call but internally filters for `git commit` substring before doing anything. On match, shells out to `git log` / `git diff-tree` to record commit hash, subject, and affected domains to a docs file. Lower-cost alternative would be a regex-over-command-string matcher if the platform supported it; current spec matches on tool name only.

### PostToolUse output sanitizer / context-poisoning advisor

Matcher `Bash` runs a Node script that parses tool-call stdout/stderr from JSON, scans for binary-leak indicators (long base64 blobs, low-ASCII clusters, inline SVG > 500 chars), and emits `{"additionalContext": "Warning: capture output contains binary/image data. Do NOT pipe through stdout..."}`. Does not gate or truncate the output itself — instructs the model to ignore it. Conversation-hygiene mechanism, not a security boundary. Top-level try/catch + 5-second stdin timeout swallow malformed input silently (fail-open).

## Session context loading

Hooks that inject context into the model's view at session start, prompt submit, or compact.

### SessionStart additionalContext injection

`SessionStart` hook with matcher `startup|resume|clear` reads a curated map file (`INDEX.md` + tail of `changes.md`) and emits `hookSpecificOutput.additionalContext`. Tight `timeout: 5` with `async: true` so the session does not block — context arrives late on slow disks rather than failing the session. Companion `PostCompact` hook re-injects the same context after compaction since `compact` is not a `SessionStart` sub-event.

### UserPromptSubmit prompt logger

`UserPromptSubmit` matcher runs a script per prompt — observed in one repo as a logger (`log-prompt.py`), not a context injector. Distinct from the SessionStart-based injection patterns.

### SessionStart for setup only (not context)

Hook fires on `*` matcher (or no matcher) and runs only the dependency installer / sanity check; no context emission. Context for the model arrives via the skill's preamble bash block when the skill is invoked, not via SessionStart.

## User configuration

Whether and how plugins expose runtime user configuration through `userConfig`.

### No userConfig

`plugin.json` declares no `userConfig` block. Plugins consume `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}` directly with hand-coded fallbacks (e.g. `CLAUDE_PROJECT_DIR ?? process.cwd()`). Some configuration leaks into a separate runtime config file the plugin's own binary reads (e.g. `~/.codeagent/models.json` for API keys) — outside Claude Code's config surface entirely.

### Custom env-var substitution in hooks.json

Hook command strings reference a non-platform variable like `${SKILL_PATH}` that the plugin expects its own runtime to populate. If Claude Code does not populate the variable, the command dereferences an empty string and the surrounding guard (`[ -f .sparv/state.yaml ] && ${SKILL_PATH}/scripts/...`) silently no-ops — fail-open hides missing-env misconfiguration.

## Plugin-to-plugin dependencies

Whether `plugin.json` declares dependencies on other plugins.

### No declarative dependencies

`dependencies` field absent from every plugin.json. No `{plugin-name}--v{version}` tag format; tags (when present) are flat repo-wide semver. Multi-plugin marketplaces are single-version where every plugin shares the same version string, or each plugin has its own version with no cross-plugin coupling declared.

### Implicit dependencies coded in installer

A self-installer hardcodes inter-module dependencies in source (`WRAPPER_REQUIRED_MODULES = new Set(["do", "omo"])` plus `WRAPPER_REQUIRED_SKILLS = new Set(["dev"])`) so selecting one module triggers `bash install.sh` for a shared binary. Not declarative; not visible to the marketplace consumer.

## Testing framework

The harness used for tests, when tests exist.

### go test

Standard Go test runner against a bundled Go binary subdir. `go test -v -cover -coverprofile=coverage.out ./...` plus `go tool cover -func=coverage.out` to print coverage. Coverage uploaded to codecov with `continue-on-error`. Coverage threshold not enforced.

### node:test with tsx loader

Node.js built-in test runner via `import { test } from 'node:test'` plus `node --import tsx/esm --test '<glob>'` for direct TypeScript execution. No third-party test framework. Pitfall: glob expansion under Windows bash may match zero files; CLAUDE.md documents an explicit-paths workaround.

### bats (Bash Automated Testing System)

`.bats` files in `tests/` exercising the plugin's CLI through bash assertions. Unit and e2e suites split into separate files; e2e requires `playwright install chromium` plus the plugin's env vars threaded through the runner.

### pytest (out-of-band Python side-project)

`pyproject.toml` + pytest for a Python utility that ships in the same repo but isn't a Claude Code plugin. Coexists with plugin tests in their own framework.

## CI

The presence and shape of GitHub Actions workflows for tests and validation.

### Push + PR matrix CI

`.github/workflows/ci.yml` triggers on `push` to default branch + release branches and `pull_request`. Matrix `os: [ubuntu-latest, windows-latest, macos-latest]` with a fixed runtime version (Go 1.21). Action pinning at tag level (`@v4`, `@v5`) — no SHA pinning. Built-in cache via the runtime's setup action's defaults.

### Single-job path-scoped CI for one plugin

Workflow scoped via `paths:` to one plugin's directory only — push/PR outside that path skips CI. Single `ubuntu-latest` runner, single Node version, no cache. Four chained jobs: syntax-check (node --check + JSON.parse on hooks/plugin/scripts manifests), unit-tests (bats), e2e-tests (bats with playwright + chromium installed), build-test (esbuild bundle exists and >1000 bytes — file-size threshold, not functional). Other plugins in the same marketplace get zero CI coverage.

### No CI

No `.github/workflows/` directory. Tests exist locally but only run on a contributor's machine. The declared version has no automated validation.

## Release automation

Workflow that runs on tag push to build artifacts and create a GitHub Release.

### Tag-triggered prebuilt-binary matrix

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`. Matrix builds a Go binary for 6 OS/arch combinations with `CGO_ENABLED=0` and `-ldflags="-X .../version=${VERSION}"` to stamp the version. Uploads all artifacts plus install scripts via `softprops/action-gh-release@v2`. Release notes generated inline via `git log ${PREVIOUS_TAG}..${TAG} --pretty=format:"- %s (%h)" --no-merges` — bypasses the project's CHANGELOG.md (git-cliff-maintained separately). No tag-sanity gates: no verify-tag-on-master, no verify-tag-matches-package-version, no tag-format regex.

### No release automation

No tags, no `release.yml`, no GitHub Releases. Installs pull HEAD of the default branch directly. Plugin version bumps live in commits with no corresponding release artifact.

## Marketplace validation

CI gates that lint or schema-check `marketplace.json` / `plugin.json` / `hooks.json` before merge.

### JSON well-formedness only

CI `syntax-check` job runs `node -e "JSON.parse(...)"` on `hooks.json`, `plugin.json`, and `scripts/package.json`. Catches malformed JSON; no schema conformance check, no event-name validation, no unknown-field detection.

### Runtime-only validation via jsonschema

`config.schema.json` exists in repo and a legacy installer (`install.py`) uses Python `jsonschema` to validate `config.json` at install-time on the user's machine. Not enforced in CI; a malformed config can be committed and only fails when a user runs the legacy installer.

### No validation

No CI, no schema files, no validators. Hook files using non-existent event names (e.g. `SubagentStart` rather than the documented `SubagentStop`) ship without complaint and never fire at runtime. `.md` files with frontmatter from a different tool's hook format coexist alongside Claude Code hooks and get treated as plugin hooks by humans even though Claude Code never executes them.

## Documentation

Required and optional doc files at root and per plugin.

### README.md at root and per plugin

Root `README.md` is the marketplace overview with per-plugin blurbs and install commands. Each plugin carries its own `README.md` covering value pitch, install instructions, command/skill listing. Bilingual variants observed (e.g. `README_CN.md` alongside `README.md`).

### CLAUDE.md at root or per plugin

Architecture-level operational doc covering build commands, build-system gotchas, hook protocol, env-var contract, supported-runtime list. Sometimes at repo root, sometimes only per-plugin, sometimes only at a `memorys/CLAUDE.md` subdirectory copied to the install target by the installer rather than read directly. Quality varies from minimal stub to highly detailed onboarding doc.

### CHANGELOG.md

Keep-a-Changelog format with emoji section markers (Features, Bug Fixes, Documentation, Refactor), generated by `git-cliff` via `cliff.toml` and a `make changelog` target. CHANGELOG dates can lag last-commit dates indicating manual regeneration. When absent (no CHANGELOG.md anywhere), the only way to see what changed in a version bump is to read commit history.

### docs/DESIGN.md and docs/SPEC.md

Architecture content lives in `docs/DESIGN.md` (~36 KB) and `docs/SPEC.md` (~22 KB) rather than a root `architecture.md`. Substantive design rationale, but a consumer following the "architecture.md at root" convention misses them.

### Joke badges and brand SVGs

Marketplace ships static SVG assets like `works-on-my-machine.svg` and `designed-in-ms-paint.svg` referenced via relative paths from every plugin's README. Marketplace-level branding through co-located assets. Persona-style READMEs may add animated typing-SVG headers and social-share buttons (X, Reddit, HN).

### LICENSE

Root `LICENSE` (e.g. AGPL-3.0 or MIT) governs the marketplace. When absent at root, GitHub API reports `license: null` even if individual plugin.json entries declare `"license": "MIT"` — repo is legally ambiguous despite the per-plugin claim. Per-plugin LICENSE files coexist with root LICENSE in some repos.

## Live monitoring and notifications

Whether plugins ship a `monitors.json` for live-sync surfaces.

### No monitors

`monitors.json` absent across every plugin. Live-sync needs are met instead by hooks (PostToolUse) and by MCP server `watchFile` calls (debounced internal cache invalidation, not a plugin-surface monitor).

## Distribution-channel novelties

Patterns unique enough to call out as their own role rather than fold into existing roles.

### Self-update advisory channel

Plugin script (`update-check.js`) hits `https://raw.githubusercontent.com/<owner>/<repo>/master/<plugin>/.claude-plugin/plugin.json` over the network, compares `.version` against the bundled value, caches the result in `~/.cache/<plugin>/update-check` with asymmetric TTLs (60 min for up-to-date, 720 min for available-update so a known update keeps surfacing for 12 h while a new release is detected within an hour). Emits `UPDATE_AVAILABLE <old> <new>` on stdout for the skill preamble to parse and surface to the user. Lightweight self-update notification that does not require marketplace infrastructure.

### Codex CLI co-distribution

Sibling directory in the same repo carries Codex-only artifacts (SKILL.md + `agents/openai.yaml`) installed via `cp -R ~/<repo>/<dir> ~/.codex/skills/` rather than `/plugin install`. Same git repo doubles as a Claude Code marketplace and a Codex skills bundle. Per-platform install instructions live in the README.

### `.codetographignore` plugin-private ignore file

Plugins that scan target-project source for indexing accept a plugin-private ignore file (`.codetographignore`) with `.gitignore` syntax that lets a project exclude paths from the plugin's scan without polluting `.gitignore`. Plugin-private ignore conventions add a parallel ignore namespace per plugin.

### Plugin-internal `.scm` query asset class

`scripts/queries/` holds per-language tree-sitter `.scm` query files loaded at runtime by an extractor module. Not a `skills/`, `agents/`, `hooks/`, or `commands/` component — an unconventional plugin-internal asset class shipping as data alongside executable code.

### MCP server reads hook-authored artifact

MCP server's tool surface is a projection of state authored by hooks: a hook (`stop.js`) writes `docs/<plugin>/map.md` via `atomicWrite` after parsing the project; the MCP server (`mcp/server.js`) parses that map and `watchFile`s it with a 500ms debounce. Decouples MCP responsiveness from heavy parsing cost — MCP doesn't parse source, it parses the rendered map. Cross-component data flow (hooks produce, MCP consumes) without RPC or shared-memory coupling.

### Hook-config stitching with module-tagged surgical unmerge

Self-installer merges per-module `hooks/hooks.json` into `~/.claude/settings.json` and tags every merged hook entry with `__module__: <module-name>`. Uninstall scans settings.json and removes only entries with the matching tag, leaving user-added hooks untouched. Surgical unmerge strategy worth naming as a pattern for installers that mutate global state.

### Operations DSL with restricted run_command

Self-installer's `config.json` defines modules as a sequence of typed operations (`copy_file`, `copy_dir`, `merge_dir`, `run_command`). `run_command` is restricted at the installer level to exactly `"bash install.sh"` — no arbitrary commands. Minimum-capability safeguard on a powerful primitive: the operation type is general but the registry only permits one specific invocation.

### Installed-modules status file

`~/.claude/installed_modules.json` tracks what was installed with timestamps and per-operation results. Used by `--update` to detect which modules to re-install and by `uninstall` to know what to remove. Durable state file separate from Claude Code's own settings, acting as the installer's source of truth for what it has done to the user's machine.

### Auto-shell-rc modification

`install.sh` detects user shell and writes PATH-append lines to shell rc files (`bashrc`, `zshrc`) with idempotency guards. Crosses the line from "install under `~/.claude`" to "modify user dotfiles" — most plugin-era patterns avoid this because plugin uninstall cannot reliably reverse the shell-rc edits.

### Post-install detection report

Installer runs `which <each-tool>` (`which codex`, `which claude`, `which gemini`, `which opencode`) and reports status with `✓`/`✗` markers, plus detects whether `~/.claude/bin` is in `$PATH`. User-friendly telemetry without phone-home — diagnostic on the user's machine only.

### Dual installer (legacy + current)

`install.py` (Python, 1,533 lines, uses `jsonschema`) and `bin/cli.js` (Node, 1,285 lines, the new blessed path) coexist. The shell wrapper prints a 5-second warning banner directing users to the npx path. Migration-in-progress visible in repo structure — a marker that the project is mid-replacement of its own infrastructure.

### TypeScript-compiled hooks with hand-patched imports

Post-`tsc` distribution step (`scripts/copy-hooks.js`) mirrors `dist/` into `hooks/dist/` + `mcp/dist/` + `scripts/` and rewrites relative imports (`'../xxx'` → `'./dist/xxx'`, etc.) so hook entry points stay plain `.js` invokable by `node` while pulling shared code from a co-located `dist/` tree. Avoids both a runtime TS loader in hooks and a bundler. Build-system gotcha called out: "Always run `npm run build:hooks` (not just `npm run build`)".

### Cool-off window on event-driven regeneration

`hooks/stop.js` skips map regeneration if the output file's mtime is within the last 60s, to avoid redundant work when a manual refresh just ran. Explicit de-dup window for event-driven artifact regeneration.

### WASM-over-native with graceful fallback

Tree-sitter parsers loaded via `web-tree-sitter` (WASM) so no native compilation needed for grammars. Only `better-sqlite3` requires native; on native failure, code falls back to a JSON file cache with identical semantics (slower for large repos). Install script exits 0 even when the native build fails, treating native as an optimization rather than a requirement.
