# mdproctor/cc-praxis

## Identification

- **URL**: https://github.com/mdproctor/cc-praxis
- **Stars**: 1
- **Last commit date**: 2026-04-17
- **Default branch**: main
- **License**: Apache-2.0
- **Sample origin**: bin-wrapper (sampled for bin/cc-praxis, which is a thin script-relative bash wrapper around a Python HTTP server). Secondary interest: aggregator marketplace with 48 relative plugins and 8 named bundles; a parallel non-claude-plugin installer (`scripts/claude-skill`) that uses a custom marketplace schema extension (`path`, `--snapshot`).
- **One-line purpose**: "Professional development skills for Claude Code — deep Java/Quarkus support plus universal principles for any project" (48 skills: Java/Quarkus, TypeScript/Node.js, Python, and cross-cutting workflow plugins).

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root.
- **Marketplace-level metadata**: top-level fields `name`, `description`, `owner` (with `name`, `url`); no `metadata` wrapper. Adds a repo-custom top-level `bundles` array (8 entries — each has `name`, `displayName`, `description`, `skills`). `bundles` is not a documented Anthropic marketplace field; it's consumed by this repo's own web/manual installers, not by Claude Code's `/plugin install`.
- **`metadata.pluginRoot`**: absent (no `metadata` wrapper at all).
- **Per-plugin discoverability**: none — no `category`, `tags`, or `keywords` on any of the 48 plugin entries. Each plugin object is minimal: `{ name, source, description, version }`.
- **`$schema`**: absent.
- **Reserved-name collision**: no (marketplace name `cc-praxis` is not on the reserved list per docs-plugin-marketplaces.md).
- **Pitfalls observed**: the top-level `bundles` field is a silent schema extension — it works because Claude Code presumably ignores unknown fields, but it means the bundle semantics are owned entirely by this repo's out-of-band installers (`scripts/claude-skill`, `scripts/web_installer.py`). A user installing via the built-in `/plugin install` gets individual plugins and has no access to bundle grouping.

## 2. Plugin source binding

- **Source format(s) observed**: all 48 entries use `source: "./<plugin-dir>"` (relative). Per docs-plugin-marketplaces.md, relative sources make `plugin.json` authoritative for version and fall back to marketplace entry for other metadata.
- **`strict` field**: absent across all entries (implicit `true` by docs default).
- **`skills` override on marketplace entry**: absent (no strict-false carving observed).
- **Version authority**: the repo writes versions in BOTH marketplace.json AND each `plugin.json` — classic drift risk. Observed drift: marketplace.json lists `git-commit: 1.0.0` but the plugin's `.claude-plugin/plugin.json` carries `1.0.0-SNAPSHOT`. Commit history shows a single "drop SNAPSHOT — all 49 skills promoted to 1.0.0" batch — the drop did not land consistently (git-commit still has SNAPSHOT at HEAD). Per docs, for relative sources `plugin.json` wins; so the user-visible version of `git-commit` is `1.0.0-SNAPSHOT`, not the `1.0.0` advertised in marketplace.json.
- **Pitfalls observed**: parallel version-authority sources invite silent drift. Claude Code will pick the plugin.json value for relative sources, but the repo's own `web_installer.py` reads marketplace.json (different answer). Two consumers, two truths, one field name.

## 3. Channel distribution

- **Channel mechanism**: no split — single marketplace, single branch (main). Users pin implicitly via the git ref they added to (default main).
- **Channel-pinning artifacts**: absent for Claude Code's `/plugin` pathway. The repo's `scripts/claude-skill` adds a parallel notion: `--snapshot` flag fetches from main HEAD vs. (undocumented, unclear) stable-tag resolution; RELEASE.md says "stable install fetches from git tag v1.0.0" but the installer source shown here pulls via `git clone` of `plugin["source"]` (which is `./<dir>` in marketplace.json — a relative path, not a URL). The claude-skill installer has logic that does not match the actual marketplace schema and would fail for all 48 plugins as-written (`plugin["source"]` is `./java-dev`, not `https://github.com/...`). This is observed, not inferred from docs.
- **Pitfalls observed**: the documented "snapshot vs stable" channel concept in RELEASE.md is not implemented by a two-marketplace split; it's declared via `-SNAPSHOT` suffix in plugin.json versions that are supposed to be consumed by the custom installer, which itself has schema mismatches. The only mechanism that actually channels for end-users today is git-tag pinning via `/plugin marketplace add ...@v1.1.0`.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: 3 annotated tags on main: `v1.0.0`, `v1.0.1`, `v1.1.0`. Corresponding GitHub releases exist (non-draft) for all three.
- **Release branching**: none — trunk-based (RELEASE.md explicitly documents this: "trunk-based development with git tags").
- **Pre-release suffixes**: Maven-style `-SNAPSHOT` applied to per-plugin `plugin.json` versions during development; stripped at tag time. Not a SemVer pre-release (`-rc`/`-beta`) and not recognized by standard semver comparators — the repo's `web_installer.py` has custom `_version_tuple` logic that treats `SNAPSHOT` as strictly older than its release counterpart.
- **Dev-counter scheme**: absent. No `0.0.z` dev counter; no automatic version bump on every commit.
- **Pre-commit version bump**: no — versions bump manually per RELEASE.md workflow.
- **Pitfalls observed**: the SNAPSHOT convention is borrowed from the Maven ecosystem (consistent with the repo's Java/Quarkus focus) but is not part of SemVer, is not recognized by any Claude Code plugin machinery, and requires custom ordering code in the repo's own installer. Mixing `1.0.0` and `1.0.0-SNAPSHOT` across 48 plugins creates ordering ambiguity for consumers that use naive string comparison.

## 5. Plugin-component registration

- **Reference style in plugin.json**: minimal — every plugin.json is 3-5 lines: `name`, `description` (many literally carry the broken string `">"` — indicating a hand-edit glitch), `version`, occasional empty `dependencies: []`. No `skills`, `commands`, `agents`, `hooks`, `mcpServers` fields anywhere. Default discovery is in force for every plugin.
- **Components observed**:
    - skills: yes (every plugin has a top-level `SKILL.md`, auto-discovered by Claude Code's default-discovery rules)
    - commands: yes (every plugin has a `commands/<name>.md`)
    - agents: no
    - hooks: no (the sole shell hook at `hooks/check_project_setup.sh` lives at the repo root, NOT inside any plugin, and is NOT registered via any plugin's `hooks.json` — it is installed manually into `~/.claude/hooks/` by the `install-skills` skill and wired into `~/.claude/settings.json` by that same skill's prose)
    - .mcp.json: no
    - .lsp.json: no
    - monitors: no
    - bin: yes, only for the root-level `bin/cc-praxis` wrapper. This bin/ directory is NOT inside any plugin's directory — it's at the repo root. Which plugin the bin is bound to is ambiguous: no plugin.json declares it, and the marketplace root is the implicit plugin scope that the docs say `bin/` auto-registers against only when placed inside a plugin. Observed behavior assumption: since the marketplace plugin entries are all `./subdir` paths, the root-level `bin/` is not auto-registered by any plugin; the README tells users to invoke `cc-praxis` directly from PATH after a local clone, or falls back to `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/web_installer.py` (see cc-praxis-ui SKILL.md).
    - output-styles: no
- **Agent frontmatter fields used**: not applicable.
- **Agent tools syntax**: not applicable.
- **Pitfalls observed**: the `bin/cc-praxis` wrapper lives at repo root with no plugin scoping, so it cannot be auto-added to PATH via the standard plugin mechanism (which requires `bin/` inside a plugin directory per docs). The skill that would invoke it (`cc-praxis-ui`) has to fall back to an absolute `${CLAUDE_PLUGIN_ROOT}/scripts/web_installer.py` path for plugin-installed usage — the `bin/cc-praxis` wrapper is effectively dead code in the plugin-install pathway and only functions from a local clone where the user adds `bin/` to their shell PATH manually. Multiple plugin.json files have `description: ">"` (artifact of a YAML block-scalar accidentally round-tripped into JSON) — that would render as a single `>` in any UI reading plugin.json; marketplace.json has the real descriptions, so the built-in CLI reads those and the problem is silent for most users.

## 6. Dependency installation

- **Applicable**: yes — the repo has Python dependencies (`requirements.txt`: requests, pytest, PyYAML) but they serve CI and local dev of the installer scripts, not the skills themselves. No plugin-install-time hook installs them. The `scripts/web_installer.py` uses only standard library (http.server, json, pathlib, subprocess), so installed-plugin runtime has no Python deps beyond system python3.
- **Dep manifest format**: `requirements.txt` for CI/dev only.
- **Install location**: not applicable for plugin-runtime — there is no plugin-scoped venv or data dir. `CLAUDE_PLUGIN_DATA` and `CLAUDE_PLUGIN_ROOT` are not used for install.
- **Install script location**: not applicable (no plugin-install hook). Separately, the bundled `scripts/claude-skill` (which is not a plugin hook — it's a standalone CLI the user runs after cloning) installs into `~/.claude/skills/<name>/` via `git clone --filter=blob:none --sparse`.
- **Change detection**: not applicable.
- **Retry-next-session invariant**: not applicable.
- **Failure signaling**: not applicable (no hook); the standalone `claude-skill` script uses `print("❌ ...", file=sys.stderr)` + `sys.exit(1)` for its own errors.
- **Runtime variant**: not applicable — runtime uses system `python3`, no venv, no uv, no pip at run time.
- **Alternative approaches**: this repo's interesting alternative is the "parallel manual installer" pattern — `scripts/claude-skill` and the `scripts/web_installer.py` localhost UI both operate on the marketplace.json schema from outside Claude Code entirely, installing skills as `~/.claude/skills/<name>/` bare directories rather than through `/plugin install`. This predates or side-steps the Claude Code plugin system.
- **Version-mismatch handling**: the web_installer.py's custom SNAPSHOT-aware version comparator (`_version_tuple`) is the only version-mismatch logic in the repo.
- **Pitfalls observed**: the repo straddles two distribution models — claude-plugin (via marketplace.json + `/plugin install`) and pre-plugin skill installation (via `scripts/claude-skill` + `~/.claude/skills/`). It is not clear from the code which model is canonical. The `install-skills` SKILL.md explicitly writes `~/.claude/hooks/check_project_setup.sh` and edits `~/.claude/settings.json` — operating on user-level settings from inside a plugin skill, not on plugin-scoped hook config. This is a contract inversion: the plugin persists state outside the plugin's own sandbox, surviving uninstall.

## 7. Bin-wrapped CLI distribution

- **Applicable**: yes — `bin/cc-praxis` at repo root.
- **`bin/` files**: `bin/cc-praxis` — 316 bytes, a 6-line bash wrapper whose only purpose is `exec python3 "$PLUGIN_ROOT/scripts/web_installer.py" "$@"` where `$PLUGIN_ROOT` is derived script-relatively.
- **Shebang convention**: `#!/bin/bash` (not `#!/usr/bin/env bash`). Explicit absolute path — less portable on systems where bash is not at `/bin/bash` (e.g., some NixOS configurations, Alpine with `ash`-only defaults).
- **Runtime resolution**: **script-relative only**. The resolution is `PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"`. No check for `${CLAUDE_PLUGIN_ROOT}` env var. The comment in the file states "Works both from the plugin cache (${CLAUDE_PLUGIN_ROOT}) and from a local clone" — but the mechanism is the same path math in both cases: resolve the script's parent's parent. This works because when Claude Code installs the plugin into its cache, the `bin/` and `scripts/` directories end up siblings under a common root, preserving the script-relative layout. There is no env-var preference, no fallback cascade, no "script-relative fallback if env var unset" — strictly script-relative, always.
- **Venv handling (Python)**: not applicable — `exec python3` uses whatever `python3` is on PATH (system Python). No venv activation, no uv, no pip install.
- **Platform support**: POSIX bash-only. No `.cmd`, `.ps1`, or OS-detecting fallback. Windows CMD / native PowerShell users cannot invoke it without WSL or Git Bash.
- **Permissions**: 100755 (executable, confirmed via GitHub tree API mode field).
- **SessionStart relationship**: none — static script, no hook populates or depends on it. Its own lifecycle is independent of any plugin hook; the `cc-praxis-ui` skill's workflow is to `bash: cc-praxis --no-browser &` on user invocation.
- **Pitfalls observed**: the "script-relative only" pattern is simpler than the env-var-first-with-fallback convention but depends on the cache preserving the repo's internal layout — if Claude Code's cache flattening or rearrangement ever changes, the wrapper breaks silently (Python is invoked on a wrong path, likely with ImportError from `web_installer.py` trying to load `docs/index.html`). Placing `bin/` at repo root rather than inside a specific plugin means it's not auto-registered with any plugin in the claude-plugin sense; the wrapper is only reachable from a local clone whose `bin/` is on the user's shell PATH manually. The cc-praxis-ui SKILL.md falls back to an explicit `${CLAUDE_PLUGIN_ROOT}/scripts/web_installer.py` for the plugin-installed path — so the bin wrapper's value is only for local-clone users.

## 8. User configuration

- **`userConfig` present**: no. Not in marketplace.json, not in any plugin.json.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable.
- **Pitfalls observed**: the web_installer.py reads a `CLAUDE_SKILLS_DIR` env var to relocate the install root for tests. This is env-var-based configuration managed by the script, not `userConfig` — an alternative pattern that bypasses Claude Code's user-config UI entirely.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable.
- **Failure posture**: not applicable.
- **Top-level try/catch wrapping**: not applicable.
- **Pitfalls observed**: the repo has no tool-use enforcement hooks at all. The only hook-shaped artifact is `hooks/check_project_setup.sh` (which is a SessionStart-style nudge, not a tool-use gate) and it is installed into user settings, not registered via any plugin's hooks.json.

## 10. Session context loading

- **SessionStart used for context**: yes, but via user-settings rather than plugin-hooks. The `install-skills` skill instructs Claude to write `~/.claude/hooks/check_project_setup.sh` and add it to `~/.claude/settings.json` as a user-level session-start hook. It does NOT register via any plugin's `hooks.json`. The hook prints "⚠️ ACTION REQUIRED" directives to stdout that Claude reads as system-level context at session start (per the script's own comment: "Output is read by Claude at session start — messages are directives to act on").
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: no — the hook uses plain stdout print, not the structured JSON `additionalContext` channel.
- **SessionStart matcher**: not applicable at the plugin level. At the user-settings level, exact matcher not visible without fetching the prescribed settings.json contents (the install-skills SKILL.md shows a template but in excerpts; full matcher string not inspected in this pass).
- **Pitfalls observed**: context-loading is delivered by a skill that mutates user-level config rather than by plugin-scoped hook registration. Consequences: (1) the behavior persists after plugin uninstall unless `uninstall-skills` explicitly unwinds; (2) the hook runs globally on every session regardless of whether cc-praxis is installed in that project; (3) the `/plugin uninstall` builtin will not clean it up because it's not a plugin-owned artifact.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: partial — three observed shapes across the 48 plugins:
    1. Omitted entirely (majority, e.g., `cc-praxis-ui`, `adr`, `git-commit`).
    2. Present and empty (`"dependencies": []`) — e.g., `install-skills`.
    3. Per README, the `scripts/claude-skill install quarkus-flow-testing` automatically pulls `java-dev + quarkus-flow-dev` — so some plugin.json files must contain real dependency arrays. Not sampled in this pass.
- **Entries**: bare string or object with `{name: ...}` accepted by the custom resolver (`dep["name"] if isinstance(dep, dict) else dep`). Cross-marketplace not observed. No semver ranges in the resolver (`resolve_dependencies` just walks by name).
- **`{plugin-name}--v{version}` tag format observed**: no. The three tags (`v1.0.0`, `v1.0.1`, `v1.1.0`) apply to the whole repo, not per-plugin.
- **Pitfalls observed**: the repo's dependency resolution is performed client-side by the custom `scripts/claude-skill` and `web_installer.py`, not by Claude Code's `dependencies` field (which is a v2.1.110+ feature per docs-plugin-dependencies.md). README explicitly acknowledges this: "The official Claude Code marketplace doesn't yet support automatic dependency resolution ([Issue #9444](https://github.com/anthropics/claude-code/issues/9444))." So the repo is knowingly routing around the platform with its own resolver — the claude-plugin `dependencies` entries may or may not be present/correct; since `/plugin install` ignores them pre-v2.1.110, validation slips.

## 13. Testing and CI

- **Test framework**: pytest (extensive — 35+ test files in `tests/`).
- **Tests location**: `tests/` at repo root (flat), plus per-plugin `tests/test_cases.json` fixtures inside skill directories (e.g., `adr/tests/test_cases.json`) that drive behavior tests from a central `test_base.py`.
- **Pytest config location**: dedicated `pytest.ini` at repo root. Config is minimal — only defines a `slow` marker. No `[tool.pytest.ini_options]` in pyproject.toml (there is no pyproject.toml).
- **Python dep manifest for tests**: `requirements.txt` (requests, pytest, PyYAML) — no requirements-dev.txt.
- **CI present**: yes.
- **CI file(s)**: `.github/workflows/skill-validation.yml` (CI validators + tests) and `.github/workflows/pages.yml` (Jekyll docs site → GitHub Pages).
- **CI triggers**: `push: branches: [main]`, `pull_request: branches: [main]`, `workflow_dispatch` (skill-validation); `push: branches: [main]`, `workflow_dispatch` (pages).
- **CI does**: 3-tier custom validator (`python3 scripts/validate_all.py --tier commit`, `--tier push`, `--tier ci` — tiers run sequentially) + `pytest tests/ -v`. The "tiered validators" concept is distinctive: a single validator driver that runs different validator sets at different rigor levels, and CI runs all three tiers. Pages workflow builds Jekyll from `docs/` with Ruby 3.3.
- **Matrix**: none — single Python 3.11 x ubuntu-latest on the validation workflow.
- **Action pinning**: major-version tags (`actions/checkout@v4`, `actions/setup-python@v5`, `ruby/setup-ruby@v1`, `actions/configure-pages@v5`, `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4`). No SHA pinning.
- **Caching**: built-in `cache: 'pip'` on `actions/setup-python@v5`; `bundler-cache: true` on `ruby/setup-ruby@v1`. No `actions/cache`.
- **Test runner invocation**: direct `python3 -m pytest tests/ -v`.
- **Pitfalls observed**: the tiered-validator concept is undocumented in the workflow — a reader has to open `scripts/validate_all.py` to learn which validators run at which tier. The `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` env var is set at job-scope, a symptom of a recent Node upgrade churn in GitHub Actions runners.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no automated release workflow.
- **Release trigger**: not applicable.
- **Automation shape**: fully manual per RELEASE.md — bump `plugin.json`, commit, tag annotated, push `--tags`. GitHub releases (3 exist, all non-draft) are created manually via the GitHub UI or `gh release create` (not automated).
- **Tag-sanity gates**: none — no workflow verifies the tag is on main or that `plugin.json` version matches the tag name.
- **Release creation mechanism**: manual (`git tag -a` + manual release creation).
- **Draft releases**: no.
- **CHANGELOG parsing**: no CHANGELOG.md present. Release notes are written per-release in the GitHub release body (manual).
- **Pitfalls observed**: no automation gives no safety net — the `1.0.0` vs `1.0.0-SNAPSHOT` drift in `git-commit/.claude-plugin/plugin.json` at HEAD (post v1.1.0 tag) is exactly the kind of thing a tag-sanity gate would catch.

## 15. Marketplace validation

- **Validation workflow present**: no dedicated marketplace-validation workflow. However, `scripts/validate_all.py` runs a broad validator set that includes `scripts/validation/validate_frontmatter.py`, `validate_structure.py`, `validate_doc_structure.py`, `validate_references.py`, `validate_links.py`, and 15+ others targeting skill content (not marketplace.json schema specifically).
- **Validator**: custom Python — not bun+zod, not `claude plugin validate` CLI.
- **Trigger**: `push` and `pull_request` (via the skill-validation.yml workflow tiered invocations).
- **Frontmatter validation**: yes (`validate_frontmatter.py`, `validate_blog_frontmatter.py`).
- **Hooks.json validation**: not applicable (no plugin-level hooks.json exists).
- **Pitfalls observed**: the validator suite targets skill/doc content, not the marketplace.json schema. No validator checks marketplace-plugin-entry schema conformance or version-drift between marketplace.json and plugin.json — which is exactly how the SNAPSHOT drift slipped through.

## 16. Documentation

- **`README.md` at repo root**: present (~450 lines including install guide, project-type table, skill catalog, bundle descriptions, commit workflow, key features, contributing).
- **`README.md` per plugin**: absent — each plugin has only `SKILL.md` (no per-plugin README).
- **`CHANGELOG.md`**: absent.
- **`architecture.md`**: present at repo root as `docs/architecture.md` (not sampled deeply).
- **`CLAUDE.md`**: present at repo root (declares project-type: skills, documents the no-AI-attribution rule, project identity).
- **Community health files**: `DESIGN.md` (architectural-decisions doc, Java-flavored), `PHILOSOPHY.md`, `QUALITY.md`, `HANDOFF.md`, `IDEAS.md`, `RELEASE.md`, `LICENSE`. No `SECURITY.md`, `CONTRIBUTING.md`, or `CODE_OF_CONDUCT.md`.
- **LICENSE**: present (Apache-2.0).
- **Badges / status indicators**: not observed in the README head — no CI, license, or version badges near the logo.
- **Pitfalls observed**: extensive meta-docs at repo root (DESIGN.md, PHILOSOPHY.md, QUALITY.md, HANDOFF.md, IDEAS.md, RELEASE.md) are the repo's own workflow artifacts — the `handover` and `idea-log` plugins are themselves bootstrapped here. This doubles as dogfooding but means a reader trying to understand the plugin offering has to mentally separate "repo-own meta-docs" from "user-facing skill docs" (which live in `docs/` and are published to GitHub Pages at mdproctor.github.io/cc-praxis).

## 17. Novel axes

- **Bundle abstraction as marketplace extension**: the top-level `bundles` field in marketplace.json groups plugins into named collections (`quick-start-java`, `core`, `principles`, etc.) with display metadata. This is a non-standard extension — Claude Code's marketplace schema has no `bundles` concept. It's consumed only by the repo's custom installers (`web_installer.py` serves these for UI grouping; `scripts/claude-skill` uses them for `install-all` subsetting). Worth surfacing as "novel marketplace-level grouping surface" candidate: how do other marketplaces organize plugins into user-facing collections when the schema doesn't have a native grouping primitive?
- **Parallel manual installer pattern**: the repo ships `scripts/claude-skill` (CLI) and `scripts/web_installer.py` (localhost HTTP UI at :8765) as alternatives to `/plugin install`. The web installer reads marketplace.json and writes to `~/.claude/skills/<name>/` via sparse-checkout git-clone — completely outside Claude Code's plugin caching. Motivation stated in README: "The official Claude Code marketplace doesn't yet support automatic dependency resolution." This is an interesting "escape valve" design — building your own installer when the platform's is insufficient for your feature set.
- **SNAPSHOT-versioning convention borrowed from Maven**: plugins use `1.0.0-SNAPSHOT` during development (stripped at release). Custom version comparator in `web_installer.py` (`_version_tuple`) treats SNAPSHOT as strictly older than the release. Not a SemVer pre-release identifier (`-rc`, `-beta`). Worth noting as a language-ecosystem borrowing — the Java/Quarkus-focused author brings Maven versioning conventions across to the plugin ecosystem.
- **User-settings mutation from inside a plugin skill**: the `install-skills` SKILL.md instructs Claude to write `~/.claude/hooks/check_project_setup.sh` and modify `~/.claude/settings.json` to register it as a session-start hook — operating on user-level settings rather than plugin-scoped `hooks.json`. Effect: the plugin persists state outside the plugin sandbox; `/plugin uninstall` cannot clean it up; the `uninstall-skills` plugin exists to manually unwind. Interesting contract violation — the plugin extends its reach beyond its own lifecycle.
- **Tiered-validator CI**: single driver script (`scripts/validate_all.py`) invoked with `--tier {commit,push,ci}` — the same runner escalates rigor at different CI stages. Not a matrix, not separate jobs — one driver, tiered flags. Distinct from the more common "one workflow per validator type" pattern.
- **Project-type registry as cross-cutting routing mechanism**: the `CLAUDE.md` declares a `## Project Type` field (`java | skills | blog | custom | generic`) that multiple skills (`git-commit`, `update-claude-md`, `project-health`, etc.) read at runtime to dispatch to language-specific sub-skills (`java-git-commit`, `blog-git-commit`, etc.). A user-config-in-CLAUDE.md pattern that achieves what `userConfig` might otherwise handle — but at project scope, not user scope. Novel instance of "CLAUDE.md as config-surface."
- **bin/ at repo root, not inside a plugin**: atypical placement — the `bin/cc-praxis` wrapper has no owning plugin directory, so auto-PATH registration (which depends on `bin/` inside a plugin dir per the plugin model) does not happen. Only reachable for local-clone users who add `bin/` to their shell PATH manually; plugin-installed users fall back to the explicit `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/web_installer.py` in the cc-praxis-ui SKILL.md.

## 18. Gaps

- **install-skills settings.json template full text**: the `install-skills` SKILL.md was sampled up to line 80 — the full JSON block that gets written to `~/.claude/settings.json` (including the exact matcher shape for the session-start entry) is not captured in this pass. Resolve by fetching lines 80-200 of `install-skills/SKILL.md`.
- **Per-plugin `dependencies` entries**: only three plugin.json files were sampled. The README implies real dependency chains (e.g., `quarkus-flow-testing` pulls `java-dev + quarkus-flow-dev`), so some plugin.json files must contain real `dependencies` arrays. To resolve: fetch plugin.json for `quarkus-flow-testing`, `ts-code-review`, `java-code-review`, `java-update-design`, `npm-dependency-update` and inspect the `dependencies` shape. Whether these use bare-string or `{name, version}` object form and whether version-ranges are specified is unknown.
- **Exact mechanism by which `scripts/claude-skill install <x>` resolves to a GitHub clone URL**: the script sampled here does `git clone plugin["source"]` where `source` is `./java-dev` in marketplace.json. Either the actual marketplace.json is rewritten before install (not observed) or the installer has additional URL-resolution logic further in the file not sampled (`claude-skill` was sampled to line 130 of ~unknown total). To resolve: fetch the rest of `scripts/claude-skill` to confirm.
- **SessionStart matcher shape**: whether the install-skills-written session-start hook uses `matcher: "startup"`, `"startup|clear|compact"`, or no matcher is not visible from the excerpts sampled. Resolve by fetching the full SKILL.md body or the hook-install block of `scripts/claude-skill`.
- **Plugin.json `description: ">"` glitch**: 2 of 3 sampled plugin.json files have `description: ">"` (literal greater-than sign). This appears to be an artifact of accidentally committing a YAML block-scalar indicator instead of the prose. Unknown whether this affects all 48 or only some; fetch a broader sample to verify and determine whether Claude Code silently falls back to marketplace.json description when plugin.json description is nonsensical.
- **Does the web_installer.py localhost server auto-launch on session start or only on explicit skill invocation?** The `cc-praxis-ui` SKILL.md workflow shows `bash: cc-praxis --no-browser &` inside a skill step — so it's on-demand, not on session start. But the repo's `hooks/check_project_setup.sh` is strictly a nudge, not a server launcher. Resolve by reading all of `cc-praxis-ui/SKILL.md`.
