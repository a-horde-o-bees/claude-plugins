# Sample

Pass-1 Phase-1a partial for bin 11. Functional decomposition of `anthropics--claude-plugins-official.md`, `anthropics--financial-services-plugins.md`, and `anthropics--healthcare.md`, organized by role with implementation paths as sub-sections.

## Marketplace manifest layout

How the marketplace describes itself and the plugins it lists.

### Single root-level manifest

A single `.claude-plugin/marketplace.json` at the repo root is the only distribution surface. The file lists every plugin in one `plugins: [...]` array. Scales from a small handful of entries up to triple digits in one file. No supporting registry files, no per-plugin shards. Consumers point `/plugin marketplace add` at the repo URL and receive the complete plugin set.

### Top-level fields without a metadata wrapper

Plugins live alongside `name`, `owner`, optional `description`, optional `$schema` at the top level — no `metadata: {...}` wrapper. The owner block carries `{name, email}`, sometimes without `url`. Appropriate when there is no marketplace-wide version or content root to declare; the manifest acts as a flat list.

### `metadata.version` wrapper for marketplace-wide release tagging

A `metadata: {version, description}` wrapper sits above `plugins`, where `metadata.version` is the only machine-readable version covering plugins that carry no `plugin.json` of their own. Lets a single tag (`v1.0.0`) cover the whole catalog when all entries are carved from the same repo and individual plugin versioning would be redundant. Constraint: no per-plugin granularity — every carved plugin moves at the catalog's pace.

### Per-entry discoverability fields

The marketplace entry can carry `category`, `tags`, and `keywords`. Adoption is uneven across the samples — uniform `category` + `tags` on a small focused catalog, partial `category` adoption with negligible `tags`/`keywords` on a large mixed catalog, or none at all on a small flat catalog. Matters for the in-CLI `/plugin > Discover` browsing surface; absence pushes discovery into README prose.

## Plugin source binding

How a marketplace entry points at the actual plugin payload.

### Relative path into the same repo

`source: "./<dir>"` (or `source: "./"` for repo-root carves) names a directory inside the marketplace repo. The plugin payload ships in the same git history as the manifest. Appropriate for first-party catalogs where the marketer authors the plugins; constrains release cadence to whatever git posture the marketplace itself uses.

### Cloneable URL

`source: {source: "url", url: "<git-url>"}` clones an arbitrary git repo at marketplace-resolve time. No path scoping inside the cloned repo — the whole repo is treated as the plugin. Used for partner-built plugins whose canonical home is a separate repository.

### `git-subdir` with SHA pin

`source: {source: "git-subdir", repo: "<repo>", path: "<dir>", sha: "<commit>"}` pins a specific commit of a subdirectory inside an external repo. The only source kind in the corpus that gives reproducible installs across time. Combined with bot-maintained SHA bumps (see *Source-pin maintenance*), this is the recipe for a curated catalog of upstream content with predictable refresh cadence.

### `github` shorthand

`source: {source: "github", repo: "<owner>/<name>"}` exists as a more declarative alternative to the `url` form. Effectively unused in the corpus — surfaced once across the samples — suggesting either historical residue or a path the larger catalogs have not adopted.

### `strict: false` to carve component subsets from a source

A marketplace entry with `strict: false` opts out of expecting a `plugin.json` at the source root and instead declares the plugin's components inline on the entry itself. Two adoption shapes observed:

- *Single-skill carves from a shared repo root* — `source: "./"`, `strict: false`, `skills: ["./<one-skill-dir>"]`. Three sibling plugins all read from the same repo root, each carving exactly one skill directory. Avoids per-plugin `.claude-plugin/plugin.json` files at the cost of having no per-plugin version surface.
- *Hollow plugin directory with all definition on the entry* — `strict: false`, full component config (e.g., `lspServers: {...}`) on the marketplace entry; the plugin directory holds only `README.md` + `LICENSE`. Used as an "umbrella" pattern (one plugin per language, all centrally declared).

Constrains version authority: `strict: false` carves typically have nothing on the marketplace entry's `version` either, so the only version is whatever the manifest itself carries.

## Plugin metadata and component registration

What the plugin says about itself once installed and how its components get wired.

### Default-discovery `plugin.json`

`plugin.json` declares only identity (`name`, `description`, `author`, sometimes `version`) and lets the loader find components by convention (`commands/*.md`, `agents/*.md`, `skills/*/SKILL.md`, `hooks/hooks.json`, `.mcp.json`). The dominant pattern across all three samples for plugins that ship multiple component types. Path: minimal metadata, conventional layout, no explicit registration.

### Inline `mcpServers` in `plugin.json`

`plugin.json` carries `mcpServers: {<name>: {...}}` inline, replacing or duplicating an external `.mcp.json`. Used when the plugin's only component is an MCP server (no skills, no commands) — keeps the whole plugin definition in one file. Constraint: when both forms exist (one plugin in the corpus does this), they are two sources of truth with no automation reconciling them.

### Marketplace-entry-only definition (no `plugin.json`)

Plugin directory has no `.claude-plugin/plugin.json`; the marketplace entry's own fields (`skills`, `lspServers`, `version`, etc.) are the entire definition. Requires `strict: false` on the entry. Two shapes: skill-carving (entry's `skills: ["./<dir>"]` is the only registration) and hollow umbrella (entry's `lspServers: {...}` is the entire plugin). Trade-off: centralizes definition in the manifest at the cost of independent plugin-level versioning.

### Empty hooks scaffolding

`hooks/hooks.json` exists but contains `{}` or `[]` — no hooks registered. Shows up uniformly across plugins from one marketplace, suggesting template residue or forward-compat scaffolding rather than active hooks. Either an anti-pattern (dead files) or a deliberate "extension point" convention; the corpus shows no documentation explaining the choice.

## Plugin component composition

What components a plugin actually ships, named by which kinds appear together.

### Skill-only payload

Plugin contains only `skills/<name>/SKILL.md` (plus optional `references/`, `assets/`, `scripts/`). Skill description does the work of surfacing the plugin to the agent; nothing else interacts with the host. Appropriate for content-driven domain knowledge (clinical-trial protocols, FHIR development) where the plugin's value is the prompt content the skill carries.

### MCP-only payload

Plugin contains only `.mcp.json` (or inline `mcpServers` in `plugin.json`) plus identity metadata. Surfaces remote MCP tools to the agent. Appropriate when the plugin's value is access to a hosted backend; the local payload is just the connection config.

### Mixed skills + commands + agents + hooks + MCP

Plugin ships several component kinds together — skills for surfaceable domain knowledge, commands for agent-invokable verbs, agents for sub-task delegation, hooks for tool-use enforcement or context injection, MCP for backend tools. Default-discovery `plugin.json` is the wiring; conventions handle the rest. Appropriate for plugins that wrap a workflow rather than expose a single resource.

### LSP-server-only "hollow" plugin

Plugin directory holds only `README.md` + `LICENSE`; the marketplace entry's `lspServers` block is the entire plugin definition. One plugin per language server, distributed independently but with no component body in the plugin tree.

## Channel distribution

How a marketplace exposes versioning to consumers between releases.

### Tip-of-main only (no channel)

`main` is the sole distribution stream; `/plugin install X@<marketplace>` resolves against current `main` HEAD. No tags, no release branches, no `stable` vs `latest` duplicate manifests. Dominant posture across the corpus — consumers implicitly track HEAD.

### Single tag with main drift

A single annotated tag (`v1.0.0`) exists on `main` but `main` continues to advance past it. Without a tag-pinning install path (`@v1.0.0` semantics), the tag is effectively a snapshot artifact rather than a channel. Constraint: consumers cannot easily diff intervening changes from manifest to tag.

### SHA-pinning per `git-subdir` source

Reproducibility lives inside the source kind, not on the manifest as a whole. Each `git-subdir` entry carries its own `sha`, and a bot-PR cycle (see *Source-pin maintenance*) rolls those forward. The marketplace itself stays single-channel; pin discipline is per-entry.

## Version authority

Where the version each consumer sees originates.

### `plugin.json` only

`plugin.json.version` is the sole version source. Marketplace entry carries no `version`. Each plugin bumps independently. Constrains the manifest from authoritatively expressing release state — drift is invisible until a consumer notices.

### Marketplace entry `version` for entries without a plugin body

`version` on the marketplace entry is authoritative for plugins whose entry carries the entire definition (LSP umbrellas at `1.0.0`, similar carves). Used because the plugin directory has no `plugin.json` to carry one.

### Marketplace `metadata.version` as catalog-wide version

`metadata.version` covers all plugins simultaneously when individual entries have no `plugin.json` and no entry-level `version`. Single coarse version for the whole catalog; appropriate when catalog and content release together.

### Manual bump without enforcement

Versions exist but nothing verifies bump-on-change — no pre-commit hook, no CI gate, no tag-vs-version assertion. Plugins ship at `0.1.0` while peers move ahead independently; breaking changes can land without any version bump. The version field is cosmetic.

## Distribution model

How the catalog mixes content sourced from different places.

### First-party-only flat catalog

Every plugin is authored by the marketplace owner and lives in the same repo. Uniform structural convention, single review surface, single license posture. Appropriate for tightly-curated domain catalogs.

### Hybrid first-party + partner-built via in-repo vendoring

A `partner-built/<partner>/` directory convention separates third-party-authored plugins from first-party ones in the same tree. Partner plugins may declare their own `repository:` pointing at a canonical home; the in-repo copy is a vendored snapshot. No filesystem-marker beyond the path; sync mechanism (manual pull vs scripted) is not visible from the repo content alone.

### Hybrid in-repo + external SHA-pinned + cloneable URL

A single manifest mixes (a) `./plugins/<name>` entries owned by the marketplace, (b) `git-subdir` SHA-pinned external subdirectories, (c) `url`-cloneable whole-repo entries, with no structural distinction at install time — all surface uniformly through the same install command. Allows the marketplace to be both author-of-record (for in-repo content) and broker-of-record (for external content). Constrains the bump/release story per source kind; only `git-subdir` is reproducibly pinned.

## User configuration delivery

How a plugin lets the user configure it without hard-coding values.

### Bare `${ENV_VAR}` substitution in `.mcp.json`

`.mcp.json` references shell environment variables directly (`Authorization: "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"`, `-e TFE_TOKEN=${TFE_TOKEN}`). The user is expected to set the variable in their shell. Constrains discoverability — the user must read `.mcp.json` (or README) to learn what variables the plugin expects; no schema, no `sensitive: true` handling.

### Gitignored `.local.md` convention

A plugin ships an `<name>.local.md.example` template; the user copies it to `<name>.local.md` (gitignored) and edits values. Skills read the file at runtime via prose instructions, not a harness substitution mechanism. User-facing configuration as a file convention layered atop markdown — works without harness involvement, lacks any schema enforcement.

### External schema in admin-run script

Configuration is collected by a user-side script the admin runs out-of-band (`build-manifest.mjs`) that hand-rolls a `KEYS` object with regex patterns, hints, and `secret: true` flags, then emits a downstream config artifact. Plugin metadata layer is bypassed entirely; the plugin ships *tooling for the admin* rather than being configured itself. Recreates `userConfig` semantics outside the manifest.

## Plugin-to-plugin dependencies

How a plugin expresses that another plugin must be installed first.

### Implicit prose-only dependency

README states "install plugin X first" without expressing the relationship in any manifest. A function-specific plugin's skills reference MCP tools owned by a sibling core plugin; if the user installs only the function plugin, skills load but the tools they call are missing. Documentation is the only enforcement; failure surfaces at use time.

### No declared dependencies (flat catalog)

`dependencies` field is unused. Plugins are designed to be independent or to fail gracefully when peers aren't installed. Appropriate for flat catalogs where each plugin owns its full surface; insufficient when one plugin owns shared infrastructure that others reference.

## Tool-use enforcement

How the plugin observes or constrains tool calls in the host session.

### Universal-matcher rule evaluator

A `PreToolUse` hook with no matcher (fires on every tool call) plus a `PostToolUse` companion runs a Python evaluator against user-defined rules in `.claude/<plugin>.*.local.md` files. Output is JSON `{"systemMessage": "..."}` to stdout; failure posture is uniformly fail-open with try/except wrapping that always exits 0 ("never block operations due to hook errors"). Timeouts declared (10s). Used to give the user a configurable tool-policy mechanism without modifying the harness.

### Edit-targeted security reminder

A `PreToolUse` hook with `matcher: "Edit|Write|MultiEdit"` runs a security-warning script on file modifications. No declared timeout; if it hangs, the harness waits. Narrower trigger than the universal evaluator; still uses the JSON-to-stdout output convention.

### No enforcement (empty or absent)

`hooks/hooks.json` either does not exist or is empty (`{}` / `[]`). No PreToolUse, PostToolUse, or PermissionRequest hooks. Dominant posture across the corpus.

## Session context loading

How the plugin injects always-on or per-prompt context into the agent.

### `SessionStart` `additionalContext` injection

A `SessionStart` hook's handler script emits `{"hookSpecificOutput": {"additionalContext": "<blob>"}}` to stdout. Used to load a large instruction blob at session start (e.g., to emulate the unshipped "output style" feature: an entire prose blob that re-shapes the model's output behavior). Bash here-doc is the typical implementation; no matcher means it fires on `startup|clear|compact`. Demonstrates that the hooks API can subsume a missing first-class harness feature.

### `UserPromptSubmit` for rule evaluation (not context)

A `UserPromptSubmit` hook exists but its purpose is rule evaluation rather than additive context — output is system messages reacting to the prompt, not appending instructions. Distinct from `SessionStart` injection.

### No session-context loading

No `SessionStart`, no `UserPromptSubmit`, no `additionalContext`. Plugin relies on skill frontmatter `description` matching for surface — content loads on demand when the agent recognizes the skill is relevant. Dominant pattern; aligns with the "no always-on injection" Cowork posture.

### Stop-hook prompt re-injection loop

A `Stop` hook emits `{decision: "block", reason: "<previous-prompt>", systemMessage: "..."}` to re-feed the prior prompt back into the agent on each Stop, implementing a self-iterating work loop. State (iteration counter, escape protocol, session ID gating) lives in `.claude/<plugin>.local.md`. Non-obvious use of the Stop block protocol as a control-flow primitive — the hook API as agentic-loop substrate.

## Dependency installation

How a plugin gets runtime dependencies onto the user's machine.

### No managed install (user prerequisite)

README states "Requirements: Python with scipy and numpy" or similar; plugin ships a script that imports the deps and crashes with `ImportError` if they're missing. No `requirements.txt`, no plugin-managed venv, no SessionStart install hook. User-side prerequisite is the entire install story.

### Ad-hoc runtime fetch via launcher command

External MCP plugins use launcher commands like `npx @playwright/mcp@latest`, `uvx --from git+... serena`, `docker run hashicorp/terraform-mcp-server:0.4.0` in `.mcp.json`. The launcher fetches the package each session (or uses its own cache); the plugin itself manages no state. Sidesteps install entirely — the cost is per-session fetch overhead.

### Remote HTTP MCP (no client install)

Plugin's tools are reached by HTTP MCP at a hosted URL. No local process, no command, no env vars beyond auth. The "dependency" is the provider's SaaS uptime and the user's subscription. Cleanest distribution shape — dependency installation simply doesn't apply.

### Out-of-band admin tooling

Plugin ships a Node `scripts/build-manifest.mjs` and a Python `examples/python-bootstrap/` reference server. The setup command shells out to `node`/`npx` after asking the admin to install Node themselves. Genuine dep-bearing code lives outside the plugin component surface — `scripts/` and `examples/` are admin tooling, not plugin components. No plugin-install hook touches them.

## Bin-wrapped CLI distribution

Plugin shipping its own user-runnable executables.

### No `bin/` (corpus-wide absence)

No `bin/` directory exists in any plugin across all three samples. Hook scripts are invoked via `${CLAUDE_PLUGIN_ROOT}/hooks/<file>.sh` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py` from `hooks.json`, not as bin entry points. Scripts the user runs (e.g., a manifest builder) live under plugin-local `scripts/` and are invoked from command markdown via raw shell — not wrapped, not registered.

## Source-pin maintenance

Keeping `git-subdir` SHA pins fresh over time without manual labor.

### Scheduled bot-PR with fairness ordering

A `bump-plugin-shas.yml` workflow runs on cron (weekly), iterates pinned `git-subdir` entries, queries each upstream for the latest commit on the pinned ref (respecting `path` scope), sorts by `-age_days` so the oldest-pinned entries roll first ("prevents starvation under the cap"), applies up to N bumps per run (default 20, configurable), and opens a single bot-signed PR. Concurrency is enforced via label-based check (`gh pr list --label sha-bump --state open`) so at most one open bump PR exists at a time. Force-pushed-away SHAs and 404s are categorized as "dead" without blocking other bumps. Permissions live on a GitHub App (org policy bars `GITHUB_TOKEN` from creating PRs).

## CI validation

What the marketplace verifies on PRs and pushes.

### Schema-and-shape validators in TS

Bun-run TypeScript scripts validate `marketplace.json` (object shape, `plugins` array, per-entry required fields, duplicate detection) and frontmatter on agents/commands/skills (per-type required fields, glob-special-char pre-quoting so patterns like `**/*.{ts,tsx}` parse). PR-only triggers, path-scoped so each validator fires only on relevant changes. Plain TS, no zod. Constraint: validates field presence, not shape (e.g., `source` must be truthy but its discriminator isn't checked).

### Alphabetical-sort enforcement

A `check-marketplace-sorted.ts` script runs on every PR touching `marketplace.json` and fails if `plugins[].name` isn't case-insensitively sorted. Provides a `--fix` flag that rewrites the file in place. Treats the manifest as a sorted registry — CI rather than pre-commit hook is the enforcement point.

### Agent-driven semantic review

PR workflows install a sibling Anthropic plugin (e.g., `code-review` from `claude-code-plugins`, `example-skills` from `anthropic-agent-skills`) and run a slash command (`/code-review:code-review`, skill-creator) against the diff. Comments land on the PR. Distinct from deterministic validation — these are LLM-in-the-loop reviewers; no pytest, no ruff, no JSON-schema validator. A dynamic matrix over `find . -name SKILL.md` runs one review job per affected skill so the workflow auto-adjusts to new skills without edits.

### `@claude` mention responder

A general-purpose `claude.yml` workflow on `issue_comment`, `pull_request_review_comment`, `issues`, `pull_request_review` events, gated on `@claude` mention. Uses `anthropics/claude-code-action@v1`. Not validation per se — turns the repo into an agent-addressable surface for ad-hoc questions and patches.

### Organizational PR bouncer

A `close-external-prs.yml` workflow on `pull_request_target: [opened]` checks the PR author's collaborator permission level via the GitHub API and auto-closes any PR from non-admin/non-write users with a comment redirecting to a submission form. Disableable via repo variable. Implements org-wide submission gating as a workflow rather than as branch-protection rules — appropriate when admin-controlled merging needs an explicit "this is not the contribution path" signal at PR-open time.

### No CI surface

No `.github/workflows/` directory. All quality control is review-time on PRs. Plugins land at tip-of-main with manual review as the only gate. Notable for first-party Anthropic-owned marketplaces of substantial scale.

## Release packaging

How a marketplace produces installable artifacts at tag time.

### Tag-triggered skill-zip packaging with draft release

`release.yml` triggers on `push: tags: ['v*']`. Iterates directories matching `*-skill/`, zips each, and attaches all zips to a draft GitHub release via `softprops/action-gh-release@v1` with `generate_release_notes: true`. No CHANGELOG parsing — release notes are auto-generated. Discovery of what to package is structural (the `*-skill` glob); MCP plugin directories that don't match are silently excluded from release artifacts. Constrains naming convention: skill plugins must end in `-skill/` to be released.

### No release pipeline

No `release.yml`. No tags. No CHANGELOG. Plugins distribute exclusively through tip-of-main install. Dominant pattern across the larger corpus. Appropriate when consumers expect rolling deployment; mismatched with version fields that nothing enforces or surfaces.

## Documentation

Project-level and plugin-level prose for users.

### Repo README + per-plugin READMEs

Repo root has a substantial `README.md` covering install, structure, and contribution; each (or most) plugins also ship their own `README.md`. Coverage is uneven — first-party plugins typically ship one, thin external MCP wrappers usually do not. Skills without a README rely on `SKILL.md` frontmatter for discoverability.

### Repo README only

Single substantial README at repo root; plugins do not ship per-plugin READMEs. Plugin discovery happens through marketplace metadata (`description`, `category`, `tags`) and the README's own plugin matrix.

### Stale `CLAUDE.md`

A repo-root `CLAUDE.md` references paths and structures that do not exist in the current tree (`mcp/`, `mcp-categories.json` referenced but absent). Generic template scaffolding never updated to match reality. Following it would mislead an agent — the document looks authoritative but isn't.

### No CHANGELOG, no architecture document, no community-health files

`CHANGELOG.md`, `ARCHITECTURE.md` / `architecture.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` are absent across the corpus. README "Contributing" subsections substitute where contribution guidance exists at all.

### Per-plugin LICENSE without repo-level LICENSE

Each plugin directory ships its own `LICENSE` file (Apache-2.0 boilerplate, byte-identical across internal plugins). Repo root has no `LICENSE`; GitHub API reports `license: null`. README explicitly directs readers to per-plugin LICENSE files. Constraint: GitHub's license picker shows "No license" for the repo as a whole even though Apache-2.0 is present throughout.

### Repo-level LICENSE only

Apache-2.0 at repo root applies to all plugins; partner-built directories may carry their own LICENSE additionally. Standard ecosystem shape.

### No machine-readable license

No `LICENSE` file, no SPDX identifier; README prose ("provided under Anthropic's terms of service") is the entire license surface. GitHub license detection returns null. Downstream package tooling cannot identify terms.

## Workflow state persistence

Where running plugin state lives between sessions.

### User-visible markdown setup log

Plugin instructs the agent to read `~/Desktop/<plugin>-setup.md` first and append a `## Run — <timestamp>` section on each invocation. Setup is fully resumable across sessions; the human can inspect or edit the log directly. Uses a user-visible plain markdown file as workflow state — distinct from hidden caches or harness-managed state.

### Plugin-local `.local.md` with YAML frontmatter

Plugin reads/writes `.claude/<plugin>.local.md` (markdown body with YAML frontmatter) for iteration counters, escape protocols, and session-ID gating. Hidden but inspectable; persists across Stop-hook iterations within a session and across sessions. Used by the Stop-hook re-injection loop pattern.
