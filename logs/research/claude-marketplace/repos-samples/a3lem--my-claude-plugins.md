# Sample

Mirrors of `https://github.com/a3lem/my-claude-plugins`. Personal collection of 11 plugins covering SDD, Python rules injection, notes/decisions/journal, auto-memory, LSP, provenance frontmatter, comment conventions, ticket-cli integration, and a language-agnostic differential testing skill. No LICENSE declared (repo API `license` field is null), default branch `main`, 0 stars, last commit 2026-03-31; sample origin: bin-wrapper (the `bin/inject-rules` standalone Python wrapper symlinked into hook dirs).

## Marketplace manifest layout

### Multi-plugin owned-aggregator marketplace

Single `.claude-plugin/marketplace.json` at repo root listing 11 plugins under `plugins/<name>/`, each with its own `.claude-plugin/plugin.json` and source tree. Every entry uses a relative source (`./plugins/<name>`); the owner authors all listed plugins. The marketplace `description` field for `theo-calvin-testing` claims "Differential testing with tc - input.json to output.json, diffed against expected.json", but the same plugin's `plugin.json` carries a different string ("Theodore Calvin's testing framework - language-agnostic, JSON-based test runner") — drift between marketplace entry and plugin.json description is silent and unreconciled. Per-entry vs per-plugin version-sync surface is unguarded by validation.

### Top-level `metadata` wrapper variants

`metadata.{description}` wrapper — only `description` inside `metadata`; top-level carries `name`, `owner`, `$schema`, and `plugins`. `metadata.pluginRoot` is absent — per-plugin `source` fields carry relative paths directly (`./plugins/<name>`).

### `$schema` declaration on marketplace.json

Present (`https://anthropic.com/claude-code/marketplace.schema.json`). No CI step actively validates against the schema — editor-assistance only.

## Plugin source binding

### Relative source pointing to subdirectory

Every plugin entry uses `"source": "./plugins/<name>"`. No github/url/git-subdir/npm sources.

### `strict` field default

`strict` is absent on every entry — implicit-true default. No `skills` override on any entry — no carving via override.

## Per-plugin discoverability metadata

### Bare-minimum (name, version, description only)

Every plugin entry has only `name`, `source`, `description`; no `category`, `tags`, `keywords` on marketplace entries. Some `plugin.json`s carry an `author` object but none carry keywords/tags. Several `plugin.json`s omit `version` entirely (`auto-memory` has `"version": "1.1"` — a non-semver shorthand; `better-comments` and `session-setup` have no version field at all). `auto-memory`'s `1.1` is neither semver-major-minor-patch nor consistent with its siblings (`1.0.0`, `0.1.0`, etc.) — runtime handling of truncated semver is implementation-defined. Missing `version` on two plugins likely survives only because Claude Code does not currently reject manifests without one.

## Version coordination

### Multi-site sprawl (5+ locations)

`spec-driven-dev/CHANGELOG.md` documents through `2.1.0` (2026-03-13) while the plugin's `plugin.json` still says `"version": "1.0.0"`. SKILL.md frontmatter says `version: 3.2.0`. Three different version authorities disagree within a single plugin. Marketplace entries carry no `version` field; each plugin's `plugin.json` carries its own `version`, eliminating one drift surface but leaving the per-plugin three-way (CHANGELOG / plugin.json / SKILL.md frontmatter) drift in place.

## Channel distribution

### No pinning surface

No channel split — users pin via `@ref` if at all. No stable/latest separation. No duplicate marketplace files, no release-branch split, no channel tags. Single `main` branch tracks everything. Conscious minimalism; personal repo with no downstream consumers.

## Tag and release lifecycle

### No tags at all

`git/refs/tags` returned 404 (no tags exist) and `/releases` is empty. No release branching (tag-on-main would be the natural fit, but no tags are cut). No pre-release suffixes. No dev-counter scheme — per-plugin `version` fields are manually bumped when the author remembers (root CHANGELOG shows `[Unreleased]`; `spec-driven-dev` carries its own CHANGELOG with proper `[1.0.0]`, `[2.0.0]`, `[2.1.0]` dates, but `plugin.json` still reads `1.0.0` — stale). No pre-commit version bump — last commit is literally titled "lazy commit"; there is no hook infrastructure.

## Plugin-component registration

### Default convention discovery

Every `plugin.json` carries only `name`, `description`, optional `version`, optional `author`. No `commands`, `skills`, `agents`, `hooks`, `mcpServers`, or `monitors` arrays. Discovery is purely convention-based: Claude Code finds `commands/`, `skills/`, `agents/`, `hooks/hooks.json`, `.lsp.json`, `.mcp.json` by filesystem convention.

### Out-of-band hook registration

`hooks/inject-rules` files in five plugins (`auto-memory`, `better-comments`, `python-rules`, `ticket-cli`, `session-setup`) are git-tracked symlinks (mode 120000) whose target is `/Users/<author>/Code/projects/my-claude-plugins/bin/inject-rules` — an absolute path baked into the symlink text. When a user installs the plugin via the marketplace, Claude Code copies the plugin directory only; the symlink resolves to the author's home path on the installing machine and fails. The author's documented rationale (in root `CLAUDE.md`) expects the symlink to carry a relative path for the "ship-with-install" strategy to work, not an absolute one. Symlinks are stored with absolute targets so the strategy is broken as committed; installed plugins will fail the SessionStart hook with a file-not-found error.

## Component composition

### Skills (universal)

Across all 11 plugins: skills present in `frontmatter`, `project-knowledge`, `project-notes`, `decision-log`, `journal`, `spec-driven-development`, `theo-calvin-testing`, `ticket`. Some samples place loose `skills/<name>.md` files at the skills/ root with command-style frontmatter, which is non-canonical.

### Commands

`remember`, `forget` in `auto-memory`; `apply`, `archive`, `explore`, `propose`, `refine` in `spec-driven-dev`.

### Agents

`spec-critic`, `spec-sync` in `spec-driven-dev`.

### Hooks

SessionStart hooks across `auto-memory`, `better-comments`, `python-rules`, `ticket-cli`, `session-setup`.

### LSP config

`basedpyright-lsp` is a single-file plugin that ships only `.claude-plugin/plugin.json`, `.lsp.json`, and a README — no skills, no commands, no hooks, no agents. Demonstrates the minimum-viable plugin surface for LSP enablement.

### bin

`bin/inject-rules` at marketplace root; plugins consume via symlink, not their own `bin/`.

## Plugin-component placement

### Outside plugin directory at repo root

`bin/` lives at the marketplace root with no owning plugin. Designed as a shared utility consumed by multiple plugins via per-plugin symlink (`plugins/<name>/hooks/inject-rules`).

## Skill authoring conventions

### Standard frontmatter

`SKILL.md` files use standard frontmatter (`name`, `description`, etc.). The `spec-driven-dev` plugin's SKILL.md frontmatter carries `version: 3.2.0` while the plugin's `plugin.json` reads `1.0.0` and CHANGELOG documents `2.1.0` — three-way per-skill version drift within a single plugin.

## Agent declaration conventions

### Plain tool-name list

`allowed-tools: Read, Glob, Grep` (comma-joined line) or `Read, Edit, Write, Glob`. No permission-rule syntax like `Bash(uv run *)`.

### Standard fields plus model / color

Frontmatter uses `name`, `description`, `model: sonnet`, `allowed-tools` (plain list), and `skills` (pointer to a named skill).

### Custom agent frontmatter extensions

`spec-critic.md` and `spec-sync.md` declare `allowed-prompts:` with a nested list of `{tool, prompt}` pairs. This is not a documented field in the Claude Code plugins reference. Either an experimental field, a convention from another tool, or dead configuration. May silently do nothing.

## Server runtime (MCP)

### In-place stdlib script (no installer)

`spec-driven-dev`'s `spectl.py` is run directly via system `python3` and imports only stdlib (argparse, json, os, re, shutil, string, sys, datetime, pathlib, random). `pyproject.toml` declares `requires-python = ">=3.14"` for a `uv sync` path that no runtime code path actually exercises — the floor is functionally unenforced because the script's stdlib-only imports work on much earlier Python; it would only bite anyone who tries the documented `uv` path. README and CLAUDE.md both invoke as `python3 scripts/spectl.py`. The dev dependency group contains only pytest.

## Bin entry mechanism

### Marketplace-root bin with per-plugin symlink

A single shared wrapper `bin/inject-rules` at the marketplace root is designed to be called by hooks across multiple plugins. Implementation: standalone Python (stdlib) script that reads one or more markdown files and emits a `<system-reminder>` block to stdout for SessionStart consumption. Resolves the plugin name from `plugin.json` and the marketplace name by walking up to `.claude-plugin/marketplace.json`, then builds a display path like `"references/STYLE.md from plugin python-rules@a3lem-claude-plugins"`. Wrapper shebang is `#!/usr/bin/env python3` — standalone (no venv, no `uv run`, pure stdlib). One `hooks/session-start.sh` in `ticket-cli` uses `#!/usr/bin/env bash` for an independent priming hook. Runtime resolution: `${CLAUDE_PLUGIN_ROOT}` in every `hooks.json` command. The wrapper script itself resolves the plugin directory via `CLAUDE_PLUGIN_ROOT` env var, with a fallback to the file's own path if the env var is absent. Permissions: `bin/inject-rules` is 100755 (executable). `plugins/*/hooks/inject-rules` are 120000 (symlinks) pointing to `/Users/<author>/Code/projects/my-claude-plugins/bin/inject-rules` — absolute target paths keyed to the author's home directory. The author documents the symlink-sharing pattern in root `CLAUDE.md` ("To use a shared utility from a plugin, symlink it into the plugin directory … so it ships with the plugin on install"), but the committed symlinks have absolute targets keyed to the author's machine. Once installed on any other machine, the symlinks are dead. The correct fix is `ln -s ../../../../bin/inject-rules` (relative) or bundling a copy per plugin; either would ship through the marketplace copy. POSIX-only — bash + python3 only. No .cmd/.ps1 pair. Absolute-path symlink targets would break on any Windows/WSL path layout too. Auto-memory's `inject-memory` is a distinct 100755 regular file (not a symlink) with its own logic.

### No bin entry / direct invocation

Per-plugin `bin/` directories absent; the static bin wrapper is invoked directly from `hooks.json`'s SessionStart command. No hook builds or populates bin/.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

Wrapper script resolves the plugin directory via `CLAUDE_PLUGIN_ROOT` env var, with a fallback to the file's own path if the env var is absent.

## Dependency installation

### Zero dependencies / stdlib only

The plugin set deliberately avoids adding runtime deps. No plugin installs dependencies at session start. `spec-driven-dev` declares Python deps in `pyproject.toml` + `uv.lock` but expects the user to have them installed. `spectl.py` is run in-place as `python3 scripts/spectl.py` with stdlib-only imports. `frontmatter.py` and `inject-rules` / `inject-memory` all shebang `#!/usr/bin/env python3` and rely on system Python + stdlib. No `uv run`, no venv management, no `uvx` ad-hoc. `spec-driven-dev/pyproject.toml` declares `requires-python = ">=3.14"` — an extremely narrow floor (released October 2025); users on 3.12 or 3.13 will hit a soft-fail only if they `uv sync`/`pip install`. Since the plugin is run as `python3 scripts/spectl.py` with stdlib-only imports, the floor is functionally unenforced at runtime — but it would bite anyone who tries the documented `uv` path.

## Hook handler runtime

### Bash scripts at conventional path

`ticket-cli/hooks/session-start.sh` uses `#!/usr/bin/env bash` for an independent priming hook.

### Python stdlib runner with external probing

`bin/inject-rules` and `inject-memory` are standalone Python scripts (`#!/usr/bin/env python3`) using only stdlib. Hooks call these via `${CLAUDE_PLUGIN_ROOT}/hooks/inject-rules` (the per-plugin symlink) which delegates to the marketplace-root wrapper.

## Hook output contract

### `additionalContext` for context injection

The scripts print to stdout wrapped in `<system-reminder>` blocks (and `<rule>` blocks), relying on Claude Code's convention of capturing SessionStart stdout as an additional system message, not the newer structured `hookSpecificOutput.additionalContext` JSON channel. No JSON responses, no stderr channel for structured signals.

## Hook failure posture

### Fail-open with always-exit-0

`ticket-cli/hooks/session-start.sh` explicitly `exit 0` when `tk` is absent or `.tickets/` missing. Python hooks print to stderr and `sys.exit(1)` only on argparse/file-missing errors. No top-level exception handlers; any unexpected error propagates to Claude Code. The 2-3 second hook timeouts (`"timeout": 2` for inject-rules, `"timeout": 3` for inject-memory) are tight. On cold start with slow I/O, reading every markdown file and walking up for marketplace.json may approach the limit. No retries, no fallback.

## User configuration and authentication

### No userConfig, env-var only

No `plugin.json` declares `userConfig`. `auto-memory` honors `AUTO_MEMORY_DIR` env var (read in `inject-memory` via `os.environ.get`), not `${user_config.KEY}` substitution — configurability exists but via plain env vars, not the Claude Code userConfig channel. `auto-memory`'s description promises "configurable storage location" and the hook code supports `AUTO_MEMORY_DIR` env var override, but this isn't surfaced through `userConfig` — a user has to know to set the env var externally. Demonstrates a pattern where configurability is opaque to the plugin ecosystem; a user cannot discover the toggle by reading `plugin.json` or marketplace metadata.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse, PostToolUse, or PermissionRequest/PermissionDenied hooks. Output convention: stdout plain-text (a single `<system-reminder>` block or `<rule>` block) — no JSON responses, no stderr channel for structured signals. Failure posture: fail-open. Top-level try/catch wrapping is absent — Python hooks have no top-level exception handlers.

## Session context loading

### SessionStart stdout as system-reminder

Five of eleven plugins (`auto-memory`, `better-comments`, `python-rules`, `ticket-cli`, `session-setup`) use SessionStart hooks to inject rules into the system prompt. The scripts print to stdout wrapped in `<system-reminder>` blocks, relying on Claude Code's convention of capturing SessionStart stdout as an additional system message rather than the newer structured `hookSpecificOutput.additionalContext` JSON channel. UserPromptSubmit is not used. SessionStart matcher: none on any hook — every SessionStart hook fires on all sub-events (startup, clear, compact) without a matcher filter. `session-setup` uses a raw `echo` command in the hook (`echo 'IMPORTANT: At the start of the session, before answering for the first time, execute all steps in (optional) ' Session Setup' section of CLAUDE.md'`) — fires on clear/compact too, re-prompting the agent every time context is cleared.

### Provenance-decorated stdout

`bin/inject-rules` and `inject-memory` do work beyond simple concatenation — they look up the plugin's `name` from `plugin.json` and walk upward for the marketplace's `name`, then decorate the file path in the emitted `<system-reminder>` block with a `"path from plugin <name>@<marketplace>"` suffix. Gives the agent provenance for injected rules.

## SessionStart matcher scope

### Empty matcher (all sub-events)

Every SessionStart hook fires on all sub-events (startup, clear, compact) without a matcher filter.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. None of the 11 plugins ship monitors.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field in any `plugin.json`. The three "knowledge ecosystem" plugins (`spec-driven-dev`, `project-notes`, `project-knowledge`) are coupled by convention (README describes the coordination) but there is no machine-enforced `dependencies` field. The `project-knowledge` README explicitly says "This plugin doesn't manage any store directly – it routes to spec-driven-dev … and project-notes". A user installing only `project-knowledge` gets broken routing — and there is no `dependencies` declaration to prevent that. Coordination is documented prose, not enforced structure. No tags at all means the `{plugin-name}--v{version}` tag format is moot.

## Testing

### Co-located test placement

`spec-driven-dev`'s tests live inside the plugin directory at `plugins/spec-driven-dev/tests/` with 11 test files (test_archive, test_archived, test_changes, test_computed_status, test_discovery, test_info, test_links, test_new, test_refs, test_resolve, test_validate) and a `conftest.py` fixture module. No repo-root tests, no other plugin carries tests.

### Pytest with asyncio support

Test framework: pytest (only in `spec-driven-dev`). No `pytest.ini` and no `[tool.pytest.ini_options]` in the plugin's `pyproject.toml` — pytest relies on discovery defaults. Python dep manifest for tests: `pyproject.toml` `[dependency-groups] dev` section with `pytest>=9.0.2` (an extremely recent floor, tightly coupled to the `requires-python = ">=3.14"` floor). Test runner invocation: direct `pytest` (implied by conftest.py + standard layout). No `scripts/test.sh` wrapper. The `conftest.py` runs `spectl.py` as a subprocess via `sys.executable`, so tests self-locate the script relative to the test file. The other ten plugins have zero tests.

## CI workflow shape

### No CI

`.github/` returns 404 on the content API. No CI means the tests have no enforcement — they exist as a developer artifact only.

## Marketplace validation

### No validation

No `claude plugin validate` CLI hook, no pre-commit hook, no bun+zod or Python validator. `marketplace.json` carries `$schema` (`https://anthropic.com/claude-code/marketplace.schema.json`) but no tool in-repo runs schema validation against it. Drift between plugins' intended descriptions and their recorded ones would be caught by such validation but is not.

## Release automation

### No release automation / manual

The repo has no releases, no tags, and no CI. Versions in `plugin.json` are bumped manually and inconsistently. Per-plugin CHANGELOGs (`spec-driven-dev/CHANGELOG.md`, `theo-calvin-testing/CHANGELOG.md`, root `CHANGELOG.md`) are hand-maintained prose. Nothing verifies that CHANGELOG and `plugin.json` agree.

## Documentation surface

### Layered repo / plugin / skill READMEs (uneven)

Repo-root `README.md` (~2.3 KB, 38 lines) is a plugin index plus Knowledge Ecosystem routing table. Per-plugin READMEs are mixed — 7 of 11 plugins have one (`basedpyright-lsp`, `project-knowledge`, `project-notes`, `python-rules`, `session-setup`, `spec-driven-dev`, `theo-calvin-testing`, `ticket-cli`); `auto-memory`, `better-comments`, `frontmatter` have no per-plugin README. `architecture.md` is absent anywhere. `CLAUDE.md` is present at repo root (short, 21 lines), in `plugins/project-notes/` (16 lines), and `plugins/spec-driven-dev/` (workflow + layout). Not present in the other plugins.

### Free-form CHANGELOG variants

Root `CHANGELOG.md` is rudimentary; richer per-plugin in `spec-driven-dev` (most closely resembles Keep a Changelog with versioned `## [x.y.z] - YYYY-MM-DD` headers and Added/Changed/Removed subsections) and `theo-calvin-testing`. Format is ad-hoc.

## License declaration

### Single repo-level license

LICENSE is absent — no LICENSE file at repo root, repo API `license` field is null. No `license` field in `plugin.json` files. Technically the repo is "all rights reserved" by default — anyone cloning the marketplace has no explicit permission to reuse individual plugins beyond what GitHub's ToS provides.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md`.

## Cross-platform discipline

### POSIX-only with no Windows story

POSIX — bash + python3 only. No `.cmd`/`.ps1` pair. Absolute-path symlink targets would break on any Windows/WSL path layout too.

