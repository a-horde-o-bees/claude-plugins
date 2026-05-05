# Sample

Mirrors of `https://github.com/Emasoft/token-reporter-plugin`. A per-operation token usage reporter for Claude Code 2.1.108+ that emits hook-driven reports showing token counts, cost estimates, tool/skill/agent attribution, cache invalidation detection, worktree sub-agent breakdown, compact_boundary markers, CLAUDE.md reload events, and file activity at agent completion. Single-plugin source repo (default branch `main`, MIT licensed, version `1.10.3` at sample capture, last commit `2026-04-15` `d79e67d`). Marketplace listing lives in the sibling repo `Emasoft/emasoft-plugins`.

## Marketplace manifest layout

### No marketplace manifest (plugin source repo only)

The repo carries only `.claude-plugin/plugin.json`; no `marketplace.json` exists in the tree. Marketplace listing lives in the separate `Emasoft/emasoft-plugins` aggregator repo. The `notify-marketplace.yml` workflow fires a `plugin-updated` repository_dispatch event on `Emasoft/emasoft-plugins` when `.claude-plugin/plugin.json` changes on main, authenticated by a PAT secret. Per-plugin discoverability fields on `plugin.json` consist of 13 `keywords` (`tokens`, `usage`, `cost`, `reporter`, `hooks`, `debug`, `cache`, `attribution`, `monitoring`, `compaction`, `instructions-loaded`, `skills`, `agents`); no `category`, no `tags`. `$schema` is absent on `plugin.json`.

## Plugin source binding

### `source: github` with explicit coords or `ref` pinning

Source binding is determined by the external `Emasoft/emasoft-plugins` aggregator repo, not by this repo. From this repo's perspective `.claude-plugin/plugin.json` sits at `./.claude-plugin/plugin.json`; the aggregator's marketplace.json points at this repo by `github` source or equivalent. Plugin name is `token-reporter` while the repo is `token-reporter-plugin`; README warns users to install as `token-reporter@emasoft-plugins`.

## Source layout

### Single tree (plugin equals repo)

Plugin root and repo root coincide. The single tree carries `.claude-plugin/plugin.json`, `bin/token-report.py`, `hooks/hooks.json`, `scripts/token-reporter.py` (~2400 LOC), `scripts/publish.py`, `scripts/pre-push`, `pyproject.toml`, `CHANGELOG.md`, `README.md`, `LICENSE`, and `.github/workflows/notify-marketplace.yml`. No `tests/` or `tests_dev/` directory in the git tree.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

`plugin.json` declares 13 keywords (`tokens`, `usage`, `cost`, `reporter`, `hooks`, `debug`, `cache`, `attribution`, `monitoring`, `compaction`, `instructions-loaded`, `skills`, `agents`) with no `category` or `tags`.

### `$schema` absence on per-plugin manifests

`.claude-plugin/plugin.json` carries no `$schema` field.

## Version coordination

### Dual-file version (manifest pair)

`.claude-plugin/plugin.json` and `pyproject.toml` both carry `version = "1.10.3"`. `scripts/publish.py` step 8 atomically updates both, with CPV (`claude-plugins-validation`) re-validation as the post-bump gate. A third sync point exists with the `Emasoft/emasoft-plugins` marketplace repo, propagated via `notify-marketplace.yml` repository_dispatch on plugin.json changes.

### Atomic-bump release script with pre-push gate

`scripts/publish.py` orchestrates the version bump (via `git-cliff --bumped-version` from conventional commits by default, or explicit `--patch/--minor/--major/--set X.Y.Z`), commits "chore(release): vX.Y.Z", tags annotated, pushes via `git push --follow-tags`, and creates a GitHub release. `scripts/pre-push` gates pushes to main by walking the process tree (`ps -p <pid> -o args=` per ancestor PID) and rejecting unless `scripts/publish.py` is an ancestor process. Feature-branch pushes only run lint/syntax/manifest checks via the same hook.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

A single linear tag sequence `v1.0.0 ... v1.10.3` on main with no channel split. Consumers pin via `@ref` on the marketplace entry in the aggregator repo if desired. The aggregator side could layer a stable/latest split on top, but no channel-pinning artifact exists in this repo.

## Tag and release lifecycle

### Tag-on-main, single branch

Tags `v1.0.0` through `v1.10.3` all on main; tag `v1.10.3` matches main HEAD (`d79e67d`). No release branches. No pre-release suffixes. No dev-counter scheme — versions jump directly between real semver on main.

## Plugin-component registration

### Default convention discovery

`plugin.json` declares metadata + `userConfig` only — no `hooks`, `commands`, `agents`, or `mcpServers` fields. Hooks are discovered via the conventional path `hooks/hooks.json`.

### Hooks-json with broad event coverage

`hooks/hooks.json` registers the same command (`uv run --with tiktoken python3 ${CLAUDE_PLUGIN_ROOT}/scripts/token-reporter.py`) against 9 events: Stop, StopFailure, SubagentStop, TeammateIdle, TaskCompleted, InstructionsLoaded, PostCompact, TaskCreated, PermissionDenied. The script dispatches on the hook event name read from stdin JSON. README notes older Claude Code versions silently ignore hook registrations for unsupported events, so registering events not yet supported degrades gracefully.

## Bin entry mechanism

### Python `bin/` script with uv injection

`bin/token-report.py` carries `#!/usr/bin/env python3` and uses `uv run --with tiktoken <sys.executable> <script> --on-demand` internally to inject the tiktoken dep at invocation time. Plugin-root resolution via `_resolve_plugin_root()` returns `os.environ["CLAUDE_PLUGIN_ROOT"]` if set, else `Path(__file__).resolve().parent.parent` (the file lives in `<plugin_root>/bin/`). Cross-platform via `subprocess.run` (chosen over `os.execvp` because the latter is POSIX-only and raises `AttributeError` on Windows — comment in source). Permissions are `100755`. Module docstring declares "v2.1.91+ plugins can ship executables in bin/ which are added to the Bash tool's PATH while the plugin is enabled." A repeat `--on-demand` safeguard (`if "--on-demand" not in user_args: user_args = ["--on-demand", *user_args]`) prevents passing the flag twice. Catches `OSError` from subprocess to surface a clean "uv is not on PATH" message.

### Version-floor declared only in prose

The `v2.1.91+` floor for the bin/ feature is declared in three documentation layers: the `bin/token-report.py` module docstring, a `README.md` section header ("On-demand report (v2.1.91+ bin/ helper)"), and the `README.md` prerequisites listing per-feature Claude Code version floors (2.1.69+, 2.1.78+, 2.1.85+, 2.1.90+, 2.1.91+, 2.1.101+, 2.1.108+). `plugin.json` has no `requires`/`engines`/`claudeCode` field — version floor is documentation-only. The plugin relies on Claude Code's silent-ignore behavior for unsupported hook event names as a graceful-degradation substitute for declared floors.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

`bin/token-report.py` resolves the plugin root via `os.environ["CLAUDE_PLUGIN_ROOT"]` if set, else `Path(__file__).resolve().parent.parent`. The fallback enables raw-clone development without invoking through Claude Code.

## Dependency installation

### Ad-hoc per-invocation fetch via `uv run --with`

`pyproject.toml` lists `dependencies = ["tiktoken"]`; no `requirements.txt`. The hook command is `uv run --with tiktoken python3 ${CLAUDE_PLUGIN_ROOT}/scripts/token-reporter.py` — each invocation uses uv's global cache (~3s first run, ~3ms subsequent per README). No SessionStart install hook, no `${CLAUDE_PLUGIN_DATA}` venv. The `bin/token-report.py` wrapper uses the same `uv run --with tiktoken` pattern internally. The main `scripts/token-reporter.py` script has a classical `#!/usr/bin/env python3` shebang (not PEP 723 `env -S uv run --script`); the `--with` flag on the hook command is what injects the dep. Plugin hard-requires `uv` on PATH; README documents this prerequisite and gives the curl installer. README also documents tiktoken-missing fallback: script falls back to `chars/4` estimate and writes a warning to stderr; hook still exits 0.

## User configuration and authentication

### Native `userConfig` with `${user_config.KEY}` substitution

`plugin.json` declares 3 fields under `userConfig`: `OUTPUT_LIMIT_CHARS`, `SKILLS_BOX`, `MAX_ENTRIES_PER_SECTION`. Each entry has `type` (`number` / `boolean`), `title`, `default`, and a detailed `description`. The description for `OUTPUT_LIMIT_CHARS` links to `https://code.claude.com/docs/en/hooks` to explain why default is 10000. None of the three fields are secrets, so `sensitive: true` does not apply. `hooks/hooks.json` does not surface `${user_config.KEY}` substitution — the hook command is a static `uv run` invocation; the script reads the userConfig-populated env vars internally.

### Env-var fallback alongside userConfig

README documents `TOKEN_REPORTER_OUTPUT_LIMIT_CHARS`, `TOKEN_REPORTER_SKILLS_BOX`, `TOKEN_REPORTER_MAX_ENTRIES_PER_SECTION` as "alternative for older Claude Code versions that lack `userConfig` support." The script reads both userConfig-populated env vars and these plain-env fallbacks internally. Resilience layer against the host-side `userConfig` feature being unavailable.

## Session context loading

### No session-context loading

No `SessionStart` hook in `hooks/hooks.json`. No `UserPromptSubmit` for context. Reports are emitted at agent completion only; no session-context ambition.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse hooks. No PostToolUse hooks. `PermissionDenied` is registered as one of the 9 events but is treated as a lightweight event-logger ("permission-denial count surfaces as a red row in the report" per README), not an enforcement gate. The plugin is strictly observational — it does not enforce or gate any tool use.

## Hook output contract

### `systemMessage` for human-readable summaries

Stdout JSON for report-emitting hooks (Stop, StopFailure, SubagentStop, TeammateIdle, TaskCompleted) writes `{"systemMessage": "..."}`.

### Inline-truncated + full-HTML dual output

When a report exceeds Claude Code's 10,000-char hook output cap, the inline output is truncated with `⋯ +N more — see HTML report` indicators while a full HTML file is always written to `<project>/reports/token-reporter/<timestamp>-<event>-<session>.html`. README documents the cross-plugin convention that all of this author's plugins save under `<project>/reports/<plugin-name>/`.

## Hook failure posture

### Fail-open with always-exit-0

The hook exits 0 even when tiktoken is unavailable (falls back to chars/4 estimate with stderr warning). The "debug-gate" design is also fail-open: if no `claude --debug` ancestor process is detected via process-tree walk, the hook exits immediately with no output. README's failure-posture descriptions (retry loop with exponential backoff for transcript flush, fallback for missing tiktoken) imply defensive error handling at the top level. Stderr is used for debug logs prefixed `[token-reporter]`.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. The plugin has no live-monitor surface.

## Plugin-to-plugin coordination

### `dependencies` field absent

`plugin.json` does not include a `dependencies` key. Tags are plain `vX.Y.Z` (no plugin-name prefix) — single-plugin repo.

## Testing

### Tests referenced but absent in tree

`scripts/publish.py` gate 6 expects `tests_dev/` to exist and references "every test in tests_dev/ passes (0 failures)" in its docstring, but no `tests/` or `tests_dev/` directory is in the git tree. Either listed in `.gitignore` and lives only locally, or the gate is currently dormant. `pyproject.toml` configures ruff + mypy; no pytest config block.

## CI workflow shape

### Minimal cloud CI

One workflow only: `.github/workflows/notify-marketplace.yml`. Triggers on `workflow_dispatch` plus `push: branches: [main], paths: ['.claude-plugin/plugin.json']`. CI parses plugin.json name via inline `python3` heredoc, then `peter-evans/repository-dispatch@28959ce8df70de7be546dd1250a005dd32156697 # v4.0.1` fires `plugin-updated` event on `Emasoft/emasoft-plugins`. No matrix. No pytest, no linting, no manifest validation in cloud CI. `actions/checkout@v4` is tag-pinned (inconsistent with the SHA-pinned `repository-dispatch` action). No caching. Local `scripts/publish.py` gates 3-7 cover lint, type-check, and tests pre-push and at release time only.

## Pre-commit and pre-push hooks (git)

### Process-ancestry-verified pre-push gate

`.githooks/pre-push` symlinks to `scripts/pre-push`. The hook walks the process tree via `ps -p <pid> -o args=` per ancestor PID and rejects pushes to main unless `scripts/publish.py` is an ancestor process (absolute path match, with CWD-qualified relative-path fallback). The script's rationale comment contrasts this to env-var / marker-file schemes ("trivially spoofable"). Feature-branch pushes only run lint + syntax + JSON-parse validation. Users either run `git config core.hooksPath .githooks` or manually `ln -sf ../../scripts/pre-push .git/hooks/pre-push` (README documents the latter).

## Marketplace validation

### External validator referenced by name

CPV (`claude-plugins-validation`) is invoked twice in `scripts/publish.py` (gate 7 pre-bump and gate 9 post-bump re-validation), but the validator is not vendored or fetched into this repo — it's referenced by name only in `publish.py` docstring + README. Implementation is external. A network failure on release day blocks the release because gates fetch CPV remotely. Pre-push hook step 3 also runs `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"` as a JSON-parse-only gate. No frontmatter validation (no skills/commands with frontmatter in this plugin). No hooks.json validation as a separate gate (CPV is the presumed superset). Marketplace validation is entirely local — a contributor's PR branch gets only the feature-branch pre-push gates (lint + syntax + JSON parse), no CPV.

## Release automation

### Local-script release pipeline

No cloud release workflow. Releases are produced by `scripts/publish.py` running locally on the maintainer's machine, invoked manually as `uv run scripts/publish.py [--patch|--minor|--major|--set X.Y.Z|--dry-run]`. 15 mandatory gates: tool availability check, pre-push hook installed+executable, clean tree, ruff lint + format, mypy, py_compile, tests_dev, CPV validation, atomic version bump in plugin.json + pyproject.toml, CPV re-validation, git-cliff CHANGELOG regen, release commit ("chore(release): vX.Y.Z"), annotated tag, `git push --follow-tags` (invoking the pre-push ancestry gate), `gh release create` with notes extracted from CHANGELOG.md. Tag-format regex `^\d+\.\d+\.\d+$` enforced for `--set`. Working-tree-clean gate plus pre-push ancestry gate substitute for a separate verify-tag-on-main step. No draft releases — full GitHub release created. Release pipeline depends on local toolchain (uvx, git-cliff, gh CLI, uv) being correctly installed.

### CHANGELOG-parsing release action

`scripts/publish.py` step 14 extracts release notes from `CHANGELOG.md` via `extract_release_notes()` regex `^## \[{re.escape(version)}\][^\n]*\n?(.*?)(?=^## \[|\Z)` (MULTILINE | DOTALL), then passes to `gh release create`.

### Cross-repo notify on plugin.json change

`notify-marketplace.yml` is the only cloud workflow; it fires `repository_dispatch` event on `Emasoft/emasoft-plugins` when `.claude-plugin/plugin.json` changes on main, authenticated by a PAT secret. Keeps the marketplace-aggregator repo in sync without either repo having write access to the other beyond the PAT.

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

`README.md` at repo root (~15 KB). Covers report examples, prerequisites, installation variants, directory structure tree, per-hook table, userConfig table, debug-mode explanation, pricing table, color scheme, publish instructions. Single-plugin repo — README at repo root serves as the plugin README. No `architecture.md` at repo root — architectural narrative is embedded in README ("How it works", "Token attribution model", "Rate limit accounting", "Hook command" sections). No `CLAUDE.md`. No badges or status indicators.

### CHANGELOG with non-Keep-a-Changelog custom sections

`CHANGELOG.md` present, generated by `git-cliff`. Sections: Features / Bug Fixes / Documentation / Miscellaneous / Refactoring / Performance / Testing, grouped by `[X.Y.Z] - YYYY-MM-DD` headers.

## Community health files

### Bare minimum (LICENSE only)

`LICENSE` present (MIT, SPDX `MIT`). No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md`.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

LICENSE at repo root (MIT) plus SPDX `MIT` in manifests; single source of truth.
