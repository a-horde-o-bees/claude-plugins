# Sample

Mirrors of `https://github.com/tretuttle/AI-Stuff`. Aggregator marketplace shipping five unrelated plugins (personas, theme generator, browser-capture, project-recon, parkpal-content) plus a Codex-only skill (`codex-session-export`) and a standalone Python side-project (`recon-wrapper/`). Default branch `master`, 1 star, last commit 2026-04-14 (`acfbd1d` — "feat(recon-wrapper): frontend-agnostic HTTP/SSE API + repo .gitignore"); sample origin: dep-management (browser-capture's Playwright+Chromium installer). From root README opening: "A Claude Code plugin marketplace by tretuttle."

## Marketplace manifest layout

### Multi-plugin owned-aggregator marketplace

`/.claude-plugin/marketplace.json` at repo root lists all five plugins (`omarchy-theme`, `browser-capture`, `persona`, `project-recon`, `parkpal-content`), each authored by the owner and sourced via relative path `./<dir>`. Top-level fields are `name` (`ai-stuff`) and `owner.name` only — no `metadata.{description, version, pluginRoot}` wrapper, no top-level `description`, no marketplace-level `version`.

### Nested mini-marketplace inside a plugin directory

A second `persona/.claude-plugin/marketplace.json` lives inside the persona plugin and lists only `persona` with `"source": "."` — making `persona/` independently installable as its own mini-marketplace. The nested entry's `version: "1.0.0"` already lags the plugin's own `plugin.json: "1.1.1"`.

## Plugin source binding

### Relative source pointing to subdirectory

Every entry uses `"source": "./<dir>"`; persona's nested marketplace uses `"source": "."`. No `git-subdir`, no `url`, no `npm` source kind.

### `strict` field default

`strict` is absent on every entry (implicit `true`). No `skills` override on any entry.

## Per-plugin discoverability metadata

### Mixed-by-origin metadata

Different field sets per plugin entry in one `plugins[]` array — no uniform shape across siblings:

- `omarchy-theme` — description only (no version, no keywords, no author)
- `browser-capture` — description + version (`1.1.0`) + author + keywords (11 keywords)
- `persona` — description only
- `project-recon` — description + version + author + keywords (5 keywords)
- `parkpal-content` — description + version + author + keywords (6 keywords)

None use `category`, `tags`, or `categories`.

### `$schema` absence on per-plugin manifests

`$schema` absent on `marketplace.json` and on every `plugin.json`.

## Version coordination

### Dual-file version (manifest pair)

`browser-capture`, `project-recon`, `parkpal-content` carry a `version` string in both the marketplace entry and `plugin.json`. Already mismatched on `persona`: nested marketplace declares `"version": "1.0.0"`, plugin.json declares `"1.1.1"`. Marketplace-level `version` itself is absent.

## Channel distribution

### No pinning surface

No tags (`gh api repos/tretuttle/AI-Stuff/tags` returns `[]`), no release branches, no marketplace channel split. Users install via `/plugin install <name>@ai-stuff` and get whatever HEAD of `master` happens to be.

### Marketplace-cache invalidation hack

`plugin.json.version` is hand-bumped within feature commits explicitly for cache invalidation. Commit message `chore(project-recon): bump to 1.2.0 for cache bust` documents the version field operating as a refetch trigger for downstream `/plugin update` rather than as a release coordinate.

## Tag and release lifecycle

### No tags at all

Zero tags in the repo. Branches observed: `master`, `copilot/sub-pr-2`, `feat/persona-plugin`, `feat/persona-plugin-pr` — feature branches, not release branches. Plugin.json versions advance through hand-edits (`1.1.0`, `1.1.1`, `1.2.0`, `1.0.0`) with no tag anchoring; commits like `chore(project-recon): bump to 1.2.0 for cache bust` indicate version bumps used as cache-invalidation levers.

## Plugin-component registration

### Default convention discovery

None of the five `plugin.json` files declare a `components` object, `skills` path array, `commands` path array, `hooks` path, `agents` path, or `mcpServers`. Every plugin relies on Claude Code's default layout discovery (`skills/`, `commands/`, `agents/`, `hooks/hooks.json`).

### Hooks-json with broad event coverage

`persona/hooks/hooks.json` uses `SubagentStart`/`SubagentStop` event names. `SubagentStart` is not in the canonical list of documented Claude Code events (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`, `Notification`, `Stop`, `SubagentStop`, `PreCompact`, `PostCompact`, `SessionStart`, `SessionEnd`) — declares an event the runtime may not emit, with no documented version-floor.

### Empty hooks scaffolding

`parkpal-content`'s `hooks/` directory contains `hookify.require-schema-validation.local.md` and `hookify.warn-trivia-firewall.local.md` — frontmatter fields like `event: stop`, `event: file`, `conditions:`, `pattern:` — these are not Claude Code `hooks.json` format. They look like a separate tool ("hookify") the author uses; Claude Code will not execute them. The `.local.md` suffix and plugin layout imply the author intends them as plugin-shipped hooks but they won't fire.

## Component composition

### Skills (universal)

browser-capture, parkpal-content (×5), persona (×3), project-recon (×1), omarchy-theme (×1), codex-session-export (×1).

### Commands

browser-capture, project-recon, omarchy-theme.

### Agents

browser-capture, omarchy-theme, persona (×14 + template), project-recon. `codex-session-export` carries an `agents/openai.yaml` which is a Codex agent definition, not a Claude agent.

### Hooks

browser-capture, omarchy-theme, persona, parkpal-content (the parkpal `hookify.*.local.md` files don't fire under Claude Code).

### bin

`omarchy-theme/bin/.gitkeep` only — `setup.sh` populates `bin/hellwal` and `bin/tint` at first run.

### Composition shapes

Mixed across plugins: skills + agents (codex-session-export); skills + commands + hooks + bin (omarchy-theme); skills + commands + agents + hooks (browser-capture, project-recon); skills + agents + hooks (persona); skills (parkpal-content). No `.mcp.json`, no `.lsp.json`, no `monitors.json`, no output-styles in any plugin.

## Skill authoring conventions

### Mixed `allowed-tools` syntax

Different skills use different forms across the repo. browser-capture uses env-var threading from SKILL.md preambles; persona skills declare custom tool fields per-agent.

## Agent declaration conventions

### `model` + `effort` + `maxTurns` for cost control

`capture-analyst.md` (browser-capture): `name`, `description`, `model: sonnet`, `effort: medium`, `maxTurns: 30`.

### Standard fields plus model / color

`theme-generator.md` (omarchy-theme): `name`, `description`, `model: inherit`, `color: cyan`, `allowed-tools: Bash, Read, Write, Edit, WebFetch` (comma-delimited string form).

### Tool-restricted with orchestration knobs

`theprimeagen.md` (persona, representative): `name`, `description`, `tools: Read, Glob, Grep, Bash`, `disallowedTools: Write, Edit, NotebookEdit`, `memory: project`, `model: inherit`, `maxTurns: 10`.

### Plain tool-name list

`project-scout.md` (project-recon): `name`, `description`, `model: inherit`, `color: cyan`, `tools: ["Read", "Bash", "Grep", "Glob", "Write"]` (YAML list form).

Three syntactic variants for tool declarations coexist within one repo: comma-delimited string (`theme-generator`), bare comma list (`theprimeagen`), YAML list (`project-scout`). No `Bash(uv run *)`-style permission-rule syntax observed.

## Cross-platform skill publishing

### Per-skill Codex sibling marker

`codex-session-export/agents/openai.yaml` declares Codex-platform interface metadata alongside the SKILL.md. Repo doubles as a Claude Code marketplace and a Codex skills bundle.

### Codex CLI co-distribution

`codex-session-export/` is a sibling directory in the repo with its own SKILL.md and `agents/openai.yaml`. README explicitly says "For Codex-only skills, use the package README in this repo instead of `/plugin install`" and shows `cp -R ~/AI-Stuff/codex-session-export ~/.codex/skills/`.

## Bin entry mechanism

### `bin/.gitkeep` placeholder populated by setup

omarchy-theme's `bin/` directory is checked in with only `.gitkeep`; `scripts/setup.sh` populates `bin/<binary>` at first run by compiling C source (`cc -Wall -Wextra -O3 hellwal.c -o bin/hellwal`) and downloading prebuilt tarballs. Linux/x86_64 hardcoded — porting to other platforms requires script edits. browser-capture has no `bin/` directory; invocation is via `node "$bundled_or_source.js"` with env-var threading (`NODE_PATH`, `PLAYWRIGHT_BROWSERS_PATH`, `CLAUDE_PLUGIN_DATA`) at every invocation point. omarchy-theme's shell scripts (`check-dependencies.sh`, `validate-theme-path.sh`) are invoked directly via `${CLAUDE_PLUGIN_ROOT}/hooks/<script>.sh` (executable). browser-capture scripts are `.js` invoked via `node`.

### No bin entry / direct invocation

browser-capture's executable surface flows entirely through skills, hooks, and `node` invocations against `.js` files inside the plugin tree.

## Dependency installation

### Browser-bundle install alongside node_modules

`plugins/browser-capture/scripts/install-deps.js` installs both `node_modules` (via `npm install --production`) and Playwright Chromium (~170 MB via `npx playwright install chromium`) under `${CLAUDE_PLUGIN_DATA}` with `PLAYWRIGHT_BROWSERS_PATH=<data>`. `verifyBrowser()` actually launches a headless instance and closes it before declaring success — catches broken downloads that pure file-existence would miss. SessionStart 300-second timeout is the hard ceiling; `npm install` has a 120 s internal timeout, `playwright install chromium` has a 240 s internal timeout — totaling 360 s in the worst case. On a cold first-run with slow network, the hook is killed before internal timeouts fire.

### Hard-coded versions in install script

omarchy-theme's `scripts/setup.sh` builds hellwal from a hardcoded version (`HELLWAL_VERSION="1.0.7"`) — no update mechanism; users get whatever was pinned at commit time. Hooks reference `${CLAUDE_PLUGIN_ROOT}/bin/<binary>` directly (no PATH discovery). Linux/x86_64 hardcoded — `tint_linux_x86_64.tar.gz` downloaded directly; `cc` invocation for hellwal compile. Native binaries install into `${CLAUDE_PLUGIN_ROOT}/bin/` (the plugin directory itself, not the data dir). omarchy-theme has no `package.json`/`requirements.txt`/`Cargo.toml`/`go.mod` manifest — `setup.sh` is the entire dep declaration. omarchy-theme's bash scripts use `set -euo pipefail`-style strict failure; the dependency hook emits `{"systemMessage": "…"}` JSON when binaries are missing (advisory, no exit-2 gate).

### SessionStart hook → npm install local to plugin

browser-capture's `install-deps.js` runs `npm install --production` reading `plugins/browser-capture/scripts/package.json` (`playwright ^1.58.2`, `js-beautify ^1.15.4`, `better-sqlite3 ^11.7.0`) and writes `node_modules` into `${CLAUDE_PLUGIN_DATA}`. Sha256 hash of the bundled `scripts/package.json` vs the cached copy in `${CLAUDE_PLUGIN_DATA}/package.json` short-circuits when they match (see *Install change detection*). `install-deps.js` uses a top-level try/catch, writes human-readable `[browser-capture] …` lines to stderr, and exits non-zero on fatal failure (see *Install failure posture*). The `.install-ok` marker JSON records `node: process.version` and `platform: process.platform` — but the hash-based `depsUpToDate()` check does not read these fields, so a Node major version change or platform switch does not trigger reinstall (the fields are informational only).

### Coexisting redundant install paths

browser-capture has a split install responsibility: SessionStart hook installs `node_modules` + Chromium, but the skill preamble runs `scripts/build.js` which calls its own `ensureDeps()` and `ensureChromium()` if the bundle is missing. Two install paths for the same deps. `build.js` writes `${PLUGIN_DATA}/package.json` with esbuild added to dependencies; next SessionStart's `fileHash(bundledPkg) === fileHash(cachedPkg)` is then false, triggering a full reinstall — observed bug from the interaction of two install paths managing the same manifest.

## Install change detection

### sha256 of manifest + post-verify marker

browser-capture's `depsUpToDate()` checks BOTH (a) sha256 hash of the bundled `scripts/package.json` against the cached copy in `${CLAUDE_PLUGIN_DATA}/package.json`, AND (b) an `.install-ok` marker file. The marker is deleted before install starts and only rewritten after `verifyBrowser()` (a real headless Chromium launch) succeeds. Marker JSON also records `{version, hash, timestamp, node, platform}`. A partial install (manifest copied but install crashed, or Chromium launch failed) leaves the cached manifest matching but the marker absent — next-session check sees marker missing and retries from a clean state. The failure branch in the outer try/catch also wipes the cached manifest for redundant safety. Strongest atomicity posture.

### Existence-only check

omarchy-theme uses `[ ! -x "${BIN_DIR}/hellwal" ]` — once the binary is present, the install hook never replaces it. Upgrades require manual cache wipe.

## Install trigger and lifecycle

### SessionStart direct invocation

browser-capture's SessionStart hook invokes `install-deps.js` synchronously with `"timeout": 300` bounding the worst case. omarchy-theme's SessionStart `check-dependencies.sh` reports missing binaries but does not run install — the user runs `setup.sh` manually.

### Skill preamble lazy build

browser-capture's skill preamble (the bash block at the top of SKILL.md) runs `update-check.js` and `build.js` lazily on first skill use, separate from any hook. Defers heavy work (esbuild bundling) from session start to skill activation. The lazy builder mutates `package.json` in the data dir to add esbuild, which then defeats the sha256 staleness check the SessionStart installer relies on.

## Install failure posture

### Pre-delete the marker so failure is structurally visible

`install-deps.js` removes `.install-ok` BEFORE starting and only writes it after `verifyBrowser()` succeeds. `depsUpToDate()` checks both marker presence AND hash equality, so a partial install (where `package.json` was copied but playwright crashed mid-install, or where chromium failed to launch) leaves `cachedPkg` present but `.install-ok` absent — next session's `depsUpToDate()` returns false and retries. The failure branch in the outer try/catch also deletes `cachedPkg` for redundant safety. `verifyBrowser()` returning false skips the `writeFileSync(installMarker, …)` call, so the marker is not written on verification failure (comment in code: "Don't write marker so next session retries").

### Multi-layer fail-open with stderr advisory

omarchy-theme's `check-dependencies.sh` always exits 0 regardless of missing deps; emits `{"systemMessage": "…"}` JSON with corrective install guidance. No autonomous repair path — user must run `setup.sh` manually.

## User configuration and authentication

### No user-supplied config

No `userConfig` in any plugin.json. Plugins consume `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` heavily in hooks and commands. No `${user_config.*}` substitutions anywhere.

## Tool-use enforcement

### PreToolUse Edit/Write path validator

omarchy-theme's `Write|Edit` matcher runs `validate-theme-path.sh`. The bash script reads the tool-call payload via stdin + `jq`, denies writes to a protected path glob (`~/.config/omarchy/themes/`, `~/.local/share/omarchy/`), and exits 2 with `permissionDecision: "deny"` plus a `systemMessage` telling the user where to develop instead. Fail-closed posture. Pitfall: `input=$(cat)` has no timeout, so a stalled stdin can hang up to the PreToolUse default budget. Regex patterns also ambient-match any `Bash` command mentioning the omarchy plugin directory.

### PostToolUse output sanitizer / context-poisoning advisor

browser-capture's `Bash` matcher runs `sanitize-output.js` — parses tool-call stdout/stderr from JSON, scans for binary-leak indicators (long base64 blobs `/data:[^;]+;base64,[A-Za-z0-9+/=]{100,}/`, low-ASCII clusters `/[\x00-\x08\x0e-\x1f]{10,}/`, inline SVG > 500 chars), and emits `{"additionalContext": "[browser-capture] Warning: capture output contains binary/image data. Do NOT pipe _metadata.json or captured files through stdout..."}` to warn the agent off poisoning the conversation context. Does not gate or truncate the tool output itself — instructs the model to ignore it. Conversation-hygiene mechanism, not a security boundary. Top-level try/catch + 5-second stdin timeout swallow malformed input silently (fail-open).

## Hook output contract

### Stderr for human display + stdout JSON for harness

Stdout JSON for hook-specific output (`permissionDecision`, `additionalContext`, `systemMessage`); stderr for human-readable logs (`[browser-capture] …`). Mixed per hook.

## Hook failure posture

### Mixed posture (fail-closed for security, fail-open for context)

`validate-theme-path.sh` — fail-closed (exit 2 + permissionDecision deny). `sanitize-output.js` — fail-open silent (top-level try/catch around JSON.parse swallows malformed input; stdin timeout exits 0 after 5 s). `check-dependencies.sh` — fail-open with systemMessage (always exits 0 regardless of missing deps).

## Session context loading

### Dependency install only (no context emission)

browser-capture's SessionStart hook only handles dep install; no `additionalContext` emission. omarchy-theme's SessionStart only reports missing deps via `systemMessage`. `additionalContext` is used only on PostToolUse (sanitize-output.js).

## SessionStart matcher scope

### Empty matcher (all sub-events)

browser-capture uses no matcher (fires on all SessionStart sub-events). omarchy-theme uses `"matcher": "*"` (same effective behavior, explicit wildcard).

## Live monitoring

### `monitors.json` absent

No `monitors.json` in any plugin.

### Update notification mechanism

browser-capture's skill body opens with a `## Preamble (run ONCE when skill is invoked)` block that the agent shells out on, invoking `bin/<plugin>-update-check`-equivalent (`update-check.js`). The script polls a release endpoint, writes a status cache with TTL, and emits `UPGRADE_AVAILABLE`/`JUST_UPGRADED`/nothing. Sentinel files in the data dir (`last-update-check`, `update-snoozed`, `just-upgraded-from`) coordinate state.

### Self-update advisory channel

Asymmetric cache TTL: 60 min for up-to-date, 720 min for available-update — once an update is known to exist, the cache keeps that signal for 12 h while a freshly-published release surfaces within the hour. Lightweight self-update notification that does not require marketplace infrastructure.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `plugin.json` declares the schema-level `dependencies` field. Tags are absent so the `{plugin-name}--v{version}` form is moot. The five plugins are functionally independent (no shared libraries across plugins, no cross-plugin skill calls).

## Testing

### bats (Bash Automated Testing System)

`plugins/browser-capture/tests/` contains `capture-cli.bats`, `e2e-capture.bats`, `health-check.bats`, `sanitize-output.bats`, `update-check.bats`, plus `fixtures/basic.html` and `test_helper.bash`. e2e requires `playwright install chromium` plus the plugin's env vars threaded through the runner.

### pytest with optional inline cov

`recon-wrapper/pyproject.toml` configures pytest for the side-project (not a plugin).

### No tests

No tests for omarchy-theme, persona, project-recon, parkpal-content, or codex-session-export.

## CI workflow shape

### Single-job path-scoped CI for one plugin

`.github/workflows/browser-capture-tests.yml` — only CI workflow in the repo. Triggers `push` and `pull_request` scoped via `paths:` to `plugins/browser-capture/**` and the workflow file itself. Single `ubuntu-latest` runner, single Node version (`20`). Four chained jobs by `needs:`: `syntax-check` (`node --check` on every JS file, `JSON.parse` validation of `hooks.json`, `plugin.json`, `scripts/package.json`); `unit-tests` (`npm install -g bats` then runs the 4 unit bats files); `e2e-tests` (`npm install --production`, `npx playwright install chromium`, `npx playwright install-deps chromium`, runs `e2e-capture.bats` with `CLAUDE_PLUGIN_ROOT` and `CLAUDE_PLUGIN_DATA` wired to the workspace); `build-test` (installs esbuild, runs `scripts/build.js`, verifies output bundle exists and is larger than 1000 bytes — file-size threshold, not functional). Other plugins in the same marketplace get zero CI coverage.

### Action-pinning conventions

`actions/checkout@v4`, `actions/setup-node@v4` — tag-pinned, not SHA-pinned. No `cache: 'npm'` configured — every CI run re-downloads all npm deps (playwright + chromium ~300 MB on every e2e run).

## Marketplace validation

### JSON well-formedness only

CI `syntax-check` job runs `node -e "JSON.parse(...)"` on `hooks.json`, `plugin.json`, and `scripts/package.json` (browser-capture's files only). No marketplace-wide validation. The `persona/hooks/hooks.json` (with non-existent `SubagentStart` event) and the parkpal `hookify.*.local.md` files (not Claude Code hook format at all) would not be caught by any validator.

## Release automation

### No release automation / manual

No `release.yml`, no tags, no GitHub Releases. Plugin versions in `plugin.json` and marketplace entries are hand-bumped with commit messages like `chore(project-recon): bump to 1.2.0 for cache bust` — version bump used to force consumer `/plugin update` to refetch rather than to mark an actual release. No `CHANGELOG.md` anywhere in the repo.

## Documentation surface

### Repo-root README only (no per-plugin)

Repo-root `README.md` (~5.4 KB) — marketplace overview with per-plugin blurbs and install commands. (Per-plugin READMEs do exist for each plugin, but the marketplace surface treats the root as authoritative for the multi-plugin index.)

### Per-plugin README mixed coverage

Per-plugin READMEs present: browser-capture (~7.3 KB), omarchy-theme (~5.4 KB), persona (~12.4 KB), project-recon (~5 KB), parkpal-content (~4 KB), codex-session-export (~3 KB). Plus `recon-wrapper/README.md` (~3.6 KB, side project).

### CLAUDE.md at root or per plugin

Per-plugin only. `persona/CLAUDE.md` (~11 KB, uses `<!-- GSD:… -->` markers suggesting a "Get-Stuff-Done" templating convention) and `parkpal-content/CLAUDE.md` (~4 KB). No root CLAUDE.md, none in the other plugins. persona's CLAUDE.md contains `<!-- GSD:project-start source:PROJECT.md -->` markers — a third-party templating system that synthesizes CLAUDE.md from other source files; the source files (PROJECT.md, research/STACK.md) don't appear in the repo.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` anywhere. No root `architecture.md`; persona has `persona/docs/ARCHITECTURE.md` only.

### Joke badges and brand SVGs

`/assets/works-on-my-machine.svg` and `/assets/designed-in-ms-paint.svg` referenced via relative paths from every plugin's README. Marketplace-level branding through co-located static assets. persona README adds animated typing-SVG header and social-share buttons (X, Reddit, HN).

## License declaration

### LICENSE declared in manifests, no LICENSE file

`license: "MIT"` in individual `plugin.json` files but no `LICENSE` file at repo root — GitHub API reports `license: null` because there's no root LICENSE file. `omarchy-theme/LICENSE` is the only LICENSE file present (MIT, plugin-scoped only). Repo is legally ambiguous despite per-plugin claims.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md` anywhere.

## Cross-platform discipline

### POSIX-only with no Windows story

omarchy-theme is Linux-first: `setup.sh` downloads `tint_linux_x86_64.tar.gz` (hardcoded Linux/x86_64) and compiles hellwal with a plain `cc` invocation. No Windows code path. browser-capture scripts are `.js` invoked via `node` so they're more portable but tested only on `ubuntu-latest`.

## Novel and cross-cutting concerns

### Generated-package.json pattern

browser-capture's `build.js` mutates the cached `${CLAUDE_PLUGIN_DATA}/package.json` to add esbuild as a dep at first skill use. Defeats the sha256 staleness check the SessionStart installer relies on, since the next session sees mismatched manifests and re-runs the entire install.

### Cool-off window on event-driven regeneration

browser-capture's update-check uses asymmetric TTL caching (60 min up-to-date / 720 min update-available) to bound how often the GitHub raw endpoint is polled per skill invocation.

## Cross-role tools

### Node + npm + npx

Node fills the entire browser-capture install pipeline (`install-deps.js`, `update-check.js`, `build.js`, `sanitize-output.js`); plugin runtime (`scripts/capture.js`, `cookie-import.js`); test runner via `bats` (Node not used as test runner, but `npm install --production` and `npx playwright install chromium` are install primitives).

### bash

omarchy-theme's `check-dependencies.sh`, `validate-theme-path.sh`, `setup.sh`. The browser-capture test suite is bats (Bash Automated Testing System).

### Python (stdlib + pip + uv)

`recon-wrapper/` (a Python side-project, not a plugin) uses pytest via `pyproject.toml`.

### `${CLAUDE_PLUGIN_ROOT}` env var

Used by browser-capture's hooks (commands resolve via `node "${CLAUDE_PLUGIN_ROOT}/<script>.js"`) and omarchy-theme's hooks (`${CLAUDE_PLUGIN_ROOT}/hooks/<script>.sh`, `${CLAUDE_PLUGIN_ROOT}/bin/hellwal`).

### `${CLAUDE_PLUGIN_DATA}`

Install destination for browser-capture's `node_modules` and Chromium browser; `.install-ok` marker file location; cached `package.json` location.

### `hookSpecificOutput.additionalContext`

Used by browser-capture's PostToolUse `sanitize-output.js` to emit a binary-data-warning advisory to the agent.
