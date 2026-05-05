# Sample

Merge of 6 partials (bins 7-12) into `_CONSOLIDATED_pass1-merge-stage1-b.md`. Functional roles with implementation paths and qualitative descriptions; no inline citations (see `references` verb for provenance).

## Marketplace manifest layout

How the plugin's identity and source binding are exposed to Claude Code's marketplace machinery — where manifest files sit, how many there are, and what wrapping object their top-level metadata takes.

### Single-plugin marketplace at repo root with `source: "./"`

A `.claude-plugin/marketplace.json` sits next to `plugin.json` at repo root and carries one entry whose `source` is `./` — the plugin IS the repo. The marketplace exists only to satisfy the install protocol; the catalog name is a thin wrapper around the plugin name (`<plugin>-marketplace`, `<plugin>-local`). Metadata (description, owner, tags, keywords, category) is declared on the marketplace entry inline; some authors place a top-level `description` directly on the marketplace object, others wrap it under a `metadata.{}` object. `metadata.pluginRoot` is omitted because the plugin already lives at repo root. `$schema` may or may not be present — when absent, schema-aware editors lose autocomplete. Constrains versioning to a single track and any pinning has to come from the plugin source rather than from the catalog. The "-local" suffix variant signals "developing in place" — users see the suffix in `/plugin install <name>@<marketplace>`.

### Multi-plugin owned-aggregator marketplace

A repo-root `.claude-plugin/marketplace.json` lists N plugins under `plugins/<name>/`, each with its own `.claude-plugin/plugin.json` and source tree. Every entry uses a relative source (`./plugins/<name>`); the owner authors all listed plugins. Appropriate when one team ships a coordinated catalog. Constrains release cadence (one repo, one tag stream) and creates per-entry vs per-plugin version-sync surface that needs custom validation. Top-level fields are `name`, `owner`, optional `$schema`, and a `plugins` array; some authors wrap a `metadata` object carrying `description` and (rarely) `pluginRoot`.

### Pure external aggregator manifest

The repo holds only `marketplace.json` + LICENSE + README + minimal CI; every plugin is sourced externally via `url` (full clone with `sha` pin), `git-subdir` (path into an upstream monorepo), or `github` (subpath into a sibling repo). The repo authors zero plugin content — it's a denormalized index. Appropriate as a community directory or curated mirror. Constrains the field surface that survives the aggregator boundary (only `name`, `description`, `source`, `homepage`, occasional `category` are preserved); upstream `version`, `author`, `license`, `dependencies`, `tags`, `strict`, `skills` are dropped and resurface only after install.

### Standalone repo without a marketplace

The repo ships only `.claude-plugin/plugin.json` with no `marketplace.json`. Installation is local-directory via `claude --plugin-dir <path>` or out-of-band: users clone the repo and edit their own MCP host config manually. Equivalent to `source: "relative"` if someone re-packaged the repo into a marketplace later. Loses the marketplace surface entirely — no `source`, `strict`, `category`, or channel pinning to declare. Consumers must track commit SHAs themselves; "latest main" is the only pointer. Appropriate when the author treats the work as a portable MCP server first and a Claude Code plugin only secondarily — but it means the plugin cannot be installed by `/plugin marketplace add` workflows, and the load-bearing config is whatever `.mcp.json` template the README tells the user to paste into their own project.

### Single root manifest plus nested per-plugin manifest

A second self-contained `.claude-plugin/marketplace.json` lives inside one of the plugin directories, declaring that single plugin as a standalone marketplace with `metadata.pluginRoot: "."`. The same plugin is reachable two ways — as an entry in the aggregator's root manifest and as the only entry of its own nested marketplace. Suits a host repo that vendors a partner's plugin while letting the partner upstream the same directory to their own repo as a self-contained marketplace.

### Dual-publishing one manifest under two paths

The same JSON object is placed at `.claude-plugin/marketplace.json` (for Claude Code) and `.github/plugin/marketplace.json` (for GitHub Copilot CLI) — byte-identical files, two discovery paths. Targets two agentic CLIs from one source without maintaining parallel manifests. Drift between the two copies is a manual-discipline risk; nothing automated keeps them aligned.

### Top-level `metadata` wrapper

Whether the manifest opens with a `metadata: { ... }` object (carrying `version`, `description`, optional `pluginRoot`) or jumps straight to `name`/`owner`/`plugins`. The wrapper is conventional for partner-style and single-plugin marketplaces; large primary-owned aggregators sometimes omit it entirely. When the wrapper carries a `version` it tends to drift — set once at marketplace birth and rarely bumped against release-tag advances, so consumers reading it see a stale value relative to git tags. `metadata.version` can also serve as a catalog-wide release tag covering plugins that carry no `plugin.json` of their own — a single tag (`v1.0.0`) covers the whole catalog when individual plugin versioning would be redundant. No per-plugin granularity then — every carved plugin moves at the catalog's pace.

## Plugin source binding

How the marketplace entry locates the plugin manifest — relative path, vendored subtree, externally-pulled source, or skill-carving over a shared root.

### Relative same-repo path

`source: "./"` (self-reference) or `source: "./plugins/<name>"` names a directory inside the marketplace repo. The plugin payload travels in the same git history as the manifest. Pairs naturally with single-plugin marketplaces where the catalog and the plugin share one repo, and with owned-aggregator shapes that carve one tree into many entries. With `strict: false` set explicitly, the entry permits components beyond canonical roots (root-level `CLAUDE.md`, `SKILL.md`, custom directories like `prompts/`, `algorithms/`, `templates/`). With `strict` left default-true, the manifest at `.claude-plugin/plugin.json` carries the entire registration burden. Constrains the marketplace and plugin to one repo, one tag stream; every plugin moves on the marketplace's release cadence. The whole repo becomes the plugin payload at install time, including non-plugin assets (docs, benchmarks, tests, templates) — plugins on this path either accept the bloat or ship their own slimming utility.

### `source: "github"` with `ref` pinning

The marketplace entry references a GitHub repo by `repo` and `ref`. When `ref` is set to a moving branch (e.g. `main`), every install resolves to whatever tip-of-branch is at install time — no pin story, users always get latest. Implies `strict: true` (default) so the plugin manifest must live at the canonical `.claude-plugin/plugin.json` path inside the source. Variant `{source: "github", url, path}` binds to a subdirectory of a sibling repo where the plugin tree lives apart from the rest of the source (e.g., binaries and aggregator metadata in different repos). Effectively under-used relative to the `url` form — surfaced rarely across the corpus.

### `url` clone with `sha` pin

`source` is an object `{url, sha}` cloning an external repo at a specific commit. SHA pinning is universal in this path — pinning is the contract. Appropriate when aggregating external plugins; produces deterministic consumer state per marketplace snapshot. Constrains the aggregator to a sync workflow that updates SHAs on cadence. A `url`-source entry without a `sha` field accepts whatever is at HEAD of the upstream repo — non-reproducible installs that surface as drift from convention rather than an intentional "track main" choice.

### `git-subdir` into upstream

`source` is `{source: "git-subdir", url, path, ref [, sha]}` reaching into a path inside an external monorepo. `url` is mixed in practice — bare `owner/repo` slug or full `https://`. With a `sha` pin this is the only source kind that gives reproducible installs across time; with only `ref` defaulting to `main` it floats with upstream. Combined with bot-maintained SHA bumps (see *Source-pin maintenance*), this is the recipe for a curated catalog of upstream content with predictable refresh cadence. Constrains determinism: branch-floated entries move whenever upstream pushes.

### Vendored-partner subtree

Plugin entries point at `./<root>/<partner-name>` directories whose code is authored by an external partner but lives inside the host repo's tree, with the partner's own LICENSE and author attribution. Distinct from external `url`-source entries — partner code is vendored into the host's tree rather than pulled remotely. Sync mechanism (manual pull vs scripted) is not visible from the repo content alone.

### Skill-carving via shared root + `skills` override

Multiple distinct marketplace entries set `source: "./"` (the repo root) plus `strict: false` (disabling validation of a `.claude-plugin/plugin.json` at the root) plus `skills: ["./<skill-dir>"]` on the entry itself. The marketplace entry replaces `plugin.json` for skills — supplying name, description, category, tags directly — and lets one repo host many skills without a per-skill `plugin.json` wrapper. Two adoption shapes coexist: single-skill carves from a shared repo root (three sibling plugins all reading from the same root, each carving exactly one skill directory) and hollow umbrellas where the entry carries full component config (e.g., `lspServers: {...}`) and the plugin directory holds only `README.md` + `LICENSE`. Trade-off: no per-skill versionable manifest; bumping a skill's version requires re-releasing the whole repo.

### Mixed-provenance composition

A single `plugins[]` array hosting in-repo, vendored-partner, and externally-pulled entries simultaneously — three provenance tiers in one manifest. Distinct from pure inline marketplaces or pure aggregator marketplaces. Allows the marketplace to be both author-of-record (for in-repo content) and broker-of-record (for external content). Constrains the bump/release story per source kind; only `git-subdir` (with `sha`) is reproducibly pinned.

## Plugin discoverability metadata

How the plugin makes itself findable beyond raw repo identity — categorization, keywords, and tag dimensions surfaced for marketplace browsing. Distinct from manifest layout: this concerns the content of the metadata fields, not their location.

### Multi-dimensional (`category` + `keywords` + `tags`)

All three dimensions populated for a single plugin, giving overlapping facets for marketplace browsers. `keywords` is the long form (project-specific terminology, ~10 terms), `tags` shorter and ecosystem-oriented (`claude-code`, `cursor`, `codex`), `category` a single bucket. Increases discoverability surface area but also creates synchronization burden — three lists drift independently. In practice `tags` and `keywords` are often byte-identical duplicates: the author either doesn't know they serve different purposes or is hedging across tooling that may read one and not the other.

### Category + tags pair

Every entry carries `category: "<single-string>"` plus `tags: [...]`; `keywords` unused. Uniform across all entries; suits a focused-domain marketplace where one category fits all and tags differentiate within it.

### Category-only with deep-link homepage

Each entry carries a single `category` enum value plus a `homepage` deep-linking to `/tree/main/plugins/<name>`. No `tags`, no `keywords`. Discoverability rests on category enum + name + description. Appropriate when the catalog is small enough that browsing-by-category beats keyword search, and when the author wants a controlled vocabulary.

### Keywords-only

Only `keywords` populated; no `category`, no `tags`. Minimal categorization — the plugin relies on its name and description to surface in search rather than facet-filtering. GitHub repo `topics` may also be empty, so external indexing also has nothing to grip.

### Description-only with sparse opt-in category

Only `description` is universal across entries; `category` appears on a small minority (≈3% in one mirror) with inconsistent capitalization (`development` vs `Developer Tools`). No tags, no keywords. Appropriate when the catalog is too large for any author-supplied taxonomy to stay coherent, but produces an uncontrolled vocabulary even among the opt-in subset.

### Mixed-by-origin metadata

Different field sets per provenance tier in one `plugins[]` array — primary-owned entries use only `name` + `source` + `description`; vendored-partner entries add `author.name`; externally-pulled entries variably add `category` and `homepage`. No uniform shape across the array, which makes client-side schema validation awkward but reflects that the marketplace acts as an aggregator over heterogeneous sources.

### Cross-file category drift

`category` declared on both the marketplace entry and `plugin.json` with no automated sync — the two values drift (e.g. `"mobile-development"` on the marketplace entry vs. `"development"` on `plugin.json`). Unlike `version`, which is commonly guarded by sync scripts, `category` has no enforcement, so drift goes unnoticed.

## Version authority

Where the canonical version of the plugin lives and how copies stay in sync across the artifacts that need to declare it.

### Single-file authority (`plugin.json` only)

Version is declared once in `plugin.json`. Marketplace entries omit `version` entirely (no duplication risk). Simplest invariant — no sync needed. Drift-free by construction. Appropriate when the marketplace is just a routing layer and Claude Code reads version from `plugin.json` at install time, with no sub-package, no compiled artifacts, and no marketplace manifest of its own. The cost is paid back when a second version source is added later. Per-plugin discipline only — `plugin.json` may itself drift from a CHANGELOG or a SKILL.md frontmatter version field maintained by the same author. CI scripts may parse marketplace entries and warn if a `version` is missing, surfacing intent without enforcing it.

### Two-file authority synced by script

`plugin.json` is authoritative; `marketplace.json` mirrors it. A `sync-versions.sh` (or `bump_version.py`) script (run via pre-commit hook plus CI) compares the two and fails on drift. The script can also regex-scan source for hardcoded version literals (regression guard against re-introducing inline `version: "x.y.z"` strings the runtime is supposed to read from a manifest) and validate that the new version is a legal semver bump from the previous.

### Multi-file with bump script as enforcer (multi-registry)

Version lives simultaneously in `server.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and a regex-pinned arg in `.mcp.json` (e.g. `uvx mcp-outline==<ver>`). A `scripts/bump_version.py` rewrites all four atomically and validates semver-bump legality. Appropriate when the repo publishes to multiple registries (Claude Code marketplace + MCP registry + PyPI) that each demand the version in their own manifest format. The script is the single source of truth at author-time; structural drift is prevented by always running it instead of editing files individually. CI does not necessarily re-run the validator, so a manual edit to one file leaves the others behind silently.

### Multi-runtime fan-out (single source compiled to N artifacts)

A single source file (`plugin.universal.yaml`) is declared the source of truth and compiled by an external tool into per-runtime manifests (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, plus the `hooks.json` family). Five-plus version copies in the tree at any time. The compiler is not vendored or pinned, so the compile step is a user-side build no CI verifies — observed drift in practice (universal yaml at one version while compiled artifacts have moved on).

### Independent semver streams (sub-package versioning)

Multiple semver tracks coexist in one repo: the plugin itself, and one or more sub-packages (Node MCP server with its own `package.json`, etc.). Each bumps independently with its own changelog discipline. CHANGELOG explicitly reconciles them ("MCP server bumped to X.Y.Z while plugin is at A.B.C"). Plugin-level sync scripts do NOT cover the sub-package — it's intentionally outside the synchronized set, with its own release cadence.

### Multi-file hand-synced (no enforcer)

Two-to-five copies of the same version literal hand-maintained across `plugin.json`, marketplace entry, marketplace metadata, `package.json`, `pyproject.toml`, `.codex-plugin/plugin.json`, root-level `VERSION` file, and CHANGELOG. No automation enforces equality; drift is observed in practice (CHANGELOG top entry diverging from manifests during in-flight rebrands; pyproject Python-package version diverging from plugin version; CHANGELOG documents 2.1.0 while `plugin.json` still reads 1.0.0). Common in personal/early repos before tooling is added; appropriate as a transitional state when consolidating onto a single source has not yet happened.

### Cross-ecosystem version sprawl

A release script enumerates many version-bearing files (one observed sample lists 17: `package.json`, `package-lock.json`, multiple `AGENTS.md` locale variants, `agent.yaml`, `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, sibling-ecosystem manifests for Codex/OpenCode/Cursor/Gemini, README locales, architecture docs) that must move atomically. Appropriate when distributing the same plugin across multiple AI-harness ecosystems. Constrains release engineering: adding a new version-bearing manifest requires editing the script; CI tag-verification typically only checks one file, so drift between the others isn't caught.

### Marketplace-side pin via source ref

In aggregator marketplaces, `source.sha` (for `url`) or `source.ref` (for `git-subdir`) is the version contract. Upstream `plugin.json` versions are not surfaced. Appropriate when the marketplace cannot trust upstream version discipline. Constrains the user: the only pinning surface is the source ref the aggregator sets.

### Tag-stamped at release time

A release workflow extracts `version` from a `plugin-v*` tag name and writes it into `plugin.json` during packaging. One-way coupling from tag to manifest ensures consistency at the tagged commit, but intermediate `plugin.json` changes (between tags) ship without the validator.

### Marketplace `metadata.version` as catalog-wide

`metadata.version` covers all plugins simultaneously when individual entries have no `plugin.json` and no entry-level `version`. Single coarse version for the whole catalog; appropriate when catalog and content release together.

### Pinned manifest version, floating release tag

Every `plugin.json` holds a hardcoded version (e.g., `"1.0.0"`) regardless of release cuts; the release tag (`v1.1.1`) lives only on git tags and release-asset filenames. `plugin.json` is treated as written-once-at-introduction; consumers' source of truth is the tag.

### Deliberate divergence: wrapper vs underlying binary

`plugin.json.version` tracks the plugin wrapper release; the underlying binary version floats to upstream HEAD via runtime resolution. Designed to let the binary iterate without forcing plugin bumps. Distinct from a drift defect — the manifest declares "wrapper 1.5.0" while the binary it installs is whatever is freshest. The dual-tag-namespace release mechanism (see *Tag and release lifecycle*) supports this directly.

### No plugin-level version

Skill-carving entries have no `plugin.json` at all — only the marketplace entry and `SKILL.md`. There is no per-plugin version concept; the only versionable artifact is the marketplace tag covering all skills together. Or the version field is cosmetic — declared but no automation verifies bump-on-change, no pre-commit hook, no CI gate, no tag-vs-version assertion. Plugins ship at `0.1.0` while peers move ahead independently; breaking changes can land without any version bump.

### Stale fallback constants in code

Bin scripts and hooks read a `VERSION` file with a hardcoded fallback literal for "VERSION file unreadable" — but the fallback drifts from the current version over time, so a broken install displays a number that may be many versions out of date. A symptom of the multi-source version problem: even the centralization attempt embeds a copy.

## Channel distribution

How users pin to a specific revision of the plugin — release-branch splits, tag handling, channel duplicates, or a self-update mechanism baked into the plugin itself.

### Single-channel tag-on-main

No release branch, no stable/latest split — `main` IS the release branch. Tags live on main commits. Users pin via `@<marketplace-name>` in the install command; the marketplace pulls from main HEAD whatever was last published. Acceptable for low-cadence plugins; on high-cadence repos, on-main bumps can ship through the marketplace without producing a tag, leading to "tag count << version count" gaps. Dominant posture across the corpus — consumers implicitly track HEAD.

### Single tag with main drift

A single annotated tag (`v1.0.0`) exists on `main` but `main` continues to advance past it. Without a tag-pinning install path (`@v1.0.0` semantics), the tag is effectively a snapshot artifact rather than a channel. A clear anti-pattern when per-plugin `plugin.json` versions advance (e.g., `1.0.1`, `1.1.0`) without follow-up tags — users pinning the only tag get stale plugins indefinitely.

### No pinning surface

No tags, no release branches, no marketplace channel — the only pointer is whatever main HEAD happens to be at clone time. Any consumer has to track commit SHAs out-of-band. Common in early-stage / never-released repos.

### Sync-PR cadence with no tags

The mirror has zero tags; "release" is implicit in each merged sync PR. Sync branches (`sync/manual-YYYY-MM-DD`, `sync/auto-vendor`) merge into main on a weekly batch cadence. Appropriate for pure aggregators backed by an internal review pipeline. Constrains consumers: the only stable handle is a marketplace-repo commit SHA, which the standard install command doesn't capture by default.

### SHA pinning per external entry

For external `url`-sourced or `git-subdir`-sourced plugins, the `sha` field on each entry acts as a per-plugin pin — the marketplace itself tracks HEAD but each external plugin is frozen at the SHA the maintainer chose. Effectively a per-entry channel pin without a global stable/latest split. Reproducibility lives inside the source kind, not on the manifest as a whole.

### npm registry as de facto channel substrate

A Node-based installer (`bin/install.cjs`) is published to npm so users can `npx <plugin>@latest` or pin `npx <plugin>@<version>`. Versioning effectively delegates to npm's package versioning rather than git tags. Appropriate when the plugin has a Node toolchain anyway; constrains the plugin to publish releases to npm manually, parallel to the marketplace install path. Creates a third install channel alongside marketplace and direct-clone paths — same plugin, different version stories per substrate.

### SessionStart self-update

A SessionStart hook performs `git fetch` + `git merge --ff-only origin/main` against the plugin's own clone, with a 24h cache and an opt-out env var. Two install modes handled by one hook: when the plugin is a git clone (Codex / OpenCode / self-hosted), the hook auto-updates; when installed via a marketplace (Claude / Cursor), the hook instead emits a "run `/plugin update`" notice. Effectively turns SessionStart into a soft auto-update channel for non-marketplace installs.

## Plugin-component registration

How the plugin tells Claude Code (and sibling runtimes) where its skills, commands, agents, and hooks live — explicit path arrays vs. convention-based discovery.

### Convention-based default discovery

`plugin.json` carries identity/metadata only (`name`, `description`, `version`, `author`, `keywords`, `homepage`, `repository`, `license`); component locations are implicit per Claude Code's directory conventions (`skills/`, `agents/`, `commands/`, `hooks/hooks.json`, `.mcp.json`, `.lsp.json` at repo root). Lowest manifest-side ceremony. The dominant choice across most samples. Fails when the plugin must satisfy a runtime that requires explicit paths (Codex, Cursor) — those runtimes need a sibling `plugin.json` with explicit `skills` and `agents` keys, so single-runtime convention discovery does not generalize.

### Explicit path arrays in plugin.json

`plugin.json` declares each component category by path (`skills`, `agents`, `commands`, `hooks` arrays; `mcpServers` as an inline object). Higher manifest cost but every component location is grep-able from one file, and the plugin can reference targets outside the default directories. MCP servers can be inlined in `plugin.json.mcpServers` rather than externalized to a `.mcp.json`. Used when component count is large (one sample lists 80+ agent paths) and the manifest is treated as the authoritative inventory — mismatches between the array and filesystem (e.g. one extra unreferenced agent file) become discoverable drift signals.

### Explicit path string for one component

`plugin.json` declares one component's path explicitly (e.g. `"skills": "./skills/"`) even when the path matches default discovery. Redundant but valid. Often appears alongside the default-discovery pattern when only one component needs a non-default location and the author opts to be explicit about all of them.

### Asymmetric registration: file paths for agents, directory for skills/commands

`agents` is an enumerated list of `./agents/<name>.md` paths (per-file); `skills` and `commands` use directory references like `["./skills/"]`. The asymmetry tracks an observed validator restriction (`agents: Invalid input` when a directory is passed) that does not apply equally to skills and commands. Appropriate when validator behavior is asymmetric; produces verbose `agents` blocks that grow with the agent count.

### Inline `mcpServers` config in `plugin.json`

`mcpServers` is declared inside `plugin.json` itself rather than in a separate `.mcp.json`. Two shapes coexist: object form (`{"<ServerName>": {"type": "http", "url": "..."}}`) and string-URL form pointing at an `.mcpb` bundle hosted externally. The object form is conventional; the string-URL form is docs-silent and may be a loader-specific extension that triggers a remote fetch. Used when the plugin's only component is an MCP server (no skills, no commands) — keeps the whole plugin definition in one file. When both inline and external `.mcp.json` forms exist, they are two sources of truth with no automation reconciling them.

### `.mcp.json` sibling file

`.mcp.json` lives alongside `plugin.json` carrying the MCP server configuration separately. Suits plugins where MCP setup is the bulk of the plugin's surface and benefits from being its own file. Loaded by the install flow without an explicit `plugin.json` reference — well-known filename at well-known path.

### Hooks at well-known path without `plugin.json` reference

`hooks/hooks.json` sits at a known path and is loaded by the install flow without an explicit `plugin.json` reference. Path is fixed, not configurable.

### Empty hooks scaffolding

`hooks/hooks.json` exists but contains `{}` or `[]` — no hooks registered. Shows up uniformly across plugins from one marketplace, suggesting template residue or forward-compat scaffolding rather than active hooks. Either an anti-pattern (dead files) or a deliberate "extension point" convention; the corpus shows no documentation explaining the choice.

### Marketplace-entry-only definition (no `plugin.json`)

Plugin directory has no `.claude-plugin/plugin.json`; the marketplace entry's own fields (`skills`, `lspServers`, `version`, etc.) are the entire definition. Requires `strict: false` on the entry. Two shapes: skill-carving (entry's `skills: ["./<dir>"]` is the only registration) and hollow umbrella (entry's `lspServers: {...}` is the entire plugin). Trade-off: centralizes definition in the manifest at the cost of independent plugin-level versioning.

### Mixed convention per runtime (per-runtime manifests)

Repo hosts multiple `*-plugin/` directories (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`) — each with its own `plugin.json`. Claude relies on directory convention; Codex and Cursor's manifests explicitly set `"skills": "./skills/"` (and Cursor adds `"agents": "./agents/"`) because those runtimes require explicit paths. The single source of truth (universal YAML) compiles to all three.

### Marketplace-root shared bin via per-plugin symlink

`bin/<wrapper>` at the marketplace root (not under any individual plugin), with each consuming plugin shipping a symlink at `plugins/<name>/hooks/<wrapper>` pointing at the shared file. Author's documented intent is DRY at the marketplace level — one wrapper, many plugin consumers. See *Bin-wrapped CLI distribution* for the constraint this creates around symlink target form (relative survives the install copy; absolute breaks on any non-author machine).

## Component types in use

Which Claude Code component types — skills, commands, agents, hooks, MCP servers, monitors, output styles, bin, LSP — actually appear across plugins in a marketplace. Component-mix observations distinct from registration mechanism.

### Skills

Universal across most observed plugins. Every plugin tends to ship at least one `skills/<name>/SKILL.md`. The dominant component type. Some samples place loose `skills/<name>.md` files at the skills/ root with command-style frontmatter, which is non-canonical and appears to be a misunderstanding of skills-vs-commands or leftover scaffolding.

### Commands

Present in some plugins as a legacy form. Per documentation in mid-migration repos, "the legacy `commands/` format still works but new plugins should use `skills/*/SKILL.md`." Frontmatter `name`, `description`, `argument-hint`. Body instructs Claude on what to do (e.g., call a specific MCP tool with the argument). Appropriate when one user-invoked entry point is the primary affordance.

### Agents

Variable adoption — common in workflow-heavy plugins, rare in content-driven ones. Ship as `agents/<name>.md` files with frontmatter declaring identity, model, and tool permissions. Tools listed as plain names rather than permission-rule syntax. See *Agent declaration conventions* for frontmatter detail.

### Hooks

Often absent entirely. A marketplace can ship dozens of plugins and zero `hooks.json` files. Aligned with a "no infrastructure" design posture; absence of hooks correlates with absence of session-start install, tool-use enforcement, monitors, and session-context-loading mechanisms. When present, see *Tool-use enforcement (hooks)* and *Session context loading* for the actual mechanisms.

### MCP servers

Common — declared either via inline `mcpServers` in `plugin.json` or via a sibling `.mcp.json`. Plugin's value is bridging an external service to MCP. See *Server runtime (MCP)* for execution-path detail.

### bin

Variable adoption. Used when the plugin distributes a binary CLI through shim wrappers. Absent when the plugin is "just markdown and JSON." See *Bin-wrapped CLI distribution* for shapes.

### LSP config

`.lsp.json` — minimal-viable plugin can ship only `.claude-plugin/plugin.json` + `.lsp.json` + README, with no skills/commands/hooks/agents at all. Demonstrates the floor of plugin footprint.

### output-styles, monitors

Not observed in any sample. Equivalent functionality (notification, monitoring) is delivered via Stop and PostToolUse hooks where present. See *Live monitoring* and *Notification surface*.

### Component composition shapes

Plugins cluster into four common composition shapes: skill-only payload (only `skills/<name>/SKILL.md` plus optional `references/`, `assets/`, `scripts/` — appropriate for content-driven domain knowledge); MCP-only payload (only `.mcp.json` or inline `mcpServers` plus identity metadata — appropriate when the plugin's value is access to a hosted backend); mixed skills + commands + agents + hooks + MCP (default-discovery `plugin.json` is the wiring; conventions handle the rest — appropriate for plugins that wrap a workflow rather than expose a single resource); LSP-server-only "hollow" plugin (plugin directory holds only `README.md` + `LICENSE`; the marketplace entry's `lspServers` block is the entire plugin definition — one plugin per language server).

## Agent declaration conventions

Frontmatter fields on agent files — what gets declared, how tool permissions are scoped, and what runtime knobs are exposed.

### Rich frontmatter with embedded examples

Agents declare `name`, `description` (multi-paragraph YAML literal block with `<example>` / `<commentary>` XML blocks and "Triggers:" keyword lists), `tools` (per-agent comma-separated tool list), `model` (`sonnet` / `opus`), plus optional knobs — `effort: high` (reasoning budget), `memory: true` (cross-session memory enabled), `color`, and `skills` (in-plugin skills referenced by bare name). Description content drives the agent matcher; examples function as trigger-rich few-shot prompts at metadata level.

### Frontmatter with model + JSON-array tools

Frontmatter fields `name`, `description`, `tools` (JSON array of plain tool names like `["Read", "Grep", "Glob", "Bash"]`), `model` (e.g., `opus`, `sonnet`). No permission-rule syntax (no `Bash(uv run *)` style). Appropriate for tool-allowlist semantics where any invocation of the named tool is acceptable.

### Frontmatter with space-separated tools and `effort` field

Frontmatter uses space-separated tool names (`tools: Read Grep Bash`), plus a non-standard `effort: max` field, alongside `model`. Appropriate when targeting a specific harness convention; produces ambiguity for parsers that expect YAML-list syntax.

### Minimal frontmatter, parent-session permissions

Agents declare only `name`, `description`, `model: inherit`, and (optionally) `memory: user`. No `tools` allow-list — the agent inherits the parent session's permissions. Smaller frontmatter surface; pushes permission decisions out to the user-level Claude Code config rather than scoping per-agent.

### Worktree-isolated agent with hard turn cap

Agent frontmatter declares `isolation: worktree` plus `maxTurns: <N>`. The agent runs in a git-worktree isolation envelope (presumes the invoking session's project is a git repo) and is hard-capped at N turns. Constrains other parts: tools list mixes fully-qualified MCP names with built-in tools; the hard turn cap means long-running research can truncate mid-flow with no documented recovery.

### MCP-server allowlist binding

Agents declare `mcpServers: [<server-name>]` to bind to a specific MCP server's tools, alternative to listing tools individually. Appropriate when the agent's purpose is one MCP-driven workflow.

### Defensive prompt directives in agent body

Agent body carries the prompt — sometimes including defensive directives like "USE THE TOOL-CALLING INTERFACE … NEVER simulate, write out, or fake function calls" guarding against model hallucination of tool calls. Caller-supplied parameters can be encoded in prose (e.g., the agent body declares quick/medium/very-thorough modes the caller names at invoke time).

### Custom agent frontmatter extensions

Standard fields (`name`, `description`, `model`, `tools`) coexist with non-standard ones — `stakes` (low/medium/high, borrowed from the 12-Factor-Agents discipline), `subagent_type` namespaced as `<plugin>:<name>`, plus `effort`, `maxTurns`, `disallowedTools`, `color`, `memory`. The plugin's internal readers consume these; the harness ignores them. Appropriate when the plugin has internal agent-orchestration logic that needs richer per-agent classification than the harness provides. Constrains portability: validators that enforce only the canonical schema reject these, so the plugin maintains its own validators. Non-standard fields like `allowed-prompts` with nested `{tool, prompt}` pair lists are also observed but not in the documented Claude Code reference — possibly experimental, possibly silently ignored.

### Bare-name in-plugin skill references

Agents reference skills by bare name (`skills: rn-testing, rn-best-practices`) rather than the qualified `plugin:skill` form. Correct for skills in the same plugin; future cross-plugin reuse would need qualification. Same field shape as agents declaring tools, but distinct semantics — references resolved against the local skill directory.

## Skill-frontmatter extensions and dispatch

Non-canonical SKILL.md frontmatter fields and dispatch mechanisms a marketplace adopts beyond the documented schema.

### Frontmatter `context: fork` + `agent: <name>`

A SKILL.md frontmatter declares `context: fork` and `agent: campaign-auditor` to drop into an isolated sub-agent context. The named agent file lives alongside `skills/` in `agents/<name>.md`. Appropriate when the skill's work warrants a clean context with restricted tools. Constrains skill author: the agent must exist as a sibling component in the plugin.

### `user-invocable: false`

Marks a skill as composition-only — used by other skills, not exposed as a slash command. Not in the core plugin-reference frontmatter docs; appears to be a host-environment-specific extension.

### `compatibility:` prose

Free-form prose declaring platform prerequisites (e.g., "Requires Cowork desktop app environment"). Not in the canonical schema; another host-environment extension.

### `allowed-tools` as scalar

Single-string scalar (e.g., `allowed-tools: Bash`) rather than a list, gating which tools the skill may invoke.

## Tool permission syntax inside agents

How the agent restricts which tools (especially MCP tools) it can call.

### Plain tool-name list

Comma-separated tool names — `Bash, Read, Write, Edit, Glob, Grep`. No permission-rule syntax (`Bash(uv run *)`-style). Simplest form; cannot scope `Bash` to specific commands at the frontmatter layer.

### Fully-qualified MCP tool names

Each MCP tool listed by full name (`mcp__academic-search__search_papers`) rather than wildcard. Tighter scoping than `mcp__academic-search__*` but high maintenance — adding a tool to the server requires updating each agent's allow-list. Compare with `allowed-tools` on commands, which often use the wildcard form even when the agent in the same plugin uses fully-qualified names — two conventions for the same kind of access scoping.

## Server runtime (MCP)

The execution path that actually serves MCP requests when the plugin is active.

### Pinned PyPI wheel via `uvx`

`.mcp.json` declares `uvx <pkg>==<exact-ver>` as the launch command. `uvx` (Astral's ad-hoc runner) fetches the exact pinned wheel into its cache (`~/.cache/uv/`) per invocation. Appropriate when the author publishes the server independently to PyPI and wants the plugin to lock to a specific wheel. Constrains: any Python 3.10+ interpreter on the host accepted (pure-Python wheel); no plugin-side venv to manage; old plugin tags will always pull old wheels even after upstream patches; no SessionStart install hook needed. The plugin is effectively a thin client of PyPI.

### Local venv built by SessionStart hook

A `scripts/setup.sh` invoked from `hooks/hooks.json` SessionStart creates `${CLAUDE_PLUGIN_DATA}/venv`, runs `python3 -m venv`, upgrades pip, then `pip install -r requirements.txt`. Appropriate when the plugin is the server, not just a client of one — runtime code lives in the repo and needs a Python environment to run. Constrains: `python3` from PATH (no version pin); install must complete before the MCP server is launched; venv path must thread through to the MCP launch command (commonly broken — README's "install from source" creates `<checkout>/.venv` while the SessionStart hook creates `${CLAUDE_PLUGIN_DATA}/venv`, two parallel venvs neither aware of the other). System-tool dependency on `shasum` (BSD/macOS) vs `sha256sum` (Linux) — no fallback observed.

### In-place stdlib script (no installer)

The Python script (e.g., `scripts/spectl.py`) is run directly via system `python3`, importing only stdlib (argparse, json, os, re, shutil, string, sys, datetime, pathlib, random). No venv, no `uv run`, no pip-install. Appropriate when the author deliberately constrains the plugin to stdlib to eliminate install friction. Cost: a `pyproject.toml` may declare `requires-python = ">=3.14"` for a `uv sync` path that no runtime code path actually exercises — the floor is functionally unenforced because the script's stdlib-only imports work on much earlier Python.

### Runtime-fetched server via `npx -y`

An MCP server entry uses `npx -y @scope/server --stdio` to fetch and run a Node MCP server on demand. Ad-hoc runtime fetch with no caching managed by the plugin. Trade-off: zero install ceremony, network round-trip on every session.

### Remote HTTP MCP

Plugin's tools are reached by HTTP MCP at a hosted URL. No local process, no command, no env vars beyond auth. The "dependency" is the provider's SaaS uptime and the user's subscription. Cleanest distribution shape — dependency installation simply doesn't apply.

### Docker-launched MCP server

`.mcp.json` declares `docker run <image>:<tag>` to launch the MCP server in a container. Pinned tag freezes the version; `latest` floats. Cross-role: Docker also surfaces under *Distribution channels* via ghcr.io image and under *Release automation* via the multi-arch build pipeline.

## Dependency installation

How runtime dependencies (Python packages, Node modules, system binaries) are installed when the plugin needs them, including where they live, how change is detected, and how failure is signaled.

### Zero dependencies

The plugin deliberately ships no runtime dependencies — hooks are capped at Node built-ins (`fs`, `path`, `crypto`, `child_process`). No `requirements.txt`, no `pyproject.toml`, no `package.json` at the plugin root. Install step disappears entirely. The constraint shapes everything downstream: hooks cannot use NPM ecosystem libraries, and any future dep would force the architecture to grow an install path. Trade-off is hand-rolled equivalents of common functionality (parsing, compression, etc.) inside the hook source.

### Delegated to PyPI runner

No plugin-side install state. `uvx` fetches the wheel on demand; the plugin directory holds no installed deps. No SessionStart install hook. Appropriate when dependencies belong to an upstream package the plugin only references. Failure mode is a standard MCP server launch failure — Claude Code reports the missing `uvx` or the unresolvable package; no plugin-specific error path.

### SessionStart-driven Python venv with hash gating

A `SessionStart` hook (`scripts/setup.sh`, `ensure-venv.sh` / `ensure-venv.ps1`, ~180s timeout in some samples) creates a venv under `${CLAUDE_PLUGIN_DATA}/venv/`, runs `pip install -r requirements.txt`, then on success copies `requirements.txt` to `requirements.stamp` (or computes sha256 → `requirements.hash`). Next session: `diff -q requirements.txt requirements.stamp` (or hash compare) skips re-install when unchanged. The stamp-write-after-success structure is the retry invariant: failures leave the stamp absent or stale, so the next session retries the diff path. On failure, the script emits `{"systemMessage": ...}` JSON with `exit 0` (never block); pip stderr redirects to `install.log`. Appropriate when the plugin owns its runtime and dependencies are non-trivial. Constraints: hash is over the declared-deps file, not a lockfile, so transitive-dep upstream patches are invisible; no Python minor-version stamping (a user upgrading Python keeps the old venv); `install.log` doesn't rotate; install location may not be where the MCP launch command points; `shasum` (BSD/macOS) vs `sha256sum` (Linux) is a fragility surface.

### SessionStart-driven dual-runtime install (Python venv + Node modules)

A single SessionStart shell hook handles both Python venv + `pip install -r requirements.txt` and Node `npm install` in the same script. Each manager is guarded by `diff -q` between the source manifest in `$CLAUDE_PLUGIN_ROOT` and a cached copy in `$CLAUDE_PLUGIN_DATA`. On `diff` miss, install runs and cache is refreshed; on install failure, the cached copy is `rm -f`'d so next session retries. Symmetric retry semantics across both ecosystems in one script. Distinct from per-manager hooks: one hook fans out to N managers with identical diff/retry shape. Refinements: `diff -q` is sensitive to source-vs-cache equality only — a flaky-network install that returns 0 but partially lands packages will leave an "in sync" cache that does not retry. `2>/dev/null` suppression on the install branches keeps stderr quiet to avoid corrupting the JSON channel the same hook uses for context injection, but loses corrective error messages. `python3 -m venv ... 2>/dev/null || true` makes venv-creation failure invisible — a user without `python3-venv` installed gets a silent no-op then a confusing "pip not found" downstream.

### Version-stamped persistent install with back-symlink

`node_modules` (or equivalent) installs into a stable location under `$CLAUDE_PLUGIN_DATA` (e.g. `$CLAUDE_PLUGIN_DATA/cdp-node_modules/node_modules/`) and a `ln -sfn` symlink back into `$CLAUDE_PLUGIN_ROOT/<expected-path>/node_modules` so relative `require` resolves. Solves two problems at once: the plugin cache is wiped on every Claude Code update (so installs into ROOT do not survive), and the runtime still expects modules at the in-tree path. A version stamp file (`$CLAUDE_PLUGIN_DATA/<dir>/.version-stamp` containing the sub-package's `package.json` version) is the change-detection key — reinstall triggers when stamp absent OR mismatched. Pre-scans for a dangling symlink from a previous persistent install and cleans it before falling back to a local install. Includes a stamp-flip-flop guard: skip persistent path when the runtime is unavailable (e.g. `node` missing), so an "unknown" version cannot be written.

### First-run pip-install in bin wrapper

The bin wrapper probes for a Python module (`python -c "import <module>"`) and on ImportError runs `pip install <pkgs> --quiet` against whatever `python`/`pip` are on PATH. No venv, no version pinning, no lockfile, no change detection beyond existence. Appropriate as the minimum viable Python-dep-install pattern. Constrains everything else: dependency isolation becomes the user's problem; PEP 668 externally-managed-environment errors surface to the user rather than being handled; `python` (vs `python3`) PATH assumptions break on Linux distros that ship only `python3`. Idempotent by retry (every invocation re-probes) but not hook-driven. The `.cmd` Windows counterpart cannot replicate `set -e` and silently swallows failed installs.

### Repo-local Node install via shell wrapper

`install.sh` (POSIX) and `install.ps1` (Windows) at repo root run `npm install --no-audit --no-fund` into a repo-local `node_modules`, then delegate to a Node-based real installer (`scripts/install-apply.js`). Existence-only change detection (`if [ ! -d node_modules ]`); no checksum stamping. Appropriate when the plugin predates the Claude Code plugin spec and needed its own user-facing install entry. Constrains: marketplace-flow installs bypass `install.sh` entirely; the path's completeness via the plugin runtime is uncertain.

### Bun install via Node packaging

`package.json` plus `bun.lock` declare Node deps; the npm-published installer runs `bun install` into the installer's working directory. Plugin-marketplace installs do NOT run `bun install` — only the npm install path does. This means features gated on `node_modules/` (Ink TUI, dashboards) silently fall back to plain text on a marketplace install. Appropriate when Node is the primary toolchain and npm is the distribution substrate; constrains the marketplace path to graceful degradation for everything Node-dependent.

### External CLI auto-install via vendor scripts and global package managers

System-level CLIs (e.g. `agent-device`, `maestro-runner`, `ffmpeg`) are installed during SessionStart by a family of `ensure-*.sh` scripts, each targeting one tool with its preferred install mechanism — `npm install -g` for npm globals, `curl -fsSL <url> | bash` (vendor install scripts) for standalone binaries, with `brew install` printed as a manual fallback when auto-install fails. Some scripts use `set -euo pipefail` for strict failure; others omit it to allow graceful fallback to local install. Lands tools wherever the installer puts them (`~/.maestro-runner/bin/`, npm global prefix), outside the plugin's own data directory.

### Lazy-download from project's own releases

Bin shims trigger a one-shot installer that hits the project's GitHub releases API (unauthenticated), filters tags client-side, picks a release, downloads platform-appropriate tarball/zip, extracts to `${CLAUDE_PLUGIN_DATA}/bin/`, writes a version stamp. Existence-only change detection: short-circuits if both binaries exist regardless of version. `mktemp`-based staging with `trap` cleanup so failed downloads leave the target dir untouched. No SessionStart hook involved — install fires on first invocation of the bin shim. Trade-off: zero session-start overhead but the first call pays the download time.

### Manual venv with documented commands

The plugin documents `python3 -m venv .venv && .venv/bin/pip install -r requirements-optional.txt` in README/CLAUDE.md and ships no auto-install mechanism. Optional deps live in `requirements-optional.txt` with a header explicitly invoking PEP 668. Appropriate when the dep surface is large, version-sensitive, and the author refuses to pollute the user's environment. Constrains user experience: "plugin installed" diverges from "plugin functional" — features silently degrade when optional deps are missing (e.g. ChromaDB falls back to grep). The plugin must tolerate every dep being absent.

### `requirements.txt` with manual user invocation

A skill ships `requirements.txt` with pinned versions; SKILL.md or a comment in the file instructs the user to run `pip install -r requirements.txt --break-system-packages` themselves. Reproducibility depends on user discipline; `--break-system-packages` is user-hostile on PEP 668-managed systems where no plugin-managed venv exists. No change detection, no retry, no failure signaling — entirely user-driven.

### No managed install (user prerequisite)

README states "Requirements: Python with scipy and numpy" or similar; plugin ships a script that imports the deps and crashes with `ImportError` if they're missing. No `requirements.txt`, no plugin-managed venv, no SessionStart install hook. User-side prerequisite is the entire install story.

### Inline `python3 -c` for ad-hoc scripting

Bash hooks pipe data through `python3 -c "..."` for JSON manipulation rather than declaring a Python dep. Relies on system Python 3 being present. Appropriate for tiny one-shot transformations in shell hooks; constrains the plugin to whatever standard library the system Python provides.

### Plugin-upgrade awareness via tmp-file stamp

A separate stamp at `$TMPDIR/<plugin>-last-version` records the plugin's own version, compared next session to detect plugin-level upgrades (vs. dep-level). On mismatch, emits a notice ("plugin upgraded from vX to vY; restart Claude Code to reinitialize MCP servers") to surface the MCP-subprocess-doesn't-auto-restart class of bug. `$TMPDIR` resets on macOS reboot, so the stamp survives a boot cycle but not a restart — accepted trade-off.

### Failure-signaling spectrum

Install failure can be signaled three ways: (1) **silent** — `2>/dev/null` + `|| rm -f` cache marker; the only feedback is a downstream import error at tool-invocation time; (2) **stderr with corrective command** — `WARNING: <component> deps failed. Run: cd <path> && npm install`, printed before the session banner so users see it; (3) **stamp-mismatch retry** — no stderr, but the stamp file is the durable signal; next session re-detects mismatch and retries. The choice constrains UX: silent fails disappear into runtime errors; stderr+corrective preserves the install attempt's exit code 0 (non-blocking) while still informing.

### No deps (pure manifest aggregator)

Repo ships only `marketplace.json` + LICENSE + README + a single CI workflow; nothing to install. Appropriate for pure aggregators.

## Bin-wrapped CLI distribution

Whether and how the plugin exposes user-invokable command-line entry points, including OS portability concerns.

### No bin layer (direct invocation)

The plugin exposes no user-facing CLI. Internal entry points are invoked by full path (e.g. `node ${CLAUDE_PLUGIN_ROOT}/src/parsers/pdf-parser.js`) from commands or hooks rather than via a `bin/` wrapper. MCP servers resolve via `.mcp.json`'s explicit `command:` path. Lowest portability burden, but no shell-discoverable entry points. Hook scripts the user runs (e.g., a manifest builder) live under plugin-local `scripts/` and are invoked from command markdown via raw shell — not wrapped, not registered. Aligned with the "no code" posture.

### POSIX shell wrapper with `${CLAUDE_PLUGIN_ROOT}` fallback

A short `bin/<plugin>` script resolves the plugin root via `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}` (or `sh`-portable equivalent using `dirname "$0"`), then `exec`s the underlying interpreter on a script inside the plugin. The fallback makes the same script work under Claude Code (env var set) and from a bare clone (env var unset) with no other changes. Canonical pattern, observed verbatim across multiple samples. Shebang varies: `#!/usr/bin/env bash` is typical; `#!/usr/bin/env sh` appears when the wrapper is intentionally bashism-free. POSIX-only — Windows requires a separate `.cmd` or `.ps1` pair. `CDPATH= cd --` guards against hostile `CDPATH` and dash-prefixed paths in the fallback branch.

### Bash + `.cmd` pair for cross-platform

POSIX `.sh`/no-extension bash wrapper plus a Windows `.cmd` batch file with the same behavior — `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..` for runtime resolution, `%PYTHONPATH%`, `%*` argument passthrough. PowerShell `.ps1` is not used as a runtime shim — only as a one-shot installer when present. Appropriate for plugins that genuinely target both platforms; constrains feature parity because `.cmd` cannot replicate `set -euo pipefail` and error handling diverges.

### Lazy-install bin shim with fallback chain

Small bash and Windows-batch shims (~600-800 bytes each) live in `bin/` and are auto-discovered by the loader (PATH integration by convention). Each shim checks for the real binary at `${CLAUDE_PLUGIN_DATA}/bin/<name>` (with `$HOME/.<plugin>/bin` fallback); if absent, runs an installer script (also in `scripts/` of the plugin) that downloads platform-appropriate binaries from the project's GitHub Releases, then re-execs. A separate "drop-in" shim layers fallback through co-located alternatives, then a system-installed binary, then the original tool — graceful degradation if anything breaks. Shebang `#!/usr/bin/env bash` with `set -euo pipefail`. Script-relative path resolution (`SCRIPT_DIR=...`) rather than `${CLAUDE_PLUGIN_ROOT}` reference. Self-recursion guarded by a marker string embedded in the shim that the installer greps for.

### Pointer-file shim invoked via `.mcp.json`

A `bin/python_shim.sh` (POSIX) + `bin/python_shim.ps1` (Windows) reads `${CLAUDE_PLUGIN_DATA}/python_path.txt` (written by the venv-bootstrap SessionStart hook), validates the path is executable, and `exec "$PY" "$@"` to run the requested server script. `.mcp.json` invokes via `bash ${CLAUDE_PLUGIN_ROOT}/bin/python_shim.sh <server.py>`. Appropriate when the venv interpreter path is OS-dependent and unknown until first session; decouples MCP registration from path encoding. Constrains: if the venv hook has never succeeded, `python_path.txt` is missing and the shim exits 127 with a corrective message; recovery requires the user to install the prerequisite and restart Claude Code. The PowerShell sibling exists but `.mcp.json` only references the `.sh`, leaving Windows users dependent on Git Bash or WSL.

### Multi-script bin family

A `bin/` directory contains many small per-purpose scripts (`pos-init`, `pos-config`, `pos-analytics`, `pos-sync`, `pos-telemetry`, `pos-update-check`, plus a Node installer) rather than one entry point. Each script handles one verb; hooks invoke them via full path. Appropriate when the plugin exposes a CLI surface with many independent operations to user and to internal hooks. Constrains permissions discipline: scripts invoked by full path do not require executable bits, so chmod handling is inconsistent (the npm-`bin`-declared file gets chmod from npm; sibling scripts do not).

### Marketplace-root bin with per-plugin symlink

`bin/<wrapper>` at the marketplace root is a stdlib Python script with `#!/usr/bin/env python3` shebang. Each consuming plugin ships `plugins/<name>/hooks/<wrapper>` as a git-tracked symlink (mode 120000) pointing at the shared file. Hook configuration invokes via `${CLAUDE_PLUGIN_ROOT}/hooks/<wrapper>`. The wrapper resolves the plugin name from `plugin.json` and the marketplace name by walking up to `.claude-plugin/marketplace.json`, then enriches its output with provenance metadata. Appropriate when multiple plugins in one marketplace want a shared executable without copy-paste duplication. Critical constraint: Claude Code installs by copying the plugin directory only, so the symlink target must be relative (e.g., `../../../bin/<wrapper>`) to survive the copy. Absolute symlink targets keyed to the author's home directory break on every other machine — the install ships dead symlinks. Observed in lower-discipline form, where the documented intent is correct but the committed symlink targets are absolute.

### Git-symlink bin wrappers (mode 120000)

`bin/<friendly-name>` files are committed as git symlinks (mode 120000) pointing to `../scripts/<real-name>.sh`. Provides user-friendly naming at the bin layer without duplicating script content; target scripts use `dirname "$0"`-based resolution which transparently resolves through the symlink to the real-file plugin root. Constraint: Windows-native git checkouts convert symlinks to plain text files containing the target path unless `core.symlinks=true` — silently breaks on Windows. Also depends on the target file having the executable bit set; one missing exec bit makes the bin entry broken-by-default for strict-perm consumers.

### Polyglot CMD/bash wrapper for cross-platform hook invocation

A single file (`run-hook.cmd`) interpreted differently by `cmd.exe` (Windows batch syntax) and by `bash` (via `: << 'CMDBLOCK' … CMDBLOCK` heredoc trick). Searches `C:\Program Files\Git\bin\bash.exe` and `C:\Program Files (x86)\Git\bin\bash.exe`, then `bash` on PATH; silently succeeds if none found. Hook script filenames are deliberately extensionless (`session-start`, not `session-start.sh`) to avoid Claude Code's Windows auto-detection prepending `bash` to any `.sh` command. Used internally by SessionStart, not as a user-facing CLI — but solves the same cross-platform invocation problem `bin/` would face.

### Single-file install + skill copy via standalone installer

`install.sh` / `install.ps1` at repo root for non-plugin install methods runs `pip install <subdir>/` and copies the canonical `SKILL.md` into the user's skills directory. Independent from the plugin-marketplace install path: same source tree, two install mechanisms, two copies of `SKILL.md` (root copy for standalone-install consumers; `skills/<name>/SKILL.md` for plugin-install consumers) maintained in parallel. Appropriate when the author wants to support both Claude-Code-plugin-installed users and standalone-skill-copy users from one repo; constrains single-source-of-truth because the same content must land in two places.

### Stale hardcoded paths after rebrand

A bin script targets a hardcoded path under `~/.claude/plugins/cache/<old-slug>/<old-slug>/<old-version>` rather than resolving via `CLAUDE_PLUGIN_ROOT`. After a project rebrand, the path is stale and the script silently no-ops. A refactor-rot signal: any bin script with a hardcoded cache path is a candidate for the env-var-resolution pattern.

## Plugin-runtime root resolution

How bin scripts and hooks find the plugin's installed location across substrates.

### `${CLAUDE_PLUGIN_ROOT}` env var with script-relative fallback

Bash scripts use `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}`; sh scripts use `dirname "$0"`-based equivalents; cmd files use `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..`. Canonical pattern across all bin and hook scripts in a sample. The fallback enables raw-clone development without invoking through Claude Code. Appropriate as the single resolution mechanism; deviations (hardcoded cache paths) are refactor-rot.

### Centralized inline-bootstrap dispatcher

Every hook command is ~1.5KB of inline `node -e "..."` boilerplate that re-implements `CLAUDE_PLUGIN_ROOT` resolution across a fallback chain (env var → `~/.claude` direct → six well-known plugin slug paths → versioned cache dirs), then hands off to `plugin-hook-bootstrap.js` which calls `run-with-flags.js {event-id} {handler-script-path} {profile-flags}`. Hook IDs use a structured `{lifecycle}:{scope}:{purpose}` taxonomy (e.g., `pre:edit-write:gateguard-fact-force`). Profile gating (`standard`, `strict`) lets users opt in or out of disciplines. Appropriate for plugins with many hooks and uncertainty about how reliably the host sets `CLAUDE_PLUGIN_ROOT`. Constrains: SessionStart specifically had to be extracted to a standalone file because inline `!` characters trigger bash history expansion and produce a visible CLI error header; the inline pattern is fragile across shell environments.

## Authentication and credential delivery

How user-supplied configuration (API keys, secrets, preferences) is declared in the manifest and consumed at runtime.

### Native `userConfig` with `${user_config.KEY}` substitution

`plugin.json` declares fields under `userConfig` with `description`, `sensitive: true|false`, optional `type`, `default`, etc. `.mcp.json`'s `env` block uses `${user_config.KEY}` substitution to translate user config into `CLAUDE_PLUGIN_OPTION_<KEY>` env vars consumed by the MCP server via `os.environ.get(...)`. Round-trip is observable: Claude Code prompts for the values at install time, stores them, substitutes into the env block, server reads them. Multiple variants observed:
- *Two-form referencing* — `.mcp.json` references each value twice per server entry — once via `${user_config.KEY}` substitution into config strings and once as a `CLAUDE_PLUGIN_OPTION_KEY` env var that hook scripts read directly with `$CLAUDE_PLUGIN_OPTION_KEY`. Appropriate for credential-heavy plugins that need both injection forms.
- *Sensitive flagging* — `sensitive: true` flags genuine secrets (API keys); `sensitive: false` correctly applied to identifiers that are public rate-limit handles (e.g. an Unpaywall email).
- *Cross-ecosystem duplication* — Cross-ecosystem deployments may duplicate the `userConfig` block verbatim into the Cursor manifest with no sync mechanism — drift risk identical to the version-string problem.

Common defect: `userConfig` declared in tests + docs, but live `plugin.json` omits it — every substitution resolves empty and the runtime starts with empty credentials.

### `userConfig` without explicit substitution

`userConfig` declared but no `${user_config.KEY}` references appear in the manifest. Claude Code translates user config into env vars implicitly for MCP subprocesses. Works in practice (the implicit translation is part of the plugin protocol) but a consumer expecting explicit substitution will be surprised.

### Schema richness — minimal vs. validated

When `userConfig` IS declared, the schema is typically thin — `description` and (sometimes) `sensitive` only, no `type`, `default`, enum, or validation pattern. Validation is deferred to runtime: the server raises a runtime error at first tool invocation when a required field is unset (`if not email: raise ValueError(...)`). A user who skips the prompt gets a deep runtime error rather than an install-time failure. No validation that the configured value matches its semantic shape (an email field accepts any non-empty string).

### Plain OS env var (no `userConfig`)

The plugin reads env vars directly via `os.environ.get` (e.g., `OUTLINE_API_KEY`, `LANCEDB_PATH`, `AUTO_MEMORY_DIR`, `CLAUDE_PLUGIN_*`). For the MCP-server case, `.mcp.json` declares passthroughs via shell-style `${VAR:-default}` or bare `${VAR_NAME}` for bearer tokens. The user is expected to set the variable in their shell. Constrains: not surfaced in Claude Code's config UI, no `sensitive: true` masking, no schema validation, no in-plugin prompt. Discoverability gap — the user must read `.mcp.json` (or README) to learn what variables the plugin expects. For required secrets a missed-opportunity pattern — `userConfig` with `sensitive: true` is the idiomatic surface.

### Env-var + INI-config knob pattern

No `userConfig` at all. Configuration knobs are read directly by the hooks from environment variables (`SP_NO_COMPRESS=1`, `SUPERPOWERS_AUTO_UPDATE=0|1`) and from a user-side INI file (`~/.config/superpowers/update.conf` parsed by awk). The knob surface is documented only in the README and hook source — schema-aware tooling cannot discover it. Constraint: no install-time prompt for values; users must know which env vars exist before setting them.

### MCP-registry-schema sidecar

`server.json` (the modelcontextprotocol/registry schema) declares `OUTLINE_API_KEY` with `isSecret: true` — the MCP-registry equivalent of `sensitive: true`. The same plugin's `plugin.json` has no `userConfig`. The two registries each demand their own config-schema dialect, and the author honors the MCP one but not the Claude Code one. Demonstrates that "no `userConfig`" can mean "we use a different registry's secret-marking" rather than "we don't acknowledge secrets exist."

### Plugin-managed JSON file with custom CLI

The plugin writes a settings JSON under a plugin-chosen path (`$HOME/.<plugin>/config/settings.json`) and provides a `<plugin>-config get/set/list` bin tool with an internal allowlist of legal keys. The Claude Code config UI does not see these settings. Appropriate when the plugin needs configuration semantics richer than the native `userConfig` (e.g. cross-session, cross-project, cross-tool sharing or behavior toggles like `proactive`, `auto_review`, `self_eval`). Constrains discoverability: users must learn the bin CLI; validation duplicates work the manifest schema would provide.

### Gitignored `.local.md` convention

A plugin ships an `<name>.local.md.example` template; the user copies it to `<name>.local.md` (gitignored) and edits values. Skills read the file at runtime via prose instructions, not a harness substitution mechanism. User-facing configuration as a file convention layered atop markdown — works without harness involvement, lacks any schema enforcement.

### External schema in admin-run script

Configuration is collected by a user-side script the admin runs out-of-band (`build-manifest.mjs`) that hand-rolls a `KEYS` object with regex patterns, hints, and `secret: true` flags, then emits a downstream config artifact. Plugin metadata layer is bypassed entirely; the plugin ships *tooling for the admin* rather than being configured itself. Recreates `userConfig` semantics outside the manifest.

### OAuth client embedded in MCP config

`.mcp.json` carries an `oauth` subfield with `clientId` and `callbackPort`, embedding OAuth client binding directly in the MCP server definition. Likely a Claude Code extension to the standard MCP server schema.

### Delegated to external CLI

The plugin assumes a sibling tool (e.g., `gh auth login`) handles authentication. Plugin README explicitly defers; no auth surface inside the plugin. Suits plugins that wrap an existing authenticated CLI.

### Delegated to MCP server's own login

For remote HTTP MCPs, the README tells users they will "authenticate through the server's web interface when prompted" at first connect. The plugin carries no credential plumbing; the MCP endpoint handles its own auth flow.

### Encrypted vault file with passphrase env-var

A vault file on disk holds Fernet-encrypted credentials, with the passphrase supplied via `userConfig` env var (`CLAUDE_PLUGIN_OPTION_PPC_VAULT_PASSPHRASE`); PBKDF2-HMAC-SHA256 with 100000 iterations derives the key. File-locking governs writes; in-memory cache per MCP-server-process. Appropriate for plugins juggling many third-party API tokens (e.g., Google Ads, Meta Ads). Constrains: passphrase loss = vault loss; `userConfig` field must actually ship in `plugin.json`.

### No user-supplied config

The plugin takes all inputs via conversational flow or file-path arguments to the CLI. No `userConfig`, no settings file. Appropriate when the plugin is fully driven by per-invocation arguments and has no per-user secrets or preferences.

## Tool-use enforcement (hooks)

What PreToolUse / PostToolUse / SubagentStart / CwdChanged / PostToolUseFailure / Stop hooks the plugin registers, and the failure posture they take.

### No enforcement

The plugin registers no PreToolUse / PostToolUse hooks. Behavior is shaped entirely through SessionStart persona injection plus skill / command instructions. Plugins relying on read-only or restricted tool surfaces enforce that at the MCP server level (e.g., `OUTLINE_READ_ONLY=true` env var passed through `.mcp.json`) or via prose directives in agent prompts ("perform read-only operations only") — no structural enforcement at the Claude Code hook layer. Lowest hook-maintenance burden; loses the ability to block wrong tool calls deterministically. Dominant posture across the corpus.

### Skill-description prose as enforcement surrogate

The SKILL.md `description` field uses capitalized "MANDATORY" / "Never invoke X directly" phrasing to bias the agent toward the plugin's wrapper. Relies on skill auto-load by relevance match; no hard gate. Trade-off: zero infrastructure, but model-variance can let the agent slip through if the skill doesn't auto-load.

### Multi-pattern PreToolUse safety stack

Multiple PreToolUse hooks all matching `Bash` (or `Read|Edit|Write|Bash`) run sequentially on every matching tool call. Examples: a destructive-command blocker (~30+ patterns, 3-tier severity), a secret-protector (~50+ file patterns + ~14 content patterns for hardcoded keys / tokens / PEM / connection strings), and a Bash-output compressor that rewrites noisy commands through an optimizer (with a never-compress allow-list for diffs / reads / failed commands). Latency compounds — each Bash call passes through every matching hook before execution. Documented fail-open posture for non-safety hooks (errors result in original command running unmodified); safety hooks presumed fail-closed on pattern match, fail-open on unexpected errors.

### PreToolUse guard set with multi-matcher concurrency

`hooks/hooks.json` declares multiple matcher blocks. One matcher (broad — `Edit|Write|Bash|NotebookEdit|mcp__filesystem__*`) runs a scope-enforcement script. A second matcher (`Edit|Write|Bash`) runs three guards in parallel: repo-boundary, protected-file, pre-edit-security. A third matcher (`Bash` only) runs a secret-scanner (gitleaks). Appropriate when policy is composable across orthogonal concerns (scope vs boundary vs security vs secrets). Constrains performance: every gated tool call waits on the slowest concurrent guard; deduplication across hooks is the author's responsibility.

### Universal-matcher rule evaluator

A `PreToolUse` hook with no matcher (fires on every tool call) plus a `PostToolUse` companion runs a Python evaluator against user-defined rules in `.claude/<plugin>.*.local.md` files. Output is JSON `{"systemMessage": "..."}` to stdout; failure posture is uniformly fail-open with try/except wrapping that always exits 0 ("never block operations due to hook errors"). Timeouts declared (10s). Used to give the user a configurable tool-policy mechanism without modifying the harness.

### Edit-targeted security reminder

A `PreToolUse` hook with `matcher: "Edit|Write|MultiEdit"` runs a security-warning script on file modifications. No declared timeout; if it hangs, the harness waits. Narrower trigger than the universal evaluator; still uses the JSON-to-stdout output convention.

### Fact-forcing first-edit gate

A `pre:edit-write:gateguard-fact-force` hook blocks the first `Edit`/`Write`/`MultiEdit` per file and demands the agent investigate (importers, schemas, prior context) before allowing. Appropriate for workflow-discipline plugins targeting agent research quality.

### Post-edit health-check (PostToolUse on `Edit|MultiEdit|Write`)

A PostToolUse hook on edit / write tools runs a domain-specific check (e.g. simulator compilation / crash check via CDP) with a short timeout. Last-write-wins debounce — only the most recent edit triggers the check. Silent-skip when prerequisite state is missing (no active session, file-type mismatch, target is a test or config file). Output is plain stdout text the agent reads, not structured JSON; documented exit-code convention (0 = success, 1 = error logged non-blocking, 2 = block operation explicitly NOT used).

### PostToolUse async telemetry + eval gate

A matcher block runs four async post-edit scripts on every Edit/Write: self-learn, telemetry, review-hint, eval-gate. A separate matcher emits async post-bash telemetry. The async modifier prevents tool-call latency but leaks background processes if the user exits mid-call. Appropriate when the plugin layers on cross-session learning, analytics, and self-evaluation; constrains process hygiene because nothing reaps the async children.

### PostToolUse skill telemetry / edit tracking

A PostToolUse on `Skill` records skill-invocation telemetry. A PostToolUse on `Edit|Write` logs file changes (drives TDD reminders downstream) and auto-appends working-state files (project-map.md, session-log.md, state.md) to `.gitignore` on first write. Keeps the plugin's working-state files out of git automatically — consumer never has to remember to add them.

### `PostToolUseFailure` post-hoc diagnostic hook

A hook fires on failures of MCP tools matching a namespace (`mcp__*<plugin>*`) and emits a tailored diagnostic ("CDP session is not active. Metro is not running on port X. Try: cdp_status to reconnect.") that the agent reads as plain stdout. Effectively a "here's why your MCP call just failed" surface — rare in the ecosystem; most plugins use PreToolUse for validation rather than post-hoc explanation. The hook inspects multiple environment / process states (active flag, port availability, simulator boot state, adb device presence) to compose the diagnostic.

### `SubagentStart` context injection

A SubagentStart hook injects connection / state info ("CDP bridge is connected (platform: X, port: Y)") into every subagent spawn so the subagent does not need to re-probe. Paired with frontmatter "PARENT-SESSION-ONLY" warnings on agents that cannot run under Task-tool spawning (because MCP stdio doesn't propagate to subprocesses). Documents an MCP-inheritance gotcha at the hook layer.

### `CwdChanged` re-detection hook

Re-runs project-type detection when the user `cd`s to a new directory; emits a warning ("tools may not work here") when the new cwd doesn't satisfy plugin prerequisites. Rare across the ecosystem — most plugins do not react to cwd changes.

### Stop-event handlers for session-end aggregation

Stop hooks (multiple, e.g. session-handoff, instinct-extraction, eval-gate finalization) run when the session ends. Each one aggregates JSONL events the PostToolUse hooks emitted during the session into summaries or longer-term stores. Appropriate when the plugin maintains durable cross-session state and needs a deterministic place to consolidate it; constrains start-of-session UX because the consolidated view is only refreshed on Stop, not on session open.

### Stop-hook prompt re-injection loop

A `Stop` hook emits `{decision: "block", reason: "<previous-prompt>", systemMessage: "..."}` to re-feed the prior prompt back into the agent on each Stop, implementing a self-iterating work loop. State (iteration counter, escape protocol, session ID gating) lives in `.claude/<plugin>.local.md`. Non-obvious use of the Stop block protocol as a control-flow primitive — the hook API as agentic-loop substrate.

### Per-hook bash scripts with selective strict mode

Each hook is a small `.sh` script invoked directly from `hooks.json`. `set -euo pipefail` is used on hooks that need fail-fast (e.g., pre-write content validation); other hooks run without strict mode and rely on `exit 0` to fail-open. `{"systemMessage": "..."}` JSON on stdout for non-blocking advice; stderr + `exit 2` for hard blocks. Appropriate when hook count is small and per-hook concerns are simple. Constrains: no centralized fallback for env-var resolution; per-hook copies of common boilerplate accumulate over time.

### Fail-open posture with explicit comment contract

Every shell hook begins with a comment declaring the contract ("Exit code MUST be 0 always — a failing hook must not interrupt Claude") and uses `set -euo pipefail` plus `|| true` on every external call, terminating with `exit 0`. Selective failure: a typo outside a command path still halts; CLI failures are swallowed. Appropriate when hook reliability matters more than hook correctness — the author would rather miss telemetry than block the user. Constrains visibility: silent swallowed failures need an out-of-band log (`hook-errors.log` written by an `_log_error` helper) to diagnose.

### Skill-level gating with no runtime hooks

The plugin omits hooks entirely and relies on the SKILL.md's workflow steps to enforce policy. Appropriate when the workflow is purely conversational and the gates are decisions the agent makes during step execution; constrains enforcement to whatever the agent honors voluntarily.

## Session context loading

How the plugin gets domain context, persona, or routing instructions into the model at session start.

### `hookSpecificOutput.additionalContext` JSON via SessionStart

A SessionStart hook prints a JSON object on stdout with `hookSpecificOutput.hookEventName: "SessionStart"` and `additionalContext: "<long persona / routing / instructions string>"`. The string is heredoc-embedded in the shell script. Effectively turns SessionStart into a context-injection channel without modifying any system prompt. Used to load a large instruction blob at session start (e.g., to emulate the unshipped "output style" feature: an entire prose blob that re-shapes the model's output behavior). Demonstrates that the hooks API can subsume a missing first-class harness feature.

### Plain-stdout context banner

SessionStart emits a large heredoc banner (40+ lines of prose) listing tool inventory, prerequisites, and version warnings via plain `echo` rather than structured JSON. Re-injected on every sub-event (`startup`, `clear`, `compact`) when no matcher restricts firing — significant context tax on long sessions. Hard-coded counts in the banner ("plugin is active with 51 MCP tools") drift from other hard-coded counts elsewhere (README "53 MCP tools"; source `grep -c "trackedTool("`).

### SessionStart stdout as system-reminder

Hook command (Python or bash) prints a `<system-reminder>` block to stdout. Claude Code captures SessionStart stdout and treats it as an additional system message — a legacy convention pre-dating the structured `hookSpecificOutput.additionalContext` JSON channel. Multiple plugins in one marketplace can register the same pattern, each contributing rules. Appropriate for "always-on rules" the agent should see at session start. No matcher means the hook also fires on `clear` and `compact`, re-injecting the rules each time context is reset — generally desired since the cleared session has lost them. Cost considerations: 2-3 second hook timeouts are tight; on cold start with slow I/O, reading multiple markdown files and walking up for `marketplace.json` may approach the limit. No retries, no fallback. Failure posture is fail-open — `exit 0` when sources are absent rather than blocking the session.

### Provenance-decorated stdout

A wrapper script (e.g., `bin/inject-rules`) doesn't just concatenate file contents — it resolves the plugin name from `plugin.json` and the marketplace name by walking up to `.claude-plugin/marketplace.json`, then decorates each injected file's path in the emitted `<system-reminder>` block as `"<path> from plugin <name>@<marketplace>"`. Gives the agent provenance for injected rules so it can attribute and reason about which plugin's rule applies. Refines the bare stdout-cat pattern by encoding metadata the agent can use to disambiguate.

### SessionStart banner with runtime probes

A SessionStart hook with matcher covering all four sub-events (`startup|resume|clear|compact`) emits a banner showing agent/command/hook counts, project name, version, etc. Implementation probes for a TUI framework (bun + Ink) at runtime, falling back to plain text when unavailable. Output goes to stdout as a printed banner, not via the structured `hookSpecificOutput.additionalContext` channel. Appropriate when the plugin wants a consistent visible-on-every-session presence; constrains performance (every session pays the probe cost) and may include intrusive defaults like auto-launching a GUI app when a config flag is set.

### SessionStart welcome banner via `systemMessage`

A `welcome.sh` runs on every SessionStart sub-event (no matcher restriction) and emits `{"systemMessage": ...}` JSON with skill counts, line-count warnings, or other lint-in-banner output. Appropriate for surfacing repo-state diagnostics to the user at session boundaries. Constrains: with no matcher, welcome banners re-emit on every `clear` and `compact`, polluting mid-session context.

### SessionStart sub-event matcher (`startup|clear|compact`)

The expensive synchronous SessionStart hook is scoped to `startup|clear|compact` and excludes `resume` (where routing is already in context). A second unscoped SessionStart entry runs the cheap async context-engine on every sub-event including `resume`. Pattern reduces wasted re-injection while preserving cheap state work. Codex equivalent uses `startup|resume` because Codex lacks the `clear`/`compact` sub-events.

### SessionStart with structured handler in standalone file

A SessionStart bootstrap (`session-start-bootstrap.js`) was specifically extracted to a standalone file (separate from inline `node -e` patterns used by other hooks) because inline `!` characters in fallback logic triggered bash history expansion in the inline pattern. Appropriate for SessionStart specifically; the extraction-to-file pattern resolves a real shell-environment fragility.

### SessionStart for runtime provisioning

SessionStart drives venv ensure + credential check, not user-facing context. Output is `systemMessage` JSON only on failure or status changes. Appropriate when the plugin needs setup work but no banner. Constrains: SessionStart timeout (e.g., 180s for venv) gates session readiness — long first-session installs delay the user.

### Echo-as-prompt for SESSION_SETUP

A SessionStart hook with a literal `echo` command reminding the agent to execute a `# Session Setup` section in CLAUDE.md. Fires on clear/compact too without a matcher, re-prompting after every context reset. Crude but functional — the agent treats the echoed string as a system message and acts on it.

### `UserPromptSubmit` skill-activator with confidence threshold

A UserPromptSubmit hook emits `hookSpecificOutput.additionalContext` with skill hints + memory recall (from a `session-log.md` style file) when a confidence threshold is met. Different trigger from SessionStart: fires per-prompt, can scope context to the current question. Sister hook to the SessionStart pair — three different context channels feeding the model.

### `UserPromptSubmit` for rule evaluation (not context)

A `UserPromptSubmit` hook exists but its purpose is rule evaluation rather than additive context — output is system messages reacting to the prompt, not appending instructions. Distinct from `SessionStart` injection.

### Persona duplication between hook and skill

The persona text injected by SessionStart is also embedded in the skill's `SKILL.md`. Two copies diverge on edit — single-source-of-truth violation. Caused by fusing dep-install and persona-injection in the same SessionStart hook; refactoring would require splitting.

### Release-notes-as-context

After a successful self-update, the SessionStart hook extracts the current release's "What's New" section from `RELEASE-NOTES.md` (a 100+ KB file) and injects it as `additionalContext`. Self-announcing upgrade pattern. Constraint: section-selection logic must be precise; an off-by-one would flood the prompt with the entire 100 KB file.

### No SessionStart, only PreCompact / PostCompact / Stop / SessionEnd

The plugin registers compact-cycle and end-of-session hooks but no SessionStart. Inbound context is instead loaded on demand via slash commands. Appropriate when the plugin's context shape is determined by user intent at session start rather than baked-in defaults; constrains first-session-after-gap UX because cross-session memory is only refreshed on Stop, not at the next session's open.

### No session-context loading

No `SessionStart`, no `UserPromptSubmit`, no `additionalContext`. Plugin relies on skill frontmatter `description` matching for surface — content loads on demand when the agent recognizes the skill is relevant. Dominant pattern; aligns with the "no always-on injection" posture. Skill-driven first-run bootstrapping (copying assets into cwd, creating files) runs only when the user explicitly invokes the bootstrap skill — setup never happens automatically.

## Live monitoring and notification

Whether the plugin uses the `monitors.json` component type for passive observation, or implements equivalent functionality via hooks.

### No monitors

None of the sampled plugins use `monitors.json`. Equivalent functionality is delivered via hooks (PostToolUse + Stop + SubagentStop combinations) plus runtime MCP tool calls (e.g. `cdp_status`). Author awareness varies — at least one plugin has real-time diagnostic needs that a `monitors.json` could surface; the hook-based equivalent works but is not equivalent to a declarative monitor.

### Stop-hook driven desktop notification

A `Stop` hook runs `desktop-notify.js` after Stop events to fire macOS desktop notifications. Implemented at the hook layer rather than via a dedicated `monitors.json`. Appropriate when the plugin needs notifications but `monitors.json` isn't yet broadly adopted in the runtime. Constrains: notification delivery is OS-specific to whatever the script targets; multi-OS support requires per-OS handlers.

## Cross-session memory and state persistence

How the plugin persists state between sessions for the model to pick back up.

### File-based memory stack with auto-gitignore

A small set of working-state files at the project root capture cross-session state: a JSON snapshot (auto-managed, e.g. git blast radius), a structure-cache markdown file, a decision-history log, a task-snapshot file, and an error→solution map. The stack is auto-appended to `.gitignore` on first write by a PostToolUse hook so it never gets committed by accident. Read by SessionStart / UserPromptSubmit hooks to re-hydrate context. Distinct from `memory: user|true` agent frontmatter, which signals model-side memory rather than file-based state.

### Skill-side experience seeds with stateful HOME directory

Seed YAML files (e.g. `seed-experience/common-failures.yaml`, `expo-gotchas.yaml`, `platform-quirks.yaml`, `recovery-playbook.yaml`) ship with the plugin and are initialized into `$HOME/.claude/<plugin>/` by a SessionStart `ensure-*.sh` script — establishing telemetry and candidates directories plus a scratchpad markdown file. Combines plugin-shipped seed data with user-side mutable state outside the plugin's data directory.

### Plugin-chosen `$HOME/.<plugin>/` with override env var

A plugin-named state directory under the user's home (e.g. `$HOME/.<plugin>/`) holds config, analytics, sessions, and other durable state. An override env var (`<PLUGIN>_HOME`) lets users relocate it. Appropriate when state is meant to survive across projects, across Claude Code reinstalls, and across cross-tool deployments (Claude + Codex sharing one state dir). Constrains backup and discovery: not where users expect plugin data per Claude Code conventions, so docs must call out the location explicitly.

### Plugin-managed file location, no convention

State files (JSONL telemetry, learning logs, session timelines) live under the plugin-chosen `$HOME` path rather than `${CLAUDE_PLUGIN_DATA}`. The plugin's bin tools read/write directly. Appropriate for the same cross-tool-sharing rationale; constrains visibility because the Claude Code harness has no awareness of these files.

### User-visible markdown setup log

Plugin instructs the agent to read `~/Desktop/<plugin>-setup.md` first and append a `## Run — <timestamp>` section on each invocation. Setup is fully resumable across sessions; the human can inspect or edit the log directly. Uses a user-visible plain markdown file as workflow state — distinct from hidden caches or harness-managed state.

### Plugin-local `.local.md` with YAML frontmatter

Plugin reads/writes `.claude/<plugin>.local.md` (markdown body with YAML frontmatter) for iteration counters, escape protocols, and session-ID gating. Hidden but inspectable; persists across Stop-hook iterations within a session and across sessions. Used by the Stop-hook re-injection loop pattern.

## Telemetry and self-evaluation

How the plugin records its own operation and grades its own output.

### JSONL append-only event logs

Telemetry, analytics, learnings, review events, and timeline entries are written as JSONL append-only files under the plugin's state directory. Bin tools (`<plugin>-telemetry`, `<plugin>-learnings-log`, `<plugin>-learnings-search`) emit and query these. Appropriate for a plugin that wants durable cross-session memory; constrains rotation and retention (no auto-pruning visible) and creates a deduplication problem when multiple async hooks may write the same event.

### Eval-gate as a CI job

CI runs the plugin's own evaluation harness (`bun run eval` or equivalent), parses score and critical-finding count out of stdout via grep, and fails the build on any critical findings. The plugin grades its own artifacts against its own rubrics on every push. Appropriate when the plugin's purpose is review/judging and the author wants meta-coverage; constrains stability because grep-of-stdout is brittle to eval output format changes and shifts to structured output (JSON exit) would harden the gate.

## Plugin-to-plugin coordination

Whether the plugin declares dependencies on other plugins or relies on prose-only coordination.

### No declared dependencies

`dependencies` field absent from every entry across the corpus. Plugins are flat and independent. The `<plugin-name>--v<version>` git tag format (the cross-plugin pinning mechanism) is consequently not exercised — single-plugin marketplaces use plain `vX.Y.Z` tags, and cross-plugin contracts are enforced only by intra-plugin convention, not the runtime. Cross-plugin interactions (e.g., two plugins both connecting to the same external service via their own `.mcp.json`) are handled by convention rather than declared.

### Implicit prose-only dependency

README states "install plugin X first" or "this plugin doesn't manage any store directly – it routes to <other-plugin>" without expressing the relationship in any manifest. A function-specific plugin's skills reference MCP tools owned by a sibling core plugin; if the user installs only the function plugin, skills load but the tools they call are missing. Documentation is the only enforcement; failure surfaces at use time. Coordination is by discipline, not structure.

### Skill chaining via Stop-hook tail-grep

A `Stop` hook tails the last 200 lines of the transcript, matches the most recent skill invocation, and emits a `systemMessage` recommending the next skill in an intra-plugin DAG. Appropriate when the plugin's skills form an ordered workflow. Constrains: depends on a stable transcript-line format and accurate matching — observed inconsistency where one variant grepped the path string instead of file contents, so it never matched correctly.

## Testing framework

How the plugin's deterministic tests are organized.

### No tests

No test directory, no test files. The most recent commit message may reference "code review issues" implying manual review, but nothing automates continued correctness. Common in early / single-author plugins where the author tests by manual installation. Pure aggregator marketplaces also ship no test code — there's no plugin payload to verify locally; all validation is at the aggregator boundary or in the upstream review pipeline.

### Bash scripts under `tests/<platform>/` with no CI

Tests live as bash scripts under `tests/claude-code/`, `tests/codex/`, `tests/opencode/`, etc., plus standalone Python analyzers. Run manually by the maintainer; no GitHub Actions exercise them. Multi-platform layout signals testing intent without CI investment. Quality gap is visible — version sprawl across multiple files plus a YAML source-of-truth shows drift in practice (compiled artifacts at one version, source at an older version) that CI would catch immediately.

### pytest with sys.path manipulation

`tests/` directory holds pytest test files; tests manipulate `sys.path` via `sys.path.insert(0, str(ROOT))` to locate the source tree because no installed-package layout is assumed. Pytest config may live in a dedicated `pytest.ini` (with `testpaths`, `python_files` patterns, custom markers like `network`, `claude`, `replay`, `browser`) or be omitted entirely. Appropriate when the plugin has Python code and the author wants tests to run against source, not the installed copy. Constrains debuggability: install-path bugs (e.g. console-script vs PYTHONPATH-pointed-at-src divergence) hide because tests bypass the install path.

### Pytest with marker-segmented suites

Pytest with markers (`integration`, `e2e`) routing tests into tiers. Default `addopts` excludes the heavier markers so bare `pytest` runs unit tests only. `tests/` at repo root, split into `features/`, `e2e/`, `utils/`. Adjacent markdown sidecars (`test_*.md`) appear next to some tests as human-written per-test documentation. Dependency declared via uv-native `[dependency-groups].dev`. Local invocation via `poe test-unit`/`test-integration`/`test-e2e` tasks (poethepoet). Pitfall: pytest `addopts = "-m 'not e2e and not integration'"` combined with markers named `integration` and `e2e` means a bare `pytest` silently skips a category developers may not realize is there.

### Pytest, flat tests directory

`tests/` at repo root, flat layout (`test_chunker.py`, `test_indexer.py`, `test_mcp_tools.py`, `test_parsers.py`, etc.). Pytest config in `[tool.pytest.ini_options]` with `pythonpath = ["."]`. No marker tiers. Local-only invocation per README (`pytest tests/ -v`).

### Pytest scoped to one plugin within a marketplace

Tests live inside the plugin directory (`plugins/<name>/tests/{unit,integration,lint}/`) with a `conftest.py` that runs the plugin's main script as a subprocess via `sys.executable`, self-locating relative to the test file. The other plugins in the same marketplace ship zero tests. Pytest config relies on discovery defaults; tests assume invocation via the plugin's own Makefile, not a top-level runner. Pytest version floor (`pytest>=9.0.2`) tightly couples to a high Python floor (`>=3.14`).

### Node `node:test` with multi-job CI

`node --test 'test/unit/*.test.js'` runs hundreds of tests against the in-plugin Node MCP server (located under a sub-path like `scripts/<server>/test/`, not repo root). CI runs three parallel jobs: TypeScript build, unit tests, and a separate `version-sync` job comparing manifest copies. No matrix — single Node version, single OS. Action versions pinned by tag (`@v4`), not SHA. Caching via setup-node's built-in npm cache with explicit `cache-dependency-path` to the sub-package's lockfile. CI does NOT run on tag push — release creation is fully manual. Integration tests are a thin slice of the test count; full E2E (simulator-driven) runs on the maintainer's dev box, not in CI.

### bun test with TypeScript

`bun test` (Jest-compatible runner) executes `*.test.ts` files in a flat `tests/` directory. Appropriate for Node-toolchain plugins; constrains runner choice (locks the project to bun rather than node+jest or vitest).

### Mixed `node:test` + pytest with custom runner

Primary tests use `node:test` via `tests/**/*.test.js`, executed by a custom `tests/run-all.js` that `spawnSync`s each file and aggregates pass/fail in an ASCII box. Python tests (pytest + pytest-asyncio + pytest-cov + pytest-mock) cover a Python sub-package via `pyproject.toml`'s `[project.optional-dependencies] dev`. Appropriate when the plugin spans Node and Python; produces robust coverage but requires the custom runner to coordinate. Constrains: in the observed sample, the custom runner only invokes Node tests — pytest is configured but orphaned from CI.

### Go test toolchain

`go test -race -coverprofile`, `go vet`, `gofmt -l .` against Go source. Appropriate when the plugin wraps a Go binary.

## CI pipeline

What CI verifies on push and pull request.

### No CI

`.github/workflows/` does not exist. All testing is local/manual. README claims may not be enforced (e.g., "56 tests covering …" is unverifiable on PRs). Regressions caught only when the author runs pytest locally before committing. Common in personal/early repos. Notable for first-party Anthropic-owned marketplaces of substantial scale — even at scale, plugins land at tip-of-main with manual review as the only gate.

### CI workflows present but no tests

`.github/workflows/` carries claude-action wrappers (`claude.yml` for `@claude` mention response, `claude-code-review.yml` on PR, `claude-skill-review.yml` on PR) plus a release workflow. None invoke a test runner; the LLM-driven reviews substitute for tests.

### Single-workflow validate + lint + eval-gate + convergence

One `ci.yml` runs four jobs: validate (install + skill checks + schema-validation + full test), lint (strict `tsc --noEmit`), eval-gate (self-eval grader), convergence (custom convergence test). Triggered on `push` and `pull_request` against `main`. Single OS, single runtime version pinned. Action versions tag-pinned (no SHA pinning). Appropriate when the plugin has many in-repo validators it wants to gate centrally; constrains supply-chain hygiene because tag-pinned actions can be moved by their authors.

### Multi-workflow with pytest matrix and security scan

Tests run against a Python version matrix (`3.12`, `3.14`); a separate `security.yml` runs `gitleaks/gitleaks-action@v2` on push and PR; a tag-triggered `release.yml` re-runs tests on `v*` tag pushes. Appropriate for Python-toolchain plugins that want to catch version-specific breakage early. Constrains workflow maintenance because the same checks duplicate across files.

### Multi-workflow with version matrix and SHA-pinned actions

Eight workflows (`ci.yml`, `e2e.yml`, `publish-pypi.yml`, `release.yml`, `docker-build.yml`, `codeql.yml`, `claude.yml`, `claude-code-review.yml`). `ci.yml` runs ruff format check, ruff lint, pyright type-check, pytest with junit XML + coverage; matrices Python 3.10 × 3.11 × 3.12 × 3.13 (`fail-fast: false`); ubuntu-latest only. `e2e.yml` brings up Docker Compose against the real upstream service. CodeQL scans Python source plus the workflow files themselves (`language: actions`) with `security-extended` queries, on a weekly cron. Caching: `astral-sh/setup-uv` with `enable-cache: true` (uv's GH-Actions backend); Docker uses `type=gha` buildx cache. `claude.yml` and `claude-code-review.yml` ship fully wired with credentials but triggers commented out and only `workflow_dispatch: {}` enabled — deliberate opt-in staging of Anthropic automation, easy to flip on later.

### Multi-job matrix with parallel test/validate/security/lint

`ci.yml` defines four parallel jobs — `test` (matrix-runs), `validate` (multi-validator chain), `security` (npm audit), `lint` (ESLint + markdownlint). Triggers: `push: [main]` + `pull_request: [main]`. Matrix is OS × Node × package-manager (e.g., `[ubuntu, windows, macos] × [18, 20, 22] × [npm, pnpm, yarn, bun]`, minus exclusions = ~33 lanes). `fail-fast: false`. Appropriate for plugins targeting wide cross-platform support. Constrains: matrix cost — minutes per lane × lane count = significant CI minutes per PR.

### Multi-OS Go test matrix plus daily cross-version run

`ci.yml` runs Go tooling on a `{ubuntu-latest, windows-latest}` matrix at PR time and adds macOS plus `{stable, oldstable}` Go on a daily schedule. Release workflow crosses six GOOS/GOARCH pairs. Plugin shims are validated only by `bash -n` parse checks at release time — never end-to-end. Action pinning via major tags (`@v4`, `@v5`), no SHA pins. `actions/setup-go@v5` with `go-version-file: go.mod` for implicit module caching.

### Single-runner JSON validation only

One workflow (`validate-marketplace.yml`) runs on `ubuntu-latest`, Node 20, no matrix, performing only `node -e "JSON.parse(...)"` syntax checks on `marketplace.json` and each `plugin.json`, plus a custom version-sync script. Test suites (where they exist) are not invoked. Appropriate when the plugin payload is content-only (skills/agents) with no runtime to test. Constrains: defects in the payload (manifest fields the docs/tests describe but the live file omits) ship to consumers because no test job catches them.

### Single PR-gatekeeper workflow

The only workflow is `close-external-prs.yml` triggered on `pull_request_target` opened/reopened. Uses `actions/github-script` to check the PR author's collaborator permission; if not `admin`/`write`, posts a canned redirect comment and closes the PR. No manifest validation, no tests. Appropriate for read-only mirrors with explicit anti-contribution posture. Constrains: zero protection against malformed sync-PR merges; a stale `source` entry with a missing directory was observed live.

### `@claude` mention responder

A general-purpose `claude.yml` workflow on `issue_comment`, `pull_request_review_comment`, `issues`, `pull_request_review` events, gated on `@claude` mention. Uses `anthropics/claude-code-action@v1`. Not validation per se — turns the repo into an agent-addressable surface for ad-hoc questions and patches.

### Organizational PR bouncer

A `close-external-prs.yml` workflow on `pull_request_target: [opened]` checks the PR author's collaborator permission level via the GitHub API and auto-closes any PR from non-admin/non-write users with a comment redirecting to a submission form. Disableable via repo variable. Implements org-wide submission gating as a workflow rather than as branch-protection rules — appropriate when admin-controlled merging needs an explicit "this is not the contribution path" signal at PR-open time.

## Action pinning discipline

How CI workflows pin third-party GitHub Actions.

### SHA-pinned with version comment

Every action pinned by 40-char SHA with a `# vX.Y.Z` trailing comment (e.g., `actions/checkout@de0fac2e... # v6.0.2`). Appropriate when supply-chain risk is taken seriously and the workflow surface is large. Constrains: pin updates require re-fetching the SHA at every version bump; tooling like Dependabot can automate. Some action references in mature workflows still mix in floating `@v6`/`@v4` tags — inconsistency.

### Tag-pinned to major

Major-tag pins (`actions/checkout@v4`, `actions/setup-node@v4`, third-party `@v1`). Appropriate for low-blast-radius workflows or when the supply-chain threat model accepts tag mutation risk. Constrains: a compromised tag could inject code; mitigations rest on the action publisher.

## Tag and release lifecycle

How the repo cuts version tags and how releases are produced.

### Tag-on-main with active cadence

Tags `vX.Y.Z` placed directly on commits merged to `main` (no release branch). 18 tags over ~13 months in one observed sample, mostly major v1.x cuts in a burst. No pre-release suffixes used in practice, though the release pipeline reserves `-rc` semantics. Pre-commit hooks include ruff + pytest but no auto-bump. Version bumps are manual via a `poe bump-version` task.

### Tag-on-main, no release branches

Tags `vX.Y.Z` cut directly on main, no `release/*` or `v*` legacy branches. Pre-release suffixes absent in observed samples. Appropriate for linear release histories. Constrains rollback: bug fixes ship by cutting a new tag from main, not by maintaining release branches. Coarse cadence in some cases (e.g., three tags over four months); all `plugin.json` versions stay frozen across the tag sequence in single-namespace shapes.

### Tag-on-main with single release

Sole tag is `v0.1.0` on `main`. First release; cadence patterns aren't established. No automation aligns the tag with `plugin.json` version (coincidence-by-discipline so far).

### Single lifetime tag with drift

A single `v1.0.0` tag exists at marketplace creation; per-plugin `plugin.json` versions advance (e.g., `1.0.1`, `1.1.0`) without follow-up tags. CHANGELOG.md and README also drift from live state. Operationally appropriate when no automation forces tag-version correspondence — but a clear anti-pattern: users pinning the only tag get stale plugins indefinitely.

### Untagged sync-only

Zero tags ever; the entire release surface is the sync-PR merge stream. Appropriate for read-only mirrors of an upstream pipeline. Constrains: no pin handle other than commit SHA.

### No tags, no releases

`git/refs/tags` returns 404; releases are empty. Versions live only in per-plugin `plugin.json` files and are bumped manually when the author remembers. The "lazy commit" message on HEAD signals deliberate informality. Periodic `bump-versions-*` branches in commit history suggest manual batch bumps. Appropriate for a personal repo with no downstream consumers, or deliberately informal even at high traffic.

### Dual tag namespaces on a single trunk

Two distinct tag prefixes coexist on `main` — one for an underlying binary (`v*`) and one for the plugin (`plugin-v*`). Each tag prefix triggers its own release workflow. Lets the binary iterate rapidly without forcing plugin bumps and vice versa.

## Release automation

How tags become releases and how release notes flow to users.

### Manual release creation, no workflow

Release creation is `gh release create` (manual) or the GitHub Releases UI. Notes are hand-composed; CHANGELOG.md is updated in the same commit cycle. No tag-sanity gate — no enforcement that tag format matches `v*` or that the tagged version equals `plugin.json.version`. Tag count substantially less than version count when high-cadence on-main bumps ship through the marketplace without a corresponding tag.

### Tag-triggered test verification only

A `release.yml` workflow triggered on `push: tags: ['v*']` re-runs tests but does not build artifacts, create GitHub releases, or publish anywhere. The workflow header explicitly disclaims: "manual marketplace steps still required." Appropriate as a sanity check over manual releases; constrains the release process because tag-on-main verification, version-equality checks, and tag-format regex are absent — a tag from any commit passes if tests pass.

### Triple-target publish on single tag (PyPI + MCP Registry + Docker)

On `push: tags: ['v*']`, three workflows fire concurrently:
1. PyPI publish via `pypa/gh-action-pypi-publish` with OIDC trusted publishing (no stored secrets); a TestPyPI sub-job conditional on `contains(github.ref, '-rc')` routes pre-releases to TestPyPI; a fourth job authenticates to the MCP registry via GitHub OIDC (`./mcp-publisher login github-oidc`) and rewrites `server.json` in the ephemeral checkout with `jq` before publishing
2. GitHub Release via raw `gh release create --generate-notes --notes-start-tag $(git describe --tags --abbrev=0 ${ref}^)` — auto-computes previous tag for changelog range
3. Multi-arch Docker (amd64+arm64) via `docker/setup-qemu-action` + `docker/setup-buildx-action` + `docker/metadata-action` computing a six-form tag set (`{{version}}`, `{{major}}.{{minor}}`, `{{major}}`, `latest`, branch, short-SHA); single-arch validate (curl `/health` retry loop) before multi-arch final build; only pushes on `refs/tags/v*`

Tag-form fragility: `release.yml` and `docker-build.yml` lack the `-rc` filter that `publish-pypi.yml` has, so a pre-release tag also cuts a GitHub Release and pushes a `latest` Docker image — `latest` would leak an rc build. The MCP-registry job rewrites `server.json` in-checkout but doesn't commit it back; if local source-of-truth disagrees with the tag-derived value, the registry silently wins for that publish.

### Tag-triggered release with multi-gate sanity (npm)

`release.yml` triggers on `push: tags: ['v*']`, runs three gates — tag format regex (`^v[0-9]+\.[0-9]+\.[0-9]+$`, no pre-release), tag-equals-package.json-version comparison, and a manifest-sync test (`plugin-manifest.test.js`) — then conditionally `npm publish --access public --provenance`, then creates a GitHub Release via `softprops/action-gh-release` with `body_path: release_body.md` (a heredoc'd template) plus `generate_release_notes: true`. Idempotency: `npm view ${NAME}@${VERSION}` gates the publish step. Appropriate for npm-published plugins with strong release-engineering needs. Constrains: the templated release body adds little over auto-generated notes (anti-pattern signal); cross-manifest version sync is only verified for one of the many version-bearing files.

### Skill-zip build via filesystem glob

A workflow triggered on `v*` tags globs `*/`, gates on `SKILL.md` presence, zips each matching directory as `<dir>-<tag>.zip`, attaches all zips to a draft GitHub release. Discovery is filesystem-driven, not marketplace-driven — adding a SKILL.md-bearing directory automatically ships a zip on next tag, even if that directory isn't a marketplace-listed plugin. MCP-only plugins produce no zip (they're consumed in-place via `plugin.json`). `softprops/action-gh-release@v1`, `draft: true`, `generate_release_notes: true`. No tag-sanity gates beyond the `v*` glob. A variant iterates directories matching `*-skill/` specifically and constrains naming convention: skill plugins must end in `-skill/` to be released.

### Cross-compile binary release with multi-target packaging

A `release.yml` triggered on `v*` tags cross-compiles a Go binary across six GOOS/GOARCH pairs, packages tar.gz (POSIX) / zip (Windows) including a generated shim inside each archive, uploads via `softprops/action-gh-release@v2`, computes sha256 checksums, then synthesizes a Homebrew formula via heredoc and pushes it to a sibling tap repo. Substantial automation; the plugin is one of multiple distribution channels.

### Plugin-tagged release with stamp-from-tag

A `release-plugin.yml` triggered on `plugin-v*` tags validates the plugin tree (file existence, JSON lint, `bash -n` parse), stamps `plugin.json.version` from the tag using a Python one-liner, packages a tarball, computes sha256, creates a GitHub release. Tag-to-manifest equality is enforced one-way at release time. Validation only fires at release; pre-merge structural drift sits latent on `main` until a tag is pushed.

### Sponsor automation as scheduled workflow

A `sponsors.yml` runs daily (`schedule: "0 6 * * *"`) plus `workflow_dispatch`, calling `JamesIves/github-sponsors-readme-action` six times (one per pledge tier) to sync `SPONSORS.md` and `README.md`. Appropriate for community-funded projects. Constrains: in the observed sample, the action targets `branch: master` while the default branch is `main` — a config drift that would fail on first run.

### CHANGELOG with non-Keep-a-Changelog custom sections

CHANGELOG.md follows the Keep a Changelog base format (`## [X.Y.Z] — date`, `### Added`, `### Fixed`) but adds custom sections (`### Verified-stale`, `### Multi-review`, `### Benchmarks validated live`, `### Backlog state`). Entries reference internal ticket IDs and external issue numbers. Hand-maintained — release notes on GitHub Releases manually duplicate a subset of CHANGELOG prose. A `release-please`-style auto-generator wouldn't handle the custom sections; the format trades automation for richness.

### `RELEASE-NOTES.md` consumed by SessionStart hook

A free-form `RELEASE-NOTES.md` (100+ KB) replaces a conventional CHANGELOG. The session-start hook reads it on update to extract the current release's "What's New" section and inject inline as context. Inline release-notes-as-context pattern — see *Session context loading > Release-notes-as-context* for the consumption side.

### None — manual everything

No release workflow, no automated `gh release create`, no marketplace publish. The CHANGELOG (when present) is human-maintained. Appropriate when the plugin has no released versions and the author has not yet committed to a release process; constrains user trust because there is no signed/dated artifact. Tags created manually via GitHub UI or `gh release create`. No automation verifies tag matches `plugin.json` version. Appropriate for first-release / personal-scope projects.

### No releases at all

No tags, no release workflows. Versions are mutable strings in `plugin.json` files, not pinned anywhere downstream consumers can resolve.

## Marketplace validation

What schema / structural validation runs against the manifests in CI.

### No validation

`plugin.json` and `marketplace.json` are structurally hand-validated only. No JSON Schema validation step. The `$schema` reference (when present) points at the canonical Anthropic schema URL but no build step fetches or validates against it. Frontmatter on agents / skills / commands is unvalidated. Hooks.json correctness is implicit (pre-commit version-sync; CI re-runs it; hook scripts get the executable bit checked by git). Drift between marketplace `description` and per-plugin `plugin.json` `description`, missing `version` fields on some `plugin.json`s, non-semver shorthand like `"1.1"`, missing-SHA entries, inconsistent field sets, author-name mismatches between nested manifests, placeholder `owner.email: "your-email@example.com"` shipping to production — all would be caught by schema validation but aren't. Pure-aggregator workflows do no manifest parsing; they rely on an internal review pipeline (private to the marketplace owner) to gate entries before merge — public-facing repo has no recovery if the upstream gate misses something (observed: a stale `./<plugin-name>` source entry with no matching directory shipped to consumers). The closest to validation is a `bump_version.py` that checks semver-bump validity on author-initiated runs, not as a CI guard.

### Script-based source linting (regression guard)

A maintainer-authored script (e.g. `sync-versions.sh`) regex-scans source files for forbidden patterns (hardcoded version literals, etc.) as a regression guard. Not full schema validation — targets specific known-bad patterns. Runs in pre-commit and CI for cross-checking.

### In-CI custom validators

Validation is a job in the main CI workflow rather than a standalone workflow. Implementation is in-repo TypeScript or Python validators (`scripts/skill-check.ts`, `scripts/validate-agents.ts`, `scripts/<cli>.py check --plugin-repo`). These enforce both standard schemas and plugin-internal extensions (custom frontmatter fields). Appropriate when the plugin's manifest extensions exceed what `claude plugin validate` covers; constrains shareability because validators are not published as a reusable tool — they live and die with this repo. Passing here does not equate to passing the canonical CLI validator.

### Multi-validator composition

A `validate` CI job runs many discrete validators in sequence with `continue-on-error: false` — each validator targets one component type or concern: `validate-agents.js`, `validate-hooks.js`, `validate-commands.js`, `validate-skills.js`, `validate-install-manifests.js` (cross-ecosystem manifest sync), `validate-workflow-security.js` (GitHub Actions hygiene — SHA-pinning, minimal permissions), `validate-rules.js`, `catalog.js --text`, `check-unicode-safety.js` (invisible-unicode / zero-width injection block, an AI-agent prompt-injection vector). Appropriate when the plugin surface is large and concerns separate cleanly. Constrains: each validator is its own script to maintain.

### Schema-and-shape validators in TS

Bun-run TypeScript scripts validate `marketplace.json` (object shape, `plugins` array, per-entry required fields, duplicate detection) and frontmatter on agents/commands/skills (per-type required fields, glob-special-char pre-quoting so patterns like `**/*.{ts,tsx}` parse). PR-only triggers, path-scoped so each validator fires only on relevant changes. Plain TS, no zod. Constraint: validates field presence, not shape (e.g., `source` must be truthy but its discriminator isn't checked).

### Alphabetical-sort enforcement

A `check-marketplace-sorted.ts` script runs on every PR touching `marketplace.json` and fails if `plugins[].name` isn't case-insensitively sorted. Provides a `--fix` flag that rewrites the file in place. Treats the manifest as a sorted registry — CI rather than pre-commit hook is the enforcement point.

### JSON-parse plus version-sync only

`node -e "JSON.parse(...)"` against `marketplace.json` and each `plugin.json`, plus a `check-versions.mjs` script that compares marketplace-entry `version` against `plugin.json` version. Frontmatter validation, hooks.json validation absent. Appropriate when the plugin payload is content with simple structural needs. Constrains: defects in non-validated files (frontmatter formats, hooks shapes) ship.

### Ad-hoc shell + JSON-lint at release time

The plugin-release workflow runs `python3 -m json.tool` on `plugin.json`, `bash -n` on each shim, and filesystem existence/executable-bit checks. Validation fires only on tag push, not on PR or merge to main. Coverage zero before tag time.

### LLM-driven PR review

Workflows invoke `anthropics/claude-code-action@v1` or a reusable cross-repo `claude-skill-review.yml@main` to let Claude comment on PR contents — including frontmatter and manifest changes. Not deterministic; LLM inspection rather than schema enforcement. Trade-off: catches semantic issues a schema can't, misses some structural typos a schema would. A dynamic matrix over `find . -name SKILL.md` runs one review job per affected skill so the workflow auto-adjusts to new skills without edits.

### Reverse-engineered validator notes as primary-source artifact

A `.claude-plugin/PLUGIN_SCHEMA_NOTES.md` document captures undocumented plugin-validator constraints (e.g., `version` is mandatory; `agents`/`commands`/`skills`/`hooks` must be arrays not strings; `agents` MUST be explicit file paths, directory paths reject with `"agents: Invalid input"`) written from observed install failures. Appropriate when the plugin runtime's validator behavior isn't documented elsewhere; the artifact accumulates real-world failure-mode evidence.

## Source-pin maintenance

Keeping `git-subdir` SHA pins fresh over time without manual labor.

### Scheduled bot-PR with fairness ordering

A `bump-plugin-shas.yml` workflow runs on cron (weekly), iterates pinned `git-subdir` entries, queries each upstream for the latest commit on the pinned ref (respecting `path` scope), sorts by `-age_days` so the oldest-pinned entries roll first ("prevents starvation under the cap"), applies up to N bumps per run (default 20, configurable), and opens a single bot-signed PR. Concurrency is enforced via label-based check (`gh pr list --label sha-bump --state open`) so at most one open bump PR exists at a time. Force-pushed-away SHAs and 404s are categorized as "dead" without blocking other bumps. Permissions live on a GitHub App (org policy bars `GITHUB_TOKEN` from creating PRs).

## Pre-commit and pre-push hooks (git)

Whether git hooks enforce discipline at commit time.

### `.pre-commit-config.yaml` with linters only

Pre-commit hooks run `ruff --fix` on script directories and `python3 -m compileall` on Python source. No version manipulation, no manifest validation. Appropriate as a low-overhead floor; constrains because anything beyond syntax+style (version sync, manifest schema) is left to CI.

### Multi-tool pre-commit including pytest

`.pre-commit-config.yaml` runs ruff format check, ruff lint, pyright type-check, pytest (`uv run pytest tests/ -v`), plus basic hygiene hooks. Pytest at commit time is unusual — most projects pre-commit ruff/format only — and forces every commit to pass the unit suite. Costlier per commit but catches breakage at the lowest-friction point. Plus standard hygiene (trailing whitespace, end-of-file fixer, etc.).

### Absent

No git hooks committed. No commit-time enforcement. Commits land regardless of test or lint state. The implicit gate is the author's local discipline. Appropriate at pre-release maturity; constrains because manifest drift and version drift have no commit-time gate.

## Ecosystem health automation

Dependency updates and security scanning beyond bare CI.

### Dependabot + CodeQL + grouped updates

`.github/dependabot.yml` weekly updates for `pip` (grouped minor+patch into a single PR labeled `minor-and-patch`) and `github-actions` (SHA bumps for the SHA-pinned action references). CodeQL scheduled weekly with `security-extended` queries scanning Python source plus workflow files themselves (`language: actions`). Reduces PR churn while keeping the supply chain monitored.

### None

No Dependabot config, no CodeQL workflow. Dependency updates are author-discretion only.

## Documentation surface

What human-readable docs ship with the plugin and where they live.

### Single root `README.md` plus `LICENSE`

Standard minimum: a README at repo root covering install / setup / usage, plus a LICENSE file (typically MIT). Substantial READMEs include benchmarks, troubleshooting, security sections; thin READMEs cover only install + usage. Single-skill plugins consolidate everything into one README plus the SKILL.md. Community health files (SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md) are typically absent — security guidance lives as a `## Security` section in README instead.

### Comprehensive single README + ad-hoc CLAUDE.md

Repo-root `README.md` is the consumer-facing entry point — features, prereqs, install instructions for multiple MCP clients (Claude Code, Cursor, Windsurf, Cline), per-client config templates, env-var catalog, tool catalog, dev quick-start, troubleshooting. `CLAUDE.md` (when present) carries developer/agent guidance — architecture summary, registration patterns, test conventions, release runbook. The two often conflate concerns — `CLAUDE.md` mixes architecture-reference content with operational procedure, acceptable for solo projects but blurs the project-doc-separation discipline of larger systems.

### Marketing-grade README (40+ KB)

README doubles as marketing and technical reference. Sections include research motivation, third-party testimonials, shields.io badges (stars, version, license, install CTA), full skill catalog, hook inventory. Drives the file past 40 KB. Trade-off: discoverability and credibility benefit; maintenance cost grows; some sections (e.g. third-party LLM quotes) are unusual for a plugin README.

### Sprawling root with many entry-point markdowns

17+ top-level files including README, CHANGELOG, ARCHITECTURE, CLAUDE.md, SKILL.md, SKILL_REGISTRY.md, AGENTS.md, ETHOS.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, LICENSE, VERSION, plus tooling configs. Appropriate for plugins with substantial internal complexity that need multi-perspective entry points; constrains discoverability because the root becomes a kitchen-sink and roles overlap (CLAUDE.md vs SKILL.md at the same level signals conflated governance).

### Multi-document agent-context layer

Repo root carries 14+ markdown files: `README.md` (multi-locale `docs/<locale>/`), `CHANGELOG.md`, `CLAUDE.md`, `AGENTS.md`, `RULES.md`, `SOUL.md`, `TROUBLESHOOTING.md`, `WORKING-CONTEXT.md`, `EVALUATION.md`, `REPO-ASSESSMENT.md`, `COMMANDS-QUICK-REF.md`, `SPONSORING.md`, `SPONSORS.md`, plus `the-longform-guide.md` / `the-shortform-guide.md` / `the-security-guide.md`. Multi-language READMEs for pt-BR, zh-CN, zh-TW, ja-JP, ko-KR, tr. Appropriate when the audience needs both marketing surface and rich agent-facing context. Constrains: locale README maintenance burden — observed release script bumps version in only two locales, so the others drift.

### Nested `docs/` tree with map in README

A `docs/` directory holds `QUICKSTART.md`, `INSTALL.md`, `CLI.md`, `CONFIGURATION.md`, `ENV.md`, `SLASH-COMMANDS.md`, `PUBLISHING.md`, `QAPLAYBOOK.md`, etc. The README contains a "documentation map" table that routes readers to the right doc. Appropriate when the plugin has many distinct user concerns each warranting their own page; constrains link discipline because case-mismatch bugs (`docs/architecture.md` on disk vs `docs/ARCHITECTURE.md` in a link) only surface on case-sensitive filesystems.

### Layered repo / plugin / skill READMEs (uneven)

Repo-root `README.md` describes the marketplace; a subset of plugins ship plugin-level `README.md` (4 of 10 in one observed sample), and skills ship per-skill `SKILL.md`. `architecture.md` exists at the plugin level for one plugin only (the runtime-heavy one); other structurally substantial plugins lack architecture docs. Appropriate as a target structure but unevenly executed. Constrains: nesting-discipline pattern breaks when intermediate layers are skipped.

### Per-plugin README mixed coverage

In multi-plugin marketplaces, per-plugin READMEs are uneven — some plugins ship one, others don't, with no rule. First-party plugins typically ship one, thin external MCP wrappers usually do not. Skills without a README rely on `SKILL.md` frontmatter for discoverability. Tied to plugin maturity and author attention rather than a discipline rule.

### Minimal consumer-facing README only

A short `README.md` (~1.4 KB) explains the install commands and submission flow. No `CHANGELOG`, no `architecture.md`, no `CLAUDE.md`, no community health files. Appropriate for read-only mirrors with intentionally-routed contribution paths.

### Repo-root README only (no per-plugin)

Single substantial README at repo root; plugins do not ship per-plugin READMEs. Plugin discovery happens through marketplace metadata (`description`, `category`, `tags`) and the README's own plugin matrix.

### Agent-targeted install preamble in README

The README opens with a blockquote-rendered "For AI Coding Agents — Read This First" section containing literal shell commands segmented by OS × scope × agent (Claude Code, Cursor, Codex, OpenClaw). When a user asks their coding agent to install the plugin, the agent fetches the README and gets an unambiguous install recipe at the top. A distinct consumer surface from the human-facing install sections elsewhere in the README — the same install intent encoded twice. Appropriate when agent-driven installs are a major install vector.

### Bilingual content

README is explicitly bilingual (English + Chinese, with anchor-linked language sections). Uncommon in Claude Code plugin READMEs; signals community reach.

### Astro Starlight docs site with auto-generated MDX

A `docs-site/` directory ships a full Astro Starlight site, with generator scripts (`docs-site/scripts/generate-bp-docs.mjs`, `generate-tool-docs.mjs`) that auto-generate MDX from in-plugin sources (best-practice rules in `skills/<skill>/references/*.md`; MCP tool registrations). Published to GitHub Pages via a separate `deploy-docs.yml` workflow with path filters. The docs site is a first-class user-facing artifact in the same repo as the plugin code — secondary build pipeline driven by the same source.

### CLAUDE.md template shipped for consumer projects

A `CLAUDE-MD-TEMPLATE.md` file ships at repo root, intended to be copied into the consumer's own project (not the plugin's own CLAUDE.md). Turns the plugin into a shipped convention: "add this to YOUR project's CLAUDE.md to tell Claude how to use us." Distinct from the plugin's own CLAUDE.md (when present) which documents the plugin's internal development.

### Committed planning artifacts

`IMPLEMENTATION_PLAN.md` (large, 44 KB), `memory/project_*.md` files, and `memory/MEMORY.md` indexes shipped as first-class repo content (not gitignored). The author's working notes, design context, and personal Claude Code memory become public artifacts. Unusual; most repos either gitignore working notes or isolate to `docs/`. Exposes paths and process detail not strictly needed by consumers, but allows the author to pick up where they left off across machines.

### Stale `CLAUDE.md`

A repo-root `CLAUDE.md` references paths and structures that do not exist in the current tree (`mcp/`, `mcp-categories.json` referenced but absent). Generic template scaffolding never updated to match reality. Following it would mislead an agent — the document looks authoritative but isn't.

### `AGENTS.md` as ecosystem-neutral alternative to `CLAUDE.md`

A file targeting "agent tools that look for `AGENTS.md`" — explicit framing as the cross-ecosystem counterpart to Claude-specific `CLAUDE.md`. Observed in a single partner plugin; emerging cross-ecosystem signal.

### `CONNECTORS.md` sibling-doc convention

A de-facto per-plugin file describing bundled MCP servers, cross-referenced from SKILL.md files via relative paths. Not a Claude-spec filename — repo-originated convention spread across many plugins in one marketplace.

### Architecture / design docs

`SPEC.md`, `ADR.md`, `ARCHITECTURE.md` (or lowercase variants) at repo root cover the project's underlying design (e.g., a binary the plugin wraps). Not always mirrored into the plugin subdirectory; sometimes absent entirely or replaced by `RELEASE-NOTES.md`-style files.

### Free-form CHANGELOG

A partner plugin ships a `CHANGELOG.md` as a free-form "Unreleased" list, not Keep-a-Changelog format. Nothing parses it. Most marketplaces lean on GitHub Releases' `generate_release_notes` as their de facto changelog. Or per-plugin `CHANGELOG.md` files in multi-plugin marketplaces resemble Keep a Changelog format (`## [x.y.z] - YYYY-MM-DD` headers with Added/Changed/Removed subsections) but are hand-maintained — no automation aligns the CHANGELOG with `plugin.json` version, so divergence is normal.

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` (replaced by `RELEASE-NOTES.md` or absent entirely) and no `ARCHITECTURE.md` at repo root. Architecture content lives in a `docs/architecture/` directory or in a separate Astro Starlight docs site published to GitHub Pages. Constraint: a reader looking at repo root for the standard three-document set (README / ARCHITECTURE / CLAUDE) finds only README.

### License-declared-but-no-LICENSE-file

README and `package.json` declare MIT, but no `LICENSE` file in the tree. GitHub's license detector returns null. Legal reuse ambiguous — automated tooling (Sourcegraph, GitHub repo card) cannot confirm the license. Common in early single-author plugins. Or no `LICENSE` file, no SPDX identifier; README prose ("provided under Anthropic's terms of service") is the entire license surface — downstream package tooling cannot identify terms. Or per-plugin LICENSE without repo-level LICENSE: each plugin directory ships its own `LICENSE` file (Apache-2.0 boilerplate, byte-identical across internal plugins). Repo root has no `LICENSE`; GitHub API reports `license: null`. README explicitly directs readers to per-plugin LICENSE files.

## Agent-docs synchronization

How `CLAUDE.md`, `AGENTS.md`, and similar parallel agent-facing files stay in sync.

### Shared block with marker-bracketed sync

A canonical `docs/AGENTS.shared.md` is the single source; a `sync_agent_docs.py` script propagates it into `CLAUDE.md`, `AGENTS.md`, and a Cursor `.mdc` rules file between `<!-- BEGIN AGENTS_SHARED -->` / `<!-- END AGENTS_SHARED -->` markers. CI enforces with `--check` mode. Appropriate when the same agent guidance must reach multiple ecosystems verbatim. Constrains: any unique-per-tool content must live outside the markers in the destination file.

### Hand-maintained parallel files

`CLAUDE.md` and `AGENTS.md` exist at the same level with no sync mechanism. Appropriate when the two files diverge intentionally; constrains because drift is silent until a reader notices.

## Licensing posture

Where LICENSE files live and what license applies to which artifacts.

### Single repo-level license

`LICENSE` at repo root applies to everything. Conventional MIT/Apache LICENSE; standard ecosystem shape, suits single-plugin marketplaces and most projects.

### Repo-root LICENSE plus per-plugin duplicates

A repo-root `LICENSE` (e.g., Apache-2.0) governs the marketplace-level artifacts, with identical copies inside primary-owned plugin directories. Vendored-partner plugins ship their own LICENSE file, sometimes a different license (MIT vs Apache-2.0).

### Layered: repo-MIT, plugin-MIT, per-skill-Apache-2.0

Plugin code is MIT, but per-skill content is Apache 2.0 under `skills/<name>/LICENSE.txt`. Granular license delineation inside a plugin. Appropriate when content licensing differs from code licensing (Apache for shareable prompt content, MIT for tooling). Constrains: every skill must ship its own LICENSE.txt; mixed licensing requires consumer awareness.

### No repo-root LICENSE; per-skill LICENSE only

`LICENSE.txt` (Apache-2.0) inside each skill directory; nothing at repo root. GitHub's license detector returns null. Marketplace-level artifacts (marketplace.json, README, workflows) are under no declared license.

## Multi-runtime portability

How the plugin supports parallel runtimes (Claude Code + Cursor + Codex + OpenCode + Gemini + Copilot CLI) from one repo.

### Per-runtime manifest directories

Repo hosts `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/` top-level directories, each with its own `plugin.json` (or runtime-specific equivalent). Hooks are duplicated across runtimes with naming-convention differences: Claude `hooks.json` uses PascalCase event names (`SessionStart`, `PreToolUse`); Cursor `hooks-cursor.json` uses camelCase (`sessionStart`, `preToolUse`); Codex bash launchers inline a multi-location plugin-root discovery routine because Codex lacks a `${PLUGIN_ROOT}` env var. Same source, different syntax — drives the need for a single-source-of-truth compiler upstream.

### Parallel manifests for Claude + Cursor + Codex

The repo ships `.claude-plugin/marketplace.json`+`plugin.json`, `.cursor-plugin/plugin.json` (richer — explicit component paths, `displayName`, `publisher`, `logo`, `category`, `tags`), `.codex-plugin/plugin.json` or `.codex/config.toml`, plus an `AGENTS.md`. Each ecosystem reads its own manifest. Appropriate when the plugin's value is portable across agent CLIs and the author commits to maintaining each surface. Constrains because configuration that should be shared (`userConfig`, version strings, skill paths) is duplicated across manifests with no sync — drift surface scales with ecosystem count. A build script (`scripts/gen-targets.ts`) may regenerate mirrored skill content into `.claude/skills/`, `skills/`, `codex-skills/`, but a hand-edited mirror is the default starting point.

### Skill content mirrored under multiple paths

The same skill files appear under `.claude/skills/`, top-level `skills/`, and `codex-skills/`. A regeneration script copies between locations. Appropriate when each ecosystem expects a different canonical path; constrains because hand-edits to one location must be regenerated to the others.

### Polyglot wrapper for cross-OS hook invocation

See *Bin-wrapped CLI distribution > Polyglot CMD/bash wrapper*. The wrapper itself is a portability mechanism — one file invoked by both Windows `cmd.exe` and POSIX `bash` to dispatch hooks consistently across OSes.

### POSIX-only with no Windows story

Plugin ships only nix-style paths (`venv/bin/python`, `#!/usr/bin/env bash`). No Windows path branch, no `.cmd`/`.ps1` pair. Acceptable when the plugin's target domain is itself POSIX-only (e.g. iOS / Android simulator tooling). Loud failure mode on Windows: `.mcp.json` referencing `venv/bin/python` won't resolve at all. README typically declares minimum runtime versions but not OS support.

## Distribution channels

Where the artifact ends up published / how end users consume it.

### Marketplace only

Plugins are installed via `/plugin marketplace add <owner>/<repo>` and that's the only intended path. No PyPI, no Docker, no git-clone instructions for the plugin functionality itself. Dominant pattern.

### Marketplace + git-clone-only

Plugin metadata exists for Claude Code's plugin system but the primary install path documented in README is "clone the repo + paste this `.mcp.json` template into your own project, substituting your own absolute paths." Per-client templates for Claude Code / Cursor / Windsurf / Cline. The plugin is explicitly marketed as MCP-portable, not Claude Code-specific. The `.claude-plugin/plugin.json` becomes secondary; the load-bearing config is whatever the user pastes.

### Multi-registry: PyPI + MCP Registry + ghcr.io + Claude marketplace

Same plugin published to four discovery surfaces with four manifest formats: `plugin.json` for Claude Code, `server.json` for the official MCP registry, PyPI metadata via setuptools-scm, ghcr.io image (multi-arch). A separate `glama.json` (three-line maintainer declaration) targets glama.ai's MCP server directory as a fifth surface. The bump script keeps the local manifests in lockstep; CI handles the publishes. Appropriate when the author wants the server to be installable from whichever ecosystem the user already lives in.

### Dual-distribution: marketplace + npm

The same source ships as both a Claude Code plugin marketplace entry and an npm package (e.g., `ecc-universal`), with the npm `files:` list including the entire plugin payload. Users can `npm install -g <pkg>` or use the plugin marketplace. Appropriate when the audience overlaps with npm consumers. Constrains: every release must satisfy both packaging contracts (the npm publish gate is an additional release-time check).

### Cross-ecosystem multi-harness distribution

The same plugin payload also ships via parallel manifests for sibling AI harnesses (Codex, OpenCode, Cursor, Gemini), each with its own version-bearing file. The release script lists all of them as version-locked. Appropriate when the plugin is intentionally portable across harnesses. Constrains: cross-ecosystem manifest sync (validated by `validate-install-manifests.js` in one observed sample) becomes a CI concern; sibling-ecosystem changes ripple back into the Claude release.

### Homebrew formula generated by release workflow

The release workflow synthesizes a Homebrew formula via heredoc (with per-platform URLs and sha256), clones a sibling `homebrew-tap` repo with a PAT, commits `Formula/<name>.rb`, pushes. The plugin is one channel; the tap is another. Orthogonal to the plugin but worth noting as an additional distribution surface for users who want the underlying tool system-wide.

## Contribution posture

How the repo invites or routes external contributions.

### Open contribution with health files

`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` present; PRs welcomed and reviewed. Appropriate for community-driven projects.

### Anti-contribution with auto-close gatekeeper

`pull_request_target` workflow checks the PR author's collaborator permission via GitHub API; if not admin/write, posts a canned redirect comment to a submission portal and closes the PR with `pulls.update({state: 'closed'})`. No `CONTRIBUTING.md` to make the gate discoverable in GitHub's UI; the README carries the routing message. Appropriate for read-only mirrors with submissions accepted via a separate portal. Constrains: first-time visitors may not realize direct PRs are unwelcome until the auto-close fires; the `pull_request_target` trigger runs with repo-scoped secrets so the inline script must avoid checking out PR code.

## Locale and content-style enforcement

How a project enforces written-content conventions beyond syntax.

### Australian English mandate with lint check

`CLAUDE.md` and per-plugin tests prescribe Australian English (`colour`, `optimise`, `behaviour`, `organisation`) in narrative text, with a `tests/lint/test_australian_english.py` lint module enforcing the rule. Appropriate when the project has a defined audience locale and wants to keep the voice consistent. Constrains: contributors from other locales must adapt; lint mechanism (word-list grep, regex, AST?) shapes the false-positive rate.

## Template-customization mechanism

How a plugin offers human-customizable templates separate from Claude's runtime config-substitution syntax.

### Placeholder-token convention

Generic plugins use placeholders like `~~jira` or `~~your-team-channel` as customization markers. A "customizer" skill walks the user through replacing tokens with their organization's specifics. Distinct from `${user_config.KEY}` substitution — a separate human-in-the-loop templating layer that the customizer skill processes.

## Bundled static asset delivery

How a skill ships non-code assets (HTML, images, templates) and gets them to the user's working directory.

### Skill-instruction-driven copy

A static asset (e.g., `dashboard.html`) lives inside the skill directory and SKILL.md instructs the model to copy it from `${CLAUDE_PLUGIN_ROOT}/skills/<name>/<asset>` to the user's cwd at first invocation. Not a canonical plugin component type — the skill treats it as a bundled asset and the model executes the copy via Bash.

## Test stack — Docker

(Cross-role: Docker also surfaces under *Server runtime (MCP)* via `docker run`, under *Distribution channels* via ghcr.io image, and under *Release automation* via the multi-arch build pipeline.)

### Docker Compose for E2E

`e2e.yml` brings up a full Docker Compose stack (e.g., the upstream service + an OIDC provider) before running the e2e-marked subset. Pinned to a single Python version (no matrix) — e2e is an integration check, not a portability check. Appropriate when the system under test is meaningful only against a real running peer.
