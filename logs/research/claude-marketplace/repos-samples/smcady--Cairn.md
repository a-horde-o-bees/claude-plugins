# Sample

Mirrors of `https://github.com/smcady/Cairn`. Persistent reasoning graph for AI memory — tracks what was decided, contradicted, and left open across sessions; surfaces 7 MCP tools (`harness_status`, `harness_query`, `harness_ingest`, `harness_search`, `harness_orient`, `harness_trace`, `harness_debug`) plus three lifecycle hooks. MIT-licensed (LICENSE present, SPDX `MIT`, 1067 bytes); 3 stars at sample time; current tip is commit `fd9da2fe` on `main` (2026-03-21, "Async ingest + graph cache: eliminate per-turn rebuild") with no tags or releases.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` at repo root (298 bytes) with one plugin entry. Top-level keys are `name`, `owner`, `plugins` only. No `metadata` wrapper, no top-level `description`. Marketplace name `cairn-marketplace`, plugin name `cairn` (no reserved-name collision). `owner` is `{"name": "Shawn Cady"}` with no `email` or `url`.

## Plugin source binding

### Relative source pointing to repo root (`./`)

Marketplace entry has `"source": "."`. Single plugin at repo root.

### `strict` field default

`strict` field absent on the marketplace entry — implicit-true default. No `skills` override (no skills in this plugin at all).

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

Marketplace entry has `name`, `description`, `version`, `source` only — no `category`, `tags`, or `keywords`. `plugin.json` carries `keywords: ["memory","reasoning","agents","graph"]` but those are plugin-level, not marketplace-entry-level.

### `$schema` absence on per-plugin manifests

`$schema` absent on both marketplace.json and plugin.json.

## Version coordination

### Dual-file version (manifest pair)

`marketplace.json` plugin entry and `plugin.json` both declare `"version": "0.1.0"`. No mechanism (hook/script) keeps them in sync — hand-edit discipline required on every bump.

## Channel distribution

### No pinning surface

Single manifest, single main branch, no stable/latest separation. Users pin via marketplace ref if they want a specific version. Single-plugin personal marketplace at 0.1.0 with no distribution ladder.

## Tag and release lifecycle

### No tags at all

`gh api /tags` returns an empty list. Only `main` branch exists. No pre-release suffixes. Plain `0.1.0` string in plugin.json, no auto-increment, no pre-commit version bump (no `.pre-commit-config.yaml`, `.github/hooks`, `.husky/`). Plugin is pre-release across a ~3-day burst of commits (2026-03-18 to 2026-03-21); install via marketplace pulls `main` head.

## Plugin-component registration

### Inline `mcpServers` definition in `plugin.json`

`plugin.json`'s `mcpServers` is inlined as `{"cairn": {"command": "bash", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/run-mcp.sh"]}}`. No `hooks` key in plugin.json — hooks are discovered from `hooks/hooks.json` by Claude Code's default discovery.

## Component composition

### MCP servers

Single MCP server `cairn` declared inline in plugin.json, launched via `bash ${CLAUDE_PLUGIN_ROOT}/scripts/run-mcp.sh`. The server exposes 7 MCP tools (`harness_status`, `harness_query`, `harness_ingest`, `harness_search`, `harness_orient`, `harness_trace`, `harness_debug`).

### Hooks

`hooks/hooks.json` declares three hooks: SessionStart (bootstrap), Stop (async ingest), UserPromptSubmit (orient).

### Component types absent across the corpus

No skills, no commands, no agents, no `.mcp.json` (MCP server is declared inline; `.mcp.json.example` exists at repo root but is a user-installation template for library-mode install, not a plugin component), no `.lsp.json`, no monitors, no bin, no output-styles. The plugin's entire product surface is one MCP server plus three hook scripts — unusual for a marketplace plugin.

## Server runtime (MCP)

### Inline `mcpServers` definition in `plugin.json`

`plugin.json` declares the MCP server inline (plugin-mode install, plugin-root-relative paths). A parallel project-local `.mcp.json.example` at repo root and a `cairn init` CLI command (visible only after `pip install -e ".[dev]"`) wire the same server with absolute project paths for library-mode install. Plugin-mode and library-mode use different path roots so there's no overlap at runtime.

### Local venv built by SessionStart hook

`scripts/run-mcp.sh` does `exec "${VENV}/bin/python" -m cairn.mcp_server "$@"` — direct exec of the venv python (no `source activate`). Venv discovery relies on `CAIRN_VENV` being present in the shell environment (written to `CLAUDE_ENV_FILE` by the SessionStart bootstrap).

## Dependency installation

### SessionStart-driven Python venv with hash gating

Dep manifest is `pyproject.toml` (hatchling build-backend, Python >=3.12; 9 runtime deps including `anthropic`, `mcp[cli]`, `networkx`, `pydantic`, `fastembed`, `numpy`, `pyyaml`, `python-dotenv`). Install location is `${CLAUDE_PLUGIN_DATA}/.venv` — venv created in plugin data dir, not plugin root. Install script is `scripts/bootstrap.sh` (1309 bytes), wired as the `SessionStart` hook command in `hooks/hooks.json`. Bootstrap runs `python3 -m venv` (with `2>/dev/null || python -m venv` fallback for systems without `python3`) then `pip install --quiet --disable-pip-version-check "${PLUGIN_ROOT}"`. Pip output piped through `2>&1 | tail -5` so users see only the last 5 lines on failure. No `uv`, no `uvx`, no PEP 723 inline metadata. The cached `.plugin_root` trigger handles plugin-directory moves but Python minor version changes (3.12 → 3.13) are not tracked — venv silently keeps the old interpreter.

## Install change detection

### Three-pronged OR (path drift + manifest diff + venv health)

Three-pronged OR. Reinstall fires if any of: (1) cached plugin-root path file (`${DATA_DIR}/.plugin_root`) is missing or its content differs from current `${CLAUDE_PLUGIN_ROOT}` (detects plugin directory move on update); (2) `diff -q "${PLUGIN_ROOT}/pyproject.toml" "${DATA_DIR}/pyproject.toml"` returns non-zero (detects dependency manifest change); (3) `${VENV_DIR}/bin/python` is not executable (detects missing/broken venv). The three triggers are evaluated with `elif` chains so the first match short-circuits — order is (plugin-root moved) → (pyproject differs) → (venv missing). Order doesn't affect correctness since all three set the same flag, but it means the install reason isn't logged.

## Install trigger and lifecycle

### SessionStart direct invocation

`scripts/bootstrap.sh` is the SessionStart hook command in `hooks/hooks.json`.

## Install failure posture

### Implicit retry via late-write cache marker

No `rm` on failure. `set -euo pipefail` halts the bootstrap if any step fails — no cleanup, so a partially-created venv may remain. The two content triggers (`.plugin_root` file, cached `pyproject.toml`) are written *only* after pip install succeeds; on failure neither is updated, so the next session's `diff -q` check fails again and re-enters the install branch. Pip stderr truncated to last 5 lines is the user-facing failure surface.

## Hook handler runtime

### Python stdlib runner with external probing

`scripts/hook_orient.py` and `scripts/hook_ingest.py` are Python (shebang `#!/usr/bin/env python3` is cosmetic — they're invoked via `"${CAIRN_VENV}/bin/python" "...py"` in the hooks.json command strings, so the shebang is unused). Bootstrap and run-mcp wrappers use `#!/usr/bin/env bash`.

## Hook output contract

### `additionalContext` for context injection

`hook_orient.py` emits stdout JSON `{"additionalContext": summary}` — bare top-level `additionalContext` key, not wrapped in `hookSpecificOutput.{hookEventName, additionalContext}`. Per the hooks reference the spec form is the wrapped one; the bare form is either tolerated legacy or potentially a no-op.

### `hookSpecificOutput.additionalContext` envelope versus bare top-level

This sample emits the bare top-level form rather than the documented `hookSpecificOutput.additionalContext` envelope.

## Hook failure posture

### Silent fail-open (`exit 0` always, retry every hook)

`hook_orient.py` wraps `asyncio.run(orient(prompt))` in `try: ... except Exception: sys.exit(0)`. `hook_ingest.py` does not wrap top-level (relies on `sys.exit(0)` on missing transcript + letting `asyncio.run(ingest(content))` propagate). Errors during ingest or orient never surface to the user.

## Hook timeout and async philosophy

### Differentiated per-hook timeouts

Three hooks with three distinct timeout postures, encoded directly in `hooks.json`. `UserPromptSubmit` carries `"timeout": 10000` (10 seconds — must complete fast so the model isn't blocked). `Stop` is `"async": true` with no timeout (fire-and-forget background ingest). `SessionStart` (the bootstrap, which can pip-install on first run) has no timeout at all — provisioning, can take minutes on first install. The asymmetry is intentional: bootstrap must not be killed; orient must complete fast; ingest is fire-and-forget. The 10-second ceiling on orient drives design choices throughout: graph cache (`MemoryEngine.from_cache` at `hook_orient.py:42` and the commit "Async ingest + graph cache: eliminate per-turn rebuild") and the `k=5` limit on `search_nodes` are pressure responses to the `UserPromptSubmit` budget.

## Session context loading

### Dependency install only (no context emission)

`bootstrap.sh` (SessionStart) creates the venv and persists `CAIRN_VENV` — does not emit context.

### `UserPromptSubmit` skill-activator with confidence threshold

`hook_orient.py` queries the reasoning graph for content relevant to the user's prompt and injects it as `additionalContext` (bare top-level shape — see *Hook output contract*). The 10-second timeout caps query latency; cached graph (`MemoryEngine.from_cache`) and `k=5` search ceiling keep queries inside the budget.

## SessionStart matcher scope

### Empty matcher (all sub-events)

The `SessionStart` entry in `hooks.json` has no `matcher` field — fires on all sub-events (`startup`, `clear`, `compact`, `resume`). Re-runs of bootstrap on every event are acceptable because the three-check short-circuits to a no-op when the venv is already good — but it does mean `echo "export CAIRN_VENV=..." >> "${CLAUDE_ENV_FILE}"` appends on every single session event, not just startup.

## Cross-hook environment plumbing

### `$CLAUDE_ENV_FILE` append for cross-hook env vars

Bootstrap writes `export CAIRN_VENV=...` into `${CLAUDE_ENV_FILE}` so the `Stop` and `UserPromptSubmit` hooks can find the venv Python and `scripts/run-mcp.sh` (the MCP server launcher) reads it from env. If `CLAUDE_ENV_FILE` is not set, the env var is silently not persisted — downstream hooks fail with `run-mcp.sh`'s error message ("Cairn not bootstrapped. Restart your Claude Code session."). Bootstrap appends to `CLAUDE_ENV_FILE` on every session even when no reinstall is needed — multiple `export CAIRN_VENV=...` lines accumulate across sessions if the env file is not truncated by the harness between sessions.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. Plugin's surface is the MCP server (which is launched by Claude Code as needed) plus the three lifecycle hooks.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field on plugin.json. Single-plugin marketplace.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks. Plugin is a context-provider plugin, not a gatekeeper. The three hooks that exist (`SessionStart`, `Stop`, `UserPromptSubmit`) inject/persist context but do not gate tool calls.

## Testing

### Pytest with asyncio support

Test framework is pytest plus `pytest-asyncio` (`asyncio_mode = "auto"` in `pyproject.toml [tool.pytest.ini_options]`). `pyproject.toml` declares `pytest>=7.0`, `pytest-asyncio>=0.21`, `voyageai>=0.3.3` under `[project.optional-dependencies].dev`. Test runner invocation: README documents `.venv/bin/python -m pytest tests/ -m "not integration"` for unit tests and `-m integration` for integration tests (which require `ANTHROPIC_API_KEY` / optional `VOYAGE_API_KEY`).

### Pytest with marker-segmented suites

Integration tests live in `tests/integration/` with `test_agent_loop.py`, `test_sdk_e2e.py`, and an `external_project` fixture dir. `tests/conftest.py` provides a session-metrics accumulator and asserts the `integration` marker. `[tool.pytest.ini_options]` declares `testpaths = ["tests"]` and the `integration` marker.

### Centralized `tests/` placement

`tests/` at repo root with 17 test files (`test_resolver.py` 20KB, `test_integration.py` 29KB, `test_mutator.py` 20KB) plus `tests/integration/` subdir.

## CI workflow shape

### No CI

`.github/` directory does not exist (`gh api /contents/.github` returns 404). Substantial test suite (~17 files) with no CI to enforce it. Integration tests gated behind the `integration` marker and live LLM keys; no lint or unit-only CI either.

## Release automation

### No release automation / manual

No releases published (`gh api /releases` returns empty list). No release workflow, no automation, no tag-sanity gates. No `CHANGELOG.md`.

## Marketplace validation

### No validation

No validation workflow, no manifest validator, no pre-commit hook. No skills/agents with frontmatter, no hooks.json validator.

## Documentation surface

### README + ARCHITECTURE + CLAUDE-as-pointer

Root `README.md` (7911 bytes) — Quick Start, Claude Code integration section, MCP tools table, SDK integration section, "How It Works" pipeline diagram, configuration/prereqs/tests sections, known-limitations pointer.

### Nested `docs/` tree with map in README

`docs/architecture.md` (5320 bytes) describes the classify→resolve→mutate→index pipeline, data model, MemoryEngine coordinator, SDK wrapper, MCP server, LLM model choices, merge detector. Plus `docs/configuration.md`, `docs/walkthrough.md`, `docs/limitations.md`, `docs/assets/`. Documentation is unusually complete for a 3-star repo; `docs/` is a real dev reference, not a placeholder.

### No CLAUDE.md

`.gitignore` explicitly excludes `CLAUDE.md` and `**/CLAUDE.md` repo-wide — deliberate "don't commit agent-context files" stance.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` at root (architecture lives at `docs/architecture.md`, not at root).

## Community health files

### Bare minimum (LICENSE only)

No `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`. GitHub Discussions is enabled (`has_discussions: true`) and README links to it. README opens with a logo image and tagline; no shields/badges.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

`LICENSE` file present at repo root, SPDX `MIT`. plugin.json/marketplace.json declarations align.

## User configuration and authentication

### `.env` files in cloned repo

No `userConfig` block in plugin.json or marketplace.json. Secrets (`ANTHROPIC_API_KEY`, `VOYAGE_API_KEY`) are expected via project-local `.env.local` which the hook scripts load at runtime via `python-dotenv` — not via Claude Code's `${user_config.KEY}` mechanism.

### No userConfig, env-var only

Plugin ships requiring an `ANTHROPIC_API_KEY` (declared as a prereq in README) but does not declare it as `userConfig` with `sensitive: true`. Users must hand-configure `.env.local` — the Claude Code install flow won't prompt for the key. Legitimate design choice (the key is for the plugin's own LLM use, not forwarded by the harness) but leaves discovery to documentation.

## State persistence

### `${CLAUDE_PLUGIN_DATA}` for venvs and stamps

Venv at `${CLAUDE_PLUGIN_DATA}/.venv`. Cached `pyproject.toml` and `.plugin_root` files at `${CLAUDE_PLUGIN_DATA}` for change detection. Reasoning graph data (the plugin's runtime state) lives under plugin data dir paths.

## Plugin/state separation

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code is read-only at `${CLAUDE_PLUGIN_ROOT}` (referenced from `plugin.json`'s mcpServers, hooks.json command strings). Venv and state under `${CLAUDE_PLUGIN_DATA}`.

## Cross-platform discipline

### POSIX-only with no Windows story

All scripts are bash or Python; POSIX paths; no `.cmd`/`.ps1`. Scripts invoked via `bash "..."` and `"${CAIRN_VENV}/bin/python" "..."` so executable bits aren't required for the observed invocation paths.

## Cross-role tools

### Python (stdlib + pip + uv)

`python3 -m venv` and `pip install` are the install primitives. No `uv`/`uvx`. Tests via `pytest`.

### Bash

Bootstrap and `run-mcp.sh` wrappers are bash with `#!/usr/bin/env bash`. `set -euo pipefail` enforced in bootstrap.

### `${CLAUDE_PLUGIN_ROOT}` env var

Used in plugin.json's mcpServers args (`${CLAUDE_PLUGIN_ROOT}/scripts/run-mcp.sh`) and hooks.json command strings.

### `${CLAUDE_PLUGIN_DATA}`

Venv location and change-detection cache files.

### `$CLAUDE_ENV_FILE`

Append target for `CAIRN_VENV` so the MCP server wrapper and hook scripts find the venv path without re-deriving it.

### `plugin.json.version`

Plugin version source (`0.1.0`); also duplicated in marketplace entry.
