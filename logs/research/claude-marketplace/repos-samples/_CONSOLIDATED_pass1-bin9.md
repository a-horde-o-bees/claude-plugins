# Sample

Pass-1 Phase-1a partial for bin 9. Functional decomposition of Vortiago/mcp-outline, ZhuBit/cowork-semantic-search, and a3lem/my-claude-plugins, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How the repo declares itself to Claude Code's plugin discovery system — the file(s) that let `/plugin marketplace add` resolve the repo to one or more installable plugins.

### Single marketplace.json at repo root

`.claude-plugin/marketplace.json` lives at repo root and lists plugin entries. Top-level fields are `name`, `owner`, optional `$schema`, and a `plugins` array; some authors wrap a `metadata` object carrying `description` and (rarely) `pluginRoot`. Plugin entries are siblings of the marketplace manifest. Appropriate for repos that intend to be addable as a marketplace by name (`/plugin marketplace add owner/repo`). `$schema` adoption is inconsistent — present on some manifests, absent on others.

### Repo doubles as both marketplace and single plugin

`.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` coexist at repo root, with the marketplace's sole plugin entry pointing at `source: "./"` (relative self-reference). Appropriate when the repo's purpose is one MCP server / one plugin and the author wants discoverability without a separate distribution repo. Cost: marketplace entry duplicates `plugin.json` fields (name, description, version, author, license) and there is no structural prevention of drift — keeping them in sync depends on author discipline or a bump script.

### No marketplace manifest

Repo ships only `.claude-plugin/plugin.json` (no `marketplace.json`). Installation is out-of-band — users clone the repo and edit their own MCP host config manually. Appropriate when the author treats the work as a portable MCP server first and a Claude Code plugin only secondarily, but it means the plugin cannot be installed by `/plugin marketplace add` workflows. The `.claude-plugin/plugin.json` becomes ornamental from Claude Code's perspective; the load-bearing config is whatever `.mcp.json` template the README tells the user to paste into their own project.

## Plugin source binding

How marketplace entries point at the plugin's content directory.

### Relative path under marketplace repo

Every plugin entry uses `"./plugins/<name>"` (or `"./"` for self-reference). Plugin source travels with the marketplace repo; pinning the marketplace pins all plugins together. Appropriate for monorepo marketplaces where author owns every listed plugin. `strict` field is universally absent (defaults to implicit true); no `skills` override observed at the entry level.

## Version authority

Where the canonical version string lives, and how multiple representations stay aligned.

### Single source — plugin.json only

`plugin.json` carries `version`; marketplace entries omit `version` entirely (no duplication risk). Appropriate when the marketplace is just a routing layer and Claude Code reads version from `plugin.json` at install time. Drift-free by construction. Cost: per-plugin discipline only — plugin.json may itself drift from a CHANGELOG or a SKILL.md frontmatter version field maintained by the same author.

### Multi-file with bump script as enforcer

Version lives simultaneously in `server.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and a regex-pinned arg in `.mcp.json` (e.g. `uvx mcp-outline==<ver>`). A `scripts/bump_version.py` rewrites all four atomically and validates that the new version is a legal semver bump from the previous. Appropriate when the repo publishes to multiple registries (Claude Code marketplace + MCP registry + PyPI) that each demand the version in their own manifest format. The script is the single source of truth at author-time; structural drift is prevented by always running it instead of editing files individually. CI does not re-run the validator, so a manual edit to one file leaves the other three behind silently.

### Multi-file with no enforcer

`plugin.json` and `pyproject.toml` both carry `version`; both must be bumped manually. No script, no hook, no CI check. Drift-prone — first observed drift is when a CHANGELOG documents 2.1.0, plugin.json reads 1.0.0, and SKILL.md frontmatter says 3.2.0 in the same plugin. Common in personal/early repos before tooling is added.

## Plugin-component registration style

How `plugin.json` declares which components ship in the plugin.

### Default discovery (convention-based)

`plugin.json` carries only metadata fields (`name`, `description`, `version`, `author`, `keywords`, `homepage`, `repository`, `license`). No `mcpServers`, `agents`, `skills`, `commands`, `hooks`, or `monitors` arrays. Claude Code auto-discovers components from conventional directory names (`agents/`, `skills/`, `commands/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json`). Appropriate when the plugin uses standard layout and component count is small enough that explicit registration adds no value. The dominant choice across the bin's samples.

## Component mix

Which Claude Code component types the plugin ships. Cross-plugin observations on what surfaces beyond the metadata.

### MCP server (`.mcp.json`)

Plugin ships a `.mcp.json` (at repo root or under `.claude-plugin/` per spec) declaring an MCP server invocation. Appropriate when the plugin's value is bridging an external service to MCP. Pin style varies — exact-version pins (`uvx mcp-outline==1.8.0`) trade fresh-install for reproducibility; unpinned `uvx <pkg>` resolves to the latest wheel each invocation. A `.mcp.dev.json` companion that swaps to in-repo source (`uv run <pkg>`) is one approach to dev-vs-prod separation. Misplaced repo-root `.mcp.json` with hardcoded absolute paths from the author's machine appears as a leaked dev artifact in lower-discipline samples.

### Slash command

`commands/<name>.md` with frontmatter `name`, `description`, `argument-hint`. Body instructs Claude on what to do (e.g., call a specific MCP tool with the argument). Appropriate when one user-invoked entry point is the primary affordance.

### Skill

`skills/<name>/SKILL.md` is the canonical layout per spec. Some samples place loose `skills/<name>.md` files at the skills/ root with command-style frontmatter, which is non-canonical and appears to be a misunderstanding of skills-vs-commands or leftover scaffolding.

### Agent

`agents/<name>.md` with frontmatter declaring `name`, `description` (often with `<example>` blocks describing trigger conditions), `model` (haiku/sonnet), optional `color`, and either `mcpServers: [<server-name>]` (allowlist binding the agent to a specific MCP server) or `allowed-tools: <comma-list>` (plain tool names, no permission-rule syntax). Agent body carries the prompt — sometimes including defensive directives like "USE THE TOOL-CALLING INTERFACE … NEVER simulate, write out, or fake function calls" guarding against model hallucination of tool calls. Caller-supplied parameters can be encoded in prose (e.g., the agent body declares quick/medium/very-thorough modes the caller names at invoke time).

Non-standard frontmatter fields appear: `allowed-prompts` with nested `{tool, prompt}` pair lists is observed but is not in the documented Claude Code reference — possibly an experimental convention, possibly silently ignored.

### Hook (SessionStart)

`hooks/hooks.json` registering a SessionStart hook command. Two distinct purposes observed under the same mechanism — see *Dependency installation* (install on session start) and *Session context loading* (inject rules on session start). No matcher is the common case, meaning the hook fires on startup, clear, and compact alike.

### LSP config

`.lsp.json` — minimal-viable plugin can ship only `.claude-plugin/plugin.json` + `.lsp.json` + README, with no skills/commands/hooks/agents at all. Demonstrates the floor of plugin footprint.

### Marketplace-root shared bin

`bin/<wrapper>` at the marketplace root (not under any individual plugin), with each consuming plugin shipping a symlink at `plugins/<name>/hooks/<wrapper>` pointing at the shared file. Author's documented intent is DRY at the marketplace level — one wrapper, many plugin consumers. See *Bin-wrapped CLI distribution* for the constraint this creates around symlink target form (relative survives the install copy; absolute breaks on any non-author machine).

## Server runtime (MCP)

The execution path that actually serves MCP requests when the plugin is active.

### Pinned PyPI wheel via `uvx`

`.mcp.json` declares `uvx <pkg>==<exact-ver>` as the launch command. `uvx` (Astral's ad-hoc runner) fetches the exact pinned wheel into its cache (`~/.cache/uv/`) per invocation. Appropriate when the author publishes the server independently to PyPI and wants the plugin to lock to a specific wheel. Constrains: any Python 3.10+ interpreter on the host accepted (pure-Python wheel); no plugin-side venv to manage; old plugin tags will always pull old wheels even after upstream patches; no SessionStart install hook needed. The plugin is effectively a thin client of PyPI.

### Local venv built by SessionStart hook

A `scripts/setup.sh` invoked from `hooks/hooks.json` SessionStart creates `${CLAUDE_PLUGIN_DATA}/venv`, runs `python3 -m venv`, upgrades pip, then `pip install -r requirements.txt`. Appropriate when the plugin is the server, not just a client of one — runtime code lives in the repo and needs a Python environment to run. Constrains: `python3` from PATH (no version pin); install must complete before the MCP server is launched; venv path must thread through to the MCP launch command (commonly broken — see pitfalls). System-tool dependency on `shasum` (BSD/macOS) vs `sha256sum` (Linux) — no fallback observed.

### In-place stdlib script (no installer)

The Python script (e.g., `scripts/spectl.py`) is run directly via system `python3`, importing only stdlib (argparse, json, os, re, shutil, string, sys, datetime, pathlib, random). No venv, no `uv run`, no pip-install. Appropriate when the author deliberately constrains the plugin to stdlib to eliminate install friction. Cost: a `pyproject.toml` may declare `requires-python = ">=3.14"` for a `uv sync` path that no runtime code path actually exercises — the floor is functionally unenforced because the script's stdlib-only imports work on much earlier Python.

## Dependency installation

How runtime dependencies (separate from the plugin's metadata) get onto the user's machine.

### Delegated to PyPI runner

No plugin-side install state. `uvx` fetches the wheel on demand; the plugin directory holds no installed deps. No SessionStart install hook. Appropriate when dependencies belong to an upstream package the plugin only references. Failure mode is a standard MCP server launch failure — Claude Code reports the missing `uvx` or the unresolvable package; no plugin-specific error path.

### SessionStart venv install with hash gating

`scripts/setup.sh` invoked from SessionStart hook. Mechanism:

1. Compute `sha256` of `requirements.txt` via `shasum -a 256` (no `sha256sum` fallback)
2. Read previous hash from `${CLAUDE_PLUGIN_DATA}/requirements.hash` if present
3. If hash differs OR venv missing: create venv, upgrade pip, run `pip install -r requirements.txt`, then write the new hash
4. Hash write happens only after install succeeds (`set -e` ensures abort-before-write on failure) — failed install leaves stale hash so next session retries

Appropriate when the plugin owns its runtime and dependencies are non-trivial. Constraints/costs: hash is over the declared-deps file, not a lockfile, so transitive-dep upstream patches are invisible; no `set -u`/`-o pipefail`; partial venv from a mid-pip failure isn't cleaned (`pip install` re-attempt usually self-heals); SessionStart fires on clear/compact too without a matcher (cheap due to the hash check, but not zero); install location may not be where the MCP launch command points at (a bug surfaces when README's "install from source" creates `<checkout>/.venv` but the SessionStart hook creates `${CLAUDE_PLUGIN_DATA}/venv` and the MCP config references the former — two parallel venvs, neither aware of the other).

### No installer

Plugin uses stdlib-only Python or expects the user to have the deps already. No SessionStart install path. Appropriate when the plugin avoids runtime deps as a design property; expressed as "the plugin set deliberately avoids adding runtime deps."

## Bin-wrapped CLI distribution

How standalone executables ship with a plugin and resolve at runtime.

### Marketplace-root bin with per-plugin symlink

`bin/<wrapper>` at the marketplace root is a stdlib Python script with `#!/usr/bin/env python3` shebang. Each consuming plugin ships `plugins/<name>/hooks/<wrapper>` as a git-tracked symlink (mode 120000) pointing at the shared file. Hook configuration invokes via `${CLAUDE_PLUGIN_ROOT}/hooks/<wrapper>`. The wrapper resolves the plugin name from `plugin.json` and the marketplace name by walking up to `.claude-plugin/marketplace.json`, then enriches its output with provenance metadata. Appropriate when multiple plugins in one marketplace want a shared executable without copy-paste duplication.

Critical constraint: Claude Code installs by copying the plugin directory only, so the symlink target must be relative (e.g., `../../../bin/<wrapper>`) to survive the copy. Absolute symlink targets keyed to the author's home directory break on every other machine — the install ships dead symlinks. Observed in lower-discipline form, where the documented intent is correct but the committed symlink targets are absolute.

### No `bin/`

Plugin's runtime entry is the MCP server itself, launched directly by the host's MCP config. Appropriate when there's nothing the user invokes outside an active session.

## Tool-use enforcement

PreToolUse, PostToolUse, and PermissionRequest/PermissionDenied hooks that police tool calls at runtime.

### None

No samples in the bin install enforcement hooks. Plugins relying on read-only or restricted tool surfaces enforce that at the MCP server level (e.g., `OUTLINE_READ_ONLY=true` env var passed through `.mcp.json`) or via prose directives in agent prompts ("perform read-only operations only") — no structural enforcement at the Claude Code hook layer. The MCP server's tool-registration phase is the actual enforcement point; the Claude Code hook layer is bypassed entirely.

## Session context loading

Hooks that inject content into the session prompt at startup.

### SessionStart stdout as system-reminder

Hook command (Python or bash) prints a `<system-reminder>` block to stdout. Claude Code captures SessionStart stdout and treats it as an additional system message — a legacy convention pre-dating the structured `hookSpecificOutput.additionalContext` JSON channel. Multiple plugins in one marketplace can register the same pattern, each contributing rules. Appropriate for "always-on rules" the agent should see at session start. No matcher means the hook also fires on `clear` and `compact`, re-injecting the rules each time context is reset — generally desired since the cleared session has lost them.

Cost considerations: 2-3 second hook timeouts are tight; on cold start with slow I/O, reading multiple markdown files and walking up for `marketplace.json` may approach the limit. No retries, no fallback. Failure posture is fail-open — `exit 0` when sources are absent rather than blocking the session.

### Provenance-decorated stdout

A wrapper script (e.g., `bin/inject-rules`) doesn't just concatenate file contents — it resolves the plugin name from `plugin.json` and the marketplace name by walking up to `.claude-plugin/marketplace.json`, then decorates each injected file's path in the emitted `<system-reminder>` block as `"<path> from plugin <name>@<marketplace>"`. Gives the agent provenance for injected rules so it can attribute and reason about which plugin's rule applies. Refines the bare stdout-cat pattern by encoding metadata the agent can use to disambiguate.

### Echo-as-prompt for SESSION_SETUP

A SessionStart hook with a literal `echo` command reminding the agent to execute a `# Session Setup` section in CLAUDE.md. Fires on clear/compact too without a matcher, re-prompting after every context reset. Crude but functional — the agent treats the echoed string as a system message and acts on it.

### None

Plugin ships no SessionStart context-injection. Users get the host's default system prompt plus whatever MCP server tool descriptions surface — nothing else. Appropriate for plugins that are pure tool surfaces; the plugin's value is the tools, not pre-loaded instructions.

## User configuration surface

How users configure plugin behavior — secrets, paths, toggles.

### `userConfig` block in `plugin.json`

Not observed in any sample in this bin. The declarative surface that would let Claude Code's config UI manage plugin settings (with `sensitive: true` for secrets, schema-validated fields) is absent across all three.

### Plain OS env var

The plugin reads env vars directly via `os.environ.get` (e.g., `OUTLINE_API_KEY`, `LANCEDB_PATH`, `AUTO_MEMORY_DIR`). For the MCP-server case, `.mcp.json` declares passthroughs via shell-style `${VAR:-default}`. Appropriate when the user already manages the secret/config externally; constrains: not surfaced in Claude Code's config UI, no `sensitive: true` masking, no schema validation, no in-plugin prompt. The user has to know to set the var. For required secrets a missed-opportunity pattern — `userConfig` with `sensitive: true` is the idiomatic surface.

### MCP-registry-schema sidecar

`server.json` (the modelcontextprotocol/registry schema) declares `OUTLINE_API_KEY` with `isSecret: true` — the MCP-registry equivalent of `sensitive: true`. The same plugin's `plugin.json` has no `userConfig`. The two registries each demand their own config-schema dialect, and the author honors the MCP one but not the Claude Code one. Demonstrates that "no `userConfig`" can mean "we use a different registry's secret-marking" rather than "we don't acknowledge secrets exist."

## Documentation surface

What documentation files ship and what they cover.

### Comprehensive single README + ad-hoc CLAUDE.md

Repo-root `README.md` is the consumer-facing entry point — features, prereqs, install instructions for multiple MCP clients (Claude Code, Cursor, Windsurf, Cline), per-client config templates, env-var catalog, tool catalog, dev quick-start, troubleshooting. `CLAUDE.md` (when present) carries developer/agent guidance — architecture summary, registration patterns, test conventions, release runbook. The two often conflate concerns — `CLAUDE.md` mixes architecture-reference content with operational procedure, acceptable for solo projects but blurs the project-doc-separation discipline of larger systems.

### Per-plugin README mixed coverage

In multi-plugin marketplaces, per-plugin READMEs are uneven — some plugins ship one, others don't, with no rule. Tied to plugin maturity and author attention rather than a discipline rule.

### Committed planning artifacts

`IMPLEMENTATION_PLAN.md` (large, 44 KB), `memory/project_*.md` files, and `memory/MEMORY.md` indexes shipped as first-class repo content (not gitignored). The author's working notes, design context, and personal Claude Code memory become public artifacts. Unusual; most repos either gitignore working notes or isolate to `docs/`. Exposes paths and process detail not strictly needed by consumers, but allows the author to pick up where they left off across machines.

### License absent

No `LICENSE` file at repo root and the GitHub API `license` field is null. Means default copyright applies — anyone cloning has no explicit reuse permission beyond what GitHub's ToS provides. For a "personal plugins for own use" repo the author probably intends more permissive use; the gap is silent.

### Per-plugin CHANGELOG with hand-maintained entries

Some plugins carry `CHANGELOG.md` resembling Keep a Changelog format (`## [x.y.z] - YYYY-MM-DD` headers with Added/Changed/Removed subsections). Hand-maintained — no automation aligns the CHANGELOG with `plugin.json` version, so divergence is normal (CHANGELOG documents 2.1.0 while `plugin.json` still reads 1.0.0).

## Tag and release lifecycle

Whether the repo cuts version tags and how releases are produced.

### Tag-on-main with active cadence

Tags `vX.Y.Z` placed directly on commits merged to `main` (no release branch). 18 tags over ~13 months, mostly major v1.x cuts in a burst. No pre-release suffixes used in practice, though the release pipeline reserves `-rc` semantics. Pre-commit hooks include ruff + pytest but no auto-bump. Version bumps are manual via a `poe bump-version` task.

### Tag-on-main with single release

Sole tag is `v0.1.0` on `main`. First release; cadence patterns aren't established. No automation aligns the tag with `plugin.json` version (coincidence-by-discipline so far).

### No tags, no releases

`git/refs/tags` returns 404; releases are empty. Versions live only in per-plugin `plugin.json` files and are bumped manually when the author remembers. The "lazy commit" message on HEAD signals deliberate informality. Appropriate for a personal repo with no downstream consumers — the marketplace name is the install handle, not a version pin.

## Pre-commit and local-quality gating

Hooks running at commit time to enforce quality before the change leaves the local machine.

### Multi-tool pre-commit including pytest

`.pre-commit-config.yaml` runs ruff format check, ruff lint, pyright type-check, pytest (`uv run pytest tests/ -v`), plus basic hygiene hooks. Pytest at commit time is unusual — most projects pre-commit ruff/format only — and forces every commit to pass the unit suite. Costlier per commit but catches breakage at the lowest-friction point. Plus standard hygiene (trailing whitespace, end-of-file fixer, etc.).

### None

No `.pre-commit-config.yaml`, no `.githooks/`, no commit-time enforcement. Commits land regardless of test or lint state. The implicit gate is the author's local discipline.

## CI and quality enforcement

GitHub Actions workflows running on push/PR — what they verify and what they don't.

### Multi-workflow with version matrix and SHA-pinned actions

Eight workflows (ci.yml, e2e.yml, publish-pypi.yml, release.yml, docker-build.yml, codeql.yml, claude.yml, claude-code-review.yml). `ci.yml` runs ruff format check, ruff lint, pyright type-check, pytest with junit XML + coverage; matrices Python 3.10 × 3.11 × 3.12 × 3.13 (`fail-fast: false`); ubuntu-latest only. `e2e.yml` brings up Docker Compose against the real upstream service. CodeQL scans Python source plus the workflow files themselves (`language: actions`) with `security-extended` queries, on a weekly cron. Third-party actions are SHA-pinned with `# v<tag>` comment for human readability; Dependabot weekly-updates the SHAs. Some action references still use floating `@v6`/`@v4` tags — inconsistency.

Caching: `astral-sh/setup-uv` with `enable-cache: true` (uv's GH-Actions backend); Docker uses `type=gha` buildx cache. `claude.yml` and `claude-code-review.yml` ship fully wired with credentials but triggers commented out and only `workflow_dispatch: {}` enabled — deliberate opt-in staging of Anthropic automation, easy to flip on later.

Pitfall: pytest `addopts = "-m 'not e2e and not integration'"` combined with markers named `integration` and `e2e` means a bare `pytest` silently skips a category developers may not realize is there.

### None

No `.github/workflows/` directory. All testing is local/manual. README claims may not be enforced (e.g., "56 tests covering …" is unverifiable on PRs). Regressions caught only when the author runs pytest locally before committing. Common in personal/early repos.

## Test framework and coverage

How tests are organized when present.

### Pytest with marker-segmented suites

Pytest with markers (`integration`, `e2e`) routing tests into tiers. Default `addopts` excludes the heavier markers so bare `pytest` runs unit tests only. `tests/` at repo root, split into `features/`, `e2e/`, `utils/`. Adjacent markdown sidecars (`test_*.md`) appear next to some tests as human-written per-test documentation. Dependency declared via uv-native `[dependency-groups].dev`. Local invocation via `poe test-unit`/`test-integration`/`test-e2e` tasks (poethepoet).

### Pytest, flat tests directory

`tests/` at repo root, flat layout (`test_chunker.py`, `test_indexer.py`, `test_mcp_tools.py`, `test_parsers.py`, etc.). Pytest config in `[tool.pytest.ini_options]` with `pythonpath = ["."]`. No marker tiers. Local-only invocation per README (`pytest tests/ -v`).

### Pytest scoped to one plugin within a marketplace

Tests live inside the plugin directory (`plugins/<name>/tests/`) with a `conftest.py` that runs the plugin's main script as a subprocess via `sys.executable`, self-locating relative to the test file. The other plugins in the same marketplace ship zero tests. Pytest config relies on discovery defaults. Pytest version floor (`pytest>=9.0.2`) tightly couples to a high Python floor (`>=3.14`).

## Release automation

Workflows that run on tag push to publish artifacts.

### Triple-target publish on single tag

On `push: tags: ['v*']`, three workflows fire concurrently:

1. PyPI publish via `pypa/gh-action-pypi-publish` with OIDC trusted publishing (no stored secrets); a TestPyPI sub-job conditional on `contains(github.ref, '-rc')` routes pre-releases to TestPyPI; a fourth job authenticates to the MCP registry via GitHub OIDC (`./mcp-publisher login github-oidc`) and rewrites `server.json` in the ephemeral checkout with `jq` before publishing
2. GitHub Release via raw `gh release create --generate-notes --notes-start-tag $(git describe --tags --abbrev=0 ${ref}^)` — auto-computes previous tag for changelog range
3. Multi-arch Docker (amd64+arm64) via `docker/setup-qemu-action` + `docker/setup-buildx-action` + `docker/metadata-action` computing a six-form tag set (`{{version}}`, `{{major}}.{{minor}}`, `{{major}}`, `latest`, branch, short-SHA); single-arch validate (curl `/health` retry loop) before multi-arch final build; only pushes on `refs/tags/v*`

Tag-form fragility: `release.yml` and `docker-build.yml` lack the `-rc` filter that `publish-pypi.yml` has, so a pre-release tag also cuts a GitHub Release and pushes a `latest` Docker image — `latest` would leak an rc build. The MCP-registry job rewrites `server.json` in-checkout but doesn't commit it back; if local source-of-truth disagrees with the tag-derived value, the registry silently wins for that publish.

### Manual release creation

No `.github/workflows/release*.yml`. Tags created manually via GitHub UI or `gh release create`. No automation verifies tag matches `plugin.json` version. Appropriate for first-release / personal-scope projects.

### None — no releases at all

No tags, no release workflows. Versions are mutable strings in `plugin.json` files, not pinned anywhere downstream consumers can resolve.

## Distribution channels

Where the artifact ends up published / how end users consume it.

### Multi-registry: PyPI + MCP Registry + ghcr.io + Claude marketplace

Same plugin published to four discovery surfaces with four manifest formats: `plugin.json` for Claude Code, `server.json` for the official MCP registry, PyPI metadata via setuptools-scm, ghcr.io image (multi-arch). A separate `glama.json` (three-line maintainer declaration) targets glama.ai's MCP server directory as a fifth surface. The bump script keeps the local manifests in lockstep; CI handles the publishes. Appropriate when the author wants the server to be installable from whichever ecosystem the user already lives in.

### Marketplace + git-clone-only

Plugin metadata exists for Claude Code's plugin system but the primary install path documented in README is "clone the repo + paste this `.mcp.json` template into your own project, substituting your own absolute paths." Per-client templates for Claude Code / Cursor / Windsurf / Cline. The plugin is explicitly marketed as MCP-portable, not Claude Code-specific. The `.claude-plugin/plugin.json` becomes secondary; the load-bearing config is whatever the user pastes.

### Marketplace only

Plugins are installed via `/plugin marketplace add <owner>/<repo>` and that's the only intended path. No PyPI, no Docker, no git-clone instructions for the plugin functionality itself.

## Ecosystem health automation

Dependency updates and security scanning beyond bare CI.

### Dependabot + CodeQL + grouped updates

`.github/dependabot.yml` weekly updates for `pip` (grouped minor+patch into a single PR labeled `minor-and-patch`) and `github-actions` (SHA bumps for the SHA-pinned action references). CodeQL scheduled weekly with `security-extended` queries scanning Python source plus workflow files themselves (`language: actions`). Reduces PR churn while keeping the supply chain monitored.

### None

No Dependabot config, no CodeQL workflow. Dependency updates are author-discretion only.

## Marketplace validation

Whether anything checks marketplace.json/plugin.json structural validity.

### None

No CI step validates `.claude-plugin/marketplace.json` or `.claude-plugin/plugin.json` schema across any sample in the bin. `$schema` URLs are sometimes declared (`https://anthropic.com/claude-code/marketplace.schema.json`) but no in-repo tool runs schema validation against them. Drift between marketplace `description` and per-plugin `plugin.json` `description` (silent and unreconciled in practice), missing `version` fields on some `plugin.json`s, non-semver shorthand like `"1.1"` — all would be caught by schema validation but aren't. The closest to validation is a `bump_version.py` that checks semver-bump validity on author-initiated runs, not as a CI guard.

## Plugin-to-plugin coordination

How plugins in the same marketplace declare relationships.

### Documented prose only

Multi-plugin marketplaces describe coordination in README ("This plugin doesn't manage any store directly – it routes to <other-plugin> and <other-plugin>") but no `dependencies` field in `plugin.json` enforces installation. A user installing only the routing plugin gets broken behavior. Coordination is by discipline, not structure.

### None

Single-plugin marketplaces don't surface this concern.

## Test stack — Docker

(Cross-role: Docker also surfaces under *Distribution channels* via ghcr.io image and under *Release automation* via the multi-arch build pipeline.)

### Docker Compose for E2E

`e2e.yml` brings up a full Docker Compose stack (e.g., the upstream service + an OIDC provider) before running the e2e-marked subset. Pinned to a single Python version (no matrix) — e2e is an integration check, not a portability check. Appropriate when the system under test is meaningful only against a real running peer.
