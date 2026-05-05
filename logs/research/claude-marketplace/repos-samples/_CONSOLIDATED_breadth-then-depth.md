# Sample

Merge of 3 partials into `_CONSOLIDATED_breadth-then-depth.md`. Functional roles with implementation paths and qualitative descriptions; no inline citations (see `references` verb for provenance).

## Marketplace manifest layout

Where the marketplace-discovery JSON lives in the repo, what shape it takes, how many manifests coexist relative to the plugin trees they advertise, and what wrapping object their top-level metadata takes.

### No marketplace manifest (plugin source repo only)

The repo carries only `.claude-plugin/plugin.json`; no `marketplace.json` exists anywhere in the tree. Installation is local-directory via `claude --plugin-dir <path>` or `git clone` plus manual `.mcp.json` template paste, or out-of-band: a separate (often privately-controlled) marketplace-aggregator repo lists the plugin and points at this repo as a source. The plugin repo is a leaf source, not an aggregator. Cross-repo aggregator dispatch — where the plugin repo's release workflow fires a `repository_dispatch` event (e.g., `plugin-release` with `{plugin, version}` payload, authenticated by a `MARKETPLACE_TOKEN` PAT scoped to the aggregator) — is one common pairing. Appropriate when the author wants the plugin repo to look like a normal source repo (npm-publishable, no marketplace concerns) and centralizes discovery in a separate aggregator they control. Constrains forks (without the cross-repo dispatch token, a fork cannot fully release) and constrains discoverability fields (`category`/`tags`/`keywords` may live only on the aggregator side, invisible from the plugin repo). Discoverability metadata may live in a sibling `package.json` for npm-style aggregators, leaving any marketplace consumer that reads only `plugin.json` blind.

### Self-referential single-plugin marketplace at repo root

A single `.claude-plugin/marketplace.json` co-located with `.claude-plugin/plugin.json` at repo root, with one plugin entry whose `source` is `"./"` — the marketplace and its sole plugin share the same repo root. The marketplace exists only to satisfy the install protocol; the catalog name is a thin wrapper around the plugin name (`<plugin>-marketplace`, `<plugin>-local`). The marketplace manifest may declare `metadata.{description, version}` or only flat top-level fields; either way it advertises one entry pointing back at the same root. `metadata.pluginRoot` is omitted because the plugin already lives at repo root. `$schema` may or may not be present — when absent, schema-aware editors lose autocomplete. Lowest-overhead pattern: one `git push` ships both the storefront and the wares. Appropriate when one repo ships exactly one plugin and the author wants the repo itself to be installable as a marketplace. Constrains the plugin's filesystem layout to start at repo root — any repo content (CI configs, `node_modules/` after install, contributor docs) sits inside the plugin's filesystem boundary unless filtered. Often produces visually-confusing install strings (e.g. `<name>@<name>`) when repo, marketplace, and plugin names coincide. The "-local" suffix variant signals "developing in place" — users see the suffix in `/plugin install <name>@<marketplace>`. Source-binding gotcha: bare `"."` fails marketplace validation; the trailing slash is required.

### Single root manifest with relative source under `plugins/<name>/`

`.claude-plugin/marketplace.json` at repo root with `plugins[0].source: "./plugins/<name>"` (or `"./plugin"`) pointing into a subdirectory holding the actual plugin. The marketplace is the door to it. Suits repos that anticipate hosting more plugins, that separate plugin source from repo-level scaffolding (docs, dashboard source, dev scripts), or that need the repo to carry non-plugin content outside the plugin tree. Forces a dual-source-tree discipline when paired with packaged-copy layouts (see *Source layout*).

### Multi-plugin owned-aggregator marketplace

A repo-root `.claude-plugin/marketplace.json` lists N plugins under `plugins/<name>/`, each with its own `.claude-plugin/plugin.json` and source tree. Every entry uses a relative source (`./plugins/<name>`); the owner authors all listed plugins. Appropriate when one team ships a coordinated catalog. Contributor convention treats repo-level state (root README, CLAUDE.md, settings.json) as non-shipped infrastructure and the plugin trees as the published artifacts. Constrains release cadence (one repo, one tag stream) and creates per-entry vs per-plugin version-sync surface that needs custom validation. Top-level fields are `name`, `owner`, optional `$schema`, and a `plugins` array; some authors wrap a `metadata` object carrying `description` and (rarely) `pluginRoot`.

### Pure external aggregator manifest

The repo holds only `marketplace.json` + LICENSE + README + minimal CI; every plugin is sourced externally via `url` (full clone with `sha` pin), `git-subdir` (path into an upstream monorepo), or `github` (subpath into a sibling repo). The repo authors zero plugin content — it's a denormalized index. Appropriate as a community directory or curated mirror. Constrains the field surface that survives the aggregator boundary (only `name`, `description`, `source`, `homepage`, occasional `category` are preserved); upstream `version`, `author`, `license`, `dependencies`, `tags`, `strict`, `skills` are dropped and resurface only after install. Pure aggregators routinely have no manifest validation in CI, so relative-source entries pointing at non-existent directories (e.g., `"./<some-name>"` where `<some-name>/` is not in the repo) are not caught at merge time and only surface when a consumer attempts install.

### Nested mini-marketplace inside a plugin directory

A second self-contained `marketplace.json` lives one level deep (e.g., `<plugin-dir>/.claude-plugin/marketplace.json`) listing only the enclosing plugin with `"source": "."` and `metadata.pluginRoot: "."`. The same plugin is reachable two ways — as an entry in the aggregator's root manifest and as the only entry of its own nested marketplace. Suits a host repo that vendors a partner's plugin while letting the partner upstream the same directory to their own repo as a self-contained marketplace. Drift hazard: the nested entry's version field is hand-maintained and observed lagging the plugin's own `plugin.json`.

### Duplicated marketplace manifest at root and nested

Two `marketplace.json` copies coexist — a canonical one at repo root (consumed by Claude Code's `marketplace add`) and a duplicate elsewhere (`.github/plugin/`, `plugin/.claude-plugin/`, or `plugins/<name>/.claude-plugin/`) — with often-identical content but no sync mechanism. Three subcases observed: (a) **deliberate cross-host duplicate** — the same JSON object placed at `.claude-plugin/marketplace.json` (for Claude Code) and `.github/plugin/marketplace.json` (for GitHub Copilot CLI), byte-identical files, two discovery paths, targeting two agentic CLIs from one source without parallel manifests; (b) **vestigial duplicate** — alternate-host path with no observable consumer (aspirational, iteration leftover); (c) **nested-as-version-drift-source** — the nested copy ends up tracking a different version than the root copy (e.g., root `0.6.0`, nested `1.3.4` matching the live plugin version while root lags), with the nested manifest matching reality but unread by the marketplace installer; the duplication is the substrate enabling the drift. Both files may carry unofficial private keys (e.g. `_description`) outside the documented schema. Drift-prone — release commits routinely bump one and miss the other, surfacing as hot-fix commits ("bump repo-root marketplace.json to <version>"). CI manifest-equality checks may cover only one of the two copies. Duplicated marketplace manifests can also carry different facet sets (category on the root, tags on the nested) — only one set reaches the consumer. Appropriate to flag as an anti-pattern when not deliberate cross-host: doubles the manual-edit burden during a release with zero observable upside.

### Parallel non-marketplace inventory

Same repo carries `marketplace.json` AND a separate `config.json` enumerating a strictly larger set of modules + a "skills" axis for an alternate installer (npx self-installer). The two inventories are intentionally disjoint: slash-command flow gets the marketplace subset; npx flow gets the richer config.json menu with its own operations DSL (`copy_file`, `copy_dir`, `merge_dir`, `run_command`).

### `$schema` declaration on marketplace.json

A declarative `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"` field on the marketplace document. No CI step actively validates against the schema in any observed sample, so the field is editor-assistance only — IDEs offer field completion and inline error squiggles. Largely absent across the corpus; an outlier when it appears. Appropriate when an author wants editor-time validation without committing to wire-up of a real schema-validation gate.

### Custom non-schema fields on marketplace entries

Fields not in any documented marketplace schema, used as de-facto extension points. Observed: `images: [url]` carrying marketing-asset URLs, `tags: ["community-managed"]` flag distinct from `keywords` and used as a provenance signal, `bundles` field grouping plugins into named user-facing collections (`quick-start-java`, `core`) consumed only by the repo's own out-of-band installers (web installer, custom CLI). Permissive consumers ignore these; strict consumers reject them. Constrains validator choice — strict schema enforcement breaks. Appropriate as a forward-compatible extension hook when no upstream field exists for the metadata the author wants to expose; constrains: users on the built-in CLI cannot access the extension, and it is invisible to anyone not running the custom installer.

### Redundant metadata sub-object on plugin entries

A nested `metadata: {}` dict on a plugin entry that duplicates sibling fields (`author`, `homepage`, `license`, `keywords`, `category`). Two locations on the same entry carry the same facts; `keywords` and `tags` arrays may also be identical. Constrains validators that want to enforce single-source-of-truth — a drift detector has to either pick a winner or accept divergence. Appears to be a layering accident from generators or from manual edits across two different consumer expectations.

### Top-level `metadata` wrapper variants

Marketplace-level (not plugin-level) descriptive fields the manifest declares — flat top-level fields versus a `metadata` object. Several wrapper shapes coexist across the corpus:

- **Flat top-level fields only** — `name`, `owner`, `plugins`, optional `version` directly on the JSON root. No `metadata` wrapper, no `metadata.description`, no `metadata.pluginRoot`, no `$schema`. Minimal scaffolding.
- **`metadata.{description, version?}` wrapper** — catalog-level fields wrapped, often paired with `owner.{name, url}`. `metadata.pluginRoot` generally absent. The marketplace-level `version` is documented as marketplace-bundle version rather than plugin version and is decoupled from individual plugin's `version`, so it tracks an independent (often stale) cadence — observed cases of marketplace `version: 1.0.0` left frozen while the plugin inside ships `2.0.5`, `0.5.1`, or 35 minors ahead. The `version` field can also serve as a catalog-wide release tag covering plugins that carry no `plugin.json` of their own — a single tag (`v1.0.0`) covers the whole catalog when individual plugin versioning would be redundant.
- **`metadata.{description, version, license}`** — adds license at the marketplace surface, surfacing marketplace identity separately from plugin identity. Exposes a marketplace-level version distinct from plugin versions; license signal at the catalog layer.
- **`metadata.{title, description, categories, tags}`** — richer block adding catalog-scoped categories and tags so the marketplace itself can be browsed taxonomically (independent of per-plugin tags). Adds a second source of truth for description/version that must be kept in lockstep with `plugin.json`.

Consumers expecting a single authoritative version see drift; the marketplace version is rarely surfaced to users so the drift goes unnoticed by maintainers.

## Plugin source binding

How the marketplace entry locates the plugin payload on install — relative path, vendored subtree, externally-pulled source, npm package, or skill-carving over a shared root.

### Relative source pointing to repo root (`./`)

`"source": "./"` on the marketplace entry; plugin root and repo root are the same path. Pairs with the self-referential single-plugin marketplace pattern. Trailing slash is mandatory — bare `"."` fails validation. Trivial to author and audit; works only when the repo hosts exactly one plugin at root and ships nothing the plugin doesn't include. No remote re-fetch — install resolves entirely from whatever ref the consumer added. Makes `plugin.json` the de-facto version-of-record (per docs convention for relative sources), but does not prevent the marketplace entry from carrying its own `version` field that drifts.

### Relative source pointing to subdirectory

`"source": "./plugin"` (or similar relative path) when the plugin payload lives in a subdirectory of the marketplace repo. Used when a marketplace publishes multiple plugins that share contributor docs, vendored dev toolkits, or cross-cutting build infrastructure, OR when the repo carries non-plugin content (docs, dashboard source, dev scripts) outside the plugin tree. For relative sources the docs say `plugin.json` wins on version; the marketplace entry is the discovery surface. With `strict: false` set explicitly, the entry permits components beyond canonical roots (root-level `CLAUDE.md`, `SKILL.md`, custom directories like `prompts/`, `algorithms/`, `templates/`). With `strict` left default-true, the manifest at `.claude-plugin/plugin.json` carries the entire registration burden.

### `source: github` with explicit coords or `ref` pinning

The marketplace entry references a GitHub repo by `owner/repo` (or as `repo` plus optional `ref`); `/plugin install` clones the repo at HEAD or at a specified ref. When `ref` is set to a moving branch (e.g. `main`), every install resolves to whatever tip-of-branch is at install time — no pin story, users always get latest. Implies `strict: true` (default) so the plugin manifest must live at the canonical `.claude-plugin/plugin.json` path inside the source. Variant `{source: "github", url, path}` binds to a subdirectory of a sibling repo where the plugin tree lives apart from the rest of the source (e.g., binaries and aggregator metadata in different repos). Forks are first-class — install URL changes, install path same. Installs survive registry outages but depend on GitHub availability. Appropriate when the plugin author wants direct fork-friendliness and is willing to push releases as git refs rather than registry artifacts. When the plugin lives under a non-root path and no marketplace.json exists in the same repo, any external marketplace that lists this plugin must author a `source: { source: "github", repo: "<owner>/<repo>", path: "<subdir>" }` entry by hand.

### Direct git install (no marketplace.json in source repo)

Users install via `claude plugin install github:<owner>/<repo>` — no marketplace-level binding because no marketplace.json exists in the plugin repo. The cross-repo aggregator handles binding separately.

### `url` clone with `sha` pin

`source` is an object `{url, sha}` cloning an external repo at a specific commit. SHA pinning is universal in this path — pinning is the contract. Appropriate when aggregating external plugins; produces deterministic consumer state per marketplace snapshot. Constrains the aggregator to a sync workflow that updates SHAs on cadence. A `url`-source entry without a `sha` field accepts whatever is at HEAD of the upstream repo — non-reproducible installs that surface as drift from convention rather than an intentional "track main" choice.

### `url` self-referencing source

`{"source": "url", "url": "https://github.com/<owner>/<repo>.git"}` where the marketplace manifest points back at the same repo it lives in. The marketplace and plugin payload ship together but the marketplace install treats the repo as a remote source. A locally-cloned-but-uninstalled checkout isn't usable as a marketplace source without `url` rewriting or switching to `relative`. Appropriate when the project plans to publish to a wider marketplace but isn't yet there.

### `git-subdir` into upstream

`source` is `{source: "git-subdir", url, path, ref [, sha]}` reaching into a path inside an external monorepo. `url` is mixed in practice — bare `owner/repo` slug or full `https://`. With a `sha` pin this is the only source kind that gives reproducible installs across time; with only `ref` defaulting to `main` it floats with upstream. Combined with bot-maintained SHA bumps (see *Source-pin maintenance* under *Marketplace validation*), this is the recipe for a curated catalog of upstream content with predictable refresh cadence. Constrains determinism: branch-floated entries move whenever upstream pushes.

### `git-subdir` self-pointing

A `git-subdir` source whose `url` is the same repo as the marketplace manifest, with `path: <subdir>` naming a subdirectory. `plugin install` re-fetches the plugin from GitHub even when the consumer has already cloned the marketplace — a network round-trip that a `relative` source would avoid, but `git-subdir` permits standalone marketplace-add without expecting users to clone. Appropriate when the author wants users to install via `claude plugin marketplace add <owner>/<repo>` directly without cloning. Trade-off is the redundant fetch when a clone already exists locally.

### Vendored-partner subtree

Plugin entries point at `./<root>/<partner-name>` directories whose code is authored by an external partner but lives inside the host repo's tree, with the partner's own LICENSE and author attribution. Distinct from external `url`-source entries — partner code is vendored into the host's tree rather than pulled remotely. Sync mechanism (manual pull vs scripted) is not visible from the repo content alone.

### `source: npm`

The marketplace entry is `{ "source": "npm", "package": "<name>" }`; `claude plugin install` resolves the package against the public npm registry. Constrains the plugin to be a Node package and pulls in npm's distribution surface (CDN propagation delay, dist-tags, `npm unpublish` risk). A user cannot install a fork or PR until the fork is published to npm under a different name. Appropriate when the plugin is fundamentally a Node CLI with broader reach than just Claude (the same package powers Claude Desktop, Cursor, OpenCode, etc.); the Claude plugin entry is then a thin alias of the npm package.

### Skill-carving via shared root + `skills` override

Multiple distinct marketplace entries set `source: "./"` (the repo root) plus `strict: false` (disabling validation of a `.claude-plugin/plugin.json` at the root) plus `skills: ["./<skill-dir>"]` on the entry itself. The marketplace entry replaces `plugin.json` for skills — supplying name, description, category, tags directly — and lets one repo host many skills without a per-skill `plugin.json` wrapper. Two adoption shapes coexist: single-skill carves from a shared repo root (three sibling plugins all reading from the same root, each carving exactly one skill directory) and hollow umbrellas where the entry carries full component config (e.g., `lspServers: {...}`) and the plugin directory holds only `README.md` + `LICENSE`. Trade-off: no per-skill versionable manifest; bumping a skill's version requires re-releasing the whole repo.

### Mixed-provenance composition

A single `plugins[]` array hosting in-repo, vendored-partner, and externally-pulled entries simultaneously — three provenance tiers in one manifest. Distinct from pure inline marketplaces or pure aggregator marketplaces. Allows the marketplace to be both author-of-record (for in-repo content) and broker-of-record (for external content). Constrains the bump/release story per source kind; only `git-subdir` (with `sha`) is reproducibly pinned.

### `strict` field default

Across the corpus, `strict` is absent on every marketplace entry, taking the implicit-true default. Whether authors intended strict mode is generally not documented. `strict: false` set on a plugin entry without a corresponding `skills`/`agents`/etc override array reads as defensive ceremony or copy-paste; semantically unnecessary for normal discovery — `strict` only matters when carving components out of a non-standard layout. The marketplace entry rarely overrides the plugin's component layout — no skill-carving, no path remapping — except in skill-carving / hollow-umbrella shapes; full plugin trees ship as authored.

## Source layout

How the files the plugin needs at runtime are organized in the repo, independent of how the marketplace entry binds to them.

### Single tree (plugin equals repo)

Plugin manifest at `.claude-plugin/`, components (skills, commands, hooks, agents, bin) at conventional top-level directories. Simplest layout; no synchronization burden. Appropriate when the repo's only purpose is the plugin and there is no separate authoring/distribution distinction. When paired with `source: "./"` self-referential marketplace, the plugin filesystem boundary swallows non-plugin content (CI configs, lockfiles, contributor docs, `node_modules/` after install) unless filtered by `.claude-plugin/ignore` or similar — common when the repo's only purpose is the plugin but consumes-everything semantics is an unintended side effect.

### Dual tree with sync gate

Authoring sources live at repo root (`/hooks/`, `/bin/`, `/audio/`, `/config/`) and a packaged copy lives at `plugins/<name>/...`. A reconciler script (e.g., `build-plugin.sh [--check]`) does `cp + cmp -s` to keep them in sync; CI runs the same script with `--check` to fail PRs that drift. Justified when Claude Code's plugin cache treats `plugins/<name>/` as a self-contained unit but the author wants a cleaner top-level surface for non-plugin tooling, tests, or cross-target packaging. Cost: every change to a hook, bin, or config file is a two-place edit unless the author runs the reconciler.

### Generated manifests from upstream config

Plugin manifests (`plugin.json`, `hooks.json`, `settings.json`, `agents/*`, `monitors/monitors.json`) are emitted by a `sync` subcommand of an in-repo binary that reads a single authored source (`harness.toml`). The committed manifests are derived artifacts; a CI consistency check verifies the working tree matches what `sync` would produce. Inverts the usual "manifest is hand-authored" assumption; appropriate when the plugin's surface is too large or schema-fragile for hand maintenance and when a custom binary already exists to interpret the upstream config.

## Per-plugin discoverability metadata

Searchable, filterable, and categorizable fields on the plugin entry inside the marketplace and on `plugin.json` — what a marketplace consumer indexes to make plugins findable.

### Bare-minimum (name, version, description only)

The plugin advertises only `{name, description, version}` in `plugin.json` — no `category`, `tags`, `keywords`, `author`, or `repository`. Marketplace entry, when present, mirrors this minimum or carries only the fields required to install. Discoverability is fully delegated to whichever marketplace aggregator carries the entry, OR carried by description prose and any external surface (README, GitHub repo topics). Workable when an external aggregator supplies metadata, but ships zero plugin-self-described discovery facets. The bare-minimum can be either well-formed (all required fields present, valid SemVer, intentionally minimal) or defective (non-SemVer shorthand like `"version": "1.1"`, missing `version` field entirely on individual plugins). Defective bare-minimums survive only because Claude Code's manifest validation is currently lenient; a stricter validator would reject them.

### Keywords-only on plugin.json

Marketplace entry carries minimal metadata (`name`, `version`, `source`, `description`); `keywords` lives exclusively in `plugin.json`. No `category` or `tags` on the marketplace surface, so category-based browser filters cannot surface the plugin. Authoring overhead is low (one list, one location), at the cost of marketplace-side filterability. Often paired with `plugin.json` carrying a slightly different `keywords` list creating a second drift surface.

### Category-only

Each entry carries `category` (commonly `"productivity"`, `"development"`) and no `tags`/`keywords`. Single-axis classification for a small fixed taxonomy. Sometimes paired with a `homepage` deep-linking to `/tree/main/plugins/<name>`. Appropriate when the catalog is small enough that browsing-by-category beats keyword search, and the author wants a controlled vocabulary.

### Category + tags pair

Every entry carries `category: "<single-string>"` plus `tags: [...]`; `keywords` unused. Uniform across all entries; suits a focused-domain marketplace where one category fits all and tags differentiate within it.

### Description + version + author + keywords

Mid-richness entry: human-readable description, semver `version` (duplicating the plugin's own `plugin.json` version), `author` block, and a `keywords` array of 5-11 terms. No `category` or `tags`. Sibling entries in the same marketplace can drift between this richness and description-only — no enforced schema across siblings.

### Marketplace-entry facets plus duplicated keywords on plugin.json

The marketplace entry declares `category` (single string, commonly `"productivity"`) and `tags` (array — e.g., `["team", "agents", "automation", "project-management"]`); `plugin.json` independently carries `keywords` with semantically identical values. Two field names for the same intent across two manifests — drift surface but no enforcement. Two discovery vocabularies with no single source. A search via one surface misses tokens only present in the other; no tooling reconciles them.

### Multi-dimensional (category + keywords + tags)

All three dimensions populated for a single plugin, giving overlapping facets for marketplace browsers. `keywords` is the long form (project-specific terminology, ~10 terms), `tags` shorter and ecosystem-oriented (`claude-code`, `cursor`, `codex`), `category` a single bucket. Marketplace entry sets `category`, `tags`, `keywords`, `description`, `author`, `homepage`, `repository`, and `license` together; `plugin.json` mirrors fields at the plugin layer. Plugin appears in browsing flows that filter by any axis. Tags and keywords overlap heavily — sometimes byte-identical duplicates, the author either not knowing they serve different purposes or hedging across tooling that may read one and not the other. Increases discoverability surface area and synchronization burden — three lists drift independently. Appropriate for plugins seeking maximum discoverability; cost is duplication burden when the marketplace entry mirrors fields already in `plugin.json`.

### Description-only with sparse opt-in category

Only `description` is universal across entries; `category` appears on a small minority (≈3% in one mirror) with inconsistent capitalization (`development` vs `Developer Tools`). No tags, no keywords. Appropriate when the catalog is too large for any author-supplied taxonomy to stay coherent, but produces an uncontrolled vocabulary even among the opt-in subset.

### No discoverability fields on marketplace entry

Marketplace entry exposes neither `category` nor `tags` nor `keywords`, even when `plugin.json` has its own `keywords` array. The `$schema` reference may still be present (the schema does not require these fields). Plugin is reachable only by direct install URL; browsing flows will not find it.

### Mixed-by-origin metadata

Different field sets per provenance tier in one `plugins[]` array — primary-owned entries use only `name` + `source` + `description`; vendored-partner entries add `author.name`; externally-pulled entries variably add `category` and `homepage`. No uniform shape across the array, which makes client-side schema validation awkward but reflects that the marketplace acts as an aggregator over heterogeneous sources.

### Cross-file category drift

`category` declared on both the marketplace entry and `plugin.json` with no automated sync — the two values drift (e.g. `"mobile-development"` on the marketplace entry vs. `"development"` on `plugin.json`). Unlike `version`, which is commonly guarded by sync scripts, `category` has no enforcement, so drift goes unnoticed.

### Repo-level GitHub topics

GitHub repository topics (`agent-skills`, `ai-coding`, `semantic-search`) declared on the GitHub repo itself, not in any manifest. Drives GitHub search but not Claude Code's marketplace UI. Useful complement to manifest discoverability when the project also wants discoverability through GitHub's surface.

### `$schema` absence on per-plugin manifests

`$schema` URL absent from `plugin.json` across most of the corpus. Editor schema-completion and ahead-of-time validation are unavailable; reactive detection (install errors, CI gates) is the only feedback channel.

## Version coordination

Where the canonical version of a plugin lives, how many parallel version streams exist, what enforces lockstep, and how drift is detected — drift is the dominant failure mode.

### Single source of truth (`plugin.json` only)

`plugin.json.version` is the only user-facing version of record; the marketplace entry omits a version field. Users who want to pin must do so at the Git ref level (`@<sha>` or `@<tag>`). Eliminates drift risk by construction. A `pyproject.toml` may carry its own `version` field that drifts (frozen at `0.0.1` while plugin.json advances) — not consumed by anything user-facing, only by pip metadata, so the drift is immaterial. Single-source clarity; risk lives only in tag-vs-manifest drift, not in cross-file drift. CI scripts may parse marketplace entries and warn if a `version` is missing, surfacing intent without enforcing it. Per-plugin discipline only — `plugin.json` may itself drift from a CHANGELOG or a SKILL.md frontmatter version field maintained by the same author. Rare in the observed corpus — most samples maintain at least two independent copies.

### Dual-file version (manifest pair)

Both `plugin.json` and `marketplace.json` carry `version`. The pair must be edited together on every release; a single-file edit produces drift the install path will not catch. Drift is detected by humans or by a CI consistency script (`sync-versions.sh` or equivalent). The script can also regex-scan source for hardcoded version literals (regression guard against re-introducing inline `version: "x.y.z"` strings the runtime is supposed to read from a manifest) and validate that the new version is a legal semver bump. CHANGELOG narration in some samples explicitly documents shipping a release where some sites updated and others didn't, motivating retroactive addition of CI version-bump checks.

### Dual-manifest versioning with CI gate

`package.json` (npm) and `.claude-plugin/plugin.json` both carry the version because both ecosystems insist on owning it. Neither derives from the other. CI enforces equality with a `Verify version sync` step that fails the build when they differ. CLAUDE.md prescribes "after bumping plugin.json, also update package.json before creating the GitHub Release." A "two sources, one gate" pattern, distinct from single-source-of-truth derivation.

### Triple-file version (build manifest joins)

Three sites carry the version: `plugin.json`, `marketplace.json` (often two slots — top-level `metadata.version` plus `plugins[i].version`), and the language ecosystem's build manifest (`Cargo.toml`, `package.json`, `pyproject.toml`). Drift mitigated procedurally — by a documented release skill, a manual checklist, or by convention — rather than structurally. Hot-fix commits explicitly titled "bump repo-root marketplace.json to <version>" surface when the discipline slips. Release CI may gate `tag == package.json.version` only — drift between `package.json` and the plugin-side manifests is not caught structurally. The sibling-harness manifest (`gemini-extension.json`) can join as a third site in cross-ecosystem distributions. Contributor docs may designate one pair as the "must match" pair and treat marketplace metadata version as an independent stream tracking the marketplace itself — three-way version space with two enforced relationships and one independent axis is the most version-aware shape and also the most drift-prone.

### Multi-file with bump script as enforcer (multi-registry)

Version lives simultaneously in `server.json`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and a regex-pinned arg in `.mcp.json` (e.g. `uvx mcp-outline==<ver>`). A `scripts/bump_version.py` rewrites all four atomically and validates semver-bump legality. Appropriate when the repo publishes to multiple registries (Claude Code marketplace + MCP registry + PyPI) that each demand the version in their own manifest format. The script is the single source of truth at author-time; structural drift is prevented by always running it instead of editing files individually. CI does not necessarily re-run the validator, so a manual edit to one file leaves the others behind silently.

### Multi-site sprawl (5+ locations)

Version scattered across `plugin.json`, two slots in `marketplace.json`, a top-level `VERSION` file, the language build manifest, README badge(s), CHANGELOG, hardcoded source-code literals (e.g., MCP server's `version: "0.1.0"`), CLAUDE.md "Current version" line, hook banners (e.g., `echo '...v2.0.0...'` baked into a SessionStart hook payload), and sometimes mock-output version inside test fixtures. No generation or sync mechanism; each release is many hand-edits. Cross-format encoding compounds the problem: the same conceptual version may appear as `5.0.0-alpha` (semver), `5.0.0a1` (PEP 440), and `v5.0.0-alpha` (tag) in three different surface forms; each ecosystem's sort/normalization rules differ, so a bump tool must emit each form correctly. A `scripts/bump-version.sh <new>` (when present) patches all sites in one invocation; CLAUDE.md additionally maintains a "Version Sync Checklist." Atomic-bump scripts may regex-rewrite pinned literals inside arg arrays (e.g. `==<ver>` inside `.mcp.json`) in addition to JSON field assignment. The script can be substrate-fragile (e.g., `sed -i ''` BSD-syntax fails on GNU Linux sed) — author's local platform leaks into a shared release tool. Variant: "no sync mechanism at all" — five-way version sprawl with no bump script, no CI gate, and no pre-commit hook, where every site is edited independently and drift is the default. Distinct from `Multi-site drift accepted as cosmetic` (deliberately tolerated divergence) by being unintentional. Solves the multi-file problem with project-local tooling rather than runtime indirection.

### Atomic-bump release script with pre-push gate

A local-only Python or Node script (e.g. `scripts/publish.py`, `scripts/bump-version.mjs`, `scripts/sync-version.js`) bumps every version-carrying file in one step, then re-runs the schema validator post-bump to confirm parity. Generalizes to ~15 manifests/HTML pages syncing from one source (`package.json` as authority). The same script in `--check` mode runs in pre-commit, CI, and publish workflows to fail builds on drift. A process-ancestry pre-push gate (walks `ps -p <pid> -o args=` rejecting any push not driven by the script) prevents the gate from being bypassed; env-var/marker-file schemes are "trivially spoofable" by comparison. Constrains every contributor to either run the writer script before commit or accept a CI failure. Appropriate when the version surface is genuinely large and a per-file manual checklist would be impractical.

### Pre-commit hook auto-sync (consistency, not increment)

Git pre-commit hook (`.githooks/pre-commit` installed by `scripts/install-git-hooks.sh`) detects mismatch between a `VERSION` source-of-truth file and `plugin.json`/`harness.toml` and runs `sync-version.sh sync` to mirror, re-staging the corrected files. Does not auto-bump; bump itself is manual via `sync-version.sh bump [patch|minor|major]`. The hook only enforces consistency, not increment. Pre-first-release projects (`0.0.z` until first `v0.1.0`) sometimes auto-bump `z` per commit via this hook to keep reload-detection firing.

### Manual checklist with rubric-based audit

No bump automation; release-prep PRs hand-edit each version-carrying file (5+ files: `plugin.json`, marketplace.json, README badge, README.ru badge, per-skill `metadata.version`). A separate machine-checked rubric (e.g. `tests/meta_review.py` gates `M-C5`/`M-C6`) runs in CI and validates that all files agree on a single version. Catches drift but does not prevent it. The rubric is the safety net rather than the guard rail. Appropriate when the maintainer prefers explicit-edit discipline and treats CI as the late-stage drift detector.

### Cross-ecosystem version sprawl

A release script enumerates many version-bearing files (one observed sample lists 17: `package.json`, `package-lock.json`, multiple `AGENTS.md` locale variants, `agent.yaml`, `VERSION`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, sibling-ecosystem manifests for Codex/OpenCode/Cursor/Gemini, README locales, architecture docs) that must move atomically. Appropriate when distributing the same plugin across multiple AI-harness ecosystems. Constrains release engineering: adding a new version-bearing manifest requires editing the script; CI tag-verification typically only checks one file, so drift between others isn't caught.

### Cross-runtime version multiplication

When the same plugin ships under multiple runtimes, each runtime's manifest carries its own version field. A repo supporting Claude + Cursor + Codex maintains `version` in `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, the marketplace entry, and any runtime-specific install hint. Hand-discipline alignment with no cross-manifest validation; commit history shows explicit "align cursor plugin version to match claude plugin" commits as the only enforcement mechanism.

### Cross-repo registry-side sync

The marketplace listing in a sibling repo is a third version sync point, kept in lockstep via a webhook-style notifier (`repository_dispatch` `plugin-updated` event, PAT-gated, fired on `.claude-plugin/plugin.json` change). Constrains the publish flow to a cross-repo coordination dance even after intra-repo bumps are clean.

### Multi-runtime fan-out (single source compiled to N artifacts)

A single source file (`plugin.universal.yaml`) is declared the source of truth and compiled by an external tool into per-runtime manifests (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, plus the `hooks.json` family). Five-plus version copies in the tree at any time. The compiler is not vendored or pinned, so the compile step is a user-side build no CI verifies — observed drift in practice (universal yaml at one version while compiled artifacts have moved on).

### Independent semver streams (sub-package versioning)

Multiple semver tracks coexist in one repo: the plugin itself, and one or more sub-packages (Node MCP server with its own `package.json`, etc.). Each bumps independently with its own changelog discipline. CHANGELOG explicitly reconciles them ("MCP server bumped to X.Y.Z while plugin is at A.B.C"). Plugin-level sync scripts do NOT cover the sub-package — it's intentionally outside the synchronized set, with its own release cadence.

### Multi-artifact lockstep across N>2 manifests

Version mirrored across plugin manifest plus one or more sibling artifact manifests — `package.json`, `pyproject.toml`, firmware `.fam` `fap_version`, source-embedded version strings (`ui.c` constants, Go `-ldflags`-injected vars). Coordination via a release checklist or `Makefile` `release` target; no structural verification. Appropriate when the plugin is one artifact among several in a multi-product repo. Constraint: a release commit must touch every artifact's version field or one of them silently lags.

### Marketplace-side pin via source ref

In aggregator marketplaces, `source.sha` (for `url`) or `source.ref` (for `git-subdir`) is the version contract. Upstream `plugin.json` versions are not surfaced. Appropriate when the marketplace cannot trust upstream version discipline. Constrains the user: the only pinning surface is the source ref the aggregator sets. Defect signal: a `url`-source entry with no `sha` field on a manifest where every other entry pins explicitly is a non-reproducible install for that one entry — yields tracking-HEAD installs, which can be deliberate ("this one tracks main") or an authoring oversight; the manifest does not distinguish the two intents. The marketplace-entry version field, when present alongside source-ref pinning, is purely informational and silently stale: for relative sources Claude Code uses `plugin.json` as authoritative, so the marketplace-entry version drifts when release tooling forgets to update it.

### Tag-stamped at release time

A release workflow extracts `version` from a `plugin-v*` tag name and writes it into `plugin.json` during packaging. One-way coupling from tag to manifest ensures consistency at the tagged commit, but intermediate `plugin.json` changes (between tags) ship without the validator.

### Pinned manifest version, floating release tag

Every `plugin.json` holds a hardcoded version (e.g., `"1.0.0"`) regardless of release cuts; the release tag (`v1.1.1`) lives only on git tags and release-asset filenames. `plugin.json` is treated as written-once-at-introduction; consumers' source of truth is the tag.

### Deliberate divergence: wrapper vs underlying binary

`plugin.json.version` tracks the plugin wrapper release; the underlying binary version floats to upstream HEAD via runtime resolution. Designed to let the binary iterate without forcing plugin bumps. Distinct from a drift defect — the manifest declares "wrapper 1.5.0" while the binary it installs is whatever is freshest. The dual-tag-namespace release mechanism (see *Tag and release lifecycle*) supports this directly.

### Tag-on-main with synthesized dev version inside binary

Plugin manifest carries plain semver tracking releases. Dev builds of an embedded binary synthesize a `-dev.N+sha` suffix at build time via `git describe --tags --match 'v*' --always --long` and `-ldflags`, never applied to git tags. Wrapper script recognizes the dev marker (`version.includes("-dev.")`) and applies looser version-comparison rules. Appropriate when binary builds outpace plugin releases and the wrapper needs to discriminate locally-built vs released binaries.

### Three-way version split (marketplace vs npm vs git tags)

Marketplace + plugin.json (5.6.1), `package.json` consumed by npx installer (6.7.0), and git tags on master (v6.8.2) all carry independent version numbers that drift independently. Each is meaningful in its own context but not reconciled. The npx installer asks GitHub's releases API for `tag_name` at runtime and bypasses the checked-in version fields entirely, so installed artifacts match the tag while a consumer reading the source files sees stale fields.

### Multi-site drift accepted as cosmetic

Five-or-more sites advertise different versions intentionally or accidentally: `plugin.json`, `VERSION`, `pyproject.toml`/`package.json`, CHANGELOG, README badge, hook banners, and the git tag may all be at different versions (e.g. `5.0.0-alpha` vs `4.2.0` vs `2.0.0` vs `3.0.0-dev`). The pattern can be deliberate ("marketplace only advances at stable release") or accidental drift. Pre-release suffix handling (semver vs PEP 440 vs tag) compounds the inconsistency: `5.0.0-alpha`, `5.0.0a1`, and `v5.0.0-alpha` are three forms of the same version that downstream sorting rules may not reconcile. Release process accepts the drift as cosmetic; users see different version strings depending on which surface they look at.

### No plugin-level version

Skill-carving entries have no `plugin.json` at all — only the marketplace entry and `SKILL.md`. There is no per-plugin version concept; the only versionable artifact is the marketplace tag covering all skills together. Or the version field is cosmetic — declared but no automation verifies bump-on-change, no pre-commit hook, no CI gate, no tag-vs-version assertion. Plugins ship at `0.1.0` while peers move ahead independently; breaking changes can land without any version bump.

### Stale fallback constants in code

Bin scripts and hooks read a `VERSION` file with a hardcoded fallback literal for "VERSION file unreadable" — but the fallback drifts from the current version over time, so a broken install displays a number that may be many versions out of date. A symptom of the multi-source version problem: even the centralization attempt embeds a copy. Convention sub-case: every `plugin.json` permanently pinned at `1.0.0` (or other constant) regardless of release-tag activity — release-tag versions live only on git tags and release-asset filenames; for skill-only plugins this is internally coherent (skills have no plugin.json), for MCP plugins it means manifest version is decoupled from release cadence by author convention rather than by defect.

## Channel distribution

Whether the plugin offers stable / latest / dev channels, how consumers pin a version, and whether the channel mechanism operates at the marketplace, branch, or artifact layer.

### Single channel — tag-on-main with git-ref pinning

No channel split; users install via `/plugin marketplace add <owner>/<repo>` and pin via `@ref` (`@main` for rolling, `@vX.Y.Z` for a specific tag, or commit SHA for frozen). Every commit on `main` is a release candidate; tags `vX.Y.Z` land on main. Constrains rollback to git-ref pinning by the consumer rather than channel switching by the publisher. Appropriate for solo or small-scale plugins where formal release ceremony is not warranted; the cost is no easy "give me the last known-good" label without naming a specific tag. Dominant posture across the corpus — consumers implicitly track HEAD. Tags can exist as a pinning surface even when the README's install instructions don't document the `@vX.Y.Z` syntax — release tags become an undocumented pinning option, with HEAD-tracking the de-facto consumer experience. Even high-velocity / high-traffic repos sometimes skip a staging-branch model entirely and rely on tag cadence as the only stabilization layer.

### Tag-pinned with trunk-based releases

Annotated tags on main (e.g., `v1.0.0`, `v1.0.1`, `v1.1.0` with corresponding GitHub releases). Users pin via `/plugin marketplace add ...@vX.Y.Z`. Appropriate for stable-release discipline without channel separation; constrains contributors to a tag-on-main workflow with no in-flight `release/*` branches.

### Linear `0.0.z` dev counter

The repo's only versioning scheme is a monotonic `0.0.z` counter — every tag bumps `z`, with no `0.1.0` carve-out and no parallel `x.y.z` release lane. Tags `v0.0.1`..`v0.0.z` chain linearly on `main`. Appropriate for pre-release / experimental plugins where every commit is essentially a dev snapshot; the cost is no signal of stability and no inflection point to mark "first real release."

### Pre-release tag suffixes on a single channel

Tags carry a `-alpha` / `-beta` / `-rc` / `-dev` suffix to mark pre-release status (e.g. `v5.0.0-alpha`, `-alpha.N`, `-beta.N`, `-rc.N`). GitHub Releases marks the corresponding release `prerelease: true` correctly. PEP 440 form (`5.0.0a1`) appears on `pyproject.toml` for Python tooling compatibility. Code-side helpers (`isPrereleaseVersion()`) feeding `--prerelease` to `gh release create` may exist without any actual prerelease tags published — infrastructure-ready but cold. Users can pin to a specific pre-release tag, but installing from `main` always lands on whatever `plugin.json` currently says, including in-development `-dev` versions. Appropriate when an author wants to ship versioned snapshots without claiming stability; the cost is uncertain handling by Claude Code's plugin semver parser, which is undocumented for pre-release suffixes.

### Pre-release suffix as channel marker (Maven-style)

Maven-style `1.0.0-SNAPSHOT` suffix in `plugin.json` versions during development; stripped at release. Custom version comparator in the repo's installer treats SNAPSHOT as strictly older than the bare release. Not a SemVer pre-release identifier (`-rc`, `-beta`) and not recognized by Claude Code's plugin machinery. Appropriate when the author is borrowing conventions from a host-language ecosystem (Java/Quarkus). Constrains: any consumer not running the custom installer treats `1.0.0-SNAPSHOT` and `1.0.0` as different opaque strings — naive ordering breaks.

### Aggressive minor-only cadence with reactive patch bursts

Every shippable change cuts a minor (10 minors in ~1 month observed); no patch releases, no pre-release suffixes. Implies the project treats every visible change as user-facing. CHANGELOG.md becomes the only durable release-notes artifact since GitHub Releases (when present) are auto-generated from PR titles via `--generate-notes`. Reactive patch bursts (multiple patch releases within hours, e.g., v3.4.1 → v3.4.4 in 36 hours) indicate absence of a buffer between development and release; every push reaches users immediately. Forces tight feedback loops in CI to compensate.

### Single channel with version-reset across rebrand

Plugin moves through major versions under one name, then resets to `0.1.0` under a new name. Users pinned at `<old-name>@vX.Y.Z` do not auto-update because the plugin name changed; the rebrand is communicated via README/CHANGELOG only, not enforced in the manifest. Identity transition is a soft event — the marketplace cannot bridge it.

### Marketplace-cache invalidation hack

Patch-level version bump committed with no functional change, intended solely to force the marketplace cache to re-pull a prior release. Documented openly in CHANGELOG ("Patch bump to force the marketplace to pull v2.3.0's bundled-MCP changes. No code changes vs 2.3.0."). Symptom of having no control over marketplace refresh timing and no immutable release artifact. Variant: hand-bumped version-as-cache-bust where `plugin.json.version` is bumped within feature commits explicitly for cache invalidation (`bump to 1.2.0 for cache bust`) — the version field operating as a refetch trigger for downstream `/plugin update` rather than as a release coordinate.

### Sync-PR cadence with no tags

The mirror has zero tags; "release" is implicit in each merged sync PR. Sync branches (`sync/manual-YYYY-MM-DD`, `sync/auto-vendor`, `sync/batch-plus-N`) merge into main on a weekly batch cadence with growing batch sizes (e.g., 214 → 500 → 814 → 1095 → 1636 entries over weeks of activity). Appropriate for pure aggregators backed by an internal review pipeline. Constrains consumers: the only stable handle is a marketplace-repo commit SHA, which the standard install command doesn't capture by default.

### SHA pinning per external entry

For external `url`-sourced or `git-subdir`-sourced plugins, the `sha` field on each entry acts as a per-plugin pin — the marketplace itself tracks HEAD but each external plugin is frozen at the SHA the maintainer chose. Effectively a per-entry channel pin without a global stable/latest split. Reproducibility lives inside the source kind, not on the manifest as a whole.

### Dual-asset filename aliasing on GitHub Release

Both a versioned filename (`<plugin>-v1.14.1.mcpb`) and a channel-aliased filename (`<plugin>.mcpb`) are uploaded to the same release via `cp`. The channel filename rolls forward with each release; the versioned filename pins. Orthogonal to marketplace channels — operates at the GitHub Release artifact layer. Constrains consumers to choose at download time which lifecycle they want. Appropriate as a lightweight alternative to maintaining parallel `stable-*`/`latest-*` marketplace manifests.

### Floating snapshot binary alongside single-track plugin

The plugin itself is single-track, but a separate binary-distribution release tag (e.g., `snapshot`) is force-recreated on every push to main as a prerelease. Used by a binary-download wrapper as a fallback URL — not a marketplace channel, a binary channel. Appropriate when the plugin ships a downloadable native artifact with a faster cadence than the plugin's semver. Constrains binary consumers caching by tag SHA against the floating tag — they see silent moves.

### Disabled-channel skeleton

Release-channel infrastructure that exists in code but is intentionally inert until the maintainer flips a switch — e.g., `release/*` short-lived branches with a fixture-smoke workflow whose job header carries `if: false` plus a missing `ANTHROPIC_API_KEY` secret. The infrastructure is committed for completeness and discoverability but consumers see a single-channel experience. Documents the future shape without absorbing the cost (paid CI runs, multi-channel maintenance).

### Application-level channels distinct from distribution channels

Some plugins ship a `channels.sh` library inside `hooks/lib/` for the plugin's own feature routing (which rules apply to which projects), independent of marketplace channel distribution. Worth distinguishing — the term "channel" overloads at the plugin and marketplace layers.

### Multi-channel via parallel distribution paths

The plugin is published to more than one delivery surface (marketplace + npm `npx <plugin>@latest` + direct GitHub install) without a unified pinning story. Each channel carries its own version semantics (marketplace uses git refs, npm uses standard semver tags). Cross-host secondary channel via `npx skills` — plugin installable via `npx skills add <owner>/<repo>@<skill-name>` (skills.sh) in addition to the Claude Code marketplace. Two distribution channels for the same artifact, each with its own consumer base. Forces the SKILL.md description to work simultaneously for Claude Code and other agent hosts. Appropriate when the plugin needs to support runtimes outside Claude Code (Cursor/Codex/Windsurf via npm). Constrains: consumers and channels can diverge between tags; an unreleased commit on main may already be visible to marketplace consumers while npm consumers still see the last published version.

### npm registry as de facto channel substrate

A Node-based installer (`bin/install.cjs`) is published to npm so users can `npx <plugin>@latest` or pin `npx <plugin>@<version>`. Versioning effectively delegates to npm's package versioning rather than git tags. Appropriate when the plugin has a Node toolchain anyway; constrains the plugin to publish releases to npm manually, parallel to the marketplace install path. Creates a third install channel alongside marketplace and direct-clone paths — same plugin, different version stories per substrate.

### SessionStart self-update

A SessionStart hook performs `git fetch` + `git merge --ff-only origin/main` against the plugin's own clone, with a 24h cache and an opt-out env var. Two install modes handled by one hook: when the plugin is a git clone (Codex / OpenCode / self-hosted), the hook auto-updates; when installed via a marketplace (Claude / Cursor), the hook instead emits a "run `/plugin update`" notice. Effectively turns SessionStart into a soft auto-update channel for non-marketplace installs.

### Plugin-ref ↔ CLI-version coupling via SessionStart

The plugin ships a SessionStart hook that pins an external runtime tool (e.g., `npm install -g <pkg>@<plugin-version>`). The plugin-ref and the runtime tool's version are coupled at session start, not by a marketplace channel mechanism. Effectively a "channel" that lives in the hook layer rather than the marketplace.

### No pinning surface

No tags, no release branches, no marketplace channel — the only pointer is whatever main HEAD happens to be at clone time. Any consumer has to track commit SHAs out-of-band. Common in early-stage / never-released repos. Bare-plugin `claude --plugin-dir` installs are pinned only by the consumer's checkout SHA.

## Tag and release lifecycle

How the repo cuts version tags, where they sit in git history, and how releases are produced — discipline around tag form, branching, and frequency.

### Tag-on-main, single branch

All version tags sit on `main`'s linear history; no `release/*` branches. Feature branches (`feat/*`, `fix/*`, `chore/*`) merge to `main` via PR; a tag is cut from `main`; release automation (if any) fires on tag push. Appropriate for small-team or single-maintainer repos where the simplicity of one branch outweighs the safety of release branches; the cost is no isolated lane to backport fixes against a previously-shipped version. Implies `main` ≈ release; HEAD consumers see the latest version immediately on every release commit. Tagging happens at the same minute as the underlying commit lands; releases are hand-cut via `gh release create` or the GitHub UI. Cadence can be rapid (multiple bugfix releases within a single day) when blocking issues are caught post-tag.

### Tag-on-main with merge-base ancestry gate

Tag on main, but the release workflow's first step asserts `git merge-base --is-ancestor HEAD origin/main` — failing the publish if the tagged commit is not actually on main. Cheap structural guard against tagging a feature branch by mistake. Pairs naturally with `fetch-depth: 0` in the CI checkout step.

### Tag-on-main with active cadence (semver discipline)

Tags `vX.Y.Z` placed directly on commits merged to `main`. CHANGELOG generated by tools like `git-cliff` (configured via `cliff.toml`) and invoked manually. 18 tags over ~13 months in one observed sample, mostly major v1.x cuts in a burst. No pre-release suffixes used in practice, though the release pipeline reserves `-rc` semantics. Pre-commit hooks include ruff + pytest but no auto-bump. Version bumps are manual via a `poe bump-version` task. Trade-off: gives consumers a pinnable surface but provides no objective gate between "tagged" and "shipped" without CI. Tag-sanity is unenforced — `package.json` or `marketplace.json` version can lag the tags indefinitely.

### Tag-on-main with manual GitHub Release

Tags `vX.Y.Z` live on the default branch; releases are not triggered by tag push but by a GitHub Release `published` event. The author runs `gh release create v<version> --generate-notes` to fire the release pipeline. Tag alone does not ship — the manual release step is load-bearing. Appropriate when release notes need human curation; constrains automation because forgetting `gh release create` silently skips the publish. Recurring symptom: **tag-release count drift** — tags accumulate faster than the manual GitHub Releases catch up (e.g., 10 tags but only 7 published Releases, with intermediate versions like `v2.0.3`/`v2.0.4` having tags but no Release). Pinning by tag continues to work for those drifted versions but pinning by Release does not, splitting the consumer experience by which surface they pin against.

### Tag-on-main with stale side branch

The dominant pattern is tag-on-main, but a side branch (`vX.Y/<topic>`) exists alongside `main` without serving as a long-lived release channel — it looks like an in-flight feature branch that was pushed and not deleted. Appropriate to flag as messiness rather than a deliberate channel pattern: users on `main` get the alpha; the side branch isn't a stable fallback.

### Short-lived `release/*` branches as workflow gate

PR-shaped release-prep branches (`release/v1.x.y`) exist solely to run an expensive workflow that's disabled on main (e.g., fixture-smoke against the live Claude CLI). The branch is merged back and tagged on main. Not a long-lived channel branch. Appropriate when one specific workflow is too expensive or too flaky to run on every main commit.

### Release-codename branches without tag ownership

Long-lived branches named after release codenames (`release/v4.3.0-arcana`) exist but tags land on `main`, not on these branches. The branches snapshot release-prep state and may be behind main by the time the tag is cut. Differs from the typical `release/*` pattern that owns tags. Branches function as historical/preparation markers rather than as authoritative release pointers.

### Hand-bumped versions on main (untagged)

The release marker is a plain commit titled `chore(plugin): bump 0.1.4 -> 0.1.5` (or the local equivalent). No automation; no pre-commit hook to derive the bump. Version drift across multiple manifest surfaces is hand-aligned via separate "align cursor plugin version to match claude plugin" commits when contributors notice. CHANGELOG may have versioned headings without git anchors. Constrains downstream pinning — there is no `git checkout vX.Y.Z` available — and creates an apparent version that disagrees with the latest tagged release.

### Single lifetime tag with drift

A single annotated tag (`v1.0.0`) exists on `main` but `main` continues to advance past it. Per-plugin `plugin.json` versions advance (e.g., `1.0.1`, `1.1.0`) without follow-up tags. Without a tag-pinning install path (`@v1.0.0` semantics), the tag is effectively a snapshot artifact rather than a channel. CHANGELOG.md and README also drift from live state. Operationally appropriate when no automation forces tag-version correspondence — but a clear anti-pattern: users pinning the only tag get stale plugins indefinitely.

### Mixed annotated and lightweight tags

Some tags are annotated (carry tagger info, message), others are lightweight (direct commit refs). Surfaces in GitHub API responses with different object types. Inconsistency suggests releases were cut by different mechanisms over time — `git tag -a` for some, web-UI lightweight for others. Appropriate as long as consumers don't filter on tag type.

### Plugin-name-prefixed tag format

In multi-plugin repos, tags use `{plugin-name}--v{version}` to disambiguate per-plugin lifecycles. Single-plugin repos use plain `vX.Y.Z`. Constrains the parent repo's tag namespace. Across the corpus, this format is largely unobserved — when multiple plugins share a marketplace, tags (when present) are flat repo-wide semver — every plugin shares the same tag identity, or each plugin has independent untagged versions in its `plugin.json`.

### Dual tag namespaces on a single trunk

Two distinct tag prefixes coexist on `main` — one for an underlying binary (`v*`) and one for the plugin (`plugin-v*`). Each tag prefix triggers its own release workflow. Lets the binary iterate rapidly without forcing plugin bumps and vice versa.

### Untagged sync-only

Zero tags ever; the entire release surface is the sync-PR merge stream. Appropriate for read-only mirrors of an upstream pipeline. Constrains: no pin handle other than commit SHA. Every commit may be `chore: sync <plugin-list>` produced by an upstream pipeline outside the marketplace repo — versions bump in the upstream plugin repos, and the aggregator imports the bumped artifacts via batched commits. The aggregator has no independent release identity — its own "version" is just the commit SHA of the latest sync.

### No tags at all

Repo has zero tags. "Release" means whatever `main` currently holds. No history of release points; rolling back to a prior version requires checking out a specific commit. The plugin's `version` field is frozen at an initial value (typically `0.1.0`) across many commits. Conventional commit subjects substitute for a changelog. Periodic `bump-versions-*` branches in commit history may suggest manual batch bumps. Often paired with no CI and no validation — a low-ceremony, low-investment plugin. Compounds the channel-from-HEAD problem: there is no way to recover any prior release state. Appropriate while pre-1.0 and exploring the design space, but offers no rollback or reproducibility for downstream consumers.

### Skill-driven release

A project-local skill (e.g., `/dev:release` under `.claude/skills/dev-release/`) bumps versions in known manifest files, generates a `CHANGELOG.md` entry from conventional-commit-prefixed log output (`feat:`, `fix:`, `refactor:`), creates an annotated tag, runs `gh release create`, and runs `npm publish` for multi-channel plugins. Appropriate when the author wants release automation but lives entirely in-editor; constrains: the skill must be kept in sync with all version-bearing files, and any file not in its bump set silently drifts (most commonly the marketplace entry's duplicated version field).

## Plugin-component registration

How `plugin.json` declares (or omits) the plugin's components — skills, commands, agents, hooks, MCP servers, monitors, output styles — explicit declaration versus directory-convention discovery.

### Default convention discovery

`plugin.json` carries identity/metadata only (`name`, `version`, `description`, `author`, `repository`, `license`, `keywords`, `homepage`, optionally `userConfig`). Components are resolved by Claude Code from conventional directory names (`commands/`, `agents/`, `skills/<name>/SKILL.md`, `hooks/hooks.json`, `monitors/monitors.json`, `bin/`, `.mcp.json`, `.lsp.json` at repo root, `output-styles/`, `channels/`). Adding or removing a component requires no manifest edit; the directory structure IS the registration. Lowest-overhead path; aligns with the official plugin reference; communicates "follow conventions" to readers and keeps the manifest stable across component additions. The dominant choice across most samples. Inline component definitions in `plugin.json` (e.g., `skills: [{name, description, ...}]`) were valid in older Claude Code schemas but break newer versions — projects that started with inline definitions had to migrate to default discovery (CHANGELOG explicitly: "skills/agents in plugin.json used inline objects incompatible with Claude Code v2.1.92 schema; removed inline; auto-discovery now"). Past tightening of Claude Code's plugin validator has caused authors to remove previously-declared "invalid auto-discovery fields" — the validator now penalizes redundant declaration of auto-discoverable components, making discovery the safer default. Constrains naming and placement to whatever the harness expects but eliminates a class of "registered but missing" drift. Fails when the plugin must satisfy a runtime that requires explicit paths (Codex, Cursor) — those runtimes need a sibling `plugin.json` with explicit `skills` and `agents` keys. When a single source tree publishes to multiple ecosystems, the Claude `plugin.json` may use default discovery while sibling `.codex-plugin/plugin.json` and `.cursor-plugin/plugin.json` set explicit paths — the same content is expressed two ways in parallel manifests, not as an either/or choice.

### Explicit per-component path arrays

Every component declared by path: `"skills": ["./skills/audio-hooks/"]` or `["./skills/"]`, `"agents": ["./agents/foo.md", ...]`, `"hooks": "./.claude-plugin/hooks.json"`, `"mcpServers": ["./.mcp.json"]`. Higher manifest cost but every component location is grep-able from one file, and the plugin can reference targets outside the default directories. Used when component count is large (one sample lists 80+ agent paths) and the manifest is treated as the authoritative inventory — mismatches between the array and filesystem (e.g. one extra unreferenced agent file) become discoverable drift signals. The trailing-slash directory glob form recurses to find every `<name>/SKILL.md`. The explicit list creates ambiguity about whether it is authoritative or additive — orphan files in `commands/` may or may not be exposed depending on host behavior.

### Explicit path string for one component

`plugin.json` declares one component's path explicitly (e.g. `"skills": "./skills/"`) even when the path matches default discovery. Redundant but valid. Often appears alongside the default-discovery pattern when only one component needs a non-default location and the author opts to be explicit about all of them.

### Asymmetric registration: file paths for agents, directory for skills/commands

`agents` is an enumerated list of `./agents/<name>.md` paths (per-file); `skills` and `commands` use directory references like `["./skills/"]`. The asymmetry tracks an observed validator restriction (`agents: Invalid input` when a directory is passed) that does not apply equally to skills and commands. Appropriate when validator behavior is asymmetric; produces verbose `agents` blocks that grow with the agent count.

### Mixed (paths + auto-discovery)

Some components declared by path, others left to convention. E.g., skills listed by path but agents discovered from `agents/` directory; or `hooks: "./hooks.json"` external file plus `lspServers: { … }` inline plus skills via convention. Often arises when the plugin gradually adopted explicit declarations only for components that didn't fit conventions, or when the author wants large/frequently-edited config in dedicated files while inlining short structural blocks. Constrains readers to look in multiple places to enumerate what the plugin registers.

### Directory-pointer mixed with file-pointer

`plugin.json` mixes directory pointers (`"skills": "./skills/"`) with file pointers (`"mcpServers": "./mcp/mcp.json"`) and explicit arrays (`"agents": [".../foo.md", …]`) in the same manifest, often with the mixture varying plugin-to-plugin within one marketplace. Appropriate when some component locations are conventional and others are non-default. Constrains: inconsistency within a marketplace makes it harder for tooling to predict where to look.

### Inline `mcpServers` definition in `plugin.json`

`plugin.json` carries an `mcpServers` object directly: `{ "<server>": { "command": "npx", "args": [...] } }` or similar, OR a string-URL form pointing at an `.mcpb` bundle hosted externally. The object form is conventional; the string-URL form is docs-silent and may be a loader-specific extension that triggers a remote fetch. No separate `.mcp.json`. Claude Code launches the server with the inline command. Env block typically threads `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` so the server resolves its own runtime location. Used when the plugin's only component is an MCP server (no skills, no commands) — keeps the whole plugin definition in one file. Constrains MCP server config to flow through the plugin manifest; a sibling `.mcp.json` is unused. Pitfall: env-thread paths assume the dependency-install side-channel has populated `${CLAUDE_PLUGIN_DATA}/node_modules` before MCP server startup, with no startup gate. When both inline and external `.mcp.json` forms exist, they are two sources of truth with no automation reconciling them.

### Inline manifest with high-fan-out hooks

`plugin.json` inlines `mcpServers` and `hooks` (10+ event types, 17+ total registrations all matchering `*`). Skills and agents discovered by path convention. Appropriate when the plugin wants centralized declarative control. Constrains tool-call latency — every tool invocation spawns multiple hook processes.

### `.mcp.json` sibling file

`.mcp.json` lives alongside `plugin.json` carrying the MCP server configuration separately. Suits plugins where MCP setup is the bulk of the plugin's surface and benefits from being its own file. Loaded by the install flow without an explicit `plugin.json` reference — well-known filename at well-known path.

### Hooks at well-known path without `plugin.json` reference

`hooks/hooks.json` sits at a known path and is loaded by the install flow without an explicit `plugin.json` reference. Path is fixed, not configurable.

### Empty hooks scaffolding

`hooks/hooks.json` exists but contains `{}` or `[]` — no hooks registered. Shows up uniformly across plugins from one marketplace, suggesting template residue or forward-compat scaffolding rather than active hooks. Either an anti-pattern (dead files) or a deliberate "extension point" convention; the corpus shows no documentation explaining the choice. Variant: the `hooks/` directory contains files in a non-Claude-Code hook format (e.g., `hookify.*.local.md` with frontmatter `event:` / `conditions:` / `pattern:` for a separate tool). Files look authoritative — right directory, right plugin layout — but Claude Code will not execute them. Distinct mode from "empty file" — non-empty but inert under Claude Code; usually appears in plugins that span multiple agentic tools and reuse the `hooks/` convention loosely.

### Hooks-json with broad event coverage

A standalone `hooks/hooks.json` registering many event types (15+ including `Notification`, `StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`) each with empty-string matchers (fire on everything). Two distinguishable subcases: (a) **forward-compat anticipation** — the plugin anticipates emerging events and ships handlers older Claude Code silently ignores; constrains the plugin to versions of Claude Code that emit those events without a declared version floor. (b) **Undocumented event name as silent dead code** — a single hook declares an event name not in Claude Code's documented event list (e.g., `SubagentStart` when only `SubagentStop` is documented). The hook ships valid JSON but the runtime never emits the event, so the hook is silent dead code regardless of host version. Distinct from forward-compat in that no future host will emit the event — the name is wrong, not aspirational.

### Slash-command surface via skill frontmatter

Slash commands are exposed through `skills/<name>/SKILL.md` files with frontmatter `name: <plugin>:<verb>`, while `commands/` holds only diagnostic stubs (`doctor.md`, `hello.md`). The skill-namespacing prefix in frontmatter is doing the work a `commands/` directory usually would. A reader expecting "commands go in `commands/`" misses most of the surface. Appropriate when the project uses skills as the primary user-facing verb but pays a discoverability cost.

### Out-of-band hook registration

Hooks live in the repo as scripts (`hooks/*.sh`) but `plugin.json` has no `hooks` field. Registration happens via a side script (`scripts/sync-to-active.sh`) that patches the user's `~/.claude/settings.json`, or via a skill (`/adopt`) that writes a project `.claude/settings.json` from a template. The plugin's hook layer is not part of `/plugin install`'s reach. Constrains the user to a manual post-install step to get full hook coverage; the README has to document the gap. Appropriate when hooks are intended for opt-in adoption rather than passive activation, but needs a drift-guard since the hook inventory and the registration list can disagree.

### Marketplace-entry-only definition (no `plugin.json`)

Plugin directory has no `.claude-plugin/plugin.json`; the marketplace entry's own fields (`skills`, `lspServers`, `version`, etc.) are the entire definition. Requires `strict: false` on the entry. Two shapes: skill-carving (entry's `skills: ["./<dir>"]` is the only registration) and hollow umbrella (entry's `lspServers: {...}` is the entire plugin). Trade-off: centralizes definition in the manifest at the cost of independent plugin-level versioning.

### Mixed convention per runtime (per-runtime manifests)

Repo hosts multiple `*-plugin/` directories (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`) — each with its own `plugin.json`. Claude relies on directory convention; Codex and Cursor's manifests explicitly set `"skills": "./skills/"` (and Cursor adds `"agents": "./agents/"`) because those runtimes require explicit paths. Cursor's runtime apparently doesn't inherit the Claude default-discovery behavior, so its manifest is more verbose. Same `skills/` tree on disk, multiple manifest views over it. The single source of truth (universal YAML) compiles to all three.

### Marketplace-root shared bin via per-plugin symlink

`bin/<wrapper>` at the marketplace root (not under any individual plugin), with each consuming plugin shipping a symlink at `plugins/<name>/hooks/<wrapper>` pointing at the shared file. Author's documented intent is DRY at the marketplace level — one wrapper, many plugin consumers. See *Bin entry mechanism* for the constraint this creates around symlink target form (relative survives the install copy; absolute breaks on any non-author machine).

### Custom sidecar manifest

Each plugin ships a non-standard `.claude-plugin/capabilities.json` alongside `plugin.json` carrying `{plugin, version, schema_version, capabilities[]}` with per-capability `id, name, type, applicable_phases, guidance, anti_patterns, priority`. Not in the official spec; consumed by the marketplace's own router/selector layer that picks which capability to invoke based on phase + priority. Capability versions drift independently from `plugin.json.version`. Appropriate when a marketplace ships its own routing/selection mechanism; constrains: the sidecar is meaningless to vanilla Claude Code clients and must be parsed by a co-shipped consumer.

### Three-channel parallel registration

Components are registered three ways in the same repo: (a) marketplace.json plugin entries for the slash-command flow (relies on directory conventions), (b) `config.json` modules for the npx flow (enumerates per-module operations explicitly: `copy_file`, `copy_dir`, `merge_dir`, `run_command`), (c) legacy Makefile targets like `deploy-bmad`. Each channel registers components differently; the npx path also merges per-module agent presets into `~/.codeagent/models.json` and tags every merged hook entry with `__module__: <name>` for surgical unmerge on uninstall.

### Skill `triggers` array with fuzzy matching

Skills declare `triggers: [phrase1, phrase2, ...]` (a custom array of 3-10 short phrases per skill) in addition to or in place of `description`. A `UserPromptSubmit` hook fuzzy-matches the prompt against triggers (typo-tolerant) and injects up to 3 matching skills' content via `additionalContext`. Distinct from Claude Code's built-in `description`-based activation; layers on top rather than replacing. Appropriate when activation precision matters and the plugin is willing to ship its own matcher. Constrains skill authors to maintain trigger arrays in addition to descriptions.

### Authored agents not registered as plugin agents

A directory like `src/agents/*.md` contains files with Claude-Code-style agent frontmatter (`name`, `description`, `defaultModel`, `readOnly`, `tools` array). They are not wired via `.claude-plugin/agents/` and there's no `agents` field in `plugin.json` — they're consumed by an internal swarm/orchestration skill rather than registered as Claude Code sub-agents. Constrains discoverability: a reader scanning by directory convention may misidentify them as plugin-registered agents.

### Non-standard component directories

In addition to standard `commands/`, `skills/`, `agents/`, `hooks/`, the plugin includes directories that don't correspond to any documented component type — e.g., `teams/` (orchestration definitions), `setup/templates/` (config scaffolding), `output-styles/<name>.md` (response-formatting markdown, terse vs reviewer modes), `channels/<name>/` (in-plugin MCP "channel" research-preview component). Some are consumed only by the plugin's own commands; others may be experimental forward-looking surfaces. No structural validation — users learn the convention from the plugin's own code.

### Component types absent across the corpus

Several component types declared by Claude Code's plugin schema rarely or never appear in observed samples: `monitors.json` is largely absent (notifications flow through hooks); `.lsp.json` appears occasionally inline; `output-styles/` appears rarely. Their absence across the bin is itself a signal — the observed plugins solve their problems through hooks and skills instead.

## Component composition

Which kinds of components the plugin ships and how the mix shapes the plugin's product surface.

### Skills (universal)

Universal across most observed plugins. Every plugin tends to ship at least one `skills/<name>/SKILL.md`. The dominant component type. Some samples place loose `skills/<name>.md` files at the skills/ root with command-style frontmatter, which is non-canonical and appears to be a misunderstanding of skills-vs-commands or leftover scaffolding.

### Commands

Present in some plugins as a legacy form. Per documentation in mid-migration repos, "the legacy `commands/` format still works but new plugins should use `skills/*/SKILL.md`." Frontmatter `name`, `description`, `argument-hint`. Body instructs Claude on what to do (e.g., call a specific MCP tool with the argument). Appropriate when one user-invoked entry point is the primary affordance.

### Agents

Variable adoption — common in workflow-heavy plugins, rare in content-driven ones. Ship as `agents/<name>.md` files with frontmatter declaring identity, model, and tool permissions. See *Agent declaration conventions* for frontmatter detail.

### Hooks

Often absent entirely. A marketplace can ship dozens of plugins and zero `hooks.json` files. Aligned with a "no infrastructure" design posture; absence of hooks correlates with absence of session-start install, tool-use enforcement, monitors, and session-context-loading mechanisms. When present, see *Tool-use enforcement* and *Session context loading* for the actual mechanisms.

### MCP servers

Common — declared either via inline `mcpServers` in `plugin.json` or via a sibling `.mcp.json`. Plugin's value is bridging an external service to MCP. See *Server runtime (MCP)* for execution-path detail.

### bin

Variable adoption. Used when the plugin distributes a binary CLI through shim wrappers. Absent when the plugin is "just markdown and JSON." See *Bin entry mechanism* for shapes.

### LSP config

`.lsp.json` — minimal-viable plugin can ship only `.claude-plugin/plugin.json` + `.lsp.json` + README, with no skills/commands/hooks/agents at all. Demonstrates the floor of plugin footprint.

### output-styles, monitors

Not observed in any sample. Equivalent functionality (notification, monitoring) is delivered via Stop and PostToolUse hooks where present. See *Live monitoring*.

### Composition shapes

Plugins cluster into common composition shapes:

- **Skill-only payload** — only `skills/<name>/SKILL.md` plus optional `references/`, `assets/`, `scripts/`. Appropriate for content-driven domain knowledge.
- **MCP-only payload** — only `.mcp.json` or inline `mcpServers` plus identity metadata. Appropriate when the plugin's value is access to a hosted backend.
- **Skills + hooks + bin** — multiple skills (each as `skills/<name>/SKILL.md`) plus a SessionStart hook plus a single bin entry point that the skills invoke via `Bash(<binname> *)` permission rules. The bin is the orchestrator; skills are user-invocable; the hook handles environment setup. Appropriate when the workflow is dominated by command-line tooling.
- **Mixed skills + commands + agents + hooks + MCP** — default-discovery `plugin.json` is the wiring; conventions handle the rest. Appropriate for plugins that wrap a workflow rather than expose a single resource.
- **Hooks + MCP server (no skills/commands/agents/bin)** — entire product surface is one MCP server with several tools plus two or three hook scripts. Appropriate when the plugin is purely a context-provider (memory, retrieval, indexing) — Claude reaches its tools via MCP, not via slash commands or skill invocations, and hooks handle background ingestion and per-prompt context injection.
- **Skills + commands + agents + hooks + bin** — multi-component plugin with skills (single-file `SKILL.md`), commands (markdown files for slash invocation), agents (sub-agent definitions with their own model/isolation/color), hooks (pre/post tool use plus session-start/pre-compact), and a thin bin wrapper. Appropriate for spec-driven-development style workflows where each phase has its own command surface, agents handle execution in worktrees, and the bin is a shared utility.
- **Skills + hooks + channel** — skills, hooks, AND an in-plugin MCP "channel" (research-preview feature) under `channels/<name>/` with its own server source and dep manifest — a fourth component class beyond the conventional set.
- **LSP-server-only "hollow" plugin** — plugin directory holds only `README.md` + `LICENSE`; the marketplace entry's `lspServers` block is the entire plugin definition. One plugin per language server.
- **Broadest palette** — skills, commands, agents, hooks/hooks.json, `.mcp.json` at plugin level, `monitors.json`, and `bin/`. Cross-section surface area for a single plugin reaching the full Claude Code component matrix.

## Plugin-component placement

Where component directories physically live relative to plugin boundaries.

### Inside plugin directory

`plugins/<name>/skills/`, `plugins/<name>/hooks/`, `plugins/<name>/bin/` — components live under the plugin they belong to. Standard model; auto-discovery and `${CLAUDE_PLUGIN_ROOT}` interpolation work as designed.

### Outside plugin directory at repo root

`bin/`, `hooks/`, or other component-shaped directories live at repo root with no owning plugin. Auto-PATH registration (which depends on `bin/` inside a plugin per the plugin model) does not happen. Appropriate when the artifact serves the marketplace as a whole (a manual installer CLI, a project-setup nudge) rather than any specific plugin. Constrains: only reachable for local-clone users who add the directory to PATH themselves; plugin-installed users must fall back to absolute paths via `${CLAUDE_PLUGIN_ROOT}/scripts/...` in skill steps. The `bin/` entry at repo root is effectively dead in the plugin-install pathway.

## Skill authoring conventions

Frontmatter fields, tool-permission syntax, and dispatch mechanisms used inside `SKILL.md` files.

### Standard frontmatter

`name`, `description`, `argument-hint`, `allowed-tools`, `license`, plus `metadata.{author, version, category, tags}`. Per-skill versioning (where present) means SKILL.md frontmatter is yet another version-sync site. The description field has a hard 1024-char limit (300-500-char target) and is read by many agent hosts simultaneously when the skill is multi-host.

### Multi-host description tuning

`SKILL.md` description is authored to match trigger verbs/nouns users actually say, with a hard 1024-char limit and a 300-500-char target. Explicitly written to work simultaneously for Claude Code, Cursor, GitHub Copilot, Windsurf, Gemini CLI, Codex, Goose, Amp, Roo Code, OpenCode, OpenClaw — each with its own project-scope and user-scope skills directory conventions. Description-writing rules codified in `CLAUDE.md` ("don't bake in anti-patterns against failure modes of one session — read by many agents in many contexts"). Pattern requires the maintainer to keep the description host-neutral.

### `disable-model-invocation: true` for high-blast-radius skills

A frontmatter flag that prevents auto-routing — the skill won't be auto-invoked via fuzzy embedding match. Users must call by name; routers must explicitly delegate. Applied to `/deploy`, `/migrate`, `/migrate-prod`, `/autopilot` and similar destructive operations. Constrains how the host model surfaces the skill in completion-style invocation. Appropriate for destructive operations where false-positive auto-routing has real cost.

### `context: fork` invocation hint

A frontmatter field on a router-style skill (`/autopilot`) suggesting subagent-like forked-context invocation. Documentation status unclear — possibly an undocumented Claude Code feature or a methodology-specific extension. Constrains the skill to a mode where it spins up a fresh agent context rather than continuing in the caller's. May coexist with `agent: <name>` to drop into an isolated sub-agent context — the named agent file lives alongside `skills/` in `agents/<name>.md`. Appropriate when the skill's work warrants a clean context with restricted tools.

### `user-invocable: false`

Marks a skill as composition-only — used by other skills, not exposed as a slash command. Not in the core plugin-reference frontmatter docs; appears to be a host-environment-specific extension.

### Non-standard `user-invocable: true`

Every `SKILL.md` declares `user-invocable: true`. The Claude Code plugins reference does not document this field — either author-invented (and ignored at runtime) or an undocumented behavior. If ignored, it is dead metadata; if respected, it is an undocumented dependency.

### `compatibility:` prose

Free-form prose declaring platform prerequisites (e.g., "Requires Cowork desktop app environment"). Not in the canonical schema; another host-environment extension.

### `allowed-tools` with permission-rule syntax

Skill frontmatter carries `allowed-tools` using Claude Code's permission-rule syntax (`Bash(<cmd> <args> *)` form), explicitly enumerating safe read-only invocations and deliberately omitting write-side commands so they trigger permission prompts. Frontmatter also carries `name`, `description`, `user-invocable`, `argument-hint`. Appropriate when the plugin wants tool-level allowlisting without per-tool hooks.

### `allowed-tools` with plain tool names

Skill frontmatter carries `allowed-tools: Bash` (no permission-rule brackets) or as a single-string scalar. Looser than the permission-rule form; relies on user-level permission gates rather than skill-declared per-command allowlists. Appropriate when the skill intends to be broadly capable and tool gating is owned elsewhere.

### `allowed-tools` as YAML array

Skills declare `allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Agent, AskUserQuestion]` as a YAML array (vs. comma-separated scalar). The token `Agent` is the legacy name for the Task tool used to launch sub-agents. Constrains nothing — purely stylistic — but observed consistently across one plugin's skills, suggesting authoring convention.

### Mixed `allowed-tools` syntax

Same frontmatter line carrying plain tool names (`Read Write Edit`) and permission-rule syntax (`Bash(git:*)`, `Bash(pytest:*)`). The two forms coexist within one declaration. Constrains the parser; an author has to know which form Claude Code accepts in which slot. Appropriate when the skill needs both broad tool access and narrow command-pattern carve-outs.

## Agent declaration conventions

Frontmatter fields used in `agents/*.md` to declare model, tools, capabilities, and orchestration knobs.

### Minimal frontmatter (name, description)

Agents declare `name` and `description` only. No `model`, `tools`, `allowed-tools`, `disallowedTools`, `memory`, `maxTurns`, `color`, `effort`, `background`, or `isolation`. Relies on Claude Code defaults for everything else.

### Minimal `name`, `description`, `tools`

Bare-minimum agent declaration. `tools:` is a YAML list of plain tool names (`[Bash, Read, Write, Edit, Glob, Grep]`) or a comma-separated string — both forms accepted. No model selection, no turn budget, no permission-rule syntax (`Bash(uv run *)`).

### Minimal frontmatter, parent-session permissions

Agents declare only `name`, `description`, `model: inherit`, and (optionally) `memory: user`. `model: inherit` defers to whatever model the parent session uses. No `tools` allow-list — the agent inherits the parent session's permissions. `color` (e.g. `violet`, `green`) may appear as a UI cue. Native-language descriptions (Chinese in observed cases) flow through `description` directly without an i18n layer, so the template picker shows the source language to all users. Appropriate for thin agents that exist only to be entered into a routing decision.

### Plain tool-name list

`tools:` field as a YAML list, comma-separated string, or space-separated list of bare tool names (`Read, Write, Glob, Grep, Edit, Bash, Agent`). No permission-rule syntax (`Bash(uv run *)` etc.) — Bash scoping, when needed, is enforced elsewhere (PreToolUse hook). Three syntactic variants (comma-delimited, bare list, YAML array) sometimes observed across one repo — inconsistency within sibling agents indicates no enforced schema. Field-name regressions are common (CHANGELOG: `tools:` → `allowedTools:` correction across multiple agent files in a single patch). Appropriate when the agent has a clearly-scoped role.

### Standard fields plus model / color

`name`, `description`, `model` (selecting between `sonnet`/`opus` per agent role), `color`. The `description` field embeds XML-ish `<example>` blocks inline in YAML strings — readable but assumes the platform doesn't strip or parse them. Agents inherit default tool access; no `tools` field. Appropriate when different agents have different cost/capability budgets.

### `model` + `effort` + `maxTurns` for cost control

Frontmatter declares `model` (e.g. `claude-sonnet-4-6`, `haiku`, `opus`, `sonnet`), `effort` (`high`, `medium`, `low`, `max`), and `maxTurns` (integer cap on agent turns) for explicit cost-and-budget control per agent. Cheaper-model selection (`haiku` for exploration agents) is an explicit token-cost optimization — offload iterative searches to a cheaper model so the caller's expensive-model conversation stays short. Pattern surfaces in pipeline-style plugins where different waves of agents have different cost profiles.

### Tool-restricted with orchestration knobs

Frontmatter includes `tools` (allowed) and optionally `disallowedTools` listing tool names. The denylist appears in two distinct shapes:

- **Subtractive** — agent omits `tools:` (inheriting harness defaults) and uses `disallowedTools:` to subtract a few specific tools. Compact when the agent should mostly behave like a default agent minus a few capabilities.
- **Belt-and-suspenders** — agent declares both an explicit `tools:` allowlist AND a `disallowedTools:` block, redundantly naming forbidden tools. Suggests authors do not uniformly trust `tools:` as a hard allowlist, or are defensively coding against ecosystem-wide enforcement-semantics ambiguity.

Plus orchestration knobs: `memory: project|user`, `model: inherit`, `maxTurns: <int>`, `effort`. The plain MCP tool id form (`mcp__<server>__<tool>`) appears alongside core tool names in both `tools:` and `disallowedTools:`.

### Rich behavior fields (background, isolation, memory)

In addition to documented fields, agents declare `background: true` (run in background), `isolation: worktree` (per-role git-worktree isolation, presumes the invoking session's project is a git repo), `memory: project|user`, and `effort` as a host-specific scheduling hint. Hard turn cap may pair with worktree isolation (`maxTurns: <N>`) — long-running research can truncate mid-flow with no documented recovery. These fields are not in the public Claude Code plugin reference; whether the harness honors them or silently drops them is unverified. If a client doesn't support worktree isolation, parallel execution silently becomes serial. Appropriate when parallel execution of multiple instances of the same agent is fundamental to the workflow (e.g., spec-driven dev with parallel task execution).

### `permissionMode: acceptEdits` + worktree isolation

Agent runs with pre-granted edit authority (`permissionMode: acceptEdits`) inside a git worktree the orchestrating skill creates. Safety comes from worktree boundary + post-hoc human review at a `/deploy` skill, not from tool-use hooks or in-flight permission gates. Constrains: the orchestrating skill MUST set up the worktree first, otherwise the agent operates on the live tree with full edit authority.

### MCP-server allowlist binding

Agents declare `mcpServers: [<server-name>]` to bind to a specific MCP server's tools, alternative to listing tools individually. Appropriate when the agent's purpose is one MCP-driven workflow.

### Fully-qualified MCP tool names

Each MCP tool listed by full name (`mcp__academic-search__search_papers`) rather than wildcard. Tighter scoping than `mcp__academic-search__*` but high maintenance — adding a tool to the server requires updating each agent's allow-list. Compare with `allowed-tools` on commands, which often use the wildcard form even when the agent in the same plugin uses fully-qualified names — two conventions for the same kind of access scoping.

### `skills:` array delegating to skill packages

Agent frontmatter lists `skills: [<plugin>:<skill-name>, ...]` to grant the subagent access to specific skills the parent has loaded. Bare-name in-plugin skill references (`skills: rn-testing, rn-best-practices`) are correct for skills in the same plugin; future cross-plugin reuse would need qualification. Composes subagent + skill into a token-cost-aware unit (cheap-model agent invokes the skill's full context). Pattern requires the named skill to exist in the agent's discovery scope.

### Read-only agents

All agents in the population declare only read tools (`Read Grep Glob`) — no `Write`/`Edit`. Agents return structured markdown that the caller skill writes. Constrains the caller-callee contract: agents are advisors, the calling skill is the only writer. Appropriate when the author wants a clean read/write split between layers.

### Defensive prompt directives in agent body

Agent body carries the prompt — sometimes including defensive directives like "USE THE TOOL-CALLING INTERFACE … NEVER simulate, write out, or fake function calls" guarding against model hallucination of tool calls. Caller-supplied parameters can be encoded in prose (e.g., the agent body declares quick/medium/very-thorough modes the caller names at invoke time).

### Custom agent frontmatter extensions

Standard fields (`name`, `description`, `model`, `tools`) coexist with non-standard ones — `stakes` (low/medium/high, borrowed from the 12-Factor-Agents discipline), `subagent_type` namespaced as `<plugin>:<name>`, plus `effort`, `maxTurns`, `disallowedTools`, `color`, `memory`, `allowed-prompts` with nested `{tool, prompt}` pair lists. The plugin's internal readers consume these; the harness ignores them. Appropriate when the plugin has internal agent-orchestration logic that needs richer per-agent classification than the harness provides. Constrains portability: validators that enforce only the canonical schema reject these, so the plugin maintains its own validators.

### Experimental orchestration tool names

Agent `allowedTools` arrays include tool names not documented in the plugin reference (e.g., `TeamCreate`, `TaskCreate`, `TaskList`, `TaskUpdate`, `SendMessage`) for agents that orchestrate sub-agents or manage shared state. Implies bespoke runtime support inside the plugin rather than the standard tool set. No validator checks tool-name validity — typos or reference-mismatches surface only at runtime.

### Native-language-first templates

All agent templates written in the project's primary spoken language (Chinese observed); descriptions and full template body are not translated from English. English-only Claude Code users see the agent `description` in the source language in the template picker. Genuinely native-first design rather than translated; no i18n layer.

## Cross-platform skill publishing

How skills are exposed to non-Claude agent runtimes alongside the Claude-native form.

### Per-skill Codex sibling marker

Every `skills/<name>/` directory contains a sibling `agents/openai.yaml` file declaring Codex-platform interface metadata (`interface: {display_name, short_description}`, `policy: {allow_implicit_invocation}`). Lives alongside the Claude-native `SKILL.md` so the same skill folder publishes to both platforms. Appropriate when the author wants one skill source-of-truth feeding multiple agent ecosystems; constrains: skill folder layout becomes platform-fan-out — adding a new target runtime means another sibling file in every skill dir.

### Multi-runtime install via npm bootstrap

A Node CLI (`bin/install.js`, invoked via `npx <plugin>@latest`) copies skills/agents/tools into runtime-specific directories (`~/.claude`, `~/.cursor`, `~/.codex`, `~/.windsurf`) with an interactive prompt selecting subset. Same source ships as a Claude Code marketplace plugin AND as a multi-runtime skill bundle through npm. Appropriate when the plugin's value proposition is portable beyond Claude Code; constrains skills to cope with two filesystem layouts at runtime — plugin mode under `${CLAUDE_PLUGIN_DATA}`, npm mode under `~/.<runtime>/` — typically via env-var fallback chains in skill steps.

### Codex CLI co-distribution

Sibling directory in the same repo carries Codex-only artifacts (SKILL.md + `agents/openai.yaml`) installed via `cp -R ~/<repo>/<dir> ~/.codex/skills/` rather than `/plugin install`. Same git repo doubles as a Claude Code marketplace and a Codex skills bundle. Per-platform install instructions live in the README.

### Multi-runtime skill mirrors

Skills authored once in `skills/`, then mirrored to sibling directories for other runtimes (`skills-codex/`, `codex/.codex/skills/`, `opencode/skills/`) by build scripts (`scripts/build-opencode.js`, `scripts/sync-skill-mirrors.sh`). A dedicated CI workflow (`opencode-compat.yml`) fails if mirrors drift. Differs from per-skill sibling markers by mirroring derivative copies rather than running the same files through divergent registration manifests.

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

## Bin entry mechanism

Whether the plugin ships executable wrappers under `bin/`, what those wrappers do, how they resolve the plugin root, and how they relate to the binaries that actually run.

### No bin entry / direct invocation

The plugin's executable surface is hook scripts under `scripts/` invoked by hook events, plus markdown command files. Nothing is surfaced as a user-PATH binary. All invocation flows through skills, hooks, or MCP. Internal entry points are invoked by full path (e.g. `node ${CLAUDE_PLUGIN_ROOT}/src/parsers/pdf-parser.js`) from commands or hooks rather than via a `bin/` wrapper. MCP servers resolve via `.mcp.json`'s explicit `command:` path. The MCP server, when present, is registered through `.mcp.json` rather than as a bin entry. Lowest portability burden, no shell-discoverable entry points; aligned with the "no code" posture. Suits plugins where everything goes through Claude Code's hook/command dispatch, or where the plugin's value is methodology / contextual injection rather than user-facing tools. Reduces the discoverability surface compared to bin-wrapped CLIs but eliminates the version-of-record question for a wrapper script.

### POSIX shell wrapper with `${CLAUDE_PLUGIN_ROOT}` fallback

A short `bin/<plugin>` script resolves the plugin root via `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}` (or `sh`-portable equivalent using `dirname "$0"`), then `exec`s the underlying interpreter on a script inside the plugin. The fallback makes the same script work under Claude Code (env var set) and from a bare clone (env var unset). Canonical pattern, observed verbatim across multiple samples. Shebang varies: `#!/usr/bin/env bash` is typical; `#!/usr/bin/env sh` appears when the wrapper is intentionally bashism-free. Cross-platform via shebang on POSIX; on Windows requires either `node bin/<verb>.js` or a sibling `.cmd` launcher. POSIX-only — Windows requires a separate `.cmd` or `.ps1` pair. `CDPATH= cd --` guards against hostile `CDPATH` and dash-prefixed paths in the fallback branch. CI may not enforce executability on `bin/*` (the validator's allowlist commonly covers `hooks/*.sh` but not `bin/*`), so the +x bit must be set deliberately.

### Bash thin exec-delegate wrapper

`bin/<plugin>-<verb>` shell scripts that `exec bash "$(cd "$(dirname "$0")/.." && pwd)/<internal>.sh" "$@"` — resolving the plugin root via `$(dirname "$0")` rather than `${CLAUDE_PLUGIN_ROOT}`, so the script works whether invoked directly from a terminal or from a Claude Code Bash-tool context where `CLAUDE_PLUGIN_ROOT` may be absent. Lets one implementation serve both the hook-event invocation and a CLI invocation.

### Bash wrapper that synthesizes a hook input envelope

`bin/<plugin>-validate` reconstructs the PostToolUse JSON input envelope (`{tool_input: {file_path: $fp}}`) via `jq -n` and pipes it into the hook script — letting a user run the same hook validator from a terminal as Claude Code runs at PostToolUse. "One implementation, two surfaces." The reconstructed envelope is brittle against hook-input schema changes; if Claude Code adds required fields, the CLI surface silently breaks while the hook-event surface still works.

### Bash + `.cmd` pair for cross-platform

POSIX `.sh`/no-extension bash wrapper plus a Windows `.cmd` batch file with the same behavior — `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..` for runtime resolution, `%PYTHONPATH%`, `%*` argument passthrough. PowerShell `.ps1` is not used as a runtime shim — only as a one-shot installer when present. Probes for the right Python interpreter (`python3 → python → py`) with a smoke `python -c "import sys"` to defeat the Microsoft Store `python3.exe` stub on Windows. More defensive than relying on the Python shebang alone; addresses Git Bash on Windows specifically. Files often have non-exec permission (100644) on the assumption Claude Code's plugin cache adds `bin/` to `PATH` and shell resolution honors the shebang via `bash <path>`. Constrains feature parity because `.cmd` cannot replicate `set -euo pipefail` and error handling diverges.

### Cross-platform shim dispatching to pre-built binaries

`bin/<name>` POSIX shell wrapper resolves `uname -s`/`uname -m` and `exec`s the matching pre-built binary (`bin/<name>-darwin-arm64`, `bin/<name>-linux-amd64`). Platforms not built receive silent no-op (exit 0, stderr diagnostic). Zero-install at runtime; constrained by which architectures the author cross-compiles. Linux ARM64 and Windows often gaps; graceful degradation means users get no error, just no functionality.

### Python `bin/` script with uv injection

`bin/<name>.py` with `#!/usr/bin/env python3` shebang; the script body does `uv run --with <pkg>` internally to inject deps. Plugin-root resolution via `${CLAUDE_PLUGIN_ROOT}` env var with `Path(__file__).resolve().parent.parent` fallback. Cross-platform via `subprocess.run` (chosen over `os.execvp` because the latter raises on Windows). Constrains the bin to use `.py` extension (extensionless or `.sh` flagged by validators as platform-specific); on Windows, `.py` association must be set for PATH invocation. Permissions are 100755. Appropriate when the plugin wants both hook-fire and on-demand-CLI access modes against the same script body.

### Node CLI launcher with `env node` shebang

`bin/<verb>.js` opens with `#!/usr/bin/env node`, resolves a wrapper path script-relative (`path.resolve(__dirname, '..', 'scripts', '<wrapper>.mjs')`), and `spawn`s `process.execPath` with the wrapper as argv. Inherits stdio, propagates child exit code/signal. Declared as the `bin` entry in root `package.json`. Cross-platform via shebang on POSIX. Secondary env-var overrides (e.g. `<PLUGIN>_CLAUDE_CMD`, `<PLUGIN>_WRAP_SPAWN`) provide runtime escape hatches.

### Auto-generated Windows `.cmd` launchers with absolute paths

A SessionStart hook discovers `process.execPath` and the `claude` binary location, then writes `bin/*.cmd` Windows launchers with those absolute paths embedded, plus optional `set <ENV>=<path>` lines. Solves "node not on PATH" on Windows without requiring user editing. Files are committed with the author's machine's paths frozen — a reader inspecting the committed file sees one specific machine's layout. Header banners declare "auto-generated ... edits will be overwritten next session" so user customization is impossible. POSIX users rely on the `bin` field in `package.json` instead.

### Skill-invoked update poller

A single `bin/<plugin>-update-check` shell script, not registered in `plugin.json`'s component fields, invoked from a `## Preamble (run first)` block embedded in a SKILL.md. The agent reads the skill body, shells out per the prose instructions, parses output (`UPGRADE_AVAILABLE <old> <new>` / `JUST_UPGRADED <old> <new>` / nothing), and conditionally surfaces a notification. Polling cadence is gated by a cache file with a TTL. Novel because it embeds polling logic in documentation text the model must parse and act on, rather than in a structured hook contract. State coordination (read by skill, written by install hook) sits in shared sentinel files (`.version`, `just-upgraded-from`, `last-update-check`, `update-snoozed`). Variant: half-implemented snooze — the script reads a `$SNOOZE_FILE` carrying a 3-field record (`version level epoch`) and switches on level (24h / 48h / 7d) but no writer in the repo creates or updates the file. Read path exists; write path absent. Documents the design intent without runtime functionality.

### Pre-built binary download (lazy, per-hook)

Runtime is a Go (or similar compiled-language) binary downloaded from GitHub Releases on demand. Build-time deps live in `go.mod`; users never compile. The binary is materialized into `${CLAUDE_PLUGIN_ROOT}/bin/` (inside the plugin cache, not `${CLAUDE_PLUGIN_DATA}`) or `${CLAUDE_PLUGIN_DATA}/bin/` (with `$HOME/.<plugin>/bin` fallback) by an `install.sh` script invoked by a wrapper script on every hook fire — not gated behind SessionStart, so the first hook of a session effectively becomes the bootstrap moment. A version-cache file at `${XDG_CACHE_HOME}/<plugin>/verified-version` short-circuits the binary-launch cost on the happy path; cache miss falls back to executing `<binary> version` and comparing to `plugin.json.version`. Appropriate when the runtime is a compiled language whose CGO/static-link story sidesteps interpreter version drift; the cost is platform-asset matrix complexity (per-OS, per-arch artifacts plus signed/notarized macOS app bundle) and a wrapper that must self-heal across cross-platform git quirks. Pitfalls: existence-only change detection (`if [ -f "$BINARY_PATH" ]; then exit 0`) means once present, install never re-downloads — `/plugin update` doesn't pick up new binaries, requiring manual cache-purge by the user. Unauthenticated GitHub API calls (`/releases/latest`) hit the 60-req/hour-per-IP rate limit, surfacing as cryptic "Failed to find binary for ..." errors when the limit hits. Some installers compute version live by hitting `https://api.github.com/repos/<owner>/<repo>/releases` and filtering tag prefixes, so the plugin always installs the freshest upstream binary regardless of `plugin.json.version`. Hard fails are common on unsupported `uname -s`/`uname -m` combinations.

### Lazy-install bin shim with fallback chain

Small bash and Windows-batch shims (~600-800 bytes each) live in `bin/` and are auto-discovered by the loader (PATH integration by convention). Each shim checks for the real binary at `${CLAUDE_PLUGIN_DATA}/bin/<name>` (with `$HOME/.<plugin>/bin` fallback); if absent, runs an installer script (also in `scripts/` of the plugin) that downloads platform-appropriate binaries from the project's GitHub Releases, then re-execs. A separate "drop-in" shim layers fallback through co-located alternatives, then a system-installed binary, then the original tool — graceful degradation if anything breaks. Shebang `#!/usr/bin/env bash` with `set -euo pipefail`. Script-relative path resolution (`SCRIPT_DIR=...`) rather than `${CLAUDE_PLUGIN_ROOT}` reference. Self-recursion guarded by a marker string embedded in the shim that the installer greps for.

### Bash three-tier resolution shim

`bin/<name>` carrying `#!/usr/bin/env bash`, mode 100755, three resolution tiers: (1) PATH cleaned of `self_dir` then `command -v <name>` — exec user's install if found; (2) plugin-managed cache at `${CLAUDE_PLUGIN_DATA}/bin/<name>` with version-stamp match — exec if version aligns; (3) lazy download from GitHub release — curl + tar xzf + chmod +x + macOS quarantine strip + exec. Appropriate when the upstream binary is a distinct user-installable product. Constraint: PATH-cleaning is fixed-string match; trailing slash or case differences in PATH entries would not be stripped.

### Cargo/Homebrew user install with plugin-managed cache fallback

The plugin's bin shim tries the user's own install first (`cargo install <pkg> --locked` or `brew install <tap>/<pkg>`), then a plugin-managed binary at `${CLAUDE_PLUGIN_DATA}/bin/<name>`, then downloads from GitHub releases as a last resort. PATH-cleaning via `grep -vFx "$self_dir"` on PATH entries prevents the shim from finding itself. User's install is authoritative even if it's a different version than `plugin.json` declares — deliberate trade for ergonomics. Appropriate when the upstream binary is published to multiple package managers and users routinely install it that way.

### Pointer-file shim invoked via `.mcp.json`

A `bin/python_shim.sh` (POSIX) + `bin/python_shim.ps1` (Windows) reads `${CLAUDE_PLUGIN_DATA}/python_path.txt` (written by the venv-bootstrap SessionStart hook), validates the path is executable, and `exec "$PY" "$@"` to run the requested server script. `.mcp.json` invokes via `bash ${CLAUDE_PLUGIN_ROOT}/bin/python_shim.sh <server.py>`. Appropriate when the venv interpreter path is OS-dependent and unknown until first session; decouples MCP registration from path encoding. Constrains: if the venv hook has never succeeded, `python_path.txt` is missing and the shim exits 127 with a corrective message; recovery requires the user to install the prerequisite and restart Claude Code. The PowerShell sibling exists but `.mcp.json` only references the `.sh`, leaving Windows users dependent on Git Bash or WSL.

### Multi-script bin family / CLI dispatcher

A `bin/` directory contains many small per-purpose scripts (`pos-init`, `pos-config`, `pos-analytics`, `pos-sync`, `pos-telemetry`, `pos-update-check`, plus a Node installer) rather than one entry point. Each script handles one verb; hooks invoke them via full path. Multi-script bash CLI variant uses uniform `#!/usr/bin/env bash` shebang and computes `<TOOL>_HOME="${CLAUDE_PLUGIN_ROOT:-${<TOOL>_HOME:-$(dirname "$SCRIPT_DIR")}}"` so the scripts work under plugin install, manual clone, or ad-hoc invocation. Sources a shared library (`lib/state.sh`) for state operations. POSIX-only (no `.cmd`/`.ps1` pair); macOS-aware (e.g., warns "no `grep -P`; use `sed`/`awk`/`python3 -c`"). Appropriate when the plugin exposes a CLI surface with many independent operations to user and to internal hooks. Constrains permissions discipline: scripts invoked by full path do not require executable bits, so chmod handling is inconsistent.

### Marketplace-root bin with per-plugin symlink

`bin/<wrapper>` at the marketplace root is a stdlib Python script with `#!/usr/bin/env python3` shebang. Each consuming plugin ships `plugins/<name>/hooks/<wrapper>` as a git-tracked symlink (mode 120000) pointing at the shared file. Hook configuration invokes via `${CLAUDE_PLUGIN_ROOT}/hooks/<wrapper>`. The wrapper resolves the plugin name from `plugin.json` and the marketplace name by walking up to `.claude-plugin/marketplace.json`, then enriches its output with provenance metadata. Appropriate when multiple plugins in one marketplace want a shared executable without copy-paste duplication. Critical constraint: Claude Code installs by copying the plugin directory only, so the symlink target must be relative (e.g., `../../../bin/<wrapper>`) to survive the copy. Absolute symlink targets keyed to the author's home directory break on every other machine — the install ships dead symlinks. Observed in lower-discipline form, where the documented intent is correct but the committed symlink targets are absolute.

### Git-symlink bin wrappers (mode 120000)

`bin/<friendly-name>` files are committed as git symlinks (mode 120000) pointing to `../scripts/<real-name>.sh`. Provides user-friendly naming at the bin layer without duplicating script content; target scripts use `dirname "$0"`-based resolution which transparently resolves through the symlink to the real-file plugin root. Constraint: Windows-native git checkouts convert symlinks to plain text files containing the target path unless `core.symlinks=true` — silently breaks on Windows. Also depends on the target file having the executable bit set.

### Polyglot CMD/bash wrapper for cross-platform hook invocation

A single file (`run-hook.cmd`) interpreted differently by `cmd.exe` (Windows batch syntax) and by `bash` (via `: << 'CMDBLOCK' … CMDBLOCK` heredoc trick). Searches `C:\Program Files\Git\bin\bash.exe` and `C:\Program Files (x86)\Git\bin\bash.exe`, then `bash` on PATH; silently succeeds if none found. Hook script filenames are deliberately extensionless (`session-start`, not `session-start.sh`) to avoid Claude Code's Windows auto-detection prepending `bash` to any `.sh` command. Used internally by SessionStart, not as a user-facing CLI.

### TypeScript bun-shebang launcher with download fallback

`bin/<name>-wrapper.ts` carrying `#!/usr/bin/env bun`. Self-heals `node_modules`, verifies the native binary exists at `bin/<name>[.exe]`, downloads/version-checks via a sibling downloader module, forwards argv to the binary via `spawnSync` with `stdio: "inherit"`. Cross-platform `.exe` suffix branching, GOOS/GOARCH-specific binary naming. Plugin-root resolution precedence: custom env var > `CLAUDE_PLUGIN_ROOT` > `realpathSync`-based script-dir fallback for symlink-via-`node_modules/.bin/` installs. Bun-specific calls (`Bun.sleepSync`) bind the wrapper to Bun even though the downloader supports Node.

### Single bash wrapper exec'ing a Node bundle

`bin/<tool>` is a thin bash wrapper that resolves `PLUGIN_ROOT` from the script location and `exec node "$PLUGIN_ROOT/dist/index.js" "$@"`. Script-relative resolution only — does NOT consult `${CLAUDE_PLUGIN_ROOT}`. Fails if `dist/` isn't shipped (e.g., when `.gitignore` excludes the build output and no `prepare`/`postinstall` builds it at install time). When the bundle isn't present, downstream consumers fall through to a different CLI resolution path (e.g., the SessionStart-installed global `<tool>` on PATH), making the in-repo wrapper effectively dead code despite its comment claiming "works without global npm install" — wrapper-as-aspirational-contract rather than wrapper-as-runtime.

### Plugin-bin + npm-bin dual-target

`package.json` declares `"bin": {"<tool>": "./bin/<tool>"}` so `npm install -g <tool>` or `npx <tool>` exposes the same CLI the plugin install does. Dual-target distribution lets users drive the tool without installing Claude Code plugins at all. Adds `engines.node >= <N>` to `package.json` even if the core plugin code is bash/Python — Node is only needed for the npm consumption path. npm symlinks the binary into the user's `node_modules/.bin/`; on a global install it's on PATH. The plugin manifest is a thin alias and the bin reaches the user via the npm package, not through `/plugin install`'s payload. Used when the same project ships as both a Claude plugin and an npm package.

### npm bin entry without shipped binary (dead)

`package.json` declares `"bin": {"<name>": "./<path>.js"}` for npm `npx` distribution. Inside Claude Code the JS is invoked via `node "${CLAUDE_PLUGIN_ROOT}/dist/cli/index.js"` from `mcp.json` args rather than through the bin entry. Sometimes the bin path is dead — `package.json` references `./src/cli.js` but `src/` doesn't exist in the committed tree, leaving npm metadata pointing at vapor.

### Discovery utility — bin as context bridge

A 5-line bash script that prints the plugin's root directory. Not a user CLI; skills invoke it (e.g. `<plugin>-plugin-root 2>/dev/null`) to locate the plugin tree when `$CLAUDE_PLUGIN_ROOT` is unavailable. The pattern exists because Claude Code populates `$CLAUDE_PLUGIN_ROOT` only in hook contexts, not in skill or agent contexts. Skill preambles use a triple-fallback chain — env var if set, bin-wrapper output, or a hard-coded install path for cross-runtime portability. Distinct role from user-CLI bin: this is bin-as-discovery, not bin-as-tool. Constrains the rest of the plugin to assume `bin/` is on PATH.

### Script-relative shell wrapper

`bin/<name>` is a short bash script that resolves `PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"` and execs the actual binary (typically Python). No `${CLAUDE_PLUGIN_ROOT}` env var check, no fallback cascade — strictly script-relative, always. Works because Claude Code's cache preserves the repo's internal directory layout. Pairs naturally with a PreToolUse hook that hard-blocks any regression to the env-var-based pattern. Wrapper itself is ~6 lines with `set -u` only (deliberately omitting `-eo pipefail` so trailing args aren't lost before the terminal `exec`). Constrains: assumes the bin and its target library remain in fixed relative positions; refactoring layout requires updating the wrapper.

### Daemon launcher (no bin-wrapper)

No `bin/` directory. The plugin entry point is reached via `"$VENV_DIR/bin/python" -m <pkg>` directly from the SessionStart hook, spawned with `nohup ... &` so the daemon detaches. Lifecycle managed via `/tmp/`-based socket/PID/refcount files. Users wanting to inspect or restart the daemon do so via tail-the-log + kill-the-PID, not a CLI.

### Node-only with mcp.json invocation

Plugin runtime is JavaScript; the binary is invoked via `node "${CLAUDE_PLUGIN_ROOT}/dist/cli/index.js" mcp` directly from the MCP server config or hook commands. No bash wrapper, no executable bit needed. Appropriate when plugin is pure Node and target platforms include Windows where bash wrappers fail. Constrains hooks that need shell features to live in separate `.sh` files invoked by `bash "$CLAUDE_PLUGIN_ROOT/hooks/foo.sh"`.

### `${CLAUDE_PLUGIN_DATA}` with HOME fallback

The wrapper reads `${CLAUDE_PLUGIN_DATA}` to locate its venv and falls back to `$HOME/.claude/plugins/data/<plugin-name>` if the env var isn't set. Does not consult `${CLAUDE_PLUGIN_ROOT}`. Appropriate when the wrapper needs the venv (in plugin data) but not the plugin source — running the installed package, not the source. Trade-off: hard-codes a conventional fallback path; if the harness's plugin-data layout changes, the fallback breaks silently.

### Source activate then exec python vs direct exec

Two variants for invoking a venv Python from a wrapper:

- **Source activate then exec** — wrapper `source`s `$VENV_DIR/bin/activate` then `exec python -m <module>`. Functionally correct because `source activate` mutates `$PATH` and sets `VIRTUAL_ENV`. Strictly weaker than direct-exec: requires the activate script to be present (some `uv`-managed venvs may omit it); is bash-only (`source` not portable to `dash`); sources ~50 lines of activate boilerplate; depends on `$PATH` order surviving any conda or other venv init.
- **Direct exec of venv Python (no activate)** — wrapper does `exec "$VENV/bin/python" -m <module> "$@"` without sourcing `activate`. Avoids the entire activate-script surface, works under any minimal shell, runs identically against `uv`-managed and stripped venvs that may lack `activate` entirely. Pairs naturally with the wrapper resolving the venv via env var (e.g., `${CAIRN_VENV}`) populated in `$CLAUDE_ENV_FILE` by the SessionStart bootstrap.

### `cd`-before-exec with `--file` argument rewriting

The wrapper resolves selected relative-path arguments (e.g., `--file <path>`) against `$ORIG_CWD` before `cd "$STATE_DIR"`, then `exec`s the entry point. Because the entry point is forced to a fixed working directory (state dir), any user-passed relative path that isn't pre-resolved would silently resolve against `$STATE_DIR` instead of the user's PWD. The `--file`-only rewrite is partial coverage — other relative-path flags pass through unresolved. Argument parsing uses a `next_is_file=true` flag walk over `"$@"`, which handles `--file path` form but not `--file=path` (equals-form passes through unresolved).

### Zero-dependency Node self-installer at `bin/cli.js`

Single-file Node.js CLI (~1,300 lines) using only stdlib (`https`, `zlib`, `fs`, `crypto`, `child_process`, `readline`). Hand-rolled implementations of: GitHub API client, https downloader, in-memory `tar.gz` extractor with path-safety validation, interactive `readline`-raw-mode multiselect, hook-config merger with surgical-unmerge tagging. Invoked via `npx github:<owner>/<repo>` (no npm registry publish needed). Cross-platform via `process.platform === "win32"` checks. Maintenance burden is high (TAR parsing from scratch) but supply-chain surface is zero.

### Single-file install + skill copy via standalone installer

`install.sh` / `install.ps1` at repo root for non-plugin install methods runs `pip install <subdir>/` and copies the canonical `SKILL.md` into the user's skills directory. Independent from the plugin-marketplace install path: same source tree, two install mechanisms, two copies of `SKILL.md` (root copy for standalone-install consumers; `skills/<name>/SKILL.md` for plugin-install consumers) maintained in parallel. Appropriate when the author wants to support both Claude-Code-plugin-installed users and standalone-skill-copy users from one repo; constrains single-source-of-truth because the same content must land in two places.

### `bin/.gitkeep` placeholder populated by setup

`bin/` directory checked in with only a `.gitkeep` placeholder; `scripts/setup.sh` populates `bin/<binary>` at first run by compiling C source (`cc -Wall -Wextra -O3 hellwal.c -o bin/hellwal`) and downloading prebuilt tarballs. Linux/x86_64 hardcoded — porting to other platforms requires script edits.

### Stale hardcoded paths after rebrand

A bin script targets a hardcoded path under `~/.claude/plugins/cache/<old-slug>/<old-slug>/<old-version>` rather than resolving via `CLAUDE_PLUGIN_ROOT`. After a project rebrand, the path is stale and the script silently no-ops. A refactor-rot signal: any bin script with a hardcoded cache path is a candidate for the env-var-resolution pattern.

### Orphaned wrapper alongside downloaded binary

`bin/<plugin>-wrapper.sh` is committed and `chmod +x`ed but `plugin.json`'s `lspServers.command` (or equivalent) points directly at the downloaded native binary, not the wrapper. The wrapper sources a `~/.config/<plugin>/config` file before `exec`ing the binary; the binary itself reads the same config natively, making the wrapper redundant. Classic half-refactored state — wrapper was written first, then superseded by in-binary config loading, then left in place.

### Committed binaries in tree

Pre-built platform-specific binaries are committed to the repo (`bin/harness-darwin-arm64`, `bin/harness-linux-amd64`, etc.) and dispatched at runtime by a shim that detects `uname`. Users get binaries by cloning. Trades repo size (~33MB of binaries per clone) for zero runtime install latency and zero dependency on GitHub Release artifacts being present. Single-architecture gaps are handled by graceful no-op.

### Version-floor declared only in prose

The minimum Claude Code version supporting a feature (`v2.1.91+` for `bin/`) is declared in a script docstring, a README section header, and README prerequisites — three documentation layers, zero machine-readable fields. `plugin.json` has no `requires.claude-code` / `engines` field. Constrains version-floor enforcement to graceful-degradation discipline (Claude Code silently ignores unknown hook events / fields, so older hosts get partial functionality). Appropriate when no machine-readable mechanism exists upstream and the plugin author prefers prose-documented degradation over a hard precondition check.

## Plugin-runtime root resolution

How bin scripts and hooks find the plugin's installed location across substrates.

### Two-tier env-var-first fallback

Bash scripts use `${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}`; sh scripts use `dirname "$0"`-based equivalents; cmd files use `IF "%PLUGIN_ROOT%"=="" SET PLUGIN_ROOT=%~dp0..`. Canonical pattern across all bin and hook scripts in a sample. The fallback enables raw-clone development without invoking through Claude Code. Appropriate as the single resolution mechanism; deviations (hardcoded cache paths) are refactor-rot.

### Three-tier with hardcoded data-dir terminal fallback

`${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd || echo "$HOME/.config/<plugin>")}` adds a hardcoded user-config path as the third tier — semantically wrong for code that needs to read SKILL.md siblings but works by coincidence because `2>/dev/null || true` swallows the resulting failures.

### Cascading multi-host fallback

`${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}` supports invocation from Claude Code (first), Codex (second), or git working tree (third). Used when the same plugin code ships into multiple agent ecosystems.

### Plugin-root resolution with custom env-var precedence

Wrapper reads a plugin-specific env var (e.g., `AIDE_PLUGIN_ROOT`) before `CLAUDE_PLUGIN_ROOT`, then falls back to `realpathSync`-canonicalized script-dir. Custom-var-first rationale: the same wrapper ships to multiple AI-coding-assistant ecosystems (Claude Code, OpenCode, Codex CLI), and `CLAUDE_PLUGIN_ROOT` is treated as a Claude-Code-specific fallback rather than the primary.

### Centralized inline-bootstrap dispatcher

Every hook command is ~1.5KB of inline `node -e "..."` boilerplate that re-implements `CLAUDE_PLUGIN_ROOT` resolution across a fallback chain (env var → `~/.claude` direct → six well-known plugin slug paths → versioned cache dirs), then hands off to `plugin-hook-bootstrap.js` which calls `run-with-flags.js {event-id} {handler-script-path} {profile-flags}`. Hook IDs use a structured `{lifecycle}:{scope}:{purpose}` taxonomy (e.g., `pre:edit-write:gateguard-fact-force`). Profile gating (`standard`, `strict`) lets users opt in or out of disciplines. Appropriate for plugins with many hooks and uncertainty about how reliably the host sets `CLAUDE_PLUGIN_ROOT`. Constrains: SessionStart specifically had to be extracted to a standalone file because inline `!` characters trigger bash history expansion and produce a visible CLI error header; the inline pattern is fragile across shell environments.

## Dependency installation

How runtime dependencies (Python packages, Node modules, native binaries, system tools) reach the user's machine on first use and on update — runtime ecosystem, manifest format, install location, change detection, install trigger, and failure recovery.

### Zero dependencies / stdlib only

The plugin deliberately ships no runtime dependencies — hooks are capped at language built-ins (Node `fs`/`path`/`crypto`/`child_process`; Python stdlib only). No `requirements.txt`, no `pyproject.toml`, no `package.json` `dependencies`. Probes for system tools (audio players, `gh`, `jq`, PHPStan, ESLint, deptrac, dependency-cruiser, shellcheck, `python3`, `bash 3.2+`) at runtime; features light up when their required tool is present, absent tools mean degraded but still-functional behavior. Documented as a degradation ladder rather than a caveat (e.g., `docs/CI.md` documents "intentionally zero-dependency"). Tests are stdlib-only too (`unittest`, no pytest). Appropriate when the plugin's value proposition includes "zero setup" — sidesteps `uv`/`pip` questions, venv placement, and Python ABI tracking entirely; removes supply-chain risk and the SessionStart-install lifecycle entirely. The cost is hand-written replacements for what libraries would provide (custom JSON-schema validation, mini YAML parsers, bespoke circuit breakers), often amounting to substantial test-code volume; constrains the plugin to whatever bash + stdlib Python can do. Runtime prerequisites documented in README (`Python 3.6+`, `Bash`, `Git`) are not validated at session start — silent failures if a stdlib feature exceeds the documented floor.

### Zero-dep system-tool stance (bash + jq only)

The plugin requires only bash (4+) and `jq` (1.6+), both expected to be present on the user's system. No SessionStart-installed venv, no Python packages, no npm packages, no binary downloads. Appropriate for plugins whose business logic fits in shell. Trade-off: avoids the entire dep-install surface and its failure modes, but constrains the tools the author can use. System-tool requirements are stated in README only — there is no runtime probe checking versions before use, so older platforms with bash 3.2 by default produce cryptic failure modes.

### No managed install — pure shell/markdown

The plugin assumes a baseline of system tools (`bash`, `jq`, `git`, `python3`) on `$PATH` and detects everything else at runtime via `command -v`. No install hook, no manifest, no cache directory. Failure mode: silent degradation when a missing tool is reached at runtime — a hook depending on `jq` simply behaves differently when `jq` is absent because there's no install path to fail.

### Delegated to PyPI runner (`uvx`)

No plugin-side install state. `uvx` fetches the wheel on demand; the plugin directory holds no installed deps. No SessionStart install hook. Appropriate when dependencies belong to an upstream package the plugin only references. Failure mode is a standard MCP server launch failure — Claude Code reports the missing `uvx` or the unresolvable package; no plugin-specific error path.

### Pip + stdlib venv (no `uv`)

Python deps are installed into `${CLAUDE_PLUGIN_DATA}/venv` via stdlib `venv` + pip during a SessionStart hook. The install script reads `pyproject.toml` for the dep list and pip-installs the plugin root itself as an editable-style package so its own `lib/` becomes importable from skill scripts. A version stamp file at `${CLAUDE_PLUGIN_DATA}/installed-version` short-circuits the install on subsequent sessions when its content matches `plugin.json.version`. Appropriate for plugins that need third-party Python packages but don't want to require `uv` on the user's system; the cost is slower first-install (~tens of seconds, sometimes synchronously blocking SessionStart) and reliance on the host having a usable system `python3`.

### Plugin-data venv with `diff -q` change detection

Bootstrap script (`bootstrap.py` or `install-deps.sh`) creates `${CLAUDE_PLUGIN_DATA}/venv`, pip-installs requirements plus the plugin package, then injects `site-packages` onto `sys.path` and rewrites `sys.executable`. Change detection via byte-comparison (`diff -q`) against a copy of `requirements.txt` saved into `${CLAUDE_PLUGIN_DATA}` as a marker. Strong invariant when paired with `set -e`; weaker when subprocess return codes aren't checked before stamping the marker. Isolates plugin deps from the user's Python environment at the cost of needing the venv to survive Python upgrades.

### `pip install` against `sys.executable` (no venv isolation)

SessionStart Python hook (`auto_install.py`) tries `import <package>`; on `ImportError`, runs `pip install git+https://<repo>.git` against whatever `sys.executable` resolves to (typically user-global or active interpreter). No venv isolation — mutates user's Python environment silently. Restart of Claude Code is required after first install for the MCP server to pick up the new `sys.path`; this is signaled back to the user via `hookSpecificOutput.additionalContext` declaring "Please restart Claude Code to activate MCP tools." Appropriate as a low-ceremony bootstrap; risky on system-Python with restricted site-packages.

### Ad-hoc per-invocation fetch via `uv run --with`

Python plugins use `uv run --with <pkg> python3 ...` as the hook command. uv's global cache satisfies subsequent invocations (~3s first run, ~3ms cache hit per author measurement). No `SessionStart` hook, no `${CLAUDE_PLUGIN_DATA}` venv. Constrains the plugin to one-shot Python invocations (no long-running state across hook fires); requires `uv` on PATH; the plugin does not own a venv. Appropriate for thin plugins where dep set is small and per-invocation latency is acceptable.

### Inline-deps-per-script (PEP 723)

Every Python file (bin dispatchers, skill scripts, hooks, monitors) starts with `#!/usr/bin/env -S uv run --script` plus a `# /// script` block declaring `requires-python` and exact-version deps (e.g. `httpx==0.27.2`). No `requirements.txt`, no `pyproject.toml`, no `__init__.py`. Each script invocation creates or reuses uv's cached ephemeral env keyed by the inline-dep hash. Trade-off: cold-start cost on every subcommand because subprocess-dispatch from a bin wrapper to a skill script materializes a fresh env, but no plugin-managed venv to maintain or invalidate.

### SessionStart-driven Python venv with hash gating

A `SessionStart` hook (`scripts/setup.sh`, `ensure-venv.sh` / `ensure-venv.ps1`, ~180s timeout in some samples) creates a venv under `${CLAUDE_PLUGIN_DATA}/venv/`, runs `pip install -r requirements.txt`, then on success copies `requirements.txt` to `requirements.stamp` (or computes sha256 → `requirements.hash`). Next session: `diff -q requirements.txt requirements.stamp` (or hash compare) skips re-install when unchanged. The stamp-write-after-success structure is the retry invariant: failures leave the stamp absent or stale, so the next session retries the diff path. On failure, the script emits `{"systemMessage": ...}` JSON with `exit 0` (never block); pip stderr redirects to `install.log`. Appropriate when the plugin owns its runtime and dependencies are non-trivial. Constraints: hash is over the declared-deps file, not a lockfile, so transitive-dep upstream patches are invisible; no Python minor-version stamping (a user upgrading Python keeps the old venv); `install.log` doesn't rotate; install location may not be where the MCP launch command points; `shasum` (BSD/macOS) vs `sha256sum` (Linux) is a fragility surface — a script that uses ONLY `shasum -a 256` with no `sha256sum` fallback aborts via `set -e` with "command not found" on Linux distros where Perl-based `shasum` is absent. Hashing variant: concatenate `pyproject.toml` + `bridge/*.py` and pipe through `md5 -q` (BSD) with `md5sum | cut -d' ' -f1` fallback (GNU) and a final `|| echo "none"` trapdoor — content-aware hash, with the `"none"` fallback either causing forever-reinstall (re-stored each session) or pin-forever (stored verbatim), depending on persistence semantics. Source-aware variant: hash sorted concatenation of source files plus manifest plus docs (`pipeline/**/*.py + pyproject.toml + *.md`) when the plugin treats itself as a pip-installable package and `pip install --force-reinstall ${PLUGIN_ROOT}` runs on every change — over-eager invalidation (editing README triggers reinstall) is a known trade-off.

### Python uv preferred, pip fallback

Hook detects `uv` and uses it for venv creation + install (`uv venv`, `uv pip install`); falls back to stdlib `python -m venv` + `pip install` if `uv` is absent. The package manager preference is encoded in the script's branching, not in any manifest. Appropriate when the plugin needs Python tooling and wants the speed of `uv` when available without making it a hard dependency. Both paths produce a venv at the same location.

### Per-user venv with project-mode + npx-mode forks

Plugin mode uses `${CLAUDE_PLUGIN_DATA}/venv`; npx-bootstrap mode uses `~/.<plugin-name>/venv`. Skills resolve `$<PLUGIN>_PY` env var with shell-default fallback to the npx path. Appropriate for multi-runtime plugins. Constrains: a user who installs both ways ends up with two venvs — skill invocations are non-deterministic about which one runs unless skills always read `$<PLUGIN>_PY` first.

### Manual venv with documented commands

The plugin documents `python3 -m venv .venv && .venv/bin/pip install -r requirements-optional.txt` in README/CLAUDE.md and ships no auto-install mechanism. Optional deps live in `requirements-optional.txt` with a header explicitly invoking PEP 668. Appropriate when the dep surface is large, version-sensitive, and the author refuses to pollute the user's environment. Constrains user experience: "plugin installed" diverges from "plugin functional" — features silently degrade when optional deps are missing (e.g. ChromaDB falls back to grep). The plugin must tolerate every dep being absent.

### `requirements.txt` with manual user invocation

A skill ships `requirements.txt` with pinned versions; SKILL.md or a comment in the file instructs the user to run `pip install -r requirements.txt --break-system-packages` themselves. Reproducibility depends on user discipline; `--break-system-packages` is user-hostile on PEP 668-managed systems where no plugin-managed venv exists. No change detection, no retry, no failure signaling — entirely user-driven.

### First-run pip-install in bin wrapper

The bin wrapper probes for a Python module (`python -c "import <module>"`) and on ImportError runs `pip install <pkgs> --quiet` against whatever `python`/`pip` are on PATH. No venv, no version pinning, no lockfile, no change detection beyond existence. Appropriate as the minimum viable Python-dep-install pattern. Constrains everything else: dependency isolation becomes the user's problem; PEP 668 externally-managed-environment errors surface to the user rather than being handled; `python` (vs `python3`) PATH assumptions break on Linux distros that ship only `python3`. Idempotent by retry (every invocation re-probes) but not hook-driven. The `.cmd` Windows counterpart cannot replicate `set -e` and silently swallows failed installs.

### Inline `python3 -c` for ad-hoc scripting

Bash hooks pipe data through `python3 -c "..."` for JSON manipulation rather than declaring a Python dep. Relies on system Python 3 being present. Appropriate for tiny one-shot transformations in shell hooks; constrains the plugin to whatever standard library the system Python provides.

### Ad-hoc per-invocation fetch via `npx --yes --package`

Node plugins use `npx --yes --package <name> <bin> serve` as the MCP-server command. Resolves through the user's npm cache; first launch fetches from the registry. The unpinned form silently rolls forward with whatever `latest` resolves to. A pinned variant (`<name>@<version>`) is available but not surfaced as the default. Constrains the runtime to npm-cache state; auto-upgrade is the default behavior unless the user explicitly pins. Appropriate when the plugin is itself an npm package and wants to share its CLI surface across multiple host integrations.

### Node `npm install --prefix ${CLAUDE_PLUGIN_ROOT}` from SessionStart

SessionStart hook runs `npm install --prefix "${CLAUDE_PLUGIN_ROOT}"` reading `${CLAUDE_PLUGIN_ROOT}/package.json`. Installs land in `${CLAUDE_PLUGIN_ROOT}/node_modules`. Choice of ROOT over DATA is rooted in ESM module resolution: ESM walks up from the importing file looking for `node_modules/`; installing into `CLAUDE_PLUGIN_DATA` would place node_modules outside that walk path, and ESM deliberately ignores `NODE_PATH`, so the CJS env-var workaround cannot bridge the gap. Pure-ESM workers (`"type": "module"` + top-level `import`) require the install path to be adjacent to the import sites.

### SessionStart Node hook with mtime-driven `npm install`

Hook (`hooks/mcp-deps-install.js` or similar) registered on SessionStart iterates install targets (`mcp/`, `packages/<lib>/`) and reinstalls when `node_modules/` is absent, `package-lock.json` is absent, or `package.json` is newer than `node_modules/.package-lock.json`. Calls `execFileSync(process.execPath, [npmCli, ...args])` resolving `npmCli` from Node's bundled npm rather than bare `npm` on PATH. Prefers `npm ci` when a lockfile exists, falls back to `npm install`. On failure, removes `node_modules` so next session retries. Diff-based change detection means repeated runs converge without redoing work.

### SessionStart hook → npm install local to plugin

A SessionStart hook runs an `install-deps.sh` script (or `npm install --production`) that populates `node_modules/` either inline in the install script's hard-coded list or driven by a committed `package.json`. The package list may be hard-coded inline (no committed manifest, just `npm install <pkg> <pkg>` in the script) or driven by a `package.json` that may or may not also commit a lockfile. Where no `package.json` ships, the install script generates a minimal `{"private":true}` `package.json` at install time so npm has a valid project to operate on. Idempotency is gated by various detection mechanisms (sentinel + version file, sha256 hash, `diff -q`, ABI marker — see *Install change detection*). Failure path explicitly removes the sentinel and version files so the next session re-attempts install. Script is `set +e` with `|| exit 0` fallthrough on every failure, with the explicit comment `MUST NEVER exit non-zero — that blocks sessions`.

### SessionStart hook → npm install pinned to plugin version (global)

The SessionStart hook runs `npm install -g <pkg>@<plugin-version>`, where `<plugin-version>` is grep-extracted from `plugin.json`. Installs into the user's npm prefix (global), not the plugin directory. Opt-out via env var (e.g., `<TOOL>_NO_AUTO_INSTALL=1`). The plugin "installs its own peer CLI" as a side effect of session startup. Pin is exact (`@<version>`) — fully deterministic per session. Constraints: requires `npm` on PATH (fail-open with stderr warning otherwise); writes to a global location outside `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}`, mutating the user's system state; matcher set to `*` means version check fires on `clear` and `compact` too; 120-second hook timeout may be tight for cold installs on slow networks; opt-out env var is undiscoverable unless the user reads the hook source.

### SessionStart hook → npm install inside `${CLAUDE_PLUGIN_ROOT}`

The SessionStart hook runs `npm install` inside `${CLAUDE_PLUGIN_ROOT}/<server-dir>/`, populating `node_modules/` adjacent to the importing JS files. Driven by a hash sentinel (`sha256` of `package.json`, persisted to `.package-hash` next to `node_modules/`); reinstall fires when hash differs OR `node_modules/` is missing. Fallback hash chain handles missing `sha256sum` / `shasum` / last-resort `wc -c` byte count. The install location choice is load-bearing — ESM `import` resolution walks the filesystem from the importer's location looking for `node_modules`, and `NODE_PATH` is CJS-only (silently ignored by ESM). So `${CLAUDE_PLUGIN_DATA}/node_modules` would break every `import`. Documenting this rationale inline in the install script (rather than in a separate planning doc) gives any developer reading the hook the "why" without external references.

### Plugin data dir with symlink-out

Install into `${CLAUDE_PLUGIN_DATA}/<deps>` (writable user data dir) then `ln -sfn $PLUGIN_DATA/node_modules $PLUGIN_ROOT/node_modules` so ESM `import` from plugin source resolves without `NODE_PATH` hacks. Inverse of "install into plugin root"; relies on the plugin root being a managed/read-only space. Constrains nothing for the consumer; the plugin author must remember to keep the symlink fresh on every reinstall.

### Version-stamped persistent install with back-symlink

`node_modules` (or equivalent) installs into a stable location under `$CLAUDE_PLUGIN_DATA` (e.g. `$CLAUDE_PLUGIN_DATA/cdp-node_modules/node_modules/`) and a `ln -sfn` symlink back into `$CLAUDE_PLUGIN_ROOT/<expected-path>/node_modules` so relative `require` resolves. Solves two problems at once: the plugin cache is wiped on every Claude Code update (so installs into ROOT do not survive), and the runtime still expects modules at the in-tree path. A version stamp file (`$CLAUDE_PLUGIN_DATA/<dir>/.version-stamp` containing the sub-package's `package.json` version) is the change-detection key — reinstall triggers when stamp absent OR mismatched. Pre-scans for a dangling symlink from a previous persistent install and cleans it before falling back to a local install. Includes a stamp-flip-flop guard: skip persistent path when the runtime is unavailable (e.g. `node` missing), so an "unknown" version cannot be written.

### Diff-based change detection with separate sentinel and manifest

Two manifests coexist with different roles: `package.json` is what npm actually reads (`npm install --prefix` reads the prefix dir's `package.json`), while a sibling `runtime-deps.json` (or similar) is the sentinel-diff source for idempotency. SessionStart runs `diff -q $MANIFEST $SENTINEL` against `${CLAUDE_PLUGIN_DATA}/.<plugin>-deps-installed.json`; on mismatch, reinstall + update sentinel. Double-checked with `[ -d "${ROOT}/node_modules/<probe-pkg>" ]` so an external `node_modules` wipe forces reinstall even with intact sentinel. The two manifests can drift — undocumented constraint that the sentinel must mirror the npm-read manifest, or the diff lies. Failure path: `rm -rf node_modules` + `rm -f $SENTINEL` so next session retries clean.

### Self-healing inline install at MCP launch

`scripts/mcp-wrapper.sh` independently runs `npm install` if a probe directory under `node_modules/` is missing when the MCP server launches. A second install path — not a fallback delegate, a full duplicate — covering the race where Claude Code spawns the MCP server before the SessionStart hook completes. Variant: a bin-wrapper invoked by Claude Code as the MCP server entry detects missing `node_modules` (gitignored, lost after marketplace `autoUpdate`) and runs `bun install --frozen-lockfile` inline before delegating. Lazy `require('cross-spawn')` after install completes lets the bootstrap survive starting from empty. Suits plugins where the MCP server may launch parallel to or before SessionStart. Makes the install idempotent across two entry surfaces. Constrains the runtime: Bun (or Node) must be on user PATH; the wrapper has no graceful-degradation path if it isn't.

### Manual `npm install` post-install

No `SessionStart` hook for install. README instructs users to `cd` into the plugin cache directory and run `npm install` once. `node_modules/` materializes inside the plugin root. Change detection is the user reading `ls node_modules/zx`. Failure mode is silent: if `npm install` was never run, hook handlers fail at `import` time before any top-level `try/catch` can engage. Deviates from the docs-prescribed `diff -q`/retry-next-session pattern; the author has accepted this friction in exchange for not maintaining an install hook. Required when hooks need an npm runtime dep (e.g., `zx`) that the plugin cannot ship pre-resolved.

### Mixed Python + Node install

Two parallel dep stories coexist: Python via PEP 723 inline metadata (every `.py` script declares its own deps) and Node for an MCP-channel server (installed via a SessionStart hook gated by `diff -q`). The Node side prefers `bun` and falls back to `npm`, runtime-probed via `command -v`. Persistence retry-invariant uses stamp-on-success rather than the docs-example rm-on-failure: the cached `package.json` is only copied AFTER `node_modules` is verified present.

### SessionStart-driven dual-runtime install (Python venv + Node modules)

A single SessionStart shell hook handles both Python venv + `pip install -r requirements.txt` and Node `npm install` in the same script. Each manager is guarded by `diff -q` between the source manifest in `$CLAUDE_PLUGIN_ROOT` and a cached copy in `$CLAUDE_PLUGIN_DATA`. On `diff` miss, install runs and cache is refreshed; on install failure, the cached copy is `rm -f`'d so next session retries. Symmetric retry semantics across both ecosystems in one script. Distinct from per-manager hooks: one hook fans out to N managers with identical diff/retry shape. Refinements: `diff -q` is sensitive to source-vs-cache equality only — a flaky-network install that returns 0 but partially lands packages will leave an "in sync" cache that does not retry. `2>/dev/null` suppression on the install branches keeps stderr quiet to avoid corrupting the JSON channel the same hook uses for context injection, but loses corrective error messages. `python3 -m venv ... 2>/dev/null || true` makes venv-creation failure invisible — a user without `python3-venv` installed gets a silent no-op then a confusing "pip not found" downstream.

### In-tree vendored node_modules

`node_modules/` (or pnpm `.pnpm/`) committed directly into the plugin tree. No install step at runtime; deps load straight from the committed copy. Appropriate when the plugin author wants zero-install determinism. Constrains: platform-specific binaries (e.g., `@esbuild/linux-x64`) inside the vendored tree lock users to whatever OS/arch was committed — Windows or Darwin users get a broken install with no automatic recovery.

### Bun install via Node packaging

`package.json` plus `bun.lock` declare Node deps; the npm-published installer runs `bun install` into the installer's working directory. Plugin-marketplace installs do NOT run `bun install` — only the npm install path does. This means features gated on `node_modules/` (Ink TUI, dashboards) silently fall back to plain text on a marketplace install. Appropriate when Node is the primary toolchain and npm is the distribution substrate; constrains the marketplace path to graceful degradation for everything Node-dependent.

### Repo-local Node install via shell wrapper

`install.sh` (POSIX) and `install.ps1` (Windows) at repo root run `npm install --no-audit --no-fund` into a repo-local `node_modules`, then delegate to a Node-based real installer (`scripts/install-apply.js`). Existence-only change detection (`if [ ! -d node_modules ]`); no checksum stamping. Appropriate when the plugin predates the Claude Code plugin spec and needed its own user-facing install entry. Constrains: marketplace-flow installs bypass `install.sh` entirely; the path's completeness via the plugin runtime is uncertain.

### Hook-driven prebuilt native binary

`SessionStart` hook downloads a prebuilt platform-specific binary (Rust release artifact) into `${CLAUDE_PLUGIN_ROOT}/bin/`, picking the right asset by detecting OS and architecture (`macos-arm64`, `linux-x86_64`, `linux-arm64`). Existence-only change detection: the script no-ops if the binary exists, so `/plugin update` does not re-download — users must manually wipe the cache to pick up a new binary. Calls the unauthenticated GitHub Releases API at install time, coupling first-run success to GitHub rate limits. No sha verification; trust is implicit in HTTPS plus GitHub Releases.

### Native binary downloaded on first use with version-stamp idempotency

A SessionStart hook (or lazy bin-wrapper, or both) downloads a pre-built native binary from a GitHub release into `${CLAUDE_PLUGIN_DATA}/bin/<name>`. Change detection via a sibling `<binary>.version` stamp file written *only after* successful extraction (`tar xzf` then `chmod +x` then `xattr -d com.apple.quarantine` then write stamp). A failed download leaves no stamp; the next invocation re-attempts cleanly without explicit `rm`-on-failure. Version compared against `plugin.json`'s `version` (read with `jq -r`). Appropriate when the binary is a separately-cross-compiled artifact too large to vendor in git. Constraint: the asset URL pattern is hardcoded in the shim; release-workflow asset-name changes must be coordinated.

### Native binary with versioned-then-floating download URLs

Wrapper attempts a versioned URL (`releases/download/v<plugin-version>/<binary>`) first, then falls back to `releases/latest/download/<binary>`. Mitigates a race where the marketplace pulls the new plugin version before the release workflow has finished uploading binary artifacts. `releases/latest/...` is the floating-tag fallback, paired with a separately-maintained `snapshot` prerelease tag for dev builds. Constraint: dev/release version distinction is encoded in version-string suffix matching (e.g., `version.includes("-dev.")`) — three-state logic (release/dev/unknown) inside the wrapper.

### Hook-driven WASM payload

`SessionStart` hook downloads a raw WebAssembly binary plus its JS wrapper from GitHub Releases on a separate repo, installing into `${CLAUDE_PLUGIN_DATA}` with a hardcoded `$HOME/.config/<plugin>` fallback. No package manager — release artifacts substitute for npm/PyPI. The MCP server consumes the WASM via `WebAssembly.Module` + `initSync({ module })` at startup. Pattern: release-as-CDN, where GitHub Releases acts as a binary distribution channel without a package manager mediating. Constrains the plugin's release cadence to the engine repo's release cadence — engine release must precede plugin install success, and version pinning is exact-match (any inequality re-downloads all files).

### Lazy-download from project's own releases

Bin shims trigger a one-shot installer that hits the project's GitHub releases API (unauthenticated), filters tags client-side, picks a release, downloads platform-appropriate tarball/zip, extracts to `${CLAUDE_PLUGIN_DATA}/bin/`, writes a version stamp. Existence-only change detection: short-circuits if both binaries exist regardless of version. `mktemp`-based staging with `trap` cleanup so failed downloads leave the target dir untouched. No SessionStart hook involved — install fires on first invocation of the bin shim. Trade-off: zero session-start overhead but the first call pays the download time.

### Browser-bundle install alongside node_modules

Browser-capture plugins place `node_modules` plus a Chromium download (~170 MB) under `${CLAUDE_PLUGIN_DATA}` via `PLAYWRIGHT_BROWSERS_PATH=<data>`. One-time download skipped on subsequent sessions when the staleness check passes. Verifies by launching a headless instance and closing it before declaring success — catches broken downloads that pure file-existence would miss.

### External CLI auto-install via vendor scripts

System-level CLIs (e.g. `agent-device`, `maestro-runner`, `ffmpeg`) are installed during SessionStart by a family of `ensure-*.sh` scripts, each targeting one tool with its preferred install mechanism — `npm install -g` for npm globals, `curl -fsSL <url> | bash` (vendor install scripts) for standalone binaries, with `brew install` printed as a manual fallback when auto-install fails. Some scripts use `set -euo pipefail` for strict failure; others omit it to allow graceful fallback to local install. Lands tools wherever the installer puts them (`~/.maestro-runner/bin/`, npm global prefix), outside the plugin's own data directory.

### Pre-plugin-era installer outside plugin tree

Pre-plugin-era installer writes its bin directory to `~/.claude/bin/` regardless of which plugin invoked the install, plus appends that path to user shell rc files via auto-detection (`bashrc`, `zshrc`). Cuts against the plugin-era convention of containing artifacts under `${CLAUDE_PLUGIN_ROOT}` and lets the binary outlive plugin uninstall. Visible as an artifact of installers that predate the plugin model.

### Hard-coded versions in install script

`scripts/setup.sh` downloads or compiles binaries with versions hardcoded in the script itself (`HELLWAL_VERSION="1.0.7"`). No declarative manifest, no update mechanism — users get whatever was pinned at the commit time of the setup script. Hooks reference `${CLAUDE_PLUGIN_ROOT}/bin/<binary>` directly (no PATH discovery). Linux/x86_64 hardcoded — porting to other platforms requires script edits.

### Manual install script (no host-driven install)

A standalone `install.py` (or equivalent) at repo root, invoked manually by the user with verbs (`--platform`, `--uninstall`, `--verify`, `--add-to-path`). Not tied to any hook lifecycle. Idempotent through full-wipe + re-create rather than diff. Appropriate when the plugin must wire itself up to multiple host CLIs (Claude Code, Copilot CLI, Codex CLI) where each has its own install convention — the manual script can detect host presence and stage files into the right places.

### One-time interactive setup with OS credential store

User runs `python setup.py` once; the script stores secrets (API keys) in macOS Keychain / Linux Secret Service / Windows Credential Manager. No package install — runtime scripts use stdlib only. Distinct posture: "no deps to install" is the alternative. Cross-agent credential sharing is the explicit motivation — the credential lives in OS-wide storage, not per-plugin or per-session. Pairs with a SessionStart hook that probes for credential presence and nudges the user to run setup if absent.

### npm CLI as the sole install surface

The plugin form has no installer; the project's npm package (`package.json.bin.<name>`) carries an `install.sh` that wraps `npx -y <package> init` to copy hooks/skills into the user's `.claude/`. The plugin form is then self-sufficient because everything is markdown + bash with no runtime deps. Used when the same project ships as both a plugin and an npm CLI, with the CLI doing one-time install work the plugin form doesn't need.

### Pre-built npm package as runtime

The plugin is itself an npm package; users install it through npm (transitively via the marketplace's `source: npm` binding), and the plugin manifest's commands invoke `npx <name>` against the installed package. No SessionStart install hook is needed because npm did the work. Constrains the entire plugin to npm's distribution model. Appropriate when the codebase is large (40+ runtime deps including native modules like `better-sqlite3`) and the plugin is one of many consumer surfaces over the same package.

### No managed install (user prerequisite)

README states "Requirements: Python with scipy and numpy" or similar; plugin ships a script that imports the deps and crashes with `ImportError` if they're missing. No `requirements.txt`, no plugin-managed venv, no SessionStart install hook. User-side prerequisite is the entire install story.

### Ownership-based install location split

Third-party MCPs install to a shared user-home directory (`${HOME}/.<framework>/mcp/`) — amortizes download across plugin versions, decouples lifecycle from plugin updates. First-party bundled MCPs ship inside `${CLAUDE_PLUGIN_ROOT}/mcp/<name>/dist/` with their dependencies installed to `${CLAUDE_PLUGIN_DATA}/<name>/node_modules/` at first session start, wired together via `NODE_PATH` in `.mcp.json`. The axis is "we own the code" vs. "someone else does"; the install-location mechanic follows ownership rather than runtime.

### Plugin-upgrade awareness via tmp-file stamp

A separate stamp at `$TMPDIR/<plugin>-last-version` records the plugin's own version, compared next session to detect plugin-level upgrades (vs. dep-level). On mismatch, emits a notice ("plugin upgraded from vX to vY; restart Claude Code to reinitialize MCP servers") to surface the MCP-subprocess-doesn't-auto-restart class of bug. `$TMPDIR` resets on macOS reboot, so the stamp survives a boot cycle but not a restart — accepted trade-off.

### Persistence contract — `${CLAUDE_PLUGIN_DATA}` as install destination

Across managed-install plugins, `${CLAUDE_PLUGIN_DATA}` is the install target — `node_modules/`, version stamps, sentinels, and any persistent cache live here. `${CLAUDE_PLUGIN_ROOT}` is treated as cache (wiped on plugin update) and not used for state. Contributor docs warn explicitly against the inversion: "Using `${CLAUDE_PLUGIN_ROOT}` for persistent state — WRONG, it's the cache dir that gets wiped on plugin update."

### Coexisting redundant install paths

Multiple install scripts in tree (SessionStart hook + bootstrap.py + install-deps.sh) where only one is wired to lifecycle events; the rest are dormant rejected-state alternatives kept for reference. A reader has to trace `hooks.json` and `.mcp.json` to know which is live. Drift-prone — the dormant scripts can fall behind the live one without anyone noticing. Higher-risk variant: each redundant path uses a *different* change-detection mechanism (`auto_install.py` checks `import` existence, `bootstrap.py` does `diff -q` against a marker, `install-deps.sh` uses bash `set -e` plus copy-after-success). When the redundant paths each carry distinct invariants, a reader picking the wrong one for reference will copy the wrong invariant — naming the duplication is insufficient; the per-path-invariant divergence is the load-bearing hazard.

### No deps (pure manifest aggregator)

Repo ships only `marketplace.json` + LICENSE + README + a single CI workflow; nothing to install. Appropriate for pure aggregators.

## Install change detection

How the install path decides "is the cached state up to date?" — what the gate compares against and what triggers re-install.

### Plugin-version stamp file

A single text file (e.g. `${CLAUDE_PLUGIN_DATA}/installed-version`, `${INSTALL_DIR}/.version`, or `${XDG_CACHE_HOME}/<plugin>/verified-version`) carries the last-installed `plugin.json.version` string. On each lifecycle hit, the script reads `plugin.json.version`, compares to the stamp, and skips on match. Idempotent — every `SessionStart` re-runs the script but does no work in the steady state. The committed-version file is written only on full success, so a partial failure leaves the stamp absent and the next session retries; cleanup of partial tmp files on failure preserves the retry invariant. Makes `plugin.json.version` double-duty: user-facing semver AND install-staleness signal. The trade-off is that a no-op version bump (e.g. README-only) triggers a full reinstall, which most authors accept as cheap insurance.

### Two-tier version cache (file + binary self-report)

Fast path: a cache file holds the last verified version; if the file exists and matches `plugin.json.version`, skip. Cold path: cache miss invokes `<binary> version` (a process exec costing ~tens-of-ms) and compares to `plugin.json`; mismatch triggers `install.sh --force`. Appropriate when the binary is the source of truth for what's actually deployed and the file is just a launch-cost optimization; the structure makes sense when the binary itself is downloaded (not built) and the cache could be wiped without losing correctness.

### Diff-based byte comparison of manifest

`SessionStart` script byte-compares (`diff -q`) a committed `package.json`/`requirements.txt` against a cached copy in `${CLAUDE_PLUGIN_DATA}/...`, and runs `npm install` / `pip install` only when they differ. On install failure, removes the cached copy so the next session retries; never hard-fails the hook. Diff-based change detection means repeated runs converge without redoing work. May double-check with `[ -d "${ROOT}/node_modules/<probe-pkg>" ]` so an external `node_modules` wipe forces reinstall even with intact sentinel. Pitfall: works only for diffable manifests; misses semantic equivalence (e.g., reordered keys produce a false-positive reinstall). Variant: byte-for-byte content equality — reads `${CLAUDE_PLUGIN_ROOT}/package.json` and `${CLAUDE_PLUGIN_DATA}/package.json` and compares full string contents. Pitfall in copy-then-install ordering: the manifest is copied to the data dir BEFORE `npm install` runs there, so a failed install leaves a "fresh" copy that makes the next equality check pass and masks the failure.

### Source-content hash via cross-platform md5

Concatenate dep manifest plus glob of source files; pipe through `md5 -q` (BSD) → `md5sum | cut` (GNU) → literal `"none"` fallback. Stored in the venv directory; compared each session. Recomputes deterministically across edits to any included file. Constraint: the `"none"` fallback can pin install state on a minimal system. The marker is interpreter-version-blind — a system Python upgrade isn't detected.

### Hash over source plus manifest (sha256)

A sha256 hash is computed over the plugin's Python source files, manifest, and (sometimes) markdown — the union representing "anything that would change what `pip install .` produces". The hash is stored in `${CLAUDE_PLUGIN_DATA}/.deps-hash` and compared on every SessionStart. Mismatch triggers `--force-reinstall`. Appropriate when the plugin installs itself from source via `pip install .` — the installed package is not just the manifest, so manifest-only hashing misses source changes. Trade-off: editing README invalidates the hash and forces a venv reinstall (over-eager invalidation). Hash is computed via `find ... | sort | xargs cat | shasum -a 256` to stabilize across filesystems with non-deterministic `find` ordering.

### sha256 of manifest + post-verify marker

Hash of the bundled `package.json` is compared against a hash of the cached copy in `${CLAUDE_PLUGIN_DATA}`. AND an `.install-ok` marker file must exist; the marker is deleted before install starts and only rewritten after a verification step (e.g. headless browser launch) succeeds. Marker JSON also records `{version, hash, timestamp, node, platform}` for forensics. A partial install (manifest copied but install crashed) leaves the cached manifest matching but the marker missing — next session retries cleanly.

### Three-pronged OR (path drift + manifest diff + venv health)

Three independent checks evaluated with `elif` short-circuit: (a) cached `${CLAUDE_PLUGIN_ROOT}` path file content differs from current value (detects plugin-cache directory move on Claude Code update), (b) `diff -q` against a cached copy of `pyproject.toml` (detects manifest change), (c) `${VENV_DIR}/bin/python` is missing or non-executable (detects broken venv). Any one trigger forces reinstall. Appropriate when plugin-directory relocation is a real failure mode. Trade-off: install reason isn't logged because the flag is set without echoing which trigger fired; cached files are written only after pip success, so a failed install leaves stale cache content and the next session naturally retries via the manifest-diff trigger.

### Existence-only check

`if [ -f "${BINARY_PATH}" ]; then exit 0` or `[ ! -f "$VENV_PY" ]`. Once the artifact is present, the install hook never replaces it. Upgrades require manual cache wipe — the install path is not idempotent across version changes, only across no-change re-invocations. Pairs uneasily with `/plugin update`, which does not clear the binary, so users hit a documented troubleshooting path. Appropriate for tiny stable dep sets. Constrains: misses upgrades — if the plugin later requires a higher version, the existence check passes silently and the new requirement surfaces as a runtime ImportError or AttributeError far from the install hook. Hybrid form: existence-plus-importability ("file exists" plus `python -c 'import <pkg>'` succeeds) is still upgrade-blind because importability doesn't carry version semantics — no declared version floor anywhere means a 0.2.0 install satisfies a 0.3.5-required feature surface.

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

### Out-of-band user check

User runs `ls node_modules/<pkg>` to verify install. No automated detection at all. Failures surface as runtime import errors when hooks fire.

### Full-wipe (no detection)

The install script always deletes its target dir and rebuilds (`reset_directory()`). No staleness detection — every install is a fresh install. Appropriate for adapter-style plugins that wire into multiple host CLIs where each install is rare (manual user invocation) and partial state is more dangerous than redundant work.

### No change detection

Marketplace entry `version` is bumped manually as a cache-bust signal so consumer `/plugin update` refetches the whole plugin tree. The "change detection" lives in the marketplace consumer, not in the plugin itself — there's no install-time hook that compares manifests or hashes.

## Install trigger and lifecycle

When the install script fires — SessionStart, lazy on first invocation, manual user, or self-healing at MCP launch.

### SessionStart direct invocation

Plugin registers a `SessionStart` hook that runs the installer script synchronously (or via `child_process.spawn`) on every session start, with the change-detection layer short-circuiting fast on no-op. Timeout budget (e.g. `"timeout": 300`) bounds the worst-case install. Pitfall: aggregate internal timeouts of the install pipeline (npm + browser download) can exceed the hook timeout on cold first-run.

### Sanity-check-gated indirect invocation

`SessionStart` hook calls a generic sanity-check function (`runSanityCheck({ fix: true })`) that owns ~17 invariants of which deps are two; the sanity routine spawns the install detached + unref'd when its `node_modules`/manifest checks fail. Same code path is reachable via a manual `/sanity` skill invocation. Decouples "install dependency" from "this plugin starts up" by treating it as just another self-healing invariant. Pitfall: detached fire-and-forget means the hook returns before install finishes; MCP server startup races against `node_modules` materialization.

### Lazy bootstrap on first hook (no SessionStart)

No SessionStart hook at all. Whatever bootstrap work is needed (binary download, cache priming) happens on the first non-SessionStart hook of the session. The author's stated rationale (in one sample) is that Claude Code plugins historically lacked post-install hooks, so lazy-on-every-hook is the most robust pattern; even after SessionStart became available, lazy-at-every-hook self-heals through mid-session plugin upgrades that SessionStart-only would miss. Appropriate when the bootstrap cost is small and the wrapper-per-hook overhead is acceptable.

### User-invoked one-shot installer

Install is not a hook at all — user runs `npx github:<owner>/<repo>` or `bash setup.sh` manually. The installer is a CLI app that handles tarball download, interactive multiselect, copy operations, and merging into `~/.claude/settings.json`. Plugin install via `/plugin marketplace add` is the secondary channel that gets a smaller subset.

### Skill preamble lazy build

Skill preamble (the bash block at the top of a SKILL.md) runs an `update-check.js` and a `build.js` lazily on first skill use, separate from any hook. Defers heavy work (esbuild bundling) from session start to skill activation. Pitfall: the lazy builder mutates `package.json` in the data dir to add esbuild, which then defeats the sha256 staleness check the SessionStart installer relies on — observed bug from the interaction of two install paths managing the same manifest.

### Mkdir-based atomic install lock

`bin/.<name>-download.lock/pid` directory created via `mkdir` for atomicity (mkdir is atomic on POSIX); 60-second timeout with forced-remove fallback for stale locks from crashed processes. Used to serialize concurrent install attempts (SessionStart hook + bin-wrapper both calling the downloader). Constraint: a fast SessionStart after a crash blocks up to a minute before forcing the lock.

## Install failure posture

What happens when install fails mid-way, and how that failure is signaled.

### `rm` stamp on failure (retry next session)

The install script wraps install + stamp-write in a single try/except; on any exception it deletes the stamp file and re-raises. Result: a half-installed venv is not remembered as "done"; next SessionStart sees the missing stamp and retries. Exception propagates to non-zero exit so the host surfaces failure. Appropriate when the host gracefully reports failure to the user and partial state is detectable from stamp absence.

### Implicit retry via late-write cache marker

`set -euo pipefail` halts on any failing command. No explicit `rm` of partial state. The change-detection cache (hash file or cached manifest copy) is written only after pip install succeeds, so a failure leaves the old cache content intact — the next session's change-detection check naturally re-fires the install branch. This amounts to retry without explicit cleanup. Trade-off: a partially-created venv may persist on disk; if the venv's `python` binary happens to be present, the venv-existence trigger short-circuits past the actual broken state, which is why manifest/hash drift triggers are critical to the recovery story.

### Pre-delete the marker so failure is structurally visible

`.install-ok` marker is deleted before any install work begins and only rewritten after end-to-end verification (e.g. headless browser launch) succeeds. A crashed install leaves the cached manifest in place but the marker absent; the next-session check sees marker missing and retries from a clean state. The failure branch in the outer try/catch also wipes the cached manifest for redundant safety. Strongest atomicity posture observed.

### Self-healing via marker cleanup

On any failure branch the script `rm -f` the cached manifest and ABI marker, then `exit 0`. Next SessionStart sees no cached state and retries from scratch. Constrains the script to never persist partial state — every write must be paired with cleanup-on-failure.

### Silent fail-open (`exit 0` always, retry every hook)

Install script and wrapper use `|| true` on every side effect and `exit 0` unconditionally. Failure leaves the binary missing; the wrapper's `binary_ok` check returns false at the end and the wrapper exits silently (Claude never sees the error). Next hook fires → same check cycle retries. The wrapper's top comment makes the trade-off explicit: never block the user, even at the cost of broken installs being invisible. Appropriate when the plugin's behavior is observational (notifications, logging) rather than gating; the cost is users with persistently-broken installs see "no notifications" and may not know why.

### `set -euo pipefail` + `trap 'exit 0' ERR` — non-blocking with cleanup

Strict-on-failure inside the script body, but a top-level ERR trap converts any unhandled failure to `exit 0`. npm/pip output piped through `2>&1 | head -50 >&2` so only the first 50 lines reach the terminal and nothing leaks to stdout (hook JSON contract). Always exits 0; never blocks the tool. Failure path explicitly cleans up partial state (`rm -rf node_modules; rm -f $SENTINEL`) so next session retries clean.

### Strict-on-failure with typed errors and colored stderr

`set -euo pipefail` plus a `{ ... }` download-guard block (specifically defending against partial-execution under `curl | bash`). Throws typed errors (e.g., `err.pluginPaths` when both plugin and CLI install forms coexist) and streams colored stderr guidance. Used in user-invoked install scripts where a hard error is the right outcome.

### `[OK]/[WARN]/[FAIL]` print + non-zero exit

Manual install script prints prefixed status lines to stdout and exits 0 on success / 1 on failure. The user sees outcomes directly because they invoked the script themselves. Appropriate for user-driven install paths where exit codes feed the user's shell rather than a hook lifecycle.

### Human-readable stderr plus exit 1

`set -euo pipefail` plus prefixed stderr lines (e.g., `[plugin-name] ERROR: …`) plus `exit 1` on failure. Success path prints a single confirmation line to stdout. No JSON `systemMessage`, no `continue: false`, no structured hook output. Corrective hints embedded in error text (e.g., "delete `${INSTALL_DIR}` and restart your session"). Sufficient for users who watch the session start; opaque to agents that don't parse stderr.

### Multi-layer fail-open with stderr advisory

Installer writes human-readable `[plugin-name] <message>` lines to stderr with corrective install commands ("install build-essential" / "install Visual Studio Build Tools"). Top-level catch swallows errors so session start never fails. Hook output is a JSON `hookSpecificOutput.additionalContext` warning prefixed with a glyph (`⚠`) that tells the user to run `/sanity` or similar. No `continue: false`, no exit-2 — the model gets degraded context but the session lives.

### Set -e bash with stderr exit-1

Bash installer uses `set -euo pipefail`; first failed step terminates with stderr message and exit 1. Caller (Node CLI) rejects its install promise with `install script failed (exit ${code})`. Top-level `.catch` writes `ERROR: <msg>` to stderr and `process.exit(1)` — user-facing CLI output, not hook JSON.

### Postinstall failure suppression

`package.json` `postinstall` and `prepare` scripts wrap their commands with `|| true` (or `>/dev/null 2>&1 || true`). A crashed install-time banner or hooks-installer never fails `npm install`. Constrains user-visible install reliability; means install-time bugs are hidden until the runtime fires.

### Silent fail-through

Every install invocation is `>/dev/null 2>&1` and ends with `|| true`. Failures are invisible in the hook; the dep-consuming skill or tool surfaces the failure later via ImportError. Appropriate when the install-hook author would rather skill-level errors carry the diagnostic; constrains: users see a confusing downstream error with no signal pointing at the install hook as the actual failure site.

### No retry path

Install runs once; on failure the venv may exist with a half-installed package set, and the existence-only change detector skips the reinstall on subsequent sessions. Recovery only via manual venv removal. Constrains the install logic to be all-or-nothing within a single hook execution.

### Silent failure (no install hook at all)

Hook is absent or no-ops; the install never runs. Failure surfaces only when the missing dependency is needed at runtime (e.g., `Cannot use import statement outside a module` from a hook with no `node_modules`). Documented as a troubleshooting path the user must follow manually. Trades discoverability for zero install-machinery cost.

## User configuration and authentication

How the plugin lets a user customize its behavior and supply credentials — declared `userConfig`, env vars, custom config files, OS credential stores, markdown blocks, vault files, or external CLI delegation.

### No userConfig, env-var only

`plugin.json` declares no `userConfig`. Configuration is read from shell environment variables (`<PLUGIN>_CACHE_DIR`, `EFFORT_LEVEL`, `ANTHROPIC_API_KEY`, `OUTLINE_API_KEY`, `LANCEDB_PATH`, etc.) by the plugin's own helper at runtime, OR via `os.environ.get` for the MCP-server case where `.mcp.json` declares passthroughs via shell-style `${VAR:-default}` or bare `${VAR_NAME}` for bearer tokens. SKILL.md documents which env vars are required. Knobs that exist (e.g., service API keys for a paid tier) are read from process env outside the plugin manifest. Sidesteps the schema but loses Claude Code's `sensitive: true` flag and built-in CLI-driven UX for the secret fields. Discoverability gap — the user must read `.mcp.json` (or README) to learn what variables the plugin expects. Appropriate when the only configurable surface is secrets that should not pass through plugin config; for required secrets a missed-opportunity pattern — `userConfig` with `sensitive: true` is the idiomatic surface.

### Native `userConfig` with `${user_config.KEY}` substitution

`plugin.json` declares fields under `userConfig` with `description`, `sensitive: true|false`, optional `type`, `default`, `enum`, etc. `.mcp.json`'s `env` block uses `${user_config.KEY}` substitution to translate user config into `CLAUDE_PLUGIN_OPTION_<KEY>` env vars consumed by the MCP server via `os.environ.get(...)`. Round-trip is observable: Claude Code prompts for the values at install time, stores them, substitutes into the env block, server reads them. Multiple variants observed:

- *Two-form referencing* — `.mcp.json` references each value twice per server entry — once via `${user_config.KEY}` substitution into config strings and once as a `CLAUDE_PLUGIN_OPTION_KEY` env var that hook scripts read directly with `$CLAUDE_PLUGIN_OPTION_KEY`.
- *Sensitive flagging* — `sensitive: true` flags genuine secrets (API keys); `sensitive: false` correctly applied to identifiers that are public rate-limit handles (e.g. an Unpaywall email).
- *Cross-ecosystem duplication* — Cross-ecosystem deployments may duplicate the `userConfig` block verbatim into the Cursor manifest with no sync mechanism — drift risk identical to the version-string problem.

Common defect: `userConfig` declared in tests + docs, but live `plugin.json` omits it — every substitution resolves empty and the runtime starts with empty credentials. The substituted values reach the runtime via `CLAUDE_PLUGIN_OPTION_<KEY>` environment variables Claude Code sets when invoking hooks. Schema richness varies — `title`/`description` always present; `default`, `enum`, `sensitive` optional and frequently omitted (enum values may appear only in prose descriptions, leaving install-time validation gap). The `type` and `title` fields are load-bearing — current manifest-validator schema rejects entries that omit them, breaking installs reactively until the user-config block is updated.

### Typed `userConfig` schema with rich field types

Top-level `userConfig` object declares typed fields (`type` (`number`/`boolean`/`string`/`directory`), `title`, `default`, `description`, `enum`, `required`, `sensitive: true`); Claude Code surfaces these in the install/configure UI. Descriptions can be substantive (multi-sentence, with links to upstream documentation explaining the default). Numeric/boolean fields declare defaults; the secret field carries the description "stored securely in keychain". Aligns with Claude Code's secure-storage UX. The `directory` type is a typed variant beyond bare strings. A recurring pattern: remote MCP servers receive bearer tokens by injecting `${user_config.<key>}` into `headers.Authorization` with the key marked `sensitive: true` — substitution flows from keychain → manifest → outbound HTTP header without disk persistence. Manifest-level substitution via `${user_config.<KEY>}` in `.mcp.json` env blocks or hook commands is a separate concern — declaring fields and wiring them are independent steps. Appropriate for a small bootstrap surface (≤5 fields) with a deeper config schema mutated out-of-band by the plugin's CLI.

### userConfig as typed schema with stringly-typed values

The plugin declares 15-18 `userConfig` fields per plugin (in a multi-plugin repo). Every field has `type: "string"` and a default value (`""` or a concrete string). Numeric-looking values (`MAX_ORDER_USDC: "100"`, `KELLY_FRACTION: "0.25"`) are stringly-typed and parsed downstream. No enums, no numeric or boolean types. Reference into other manifests via `${user_config.<KEY>}` substitution.

### `userConfig` declared but not wired through manifest substitution

Fields declared (with `sensitive: true` etc.) but no `${user_config.<KEY>}` references in `.mcp.json` env block or hook commands. The runtime reads credentials from a chain of fallbacks (userConfig → env var → on-disk config file at `~/.<plugin>/config.json`). Documented in README but not enforced in the manifest — if the runtime code path that queries userConfig is absent or stale, the userConfig surface is a no-op. Claude Code translates user config into env vars implicitly for MCP subprocesses. Works in practice (the implicit translation is part of the plugin protocol) but a consumer expecting explicit substitution will be surprised. Sub-cases: **declared-but-unused** — a field is declared for an out-of-band consumer (e.g., `ANTHROPIC_API_KEY` documented as "only for GitHub Actions cron, not for plugin use"), creating a structural inversion where the userConfig surface points at a non-plugin consumer. **Declared-but-partially-wired** — the SessionStart hook bridges most declared fields into env but omits a subset; the omitted fields are invisible to the plugin runtime even though they appear in the install-time prompt. **Cross-ecosystem duplication** — the userConfig block is duplicated verbatim into a sibling Cursor / Codex manifest with no sync mechanism, drift risk identical to version-string drift.

### Schema richness — minimal vs. validated

When `userConfig` IS declared, the schema is typically thin — `description` and (sometimes) `sensitive` only, no `type`, `default`, enum, or validation pattern. Validation is deferred to runtime: the server raises a runtime error at first tool invocation when a required field is unset (`if not email: raise ValueError(...)`). A user who skips the prompt gets a deep runtime error rather than an install-time failure. No validation that the configured value matches its semantic shape (an email field accepts any non-empty string).

### `sensitive: true` flag absent on secret fields

Across one userConfig-using plugin, every secret-class field (private keys, API secrets, webhook secrets) lacks the `sensitive: true` flag despite descriptions explicitly labelling them "SECRET — treat like a password." Seven of seven secret fields lack the flag; the documented mechanism for routing to OS keychain storage is consistently skipped. Repeated three times across three plugins in the same repo — systematic authoring gap rather than a one-off.

### Env-var fallback alongside userConfig

For hosts (older Claude Code versions) that don't support `userConfig`, the plugin reads plain env vars (`<PLUGIN>_<KEY>`) as a documented fallback. The runtime checks both the userConfig-populated env var and the plain-env name. Constrains the plugin to maintain two env-var conventions but extends host coverage. Appropriate when backwards-compat with a wider host set matters.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

Hooks read userConfig values through Claude Code's `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (e.g., `CLAUDE_PLUGIN_OPTION_agent_hooks` for early-exit on a boolean toggle). No `${user_config.KEY}` token substitution in hook commands — values flow through env vars instead. Coexists with a parallel project-level YAML config file (`.craft-config.yml`); SessionStart warns when the two surfaces diverge, but neither is canonical.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var forwarding / re-export

A SessionStart hook reads `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (the substitution channel for `userConfig` values) and re-exports them under plugin-specific names (e.g., `FLIPPER_<KEY>`). Decouples manifest-key naming from the daemon's env-var contract; either side can evolve independently. Variant: SessionStart hook reads `CLAUDE_PLUGIN_OPTION_<KEY>` env vars and writes `export KEY="${CLAUDE_PLUGIN_OPTION_KEY}"` lines into `$CLAUDE_ENV_FILE`. This bridges Claude Code's plugin-option namespace to the conventional env-var names that a CLI library already expects (e.g., `CLAUDE_PLUGIN_OPTION_BLUESKY_HANDLE` → `BLUESKY_HANDLE`). Appropriate when the plugin is a wrapper over a pre-existing CLI that expects standard env-var names. Trade-off: duplicates the value into a file on disk (security depends on file mode of `$CLAUDE_ENV_FILE`); fields declared in `userConfig` but missed in the bridge block silently fail to propagate.

### Plugin-managed JSON file with custom CLI

`plugin.json` declares no `userConfig`. The plugin maintains its own `config/config.json` schema (richer than `userConfig` allows — webhook presets, per-status overrides, platform flags) and exposes a slash command (e.g. `/<plugin>:settings`) or a `<plugin>-config get/set/list` bin tool with an internal allowlist of legal keys to edit it. `${CLAUDE_PLUGIN_ROOT}` is referenced inside the JSON for resource paths and is expanded by the plugin's own runtime, not by Claude Code's substitution mechanism. The plugin writes a settings JSON under a plugin-chosen path (`$HOME/.<plugin>/config/settings.json`). Appropriate when the schema needs are too rich for `userConfig`; the cost is no presence in Claude Code's UI and a parallel config-edit UX for the user. Validation duplicates work the manifest schema would provide.

### External config file owned by plugin

Plugin reads its own JSON/YAML file (`root.config.json`, `.claude-code-harness.config.yaml`, `<tool>.config.json`, `.coco/config.yaml`, `.evolver.json`, `~/.config/<name>/config.toml`) from the consumer's repo or a known location. Schema is plugin-controlled, often versioned (`configVersion: 2`) with in-plugin migration logic to upgrade older versions on session start. Bypasses Claude Code's config UI entirely — config authorship is in the consumer's repo, version-controlled with the project. Appropriate when the surface is large enough that `userConfig`'s flat schema would be unwieldy or when config needs to evolve through schema migrations the plugin itself owns. Plugin uninstall does not clean up project-level config files; users must know to remove them manually.

### Layered file-based config with schema-versioned migration

Three-tier file system replaces `userConfig`. Plugin-side defaults (`<plugin>-config.default.json`) → user-side migrated copy at `${CLAUDE_PLUGIN_DATA}/<file>.json` → project-side state (`.pipeline/project.json`). Plugin-side default JSON carries a `schemaVersion` integer. SessionStart hook compares it against the live user-side copy; on mismatch performs field-level diff-merge that adds/updates plugin-owned fields (providers, models, agentMap entries) while preserving user-owned fields (`enabled`, `envVar`, user-added entries). Writes a timestamped `.bak-<ISO>.json` backup before overwriting and logs a one-line summary. Robust when config-schema evolution is a regular need; the backup preserves the pre-migration state for rollback. The migration logic ends up nearly as expressive as a `userConfig` schema would be — purpose-built for the project's specific shape.

### `.env` files in cloned repo

User edits a `.env` file (or `.env.example` template) in the cloned repo. Secrets (`ANTHROPIC_API_KEY`, DB creds, `REDIS_URL`) live outside Claude Code's plugin config surface entirely. Appropriate when the plugin backs a long-running server that needs config to persist outside any single Claude Code session. Cost: users don't benefit from Claude Code's secret-handling affordances.

### Env-var + INI-config knob pattern

No `userConfig` at all. Configuration knobs are read directly by the hooks from environment variables (`SP_NO_COMPRESS=1`, `SUPERPOWERS_AUTO_UPDATE=0|1`) and from a user-side INI file (`~/.config/superpowers/update.conf` parsed by awk). The knob surface is documented only in the README and hook source — schema-aware tooling cannot discover it.

### Env-var opt-out without `userConfig` declaration

A single boolean opt-out (e.g., `<TOOL>_NO_AUTO_INSTALL=1`) is read from the environment by a hook script, with no corresponding `userConfig` field. Documented only in the hook source comment header. Constrains discoverability — users who want the opt-out have to read the hook to find it; a `userConfig` boolean would surface it in the plugin configuration UI.

### Out-of-band env vars (no `userConfig`)

No `userConfig` in `plugin.json`. Configuration via a documented set of env vars (`AIDE_DEBUG`, `AIDE_FORCE_INIT`, etc.) plus a few hardcoded values in the manifest's `mcpServers.env` block. Users discover the knobs only by reading the README; Claude Code's marketplace UX has no way to surface them.

### Env var read by script (hidden interface)

A plugin script (not `userConfig`) reads an env var like `CLAUDE_SKILLS_DIR` to relocate behavior. Appropriate for testability hooks the plugin author wants but doesn't want to expose as user config; constrains: the env var is a hidden interface — consumers won't find it without reading source.

### MCP-registry-schema sidecar

`server.json` (the modelcontextprotocol/registry schema) declares `OUTLINE_API_KEY` with `isSecret: true` — the MCP-registry equivalent of `sensitive: true`. The same plugin's `plugin.json` has no `userConfig`. The two registries each demand their own config-schema dialect, and the author honors the MCP one but not the Claude Code one. Demonstrates that "no `userConfig`" can mean "we use a different registry's secret-marking" rather than "we don't acknowledge secrets exist."

### Gitignored `.local.md` convention

A plugin ships an `<name>.local.md.example` template; the user copies it to `<name>.local.md` (gitignored) and edits values. Skills read the file at runtime via prose instructions, not a harness substitution mechanism. User-facing configuration as a file convention layered atop markdown — works without harness involvement, lacks any schema enforcement.

### External schema in admin-run script

Configuration is collected by a user-side script the admin runs out-of-band (`build-manifest.mjs`) that hand-rolls a `KEYS` object with regex patterns, hints, and `secret: true` flags, then emits a downstream config artifact. Plugin metadata layer is bypassed entirely; the plugin ships *tooling for the admin* rather than being configured itself. Recreates `userConfig` semantics outside the manifest.

### Markdown block in consumer's CLAUDE.md

Plugin parses a `## Session Config` block from the consumer repo's `CLAUDE.md` or `AGENTS.md`, extracting fields (`test-command`, `typecheck-command`, `lint-command`, `enforcement`, `agents-per-wave`, `waves`, `allow-destructive-ops`, etc.). Validated against a homegrown JSON-Schema (`config-schema.mjs`); a bypass env var (`SO_SKIP_CONFIG_VALIDATION=1`) lets users opt out for emergencies. The plugin re-implements parser + validator rather than using the platform's `userConfig` mechanism. Constrains config to a markdown surface users already maintain, enabling per-project config without Claude-Code-side plumbing, at the cost of a parallel parser the plugin must keep aligned with the schema.

### Per-mission flags (no install-time config)

Configuration passes as CLI flags to the plugin's own CLI verb (e.g. `<cli> init --objective ... --allowed-path ...`) for each invocation. No persistent install-time config exists. Appropriate when the configurable surface is mission-scoped rather than session-scoped.

### OS-level secret storage

`plugin.json` declares no `userConfig`. Secrets live in OS credential store (Keychain / Secret Service / Credential Manager), accessed by Python at runtime. Justification: cross-agent sharing — the key is stored once and shared across all agents on the machine. A `userConfig` field with `sensitive: true` would fragment storage per-agent. Trade-off: users don't get install-time config-prompt UX; configuration happens via a one-time interactive wizard.

### Encrypted vault file with passphrase env-var

A vault file on disk holds Fernet-encrypted credentials, with the passphrase supplied via `userConfig` env var (`CLAUDE_PLUGIN_OPTION_PPC_VAULT_PASSPHRASE`); PBKDF2-HMAC-SHA256 with 100000 iterations derives the key. File-locking governs writes; in-memory cache per MCP-server-process. Appropriate for plugins juggling many third-party API tokens (e.g., Google Ads, Meta Ads). Constrains: passphrase loss = vault loss; `userConfig` field must actually ship in `plugin.json`.

### Home-directory KEY=VALUE file

The native binary reads `~/.config/<plugin>/config` directly (KEY=VALUE lines, optional `export` prefix, no shell expansion). Plugin declares no `userConfig` in `plugin.json`. Decouples config lifetime from plugin cache churn — config survives uninstall/reinstall — but sacrifices Claude-Code-side discoverability and validation. Priority chain documented as `CLI flag > env var > config file > default`. Constrains the plugin to handle config parsing and schema enforcement entirely in its own runtime code.

### Vendor-CLI credential file

Plugin secrets (e.g., `LANGSMITH_API_KEY`) are stored in a third-party CLI's credential store (`~/.config/<vendor-cli>/credentials` or platform-specific equivalent), loaded by the SessionStart hook, and exported into `$CLAUDE_ENV_FILE`. Appropriate when the plugin wraps a vendor CLI that already manages credentials; constrains the plugin to a hard dependency on the vendor CLI's credential-file format remaining stable, and bypasses Claude Code's plugin-config UI entirely (users configure via `<vendor-cli> auth`).

### OAuth client embedded in MCP config

`.mcp.json` carries an `oauth` subfield with `clientId` and `callbackPort`, embedding OAuth client binding directly in the MCP server definition. Likely a Claude Code extension to the standard MCP server schema.

### Delegated to external CLI

The plugin assumes a sibling tool (e.g., `gh auth login`) handles authentication. Plugin README explicitly defers; no auth surface inside the plugin. Suits plugins that wrap an existing authenticated CLI.

### Delegated to MCP server's own login

For remote HTTP MCPs, the README tells users they will "authenticate through the server's web interface when prompted" at first connect. The plugin carries no credential plumbing; the MCP endpoint handles its own auth flow.

### Custom env-var substitution in hooks.json or .mcp.json

Hook command strings or `.mcp.json` field values reference non-platform variables like `${SKILL_PATH}`, `${ZOOM_MCP_ACCESS_TOKEN}` etc. that the plugin expects its own runtime or the user's process environment to populate. In hooks.json, if Claude Code does not populate the variable, the command dereferences an empty string and the surrounding guard (`[ -f .sparv/state.yaml ] && ${SKILL_PATH}/scripts/...`) silently no-ops — fail-open hides missing-env misconfiguration. The same substitution surface also appears inside `.mcp.json` header values (e.g., `Authorization: "Bearer ${ZOOM_MCP_ACCESS_TOKEN}"` for remote MCPs), with README telling users to `export` the variables before launch — process-environment pattern with no `userConfig` surface and no manifest-level wiring.

### Hard-coded path as missing userConfig

In one sample the plugin's primary user-configurable surface — the path to the user's Obsidian vault — is hard-coded in the README as `~/ObsidianVault/03-Resources/` and enforced by the skill's directory walk. This is what a `userConfig` field would naturally hold; instead it's a prose convention. Demonstrates the absent-userConfig path's failure mode when a real config surface exists.

### Settings.json env-field workaround

In-code comment: "Plugin settings.json env field is NOT supported by CC (only 'agent' key works)." A SessionStart hook writes the required env var (e.g. `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) directly into `~/.claude/settings.json` as a workaround. Concrete data point on a documented-but-actually-broken plugin capability. Fragile because it modifies user-scope settings the user may have customized; appropriate only when the env var is plugin-essential and has no other delivery channel.

### Per-rule inline suppression

`<plugin>-ignore: <RULE_ID>` comments inside source files disable specific rules on that line or file. Multi-rule form `<plugin>-ignore: PHP001, TS001, LAYER001` supported. Helpers `line_has_ignore` and `file_has_ignore` in the rule engine. Metrics record both "blocked violations" and "ignored violations" — partial suppression is first-class, not a workaround.

### Inline file-mode modifier comments

Source-file comments declare the active stack/layer for the ruleset (e.g., `<plugin>-stack: symfony`), enabling per-file rule tuning without external configuration. Same channel as inline suppression.

### No user-supplied config

The plugin takes all inputs via conversational flow or file-path arguments to the CLI. No `userConfig`, no settings file, no env vars. Appropriate when the plugin is fully driven by per-invocation arguments and has no per-user secrets or preferences.

## Session context loading

How and when the plugin contributes to the model's context — at session boundaries (`SessionStart`), per-prompt (`UserPromptSubmit`), via skill invocation, on compact, or as out-of-band file writes.

### Dependency install only (no context emission)

SessionStart fires `ensure-deps.py` (or equivalent), which idempotently installs Python deps if the version stamp doesn't match. No matcher set, so it fires on all sub-events (`startup`, `resume`, `clear`, `compact`) — wasted work on no-op paths is accepted as cheap. `statusMessage: "<plugin>: Installing dependencies..."` is surfaced during exec; `{"systemMessage": "..."}` JSON on stdout reports completion to the host. No `additionalContext` emission. Output is `systemMessage` JSON only on failure or status changes. Constrains: SessionStart timeout (e.g., 180s for venv) gates session readiness — long first-session installs delay the user. Appropriate when the plugin's only lifecycle need is dep readiness or when context is request-driven, not session-startup-driven.

### `additionalContext` payload at SessionStart

Hook reads project state (e.g. mission manifest from `<git-common-dir>/<plugin>/`) and emits `hookSpecificOutput.additionalContext` JSON object containing project-detection results, available command list, worker/system status, or a slim summary plus an age warning if stale. Built with `jq -Rs .` for safe escaping. Wired to both SessionStart and UserPromptSubmit (the latter as fallback for upstream issues), with a `/tmp/<plugin>_session_${SESSION_ID}.initialized` flag file for once-per-session deduplication. Matcher `"startup|resume|clear|compact"` is the broad form — fires on all sub-events. May summarize plugin state — counts of projects/posts tracked, ready-state messages, slash-command hints — computed by grepping state files cheaply on every session start. Tight `timeout: 5` with `async: true` is sometimes used so the session does not block — context arrives late on slow disks rather than failing the session. Companion `PostCompact` hook re-injects the same context after compaction since `compact` is not a `SessionStart` sub-event. Trade-off: the recompute is tightly coupled to the exact state-file formats — a schema change would silently produce zero counts.

### `systemMessage` payload (broader rendered form)

SessionStart emits `{systemMessage: "..."}` JSON containing a multi-line profile summary (active stack, strictness, enabled rules, learning trends from prior sessions, healthcheck, command routing table). Less structured than `additionalContext` but renders verbatim in the session's system context. Used when the surface is many concise lines rather than a single rich payload. Constrains output volume to whatever Claude Code's hook-output cap allows (10,000 chars; overflow silently replaced with an opaque stub).

### SessionStart stdout as system-reminder

Hook command (Python or bash) prints a `<system-reminder>` block to stdout. Claude Code captures SessionStart stdout and treats it as an additional system message — a legacy convention pre-dating the structured `hookSpecificOutput.additionalContext` JSON channel. Multiple plugins in one marketplace can register the same pattern, each contributing rules. Appropriate for "always-on rules" the agent should see at session start. No matcher means the hook also fires on `clear` and `compact`, re-injecting the rules each time context is reset — generally desired since the cleared session has lost them. Cost considerations: 2-3 second hook timeouts are tight; on cold start with slow I/O, reading multiple markdown files and walking up for `marketplace.json` may approach the limit. No retries, no fallback. Failure posture is fail-open — `exit 0` when sources are absent rather than blocking the session.

### Provenance-decorated stdout

A wrapper script (e.g., `bin/inject-rules`) doesn't just concatenate file contents — it resolves the plugin name from `plugin.json` and the marketplace name by walking up to `.claude-plugin/marketplace.json`, then decorates each injected file's path in the emitted `<system-reminder>` block as `"<path> from plugin <name>@<marketplace>"`. Gives the agent provenance for injected rules so it can attribute and reason about which plugin's rule applies. Refines the bare stdout-cat pattern by encoding metadata the agent can use to disambiguate.

### Plain-stdout context banner

A literal `echo '🎯 Plugin v2.0.0 — …'` line in `SessionStart` pushes a banner via stdout rather than via `hookSpecificOutput.additionalContext` JSON, OR a large heredoc banner (40+ lines of prose) listing tool inventory, prerequisites, and version warnings via plain `echo`. Functions as session-start context for the user but not as structured context for the agent. Re-injected on every sub-event (`startup`, `clear`, `compact`) when no matcher restricts firing — significant context tax on long sessions. Hard-coded counts in the banner ("plugin is active with 51 MCP tools") drift from other hard-coded counts elsewhere — counts often appear in three or more places (README ("53 MCP tools"), banner ("51 MCP tools"), runtime grep of source for the actual count). Each is a derived value with no single source. Drift hazard: the banner text typically hardcodes a version that diverges from `plugin.json` over time.

### SessionStart prints plain markdown to stdout

The hook script prints plain markdown text to stdout (which Claude Code surfaces to the agent at session start) rather than using the structured JSON `additionalContext` mechanism. Content is either a first-run nag ("plugin detected but not initialized") or the contents of a session-memory file (populated by `PreCompact`) when present. Multiple plugins competing for SessionStart output produce concatenated blocks in undefined order. Trade-off: no validation against the structured-output contract; relies on Claude Code's tolerance for non-JSON SessionStart output.

### Banner-plus-additionalContext (dual surface)

Hook prints a banner to stderr (visual cue for the operator) and emits the same content via `hookSpecificOutput.additionalContext` (model-visible context injection). Documented evolution path through three generations of output mechanism ending at "stderr direct print + additionalContext for model awareness." Both surfaces because each serves a distinct audience.

### SessionStart banner with runtime probes

A SessionStart hook with matcher covering all four sub-events (`startup|resume|clear|compact`) emits a banner showing agent/command/hook counts, project name, version, etc. Implementation probes for a TUI framework (bun + Ink) at runtime, falling back to plain text when unavailable. Output goes to stdout as a printed banner, not via the structured `hookSpecificOutput.additionalContext` channel. Appropriate when the plugin wants a consistent visible-on-every-session presence; constrains performance (every session pays the probe cost) and may include intrusive defaults like auto-launching a GUI app when a config flag is set.

### SessionStart welcome banner via `systemMessage`

A `welcome.sh` runs on every SessionStart sub-event (no matcher restriction) and emits `{"systemMessage": ...}` JSON with skill counts, line-count warnings, or other lint-in-banner output. Appropriate for surfacing repo-state diagnostics to the user at session boundaries. Constrains: with no matcher, welcome banners re-emit on every `clear` and `compact`, polluting mid-session context.

### Conditional `additionalContext` for setup nudge

SessionStart hook (`check_auth.sh`) emits `additionalContext` only when a precondition fails (e.g., API key missing); when present, no context is injected. Matcher restricted to `startup` (not `startup|clear|compact`) so the nudge is one-shot per fresh session. Appropriate as a guidance injection, not a status line. The `startup`-only matcher means user adding a credential mid-session won't see updated state until next fresh session.

### Full-briefing context with API call

Hook (`session_bootstrap.py`) hits a local API server for team status and task data, then writes a multi-page briefing (behavior rules, available agent templates enumerated from `~/.claude/agents/*.md`, available skills) to stdout for context injection. Rich runtime-driven context — contrast with static banners. Pays a startup-time cost for the API call plus optional opportunistic git-fetch update check. SessionStart matcher absent so all sub-events trigger the full chain unconditionally.

### Layered SessionStart context with conditional inclusion

A single SessionStart script composes one `additionalContext` from up to four layers, each conditional on a file existing in the repo: a hard-coded routing policy always emitted; a curated extract from a learnings file (only entries with `**Status**: verified` frontmatter, awk-filtered on `---` record separators); a whole-file inject of a docs index; a single-line pointer to a design doc when present. Each layer adds depth on demand; absent files contribute nothing. Layer-1 routing policy hard-codes the skill catalog in bash, requiring hook updates when skills are added/renamed.

### Self-emitting schema detection for cross-runtime context

The same SessionStart script produces one of two JSON schemas based on which runtime invokes it: under Claude, `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": …}}`; under Cursor (detected via `$CURSOR_PLUGIN_ROOT`), `{"additional_context": …}`. Single script, runtime-discriminated output. Avoids duplicating the layered-composition logic across two scripts.

### XML-tag emphasis wrapping

Layer-1 routing policy is wrapped in `<EXTREMELY_IMPORTANT>...</EXTREMELY_IMPORTANT>` tags as a prompt-engineering construct emitted as session context. The wrapper is a content convention, not a hook-schema field — it goes inside `additionalContext` as raw text.

### File-backed context written at SessionStart

A SessionStart hook runs a script that scans some workspace state and writes a daily/cycle brief to a known file location (e.g., `notes/daily/<date>-brief.md`). The model does not see the brief automatically; the user opens it or a downstream skill reads it on demand. Less intrusive than `additionalContext` injection — survives token-limit pressure, inspectable, idempotent. Tradeoff: discoverability, since the prompt has no signal that fresh context just landed.

### SessionStart + UserPromptSubmit chain for context injection

`SessionStart` fires `memory-bridge` and similar handlers; `UserPromptSubmit` chains 5-6 hooks (`memory-bridge`, `inject-policy`, `track-command`, `fix-proposal`, `breezing-signal`) that inject context into every prompt. Matchers narrowed (`startup|resume`, skipping `clear`/`compact`) so PreCompact/PostCompact handlers can do compact-aware context preservation separately. `once: true` prevents duplicate fires within a session.

### Per-prompt context reminder

`UserPromptSubmit` hook emits a small (~100-token) baseline reminder of the methodology's core rules on every prompt. Reinforces context as the conversation moves; cost is one hook invocation per prompt.

### Per-prompt bias / signal detection

The hook scans the prompt text for cognitive biases (acceleration, scope creep, over-optimization) or first-person distress phrases ("i'm stuck", "confidence: low"), logs hits to a rolling cache, and emits warnings or stronger nudges when threshold counts are reached within a time window. State-across-prompts implemented in a stateless hook via a pruned-log file at a stable cache path.

### Per-prompt anti-speculation rule injection

Hook (`anti-speculation-inject.js`) injects an epistemic-discipline rule on every user prompt — "cite a file:line from a Read/Grep done THIS turn, or say 'I don't know, checking'." Hook-based mechanism for enforcing agent epistemic discipline across a whole plugin surface, codified in `CLAUDE.md` and hooked in at runtime.

### Per-prompt context-window warning

Hook (`context_tracker.py`) reads the transcript JSONL referenced by the hook payload, sums `usage.input_tokens + cache_read + cache_creation`, emits `[CONTEXT WARNING]` at ≥80% or `[CONTEXT CRITICAL]` at ≥90%. Auto-detects 1M context window via model-name match plus by-value fallback. Pure observability injected into the user-prompt path.

### Per-prompt version-mismatch / worker-restart check

The hook calls a local worker daemon's `/api/version` endpoint and compares against the installed `plugin.json` version, killing and restarting the worker on mismatch. Runs on every prompt (intentionally exempt from any once-per-session dedup) so mid-session updates are caught immediately. Cost: one HTTP call per prompt.

### `UserPromptSubmit` skill-activator with confidence threshold

A UserPromptSubmit hook emits `hookSpecificOutput.additionalContext` with skill hints + memory recall (from a `session-log.md` style file) when a confidence threshold is met. Different trigger from SessionStart: fires per-prompt, can scope context to the current question. Sister hook to the SessionStart pair — three different context channels feeding the model.

### `UserPromptSubmit` fuzzy-matched skill injection

UserPromptSubmit hook fuzzy-matches the user prompt against YAML-frontmatter `triggers` arrays in `skills/**/*.md` (and per-project overrides like `.<name>/skills/**/*.md`), picks up to N matching skills, and returns their content via `hookSpecificOutput.additionalContext`. Skill discovery layered across project-local > plugin-bundled > user-home. Constraint: fuzzy-match tolerance allows unintended activation on typos.

### `UserPromptSubmit` for rule evaluation (not context)

A `UserPromptSubmit` hook exists but its purpose is rule evaluation rather than additive context — output is system messages reacting to the prompt, not appending instructions. Distinct from `SessionStart` injection.

### UserPromptSubmit prompt logger

`UserPromptSubmit` matcher runs a script per prompt — observed in one repo as a logger (`log-prompt.py`), not a context injector. Distinct from the SessionStart-based injection patterns.

### SessionStart purely for non-context side effects

SessionStart hook fires but emits no `additionalContext` / `systemMessage`; instead it performs side-effecting setup — writes bridge files (`~/.claude/<plugin>-session-state-path` containing the resolved `CLAUDE_PLUGIN_DATA` location), generates wrappers (per-session executable shell wrappers with the plugin's resolved lib path baked in at `~/.claude/<plugin>-<verb>.sh`), launches background services, plays distinct audio cues per matcher (`startup`/`resume`/`clear`/`compact`), prints effort/model nudges to stderr, OR writes shell-format env-var exports (`EVOLVER_PY=/path/to/venv/python`) into `$CLAUDE_ENV_FILE` for downstream skill steps to consume. Skills running in Bash-tool context don't receive `CLAUDE_PLUGIN_ROOT` or `CLAUDE_PLUGIN_DATA` from the harness, so bridge files at stable absolute locations bridge the env-var gap. Side-effect-at-startup pattern; vulnerable to test pollution (test runs that exercise SessionStart can overwrite the real bridge file with temp paths) — tests need backup/restore guards. Variant: SessionStart with multi-script division of labor — one script handles dep install silently while a sibling `session-start-env.py` prints a markdown readiness block with which env vars are set/missing, data-dir status, and channel-runtime status. Separates "make the world ready" from "tell the user what's ready."

### Echo-as-prompt for SESSION_SETUP

A SessionStart hook with a literal `echo` command reminding the agent to execute a `# Session Setup` section in CLAUDE.md. Fires on clear/compact too without a matcher, re-prompting after every context reset. Crude but functional — the agent treats the echoed string as a system message and acts on it.

### SessionStart with structured handler in standalone file

A SessionStart bootstrap (`session-start-bootstrap.js`) was specifically extracted to a standalone file (separate from inline `node -e` patterns used by other hooks) because inline `!` characters in fallback logic triggered bash history expansion in the inline pattern. Appropriate for SessionStart specifically; the extraction-to-file pattern resolves a real shell-environment fragility.

### Persona duplication between hook and skill

The persona text injected by SessionStart is also embedded in the skill's `SKILL.md`. Two copies diverge on edit — single-source-of-truth violation. Caused by fusing dep-install and persona-injection in the same SessionStart hook; refactoring would require splitting.

### Release-notes-as-context

After a successful self-update, the SessionStart hook extracts the current release's "What's New" section from `RELEASE-NOTES.md` (a 100+ KB file) and injects it as `additionalContext`. Self-announcing upgrade pattern. Constraint: section-selection logic must be precise; an off-by-one would flood the prompt with the entire 100 KB file.

### Lazy bootstrap on first hook (no SessionStart)

No SessionStart hook at all. Whatever bootstrap work is needed (binary download, cache priming) happens on the first non-SessionStart hook of the session. The author's stated rationale (in one sample) is that Claude Code plugins historically lacked post-install hooks, so lazy-on-every-hook is the most robust pattern; even after SessionStart became available, lazy-at-every-hook self-heals through mid-session plugin upgrades that SessionStart-only would miss.

### Install plus session telemetry

`SessionStart` runs two handlers in sequence: an install/banner echo, and a Node script that emits a structured session-started event to a metrics file (and optionally POSTs to a remote event bus when an env-var secret is set). Async, 5s timeout. Informational; never blocks. Adds an `on-session-start.mjs` companion to the install script. Constrains the plugin to ship telemetry plumbing alongside install plumbing.

### User-settings session-start hook installed by a skill

A skill writes a hook script to `~/.claude/hooks/<file>.sh` and edits `~/.claude/settings.json` to register it as a global session-start hook — outside the plugin's own `hooks.json`. The hook then prints "ACTION REQUIRED" directives to stdout that Claude reads at session start. Appropriate when the author wants always-on user-level nudges across all projects; constrains: the hook persists after `/plugin uninstall` (it lives in user config, not plugin scope), runs in every project regardless of relevance, and requires a sibling "uninstall" skill to unwind.

### Agent-driven resume protocol (no SessionStart)

No SessionStart hook is registered. Resume context is loaded by the agent itself per a "Session Resume Protocol" in its agent.md (reads a session-brief markdown, append-only JSONL, current state JSON, idea log). Resume only fires when the user launches the specific agent explicitly — a normal Claude Code session opened in the same directory does not auto-load.

### PreCompact hook for state-file eviction

A PreCompact hook scans the pre-compact transcript for an interrupt-then-unrelated-user-message pattern and archives the orchestrator's state file before compact removes the evidence. Protects against post-compact false resumption when the user cancelled mid-flow. Rarely-used hook event put to specific use.

### No SessionStart, only PreCompact / PostCompact / Stop / SessionEnd

The plugin registers compact-cycle and end-of-session hooks but no SessionStart. Inbound context is instead loaded on demand via slash commands. Appropriate when the plugin's context shape is determined by user intent at session start rather than baked-in defaults; constrains first-session-after-gap UX because cross-session memory is only refreshed on Stop, not at the next session's open.

### No session-context loading

The plugin does not register `SessionStart` or `UserPromptSubmit` hooks; reports or other behaviors fire only on completion-class events (`Stop`, `TaskCompleted`, etc.). Plugin relies on skill frontmatter `description` matching for surface — content loads on demand when the agent recognizes the skill is relevant. Dominant pattern; aligns with the "no always-on injection" posture. Skill-driven first-run bootstrapping (copying assets into cwd, creating files) runs only when the user explicitly invokes the bootstrap skill — setup never happens automatically. Constrains the plugin to post-fact observation. Appropriate when the plugin's job is summarization rather than guidance.

## SessionStart matcher scope

Which session sub-events the hook fires on.

### Empty matcher (all sub-events)

`matcher: ""` or matcher absent — fires on `startup`, `resume`, `clear`, `compact` alike. Appropriate for idempotent operations cheap to repeat. Wasteful when the operation is non-trivial (e.g., running `diff -q` and `command -v` checks on every `/clear`). Side effects that are non-idempotent (e.g., appending to `$CLAUDE_ENV_FILE`) accumulate across sub-events; idempotency must be designed in or accepted as a known issue.

### Explicit subset

`matcher: "startup|resume"` or `"startup"` only — fires on the chosen session phases. Appropriate when the hook produces side effects that should not repeat on every compaction. Constrains the author to know which phases matter for their hook's purpose.

### Per-hook differentiation within one plugin

Different hooks within the same plugin use different matchers — e.g., dep-install on empty matcher (any sub-event), context-emit on `startup|resume|compact`. Constrains coordination — one plugin's "boot work" may run on different triggers than its "context emit" work, with no shared coordination point.

### SessionStart sub-event matcher (`startup|clear|compact` excluding resume)

The expensive synchronous SessionStart hook is scoped to `startup|clear|compact` and excludes `resume` (where routing is already in context). A second unscoped SessionStart entry runs the cheap async context-engine on every sub-event including `resume`. Pattern reduces wasted re-injection while preserving cheap state work. Codex equivalent uses `startup|resume` because Codex lacks the `clear`/`compact` sub-events.

## Tool-use enforcement

Whether and how the plugin gates, modifies, or annotates tool calls before, during, or after execution — covering PreToolUse, PostToolUse, PermissionRequest, PermissionDenied, and event-completion gates.

### No enforcement (observational only)

The plugin registers no PreToolUse / PostToolUse hooks. Behavior is shaped entirely through SessionStart persona injection plus skill / command instructions. Plugins relying on read-only or restricted tool surfaces enforce that at the MCP server level (e.g., `OUTLINE_READ_ONLY=true` env var passed through `.mcp.json`) or via prose directives in agent prompts ("perform read-only operations only") — no structural enforcement at the Claude Code hook layer. The MCP server, when present, may have its own defensive code (typed errors, top-level `process.exit(1)` on fatal errors), but that's runtime defense inside the server, not Claude Code hook enforcement. Skill-level `allowed-tools` permission rules in frontmatter may be the only gate. Appropriate for plugins whose components are skills and reference docs rather than actions with side effects. Surface is install-only (`SessionStart`) plus user-facing components. Even events like `PermissionDenied` are inert as gates. Lowest hook-maintenance burden; loses the ability to block wrong tool calls deterministically. Dominant posture across the corpus.

### Skill-description prose as enforcement surrogate

The SKILL.md `description` field uses capitalized "MANDATORY" / "Never invoke X directly" phrasing to bias the agent toward the plugin's wrapper. Relies on skill auto-load by relevance match; no hard gate. Trade-off: zero infrastructure, but model-variance can let the agent slip through if the skill doesn't auto-load.

### Skill-level gating with no runtime hooks

The plugin omits hooks entirely and relies on the SKILL.md's workflow steps to enforce policy. Appropriate when the workflow is purely conversational and the gates are decisions the agent makes during step execution; constrains enforcement to whatever the agent honors voluntarily.

### Hook-only enforcement (frontmatter is documentation)

Agent frontmatter lists tools but does not encode permission rules; actual enforcement happens in PreToolUse, which reads a role spec and computes allow/deny. Appropriate when the plugin needs richer rules than frontmatter expresses (per-path scopes, bash-policy categories, blind-from constraints) — the spec becomes the source of truth and frontmatter is a documentation surface.

### Frontmatter-only enforcement (no PreToolUse)

Agent frontmatter declares `tools: <list>` and Claude Code's built-in scoping handles enforcement; no PreToolUse hook augments it. Appropriate for simple agents whose tool needs are static and fully expressible in the documented frontmatter schema.

### Auto-allow plugin's own scripts

Single PreToolUse with matcher `"Bash"` (or compound), purpose: detect when a Bash command is invoking one of this plugin's own venv-Python scripts and emit an `allow` decision so the user is not prompted. Inline bash `case` fast-path string-matches the stdin JSON; only on match does the hook pipe into a Python validator. Validator uses `Path.resolve(strict=True)` for traversal-resistance and exits with no-output ("pessimistic no-opinion") on any uncertainty, deferring to the normal permission flow. Appropriate as a UX optimization for plugins whose skills always invoke the same Python scripts; the cost is hard-coding the plugin name into the bash matcher pattern, breaking on rename.

### Multi-pattern PreToolUse safety stack

Multiple PreToolUse hooks all matching `Bash` (or `Read|Edit|Write|Bash`) run sequentially on every matching tool call. Examples: a destructive-command blocker (~30+ patterns, 3-tier severity), a secret-protector (~50+ file patterns + ~14 content patterns for hardcoded keys / tokens / PEM / connection strings), and a Bash-output compressor that rewrites noisy commands through an optimizer (with a never-compress allow-list for diffs / reads / failed commands). Latency compounds — each Bash call passes through every matching hook before execution. Documented fail-open posture for non-safety hooks (errors result in original command running unmodified); safety hooks presumed fail-closed on pattern match, fail-open on unexpected errors.

### PreToolUse guard set with multi-matcher concurrency

`hooks/hooks.json` declares multiple matcher blocks. One matcher (broad — `Edit|Write|Bash|NotebookEdit|mcp__filesystem__*`) runs a scope-enforcement script. A second matcher (`Edit|Write|Bash`) runs three guards in parallel: repo-boundary, protected-file, pre-edit-security. A third matcher (`Bash` only) runs a secret-scanner (gitleaks). Appropriate when policy is composable across orthogonal concerns (scope vs boundary vs security vs secrets). Constrains performance: every gated tool call waits on the slowest concurrent guard; deduplication across hooks is the author's responsibility.

### Multi-PreToolUse fan-out with matcher `*`

Five PreToolUse hooks all matchering `*` — per-agent tool tracking, write-protection, read-only/agent-tool-access enforcement, context-window pressure, search-input augmentation. Every tool invocation spawns multiple hook processes. Appropriate when the plugin layers several orthogonal pre-call concerns. Constrains latency: hook timeouts (2-60s per hook) compound under fan-out.

### Universal-matcher rule evaluator

A `PreToolUse` hook with no matcher (fires on every tool call) plus a `PostToolUse` companion runs a Python evaluator against user-defined rules in `.claude/<plugin>.*.local.md` files. Output is JSON `{"systemMessage": "..."}` to stdout; failure posture is uniformly fail-open with try/except wrapping that always exits 0 ("never block operations due to hook errors"). Timeouts declared (10s). Used to give the user a configurable tool-policy mechanism without modifying the harness.

### Scope enforcement (block out-of-scope writes)

Matcher `"Write|Edit|MultiEdit|Bash"`, purpose: enforce per-role write-scope and bash-policy for multi-agent setups. Reads role declaration from a spec file, computes allow/deny against the active subagent's scope, emits `pretool_deny` payloads as JSON on stdout. Configurable failure mode (`fail_open` / `deny`) per mission. Appropriate when the plugin runs multi-agent flows where each agent must be sandboxed to a subset of the codebase; the cost is the gate is now the trust anchor and must be carefully tested.

### PreToolUse as phase-scoped artifact gate

A single PreToolUse hook (no matcher, fires on all tools) enforces artifact-access rules driven by a YAML-frontmatter state file the orchestrator writes. Four rules encoded — block reads of cross-phase artifacts, block writes outside scoped directories, protect the state file from being overwritten by anything except the orchestrator. Only gates subagent calls (non-empty `agent_id`); orchestrator calls pass through. Fast-exit case-match on raw JSON fields skips the `jq` invocation when the tool isn't Read/Write/Edit. Output is `{"decision":"block","reason":"…"}` via `jq -n`; exit 0 silent on allow.

### Block-list with hard deny + soft warn classes

`scripts/file-guard.sh` classifies the target path against two pattern groups: hard-block (`.env`, `*.pem`, `*.key`, `*credentials*`, `*secret*`, `*.lock`, `package-lock.json`, `*/node_modules/*`, `*/.venv/*`, `*/target/*`) emits `exit 2` + stderr human message + stdout `hookSpecificOutput.permissionDecision: "deny"`; soft-warn (`migrations/*.sql`, `*.pb.go`, `*_generated.*`, `CHANGELOG.md`) emits `exit 0` + `systemMessage` JSON. Dual-output contract — stderr for the terminal display + stdout JSON for the harness's permission-decision schema. User-extensible block list via `<PLUGIN>_EXTRA_BLOCKED` env var (colon-separated globs).

### Fail-closed scope and command guards (belt-and-suspenders)

Multiple `PreToolUse` hooks (`Edit|Write` for path-scope enforcement, `Bash` for destructive-command guards and per-wave allowlist enforcement). Every security-critical hook wraps its body in `main().catch((e) => emitDeny(...))` so any unhandled error denies the call rather than allowing it through. Output convention is centralized: `emitAllow`/`emitDeny`/`emitWarn`/`emitSystemMessage` helpers in a shared `io.mjs` library produce a uniform JSON wire format (`{"permissionDecision":"deny","reason":"..."}` plus exit 2 for deny; exit 0 silent for allow). Hook emits both the `hookSpecificOutput.permissionDecision: "deny"` JSON envelope on stdout AND a human message on stderr, then `process.exit(2)` — documented rationale: "exit 2 alone is silently discarded by the current runtime." `emitDeny` requires a non-empty reason (throws if missing) — silent-deny is structurally unrepresentable. Path normalization (Windows separator, realpath symlink resolution) plus an ENOENT ancestor-walk for not-yet-existing Write targets defends against symlink escape. Stdin reads guard against runaway input via 1 MB byte cap plus 5s `AbortController` timeout. Appropriate for security-sensitive matchers where deny must succeed; a consumer who picks just one form (stderr OR stdout) will have hooks that appear to work in tests but silently pass in production.

### PreToolUse Bash matcher as ask-first guardrail

Two distinct PreToolUse scripts on `Bash` matcher parse the Bash argv to identify trade-placement (or sensitive) subcommands and emit JSON `permissionDecision: ask` with a summary so the user sees the intent before approving. `deny` is reserved for hard policy violations (cancel-all without `--yes-really`, network not in allow-list); `allow` is implied by no-op exit. Failure posture is fail-open silent — exit 0 on parse failure or unknown commands. Output convention: stdout JSON with `hookSpecificOutput.permissionDecision` and `permissionDecisionReason`; no parallel stderr-human messages.

### PreToolUse Bash matcher as executable-path enforcer

A `PreToolUse` hook with `matcher: "Bash"` parses the agent's intended command and rejects invocations that diverge from a sanctioned shape. Example: validates that a `--command` flag passed to a benchmark runner resolves to a specific known-good script (`./<tool>.sh`), after stripping a fixed set of wrapper prefixes (`env`, `time`, `nice`, `nohup`, `timeout <n>`, `VAR=val`). Blocks with `exit 2` + stderr human-readable message. Self-arming — the hook only activates when its target artifact exists in the workdir AND the relevant mode is active; outside that envelope, parse failures fall through. Constraints: regex-based command parsing is best-effort; commands constructed via shell variable expansion can slip through; novel wrappers (`chrt`, `taskset`, `stdbuf`) would block legitimate invocations.

### PreToolUse Bash dangerous-command blocker

`hooks.json` matcher `Bash` runs a Python script that inspects the bash command, optionally rewrites or blocks based on a denylist. Companion `inject-spec.py` on the same matcher likely rewrites the command rather than emitting `additionalContext` (placement on PreToolUse:Bash is unusual for context injection).

### Prompt-type Bash-pattern policy engine

A `PreToolUse` hook with matcher `Bash` and type `prompt` whose body is a multi-hundred-word list of blocked Bash patterns and their corrected rewrites. Claude evaluates the prompt against each proposed Bash command and returns a BLOCK or ALLOW verdict. The prompt also lists the rewrite for each blocked pattern, turning the hook into an in-context style guide that teaches the agent how to call the plugin's bin correctly. Blocks `cd && compound`, `&&`/`||` chains, `$()` in echo/printf, multiline JSON, `for` loops, piping tracker output to Python, and any non-bare invocation of the plugin's bin. Trade-off: prompt-engineering rather than deterministic code, with attendant non-determinism and per-call latency cost; duplicates much of the documentation also kept elsewhere.

### Inline `type: agent` hooks invoking secondary models

PreToolUse / PostToolUse / PreCompact / Stop hooks declared with `type: agent` and a literal multi-hundred-character prompt that invokes a secondary model (Haiku) for review. Stop's agent reads workspace state files and returns `{"decision": "block"}` to gate session termination. Parallel model invocation during hook evaluation; differs from the usual "hook calls a binary" pattern. Specific hooks return `{"permissionDecision": "deny"}` when the embedded agent or rule detects a violation (secrets in commit, TODO markers, injection patterns).

### PreToolUse advisory injection (no blocking)

A hook on `PreToolUse` matched against `Bash|Edit|Write|NotebookEdit` (or similar) writes `hookSpecificOutput.additionalContext` JSON on stdout to inject context before the tool call. No blocking by default; the agent reads the injected lessons and can choose to comply. Constrains the agent's information environment without restricting its action space. Variant: `PreToolUse` matchers on `Edit`, `Bash`, `Write` inject context (e.g., "blast radius" warning showing which symbols an edit affects, or staleness check on an index) but never block — `exit 0` always. Output is JSON on stdout for context injection; stderr for diagnostics. Constrains: the hook runs on the critical path of every matched tool call and budget management matters (e.g., 8-second timeout on a child node process invoked from PreToolUse means edits stall up to that budget on slow queries). Appropriate when the goal is teaching or reminding rather than blocking.

### PreToolUse blocking gate (env-var opt-in)

The same advisory hook adds a `decision: "block"` output when an env var (e.g., `<PLUGIN>_HOOKS_ENFORCE=1`) is set and a risk threshold is crossed. Default-off, opt-in to enforcement. Constrains the user to an explicit env-var flip before any blocking behavior fires; protects against accidental deadlocks during plugin onboarding. Appropriate when the hook's invariants are real but the maintainer wants advisory mode as the safe default.

### Soft-then-escalating PreToolUse hook

A hook starts in advisory mode, counts ignored reminders, and escalates to blocking after N consecutive ignores (e.g., 3 in `check-tool-skill.sh`). Constrains the agent to a documented escalation curve. Appropriate when the discipline being enforced is genuinely best-effort but persistent ignoring is a defect.

### Hard-blocking PreToolUse on commit-shape invariants

Hooks matched against `Bash` parse the command and block `git commit` when staged content fails a structural check (e.g. SKILL.md edited without referenced `references/` files; >2 files touched without `/review`). Constrains commit shape; users who legitimately need to bypass create a documented escape-hatch file (e.g. `.methodology-self-extend-override`). Appropriate when commit shape is verifiable from staged state and the cost of false-positives is bearable given a documented bypass.

### Workflow-state gate (PreToolUse `Write|Edit`)

Hook matches `Write` and `Edit` and gates them against pipeline state — denies edits when the plugin's state machine is in a phase where edits aren't allowed (e.g., before a planning gate is approved). Same belt-and-suspenders output as Bash deny. Models workflow state via hooks rather than relying on skill prose to guide the agent; structural enforcement of pipeline transitions. Plugin can be structured as a state machine with explicit user-approval gates between agent waves (Gate #1 = plan approval, Gate #2 = implementation approval). Skills represent transitions between states (`/forge:plan`, `/forge:implement`, `/forge:review`); hooks ensure illegal transitions can't happen by tool-level enforcement.

### Fact-forcing first-edit gate

A `pre:edit-write:gateguard-fact-force` hook blocks the first `Edit`/`Write`/`MultiEdit` per file and demands the agent investigate (importers, schemas, prior context) before allowing. Appropriate for workflow-discipline plugins targeting agent research quality.

### PreToolUse `Agent` routing/gate enforcement

Hook matches `Agent` (subagent dispatch) and constrains which subagents can run based on pending gates. Stops dispatch of agents that shouldn't run yet (e.g. implementer before plan is approved). Pipeline-state-as-policy pattern; hook-as-policy-engine.

### Layer-import / architecture rule validation

PreToolUse for `Write|Edit` runs an architecture-rule engine before the write commits — checks layer-import boundaries on PHP/TS/TSX (e.g., LAYER001-003, PHP001) and `exit 2` blocks the write. Same engine source as the PostToolUse rules — single rule engine across hook + CI lanes (see *Rule engine reuse*).

### Edit-targeted security reminder

A `PreToolUse` hook with `matcher: "Edit|Write|MultiEdit"` runs a security-warning script on file modifications. No declared timeout; if it hangs, the harness waits. Narrower trigger than the universal evaluator; still uses the JSON-to-stdout output convention.

### PreToolUse Edit/Write path validator

Matcher `Write|Edit` runs a bash script that reads the tool-call payload via stdin + `jq`, denies writes to a protected path glob (`~/.config/<tool>/themes/`), and exits 2 with `permissionDecision: "deny"` + a `systemMessage` telling the user where to develop instead. Fail-closed posture. Pitfall: `input=$(cat)` has no timeout, so a stalled stdin can hang up to the PreToolUse default budget.

### PreToolUse Edit/Write risk advisor

Matcher `Edit|Write` runs a check script (`check-ehrb.sh --diff --dry-run`) gated on a state file's existence (`[ -f .sparv/state.yaml ] && ...`). The `|| true` suffix makes non-zero exits fail-open — the advisor never blocks, only annotates. Used for risk-of-modification surfacing without interrupting work.

### `if:` permission-rule sub-matcher

PreToolUse entry registered with `matcher: "Bash"` and an additional `"if": "Bash(git push*)"` field that further narrows the hook to git-push-shaped commands only, using the same permission-rule glob syntax as `permissions.allow/deny`. Multiple alternatives across tools supported (`"if": "Write(src/**) Edit(src/**) MultiEdit(src/**)"` — the `if:` field carries space-separated tool/glob alternatives, narrowing the hook to writes under a specific path prefix). Far more precise than matching all Bash invocations and re-parsing inside the hook. The path pattern is hard-coded per-consumer (a comment instructs the user to "customize this pattern to match your source directory") — installation requires post-install customization. Brittle against future Claude Code changes to `if:` parsing — silent regression possible.

### `PermissionRequest` with `if:` allowlist

`PermissionRequest` hook on `matcher: "Bash"` uses an `if:` clause enumerating auto-allow patterns (`git status*`, `git diff*`, `npm test*`, `pytest*`, `go test*`). Fine-grained per-hook conditional gating without dispatching to a binary. Replaces the "binary returns permissionDecision" round-trip with declarative conditions in the manifest itself.

### `PermissionRequest` delegated to hardware

A `PermissionRequest` hook routes the allow/deny decision to a physical input device (Flipper Zero) via a 60-second socket round-trip. Emits `hookSpecificOutput.decision` JSON with `{behavior: "allow"}` / `{"deny"}` / `{"ask"}`. On no-bridge or timeout the hook exits 1 to fall back to Claude's native dialog. Generalizes to any "remote approval" surface. Constraint: the timeout is non-configurable; user walks away → Claude waits a full minute.

### `PermissionRequest` dormant in source

A `permission-handler.ts` (or similar) exists with header comment "OPT-IN: This hook is NOT registered in plugin.json by default. To enable, add a PermissionRequest entry." Present in source, absent in manifest. Constraint: a reader grepping hook registrations won't find it; only the file header reveals it.

### `PermissionDenied` classification with retry-state TTL

Hook reads denial JSON, calls a sidecar API to classify into one of four buckets (`recoverable_with_retry`, `recoverable_with_workaround`, `needs_user_approval`, `permanent_denial`), then emits retry hints, workaround guidance, or logs silently per classification. Falls back to local keyword matching when API is unreachable. Retry state persisted in a JSON file with 1-hour TTL to prevent retry loops. Hook-as-classifier — offloads policy decisions to a sidecar so policy updates don't require redistributing the plugin.

### `PermissionDenied` as event log

The `PermissionDenied` hook event is registered, but the handler treats it as a counter / log source, not an enforcement gate. The hook tallies denials and surfaces the count in a report. Constrains nothing about future tool calls. Appropriate when the goal is observability rather than gating.

### Compensating revert (PostToolUse defense in depth)

Matcher `"Write|Edit|MultiEdit|Bash"`, purpose: if a write slipped past PreToolUse for a role that should not write (e.g. PreToolUse fail-opened, or a custom role bypassed scope), revert the write. `git checkout` for tracked files; `rm` for untracked. Ledger records `revert_mode` and `revert_success`. Appropriate when the plugin's correctness model is "no out-of-scope writes ever, even if a gate bug fires" — pairs with PreToolUse to make scope a two-layer guarantee.

### Format-then-lint PostToolUse (non-blocking)

PostToolUse runs `scripts/format.sh` then `scripts/lint.sh` sequentially, both non-blocking — warns on failure, doesn't block. Dual command in a single hook entry. Lightweight; assumes the formatter/linter are installed on the host.

### Full rule engine with cross-file pattern aggregation

PostToolUse runs a 13.5KB+ rules engine that consults a session-state DB (SQLite) after recording a violation. If the same rule has fired in 3+ files this session, the hook appends a "PROJECT-WIDE PATTERN: {rule} found in {N} files — consider a project-wide fix or global ignore" banner to the block/warn message. Session-aware violation aggregation delivered through hook output. Per-rule inline suppression supported via `<plugin>-ignore: <RULE_ID>` comments inside source files.

### Informational fail-open post-edit hook

Single `Edit|Write` `PostToolUse` hook running an incremental typecheck on the edited file. Implemented fail-open (`.catch(() => process.exit(0))`) — never blocks tool flow. Purely informational; surfaces typecheck issues as warnings without obstructing the edit. Counterpart to fail-closed `PreToolUse` enforcement: pre-checks gate, post-checks observe.

### Post-edit health-check (PostToolUse on `Edit|MultiEdit|Write`)

A PostToolUse hook on edit / write tools runs a domain-specific check (e.g. simulator compilation / crash check via CDP) with a short timeout. Last-write-wins debounce — only the most recent edit triggers the check. Silent-skip when prerequisite state is missing (no active session, file-type mismatch, target is a test or config file). Output is plain stdout text the agent reads, not structured JSON; documented exit-code convention (0 = success, 1 = error logged non-blocking, 2 = block operation explicitly NOT used).

### PostToolUse async telemetry + eval gate

A matcher block runs four async post-edit scripts on every Edit/Write: self-learn, telemetry, review-hint, eval-gate. A separate matcher emits async post-bash telemetry. The async modifier prevents tool-call latency but leaks background processes if the user exits mid-call. Appropriate when the plugin layers on cross-session learning, analytics, and self-evaluation; constrains process hygiene because nothing reaps the async children.

### PostToolUse skill telemetry / edit tracking

A PostToolUse on `Skill` records skill-invocation telemetry. A PostToolUse on `Edit|Write` logs file changes (drives TDD reminders downstream) and auto-appends working-state files (project-map.md, session-log.md, state.md) to `.gitignore` on first write. Keeps the plugin's working-state files out of git automatically — consumer never has to remember to add them.

### PostToolUse doc-size guard + state sync

Hook matches `Write|Edit` and enforces a doc-size cap plus syncs the plugin's gate state to reflect the just-completed write. Two responsibilities chained on the same matcher.

### PostToolUse `*` context tracking

Hook matches `*` and records every tool call to the plugin's context store; always-on observability. Distinct fail-open posture — context tracking that fails should never block the user.

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

### Test-success unlocks subsequent action

`PostToolUse` matcher `Bash` (with `async: true`) inspects the tool result's exit code and command line; if exit is 0 and the command matches a regex of common test runners (`run-tests.sh|phpunit|jest|vitest|pytest|cargo test|go test|npm test|pnpm test|yarn test`), the hook flips a session-state `verified=true` flag. A separate PreToolUse on `git push` (via `if: "Bash(git push*)"`) reads that flag and allows the push without further friction. Emergent workflow: "test-then-push unlocks push automatically." State-machine semantics implemented across two stateless hooks via shared session state.

### Manual-only PreCompact with self-healing seam check

`PreCompact` hook with `matcher: manual` (so auto-compact is never blocked — it could push context over 100% and lose everything). On manual `/compact`, the hook reads `.reviews/handoff.json` and blocks if status is `PENDING_REVIEW` or `PENDING_RECHECK`, or if a git rebase/merge/cherry-pick is in progress. Self-heals: if the handoff has a `pr_number` and `gh pr view` reports the PR `MERGED`, the gate clears the status and lets the compact proceed. Requires Claude Code v2.1.105+.

### TaskCompleted hard-block on missing memo/result

Hook matches `TaskCompleted`, reads task ID from the payload, calls the sidecar API to verify the task has a memo and result recorded; on failure writes `[OS BLOCK] <reason>` to stderr and exits code 2 (the hard-block convention). Connects the hook's deny convention to external business state (sidecar API), not just local rules — a hook that enforces "you can't mark this done until you've logged progress."

### Event forwarding to sidecar (PreToolUse + PostToolUse)

Hook matches `Agent|Bash|Edit|Write` and forwards the event payload to a plugin-owned HTTP server (`POST /api/hooks/<event>`). Pure observer — no policy decisions in-hook; the sidecar dashboard consumes the events. Pays a per-tool-call subprocess spawn cost (paired with a sibling reminder hook on the same matcher means two spawns per pre and post phase).

### PostToolUse local workflow reminders

Hook matches the same broad event set and emits stdout reminders based on a local rules engine (delegation-threshold counters, sequence triggers). Self-described <100ms target with local-only file I/O. Large hook script (~54KB) representing a non-trivial rules engine in the hook layer — "thick local hook, thin sidecar server" division of labor. Discrimination strategies that prevent false-positive nudges: word-boundary regex (e.g., `(^|[^a-zA-Z0-9-])mm($|[[:space:]])` matches `mm` only as a whole token, avoiding substrings inside `mmdd`/`commit`/`common`); session-scoped one-shot markers (e.g., `${TMPDIR}/.<plugin>-skill-nudge-${session_id}` with `$PPID` fallback) that fire the nudge once per session rather than on every matching tool call; cross-language Bash → Python trampolines (`bash -c 'PY=$(command -v python3 || command -v python || command -v py); …'`) for Windows / Git-Bash compatibility. Reminders may emit a `<system-reminder>` envelope pointing the agent at a relevant skill via `hookSpecificOutput.additionalContext`.

### TDD reminder (PreToolUse on src/ writes)

PreToolUse with an `if:` clause narrowing to writes under `src/**`. On match, emits `hookSpecificOutput.additionalContext` with a "write a failing test first" prompt. Fail-open (no `set -e`); silent on non-matching paths.

### Observational notification trigger

Matcher `"ExitPlanMode|AskUserQuestion"` (and similar Claude-Code-decision events), purpose: fire desktop or webhook notifications when Claude reaches a decision point. Not gating — never emits deny. `timeout: 30` to avoid hanging the host. Appropriate when the plugin's role is alerting the human, not modifying the model's flow.

### Validate-and-nudge on InstructionsLoaded

`InstructionsLoaded` hook validates that project documentation files (e.g., `SDLC.md`, `TESTING.md`) exist, nudges on missing files, on stale plugin version (≥3 minor delta), and on open API-shepherd issues from a weekly cron. Cheap one-shot check at session start. Available since Claude Code v2.1.69 — version floor declared inline in hook comments rather than in `plugin.json`.

### `PostToolUseFailure` post-hoc diagnostic hook

A hook fires on failures of MCP tools matching a namespace (`mcp__*<plugin>*`) and emits a tailored diagnostic ("CDP session is not active. Metro is not running on port X. Try: cdp_status to reconnect.") that the agent reads as plain stdout. Effectively a "here's why your MCP call just failed" surface — rare in the ecosystem; most plugins use PreToolUse for validation rather than post-hoc explanation. The hook inspects multiple environment / process states (active flag, port availability, simulator boot state, adb device presence) to compose the diagnostic.

### `SubagentStart` context injection

A SubagentStart hook injects connection / state info ("CDP bridge is connected (platform: X, port: Y)") into every subagent spawn so the subagent does not need to re-probe. Paired with frontmatter "PARENT-SESSION-ONLY" warnings on agents that cannot run under Task-tool spawning (because MCP stdio doesn't propagate to subprocesses). Documents an MCP-inheritance gotcha at the hook layer.

### `CwdChanged` re-detection hook

Re-runs project-type detection when the user `cd`s to a new directory; emits a warning ("tools may not work here") when the new cwd doesn't satisfy plugin prerequisites. Rare across the ecosystem — most plugins do not react to cwd changes.

### Stop-event handlers for session-end aggregation

Stop hooks (multiple, e.g. session-handoff, instinct-extraction, eval-gate finalization) run when the session ends. Each one aggregates JSONL events the PostToolUse hooks emitted during the session into summaries or longer-term stores. Appropriate when the plugin maintains durable cross-session state and needs a deterministic place to consolidate it; constrains start-of-session UX because the consolidated view is only refreshed on Stop, not on session open. Two distinct uses observed: **aggregation for export** (compose handoff summaries, write to JSONL or external sink, consumed across sessions) versus **ingestion for plugin-local state update** (Stop hook parses transcript and writes to plugin-owned persistent state like a reasoning graph; data never leaves the plugin). Stop and SubagentStop may share a single handler file via `hook_event_name` discrimination — same event-shape contract, two events.

### Stop-hook prompt re-injection loop

A `Stop` hook emits `{decision: "block", reason: "<previous-prompt>", systemMessage: "..."}` to re-feed the prior prompt back into the agent on each Stop, implementing a self-iterating work loop. State (iteration counter, escape protocol, session ID gating) lives in `.claude/<plugin>.local.md`. Non-obvious use of the Stop block protocol as a control-flow primitive — the hook API as agentic-loop substrate.

### Stop-hook with budgeted resume

A `Stop` hook decides whether to auto-relaunch an agent, capped by per-session resume count and time-since-last-resume. State persisted in a session JSON file (`resume_count`, `resume_at`). Three modes: `headless` (launches a new background `claude -p` process), `prompt` (prints instructions to the user), `off` (disables auto-resume). Plugin-level flow control distinct from in-agent loop bounds; the hook constrains the harness's session lifecycle directly.

### Repo-scope self-restriction

Hooks inspect `cwd` for `.claude-plugin/plugin.json` (or another sentinel) and exit silently when run outside the methodology repo. Prevents the plugin's enforcement from interfering with unrelated projects on the same host. Constrains the hook surface to the repo where it makes sense; means the hook never fires outside that repo unless `/adopt` has written project-level settings. Appropriate for plugins whose enforcement only applies to their own methodology context.

### Documented bypass mechanism

A sentinel file (e.g. `.methodology-self-extend-override`) that, when present in the repo, suppresses hard-enforcement hooks. Documented in the hook README rather than hidden. Constrains the hook's invariant — "block unless escape hatch is explicitly present." Appropriate when there are legitimate cases (extending the methodology, e.g.) where the invariant should not apply.

### Numbered-requirement traceability annotations

Every security-critical hook source file opens with a `SECURITY notes (inline refs)` block listing `REQ-01` through `REQ-NN`, and every relevant function cites its REQ number inline (`// SECURITY-REQ-03: resolve symlinks ...`). Pattern: requirements in a security pre-review document trace to specific lines of code via comment annotations. Discipline that lets a reviewer confirm coverage by grep rather than by re-deriving the threat model. Notable for agent-written code where the requirement-to-line traceability would otherwise erode rapidly.

### Documentation-asserted but unwired hooks

ARCHITECTURE.md (or README, or test fixtures) describes a richer hook surface (`pre-commit-gate.sh`, `post-write-check.sh`, `post-test-verify.sh`, `userConfig` declarations, registration-list constraints) than `hooks/hooks.json` (or `plugin.json`) actually wires. Either future work or invoked by a non-Claude-Code mechanism. Surface-asymmetry is a research-relevant signal: docs may overstate the shipped enforcement surface. Variants observed: hooks shipped in the repo but absent from the registration list (a regression where the synced registration list omitted a real hook for two minor versions); hooks asserted by tests but missing from the manifest (test contracts disagree with production wiring); design-intent visible in source but no runtime path that exercises it (e.g., snooze-file read path with no writer, partial CLI wrappers exec'ing artifacts that no build step produces).

### Rule engine reuse across hook + CI lanes

Both `ci/<plugin>-ci.sh` (pipeline-mode CI) and `hooks/post-write-check.sh` (real-time-mode hook) source the same `hooks/lib/pack-loader.sh` and `hooks/lib/rules-engine.sh`. README markets this as "zero drift" — same engine invoked at two different lifecycle points. Adapter pattern (`adapter_detect/run/annotate/comment/exit`) provides four CI-provider implementations (GitHub Actions, GitLab CI, Bitbucket Pipelines, Jenkins). One engine; two surfaces; pluggable CI substrate.

## Hook handler runtime

What language or binary the hook handlers run on, and how dispatch is structured.

### Bash scripts at conventional path

Hook commands point at `.sh` files in `hooks/scripts/`. Mixed shebangs across scripts (`#!/bin/bash`, `#!/usr/bin/env bash`). May use `set -uo pipefail` (NOT `-e` because `realpath` and other commands that may fail on not-yet-existing files cannot use bare `set -e`). Handlers may print stderr human text only, never JSON, with soft-exits throughout. Appropriate for low-complexity side-effects (frontmatter checks, edit logging) where bash is sufficient and the failure mode should never block tool calls.

### Per-hook bash scripts with selective strict mode

Each hook is a small `.sh` script invoked directly from `hooks.json`. `set -euo pipefail` is used on hooks that need fail-fast (e.g., pre-write content validation); other hooks run without strict mode and rely on `exit 0` to fail-open. `{"systemMessage": "..."}` JSON on stdout for non-blocking advice; stderr + `exit 2` for hard blocks. Appropriate when hook count is small and per-hook concerns are simple. Constrains: no centralized fallback for env-var resolution; per-hook copies of common boilerplate accumulate over time.

### Single Go binary with subcommand dispatch

Every hook entry calls `${CLAUDE_PLUGIN_ROOT}/bin/<plugin> hook <event-name>`. The binary owns hook protocol, JSON schema emission, decision logic, and per-event handlers. One executable, many entry points. Appropriate when the plugin's logic is large enough to warrant a compiled engine and when consistent JSON output across all hooks matters (the binary alone knows the full schema).

### Python stdlib runner with external probing

Hooks call `python "${CLAUDE_PLUGIN_ROOT}/runner/run.py"` (a single Python file using only stdlib). Runner shells out to system audio binaries (`mpg123`, `ffplay`, `paplay`, `aplay`, `afplay`, PowerShell players) by probing the platform. No Python venv, no third-party packages. Appropriate when the only "dependencies" are system tools the user already has, the failure mode should be silent skip, and zero-install is the design goal.

### Node `.mjs` files invoked via `node`

Hook commands point at `hooks/<name>.mjs` invoked through `node` in `hooks.json`. ESM modules with top-level `import`. Requires a `node_modules/` adjacent (see *Dependency installation*). Appropriate when the plugin's runtime is Node and its hooks share a library tree.

### TypeScript-compiled hooks with hand-patched imports

Post-`tsc` distribution step (`scripts/copy-hooks.js`) mirrors `dist/` into `hooks/dist/` + `mcp/dist/` + `scripts/` and rewrites relative imports (`'../xxx'` → `'./dist/xxx'`, etc.) so hook entry points stay plain `.js` invokable by `node` while pulling shared code from a co-located `dist/` tree. Avoids both a runtime TS loader in hooks and a bundler. Build-system gotcha called out: "Always run `npm run build:hooks` (not just `npm run build`)".

## Hook output contract

How hooks signal decisions to the harness and surface them to the user — JSON envelopes, where logs go, and how output discipline is enforced.

### Stderr for human display + stdout JSON for harness

Hook emits a human-readable message on stderr (terminal display) AND a `hookSpecificOutput` JSON object on stdout (harness's permission-decision schema). Both surfaces are written for blocking exits; warning-only exits emit only `{systemMessage: "..."}` on stdout. Without stderr, the user sees only "No stderr output" and no actionable message — the dual contract is required for usable UX. CHANGELOG entries explicitly call out fixes for this regression. Stderr is reserved for debug-mode logs prefixed with the plugin's name; stdout for the contract — the JSON-on-stdout discipline is maintained regardless of debug verbosity.

### `systemMessage` for human-readable summaries

Hooks emit `{"systemMessage": "..."}` JSON on stdout for report-style output that Claude Code surfaces inline. Used for completion-event reports (Stop, TaskCompleted, etc.). Constrains output volume to whatever Claude Code's hook-output cap allows (10,000 chars; overflow silently replaced with an opaque stub).

### `additionalContext` for context injection

Hooks emit `{"hookSpecificOutput": {"additionalContext": "..."}}` JSON to inject context the agent reads. Used by PreToolUse advisory injection and by SessionStart/UserPromptSubmit context loading. Distinct from `systemMessage` in that the agent processes the content rather than the user reading it directly.

### `decision: "block"` for gating

PreToolUse hooks emit `{"decision": "block", "reason": "..."}` JSON to refuse a tool call. Used by hard-blocking gates and the env-var-gated optional gates. Stderr carries the human message; stdout carries the contract.

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

### Inline-truncated + full-HTML dual output

When a report exceeds Claude Code's 10,000-char inline cap, the inline copy is truncated with `⋯ +N more — see HTML report` markers while a full HTML file is always written to a project-relative path (`<project>/reports/<plugin-name>/<timestamp>-<event>-<session>.html`). Convention is per-author across all their plugins, not a Claude Code platform feature. Constrains the plugin to manage its own out-of-band output store. Appropriate when reports legitimately exceed the inline cap and the user wants both a quick scan and a deep-dive.

## Hook failure posture

How hook scripts handle their own exceptions, and how those failures relate to tool execution.

### Fail-open with always-exit-0

Every hook (`.mjs`, `.sh`, `.py`) wraps its body in try/catch (or shell `|| true`) and ends with `exit 0`. Combined patterns:

- `set -uo pipefail` (no `-e`) plus per-statement `|| echo ""` fallbacks
- Inline `bash -c '… || exit 0'` trampoline at the `hooks.json` command layer
- Python scripts with top-level `try/except` and `sys.exit(0)` on failure
- `trap 'exit 0' ERR` while preserving `set -e` semantics elsewhere
- `try { ... } catch { outputContinue(); }` with centralized helpers emitting `{"continue": true}`

Multiple layers of fail-open compose to "never block the user's session" as an explicit principle. The system can be three layers deep — trampoline + script-level + handler-level. Even Pre/PostToolUse hooks documented as "blocking" are sometimes effectively advisory. Codified at the project level: "all hook scripts MUST use `exit 0` (pass) or `exit 2` (block); NEVER `exit 1`." Even the fallback's own ledger-write attempt is wrapped in its own try/except. Rationale: "a bug in the hook never deadlocks the agent" / "Never throw from a hook function." Constraints: persistent failure modes (no network, missing tool, malformed input) are silently absorbed; diagnosing a "hook isn't working" report requires reading the hook source.

### Fail-open envelope via `trap 'exit 0' ERR`

Every hook script opens with `set -uo pipefail` plus `trap 'echo "WARNING: <hook> failed at line $LINENO" >&2; exit 0' ERR` — on crash, the hook emits a warning to stderr but exits 0 so writes/pushes are never blocked by hook bugs. Pairs with explicit-exit-code discipline inside the hook body.

### Fail-open posture with explicit comment contract

Every shell hook begins with a comment declaring the contract ("Exit code MUST be 0 always — a failing hook must not interrupt Claude") and uses `set -euo pipefail` plus `|| true` on every external call, terminating with `exit 0`. Selective failure: a typo outside a command path still halts; CLI failures are swallowed. Appropriate when hook reliability matters more than hook correctness — the author would rather miss telemetry than block the user. Constrains visibility: silent swallowed failures need an out-of-band log (`hook-errors.log` written by an `_log_error` helper) to diagnose.

### Pipefail with selective suppression

`set -euo pipefail` halts on errors early; later hook steps deliberately suppress with `|| true` or `2>/dev/null || true` so notification failures don't propagate. Final `exit 0` regardless. Mixes strict-by-default with explicit per-step graceful degradation. Appropriate for shell hooks that interact with optional hardware/services.

### Fail-open with degraded-mode fallback

When a runtime dep is missing (e.g. `tiktoken`), the plugin falls back to a cruder approximation (chars/4 estimate) and writes a warning to stderr. Hook still exits 0. Constrains the report's accuracy but preserves liveness. Appropriate when graceful degradation is more useful than total absence.

### Fail-closed with circuit breaker (retry with backoff)

A purpose-built `HookCircuitBreaker` wraps the hook body, retrying with backoff (e.g. 100ms, 500ms) before escalating to a per-hook configurable failure mode: `deny` for pre-tool, `block` for subagent-stop, `warn` for stop. Configurable per mission via a manifest flag. Pattern-influenced by Erlang/OTP and resilience guidance. Appropriate when correctness matters more than blast-radius — gates that must not silently fail.

### Pessimistic no-opinion (exit 0 with no output)

The hook exits 0 with no stdout output on any uncertainty rather than emitting `allow` or `deny`. Effect: Claude Code falls back to its normal permission flow and prompts the user. Distinct from fail-open-with-allow (which auto-approves on uncertainty) and from deny-on-uncertainty (which over-blocks). Appropriate for permission-augmenting hooks where over-approval is a safety problem; the cost is a slightly busier permission UX when the validator is fragile.

### Mixed posture (fail-closed for security, fail-open for context)

Per-hook decision documented in code comments. Security-sensitive matchers (`bash-guard`, `workflow-guard`, `task_completed_gate`) emit deny + exit 2 on policy violation. Observability hooks (context trackers, banner printers, dep installers) swallow errors and exit 0. Mixed posture is intentional and documented per-hook. Hooks intended to block (PreToolUse/Bash) are `prompt` type — Claude evaluates and returns BLOCK/ALLOW. Hooks intended not to block (PostToolUse, PreCompact, SessionStart) are `command` type and exit 0 unconditionally with `|| true` suppression on every sub-command. Defensive `[ -f "$CONFIG_FILE" ] || exit 0` guards at the top of every non-blocking hook. Appropriate as a learned discipline — earlier `prompt`-type non-blocking hooks caused "stopped continuation" errors when their inputs were missing; command-type with explicit fail-open is the corrective. Combines naturally with inline `type: agent` hooks where the agent's judgment is the gating signal.

### Fail-closed on bootstrap, silent fail-open on runtime hooks

SessionStart bootstrap uses `set -euo pipefail` and halts on any error (Python version check, venv create failure, pip install failure). Runtime hooks (Stop, UserPromptSubmit) wrap their async work in bare `except Exception: sys.exit(0)` blocks — errors during ingest or context injection never surface to the user. Appropriate when the bootstrap must establish strict preconditions but the runtime hooks are "best-effort" augmentations. Trade-off: silent failure means a misconfigured runtime hook is invisible to the user.

### Silent-on-failure SessionStart

SessionStart hook silences all install errors via `>/dev/null 2>&1` and `|| true`. No JSON `systemMessage`, no stderr message, no `stopReason`. Appropriate for hooks that should never block session start under any circumstance; constrains observability — there is no in-session signal of install failure.

### Fail-closed permission deny

Hook script outputs `{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "..."}` and exits 2 to block the offending tool call entirely. Used for invariants like "do not write to this protected path" rather than for missing deps. Stdin parsed with `jq` against the tool-call payload.

### Silent-ignore graceful degradation

Older Claude Code versions silently ignore unknown hook event names, missing `userConfig`, etc. Plugins relying on the host's silent-ignore behavior have no machine-readable version floor — the runtime degrades to whatever subset the host supports. Constrains version-floor declaration to documentation only.

## Hook timeout and async philosophy

How the plugin sizes the latency budget for each hook based on what the hook does and what it blocks.

### Differentiated per-hook timeouts

`UserPromptSubmit` carries an explicit timeout (e.g., 10000 ms) because it blocks the model and must finish fast. `Stop` is `"async": true` with no timeout — fire-and-forget background work like graph ingest. `SessionStart` has no timeout because provisioning (pip install, venv build) can take minutes on first install and must not be killed. Three different postures for three different latency budgets on the same plugin. The 10-second ceiling on prompt-time context injection drives downstream design choices (graph cache to eliminate per-turn rebuild, k-limited search) — the timeout is not just a guardrail but a budget that shapes what the hook can do.

## Cross-platform Python invocation

How Python hook scripts cope with the absence of a uniform `python3` on every platform.

### Bash trampoline resolving python3 → python → py

`hooks/hooks.json` commands are wrapped in `bash -c 'PY=$(command -v python3 || command -v python || command -v py); [ -n "$PY" ] && "$PY" <script> <arg> || exit 0'`. The trampoline accommodates Windows / Git-Bash-on-Windows where `python3` may not exist but `python` or `py` does. Documented in CHANGELOG as a Windows-compatibility fix. Constraints: the trampoline shape is duplicated inline across every hook entry; any change requires repeating the edit at every site.

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

## State persistence

Where the plugin keeps state that survives across sessions — caches, ledgers, manifests, mission state, file-based memory, cross-session telemetry.

### `${CLAUDE_PLUGIN_DATA}` for venvs and stamps

Per-plugin data dir under the host's plugin-cache root. Used for the venv (`/venv`), the install-version stamp (`/installed-version`), and similar "host-managed cache that survives session boundaries" content. State files (e.g., `session-state.json`, version-stamp markers, last-checked timestamps, retry-state JSON, permission-denial TTL state) under the plugin's managed data dir. Inspectable, simple format. Standard idiom; aligns with the plugin reference. Persists across sessions; survives plugin upgrades. Distinct from `${CLAUDE_PLUGIN_ROOT}` which holds plugin-distributed assets. Appropriate when state is per-user and must be writable.

### `${CLAUDE_PLUGIN_ROOT}/bin/` for downloaded binaries

Inside the plugin cache itself (next to the wrapper that downloads them). Distinct from `${CLAUDE_PLUGIN_DATA}` — keeps everything the wrapper might need adjacent to the wrapper. Appropriate when the binary should be co-located with the script that resolves its path; the cost is binary churn lives inside the plugin cache rather than a dedicated data area.

### `${XDG_CACHE_HOME:-$HOME/.cache}/<plugin>/` for verified-version cache

User-level cache directory for fast-path verification — separate from the plugin cache so it survives plugin reinstalls/upgrades. Appropriate when the cache is purely an optimization (cold path can rebuild it) and shouldn't be invalidated by plugin reinstall.

### `<git-common-dir>/<plugin>/` for mission state

State stored under the git common directory rather than `.git/` directly — crucial when the plugin uses worktree isolation, because `.git/` differs per worktree but `git-common-dir` resolves to the same location across them. Mission manifest, ledger, per-role results all live here so coordinator + worktree-isolated subagents share one state. Appropriate when the plugin's correctness depends on cross-worktree state coherence; the cost is dependency on a git repo being present and the user not removing the dir manually.

### `${CLAUDE_CONFIG_DIR:-${CLAUDE_HOME:-$HOME/.claude}}/<plugin>/` pointer files

A pointer file at the host's config dir holding the plugin's current resolved root, written through "only on change" with atomic rename. Used so older cached paths and shim wrappers can find the current plugin root across reinstalls. Cross-session breadcrumb for binaries that might be invoked from multiple resolved paths over their lifetime. Appropriate as a fallback for shim wrappers; the cost is leakage if the plugin is uninstalled (the pointer file persists in `~/.claude`).

### Bridge files at `~/.claude/<plugin>-*` for Bash-tool-context access

Skills running in Bash-tool context don't receive `CLAUDE_PLUGIN_DATA`, so the plugin writes a path-bridge file at a stable location every SessionStart that resolves to the data dir, plus optional executable wrappers (`~/.claude/<plugin>-<verb>.sh`) with the plugin's resolved lib path baked in. Rebuilt every session; stale wrappers from old plugin versions are silently overwritten — clean by design but fragile against tests running SessionStart in isolation.

### Plugin-chosen `$HOME/.<plugin>/` with override env var

A plugin-named state directory under the user's home (e.g. `$HOME/.<plugin>/`) holds config, analytics, sessions, and other durable state. An override env var (`<PLUGIN>_HOME`) lets users relocate it. Appropriate when state is meant to survive across projects, across Claude Code reinstalls, and across cross-tool deployments (Claude + Codex sharing one state dir). Constrains backup and discovery: not where users expect plugin data per Claude Code conventions, so docs must call out the location explicitly.

### Plugin-managed file location, no convention

State files (JSONL telemetry, learning logs, session timelines) live under the plugin-chosen `$HOME` path rather than `${CLAUDE_PLUGIN_DATA}`. The plugin's bin tools read/write directly. Appropriate for the same cross-tool-sharing rationale; constrains visibility because the Claude Code harness has no awareness of these files.

### File-based memory stack with auto-gitignore

A small set of working-state files at the project root capture cross-session state: a JSON snapshot (auto-managed, e.g. git blast radius), a structure-cache markdown file, a decision-history log, a task-snapshot file, and an error→solution map. The stack is auto-appended to `.gitignore` on first write by a PostToolUse hook so it never gets committed by accident. Read by SessionStart / UserPromptSubmit hooks to re-hydrate context. Distinct from `memory: user|true` agent frontmatter, which signals model-side memory rather than file-based state.

### Skill-side experience seeds with stateful HOME directory

Seed YAML files (e.g. `seed-experience/common-failures.yaml`, `expo-gotchas.yaml`, `platform-quirks.yaml`, `recovery-playbook.yaml`) ship with the plugin and are initialized into `$HOME/.claude/<plugin>/` by a SessionStart `ensure-*.sh` script — establishing telemetry and candidates directories plus a scratchpad markdown file. Combines plugin-shipped seed data with user-side mutable state outside the plugin's data directory.

### User-visible markdown setup log

Plugin instructs the agent to read `~/Desktop/<plugin>-setup.md` first and append a `## Run — <timestamp>` section on each invocation. Setup is fully resumable across sessions; the human can inspect or edit the log directly. Uses a user-visible plain markdown file as workflow state — distinct from hidden caches or harness-managed state.

### Plugin-local `.local.md` with YAML frontmatter

Plugin reads/writes `.claude/<plugin>.local.md` (markdown body with YAML frontmatter) for iteration counters, escape protocols, and session-ID gating. Hidden but inspectable; persists across Stop-hook iterations within a session and across sessions. Used by the Stop-hook re-injection loop pattern.

### SQLite for behavioral metrics

`metrics.db` SQLite database under `${CLAUDE_PLUGIN_DATA}` tracks rule-violation events and corrections across sessions. Atomic writes; SessionStart queries trends and surfaces them as `Learning: <rule> fix rate <pct>%` in the session context payload. Persistence is local per-machine — no cloud sync. "Behavioral feedback loop" framed as a unique-in-the-ecosystem capability by the project's README.

### State-of-watcher files in `.github/last-checked-*.txt`

Repository-tracked state files (`.github/last-checked-version.txt`, `.github/last-community-scan.txt`, `.github/last-checked-api-date.txt`) act as durable cron-watcher checkpoints — "where did I leave off?" — committed back to the repo so the next cron run resumes correctly. CI enforces their existence as a structural invariant.

### Sidecar port-discovery file

Plugin's API server writes its actually-bound port into `~/.claude/data/<plugin>/api_port.txt` at startup; hooks read the file before each call to resolve the URL. An env var (e.g. `<PLUGIN>_API_URL`) overrides. Lightweight IPC contract — handy when port 8000 is taken; risky when two projects run concurrently because only one wins the file. Concrete bug reported in changelog where a hardcoded `.mcp.json` env var defeated the fallback.

### Three-file separation by consumer

Three files, each serving one consumer:

- A living-prose markdown document (e.g., `<tool>.md`) — human-facing and resume context for the agent
- An append-only JSONL log (e.g., `<tool>.jsonl`) — tooling consumption (dashboard, scoring, classification)
- A current-state JSON (e.g., `.<tool>.state`) — hook + statusline polling

Deliberate separation across format × access pattern. Each file's format matches its consumer's needs (markdown for narrative, JSONL for stream, JSON for poll).

### Runtime policy file tree

A directory tree under `.orchestrator/policy/` (or similar) holds runtime policies (`blocked-commands.json` with N rules, `quality-gates.schema.json` plus `.example.json`, `ecosystem.schema.json`). Hook reads the policy plus a per-session scope file (`wave-scope.json`); the contract between policy and hook is a JSON-Schema rather than inline rules in code. Pattern: pluggable policy JSON loaded per invocation. Lets the user (or the plugin's own session-start skill) edit rules without modifying hook source. Constrains schema evolution: any policy field rename requires updating both the schema file and every consuming hook.

## Sidecar daemon and IPC lifecycle

Whether the plugin runs a long-lived background process beyond the Claude Code session, and how it coordinates across sessions.

### No daemon — session-bounded only

Plugin process state lives entirely within the Claude Code session. No background server, no sidecar dashboard. Hooks are short-lived shell/script invocations; state persists via files on disk. Plugin is invoked per-call (CLI shim or MCP server started by Claude Code per tool call). No daemon, no `/tmp/` state, no refcount. Lowest operational footprint. Appropriate for skill-shaped plugins or stateless / per-invocation tools.

### Local Fastify HTTP daemon on a fixed port

The plugin runs a Node Fastify worker on `localhost:<port>` with multiple endpoints (e.g., `/api/version`, ingestion endpoints, query endpoints), auto-started by `scripts/worker-start.sh` from `session-start.sh`. PID + port files in the data dir. UserPromptSubmit hook checks the worker's `/api/version` against the installed plugin version on every prompt and kills+restarts on mismatch. A separate MCP server process runs alongside, both reading the same SQLite via per-call DB resolution. Goes well beyond "plugin is a directory of markdown + scripts" — it's a full long-running service. Architecture (worker + MCP server as peer processes sharing SQLite) is distinctive; significant operational complexity.

### Persistent FastAPI server with React dashboard UI

Plugin runs its own FastAPI process on a fixed port (e.g. 8000) and ships a React dashboard built into `plugin/dashboard-dist/`. Hooks forward events over HTTP to the FastAPI app; the dashboard consumes them. Sidesteps Claude Code's `monitors.json` mechanism entirely because the UI is served by the plugin's own HTTP server. Trades the tidy single-process model for a persistent-daemon architecture. Appropriate when long-running coordination state must survive across sessions and user-facing observability requires more than terminal output.

### Sidecar terminal observer with auto-split

Plugin invokes `scripts/forge-observer.mjs` from a SessionStart hook to launch a local auto-split terminal observer alongside the Claude session. Plugin-native concept named "observer" or "dashboard" — distinct vocabulary from Claude Code's `monitors.json` mechanism. Different surface area; same intent (visibility into long-running plugin state) achieved without Claude Code's monitor primitives.

### Refcount-gated daemon with /tmp/-resident state

A SessionStart bash hook is simultaneously a dep-install gate, daemon launcher, stale-state cleaner, and session registrar. The daemon (Python `python -m bridge` via the venv's interpreter, spawned with `nohup ... &`) is started once across N concurrent sessions: each session increments `/tmp/<name>.refcount` on start, decrements on end; daemon killed only at zero. Runtime files in `/tmp/`: `<name>.sock`, `<name>.pid`, `<name>.refcount`, `<name>.log`, `<name>.skip-stop.flag`, `<name>-turn-stats.json`, `<name>-bt-name.cache`. Appropriate for plugins backed by a shared resource (hardware device, service connection) that should be singleton across concurrent Claude Code windows. Constraint: hook does multi-purpose work; reading it for one concern reveals all four.

## Live monitoring

Whether the plugin uses Claude Code's monitor surface or alternative ambient-tick mechanisms — distinct from the sidecar daemon question.

### `monitors.json` absent

No `monitors.json` in observed samples. Notifications, when produced, flow through the hook system (Stop, SubagentStop, Notification, TeammateIdle) directly. The samples surface this is a real gap: a plugin literally named "notifications" does not use the documented monitor channel — anyone searching for monitor examples would miss it. Either the surface is too new, the plugins predate it, or none have a polling-style use case. Absent `monitors.json` may coexist with substantial live-notification machinery implemented at a different layer: PostToolUse-driven file writes plus a separately-installed status-line wrapper for live HUD updates; sound/vibration/display notifications routed through hook events to peripheral hardware; durable scheduled work routed to GitHub Actions cron with the plugin acting as the interactive author/debug surface; agent-invoked status commands (`/<plugin>:dashboard`, `/<plugin>:status`) the user runs interactively; sidecar daemons polled out-of-band; Claude Code's Monitor tool used directly inside agent commands as an alternative to declarative monitors. Constrains the plugin's ability to do truly background work without piggy-backing on hook events. Appropriate to flag as a corpus-wide observation: monitors may be under-adopted relative to their advertised role.

### `monitors.json` with single watcher

`monitors/monitors.json` declares one monitor (`<plugin>-session-monitor`) with `when: always` that polls workspace state for drift signals. Reuses the same hook-binary subcommand surface (`bin/<plugin> hook session-monitor`) so monitors and hooks share one binary and one dispatch plane. Version-floor declared in README ("v2.1.105+ recommended (PreCompact hook + monitors manifest)").

### Polling daemons via monitors.json

A plugin ships 2-3 monitor entries in `monitors.json`, each pointing at a `.py` script that polls a venue API at a fixed cadence (15s-15min) and emits one line per event. Schema fields used: `name`, `command`, `description`, `when`. `when` is `always` across all monitors observed; no `on-skill-invoke:<skill>` variant. Each monitor is a long-lived daemon launched at session start. Coupling: monitors are venue-coupled (a venue plugin ships them; venue-agnostic shared-layer plugins ship none even when they're heavier).

### Stop-hook driven desktop notification

A `Stop` hook runs `desktop-notify.js` after Stop events to fire macOS desktop notifications. Implemented at the hook layer rather than via a dedicated `monitors.json`. Appropriate when the plugin needs notifications but `monitors.json` isn't yet broadly adopted in the runtime. Constrains: notification delivery is OS-specific to whatever the script targets; multi-OS support requires per-OS handlers.

### Status line via user-settings mutation

The plugin ships a status-line script and provides a CLI subcommand (`<plugin> statusline install`) that mutates the user's `~/.claude/settings.json` to register the script. Plugin manifest does not declare statusline capability — the status line is "semantically a live monitor" (refreshes, shows context/quota usage) but implemented through the user-settings surface because the plugin manifest schema has no statusline component type. Pros: explicit user opt-in. Cons: uninstall does not automatically reverse the mutation; statusline registration outlives plugin removal unless the user runs `<plugin> statusline uninstall`. A `statusLine` entry can also be invoked from `.claude/settings.json` directly to render a per-session status line, updated reactively via PostToolUse hook on specific MCP tool calls. Dogfood-only variant: the `.claude/settings.json` lives in the plugin's own repo (for the author's dev sessions), not in `.claude-plugin/` shipped to consumers, so the status line is a developer-only artifact rather than a plugin feature.

### Status line as primary observability surface

Instead of a `monitors.json`, the plugin integrates with Claude Code's `statusLine` setting. A bash script (`bin/statusline.sh`) reads both the harness's session JSON on stdin and walks up to a project marker (e.g., `.git`) looking for plugin state files. Emits a single colorized line with a health glyph (●/▲/◆/⚕/✖/⏸), counters, streaks, durations, cost, context %. Auto-installed into the user's `.claude/settings.local.json` by a setup script. Composition via `--chain <prior-cmd>`: the statusline script accepts an existing statusLine command and delegates the raw session JSON to it before printing its own line, preserving prior configuration. Most plugins treat statusLine as a user-owned concern; this path claims it as a plugin surface and composes with prior values rather than replacing.

### Hook-driven file-write status line

No `monitors.json`. A PostToolUse hook writes status to `.<name>/state/hud.txt` and a Claude Code status-line integration reads from it. A SessionStart hook installs a wrapper script (`~/.claude/bin/<name>-hud.ts`) that discovers the newest installed plugin version under `~/.claude/plugins/cache/*/` and delegates. Decouples user-facing HUD from plugin upgrades — new versions provide new HUD scripts; the wrapper always finds the newest. Constraint: side-effect on the user's home directory not declared anywhere in the plugin manifest.

### Standalone terminal dashboard (out of plugin scope)

`bin/dashboard.sh --watch` runs as a user-invoked terminal dashboard in a separate shell. Not plugin-managed — the user starts and stops it; the plugin only writes the state files the dashboard tails.

### Hardware-device notification fan-out

Hook events fan out to a physical device (Flipper Zero) via a daemon socket — sounds, vibration, display text. Hook-event variety is used to discriminate notification cues at fine granularity. Includes events outside the canonical Claude Code hook list (`StopFailure`, `PostToolUseFailure`, `TaskCompleted`, `Elicitation`, `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`). Constraint: events that aren't yet emitted by a given Claude Code version silently no-op; no version-floor declaration.

### External-change watcher (shepherd pattern)

Cron-scheduled GitHub Actions workflows poll external sources (release pages, API changelogs, community forums) on a schedule (weekly Monday 09:00 UTC, monthly 1st 11:00 UTC). They do cheap detection only and open or update a single tracking GitHub issue per source; an `InstructionsLoaded` hook nudges the next session toward those issues. The Anthropic API changelog detector specifically fetches `.md` URLs (Mintlify convention) rather than scraping rendered HTML — deliberate stability choice. A simpler in-plugin form polls `npm view <package> version` at most once per 24h (cached at `$HOME/.cache/<plugin>/latest-version`, regex-validated as semver) and emits a non-blocking warning to the next session — loud multi-line block at ≥3-minor lag, mild one-liner otherwise. Replaces what `monitors.json` would do at the plugin level.

### Update notification mechanism

Skill body opens with a `## Preamble (run first)` block that the agent shells out on, invoking `bin/<plugin>-update-check`. The script polls a release endpoint, writes a status cache (with a TTL to avoid hitting the endpoint every invocation), and emits one of `UPGRADE_AVAILABLE`, `JUST_UPGRADED`, or nothing. The agent parses output and conditionally surfaces a notification. State coordination uses sentinel files in the data dir (`last-update-check`, `update-snoozed`, `just-upgraded-from`); the install hook writes some, the update-check reads and clears them. Constrains discovery to skill invocation: agents never invoking the skill never see the notification.

### Self-update advisory channel

Plugin script (`update-check.js`) hits `https://raw.githubusercontent.com/<owner>/<repo>/master/<plugin>/.claude-plugin/plugin.json` over the network, compares `.version` against the bundled value, caches the result in `~/.cache/<plugin>/update-check` with asymmetric TTLs (60 min for up-to-date, 720 min for available-update so a known update keeps surfacing for 12 h while a new release is detected within an hour). Emits `UPDATE_AVAILABLE <old> <new>` on stdout for the skill preamble to parse and surface to the user. Lightweight self-update notification that does not require marketplace infrastructure.

### Version-floor declaration absent

Where monitors are used, no plugin.json or README declares a minimum Claude Code version for the monitors feature. Repo-level docs may name a Claude Code version for unrelated features (a channels-preview floor) but not specifically for monitors.

### No update mechanism

Plugin ships no update poller. `/plugin update` re-fetches the marketplace entry but the plugin's runtime never proactively checks for new versions. Users discover updates through external channels (release feeds, social posts, the marketplace browse UI).

## Telemetry and self-evaluation

Whether the plugin emits structured events about its own lifecycle or grades its own output.

### JSONL append-only event logs

Telemetry, analytics, learnings, review events, and timeline entries are written as JSONL append-only files under the plugin's state directory. Bin tools (`<plugin>-telemetry`, `<plugin>-learnings-log`, `<plugin>-learnings-search`) emit and query these. Appropriate for a plugin that wants durable cross-session memory; constrains rotation and retention (no auto-pruning visible) and creates a deduplication problem when multiple async hooks may write the same event.

### JSONL append plus optional remote POST

A library (`scripts/lib/events.mjs`) writes structured events as JSONL appends to `.orchestrator/metrics/events.jsonl` (or similar). When an env-var secret (e.g. `<PLUGIN>_EVENT_SECRET`) is set, events also POST to a configurable webhook via native `fetch` plus `AbortSignal.timeout(3000)`; errors are swallowed so remote failures never affect local execution. Pattern: graceful optional remote telemetry. Local logging is always on; remote forwarding is opt-in by environment.

### Eval-gate as a CI job

CI runs the plugin's own evaluation harness (`bun run eval` or equivalent), parses score and critical-finding count out of stdout via grep, and fails the build on any critical findings. The plugin grades its own artifacts against its own rubrics on every push. Appropriate when the plugin's purpose is review/judging and the author wants meta-coverage; constrains stability because grep-of-stdout is brittle to eval output format changes and shifts to structured output (JSON exit) would harden the gate.

### Multi-hook recording pipeline → MCP server → read-only agent

A 4-hook recording pipeline (SessionStart, UserPromptSubmit, Stop, PostToolUse with selector and PostToolUse without matcher) feeds a single Python recorder that appends to a JSONL log, which is then flushed to a database (e.g., MongoDB) by a dedicated MCP server, which is then queried by a read-only agent constrained via `tools:` allowlist + `disallowedTools:` denylist. Five layers (hook → recorder → JSONL → MCP flush → agent) for workspace observability alone. A coherent subsystem within a single plugin: every layer is plugin-shipped, every boundary is explicit, and the read-only agent is a first-class consumer. Distinct from generic hook usage; closer to "observability as a plugin product axis."

### No telemetry

Plugin does not emit structured events. Diagnostic information lives only in stderr of hook invocations and log files the user inspects manually.

## Plugin-to-plugin coordination

Whether the plugin declares dependencies on other plugins via the manifest schema, relies on prose-only coordination, or relies on shared filesystem/event conventions.

### `dependencies` field absent

No `plugin.json` declares the schema-level `dependencies` field. Plugins are flat and independent. The `<plugin-name>--v<version>` git tag format (the cross-plugin pinning mechanism) is consequently not exercised — single-plugin marketplaces use plain `vX.Y.Z` tags, and cross-plugin contracts are enforced only by intra-plugin convention, not the runtime. Cross-plugin interactions (e.g., two plugins both connecting to the same external service via their own `.mcp.json`) are handled by convention rather than declared. Concrete failure mode: documented coordination without machine-enforcement — three plugins form a "knowledge ecosystem" coupled by README prose ("This plugin doesn't manage any store directly — it routes to <plugin-A> and <plugin-B>"), but a user installing only one of the three gets broken routing with no install-time error because no `dependencies` field exists to enforce the coupling.

### `dependencies` field declared

`plugin.json` carries a `dependencies` array. May be empty (`[]`), bare strings (`["foo"]`), or objects (`{"name": "foo"}`). Custom resolver code accepts both shapes. Appropriate when the marketplace has multi-plugin dependency chains. Constrains tooling — Claude Code's native `dependencies` field is platform-version-gated (v2.1.110+ per the docs), so pre-version consumers ignore the field entirely; resolver behavior depends on consumer version.

### Implicit prose-only dependency

README states "install plugin X first" or "this plugin doesn't manage any store directly – it routes to <other-plugin>" without expressing the relationship in any manifest. A function-specific plugin's skills reference MCP tools owned by a sibling core plugin; if the user installs only the function plugin, skills load but the tools they call are missing. Documentation is the only enforcement; failure surfaces at use time. README prose only — plugin requires the user to manually `/plugin disable <other-plugin>@<other-marketplace>` before installing in conflict cases. Coordination is by discipline, not structure.

### Implicit via filesystem convention

Plugin A reads files written by plugin B at a shared path (e.g., `~/.ai-sessions/spool/events.jsonl`) without any declared dependency. If B is not installed, A silently degrades (drift warnings stop firing, drift summary becomes empty, etc.). Appropriate when the dependency is genuinely optional. Constrains: there is no static signal of the coupling — install-time resolution can't detect that A would benefit from B.

### Implicit dependencies coded in installer

A self-installer hardcodes inter-module dependencies in source (`WRAPPER_REQUIRED_MODULES = new Set(["do", "omo"])` plus `WRAPPER_REQUIRED_SKILLS = new Set(["dev"])`) so selecting one module triggers `bash install.sh` for a shared binary. Not declarative; not visible to the marketplace consumer.

### Skill chaining via Stop-hook tail-grep

A `Stop` hook tails the last 200 lines of the transcript, matches the most recent skill invocation, and emits a `systemMessage` recommending the next skill in an intra-plugin DAG. Appropriate when the plugin's skills form an ordered workflow. Constrains: depends on a stable transcript-line format and accurate matching — observed inconsistency where one variant grepped the path string instead of file contents, so it never matched correctly.

### Content-level integration with sibling project

`plugin.json` has no `dependencies` field. Where the plugin integrates with another project (e.g., a methodology framework like BMAD), the integration is content-level — embedded artifacts under a directory prefix and a dedicated skill that consumes them — not manifest-level. If the other project ships as a Claude Code plugin in the future, a `dependencies` entry would be a cleaner binding.

### External-MCP install during bootstrap

The npm bootstrap CLI offers to install third-party MCP servers (Context7, LangChain Docs) via `claude mcp add` during plugin install, prompting the user interactively. The MCPs are not declared as plugin dependencies; their install is a side-effect of running the bootstrap. Constrains: only fires through the npx path, not through `/plugin install`, so marketplace-installed users miss the augmentation entirely.

## Testing

How the plugin verifies its own behavior — test framework, harness, runner discovery, placement, and coverage scope.

### No tests

Repo has no `tests/` directory and no test files. No round-trip validation of manifests, no smoke test of install scripts, no MCP-server registration test. Quality assurance is manual; release process is commit-to-main. CLAUDE.md may explicitly state "No test suite. The dev loop is: edit → reinstall the plugin → exercise skills manually." Manual validation steps documented as ad-hoc commands (e.g., `claude plugin validate .`, type-check via `uvx ty check <file>`). Verification posture leans on runtime hosts surfacing errors and on contributor-invoked review agents during authoring sessions. Manifest-correctness is trust-on-commit. Bug-detection burden falls entirely on consumers and human review. Common in personal/early plugins. Notable for first-party Anthropic-owned marketplaces of substantial scale — even at scale, plugins land at tip-of-main with manual review as the only gate. Pure aggregator marketplaces also ship no test code — there's no plugin payload to verify locally; all validation is at the aggregator boundary or in the upstream review pipeline.

### Tests referenced but absent in tree

The repo references tests in release-script docstrings (`scripts/publish.py` gate 6 expects `tests_dev/`) but no test directory is checked in. Either gitignored locally-only or the gate is dormant. Constrains the project's claimed test discipline to the maintainer's local machine. Or `package.json` declares a `test` script but no test sources are committed (tests stripped before sync from upstream). Constrains validation to whatever the upstream pipeline did before sync.

### Hand-rolled bash tests

The plugin ships `tests/*.sh` files with hand-rolled PASS/FAIL counters, `mktemp -d` fixtures, and `git init -q` scratch repos for git-state-dependent tests. Includes `assert_eq`, `assert_contains`, `assert_not_null` helpers. No top-level runner; each test file self-executes via `bash tests/<test>.sh`. Tests typically `source` the underlying library directly rather than invoking the bin wrapper, so wrapper-path bugs are untested. Coverage scope: workflow scripts and end-to-end phase flows; hooks themselves are documented as "test by piping JSON into the hook script" rather than scripted.

### Author-time validator agents instead of automated tests

A repo with no `tests/` directory documents in contributor docs a manual-validation pipeline: contributor runs `plugin-validator` and `skill-reviewer` agents (vendored from Anthropic's official plugin suite) after any component change. Validation is interactive, runs inside a Claude Code session, and depends on contributor discipline. Repo-level `.claude/settings.json` blocks `git commit --no-verify` and `git push --force` but no commit hook invokes the validators.

### Bash scripts under `tests/<platform>/` with no CI

Tests live as bash scripts under `tests/claude-code/`, `tests/codex/`, `tests/opencode/`, etc., plus standalone Python analyzers. Run manually by the maintainer; no GitHub Actions exercise them. Multi-platform layout signals testing intent without CI investment. Quality gap is visible — version sprawl across multiple files plus a YAML source-of-truth shows drift in practice (compiled artifacts at one version, source at an older version) that CI would catch immediately.

### Python unittest under pytest discovery

Tests use stdlib `unittest` (module-level classes); the discovery/runner is pytest invoked as `python -m pytest tests/ -v`. No `pytest.ini` or `[tool.pytest.ini_options]`; pytest's default discovery suffices. Appropriate when the project values stdlib-only test code but accepts pytest as the runner for its better output and discovery; the cost is the contributor must know that pytest will pick up unittest-style classes.

### Python unittest with explicit `unittest discover`

Tests run via `python -m unittest discover -s tests -p 'test_*.py' -v`. No pytest. Stdlib-only. Appropriate when stdlib-only is a hard policy; the cost is somewhat noisier output and slower test feedback compared to pytest.

### pytest with optional inline cov

Tests in `tests/` at repo root using pytest with `pytest-cov` and optionally `pytest-asyncio`. Pytest config either in `pyproject.toml` `[tool.pytest.ini_options]` (canonical) or absent (CI invokes pytest with inline flags). Tests cross the skill boundary — import skill scripts via `sys.path.insert` + `importlib.util.spec_from_file_location` when the skill code isn't a packaged module. Standard Python test posture.

### pytest with sys.path manipulation

`tests/` directory holds pytest test files; tests manipulate `sys.path` via `sys.path.insert(0, str(ROOT))` to locate the source tree because no installed-package layout is assumed. Pytest config may live in a dedicated `pytest.ini` (with `testpaths`, `python_files` patterns, custom markers like `network`, `claude`, `replay`, `browser`) or be omitted entirely. Appropriate when the plugin has Python code and the author wants tests to run against source, not the installed copy. Constrains debuggability: install-path bugs (e.g. console-script vs PYTHONPATH-pointed-at-src divergence) hide because tests bypass the install path.

### Pytest with marker-segmented suites

Pytest with markers (`integration`, `e2e`) routing tests into tiers. Default `addopts` excludes the heavier markers so bare `pytest` runs unit tests only. `tests/` at repo root, split into `features/`, `e2e/`, `utils/`. Adjacent markdown sidecars (`test_*.md`) appear next to some tests as human-written per-test documentation. Dependency declared via uv-native `[dependency-groups].dev`. Local invocation via `poe test-unit`/`test-integration`/`test-e2e` tasks (poethepoet). Pitfall: pytest `addopts = "-m 'not e2e and not integration'"` combined with markers named `integration` and `e2e` means a bare `pytest` silently skips a category developers may not realize is there.

### Pytest with asyncio support

`pytest` with `pytest-asyncio` declared in `[project.optional-dependencies].dev` of `pyproject.toml`. `[tool.pytest.ini_options]` configures `testpaths = ["tests"]`, `asyncio_mode = "auto"`, custom markers (e.g., `integration` for tests that hit real LLM APIs). Test runner invoked as direct `pytest tests/ -v` or with marker filters. Substantial test suites (multi-thousand-line files) can coexist without CI when integration tests require live API keys.

### Pytest scoped to one plugin within a marketplace

Tests live inside the plugin directory (`plugins/<name>/tests/{unit,integration,lint}/`) with a `conftest.py` that runs the plugin's main script as a subprocess via `sys.executable`, self-locating relative to the test file. The other plugins in the same marketplace ship zero tests. Pytest config relies on discovery defaults; tests assume invocation via the plugin's own Makefile, not a top-level runner. Pytest version floor (`pytest>=9.0.2`) tightly couples to a high Python floor (`>=3.14`).

### Stdlib-only Python rubric tests

Tests are zero-dependency Python 3.11 stdlib scripts (`tests/meta_review.py`, `tests/verify_snapshot.py`, `tests/verify_triggers.py`), invoked directly via `python3 tests/<script>.py`. No pytest, no test framework. Plus bash fixture-runner scripts for live-CLI tests. Test model is "structural-rubric + golden snapshots," not unit tests. Each rubric check has a stable ID (`M-C1`...`M-C16` Critical, `M-I1`...`M-I9` Important) referenced in CHANGELOG entries — CI-check-as-named-entity. Constrains contributors to write rubric checks in stdlib idioms; rationale: <30s runs, no supply-chain risk in CI itself, runnable locally without setup. Appropriate when the project privileges CI itself being trust-minimized.

### Smoke-only Python import + subcommand exercise

Single `smoke.yml` workflow runs `python -c "import hook_runner"` against canonical and packaged paths, invokes every CLI subcommand once (`audio-hooks.py test all` dispatches all 26 hooks), and runs a `--check` plugin-sync verification. Matrix across OS × Python versions (`ubuntu × windows × macos × 3.9 × 3.12 × 3.13`, fail-fast: false). Catches runtime regressions; does not validate schemas.

### Go test

Tests run via `go test -v -race -coverprofile=coverage.txt -covermode=atomic ./...`. Colocated `*_test.go` files alongside source per Go convention. CGO-enabled tests (`malgo` for audio) exercise `-race` across all OSes. Coverage uploaded to codecov with `continue-on-error`. Coverage threshold not enforced. Appropriate when the runtime is Go; the cost is platform asymmetry (CGO doesn't cross-compile cleanly to all arches).

### cargo test

Rust integration-test layout — `tests/` at repo root holds top-level integration test files (`crash_recovery_test.rs`, `doctor_test.rs`, `multi_venv_test.rs`, `smoke_test.rs`, `venv_detection_test.rs`) with shared fixtures under `tests/support/mod.rs`. Wrapped behind `make ci` (= `fmt-check` + `clippy -- -D warnings` + `cargo test`).

### Node `node:test` chained suite

Hundreds of `tests/<name>.test.js` files under one flat directory; each wired to a `test:<name>` npm script; the root `npm test` chains 70+ entries with `&&`. Sequential, ordering-load-bearing, single failure aborts the chain. Constrains parallelism (none) and ordering discipline (highly so). Plus a separate `prove:*` tier — seven scripts that emit machine-readable `proof/<area>/report.{json,md}` artifacts to GitHub Actions, distinct from the `test:*` tier. Appropriate at scale where the maintainer wants every behavior covered and accepts the long-chain trade-off; the `prove:*` tier supports post-hoc auditing of CI runs.

### Node `node:test` with multi-job CI

`node --test 'test/unit/*.test.js'` runs hundreds of tests against the in-plugin Node MCP server (located under a sub-path like `scripts/<server>/test/`, not repo root). CI runs three parallel jobs: TypeScript build, unit tests, and a separate `version-sync` job comparing manifest copies. No matrix — single Node version, single OS. Action versions pinned by tag (`@v4`), not SHA. Caching via setup-node's built-in npm cache with explicit `cache-dependency-path` to the sub-package's lockfile. CI does NOT run on tag push — release creation is fully manual. Integration tests are a thin slice of the test count; full E2E (simulator-driven) runs on the maintainer's dev box, not in CI.

### node:test with tsx loader

Node.js built-in test runner via `import { test } from 'node:test'` plus `node --import tsx/esm --test '<glob>'` for direct TypeScript execution. No third-party test framework. Pitfall: glob expansion under Windows bash may match zero files; CLAUDE.md documents an explicit-paths workaround.

### Multi-runner — `node --test` + bats

`node --test` (built-in Node test runner) for JS test files co-located with code (`worker/**/*.test.js`), plus `bats-core` (submodule-pinned) for shell-integration tests under `tests/*.bats`. Mixed runner per language. Submodule pinning the bats binary aims for reproducibility but introduces a "submodule not fetched" graceful-skip path that can mask CI gaps.

### Mixed `node:test` + pytest with custom runner

Primary tests use `node:test` via `tests/**/*.test.js`, executed by a custom `tests/run-all.js` that `spawnSync`s each file and aggregates pass/fail in an ASCII box. Python tests (pytest + pytest-asyncio + pytest-cov + pytest-mock) cover a Python sub-package via `pyproject.toml`'s `[project.optional-dependencies] dev`. Appropriate when the plugin spans Node and Python; produces robust coverage but requires the custom runner to coordinate. Constrains: in the observed sample, the custom runner only invokes Node tests — pytest is configured but orphaned from CI.

### Custom Node `node:test`-style runner with suffix discovery

Custom runner at `scripts/run-tests.mjs` discovers tests by directory + suffix convention (`hooks/*-test.js`, `mcp/*-test.mjs`), spawns each via `node <path>` sequentially, inherits stdio, aggregates exit codes. No Jest/Vitest dependency. Tests are plain assertion scripts co-located with the code they test. Tight discovery — a contributor adding `*.test.js` (dot, not hyphen) silently skips. Appropriate when avoiding test-framework dependency is a goal.

### vitest

Node plugins declare `"test": "vitest run"` with `vitest` devDep. Standard Node test runner.

### vitest with multi-suite layout

Vitest as the primary runner, configured via `vitest.config.mjs` to glob both top-level `tests/**/*.test.mjs` and nested skill-local `skills/*/tests/**/*.test.mjs`. Tests are organized into `hooks/`, `integration/`, `lib/`, `skills/`, `unit/`, `fixtures/` subdirs at repo root. Replaces an earlier bats-based suite. Direct invocation via `npm test` → `vitest --run`; typecheck delegated to a custom `node scripts/typecheck.mjs` rather than `tsc`.

### Multi-stack test setup (vitest + BATS)

Unit tests via vitest (1650+ tests at the sampled snapshot) with config at `vitest.config.ts`; shell-script integration tests via BATS, invoked as `bats tests/*.bats`. BATS installed at CI time via git clone + install script (not an action). Tests directories at `test/` (vitest) and `tests/` (BATS) coexist.

### bun test with TypeScript

`bun test` (Jest-compatible runner) executes `*.test.ts` files in a flat `tests/` directory. Appropriate for Node-toolchain plugins; constrains runner choice (locks the project to bun rather than node+jest or vitest).

### bats (Bash Automated Testing System)

`.bats` files in `tests/` exercising the plugin's CLI through bash assertions. Unit and e2e suites split into separate files; e2e requires `playwright install chromium` plus the plugin's env vars threaded through the runner.

### Bash scripts only

`tests/run-tests.sh` (or per-area `tests/*-test.sh`) as the entry point, with bash test files dispatching into subdirectories (`tests/hooks/`, `tests/ci/`, `tests/core/`, etc.). Or a single `tests/validate-plugin.sh` orchestrating ~60 individual `tests/test-*.sh` files. No pytest/jest/vitest. Pure-bash discipline; CLAUDE.md may explicitly note "No traditional unit tests (bash scripts only)." Suits plugins whose own runtime is shell-scripts; weak when test logic gets complex.

### Bash + Python helpers (no Python test framework)

Bash scripts as the test runner with Python used inline for YAML/markdown parsing within shell scripts (`python3 -c "import yaml; yaml.safe_load(...)"`). No pytest. Suits plugins that already require `python3` for runtime helpers — same dependency.

### Shell script tests (installer harness)

Bash unit tests (`bin/install_test.sh`) and end-to-end tests (`bin/install_e2e_test.sh`) for the install flow itself, with a Python stdlib mock HTTP server (`bin/mock_server.py`) standing in for GitHub Releases. Run alongside the language-native tests in CI. Appropriate when the install script is itself substantial logic that must not regress.

### Headless `claude -p` snapshot testing

A workflow runs the Claude Code CLI itself in non-interactive `--input-format stream-json --output-format stream-json --no-session-persistence --dangerously-skip-permissions --max-budget-usd <N>` mode against pre-seeded `stream.jsonl` user-turn fixtures, validating output against `expected-snapshot.json`. Per-fixture USD budget cap enforced by the CLI. Cost profiles documented in-tree (~$8–$12 per release). Constrains the testing budget to real money and exposes test results to model-variance. Appropriate when the plugin's core value is the methodology's behavior under a real model — unit tests cannot substitute.

### CI runs Claude against scenarios — meta-dogfood

The CI pipeline runs the real `anthropics/claude-code-action@v1` against a baseline (main) wizard and a candidate (PR) wizard, executing simulated SDLC scenarios and scoring compliance. Tier 1 (every PR): 1+1 simulation. Tier 2 (on `merge-ready` label): 5+5 evaluations with t-distribution 95% CI computed via `tests/e2e/lib/stats.sh`, emitting `IMPROVED`/`STABLE`/`REGRESSION` verdicts and a Robustness score. The plugin evaluates itself by running an agent against fixtures. Bootstrap mode handles the "no baseline yet" case.

### Hook integration test via piped JSON

CI integration job pipes a synthesized hook-event JSON to the compiled hook script and asserts `jq -e '.continue == true'` on the output. Drives a real round-trip (hook reads stdin, performs work, emits stdout JSON) without spinning up Claude Code. Appropriate for verifying hook output discipline; constrains to deterministic hooks (stochastic ones would need fuzz harnesses).

### `verification/` directory of per-story proof documents

A dedicated `verification/` directory holds proof artifacts per story or feature. Not test code; a product artifact tracked in git. A novel answer to "how does an agent prove a feature works" sitting at the boundary of agent tooling.

### Co-located test placement

Tests sit next to source files (`hooks/gate-sync-test.js` next to `hooks/gate-sync.js`, `mcp/router-test.mjs` next to `mcp/router.mjs`). Discovery happens via filename suffix. No central `tests/` directory. Appropriate when tests pair tightly with their immediate source and the project has no need for a global test root.

### Centralized `tests/` placement

All tests under a root `tests/` directory, often subdivided into `unit/`, `integration/`, `e2e/`. Plugin/code tree separate. Standard Python posture. Appropriate when tests are organized by category or scope rather than by source-file pairing.

### Retroactive CI as documented regression response

CI added in direct response to a specific shipped bug; CHANGELOG entry explicitly cites the regression that motivated each gate. Commit history reads as "no CI → broken tag → add CI gate that reproduces the bug" — clean case study of post-incident gate accumulation.

## CI workflow shape

What CI does on push/PR, how strictly it gates merges, and how the workflows are organized.

### No CI

`.github/workflows/` does not exist. Nothing verifies version-bump → tag → install path on each commit. Failures show up on user `SessionStart` only. Regressions are caught only when someone runs the test suite locally. Schema fixes appear as recurring entries in CHANGELOG (the cost signature of "no manifest-validation gate"). Tests exist locally but only run on a contributor's machine. The declared version has no automated validation. Appropriate when the project is single-author and pre-1.0; risk grows as contributors and release cadence grow.

### CI workflows present but no tests

`.github/workflows/` carries claude-action wrappers (`claude.yml` for `@claude` mention response, `claude-code-review.yml` on PR, `claude-skill-review.yml` on PR) plus a release workflow. None invoke a test runner; the LLM-driven reviews substitute for tests.

### Single workflow, OS × language matrix

One `.github/workflows/test.yml` runs the test suite across an OS matrix (`ubuntu-latest`, `macos-latest`, `windows-latest`) and a language-version matrix (Python 3.10/3.11/3.12 or Go 1.21/1.22). Triggers on `push` to `main` and `pull_request` to `main`. Steps: `npm ci`/`uv sync`, optional nested-skill installs, `npm run lint` (eslint), conditional `npm run typecheck`, `npm test`/`pytest`/`go test`. Actions SHA-pinned with tag annotations preserved as comments. Built-in `actions/setup-node` cache keyed on `npm`. `concurrency` group with `cancel-in-progress: true` supersedes queued runs on rapid push. Per-job `timeout-minutes: 15` and minimum-`contents: read` permissions. No linters, no type checkers, no manifest validators in this workflow. Appropriate when the test suite is cohesive and self-validating.

### Single-workflow validate + lint + eval-gate + convergence

One `ci.yml` runs four jobs: validate (install + skill checks + schema-validation + full test), lint (strict `tsc --noEmit`), eval-gate (self-eval grader), convergence (custom convergence test). Triggered on `push` and `pull_request` against `main`. Single OS, single runtime version pinned. Action versions tag-pinned (no SHA pinning). Appropriate when the plugin has many in-repo validators it wants to gate centrally; constrains supply-chain hygiene because tag-pinned actions can be moved by their authors.

### Two-job workflow — build-and-test plus validate-plugin

`ci.yml` runs on push and PR to default branches. Job 1 (`build-and-test`): `npm ci` → version-sync gate → `npm run build` → vitest unit tests → install BATS → `bats tests/*.bats`. Job 2 (`validate-plugin`): `python3 -c` JSON parse of `plugin.json`, required-field check (`name`/`version`/`description`), `bash -n` syntax check on subset of shell scripts. Pinned to `ubuntu-latest` + Node 20. No matrix. Action pinning by tag (`@v4`), not SHA. The shell-syntax glob may exclude critical directories (e.g., omits `hooks/*.sh`). `hooks/hooks.json` is not JSON-parse-checked; agent/skill/command frontmatter is not validated.

### Format + lint + test wrapper

`make ci` wrapping `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test`. Runs on `push: branches: [main]` and `pull_request` with `paths-ignore: ['*.md']`. Matrix is OS only (`ubuntu-latest`, `macos-latest`, `ubuntu-24.04-arm`); no MSRV check despite `Cargo.toml` declaring `rust-version`. Actions tag-pinned. Rust target/registry caching via `Swatinem/rust-cache@v2`.

### Per-OS workflow files (deliberate split)

Three CI workflow files (`ci-ubuntu.yml`, `ci-macos.yml`, `ci-windows.yml`) instead of one with `matrix.os`. Per-OS steps diverge significantly enough that splitting trades DRY for readability — Linux installs `libasound2-dev`, Windows uses `pwsh` for fmt check, macOS builds platform-specific sidecar binaries. Plus auxiliary workflows for signing smoke tests (`notifier-signing-smoke.yml`) and release builds. Appropriate when per-OS divergence is irreducible; the cost is duplicated boilerplate when shared steps must change in three places.

### Single-workflow with multiple jobs in a DAG

`.github/workflows/ci.yml` containing all validation jobs in a `needs:` dependency graph. A seed job (e.g., secrets-scan) gates all downstream work. Jobs cover: JSON parseability, hooks.json schema validation, plugin manifest schema, shell script syntax + executability + shellcheck lint, skill frontmatter, agent frontmatter, knowledge-base presence, test-runner, and a final summary job that fails if any upstream did. One file, full visibility, fragile against adding new components (new hooks require editing the script allowlist in CI too).

### Multi-workflow split by trigger and concern

Multiple workflow files split by trigger: `ci.yml` for PR validation, `release.yml` for tag pushes, `pr-review.yml` for ready-for-review automation, `weekly-update.yml`/`weekly-api-update.yml`/`monthly-research.yml` for cron shepherds, `benchmark-*.yml` for performance work. `concurrency` block on `ci.yml` with `cancel-in-progress: true` to prevent stale re-runs. Eight or more workflows total in an ambitious project.

### Multi-workflow with pytest matrix and security scan

Tests run against a Python version matrix (`3.12`, `3.14`); a separate `security.yml` runs `gitleaks/gitleaks-action@v2` on push and PR; a tag-triggered `release.yml` re-runs tests on `v*` tag pushes. Appropriate for Python-toolchain plugins that want to catch version-specific breakage early. Constrains workflow maintenance because the same checks duplicate across files.

### Multi-workflow with version matrix and SHA-pinned actions

Eight workflows (`ci.yml`, `e2e.yml`, `publish-pypi.yml`, `release.yml`, `docker-build.yml`, `codeql.yml`, `claude.yml`, `claude-code-review.yml`). `ci.yml` runs ruff format check, ruff lint, pyright type-check, pytest with junit XML + coverage; matrices Python 3.10 × 3.11 × 3.12 × 3.13 (`fail-fast: false`); ubuntu-latest only. `e2e.yml` brings up Docker Compose against the real upstream service. CodeQL scans Python source plus the workflow files themselves (`language: actions`) with `security-extended` queries, on a weekly cron. Caching: `astral-sh/setup-uv` with `enable-cache: true` (uv's GH-Actions backend); Docker uses `type=gha` buildx cache. `claude.yml` and `claude-code-review.yml` ship fully wired with credentials but triggers commented out and only `workflow_dispatch: {}` enabled — deliberate opt-in staging of Anthropic automation, easy to flip on later.

### Multi-job matrix with parallel test/validate/security/lint

`ci.yml` defines four parallel jobs — `test` (matrix-runs), `validate` (multi-validator chain), `security` (npm audit), `lint` (ESLint + markdownlint). Triggers: `push: [main]` + `pull_request: [main]`. Matrix is OS × Node × package-manager (e.g., `[ubuntu, windows, macos] × [18, 20, 22] × [npm, pnpm, yarn, bun]`, minus exclusions = ~33 lanes). `fail-fast: false`. Appropriate for plugins targeting wide cross-platform support. Constrains: matrix cost — minutes per lane × lane count = significant CI minutes per PR.

### Multi-OS Go test matrix plus daily cross-version run

`ci.yml` runs Go tooling on a `{ubuntu-latest, windows-latest}` matrix at PR time and adds macOS plus `{stable, oldstable}` Go on a daily schedule. Release workflow crosses six GOOS/GOARCH pairs. Plugin shims are validated only by `bash -n` parse checks at release time — never end-to-end. Action pinning via major tags (`@v4`, `@v5`), no SHA pins. `actions/setup-go@v5` with `go-version-file: go.mod` for implicit module caching.

### Multi-stack matrix CI (TS + Go + integration)

`ci.yml` with five-plus jobs: TypeScript (`bunx tsc --noEmit`, `bun run build`, `bunx vitest run`, `bun run lint`); Go (`go test -v -race -coverprofile=coverage.out ./...` per submodule, Codecov upload `continue-on-error: true`); Go-lint (`golangci-lint-action@v9`); cross-stack build verification (`--help` smoke test of compiled binaries); integration (drives hooks with piped JSON: `echo '{"hook_event_name":...}' | bun dist/hooks/<hook>.js | jq -e '.continue == true'`). Triggers on push-to-main + PR-to-main. Action-pinning by major tag uniformly.

### Rust matrix CI with paths-ignore for plugin surface

`ci.yaml` with fmt + clippy + test + audit + docs jobs. Test matrix `{stable, ubuntu-latest}`, `{MSRV-from-Cargo.toml, ubuntu-latest}`, `{stable, macos-latest}`. Triggers `push: branches: [main]` + `pull_request`, both with `paths-ignore: ["**.md", "LICENSE", ".claude-plugin/**", "skills/**", "hooks/**"]` — plugin-surface edits don't retrigger Rust CI. Caching via `Swatinem/rust-cache@v2`. No shellcheck or hook-script lint. Constraint: pure skill/hook iteration ships without CI signal of any kind on the shell scripts.

### Push + PR matrix CI

`.github/workflows/ci.yml` triggers on `push` to default branch + release branches and `pull_request`. Matrix `os: [ubuntu-latest, windows-latest, macos-latest]` with a fixed runtime version (Go 1.21). Action pinning at tag level (`@v4`, `@v5`) — no SHA pinning. Built-in cache via the runtime's setup action's defaults.

### Test workflow on push/PR plus scheduled jobs

`.github/workflows/test.yml` runs lint (e.g., `ruff check`) and `pytest tests/ -v` on `push: branches: [main]` and `pull_request: branches: [main]`. Additional workflows handle scheduled work (daily cron) or manual dispatch (release/launch). All workflows hard-code Python 3.12 and ubuntu-latest with no matrix; actions are pinned to major tags without SHA pinning; no caching. Trade-off: scheduled bot commits trigger test runs for no code change, burning CI minutes; could gate on path filters.

### Single workflow, sparse coverage

CI runs a few jobs: manifest lint, shell-lint, a partial test job that only exercises a subset of test files. Most of the test suite is not run by CI (e.g., 70+ JS test files visible in tree but only one subdirectory is actually executed). Massive coverage gap — typically the result of evolution outpacing CI updates.

### Test workflow with pinned actions, no caching

`.github/workflows/ci.yml` triggered on push and PR to `main`. Single ubuntu-latest job, single Python version. Inline `pip install pytest pytest-cov`. Runs `python -m pytest tests -v --cov=skills --cov-report=term-missing`. Actions SHA-pinned with tag comments. No caching; no lint; no manifest validation. Coverage is `term-missing` only — no codecov upload, no trend tracking. Minimal CI scope reflects "runtime is tested, manifests are trusted" posture.

### Split test + lint workflows with `|| true` permissive runs

Two workflows — `ci.yml` (test + dashboard typecheck) and `lint.yml` (ruff + eslint). Both trigger on push and PR to multiple branches. Test job pip-installs deps with `|| true` and runs pytest with `|| true` — failures don't fail CI. CI tolerates environment-caused pip failures without distinguishing them from genuine regressions; effectively a smoke check. Action pinning by tag (not SHA). Built-in `setup-node` cache for npm; no Python cache.

### Single-runner JSON validation only

One workflow (`validate-marketplace.yml`) runs on `ubuntu-latest`, Node 20, no matrix, performing only `node -e "JSON.parse(...)"` syntax checks on `marketplace.json` and each `plugin.json`, plus a custom version-sync script. Test suites (where they exist) are not invoked. Appropriate when the plugin payload is content-only (skills/agents) with no runtime to test. Constrains: defects in the payload (manifest fields the docs/tests describe but the live file omits) ship to consumers because no test job catches them.

### Single-job path-scoped CI for one plugin

Workflow scoped via `paths:` to one plugin's directory only — push/PR outside that path skips CI. Single `ubuntu-latest` runner, single Node version, no cache. Four chained jobs: syntax-check (node --check + JSON.parse on hooks/plugin/scripts manifests), unit-tests (bats), e2e-tests (bats with playwright + chromium installed), build-test (esbuild bundle exists and >1000 bytes — file-size threshold, not functional). Other plugins in the same marketplace get zero CI coverage.

### Minimal cloud CI

A single workflow that does one job — typically a webhook-style notify (e.g., `notify-marketplace.yml` fires `repository_dispatch` to a sibling marketplace repo when `plugin.json` changes). Linting, type-checking, and test execution live in pre-push hooks and release scripts, not in cloud CI. Constrains contributors who fork the repo without adopting the local hook setup — they get no quality gates at all. Appropriate when the maintainer trusts the local pipeline more than cloud CI and wants minimal cloud surface.

### Discipline-checking CI on push and PR

Workflows on `push: main` + `pull_request: main` run a custom rubric (e.g., `meta-review.yml` running `meta_review.py`, `verify_triggers.py`, `verify-sync-to-active.sh`). Targets methodology invariants — version-string parity, skill-count, frontmatter, registration-list drift — rather than the marketplace schema. Constrains the meta-rubric to be the gating contract; external `$schema` validation is not wired in even when declared. Appropriate when the plugin's invariants are richer than the upstream schema.

### Single PR-gatekeeper workflow

The only workflow is `close-external-prs.yml` triggered on `pull_request_target` opened/reopened. Uses `actions/github-script` to check the PR author's collaborator permission; if not `admin`/`write`, posts a canned redirect comment and closes the PR. No manifest validation, no tests. Appropriate for read-only mirrors with explicit anti-contribution posture. Constrains: zero protection against malformed sync-PR merges; a stale `source` entry with a missing directory was observed live.

### `@claude` mention responder

A general-purpose `claude.yml` workflow on `issue_comment`, `pull_request_review_comment`, `issues`, `pull_request_review` events, gated on `@claude` mention. Uses `anthropics/claude-code-action@v1`. Not validation per se — turns the repo into an agent-addressable surface for ad-hoc questions and patches.

### Organizational PR bouncer

A `close-external-prs.yml` workflow on `pull_request_target: [opened]` checks the PR author's collaborator permission level via the GitHub API and auto-closes any PR from non-admin/non-write users with a comment redirecting to a submission form. Disableable via repo variable. Implements org-wide submission gating as a workflow rather than as branch-protection rules — appropriate when admin-controlled merging needs an explicit "this is not the contribution path" signal at PR-open time.

### Sprawling autonomous workflows

The `.github/workflows/` directory hosts 30+ workflows including cron-driven autonomous loops (`daily-revenue-loop.yml`, `instagram-autopilot.yml`, `gtm-autonomous-loop.yml`, `ralph-loop.yml`, `self-healing-auto-fix.yml`). Orthogonal to plugin distribution but co-resident in the same repo. Constrains the repo's surface area dramatically; mixes plugin-distribution workflows with non-code automation. Appropriate only when the repo intentionally serves both as a plugin source and as an operations hub.

### Firmware-build-only CI

Single `build-fap.yml` workflow: `ufbt build` of a Flipper FAP firmware binary, artifact upload, conditional `softprops/action-gh-release@v2` when ref is a tag. Triggers `workflow_dispatch` + `push` with path filter `flipper-app/**` + `tags: '*'`. No pytest, no shellcheck, no manifest validation. Plugin code (Python bridge, hook scripts) ships green even when broken.

### Action-pinning conventions

Sampled choices: SHA-pinned with version comment (`peter-evans/repository-dispatch@<sha> # v4.0.1`), tag-pinned (`actions/checkout@v4`, `actions/setup-node@v6`), major-tag pinning (`@v4`, `@v5`). Even within one repo, conventions can be inconsistent (SHA on one action, tag on another). Constrains the security posture — SHA pinning resists hostile-tag substitution; tag pinning trusts the action publisher. Appropriate when supply-chain risk is taken seriously and the workflow surface is large; constrains: pin updates require re-fetching the SHA at every version bump; tooling like Dependabot can automate.

### CI-trigger-as-signal-of-traction

Documented case: CI was added specifically because the repo got "3 GitHub stars within 24h of publishing." Adoption signal flipped the cost/benefit on adding CI. Captures the pattern: small projects defer CI until a traction signal appears.

## Pre-commit and pre-push hooks (git)

Whether git hooks enforce discipline at commit time.

### `.pre-commit-config.yaml` with linters only

Pre-commit hooks run `ruff --fix` on script directories and `python3 -m compileall` on Python source. No version manipulation, no manifest validation. Appropriate as a low-overhead floor; constrains because anything beyond syntax+style (version sync, manifest schema) is left to CI.

### Multi-tool pre-commit including pytest

`.pre-commit-config.yaml` runs ruff format check, ruff lint, pyright type-check, pytest (`uv run pytest tests/ -v`), plus basic hygiene hooks. Pytest at commit time is unusual — most projects pre-commit ruff/format only — and forces every commit to pass the unit suite. Costlier per commit but catches breakage at the lowest-friction point. Plus standard hygiene (trailing whitespace, end-of-file fixer, etc.).

### Process-ancestry-verified pre-push gate

`scripts/pre-push` walks the process tree via `ps -p <pid> -o args=` to confirm `scripts/publish.py` is an ancestor process, rejecting pushes to main otherwise. Rationale: env-var/marker-file schemes are "trivially spoofable"; an ancestry check enforces release-discipline without trusting any mutable signal. Constrains all main pushes to flow through the release script. Appropriate when release discipline is non-negotiable and the maintainer accepts the rigidity.

### Absent

No git hooks committed. No commit-time enforcement. Commits land regardless of test or lint state. The implicit gate is the author's local discipline. Appropriate at pre-release maturity; constrains because manifest drift and version drift have no commit-time gate.

## Ecosystem health automation

Dependency updates and security scanning beyond bare CI.

### Dependabot + CodeQL + grouped updates

`.github/dependabot.yml` weekly updates for `pip` (grouped minor+patch into a single PR labeled `minor-and-patch`) and `github-actions` (SHA bumps for the SHA-pinned action references). CodeQL scheduled weekly with `security-extended` queries scanning Python source plus workflow files themselves (`language: actions`). Reduces PR churn while keeping the supply chain monitored.

### None

No Dependabot config, no CodeQL workflow. Dependency updates are author-discretion only.

## Marketplace validation

Whether anything programmatically checks `marketplace.json`, `plugin.json`, `hooks.json`, frontmatter, and SHA-pin staleness for shape and consistency.

### No validation

No CI step validates manifest shape, version agreement, or frontmatter conformance. A bad commit corrupting these files would not fail CI — it would fail at install time on the user's machine. Type checking via pyright or similar runs only in the developer's editor with no enforcement gate. Validation relies on Claude Code's load-time checks plus manual testing. Manifest regressions surface only at install time on a real Claude Code session. The `$schema` reference (when present) points at the canonical Anthropic schema URL but no build step fetches or validates against it. Frontmatter on agents / skills / commands is unvalidated. Hooks.json correctness is implicit. Drift between marketplace `description` and per-plugin `plugin.json` `description`, missing `version` fields on some `plugin.json`s, non-semver shorthand like `"1.1"`, missing-SHA entries, inconsistent field sets, author-name mismatches between nested manifests, placeholder `owner.email: "your-email@example.com"` shipping to production — all would be caught by schema validation but aren't. Pure-aggregator workflows do no manifest parsing; they rely on an internal review pipeline (private to the marketplace owner) to gate entries before merge — public-facing repo has no recovery if the upstream gate misses something. Hook files using non-existent event names ship without complaint and never fire at runtime. Most low-investment plugins land here.

### `jq` parseability + name-equality assertions

CI runs `jq empty` against every JSON manifest (parseability) and `jq` queries asserting `name` fields are equal across plugin.json, marketplace.json's plugins entry, and any other manifest slot. Cheap; doesn't validate schema (no check that `timeout` is a number, no check that `command` correctly substitutes `${CLAUDE_PLUGIN_ROOT}`). Notable failure mode: name-equality may not cover every manifest in a multi-manifest layout; the unguarded one is precisely the one that drifts.

### Inline Python validators in CI YAML

Heredoc Python scripts inside `ci.yml` step bodies validating: hook event names against an allowlist set, hook types in `["command", "agent"]`, agent `model` in `["haiku", "sonnet", "opus"]`, plugin manifest required fields, semver regex on version. Most thorough hooks validator surface observed. Drawback: validator changes appear as ci.yml diffs, which is worse for review than tracked Python files. The validator itself can lag the runtime — a patch release was specifically needed to add 4 new hook events to the allowlist after the runtime accepted them.

### Frontmatter validation by grep

`grep -q "^name:"` / `grep "^model:"` against `skills/*/SKILL.md` and `agents/*.md`. Catches missing fields; misses YAML quoting issues, multi-line descriptions, partial matches. Cheap; partial.

### YAML safety regex sweep

CI greps workflow YAML files for unsafe `${{ }}` interpolation patterns, blocking specific shapes that have caused production breakage. Watch-for-regressions guard that evolved from prior incidents; documented in CHANGELOG. Defense-in-depth around shell-injection through GitHub Actions expressions.

### Custom in-repo validator

`tests/validate-plugin.sh` (39-item structural check) plus `scripts/ci/check-consistency.sh` (templates/refs/version/hooks) run on every PR and push. Predates the public `claude plugin validate` CLI; project has not migrated. Validators are project-specific assertions, not schema validation against the public spec.

### Custom verify command (existence-only)

A plugin-specific CLI verb (`<cli> verify`) shells through the layout and asserts that required files exist (`.claude-plugin/plugin.json`, `hooks/hooks.json`, adapter manifests). Does not check JSON schema conformance, version agreement, or frontmatter validity. Run as a CI step alongside tests. Appropriate when the project's primary risk is "deleted file" rather than "malformed file"; the cost is the false confidence that a plugin "passes verify" might give.

### Implicit via runtime exercise

CI invokes the plugin's CLI test surface (`<plugin> test all`) which dispatches every registered hook. If `hooks.json` points at a nonexistent handler, the test fails. Catches reference integrity but not schema drift.

### External validator referenced by name

A third-party tool (`cpv-validate` / claude-plugins-validation) referenced in release-script docstrings as the schema validator. Not vendored; fetched per gate; depends on network availability on release day. Constrains release-day reliability to the validator's host being up. Appropriate when the validator is genuinely shared infrastructure across the ecosystem.

### Custom rubric covering methodology invariants

A bespoke `tests/meta_review.py` (or equivalent) checks version parity, frontmatter validity, skill-count, marketplace.json internal consistency, trigger-phrase drift, hook-sync drift. Treats the marketplace schema as a side concern (the `$schema` link is declarative only). Constrains the validator surface to whatever the rubric covers; a strict schema validator would catch different things. Appropriate when methodology invariants are higher-value than schema conformance.

### Cross-manifest version-sync as validation

A drift-detector script (`sync-version.js --check`) is invoked from CI, pre-commit, and publish workflows. It validates that `package.json`, `plugin.json`, `marketplace.json`, `server.json`, README badges, etc. all carry the same version. Constrains every contributor to use the writer-mode of the same script (or to update all manifests by hand and accept the gate).

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

### Local-only validation, no cloud gate

Manifest validation lives entirely in pre-push hooks and the release script. PR branches run only feature-branch gates (lint + JSON parse). Constrains validation to the maintainer's discipline; contributor PRs ship with weaker checks. Appropriate when the maintainer is the only release author.

### Homegrown validators not wired to CI

Repo-local scripts (`scripts/validate-plugin.sh`, `scripts/validate-wave-scope.sh`, `scripts/validate-config.mjs`) plus a frontmatter validator with its own test suite (`tests/lib/agent-frontmatter.test.mjs`) exist but are not invoked by CI workflows. Library-internal use only. "Defense in depth but no enforcement at the marketplace manifest layer."

### Custom skill-frontmatter linter, not CI-wired

A `scripts/validate-skills.ts` (or similar) implements an inline YAML-frontmatter parser and validates SKILL.md files for required fields (`name`, `description`, `triggers` non-empty array), no duplicate names, basic markdown sanity. Run manually via `bun run scripts/validate-skills.ts`. Not invoked by any CI workflow.

### Manual validator-agent invocation

A contributor runs an interactive validator agent (`plugin-validator`, vendored from Anthropic's official plugin suite) after any component change. The agent reads manifests and skill frontmatter and reports issues conversationally. Trigger is manual; correctness depends on the contributor remembering to invoke. Frontmatter validation is delegated to a separate `skill-reviewer` agent.

### CI-gated minimal validation (plugin.json fields + shell syntax)

A `validate-plugin` CI job parses `plugin.json` JSON, checks required fields (`name`, `version`, `description`), and runs `bash -n` against curated shell-script globs. No frontmatter validation, no `hooks/hooks.json` validation, no formal JSON-schema validation. Limited but better than nothing; missing surfaces ship undetected.

### JSON well-formedness only

CI `syntax-check` job runs `node -e "JSON.parse(...)"` on `hooks.json`, `plugin.json`, and `scripts/package.json`. Catches malformed JSON; no schema conformance check, no event-name validation, no unknown-field detection.

### Manual validation only

`claude plugin validate .` documented in CLAUDE.md as a developer's local step; not gated in CI.

### Tiered validator driver

A single Python driver (`validate_all.py`) accepts `--tier {commit,push,ci}` and runs different validator subsets at each tier, with CI running all three sequentially. Drives 15+ underlying validators (frontmatter, structure, links, references, doc-structure, etc.). Constrains readers — the tier-to-validator mapping lives only in the driver source, not in the workflow YAML.

### In-editor skill (no CI)

A `/dev:validate` skill the author runs in-editor before `/dev:release`. Checks frontmatter, version sync between `package.json` and `plugin.json`, Python AST parse on tool files, executable bit on hook scripts, JSON validity of `hooks.json`, cross-references between skill `subagent_type:` and agent files. Validation is human-triggered; contributors without the skill ship blind.

### Runtime-only validation via jsonschema

`config.schema.json` exists in repo and a legacy installer (`install.py`) uses Python `jsonschema` to validate `config.json` at install-time on the user's machine. Not enforced in CI; a malformed config can be committed and only fails when a user runs the legacy installer.

### Hardcoded script allowlists in CI

CI's `validate-shell-scripts` job and the ShellCheck step list specific scripts by path (`hooks/<name>.sh`, `tests/run-tests.sh`). Adding a new hook requires editing `ci.yml` too. Fragile; surfaces as CI no-ops for new files.

### Schema validators that lag the runtime

The hooks-event-name allowlist in CI predates the runtime's acceptance of new events (PostToolUseFailure, SubagentStop, PreCompact, PostCompact). A patch release of the plugin added these to the allowlist after the runtime started accepting them — validator-as-second-source-of-truth lagging the actual runtime.

### Knowledge-base presence checks with subtle bugs

`validate-knowledge-base` job checks for directory presence and counts files but never compares the count to a minimum, so an empty knowledge directory still passes the existence check. Latent gap that looks like coverage.

### Script-based source linting (regression guard)

A maintainer-authored script (e.g. `sync-versions.sh`) regex-scans source files for forbidden patterns (hardcoded version literals, etc.) as a regression guard. Not full schema validation — targets specific known-bad patterns. Runs in pre-commit and CI for cross-checking.

### Plugin diagnostics surface

A `commands/<plugin>/doctor.md` slash command (or skill of the same name) walks installation diagnostics: node-on-PATH, plugin root resolved, MCP launcher generation, dependencies installed, server connectivity, project init state. Designed for the user to run after install to surface configuration problems. Appropriate when the plugin has multi-step bootstrap that can fail at any of several points. Distinct from CI-time validation: this runs at user invocation against a real install, not at PR time.

### No diagnostic surface

Plugin ships no diagnostic command. Users debug install failures by reading hook stderr or running scripts manually. Appropriate when the plugin's surface is small enough that failure modes are obvious.

## Source-pin maintenance

Keeping `git-subdir` SHA pins fresh over time without manual labor.

### Scheduled bot-PR with fairness ordering

A `bump-plugin-shas.yml` workflow runs on cron (weekly), iterates pinned `git-subdir` entries, queries each upstream for the latest commit on the pinned ref (respecting `path` scope), sorts by `-age_days` so the oldest-pinned entries roll first ("prevents starvation under the cap"), applies up to N bumps per run (default 20, configurable), and opens a single bot-signed PR. Concurrency is enforced via label-based check (`gh pr list --label sha-bump --state open`) so at most one open bump PR exists at a time. Force-pushed-away SHAs and 404s are categorized as "dead" without blocking other bumps. Permissions live on a GitHub App (org policy bars `GITHUB_TOKEN` from creating PRs).

## Release automation

How tag pushes, GitHub releases, or other automation cut releases — versus hand-cut releases without automation.

### No release automation / manual

Releases are bare git tags on `main` (sometimes with a hand-created GitHub Release). Tag-name discipline is human: name the bump commit, push the tag. CHANGELOG.md is the only narrative, but no automation consumes it. No `softprops/action-gh-release`, no `release-please`, no `semantic-release`. No tag-sanity gates verify `plugin.json` version matches the tag, that the tag is on main, or that anything was tested before tag time. `CHANGELOG.md` versioned headings without git tags or GitHub releases — no pinnable artifact. Releases produced via GitHub UI or `gh release create`. CHANGELOG.md may follow Keep a Changelog format with rich per-release sections. Drift symptoms: tags without published Releases, missing tag numbers, mismatched `plugin.json.version` and tag name. Tag count substantially less than version count when high-cadence on-main bumps ship through the marketplace without a corresponding tag. Appropriate for low-volume releases and small audiences; the cost is no automated tag-vs-version sanity gate.

### Tag-driven version-bump script with no GitHub Actions

A project-local script (`scripts/bump-version.mjs`) bumps versions across `plugin.json` and `marketplace.json` in one operation, but tag creation and release publishing remain manual. The script enforces version-file sync but not tag-vs-manifest alignment. Failure mode: contributor commits feature work after a tag without bumping, leaving `plugin.json` temporarily behind reality. Variant: contributor runs `scripts/bump-version.sh <new>`, commits, manually `git tag`, and `git push origin main && git push origin <tag>`. The script's tail prints the next-step instructions. GitHub Releases (when present) are created via the GitHub UI, manually copy-pasting from CHANGELOG.

### Tag-triggered test verification only

A `release.yml` workflow triggered on `push: tags: ['v*']` re-runs tests but does not build artifacts, create GitHub releases, or publish anywhere. The workflow header explicitly disclaims: "manual marketplace steps still required." Appropriate as a sanity check over manual releases; constrains the release process because tag-on-main verification, version-equality checks, and tag-format regex are absent — a tag from any commit passes if tests pass.

### Tag-triggered cross-build with CHANGELOG awk extraction

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`, cross-builds platform binaries (Go), and attaches them to the GitHub Release. Release notes body is extracted from `CHANGELOG.md` by an awk script that grabs the section between `## [VERSION]` and the next `## [` heading. Workflow first checks whether an external tool already created the release — if so, only refreshes binaries via `gh release upload --clobber`; otherwise creates the release itself as a safety-net. Inverts the usual "workflow IS the release mechanism" pattern.

### Tag-triggered cross-compile + asset upload

`.github/workflows/release.yml` triggered by `push: tags: ['v*']`. Cross-compiles the binary to multiple targets (e.g., `aarch64-apple-darwin`, `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`), installs cross toolchains for non-native targets, renames outputs to platform-tagged asset names (`<plugin>-macos-arm64`, `<plugin>-linux-x86_64`, `<plugin>-linux-arm64`), and uploads via `softprops/action-gh-release@v1` with `generate_release_notes: true`. No tag-sanity gates. Action pinned to a major tag rather than a SHA.

### Tag-triggered prebuilt-binary matrix

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`. Matrix builds a Go binary for 6 OS/arch combinations with `CGO_ENABLED=0` and `-ldflags="-X .../version=${VERSION}"` to stamp the version. Uploads all artifacts plus install scripts via `softprops/action-gh-release@v2`. Release notes generated inline via `git log ${PREVIOUS_TAG}..${TAG} --pretty=format:"- %s (%h)" --no-merges` — bypasses the project's CHANGELOG.md. No tag-sanity gates: no verify-tag-on-master, no verify-tag-matches-package-version, no tag-format regex.

### Tag-triggered binary build + GH Release with signing

Workflow triggers on `push: tags: ['v*']` and runs a multi-job pipeline: per-platform binary build (CGO_ENABLED=1 with stripped/trimmed flags), platform-specific signing/notarization (Apple Developer ID for macOS app bundle), checksum generation, GitHub Release creation via `softprops/action-gh-release@v1` with auto-generated notes, and a post-publish smoke test that re-downloads the released asset and runs `<binary> version` on each OS. No tag-format regex gate, no tag-equals-plugin-version verification. Appropriate when the release artifact is a compiled binary with platform variants; the cost is platform-specific secrets management (Apple cert P12, password, team ID) and post-release smoke testing being a verification rather than a gate.

### Tag-triggered with sanity gates and `--generate-notes`

Workflow on `push: tags: ['v*']`. Two sanity gates: (a) `git merge-base --is-ancestor HEAD origin/main` to assert the tag is on main; (b) tag value (`${GITHUB_REF#refs/tags/v}`) must equal `package.json.version`. Failure aborts publish with targeted `::error::` messages. Then runs `npm publish --provenance` (sigstore via `id-token: write` permission) and `gh release create "$TAG_NAME" --generate-notes` (release notes from PR titles since last tag, NOT from CHANGELOG.md). Gates do not check that tag matches `plugin.json` or `marketplace.json` versions — drift between npm and plugin metadata still possible. `fetch-depth: 0` on checkout required for the ancestry gate.

### Tag-triggered release with multi-gate sanity (npm)

`release.yml` triggers on `push: tags: ['v*']`, runs three gates — tag format regex (`^v[0-9]+\.[0-9]+\.[0-9]+$`, no pre-release), tag-equals-package.json-version comparison, and a manifest-sync test (`plugin-manifest.test.js`) — then conditionally `npm publish --access public --provenance`, then creates a GitHub Release via `softprops/action-gh-release` with `body_path: release_body.md` (a heredoc'd template) plus `generate_release_notes: true`. Idempotency: `npm view ${NAME}@${VERSION}` gates the publish step. Appropriate for npm-published plugins with strong release-engineering needs. Constrains: the templated release body adds little over auto-generated notes (anti-pattern signal); cross-manifest version sync is only verified for one of the many version-bearing files.

### Triple-target publish on single tag (PyPI + MCP Registry + Docker)

On `push: tags: ['v*']`, three workflows fire concurrently: PyPI publish via `pypa/gh-action-pypi-publish` with OIDC trusted publishing (no stored secrets); a TestPyPI sub-job conditional on `contains(github.ref, '-rc')` routes pre-releases to TestPyPI; a fourth job authenticates to the MCP registry via GitHub OIDC (`./mcp-publisher login github-oidc`) and rewrites `server.json` in the ephemeral checkout with `jq` before publishing. GitHub Release via raw `gh release create --generate-notes --notes-start-tag $(git describe --tags --abbrev=0 ${ref}^)` — auto-computes previous tag for changelog range. Multi-arch Docker (amd64+arm64) via `docker/setup-qemu-action` + `docker/setup-buildx-action` + `docker/metadata-action` computing a six-form tag set; single-arch validate (curl `/health` retry loop) before multi-arch final build; only pushes on `refs/tags/v*`. Tag-form fragility: `release.yml` and `docker-build.yml` lack the `-rc` filter that `publish-pypi.yml` has, so a pre-release tag also cuts a GitHub Release and pushes a `latest` Docker image — `latest` would leak an rc build. The MCP-registry job rewrites `server.json` in-checkout but doesn't commit it back; if local source-of-truth disagrees with the tag-derived value, the registry silently wins for that publish.

### Multi-target release pipeline (npm + cross-repo marketplace dispatch)

`release.yml` triggers on `release: [published]` (GitHub Release event) or `workflow_dispatch` with a `tag` input. Three jobs: `test` (re-runs CI flow plus `npm run lint` and size guards), `publish-npm` (`npm publish --access public --provenance` via OIDC trusted publishing — no `NPM_TOKEN`), `marketplace` (cross-repo `repository_dispatch` to the aggregator with `MARKETPLACE_TOKEN`). Manual `gh release create` is load-bearing — tag push alone does not ship. The `publish-npm` job re-runs `npm ci` + `npm run build` rather than consuming an artifact from the `test` job. Cross-repo dispatch token coupling means a forked user cannot release without the aggregator-scoped PAT. Split runtime: `test` on Node 20, `publish-npm` on Node 24.

### Multi-trigger workflow with single-snapshot path

One `release.yml` (28 KB) handles PR CI, main-branch snapshots, and tag releases by gating jobs on `needs.prepare.outputs.is_release` and `github.event_name == 'push'`. `prepare` job computes version (from tag or from `git describe`), then test → build (six-platform matrix, CGO + zig cross-compile, UPX compression on linux/windows-amd64) + build-web + build-grammars (per-language tree-sitter `.so`/`.dylib`/`.dll` from upstream-cloned grammar repos at pinned tags) + build-npm. Tag push → `release` job (softprops/action-gh-release@v2 with `generate_release_notes: true`) + `publish-npm` (`npm publish --provenance --access public` requiring `id-token: write`). Main push → `snapshot` job (delete + recreate `snapshot` tag + prerelease release). `prepare` includes "commit already has release tag — skip" check via `git tag --points-at HEAD` regex. Constraint: snapshot tag force-recreated on every main push; consumers caching by tag SHA see silent moves.

### Dual-workflow split (CI + release)

Separate `ci.yaml` (lint/test/audit) and `release.yaml` (cross-compile + GitHub Release). Release triggers `push: tags: ["v*"]`. Build job: matrix over arch targets, `taiki-e/upload-rust-binary-action@v1` with `dry-run: true` to produce archives, `actions/upload-artifact@v7` to stash. Release job: download artifacts, `taiki-e/create-gh-release-action@v1` with `changelog: CHANGELOG.md` (parses Keep-a-Changelog format), `gh release upload <tag> artifacts/*`. Constraint: asset URL pattern (`mm-<target>.tar.gz`) is hardcoded in the bin shim; release-action default-naming changes break the shim silently.

### Tag-conditional step inside build workflow

No dedicated release workflow. Build workflow has a `if: startsWith(github.ref, 'refs/tags/')` step using `softprops/action-gh-release@v2` to attach the built artifact. Default GitHub auto-generated release notes (no body provided to action). Tag pattern `*` is permissive — any tag fires. Constraint: no tag-format gate, no version-match check; an accidental tag publishes a release.

### Local-script release pipeline

A maintainer-machine-only Python script (`scripts/publish.py`) orchestrates 15 mandatory gates: tool availability, pre-push hook, clean tree, lint, type-check, py_compile, tests, schema validate, atomic version bump, schema re-validate, CHANGELOG regen via `git-cliff`, release commit, annotated tag, push (gated by ancestry check), `gh release create` with notes from CHANGELOG. Process-ancestry pre-push gate (walks `ps -p <pid> -o args=` rejecting any push not driven by the script) prevents the gate from being bypassed. Constrains the release to the maintainer's working machine; no cloud audit trail; depends on local toolchain (uvx, git-cliff, gh CLI, uv) being correctly installed. Appropriate when the maintainer privileges total local control over cloud reproducibility.

### Path-filtered cloud publish workflow

A workflow on `push: main` with `paths` filter targeting only `package.json`/`package-lock.json`/`server.json`/the workflow file. Tag creation moves *inside* the job, conditional on a decision script's output (`scripts/publish-decision.js`). Multi-trigger: `push: main` + `release: published` + `workflow_dispatch`. Constrains a maintainer to bumping `package.json` deliberately to fire the workflow; non-bump commits don't ship. Appropriate when the publish discipline is "bump = release" and main has high commit cadence on non-shipping changes.

### Skill-zip build via filesystem glob

A workflow triggered on `v*` tags globs `*/`, gates on `SKILL.md` presence, zips each matching directory as `<dir>-<tag>.zip`, attaches all zips to a draft GitHub release. Discovery is filesystem-driven, not marketplace-driven — adding a SKILL.md-bearing directory automatically ships a zip on next tag, even if that directory isn't a marketplace-listed plugin. MCP-only plugins produce no zip (they're consumed in-place via `plugin.json`). `softprops/action-gh-release@v1`, `draft: true`, `generate_release_notes: true`. No tag-sanity gates beyond the `v*` glob. A variant iterates directories matching `*-skill/` specifically and constrains naming convention: skill plugins must end in `-skill/` to be released.

### Cross-compile binary release with multi-target packaging

A `release.yml` triggered on `v*` tags cross-compiles a Go binary across six GOOS/GOARCH pairs, packages tar.gz (POSIX) / zip (Windows) including a generated shim inside each archive, uploads via `softprops/action-gh-release@v2`, computes sha256 checksums, then synthesizes a Homebrew formula via heredoc and pushes it to a sibling tap repo. Substantial automation; the plugin is one of multiple distribution channels.

### Plugin-tagged release with stamp-from-tag

A `release-plugin.yml` triggered on `plugin-v*` tags validates the plugin tree (file existence, JSON lint, `bash -n` parse), stamps `plugin.json.version` from the tag using a Python one-liner, packages a tarball, computes sha256, creates a GitHub release. Tag-to-manifest equality is enforced one-way at release time. Validation only fires at release; pre-merge structural drift sits latent on `main` until a tag is pushed.

### Manual release commit with bump script

No release workflow; the contributor runs `scripts/bump-version.sh <new>` (which patches version across many files), commits, manually `git tag`, and `git push origin main && git push origin <tag>`. The script's tail prints the next-step instructions. GitHub Releases (when present) are created via the GitHub UI, manually copy-pasting from CHANGELOG. Many tags accumulate with no automation to guarantee tag == plugin.json version — silent failure mode.

### Silent-no-op regression detector

A guard step in publish workflows that fails CI when the version is already on the registry *and* the shipped-files allow-list has commits since the last `v*` tag. Encodes a specific past regression class ("version published, content changed but not shipped"). Constrains every commit to either bump version or not touch shipped files. Appropriate as a defense-in-depth step where a known regression class has burned the maintainer.

### Post-publish runtime smoke

After `npm publish`, a workflow step pulls the freshly-published tarball *back from the registry* (`prove-packaged-runtime.js --package-spec "<name>@<version>" --install-attempts 12 --install-delay-ms 10000`) and smoke-tests it. Retries handle CDN propagation. Closed-loop: "publish verified only when the thing downstream users would pull actually works." Constrains the publish workflow's wall-clock; provides positive evidence of consumer-side install success.

### Cross-repo notify on plugin.json change

Workflow fires `repository_dispatch` (`plugin-updated` event) on a sibling marketplace repo when `.claude-plugin/plugin.json` changes. PAT-gated, one-way. Keeps marketplace state in sync without bidirectional write access. Constrains the relationship to a single secret (PAT) and a custom event-name convention. Appropriate when source and aggregator are decoupled and the maintainer wants a lightweight sync trigger.

### Sponsor automation as scheduled workflow

A `sponsors.yml` runs daily (`schedule: "0 6 * * *"`) plus `workflow_dispatch`, calling `JamesIves/github-sponsors-readme-action` six times (one per pledge tier) to sync `SPONSORS.md` and `README.md`. Appropriate for community-funded projects. Constrains: in the observed sample, the action targets `branch: master` while the default branch is `main` — a config drift that would fail on first run.

### CHANGELOG-parsing release action

`taiki-e/create-gh-release-action@v1` reads `CHANGELOG.md` (Keep-a-Changelog format) and extracts the section matching the tag's version. Release notes derived from the changelog rather than auto-generated commit log. Appropriate when curated release notes matter and the project commits to Keep-a-Changelog discipline.

### Auto-generated release notes from commits

`generate_release_notes: true` on `softprops/action-gh-release@v2` delegates to GitHub's built-in commit-based note generator. No CHANGELOG.md in repo. Appropriate for projects with conventional-commit-style histories. Constraint: regression investigation requires walking tags and comparing auto-generated notes; no human-curated narrative.

### CHANGELOG with non-Keep-a-Changelog custom sections

CHANGELOG.md follows the Keep a Changelog base format (`## [X.Y.Z] — date`, `### Added`, `### Fixed`) but adds custom sections (`### Verified-stale`, `### Multi-review`, `### Benchmarks validated live`, `### Backlog state`). Entries reference internal ticket IDs and external issue numbers. Hand-maintained — release notes on GitHub Releases manually duplicate a subset of CHANGELOG prose. A `release-please`-style auto-generator wouldn't handle the custom sections; the format trades automation for richness.

### `RELEASE-NOTES.md` consumed by SessionStart hook

A free-form `RELEASE-NOTES.md` (100+ KB) replaces a conventional CHANGELOG. The session-start hook reads it on update to extract the current release's "What's New" section and inject inline as context. Inline release-notes-as-context pattern.

### No releases at all

No tags, no GitHub Releases on the plugin repo. "Release" means whatever `main` currently points at. Often paired with no CI and a dangling external dependency (e.g., an update-check pipeline that polls a sister repo's releases endpoint that itself returns 404). The plugin ships with the release infrastructure code written but the supporting endpoints unbuilt. Versions are mutable strings in `plugin.json` files, not pinned anywhere downstream consumers can resolve.

## Documentation surface

What user-facing, developer-facing, and agent-facing docs the repo carries, and how they're organized.

### Stub README only

Repo `README.md` is small (~few hundred bytes) — headings and a "currently in active development" caution, no install/usage instructions. No per-plugin README. No CHANGELOG. No `architecture.md`. No `CLAUDE.md`. Substantive documentation, when it exists, lives in an internal `worklog/` directory with numerically-keyed specs/decisions/tasks. Appropriate for early-stage repos; the cost is a new consumer must infer install from manifests and SKILL.md files.

### README only

The plugin ships only `README.md` at the repo root — install + use + what-it-does + credentials/config + dev instructions. Substantial READMEs include benchmarks, troubleshooting, security sections; thin READMEs cover only install + usage. No `CHANGELOG.md`, no `architecture.md`, no `CLAUDE.md`. Architecture content (where present) lives inside the README as a narrative section. Single-skill plugins consolidate everything into one README plus the SKILL.md. Community health files (SECURITY.md, CONTRIBUTING.md, CODE_OF_CONDUCT.md) are typically absent — security guidance lives as a `## Security` section in README instead. Constraint: rationale for breaking changes lives only in commit messages — a user upgrading across a major bump has no migration guide. Technical readers must reverse-engineer the design from source.

### README + LICENSE (minimal)

Standard minimum: a README at repo root covering install / setup / usage, plus a LICENSE file (typically MIT). Appropriate for thin plugins where doc volume doesn't justify multi-file split.

### Comprehensive single README + ad-hoc CLAUDE.md

Repo-root `README.md` is the consumer-facing entry point — features, prereqs, install instructions for multiple MCP clients (Claude Code, Cursor, Windsurf, Cline), per-client config templates, env-var catalog, tool catalog, dev quick-start, troubleshooting. `CLAUDE.md` (when present) carries developer/agent guidance — architecture summary, registration patterns, test conventions, release runbook. The two often conflate concerns — `CLAUDE.md` mixes architecture-reference content with operational procedure (e.g., a "release runbook" embedded inline next to architecture description), acceptable for solo projects but blurs the project-doc-separation discipline of larger systems. A reader looking for either purpose has to skim past the other. Some plugins extend `CLAUDE.md` with explicit lists of frontmatter fields the harness silently drops (e.g., `color`, `hooks`, `mcpServers`, `permissionMode` ignored), enshrining harness-version-specific constraints inline rather than treating the silence as discoverable elsewhere — surfaces what is deliberately not used to contributors.

### Substantial root README + CHANGELOG + community files + badges

Repo `README.md` is ~15-25 KB covering features, install paths (often three: bootstrap curl-pipe, manual `/plugin` slash commands, classic marketplace add), supported platforms, configuration UX, troubleshooting. Opens with a hook framing or a value-prop scare example. Includes badges (CI, license, version, deps-zero). `CHANGELOG.md` follows Keep-a-Changelog format with `### Added/Fixed/Changed` under `## [x.y.z] - YYYY-MM-DD` headers, OR a custom format with theme statements. `CONTRIBUTING.md`, `LICENSE`, optional `.github/ISSUE_TEMPLATE/`. Architecture docs at `docs/ARCHITECTURE.md` (off-root, by docs-directory convention) or as a PNG diagram only.

### Marketing-grade README (40+ KB)

README doubles as marketing and technical reference. Sections include research motivation, third-party testimonials, shields.io badges (stars, version, license, install CTA), full skill catalog, hook inventory. Drives the file past 40 KB. Trade-off: discoverability and credibility benefit; maintenance cost grows; some sections (e.g. third-party LLM quotes) are unusual for a plugin README.

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` (user-facing pitch + install + commands), `ARCHITECTURE.md` (multi-layer diagram, hooks/skills tables, design flows), `CLAUDE.md` (project instructions for Claude operating *on* this repo), and `CHANGELOG.md` in Keep-a-Changelog format. Aligns with the system-docs convention. Sometimes paired with localized mirrors (`README_ja.md`, `LICENSE.ja.md`) when bilingual. Substantive subsystem READMEs for contributors (e.g., `<lib>/README.md`, `adapters/README.md`). Hosted Docusaurus site mirrors much of the in-repo documentation, with `docs/versioned_docs/version-X.Y.Z/` snapshotted per release. Constraint: two sources of truth (in-repo + Docusaurus) drift; the hosted version often lags. The architectural document may describe a richer hook surface than `hooks/hooks.json` actually wires.

### Two-document model (README + CLAUDE)

`README.md` (user-facing) plus a single `CLAUDE.md` (developer/contributor-facing — conventions, project structure, testing). No dedicated `ARCHITECTURE.md`; architecture content folded into `README.md`'s "Architecture" section (directory tree + protocol notes).

### README + ARCHITECTURE + CLAUDE-as-pointer

Substantial `README.md` (~16 KB) plus a sizable `ARCHITECTURE.md` at repo root with mermaid diagrams and design-principle prose. `CLAUDE.md` exists but contains only a pointer (`@AGENTS.md`-style include) — `AGENTS.md` is the canonical agent-rules file. Convention inversion: Claude Code loads `CLAUDE.md`, but the actual content lives elsewhere. Works because of the include directive. Constrains contributors to know the indirection or risk editing the wrong file.

### CLAUDE.md without ARCHITECTURE.md, ADRs as decision capture

CLAUDE.md carries an "Architecture" section with directory tree + role annotations, plus 15+ ADRs under `docs/adr/` in Nygard format (Status/Date/Context/Decision/Consequences). CHANGELOG entries cross-reference specific ADRs. Decision capture is strong; structural overview is split between CLAUDE.md and the ADR tree, requiring readers to reconcile both.

### Multi-doc architecture (no separate ARCHITECTURE.md)

Substantial root README plus per-skill SKILL.md plus contributing/changelog/CI docs (`docs/CI.md`, `docs/CONTENT-PLAN.md`). No top-level `ARCHITECTURE.md`. The architectural narrative lives in README sections (e.g., "Call Graph", "Skill Contracts", "How It Works"). Constrains future maintainers to reconstruct the architecture from prose; works while the README author and the maintainer are the same person. Appropriate when README discipline is high and the architecture is methodology-shaped rather than code-shaped.

### CLAUDE.md as architecture-doc carrier

No dedicated `architecture.md`; architectural content (three-layer diagram, threading model, protocol, runtime files, platform notes) lives inside `CLAUDE.md` at repo root. Combines build commands, architecture, threading rules, protocol reference, runtime files, platform notes, command menu, and release procedure. Blurs the agent-ops vs architecture separation conventional in the three-doc model.

### Heavy doc surface with meta-project artifacts

20+ top-level markdown files: README, ARCHITECTURE, CLAUDE, CHANGELOG plus competitor audits, research notes, roadmap, score-trend logs, audit-progress logs. README stays focused on the user; sprawl is absorbed into siblings. Can include "two CLAUDE-like files with different audiences" — `CLAUDE.md` for contributors, `<PLUGIN>_WIZARD.md` shipped as the wizard artifact consumers `cat` or WebFetch during setup.

### Sprawling root with many entry-point markdowns

17+ top-level files including README, CHANGELOG, ARCHITECTURE, CLAUDE.md, SKILL.md, SKILL_REGISTRY.md, AGENTS.md, ETHOS.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, LICENSE, VERSION, plus tooling configs. Appropriate for plugins with substantial internal complexity that need multi-perspective entry points; constrains discoverability because the root becomes a kitchen-sink and roles overlap (CLAUDE.md vs SKILL.md at the same level signals conflated governance).

### Multi-document agent-context layer

Repo root carries 14+ markdown files: `README.md` (multi-locale `docs/<locale>/`), `CHANGELOG.md`, `CLAUDE.md`, `AGENTS.md`, `RULES.md`, `SOUL.md`, `TROUBLESHOOTING.md`, `WORKING-CONTEXT.md`, `EVALUATION.md`, `REPO-ASSESSMENT.md`, `COMMANDS-QUICK-REF.md`, `SPONSORING.md`, `SPONSORS.md`, plus `the-longform-guide.md`/`the-shortform-guide.md`/`the-security-guide.md`. Multi-language READMEs for pt-BR, zh-CN, zh-TW, ja-JP, ko-KR, tr. Appropriate when the audience needs both marketing surface and rich agent-facing context. Constrains: locale README maintenance burden — observed release script bumps version in only two locales, so the others drift.

### Full kitchen-sink docs

`README.md` plus a large `CHANGELOG.md` (Keep-a-Changelog format, dev-trail entries during pre-release cycles) plus `docs/<architecture>.md` and `docs/migration-*.md` plus `docs/USER-GUIDE.md` (~60 KB) plus `docs/prd/*.md` for feature specs plus a long `CONTRIBUTING.md` (~22 KB) plus `SECURITY.md` plus `CODE_OF_CONDUCT.md` plus issue and PR templates. Documentation-as-code practice extending to PRDs. `CLAUDE.md` is operational procedures (agent-authoring pitfalls, structure overview, destructive-command-guard documentation), not just a pointer. Drift hazard at this scale: stale references in `SECURITY.md` to pre-refactor file names linger across migrations.

### Nested `docs/` tree with map in README

A `docs/` directory holds `QUICKSTART.md`, `INSTALL.md`, `CLI.md`, `CONFIGURATION.md`, `ENV.md`, `SLASH-COMMANDS.md`, `PUBLISHING.md`, `QAPLAYBOOK.md`, etc. The README contains a "documentation map" table that routes readers to the right doc. Appropriate when the plugin has many distinct user concerns each warranting their own page; constrains link discipline because case-mismatch bugs (`docs/architecture.md` on disk vs `docs/ARCHITECTURE.md` in a link) only surface on case-sensitive filesystems.

### README + docs/ tree (architecture, configuration, walkthrough, limitations)

Repo-root `README.md` (Quick Start, Claude Code integration, MCP tools table, SDK integration, "How It Works" pipeline diagram) plus a `docs/` directory with `architecture.md`, `configuration.md`, `walkthrough.md`, `limitations.md`, `assets/`. `.gitignore` may explicitly exclude `CLAUDE.md` and `**/CLAUDE.md` — a deliberate stance that agent-context files are not committed.

### docs/DESIGN.md and docs/SPEC.md

Architecture content lives in `docs/DESIGN.md` (~36 KB) and `docs/SPEC.md` (~22 KB) rather than a root `architecture.md`. Substantive design rationale, but a consumer following the "architecture.md at root" convention misses them.

### Internal developer log as primary architecture doc

The repo carries a structured internal log directory (`worklog/spec/`, `worklog/decision/`, `worklog/archive/task/`) with numerically-keyed specs, ADRs, and archived tasks. Each decision uses TOML-fence frontmatter with `id`, `title`, `relates_to`, `supersedes` keys; tasks move through spec → task → archived-task lifecycle. Cross-linking is explicit. Appropriate as a long-form design practice that embeds decision history inside the repo rather than relying on PR/issue history; the cost is the docs are inward-facing and a new user without the convention has to map it.

### Shipped planning corpus visible in public repo

`.planning/` tree with MILESTONES.md, ROADMAP.md, STATE.md, per-version phase directories each holding CONTEXT/PLAN/SUMMARY/VERIFICATION/RESEARCH files. 260+ planning files visible in the public repo. Some projects keep this private; others publish their entire milestone-planning process. Variant: `IMPLEMENTATION_PLAN.md` (large, 44 KB), `memory/project_*.md` files, and `memory/MEMORY.md` indexes shipped as first-class repo content (not gitignored). The author's working notes, design context, and personal Claude Code memory become public artifacts. Risk: planning docs can carry stale references (e.g., legacy plugin name paths after a rebrand).

### CHANGELOG with "Why" and "Migration" subsections

Beyond Keep-a-Changelog's prescription, each release entry adds a `Why` section (decision rationale, sometimes citing external docs) and a `Migration` checklist for consumers. CHANGELOG functions as design-decision log, not just release notes. Significantly more substantive than typical CHANGELOGs.

### CHANGELOG depth as documentation

CHANGELOG entries carry not just `Added`/`Changed`/`Fixed` but `Ops` (per-release manual checklists), `Context`, `Rationale`, `Lessons learned (meta-review gap)`, `Deliberately not done (deferred)`. The latter two close a feedback loop between CI output and rubric improvements; the deferred section captures negative-space decisions as first-class entries. Constrains release discipline to thoughtful authoring. Appropriate when CHANGELOG is treated as the project's reasoning log rather than a feature manifest.

### Keep-a-Changelog with root-cause prose

`CHANGELOG.md` declares Keep-a-Changelog format at top; every release block has Added/Changed/Fixed sections with prose explaining root causes (e.g. why a hook was rewritten, what bug a new fallback addresses). Unusually detailed for a plugin repo. Appropriate when the project has substantial cross-release behavior changes that demand explanation.

### CHANGELOG as in-product upgrade source

`CHANGELOG.md` doubles as the source the in-product update skill consumes — fetched via WebFetch and diffed against the installed version stamp embedded in a shipped doc. Not just a release-notes artifact; an active runtime input for the plugin's self-update flow.

### Free-form CHANGELOG variants

Multiple shapes coexist across the corpus:

- **Keep a Changelog (1.1.0)** — `CHANGELOG.md` at repo root, SemVer-aligned `## vX.Y.Z` sections, parsed by `taiki-e/create-gh-release-action@v1` for release notes
- **Hybrid Keep-a-Changelog-ish** — header declares semver, entries are `## [X.Y.Z] — <date>` with narrative subsections (no strict `Added`/`Changed`/`Fixed` buckets)
- **Custom firmware-scoped CHANGELOG** — `<subsystem>/CHANGELOG.md` (not at repo root), custom `## vX.Y` section format, not parsed by automation
- **Per-plugin Keep-a-Changelog** — within a multi-plugin marketplace, some plugins ship `docs/CHANGELOG.md` while others lack changelogs entirely despite high patch-version counts. Resemble Keep a Changelog format but are hand-maintained — no automation aligns the CHANGELOG with `plugin.json` version, so divergence is normal.
- **Conventional-commit-driven** — `CHANGELOG.md` updated by the release skill or `git-cliff`, parses `feat:`/`fix:`/`refactor:` prefixes from `git log` output and inserts dated sections
- **Free-form Unreleased list** — a partner plugin ships a `CHANGELOG.md` as a free-form "Unreleased" list, not Keep-a-Changelog format. Nothing parses it
- **Absent** — release notes from `generate_release_notes: true` (auto-generated commit log) or no changelog at all

### CHANGELOG and ARCHITECTURE absent at root

No `CHANGELOG.md` (replaced by `RELEASE-NOTES.md` or absent entirely) and no `ARCHITECTURE.md` at repo root. Architecture content lives in a `docs/architecture/` directory or in a separate Astro Starlight docs site published to GitHub Pages. Constraint: a reader looking at repo root for the standard three-document set (README / ARCHITECTURE / CLAUDE) finds only README.

### Multi-language READMEs

Paired English-and-other-language versions (`README.md` + `README.zh-CN.md`, `README.md` + `README.ru.md`) with no sync-enforcement (or, in some cases, version-sync script enforcing parity). Per-skill `## Trigger phrases` lists in both languages; `check-skills.sh` regex tables include both-language matches. Constrains every doc-touch to update both READMEs. Appropriate when the user population is genuinely multi-lingual and each language carries equal trigger weight; cost is content-drift between locales when sync is unenforced.

### Bilingual content

README is explicitly bilingual (English + Chinese, with anchor-linked language sections). Uncommon in Claude Code plugin READMEs; signals community reach.

### Documentation sprawl

Many root-level docs covering go-to-market content (`LAUNCH.md`, `LAUNCH_NOW.md`, `LAUNCH_POSTS.md`, `DISTRIBUTION_RUNBOOK.md`, `FIRST_CUSTOMER_BATTLE_PLAN.md`, `gate-program.md`, `primer.md`) alongside developer docs. A new contributor cannot tell from `ls` which doc to read first. Constrains discoverability; works when the project intentionally mixes business and engineering surfaces.

### Promotion drafts in-repo

`docs/promotion/drafts/` carries marketing copy for HN, devto, habr, reddit, twitter. The custom rubric scans these for stale version references — promo content participates in version-drift validation. Constrains every release to update promo too.

### Per-plugin README in `.claude-plugin/`

A scoped README (`.claude-plugin/README.md`) inside the plugin manifest directory, distinct from the root README and tailored to the Claude-Desktop install surface. Constrains the maintainer to two README surfaces with overlapping but non-identical content. Appropriate when the plugin is one of several integration shims and the root README is multi-host marketing material.

### SKILL.md as primary doc for the skill component

`skills/<name>/SKILL.md` (10KB+ in observed cases) is the deep operational doc; root README is install-focused. Appropriate when the plugin is essentially a skill — most of the substantive content describes what the skill does and how to invoke it. Description field has a hard 1024-char limit and is read by many agent hosts simultaneously when the skill is multi-host.

### README + WALKTHROUGH.md as architecture-adjacent

A single-plugin repo ships a `README.md` (install, prerequisites, per-command usage) and a long-form `WALKTHROUGH.md` (~17KB) that describes the underlying methodology, schema contract, and per-command flow. The walkthrough is framed as user tutorial but carries content an `architecture.md` would otherwise hold. No `CLAUDE.md` at repo root — though the plugin generates a `CLAUDE.md` template inside each user-created data directory as a per-data-directory schema anchor.

### AGENTS.md as cross-runtime governance unification

A repo serving Claude + Cursor + Codex consumers uses `AGENTS.md` (Codex-first convention) as the single agent-facing governance doc, in place of the Claude-native `CLAUDE.md`. Carries what would be both `CLAUDE.md` (operational procedures) and `architecture.md` (how the plugin works) in a Claude-native convention. Trade-off: per-runtime specificity for a single doc surface. Sub-architecture lives in `docs/design/<NNN>-<topic>.md` files — numbered design notes rather than monolithic.

### `AGENTS.md` as ecosystem-neutral alternative to `CLAUDE.md`

A file targeting "agent tools that look for `AGENTS.md`" — explicit framing as the cross-ecosystem counterpart to Claude-specific `CLAUDE.md`. Observed in a single partner plugin; emerging cross-ecosystem signal.

### `CONNECTORS.md` sibling-doc convention

A de-facto per-plugin file describing bundled MCP servers, cross-referenced from SKILL.md files via relative paths. Not a Claude-spec filename — repo-originated convention spread across many plugins in one marketplace.

### Architecture / design docs

`SPEC.md`, `ADR.md`, `ARCHITECTURE.md` (or lowercase variants) at repo root cover the project's underlying design (e.g., a binary the plugin wraps). Not always mirrored into the plugin subdirectory; sometimes absent entirely or replaced by `RELEASE-NOTES.md`-style files.

### CLAUDE.md template shipped for consumer projects

A `CLAUDE-MD-TEMPLATE.md` file ships at repo root, intended to be copied into the consumer's own project (not the plugin's own CLAUDE.md). Turns the plugin into a shipped convention: "add this to YOUR project's CLAUDE.md to tell Claude how to use us." Distinct from the plugin's own CLAUDE.md (when present) which documents the plugin's internal development.

### Dual-CLAUDE.md (developer + user-workspace)

A repo-root `CLAUDE.md` is developer-facing (architecture for the plugin author), and a `templates/CLAUDE.md` is deployed into the user's workspace by a setup skill (architecture for the user's project). Same filename, different audiences. The root file's opening warning ("don't confuse the two") is load-bearing — without it, an agent working on the plugin could easily edit the wrong one.

### CLAUDE.md and AGENTS.md duplicating each other

Both files at repo root carry near-identical content (CLI shape, output formats, exit codes, build, commit format, dependencies, skills). No declared single-source-of-truth pointer. Drift risk on refactor.

### CLAUDE.md as project-config surface

`CLAUDE.md` declares a `## Project Type` field (`java | skills | blog | custom | generic`) that multiple skills read at runtime to dispatch to language-specific sub-skills. The doc doubles as agent-facing rules AND a runtime config surface. Constrains: skills must defensively parse the field and handle missing values, and the CLAUDE.md schema becomes part of the plugin's interface.

### Plugin scaffolds CLAUDE.md as user-data schema

A plugin generates a `CLAUDE.md` template inside each user-created data directory (`~/ObsidianVault/<wiki>/CLAUDE.md`) as part of its setup operation. This `CLAUDE.md` is not the plugin's own governance doc — it's user data that becomes the schema contract for subsequent skill invocations.

### CLAUDE.md at root or per plugin

Architecture-level operational doc covering build commands, build-system gotchas, hook protocol, env-var contract, supported-runtime list. Sometimes at repo root, sometimes only per-plugin, sometimes only at a `memorys/CLAUDE.md` subdirectory copied to the install target by the installer rather than read directly. Quality varies from minimal stub to highly detailed onboarding doc.

### No CLAUDE.md

Plugin or marketplace ships no `CLAUDE.md` operational doc. Agents working in the repo have no project-specific procedures to follow. Constrains agents to default behavior; rules and patterns live only in skill bodies if anywhere.

### Stale `CLAUDE.md`

A repo-root `CLAUDE.md` references paths and structures that do not exist in the current tree (`mcp/`, `mcp-categories.json` referenced but absent). Generic template scaffolding never updated to match reality. Following it would mislead an agent — the document looks authoritative but isn't.

### Layered repo / plugin / skill READMEs (uneven)

Repo-root `README.md` describes the marketplace; a subset of plugins ship plugin-level `README.md` (4 of 10 in one observed sample), and skills ship per-skill `SKILL.md`. `architecture.md` exists at the plugin level for one plugin only (the runtime-heavy one); other structurally substantial plugins lack architecture docs. Inconsistency within a single marketplace makes a reader unable to predict where to find architectural detail without checking each plugin separately.

### Per-plugin README mixed coverage

In multi-plugin marketplaces, per-plugin READMEs are uneven — some plugins ship one, others don't, with no rule. First-party plugins typically ship one, thin external MCP wrappers usually do not. Skills without a README rely on `SKILL.md` frontmatter for discoverability. Tied to plugin maturity and author attention rather than a discipline rule.

### Minimal consumer-facing README only

A short `README.md` (~1.4 KB) explains the install commands and submission flow. No `CHANGELOG`, no `architecture.md`, no `CLAUDE.md`, no community health files. Appropriate for read-only mirrors with intentionally-routed contribution paths.

### Repo-root README only (no per-plugin)

Single substantial README at repo root; plugins do not ship per-plugin READMEs. Plugin discovery happens through marketplace metadata (`description`, `category`, `tags`) and the README's own plugin matrix.

### Agent-targeted install preamble in README

The README opens with a blockquote-rendered "For AI Coding Agents — Read This First" section containing literal shell commands segmented by OS × scope × agent (Claude Code, Cursor, Codex, OpenClaw). When a user asks their coding agent to install the plugin, the agent fetches the README and gets an unambiguous install recipe at the top. A distinct consumer surface from the human-facing install sections elsewhere in the README — the same install intent encoded twice. Appropriate when agent-driven installs are a major install vector.

### Astro Starlight docs site with auto-generated MDX

A `docs-site/` directory ships a full Astro Starlight site, with generator scripts (`docs-site/scripts/generate-bp-docs.mjs`, `generate-tool-docs.mjs`) that auto-generate MDX from in-plugin sources (best-practice rules in `skills/<skill>/references/*.md`; MCP tool registrations). Published to GitHub Pages via a separate `deploy-docs.yml` workflow with path filters. The docs site is a first-class user-facing artifact in the same repo as the plugin code — secondary build pipeline driven by the same source.

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

### README + CONTRIBUTING + CLAUDE.md (no architecture.md, no CHANGELOG)

Repo-root `README.md` (with badges, installation, command/skill catalog), `CONTRIBUTING.md` (prerequisites, project structure), and `CLAUDE.md` doubling as project overview plus agent-facing operational reference. No dedicated `architecture.md` — architectural content is split between CLAUDE.md "Architecture" and README "How It Works", with a separate long-form `GUIDE.md` for human readers.

### Repo-meta docs alongside user-facing docs

Root carries the repo's own workflow artifacts (`DESIGN.md`, `PHILOSOPHY.md`, `QUALITY.md`, `HANDOFF.md`, `IDEAS.md`, `RELEASE.md`) — meta-documentation about how the repo operates. Often coexists with user-facing docs in `docs/`. Appropriate when the repo dogfoods plugins it ships.

### README references to docs that don't exist

README links to `docs/ARCHITECTURE.md`, `docs/<plugin>-OVERVIEW.md`, etc. that aren't present in the repo's `docs/` listing. Either aspirational ("we plan to write these"), removed without README update, or in a nested location not surfaced by listing. Reader clicking links 404s. Drift symptom — README and disk state diverged.

### Documentation drift signals

Two specific drift shapes recur:

- **README/CLAUDE.md disagrees with the actual install script** about install location (`${CLAUDE_PLUGIN_DATA}/node_modules` vs `${CLAUDE_PLUGIN_ROOT}/<server>/node_modules`). The script is the source of truth; the doc was not updated when the install location moved
- **README cites `engines.node >= N`** but `package.json` declares `>= N+M`, or `engines.node >= 22` while CI tests on Node 20 — engines floors are sometimes aspirational and not gated

### Plugin-bridge cross-agent symlinker

`tools/plugin-bridge/` ships an auxiliary bash toolkit (install + launchd plist + update + uninstall + README) that maintains a symlink from another agent's skills directory (e.g. `~/.codex/skills/<name>`) to `~/.claude/plugins/cache/<marketplace>/<plugin>/<latest-version>/skills/<name>`. Auto-relinks on `claude plugin update` via launchd `WatchPaths`. Linux equivalent uses `systemd --user` path units. Converts Claude Code's versioned plugin cache into a live source for non-Claude agents. Appropriate when the skill targets multiple agent hosts and the maintainer wants a single source of truth for the skill's content.

## Agent-docs synchronization

How `CLAUDE.md`, `AGENTS.md`, and similar parallel agent-facing files stay in sync.

### Shared block with marker-bracketed sync

A canonical `docs/AGENTS.shared.md` is the single source; a `sync_agent_docs.py` script propagates it into `CLAUDE.md`, `AGENTS.md`, and a Cursor `.mdc` rules file between `<!-- BEGIN AGENTS_SHARED -->` / `<!-- END AGENTS_SHARED -->` markers. CI enforces with `--check` mode. Appropriate when the same agent guidance must reach multiple ecosystems verbatim. Constrains: any unique-per-tool content must live outside the markers in the destination file.

### Hand-maintained parallel files

`CLAUDE.md` and `AGENTS.md` exist at the same level with no sync mechanism. Appropriate when the two files diverge intentionally; constrains because drift is silent until a reader notices.

## License declaration

Where the LICENSE is declared and how it propagates to ecosystem detectors.

### LICENSE file present + SPDX in manifests (single source agreement)

A full LICENSE file at repo root (e.g., 10.5 KB Apache-2.0 text, MIT text) plus `license` field in `plugin.json` and `package.json` carrying the SPDX identifier. README references the same. GitHub auto-detects and badges the license. All four agree. Standard hygiene.

### Single repo-level license

`LICENSE` at repo root applies to everything. Conventional MIT/Apache LICENSE; standard ecosystem shape, suits single-plugin marketplaces and most projects.

### Repo-root LICENSE plus per-plugin duplicates

A repo-root `LICENSE` (e.g., Apache-2.0) governs the marketplace-level artifacts, with identical copies inside primary-owned plugin directories. Vendored-partner plugins ship their own LICENSE file, sometimes a different license (MIT vs Apache-2.0).

### Layered: repo-MIT, plugin-MIT, per-skill-Apache-2.0

Plugin code is MIT, but per-skill content is Apache 2.0 under `skills/<name>/LICENSE.txt`. Granular license delineation inside a plugin. Appropriate when content licensing differs from code licensing (Apache for shareable prompt content, MIT for tooling). Constrains: every skill must ship its own LICENSE.txt; mixed licensing requires consumer awareness.

### No repo-root LICENSE; per-skill LICENSE only

`LICENSE.txt` (Apache-2.0) inside each skill directory; nothing at repo root. GitHub's license detector returns null. Marketplace-level artifacts (marketplace.json, README, workflows) are under no declared license.

### LICENSE declared in manifests, no LICENSE file

`license: "MIT"` (or similar) in `package.json` and `plugin.json` but no `LICENSE` file at repo root. GitHub license API returns 404; no SPDX detection. npm publishes the package without a LICENSE file in the tarball unless added to `package.json.files`. Real defect — propagates the license claim via metadata only. Common in early single-author plugins. When per-plugin `plugin.json` entries declare licenses but no root `LICENSE` exists, GitHub API reports `license: null` even though individual plugins claim a license — repo is legally ambiguous despite the per-plugin claim.

### License only in README prose

License claim lives only in README prose without an SPDX-identifiable `LICENSE` file. GitHub UI reports the repo as unlicensed regardless of the README claim because no SPDX-identifiable file exists.

### Three-way disagreement

README asserts one thing ("Plugin wrapper: MIT. Extraction engine: proprietary."), `plugin.json` declares another (`"license": "UNLICENSED"`), no `LICENSE` file commits anything, GitHub API returns null. Author intent is unrecoverable from static inspection. GitHub UI and tooling report the repo as unlicensed regardless of the README claim.

### AGPL-3.0 with embedded badge

LICENSE present, SPDX `AGPL-3.0-only`, README carries the AGPL badge alongside CI/version badges.

### No license declaration anywhere

No `LICENSE` file at repo root, no `license` field in `plugin.json`, no SPDX claim in `package.json`, no claim in README. GitHub license detector returns null. Without an explicit grant, default copyright applies — downstream consumers have no legal basis to redistribute, modify, or repackage the plugin. Common in solo / hobbyist marketplaces and multi-plugin aggregators that never adopted licensing as a release-checklist item; observably worse than a stale LICENSE because the absence is total. Distinct from `LICENSE declared in manifests, no LICENSE file` (where at least one declaration exists) and from `License only in README prose` (where intent is recorded informally).

## Community health files

Standard open-source repo files beyond LICENSE.

### Open contribution with health files

`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` present; PRs welcomed and reviewed. Appropriate for community-driven projects.

### Bare minimum (LICENSE only)

Root carries `LICENSE`. No `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/ISSUE_TEMPLATE/`, `.github/PULL_REQUEST_TEMPLATE.md`. Constrains contributor-onboarding to whatever the README says.

### LICENSE + CODE_OF_CONDUCT + issue templates

Root carries `LICENSE` and `CODE_OF_CONDUCT.md`; `.github/ISSUE_TEMPLATE/` has `bug_report.md` and `feature_request.md`. No `SECURITY.md` or `CONTRIBUTING.md`. Constrains: contribution flow is implicit, security-disclosure path undocumented.

### Community health files absent

`SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `ISSUE_TEMPLATE/`, `PULL_REQUEST_TEMPLATE.md` uniformly absent. Where security-relevant policy exists (secret-file deny rules), it lives inside `.claude/settings.json` rather than a standalone doc.

### Anti-contribution with auto-close gatekeeper

`pull_request_target` workflow checks the PR author's collaborator permission via GitHub API; if not admin/write, posts a canned redirect comment to a submission portal and closes the PR with `pulls.update({state: 'closed'})`. No `CONTRIBUTING.md` to make the gate discoverable in GitHub's UI; the README carries the routing message. Appropriate for read-only mirrors with submissions accepted via a separate portal. Constrains: first-time visitors may not realize direct PRs are unwelcome until the auto-close fires; the `pull_request_target` trigger runs with repo-scoped secrets so the inline script must avoid checking out PR code.

## Cross-platform discipline

How the plugin's runtime code accommodates Windows, macOS, and Linux beyond what dependency-installation strategies cover.

### POSIX `/bin/sh` discipline in hot path

Hot-path scripts (e.g. hook wrapper invoked on every event) use `/bin/sh` shebang strict POSIX — no `[[ ]]`, no arrays, no process substitution, no `local`. Manual iteration replaces `mapfile`. Appropriate because Debian/Ubuntu point `/bin/sh` at `dash`, not `bash`, and any bashism would crash silently for those users. One-shot paths (installer, bootstrap) can be bash-rich; hot path stays POSIX.

### Mixed shebangs partitioned by criticality

Hot path: `/bin/sh` (POSIX). Installer: `/bin/bash` with `set -e`. Bootstrap one-shot: `/bin/bash` with `set -euo pipefail`. Test mock server: `#!/usr/bin/env python3`. Each role gets its own shebang appropriate to its constraints. Appropriate as a deliberate partition; the alternative is uniform `#!/bin/bash` everywhere and accepting risk on the hot path.

### Dual-fallback OS detection

`uname -s` primary; `$OS` env var (e.g. `Windows_NT`) fallback for shells without `uname`. Architecture: `uname -m` normalized to `amd64`/`arm64`. Pattern worth codifying: don't trust one probe on Windows.

### Git symlink-as-text-file detection on Windows

Git on Windows with `core.symlinks=false` (the default) materializes symlinks as plain text files containing the target string. A wrapper detects this case (file size < 1KB, contents match an expected binary-name pattern) and either resolves to the real target or synthesizes a `MISSING` path to force re-install. `.gitattributes` codifies `text eol=lf` for `*.sh` and `eol=crlf` for `*.bat`/`*.ps1`. Cross-platform workaround for a git-setting difference most plugin authors don't realize they're hitting.

### Adapter directory per host CLI

Multi-host plugins ship `adapters/<host>/` directories (e.g. `adapters/copilot_cli/`, `adapters/codex_cli/`) each with its own manifest format. Shared core in a common module (e.g. `hooks/scripts/core/`); adapters import, not duplicate. Installer detects which host CLI is present and wires up the right adapter surface. Appropriate when the plugin must support multiple Claude-adjacent CLIs; the cost is a multi-times manifest-edit burden during a refactor.

### Documented Windows-native migration

CHANGELOG explicitly enumerates each cross-platform concern as it lands: `os.tmpdir()` replaces `${TMPDIR:-/tmp}`, `path.parse(dir).root` replaces `/`-terminator for filesystem walks, Windows backslash normalization before glob matching, CRLF-tolerant config parsing, `.gitattributes` EOL rules. Pattern: windows-native as a documented migration. Most marketplaces implicitly assume POSIX; this one lists each accommodation as a deliberate change with rationale.

### POSIX with documented platform rejection

`install.sh` detects platform and explicitly errors on unsupported configurations (e.g., Intel macOS, Windows) with corrective guidance pointing at a local-build escape hatch. No silent fallback; no Windows code path. Cross-platform support stops at "build it yourself if you're not on the supported list."

### POSIX with `stat` portability fallback

Bash scripts wrap stat invocations as `stat -f %m || stat -c %Y || echo 0` (BSD form, then GNU form, then literal zero). Final `echo 0` is a silent cache-disable failure mode rather than a hard error: when both stat forms fail, the resulting epoch is so far in the past that subsequent freshness comparisons always return false. Works on macOS and GNU/Linux; behavior on busybox, Alpine, FreeBSD is unverified.

### POSIX-only with no Windows story

Plugin ships only nix-style paths (`venv/bin/python`, `#!/usr/bin/env bash`). No Windows path branch, no `.cmd`/`.ps1` pair. Acceptable when the plugin's target domain is itself POSIX-only (e.g. iOS / Android simulator tooling). Loud failure mode on Windows: `.mcp.json` referencing `venv/bin/python` won't resolve at all. README typically declares minimum runtime versions but not OS support.

### macOS-only with explicit non-Darwin runtime rejection

Plugin installs cleanly on any OS but its underlying binary exits with a specific message (e.g. `"<plugin> is macOS-only"`) plus install hints (`cargo install …`, `brew install …`) on non-Darwin platforms. The capability filter is runtime, not install-time — works because the upstream integration target (e.g., a macOS GUI app) is itself OS-bound, while the plugin's own surface is OS-agnostic. Distinct from `POSIX-only with no Windows story` (which silently degrades) and from `POSIX with documented platform rejection` (which rejects at install). Constrains: plugin install never errors, so users on Windows / Linux see the failure only when invoking a tool.

### Polyglot wrapper for cross-OS hook invocation

See *Bin entry mechanism > Polyglot CMD/bash wrapper*. The wrapper itself is a portability mechanism — one file invoked by both Windows `cmd.exe` and POSIX `bash` to dispatch hooks consistently across OSes.

## Multi-runtime portability

How the plugin supports parallel runtimes (Claude Code + Cursor + Codex + OpenCode + Gemini + Copilot CLI) from one repo.

### Single-runtime — Claude Code only

Plugin manifests live exclusively under `.claude-plugin/`. No `.cursor-plugin/`, no `.codex/`. Skills, hooks, and bin wrappers assume Claude Code's env vars and hook schema. The default shape across most of the corpus.

### Per-runtime manifest directories

Repo hosts `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/` top-level directories, each with its own `plugin.json` (or runtime-specific equivalent). Hooks are duplicated across runtimes with naming-convention differences: Claude `hooks.json` uses PascalCase event names (`SessionStart`, `PreToolUse`); Cursor `hooks-cursor.json` uses camelCase (`sessionStart`, `preToolUse`); Codex bash launchers inline a multi-location plugin-root discovery routine because Codex lacks a `${PLUGIN_ROOT}` env var. Same source, different syntax — drives the need for a single-source-of-truth compiler upstream.

### Parallel manifests for Claude + Cursor + Codex

The repo ships `.claude-plugin/marketplace.json`+`plugin.json`, `.cursor-plugin/plugin.json` (richer — explicit component paths, `displayName`, `publisher`, `logo`, `category`, `tags`), `.codex-plugin/plugin.json` or `.codex/config.toml`, plus an `AGENTS.md`. Each ecosystem reads its own manifest. Appropriate when the plugin's value is portable across agent CLIs and the author commits to maintaining each surface. Constrains because configuration that should be shared (`userConfig`, version strings, skill paths) is duplicated across manifests with no sync — drift surface scales with ecosystem count. A build script (`scripts/gen-targets.ts`) may regenerate mirrored skill content into `.claude/skills/`, `skills/`, `codex-skills/`, but a hand-edited mirror is the default starting point.

### Triple-runtime parallel manifests

The repo ships three parallel manifest trees: `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, and `.codex/` (install-by-symlink). Same `scripts/` and `skills/` trees. Hook schemas differ per runtime — Claude uses nested `{hooks:[{hooks:[{type, command}]}]}`, Cursor uses flat `sessionStart: [{command: "./hooks/session-start"}]` plus a top-level `version: 1` field, Codex adds `statusMessage` and `timeout` fields Claude lacks. A trivial bash exec wrapper bridges Cursor's relative-command schema to the shared script. Skill preambles use a triple-fallback chain (`SHIP_PLUGIN_ROOT` env, bin-discovery wrapper, hard-coded Codex install path) to locate the plugin tree under any runtime. Cross-runtime version drift is live and hand-aligned.

### Skill content mirrored under multiple paths

The same skill files appear under `.claude/skills/`, top-level `skills/`, and `codex-skills/`. A regeneration script copies between locations. Appropriate when each ecosystem expects a different canonical path; constrains because hand-edits to one location must be regenerated to the others.

## Cross-ecosystem distribution

When the same project ships through multiple delivery surfaces or to multiple agent ecosystems.

### Single-ecosystem (Claude only)

`.claude-plugin/marketplace.json` is the only manifest. No Codex, no Cursor, no other agent-host configuration in the tree. Plugin manifest, hook scripts, components scoped to Claude Code's plugin protocol. No siblings.

### Plugin + npm CLI + curl-bash with collision detection

Same content shipped via three install paths: Claude plugin (enabled inside Claude Code), npm CLI (installable via `npx`, `npm install -g`, or Homebrew tap), and `curl | bash` script. The CLI's init code explicitly probes for the plugin install paths and blocks with a typed error when both coexist; a session-start hook also nudges on dual-install. Six documented install paths (npx, curl-bash, Homebrew tap, gh extension, `npx github:`, global npm) — heavy investment in distribution surface area. The engineering cost is documented in CHANGELOG with a referenced PR.

### Plugin + monolithic repo with rebrand legacy

Plugin shipped under a current name, with extensive backward-compatibility for a legacy name across every runtime surface — env var pairs (`<NEW>_API_KEY`/`<OLD>_API_KEY`, `<NEW>_WORKER_PORT`/`<OLD>_WORKER_PORT`, etc.), data dirs (`~/.<new>/` preferred, `~/.<old>/` honored if new dir doesn't exist), config files (`<new>.config.json` preferred, `<old>.config.json` honored). Identity-transition discipline far thicker than typical rebrand-compat — every observable surface honors both spellings. Intermediate artifacts may still carry the old name (e.g., a `runtime-deps.json` with `name: "@<old>/runtime-deps"` at version 5.7.0 inside a v0.1.0 release of the new identity).

### Dual-harness (Claude Code + second agentic CLI)

Single source tree (or a shared marketplace manifest mirrored across two well-known paths) carries one Claude Code surface plus one or more sibling-runtime surfaces — Gemini CLI, GitHub Copilot CLI, etc. Common forms: parallel manifests in the same repo (`.claude-plugin/plugin.json` + `gemini-extension.json`), or byte-identical `marketplace.json` mirrored at `.claude-plugin/marketplace.json` and `.github/plugin/marketplace.json` to target Claude Code and Copilot CLI from one source. Commands are `*.toml + *.md` pairs designed to be harness-agnostic; hook scripts in `hooks/scripts/` (not `.claude-plugin/hooks/`) so both harnesses can wire them via their respective registration files (`.claude-plugin/hooks.json` vs `hooks/gemini-hooks.json`). Hook scripts guard on `${CLAUDE_PLUGIN_ROOT:-}` presence to skip Claude-only logic when running under another runtime. Multi-file version sync (`plugin.json`, `marketplace.json`, `gemini-extension.json`) lives in prose. Deliberate decision recorded in CHANGELOG that the plugin's distribution model differs per harness (e.g., bundled MCP for Claude, install-dir model for Gemini). Where the same harness wraps differently across runtimes — install location asymmetry between Claude and Gemini installs, for example — install-side scripts must encode the per-runtime path conventions.

### Triple-ecosystem (Claude + Codex + Cursor)

Single repo ships `.claude-plugin/marketplace.json` for Claude Code, `.codex-plugin/plugin.json` for Codex, and `.cursor/rules/*.mdc` for Cursor IDE — three concurrent manifest systems. Bootstrap scripts (`scripts/codex-install.sh`, `scripts/cursor-install.sh`) adapt the same skills/agents/hooks to each host. A shared `platform.mjs` exposes `SO_PLATFORM`, `SO_IS_WINDOWS`, `SO_IS_WSL` so library code can branch without duplicating logic. Cascading runtime resolution chain (`${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}`) supports invocation from any host. Constrains every install-side change to be tested across three ecosystems and pushes the plugin into a "lowest common denominator" portion of each host's API surface.

### Multi-adapter single-package shape

One npm package ships internal adapters for multiple host ecosystems (`adapters/{amp,chatgpt,claude,codex,forge,gemini,mcp,opencode}/`), each with its own integration descriptor (`config.toml`, `opencode.json`, `function-declarations.json`, `openapi.yaml`). A parallel `plugins/{amp-skill,claude-codex-bridge,claude-skill,codex-profile,cursor-marketplace,gemini-extension,opencode-profile}/` tree mirrors that at the plugin-format layer. Constrains every release to update every descriptor; the version-sync script makes this tractable. Appropriate when the codebase is genuinely platform-neutral and the author wants one bug-fix to land everywhere.

### Tri-target same-codebase plugin

Same source packaged as (a) Claude Code marketplace plugin, (b) OpenCode npm package (`@<author>/<name>-plugin` via `packages/opencode-plugin/`), (c) Codex CLI install target (via `bunx @<author>/<name>-plugin install --platform codex`). TypeScript core under `src/core/` is shared; an `src/opencode/` adapter layer adapts it; `src/cli/` drives the npm install flow for non-Claude-Code consumers. The bin-wrapper's `<name>_PLUGIN_ROOT` env-var-first resolution exists specifically because `CLAUDE_PLUGIN_ROOT` isn't set in non-Claude-Code ecosystems. Constraint: every plugin-protocol concern must be expressed across all three target conventions.

### Dual-mode plugin/library

The same source tree installs either as a Claude Code plugin (via marketplace) or as a pip-installable Python library (via `pip install -e ".[dev]"` plus a project-local `init` command). The library-mode entry point declared in `pyproject.toml [project.scripts]` is invisible to plugin-mode users because their venv lives in plugin data and isn't on PATH. Two install paths, one conceptual surface, no runtime overlap because plugin-mode uses `${CLAUDE_PLUGIN_ROOT}`-relative paths and library-mode uses project-absolute paths. Some configuration (e.g., MCP server registration) has parallel mechanisms (inline in `plugin.json` for plugin-mode, `.mcp.json.example` template for library-mode).

### Multi-registry publishing

Same release ships to npm, GitHub Releases (`.mcpb` bundle), and the MCP Registry (`server.json`-driven). Each surface has its own publish workflow (`publish-npm.yml`, `publish-claude-plugin.yml`, `mcp-registry-publish.yml`, `publish-codex-plugin.yml`, `publish-tessl.yml`). Constrains the release pipeline to coordinate N parallel workflows; an artifact failure in one needs an explicit re-run rather than blocking the others. Appropriate when each registry serves a distinct discovery population.

### MCP Registry presence (`server.json`)

A separate `server.json` at repo root (distinct from `plugin.json` and `marketplace.json`) carries `$schema` pinned to `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`. Drives `mcp-registry-publish.yml`. The plugin reaches consumers through three discovery surfaces: npm registry, GitHub Release `.mcpb`, and MCP Registry. Constrains every release to update three registries; exposes the plugin to populations that don't search the Claude Code marketplace. Appropriate when the underlying server is genuinely MCP-shaped (not Claude-Code-specific). Most samples don't touch the MCP Registry; the marketplace and a single git/npm source are sufficient.

### Multi-registry: PyPI + MCP Registry + ghcr.io + Claude marketplace

Same plugin published to four discovery surfaces with four manifest formats: `plugin.json` for Claude Code, `server.json` for the official MCP registry, PyPI metadata via setuptools-scm, ghcr.io image (multi-arch). A separate `glama.json` (three-line maintainer declaration) targets glama.ai's MCP server directory as a fifth surface. The bump script keeps the local manifests in lockstep; CI handles the publishes. Appropriate when the author wants the server to be installable from whichever ecosystem the user already lives in.

### Dual-distribution: marketplace + npm

The same source ships as both a Claude Code plugin marketplace entry and an npm package (e.g., `ecc-universal`), with the npm `files:` list including the entire plugin payload. Users can `npm install -g <pkg>` or use the plugin marketplace. Appropriate when the audience overlaps with npm consumers. Constrains: every release must satisfy both packaging contracts (the npm publish gate is an additional release-time check).

### Cross-ecosystem multi-harness distribution

The same plugin payload also ships via parallel manifests for sibling AI harnesses (Codex, OpenCode, Cursor, Gemini), each with its own version-bearing file. The release script lists all of them as version-locked. Appropriate when the plugin is intentionally portable across harnesses. Constrains: cross-ecosystem manifest sync (validated by `validate-install-manifests.js` in one observed sample) becomes a CI concern; sibling-ecosystem changes ripple back into the Claude release.

### Marketplace + git-clone-only

Plugin metadata exists for Claude Code's plugin system but the primary install path documented in README is "clone the repo + paste this `.mcp.json` template into your own project, substituting your own absolute paths." Per-client templates for Claude Code / Cursor / Windsurf / Cline. The plugin is explicitly marketed as MCP-portable, not Claude Code-specific. The `.claude-plugin/plugin.json` becomes secondary; the load-bearing config is whatever the user pastes.

### Marketplace only

Plugins are installed via `/plugin marketplace add <owner>/<repo>` and that's the only intended path. No PyPI, no Docker, no git-clone instructions for the plugin functionality itself. Dominant pattern.

### Homebrew formula generated by release workflow

The release workflow synthesizes a Homebrew formula via heredoc (with per-platform URLs and sha256), clones a sibling `homebrew-tap` repo with a PAT, commits `Formula/<name>.rb`, pushes. The plugin is one channel; the tap is another. Orthogonal to the plugin but worth noting as an additional distribution surface for users who want the underlying tool system-wide.

### Cross-agent skill via `npx skills`

Plugin installable via `npx skills add <owner>/<repo>@<skill-name>` (skills.sh) in addition to the Claude Code marketplace. Two distribution channels for the same artifact. The skills.sh channel resolves into the agent's skills directory directly, whichever host the user is running.

## Distribution exclusion and dogfood layout

How the project decides what ships to consumers vs what stays in the repo, and how the project's own self-use shares content with the plugin install.

### `.claude-plugin/ignore` exclusion list

A 14-line ignore file alongside `marketplace.json` listing heavy dependencies (`packs/*/mcp/*/node_modules/`, `packs/*/mcp/*/dist/`), dev-only directories (`tests/`, `scripts/`, `examples/`), CI artifacts, and selected docs (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`). The plugin archive served to users is a curated subset of the repo. Distribution-shaping mechanism distinct from `.gitignore`.

### `.claude/skills/<name>` symlinked into `skills/`

Repo's own `.claude/skills/<name>` are git symlinks (mode 120000) into the top-level `skills/<name>/`. The plugin form (via `plugin.json` discovering `skills/`), the CLI install form (which copies `skills/*` into a consumer's `.claude/`), and the repo's self-use all share one source-of-truth set of SKILL.md files. Single content, multiple entry forms. Symlink fragility surfaces as regressions when an absolute symlink slips in (CHANGELOG: "absolute symlink restored to relative — broken on other machines").

### Repo-local developer skills exposed as plugin skills

`.claude/skills/<dev-skill>/` directories (e.g., `plugin-test-cycle`, `publish`) sit at repo root and are auto-discovered by Claude Code whenever the plugin is installed. End users see `plugin-test` and `publish` triggers that are meaningful only to the plugin author. Similar to seeing internal `.vscode/launch.json` entries leak into a distribution. Fix is either to scope these skills with a guard or to move them outside the plugin filesystem boundary.

### Repo-local hooks in `.claude/settings.json`

A `PostToolUse` hook wired in `.claude/settings.json` runs `make lint 2>&1 | head -30` on `Write|Edit|MultiEdit`. Repo-local developer tooling. File is committed and (depending on harness behavior) could leak into plugin distribution if Claude Code ever started harvesting it. Worth flagging because the plugin's own `hooks.json` does not declare this hook — the leak surface is settings, not the plugin manifest.

### Lockfile and node_modules inside plugin root

`package-lock.json` (~80 KB) ships inside the plugin filesystem; `node_modules/` materializes inside the plugin root after the user runs `npm install`. The `.claudeignore` filter at repo root has only a few entries (excluding metrics dirs and example folders) and does not gate the lockfile or future module trees. Constrains plugin update behavior: re-installing the plugin without clearing `node_modules/` produces a stale module tree the user must manually purge.

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

## Sandbox and security posture

Whether the plugin declares network/filesystem boundaries via Claude Code's sandbox settings.

### Default — no sandbox declaration

`settings.json` has no `sandbox` block; plugin runs with whatever permissions Claude Code grants by default.

### Explicit deny lists for cloud metadata and filesystem paths

`.claude-plugin/settings.json` declares `sandbox.failIfUnavailable`, `sandbox.network.deniedDomains` (including `169.254.169.254`, `metadata.google.internal`, `metadata.azure.com`), and `sandbox.filesystem.{denyRead, allowRead}` blocks. Explicit SSRF-defense posture; makes the plugin's threat model legible from the manifest.

## Governance and self-audit

How the plugin checks its own state for invariants beyond standard testing.

### Registration-list drift guard

A script (e.g., `scripts/verify-sync-to-active.sh`) cross-checks every `hooks/*.sh` against a `DESIRED_HOOKS` allowlist in the registration script, with an explicit `EXEMPT` list for opt-in-only hooks. Run in CI as a separate gate. Constrains every new hook to be either registered or explicitly exempted. Added in response to a specific regression where a hook shipped to the repo but never landed in the sync script (users got 12/13 hooks). Appropriate when the registration list and the inventory are maintained separately and the gap is a documented failure mode.

### Derived-artifact drift detector

A validator cross-checks two files where one is meant to be a derived projection of another — e.g., `tests/verify_triggers.py` cross-checks every `## Trigger phrases` list in `skills/*/SKILL.md` against the regex patterns in `hooks/check-skills.sh`. The SKILL.md is source of truth; CI fails on drift. Constrains every trigger-edit to update both sites. Appropriate when one artifact auto-completes from another by hand and the gap is high-value to catch.

### Self-observability via live API checks

A `test:congruence:live` step in CI calls the live GitHub API to verify the published "About" panel matches the repo's current state. Self-introspection during CI; depends on `GH_PAT` and external network. Constrains CI to occasional flakiness from API outages; provides drift detection between repo and registered metadata.

### Override file as documented bypass

The `.methodology-self-extend-override` sentinel file documents an opt-in suppression of hard enforcement. Mentioned in the plugin's defense-in-depth table. Constrains the hook's invariant to be "block unless this file is present"; surfaces the bypass in user-facing documentation rather than hiding it.

## Author identity and provenance

How owner / author metadata stays synchronized with reality and how plugin-name vs repo-name relationships are managed.

### Owner-rename in flight

A repo migrates from one owner to another (e.g., personal user → organisation). Code commits and homepage URLs update first; `marketplace.json.owner.name`, plugin `author.name`, and similar identity fields lag. GitHub redirect makes both URLs resolve to the same repo, but a consumer reading `owner.name` alone gets the pre-rename identity. No standard validator catches the inconsistency. Constrains long-running plugins to a periodic identity audit; the cost of fixing is low but the surface is wide.

### Plugin name vs repo name drift

Repo name (`token-reporter-plugin`) intentionally differs from plugin name (`token-reporter`). README warns users to install as `<plugin>@<marketplace>` to disambiguate. Constrains marketplace aggregators to track both names; users who type the repo name to install get nothing. Appropriate when the maintainer wants the repo namespace and the plugin namespace to be independent (e.g. multiple plugins in a shared repo or vice versa).

### Personal-email owner address

`owner.email` in marketplace.json is a personal Gmail rather than a role/group alias. Constrains the maintainer to handle marketplace-aggregator notifications personally; on owner rename or off-boarding, the email becomes stale.

## PATH augmentation and host-project setup

How the plugin handles user-installed CLIs that aren't in the minimal PATH Claude Code propagates, and how it scaffolds in the user's host project.

### PATH-bootstrap script sourced by every hook

A `scripts/path-bootstrap.sh` prepends common user bin dirs (`$HOME/.ship/bin`, `/opt/homebrew/bin`, `/usr/local/bin`, `$HOME/.local/bin`, `$HOME/go/bin`) to PATH. Sourced from the top of every hook script. Driven by the observation that "Claude Code and some CI environments inherit a minimal PATH that excludes common install dirs" — an adaptation layer for missing-PATH pathology rather than a plugin-managed install of those tools.

### Runtime-environment sanitization at invocation site

A skill wraps third-party CLI invocations in `env -u <VAR> <cli>` to defend against user-environment contamination — specifically `env -u BUN_INSTALL` to prevent Bun's bundled SQLite (which lacks extension loading) from being picked up over Node when invoking a tool that needs SQLite extensions. Plugin-side defense at the skill level rather than at install time.

### Auto-shell-rc modification

`install.sh` detects user shell and writes PATH-append lines to shell rc files (`bashrc`, `zshrc`) with idempotency guards. Crosses the line from "install under `~/.claude`" to "modify user dotfiles" — most plugin-era patterns avoid this because plugin uninstall cannot reliably reverse the shell-rc edits.

### Plugin-distributed MCP server

A plugin ships `.mcp.json` inside its plugin tree, registering an MCP server (e.g., a Bun/TypeScript channel server) that the plugin distributes. Substituted via `${user_config.<KEY>}` for env values. Travels with the plugin to consumers. Constraint: the plugin must also ship the server source (`channels/<name>/server.ts`) and its dep-install hook.

### Repo-root MCP server for contributor use

A `.mcp.json` lives at repo root (not under any plugin tree) registering a peer MCP server for use by skills during local development of the plugin itself. Consumers installing via `/plugin install` don't inherit this — it's not part of the plugin tree. Contributors clone the repo and get the MCP wiring as part of working on the plugin source. Distinct role: plugin-distributed MCP travels to users; repo-root MCP serves the maintainer.

### Setup script writes scoped entries into target project's settings.local.json

A bash script under `bin/` (e.g., `setup-permissions.sh`) writes an enumerated allow-list of specific paths and command shapes into the target project's `.claude/settings.local.json`. Examples: specific script paths, project-relative glob shapes (`./<tool>.sh*`), narrow git operations (`git checkout -b <prefix>/*`, `git commit -m "<prefix>:*"`, scoped `git add`/`log`/`diff`/`status`/`rev-parse`), plus the `statusLine` block. Existing `permissions.allow` entries are preserved; duplicates skipped. Allow-list-first (not `*`-blanket) — each grant is the narrowest pattern that lets the workflow function. Constrains: the grant set is plugin-author-curated; expanding the workflow requires editing the setup script and re-running. The grants live in the user's project, not the plugin, and persist across plugin updates until the user removes them.

### Setup script scaffolds the host project

A `scripts/setup.sh` (often invoked via a `/<plugin>:setup` slash command) creates a project-local config directory (e.g., `.coco/`), populates a default config file, installs git hooks into `.git/hooks/` of the host project, merges plugin permissions into the host's `.claude/settings.json`, and adds plugin artifacts to the host's `.gitignore`. Migration logic (e.g., legacy slug rename) may also be embedded. Most plugins leave host-project setup to the user; this approach takes ownership. Trade-off: setup script in-tree and slash-command both invoke the same scaffolding and the duplication is real; one path is sometimes legacy. Aggressive scaffolding mutates the host project in ways the user must re-discover when they move to a fresh checkout.

### None (plugin operates standalone)

The plugin requires no host-project scaffolding. State and config live entirely under `${CLAUDE_PLUGIN_DATA}` or are derived from the user's existing repo without modification. Appropriate when the plugin is self-contained and the host project is a passive subject of the plugin's operations.

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

## API-cost transparency and cost-gated MCP tools

Whether the plugin discloses runtime cost to users and how it constrains paid or rate-limited tool surfaces.

### Explicit cost-model section in README

README's "API Cost Model" section quantifies the agent-hook cost at ~$0.15-0.30 per session with a per-hook breakdown table, and provides an explicit opt-out (`agent_hooks: false` in `userConfig`). Rare for plugins to publish cost transparency; novel surface.

### Per-call rule gates plus pinned tool subset

A paid MCP integration is opt-in and rule-gated (e.g., `icp_score >= 7` or `priority: high/urgent`, always confirmation-gated, forbidden in specific stages of a workflow). The MCP server URL pins a narrow tool subset via query string (`?tools=docs,code_crafter/leads-finder,...`) so even a rule-bypass cannot reach the broader API surface. Rule enforcement is distributed across multiple agent prompts and a `templates/CLAUDE.md` that downstream sessions read. A defensive configuration move — pinning the tool subset at the URL is structural (cannot be widened by prompt drift), while the rule gates are normative (depend on agent compliance).

## Output styles

Whether the plugin ships shared report formats agents and skills reference.

### Shared markdown templates under `output-styles/`

3+ markdown files at `output-styles/` (e.g., `session-report.md`, `finding-report.md`, `wave-summary.md`) define the prescribed output shape for skill or agent emissions. Agents and skills reference these by path, ensuring report consistency across the plugin's surface. Layer not always documented in plugin docs but legitimately registered via convention discovery. Constrains the plugin to maintain template-to-consumer coupling — a template rename requires updating every reference.

### No output styles

Plugin ships no `output-styles/` directory. Skills and agents emit free-form output, with consistency enforced (or not) at the prose level only.

## Explainable state machine surface

How the plugin exposes its internal state to the agent.

### CLI verb returning structured state explanation

A first-class CLI verb (e.g., `<tool> explain`) prints `Health / Mode / Failure / Action / Reason / Baseline / Best / Last / Streaks` from the persisted state plus a segment summary plus config. The agent is instructed to call it on resume and after any ambiguity. Makes the state machine introspectable by the agent itself, not just by the user.

## Novel and cross-cutting concerns

Patterns surfaced by samples that don't fit a single role above.

### MCP "channel" as inbound event bus

One sample ships an MCP-channels-as-inbound-event-bus pattern (research-preview Claude Code feature gated to v2.1.80+ and `claude.ai` login, not API-key auth). The channel server (Bun/TypeScript) declares `claude/channel` capability, exposes HMAC-gated webhook routes (`/tradingview`, `/polymarket/fill`, `/cdp`, `/commerce`, `/custom?kind=...`), and converts each inbound event into a `<channel source="..." type="..." ...>...</channel>` context tag inside the running Claude session. Distinct primitive from `monitors.json` (outbound stdout lines) and from normal MCP tool servers (stateful request/response). One-way inbound only — README claims "NO reply tool, NO permission relay."

### MCP server reads hook-authored artifact

MCP server's tool surface is a projection of state authored by hooks: a hook (`stop.js`) writes `docs/<plugin>/map.md` via `atomicWrite` after parsing the project; the MCP server (`mcp/server.js`) parses that map and `watchFile`s it with a 500ms debounce. Decouples MCP responsiveness from heavy parsing cost — MCP doesn't parse source, it parses the rendered map. Cross-component data flow (hooks produce, MCP consumes) without RPC or shared-memory coupling.

### Generated-package.json pattern

A SessionStart install script writes a minimal `{"private":true}` `package.json` into `${CLAUDE_PLUGIN_DATA}` on first run rather than shipping one. Keeps the plugin repo free of Node-ecosystem noise (no committed lockfile, no `node_modules/` gitignore, no committed dep manifest) while still giving npm a valid project to operate on. Authoritative dep declaration lives inline in the install script's `npm install <pkg>` command.

### Graceful-degradation via fallback tool

When a plugin's optional tool (installed by SessionStart) is missing, the skill falls back to a manual stdlib-only path (e.g., `wiki/index.md` read + grep instead of `qmd` query). Documented fail-soft inside the skill body, not an install retry. The plugin works in reduced mode even if dep install permanently fails. Pairs with the install script's fail-open stance.

### Cool-off window on event-driven regeneration

`hooks/stop.js` skips map regeneration if the output file's mtime is within the last 60s, to avoid redundant work when a manual refresh just ran. Explicit de-dup window for event-driven artifact regeneration.

### Test stack — Docker

Cross-role: Docker also surfaces under *Server runtime (MCP)* via `docker run`, under *Cross-ecosystem distribution* via ghcr.io image, and under *Release automation* via the multi-arch build pipeline.

- **Docker Compose for E2E** — `e2e.yml` brings up a full Docker Compose stack (e.g., the upstream service + an OIDC provider) before running the e2e-marked subset. Pinned to a single Python version (no matrix) — e2e is an integration check, not a portability check. Appropriate when the system under test is meaningful only against a real running peer.

## Cross-role tools

Tools that fill multiple roles in the corpus and are named under each role's section above.

### Python (stdlib + pip + uv)

Python 3.10+ appears as: the runtime for hook scripts (stdlib only when zero-dep policy in force; pip + third-party when not), the install-script language (`install.py`, `ensure-deps.py`, `auto_install.py`), the mock HTTP server in install E2E tests (`mock_server.py`), the test framework (`unittest` stdlib, pytest, stdlib-rubric scripts), CI inline validation (heredoc Python in ci.yml steps), YAML/markdown parsing in shell scripts (inline `python3 -c "import yaml; ..."`), and helper-script runtime (session_state.py, metrics-query.py, yaml-parser.py invoked via `python3` on system PATH). Different roles use different sub-uses (stdlib only vs pip + third-party vs `uv run --with` vs PEP 723 inline).

### Node + npm + npx

Fills runtime (worker daemon, MCP server, npm CLI, hook handlers as `.mjs`), dependency installation (`npm install --prefix`, `npx --yes --package`), bin-wrapped CLI distribution (npm bin entry point), test stack (`node --test` test runner, vitest, custom node-test runners), and release automation (`npm publish --provenance`).

### Bun

TypeScript runtime for bin-wrapper (Bin entry mechanism); Node-modules installer in self-heal path (Dependency installation); test runner via `bunx vitest run` (Testing); skill-validator host (Marketplace validation).

### bash

Fills bin-wrapped CLI distribution (thin exec-wrappers, cross-platform shims), hook scripts (file-guard, post-write-check, session-start), install scripts (install-deps.sh, install.sh), test stack (run-tests.sh hierarchical bash test suites, bats), and failure-signaling envelope (the `set -uo pipefail` + `trap ERR` pattern). Hot-path POSIX `/bin/sh` discipline distinguishes it from one-shot bash use.

### Docker / npm packages / package.json

Dep manifest format (Dependency installation); bin-entry surface for npm distribution (Bin entry mechanism); release publication target (Release automation); MCP server runtime via `docker run` (Server runtime); ghcr.io image distribution (Cross-ecosystem distribution); multi-arch build pipeline (Release automation).

### SQLite

Fills state persistence (`metrics.db` for behavioral metrics) and is consumed by both the worker daemon and the MCP server in a peer-process architecture (per-call DB resolution, atomic writes).

### `jq`

Fills hook output construction (building `hookSpecificOutput` JSON, escaping context with `jq -Rs .`), CI manifest validation (`jq empty` parseability and `jq` queries for name-equality), bin-wrapped CLI input synthesis (reconstructing the PostToolUse envelope via `jq -n`), version extraction from `plugin.json` in download shims (Dependency installation), zero-dep stance prerequisite (Identity and brand stance), and tool-call payload parsing in PreToolUse path validators (Tool-use enforcement).

### GitHub Actions cron

Fills external-change watcher (weekly/monthly cron workflows polling release pages, API changelogs, community signals), CI workflow shape (PR validation, release publish on tag, autonomous loops, cross-repo notify), and long-running scheduled behavior (outsourced cron loops).

### `softprops/action-gh-release@v2`

Release-creation mechanism in tag-conditional step, dual-workflow split, snapshot path, and prebuilt-binary matrix (Release automation); native-artifact upload step (Native artifact distribution).

### `${CLAUDE_PLUGIN_ROOT}` env var

Used by hook wrappers to locate the plugin's bin scripts; used inside `config/config.json` for resource paths (expanded by the plugin's own runtime, not by the host); used in `hooks/hooks.json` to locate hook scripts; code/cache directory in plugin/state separation (Plugin/state separation); inline-config path interpolation in plugin.json (Plugin-component registration); env-var fallback in bin wrappers (Bin entry mechanism). The same env var fills "find my own files" across multiple roles and underpins the runtime resolution variable chain in state persistence.

### `${CLAUDE_PLUGIN_DATA}`

Install destination for managed deps (Dependency installation); state directory in plugin/state separation (Plugin/state separation); native binary install location (Native artifact distribution); bin wrapper venv resolution (Bin entry mechanism).

### `$CLAUDE_ENV_FILE`

Cross-hook env propagation (Cross-hook environment plumbing); userConfig-to-dotenv bridge (User configuration); SessionStart writing env vars (Session context loading).

### `hookSpecificOutput.additionalContext`

Context-injection channel in SessionStart welcome-state path (Session context loading); same channel in PostToolUse skill-nudge path (Tool-use enforcement); same channel in UserPromptSubmit fuzzy-match path (Session context loading); fail-open dep-install advisory (Dependency installation).

### `plugin.json.version`

The same string drives user-facing version display, the install-skip predicate (matched against a stamp file), the lazy-download URL for the matching binary asset, and (often, fragilely) banner version literals embedded in hooks. Triple-or-more-duty as both data and control signal across version coordination, install change detection, and session context loading.

### Bash `case` + Python validator pattern

Inline `case "$input" in <pattern>) python validator ;; esac` in hooks.json fast-paths 99% of unrelated calls without paying Python startup cost. The here-string `<<< "$input"` safely passes JSON with embedded quotes. Surfaces under PreToolUse hook (auto-allow scripts) and tool-use enforcement (gating).

### Git as state substrate

Git fills branching and tag placement at the release layer, `<git-common-dir>/` as a state-storage root for mission state (state persistence), worktree creation as the per-role isolation mechanism (Agent declaration conventions), and the underlying mechanic of marketplace install (clone-or-update of a remote repo). Each role uses a different facet.

### GitHub Releases

Primary download source for native binaries (Native artifact distribution); same surface used by binary-download dependency-install paths (Dependency installation); release pipeline target (Release automation).

### `/tmp/`-based filesystem state

Daemon coordination via socket/PID/refcount (Sidecar daemon and IPC lifecycle); cross-hook flag-file coordination (Cross-hook environment plumbing); session-scoped one-shot nudge marker (Tool-use enforcement).

### macOS Gatekeeper handling (`xattr -d com.apple.quarantine`)

Post-download install step (Dependency installation); same step in bin-wrapper lazy-download path (Bin entry mechanism); native artifact post-extract step (Native artifact distribution).

### CHANGELOG.md

Release-notes source for `taiki-e/create-gh-release-action@v1` (Release automation); auto-generated by `git-cliff` (Tag and release lifecycle); part of the documentation surface (Documentation surface).

### Codex / OpenAI runtime

Co-distribution via sibling `agents/openai.yaml` (Cross-platform skill publishing); npx-based install target alongside Claude (Multi-runtime portability, Cross-ecosystem distribution); manifest convention difference (Plugin-component registration).

### Docker (largely absent in some bins)

Docker does not surface in some sample sets as a runtime, distribution, or test-stack tool. Worth flagging the absence — many plugin ecosystems lean on Docker; some subsets of this corpus do not.
