# Sample

Mirrors of `https://github.com/anthril/official-claude-plugins`. A curated 10-plugin marketplace under `plugins/<name>/` covering data-analysis, knowledge-engineering, business-economics, business-operations, brand-manager, database-design, npm-package-audit, plan-completion-audit, ppc-manager, skill-creator, software-development. 2 stars; default branch `main`; MIT license at root with per-skill Apache-2.0 LICENSE.txt and ppc-manager carrying its own LICENSE; latest commit 2026-04-20.

## Marketplace manifest layout

### Single root manifest with relative source under `plugins/<name>/`

Single `.claude-plugin/marketplace.json` at repo root aggregating 10 plugins under `plugins/<name>/`. Each entry uses `"source": "./plugins/<name>"`. Top-level keys are flat — `name` (`anthril-claude-plugins`), `description`, `owner.{name, email}`, and `plugins`. No `metadata` wrapper, no `metadata.pluginRoot`, no `version` at the marketplace root.

### `$schema` declaration on marketplace.json

Marketplace document declares `"$schema": "https://anthropic.com/claude-code/marketplace.schema.json"`. No CI step actively validates against the schema; the field provides editor assistance only.

## Per-plugin discoverability metadata

### Category-only

Every plugin entry carries a `category` string with values `data-analysis`, `knowledge-engineering`, `business-operations`, `developer-tools`, or `marketing`. No `tags`, no `keywords` on any entry. Every entry also carries a `homepage` deep-linking to `/tree/main/plugins/<name>`. No `version` field on any marketplace entry, even though `scripts/check-versions.mjs` (run in CI) expects every entry to have `version` and emits `"marketplace entry is missing 'version' (required for relative-path plugins)"` for each plugin on mismatch — internal inconsistency between the validator's expectation and the live state. README documents 9 plugins while the marketplace registers 10 (database-design was added without updating README's count).

### `$schema` absence on per-plugin manifests

`$schema` URL absent from every shipped `plugin.json` across the 10 plugins.

## Plugin source binding

### Relative source pointing to subdirectory

Every entry uses `"source": "./plugins/<name>"` (uniform across all 10 plugins). The `./` prefix concatenates with `metadata.pluginRoot` (defaulted to `.`) via `join(repoRoot, pluginRoot, source)` in `check-versions.mjs`. The CLAUDE.md template for new-plugin registration shows `"source": "plugin-name"` (no `./` prefix), inconsistent with the actual file's `"./plugins/plugin-name"` form.

## Version coordination

### Single source of truth (`plugin.json` only)

`plugin.json.version` is the only user-facing version of record; marketplace entries omit `version` entirely (despite the validator expecting it). `.claude/CLAUDE.md` and `check-versions.mjs` both treat the two as dual sources with `plugin.json` as "the source of truth that Claude Code silently lets win" per the script's banner comment. Several plugins have advanced beyond the single repo-wide `v1.0.0` tag — `database-design` at `1.1.0`, `ppc-manager` at `1.0.1`, `data-analysis` at `1.0.1` — without follow-up tags being cut.

## Channel distribution

### No pinning surface

No channel split. Single repo-wide `v1.0.0` tag exists on main but no matching GitHub Release was published. Several plugins are at `1.0.1` or higher in their own `plugin.json` (database-design at `1.1.0`, ppc-manager at `1.0.1`); the tag predates these bumps and no follow-up tags have been cut. Users who pin `@v1.0.0` get stale plugins. No `{plugin-name}--v{version}` tag format observed.

## Tag and release lifecycle

### Single lifetime tag with drift

A single `v1.0.0` tag on main, repo-wide (not plugin-scoped). Several plugins ship `1.0.1` or `1.1.0` in their own `plugin.json` while the tag stays at `v1.0.0`. Tag predates the bumps; no follow-up tags. Root `CHANGELOG.md` shows `[1.0.0] - 2025-05-20` listing 6 plugins with 14 skills — out of sync with current state (10 plugins, ~48 skills, several at 1.0.1/1.1.0).

## Plugin-component registration

### Default convention discovery

Every shipped `plugin.json` is minimal — `name`, `version`, `description`, `author` only — with no explicit component paths. Component discovery relies entirely on defaults: skills auto-discovered under `skills/`, hooks loaded from `hooks/hooks.json` at plugin root, `.mcp.json` at plugin root. The contributor-facing `.claude/CLAUDE.md` advertises `"skills": "./skills/"` and `"hooks": "./hooks/hooks.json"` as explicit path fields; `tests/lint/test_manifests.py` asserts that `license`, `keywords`, `skills`, and `userConfig` must be present in plugin.json — but the live `plugin.json` files do not contain any of these. Documentation and tests describe an intended state that shipping code does not match.

### Inline `mcpServers` definition in `plugin.json`

ppc-manager only — `.mcp.json` at the ppc-manager plugin root declares 4 MCP servers (the other 9 plugins have no MCP servers). No inline `mcpServers` in `plugin.json`; MCP definitions live in the sibling `.mcp.json`.

## Component composition

### Skills (universal)

All 10 plugins ship skills under `skills/<name>/SKILL.md`. ~48 skills total across the marketplace per README.

### Agents

Only ppc-manager ships an agent (`agents/campaign-auditor.md`).

### Hooks

7 of 10 plugins ship `hooks/hooks.json`.

### MCP servers

ppc-manager only — `.mcp.json` declaring 4 servers.

### bin

ppc-manager only — `bin/python_shim.sh` (POSIX) and `bin/python_shim.ps1` (Windows).

## Skill authoring conventions

### `compatibility:` prose

SKILL.md frontmatter includes free-form `compatibility:` prose declaring platform prerequisites.

### `context: fork` invocation hint

`campaign-audit/SKILL.md` declares `context: fork` plus `agent: campaign-auditor` in frontmatter to drop into an isolated sub-agent context defined by the sibling `agents/campaign-auditor.md` file.

## Agent declaration conventions

### `model` + `effort` + `maxTurns` for cost control

`agents/campaign-auditor.md` declares `model: sonnet`, `effort: max`, plus `tools: Read Grep Bash` (plain space-separated tool names, not permission-rule syntax). No `skills`, `memory`, `background`, `isolation`, or `context` on the agent itself; the invoking skill's `context: fork` + `agent:` frontmatter handles the dispatch.

## Dependency installation

### SessionStart-driven Python venv with hash gating

ppc-manager only — the one plugin with Python runtime deps. `plugins/ppc-manager/hooks/scripts/ensure-venv.sh` (POSIX) and `ensure-venv.ps1` (Windows sibling) wired via `SessionStart` in `hooks/hooks.json` with `timeout: 180`. The hook creates a venv under `${CLAUDE_PLUGIN_DATA}/venv/` from `requirements.txt` (no `pyproject.toml`, no `setup.cfg`); on POSIX uses `diff -q requirements.txt requirements.stamp` for change detection; on Windows uses `Get-FileHash` SHA256 equality. The stamp file is a verbatim copy of `requirements.txt` written via `cp "$REQ" "$STAMP"` after `pip install -r` succeeds — the write-after-success structure preserves the retry invariant: failure leaves the stamp absent or stale, so the next session re-attempts on the diff. On pip failure the script emits `{"systemMessage": "pip install failed. See .../install.log"}` and `exit 0` without removing the stamp; pip stderr redirects to `${CLAUDE_PLUGIN_DATA}/install.log` for postmortem. Runtime is Python stdlib `venv` + pip (no `uv`, no `uvx`); requires Python 3.11+ on `$PATH`; interpreter resolved via `command -v python3 || command -v python` (POSIX) or `python || py -3` (Windows); override via `PPC_PYTHON` env var. Python version guard (`sys.version_info >= (3, 11)`) runs before venv creation; on fail emits systemMessage and `exit 0`.

## Bin entry mechanism

### Pointer-file shim invoked via `.mcp.json`

ppc-manager only. `bin/python_shim.sh` (`#!/usr/bin/env bash`, POSIX) and `bin/python_shim.ps1` (PowerShell sibling, no shebang). The POSIX shim reads `${CLAUDE_PLUGIN_DATA}/python_path.txt` (written by `ensure-venv.sh`), validates the path is executable (`-x` or `-f`), then `exec "$PY" "$@"`. PowerShell sibling does the same on Windows via `& $py @args`. `.mcp.json` invokes via `bash ${CLAUDE_PLUGIN_ROOT}/bin/python_shim.sh <server.py>` — the `.ps1` shim is not referenced anywhere in `.mcp.json`, leaving Windows users dependent on Git Bash or WSL. `CLAUDE_PLUGIN_DATA` defaults to `$HOME/.claude/plugins/data/ppc-manager` (POSIX) or `$USERPROFILE\.claude\plugins\data\ppc-manager` (Windows) when unset. SessionStart relationship: `ensure-venv.sh` (180s timeout) writes `python_path.txt`; `check-credentials.sh` (15s timeout) consumes `python_path.txt` to run `token_validator.py --quiet --json`; `bin/python_shim.sh` consumes the same file at MCP launch. If `ensure-venv.sh` has never succeeded (e.g. Python 3.11 unavailable on first session), `python_path.txt` is missing and `python_shim.sh` exits 127 with a corrective message; recovery requires installing Python and restarting Claude Code.

## User configuration and authentication

### `userConfig` declared but not wired through manifest substitution

The shipped `plugin.json` files (all 10) contain only name/version/description/author — no `userConfig` block. The intended design surfaces in three places: `.mcp.json` references eight `${user_config.*}` placeholders (e.g., `${user_config.ppc_vault_passphrase}`, `${user_config.google_ads_developer_token}`, `${user_config.meta_app_id}`, `${user_config.meta_app_secret}`); `tests/lint/test_manifests.py` asserts `userConfig` must include `ppc_vault_passphrase`, `google_ads_developer_token`, `meta_app_secret`, `meta_app_id`, and `google_ads_login_customer_id`, with `sensitive: true` on the first three; README states "On first enable, Claude Code prompts you for the 8 `userConfig` fields." Installing the plugin today would leave every `${user_config.*}` unresolved and every MCP server would start with empty values, causing `check-credentials.sh` to emit "vault passphrase not set" — the pattern is documented but the materialization is incomplete.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

Hooks read process env vars directly. `check-credentials.sh` reads `CLAUDE_PLUGIN_OPTION_PPC_VAULT_PASSPHRASE` directly; `.mcp.json` env values use both `${user_config.KEY}` (for MCP-server consumption) and `CLAUDE_PLUGIN_OPTION_<KEY>` (for hook-script consumption) — the same user_config field is materialised twice per server entry under different names, a double-binding compared to the more common single-projection pattern.

## Tool-use enforcement

### PreToolUse Bash matcher as ask-first guardrail

`npm-package-audit` ships a PreToolUse hook with `matcher: "Bash"` running `check-npm.sh` to verify `npm` and `node` are on PATH. One-shot per session — the script writes `/tmp/.npm-package-audit-check-done` as a flag file to gate to first invocation. Flag is never cleared; mid-session changes (e.g., user installs npm later) are not re-detected, and the global `/tmp/` path collides on multi-user systems.

### Hard-blocking PreToolUse on commit-shape invariants

`skill-creator/hooks/scripts/pre-write-skill.sh` runs on `matcher: "Write"`, hard-blocks SKILL.md writes missing `$ARGUMENTS` via `exit 2` and stderr error message. Uses `set -euo pipefail`. Fail-open on environmental gap (`jq` not installed → `exit 0`, graceful degradation). Header comment reads "AI Cookbook — PreToolUse hook" suggesting copy-paste origin from another project.

### Format-then-lint PostToolUse (non-blocking)

`skill-creator` ships PostToolUse hooks on `matcher: "Write|Edit"` running `post-edit-skill.sh` and `post-edit-script.sh` — content not verified but named for skill/script edit validation.

## Session context loading

### SessionStart welcome banner via `systemMessage`

`data-analysis`, `business-economics`, `knowledge-engineering`, `plan-completion-audit`, and `skill-creator` all use `welcome.sh` SessionStart hooks emitting `{"systemMessage": "..."}` JSON with skill count and line-count warnings (a lint-in-banner convention). No SessionStart matcher on any entry — fires on all sub-events (startup, clear, compact), so `welcome.sh` re-emits the banner mid-session on every clear/compact. ppc-manager's SessionStart is exclusively for `ensure-venv.sh` + `check-credentials.sh` (no welcome banner).

### Per-prompt context reminder

`suggest-related.sh` (data-analysis) and `suggest-next-skill.sh` (ppc-manager) use UserPromptSubmit/Stop hooks for skill-chain navigation. The data-analysis variant has a defect — it `echo "$TRANSCRIPT" | grep`s the transcript path string itself rather than the transcript contents, so any skill name in the transcript filename matches by coincidence or never matches otherwise. ppc-manager's `suggest-next-skill.sh` is correctly implemented — it `tail -200 "$TRANSCRIPT" | grep`s the file's actual tail content.

## Plugin-to-plugin coordination

### Skill chaining via Stop-hook tail-grep

ppc-manager's `suggest-next-skill.sh` tails the last 200 lines of `$CLAUDE_TRANSCRIPT`, matches the most recent skill invocation, and emits a `systemMessage` recommending the next skill in the encoded skill DAG. The 23 ppc-manager skills form a directed chain that this hook navigates the user through.

### `dependencies` field absent

No `plugin.json` declares the schema-level `dependencies` field. Plugins are flat and independent. `{plugin-name}--v{version}` tag format not observed; only a single repo-wide `v1.0.0` tag.

## Testing

### Pytest scoped to one plugin within a marketplace

Tests live inside one plugin only — `plugins/ppc-manager/tests/{unit,integration,lint}/` (17 test modules total). The other 9 plugins ship zero tests. Pytest config is absent (no `pyproject.toml`, no `pytest.ini`, no `setup.cfg`); `plugins/ppc-manager/tests/conftest.py` handles `sys.path` shimming (inserts `scripts/` onto `sys.path`). Local invocation via the plugin's own `Makefile` (`make test` / `make test-live` / `make coverage`); `requirements-dev.txt` is separate from runtime `requirements.txt`. Test runner is NOT invoked from CI — `validate-marketplace.yml` runs only JSON and version-sync validation.

## CI workflow shape

### Single-runner JSON validation only

Two workflows in `.github/workflows/`: `validate-marketplace.yml` (push to main, PR to main, workflow_dispatch) runs only `node -e "JSON.parse(...)"` on `marketplace.json` and every `plugins/*/.claude-plugin/plugin.json`, then `node scripts/check-versions.mjs` for cross-manifest version sync. No matrix (single Node 20 on ubuntu-latest); no caching; actions tag-pinned (`@v4`, `@v1`), not SHA-pinned. Test suites are not invoked by CI.

## Marketplace validation

### JSON-parse plus version-sync only

Validation runs as `node -e "JSON.parse(...)"` against `marketplace.json` and each `plugin.json`, plus `scripts/check-versions.mjs` comparing marketplace-entry `version` against `plugin.json` version. Frontmatter validation absent (although a pytest lint module `tests/lint/test_skill_structure.py` exists, it is not run by CI). Hooks.json validation absent. `check-versions.mjs` uses `metadata.pluginRoot` defaulted to `.` and joins paths; `join(repoRoot, '.', './plugins/<name>')` resolves correctly on POSIX. Frontmatter parsing in `tests/lint/test_skill_structure.py` references an `allowed-tools` field that every observed SKILL.md declares with space-separated string scalar values (`Read Write Edit Grep Bash Agent`). `argument-hint` uses prose-bracketed placeholders (e.g., `[platform-and-account-id]`). The `ultrathink` token appears as a standalone body line (not a frontmatter key) in campaign-audit and dead-code-audit, while brand-identity has no ultrathink at all.

## Release automation

### No release automation / manual

No `release.yml` workflow. Releases are not automated. The single `v1.0.0` tag was cut manually; no GitHub Release artifact was published (`releases: []`). CHANGELOG.md exists at root and at `plugins/ppc-manager/CHANGELOG.md` (both Keep-a-Changelog format, both covering only `1.0.0`); neither is consumed by any workflow. No tooling enforces that plugin.json version bumps get tagged.

### Sponsor automation as scheduled workflow

`sponsors.yml` runs daily (`schedule: "0 6 * * *"`) plus `workflow_dispatch`, using `JamesIves/github-sponsors-readme-action@v1` six times (one per pledge tier — Founding/Partners/Backers/Builders/Supporters/Featured) with pledge-range gating, plus `JamesIves/github-pages-deploy-action@v4`. The deploy-action targets `branch: master` with `folder: "."` while the default branch is `main` — this would fail on first run because no `master` ref exists.

## Documentation surface

### Layered repo / plugin / skill READMEs (uneven)

Repo-root `README.md` (~15 KB) describes the marketplace, install, lists every skill per plugin with one-line description in tables, includes directory-layout tree, quality checklist, contributing section. Per-plugin READMEs are uneven — `brand-manager`, `database-design`, `ppc-manager`, and `software-development` ship them; `business-economics`, `data-analysis`, `knowledge-engineering`, `npm-package-audit`, `plan-completion-audit`, and `skill-creator` do not. Each skill ships a SKILL.md. `plugins/ppc-manager/docs/architecture.md` (~12 KB) is the only architecture document — covering directory layout, data-flow, MCP server tool surface, auth library design, hook system, test strategy, dependency graph, extension guide. No repo-root architecture.md. Other structurally substantial plugins (brand-manager with 9 skills, database-design) ship no architecture document.

### CLAUDE.md as project-config surface

`.claude/CLAUDE.md` (repo root) carries development standards — Australian English mandate, skill structure, SKILL.md frontmatter schema, plugin manifest template, marketplace registration template, hooks conventions, version management, quality checklist. CLAUDE.md templates an explicit plugin.json shape that the actual plugin.json files don't follow. No per-plugin CLAUDE.md.

### Free-form CHANGELOG variants

Root `CHANGELOG.md` is Keep-a-Changelog format covering only `1.0.0` dated 2025-05-20 (out of date vs live `1.0.1`/`1.1.0` plugin versions). Plugin-level `plugins/ppc-manager/CHANGELOG.md` is also Keep-a-Changelog format covering only `1.0.0` dated 2026-04-11. Neither is parsed by automation.

## License declaration

### Layered: repo-MIT, plugin-MIT, per-skill-Apache-2.0

Repo-root `LICENSE` is MIT (SPDX `MIT`). `ppc-manager` ships its own `LICENSE` (also MIT). Every skill ships a per-skill `LICENSE.txt` which is Apache 2.0 per README text — granular license delineation per skill within the plugin.

## Community health files

### Bare minimum (LICENSE only)

Root `LICENSE` (MIT) plus an auto-maintained `SPONSORS.md`. No `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE/`, no `.github/PULL_REQUEST_TEMPLATE.md`. README has no badges (no workflow badge, no version badge, no license badge).

## Locale and content-style enforcement

### Australian English mandate with lint check

`.claude/CLAUDE.md` and per-plugin tests prescribe "Australian English in all narrative text (colour, optimise, behaviour, organisation)" and ship `tests/lint/test_australian_english.py` to enforce the rule. Mechanism (word-list grep, regex, or AST) was not inspected from the test source.
