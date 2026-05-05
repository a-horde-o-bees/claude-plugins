# Sample

Mirrors of `https://github.com/SankaiAI/ats-optimized-resume-agent-skill`. Single-skill plugin that transforms a master resume and job description into a tailored, ATS-optimized Word document via a Python renderer using `python-docx` and `lxml`. Default branch `main`; MIT license; 65 stars; last commit 2026-04-11. Sample origin: bin-wrapper.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` co-located with `.claude-plugin/plugin.json` at repo root, advertising one plugin entry whose `source` is `"./"`. Marketplace name `resume-skill-marketplace`; plugin name `resume-skill` — no reserved-name collision. The marketplace exists only to publish this one plugin. `metadata.{description, version}` wrapper carries `description: "Community marketplace for the resume-skill Claude Code plugin"` and `version: "0.1.0"`. `metadata.pluginRoot` absent. `$schema` absent on marketplace.json.

### Redundant metadata sub-object on plugin entries

The marketplace entry duplicates the plugin's `description` field (identical string repeated in `plugin.json`); the two are hand-kept in sync without automation.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry; plugin root and repo root coincide. With `strict` field absent, implicit `strict: true` applies — the plugin manifest at `.claude-plugin/plugin.json` carries the registration burden.

### `source: github` with explicit coords or `ref` pinning

The marketplace entry also records `{"source":"github","repo":"SankaiAI/ats-optimized-resume-agent-skill","ref":"main"}`. `ref: "main"` pins to a moving branch — every install resolves to whatever tip-of-main is at install time; users have no way to hold a release.

### `strict` field default

`strict` field absent on the marketplace entry — implicit `strict: true`. The marketplace entry has no `skills` override; skills location is declared in `plugin.json` only as `"skills": "./skills/"`.

## Per-plugin discoverability metadata

### Marketplace-entry facets plus duplicated keywords on plugin.json

Marketplace entry sets `category: "productivity"` plus `keywords: ["resume","docx","ats","job-search","career"]` (no `tags`). `plugin.json` independently carries the identical `keywords` list — two locations for the same intent with no automation reconciling them.

### `$schema` absence on per-plugin manifests

`$schema` absent from `plugin.json`.

## Version coordination

### Multi-site sprawl (5+ locations)

Three separate `version: "0.1.0"` strings exist in the repo: marketplace-level `metadata.version`, marketplace plugin-entry `version`, and `plugin.json.version`. All hand-maintained, no enforcement. The version has remained at `0.1.0` from first commit (2026-04-08) through latest (2026-04-11); any future bump must be coordinated across all three files.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

`ref: "main"` is the only distribution channel. No tags, no release branches. `gh api .../tags` returns empty.

## Tag and release lifecycle

### No tags at all

`gh api .../tags` returns empty; `gh api .../releases` returns count=0. The repo has no tags and has cut no releases since first commit. Default branch is `main`. No release branches exist — only `main`.

## Plugin-component registration

### Explicit path string for one component

`plugin.json` carries `"skills": "./skills/"` as the only component field. This is a non-default value — default discovery would look for `skills/` implicitly anyway, so the explicit `./skills/` is redundant but valid. No `commands`, `agents`, `hooks`, `.mcp.json`, `.lsp.json`, `monitors`, or `output-styles` fields.

## Component composition

### Skills (universal)

`skills/build-tailored-resume/SKILL.md` plus a duplicate root `SKILL.md`. Both files report 17916 bytes with identical opening frontmatter — content duplicated across two paths. The root copy is consumed by `install.sh`/`install.ps1` for non-plugin install methods; the `skills/` copy serves the plugin install path. Each edit must land in both locations or the two drift.

### bin

Two files — `bin/resume-skill` (POSIX bash, 1055 bytes) and `bin/resume-skill.cmd` (Windows batch, 408 bytes). No agents, commands, hooks, or MCP server.

## Skill authoring conventions

### Standard frontmatter

`SKILL.md` frontmatter carries `name`, `description`, plus the skill body driving the build-tailored-resume workflow.

## Server runtime (MCP)

### No bin entry / direct invocation

Plugin does not ship an MCP server. All execution flows through the bin wrapper which `exec`s the Python CLI under `renderer/src/cli.py`.

## Bin entry mechanism

### Bash + `.cmd` pair for cross-platform

`bin/resume-skill` (POSIX bash, `#!/usr/bin/env bash`) and `bin/resume-skill.cmd` (Windows batch, no shebang) form a cross-platform pair. The bash wrapper resolves the plugin root via `"${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"`. The `.cmd` counterpart resolves via `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..`. The `.cmd` mirrors the bash wrapper's check-and-install logic — `python -c "import docx" 2>nul || pip install ...`, `%PYTHONPATH%` setup, `%*` argument passthrough. PowerShell `.ps1` exists separately as a one-shot installer (`install.ps1`) but is not used as a runtime shim. The `.cmd` cannot replicate `set -e`; a failing pip install in the `.cmd` path is silently ignored, and the subsequent `python cli.py` then fails with a less-useful ImportError.

### First-run pip-install in bin wrapper

The POSIX wrapper probes `python -c "import docx"`; on ImportError it runs `pip install python-docx lxml --quiet` against whatever `python`/`pip` resolve in PATH, then sets `PYTHONPATH="$PLUGIN_ROOT/renderer"` pointing at `src/` and `exec`s `python renderer/src/cli.py`. No venv, no version pin, no lockfile, no sha/md5. Re-runs are idempotent-by-retry because the `import docx` probe short-circuits subsequent invocations. The wrapper hard-codes `python` (not `python3`) and `pip` (not `pip3`), which fails on Linux distros where only `python3` exists. There is no `command -v python` precheck and no "python not found" guidance.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Both bin wrappers prefer `${CLAUDE_PLUGIN_ROOT}` when set and fall back to a script-relative computation. The bash form uses `"${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"`; the `.cmd` form uses `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..`. The fallback makes both wrappers runnable from a bare clone outside the plugin harness.

## Dependency installation

### `pip install` against `sys.executable` (no venv isolation)

Renderer dependencies (`python-docx>=1.1.0`, `lxml>=5.0.0`) are installed via ad-hoc `pip install` into whatever Python environment the user's `pip` points at — system Python, conda env, pyenv shim, etc. No `${CLAUDE_PLUGIN_DATA}` venv, no `${CLAUDE_PLUGIN_ROOT}`-scoped venv. `install.sh`/`install.ps1` runs `pip install "$SCRIPT_DIR/renderer" --quiet`; the `bin/resume-skill` wrapper performs the same check-and-install on every CLI invocation.

### Coexisting redundant install paths

Two parallel install paths exist: (a) `install.sh`/`install.ps1` does a proper `pip install renderer/` and creates a `resume-skill` console script per `pyproject.toml`'s `project.scripts`; (b) `bin/resume-skill` shims directly to the source tree via `PYTHONPATH="$PLUGIN_ROOT/renderer"` pointing at `src/`, bypassing the installed console script. The two paths can disagree.

### Manual venv with documented commands

Renderer dependencies declared twice — `renderer/requirements.txt` (`python-docx>=1.1.0`, `lxml>=5.0.0`) and `renderer/pyproject.toml` `[project.dependencies]` listing the same two. `pyproject.toml` is authoritative (consumed by `pip install renderer/`); `requirements.txt` is duplicative. `pyproject.toml` declares `requires-python = ">=3.10"` as the only Python version constraint.

## Install change detection

### Existence-only check

Change detection is a single Python import probe — `python -c "import docx"`. Success short-circuits install; failure triggers `pip install`. No version compare, no lockfile, no sha/md5.

## Install trigger and lifecycle

### Lazy bootstrap on first hook (no SessionStart)

There is no `hooks.json`, no SessionStart, no UserPromptSubmit. The bin wrapper itself triggers dep install lazily on every CLI invocation — first-run installs deps, subsequent runs short-circuit on the import probe.

## Install failure posture

### Set -e bash with stderr exit-1

The bash wrapper uses `set -e` — any non-zero exit halts the script. `pip install --quiet` suppresses stderr only on success; on failure pip's stderr is user-visible and the script exits non-zero. The Windows `.cmd` has no equivalent of `set -e`; a failed `pip install` is silently ignored.

## User configuration and authentication

### No userConfig, env-var only

`userConfig` not declared. Skill takes all inputs via conversational flow or file paths passed to the CLI; no env vars consumed. No OS credential store, no API keys, no auth surface.

## Session context loading

### No session-context loading

No hooks of any kind. The plugin loads context via SKILL.md frontmatter description matching only.

## Tool-use enforcement

### Skill-description prose as enforcement surrogate

No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks. The plugin uses skill-level workflow enforcement — gates inside SKILL.md — instead of runtime hooks.

## Live monitoring

### `monitors.json` absent

No `monitors.json` and no monitoring surface.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field on `plugin.json`. Single-plugin marketplace, no inter-plugin coordination.

## Testing

### pytest with sys.path manipulation

Tests live at `renderer/tests/` (`test_rendering.py`, 9337 bytes; `test_validation.py`, 4437 bytes), importing pytest directly. Tests manipulate `sys.path` via `sys.path.insert(0, str(ROOT))` to locate `src/`, since the package layout uses `src/` mapped to `resume_skill` via `[tool.setuptools.package-dir]`. No `pytest.ini`, no `[tool.pytest.ini_options]` in `renderer/pyproject.toml`. `pyproject.toml` carries no `[project.optional-dependencies]` for dev/test — pytest is expected to be installed separately by whoever runs the tests. The test docstring instructs `cd resume_skill && python -m pytest tests/ -v` but the directory on disk is `renderer/`, not `resume_skill/` (the package name vs source directory drift); the correct invocation is `cd renderer && python -m pytest tests/ -v`.

## CI workflow shape

### No CI

`.github/` directory does not exist (`gh api .../contents/.github` returns 404). No workflows, no triggers, no matrix. The pyproject/requirements drift, the stale test-docstring path, and the duplicated-SKILL.md inconsistency are caught only by manual review.

## Marketplace validation

### No validation

No validation tooling. The `owner.email: "your-email@example.com"` placeholder in `marketplace.json` was never replaced before publish — any schema-level validator would have caught it.

## Release automation

### No release automation / manual

No `release.yml` or equivalent. `gh api .../releases` count=0. The plugin has never cut a release; users cannot install a stable ref.

## Documentation surface

### Marketing-grade README (40+ KB)

Repo-root `README.md` is 40958 bytes — bilingual (English + Chinese with anchor-linked language sections), Table of Contents, five install methods, update/uninstall instructions, and a leading "⚡ For AI Coding Agents — Read This First" block containing literal clone+install commands segmented by OS (Mac/Linux, Windows) × scope (user, project) × agent (Claude Code, OpenClaw). Designed so an agent WebFetching the README at install time gets an unambiguous recipe at the top.

### Bilingual content

README is explicitly bilingual (English `[English](#english)` + Chinese `| [中文](#chinese)`).

### Agent-targeted install preamble in README

README opens with a blockquote-rendered "⚡ For AI Coding Agents — Read This First" block carrying pre-written shell commands per OS × scope × agent (Mac/Linux, Windows; user, project; Claude Code, OpenClaw). The same install intent is encoded twice — once for agents at the top, once for humans further down in the "Method 0/1/2/3/4" sections.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

MIT license. SPDX identifier `MIT` appears in manifests; `LICENSE` file present at repo root.

## Community health files

### Bare minimum (LICENSE only)

`PRIVACY.md` (1530 bytes) is present alongside `LICENSE`. No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md`. No badges or status indicators in README.

## Cross-platform discipline

### POSIX-only with no Windows story

The bash wrapper hard-codes `python` and `pip` (not `python3`/`pip3`), fragile on Linux distros without a `python` shim. No `command -v python` precheck. The Windows `.cmd` companion exists but cannot replicate `set -euo pipefail` discipline; `|| pip install` after `python -c "import docx" 2>nul` only runs on nonzero exit of the probe — a distro where the probe fails for reasons other than missing `docx` (e.g., python not on PATH) triggers a spurious install attempt with no further error handling.

## Novel and cross-cutting concerns

- **Coexisting redundant install paths.** The plugin install path (`bin/resume-skill` → `PYTHONPATH=renderer/src/`) and the standalone install path (`install.sh` → `pip install renderer/` → console script) reach the same source via different mechanics and can disagree.
- **First-run pip-install pattern without venv or change detection.** `bin/resume-skill` probes `python -c "import docx"` and pip-installs into whatever `python`/`pip` resolve to in PATH on miss. No venv, no pinning, no change detection beyond import existence — the minimum-viable Python-dep-install pattern.
- **Three-way version sync with no enforcement.** `marketplace.json` carries `metadata.version`, `plugins[0].version`, and `plugin.json.version` — all three hand-maintained with no schema validation, CI check, or single-source designation.
- **Bash + `.cmd` pair (no `.ps1` runtime shim).** Windows runtime support is via `bin/resume-skill.cmd` (cmd.exe batch); `install.ps1` exists separately for the one-shot install flow but is not used as a runtime shim.
- **Agent-targeted install preamble in README.** A blockquote-rendered "⚡ For AI Coding Agents — Read This First" section at the top of the README carries pre-written install commands segmented by OS × scope × agent.

## Cross-role tools

### Python (stdlib + pip + uv)

System Python with `python` and `pip` (not `python3`/`pip3`) from PATH. No uv, no uvx. `pyproject.toml` declares `requires-python = ">=3.10"`.

### `${CLAUDE_PLUGIN_ROOT}` env var

Both bin wrappers consult `${CLAUDE_PLUGIN_ROOT}` first and fall back to a script-relative computation; the env var is the primary plugin-root resolution mechanism.
