# Emasoft/token-reporter-plugin

## Identification

- **URL**: https://github.com/Emasoft/token-reporter-plugin
- **Stars**: 1
- **Last commit date**: 2026-04-15 (main @ `d79e67d`, "chore(release): v1.10.3")
- **Default branch**: main
- **License**: MIT
- **Sample origin**: bin-wrapper
- **One-line purpose**: "Per-operation token usage reporter for Claude Code 2.1.108+. Shows token counts, cost estimates, tool + skill + agent attribution, cache invalidation detection, worktree sub-agent breakdown, compact_boundary markers, CLAUDE.md reload events, and file activity when agents complete. Only outputs in debug mode (claude --debug)." (from plugin.json description; README opens with same framing)

## 1. Marketplace discoverability

- **Manifest layout**: not applicable — this is a single-plugin source repo; there is no `.claude-plugin/marketplace.json`. Marketplace listing lives in the sibling repo `Emasoft/emasoft-plugins` (referenced by README as the install source). Only `.claude-plugin/plugin.json` is present at repo root
- **Marketplace-level metadata**: not applicable (no marketplace.json here)
- **`metadata.pluginRoot`**: not applicable — no marketplace.json in this repo. `plugin.json` sits at `./.claude-plugin/plugin.json`, implying the marketplace entry in `emasoft-plugins` either uses `source.path = "."` or a git source pointing at repo root
- **Per-plugin discoverability**: observed in `plugin.json`: 13 `keywords` (`tokens`, `usage`, `cost`, `reporter`, `hooks`, `debug`, `cache`, `attribution`, `monitoring`, `compaction`, `instructions-loaded`, `skills`, `agents`); no `category`, no `tags`
- **`$schema`**: absent in `plugin.json`
- **Reserved-name collision**: no — plugin name is `token-reporter`
- **Pitfalls observed**: repo name (`token-reporter-plugin`) intentionally differs from plugin name (`token-reporter`); README warns users to always install as `token-reporter@emasoft-plugins`. Plugin-name-vs-repo-name drift is an inconsistency axis a marketplace aggregator has to track

## 2. Plugin source binding

- **Source format(s) observed**: not applicable from this repo's perspective — this repo is the plugin source, not a marketplace. How `emasoft-plugins/marketplace.json` references this plugin (github/git-subdir/other) is not determinable from within this repo
- **`strict` field**: not applicable (no marketplace.json here)
- **`skills` override on marketplace entry**: not applicable (no marketplace.json here); no `skills/` directory in this repo so no strict-false carving would apply
- **Version authority**: `.claude-plugin/plugin.json` carries `version: "1.10.3"` and `pyproject.toml` carries the same `version = "1.10.3"` — release pipeline (`scripts/publish.py` step 8) updates both "atomically" per its docstring. The marketplace entry in `emasoft-plugins` would be a third location, not inspected here
- **Pitfalls observed**: two sources of truth for version (plugin.json + pyproject.toml) mitigated by publish.py enforcing atomic bump and CPV post-bump re-validation; a third sync point with the marketplace repo exists (notify-marketplace.yml dispatches when `plugin.json` changes)

## 3. Channel distribution

- **Channel mechanism**: no split observed in this repo — a single linear tag sequence `v1.0.0 ... v1.10.3` on main. Consumers pin via `@ref` on the marketplace entry if desired (not controlled here)
- **Channel-pinning artifacts**: absent
- **Pitfalls observed**: none in this repo. Note the marketplace side (`emasoft-plugins`) could layer a stable/latest split on top, not visible from here

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main — tags `v1.0.0` through `v1.10.3` all on main (observed `v1.10.3` sha `d79e67d` matches `main` HEAD)
- **Release branching**: none — tag-on-main only
- **Pre-release suffixes**: none observed
- **Dev-counter scheme**: absent — versions jump directly between real semver on main (no `0.0.z` dev counter)
- **Pre-commit version bump**: no — version bump is release-time only. `scripts/publish.py` orchestrates the bump (via `git-cliff --bumped-version` from conventional commits by default, or explicit `--patch/--minor/--major/--set`), then commits "chore(release): vX.Y.Z", tags, pushes, and creates the GitHub release. A `scripts/pre-push` hook gates pushes to main by requiring `scripts/publish.py` to be an ancestor process (walks `ps -o args=` on each ancestor PID); feature-branch pushes only run lint/syntax/manifest checks
- **Pitfalls observed**: pre-push ancestry gate is stringent — it intentionally rejects env-var / marker-file spoofing, but it also means any main push not driven by publish.py is blocked. `.githooks/pre-push` is a symlink to `../scripts/pre-push` — user must either `git config core.hooksPath .githooks` or manually `ln -sf ../../scripts/pre-push .git/hooks/pre-push` (README documents the latter)

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` declares metadata + `userConfig` only; no `hooks`, `commands`, `agents`, or `mcpServers` fields. Hooks are discovered via the conventional path `hooks/hooks.json`
- **Components observed**: skills no, commands no, agents no, hooks yes (`hooks/hooks.json`, 9 events), `.mcp.json` no, `.lsp.json` no, monitors no, bin yes (`bin/token-report.py`), output-styles no
- **Agent frontmatter fields used**: not applicable — no agents
- **Agent tools syntax**: not applicable — no agents
- **Pitfalls observed**: `hooks/hooks.json` registers the same command against 9 events (Stop, StopFailure, SubagentStop, TeammateIdle, TaskCompleted, InstructionsLoaded, PostCompact, TaskCreated, PermissionDenied) — the script itself dispatches on the hook event name read from stdin JSON. README notes older Claude Code versions "silently ignore hook registrations for events they don't support," so registering unsupported events is tolerated

## 6. Dependency installation

- **Applicable**: yes — tiktoken is the one runtime dep
- **Dep manifest format**: `pyproject.toml` (project-level) lists `dependencies = ["tiktoken"]`; there is no `requirements.txt`
- **Install location**: ad-hoc runtime fetch via `uv run --with tiktoken` — no SessionStart install hook, no `${CLAUDE_PLUGIN_DATA}` venv. Each hook invocation uses uv's cache (README documents ~3s first run, ~3ms subsequent)
- **Install script location**: not applicable — no install script; inline in the hook command `uv run --with tiktoken python3 ${CLAUDE_PLUGIN_ROOT}/scripts/token-reporter.py`
- **Change detection**: not applicable — uv handles cache invalidation itself
- **Retry-next-session invariant**: not applicable — no persistent install state to clean
- **Failure signaling**: README documents tiktoken-missing fallback: script falls back to `chars/4` estimate and writes a warning to stderr; hook still exits 0 so it doesn't block the session
- **Runtime variant**: Python via `uv run --with <pkg>` — ad-hoc (no venv management owned by the plugin)
- **Alternative approaches**: `uv run --with <pkg>` pattern is the chosen alternative to PEP 723 inline script metadata or a SessionStart pip install. The main script has a classical `#!/usr/bin/env python3` shebang (not PEP 723 `env -S uv run --script`); the `--with` flag on the hook command is what injects the dep
- **Version-mismatch handling**: none — uv resolves tiktoken per-invocation
- **Pitfalls observed**: plugin hard-requires `uv` on PATH; README calls this out as a prerequisite and gives the curl installer. No graceful detection if uv is missing — the hook command just fails to invoke

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — `bin/token-report.py` is the bin-wrapper sample
- **`bin/` files**:
    - `bin/token-report.py` — on-demand token report CLI; wraps `scripts/token-reporter.py --on-demand` via uv. Docstring explicitly declares: "v2.1.91+ plugins can ship executables in bin/ which are added to the Bash tool's PATH while the plugin is enabled."
- **Shebang convention**: `#!/usr/bin/env python3` (plain CPython shebang; `uv run` is invoked inside the script body, not via PEP 723 script metadata)
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` env var with script-relative fallback — `_resolve_plugin_root()` returns `os.environ["CLAUDE_PLUGIN_ROOT"]` if set, else `Path(__file__).resolve().parent.parent` (file lives in `<plugin_root>/bin/`)
- **Venv handling (Python)**: `uv run --with tiktoken <sys.executable> <script> --on-demand` — ephemeral uv-managed dep injection per invocation; no pre-created venv. `sys.executable` is forwarded so the child inherits the wrapper's Python interpreter
- **Platform support**: cross-platform Python — docstring and README both call out macOS / Linux / Windows. Uses `subprocess.run` (explicitly chosen over `os.execvp` because the latter is POSIX-only and raises AttributeError on Windows — comment in source)
- **Permissions**: 100755 (executable) on `bin/token-report.py` (confirmed from git tree mode)
- **SessionStart relationship**: static — no SessionStart hook in this plugin; bin is a pre-committed executable, not populated or pointed-to by a hook
- **Pitfalls observed**: README calls out a CPV (claude-plugins-validation) rule that flagged extensionless executables and `.sh` files as platform-specific, motivating the `.py` choice. On Windows the `.py` extension must be associated with Python for PATH-invocation to work; the README doesn't document this constraint. Also: when the user asks Claude Code to `Please run: token-report.py`, the bin is invoked by name — the script handles a repeat `--on-demand` safeguard (`if "--on-demand" not in user_args: user_args = ["--on-demand", *user_args]`) so passing the flag twice is prevented, and catches `OSError` from subprocess to surface a clean "uv is not on PATH" message

### Version-requirement declaration (repo-specific)

The `v2.1.91+` floor for the bin/ feature is declared in three places, none of which is a machine-readable field:

1. `bin/token-report.py` module docstring — "v2.1.91+ plugins can ship executables in bin/ which are added to the Bash tool's PATH while the plugin is enabled." (prose, inline at top of wrapper)
2. `README.md` section header — "On-demand report (v2.1.91+ bin/ helper)"
3. `README.md` prerequisites — version floors for each hook event are enumerated in prose ("PostCompact/TaskCreated/PermissionDenied require 2.1.90+", "InstructionsLoaded / `agent_id` / `agent_type` hook input fields require 2.1.101+", etc.), and the plugin.json description says "Claude Code 2.1.108+"

There is no `requires.claude-code` or equivalent field in `plugin.json` — version floor is documentation-only. The Claude Code binary silently ignores unrecognized hook event names in older versions, so the plugin degrades gracefully by design rather than by enforcement.

## 8. User configuration

- **`userConfig` present**: yes
- **Field count**: 3 — `OUTPUT_LIMIT_CHARS`, `SKILLS_BOX`, `MAX_ENTRIES_PER_SECTION`
- **`sensitive: true` usage**: not applicable — none of the three fields are secrets (numeric caps + boolean toggle)
- **Schema richness**: typed — each entry has `type` (`number` / `boolean`), `title`, `default`, `description`. Descriptions are detailed, including a link to `https://code.claude.com/docs/en/hooks` explaining why `OUTPUT_LIMIT_CHARS` default is 10000
- **Reference in config substitution**: not observed in `hooks/hooks.json` — the hook command is a static `uv run` invocation. README documents env-var overrides (`TOKEN_REPORTER_OUTPUT_LIMIT_CHARS`, `TOKEN_REPORTER_SKILLS_BOX`, `TOKEN_REPORTER_MAX_ENTRIES_PER_SECTION`) as "alternative for older Claude Code versions that lack `userConfig` support" — the script reads both userConfig-populated env vars and these plain-env fallbacks internally (inferred from README wording; not verified by reading scripts/token-reporter.py)
- **Pitfalls observed**: `userConfig` description for `OUTPUT_LIMIT_CHARS` warns against raising the default — Claude Code itself hardcodes a 10,000 char cap on hook output and silently replaces overflow with an opaque stub. The plugin enforces its own cap so the inline box stays renderable; this is documented in both plugin.json and README

## 9. Tool-use enforcement

- **PreToolUse hooks**: none
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: observed — `PermissionDenied` is one of the 9 registered events, but it is treated as a lightweight event-logger, not an enforcement gate (per README: "Permission-denial count surfaces as a red row in the report")
- **Output convention**: stdout JSON for report-emitting hooks (Stop, StopFailure, SubagentStop, TeammateIdle, TaskCompleted write `{"systemMessage": "..."}`); stderr is used for debug logs prefixed `[token-reporter]`. README confirms this convention
- **Failure posture**: fail-open — the hook exits 0 even when tiktoken is unavailable (falls back to chars/4 estimate with stderr warning). The "debug-gate" design is also fail-open: if no `claude --debug` ancestor process is detected via process-tree walk, the hook exits immediately with no output
- **Top-level try/catch wrapping**: not verified (would require reading `scripts/token-reporter.py` at ~2400 LOC); README's failure-posture descriptions (retry loop with exponential backoff for transcript flush, fallback for missing tiktoken) imply defensive error handling at the top level
- **Pitfalls observed**: this plugin is strictly observational — it does not enforce or gate any tool use. The inclusion of `PermissionDenied` alongside enforcement-style events is misleading if read in isolation; it's used for counting, not for blocking

## 10. Session context loading

- **SessionStart used for context**: no — no `SessionStart` event in `hooks/hooks.json`
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no — output uses `systemMessage` per README ("script reads hook input from stdin (JSON) and writes `{"systemMessage": "..."}` to stdout")
- **SessionStart matcher**: not applicable — no SessionStart
- **Pitfalls observed**: none — the plugin has no session-context ambition. Reports are emitted at agent completion only

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable — no monitor feature. Note the plugin declares version floors for the bin/ feature in README + docstring (see §7), not via any machine-readable monitors/version field
- **Pitfalls observed**: none

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — `plugin.json` does not include a `dependencies` key
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin repo. Tags are plain `vX.Y.Z` (no plugin-name prefix)
- **Pitfalls observed**: none

## 13. Testing and CI

- **Test framework**: inferred from `publish.py` docstring reference "every test in tests_dev/ passes (0 failures)" — but `tests_dev/` is not present in the repo tree. Either it lives in `.gitignore` (not checked into git) or the gate is currently dormant. pyproject.toml configures ruff + mypy; no pytest config block in pyproject.toml
- **Tests location**: no `tests/` or `tests_dev/` directory observed in the git tree
- **Pytest config location**: not present
- **Python dep manifest for tests**: not applicable — no test dir
- **CI present**: yes — one workflow: `.github/workflows/notify-marketplace.yml`
- **CI file(s)**: `.github/workflows/notify-marketplace.yml` only (no test/lint/release workflow in `.github/workflows/`)
- **CI triggers**: `workflow_dispatch` + `push: branches: [main], paths: ['.claude-plugin/plugin.json']`
- **CI does**: parse plugin.json name via inline python3 heredoc, then `peter-evans/repository-dispatch` to fire `plugin-updated` event on `Emasoft/emasoft-plugins` marketplace repo; no pytest, no linting, no manifest validation
- **Matrix**: none
- **Action pinning**: SHA-pinned with version comment — `peter-evans/repository-dispatch@28959ce8df70de7be546dd1250a005dd32156697 # v4.0.1`; `actions/checkout@v4` (tag-pinned, inconsistent with the other action)
- **Caching**: none
- **Test runner invocation**: not applicable (no tests run in CI). Local publish.py gate 6 runs tests if `tests_dev/` exists
- **Pitfalls observed**: linting, type-checking, and test execution are **pre-push only** (via `scripts/pre-push` hook) and **release-time only** (via `scripts/publish.py` gates 3-7), never in cloud CI. GitHub Actions is used only for the marketplace-notify dispatch. A consumer forking this repo without installing the pre-push hook or running publish.py would have no quality gates at all

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — no cloud release workflow. Releases are produced by `scripts/publish.py` running locally on the maintainer's machine
- **Release trigger**: not applicable (no cloud trigger). `scripts/publish.py` is invoked manually: `uv run scripts/publish.py [--patch|--minor|--major|--set X.Y.Z|--dry-run]`
- **Automation shape**: local-script release pipeline — 15 mandatory gates in `scripts/publish.py`: tool availability check, pre-push hook installed+executable, clean tree, ruff lint + format, mypy, py_compile, tests_dev, CPV validation, atomic version bump in plugin.json + pyproject.toml, CPV re-validation, git-cliff CHANGELOG regen, release commit ("chore(release): vX.Y.Z"), annotated tag, `git push --follow-tags` (invoking the pre-push ancestry gate), `gh release create` with notes extracted from CHANGELOG.md
- **Tag-sanity gates**: verify-tag=package-version (implicit — bump step sets both plugin.json and pyproject.toml, verified by CPV re-validation step); tag-format regex enforced via semver validation in `bump_version()` and `compute_next_version()` (regex `^\d+\.\d+\.\d+$` for `--set`); verify-tag-on-main enforced by pre-push ancestry gate plus working-tree-clean gate; no separate verify-tag-on-main gate beyond these
- **Release creation mechanism**: `gh release create` (step 14 of publish.py). Release notes extracted from CHANGELOG.md via `extract_release_notes()` regex matching the `## [X.Y.Z] - YYYY-MM-DD` section until the next `## [` header or EOF
- **Draft releases**: no — full GitHub release created
- **CHANGELOG parsing**: yes — regex-based section extraction in publish.py (`^## \[{re.escape(version)}\][^\n]*\n?(.*?)(?=^## \[|\Z)`, MULTILINE | DOTALL)
- **Pitfalls observed**: entire release pipeline runs on maintainer's machine — no cloud audit trail, no matrix testing. The workflow is explicitly documented as "NO EXCEPTIONS. NO SKIPS." but depends on local toolchain (uvx, git-cliff, gh CLI, uv) being correctly installed. CPV ("claude-plugins-validation") is fetched remotely per gate 7 — a network failure on release day would block the release

## 15. Marketplace validation

- **Validation workflow present**: not applicable in cloud CI. Manifest validation happens at three local points:
    1. `scripts/pre-push` step 3: `python3 -c "import json; json.load(open('.claude-plugin/plugin.json'))"` (JSON parse only)
    2. `scripts/publish.py` gates 7 and 9: remote `cpv-validate` ("claude-plugins-validation"), inferred from comments — actual tool not examined
    3. `scripts/publish.py` gate 8: atomic bump step re-reads both plugin.json and pyproject.toml
- **Validator**: CPV (claude-plugins-validation) — external validator referenced by name only in publish.py docstring + README; implementation not in this repo
- **Trigger**: pre-push hook + manual publish.py invocation; never on push/PR in cloud
- **Frontmatter validation**: not applicable — no skills/commands with frontmatter in this plugin
- **Hooks.json validation**: not explicitly called out as a separate gate; CPV is the presumed superset validator
- **Pitfalls observed**: marketplace validation is entirely local and depends on the maintainer running publish.py. A contributor's PR branch gets only the feature-branch pre-push gates (lint + syntax + JSON parse) — no CPV on PR

## 16. Documentation

- **`README.md` at repo root**: present (~15 KB, comprehensive — report examples, prerequisites, installation variants, directory structure tree, per-hook table, userConfig table, debug-mode explanation, pricing table, color scheme, publish instructions)
- **`README.md` per plugin**: not applicable — single-plugin repo, README at repo root serves as the plugin README
- **`CHANGELOG.md`**: present — Keep a Changelog-like format, generated by git-cliff. Sections: Features / Bug Fixes / Documentation / Miscellaneous / Refactoring / Performance / Testing, grouped by `[X.Y.Z] - YYYY-MM-DD` headers
- **`architecture.md`**: absent — none at repo root. Architectural narrative is embedded in README ("How it works", "Token attribution model", "Rate limit accounting", "Hook command" sections)
- **`CLAUDE.md`**: absent
- **Community health files**: none — no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`
- **LICENSE**: present (MIT, SPDX `MIT`)
- **Badges / status indicators**: absent — no README badges
- **Pitfalls observed**: absence of architecture.md despite an active ~2400 LOC Python hook script means future maintainers must reconstruct the token-attribution model from README prose + source comments. README mitigates by enumerating the JSONL-field-level attribution rules explicitly

## 17. Novel axes

- **Process-ancestry-verified pre-push gate.** `scripts/pre-push` for pushes to main walks the process tree via `ps -p <pid> -o args=`, rejecting the push unless `scripts/publish.py` is an ancestor process (absolute path match, with CWD-qualified relative-path fallback). The rationale comment explicitly contrasts this to env-var / marker-file schemes ("trivially spoofable"). A process-ancestry gate enforces release-discipline without trusting any mutable signal the user could forge. Candidate for a release-discipline subsection alongside conventional tag-sanity gates
- **Bin-feature version floor declared in three documentation layers, zero machine-readable fields.** `bin/token-report.py`'s module docstring, the README section header, and the README prerequisites all enumerate per-feature Claude Code version floors (2.1.69+, 2.1.78+, 2.1.85+, 2.1.90+, 2.1.91+, 2.1.101+, 2.1.108+). `plugin.json` has no `requires`/`engines`/`claudeCode` field — the plugin relies on Claude Code's silent-ignore behavior for unsupported hook event names as a graceful-degradation substitute for declared floors. Candidate pattern to surface: "silent-ignore graceful degradation vs. machine-readable version floors"
- **Env-var backcompat for userConfig.** README documents a `TOKEN_REPORTER_<KEY>` env-var override pattern "for older Claude Code versions that lack `userConfig` support." The plugin reads both the userConfig-populated values (via whatever env-var Claude Code substitutes) and the plain-env fallback. This is an explicit resiliency layer against a host-side feature not being available — distinct from the normal `${user_config.KEY}` substitution pattern
- **`uv run --with <pkg>` per-invocation as alternative to SessionStart venv management.** The plugin elects not to own a venv at all — every hook fire invokes `uv run --with tiktoken python3 ...` which uses uv's global cache. First run ~3s, subsequent ~3ms per README. Side-steps the `${CLAUDE_PLUGIN_DATA}` venv pattern entirely. Candidate alternative to document alongside SessionStart install patterns
- **HTML-always + inline-truncated dual-output.** When a report exceeds Claude Code's 10,000-char hook output cap, inline is truncated with `⋯ +N more — see HTML report` indicators while a full HTML file is always written to `<project>/reports/token-reporter/<timestamp>-<event>-<session>.html`. README documents the convention that all of this author's plugins save under `<project>/reports/<plugin-name>/`. This is a cross-plugin convention, not a Claude Code platform feature
- **Marketplace-notify dispatch workflow.** The only cloud workflow in this repo is a webhook-style notifier (`notify-marketplace.yml`) that fires on changes to `.claude-plugin/plugin.json` and dispatches a `plugin-updated` event to `Emasoft/emasoft-plugins`. This keeps a separate marketplace-aggregator repo in sync without either repo having write access to the other beyond a single PAT secret. Candidate pattern: "marketplace-aggregator sync via repository_dispatch"
- **CPV (claude-plugins-validation) as an external third-party validator.** Referenced by name only — not vendored into this repo. Invoked twice in `scripts/publish.py` (pre-bump + post-bump re-validation). Novel in that the plugin author treats marketplace-schema validation as an external service rather than a local JSON-schema check

## 18. Gaps

- **Contents of `scripts/token-reporter.py` (~2400 LOC)** — not read in full due to WebFetch budget. Failure posture specifics (try/except boundaries, exit-code discipline on parser errors, how `--on-demand` differs from hook-invoked mode, env-var override precedence vs. userConfig) would need a direct read. Source: `https://raw.githubusercontent.com/Emasoft/token-reporter-plugin/main/scripts/token-reporter.py`
- **`tests_dev/` existence** — `scripts/publish.py` gate 6 claims "every test in tests_dev/ passes," but no such directory is in the git tree. Either (a) listed in `.gitignore` and lives only locally, or (b) the gate is currently dormant. Source: check `.gitignore` contents and `git log --all -- tests_dev/`
- **CPV (claude-plugins-validation) schema** — the validator is referenced by name in publish.py but never fetched or vendored. What fields it validates, whether it checks bin/ permissions, whether it enforces version-floor declarations, etc., are unknown. Source: whatever repo hosts the `cpv-validate` binary — not linked from this repo
- **Marketplace-side entry** — how `Emasoft/emasoft-plugins/marketplace.json` references this plugin (source format, strict setting, skills override, version authority) is not determinable from this repo. Source: fetch `https://raw.githubusercontent.com/Emasoft/emasoft-plugins/main/.claude-plugin/marketplace.json`
- **`scripts/bump_version.py`** — referenced in the README directory tree as "Semver bumper for plugin.json" but not opened here. Relationship to `scripts/publish.py`'s internal `bump_version()` (duplication vs. delegation) unknown. Source: `https://raw.githubusercontent.com/Emasoft/token-reporter-plugin/main/scripts/bump_version.py`
- **Rest of `scripts/publish.py` past line 200** — opened the first ~200 lines. Gates 7 (CPV), 10 (changelog regen), 11 (commit), 12 (tag), 13 (push), 14 (gh release create) implementation details not confirmed. Source: same URL, lines 200-end
