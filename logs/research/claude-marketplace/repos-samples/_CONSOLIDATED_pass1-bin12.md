# Sample

Pass-1 Phase-1a partial for bin 12. Functional decomposition of `anthropics--knowledge-work-plugins`, `anthropics--life-sciences`, and `brunoborges--ghx`, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How the marketplace exposes its entries — where the `marketplace.json` lives, whether it appears once or multiple times, and what shape its top-level metadata takes.

### Single root manifest

A single `.claude-plugin/marketplace.json` at repo root is the standard layout. The file enumerates every plugin the marketplace surfaces; consumers add the marketplace by repo identifier and read this one file. Suits primary-owned marketplaces and small single-plugin sources alike.

### Single root manifest plus nested per-plugin manifest

A second self-contained `.claude-plugin/marketplace.json` lives inside one of the plugin directories, declaring that single plugin as a standalone marketplace with `metadata.pluginRoot: "."`. The same plugin is reachable two ways — as an entry in the aggregator's root manifest and as the only entry of its own nested marketplace. Suits a host repo that vendors a partner's plugin while letting the partner upstream the same directory to their own repo as a self-contained marketplace.

### Dual-publishing one manifest under two paths

The same JSON object is placed at `.claude-plugin/marketplace.json` (for Claude Code) and `.github/plugin/marketplace.json` (for GitHub Copilot CLI) — byte-identical files, two discovery paths. Targets two agentic CLIs from one source without maintaining parallel manifests. Drift between the two copies is a manual-discipline risk; nothing automated keeps them aligned.

### Top-level metadata wrapper

Whether the manifest opens with a `metadata: { ... }` object (carrying `version`, `description`, optional `pluginRoot`) or jumps straight to `name`/`owner`/`plugins`. The wrapper is conventional for partner-style and single-plugin marketplaces; large primary-owned aggregators sometimes omit it entirely. When the wrapper carries a `version` it tends to drift — set once at marketplace birth and rarely bumped against release-tag advances, so consumers reading it see a stale value relative to git tags.

## Per-entry plugin metadata

The fields the marketplace attaches to each plugin entry beyond the bare `name` + `source` — what discovery affordances (categories, tags, keywords) and provenance markers (author, homepage, license) the entry surfaces.

### Category + tags pair

Every entry carries `category: "<single-string>"` plus `tags: [...]`. Uniform across all entries in the marketplace; suits a focused-domain marketplace where one category fits all and tags differentiate within it. `keywords` is unused at the marketplace-entry level.

### Keywords-only

The single-plugin marketplace ships only `keywords: [...]` on the entry — no `category`, no `tags`. Lower-ceremony when there's only one plugin to differentiate against itself.

### Mixed-by-origin metadata

Different field sets per provenance tier in one `plugins[]` array — primary-owned entries use only `name` + `source` + `description`; vendored-partner entries add `author.name`; externally-pulled entries variably add `category` and `homepage`. No uniform shape across the array, which makes client-side schema validation awkward but reflects that the marketplace acts as an aggregator over heterogeneous sources.

## Plugin source binding

How a marketplace entry locates the plugin's content — relative path, vendored partner directory, externally-pulled source, or skill-carving over a shared directory.

### Relative-path string source

`"source": "./<plugin-dir>"` (string form) pointing at an in-repo directory containing `.claude-plugin/plugin.json`. The dominant binding for plugins authored in the marketplace's own repo.

### Object-form remote source with SHA pin

`{source: "url", url, sha}` pulls a plugin from an external repo and pins to a specific commit, yielding reproducible installs. Marketplace re-updates depend on a maintainer manually bumping the `sha`. Variant `{source: "git-subdir", url, path, ref, sha}` carves a subdirectory of an external repo as the plugin root.

### GitHub source with subpath binding

`{source: "github", url, path}` binds to a subdirectory of a sibling repo where the plugin tree lives apart from the rest of the source (e.g., binaries and aggregator metadata in different repos).

### Skill-carving via shared root + skills override

Multiple distinct marketplace entries set `source: "./"` (the repo root) plus `strict: false` (disabling validation of a `.claude-plugin/plugin.json` at the root) plus `skills: ["./<skill-dir>"]` on the entry itself. The marketplace entry replaces `plugin.json` for skills — supplying name, description, category, tags directly — and lets one repo host many skills without a per-skill `plugin.json` wrapper. The trade-off is no per-skill versionable manifest; bumping a skill's version requires re-releasing the whole repo.

### Vendored-partner subtree

Plugin entries point at `./<root>/<partner-name>` directories whose code is authored by an external partner but lives inside the host repo's tree, with the partner's own LICENSE and author attribution. Distinct from external `url`-source entries — partner code is vendored into the host's tree rather than pulled remotely.

### Missing SHA pin on external source

A `{source: "url", url}` entry without a `sha` field accepts whatever is at HEAD of the upstream repo — non-reproducible installs. Appears as drift from the project's own convention rather than an intentional "track main" choice when every other external entry pins.

### Mixed-provenance composition

A single `plugins[]` array hosting in-repo, vendored-partner, and externally-pulled entries simultaneously — three provenance tiers in one manifest. Distinct from pure inline marketplaces or pure aggregator marketplaces.

## Version authority

Where a plugin's version lives — manifest field, marketplace entry, git tag, or none of the above — and which source wins when multiple disagree.

### `plugin.json` only

`version` lives only inside each plugin's `plugin.json`. The marketplace entry carries no `version` field. Plugins drift independently; no two-source-of-truth conflict.

### Manifest plus marketplace entry, manually coordinated

`version` is declared in both `plugin.json` and the marketplace entry (and possibly multiple manifest copies). No automation links them — coordination is hand-edits. Drift emerges as soon as one bump is forgotten in another location.

### Tag-stamped at release time

A release workflow extracts `version` from a `plugin-v*` tag name and writes it into `plugin.json` during packaging. One-way coupling from tag to manifest ensures consistency at the tagged commit, but intermediate plugin.json changes (between tags) ship without the validator.

### No plugin-level version (skill-carving)

Skill-carving entries have no `plugin.json` at all — only the marketplace entry and `SKILL.md`. There is no per-plugin version concept; the only versionable artifact is the marketplace tag covering all skills together.

### Pinned manifest version, floating release tag

Every `plugin.json` holds a hardcoded version (e.g., `"1.0.0"`) regardless of release cuts; the release tag (`v1.1.1`) lives only on git tags and release-asset filenames. plugin.json is treated as written-once-at-introduction; consumers' source of truth is the tag.

### Deliberate divergence: wrapper vs underlying binary

`plugin.json.version` tracks the plugin wrapper release; the underlying binary version floats to upstream HEAD via runtime resolution. Designed to let the binary iterate without forcing plugin bumps. Distinct from a drift defect — the manifest declares "wrapper 1.5.0" while the binary it installs is whatever is freshest.

## Channel distribution

Whether the marketplace exposes multiple update channels (stable vs latest, dev vs release) or one undifferentiated stream.

### No split

Single channel. Users install via `@<marketplace-name>` and track HEAD of the default branch. Release tags exist but consumers are not directed to pin to them. Suits informal release cadence; downstream pinning happens at the consumer's end if at all.

### SHA pinning per external entry

For external `url`-sourced plugins, the `sha` field on each entry acts as a per-plugin pin — the marketplace itself tracks HEAD but each external plugin is frozen at the SHA the maintainer chose. Effectively a per-entry channel pin without a global stable/latest split.

## Plugin-component registration

How a plugin's components (skills, commands, agents, hooks, MCP servers, bin/) are declared to the loader — explicit paths in the manifest, or convention-based discovery from the directory tree.

### Convention-based discovery only

`plugin.json` lists `name`, `version`, `description`, `author`, optionally `homepage`/`repository`/`license`/`keywords`. No `skills`, `commands`, `agents`, `hooks`, or `mcpServers` paths. Components are picked up from conventional directories (`skills/`, `commands/`, `agents/`, `bin/`, `.mcp.json`). Lowest-ceremony declaration; suits the "no code, no infrastructure" posture where the plugin is just markdown and JSON.

### Inline `mcpServers` config in plugin.json

`mcpServers` is declared inside `plugin.json` itself rather than in a separate `.mcp.json`. Two shapes coexist: object form (`{"<ServerName>": {"type": "http", "url": "..."}}`) and string-URL form pointing at an `.mcpb` bundle hosted externally. The object form is conventional; the string-URL form is docs-silent and may be a loader-specific extension that triggers a remote fetch.

### `.mcp.json` sibling file

`.mcp.json` lives alongside `plugin.json` carrying the MCP server configuration separately. Suits plugins where MCP setup is the bulk of the plugin's surface and benefits from being its own file.

### Skill-carving entry with no `plugin.json`

A marketplace entry uses `strict: false` + `skills: [...]` to register a skill directly without any `plugin.json`. The skill directory contains only `SKILL.md` (plus optional `scripts/`, `references/`, `LICENSE.txt`); the marketplace entry supplies plugin-level identity. Discovery is fully driven by the marketplace entry rather than by directory convention.

## Component types in use

Which plugin component categories — skills, commands, agents, hooks, MCP servers, monitors, output styles, bin/ — actually appear across the plugins of a marketplace.

### Skills

Universal across all observed plugins. Every plugin ships at least one `skills/<name>/SKILL.md`. The dominant component type for marketplace plugins.

### Commands

Present in some plugins as a legacy form. Per documentation in mid-migration repos, "the legacy `commands/` format still works but new plugins should use `skills/*/SKILL.md`."

### Agents

Rare. Observed only in one partner-built plugin shipping `agents/*.md` files with frontmatter `name`, `description` (multi-line YAML folded, embedding `<example>` blocks), `model`, `color`, `tools` (plain list — `Read`, `Glob`, `Grep`), `maxTurns`. Tools listed as plain names rather than permission-rule syntax (`Bash(uv run *)`).

### Hooks

Often absent entirely. A marketplace can ship dozens of plugins and zero `hooks.json` files. Aligned with a "no infrastructure" design posture; absence of hooks correlates with absence of session-start install, tool-use enforcement, monitors, and session-context-loading mechanisms.

### MCP servers

Common — declared either via inline `mcpServers` in `plugin.json` or via a sibling `.mcp.json`.

### bin/

Rare. Used when the plugin distributes a binary CLI through shim wrappers (see *CLI distribution*). Absent when the plugin is "just markdown and JSON."

### output-styles, monitors, .lsp.json

Not observed in any sample.

## CLI distribution

Whether and how a plugin ships an executable CLI to the user — committed binaries, lazy-downloaded shims, language-managed runtime fetches.

### No CLI distribution

Plugin contains no `bin/` directory and ships no launcher scripts. Skills that have helper Python scripts under `skills/<name>/scripts/` are read by the LLM and invoked directly via `python path/to/script.py` rather than wrapped behind a CLI. Aligned with the "no code" posture.

### Lazy-install bin shim with fallback chain

Small bash and Windows-batch shims (~600-800 bytes each) live in `bin/` and are auto-discovered by the loader (PATH integration by convention). Each shim checks for the real binary at `${CLAUDE_PLUGIN_DATA}/bin/<name>` (with `$HOME/.<plugin>/bin` fallback); if absent, runs an installer script (also in `scripts/` of the plugin) that downloads platform-appropriate binaries from the project's GitHub Releases, then re-execs. A separate "drop-in" shim layers fallback through co-located alternatives, then a system-installed binary, then the original tool — graceful degradation if anything breaks. Shebang `#!/usr/bin/env bash` with `set -euo pipefail`. Script-relative path resolution (`SCRIPT_DIR=...`) rather than `${CLAUDE_PLUGIN_ROOT}` reference. Self-recursion guarded by a marker string embedded in the shim that the installer greps for.

### Runtime-fetched MCP server via `npx -y`

An MCP server entry uses `npx -y @scope/server --stdio` to fetch and run a Node MCP server on demand. Ad-hoc runtime fetch with no caching managed by the plugin. Trade-off: zero install ceremony, network round-trip on every session.

## Dependency installation

How runtime dependencies (Python packages, Go binaries, Node modules) reach the user's environment — manual user steps, hook-driven installers, lazy-download shims, or absent entirely.

### Not applicable / skill scripts read-only

Skills ship Python scripts under `skills/<name>/scripts/` as code for the LLM to read and adapt rather than to directly execute. The dep surface is whatever the user's environment already has when Claude eventually runs the adapted code via Bash. No manifests declared.

### `requirements.txt` with manual user invocation

A skill ships `requirements.txt` with pinned versions; SKILL.md or a comment in the file instructs the user to run `pip install -r requirements.txt --break-system-packages` themselves. Reproducibility depends on user discipline; `--break-system-packages` is user-hostile on PEP 668-managed systems where no plugin-managed venv exists. No change detection, no retry, no failure signaling — entirely user-driven.

### Lazy-download from project's own releases

Bin shims trigger a one-shot installer that hits the project's GitHub releases API (unauthenticated), filters tags client-side, picks a release, downloads platform-appropriate tarball/zip, extracts to `${CLAUDE_PLUGIN_DATA}/bin/`, writes a version stamp. Existence-only change detection: short-circuits if both binaries exist regardless of version. `mktemp`-based staging with `trap` cleanup so failed downloads leave the target dir untouched. No SessionStart hook involved — install fires on first invocation of the bin shim. Trade-off: zero session-start overhead but the first call pays the download time.

### Runtime-fetch via `npx -y`

For Node MCP servers: `npx -y @scope/server` declared in the MCP config performs the fetch on every session start. Distinct from the lazy-download pattern in that nothing is cached at the plugin's data dir.

## Authentication and credential delivery

How plugins handle secrets and authentication — `userConfig` schemas, environment-variable substitution, OAuth flows embedded in MCP config, or delegation to external CLIs.

### No user configuration

`plugin.json` declares no `userConfig`. Whatever credentials are needed are sourced elsewhere (environment, external CLI auth, MCP server's own login flow).

### Environment-variable substitution in MCP config

`.mcp.json` headers reference `${VAR_NAME}` for bearer tokens; the plugin's README tells users to `export` the variables before launch. Process-environment pattern, not a `userConfig` surface. Nothing marks the variables as sensitive at the plugin level — secret hygiene is entirely the user's shell.

### OAuth client embedded in MCP config

`.mcp.json` carries an `oauth` subfield with `clientId` and `callbackPort`, embedding OAuth client binding directly in the MCP server definition. Likely a Claude Code extension to the standard MCP server schema.

### Delegated to external CLI

The plugin assumes a sibling tool (e.g., `gh auth login`) handles authentication. Plugin README explicitly defers; no auth surface inside the plugin. Suits plugins that wrap an existing authenticated CLI.

### Delegated to MCP server's own login

For remote HTTP MCPs, the README tells users they will "authenticate through the server's web interface when prompted" at first connect. The plugin carries no credential plumbing; the MCP endpoint handles its own auth flow.

## Tool-use enforcement

How a plugin biases or restricts the agent's tool-use choices — hook-based redirection, skill-prose-based bias, or none.

### No enforcement

No `hooks.json`, no PreToolUse matchers. The agent is free to call any tool the harness permits.

### Skill-description prose as enforcement surrogate

The SKILL.md `description` field uses capitalized "MANDATORY" / "Never invoke X directly" phrasing to bias the agent toward the plugin's wrapper. Relies on skill auto-load by relevance match; no hard gate. Trade-off: zero infrastructure, but model-variance can let the agent slip through if the skill doesn't auto-load.

## Session context loading

Whether plugins inject ambient context at session start (or other hook points) versus loading content only on explicit invocation.

### No session-start context

No `SessionStart` hooks, no `UserPromptSubmit` hooks, no `hookSpecificOutput.additionalContext`. Skill-driven first-run bootstrapping (copying assets into cwd, creating files) runs only when the user explicitly invokes the bootstrap skill — aligned with the "no infrastructure" posture but means setup never happens automatically.

## Tag and release cadence

How a project marks released versions — git tag scheme, release branches, pre-release suffixes, dev counters — and how often it cuts releases.

### No tags

The repo carries zero git tags. Version changes are visible only inside each `plugin.json`; consumers pinning `@main` take whatever HEAD has. Periodic `bump-versions-*` branches in commit history suggest manual batch bumps. Deliberately informal even for high-traffic marketplaces.

### Single-namespace `v*` tags on main

`v<semver>` tags placed on main, no release branches. Coarse cadence (e.g., three tags over four months). All `plugin.json` versions stay frozen across the tag sequence; the tag is the only authoritative version marker.

### Dual tag namespaces on a single trunk

Two distinct tag prefixes coexist on `main` — one for an underlying binary (`v*`) and one for the plugin (`plugin-v*`). Each tag prefix triggers its own release workflow. Lets the binary iterate rapidly without forcing plugin bumps and vice versa.

## Release automation

What fires when a release tag is pushed — packaging, asset upload, validation, distribution-channel updates.

### No release automation

No `release.yml`, no workflow files. Release surface is "edit plugin.json version, commit to main, consumers take HEAD." No tag-on-commit, no immutable marker.

### Skill-zip build via filesystem glob

A workflow triggered on `v*` tags globs `*/`, gates on `SKILL.md` presence, zips each matching directory as `<dir>-<tag>.zip`, attaches all zips to a draft GitHub release. Discovery is filesystem-driven, not marketplace-driven — adding a SKILL.md-bearing directory automatically ships a zip on next tag, even if that directory isn't a marketplace-listed plugin. MCP-only plugins produce no zip (they're consumed in-place via `plugin.json`). `softprops/action-gh-release@v1`, `draft: true`, `generate_release_notes: true`. No tag-sanity gates beyond the `v*` glob.

### Cross-compile binary release with multi-target packaging

A `release.yml` triggered on `v*` tags cross-compiles a Go binary across six GOOS/GOARCH pairs, packages tar.gz (POSIX) / zip (Windows) including a generated shim inside each archive, uploads via `softprops/action-gh-release@v2`, computes sha256 checksums, then synthesizes a Homebrew formula via heredoc and pushes it to a sibling tap repo. Substantial automation; the plugin is one of multiple distribution channels.

### Plugin-tagged release with stamp-from-tag

A `release-plugin.yml` triggered on `plugin-v*` tags validates the plugin tree (file existence, JSON lint, `bash -n` parse), stamps `plugin.json.version` from the tag using a Python one-liner, packages a tarball, computes sha256, creates a GitHub release. Tag-to-manifest equality is enforced one-way at release time. Validation only fires at release; pre-merge structural drift sits latent on `main` until a tag is pushed.

## Marketplace validation

What checks the marketplace.json or per-plugin manifests before they reach users — dedicated validators, schema checks, LLM-driven reviewers, or nothing.

### No validation

No validation workflow, no schema check, no pre-commit hook. Drift like missing-SHA entries, inconsistent field sets, or author-name mismatches between nested manifests can ship to main without catching. Reliance on a separate `claude plugin validate` CLI tool not committed to the repo.

### LLM-driven PR review

Workflows invoke `anthropics/claude-code-action@v1` or a reusable cross-repo `claude-skill-review.yml@main` to let Claude comment on PR contents — including frontmatter and manifest changes. Not deterministic; LLM inspection rather than schema enforcement. Trade-off: catches semantic issues a schema can't, misses some structural typos a schema would.

### Ad-hoc shell + JSON-lint at release time

The plugin-release workflow runs `python3 -m json.tool` on `plugin.json`, `bash -n` on each shim, and filesystem existence/executable-bit checks. Validation fires only on tag push, not on PR or merge to main. Coverage zero before tag time.

## Testing and CI

Whether the marketplace has automated tests beyond release-time validation, and what the CI matrix exercises.

### No tests, no CI

No `tests/` directory, no test config, no `.github/workflows/`. Validation is whatever the maintainer runs manually (or what an external CLI provides).

### CI workflows present but no tests

`.github/workflows/` carries claude-action wrappers (claude.yml for `@claude` mention response, claude-code-review.yml on PR, claude-skill-review.yml on PR) plus a release workflow. None invoke a test runner; the LLM-driven reviews substitute for tests.

### Multi-OS Go test matrix plus daily cross-version run

`ci.yml` runs `go test -race -coverprofile`, `go vet`, `gofmt -l .` on a `{ubuntu-latest, windows-latest}` matrix at PR time and adds macOS plus `{stable, oldstable}` Go on a daily schedule. Release workflow crosses six GOOS/GOARCH pairs. Plugin shims are validated only by `bash -n` parse checks at release time — never end-to-end. Action pinning via major tags (`@v4`, `@v5`), no SHA pins. `actions/setup-go@v5` with `go-version-file: go.mod` for implicit module caching.

## Plugin-to-plugin dependencies

Whether a plugin declares dependencies on other plugins via a manifest field, or stays standalone.

### No declared dependencies

No `plugin.json` declares a `dependencies` field. Plugins are flat and independent. Cross-plugin interactions (e.g., two plugins both connecting to the same external service via their own `.mcp.json`) are handled by convention rather than declared.

## Documentation set

What documentation files a plugin or marketplace ships beyond the manifest — READMEs at various scopes, CHANGELOGs, architecture docs, agent-specific docs, license files, community health files.

### Repo-root README only

Single `README.md` at repo root covering install + plugin table + how-it-works. Per-plugin READMEs absent or sparse. Skills rely on `SKILL.md` frontmatter + body as their user-facing doc.

### Per-plugin READMEs alongside repo-root README

Most plugins ship their own `README.md` for their specific feature surface. One or two plugins omit it.

### `CONNECTORS.md` sibling-doc convention

A de-facto per-plugin file describing bundled MCP servers, cross-referenced from SKILL.md files via relative paths. Not a Claude-spec filename — repo-originated convention spread across many plugins in one marketplace.

### `AGENTS.md` as ecosystem-neutral alternative to `CLAUDE.md`

A file targeting "agent tools that look for `AGENTS.md`" — explicit framing as the cross-ecosystem counterpart to Claude-specific `CLAUDE.md`. Observed in a single partner plugin; emerging cross-ecosystem signal.

### `CLAUDE.md` agent-procedures doc

Thin per-plugin pointer doc listing commands and skills. Rare; absent from most plugins and from most repo roots.

### Architecture / design docs

`SPEC.md` and `ADR.md` at repo root cover the project's underlying design (e.g., a binary the plugin wraps). Not mirrored into the plugin subdirectory.

### Community health files

`LICENSE` is universal at repo root; `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` are intermittent. License placement varies — repo-root-only, plus per-plugin LICENSE copies, or LICENSE inside each skill directory only with no repo-root LICENSE (leaving marketplace-level artifacts under no declared license).

### Free-form CHANGELOG

A partner plugin ships a `CHANGELOG.md` as a free-form "Unreleased" list, not Keep-a-Changelog format. Nothing parses it. Most marketplaces lean on GitHub Releases' `generate_release_notes` as their de facto changelog.

## Licensing posture

Where LICENSE files live and what license applies to which artifacts.

### Repo-root LICENSE plus per-plugin duplicates

A repo-root `LICENSE` (e.g., Apache-2.0) governs the marketplace-level artifacts, with identical copies inside primary-owned plugin directories. Vendored-partner plugins ship their own LICENSE file, sometimes a different license (MIT vs Apache-2.0).

### No repo-root LICENSE; per-skill LICENSE only

`LICENSE.txt` (Apache-2.0) inside each skill directory; nothing at repo root. GitHub's license detector returns null. Marketplace-level artifacts (marketplace.json, README, workflows) are under no declared license.

### Single repo-root LICENSE

Conventional MIT/Apache LICENSE at repo root covers everything. Suits single-plugin marketplaces.

## Template-customization mechanism

How a plugin offers human-customizable templates separate from Claude's runtime config-substitution syntax.

### Placeholder-token convention

Generic plugins use placeholders like `~~jira` or `~~your-team-channel` as customization markers. A "customizer" skill walks the user through replacing tokens with their organization's specifics. Distinct from `${user_config.KEY}` substitution — a separate human-in-the-loop templating layer that the customizer skill processes.

## Bundled static asset delivery

How a skill ships non-code assets (HTML, images, templates) and gets them to the user's working directory.

### Skill-instruction-driven copy

A static asset (e.g., `dashboard.html`) lives inside the skill directory and SKILL.md instructs the model to copy it from `${CLAUDE_PLUGIN_ROOT}/skills/<name>/<asset>` to the user's cwd at first invocation. Not a canonical plugin component type — the skill treats it as a bundled asset and the model executes the copy via Bash.

## Skill-frontmatter extensions

Non-canonical SKILL.md frontmatter fields a marketplace adopts beyond the documented schema.

### `user-invocable: false`

Marks a skill as composition-only — used by other skills, not exposed as a slash command. Not in the core plugin-reference frontmatter docs; appears to be a host-environment-specific extension.

### `compatibility:` prose

Free-form prose declaring platform prerequisites (e.g., "Requires Cowork desktop app environment"). Not in the canonical schema; another host-environment extension.

### `allowed-tools` as scalar

Single-string scalar (e.g., `allowed-tools: Bash`) rather than a list, gating which tools the skill may invoke.

## Distribution channels orthogonal to the plugin

Additional ways the same software reaches users alongside the plugin path.

### Homebrew formula generated by release workflow

The release workflow synthesizes a Homebrew formula via heredoc (with per-platform URLs and sha256), clones a sibling `homebrew-tap` repo with a PAT, commits `Formula/<name>.rb`, pushes. The plugin is one channel; the tap is another. Orthogonal to the plugin but worth noting as an additional distribution surface for users who want the underlying tool system-wide.
