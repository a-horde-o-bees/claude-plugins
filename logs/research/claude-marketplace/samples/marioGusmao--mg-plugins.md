# marioGusmao/mg-plugins

## Identification

- **URL**: https://github.com/marioGusmao/mg-plugins
- **Stars**: 0
- **Last commit date**: 2026-04-20 (HEAD `531f5ea9`)
- **Default branch**: `main`
- **License**: MIT (SPDX: `MIT`; root `LICENSE` plus per-plugin `LICENSE` inside `ai-quality-guardrails/`)
- **Sample origin**: dep-management (observed: `plugins/codegraph/hooks/install-deps.sh` — `npm install` + native-module `npm rebuild` gated by `diff -q` on `package.json` and by a Node ABI marker)
- **One-line purpose**: Marketplace bundling code intelligence, quality guardrails, documentation tools, and protocol routing (root `README.md` tagline; `marketplace.json.description`: "Code intelligence, quality guardrails, documentation tools, and protocol routing").

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: top-level `{name, description, owner, plugins}`; no `metadata.{description,version,pluginRoot}` wrapper. `owner` is `{"name": "Mario Silva Gusmao"}`
- **`metadata.pluginRoot`**: absent (no `metadata` object)
- **Per-plugin discoverability**: `category` + `keywords` on every entry except `kdoc` (keywords `[]`). Values: `category: "development"` for all five; `keywords` non-empty for 4/5. No `tags` field observed
- **`$schema`**: absent
- **Reserved-name collision**: no (plugin names `ai-quality-guardrails`, `claude-utils`, `codegraph`, `kdoc`, `router-plugin` are all non-reserved)
- **Pitfalls observed**: `kdoc` ships with empty `keywords: []` — technically present but provides no discovery surface; other four plugins list 5-7 keywords each. Inconsistency across same marketplace hurts search.

## 2. Plugin source binding

- **Source format(s) observed**: relative only — every entry uses `"source": "./plugins/<name>"`
- **`strict` field**: default (implicit true) — field not set on any entry
- **`skills` override on marketplace entry**: absent (skills are declared inside each plugin's own `plugin.json` via `"skills": "./skills/"` directory pointer, not on the marketplace entry)
- **Version authority**: marketplace entry + `plugin.json` — both carry `version` and must match. Observed in sync: marketplace entries record `codegraph: 1.1.22, kdoc: 1.0.38, claude-utils: 1.0.19, ai-quality-guardrails: 0.1.18, router-plugin: 1.0.8` and the first four match their own `plugin.json`. **Drift observed**: `router-plugin/package.json` declares `"version": "0.1.0"` while `router-plugin/.claude-plugin/plugin.json` and marketplace entry both say `1.0.8` — the `package.json` was not kept in sync during the upstream release flow
- **Pitfalls observed**: Duplicate version declarations across `marketplace.json` + `plugin.json` + `package.json` without a single source of truth. Release cadence is "chore: sync codegraph vX, kdoc vY, …" commits (all 27 commits are sync-from-upstream bumps), so drift between marketplace-level and per-plugin-level strings depends on commit discipline alone.

## 3. Channel distribution

- **Channel mechanism**: no split — single `main` branch, users pin via commit SHA or default to `HEAD`
- **Channel-pinning artifacts**: absent (no stable/latest marketplace, no release branches, no tags at all — `gh api tags` returns empty)
- **Pitfalls observed**: Every consumer implicitly tracks `HEAD` of `main`. Because commits are "chore: sync …" batches that bump several plugin versions at once, there is no way to pin one plugin's version without pinning the whole marketplace to a specific commit.

## 4. Version control and release cadence

- **Default branch name**: `main`
- **Tag placement**: none — `gh api tags` returns empty list
- **Release branching**: none — single `main` branch only (`gh api branches` shows only `main`)
- **Pre-release suffixes**: none observed (no tags; `plugin.json` versions are plain semver, no `-rc`/`-beta`)
- **Dev-counter scheme**: absent. Versions bump real semver — e.g., `codegraph` at `1.1.22`, `kdoc` at `1.0.38` (high patch counts imply the upstream repos release frequently and this aggregator syncs each bump)
- **Pre-commit version bump**: no (version bumps are produced by upstream repos and imported by "chore: sync" commits; no hook observed here)
- **Pitfalls observed**: Zero tags + zero releases means no reproducible install target beyond commit SHAs. Recent commit history is entirely upstream-sync chores: `chore: sync codegraph v1.1.22, kdoc v1.0.38, claude-utils v1.0.19` (2026-04-20); the aggregator has no independent release identity.

## 5. Plugin-component registration

- **Reference style in plugin.json**: mixed per plugin:
    - `codegraph`: directory pointer `"skills": "./skills/"` + external file `"mcpServers": "./mcp/mcp.json"` (no hooks field — hooks auto-discovered via `hooks/hooks.json` convention)
    - `kdoc`: directory pointer `"skills"`, file pointer `"mcpServers"`, explicit `agents` array listing 4 files
    - `ai-quality-guardrails`: directory pointer `"skills"` + explicit `agents` array listing 4 files
    - `claude-utils`: no component fields at all — relies entirely on plugin auto-discovery (hooks/, skills/, scripts/)
    - `router-plugin`: directory pointer `"skills"` only
- **Components observed**: skills yes (all 5 plugins); commands no; agents yes (ai-quality-guardrails top-level, kdoc top-level under `agents/claude-code/` + `agents/codex/`, and every skill has a `skills/<name>/agents/openai.yaml` Codex marker); hooks yes (codegraph, kdoc, claude-utils); `.mcp.json` no — each plugin uses its own `mcp/mcp.json` pointed at by `mcpServers` field (codegraph, kdoc); `.lsp.json` no; monitors no; bin yes (package-json `bin` in codegraph and router-plugin); output-styles no
- **Agent frontmatter fields used** (sample: `ai-quality-guardrails/agents/explorer.md`):
    - `name`, `description` (with embedded `<example>` XML blocks), `model: sonnet`, `color: cyan`, `tools: Read, Grep, Glob, WebFetch, WebSearch`, `disallowedTools: Write, Edit, NotebookEdit`, `maxTurns: 30`
- **Agent tools syntax**: plain tool names, comma-separated (`tools: Read, Grep, Glob, WebFetch, WebSearch`). Uses `disallowedTools` as negative list. No permission-rule syntax observed (no `Bash(...)` wildcards)
- **Pitfalls observed**: Non-standard `.claude-plugin/capabilities.json` file per plugin (custom schema with `schema_version`, `capabilities[]`, `applicable_phases`, `priority`) — not part of the official plugin manifest. This is a **novel sidecar** (see §17). `claude-utils` plugin.json omits all component fields but relies on convention for hook/script discovery; the package works because hooks-dir convention is well-documented, but the missing explicit declarations make the plugin's surface invisible without reading the filesystem. Each skill carries a sibling `skills/<name>/agents/openai.yaml` (Codex interop marker) — Codex-specific fan-out inside a Claude plugin manifest.

## 6. Dependency installation

- **Applicable**: yes — `codegraph` installs Node production dependencies (including native modules `better-sqlite3`, `tree-sitter`, `tree-sitter-typescript`, `tree-sitter-javascript`) at SessionStart; `kdoc` ships pre-built CLI in `cli/dist/` with vendored `node_modules/` committed in-tree under pnpm layout
- **Dep manifest format**: `package.json` + `package-lock.json` (codegraph, kdoc, router-plugin). No Python/Rust/Go
- **Install location**: `${CLAUDE_PLUGIN_DATA}` for codegraph, then `ln -sfn $PLUGIN_DATA/node_modules $PLUGIN_ROOT/node_modules` — install lives in writable data dir, exposed back to plugin root via symlink so ESM import resolution works (plugin root is typically read-only managed space). kdoc takes the opposite approach — `node_modules/` committed directly into the plugin tree (pnpm `.pnpm/` layout visible under `plugins/kdoc/cli/node_modules/.pnpm/@esbuild+linux-x64@0.27.4/...`, a platform-locked bundle)
- **Install script location**: `plugins/codegraph/hooks/install-deps.sh` (referenced by `hooks/hooks.json` SessionStart with empty matcher `""`, timeout 120000 ms). kdoc has none — deps are pre-vendored
- **Change detection**: `diff -q "$src_pkg" "$data_pkg"` on `package.json` AND existence of `$PLUGIN_ROOT/node_modules` symlink AND separate Node-ABI marker `$PLUGIN_DATA/.node-abi` containing `process.versions.modules`. Two independent triggers: (a) package.json drift → full reinstall; (b) ABI drift → `npm rebuild` of native modules only
- **Retry-next-session invariant**: yes — on any failure the script `rm -f "$data_pkg" "$abi_marker"` so the next SessionStart re-attempts. `exit 0` keeps the hook non-blocking
- **Failure signaling**: `set -euo pipefail` halts on unexpected errors; explicit failure branches write human-readable stderr messages prefixed `[CodeGraph]` and still `exit 0` (never blocks session start). No JSON systemMessage, no `continue: false`
- **Runtime variant**: Node (npm). `package.json` declares `"engines": {"node": ">=20 <26"}`. Install uses `npm install --omit=dev --ignore-scripts --no-audit --no-fund` — `--ignore-scripts` explicitly avoids the `prepare`/`build` scripts (those need source that lives in plugin root, not data dir)
- **Alternative approaches**: kdoc commits `node_modules/` (all pnpm-managed deps, including platform-specific native binaries like `@esbuild/linux-x64`) directly in the repo — no install step, but locks users to the committed OS/arch. codegraph uses the data-dir + symlink approach to avoid committing binaries. No PEP 723, no `npx`/`uvx`
- **Version-mismatch handling** (the distinctive axis this repo surfaces): **Node ABI tracking**. The install script writes `$PLUGIN_DATA/.node-abi` containing `process.versions.modules` (Node's `NODE_MODULE_VERSION` — the C++ ABI that native addons compile against). On every SessionStart it compares `current_abi` against the saved marker; on mismatch it runs `npm rebuild better-sqlite3 tree-sitter tree-sitter-typescript tree-sitter-javascript` (explicit enumeration — only native modules are rebuilt, not the whole tree) and writes the new ABI back. Two independent change-detection axes: `package.json` diff drives full reinstall; ABI diff drives rebuild-only. The `session-start.mjs` hook reinforces this — it runs `execFileSync('node', ['-e', 'require("better-sqlite3")'])` and if the error message matches `/NODE_MODULE_VERSION|was compiled against a different/` it triggers the same rebuild inline as a recovery path (so even if the ABI marker is accurate but the binary is somehow stale, the runtime-probe fallback catches it).

    ```
    current_abi="$(node -e 'process.stdout.write(process.versions.modules)')"
    ...
    saved_abi="$(cat "$abi_marker")"
    if [ "$saved_abi" != "$current_abi" ]; then needs_rebuild=true; fi
    ...
    npm rebuild better-sqlite3 tree-sitter tree-sitter-typescript tree-sitter-javascript
    echo -n "$current_abi" > "$abi_marker"
    ```

    This is analogous to Python's "track minor version to detect a major bump" pattern, but cheaper — Node ABIs are a single integer (e.g., `115` for Node 20, `127` for Node 22), not a version string, and native-only rebuild is far faster than full reinstall.
- **Pitfalls observed**: `--ignore-scripts` is required because `prepare` script runs `npm run build` which needs source in plugin root, not the copy in data dir. The rebuild enumerates native modules by name — adding a new native dep requires editing the shell script. `cli/node_modules/.pnpm/@esbuild+linux-x64@0.27.4` committed inside kdoc means Windows or Darwin users get a broken install; this is the opposite failure mode to codegraph's runtime-install. Also: both install variants skip peer-dep resolution entirely.

## 7. Bin-wrapped CLI distribution

- **Applicable**: partial — `codegraph/package.json` declares `"bin": {"codegraph": "./dist/cli/index.js"}` and `router-plugin/package.json` declares `"bin": {"router-plugin": "./src/cli.js"}`. But no `bin/` directory ships at plugin root, no shell wrappers observed — these are standard npm-style bin entries resolved by `node` via the `mcp/mcp.json` command, not by a `bin/` discovery mechanism
- **`bin/` files**: none (no directory named `bin` at any plugin root)
- **Shebang convention**: not applicable — the JS files are invoked via `node "${CLAUDE_PLUGIN_ROOT}/dist/cli/index.js" mcp` in `mcp.json` rather than as executable shebang scripts
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` interpolation in `mcp/mcp.json` args. Hooks separately use `resolve-root.mjs` helper that prefers `CLAUDE_PLUGIN_ROOT` then `__dirname`-based fallback
- **Venv handling (Python)**: not applicable — Node runtime only
- **Platform support**: nix + Windows via Node (no bash-only scripts in the MCP command path, though hooks are bash). kdoc's committed `@esbuild+linux-x64` platform-locks its pre-built CLI to Linux
- **Permissions**: not applicable — JS files invoked by `node`, no executable bit needed
- **SessionStart relationship**: tight — codegraph's SessionStart hook verifies the built `dist/cli/index.js` exists and auto-rebuilds native deps if ABI-mismatched, so the MCP server launch in the same session finds a working binary
- **Pitfalls observed**: `router-plugin/package.json` declares `"bin": {"router-plugin": "./src/cli.js"}` but **there is no `src/` directory** in `plugins/router-plugin/` (tree contains only `.claude-plugin/`, `docs/`, `skills/`, `templates/`, `README.md`, `package.json`). The bin reference is dead. Separately, `"version": "0.1.0"` in package.json vs `1.0.8` in plugin.json/marketplace means the npm metadata is years behind.

## 8. User configuration

- **`userConfig` present**: no — no plugin declares `userConfig` in its `plugin.json`
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable — no `${user_config.*}` or `CLAUDE_PLUGIN_OPTION_*` usage observed in hooks, scripts, or mcp configs
- **Pitfalls observed**: kdoc's session-start hook reads project-level `.kdoc.yaml` (project root) rather than surfacing config through `userConfig` — config-as-file convention instead of plugin-declared schema. See §17.

## 9. Tool-use enforcement

- **PreToolUse hooks**: count 3 — codegraph has two (`matcher: "Edit"` → `blast-gate.mjs`, `matcher: "Bash"` → `auto-index.mjs`); kdoc has one (`matcher: "Bash"` → `pre-push-check.mjs`)
- **PostToolUse hooks**: count 5 — codegraph has three (`Edit` and `Write` both → `check-staleness.mjs`, `Bash` → `post-bash-reindex.mjs`); claude-utils has two (`Skill` → `capture-event.sh skill.invoke`, empty-matcher catch-all → `capture-event.sh observation`)
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: stderr human-readable for diagnostics + stdout JSON for context injection. Example: codegraph's `check-staleness.mjs` emits `JSON.stringify({ ... })` on stdout when index is stale (structured additional-context payload) while `install-deps.sh` writes human lines like `[CodeGraph] Dependencies installed successfully.` to stdout/stderr
- **Failure posture**: fail-open throughout. Every hook catches errors and calls `process.exit(0)`; install-deps.sh is `set -euo pipefail` but every failure branch still explicitly `exit 0` after `rm -f` of the marker files. kdoc's `pre-push-check.mjs` is documented as "exit code is ALWAYS 0 — this is a reminder, not a block". This is a uniform convention across the repo
- **Top-level try/catch wrapping**: observed — every `.mjs` hook wraps stdin read + JSON parse in `try { … } catch { process.exit(0); }`. No unhandled-rejection handlers, but the synchronous-only style (via `execFileSync`) avoids the need
- **Pitfalls observed**: `blast-gate.mjs` runs on `Edit` and spawns a child Node process (`execFileSync`) with an 8 s timeout — hooks are on the Edit critical path, so a slow SQLite query stalls every edit up to that budget. The hook skips non-indexed extensions early, but on TS/TSX files the database query is unconditional (provided index exists). Also, the repo never uses `continue: false` — there is no gate that actually blocks an edit; "blast radius warning" only injects context.

## 10. Session context loading

- **SessionStart used for context**: yes — multiple plugins inject on startup. `claude-utils/scripts/git-context.sh` writes branch/recent-commits/uncommitted-changes to stdout. `kdoc/hooks/session-start.mjs` reads project `.kdoc.yaml` and writes a markdown summary of active knowledge areas. `codegraph/hooks/session-start.mjs` writes index-status / build-status / setup instructions
- **UserPromptSubmit for context**: no — `claude-utils` has a `UserPromptSubmit` hook but it only captures the event to the ai-sessions daemon spool (`capture-event.sh prompt`); it does not inject context back into the prompt
- **`hookSpecificOutput.additionalContext` observed**: not the explicit key — codegraph's `check-staleness.mjs` outputs bare `JSON.stringify({...})` with top-level fields rather than nesting under `hookSpecificOutput.additionalContext`. Other hooks rely on plain stdout being treated as context. Sample from `check-staleness.mjs` shown truncated in output; need more lines to confirm exact shape
- **SessionStart matcher**: mixed per plugin:
    - `codegraph`: empty matcher `""` for install-deps.sh (runs on all sub-events) + `"startup|resume|clear|compact"` for session-start.mjs
    - `kdoc`: `"startup|resume"`
    - `claude-utils`: `"startup"` for most, `"resume"` for a subset, `"startup|resume|compact"` for git-context.sh
- **Pitfalls observed**: Three plugins compete for SessionStart output — codegraph writes a status block, kdoc writes a governance summary, claude-utils writes a git block. No explicit ordering, so the agent sees a concatenated stream whose order depends on plugin-load order. Also, codegraph install-deps.sh uses an empty-string matcher (matches all sub-events including `compact`, triggering a cold-path `diff -q` check on every compaction cycle) while the real "boot" work is in the startup-matcher-scoped session-start.mjs — the two hooks are not co-ordinated.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none — feature not used. Stop + Notification hooks in `claude-utils` (`notify.sh`, `cleanup.sh`) substitute for desktop-notification monitors.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — no plugin.json declares a `dependencies` array of other plugins
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: no (the repo has zero tags)
- **Pitfalls observed**: `kdoc`'s session-start hook depends on the ai-sessions daemon spool at `~/.ai-sessions/spool/events.jsonl` and `claude-utils/capture-event.sh` writes to the same spool — a de-facto plugin-to-plugin dependency via filesystem convention, but not declared. If a user installs `kdoc` alone they get no drift warnings from the spool because claude-utils isn't writing to it.

## 13. Testing and CI

- **Test framework**: mixed — `codegraph/package.json` declares `"test": "vitest run"` with `vitest ^3.0.0` devDep; `router-plugin/package.json` declares `"test": "node --test"` (node:test native runner); `kdoc/package.json` delegates to `cd cli && pnpm test`; others have no test script
- **Tests location**: none visible in the tree — no `tests/` directory, no `*.test.*` files, no `__tests__/`. Test scripts are declared but test sources are not committed (likely stripped before sync from upstream)
- **Pytest config location**: not applicable (Node only)
- **Python dep manifest for tests**: not applicable
- **CI present**: no — `.github/` directory does not exist (`gh api repos/.../contents/.github` returns 404)
- **CI file(s)**: none
- **CI triggers**: not applicable
- **CI does**: not applicable
- **Matrix**: not applicable
- **Action pinning**: not applicable
- **Caching**: not applicable
- **Test runner invocation**: not applicable (no CI); local `npm test` / `pnpm test` are declared but no fixtures present
- **Pitfalls observed**: This is a pure aggregator repo — plugins are built/tested in separate upstream repos and synced in via `chore: sync ...` commits. The marketplace itself has no validation, no manifest schema check, no tag-sanity gate. Any drift (like `router-plugin/package.json` version `0.1.0` vs plugin.json `1.0.8`) could have been caught by a trivial pre-commit check, but the repo has no enforcement layer at all.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable — releases are implicit (commit to main = release)
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable (no GitHub releases exist)
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable for marketplace. Per-plugin `ai-quality-guardrails/docs/CHANGELOG.md` uses Keep-a-Changelog format manually
- **Pitfalls observed**: Zero release automation. Consumers must track `main` HEAD or pin commit SHA. A user who runs `/plugin install codegraph@mg-plugins` today gets `1.1.22`; tomorrow they get whatever the next "chore: sync" commit brings — no channel boundary, no ability to opt out of a breaking upstream change.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: no
- **Hooks.json validation**: no
- **Pitfalls observed**: `marketplace.json` contains no `$schema`, so even client-side editor validation is off. Combined with zero CI, any JSON syntax error would ship to users undetected.

## 16. Documentation

- **`README.md` at repo root**: present (short — ~30 lines, install commands + plugin table)
- **Owner profile README at `github.com/marioGusmao/marioGusmao`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: mixed — `ai-quality-guardrails`, `codegraph`, `kdoc`, `router-plugin` have READMEs; `claude-utils` does not (no README at `plugins/claude-utils/`)
- **`CHANGELOG.md`**: mixed — only `ai-quality-guardrails/docs/CHANGELOG.md` exists (Keep-a-Changelog format, entries `[0.1.0] - 2026-03-17 Added ...`). No root CHANGELOG. Other plugins lack changelogs despite high patch-version counts (kdoc at `1.0.38`, codegraph at `1.1.22` — dozens of versions with no changelog history)
- **`architecture.md`**: absent at repo root. Per-plugin: `ai-quality-guardrails/docs/ARCHITECTURE.md` present; `codegraph` embeds architecture rationale in `README.md` ("Why Hybrid Indexing", "Why SQLite", "Why symbol_uid") rather than a separate file; kdoc has `docs/superpowers/specs/` and `docs/superpowers/plans/` instead of architecture.md; router-plugin has `docs/PROTOCOL.md`/`ADOPTION.md`/`CERTIFY.md`/`SCAFFOLD.md` — four topical specs instead of one architecture doc
- **`CLAUDE.md`**: absent everywhere (no operational procedures document)
- **Community health files**: none — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, etc.
- **LICENSE**: present. Root `LICENSE` (MIT, "Copyright (c) 2026 Mario Silva Gusmao"); `ai-quality-guardrails/LICENSE` also present (MIT)
- **Badges / status indicators**: absent
- **Pitfalls observed**: Inconsistent documentation discipline across the five plugins — same marketplace, four different structural conventions (`docs/ARCHITECTURE.md` vs embedded-in-README vs superpowers/specs vs topical docs). No SECURITY.md despite shipping hooks that gate `Edit` and `Bash` tool calls.

## 17. Novel axes

- **Custom `capabilities.json` sidecar per plugin** — every plugin ships `.claude-plugin/capabilities.json` alongside `plugin.json` with a non-standard schema: `{plugin, version, schema_version: "1.0.0", capabilities: [{id, name, type: "skill"|"agent"|"mcp_tool"|"hook", applicable_phases: ["plan"|"implement"|"review"|"fix"|"docs"|"cross_phase"], guidance, anti_patterns: [...], priority: 1-10}]}`. This is not in the official Claude Code plugin spec. The `capabilities.version` field also drifts independently from `plugin.json.version` (e.g., codegraph plugin.json `1.1.22`, capabilities.json `1.1.18`) — suggesting this sidecar is maintained by a separate pipeline. Appears designed to feed a router/selector layer (the `router-plugin` in this same marketplace is likely the consumer) that picks which plugin capability to invoke based on `applicable_phases` + `priority`.
- **Codex interop marker at the skill level** — every `skills/<name>/` directory contains an `agents/openai.yaml` file (e.g., `interface: {display_name: "TDD Enforcement", short_description: "..."}`, `policy: {allow_implicit_invocation: true}`). This is a Codex-platform sibling contract alongside the Claude-native `SKILL.md`. The parent plugin.json (`ai-quality-guardrails`) carries Claude-Code-only `agents/` at the plugin root AND these per-skill Codex markers simultaneously — cross-platform skill publishing pattern.
- **Node ABI tracking as a first-class install-state dimension** — two orthogonal change detectors (`diff -q package.json` vs `.node-abi` marker) driving two distinct recovery actions (full `npm install` vs native-only `npm rebuild <list>`). Enumerated native module list means adding a new native dep requires editing the shell script, but the ABI-only path is ~10× faster than a full reinstall on Node major bumps. Paired with a **runtime-probe fallback in the Node session-start hook** — it literally `require("better-sqlite3")` in a child process and pattern-matches `/NODE_MODULE_VERSION|was compiled against a different/` on the error to trigger the same `npm rebuild` inline. Belt-and-suspenders: marker-file detection catches the common case cheaply, runtime probe catches stale markers or corrupted installs.
- **Symlink-out-of-data-dir install layout** — codegraph installs into `$CLAUDE_PLUGIN_DATA` (writable) then `ln -sfn $PLUGIN_DATA/node_modules $PLUGIN_ROOT/node_modules` so ESM `import` from the plugin's own source resolves without needing `NODE_PATH` hacks. Inverse of the more common "install into plugin root" pattern.
- **Hybrid auto-reindex triggers** — codegraph registers PreToolUse+PostToolUse on `Bash` with a shared regex set `/\bgit\s+(pull|merge|rebase|checkout|switch|cherry-pick|reset|restore)\b/` + `/\b(npm|pnpm|yarn)\s+install\b/` to invalidate the index on working-tree-changing commands. Gated on `existsSync(dbPath)` so first pulls don't spuriously create indexes.
- **Project-level YAML config read by session hook instead of `userConfig`** — kdoc reads `.kdoc.yaml` from project root in its session-start hook rather than exposing settings via plugin-manifest `userConfig`. Config lives with the project it configures, not with the user.
- **Filesystem-convention plugin-to-plugin coupling** — kdoc reads `~/.ai-sessions/spool/events.jsonl` and claude-utils writes to the same spool via `capture-event.sh`. No declared dependency; kdoc's drift-warning feature silently degrades when claude-utils isn't installed.
- **Router-via-marketplace protocol pack** — `router-plugin` ships `templates/router/` (inbox/, outbox/, conformance fixtures) plus `docs/PROTOCOL.md`, `docs/ADOPTION.md`, `docs/CERTIFY.md`, `docs/SCAFFOLD.md`. The plugin is a protocol specification + templates, not runtime code — uses the marketplace as a distribution channel for a packet contract that consumer repos adopt.
- **Pre-push reminder hook via Bash matcher** — kdoc hooks `PreToolUse` on `Bash` and parses the command string for `git push` patterns, then reports staleness of `governance-health.md` (always exit 0 — reminder, not block). Uses the Bash tool hook as a proxy for a git pre-push hook, with explicit documentation that terminal pushes aren't covered.

## 18. Gaps

- **No git commit signals a release** — every commit is "chore: sync <plugin-list>", so "what version of the marketplace is this" has no answer beyond commit SHA. Upstream repos (not in this aggregator) presumably hold changelogs and tags. Would need access to `marioGusmao/codegraph` and peer upstream repos to reconstruct release history and cadence.
- **Tests absent from tree** — `vitest` and `node --test` scripts declared but no test sources committed. Can't assess test coverage or style without upstream access.
- **capabilities.json consumer unknown** — the sidecar is clearly used, but which runtime reads it and how `priority` + `applicable_phases` map to invocation is not visible in this repo. Likely consumed by `router-plugin` or by a host-side agent selector not committed here.
- **`hookSpecificOutput.additionalContext` usage unconfirmed** — saw `JSON.stringify({...})` on stdout from `check-staleness.mjs` but only read first 40 lines; need to confirm whether the payload uses the `{hookSpecificOutput: {additionalContext: ...}}` envelope or top-level context fields.
- **router-plugin `src/` directory missing** — package.json bin points at `./src/cli.js` but `src/` doesn't exist in the committed tree. Either the plugin is deliberately "docs+templates only" (README confirms "does not ship a runtime SDK yet") and the bin entry is vestigial, or the src/ was dropped during a sync. Consumer repos adopting this plugin must not use the `bin` field.
- **kdoc pnpm `node_modules/` vendoring** — the `.pnpm/` tree under `plugins/kdoc/cli/node_modules/` includes platform-locked binaries (`@esbuild+linux-x64@0.27.4`). I sampled only one platform path; need to confirm whether other-arch binaries are also committed or if Linux-x64 is the sole supported target. If Linux-only, this is a hard install gate for macOS/Windows users that isn't documented in the plugin README.
- **Release automation in upstream repos** — not visible. The aggregator's "chore: sync vX.Y.Z" commits imply upstream automation exists somewhere but that belongs to `marioGusmao/codegraph`/`kdoc`/etc., outside this repo's scope.
