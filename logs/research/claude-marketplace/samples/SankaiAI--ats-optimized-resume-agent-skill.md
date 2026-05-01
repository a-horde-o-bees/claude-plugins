# SankaiAI/ats-optimized-resume-agent-skill

## Identification

- **URL**: https://github.com/SankaiAI/ats-optimized-resume-agent-skill
- **Stars**: 65 (observed via `gh api` at research time)
- **Last commit date**: 2026-04-11 (`153209b Update skill instruction.`); repo `updated_at` 2026-04-19
- **Default branch**: `main`
- **License**: MIT (SPDX `MIT`, present as `LICENSE` at root)
- **Sample origin**: bin-wrapper
- **One-line purpose**: "Transforms a master resume and job description into a tailored, ATS-optimized Word document (.docx) with human-sounding bullets and deterministic table-based layout." (from `plugin.json` / marketplace entry — the repo's own tagline is more marketing-y; the manifest version is used here since it matches purpose-statement discipline.)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (one plugin entry)
- **Marketplace-level metadata**: `metadata.{description, version}` wrapper — `description: "Community marketplace for the resume-skill Claude Code plugin"`, `version: "0.1.0"`. No `metadata.pluginRoot`.
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: `category: "productivity"` + `keywords: ["resume","docx","ats","job-search","career"]`. No `tags` field. (Single-plugin marketplace — uniform by construction.)
- **`$schema`**: absent
- **Reserved-name collision**: no — plugin name `resume-skill`, marketplace name `resume-skill-marketplace`
- **Pitfalls observed**: `owner.email` in `marketplace.json` is literally `"your-email@example.com"` — placeholder was never filled in before publish. Plugin-level `description` on the marketplace entry duplicates the identical string in `plugin.json`; both are kept in sync manually (see §2 drift risk).

## 2. Plugin source binding

- **Source format(s) observed**: `github` — `{"source":"github","repo":"SankaiAI/ats-optimized-resume-agent-skill","ref":"main"}`
- **`strict` field**: default (absent) — implicit `strict: true`. Since the plugin manifest lives under `.claude-plugin/plugin.json` at the repo root pointed at by the `github` source, strict discovery works without overrides.
- **`skills` override on marketplace entry**: absent. Skills location is declared in `plugin.json` only (`"skills": "./skills/"`).
- **Version authority**: both — `plugin.json.version = "0.1.0"` and marketplace-entry `version = "0.1.0"` must be hand-kept in sync (drift risk). Marketplace-level `metadata.version` is also `0.1.0`, triply redundant.
- **Pitfalls observed**: three separate `version: "0.1.0"` strings (marketplace metadata, plugin entry, plugin.json) with no single source. `ref: "main"` pins the source to a moving branch, so anyone who installs is always on tip-of-main — no way for the user to hold a release.

## 3. Channel distribution

- **Channel mechanism**: no split — `ref: "main"` is the only channel; users cannot pin to a release because no tags or release branches exist.
- **Channel-pinning artifacts**: absent
- **Pitfalls observed**: no `@ref` pin story documented; users get whatever main has.

## 4. Version control and release cadence

- **Default branch name**: `main`
- **Tag placement**: none — `gh api .../tags` returns empty
- **Release branching**: none — only `main` branch exists
- **Pre-release suffixes**: none observed
- **Dev-counter scheme**: absent — version is hand-edited `0.1.0` across three files
- **Pre-commit version bump**: no — no git hooks committed
- **Pitfalls observed**: no release discipline at all. `gh api .../releases` returns `count=0`. The plugin has been at `0.1.0` since first commit (2026-04-08) through latest (2026-04-11). Any future bump has to be coordinated across three files.

## 5. Plugin-component registration

- **Reference style in plugin.json**: explicit string path for skills (`"skills": "./skills/"`), no other component fields. This is a non-default value — default discovery would look for `skills/` implicitly anyway, so the explicit `./skills/` is redundant (but valid).
- **Components observed**: skills=yes, commands=no, agents=no, hooks=no, `.mcp.json`=no, `.lsp.json`=no, monitors=no, bin=yes (`bin/resume-skill`, `bin/resume-skill.cmd`), output-styles=no
- **Agent frontmatter fields used**: not applicable (no agents)
- **Agent tools syntax**: not applicable
- **Pitfalls observed**: `skills/build-tailored-resume/SKILL.md` and root `SKILL.md` have **identical content** (both 17916 bytes, identical opening frontmatter). The root `SKILL.md` is the canonical file copied by `install.sh`/`install.ps1` for non-plugin installs (Methods 1-3). The `skills/` copy is what the plugin path (Method 4) uses. Two maintenance locations for the same text — classic Single-Source-of-Truth violation. Any edit has to land twice or they drift.

## 6. Dependency installation

- **Applicable**: yes — renders DOCX with `python-docx` and `lxml`
- **Dep manifest format**: both — `renderer/requirements.txt` (`python-docx>=1.1.0`, `lxml>=5.0.0`) and `renderer/pyproject.toml` (PEP 621 `[project.dependencies]` listing the same two). `pyproject.toml` is authoritative (it's what `pip install renderer/` consumes); `requirements.txt` is duplicative.
- **Install location**: ad-hoc `pip install` into whatever python environment the user's `pip` points at. No `${CLAUDE_PLUGIN_DATA}`, no `${CLAUDE_PLUGIN_ROOT}`-scoped venv. Installer script runs `pip install "$SCRIPT_DIR/renderer" --quiet` directly.
- **Install script location**: two parallel entry points:
  - `install.sh` / `install.ps1` at repo root — for non-plugin install methods (runs `pip install renderer/`, copies SKILL.md)
  - `bin/resume-skill` / `bin/resume-skill.cmd` — runtime wrappers that check-and-install on every invocation
- **Change detection**: none — `bin/resume-skill` uses `python -c "import docx"` as an existence probe. If import succeeds, skip install; if it fails, `pip install python-docx lxml --quiet`. No version pin checked, no lockfile, no sha/md5.
- **Retry-next-session invariant**: not applicable (no per-session hook; the `import docx || pip install` runs on every CLI invocation, so it's idempotent-by-retry but not hook-driven)
- **Failure signaling**: `set -e` in bash wrapper — any non-zero exit halts. `pip install --quiet` drops stderr only on success; on failure pip stderr is user-visible. No JSON output, no `systemMessage`. Windows `.cmd` has no error handling equivalent — `|| pip install` chains run unconditionally on a failed probe but a failing `pip install` is silently ignored since there's no subsequent check.
- **Runtime variant**: Python pip (not uv, no venv)
- **Alternative approaches**: N/A — does not use PEP 723, pointer-file, `uvx`, or `npx`
- **Version-mismatch handling**: none — no Python version pinning beyond `requires-python = ">=3.10"` in pyproject.toml
- **Pitfalls observed**: `bin/resume-skill` hard-codes `python` (not `python3`) which fails on many Linux distros where only `python3` exists. The install-on-first-run pattern pollutes whatever environment the user's `python`/`pip` resolve to — a system python, a conda env, a pyenv shim — with no isolation. The CLI wrapper runs `cli.py` via `PYTHONPATH="$PLUGIN_ROOT/renderer"` pointing at `src/`, bypassing the installed `resume-skill` console-script entry point that `pyproject.toml` declares. So there are **two independent install paths**: (a) `install.sh` does a proper `pip install renderer/` and creates the `resume-skill` console script; (b) `bin/resume-skill` shims to the source tree directly, ignoring that installed console script. The two paths can disagree.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — the primary observation this sample was selected for
- **`bin/` files**:
  - `bin/resume-skill` (1055 bytes) — POSIX bash wrapper; probes `import docx`, pip-installs on miss, sets `PYTHONPATH`, execs `python renderer/src/cli.py`
  - `bin/resume-skill.cmd` (408 bytes) — Windows CMD wrapper; same logic, `%CLAUDE_PLUGIN_ROOT%` resolution, `%~dp0..` fallback, `%PYTHONPATH%`, `%*` passthrough
- **Shebang convention**: `#!/usr/bin/env bash` on the POSIX file; `.cmd` has no shebang (Windows batch)
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback — bash uses `"${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"`; cmd uses `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..`
- **Venv handling (Python)**: pip-install at first run (no venv — system/active-env `python` is used directly, deps installed globally into that environment)
- **Platform support**: bash + `.cmd` pair (no `.ps1` wrapper for runtime; `.ps1` exists only for the one-shot `install.ps1`, not as a runtime shim)
- **Permissions**: cannot verify octal directly via the GitHub API contents endpoint, but the `#!/usr/bin/env bash` shebang and the README/architecture expectation (`chmod +x install.sh` is prescribed; `bin/resume-skill` is intended to be invoked by PATH resolution) imply 100755. Observed-as-inferred from the shebang and the documented "Claude Code adds bin\ to PATH automatically" comment, not verified against the blob mode byte.
- **SessionStart relationship**: static — there is no hooks.json, no `SessionStart`, no `UserPromptSubmit`. The bin wrapper itself is what triggers dep install, lazily, on CLI invocation.
- **Pitfalls observed**: the POSIX wrapper uses `python` not `python3`, and `pip` not `pip3` — fragile on Linux distros without a `python` shim. The Windows `.cmd` equivalent is likewise shell-dependent: `|| pip install` after `python -c "import docx" 2>nul` only runs on nonzero exit of the probe, so a distro where the probe errors for some reason other than missing docx (e.g., python not on PATH) would trigger a spurious install attempt. No PATH sanity check, no `command -v python`, no "python not found" guidance. The `.cmd` counterpart to `set -e` does not exist; a failed pip install is invisible and the subsequent `python cli.py` then also fails with a less-useful ImportError.

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable
- **Pitfalls observed**: none — skill takes all inputs via conversational flow or file paths passed to the CLI

## 9. Tool-use enforcement

- **PreToolUse hooks**: none — no hooks.json, no `.claude-plugin/hooks/`
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: not applicable
- **Failure posture**: not applicable
- **Top-level try/catch wrapping**: not applicable
- **Pitfalls observed**: none — plugin uses skill-level workflow enforcement (the gates in SKILL.md) instead of runtime hooks

## 10. Session context loading

- **SessionStart used for context**: no — no hooks of any kind
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: not applicable
- **SessionStart matcher**: not applicable
- **Pitfalls observed**: none — single-skill plugin loads context via SKILL.md frontmatter description matching only

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace, no tags at all)
- **Pitfalls observed**: none

## 13. Testing and CI

- **Test framework**: pytest — `renderer/tests/test_rendering.py` (9337 bytes), `renderer/tests/test_validation.py` (4437 bytes); imports `pytest` directly
- **Tests location**: inside the renderer subdirectory — `renderer/tests/` (not at repo root; not per-plugin in a `tests/plugins/<name>/` layout since the plugin has only this one internal library)
- **Pytest config location**: none — no `pytest.ini`, no `[tool.pytest.ini_options]` in `renderer/pyproject.toml`. Tests manipulate `sys.path` manually (`sys.path.insert(0, str(ROOT))`) to locate `src/` since package layout uses `src/` mapped to `resume_skill` via `[tool.setuptools.package-dir]`.
- **Python dep manifest for tests**: pyproject.toml (no `[project.optional-dependencies]` for dev/test — pytest is expected to be installed separately by whoever runs the tests)
- **CI present**: no — `.github/` directory does not exist (`gh api .../contents/.github` returns 404)
- **CI file(s)**: none
- **CI triggers**: not applicable
- **CI does**: not applicable
- **Matrix**: not applicable
- **Action pinning**: not applicable
- **Caching**: not applicable
- **Test runner invocation**: test file docstring says `cd resume_skill && python -m pytest tests/ -v` — but the directory is actually `renderer/`, not `resume_skill/`, so the doc itself is stale (the `resume_skill` name refers to the installed package, not the source directory). Correct invocation: `cd renderer && python -m pytest tests/ -v`.
- **Pitfalls observed**: no CI means the pyproject.toml / requirements.txt drift, the stale test-docstring path, and the two-SKILL.md-copies inconsistency are never caught automatically. Tests manipulate `sys.path` instead of relying on an installed package, so they run against source even if an older version is pip-installed — hides install-path bugs.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable — no releases have ever been cut (`gh api .../releases` count=0)
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable — no `CHANGELOG.md`
- **Pitfalls observed**: no release process means version-drift is the only version story; users cannot install a stable ref.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable — no validation tooling
- **Trigger**: not applicable
- **Frontmatter validation**: not applicable
- **Hooks.json validation**: not applicable (no hooks.json to validate)
- **Pitfalls observed**: the `owner.email: "your-email@example.com"` placeholder in `marketplace.json` would have been caught by any schema-level validator. It was not.

## 16. Documentation

- **`README.md` at repo root**: present — 40958 bytes, bilingual (English + Chinese), with Table of Contents, five install methods, update/uninstall, dual AI-agent-targeted install-prompt section ("For AI Coding Agents — Read This First") containing literal clone+install commands for Claude Code, Cursor, Windsurf, OpenClaw
- **Owner profile README at `github.com/SankaiAI/SankaiAI`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: absent — single-plugin repo; the root README is the plugin README
- **`CHANGELOG.md`**: absent
- **`architecture.md`**: absent
- **`CLAUDE.md`**: absent
- **Community health files**: `PRIVACY.md` present (1530 bytes). No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- **LICENSE**: present (MIT)
- **Badges / status indicators**: absent
- **Pitfalls observed**: README opens with a prompt-injection-style "⚡ For AI Coding Agents — Read This First" block containing pre-written install commands — a deliberate pattern targeting agent-assisted installs, not a pitfall per se, but worth flagging as a design choice (see §17). `architecture.md`/`CLAUDE.md` absence is consistent with the project being a single-skill plugin where `SKILL.md` + `README.md` carry the load.

## 17. Novel axes

- **Agent-targeted install preamble in README.** The README begins with a blockquote-rendered "⚡ For AI Coding Agents — Read This First" section containing literal shell commands to clone+install, segmented by OS (Mac/Linux, Windows) × scope (user, project) × agent (Claude Code, OpenClaw). The intent is that when a user asks their coding agent to install this plugin, the agent WebFetches the README and gets an unambiguous install recipe at the very top. This is a distinct consumer surface from the human-facing "Method 0/1/2/3/4" sections further down — the same install intent encoded twice, once for agents, once for humans.

- **Dual install paths via independent mechanisms.** The repo supports (a) marketplace install via `.claude-plugin/marketplace.json` + `plugin.json` + `bin/` wrappers, and (b) direct install via `install.sh` / `install.ps1` + `pip install renderer/` + copying root `SKILL.md` into the user's skills dir. The two paths use different install mechanics (plugin bin-wrapper pip-install-on-first-run vs. standalone pip-install) and different source-tree consumption (PYTHONPATH-pointed-at-`src/` vs. proper installed console-script). A single-source-of-truth violation — the plugin mechanism does not share the standalone-install mechanism.

- **First-run pip-install pattern without venv or change detection.** The `bin/resume-skill` wrapper probes `python -c "import docx"` and, on ImportError, runs `pip install python-docx lxml --quiet` against whatever `python`/`pip` are in PATH. No venv, no pinning, no change detection beyond existence. Contrast with patterns seen elsewhere in research sample (uv venv under `${CLAUDE_PLUGIN_DATA}`, PEP 723 inline metadata with `uv run --script`, `requirements.txt` sha tracking). This is the minimum-viable Python-dep-install pattern and makes dependency isolation the user's problem.

- **Bash + `.cmd` pair (no `.ps1` runtime shim).** Windows support for the runtime CLI is via `bin/resume-skill.cmd` (cmd.exe batch), not PowerShell. This is a specific cross-platform-CLI pattern worth calling out — the convention is "POSIX bash + Windows .cmd" rather than "POSIX bash + PowerShell .ps1". A single `install.ps1` exists separately for the one-shot install flow, but the runtime wrapper is `.cmd`.

- **Three-way version sync with no enforcement.** `marketplace.json` has `metadata.version`, `plugins[0].version`, AND the pointed-to `plugin.json.version` — all three hand-maintained. No schema validation, no CI check, no single-source marking which is authoritative.

- **Triple bilingual content.** README is explicitly bilingual (English + Chinese, `[English](#english) | [中文](#chinese)`). Uncommon in Claude Code plugin READMEs — worth noting as community-reach signal.

## 18. Gaps

- **Blob file mode (octal permissions).** The GitHub API `contents` endpoint I used does not expose the git blob mode byte for `bin/resume-skill` and `install.sh`. Answer inferred from shebang presence and README prescription (`chmod +x install.sh`). Definitive answer would require `git ls-tree HEAD bin/` on a local clone or the `git/trees` API tree-entry `mode` field. Tree API does include `mode` but I did not request it specifically; acknowledging as a verification gap.

- **Whether `skills/build-tailored-resume/SKILL.md` is a git-native symlink or a content duplicate.** Both files are reported as 17916 bytes and I read the frontmatter of both and observed identical opening content. The tree listing reported both as `blob` type, not `120000` symlink mode — but again, mode not inspected. If the two are genuinely a content copy, every future SKILL.md edit has to land twice. If one is a symlink, only one is authoritative. A `git cat-file -p` against the tree entry would resolve this; within the WebFetch/gh-api budget I could not confirm.

- **Whether the `bin/` directory is actually added to PATH by Claude Code at install time as the bash wrapper's comment claims.** The `resume-skill` comment says "Claude Code automatically adds the plugin's bin/ directory to the Bash tool's PATH when the plugin is installed." This is a claim about Claude Code runtime behavior, not about the repo itself. Verification would require the Claude Code `docs-plugins-reference.md` (present in `research/claude-marketplace/context-resources/`) — I did not cross-reference during this pass. The claim matches the surfaced "bin directory on PATH" pattern from the plugin reference docs, but I did not re-verify against the current doc version.

- **Actual pip-install behavior across Python environments.** The `bin/resume-skill` wrapper's `|| pip install` is behavior-tested only by whatever test suite the author ran locally; with no CI and no integration tests covering the install flow, any claim about "does this actually work on Python 3.10 / 3.11 / 3.12 / on macOS / on Windows / on WSL / under conda" is untestable from the repo alone. I documented the code; I cannot attest to runtime correctness.

- **Whether the placeholder email (`your-email@example.com`) causes any marketplace-installer warning.** Claude Code's `/plugin install` flow may or may not surface this as a validation warning. Unable to confirm without running the install.
