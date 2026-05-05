# Sample

Mirrors of `https://github.com/anthropics/life-sciences`. Anthropic-owned Claude Code marketplace of MCP servers and skills for life-sciences research, data analysis, and discovery. README opens: "This marketplace provides MCP (Model Context Protocol) servers and skills for life sciences tools." 314 stars; default branch `main`; no repo-root LICENSE (`license: null` in GitHub API) but Apache-2.0 `LICENSE.txt` duplicated inside each skill directory (added in PR #34, 2026-01-26). Latest commit 2026-01-26.

## Marketplace manifest layout

### Multi-plugin owned-aggregator marketplace

Single `.claude-plugin/marketplace.json` at repo root, hosting 17 plugin entries.

### Top-level `metadata` wrapper variants

`metadata.{version, description}` wrapper present (`version: "1.0.0"`, description string). No `metadata.pluginRoot`. No `$schema`. The `metadata.version: "1.0.0"` on the marketplace wrapper is decoupled from the git release tags `v1.0.0`/`v1.1.0`/`v1.1.1` — the wrapper hasn't been bumped as releases advanced; consumers reading the wrapper see `1.0.0` while the repo is at `v1.1.1`.

### Parallel non-marketplace inventory

`scientific-problem-selection/` exists on disk (with `SKILL.md`, `scripts/`, `references/`, `LICENSE.txt`) and is packaged by `release.yml` into `scientific-problem-selection-v1.1.1.zip`, but is NOT listed as a plugin in `marketplace.json`. The release-asset list and the marketplace plugin list have drifted — only 17 plugins are installable via `@life-sciences`, even though 7 skill zips ship in the v1.1.1 release.

## Plugin source binding

### Relative source pointing to subdirectory

10 of 17 entries use `"source": "./<plugin-dir>"` pointing at a directory containing `.claude-plugin/plugin.json` — the MCP plugins plus the two `.mcpb`-bundle plugins `10x-genomics` and `tooluniverse`.

### Skill-carving via shared root + `skills` override

5 of 17 entries use `"source": "./"` paired with `"strict": false` and `"skills": ["./<skill-dir>"]` (`single-cell-rna-qc`, `instrument-data-to-allotrope`, `nextflow-development`, `scvi-tools`, `clinical-trial-protocol`). Each uses a single-element array with the skill directory path. The same root directory is bound as the "plugin root" for five distinct marketplace entries; `strict: false` disables validation of a `plugin.json` at that root, and `skills: [...]` carves the actual skill out. The skill's SKILL.md plus its directory tree is the entire deliverable; the marketplace entry replaces plugin.json for those five.

### `strict` field default

Default (implicit `true`) on the 12 MCP/bundle entries; explicit `strict: false` on the 5 skill-carving entries.

## Per-plugin discoverability metadata

### Category + tags pair

Every plugin has `category: "life-sciences"` and `tags: [...]`. No `keywords` field used. Uniform across all 17 entries.

### `$schema` absence on per-plugin manifests

`$schema` is absent.

## Version coordination

### Stale fallback constants in code

Every plugin.json holds `version: "1.0.0"` regardless of release cut. The release-tag version (`v1.1.1`) lives only on git tags and release-asset filenames (`<skill>-v1.1.1.zip`). For skills this is coherent because skills have no plugin.json; for MCP plugins it means plugin.json versions are permanently pinned at `1.0.0`. All 11 surveyed plugin.json files (10 MCP + tooluniverse) hold `version: "1.0.0"` unchanged across the v1.0.0 → v1.1.1 release sequence — `plugin.json.version` appears to be written once at plugin introduction and never bumped. The marketplace wrapper `metadata.version: "1.0.0"` has not been bumped across release cuts either; it names the marketplace schema/entry-set version at repo birth, not the current release.

### No plugin-level version

The 5 skill-carving entries have no `plugin.json` at all — each skill directory contains only `SKILL.md` (plus `scripts/`, `references/`, `LICENSE.txt`), so the marketplace entry is the only source of plugin identity (`name`, `description`). "Version" does not exist as a concept at the plugin level for those five. Bumping a skill version requires re-releasing and re-tagging the whole repo. `clinical-trial-protocol` marketplace entry points at directory `clinical-trial-protocol-skill/` (plugin name and directory name diverge); SKILL.md frontmatter `name: clinical-trial-protocol-skill` matches the directory but not the marketplace plugin ID. Deliberately noted in branch history (`claude/slack-copy-clinical-trial-protocol-X6rjk`).

## Channel distribution

### Single channel — tag-on-main with git-ref pinning

No channel split. Users install via `@life-sciences` at HEAD; there is no `stable` vs `latest` pair. Release tags (v1.0.0, v1.1.0, v1.1.1) exist but consumers are not directed to pin to them in the README. README install instruction is `/plugin marketplace add anthropics/life-sciences` (tracking `main`). Tags are published as GitHub releases (with zip assets) but marketplace consumers don't have a channel-aware install UX.

## Tag and release lifecycle

### Tag-on-main, single branch

Tag placement on main (inferred — release workflow triggers on `push: tags: ['v*']` with no branch restriction). No release branching; feature work happens on topic branches (e.g., `daisy/initial-marketplace`, `jwei/nextflow`, `andres/add-medidata-plugin`) merged via PR to main. Pre-release suffixes none observed; v1.0.0, v1.1.0, v1.1.1 only. Release workflow hardcodes `prerelease: false`. Three tags over the lifetime of the repo (2025-10 → 2026-01), one (v1.0.0) predating most plugins. Coarse cadence that doesn't match per-plugin change pace.

## Plugin-component registration

### Inline `mcpServers` definition in `plugin.json`

All MCP plugins use inline `mcpServers` config objects inside their `plugin.json`. Object form: `"mcpServers": {"<ServerName>": {"type": "http", "url": "https://..."}}` — used by pubmed, biorender, synapse, wiley-scholar-gateway, biorxiv, clinical-trials, chembl, owkin, open-targets, medidata.

### Marketplace-entry-only definition (no `plugin.json`)

The 5 skill-carving entries (`single-cell-rna-qc`, `instrument-data-to-allotrope`, `nextflow-development`, `scvi-tools`, `clinical-trial-protocol`) have no `plugin.json` at all. Skill directories contain only `SKILL.md` plus `scripts/`, `references/`, `LICENSE.txt`. Marketplace entry is the only source of plugin identity (`name`, `description`); version concept does not exist at the plugin level for those five.

## Component composition

### Skills (universal)

5 marketplace-listed skills plus 1 orphan (`scientific-problem-selection/`).

### Commands

None.

### Agents

None.

### Hooks

None.

### MCP servers

Inlined via `mcpServers` in plugin.json (no `.mcp.json` sibling files). Two distinct shapes: object form for 10 plugins, URL-string form for 2 plugins (10x-genomics, tooluniverse).

## Server runtime (MCP)

### Remote HTTP MCP

10 plugins (pubmed, biorender, synapse, wiley-scholar-gateway, biorxiv, clinical-trials, chembl, owkin, open-targets, medidata) declare `{"type": "http", "url": "https://..."}` — the MCP runtime is hosted at remote HTTPS endpoints. The repo ships no runtime code; README explicitly states the repo "will continue to host the marketplace.json long-term, but not the actual MCP servers."

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory in any plugin; no shebang'd launcher scripts. Skill scripts under `scripts/` are invoked as `python3 scripts/<name>.py` from SKILL.md instructions, not through a `bin/`-wrapped CLI.

## Dependency installation

### `requirements.txt` with manual user invocation

Only `instrument-data-to-allotrope/requirements.txt` exists. Pinned versions: `allotropy==0.1.55`, `pandas==2.0.3`, `openpyxl==3.1.2`, `pdfplumber==0.9.0`. SKILL.md instructs user to `pip install -r requirements.txt --break-system-packages` — user-driven, system-wide. Reproducibility note in the requirements.txt comment asks users to install the exact pinned set "to ensure identical ASM output." No SessionStart-based installer; no `${CLAUDE_PLUGIN_DATA}`-scoped venv.

### No managed install (user prerequisite)

Other skills (`single-cell-rna-qc`, `nextflow-development`, `scvi-tools`, `clinical-trial-protocol-skill`, `scientific-problem-selection`) ship no `requirements.txt` at all — they rely on the user having scanpy, Nextflow, etc. already installed system-wide. Skills with substantial scripts (scvi-tools has `cluster_embed.py`, `differential_expression.py`, `integrate_datasets.py`, `train_model.py`) have zero declared Python deps. Skill scripts are code for Claude to read and adapt, not to directly execute, so the dep surface is whatever Claude's downstream bash runs against the user's environment.

## User configuration and authentication

### Delegated to MCP server's own login

README directs the user to enter credentials via the `/plugin` → "Manage plugins" → "Configure" flow, but no `userConfig` schema is declared in any plugin.json. Authentication for biorender, synapse, wiley, 10x-genomics is delegated to each MCP server's own OAuth/web-login flow at connect time ("authenticate through the server's web interface when prompted"). No `userConfig`, no `sensitive: true` flag.

## Tool-use enforcement

### No enforcement (observational only)

No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks anywhere. No `hooks.json` files in this repo.

## Session context loading

### No session-context loading

No SessionStart hooks, no UserPromptSubmit hooks, no `additionalContext` payloads. No hooks anywhere in this repo.

## Live monitoring

### `monitors.json` absent

No `monitors.json` files anywhere.

## Plugin-to-plugin coordination

### `dependencies` field absent

None of the 11 surveyed plugin.json files declare a `dependencies` field. Tags follow `v<semver>` at the marketplace level.

## Testing

### No tests

No `tests/` directory, no test manifests, no test scripts.

## CI workflow shape

### Multi-workflow split by trigger and concern

Four workflow files: `claude.yml`, `claude-code-review.yml`, `claude-skill-review.yml`, `release.yml`. None run tests. Triggers: `claude.yml` runs `anthropics/claude-code-action@v1` on `issue_comment`, `pull_request_review_comment`, `issues`, `pull_request_review` with `@claude` mention gating. `claude-code-review.yml` runs on `pull_request` types `[opened, synchronize, ready_for_review, reopened]` and invokes `/code-review:code-review` from the `code-review@claude-code-plugins` marketplace plugin on every PR. `claude-skill-review.yml` is a one-line wrapper delegating to a reusable workflow `anthropics/healthcare/.github/workflows/claude-skill-review.yml@main` (cross-repo reference to the sibling Anthropic marketplace, pinned to a floating branch — any change to that upstream workflow applies on next PR without local version gate). `release.yml` runs on `push: tags: ['v*']`. Action pinning is by major tag (`actions/checkout@v4`, `softprops/action-gh-release@v1`, `anthropics/claude-code-action@v1`); no caching declared.

### `@claude` mention responder

`claude.yml` runs `anthropics/claude-code-action@v1` to let Claude respond to `@claude` mentions in PR/issue threads.

## Marketplace validation

### LLM-driven PR review

`claude-code-review.yml` and `claude-skill-review.yml` invoke Claude-driven review but don't run a schema validator. The repo relies on Claude-authored PR review as its primary quality gate for skill and manifest changes. No deterministic schema check exists to catch typos, missing required fields, or malformed JSON before merge. `.claude-plugin/marketplace.json` is not syntactically or semantically checked before merge to main.

## Release automation

### Skill-zip build via filesystem glob

`release.yml` triggered by `push: tags: ['v*']`. Loops over `*/`, gates on `SKILL.md` presence, zips each directory containing `SKILL.md` into `<dir>-<tag>.zip`, attaches all zips to a draft GitHub release via `softprops/action-gh-release@v1`. No MCP plugin packaging step — only skill directories are bundled (consistent with the remote-MCP design where plugin.json is the entire deliverable). `draft: true` in workflow but published releases v1.0.0 and v1.1.1 are both `draft: false`, indicating a manual publish step exists outside the automation. `generate_release_notes: true` produces PR-listing body automatically.

Doesn't read `marketplace.json` to discover packagable units — packaging is driven by filesystem layout. Adding a skill dir with a SKILL.md auto-ships a zip on next tag even if it isn't marketplace-listed (exhibited by `scientific-problem-selection-v1.1.1.zip`). MCP plugins produce no zip — their `plugin.json` is the deployable and is consumed in-place from the ref the marketplace points at.

No tag-sanity gates: no verify-tag-on-main step, no verify-tag-matches-plugin-version step, no tag-format regex beyond the `v*` glob. A tag pushed from any branch would still cut a release. Because skills have no `plugin.json`, there's no "verify tag == plugin version" check to run — the tag is the only authoritative version marker for skill plugins.

## Documentation surface

### Repo-root README only (no per-plugin)

`README.md` at repo root (~176 lines, ~5.8 KB) — sections: Quick Start, Available Plugins (grouped Remote MCP / Local MCP / Skills), Detailed Installation, Authentication Requirements, Support, License, Removed Plugins. Per-plugin README mostly absent — `clinical-trial-protocol-skill/README.md` exists (only one). Skills rely on `SKILL.md` frontmatter + body as their user-facing doc; MCP plugins rely on plugin.json `description` only. The "Removed Plugins" section in the README (currently documenting Benchling removal) is a small ad-hoc change-log substitute.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md`. No `architecture.md`. No `CLAUDE.md`. GitHub Releases' auto-generated notes serve as the de facto change log.

### Badges and status indicators

Absent.

## License declaration

### No repo-root LICENSE; per-skill LICENSE only

No repo-root LICENSE (`license: null` in GitHub API). `LICENSE.txt` (Apache-2.0) present inside each skill directory; no license attaches to the marketplace.json, README, or MCP plugin wrappers. GitHub's license detector returns `null`. Marketplace-level artifacts (marketplace.json, README, workflows) are under no declared license. Only the skill bundles are Apache-2.0.

## Community health files

### Community health files absent

No `CONTRIBUTING.md`, `SECURITY.md`, or `CODE_OF_CONDUCT.md` at root. `has_wiki: true` but no wiki URL surfaces in docs; likely unused.
