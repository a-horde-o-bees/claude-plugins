# a3lem/my-claude-plugins

## Identification

- **URL**: https://github.com/a3lem/my-claude-plugins
- **Stars**: 0
- **Last commit date**: 2026-03-31 (`3643bd4 "lazy commit"`)
- **Default branch**: main
- **License**: absent (no LICENSE file at repo root; repo API `license` field is null)
- **Sample origin**: bin-wrapper (the `bin/inject-rules` standalone Python wrapper symlinked into hook dirs)
- **One-line purpose**: "A Claude Code Marketplace for my own plugins" — personal collection of 11 plugins covering SDD, Python rules injection, notes/decisions/journal, auto-memory, LSP, provenance frontmatter, comment conventions, ticket-cli integration, and a language-agnostic differential testing skill.

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: `metadata.{description}` wrapper — only `description` inside `metadata`; top-level carries `name`, `owner`, `$schema`, and `plugins`
- **`metadata.pluginRoot`**: absent — per-plugin `source` fields carry relative paths directly (`./plugins/<name>`)
- **Per-plugin discoverability**: none — every plugin entry has only `name`, `source`, `description`; no `category`, `tags`, `keywords` on marketplace entries. Some `plugin.json`s carry an `author` object but none carry keywords/tags.
- **`$schema`**: present (`https://anthropic.com/claude-code/marketplace.schema.json`)
- **Reserved-name collision**: no
- **Pitfalls observed**: the marketplace `description` field for `theo-calvin-testing` claims "Differential testing with tc - input.json to output.json, diffed against expected.json", but the same plugin's `plugin.json` carries a different string ("Theodore Calvin's testing framework - language-agnostic, JSON-based test runner"). Drift between marketplace entry and plugin.json description is silent and unreconciled.

## 2. Plugin source binding

- **Source format(s) observed**: relative — every entry uses `"./plugins/<name>"`. No github/url/git-subdir/npm sources.
- **`strict` field**: default (field absent on every entry — implicit true)
- **`skills` override on marketplace entry**: absent — no entry carves components via override
- **Version authority**: `plugin.json` only — marketplace entries carry no `version` field; each plugin's `plugin.json` carries its own `version`. No drift risk because marketplace doesn't duplicate the value.
- **Pitfalls observed**: several `plugin.json`s omit `version` entirely (`auto-memory` has `"version": "1.1"` — a non-semver shorthand; `better-comments` and `session-setup` have no version field at all). `auto-memory`'s `1.1` is neither semver-major-minor-patch nor consistent with its siblings (`1.0.0`, `0.1.0`, etc.) — runtime handling of truncated semver is implementation-defined. Observed — missing `version` on two plugins likely survives only because Claude Code does not currently reject manifests without one.

## 3. Channel distribution

- **Channel mechanism**: no split — users pin via `@ref` if at all; there is no stable/latest separation
- **Channel-pinning artifacts**: absent — no duplicate marketplace files, no release-branch split, no channel tags. Single `main` branch tracks everything.
- **Pitfalls observed**: none — conscious minimalism; personal repo with no downstream consumers.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: none — `git/refs/tags` returned 404 (no tags exist) and `/releases` is empty
- **Release branching**: none — tag-on-main would be the natural fit, but no tags are cut
- **Pre-release suffixes**: none observed — no tags at all
- **Dev-counter scheme**: absent — per-plugin `version` fields are manually bumped when the author remembers (CHANGELOG shows `[Unreleased]` for the root changelog; `spec-driven-dev` carries its own CHANGELOG with proper `[1.0.0]`, `[2.0.0]`, `[2.1.0]` dates, but `plugin.json` still reads `1.0.0` — stale)
- **Pre-commit version bump**: no — last commit is literally titled "lazy commit"; there is no hook infrastructure
- **Pitfalls observed**: `spec-driven-dev/CHANGELOG.md` documents through `2.1.0` (2026-03-13) while the plugin's `plugin.json` still says `"version": "1.0.0"`. SKILL.md frontmatter says `version: 3.2.0`. Three different version authorities disagree within a single plugin — classic drift.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery (no component fields) — every `plugin.json` carries only `name`, `description`, optional `version`, optional `author`. No `commands`, `skills`, `agents`, `hooks`, `mcpServers`, or `monitors` arrays. Discovery is purely convention-based: Claude Code finds `commands/`, `skills/`, `agents/`, `hooks/hooks.json`, `.lsp.json`, `.mcp.json` by filesystem convention.
- **Components observed** (across all 11 plugins):
  - skills: yes (frontmatter, project-knowledge, project-notes, decision-log, journal, spec-driven-development, theo-calvin-testing, ticket)
  - commands: yes (remember, forget in auto-memory; apply, archive, explore, propose, refine in spec-driven-dev)
  - agents: yes (spec-critic, spec-sync in spec-driven-dev)
  - hooks: yes (SessionStart across auto-memory, better-comments, python-rules, ticket-cli, session-setup)
  - .mcp.json: no
  - .lsp.json: yes (basedpyright-lsp — single-file plugin that ships only a `.lsp.json`)
  - monitors: no
  - bin: yes at marketplace root (`bin/inject-rules`); plugins consume via symlink, not their own `bin/`
  - output-styles: no
- **Agent frontmatter fields used**: `name`, `description`, `model` (sonnet), `allowed-tools` (plain list), `allowed-prompts` (a non-standard nested list of `{tool, prompt}` pairs), `skills` (pointer to a named skill)
- **Agent tools syntax**: plain tool names — `allowed-tools: Read, Glob, Grep` (comma-joined line) or `Read, Edit, Write, Glob`. No permission-rule syntax like `Bash(uv run *)`.
- **Pitfalls observed**: `allowed-prompts` on the spec-critic and spec-sync agents is not a documented plugin field in the Claude Code reference the author appears to have consulted — likely a convention from a tooling experiment. May silently do nothing. The per-plugin `hooks/inject-rules` files are git-tracked symlinks (mode 120000) whose target is `/Users/adriaan/Code/projects/my-claude-plugins/bin/inject-rules` — an absolute path baked into the symlink text. When a user installs the plugin via the marketplace, Claude Code copies the plugin directory only; the symlink resolves to the author's home path on the installing machine and fails (as documented in the repo's own `CLAUDE.md`: "To use a shared utility from a plugin, symlink it into the plugin directory … so it ships with the plugin on install"). The author's documented rationale expects the relative symlink to carry a relative path, not an absolute one. Observed — symlinks are stored with absolute targets so the "ship-with-install" strategy is broken as committed; installed plugins will fail the SessionStart hook with a file-not-found error.

## 6. Dependency installation

- **Applicable**: partial — no plugin installs dependencies at session start. `spec-driven-dev` declares Python deps in `pyproject.toml` + `uv.lock` but expects the user to have them installed (README and CLAUDE.md both say `python3 scripts/spectl.py` as plain invocation; the dev dependency group contains only pytest).
- **Dep manifest format**: pyproject.toml + uv.lock in `spec-driven-dev` only; none in other plugins
- **Install location**: not applicable — no installer; `spectl.py` is run in-place as `python3 scripts/spectl.py` with stdlib-only imports (argparse, json, os, re, shutil, string, sys, datetime, pathlib, random)
- **Install script location**: not applicable
- **Change detection**: not applicable — no auto-install
- **Retry-next-session invariant**: not applicable
- **Failure signaling**: not applicable
- **Runtime variant**: stdlib Python — `spectl.py` imports only stdlib. Dev-only pytest. No `uv run`, no venv management, no `uvx` ad-hoc. `frontmatter.py` and `inject-rules` / `inject-memory` all shebang `#!/usr/bin/env python3` and rely on system Python + stdlib.
- **Alternative approaches**: none — the plugin set deliberately avoids adding runtime deps. This is a key property of the minimalist approach.
- **Version-mismatch handling**: none
- **Pitfalls observed**: `spec-driven-dev/pyproject.toml` declares `requires-python = ">=3.14"`. Python 3.14 is an extremely narrow floor (released October 2025); users on 3.12 or 3.13 will hit a soft-fail only if they `uv sync`/`pip install`. Since the plugin is run as `python3 scripts/spectl.py` with stdlib-only imports, the floor is functionally unenforced at runtime — but it would bite anyone who tries the documented `uv` path.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — a single shared wrapper (`bin/inject-rules`) at the marketplace root is designed to be called by hooks across multiple plugins
- **`bin/` files**:
  - `bin/inject-rules` — standalone Python (stdlib) script that reads one or more markdown files and emits a `<system-reminder>` block to stdout for SessionStart consumption. Resolves the plugin name from `plugin.json` and the marketplace name by walking up to `.claude-plugin/marketplace.json`, then builds a display path like `"references/STYLE.md from plugin python-rules@a3lem-claude-plugins"`.
- **Shebang convention**: `#!/usr/bin/env python3` — all wrapper scripts. Standalone (no venv, no `uv run`, pure stdlib). One `hooks/session-start.sh` in `ticket-cli` uses `#!/usr/bin/env bash` for an independent priming hook.
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` in every `hooks.json` command. The wrapper script itself resolves the plugin directory via `CLAUDE_PLUGIN_ROOT` env var, with a fallback to the file's own path if the env var is absent.
- **Venv handling (Python)**: none — system python3, stdlib only. No venv, no `uv run`, no pip-install.
- **Platform support**: POSIX — bash + python3 only. No .cmd/.ps1 pair. Absolute-path symlink targets would break on any Windows/WSL path layout too.
- **Permissions**: `bin/inject-rules` is 100755 (executable). `plugins/*/hooks/inject-rules` are 120000 (symlinks) pointing to `/Users/adriaan/Code/projects/my-claude-plugins/bin/inject-rules`. `plugins/auto-memory/hooks/inject-memory` is a distinct 100755 regular file (not a symlink) with its own logic.
- **SessionStart relationship**: static — the bin wrapper is invoked directly from `hooks.json`'s SessionStart command. No hook builds or populates bin/.
- **Pitfalls observed**: the symlink-sharing pattern the author describes in root `CLAUDE.md` is a fine idea (one shared executable, plugins link it in), but the symlinks committed to git have absolute targets keyed to the author's home directory. Once installed on any other machine, the symlinks are dead. The correct fix is `ln -s ../../../../bin/inject-rules` (relative) or bundling a copy per plugin; either would ship through the marketplace copy. This is the load-bearing reason to treat this repo as a "sample of the pattern, not a working implementation" for the bin-wrapper axis.

## 8. User configuration

- **`userConfig` present**: no — no `plugin.json` declares `userConfig`
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: `auto-memory` uses `AUTO_MEMORY_DIR` environment variable (read in `inject-memory` via `os.environ.get`), not `${user_config.KEY}` substitution — so configurability exists, but via plain env vars not the Claude Code userConfig channel
- **Pitfalls observed**: `auto-memory`'s description promises "configurable storage location" and the hook code supports `AUTO_MEMORY_DIR` env var override, but this isn't surfaced through `userConfig` — a user has to know to set the env var externally. Missed opportunity to use the declarative surface.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: stdout plain-text (a single `<system-reminder>` block or `<rule>` block) — no JSON responses, no stderr channel for structured signals
- **Failure posture**: fail-open — `ticket-cli/hooks/session-start.sh` explicitly `exit 0` when `tk` is absent or `.tickets/` missing; Python hooks print to stderr and `sys.exit(1)` only on argparse/file-missing errors
- **Top-level try/catch wrapping**: absent — Python hooks have no top-level exception handlers; any unexpected error propagates to Claude Code
- **Pitfalls observed**: the 2-3 second hook timeouts (`"timeout": 2` for inject-rules, `"timeout": 3` for inject-memory) are tight. On cold start with slow I/O, reading every markdown file and walking up for marketplace.json may approach the limit. No retries, no fallback.

## 10. Session context loading

- **SessionStart used for context**: yes — this is the dominant pattern in the repo. Five of eleven plugins (`auto-memory`, `better-comments`, `python-rules`, `ticket-cli`, `session-setup`) use SessionStart hooks to inject rules into the system prompt at session start.
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no — the scripts print to stdout wrapped in `<system-reminder>` blocks, relying on Claude Code's convention of capturing SessionStart stdout as an additional system message, not the newer structured `hookSpecificOutput.additionalContext` JSON channel
- **SessionStart matcher**: none on any hook — every SessionStart hook fires on all sub-events (startup, clear, compact) without a matcher filter
- **Pitfalls observed**: `session-setup` uses a raw `echo` command in the hook: `echo 'IMPORTANT: At the start of the session, before answering for the first time, execute all steps in (optional) `# Session Setup` section of CLAUDE.md'`. This fires on clear/compact too, re-prompting the agent every time context is cleared. No matcher scoping.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none
- **`{plugin-name}--v{version}` tag format observed**: not applicable — no tags at all. The three "knowledge ecosystem" plugins (`spec-driven-dev`, `project-notes`, `project-knowledge`) are coupled by convention (README describes the coordination) but there is no machine-enforced `dependencies` field.
- **Pitfalls observed**: the `project-knowledge` README explicitly says "This plugin doesn't manage any store directly – it routes to spec-driven-dev … and project-notes". A user installing only `project-knowledge` gets broken routing — and there is no `dependencies` declaration to prevent that. Coordination is documented prose, not enforced structure.

## 13. Testing and CI

- **Test framework**: pytest (only in `spec-driven-dev`)
- **Tests location**: inside plugin directory — `plugins/spec-driven-dev/tests/` with 11 test files (test_archive, test_archived, test_changes, test_computed_status, test_discovery, test_info, test_links, test_new, test_refs, test_resolve, test_validate) and a `conftest.py` fixture module. No repo-root tests, no other plugin carries tests.
- **Pytest config location**: not present — neither `pytest.ini` nor `[tool.pytest.ini_options]` in the plugin's `pyproject.toml`. Pytest relies on discovery defaults.
- **Python dep manifest for tests**: `pyproject.toml` `[dependency-groups] dev` section with `pytest>=9.0.2`
- **CI present**: no — `.github/` returns 404 on the content API
- **CI file(s)**: none
- **CI triggers**: not applicable
- **CI does**: not applicable
- **Matrix**: not applicable
- **Action pinning**: not applicable
- **Caching**: not applicable
- **Test runner invocation**: direct `pytest` (implied by conftest.py + standard layout). No `scripts/test.sh` wrapper. The `conftest.py` runs `spectl.py` as a subprocess via `sys.executable`, so tests self-locate the script relative to the test file.
- **Pitfalls observed**: `pytest>=9.0.2` is an extremely recent floor (pytest 9.x is the current generation), tightly coupled to the `requires-python = ">=3.14"` floor. No CI means the tests have no enforcement — they exist as a developer artifact only. The other ten plugins have zero tests.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable — the repo has no releases, no tags, and no CI. Versions in `plugin.json` are bumped manually and inconsistently.
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable
- **Pitfalls observed**: the per-plugin CHANGELOGs (`spec-driven-dev/CHANGELOG.md`, `theo-calvin-testing/CHANGELOG.md`, root `CHANGELOG.md`) are hand-maintained prose. Nothing verifies that CHANGELOG and `plugin.json` agree, and as noted in purpose 4, they diverge in `spec-driven-dev`.

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable — no `claude plugin validate` CLI hook, no pre-commit hook, no bun+zod or Python validator
- **Trigger**: not applicable
- **Frontmatter validation**: not applicable
- **Hooks.json validation**: not applicable
- **Pitfalls observed**: `marketplace.json` carries `$schema` (`https://anthropic.com/claude-code/marketplace.schema.json`) but no tool in-repo runs schema validation against it. Drift between plugins' intended descriptions and their recorded ones (purpose 1 pitfall) would be caught by such validation.

## 16. Documentation

- **`README.md` at repo root**: present (~2.3 KB, 38 lines — plugin index + Knowledge Ecosystem routing table)
- **Owner profile README at `github.com/a3lem/a3lem`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: mixed — 7 of 11 plugins have one (`basedpyright-lsp`, `project-knowledge`, `project-notes`, `python-rules`, `session-setup`, `spec-driven-dev`, `theo-calvin-testing`, `ticket-cli`). `auto-memory`, `better-comments`, `frontmatter` have no per-plugin README.
- **`CHANGELOG.md`**: present (rudimentary at repo root; richer per-plugin in `spec-driven-dev` and `theo-calvin-testing`). Format is ad-hoc; the `spec-driven-dev` CHANGELOG most closely resembles Keep a Changelog (versioned `## [x.y.z] - YYYY-MM-DD` headers with Added/Changed/Removed subsections).
- **`architecture.md`**: absent anywhere
- **`CLAUDE.md`**: present at repo root (short, 21 lines) and in `plugins/project-notes/` (16 lines) and `plugins/spec-driven-dev/` (workflow + layout). Not present in the other plugins.
- **Community health files**: none (no `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`)
- **LICENSE**: absent
- **Badges / status indicators**: absent
- **Pitfalls observed**: no license means technically the repo is "all rights reserved" by default — anyone cloning the marketplace has no explicit permission to reuse individual plugins beyond what GitHub's ToS provides (display/fork on the platform). For a "personal plugins" collection the author probably intends more permissive use; the gap is silent.

## 17. Novel axes

- **Inline symlink as plugin-distribution escape hatch**: the author documents a deliberate pattern in the root `CLAUDE.md` — shared utilities live in `bin/` at the marketplace root, and each consuming plugin ships a symlink (`plugins/<name>/hooks/inject-rules`) into that shared location. This is a DRY play at the marketplace level rather than copy-pasting the script per plugin. The Claude Code plugin install model copies only the plugin directory, so the symlink strategy has to survive the copy. It would work with a relative symlink target, but the committed symlinks here have absolute targets keyed to the author's machine. The axis is worth elevating to the pattern doc because it surfaces a genuine tension in the marketplace model: shared utilities vs install-time independence. Candidates for a new purpose: "Shared utility distribution — inline per-plugin / symlink / submodule / none".
- **Env-var-configured memory path instead of userConfig**: `auto-memory` honors `AUTO_MEMORY_DIR` from the env but does not declare it in `userConfig`. Demonstrates a pattern where configurability is opaque to the plugin ecosystem — a user cannot discover the toggle by reading `plugin.json` or marketplace metadata. Minor but distinct from the "documented `userConfig` surface" pattern.
- **Wrapper script as context-enrichment formatter**: `bin/inject-rules` and `inject-memory` both do work beyond simple concatenation — they look up the plugin's `name` from `plugin.json` and walk upward for the marketplace's `name`, then decorate the file path in the emitted `<system-reminder>` block with a `"path from plugin <name>@<marketplace>"` suffix. This gives the agent provenance for injected rules. Novel vs the simpler "just cat the file into the hook output" pattern seen elsewhere.
- **`allowed-prompts` agent frontmatter field**: `spec-critic.md` and `spec-sync.md` declare `allowed-prompts:` with a nested list of `{tool, prompt}` pairs. This is not a field in the Claude Code plugin reference as of the research context. Either an experimental field, a convention from another tool, or dead configuration. Worth logging as a potential axis — "plugin-specific agent frontmatter extensions" — and also as a gap: does Claude Code silently ignore it, or does some code path honor it?
- **Gherkin/EARS notation choice for specs**: `spec-driven-dev` explicitly mixes SHALL statements, Given/When/Then scenarios, and plain prose. Nowhere else in the surveyed landscape does a plugin commit to EARS/Gherkin as the spec notation. A distinctive choice, not a pattern axis per se, but a candidate cross-repo comparison for any "spec management" cluster.
- **`.lsp.json` as a single-file plugin**: `basedpyright-lsp` carries only `.claude-plugin/plugin.json`, `.lsp.json`, and a README — no skills, no commands, no hooks. Demonstrates the minimum-viable plugin surface for LSP enablement. Worth elevating: "minimum-viable plugin footprint" as a novel pattern on the discoverability axis.

## 18. Gaps

- **Actual symlink target verification**: I read the raw blob content of the per-plugin `hooks/inject-rules` files (which returns the symlink's target path for mode 120000 blobs) but did not clone the repo to observe how Claude Code's installer actually handles these during plugin install. Source that would resolve: cloning the repo with `git -c core.symlinks=true clone` and inspecting whether the symlinks resolve on a fresh checkout; or testing an actual `claude plugin install` of one of these plugins and watching whether the SessionStart hook fires.
- **`allowed-prompts` semantics**: unable to determine whether the field is honored by any Claude Code code path, ignored silently, or warned-about. Source that would resolve: the Claude Code plugin reference at https://code.claude.com/docs/en/plugins-reference (not fetched in this research) — or searching the Claude Code SDK source.
- **Whether the `plugin.json` `version` semver-lenient values (`"1.1"`) cause install-time warnings**: not tested. Source that would resolve: a real install with a Claude Code version that validates plugin.json strictly.
- **`spec-driven-dev` test pass rate**: the 11 test files are declared but not executed in this research. Source that would resolve: `cd plugins/spec-driven-dev && uv sync && pytest` on a Python 3.14 machine.
- **Why three separate versioning authorities disagree in `spec-driven-dev`**: CHANGELOG (2.1.0), plugin.json (1.0.0), SKILL.md frontmatter (3.2.0). Source that would resolve: commit-message archaeology on the three files' histories — I sampled only the last 30 commits and found the big `spec-driven-dev: rewrite` cluster on 2026-03-08 but did not trace individual version-field edits.
- **Whether the `auto-memory` plugin's memory directory walking logic is stable across symlinked workspaces or nested git repos**: code inspection suggests it walks `Path.cwd()` upward looking for `.agents/memory`, which would stop at the first match in a nested-repo scenario. Not verified in practice.
- **Marketplace-level `owner` vs per-plugin `author`**: the marketplace declares `owner: {name: "Adriaan", email: "a3lem@pm.me"}`, most but not all per-plugin `plugin.json`s carry `author: {name: "a3lem"}` (mixing display-name "Adriaan" with handle "a3lem"). Impact on install UX unknown.
