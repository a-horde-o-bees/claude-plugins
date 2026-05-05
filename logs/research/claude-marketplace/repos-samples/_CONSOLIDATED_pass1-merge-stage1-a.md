# Sample

Merge of 6 partials (bins 1-6) into `_CONSOLIDATED_pass1-merge-stage1-a.md`. Functional roles with implementation paths and qualitative descriptions; no inline citations (see `references` verb for provenance).

## Marketplace manifest layout

Where the marketplace-discovery JSON lives in the repo, what shape it takes, and how it relates to the plugin payload it advertises.

### No marketplace manifest (plugin source repo only)

The repo carries only `.claude-plugin/plugin.json`; no `marketplace.json` exists anywhere in the tree. The marketplace listing, when present, lives in a sibling repo (often controlled by the same author) that points at this repo as a source. The plugin repo is a leaf source, not an aggregator. Consumers wishing to install via marketplace tooling must add the repo with an explicit subdirectory pointer authored by the aggregator. Appropriate when the author wants discovery handled by a separate aggregator or expects discovery to flow through a third-party catalog; the trade-off is no self-advertised category, tags, or version metadata at the marketplace layer, and forks become installable only after publishing through the sibling marketplace.

### Self-referential single-plugin marketplace at repo root

A single `.claude-plugin/marketplace.json` co-located with `.claude-plugin/plugin.json` at repo root, with one plugin entry whose `source` is `"./"` — the marketplace and its sole plugin share the same repo root. The marketplace manifest may declare `metadata.{description, version}` or only flat top-level fields; either way it advertises one entry pointing back at the same root. Lowest-overhead pattern: one `git push` ships both the storefront and the wares. Appropriate when one repo ships exactly one plugin and the author wants the repo itself to be installable as a marketplace. Constrains the plugin's filesystem layout to start at repo root — any repo content (CI configs, `node_modules/` after install, contributor docs) sits inside the plugin's filesystem boundary unless filtered. Often produces visually-confusing install strings (e.g. `<name>@<name>`) when repo, marketplace, and plugin names coincide.

### Single root manifest with relative source under `plugins/<name>/`

`.claude-plugin/marketplace.json` at repo root with `plugins[0].source: "./plugins/<name>"` (or `"./plugin"`) pointing into a subdirectory holding the actual plugin. The marketplace is the door to it. Suits repos that anticipate hosting more plugins, that separate plugin source from repo-level scaffolding (docs, dashboard source, dev scripts), or that need the repo to carry non-plugin content outside the plugin tree. Forces a dual-source-tree discipline when paired with packaged-copy layouts (see *Source layout*).

### Duplicated marketplace manifest at root and nested

Two `marketplace.json` copies coexist — a canonical one at repo root (consumed by Claude Code's `marketplace add`) and a duplicate elsewhere (`.github/plugin/`, `plugin/.claude-plugin/`, or `plugins/<name>/.claude-plugin/`) — with often-identical content but no sync mechanism. Only the canonical path is consumed; the duplicate appears to be aspirational (aimed at GitHub Pages, an alternate host CLI, or a different discovery surface), iteration leftover, or vestigial. Both files may carry unofficial private keys (e.g. `_description`) outside the documented schema. Drift-prone — release commits routinely bump one and miss the other, surfacing as hot-fix commits ("bump repo-root marketplace.json to <version>"). CI manifest-equality checks may cover only one of the two copies. Appropriate to flag as an anti-pattern: doubles the manual-edit burden during a release with zero observable upside.

### `$schema` declaration on marketplace.json

A declarative `$schema: "https://anthropic.com/claude-code/marketplace.schema.json"` field on the marketplace document. No CI step actively validates against the schema in any observed sample, so the field is editor-assistance only — IDEs offer field completion and inline error squiggles. Largely absent across the corpus; an outlier when it appears. Appropriate when an author wants editor-time validation without committing to wire-up of a real schema-validation gate.

### Custom non-schema fields on marketplace entries

Fields not in any documented marketplace schema, used as de-facto extension points. Observed: `images: [url]` carrying marketing-asset URLs, `tags: ["community-managed"]` flag distinct from `keywords` and used as a provenance signal. Permissive consumers ignore these; strict consumers reject them. Constrains validator choice — strict schema enforcement breaks. Appropriate as a forward-compatible extension hook when no upstream field exists for the metadata the author wants to expose.

### Redundant metadata sub-object on plugin entries

A nested `metadata: {}` dict on a plugin entry that duplicates sibling fields (`author`, `homepage`, `license`, `keywords`, `category`). Two locations on the same entry carry the same facts; `keywords` and `tags` arrays may also be identical. Constrains validators that want to enforce single-source-of-truth — a drift detector has to either pick a winner or accept divergence. Appears to be a layering accident from generators or from manual edits across two different consumer expectations.

## Marketplace metadata wrapper

Marketplace-level (not plugin-level) descriptive fields the manifest declares — flat top-level fields versus a `metadata` object.

### Flat top-level fields only

Top-level `name`, `owner`, `plugins`, `version` directly on the JSON root. No `metadata` wrapper, no `metadata.description`, no `metadata.pluginRoot`, no `$schema`. Minimal scaffolding; works but provides no structured place for marketplace-wide description or root-relative plugin-tree base.

### `metadata.{description, version}` wrapper without pluginRoot

A `metadata: {description, version?}` object at the top of marketplace.json alongside `name`, `owner`, `plugins`. Often paired with `owner.{name, url}`. `metadata.pluginRoot` is generally absent — single-plugin manifests bind via `source` instead. The marketplace-level `version` is documented as marketplace-bundle version rather than plugin version and is decoupled from any individual plugin's `version`, so it tracks an independent (often stale) cadence — observed cases of marketplace `version: 1.0.0` left frozen while the plugin inside ships `2.0.5`, `0.5.1`, or 35 minors ahead. Consumers expecting a single authoritative version see drift; the marketplace version is rarely surfaced to users so the drift goes unnoticed by maintainers.

## Per-plugin discoverability metadata

Fields on the marketplace entry and `plugin.json` that drive search, categorization, listing, and recognition.

### Minimal metadata only (name, description, version)

The plugin advertises only `{name, description, version}` in `plugin.json` — no `category`, `tags`, `keywords`, `author`, or `repository`. Marketplace entry, when present, mirrors this minimum. Appropriate for early-development or stub plugins where discoverability is not yet a concern; the cost is zero presence in any category-based or tag-based marketplace browsing.

### Keywords-only on plugin.json

Marketplace entry carries minimal metadata (`name`, `version`, `source`, `description`); `keywords` lives exclusively in `plugin.json`. No `category` or `tags` on the marketplace surface, so category-based browser filters cannot surface the plugin. Authoring overhead is low (one list, one location), at the cost of marketplace-side filterability. Often paired with `plugin.json` carrying a slightly different `keywords` list creating a second drift surface.

### Category + tags on marketplace, keywords on plugin.json

Marketplace entry declares `category` (single string, commonly `"productivity"`) and `tags` (array — e.g., `["team", "agents", "automation", "project-management"]`); `plugin.json` separately carries `keywords`. Both surfaces are populated, but the two lists drift independently — tags meaningful at the marketplace level (e.g., `rule-engine`, `ci`) and keywords meaningful at the plugin level (e.g., individual technologies, methodology names) overlap partially. Two discovery vocabularies with no single source. A search via one surface misses tokens only present in the other; no tooling reconciles them.

### Fully populated discoverability

Marketplace entry sets `category`, `tags`, `keywords`, `description`, `author`, `homepage`, `repository`, and `license` together; `plugin.json` mirrors fields at the plugin layer. Plugin appears in browsing flows that filter by any axis. Tags and keywords overlap heavily — `keywords` is sometimes documented as redundant with `tags` and pruned from sibling configs but persists at the marketplace level. Appropriate for plugins seeking maximum discoverability; the cost is a duplication burden when the marketplace entry mirrors fields already in `plugin.json` and each axis adds maintenance surface.

### No discoverability fields on marketplace entry

Marketplace entry exposes neither `category` nor `tags` nor `keywords`, even when `plugin.json` has its own `keywords` array. The `$schema` reference may still be present (the schema does not require these fields). Plugin is reachable only by direct install URL; browsing flows will not find it.

### `strict: false` without override array

`strict: false` set on the plugin entry without a corresponding `skills`/`agents`/etc override array. Semantically unnecessary for normal discovery — `strict` only matters when carving components out of a non-standard layout. Reads as defensive ceremony or copy-paste; a reader cannot tell from the manifest what protection it provides.

### Repo-level GitHub topics

GitHub repository topics (`agent-skills`, `ai-coding`, `semantic-search`) declared on the GitHub repo itself, not in any manifest. Drives GitHub search but not Claude Code's marketplace UI. Useful complement to manifest discoverability when the project also wants discoverability through GitHub's surface.

## Plugin source binding

How the marketplace entry locates the plugin payload on install — relative path, GitHub coords, npm package, or other source form.

### Relative source pointing to repo root

`"source": "./"` on the marketplace entry; plugin root and repo root are the same path. Pairs with the self-referential single-plugin marketplace pattern. Trivial to author and audit; works only when the repo hosts exactly one plugin at root and ships nothing the plugin doesn't include. Makes `plugin.json` the de-facto version-of-record (per docs convention for relative sources), but does not prevent the marketplace entry from carrying its own `version` field that drifts.

### Relative source pointing to subdirectory

`"source": "./plugin"` (or similar relative path) when the plugin payload lives in a subdirectory of the marketplace repo. Keeps marketplace and plugin colocated in one repo, with the manifest pointing at a child folder. Necessary when the repo carries non-plugin content (docs, dashboard source, dev scripts) outside the plugin tree.

### `source: github` with explicit coords

The marketplace entry points at a GitHub repo by `owner/repo`; `/plugin install` clones the repo at HEAD or at a specified ref. Installs survive registry outages but depend on GitHub availability. Forks are first-class — install URL changes, install path same. Appropriate when the plugin author wants direct fork-friendliness and is willing to push releases as git refs rather than registry artifacts.

### `source: github` with subdirectory pointer (consumer-authored)

When the plugin lives under a non-root path (e.g. `plugin/`) and no marketplace.json exists in the same repo, any external marketplace that lists this plugin must author a `source: { source: "github", repo: "<owner>/<repo>", path: "<subdir>" }` entry by hand. Appropriate when the author wants to publish a plugin from a non-conventional layout but accepts that downstream marketplaces carry the binding logic.

### `source: npm`

The marketplace entry is `{ "source": "npm", "package": "<name>" }`; `claude plugin install` resolves the package against the public npm registry. Constrains the plugin to be a Node package and pulls in npm's distribution surface (CDN propagation delay, dist-tags, `npm unpublish` risk). A user cannot install a fork or PR until the fork is published to npm under a different name. Appropriate when the plugin is fundamentally a Node CLI with broader reach than just Claude (the same package powers Claude Desktop, Cursor, OpenCode, etc.); the Claude plugin entry is then a thin alias of the npm package.

### `url` self-referencing source

`{"source": "url", "url": "https://github.com/<owner>/<repo>.git"}` where the marketplace manifest points back at the same repo it lives in. The marketplace and plugin payload ship together but the marketplace install treats the repo as a remote source. A locally-cloned-but-uninstalled checkout isn't usable as a marketplace source without `url` rewriting or switching to `relative`. Appropriate when the project plans to publish to a wider marketplace but isn't yet there.

## Source layout

How the files the plugin needs at runtime are organized in the repo, independent of how the marketplace entry binds to them.

### Single tree (plugin equals repo)

Plugin manifest at `.claude-plugin/`, components (skills, commands, hooks, agents, bin) at conventional top-level directories. Simplest layout; no synchronization burden. Appropriate when the repo's only purpose is the plugin and there is no separate authoring/distribution distinction.

### Dual tree with sync gate

Authoring sources live at repo root (`/hooks/`, `/bin/`, `/audio/`, `/config/`) and a packaged copy lives at `plugins/<name>/...`. A reconciler script (e.g. `build-plugin.sh [--check]`) does `cp + cmp -s` to keep them in sync; CI runs the same script with `--check` to fail PRs that drift. Justified when Claude Code's plugin cache treats `plugins/<name>/` as a self-contained unit but the author wants a cleaner top-level surface for non-plugin tooling, tests, or cross-target packaging. Cost: every change to a hook, bin, or config file is a two-place edit unless the author runs the reconciler.

### Generated manifests from upstream config

Plugin manifests (`plugin.json`, `hooks.json`, `settings.json`, `agents/*`, `monitors/monitors.json`) are emitted by a `sync` subcommand of an in-repo binary that reads a single authored source (`harness.toml`). The committed manifests are derived artifacts; a CI consistency check verifies the working tree matches what `sync` would produce. Inverts the usual "manifest is hand-authored" assumption; appropriate when the plugin's surface is too large or schema-fragile for hand maintenance and when a custom binary already exists to interpret the upstream config.

## Version coordination

Where the canonical version string lives, how many independent copies must stay in sync, and what enforces lockstep — drift is the dominant failure mode.

### Single source of truth (`plugin.json` only)

`plugin.json.version` is the only user-facing version of record; the marketplace entry has no `version` field of its own. Git tags use plain `vX.Y.Z` matching `plugin.json` one-to-one as a release-discipline convention rather than a structural enforcement. A `pyproject.toml` may carry its own `version` field that drifts (frozen at `0.0.1` while plugin.json advances) — not consumed by anything user-facing, only by pip metadata, so the drift is immaterial. Single-source clarity; risk lives only in tag-vs-manifest drift, not in cross-file drift. Rare in the observed corpus — most samples maintain at least two independent copies.

### Dual-file version (manifest pair)

Both `plugin.json` and `marketplace.json` carry `version`. The pair must be edited together on every release; a single-file edit produces drift the install path will not catch. Drift is detected by humans or by a CI consistency script. CHANGELOG narration in some samples explicitly documents shipping a release where some sites updated and others didn't, motivating retroactive addition of CI version-bump checks.

### Triple-file version (build manifest joins)

Three sites carry the version: `plugin.json`, `marketplace.json` (often two slots — top-level `metadata.version` plus `plugins[i].version`), and the language ecosystem's build manifest (`Cargo.toml`, `package.json`, `pyproject.toml`). Drift mitigated procedurally — by a documented release skill, a manual checklist, or by convention — rather than structurally. Hot-fix commits explicitly titled "bump repo-root marketplace.json to <version>" surface when the discipline slips. Release CI may gate `tag == package.json.version` only — drift between `package.json` and the plugin-side manifests is not caught structurally. The sibling-harness manifest (`gemini-extension.json`) can join as a third site in cross-ecosystem distributions.

### Multi-site sprawl (5+ locations)

Version scattered across `plugin.json`, two slots in `marketplace.json`, a top-level `VERSION` file, the language build manifest, README badge(s), CHANGELOG, hardcoded source-code literals (e.g., MCP server's `version: "0.1.0"`), CLAUDE.md "Current version" line, hook banners, and sometimes mock-output version inside test fixtures. No generation or sync mechanism; each release is many hand-edits. A `scripts/bump-version.sh <new>` (when present) patches all sites in one invocation; CLAUDE.md additionally maintains a "Version Sync Checklist." The script can be substrate-fragile (e.g., `sed -i ''` BSD-syntax fails on GNU Linux sed) — author's local platform leaks into a shared release tool. Solves the multi-file problem with project-local tooling rather than runtime indirection.

### Atomic-bump release script with pre-push gate

A local-only Python or Node script (e.g. `scripts/publish.py`, `scripts/bump-version.mjs`, `scripts/sync-version.js`) bumps every version-carrying file in one step, then re-runs the schema validator post-bump to confirm parity. Generalizes to ~15 manifests/HTML pages syncing from one source (`package.json` as authority). The same script in `--check` mode runs in pre-commit, CI, and publish workflows to fail builds on drift. A process-ancestry pre-push gate (walks `ps -p <pid> -o args=` rejecting any push not driven by the script) prevents the gate from being bypassed; env-var/marker-file schemes are "trivially spoofable" by comparison. Constrains every contributor to either run the writer script before commit or accept a CI failure. Appropriate when the version surface is genuinely large and a per-file manual checklist would be impractical.

### Pre-commit hook auto-sync (consistency, not increment)

Git pre-commit hook (`.githooks/pre-commit` installed by `scripts/install-git-hooks.sh`) detects mismatch between a `VERSION` source-of-truth file and `plugin.json`/`harness.toml` and runs `sync-version.sh sync` to mirror, re-staging the corrected files. Does not auto-bump; bump itself is manual via `sync-version.sh bump [patch|minor|major]`. The hook only enforces consistency, not increment. Pre-first-release projects (`0.0.z` until first `v0.1.0`) sometimes auto-bump `z` per commit via this hook to keep reload-detection firing.

### Manual checklist with rubric-based audit

No bump automation; release-prep PRs hand-edit each version-carrying file (5+ files: `plugin.json`, marketplace.json, README badge, README.ru badge, per-skill `metadata.version`). A separate machine-checked rubric (e.g. `tests/meta_review.py` gates `M-C5`/`M-C6`) runs in CI and validates that all files agree on a single version. Catches drift but does not prevent it. The rubric is the safety net rather than the guard rail. Appropriate when the maintainer prefers explicit-edit discipline and treats CI as the late-stage drift detector.

### Cross-repo registry-side sync

The marketplace listing in a sibling repo is a third version sync point, kept in lockstep via a webhook-style notifier (`repository_dispatch` `plugin-updated` event, PAT-gated, fired on `.claude-plugin/plugin.json` change). Constrains the publish flow to a cross-repo coordination dance even after intra-repo bumps are clean.

### Multi-site drift accepted as cosmetic

Five-or-more sites advertise different versions intentionally or accidentally: `plugin.json`, `VERSION`, `pyproject.toml`/`package.json`, CHANGELOG, README badge, hook banners, and the git tag may all be at different versions (e.g. `5.0.0-alpha` vs `4.2.0` vs `2.0.0` vs `3.0.0-dev`). The pattern can be deliberate ("marketplace only advances at stable release") or accidental drift. Pre-release suffix handling (semver vs PEP 440 vs tag) compounds the inconsistency: `5.0.0-alpha`, `5.0.0a1`, and `v5.0.0-alpha` are three forms of the same version that downstream sorting rules may not reconcile. Release process accepts the drift as cosmetic; users see different version strings depending on which surface they look at.

## Channel distribution

Whether the plugin offers stable / latest / dev channels, how consumers pin a version, and whether the channel mechanism operates at the marketplace, branch, or artifact layer.

### Single channel — tag-on-main with git-ref pinning

No channel split; users install via `/plugin marketplace add <owner>/<repo>` and pin via `@ref` (`@main` for rolling, `@vX.Y.Z` for a specific tag, or commit SHA for frozen). Every commit on `main` is a release candidate; tags `vX.Y.Z` land on main. Constrains rollback to git-ref pinning by the consumer rather than channel switching by the publisher. Appropriate for solo or small-scale plugins where formal release ceremony is not warranted; the cost is no easy "give me the last known-good" label without naming a specific tag.

### Linear `0.0.z` dev counter

The repo's only versioning scheme is a monotonic `0.0.z` counter — every tag bumps `z`, with no `0.1.0` carve-out and no parallel `x.y.z` release lane. Tags `v0.0.1`..`v0.0.z` chain linearly on `main`. Appropriate for pre-release / experimental plugins where every commit is essentially a dev snapshot; the cost is no signal of stability and no inflection point to mark "first real release."

### Pre-release tag suffixes on a single channel

Tags carry a `-alpha` / `-beta` / `-rc` / `-dev` suffix to mark pre-release status (e.g. `v5.0.0-alpha`, `-alpha.N`, `-beta.N`, `-rc.N`). GitHub Releases marks the corresponding release `prerelease: true` correctly. PEP 440 form (`5.0.0a1`) appears on `pyproject.toml` for Python tooling compatibility. Code-side helpers (`isPrereleaseVersion()`) feeding `--prerelease` to `gh release create` may exist without any actual prerelease tags published — infrastructure-ready but cold. Users can pin to a specific pre-release tag, but installing from `main` always lands on whatever `plugin.json` currently says, including in-development `-dev` versions. Appropriate when an author wants to ship versioned snapshots without claiming stability; the cost is uncertain handling by Claude Code's plugin semver parser, which is undocumented for pre-release suffixes.

### Aggressive minor-only cadence with reactive patch bursts

Every shippable change cuts a minor (10 minors in ~1 month observed); no patch releases, no pre-release suffixes. Implies the project treats every visible change as user-facing. CHANGELOG.md becomes the only durable release-notes artifact since GitHub Releases (when present) are auto-generated from PR titles via `--generate-notes`. Reactive patch bursts (multiple patch releases within hours, e.g., v3.4.1 → v3.4.4 in 36 hours) indicate absence of a buffer between development and release; every push reaches users immediately. Forces tight feedback loops in CI to compensate.

### Single channel with version-reset across rebrand

Plugin moves through major versions under one name, then resets to `0.1.0` under a new name. Users pinned at `<old-name>@vX.Y.Z` do not auto-update because the plugin name changed; the rebrand is communicated via README/CHANGELOG only, not enforced in the manifest. Identity transition is a soft event — the marketplace cannot bridge it.

### Marketplace-cache invalidation hack

Patch-level version bump committed with no functional change, intended solely to force the marketplace cache to re-pull a prior release. Documented openly in CHANGELOG ("Patch bump to force the marketplace to pull v2.3.0's bundled-MCP changes. No code changes vs 2.3.0."). Symptom of having no control over marketplace refresh timing and no immutable release artifact.

### Dual-asset filename aliasing on GitHub Release

Both a versioned filename (`<plugin>-v1.14.1.mcpb`) and a channel-aliased filename (`<plugin>.mcpb`) are uploaded to the same release via `cp`. The channel filename rolls forward with each release; the versioned filename pins. Orthogonal to marketplace channels — operates at the GitHub Release artifact layer. Constrains consumers to choose at download time which lifecycle they want. Appropriate as a lightweight alternative to maintaining parallel `stable-*`/`latest-*` marketplace manifests.

### Disabled-channel skeleton

Release-channel infrastructure that exists in code but is intentionally inert until the maintainer flips a switch — e.g., `release/*` short-lived branches with a fixture-smoke workflow whose job header carries `if: false` plus a missing `ANTHROPIC_API_KEY` secret. The infrastructure is committed for completeness and discoverability but consumers see a single-channel experience. Documents the future shape without absorbing the cost (paid CI runs, multi-channel maintenance).

### Application-level channels distinct from distribution channels

Some plugins ship a `channels.sh` library inside `hooks/lib/` for the plugin's own feature routing (which rules apply to which projects), independent of marketplace channel distribution. Worth distinguishing — the term "channel" overloads at the plugin and marketplace layers.

### Cross-host secondary channel via `npx skills`

Plugin doubles as a universal skill installable via `npx skills add <owner>/<repo>@<skill-name>` (skills.sh) in addition to the Claude Code marketplace. Two distribution channels for the same artifact, each with its own consumer base. Forces the SKILL.md description to work simultaneously for Claude Code and other agent hosts. Appropriate when the skill is intentionally multi-host and the maintainer accepts the cross-host description-tuning constraint.

## Branching and tag placement

Where release tags sit in git history, whether release branches buffer between development and release, and the discipline around tag form.

### Tag-on-main, single branch

All version tags sit on `main`'s linear history; no `release/*` branches. Feature branches (`feat/*`, `fix/*`, `chore/*`) merge to `main` via PR; a tag is cut from `main`; release automation (if any) fires on tag push. Appropriate for small-team or single-maintainer repos where the simplicity of one branch outweighs the safety of release branches; the cost is no isolated lane to backport fixes against a previously-shipped version. Implies `main` ≈ release; HEAD consumers see the latest version immediately on every release commit.

### Tag-on-main with merge-base ancestry gate

Tag on main, but the release workflow's first step asserts `git merge-base --is-ancestor HEAD origin/main` — failing the publish if the tagged commit is not actually on main. Cheap structural guard against tagging a feature branch by mistake. Pairs naturally with `fetch-depth: 0` in the CI checkout step.

### Tag-on-main with stale side branch

The dominant pattern is tag-on-main, but a side branch (`vX.Y/<topic>`) exists alongside `main` without serving as a long-lived release channel — it looks like an in-flight feature branch that was pushed and not deleted. Appropriate to flag as messiness rather than a deliberate channel pattern: users on `main` get the alpha; the side branch isn't a stable fallback.

### Short-lived `release/*` branches as workflow gate

PR-shaped release-prep branches (`release/v1.x.y`) exist solely to run an expensive workflow that's disabled on main (e.g., fixture-smoke against the live Claude CLI). The branch is merged back and tagged on main. Not a long-lived channel branch. Appropriate when one specific workflow is too expensive or too flaky to run on every main commit.

### Release-codename branches without tag ownership

Long-lived branches named after release codenames (`release/v4.3.0-arcana`) exist but tags land on `main`, not on these branches. The branches snapshot release-prep state and may be behind main by the time the tag is cut. Differs from the typical `release/*` pattern that owns tags. Branches function as historical/preparation markers rather than as authoritative release pointers.

### Mixed annotated and lightweight tags

Some tags are annotated (carry tagger info, message), others are lightweight (direct commit refs). Surfaces in GitHub API responses with different object types. Inconsistency suggests releases were cut by different mechanisms over time — `git tag -a` for some, web-UI lightweight for others. Appropriate as long as consumers don't filter on tag type.

### Plugin-name-prefixed tag format

In multi-plugin repos, tags use `{plugin-name}--v{version}` to disambiguate per-plugin lifecycles. Single-plugin repos use plain `vX.Y.Z`. Constrains the parent repo's tag namespace.

### No tags at all

Repo has zero tags. "Release" means whatever `main` currently holds. No history of release points; rolling back to a prior version requires checking out a specific commit. Often paired with no CI and no validation — a low-ceremony, low-investment plugin. Compounds the channel-from-HEAD problem: there is no way to recover any prior release state.

## Plugin-component registration

How `plugin.json` declares (or omits) the plugin's components — skills, commands, agents, hooks, MCP servers, output styles.

### Default convention discovery

`plugin.json` carries identity fields only (`name`, `version`, `description`, `author`, `repository`, `license`, `keywords`, optionally `userConfig`). Components are resolved by Claude Code from conventional directory names (`hooks/hooks.json`, `skills/<name>/SKILL.md`, `agents/`, `commands/`, root `.mcp.json`, `output-styles/`). Lowest-overhead path; aligns with the official plugin reference; communicates "follow conventions" to readers and keeps the manifest stable across component additions. Inline component definitions in `plugin.json` (e.g., `skills: [{name, description, ...}]`) were valid in older Claude Code schemas but break newer versions — projects that started with inline definitions had to migrate to default discovery (CHANGELOG explicitly: "skills/agents in plugin.json used inline objects incompatible with Claude Code v2.1.92 schema; removed inline; auto-discovery now"). Constrains naming and placement to whatever the harness expects but eliminates a class of "registered but missing" drift.

### Explicit per-component path arrays

Every component declared by path: `"skills": ["./skills/audio-hooks/"]` or `["./skills/"]`, `"agents": ["./agents/foo.md", ...]`, `"hooks": "./.claude-plugin/hooks.json"`, `"mcpServers": ["./.mcp.json"]`. Used when components live outside convention paths (e.g., `.claude-plugin/hooks.json` for hooks, sibling `.mcp.json` for MCP) or when the author wants the manifest itself to enumerate the surface. The trailing-slash directory glob form recurses to find every `<name>/SKILL.md`. The explicit list creates ambiguity about whether it is authoritative or additive — orphan files in `commands/` may or may not be exposed depending on host behavior. More verbose than auto-discovery but makes the component inventory readable from the manifest alone; cost is the orphan-detection burden during refactors.

### Mixed (paths + auto-discovery)

Some components declared by path, others left to convention. E.g., skills listed by path but agents discovered from `agents/` directory; or `hooks: "./hooks.json"` external file plus `lspServers: { … }` inline plus skills via convention. Often arises when the plugin gradually adopted explicit declarations only for components that didn't fit conventions, or when the author wants large/frequently-edited config in dedicated files while inlining short structural blocks. Constrains readers to look in multiple places to enumerate what the plugin registers.

### Inline `mcpServers` definition

`plugin.json` carries an `mcpServers` object directly: `{ "<server>": { "command": "npx", "args": [...] } }` or similar. No separate `.mcp.json`. Claude Code launches the server with the inline command. Constrains MCP server config to flow through the plugin manifest; a sibling `.mcp.json` is unused. Appropriate when the plugin owns the MCP-server lifecycle and wants no second-source-of-truth for the launch command. Mixed style — inline keeps the MCP server bundled with the manifest (single source for plugin metadata + MCP wiring) but loses the composability `.mcp.json` offers.

### Slash-command surface via skill frontmatter

Slash commands are exposed through `skills/<name>/SKILL.md` files with frontmatter `name: <plugin>:<verb>`, while `commands/` holds only diagnostic stubs (`doctor.md`, `hello.md`). The skill-namespacing prefix in frontmatter is doing the work a `commands/` directory usually would. A reader expecting "commands go in `commands/`" misses most of the surface. Appropriate when the project uses skills as the primary user-facing verb but pays a discoverability cost.

### Out-of-band hook registration

Hooks live in the repo as scripts (`hooks/*.sh`) but `plugin.json` has no `hooks` field. Registration happens via a side script (`scripts/sync-to-active.sh`) that patches the user's `~/.claude/settings.json`, or via a skill (`/adopt`) that writes a project `.claude/settings.json` from a template. The plugin's hook layer is not part of `/plugin install`'s reach. Constrains the user to a manual post-install step to get full hook coverage; the README has to document the gap. Appropriate when hooks are intended for opt-in adoption rather than passive activation, but needs a drift-guard since the hook inventory and the registration list can disagree.

### Non-standard component directories

In addition to standard `commands/`, `skills/`, `agents/`, `hooks/`, the plugin includes directories that don't correspond to any documented component type — e.g., `teams/` (orchestration definitions), `setup/templates/` (config scaffolding), `output-styles/<name>.md` (response-formatting markdown, terse vs reviewer modes). Some are consumed only by the plugin's own commands; others may be experimental forward-looking surfaces. No structural validation — users learn the convention from the plugin's own code.

### Component types absent across the corpus

Several component types declared by Claude Code's plugin schema rarely or never appear in observed samples: `monitors.json` is largely absent (notifications flow through hooks); `.lsp.json` appears occasionally inline; output-styles appears rarely. Their absence across the bin is itself a signal — the observed plugins solve their problems through hooks and skills instead.

## Skill authoring conventions

Frontmatter fields and tool-permission syntax used inside `SKILL.md` files.

### Standard frontmatter

`name`, `description`, `argument-hint`, `allowed-tools`, `license`, plus `metadata.{author, version, category, tags}`. Per-skill versioning (where present) means SKILL.md frontmatter is yet another version-sync site. The description field has a hard 1024-char limit (300-500-char target) and is read by many agent hosts simultaneously when the skill is multi-host.

### Multi-host description tuning

`SKILL.md` description is authored to match trigger verbs/nouns users actually say, with a hard 1024-char limit and a 300-500-char target. Explicitly written to work simultaneously for Claude Code, Cursor, GitHub Copilot, Windsurf, Gemini CLI, Codex, Goose, Amp, Roo Code, OpenCode, OpenClaw — each with its own project-scope and user-scope skills directory conventions. Description-writing rules codified in `CLAUDE.md` ("don't bake in anti-patterns against failure modes of one session — read by many agents in many contexts"). Pattern requires the maintainer to keep the description host-neutral.

### `disable-model-invocation: true` for high-blast-radius skills

A frontmatter flag that prevents auto-routing — the skill won't be auto-invoked via fuzzy embedding match. Users must call by name; routers must explicitly delegate. Applied to `/deploy`, `/migrate`, `/migrate-prod`, `/autopilot` and similar destructive operations. Constrains how the host model surfaces the skill in completion-style invocation. Appropriate for destructive operations where false-positive auto-routing has real cost.

### `context: fork` invocation hint

A frontmatter field on a router-style skill (`/autopilot`) suggesting subagent-like forked-context invocation. Documentation status unclear — possibly an undocumented Claude Code feature or a methodology-specific extension. Constrains the skill to a mode where it spins up a fresh agent context rather than continuing in the caller's.

### Mixed `allowed-tools` syntax

Same frontmatter line carrying plain tool names (`Read Write Edit`) and permission-rule syntax (`Bash(git:*)`, `Bash(pytest:*)`). The two forms coexist within one declaration. Constrains the parser; an author has to know which form Claude Code accepts in which slot. Appropriate when the skill needs both broad tool access and narrow command-pattern carve-outs.

## Agent authoring conventions

Frontmatter fields and tool-syntax used in `agents/*.md` to declare model, tools, and capabilities.

### Minimal frontmatter (name, description, model)

Only `name`, `description`, and `model` declared. `model: inherit` is common — defers to whatever model the parent session uses. No `tools`, no scope or behavior fields. `color` (e.g. `violet`, `green`) may appear as a UI cue. Native-language descriptions (Chinese in observed cases) flow through `description` directly without an i18n layer, so the template picker shows the source language to all users. Appropriate for thin agents that exist only to be entered into a routing decision; all behavior comes from skills they invoke.

### Plain tool-name list

`tools:` field as a YAML list or comma-separated list of bare tool names (`Read, Write, Glob, Grep, Edit, Bash, Agent`). No permission-rule syntax (`Bash(uv run *)` etc.) — Bash scoping, when needed, is enforced elsewhere (PreToolUse hook). Minimal capability declaration that lets the agent invoke the named tools. Field-name regressions are common (CHANGELOG: `tools:` → `allowedTools:` correction across multiple agent files in a single patch). Appropriate when the agent has a clearly-scoped role and the tool list serves as documentation as much as enforcement.

### `model` + `effort` + `maxTurns` for cost control

Frontmatter declares `model` (e.g. `claude-sonnet-4-6`, `haiku`, `opus`, `sonnet`), `effort` (`high`, `medium`, `low`), and `maxTurns` (integer cap on agent turns) for explicit cost-and-budget control per agent. Cheaper-model selection (`haiku` for exploration agents) is an explicit token-cost optimization — offload iterative searches to a cheaper model so the caller's expensive-model conversation stays short. Pattern surfaces in pipeline-style plugins where different waves of agents have different cost profiles.

### Rich behavior fields (background, isolation, memory)

In addition to documented fields, agents declare `background: true` (run in background), `isolation: worktree` (per-role git-worktree isolation), `memory: project|user`, and `effort` as a host-specific scheduling hint. These fields are not in the public Claude Code plugin reference; whether the harness honors them or silently drops them is unverified. Appropriate as a forward-looking declaration where the author treats unknown-but-tolerated frontmatter as a future-proofing surface.

### `skills:` array delegating to skill packages

Agent frontmatter lists `skills: [<plugin>:<skill-name>, ...]` to grant the subagent access to specific skills the parent has loaded. Composes subagent + skill into a token-cost-aware unit (cheap-model agent invokes the skill's full context). Pattern requires the named skill to exist in the agent's discovery scope.

### Experimental orchestration tool names

Agent `allowedTools` arrays include tool names not documented in the plugin reference (e.g., `TeamCreate`, `TaskCreate`, `TaskList`, `TaskUpdate`, `SendMessage`) for agents that orchestrate sub-agents or manage shared state. Implies bespoke runtime support inside the plugin rather than the standard tool set. No validator checks tool-name validity — typos or reference-mismatches surface only at runtime.

### Read-only agents

All agents in the population declare only read tools (`Read Grep Glob`) — no `Write`/`Edit`. Agents return structured markdown that the caller skill writes. Constrains the caller-callee contract: agents are advisors, the calling skill is the only writer. Appropriate when the author wants a clean read/write split between layers.

### Native-language-first templates

All agent templates written in the project's primary spoken language (Chinese observed); descriptions and full template body are not translated from English. English-only Claude Code users see the agent `description` in the source language in the template picker. Genuinely native-first design rather than translated; no i18n layer.

## Bin entry mechanism

Whether the plugin ships executable wrappers under `bin/`, what those wrappers do, and how they relate to the binaries that actually run.

### No bin entry

The plugin's executable surface is hook scripts under `scripts/` invoked by hook events, plus markdown command files. Nothing is surfaced as a user-PATH binary. All invocation flows through skills, hooks, or MCP. The MCP server, when present, is registered through `.mcp.json` rather than as a bin entry. Suits plugins where everything goes through Claude Code's hook/command dispatch, or where the plugin's value is methodology / contextual injection rather than user-facing tools. Reduces the discoverability surface compared to bin-wrapped CLIs but eliminates the version-of-record question for a wrapper script.

### Bash thin exec-delegate wrapper

`bin/<plugin>-<verb>` shell scripts that `exec bash "$(cd "$(dirname "$0")/.." && pwd)/<internal>.sh" "$@"` — resolving the plugin root via `$(dirname "$0")` rather than `${CLAUDE_PLUGIN_ROOT}`, so the script works whether invoked directly from a terminal or from a Claude Code Bash-tool context where `CLAUDE_PLUGIN_ROOT` may be absent. Lets one implementation serve both the hook-event invocation and a CLI invocation. CI may not enforce executability on `bin/*` (the validator's allowlist commonly covers `hooks/*.sh` but not `bin/*`), so the +x bit must be set deliberately.

### Bash wrapper that synthesizes a hook input envelope

`bin/<plugin>-validate` reconstructs the PostToolUse JSON input envelope (`{tool_input: {file_path: $fp}}`) via `jq -n` and pipes it into the hook script — letting a user run the same hook validator from a terminal as Claude Code runs at PostToolUse. "One implementation, two surfaces." The reconstructed envelope is brittle against hook-input schema changes; if Claude Code adds required fields, the CLI surface silently breaks while the hook-event surface still works.

### Bash wrapper with cross-platform interpreter probing

`bin/<name>` bash script probes `python3 → python → py`, runs a smoke `python -c "import sys"` to defeat the Microsoft Store `python3.exe` stub on Windows, then `exec`s the sibling `<name>.py`. Sibling `<name>.cmd` provides a Windows batch entry. More defensive than relying on the Python shebang alone; addresses Git Bash on Windows specifically. Files often have non-exec permission (100644) on the assumption Claude Code's plugin cache adds `bin/` to `PATH` and shell resolution honors the shebang via `bash <path>`.

### Cross-platform shim dispatching to pre-built binaries

`bin/<name>` POSIX shell wrapper resolves `uname -s`/`uname -m` and `exec`s the matching pre-built binary (`bin/<name>-darwin-arm64`, `bin/<name>-linux-amd64`). Platforms not built receive silent no-op (exit 0, stderr diagnostic). Zero-install at runtime; constrained by which architectures the author cross-compiles. Linux ARM64 and Windows often gaps; graceful degradation means users get no error, just no functionality.

### Python `bin/` script with uv injection

`bin/<name>.py` with `#!/usr/bin/env python3` shebang; the script body does `uv run --with <pkg>` internally to inject deps. Plugin-root resolution via `${CLAUDE_PLUGIN_ROOT}` env var with `Path(__file__).resolve().parent.parent` fallback. Cross-platform via `subprocess.run` (chosen over `os.execvp` because the latter raises on Windows). Constrains the bin to use `.py` extension (extensionless or `.sh` flagged by validators as platform-specific); on Windows, `.py` association must be set for PATH invocation. Permissions are 100755. Appropriate when the plugin wants both hook-fire and on-demand-CLI access modes against the same script body.

### Node CLI launcher with `env node` shebang

`bin/<verb>.js` opens with `#!/usr/bin/env node`, resolves a wrapper path script-relative (`path.resolve(__dirname, '..', 'scripts', '<wrapper>.mjs')`), and `spawn`s `process.execPath` with the wrapper as argv. Inherits stdio, propagates child exit code/signal. Declared as the `bin` entry in root `package.json`. Cross-platform via shebang on POSIX; on Windows requires either `node bin/<verb>.js` or a sibling `.cmd` launcher. Secondary env-var overrides (e.g. `<PLUGIN>_CLAUDE_CMD`, `<PLUGIN>_WRAP_SPAWN`) provide runtime escape hatches.

### Auto-generated Windows `.cmd` launchers with absolute paths

A SessionStart hook discovers `process.execPath` and the `claude` binary location, then writes `bin/*.cmd` Windows launchers with those absolute paths embedded, plus optional `set <ENV>=<path>` lines. Solves "node not on PATH" on Windows without requiring user editing. Files are committed with the author's machine's paths frozen — a reader inspecting the committed file sees one specific machine's layout. Header banners declare "auto-generated ... edits will be overwritten next session" so user customization is impossible. POSIX users rely on the `bin` field in `package.json` instead.

### Skill-invoked update poller

A single `bin/<plugin>-update-check` shell script, not registered in `plugin.json`'s component fields, invoked from a `## Preamble (run first)` block embedded in a SKILL.md. The agent reads the skill body, shells out per the prose instructions, parses output (`UPGRADE_AVAILABLE <old> <new>` / `JUST_UPGRADED <old> <new>` / nothing), and conditionally surfaces a notification. Polling cadence is gated by a cache file with a TTL. Novel because it embeds polling logic in documentation text the model must parse and act on, rather than in a structured hook contract. State coordination (read by skill, written by install hook) sits in shared sentinel files (`.version`, `just-upgraded-from`).

### Orphaned wrapper alongside downloaded binary

`bin/<plugin>-wrapper.sh` is committed and `chmod +x`ed but `plugin.json`'s `lspServers.command` (or equivalent) points directly at the downloaded native binary, not the wrapper. The wrapper sources a `~/.config/<plugin>/config` file before `exec`ing the binary; the binary itself reads the same config natively, making the wrapper redundant. Classic half-refactored state — wrapper was written first, then superseded by in-binary config loading, then left in place.

### Pre-built binary download (lazy, per-hook)

Runtime is a Go (or similar compiled-language) binary downloaded from GitHub Releases on demand. Build-time deps live in `go.mod`; users never compile. The binary is materialized into `${CLAUDE_PLUGIN_ROOT}/bin/` (inside the plugin cache, not `${CLAUDE_PLUGIN_DATA}`) by an `install.sh` script invoked by a wrapper script on every hook fire — not gated behind SessionStart, so the first hook of a session effectively becomes the bootstrap moment. A version-cache file at `${XDG_CACHE_HOME}/<plugin>/verified-version` short-circuits the binary-launch cost on the happy path; cache miss falls back to executing `<binary> version` and comparing to `plugin.json.version`. Appropriate when the runtime is a compiled language whose CGO/static-link story sidesteps interpreter version drift; the cost is platform-asset matrix complexity (per-OS, per-arch artifacts plus signed/notarized macOS app bundle) and a wrapper that must self-heal across cross-platform git quirks.

### Committed binaries in tree

Pre-built platform-specific binaries are committed to the repo (`bin/harness-darwin-arm64`, `bin/harness-linux-amd64`, etc.) and dispatched at runtime by a shim that detects `uname`. Users get binaries by cloning. Trades repo size (~33MB of binaries per clone) for zero runtime install latency and zero dependency on GitHub Release artifacts being present. Single-architecture gaps are handled by graceful no-op.

### npm bin (separate distribution lane)

`package.json.bin.<name> = "./cli/bin/<name>.js"` exposes a Node CLI separate from any plugin-side `bin/`. npm symlinks the binary into the user's `node_modules/.bin/`; on a global install it's on PATH. The plugin manifest is a thin alias and the bin reaches the user via the npm package, not through `/plugin install`'s payload. Used when the same project ships as both a Claude plugin and an npm package — the npm form distributes the CLI for one-shot init/update; the plugin form is enabled inside Claude Code. Constrains discovery — a user who installed only via the Claude marketplace might not have the bin unless the plugin is also globally `npm install`ed. The two distribution surfaces share content via copying or symlinks.

### Version-floor declared only in prose

The minimum Claude Code version supporting a feature (`v2.1.91+` for `bin/`) is declared in a script docstring, a README section header, and README prerequisites — three documentation layers, zero machine-readable fields. `plugin.json` has no `requires.claude-code` / `engines` field. Constrains version-floor enforcement to graceful-degradation discipline (Claude Code silently ignores unknown hook events / fields, so older hosts get partial functionality). Appropriate when no machine-readable mechanism exists upstream and the plugin author prefers prose-documented degradation over a hard precondition check.

## Dependency installation

Whether and how the plugin installs runtime dependencies on first use, and where they land.

### No runtime dependencies (stdlib + system probes only)

The plugin declares zero runtime deps as policy — `pyproject.toml` may exist for PyPI metadata but lists no `[project.dependencies]`; all hook scripts and tooling rely on language stdlib only. Probes for system tools (audio players, `gh`, `jq`, PHPStan, ESLint, deptrac, dependency-cruiser, shellcheck, `python3`, `bash 3.2+`) at runtime; features light up when their required tool is present, absent tools mean degraded but still-functional behavior. Documented as a degradation ladder rather than a caveat (e.g., `docs/CI.md` documents "intentionally zero-dependency"). Tests are stdlib-only too (`unittest`, no pytest). Appropriate when the plugin's value proposition includes "zero setup" — sidesteps `uv`/`pip` questions, venv placement, and Python ABI tracking entirely; removes supply-chain risk and the SessionStart-install lifecycle entirely. The cost is hand-written replacements for what libraries would provide (custom JSON-schema validation, mini YAML parsers, bespoke circuit breakers), often amounting to substantial test-code volume; and constrains the plugin to whatever bash + stdlib Python can do.

### Pip + stdlib venv (no `uv`)

Python deps are installed into `${CLAUDE_PLUGIN_DATA}/venv` via stdlib `venv` + pip during a SessionStart hook. The install script reads `pyproject.toml` for the dep list and pip-installs the plugin root itself as an editable-style package so its own `lib/` becomes importable from skill scripts. A version stamp file at `${CLAUDE_PLUGIN_DATA}/installed-version` short-circuits the install on subsequent sessions when its content matches `plugin.json.version`. Appropriate for plugins that need third-party Python packages but don't want to require `uv` on the user's system; the cost is slower first-install (~tens of seconds, sometimes synchronously blocking the SessionStart) and reliance on the host having a usable system `python3`.

### Plugin-data venv with `diff -q` change detection

Bootstrap script (`bootstrap.py` or `install-deps.sh`) creates `${CLAUDE_PLUGIN_DATA}/venv`, pip-installs requirements plus the plugin package, then injects `site-packages` onto `sys.path` and rewrites `sys.executable`. Change detection via byte-comparison (`diff -q`) against a copy of `requirements.txt` saved into `${CLAUDE_PLUGIN_DATA}` as a marker. Strong invariant when paired with `set -e`; weaker when subprocess return codes aren't checked before stamping the marker. Isolates plugin deps from the user's Python environment at the cost of needing the venv to survive Python upgrades.

### `pip install` against `sys.executable` (no venv isolation)

SessionStart Python hook (`auto_install.py`) tries `import <package>`; on `ImportError`, runs `pip install git+https://<repo>.git` against whatever `sys.executable` resolves to (typically user-global or active interpreter). No venv isolation — mutates user's Python environment silently. Restart of Claude Code is required after first install for the MCP server to pick up the new `sys.path`; this is signaled back to the user via `hookSpecificOutput.additionalContext` declaring "Please restart Claude Code to activate MCP tools." Appropriate as a low-ceremony bootstrap; risky on system-Python with restricted site-packages.

### Ad-hoc per-invocation fetch via `uv run --with`

Python plugins use `uv run --with <pkg> python3 ...` as the hook command. uv's global cache satisfies subsequent invocations (~3s first run, ~3ms cache hit per author measurement). No `SessionStart` hook, no `${CLAUDE_PLUGIN_DATA}` venv. Constrains the plugin to one-shot Python invocations (no long-running state across hook fires); requires `uv` on PATH; the plugin does not own a venv. Appropriate for thin plugins where dep set is small and per-invocation latency is acceptable.

### Ad-hoc per-invocation fetch via `npx --yes --package`

Node plugins use `npx --yes --package <name> <bin> serve` as the MCP-server command. Resolves through the user's npm cache; first launch fetches from the registry. The unpinned form silently rolls forward with whatever `latest` resolves to. A pinned variant (`<name>@<version>`) is available but not surfaced as the default. Constrains the runtime to npm-cache state; auto-upgrade is the default behavior unless the user explicitly pins. Appropriate when the plugin is itself an npm package and wants to share its CLI surface across multiple host integrations.

### Node `npm install --prefix ${CLAUDE_PLUGIN_ROOT}` from SessionStart

SessionStart hook runs `npm install --prefix "${CLAUDE_PLUGIN_ROOT}"` reading `${CLAUDE_PLUGIN_ROOT}/package.json`. Installs land in `${CLAUDE_PLUGIN_ROOT}/node_modules`. Choice of ROOT over DATA is rooted in ESM module resolution: ESM walks up from the importing file looking for `node_modules/`; installing into `CLAUDE_PLUGIN_DATA` would place node_modules outside that walk path, and ESM deliberately ignores `NODE_PATH`, so the CJS env-var workaround cannot bridge the gap. Pure-ESM workers (`"type": "module"` + top-level `import`) require the install path to be adjacent to the import sites.

### SessionStart Node hook with mtime-driven `npm install`

Hook (`hooks/mcp-deps-install.js` or similar) registered on SessionStart iterates install targets (`mcp/`, `packages/<lib>/`) and reinstalls when `node_modules/` is absent, `package-lock.json` is absent, or `package.json` is newer than `node_modules/.package-lock.json`. Calls `execFileSync(process.execPath, [npmCli, ...args])` resolving `npmCli` from Node's bundled npm rather than bare `npm` on PATH. Prefers `npm ci` when a lockfile exists, falls back to `npm install`. On failure, removes `node_modules` so next session retries. Diff-based change detection means repeated runs converge without redoing work.

### Diff-based change detection with separate sentinel and manifest

Two manifests coexist with different roles: `package.json` is what npm actually reads (`npm install --prefix` reads the prefix dir's `package.json`), while a sibling `runtime-deps.json` (or similar) is the sentinel-diff source for idempotency. SessionStart runs `diff -q $MANIFEST $SENTINEL` against `${CLAUDE_PLUGIN_DATA}/.<plugin>-deps-installed.json`; on mismatch, reinstall + update sentinel. Double-checked with `[ -d "${ROOT}/node_modules/<probe-pkg>" ]` so an external `node_modules` wipe forces reinstall even with intact sentinel. The two manifests can drift — undocumented constraint that the sentinel must mirror the npm-read manifest, or the diff lies. Failure path: `rm -rf node_modules` + `rm -f $SENTINEL` so next session retries clean.

### Self-healing inline install at MCP launch

`scripts/mcp-wrapper.sh` independently runs `npm install` if a probe directory under `node_modules/` is missing when the MCP server launches. A second install path — not a fallback delegate, a full duplicate — covering the race where Claude Code spawns the MCP server before the SessionStart hook completes. Suits plugins where the MCP server may launch parallel to or before SessionStart. Makes the install idempotent across two entry surfaces.

### Manual `npm install` post-install

No `SessionStart` hook for install. README instructs users to `cd` into the plugin cache directory and run `npm install` once. `node_modules/` materializes inside the plugin root. Change detection is the user reading `ls node_modules/zx`. Failure mode is silent: if `npm install` was never run, hook handlers fail at `import` time before any top-level `try/catch` can engage. Deviates from the docs-prescribed `diff -q`/retry-next-session pattern; the author has accepted this friction in exchange for not maintaining an install hook. Required when hooks need an npm runtime dep (e.g., `zx`) that the plugin cannot ship pre-resolved.

### Hook-driven prebuilt native binary

`SessionStart` hook downloads a prebuilt platform-specific binary (Rust release artifact) into `${CLAUDE_PLUGIN_ROOT}/bin/`, picking the right asset by detecting OS and architecture (`macos-arm64`, `linux-x86_64`, `linux-arm64`). Existence-only change detection: the script no-ops if the binary exists, so `/plugin update` does not re-download — users must manually wipe the cache to pick up a new binary. Calls the unauthenticated GitHub Releases API at install time, coupling first-run success to GitHub rate limits. No sha verification; trust is implicit in HTTPS plus GitHub Releases.

### Hook-driven WASM payload

`SessionStart` hook downloads a raw WebAssembly binary plus its JS wrapper from GitHub Releases on a separate repo, installing into `${CLAUDE_PLUGIN_DATA}` with a hardcoded `$HOME/.config/<plugin>` fallback. No package manager — release artifacts substitute for npm/PyPI. The MCP server consumes the WASM via `WebAssembly.Module` + `initSync({ module })` at startup. Pattern: release-as-CDN, where GitHub Releases acts as a binary distribution channel without a package manager mediating. Constrains the plugin's release cadence to the engine repo's release cadence — engine release must precede plugin install success, and version pinning is exact-match (any inequality re-downloads all files).

### Manual install script (no host-driven install)

A standalone `install.py` (or equivalent) at repo root, invoked manually by the user with verbs (`--platform`, `--uninstall`, `--verify`, `--add-to-path`). Not tied to any hook lifecycle. Idempotent through full-wipe + re-create rather than diff. Appropriate when the plugin must wire itself up to multiple host CLIs (Claude Code, Copilot CLI, Codex CLI) where each has its own install convention — the manual script can detect host presence and stage files into the right places.

### One-time interactive setup with OS credential store

User runs `python setup.py` once; the script stores secrets (API keys) in macOS Keychain / Linux Secret Service / Windows Credential Manager. No package install — runtime scripts use stdlib only. Distinct posture: "no deps to install" is the alternative. Cross-agent credential sharing is the explicit motivation — the credential lives in OS-wide storage, not per-plugin or per-session. Pairs with a SessionStart hook that probes for credential presence and nudges the user to run setup if absent.

### Ownership-based install location split

Third-party MCPs install to a shared user-home directory (`${HOME}/.<framework>/mcp/`) — amortizes download across plugin versions, decouples lifecycle from plugin updates. First-party bundled MCPs ship inside `${CLAUDE_PLUGIN_ROOT}/mcp/<name>/dist/` with their dependencies installed to `${CLAUDE_PLUGIN_DATA}/<name>/node_modules/` at first session start, wired together via `NODE_PATH` in `.mcp.json`. The axis is "we own the code" vs. "someone else does"; the install-location mechanic follows ownership rather than runtime.

### npm CLI as the sole install surface

The plugin form has no installer; the project's npm package (`package.json.bin.<name>`) carries an `install.sh` that wraps `npx -y <package> init` to copy hooks/skills into the user's `.claude/`. The plugin form is then self-sufficient because everything is markdown + bash with no runtime deps. Used when the same project ships as both a plugin and an npm CLI, with the CLI doing one-time install work the plugin form doesn't need.

### Pre-built npm package as runtime

The plugin is itself an npm package; users install it through npm (transitively via the marketplace's `source: npm` binding), and the plugin manifest's commands invoke `npx <name>` against the installed package. No SessionStart install hook is needed because npm did the work. Constrains the entire plugin to npm's distribution model. Appropriate when the codebase is large (40+ runtime deps including native modules like `better-sqlite3`) and the plugin is one of many consumer surfaces over the same package.

### Coexisting redundant install paths

Multiple install scripts in tree (SessionStart hook + bootstrap.py + install-deps.sh) where only one is wired to lifecycle events; the rest are dormant rejected-state alternatives kept for reference. A reader has to trace `hooks.json` and `.mcp.json` to know which is live. Drift-prone — the dormant scripts can fall behind the live one without anyone noticing.

## Install change detection

How the install path decides "is the cached state up to date?" — what the gate compares against and what triggers re-install.

### Plugin-version stamp file

A single text file (e.g. `${CLAUDE_PLUGIN_DATA}/installed-version`, `${INSTALL_DIR}/.version`, or `${XDG_CACHE_HOME}/<plugin>/verified-version`) carries the last-installed `plugin.json.version` string. On each lifecycle hit, the script reads `plugin.json.version`, compares to the stamp, and skips on match. Idempotent — every `SessionStart` re-runs the script but does no work in the steady state. The committed-version file is written only on full success, so a partial failure leaves the stamp absent and the next session retries; cleanup of partial tmp files on failure preserves the retry invariant. Makes `plugin.json.version` double-duty: user-facing semver AND install-staleness signal. The trade-off is that a no-op version bump (e.g. README-only) triggers a full reinstall, which most authors accept as cheap insurance.

### Two-tier version cache (file + binary self-report)

Fast path: a cache file holds the last verified version; if the file exists and matches `plugin.json.version`, skip. Cold path: cache miss invokes `<binary> version` (a process exec costing ~tens-of-ms) and compares to `plugin.json`; mismatch triggers `install.sh --force`. Appropriate when the binary is the source of truth for what's actually deployed and the file is just a launch-cost optimization; the structure makes sense when the binary itself is downloaded (not built) and the cache could be wiped without losing correctness.

### Diff-based byte comparison of manifest

`SessionStart` script byte-compares (`diff -q`) a committed `package.json`/`requirements.txt` against a cached copy in `${CLAUDE_PLUGIN_DATA}/...`, and runs `npm install` / `pip install` only when they differ. On install failure, removes the cached copy so the next session retries; never hard-fails the hook. Diff-based change detection means repeated runs converge without redoing work. May double-check with `[ -d "${ROOT}/node_modules/<probe-pkg>" ]` so an external `node_modules` wipe forces reinstall even with intact sentinel.

### Existence-only check

`if [ -f "${BINARY_PATH}" ]; then exit 0`. Once the artifact is present, the install hook never replaces it. Upgrades require manual cache wipe — the install path is not idempotent across version changes, only across no-change re-invocations. Pairs uneasily with `/plugin update`, which does not clear the binary, so users hit a documented troubleshooting path.

### Out-of-band user check

User runs `ls node_modules/<pkg>` to verify install. No automated detection at all. Failures surface as runtime import errors when hooks fire.

### Full-wipe (no detection)

The install script always deletes its target dir and rebuilds (`reset_directory()`). No staleness detection — every install is a fresh install. Appropriate for adapter-style plugins that wire into multiple host CLIs where each install is rare (manual user invocation) and partial state is more dangerous than redundant work.

## Install failure posture

What happens when install fails mid-way, and how that failure is signaled.

### `rm` stamp on failure (retry next session)

The install script wraps install + stamp-write in a single try/except; on any exception it deletes the stamp file and re-raises. Result: a half-installed venv is not remembered as "done"; next SessionStart sees the missing stamp and retries. Exception propagates to non-zero exit so the host surfaces failure. Appropriate when the host gracefully reports failure to the user and partial state is detectable from stamp absence.

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

### Postinstall failure suppression

`package.json` `postinstall` and `prepare` scripts wrap their commands with `|| true` (or `>/dev/null 2>&1 || true`). A crashed install-time banner or hooks-installer never fails `npm install`. Constrains user-visible install reliability; means install-time bugs are hidden until the runtime fires. Appropriate as a courtesy to users; trade-off accepted by author.

### Silent failure (no install hook at all)

Hook is absent or no-ops; the install never runs. Failure surfaces only when the missing dependency is needed at runtime (e.g., `Cannot use import statement outside a module` from a hook with no `node_modules`). Documented as a troubleshooting path the user must follow manually. Trades discoverability for zero install-machinery cost.

## Session context loading

How and when the plugin contributes to the model's context — at session boundaries (`SessionStart`), per-prompt (`UserPromptSubmit`), or via skill invocation.

### Dependency install only (no context emission)

SessionStart fires `ensure-deps.py` (or equivalent), which idempotently installs Python deps if the version stamp doesn't match. No matcher set, so it fires on all sub-events (`startup`, `resume`, `clear`, `compact`) — wasted work on no-op paths is accepted as cheap. `statusMessage: "<plugin>: Installing dependencies..."` is surfaced during exec; `{"systemMessage": "..."}` JSON on stdout reports completion to the host. No `additionalContext` emission. Appropriate when the plugin's only lifecycle need is dep readiness or when context is request-driven, not session-startup-driven.

### `additionalContext` payload at SessionStart

Hook reads project state (e.g. mission manifest from `<git-common-dir>/<plugin>/`) and emits `hookSpecificOutput.additionalContext` JSON object containing project-detection results, available command list, worker/system status, or a slim summary plus an age warning if stale. Built with `jq -Rs .` for safe escaping. Wired to both SessionStart and UserPromptSubmit (the latter as fallback for upstream issues), with a `/tmp/<plugin>_session_${SESSION_ID}.initialized` flag file for once-per-session deduplication. Matcher `"startup|resume|clear|compact"` is the broad form — fires on all sub-events. Appropriate when the plugin maintains durable state outside the model's context that must be re-introduced at session boundaries; the cost is the host re-injects context every resume.

### `systemMessage` payload (broader rendered form)

SessionStart emits `{systemMessage: "..."}` JSON containing a multi-line profile summary (active stack, strictness, enabled rules, learning trends from prior sessions, healthcheck, command routing table). Less structured than `additionalContext` but renders verbatim in the session's system context. Used when the surface is many concise lines rather than a single rich payload. Constrains output volume to whatever Claude Code's hook-output cap allows (10,000 chars; overflow silently replaced with an opaque stub).

### Banner echo as context push

A literal `echo '🎯 Plugin v2.0.0 — …'` line in `SessionStart` pushes a banner via stdout rather than via `hookSpecificOutput.additionalContext` JSON. Functions as session-start context for the user but not as structured context for the agent. Drift hazard: the banner text typically hardcodes a version that diverges from `plugin.json` over time.

### Banner-plus-additionalContext (dual surface)

Hook prints a banner to stderr (visual cue for the operator) and emits the same content via `hookSpecificOutput.additionalContext` (model-visible context injection). Documented evolution path through three generations of output mechanism ending at "stderr direct print + additionalContext for model awareness." Both surfaces because each serves a distinct audience.

### Conditional `additionalContext` for setup nudge

SessionStart hook (`check_auth.sh`) emits `additionalContext` only when a precondition fails (e.g., API key missing); when present, no context is injected. Matcher restricted to `startup` (not `startup|clear|compact`) so the nudge is one-shot per fresh session. Appropriate as a guidance injection, not a status line. The `startup`-only matcher means user adding a credential mid-session won't see updated state until next fresh session.

### Full-briefing context with API call

Hook (`session_bootstrap.py`) hits a local API server for team status and task data, then writes a multi-page briefing (behavior rules, available agent templates enumerated from `~/.claude/agents/*.md`, available skills) to stdout for context injection. Rich runtime-driven context — contrast with static banners. Pays a startup-time cost for the API call plus optional opportunistic git-fetch update check. SessionStart matcher absent so all sub-events trigger the full chain unconditionally.

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

### SessionStart purely for non-context side effects

SessionStart hook fires but emits no `additionalContext` / `systemMessage`; instead it performs side-effecting setup — writes bridge files (`~/.claude/<plugin>-session-state-path` containing the resolved `CLAUDE_PLUGIN_DATA` location), generates wrappers (per-session executable shell wrappers with the plugin's resolved lib path baked in at `~/.claude/<plugin>-<verb>.sh`), launches background services, plays distinct audio cues per matcher (`startup`/`resume`/`clear`/`compact`), or prints effort/model nudges to stderr. Skills running in Bash-tool context don't receive `CLAUDE_PLUGIN_ROOT` or `CLAUDE_PLUGIN_DATA` from the harness, so bridge files at stable absolute locations bridge the env-var gap. Side-effect-at-startup pattern; vulnerable to test pollution (test runs that exercise SessionStart can overwrite the real bridge file with temp paths) — tests need backup/restore guards.

### Lazy bootstrap on first hook (no SessionStart)

No SessionStart hook at all. Whatever bootstrap work is needed (binary download, cache priming) happens on the first non-SessionStart hook of the session. The author's stated rationale (in one sample) is that Claude Code plugins historically lacked post-install hooks, so lazy-on-every-hook is the most robust pattern; even after SessionStart became available, lazy-at-every-hook self-heals through mid-session plugin upgrades that SessionStart-only would miss. Appropriate when the bootstrap cost is small and the wrapper-per-hook overhead is acceptable.

### Install plus session telemetry

`SessionStart` runs two handlers in sequence: an install/banner echo, and a Node script that emits a structured session-started event to a metrics file (and optionally POSTs to a remote event bus when an env-var secret is set). Async, 5s timeout. Informational; never blocks. Adds an `on-session-start.mjs` companion to the install script. Constrains the plugin to ship telemetry plumbing alongside install plumbing.

### No session-context ambition

The plugin does not register `SessionStart` or `UserPromptSubmit` hooks; reports or other behaviors fire only on completion-class events (`Stop`, `TaskCompleted`, etc.). Constrains the plugin to post-fact observation. Appropriate when the plugin's job is summarization rather than guidance.

## Tool-use enforcement

Whether and how the plugin gates, modifies, or annotates tool calls before, during, or after execution — covering PreToolUse, PostToolUse, PermissionRequest, PermissionDenied, and event-completion gates.

### Hook-only enforcement (frontmatter is documentation)

Agent frontmatter lists tools but does not encode permission rules; actual enforcement happens in PreToolUse, which reads a role spec and computes allow/deny. Appropriate when the plugin needs richer rules than frontmatter expresses (per-path scopes, bash-policy categories, blind-from constraints) — the spec becomes the source of truth and frontmatter is a documentation surface.

### Frontmatter-only enforcement (no PreToolUse)

Agent frontmatter declares `tools: <list>` and Claude Code's built-in scoping handles enforcement; no PreToolUse hook augments it. Appropriate for simple agents whose tool needs are static and fully expressible in the documented frontmatter schema.

### Auto-allow plugin's own scripts

Single PreToolUse with matcher `"Bash"` (or compound), purpose: detect when a Bash command is invoking one of this plugin's own venv-Python scripts and emit an `allow` decision so the user is not prompted. Inline bash `case` fast-path string-matches the stdin JSON; only on match does the hook pipe into a Python validator. Validator uses `Path.resolve(strict=True)` for traversal-resistance and exits with no-output ("pessimistic no-opinion") on any uncertainty, deferring to the normal permission flow. Appropriate as a UX optimization for plugins whose skills always invoke the same Python scripts; the cost is hard-coding the plugin name into the bash matcher pattern, breaking on rename.

### Scope enforcement (block out-of-scope writes)

Matcher `"Write|Edit|MultiEdit|Bash"`, purpose: enforce per-role write-scope and bash-policy for multi-agent setups. Reads role declaration from a spec file, computes allow/deny against the active subagent's scope, emits `pretool_deny` payloads as JSON on stdout. Configurable failure mode (`fail_open` / `deny`) per mission. Appropriate when the plugin runs multi-agent flows where each agent must be sandboxed to a subset of the codebase; the cost is the gate is now the trust anchor and must be carefully tested.

### Block-list with hard deny + soft warn classes

`scripts/file-guard.sh` classifies the target path against two pattern groups: hard-block (`.env`, `*.pem`, `*.key`, `*credentials*`, `*secret*`, `*.lock`, `package-lock.json`, `*/node_modules/*`, `*/.venv/*`, `*/target/*`) emits `exit 2` + stderr human message + stdout `hookSpecificOutput.permissionDecision: "deny"`; soft-warn (`migrations/*.sql`, `*.pb.go`, `*_generated.*`, `CHANGELOG.md`) emits `exit 0` + `systemMessage` JSON. Dual-output contract — stderr for the terminal display + stdout JSON for the harness's permission-decision schema. User-extensible block list via `<PLUGIN>_EXTRA_BLOCKED` env var (colon-separated globs).

### Fail-closed scope and command guards (belt-and-suspenders)

Multiple `PreToolUse` hooks (`Edit|Write` for path-scope enforcement, `Bash` for destructive-command guards and per-wave allowlist enforcement). Every security-critical hook wraps its body in `main().catch((e) => emitDeny(...))` so any unhandled error denies the call rather than allowing it through. Output convention is centralized: `emitAllow`/`emitDeny`/`emitWarn`/`emitSystemMessage` helpers in a shared `io.mjs` library produce a uniform JSON wire format (`{"permissionDecision":"deny","reason":"..."}` plus exit 2 for deny; exit 0 silent for allow). Hook emits both the `hookSpecificOutput.permissionDecision: "deny"` JSON envelope on stdout AND a human message on stderr, then `process.exit(2)` — documented rationale: "exit 2 alone is silently discarded by the current runtime." `emitDeny` requires a non-empty reason (throws if missing) — silent-deny is structurally unrepresentable. Path normalization (Windows separator, realpath symlink resolution) plus an ENOENT ancestor-walk for not-yet-existing Write targets defends against symlink escape. Stdin reads guard against runaway input via 1 MB byte cap plus 5s `AbortController` timeout. Appropriate for security-sensitive matchers where deny must succeed; a consumer who picks just one form (stderr OR stdout) will have hooks that appear to work in tests but silently pass in production.

### PreToolUse advisory injection (no blocking)

A hook on `PreToolUse` matched against `Bash|Edit|Write|NotebookEdit` (or similar) writes `hookSpecificOutput.additionalContext` JSON on stdout to inject context before the tool call. No blocking by default; the agent reads the injected lessons and can choose to comply. Constrains the agent's information environment without restricting its action space. Appropriate when the goal is teaching or reminding rather than blocking.

### PreToolUse blocking gate (env-var opt-in)

The same advisory hook adds a `decision: "block"` output when an env var (e.g., `<PLUGIN>_HOOKS_ENFORCE=1`) is set and a risk threshold is crossed. Default-off, opt-in to enforcement. Constrains the user to an explicit env-var flip before any blocking behavior fires; protects against accidental deadlocks during plugin onboarding. Appropriate when the hook's invariants are real but the maintainer wants advisory mode as the safe default.

### Soft-then-escalating PreToolUse hook

A hook starts in advisory mode, counts ignored reminders, and escalates to blocking after N consecutive ignores (e.g., 3 in `check-tool-skill.sh`). Constrains the agent to a documented escalation curve. Appropriate when the discipline being enforced is genuinely best-effort but persistent ignoring is a defect.

### Hard-blocking PreToolUse on commit-shape invariants

Hooks matched against `Bash` parse the command and block `git commit` when staged content fails a structural check (e.g. SKILL.md edited without referenced `references/` files; >2 files touched without `/review`). Constrains commit shape; users who legitimately need to bypass create a documented escape-hatch file (e.g. `.methodology-self-extend-override`). Appropriate when commit shape is verifiable from staged state and the cost of false-positives is bearable given a documented bypass.

### Workflow-state gate (PreToolUse `Write|Edit`)

Hook matches `Write` and `Edit` and gates them against pipeline state — denies edits when the plugin's state machine is in a phase where edits aren't allowed (e.g., before a planning gate is approved). Same belt-and-suspenders output as Bash deny. Models workflow state via hooks rather than relying on skill prose to guide the agent; structural enforcement of pipeline transitions. Plugin can be structured as a state machine with explicit user-approval gates between agent waves (Gate #1 = plan approval, Gate #2 = implementation approval). Skills represent transitions between states (`/forge:plan`, `/forge:implement`, `/forge:review`); hooks ensure illegal transitions can't happen by tool-level enforcement.

### PreToolUse `Agent` routing/gate enforcement

Hook matches `Agent` (subagent dispatch) and constrains which subagents can run based on pending gates. Stops dispatch of agents that shouldn't run yet (e.g. implementer before plan is approved). Pipeline-state-as-policy pattern; hook-as-policy-engine.

### Layer-import / architecture rule validation

PreToolUse for `Write|Edit` runs an architecture-rule engine before the write commits — checks layer-import boundaries on PHP/TS/TSX (e.g., LAYER001-003, PHP001) and `exit 2` blocks the write. Same engine source as the PostToolUse rules — single rule engine across hook + CI lanes (see *Rule engine reuse*).

### `if:` permission-rule sub-matcher

PreToolUse entry registered with `matcher: "Bash"` and an additional `"if": "Bash(git push*)"` field that further narrows the hook to git-push-shaped commands only, using the same permission-rule glob syntax as `permissions.allow/deny`. Multiple alternatives across tools supported (`"if": "Write(src/**) Edit(src/**) MultiEdit(src/**)"` — the `if:` field carries space-separated tool/glob alternatives, narrowing the hook to writes under a specific path prefix). Far more precise than matching all Bash invocations and re-parsing inside the hook. The path pattern is hard-coded per-consumer (a comment instructs the user to "customize this pattern to match your source directory") — installation requires post-install customization. Brittle against future Claude Code changes to `if:` parsing — silent regression possible.

### `PermissionRequest` with `if:` allowlist

`PermissionRequest` hook on `matcher: "Bash"` uses an `if:` clause enumerating auto-allow patterns (`git status*`, `git diff*`, `npm test*`, `pytest*`, `go test*`). Fine-grained per-hook conditional gating without dispatching to a binary. Replaces the "binary returns permissionDecision" round-trip with declarative conditions in the manifest itself.

### Inline `type: agent` hooks invoking secondary models

PreToolUse / PostToolUse / PreCompact / Stop hooks declared with `type: agent` and a literal multi-hundred-character prompt that invokes a secondary model (Haiku) for review. Stop's agent reads workspace state files and returns `{"decision": "block"}` to gate session termination. Parallel model invocation during hook evaluation; differs from the usual "hook calls a binary" pattern. Specific hooks return `{"permissionDecision": "deny"}` when the embedded agent or rule detects a violation (secrets in commit, TODO markers, injection patterns).

### Compensating revert (PostToolUse defense in depth)

Matcher `"Write|Edit|MultiEdit|Bash"`, purpose: if a write slipped past PreToolUse for a role that should not write (e.g. PreToolUse fail-opened, or a custom role bypassed scope), revert the write. `git checkout` for tracked files; `rm` for untracked. Ledger records `revert_mode` and `revert_success`. Appropriate when the plugin's correctness model is "no out-of-scope writes ever, even if a gate bug fires" — pairs with PreToolUse to make scope a two-layer guarantee.

### Format-then-lint PostToolUse (non-blocking)

PostToolUse runs `scripts/format.sh` then `scripts/lint.sh` sequentially, both non-blocking — warns on failure, doesn't block. Dual command in a single hook entry. Lightweight; assumes the formatter/linter are installed on the host.

### Full rule engine with cross-file pattern aggregation

PostToolUse runs a 13.5KB+ rules engine that consults a session-state DB (SQLite) after recording a violation. If the same rule has fired in 3+ files this session, the hook appends a "PROJECT-WIDE PATTERN: {rule} found in {N} files — consider a project-wide fix or global ignore" banner to the block/warn message. Session-aware violation aggregation delivered through hook output. Per-rule inline suppression supported via `<plugin>-ignore: <RULE_ID>` comments inside source files.

### Informational fail-open post-edit hook

Single `Edit|Write` `PostToolUse` hook running an incremental typecheck on the edited file. Implemented fail-open (`.catch(() => process.exit(0))`) — never blocks tool flow. Purely informational; surfaces typecheck issues as warnings without obstructing the edit. Counterpart to fail-closed `PreToolUse` enforcement: pre-checks gate, post-checks observe.

### PostToolUse doc-size guard + state sync

Hook matches `Write|Edit` and enforces a doc-size cap plus syncs the plugin's gate state to reflect the just-completed write. Two responsibilities chained on the same matcher.

### PostToolUse `*` context tracking

Hook matches `*` and records every tool call to the plugin's context store; always-on observability. Distinct fail-open posture — context tracking that fails should never block the user.

### Test-success unlocks subsequent action

`PostToolUse` matcher `Bash` (with `async: true`) inspects the tool result's exit code and command line; if exit is 0 and the command matches a regex of common test runners (`run-tests.sh|phpunit|jest|vitest|pytest|cargo test|go test|npm test|pnpm test|yarn test`), the hook flips a session-state `verified=true` flag. A separate PreToolUse on `git push` (via `if: "Bash(git push*)"`) reads that flag and allows the push without further friction. Emergent workflow: "test-then-push unlocks push automatically." State-machine semantics implemented across two stateless hooks via shared session state.

### Manual-only PreCompact with self-healing seam check

`PreCompact` hook with `matcher: manual` (so auto-compact is never blocked — it could push context over 100% and lose everything). On manual `/compact`, the hook reads `.reviews/handoff.json` and blocks if status is `PENDING_REVIEW` or `PENDING_RECHECK`, or if a git rebase/merge/cherry-pick is in progress. Self-heals: if the handoff has a `pr_number` and `gh pr view` reports the PR `MERGED`, the gate clears the status and lets the compact proceed. Requires Claude Code v2.1.105+.

### TaskCompleted hard-block on missing memo/result

Hook matches `TaskCompleted`, reads task ID from the payload, calls the sidecar API to verify the task has a memo and result recorded; on failure writes `[OS BLOCK] <reason>` to stderr and exits code 2 (the hard-block convention). Connects the hook's deny convention to external business state (sidecar API), not just local rules — a hook that enforces "you can't mark this done until you've logged progress."

### Event forwarding to sidecar (PreToolUse + PostToolUse)

Hook matches `Agent|Bash|Edit|Write` and forwards the event payload to a plugin-owned HTTP server (`POST /api/hooks/<event>`). Pure observer — no policy decisions in-hook; the sidecar dashboard consumes the events. Pays a per-tool-call subprocess spawn cost (paired with a sibling reminder hook on the same matcher means two spawns per pre and post phase).

### PostToolUse local workflow reminders

Hook matches the same broad event set and emits stdout reminders based on a local rules engine (delegation-threshold counters, sequence triggers). Self-described <100ms target with local-only file I/O. Large hook script (~54KB) representing a non-trivial rules engine in the hook layer — "thick local hook, thin sidecar server" division of labor.

### TDD reminder (PreToolUse on src/ writes)

PreToolUse with an `if:` clause narrowing to writes under `src/**`. On match, emits `hookSpecificOutput.additionalContext` with a "write a failing test first" prompt. Fail-open (no `set -e`); silent on non-matching paths.

### Observational notification trigger

Matcher `"ExitPlanMode|AskUserQuestion"` (and similar Claude-Code-decision events), purpose: fire desktop or webhook notifications when Claude reaches a decision point. Not gating — never emits deny. `timeout: 30` to avoid hanging the host. Appropriate when the plugin's role is alerting the human, not modifying the model's flow.

### Validate-and-nudge on InstructionsLoaded

`InstructionsLoaded` hook validates that project documentation files (e.g., `SDLC.md`, `TESTING.md`) exist, nudges on missing files, on stale plugin version (≥3 minor delta), and on open API-shepherd issues from a weekly cron. Cheap one-shot check at session start. Available since Claude Code v2.1.69 — version floor declared inline in hook comments rather than in `plugin.json`.

### `PermissionDenied` classification with retry-state TTL

Hook reads denial JSON, calls a sidecar API to classify into one of four buckets (`recoverable_with_retry`, `recoverable_with_workaround`, `needs_user_approval`, `permanent_denial`), then emits retry hints, workaround guidance, or logs silently per classification. Falls back to local keyword matching when API is unreachable. Retry state persisted in a JSON file with 1-hour TTL to prevent retry loops. Hook-as-classifier — offloads policy decisions to a sidecar so policy updates don't require redistributing the plugin.

### `PermissionDenied` as event log

The `PermissionDenied` hook event is registered, but the handler treats it as a counter / log source, not an enforcement gate. The hook tallies denials and surfaces the count in a report. Constrains nothing about future tool calls. Appropriate when the goal is observability rather than gating.

### Repo-scope self-restriction

Hooks inspect `cwd` for `.claude-plugin/plugin.json` (or another sentinel) and exit silently when run outside the methodology repo. Prevents the plugin's enforcement from interfering with unrelated projects on the same host. Constrains the hook surface to the repo where it makes sense; means the hook never fires outside that repo unless `/adopt` has written project-level settings. Appropriate for plugins whose enforcement only applies to their own methodology context.

### Documented bypass mechanism

A sentinel file (e.g. `.methodology-self-extend-override`) that, when present in the repo, suppresses hard-enforcement hooks. Documented in the hook README rather than hidden. Constrains the hook's invariant — "block unless escape hatch is explicitly present." Appropriate when there are legitimate cases (extending the methodology, e.g.) where the invariant should not apply.

### Numbered-requirement traceability annotations

Every security-critical hook source file opens with a `SECURITY notes (inline refs)` block listing `REQ-01` through `REQ-NN`, and every relevant function cites its REQ number inline (`// SECURITY-REQ-03: resolve symlinks ...`). Pattern: requirements in a security pre-review document trace to specific lines of code via comment annotations. Discipline that lets a reviewer confirm coverage by grep rather than by re-deriving the threat model. Notable for agent-written code where the requirement-to-line traceability would otherwise erode rapidly.

### No tool-use enforcement (observational only)

Plugin ships no `PreToolUse` or `PostToolUse` hooks, or uses hook events purely for reporting. Surface is install-only (`SessionStart`) plus user-facing components. Even events like `PermissionDenied` are inert as gates. The MCP server, when present, may have its own defensive code (typed errors, top-level `process.exit(1)` on fatal errors), but that's runtime defense inside the server, not Claude Code hook enforcement. Constrains the plugin's operational role to reporter / observer.

### Rule engine reuse across hook + CI lanes

Both `ci/<plugin>-ci.sh` (pipeline-mode CI) and `hooks/post-write-check.sh` (real-time-mode hook) source the same `hooks/lib/pack-loader.sh` and `hooks/lib/rules-engine.sh`. README markets this as "zero drift" — same engine invoked at two different lifecycle points. Adapter pattern (`adapter_detect/run/annotate/comment/exit`) provides four CI-provider implementations (GitHub Actions, GitLab CI, Bitbucket Pipelines, Jenkins). One engine; two surfaces; pluggable CI substrate.

## Hook handler runtime

What language or binary the hook handlers run on, and how dispatch is structured.

### Bash scripts at conventional path

Hook commands point at `.sh` files in `hooks/scripts/`. Mixed shebangs across scripts (`#!/bin/bash`, `#!/usr/bin/env bash`). May use `set -uo pipefail` (NOT `-e` because `realpath` and other commands that may fail on not-yet-existing files cannot use bare `set -e`). Handlers may print stderr human text only, never JSON, with soft-exits throughout. Appropriate for low-complexity side-effects (frontmatter checks, edit logging) where bash is sufficient and the failure mode should never block tool calls.

### Single Go binary with subcommand dispatch

Every hook entry calls `${CLAUDE_PLUGIN_ROOT}/bin/<plugin> hook <event-name>`. The binary owns hook protocol, JSON schema emission, decision logic, and per-event handlers. One executable, many entry points. Appropriate when the plugin's logic is large enough to warrant a compiled engine and when consistent JSON output across all hooks matters (the binary alone knows the full schema).

### Python stdlib runner with external probing

Hooks call `python "${CLAUDE_PLUGIN_ROOT}/runner/run.py"` (a single Python file using only stdlib). Runner shells out to system audio binaries (`mpg123`, `ffplay`, `paplay`, `aplay`, `afplay`, PowerShell players) by probing the platform. No Python venv, no third-party packages. Appropriate when the only "dependencies" are system tools the user already has, the failure mode should be silent skip, and zero-install is the design goal.

### Node `.mjs` files invoked via `node`

Hook commands point at `hooks/<name>.mjs` invoked through `node` in `hooks.json`. ESM modules with top-level `import`. Requires a `node_modules/` adjacent (see *Dependency installation*). Appropriate when the plugin's runtime is Node and its hooks share a library tree.

## Hook output contract

How hooks signal decisions to the harness and surface them to the user.

### Stderr for human display + stdout JSON for harness

Hook emits a human-readable message on stderr (terminal display) AND a `hookSpecificOutput` JSON object on stdout (harness's permission-decision schema). Both surfaces are written for blocking exits; warning-only exits emit only `{systemMessage: "..."}` on stdout. Without stderr, the user sees only "No stderr output" and no actionable message — the dual contract is required for usable UX. CHANGELOG entries explicitly call out fixes for this regression. Stderr is reserved for debug-mode logs prefixed with the plugin's name; stdout for the contract — the JSON-on-stdout discipline is maintained regardless of debug verbosity.

### `systemMessage` for human-readable summaries

Hooks emit `{"systemMessage": "..."}` JSON on stdout for report-style output that Claude Code surfaces inline. Used for completion-event reports (Stop, TaskCompleted, etc.). Constrains output volume to whatever Claude Code's hook-output cap allows (10,000 chars; overflow silently replaced with an opaque stub).

### `additionalContext` for context injection

Hooks emit `{"hookSpecificOutput": {"additionalContext": "..."}}` JSON to inject context the agent reads. Used by PreToolUse advisory injection and by SessionStart/UserPromptSubmit context loading. Distinct from `systemMessage` in that the agent processes the content rather than the user reading it directly.

### `decision: "block"` for gating

PreToolUse hooks emit `{"decision": "block", "reason": "..."}` JSON to refuse a tool call. Used by hard-blocking gates and the env-var-gated optional gates. Stderr carries the human message; stdout carries the contract.

### Inline-truncated + full-HTML dual output

When a report exceeds Claude Code's 10,000-char inline cap, the inline copy is truncated with `⋯ +N more — see HTML report` markers while a full HTML file is always written to a project-relative path (`<project>/reports/<plugin-name>/<timestamp>-<event>-<session>.html`). Convention is per-author across all their plugins, not a Claude Code platform feature. Constrains the plugin to manage its own out-of-band output store. Appropriate when reports legitimately exceed the inline cap and the user wants both a quick scan and a deep-dive.

## Hook failure posture

How hook scripts handle their own exceptions, and how those failures relate to tool execution.

### Fail-open with top-level try/except

Every hook script wraps `_main()` in try/except and calls a `_fail_open()` helper on any exception (or top-level try/catch in JS), which writes `[<plugin>] <error>` + stack trace to stderr and emits `exit 0`. Even the fallback's own ledger-write attempt is wrapped in its own try/except. Every step wrapped; uncaught failures fall through to allow. Rationale: "a bug in the hook never deadlocks the agent" / "Never throw from a hook function." Appropriate for non-blocking observational hooks; the cost is silent partial failure unless the user reads stderr.

### Fail-open envelope via `trap 'exit 0' ERR`

Every hook script opens with `set -uo pipefail` plus `trap 'echo "WARNING: <hook> failed at line $LINENO" >&2; exit 0' ERR` — on crash, the hook emits a warning to stderr but exits 0 so writes/pushes are never blocked by hook bugs. Codified at the project level: "all hook scripts MUST use `exit 0` (pass) or `exit 2` (block); NEVER `exit 1`." Pairs with explicit-exit-code discipline inside the hook body.

### Fail-open with degraded-mode fallback

When a runtime dep is missing (e.g. `tiktoken`), the plugin falls back to a cruder approximation (chars/4 estimate) and writes a warning to stderr. Hook still exits 0. Constrains the report's accuracy but preserves liveness. Appropriate when graceful degradation is more useful than total absence.

### Fail-closed with circuit breaker (retry with backoff)

A purpose-built `HookCircuitBreaker` wraps the hook body, retrying with backoff (e.g. 100ms, 500ms) before escalating to a per-hook configurable failure mode: `deny` for pre-tool, `block` for subagent-stop, `warn` for stop. Configurable per mission via a manifest flag. Pattern-influenced by Erlang/OTP and resilience guidance. Appropriate when correctness matters more than blast-radius — gates that must not silently fail.

### Pessimistic no-opinion (exit 0 with no output)

The hook exits 0 with no stdout output on any uncertainty rather than emitting `allow` or `deny`. Effect: Claude Code falls back to its normal permission flow and prompts the user. Distinct from fail-open-with-allow (which auto-approves on uncertainty) and from deny-on-uncertainty (which over-blocks). Appropriate for permission-augmenting hooks where over-approval is a safety problem; the cost is a slightly busier permission UX when the validator is fragile.

### Mixed posture (fail-closed for security, fail-open for context)

Per-hook decision documented in code comments. Security-sensitive matchers (`bash-guard`, `workflow-guard`, `task_completed_gate`) emit deny + exit 2 on policy violation. Observability hooks (context trackers, banner printers, dep installers) swallow errors and exit 0. Mixed posture is intentional and documented per-hook. Combines naturally with inline `type: agent` hooks where the agent's judgment is the gating signal.

### Silent-ignore graceful degradation

Older Claude Code versions silently ignore unknown hook event names, missing `userConfig`, etc. Plugins relying on the host's silent-ignore behavior have no machine-readable version floor — the runtime degrades to whatever subset the host supports. Constrains version-floor declaration to documentation only.

## User configuration surface

How the plugin lets a user customize its behavior — declared `userConfig`, env vars, custom config files, OS credential stores, or markdown blocks.

### No `userConfig`, env-var only

`plugin.json` declares no `userConfig`. Configuration is read from shell environment variables (`<PLUGIN>_CACHE_DIR`, `EFFORT_LEVEL`, `ANTHROPIC_API_KEY`, etc.) by the plugin's own helper at runtime. SKILL.md documents which env vars are required. Knobs that exist (e.g., service API keys for a paid tier) are read from process env outside the plugin manifest, requiring users to set them through the host's separate env config. Sidesteps the schema but loses Claude Code's `sensitive: true` flag and built-in CLI-driven UX for the secret fields. Appropriate when the only configurable surface is secrets that should not pass through plugin config; the cost is invisibility to Claude Code's `/plugin` settings UI.

### Typed `userConfig` schema

Top-level `userConfig` object declares typed fields (`type` (`number`/`boolean`/string), `title`, `default`, `description`, `enum`, `required`); Claude Code surfaces these in the install/configure UI. Descriptions can be substantive (multi-sentence, with links to upstream documentation explaining the default). The substituted values reach the runtime via `CLAUDE_PLUGIN_OPTION_<KEY>` environment variables Claude Code sets when invoking hooks. Schema richness varies — `title`/`description` always present; `default`, `enum`, `sensitive` optional and frequently omitted (enum values may appear only in prose descriptions, leaving install-time validation gap). Appropriate for a small bootstrap surface (≤5 fields) with a deeper config schema mutated out-of-band by the plugin's CLI.

### Rich userConfig with sensitive flag

Multi-field `userConfig` with `title`, `type`, `description`, `required`, `default`, and `sensitive: true` on the secret fields. Numeric/boolean fields declare defaults; the secret field carries the description "stored securely in keychain". Aligns with Claude Code's secure-storage UX. Manifest-level substitution via `${user_config.<KEY>}` in `.mcp.json` env blocks or hook commands is a separate concern — declaring fields and wiring them are independent steps.

### `userConfig` declared but not wired through manifest substitution

Fields declared (with `sensitive: true` etc.) but no `${user_config.<KEY>}` references in `.mcp.json` env block or hook commands. The runtime reads credentials from a chain of fallbacks (userConfig → env var → on-disk config file at `~/.<plugin>/config.json`). Documented in README but not enforced in the manifest — if the runtime code path that queries userConfig is absent or stale, the userConfig surface is a no-op.

### Env-var fallback alongside userConfig

For hosts (older Claude Code versions) that don't support `userConfig`, the plugin reads plain env vars (`<PLUGIN>_<KEY>`) as a documented fallback. The runtime checks both the userConfig-populated env var and the plain-env name. Constrains the plugin to maintain two env-var conventions but extends host coverage. Appropriate when backwards-compat with a wider host set matters.

### `CLAUDE_PLUGIN_OPTION_<KEY>` env-var consumption

Hooks read userConfig values through Claude Code's `CLAUDE_PLUGIN_OPTION_<KEY>` env vars (e.g., `CLAUDE_PLUGIN_OPTION_agent_hooks` for early-exit on a boolean toggle). No `${user_config.KEY}` token substitution in hook commands — values flow through env vars instead. Coexists with a parallel project-level YAML config file (`.craft-config.yml`); SessionStart warns when the two surfaces diverge, but neither is canonical.

### No `userConfig`, custom JSON config + slash command

`plugin.json` declares no `userConfig`. The plugin maintains its own `config/config.json` schema (richer than `userConfig` allows — webhook presets, per-status overrides, platform flags) and exposes a slash command (e.g. `/<plugin>:settings`) to edit it. `${CLAUDE_PLUGIN_ROOT}` is referenced inside the JSON for resource paths and is expanded by the plugin's own runtime, not by Claude Code's substitution mechanism. Appropriate when the schema needs are too rich for `userConfig`; the cost is no presence in Claude Code's UI and a parallel config-edit UX for the user.

### External config file owned by plugin

Plugin reads its own JSON/YAML file (`root.config.json`, `.claude-code-harness.config.yaml`) from the consumer's repo or a known location. Schema is plugin-controlled, often versioned (`configVersion: 2`) with in-plugin migration logic to upgrade older versions on session start. Bypasses Claude Code's config UI entirely — config authorship is in the consumer's repo, version-controlled with the project. Appropriate when the surface is large enough that `userConfig`'s flat schema would be unwieldy or when config needs to evolve through schema migrations the plugin itself owns.

### Layered file-based config with schema-versioned migration

Three-tier file system replaces `userConfig`. Plugin-side defaults (`<plugin>-config.default.json`) → user-side migrated copy at `${CLAUDE_PLUGIN_DATA}/<file>.json` → project-side state (`.pipeline/project.json`). Plugin-side default JSON carries a `schemaVersion` integer. SessionStart hook compares it against the live user-side copy; on mismatch performs field-level diff-merge that adds/updates plugin-owned fields (providers, models, agentMap entries) while preserving user-owned fields (`enabled`, `envVar`, user-added entries). Writes a timestamped `.bak-<ISO>.json` backup before overwriting and logs a one-line summary. Robust when config-schema evolution is a regular need; the backup preserves the pre-migration state for rollback. The migration logic ends up nearly as expressive as a `userConfig` schema would be — purpose-built for the project's specific shape.

### `.env` files in cloned repo

User edits a `.env` file (or `.env.example` template) in the cloned repo. Secrets (`ANTHROPIC_API_KEY`, DB creds, `REDIS_URL`) live outside Claude Code's plugin config surface entirely. Appropriate when the plugin backs a long-running server that needs config to persist outside any single Claude Code session. Cost: users don't benefit from Claude Code's secret-handling affordances.

### OS-level secret storage

`plugin.json` declares no `userConfig`. Secrets live in OS credential store (Keychain / Secret Service / Credential Manager), accessed by Python at runtime. Justification: cross-agent sharing — the key is stored once and shared across all agents on the machine. A `userConfig` field with `sensitive: true` would fragment storage per-agent. Trade-off: users don't get install-time config-prompt UX; configuration happens via a one-time interactive wizard.

### Home-directory KEY=VALUE file

The native binary reads `~/.config/<plugin>/config` directly (KEY=VALUE lines, optional `export` prefix, no shell expansion). Plugin declares no `userConfig` in `plugin.json`. Decouples config lifetime from plugin cache churn — config survives uninstall/reinstall — but sacrifices Claude-Code-side discoverability and validation. Priority chain documented as `CLI flag > env var > config file > default`. Constrains the plugin to handle config parsing and schema enforcement entirely in its own runtime code.

### Markdown block in consumer's CLAUDE.md

Plugin parses a `## Session Config` block from the consumer repo's `CLAUDE.md` or `AGENTS.md`, extracting fields (`test-command`, `typecheck-command`, `lint-command`, `enforcement`, `agents-per-wave`, `waves`, `allow-destructive-ops`, etc.). Validated against a homegrown JSON-Schema (`config-schema.mjs`); a bypass env var (`SO_SKIP_CONFIG_VALIDATION=1`) lets users opt out for emergencies. The plugin re-implements parser + validator rather than using the platform's `userConfig` mechanism. Constrains config to a markdown surface users already maintain, enabling per-project config without Claude-Code-side plumbing, at the cost of a parallel parser the plugin must keep aligned with the schema.

### Per-mission flags (no install-time config)

Configuration passes as CLI flags to the plugin's own CLI verb (e.g. `<cli> init --objective ... --allowed-path ...`) for each invocation. No persistent install-time config exists. Appropriate when the configurable surface is mission-scoped rather than session-scoped.

### No user-tunable surface

`plugin.json` has no `userConfig`; behavior is fixed. Appropriate for plugins whose value proposition has no meaningful axes of variation.

### Per-rule inline suppression

`<plugin>-ignore: <RULE_ID>` comments inside source files disable specific rules on that line or file. Multi-rule form `<plugin>-ignore: PHP001, TS001, LAYER001` supported. Helpers `line_has_ignore` and `file_has_ignore` in the rule engine. Metrics record both "blocked violations" and "ignored violations" — partial suppression is first-class, not a workaround.

### Inline file-mode modifier comments

Source-file comments declare the active stack/layer for the ruleset (e.g., `<plugin>-stack: symfony`), enabling per-file rule tuning without external configuration. Same channel as inline suppression.

### Settings.json env-field workaround

In-code comment: "Plugin settings.json env field is NOT supported by CC (only 'agent' key works)." A SessionStart hook writes the required env var (e.g. `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) directly into `~/.claude/settings.json` as a workaround. Concrete data point on a documented-but-actually-broken plugin capability. Fragile because it modifies user-scope settings the user may have customized; appropriate only when the env var is plugin-essential and has no other delivery channel.

## State persistence

Where the plugin keeps state that survives across sessions — caches, ledgers, manifests, mission state.

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

### SQLite for behavioral metrics

`metrics.db` SQLite database under `${CLAUDE_PLUGIN_DATA}` tracks rule-violation events and corrections across sessions. Atomic writes; SessionStart queries trends and surfaces them as `Learning: <rule> fix rate <pct>%` in the session context payload. Persistence is local per-machine — no cloud sync. "Behavioral feedback loop" framed as a unique-in-the-ecosystem capability by the project's README.

### State-of-watcher files in `.github/last-checked-*.txt`

Repository-tracked state files (`.github/last-checked-version.txt`, `.github/last-community-scan.txt`, `.github/last-checked-api-date.txt`) act as durable cron-watcher checkpoints — "where did I leave off?" — committed back to the repo so the next cron run resumes correctly. CI enforces their existence as a structural invariant.

### Sidecar port-discovery file

Plugin's API server writes its actually-bound port into `~/.claude/data/<plugin>/api_port.txt` at startup; hooks read the file before each call to resolve the URL. An env var (e.g. `<PLUGIN>_API_URL`) overrides. Lightweight IPC contract — handy when port 8000 is taken; risky when two projects run concurrently because only one wins the file. Concrete bug reported in changelog where a hardcoded `.mcp.json` env var defeated the fallback.

### Runtime resolution variable chain

How scripts resolve `${CLAUDE_PLUGIN_ROOT}` (or the data-dir analog) when the harness might or might not have set it. Two-tier env-var-first fallback (`${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}`) is the standard pattern; works whenever the script has a real path on disk. Three-tier with hardcoded data-dir terminal fallback (`${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd || echo "$HOME/.config/<plugin>")}`) adds a hardcoded user-config path as the third tier — semantically wrong for code that needs to read SKILL.md siblings but works by coincidence because `2>/dev/null || true` swallows the resulting failures. Cascading multi-host fallback (`${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}`) supports invocation from Claude Code (first), Codex (second), or git working tree (third). Used when the same plugin code ships into multiple agent ecosystems.

### Runtime policy file tree

A directory tree under `.orchestrator/policy/` (or similar) holds runtime policies (`blocked-commands.json` with N rules, `quality-gates.schema.json` plus `.example.json`, `ecosystem.schema.json`). Hook reads the policy plus a per-session scope file (`wave-scope.json`); the contract between policy and hook is a JSON-Schema rather than inline rules in code. Pattern: pluggable policy JSON loaded per invocation. Lets the user (or the plugin's own session-start skill) edit rules without modifying hook source. Constrains schema evolution: any policy field rename requires updating both the schema file and every consuming hook.

## Sidecar daemon

Whether the plugin runs a long-lived background process beyond the Claude Code session, and what it does.

### No daemon — session-bounded only

Plugin process state lives entirely within the Claude Code session. No background server, no sidecar dashboard. Hooks are short-lived shell/script invocations; state persists via files on disk. Lowest operational footprint. Appropriate for skill-shaped plugins.

### Local Fastify HTTP daemon on a fixed port

The plugin runs a Node Fastify worker on `localhost:<port>` with multiple endpoints (e.g., `/api/version`, ingestion endpoints, query endpoints), auto-started by `scripts/worker-start.sh` from `session-start.sh`. PID + port files in the data dir. UserPromptSubmit hook checks the worker's `/api/version` against the installed plugin version on every prompt and kills+restarts on mismatch. A separate MCP server process runs alongside, both reading the same SQLite via per-call DB resolution. Goes well beyond "plugin is a directory of markdown + scripts" — it's a full long-running service. Architecture (worker + MCP server as peer processes sharing SQLite) is distinctive; significant operational complexity.

### Persistent FastAPI server with React dashboard UI

Plugin runs its own FastAPI process on a fixed port (e.g. 8000) and ships a React dashboard built into `plugin/dashboard-dist/`. Hooks forward events over HTTP to the FastAPI app; the dashboard consumes them. Sidesteps Claude Code's `monitors.json` mechanism entirely because the UI is served by the plugin's own HTTP server. Trades the tidy single-process model for a persistent-daemon architecture. Appropriate when long-running coordination state must survive across sessions and user-facing observability requires more than terminal output.

### Sidecar terminal observer with auto-split

Plugin invokes `scripts/forge-observer.mjs` from a SessionStart hook to launch a local auto-split terminal observer alongside the Claude session. Plugin-native concept named "observer" or "dashboard" — distinct vocabulary from Claude Code's `monitors.json` mechanism. Different surface area; same intent (visibility into long-running plugin state) achieved without Claude Code's monitor primitives.

## Live monitoring

Whether the plugin uses Claude Code's monitor surface or alternative ambient-tick mechanisms, distinct from the sidecar daemon question.

### `monitors.json` absent

No `monitors.json` in observed samples. Notifications, when produced, flow through the hook system (Stop, SubagentStop, Notification, TeammateIdle) directly. The samples surface this is a real gap: a plugin literally named "notifications" does not use the documented monitor channel — anyone searching for monitor examples would miss it. Either the surface is too new, the plugins predate it, or none have a polling-style use case. Constrains the plugin's ability to do truly background work without piggy-backing on hook events. Appropriate to flag as a corpus-wide observation: monitors may be under-adopted relative to their advertised role.

### `monitors.json` with single watcher

`monitors/monitors.json` declares one monitor (`<plugin>-session-monitor`) with `when: always` that polls workspace state for drift signals. Reuses the same hook-binary subcommand surface (`bin/<plugin> hook session-monitor`) so monitors and hooks share one binary and one dispatch plane. Version-floor declared in README ("v2.1.105+ recommended (PreCompact hook + monitors manifest)").

### Status line via user-settings mutation

The plugin ships a status-line script and provides a CLI subcommand (`<plugin> statusline install`) that mutates the user's `~/.claude/settings.json` to register the script. Plugin manifest does not declare statusline capability. Pros: explicit user opt-in. Cons: uninstall does not automatically reverse the mutation; statusline registration outlives plugin removal unless the user runs `<plugin> statusline uninstall`. A `statusLine` entry can also be invoked from `.claude/settings.json` directly to render a per-session status line, updated reactively via PostToolUse hook on specific MCP tool calls.

### External-change watcher (shepherd pattern)

Cron-scheduled GitHub Actions workflows poll external sources (release pages, API changelogs, community forums) on a schedule (weekly Monday 09:00 UTC, monthly 1st 11:00 UTC). They do cheap detection only and open or update a single tracking GitHub issue per source; an `InstructionsLoaded` hook nudges the next session toward those issues. The Anthropic API changelog detector specifically fetches `.md` URLs (Mintlify convention) rather than scraping rendered HTML — deliberate stability choice. A simpler in-plugin form polls `npm view <package> version` at most once per 24h (cached at `$HOME/.cache/<plugin>/latest-version`, regex-validated as semver) and emits a non-blocking warning to the next session — loud multi-line block at ≥3-minor lag, mild one-liner otherwise. Replaces what `monitors.json` would do at the plugin level.

### Update notification mechanism

Skill body opens with a `## Preamble (run first)` block that the agent shells out on, invoking `bin/<plugin>-update-check`. The script polls a release endpoint, writes a status cache (with a TTL to avoid hitting the endpoint every invocation), and emits one of `UPGRADE_AVAILABLE`, `JUST_UPGRADED`, or nothing. The agent parses output and conditionally surfaces a notification. State coordination uses sentinel files in the data dir (`last-update-check`, `update-snoozed`, `just-upgraded-from`); the install hook writes some, the update-check reads and clears them. Constrains discovery to skill invocation: agents never invoking the skill never see the notification.

### No update mechanism

Plugin ships no update poller. `/plugin update` re-fetches the marketplace entry but the plugin's runtime never proactively checks for new versions. Users discover updates through external channels (release feeds, social posts, the marketplace browse UI).

## Telemetry and event emission

Whether the plugin emits structured events about its own lifecycle, and to where.

### JSONL append plus optional remote POST

A library (`scripts/lib/events.mjs`) writes structured events as JSONL appends to `.orchestrator/metrics/events.jsonl` (or similar). When an env-var secret (e.g. `<PLUGIN>_EVENT_SECRET`) is set, events also POST to a configurable webhook via native `fetch` plus `AbortSignal.timeout(3000)`; errors are swallowed so remote failures never affect local execution. Pattern: graceful optional remote telemetry. Local logging is always on; remote forwarding is opt-in by environment.

### No telemetry

Plugin does not emit structured events. Diagnostic information lives only in stderr of hook invocations and log files the user inspects manually.

## Test framework

What runs the tests — language, runner, harness, discovery convention.

### Python unittest (stdlib) under pytest discovery

Tests use stdlib `unittest` (module-level classes); the discovery/runner is pytest invoked as `python -m pytest tests/ -v`. No `pytest.ini` or `[tool.pytest.ini_options]`; pytest's default discovery suffices. Appropriate when the project values stdlib-only test code but accepts pytest as the runner for its better output and discovery; the cost is the contributor must know that pytest will pick up unittest-style classes.

### Python unittest with explicit `unittest discover`

Tests run via `python -m unittest discover -s tests -p 'test_*.py' -v`. No pytest. Stdlib-only. Appropriate when stdlib-only is a hard policy; the cost is somewhat noisier output and slower test feedback compared to pytest.

### pytest with optional inline cov

Tests in `tests/` at repo root using pytest with `pytest-cov` and optionally `pytest-asyncio`. Pytest config either in `pyproject.toml` `[tool.pytest.ini_options]` (canonical) or absent (CI invokes pytest with inline flags). Tests cross the skill boundary — import skill scripts via `sys.path.insert` + `importlib.util.spec_from_file_location` when the skill code isn't a packaged module. Standard Python test posture.

### Stdlib-only Python rubric tests

Tests are zero-dependency Python 3.11 stdlib scripts (`tests/meta_review.py`, `tests/verify_snapshot.py`, `tests/verify_triggers.py`), invoked directly via `python3 tests/<script>.py`. No pytest, no test framework. Plus bash fixture-runner scripts for live-CLI tests. Test model is "structural-rubric + golden snapshots," not unit tests. Each rubric check has a stable ID (`M-C1`...`M-C16` Critical, `M-I1`...`M-I9` Important) referenced in CHANGELOG entries — CI-check-as-named-entity. Constrains contributors to write rubric checks in stdlib idioms; rationale: <30s runs, no supply-chain risk in CI itself, runnable locally without setup. Appropriate when the project privileges CI itself being trust-minimized.

### Smoke-only Python import + subcommand exercise

Single `smoke.yml` workflow runs `python -c "import hook_runner"` against canonical and packaged paths, invokes every CLI subcommand once (`audio-hooks.py test all` dispatches all 26 hooks), and runs a `--check` plugin-sync verification. Matrix across OS × Python versions (`ubuntu × windows × macos × 3.9 × 3.12 × 3.13`, fail-fast: false). Catches runtime regressions; does not validate schemas.

### Go test

Tests run via `go test -v -race -coverprofile=coverage.txt -covermode=atomic ./...`. Colocated `*_test.go` files alongside source per Go convention. CGO-enabled tests (`malgo` for audio) exercise `-race` across all OSes. Appropriate when the runtime is Go; the cost is platform asymmetry (CGO doesn't cross-compile cleanly to all arches).

### cargo test

Rust integration-test layout — `tests/` at repo root holds top-level integration test files (`crash_recovery_test.rs`, `doctor_test.rs`, `multi_venv_test.rs`, `smoke_test.rs`, `venv_detection_test.rs`) with shared fixtures under `tests/support/mod.rs`. Wrapped behind `make ci` (= `fmt-check` + `clippy -- -D warnings` + `cargo test`).

### Node `node:test` chained suite

Hundreds of `tests/<name>.test.js` files under one flat directory; each wired to a `test:<name>` npm script; the root `npm test` chains 70+ entries with `&&`. Sequential, ordering-load-bearing, single failure aborts the chain. Constrains parallelism (none) and ordering discipline (highly so). Plus a separate `prove:*` tier — seven scripts that emit machine-readable `proof/<area>/report.{json,md}` artifacts to GitHub Actions, distinct from the `test:*` tier. Appropriate at scale where the maintainer wants every behavior covered and accepts the long-chain trade-off; the `prove:*` tier supports post-hoc auditing of CI runs.

### Multi-runner — `node --test` + bats

`node --test` (built-in Node test runner) for JS test files co-located with code (`worker/**/*.test.js`), plus `bats-core` (submodule-pinned) for shell-integration tests under `tests/*.bats`. Mixed runner per language. Submodule pinning the bats binary aims for reproducibility but introduces a "submodule not fetched" graceful-skip path that can mask CI gaps.

### Custom Node `node:test`-style runner with suffix discovery

Custom runner at `scripts/run-tests.mjs` discovers tests by directory + suffix convention (`hooks/*-test.js`, `mcp/*-test.mjs`), spawns each via `node <path>` sequentially, inherits stdio, aggregates exit codes. No Jest/Vitest dependency. Tests are plain assertion scripts co-located with the code they test. Tight discovery — a contributor adding `*.test.js` (dot, not hyphen) silently skips. Appropriate when avoiding test-framework dependency is a goal.

### vitest with multi-suite layout

Vitest as the primary runner, configured via `vitest.config.mjs` to glob both top-level `tests/**/*.test.mjs` and nested skill-local `skills/*/tests/**/*.test.mjs`. Tests are organized into `hooks/`, `integration/`, `lib/`, `skills/`, `unit/`, `fixtures/` subdirs at repo root. Replaces an earlier bats-based suite. Direct invocation via `npm test` → `vitest --run`; typecheck delegated to a custom `node scripts/typecheck.mjs` rather than `tsc`.

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

### Co-located test placement

Tests sit next to source files (`hooks/gate-sync-test.js` next to `hooks/gate-sync.js`, `mcp/router-test.mjs` next to `mcp/router.mjs`). Discovery happens via filename suffix. No central `tests/` directory. Appropriate when tests pair tightly with their immediate source and the project has no need for a global test root.

### Centralized `tests/` placement

All tests under a root `tests/` directory, often subdivided into `unit/`, `integration/`, `e2e/`. Plugin/code tree separate. Standard Python posture. Appropriate when tests are organized by category or scope rather than by source-file pairing.

### No tests

Repo has no `tests/` directory and no test files. No round-trip validation of manifests, no smoke test of install scripts, no MCP-server registration test. Quality assurance is manual; release process is commit-to-main. Bug-detection burden falls entirely on consumers and human review.

### Tests referenced but absent in tree

The repo references tests in release-script docstrings (`scripts/publish.py` gate 6 expects `tests_dev/`) but no test directory is checked in. Either gitignored locally-only or the gate is dormant. Constrains the project's claimed test discipline to the maintainer's local machine. Appropriate when the maintainer treats tests as private and CI as a public surface.

### Retroactive CI as documented regression response

CI added in direct response to a specific shipped bug; CHANGELOG entry explicitly cites the regression that motivated each gate. Commit history reads as "no CI → broken tag → add CI gate that reproduces the bug" — clean case study of post-incident gate accumulation.

## CI workflow shape

What CI does on push/PR, how strictly it gates merges, and how the workflows are organized.

### No CI

No `.github/workflows/` directory. Nothing verifies version-bump → tag → install path on each commit. Failures show up on user `SessionStart` only. Regressions are caught only when someone runs the test suite locally. Appropriate when the project is single-author and pre-1.0; risk grows as contributors and release cadence grow.

### Single workflow, OS × language matrix

One `.github/workflows/test.yml` runs the test suite across an OS matrix (`ubuntu-latest`, `macos-latest`, `windows-latest`) and a language-version matrix (Python 3.10/3.11/3.12 or Go 1.21/1.22). Triggers on `push` to `main` and `pull_request` to `main`. Steps: `npm ci`/`uv sync`, optional nested-skill installs, `npm run lint` (eslint), conditional `npm run typecheck`, `npm test`/`pytest`/`go test`. Actions SHA-pinned with tag annotations preserved as comments. Built-in `actions/setup-node` cache keyed on `npm`. `concurrency` group with `cancel-in-progress: true` supersedes queued runs on rapid push. Per-job `timeout-minutes: 15` and minimum-`contents: read` permissions. No linters, no type checkers, no manifest validators in this workflow. Appropriate when the test suite is cohesive and self-validating.

### Format + lint + test wrapper

`make ci` wrapping `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test`. Runs on `push: branches: [main]` and `pull_request` with `paths-ignore: ['*.md']`. Matrix is OS only (`ubuntu-latest`, `macos-latest`, `ubuntu-24.04-arm`); no MSRV check despite `Cargo.toml` declaring `rust-version`. Actions tag-pinned. Rust target/registry caching via `Swatinem/rust-cache@v2`.

### Per-OS workflow files (deliberate split)

Three CI workflow files (`ci-ubuntu.yml`, `ci-macos.yml`, `ci-windows.yml`) instead of one with `matrix.os`. Per-OS steps diverge significantly enough that splitting trades DRY for readability — Linux installs `libasound2-dev`, Windows uses `pwsh` for fmt check, macOS builds platform-specific sidecar binaries. Plus auxiliary workflows for signing smoke tests (`notifier-signing-smoke.yml`) and release builds. Appropriate when per-OS divergence is irreducible; the cost is duplicated boilerplate when shared steps must change in three places.

### Single-workflow with multiple jobs in a DAG

`.github/workflows/ci.yml` containing all validation jobs in a `needs:` dependency graph. A seed job (e.g., secrets-scan) gates all downstream work. Jobs cover: JSON parseability, hooks.json schema validation, plugin manifest schema, shell script syntax + executability + shellcheck lint, skill frontmatter, agent frontmatter, knowledge-base presence, test-runner, and a final summary job that fails if any upstream did. One file, full visibility, fragile against adding new components (new hooks require editing the script allowlist in CI too).

### Multi-workflow split by trigger and concern

Multiple workflow files split by trigger: `ci.yml` for PR validation, `release.yml` for tag pushes, `pr-review.yml` for ready-for-review automation, `weekly-update.yml`/`weekly-api-update.yml`/`monthly-research.yml` for cron shepherds, `benchmark-*.yml` for performance work. `concurrency` block on `ci.yml` with `cancel-in-progress: true` to prevent stale re-runs. Eight or more workflows total in an ambitious project.

### Single workflow, sparse coverage

CI runs a few jobs: manifest lint, shell-lint, a partial test job that only exercises a subset of test files. Most of the test suite is not run by CI (e.g., 70+ JS test files visible in tree but only one subdirectory is actually executed). Massive coverage gap — typically the result of evolution outpacing CI updates.

### Test workflow with pinned actions, no caching

`.github/workflows/ci.yml` triggered on push and PR to `main`. Single ubuntu-latest job, single Python version. Inline `pip install pytest pytest-cov`. Runs `python -m pytest tests -v --cov=skills --cov-report=term-missing`. Actions SHA-pinned with tag comments. No caching; no lint; no manifest validation. Coverage is `term-missing` only — no codecov upload, no trend tracking. Minimal CI scope reflects "runtime is tested, manifests are trusted" posture.

### Split test + lint workflows with `|| true` permissive runs

Two workflows — `ci.yml` (test + dashboard typecheck) and `lint.yml` (ruff + eslint). Both trigger on push and PR to multiple branches. Test job pip-installs deps with `|| true` and runs pytest with `|| true` — failures don't fail CI. CI tolerates environment-caused pip failures without distinguishing them from genuine regressions; effectively a smoke check. Action pinning by tag (not SHA). Built-in `setup-node` cache for npm; no Python cache.

### Minimal cloud CI

A single workflow that does one job — typically a webhook-style notify (e.g., `notify-marketplace.yml` fires `repository_dispatch` to a sibling marketplace repo when `plugin.json` changes). Linting, type-checking, and test execution live in pre-push hooks and release scripts, not in cloud CI. Constrains contributors who fork the repo without adopting the local hook setup — they get no quality gates at all. Appropriate when the maintainer trusts the local pipeline more than cloud CI and wants minimal cloud surface.

### Discipline-checking CI on push and PR

Workflows on `push: main` + `pull_request: main` run a custom rubric (e.g., `meta-review.yml` running `meta_review.py`, `verify_triggers.py`, `verify-sync-to-active.sh`). Targets methodology invariants — version-string parity, skill-count, frontmatter, registration-list drift — rather than the marketplace schema. Constrains the meta-rubric to be the gating contract; external `$schema` validation is not wired in even when declared. Appropriate when the plugin's invariants are richer than the upstream schema.

### Sprawling autonomous workflows

The `.github/workflows/` directory hosts 30+ workflows including cron-driven autonomous loops (`daily-revenue-loop.yml`, `instagram-autopilot.yml`, `gtm-autonomous-loop.yml`, `ralph-loop.yml`, `self-healing-auto-fix.yml`). Orthogonal to plugin distribution but co-resident in the same repo. Constrains the repo's surface area dramatically; mixes plugin-distribution workflows with non-code automation. Appropriate only when the repo intentionally serves both as a plugin source and as an operations hub.

### Action-pinning conventions

Sampled choices: SHA-pinned with version comment (`peter-evans/repository-dispatch@<sha> # v4.0.1`), tag-pinned (`actions/checkout@v4`, `actions/setup-node@v6`). Even within one repo, conventions can be inconsistent (SHA on one action, tag on another). Constrains the security posture — SHA pinning resists hostile-tag substitution; tag pinning trusts the action publisher.

### CI-trigger-as-signal-of-traction

Documented case: CI was added specifically because the repo got "3 GitHub stars within 24h of publishing." Adoption signal flipped the cost/benefit on adding CI. Captures the pattern: small projects defer CI until a traction signal appears.

## Marketplace validation

Whether anything programmatically checks `marketplace.json`, `plugin.json`, `hooks.json`, and frontmatter for shape and consistency.

### No validation

No CI step validates manifest shape, version agreement, or frontmatter conformance. A bad commit corrupting these files would not fail CI — it would fail at install time on the user's machine. Type checking via pyright or similar runs only in the developer's editor with no enforcement gate. Validation relies on Claude Code's load-time checks plus manual testing. Manifest regressions surface only at install time on a real Claude Code session. Most low-investment plugins land here.

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

### Local-only validation, no cloud gate

Manifest validation lives entirely in pre-push hooks and the release script. PR branches run only feature-branch gates (lint + JSON parse). Constrains validation to the maintainer's discipline; contributor PRs ship with weaker checks. Appropriate when the maintainer is the only release author.

### Homegrown validators not wired to CI

Repo-local scripts (`scripts/validate-plugin.sh`, `scripts/validate-wave-scope.sh`, `scripts/validate-config.mjs`) plus a frontmatter validator with its own test suite (`tests/lib/agent-frontmatter.test.mjs`) exist but are not invoked by CI workflows. Library-internal use only. "Defense in depth but no enforcement at the marketplace manifest layer."

### Hardcoded script allowlists in CI

CI's `validate-shell-scripts` job and the ShellCheck step list specific scripts by path (`hooks/<name>.sh`, `tests/run-tests.sh`). Adding a new hook requires editing `ci.yml` too. Fragile; surfaces as CI no-ops for new files.

### Schema validators that lag the runtime

The hooks-event-name allowlist in CI predates the runtime's acceptance of new events (PostToolUseFailure, SubagentStop, PreCompact, PostCompact). A patch release of the plugin added these to the allowlist after the runtime started accepting them — validator-as-second-source-of-truth lagging the actual runtime.

### Knowledge-base presence checks with subtle bugs

`validate-knowledge-base` job checks for directory presence and counts files but never compares the count to a minimum, so an empty knowledge directory still passes the existence check. Latent gap that looks like coverage.

### Plugin diagnostics surface

A `commands/<plugin>/doctor.md` slash command (or skill of the same name) walks installation diagnostics: node-on-PATH, plugin root resolved, MCP launcher generation, dependencies installed, server connectivity, project init state. Designed for the user to run after install to surface configuration problems. Appropriate when the plugin has multi-step bootstrap that can fail at any of several points. Distinct from CI-time validation: this runs at user invocation against a real install, not at PR time.

### No diagnostic surface

Plugin ships no diagnostic command. Users debug install failures by reading hook stderr or running scripts manually. Appropriate when the plugin's surface is small enough that failure modes are obvious.

## Release automation

Whether tag pushes or version bumps trigger an automated release pipeline.

### Manual (no `release.yml`)

No release workflow. Releases are bare git tags on `main` (sometimes with a hand-created GitHub Release). Tag-name discipline is human: name the bump commit, push the tag. CHANGELOG.md is the only narrative, but no automation consumes it. Appropriate for low-volume releases and small audiences; the cost is no automated tag-vs-version sanity gate.

### Manual GitHub UI release creation

Releases cut by hand: bump `plugin.json` → commit → annotate tag → push main + tag → write release notes in GitHub UI (sometimes). No automation, no tag-sanity gates. Drift symptoms: tags without published Releases, missing tag numbers, mismatched `plugin.json.version` and tag name. The release-notes UX is a manual step that has fallen behind the tag cadence in practice. Releases produced via GitHub UI or `gh release create`. CHANGELOG.md may follow Keep a Changelog format with rich per-release sections.

### Tag-driven version-bump script with no GitHub Actions

A project-local script (`scripts/bump-version.mjs`) bumps versions across `plugin.json` and `marketplace.json` in one operation, but tag creation and release publishing remain manual. The script enforces version-file sync but not tag-vs-manifest alignment. Failure mode: contributor commits feature work after a tag without bumping, leaving `plugin.json` temporarily behind reality.

### Tag-triggered cross-build with CHANGELOG awk extraction

`.github/workflows/release.yml` triggers on `push: tags: ['v*']`, cross-builds platform binaries (Go), and attaches them to the GitHub Release. Release notes body is extracted from `CHANGELOG.md` by an awk script that grabs the section between `## [VERSION]` and the next `## [` heading. Workflow first checks whether an external tool already created the release — if so, only refreshes binaries via `gh release upload --clobber`; otherwise creates the release itself as a safety-net. Inverts the usual "workflow IS the release mechanism" pattern.

### Tag-triggered cross-compile + asset upload

`.github/workflows/release.yml` triggered by `push: tags: ['v*']`. Cross-compiles the binary to multiple targets (e.g., `aarch64-apple-darwin`, `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`), installs cross toolchains for non-native targets, renames outputs to platform-tagged asset names (`<plugin>-macos-arm64`, `<plugin>-linux-x86_64`, `<plugin>-linux-arm64`), and uploads via `softprops/action-gh-release@v1` with `generate_release_notes: true`. No tag-sanity gates (no verify-tag-on-main, no verify-tag-matches-build-manifest-version, no tag-format regex). Action pinned to a major tag rather than a SHA.

### Tag-triggered binary build + GH Release with signing

Workflow triggers on `push: tags: ['v*']` and runs a multi-job pipeline: per-platform binary build (CGO_ENABLED=1 with stripped/trimmed flags), platform-specific signing/notarization (Apple Developer ID for macOS app bundle), checksum generation, GitHub Release creation via `softprops/action-gh-release@v1` with auto-generated notes, and a post-publish smoke test that re-downloads the released asset and runs `<binary> version` on each OS. No tag-format regex gate, no tag-equals-plugin-version verification. Appropriate when the release artifact is a compiled binary with platform variants; the cost is platform-specific secrets management (Apple cert P12, password, team ID) and post-release smoke testing being a verification rather than a gate.

### Tag-triggered with sanity gates and `--generate-notes`

Workflow on `push: tags: ['v*']`. Two sanity gates: (a) `git merge-base --is-ancestor HEAD origin/main` to assert the tag is on main; (b) tag value (`${GITHUB_REF#refs/tags/v}`) must equal `package.json.version`. Failure aborts publish with targeted `::error::` messages. Then runs `npm publish --provenance` (sigstore via `id-token: write` permission) and `gh release create "$TAG_NAME" --generate-notes` (release notes from PR titles since last tag, NOT from CHANGELOG.md). Gates do not check that tag matches `plugin.json` or `marketplace.json` versions — drift between npm and plugin metadata still possible. `fetch-depth: 0` on checkout required for the ancestry gate.

### Local-script release pipeline

A maintainer-machine-only Python script (`scripts/publish.py`) orchestrates 15 mandatory gates: tool availability, pre-push hook, clean tree, lint, type-check, py_compile, tests, schema validate, atomic version bump, schema re-validate, CHANGELOG regen via `git-cliff`, release commit, annotated tag, push (gated by ancestry check), `gh release create` with notes from CHANGELOG. Process-ancestry pre-push gate (walks `ps -p <pid> -o args=` rejecting any push not driven by the script) prevents the gate from being bypassed. Constrains the release to the maintainer's working machine; no cloud audit trail; depends on local toolchain (uvx, git-cliff, gh CLI, uv) being correctly installed. Appropriate when the maintainer privileges total local control over cloud reproducibility.

### Path-filtered cloud publish workflow

A workflow on `push: main` with `paths` filter targeting only `package.json`/`package-lock.json`/`server.json`/the workflow file. Tag creation moves *inside* the job, conditional on a decision script's output (`scripts/publish-decision.js`). Multi-trigger: `push: main` + `release: published` + `workflow_dispatch`. Constrains a maintainer to bumping `package.json` deliberately to fire the workflow; non-bump commits don't ship. Appropriate when the publish discipline is "bump = release" and main has high commit cadence on non-shipping changes.

### Manual release commit with bump script

No release workflow; the contributor runs `scripts/bump-version.sh <new>` (which patches version across many files), commits, manually `git tag`, and `git push origin main && git push origin <tag>`. The script's tail prints the next-step instructions. GitHub Releases (when present) are created via the GitHub UI, manually copy-pasting from CHANGELOG. Many tags accumulate with no automation to guarantee tag == plugin.json version — silent failure mode.

### Silent-no-op regression detector

A guard step in publish workflows that fails CI when the version is already on the registry *and* the shipped-files allow-list has commits since the last `v*` tag. Encodes a specific past regression class ("version published, content changed but not shipped"). Constrains every commit to either bump version or not touch shipped files. Appropriate as a defense-in-depth step where a known regression class has burned the maintainer.

### Post-publish runtime smoke

After `npm publish`, a workflow step pulls the freshly-published tarball *back from the registry* (`prove-packaged-runtime.js --package-spec "<name>@<version>" --install-attempts 12 --install-delay-ms 10000`) and smoke-tests it. Retries handle CDN propagation. Closed-loop: "publish verified only when the thing downstream users would pull actually works." Constrains the publish workflow's wall-clock; provides positive evidence of consumer-side install success.

### Cross-repo notify on plugin.json change

Workflow fires `repository_dispatch` (`plugin-updated` event) on a sibling marketplace repo when `.claude-plugin/plugin.json` changes. PAT-gated, one-way. Keeps marketplace state in sync without bidirectional write access. Constrains the relationship to a single secret (PAT) and a custom event-name convention. Appropriate when source and aggregator are decoupled and the maintainer wants a lightweight sync trigger.

### No releases at all

No tags, no GitHub Releases on the plugin repo. "Release" means whatever `main` currently points at. Often paired with no CI and a dangling external dependency (e.g., an update-check pipeline that polls a sister repo's releases endpoint that itself returns 404). The plugin ships with the release infrastructure code written but the supporting endpoints unbuilt.

## Documentation surface

What user-facing and developer-facing docs the repo carries, and how they're organized.

### Stub README only

Repo `README.md` is small (~few hundred bytes) — headings and a "currently in active development" caution, no install/usage instructions. No per-plugin README. No CHANGELOG. No `architecture.md`. No `CLAUDE.md`. Substantive documentation, when it exists, lives in an internal `worklog/` directory with numerically-keyed specs/decisions/tasks. Appropriate for early-stage repos; the cost is a new consumer must infer install from manifests and SKILL.md files.

### Single comprehensive README serves all

`README.md` at repo root is the only documentation. Covers install, usage, format reference, and (sometimes) license/privacy. No `CHANGELOG.md`, no `ARCHITECTURE.md`, no `CLAUDE.md`. Architecture content embedded inline rather than separated. Constrains a reader's ability to navigate to one specific concern. Appropriate for thin plugins where doc volume doesn't justify multi-file split.

### Substantial root README + CHANGELOG + community files + badges

Repo `README.md` is ~15-25 KB covering features, install paths (often three: bootstrap curl-pipe, manual `/plugin` slash commands, classic marketplace add), supported platforms, configuration UX, troubleshooting. Opens with a hook framing or a value-prop scare example. Includes badges (CI, license, version, deps-zero). `CHANGELOG.md` follows Keep-a-Changelog format with `### Added/Fixed/Changed` under `## [x.y.z] - YYYY-MM-DD` headers, OR a custom format with theme statements. `CONTRIBUTING.md`, `LICENSE`, optional `.github/ISSUE_TEMPLATE/`. Architecture docs at `docs/ARCHITECTURE.md` (off-root, by docs-directory convention) or as a PNG diagram only.

### Three-document core (README + ARCHITECTURE + CLAUDE) plus CHANGELOG

`README.md` (user-facing pitch + install + commands), `ARCHITECTURE.md` (multi-layer diagram, hooks/skills tables, design flows), `CLAUDE.md` (project instructions for Claude operating *on* this repo, separate from any shipped wizard doc the plugin may carry), and `CHANGELOG.md` in Keep-a-Changelog format. Aligns with the system-docs convention. Sometimes paired with localized mirrors (`README_ja.md`, `LICENSE.ja.md`) when bilingual.

### README + ARCHITECTURE + CLAUDE-as-pointer

Substantial `README.md` (~16 KB) plus a sizable `ARCHITECTURE.md` at repo root with mermaid diagrams and design-principle prose. `CLAUDE.md` exists but contains only a pointer (`@AGENTS.md`-style include) — `AGENTS.md` is the canonical agent-rules file. Convention inversion: Claude Code loads `CLAUDE.md`, but the actual content lives elsewhere. Works because of the include directive. Constrains contributors to know the indirection or risk editing the wrong file.

### CLAUDE.md without ARCHITECTURE.md, ADRs as decision capture

CLAUDE.md carries an "Architecture" section with directory tree + role annotations, plus 15+ ADRs under `docs/adr/` in Nygard format (Status/Date/Context/Decision/Consequences). CHANGELOG entries cross-reference specific ADRs. Decision capture is strong; structural overview is split between CLAUDE.md and the ADR tree, requiring readers to reconcile both.

### Multi-doc architecture (no separate ARCHITECTURE.md)

Substantial root README plus per-skill SKILL.md plus contributing/changelog/CI docs (`docs/CI.md`, `docs/CONTENT-PLAN.md`). No top-level `ARCHITECTURE.md`. The architectural narrative lives in README sections (e.g., "Call Graph", "Skill Contracts", "How It Works"). Constrains future maintainers to reconstruct the architecture from prose; works while the README author and the maintainer are the same person. Appropriate when README discipline is high and the architecture is methodology-shaped rather than code-shaped.

### Heavy doc surface with meta-project artifacts

20+ top-level markdown files: README, ARCHITECTURE, CLAUDE, CHANGELOG plus competitor audits, research notes, roadmap, score-trend logs, audit-progress logs. README stays focused on the user; sprawl is absorbed into siblings. Can include "two CLAUDE-like files with different audiences" — `CLAUDE.md` for contributors, `<PLUGIN>_WIZARD.md` shipped as the wizard artifact consumers `cat` or WebFetch during setup.

### Full kitchen-sink docs

`README.md` plus a large `CHANGELOG.md` (Keep-a-Changelog format, dev-trail entries during pre-release cycles) plus `docs/<architecture>.md` and `docs/migration-*.md` plus `docs/USER-GUIDE.md` (~60 KB) plus `docs/prd/*.md` for feature specs plus a long `CONTRIBUTING.md` (~22 KB) plus `SECURITY.md` plus `CODE_OF_CONDUCT.md` plus issue and PR templates. Documentation-as-code practice extending to PRDs. `CLAUDE.md` is operational procedures (agent-authoring pitfalls, structure overview, destructive-command-guard documentation), not just a pointer. Drift hazard at this scale: stale references in `SECURITY.md` to pre-refactor file names linger across migrations.

### Internal developer log as primary architecture doc

The repo carries a structured internal log directory (`worklog/spec/`, `worklog/decision/`, `worklog/archive/task/`) with numerically-keyed specs, ADRs, and archived tasks. Each decision uses TOML-fence frontmatter with `id`, `title`, `relates_to`, `supersedes` keys; tasks move through spec → task → archived-task lifecycle. Cross-linking is explicit. Appropriate as a long-form design practice that embeds decision history inside the repo rather than relying on PR/issue history; the cost is the docs are inward-facing and a new user without the convention has to map it.

### Shipped planning corpus visible in public repo

`.planning/` tree with MILESTONES.md, ROADMAP.md, STATE.md, per-version phase directories each holding CONTEXT/PLAN/SUMMARY/VERIFICATION/RESEARCH files. 260+ planning files visible in the public repo. Some projects keep this private; others publish their entire milestone-planning process. Candidate "development-process transparency" surface — risk: planning docs can carry stale references (e.g., legacy plugin name paths after a rebrand).

### CHANGELOG with "Why" and "Migration" subsections

Beyond Keep-a-Changelog's prescription, each release entry adds a `Why` section (decision rationale, sometimes citing external docs) and a `Migration` checklist for consumers. CHANGELOG functions as design-decision log, not just release notes. Significantly more substantive than typical CHANGELOGs.

### CHANGELOG depth as documentation

CHANGELOG entries carry not just `Added`/`Changed`/`Fixed` but `Ops` (per-release manual checklists), `Context`, `Rationale`, `Lessons learned (meta-review gap)`, `Deliberately not done (deferred)`. The latter two close a feedback loop between CI output and rubric improvements; the deferred section captures negative-space decisions as first-class entries. Constrains release discipline to thoughtful authoring. Appropriate when CHANGELOG is treated as the project's reasoning log rather than a feature manifest.

### Keep-a-Changelog with root-cause prose

`CHANGELOG.md` declares Keep-a-Changelog format at top; every release block has Added/Changed/Fixed sections with prose explaining root causes (e.g. why a hook was rewritten, what bug a new fallback addresses). Unusually detailed for a plugin repo. Appropriate when the project has substantial cross-release behavior changes that demand explanation.

### CHANGELOG as in-product upgrade source

`CHANGELOG.md` doubles as the source the in-product update skill consumes — fetched via WebFetch and diffed against the installed version stamp embedded in a shipped doc. Not just a release-notes artifact; an active runtime input for the plugin's self-update flow.

### Multi-language READMEs

Paired English-and-other-language versions (`README.md` + `README.zh-CN.md`, `README.md` + `README.ru.md`) with no sync-enforcement (or, in some cases, version-sync script enforcing parity). Per-skill `## Trigger phrases` lists in both languages; `check-skills.sh` regex tables include both-language matches. Constrains every doc-touch to update both READMEs. Appropriate when the user population is genuinely multi-lingual and each language carries equal trigger weight; cost is content-drift between locales when sync is unenforced.

### Documentation sprawl

Many root-level docs covering go-to-market content (`LAUNCH.md`, `LAUNCH_NOW.md`, `LAUNCH_POSTS.md`, `DISTRIBUTION_RUNBOOK.md`, `FIRST_CUSTOMER_BATTLE_PLAN.md`, `gate-program.md`, `primer.md`) alongside developer docs. A new contributor cannot tell from `ls` which doc to read first. Constrains discoverability; works when the project intentionally mixes business and engineering surfaces.

### Promotion drafts in-repo

`docs/promotion/drafts/` carries marketing copy for HN, devto, habr, reddit, twitter. The custom rubric scans these for stale version references — promo content participates in version-drift validation. Constrains every release to update promo too.

### Per-plugin README in `.claude-plugin/`

A scoped README (`.claude-plugin/README.md`) inside the plugin manifest directory, distinct from the root README and tailored to the Claude-Desktop install surface. Constrains the maintainer to two README surfaces with overlapping but non-identical content. Appropriate when the plugin is one of several integration shims and the root README is multi-host marketing material.

### SKILL.md as primary doc for the skill component

`skills/<name>/SKILL.md` (10KB+ in observed cases) is the deep operational doc; root README is install-focused. Appropriate when the plugin is essentially a skill — most of the substantive content describes what the skill does and how to invoke it. Description field has a hard 1024-char limit and is read by many agent hosts simultaneously when the skill is multi-host.

### README references to docs that don't exist

README links to `docs/ARCHITECTURE.md`, `docs/<plugin>-OVERVIEW.md`, etc. that aren't present in the repo's `docs/` listing. Either aspirational ("we plan to write these"), removed without README update, or in a nested location not surfaced by listing. Reader clicking links 404s. Drift symptom — README and disk state diverged.

### Plugin-bridge cross-agent symlinker

`tools/plugin-bridge/` ships an auxiliary bash toolkit (install + launchd plist + update + uninstall + README) that maintains a symlink from another agent's skills directory (e.g. `~/.codex/skills/<name>`) to `~/.claude/plugins/cache/<marketplace>/<plugin>/<latest-version>/skills/<name>`. Auto-relinks on `claude plugin update` via launchd `WatchPaths`. Linux equivalent uses `systemd --user` path units. Converts Claude Code's versioned plugin cache into a live source for non-Claude agents. Appropriate when the skill targets multiple agent hosts and the maintainer wants a single source of truth for the skill's content.

## License declaration

How the LICENSE is declared and whether files agree across `LICENSE`, `plugin.json`, README, and the GitHub API.

### LICENSE file present + SPDX in manifests (single source agreement)

A full LICENSE file at repo root (e.g., 10.5 KB Apache-2.0 text, MIT text) plus `license` field in `plugin.json` and `package.json` carrying the SPDX identifier. README references the same. GitHub auto-detects and badges the license. All four agree. Standard hygiene.

### LICENSE declared in manifests, no LICENSE file

`license: "MIT"` (or similar) in `package.json` and `plugin.json` but no `LICENSE` file at repo root. GitHub license API returns 404; no SPDX detection. npm publishes the package without a LICENSE file in the tarball unless added to `package.json.files`. Real defect — propagates the license claim via metadata only.

### License only in README prose

License claim lives only in README prose without an SPDX-identifiable `LICENSE` file. GitHub UI reports the repo as unlicensed regardless of the README claim because no SPDX-identifiable file exists.

### Three-way disagreement

README asserts one thing ("Plugin wrapper: MIT. Extraction engine: proprietary."), `plugin.json` declares another (`"license": "UNLICENSED"`), no `LICENSE` file commits anything, GitHub API returns null. Author intent is unrecoverable from static inspection. GitHub UI and tooling report the repo as unlicensed regardless of the README claim.

### AGPL-3.0 with embedded badge

LICENSE present, SPDX `AGPL-3.0-only`, README carries the AGPL badge alongside CI/version badges.

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

## Cross-ecosystem distribution

When the same project ships through multiple delivery surfaces or to multiple agent ecosystems.

### Single-ecosystem (Claude only)

`.claude-plugin/marketplace.json` is the only manifest. No Codex, no Cursor, no other agent-host configuration in the tree. Plugin manifest, hook scripts, components scoped to Claude Code's plugin protocol. No siblings.

### Plugin + npm CLI + curl-bash with collision detection

Same content shipped via three install paths: Claude plugin (enabled inside Claude Code), npm CLI (installable via `npx`, `npm install -g`, or Homebrew tap), and `curl | bash` script. The CLI's init code explicitly probes for the plugin install paths and blocks with a typed error when both coexist; a session-start hook also nudges on dual-install. Six documented install paths (npx, curl-bash, Homebrew tap, gh extension, `npx github:`, global npm) — heavy investment in distribution surface area. The engineering cost is documented in CHANGELOG with a referenced PR.

### Plugin + monolithic repo with rebrand legacy

Plugin shipped under a current name, with extensive backward-compatibility for a legacy name across every runtime surface — env var pairs (`<NEW>_API_KEY`/`<OLD>_API_KEY`, `<NEW>_WORKER_PORT`/`<OLD>_WORKER_PORT`, etc.), data dirs (`~/.<new>/` preferred, `~/.<old>/` honored if new dir doesn't exist), config files (`<new>.config.json` preferred, `<old>.config.json` honored). Identity-transition discipline far thicker than typical rebrand-compat — every observable surface honors both spellings. Intermediate artifacts may still carry the old name (e.g., a `runtime-deps.json` with `name: "@<old>/runtime-deps"` at version 5.7.0 inside a v0.1.0 release of the new identity).

### Dual-harness (Claude Code + Gemini CLI)

Single source tree carries `.claude-plugin/plugin.json` AND `gemini-extension.json`; commands are `*.toml + *.md` pairs designed to be harness-agnostic; hook scripts in `hooks/scripts/` (not `.claude-plugin/hooks/`) so both harnesses can wire them via their respective registration files (`.claude-plugin/hooks.json` vs `hooks/gemini-hooks.json`). Hook scripts guard on `${CLAUDE_PLUGIN_ROOT:-}` presence to skip Claude-only logic when running under Gemini. Three-file version sync rule (`plugin.json`, `marketplace.json`, `gemini-extension.json`) lives in prose. Deliberate decision recorded in CHANGELOG that the plugin's distribution model differs per harness (e.g., bundled MCP for Claude, install-dir model for Gemini).

### Triple-ecosystem (Claude + Codex + Cursor)

Single repo ships `.claude-plugin/marketplace.json` for Claude Code, `.codex-plugin/plugin.json` for Codex, and `.cursor/rules/*.mdc` for Cursor IDE — three concurrent manifest systems. Bootstrap scripts (`scripts/codex-install.sh`, `scripts/cursor-install.sh`) adapt the same skills/agents/hooks to each host. A shared `platform.mjs` exposes `SO_PLATFORM`, `SO_IS_WINDOWS`, `SO_IS_WSL` so library code can branch without duplicating logic. Cascading runtime resolution chain (`${CLAUDE_PLUGIN_ROOT:-${CODEX_PLUGIN_ROOT:-$(git rev-parse --show-toplevel)}}`) supports invocation from any host. Constrains every install-side change to be tested across three ecosystems and pushes the plugin into a "lowest common denominator" portion of each host's API surface.

### Multi-runtime skill mirrors

Skills authored once in `skills/`, then mirrored to sibling directories for other runtimes (`skills-codex/`, `codex/.codex/skills/`, `opencode/skills/`) by build scripts (`scripts/build-opencode.js`, `scripts/sync-skill-mirrors.sh`). A dedicated CI workflow (`opencode-compat.yml`) fails if mirrors drift. Differs from dual-harness distribution above by mirroring derivative copies rather than running the same files through divergent registration manifests.

### Multi-adapter single-package shape

One npm package ships internal adapters for multiple host ecosystems (`adapters/{amp,chatgpt,claude,codex,forge,gemini,mcp,opencode}/`), each with its own integration descriptor (`config.toml`, `opencode.json`, `function-declarations.json`, `openapi.yaml`). A parallel `plugins/{amp-skill,claude-codex-bridge,claude-skill,codex-profile,cursor-marketplace,gemini-extension,opencode-profile}/` tree mirrors that at the plugin-format layer. Constrains every release to update every descriptor; the version-sync script makes this tractable. Appropriate when the codebase is genuinely platform-neutral and the author wants one bug-fix to land everywhere.

### Multi-registry publishing

Same release ships to npm, GitHub Releases (`.mcpb` bundle), and the MCP Registry (`server.json`-driven). Each surface has its own publish workflow (`publish-npm.yml`, `publish-claude-plugin.yml`, `mcp-registry-publish.yml`, `publish-codex-plugin.yml`, `publish-tessl.yml`). Constrains the release pipeline to coordinate N parallel workflows; an artifact failure in one needs an explicit re-run rather than blocking the others. Appropriate when each registry serves a distinct discovery population.

### MCP Registry presence (`server.json`)

A separate `server.json` at repo root (distinct from `plugin.json` and `marketplace.json`) carries `$schema` pinned to `https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json`. Drives `mcp-registry-publish.yml`. The plugin reaches consumers through three discovery surfaces: npm registry, GitHub Release `.mcpb`, and MCP Registry. Constrains every release to update three registries; exposes the plugin to populations that don't search the Claude Code marketplace. Appropriate when the underlying server is genuinely MCP-shaped (not Claude-Code-specific). Most samples don't touch the MCP Registry; the marketplace and a single git/npm source are sufficient.

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

### Process-ancestry-verified pre-push gate

`scripts/pre-push` walks the process tree via `ps -p <pid> -o args=` to confirm `scripts/publish.py` is an ancestor process, rejecting pushes to main otherwise. Rationale: env-var/marker-file schemes are "trivially spoofable"; an ancestry check enforces release-discipline without trusting any mutable signal. Constrains all main pushes to flow through the release script. Appropriate when release discipline is non-negotiable and the maintainer accepts the rigidity.

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

## Plugin-conflict and dependency declaration

How the plugin tells the user it cannot coexist with another plugin, and whether it declares dependence on others.

### README prose only

Plugin requires the user to manually `/plugin disable <other-plugin>@<other-marketplace>` before installing. The conflict is declared only in README narrative; plugin metadata has no `incompatibleWith` or equivalent field. Installing both leaves the user with conflicting servers (e.g., two LSP backends) silently. Procedural-only enforcement; structural enforcement absent.

### No declared cross-plugin dependencies

`plugin.json` carries no `dependencies` field. Single-plugin marketplace, self-contained payload. Appropriate when the plugin doesn't compose with sibling marketplace plugins. Cross-plugin coordination doesn't arise. Whether the field is unsupported, unused, or simply unneeded is not determinable from the samples alone — none observed.

## API-cost transparency

Whether the plugin discloses runtime cost to users.

### Explicit cost-model section in README

README's "API Cost Model" section quantifies the agent-hook cost at ~$0.15-0.30 per session with a per-hook breakdown table, and provides an explicit opt-out (`agent_hooks: false` in `userConfig`). Rare for plugins to publish cost transparency; novel surface.

## Output styles

Whether the plugin ships shared report formats agents and skills reference.

### Shared markdown templates under `output-styles/`

3+ markdown files at `output-styles/` (e.g., `session-report.md`, `finding-report.md`, `wave-summary.md`) define the prescribed output shape for skill or agent emissions. Agents and skills reference these by path, ensuring report consistency across the plugin's surface. Layer not always documented in plugin docs but legitimately registered via convention discovery. Constrains the plugin to maintain template-to-consumer coupling — a template rename requires updating every reference.

### No output styles

Plugin ships no `output-styles/` directory. Skills and agents emit free-form output, with consistency enforced (or not) at the prose level only.

## Cross-role tools

Tools that fill multiple roles in the corpus and are named under each role's section above.

### Python (stdlib + pip)

Python 3.10+ appears as: the runtime for hook scripts (stdlib only when zero-dep policy in force; pip + third-party when not), the install-script language (`install.py`, `ensure-deps.py`, `auto_install.py`), the mock HTTP server in install E2E tests (`mock_server.py`), the test framework (`unittest` stdlib, pytest, stdlib-rubric scripts), CI inline validation (heredoc Python in ci.yml steps), YAML/markdown parsing in shell scripts (inline `python3 -c "import yaml; ..."`), and helper-script runtime (session_state.py, metrics-query.py, yaml-parser.py invoked via `python3` on system PATH). Different roles use different sub-uses (stdlib only vs pip + third-party).

### Node + npm + npx

Fills runtime (worker daemon, MCP server, npm CLI, hook handlers as `.mjs`), dependency installation (`npm install --prefix`, `npx --yes --package`), bin-wrapped CLI distribution (npm bin entry point), test stack (`node --test` test runner, vitest, custom node-test runners), and release automation (`npm publish --provenance`).

### bash

Fills bin-wrapped CLI distribution (thin exec-wrappers, cross-platform shims), hook scripts (file-guard, post-write-check, session-start), install scripts (install-deps.sh, install.sh), test stack (run-tests.sh hierarchical bash test suites, bats), and failure-signaling envelope (the `set -uo pipefail` + `trap ERR` pattern). Hot-path POSIX `/bin/sh` discipline distinguishes it from one-shot bash use.

### SQLite

Fills state persistence (`metrics.db` for behavioral metrics) and is consumed by both the worker daemon and the MCP server in a peer-process architecture (per-call DB resolution, atomic writes).

### `jq`

Fills hook output construction (building `hookSpecificOutput` JSON, escaping context with `jq -Rs .`), CI manifest validation (`jq empty` parseability and `jq` queries for name-equality), and bin-wrapped CLI input synthesis (reconstructing the PostToolUse envelope via `jq -n`).

### GitHub Actions cron

Fills external-change watcher (weekly/monthly cron workflows polling release pages, API changelogs, community signals) and CI workflow shape (PR validation, release publish on tag, autonomous loops, cross-repo notify).

### `${CLAUDE_PLUGIN_ROOT}` env var

Used by hook wrappers to locate the plugin's bin scripts; used inside `config/config.json` for resource paths (expanded by the plugin's own runtime, not by the host); used in `hooks/hooks.json` to locate hook scripts. The same env var fills "find my own files" across three roles and underpins the runtime resolution variable chain in state persistence.

### `plugin.json.version`

The same string drives user-facing version display, the install-skip predicate (matched against a stamp file), the lazy-download URL for the matching binary asset, and (often, fragilely) banner version literals embedded in hooks. Triple-or-more-duty as both data and control signal across version coordination, install change detection, and session context loading.

### Bash `case` + Python validator pattern

Inline `case "$input" in <pattern>) python validator ;; esac` in hooks.json fast-paths 99% of unrelated calls without paying Python startup cost. The here-string `<<< "$input"` safely passes JSON with embedded quotes. Surfaces under PreToolUse hook (auto-allow scripts) and tool-use enforcement (gating).

### Git as state substrate

Git fills branching and tag placement at the release layer, `<git-common-dir>/` as a state-storage root for mission state (state persistence), worktree creation as the per-role isolation mechanism, and the underlying mechanic of marketplace install (clone-or-update of a remote repo). Each role uses a different facet.

### Docker (largely absent)

Docker does not surface in this set of bins as a runtime, distribution, or test-stack tool. Worth flagging the absence — many plugin ecosystems lean on Docker; this corpus does not.
