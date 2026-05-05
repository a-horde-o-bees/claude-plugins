# Sample

Mirrors of `https://github.com/anthropics/knowledge-work-plugins`. Anthropic-owned aggregator marketplace for "plugins that turn Claude into a specialist for your role, team, and company"; built for Claude Cowork, also compatible with Claude Code. 11,398 stars; default branch `main`; Apache-2.0 at repo root with per-plugin LICENSE variants. The `.claude-plugin/marketplace.json` registers 41 plugin entries spanning three provenance tiers — 13 Anthropic-owned, 5 partner-built (vendored into `partner-built/`), and 23 external (`url`/`git-subdir`).

## Marketplace manifest layout

### Multi-plugin owned-aggregator marketplace

Single `.claude-plugin/marketplace.json` at repo root (16 KB, 41 plugin entries). Top-level keys are `name`, `owner`, `plugins` only — no `metadata` wrapper, no top-level `description`, no top-level `version`, no `pluginRoot`, no `$schema`.

### Nested mini-marketplace inside a plugin directory

A second self-contained `.claude-plugin/marketplace.json` exists nested at `partner-built/brand-voice/.claude-plugin/marketplace.json`. The nested manifest declares a single-plugin marketplace with `metadata.pluginRoot: "."` describing brand-voice as if it were its own standalone marketplace, while the root `marketplace.json` *also* registers brand-voice via `./partner-built/brand-voice`. The same directory is dual-addressable: the partner can develop out of a mirror repo with `marketplace.json` pointing at the root, while Anthropic's aggregator surfaces it via the nested entry. The nested manifest declares author `"TribeAI"` while the root marketplace entry uses `"Tribe AI"` (mismatch).

## Plugin source binding

### Mixed-provenance composition

The single `plugins[]` array hosts 41 entries across three provenance tiers: 21 × in-repo string-form `./<relative-path>` (13 Anthropic-owned at repo root, 5 partner-built under `partner-built/`, 3 later-added role plugins like `engineering`, `human-resources`, `design`, `operations`, plus pdf-viewer), 18 × external `{source: "url", url, sha}`, 2 × `{source: "git-subdir", url, path, ref, sha}`. Aggregates external ecosystem plugins alongside in-tree plugins in a single manifest.

### Relative source pointing to subdirectory

String-form `./<relative-path>` is the dominant in-repo binding — 21 of 41 entries.

### `url` clone with `sha` pin

18 of 41 entries use `{source: "url", url, sha}`. SHA pinning is universal across these except for the `figma` entry, which uses `source.source: "url"` without a `sha` pin (1/18 omits SHA — non-reproducible install for that one plugin; appears to be an oversight rather than intentional "track main").

### `git-subdir` into upstream

2 of 41 entries use `{source: "git-subdir", url, path, ref, sha}`.

### Vendored-partner subtree

5 plugins (apollo, brand-voice, common-room, slack-by-salesforce, zoom-plugin) are authored by external partners (Apollo.io, Tribe AI, Common Room, Salesforce, Zoom) but live inside the host repo tree at `partner-built/<name>/` with their own LICENSEs (MIT for slack/zoom-plugin/apollo) and `author.name` attributions on the marketplace entry. Distinct from external `url`-source entries — partner code is vendored into Anthropic's tree rather than pulled from the partner's repo.

### `strict` field default

Discovery is implicit (default-true semantics per the plugin spec). `strict` is absent on every marketplace entry.

## Per-plugin discoverability metadata

### Mixed-by-origin metadata

Three provenance tiers carry different field sets on their marketplace entries. The 13 Anthropic-owned entries (productivity, sales, finance, …, pdf-viewer) use only `name` + `source` + `description`, no `category`, `keywords`, or `tags`. The 5 partner-built entries served from `./partner-built/<name>` add `author.name`. The 23 external `url`/`git-subdir` entries variably add `category` (e.g., planetscale `database`, zapier `productivity`) and `homepage`. `keywords` appear only in per-plugin `plugin.json` files, never in marketplace entries.

### `$schema` absence on per-plugin manifests

`$schema` is absent from `marketplace.json` and from the per-plugin `plugin.json` files surveyed.

## Version coordination

### Single source of truth (`plugin.json` only)

Per-plugin `plugin.json` is the only version authority. The marketplace entry never carries `version`. Anthropic-owned plugins drift independently — most at `1.2.0`, `data` at `1.1.0`, `bio-research` at `1.1.0`, `cowork-plugin-management` at `0.2.2`, `pdf-viewer` at `0.2.0`. Partner-built range `1.0.0`–`1.1.0`.

### Marketplace-side pin via source ref

External entries pin via `source.sha` except for the `figma` entry, which omits SHA — that one entry effectively tracks HEAD of the external repo. The brand-voice nested `plugin.json` declares `version: "1.0.0"` while the root marketplace entry has no version field, so clients cannot know what version they're pulling without cloning the source.

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split. Single marketplace consumed by both Claude Cowork (primary) and Claude Code (secondary). README directs Code users to run `claude plugin marketplace add anthropics/knowledge-work-plugins`, implying `@main` pinning by convention. No `stable-tools` / `latest-tools` pattern, no release/latest branch split.

## Tag and release lifecycle

### No tags at all

`gh api /repos/.../tags` returns an empty array. Repo uses 0 tags. No `release/*` or `v*` branches; 20+ feature branches exist (`add-plugin/*`, `fix/*`, `ci/verify-community-merged`, `bump-versions-command-deprecation`) but none govern releases. No GitHub Releases.

### Hand-bumped versions on main (untagged)

Versions are visible only inside each `plugin.json`. Commit history shows periodic `bump-versions-*` branches, suggesting manual batch bumps rather than per-PR bumps. Consumers who pin `@main` take whatever version is committed. The entire release surface is "edit `plugin.json` version, commit to `main`, consumers take HEAD". For a marketplace with 11k+ stars, this is deliberately informal.

## Plugin-component registration

### Default convention discovery

Every `plugin.json` examined (productivity, pdf-viewer, cowork-plugin-management, apollo, brand-voice, zoom-plugin, slack-by-salesforce, common-room) contains only `name` + `version` + `description` + `author` plus optional `homepage`/`repository`/`license`/`keywords` on partner builds. None declare `skills`, `commands`, `agents`, `hooks`, or `mcpServers` paths — all components are picked up by convention from `skills/`, `commands/`, `agents/`, `.mcp.json`. Mid-migration between two component conventions: `cowork-plugin-customizer` skill explicitly documents "legacy `commands/` format still works, but new plugins should use `skills/*/SKILL.md`".

### `.mcp.json` sibling file

17 of 18 in-repo plugins ship a `.mcp.json` at plugin root; `cowork-plugin-management` is the one without.

## Component composition

### Skills (universal)

Every plugin has `skills/*/SKILL.md` (universal across all 18 in-repo plugins).

### Commands

Present in pdf-viewer, partner-built/slack, partner-built/common-room, partner-built/brand-voice, plus grep hits in product-management. Documented as legacy format per `cowork-plugin-management` docs.

### Agents

Only in `partner-built/brand-voice/agents/` — 5 agent `.md` files.

### Hooks

No `hooks.json` files anywhere in-tree.

### MCP servers

17 of 18 in-repo plugins have a `.mcp.json`. `cowork-plugin-management` is the one without.

## Skill authoring conventions

### `user-invocable: false`

`productivity/skills/task-management/SKILL.md` uses `user-invocable: false` to mark the skill as composition-only (used by other skills, not exposed as a slash command). Not in the core plugin-reference frontmatter docs; may be a Cowork-specific extension.

### `compatibility:` prose

Observed in `cowork-plugin-management/skills/{create-cowork-plugin,cowork-plugin-customizer}/SKILL.md` — free-form prose declaring platform prerequisites (e.g., "Requires Cowork desktop app environment"). Not in canonical SKILL.md frontmatter schema; another Cowork-ism.

## Agent declaration conventions

### Standard fields plus model / color

Observed on `partner-built/brand-voice/agents/*.md`: `name`, `description` (multi-line YAML `>` folded, embeds `<example>` blocks for Claude few-shot), `model` (`sonnet`), `color` (e.g., `magenta`), `tools` (plain list — `Read`, `Glob`, `Grep`), `maxTurns` (numeric, e.g., `15`). No `skills`, `memory`, `background`, `isolation` fields.

### Plain tool-name list

`tools` declared as plain tool names (`Read`, `Glob`, `Grep`) — not the `Bash(uv run *)` permission-rule syntax.

## Server runtime (MCP)

### Runtime-fetched server via `npx -y`

`pdf-viewer/.mcp.json` uses `npx -y @modelcontextprotocol/server-pdf --stdio` — ad-hoc runtime-fetch pattern for a Node MCP server.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directories anywhere in the tree. Skills ship Python scripts under `skills/<name>/scripts/` (bio-research, data/data-context-extractor) but these are invoked by the skill's LLM via direct `python path/to/script.py` calls rather than through any wrapper. Script files under `skills/*/scripts/` are plain `.py` files, not marked executable.

## Dependency installation

### `requirements.txt` with manual user invocation

One skill (`bio-research/skills/instrument-data-to-allotrope/`) ships a `requirements.txt` pinning `allotropy==0.1.55`, `pandas==2.0.3`, `openpyxl==3.1.2`, `pdfplumber==0.9.0` (with commented-out optional `numpy`/`scipy`). The requirements file's preamble says `pip install -r requirements.txt --break-system-packages`. No install script, no hook, no `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PLUGIN_ROOT}` venv — user-directed pip invocation. The `--break-system-packages` instruction will fail on PEP 668-managed systems unless a venv is already active; no plugin-managed venv to isolate into.

### No managed install (user prerequisite)

Nothing else in the repo has runtime Python/Node deps managed through a manifest. Skills with substantial scripts elsewhere rely on whatever Python the user has configured.

## User configuration and authentication

### No userConfig, env-var only

No `plugin.json` examined declares `userConfig`. `partner-built/zoom-plugin/.mcp.json` uses raw `${ZOOM_MCP_ACCESS_TOKEN}` / `${ZOOM_DOCS_MCP_ACCESS_TOKEN}` / `${ZOOM_WHITEBOARD_MCP_ACCESS_TOKEN}` environment-variable substitution in MCP `Bearer` headers, with the README telling users to `export` them before launch. Process-environment pattern, not a `userConfig` surface. The Zoom plugin's README shows the same token reused for two different MCP endpoints (`ZOOM_MCP_ACCESS_TOKEN` and `ZOOM_WHITEBOARD_MCP_ACCESS_TOKEN`) — these are separate token scopes. No `sensitive: true` flagging.

### OAuth client embedded in MCP config

`partner-built/slack/.mcp.json` carries `{oauth: {clientId: "...", callbackPort: 3118}}` — embeds an OAuth client binding directly inside the MCP server definition rather than in a separate config surface. Likely a Claude Code / Cowork extension to the standard MCP server schema.

## Session context loading

### No session-context loading

No SessionStart hooks, no UserPromptSubmit hooks, no `hookSpecificOutput.additionalContext`. The `productivity/skills/start/SKILL.md` performs first-run bootstrapping (copying `dashboard.html` from `${CLAUDE_PLUGIN_ROOT}/skills/dashboard.html` into the cwd, creating `TASKS.md` / `CLAUDE.md` / `memory/` if absent) entirely via skill instructions to the model — bootstrap only happens when the user explicitly invokes `/productivity:start`.

## Tool-use enforcement

### No enforcement (observational only)

No `hooks.json` files in the repo. No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks anywhere.

## Live monitoring

### `monitors.json` absent

No `monitors.json` files anywhere.

## Plugin-to-plugin coordination

### `dependencies` field absent

No `plugin.json` declares `dependencies`. Plugins are intentionally flat and independent; cross-plugin interactions are handled by convention (e.g., `sales` and `marketing` both connect to HubSpot via their own `.mcp.json`) rather than by declared dependency.

## Testing

### No tests

No `tests/` directory, no `pytest.ini`, no `pyproject.toml`, no `package.json` with a `test` script. Only test-adjacent files are `scripts/` inside bio-research skills, which are the production scripts themselves, not tests.

## CI workflow shape

### No CI

The repo has no `.github/workflows/` directory; `gh api /contents/.github` returns 404. The `ci/verify-community-merged` branch name hints CI was considered or staged, but nothing lives on `main`. Commit message "Add manual plugin validation fallback when CLI validator is unavailable (#63)" suggests validation is currently a manual/CLI-tool step rather than automated.

## Marketplace validation

### Manual validation only

No validation workflow in-tree. Commit message "Add manual plugin validation fallback when CLI validator is unavailable (#63)" indicates reliance on an external `claude plugin validate` CLI command (not committed to the repo). Absence of automated validation means issues like the `figma` entry's missing `sha`, inconsistent field sets across marketplace entries, and the nested `brand-voice` author-name mismatch (`"TribeAI"` in nested manifest vs `"Tribe AI"` in root marketplace entry) ship to main without catching.

## Release automation

### No release automation / manual

No release workflows, no GitHub Releases, no tags. The entire release surface is "edit `plugin.json` version, commit to `main`, consumers take HEAD". A `CHANGELOG.md` exists only at `partner-built/zoom-plugin/CHANGELOG.md` (authored by the partner) and is a free-form "Unreleased" list, not Keep-a-Changelog. Nothing parses it.

## Documentation surface

### Layered repo / plugin / skill READMEs (uneven)

`README.md` at repo root (~6 KB) — plugin table with per-plugin links, Claude Code install instructions, "How Plugins Work" section, "Making Them Yours" customization guide. Per-plugin README mostly present: Anthropic-owned plugins (productivity, pdf-viewer, bio-research, customer-support, data, enterprise-search, finance, legal, marketing, design, engineering, human-resources, operations) all ship a `README.md`. `cowork-plugin-management` ships no `README.md` (only skills + LICENSE). Partner-built (slack, zoom-plugin, apollo, common-room, brand-voice) all ship READMEs.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` at repo root (only `partner-built/zoom-plugin/CHANGELOG.md` — free-form, not Keep a Changelog). No `architecture.md` anywhere; architecture descriptions live inside the `cowork-plugin-management/skills/create-cowork-plugin/SKILL.md` instructional content. No `CLAUDE.md` at repo root; present only at `partner-built/slack/CLAUDE.md` (~1 KB — a thin pointer doc listing commands and skills).

### `AGENTS.md` as ecosystem-neutral alternative to `CLAUDE.md`

Present at `partner-built/zoom-plugin/AGENTS.md` (1.7 KB) — a cross-ecosystem discovery file targeted at agent tools that look for `AGENTS.md` rather than `CLAUDE.md`. Explicitly frames itself as an ecosystem-neutral alternative to the Claude-specific `CLAUDE.md`.

### `CONNECTORS.md` sibling-doc convention

13 plugins ship a `CONNECTORS.md` alongside their `README.md` describing which MCP servers are bundled and what each one does. Referenced by command/skill files using `../CONNECTORS.md` or `../../CONNECTORS.md` relative paths. Not a Claude-prescribed filename; a repo convention spread across 13+ plugins. A consumer unfamiliar with the repo would have to infer its role from relative-path references in SKILL.md files.

### Badges and status indicators

Absent. README is plain markdown — no shields.io badges, no CI status, no version badges.

## License declaration

### Repo-root LICENSE plus per-plugin duplicates

Apache-2.0 `LICENSE` at repo root. Most Anthropic-owned plugin directories ship a copy of the same Apache-2.0 file. Partner-built plugins ship their own LICENSE — `slack` MIT, `zoom-plugin` MIT, `apollo` MIT, `common-room` Apache-2.0-style, `brand-voice` Apache-2.0-style.

## Community health files

### Bare minimum (LICENSE only)

LICENSE at repo root. No root `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` despite README saying "Fork the repo, make your changes, and submit a PR." `partner-built/zoom-plugin/CONTRIBUTING.md` (6.3 KB, partner-specific) is the only `CONTRIBUTING.md` in tree.

## Bundled static asset delivery

### Skill-instruction-driven copy

`productivity/skills/dashboard.html` is a static HTML asset the skill copies into the user's cwd via instructions to the model. Not a canonical plugin component type — the skill treats it as a bundled asset.

## Template-customization mechanism

### Placeholder-token convention

The `cowork-plugin-customizer` skill documents and actions a convention where template placeholders in generic plugins use `~~jira`, `~~your-team-channel`, etc., for customization. Unrelated to Claude's config-substitution syntax — a separate human-in-the-loop templating layer.
