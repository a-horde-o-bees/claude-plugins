# affaan-m/everything-claude-code

## Identification

- **URL**: https://github.com/affaan-m/everything-claude-code
- **Stars**: 162,189 (per `gh api repos/affaan-m/everything-claude-code`; README badge claims "140K+")
- **Last commit date**: 2026-04-19 (`8bdf88e5` — "Merge pull request #1501 from affaan-m/feat/ecc2-board-observability-integration")
- **Default branch**: `main`
- **License**: MIT (SPDX `MIT`, via GitHub license API)
- **Sample origin**: primary (community)
- **One-line purpose**: "The performance optimization system for AI agent harnesses. From an Anthropic hackathon winner. Not just configs. A complete system: skills, instincts, memory optimization, continuous learning, security scanning, and research-first development." Works across Claude Code, Codex, Cursor, OpenCode, Gemini. (From `README.md` opening + `package.json` description; npm pkg name is `ecc-universal`.)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root. Sibling `.claude-plugin/plugin.json`, `.claude-plugin/README.md`, and `.claude-plugin/PLUGIN_SCHEMA_NOTES.md` (a hand-written document on undocumented validator constraints). Single-plugin marketplace wrapping the repo root as `source: "./"`.
- **Marketplace-level metadata**: top-level `name` + `owner` + `metadata.description` wrapper (no `version`, no `pluginRoot`). `metadata` contains only `description: "Battle-tested Claude Code configurations from an Anthropic hackathon winner"`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: category + tags + keywords (all three). Single plugin entry has `category: "workflow"`, identical arrays for `tags` and `keywords` (8 entries each: agents, skills, hooks, commands, tdd, code-review, security, best-practices). Homepage, repository, license, author all present inline.
- **`$schema`**: absent on `marketplace.json` and `plugin.json`. However, `hooks/hooks.json` does set `"$schema": "https://json.schemastore.org/claude-code-settings.json"` — interesting inconsistency.
- **Reserved-name collision**: no (plugin name `everything-claude-code` is not a reserved value).
- **Pitfalls observed**: `tags` and `keywords` are byte-identical duplicates — either the author doesn't know they serve separate purposes, or they're hedging in case marketplace tooling reads one and not the other. Marketplace has no `version` field, so marketplace-level versioning isn't tracked; all version authority is in `plugin.json` (see §2). The `.claude-plugin/PLUGIN_SCHEMA_NOTES.md` file is a *rare primary-source artifact* — the author has written down validator rules they reverse-engineered after real install failures (e.g., "`version` is required," "`agents` must be array of file paths not directory paths," "strings are not accepted even for single entries"). Worth harvesting.

## 2. Plugin source binding

- **Source format(s) observed**: `"./"` (relative, same-repo). Single plugin entry; no mix.
- **`strict` field**: `false` explicit on the marketplace entry.
- **`skills` override on marketplace entry**: absent. `strict: false` is used without an overriding `skills` list — the marketplace entry delegates entirely to `plugin.json` for component discovery.
- **Version authority**: both `plugin.json` (`1.10.0`) and sibling `package.json` (npm pkg `ecc-universal@1.10.0`) and a standalone `VERSION` file (`1.10.0`) and `agent.yaml` and multiple cross-ecosystem manifests (`.codex-plugin/plugin.json`, `.opencode/package.json`, `.agents/plugins/marketplace.json`). The `scripts/release.sh` enforces synchronization across ~17 version-bearing files, all bumped atomically. Marketplace manifest itself has no `version`.
- **Pitfalls observed**: `strict: false` without an accompanying `skills` override on the marketplace entry means the installer falls back to full directory scanning. With 156 skills, 38 agents, and 72 command shims, that's a heavy discovery surface on every install. The release script lists 17 distinct version-bearing files that all must move in lockstep — dead-giveaway that version sprawl became a real operational problem. Tag verification in CI only checks `package.json` version; drift between the other 16 files would not be caught by the release gate.

## 3. Channel distribution

- **Channel mechanism**: no split. Users pin via git ref (`@ref`) against main. Single release track via `v*` tags on `main`.
- **Channel-pinning artifacts**: absent. No stable/latest marketplace split; no dev-counter scheme on main.
- **Pitfalls observed**: With a repo this heavily used daily (162k stars, 1501+ PRs), the absence of a channel split means every commit on main is effectively a release candidate for anyone who pulls latest. The main branch is also where release tags are cut from, so there is no staging branch between dev and release. Tag cadence (v1.6 → v1.10 visible) appears to provide the "stable" surface; non-tag users ride main raw.

## 4. Version control and release cadence

- **Default branch name**: `main`.
- **Tag placement**: on `main`. `gh api tags` confirms `v1.10.0` (sha 846ffb75) → `v1.9.0` → `v1.8.0` → `v1.7.0` → `v1.6.0` are all on main.
- **Release branching**: none (tag-on-main). No `release/*` or `v*` legacy branches observed.
- **Pre-release suffixes**: none observed. All tags are clean `vX.Y.Z`.
- **Dev-counter scheme**: absent. `plugin.json` on main sits at the latest released version (`1.10.0`), not a monotonic `0.0.z` counter.
- **Pre-commit version bump**: no. Version bumping is explicit via `scripts/release.sh VERSION` — a shell script that bumps ~17 files, verifies they exist, then creates commit + tag.
- **Pitfalls observed**: release.sh encodes ALL 17 version-bearing files as named paths; adding a new version-synchronized manifest requires editing the script. Tag creation mechanics are human-gated (`./scripts/release.sh X.Y.Z`) but the CI release workflow does enforce tag=package.json consistency on the push. The workflow only verifies against `package.json`, so if release.sh has a bug and misses one of the other 16 files, CI won't catch it.

## 5. Plugin-component registration

- **Reference style in plugin.json**: explicit path arrays for `agents` (38 absolute file paths enumerated — `./agents/architect.md`, etc.), directory references for `skills: ["./skills/"]` and `commands: ["./commands/"]`. No `hooks` path (hooks live at `hooks/hooks.json` and are picked up by some other mechanism — possibly the installer, not the plugin manifest). No MCP reference in plugin.json; `.mcp.json` sits at repo root.
- **Components observed**:
  - skills: yes (156 per README claim; `./skills/` directory reference)
  - commands: yes (72 legacy command shims per README; `./commands/` directory reference)
  - agents: yes (38 explicit file paths)
  - hooks: yes (`hooks/hooks.json` with PreToolUse, PostToolUse, SessionStart, PreCompact, Stop, SessionEnd — not referenced by plugin.json but loaded by install flow)
  - .mcp.json: yes (at repo root, 6 MCP servers: github, context7, exa, memory, playwright, sequential-thinking)
  - .lsp.json: no
  - monitors: no
  - bin: no (no `bin/` directory; install via `install.sh`/`install.ps1`)
  - output-styles: no
- **Agent frontmatter fields used**: `name`, `description`, `tools`, `model`. Sample from `agents/planner.md`: `name: planner`, `description: "Expert planning specialist for complex features and refactoring. Use PROACTIVELY when users request feature implementation..."`, `tools: ["Read", "Grep", "Glob"]`, `model: opus`. Sample from `agents/code-reviewer.md`: `tools: ["Read", "Grep", "Glob", "Bash"]`, `model: sonnet`. No `skills`, `memory`, `background`, or `isolation` fields observed.
- **Agent tools syntax**: plain tool names in a JSON array (`["Read", "Grep", "Glob", "Bash"]`). No permission-rule syntax like `Bash(uv run *)`.
- **Pitfalls observed**: The author's own `PLUGIN_SCHEMA_NOTES.md` explicitly documents that the validator rejects `"agents": ["./agents/"]` (directory paths) — they hit this validator restriction and enumerated all 38 agents by hand, but still used directory references for `skills` and `commands`. Either those two fields have different validator rules or they're currently tolerated because the plugin is loaded `strict: false`. The observation `"agents: Invalid input"` quoted in PLUGIN_SCHEMA_NOTES is a verbatim error string worth capturing in the pattern doc as a known validator failure mode.

## 6. Dependency installation

- **Applicable**: yes. Mixed runtime — Node (primary) + Python (secondary for `llm-abstraction` subpackage + `ecc_dashboard.py`).
- **Dep manifest format**: `package.json` + `package-lock.json` + `yarn.lock` (root, Yarn-native but all PM lockfiles present for CI matrix); `pyproject.toml` (for `src/llm` Python abstraction).
- **Install location**: repo-local `node_modules` via `install.sh`, not `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PLUGIN_ROOT}` isolated venv. `install.sh` runs `npm install --no-audit --no-fund` if `node_modules` missing, then delegates to `scripts/install-apply.js`.
- **Install script location**: `install.sh` (POSIX bash) + `install.ps1` (PowerShell for Windows) at repo root. Bash wrapper resolves symlinks, cygpath-converts on MSYS2, then execs `node scripts/install-apply.js "$@"`.
- **Change detection**: existence-only (`if [ ! -d "$SCRIPT_DIR/node_modules" ]`). No checksum or version-file stamping for installed deps.
- **Retry-next-session invariant**: no `rm` on failure. `install.sh` runs `set -euo pipefail` — `npm install` failure aborts the script, but the checkout state is unchanged.
- **Failure signaling**: `set -euo pipefail` halts with non-zero exit; stderr surfaces npm's own output. No structured JSON `systemMessage` or hook-specific `continue: false`.
- **Runtime variant**: Node npm (primary) + Node yarn/pnpm/bun (CI matrix exercises all four). Python `uv` is NOT used; `pyproject.toml` uses hatchling build-backend and classic pip-style optional-dependencies.
- **Alternative approaches**: none (no PEP 723, no pointer-file pattern, no uvx/npx for plugin code — MCP servers do use `npx` for fetching, see §5).
- **Version-mismatch handling**: none (no Python minor version tracking; no Node ABI tracking). CI matrix covers the combinatorial surface instead (3 OS × 3 Node × 4 PM = 36 lanes, minus bun-on-Windows).
- **Pitfalls observed**: `install.sh` is legacy shell wrapping Node — the comment in it says so explicitly. The actual installer (`scripts/install-apply.js`) is Node-based and does the real work. The repo doesn't rely on plugin-native dependency-install hooks (e.g., SessionStart hooks that install into an isolated plugin venv the way the user's claude-plugins ocd pattern does). Instead, the install model is "clone the repo, run `install.sh`, modifies `~/.claude/`" — this is the *pre-plugin-spec* distribution model, adapted to also work as a plugin but not relying on plugin-managed data dirs. Users installing via the Claude marketplace plugin flow bypass `install.sh` entirely; unclear from this research whether that path is complete.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no. No `bin/` directory in the repo. `install.sh` and `install.ps1` live at repo root as user-facing installers, not `bin/`-distributed binaries. The npm package (`ecc-universal`) publishes a long `files:` list including `install.sh`, `install.ps1`, `scripts/*.js`, and various `.agents/`, `.codex/`, `.opencode/` sibling directories — but does not expose anything via npm `bin`.
- **`bin/` files**: none.
- **Shebang convention**: not applicable (no `bin/` directory). Root scripts use `#!/usr/bin/env bash` (`install.sh`) and `#!/usr/bin/env node` (`scripts/hooks/*.js`, `scripts/release.sh` is bash).
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: not applicable (no Python plugin bin).
- **Platform support**: not applicable.
- **Permissions**: not applicable.
- **SessionStart relationship**: not applicable (no `bin/`). SessionStart hook (`session:start`) loads previous context and detects package manager; it does not write bin/ pointer files.
- **Pitfalls observed**: The absence of `bin/` + presence of heavy hooks means this plugin's runtime surface is entirely hook-driven, not invocation-driven. All "user-facing" entry points are slash commands routed through `commands/` or skills routed through `skills/`.

## 8. User configuration

- **`userConfig` present**: no. Neither `plugin.json` nor `marketplace.json` declares a `userConfig` block.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable. However, hooks read *process env vars* directly — e.g., `CLAUDE_PLUGIN_ROOT`, `CLAUDE_CODE_PACKAGE_MANAGER` (set by CI matrix), `ECC_GOVERNANCE_CAPTURE` (hook opt-in). These are user/CI-supplied env vars, not plugin userConfig bindings.
- **Pitfalls observed**: `.env.example` exists at repo root (likely for the `src/llm` abstraction layer — anthropic/openai keys), but that's application config, not plugin userConfig. The plugin relies on "read the env var if set" rather than declaring any configuration surface — a user who wants to toggle a hook profile must know the env var name from documentation.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 9 observed in `hooks/hooks.json`, all wrapped with a giant inline `node -e` bootstrap that resolves `CLAUDE_PLUGIN_ROOT`:
  - `pre:bash:dispatcher` (matcher `Bash`) — consolidated Bash preflight dispatcher (quality, tmux, push, GateGuard)
  - `pre:write:doc-file-warning` (matcher `Write`) — warn about non-standard doc files (exit 0, warn only)
  - `pre:edit-write:suggest-compact` (matcher `Edit|Write`) — suggest manual `/compact` at intervals
  - `pre:observe:continuous-learning` (matcher `*`) — capture tool-use observations (async, 10s timeout)
  - `pre:governance-capture` (matcher `Bash|Write|Edit|MultiEdit`) — capture governance events (opt-in via `ECC_GOVERNANCE_CAPTURE=1`, 10s timeout)
  - `pre:config-protection` (matcher `Write|Edit|MultiEdit`) — block mods to linter/formatter config files (5s timeout)
  - `pre:mcp-health-check` (matcher `*`) — check MCP server health before MCP tool execution
  - `pre:edit-write:gateguard-fact-force` (matcher `Edit|Write|MultiEdit`) — block first edit per file, demand investigation before allowing (5s timeout)
  - (ninth Bash pre-hook folded into dispatcher)
- **PostToolUse hooks**: 6+ observed (truncated in fetched response):
  - `post:bash:dispatcher` (matcher `Bash`) — logging, PR, build notifications (async, 30s)
  - `post:quality-gate` (matcher `Edit|Write|MultiEdit`) — fast quality checks (async, 30s)
  - `post:edit:design-quality-check` (matcher `Edit|Write|MultiEdit`) — warn on generic-template UI drift
  - `post:edit:accumulator` (matcher `Edit|Write|MultiEdit`) — record edited JS/TS paths for batch format+typecheck at Stop
  - `post:edit:console-warn` (matcher `Edit`) — warn about console.log
  - `post:governance-capture` (matcher `Bash|Write|Edit|MultiEdit`) — capture governance from outputs
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stderr human-readable + exit-code gated. Per `hooks/README.md`: "PreToolUse hooks can **block** (exit code 2) or **warn** (stderr without blocking)." No stdout JSON convention for structured systemMessage observed.
- **Failure posture**: mixed per-hook, centrally documented. README table explicitly annotates each hook's exit behavior ("2 (blocks)" vs "0 (warns)"). Infrastructure hooks (MCP health check, config protection, GateGuard) fail-closed; observational hooks (continuous learning, design quality) fail-open.
- **Top-level try/catch wrapping**: observed in bootstrap shim — the inline `node -e` fallback-root resolution is wrapped `try { ... } catch(x) {}`. Individual hook scripts not fully inspected, but `plugin-hook-bootstrap.js` is the enforced entrypoint and does top-level error-silencing for the resolver.
- **Pitfalls observed**: The hook command is ~1.5KB of inline `node -e "..."` boilerplate that re-implements `CLAUDE_PLUGIN_ROOT` resolution (env var → `~/.claude/` direct → well-known plugin slug paths including both `ecc` and legacy `everything-claude-code` + `@ecc` + `marketplace/ecc` prefixes → versioned cache dirs under `~/.claude/plugins/cache/`). This fallback chain is *evidence* that the Claude Code plugin runtime does not reliably set `CLAUDE_PLUGIN_ROOT` across all install paths — a meaningful finding for the pattern doc. `session-start-bootstrap.js` documents this explicitly: "the previous approach embedded this logic as an inline `node -e "..."` string inside hooks.json. Characters like `!` (used in `!org.isDirectory()`) can trigger bash history expansion... causing 'SessionStart:startup hook error' to appear in the Claude Code CLI header." So they extracted SessionStart only to a standalone file — but the other 15+ hooks still embed the inline bootstrap. This tension (duplicated-bootstrap-in-hooks.json vs extracted-file) is a genuine friction point. Hook IDs follow a structured `{lifecycle}:{scope}:{purpose}` convention (e.g., `pre:edit-write:gateguard-fact-force`) — worth noting as a pattern.

## 10. Session context loading

- **SessionStart used for context**: yes. `session:start` hook (matcher `*`) — "Load previous context and detect package manager on new session." Runs `session-start-bootstrap.js` → `run-with-flags.js session:start` → actual handler.
- **UserPromptSubmit for context**: not observed in the fetched hooks.json section. May exist; not verified.
- **`hookSpecificOutput.additionalContext` observed**: not directly verified. Structured stdout from SessionStart handler was not inspected.
- **SessionStart matcher**: `*` (fires on all sub-events including startup, clear, compact).
- **Pitfalls observed**: SessionStart is the ONLY hook that got the standalone-file extraction treatment, specifically because inline `node -e` with `!` characters was triggering bash history expansion and producing the user-visible error header. This is a recurring distribution problem worth calling out in the pattern doc — inline hook commands are fragile across shell environments.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no. `gh api contents/monitors.json` returned 404.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: The plugin implements *notification-like* behavior via Stop hooks instead (`desktop-notify.js` sends macOS desktop notifications after Stop events per the hooks/README table). So the feature exists but is implemented at the hook layer, not via the dedicated monitors.json surface. This is evidence that the monitors.json abstraction is not yet broadly adopted even in very mature plugins.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace, tags are `v1.10.0` style not prefixed).
- **Pitfalls observed**: Single-plugin aggregator marketplace — everything is self-contained in the one entry. No need for inter-plugin dependency mechanics.

## 13. Testing and CI

- **Test framework**: multiple — `node:test` (primary via `tests/**/*.test.js`), pytest (for `src/llm` Python abstraction via `tests/docs`, `tests/integration`), plus custom JS validators under `scripts/ci/`. README mentions Jest-compatible naming but the runner uses `spawnSync('node', [testPath])` directly — the `.test.js` files are plain node modules, not jest.
- **Tests location**: `tests/` at repo root, with subdirectories (`tests/hooks/`, `tests/integration/`, `tests/lib/`, `tests/docs/`, `tests/scripts/`, `tests/ci/`). There is also `tests/plugins/everything-claude-code/` — the per-plugin nested-test precedent mentioned in the task, but it contains only one file (inspection of subdir not fully drilled). Root-level test files (`test_builder.py`, `test_executor.py`, `test_resolver.py`, `test_types.py`, `codex-config.test.js`, `opencode-config.test.js`, `plugin-manifest.test.js`) mix Python pytest and JS node:test at the same level.
- **Pytest config location**: `[tool.pytest.ini_options]` in `pyproject.toml` — `testpaths = ["tests"]`, `asyncio_mode = "auto"`, `filterwarnings = ["ignore::DeprecationWarning"]`.
- **Python dep manifest for tests**: `pyproject.toml` via `[project.optional-dependencies] dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "pytest-cov>=4.1", "pytest-mock>=3.12", "ruff>=0.4", "mypy>=1.10"]`.
- **CI present**: yes.
- **CI file(s)**: 7 workflows — `ci.yml`, `release.yml`, `maintenance.yml`, `monthly-metrics.yml`, `reusable-test.yml`, `reusable-release.yml`, `reusable-validate.yml`.
- **CI triggers**: `ci.yml` on `push: branches: [main]` + `pull_request: branches: [main]`; `release.yml` on `push: tags: ['v*']`; `maintenance.yml` on `schedule: '0 9 * * 1'` + `workflow_dispatch`; `monthly-metrics.yml` on `schedule: '0 14 1 * *'` + `workflow_dispatch`; reusable-* on `workflow_call` (+ `workflow_dispatch` for reusable-release).
- **CI does**: `ci.yml` has four parallel jobs — `test` (runs `node tests/run-all.js` across matrix), `validate` (10 validator scripts: agents, hooks, commands, skills, install-manifests, workflow-security, rules, catalog, unicode-safety), `security` (npm audit `--audit-level=high`, continue-on-error), `lint` (ESLint on scripts/tests + markdownlint on agents/skills/commands/rules). `release.yml` does tag-format validation + tag=package.json version verification + npm publish state check + conditional `npm publish --access public --provenance` + GitHub release via `softprops/action-gh-release`.
- **Matrix**: OS × Node × PM — `[ubuntu-latest, windows-latest, macos-latest] × [18.x, 20.x, 22.x] × [npm, pnpm, yarn, bun]`, with `exclude: bun on windows-latest`. Net 33 lanes (36 minus 3 bun-on-windows). `fail-fast: false`.
- **Action pinning**: SHA (every action is pinned by 40-char SHA with a `# vX.Y.Z` comment — e.g., `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2`). Consistent across all workflows.
- **Caching**: `actions/cache` keyed per-PM (npm/pnpm/yarn/bun), scoped by `runner.os`-`node-version`-`pm`-`hashFiles(<lockfile>)`. Built-in setup-node cache is NOT used (explicit `actions/cache` steps per package manager instead).
- **Test runner invocation**: `node tests/run-all.js` — a custom runner that globs `tests/**/*.test.js`, spawnSyncs each, aggregates pass/fail counts in an ASCII box. Python tests are NOT invoked by run-all.js (they're separately runnable via `pytest` per `pyproject.toml` config but not wired into CI).
- **Pitfalls observed**: The `reusable-test.yml` and `reusable-release.yml` and `reusable-validate.yml` exist but are **duplicated by ci.yml + release.yml** — the main workflows inline-copy the reusable content instead of calling it. Probably a migration-in-progress: reusables are set up but not yet consumed by the primary workflows. Worth noting as an anti-pattern (duplicated workflow bodies create drift risk — the release.yml body and reusable-release.yml body are nearly identical but differ on REF_NAME vs inputs.tag). The 33-lane matrix is expensive — ~5-10 minutes per lane × 33 lanes = significant CI minutes per PR. Python tests are defined via pyproject.toml but appear orphaned from CI — `scripts/ci/` validators are all Node. Hook/bootstrap scripts have tests (tests/hooks/*.test.js, 20+ files) — worth calling out as mature coverage of the hook surface.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes (`.github/workflows/release.yml`; also `reusable-release.yml` as a parallel unused copy).
- **Release trigger**: `push: tags: ['v*']` on `release.yml`. `reusable-release.yml` is `workflow_call` + `workflow_dispatch` (for republish scenarios).
- **Automation shape**: tag-sanity gates → version sync verification → npm publish (idempotent) → GitHub release creation with custom body + `generate_release_notes: true`.
- **Tag-sanity gates**: three gates —
  1. Tag format: `^v[0-9]+\.[0-9]+\.[0-9]+$` (no pre-release suffixes allowed)
  2. Tag == package.json version: shell-strips `v` prefix, compares with `node -p "require('./package.json').version"`
  3. `plugin-manifest.test.js` runs as part of the release job ("Verify release metadata stays in sync") — covers cross-manifest version drift
- **Release creation mechanism**: `softprops/action-gh-release@b4309332981a82ec1c5618f44dd2e27cc8bfbfda # v3.0.0` with `body_path: release_body.md` (generated inline in the workflow) + `generate_release_notes: true` (stacks auto-generated commit list on top of custom highlights).
- **Draft releases**: no. Release is created published.
- **CHANGELOG parsing**: no. The workflow generates a heredoc'd `release_body.md` with hardcoded section templates ("What This Release Focuses On", "Notable Changes", "Notes"). The actual `CHANGELOG.md` in the repo is maintained separately and not programmatically consumed by the release workflow.
- **Pitfalls observed**: The release body is LLM-style boilerplate baked into the workflow ("Harness reliability and hook stability across Claude Code, Cursor, OpenCode, and Codex") — it ships identical marketing copy every release unless manually edited. The real per-release detail comes from `generate_release_notes: true` (auto commit list). This is a release-body pattern where the custom body adds almost no information over what GitHub auto-generates — may be an anti-pattern. `npm publish --provenance` is used, which requires `permissions: id-token: write` (correctly set). Idempotency is explicit: `npm view "${NAME}@${VERSION}"` gates the publish step, so rerunning on a published tag doesn't error. `reusable-release.yml` has `workflow_dispatch` with a `tag` input so any version can be republished, but `release.yml` doesn't `uses:` it — so the republish capability is only available if someone manually triggers the reusable workflow.

## 15. Marketplace validation

- **Validation workflow present**: yes — `validate` job in `ci.yml`, plus `reusable-validate.yml`.
- **Validator**: node custom scripts — 10 discrete validators under `scripts/ci/`:
  - `validate-agents.js`
  - `validate-hooks.js`
  - `validate-commands.js`
  - `validate-skills.js`
  - `validate-install-manifests.js`
  - `validate-workflow-security.js`
  - `validate-rules.js`
  - `catalog.js --text` (counts sanity)
  - `check-unicode-safety.js`
- **Trigger**: `push: [main]` + `pull_request: [main]` via `ci.yml`. Also callable via `reusable-validate.yml` as `workflow_call`.
- **Frontmatter validation**: yes — `validate-agents.js`, `validate-skills.js`, and `validate-commands.js` all presumably parse YAML frontmatter (inferred from purpose; not inspected).
- **Hooks.json validation**: yes — `validate-hooks.js`.
- **Pitfalls observed**: `validate-workflow-security.js` is a NOVEL validator — not a standard plugin concern, but this repo has so many GitHub workflows that they wrote a dedicated CI check for workflow hygiene (likely SHA-pinning enforcement, permissions minimization, etc.). `validate-install-manifests.js` is also novel — validates the cross-ecosystem install manifests (Codex, OpenCode, Cursor, Gemini plugins) stay in sync with the Claude ones. `check-unicode-safety.js` is again novel — presumably blocks invisible unicode (zero-width, RTL override, etc.) in authored markdown/JS, a real prompt-injection vector for AI-agent plugins. These three are worth calling out as validators the pattern doc has not yet surfaced.

## 16. Documentation

- **`README.md` at repo root**: present, large (many thousands of lines per README badges + ToC references). Heavy badge header, multi-language READMEs for pt-BR, zh-CN, zh-TW, ja-JP, ko-KR, tr (under `docs/<locale>/`). Top-level also contains README.zh-CN.md as a direct translation file.
- **Owner profile README at `github.com/affaan-m/affaan-m`**: present (~148 lines, marketing collateral — manifesto + flagship project framing)
- **`README.md` per plugin**: n/a (single-plugin marketplace; plugin root IS repo root). `.claude-plugin/README.md` exists and presumably describes the marketplace-level metadata only.
- **`CHANGELOG.md`**: present. Format is custom "per-release headings with sub-sections (Highlights, Release Surface, New Workflow Lanes, ECC 2.0 Alpha, Notes)" — not Keep a Changelog format. Chronological reverse-order.
- **`architecture.md`**: absent at repo root. No per-plugin architecture.md. There is a `docs/SELECTIVE-INSTALL-ARCHITECTURE.md` (referenced in release.sh) that covers one specific subsystem.
- **`CLAUDE.md`**: present at repo root (also `AGENTS.md`, `RULES.md`, `SOUL.md`, `TROUBLESHOOTING.md`, `WORKING-CONTEXT.md`, `SPONSORING.md`, `SPONSORS.md`, `EVALUATION.md`, `REPO-ASSESSMENT.md`, `COMMANDS-QUICK-REF.md`, `the-longform-guide.md`, `the-security-guide.md`, `the-shortform-guide.md` — an unusually dense per-consumer documentation surface).
- **Community health files**: `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` — all present.
- **LICENSE**: present (MIT).
- **Badges / status indicators**: extensive — 9+ badges in README header (stars, forks, contributors, npm weekly downloads for two packages, GitHub app installs, license, language icons, Anthropic-hackathon-winner blockquote).
- **Pitfalls observed**: 14+ top-level markdown files (CLAUDE.md, AGENTS.md, RULES.md, SOUL.md, TROUBLESHOOTING.md, WORKING-CONTEXT.md, EVALUATION.md, REPO-ASSESSMENT.md, COMMANDS-QUICK-REF.md, SPONSORING.md, SPONSORS.md, README.md, README.zh-CN.md, CHANGELOG.md, LICENSE) plus three "the-*.md" guides — this is far beyond the typical plugin docs surface. Evidence that the author prefers documentation-as-marketing (README badges) AND documentation-as-agent-context (CLAUDE.md, AGENTS.md, SOUL.md). The `PLUGIN_SCHEMA_NOTES.md` inside `.claude-plugin/` is particularly valuable as primary-source reverse-engineered validator rules. Multi-language README maintenance is burdensome — release.sh bumps version in both README.md and docs/zh-CN/README.md, but the other locales (pt-BR, zh-TW, ja-JP, ko-KR, tr) are not in the release.sh file list, so they likely drift.

## 17. Novel axes

- **Validator reverse-engineering as primary source**: `.claude-plugin/PLUGIN_SCHEMA_NOTES.md` is a standalone document capturing undocumented Claude Code plugin validator constraints, written from observed failures. Explicit rules documented: `version` is mandatory (not just recommended), `agents`/`commands`/`skills`/`hooks` must be arrays (strings rejected even for single entries), `agents` MUST be explicit file paths (directory paths rejected with error `"agents: Invalid input"`). This is the only repo in the known sample that publishes its validator learnings as a first-class artifact. Worth linking from the pattern doc as external validation evidence.

- **Pre-commit/pre-hook environment fragility workarounds**: hook commands embed ~1.5KB of inline `node -e "..."` bootstrap logic that re-implements `CLAUDE_PLUGIN_ROOT` resolution across a chain of fallbacks (env var → `~/.claude` direct → 6 well-known plugin slug paths including `ecc`, `ecc@ecc`, `marketplace/ecc`, `everything-claude-code`, `everything-claude-code@everything-claude-code`, `marketplace/everything-claude-code` → versioned cache dirs). SessionStart was specifically extracted to a standalone file because inline `!` characters triggered bash history expansion and caused visible "SessionStart:startup hook error" in the CLI header. This is real-world evidence that the inline-hook-command pattern is fragile across shell environments — a novel distribution-concern axis worth a dedicated purpose section.

- **Cross-ecosystem version sprawl**: `scripts/release.sh` enumerates 17 version-bearing files that must move in lockstep for a release: `package.json`, `package-lock.json`, `AGENTS.md`, `docs/tr/AGENTS.md`, `docs/zh-CN/AGENTS.md`, `agent.yaml`, `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`, `.opencode/package.json`, `.opencode/package-lock.json`, `.opencode/plugins/ecc-hooks.ts`, `README.md`, `docs/zh-CN/README.md`, `docs/SELECTIVE-INSTALL-ARCHITECTURE.md`. This is a cross-ecosystem (Claude + Codex + OpenCode + Cursor + Gemini) distribution pattern not captured in the current pattern doc — multi-harness plugin distribution as a novel axis.

- **Validator script composition surface**: the `validate` job composes 10 distinct validators (agents, hooks, commands, skills, install-manifests, workflow-security, rules, catalog, unicode-safety) as separate CI steps with `continue-on-error: false`. Three are novel relative to the known sample:
  - `validate-workflow-security.js` — presumed GitHub Actions hygiene (SHA-pinning, minimal permissions)
  - `validate-install-manifests.js` — cross-ecosystem manifest sync verification
  - `check-unicode-safety.js` — invisible-unicode/zero-width-character injection check (a prompt-injection vector specific to AI-agent plugins)

- **Centralized hook bootstrap pattern**: all hooks invoke `plugin-hook-bootstrap.js` which delegates to `run-with-flags.js {event-id} {handler-script-path} {profile-flags}` — a *hook profile gating layer* (`standard,strict`) that allows hooks to opt in/out based on user-selected discipline level. The `ECC_GOVERNANCE_CAPTURE=1` env-var opt-in for governance hooks is part of this system. This bootstrap+runner+profile-gate architecture is a novel distribution pattern.

- **Hook ID taxonomy**: structured IDs like `pre:bash:dispatcher`, `pre:edit-write:suggest-compact`, `post:edit:accumulator`, `pre:edit-write:gateguard-fact-force` — `{lifecycle}:{scope}:{purpose}` — machine-parseable, filterable, and deduplicatable. Worth noting as a naming convention.

- **Reusable-workflow declared-but-unused pattern**: the three reusable workflows (`reusable-test.yml`, `reusable-release.yml`, `reusable-validate.yml`) exist but are not `uses:`d by the primary `ci.yml`/`release.yml`. Contents are duplicated — this is an in-progress migration, not a finished pattern. Mark as anti-pattern if surfaced in the pattern doc: declaring reusable workflows without consuming them creates drift risk (two copies of the same CI body have already diverged on input-variable names: `REF_NAME` vs `inputs.tag`).

- **Npm publish as distribution in addition to plugin marketplace**: the plugin is ALSO distributed as the `ecc-universal` npm package — same source, parallel channel. The `files:` list in `package.json` includes the entire plugin payload. Users can `npm install -g ecc-universal` or use it via the plugin marketplace. Dual-distribution is a novel axis.

- **GateGuard / fact-forcing first-edit gate**: `pre:edit-write:gateguard-fact-force` blocks the first `Edit`/`Write`/`MultiEdit` per file and demands investigation (importers, data schemas, user instruction) before allowing. This is a workflow-discipline hook specific to agent research quality — not documented in any of the known pattern areas. Worth a novel purpose-section candidate.

## 18. Gaps

- **`.claude/skills/` contents**: only inspected the single subdirectory `everything-claude-code/SKILL.md` at top level of `.claude/skills/`. The skill declares itself as "Development conventions and patterns for everything-claude-code" — appears to be a meta-skill teaching Claude to operate on this repo's own conventions. Full skill surface under `skills/` (the 156-skill directory) was not enumerated — `gh api contents/skills` would return 156+ entries, which would exhaust budget for little marginal value given `plugin.json` uses `./skills/` as a directory reference.

- **SessionStart / UserPromptSubmit additional-context shape**: `session-start-bootstrap.js` was inspected to understand its `CLAUDE_PLUGIN_ROOT` resolution logic but the downstream `session-start.js` handler (which actually produces context output) was not. Whether it emits `hookSpecificOutput.additionalContext` JSON or just stderr/stdout strings is unverified. Resolving would require fetching `scripts/hooks/session-start.js`.

- **Full PostToolUse/Stop hook list**: `hooks/hooks.json` was fetched with `head -200`, capturing PreToolUse + PreCompact + SessionStart + partial PostToolUse. The `Stop` and `SessionEnd` sections (mentioned in hooks/README.md with 4-5 hooks each) were not retrieved in detail. Would require fetching the full `hooks.json` (larger than 200 lines).

- **`tests/plugins/everything-claude-code/` contents**: directory confirmed to exist but contents not enumerated. The task mentioned this as the per-plugin nested tests precedent; verifying it's a real pattern vs a placeholder requires `gh api contents/tests/plugins/everything-claude-code` — not fetched to preserve budget.

- **`validate-workflow-security.js` / `validate-install-manifests.js` / `check-unicode-safety.js` internals**: identified as novel validators but actual rule set not inspected. Budget-constrained; would require 3 more raw fetches.

- **`reusable-release.yml` vs `release.yml` divergence audit**: comparison was visual, not byte-level. Possible additional drift exists beyond `REF_NAME` vs `inputs.tag`.

- **How hooks/hooks.json gets installed**: `plugin.json` doesn't reference it; `install.sh` uses `scripts/install-apply.js` (Node-based installer); plugin-marketplace install path behavior vs legacy `install.sh` path not distinguished. Whether plugin-marketplace users get hooks at all is unclear from the surface-level inspection.

- **Stars discrepancy**: GitHub API reports 162,189 stars; README badge says "140K+". Either stars grew significantly post-README-update or badge is cached. Noted but not resolved.

- **`agent.yaml`**: referenced in release.sh as version-bearing but file contents not inspected. Unknown consumer (possibly an AGENT.md-adjacent unified-agent-manifest the author invented). Would reward a single raw fetch.
