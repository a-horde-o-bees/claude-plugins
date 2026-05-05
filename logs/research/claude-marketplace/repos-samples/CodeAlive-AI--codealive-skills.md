# Sample

Mirrors of `https://github.com/CodeAlive-AI/codealive-skills`. Agent skill + Claude Code plugin providing semantic code search and AI-powered codebase Q&A across indexed repositories via the CodeAlive REST API. MIT-licensed; 10 stars at sample time; current tip is `v2.0.5` (commit `c9229b4c`, 2026-04-18) on the `main` branch.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root with one plugin entry pointing at `"./"` (plugin lives at repo root). No `metadata.pluginRoot`.

### Top-level `metadata` wrapper variants

`metadata.{description, version}` wrapper — `metadata.description: "CodeAlive integrations for AI coding agents"`, `metadata.version: "1.0.0"`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry; plugin root and repo root are the same path.

### `strict` field default

`strict: false` is set explicitly on the single plugin entry. With `pluginRoot` absent and `source: "./"`, `strict: false` is semantically unnecessary for normal discovery — strict only matters when carving components out of a non-standard layout. No `skills` override on the entry. Likely defensive ceremony or copy-paste; cannot be inferred from manifest content alone whether (a) hedge against future component additions or (b) artifact from before skills/agents/hooks were moved under canonical paths.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Marketplace entry carries minimal metadata (`name`, `version`, `source`, `description`); `keywords` lives exclusively in `plugin.json` as `["code-search", "codebase", "semantic-search", "code-intelligence"]`. No `category` or `tags` on the marketplace surface.

### Repo-level GitHub topics

GitHub repo topics declared on the GitHub repo itself: `agent-skills`, `ai-coding`, `codealive`, `semantic-search`, `skill-md`, `skills`. Drives GitHub search but not Claude Code's marketplace UI.

### `$schema` absence on per-plugin manifests

`$schema` absent on both marketplace.json and plugin.json.

## Version coordination

### Single source of truth (`plugin.json` only)

`plugin.json.version` (`2.0.5`) is the user-facing version of record; the marketplace entry has no `version` field. Git tags (`v2.0.5` etc.) match `plugin.json` one-to-one — `CLAUDE.md` documents "bump plugin.json, then annotate a tag matching vX.Y.Z" as the release step. Marketplace-level `metadata.version: "1.0.0"` is decoupled from `plugin.json` and has been left at `1.0.0` across every release cut — drift surface but not a single-source-of-truth violation since the marketplace metadata version is rarely surfaced to users.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split — users pin via `@ref` if they want a specific version, otherwise `/plugin install codealive@codealive-marketplace` resolves to the head of `main`. Single long-lived branch (`main`) plus one feature branch (`COD-XXX-search-surface-split`). No `stable-*`/`latest-*` marketplaces, no dev-counter split, no release-branch family.

### Multi-channel via parallel distribution paths

The skill is also installable via `npx skills add CodeAlive-AI/codealive-skills@codealive-context-engine` (skills.sh) — a separate distribution channel outside Claude Code's marketplace. Two distribution channels for the same artifact, each with its own consumer base.

## Tag and release lifecycle

### Tag-on-main, single branch

Default branch `main`. Ten tags (`v1.0.0` through `v2.0.5`) all point at commits that are ancestors of `main`. No release branches. All tags are plain `vX.Y.Z` (no pre-release suffixes). Version bump is manual per `CLAUDE.md` step 2 ("Bump `.claude-plugin/plugin.json` version").

### Tag-on-main with manual GitHub Release

Tags live on `main`; releases are not triggered by tag push but by manual `gh release create` (or web UI). Ten git tags (`v1.0.0`, `v1.1.0`, `v1.2.0`, `v1.2.1`, `v1.3.0`, `v2.0.0`, `v2.0.1`, `v2.0.3`, `v2.0.4`, `v2.0.5`) but only seven GitHub Releases (stops at `v2.0.1`) — `v2.0.3`/`v2.0.4`/`v2.0.5` are tags without published Releases, and `v2.0.2` is a skipped number with no tag and no release. Release-notes UX is a manual step that has fallen behind the tag cadence — consequence of the manual step being load-bearing.

## Plugin-component registration

### Default convention discovery

`plugin.json` is minimal manifest metadata (name, description, version, author, homepage, repository, license, keywords). No `skills`, `agents`, `hooks`, `mcpServers`, `commands` fields. Claude Code picks up components via convention directories (`skills/`, `agents/`, `hooks/hooks.json`).

## Component composition

### Skills (universal)

One skill: `skills/codealive-context-engine/` with `SKILL.md` (~13 KB).

### Agents

One agent: `agents/codealive-context-explorer.md`.

### Hooks

`hooks/hooks.json` plus `hooks/scripts/check_auth.sh` — a SessionStart-only hook (auth check / setup nudge).

## Skill authoring conventions

### Standard frontmatter

`skills/codealive-context-engine/SKILL.md` carries standard frontmatter. `CLAUDE.md` explicitly prescribes description-writing rules: "include concrete trigger verbs/nouns users actually say", "1024 char hard limit, aim 300-500", "don't bake in anti-patterns against failure modes of one session — read by many agents in many contexts."

### Multi-host description tuning

The skill description is authored to work simultaneously for ten "SKILL.md-compatible" agents enumerated in README (Claude Code, Cursor, GitHub Copilot, Windsurf, Gemini CLI, Codex, Goose, Amp, Roo Code, OpenCode, OpenClaw) — each with its own project-scope and user-scope skills directory conventions. `CLAUDE.md` codifies the multi-host posture: "the description is read by many agents in many contexts."

## Agent declaration conventions

### `skills:` array delegating to skill packages

`agents/codealive-context-explorer.md` declares `tools: Bash, Read, Grep, Glob`, `model: haiku`, and `skills: [codealive-context-engine]` to grant the subagent access to the skill. Cheap-model selection (`haiku`) is an explicit token-cost optimization — offload iterative searches so the caller's expensive-model conversation stays short.

### Plain tool-name list

`tools: Bash, Read, Grep, Glob` (comma-separated bare names). No permission-rule syntax like `Bash(uv run *)`.

## Cross-platform skill publishing

### Multi-runtime install via npm bootstrap

The skill is installable via `npx skills add CodeAlive-AI/codealive-skills@codealive-context-engine` (skills.sh) into runtime-specific directories (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.windsurf`, etc.). Same source ships as a Claude Code marketplace plugin AND as a multi-runtime skill bundle through npm.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory. The plugin ships Python scripts the agent invokes directly (`python scripts/search.py`) and a `hooks/scripts/check_auth.sh` hook. SKILL.md and the subagent reference scripts with `python scripts/datasources.py` and note "If the path fails, check `${CLAUDE_PLUGIN_ROOT}/skills/codealive-context-engine/scripts/`" — a soft fallback rather than a deterministic resolution.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

`hooks/scripts/check_auth.sh` resolves plugin root via `${CLAUDE_PLUGIN_ROOT:-$(dirname "$(dirname "$(dirname "$0")")")}` — a defensive two-way resolution so the script works whether Claude Code sets the env var or not. Pattern reusable as a template for other hooks.

## Dependency installation

### Zero dependencies / stdlib only

The skill's Python scripts use only the stdlib (`urllib.request`, `subprocess`, `json`, `platform`) — no third-party runtime deps. No `requirements.txt`, no `pyproject.toml`, no `setup.py`-as-packaging (the file at the skill root named `setup.py` is a standalone interactive configurator, not a packaging manifest). No venv. The agent/user invokes `python scripts/*.py` directly using whatever `python` is on PATH. CI installs `pytest pytest-cov` via inline `pip install`.

### One-time interactive setup with OS credential store

`skills/codealive-context-engine/setup.py` is a user-invoked interactive configurator. Stores the API key in the OS credential store (macOS Keychain / Linux Secret Service / Windows Credential Manager). No Python packages are installed anywhere. README invokes via `python setup.py`. The shared-name with the Python packaging sentinel `setup.py` is an authoring-collision risk — a Python-tooling agent could mistake it for a distutils/setuptools entry and run `python setup.py install`. The file's docstring (`"""CodeAlive Context Engine — Setup\n\nStores the API key…"""`) disambiguates on read.

## Install change detection

### No change detection

No SessionStart-driven dep install; deps are not managed.

## Install trigger and lifecycle

### User-invoked one-shot installer

`setup.py` at `skills/codealive-context-engine/setup.py` — user-invoked, not hook-invoked. README documents `python setup.py`.

## Install failure posture

### Silent fail-open (`exit 0` always, retry every hook)

`check_auth.sh` (SessionStart) signals missing credential via `hookSpecificOutput.additionalContext` JSON on stdout, nudging the agent to run `python setup.py`. `exit 0` always — fail-open, non-blocking.

## User configuration and authentication

### OS-level secret storage

The plugin handles a secret (API key) but chose OS credential store + env var (`CODEALIVE_API_KEY` / `CODEALIVE_BASE_URL`) over `userConfig`. README: "The key is stored once and shared across all agents on the same machine." A `userConfig` field would have fragmented storage per-agent. macOS Keychain / Linux Secret Service / Windows Credential Manager (via WSL probing for cross-boundary access).

### No userConfig, env-var only

`plugin.json` contains no `userConfig` block. Configuration lives in `CODEALIVE_API_KEY` / `CODEALIVE_BASE_URL` env vars; secrets stay out of `settings.json`.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse hooks, no PostToolUse hooks, no PermissionRequest/PermissionDenied hooks. The single SessionStart hook is observational (auth check / setup nudge), not gating.

## Hook handler runtime

### Bash scripts at conventional path

`hooks/scripts/check_auth.sh` opens with `#!/bin/bash`. Uses `|| true` on each credential lookup to avoid `set -e`-style propagation, but `set -e` is not set, so each failure is swallowed independently. Probes macOS Keychain (`security find-generic-password ...`), Linux Secret Service (`secret-tool lookup ...`), and WSL-to-Windows Credential Manager (`grep -qi microsoft /proc/version` then `cmd.exe /c cmdkey /list:codealive-api-key`) in order.

## Hook output contract

### `additionalContext` for context injection

SessionStart hook emits JSON on stdout via the `hookSpecificOutput` envelope when the API key is missing — exactly the Claude Code SessionStart output envelope documented in the plugin-reference hooks page. No stderr usage.

## Hook failure posture

### Fail-open with always-exit-0

`check_auth.sh` exits 0 unconditionally, even when no credential is found. The hook's role is to inject guidance into additionalContext, not to block the session.

## Session context loading

### Conditional `additionalContext` for setup nudge

`check_auth.sh` injects `additionalContext` only when the API key is missing; when present, no context is injected. The "missing-key" message is a one-shot nudge, not a status line. WSL branch uses a sentinel `KEY="windows-credential-store"` because bash can't read the actual credential value across the WSL boundary — the real value is read at Python runtime via `powershell.exe`. A hook author copying this pattern must know the sentinel is intentional; it looks like a bug until the runtime path is traced.

## SessionStart matcher scope

### Explicit subset

Matcher is `startup` only (not `startup|clear|compact` or empty). `/clear` and `/compact` do not re-trigger the auth check — if the user adds a credential mid-session, the skill won't see the updated state until the next fresh session.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. No monitor count. No version-floor declaration in README.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field on `plugin.json`. Single-plugin marketplace; tag format is plain `vX.Y.Z`.

## Testing

### pytest with optional inline cov

Tests at `tests/` (repo root): `tests/helpers.py`, `tests/test_cli_smoke.py`, `tests/test_setup_and_client.py`. Tests cross the skill boundary — they import from `skills/codealive-context-engine/scripts/lib/` via `sys.path.insert` and `importlib.util.spec_from_file_location`.

### pytest with sys.path manipulation

Tests use `sys.path.insert` and `importlib.util.spec_from_file_location` to import from `skills/codealive-context-engine/scripts/lib/` because the lib isn't a packaged module. No `pyproject.toml`, no `pytest.ini`, no `setup.cfg`.

### Centralized `tests/` placement

Tests placed at `tests/` repo root, not co-located with skill source. CI invokes pytest with inline flags: `python -m pytest tests -v --cov=skills --cov-report=term-missing`. CI inline-installs `pytest pytest-cov` via `pip install`.

## CI workflow shape

### Single workflow, sparse coverage

`.github/workflows/ci.yml` triggers `push: branches: [main]`, `pull_request: branches: [main]`. Single job `ubuntu-latest` × Python `3.11` (no matrix). Installs pytest + pytest-cov, runs `python -m pytest tests -v --cov=skills --cov-report=term-missing`. No linting, no manifest validation, no release automation. Direct `python -m pytest` invocation; no wrapper script. The dependency-install strategy of "no manifest, CI pins pytest inline" means CI's pytest version floats; a pytest release with a breaking API change could surface as a CI failure with no pinned-version paper trail. Coverage output is `term-missing` only — no codecov or artifact upload, so coverage trend is not tracked across commits.

### Action-pinning conventions

SHA pinning with tag comments: `actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd # v6.0.2`, `actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405 # v6.2.0`. No caching — neither the built-in `setup-python` cache input nor an explicit `actions/cache` step.

## Marketplace validation

### No validation

No validation workflow, no validator. Marketplace.json and plugin.json are hand-maintained without schema validation. No pre-commit hook. Frontmatter has no automated validation. "Runtime is tested, manifests are trusted" posture — relies on plugin-install failures to catch malformed JSON.

## Release automation

### No release automation / manual

No `release.yml`. Releases are cut manually: bump `plugin.json` → commit → annotate tag `vX.Y.Z` → push main and tag → write release notes in GitHub UI (sometimes). Tag-release drift (10 tags, 7 Releases, missing `v2.0.2` number) is a direct symptom. CLAUDE.md's release steps document the manual process but include no validation — nothing prevents shipping a tag whose `plugin.json` version doesn't match. Release names duplicate the tag prefix (`v2.0.1 — Sharpen semantic vs grep search guidance`) rather than using `generate_release_notes`.

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

`README.md` at repo root (~4.4 KB) — installation options (skills.sh, Claude Code plugin, MCP server, plugin-bridge), setup instructions, API key storage table per-OS, usage examples. `CLAUDE.md` at repo root (~2.4 KB) — positions the skill against MCP ("the skill is NOT an MCP wrapper"), documents release procedure, writing-guidance for the SKILL.md description field. SKILL.md (`skills/codealive-context-engine/SKILL.md` ~13 KB). `tools/plugin-bridge/README.md` ~3.5 KB for the auxiliary bridge tool. No `architecture.md`. No `CHANGELOG.md` (404 on main).

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` present at repo root (MIT, SPDX `MIT`). SPDX `MIT` declared in `plugin.json` `license` field.

## Community health files

### Bare minimum (LICENSE only)

`LICENSE` present. No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`. No CI badge, version badge, or license badge on README.

## Cross-platform discipline

### POSIX `/bin/sh` discipline in hot path

Auth hook uses `#!/bin/bash`. Python scripts use `#!/usr/bin/env python3`. Plugin-bridge shell scripts use `#!/usr/bin/env bash`. `.gitattributes` forces `eol=lf` for `*.sh` to prevent CRLF-from-Windows breaking shebangs on WSL/Linux. `.sh` files are mode `100755`.

### Dual-fallback OS detection

`check_auth.sh` probes macOS (`security find-generic-password`), then Linux (`secret-tool lookup`), then WSL (`grep -qi microsoft /proc/version` → `cmd.exe /c cmdkey`). Each platform branch is independently failure-tolerant via `|| true`.

## Cross-ecosystem distribution

### Cross-agent skill via `npx skills`

The skill is installable via `npx skills add CodeAlive-AI/codealive-skills@codealive-context-engine` (skills.sh) outside Claude Code's marketplace. Same skill folder doubles as a Claude Code plugin and a skills.sh-distributable. README enumerates ten "SKILL.md-compatible" agent runtimes the skill supports.

## PATH augmentation and host-project setup

### None (plugin operates standalone)

Plugin does not modify host PATH. Auxiliary `tools/plugin-bridge/` ships its own bash toolkit (install script + `launchd` plist template + update script + uninstall script) for cross-agent symlink management — opt-in, not part of plugin install.

## Cross-role tools

### Python (stdlib + pip + uv)

Python is the runtime for skill scripts (`urllib.request`, `subprocess`, `json`, `platform`, all stdlib), for `setup.py` (interactive configurator), and for tests. No `uv`, no third-party runtime deps. CI uses Python 3.11.

### bash

`hooks/scripts/check_auth.sh` (`#!/bin/bash`); plugin-bridge scripts (`#!/usr/bin/env bash`).

### `${CLAUDE_PLUGIN_ROOT}` env var

Used in `hooks/scripts/check_auth.sh`'s defensive plugin-root resolution and referenced in SKILL.md's path-fallback guidance.

### `hookSpecificOutput.additionalContext`

SessionStart auth hook emits via the `hookSpecificOutput.additionalContext` envelope when credential is missing.

