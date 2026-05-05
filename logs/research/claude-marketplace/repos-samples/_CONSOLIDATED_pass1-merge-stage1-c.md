# Sample

Merge of 6 partials (bins 13-18) into `_CONSOLIDATED_pass1-merge-stage1-c.md`. Functional roles with implementation paths and qualitative descriptions; no inline citations (see `references` verb for provenance).

## Marketplace manifest layout

Where the marketplace inventory is declared and how many manifests coexist relative to the plugin trees they advertise.

### Single root marketplace.json

One `.claude-plugin/marketplace.json` at repo root listing every plugin entry (single-plugin or many) via relative `source` paths. The standard claude-code aggregator shape — manifest and plugin trees travel together in one git repo. `strict` is implicit-true (omitted) on every entry. Appropriate for monorepo marketplaces and single-plugin-at-root layouts alike; adding a second plugin only requires another entry.

### Self-hosted single-plugin marketplace at repo root

`.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` coexist at the same repo root, with the marketplace's only entry pointing back at the same root via `"source": "./"` (or `"."`). The marketplace IS the plugin — adding the repo as a marketplace and installing the one plugin it advertises are the only paths users have. Trivially deployable for a single-plugin author and matches how users typically encounter the work, but is not extensible to a second plugin without restructuring. Frees the author from running a separate aggregator marketplace solely to publish one plugin.

### Nested mini-marketplace inside a plugin directory

A second `marketplace.json` lives one level deep (e.g. `<plugin-dir>/.claude-plugin/marketplace.json`) listing only the enclosing plugin with `"source": "."`. Lets the plugin be installed either via the aggregator marketplace OR as its own standalone marketplace pointing at its own directory. Drift hazard: the nested entry's version field is hand-maintained and observed lagging the plugin's own `plugin.json`.

### No in-repo marketplace; aggregator dispatched cross-repo

The plugin repo carries no `.claude-plugin/marketplace.json` at all. A separate (often private) marketplace-aggregator repo registers the plugin; the plugin repo's release workflow fires a `repository_dispatch` event (e.g., `plugin-release` with `{plugin, version}` payload, authenticated by a `MARKETPLACE_TOKEN` PAT scoped to the aggregator) to update the aggregator. Appropriate when the author wants the plugin repo to look like a normal source repo (npm-publishable, no marketplace concerns) and centralizes discovery in a separate aggregator they control. Constrains forks — without the cross-repo dispatch token, a fork cannot fully release. Constrains discoverability fields — `category`/`tags`/`keywords` may live only on the aggregator side, invisible from the plugin repo.

### No marketplace manifest at all

Repo ships a single bare plugin via `.claude-plugin/plugin.json` only; install is by `git clone` + `claude --plugin-dir <path>`. Plugin is invisible to `/plugin install` discovery without an external marketplace registering it. Discoverability metadata may live in a sibling `package.json` for npm-style aggregators, leaving any marketplace consumer that reads only `plugin.json` blind.

### Parallel non-marketplace inventory

Same repo carries `marketplace.json` AND a separate `config.json` enumerating a strictly larger set of modules + a "skills" axis for an alternate installer (npx self-installer). The two inventories are intentionally disjoint: slash-command flow gets the marketplace subset; npx flow gets the richer config.json menu with its own operations DSL (`copy_file`, `copy_dir`, `merge_dir`, `run_command`).

### Custom top-level extension fields

Repo adds non-standard top-level fields to the marketplace manifest that Claude Code presumably ignores. The `bundles` field groups plugins into named user-facing collections (`quick-start-java`, `core`, etc.) with display metadata; consumed only by the repo's own out-of-band installers (web installer, custom CLI), not by `/plugin install`. Appropriate when the schema lacks a primitive the author needs (here: plugin grouping for UI presentation) and the author is willing to ship their own consumer to read the extension. Constrains: users on the built-in CLI cannot access the grouping; the extension is invisible to anyone not running the custom installer.

### Source-binding mechanics gotcha

Across layouts using `"source": "./"`, a live schema gotcha: bare `"."` fails marketplace validation; the trailing slash is required. Marketplace-level `metadata` wrapper and `metadata.pluginRoot` may both be absent for this layout.

## Marketplace-level metadata

Top-level fields on `marketplace.json` describing the marketplace itself, separate from per-plugin entries.

### Minimalist top-level keys only

Marketplace declares only the minimum keys Claude Code needs — typically `name`, `owner`, and the `plugins` array, sometimes a top-level `description`. There is no `metadata` wrapper, no `metadata.pluginRoot`, no `metadata.description`. A consuming aggregator that expects nested metadata sees nothing under the wrapper key. Appropriate when the author treats the marketplace purely as a vehicle for the plugin(s) it advertises and does not anticipate a third party indexing its metadata fields.

### Description and owner object at top level

`marketplace.json` carries `name`, `description`, and an `owner` object (with `name` and `url`) at top level — no `metadata` wrapper, no marketplace-level version. Mid-weight choice: enough metadata for a consumer to read what the marketplace is, but no taxonomy for category-based discovery and no version axis distinct from per-plugin versions.

### `metadata.{description, version, license}` wrapper

Marketplace uses a `metadata` object for catalog-level fields (description, version, license, sometimes `pluginRoot`), keeps `name`/`owner` at top level, and may equip per-plugin entries with their own discoverability fields. Maximally discoverable shape — surfaces the marketplace identity separately from plugin identity, exposes a marketplace-level version distinct from plugin versions, and signals license at the marketplace surface. Trade-off: marketplace-level version is a third version axis (alongside marketplace-entry version and plugin.json version) with no enforced sync between any pair.

### `metadata.{title, description, categories, tags}` wrapper

A richer `metadata` block adds catalog-scoped categories and tags so the marketplace itself can be browsed taxonomically (independent of per-plugin tags). Appropriate when the marketplace is single-plugin and the metadata wrapper is the natural place to advertise the whole repo. Constrains nothing about how the plugin source resolves but adds a second source of truth for description/version that must be kept in lockstep with `plugin.json`.

### `$schema` declaration

Top-level `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"` declared on the marketplace document. Enables editor IntelliSense but is generally not validated in CI — remote schema is fetched at edit time only. Adoption is uneven across the corpus; many marketplaces ship without the field.

## Per-plugin discoverability metadata

Searchable/filterable fields on the plugin entry inside the marketplace — what a marketplace consumer indexes to make plugins findable.

### Sparse — name/source/description only

Plugin entries carry only the fields required to install (`name`, `source`, sometimes `description` and `version`). No `category`, `tags`, or `keywords` on the marketplace entry. Where keywords exist, they live in `plugin.json` and are not surfaced into the marketplace entry. GitHub repo topics may compensate as an external discovery surface but do not flow into the manifest. Discoverability is therefore carried by the description prose and any external surface (README, GitHub topics), not by structured manifest metadata.

### Description + version + author + keywords

Mid-richness entry: human-readable description, semver `version` (duplicating the plugin's own `plugin.json` version), `author` block, and a `keywords` array of 5-11 terms. No `category` or `tags`. Sibling entries in the same marketplace can drift between this richness and description-only — no enforced schema across siblings.

### Category-only

Each entry carries `category` (values like `development`, `productivity`) and no `tags`/`keywords`. Single-axis classification for a small fixed taxonomy.

### Keywords + category

Each plugin entry carries a `keywords` array (typically 5-7 strings) and a `category` string (commonly `"development"`). Provides search/filter surface for marketplace UIs. Inconsistency within a single marketplace is observed — one plugin shipping `keywords: []` while siblings carry full lists hurts discoverability for that plugin specifically.

### Marketplace-entry facets plus duplicated keywords on plugin.json

The marketplace entry carries `category` and `tags`; `plugin.json` independently carries `keywords` with semantically identical values. Two field names for the same intent across two manifests — drift surface but no enforcement. The marketplace consumes its facets; the plugin manifest's `keywords` are decorative unless surfaced elsewhere.

### Bare-minimum plugin.json (name, version, description only)

`plugin.json` declares only `name`, `version`, `description` — no `category`, `tags`, `keywords`, `author`, or `homepage`. Discoverability is fully delegated to whichever marketplace aggregator carries the entry. Workable when an external aggregator supplies the metadata, but ships zero plugin-self-described discovery facets and depends on the aggregator being authoritative.

### `$schema` absence on per-plugin manifests

`$schema` URL absent from `plugin.json` across most of the corpus. Editor schema-completion and ahead-of-time validation are unavailable; reactive detection (install errors, CI gates) is the only feedback channel.

## Plugin source binding

How a marketplace entry resolves to the plugin tree it serves at install time.

### Relative same-repo (`./`)

Single-plugin marketplace where the plugin lives at the repo root; `source` is `"./"`. Trailing slash is mandatory — bare `"."` fails validation. Suits the single-plugin-at-root layout; trivial binding, no version drift surface when the marketplace entry omits its own version. No remote re-fetch — install resolves entirely from whatever ref the consumer added. Implies one repo equals one plugin.

### Relative subdirectory per plugin in monorepo

The marketplace entry uses `source: "./<plugin-dir>"` to point at one of several plugin trees under a single repo. Used when a marketplace publishes multiple plugins that share contributor docs, vendored dev toolkits, or cross-cutting build infrastructure. Each plugin tree is self-contained; the marketplace.json enumerates them. Implies a contributor convention that repo-level state (root README, CLAUDE.md, settings.json) is non-shipped infrastructure and the plugin trees are the published artifacts. For relative sources the docs say `plugin.json` wins on version; the marketplace entry is the discovery surface.

### Git-subdir self-pointing

A `git-subdir` source whose `url` is the same repo as the marketplace manifest, with `path: <subdir>` naming a subdirectory. `plugin install` re-fetches the plugin from GitHub even when the consumer has already cloned the marketplace — a network round-trip that a `relative` source would avoid, but `git-subdir` permits standalone marketplace-add without expecting users to clone. Appropriate when the author wants users to install via `claude plugin marketplace add <owner>/<repo>` directly without cloning. Trade-off is the redundant fetch when a clone already exists locally.

### Direct git install (no marketplace.json in source repo)

Users install via `claude plugin install github:<owner>/<repo>` — no marketplace-level binding because no marketplace.json exists in the plugin repo. The cross-repo aggregator handles binding separately.

### `strict` field default

Across the corpus, `strict` is absent on every marketplace entry, taking the implicit-true default. Whether authors intended strict mode is generally not documented in samples; the absence is uniform but not deliberate.

### `skills` override on marketplace entry absent

The marketplace entry never overrides the plugin's component layout — no `skills` carving, no path remapping. Full plugin trees ship as authored. When alternate-runtime manifests (`.cursor-plugin/plugin.json`) need different paths, they declare those at the plugin-manifest level rather than the marketplace level.

### Parallel duplicated metadata across multiple manifests

The same plugin's `version` (and sometimes `description`/`keywords`) is carried independently in `marketplace.json`, `plugin.json`, and (for Node plugins) `package.json` — three separate copy-paste sites for the same string. Drift surfaces in characteristic shapes: `package.json` years behind `plugin.json` (npm metadata not kept in sync), `marketplace.json` behind `plugin.json` (release skill bumps plugin manifest but not marketplace entry across multiple releases), or per-plugin `plugin.json` lagging marketplace's projection. Different consumers (`/plugin install`, marketplace UIs, custom installers) read different fields, and each may answer differently for the same plugin. The pattern is the failure mode, not the choice.

## Version authority

Where the canonical version of a plugin lives, and how many parallel version streams the manifest surface admits.

### Single source — plugin.json only

The plugin's `version` string lives exclusively in `plugin.json`; the marketplace entry omits a version field. Users who want to pin must do so at the Git ref level (`@<sha>` or `@<tag>`). Eliminates drift risk by construction (one place, one truth) but pushes pinning out of the marketplace abstraction. Simplest possible shape; works for single-plugin-at-root layouts.

### Dual source — marketplace entry + plugin.json, hand-aligned

Both `plugin.json.version` and the marketplace entry's `version` carry the same string, hand-maintained at release time with no validating workflow. Drift is observed in practice — one sample carries marketplace `1.9.0` against plugin `0.1.6` where the marketplace ran ahead during independent bumps and was not reconciled. The marketplace path uses whichever the consumer's installer reads first. Trade-off: marketplace consumers can read the version directly without dereferencing `plugin.json`, at the cost of a second hand-maintained surface.

### Triple source — marketplace metadata version + per-entry version + plugin.json version

A monorepo with marketplace-level `metadata.version` (`0.4.0`), per-plugin marketplace-entry `version` (`0.1.0`), and per-plugin `plugin.json.version` (`0.1.0`). Contributor docs designate the latter two as the "must match" pair and the marketplace metadata version as an independent stream tracking the marketplace itself. Three-way version space with two enforced relationships and one independent axis — the most version-aware shape and also the most drift-prone.

### Dual-manifest versioning with CI gate

`package.json` (npm) and `.claude-plugin/plugin.json` both carry the version because both ecosystems insist on owning it. Neither derives from the other. CI enforces equality with a `Verify version sync` step that fails the build when they differ. CLAUDE.md prescribes "after bumping plugin.json, also update package.json before creating the GitHub Release." A "two sources, one gate" pattern, distinct from single-source-of-truth derivation.

### Triple-manifest versioning, ungated

Three independent files (marketplace.json, plugin.json, package.json) each declare the version with no CI gate. Drift is possible and observed in practice — declared version ahead of the latest tagged release, manual bump commits without tags. The risk materializes when users following GitHub Releases see one version while marketplace installs (HEAD) deliver another.

### Multi-artifact lockstep across N>2 manifests

Version mirrored across plugin manifest plus one or more sibling artifact manifests — `package.json`, `pyproject.toml`, firmware `.fam` `fap_version`, source-embedded version strings (`ui.c` constants, Go `-ldflags`-injected vars). Coordination via a release checklist or `Makefile` `release` target; no structural verification. Appropriate when the plugin is one artifact among several in a multi-product repo. Constraint: a release commit must touch every artifact's version field or one of them silently lags.

### Cross-runtime version multiplication

When the same plugin ships under multiple runtimes, each runtime's manifest carries its own version field. A repo supporting Claude + Cursor + Codex maintains `version` in `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, the marketplace entry, and any runtime-specific install hint. Hand-discipline alignment with no cross-manifest validation; commit history shows explicit "align cursor plugin version to match claude plugin" commits as the only enforcement mechanism.

### Three-way version split (marketplace vs npm vs git tags)

Marketplace + plugin.json (5.6.1), `package.json` consumed by npx installer (6.7.0), and git tags on master (v6.8.2) all carry independent version numbers that drift independently. Each is meaningful in its own context but not reconciled. The npx installer asks GitHub's releases API for `tag_name` at runtime and bypasses the checked-in version fields entirely, so installed artifacts match the tag while a consumer reading the source files sees stale fields.

### Tag-on-main with synthesized dev version inside binary

Plugin manifest carries plain semver tracking releases. Dev builds of an embedded binary synthesize a `-dev.N+sha` suffix at build time via `git describe --tags --match 'v*' --always --long` and `-ldflags`, never applied to git tags. Wrapper script recognizes the dev marker (`version.includes("-dev.")`) and applies looser version-comparison rules. Appropriate when binary builds outpace plugin releases and the wrapper needs to discriminate locally-built vs released binaries.

## Channel distribution

Whether the plugin offers stable/latest channel separation or any pinning surface beyond raw git refs.

### Single channel — main HEAD only

No stable/latest split, no release branches, no channel-pinning artifacts. Users `/plugin marketplace add` resolves to whatever `main` (or `master`) currently points at. README typically says "re-run install to update." Appropriate for hobby-grade plugins where the distinction between "tested release" and "current main" hasn't justified the maintenance overhead. Constrains downstream pinning to commit SHAs (the only stable ref a consumer can name).

### Tag-pinned with trunk-based releases

Annotated tags on main (e.g., `v1.0.0`, `v1.0.1`, `v1.1.0` with corresponding GitHub releases). Users pin via `/plugin marketplace add ...@vX.Y.Z`. Appropriate for stable-release discipline without channel separation; constrains contributors to a tag-on-main workflow with no in-flight `release/*` branches.

### Multi-channel via parallel distribution paths

The plugin is published to more than one delivery surface (marketplace + npm `npx <plugin>@latest` + direct GitHub install) without a unified pinning story. Each channel carries its own version semantics (marketplace uses git refs, npm uses standard semver tags). Appropriate when the plugin needs to support runtimes outside Claude Code (Cursor/Codex/Windsurf via npm). Constrains: consumers and channels can diverge between tags; an unreleased commit on main may already be visible to marketplace consumers while npm consumers still see the last published version.

### Pre-release suffix as channel marker

Maven-style `1.0.0-SNAPSHOT` suffix in `plugin.json` versions during development; stripped at release. Custom version comparator in the repo's installer treats SNAPSHOT as strictly older than the bare release. Not a SemVer pre-release identifier (`-rc`, `-beta`) and not recognized by Claude Code's plugin machinery. Appropriate when the author is borrowing conventions from a host-language ecosystem (here Java/Quarkus). Constrains: any consumer not running the custom installer treats `1.0.0-SNAPSHOT` and `1.0.0` as different opaque strings — naive ordering breaks.

### Floating snapshot binary alongside single-track plugin

The plugin itself is single-track, but a separate binary-distribution release tag (e.g., `snapshot`) is force-recreated on every push to main as a prerelease. Used by a binary-download wrapper as a fallback URL — not a marketplace channel, a binary channel. Appropriate when the plugin ships a downloadable native artifact with a faster cadence than the plugin's semver. Constrains binary consumers caching by tag SHA against the floating tag — they see silent moves.

### Plugin-ref ↔ CLI-version coupling via SessionStart

The plugin ships a SessionStart hook that pins an external runtime tool (e.g., `npm install -g <pkg>@<plugin-version>`). The plugin-ref and the runtime tool's version are coupled at session start, not by a marketplace channel mechanism. Effectively a "channel" that lives in the hook layer rather than the marketplace.

### Tags-on-default-branch single channel with @ref pinning

No stable/latest split in the manifest; users pin via `@ref` syntax or default to GitHub's latest-release endpoint. Tags live on the default branch directly. `rc/*` branch pattern may exist for pre-merge CI validation but produces no release artifact. The `--tag <tag>` flag on a self-installer CLI is the explicit pinning mechanism.

### No channel mechanism at all

No tags, no releases, no branch pinning convention — every install pulls HEAD of the default branch. Bare-plugin `claude --plugin-dir` installs are pinned only by the consumer's checkout SHA. Version bumps in `plugin.json` may appear as hand-edits in feature commits with messages like `chore: bump for cache bust`, indicating the version is being used as a cache-invalidation lever for `/plugin update` rather than as a stable channel coordinate.

## Release cadence and tagging

How releases on main are marked and triggered — frequency, granularity, and discipline around marking specific commits as releases.

### Manual semver tagging on main

Tags `vX.Y.Z` are pushed directly on main commits — no release branches, no `-rc`/`-beta` suffixes, no dev-counter scheme. Tagging happens at the same minute as the underlying commit lands; releases are hand-cut via `gh release create` or the GitHub UI. CHANGELOG generated by tools like `git-cliff` (configured via `cliff.toml`) and invoked manually. Cadence can be rapid (multiple bugfix releases within a single day) when blocking issues are caught post-tag. Trade-off: gives consumers a pinnable surface but provides no objective gate between "tagged" and "shipped" without CI. Tag-sanity is unenforced — `package.json` or `marketplace.json` version can lag the tags indefinitely.

### Tag-on-main with manual GitHub Release

Tags `vX.Y.Z` live on the default branch; releases are not triggered by tag push but by a GitHub Release `published` event. The author runs `gh release create v<version> --generate-notes` to fire the release pipeline. Tag alone does not ship — the manual release step is load-bearing. Appropriate when release notes need human curation; constrains automation because forgetting `gh release create` silently skips the publish.

### Tag-on-main with automation triggered by tag push

Tags on the default branch with releases triggered by `push: tags: ['v*']`. Automation runs unconditionally on any matching tag.

### Hand-bumped versions on main (untagged)

The release marker is a plain commit titled `chore(plugin): bump 0.1.4 -> 0.1.5` (or the local equivalent). No automation; no pre-commit hook to derive the bump. Version drift across multiple manifest surfaces is hand-aligned via separate "align cursor plugin version to match claude plugin" commits when contributors notice. CHANGELOG may have versioned headings without git anchors. Constrains downstream pinning — there is no `git checkout vX.Y.Z` available — and creates an apparent version that disagrees with the latest tagged release.

### Untagged main (no releases)

No tags exist; no GitHub releases have been cut. The plugin's `version` field is frozen at an initial value (typically `0.1.0`) across many commits. Every install takes HEAD; there is no version-pinning surface. Conventional commit subjects substitute for a changelog. Appropriate while pre-1.0 and exploring the design space, but offers no rollback or reproducibility for downstream consumers.

### Hand-bumped version-as-cache-bust

No tags at all; `plugin.json.version` is bumped within feature commits explicitly for cache invalidation (`bump to 1.2.0 for cache bust`). The version field is operating as a refetch trigger for downstream `/plugin update` rather than as a release coordinate. Sibling plugins in the same marketplace can each have independent versions that get bumped at unrelated times.

### Upstream-aggregator chore-sync

Every commit is `chore: sync <plugin-list>` produced by an upstream pipeline outside the marketplace repo. Versions bump in the upstream plugin repos, and the aggregator imports the bumped artifacts via batched commits. Appropriate when the marketplace is a fan-in aggregator from independently-released plugin repos; constrains the aggregator to having no independent release identity — its own "version" is just the commit SHA of the latest sync.

### Pre-commit version bump absent

Across the corpus, no `.pre-commit-config.yaml`, `.husky/`, or `.github/hooks` configuration auto-bumps the version on commit. Version is hand-edited at release time. Appropriate when the release model is "tag deliberately, version manually" rather than "every commit gets a unique patch level." Implies long stretches where many commits share a single version string, with the changelog effectively being `git log` between tags.

### Skill-driven release

A project-local skill (e.g., `/dev:release` under `.claude/skills/dev-release/`) bumps versions in known manifest files, generates a `CHANGELOG.md` entry from conventional-commit-prefixed log output (`feat:`, `fix:`, `refactor:`), creates an annotated tag, runs `gh release create`, and runs `npm publish` for multi-channel plugins. Appropriate when the author wants release automation but lives entirely in-editor; constrains: the skill must be kept in sync with all version-bearing files, and any file not in its bump set silently drifts (most commonly the marketplace entry's duplicated version field).

### Per-plugin tag prefix absent

Tag format `{plugin-name}--v{version}` for marketplaces aggregating independently-versioned plugins is not observed in the corpus. When multiple plugins share a marketplace, tags (when present) are flat repo-wide semver — every plugin shares the same tag identity, or each plugin has independent untagged versions in its `plugin.json`.

## Plugin-component registration

How `plugin.json` connects to the components (skills, agents, commands, hooks, MCP servers) that ship with the plugin — explicit declaration versus directory-convention discovery.

### Default convention-based discovery

`plugin.json` declares only top-level metadata (`name`, `description`, `version`, `author`) and omits all component fields. Claude Code auto-discovers `commands/`, `agents/`, `skills/`, `hooks/hooks.json`, `monitors/monitors.json`, `bin/`, `.mcp.json`, `channels/` from convention paths. Adding or removing a component requires no manifest edit; the directory structure IS the registration. Constrains the plugin to the conventional layout but eliminates a class of manifest-drift bugs. Past tightening of Claude Code's plugin validator has caused authors to remove previously-declared "invalid auto-discovery fields" — i.e., the validator now penalizes redundant declaration of auto-discoverable components, making discovery the safer default.

### Inline configuration for non-discoverable components

`plugin.json` declares `mcpServers` inline as a configuration object (e.g., `{"<name>": {"command": "bash", "args": ["${CLAUDE_PLUGIN_ROOT}/scripts/run-mcp.sh"]}}`) rather than referencing an external `.mcp.json`. Hooks remain auto-discovered from `hooks/hooks.json`. Env block typically threads `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` so the server resolves its own runtime location. Appropriate for components like MCP servers that need explicit command/args declaration and have no canonical directory equivalent. Pitfall: env-thread paths assume the dependency-install side-channel has populated `${CLAUDE_PLUGIN_DATA}/node_modules` before MCP server startup, with no startup gate.

### Inline manifest with high-fan-out hooks

`plugin.json` inlines `mcpServers` and `hooks` (10+ event types, 17+ total registrations all matchering `*`). Skills and agents discovered by path convention. Appropriate when the plugin wants centralized declarative control. Constrains tool-call latency — every tool invocation spawns multiple hook processes.

### Hooks-json with broad event coverage

A standalone `hooks/hooks.json` registering many event types (15+ including `Notification`, `StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`) each with empty-string matchers (fire on everything). Several may not be in the canonical Claude Code event list — the plugin anticipates or relies on emerging events. Constrains the plugin to versions of Claude Code that emit those events without a declared version floor; older hosts silently get a subset.

### Directory-pointer mixed with file-pointer

`plugin.json` mixes directory pointers (`"skills": "./skills/"`) with file pointers (`"mcpServers": "./mcp/mcp.json"`) and explicit arrays (`"agents": [".../foo.md", …]`) in the same manifest, often with the mixture varying plugin-to-plugin within one marketplace. Appropriate when some component locations are conventional and others are non-default. Constrains: inconsistency within a marketplace makes it harder for tooling to predict where to look.

### Explicit paths in alternate-runtime plugin.json

When a plugin ships a Cursor variant (`.cursor-plugin/plugin.json`), that manifest sets explicit fields like `"skills": "./skills/"` and `"hooks": "./hooks/hooks-cursor.json"` — different path conventions, different hook manifest filename. Cursor's runtime apparently doesn't inherit the Claude default-discovery behavior, so its manifest is more verbose. Same `skills/` tree on disk, two manifest views over it.

### Custom sidecar manifest

Each plugin ships a non-standard `.claude-plugin/capabilities.json` alongside `plugin.json` carrying `{plugin, version, schema_version, capabilities[]}` with per-capability `id, name, type, applicable_phases, guidance, anti_patterns, priority`. Not in the official spec; consumed by the marketplace's own router/selector layer that picks which capability to invoke based on phase + priority. Capability versions drift independently from `plugin.json.version`. Appropriate when a marketplace ships its own routing/selection mechanism; constrains: the sidecar is meaningless to vanilla Claude Code clients and must be parsed by a co-shipped consumer.

### Three-channel parallel registration

Components are registered three ways in the same repo: (a) marketplace.json plugin entries for the slash-command flow (relies on directory conventions), (b) `config.json` modules for the npx flow (enumerates per-module operations explicitly: `copy_file`, `copy_dir`, `merge_dir`, `run_command`), (c) legacy Makefile targets like `deploy-bmad`. Each channel registers components differently; the npx path also merges per-module agent presets into `~/.codeagent/models.json` and tags every merged hook entry with `__module__: <name>` for surgical unmerge on uninstall.

### Skill `triggers` array with fuzzy matching

Skills declare `triggers: [phrase1, phrase2, ...]` (a custom array of 3-10 short phrases per skill) in addition to or in place of `description`. A `UserPromptSubmit` hook fuzzy-matches the prompt against triggers (typo-tolerant) and injects up to 3 matching skills' content via `additionalContext`. Distinct from Claude Code's built-in `description`-based activation; layers on top rather than replacing. Appropriate when activation precision matters and the plugin is willing to ship its own matcher. Constrains skill authors to maintain trigger arrays in addition to descriptions.

### Authored agents not registered as plugin agents

A directory like `src/agents/*.md` contains files with Claude-Code-style agent frontmatter (`name`, `description`, `defaultModel`, `readOnly`, `tools` array). They are not wired via `.claude-plugin/agents/` and there's no `agents` field in `plugin.json` — they're consumed by an internal swarm/orchestration skill rather than registered as Claude Code sub-agents. Constrains discoverability: a reader scanning by directory convention may misidentify them as plugin-registered agents.

## Component composition

Which kinds of components the plugin ships and how the mix shapes the plugin's product surface.

### Skills + hooks + bin

Multiple skills (each as `skills/<name>/SKILL.md`) plus a SessionStart hook plus a single bin entry point that the skills invoke via `Bash(<binname> *)` permission rules. No commands, no agents. The bin is the orchestrator; skills are the user-invocable surface; the hook handles environment setup. Appropriate when the workflow is dominated by command-line tooling that the agent triggers via Bash-permissioned skill invocations.

### Skills + commands + agents + hooks + bin

A multi-component plugin with skills (single-file `SKILL.md`), commands (markdown files for slash invocation), agents (sub-agent definitions with their own model/isolation/color), hooks (pre/post tool use plus session-start/pre-compact), and a thin bin wrapper. Appropriate for spec-driven-development style workflows where each phase has its own command surface, agents handle execution in worktrees, and the bin is a shared utility called from every component context. Skill files are kept single-file (no supporting files) — each skill body is its complete operational reference.

### Hooks + MCP server (no skills/commands/agents/bin)

The plugin's entire product surface is one MCP server with several tools plus two or three hook scripts. No skills, commands, or agents at all. Appropriate when the plugin is purely a context-provider (memory, retrieval, indexing) — Claude reaches its tools via MCP, not via slash commands or skill invocations, and hooks handle background ingestion and per-prompt context injection. Unusual for a marketplace plugin and worth noting: components are not all present in every plugin; the absence of a skills surface is a legitimate design.

### Skills + hooks + channel

One sample ships skills, hooks, AND an in-plugin MCP "channel" (research-preview feature) under `channels/<name>/` with its own server source and dep manifest — a fourth component class beyond the conventional skills/commands/agents/hooks/bin set.

### Skills + commands + agents + hooks + .mcp.json + monitors + bin (broadest)

Plugins exercising the broadest component palette ship all of: skills, commands, agents, hooks/hooks.json, `.mcp.json` at plugin level, `monitors.json`, and `bin/`. Cross-section surface area for a single plugin reaching the full Claude Code component matrix.

## Plugin-component placement

Where component directories physically live relative to plugin boundaries.

### Inside plugin directory

`plugins/<name>/skills/`, `plugins/<name>/hooks/`, `plugins/<name>/bin/` — components live under the plugin they belong to. Standard model; auto-discovery and `${CLAUDE_PLUGIN_ROOT}` interpolation work as designed.

### Outside plugin directory at repo root

`bin/`, `hooks/`, or other component-shaped directories live at repo root with no owning plugin. Auto-PATH registration (which depends on `bin/` inside a plugin per the plugin model) does not happen. Appropriate when the artifact serves the marketplace as a whole (a manual installer CLI, a project-setup nudge) rather than any specific plugin. Constrains: only reachable for local-clone users who add the directory to PATH themselves; plugin-installed users must fall back to absolute paths via `${CLAUDE_PLUGIN_ROOT}/scripts/...` in skill steps. The `bin/` entry at repo root is effectively dead in the plugin-install pathway.

## Cross-platform skill publishing

How skills are exposed to non-Claude agent runtimes alongside the Claude-native form.

### Per-skill Codex sibling marker

Every `skills/<name>/` directory contains a sibling `agents/openai.yaml` file declaring Codex-platform interface metadata (`interface: {display_name, short_description}`, `policy: {allow_implicit_invocation}`). Lives alongside the Claude-native `SKILL.md` so the same skill folder publishes to both platforms. Appropriate when the author wants one skill source-of-truth feeding multiple agent ecosystems; constrains: skill folder layout becomes platform-fan-out — adding a new target runtime means another sibling file in every skill dir.

### Multi-runtime install via npm bootstrap

A Node CLI (`bin/install.js`, invoked via `npx <plugin>@latest`) copies skills/agents/tools into runtime-specific directories (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.windsurf`) with an interactive prompt selecting subset. Same source ships as a Claude Code marketplace plugin AND as a multi-runtime skill bundle through npm. Appropriate when the plugin's value proposition is portable beyond Claude Code; constrains skills to cope with two filesystem layouts at runtime — plugin mode under `${CLAUDE_PLUGIN_DATA}`, npm mode under `~/.<runtime>/` — typically via env-var fallback chains in skill steps.

### Codex CLI co-distribution

Sibling directory in the same repo carries Codex-only artifacts (SKILL.md + `agents/openai.yaml`) installed via `cp -R ~/<repo>/<dir> ~/.codex/skills/` rather than `/plugin install`. Same git repo doubles as a Claude Code marketplace and a Codex skills bundle. Per-platform install instructions live in the README.

## Agent frontmatter shape

Fields used in `agents/*.md` frontmatter to describe sub-agents.

### Minimal name + description

Agents declare `name` and `description` only. No `model`, `tools`, `allowed-tools`, `disallowedTools`, `memory`, `maxTurns`, `color`, `effort`, `background`, or `isolation`. Relies on Claude Code defaults for everything else.

### Minimal `name`, `description`, `tools`

Bare-minimum agent declaration. `tools:` is a YAML list of plain tool names (`[Bash, Read, Write, Edit, Glob, Grep]`) or a comma-separated string — both forms accepted. No model selection, no turn budget, no permission-rule syntax (`Bash(uv run *)`).

### Standard fields plus `model`/`color`

`name`, `description`, `model` (selecting between `sonnet`/`opus` per agent role), `color`. The `description` field embeds XML-ish `<example>` blocks inline in YAML strings — readable but assumes the platform doesn't strip or parse them. Agents inherit default tool access; no `tools` field. Appropriate when different agents have different cost/capability budgets (cheap sonnet for execution, expensive opus for review) and agents can use whatever tools the harness allows.

### Extended (`model`, `effort`, `maxTurns`, `disallowedTools`)

Adds model selection (`model: sonnet`), effort budget (`effort: high`), turn cap (`maxTurns: 60`), and a denylist (`disallowedTools:`). The denylist appears in two distinct shapes:

- **Subtractive** — agent omits `tools:` (inheriting harness defaults) and uses `disallowedTools:` to subtract a few specific tools. Compact when the agent should mostly behave like a default agent minus a few capabilities.
- **Belt-and-suspenders** — agent declares both an explicit `tools:` allowlist AND a `disallowedTools:` block, redundantly naming forbidden tools. Suggests authors do not uniformly trust `tools:` as a hard allowlist, or are defensively coding against ecosystem-wide enforcement-semantics ambiguity.

The plain MCP tool id form (`mcp__<server>__<tool>`) appears alongside core tool names in both `tools:` and `disallowedTools:`.

### Tool-restricted with orchestration knobs

Frontmatter includes `tools` (allowed) and optionally `disallowedTools` listing tool names like `Read, Glob, Grep, Bash` and `Write, Edit, NotebookEdit`. Plus orchestration knobs: `memory: project`, `model: inherit`, `maxTurns: <int>`. Three syntactic variants of the tools list observed across one repo: comma-delimited string (`Read, Glob, Grep, Bash`), bare comma list, and YAML array (`["Read", "Bash"]`) — inconsistency within sibling agents indicates no enforced schema.

### Effort-tier model selection

Frontmatter declares `model: sonnet` (specific model name, not `inherit`) plus `effort: medium` and `maxTurns: 30`. Pins compute envelope per agent rather than inheriting from the session.

### `isolation: worktree`

A non-standard frontmatter field declaring that the agent should run in an isolated worktree. Assumes Claude Code's worktree isolation feature; if a client doesn't support it, parallel execution silently becomes serial. Appropriate when parallel execution of multiple instances of the same agent is fundamental to the workflow (e.g., spec-driven dev with parallel task execution).

## Skill frontmatter shape

Fields used in `skills/*/SKILL.md` frontmatter beyond `name`/`description`.

### `allowed-tools` with permission-rule syntax

Skill frontmatter carries `allowed-tools` using Claude Code's permission-rule syntax (`Bash(<cmd> <args> *)` form), explicitly enumerating safe read-only invocations and deliberately omitting write-side commands so they trigger permission prompts. Frontmatter also carries `name`, `description`, `user-invocable`, `argument-hint`. Appropriate when the plugin wants tool-level allowlisting without per-tool hooks.

### `allowed-tools` with plain tool names

Skill frontmatter carries `allowed-tools: Bash` (no permission-rule brackets). Looser than the permission-rule form; relies on user-level permission gates rather than skill-declared per-command allowlists. Appropriate when the skill intends to be broadly capable and tool gating is owned elsewhere.

### `allowed-tools` as YAML array

Skills declare `allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion]` as a YAML array (vs. comma-separated scalar). The token `Agent` is the legacy name for the Task tool used to launch sub-agents. Constrains nothing — purely stylistic — but observed consistently across one plugin's skills, suggesting authoring convention.

### Non-standard `user-invocable: true`

Every `SKILL.md` declares `user-invocable: true`. The Claude Code plugins reference does not document this field — either author-invented (and ignored at runtime) or an undocumented behavior. If ignored, it is dead metadata; if respected, it is an undocumented dependency. Worth flagging as an "uncommon frontmatter field observed in the wild" data point.

## Dependency installation

How runtime dependencies (Python packages, Node modules, native binaries, system tools) reach the user's machine on first use and on update — runtime ecosystem, manifest format, install location, change detection, install trigger, and failure recovery.

### No managed install — pure shell/markdown plugin

The plugin assumes a baseline of system tools (`bash`, `jq`, `git`, `python3`) on `$PATH` and detects everything else at runtime via `command -v`. No install hook, no manifest, no cache directory. Constrains the plugin to be lightweight and pushes responsibility for tool installation onto the user. Failure mode: silent degradation when a missing tool is reached at runtime — a hook depending on `jq` simply behaves differently when `jq` is absent because there's no install path to fail.

### Stdlib only

Plugin code uses only language-stdlib + system tools (Python 3 stdlib, bash, git). No `requirements.txt`, no `pyproject.toml`, no `package.json` `dependencies`. Runtime prerequisites are documented in README (`Python 3.6+`, `Bash`, `Git`) but not validated at session start. Constrains: silent failures if a stdlib feature exceeds the documented floor.

### Zero-dep system-tool stance (bash + jq only)

The plugin requires only bash (4+) and `jq` (1.6+), both expected to be present on the user's system. No SessionStart-installed venv, no Python packages, no npm packages, no binary downloads. Appropriate for plugins whose business logic fits in shell. Trade-off: avoids the entire dep-install surface and its failure modes, but constrains the tools the author can use. System-tool requirements (bash 4+, jq 1.6+) are stated in README only — there is no runtime probe checking versions before use, so older platforms with bash 3.2 by default produce cryptic failure modes.

### SessionStart hook → npm install local to plugin

A SessionStart hook runs an `install-deps.sh` script (or `npm install --production`) that populates `node_modules/` either inline in the install script's hard-coded list or driven by a committed `package.json`. The package list may be hard-coded inline (no committed manifest, just `npm install <pkg> <pkg>` in the script) or driven by a `package.json` that may or may not also commit a lockfile. Where no `package.json` ships, the install script generates a minimal `{"private":true}` `package.json` at install time so npm has a valid project to operate on. Idempotency is gated by various detection mechanisms (sentinel + version file, sha256 hash, `diff -q`, ABI marker — see change-detection sub-paths below). Failure path explicitly removes the sentinel and version files so the next session re-attempts install. Script is `set +e` with `|| exit 0` fallthrough on every failure, with the explicit comment `MUST NEVER exit non-zero — that blocks sessions`.

### SessionStart hook → npm install pinned to plugin version (global)

The SessionStart hook runs `npm install -g <pkg>@<plugin-version>`, where `<plugin-version>` is grep-extracted from `plugin.json`. Installs into the user's npm prefix (global), not the plugin directory. Opt-out via env var (e.g., `<TOOL>_NO_AUTO_INSTALL=1`). The plugin "installs its own peer CLI" as a side effect of session startup. Pin is exact (`@<version>`) — fully deterministic per session. Constraints: requires `npm` on PATH (fail-open with stderr warning otherwise); writes to a global location outside `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`, mutating the user's system state; matcher set to `*` means version check fires on `clear` and `compact` too; 120-second hook timeout may be tight for cold installs on slow networks; opt-out env var is undiscoverable unless the user reads the hook source.

### SessionStart hook → npm install inside `${CLAUDE_PLUGIN_ROOT}`

The SessionStart hook runs `npm install` inside `${CLAUDE_PLUGIN_ROOT}/<server-dir>/`, populating `node_modules/` adjacent to the importing JS files. Driven by a hash sentinel (`sha256` of `package.json`, persisted to `.package-hash` next to `node_modules/`); reinstall fires when hash differs OR `node_modules/` is missing. Fallback hash chain handles missing `sha256sum` / `shasum` / last-resort `wc -c` byte count. The install location choice is load-bearing — ESM `import` resolution walks the filesystem from the importer's location looking for `node_modules`, and `NODE_PATH` is CJS-only (silently ignored by ESM). So `${CLAUDE_PLUGIN_DATA}/node_modules` would break every `import`. Documenting this rationale inline in the install script (rather than in a separate planning doc) gives any developer reading the hook the "why" without external references.

### Plugin data dir with symlink-out

Install into `${CLAUDE_PLUGIN_DATA}/<deps>` (writable user data dir) then `ln -sfn $PLUGIN_DATA/node_modules $PLUGIN_ROOT/node_modules` so ESM `import` from plugin source resolves without `NODE_PATH` hacks. Inverse of "install into plugin root"; relies on the plugin root being a managed/read-only space. Constrains nothing for the consumer; the plugin author must remember to keep the symlink fresh on every reinstall.

### Per-user venv with project-mode + npx-mode forks

Plugin mode uses `${CLAUDE_PLUGIN_DATA}/venv`; npx-bootstrap mode uses `~/.<plugin-name>/venv`. Skills resolve `$<PLUGIN>_PY` env var with shell-default fallback to the npx path. Appropriate for multi-runtime plugins. Constrains: a user who installs both ways ends up with two venvs — skill invocations are non-deterministic about which one runs unless skills always read `$<PLUGIN>_PY` first.

### In-tree vendored node_modules

`node_modules/` (or pnpm `.pnpm/`) committed directly into the plugin tree. No install step at runtime; deps load straight from the committed copy. Appropriate when the plugin author wants zero-install determinism. Constrains: platform-specific binaries (e.g., `@esbuild/linux-x64`) inside the vendored tree lock users to whatever OS/arch was committed — Windows or Darwin users get a broken install with no automatic recovery.

### Inline-deps-per-script (PEP 723)

Every Python file (bin dispatchers, skill scripts, hooks, monitors) starts with `#!/usr/bin/env -S uv run --script` plus a `# /// script` block declaring `requires-python` and exact-version deps (e.g. `httpx==0.27.2`). No `requirements.txt`, no `pyproject.toml`, no `__init__.py`. Each script invocation creates or reuses uv's cached ephemeral env keyed by the inline-dep hash. Trade-off: cold-start cost on every subcommand because subprocess-dispatch from a bin wrapper to a skill script materializes a fresh env, but no plugin-managed venv to maintain or invalidate.

### Classical `python3 -m venv` + `pip install`

`python3 -m venv` creates a venv at `${CLAUDE_PLUGIN_DATA}/venv` (or `.venv`), then `pip install` is run against the plugin source. Some variants pass `--force-reinstall` to guarantee a clean state on every change-detection trigger; others rely on pip's incremental semantics. No `uv`, no `uvx`. Appropriate when the plugin's authors prefer the standard library's bundled tooling over an extra system-tool dependency on `uv`. Trade-off: brute-force reinstall is correct but slow; incremental pip is faster but harder to reason about for cache-coherence.

### Python uv preferred, pip fallback

Hook detects `uv` and uses it for venv creation + install (`uv venv`, `uv pip install`); falls back to stdlib `python -m venv` + `pip install` if `uv` is absent. The package manager preference is encoded in the script's branching, not in any manifest. Appropriate when the plugin needs Python tooling and wants the speed of `uv` when available without making it a hard dependency. Both paths produce a venv at the same location.

### Mixed Python + Node install

Two parallel dep stories coexist: Python via PEP 723 inline metadata (every `.py` script declares its own deps) and Node for an MCP-channel server (installed via a SessionStart hook gated by `diff -q`). The Node side prefers `bun` and falls back to `npm`, runtime-probed via `command -v`. Persistence retry-invariant uses stamp-on-success rather than the docs-example rm-on-failure: the cached `package.json` is only copied AFTER `node_modules` is verified present.

### Node modules self-heal at every MCP launch

A bin-wrapper invoked by Claude Code as the MCP server entry detects missing `node_modules` (gitignored, lost after marketplace `autoUpdate`) and runs `bun install --frozen-lockfile` inline before delegating. Lazy `require('cross-spawn')` after install completes lets the bootstrap survive starting from empty. No SessionStart-registered install step; every MCP launch self-heals. Appropriate when the plugin can't rely on SessionStart firing before the MCP client connects. Constrains the runtime: Bun (or Node) must be on user PATH; the wrapper has no graceful-degradation path if it isn't.

### Native binary downloaded on first use with version-stamp idempotency

A SessionStart hook (or lazy bin-wrapper, or both) downloads a pre-built native binary from a GitHub release into `${CLAUDE_PLUGIN_DATA}/bin/<name>`. Change detection via a sibling `<binary>.version` stamp file written *only after* successful extraction (`tar xzf` then `chmod +x` then `xattr -d com.apple.quarantine` then write stamp). A failed download leaves no stamp; the next invocation re-attempts cleanly without explicit `rm`-on-failure. Version compared against `plugin.json`'s `version` (read with `jq -r`). Appropriate when the binary is a separately-cross-compiled artifact too large to vendor in git. Constraint: the asset URL pattern is hardcoded in the shim; release-workflow asset-name changes must be coordinated.

### Native binary with versioned-then-floating download URLs

Wrapper attempts a versioned URL (`releases/download/v<plugin-version>/<binary>`) first, then falls back to `releases/latest/download/<binary>`. Mitigates a race where the marketplace pulls the new plugin version before the release workflow has finished uploading binary artifacts. `releases/latest/...` is the floating-tag fallback, paired with a separately-maintained `snapshot` prerelease tag for dev builds. Constraint: dev/release version distinction is encoded in version-string suffix matching (e.g., `version.includes("-dev.")`) — three-state logic (release/dev/unknown) inside the wrapper.

### Cargo/Homebrew user install with plugin-managed cache fallback

The plugin's bin shim tries the user's own install first (`cargo install <pkg> --locked` or `brew install <tap>/<pkg>`), then a plugin-managed binary at `${CLAUDE_PLUGIN_DATA}/bin/<name>`, then downloads from GitHub releases as a last resort. PATH-cleaning via `grep -vFx "$self_dir"` on PATH entries prevents the shim from finding itself. User's install is authoritative even if it's a different version than `plugin.json` declares — deliberate trade for ergonomics. Appropriate when the upstream binary is published to multiple package managers and users routinely install it that way.

### Browser-bundle install alongside node_modules

Browser-capture plugins place `node_modules` plus a Chromium download (~170 MB) under `${CLAUDE_PLUGIN_DATA}` via `PLAYWRIGHT_BROWSERS_PATH=<data>`. One-time download skipped on subsequent sessions when the staleness check passes. Verifies by launching a headless instance and closing it before declaring success — catches broken downloads that pure file-existence would miss.

### Pre-plugin-era installer outside plugin tree

Pre-plugin-era installer writes its bin directory to `~/.claude/bin/` regardless of which plugin invoked the install, plus appends that path to user shell rc files via auto-detection (`bashrc`, `zshrc`). Cuts against the plugin-era convention of containing artifacts under `${CLAUDE_PLUGIN_ROOT}` and lets the binary outlive plugin uninstall. Visible as an artifact of installers that predate the plugin model.

### Hard-coded versions in install script

`scripts/setup.sh` downloads or compiles binaries with versions hardcoded in the script itself (`HELLWAL_VERSION="1.0.7"`). No declarative manifest, no update mechanism — users get whatever was pinned at the commit time of the setup script. Hooks reference `${CLAUDE_PLUGIN_ROOT}/bin/<binary>` directly (no PATH discovery). Linux/x86_64 hardcoded — porting to other platforms requires script edits.

### Persistence contract — `${CLAUDE_PLUGIN_DATA}` as install destination

Across managed-install plugins, `${CLAUDE_PLUGIN_DATA}` is the install target — `node_modules/`, version stamps, sentinels, and any persistent cache live here. `${CLAUDE_PLUGIN_ROOT}` is treated as cache (wiped on plugin update) and not used for state. Contributor docs warn explicitly against the inversion: "Using `${CLAUDE_PLUGIN_ROOT}` for persistent state — WRONG, it's the cache dir that gets wiped on plugin update."

### Source-content hash via cross-platform md5

Concatenate dep manifest plus glob of source files; pipe through `md5 -q` (BSD) → `md5sum | cut` (GNU) → literal `"none"` fallback. Stored in the venv directory; compared each session. Recomputes deterministically across edits to any included file. Constraint: the `"none"` fallback can pin install state on a minimal system. The marker is interpreter-version-blind — a system Python upgrade isn't detected.

### Hash over source plus manifest (sha256)

A sha256 hash is computed over the plugin's Python source files, manifest, and (sometimes) markdown — the union representing "anything that would change what `pip install .` produces". The hash is stored in `${CLAUDE_PLUGIN_DATA}/.deps-hash` and compared on every SessionStart. Mismatch triggers `--force-reinstall`. Appropriate when the plugin installs itself from source via `pip install .` — the installed package is not just the manifest, so manifest-only hashing misses source changes. Trade-off: editing README invalidates the hash and forces a venv reinstall (over-eager invalidation). Hash is computed via `find ... | sort | xargs cat | shasum -a 256` to stabilize across filesystems with non-deterministic `find` ordering.

### sha256 of manifest + post-verify marker

Hash of the bundled `package.json` is compared against a hash of the cached copy in `${CLAUDE_PLUGIN_DATA}`. AND an `.install-ok` marker file must exist; the marker is deleted before install starts and only rewritten after a verification step (e.g. headless browser launch) succeeds. Marker JSON also records `{version, hash, timestamp, node, platform}` for forensics. A partial install (manifest copied but install crashed) leaves the cached manifest matching but the marker missing — next session retries cleanly.

### Three-pronged OR (path drift + manifest diff + venv health)

Three independent checks evaluated with `elif` short-circuit: (a) cached `${CLAUDE_PLUGIN_ROOT}` path file content differs from current value (detects plugin-cache directory move on Claude Code update), (b) `diff -q` against a cached copy of `pyproject.toml` (detects manifest change), (c) `${VENV_DIR}/bin/python` is missing or non-executable (detects broken venv). Any one trigger forces reinstall. Appropriate when plugin-directory relocation is a real failure mode. Trade-off: install reason isn't logged because the flag is set without echoing which trigger fired; cached files are written only after pip success, so a failed install leaves stale cache content and the next session naturally retries via the manifest-diff trigger.

### Manifest diff (`diff -q`)

Hook caches the source `package.json` (or equivalent) into `${CLAUDE_PLUGIN_DATA}` and compares each session via `diff -q "$src" "$cached"`. Mismatch triggers reinstall and updates the cache. Appropriate when reinstall is cheap relative to importing or compiling. Constrains: works only for diffable manifests; misses semantic equivalence (e.g., reordered keys produce a false-positive reinstall).

### Byte-for-byte content equality on manifest

Reads `${CLAUDE_PLUGIN_ROOT}/package.json` and `${CLAUDE_PLUGIN_DATA}/package.json` and compares full string contents. No hash, no mtime, no version-only check. Pitfall: copy-then-install ordering is asymmetric — the manifest is copied to the data dir BEFORE `npm install` runs there, so a failed install leaves a "fresh" copy that makes the next equality check pass and masks the failure.

### Existence-only

Hook checks `[ ! -f "$VENV_PY" ]` and only creates the venv if missing; checks `python -c "import <pkg>"` and only installs if the import fails, OR `[ ! -x "${BIN_DIR}/<binary>" ]` gates install. No version check, no manifest hash, no diff. Appropriate for tiny stable dep sets. Constrains: misses upgrades — if the plugin later requires a higher version, the existence check passes silently and the new requirement surfaces as a runtime ImportError or AttributeError far from the install hook.

### Existence-plus-version-compare

Existence of `node_modules` directory or `bin/<name>` binary plus `<binary> version` output parsed with regex and SemVer-compared (`versionGte`). No content hashing. Cheaper than a hash but blind to manifest edits that don't bump the binary's reported version; relies on the binary's version string being reliable.

### Version-stamp file written after success

`<binary>.version` text file containing the version string, written *only after* successful extraction or install. Compared against `plugin.json`'s `version` via `jq -r '.version'`. Failure leaves no stamp → next run retries cleanly. Compare/contrast with marker-written-before-extraction approaches that need explicit `rm`-on-failure recovery.

### ABI marker for native modules

Beyond manifest-diff, a separate `.node-abi` marker file holds Node's `process.versions.modules` integer. On every SessionStart the current ABI is compared against the marker; mismatch triggers `npm rebuild <native-modules-explicit-list>` (only enumerated native modules, not the whole tree). Two orthogonal change axes: package.json drift drives full reinstall, ABI drift drives native-only rebuild. Constraint: rebuild list is hard-coded — adding a new native dep requires editing the shell script.

### Runtime-probe fallback

In addition to marker-based detection, the runtime hook actually invokes the native module (`require("better-sqlite3")` in a child process) and pattern-matches `/NODE_MODULE_VERSION|was compiled against a different/` on the error to trigger inline rebuild. Belt-and-suspenders against stale or corrupted markers.

### Three-gate idempotency

A SessionStart dep-install script checks `sentinel file existence` AND `dest version file existence` AND `diff -q version file match` before skipping. Each gate catches a different corruption mode (aborted install, partial file write, upstream version bump). Stricter than any single gate and resilient under partial-state recovery.

### No change detection

Marketplace entry `version` is bumped manually as a cache-bust signal so consumer `/plugin update` refetches the whole plugin tree. The "change detection" lives in the marketplace consumer, not in the plugin itself — there's no install-time hook that compares manifests or hashes.

### SessionStart direct invocation

Plugin registers a `SessionStart` hook that runs the installer script synchronously (or via `child_process.spawn`) on every session start, with the change-detection layer short-circuiting fast on no-op. Timeout budget (e.g. `"timeout": 300`) bounds the worst-case install. Pitfall: aggregate internal timeouts of the install pipeline (npm + browser download) can exceed the hook timeout on cold first-run.

### Sanity-check-gated indirect invocation

`SessionStart` hook calls a generic sanity-check function (`runSanityCheck({ fix: true })`) that owns ~17 invariants of which deps are two; the sanity routine spawns the install detached + unref'd when its `node_modules`/manifest checks fail. Same code path is reachable via a manual `/sanity` skill invocation. Decouples "install dependency" from "this plugin starts up" by treating it as just another self-healing invariant. Pitfall: detached fire-and-forget means the hook returns before install finishes; MCP server startup races against `node_modules` materialization.

### User-invoked one-shot installer

Install is not a hook at all — user runs `npx github:<owner>/<repo>` or `bash setup.sh` manually. The installer is a CLI app that handles tarball download, interactive multiselect, copy operations, and merging into `~/.claude/settings.json`. Plugin install via `/plugin marketplace add` is the secondary channel that gets a smaller subset.

### Skill preamble lazy build

Skill preamble (the bash block at the top of a SKILL.md) runs an `update-check.js` and a `build.js` lazily on first skill use, separate from any hook. Defers heavy work (esbuild bundling) from session start to skill activation. Pitfall: the lazy builder mutates `package.json` in the data dir to add esbuild, which then defeats the sha256 staleness check the SessionStart installer relies on — observed bug from the interaction of two install paths managing the same manifest.

### Self-healing via marker cleanup

On any failure branch the script `rm -f` the cached manifest and ABI marker, then `exit 0`. Next SessionStart sees no cached state and retries from scratch. Constrains the script to never persist partial state — every write must be paired with cleanup-on-failure.

### Implicit retry via late-write cache marker

`set -euo pipefail` halts on any failing command. No explicit `rm` of partial state. The change-detection cache (hash file or cached manifest copy) is written only after pip install succeeds, so a failure leaves the old cache content intact — the next session's change-detection check naturally re-fires the install branch. This amounts to retry without explicit cleanup. Trade-off: a partially-created venv may persist on disk; if the venv's `python` binary happens to be present, the venv-existence trigger short-circuits past the actual broken state, which is why manifest/hash drift triggers are critical to the recovery story.

### Pre-delete the marker so failure is structurally visible

`.install-ok` marker is deleted before any install work begins and only rewritten after end-to-end verification (e.g. headless browser launch) succeeds. A crashed install leaves the cached manifest in place but the marker absent; the next-session check sees marker missing and retries from a clean state. The failure branch in the outer try/catch also wipes the cached manifest for redundant safety. Strongest atomicity posture observed.

### Multi-layer fail-open with stderr advisory

Installer writes human-readable `[plugin-name] <message>` lines to stderr with corrective install commands ("install build-essential" / "install Visual Studio Build Tools"). Top-level catch swallows errors so session start never fails. Hook output is a JSON `hookSpecificOutput.additionalContext` warning prefixed with a glyph (`⚠`) that tells the user to run `/sanity` or similar. No `continue: false`, no exit-2 — the model gets degraded context but the session lives.

### Set -e bash with stderr exit-1

Bash installer uses `set -euo pipefail`; first failed step terminates with stderr message and exit 1. Caller (Node CLI) rejects its install promise with `install script failed (exit ${code})`. Top-level `.catch` writes `ERROR: <msg>` to stderr and `process.exit(1)` — user-facing CLI output, not hook JSON.

### Silent fail-through

Every install invocation is `>/dev/null 2>&1` and ends with `|| true`. Failures are invisible in the hook; the dep-consuming skill or tool surfaces the failure later via ImportError. Appropriate when the install-hook author would rather skill-level errors carry the diagnostic; constrains: users see a confusing downstream error with no signal pointing at the install hook as the actual failure site.

### No retry path

Install runs once; on failure the venv may exist with a half-installed package set, and the existence-only change detector skips the reinstall on subsequent sessions. Recovery only via manual venv removal. Constrains the install logic to be all-or-nothing within a single hook execution.

### Mkdir-based atomic install lock

`bin/.<name>-download.lock/pid` directory created via `mkdir` for atomicity (mkdir is atomic on POSIX); 60-second timeout with forced-remove fallback for stale locks from crashed processes. Used to serialize concurrent install attempts (SessionStart hook + bin-wrapper both calling the downloader). Constraint: a fast SessionStart after a crash blocks up to a minute before forcing the lock.

## Bin-wrapped CLI distribution

How the plugin uses `bin/` and what role its contents play — user-facing CLI, discovery utility, MCP launcher, or self-healing wrapper.

### User-facing CLI dispatcher

`bin/<name>` files are user-invokable command-line tools the plugin distributes onto the user's PATH (Claude Code adds each plugin's `bin/` to PATH at activation). Dispatchers route subcommands to skill scripts via subprocess. Shebang convention varies (PEP 723 `#!/usr/bin/env -S uv run --script` for Python dispatchers; `#!/usr/bin/env bash`; `#!/usr/bin/env bun`/`node`). Runtime resolution uses `${CLAUDE_PLUGIN_ROOT}` with a `Path(__file__).resolve().parent.parent` fallback — works in hook contexts where the env var is populated AND in interactive contexts where it isn't.

### Discovery utility — bin as context bridge

A 5-line bash script that prints the plugin's root directory. Not a user CLI; skills invoke it (e.g. `<plugin>-plugin-root 2>/dev/null`) to locate the plugin tree when `$CLAUDE_PLUGIN_ROOT` is unavailable. The pattern exists because Claude Code populates `$CLAUDE_PLUGIN_ROOT` only in hook contexts, not in skill or agent contexts. Skill preambles use a triple-fallback chain — env var if set, bin-wrapper output, or a hard-coded install path for cross-runtime portability. Distinct role from user-CLI bin: this is bin-as-discovery, not bin-as-tool. Constrains the rest of the plugin to assume `bin/` is on PATH.

### Multi-script bash CLI with `${CLAUDE_PLUGIN_ROOT}` resolution

Multiple bash scripts under `bin/` (e.g., `<tool>`, `init-experiment.sh`, `run-experiment.sh`, `dashboard.sh`, `setup-permissions.sh`, `statusline.sh`). Uniform `#!/usr/bin/env bash` shebang. Each script computes `<TOOL>_HOME="${CLAUDE_PLUGIN_ROOT:-${<TOOL>_HOME:-$(dirname "$SCRIPT_DIR")}}"` so the scripts work under plugin install, manual clone, or ad-hoc invocation. Sources a shared library (`lib/state.sh`) for state operations. POSIX-only (no `.cmd`/`.ps1` pair); macOS-aware (e.g., warns "no `grep -P`; use `sed`/`awk`/`python3 -c`").

### Single bash wrapper exec'ing a Node bundle

`bin/<tool>` is a thin bash wrapper that resolves `PLUGIN_ROOT` from the script location and `exec node "$PLUGIN_ROOT/dist/index.js" "$@"`. Script-relative resolution only — does NOT consult `${CLAUDE_PLUGIN_ROOT}`. Fails if `dist/` isn't shipped (e.g., when `.gitignore` excludes the build output and no `prepare`/`postinstall` builds it at install time). When the bundle isn't present, downstream consumers fall through to a different CLI resolution path (e.g., the SessionStart-installed global `<tool>` on PATH), making the in-repo wrapper effectively dead code despite its comment claiming "works without global npm install" — wrapper-as-aspirational-contract rather than wrapper-as-runtime.

### Plugin-bin + npm-bin dual-target

`package.json` declares `"bin": {"<tool>": "./bin/<tool>"}` so `npm install -g <tool>` or `npx <tool>` exposes the same CLI the plugin install does. Dual-target distribution lets users drive the tool without installing Claude Code plugins at all. Adds `engines.node >= <N>` to `package.json` even if the core plugin code is bash/Python — Node is only needed for the npm consumption path.

### npm bin entry without shipped binary (dead)

`package.json` declares `"bin": {"<name>": "./<path>.js"}` for npm `npx` distribution. Inside Claude Code the JS is invoked via `node "${CLAUDE_PLUGIN_ROOT}/dist/cli/index.js"` from `mcp.json` args rather than through the bin entry. Sometimes the bin path is dead — `package.json` references `./src/cli.js` but `src/` doesn't exist in the committed tree, leaving npm metadata pointing at vapor.

### TypeScript bun-shebang launcher with download fallback

`bin/<name>-wrapper.ts` carrying `#!/usr/bin/env bun`. Self-heals `node_modules`, verifies the native binary exists at `bin/<name>[.exe]`, downloads/version-checks via a sibling downloader module, forwards argv to the binary via `spawnSync` with `stdio: "inherit"`. Cross-platform `.exe` suffix branching, GOOS/GOARCH-specific binary naming. Plugin-root resolution precedence: custom env var > `CLAUDE_PLUGIN_ROOT` > `realpathSync`-based script-dir fallback for symlink-via-`node_modules/.bin/` installs. Bun-specific calls (`Bun.sleepSync`) bind the wrapper to Bun even though the downloader supports Node.

### Bash three-tier resolution shim

`bin/<name>` carrying `#!/usr/bin/env bash`, mode 100755, three resolution tiers: (1) PATH cleaned of `self_dir` then `command -v <name>` — exec user's install if found; (2) plugin-managed cache at `${CLAUDE_PLUGIN_DATA}/bin/<name>` with version-stamp match — exec if version aligns; (3) lazy download from GitHub release — curl + tar xzf + chmod +x + macOS quarantine strip + exec. Appropriate when the upstream binary is a distinct user-installable product. Constraint: PATH-cleaning is fixed-string match; trailing slash or case differences in PATH entries would not be stripped.

### Plugin-root resolution with custom env-var precedence

Wrapper reads a plugin-specific env var (e.g., `AIDE_PLUGIN_ROOT`) before `CLAUDE_PLUGIN_ROOT`, then falls back to `realpathSync`-canonicalized script-dir. Custom-var-first rationale: the same wrapper ships to multiple AI-coding-assistant ecosystems (Claude Code, OpenCode, Codex CLI), and `CLAUDE_PLUGIN_ROOT` is treated as a Claude-Code-specific fallback rather than the primary.

### Script-relative shell wrapper

`bin/<name>` is a short bash script that resolves `PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"` and execs the actual binary (typically Python). No `${CLAUDE_PLUGIN_ROOT}` env var check, no fallback cascade — strictly script-relative, always. Works because Claude Code's cache preserves the repo's internal directory layout. Pairs naturally with a PreToolUse hook that hard-blocks any regression to the env-var-based pattern. Wrapper itself is ~6 lines with `set -u` only (deliberately omitting `-eo pipefail` so trailing args aren't lost before the terminal `exec`). Constrains: assumes the bin and its target library remain in fixed relative positions; refactoring layout requires updating the wrapper.

### Daemon launcher (no bin-wrapper)

No `bin/` directory. The plugin entry point is reached via `"$VENV_DIR/bin/python" -m <pkg>` directly from the SessionStart hook, spawned with `nohup ... &` so the daemon detaches. Lifecycle managed via `/tmp/`-based socket/PID/refcount files. Users wanting to inspect or restart the daemon do so via tail-the-log + kill-the-PID, not a CLI.

### Node-only with mcp.json invocation

Plugin runtime is JavaScript; the binary is invoked via `node "${CLAUDE_PLUGIN_ROOT}/dist/cli/index.js" mcp` directly from the MCP server config or hook commands. No bash wrapper, no executable bit needed. Appropriate when plugin is pure Node and target platforms include Windows where bash wrappers fail. Constrains hooks that need shell features to live in separate `.sh` files invoked by `bash "$CLAUDE_PLUGIN_ROOT/hooks/foo.sh"`.

### `${CLAUDE_PLUGIN_DATA}` with HOME fallback

The wrapper reads `${CLAUDE_PLUGIN_DATA}` to locate its venv and falls back to `$HOME/.claude/plugins/data/<plugin-name>` if the env var isn't set. Does not consult `${CLAUDE_PLUGIN_ROOT}`. Appropriate when the wrapper needs the venv (in plugin data) but not the plugin source — running the installed package, not the source. Trade-off: hard-codes a conventional fallback path; if the harness's plugin-data layout changes, the fallback breaks silently.

### `cd`-before-exec with `--file` argument rewriting

The wrapper resolves selected relative-path arguments (e.g., `--file <path>`) against `$ORIG_CWD` before `cd "$STATE_DIR"`, then `exec`s the entry point. Because the entry point is forced to a fixed working directory (state dir), any user-passed relative path that isn't pre-resolved would silently resolve against `$STATE_DIR` instead of the user's PWD. The `--file`-only rewrite is partial coverage — other relative-path flags pass through unresolved. Argument parsing uses a `next_is_file=true` flag walk over `"$@"`, which handles `--file path` form but not `--file=path` (equals-form passes through unresolved).

### Source activate then exec python

The wrapper `source`s `$VENV_DIR/bin/activate` (with `# shellcheck disable=SC1091`), then `exec python -m <module>`. Functionally correct because `source activate` mutates `$PATH` and sets `VIRTUAL_ENV`. Strictly weaker than the direct-exec form: requires the activate script to be present (some `uv`-managed venvs may omit it); is bash-only (`source` not portable to `dash`); sources ~50 lines of activate boilerplate; depends on `$PATH` order surviving any conda or other venv init in the user's shell rc.

### Direct exec of venv Python (no activate)

The wrapper does `exec "$VENV/bin/python" -m <module> "$@"` without sourcing `activate`. Avoids the entire activate-script surface, works under any minimal shell, runs identically against `uv`-managed and stripped venvs that may lack `activate` entirely. Pairs naturally with the wrapper resolving the venv via env var (e.g., `${CAIRN_VENV}`) populated in `$CLAUDE_ENV_FILE` by the SessionStart bootstrap, decoupling venv location from wrapper logic.

### Zero-dependency Node self-installer at `bin/cli.js`

Single-file Node.js CLI (~1,300 lines) using only stdlib (`https`, `zlib`, `fs`, `crypto`, `child_process`, `readline`). Hand-rolled implementations of: GitHub API client, https downloader, in-memory `tar.gz` extractor with path-safety validation, interactive `readline`-raw-mode multiselect, hook-config merger with surgical-unmerge tagging. Invoked via `npx github:<owner>/<repo>` (no npm registry publish needed). Cross-platform via `process.platform === "win32"` checks. Maintenance burden is high (TAR parsing from scratch) but supply-chain surface is zero.

### `bin/.gitkeep` placeholder populated by setup

`bin/` directory checked in with only a `.gitkeep` placeholder; `scripts/setup.sh` populates `bin/<binary>` at first run by compiling C source (`cc -Wall -Wextra -O3 hellwal.c -o bin/hellwal`) and downloading prebuilt tarballs. Linux/x86_64 hardcoded — porting to other platforms requires script edits.

### No bin directory; node-invoked scripts

No `bin/`. Scripts live under `scripts/` and are invoked as `node ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.js` from skill commands and hook entries. Shebangs (`#!/usr/bin/env node`) are present but the scripts are launched via `process.execPath` rather than the shebang, so executable mode bits don't matter. Cross-platform without `.cmd`/`.ps1` pair.

### No bin directory (plugin invokes deps via absolute path)

Some plugins ship no `bin/` at all — they invoke third-party CLIs from npm install output by absolute path under `${CLAUDE_PLUGIN_DATA}/node_modules/.bin/<name>`, exposing them as shell variables inside skill bodies. The plugin owns no PATH-level surface; everything is path-resolved at use site. Appropriate when the plugin is purely a knowledge/skill distributor.

### Shipped vs hook-populated

`bin/` contents (where present) are typically shipped as committed source. No SessionStart hook writes or mutates `bin/` files except in the `.gitkeep` placeholder pattern. Wrappers are static; their behavior changes only by editing and committing.

## User configuration

How user-tunable settings reach the plugin's runtime — manifest-declared `userConfig`, env vars, external config files.

### No userConfig

The plugin declares no `userConfig` block in `plugin.json`. All per-repo state is on-disk under repo-local directories produced by setup skills. Configuration-free shape — no secrets, no toggles, no per-user preferences exposed through the manifest. Plugins consume `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}` directly with hand-coded fallbacks. Constraint: anything that varies per user must be inferred (repo-local files, env vars, runtime detection) rather than declared.

### Typed userConfig with `sensitive` discrimination

`plugin.json` declares a `userConfig` block with one entry per field, each typed (`type: "string"`, `directory`, `boolean`), titled, described, marked `required` true/false, and flagged `sensitive: true` only for actual secrets (API keys, app passwords, access tokens, webhooks, PATs). Non-secret identifiers (handles, URLs, publication IDs, board IDs) are explicitly `sensitive: false`. No `default`, no enum-narrowing, no pattern/regex validation. The `directory` type is a typed variant beyond bare strings. The `type` and `title` fields are load-bearing — current manifest-validator schema rejects entries that omit them, breaking installs reactively until the user-config block is updated. References flow through to consumers via `${user_config.<key>}` substitution in `.mcp.json` and as `CLAUDE_PLUGIN_OPTION_<KEY>` env vars in scripts. A recurring pattern: remote MCP servers receive bearer tokens by injecting `${user_config.<key>}` into `headers.Authorization` with the key marked `sensitive: true` — substitution flows from keychain → manifest → outbound HTTP header without disk persistence.

### userConfig as typed schema with stringly-typed values

The plugin declares 15-18 `userConfig` fields per plugin (in a multi-plugin repo). Every field has `type: "string"` and a default value (`""` or a concrete string). Numeric-looking values (`MAX_ORDER_USDC: "100"`, `KELLY_FRACTION: "0.25"`) are stringly-typed and parsed downstream. No enums, no numeric or boolean types. Reference into other manifests via `${user_config.<KEY>}` substitution.

### `sensitive: true` flag absent on secret fields

Across one userConfig-using plugin, every secret-class field (private keys, API secrets, webhook secrets) lacks the `sensitive: true` flag despite descriptions explicitly labelling them "SECRET — treat like a password." Seven of seven secret fields lack the flag; the documented mechanism for routing to OS keychain storage is consistently skipped. Repeated three times across three plugins in the same repo — systematic authoring gap rather than a one-off.

### Hard-coded path as missing userConfig

In one sample the plugin's primary user-configurable surface — the path to the user's Obsidian vault — is hard-coded in the README as `~/ObsidianVault/03-Resources/` and enforced by the skill's directory walk. This is what a `userConfig` field would naturally hold; instead it's a prose convention. Demonstrates the absent-userConfig path's failure mode when a real config surface exists.

### Project-local config file (no `userConfig`)

Plugin reads configuration from a project-rooted file (e.g., `<tool>.config.json`, `.coco/config.yaml`, `.evolver.json`, `CLAUDE.md` `## Project Type` section) at runtime, bypassing the Claude Code `userConfig` surface entirely. Appropriate when the configuration describes the active session/project rather than a global user preference. Stored alongside the session's other persistence files so the whole session travels with the project. Plugin uninstall does not clean up project-level config files; users must know to remove them manually.

### Env-var opt-out without `userConfig` declaration

A single boolean opt-out (e.g., `<TOOL>_NO_AUTO_INSTALL=1`) is read from the environment by a hook script, with no corresponding `userConfig` field. Documented only in the hook source comment header. Constrains discoverability — users who want the opt-out have to read the hook to find it; a `userConfig` boolean would surface it in the plugin configuration UI.

### Out-of-band env vars (no `userConfig`)

No `userConfig` in `plugin.json`. Configuration via a documented set of env vars (`AIDE_DEBUG`, `AIDE_FORCE_INIT`, etc.) plus a few hardcoded values in the manifest's `mcpServers.env` block. Users discover the knobs only by reading the README; Claude Code's marketplace UX has no way to surface them.

### External config file owned by the binary

Configuration lives at `~/.config/<name>/config.toml`, read by the binary itself, not by the plugin surface. No `userConfig`, no `CLAUDE_PLUGIN_OPTION_*`. Appropriate when the binary is a standalone CLI with its own config conventions and the plugin is just a wrapper. Constrains the user — they configure via the binary, not via Claude Code.

### Vendor-CLI credential file

Plugin secrets (e.g., `LANGSMITH_API_KEY`) are stored in a third-party CLI's credential store (`~/.config/<vendor-cli>/credentials` or platform-specific equivalent), loaded by the SessionStart hook, and exported into `$CLAUDE_ENV_FILE`. Appropriate when the plugin wraps a vendor CLI that already manages credentials; constrains the plugin to a hard dependency on the vendor CLI's credential-file format remaining stable, and bypasses Claude Code's plugin-config UI entirely (users configure via `<vendor-cli> auth`).

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var forwarding

A SessionStart hook reads `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (the substitution channel for `userConfig` values) and re-exports them under plugin-specific names (e.g., `FLIPPER_<KEY>`). Decouples manifest-key naming from the daemon's env-var contract; either side can evolve independently. Appropriate when the plugin wires user config into a daemon or subprocess that has its own naming convention.

### Bridge `CLAUDE_PLUGIN_OPTION_<KEY>` to dotenv-style env vars via `$CLAUDE_ENV_FILE`

The SessionStart hook reads `CLAUDE_PLUGIN_OPTION_<KEY>` env vars and writes `export KEY="${CLAUDE_PLUGIN_OPTION_KEY}"` lines into `$CLAUDE_ENV_FILE`. This bridges Claude Code's plugin-option namespace to the conventional env-var names that a CLI library already expects (e.g., `CLAUDE_PLUGIN_OPTION_BLUESKY_HANDLE` → `BLUESKY_HANDLE`). Appropriate when the plugin is a wrapper over a pre-existing CLI that expects standard env-var names. Trade-off: duplicates the value into a file on disk (security depends on file mode of `$CLAUDE_ENV_FILE`); fields declared in `userConfig` but missed in the bridge block silently fail to propagate.

### Custom env-var substitution in hooks.json

Hook command strings reference a non-platform variable like `${SKILL_PATH}` that the plugin expects its own runtime to populate. If Claude Code does not populate the variable, the command dereferences an empty string and the surrounding guard (`[ -f .sparv/state.yaml ] && ${SKILL_PATH}/scripts/...`) silently no-ops — fail-open hides missing-env misconfiguration.

### Env var read by script (hidden interface)

A plugin script (not `userConfig`) reads an env var like `CLAUDE_SKILLS_DIR` to relocate behavior. Appropriate for testability hooks the plugin author wants but doesn't want to expose as user config; constrains: the env var is a hidden interface — consumers won't find it without reading source.

## Cross-hook environment plumbing

How SessionStart-provisioned state (venv paths, state directories, derived values) is made available to other hooks and runtime processes that fire later in the session.

### `$CLAUDE_ENV_FILE` append for cross-hook env vars

The bootstrap appends `export VAR=...` lines to `$CLAUDE_ENV_FILE` so that later hooks (Stop, UserPromptSubmit) and the MCP server wrapper can reference the variable without knowing `${CLAUDE_PLUGIN_DATA}` or having to re-derive the venv location. Avoids hard-coding paths in `hooks.json` command strings and decouples venv location from hook definitions. Appropriate as a general pattern when one hook provisions state that others consume. Trade-off: the file is appended to on every SessionStart sub-event (startup, clear, compact, resume) rather than truncated, so multiple `export` lines accumulate across sessions; bash semantics make later exports override earlier so it is functionally idempotent, but the file grows monotonically. If `$CLAUDE_ENV_FILE` is not set by the harness in some Claude Code versions, the env var is silently not persisted and downstream hooks fail with a "not bootstrapped" error message.

### Cross-hook coordination via flag files

A `${TMPDIR}/<name>.skip-stop.flag` file is written by one hook (`on-post-tool-use.py`) and read by a sibling hook (`on-stop.sh`) to suppress a duplicate notification when the user has already triggered one via a skill. Filesystem-flag coordination between hook scripts that would otherwise race on a shared output device. Appropriate when hooks share a serial output (display, sound, hardware) and need cheap mutual-exclusion.

## Plugin/state separation

How code (immutable, replaced by upgrades) and runtime data (mutable, must survive upgrades) are organized relative to plugin root and plugin data directories.

### `${CLAUDE_PLUGIN_ROOT}` for code, `${CLAUDE_PLUGIN_DATA}` for state

Code lives under `${CLAUDE_PLUGIN_ROOT}` — read-only, immutable, overwritten on plugin upgrade. State (content, reports, projects, venvs) lives under `${CLAUDE_PLUGIN_DATA}` — read-write, mutable, durable across upgrades. Default state is seeded from `${CLAUDE_PLUGIN_ROOT}/defaults/*.yml` on first run when the data dir is empty. Implies that the bin wrapper and any state-mutating code must locate their state directory via env var rather than path-relative to the plugin root.

### `${CLAUDE_PLUGIN_ROOT}/bin/` (cross-cutting placement)

Native binaries written into the plugin's own root directory rather than the data dir. Crosses the convention that plugin root should stay read-only — the binary disappears on plugin reinstall and must be repopulated by the setup script. Used when a setup script populates a `bin/.gitkeep` placeholder at first run.

## Tool-use enforcement

How the plugin uses Pre/PostToolUse hooks to gate, advise, or audit agent tool calls.

### No enforcement hooks

The plugin has no PreToolUse or PostToolUse hooks; `hooks/hooks.json` carries only SessionStart entries (or doesn't exist at all). Tool use is ungated. Skill-level `allowed-tools` permission rules in frontmatter may be the only gate on what the agent can call. Appropriate for plugins whose components are skills and reference docs rather than actions with side effects.

### PreToolUse Bash matcher as ask-first guardrail

Two distinct PreToolUse scripts on `Bash` matcher parse the Bash argv to identify trade-placement (or sensitive) subcommands and emit JSON `permissionDecision: ask` with a summary so the user sees the intent before approving. `deny` is reserved for hard policy violations (cancel-all without `--yes-really`, network not in allow-list); `allow` is implied by no-op exit. Failure posture is fail-open silent — exit 0 on parse failure or unknown commands. Output convention: stdout JSON with `hookSpecificOutput.permissionDecision` and `permissionDecisionReason`; no parallel stderr-human messages.

### PreToolUse Bash matcher as executable-path enforcer

A `PreToolUse` hook with `matcher: "Bash"` parses the agent's intended command and rejects invocations that diverge from a sanctioned shape. Example: validates that a `--command` flag passed to a benchmark runner resolves to a specific known-good script (`./<tool>.sh`), after stripping a fixed set of wrapper prefixes (`env`, `time`, `nice`, `nohup`, `timeout <n>`, `VAR=val`). Blocks with `exit 2` + stderr human-readable message. Self-arming — the hook only activates when its target artifact exists in the workdir AND the relevant mode is active; outside that envelope, parse failures fall through. Constraints: regex-based command parsing is best-effort; commands constructed via shell variable expansion can slip through; novel wrappers (`chrt`, `taskset`, `stdbuf`) would block legitimate invocations.

### PreToolUse as phase-scoped artifact gate

A single PreToolUse hook (no matcher, fires on all tools) enforces artifact-access rules driven by a YAML-frontmatter state file the orchestrator writes. Four rules encoded — block reads of cross-phase artifacts, block writes outside scoped directories, protect the state file from being overwritten by anything except the orchestrator. Only gates subagent calls (non-empty `agent_id`); orchestrator calls pass through. Fast-exit case-match on raw JSON fields skips the `jq` invocation when the tool isn't Read/Write/Edit. Output is `{"decision":"block","reason":"…"}` via `jq -n`; exit 0 silent on allow.

### Multi-PreToolUse fan-out with matcher `*`

Five PreToolUse hooks all matchering `*` — per-agent tool tracking, write-protection, read-only/agent-tool-access enforcement, context-window pressure, search-input augmentation. Every tool invocation spawns multiple hook processes. Appropriate when the plugin layers several orthogonal pre-call concerns. Constrains latency: hook timeouts (2-60s per hook) compound under fan-out.

### PreToolUse Edit/Write path validator

Matcher `Write|Edit` runs a bash script that reads the tool-call payload via stdin + `jq`, denies writes to a protected path glob (`~/.config/<tool>/themes/`), and exits 2 with `permissionDecision: "deny"` + a `systemMessage` telling the user where to develop instead. Fail-closed posture. Pitfall: `input=$(cat)` has no timeout, so a stalled stdin can hang up to the PreToolUse default budget.

### PreToolUse Edit/Write risk advisor

Matcher `Edit|Write` runs a check script (`check-ehrb.sh --diff --dry-run`) gated on a state file's existence (`[ -f .sparv/state.yaml ] && ...`). The `|| true` suffix makes non-zero exits fail-open — the advisor never blocks, only annotates. Used for risk-of-modification surfacing without interrupting work.

### PreToolUse on Edit/Bash for advisory injection

Plugin registers `PreToolUse` matchers on `Edit`, `Bash`, `Write`. The handler injects context (e.g., "blast radius" warning showing which symbols an edit affects, or staleness check on an index) but never blocks — `exit 0` always. Output is JSON on stdout for context injection; stderr for diagnostics. Constrains: the hook runs on the critical path of every matched tool call and budget management matters (e.g., 8-second timeout on a child node process invoked from PreToolUse means edits stall up to that budget on slow queries).

### Bash matcher as proxy for git pre-push

Plugin hooks `PreToolUse` with `matcher: "Bash"` and parses the command string for `git push` patterns to fire reminder behaviors (e.g., staleness check on a governance file). Always `exit 0` — explicitly documented as a reminder, not a block. Acknowledges that terminal pushes (outside Claude's Bash tool) are uncovered.

### Prompt-type Bash-pattern policy engine

A `PreToolUse` hook with matcher `Bash` and type `prompt` whose body is a multi-hundred-word list of blocked Bash patterns and their corrected rewrites. Claude evaluates the prompt against each proposed Bash command and returns a BLOCK or ALLOW verdict. The prompt also lists the rewrite for each blocked pattern, turning the hook into an in-context style guide that teaches the agent how to call the plugin's bin correctly. Blocks `cd && compound`, `&&`/`||` chains, `$()` in echo/printf, multiline JSON, `for` loops, piping tracker output to Python, and any non-bare invocation of the plugin's bin. Trade-off: prompt-engineering rather than deterministic code, with attendant non-determinism and per-call latency cost; duplicates much of the documentation also kept elsewhere.

### PreToolUse Bash dangerous-command blocker

`hooks.json` matcher `Bash` runs a Python script that inspects the bash command, optionally rewrites or blocks based on a denylist. Companion `inject-spec.py` on the same matcher likely rewrites the command rather than emitting `additionalContext` (placement on PreToolUse:Bash is unusual for context injection).

### PostToolUse as audit trail

A PostToolUse hook on `Bash` matcher (or `Write|Edit`) sniffs successful commands across known venues and appends to a journal — SQLite, JSONL, or plain markdown. Not validating — recording. Fail-open silent: exit 0 on parse failure, no error surfaced. Constraint: the hook fires in parallel for concurrent calls; SQLite WAL mode at the consumer-skill level mitigates contention but the hook script itself doesn't take an exclusive lock.

### PostToolUse with no matcher (universal observation)

A `PostToolUse` hook with no `matcher` field fires after every tool call (including read-only `Read`/`Grep`/`Glob`). Funnels every tool invocation into a single Python recorder that appends to a JSONL log. High-volume write path; payload truncation (e.g., 2000/4000/500 char caps per field) is a deliberate readability tradeoff. Appropriate when the hook serves as the ingest stage of an analytics pipeline.

### PostToolUse with selector matcher (targeted observation)

A `PostToolUse` hook with a regex matcher (e.g., `Write|Edit`, `mcp__<server>|WebFetch|WebSearch`) appends to a domain-specific log file. Multiple selector hooks compose alongside the universal one. Each writes to its own append-only file (`documents/activity-log.md`, `research/search-log.md`).

### PostToolUse-only for notification + observation

PostToolUse hooks matchering `*` for tool-event recording into a memory store, status-line refresh, comment-validation on edits, context-pruning. PreToolUse not used. Appropriate when the plugin observes rather than gates.

### PostToolUse Bash-matcher one-shot skill nudge

A single PostToolUse with matcher `"Bash"` checks the bash command for a word-boundary regex match (`(^|[^a-zA-Z0-9-])<name>($|[[:space:]])` to exclude substrings). On match, emits a one-shot per-session `<system-reminder>` via `hookSpecificOutput.additionalContext` pointing at a skill. Marker file at `${TMPDIR}/.<name>-skill-nudge-${session_id}` ensures one-shot. Rare pattern: most nudge hooks fire every time or use PreToolUse blocking; this is one-shot informational PostToolUse. Constraint: `$PPID` fallback when `session_id` is empty can stale-trigger across sessions.

### PostToolUse for index/state maintenance

Plugin registers `PostToolUse` on `Edit`, `Write`, `Bash` to update derived state — invalidate or rebuild a code index on file edit, capture event to an external spool on every tool invocation. Appropriate when the plugin maintains derived state that must follow filesystem reality; constrains: post-hooks run after the tool completes, so any error there has no preventive effect — only signals that the next read of the derived state may be stale.

### PostToolUse Write/Edit quality gate

A `PostToolUse` hook with matcher `Write|Edit` and type `command` runs a shell script that reads project-local config (e.g., `.coco/config.yaml`) for `lint_command` / `typecheck_command` (with `{file}` substitution) and executes them against the modified file. Optionally auto-fixes on lint failure if config opts in. Silent exit 0 if config is missing or quality commands are unset. Never blocks. Pairs with the prompt-type/command-type distinction: blocking hooks are prompt-type, non-blocking quality hooks are command-type.

### PostToolUse git-commit detector

Matcher `Bash` fires on every bash call but internally filters for `git commit` substring before doing anything. On match, shells out to `git log` / `git diff-tree` to record commit hash, subject, and affected domains to a docs file. Lower-cost alternative would be a regex-over-command-string matcher if the platform supported it; current spec matches on tool name only.

### PostToolUse output sanitizer / context-poisoning advisor

Matcher `Bash` runs a Node script that parses tool-call stdout/stderr from JSON, scans for binary-leak indicators (long base64 blobs, low-ASCII clusters, inline SVG > 500 chars), and emits `{"additionalContext": "Warning: capture output contains binary/image data. Do NOT pipe through stdout..."}`. Does not gate or truncate the output itself — instructs the model to ignore it. Conversation-hygiene mechanism, not a security boundary. Top-level try/catch + 5-second stdin timeout swallow malformed input silently (fail-open).

### PermissionRequest delegated to hardware

A `PermissionRequest` hook routes the allow/deny decision to a physical input device (Flipper Zero) via a 60-second socket round-trip. Emits `hookSpecificOutput.decision` JSON with `{behavior: "allow"}` / `{"deny"}` / `{"ask"}`. On no-bridge or timeout the hook exits 1 to fall back to Claude's native dialog. Generalizes to any "remote approval" surface. Constraint: the timeout is non-configurable; user walks away → Claude waits a full minute.

### PermissionRequest dormant in source

A `permission-handler.ts` (or similar) exists with header comment "OPT-IN: This hook is NOT registered in plugin.json by default. To enable, add a PermissionRequest entry." Present in source, absent in manifest. Constraint: a reader grepping hook registrations won't find it; only the file header reveals it.

### Documentation-asserted but unwired hooks

ARCHITECTURE.md describes a richer hook surface (`pre-commit-gate.sh`, `post-write-check.sh`, `post-test-verify.sh`) than `hooks/hooks.json` actually wires. Either future work or invoked by a non-Claude-Code mechanism. Surface-asymmetry is a research-relevant signal: docs may overstate the shipped enforcement surface.

## Hook failure posture

How hook scripts behave on error — fail-open vs fail-closed — and how the design distinguishes which posture each hook should take.

### Fail-open with always-exit-0

Every hook (`.mjs`, `.sh`, `.py`) wraps its body in try/catch (or shell `|| true`) and ends with `exit 0`. Combined patterns:

- `set -uo pipefail` (no `-e`) plus per-statement `|| echo ""` fallbacks
- Inline `bash -c '… || exit 0'` trampoline at the `hooks.json` command layer
- Python scripts with top-level `try/except` and `sys.exit(0)` on failure
- `trap 'exit 0' ERR` while preserving `set -e` semantics elsewhere
- `try { ... } catch { outputContinue(); }` with centralized helpers emitting `{"continue": true}`

Multiple layers of fail-open compose to "never block the user's session" as an explicit principle. The system can be three layers deep — trampoline + script-level + handler-level. Even Pre/PostToolUse hooks documented as "blocking" are sometimes effectively advisory. Constraints: persistent failure modes (no network, missing tool, malformed input) are silently absorbed; diagnosing a "hook isn't working" report requires reading the hook source.

### Pipefail with selective suppression

`set -euo pipefail` halts on errors early; later hook steps deliberately suppress with `|| true` or `2>/dev/null || true` so notification failures don't propagate. Final `exit 0` regardless. Mixes strict-by-default with explicit per-step graceful degradation. Appropriate for shell hooks that interact with optional hardware/services.

### Mixed by hook role (blocking prompt vs non-blocking command)

Hooks intended to block (PreToolUse/Bash) are `prompt` type — Claude evaluates and returns BLOCK/ALLOW. Hooks intended not to block (PostToolUse, PreCompact, SessionStart) are `command` type and exit 0 unconditionally with `|| true` suppression on every sub-command. Defensive `[ -f "$CONFIG_FILE" ] || exit 0` guards at the top of every non-blocking hook. Appropriate as a learned discipline — earlier `prompt`-type non-blocking hooks caused "stopped continuation" errors when their inputs were missing; command-type with explicit fail-open is the corrective.

### Fail-closed on bootstrap, silent fail-open on runtime hooks

SessionStart bootstrap uses `set -euo pipefail` and halts on any error (Python version check, venv create failure, pip install failure). Runtime hooks (Stop, UserPromptSubmit) wrap their async work in bare `except Exception: sys.exit(0)` blocks — errors during ingest or context injection never surface to the user. Appropriate when the bootstrap must establish strict preconditions but the runtime hooks are "best-effort" augmentations. Trade-off: silent failure means a misconfigured runtime hook is invisible to the user.

### Silent-on-failure SessionStart

SessionStart hook silences all install errors via `>/dev/null 2>&1` and `|| true`. No JSON `systemMessage`, no stderr message, no `stopReason`. Appropriate for hooks that should never block session start under any circumstance; constrains observability — there is no in-session signal of install failure.

### Fail-closed permission deny

Hook script outputs `{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "..."}` and exits 2 to block the offending tool call entirely. Used for invariants like "do not write to this protected path" rather than for missing deps. Stdin parsed with `jq` against the tool-call payload.

## Hook output convention

The structural shape of hook stdout — JSON envelopes, where logs go, and how output discipline is enforced.

### JSON-only stdout, no stderr-human parallel

Decisions go to stdout as JSON; no stderr-human-readable parallel pattern. Failure paths are silent — the hook script prints nothing and exits 0, leaving any user-facing readiness reporting to a separate SessionStart script.

### Three-channel discipline (structured stdout, narrative stderr, file logs)

All hooks emit `JSON.stringify({continue: true/false, ...})` to stdout. Human-readable logs go to stderr and to file logs (e.g., `.aide/_logs/*.log`). Hook-crash invariant: even on exception, stdout still emits valid JSON via centralized `outputContinue()` helpers and global `process.on('uncaughtException')` / `unhandledRejection` handlers. Constraint: any hook that writes plain text to stdout breaks the harness.

### Structured-where-it-matters, silent elsewhere

PermissionRequest hook writes structured JSON (`hookSpecificOutput.decision`); sound/notification hooks exit silently with `sys.exit(0)`; failure-path scripts write to stderr. No central emit helper; each script re-implements the socket-send-with-swallow pattern. Constraint: the inconsistency means a reader can't infer hook output shape from the file.

### jq-built JSON

Hook script uses `jq -n` to construct `{hookSpecificOutput: {hookEventName, additionalContext}}` JSON for stdout. No central emit helper; jq is the formatting library. Appropriate for shell hooks where embedding JSON construction in bash is unwieldy. Constraint: jq dependency on user PATH (typically present on macOS dev machines but not universal).

### `hookSpecificOutput.additionalContext` envelope versus bare top-level

Structured JSON output `{hookSpecificOutput: {additionalContext: "..."}}` is the documented channel for context injection. Plain stdout JSON without the envelope (top-level `{"additionalContext": ...}` only) is what some hooks actually emit. Mixed observed; envelope adoption is uneven. Constrains tooling that wants to detect "this hook injects context" — must look for both shapes. Whether the bare shape is silently accepted in current Claude Code releases is uncertain.

## Hook timeout and async philosophy

How the plugin sizes the latency budget for each hook based on what the hook does and what it blocks.

### Differentiated per-hook timeouts

`UserPromptSubmit` carries an explicit timeout (e.g., 10000 ms) because it blocks the model and must finish fast. `Stop` is `"async": true` with no timeout — fire-and-forget background work like graph ingest. `SessionStart` has no timeout because provisioning (pip install, venv build) can take minutes on first install and must not be killed. Three different postures for three different latency budgets on the same plugin. The 10-second ceiling on prompt-time context injection drives downstream design choices (graph cache to eliminate per-turn rebuild, k-limited search) — the timeout is not just a guardrail but a budget that shapes what the hook can do.

## Cross-platform Python invocation

How Python hook scripts cope with the absence of a uniform `python3` on every platform.

### Bash trampoline resolving python3 → python → py

`hooks/hooks.json` commands are wrapped in `bash -c 'PY=$(command -v python3 || command -v python || command -v py); [ -n "$PY" ] && "$PY" <script> <arg> || exit 0'`. The trampoline accommodates Windows / Git-Bash-on-Windows where `python3` may not exist but `python` or `py` does. Documented in CHANGELOG as a Windows-compatibility fix. Constraints: the trampoline shape is duplicated inline across every hook entry; any change requires repeating the edit at every site.

## Session context loading

How the plugin injects context into the session at start, on user prompts, or on compact.

### SessionStart for dependency install only (no context emit)

A single SessionStart hook runs an install script and emits no `additionalContext`. The hook's role is dep management; context loading isn't part of its responsibility. Constraint: dep-install correctness must not depend on session-start emitting context.

### SessionStart with multi-script division of labor

In a plugin that combines dep install and context emission, two separate SessionStart hooks register: the install script stays silent (its only side effect is `node_modules/`), while a sibling `session-start-env.py` prints a markdown readiness block with which env vars are set/missing, data-dir status, and channel-runtime status. Separates "make the world ready" from "tell the user what's ready."

### Layered SessionStart context with conditional inclusion

A single SessionStart script composes one `additionalContext` from up to four layers, each conditional on a file existing in the repo: a hard-coded routing policy always emitted; a curated extract from a learnings file (only entries with `**Status**: verified` frontmatter, awk-filtered on `---` record separators); a whole-file inject of a docs index; a single-line pointer to a design doc when present. Each layer adds depth on demand; absent files contribute nothing. Layer-1 routing policy hard-codes the skill catalog in bash, requiring hook updates when skills are added/renamed.

### Self-emitting schema detection for cross-runtime context

The same SessionStart script produces one of two JSON schemas based on which runtime invokes it: under Claude, `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": …}}`; under Cursor (detected via `$CURSOR_PLUGIN_ROOT`), `{"additional_context": …}`. Single script, runtime-discriminated output. Avoids duplicating the layered-composition logic across two scripts.

### XML-tag emphasis wrapping

Layer-1 routing policy is wrapped in `<EXTREMELY_IMPORTANT>...</EXTREMELY_IMPORTANT>` tags as a prompt-engineering construct emitted as session context. The wrapper is a content convention, not a hook-schema field — it goes inside `additionalContext` as raw text.

### File-backed context written at SessionStart

A SessionStart hook runs a script that scans some workspace state and writes a daily/cycle brief to a known file location (e.g., `notes/daily/<date>-brief.md`). The model does not see the brief automatically; the user opens it or a downstream skill reads it on demand. Less intrusive than `additionalContext` injection — survives token-limit pressure, inspectable, idempotent. Tradeoff: discoverability, since the prompt has no signal that fresh context just landed.

### Agent-driven resume protocol (no SessionStart)

No SessionStart hook is registered. Resume context is loaded by the agent itself per a "Session Resume Protocol" in its agent.md (reads a session-brief markdown, append-only JSONL, current state JSON, idea log). Resume only fires when the user launches the specific agent explicitly — a normal Claude Code session opened in the same directory does not auto-load.

### SessionStart additionalContext via JSON

The SessionStart hook emits stdout JSON `{"hookSpecificOutput":{"additionalContext":"..."}}` summarizing plugin state — counts of projects/posts tracked, ready-state messages, slash-command hints — computed by grepping state files cheaply on every session start, OR a built welcome message including current state, recent memories, notices. Appropriate when the plugin wants to remind the agent of in-flight state at the start of every session. Tight `timeout: 5` with `async: true` is sometimes used so the session does not block — context arrives late on slow disks rather than failing the session. Companion `PostCompact` hook re-injects the same context after compaction since `compact` is not a `SessionStart` sub-event. Trade-off: the recompute is tightly coupled to the exact state-file formats — a schema change would silently produce zero counts.

### SessionStart prints plain markdown to stdout

The hook script prints plain markdown text to stdout (which Claude Code surfaces to the agent at session start) rather than using the structured JSON `additionalContext` mechanism. Content is either a first-run nag ("plugin detected but not initialized") or the contents of a session-memory file (populated by `PreCompact`) when present. Multiple plugins competing for SessionStart output produce concatenated blocks in undefined order. Trade-off: no validation against the structured-output contract; relies on Claude Code's tolerance for non-JSON SessionStart output.

### SessionStart writing env-vars to CLAUDE_ENV_FILE

Hook does not emit prompt context; instead writes shell-format env-var exports (`EVOLVER_PY=/path/to/venv/python`) into `$CLAUDE_ENV_FILE` for downstream skill steps to consume. Appropriate when the SessionStart's job is environmental, not informational.

### User-settings session-start hook installed by a skill

A skill writes a hook script to `~/.claude/hooks/<file>.sh` and edits `~/.claude/settings.json` to register it as a global session-start hook — outside the plugin's own `hooks.json`. The hook then prints "ACTION REQUIRED" directives to stdout that Claude reads at session start. Appropriate when the author wants always-on user-level nudges across all projects; constrains: the hook persists after `/plugin uninstall` (it lives in user config, not plugin scope), runs in every project regardless of relevance, and requires a sibling "uninstall" skill to unwind.

### UserPromptSubmit fuzzy-matched skill injection

UserPromptSubmit hook fuzzy-matches the user prompt against YAML-frontmatter `triggers` arrays in `skills/**/*.md` (and per-project overrides like `.<name>/skills/**/*.md`), picks up to N matching skills, and returns their content via `hookSpecificOutput.additionalContext`. Skill discovery layered across project-local > plugin-bundled > user-home. Constraint: fuzzy-match tolerance allows unintended activation on typos.

### UserPromptSubmit additionalContext via JSON

A `UserPromptSubmit` hook queries state (e.g., reasoning graph) for content relevant to the user's prompt and emits a JSON object with `additionalContext` keying the injection. Appropriate when the plugin can produce per-prompt context (memory, retrieval, query expansion) within a tight latency budget.

### UserPromptSubmit prompt logger

`UserPromptSubmit` matcher runs a script per prompt — observed in one repo as a logger (`log-prompt.py`), not a context injector. Distinct from the SessionStart-based injection patterns.

### SessionStart for non-context work only

Hook is registered but never sets `additionalContext` — its job is dep install, daemon launch, stale-state cleanup, or binary download. The "context" purpose is decoupled from session boundary in this plugin.

### PreCompact hook for state-file eviction

A PreCompact hook scans the pre-compact transcript for an interrupt-then-unrelated-user-message pattern and archives the orchestrator's state file before compact removes the evidence. Protects against post-compact false resumption when the user cancelled mid-flow. Rarely-used hook event put to specific use.

## SessionStart matcher scope

Which session sub-events the hook fires on.

### Empty matcher (all sub-events)

`matcher: ""` or matcher absent — fires on `startup`, `resume`, `clear`, `compact` alike. Appropriate for idempotent operations cheap to repeat. Wasteful when the operation is non-trivial (e.g., running `diff -q` and `command -v` checks on every `/clear`). Side effects that are non-idempotent (e.g., appending to `$CLAUDE_ENV_FILE`) accumulate across sub-events; idempotency must be designed in or accepted as a known issue.

### Explicit subset

`matcher: "startup|resume"` or `"startup"` only — fires on the chosen session phases. Appropriate when the hook produces side effects that should not repeat on every compaction. Constrains the author to know which phases matter for their hook's purpose.

### Per-hook differentiation within one plugin

Different hooks within the same plugin use different matchers — e.g., dep-install on empty matcher (any sub-event), context-emit on `startup|resume|compact`. Constrains coordination — one plugin's "boot work" may run on different triggers than its "context emit" work, with no shared coordination point.

## Live monitoring and notifications

Whether and how the plugin ships background processes, status lines, or notification fan-out for ongoing session state.

### No monitors

The plugin declares no `monitors.json`. Notifications are not part of the plugin's surface. Where session-time watching is needed, it's done via the Claude Code Monitor tool from inside skills (not the declarative monitors mechanism), or via hooks plus MCP server `watchFile` calls (debounced internal cache invalidation).

### Polling daemons via monitors.json

A plugin ships 2-3 monitor entries in `monitors.json`, each pointing at a `.py` script that polls a venue API at a fixed cadence (15s-15min) and emits one line per event. Schema fields used: `name`, `command`, `description`, `when`. `when` is `always` across all monitors observed; no `on-skill-invoke:<skill>` variant. Each monitor is a long-lived daemon launched at session start. Coupling: monitors are venue-coupled (a venue plugin ships them; venue-agnostic shared-layer plugins ship none even when they're heavier).

### Status line as primary observability surface

Instead of a `monitors.json`, the plugin integrates with Claude Code's `statusLine` setting. A bash script (`bin/statusline.sh`) reads both the harness's session JSON on stdin and walks up to a project marker (e.g., `.git`) looking for plugin state files. Emits a single colorized line with a health glyph (●/▲/◆/⚕/✖/⏸), counters, streaks, durations, cost, context %. Auto-installed into the user's `.claude/settings.local.json` by a setup script. Composition via `--chain <prior-cmd>`: the statusline script accepts an existing statusLine command and delegates the raw session JSON to it before printing its own line, preserving prior configuration. Most plugins treat statusLine as a user-owned concern; this path claims it as a plugin surface and composes with prior values rather than replacing.

### Standalone terminal dashboard (out of plugin scope)

`bin/dashboard.sh --watch` runs as a user-invoked terminal dashboard in a separate shell. Not plugin-managed — the user starts and stops it; the plugin only writes the state files the dashboard tails.

### Hook-driven file-write status line

No `monitors.json`. A PostToolUse hook writes status to `.<name>/state/hud.txt` and a Claude Code status-line integration reads from it. A SessionStart hook installs a wrapper script (`~/.claude/bin/<name>-hud.ts`) that discovers the newest installed plugin version under `~/.claude/plugins/cache/*/` and delegates. Decouples user-facing HUD from plugin upgrades — new versions provide new HUD scripts; the wrapper always finds the newest. Constraint: side-effect on the user's home directory not declared anywhere in the plugin manifest.

### Hardware-device notification fan-out

Hook events fan out to a physical device (Flipper Zero) via a daemon socket — sounds, vibration, display text. Hook-event variety is used to discriminate notification cues at fine granularity. Includes events outside the canonical Claude Code hook list (`StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`). Constraint: events that aren't yet emitted by a given Claude Code version silently no-op; no version-floor declaration.

### Version-floor declaration absent

Where monitors are used, no plugin.json or README declares a minimum Claude Code version for the monitors feature. Repo-level docs may name a Claude Code version for unrelated features (a channels-preview floor) but not specifically for monitors.

## Daemon and IPC lifecycle

Long-running background processes the plugin manages, and how it coordinates them across sessions.

### Refcount-gated daemon with /tmp/-resident state

A SessionStart bash hook is simultaneously a dep-install gate, daemon launcher, stale-state cleaner, and session registrar. The daemon (Python `python -m bridge` via the venv's interpreter, spawned with `nohup ... &`) is started once across N concurrent sessions: each session increments `/tmp/<name>.refcount` on start, decrements on end; daemon killed only at zero. Runtime files in `/tmp/`: `<name>.sock`, `<name>.pid`, `<name>.refcount`, `<name>.log`, `<name>.skip-stop.flag`, `<name>-turn-stats.json`, `<name>-bt-name.cache`. Appropriate for plugins backed by a shared resource (hardware device, service connection) that should be singleton across concurrent Claude Code windows. Constraint: hook does multi-purpose work; reading it for one concern reveals all four.

### No long-running process

Plugin is invoked per-call (CLI shim or MCP server started by Claude Code per tool call). No daemon, no `/tmp/` state, no refcount. Appropriate for stateless or per-invocation tools.

## Plugin-to-plugin dependencies

Whether and how the plugin declares reliance on another plugin via the manifest schema or implicitly.

### `dependencies` field absent

No `plugin.json` declares the schema-level `dependencies` field. Where coupling exists between plugins (a shared math/storage plugin that other plugins consume at the file-read or subprocess layer), that coupling is documentation-only — contributor docs say "consume X from your scripts" but the manifest declares nothing. Schema-supported enforcement is deliberately skipped. Failure mode: a user installing a leaf plugin without its informally-required peer gets broken scripts at runtime with no manifest-time warning.

### `dependencies` field declared

`plugin.json` carries a `dependencies` array. May be empty (`[]`), bare strings (`["foo"]`), or objects (`{"name": "foo"}`). Custom resolver code accepts both shapes. Appropriate when the marketplace has multi-plugin dependency chains. Constrains tooling — Claude Code's native `dependencies` field is platform-version-gated (v2.1.110+ per the docs), so pre-version consumers ignore the field entirely; resolver behavior depends on consumer version.

### Implicit via filesystem convention

Plugin A reads files written by plugin B at a shared path (e.g., `~/.ai-sessions/spool/events.jsonl`) without any declared dependency. If B is not installed, A silently degrades (drift warnings stop firing, drift summary becomes empty, etc.). Appropriate when the dependency is genuinely optional. Constrains: there is no static signal of the coupling — install-time resolution can't detect that A would benefit from B.

### Implicit dependencies coded in installer

A self-installer hardcodes inter-module dependencies in source (`WRAPPER_REQUIRED_MODULES = new Set(["do", "omo"])` plus `WRAPPER_REQUIRED_SKILLS = new Set(["dev"])`) so selecting one module triggers `bash install.sh` for a shared binary. Not declarative; not visible to the marketplace consumer.

### Content-level integration with sibling project

`plugin.json` has no `dependencies` field. Where the plugin integrates with another project (e.g., a methodology framework like BMAD), the integration is content-level — embedded artifacts under a directory prefix and a dedicated skill that consumes them — not manifest-level. If the other project ships as a Claude Code plugin in the future, a `dependencies` entry would be a cleaner binding.

### External-MCP install during bootstrap

The npm bootstrap CLI offers to install third-party MCP servers (Context7, LangChain Docs) via `claude mcp add` during plugin install, prompting the user interactively. The MCPs are not declared as plugin dependencies; their install is a side-effect of running the bootstrap. Constrains: only fires through the npx path, not through `/plugin install`, so marketplace-installed users miss the augmentation entirely.

### `{plugin-name}--v{version}` tag format absent

No sample uses the multi-plugin-monorepo tag format. Combined with the universal absence of any tags at all in some bins, the format's hypothetical use case doesn't surface. Multi-plugin marketplaces are single-version where every plugin shares the same version string, or each plugin has its own version with no cross-plugin coupling declared.

## Testing

How the plugin verifies its own behavior — test framework, harness, and coverage.

### No tests

The plugin ships no `tests/` directory, no test files, no test framework. Verification posture leans on runtime hosts surfacing errors and on contributor-invoked review agents during authoring sessions. Manifest-correctness is trust-on-commit. CLAUDE.md may explicitly state "No test suite. The dev loop is: edit → reinstall the plugin → exercise skills manually." Manual validation steps documented as ad-hoc commands (e.g., `claude plugin validate .`, type-check via `uvx ty check <file>`).

### Hand-rolled bash tests

The plugin ships `tests/*.sh` files with hand-rolled PASS/FAIL counters, `mktemp -d` fixtures, and `git init -q` scratch repos for git-state-dependent tests. Includes `assert_eq`, `assert_contains`, `assert_not_null` helpers. No top-level runner; each test file self-executes via `bash tests/<test>.sh`. Tests typically `source` the underlying library directly rather than invoking the bin wrapper, so wrapper-path bugs are untested. Coverage scope: workflow scripts and end-to-end phase flows; hooks themselves are documented as "test by piping JSON into the hook script" rather than scripted.

### Author-time validator agents instead of automated tests

A repo with no `tests/` directory documents in contributor docs a manual-validation pipeline: contributor runs `plugin-validator` and `skill-reviewer` agents (vendored from Anthropic's official plugin suite) after any component change. Validation is interactive, runs inside a Claude Code session, and depends on contributor discipline. Repo-level `.claude/settings.json` blocks `git commit --no-verify` and `git push --force` but no commit hook invokes the validators.

### Multi-stack test setup (vitest + BATS)

Unit tests via vitest (1650+ tests at the sampled snapshot) with config at `vitest.config.ts`; shell-script integration tests via BATS, invoked as `bats tests/*.bats`. BATS installed at CI time via git clone + install script (not an action). Tests directories at `test/` (vitest) and `tests/` (BATS) coexist.

### pytest

Python tests under `tests/`; pytest config in `pytest.ini` at repo root or absent (relying on auto-discovery). Sometimes augmented with per-plugin `tests/test_cases.json` fixtures driven by a central `test_base.py` (data-driven test pattern).

### pytest with asyncio support

`pytest` with `pytest-asyncio` declared in `[project.optional-dependencies].dev` of `pyproject.toml`. `[tool.pytest.ini_options]` configures `testpaths = ["tests"]`, `asyncio_mode = "auto"`, custom markers (e.g., `integration` for tests that hit real LLM APIs). Test runner invoked as direct `pytest tests/ -v` or with marker filters. Substantial test suites (multi-thousand-line files) can coexist without CI when integration tests require live API keys.

### vitest

Node plugins declare `"test": "vitest run"` with `vitest` devDep. Standard Node test runner.

### node:test (node --test)

Some plugins use Node's built-in test runner (`"test": "node --test"`) instead of vitest. Appropriate for plugins minimizing devDeps; constrains test-style to node:test's API surface.

### node:test with tsx loader

Node.js built-in test runner via `import { test } from 'node:test'` plus `node --import tsx/esm --test '<glob>'` for direct TypeScript execution. No third-party test framework. Pitfall: glob expansion under Windows bash may match zero files; CLAUDE.md documents an explicit-paths workaround.

### bats (Bash Automated Testing System)

`.bats` files in `tests/` exercising the plugin's CLI through bash assertions. Unit and e2e suites split into separate files; e2e requires `playwright install chromium` plus the plugin's env vars threaded through the runner.

### go test

Standard Go test runner against a bundled Go binary subdir. `go test -v -cover -coverprofile=coverage.out ./...` plus `go tool cover -func=coverage.out` to print coverage. Coverage uploaded to codecov with `continue-on-error`. Coverage threshold not enforced.

### Tests declared but absent from tree

`package.json` declares a `test` script but no test sources are committed (tests stripped before sync from upstream). Constrains validation to whatever the upstream pipeline did before sync.

### Hook integration test via piped JSON

CI integration job pipes a synthesized hook-event JSON to the compiled hook script and asserts `jq -e '.continue == true'` on the output. Drives a real round-trip (hook reads stdin, performs work, emits stdout JSON) without spinning up Claude Code. Appropriate for verifying hook output discipline; constrains to deterministic hooks (stochastic ones would need fuzz harnesses).

### `verification/` directory of per-story proof documents

A dedicated `verification/` directory holds proof artifacts per story or feature. Not test code; a product artifact tracked in git. A novel answer to "how does an agent prove a feature works" sitting at the boundary of agent tooling.

## CI

GitHub Actions workflow shape — what runs, when, and against what scope.

### No CI

`.github/` directory absent or contains only issue templates. Validation is manual or reactive (install-time errors). Schema fixes appear as recurring entries in CHANGELOG (the cost signature of "no manifest-validation gate"). Tests exist locally but only run on a contributor's machine. The declared version has no automated validation.

### Single workflow per concern

`.github/workflows/<name>.yml` per concern (skill validation, docs site build, marketplace validation). Triggers on push/PR to main. Major-version action pinning (`actions/checkout@v4`). Built-in caching via runner setup actions (`cache: 'pip'`, `bundler-cache: true`).

### Two-job workflow — build-and-test plus validate-plugin

`ci.yml` runs on push and PR to default branches. Job 1 (`build-and-test`): `npm ci` → version-sync gate → `npm run build` → vitest unit tests → install BATS → `bats tests/*.bats`. Job 2 (`validate-plugin`): `python3 -c` JSON parse of `plugin.json`, required-field check (`name`/`version`/`description`), `bash -n` syntax check on subset of shell scripts. Pinned to `ubuntu-latest` + Node 20. No matrix. Action pinning by tag (`@v4`), not SHA. The shell-syntax glob may exclude critical directories (e.g., omits `hooks/*.sh`). `hooks/hooks.json` is not JSON-parse-checked; agent/skill/command frontmatter is not validated.

### Multi-stack matrix CI (TS + Go + integration)

`ci.yml` with five-plus jobs: TypeScript (`bunx tsc --noEmit`, `bun run build`, `bunx vitest run`, `bun run lint`); Go (`go test -v -race -coverprofile=coverage.out ./...` per submodule, Codecov upload `continue-on-error: true`); Go-lint (`golangci-lint-action@v9`); cross-stack build verification (`--help` smoke test of compiled binaries); integration (drives hooks with piped JSON: `echo '{"hook_event_name":...}' | bun dist/hooks/<hook>.js | jq -e '.continue == true'`). Triggers on push-to-main + PR-to-main. Action-pinning by major tag uniformly.

### Rust matrix CI with paths-ignore for plugin surface

`ci.yaml` with fmt + clippy + test + audit + docs jobs. Test matrix `{stable, ubuntu-latest}`, `{MSRV-from-Cargo.toml, ubuntu-latest}`, `{stable, macos-latest}`. Triggers `push: branches: [main]` + `pull_request`, both with `paths-ignore: ["**.md", "LICENSE", ".claude-plugin/**", "skills/**", "hooks/**"]` — plugin-surface edits don't retrigger Rust CI. Caching via `Swatinem/rust-cache@v2`. No shellcheck or hook-script lint. Constraint: pure skill/hook iteration ships without CI signal of any kind on the shell scripts.

### Firmware-build-only CI

Single `build-fap.yml` workflow: `ufbt build` of a Flipper FAP firmware binary, artifact upload, conditional `softprops/action-gh-release@v2` when ref is a tag. Triggers `workflow_dispatch` + `push` with path filter `flipper-app/**` + `tags: '*'`. No pytest, no shellcheck, no manifest validation. Plugin code (Python bridge, hook scripts) ships green even when broken.

### Push + PR matrix CI

`.github/workflows/ci.yml` triggers on `push` to default branch + release branches and `pull_request`. Matrix `os: [ubuntu-latest, windows-latest, macos-latest]` with a fixed runtime version (Go 1.21). Action pinning at tag level (`@v4`, `@v5`) — no SHA pinning. Built-in cache via the runtime's setup action's defaults.

### Single-job path-scoped CI for one plugin

Workflow scoped via `paths:` to one plugin's directory only — push/PR outside that path skips CI. Single `ubuntu-latest` runner, single Node version, no cache. Four chained jobs: syntax-check (node --check + JSON.parse on hooks/plugin/scripts manifests), unit-tests (bats), e2e-tests (bats with playwright + chromium installed), build-test (esbuild bundle exists and >1000 bytes — file-size threshold, not functional). Other plugins in the same marketplace get zero CI coverage.

### Test workflow on push/PR plus scheduled jobs

`.github/workflows/test.yml` runs lint (e.g., `ruff check`) and `pytest tests/ -v` on `push: branches: [main]` and `pull_request: branches: [main]`. Additional workflows handle scheduled work (daily cron) or manual dispatch (release/launch). All workflows hard-code Python 3.12 and ubuntu-latest with no matrix; actions are pinned to major tags without SHA pinning; no caching. Trade-off: scheduled bot commits trigger test runs for no code change, burning CI minutes; could gate on path filters.

## Release automation

How tag pushes, GitHub releases, or other automation cut releases — versus hand-cut releases without automation.

### No release automation

Releases are bump-`plugin.json` + commit + push, OR hand-cut via `gh release create` / GitHub UI without any automation. Tag commits land on main; release notes are hand-written into the GitHub release body. No `softprops/action-gh-release`, no `release-please`, no `semantic-release`. No tag-sanity gates verify `plugin.json` version matches the tag, that the tag is on main, or that anything was tested before tag time. `CHANGELOG.md` versioned headings without git tags or GitHub releases — no pinnable artifact.

### Multi-target release pipeline (npm + cross-repo marketplace dispatch)

`release.yml` triggers on `release: [published]` (GitHub Release event) or `workflow_dispatch` with a `tag` input. Three jobs: `test` (re-runs CI flow plus `npm run lint` and size guards), `publish-npm` (`npm publish --access public --provenance` via OIDC trusted publishing — no `NPM_TOKEN`), `marketplace` (cross-repo `repository_dispatch` to the aggregator with `MARKETPLACE_TOKEN`). Manual `gh release create` is load-bearing — tag push alone does not ship. The `publish-npm` job re-runs `npm ci` + `npm run build` rather than consuming an artifact from the `test` job. Cross-repo dispatch token coupling means a forked user cannot release without the aggregator-scoped PAT. Split runtime: `test` on Node 20, `publish-npm` on Node 24.

### Multi-trigger workflow with single-snapshot path

One `release.yml` (28 KB) handles PR CI, main-branch snapshots, and tag releases by gating jobs on `needs.prepare.outputs.is_release` and `github.event_name == 'push'`. `prepare` job computes version (from tag or from `git describe`), then test → build (six-platform matrix, CGO + zig cross-compile, UPX compression on linux/windows-amd64) + build-web + build-grammars (per-language tree-sitter `.so`/`.dylib`/`.dll` from upstream-cloned grammar repos at pinned tags) + build-npm. Tag push → `release` job (softprops/action-gh-release@v2 with `generate_release_notes: true`) + `publish-npm` (`npm publish --provenance --access public` requiring `id-token: write`). Main push → `snapshot` job (delete + recreate `snapshot` tag + prerelease release). `prepare` includes "commit already has release tag — skip" check via `git tag --points-at HEAD` regex. Constraint: snapshot tag force-recreated on every main push; consumers caching by tag SHA see silent moves.

### Dual-workflow split (CI + release)

Separate `ci.yaml` (lint/test/audit) and `release.yaml` (cross-compile + GitHub Release). Release triggers `push: tags: ["v*"]`. Build job: matrix over arch targets, `taiki-e/upload-rust-binary-action@v1` with `dry-run: true` to produce archives, `actions/upload-artifact@v7` to stash. Release job: download artifacts, `taiki-e/create-gh-release-action@v1` with `changelog: CHANGELOG.md` (parses Keep-a-Changelog format), `gh release upload <tag> artifacts/*`. Constraint: asset URL pattern (`mm-<target>.tar.gz`) is hardcoded in the bin shim; release-action default-naming changes break the shim silently.

### Tag-conditional step inside build workflow

No dedicated release workflow. Build workflow has a `if: startsWith(github.ref, 'refs/tags/')` step using `softprops/action-gh-release@v2` to attach the built artifact. Default GitHub auto-generated release notes (no body provided to action). Tag pattern `*` is permissive — any tag fires. Constraint: no tag-format gate, no version-match check; an accidental tag publishes a release.

### Tag-triggered prebuilt-binary matrix

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`. Matrix builds a Go binary for 6 OS/arch combinations with `CGO_ENABLED=0` and `-ldflags="-X .../version=${VERSION}"` to stamp the version. Uploads all artifacts plus install scripts via `softprops/action-gh-release@v2`. Release notes generated inline via `git log ${PREVIOUS_TAG}..${TAG} --pretty=format:"- %s (%h)" --no-merges` — bypasses the project's CHANGELOG.md. No tag-sanity gates: no verify-tag-on-master, no verify-tag-matches-package-version, no tag-format regex.

### CHANGELOG-parsing release action

`taiki-e/create-gh-release-action@v1` reads `CHANGELOG.md` (Keep-a-Changelog format) and extracts the section matching the tag's version. Release notes derived from the changelog rather than auto-generated commit log. Appropriate when curated release notes matter and the project commits to Keep-a-Changelog discipline.

### Auto-generated release notes from commits

`generate_release_notes: true` on `softprops/action-gh-release@v2` delegates to GitHub's built-in commit-based note generator. No CHANGELOG.md in repo. Appropriate for projects with conventional-commit-style histories. Constraint: regression investigation requires walking tags and comparing auto-generated notes; no human-curated narrative.

## Marketplace validation

How the marketplace.json and plugin.json shapes are checked before publish or at install time.

### No validation

No CI workflow lints manifests; no pre-merge gate validates `marketplace.json`, `plugin.json`, `hooks.json`, or skill frontmatter. Validation relies entirely on the runtime host (Claude Code, Codex, Cursor) surfacing errors at install or runtime. The `$schema` field (when present) is declarative but not validated by any workflow — install-time rejection by Claude Code is the only enforcement. Past releases have recovered from manifest-structure mismatches that would have been caught pre-publish (e.g., `plugin.json` at wrong path, `.md` hook files instead of `hooks.json`). Hook files using non-existent event names ship without complaint and never fire at runtime.

### Manual validator-agent invocation

A contributor runs an interactive validator agent (`plugin-validator`, vendored from Anthropic's official plugin suite) after any component change. The agent reads manifests and skill frontmatter and reports issues conversationally. Trigger is manual; correctness depends on the contributor remembering to invoke. Frontmatter validation is delegated to a separate `skill-reviewer` agent.

### CI-gated minimal validation (plugin.json fields + shell syntax)

A `validate-plugin` CI job parses `plugin.json` JSON, checks required fields (`name`, `version`, `description`), and runs `bash -n` against curated shell-script globs. No frontmatter validation, no `hooks/hooks.json` validation, no formal JSON-schema validation. Limited but better than nothing; missing surfaces ship undetected.

### JSON well-formedness only

CI `syntax-check` job runs `node -e "JSON.parse(...)"` on `hooks.json`, `plugin.json`, and `scripts/package.json`. Catches malformed JSON; no schema conformance check, no event-name validation, no unknown-field detection.

### Manual validation only

`claude plugin validate .` documented in CLAUDE.md as a developer's local step; not gated in CI.

### Custom skill-frontmatter linter, not CI-wired

A `scripts/validate-skills.ts` (or similar) implements an inline YAML-frontmatter parser and validates SKILL.md files for required fields (`name`, `description`, `triggers` non-empty array), no duplicate names, basic markdown sanity. Run manually via `bun run scripts/validate-skills.ts`. Not invoked by any CI workflow.

### Tiered validator driver

A single Python driver (`validate_all.py`) accepts `--tier {commit,push,ci}` and runs different validator subsets at each tier, with CI running all three sequentially. Drives 15+ underlying validators (frontmatter, structure, links, references, doc-structure, etc.). Constrains readers — the tier-to-validator mapping lives only in the driver source, not in the workflow YAML.

### In-editor skill (no CI)

A `/dev:validate` skill the author runs in-editor before `/dev:release`. Checks frontmatter, version sync between `package.json` and `plugin.json`, Python AST parse on tool files, executable bit on hook scripts, JSON validity of `hooks.json`, cross-references between skill `subagent_type:` and agent files. Validation is human-triggered; contributors without the skill ship blind.

### Runtime-only validation via jsonschema

`config.schema.json` exists in repo and a legacy installer (`install.py`) uses Python `jsonschema` to validate `config.json` at install-time on the user's machine. Not enforced in CI; a malformed config can be committed and only fails when a user runs the legacy installer.

## Documentation surface

What governance and consumer-facing docs the plugin ships at the repo / plugin root.

### README only

The plugin ships only `README.md` at the repo root — install + use + what-it-does + credentials/config + dev instructions. No `CHANGELOG.md`, no `architecture.md`, no `CLAUDE.md`. Architecture content (where present) lives inside the README as a narrative section. Minimal-overhead docs surface; appropriate for plugins where the README plus skill bodies cover everything. Constraint: rationale for breaking changes lives only in commit messages — a user upgrading across a major bump has no migration guide. Technical readers must reverse-engineer the design from source.

### README at root and per plugin

Root `README.md` is the marketplace overview with per-plugin blurbs and install commands. Each plugin carries its own `README.md` covering value pitch, install instructions, command/skill listing. Bilingual variants observed (e.g. `README_CN.md` alongside `README.md`).

### README + per-plugin READMEs + per-plugin CHANGELOGs + repo-root CLAUDE.md

A monorepo ships a heavy repo-root `README.md` (architecture diagram, FAQ, badges, schema.org JSON-LD for LLM/search indexing), a per-plugin `README.md` for each plugin tree, a per-plugin `CHANGELOG.md` in Keep-a-Changelog-lite format, and a repo-root `CLAUDE.md` documenting layout, contributor pipeline, hard rules, and pitfalls. No `architecture.md` — architecture content is duplicated between the root README's diagram and the CLAUDE.md's layout section. Heavy doc footprint scaled with the multi-plugin scope.

### README + WALKTHROUGH.md as architecture-adjacent

A single-plugin repo ships a `README.md` (install, prerequisites, per-command usage) and a long-form `WALKTHROUGH.md` (~17KB) that describes the underlying methodology, schema contract, and per-command flow. The walkthrough is framed as user tutorial but carries content an `architecture.md` would otherwise hold. No `CLAUDE.md` at repo root — though the plugin generates a `CLAUDE.md` template inside each user-created data directory as a per-data-directory schema anchor.

### AGENTS.md as cross-runtime governance unification

A repo serving Claude + Cursor + Codex consumers uses `AGENTS.md` (Codex-first convention) as the single agent-facing governance doc, in place of the Claude-native `CLAUDE.md`. Carries what would be both `CLAUDE.md` (operational procedures) and `architecture.md` (how the plugin works) in a Claude-native convention. Trade-off: per-runtime specificity for a single doc surface. Sub-architecture lives in `docs/design/<NNN>-<topic>.md` files — numbered design notes rather than monolithic.

### Three-doc model with consumer/dev/agent split

Repo root carries `README.md` (consumer-facing), `ARCHITECTURE.md` (developer-facing — note uppercase), and may carry a `CLAUDE.md`. Substantive subsystem READMEs for contributors (e.g., `<lib>/README.md`, `adapters/README.md`). Hosted Docusaurus site mirrors much of the in-repo documentation, with `docs/versioned_docs/version-X.Y.Z/` snapshotted per release. Constraint: two sources of truth (in-repo + Docusaurus) drift; the hosted version often lags.

### Three-document model (README + ARCHITECTURE + CLAUDE)

`README.md` (user-facing — install, usage, command tables, integration notes), `ARCHITECTURE.md` at repo root (entry point, module map, lib layout, hook list — may describe more than is shipped), `CLAUDE.md` at repo root (developer-facing release process, conventions, channel distribution notes). The architectural document may describe a richer hook surface than `hooks/hooks.json` actually wires.

### Two-document model (README + CLAUDE)

`README.md` (user-facing) plus a single `CLAUDE.md` (developer/contributor-facing — conventions, project structure, testing). No dedicated `ARCHITECTURE.md`; architecture content folded into `README.md`'s "Architecture" section (directory tree + protocol notes).

### Dual-CLAUDE.md (developer + user-workspace)

A repo-root `CLAUDE.md` is developer-facing (architecture for the plugin author), and a `templates/CLAUDE.md` is deployed into the user's workspace by a setup skill (architecture for the user's project). Same filename, different audiences. The root file's opening warning ("don't confuse the two") is load-bearing — without it, an agent working on the plugin could easily edit the wrong one.

### CLAUDE.md as architecture-doc carrier

No dedicated `architecture.md`; architectural content (three-layer diagram, threading model, protocol, runtime files, platform notes) lives inside `CLAUDE.md` at repo root. Combines build commands, architecture, threading rules, protocol reference, runtime files, platform notes, command menu, and release procedure. Blurs the agent-ops vs architecture separation conventional in the three-doc model.

### CLAUDE.md and AGENTS.md duplicating each other

Both files at repo root carry near-identical content (CLI shape, output formats, exit codes, build, commit format, dependencies, skills). No declared single-source-of-truth pointer. Drift risk on refactor.

### CLAUDE.md as project-config surface

`CLAUDE.md` declares a `## Project Type` field (`java | skills | blog | custom | generic`) that multiple skills read at runtime to dispatch to language-specific sub-skills. The doc doubles as agent-facing rules AND a runtime config surface. Constrains: skills must defensively parse the field and handle missing values, and the CLAUDE.md schema becomes part of the plugin's interface.

### CLAUDE.md at root or per plugin

Architecture-level operational doc covering build commands, build-system gotchas, hook protocol, env-var contract, supported-runtime list. Sometimes at repo root, sometimes only per-plugin, sometimes only at a `memorys/CLAUDE.md` subdirectory copied to the install target by the installer rather than read directly. Quality varies from minimal stub to highly detailed onboarding doc.

### Plugin scaffolds CLAUDE.md as user-data schema

A plugin generates a `CLAUDE.md` template inside each user-created data directory (`~/ObsidianVault/<wiki>/CLAUDE.md`) as part of its setup operation. This `CLAUDE.md` is not the plugin's own governance doc — it's user data that becomes the schema contract for subsequent skill invocations.

### No CLAUDE.md

Plugin or marketplace ships no `CLAUDE.md` operational doc. Agents working in the repo have no project-specific procedures to follow. Constrains agents to default behavior; rules and patterns live only in skill bodies if anywhere.

### Standard root entry points + per-plugin variation

Root carries `README.md`, `LICENSE`, sometimes `CLAUDE.md` and `CHANGELOG.md`. Per-plugin docs vary widely within one marketplace — some plugins have `docs/ARCHITECTURE.md`, some embed architecture rationale into README ("Why X", "Why Y" sections), some have topical docs (`PROTOCOL.md`, `ADOPTION.md`, `CERTIFY.md`, `SCAFFOLD.md`), some have superpowers/specs/plans subtrees. Inconsistency within a single marketplace makes a reader unable to predict where to find architectural detail without checking each plugin separately.

### Repo-meta docs alongside user-facing docs

Root carries the repo's own workflow artifacts (`DESIGN.md`, `PHILOSOPHY.md`, `QUALITY.md`, `HANDOFF.md`, `IDEAS.md`, `RELEASE.md`) — meta-documentation about how the repo operates. Often coexists with user-facing docs in `docs/`. Appropriate when the repo dogfoods plugins it ships.

### README + CONTRIBUTING + CLAUDE.md (no architecture.md, no CHANGELOG)

Repo-root `README.md` (with badges, installation, command/skill catalog), `CONTRIBUTING.md` (prerequisites, project structure), and `CLAUDE.md` doubling as project overview plus agent-facing operational reference. No dedicated `architecture.md` — architectural content is split between CLAUDE.md "Architecture" and README "How It Works", with a separate long-form `GUIDE.md` for human readers.

### README + docs/ tree (architecture, configuration, walkthrough, limitations)

Repo-root `README.md` (Quick Start, Claude Code integration, MCP tools table, SDK integration, "How It Works" pipeline diagram) plus a `docs/` directory with `architecture.md`, `configuration.md`, `walkthrough.md`, `limitations.md`, `assets/`. `.gitignore` may explicitly exclude `CLAUDE.md` and `**/CLAUDE.md` — a deliberate stance that agent-context files are not committed.

### docs/DESIGN.md and docs/SPEC.md

Architecture content lives in `docs/DESIGN.md` (~36 KB) and `docs/SPEC.md` (~22 KB) rather than a root `architecture.md`. Substantive design rationale, but a consumer following the "architecture.md at root" convention misses them.

### CHANGELOG presence and shape

Multiple shapes coexist across the corpus:

- **Keep a Changelog (1.1.0)** — `CHANGELOG.md` at repo root, SemVer-aligned `## vX.Y.Z` sections, parsed by `taiki-e/create-gh-release-action@v1` for release notes
- **Hybrid Keep-a-Changelog-ish** — header declares semver, entries are `## [X.Y.Z] — <date>` with narrative subsections (no strict `Added`/`Changed`/`Fixed` buckets)
- **Custom firmware-scoped CHANGELOG** — `<subsystem>/CHANGELOG.md` (not at repo root), custom `## vX.Y` section format, not parsed by automation
- **Per-plugin Keep-a-Changelog** — within a multi-plugin marketplace, some plugins ship `docs/CHANGELOG.md` while others lack changelogs entirely despite high patch-version counts
- **Conventional-commit-driven** — `CHANGELOG.md` updated by the release skill or `git-cliff`, parses `feat:`/`fix:`/`refactor:` prefixes from `git log` output and inserts dated sections
- **Absent** — release notes from `generate_release_notes: true` (auto-generated commit log) or no changelog at all

### Auto-generated docs index

`docs/DOCS_INDEX.md` is generated by a repo script (`scripts/generate-docs-index.sh`) and injected into sessions via SessionStart Layer 3. Live index over `docs/`, not a hand-maintained TOC. Test coverage exists for the generator script.

### Schema.org JSON-LD as LLM-indexer surface

The repo-root README.md ends with a `<script type="application/ml+json">` block declaring `@type: SoftwareApplication`. Explicit comment in source: "Machine-readable metadata for LLM + search indexers (Perplexity / ChatGPT / Claude / Google AI Overviews)." Treats the README as a distribution surface for LLM-driven discovery, not just human readers.

### Joke badges and brand SVGs

Marketplace ships static SVG assets like `works-on-my-machine.svg` and `designed-in-ms-paint.svg` referenced via relative paths from every plugin's README. Marketplace-level branding through co-located assets. Persona-style READMEs may add animated typing-SVG headers and social-share buttons (X, Reddit, HN).

### Badges and status indicators

One sample's README carries Shields.io badges (license, runtime, language, dynamic stars/forks/issues/last-commit). Most ship none. Optional polish, no shared pattern.

### Design-lineage attribution in README

README opens with "Inspired by <other-project>" linking to a precursor. Uncommon — most plugins do not attribute design lineage in user-facing docs.

### Documentation drift signals

Two specific drift shapes recur:

- **README/CLAUDE.md disagrees with the actual install script** about install location (`${CLAUDE_PLUGIN_DATA}/node_modules` vs `${CLAUDE_PLUGIN_ROOT}/<server>/node_modules`). The script is the source of truth; the doc was not updated when the install location moved
- **README cites `engines.node >= N`** but `package.json` declares `>= N+M`, or `engines.node >= 22` while CI tests on Node 20 — engines floors are sometimes aspirational and not gated

## Community health files

Standard open-source repo files beyond LICENSE.

### Bare minimum (LICENSE only)

Root carries `LICENSE`. No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`. Constrains contributor-onboarding to whatever the README says.

### LICENSE + CODE_OF_CONDUCT + issue templates

Root carries `LICENSE` and `CODE_OF_CONDUCT.md`; `.github/ISSUE_TEMPLATE/` has `bug_report.md` and `feature_request.md`. No `SECURITY.md` or `CONTRIBUTING.md`. Constrains: contribution flow is implicit, security-disclosure path undocumented.

### Community health files absent

`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md` uniformly absent. Where security-relevant policy exists (secret-file deny rules), it lives inside `.claude/settings.json` rather than a standalone doc.

## License declaration

Where the license is declared and how it propagates to ecosystem detectors.

### LICENSE file at root

Universal across many samples — `LICENSE` (e.g. AGPL-3.0, MIT) at repo root governs the marketplace. SPDX `MIT` declared in `plugin.json` and any sibling manifests (`pyproject.toml`, `package.json`).

### LICENSE absence vs declared license

`plugin.json` and README declare a license (e.g., MIT) but no `LICENSE` file is committed. GitHub's license detector returns null. Downstream consumers have no SPDX anchor; marketplace listings cannot show a license badge. When per-plugin `plugin.json` entries declare licenses but no root `LICENSE` exists, GitHub API reports `license: null` even though individual plugins claim a license — repo is legally ambiguous despite the per-plugin claim.

### Per-plugin LICENSE alongside root LICENSE

Per-plugin LICENSE files coexist with a root LICENSE in some repos. Same SPDX, redundant placement.

## Permission and contributor governance

How the repo distinguishes contributor-environment policy from end-user-environment policy.

### Plugin-root settings.json — agent pointer only

A `settings.json` at each distributed plugin's root carries `{"agent": "<router-name>"}` to activate a custom agent as the main thread when the plugin is enabled. Contributor docs note that only `agent` and `subagentStatusLine` are the supported keys — unknown keys silently ignored. Convention: point `agent` at a broad router (not a narrow specialist) so the plugin feels natural when enabled. Distinct from the repo-root `settings.json` — the plugin-root file governs end-user sessions with the plugin enabled.

### Repo-root .claude/settings.json — contributor-only permission matrix

A `.claude/settings.json` at the repo root declares `defaultMode: "acceptEdits"`, a ~100-entry allow/ask/deny permission matrix, and secret-file deny rules (`Read/Edit/Write` against `.env*`, `credentials*`, `*.pem`, `*private*key*`). Governs contributor Claude Code sessions against this repo only; never shipped to end users (the entire `.claude/` tree is contributor-only by convention). Replaces a `SECURITY.md` — security policy as enforced settings rather than narrative doc.

### Vendored contributor toolkit as sibling marketplace

`.claude/plugins/.claude-plugin/marketplace.json` hosts a separate marketplace (e.g. `<repo>-local`) with vendored Anthropic-official plugins (`plugin-dev`, `claude-code-setup`). Contributors activate it via `/plugin marketplace add ${CLAUDE_PROJECT_DIR}/.claude/plugins`. Repo invariant: "`.claude/` is contributor-only and never shipped to end users." Reuses the marketplace.json mechanism as a dev-toolkit bootstrap rather than for plugin distribution.

### Default tools, no permission escalation

Agents declare a comma-separated `tools:` scalar string (`Read, Write, Edit, Bash, Glob, Grep`). Sometimes `disallowedTools:` provides a negative list. No `permissionMode`, no permission-rule syntax (`Bash(...)` wildcards). Appropriate for agents with conservative authority. Constrains: every edit path goes through the standard permission flow.

### `permissionMode: acceptEdits` + worktree isolation

Agent runs with pre-granted edit authority (`permissionMode: acceptEdits`) inside a git worktree the orchestrating skill creates. Safety comes from worktree boundary + post-hoc human review at a `/deploy` skill, not from tool-use hooks or in-flight permission gates. Constrains: the orchestrating skill MUST set up the worktree first, otherwise the agent operates on the live tree with full edit authority.

## PATH augmentation

How the plugin handles user-installed CLIs that aren't in the minimal PATH Claude Code propagates.

### PATH-bootstrap script sourced by every hook

A `scripts/path-bootstrap.sh` prepends common user bin dirs (`$HOME/.ship/bin`, `/opt/homebrew/bin`, `/usr/local/bin`, `$HOME/.local/bin`, `$HOME/go/bin`) to PATH. Sourced from the top of every hook script. Driven by the observation that "Claude Code and some CI environments inherit a minimal PATH that excludes common install dirs" — an adaptation layer for missing-PATH pathology rather than a plugin-managed install of those tools.

### Runtime-environment sanitization at invocation site

A skill wraps third-party CLI invocations in `env -u <VAR> <cli>` to defend against user-environment contamination — specifically `env -u BUN_INSTALL` to prevent Bun's bundled SQLite (which lacks extension loading) from being picked up over Node when invoking a tool that needs SQLite extensions. Plugin-side defense at the skill level rather than at install time.

### Auto-shell-rc modification

`install.sh` detects user shell and writes PATH-append lines to shell rc files (`bashrc`, `zshrc`) with idempotency guards. Crosses the line from "install under `~/.claude`" to "modify user dotfiles" — most plugin-era patterns avoid this because plugin uninstall cannot reliably reverse the shell-rc edits.

## MCP server scope

Where `.mcp.json` lives and which audience it serves.

### Plugin-distributed MCP server

A plugin ships `.mcp.json` inside its plugin tree, registering an MCP server (e.g., a Bun/TypeScript channel server) that the plugin distributes. Substituted via `${user_config.<KEY>}` for env values. Travels with the plugin to consumers. Constraint: the plugin must also ship the server source (`channels/<name>/server.ts`) and its dep-install hook.

### Repo-root MCP server for contributor use

A `.mcp.json` lives at repo root (not under any plugin tree) registering a peer MCP server for use by skills during local development of the plugin itself. Consumers installing via `/plugin install` don't inherit this — it's not part of the plugin tree. Contributors clone the repo and get the MCP wiring as part of working on the plugin source. Distinct role: plugin-distributed MCP travels to users; repo-root MCP serves the maintainer.

## Project-scoped permission grant

How the plugin requests or applies permission entries beyond what marketplace metadata covers.

### Setup script writes scoped entries into target project's settings.local.json

A bash script under `bin/` (e.g., `setup-permissions.sh`) writes an enumerated allow-list of specific paths and command shapes into the target project's `.claude/settings.local.json`. Examples: specific script paths, project-relative glob shapes (`./<tool>.sh*`), narrow git operations (`git checkout -b <prefix>/*`, `git commit -m "<prefix>:*"`, scoped `git add`/`log`/`diff`/`status`/`rev-parse`), plus the `statusLine` block. Existing `permissions.allow` entries are preserved; duplicates skipped. Allow-list-first (not `*`-blanket) — each grant is the narrowest pattern that lets the workflow function. Constrains: the grant set is plugin-author-curated; expanding the workflow requires editing the setup script and re-running. The grants live in the user's project, not the plugin, and persist across plugin updates until the user removes them.

## Host-project setup

How the plugin handles configuration, scaffolding, or hook installation in the user's host project versus in the plugin itself.

### None (plugin operates standalone)

The plugin requires no host-project scaffolding. State and config live entirely under `${CLAUDE_PLUGIN_DATA}` or are derived from the user's existing repo without modification. Appropriate when the plugin is self-contained and the host project is a passive subject of the plugin's operations.

### Setup script scaffolds the host project

A `scripts/setup.sh` (often invoked via a `/<plugin>:setup` slash command) creates a project-local config directory (e.g., `.coco/`), populates a default config file, installs git hooks into `.git/hooks/` of the host project, merges plugin permissions into the host's `.claude/settings.json`, and adds plugin artifacts to the host's `.gitignore`. Migration logic (e.g., legacy slug rename) may also be embedded. Most plugins leave host-project setup to the user; this approach takes ownership. Trade-off: setup script in-tree and slash-command both invoke the same scaffolding and the duplication is real; one path is sometimes legacy. Aggressive scaffolding mutates the host project in ways the user must re-discover when they move to a fresh checkout.

## Multi-runtime polyglot support

Whether the same plugin tree serves multiple agent runtimes (Claude Code, Cursor, Codex).

### Single-runtime — Claude Code only

Plugin manifests live exclusively under `.claude-plugin/`. No `.cursor-plugin/`, no `.codex/`. Skills, hooks, and bin wrappers assume Claude Code's env vars and hook schema. The default shape across most of the corpus.

### Triple-runtime parallel manifests

The repo ships three parallel manifest trees: `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, and `.codex/` (install-by-symlink). Same `scripts/` and `skills/` trees. Hook schemas differ per runtime — Claude uses nested `{hooks:[{hooks:[{type, command}]}]}`, Cursor uses flat `sessionStart: [{command: "./hooks/session-start"}]` plus a top-level `version: 1` field, Codex adds `statusMessage` and `timeout` fields Claude lacks. A trivial bash exec wrapper bridges Cursor's relative-command schema to the shared script. Skill preambles use a triple-fallback chain (`SHIP_PLUGIN_ROOT` env, bin-discovery wrapper, hard-coded Codex install path) to locate the plugin tree under any runtime. Cross-runtime version drift is live and hand-aligned.

## Multi-consumer plugin packaging

A single codebase packaged for multiple consumers (Claude Code marketplace + npm + others).

### Tri-target same-codebase plugin

Same source packaged as (a) Claude Code marketplace plugin, (b) OpenCode npm package (`@<author>/<name>-plugin` via `packages/opencode-plugin/`), (c) Codex CLI install target (via `bunx @<author>/<name>-plugin install --platform codex`). TypeScript core under `src/core/` is shared; an `src/opencode/` adapter layer adapts it; `src/cli/` drives the npm install flow for non-Claude-Code consumers. The bin-wrapper's `<name>_PLUGIN_ROOT` env-var-first resolution exists specifically because `CLAUDE_PLUGIN_ROOT` isn't set in non-Claude-Code ecosystems. Constraint: every plugin-protocol concern must be expressed across all three target conventions.

### Dual-mode plugin/library

The same source tree installs either as a Claude Code plugin (via marketplace) or as a pip-installable Python library (via `pip install -e ".[dev]"` plus a project-local `init` command). The library-mode entry point declared in `pyproject.toml [project.scripts]` is invisible to plugin-mode users because their venv lives in plugin data and isn't on PATH. Two install paths, one conceptual surface, no runtime overlap because plugin-mode uses `${CLAUDE_PLUGIN_ROOT}`-relative paths and library-mode uses project-absolute paths. Some configuration (e.g., MCP server registration) has parallel mechanisms (inline in `plugin.json` for plugin-mode, `.mcp.json.example` template for library-mode).

## Custom installer alternative

A repo-shipped distribution mechanism that side-steps `/plugin install`.

### Localhost web UI installer

`scripts/web_installer.py` runs a local HTTP server (e.g., port 8765) that reads `marketplace.json`, presents the catalog (including the custom `bundles` extension) in a browser UI, and installs selected plugins as `~/.claude/skills/<name>/` via sparse git-clone. Bypasses Claude Code's plugin caching entirely. Appropriate when the platform's install UX is insufficient for the author's feature set (here, dependency resolution and bundle grouping); constrains: behavior diverges from `/plugin install` semantics, and uninstall semantics are different.

### CLI installer with sparse-checkout

`scripts/<plugin>-skill` (or similar standalone CLI) installs into `~/.claude/skills/` via `git clone --filter=blob:none --sparse` per-plugin. Acknowledges in README that the official marketplace doesn't support automatic dependency resolution and the custom installer fills the gap.

### npm bootstrap

`bin/install.js` + `npx <plugin>@latest` installs the plugin into multiple agent runtimes (`~/.claude`, `~/.cursor`, etc.) and optionally configures external MCPs. Distinct concern from "install as Claude plugin" — same source, different consumer. Constrains the install script to detect and target each supported runtime's directory layout.

### Hook-config stitching with module-tagged surgical unmerge

Self-installer merges per-module `hooks/hooks.json` into `~/.claude/settings.json` and tags every merged hook entry with `__module__: <module-name>`. Uninstall scans settings.json and removes only entries with the matching tag, leaving user-added hooks untouched. Surgical unmerge strategy worth naming as a pattern for installers that mutate global state.

### Operations DSL with restricted run_command

Self-installer's `config.json` defines modules as a sequence of typed operations (`copy_file`, `copy_dir`, `merge_dir`, `run_command`). `run_command` is restricted at the installer level to exactly `"bash install.sh"` — no arbitrary commands. Minimum-capability safeguard on a powerful primitive: the operation type is general but the registry only permits one specific invocation.

### Installed-modules status file

`~/.claude/installed_modules.json` tracks what was installed with timestamps and per-operation results. Used by `--update` to detect which modules to re-install and by `uninstall` to know what to remove. Durable state file separate from Claude Code's own settings, acting as the installer's source of truth for what it has done to the user's machine.

### Post-install detection report

Installer runs `which <each-tool>` (`which codex`, `which claude`, `which gemini`, `which opencode`) and reports status with `✓`/`✗` markers, plus detects whether `~/.claude/bin` is in `$PATH`. User-friendly telemetry without phone-home — diagnostic on the user's machine only.

### Dual installer (legacy + current)

`install.py` (Python, 1,533 lines, uses `jsonschema`) and `bin/cli.js` (Node, 1,285 lines, the new blessed path) coexist. The shell wrapper prints a 5-second warning banner directing users to the npx path. Migration-in-progress visible in repo structure — a marker that the project is mid-replacement of its own infrastructure.

## Native artifact distribution

How a plugin distributes a compiled native binary (Go, Rust, C) to users.

### On-demand GitHub-release download

Plugin doesn't vendor the binary in git; downloaded from `releases/download/v<version>/<binary>` (with a `releases/latest/...` fallback or a separate `snapshot` floating tag for race mitigation). Versioned URLs first, floating last. macOS Gatekeeper handled by best-effort `xattr -d com.apple.quarantine` after `chmod +x`. UPX compression on a subset of platforms (linux/windows-amd64) where it works reliably; skipped on darwin and windows-arm64. Repo stays small at the cost of first-run network dependency.

### Per-platform asset matrix with shared-library carve-out

Release workflow builds N platform tarballs (e.g., linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64, windows/arm64) per binary. Tree-sitter grammars (or analogous shared libraries) built as separately-downloadable platform-specific shared libraries (`<name>-grammar-<lang>-<version>-<os>-<arch>.tar.gz`), dynamically loaded at runtime. Lockfile (`.<name>-grammars.lock`) tracks pinned upstream grammar repo tags. Cross-compile via Zig (downloaded from `ziglang.org/builds/...` per build step). Constraint: external CDN dependency at build time; deleted upstream grammar repos warn-and-continue silently.

### Rust cross-compile via Cargo + macOS-only runtime

Release workflow uses `taiki-e/upload-rust-binary-action@v1` with matrix over apple-darwin targets only (`x86_64`, `aarch64`); cross-platform compile elsewhere is CI-sanity only. The product itself is macOS-only. Asset URL `<name>-<target>.tar.gz` hardcoded in the bin shim. Constraint: non-Darwin platforms fail at runtime in the shim, not at install.

### Firmware artifact alongside plugin

A `.fap` firmware binary built via `ufbt build` and attached to the GitHub release as a sibling artifact to plugin-relevant assets. Built on `ubuntu-latest` with `actions/setup-python@v5`. Appropriate for plugins paired with custom hardware firmware; the firmware is a separately-installed product that the plugin's daemon talks to.

### Bundled go.mod for prebuilt binary

`codeagent-wrapper/go.mod` describes a Go binary bundled in the plugin source tree, rebuilt by CI for six target OS/arch combinations and attached to GitHub Releases as prebuilt artifacts. The plugin's runtime install fetches the prebuilt binary by uname-derived URL rather than rebuilding from source on the user's machine.

### WASM-over-native with graceful fallback

Tree-sitter parsers loaded via `web-tree-sitter` (WASM) so no native compilation needed for grammars. Only `better-sqlite3` requires native; on native failure, code falls back to a JSON file cache with identical semantics (slower for large repos). Install script exits 0 even when the native build fails, treating native as an optimization rather than a requirement.

## Project-convention sidecar files

Project-specific configuration files that aren't standard Git or Claude Code conventions but are read by the plugin's own logic.

### `.worktreeinclude`

A repo-root file listing files the plugin should copy into git worktrees it creates for sub-agent workflows (e.g., `.evolver.json`, `.env`, `evolution_archive/`). Read by skill steps when setting up isolated proposer worktrees. Appropriate when the plugin orchestrates multi-worktree workflows that need a curated subset of project state. Constrains: not a standard mechanism — the file is meaningful only to this plugin's skills.

### `.codetographignore` plugin-private ignore file

Plugins that scan target-project source for indexing accept a plugin-private ignore file (`.codetographignore`) with `.gitignore` syntax that lets a project exclude paths from the plugin's scan without polluting `.gitignore`. Plugin-private ignore conventions add a parallel ignore namespace per plugin.

### Plugin-internal `.scm` query asset class

`scripts/queries/` holds per-language tree-sitter `.scm` query files loaded at runtime by an extractor module. Not a `skills/`, `agents/`, `hooks/`, or `commands/` component — an unconventional plugin-internal asset class shipping as data alongside executable code.

## Identity and brand stance

Constraints on technology choices that flow from a deliberate identity ("zero deps", "self-contained", etc.) rather than from technical necessity.

### Zero-runtime-dependency stance

"bash + jq, no daemon, no database, no node_modules" is a load-bearing README badge and pitch. The stance constrains several other axes — no PEP 723 scripts, no npm packages, no binary downloads — in service of a distinctive identity. Trade-off: the surface of tools available to the author is constrained; system-tool version requirements (bash 4+, jq 1.6+) become hard prereqs that older platforms (macOS bash 3.2) silently fail against.

## Long-running scheduled behavior

How the plugin handles scheduled or recurring work that needs to run independently of an interactive Claude session.

### Outsourced to GitHub Actions cron

No `monitors.json`, no Claude Code-scheduled background work. Long-running scheduled behavior (daily cycles, engagement reports) runs in `.github/workflows/*.yml` on cron triggers. The plugin is the "author/debug" interactive surface; CI is the "operate" durable-scheduler surface. Appropriate when the plugin's user already has a GitHub repo for their work and write access to it; CI minutes are cheap. Trade-off: requires a GitHub repo and OIDC or secrets-based credentials in Actions; doesn't help users on private/self-hosted Git platforms.

### Slash-command surface only (no scheduling)

No `monitors.json`, no CI cron. Long-running state surfacing is handled entirely by agent-invoked slash commands (e.g., `/<plugin>:dashboard`, `/<plugin>:status`, `/<plugin>:standup`). Sidesteps the entire monitoring surface.

### None (context-provider plugin)

The plugin is a context provider (memory, retrieval) and does not have any scheduled or recurring surface to expose. Appropriate when the plugin's value is purely reactive (per-prompt context injection, per-stop background ingest).

## Bounded autonomy and autoresume control

Plugin-level flow control for otherwise unbounded agent loops.

### Stop-hook with budgeted resume

A `Stop` hook decides whether to auto-relaunch an agent, capped by per-session resume count and time-since-last-resume. State persisted in a session JSON file (`resume_count`, `resume_at`). Three modes:

- `headless` — launches a new background `claude -p` process
- `prompt` — prints instructions to the user
- `off` — disables auto-resume

Plugin-level flow control distinct from in-agent loop bounds; the hook constrains the harness's session lifecycle directly.

## Session persistence layout

How a long-running plugin captures the state of a multi-cycle session.

### Three-file separation by consumer

Three files, each serving one consumer:

- A living-prose markdown document (e.g., `<tool>.md`) — human-facing and resume context for the agent
- An append-only JSONL log (e.g., `<tool>.jsonl`) — tooling consumption (dashboard, scoring, classification)
- A current-state JSON (e.g., `.<tool>.state`) — hook + statusline polling

Deliberate separation across format × access pattern. Each file's format matches its consumer's needs (markdown for narrative, JSONL for stream, JSON for poll).

## Explainable state machine surface

How the plugin exposes its internal state to the agent.

### CLI verb returning structured state explanation

A first-class CLI verb (e.g., `<tool> explain`) prints `Health / Mode / Failure / Action / Reason / Baseline / Best / Last / Streaks` from the persisted state plus a segment summary plus config. The agent is instructed to call it on resume and after any ambiguity. Makes the state machine introspectable by the agent itself, not just by the user.

## Observability and telemetry pipelines

How plugins record session-level events for later analysis.

### Multi-hook recording pipeline → MCP server → read-only agent

A 4-hook recording pipeline (SessionStart, UserPromptSubmit, Stop, PostToolUse with selector and PostToolUse without matcher) feeds a single Python recorder that appends to a JSONL log, which is then flushed to a database (e.g., MongoDB) by a dedicated MCP server, which is then queried by a read-only agent constrained via `tools:` allowlist + `disallowedTools:` denylist. Five layers (hook → recorder → JSONL → MCP flush → agent) for workspace observability alone. A coherent subsystem within a single plugin: every layer is plugin-shipped, every boundary is explicit, and the read-only agent is a first-class consumer. Distinct from generic hook usage; closer to "observability as a plugin product axis."

## Cost-gated MCP tool surfaces

How plugins constrain a paid or rate-limited tool's blast radius.

### Per-call rule gates plus pinned tool subset

A paid MCP integration is opt-in and rule-gated (e.g., `icp_score >= 7` or `priority: high/urgent`, always confirmation-gated, forbidden in specific stages of a workflow). The MCP server URL pins a narrow tool subset via query string (`?tools=docs,code_crafter/leads-finder,...`) so even a rule-bypass cannot reach the broader API surface. Rule enforcement is distributed across multiple agent prompts and a `templates/CLAUDE.md` that downstream sessions read. A defensive configuration move — pinning the tool subset at the URL is structural (cannot be widened by prompt drift), while the rule gates are normative (depend on agent compliance).

## Novel and cross-cutting concerns

Patterns surfaced by samples that don't fit a single role above.

### MCP "channel" as inbound event bus

One sample ships an MCP-channels-as-inbound-event-bus pattern (research-preview Claude Code feature gated to v2.1.80+ and `claude.ai` login, not API-key auth). The channel server (Bun/TypeScript) declares `claude/channel` capability, exposes HMAC-gated webhook routes (`/tradingview`, `/polymarket/fill`, `/cdp`, `/commerce`, `/custom?kind=...`), and converts each inbound event into a `<channel source="..." type="..." ...>...</channel>` context tag inside the running Claude session. Distinct primitive from `monitors.json` (outbound stdout lines) and from normal MCP tool servers (stateful request/response). One-way inbound only — README claims "NO reply tool, NO permission relay."

### Self-update advisory channel

Plugin script (`update-check.js`) hits `https://raw.githubusercontent.com/<owner>/<repo>/master/<plugin>/.claude-plugin/plugin.json` over the network, compares `.version` against the bundled value, caches the result in `~/.cache/<plugin>/update-check` with asymmetric TTLs (60 min for up-to-date, 720 min for available-update so a known update keeps surfacing for 12 h while a new release is detected within an hour). Emits `UPDATE_AVAILABLE <old> <new>` on stdout for the skill preamble to parse and surface to the user. Lightweight self-update notification that does not require marketplace infrastructure.

### MCP server reads hook-authored artifact

MCP server's tool surface is a projection of state authored by hooks: a hook (`stop.js`) writes `docs/<plugin>/map.md` via `atomicWrite` after parsing the project; the MCP server (`mcp/server.js`) parses that map and `watchFile`s it with a 500ms debounce. Decouples MCP responsiveness from heavy parsing cost — MCP doesn't parse source, it parses the rendered map. Cross-component data flow (hooks produce, MCP consumes) without RPC or shared-memory coupling.

### Generated-package.json pattern

A SessionStart install script writes a minimal `{"private":true}` `package.json` into `${CLAUDE_PLUGIN_DATA}` on first run rather than shipping one. Keeps the plugin repo free of Node-ecosystem noise (no committed lockfile, no `node_modules/` gitignore, no committed dep manifest) while still giving npm a valid project to operate on. Authoritative dep declaration lives inline in the install script's `npm install <pkg>` command.

### Graceful-degradation via fallback tool

When a plugin's optional tool (installed by SessionStart) is missing, the skill falls back to a manual stdlib-only path (e.g., `wiki/index.md` read + grep instead of `qmd` query). Documented fail-soft inside the skill body, not an install retry. The plugin works in reduced mode even if dep install permanently fails. Pairs with the install script's fail-open stance.

### TypeScript-compiled hooks with hand-patched imports

Post-`tsc` distribution step (`scripts/copy-hooks.js`) mirrors `dist/` into `hooks/dist/` + `mcp/dist/` + `scripts/` and rewrites relative imports (`'../xxx'` → `'./dist/xxx'`, etc.) so hook entry points stay plain `.js` invokable by `node` while pulling shared code from a co-located `dist/` tree. Avoids both a runtime TS loader in hooks and a bundler. Build-system gotcha called out: "Always run `npm run build:hooks` (not just `npm run build`)".

### Cool-off window on event-driven regeneration

`hooks/stop.js` skips map regeneration if the output file's mtime is within the last 60s, to avoid redundant work when a manual refresh just ran. Explicit de-dup window for event-driven artifact regeneration.

## Cross-role tools

Tools and mechanisms that fill multiple roles in the corpus and surface under each role above:

- **Bun** — TypeScript runtime for bin-wrapper (Bin-wrapped CLI distribution); Node-modules installer in self-heal path (Dependency installation); test runner via `bunx vitest run` (Testing); skill-validator host (Marketplace validation).
- **Docker / npm packages / package.json** — dep manifest format (Dependency installation); bin-entry surface for npm distribution (Bin-wrapped CLI distribution); release publication target (Release automation).
- **softprops/action-gh-release@v2** — release-creation mechanism in tag-conditional step, dual-workflow split, snapshot path, and prebuilt-binary matrix (Release automation); native-artifact upload step (Native artifact distribution).
- **`hookSpecificOutput.additionalContext`** — context-injection channel in SessionStart welcome-state path (Session context loading); same channel in PostToolUse skill-nudge path (Tool-use enforcement); same channel in UserPromptSubmit fuzzy-match path (Session context loading); fail-open dep-install advisory (Dependency installation).
- **GitHub Releases** — primary download source for native binaries (Native artifact distribution); same surface used by binary-download dependency-install paths (Dependency installation); release pipeline target (Release automation).
- **`/tmp/`-based filesystem state** — daemon coordination via socket/PID/refcount (Daemon and IPC lifecycle); cross-hook flag-file coordination (Cross-hook environment plumbing); session-scoped one-shot nudge marker (Tool-use enforcement).
- **macOS Gatekeeper handling (`xattr -d com.apple.quarantine`)** — post-download install step (Dependency installation); same step in bin-wrapper lazy-download path (Bin-wrapped CLI distribution); native artifact post-extract step (Native artifact distribution).
- **`jq`** — `hookSpecificOutput` JSON construction in shell hooks (Hook output convention); version extraction from `plugin.json` in download shims (Dependency installation); zero-dep stance prerequisite (Identity and brand stance); tool-call payload parsing in PreToolUse path validators (Tool-use enforcement).
- **`$CLAUDE_ENV_FILE`** — cross-hook env propagation (Cross-hook environment plumbing); userConfig-to-dotenv bridge (User configuration); SessionStart writing env vars (Session context loading).
- **`${CLAUDE_PLUGIN_DATA}`** — install destination for managed deps (Dependency installation); state directory in plugin/state separation (Plugin/state separation); native binary install location (Native artifact distribution); bin wrapper venv resolution (Bin-wrapped CLI distribution).
- **`${CLAUDE_PLUGIN_ROOT}`** — code/cache directory in plugin/state separation (Plugin/state separation); inline-config path interpolation in plugin.json (Plugin-component registration); env-var fallback in bin wrappers (Bin-wrapped CLI distribution).
- **CHANGELOG.md** — release-notes source for `taiki-e/create-gh-release-action@v1` (Release automation); auto-generated by `git-cliff` (Release cadence and tagging); part of the documentation surface (Documentation surface).
- **Codex / OpenAI runtime** — co-distribution via sibling `agents/openai.yaml` (Cross-platform skill publishing); npx-based install target alongside Claude (Multi-runtime polyglot support, Multi-consumer plugin packaging); manifest convention difference (Plugin-component registration).
