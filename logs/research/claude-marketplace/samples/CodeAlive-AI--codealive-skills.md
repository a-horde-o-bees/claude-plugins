# CodeAlive-AI/codealive-skills

## Identification

- **URL**: https://github.com/CodeAlive-AI/codealive-skills
- **Stars**: 10
- **Last commit date**: 2026-04-18 (commit `c9229b4c` — "Fix 2.0.4 description and add CLAUDE.md clarifying the skill is not MCP")
- **Default branch**: `main`
- **License**: MIT
- **Sample origin**: primary (community)
- **One-line purpose**: Agent skill + Claude Code plugin providing semantic code search and AI-powered codebase Q&A across indexed repositories via the CodeAlive REST API.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root.
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper — `metadata.description = "CodeAlive integrations for AI coding agents"`, `metadata.version = "1.0.0"`. No `pluginRoot`.
- **`metadata.pluginRoot`**: absent (plugin lives at repo root, `source: "./"`).
- **Per-plugin discoverability**: none on the marketplace entry; `plugin.json` carries `keywords: ["code-search", "codebase", "semantic-search", "code-intelligence"]`. No `category` or `tags` fields. Repo-level GitHub topics are present (`agent-skills`, `ai-coding`, `codealive`, `semantic-search`, `skill-md`, `skills`) but those are not marketplace discoverability surfaces.
- **`$schema`**: absent on both marketplace.json and plugin.json.
- **Reserved-name collision**: no.
- **Pitfalls observed**: marketplace-level `metadata.version: "1.0.0"` is decoupled from plugin.json `version: "2.0.5"` and does not track — it has been left at 1.0.0 across every release cut. The marketplace doesn't appear to enforce a relationship, but a reader comparing the two will see a drift that is almost certainly unintentional (marketplace-level version is rarely surfaced to users).

## 2. Plugin source binding

- **Source format(s) observed**: relative — `"source": "./"` (plugin is the repo).
- **`strict` field**: `strict: false` explicit on the single plugin entry. With `pluginRoot` absent and `source: "./"`, `strict: false` is semantically unnecessary for normal discovery — strict only matters when carving components out of a source tree that has non-standard layout. Likely reflects copy-paste / defensive hedging rather than a specific carve.
- **`skills` override on marketplace entry**: absent. No per-component carve is performed — `strict: false` is set without an accompanying override array.
- **Version authority**: `plugin.json` only (`2.0.5`). The marketplace entry has no `version`. Git tags (`v2.0.5` etc.) match plugin.json one-to-one — CLAUDE.md documents "bump plugin.json, then annotate a tag matching vX.Y.Z" as the release step.
- **Pitfalls observed**: `strict: false` without a corresponding override looks like unused ceremony — it is either (a) a hedge against future component additions outside the default discovery roots, or (b) an artifact from before skills/agents/hooks were moved under canonical paths. Either way a reader cannot tell from the manifest what `strict: false` protects.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via `@ref` if they want a specific version, otherwise `/plugin install codealive@codealive-marketplace` resolves to the head of `main`. There is a single long-lived branch (`main`) plus one feature branch (`COD-XXX-search-surface-split`).
- **Channel-pinning artifacts**: absent. No `stable-*`/`latest-*` marketplaces, no dev-counter split, no release-branch family.
- **Pitfalls observed**: mixing "Claude Code plugin" and "universal skill via npx skills" distribution modes — the skill can also be installed via `npx skills add CodeAlive-AI/codealive-skills@codealive-context-engine`, a separate distribution channel outside Claude Code's marketplace. This is a channel in the skills.sh sense, not in the Claude marketplace sense, but reading the README a user could conflate them.

## 4. Version control and release cadence

- **Default branch name**: `main`.
- **Tag placement**: on `main` — tags `v1.0.0 … v2.0.5` all point at commits that are ancestors of `main`. No release branches.
- **Release branching**: none (tag-on-main).
- **Pre-release suffixes**: none observed — all ten tags are plain `vX.Y.Z`.
- **Dev-counter scheme**: absent.
- **Pre-commit version bump**: no. Version bump is manual per CLAUDE.md step 2 ("Bump `.claude-plugin/plugin.json` version").
- **Pitfalls observed**: ten git tags (`v1.0.0`, `v1.1.0`, `v1.2.0`, `v1.2.1`, `v1.3.0`, `v2.0.0`, `v2.0.1`, `v2.0.3`, `v2.0.4`, `v2.0.5`) but only seven GitHub Releases (stops at `v2.0.1`) — `v2.0.3`/`v2.0.4`/`v2.0.5` are tags without published Releases, and `v2.0.2` is a skipped number with no tag and no release. Release-notes UX is a manual step that has fallen behind the tag cadence. Observed pattern, not inferred — API lists ten tags and seven releases.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery only — plugin.json is minimal manifest metadata (name, description, version, author, homepage, repository, license, keywords). No `skills`, `agents`, `hooks`, `mcpServers`, `commands` fields. Claude Code picks up components via convention directories (`skills/`, `agents/`, `hooks/hooks.json`).
- **Components observed**: skills yes (`skills/codealive-context-engine/`), commands no, agents yes (`agents/codealive-context-explorer.md`), hooks yes (`hooks/hooks.json` + `hooks/scripts/check_auth.sh`), `.mcp.json` no, `.lsp.json` no, monitors no, bin no, output-styles no.
- **Agent frontmatter fields used**: `name`, `description`, `tools`, `model`, `skills`. On `codealive-context-explorer`: `tools: Bash, Read, Grep, Glob`; `model: haiku`; `skills: [codealive-context-engine]`.
- **Agent tools syntax**: plain tool names (`Bash, Read, Grep, Glob`) — no permission-rule syntax like `Bash(uv run *)`.
- **Pitfalls observed**: SKILL.md and the subagent both describe the five Python scripts in prose + fenced code blocks. The subagent references scripts with a bare `python scripts/datasources.py` path and notes "If the path fails, check `${CLAUDE_PLUGIN_ROOT}/skills/codealive-context-engine/scripts/`" — a soft fallback rather than a deterministic resolution, which makes the agent responsible for retrying with the right CWD.

## 6. Dependency installation

- **Applicable**: yes for the runtime skill (one-time interactive `setup.py`), no for a sessionized dep-install hook. The skill's Python scripts use only the stdlib (`urllib.request`, `subprocess`, `json`, `platform`) — no third-party runtime deps.
- **Dep manifest format**: none. No `requirements.txt`, `pyproject.toml`, `setup.py`-as-packaging (`setup.py` at the skill root is a standalone interactive configurator, not a packaging manifest). CI installs `pytest pytest-cov` via `pip` inline.
- **Install location**: n/a (no venv). Setup stores the API key in the OS credential store (macOS Keychain / Linux Secret Service / Windows Credential Manager). No Python packages are installed anywhere.
- **Install script location**: `skills/codealive-context-engine/setup.py` — user-invoked, not hook-invoked. Documented via README: `python setup.py`.
- **Change detection**: n/a.
- **Retry-next-session invariant**: n/a.
- **Failure signaling**: SessionStart hook (`check_auth.sh`) signals missing credential via `hookSpecificOutput.additionalContext` JSON on stdout, nudging the agent to run `python setup.py`. `exit 0` always — fail-open, non-blocking.
- **Runtime variant**: Python stdlib only. No uv, no pip, no npm. The agent/user invokes `python scripts/*.py` directly using whatever `python` is on PATH.
- **Alternative approaches**: N/A — the "no deps" posture is itself the alternative. Nothing to install.
- **Version-mismatch handling**: none. No Python minimum-version pin in any manifest; CI uses Python 3.11 but there is no floor declaration.
- **Pitfalls observed**: `setup.py` at `skills/codealive-context-engine/setup.py` shares a name with the Python packaging sentinel `setup.py`. It is not a distutils/setuptools script — it is a CLI tool. A Python tooling agent could mistake it for a package install entry point and run `python setup.py install`. The file itself opens with `"""CodeAlive Context Engine — Setup\n\nStores the API key…"""` so context disambiguates on read, but the naming collision is real.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no. No `bin/` directory. The plugin ships Python scripts the agent invokes directly (`python scripts/search.py`) and a `hooks/scripts/check_auth.sh` hook; neither is a "bin" in the `${CLAUDE_PLUGIN_ROOT}/bin/` sense.
- **`bin/` files**: none.
- **Shebang convention**: n/a for bin. For context: the auth hook uses `#!/bin/bash`; Python scripts use `#!/usr/bin/env python3`; plugin-bridge shell scripts use `#!/usr/bin/env bash`.
- **Runtime resolution**: n/a. `check_auth.sh` resolves plugin root via `${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$0")")")}` — a defensive two-way resolution so the script works whether Claude Code sets the env var or not.
- **Venv handling (Python)**: no venv. Python scripts run under system Python.
- **Platform support**: n/a.
- **Permissions**: `100755` (executable) on all `.sh` files per git tree mode listing. `.gitattributes` forces `eol=lf` for `*.sh` to prevent CRLF-from-Windows breaking shebangs on WSL/Linux.
- **SessionStart relationship**: n/a.
- **Pitfalls observed**: no bin to distribute, but the two-way plugin-root resolution in `check_auth.sh` is a template other hooks can copy — `${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$0")")")}` works when invoked directly for debugging and under Claude Code's harness.

## 8. User configuration

- **`userConfig` present**: no.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable.
- **Pitfalls observed**: the plugin does handle a secret (API key) but chose OS credential store + env var (`CODEALIVE_API_KEY` / `CODEALIVE_BASE_URL`) over `userConfig`. This is a deliberate design choice — credentials stay out of `settings.json` and are shared across all skill-aware agents on the machine (README: "The key is stored once and shared across all agents on the same machine"). A `userConfig` field would have fragmented storage per-agent.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: SessionStart hook emits JSON on stdout (`hookSpecificOutput` envelope). No stderr usage.
- **Failure posture**: fail-open — `exit 0` unconditionally, even when no credential is found. The hook's role is to inject guidance into additionalContext, not to block the session.
- **Top-level try/catch wrapping**: n/a (bash script). Uses `|| true` on each credential lookup to avoid `set -e`-style propagation, but `set -e` is not set, so each failure is swallowed independently.
- **Pitfalls observed**: the hook probes macOS Keychain, Linux Secret Service, and WSL-to-Windows Credential Manager in order and treats any discovery as success. The WSL branch sets `KEY="windows-credential-store"` (a sentinel, not the real value) because it cannot read the actual credential from bash — the real value is read at Python runtime via `powershell.exe` P/Invoke. A hook author copying this pattern must know the sentinel is intentional; it looks like a bug until you trace the runtime path.

## 10. Session context loading

- **SessionStart used for context**: yes — but only conditionally. `check_auth.sh` injects `additionalContext` only when the API key is missing; when present, no context is injected.
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: yes — exactly the Claude Code SessionStart output envelope documented in the plugin-reference hooks page.
- **SessionStart matcher**: `startup` only (not `startup|clear|compact` or empty).
- **Pitfalls observed**: matcher `startup` means `/clear` and `/compact` do not re-trigger the auth check. If the user adds a credential mid-session, the skill won't see the updated state until the next fresh session. Likely intentional — the "missing-key" message is a one-shot nudge, not a status line — but worth noting because other plugins using the same pattern for continuous reminders would need `startup|clear|compact`.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: not applicable.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin marketplace, tags are plain `vX.Y.Z`.
- **Pitfalls observed**: not applicable.

## 13. Testing and CI

- **Test framework**: pytest with pytest-cov.
- **Tests location**: `tests/` at repo root (`tests/helpers.py`, `tests/test_cli_smoke.py`, `tests/test_setup_and_client.py`). Tests cross the skill boundary — they import from `skills/codealive-context-engine/scripts/lib/` via `sys.path.insert` and `importlib.util.spec_from_file_location`.
- **Pytest config location**: none — no `pyproject.toml`, no `pytest.ini`, no `setup.cfg`. CI invokes pytest with inline flags: `python -m pytest tests -v --cov=skills --cov-report=term-missing`.
- **Python dep manifest for tests**: none — CI inline-installs `pytest pytest-cov` via `pip install`.
- **CI present**: yes.
- **CI file(s)**: `.github/workflows/ci.yml`.
- **CI triggers**: `push: branches: [main]`, `pull_request: branches: [main]`.
- **CI does**: installs pytest + pytest-cov, runs `python -m pytest tests -v --cov=skills --cov-report=term-missing`. No linting, no manifest validation, no release automation.
- **Matrix**: none — single job `ubuntu-latest` × Python `3.11`.
- **Action pinning**: SHA — `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2`, `actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0`. Both SHA-pinned with tag comments.
- **Caching**: none — neither the built-in `setup-python` cache input nor an explicit `actions/cache` step. Fresh pip install each run.
- **Test runner invocation**: direct `python -m pytest …` with inline flags. No wrapper script.
- **Pitfalls observed**: no lint, no type-check, no manifest validation in CI — only runtime tests. The dependency-install strategy of "no manifest, CI pins pytest inline" means CI's pytest version floats; a pytest release with a breaking API change could surface as a CI failure with no pinned-version paper trail. Coverage output is `term-missing` only — no codecov or artifact upload, so coverage trend is not tracked across commits.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable (no release workflow). Releases are cut manually: bump `plugin.json` → commit → annotate tag `vX.Y.Z` → push main and tag → write release notes in GitHub UI (sometimes).
- **Automation shape**: not applicable.
- **Tag-sanity gates**: none — no workflow verifies tag on main, no workflow verifies tag matches `plugin.json` version.
- **Release creation mechanism**: manual GitHub UI. For seven of ten tags a Release exists with a one-line title ("v2.0.1 — Sharpen semantic vs grep search guidance"). Three recent tags (`v2.0.3`, `v2.0.4`, `v2.0.5`) have no corresponding Release.
- **Draft releases**: no — all seven existing Releases have `draft: false`, `prerelease: false`.
- **CHANGELOG parsing**: no — repo has no `CHANGELOG.md` file (confirmed 404 on `main`).
- **Pitfalls observed**: the tag-release drift (10 tags, 7 Releases, missing `v2.0.2` number) is a direct symptom of manual release cutting without automation. The release-notes UX is manual and has fallen behind. CLAUDE.md's release steps document the manual process but include no validation — nothing prevents shipping a tag whose `plugin.json` version doesn't match.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: none.
- **Trigger**: not applicable.
- **Frontmatter validation**: no.
- **Hooks.json validation**: no.
- **Pitfalls observed**: the marketplace.json and plugin.json are hand-maintained without schema validation. No pre-commit hook. The minimal CI scope reflects a "runtime is tested, manifests are trusted" posture — relies on plugin-install failures to catch malformed JSON.

## 16. Documentation

- **`README.md` at repo root**: present (~4.4 KB) — installation options (skills.sh, Claude Code plugin, MCP server, plugin-bridge), setup instructions, API key storage table per-OS, usage examples.
- **Owner profile README at `github.com/CodeAlive-AI/CodeAlive-AI`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: n/a (single plugin, skill has `SKILL.md` at `skills/codealive-context-engine/SKILL.md` ~13 KB; `tools/plugin-bridge/README.md` ~3.5 KB for the auxiliary bridge tool).
- **`CHANGELOG.md`**: absent (404 on main).
- **`architecture.md`**: absent.
- **`CLAUDE.md`**: at repo root (~2.4 KB) — positions the skill against MCP ("the skill is NOT an MCP wrapper"), documents release procedure, writing-guidance for the SKILL.md description field.
- **Community health files**: LICENSE present. No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`.
- **LICENSE**: present (MIT, SPDX `MIT`).
- **Badges / status indicators**: absent — no CI badge, no version badge, no license badge on the README.
- **Pitfalls observed**: no CHANGELOG and seven-of-ten tags have GitHub Releases — release-history discoverability is partial. A user who wants to know what changed in `v2.0.5` must `git log v2.0.4..v2.0.5`. Release names duplicate the tag prefix (`v2.0.1 — Sharpen semantic vs grep search guidance`) rather than using `generate_release_notes`.

## 17. Novel axes

- **Multi-agent skills distribution, single source of truth**: the README enumerates ten "SKILL.md-compatible" agents (Claude Code, Cursor, GitHub Copilot, Windsurf, Gemini CLI, Codex, Goose, Amp, Roo Code, OpenCode, OpenClaw) each with their own project-scope and user-scope skills directory conventions. The repo is simultaneously (a) a Claude Code plugin marketplace via `.claude-plugin/marketplace.json`, and (b) a universal skill distributable via `npx skills add CodeAlive-AI/codealive-skills@codealive-context-engine` (skills.sh). CLAUDE.md explicitly frames this: "the description is read by many agents in many contexts" — the skill description has to work for Claude Code, Codex, Cursor, and others simultaneously. Pattern candidate for marketplace-as-cross-host-distribution.
- **Plugin-bridge as cross-agent cache symlinker**: `tools/plugin-bridge/` is an auxiliary bash toolkit (install script + `launchd` plist template + update script + uninstall script + README) that keeps a symlink from `~/.codex/skills/codealive-context-engine` (or any other agent's skills dir, via env-var override) pointed at `~/.claude/plugins/cache/codealive-marketplace/codealive/<latest-version>/skills/codealive-context-engine`. This converts Claude Code's versioned plugin cache into a live source for non-Claude agents, automatically relinking on `claude plugin update` via `launchd` `WatchPaths`. Linux equivalent is a `systemd --user` path unit described inline in the README. No other researched repo ships cross-agent plugin-cache synchronization. Pattern candidate for inter-agent artifact reuse.
- **OS-credential-store preference over `userConfig` for secrets**: deliberately avoids `userConfig.sensitive: true` in favor of macOS Keychain / Linux Secret Service / Windows Credential Manager via a one-time `python setup.py` interactive wizard. The justification (README) is cross-agent sharing: "the key is stored once and shared across all agents on the same machine." Pattern candidate alongside the `userConfig` patterns section — when secrets must be shared across tools, `userConfig` is the wrong surface.
- **WSL-aware credential lookup with sentinel pass-through**: the SessionStart hook (`check_auth.sh`) detects WSL via `grep -qi microsoft /proc/version` and probes Windows Credential Manager through `cmd.exe /c cmdkey /list:codealive-api-key`. Since bash can't read the credential value across the WSL boundary, the hook stores the sentinel string `"windows-credential-store"` to signal "credential exists, defer actual read to Python runtime via `powershell.exe`". Clever but fragile pattern — novel enough to mention.
- **Skill description authored for multi-agent matching**: CLAUDE.md explicitly prescribes description-writing rules ("include concrete trigger verbs/nouns users actually say", "1024 char hard limit, aim 300-500", "don't bake in anti-patterns against failure modes of one session — read by many agents in many contexts"). Pattern candidate for the `description` discoverability axis — SKILL.md-level discovery isn't just a Claude Code concern when the skill targets multiple hosts.
- **Subagent + skill composition**: `agents/codealive-context-explorer.md` invokes the skill via `skills: [codealive-context-engine]` frontmatter and downgrades the model to `haiku` to keep exploration cheap. This is an explicit token-cost optimization — offload iterative searches to a cheaper model so the caller's expensive-model conversation stays short. Pattern candidate for cost-aware subagent design.

## 18. Gaps

- `CHANGELOG.md` is absent — cannot observe whether the project has a prose changelog discipline outside git-tag release notes, or whether changelog-entry authoring was explicitly rejected as a practice. Source to resolve: ask maintainer or check PR history for deleted-CHANGELOG commits.
- No `CODEALIVE_BASE_URL` / `CODEALIVE_API_KEY` behavior is directly observed end-to-end — `setup.py` normalizes and verifies but its integration with the credential store (Keychain write, secret-tool write) happens in branches of the script I only skimmed. I read enough to confirm reads; writes look symmetric but I did not fetch the writer code in detail. Source to resolve: fetch `setup.py` tail (lines ~80-end) and the Linux/Windows write paths.
- Release automation is absent in workflows, and CLAUDE.md's release prescription is manual — I did not verify whether a local script (e.g., a `scripts/release.sh` at the repo root) automates bump + tag. The recursive tree listing showed no such script at root, so I'm confident it's purely manual, but haven't checked deleted/historical files.
- The ten tag names are observed from the `/tags` API; I did not verify that every tag's tree contents match the version in its `plugin.json` (i.e., no drift between tag and manifest). A sampling check would confirm the "tag matches plugin.json" invariant is held across history.
- The `COD-XXX-search-surface-split` feature branch was listed but not inspected — it may contain work-in-progress patterns that would affect future-state observation. Source to resolve: `gh api repos/CodeAlive-AI/codealive-skills/compare/main...COD-XXX-search-surface-split`.
- `plugin.json`'s `keywords` are not a Claude Code marketplace discoverability surface per the plugin-reference docs (which list `category`/`tags`); `keywords` appears to be npm-style convention. Whether Claude's marketplace indexes it is not documented — marked as an observation (keywords field present, role unclear).
- The `strict: false` intent is inferred. Confirming source: ask the maintainer or check commit that introduced it.
