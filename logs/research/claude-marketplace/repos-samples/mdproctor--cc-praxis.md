# Sample

Mirrors of `https://github.com/mdproctor/cc-praxis`. Aggregator marketplace shipping 48 professional-development skills (Java/Quarkus, TypeScript/Node.js, Python, cross-cutting workflow plugins) plus 8 named bundles, with parallel non-Claude-Code installer scripts (CLI + localhost web UI) operating on a custom marketplace schema extension.

## Marketplace manifest layout

### Single root manifest with relative source under `plugins/<name>/`

Single `.claude-plugin/marketplace.json` at repo root with 48 plugin entries, all `source: "./<plugin-dir>"`. Top-level fields: `name`, `description`, `owner` (with `name`, `url`). No `metadata` wrapper, no `metadata.pluginRoot`, no `$schema`.

### Custom non-schema fields on marketplace entries

Adds a repo-custom top-level `bundles` array with 8 entries — each `{name, displayName, description, skills}` (e.g., `quick-start-java`, `core`, `principles`). Not part of Anthropic's marketplace schema; consumed entirely by the repo's out-of-band installers (`scripts/claude-skill`, `scripts/web_installer.py`). Users installing via `/plugin install` see individual plugins with no access to bundle grouping.

## Plugin source binding

### Relative source pointing to subdirectory

All 48 entries use relative `source: "./<plugin-dir>"`. `strict` field absent on every entry (implicit `true`). No `skills` override observed; no strict-false carving.

## Per-plugin discoverability metadata

### Bare-minimum (name, version, description only)

Per-plugin marketplace entries are minimal: `{name, source, description, version}` only. No `category`, `tags`, or `keywords` on any of the 48 entries.

### `$schema` absence on per-plugin manifests

No `$schema` on `marketplace.json` or on any of the 48 per-plugin `plugin.json` files. Each `plugin.json` is 3-5 lines with `name`, `description`, `version`, occasional empty `dependencies: []`.

## Version coordination

### Dual-file version (manifest pair)

Versions written in `marketplace.json` AND each `plugin.json`. Observed drift: marketplace.json lists `git-commit: 1.0.0` but the plugin's `.claude-plugin/plugin.json` carries `1.0.0-SNAPSHOT`. Commit history shows a single "drop SNAPSHOT — all 49 skills promoted to 1.0.0" batch that did not land consistently. Per docs, for relative sources `plugin.json` wins, so the user-visible version of `git-commit` is `1.0.0-SNAPSHOT`. The repo's own `web_installer.py` reads `marketplace.json`, producing a different answer for the same field.

## Channel distribution

### Pre-release suffix as channel marker (Maven-style)

Plugins use `1.0.0-SNAPSHOT` during development (stripped at release). Custom version comparator in `web_installer.py` (`_version_tuple`) treats `SNAPSHOT` as strictly older than the release counterpart. Not a SemVer pre-release identifier (`-rc`, `-beta`); convention borrowed from the Maven ecosystem (consistent with the repo's Java/Quarkus focus). Mixing `1.0.0` and `1.0.0-SNAPSHOT` across 48 plugins creates ordering ambiguity for naive string-comparison consumers. RELEASE.md documents stable installs as fetching from git tag (`v1.0.0`) — channel separation is communicated via tag pinning rather than a marketplace split.

## Tag and release lifecycle

### Tag-on-main with active cadence (semver discipline)

3 annotated tags on main: `v1.0.0`, `v1.0.1`, `v1.1.0`. Corresponding GitHub releases exist (non-draft) for all three. Trunk-based — RELEASE.md explicitly documents "trunk-based development with git tags". No release branches.

## Plugin-component registration

### Default convention discovery

Every `plugin.json` carries minimal metadata only (`name`, `description`, `version`, occasional empty `dependencies: []`). No `skills`, `commands`, `agents`, `hooks`, `mcpServers` fields anywhere. All component discovery is by directory convention.

## Component composition

### Skills (universal)

Every plugin has a top-level `SKILL.md`, auto-discovered.

### Commands

Every plugin has a `commands/<name>.md`.

### bin

`bin/cc-praxis` ships at repo root, NOT inside any plugin's directory. Not auto-registered with any plugin.

## Plugin-component placement

### Outside plugin directory at repo root

`bin/cc-praxis` lives at repo root rather than inside a plugin directory; `hooks/check_project_setup.sh` also at repo root, NOT inside any plugin and NOT registered via any plugin's `hooks.json`. The hook is installed manually into `~/.claude/hooks/` by the `install-skills` skill, which also wires it into `~/.claude/settings.json` via skill prose. Repo-root `bin/` cannot be auto-registered with any plugin in the claude-plugin sense; the wrapper is reachable only from a local clone whose `bin/` is on the user's shell PATH manually.

## Bin entry mechanism

### Script-relative shell wrapper

`bin/cc-praxis` is a 316-byte, 6-line bash wrapper whose only purpose is `exec python3 "$PLUGIN_ROOT/scripts/web_installer.py" "$@"`. Resolution: `PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"`. No check for `${CLAUDE_PLUGIN_ROOT}` env var, no fallback cascade — strictly script-relative, always. Comment in the file says "Works both from the plugin cache (${CLAUDE_PLUGIN_ROOT}) and from a local clone" but the mechanism is the same path math in both cases. Shebang `#!/bin/bash` (not `#!/usr/bin/env bash`); explicit absolute path is less portable on systems where bash is not at `/bin/bash`. POSIX bash-only — no `.cmd`, `.ps1`, or OS-detecting fallback. Permissions `100755` (executable). The cc-praxis-ui SKILL.md falls back to an explicit `${CLAUDE_PLUGIN_ROOT}/scripts/web_installer.py` for plugin-installed usage; the bin wrapper is only useful from a local clone.

## Dependency installation

### Zero dependencies / stdlib only

Plugin runtime has no managed install. `scripts/web_installer.py` uses only standard library (`http.server`, `json`, `pathlib`, `subprocess`); installed plugins have no Python deps beyond system `python3`. `requirements.txt` (`requests`, `pytest`, `PyYAML`) exists for CI and local dev of the installer scripts, not for plugin runtime. `CLAUDE_PLUGIN_DATA` and `CLAUDE_PLUGIN_ROOT` are not used for install.

## Custom installer alternative

### Localhost web UI installer

`scripts/web_installer.py` runs a localhost HTTP server (port 8765) that serves a UI for browsing and installing skills. Reads `marketplace.json` (including the custom `bundles` field) and writes to `~/.claude/skills/<name>/` via sparse-checkout git-clone — completely outside Claude Code's plugin caching. Stated motivation in README: "The official Claude Code marketplace doesn't yet support automatic dependency resolution."

### CLI installer with sparse-checkout

`scripts/claude-skill` is a standalone CLI the user runs after cloning. Installs into `~/.claude/skills/<name>/` via `git clone --filter=blob:none --sparse`. Has a `--snapshot` flag that fetches from `main` HEAD versus stable-tag resolution. Includes its own dependency resolver (`resolve_dependencies` walks by name; bare-string or `{name}` object form accepted). The sampled installer code does `git clone plugin["source"]` where `source` is `./java-dev` in marketplace.json — a relative path, not a URL — so the actual install URL resolution requires logic further in the file not sampled.

## Session context loading

### User-settings session-start hook installed by a skill

The `install-skills` SKILL.md instructs Claude to write `~/.claude/hooks/check_project_setup.sh` and modify `~/.claude/settings.json` to register it as a user-level session-start hook. Does NOT register via any plugin's `hooks.json`. Hook prints "⚠️ ACTION REQUIRED" directives to stdout that Claude reads as system-level context at session start (per the script's own comment: "Output is read by Claude at session start — messages are directives to act on"). Plain stdout, not the structured `hookSpecificOutput.additionalContext` channel. Because the hook is registered at user level, it persists after plugin uninstall unless `uninstall-skills` explicitly unwinds, runs globally on every session regardless of project, and `/plugin uninstall` cannot clean it up.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks anywhere. The only hook-shaped artifact is `hooks/check_project_setup.sh` (a SessionStart-style nudge), and it is installed into user settings, not registered via any plugin's hooks.json.

## User configuration and authentication

### No user-supplied config

No `userConfig` in marketplace.json, no `userConfig` in any plugin.json across all 48 entries.

### Env var read by script (hidden interface)

`web_installer.py` reads `CLAUDE_SKILLS_DIR` to relocate the install root for tests. Env-var-based test override managed entirely inside the script, not exposed via `userConfig`.

### Markdown block in consumer's CLAUDE.md

The repo-root `CLAUDE.md` declares a `## Project Type` field (`java | skills | blog | custom | generic`) that multiple skills (`git-commit`, `update-claude-md`, `project-health`) read at runtime to dispatch to language-specific sub-skills (`java-git-commit`, `blog-git-commit`). Project-scope user-config-in-CLAUDE.md pattern.

## Plugin-to-plugin coordination

### `dependencies` field declared

Three observed shapes across the 48 plugins: omitted entirely (majority — `cc-praxis-ui`, `adr`, `git-commit`); present and empty (`"dependencies": []` — `install-skills`); per README, `scripts/claude-skill install quarkus-flow-testing` automatically pulls `java-dev + quarkus-flow-dev` so some plugin.json files must contain real dependency arrays (not directly sampled). The repo's resolver accepts bare strings and `{name}` objects (`dep["name"] if isinstance(dep, dict) else dep`); no semver ranges. Dependency resolution is performed client-side by the custom `scripts/claude-skill` and `web_installer.py`, not by Claude Code's `dependencies` field (a v2.1.110+ feature). README: "The official Claude Code marketplace doesn't yet support automatic dependency resolution ([Issue #9444](https://github.com/anthropics/claude-code/issues/9444))."

## Testing

### Pytest with marker-segmented suites

pytest with extensive coverage (35+ test files in `tests/`). `pytest.ini` at repo root defines a `slow` marker (no `[tool.pytest.ini_options]` in pyproject.toml — repo has no pyproject.toml). Per-plugin `tests/test_cases.json` fixtures inside skill directories (e.g., `adr/tests/test_cases.json`) drive behavior tests from a central `test_base.py`. Test deps in `requirements.txt` (`requests`, `pytest`, `PyYAML`); no `requirements-dev.txt`.

### Centralized `tests/` placement

`tests/` at repo root (flat layout), plus per-plugin `tests/test_cases.json` fixtures inside skill directories.

## CI workflow shape

### Multi-workflow split by trigger and concern

Two workflows: `.github/workflows/skill-validation.yml` (CI validators + tests) and `.github/workflows/pages.yml` (Jekyll docs site → GitHub Pages). skill-validation triggers: `push: branches: [main]`, `pull_request: branches: [main]`, `workflow_dispatch`. pages triggers: `push: branches: [main]`, `workflow_dispatch`.

### Action-pinning conventions

Major-version tags only: `actions/checkout@v4`, `actions/setup-python@v5`, `ruby/setup-ruby@v1`, `actions/configure-pages@v5`, `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4`. No SHA pinning. Built-in `cache: 'pip'` on `actions/setup-python@v5`; `bundler-cache: true` on `ruby/setup-ruby@v1`; no separate `actions/cache`. `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` env var set at job-scope (Node-upgrade workaround).

## Marketplace validation

### Tiered validator driver

A single Python driver (`scripts/validate_all.py`) invoked with `--tier {commit,push,ci}` runs different validator sets at different rigor levels; CI runs all three tiers sequentially. Same runner, escalating flag — distinct from per-stage matrices or one-workflow-per-validator-type. The validator suite includes `validate_frontmatter.py`, `validate_structure.py`, `validate_doc_structure.py`, `validate_references.py`, `validate_links.py`, plus 15+ others targeting skill content. The tiered concept is undocumented in the workflow YAML — readers must open `validate_all.py` to learn which validators run at which tier. The validator suite targets skill / doc content, not marketplace.json schema; no validator checks marketplace-plugin-entry schema conformance or version-drift between marketplace.json and plugin.json.

### Frontmatter validation by grep

`validate_frontmatter.py` and `validate_blog_frontmatter.py` validate skill-frontmatter shape.

## Release automation

### No release automation / manual

Fully manual per RELEASE.md: bump `plugin.json`, commit, tag annotated, push `--tags`. GitHub releases (3 exist, all non-draft) created manually via the GitHub UI or `gh release create`. No tag-sanity gates (no workflow verifies tag-on-main or that `plugin.json` version matches the tag). No CHANGELOG.md; release notes written per-release in the GitHub release body.

## Documentation surface

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` at repo root (~450 lines: install guide, project-type table, skill catalog, bundle descriptions, commit workflow, key features, contributing). `docs/architecture.md` at repo root. `CLAUDE.md` at repo root (declares project type, no-AI-attribution rule, project identity). No `CHANGELOG.md`.

### Heavy doc surface with meta-project artifacts

Repo-root meta-docs: `DESIGN.md` (architectural-decisions doc, Java-flavored), `PHILOSOPHY.md`, `QUALITY.md`, `HANDOFF.md`, `IDEAS.md`, `RELEASE.md`. The `handover` and `idea-log` plugins are themselves bootstrapped here. Doubles as dogfooding but mixes "repo-own meta-docs" with "user-facing skill docs" (which live in `docs/` and publish to GitHub Pages at `mdproctor.github.io/cc-praxis`).

### SKILL.md as primary doc for the skill component

Each plugin has only `SKILL.md` — no per-plugin README.

## License declaration

### Single repo-level license

Apache-2.0 declared at repo root.

## Community health files

### Bare minimum (LICENSE only)

LICENSE present (Apache-2.0). No `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`. Repo-meta files (`DESIGN.md`, `PHILOSOPHY.md`, `QUALITY.md`, `HANDOFF.md`, `IDEAS.md`, `RELEASE.md`) ship instead.

## Source layout

### Single tree (plugin equals repo)

Single tree: 48 plugin subdirectories at repo root (`./<plugin-dir>`).

## Cross-role tools

### Python (stdlib + pip + uv)

`web_installer.py` and `scripts/claude-skill` are Python; tests use pytest. No `uv`, no plugin-runtime venv.

### bash

`bin/cc-praxis` shell wrapper.
