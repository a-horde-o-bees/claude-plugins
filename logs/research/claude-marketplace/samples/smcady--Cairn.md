# smcady/Cairn

## Identification

- **URL**: https://github.com/smcady/Cairn
- **Stars**: 3
- **Last commit date**: 2026-03-21 (fd9da2fe, "Async ingest + graph cache: eliminate per-turn rebuild")
- **Default branch**: main
- **License**: MIT (SPDX `MIT`, `LICENSE` present, 1067 bytes)
- **Sample origin**: dep-management
- **One-line purpose**: "Reasoning memory for AI agents. Tracks what was decided, contradicted, and left open across sessions." (plugin.json / marketplace entry); repo tagline is "Persistent reasoning graph for AI memory — tracks what was decided, not just what was said".

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (298 bytes), one plugin entry.
- **Marketplace-level metadata**: none — top-level keys are `name`, `owner`, `plugins` only. No `metadata` wrapper, no top-level `description`.
- **`metadata.pluginRoot`**: absent (no `metadata` object at all).
- **Per-plugin discoverability**: none — the single plugin entry has `name`, `description`, `version`, `source` only. No `category`, `tags`, or `keywords` on the marketplace entry. (plugin.json carries `keywords: ["memory","reasoning","agents","graph"]` but those are plugin-level, not marketplace-entry-level.)
- **`$schema`**: absent on both marketplace.json and plugin.json.
- **Reserved-name collision**: no (`cairn-marketplace` / `cairn`).
- **Pitfalls observed**: minimalist manifest — no category/tags means the plugin relies on description text for discoverability within a consuming marketplace. `owner` is `{"name": "Shawn Cady"}` with no `email` or `url`.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "."`) — single plugin at repo root.
- **`strict` field**: default (implicit true) — no `strict` key on the marketplace entry.
- **`skills` override on marketplace entry**: absent (no skills in this plugin at all — see purpose 5).
- **Version authority**: both — `marketplace.json` plugin entry and `plugin.json` both declare `"version": "0.1.0"`. Drift risk present; no mechanism (hook/script) observed that keeps them in sync.
- **Pitfalls observed**: duplicate version string in two manifests with no sync automation — hand-edit discipline required on every bump.

## 3. Channel distribution

- **Channel mechanism**: no split — single manifest, no stable/latest separation. Users pin via marketplace ref if they want a specific version.
- **Channel-pinning artifacts**: absent.
- **Pitfalls observed**: none — this is a single-plugin personal marketplace at 0.1.0 with no distribution ladder.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: none — `gh api /tags` returns an empty list.
- **Release branching**: none — only `main` branch exists.
- **Pre-release suffixes**: not applicable (no tags or releases).
- **Dev-counter scheme**: absent — plain `0.1.0` string, no auto-increment.
- **Pre-commit version bump**: no — no `.pre-commit-config.yaml`, no `.github/hooks`, no `.husky/`, nothing observed that would bump the version on commit.
- **Pitfalls observed**: zero releases and zero tags against a `0.1.0` version across a ~3-day burst of commits (2026-03-18 to 2026-03-21) — the plugin is pre-release and versioning is informal. Install via marketplace pulls `main` head.

## 5. Plugin-component registration

- **Reference style in plugin.json**: inline config object — `mcpServers` is inlined as `{"cairn": {"command": "bash", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/run-mcp.sh"]}}`. No `hooks` key in plugin.json (hooks are discovered from `hooks/hooks.json` by Claude Code's default discovery).
- **Components observed**:
  - skills: no
  - commands: no
  - agents: no
  - hooks: yes (`hooks/hooks.json`)
  - `.mcp.json`: no (MCP server declared inline in plugin.json; `.mcp.json.example` exists at repo root but is a user-installation template, not a plugin component)
  - `.lsp.json`: no
  - monitors: no
  - bin: no
  - output-styles: no
- **Agent frontmatter fields used**: not applicable (no agents).
- **Agent tools syntax**: not applicable.
- **Pitfalls observed**: the plugin's entire product surface is (a) one MCP server with 7 tools (`harness_status`, `harness_query`, `harness_ingest`, `harness_search`, `harness_orient`, `harness_trace`, `harness_debug`) and (b) two hook scripts. No skills, commands, or agents — unusual for a marketplace plugin.

## 6. Dependency installation

- **Applicable**: yes.
- **Dep manifest format**: `pyproject.toml` (hatchling build-backend, Python >=3.12; 9 runtime deps including `anthropic`, `mcp[cli]`, `networkx`, `pydantic`, `fastembed`, `numpy`, `pyyaml`, `python-dotenv`).
- **Install location**: `${CLAUDE_PLUGIN_DATA}/.venv` — venv created in plugin data dir, not plugin root.
- **Install script location**: `scripts/bootstrap.sh` (1309 bytes). Wired as the `SessionStart` hook command in `hooks/hooks.json`.
- **Change detection**: three-pronged OR. Reinstall fires if any of:
  1. Cached plugin-root path file (`${DATA_DIR}/.plugin_root`) is missing or its content differs from current `${CLAUDE_PLUGIN_ROOT}` (detects plugin directory move on update).
  2. `diff -q "${PLUGIN_ROOT}/pyproject.toml" "${DATA_DIR}/pyproject.toml"` returns non-zero (detects dependency manifest change).
  3. `${VENV_DIR}/bin/python` is not executable (detects missing/broken venv).
- **Retry-next-session invariant**: no `rm` on failure. `set -euo pipefail` halts the bootstrap if `python3 -m venv`, `pip install`, `cp`, or `echo >` fail — no cleanup, so a partially-created venv would remain and subsequent sessions would find `${VENV_DIR}/bin/python` present (skipping the existence trigger) but may still fail if the pip install was incomplete. The two content triggers (plugin-root file, cached pyproject) are only written *after* pip install, so on failure neither is updated — meaning the next session re-enters the install branch via the pyproject-differs check (since `CACHED_PYPROJECT` wasn't updated). This amounts to implicit retry without explicit `rm`.
- **Failure signaling**: `set -euo pipefail` halts on any failing command. Pip output is piped through `2>&1 | tail -5`, so on failure the user sees only the last 5 lines of combined stdout+stderr. Venv creation has a `2>/dev/null || python -m venv` fallback (tries `python3` first, falls back to `python`). No JSON `systemMessage`, no `continue: false`, no custom exit 2.
- **Runtime variant**: Python with `python3 -m venv` + `pip install`. No `uv`, no `uvx`, no PEP 723 inline metadata.
- **Alternative approaches**: none observed — the repo uses a single classical venv + pip install-from-path (`pip install "${PLUGIN_ROOT}"` pulls deps from `pyproject.toml` via hatchling).
- **Version-mismatch handling**: none explicit. The cached `.plugin_root` trigger handles plugin-directory moves (e.g., Claude Code plugin cache relocation on update), but Python minor version changes (3.12 → 3.13) are not tracked — the venv would silently keep the old interpreter.
- **Pitfalls observed**:
  - `CAIRN_VENV` is persisted to `CLAUDE_ENV_FILE` (`echo "export CAIRN_VENV=..." >> "${CLAUDE_ENV_FILE}"`) so the `Stop` and `UserPromptSubmit` hooks can find the venv Python. If `CLAUDE_ENV_FILE` is not set (some Claude Code versions may not populate it), the env var is silently not persisted — downstream hooks fail with the run-mcp.sh error message "Cairn not bootstrapped. Restart your Claude Code session."
  - Bootstrap always appends to `CLAUDE_ENV_FILE` on every session, even when no reinstall is needed — multiple `export CAIRN_VENV=...` lines accumulate across sessions if the env file is not truncated by the harness between sessions.
  - `pip install --quiet --disable-pip-version-check` + `tail -5` means that on a successful install the user sees nothing, but on a truncated failure they may not see the actual error if it's more than 5 lines deep.
  - The three triggers are evaluated with `elif` chains, so the first matching trigger short-circuits — order is (plugin-root moved) → (pyproject differs) → (venv missing). Evaluation order doesn't affect correctness since all three set the same flag, but it means the install reason isn't logged (no echo on which trigger fired).

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — there is no `bin/` directory. `scripts/run-mcp.sh` is an MCP-server wrapper (launched by `plugin.json`'s `mcpServers.cairn.command`), not a user-facing bin. The `cairn` CLI entry point declared in `pyproject.toml` (`[project.scripts] cairn = "cairn.cli:main"`) is installed into the pip-managed venv's `bin/` as a side effect of `pip install`, but it is not exposed to the user via the plugin — users invoke `cairn init` only when using the library-mode install (README "Quick Start" path), not the plugin path.
- **`bin/` files**: not applicable.
- **Shebang convention**: not applicable for `bin/`. For reference, both `scripts/bootstrap.sh` and `scripts/run-mcp.sh` use `#!/usr/bin/env bash`; `scripts/hook_orient.py` and `scripts/hook_ingest.py` use `#!/usr/bin/env python3` (but are invoked via `"${CAIRN_VENV}/bin/python" "...py"`, so the shebang is cosmetic).
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: direct `exec "${VENV}/bin/python" -m cairn.mcp_server "$@"` in `run-mcp.sh`; hooks use `"${CAIRN_VENV}/bin/python" "${CLAUDE_PLUGIN_ROOT}/scripts/hook_*.py"` in the hooks.json command strings. No `source activate` step. Venv discovery relies on `CAIRN_VENV` being present in the shell environment (written to `CLAUDE_ENV_FILE` by bootstrap).
- **Platform support**: POSIX shell scripts only (bash). No `.cmd` / `.ps1` pair.
- **Permissions**: not observed directly (gh API does not return mode). The scripts are invoked via `bash "..."` in `hooks.json`, so executable bit is not required for the bootstrap path. `run-mcp.sh` is similarly invoked via `bash` in `plugin.json`'s mcpServers.
- **SessionStart relationship**: `SessionStart` hook runs `scripts/bootstrap.sh` which writes `CAIRN_VENV` into `CLAUDE_ENV_FILE`; `run-mcp.sh` (launched on MCP server start) reads `CAIRN_VENV` from env. The wrapper script bridges plugin-root-relative invocation to data-dir-resident venv.
- **Pitfalls observed**: not applicable (no bin/).

## 8. User configuration

- **`userConfig` present**: no — neither `plugin.json` nor `marketplace.json` declare a `userConfig` block.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable. Secrets (`ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`) are expected via project-local `.env.local` which the hook scripts load at runtime via `python-dotenv` — not via Claude Code's `${user_config.KEY}` mechanism.
- **Pitfalls observed**: plugin ships requiring an `ANTHROPIC_API_KEY` (declared as a prereq in README) but does not declare it as `userConfig` with `sensitive: true`. Users must hand-configure `.env.local` — the Claude Code install flow won't prompt for the key. This is a legitimate design choice (the key is for the plugin's own LLM use, not forwarded by the harness) but leaves discovery to documentation.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable for tool-use hooks. For reference, `hook_orient.py` emits stdout JSON `{"additionalContext": summary}` (observed — conforms to Claude Code `UserPromptSubmit` contract).
- **Failure posture**: not applicable (no tool-use hooks). The hooks that do exist (`Stop`, `UserPromptSubmit`) fail-silent via bare `except Exception: sys.exit(0)` blocks around the async work — errors during ingest or orient never surface to the user.
- **Top-level try/catch wrapping**: not applicable. In the hook scripts, top-level try/except is observed: `hook_orient.py` wraps `asyncio.run(orient(prompt))` in `try: ... except Exception: sys.exit(0)`; `hook_ingest.py` does not wrap (relies on `sys.exit(0)` on missing transcript + letting `asyncio.run(ingest(content))` propagate).
- **Pitfalls observed**: the plugin has no tool-use enforcement surface at all — it is a context-provider plugin, not a gatekeeper.

## 10. Session context loading

- **SessionStart used for context**: only for dep install — `bootstrap.sh` creates the venv and persists `CAIRN_VENV`. It does not emit context.
- **UserPromptSubmit for context**: yes — `hook_orient.py` queries the reasoning graph for content relevant to the user's prompt and injects it as `additionalContext`.
- **`hookSpecificOutput.additionalContext` observed**: partial — `hook_orient.py` emits `print(json.dumps({"additionalContext": summary}))` (a bare top-level `additionalContext` key, not wrapped in `hookSpecificOutput`). Per the hooks reference, `UserPromptSubmit` context injection should use `hookSpecificOutput.additionalContext`. Observed shape is the legacy / shortcut form. Worth flagging as a potential hooks-schema drift.
- **SessionStart matcher**: none — the `SessionStart` entry in `hooks.json` has no `matcher` field. Per the hooks reference, absence of matcher means fires on all sub-events (`startup`, `clear`, `compact`, `resume`).
- **Pitfalls observed**:
  - `UserPromptSubmit` hook has `"timeout": 10000` (10 seconds) — the only timeout declared among the three hooks. `SessionStart` (the bootstrap, which can pip-install on first run) has no timeout at all. `Stop` (background ingest) has no timeout but uses `"async": true`. This asymmetry is intentional: bootstrap can take minutes on first install and must not be killed; orient must complete fast so the model isn't blocked; ingest is fire-and-forget.
  - The 10-second ceiling on orient drives design choices throughout: graph cache (`MemoryEngine.from_cache` at `hook_orient.py:42` and the commit message "Async ingest + graph cache: eliminate per-turn rebuild") and the `k=5` limit on `search_nodes` are both pressure responses to the `UserPromptSubmit` budget.
  - SessionStart's `bootstrap.sh` re-runs on every matcher (startup/clear/compact/resume) because no matcher is declared — acceptable because the three-check short-circuits to a no-op when the venv is already good, but it does mean `echo "export CAIRN_VENV=..." >> "${CLAUDE_ENV_FILE}"` appends on every single session event, not just startup.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: not applicable.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (no tags at all, and this is a single-plugin marketplace so the multi-plugin tag convention doesn't apply).
- **Pitfalls observed**: not applicable.

## 13. Testing and CI

- **Test framework**: pytest (+ `pytest-asyncio` declared in `[project.optional-dependencies].dev`).
- **Tests location**: `tests/` at repo root — 17 test files plus `tests/integration/` subdir (with `test_agent_loop.py`, `test_sdk_e2e.py`, and an `external_project` fixture dir) and a `tests/conftest.py` that provides a session-metrics accumulator and asserts the `integration` marker.
- **Pytest config location**: `[tool.pytest.ini_options]` in `pyproject.toml` (`asyncio_mode = "auto"`, `testpaths = ["tests"]`, declares `integration` marker).
- **Python dep manifest for tests**: `pyproject.toml` `[project.optional-dependencies].dev` (`pytest>=7.0`, `pytest-asyncio>=0.21`, `voyageai>=0.3.3`).
- **CI present**: no — `.github/` directory does not exist (`gh api /contents/.github` returns 404).
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: direct `pytest` — README documents `.venv/bin/python -m pytest tests/ -m "not integration"` for unit tests and `-m integration` for integration tests (which require `ANTHROPIC_API_KEY` / optional `VOYAGE_API_KEY`).
- **Pitfalls observed**: substantial test suite (~17 test files, `test_resolver.py` 20KB, `test_integration.py` 29KB, `test_mutator.py` 20KB) with no CI to enforce it. Integration tests are gated behind the `integration` marker and live LLM keys — plausible why no CI, but there is no lint or unit-only CI either.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — no releases published (`gh api /releases` returns empty list).
- **Tag-sanity gates**: not applicable.
- **Release creation mechanism**: not applicable.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable — no `CHANGELOG.md` exists.
- **Pitfalls observed**: not applicable.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable.
- **Trigger**: not applicable.
- **Frontmatter validation**: not applicable (no skills/agents with frontmatter).
- **Hooks.json validation**: not applicable.
- **Pitfalls observed**: not applicable.

## 16. Documentation

- **`README.md` at repo root**: present (7911 bytes) — thorough, with Quick Start, Claude Code integration section, MCP tools table, SDK integration section, "How It Works" pipeline diagram, configuration/prereqs/tests sections, and known-limitations pointer.
- **Owner profile README at `github.com/smcady/smcady`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: not applicable (single-plugin marketplace, root README serves).
- **`CHANGELOG.md`**: absent.
- **`architecture.md`**: present at `docs/architecture.md` (5320 bytes) — describes the classify→resolve→mutate→index pipeline, data model, MemoryEngine coordinator, SDK wrapper, MCP server, LLM model choices, and merge detector. Plus `docs/configuration.md`, `docs/walkthrough.md`, `docs/limitations.md`, `docs/assets/`.
- **`CLAUDE.md`**: absent — and `.gitignore` explicitly excludes `CLAUDE.md` and `**/CLAUDE.md`, so this is a deliberate "don't commit agent-context files" stance.
- **Community health files**: none — no `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`. GitHub Discussions is enabled (`has_discussions: true`) and README links to it.
- **LICENSE**: present (`MIT`).
- **Badges / status indicators**: absent — README opens with a logo image and tagline, no shields.
- **Pitfalls observed**: none — documentation is unusually complete for a 3-star repo; `docs/` is a real dev reference, not a placeholder.

## 17. Novel axes

- **Three-pronged SessionStart change detection** — bootstrap evaluates (a) plugin-root-path drift via cached file content, (b) `diff -q` on `pyproject.toml` against a cached copy in `${CLAUDE_PLUGIN_DATA}`, and (c) venv Python existence. The first check is the unusual one: caching the literal `${CLAUDE_PLUGIN_ROOT}` path lets the plugin detect that it has been moved (Claude Code relocating plugin cache on update) and rebuild the venv at the new location. Most plugins with similar bootstraps only check dependency-manifest drift. This pattern names three orthogonal failure modes — plugin moved, deps changed, venv missing — and collapses them into one reinstall flag.
- **Shell-level "env file" as cross-hook env-var plumbing** — bootstrap writes `export CAIRN_VENV=...` into `${CLAUDE_ENV_FILE}` so that later hooks (Stop, UserPromptSubmit) and the MCP server (via `scripts/run-mcp.sh`) can reference `CAIRN_VENV` without knowing `CLAUDE_PLUGIN_DATA`. This avoids hard-coding venv paths in `hooks.json` command strings and decouples venv location from hook definitions. Worth documenting as a general pattern for plugins where one hook provisions state that others consume.
- **Plugin-level MCP inline vs. project-level `.mcp.json` coexistence** — `plugin.json` declares the MCP server inline (plugin-mode install via Claude Code plugin harness), while `.mcp.json.example` at repo root and `cairn init` command configure the same MCP server in a project-local `.mcp.json` (library-mode install via `pip install -e` + `cairn init`). Two install paths, one conceptual surface, no overlap in runtime because plugin-mode uses `${CLAUDE_PLUGIN_ROOT}`-relative paths and library-mode uses absolute project paths.
- **Differentiated hook timeout philosophy** — `UserPromptSubmit` carries `"timeout": 10000` (blocking the model, must finish fast), `Stop` is `"async": true` with no timeout (fire-and-forget background), `SessionStart` has no timeout (provisioning, can take minutes on first install). The three different postures for three different latency budgets on the same plugin is a legible pattern worth naming.
- **`UserPromptSubmit` additionalContext shape** — `hook_orient.py` emits `{"additionalContext": summary}` as a bare top-level key rather than the spec-documented `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": summary}}`. Potentially a legacy or tolerated form; worth flagging whether the harness accepts both shapes.
- **`.gitignore` excludes `CLAUDE.md` repo-wide** (`CLAUDE.md` + `**/CLAUDE.md`). Explicit choice that agent-context files are not-to-be-committed. Unusual posture; most projects either commit `CLAUDE.md` or have no stance.
- **Dual-mode plugin/library** — the same source tree installs either as a Claude Code plugin (via marketplace) or as a pip-installable Python library (`pip install -e ".[dev]"` + `cairn init`). The `[project.scripts] cairn = "cairn.cli:main"` entry point is only visible in library mode; plugin-mode users never see the `cairn` CLI because their venv lives in `${CLAUDE_PLUGIN_DATA}/.venv` and isn't on PATH.

## 18. Gaps

- **File permission bits** — gh API `/contents/<path>` doesn't return octal mode. Can't confirm whether `scripts/bootstrap.sh`, `scripts/run-mcp.sh`, or the hook scripts are `100755` or `100644`. They are invoked via `bash ".../bootstrap.sh"` and `"${CAIRN_VENV}/bin/python" ".../hook_*.py"` respectively, so the executable bit is not required for the observed invocation paths. Would need `git ls-tree HEAD -- scripts/` on a clone to confirm.
- **Exact behavior on bootstrap failure** — I inferred "next session re-enters install" because `CACHED_PYPROJECT` is only updated on success, but did not observe an actual failure recovery run. Would need to seed a broken venv and trigger two consecutive sessions to verify.
- **Whether the `{"additionalContext": ...}` bare shape is accepted** — the Claude Code hooks-reference documents `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ...}}`. Observed code emits the bare form. Unclear whether the harness silently accepts both or whether the injection is actually a no-op in production. Would need a runtime test against the current Claude Code release.
- **Marketplace-mode install verification** — did not install the plugin via a consuming marketplace; all findings are source-level. Install-time behavior of `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_ENV_FILE}`, and the three-pronged check are inferred from script logic, not observed running.
- **Whether `CLAUDE_ENV_FILE` is truncated between sessions** — the bootstrap's `>>` append is harmless only if the harness truncates the env file per-session. If it persists, `CAIRN_VENV` will have N occurrences after N sessions. Behavior of `CLAUDE_ENV_FILE` lifecycle is not documented in this repo and would need hooks-reference cross-check.
- **Marketplace discoverability via metadata** — marketplace.json has no top-level `description` nor `metadata.description`, which means a consuming aggregator that expects metadata-level text will see nothing — can't verify without testing against the marketplace CLI.
