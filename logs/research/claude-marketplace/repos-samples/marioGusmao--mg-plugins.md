# Sample

Mirrors of `https://github.com/marioGusmao/mg-plugins`. Multi-plugin marketplace bundling code intelligence, quality guardrails, documentation tools, and protocol routing — five plugins (`ai-quality-guardrails`, `claude-utils`, `codegraph`, `kdoc`, `router-plugin`) aggregated under one `marketplace.json`.

## Marketplace manifest layout

### Single root manifest with relative source under `plugins/<name>/`

A single `.claude-plugin/marketplace.json` lives at repo root with five entries, each `"source": "./plugins/<name>"`. Top-level fields: `{name, description, owner, plugins}` with `owner: {"name": "Mario Silva Gusmao"}`. No `metadata` wrapper, no `metadata.pluginRoot`, no `$schema`.

## Plugin source binding

### Relative source pointing to subdirectory

All five entries use `"source": "./plugins/<name>"`. No `strict` field (implicit true). No `skills` override — each plugin's own `plugin.json` carries `"skills": "./skills/"` directory pointer, not the marketplace entry.

## Per-plugin discoverability metadata

### Category + tags pair

Four of five plugins carry `category: "development"` and 5–7 keywords each on their marketplace entries. `kdoc` ships with empty `keywords: []` despite carrying the same `category`. No `tags` field used.

### `$schema` absence on per-plugin manifests

`$schema` absent on `marketplace.json`; per-plugin `plugin.json` files carry no `$schema` either.

## Version coordination

### Multi-site sprawl (5+ locations)

Versions live in `marketplace.json` entries, each plugin's `plugin.json`, and (for two plugins) the plugin's own `package.json`. Marketplace entries record `codegraph: 1.1.22, kdoc: 1.0.38, claude-utils: 1.0.19, ai-quality-guardrails: 0.1.18, router-plugin: 1.0.8`; the first four match their `plugin.json`. `router-plugin/package.json` declares `"version": "0.1.0"` while `router-plugin/.claude-plugin/plugin.json` and the marketplace entry both say `1.0.8` — the npm `package.json` was created and never re-synced. The sidecar `capabilities.json` files (see Plugin-component registration) carry their own `version` field that drifts independently — `codegraph` plugin.json `1.1.22`, `capabilities.json` `1.1.18`.

## Channel distribution

### No pinning surface

Single `main` branch, zero tags (`gh api tags` returns empty), zero releases. Consumers implicitly track `HEAD` of `main` or pin via commit SHA. No stable/latest split, no release branches, no pre-release suffixes. Recent commits are entirely `chore: sync codegraph vX.Y.Z, kdoc vA.B.C, claude-utils vP.Q.R` batches that bump multiple plugin versions at once — no way to pin one plugin without pinning the whole marketplace to a specific commit.

## Tag and release lifecycle

### No tags at all

`gh api tags` returns an empty list. Single `main` branch. All 27 commits are upstream-sync chores; the aggregator has no independent release identity.

## Plugin-component registration

### Mixed (paths + auto-discovery)

Mixed reference style across plugins. `codegraph` uses directory pointer `"skills": "./skills/"` plus external file `"mcpServers": "./mcp/mcp.json"` (no hooks field — auto-discovered via `hooks/hooks.json` convention). `kdoc` uses directory pointer `"skills"`, file pointer `"mcpServers"`, and explicit `agents` array listing four files. `ai-quality-guardrails` uses directory pointer `"skills"` plus explicit `agents` array. `claude-utils` declares no component fields and relies entirely on convention discovery (hooks/, skills/, scripts/). `router-plugin` declares only `"skills"`.

### Custom sidecar manifest

Every plugin ships `.claude-plugin/capabilities.json` alongside `plugin.json` with a non-standard schema: `{plugin, version, schema_version: "1.0.0", capabilities: [{id, name, type: "skill"|"agent"|"mcp_tool"|"hook", applicable_phases: ["plan"|"implement"|"review"|"fix"|"docs"|"cross_phase"], guidance, anti_patterns: [...], priority: 1-10}]}`. Not part of the official Claude Code plugin spec. Likely consumed by the sibling `router-plugin` for capability selection based on `applicable_phases` plus `priority`. The `capabilities.version` field drifts independently from `plugin.json.version`.

## Component composition

### Skills (universal)

All five plugins ship skills under `skills/<name>/SKILL.md`.

### Agents

`ai-quality-guardrails` declares top-level `agents/`. `kdoc` ships agents under `agents/claude-code/` plus `agents/codex/`. Every skill across every plugin also carries a sibling `skills/<name>/agents/openai.yaml` (Codex interop marker).

### Hooks

`codegraph`, `kdoc`, and `claude-utils` ship hooks via `hooks/hooks.json`.

### MCP servers

`codegraph` and `kdoc` each ship `mcp/mcp.json`, referenced from `plugin.json` via `"mcpServers": "./mcp/mcp.json"`.

### bin

`codegraph/package.json` declares `"bin": {"codegraph": "./dist/cli/index.js"}` and `router-plugin/package.json` declares `"bin": {"router-plugin": "./src/cli.js"}`. No `bin/` directory at any plugin root; npm-style bin entries only.

## Skill authoring conventions

### Standard frontmatter

Skills use standard frontmatter; `allowed-tools` not retrieved verbatim across all five plugins.

## Agent declaration conventions

### Tool-restricted with orchestration knobs

Sample `ai-quality-guardrails/agents/explorer.md` declares: `name`, `description` (with embedded `<example>` XML blocks), `model: sonnet`, `color: cyan`, `tools: Read, Grep, Glob, WebFetch, WebSearch`, `disallowedTools: Write, Edit, NotebookEdit`, `maxTurns: 30`. Uses `disallowedTools` as negative list. No permission-rule syntax (no `Bash(...)` wildcards).

### Plain tool-name list

`tools: Read, Grep, Glob, WebFetch, WebSearch` — comma-separated scalar string of bare tool names.

## Cross-platform skill publishing

### Per-skill Codex sibling marker

Every skill across every plugin carries a sibling `skills/<name>/agents/openai.yaml` Codex interop marker (e.g., `interface: {display_name, short_description}`, `policy: {allow_implicit_invocation: true}`). The parent `ai-quality-guardrails/plugin.json` simultaneously carries Claude-Code-specific top-level `agents/` plus these per-skill Codex markers — cross-platform skill publishing inside a Claude plugin.

## Bin entry mechanism

### Stale hardcoded paths after rebrand

`router-plugin/package.json` declares `"bin": {"router-plugin": "./src/cli.js"}` but no `src/` directory exists in `plugins/router-plugin/` (tree contains only `.claude-plugin/`, `docs/`, `skills/`, `templates/`, `README.md`, `package.json`). The bin reference is vestigial — file was never committed or was dropped during a sync. Separately, `package.json` `version: 0.1.0` while `plugin.json` and marketplace entry both list `1.0.8` — the npm metadata diverged from authoritative versioning.

### Node-only with mcp.json invocation

`codegraph/package.json`'s `bin: codegraph → ./dist/cli/index.js` is invoked via `node "${CLAUDE_PLUGIN_ROOT}/dist/cli/index.js" mcp` from `mcp/mcp.json`, not as an executable shebang. No `bin/` directory ships at plugin root; no shell wrapper. Plugin runs entirely under Node.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Hooks resolve plugin root via a `resolve-root.mjs` helper that prefers `${CLAUDE_PLUGIN_ROOT}` and falls back to `__dirname`-based path math. MCP commands interpolate `${CLAUDE_PLUGIN_ROOT}` directly in `mcp/mcp.json` args.

## Dependency installation

### SessionStart-driven dual-runtime install (Python venv + Node modules)

Two install patterns observed across the marketplace. `codegraph` installs Node production dependencies (including native modules `better-sqlite3`, `tree-sitter`, `tree-sitter-typescript`, `tree-sitter-javascript`) at SessionStart. `kdoc` ships pre-built CLI in `cli/dist/` with vendored `node_modules/` committed in-tree under pnpm layout (`.pnpm/@esbuild+linux-x64@0.27.4/...`, a platform-locked bundle). No Python deps anywhere; manifest format is `package.json` + `package-lock.json`.

### Plugin data dir with symlink-out

`codegraph` installs into `${CLAUDE_PLUGIN_DATA}` then runs `ln -sfn $PLUGIN_DATA/node_modules $PLUGIN_ROOT/node_modules` so ESM `import` from the plugin's own source resolves without `NODE_PATH` hacks. Install lives in writable data dir, exposed back to plugin root via symlink. Install command is `npm install --omit=dev --ignore-scripts --no-audit --no-fund` — `--ignore-scripts` avoids `prepare`/`build` scripts that need source in plugin root, not data dir. `package.json` declares `"engines": {"node": ">=20 <26"}`.

### In-tree vendored node_modules

`kdoc` commits `node_modules/` (pnpm-managed deps including platform-specific native binaries like `@esbuild/linux-x64`) directly in the repo. No install step, but locks users to the committed OS/arch (Linux-x64 observed; other-arch coverage not verified). Inverse stance to codegraph's runtime-install.

## Install change detection

### Diff-based byte comparison of manifest

`codegraph`'s install hook runs `diff -q "$src_pkg" "$data_pkg"` on `package.json`. Drift triggers a full `npm install`.

### ABI marker for native modules

A separate `$PLUGIN_DATA/.node-abi` marker stores `process.versions.modules` (Node's `NODE_MODULE_VERSION` integer — `115` for Node 20, `127` for Node 22). On every SessionStart `current_abi="$(node -e 'process.stdout.write(process.versions.modules)')"` is compared against the saved marker; on mismatch the script runs `npm rebuild better-sqlite3 tree-sitter tree-sitter-typescript tree-sitter-javascript` (explicit enumeration — only native modules rebuild, not the whole tree) and writes the new ABI back. Two independent change-detection axes drive two distinct recovery actions: package.json drift → full reinstall; ABI drift → rebuild-only.

### Runtime-probe fallback

`session-start.mjs` runs `execFileSync('node', ['-e', 'require("better-sqlite3")'])` and pattern-matches `/NODE_MODULE_VERSION|was compiled against a different/` on the error message; on match it triggers the same `npm rebuild` inline as a recovery path. Marker-file detection catches the common case cheaply; runtime probe catches stale markers or corrupted installs.

## Install trigger and lifecycle

### SessionStart direct invocation

`codegraph` registers `hooks/install-deps.sh` against SessionStart with empty matcher `""` (matches all sub-events) and `timeout: 120000` ms.

## Install failure posture

### `rm` stamp on failure (retry next session)

`codegraph`'s install script uses `set -euo pipefail` to halt on unexpected errors; explicit failure branches `rm -f "$data_pkg" "$abi_marker"` then `exit 0` so the next SessionStart re-attempts the install. Failure messages prefixed `[CodeGraph]` go to stderr; no JSON `systemMessage`, no `continue: false`.

## User configuration and authentication

### No user-supplied config

No plugin declares `userConfig` in `plugin.json`. No `${user_config.*}` substitution, no `CLAUDE_PLUGIN_OPTION_*` env-var consumption observed in any hook, script, or mcp config.

### External config file owned by plugin

`kdoc`'s session-start hook reads project-rooted `.kdoc.yaml` (the user's project working directory) instead of declaring `userConfig`. Config lives with the project it configures.

## Session context loading

### SessionStart prints plain markdown to stdout

`claude-utils/scripts/git-context.sh` writes branch / recent-commits / uncommitted-changes to stdout as plain markdown. `kdoc/hooks/session-start.mjs` reads project `.kdoc.yaml` and writes a markdown summary of active knowledge areas. `codegraph/hooks/session-start.mjs` writes index-status / build-status / setup instructions. Three plugins compete for SessionStart output — agent sees a concatenated stream whose order depends on plugin-load order. `check-staleness.mjs` (a PostToolUse hook) emits bare `JSON.stringify({...})` with top-level fields rather than the `hookSpecificOutput.additionalContext` envelope.

## SessionStart matcher scope

### Per-hook differentiation within one plugin

`codegraph` mixes matchers: empty `""` for `install-deps.sh` (matches all sub-events including `compact`); `"startup|resume|clear|compact"` for `session-start.mjs`. `kdoc` uses `"startup|resume"`. `claude-utils` uses `"startup"` for most hooks, `"resume"` for a subset, `"startup|resume|compact"` for `git-context.sh`.

## Tool-use enforcement

### Hook-only enforcement (frontmatter is documentation)

Three PreToolUse hooks across the marketplace: `codegraph`'s `matcher: "Edit"` → `blast-gate.mjs`, `matcher: "Bash"` → `auto-index.mjs`; `kdoc`'s `matcher: "Bash"` → `pre-push-check.mjs`. Five PostToolUse hooks: `codegraph`'s `Edit` and `Write` both → `check-staleness.mjs`, `Bash` → `post-bash-reindex.mjs`; `claude-utils`'s `Skill` → `capture-event.sh skill.invoke`, empty-matcher catch-all → `capture-event.sh observation`. No `PermissionRequest` / `PermissionDenied` hooks. No `continue: false` anywhere — no hook actually blocks an edit; "blast radius warning" only injects context.

### PostToolUse for index/state maintenance

`codegraph` registers PreToolUse + PostToolUse on `Bash` with shared regex set `/\bgit\s+(pull|merge|rebase|checkout|switch|cherry-pick|reset|restore)\b/` plus `/\b(npm|pnpm|yarn)\s+install\b/` to invalidate / refresh the code index on commands that mutate the working tree. Gated on `existsSync(dbPath)` so first pulls don't spuriously create indexes.

### PreToolUse Bash matcher as ask-first guardrail

`kdoc/pre-push-check.mjs` hooks `PreToolUse` on `Bash` and parses the command string for `git push` patterns, then reports staleness of `governance-health.md`. Always exit 0 — reminder, not block. Uses the Bash-tool hook as a proxy for a git pre-push hook with explicit documentation that terminal pushes (outside Claude Code's tool channel) aren't covered.

### PostToolUse async telemetry + eval gate

`claude-utils`'s PostToolUse handlers (`capture-event.sh skill.invoke`, `capture-event.sh observation`) capture events to a JSONL spool at `~/.ai-sessions/spool/events.jsonl`.

## Hook handler runtime

### Node `.mjs` files invoked via `node`

All `.mjs` hook handlers (`blast-gate.mjs`, `auto-index.mjs`, `check-staleness.mjs`, `post-bash-reindex.mjs`, `pre-push-check.mjs`, `session-start.mjs`) invoked via `node`. Bash scripts (`install-deps.sh`, `capture-event.sh`, `git-context.sh`) at conventional `hooks/` and `scripts/` paths.

## Hook output contract

### Stderr for human display + stdout JSON for harness

Diagnostic stderr lines prefixed `[CodeGraph]` for human display; stdout carries `JSON.stringify({...})` from `check-staleness.mjs` for context injection. Mixed convention across the repo.

### `hookSpecificOutput.additionalContext` envelope versus bare top-level

`check-staleness.mjs` emits bare `JSON.stringify({...})` with top-level fields rather than nesting under `hookSpecificOutput.additionalContext`. Plain stdout is treated as context.

## Hook failure posture

### Fail-open with always-exit-0

Every hook in the marketplace exits 0 on every path. Every `.mjs` hook wraps stdin read plus JSON parse in `try { … } catch { process.exit(0); }`. `install-deps.sh` is `set -euo pipefail` but every failure branch still explicitly `exit 0` after `rm -f` of the marker files. `pre-push-check.mjs` carries an explicit comment contract: "exit code is ALWAYS 0 — this is a reminder, not a block". Uniform convention across the repo.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `plugin.json` declares a `dependencies` array of other plugins.

### Implicit via filesystem convention

`kdoc`'s session-start hook reads `~/.ai-sessions/spool/events.jsonl` and `claude-utils/capture-event.sh` writes to the same spool. Filesystem-convention coupling — kdoc's drift-warning feature silently degrades when claude-utils isn't installed. Not declared anywhere in either plugin's manifest.

## Live monitoring

### `monitors.json` absent

No plugin ships a `monitors.json`. `claude-utils` Stop and Notification hooks (`notify.sh`, `cleanup.sh`) substitute for desktop-notification monitors.

## Testing

### Tests referenced but absent in tree

`codegraph/package.json` declares `"test": "vitest run"` with `vitest ^3.0.0` devDep; `router-plugin/package.json` declares `"test": "node --test"`; `kdoc/package.json` delegates to `cd cli && pnpm test`. No `tests/` directory, no `*.test.*` files, no `__tests__/` directory committed in any plugin. Test scripts declared, sources stripped before sync from upstream.

## CI workflow shape

### No CI

`.github/` directory does not exist (`gh api repos/.../contents/.github` returns 404). No workflows, no Actions configuration.

## Marketplace validation

### No validation

No validation workflow. `marketplace.json` carries no `$schema`. Combined with absent CI, JSON syntax errors would ship to users undetected.

## Release automation

### No release automation / manual

Releases are implicit (commit to `main` = release). No `release.yml`, no tags, no GitHub Releases. CHANGELOG present only as `ai-quality-guardrails/docs/CHANGELOG.md` (Keep-a-Changelog format, manual entries `[0.1.0] - 2026-03-17 Added ...`).

## Documentation surface

### Layered repo / plugin / skill READMEs (uneven)

Repo-root `README.md` is short (~30 lines: install commands + plugin table). Per-plugin READMEs present for `ai-quality-guardrails`, `codegraph`, `kdoc`, `router-plugin`; absent for `claude-utils`. Architecture docs vary across plugins: `ai-quality-guardrails/docs/ARCHITECTURE.md` present; `codegraph` embeds rationale in `README.md` ("Why Hybrid Indexing", "Why SQLite", "Why symbol_uid"); `kdoc` ships `docs/superpowers/specs/` and `docs/superpowers/plans/` instead of architecture.md; `router-plugin` ships `docs/PROTOCOL.md`/`ADOPTION.md`/`CERTIFY.md`/`SCAFFOLD.md` — four topical specs. No root architecture.md, no root CHANGELOG.

### No CLAUDE.md

No `CLAUDE.md` at repo root or in any plugin.

## License declaration

### Repo-root LICENSE plus per-plugin duplicates

Root `LICENSE` (MIT, "Copyright (c) 2026 Mario Silva Gusmao"); `ai-quality-guardrails/LICENSE` also present (MIT). SPDX `MIT` declared in manifests.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, or badges. The marketplace ships hooks that gate `Edit` and `Bash` tool calls but no SECURITY.md.

## Source layout

### Single tree (plugin equals repo)

Single tree — the repo *is* the marketplace plus its five plugin subdirectories under `plugins/<name>/`. No dual-tree sync, no generated manifests.

## Author identity and provenance

### Personal-email owner address

`marketplace.json.owner: {"name": "Mario Silva Gusmao"}`. Personal-name owner.

## Cross-role tools

### Node + npm + npx

Node runtime everywhere. `npm install` in install hook (codegraph); pnpm vendored in tree (kdoc).

### `${CLAUDE_PLUGIN_ROOT}` env var

Used in `mcp/mcp.json` argument interpolation for codegraph's MCP launch.

### `${CLAUDE_PLUGIN_DATA}`

codegraph's install-deps target directory; symlinked back to plugin root.
