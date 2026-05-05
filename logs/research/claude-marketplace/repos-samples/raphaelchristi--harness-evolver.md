# Sample

Mirrors of `https://github.com/raphaelchristi/harness-evolver`. Single-plugin marketplace for automated harness evolution — iteratively optimizes system prompts, routing, retrieval, and orchestration code using multi-agent proposers plus LangSmith experiments plus git worktrees.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root with one entry pointing at repo root (`"source": "./"`). The marketplace entry has its own `description`, `version`, `author`, `keywords`, `category` duplicating fields that also live in `plugin.json`.

### Top-level `metadata` wrapper variants

Has a `metadata.description` wrapper (`"LangSmith-native autonomous agent optimization plugin"`). No `metadata.version`, no `metadata.pluginRoot`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

Single entry uses `"source": "./"`. `strict` field absent (implicit `true`); no `skills` override.

## Per-plugin discoverability metadata

### Category + tags pair

`keywords: ["langsmith", "optimization", "evolution", "llm", "agent"]`; `category: "development"`. No `tags`.

### `$schema` absence on per-plugin manifests

No `$schema` on marketplace.json or plugin.json.

## Version coordination

### Three-way version split (marketplace vs npm vs git tags)

Three-way drift observed: `marketplace.json.plugins[0].version: 6.1.0`, `plugin.json.version: 6.4.2`, latest tag `v6.4.2` (2026-04-04), and HEAD has 14 commits past v6.4.2 (commit `87fa7612`, 2026-04-18) without bumping either file. The `/dev:release` skill bumps `package.json` and `.claude-plugin/plugin.json` only — never `.claude-plugin/marketplace.json`'s `plugins[0].version`. Over five patch / minor releases (6.1.0 → 6.4.2) the marketplace entry has never been touched. `/dev:validate` checks version sync between `package.json` and `plugin.json` but does not check the marketplace entry.

## Channel distribution

### Multi-channel via parallel distribution paths

Three distribution channels: Claude Code marketplace (effectively pins to HEAD of `main`); npm (`npx harness-evolver@latest` uses standard semver tags); direct GitHub install. No unified pinning story across channels — plugin and npm consumers can diverge at any commit between tags.

## Tag and release lifecycle

### Tag-on-main, single branch

Tags v5.3.0 through v6.4.2 all resolve to commits on `main` (feature branches like `feat/plugin-marketplace`, `fix/eval-reliability` merged back before tagging). No release branches; trunk-based with feature-branch development merging into main. No pre-release suffixes across 15 most recent tags. Between latest tag (`v6.4.2`, 2026-04-04) and HEAD (2026-04-18) sits a substantive feature merge (`feat/autogenesis-rspl` — "RSPL-lite resources, contract extraction, archive retrieval, regime-aware lenses") with no version bump.

### Skill-driven release

Release lifecycle is driven by a project-local in-editor skill (`/dev:release`, under `.claude/skills/dev-release/`) the author runs interactively, rather than a workflow or pre-commit hook. Skill bumps version files, creates the annotated tag, runs `gh release create`, runs `npm publish`. No CI verification of tag placement.

## Plugin-component registration

### Default convention discovery

`plugin.json` carries only metadata (`name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`). Component directories (`skills/`, `agents/`, `hooks/`) are discovered by convention.

## Component composition

### Skills (universal)

6 plugin-shipped skills: `setup`, `evolve`, `health`, `status`, `deploy`, `certify`. Three additional dev-skills under `.claude/skills/` (`dev-dry-run`, `dev-release`, `dev-validate`) are project-local, not plugin-shipped.

### Agents

6 agents: `harness-architect`, `harness-consolidator`, `harness-critic`, `harness-evaluator`, `harness-proposer`, `harness-testgen`.

### Hooks

`hooks/hooks.json` plus `hooks/session-start.sh`.

### bin

`bin/install.js` is the npm installer (invoked via `npx harness-evolver@latest`), not a plugin-bin; not referenced from `plugin.json`.

## Distribution exclusion and dogfood layout

### Repo-local developer skills exposed as plugin skills

Three dev-skills under `.claude/skills/` (`dev-dry-run`, `dev-release`, `dev-validate`) are project-local — used by the author with `/dev:release` and `/dev:validate` workflows — and live alongside the plugin-shipped `skills/` directory. Not part of the plugin distribution but visible in the repo tree.

## Skill authoring conventions

### `allowed-tools` as YAML array

Skill `allowed-tools` lists are YAML array form: `allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion]`. Includes `Agent` (legacy name for the Task tool used to launch subagents). Consistent across skills.

## Agent declaration conventions

### Standard fields plus model / color

Agent frontmatter uses `name`, `description`, `tools`, `color`, plus selectively `permissionMode` and `model`. `harness-architect`: `tools: Read, Write, Bash, Grep, Glob`, `color: blue`, `model: opus`. `harness-consolidator`: `tools: Read, Bash, Glob, Grep`, `color: cyan`, multi-line `description`. `harness-testgen`: `tools: Read, Write, Bash, Glob, Grep`, `color: cyan`. `harness-critic`: standard fields; model / color not retrieved verbatim.

### `permissionMode: acceptEdits` + worktree isolation

`harness-proposer` declares `tools: Read, Write, Edit, Bash, Glob, Grep`, `color: green`, `permissionMode: acceptEdits`. The proposer agent runs with pre-granted edit authority inside a git worktree the skill creates for it. Safety comes from the worktree boundary plus human review at `/harness:deploy`, not from tool-use hooks or permission gates.

### Plain tool-name list

`tools: Read, Write, Edit, Bash, Glob, Grep` — comma-separated scalar string; no permission-rule syntax (no `Bash(uv run *)` shapes).

## Cross-ecosystem distribution

### Cross-ecosystem multi-harness distribution

`bin/install.js` detects and installs into any subset of four agent runtimes (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.windsurf`) via interactive prompt. Same repo supports two distribution models with two filesystem layouts: plugin mode uses `${CLAUDE_PLUGIN_DATA}`, npx mode uses `~/.evolver`. Skills handle the split with runtime fallback (`$EVOLVER_TOOLS` / `$EVOLVER_PY` env vars, with `${VAR:-fallback}` resolving to `$HOME/.evolver` if plugin envs absent).

### Dual-distribution: marketplace + npm

Distributed both via Claude Code marketplace (`/plugin marketplace add raphaelchristi/harness-evolver-marketplace`) and via npm (`npx harness-evolver@latest`).

## Bin entry mechanism

### Node CLI launcher with `env node` shebang

`bin/install.js` is a Node CLI (~470 lines, zero runtime dependencies) with `#!/usr/bin/env node` shebang. Used only as the npm `bin` entry consumed by `npx harness-evolver@latest`; not consumed at runtime by skills. Copies skills / agents / tools into runtime directories (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.windsurf`), installs Python deps, interactively configures the LangSmith API key, and optionally wires up Context7 and LangChain Docs MCP servers via `claude mcp add`. Plugin's runtime commands invoke Python tools directly via `$EVOLVER_PY` — no wrapper layer.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Skills resolve `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` first, then fall back to `$HOME/.evolver` when running outside the plugin system (the npx bootstrap path). Skills explicitly resolve `EVOLVER_TOOLS` and `EVOLVER_PY` via `${VAR:-fallback}` expressions checking `$HOME/.evolver` if the plugin-provided env is absent.

## Dependency installation

### Python uv preferred, pip fallback

Python deps install into a per-user venv on SessionStart. Prefers `uv` for venv / install, falls back to stdlib `venv` plus `pip`. Tools also install a global `langsmith-cli` via `uv tool install` or `pip`. Dep list hard-coded in `hooks/session-start.sh` and `bin/install.js` (just `langsmith` plus `langsmith-cli`); no `requirements.txt`, `pyproject.toml`, or `package.json`-style Python manifest inside the plugin. `playground/requirements.txt` exists but applies to example agents, not plugin internals. `langsmith` installed with no version pin (`--upgrade langsmith`).

### Per-user venv with project-mode + npx-mode forks

Plugin mode installs to `${CLAUDE_PLUGIN_DATA}/venv`; npx mode installs to `~/.evolver/venv`. Tools copied to `~/.evolver/tools/` by `bin/install.js`, read from `${CLAUDE_PLUGIN_ROOT}/tools` when plugin path is set. Skills handle the split via runtime fallback. Users installing both ways can end up with two venvs and two tool copies, with skill invocations non-deterministic about which one runs.

## Install change detection

### Existence-only check

Step 1: `[ ! -f "$VENV_PY" ]` — venv (re)created only if missing. Step 2: `"$VENV_PY" -c "import langsmith" 2>/dev/null` — only installs if import fails. Step 3: `command -v langsmith-cli`. No manifest diff, no sha256, no version file stamp, no mtime, no `diff -q`. Importability check succeeds for any installed `langsmith`, regardless of version — no declared floor anywhere (no `requirements.txt`, no `pyproject.toml` pin, no version string in the script). If a future feature requires `langsmith>=0.3.5`, the hook never notices a 0.2.0 install is below the floor. `bin/install.js` uses `--upgrade langsmith` (does upgrade) but only fires on explicit `npx` re-run; the SessionStart hook never upgrades an existing install.

## Install trigger and lifecycle

### SessionStart direct invocation

`hooks/hooks.json` invokes `session-start.sh` via `bash "$CLAUDE_PLUGIN_ROOT/hooks/session-start.sh"`. No `matcher` key, so the hook fires on all SessionStart sub-events (startup, clear, compact). Idempotent on the happy path (venv exists → skip all install steps); unmatched firing pattern is benign but wasteful on `clear` / `compact`.

## Install failure posture

### Silent fail-through

`set -euo pipefail` opens the script, but every install invocation ends with `>/dev/null 2>&1`, and step 3 ends with `|| true` — failures are muted. No JSON `systemMessage`, no `continue: false`, no `stopReason`, no stderr message to the user. Half-built venv with a broken Python binary is not repaired (`[ ! -f "$VENV_PY" ]` is false). If `langsmith` fails to install, dependent skills surface the failure downstream via `ImportError`, not the hook. No `rm` on failure: if `uv venv` succeeds but `uv pip install langsmith` fails, the venv remains on disk; next session step 1 is skipped, step 2 re-checks `import langsmith` and retries the install — recovery works for the import piece because change-detection is import-based.

## User configuration and authentication

### Vendor-CLI credential file

`LANGSMITH_API_KEY` is stored in `langsmith-cli`'s credentials file (`~/.config/langsmith-cli/credentials` on Linux, `~/Library/Application Support/langsmith-cli/credentials` on macOS), not `userConfig`, not `.env`, not a plugin-specific config. SessionStart hook reads the credentials file and exports the key into `$CLAUDE_ENV_FILE` for downstream skills / tools. Skills explicitly warn "**Never pass `LANGSMITH_API_KEY` inline.** Tools resolve it automatically via [credentials file]". No `${user_config.KEY}` substitution. Plugin-ui surface bypassed entirely; users configure via `langsmith-cli auth` or hand-edit a credentials file.

### External config file owned by plugin

Project-level config lives in `.evolver.json` in the user's project (written by `/harness:setup`); skills read it and pass to tools via `--config` flags. Project configuration, not user configuration.

### No userConfig, env-var only

No `userConfig` declared in `plugin.json`.

## Session context loading

### Dependency install only (no context emission)

SessionStart hook is for dep install only. Does not emit `hookSpecificOutput.additionalContext`. Writes env vars to `$CLAUDE_ENV_FILE` (which Claude Code picks up — `EVOLVER_TOOLS`, `EVOLVER_PY`) but no prompt-context additions.

## SessionStart matcher scope

### Empty matcher (all sub-events)

`hooks.json` has no `matcher` key on the SessionStart entry; hook fires on all SessionStart sub-events.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks. The proposer agent (`permissionMode: acceptEdits`) modifies code freely in its worktree with no tool-use intercept. Safety relies entirely on git-worktree isolation plus post-hoc human review at `/harness:deploy`. The single SessionStart hook is fail-open.

## Hook handler runtime

### Bash scripts at conventional path

`hooks/session-start.sh` is a bash script invoked via `bash "$CLAUDE_PLUGIN_ROOT/hooks/session-start.sh"`. Shebang `#!/usr/bin/env bash`. Python tools use `#!/usr/bin/env python3`.

## Cross-hook environment plumbing

### `$CLAUDE_ENV_FILE` append for cross-hook env vars

SessionStart hook builds the venv, installs deps, then writes env-var exports (`EVOLVER_TOOLS`, `EVOLVER_PY`) into `$CLAUDE_ENV_FILE`. Skills and tools consume those vars.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field in `plugin.json`.

### External-MCP install during bootstrap

`bin/install.js` (npm installer path) detects and optionally auto-installs two external MCP servers (Context7, LangChain Docs) via `claude mcp add` at first-run. Dependency relationship managed outside the plugin manifest; not visible to `/plugin marketplace` tooling. Only runs via the npx path, not the plugin-install path.

## Live monitoring

### `monitors.json` absent

No `monitors.json`.

## Testing

### pytest with sys.path manipulation

pytest with a bare `__main__` fallback that lets the test file also run as `python3 tests/test_tools.py`. `tests/test_tools.py` at repo root. No `pytest.ini`, no `[tool.pytest.ini_options]` (repo has no `pyproject.toml`), no `setup.cfg`; tests rely on pytest auto-discovery. Test file imports `json`, `os`, `subprocess`, `sys`, `tempfile` — stdlib-only. Tool integration tests do `--help`-shape smoke checks; don't require `langsmith` installed.

### Smoke-only Python import + subcommand exercise

Test file does `--help`-shape smoke checks against tools.

## CI workflow shape

### No CI

`.github/` contains only `ISSUE_TEMPLATE/` (`bug_report.md`, `feature_request.md`). No `workflows/` directory. Test quality gated entirely by `/dev:validate` (in-editor skill the author runs manually) and the release workflow's assumption that the author ran validation.

## Marketplace validation

### In-editor skill (no CI)

`/dev:validate` is an in-editor skill (`.claude/skills/dev-validate/SKILL.md`). Not in CI, not a pre-commit hook, not `claude plugin validate`. Manual — author runs `/dev:validate` before `/dev:release`. Covers frontmatter (skill `name`, `description`, `allowed-tools`; agent `name`, `description`, `tools`, `color`), version sync between `package.json` and `plugin.json`, Python AST for tool files, executable bit on hook script, JSON validity of `hooks.json`, cross-references between skill `subagent_type:` declarations and agent files. Does NOT check `marketplace.json` version or the marketplace-entry schema — the most visible drift in the repo (6.1.0 vs 6.4.2) is not caught.

## Release automation

### Local-script release pipeline

`/dev:release` is a project-local skill (`.claude/skills/dev-release/`) that bumps versions in `package.json` and `.claude-plugin/plugin.json`, generates a `CHANGELOG.md` entry from conventional-commit-prefixed commits (`feat:`, `fix:`, `refactor:`), creates an annotated `v{version}` tag, runs `gh release create` (non-draft, auto-populated notes), and runs `npm publish`. Releases are created interactively in-editor by running the skill. No tag-sanity gates: no verify-tag-on-main, no tag-format regex, no tag-conflict detection. Does not bump `.claude-plugin/marketplace.json`'s `plugins[0].version` (source of the 6.1.0-vs-6.4.2 drift). `/dev:validate` is sibling but not auto-invoked.

### CHANGELOG-parsing release action

`/dev:release` skill parses conventional-commit prefixes (`feat:`, `fix:`, `refactor:`) from `git log` output and inserts them into `CHANGELOG.md` under a new dated section.

## Documentation surface

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` at repo root (~7.6KB: install flows for plugin and npx, quick-start, LangSmith prerequisite, multi-runtime support across Claude Code, Cursor, Codex, Windsurf). `docs/ARCHITECTURE.md` at repo root (capitalized; describes four-layer architecture — plugin / skills / agents / tools — but does not document versioning, channels, or multi-runtime install internals). `CLAUDE.md` at repo root (~13.9KB: operational procedures for agents working in the plugin, including the `/dev:release` plus `/dev:validate` workflow expectation). `CHANGELOG.md` (~47.9KB) follows Keep a Changelog 1.1.0 plus SemVer with dated entries per tagged release, categorized as `Added` / `Fixed` / `Changed`.

### Keep-a-Changelog with root-cause prose

`CHANGELOG.md` ~47.9KB, Keep a Changelog 1.1.0 format with SemVer and `Added` / `Fixed` / `Changed` categories.

### Shipped planning corpus visible in public repo

`docs/superpowers/plans/` and `docs/superpowers/specs/` contain in-progress design docs (4 specs, 11 plans, dated 2026-04-02 / 2026-04-03). Internal planning material that ships in the repo but is excluded from the npm package via `.npmignore`. No clear `design/` vs `docs/` boundary; consumers browsing the repo encounter the `superpowers/` subtree without explicit signaling that those are internal vs user-facing.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

LICENSE present (MIT); SPDX `MIT` declared in manifests.

## Community health files

### LICENSE + CODE_OF_CONDUCT + issue templates

`CODE_OF_CONDUCT.md` (5.2KB). Issue templates: `bug_report.md`, `feature_request.md` under `.github/ISSUE_TEMPLATE/`. No `SECURITY.md`, no `CONTRIBUTING.md`. Banner image (`banner.jpg`) in assets but no build-status badges confirmed in README.

## Source layout

### Single tree (plugin equals repo)

Single tree: plugin equals repo, `source: "./"` in marketplace.json.

## Project-convention sidecar files

### `.worktreeinclude`

`.worktreeinclude` at repo root lists files the harness should copy into its evolution worktrees (`.evolver.json`, `.env`, `evolution_archive/`). Plugin reads this list when setting up proposer worktrees. Neither a Claude Code convention nor a standard Git feature; plugin-specific mechanism encoded as a file type.

## Cross-role tools

### Python (stdlib + pip + uv)

Python tools install via `uv` (preferred) or `pip` fallback into a per-user venv. `langsmith-cli` installed via `uv tool install` or `pip`.

### Node + npm + npx

`bin/install.js` is a zero-dependency Node CLI consumed via `npx harness-evolver@latest`.

### `${CLAUDE_PLUGIN_ROOT}` env var

Skills and tools resolve `${CLAUDE_PLUGIN_ROOT}` first, fall back to `$HOME/.evolver`.

### `${CLAUDE_PLUGIN_DATA}`

Plugin-mode venv lives at `${CLAUDE_PLUGIN_DATA}/venv`.

### `$CLAUDE_ENV_FILE`

SessionStart hook writes `EVOLVER_TOOLS` and `EVOLVER_PY` exports into `$CLAUDE_ENV_FILE` for cross-hook consumption.
