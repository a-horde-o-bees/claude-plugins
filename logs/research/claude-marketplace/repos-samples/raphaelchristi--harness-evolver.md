# raphaelchristi/harness-evolver

## Identification

- **URL**: https://github.com/raphaelchristi/harness-evolver
- **Stars**: 12
- **Last commit date**: 2026-04-18 (87fa7612 `Merge pull request #25 from raphaelchristi/feat/autogenesis-rspl`)
- **Default branch**: main
- **License**: MIT (SPDX `MIT`)
- **Sample origin**: dep-management (Python venv bootstrap via SessionStart hook)
- **One-line purpose**: Automated harness evolution for AI agents — iteratively optimizes system prompts, routing, retrieval, and orchestration code using multi-agent proposers + LangSmith experiments + git worktrees.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root, single-plugin marketplace pointing at repo root (`"source": "./"`).
- **Marketplace-level metadata**: `metadata.description` wrapper only (`"LangSmith-native autonomous agent optimization plugin"`). No `metadata.version`, no `metadata.pluginRoot`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: `keywords` + `category`. `keywords: ["langsmith", "optimization", "evolution", "llm", "agent"]`; `category: "development"`. No `tags`.
- **`$schema`**: absent.
- **Reserved-name collision**: no.
- **Pitfalls observed**: the marketplace entry has its own `description`, `version`, `author`, `keywords`, `category` duplicating fields that also live in `plugin.json`. This is the root cause of the drift described in purpose 2 — the marketplace entry is an independently-authored record rather than a projection of `plugin.json`.

## 2. Plugin source binding

- **Source format(s) observed**: `relative` (single entry `"source": "./"`).
- **`strict` field**: default (implicit true) — no `strict` key present.
- **`skills` override on marketplace entry**: absent.
- **Version authority**: **both, with drift**. `plugin.json` is at `6.4.2`; `marketplace.json`'s `plugins[0].version` is at `6.1.0`. Latest tag is `v6.4.2` (2026-04-04); main has landed unversioned work on top (commit `87fa7612`, 2026-04-18) without bumping either file. Users installing via `/plugin marketplace add raphaelchristi/harness-evolver-marketplace` see version 6.1.0 in the marketplace listing while the plugin they get is 6.4.2.
- **Pitfalls observed**: marketplace-entry version is not updated by the `/dev:release` workflow. The skill description says it bumps both `package.json` and `.claude-plugin/plugin.json` — it does not mention `marketplace.json`. Over five patch/minor releases (6.1.0 → 6.4.2) the marketplace entry has never been touched. `/dev:validate` checks version sync between `package.json` and `plugin.json` but does not check the marketplace entry.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via `@ref` only if installing by npx (`npx harness-evolver@latest`) or via GitHub tag. The plugin installation pathway (marketplace) has no channel concept.
- **Channel-pinning artifacts**: absent. No `stable-tools` / `latest-tools`, no dev-counter, no `release/*` branch.
- **Pitfalls observed**: mix of distribution channels — Claude Code marketplace, npm (`npx harness-evolver@latest`), and direct GitHub install — with no unified pinning story. The npm channel uses standard semver tags; the marketplace channel effectively pins to HEAD of `main` (subject to marketplace refresh), so plugin consumers and npm consumers can diverge at any commit between tags.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: on main (tags v5.3.0 through v6.4.2 all resolve to commits on main; feature branches like `feat/plugin-marketplace`, `fix/eval-reliability` are merged back before tagging).
- **Release branching**: none. Feature-branch development (`feat/*`, `fix/*`) merging into main, tag on main.
- **Pre-release suffixes**: none observed across 15 most recent tags.
- **Dev-counter scheme**: absent.
- **Pre-commit version bump**: no.
- **Pitfalls observed**: between the latest tag (`v6.4.2`, 2026-04-04) and `HEAD` (2026-04-18) sits a substantive feature merge (`feat/autogenesis-rspl` — "RSPL-lite resources, contract extraction, archive retrieval, regime-aware lenses") with no version bump. Marketplace consumers installing today get this untagged work under the label "6.4.2" from `plugin.json` and "6.1.0" from the marketplace entry — neither accurate.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` contains only metadata (`name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`). Component directories (`skills/`, `agents/`, `hooks/`, etc.) are discovered by convention.
- **Components observed**:
  - skills: yes (6 — `setup`, `evolve`, `health`, `status`, `deploy`, `certify`; also three dev-skills under `.claude/skills/` — `dev-dry-run`, `dev-release`, `dev-validate` — but those are project-local, not plugin-shipped)
  - commands: no
  - agents: yes (6 — `harness-architect`, `harness-consolidator`, `harness-critic`, `harness-evaluator`, `harness-proposer`, `harness-testgen`)
  - hooks: yes (`hooks/hooks.json` + `hooks/session-start.sh`)
  - .mcp.json: no (MCP configured opportunistically via `claude mcp add` in the npx installer, not shipped by the plugin)
  - .lsp.json: no
  - monitors: no
  - bin: yes — but `bin/install.js` is the npm installer (invoked via `npx`), not a plugin-bin; not referenced from `plugin.json`
  - output-styles: no
- **Agent frontmatter fields used**: `name`, `description`, `tools`, `color`, plus (selectively) `permissionMode`, `model`.
  - `harness-proposer`: `tools: Read, Write, Edit, Bash, Glob, Grep`, `color: green`, `permissionMode: acceptEdits`.
  - `harness-evaluator`: standard fields; no `model`, no `permissionMode` (inferred from summary).
  - `harness-architect`: `tools: Read, Write, Bash, Grep, Glob`, `color: blue`, `model: opus`.
  - `harness-consolidator`: `tools: Read, Bash, Glob, Grep`, `color: cyan`, multi-line `description`.
  - `harness-testgen`: `tools: Read, Write, Bash, Glob, Grep`, `color: cyan`.
  - `harness-critic`: standard fields; model/color not retrieved verbatim.
- **Agent tools syntax**: plain tool names (comma-separated scalar string: `Read, Write, Edit, Bash, Glob, Grep`). No permission-rule syntax like `Bash(uv run *)`.
- **Pitfalls observed**: `permissionMode: acceptEdits` on `harness-proposer` is an unusual escalation — the agent is granted pre-approved edits, with safety delegated to the git-worktree isolation that the proposer is instructed to set up. Skill `allowed-tools` lists include `Agent`, which is the legacy name for the Task tool used to launch subagents; the array-literal YAML form (`allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion]`) is consistent across skills.

## 6. Dependency installation

- **Applicable**: yes. Python deps (`langsmith`) install into a per-user venv on SessionStart; additionally a global tool (`langsmith-cli`) installs via `uv tool install` or `pip`.
- **Dep manifest format**: none for the plugin itself — there is no `requirements.txt`, `pyproject.toml`, or `package.json`-style Python manifest inside the plugin. The list of deps is hard-coded in `hooks/session-start.sh` and `bin/install.js` (just `langsmith` + `langsmith-cli`). `playground/requirements.txt` exists but applies to example agents, not plugin internals.
- **Install location**: `${CLAUDE_PLUGIN_DATA}/venv` when run as plugin; `~/.evolver/venv` fallback when run standalone (`npx`). Tools copied to `~/.evolver/tools/` (by `bin/install.js`) but read from `${CLAUDE_PLUGIN_ROOT}/tools` when the plugin path is set.
- **Install script location**: `hooks/session-start.sh` (plugin mode) + `bin/install.js` (npm mode).
- **Change detection**: **existence only**. Step 1 checks `[ ! -f "$VENV_PY" ]` — venv is (re)created only if missing. Step 2 runs `"$VENV_PY" -c "import langsmith" 2>/dev/null` and only installs if the import fails. Step 3 checks `command -v langsmith-cli`. No manifest diff, no sha256, no version file stamp, no mtime, no `diff -q`.
- **Retry-next-session invariant**: no `rm` on failure. If `uv venv` succeeds but `uv pip install langsmith` fails, the venv remains on disk with `langsmith` still missing; next session, `[ ! -f "$VENV_PY" ]` is false (venv exists) so step 1 is skipped; step 2 re-checks `import langsmith` and retries the install. Recovery works because the change-detection is import-based, not venv-presence-based — but only for the Python-import piece; a half-built venv with a broken Python binary would not be repaired.
- **Failure signaling**: silent. The script opens with `set -euo pipefail` but every install invocation ends with `>/dev/null 2>&1`, and step 3 ends with `|| true`, muting any failure. No JSON `systemMessage`, no `continue: false`, no `stopReason`, no stderr message to the user. If `langsmith` fails to install, the skills that depend on it surface the failure downstream via `ImportError`, not the hook.
- **Runtime variant**: Python — prefers `uv` for venv/install, falls back to stdlib `venv` + `pip`. Node-side (`bin/install.js`) is used only for the `npx` installation path; the plugin itself carries no Node runtime.
- **Alternative approaches**: none observed. No PEP 723 inline metadata, no pointer file, no `uvx` ephemeral invocation; each Python tool is run directly with the venv's `python3`.
- **Version-mismatch handling**: none. `langsmith` is installed with no version pin (`--upgrade langsmith`); the hook neither pins a version nor tracks Python-minor changes. If the user's system Python upgrades from 3.11 to 3.12, the existing venv (built against 3.11) continues to exist but its `bin/python` symlink may break; the hook's existence check (`[ ! -f "$VENV_PY" ]`) will miss a stale-venv case and skip rebuild.
- **Pitfalls observed**: **existence-only detection misses upgrades**. `"$VENV_PY" -c "import langsmith"` succeeds for any installed `langsmith`, regardless of version. If the plugin later starts depending on `langsmith>=0.3.5` (e.g., a new SDK method is required), the hook will never notice that the existing 0.2.0 install is below the floor. There is no declared floor anywhere — no `requirements.txt`, no `pyproject.toml` pin, not even a version string in the script. Upgrades happen only on a fresh-install flow (missing venv), which is the exact flow the change-detection is designed to skip. The `bin/install.js` path uses `--upgrade langsmith`, which does upgrade, but only fires on explicit `npx` re-run; the SessionStart hook never upgrades an existing install.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no for plugin-shipped bins. `bin/install.js` is the npm `bin` entry used by `npx harness-evolver@latest` to bootstrap the install, not a plugin CLI wrapper consumed at runtime by skills. The plugin's runtime commands are Python tools invoked by `$EVOLVER_PY` directly — no wrapper layer.
- **`bin/` files**: `bin/install.js` — Node CLI that copies skills/agents/tools into runtime directories (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.windsurf`), installs Python deps, interactively configures LangSmith API key, and optionally wires up Context7 and LangChain Docs MCP servers via `claude mcp add`. ~470 lines, zero runtime dependencies.
- **Shebang convention**: `#!/usr/bin/env node` on `install.js`; `#!/usr/bin/env bash` on `hooks/session-start.sh`; `#!/usr/bin/env python3` on Python tools.
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` + `${CLAUDE_PLUGIN_DATA}` with fallback to `$HOME/.evolver` when running outside the plugin system (the npx bootstrap path). Skills explicitly resolve `EVOLVER_TOOLS` and `EVOLVER_PY` via `${VAR:-fallback}` expressions that check `$HOME/.evolver` if the plugin-provided env is absent.
- **Venv handling (Python)**: direct `exec` of `$VENV_PY` (no `source activate`). Skills invoke `"$EVOLVER_PY" tool.py --args`.
- **Platform support**: POSIX (macOS + Linux). The npx installer special-cases Darwin for the `langsmith-cli` credentials file path (`$HOME/Library/Application Support/langsmith-cli` vs. `$HOME/.config/langsmith-cli`), but otherwise assumes bash + a writeable home dir. No Windows support observed.
- **Permissions**: `install.js` and `session-start.sh` ship as regular files; `hooks.json` invokes `session-start.sh` via `bash "$CLAUDE_PLUGIN_ROOT/hooks/session-start.sh"`, sidestepping the executable-bit requirement. `install.js` relies on npm to set its bit during install.
- **SessionStart relationship**: hook builds the venv + installs deps, then writes env-var exports (`EVOLVER_TOOLS`, `EVOLVER_PY`) into `$CLAUDE_ENV_FILE`. Skills and tools consume those vars. The hook does *not* write a pointer file for bin wrappers (there are no bin wrappers to point at).
- **Pitfalls observed**: dual install paths (marketplace plugin + npx installer) that target different filesystem layouts — plugin mode uses `$CLAUDE_PLUGIN_DATA`, npx mode uses `~/.evolver`. Skills handle the split with runtime fallback (`$HOME/.evolver/venv/bin/python` if `$EVOLVER_PY` unset), but a user who installs both ways can end up with two venvs and two tool copies, with skill invocations non-deterministic about which one runs.

## 8. User configuration

- **`userConfig` present**: no (not in `plugin.json`).
- **Field count**: none in the plugin manifest. Project-level config lives in `.evolver.json` in the user's project (written by `/harness:setup`), which the skills read and pass to tools via `--config` flags. This is project configuration, not Claude-Code `userConfig`.
- **`sensitive: true` usage**: not applicable. The `LANGSMITH_API_KEY` secret is managed out-of-band — loaded from `langsmith-cli`'s credentials file (`~/.config/langsmith-cli/credentials` or `~/Library/Application Support/langsmith-cli/credentials`) and exported into `$CLAUDE_ENV_FILE` by the SessionStart hook. The key is never surfaced to `userConfig`.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable. Skills explicitly warn "**Never pass `LANGSMITH_API_KEY` inline.** Tools resolve it automatically via [credentials file]". No `${user_config.KEY}` substitution.
- **Pitfalls observed**: the plugin sidesteps the Claude-Code `userConfig` surface entirely, routing its secret through an external CLI tool's credential store. This is idiomatic for plugins that wrap a vendor CLI (the vendor already solves credential management), but it means users cannot configure the plugin through the plugin-ui surface Claude Code provides — they must run `langsmith-cli auth` or hand-edit a credentials file.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable (no PreToolUse / PostToolUse hooks).
- **Failure posture**: not applicable for PreToolUse / PostToolUse. The only hook (SessionStart) is fail-open — every failure is `>/dev/null 2>&1`-silenced and the `|| true` pattern explicitly ignores errors.
- **Top-level try/catch wrapping**: not applicable.
- **Pitfalls observed**: zero enforcement — the proposer agent (`permissionMode: acceptEdits`) modifies code freely in its worktree with no tool-use intercept. Safety relies entirely on git-worktree isolation + post-hoc human review at `/harness:deploy`. No hook denies a suspicious `rm -rf` or `curl | sh`, though the worktree sandbox limits blast radius.

## 10. Session context loading

- **SessionStart used for context**: only for dep install — the hook does not emit `hookSpecificOutput.additionalContext`. It writes env vars to `$CLAUDE_ENV_FILE` (which Claude Code picks up), but no prompt-context additions.
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: no.
- **SessionStart matcher**: none declared — `hooks.json` has no `matcher` key, so the hook fires on all SessionStart sub-events (startup, clear, compact). Given the hook is idempotent on the happy path (venv exists → skip all install steps), the unmatched firing pattern is benign but wasteful on `clear` / `compact`.
- **Pitfalls observed**: running the full venv-check + `command -v` + `import` sequence on every `/clear` and `/compact` adds several hundred ms of startup latency to those operations. A `matcher: "startup"` restriction would be more efficient.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no in `plugin.json`.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace).
- **Pitfalls observed**: the npx installer (`bin/install.js`) detects and optionally auto-installs two external MCP servers (Context7, LangChain Docs) via `claude mcp add`. This is a dependency relationship that is managed outside the plugin manifest — not declared in `plugin.json`'s (absent) `dependencies` field, not visible to `/plugin marketplace` tooling, and only runs via the npx path, not the plugin install path.

## 13. Testing and CI

- **Test framework**: pytest (with a bare-`__main__` fallback that lets the file also run as `python3 tests/test_tools.py`).
- **Tests location**: `tests/test_tools.py` at repo root.
- **Pytest config location**: none — no `pytest.ini`, no `[tool.pytest.ini_options]` in `pyproject.toml` (repo has no `pyproject.toml`), no `setup.cfg`. Tests rely on pytest auto-discovery.
- **Python dep manifest for tests**: none for tests themselves. The test file imports `json`, `os`, `subprocess`, `sys`, `tempfile` — stdlib-only. Tool integration tests do `--help`-shape smoke checks, so they don't require `langsmith` to be installed.
- **CI present**: **no**. `.github/` contains only `ISSUE_TEMPLATE/` (`bug_report.md` + `feature_request.md`). No `workflows/` directory exists.
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: direct `python3 -m pytest tests/test_tools.py -v` or `python3 tests/test_tools.py` (documented in the test file's docstring).
- **Pitfalls observed**: no CI at all. Test quality is gated entirely by `/dev:validate` (an in-editor skill the author runs manually) and the release workflow's assumption that the author ran validation. A PR-time check would catch frontmatter regressions, version-sync drift between `package.json` and `plugin.json`, and Python syntax breakage in `tools/*.py` that the test file's smoke checks cover — none of which fire automatically today.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable as workflow; releases are created interactively by running `/dev:release` in-editor.
- **Automation shape**: skill-driven — the `/dev:release` skill (project-local, under `.claude/skills/dev-release/`) bumps versions in `package.json` and `.claude-plugin/plugin.json`, generates a `CHANGELOG.md` entry from conventional-commit-prefixed commits (`feat:`, `fix:`, `refactor:`), creates an annotated `v{version}` tag, runs `gh release create` (non-draft, auto-populated notes), and runs `npm publish`.
- **Tag-sanity gates**: none enforced by the release tooling. `/dev:validate` is a sibling skill that *should* be run first (per `CLAUDE.md`: "Always run `/dev:validate` before release"), but `/dev:release` does not invoke it automatically. No verify-tag-on-main, no tag-format regex, no tag-conflict detection.
- **Release creation mechanism**: `gh release create` from inside the skill's Bash step.
- **Draft releases**: no — non-draft.
- **CHANGELOG parsing**: yes — the skill parses conventional-commit prefixes from `git log` output and inserts them into `CHANGELOG.md` under a new dated section.
- **Pitfalls observed**: the release skill bumps `package.json` and `.claude-plugin/plugin.json` but does not bump `.claude-plugin/marketplace.json`'s `plugins[0].version`. This is the source of the 6.1.0-vs-6.4.2 drift reported in purpose 2. Additionally, no tag-sanity gate means a release can be tagged off a branch (including detached HEAD); in practice all recent tags are on main, but that's convention, not enforcement. `/dev:validate`'s version-sync check also doesn't look at the marketplace entry — so validation passes even when the marketplace entry is stale.

## 15. Marketplace validation

- **Validation workflow present**: no in CI. `/dev:validate` is an in-editor skill that covers similar ground (frontmatter, version sync between `package.json` and `plugin.json`, Python AST for tool files, executable bit on the hook script, JSON validity of `hooks.json`, cross-references between skill `subagent_type:` declarations and agent files).
- **Validator**: in-editor skill (`.claude/skills/dev-validate/SKILL.md`). Not a CI check, not a pre-commit hook, not `claude plugin validate`.
- **Trigger**: manual — the author runs `/dev:validate` before `/dev:release`.
- **Frontmatter validation**: yes — skill frontmatter (`name`, `description`, `allowed-tools`) and agent frontmatter (`name`, `description`, `tools`, `color`) are checked.
- **Hooks.json validation**: yes (JSON syntax + `session-start.sh` executable).
- **Pitfalls observed**: validation is human-triggered and in-editor, so a contributor without the `/dev:validate` skill or who forgets to run it can merge a broken frontmatter, a version drift, or a Python syntax error without signal. `marketplace.json`'s version is not in the check set, so the most visible drift in the repo is specifically *not* caught.

## 16. Documentation

- **`README.md` at repo root**: present, 7.6KB — covers install flows (plugin + npx), quick-start, LangSmith prerequisite, multi-runtime support (Claude Code, Cursor, Codex, Windsurf).
- **`README.md` per plugin**: not applicable (single-plugin repo; the repo-root README serves the plugin).
- **`CHANGELOG.md`**: present, 47.9KB — follows Keep a Changelog 1.1.0 + SemVer, dated entries per tagged release, categorized as `Added` / `Fixed` / `Changed`.
- **`architecture.md`**: present as `docs/ARCHITECTURE.md` at repo root (capitalized; not per-plugin since there's only one plugin). Describes the four-layer architecture (plugin / skills / agents / tools) but does not document versioning, channels, or multi-runtime install internals.
- **`CLAUDE.md`**: present at repo root, 13.9KB — operational procedures for agents working in the plugin, including the `/dev:release` + `/dev:validate` workflow expectation.
- **Community health files**: `CODE_OF_CONDUCT.md` (5.2KB, present). No `SECURITY.md`, no `CONTRIBUTING.md`. Issue templates present (`bug_report.md`, `feature_request.md`).
- **LICENSE**: present (MIT).
- **Badges / status indicators**: not confirmed in this research (README opening was summarized, not fetched verbatim in full). The assets directory contains a `banner.jpg`, suggesting visual branding but not build-status badges.
- **Pitfalls observed**: `docs/superpowers/plans/` and `docs/superpowers/specs/` contain substantial in-progress design docs (4 specs, 11 plans, all dated 2026-04-02 / 2026-04-03) — internal planning material that ships in the repo but is excluded from the npm package via `.npmignore`. No separate `design/` vs `docs/` boundary; consumers browsing the repo may find the superpowers subtree confusing without context on which docs are user-facing (README, ARCHITECTURE, FEATURES) vs. internal (superpowers).

## 17. Novel axes

- **Multi-runtime installer**. `bin/install.js` detects and installs into any subset of four agent runtimes (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.windsurf`), with an interactive prompt letting the user target one, several, or all. The plugin ships as a Claude Code plugin but is distributed as a multi-runtime skill bundle when installed via npm — a pattern not seen elsewhere in the marketplace sample. This means the same repo supports two distribution models with two filesystem layouts, and skills must cope with both at runtime (via `$EVOLVER_TOOLS` / `$EVOLVER_PY` fallbacks).
- **External CLI as secret-management boundary**. `LANGSMITH_API_KEY` is stored in `langsmith-cli`'s credentials file (not `userConfig`, not `.env` directly, not a plugin-specific config). The SessionStart hook reads that file and exports the key into `$CLAUDE_ENV_FILE`. This delegates credential lifecycle to a third-party CLI tool — a pattern that avoids duplicating secret management but creates a hard dependency on the vendor CLI's file-format stability.
- **Opportunistic MCP install during bootstrap**. The npm installer asks the user at first-run whether to install Context7 and LangChain Docs MCP servers via `claude mcp add` — MCP registration as a side-effect of plugin install, rather than as a declared plugin dependency. The plugin functions without these MCPs; they're an offered augmentation, not a requirement.
- **`acceptEdits` permissionMode + git-worktree isolation as the safety model**. The proposer agent runs with pre-granted edit authority inside a git worktree the skill creates for it. Safety comes from the worktree boundary + human review at `/harness:deploy`, not from tool-use hooks or permission gates. This is an explicit "trust the agent, sandbox the writes" design — worth flagging as a novel axis because it combines plugin-level `acceptEdits` with skill-orchestrated filesystem isolation.
- **Worktree-include declaration**. `.worktreeinclude` at repo root is a project convention (list of files the harness should copy into its evolution worktrees — `.evolver.json`, `.env`, `evolution_archive/`). The plugin reads this list when setting up proposer worktrees. This is neither a Claude Code convention nor a standard Git feature; it's a plugin-specific mechanism encoded as a file type.
- **Branch-dense, tag-sparse semver discipline**. 9 long-lived feature branches on the repo simultaneously (`feat/*`, `fix/*`) with tagging only after merges to main. Feature work accumulates on branches, tags mark stable merge points — a workflow shape that's common but not formalized by release branches.
- **Version-drift between marketplace.json, plugin.json, and HEAD**. Three-way drift observed: marketplace entry at 6.1.0, plugin.json at 6.4.2, HEAD one unreleased feature-merge beyond v6.4.2. Worth a dedicated pattern-doc line as a known failure mode when the release workflow only touches a subset of version-bearing files.
- **Zero-CI plugin**. Active project (41 commits in two weeks, 10+ tagged releases) with no CI. Validation is human-triggered via `/dev:validate` skill. Stands out against the sample of CI-heavy marketplace repos and demonstrates that in-editor validation skills can substitute for CI when the author is disciplined — at the cost of losing that signal for contributors.

## 18. Gaps

- **Did not verify whether the `6.1.0` in `marketplace.json` is intentional or an oversight.** Could be resolved by checking the git blame on `.claude-plugin/marketplace.json` — first commit that introduced it, and whether subsequent release commits touched it. `gh api repos/raphaelchristi/harness-evolver/commits?path=.claude-plugin/marketplace.json` would answer.
- **`harness-critic` agent frontmatter not retrieved verbatim** — WebFetch summarized it as a quality auditor but didn't return the YAML block. Cannot confirm whether it uses `model:` or `permissionMode:`. Resolvable with a direct raw fetch.
- **Did not confirm whether `install.js` version-check against `npm view harness-evolver version` would flag the marketplace drift** — it compares local `package.json` (6.4.2) against npm registry. Whether 6.4.2 has been published is unknown; `npm view harness-evolver versions` would resolve.
- **README badges** not verified verbatim — summary did not mention badges. Could be resolved with a raw fetch of just the opening 30 lines of `README.md`.
- **Whether `langsmith-cli` is a pypi package or something vendor-specific** — the installer runs `uv tool install langsmith-cli` or `pip install langsmith-cli` but I didn't verify it exists on PyPI or what its versioning policy is. `pip show langsmith-cli` on a fresh install would clarify.
- **How skills resolve the subagent names** — skills reference agents (e.g., `subagent_type: harness-proposer`) but I didn't fetch a skill body to confirm the exact reference syntax used by this plugin. The `/dev:validate` skill description mentions checking `subagent_type:` cross-references, so the convention is present; exact grammar not captured.
- **Whether the absence of `matcher` on the SessionStart hook causes observable delay** — claimed as a pitfall but not measured. Resolvable by running the hook locally with `time bash hooks/session-start.sh` against a pre-built venv.
- **`npx` publication cadence** — whether every tagged release is published to npm, or only some, is unverified. `npm view harness-evolver time --json` would give a publish-date timeline to compare against git tag dates.
