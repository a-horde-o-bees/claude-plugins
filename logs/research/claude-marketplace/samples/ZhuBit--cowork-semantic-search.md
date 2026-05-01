# ZhuBit/cowork-semantic-search

## Identification

- **URL**: https://github.com/ZhuBit/cowork-semantic-search
- **Stars**: 26
- **Last commit date**: 2026-03-24 (commit `aec520e5`)
- **Default branch**: main
- **License**: AGPL-3.0-or-later (SPDX: AGPL-3.0; LICENSE file present)
- **Sample origin**: dep-management
- **One-line purpose**: "Search your local documents with natural language. Index folders of PDFs, Word docs, markdown, and more — then ask questions in English or German and get answers with source citations." (from `plugin.json` description; README opens with "Local semantic search for your documents. No API keys. No cloud. Works with any MCP client.")

## 1. Marketplace discoverability

- **Manifest layout**: none — no `.claude-plugin/marketplace.json` at repo root (observed HTTP 404 from `gh api repos/ZhuBit/cowork-semantic-search/contents/.claude-plugin/marketplace.json`). The repo ships a single-plugin `plugin.json` intended to be consumed via direct clone + MCP registration, not as a marketplace.
- **Marketplace-level metadata**: not applicable — no marketplace manifest exists.
- **`metadata.pluginRoot`**: not applicable — no marketplace manifest.
- **Per-plugin discoverability**: `keywords` only — `plugin.json` carries `keywords: ["search", "rag", "documents", "semantic", "pdf", "local"]`. No `category` or `tags`. Repo-level GitHub topics include `claude-code`, `mcp`, `mcp-server`, `semantic-search`, `rag` etc. (11 topics) but those are GitHub discovery, not marketplace discovery.
- **`$schema`**: absent in `plugin.json`.
- **Reserved-name collision**: no — plugin name is `semantic-search` (not a reserved name).
- **Pitfalls observed**: Repo functions as a "plugin in a repo" with no marketplace wrapping; users install via git clone + manual MCP config per the README. The `.claude-plugin/plugin.json` exists but without a marketplace.json the plugin cannot be installed by `/plugin marketplace add` workflows.

## 2. Plugin source binding

- **Source format(s) observed**: not applicable — no marketplace manifest means no source binding entries. Installation is out-of-band (README's `git clone` + manual `.mcp.json` edit with absolute paths).
- **`strict` field**: not applicable — no marketplace entry to carry `strict`.
- **`skills` override on marketplace entry**: not applicable — no marketplace entry.
- **Version authority**: `plugin.json` only (`version: 0.1.0`); also echoed in `pyproject.toml` (`version = "0.1.0"`) — two sources that must be kept in sync manually.
- **Pitfalls observed**: `plugin.json` version and `pyproject.toml` version are duplicated with no automated sync. Drift risk if only one is bumped.

## 3. Channel distribution

- **Channel mechanism**: no split — single `main` branch, single `v0.1.0` tag.
- **Channel-pinning artifacts**: absent — no stable/latest split, no release channels.
- **Pitfalls observed**: Without a marketplace manifest, channel concepts don't apply at the marketplace layer. Consumers pin by cloning a specific ref manually.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: on main — sole tag `v0.1.0` points at a commit on `main` (the only branch). `gh api repos/.../branches` returns only `main`.
- **Release branching**: none (tag-on-main).
- **Pre-release suffixes**: none observed.
- **Dev-counter scheme**: absent.
- **Pre-commit version bump**: no — no `.githooks/`, no `.pre-commit-config.yaml`, no `.github/` workflows found.
- **Pitfalls observed**: Tag `v0.1.0` matches `plugin.json` version `0.1.0` — no sanity check automation confirms this; coincidence-by-discipline so far. First release only, so cadence patterns aren't established.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` has only `name`, `version`, `description`, `author`, `keywords`. No explicit component path arrays; Claude Code auto-discovers `commands/`, `hooks/`, `skills/`, etc. at their conventional directory names.
- **Components observed**:
  - skills: yes (`skills/index.md` — a single skill file; note: this is anomalous — skills normally live in subdirectories as `skills/<name>/SKILL.md`. The file has command-style frontmatter `name: index`, `description: ...`, `argument-hint: ...`. It is more plausibly a slash command placed in the wrong directory, or the repo intends skills-as-files; content is minimal either way.)
  - commands: yes (`commands/index.md` — slash-command frontmatter `name: index`, `description: "Index a folder of documents for semantic search"`, `argument-hint: "<folder path>"`; body instructs Claude to call `index_folder` MCP tool)
  - agents: no
  - hooks: yes (`hooks/hooks.json` — one `SessionStart` hook invoking `bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh`)
  - `.mcp.json`: yes (at repo root, NOT at `.claude-plugin/.mcp.json`) — see pitfalls
  - `.lsp.json`: no
  - monitors: no
  - bin: no
  - output-styles: no
- **Agent frontmatter fields used**: not applicable — no agents.
- **Agent tools syntax**: not applicable.
- **Pitfalls observed**:
  - `.mcp.json` lives at repo root with hardcoded absolute paths to the author's Mac (`/Users/omardrljevic/Projects/OtherProjects/cowork-sematic-search/...`). This file cannot be the plugin's MCP registration — it would not work on any other machine, and the plugin docs expect `.mcp.json` at repo root or `.claude-plugin/.mcp.json`. README tells users to paste a templated `.mcp.json` into their OWN project root with their own absolute paths. The repo-root `.mcp.json` is therefore the author's local dev config committed by accident, not a plugin-distribution artifact.
  - `skills/index.md` duplicates `commands/index.md` in purpose. Either the repo has unused skill scaffolding or the author misunderstood the skill vs command split.
  - Note the typo: the local dev absolute path reads `cowork-sematic-search` (missing `n`) — the author's local dir differs from the repo name.

## 6. Dependency installation

- **Applicable**: yes.
- **Dep manifest format**: `requirements.txt` at repo root AND `pyproject.toml` at repo root (both list overlapping dependency sets; `requirements.txt` is what `setup.sh` installs, `pyproject.toml` is what `pip install -e ".[all]"` uses per the README).
- **Install location**: `${CLAUDE_PLUGIN_DATA}/venv` — SessionStart hook creates a plugin-isolated venv under the plugin data directory.
- **Install script location**: `scripts/setup.sh` (repo root), invoked by `hooks/hooks.json` SessionStart hook as `bash ${CLAUDE_PLUGIN_ROOT}/scripts/setup.sh`.
- **Change detection**: sha256 via `shasum -a 256 "$REQ_FILE"`. Mechanism:
  1. `CURRENT_HASH=$(shasum -a 256 "$REQ_FILE" | cut -d ' ' -f 1)` — hash of `requirements.txt`.
  2. `STORED_HASH=$(cat "$REQ_HASH_FILE")` if file exists at `${CLAUDE_PLUGIN_DATA}/requirements.hash`; empty string otherwise.
  3. Condition `[ "$CURRENT_HASH" != "$STORED_HASH" ] || [ ! -d "$VENV_DIR" ]` gates the install block. On mismatch OR missing venv, run `python3 -m venv "$VENV_DIR"`, upgrade pip, `pip install -r "$REQ_FILE"`, then write `echo "$CURRENT_HASH" > "$REQ_HASH_FILE"` only after successful install.
  4. Comparison approach: string-equality on the hex digest. `shasum -a 256` is used (BSD/macOS-ish tool name; Linux typically has `sha256sum` but `shasum` is available on Perl-installed systems). There is no fallback to `sha256sum`.
- **Retry-next-session invariant**: implicit — `set -e` at top of script means any failed command (pip install failure, etc.) aborts the script before the `echo "$CURRENT_HASH" > "$REQ_HASH_FILE"` line runs. So the stored hash never updates on failure, and the next session re-evaluates the `CURRENT_HASH != STORED_HASH` condition and retries install. However, the half-built venv directory IS created by `python3 -m venv` before pip runs — subsequent runs will take the `[ ! -d "$VENV_DIR" ]` path as false, relying on the hash mismatch alone. No explicit `rm -rf "$VENV_DIR"` on failure, so a partially-populated venv survives.
- **Failure signaling**: `set -e` halts on first non-zero exit. No `set -u` (undefined vars would silently expand to empty), no `set -o pipefail`. No JSON/stderr emission — errors surface via whatever pip/venv printed to stderr. No `systemMessage` or `continue: false` JSON output. Hook type is `command`, so non-zero exit is visible in Claude Code's hook log but does not block the session (SessionStart is informational in this setup).
- **Runtime variant**: Python via stdlib `venv` + `pip`. Not `uv`. Not `pipx`. Uses `python3` from PATH (no pinned version).
- **Alternative approaches**: none in-repo — no PEP 723 inline metadata, no `uvx`/`npx` ad-hoc, no pointer file.
- **Version-mismatch handling**: none — venv built against whatever `python3` resolves to; no Python version tracked. Memory file notes "Python 3.13 required (system python is 3.9, use /opt/homebrew/bin/python3.13)" but `setup.sh` makes no version check; if `python3` points at 3.9 the install succeeds but some dependencies (e.g. sentence-transformers wheels) may break at runtime.
- **Pitfalls observed**:
  - `shasum` is the chosen tool — on some Linux distributions `shasum` is absent even when `sha256sum` is present, which would cause `set -e` to abort with "command not found" before the hash comparison even runs.
  - No sentinel marking "install succeeded" apart from the hash-file write. A previous run that failed mid-pip leaves a partial venv; the next run sees venv-exists + hash-mismatch and attempts to re-install into the existing venv (pip upgrade is idempotent, so this typically works, but corrupted wheels aren't cleaned up).
  - Hash file is written only after the final `pip install`; if the hook is killed (SIGTERM) between pip finishing and the echo, the hash file stays stale and the next session reinstalls redundantly. Minor idempotency cost, not a defect.
  - Both `requirements.txt` and `pyproject.toml` list dependencies; only `requirements.txt` drives the hash-gated SessionStart install. Edits to `pyproject.toml` (e.g. adding a package under `[project.optional-dependencies]`) do NOT trigger reinstall.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — the plugin's runtime entry point is the MCP server launched by the host's MCP config (`python -m server.main`), not a `bin/` wrapper. No `bin/` directory present in `gh api .../contents`.
- **`bin/` files**: none.
- **Shebang convention**: not applicable.
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: not applicable for bin; see purpose 6 for SessionStart venv.
- **Platform support**: not applicable.
- **Permissions**: not applicable.
- **SessionStart relationship**: not applicable.
- **Pitfalls observed**: The MCP registration lives in the user's project `.mcp.json` pointing into `{plugin-checkout}/.venv/bin/python`, which is created by `pip install -e ".[all]"` per README — NOT by the plugin's `setup.sh` (which creates a venv under `${CLAUDE_PLUGIN_DATA}/venv`, a different location). There are two parallel venv setups: one for README "install-from-source" users and one for anyone who treats this as a plugin. Neither path is connected to the other.

## 8. User configuration

- **`userConfig` present**: no — `plugin.json` has no `userConfig` block.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable. The MCP server accepts `LANCEDB_PATH` via OS env var (read inside `server/main.py` and `server/indexer.py` via `os.environ.get("LANCEDB_PATH", "./lancedb")`), but this is plain-env not plugin `userConfig`.
- **Pitfalls observed**: Database path is configurable only via OS env var; not surfaced through `plugin.json` `userConfig`, so Claude Code's config UI cannot manage it.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable.
- **Failure posture**: not applicable.
- **Top-level try/catch wrapping**: not applicable.
- **Pitfalls observed**: The only hook is SessionStart for dep install; no enforcement hooks.

## 10. Session context loading

- **SessionStart used for context**: no — SessionStart is used only for dep install (see purpose 6).
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: no — `setup.sh` emits no JSON and does not populate `additionalContext`.
- **SessionStart matcher**: none — `hooks.json` declares no matcher, meaning the hook fires on all SessionStart sub-events (startup, clear, compact, etc.). Dep install on every startup is acceptable because the hash check makes it a no-op; but re-running on `compact` is wasted setup effort.
- **Pitfalls observed**: No matcher means setup runs on `clear` and `compact` too. With the hash check it's a no-op after the first successful install, so cost is a shell spawn + hash compare; not zero but small.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable — no monitors to declare a version floor for.
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — `plugin.json` carries no `dependencies` field.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: not applicable — single-plugin repo, tag is `v0.1.0` (plain semver, no plugin-name prefix).
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: pytest.
- **Tests location**: `tests/` at repo root (flat: `test_chunker.py`, `test_indexer.py`, `test_mcp_tools.py`, `test_parsers.py`, `test_search.py`, `test_store.py`, plus `helpers.py` and `__init__.py`). README claims "56 tests covering parsers, chunking, indexing, search, and MCP tool integration."
- **Pytest config location**: `[tool.pytest.ini_options]` in `pyproject.toml` with `pythonpath = ["."]`. No separate `pytest.ini`.
- **Python dep manifest for tests**: `pyproject.toml` has `[project.optional-dependencies] dev = ["pytest>=8.0"]`; `requirements.txt` also lists `pytest>=8.0` as a top-level dep.
- **CI present**: no — no `.github/` directory at all (`gh api repos/.../contents/.github` → 404).
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable — all testing is local/manual per the README ("source .venv/bin/activate; pytest tests/ -v").
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: direct `pytest tests/ -v` per README. No wrapper script.
- **Pitfalls observed**: No CI means no enforcement of the 56-test claim on PRs; regressions caught only if the author runs pytest locally before committing.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no — no `.github/workflows/` directory.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — the sole release (`v0.1.0`) was created manually via `gh release create` or the GitHub UI.
- **Tag-sanity gates**: none — no automation verifies tag matches `plugin.json` version.
- **Release creation mechanism**: manual (GitHub UI or `gh release create`).
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable — no CHANGELOG.md in repo.
- **Pitfalls observed**: First release is a single tag with title "v0.1.0 — Initial Release"; no changelog, no release body parser, no automated verification that `plugin.json.version` equals tag.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: not applicable — no marketplace.json to validate and no CI.
- **Trigger**: not applicable.
- **Frontmatter validation**: no.
- **Hooks.json validation**: no.
- **Pitfalls observed**: none; matches the "no marketplace" posture.

## 16. Documentation

- **`README.md` at repo root**: present (~8.8 KB) — extensive: why, features, supported formats, multi-client install instructions (Claude Code / Cursor / Windsurf / Cline), usage examples, architecture diagram, roadmap, license.
- **Owner profile README at `github.com/ZhuBit/ZhuBit`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: not applicable — single-plugin repo; the root README serves the plugin.
- **`CHANGELOG.md`**: absent.
- **`architecture.md`**: absent — architecture is inlined as a section in the main README (directory diagram + component-choice table).
- **`CLAUDE.md`**: absent at repo root. `memory/project_cowork_rag_plugin.md` (under a `memory/` dir) carries project context, and `memory/MEMORY.md` indexes it — this looks like an earlier Claude Code "memory" convention rather than current `CLAUDE.md` project guidance.
- **Community health files**: none observed (no SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md — not returned in the root contents listing).
- **LICENSE**: present (AGPL-3.0-or-later).
- **Badges / status indicators**: observed — README opens with 4 shields.io badges: GitHub stars, Python 3.11+, License AGPL-3.0, MCP Compatible.
- **`IMPLEMENTATION_PLAN.md`**: present (~44 KB) at repo root — a planning doc committed alongside shipped code; not required by any documentation system, but notable as a "plan-file-as-artifact" pattern.
- **Pitfalls observed**: `memory/` directory is committed into the repo, making the author's project memory public. Content is benign but exposes planning, phase notes, and paths (`/Users/omardrljevic/...`). Not sensitive but an unusual thing to ship in a public plugin repo.

## 17. Novel axes

- **Multi-MCP-client install documentation.** README provides per-client `.mcp.json` templates for Claude Code, Cursor, Windsurf, and Cline — each with the same server definition but slightly different config file paths. The plugin is explicitly marketed as MCP-portable, not Claude Code-specific; the `.claude-plugin/plugin.json` becomes secondary to the manual MCP config. This is a "hybrid plugin": ships plugin metadata for Claude Code's plugin system but the primary install path is via whichever MCP host the user runs.
- **Committed plan and memory artifacts.** Repo root carries `IMPLEMENTATION_PLAN.md` (44 KB) and `memory/project_cowork_rag_plugin.md` (2.2 KB project-memory file) — design context and author's personal Claude Code memory shipped as first-class repo content, not gitignored. This is unusual; most repos either gitignore working notes or isolate them to a `docs/` subdirectory.
- **Committed developer `.mcp.json` with absolute local paths.** `.mcp.json` at repo root hardcodes `/Users/omardrljevic/Projects/OtherProjects/cowork-sematic-search/...` (note typo: `sematic` vs `semantic`) — the author's local dev config shipped in the repo. For any consumer this file is broken; for the author it is the config that runs the plugin against their own checkout. Functionally superseded by the README's templated `.mcp.json` which tells users to substitute their own paths.
- **SHA-256 on `requirements.txt`, not on lockfile.** The hash is over the declared-dependency manifest rather than a pinned lock. Changes to transitive deps (e.g., a new sentence-transformers patch released) are invisible to the hash; only edits to the `requirements.txt` file itself trigger reinstall. Trade-off: simpler, but won't catch upstream drift between identical `requirements.txt` contents.
- **Single-tool bash dependency for hashing.** `shasum` (BSD/macOS convention) is used rather than `sha256sum` (Linux convention) or a Python one-liner. No fallback. Silently portability-limits the SessionStart hook.
- **Two venvs for one plugin.** README's "Install from source" flow (`pip install -e ".[all]"`) creates `.venv/` in the checkout; the plugin's SessionStart hook creates `${CLAUDE_PLUGIN_DATA}/venv`. Both pull the same `requirements.txt`/`pyproject.toml` deps but are independent. MCP config (per README) points at the checkout's `.venv`; the SessionStart-managed venv is never referenced by the running MCP server. The hook's install effort is therefore unused at runtime — a latent defect in the plugin layout.
- **`.mcp.json` at repo root, not `.claude-plugin/`.** Plugin spec expects `.mcp.json` under `.claude-plugin/` if intended as plugin-shipped MCP config. Repo-root `.mcp.json` is a project-level config, not a plugin artifact. Combined with the absolute paths, this is a leaked dev file.
- **Skill-as-slash-command duplication.** `skills/index.md` and `commands/index.md` both carry slash-command-style frontmatter with the same `name: index` and near-identical descriptions. `skills/` normally holds directories (`skills/<name>/SKILL.md`), not loose `.md` files — the `skills/index.md` placement is non-canonical. Either a misunderstanding of skills vs commands or leftover scaffolding.
- **App-level sha256 mirroring the infra-level sha256.** The plugin itself uses SHA-256 for document incremental-indexing (`server/indexer.py::compute_file_hash` reads in 8192-byte chunks with `hashlib.sha256`). The SessionStart install also uses SHA-256 (for `requirements.txt`). Two independent hash checks, different scopes, same algorithm — a coincidence but worth noting as a "hashing is the idempotency primitive" pattern used at both infra and app layer in this repo.

## 18. Gaps

- **CI/CD posture post-v0.1.0** — whether the author adds GitHub Actions for tests or release automation in future work is unknown; current repo has no `.github/` directory, so the "no CI" observation is for the snapshot only. Would resolve by re-fetching repo contents after future commits.
- **Whether `.mcp.json` at repo root is intentional** — could not distinguish "committed by accident" from "intentional local-dev config I use when I open this repo" without asking the author. README suggests the templated version in the user's project, so the repo-root file serves no plugin-distribution purpose either way.
- **`skills/index.md` design intent** — unknown whether the author meant to ship a skill, copy-pasted the command frontmatter as placeholder, or misunderstands skills-vs-commands. Resolving would require a commit-history review or author input.
- **How the SessionStart venv ever gets used** — no observed code path consumes `${CLAUDE_PLUGIN_DATA}/venv`; the MCP registration in README points into a different venv (repo-local `.venv/`). Without running the plugin end-to-end it's unclear whether the SessionStart install is dead code or whether the author plans to rewire the `.mcp.json` to point at `${CLAUDE_PLUGIN_DATA}/venv` in a later release.
- **`.claude-plugin/` contents beyond `plugin.json`** — the dir listing shows only `plugin.json`. Absence of `.claude-plugin/marketplace.json` or `.claude-plugin/.mcp.json` is confirmed observationally; no other files exist.
- **Whether 56 tests actually pass on CI** — claim is in the README; no CI runs them; local-only verification.
- **Commit-history view of plan evolution** — `IMPLEMENTATION_PLAN.md` (44 KB) was not read; deeper novel-axis patterns about how the plan is structured may exist, but reading it would overshoot the 25-35 call budget. Resolving would require a targeted fetch.
