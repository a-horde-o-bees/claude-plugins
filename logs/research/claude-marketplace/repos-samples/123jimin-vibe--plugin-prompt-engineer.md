# Sample

Mirrors of `https://github.com/123jimin-vibe/plugin-prompt-engineer`. Single-plugin repo for prompt-engineering tools (token counter, LLM invocation with Q&A mode, prompt playground); plugin lives at `plugin/` (not at repo root). MIT-licensed; in active development per the README admonition.

## Marketplace manifest layout

### No marketplace manifest (plugin source repo only)

The repo carries only `plugin/.claude-plugin/plugin.json`; no `marketplace.json` exists anywhere. The plugin lives at `plugin/` rather than at repo root. A marketplace consumer adding this repo must author a `source: { source: "github", repo: "123jimin-vibe/plugin-prompt-engineer", path: "plugin" }` entry by hand. README is a 162-byte stub with four headings (`# Prompt Engineer`, `## Token Counter`, `## LLM Invocation`, `## Prompt Playground`) and an "active development" caution, no install instructions.

## Plugin source binding

### Direct git install (no marketplace.json in source repo)

No `marketplace.json` is shipped in the repo, so users either install via `claude plugin install github:123jimin-vibe/plugin-prompt-engineer` or rely on a separate marketplace aggregator referencing this repo. The plugin's own `plugin/.claude-plugin/plugin.json` is at `0.0.17`; a separate `plugin/pyproject.toml` carries `version = "0.0.1"` that is never bumped — used only by pip for package metadata, not user-facing.

## Per-plugin discoverability metadata

### Bare-minimum (name, version, description only)

`plugin/.claude-plugin/plugin.json` declares only `{name, description, version}` — no `category`, `tags`, `keywords`, `author`, or `repository`. No marketplace entry exists in this repo to mirror or extend these.

### `$schema` absence on per-plugin manifests

`$schema` is absent from `plugin.json`. Editor schema-completion is unavailable.

## Version coordination

### Single source of truth (`plugin.json` only)

`plugin/.claude-plugin/plugin.json` `version` is the only user-facing version (`0.0.17`); `plugin/pyproject.toml.version = "0.0.1"` is consumed only by pip metadata and drifts harmlessly because `ensure-deps.py` reads `plugin.json.version` for install-detection. Users who want to pin do so at the git-ref level (`@v0.0.17`).

## Channel distribution

### Linear `0.0.z` dev counter

All releases are `0.0.z` monotonic with z incrementing per tagged bump (17 tags `v0.0.1`..`v0.0.17`). No `x.y.z` release-branch split; `0.0.z` is the only lane. `@main` vs `@v0.0.17` resolution is the only pinning surface. README's "active development" admonition implies `@main` is unstable.

## Tag and release lifecycle

### Tag-on-main, single branch

Tags `v0.0.1`..`v0.0.17` each sit on a linear chain in `main`'s history (confirmed via `compare/v0.0.17...main` → main is 14 commits ahead, 0 behind). Only `main` is listed in branches; no `release/*` branches exist. Bumps are manual commits titled "Update plugin.json"; no `.pre-commit-config.yaml` or `.githooks/` present. No `gh release create`, no GitHub Releases entries (`releases` API returns `[]`) — only bare git tags. Release discipline is entirely human: commit titled `Update plugin.json` → push → `git tag vX.Y.Z && git push --tags`.

## Plugin-component registration

### Default convention discovery

`plugin/.claude-plugin/plugin.json` carries only `{name, description, version}` and no component arrays. All components are discovered by convention from `plugin/skills/`, `plugin/agents/`, and `plugin/hooks/hooks.json` at the plugin root.

## Component composition

### Skills (universal)

Two skills: `plugin/skills/invoke-llm/` and `plugin/skills/token-counter/`. SKILL.md bodies invoke scripts via `${CLAUDE_SKILL_DIR}/scripts/<name>.py` paired with the instruction "Run with the plugin venv at `${CLAUDE_PLUGIN_DATA}/venv`".

### Agents

One agent: `plugin/agents/prompt-engineer.md`. Frontmatter declares `name`, `description`, `model: inherit`. No `tools`, `skills`, `memory`, `background`, or `isolation` fields. Body is two lines after frontmatter — relies on skill invocation for any script execution.

### Hooks

`plugin/hooks/hooks.json` registers a SessionStart hook for dependency install plus a single PreToolUse `"Bash"` matcher hook auto-allowing skill-script invocations.

## Skill authoring conventions

### Standard frontmatter

SKILL.md frontmatter declares standard fields. Skill bodies prescribe invocation as `<venv-python> "${CLAUDE_SKILL_DIR}/scripts/<name>.py"` using the venv at `${CLAUDE_PLUGIN_DATA}/venv`.

## Agent declaration conventions

### Minimal frontmatter (name, description)

The single agent (`prompt-engineer.md`) carries `name`, `description`, `model: inherit` — no `tools` field, no orchestration knobs (`background`, `isolation`, `effort`, `maxTurns`). Body is a 2-line stub. Has no direct tool restrictions; delegates entirely to skills.

## Server runtime (MCP)

### No bin entry / direct invocation

No MCP server registered. Skills invoke Python scripts directly via `<venv-python> <script>` inside the plugin venv; there is no `bin/` directory, no shebang wrappers, no standalone CLI. Scripts (e.g. `plugin/skills/invoke-llm/scripts/invoke.py`) have no shebang and can only be run as `<venv-python> invoke.py`.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory; no user-PATH binary. Skill scripts are invoked indirectly — the PreToolUse `allow-skill-scripts.py` hook validates that `parts[0]` (the python executable in the Bash command) is inside `${CLAUDE_PLUGIN_DATA}/venv` before auto-approving. Expected invocation shape is `<venv-python> <skill-script-path>`.

## Dependency installation

### Pip + stdlib venv (no `uv`)

Python deps installed into `${CLAUDE_PLUGIN_DATA}/venv` via stdlib `venv` + pip during a SessionStart hook. `plugin/scripts/ensure-deps.py` is invoked from `plugin/hooks/hooks.json`'s SessionStart hook as `python "${CLAUDE_PLUGIN_ROOT}/scripts/ensure-deps.py"`. `plugin/pyproject.toml` declares dependencies `anthropic>=0.45`, `openai>=1.0`, `tiktoken>=0.7` and `requires-python = ">=3.11"`. The plugin root is pip-installed as a package (`[tool.setuptools.packages.find] include = ["lib", "lib.*"]`) so skill scripts can `from lib.llm import ...`. The script does not pin to a specific Python ABI; uses `sys.platform` only to pick `Scripts/pip` (Windows) vs `bin/pip` (other). Avoids `uv` — only Python stdlib + pip inside the created venv. `subprocess.run(..., check=True)` with no stdout/stderr capture lets pip's chatty output stream through the SessionStart hook console.

## Install change detection

### Plugin-version stamp file

On each SessionStart, `ensure-deps.py` reads the current plugin version from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` via `json.loads(...)["version"]`, reads the last-installed version from `${CLAUDE_PLUGIN_DATA}/installed-version` (a plain text file containing a single version string like `0.0.17`), and if the file exists and its stripped content equals the current version: returns immediately (no-op). Otherwise creates the venv if missing (`venv.create(venv_dir, with_pip=True)`), `pip install --upgrade <plugin_root>`, then writes the new version to `installed-version` only on pip-install success. No hashing of `pyproject.toml`, no mtime, no diff of the dep list — `plugin.json.version` doubles as semver and reinstall trigger; any plugin bump (including README-only edits) triggers a full reinstall.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks.json` registers `ensure-deps.py` directly on SessionStart with `statusMessage: "prompt-engineer: Installing dependencies..."` for the pre-exec status line. SessionStart sub-event matcher is absent; the hook fires on all sub-events (startup, resume, clear, compact). On the no-op path the cost is a file-read + string compare. First install takes ~40s synchronously — `worklog/archive/task/t0004-async-session-start.md` proposed adding `"async": true` but the deployed `hooks.json` does not have it.

## Install failure posture

### `rm` stamp on failure (retry next session)

The `try/except` in `install()` wraps the pip-install + version-file-write in a single block; on any exception it calls `version_file.unlink(missing_ok=True)` and re-raises. A half-installed venv is not remembered as "done" — the next SessionStart sees the missing stamp and retries. On failure the exception propagates (non-zero exit). On success the script prints `{"systemMessage": "prompt-engineer plugin dependencies installed (v<version>)."}` to stdout. Silent on no-op (already up-to-date).

## User configuration and authentication

### Out-of-band env vars (no `userConfig`)

`plugin.json` has no `userConfig` block. API keys are read from shell environment variables `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY` via `plugin/lib/apikey.py`'s `require_api_key()`; SKILL.md documents the env var names directly. A user who has not exported `ANTHROPIC_API_KEY` gets a "variable needs to be configured" exit from `require_api_key()`. No `sensitive: true` flag because the plugin never asks the user for the key through plugin config.

## Session context loading

### Dependency install only (no context emission)

The SessionStart hook is purely for `ensure-deps.py` execution. No `additionalContext`, no `systemMessage` for context, no UserPromptSubmit hook. The plugin emits no model-facing context — purely skill + hook based.

## SessionStart matcher scope

### Empty matcher (all sub-events)

The SessionStart hook entry has no `matcher` field, so it fires on all sub-events including `compact`. On the no-op path this is wasted work but cheap (file-read + string compare).

## Tool-use enforcement

### Auto-allow plugin's own scripts

One PreToolUse hook with matcher `"Bash"`. Inline bash one-liner does a `case` fast-path string match on raw stdin (`*/.claude/*/prompt-engineer/*/skills/*/scripts/*`); only on match does it pipe into Python's `allow-skill-scripts.py` validator. Validator uses `Path.resolve(strict=True)` for traversal-resistance and exits with no output ("pessimistic no-opinion") on any uncertainty, deferring to the normal permission flow. The here-string `<<< "$input"` is used instead of `echo "$input" | ...` to safely pass JSON with embedded quotes. Decision log `d0004` documents that the *original* matcher attempt was `Bash(.*/invoke-llm/scripts/invoke\.py.*)`, which never fired because Claude Code's hook matcher tests only the bare tool name; the fix flattened matcher to `"Bash"` and did the path filter inline. The validator hard-codes `prompt-engineer` in the bash `case` pattern.

## Hook output contract

### JSON-only stdout, no stderr-human parallel

Allow path emits `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "permissionDecisionReason": "Plugin skill script invocation"}}` on stdout. Non-matches emit empty stdout, exit 0. No stderr noise. Deny decisions are never emitted.

## Hook failure posture

### Silent fail-open (`exit 0` always, retry every hook)

Per-helper `try/except` around `Path.resolve(strict=True)` calls. Malformed JSON stdin and path-resolve failures (`OSError`, `ValueError`) silently return. Missing env vars raise `RuntimeError`, exiting non-zero — propagated by `main()`. From the user's perspective, a bug in the validator means the user is asked normally rather than blocked.

## Testing

### Python unittest under pytest discovery

Tests use Python `unittest` (module-level classes), executed via `pytest` runner. Tests located in `tests/` at repo root, mirroring `plugin/` structure — `plugin/scripts/allow-skill-scripts.py` → `tests/scripts/test_allow_skill_scripts.py`; `plugin/lib/llm.py` → `tests/lib/test_llm.py`. Subdirs: `tests/lib/`, `tests/scripts/`, `tests/skills/invoke_llm/`, `tests/skills/token_counter/` (skills dirs use underscore in tests but hyphen in plugin path; tests use `importlib.util.spec_from_file_location` to load hyphen-named modules per the explicit convention in `worklog/spec/infra/s0004-testing.md`). No `pytest.ini`, no `[tool.pytest.ini_options]` in `pyproject.toml`, no `setup.cfg`. `pyrightconfig.json` exists for type checking only. Test invocation: `python -m pytest tests/ -v`. `.claude/settings.json` allow-lists `Bash(python -m pytest *)`. Tests use stdlib `unittest.mock`; runtime deps suffice. `tests/lib/test_llm.py` pre-registers `lib.apikey` into `sys.modules` manually before loading the module under test, so tests work outside the plugin venv. The testing spec mandates "tests must be written **without reading the implementation** — only the function signatures and docstrings".

## CI workflow shape

### No CI

No `.github/workflows/` directory exists (`.github` contents return 404). Nothing verifies the version-bump → tag → install-pathway integration; failures show up on user `SessionStart` only.

## Marketplace validation

### No validation

No validation workflow. Nothing checks that SKILL.md or agent YAML frontmatter is well-formed or contains required fields. Nothing checks `hooks.json` shape. The repo relies on pyright (`pyrightconfig.json` → `pythonVersion: "3.14"`, `extraPaths: ["plugin"]`, `include: ["plugin", "tests"]`) for Python type checking, but this runs only in the developer's editor.

## Release automation

### No release automation / manual

Releases are bare git tags on main — no `gh release create`, no GitHub Releases entries (confirmed `releases` API returns `[]`). Manual `git tag vX.Y.Z && git push --tags`. The `installed-version` stamp matches `plugin.json.version`, not the tag, so as long as `plugin.json` is correct the install works regardless of tag-name discipline.

## Documentation surface

### Stub README only

`README.md` at repo root is 162 bytes, consisting of four markdown headings (`# Prompt Engineer`, `## Token Counter`, `## LLM Invocation`, `### Q&A Mode`, `## Prompt Playground`) and a `> [!CAUTION]` admonition reading "This repository is currently in active development." No content under any heading. No install/usage instructions. The `plugin/` directory has no README; `plugin/skills/<name>/` has no README — each SKILL.md serves as the skill's docs. No `CHANGELOG.md`. No `architecture.md`.

### Internal developer log as primary architecture doc

`worklog/` is a first-class, numerically-keyed spec/decision/task ledger. Structure: `worklog/archive/task/t0001..t0011-<slug>.md` (11 archived completed tasks), `worklog/decision/d0001..d0004-<slug>.md` (4 ADRs), `worklog/spec/<category>/s0001..s0010-<slug>.md` (10 specs split by category — infra / lib / skill / top-level). Decision docs use TOML-fence frontmatter with `id`, `title`, `relates_to`, `supersedes` keys (`d0004` supersedes `d0003` with explicit tracking). Tasks move from spec → task → archived-task lifecycle.

## License declaration

### Single repo-level license

LICENSE at repo root, MIT (1089 bytes); SPDX `MIT` declared in `plugin.json`.

## Community health files

### Community health files absent

No `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE/`. No badges or status indicators in README.

## Cross-role tools

### Python (stdlib + pip + uv)

Python stdlib + pip; no `uv`. `requires-python = ">=3.11"`. Stdlib `venv` creates the venv; pip installs the plugin and its declared deps.

### `${CLAUDE_PLUGIN_ROOT}` env var

Used to locate the plugin source — `ensure-deps.py` reads `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` for the canonical version; the SessionStart hook command is `python "${CLAUDE_PLUGIN_ROOT}/scripts/ensure-deps.py"`.

### `${CLAUDE_PLUGIN_DATA}`

Used as the venv install location (`${CLAUDE_PLUGIN_DATA}/venv`) and the version-stamp location (`${CLAUDE_PLUGIN_DATA}/installed-version`). The PreToolUse `allow-skill-scripts.py` validates that the python executable in a Bash command is inside `${CLAUDE_PLUGIN_DATA}/venv` before auto-approving.

### `plugin.json.version`

Doubles as user-facing semver and install-staleness signal — the field is both displayed to users and read by `ensure-deps.py` to decide whether the cached venv is current. A no-op bump (e.g., README-only fix) triggers a full `pip install --upgrade`.
</content>
</invoke>