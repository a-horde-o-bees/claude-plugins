# Sample

Mirrors of `https://github.com/affaan-m/everything-claude-code`. A multi-component performance optimization system for AI agent harnesses (skills, instincts, memory optimization, continuous learning, security scanning, research-first development) that ships across Claude Code, Codex, Cursor, OpenCode, and Gemini. 162,189 stars (badge claims "140K+"); default branch `main`; MIT license; latest commit 2026-04-19 on PR #1501. Single-plugin marketplace at `everything-claude-code`; npm package name is `ecc-universal@1.10.0`.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root with one plugin entry whose `source` is `"./"` — the marketplace and its sole plugin share the same repo root. Sibling files under `.claude-plugin/`: `plugin.json`, `README.md`, and `PLUGIN_SCHEMA_NOTES.md`. Top-level keys are `name` + `owner` + `metadata.description` (no `version`, no `pluginRoot`). `metadata` contains only `description: "Battle-tested Claude Code configurations from an Anthropic hackathon winner"`. `metadata.pluginRoot` absent.

### `$schema` declaration on marketplace.json

`$schema` is absent on `marketplace.json` and `plugin.json`. However, `hooks/hooks.json` does set `"$schema": "https://json.schemastore.org/claude-code-settings.json"` — declaration on a non-marketplace document while the marketplace itself omits the field.

## Per-plugin discoverability metadata

### Multi-dimensional (category + keywords + tags)

Single plugin entry sets `category: "workflow"` plus byte-identical `tags` and `keywords` arrays (8 entries each: `agents`, `skills`, `hooks`, `commands`, `tdd`, `code-review`, `security`, `best-practices`). Homepage, repository, license, and author all present inline. The duplicated arrays suggest the author either does not know `tags` and `keywords` serve distinct purposes or is hedging across tooling that may read one and not the other.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry; plugin root and repo root are the same path. Single plugin entry; no mix.

### `strict` field default

`strict: false` is set explicitly on the marketplace entry without an accompanying `skills` override array. The installer falls back to full directory scanning over the repo root — with 156 skills, 38 agents, and 72 command shims, that is a heavy discovery surface on every install.

## Version coordination

### Multi-file with bump script as enforcer (multi-registry)

`scripts/release.sh` enumerates 17 distinct version-bearing files that must move in lockstep on every release: `package.json`, `package-lock.json`, `AGENTS.md`, `docs/tr/AGENTS.md`, `docs/zh-CN/AGENTS.md`, `agent.yaml`, `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`, `.opencode/package.json`, `.opencode/package-lock.json`, `.opencode/plugins/ecc-hooks.ts`, `README.md`, `docs/zh-CN/README.md`, `docs/SELECTIVE-INSTALL-ARCHITECTURE.md`. Adding a new version-synchronized manifest requires editing the script. Tag verification in CI checks only `package.json` version against the tag — drift between the other 16 files would not be caught by the release gate.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Users pin via git ref (`@ref`) against main; single release track via `vX.Y.Z` tags. No channel-pinning artifacts (no stable/latest marketplace split, no dev-counter scheme). Tag cadence visible: `v1.10.0` (sha 846ffb75) → `v1.9.0` → `v1.8.0` → `v1.7.0` → `v1.6.0` all on main. With 162k stars and 1500+ PRs, every commit on main is effectively a release candidate for anyone pulling latest; tags provide the "stable" surface, non-tag users ride main raw. No `release/*` staging branch between dev and release.

## Tag and release lifecycle

### Tag-on-main, single branch

Tag placement on `main`. `gh api tags` confirms `v1.10.0`, `v1.9.0`, `v1.8.0`, `v1.7.0`, `v1.6.0` all on main. No `release/*` or `v*` legacy branches. Pre-release suffixes none — all tags are clean `vX.Y.Z`. Pre-commit version bump no — version bumping is explicit via `scripts/release.sh VERSION`, a shell script that bumps 17 files, verifies they exist, then creates commit + tag. Dev-counter scheme absent — `plugin.json` on main sits at the latest released version (`1.10.0`), not a monotonic `0.0.z` counter.

## Plugin-component registration

### Asymmetric registration: file paths for agents, directory for skills/commands

`plugin.json` enumerates 38 explicit file paths for `agents` (e.g., `./agents/architect.md`), but uses directory references `["./skills/"]` and `["./commands/"]` for skills and commands. The author's own `PLUGIN_SCHEMA_NOTES.md` documents that the validator rejects `"agents": ["./agents/"]` (directory paths) with error `"agents: Invalid input"` — they hit the validator restriction and enumerated all 38 agents by hand, while keeping directory references for `skills`/`commands` either because those fields have different validator rules or they are tolerated under `strict: false`.

### Hooks at well-known path without `plugin.json` reference

`hooks/hooks.json` exists at repo root but is not referenced from `plugin.json`. The hooks are loaded by the repo's `install.sh`/`scripts/install-apply.js` installer at install time rather than referenced from the manifest. Marketplace-flow installs that bypass the legacy installer may not pick up hooks at all — completeness of hooks via the plugin runtime is uncertain.

### `.mcp.json` sibling file

`.mcp.json` sits at repo root with 6 MCP servers: github, context7, exa, memory, playwright, sequential-thinking. No MCP reference in `plugin.json`.

## Agent declaration conventions

### Plain tool-name list

Agent frontmatter uses `tools` as a JSON array of plain tool names (`["Read", "Grep", "Glob", "Bash"]`). No permission-rule syntax like `Bash(uv run *)`. Sample from `agents/planner.md`: `name: planner`, `description: "Expert planning specialist for complex features and refactoring..."`, `tools: ["Read", "Grep", "Glob"]`, `model: opus`. Sample from `agents/code-reviewer.md`: `tools: ["Read", "Grep", "Glob", "Bash"]`, `model: sonnet`.

### Standard fields plus model / color

Agent frontmatter fields: `name`, `description`, `tools`, `model`. Models split between `opus` and `sonnet` per agent role (planner uses opus; code-reviewer uses sonnet). No `skills`, `memory`, `background`, `isolation`, or `allowed-tools` fields observed.

## Component composition

### Skills (universal)

156 skills per README claim under `./skills/` directory reference.

### Commands

72 legacy command shims per README under `./commands/` directory reference.

### Agents

38 agents enumerated by explicit file path in `plugin.json` (e.g., `./agents/architect.md`).

### Hooks

`hooks/hooks.json` covering PreToolUse, PostToolUse, SessionStart, PreCompact, Stop, SessionEnd. Not referenced by `plugin.json` — loaded by the installer.

### MCP servers

`.mcp.json` at repo root with 6 servers (github, context7, exa, memory, playwright, sequential-thinking).

## Dependency installation

### Repo-local Node install via shell wrapper

Mixed runtime — Node (primary) + Python (secondary for `src/llm` abstraction layer + `ecc_dashboard.py`). `install.sh` (POSIX bash) and `install.ps1` (PowerShell) at repo root. Bash wrapper resolves symlinks, cygpath-converts on MSYS2, then execs `node scripts/install-apply.js "$@"`. Runs `npm install --no-audit --no-fund` only if `node_modules` is missing (existence-only change detection: `if [ ! -d "$SCRIPT_DIR/node_modules" ]`); installs land in repo-local `node_modules`, not `${CLAUDE_PLUGIN_DATA}` or an isolated venv. Failure signaling via `set -euo pipefail` halt with non-zero exit and npm's stderr surfaced; no structured JSON `systemMessage` or hook `continue: false`. Manifests: `package.json` + `package-lock.json` + `yarn.lock` (Yarn-native but all PM lockfiles present for CI matrix); `pyproject.toml` for the Python `src/llm` subpackage uses hatchling build-backend with classic pip-style optional-dependencies. Python `uv` is not used. The marketplace-flow plugin install bypasses `install.sh` entirely; whether plugins-flow users get hooks and assets installed correctly is uncertain.

## Plugin-runtime root resolution

### Centralized inline-bootstrap dispatcher

Every hook command in `hooks.json` is ~1.5KB of inline `node -e "..."` boilerplate that re-implements `CLAUDE_PLUGIN_ROOT` resolution across a fallback chain: env var → `~/.claude` direct → 6 well-known plugin slug paths (including both `ecc` and legacy `everything-claude-code`, plus `@ecc`, `marketplace/ecc`, `everything-claude-code@everything-claude-code`, `marketplace/everything-claude-code`) → versioned cache dirs under `~/.claude/plugins/cache/`. The bootstrap then hands off to `plugin-hook-bootstrap.js` which calls `run-with-flags.js {event-id} {handler-script-path} {profile-flags}` — a hook profile gating layer (`standard`, `strict`) that allows hooks to opt in/out based on user-selected discipline level. The `ECC_GOVERNANCE_CAPTURE=1` env-var opt-in for governance hooks is part of this profile system. SessionStart was specifically extracted to a standalone file (`session-start-bootstrap.js`) because inline `node -e` with `!` characters (used in `!org.isDirectory()`) was triggering bash history expansion and producing visible "SessionStart:startup hook error" entries in the Claude Code CLI header. The other 15+ hooks still embed the inline bootstrap.

## Tool-use enforcement

### PreToolUse advisory injection (no blocking)

Multiple PreToolUse hooks in `hooks.json` operate as advisory injections that `exit 0` after emitting stderr warnings: `pre:write:doc-file-warning` (matcher `Write`) warns about non-standard doc files; `pre:edit-write:suggest-compact` (matcher `Edit|Write`) suggests manual `/compact` at intervals; `pre:observe:continuous-learning` (matcher `*`) captures tool-use observations async with 10s timeout; `pre:edit-write:gateguard-fact-force` (matcher `Edit|Write|MultiEdit`, 5s timeout) blocks first edit per file and demands investigation before allowing.

### Multi-pattern PreToolUse safety stack

9 PreToolUse hooks observed plus 6+ PostToolUse hooks form a safety stack with mixed posture: infrastructure hooks fail-closed; observational hooks fail-open. PreToolUse entries: `pre:bash:dispatcher` (matcher `Bash`) consolidated Bash preflight dispatcher (quality, tmux, push, GateGuard); `pre:governance-capture` (matcher `Bash|Write|Edit|MultiEdit`, opt-in via `ECC_GOVERNANCE_CAPTURE=1`, 10s timeout); `pre:config-protection` (matcher `Write|Edit|MultiEdit`, 5s timeout) blocks mods to linter/formatter config files; `pre:mcp-health-check` (matcher `*`) checks MCP server health before MCP tool execution. PostToolUse entries: `post:bash:dispatcher` (matcher `Bash`, async, 30s) for logging/PR/build notifications; `post:quality-gate` (matcher `Edit|Write|MultiEdit`, async, 30s) for fast quality checks; `post:edit:design-quality-check` (matcher `Edit|Write|MultiEdit`) warns on generic-template UI drift; `post:edit:accumulator` (matcher `Edit|Write|MultiEdit`) records edited JS/TS paths for batch format+typecheck at Stop; `post:edit:console-warn` (matcher `Edit`) warns about console.log; `post:governance-capture` (matcher `Bash|Write|Edit|MultiEdit`) captures governance from outputs.

### Fact-forcing first-edit gate

`pre:edit-write:gateguard-fact-force` (matcher `Edit|Write|MultiEdit`, 5s timeout) blocks the first `Edit`/`Write`/`MultiEdit` per file and demands investigation (importers, data schemas, user instruction) before allowing.

## Hook output contract

### Stderr for human display + stdout JSON for harness

Per `hooks/README.md`: "PreToolUse hooks can **block** (exit code 2) or **warn** (stderr without blocking)." Stderr human-readable plus exit-code gated. No stdout JSON systemMessage convention observed at this layer.

## Hook failure posture

### Mixed posture (fail-closed for security, fail-open for context)

`hooks/README.md` explicitly annotates each hook's exit behavior ("2 (blocks)" vs "0 (warns)"). Infrastructure hooks (MCP health check, config protection, GateGuard) fail-closed; observational hooks (continuous learning, design quality) fail-open. Top-level try/catch wrapping is observed in the bootstrap shim — the inline `node -e` fallback-root resolution is wrapped `try { ... } catch(x) {}` and `plugin-hook-bootstrap.js` does top-level error-silencing for the resolver.

## Hook timeout and async philosophy

### Differentiated per-hook timeouts

Each hook entry carries an explicit `timeout` sized to its role: 5s for blocking guards (`pre:edit-write:gateguard-fact-force`, `pre:config-protection`); 10s for governance/observation hooks (`pre:observe:continuous-learning`, `pre:governance-capture`); 30s for `post:bash:dispatcher` and `post:quality-gate` which carry `async: true` so the agent does not wait. Three different latency budgets across hooks in one plugin.

## Session context loading

### SessionStart with structured handler in standalone file

`session:start` hook (matcher `*`) runs `session-start-bootstrap.js` → `run-with-flags.js session:start` → handler. Documented purpose: "Load previous context and detect package manager on new session." SessionStart is the only hook extracted to a standalone file specifically because inline `node -e` with `!` characters was triggering bash history expansion and producing visible "SessionStart:startup hook error" entries in the CLI header — the other 15+ hooks still embed the inline bootstrap. Whether the downstream handler emits `hookSpecificOutput.additionalContext` JSON or just stderr/stdout strings is unverified.

## SessionStart matcher scope

### Empty matcher (all sub-events)

SessionStart matcher is `*` — fires on all sub-events including startup, clear, and compact.

## Live monitoring

### `monitors.json` absent

No `monitors.json` (`gh api contents/monitors.json` returned 404).

### Stop-hook driven desktop notification

Notification-like behavior is implemented at the hook layer, not via the dedicated monitors.json surface — `desktop-notify.js` sends macOS desktop notifications after Stop events per the `hooks/README.md` table.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field declared on the single plugin entry. Single-plugin aggregator marketplace — everything is self-contained. Tags are plain `vX.Y.Z`, not the `{plugin-name}--v{version}` cross-plugin format.

## Testing

### Mixed `node:test` + pytest with custom runner

Primary tests use `node:test` via `tests/**/*.test.js`, executed by `tests/run-all.js` — a custom runner that globs `tests/**/*.test.js`, spawnSyncs each via `spawnSync('node', [testPath])`, aggregates pass/fail in an ASCII box. Plus pytest for the `src/llm` Python subpackage via `tests/docs`/`tests/integration` per `pyproject.toml`'s `[tool.pytest.ini_options]` (`testpaths = ["tests"]`, `asyncio_mode = "auto"`, `filterwarnings = ["ignore::DeprecationWarning"]`). Python deps via `[project.optional-dependencies] dev = ["pytest>=8.0", "pytest-asyncio>=0.23", "pytest-cov>=4.1", "pytest-mock>=3.12", "ruff>=0.4", "mypy>=1.10"]`. Tests location: `tests/` at repo root with subdirectories (`tests/hooks/`, `tests/integration/`, `tests/lib/`, `tests/docs/`, `tests/scripts/`, `tests/ci/`); root-level test files mix Python pytest and JS node:test at the same level (`test_builder.py`, `codex-config.test.js`, `plugin-manifest.test.js`). There is also `tests/plugins/everything-claude-code/` containing one file. Custom runner only invokes Node tests — pytest is configured but orphaned from CI. Hook surface has mature coverage (`tests/hooks/*.test.js`, 20+ files).

## CI workflow shape

### Multi-job matrix with parallel test/validate/security/lint

Seven workflows in `.github/workflows/`: `ci.yml`, `release.yml`, `maintenance.yml`, `monthly-metrics.yml`, `reusable-test.yml`, `reusable-release.yml`, `reusable-validate.yml`. Triggers: `ci.yml` on `push: branches: [main]` + `pull_request: branches: [main]`; `release.yml` on `push: tags: ['v*']`; `maintenance.yml` on `schedule: '0 9 * * 1'` + `workflow_dispatch`; `monthly-metrics.yml` on `schedule: '0 14 1 * *'` + `workflow_dispatch`; reusable-* on `workflow_call` (+ `workflow_dispatch` for reusable-release). `ci.yml` defines four parallel jobs — `test` (matrix-runs `node tests/run-all.js`), `validate` (10 validator scripts), `security` (npm audit `--audit-level=high`, continue-on-error), `lint` (ESLint on scripts/tests + markdownlint on agents/skills/commands/rules). Matrix is `[ubuntu-latest, windows-latest, macos-latest] × [18.x, 20.x, 22.x] × [npm, pnpm, yarn, bun]` with `exclude: bun on windows-latest`. Net 33 lanes. `fail-fast: false`. The reusable-* workflows exist but `ci.yml` and `release.yml` inline-copy their content rather than `uses:`-ing them — duplicated workflow bodies have already drifted (`REF_NAME` vs `inputs.tag`) — a migration-in-progress.

### Action-pinning conventions

Every action is pinned by 40-char SHA with a `# vX.Y.Z` comment annotation (e.g., `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2`). Consistent across all workflows.

### Test workflow with pinned actions, no caching

Caching uses `actions/cache` keyed per-PM (npm/pnpm/yarn/bun), scoped by `runner.os`-`node-version`-`pm`-`hashFiles(<lockfile>)`. The built-in setup-node cache is NOT used; explicit `actions/cache` steps per package manager instead.

## Marketplace validation

### Multi-validator composition

`validate` job in `ci.yml` runs 10 discrete validators sequentially with `continue-on-error: false`: `validate-agents.js`, `validate-hooks.js`, `validate-commands.js`, `validate-skills.js`, `validate-install-manifests.js` (cross-ecosystem manifest sync verification), `validate-workflow-security.js` (GitHub Actions hygiene — SHA-pinning, minimal permissions), `validate-rules.js`, `catalog.js --text`, `check-unicode-safety.js` (invisible-unicode/zero-width-character injection check, an AI-agent prompt-injection vector). Frontmatter validation for agents/skills/commands is presumed but not directly inspected. `reusable-validate.yml` wraps the same checks for `workflow_call`.

### Reverse-engineered validator notes as primary-source artifact

`.claude-plugin/PLUGIN_SCHEMA_NOTES.md` documents undocumented Claude Code plugin validator constraints reverse-engineered from real install failures: `version` is mandatory (not just recommended); `agents`/`commands`/`skills`/`hooks` must be arrays (strings rejected even for single entries); `agents` MUST be explicit file paths, with directory paths rejecting under error string `"agents: Invalid input"`. The artifact is a hand-written document that accumulates real-world failure-mode evidence for downstream consumers.

## Release automation

### Tag-triggered release with multi-gate sanity (npm)

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`; `reusable-release.yml` is `workflow_call` + `workflow_dispatch` (for republish scenarios). Three tag-sanity gates run in sequence: tag format regex `^v[0-9]+\.[0-9]+\.[0-9]+$` (no pre-release suffixes); tag equals `package.json` version (shell-strips `v` prefix and compares to `node -p "require('./package.json').version"`); `plugin-manifest.test.js` runs as part of the release job ("Verify release metadata stays in sync") covering cross-manifest version drift. Conditional `npm publish --access public --provenance` (using `permissions: id-token: write`) gated by idempotency check `npm view "${NAME}@${VERSION}"`. GitHub Release created via `softprops/action-gh-release@b4309332981a82ec1c5618f44dd2e27cc8bfbfda # v3.0.0` with `body_path: release_body.md` (heredoc'd inline in the workflow with hardcoded section templates) plus `generate_release_notes: true`. The release body is essentially boilerplate marketing copy ("Harness reliability and hook stability across Claude Code, Cursor, OpenCode, and Codex") — actual per-release detail comes from auto-generated release notes. `reusable-release.yml` exposes a `tag` input for republish, but `release.yml` does not `uses:` it, so the republish capability is only available via manual reusable-workflow trigger.

## Documentation surface

### Multi-document agent-context layer

Repo root carries 14+ markdown files: `README.md` (multi-locale `docs/<locale>/`), `CHANGELOG.md`, `CLAUDE.md`, `AGENTS.md`, `RULES.md`, `SOUL.md`, `TROUBLESHOOTING.md`, `WORKING-CONTEXT.md`, `EVALUATION.md`, `REPO-ASSESSMENT.md`, `COMMANDS-QUICK-REF.md`, `SPONSORING.md`, `SPONSORS.md`, plus `the-longform-guide.md`, `the-shortform-guide.md`, `the-security-guide.md`. Multi-language READMEs for pt-BR, zh-CN, zh-TW, ja-JP, ko-KR, tr under `docs/<locale>/` plus a top-level `README.zh-CN.md`. Release.sh bumps version only in README.md and docs/zh-CN/README.md — the other locales (pt-BR, zh-TW, ja-JP, ko-KR, tr) drift between releases. Single-plugin marketplace, so `.claude-plugin/README.md` exists as a marketplace-metadata description. No top-level `architecture.md` (a `docs/SELECTIVE-INSTALL-ARCHITECTURE.md` covers one specific subsystem).

### Free-form CHANGELOG variants

`CHANGELOG.md` follows a custom format with per-release headings and sub-sections (Highlights, Release Surface, New Workflow Lanes, ECC 2.0 Alpha, Notes) — not Keep a Changelog. Chronological reverse-order. The CHANGELOG is maintained separately and not programmatically consumed by the release workflow (which heredocs its own `release_body.md` from hardcoded templates).

### Marketing-grade README (40+ KB)

README has heavy badge header (9+ badges: stars, forks, contributors, npm weekly downloads for two packages, GitHub app installs, license, language icons, Anthropic-hackathon-winner blockquote) and is referenced by README badges and ToC. Top-level `the-longform-guide.md`, `the-shortform-guide.md`, `the-security-guide.md` add prose guides parallel to the README. SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md all present.

### Multi-language READMEs

`README.md` plus `README.zh-CN.md` at root, plus per-locale READMEs at `docs/<locale>/` (pt-BR, zh-CN, zh-TW, ja-JP, ko-KR, tr). Release.sh bumps version in README.md and docs/zh-CN/README.md only; the other locales drift unsyncronized.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` (MIT) at repo root. SPDX `MIT` declared via `package.json`'s `license` field and the marketplace entry's `license` field. Single source of truth for the license declaration.

## Community health files

### Open contribution with health files

`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` all present at repo root.

### LICENSE + CODE_OF_CONDUCT + issue templates

Repo root carries LICENSE plus full community health stack including CODE_OF_CONDUCT.md.

## Cross-ecosystem distribution

### Cross-ecosystem multi-harness distribution

The same plugin payload ships via parallel manifests for sibling AI harnesses: `.codex-plugin/plugin.json` (Codex), `.opencode/package.json` + `.opencode/package-lock.json` + `.opencode/plugins/ecc-hooks.ts` (OpenCode), `.agents/plugins/marketplace.json` (Cursor/Gemini cross-target). Release.sh treats all manifests as version-locked; `validate-install-manifests.js` validates cross-ecosystem manifest sync as a CI step. Cross-ecosystem changes ripple back into the Claude release through the 17-file version sprawl.

### Dual-distribution: marketplace + npm

The same source ships as both a Claude Code plugin marketplace entry and the `ecc-universal` npm package. The npm `package.json` `files:` list includes the entire plugin payload (`install.sh`, `install.ps1`, `scripts/*.js`, `.agents/`, `.codex/`, `.opencode/` sibling directories). Users can `npm install -g ecc-universal` or use the plugin via the Claude marketplace. `package.json.bin` is not declared (no npm bin entry), but the npm package exposes the plugin payload's directory layout for manual consumption. Every release must satisfy both packaging contracts; CI's release gate verifies tag against `package.json` version, but cross-manifest version drift is not gated against the other 16 version-bearing files.
