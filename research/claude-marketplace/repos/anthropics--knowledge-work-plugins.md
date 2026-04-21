# anthropics/knowledge-work-plugins

## Identification

- **URL**: https://github.com/anthropics/knowledge-work-plugins
- **Stars**: 11,398
- **Last commit date**: 2026-04-09 (latest commit on `main`; repo last pushed 2026-04-17)
- **Default branch**: main
- **License**: Apache-2.0 (repo-level `LICENSE`; most Anthropic-owned plugin directories ship a copy of the same Apache-2.0 file; partner-built plugins ship their own LICENSE — `slack` MIT, `zoom-plugin` MIT, `apollo` MIT, `common-room` Apache-2.0-style, `brand-voice` Apache-2.0-style)
- **Sample origin**: primary (Anthropic-owned) — but functions simultaneously as an aggregator: 18 of 41 plugin entries are external `url`-source pins and 2 are `git-subdir` pins
- **One-line purpose**: "Plugins that turn Claude into a specialist for your role, team, and company. Built for Claude Cowork, also compatible with Claude Code." (README)

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root (16 KB, 41 plugin entries). A second, self-contained `.claude-plugin/marketplace.json` also exists nested inside `partner-built/brand-voice/` — see §17.
- **Marketplace-level metadata**: no `metadata` wrapper at top level; root-level keys are just `name`, `owner`, `plugins`. No top-level `description`. (The nested `brand-voice` marketplace does use `metadata.{description, version, pluginRoot}` — see §17.)
- **`metadata.pluginRoot`**: absent at the root marketplace; present (`"."`) inside the nested `brand-voice/.claude-plugin/marketplace.json`.
- **Per-plugin discoverability**: mixed by origin.
  - The 13 Anthropic-owned entries (productivity, sales, finance, …, pdf-viewer) use only `name` + `source` + `description`. No `category`, no `keywords`, no `tags` at the marketplace-entry level.
  - The 5 partner-built entries served from `./partner-built/<name>` add `author.name` on the marketplace entry.
  - The 23 external `url`/`git-subdir` entries variably add `category` (e.g., planetscale `database`, zapier `productivity`, ai-firstify implicit none) and `homepage`. `keywords` appear only in per-plugin `plugin.json` files, never in marketplace entries.
- **`$schema`**: absent.
- **Reserved-name collision**: no. `name` uses role-scoped slugs (sales, finance, …) and partner-prefixed slugs (`slack-by-salesforce`, `zoom-plugin`, `apollo`). Nothing collides with reserved words.
- **Pitfalls observed**: the marketplace entry for `figma` uses `source.source: "url"` without a `sha` pin (all other 17 `url` entries pin `sha`). This yields non-reproducible installs for that one plugin — appears to be an oversight rather than intentional "track main". Marketplace-entry fields mix three provenance profiles (Anthropic-internal, partner-built-inline, external-repo) with no uniform field set, which makes client-side schema validation awkward.

## 2. Plugin source binding

- **Source format(s) observed**: 21 × `./<relative-path>` (string form — 13 Anthropic-owned at repo root + 5 partner-built under `partner-built/` + 3 later-added role plugins like `engineering`, `human-resources`, `design`, `operations` also relative + pdf-viewer), 18 × `{source: "url", url, sha}`, 2 × `{source: "git-subdir", url, path, ref, sha}`. String-form `./...` is by far the norm for in-repo plugins.
- **`strict` field**: absent on every marketplace entry. Discovery is implicit (default-true semantics per the plugin spec).
- **`skills` override on marketplace entry**: absent. No marketplace entry carves a subset of a plugin's skill tree.
- **Version authority**: per-plugin `plugin.json` only. The marketplace entry never carries `version`. Anthropic-owned plugins drift independently (most at `1.2.0`, `data` at `1.1.0`, `bio-research` at `1.1.0`, `cowork-plugin-management` at `0.2.2`, `pdf-viewer` at `0.2.0`). Partner-built range `1.0.0`–`1.1.0`. No drift risk between two sources of truth.
- **Pitfalls observed**: the `figma` entry's missing `sha` (§1) means its marketplace entry accepts whatever is at HEAD of the external repo — effectively unversioned. Also, `brand-voice/.claude-plugin/plugin.json` declares `version: "1.0.0"` while the root marketplace entry has no version field, so clients cannot know what version they're pulling without cloning the source.

## 3. Channel distribution

- **Channel mechanism**: no split. Single marketplace consumed by both Claude Cowork (primary) and Claude Code (secondary). README tells Code users to run `claude plugin marketplace add anthropics/knowledge-work-plugins`, implying `@main` pinning by convention rather than by repo-side channeling.
- **Channel-pinning artifacts**: absent. No `stable-tools`/`latest-tools` pattern, no release/latest branch split.
- **Pitfalls observed**: external `url` entries pin to specific SHAs, so marketplace re-updates depend on manual `sha` bumps by a maintainer editing `marketplace.json`. There is no automated sync pipeline visible.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: none — `gh api /repos/.../tags` returns an empty array. Repo uses 0 tags.
- **Release branching**: none. 20+ feature branches exist (`add-plugin/*`, `fix/*`, `ci/verify-community-merged`, `bump-versions-command-deprecation`, etc.) but no `release/*` or `v*` lineage.
- **Pre-release suffixes**: none observed; versions are all plain semver in `plugin.json`.
- **Dev-counter scheme**: absent.
- **Pre-commit version bump**: no — no `.pre-commit-config.yaml`, no husky config, no git hooks shipped in-tree.
- **Pitfalls observed**: with no tags and no releases, version changes are only visible inside each `plugin.json`. Commit history shows periodic `bump-versions-*` branches, suggesting manual batch bumps rather than per-PR bumps. Consumers who pin `@main` effectively take whatever version is committed.

## 5. Plugin-component registration

- **Reference style in plugin.json**: default discovery only. Every `plugin.json` examined (productivity, pdf-viewer, cowork-plugin-management, apollo, brand-voice, zoom-plugin, slack-by-salesforce, common-room) contains only `name` + `version` + `description` + `author` (+ optional `homepage`/`repository`/`license`/`keywords` on partner builds). None declare `skills`, `commands`, `agents`, `hooks`, or `mcpServers` paths — all components are picked up by convention from `skills/`, `commands/`, `agents/`, `.mcp.json`.
- **Components observed** (across the 13 Anthropic + 5 partner-built in-repo plugins):
  - skills — **yes** (universal; every plugin has `skills/*/SKILL.md`)
  - commands — **yes** (pdf-viewer, partner-built/slack, partner-built/common-room, partner-built/brand-voice, plus grep hits in product-management). Legacy format per cowork-plugin-management docs.
  - agents — **yes** (only `partner-built/brand-voice/agents/` — 5 agent `.md` files)
  - hooks — **no** (no `hooks.json` files anywhere in-tree)
  - .mcp.json — **yes** (17 of 18 in-repo plugins; `cowork-plugin-management` is the one with no `.mcp.json`)
  - .lsp.json — **no**
  - monitors.json — **no**
  - bin/ — **no**
  - output-styles — **no**
- **Agent frontmatter fields used** (observed on `partner-built/brand-voice/agents/*.md`): `name`, `description` (multi-line YAML `>` folded, embeds `<example>` blocks for Claude few-shot), `model` (`sonnet`), `color` (e.g., `magenta`), `tools` (plain list — `Read`, `Glob`, `Grep`), `maxTurns` (numeric, e.g., `15`). No `skills`, `memory`, `background`, `isolation` fields.
- **Agent tools syntax**: plain tool names (`Read`, `Glob`, `Grep`) — not the `Bash(uv run *)` permission-rule syntax seen in some other repos.
- **Pitfalls observed**: zero explicit component paths in `plugin.json` means any plugin that wanted to colocate skills under, say, `skills-nested/` would need to update convention rather than manifest. The `cowork-plugin-customizer` skill explicitly documents this: "legacy `commands/` format still works, but new plugins should use `skills/*/SKILL.md`" — the repo is mid-migration between two component conventions.

## 6. Dependency installation

- **Applicable**: partial — one skill (`bio-research/skills/instrument-data-to-allotrope/`) ships a `requirements.txt`. Nothing else in the repo has runtime Python/Node deps managed through a manifest.
- **Dep manifest format**: `requirements.txt` (the one file — pins `allotropy==0.1.55`, `pandas==2.0.3`, `openpyxl==3.1.2`, `pdfplumber==0.9.0`, with commented-out optional `numpy`/`scipy`).
- **Install location**: ad-hoc. The requirements file's preamble says `pip install -r requirements.txt --break-system-packages`. No install script, no hook, no `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PLUGIN_ROOT}` venv — just user-directed pip invocation.
- **Install script location**: none. No `install.sh`, no `setup.sh`, no `hooks.json` triggers install.
- **Change detection**: none — pip call is manual and the user is expected to run it once.
- **Retry-next-session invariant**: n/a (no automation).
- **Failure signaling**: n/a (no automation).
- **Runtime variant**: Python pip (user-invoked). Plus `pdf-viewer/.mcp.json` uses `npx -y @modelcontextprotocol/server-pdf --stdio` — an ad-hoc runtime-fetch pattern for a Node MCP server.
- **Alternative approaches**: `npx -y` ad-hoc fetch (pdf-viewer). No PEP 723 / uvx usage observed.
- **Version-mismatch handling**: n/a.
- **Pitfalls observed**: the `--break-system-packages` instruction in the bio-research `requirements.txt` is a stop-gap that will fail on PEP 668-managed systems unless users have a venv already active; there's no plugin-managed venv to isolate into. A hook-driven install into `${CLAUDE_PLUGIN_DATA}/venv/` would be more portable but isn't used.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no. No `bin/` directories anywhere in the tree. Skills ship Python scripts under `skills/<name>/scripts/` (bio-research, data/data-context-extractor) but these are invoked by the skill's LLM via direct `python path/to/script.py` calls rather than through any wrapper.
- **`bin/` files**: none.
- **Shebang convention**: n/a.
- **Runtime resolution**: n/a.
- **Venv handling (Python)**: n/a — scripts run against whatever Python the user has configured; no plugin-managed venv.
- **Platform support**: n/a.
- **Permissions**: n/a (script files under `skills/*/scripts/` are plain `.py` files, not marked executable).
- **SessionStart relationship**: n/a (no hooks at all).
- **Pitfalls observed**: none (absent by design — the repo emphasizes that plugins are "just markdown and JSON, no code, no infrastructure, no build steps" — README).

## 8. User configuration

- **`userConfig` present**: no — no `plugin.json` examined declares `userConfig`.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable. Instead, `partner-built/zoom-plugin/.mcp.json` uses raw `${ZOOM_MCP_ACCESS_TOKEN}` / `${ZOOM_DOCS_MCP_ACCESS_TOKEN}` / `${ZOOM_WHITEBOARD_MCP_ACCESS_TOKEN}` environment-variable substitution in MCP headers, with the README telling users to `export` them before launch. This is a process-environment pattern, not a `userConfig` surface. `partner-built/slack/.mcp.json` relies on OAuth (`oauth.clientId`, `callbackPort`) — see §17.
- **Pitfalls observed**: the env-var pattern pushes secret management entirely onto the user's shell; nothing in the plugin marks secrets as sensitive, which would matter if these configs were ever exported. The Zoom plugin's README shows the same token reused for two different MCP endpoints (`ZOOM_MCP_ACCESS_TOKEN` and `ZOOM_WHITEBOARD_MCP_ACCESS_TOKEN`), which may confuse users — these are separate token scopes.

## 9. Tool-use enforcement

- **PreToolUse hooks**: none — no `hooks.json` files in the repo.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable.
- **Failure posture**: not applicable.
- **Top-level try/catch wrapping**: not applicable.
- **Pitfalls observed**: none (absent by design).

## 10. Session context loading

- **SessionStart used for context**: no (no hooks at all).
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: not applicable.
- **SessionStart matcher**: not applicable.
- **Pitfalls observed**: the `productivity/skills/start/SKILL.md` performs first-run bootstrapping (copying `dashboard.html` from `${CLAUDE_PLUGIN_ROOT}/skills/dashboard.html` into the cwd, creating `TASKS.md` / `CLAUDE.md` / `memory/` if absent) entirely via skill instructions to the model, not via a SessionStart hook. This is intentional per the "no code, no infrastructure" design — but it means bootstrap only happens when the user explicitly invokes `/productivity:start`, not automatically.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none (absent by design).

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no — no `plugin.json` declares `dependencies`.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: no (no tags at all — see §4).
- **Pitfalls observed**: none. Plugins are intentionally flat and independent. Cross-plugin interactions are handled by convention (e.g., `sales` and `marketing` both connect to HubSpot via their own `.mcp.json`) rather than by declared dependency.

## 13. Testing and CI

- **Test framework**: none. No `tests/` directory, no `pytest.ini`, no `pyproject.toml`, no `package.json` with a `test` script. Only test-adjacent files are `scripts/` inside bio-research skills, which are the production scripts themselves, not tests.
- **Tests location**: not applicable.
- **Pytest config location**: not applicable.
- **Python dep manifest for tests**: not applicable.
- **CI present**: no — the repo has no `.github/workflows/` directory. `gh api /contents/.github` returns 404.
- **CI file(s)**: none.
- **CI triggers**: not applicable.
- **CI does**: not applicable.
- **Matrix**: not applicable.
- **Action pinning**: not applicable.
- **Caching**: not applicable.
- **Test runner invocation**: not applicable.
- **Pitfalls observed**: the `ci/verify-community-merged` branch name hints CI was considered or staged, but nothing lives on `main`. Commit message "Add manual plugin validation fallback when CLI validator is unavailable (#63)" suggests validation is currently a manual/CLI-tool step rather than automated.

## 14. Release automation

- **`release.yml` (or equivalent) present**: no.
- **Release trigger**: not applicable.
- **Automation shape**: not applicable — no release automation at all. Zero tags, zero GitHub releases, no workflow files.
- **Tag-sanity gates**: not applicable.
- **Release creation mechanism**: not applicable.
- **Draft releases**: not applicable.
- **CHANGELOG parsing**: not applicable. A `CHANGELOG.md` exists only at `partner-built/zoom-plugin/CHANGELOG.md` (authored by the partner) and is a free-form "Unreleased" list, not Keep-a-Changelog. Nothing parses it.
- **Pitfalls observed**: the entire release surface is "edit `plugin.json` version, commit to `main`, consumers take HEAD". No tag-on-commit, no immutable marker. For a marketplace with 11k+ stars, this is deliberately informal.

## 15. Marketplace validation

- **Validation workflow present**: no.
- **Validator**: none in-tree. Commit message "Add manual plugin validation fallback when CLI validator is unavailable (#63)" indicates reliance on an external `claude plugin validate` CLI command (not committed to the repo).
- **Trigger**: not applicable.
- **Frontmatter validation**: not applicable.
- **Hooks.json validation**: not applicable.
- **Pitfalls observed**: absence of automated validation means issues like the `figma` entry's missing `sha` (§1), inconsistent field sets across marketplace entries, and the nested `brand-voice` marketplace's author-name mismatch (`"TribeAI"` in nested manifest vs `"Tribe AI"` in root marketplace entry) can ship to main without catching.

## 16. Documentation

- **`README.md` at repo root**: present (~6 KB) — plugin table with per-plugin links, Claude Code install instructions, "How Plugins Work" section, "Making Them Yours" customization guide.
- **`README.md` per plugin**: mostly present. Anthropic-owned: productivity, pdf-viewer, bio-research, customer-support, data, enterprise-search, finance, legal, marketing, design, engineering, human-resources, operations all ship a `README.md`. `cowork-plugin-management` ships **no** `README.md` (only skills + LICENSE). Partner-built: slack, zoom-plugin, apollo, common-room, brand-voice all ship READMEs.
- **`CHANGELOG.md`**: absent at repo root. Present only at `partner-built/zoom-plugin/CHANGELOG.md` (free-form, not Keep a Changelog).
- **`architecture.md`**: absent everywhere. Architecture descriptions live inside the `cowork-plugin-management/skills/create-cowork-plugin/SKILL.md` instructional content, not in dedicated docs.
- **`CLAUDE.md`**: absent at repo root. Present only at `partner-built/slack/CLAUDE.md` (~1 KB — a thin pointer doc listing commands and skills).
- **`AGENTS.md`**: present at `partner-built/zoom-plugin/AGENTS.md` (1.7 KB) — a cross-ecosystem discovery file targeted at agent tools that look for `AGENTS.md` rather than `CLAUDE.md`. Explicitly frames itself as an ecosystem-neutral alternative to the Claude-specific `CLAUDE.md`.
- **`CONNECTORS.md`**: pattern — 13 plugins ship a `CONNECTORS.md` alongside their `README.md` describing which MCP servers are bundled and what each one does. Referenced by command/skill files using `../CONNECTORS.md` or `../../CONNECTORS.md` relative paths. Not a Claude-prescribed filename; it's a repo convention.
- **`CONTRIBUTING.md`**: present at `partner-built/zoom-plugin/CONTRIBUTING.md` (6.3 KB, partner-specific). Absent at repo root despite README saying "Fork the repo, make your changes, and submit a PR."
- **Community health files**: none at repo root beyond LICENSE. No root `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`.
- **LICENSE**: present at repo root (Apache-2.0). Additional LICENSE files inside most Anthropic-owned plugin directories (identical copies). Partner-built plugins ship their own LICENSE (MIT variants).
- **Badges / status indicators**: absent. README is plain markdown; no shields.io badges, no CI status, no version badges.
- **Pitfalls observed**: the `CONNECTORS.md` pattern is a de-facto documentation convention not mentioned in the official Claude plugin docs; a consumer unfamiliar with the repo would have to infer its role from relative-path references in SKILL.md files. The `AGENTS.md` presence in one partner plugin but nowhere else suggests emerging cross-ecosystem documentation is partner-driven rather than repo-mandated.

## 17. Novel axes

- **Nested marketplace.json inside a plugin directory (`partner-built/brand-voice/.claude-plugin/marketplace.json`)**. This file declares a single-plugin marketplace with `metadata.pluginRoot: "."` and describes the brand-voice plugin as if it were its own standalone marketplace. The root `marketplace.json` *also* registers `brand-voice` via `./partner-built/brand-voice`. Effect: the same directory is advertised as both (a) an inline plugin within the aggregator and (b) a self-contained marketplace a partner could upstream to their own repo. This is a "dual-addressable plugin" pattern — the partner can develop out of a mirror repo that points `marketplace.json` at the root, while Anthropic's aggregator surfaces it via the nested entry. Worth a dedicated purpose section in the pattern doc: **nested / fork-ready marketplace duplication**.

- **Aggregator-of-aggregators model via mixed `source` types in a single marketplace**. 41 plugins across three provenance tiers — 18 × in-repo (`./<path>`), 18 × external `url`-pinned, 2 × `git-subdir`-pinned — all in one `plugins[]` array. Distinct from pure inline marketplaces and pure aggregator marketplaces. This is the first primary-owned marketplace observed that hosts both in-tree plugins *and* external ecosystem plugins in the same manifest. Candidate purpose: **mixed-provenance marketplace composition**.

- **Partner-built plugins as first-class subdirectories of the host repo (`partner-built/`)**. Five plugins (apollo, brand-voice, common-room, slack, zoom-plugin) are authored by external partners (Apollo.io, Tribe AI, Common Room, Salesforce, Zoom) but live inside Anthropic's repo tree with their own LICENSEs and author attributions. This is distinct from external `url`-source entries — the partner code is vendored into Anthropic's tree rather than pulled from the partner's repo. Candidate purpose: **vendored-partner subtree pattern**.

- **`CONNECTORS.md` sibling-doc convention**. A de-facto per-plugin documentation file describing bundled MCP servers, cross-referenced by SKILL.md files via relative paths. Not Claude-spec documentation — a repo-originated convention that spread across 13+ plugins. Worth naming as a recurring documentation pattern if it appears in other marketplaces.

- **`AGENTS.md` as an ecosystem-neutral alternative to `CLAUDE.md`** (observed only in zoom-plugin). The file explicitly states it targets "agent tools that look for `AGENTS.md`". Candidate emerging standard to track.

- **Placeholder-driven customization via `~~`-prefix tokens**. The `cowork-plugin-customizer` skill documents and actions a convention where template placeholders in generic plugins use `~~jira`, `~~your-team-channel`, etc., for customization. Unrelated to Claude's config-substitution syntax — a separate human-in-the-loop templating layer. Worth naming: **template-placeholder customization pattern**.

- **Skill-level `user-invocable: false` frontmatter**. `productivity/skills/task-management/SKILL.md` uses `user-invocable: false` to mark the skill as composition-only (used by other skills, not exposed as a slash command). Not in the core plugin-reference frontmatter docs — may be a Cowork-specific extension.

- **Skill-level `compatibility:` frontmatter** (e.g., "Requires Cowork desktop app environment"). Observed in `cowork-plugin-management/skills/{create-cowork-plugin,cowork-plugin-customizer}/SKILL.md` — free-form prose declaring platform prerequisites. Not in canonical SKILL.md frontmatter schema; another Cowork-ism.

- **MCP `oauth` subfield inside `.mcp.json`** (`partner-built/slack/.mcp.json`): `{oauth: {clientId: "...", callbackPort: 3118}}`. This embeds an OAuth client binding directly in the MCP server definition, rather than in a separate config surface. Likely a Claude Code / Cowork extension to the standard MCP server schema. Candidate purpose axis: **inline OAuth-client MCP config**.

- **Env-var substitution inside `.mcp.json` header values** (`partner-built/zoom-plugin/.mcp.json` using `Bearer ${ZOOM_MCP_ACCESS_TOKEN}`) as a secret-management mechanism in lieu of `userConfig`. Useful as a comparison axis when contrasted with marketplaces that drive the same thing through `${user_config.KEY}` substitution.

- **`dashboard.html` shipped inside a skill directory**. `productivity/skills/dashboard.html` is a static HTML asset the skill copies into the user's cwd via instructions to the model. Not a canonical plugin component type — the skill treats it as a bundled asset. Candidate purpose: **bundled static-asset delivery via skill instructions**.

## 18. Gaps

- Could not enumerate every in-repo plugin's `plugin.json` in detail; spot-checked 8 (productivity, pdf-viewer, cowork-plugin-management, apollo, brand-voice, zoom-plugin, common-room, slack-by-salesforce) plus confirmed version numbers for 13 role plugins via a loop. A plugin with a non-minimal manifest (e.g., `dependencies` or `userConfig`) might exist among the unchecked few; a full pass would need one additional GitHub API listing.
- Did not read every partner-built `README.md` or `CONTRIBUTING.md` — only zoom-plugin's. Partner-specific install or configuration steps could diverge from patterns observed in the Anthropic-owned plugins.
- Did not inspect external `url`-source plugin repos (planetscale, zoominfo, sanity, …) — they are out of scope for *this* marketplace file, but observing that 18 of the 41 entries are externally sourced means the aggregator part of this marketplace delegates its plugin-internal design to downstream repos.
- Could not determine whether the nested `partner-built/brand-voice/.claude-plugin/marketplace.json` is actually consumed by any marketplace loader (i.e., whether a user could run `claude plugin marketplace add anthropics/knowledge-work-plugins/partner-built/brand-voice` and have it work). Resolving would require testing the CLI loader directly against that path.
- The "Cowork mode" platform referenced throughout (`compatibility: Requires Cowork desktop app…`) has surfaces (mounted plugin directories, outputs directory) not documented in the public plugin-reference docs. A full characterization of Cowork-specific extensions would need access to Cowork product documentation not visible in this repo.
- Could not observe any CI/validation behavior since nothing runs — any implicit maintainer-side validation (e.g., a `validate.sh` script run pre-merge) is not committed to the repo.
