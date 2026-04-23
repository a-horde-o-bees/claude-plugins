# ekadetov/llm-wiki

## Identification

- **URL**: https://github.com/ekadetov/llm-wiki
- **Stars**: 53
- **Last commit date**: 2026-04-06 (`5e49545a` — docs fix to WALKTHROUGH.md)
- **Default branch**: main
- **License**: MIT (SPDX `MIT`, per GitHub license API + LICENSE file)
- **Sample origin**: dep-management
- **One-line purpose**: "LLM Wiki — Claude Code plugin for persistent, compounding knowledge bases in Obsidian" (from repo description + README: builds knowledge bases inside Obsidian using Karpathy's LLM Wiki pattern)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root
- **Marketplace-level metadata**: none — manifest has only top-level `name`, `owner`, `plugins`; no `metadata` wrapper, no top-level `description`
- **`metadata.pluginRoot`**: absent
- **Per-plugin discoverability**: none — plugin entry has only `name`, `source`, `description`; no `category`, `tags`, or `keywords`
- **`$schema`**: absent
- **Reserved-name collision**: no — plugin name is `llm-wiki`
- **Pitfalls observed**: marketplace.json and plugin.json are minimal to the point that nothing signals discoverability — no category surface, no keywords, no version advertised at the marketplace layer. A marketplace consumer scanning categories would not see this plugin at all.

## 2. Plugin source binding

- **Source format(s) observed**: relative (`"source": "./"`) — the marketplace and the plugin are the same repo root
- **`strict` field**: default (implicit true) — no `strict` key present
- **`skills` override on marketplace entry**: absent
- **Version authority**: `plugin.json` only — `"version": "2.0.0"` lives in `plugin.json`; marketplace.json declares no version
- **Pitfalls observed**: none — co-located root is the simplest possible binding. Relative source with no strict override means the full plugin directory is consumed as-is.

## 3. Channel distribution

- **Channel mechanism**: no split — single main branch, users presumably pin via `@ref` if they want; no multiple marketplace files or tag-based channels observed
- **Channel-pinning artifacts**: absent — no `stable-tools`/`latest-tools` style, no dev-counter split
- **Pitfalls observed**: no tags exist in the repo (`gh api .../tags` returned empty) and no GitHub releases exist either, so there is no stable ref a consumer could pin to other than a commit SHA or `main`.

## 4. Version control and release cadence

- **Default branch name**: main
- **Tag placement**: none — `gh api repos/ekadetov/llm-wiki/tags` returns `[]`
- **Release branching**: none — only `main` branch exists
- **Pre-release suffixes**: none observed — version is `2.0.0`, no suffix
- **Dev-counter scheme**: absent — single semver value in plugin.json
- **Pre-commit version bump**: no evidence — no `.pre-commit-config.yaml`, no `.husky/`, no `.github/` directory at all. Commit history shows a manual `chore: bump version to 2.0.0` (e810af03) which is a human bump, not automation
- **Pitfalls observed**: repo has a version-jump history (`feat!:` breaking commits followed by a manual `chore: bump version to 2.0.0`) but zero tags and zero releases. Nothing fixes `2.0.0` to a specific commit from a consumer's perspective — the version in `plugin.json` is the only signal, and it moves with main.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery — `plugin.json` has no component path fields at all (only `name`, `version`, `description`, `author`). Components are located by Claude Code's conventional layout: `commands/*.md`, `skills/*/SKILL.md`, `hooks/hooks.json`
- **Components observed**:
    - skills: yes (`skills/wiki/SKILL.md` with `references/` subdir holding `compilation-guide.md` + `frontmatter-schemas.md`)
    - commands: yes (`commands/wiki.md`)
    - agents: no
    - hooks: yes (`hooks/hooks.json` — single SessionStart entry for dep install)
    - `.mcp.json`: no
    - `.lsp.json`: no
    - monitors: no
    - bin: no
    - output-styles: no
- **Agent frontmatter fields used**: not applicable (no agents)
- **Agent tools syntax**: not applicable
- **Pitfalls observed**: pure reliance on conventional discovery — `plugin.json` carries zero component declarations, so adding/removing a component requires no manifest edit. This is the minimum-configuration shape.

## 6. Dependency installation

- **Applicable**: yes — plugin ships a SessionStart hook that installs Node packages
- **Dep manifest format**: package.json — but generated at runtime, not checked in. `install-deps.sh` writes `{"private":true}` into `${CLAUDE_PLUGIN_DATA}/package.json` on first run. There is no committed `package.json`, `package-lock.json`, or `requirements.txt` in the repo.
- **Install location**: `${CLAUDE_PLUGIN_DATA}` — packages land in `${CLAUDE_PLUGIN_DATA}/node_modules/`, and the SKILL.md references `${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd` and `.bin/marp`
- **Install script location**: `scripts/install-deps.sh` (1590 bytes, invoked via `bash "${CLAUDE_PLUGIN_ROOT}/scripts/install-deps.sh"` from `hooks/hooks.json`)
- **Change detection**: combined **version file + `diff -q`** — `scripts/deps-version.txt` (repo-committed, value `1.0.0`) is compared to `${CLAUDE_PLUGIN_DATA}/deps-version.txt` using `diff -q`. A sentinel file `${CLAUDE_PLUGIN_DATA}/.deps-ok` gates success. Only when all three conditions hold (sentinel exists, destination version file exists, `diff -q` reports no difference) does the script skip install. Any mismatch re-triggers npm install.
- **Retry-next-session invariant**: `rm` on failure — explicit `rm -f "${SENTINEL}" "${VERSION_DST}"` on npm failure guarantees the next session retries. The repo-committed version file (`VERSION_SRC`) is never removed.
- **Failure signaling**: `set +e` explicitly disables exit-on-error; script documents `MUST NEVER exit non-zero — that blocks sessions` as a header comment. All `|| exit 0` fallthroughs and a final unconditional `exit 0`. Human-readable progress and error messages go to stderr via `echo ... >&2`. The graceful-degradation message `"Wiki will work without qmd/marp."` is the explicit fail-open contract to the user.
- **Runtime variant**: Node npm — `npm install @tobilu/qmd @marp-team/marp-cli`. No uv, pip, bun, or alternative PM in this flow.
- **Alternative approaches**: none observed — no PEP 723, no `npx`/`uvx` ad-hoc. The skill does reference `env -u BUN_INSTALL` to force Node over Bun when invoking qmd, which is a runtime-selection guard rather than an alternative install path.
- **Version-mismatch handling**: version file contents compared byte-for-byte via `diff -q`. There is no Python minor tracking and no Node ABI tracking. The `deps-version.txt` bump is the authoritative trigger — changing its content forces a re-install regardless of what npm would otherwise decide.
- **Pitfalls observed**: the `diff -q` + sentinel + version file combination is a three-gate idempotency check (sentinel exists AND dest version file exists AND matches source). Removing only the sentinel on failure but leaving the version file behind would cause a subsequent corrupted-install state to still be detected (sentinel absence alone would force re-install); the script deletes both to be safe. `set +e` at the top with `|| exit 0` scattered throughout means any mkdir, cd, or cp failure silently degrades — e.g., a read-only `${CLAUDE_PLUGIN_DATA}` would exit 0 with no trace, leaving the skill to fall back to `index.md`-only mode without surfacing why.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no — plugin does not ship any `bin/` wrappers. It invokes `${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd` and `.bin/marp` directly from npm's install output and exposes them as shell variables inside the skill (`QMD="env -u BUN_INSTALL ${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd"`). No repo-owned bin directory.
- **`bin/` files**: not applicable
- **Shebang convention**: not applicable for bin (install-deps.sh itself uses `#!/usr/bin/env bash`; lint-wiki.py uses `#!/usr/bin/env python3`)
- **Runtime resolution**: not applicable — npm places the binaries; the skill resolves them by absolute path under `${CLAUDE_PLUGIN_DATA}`
- **Venv handling (Python)**: not applicable — lint-wiki.py uses only Python stdlib (`os`, `re`, `sys`); no venv is created, system `python3` is assumed
- **Platform support**: not applicable
- **Permissions**: not applicable
- **SessionStart relationship**: not applicable — SessionStart populates `node_modules/`, which the skill references by path; no bin-wrapper pointer-file indirection
- **Pitfalls observed**: none from the bin-wrapper axis, but adjacent observation: `scripts/lint-wiki.py` is a repo script called from the skill (inferred from the `lint` operation), not a bin-exported CLI — so it bypasses the "how do I ship a CLI" question entirely.

## 8. User configuration

- **`userConfig` present**: no
- **Field count**: none
- **`sensitive: true` usage**: not applicable
- **Schema richness**: not applicable
- **Reference in config substitution**: not applicable — no `${user_config.*}` or `CLAUDE_PLUGIN_OPTION_*` references in any file examined
- **Pitfalls observed**: the README hard-codes `~/ObsidianVault/03-Resources/` as the vault path. This should be a `userConfig` field; instead it is a prose convention enforced by the skill's directory walk. Users with a vault at any other path must symlink or change their layout.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none — `hooks/hooks.json` contains only a SessionStart entry
- **PostToolUse hooks**: none
- **PermissionRequest/PermissionDenied hooks**: absent
- **Output convention**: not applicable (no tool-enforcement hooks)
- **Failure posture**: not applicable
- **Top-level try/catch wrapping**: not applicable
- **Pitfalls observed**: none — plugin consciously does not gate tool use.

## 10. Session context loading

- **SessionStart used for context**: no — the single SessionStart hook runs `install-deps.sh` for dep management only; it does not emit `hookSpecificOutput.additionalContext`
- **UserPromptSubmit for context**: no
- **`hookSpecificOutput.additionalContext` observed**: no
- **SessionStart matcher**: none — the `hooks.json` SessionStart entry has no `matcher` key, so it fires on all sub-events (startup, clear, compact). Since `diff -q` is idempotent this is fine, but it does mean every `/clear` re-runs the install check.
- **Pitfalls observed**: SessionStart's lack of a matcher means the idempotency check runs more often than strictly necessary. Each invocation is cheap (three `test -f` + one `diff -q`) so this is not a correctness problem, just redundant work.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no
- **Monitor count + purposes**: none
- **`when` values used**: not applicable
- **Version-floor declaration**: not applicable
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no
- **Entries**: none — `plugin.json` has no `dependencies` key
- **`{plugin-name}--v{version}` tag format observed**: not applicable (single-plugin marketplace, no tags at all)
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: none — repo contains no `tests/`, no `*_test.py`, no `test_*.py`, no `spec.*` files
- **Tests location**: not applicable
- **Pytest config location**: not applicable
- **Python dep manifest for tests**: not applicable
- **CI present**: no — `gh api .../contents/.github` returns 404; there is no `.github/` directory of any kind
- **CI file(s)**: none
- **CI triggers**: not applicable
- **CI does**: not applicable
- **Matrix**: none
- **Action pinning**: not applicable
- **Caching**: not applicable
- **Test runner invocation**: not applicable
- **Pitfalls observed**: zero automated verification. The plugin ships with no tests, no linting, no manifest validation, and no CI. `scripts/lint-wiki.py` is a user-facing content linter for the wiki data, not a self-test of the plugin. A broken `marketplace.json` or `hooks.json` would only surface at user install time.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no
- **Release trigger**: not applicable
- **Automation shape**: not applicable — no automation; version bumps are manual commits
- **Tag-sanity gates**: not applicable
- **Release creation mechanism**: not applicable
- **Draft releases**: not applicable
- **CHANGELOG parsing**: not applicable — no `CHANGELOG.md`
- **Pitfalls observed**: manual version management with no tag convention means there is no way to pin to `v2.0.0` as a ref — the only way to reach the 2.0.0 commit is by SHA (e810af03 bumped the version in plugin.json, but that commit is not tagged).

## 15. Marketplace validation

- **Validation workflow present**: no
- **Validator**: not applicable
- **Trigger**: not applicable
- **Frontmatter validation**: not applicable
- **Hooks.json validation**: not applicable
- **Pitfalls observed**: no validator. Marketplace and plugin manifests are hand-edited and trust-on-commit.

## 16. Documentation

- **`README.md` at repo root**: present (3390 bytes — installation, prerequisites, per-command usage with examples, wiki structure diagram, Obsidian/qmd integration notes, uninstall)
- **`README.md` per plugin**: not applicable (single-plugin, repo root IS the plugin root)
- **`CHANGELOG.md`**: absent
- **`architecture.md`**: absent
- **`CLAUDE.md`**: absent at repo root — but note: the plugin generates a `CLAUDE.md` template **inside each created wiki's root** at `~/ObsidianVault/03-Resources/<name>/CLAUDE.md` (documented in WALKTHROUGH.md as the wiki schema contract). This is user-data scaffolding, not a plugin-level governance doc.
- **Community health files**: none — no `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`, no `.github/ISSUE_TEMPLATE`
- **LICENSE**: present (MIT, 1065 bytes; SPDX `MIT` from GitHub)
- **Badges / status indicators**: absent (README has no shield badges)
- **Additional document**: `WALKTHROUGH.md` (17052 bytes) — long-form tutorial covering the Karpathy pattern, wiki structure, active-wiki detection, schema contract, per-command walkthroughs. Substantial enough to be architecture-adjacent, but framed as user tutorial rather than internal design.
- **Pitfalls observed**: no `architecture.md` and no CHANGELOG means the rationale for the v1→v2 split (visible in the commit history as `feat!: split ingest into ingest + compile operations` and `refactor!: move log.md from wiki/ to topic root`) lives only in commit messages. A user upgrading across the major bump has no user-facing migration guide — the WALKTHROUGH describes the current state only.

## 17. Novel axes

- **Generated-package.json pattern**: the SessionStart script writes a minimal `{"private":true}` `package.json` into `${CLAUDE_PLUGIN_DATA}` on first run rather than shipping one. This keeps the plugin repo free of Node-ecosystem noise (no lockfile, no `node_modules/` in gitignore, no dependency drift) while still letting npm operate on a valid project. The authoritative declaration of the two dependencies lives inline in the install script (`npm install @tobilu/qmd @marp-team/marp-cli`), not in a manifest.
- **Three-gate idempotency combination**: `sentinel file existence` AND `dest version file existence` AND `diff -q version file match` — each gate is cheap and each catches a different corruption mode (aborted install, partial file write, upstream version bump). Together they form a stricter check than any single mechanism.
- **Bun-avoidance runtime guard**: the skill's qmd invocation wraps every call in `env -u BUN_INSTALL ${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd`. This is a runtime environment sanitization specifically for a sqlite-vec incompatibility — Bun's bundled SQLite lacks extension loading, so when `BUN_INSTALL` is set, qmd fails to load its vector index. Worth noting as a plugin-side defense against user-environment contamination.
- **Plugin-generates-CLAUDE.md-as-user-schema**: the plugin scaffolds a `CLAUDE.md` inside each created wiki directory as part of `wiki init`. This CLAUDE.md is not the plugin's own governance doc — it is *user data* that becomes the schema contract for subsequent skill invocations. The skill's "active wiki detection" walks up looking for `CLAUDE.md` + `wiki/` as co-present markers. CLAUDE.md functioning as per-subdirectory schema anchor is a distinctive use of the filename.
- **Graceful-degradation via fallback tool**: qmd is not required — when `${CLAUDE_PLUGIN_DATA}/node_modules/.bin/qmd` is not executable (because SessionStart install failed), the skill falls back to manual `wiki/index.md` read + grep. This is a documented fail-soft path inside the skill itself, not an install retry — the plugin works (in reduced mode) even if dependency install permanently fails. Aligns with the install script's fail-open stance.
- **No-metadata, no-tags, no-releases minimalism**: the repo ships the minimum viable marketplace shape — no `metadata.*` wrapper, no `category`/`tags`/`keywords`, no `$schema`, no git tags, no GitHub releases, no CHANGELOG. A user would find this plugin only by direct URL or owner search. This is a data point on the opposite end of the discoverability spectrum from marketplaces that use `metadata.pluginRoot` and rich per-plugin taxonomies.

## 18. Gaps

- **lint-wiki.py invocation path**: I read the head of lint-wiki.py and confirmed it is a stdlib-only wiki content linter, but I did not verify from the SKILL.md exactly which command section calls it. The skill's `lint` operation presumably shells out to `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/lint-wiki.py <wiki-dir>` but I did not fetch the `## lint` section body to confirm. Resolution: fetch the `## lint` section of SKILL.md (~lines ~300-400 of the 542-line file).
- **Middle of SKILL.md (commands init/ingest/compile/query/remove)**: I sampled the opening (active wiki detection, qmd availability) and the closing (frontmatter schemas, index/log format, rules). The ~400 middle lines describing per-operation procedures were not fetched. Resolution: one or two more WebFetches covering `## init`, `## ingest`, `## compile`, `## query`, `## remove` sections if any operation embeds hidden infrastructure assumptions (e.g., exec permissions, additional write paths).
- **WALKTHROUGH.md full body**: I sampled the first ~80 lines which covered introduction, Obsidian rationale, and wiki structure. Later sections (Part 3+) were not read and may document install-troubleshooting, Marp slide export, or behavior under qmd absence in more detail. Resolution: two more WebFetches by line range.
- **compilation-guide.md and frontmatter-schemas.md (skill references/)**: confirmed present by directory listing but contents not fetched. They are component files under `skills/wiki/references/` (1898 + 1102 bytes) loaded via the skill's reference mechanism. Resolution: direct raw fetches from GitHub (low cost, ~3KB combined).
- **Release/tag absence verification**: I relied on empty responses from `gh api .../tags` and `gh api .../releases`. GitHub API can paginate; I did not check for a non-default ref format. Resolution: `gh api` with `--paginate` or direct check of `git/refs/tags`. Low probability of missed tags given the small repo and the command/release history both pointing at plain commits.
- **License header scan**: LICENSE file confirmed present (MIT per GitHub's license API). I did not read the file body to verify year and copyright holder — unlikely to matter for pattern verification.
- **`package.json`/`package-lock.json` absence**: verified by full recursive tree listing — no Node manifest in the repo. Confirmed rather than gap; noted here to be explicit that the dep-management pattern relies on a runtime-generated manifest.
