# anthropics/life-sciences

## Identification

- **URL**: https://github.com/anthropics/life-sciences
- **Stars**: 314
- **Last commit date**: 2026-01-26 (push timestamp 2026-01-27T00:33:20Z)
- **Default branch**: main
- **License**: no repo-root LICENSE (`license: null` in GitHub API). Apache-2.0 `LICENSE.txt` duplicated inside each skill directory (added in PR #34, 2026-01-26).
- **Sample origin**: primary (Anthropic-owned)
- **One-line purpose**: Claude Code marketplace of MCP servers and skills for life-sciences research, data analysis, and discovery. README opens: "This marketplace provides MCP (Model Context Protocol) servers and skills for life sciences tools."

## 1. Marketplace discoverability

- **Manifest layout**: single `.claude-plugin/marketplace.json` at repo root.
- **Marketplace-level metadata**: `metadata.{version, description}` wrapper (`version: "1.0.0"`, description string). No `metadata.pluginRoot`.
- **`metadata.pluginRoot`**: absent.
- **Per-plugin discoverability**: every plugin has `category: "life-sciences"` and `tags: [...]`. No `keywords` field used. Uniform across all 17 entries.
- **`$schema`**: absent.
- **Reserved-name collision**: no. Marketplace name `life-sciences` is not in the reserved-name blocklist.
- **Pitfalls observed**:
    - The `metadata.version: "1.0.0"` on the marketplace wrapper is decoupled from the git release tags `v1.0.0`/`v1.1.0`/`v1.1.1` — the wrapper hasn't been bumped as releases advanced, so the wrapper version is stale relative to the release channel. Consumers reading the wrapper see `1.0.0` while the repo is at `v1.1.1`.
    - `scientific-problem-selection/` exists on disk (with `SKILL.md`, scripts/, references/, LICENSE.txt) and is packaged by `release.yml` into `scientific-problem-selection-v1.1.1.zip`, but is NOT listed as a plugin in `marketplace.json` — the release-asset list and the marketplace plugin list have drifted. Only 17 plugins are installable via `@life-sciences`, even though 7 skill zips ship in the v1.1.1 release.

## 2. Plugin source binding

- **Source format(s) observed**: two forms of relative-path source.
    - Conventional: `"source": "./<plugin-dir>"` pointing at a directory containing `.claude-plugin/plugin.json` (10 of 17 entries — the MCP plugins plus the two `.mcpb`-bundle plugins `10x-genomics` and `tooluniverse`).
    - Skill-carving: `"source": "./"` paired with `"strict": false` and `"skills": ["./<skill-dir>"]` (5 of 17 entries — `single-cell-rna-qc`, `instrument-data-to-allotrope`, `nextflow-development`, `scvi-tools`, `clinical-trial-protocol`).
- **`strict` field**: mixed — default (implicit `true`) on the 12 MCP/bundle entries, explicit `strict: false` on the 5 skill-carving entries.
- **`skills` override on marketplace entry**: present on the 5 skill-carving entries. Each uses a single-element array with the skill directory path.
- **Version authority**: `plugin.json` only for the MCP/bundle plugins (no marketplace-entry `version` field). For the 5 skill-carving entries there is no plugin.json at all — each skill directory contains only `SKILL.md` (plus `scripts/`, `references/`, `LICENSE.txt`), so the marketplace entry is the only source of plugin identity (`name`, `description`), and "version" does not exist as a concept at the plugin level for those five.
- **Pitfalls observed**:
    - Skill-carving plugins have no versionable `plugin.json` — they are identified solely by marketplace-entry `name` + the SKILL.md frontmatter `name`. This means bumping a skill version requires re-releasing and re-tagging the whole repo; there is no per-skill plugin.json version to bump.
    - `clinical-trial-protocol` marketplace entry points at directory `clinical-trial-protocol-skill/` — the plugin `name` and the directory name diverge. The SKILL.md frontmatter `name: clinical-trial-protocol-skill` matches the directory but not the marketplace plugin ID. This mismatch is deliberately noted in branch history (`claude/slack-copy-clinical-trial-protocol-X6rjk`).
    - `source: "./"` across five entries means the same root directory is bound as the "plugin root" for five distinct marketplace entries; `strict: false` + `skills: [...]` is what carves them apart. Inferred from marketplace.json structure.

## 3. Channel distribution

- **Channel mechanism**: no split. Users install via `@life-sciences` at HEAD; there is no `stable` vs `latest` pair. Release tags (v1.0.0, v1.1.0, v1.1.1) exist but consumers are not directed to pin to them in the README.
- **Channel-pinning artifacts**: absent. No `stable-tools` / `latest-tools` style, no dev-counter scheme.
- **Pitfalls observed**:
    - Tags are published as GitHub releases (with zip assets) but marketplace consumers don't have a channel-aware install UX — install is `/plugin marketplace add anthropics/life-sciences` (tracking `main`). Inferred from README install instructions.

## 4. Version control and release cadence

- **Default branch name**: main.
- **Tag placement**: on main (inferred — release workflow triggers on `push: tags: ['v*']` with no branch restriction; tag-on-main is the natural reading).
- **Release branching**: none. Feature work happens on topic branches (e.g. `daisy/initial-marketplace`, `jwei/nextflow`, `andres/add-medidata-plugin`) merged via PR to main.
- **Pre-release suffixes**: none observed (v1.0.0, v1.1.0, v1.1.1 only). Release workflow hardcodes `prerelease: false`.
- **Dev-counter scheme**: absent. All per-plugin `plugin.json` files that exist hold `version: "1.0.0"` — no monotonic bumping.
- **Pre-commit version bump**: no. Confirmed by inspection of workflows and `.gitignore`; no hook directory present.
- **Pitfalls observed**:
    - All eleven plugin.json files surveyed (10 MCP + tooluniverse) hold `version: "1.0.0"` unchanged across the v1.0.0 → v1.1.1 release sequence. Plugin-level versions and marketplace release tags have drifted permanently; `plugin.json.version` appears to be written once at plugin introduction and never bumped.
    - Only three tags over the lifetime of the repo (2025-10 → 2026-01), one of them (v1.0.0) predating most plugins. Release cadence is coarse and doesn't match per-plugin change pace.

## 5. Plugin-component registration

- **Reference style in plugin.json**: all MCP plugins use inline `mcpServers` config objects. Two distinct shapes observed:
    - Object form: `"mcpServers": {"<ServerName>": {"type": "http", "url": "https://..."}}` — used by pubmed, biorender, synapse, wiley-scholar-gateway, biorxiv, clinical-trials, chembl, owkin, open-targets, medidata.
    - String form: `"mcpServers": "https://.../<plugin>.mcpb"` — used by 10x-genomics and tooluniverse, pointing at `.mcpb` bundle URLs hosted on the vendor's own GitHub releases (not the life-sciences repo).
- **Components observed**:
    - skills: yes (5 marketplace-listed + 1 orphan `scientific-problem-selection/`)
    - commands: no
    - agents: no
    - hooks: no
    - .mcp.json: no (mcpServers is inlined in plugin.json)
    - .lsp.json: no
    - monitors: no
    - bin: no
    - output-styles: no
- **Agent frontmatter fields used**: not applicable — no agents.
- **Agent tools syntax**: not applicable.
- **Pitfalls observed**:
    - The `mcpServers` value-as-URL-string form (10x-genomics, tooluniverse) is docs-silent — the plugin reference example shows object-form `mcpServers`. Whether a URL-string value is a supported alternative or a custom extension of the loader is unresolved from the docs captured locally. The fact that the shipped `10x-genomics/txg-node.mcpb` (16 MB) also sits in the directory suggests the URL-string form triggers a remote fetch, with the in-repo `.mcpb` either as fallback or as a cached copy; cannot verify without the loader source.
    - Two distinct `.mcpb` bundle files exist at `10x-genomics/txg-node.mcpb` and `tooluniverse/tooluniverse.mcpb`, duplicating what the string-URL would fetch. Whether both are served and which wins is not documented.

## 6. Dependency installation

- **Applicable**: partially. No hooks-based SessionStart installer anywhere in the repo. Only `instrument-data-to-allotrope/requirements.txt` exists; the skill delegates install to the user via a comment at the top of that file (`pip install -r requirements.txt --break-system-packages`). Other skills (`single-cell-rna-qc`, `nextflow-development`, `scvi-tools`, `clinical-trial-protocol-skill`, `scientific-problem-selection`) ship no `requirements.txt` at all — they rely on the user having scanpy, Nextflow, etc. already installed system-wide.
- **Dep manifest format**: `requirements.txt` (one skill only — `instrument-data-to-allotrope`). Pinned versions (`allotropy==0.1.55`, `pandas==2.0.3`, `openpyxl==3.1.2`, `pdfplumber==0.9.0`).
- **Install location**: not applicable — no installer runs; user invokes `pip install` manually.
- **Install script location**: none. SKILL.md instructs user to `pip install -r requirements.txt --break-system-packages`.
- **Change detection**: none — user-driven install, not agent-driven.
- **Retry-next-session invariant**: not applicable.
- **Failure signaling**: not applicable.
- **Runtime variant**: Python `pip` (user-driven, system-wide with `--break-system-packages`).
- **Alternative approaches**: none observed. No PEP 723 inline metadata, no `uvx`/`npx` lazy fetching, no pointer-file pattern.
- **Version-mismatch handling**: none — reproducibility note in the requirements.txt comment asks users to install the exact pinned set "to ensure identical ASM output."
- **Pitfalls observed**:
    - Skills with substantial scripts (scvi-tools has `cluster_embed.py`, `differential_expression.py`, `integrate_datasets.py`, `train_model.py`, etc.) have zero declared Python deps. Inferred design: skill scripts are code for Claude to read and adapt, not to directly execute, so the dep surface is whatever Claude's downstream bash runs against the user's environment.
    - Recommending `--break-system-packages` to lay files directly into the system Python is user-hostile and bypasses the isolation model that `${CLAUDE_PLUGIN_DATA}`-scoped venvs are designed to provide. Observed once; consequence of the absence of a SessionStart dep-install hook.

## 7. Bin-wrapped CLI distribution

- **Applicable**: no. No `bin/` directory in any plugin; no shebang'd launcher scripts. Skill scripts under `scripts/` are invoked as `python3 scripts/<name>.py` from SKILL.md instructions, not through a `bin/`-wrapped CLI.
- **`bin/` files**: none.
- **Shebang convention**: not applicable.
- **Runtime resolution**: not applicable.
- **Venv handling (Python)**: not applicable.
- **Platform support**: not applicable.
- **Permissions**: not applicable.
- **SessionStart relationship**: not applicable.
- **Pitfalls observed**: none.

## 8. User configuration

- **`userConfig` present**: no.
- **Field count**: none.
- **`sensitive: true` usage**: not applicable.
- **Schema richness**: not applicable.
- **Reference in config substitution**: not applicable.
- **Pitfalls observed**:
    - README directs the user to enter credentials via the `/plugin` → "Manage plugins" → "Configure" flow, but no `userConfig` schema is declared in any plugin.json. Authentication for biorender, synapse, wiley, 10x-genomics appears to be delegated to each MCP server's own OAuth/web-login flow (remote HTTP MCPs) rather than plumbed through plugin-level config. Inferred from README wording "authenticate through the server's web interface when prompted."

## 9. Tool-use enforcement

- **PreToolUse hooks**: none.
- **PostToolUse hooks**: none.
- **PermissionRequest/PermissionDenied hooks**: absent.
- **Output convention**: not applicable.
- **Failure posture**: not applicable.
- **Top-level try/catch wrapping**: not applicable.
- **Pitfalls observed**: none — no hooks anywhere in this repo.

## 10. Session context loading

- **SessionStart used for context**: no.
- **UserPromptSubmit for context**: no.
- **`hookSpecificOutput.additionalContext` observed**: no.
- **SessionStart matcher**: not applicable.
- **Pitfalls observed**: none.

## 11. Live monitoring and notifications

- **`monitors.json` present**: no.
- **Monitor count + purposes**: none.
- **`when` values used**: not applicable.
- **Version-floor declaration**: not applicable.
- **Pitfalls observed**: none.

## 12. Plugin-to-plugin dependencies

- **`dependencies` field present**: no. None of the 11 surveyed plugin.json files declare a `dependencies` field.
- **Entries**: none.
- **`{plugin-name}--v{version}` tag format observed**: no — tags follow `v<semver>` at the marketplace level.
- **Pitfalls observed**: none.

## 13. Testing and CI

- **Test framework**: none — no `tests/` directory, no test manifests, no test scripts.
- **Tests location**: not applicable.
- **Pytest config location**: not applicable.
- **Python dep manifest for tests**: not applicable.
- **CI present**: yes (four workflows) but none of them run tests.
- **CI file(s)**: `claude.yml`, `claude-code-review.yml`, `claude-skill-review.yml`, `release.yml`.
- **CI triggers**:
    - `claude.yml`: `issue_comment`, `pull_request_review_comment`, `issues`, `pull_request_review` with `@claude` mention gating.
    - `claude-code-review.yml`: `pull_request` types `[opened, synchronize, ready_for_review, reopened]`.
    - `claude-skill-review.yml`: same PR triggers.
    - `release.yml`: `push: tags: ['v*']`.
- **CI does**:
    - `claude.yml` — runs `anthropics/claude-code-action@v1` to let Claude respond to `@claude` mentions in PR/issue threads.
    - `claude-code-review.yml` — invokes `/code-review:code-review` from the `code-review@claude-code-plugins` marketplace plugin on every PR.
    - `claude-skill-review.yml` — delegates to a reusable workflow `anthropics/healthcare/.github/workflows/claude-skill-review.yml@main` (cross-repo reference to the sibling Anthropic marketplace).
    - `release.yml` — globs `*/` and zips any directory containing `SKILL.md` into `<dir>-<tag>.zip`, attaches to a draft GitHub release.
- **Matrix**: none.
- **Action pinning**: tag (`actions/checkout@v4`, `softprops/action-gh-release@v1`, `anthropics/claude-code-action@v1`). Cross-repo reusable workflow pinned to `@main` (floating ref — not a SHA, not a tag).
- **Caching**: none declared.
- **Test runner invocation**: not applicable (no tests).
- **Pitfalls observed**:
    - No automated manifest validation in CI — `.claude-plugin/marketplace.json` is not syntactically or semantically checked before merge to main.
    - `claude-skill-review.yml` reuses `anthropics/healthcare/.github/workflows/claude-skill-review.yml@main` — tight coupling to a separate Anthropic-owned repo pinned to a floating branch. Any change to that upstream workflow applies to this repo on next PR, without a local version gate.
    - `release.yml` zips every top-level directory with a SKILL.md, not just entries referenced from marketplace.json. This is how `scientific-problem-selection-v1.1.1.zip` ends up as a release asset even though `scientific-problem-selection` is not a marketplace-listed plugin.

## 14. Release automation

- **`release.yml` (or equivalent) present**: yes.
- **Release trigger**: `push: tags: ['v*']`.
- **Automation shape**: skill-zip build + draft release. Loops over `*/`, zips each directory containing `SKILL.md` into `<dir>-<tag>.zip`, attaches all zips to a draft release. No MCP plugin packaging step — only skill directories are bundled (consistent with the remote-MCP design where plugin.json is the entire deliverable).
- **Tag-sanity gates**: none — no verify-tag-on-main step, no verify-tag-matches-plugin-version step, no tag-format regex validation beyond the `v*` glob pattern.
- **Release creation mechanism**: `softprops/action-gh-release@v1`.
- **Draft releases**: yes — `draft: true`. Published releases v1.0.0 and v1.1.1 are both `draft: false` (per GitHub API), indicating a manual publish step exists outside the automation.
- **CHANGELOG parsing**: no explicit CHANGELOG file to parse; `generate_release_notes: true` produces PR-listing body automatically.
- **Pitfalls observed**:
    - No tag-sanity gates means a tag pushed from any branch would still cut a release. Trust is entirely in who holds tag-push permissions on the repo.
    - Because skills have no `plugin.json`, there's no "verify tag == plugin version" check to run — the tag is the only authoritative version marker for skill plugins.
    - Non-skill plugins (MCPs, `.mcpb` bundles) receive no release artifact at all — their `plugin.json` is the deployable and is consumed in-place from the ref the marketplace points at. This is consistent with the README's claim that the repo "will continue to host the marketplace.json long-term, but not the actual MCP servers."

## 15. Marketplace validation

- **Validation workflow present**: no dedicated validator. The `claude-code-review.yml` and `claude-skill-review.yml` workflows invoke Claude-driven review but don't run a schema validator.
- **Validator**: not applicable.
- **Trigger**: not applicable.
- **Frontmatter validation**: no automated validation. Claude Skill Review likely comments on frontmatter issues discovered by LLM inspection, but no deterministic validator.
- **Hooks.json validation**: not applicable (no hooks).
- **Pitfalls observed**:
    - The repo relies on Claude-authored PR review as its primary quality gate for skill and manifest changes. No deterministic schema check exists to catch typos, missing required fields, or malformed JSON before merge.

## 16. Documentation

- **`README.md` at repo root**: present (~176 lines, ~5.8 KB). Sections: Quick Start, Available Plugins (grouped Remote MCP / Local MCP / Skills), Detailed Installation, Authentication Requirements, Support, License, Removed Plugins.
- **Owner profile README at `github.com/anthropics/anthropics`**: absent — no `<owner>/<owner>` repo found via gh api on 2026-04-30
- **`README.md` per plugin**: mostly absent. `clinical-trial-protocol-skill/README.md` exists (only one). Skills rely on `SKILL.md` frontmatter + body as their user-facing doc. MCP plugins rely on plugin.json `description` only.
- **`CHANGELOG.md`**: absent. GitHub Releases' auto-generated notes serve as the change log.
- **`architecture.md`**: absent — neither repo root nor per plugin.
- **`CLAUDE.md`**: absent.
- **Community health files**: none observed (no `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md` at root).
- **LICENSE**: absent at repo root. `LICENSE.txt` (Apache-2.0) present inside each skill directory; no license attaches to the marketplace.json, README, or MCP plugin wrappers. GitHub's license detector returns `null`.
- **Badges / status indicators**: absent.
- **Pitfalls observed**:
    - No root license means the marketplace-level artifacts (marketplace.json, README, workflows) are under no declared license. Only the skill bundles are Apache-2.0.
    - The `Removed Plugins` section in the README (currently documenting Benchling removal) is a small ad-hoc change-log substitute — no formal deprecation process is visible.
    - `has_wiki: true` but no wiki URL is surfaced in docs; likely unused.

## 17. Novel axes

- **Skill-carving via `strict: false` + shared `source: "./"`**: five distinct marketplace plugins (`single-cell-rna-qc`, `instrument-data-to-allotrope`, `nextflow-development`, `scvi-tools`, `clinical-trial-protocol`) all point at the repo root as `source: "./"`, with `strict: false` disabling validation of a `.claude-plugin/plugin.json` at that root, and `skills: ["./<skill-dir>"]` carving the actual skill out. This lets a repo host many independent skills without needing a `plugin.json` wrapper per skill — the skill's SKILL.md + its directory tree is the entire deliverable, and the marketplace entry supplies the name/description/category/tags that plugin.json would otherwise carry. Effectively, the marketplace entry replaces plugin.json for skills.
- **`mcpServers` as a URL string pointing at `.mcpb` bundle**: `10x-genomics` and `tooluniverse` set `"mcpServers": "<url to .mcpb>"` rather than an object. The `.mcpb` is a packaged MCP server bundle hosted on the vendor's own GitHub releases (txg-mcp, ToolUniverse). In-repo `.mcpb` files of the same name also exist in those two plugin directories, 16 MB and smaller respectively — either as fallback or as cached copies.
- **Release zip-per-skill-dir via filesystem glob**: `release.yml` doesn't read `marketplace.json` to discover packagable units — it globs `*/` and gates on `SKILL.md` presence. Consequences: (a) adding a skill dir with a SKILL.md automatically ships a zip on next tag even if it isn't marketplace-listed (exhibited by `scientific-problem-selection-v1.1.1.zip`); (b) MCP plugins produce no zip. The packaging is driven by filesystem layout, not by marketplace-entry inclusion.
- **Cross-repo reusable workflow for skill review**: `claude-skill-review.yml` is a one-line wrapper around `anthropics/healthcare/.github/workflows/claude-skill-review.yml@main` — the marketplace repo outsources its skill-review CI to a sibling Anthropic marketplace repo's workflow, creating a shared Anthropic-wide skill-review pipeline pinned to a floating branch.
- **Stale plugin.json version across real releases**: every plugin.json holds `version: "1.0.0"` regardless of release cut. The release-tag version (`v1.1.1`) lives only on git tags and release-asset filenames (`<skill>-v1.1.1.zip`). For skills this is coherent because skills have no plugin.json; for MCP plugins it means plugin.json versions are permanently pinned at `1.0.0`.
- **Marketplace wrapper `metadata.version` vs release tag drift**: the `metadata.version: "1.0.0"` in marketplace.json has not been bumped across release cuts — it names the marketplace schema/entry-set version at repo birth, not the current release.
- **Deliberate split between marketplace-as-registry and MCP-hosting-elsewhere**: README explicitly states the repo "will continue to host the marketplace.json long-term, but not the actual MCP servers." MCP runtime is remote HTTP endpoints or externally-hosted `.mcpb` bundles; the repo ships no runtime code for MCP plugins, only plugin.json metadata pointing at third-party hosting.

## 18. Gaps

- Whether `"mcpServers": "<url>"` as a string value is a supported plugin.json field or an undocumented convention handled by a specific loader path could not be resolved from the captured docs (`docs-plugins-reference.md`'s example shows object form). Source that would resolve: Claude Code loader source for plugin.json parsing, or an explicit docs section on `.mcpb` bundle URLs.
- Whether the user-facing install-credential flow (`/plugin` → "Configure") works for plugins that declare no `userConfig` — README implies it does, but no mechanism was found in the repo itself. Likely handled by the MCP server's own OAuth at connect time, but not verified.
- Whether `metadata.version` on the marketplace wrapper has any runtime consumer (cache invalidation? display?) or is purely informational. Not covered by `docs-plugin-marketplaces.md` beyond the schema.
- Tag-on-main assumption not strictly verified — the three release tags (v1.0.0, v1.1.0, v1.1.1) point at commits that are plausibly on main, but branch-ancestry was not checked via `git merge-base --is-ancestor`.
- Whether the in-repo `.mcpb` files (`10x-genomics/txg-node.mcpb` 16 MB, `tooluniverse/tooluniverse.mcpb`) are used by the loader at all, or are relics tracked from before the plugin.json switched to the URL-string form, could not be determined without loader source.
- Whether `scientific-problem-selection` is intentionally unlisted (draft skill being tested in-tree with release artifacts built opportunistically) or is a drift defect from the marketplace.json not being synced with filesystem contents. README "Removed Plugins" section lists only Benchling; no mention of this skill.
- The `has_wiki: true` flag means a GitHub wiki is enabled but no wiki URL or link surfaces in any docs; contents unverified.
- `claude-code-review.yml` references the `code-review@claude-code-plugins` plugin from `https://github.com/anthropics/claude-code.git` — whether that repo and plugin exist as described (and what review discipline it applies to this repo's PRs) is outside scope of this research.
