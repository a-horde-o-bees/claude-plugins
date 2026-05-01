# SkinnnyJay/wiki-llm

## Identification

- **URL**: https://github.com/SkinnnyJay/wiki-llm
- **Stars**: 0 (observed via `gh api repos/SkinnnyJay/wiki-llm`)
- **Last commit date**: 2026-04-14 (commit `ed52a799`; repo `pushed_at` also 2026-04-14)
- **Default branch**: `main`
- **License**: MIT (SPDX `MIT`; `LICENSE` present at repo root)
- **Sample origin**: bin-wrapper
- **One-line purpose**: "Personal knowledge vault plugin for Claude Code, Cursor, and Codex — ingest, curate, and query markdown wiki pages with CLI tooling, MCP server, knowledge graph, and session memory." (from GitHub repo description; README opening calls it a "Claude Code plugin (and a small Python CLI) that helps you keep a personal knowledge vault next to your projects.")

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root. A parallel `.cursor-plugin/plugin.json` also exists at repo root (Cursor Marketplace variant — same plugin, different marketplace surface).
- **Marketplace-level metadata**: `metadata.{description}` wrapper present (no `version`, no `pluginRoot`). Has top-level `owner.name: "local"` outside `metadata`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: none at the marketplace-entry level — the single `plugins[0]` entry has only `name`, `source`, `description`. No `category`, `tags`, or `keywords` on the marketplace entry. Discoverability fields (`keywords`, plus Cursor-only `category` and `tags`) live in `plugin.json` / `.cursor-plugin/plugin.json` instead.
- **`$schema`**: absent.
- **Reserved-name collision**: no. Plugin name `llm-wiki`; marketplace name `llm-wiki-local`.
- **Pitfalls observed**: marketplace.json description explicitly frames this as a "Local marketplace for developing wiki-llm" — the catalog name `llm-wiki-local` is the user-facing suffix in `/plugin install llm-wiki@llm-wiki-local`. Readers who expect a "public" marketplace catalog name may be surprised by the `-local` suffix.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./"`).
- **`strict` field**: default (implicit true) — the field is absent.
- **`skills` override on marketplace entry**: absent.
- **Version authority**: `plugin.json` only (`"version": "0.2.0"`). Marketplace entry has no version. `.cursor-plugin/plugin.json` also carries `"version": "0.2.0"` — maintained in parallel; drift risk between the two manifests (observed: both currently match, but no automation was found linking them).
- **Pitfalls observed**: the relative source `./` means the marketplace entry points at the repository root, not a subdirectory — the full repo becomes the plugin, including large non-plugin assets (`docs/memory/benchmarks/`, `templates/`, `tests/`, `benchmarks/`). Plugin install copies the whole tree (README calls this out: "Local installs copy the tree into `~/.claude/plugins/cache/` (not `.gitignore`-aware)" — they ship `scripts/plugin_dev_slim.sh` as a dry-run/apply helper specifically to slim the install).

## 3. Channel distribution

- **Channel mechanism**: no split (users pin via `@ref`). Only `main` branch exists; no release branches, no tags, no GitHub releases.
- **Channel-pinning artifacts**: absent.
- **Pitfalls observed**: without tags or a stable branch, `/plugin install llm-wiki@llm-wiki-local` resolves against whatever `main` currently is — no stability guarantee. README instructs users to run `/plugin marketplace update` to pick up upstream changes, but offers no pinning path.

## 4. Version control and release cadence

- **Default branch name**: `main`.
- **Tag placement**: none (zero tags on the repo as of 2026-04-14). `release.yml` is a `push: tags: ['v*']` handler that exists but has never fired — it installs deps, runs `plugin_repo` checks, runs pytest. "Optional: verify tests when a version tag is pushed (manual marketplace steps still required)."
- **Release branching**: none (tag-on-main intended, but no tags yet).
- **Pre-release suffixes**: none observed.
- **Dev-counter scheme**: absent. `plugin.json` is manually bumped; CHANGELOG.md shows discrete releases `0.1.13` → `0.2.0` with date stamps and an "[Unreleased]" section accumulating.
- **Pre-commit version bump**: no. `.pre-commit-config.yaml` runs `ruff --fix` on `scripts/` and `python3 -m compileall scripts benchmarks` — no version manipulation.
- **Pitfalls observed**: `pyproject.toml` carries `version = "0.1.0"` while `plugin.json` is `0.2.0` — two independent version spaces (Python package vs plugin) with no reconciliation. A reader running `pip show llm-wiki` sees a different version than the Claude plugin reports.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery (no `skills`/`commands`/`agents`/`hooks` path arrays in Claude `plugin.json`) — Claude Code auto-discovers from standard directories. `.cursor-plugin/plugin.json` is explicit: `"rules": "rules"`, `"skills": "skills"`, `"commands": "commands"`, `"agents": "agents"`, `"hooks": "hooks/hooks.json"` — Cursor variant names every slot.
- **Components observed**: skills (yes — 25+ in `skills/`), commands (yes — 21 in `commands/`), agents (yes — 3 in `agents/`: `research-runner.md`, `wiki-librarian.md`, `wiki-raw-prepare.md`), hooks (yes — `hooks/hooks.json` with `PreCompact`, `Stop`, `PostCompact`, `SessionEnd`), .mcp.json (no — inline `mcpServers` block in `plugin.json`), .lsp.json (no), monitors (no), bin (yes — `bin/llm-wiki`), output-styles (no).
- **Agent frontmatter fields used**: `name`, `description`, `model` (e.g. `opus`), `effort` (e.g. `medium`), `maxTurns` (40), `disallowedTools` (e.g. `Agent`), `color`, `memory` (`project`). CHANGELOG entry for 0.2.0 records adding `disallowedTools`, `color`, `memory`, `background` to agents.
- **Agent tools syntax**: plain tool names (e.g. `disallowedTools: Agent`) — not permission-rule syntax.
- **Pitfalls observed**: the split between Claude (defaults) and Cursor (explicit paths) for the same tree means dual manifests must be kept in sync by hand. `settings.json` at repo root sets `"agent": "wiki-librarian"` as the default agent — a repo-level override that users who clone may not expect to activate globally when the plugin is installed.

## 6. Dependency installation

- **Applicable**: yes — the CLI has optional runtime deps (Chroma, Playwright, sentence-transformers, anthropic, pdf2image, mem0ai) and the plugin shell hooks call `python3` and `jq`.
- **Dep manifest format**: `requirements-optional.txt` (runtime optional extras), `requirements-dev.txt` (just `pytest>=8.0`), `pyproject.toml` (declares `dependencies = []` and a console script `llm-wiki = "llm_wiki_cli:main"`).
- **Install location**: not automated at plugin-install time. Users manually create `python3 -m venv .venv && .venv/bin/pip install -r requirements-optional.txt`. No `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PLUGIN_ROOT}` install target is scripted.
- **Install script location**: not applicable — no install step fires on plugin install. `setup` script at repo root is a detect-and-advise stub (chmod bin, warn about `.claude/`, print next steps) — not a dep installer.
- **Change detection**: none — no hook installs deps, so no diff/sha/mtime machinery exists.
- **Retry-next-session invariant**: not applicable (no auto-install).
- **Failure signaling**: not applicable.
- **Runtime variant**: system `python3` only. No venv activation from the plugin, no `uv`, no `uvx`, no `pip install` during plugin runtime. The `bin/llm-wiki` shell wrapper just `exec python3 "$ROOT/scripts/llm_wiki.py"` — relies entirely on whatever `python3` resolves to first on PATH.
- **Alternative approaches**: the project deliberately avoids dep installation — `requirements-optional.txt` header reads "Optional pip deps for llm-wiki CLI (use a venv: ...)" and notes "PEP 668: on many Linux distros the system Python is 'externally managed' — do not pip install into it; use a venv (above) or pipx." The design pushes dep management entirely to the user.
- **Version-mismatch handling**: CLAUDE.md calls out a concrete Python-version landmine: "Do not rely on `PYTHONPATH=scripts` with a relative path (Python 3.14+ can break); the script adds `scripts/` to `sys.path` itself." No automated mitigation — the mitigation is documentation.
- **Pitfalls observed**: if the user's system `python3` lacks optional deps (Chroma, Playwright), features silently degrade (e.g. `mcp.search_backend=chromadb` falls back to grep, per CLAUDE.md). The plugin will install and load even when its CLI can't satisfy the user's config — divergence between "plugin installed" and "plugin functional."

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes.
- **`bin/` files**: one — `bin/llm-wiki` — shell wrapper that `exec python3 "$ROOT/scripts/llm_wiki.py" "$@"` to launch the plugin's Python CLI.
- **Shebang convention**: `#!/usr/bin/env sh` (POSIX sh, not bash). Shell hook scripts separately use `#!/usr/bin/env bash` with `set -euo pipefail`.
- **Runtime resolution**: `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback. Exact logic: `ROOT="${CLAUDE_PLUGIN_ROOT:-}"; if [ -z "$ROOT" ]; then ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"; fi; exec python3 "$ROOT/scripts/llm_wiki.py" "$@"`. Supports both Claude-plugin invocation (env var set by Claude Code) and direct `./bin/llm-wiki` invocation from a dev clone.
- **Venv handling (Python)**: no venv (system python3). Directly `exec python3`. User is expected to manage venv externally; CLAUDE.md notes `scripts/llm_wiki.py` adds `scripts/` to `sys.path` itself to avoid the `PYTHONPATH=scripts` relative-path trap on Python 3.14+.
- **Platform support**: POSIX shell — runs on macOS/Linux. No `.cmd`/`.ps1` for Windows. `CDPATH= cd --` guards against hostile `CDPATH` / filename leading dashes in the fallback branch.
- **Permissions**: 100755 on `bin/llm-wiki` (verified via git tree mode); same on all `hooks/*.sh` scripts and the repo-root `setup` script.
- **SessionStart relationship**: static — no SessionStart hook; `hooks.json` registers `PreCompact`, `Stop`, `PostCompact`, `SessionEnd` only. The bin wrapper is a committed static file.
- **Pitfalls observed**: POSIX `sh` shebang means the wrapper is safe from bashisms (it has none), but users expecting `bash -e` behavior won't get it. Secondary Python entry point `llm_wiki_cli.py` at repo root duplicates the `sys.path` fixup — it's declared in `pyproject.toml` as `project.scripts` for `pip install` consumers (separate path from plugin install). Two independent entrypoints (`bin/llm-wiki` shell wrapper vs `llm_wiki_cli:main` pip console script) reach the same underlying `scripts/llm_wiki.py`.

## 8. User configuration

- **`userConfig` present**: yes.
- **Field count**: 3 (`firecrawl_api_key`, `brave_search_api_key`, `perplexity_api_key`). All three API keys.
- **`sensitive: true` usage**: correct — all three secrets flagged `sensitive: true`.
- **Schema richness**: typed — each field has `type: "string"`, `title`, `description`, `sensitive`. No `default` values (secrets).
- **Reference in config substitution**: not observed in `plugin.json`. The MCP server is declared with only `command: "python3"` + `args: ["${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py"]` — no `${user_config.firecrawl_api_key}` or `CLAUDE_PLUGIN_OPTION_*` env var wiring visible in the plugin manifest. The keys presumably get threaded to the CLI via environment set by Claude Code, but the wiring is implicit. Ingest adapters at `scripts/ingest/adapters/{brave_search.py, perplexity.py, web_firecrawl.py}` presumably read these from env.
- **Pitfalls observed**: `userConfig` is duplicated verbatim between `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json` with no sync mechanism — divergence risk identical to the version-string problem in §2. No `required: true` or validation — the plugin must tolerate missing keys (which it does, per CHANGELOG: "(optional)").

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable — the hooks that exist (PreCompact, Stop, PostCompact, SessionEnd) do not enforce tool-use policy. They all end with `exit 0` unconditionally. stderr is used for "hook skipped" messages; no stdout JSON.
- **Failure posture**: fail-open — every shell hook is explicit: comment in `llm_wiki_precompact.sh` reads "Exit code MUST be 0 always (a failing hook must not interrupt Claude)." Every CLI invocation inside the hooks is suffixed `|| true`.
- **Top-level try/catch wrapping**: not applicable (shell scripts, not Python handlers). Shell-level defense: `set -euo pipefail` + `|| true` on each external call, final `exit 0`.
- **Pitfalls observed**: the `set -euo pipefail` combined with `|| true` on every CLI call gives selective failure — a typo outside a command call path would still halt, but any CLI failure is swallowed. Stop hook reads `find $WIKI_DIR -newer $LAST_STOP -name "*.md"` for change detection; no `LAST_STOP` on first run falls through to always-process (explicit first-run branch).

## 10. Session context loading

- **SessionStart used for context**: no — `hooks.json` has no `SessionStart` entry at all.
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: no.
- **SessionStart matcher**: not applicable (no SessionStart hook).
- **Pitfalls observed**: none from the hook shape itself, but the plugin relies on `Stop` + `PostCompact` + `SessionEnd` + `PreCompact` exclusively for context hygiene. Inbound context (session start) is not loaded via hook — users scaffold/ingest on demand via slash commands. Parts of the doc describe a "Memory Stack" that is refreshed on `Stop` (not on session open) — the first session after a gap starts with stale wake-up context until the first Stop fires.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace; no tags on the repo at all).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: pytest.
- **Tests location**: `tests/` at repo root (47+ test files).
- **Pytest config location**: dedicated `pytest.ini` at repo root (not `pyproject.toml`). Configures `testpaths = tests`, `python_files = *.test.py test_*.py *_test.py`, `addopts = --import-mode=importlib`, custom markers (`network`, `claude`, `codex_skill_eval`, `replay`, `browser`).
- **Python dep manifest for tests**: `requirements-dev.txt` (just `pytest>=8.0`).
- **CI present**: yes.
- **CI file(s)**: `.github/workflows/tests.yml`, `.github/workflows/release.yml`, `.github/workflows/security.yml`.
- **CI triggers**: `tests.yml` — `push: branches: [main, master]`, `pull_request`, `workflow_dispatch`. `release.yml` — `push: tags: ['v*']`. `security.yml` — `push: branches: [main, master]`, `pull_request`.
- **CI does**: `tests.yml` runs `python scripts/llm_wiki.py check --plugin-repo` (agent-docs sync check + compileall) then `pytest tests/` with `PYTHONPATH=scripts` env. Optional `browser` job installs Playwright + chromium and runs `tests/test_viewer_playwright.py` (workflow_dispatch only). `security.yml` runs `gitleaks/gitleaks-action@v2`. `release.yml` runs the same checks + pytest on tag push.
- **Matrix**: Python versions only — `["3.12", "3.14"]` in `tests.yml`. No OS matrix. `release.yml` pins `3.12` singleton.
- **Action pinning**: tag — `actions/checkout@v4`, `actions/setup-python@v5`, `gitleaks/gitleaks-action@v2`. No SHA pinning.
- **Caching**: none — `setup-python@v5` defaults (no `cache:` key specified).
- **Test runner invocation**: direct `python -m pytest tests/` with inline `PYTHONPATH=scripts`. CLAUDE.md recommends `llm-wiki smoke-test` for local use; CI uses raw pytest.
- **Pitfalls observed**: CI sets `PYTHONPATH: scripts` (relative path) as a workflow env — exactly the pattern CLAUDE.md warns against for Python 3.14+ ("relative `PYTHONPATH` can crash Python 3.14+ at startup; the script adds `scripts/` to `sys.path` automatically"). The matrix includes 3.14, so this is a live risk if the warning materializes. Also: `pytest.ini` `python_files` includes both `*.test.py` and `test_*.py` — matches the mixed naming in `tests/`.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes (partial — tag-verification only, no artifact build or GitHub-release creation).
- **Release trigger**: `push: tags: ['v*']`.
- **Automation shape**: tag-sanity + test verification only. No artifact build, no `gh release create`, no draft release, no marketplace publish. Workflow header comment: "Optional: verify tests when a version tag is pushed (manual marketplace steps still required)."
- **Tag-sanity gates**: none — no verify-tag-on-main, no verify-tag-equals-version, no tag-format regex. Pure test-run gate.
- **Release creation mechanism**: none — releases are created manually (and none exist as of 2026-04-14).
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: no — CHANGELOG.md is human-maintained in Keep a Changelog format, not parsed by CI.
- **Pitfalls observed**: without a tag-on-main guard or version-match check, a tag pushed from an arbitrary commit would still pass (tests assumed green). The design explicitly defers marketplace publishing to manual steps.

## 15. Marketplace validation

- **Validation workflow present**: no standalone workflow. `scripts/llm_wiki.py check --plugin-repo` (invoked in `tests.yml` and `release.yml`) does some plugin-repo sanity — AGENTS.md / CLAUDE.md / rules sync check and `compileall` — but not a marketplace-JSON schema validator. `bin/llm-wiki sync-agent-docs --check` is the drift guard for agent docs.
- **Validator**: custom Python (`scripts/llm_wiki.py check --plugin-repo` + `scripts/sync_agent_docs.py`). No bun+zod, no `claude plugin validate` invocation in CI.
- **Trigger**: runs on every `push` + `pull_request` via `tests.yml`, plus on tag via `release.yml`.
- **Frontmatter validation**: not observed explicitly — skill frontmatter (`name`, `description`, `disable-model-invocation`, `user-invocable`) is asserted by content, not by a validator workflow.
- **Hooks.json validation**: no dedicated validator — Python `compileall` catches syntax issues in `scripts/`, but JSON validation of `hooks/hooks.json` is implicit (Claude Code fails at load time if malformed).
- **Pitfalls observed**: `tests/test_plugin_inventory.py` and `tests/plugin_contracts.test.py` likely cover plugin contracts at test time (not separately verified here). Documentation suggests README tells users to run `claude plugin validate /path/to/wiki-llm` manually.

## 16. Documentation

- **`README.md` at repo root**: present — ~15 KB, heavy with setup instructions, install variants, usage loop, documentation map, configuration overview. Opens with banner image and three SVG badges (GitHub / Claude Code / Cursor).
- **Owner profile README at `github.com/SkinnnyJay/SkinnnyJay`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: not applicable (single-plugin repo; root README covers the plugin).
- **`CHANGELOG.md`**: present — Keep a Changelog format, SemVer-tagged (`[Unreleased]`, `[0.2.0] — 2026-04-08`, `[0.1.13] — 2026-04-05`).
- **`architecture.md`**: at repo root in form of `docs/architecture.md` (also referenced as `docs/ARCHITECTURE.md` in README — case mismatch pitfall; file on disk is lowercase). Short (~2.7 KB) with a mermaid data-flow diagram and two-products (vault vs plugin repo) table.
- **`CLAUDE.md`**: at repo root. Mirrors `AGENTS.md` (content synced via `bin/llm-wiki sync-agent-docs` from `docs/AGENTS.shared.md`). Contains tool-specific sections for Claude / Cursor / Codex.
- **Community health files**: `CONTRIBUTING.md` present. No `SECURITY.md` or `CODE_OF_CONDUCT.md` observed. `ETHOS.md` is a bespoke evidence/trust document, `WORKFLOWS.md` covers day-to-day ops. `AGENTS.md` for Codex.
- **LICENSE**: present (MIT).
- **Badges / status indicators**: observed — three shields.io badges in README header (GitHub repo, Claude Code plugin, Cursor rules+plugin). No CI status badges.
- **Pitfalls observed**: README links to `docs/ARCHITECTURE.md` (uppercase) but the file is `docs/architecture.md` (lowercase) — case-sensitive filesystems will 404; GitHub's web UI is case-insensitive so the bug only surfaces on cloned trees on Linux. Documentation is heavily nested (`docs/QUICKSTART.md`, `docs/INSTALL.md`, `docs/INSPIRATION.md`, `docs/CLI.md`, `docs/CONFIGURATION.md`, `docs/ENV.md`, `docs/SLASH-COMMANDS.md`, `docs/PUBLISHING.md`, `docs/QAPLAYBOOK.md`, `docs/ARTICLE.md`, etc.) — rich, but the "documentation map" table in README is needed to navigate. `AGENTS.md` and `CLAUDE.md` are kept in sync by a dedicated `sync_agent_docs.py` with a `--check` mode enforced in CI.

## 17. Novel axes

- **Dual-ecosystem manifest in one repo** — ships `.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json` alongside `.cursor-plugin/plugin.json` + `.codex/config.toml` + `AGENTS.md`, targeting three agent CLIs from a single tree. The Cursor manifest is richer (explicit component paths, `displayName`, `publisher`, `logo`, `category`, `tags`) than Claude's (discovery-based, minimal). This is a cross-ecosystem distribution pattern distinct from the more common single-ecosystem layouts.
- **Bin wrapper pattern with POSIX-sh + CLAUDE_PLUGIN_ROOT fallback** — `bin/llm-wiki` is six effective lines: resolve `${CLAUDE_PLUGIN_ROOT}` with a script-relative fallback, `exec python3 $ROOT/scripts/llm_wiki.py "$@"`. No venv, no activation. Commented: "Resolve plugin root when invoked from PATH (Claude sets CLAUDE_PLUGIN_ROOT)." The fallback makes the same script work from a bare clone without Claude Code loading it. Notable: uses `#!/usr/bin/env sh` (not bash) for the wrapper, while the companion hooks in `hooks/` use bash with `set -euo pipefail`.
- **Secondary pip-install entrypoint** — `llm_wiki_cli.py` at repo root + `pyproject.toml` `project.scripts` = `llm-wiki = "llm_wiki_cli:main"` makes `pip install .` produce a separate console script that bypasses `bin/llm-wiki` entirely. Two ways to reach the same `scripts/llm_wiki.py` (plugin bin vs pip console script), each managing `sys.path` independently. Designed for users who want the CLI outside any plugin host.
- **Agent-docs single-source-of-truth enforcement** — `docs/AGENTS.shared.md` is the canonical shared block; `sync_agent_docs.py` propagates it into `AGENTS.md`, `CLAUDE.md`, `rules/llm-wiki.mdc` between `<!-- BEGIN AGENTS_SHARED -->` / `<!-- END AGENTS_SHARED -->` markers. CI enforces with `sync-agent-docs --check`. This pattern is a generalized answer to the "CLAUDE.md vs AGENTS.md drift" problem.
- **Plugin-dev slimming as an explicit workflow step** — `scripts/plugin_dev_slim.sh` (dry-run + `--apply`) is distributed in the repo specifically because `/plugin install` copies the whole tree (not `.gitignore`-aware). This is unusual: a plugin repo shipping a utility for slimming itself before local install.
- **Explicit `.claude/` trap documentation** — CLAUDE.md, `commands/setup.md`, and `setup` script all prominently warn that a `.claude/` directory inside the plugin root blocks Claude Code from discovering `skills/` (linking to `anthropics/claude-code#44120`). The CHANGELOG records a `.gitignore` entry for `.claude/` to prevent accidental commit. This is ecosystem scar tissue worth capturing.
- **Absent-but-present `release.yml`** — a release workflow that exists, is triggered on `v*` tags, but has never fired (no tags ever pushed). It's a declaration of intent to run tests on release without automating the release itself. Distinct from repos that either fully automate releases or omit the workflow.
- **Mem0 / LME / LoCoMo benchmark harness shipped in-plugin** — `benchmarks/` has a full retrieval-benchmark suite (peers like mem0, rubric overrides, fixtures) that runs inside the plugin's test + CLI. Novel: a plugin that treats its own retrieval quality as a first-class subsystem with benchmarks, not just features.
- **`settings.json` at repo root** — `{"agent": "wiki-librarian"}` sets a default agent; a plugin-level settings override that activates when the plugin is loaded.
- **Fail-open hook convention with explicit comment contract** — every hook begins with a one-line comment declaring the fail-open posture ("Exit code MUST be 0 always (a failing hook must not interrupt Claude)"), followed by `set -euo pipefail` + `|| true` on external calls, terminated by `exit 0`. Consistent pattern across 4 shell hooks.
- **Parallel userConfig definitions (no single source)** — `userConfig` is duplicated verbatim in `.claude-plugin/plugin.json` and `.cursor-plugin/plugin.json`. No sync — divergence is a latent problem. Contrast with `docs/AGENTS.shared.md` which does have a sync script. Candidate for a shared-config-block pattern.

## 18. Gaps

- **MCP server internals** — `scripts/mcp_server.py` not fetched (would confirm how `userConfig` keys reach the server; env var name convention unclear). Source: raw.githubusercontent.com file.
- **How `userConfig` values propagate to adapters** — the Python ingest adapters (`scripts/ingest/adapters/{brave_search, perplexity, web_firecrawl}.py`) not fetched; can't confirm whether they read env-var names that Claude Code injects from `userConfig`, or whether users must also set them in `.env`. The `.env.example` file exists but was not fetched. Source: raw file fetch.
- **Plugin-contract tests** — `tests/plugin_contracts.test.py` and `tests/test_plugin_inventory.py` could validate manifest shape, but their content wasn't fetched. Source: raw file fetch.
- **`check --plugin-repo` implementation** — invoked by CI (`scripts/llm_wiki.py check --plugin-repo`) but the actual check logic (agent-docs sync, compileall, anything else) lives inside `scripts/cli/ops_commands.py` or similar — not fetched. Source: raw fetch of that CLI module.
- **Cursor marketplace submission status** — `.cursor-plugin/plugin.json` implies a Cursor Marketplace target, but whether the plugin is actually published there (vs. just prepared) was not checked. Source: Cursor Marketplace API or website.
- **`commands/*.md` frontmatter shape beyond `setup.md`** — only `setup.md` was read; whether other commands use `$ARGUMENTS`, `argument-hint`, `allowed-tools`, etc. uniformly was inferred from the 0.2.0 CHANGELOG entry, not verified per-command. Source: raw fetch of individual command files.
- **Skill frontmatter uniformity** — only `skills/wiki-setup/SKILL.md` frontmatter was read. CHANGELOG 0.2.0 references `disable-model-invocation: true`, `user-invocable: false`, `context: fork`, `effort: high`, `allowed-tools` — applied across 25+ skills. Spot-check not performed. Source: raw fetch per-skill.
- **`.codex/config.toml` content** — file exists (354 bytes) but not fetched; defines Codex knobs for the repo. Source: raw fetch.
- **`rules/llm-wiki.mdc` content** — Cursor rules file, presumably the mirror of the shared agent block, but not fetched. Source: raw fetch.
- **Actual `python3` resolution in Claude Code plugin env** — whether `CLAUDE_PLUGIN_ROOT` environments inject a preferred python or fall through to system would clarify the venv-free runtime risk. Source: Claude Code plugin runtime docs (partially covered in `docs-plugins-reference.md`).
- **Whether the plugin works when installed from the relative `source: "./"`** — the `llm-wiki-local` marketplace name suggests local development is the primary install story; remote `/plugin marketplace add https://github.com/SkinnnyJay/wiki-llm` then `/plugin install llm-wiki@llm-wiki-local` is the README-documented path, but with `source: "./"`, it's unclear whether Claude Code actually resolves that correctly from the remote fetch. Source: live test or Claude Code plugin resolution source.
