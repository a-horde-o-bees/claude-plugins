# anthril/official-claude-plugins

## Identification

- **URL**: https://github.com/anthril/official-claude-plugins
- **Stars**: 2
- **Last commit date**: 2026-04-20 (main); `pushed_at` 2026-04-20T10:56:05Z (observed via `gh api repos/...`)
- **Default branch**: main
- **License**: MIT (SPDX `MIT`, root `LICENSE`; ppc-manager also ships its own `LICENSE` and per-skill Apache 2.0 `LICENSE.txt` files)
- **Sample origin**: dep-management + bin-wrapper (both primary signals are ppc-manager's `ensure-venv.sh` → `python_path.txt` pointer file → `bin/python_shim.sh` exec chain)
- **One-line purpose**: "A curated collection of reusable AI skills, prompts, and agent configurations. Portable across AI coding assistants and agent frameworks." (from GitHub repo description; README opens with "A curated library of Claude Code plugins for data analysis, entity modelling, business operations, PPC management, and developer tooling — packaged as a Claude Code marketplace with standalone plugins.")

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, aggregator of 10 plugins under `plugins/<name>/`
- **Marketplace-level metadata**: no `metadata` wrapper; top-level `name`, `description`, `owner {name, email}` keys only — no `version` at the marketplace root
- **`metadata.pluginRoot`**: absent (per-plugin entries use explicit relative `source`)
- **Per-plugin discoverability**: `category` only on every plugin (values: `data-analysis`, `knowledge-engineering`, `business-operations`, `developer-tools`, `marketing`); `tags`/`keywords` absent from marketplace entries. `homepage` is present on every entry (deep link to `/tree/main/plugins/<name>`). No `version` on any entry (inferred contradiction with `scripts/check-versions.mjs`; see Pitfalls)
- **`$schema`**: present — `"$schema": "https://anthropic.com/claude-code/marketplace.schema.json"`
- **Reserved-name collision**: no (`anthril-claude-plugins` is the marketplace `name`, distinct from any reserved identifier we're aware of)
- **Pitfalls observed**: `scripts/check-versions.mjs` (run in CI) expects every plugin entry to have `version`, and on mismatch fails with exit 1 — but the live `.claude-plugin/marketplace.json` has zero `version` fields on any of the 10 entries. The script's own logic emits `"marketplace entry is missing 'version' (required for relative-path plugins)"` for each plugin, which implies CI is currently red against `main` or the script was added without the marketplace catching up. This is an observed internal inconsistency in the repo. Also: `.claude/CLAUDE.md` says marketplace entries "must match" plugin.json version, reinforcing the intent. README documents 9 plugins but the marketplace registers 10 (database-design was added without updating README's "9 standalone plugins" count).

## 2. Plugin source binding

- **Source format(s) observed**: relative only — every entry uses `"source": "./plugins/<name>"` (uniform across all 10 plugins)
- **`strict` field**: absent (default, implicit true)
- **`skills` override on marketplace entry**: absent — plugins self-describe their surface via their own `plugin.json` (plus skill directory conventions)
- **Version authority**: `plugin.json` only (observed) — marketplace entries carry none. The `.claude/CLAUDE.md` contributor doc and `check-versions.mjs` both treat the two as dual sources with `plugin.json` as the source of truth "that Claude Code silently lets win" per the script's own banner comment
- **Pitfalls observed**: Relative `source` paths in marketplace entries (`./plugins/data-analysis`) include a leading `./`, while `check-versions.mjs` concatenates them as-is onto `repoRoot` via `join(repoRoot, pluginRoot, source)` — works because `pluginRoot` defaults to `.` when `metadata.pluginRoot` is absent. The CLAUDE.md doc template for new-plugin registration shows `"source": "plugin-name"` (no `./`), inconsistent with the actual file's `"./plugins/plugin-name"` form.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via `@ref` implicitly via marketplace GitHub URL; only one ref (`main`)
- **Channel-pinning artifacts**: absent (no `stable-*`/`latest-*` marketplaces, no `release/*` branches, a single `v1.0.0` tag exists but no matching GitHub Release was published)
- **Pitfalls observed**: single `v1.0.0` tag exists (repo-wide, not plugin-scoped) while several plugins are at `1.0.1` or higher in their own `plugin.json` (database-design at `1.1.0`, ppc-manager at `1.0.1`). The tag predates these bumps and no follow-up tags have been cut, so users who pin `@v1.0.0` get stale plugins. No `{plugin-name}--v{version}` tag format observed.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: a single lifetime tag on main (`v1.0.0`)
- **Release branching**: none
- **Pre-release suffixes**: none observed
- **Dev-counter scheme**: absent
- **Pre-commit version bump**: no (no pre-commit config present, no `.pre-commit-config.yaml` in tree, no husky/lefthook)
- **Pitfalls observed**: Mismatch between root `CHANGELOG.md` (`[1.0.0] - 2025-05-20`, listing 6 plugins with 14 skills) and current state (10 plugins, ~48 skills, several at 1.0.1/1.1.0). The changelog has not been kept current; the README sits at "48 production-ready skills across nine standalone plugins" while the marketplace registers ten.

## 5. Plugin-component registration

- **Reference style in plugin.json**: observed in-the-wild plugin.json files are minimal (`name`, `version`, `description`, `author` only) with no explicit component paths — relies entirely on default discovery (skills auto-discovered under `skills/`, hooks loaded from `hooks/hooks.json` at plugin root, `.mcp.json` at plugin root). The `.claude/CLAUDE.md` contributor doc advertises `"skills": "./skills/"` and `"hooks": "./hooks/hooks.json"` as explicit path fields, and `tests/lint/test_manifests.py` asserts `license`, `keywords`, `skills`, `userConfig` must be present — but the live `plugin.json` files do not contain any of these. Documentation and tests describe an intended state that shipping code does not match.
- **Components observed (across plugins/)**: skills yes; commands no; agents yes (ppc-manager/agents/campaign-auditor.md only); hooks yes (7 of 10 plugins ship `hooks/hooks.json`); `.mcp.json` yes (ppc-manager only, 4 servers); `.lsp.json` no; monitors no; bin yes (ppc-manager only, `bin/python_shim.sh` + `.ps1`); output-styles no
- **Agent frontmatter fields used**: `name`, `description`, `model` (`sonnet`), `effort` (`max`), `tools` (plain `Read Grep Bash`, space-separated). No `skills`, `memory`, `background`, `isolation`, or `context` on the agent itself, though the invoking skill frontmatter uses `context: fork` + `agent: campaign-auditor` to drop into the sub-agent
- **Agent tools syntax**: plain space-separated tool names (`tools: Read Grep Bash`), not permission-rule syntax
- **Pitfalls observed**: `skills` as a `plugin.json` field (suggested by CLAUDE.md) is not used in any shipped plugin.json; this would break `test_manifests.py` if run. The `tests/lint/test_skill_structure.py` file references an `allowed-tools` frontmatter field whose value is space-separated — every SKILL.md observed (campaign-audit, brand-identity, dead-code-audit) uses `allowed-tools: Read Write Edit Grep Bash Agent` as a space-separated string, not a list. `argument-hint` uses prose-bracketed placeholders (e.g., `[platform-and-account-id]`). The `ultrathink` value is placed as a standalone body line (not a frontmatter key) in campaign-audit and dead-code-audit, while brand-identity has no ultrathink at all.

## 6. Dependency installation

- **Applicable**: yes (ppc-manager only — it is the one plugin with Python runtime deps; the other 9 are skills-only content plugins)
- **Dep manifest format**: `requirements.txt` + `requirements-dev.txt` at ppc-manager plugin root. No `pyproject.toml`, no `setup.cfg`
- **Install location**: `${CLAUDE_PLUGIN_DATA}/venv/` (isolated per-plugin venv, outside the plugin source tree)
- **Install script location**: `plugins/ppc-manager/hooks/scripts/ensure-venv.sh` (POSIX) and `ensure-venv.ps1` (Windows sibling), wired via `SessionStart` in `hooks/hooks.json` with `timeout: 180`
- **Change detection**: `diff -q requirements.txt requirements.stamp` on POSIX (re-installs only when byte-diff); `Get-FileHash` SHA comparison on Windows. The stamp file is a verbatim copy of `requirements.txt`, written after a successful install
- **Retry-next-session invariant**: **no `rm` on failure** — on pip failure the script emits `{"systemMessage": "pip install failed. See .../install.log"}` and `exit 0` without removing the stamp. Because the stamp is only written *after* a successful install (`cp "$REQ" "$STAMP"` after `pip install` returns 0), a failure leaves the previous stamp (or no stamp) untouched — so the next session will re-attempt on the diff. The invariant is preserved structurally, not by explicit cleanup
- **Failure signaling**: JSON `systemMessage` on stdout + `exit 0` (non-blocking); pip's stderr is redirected to `${CLAUDE_PLUGIN_DATA}/install.log` for postmortem. `set -e` is set at top of shell script. Design is explicitly "never block" per the header comment
- **Runtime variant**: Python stdlib venv + pip (not `uv`, not `uvx`). Requires Python 3.11+ on `$PATH`; interpreter choice via `command -v python3 || command -v python` (POSIX) or `python || py -3` (Windows); override via `PPC_PYTHON` env var
- **Alternative approaches**: **pointer-file pattern** — `ensure-venv.sh` writes the resolved venv interpreter path to `${CLAUDE_PLUGIN_DATA}/python_path.txt`, then MCP server entries in `.mcp.json` invoke `bash ${CLAUDE_PLUGIN_ROOT}/bin/python_shim.sh <server.py>` and the shim reads the pointer file to `exec "$PY" "$@"`. No PEP 723 inline metadata, no `uvx`. `Makefile` provides a separate `.venv/` for local dev (`make install` → `$(PIP) install -r requirements-dev.txt`) kept distinct from the plugin-runtime venv
- **Version-mismatch handling**: Python version guard — `sys.version_info >= (3, 11)` check runs before venv creation; on fail, emits systemMessage and `exit 0`. No Python minor-version stamping of the venv path (a user upgrading Python across sessions would keep the old venv; there is no `python3.11/` vs `python3.12/` sub-pathing under `CLAUDE_PLUGIN_DATA/venv`)
- **Pitfalls observed**: The stamp-file convergence rule relies on the install step being the only writer; if a user manually edits `$DATA_DIR/requirements.stamp`, `diff -q` can false-negative and skip re-install. Windows PowerShell sibling uses `Get-FileHash` equality (SHA256), which is stricter but also more expensive. On POSIX, `cp "$REQ" "$STAMP"` happens only after `pip install -r` succeeds — so a partial-install (e.g., one package fails) leaves no stamp and triggers a full retry next session (idempotent but can thrash on a broken wheel). `install.log` is append-only with no rotation. The venv lives under `${CLAUDE_PLUGIN_DATA}` (good — survives plugin source updates) but is never pruned when `ppc-manager` is uninstalled.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes (ppc-manager only)
- **`bin/` files**:
    - `bin/python_shim.sh` — POSIX shim, reads `${CLAUDE_PLUGIN_DATA}/python_path.txt`, execs the pointed-to Python interpreter with forwarded args
    - `bin/python_shim.ps1` — PowerShell sibling, same behaviour on Windows via `& $py @args`
- **Shebang convention**: `#!/usr/bin/env bash` on `.sh`; PowerShell files have no shebang (invoked by host directly). The `.mcp.json` command prefix is `bash ${CLAUDE_PLUGIN_ROOT}/bin/python_shim.sh` — so shebang is effectively ignored, the file is sourced as an argument to `bash`
- **Runtime resolution**: **pointer file written by hook** — `ensure-venv.sh` writes `$DATA_DIR/python_path.txt` containing the absolute interpreter path. `bin/python_shim.sh` reads that file, validates `-x` or `-f` on the path, then `exec "$PY" "$@"`. Fallback: `CLAUDE_PLUGIN_DATA` defaults to `$HOME/.claude/plugins/data/ppc-manager` (POSIX) or `$USERPROFILE\.claude\plugins\data\ppc-manager` (Windows) if unset.
- **Venv handling (Python)**: pointer file read + exec. No `source activate`, no `uv run --script`, no direct `exec venv python` (the direct-exec target is reached via the pointer file which points at `$VENV/bin/python` or `$VENV/Scripts/python.exe`)
- **Platform support**: bash `.sh` + PowerShell `.ps1` pair. Both shim and venv-bootstrap hook ship both variants side-by-side. `.mcp.json` only references the `.sh` variant — on Windows users without Git Bash, MCP invocation would fail (the `.ps1` shim is not wired through any current manifest). This is a documented-but-unpatched gap
- **Permissions**: unknown from the API surface observed (GitHub tree API doesn't expose mode in this query); shebang present on `.sh` suggests intended 100755. Invoked via `bash <path>` from `.mcp.json` regardless, so execute bit is not strictly required
- **SessionStart relationship**: hook writes pointer file consumed by bin/. `ensure-venv.sh` (SessionStart, 180s timeout) creates/updates the venv and writes `python_path.txt`; `check-credentials.sh` (SessionStart, 15s) consumes `python_path.txt` to run `token_validator.py --quiet --json`; `bin/python_shim.sh` consumes `python_path.txt` to exec the MCP server
- **Pitfalls observed**: If `ensure-venv.sh` has never successfully run (e.g., Python 3.11 unavailable on first session), `python_path.txt` does not exist, and `python_shim.sh` exits 127 with `"python_path.txt not found; did ensure-venv run?"`. MCP server will then appear crashed. Recovery requires installing Python, restarting Claude Code (no automatic retry). The `.ps1` shim is referenced nowhere in `.mcp.json` — Windows users must invoke through WSL/Git Bash for the bundled MCP servers to work (Windows support is aspirational in the shim, but not plumbed end-to-end). No OS-detecting fallback in the MCP command (e.g., via `${CLAUDE_PLUGIN_OS}` or equivalent).

## 8. User configuration

- **`userConfig` present**: no in the shipped `plugin.json` files. Yes intended by design — `.mcp.json` references eight `${user_config.*}` placeholders (e.g., `${user_config.ppc_vault_passphrase}`, `${user_config.google_ads_developer_token}`, `${user_config.meta_app_id}`, `${user_config.meta_app_secret}`) and `tests/lint/test_manifests.py` asserts `userConfig` must include `ppc_vault_passphrase`, `google_ads_developer_token`, `meta_app_secret`, `meta_app_id`, `google_ads_login_customer_id` with `sensitive: true` on the first three. README also says "On first enable, Claude Code prompts you for the 8 `userConfig` fields"
- **Field count**: 0 in the actual `plugin.json` (all 10 plugin.json files carry only name/version/description/author). The intended count (per README + tests) is 8 on ppc-manager
- **`sensitive: true` usage**: not applicable in live state; intended correct per tests (`ppc_vault_passphrase`, `google_ads_developer_token`, `meta_app_secret` all flagged)
- **Schema richness**: not applicable (field doesn't exist in the shipped manifests)
- **Reference in config substitution**: `${user_config.KEY}` form observed in `.mcp.json` env values (4 servers × 4 identical env blocks); `CLAUDE_PLUGIN_OPTION_<KEY>` form observed alongside (e.g., `CLAUDE_PLUGIN_OPTION_GOOGLE_ADS_DEVELOPER_TOKEN`). The hook script `check-credentials.sh` reads `CLAUDE_PLUGIN_OPTION_PPC_VAULT_PASSPHRASE` directly from environment — so substitution in `.mcp.json` feeds the MCP process env, and `CLAUDE_PLUGIN_OPTION_*` is the runtime env-var projection of user_config
- **Pitfalls observed**: The credential architecture is coherent in tests and docs but the actual `plugin.json` is missing the entire `userConfig` block. Installing the plugin today would leave every `${user_config.*}` unresolved and every MCP server would start with an empty passphrase, causing `check-credentials.sh` to emit "vault passphrase not set". This is the single biggest observed defect in the repo — the pattern (env-var + sensitive + pointer-file) is well-designed and documented, but the materialization is incomplete.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 2 total across the marketplace
    - `npm-package-audit` — `matcher: "Bash"`, purpose: check `npm` + `node` are on PATH (one-shot per session via `/tmp/.npm-package-audit-check-done` flag)
    - `skill-creator` — `matcher: "Write"`, purpose: block SKILL.md writes missing `$ARGUMENTS` (hard-block via exit 2)
- **PostToolUse hooks**: 2 in `skill-creator` only — `matcher: "Write|Edit"`, runs `post-edit-skill.sh` and `post-edit-script.sh` (content not fetched but named for validation of skill edits)
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: JSON on stdout (`{"systemMessage": "..."}`) for non-blocking advice; stderr only + `exit 2` for hard blocks (skill-creator's pre-write hook prints error to stderr and returns 2)
- **Failure posture**: mixed. Most hooks are fail-open (`exit 0` after emitting systemMessage). skill-creator's pre-write hook is fail-closed (`exit 2`) and additionally fail-open on environmental gap (`jq` not installed → `exit 0`, graceful degradation). ppc-manager hooks are designed to never block
- **Top-level try/catch wrapping**: absent (pure bash); `set -euo pipefail` used selectively (`pre-write-skill.sh` only; ensure-venv uses `set -e`; most hooks run without strict mode)
- **Pitfalls observed**: `skill-creator/hooks/scripts/pre-write-skill.sh` has header comment "AI Cookbook — PreToolUse hook" (not Anthril — suggests copy-paste from another repo). `npm-package-audit/hooks/scripts/check-npm.sh` uses `/tmp/.npm-package-audit-check-done` as a flag file — on multi-user systems this collides across users. The flag is never cleared, so first-session-of-the-day succeeds but a user who installs npm mid-session will not be re-checked.

## 10. Session context loading

- **SessionStart used for context**: yes, but only for welcome banners + dep install
    - `data-analysis`, `business-economics`, `knowledge-engineering`, `plan-completion-audit`, `skill-creator` use `welcome.sh` which emits `systemMessage` JSON with skill count + line-count warnings (a lint-in-banner convention)
    - `ppc-manager` uses SessionStart exclusively for `ensure-venv.sh` + `check-credentials.sh` (no welcome banner)
- **UserPromptSubmit for context**: no (not observed in any `hooks.json`)
- **`hookSpecificOutput.additionalContext` observed**: no — all context injection uses the simpler `{"systemMessage": "..."}` JSON shape on stdout
- **SessionStart matcher**: none — no `matcher` key in any SessionStart block; fires on all sub-events (startup, clear, compact)
- **Pitfalls observed**: `welcome.sh` runs on every `clear`/`compact` (no matcher restriction), re-emitting the skill-count banner mid-session. `suggest-related.sh` greps `TRANSCRIPT` (the path) not the transcript contents — the data-analysis variant does `echo "$TRANSCRIPT" | grep` which pipes the path string itself, so any skill name in the transcript filename matches by coincidence, or never matches otherwise. ppc-manager's `suggest-next-skill.sh` is smarter — it `tail -200 "$TRANSCRIPT" | grep` the file's actual tail content. This is an observed inconsistency in hook quality across the 10 plugins.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none (feature not used)
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none — the notification surface this marketplace uses is `systemMessage` from `SessionStart` and `Stop` hooks only.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none — every plugin stands alone
- **`{plugin-name}--v{version}` tag format observed**: no; only a single repo-wide `v1.0.0` tag
- **Pitfalls observed**: the 23 ppc-manager skills form a directed chain (encoded in `suggest-next-skill.sh`), but this is an intra-plugin skill chain, not a plugin-to-plugin dependency.

## 13. Testing and CI

- **Test framework**: pytest (ppc-manager only — 17 test modules under `plugins/ppc-manager/tests/{unit,integration,lint}/`). No tests in any of the other 9 plugins
- **Tests location**: nested inside the plugin — `plugins/ppc-manager/tests/`. Not at repo root
- **Pytest config location**: none observed (no `pyproject.toml`, no `pytest.ini`, no `setup.cfg`). `conftest.py` at `plugins/ppc-manager/tests/conftest.py` handles sys.path shimming instead (inserts `scripts/` onto `sys.path`). The `Makefile` and `conftest.py` together are the config
- **Python dep manifest for tests**: `plugins/ppc-manager/requirements-dev.txt` (separate from `requirements.txt`)
- **CI present**: yes (2 workflows in `.github/workflows/`)
- **CI file(s)**: `validate-marketplace.yml`, `sponsors.yml`
- **CI triggers**:
    - `validate-marketplace.yml` — `push: [main]`, `pull_request: [main]`, `workflow_dispatch`
    - `sponsors.yml` — `workflow_dispatch`, `schedule: "0 6 * * *"` (daily)
- **CI does**:
    - `validate-marketplace.yml` — JSON validation of `marketplace.json` and every `plugins/*/.claude-plugin/plugin.json` via `node -e "JSON.parse(...)"`, then runs `node scripts/check-versions.mjs` for version sync
    - `sponsors.yml` — `JamesIves/github-sponsors-readme-action@v1` to sync `SPONSORS.md` and `README.md` sponsor tiers (five tiers by minimum pledge cents)
- **Matrix**: none (single Node 20 on ubuntu-latest)
- **Action pinning**: tag (`actions/checkout@v4`, `actions/setup-node@v4`, `JamesIves/github-sponsors-readme-action@v1`, `JamesIves/github-pages-deploy-action@v4`) — not SHA-pinned
- **Caching**: none (no `actions/cache`, no `setup-node` cache directive)
- **Test runner invocation**: **not invoked from CI** — `validate-marketplace.yml` runs only JSON and version-sync validation, never pytest. pytest is invoked via `make test` / `make test-live` / `make coverage` locally only. So ppc-manager has a test suite but no CI job runs it
- **Pitfalls observed**: Big gap — the well-developed pytest suite (unit/integration/lint + fixtures) has no CI job. `test_manifests.py` asserts `userConfig` structure in plugin.json that the shipping `plugin.json` doesn't have — running these tests locally today would fail. The `sponsors.yml` workflow pushes to branch `master` via `github-pages-deploy-action` but the default branch is `main`; this workflow would fail on first run (the deploy-action receives `folder: "."` and `branch: "master"` while no `master` ref exists).

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable — releases are not automated. The single `v1.0.0` tag was cut manually and no GitHub Release artifact was published (`releases: []` via API)
- **Tag-sanity gates**: none
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable (CHANGELOG.md exists at both root and in ppc-manager, Keep-a-Changelog format, but is not consumed by any workflow)
- **Pitfalls observed**: No tooling enforces that plugin.json version bumps get tagged, which is how ppc-manager 1.0.1, data-analysis 1.0.1, database-design 1.1.0 all ended up live without any tag pointing at them. Users pinning `@v1.0.0` (the only tag) receive older state.

## 15. Marketplace validation

- **Validation workflow present**: yes — `validate-marketplace.yml`
- **Validator**: node custom (`node -e "JSON.parse(...)"` for syntax + `scripts/check-versions.mjs` for version sync). Not `claude plugin validate`, no pre-commit hook, no zod schema
- **Trigger**: `push` (main) + `pull_request` (main) + `workflow_dispatch`
- **Frontmatter validation**: no (there is a pytest lint module `tests/lint/test_skill_structure.py` but it is not run by CI)
- **Hooks.json validation**: no (JSON-parse validation only targets `marketplace.json` and each `plugin.json`; `hooks.json` files are not parsed by CI)
- **Pitfalls observed**: `check-versions.mjs` uses `metadata.pluginRoot` with default `.` — when the marketplace uses `./plugins/<name>` as source, the script treats the leading `./` as part of the path segment and `join(repoRoot, '.', './plugins/<name>')` still resolves. But on Windows CI path-separator semantics could differ; the workflow runs on `ubuntu-latest` so this is fine in practice.

## 16. Documentation

- **`README.md` at repo root**: present, ~15KB — describes marketplace, installation, lists every skill per plugin with one-line description in tables, includes directory-layout tree, quality checklist, contributing section
- **`README.md` per plugin**: mixed — `brand-manager`, `database-design`, `ppc-manager`, `software-development` have plugin-level READMEs; `business-economics`, `data-analysis`, `knowledge-engineering`, `npm-package-audit`, `plan-completion-audit`, `skill-creator` do not
- **`CHANGELOG.md`**: present at repo root (Keep-a-Changelog, covers only `1.0.0` dated 2025-05-20, out of date vs live `1.0.1`/`1.1.0` plugin versions); also present at `plugins/ppc-manager/CHANGELOG.md` (same format, covers only `1.0.0` dated 2026-04-11)
- **`architecture.md`**: present at `plugins/ppc-manager/docs/architecture.md` only — 12KB, comprehensive directory layout, data-flow, MCP server tool surface, auth library design, hook system, test strategy, dependency graph, extension guide. No repo-root architecture.md
- **`CLAUDE.md`**: present at `.claude/CLAUDE.md` (repo root) — development standards (Australian English mandate, skill structure, SKILL.md frontmatter schema, plugin manifest template, marketplace registration template, hooks conventions, version management, quality checklist). No per-plugin CLAUDE.md
- **Community health files**: `SPONSORS.md` at root (auto-maintained by `sponsors.yml`); no `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE/`, no `.github/PULL_REQUEST_TEMPLATE.md`
- **LICENSE**: present at repo root (MIT, SPDX `MIT`); ppc-manager ships its own `LICENSE` and every skill ships `LICENSE.txt` (Apache 2.0 per README text)
- **Badges / status indicators**: none observed in README (no workflow badge, no version badge, no license badge)
- **Pitfalls observed**: README structure is well-layered (repo README → plugin README → skill SKILL.md) for the plugins that have plugin READMEs — but 6 of 10 plugins have no plugin-level README, breaking the "Nesting Discipline" pattern. `architecture.md` exists for ppc-manager only; the other structurally substantial plugins (brand-manager with 9 skills, database-design) have no architecture document. CLAUDE.md templates explicit plugin.json shape that the actual plugin.json files don't follow.

## 17. Novel axes

- **Pointer-file runtime indirection between SessionStart and MCP** — `ensure-venv.sh` writes `${CLAUDE_PLUGIN_DATA}/python_path.txt`; `bin/python_shim.sh` reads it; `.mcp.json` invokes the shim. This decouples MCP server registration from OS-specific paths, defers interpreter resolution to runtime, and lets the venv live in `CLAUDE_PLUGIN_DATA` without `.mcp.json` needing to encode Windows `Scripts\python.exe` vs POSIX `bin/python`. Worth extracting as a distinct pattern axis from generic "bin-wrapped CLI" — the *mechanism* is a shared-state file written by one hook and read by another process.
- **Stamp-file based change detection with structural retry invariant** — `requirements.stamp` is a verbatim copy of `requirements.txt`, written only after successful install. On retry, `diff -q` naturally converges: success writes stamp; failure leaves stamp stale (or absent). No explicit `rm` on failure; the invariant is preserved because the stamp is a write-after-success artefact rather than a write-on-attempt artefact.
- **Cross-tool env-var projection of user_config** — `.mcp.json` uses both `${user_config.KEY}` (for MCP-server consumption) and `CLAUDE_PLUGIN_OPTION_KEY` (for hook-script consumption via plain `$CLAUDE_PLUGIN_OPTION_KEY`). The same user_config field is materialised twice per server entry under different names, which the hook script then reads directly from process env. An unusual double-binding compared to the more common single-projection pattern.
- **Australian English mandate in content + CI check intent** — `.claude/CLAUDE.md` and per-plugin tests prescribe "Australian English in all narrative text (colour, optimise, behaviour, organisation)" and ship `tests/lint/test_australian_english.py` (not inspected here). Locale-constrained content style enforced as a lint gate is unusual.
- **Sponsor-tier automation as first-class workflow** — `sponsors.yml` has six JamesIves/github-sponsors-readme-action steps, one per tier (Founding/Partners/Backers/Builders/Supporters/Featured), each with pledge-range gating. Novel enough to note as a community-health surface.
- **Per-skill LICENSE mixing** — plugin-level code is MIT, per-skill content is Apache 2.0 under `skills/<name>/LICENSE.txt`. Granular license delineation inside a plugin is unusual; most marketplaces use a single repo-level license.
- **Skill sub-agent pairing via frontmatter `context: fork` + `agent: <name>`** — `campaign-audit/SKILL.md` declares `context: fork` + `agent: campaign-auditor` to drop execution into an isolated sub-agent context, with `agents/campaign-auditor.md` sitting alongside `skills/`. This is a skill-to-agent dispatch pattern not seen in most marketplaces.
- **Vault-file on disk with passphrase-in-keychain + encrypted-at-rest pattern** — documented in `plugins/ppc-manager/docs/architecture.md`: Fernet + PBKDF2-HMAC-SHA256 (100000 iterations), written under file-lock, cached in-memory per-MCP-server-process. Worth a novel axis on credential handling.
- **"Suggest next skill" chaining hook** — `ppc-manager/hooks/scripts/suggest-next-skill.sh` tails the last 200 lines of `$CLAUDE_TRANSCRIPT`, matches the most recent skill invocation, and emits a `systemMessage` recommending the next skill in the DAG. Implements a user-journey through an intra-plugin skill graph via a `Stop` hook.
- **Makefile alongside pytest + dual venv (dev vs runtime)** — the plugin maintains a local-development venv at `.venv/` via Makefile for running tests, separate from the runtime venv at `${CLAUDE_PLUGIN_DATA}/venv/` that the user's Claude Code session provisions. Two distinct venvs per plugin, one for authors one for users.

## 18. Gaps

- `scripts/lib/ppc_auth.py`, `scripts/lib/vault.py`, and the four `mcp_servers/*/server.py` files were not fetched — architecture.md and tests describe the interfaces, but the exact class shapes (e.g., `PPCAuth.from_env()` signature, `PPCVault` public methods, the refresh-on-read semantics) are inferred from docs. Resolving: fetch `plugins/ppc-manager/scripts/lib/ppc_auth.py` and `plugins/ppc-manager/scripts/lib/vault.py`.
- File modes on `bin/python_shim.sh` and hook scripts were not retrieved — GitHub REST `contents` API does not expose Unix mode bits by default. The tree fetch uses recursive mode which does include `mode` under each `tree[].mode`, but the surfaced listing did not show it. Resolving: re-fetch the tree with mode-carrying entries or use `gh api` on `/git/trees/<sha>` and inspect `mode` per entry (100644 vs 100755 vs 120000).
- Live status of `validate-marketplace.yml` against current `main` was not checked — given that `check-versions.mjs` fails when marketplace entries are missing `version` (they are), CI against `main` should currently be red. Resolving: `gh run list --workflow=validate-marketplace.yml --limit 5` to confirm red/green state and whether the workflow is genuinely active or has been disabled.
- The eight `userConfig` fields referenced by `.mcp.json` and asserted by `tests/lint/test_manifests.py` were not listed exhaustively — five are named in the test (`ppc_vault_passphrase`, `google_ads_developer_token`, `meta_app_secret`, `meta_app_id`, `google_ads_login_customer_id`). The remaining three are implied but not enumerated in inspected files. Resolving: inspect `skills/oauth-setup/SKILL.md` which likely enumerates all fields as part of the setup walkthrough.
- The `allowed-tools` frontmatter field was observed with space-separated values (`Read Write Edit Grep Bash Agent`), which is unusual — most Claude Code plugin conventions use YAML list syntax. Whether Claude Code accepts space-separated strings as a list of tools for validation purposes was not verified against the plugins-reference docs. Resolving: compare against `docs-plugins-reference.md` frontmatter schema in the research context resources.
- `.github/workflows/` was inspected for workflow files but `.github/` was not inspected for `FUNDING.yml`, `dependabot.yml`, `CODEOWNERS`, or issue/PR templates. Resolving: list `.github/` contents directly via the API.
- The `post-edit-skill.sh` and `post-edit-script.sh` contents (skill-creator PostToolUse hooks) were named but not fetched. Resolving: one more fetch each to complete section 9 posture details.
- `tests/lint/test_australian_english.py` was named in the directory listing but not fetched — the mechanism (word-list grep, regex, or AST?) is inferred, not observed. Resolving: fetch the file to document the validation form.
