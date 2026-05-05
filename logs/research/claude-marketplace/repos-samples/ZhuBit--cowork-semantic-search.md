# Sample

Mirrors of `https://github.com/ZhuBit/cowork-semantic-search`. Local semantic search plugin for indexing folders of PDFs, Word docs, and markdown via embeddings, then asking questions in English or German with source citations. AGPL-3.0-or-later, default branch `main`, 26 stars, last commit 2026-03-24; sample origin: dep-management.

## Marketplace manifest layout

### No marketplace manifest (plugin source repo only)

No `.claude-plugin/marketplace.json` at repo root (HTTP 404 from `gh api repos/ZhuBit/cowork-semantic-search/contents/.claude-plugin/marketplace.json`). The repo ships a single-plugin `.claude-plugin/plugin.json` intended to be consumed via direct git clone + manual MCP registration, not as a marketplace. The `.claude-plugin/plugin.json` exists but without a `marketplace.json` the plugin cannot be installed by `/plugin marketplace add` workflows. Repo functions as a "plugin in a repo" — users install via `git clone` + manual `.mcp.json` config per the README.

## Plugin source binding

### Direct git install (no marketplace.json in source repo)

No marketplace manifest means no source binding entries. Installation is out-of-band: README's `git clone` plus manual `.mcp.json` template paste with absolute paths in the user's own project root.

## Per-plugin discoverability metadata

### Keywords-only on plugin.json

`plugin.json` carries `keywords: ["search", "rag", "documents", "semantic", "pdf", "local"]`. No `category` or `tags`. No `$schema`. Plugin name `semantic-search` is not a reserved name.

### Repo-level GitHub topics

11 GitHub repository topics declared on the GitHub repo itself: `claude-code`, `mcp`, `mcp-server`, `semantic-search`, `rag`, etc. Drives GitHub search but not Claude Code's marketplace UI.

## Version coordination

### Dual-file version (manifest pair)

`plugin.json` (`version: 0.1.0`) and `pyproject.toml` (`version = "0.1.0"`) — two sources that must be kept in sync manually. No automated sync. Drift risk if only one is bumped. Tag `v0.1.0` matches `plugin.json` version `0.1.0` — coincidence-by-discipline so far; no sanity check automation confirms this.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

Single `main` branch, single `v0.1.0` tag. No stable/latest split, no release channels. Without a marketplace manifest, channel concepts don't apply at the marketplace layer. Consumers pin by cloning a specific ref manually.

## Tag and release lifecycle

### Tag-on-main, single branch

Sole tag `v0.1.0` points at a commit on `main` (the only branch). `gh api repos/.../branches` returns only `main`. No release branches. No pre-release suffixes. No dev-counter scheme. Pre-commit hooks are absent — no `.githooks/`, no `.pre-commit-config.yaml`. First release only, so cadence patterns aren't established.

## Plugin-component registration

### Default convention discovery

`plugin.json` has only `name`, `version`, `description`, `author`, `keywords`. No explicit component path arrays; Claude Code auto-discovers `commands/`, `hooks/`, `skills/`, etc. at their conventional directory names.

### `.mcp.json` sibling file

`.mcp.json` lives at repo root, NOT at `.claude-plugin/.mcp.json`. The committed file hardcodes absolute paths to the author's local Mac (`/Users/<author>/Projects/OtherProjects/cowork-sematic-search/...`) — note the typo: `sematic` vs `semantic` — the author's local dir differs from the repo name. This file cannot be the plugin's MCP registration on any other machine; the README's actual install instructions tell users to paste a templated `.mcp.json` into their own project root with their own absolute paths. The repo-root `.mcp.json` is therefore the author's local dev config committed by accident, not a plugin-distribution artifact.

## Component composition

### Skills (universal)

`skills/index.md` — a single skill file at the skills/ root with command-style frontmatter (`name: index`, `description: ...`, `argument-hint: ...`). This is non-canonical placement — skills normally live in subdirectories as `skills/<name>/SKILL.md`. The file is more plausibly a slash command placed in the wrong directory, or the repo intends skills-as-files; content is minimal either way. It duplicates `commands/index.md` in purpose, suggesting either unused skill scaffolding or misunderstanding of the skill-vs-command split.

### Commands

`commands/index.md` — slash-command frontmatter (`name: index`, `description: "Index a folder of documents for semantic search"`, `argument-hint: "<folder path>"`); body instructs Claude to call the `index_folder` MCP tool.

### Hooks

`hooks/hooks.json` registers one `SessionStart` hook invoking `bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh`.

### MCP servers

`.mcp.json` at repo root (NOT at `.claude-plugin/.mcp.json` as the plugin spec expects). Combined with the absolute paths it carries, this is a leaked dev file rather than a plugin-distribution artifact.

## Dependency installation

### SessionStart-driven Python venv with hash gating

A SessionStart shell hook runs `scripts/setup.sh` to create `${CLAUDE_PLUGIN_DATA}/venv` via stdlib `python3 -m venv`, upgrade pip, and `pip install -r requirements.txt`. Both `requirements.txt` and `pyproject.toml` exist at repo root with overlapping dependency sets — `requirements.txt` is what `setup.sh` installs, `pyproject.toml` is what `pip install -e ".[all]"` uses per the README. Edits to `pyproject.toml` (e.g., adding a package under `[project.optional-dependencies]`) do NOT trigger reinstall. Runtime is system `python3` (no version pin). Memory file notes "Python 3.13 required" but `setup.sh` makes no version check; if `python3` points at 3.9 the install succeeds but some dependencies (e.g., sentence-transformers wheels) may break at runtime. Change detection via sha256:

1. `CURRENT_HASH=$(shasum -a 256 "$REQ_FILE" | cut -d ' ' -f 1)` — hash of `requirements.txt`.
2. `STORED_HASH=$(cat "$REQ_HASH_FILE")` if file exists at `${CLAUDE_PLUGIN_DATA}/requirements.hash`; empty string otherwise.
3. Condition `[ "$CURRENT_HASH" != "$STORED_HASH" ] || [ ! -d "$VENV_DIR" ]` gates the install block. On mismatch OR missing venv, run `python3 -m venv "$VENV_DIR"`, upgrade pip, `pip install -r "$REQ_FILE"`, then write `echo "$CURRENT_HASH" > "$REQ_HASH_FILE"` only after successful install.

`set -e` at top of script means any failed command aborts before the hash-file write, so the stored hash never updates on failure and the next session retries. However, the half-built venv directory IS created by `python3 -m venv` before pip runs — subsequent runs will take the `[ ! -d "$VENV_DIR" ]` path as false, relying on the hash mismatch alone. No explicit `rm -rf "$VENV_DIR"` on failure, so a partially-populated venv survives. No `set -u`, no `set -o pipefail`. No JSON/stderr emission — errors surface via whatever pip/venv printed to stderr. No `systemMessage` or `continue: false` JSON output. The chosen tool `shasum -a 256` (BSD/macOS convention) is used rather than `sha256sum` (Linux convention) or a Python one-liner — no fallback. On some Linux distributions `shasum` is absent even when `sha256sum` is present, which would cause `set -e` to abort with "command not found" before the hash comparison even runs.

The hash is over the declared-dependency manifest (`requirements.txt`) rather than a pinned lock — changes to transitive deps (e.g., a new sentence-transformers patch released) are invisible to the hash; only edits to `requirements.txt` itself trigger reinstall. No sentinel marking "install succeeded" apart from the hash-file write. Hash file is written only after the final `pip install`; if the hook is killed (SIGTERM) between pip finishing and the echo, the hash file stays stale and the next session reinstalls redundantly.

## Bin entry mechanism

### No bin entry / direct invocation

The plugin's runtime entry point is the MCP server launched by the host's MCP config (`python -m server.main`), not a `bin/` wrapper. No `bin/` directory present. The MCP registration in README points into `{plugin-checkout}/.venv/bin/python`, which is created by `pip install -e ".[all]"` per README — NOT by the plugin's `setup.sh` (which creates a venv under `${CLAUDE_PLUGIN_DATA}/venv`, a different location). Two parallel venv setups exist: one for README "install-from-source" users and one for anyone who treats this as a plugin. Neither path is connected to the other; the SessionStart-managed venv is never referenced by the running MCP server.

## Server runtime (MCP)

### Local venv built by SessionStart hook

The MCP server is launched against the README-documented checkout-local `.venv/bin/python`, which is built by `pip install -e ".[all]"` during the README's "Install from source" flow. The plugin's own SessionStart hook builds a parallel venv at `${CLAUDE_PLUGIN_DATA}/venv` that is never referenced at MCP launch — two parallel venvs, neither aware of the other. The hook's install effort is therefore unused at runtime. System-tool dependency on `shasum` (BSD/macOS) vs `sha256sum` (Linux) — no fallback observed.

## User configuration and authentication

### No userConfig, env-var only

`plugin.json` has no `userConfig` block. The MCP server accepts `LANCEDB_PATH` via OS env var (read inside `server/main.py` and `server/indexer.py` via `os.environ.get("LANCEDB_PATH", "./lancedb")`). Database path is configurable only via OS env var; not surfaced through `plugin.json` `userConfig`, so Claude Code's config UI cannot manage it.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse, PostToolUse, or PermissionRequest/PermissionDenied hooks. The only hook is SessionStart for dep install.

## Session context loading

### Dependency install only (no context emission)

SessionStart is used only for dep install. No matcher is declared in `hooks.json`, so the hook fires on all SessionStart sub-events (startup, clear, compact, etc.). `setup.sh` emits no JSON and does not populate `additionalContext`. Dep install on every startup is acceptable because the hash check makes it a no-op; but re-running on `compact` is wasted setup effort.

## Live monitoring

### `monitors.json` absent

No `monitors.json`. No monitors, no `when` values, no version-floor declaration.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `dependencies` field in `plugin.json`. Single-plugin repo; tag is `v0.1.0` (plain semver, no plugin-name prefix).

## Testing

### Pytest with asyncio support

Test framework: pytest. Tests at `tests/` at repo root (flat: `test_chunker.py`, `test_indexer.py`, `test_mcp_tools.py`, `test_parsers.py`, `test_search.py`, `test_store.py`, plus `helpers.py` and `__init__.py`). README claims "56 tests covering parsers, chunking, indexing, search, and MCP tool integration." `[tool.pytest.ini_options]` in `pyproject.toml` with `pythonpath = ["."]`. No separate `pytest.ini`. Python dep manifest for tests: `pyproject.toml` `[project.optional-dependencies] dev = ["pytest>=8.0"]`; `requirements.txt` also lists `pytest>=8.0` as a top-level dep. Test runner invocation is direct `pytest tests/ -v` per README. No wrapper script.

## CI workflow shape

### No CI

No `.github/` directory at all (`gh api repos/.../contents/.github` → 404). All testing is local/manual per the README ("source .venv/bin/activate; pytest tests/ -v"). No enforcement of the 56-test claim on PRs; regressions caught only if the author runs pytest locally before committing.

## Marketplace validation

### No validation

No CI, no marketplace.json to validate, no validator. Frontmatter on `commands/index.md` and `skills/index.md` is unvalidated. No hooks.json schema validation.

## Release automation

### No release automation / manual

No `.github/workflows/` directory. The sole release (`v0.1.0`) was created manually via `gh release create` or the GitHub UI. No automation verifies tag matches `plugin.json` version. No CHANGELOG.md in repo. First release is a single tag with title "v0.1.0 — Initial Release"; no changelog, no release body parser, no automated verification that `plugin.json.version` equals tag.

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

`README.md` at repo root (~8.8 KB) is extensive: why, features, supported formats, multi-client install instructions (Claude Code / Cursor / Windsurf / Cline), usage examples, architecture diagram, roadmap, license. Single-plugin repo; the root README serves the plugin. Architecture is inlined as a section in the main README (directory diagram + component-choice table) — no separate `architecture.md`. `CLAUDE.md` is absent at repo root; `memory/project_cowork_rag_plugin.md` (under a `memory/` dir) carries project context, and `memory/MEMORY.md` indexes it — this is an earlier Claude Code "memory" convention rather than current `CLAUDE.md` project guidance. `CHANGELOG.md` is absent.

### Shipped planning corpus visible in public repo

`IMPLEMENTATION_PLAN.md` (~44 KB) at repo root — a planning doc committed alongside shipped code. `memory/` directory committed into the repo, making the author's project memory public — content is benign but exposes planning, phase notes, and absolute paths (`/Users/<author>/...`). Not sensitive but unusual to ship in a public plugin repo.

### Badges and status indicators

README opens with 4 shields.io badges: GitHub stars, Python 3.11+, License AGPL-3.0, MCP Compatible.

## License declaration

### LICENSE file present + SPDX in manifests (single source agreement)

LICENSE file present at repo root (AGPL-3.0-or-later); SPDX identifier `AGPL-3.0` in plugin metadata. README references the same.

## Community health files

### Community health files absent

No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md` observed in root contents listing.

## Cross-ecosystem distribution

### Cross-ecosystem multi-harness distribution

README provides per-client `.mcp.json` templates for Claude Code, Cursor, Windsurf, and Cline — each with the same server definition but slightly different config file paths. The plugin is explicitly marketed as MCP-portable, not Claude Code-specific; the `.claude-plugin/plugin.json` becomes secondary to the manual MCP config. This is a "hybrid plugin": ships plugin metadata for Claude Code's plugin system but the primary install path is via whichever MCP host the user runs.

