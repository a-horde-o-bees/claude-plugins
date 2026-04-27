# Sample

## Identification

### URL

https://github.com/anthropics/financial-services-plugins

### Stars

7700

### Last commit date

2026-04-17 (`356f09fe feat(manifest): add inference_headers config key (#68)`)

### Default branch

main

### License

Apache-2.0

### Sample origin

primary (Anthropic-owned marketplace; 8 plugins — 5 Anthropic-built core/function, 2 partner-built, 1 Office add-in admin tool)

### One-line purpose

Marketplace of Claude for Financial Services plugins (investment banking, equity research, private equity, wealth management, plus an Office-add-in admin setup plugin) built primarily for Claude Cowork, also compatible with Claude Code.

## 1. Marketplace discoverability

### Manifest layout

single `.claude-plugin/marketplace.json` at repo root (2,025 bytes)

### Marketplace-level metadata

none — top-level shape is `{ name, owner: {name}, plugins: [...] }`. No `metadata` wrapper, no top-level `description`, no `version`.

### `metadata.pluginRoot`

absent

### Per-plugin discoverability

none — entries carry only `{name, source, description}`. No `category`, `tags`, or `keywords` at the marketplace-entry level. (One partner plugin, `sp-global`, declares `keywords` inside its own `plugin.json`; no other plugin does.)

### `$schema`

absent

### Reserved-name collision

no (plugin names are descriptive: `financial-analysis`, `investment-banking`, `equity-research`, `private-equity`, `wealth-management`, `lseg`, `sp-global`, `claude-in-office`)

### Pitfalls observed

Marketplace manifest description and plugin `plugin.json` description drift — e.g. marketplace entry for `investment-banking` reads "client and market insights, deck creation, financial analysis, and transaction management" while its `plugin.json` reads "client and market insights, deck creation, financial analysis, and transaction management" (match), but the core `financial-analysis` marketplace entry and its `plugin.json` both say "Core financial modeling and analysis tools: DCF, comps, LBO, 3-statement models, competitive analysis, and deck QC" (match). Still, because the field is duplicated across two files with no automation gluing them, drift is latent. No `category`/`tags` means nothing drives faceted discovery — the README is the discovery surface.

## 2. Plugin source binding

### Source format(s) observed

`relative` only — every entry uses `"source": "./<dir>"` (five at repo root, two under `./partner-built/`, one at `./claude-in-office`).

### `strict` field

default (implicit true) — no `strict` key on any entry.

### `skills` override on marketplace entry

absent

### Version authority

`plugin.json` only — each plugin carries its own `version`; marketplace entries carry no version. (Observed versions: `financial-analysis` 0.1.0, `investment-banking` 0.2.0, `equity-research` 0.1.0, `private-equity` 0.1.0, `wealth-management` 0.1.0, `lseg` 1.0.0, `sp-global` 1.0.0, `claude-in-office` 0.1.0.)

### Pitfalls observed

plugin-name/dir mismatch for the S&P Global entry — marketplace key `sp-global`, source directory `./partner-built/spglobal` (no hyphen), and `plugin.json` `name: "sp-global"`. Functionally fine (marketplace `name` is authoritative for install), but the directory layout doesn't mirror the plugin name.

## 3. Channel distribution

### Channel mechanism

no split — users pin via `@ref` on install (install snippets in README use bare `plugin@financial-services-plugins`, no ref).

### Channel-pinning artifacts

absent — no stable/latest duplicate marketplaces, no release branches, no tags.

### Pitfalls observed

no pinning surface means any consumer implicitly tracks `main` HEAD — `claude plugin install financial-analysis@financial-services-plugins` resolves against current main. Anthropic-owned primary sample ships with the most permissive possible distribution posture.

## 4. Version control and release cadence

### Default branch name

main

### Tag placement

none (`git/tags` returns 0 entries)

### Release branching

none (branch list shows `main` plus feature branches with `author/topic` convention: `manar/inference-headers`, `aperlov/azure-foundry-manifest-keys`, `cxl/remove-yfinance`, etc.)

### Pre-release suffixes

none observed

### Dev-counter scheme

absent — plugin versions bump manually (e.g., `investment-banking` at 0.2.0 while peers sit at 0.1.0; partner plugins at 1.0.0).

### Pre-commit version bump

no — no hooks infra, no automation; commits don't touch version (recent 5 commits on main never bump `version` fields).

### Pitfalls observed

plugins ship without a release discipline. `version` fields are effectively cosmetic — nothing verifies bump-on-change, nothing tags, nothing releases. Consumers have no semver signal; a breaking change could land at `0.1.0` HEAD without any version bump.

## 5. Plugin-component registration

### Reference style in plugin.json

default discovery — every Anthropic-built `plugin.json` has only `{name, version, description, author}`. `sp-global` adds `mcpServers` inline (an object with a single `spglobal` HTTP server) despite also having `.mcp.json` at its plugin root — redundant declarations.

### Components observed

    - skills — yes (every plugin except `claude-in-office`)
    - commands — yes (every plugin)
    - agents — no (no `agents/` dir in any plugin)
    - hooks — structurally yes for five Anthropic plugins (`hooks/hooks.json` exists) but semantically no — every `hooks.json` is empty (`{}` or `[]`). Partner and claude-in-office plugins have no `hooks/` dir.
    - .mcp.json — yes for `financial-analysis` (11 servers), `partner-built/lseg` (1), `partner-built/spglobal` (1); `investment-banking/.mcp.json` is an empty `{"mcpServers": {}}`; others have none.
    - .lsp.json — no
    - monitors — no
    - bin — no (closest analog: `claude-in-office/scripts/build-manifest.mjs`, invoked from command markdown rather than surfaced as a plugin component)
    - output-styles — no

### Agent frontmatter fields used

not applicable (no agents present)

### Agent tools syntax

not applicable

### Pitfalls observed

empty `hooks/hooks.json` files on five plugins are dead scaffolding — they exist but declare no hooks. Either remnants of a template, forward-compat stubs, or scaffolding for user customization; nothing in README or CLAUDE.md explains their presence. `sp-global` duplicates MCP server config in both `.claude-plugin/plugin.json` (inline `mcpServers`) and `.mcp.json` — two sources of truth.

## 6. Dependency installation

### Applicable

no for the Anthropic-built five core/function plugins and the two partner plugins — pure markdown + JSON + HTTP MCP URLs, no runtime deps. Partially applicable for `claude-in-office`: it ships a Node `scripts/build-manifest.mjs` (plain `import` from `node:fs`, no package manifest) and a Python FastAPI reference server under `examples/python-bootstrap/` with its own `requirements.txt`.

### Dep manifest format

`requirements.txt` (only in `claude-in-office/examples/python-bootstrap/`); the `.mjs` script has no `package.json`.

### Install location

not applicable at plugin level — the Python example is a reference server the admin runs out-of-band on their own infra, not installed into `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PLUGIN_ROOT}`.

### Install script location

inline in `commands/setup.md` — the setup command checks `node --version` and asks the user to install Node via their package manager before the command shells out to `node`/`npx`.

### Change detection

none — no hook, no cache, no SessionStart dep-install machinery.

### Retry-next-session invariant

not applicable

### Failure signaling

the bundled `build-manifest.mjs` uses `console.warn`/`console.error` + non-zero `process.exit(1)` for bad input and missing URL slots; not an install-time signal.

### Runtime variant

mixed and user-side only — Node for the manifest generator (user installs), Python for the bootstrap reference server (user installs).

### Alternative approaches

`npx` invocation from command markdown is the closest pattern — no PEP 723, no pointer files, no uvx, no venv.

### Version-mismatch handling

none

### Pitfalls observed

`claude-in-office` places genuine dependency-bearing code outside the plugin component surface — `scripts/` and `examples/` are user-facing admin tooling, not plugin components. The setup command asks the admin to run `node`/`npx` on their own box. This sidesteps the whole plugin-dep-install story but also means there's no automation path when Node is missing — failure is surfaced as "stop here" in the command prose.

## 7. Bin-wrapped CLI distribution

### Applicable

no — no `bin/` directory in any plugin.

### `bin/` files

none. (`claude-in-office/scripts/build-manifest.mjs` is the only dedicated script, invoked from command markdown via `node scripts/build-manifest.mjs ...`, not registered as a plugin bin.)

### Shebang convention

not applicable

### Runtime resolution

not applicable

### Venv handling (Python)

not applicable

### Platform support

not applicable

### Permissions

not applicable

### SessionStart relationship

not applicable

### Pitfalls observed

repo demonstrates a pattern where scripts the user runs (like `build-manifest.mjs`) live alongside commands but outside the plugin bin surface. If the Claude Code bin mechanism existed in its current shape, this script would be a candidate — instead it's shell-invoked from command prose.

## 8. User configuration

### `userConfig` present

no — no plugin.json declares `userConfig`.

### Field count

none

### `sensitive: true` usage

not applicable

### Schema richness

not applicable

### Reference in config substitution

not applicable — instead, `investment-banking` ships `.claude/investment-banking.local.md.example`, a plaintext YAML template the user copies to `.claude/investment-banking.local.md` (gitignored) to encode coverage/sector/deal preferences. This is a convention-only user-config channel: the file is read by skills at runtime rather than resolved by a harness substitution mechanism.

### Pitfalls observed

`claude-in-office/scripts/build-manifest.mjs` has its own per-key schema (`KEYS` object with regex patterns, hints, and a `secret` flag) for Vertex/Bedrock/gateway config — a parallel, hand-rolled config-surface system that does exactly what `userConfig` exists for, but lives outside the plugin metadata layer. Notably, it *does* flag secrets (`gateway_token: { secret: true }`) and emits a warning when those are used in the manifest (which is org-wide), steering the admin toward per-user extension attrs instead. This is a mature "don't-put-secrets-here" posture implemented outside the manifest format.

## 9. Tool-use enforcement

### PreToolUse hooks

none (every `hooks.json` that exists is empty)

### PostToolUse hooks

none

### PermissionRequest/PermissionDenied hooks

absent

### Output convention

not applicable

### Failure posture

not applicable

### Top-level try/catch wrapping

not applicable

### Pitfalls observed

all five Anthropic-built plugins ship a `hooks/hooks.json` file but register zero hooks. The scaffolding is present, the behavior is absent — pure boilerplate.

## 10. Session context loading

### SessionStart used for context

no

### UserPromptSubmit for context

no

### `hookSpecificOutput.additionalContext` observed

no

### SessionStart matcher

not applicable

### Pitfalls observed

no session-context loading at all. Plugins rely entirely on skills' frontmatter `description` matching to surface domain knowledge when relevant — the classic Cowork pattern (no always-on injection).

## 11. Live monitoring and notifications

### `monitors.json` present

no

### Monitor count + purposes

none

### `when` values used

not applicable

### Version-floor declaration

not applicable

### Pitfalls observed

none (monitors simply not used)

## 12. Plugin-to-plugin dependencies

### `dependencies` field present

no — no `plugin.json` declares a `dependencies` field. The README states "Start with **financial analysis** — the core plugin that provides shared modeling tools and all MCP data connectors" but enforces this only as prose, not as a manifest dependency. `investment-banking` etc. have an empty `.mcp.json` and skills that assume `financial-analysis`'s MCP servers are loaded, but nothing in the metadata expresses that.

### Entries

none

### `{plugin-name}--v{version}` tag format observed

not applicable (no tags at all)

### Pitfalls observed

implicit dependency on `financial-analysis`: the core plugin owns all 11 MCP connectors, and function-specific plugins reference them in skill prose without declaring the dependency. If a user installs `investment-banking` without `financial-analysis`, the skills will still load but reference MCP tools that aren't configured. The dependency is documented in README ("install first") but not enforced by metadata.

## 13. Testing and CI

### Test framework

none — no `tests/` directory anywhere, no pytest config, no jest/vitest config.

### Tests location

not applicable

### Pytest config location

not applicable

### Python dep manifest for tests

not applicable

### CI present

no — `.github/` directory does not exist at repo root (GitHub API returns 404 for `/contents/.github`).

### CI file(s)

none

### CI triggers

not applicable

### CI does

not applicable

### Matrix

not applicable

### Action pinning

not applicable

### Caching

not applicable

### Test runner invocation

not applicable

### Pitfalls observed

zero CI surface on an Anthropic-owned, 7.7k-star, public marketplace. No manifest validation, no schema check, no command-markdown frontmatter lint. All quality control appears to be review-time on PRs. Branch list shows auto-generated branches like `claude/fix-script-integrity-wwwVc` — suggests some sort of external bot/agent-driven workflow operates on the repo but runs outside its own `.github/workflows`.

## 14. Release automation

### `release.yml` (or equivalent) present

no

### Release trigger

not applicable

### Automation shape

not applicable — no releases, no tags, no CHANGELOG.

### Tag-sanity gates

not applicable

### Release creation mechanism

not applicable

### Draft releases

not applicable

### CHANGELOG parsing

not applicable

### Pitfalls observed

confirms the "tip-of-main install" posture — Cowork pulls live; there is no released artifact.

## 15. Marketplace validation

### Validation workflow present

no

### Validator

not applicable

### Trigger

not applicable

### Frontmatter validation

not applicable

### Hooks.json validation

not applicable

### Pitfalls observed

given the manual-version-bump / no-CI posture, nothing prevents malformed JSON from landing on main. The only guardrail is manual PR review.

## 16. Documentation

### `README.md` at repo root

present (~10.7 KB — thorough marketplace overview, install snippets, plugin matrix, MCP provider table, "Making Them Yours" customization section, "Contributing" subsection)

### `README.md` per plugin

mixed — `investment-banking/README.md`, `claude-in-office/README.md`, `partner-built/lseg/README.md`, `partner-built/spglobal/README.md` present; `financial-analysis`, `equity-research`, `private-equity`, `wealth-management` have no per-plugin README.

### `CHANGELOG.md`

absent

### `architecture.md`

absent

### `CLAUDE.md`

at repo root — but content is sparse (~1.5 KB, generic "repo structure + plugin layout + development workflow" scaffolding; references `mcp/` and `mcp-categories.json` paths that don't actually exist in the current tree — stale template). No per-plugin CLAUDE.md.

### Community health files

none (no SECURITY.md, no CONTRIBUTING.md, no CODE_OF_CONDUCT.md at repo root). README has a "Contributing" subsection with three-item fork-and-PR guidance.

### LICENSE

present (Apache-2.0 at repo root, ~11.4 KB); `partner-built/spglobal/LICENSE` also present (Apache-2.0 declared explicitly in its plugin.json); `financial-analysis/skills/skill-creator/LICENSE.txt` also present.

### Badges / status indicators

absent (no CI badge because no CI; no release badge because no releases).

### Pitfalls observed

root CLAUDE.md is stale — references `mcp/` and `mcp-categories.json` that don't exist, and documents a template scaffolding layout that no plugin follows (the actual pattern is `.mcp.json` at plugin root, no `mcp/` directory, no `mcp-categories.json`). Running off this CLAUDE.md would mislead. Per-plugin docs are inconsistent — four of eight plugins have a README; half don't.

## 17. Novel axes

- **Plaintext user-config via gitignored `.local.md` convention** — `investment-banking/.claude/investment-banking.local.md.example` ships a YAML-body markdown template the user copies to `.local.md` (gitignored per the plugin's `.gitignore`) to encode coverage, sectors, deal size, active mandates. Skills read this file at runtime. This is user configuration implemented entirely as file convention + skill prose — no `userConfig`, no `${user_config.KEY}` substitution, no harness involvement. Candidate axis: "file-convention user config" as an alternative pattern to manifest-declared `userConfig`.

- **Partner-built namespace carving** — the marketplace mixes first-party (Anthropic-authored) and third-party (partner-authored) plugins using a `./partner-built/<partner>/` directory convention. No manifest-level marker distinguishes them; the convention is purely filesystem-path-based. `sp-global` advertises its own `repository: https://github.com/kensho-technologies/spglobal-agent-skills`, suggesting the tree here is a vendored copy. Candidate axis: "in-repo partner-built vendoring" as a provenance pattern for aggregator marketplaces.

- **External HTTPS MCP as the dependency surface** — all 11 connectors in `financial-analysis/.mcp.json` are remote HTTP MCP servers hosted by data providers. No local MCP server processes, no stdio MCP, no bundled runtime. This sidesteps the entire local-install story (purpose 6) — the "dependency" is the provider's SaaS uptime and the user's subscription. Candidate axis: "HTTP-MCP-only" plugins as a distinct distribution class.

- **Config-surface in user-side script rather than manifest** — `claude-in-office/scripts/build-manifest.mjs` hand-rolls a `KEYS` schema (regex patterns, hints, `secret: true` flags, required-companion-field validation) for Vertex/Bedrock/gateway customization. It implements `sensitive`-equivalent behavior ("this key goes in every user's manifest; warn if it's per-user sensitive") that the manifest-layer `userConfig` also offers. Candidate axis: "external config schema in admin-run script" — deliberate inversion where the plugin ships tooling for the admin to generate downstream configs rather than being configured itself.

- **Setup-log resumability via Desktop markdown** — `claude-in-office/commands/setup.md` instructs the agent to read `~/Desktop/claude-in-office-setup.md` first and append a `## Run — <timestamp>` section on each invocation, making setup fully resumable across sessions. Contrast with SessionStart-based context-loading (which this repo never uses): resumption state lives in a user-visible file the human can inspect and share. Candidate axis: "user-visible markdown as workflow state".

- **Empty-scaffold hooks** — five plugins carry a `hooks/hooks.json` with empty content (`{}` or `[]`). Either template residue or a placeholder telegraphing "this is where hooks would go if you added them". Candidate axis: "template-scaffolded but unused component directories" as either an anti-pattern (dead files) or a deliberate extension-point convention.

## 18. Gaps

### CLAUDE.md staleness root cause

root `CLAUDE.md` describes a `mcp/` + `mcp-categories.json` structure that's absent from the tree. Could not determine whether this is (a) a generic template copied from an older repo and never updated, (b) deliberate future-state, or (c) reference to a prior refactor. Commit history on `CLAUDE.md` would resolve.

### Why `investment-banking` is at 0.2.0 while peers sit at 0.1.0

no CHANGELOG, no release notes, no tags — the single bump reason isn't recoverable without a git-log dive on `investment-banking/.claude-plugin/plugin.json`.

### External bot branches

branch list contains `claude/fix-script-integrity-wwwVc` and `claude/slack-update-readme-plugin-submission-jvRwz` style branches; the PR-creating agent runs outside the repo (no workflow file sources it here). Which agent/bot creates these, whether they have a schedule, and whether any of them perform validation isn't visible from repo contents.

### Partner-built vendoring sync mechanism

`sp-global/plugin.json` lists `repository: github.com/kensho-technologies/spglobal-agent-skills` — whether the vendored copy under `./partner-built/spglobal/` is manually pulled or scripted isn't visible in this repo. No `git submodule`, no subtree hints in README.

### Why `hooks.json` files are empty

no documentation explains their presence; could be scaffolding from a template, forward-compat, or residual. Would need to correlate plugin creation commits against the "template" state to tell.

### Cowork-vs-Code runtime behavior differences

README frames this as "Built for Claude Cowork, also compatible with Claude Code." The reference patterns observed (no hooks, no SessionStart, no `userConfig`, no release pipeline, tip-of-main install) are more aligned with Cowork's managed-install model than with Claude Code's local-plugin lifecycle. Whether the Cowork harness imposes different constraints (e.g., no hooks support, no binary distribution) would contextualize every "absent" finding above — resolves only with Cowork's plugin-runtime docs.
