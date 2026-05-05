# Sample

Mirrors of `https://github.com/anthropics/financial-services-plugins`. Marketplace of Claude for Financial Services plugins (investment banking, equity research, private equity, wealth management, plus an Office-add-in admin setup plugin) built primarily for Claude Cowork, also compatible with Claude Code. 7,700 stars; default branch `main`; last commit 2026-04-17 (`356f09fe feat(manifest): add inference_headers config key (#68)`); 8 plugins (5 Anthropic-built core/function, 2 partner-built, 1 Office add-in admin tool).

## Marketplace manifest layout

### Multi-plugin owned-aggregator marketplace

Single `.claude-plugin/marketplace.json` at repo root (2,025 bytes). Top-level shape is `{ name, owner: {name}, plugins: [...] }` — no `metadata` wrapper, no top-level `description`, no `version`. 8 plugins: 5 Anthropic-authored at repo root, 2 partner-built under `./partner-built/`, 1 Office add-in admin tool at `./claude-in-office`. No `$schema` field declared.

### Top-level `metadata` wrapper variants

Flat top-level fields only — `name`, `owner: {name}`, `plugins: [...]`. No `metadata` wrapper, no top-level `description`, no `version`. `metadata.pluginRoot` absent.

## Plugin source binding

### Relative source pointing to subdirectory

Every entry uses `"source": "./<dir>"` — five at repo root (`./financial-analysis`, `./investment-banking`, `./equity-research`, `./private-equity`, `./wealth-management`), two under `./partner-built/` (`./partner-built/lseg`, `./partner-built/spglobal`), one at `./claude-in-office`. Plugin-name/dir mismatch on the S&P Global entry: marketplace key `sp-global`, source directory `./partner-built/spglobal` (no hyphen), and `plugin.json` `name: "sp-global"`.

### `strict` field default

Default (implicit true) — no `strict` key on any entry.

### Vendored-partner subtree

Two plugin entries under `./partner-built/<partner>/` whose code is authored by external partners but lives inside the host repo's tree, with the partner's own LICENSE and author attribution. `sp-global` advertises its own `repository: https://github.com/kensho-technologies/spglobal-agent-skills`, suggesting the tree here is a vendored copy. No manifest-level marker distinguishes first-party from third-party — the convention is purely filesystem-path-based. Sync mechanism (manual pull vs scripted) is not visible from the repo content alone (no `git submodule`, no subtree hints in README).

## Per-plugin discoverability metadata

### No discoverability fields on marketplace entry

Marketplace entries carry only `{name, source, description}`. No `category`, `tags`, or `keywords` at the marketplace-entry level. The `$schema` reference is also absent.

### Keywords-only on plugin.json

`sp-global` declares `keywords` inside its own `plugin.json`; no other plugin does. The keywords surface only via the plugin manifest, not the marketplace entry — category-based browser filters cannot surface the plugin.

## Version coordination

### Single source of truth (`plugin.json` only)

Each plugin carries its own `version`; marketplace entries carry no version. Observed: `financial-analysis` 0.1.0, `investment-banking` 0.2.0, `equity-research` 0.1.0, `private-equity` 0.1.0, `wealth-management` 0.1.0, `lseg` 1.0.0, `sp-global` 1.0.0, `claude-in-office` 0.1.0.

### No plugin-level version

`version` fields are effectively cosmetic — nothing verifies bump-on-change, nothing tags, nothing releases. Plugins ship without release discipline; a breaking change could land at `0.1.0` HEAD without any version bump. `investment-banking` is at 0.2.0 while peers sit at 0.1.0; the single bump reason is not recoverable without a git-log dive on `investment-banking/.claude-plugin/plugin.json` (no CHANGELOG, no release notes, no tags).

## Channel distribution

### No pinning surface

No tags, no release branches, no marketplace channel. README install snippets use bare `plugin@financial-services-plugins`, no ref. Any consumer implicitly tracks `main` HEAD — `claude plugin install financial-analysis@financial-services-plugins` resolves against current main.

## Tag and release lifecycle

### No tags at all

`git/tags` returns 0 entries. No release branching — branch list shows `main` plus feature branches with `author/topic` convention (`manar/inference-headers`, `aperlov/azure-foundry-manifest-keys`, `cxl/remove-yfinance`). No pre-release suffixes, no dev-counter scheme. Recent 5 commits on main never bump `version` fields. Branch list also shows auto-generated branches like `claude/fix-script-integrity-wwwVc` and `claude/slack-update-readme-plugin-submission-jvRwz`-style, suggesting an external bot/agent operates on the repo but runs outside its own `.github/workflows`.

## Plugin-component registration

### Default convention discovery

Every Anthropic-built `plugin.json` has only `{name, version, description, author}`. Component wiring relies on the default-discovery conventions for `commands/`, `skills/<name>/SKILL.md`, `hooks/hooks.json`, and `.mcp.json`.

### Inline `mcpServers` definition in `plugin.json`

`sp-global` adds `mcpServers` inline (an object with a single `spglobal` HTTP server) despite also having `.mcp.json` at its plugin root — redundant declarations, two sources of truth.

### Empty hooks scaffolding

Five Anthropic-built plugins ship `hooks/hooks.json` files with empty content (`{}` or `[]`) — register zero hooks. Scaffolding present, behavior absent. Partner and `claude-in-office` plugins have no `hooks/` dir at all. Either remnants of a template, forward-compat stubs, or scaffolding for user customization; nothing in README or CLAUDE.md explains their presence.

## Component composition

### Skills (universal)

Every plugin except `claude-in-office` ships skills.

### Commands

Every plugin ships commands.

### MCP servers

`financial-analysis/.mcp.json` declares 11 servers; `partner-built/lseg/.mcp.json` declares 1; `partner-built/spglobal/.mcp.json` declares 1. `investment-banking/.mcp.json` is an empty `{"mcpServers": {}}`. All 11 connectors in `financial-analysis/.mcp.json` are remote HTTP MCP servers hosted by data providers — no local MCP server processes, no stdio MCP, no bundled runtime.

### Composition shapes

Five Anthropic-built plugins follow a "Skills + commands + empty hooks scaffolding" composition. `financial-analysis` adds an MCP-only payload (11 HTTP MCP servers in `.mcp.json`). `claude-in-office` is the outlier — Skills + commands plus user-side admin tooling (`scripts/build-manifest.mjs`, `examples/python-bootstrap/` FastAPI reference server) outside the plugin component surface.

## Server runtime (MCP)

### Remote HTTP MCP

All 11 connectors in `financial-analysis/.mcp.json` are remote HTTP MCP servers hosted by data providers. No local MCP server processes, no stdio MCP, no bundled runtime. The "dependency" is the provider's SaaS uptime and the user's subscription. `partner-built/lseg` and `partner-built/spglobal` similarly use remote HTTP endpoints.

## Bin entry mechanism

### No bin entry / direct invocation

No `bin/` directory in any plugin. The closest analog is `claude-in-office/scripts/build-manifest.mjs`, invoked from command markdown via `node scripts/build-manifest.mjs ...`, not registered as a plugin bin entry. The script lives alongside commands but outside the plugin bin surface.

## Dependency installation

### No managed install — pure shell/markdown

The five Anthropic-built core/function plugins and the two partner plugins ship pure markdown + JSON + HTTP MCP URLs, no runtime deps. `claude-in-office` is partially applicable: it ships a Node `scripts/build-manifest.mjs` (plain `import` from `node:fs`, no `package.json`) and a Python FastAPI reference server under `examples/python-bootstrap/` with its own `requirements.txt`. The setup command (`commands/setup.md`) checks `node --version` and asks the user to install Node via their package manager before the command shells out to `node`/`npx`. The Python example is a reference server the admin runs out-of-band on their own infra, not installed into `${CLAUDE_PLUGIN_DATA}` or `${CLAUDE_PLUGIN_ROOT}`. The bundled `build-manifest.mjs` uses `console.warn`/`console.error` + non-zero `process.exit(1)` for bad input and missing URL slots.

## User configuration and authentication

### Gitignored `.local.md` convention

`investment-banking/.claude/investment-banking.local.md.example` ships a YAML-body markdown template the user copies to `.local.md` (gitignored per the plugin's `.gitignore`) to encode coverage/sector/deal preferences. Skills read this file at runtime via prose instructions, not a harness substitution mechanism. No `userConfig`, no `${user_config.KEY}` substitution, no harness involvement.

### External schema in admin-run script

`claude-in-office/scripts/build-manifest.mjs` hand-rolls a `KEYS` object with regex patterns, hints, and a `secret` flag for Vertex/Bedrock/gateway config — a parallel, hand-rolled config-surface system that does what `userConfig` exists for, but lives outside the plugin metadata layer. `gateway_token: { secret: true }` flags secrets and emits a warning when those are used in the manifest (which is org-wide), steering the admin toward per-user extension attrs instead. Plugin metadata layer is bypassed entirely; the plugin ships tooling for the admin to generate downstream configs rather than being configured itself.

## Tool-use enforcement

### No enforcement (observational only)

Every `hooks.json` that exists is empty (`{}` or `[]`). No PreToolUse, PostToolUse, PermissionRequest, or PermissionDenied hooks across any plugin. All five Anthropic-built plugins ship a `hooks/hooks.json` file but register zero hooks — the scaffolding is present, the behavior is absent.

## Session context loading

### No session-context loading

No SessionStart hook, no UserPromptSubmit hook for context. No `hookSpecificOutput.additionalContext` observed. Plugins rely entirely on skills' frontmatter `description` matching to surface domain knowledge when relevant.

### File-backed context written at SessionStart

`claude-in-office/commands/setup.md` instructs the agent to read `~/Desktop/claude-in-office-setup.md` first and append a `## Run — <timestamp>` section on each invocation, making setup fully resumable across sessions. Resumption state lives in a user-visible plain markdown file the human can inspect and share. (Note: not technically a SessionStart hook — the file-backed context pattern is invoked by the user running the setup command.)

## Live monitoring

### `monitors.json` absent

No `monitors.json` in any plugin.

## Plugin-to-plugin coordination

### Implicit prose-only dependency

No `plugin.json` declares a `dependencies` field. README states "Start with **financial analysis** — the core plugin that provides shared modeling tools and all MCP data connectors" but enforces this only as prose, not as a manifest dependency. `investment-banking` etc. have an empty `.mcp.json` and skills that assume `financial-analysis`'s MCP servers are loaded, but nothing in the metadata expresses that. If a user installs `investment-banking` without `financial-analysis`, the skills will still load but reference MCP tools that aren't configured.

## Testing

### No tests

No `tests/` directory anywhere, no pytest config, no jest/vitest config.

## CI workflow shape

### No CI

`.github/` directory does not exist at repo root (GitHub API returns 404 for `/contents/.github`). Zero CI surface on a 7.7k-star Anthropic-owned public marketplace. No manifest validation, no schema check, no command-markdown frontmatter lint. All quality control appears to be review-time on PRs.

## Marketplace validation

### No validation

No CI, no `validate.yml`, no pre-commit hook, no `claude plugin validate` invocation. Nothing prevents malformed JSON from landing on main; the only guardrail is manual PR review.

## Release automation

### No release automation / manual

No `release.yml`, no tags, no CHANGELOG.md, no GitHub releases. Confirms the "tip-of-main install" posture — Cowork pulls live; there is no released artifact.

## Documentation surface

### Comprehensive single README + ad-hoc CLAUDE.md

Repo-root `README.md` is ~10.7 KB — thorough marketplace overview, install snippets, plugin matrix, MCP provider table, "Making Them Yours" customization section, "Contributing" subsection. Repo-root `CLAUDE.md` is sparse (~1.5 KB) — generic "repo structure + plugin layout + development workflow" scaffolding referencing `mcp/` and `mcp-categories.json` paths that don't actually exist in the current tree (stale template). No per-plugin `CLAUDE.md`. No `CHANGELOG.md`, no `architecture.md` at root.

### Stale `CLAUDE.md`

Repo-root `CLAUDE.md` references a `mcp/` directory and an `mcp-categories.json` file that don't exist in the current tree, and documents a template scaffolding layout that no plugin follows (the actual pattern is `.mcp.json` at plugin root, no `mcp/` directory, no `mcp-categories.json`). Running off this CLAUDE.md would mislead.

### Per-plugin README mixed coverage

Per-plugin READMEs uneven: `investment-banking/README.md`, `claude-in-office/README.md`, `partner-built/lseg/README.md`, `partner-built/spglobal/README.md` present; `financial-analysis`, `equity-research`, `private-equity`, `wealth-management` have no per-plugin README — four of eight plugins ship one, half don't.

## License declaration

### Single repo-level license

`LICENSE` (Apache-2.0) at repo root, ~11.4 KB. `partner-built/spglobal/LICENSE` also present (Apache-2.0 declared explicitly in its plugin.json); `financial-analysis/skills/skill-creator/LICENSE.txt` also present.

## Community health files

### Bare minimum (LICENSE only)

`LICENSE` at repo root. No `SECURITY.md`, no `CONTRIBUTING.md`, no `CODE_OF_CONDUCT.md`. README has a "Contributing" subsection with three-item fork-and-PR guidance.
