# 123jimin-vibe/plugin-prompt-engineer

## Identification

- **URL**: https://github.com/123jimin-vibe/plugin-prompt-engineer
- **Stars**: 0
- **Last commit date**: 2026-04-11 (commit `7e9e336d`, "Update hypotheses.md")
- **Default branch**: main
- **License**: MIT (SPDX `MIT`)
- **Sample origin**: dep-management
- **One-line purpose**: "Claude Code plugin for prompt engineering" (repo description; README body adds token-counter, LLM invocation with Q&A mode, and a "prompt playground" — all marked as in-active-development).

## 1. Marketplace discoverability

- **Manifest layout**: no marketplace manifest — this is a single-plugin repo, not a marketplace. Repo root `.claude-plugin/` does not exist; only `plugin/.claude-plugin/plugin.json` is present. Plugin lives at `plugin/` (non-conventional — most single-plugin repos put `.claude-plugin/` at repo root).
- **Marketplace-level metadata**: not applicable (no marketplace.json).
- **`metadata.pluginRoot`**: not applicable (no marketplace.json).
- **Per-plugin discoverability**: `plugin.json` contains only `name`, `description`, `version` — no category/tags/keywords.
- **`$schema`**: absent.
- **Reserved-name collision**: no.
- **Pitfalls observed**: a marketplace consumer adding this repo must use `source: { source: "github", repo: "123jimin-vibe/plugin-prompt-engineer", path: "plugin" }` (or equivalent subdir pointer) rather than expect a root-level plugin; there is no marketplace.json to self-advertise. README is a stub (162 bytes) with just headings and an "active development" caution — no installation instructions.

## 2. Plugin source binding

- **Source format(s) observed**: not applicable — repo publishes a plugin, not a marketplace entry. Only the plugin's own `plugin.json` is present; no `source:` field is declared anywhere.
- **`strict` field**: not applicable (no marketplace entry in this repo).
- **`skills` override on marketplace entry**: not applicable.
- **Version authority**: `plugin/.claude-plugin/plugin.json` only (currently `0.0.17`). The separate `plugin/pyproject.toml` has its own `version = "0.0.1"` that is never bumped — it's used only by pip-install for package metadata; the plugin version is what `ensure-deps.py` reads. Drift risk is immaterial here because the pyproject version is never referenced by anything user-facing.
- **Pitfalls observed**: the `pyproject.toml` version at `0.0.1` while `plugin.json` is `0.0.17` could confuse someone skimming the package. The plugin treats `plugin.json.version` as the single source of truth for install-detection; `pyproject.toml.version` is effectively a dummy.

## 3. Channel distribution

- **Channel mechanism**: no split. Users pin via git `@ref` in their marketplace entry — tags `v0.0.1` through `v0.0.17` are all monotonic on `main` (tag chain is a linear ancestor of HEAD).
- **Channel-pinning artifacts**: absent.
- **Pitfalls observed**: no stable-vs-latest carve-out exists, so consumers choosing `@main` vs `@v0.0.17` get dev vs last-tag in the normal way. The in-active-development caution in README suggests `@main` is unstable.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main — tags `v0.0.1`..`v0.0.17` each sit on a linear chain in `main`'s history (confirmed via `compare/v0.0.17...main` → main is 14 commits ahead, 0 behind).
- **Release branching**: none (tag-on-main). No `release/*` branches exist — only `main` is listed in branches.
- **Pre-release suffixes**: none observed.
- **Dev-counter scheme**: present but flat — all versions are `0.0.z` monotonic with z incrementing on each tagged bump (17 tags across `0.0.1`..`0.0.17`). No `0.0.z` dev + `x.y.z` release-branch split; `0.0.z` is the only lane.
- **Pre-commit version bump**: no automated hook observed. The bumps appear to be manual commits titled "Update plugin.json" — e.g. the `v0.0.17` commit message is literally `Update plugin.json`. No `.pre-commit-config.yaml` or `.githooks/` present.
- **Pitfalls observed**: there is no release automation, no tag-sanity gate, and no pre-release suffix convention. Human discipline (name the commit "Update plugin.json", tag immediately) is the only safeguard against a drift between the committed plugin.json version and the tag name.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery only — `plugin.json` contains `{name, description, version}` and nothing else. All components are discovered by convention from the plugin root.
- **Components observed**:
    - skills: yes (`plugin/skills/invoke-llm/`, `plugin/skills/token-counter/`)
    - commands: no
    - agents: yes (`plugin/agents/prompt-engineer.md`)
    - hooks: yes (`plugin/hooks/hooks.json`)
    - .mcp.json: no
    - .lsp.json: no
    - monitors: no
    - bin: no
    - output-styles: no
- **Agent frontmatter fields used**: `name`, `description`, `model`. Only one agent (`prompt-engineer.md`) observed. `model: inherit` is used — no `tools`, `skills`, `memory`, `background`, or `isolation` fields declared.
- **Agent tools syntax**: not applicable — no `tools` field on the agent.
- **Pitfalls observed**: skills use `${CLAUDE_SKILL_DIR}/scripts/<name>.py` in their SKILL.md bodies, paired with instruction "Run with the plugin venv at `${CLAUDE_PLUGIN_DATA}/venv`". The agent relies on skill invocation for any script execution; it has no direct `tools` restrictions.

## 6. Dependency installation

- **Applicable**: yes. Python deps via uv-less pip + venv pattern.
- **Dep manifest format**: `pyproject.toml` at `plugin/pyproject.toml`. Dependencies: `anthropic>=0.45`, `openai>=1.0`, `tiktoken>=0.7`. `requires-python = ">=3.11"`. The plugin root itself is pip-installed as an editable-style package (`[tool.setuptools.packages.find] include = ["lib", "lib.*"]`) so scripts can `from lib.llm import ...`.
- **Install location**: `${CLAUDE_PLUGIN_DATA}/venv` (virtualenv) and `${CLAUDE_PLUGIN_DATA}/installed-version` (version sentinel file).
- **Install script location**: `plugin/scripts/ensure-deps.py`, invoked from `plugin/hooks/hooks.json`'s SessionStart hook as `python "${CLAUDE_PLUGIN_ROOT}/scripts/ensure-deps.py"`.
- **Change detection**: **version file stamp**. On each SessionStart, `ensure-deps.py`:
    1. Reads current plugin version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` via `json.loads(...)["version"]`.
    2. Reads the last-installed version from `${CLAUDE_PLUGIN_DATA}/installed-version` (a plain text file containing a single version string like `0.0.17`).
    3. If the file exists and its stripped content equals the current version: return immediately (no-op — "up to date").
    4. Otherwise: create venv if missing (`venv.create(venv_dir, with_pip=True)`), `pip install --upgrade <plugin_root>`, then **write the new version to `installed-version` only on pip-install success**.

    The stamp file is treated as authoritative: its absence or mismatched content triggers a reinstall. No hashing of `pyproject.toml`, no mtime, no diff of the dep list itself — the plugin version bump *is* the reinstall trigger. That makes `plugin.json.version` a double-duty field: semver for users and install-staleness signal for the ensure-deps script.
- **Retry-next-session invariant**: `rm` on failure — the `try/except` in `install()` wraps the pip-install + version-file-write in a single block; on any exception it calls `version_file.unlink(missing_ok=True)` and re-raises. This guarantees a half-installed venv is not remembered as "done" — next SessionStart will see the missing stamp and retry.
- **Failure signaling**: on failure the exception propagates (non-zero exit). On success the script prints `{"systemMessage": "prompt-engineer plugin dependencies installed (v<version>)."}` to stdout so the host surfaces the install event in the session transcript. Silent on no-op (already up-to-date). `hooks.json` sets `statusMessage: "prompt-engineer: Installing dependencies..."` for the pre-exec status line.
- **Runtime variant**: Python `pip` (not uv) + stdlib `venv`. Deliberately avoids external tooling — only Python stdlib + pip inside the created venv.
- **Alternative approaches**: none — pip-installs the plugin as a package so `lib/` becomes importable. No PEP 723 scripts, no `uvx`, no pointer-file pattern.
- **Version-mismatch handling**: none beyond the stamp-file mechanism. The script does not pin to a specific Python ABI — it relies on `sys.platform` only to pick `Scripts/pip` (Windows) vs `bin/pip` (everything else). If the host Python minor version changes, the stale venv would not be detected (the version stamp is plugin version, not Python version); the user would have to manually wipe `${CLAUDE_PLUGIN_DATA}/venv`.
- **Pitfalls observed**:
    - The ensure-deps script docstring explicitly calls itself "reusable across any Claude Code plugin that ships a `pyproject.toml`" — it is a reference implementation that could be copy-pasted, but the emit_system_message hard-codes the `prompt-engineer` name.
    - `subprocess.run(..., check=True)` with no stdout/stderr capture means pip's chatty output streams through the SessionStart hook console.
    - t0004 in `worklog/archive/task/` targeted adding `"async": true` to the SessionStart hook ("initial installation takes ~40s"); the deployed `hooks.json` does *not* have `async: true` yet — the archived task predates or was abandoned. Users hitting first install wait ~40s synchronously.
    - The version-file approach treats any plugin bump (e.g. a README edit bump) as a full reinstall — including pure-metadata changes that don't touch deps.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no. Skills invoke Python scripts directly via `python "<script>"` inside the plugin venv; there is no `bin/` directory, no shebang wrappers, no standalone CLI.
- **`bin/` files**: not applicable.
- **Shebang convention**: not applicable (scripts are invoked by the venv's python, not by shebang).
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: invoked indirectly — the PreToolUse `allow-skill-scripts.py` hook validates that `parts[0]` (the python executable in the Bash command) is inside `${CLAUDE_PLUGIN_DATA}/venv` before auto-approving. The expected invocation shape is `<venv-python> <skill-script-path>`.
- **Platform support**: not applicable.
- **Permissions**: not applicable.
- **SessionStart relationship**: not applicable.
- **Pitfalls observed**: the scripts themselves (e.g. `plugin/skills/invoke-llm/scripts/invoke.py`) have no shebang. They can only be run as `<venv-python> invoke.py`. Users cannot chmod-exec them.

## 8. User configuration

- **`userConfig` present**: no.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable. API keys are read from shell environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`) via `plugin/lib/apikey.py`'s `require_api_key()`; there is no plugin-config surface to substitute. SKILL.md documents the env var names directly.
- **Pitfalls observed**: no `sensitive: true` flag because the plugin never asks the user for the key through plugin config — it assumes shell-level env vars. A user who has not exported `ANTHROPIC_API_KEY` gets a "variable needs to be configured" exit from `require_api_key()`.

## 9. Tool-use enforcement

- **PreToolUse hooks**: 1, matcher `"Bash"`, purpose: auto-allow plugin skill-script invocations. The hook command is an inline bash one-liner doing a `case` fast-path string match on raw stdin (`*/.claude/*/prompt-engineer/*/skills/*/scripts/*`); only on match does it pipe into Python's `allow-skill-scripts.py` validator.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: stdout JSON only on allow (`{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "permissionDecisionReason": "Plugin skill script invocation"}}`); silent (empty stdout, exit 0) for non-matches. No stderr noise. Deny decisions are never emitted — the hook is "pessimistic" (per script docstring): if validation fails, it exits with no opinion rather than deny, letting the normal permission flow ask the user.
- **Failure posture**: fail-open from the user's perspective — a bug in the validator means the user is asked normally rather than blocked. Malformed JSON stdin, missing env vars (well — missing env vars raise `RuntimeError`, which exits non-zero), or path-resolve failures (`OSError`, `ValueError` on `Path.resolve(strict=True)`) all silently return.
- **Top-level try/catch wrapping**: per-helper try/except around `Path.resolve(strict=True)` calls, not a top-level wrapper. `main()` will propagate exceptions from `RuntimeError` on missing env vars.
- **Pitfalls observed**:
    - `d0004` (decision log) documents that the *original* matcher attempt was `Bash(.*/invoke-llm/scripts/invoke\.py.*)` which never fired because Claude Code's hook matcher tests only the bare tool name, not the input; the permission-rules `Tool(pattern)` syntax is a separate code path. The fix was to flatten matcher to `"Bash"` and do the path filter inline in bash — fast-path for 99% of unrelated Bash calls.
    - The here-string `<<< "$input"` is used instead of `echo "$input" | ...` to safely pass JSON with embedded quotes.
    - The validator hard-codes `prompt-engineer` in the bash `case` pattern, making it non-portable across plugin renames.

## 10. Session context loading

- **SessionStart used for context**: no — only for dep install (see purpose 6).
- **UserPromptSubmit for context**: no (hook is absent).
- **`hookSpecificOutput.additionalContext` observed**: no.
- **SessionStart matcher**: none declared — the hook entry has no `matcher` field, so it fires on all SessionStart sub-events (startup, resume, clear, compact per Claude Code's reference).
- **Pitfalls observed**: ensure-deps re-runs on every sub-event including `compact`, which is wasted work on the no-op path but cheap (file-read + string compare). No additional context is injected; this plugin is purely skill + hook based.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none — monitors are simply not used.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin repo; tag format is plain `v0.0.z`).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: Python `unittest` (module-level classes), executed via `pytest` runner.
- **Tests location**: `tests/` at repo root, mirroring `plugin/` structure — e.g. `plugin/scripts/allow-skill-scripts.py` → `tests/scripts/test_allow_skill_scripts.py`; `plugin/lib/llm.py` → `tests/lib/test_llm.py`. Subdirs: `tests/lib/`, `tests/scripts/`, `tests/skills/invoke_llm/`, `tests/skills/token_counter/` (note skills dirs use underscore in tests but hyphen in plugin path; tests use `importlib.util.spec_from_file_location` to load hyphen-named modules).
- **Pytest config location**: none — no `pytest.ini`, no `[tool.pytest.ini_options]` in `pyproject.toml`, no `setup.cfg`. `pyrightconfig.json` exists for type checking only. Test invocation relies on pytest's default discovery.
- **Python dep manifest for tests**: `pyproject.toml` at `plugin/pyproject.toml` lists runtime deps; there is no `requirements-dev.txt` or dev-dep group declared. Tests use `unittest.mock` from stdlib, so the runtime deps suffice.
- **CI present**: no. No `.github/workflows/` directory exists (404 on `.github` contents).
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: `python -m pytest tests/ -v` per `worklog/spec/infra/s0004-testing.md`. No wrapper script. `.claude/settings.json` allow-lists `Bash(python -m pytest *)`.
- **Pitfalls observed**:
    - No CI means nothing verifies the version-bump → tag → install-pathway integration; failures show up on user `SessionStart` only.
    - Tests load modules with hyphens in filenames (`allow-skill-scripts.py`) via `importlib.util.spec_from_file_location` per an explicit convention documented in `s0004-testing.md` — this is load-bearing because pytest's standard import machinery can't handle the hyphen. The testing spec also mandates "tests must be written **without reading the implementation** — only the function signatures and docstrings" as a discipline rule.
    - `tests/lib/test_llm.py` pre-registers `lib.apikey` into `sys.modules` manually before loading the module under test, so tests work outside the plugin venv — a notable workaround to avoid needing the plugin venv for development.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable. Releases are bare git tags on main — no `gh release create`, no GitHub Releases entries (confirmed `releases` API returns `[]`).
- **Tag-sanity gates**: none. Nothing verifies `plugin.json.version` matches the tag name.
- **Release creation mechanism**: manual `git tag vX.Y.Z && git push --tags` implied by the history. The `releases` API endpoint returns 0 entries, so no GitHub Release objects exist — only bare tags.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable (no CHANGELOG.md).
- **Pitfalls observed**: the release discipline is entirely human: commit titled `Update plugin.json` → push → tag. A mismatched tag name (e.g., `git tag v0.0.18` when plugin.json says `0.0.17`) would deploy a version that install-detection can't distinguish from a prior install. The `installed-version` stamp matches plugin.json, not the tag, so as long as plugin.json is correct the install works — the tag is purely a git convenience for consumers pinning with `@v0.0.17`.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable.
- **Trigger**: not applicable.
- **Frontmatter validation**: no — nothing checks that SKILL.md or agent YAML frontmatter is well-formed or contains required fields.
- **Hooks.json validation**: no — nothing checks hooks.json shape. `d0003` (superseded by `d0004`) was a manual investigation into why skill-scoped matchers didn't fire; a validator would not have caught this (it's a semantic runtime bug, not a schema error).
- **Pitfalls observed**: the repo relies on pyright (`pyrightconfig.json` → `pythonVersion: "3.14"`, `extraPaths: ["plugin"]`, `include: ["plugin", "tests"]`) for Python type checking, but this runs only in the developer's editor — there is no enforced pre-commit gate or CI check for anything.

## 16. Documentation

- **`README.md` at repo root**: present but **stub-only** — 162 bytes, consisting of four markdown headings (`# Prompt Engineer`, `## Token Counter`, `## LLM Invocation`, `### Q&A Mode`, `## Prompt Playground`) and a `> [!CAUTION]` admonition reading "This repository is currently in active development." No content under any heading. No install/usage instructions.
- **Owner profile README at `github.com/123jimin-vibe/123jimin-vibe`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: absent. The `plugin/` directory has no README; nor do `plugin/skills/<name>/`. Each SKILL.md serves as the skill's docs.
- **`CHANGELOG.md`**: absent.
- **`architecture.md`**: absent in the conventional sense, but `worklog/spec/` functions as a scattered architecture reference: `s0001-prompt-engineer-plugin.md` (top-level), `s0003-python-environment.md`, `s0004-testing.md`, `s0006-invoke-llm.md`, `s0007-exams.md`, `s0008-llm-providers.md`, `s0009-hooks.md`, `s0010-prompt-engineer-agent.md` etc.
- **`CLAUDE.md`**: absent.
- **Community health files**: none — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`.
- **LICENSE**: present — MIT (1089 bytes).
- **Badges / status indicators**: absent.
- **Pitfalls observed**: the public-facing documentation is effectively absent (stub README + no per-plugin README). The project's substantive documentation lives entirely inside `worklog/` (specs, decisions, archived tasks) — an internal developer log, not a user-facing doc. A new consumer has no guidance on how to install or configure the plugin; they must infer from `plugin.json`, `hooks.json`, and the SKILL.md files.

## 17. Novel axes

- **Worklog as a primary design artifact**: the `worklog/` directory is a first-class, numerically-keyed spec/decision/task ledger — not the one-offs I've seen in most repos. Structure: `worklog/archive/task/t0001..t0011-<slug>.md` (completed tasks, 11 archived), `worklog/decision/d0001..d0004-<slug>.md` (4 ADRs), `worklog/spec/<category>/s0001..s0010-<slug>.md` (10 specs split by category — infra / lib / skill / top-level). Each decision doc uses TOML-fence frontmatter with `id`, `title`, `relates_to`, `supersedes` keys (`d0004` supersedes `d0003` with explicit tracking). This is a deliberate long-form design practice built into the repo layout — tasks move from spec → task → archived-task lifecycle, and decisions cross-link. Noteworthy as a reference for how a plugin repo can embed design-decision history inside the repo rather than rely on PRs/issues.
- **`lab/` compression experiments**: the repo contains a substantial `lab/compression/` experimental directory with TOML config files, JSONL data files (`document.jsonl`, `paragraph.jsonl`, `sentence.jsonl`), per-granularity analysis docs (`doc/01..16`, `para/01..20`, `sent/01..20`), and results (`results/*.jsonl`) — appears to be an active research effort on prompt/context compression that's part of the repo but not shipped in the plugin. This is a "research living with the product" organization.
- **`exams/` directory**: top-level `exams/token-counter/basic-usage.toml` suggests an evaluation corpus for skill outputs — a structured test-by-example mechanism external to the unit tests. Minimally populated but indicates intent.
- **"Pessimistic no-opinion" hook design**: the `allow-skill-scripts.py` docstring explicitly states the design discipline — "every check that fails exits 0 with no output (no opinion, does not auto-allow). Only an exact match produces an allow." This is a consciously chosen safer default than fail-open-with-allow or deny-on-uncertainty; it defers to the normal permission flow for anything unclear. Worth lifting as a convention for other hook authors.
- **Bash fast-path + Python validator hook shape**: the inline `case "$input" in <pattern>) python validator ;; esac` pattern in `hooks.json` — avoiding Python startup for 99% of unrelated Bash calls while keeping full-strength validation for matches — is a substantive design pattern documented in `d0004`. The here-string `<<< "$input"` for JSON-safe piping is a subtle detail worth codifying.
- **Plugin root is a pip-installable package**: `plugin/pyproject.toml` declares `[tool.setuptools.packages.find] include = ["lib", "lib.*"]` so scripts can use `from lib.llm import invoke as llm_invoke`. The ensure-deps script pip-installs `str(plugin_root)` against the venv, not just the deps — this is how `lib/` becomes importable from skill scripts. This is an alternative to PYTHONPATH manipulation or sys.path.insert gymnastics and is worth naming as a distinct pattern.
- **Plugin version double-duty as install-staleness trigger**: using `plugin.json.version` as both the user-facing semver and the single "reinstall needed?" signal — rather than a separate content hash or `requirements.txt` mtime — is a clean simplification that's worth calling out. The cost is that a no-op plugin version bump (e.g., a README-only fix) triggers a full `pip install --upgrade`, which the repo appears to accept.
- **`statusMessage` vs `systemMessage` distinction**: the hooks.json SessionStart entry sets `statusMessage: "prompt-engineer: Installing dependencies..."` (shown during execution), while `ensure-deps.py` emits `{"systemMessage": "..."}` on success (shown after). Two surfaces, two stages.

## 18. Gaps

- **Plan for async SessionStart**: `worklog/archive/task/t0004-async-session-start.md` documents adding `"async": true` to the SessionStart hook but the currently deployed `hooks.json` does not contain that field. Whether t0004 was abandoned, whether a follow-up changed course, or whether `async` doesn't need to appear in the config (e.g. automatic) — I couldn't resolve from visible files. Git log of `plugin/hooks/hooks.json` would clarify.
- **Actual `invoke.py` + `count.py` sizes and shebangs**: I saw only the first ~60–100 lines of each; whether they fully absent shebangs (as implied) vs have some other exec convention would need the full file. The SKILL.md phrasing ("Run with the plugin venv at `${CLAUDE_PLUGIN_DATA}/venv`") and the allow-skill-scripts validator shape (which expects `parts[0]` to be a venv python) both indicate no shebang, but I didn't read the final lines.
- **Exams directory purpose**: `exams/` contains `token-counter/basic-usage.toml` but no docs on how exams are run. `worklog/spec/infra/s0007-exams.md` presumably defines this; I didn't fetch it.
- **`lab/compression/` experiment goal**: unclear whether it's a planned future skill, a writeup, or a one-off research artifact. `lab/compression/hypotheses.md` and `findings.md` would resolve.
- **Any consumer of this plugin as a marketplace source**: without a marketplace.json in this repo, it's unclear whether the author maintains a separate marketplace repo that references `123jimin-vibe/plugin-prompt-engineer` — a cross-repo reference would determine the `source:` format actually in use.
- **Prompt-engineer agent's deployment shape**: the agent file is tiny (2-line body after frontmatter) and `model: inherit`. Unclear if it's a stub under active development (README caution supports this) or a deliberate thin agent that delegates entirely to skills.
- **Whether `pyproject.toml.version = "0.0.1"` is a bug**: it's possible the author intentionally freezes it because nothing consumes it; alternatively it may be an oversight. A commit-log review of `plugin/pyproject.toml` would clarify intent.
