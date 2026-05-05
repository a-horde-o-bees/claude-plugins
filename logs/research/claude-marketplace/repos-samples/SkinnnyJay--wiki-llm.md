# Sample

Mirrors of `https://github.com/SkinnnyJay/wiki-llm`. Personal knowledge vault plugin for Claude Code, Cursor, and Codex — ingests, curates, and queries markdown wiki pages with CLI tooling, MCP server, knowledge graph, and session memory. Default branch `main`; MIT license; 0 stars; last commit 2026-04-14. Sample origin: bin-wrapper.

## Marketplace manifest layout

### Self-referential single-plugin marketplace at repo root

Single `.claude-plugin/marketplace.json` at repo root advertising one plugin entry whose `source` is `"./"`. A parallel `.cursor-plugin/plugin.json` also exists at repo root (Cursor Marketplace variant — same plugin, different marketplace surface). Marketplace name `llm-wiki-local`; plugin name `llm-wiki` — no reserved-name collision. The marketplace.json description explicitly frames this as a "Local marketplace for developing wiki-llm"; the catalog name `llm-wiki-local` is the user-facing suffix in `/plugin install llm-wiki@llm-wiki-local`. `metadata.{description}` wrapper present (no `version`, no `pluginRoot`). `owner.name: "local"` declared at the marketplace top level outside `metadata`. `$schema` absent.

## Plugin source binding

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry — plugin and repo root coincide. The relative source means the marketplace entry points at the full repository root, including large non-plugin assets (`docs/memory/benchmarks/`, `templates/`, `tests/`, `benchmarks/`). README notes "Local installs copy the tree into `~/.claude/plugins/cache/` (not `.gitignore`-aware)"; the plugin ships `scripts/plugin_dev_slim.sh` as a dry-run/apply helper to slim the install.

### `strict` field default

`strict` field absent — implicit true. No `skills` override on the marketplace entry.

## Per-plugin discoverability metadata

### No discoverability fields on marketplace entry

Marketplace entry exposes only `name`, `source`, `description` — no `category`, `tags`, or `keywords`. Discoverability fields (`keywords` plus Cursor-only `category` and `tags`) live in `plugin.json` / `.cursor-plugin/plugin.json` instead.

### `$schema` absence on per-plugin manifests

`$schema` absent from `plugin.json`.

## Version coordination

### Multi-file with bump script as enforcer (multi-registry)

`plugin.json.version = "0.2.0"` is the plugin version of record; marketplace entry has no version field. `.cursor-plugin/plugin.json` carries `"version": "0.2.0"` in parallel — maintained by hand without automation linking the two; both currently match. `pyproject.toml` carries an independent `version = "0.1.0"` for the Python package, decoupled from the plugin version — a reader running `pip show llm-wiki` sees a different version than the Claude plugin reports.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Only `main` branch exists; no release branches, no tags, no GitHub releases. `/plugin install llm-wiki@llm-wiki-local` resolves against whatever `main` currently is. README instructs users to run `/plugin marketplace update` to pick up upstream changes, but offers no pinning path.

## Tag and release lifecycle

### Tag-on-main, single branch

Default branch `main`. Zero tags as of 2026-04-14 — `release.yml` is a `push: tags: ['v*']` handler that exists but has never fired. The release intent is tag-on-main; no tags have been pushed yet. CHANGELOG.md shows discrete releases `0.1.13` → `0.2.0` with date stamps and an `[Unreleased]` section accumulating. `plugin.json` is manually bumped. `.pre-commit-config.yaml` runs `ruff --fix` on `scripts/` and `python3 -m compileall scripts benchmarks` — no version manipulation in pre-commit.

## Plugin-component registration

### Default convention discovery

`plugin.json` has no `skills`/`commands`/`agents`/`hooks` path arrays — Claude Code auto-discovers from standard directories. `.cursor-plugin/plugin.json` is explicit by contrast: `"rules": "rules"`, `"skills": "skills"`, `"commands": "commands"`, `"agents": "agents"`, `"hooks": "hooks/hooks.json"` — the Cursor variant names every slot. The split between Claude (defaults) and Cursor (explicit paths) for the same tree means the dual manifests must be hand-synced.

### Inline `mcpServers` definition in `plugin.json`

MCP server is declared inline in `plugin.json` (no `.mcp.json` sibling file). The MCP server is invoked with `command: "python3"` + `args: ["${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py"]`.

## Component composition

### Skills (universal)

25+ skills in `skills/`.

### Commands

21 files in `commands/`.

### Agents

3 files in `agents/`: `research-runner.md`, `wiki-librarian.md`, `wiki-raw-prepare.md`.

### Hooks

`hooks/hooks.json` declaring `PreCompact`, `Stop`, `PostCompact`, `SessionEnd` events.

### MCP servers

Inline `mcpServers` block in `plugin.json` referencing `scripts/mcp_server.py`.

### bin

One file — `bin/llm-wiki` — shell wrapper.

### Component types absent across the corpus

`.lsp.json` no, monitors no, `output-styles` no.

## Plugin-component placement

### Inside plugin directory

Components live under the plugin root: `skills/`, `commands/`, `agents/`, `hooks/`, `bin/`. Auto-discovery and `${CLAUDE_PLUGIN_ROOT}` interpolation work as designed.

## Skill authoring conventions

### Standard frontmatter

Skill frontmatter carries fields documented in CHANGELOG 0.2.0 across 25+ skills — `disable-model-invocation: true`, `user-invocable: false`, `context: fork`, `effort: high`, `allowed-tools` — applied uniformly.

## Agent declaration conventions

### Tool-restricted with orchestration knobs

Agent frontmatter uses `name`, `description`, `model` (e.g., `opus`), `effort` (e.g., `medium`), `maxTurns` (40), `disallowedTools` (e.g., `Agent`), `color`, `memory` (`project`). CHANGELOG 0.2.0 records adding `disallowedTools`, `color`, `memory`, `background` to agents. Tool syntax uses plain tool names (`disallowedTools: Agent`) — not permission-rule syntax. `settings.json` at repo root sets `"agent": "wiki-librarian"` as the default agent — a repo-level override that activates when the plugin is loaded.

## Cross-platform skill publishing

### Multi-runtime skill mirrors

Same source tree targets three agent CLIs: `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` for Claude, `.cursor-plugin/plugin.json` for Cursor, `.codex/config.toml` + `AGENTS.md` for Codex. The Cursor manifest is richer (explicit component paths, `displayName`, `publisher`, `logo`, `category`, `tags`) than Claude's (discovery-based, minimal).

## Server runtime (MCP)

### In-place stdlib script (no installer)

The MCP server is launched by `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py"` declared inline in `plugin.json`. `pyproject.toml` declares `dependencies = []` and a console script `llm-wiki = "llm_wiki_cli:main"`. Script-runtime variant: system `python3` only — no venv activation from the plugin. Optional runtime deps (Chroma, Playwright, sentence-transformers, anthropic, pdf2image, mem0ai) are listed in `requirements-optional.txt` for users to install manually.

## Bin entry mechanism

### POSIX shell wrapper with `${CLAUDE_PLUGIN_ROOT}` fallback

`bin/llm-wiki` is a single shell wrapper that `exec python3 "$ROOT/scripts/llm_wiki.py" "$@"`. Shebang is `#!/usr/bin/env sh` (POSIX sh, not bash). Runtime resolution: `ROOT="${CLAUDE_PLUGIN_ROOT:-}"; if [ -z "$ROOT" ]; then ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"; fi`. Supports both Claude-plugin invocation (env var set by Claude Code) and direct `./bin/llm-wiki` invocation from a dev clone. `CDPATH= cd --` guards against hostile `CDPATH`/filename leading dashes in the fallback branch. Permissions are 100755 (verified via git tree mode); same on `hooks/*.sh` and the repo-root `setup` script. Companion shell hook scripts use `#!/usr/bin/env bash` with `set -euo pipefail`.

### Plugin-bin + npm-bin dual-target

`pyproject.toml` declares `project.scripts = { llm-wiki = "llm_wiki_cli:main" }`, so `pip install .` produces a console script that bypasses `bin/llm-wiki` entirely. Two ways to reach the same `scripts/llm_wiki.py` (plugin bin shell wrapper vs pip console script via `llm_wiki_cli.py` at repo root), each managing `sys.path` independently. Designed for users who want the CLI outside any plugin host.

## Plugin-runtime root resolution

### Two-tier env-var-first fallback

`bin/llm-wiki` consults `${CLAUDE_PLUGIN_ROOT}` first, falling back to a script-relative computation. The fallback makes the wrapper runnable from a bare clone outside Claude Code.

## Dependency installation

### Manual venv with documented commands

Optional runtime deps live in `requirements-optional.txt` (Chroma, Playwright, sentence-transformers, anthropic, pdf2image, mem0ai). `requirements-dev.txt` lists `pytest>=8.0`. `pyproject.toml` declares `dependencies = []` and the console script. Users manually create `python3 -m venv .venv && .venv/bin/pip install -r requirements-optional.txt`. No `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PLUGIN_ROOT}` install target is scripted. `requirements-optional.txt` header reads "Optional pip deps for llm-wiki CLI (use a venv: ...)" and notes "PEP 668: on many Linux distros the system Python is 'externally managed' — do not pip install into it; use a venv (above) or pipx."

### No managed install (user prerequisite)

The project deliberately avoids dep installation. The `setup` script at repo root is a detect-and-advise stub (chmod bin, warn about `.claude/`, print next steps) — not a dep installer. Dep management is pushed entirely to the user. If the user's system `python3` lacks optional deps (Chroma, Playwright), features silently degrade (e.g., `mcp.search_backend=chromadb` falls back to grep, per CLAUDE.md).

## Install change detection

### No change detection

No hook installs deps, so no diff/sha/mtime machinery exists.

## Install trigger and lifecycle

### No managed install — pure shell/markdown

No install step fires on plugin install. The `bin/llm-wiki` shell wrapper just `exec python3 "$ROOT/scripts/llm_wiki.py"` against whatever `python3` resolves to first on PATH. The CLAUDE.md calls out a concrete Python-version landmine: "Do not rely on `PYTHONPATH=scripts` with a relative path (Python 3.14+ can break); the script adds `scripts/` to `sys.path` itself." No automated mitigation — the mitigation is documentation.

## Install failure posture

### No retry path

No install hook means no retry path; the plugin will install and load even when its CLI cannot satisfy the user's config — divergence between "plugin installed" and "plugin functional".

## User configuration and authentication

### Typed `userConfig` schema with rich field types

`userConfig` declared in `plugin.json` with three fields (`firecrawl_api_key`, `brave_search_api_key`, `perplexity_api_key`). All three flagged `sensitive: true`. Each field has `type: "string"`, `title`, `description`. No `default` values (secrets). No `required: true` — the plugin tolerates missing keys (CHANGELOG: "(optional)").

### `userConfig` declared but not wired through manifest substitution

No `${user_config.firecrawl_api_key}` or `CLAUDE_PLUGIN_OPTION_*` env-var wiring in `plugin.json`. The MCP server is declared with only `command: "python3"` + `args: ["${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py"]` — keys presumably get threaded to the CLI via environment set by Claude Code, but the wiring is implicit. Ingest adapters at `scripts/ingest/adapters/{brave_search.py, perplexity.py, web_firecrawl.py}` presumably read these from env. `userConfig` block is duplicated verbatim between `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` with no sync mechanism — drift risk identical to the version-string problem.

## Session context loading

### No SessionStart, only PreCompact / PostCompact / Stop / SessionEnd

`hooks.json` has no `SessionStart` entry. Inbound context (session start) is not loaded via hook — users scaffold/ingest on demand via slash commands. The "Memory Stack" is refreshed on `Stop` (not on session open) — the first session after a gap starts with stale wake-up context until the first Stop fires.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse hooks. No PostToolUse hooks. No PermissionRequest/PermissionDenied hooks. The hooks that exist (PreCompact, Stop, PostCompact, SessionEnd) do not enforce tool-use policy. They all end with `exit 0` unconditionally. stderr is used for "hook skipped" messages; no stdout JSON.

## Hook handler runtime

### Per-hook bash scripts with selective strict mode

Each hook is a small `.sh` script with `set -euo pipefail`. The `set -euo pipefail` combined with `|| true` on every external CLI call gives selective failure — a typo outside a command path still halts, but any CLI failure is swallowed. Stop hook reads `find $WIKI_DIR -newer $LAST_STOP -name "*.md"` for change detection; no `LAST_STOP` on first run falls through to always-process via an explicit first-run branch.

## Hook output contract

### JSON-only stdout, no stderr-human parallel

Hooks that exist do not write JSON to stdout — they exit 0 unconditionally with stderr-only "hook skipped" messages. No `systemMessage`, no `additionalContext`, no `decision` envelope.

## Hook failure posture

### Fail-open posture with explicit comment contract

Every hook begins with a one-line comment declaring the fail-open posture ("Exit code MUST be 0 always (a failing hook must not interrupt Claude)"), followed by `set -euo pipefail` + `|| true` on external calls, terminated by `exit 0`. Consistent pattern across 4 shell hooks.

## State persistence

### File-based memory stack with auto-gitignore

A "Memory Stack" file-based memory mechanism refreshed on `Stop` hooks. Stop hook tracks change detection via `find $WIKI_DIR -newer $LAST_STOP -name "*.md"`. CHANGELOG records a `.gitignore` entry for `.claude/` to prevent accidental commit (since a `.claude/` directory inside the plugin root blocks Claude Code from discovering `skills/`, per `anthropics/claude-code#44120`).

## Live monitoring

### `monitors.json` absent

No `monitors.json`, no monitor surface.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field on `plugin.json`. Single-plugin marketplace.

## Testing

### pytest with sys.path manipulation

47+ test files in `tests/` at repo root using pytest. Dedicated `pytest.ini` at repo root (not `pyproject.toml`) configures `testpaths = tests`, `python_files = *.test.py test_*.py *_test.py`, `addopts = --import-mode=importlib`, custom markers (`network`, `claude`, `codex_skill_eval`, `replay`, `browser`). Python dep manifest for tests: `requirements-dev.txt` (just `pytest>=8.0`). Test runner invocation is direct `python -m pytest tests/` with inline `PYTHONPATH=scripts`. CLAUDE.md recommends `llm-wiki smoke-test` for local use; CI uses raw pytest.

## CI workflow shape

### Multi-workflow split by trigger and concern

Three workflow files: `.github/workflows/tests.yml`, `.github/workflows/release.yml`, `.github/workflows/security.yml`. `tests.yml` triggers on `push: branches: [main, master]`, `pull_request`, `workflow_dispatch`; runs `python scripts/llm_wiki.py check --plugin-repo` (agent-docs sync check + compileall) then `pytest tests/` with `PYTHONPATH=scripts` env. Optional `browser` job (workflow_dispatch only) installs Playwright + chromium and runs `tests/test_viewer_playwright.py`. Matrix is Python versions only — `["3.12", "3.14"]` in `tests.yml`. No OS matrix. `release.yml` pins `3.12` singleton. Action pinning by tag — `actions/checkout@v4`, `actions/setup-python@v5`, `gitleaks/gitleaks-action@v2`. No SHA pinning. No caching — `setup-python@v5` defaults (no `cache:` key specified). `security.yml` runs `gitleaks/gitleaks-action@v2` on `push: branches: [main, master]` and `pull_request`. CI sets `PYTHONPATH: scripts` (relative path) as a workflow env — exactly the pattern CLAUDE.md warns against for Python 3.14+; the matrix includes 3.14, so this is a live risk.

## Marketplace validation

### Custom in-repo validator

No standalone validation workflow. `scripts/llm_wiki.py check --plugin-repo` (invoked in `tests.yml` and `release.yml`) does plugin-repo sanity — AGENTS.md / CLAUDE.md / rules sync check and `compileall`. `bin/llm-wiki sync-agent-docs --check` is the drift guard for agent docs. Custom Python validators (`scripts/llm_wiki.py check --plugin-repo` + `scripts/sync_agent_docs.py`) — no bun+zod, no `claude plugin validate` invocation in CI. Frontmatter validation not observed explicitly — skill frontmatter (`name`, `description`, `disable-model-invocation`, `user-invocable`) is asserted by content, not by a validator workflow. Hooks.json validation: no dedicated validator — Python `compileall` catches syntax issues; JSON validation of `hooks/hooks.json` is implicit (Claude Code fails at load time if malformed). `tests/test_plugin_inventory.py` and `tests/plugin_contracts.test.py` likely cover plugin contracts at test time.

## Release automation

### Tag-triggered test verification only

`release.yml` triggers on `push: tags: ['v*']`. Workflow header comment: "Optional: verify tests when a version tag is pushed (manual marketplace steps still required)." Tag-sanity gates: none — no verify-tag-on-main, no verify-tag-equals-version, no tag-format regex. Pure test-run gate. No artifact build, no `gh release create`, no draft release, no marketplace publish. Releases are created manually and none exist as of 2026-04-14. CHANGELOG.md is human-maintained in Keep a Changelog format, not parsed by CI.

## Documentation surface

### Nested `docs/` tree with map in README

Repo-root `README.md` is ~15 KB — heavy with setup instructions, install variants, usage loop, documentation map, configuration overview. Opens with banner image and three SVG badges (GitHub / Claude Code / Cursor). A `docs/` directory holds `QUICKSTART.md`, `INSTALL.md`, `INSPIRATION.md`, `CLI.md`, `CONFIGURATION.md`, `ENV.md`, `SLASH-COMMANDS.md`, `PUBLISHING.md`, `QAPLAYBOOK.md`, `ARTICLE.md`, etc. The README contains a "documentation map" table that routes readers to the right doc. README links to `docs/ARCHITECTURE.md` (uppercase) but the file is `docs/architecture.md` (lowercase) — case-sensitive filesystems will 404; GitHub's web UI is case-insensitive so the bug only surfaces on cloned trees on Linux. The architecture doc is short (~2.7 KB) with a mermaid data-flow diagram and two-products (vault vs plugin repo) table.

### Free-form CHANGELOG variants

`CHANGELOG.md` is Keep a Changelog format, SemVer-tagged (`[Unreleased]`, `[0.2.0] — 2026-04-08`, `[0.1.13] — 2026-04-05`). Hand-maintained, no automation.

## Agent-docs synchronization

### Shared block with marker-bracketed sync

`docs/AGENTS.shared.md` is the canonical shared block. `sync_agent_docs.py` propagates it into `AGENTS.md`, `CLAUDE.md`, `rules/llm-wiki.mdc` between `<!-- BEGIN AGENTS_SHARED -->` / `<!-- END AGENTS_SHARED -->` markers. CI enforces with `sync-agent-docs --check`. `bin/llm-wiki sync-agent-docs --check` is the drift guard. CLAUDE.md and AGENTS.md are kept in sync by this dedicated script.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

MIT license. SPDX `MIT`; `LICENSE` present at repo root.

## Community health files

### Bare minimum (LICENSE only)

`CONTRIBUTING.md` present. No `SECURITY.md` or `CODE_OF_CONDUCT.md`. `ETHOS.md` is a bespoke evidence/trust document; `WORKFLOWS.md` covers day-to-day ops. `AGENTS.md` for Codex. README header carries three shields.io badges (GitHub repo, Claude Code plugin, Cursor rules+plugin) — no CI status badges.

## Cross-platform discipline

### POSIX-only with no Windows story

`bin/llm-wiki` uses `#!/usr/bin/env sh` (POSIX sh, not bash). Hook scripts use `#!/usr/bin/env bash`. Runs on macOS/Linux. No `.cmd`/`.ps1` for Windows. `CDPATH= cd --` guards against hostile `CDPATH`/filename leading dashes in the fallback branch.

## Multi-runtime portability

### Triple-runtime parallel manifests

Single repo targets three agent CLIs via parallel manifests: `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` (Claude), `.cursor-plugin/plugin.json` (Cursor), `.codex/config.toml` + `AGENTS.md` (Codex). The Cursor manifest is richer (explicit component paths, `displayName`, `publisher`, `logo`, `category`, `tags`) than Claude's (discovery-based, minimal).

## Cross-ecosystem distribution

### Triple-ecosystem (Claude + Codex + Cursor)

Same git repo distributes to Claude Code, Cursor, and Codex from one tree, with per-ecosystem manifests at `.claude-plugin/`, `.cursor-plugin/`, `.codex/config.toml` plus `AGENTS.md`.

## Distribution exclusion and dogfood layout

### `.claude-plugin/ignore` exclusion list

`scripts/plugin_dev_slim.sh` (dry-run + `--apply`) is distributed in the repo specifically because `/plugin install` copies the whole tree (not `.gitignore`-aware). A plugin repo shipping a utility for slimming itself before local install — addresses the consequence of `source: "./"` copying everything. CHANGELOG records a `.gitignore` entry for `.claude/` to prevent accidental commit (a `.claude/` directory inside the plugin root blocks Claude Code from discovering `skills/`).

## Novel and cross-cutting concerns

- **Dual-ecosystem manifest in one repo with cross-runtime governance.** Ships `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` alongside `.cursor-plugin/plugin.json` + `.codex/config.toml` + `AGENTS.md`. The Cursor manifest is richer than Claude's.
- **Bin wrapper pattern with POSIX-sh + CLAUDE_PLUGIN_ROOT fallback.** `bin/llm-wiki` is six effective lines: resolve `${CLAUDE_PLUGIN_ROOT}` with a script-relative fallback, `exec python3 $ROOT/scripts/llm_wiki.py "$@"`. No venv, no activation. Uses `#!/usr/bin/env sh` (not bash) for the wrapper while companion hooks in `hooks/` use bash with `set -euo pipefail`.
- **Secondary pip-install entrypoint.** `llm_wiki_cli.py` at repo root + `pyproject.toml` `project.scripts` = `llm-wiki = "llm_wiki_cli:main"` makes `pip install .` produce a separate console script that bypasses `bin/llm-wiki`. Two ways to reach the same `scripts/llm_wiki.py`, each managing `sys.path` independently.
- **Agent-docs single-source-of-truth enforcement.** `docs/AGENTS.shared.md` is the canonical shared block; `sync_agent_docs.py` propagates it into `AGENTS.md`, `CLAUDE.md`, `rules/llm-wiki.mdc` between marker brackets. CI enforces with `sync-agent-docs --check`.
- **Plugin-dev slimming as an explicit workflow step.** `scripts/plugin_dev_slim.sh` is distributed in the repo specifically because `/plugin install` copies the whole tree.
- **Explicit `.claude/` trap documentation.** CLAUDE.md, `commands/setup.md`, and `setup` script all warn that a `.claude/` directory inside the plugin root blocks Claude Code from discovering `skills/` (linking to `anthropics/claude-code#44120`).
- **Absent-but-present `release.yml`.** A release workflow that exists, is triggered on `v*` tags, but has never fired. A declaration of intent to run tests on release without automating the release itself.
- **Mem0 / LME / LoCoMo benchmark harness shipped in-plugin.** `benchmarks/` carries a full retrieval-benchmark suite (peers like mem0, rubric overrides, fixtures) running inside the plugin's test + CLI. A plugin treating its own retrieval quality as a first-class subsystem.
- **`settings.json` at repo root sets default agent.** `{"agent": "wiki-librarian"}` activates when the plugin is loaded — a plugin-level settings override.
- **Fail-open hook convention with explicit comment contract.** Every hook begins with a one-line comment declaring the fail-open posture, followed by `set -euo pipefail` + `|| true` on external calls, terminated by `exit 0`.
- **Parallel userConfig definitions (no single source).** `userConfig` is duplicated verbatim in `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` with no sync, contrasting with `docs/AGENTS.shared.md` which does have a sync script.

## Cross-role tools

### Python (stdlib + pip + uv)

System `python3` only. `pyproject.toml` declares `dependencies = []` with `requires-python` floor implied. `requirements-optional.txt` and `requirements-dev.txt` list user-installed extras. CLAUDE.md flags Python 3.14+ landmine with relative `PYTHONPATH=scripts`.

### `${CLAUDE_PLUGIN_ROOT}` env var

`bin/llm-wiki` consults `${CLAUDE_PLUGIN_ROOT}` first, falling back to script-relative computation. Also referenced in `plugin.json`'s inline `mcpServers` block as `${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py`.

### `plugin.json.version`

Single source of truth for plugin version (`0.2.0`); marketplace entry omits version field. `.cursor-plugin/plugin.json` carries the same version in parallel.
