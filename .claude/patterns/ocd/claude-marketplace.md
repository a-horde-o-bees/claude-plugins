# Claude Marketplace

Canonical shape for a Claude Code plugin marketplace repository. Organized by purpose — what a marketplace builder is trying to accomplish — rather than by system feature. Each purpose section composites the mechanisms, adoption signals, and pitfalls that apply, so a reader can locate all relevant guidance for their current decision in one place.

Derived from three overlapping samples of public repos:

- **Primary sample (18)** — Anthropic-owned and community marketplaces satisfying marketplace manifest + Python + tests + multi-branch or tagged discipline filters.
- **Dependency-management sample (20)** — plugins with real runtime dependency management (Python venvs, Node `node_modules`, binary downloads). Used for dependency-installation guidance.
- **Bin-wrapper sub-sample (23)** — plugins shipping a `bin/` directory, discovered via GitHub code search on `CLAUDE_PLUGIN_ROOT path:bin`. Used for bin-wrapper guidance.

Repos appear in multiple samples where filters overlap. Full lists in *References*.

## Legend and conventions

**Docs column:**

- ★ — path explicitly prescribed or recommended in [plugins-reference](https://code.claude.com/docs/en/plugins-reference) or [plugin-marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- ☆ — docs shown as valid without endorsement
- (blank) — docs silent; adoption is the only available signal

**Denominator rule.** Each table's denominator is the applicable subset for that purpose, not the full sample. When a purpose does not apply universally, applicability is named in the section's preamble. Adoption counts are always "adoption where applicable."

When the ★ path and the highest-adoption path disagree, the conflict is flagged explicitly in the section narrative.

## When to use

- **This pattern** — a repository publishing one or more Claude Code plugins through a `.claude-plugin/marketplace.json` manifest at its root.
- **Adaptation: single-plugin repo** — drop the `plugins/` wrapper; the plugin lives at the repo root with `source: "./"`.
- **Adaptation: curated third-party aggregator** — plugin dirs hold only metadata; `source` pins external repos by `sha`. Different discipline (scheduled SHA-bump PRs, `strict: false` entries).
- **Adaptation: LSP-wrapper plugin** — thin plugin whose entire purpose is configuring a language server via `.lsp.json`. No skills, agents, or commands; binary must be pre-installed by user. Anthropic ships 13 such plugins (`pyright-lsp`, `typescript-lsp`, `rust-analyzer-lsp`, etc.) in `claude-plugins-official`.
- **Not for MCP-only repos** — standalone MCP servers distribute via npm or PyPI, not the marketplace manifest.

## Canonical shape

```text
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Single manifest at this exact path
├── plugins/
│   └── <plugin>/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin name and version live here
│       ├── skills/ commands/ agents/ hooks/ bin/
│       ├── monitors/              # If applicable (v2.1.105+)
│       ├── .mcp.json .lsp.json   # If applicable
│       ├── README.md LICENSE
│       └── architecture.md       # Plugin-level design (optional)
├── tests/                        # At repo root
│   ├── integration/
│   └── plugins/<plugin>/         # Per-plugin nesting (optional; precedent exists)
├── scripts/
│   ├── test.sh                   # Wrapper around the project's test runner
│   └── release.sh                # Optional — tag-cut automation
├── .github/
│   └── workflows/
│       ├── ci.yml                # Push/PR pytest
│       ├── release.yml           # Tag-triggered release (optional)
│       └── validate.yml          # Manifest linting (optional)
├── pyproject.toml                # Python deps + pytest config
├── README.md
├── CHANGELOG.md                  # Optional
├── LICENSE
├── architecture.md               # Optional
└── CLAUDE.md                     # Agent procedures (optional)
```

## Purposes

### Marketplace discoverability

Make the marketplace catalog locatable, interpretable, and safely named — at both the marketplace level and the individual plugin-entry level.

#### Manifest layout

Where the marketplace catalog lives. Determines whether Claude Code can find it via the documented default path.

| Path | Docs | Adoption |
|---|---|---|
| Single `.claude-plugin/marketplace.json` at repo root | | 17/18 |
| Multiple `marketplace.json` files at different paths | | 1/18 |

Docs do not prescribe a file count. Community convention is single.

#### Marketplace-level metadata

How the marketplace describes itself in the manifest.

| Path | Docs | Adoption |
|---|---|---|
| `metadata: { description, version, pluginRoot }` wrapper | ☆ | 12/21 |
| Top-level `description` (no wrapper) | | 6/21 (incl. `anthropics/claude-plugins-official`) |
| No marketplace-level description | | 3/21 |

Both forms work; the `metadata` wrapper is the newer schema shape. Anthropic's flagship `claude-plugins-official` still uses top-level `description` — schema migration in progress.

`metadata.pluginRoot` is docs-available (prepends a base dir to relative plugin sources so entries can write `"source": "formatter"` instead of `"source": "./plugins/formatter"`) but 0/21 adopt it. Writing the full relative path is the universal convention.

#### Per-plugin discoverability fields

Metadata on individual plugin entries that aids user discovery.

| Path | Adoption |
|---|---|
| `category` only | 5/21 |
| `category` + `tags` | 5/21 |
| `keywords` only (in `plugin.json`) | 7/21 |
| `category` + `tags` + `keywords` | 1/21 |
| No discoverability metadata | 4/21 |

Docs list all three fields without distinguishing semantics. Anthropic's own marketplaces split: `claude-plugins-official` uses `category` alone, `life-sciences` and `healthcare` use `category + tags`. Emerging convention: `tags: ["community-managed"]` as a signal-flag distinct from content-topic tags.

#### `$schema` reference

| Path | Docs | Adoption |
|---|---|---|
| `"$schema": "https://anthropic.com/claude-code/marketplace.schema.json"` | | ~6/54 |
| No `$schema` | | ~48/54 |

Cosmetic — enables editor autocomplete. The URL is emitted by Anthropic's own tooling but not documented. Not required, but all six adopters are high-signal or Anthropic-aligned repos (`claude-plugins-official`, `hihol-labs/idea-to-deploy`, `hwuiwon/autotune`, `a3lem/my-claude-plugins`, `lukasmalkmus/moneymoney`, `jmylchreest/aide`).

#### Pitfalls

**Reserved marketplace names reject publishing.** ★ Docs enumerate a blocklist: `claude-code-marketplace`, `claude-code-plugins`, `claude-plugins-official`, `anthropic-marketplace`, `anthropic-plugins`, `agent-skills`, `knowledge-work-plugins`, `life-sciences`. Names that impersonate official marketplaces are also blocked. Picking one of these silently fails at publish time.

**Non-schema fields render nowhere.** Some repos set fields like `images: [url]` or `screenshots: [url]` on plugin entries. Claude Code does not parse these — they exist only for future compatibility or external renderers. Adopt with the understanding they produce no current UI affordance.

**Marketplace state is per-user, not per-worktree.** `~/.claude/plugins/known_marketplaces.json` is global — switching worktrees does not isolate marketplace config. Authors testing installs across forks or branches share one registration namespace.

**Enterprise consumers pin via `strictKnownMarketplaces`.** Managed-settings consumers can pin marketplaces by `owner/repo@ref`. Repo renames or branch deletions break every managed deployment silently. Design stable refs (main stable, semver tags) with this in mind.

### Plugin source binding

How a marketplace entry points at plugin source code and claims authority over plugin identity.

#### Source format

| Path | Docs | Adoption |
|---|---|---|
| Relative string (`"./<dir>"`) | ☆ | 14/18 |
| `url` + `sha` object | ☆ | 2/18 |
| `github` object | ☆ | 1/18 |
| `npm` object | ☆ | 1/18 |
| `git-subdir` as default source | ☆ | 0/18 (appears only as per-entry pinning in aggregator catalogs) |

Docs show all shapes as valid without endorsing one. Couples with version authority (below): relative sources canonically get `version` in the marketplace entry; other sources get it in `plugin.json`.

#### Authority — `strict`

Whether the marketplace entry or `plugin.json` is authoritative for the plugin definition.

| Path | Docs | Adoption |
|---|---|---|
| `strict: true` (default — `plugin.json` authoritative) | ☆ | 16/21 (default, implicit) + 1/21 (explicit) |
| `strict: false` — marketplace entry authoritative, `plugin.json` ignored | ☆ | 4/21 |

Setting `strict: false` lets one physical plugin source directory appear as multiple marketplace entries with different skill selections. Anthropic's `life-sciences` and `healthcare` use this to expose five or three subskills respectively as separate catalog entries — each `strict: false` entry carries its own `skills: ["./skill-name"]` list.

**Hybrid carving variant** — `anthropics/healthcare` additionally mixes `strict: false` skill-carving plugins with conventional `strict: true` MCP-only plugins in the same manifest. The skill-carved plugins have no `plugin.json` file at all — all metadata lives in the marketplace entry, plus `metadata.version` at the marketplace level. This "metadata-only-plugin" form is docs-valid but worth naming: it exists only as marketplace-entry data, with the physical directory containing only content files.

#### Version authority

Single source of truth for a plugin's version. Applicable to repos that declare a version somewhere. 4 aggregator marketplaces declare no version anywhere and are excluded.

| Path | Docs | Adoption |
|---|---|---|
| `plugin.json` only (for `github`/`url`/`git-subdir`/`npm` sources) | ★ | 10/14 |
| Marketplace entry only (for relative-path sources) | ★ | 3/14 |
| Both (duplicated) | | 1/14 primary sample; ~20/54 across the full sample |

Docs split the recommendation by source type: *"For relative-path plugins, set the version in the marketplace entry. For all other plugin sources, set it in the plugin manifest."* Community majority puts version in `plugin.json` regardless of source shape — an observed docs-vs-adoption conflict that this repo resolves by following the majority.

#### Pitfalls

**Version duplication is common, and live drift is frequent.** Plugin-reference documents "plugin manifest always wins silently" when both locations carry the field. Across the 54-repo sample, version fields live in 2-5 files per repo (most commonly `plugin.json` + marketplace entry; also `package.json`, `pyproject.toml`, `VERSION`, `Cargo.toml`, per-harness manifests). Approximately 20/54 repos duplicate across at least two files. Live drift — mismatched values at research time — was observed in ~9/54 (AgentBuildersApp, marioGusmao, ShaheerKhawaja, Chulf58, raphaelchristi, stellarlinkco, CronusL-1141, damionrashford, anthril). Enforcement mechanisms (pre-commit scripts, CI version-sync checks) exist in ~6/54; manual discipline is the norm and routinely fails.

**Relative-path sources require a git-based marketplace.** Users adding the marketplace via direct URL to `marketplace.json` (not git clone) get resolution failures on relative paths. Use explicit `github` + `ref` sources if both install paths need to work.

### Channel distribution

Let users subscribe to stable vs dev channels of the same plugin.

| Path | Docs | Adoption |
|---|---|---|
| Two separate marketplaces with different `name` values, each pinning a different ref/SHA | ★ | 0/18 |
| No channel split declared; users pin via CLI `@ref` | | 18/18 |

**Docs vs adoption conflict.** The plugin-marketplaces doc explicitly recommends two marketplaces with different `name` values for stable/latest channels (worked example: `stable-tools` + `latest-tools`). Zero sample repos implement this — community treats `@ref` pinning as the de-facto mechanism. Plugin-name collisions between channels (each `plugin.json` carries the same `name` unless authors ship separate plugin files) explain why community doesn't adopt. For portfolio signal, the docs pattern is the formal choice; for real-world compatibility, most users expect the `@ref` pattern.

### Multi-harness distribution

Ship one codebase that serves multiple AI-coding-assistant ecosystems from a single source tree — Claude Code + Cursor + Codex CLI + OpenCode + Gemini. Applicability: plugins whose content (skills, agents, hooks) is substantially portable and whose authors want one git repo to be the canonical distribution for all consumers.

Observed in ~6/54 repos: ship (`.claude-plugin/` + `.cursor-plugin/` + `.codex/config.toml`), jmylchreest/aide (Claude marketplace + `@jmylchreest/aide-plugin` npm + Codex CLI), REPOZY/superpowers-optimized (4 hook schemas: claude/codex/cursor/opencode), SkinnnyJay/wiki-llm (Claude + Cursor manifests), ShaheerKhawaja/ProductionOS (Claude + `.codex-plugin/plugin.json`), stellarlinkco/myclaude, Chachamaru127/claude-code-harness (skills/ + skills-codex/ + codex/ + opencode/ cross-runtime mirrors), brunoborges/agent-plugins (dual-published `.claude-plugin/` + `.github/plugin/` at aggregator level).

Docs-silent. No canonical multi-harness convention exists; each repo invents its own layout.

#### Mechanisms observed

- **Parallel manifest files** — separate `plugin.json` variants per harness, authored by hand. Drift between them is routine (often observed at research time).
- **Content mirroring** — `skills/` + `skills-codex/` + `opencode/` as shadow trees, synced by a script (e.g., Chachamaru127's drift-gate CI).
- **Per-harness hook-event schemas** — hook config files differ: `hooks.json` for Claude, Codex-specific hook formats for Codex. Requires maintaining separate files.
- **Runtime-dispatched output schemas** — a single hook script branches on `$CURSOR_PLUGIN_ROOT` vs `$CLAUDE_PLUGIN_ROOT` and emits schema-appropriate JSON (ship's SessionStart hook).
- **Polyglot runtime stubs** — `.cmd` + bash pair invoking the same hook script on Windows/POSIX, extensionless filenames to avoid auto-detection (REPOZY's `run-hook.cmd`).

#### Pitfalls

**Manifest drift across harnesses is systemic.** Six repos observed at research time had version or description drift between their Claude manifest and Cursor/Codex/etc. counterparts. Without automated sync (1/6 have it), drift accumulates over time. Declare one manifest as authoritative and generate the others, or accept drift as routine.

**Hook-event schemas diverge and cannot be unified.** Claude Code, Cursor, and Codex define different hook event vocabularies and JSON shapes. There is no cross-harness hook schema — authors either maintain separate hook files or live with per-harness behavioral differences.

**Cross-harness installability is not equivalent.** `--plugin-dir` dev mode, marketplace install, and per-harness install each have different path resolution semantics. Test install on every harness before releasing.

### Version control and release cadence

Branching discipline, tag placement, and pre-release signaling.

#### Default branch

| Path | Docs | Adoption |
|---|---|---|
| `main` | | 16/18 |
| `master` | | 2/18 |

Docs silent. Convention is `main`.

#### Tag placement

Where semver tags annotate commits. Docs prescribe semver (`MAJOR.MINOR.PATCH`) for tags but not where to place them. Applicable to repos that tag — 4 untagged aggregators excluded.

| Path | Docs | Adoption |
|---|---|---|
| Tags on `main` | | 14/14 |
| Tags on `release/*` branches (owning the release cut) | | 0/14 |

#### Release branching

Applicable to repos with a release cadence. 4 aggregators excluded.

| Path | Docs | Adoption |
|---|---|---|
| Tag on `main` directly; no release branches | | 13/14 |
| Release-prep / codename branches that do NOT own tags (tags still on main) | | 1/14 (Chachamaru127) |

Docs silent. Community norm is tag-on-main. Chachamaru127/claude-code-harness uses `release/vX.Y.0-<codename>` branches as historical prep snapshots, but tags actually land on main and the release branches sit behind main at tag time. No sampled repo uses `release/*` branches as the canonical tag-bearing surface. The dev-counter-on-main + semver-on-release-branch split (this project's pattern) is unobserved in the sample but not in conflict with any convention — defensible as an original choice.

#### Pre-release suffixes

Docs call out pre-release suffixes: *"Use pre-release versions like `2.0.0-beta.1` for testing."* Applicable to repos that tag.

| Path | Docs | Adoption |
|---|---|---|
| Plain semver only (`vX.Y.Z`) | ★ | 12/14 |
| Pre-release suffixes (`-rc`, `-beta`, `-alpha`) | ★ | 2/14 |

Both paths are docs-prescribed: plain semver for releases, pre-release suffixes for testing versions. Use either as appropriate.

#### Pitfalls

**Pre-commit version bump skipped with `--no-verify`.** When `main` uses a dev build counter (`0.0.z`) for cache invalidation, the bump usually rides a pre-commit hook. `git commit --no-verify` silently skips the bump, leaving Claude Code's reload detection stale.

**Branch names that shadow tag names.** Creating a branch `v0.1.0` and a tag `v0.1.0` produces ambiguous git resolution. Use `release/0.1` for branches and reserve `v*` for tags.

**Background auto-updates run without git credentials.** Private-repo plugins require `GITHUB_TOKEN` or equivalent exported in the user's shell; otherwise silent update failures accumulate.

### Plugin-component registration

How plugins declare their skills, agents, commands, MCP servers, and LSP servers in `plugin.json` — inline, via external file, or via default-directory discovery.

| Path | Docs | Adoption |
|---|---|---|
| Default directory discovery (minimal `plugin.json`, components found under `skills/`, `agents/`, etc.) | ☆ | ~35/54 |
| Explicit default path arrays (`"skills": ["./skills/"]`) | ☆ | ~12/54 |
| Inline configuration objects (`mcpServers: {…}` in `plugin.json`) | ☆ | ~8/54 |
| External file reference (`"mcpServers": "./.mcp.json"`) | ☆ | ~3/54 |

Default discovery is the prevailing pattern. Explicit path arrays — previously believed rare — are the second-most-common, used when authors want the plugin.json to be self-documenting about which files are components (BrandCast-Signage, Chachamaru127, marioGusmao, rn-dev-agent, trader-os, moneymoney, aide). External file reference is the cleanest option when the component config is large enough to warrant its own file — one source of truth, easier to diff. Inline is fine when the config is short.

#### Agent frontmatter

Plugin-shipped agents under `agents/` use YAML frontmatter with `name`, `description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`, `background`, `isolation`.

`hooks`, `mcpServers`, `permissionMode` are **not** supported in plugin-shipped agent frontmatter — these are stripped for security. A plugin cannot ship an agent that declares its own hook handlers or MCP servers.

The `tools:` list accepts the same permission-rule syntax as settings.json `permissions.allow` — `Bash(uv run *)`, `Bash(jq *)` — restricting an agent's shell access to a whitelist with glob patterns. Observed in damionrashford/trader-os's quant-analyst agent and skullninja/coco-workflow's skill `allowed-tools` (rare — 2/54).

**Non-canonical frontmatter fields observed in the wild.** Research surfaced several fields that are not in the docs schema but appear in community agents. Some may be silently ignored by Claude Code; some may require specific versions; some are consumer-specific (Cowork, HumanLayer). Authors adopt them at their own risk until docs catch up:

- `memory: project` or `memory: user` — BULDEE, Chachamaru127, damionrashford, Lykhoyda.
- `background: true` — AgentBuildersApp, damionrashford.
- `isolation: worktree` — 7+ repos (documented).
- `effort: xhigh` — Chachamaru127 (Claude Code v2.1.111+).
- `stakes: low|medium|high` — ShaheerKhawaja (HumanLayer-borrowed vocabulary).
- `subagent_type: <plugin>:<name>` — ShaheerKhawaja (namespacing extension).
- `user-invocable: false` — knowledge-work-plugins/productivity (Cowork-specific).
- `context: fork` — HiH-DimaN, anthril (sub-skill dispatch).
- `permissionMode: acceptEdits` — raphaelchristi (relies on this despite docs saying stripped — verify current Claude Code behavior).
- `allowed-prompts` — a3lem (undocumented).
- `disable-model-invocation: true` — HiH-DimaN (prevents the model from invoking the agent without user confirmation).

### Description as the discovery surface

Claude Code discovers skills and agents at prompt time by matching the user's intent against each one's frontmatter `description` field. The description is therefore not documentation prose — it is a discovery contract. A skill that does useful work but whose description doesn't surface matching trigger verbs or nouns will not be reached by the model when the user needs it.

#### Explicit discipline

1/54 repos codify description-writing rules explicitly. **CodeAlive-AI/codealive-skills** prescribes concrete targets in its `CLAUDE.md`: length aim 300–500 characters, hard limit 1024, include "concrete trigger verbs/nouns users actually say," and design for many agents in many contexts rather than one session's failure modes. The discipline is explicit because the plugin targets multiple AI hosts (Claude Code + skills.sh + MCP + plugin-bridge) where each host's matcher behaves differently.

Elsewhere in the sample, descriptions vary widely in shape, length, and whether they name a trigger verb. The adoption count is low because most authors don't formalize their rules — not because the discipline is contested.

#### Few-shot patterns in agent descriptions

Agents' `description` field accepts inline `<example>…<commentary>` XML blocks that Claude Code treats as few-shot triggers for its agent-matcher:

- **Lykhoyda/rn-dev-agent** — multi-paragraph YAML literal block with 3 example blocks per agent; matcher reads the full block as a trigger-rich description.
- **anthropics/knowledge-work-plugins** — `partner-built/brand-voice/agents/*.md` uses YAML folded scalar (`>`) with embedded `<example>` blocks.

2–3/54 directly observed — not yet a named convention, but illustrative of the few-shot axis that skill descriptions can also (informally) exploit.

#### Multilingual trigger surface

**HiH-DimaN/idea-to-deploy** embeds bilingual trigger phrases (Russian + English) inside a `## Trigger phrases` heading at the top of each skill's body, extending the matcher's surface area across linguistic populations. 1/54 observed; candidate pattern for plugins targeting multiple user populations.

#### Pitfalls

**Description lacking trigger verbs/nouns doesn't surface.** The matcher works against the description content — a well-documented skill with a vague description ("Handles the Foo domain") won't be found when the user says "add a Foo." Name the verbs users actually say.

**Frontmatter description is effectively one line.** Claude Code's skill metadata layer caps scalar description fields around 1024 characters. Longer content belongs in the body, not the frontmatter — CodeAlive-AI's explicit 1024 hard limit aligns with observed matcher behavior.

### Command and skill frontmatter

Field-level discipline on slash-command and SKILL.md frontmatter. Complements *Description as the discovery surface* above: that subsection covers the matcher mechanism and the description content itself; this one covers the surrounding fields (`name`, `argument-hint`, `allowed-tools`) and their asymmetric handling between command and skill surfaces.

Sample: 14 skill/command files across 9 repos — BULDEE, Chulf58, HiH-DimaN, ZhuBit, lukasmalkmus, anthropics/claude-plugins-official, Kanevry, Vortiago, CodeAlive-AI, damionrashford, NoelClay, SkinnnyJay.

#### Description length regimes

Two clusters:

- **Short commands** — 19-97 chars for task-style commands with explicit invocation. Examples: anthropics/commit (19), SkinnnyJay/query (78), BULDEE/session-init (101).
- **Medium-to-long skills** — 145-847 chars for description-matched skills. Examples: HiH-DimaN/kickstart (145), CodeAlive-AI/context-engine (262), damionrashford/quant-math (847 — heavy trigger-verb enumeration).

No sampled surface exceeds the ★ docs-prescribed 1,536-char display cap (`https://code.claude.com/docs/en/skills#frontmatter-reference` — "the combined `description` and `when_to_use` text is truncated at 1,536 characters").

#### Description framing

9/14 sampled surfaces lead with trigger-verb framing ("Use when the user…", "Activated automatically when…") — ★ matches docs guidance ("Front-load the key use case"). 5/14 use bare "what it does" descriptors — misaligned with docs and leaving the matcher without trigger phrases. The framing split is load-bearing: bare descriptors don't reach users who describe the task by action rather than by domain.

#### `argument-hint` format drift

Four distinct forms observed across 9 argument-taking surfaces:

| Form | Example | Adoption |
|---|---|---|
| Typed angle-bracket (★ docs-prescribed) | `"<folder path>"` | 4/9 |
| Prose description | `project idea or description` | 3/9 |
| Flag-style enumeration | `[--fast\|--standard\|--deep] [--upgrade <tier>]` | 1/9 (Kanevry) |
| Subcommand | `[subcommand]` | 1/9 (damionrashford) |

Only the typed bracket form matches docs examples (`[issue-number]`, `[filename] [format]`). The prose form is legal but inconsistent; agents consuming skill metadata programmatically have to parse two formats.

#### `name:` — command vs skill asymmetry

Commands and skills handle `name:` differently:

- **Commands** — 4/7 omit `name:` (anthropics/commit, anthropics/feature-dev, anthropics/create-plugin, BULDEE/challenge, Kanevry/bootstrap); 2/7 include it (ZhuBit/index, NoelClay/learn); 1/7 has no frontmatter at all. Omission enables Claude Code's directory-based namespacing — the command resolves as `/<plugin>:<command>` from the file path, producing the correct plugin-qualified slash command.
- **SKILL.md** — 8/8 include `name:`. Directory-name fallback exists but authors opt in; skills must survive directory moves, and pinning `name:` keeps identity stable across filesystem layout changes.

The asymmetry is ★ docs-prescribed (skills-reference) and load-bearing: commands benefit from auto-namespacing, skills benefit from pinned identity. 3/4 of the `name:`-omitting commands are in plugin layouts where namespace-from-directory is the right answer.

#### `allowed-tools` syntax variance

Three legal forms observed, plus absence:

| Form | Example | Adoption |
|---|---|---|
| Space-separated plain names | `Read Write Edit Glob Grep` | 2/14 |
| Permission-rule scoped | `Bash(git add:*)`, `Bash(mm accounts *)` | 2/14 |
| YAML array / list | `- Read`, `- Write`, ... | 2/14 |
| Absent | — | 8/14 |

Docs prescribe "a space-separated string or a YAML list." Permission-rule scoping (lukasmalkmus/moneymoney deliberately omits write-verb scopes like `mm transfer` to force confirmation prompts) is a sharper design pattern — scope-limiting as UX. The mixed form within a single field (HiH-DimaN's kickstart has plain tool names alongside `Bash(git:*)` in the same space-separated list) is legal but confusing.

#### Pitfalls

**Setting `name:` on command frontmatter breaks auto-namespacing.** BULDEE/ai-craftsman-superpowers' CHANGELOG v3.3.3 documents the trap: when a command file under `commands/` declares `name:` in its frontmatter, Claude Code uses the literal value as the slash-command name instead of deriving `<plugin>:<command>` from the filename and plugin directory. Autocomplete shows the bare name (e.g. `/setup`) instead of the namespaced form (`/craftsman:setup`). Confirmed by the 4/7 omission pattern across the sample, including Anthropic's own plugins (vercel, metrikia, stripe, commit-commands). Corrective pattern: omit `name:` from command frontmatter. SKILL.md files are distinct — they require `name:` for the skill-matcher.

**Bare "what it does" description loses the discovery surface.** 5/14 of sampled surfaces use bare descriptors naming the domain noun but not the trigger verbs. The matcher works against the description content — a well-documented skill with a vague description ("Handles the Foo domain") won't be found when the user says "add a Foo." Name the verbs users actually say.

**`argument-hint` prose form doesn't round-trip.** Prose hints ("project idea or description") render correctly as autocomplete hints but don't align with docs' typed-bracket convention. Agents parsing skill metadata programmatically have to handle two forms; style drift in docs-consuming tooling follows.

### Dependency installation

Get runtime dependencies — language interpreters, packages, binaries — onto the user's machine before the plugin needs them, and keep them in sync with what the plugin ships. Applies to plugins that run code beyond pure skill content.

Docs prescribe a complete pattern: SessionStart hook installs into `${CLAUDE_PLUGIN_DATA}` using manifest-diff change detection, with a retry-next-session invariant on failure. Plugins-reference quotes: *"a persistent directory for plugin state that survives updates. Use this for installed dependencies such as `node_modules` or Python virtual environments... The recommended pattern compares the bundled manifest against a copy in the data directory and reinstalls when they differ."*

**Sample scope.** 20-repo dependency-management sub-sample (plugins with real runtime dep management).

#### Install location

| Path | Docs | Adoption |
|---|---|---|
| `${CLAUDE_PLUGIN_DATA}` — persistent across plugin updates | ★ | ~12/20 |
| `${CLAUDE_PLUGIN_ROOT}` citing ESM resolution constraints | | ~4/20 |
| Hybrid `${CLAUDE_PLUGIN_DATA}` + symlink back to `${CLAUDE_PLUGIN_ROOT}` | | 2/20 |
| Global-npm / system install | | 2/20 |
| Ad-hoc runtime fetch (`uv run --script`, `uvx`, `npx`) | | 2/20 |
| Third-party shared home-dir (e.g. `~/.root-framework`) | | 1/20 |

Docs prescribe `DATA` because it survives plugin updates. `ROOT` is chosen when language-specific module resolution requires it — most commonly Node ESM, where `node_modules` must sit next to `package.json` in `ROOT` and `NODE_PATH` is silently ignored by ESM `import`. Rationale is explicitly documented in source for Arcanon-hub/arcanon (planning doc + inline comment) and includeHasan/prospect-studio (inline comment in install script) — both cite ESM as the non-optional reason. The hybrid DATA+symlink pattern (Lykhoyda/rn-dev-agent, marioGusmao/codegraph) resolves the tension by installing into DATA and symlinking back for ESM resolution.

#### Change detection

How the install hook decides whether to reinstall on session start.

| Path | Docs | Adoption |
|---|---|---|
| `diff -q` bundled manifest against cached copy | ★ | 12/20 |
| Hash (sha256/md5) comparison | | 4/20 |
| Version file stamp | | 3/20 |
| mtime vs lockfile (weak change detection) | | 1/20 |
| Existence only — misses upgrades | | 3/20 (raphaelchristi, brunoborges, iVintik) |

Docs ship a worked example using `diff -q`. Hashing is functionally equivalent with an extra step per session. Existence-only detection is a defect at the discipline level — upgrades to the bundled manifest silently don't install because the existence check passes on any prior version.

#### Retry-next-session invariant

Docs-prescribed shape: at the end of the hook, if install failed, `rm -f` the cached manifest copy so the next session's change detection sees a mismatch and retries. Without this step, a partial failure poisons the cache — subsequent sessions see a cached manifest matching the bundled one and skip install, leaving the plugin broken until the user clears the cache manually.

#### Failure signaling

How install failure surfaces to the user.

| Path | Docs | Adoption |
|---|---|---|
| Silent retry (exit 0 + `rm -f` cached manifest on failure) | ★ | ~15/20 |
| Silent stderr (default shell behavior, no explicit retry) | | ~4/20 |
| JSON `systemMessage` on stdout | | 1/20 (anthril) |

Docs prescribe silent retry — the worked example's `rm -f` trailing clause restores the cached manifest to a state that the next session's `diff -q` will re-trigger. **No JSON `systemMessage` is emitted by the docs worked example.** Community overwhelmingly follows silent retry (the ★ path above). Emitting a `systemMessage` is a valid extension but is not the prescribed path and appears in only 1/20 sampled repos.

#### Runtime variant

Which language ecosystem the install pattern wraps. Not a choice per se — determined by what the plugin runs — but shapes the concrete install command.

| Variant | Adoption | Representative repos |
|---|---|---|
| Python venv (uv/pip) | ~8/20 | CronusL-1141/AI-company, smcady/Cairn, ZhuBit/cowork-semantic-search |
| Node via npm/bun | ~9/20 | Arcanon-hub/arcanon, ekadetov/llm-wiki, marioGusmao/mg-plugins |
| Prebuilt Go/Rust binary download | ~2/20 | brunoborges/ghx, 777genius/claude-notifications-go |
| Mixed (Python + Node, Python + Playwright) | ~2/20 | NoelClay/academic-research-mcp-plugin, tretuttle/AI-Stuff |
| WASM binary | 1/20 | JordanCoin/pdf-to-text |

#### Alternative — inline per-script deps (Python only)

PEP 723 inline metadata with `uv run --script` sidesteps SessionStart entirely. Each script invocation creates its own ephemeral venv from a `# /// script ... dependencies = [...] ///` block in the file.

Observed: 1/20 (damionrashford/trader-os, 3 scripts across 3 plugins). Fits small one-off scripts where full SessionStart infrastructure is heavy. Doesn't fit plugins with many scripts sharing a common environment — each invocation pays ephemeral-venv overhead.

#### Pitfalls

**`${CLAUDE_PLUGIN_DATA}` silently missing on older Claude Code versions.** Guard with a fallback (`DATA_DIR="${CLAUDE_PLUGIN_DATA:-${HOME}/.config/<plugin>}"`) or fail loudly with a version-requirement error. Silent `$DATA_DIR=""` expansion installs to filesystem root.

**Shared install locations create cross-plugin conflicts.** Installing into `~/.local/pipx`, `~/.venvs/shared`, or similar shared paths means plugin A's dep upgrade breaks plugin B. The docs' per-plugin `${CLAUDE_PLUGIN_DATA}` isolation exists for this reason.

**`source activate` in the SessionStart hook doesn't persist.** Activating a venv inside the hook does not propagate to Claude Code's tool-invocation environment — the hook's shell exits and its env goes with it. Correct pattern: bin wrappers `exec` the venv's interpreter directly, or the hook writes a pointer file the wrapper reads (anthril/ppc-manager).

**SessionStart fires on `startup`, `clear`, and `compact`.** Installing on every sub-event wastes work. Scope the install to `"matcher": "startup"` unless reinstall is genuinely needed after cache clears.

#### Install-timing: SessionStart vs bin-wrapper lazy install

Three distinct install-timing patterns are worth distinguishing:

- **SessionStart install** — the docs-prescribed pattern above. Install runs at session boot (before any tool call). Predictable cost paid upfront; no surprises at tool-call time. Most common.
- **Bin-wrapper lazy install** — no SessionStart hook; the bin wrapper itself downloads/installs dependencies on first invocation. Observed in brunoborges/ghx (shim lazy-downloads Go binary), 777genius (POSIX wrapper lazy-downloads per OS/arch at every hook fire, with version-cache short-circuit), lukasmalkmus/moneymoney (three-tier resolution: user-PATH → cached → download). Appropriate when the binary is optional or large enough that eager install on every session is wasteful.
- **Hybrid — hook-driven install + wrapper fallback** — SessionStart does best-effort; wrapper has a fallback if install failed or was skipped. Observed in iVintik (SessionStart auto-npm-install-global with wrapper using PATH-resolved CLI), Emasoft (bin wrapper uses `uv run --with tiktoken` per-invocation — no SessionStart needed).

Trade-off: SessionStart guarantees availability at tool-call time but pays cost every session. Lazy install defers cost until actually needed but may surprise with latency on first tool call. Hybrid gets the best of both at the cost of maintaining two install paths.

### Bin-wrapped CLI distribution

Ship PATH-accessible commands that Claude Code invokes via the Bash tool. Applies to plugins providing user-facing CLIs beyond skills and agents.

Docs prescribe the `bin/` directory location but are silent on wrapper implementation. No Anthropic-owned marketplace ships a `bin/` directory in its own plugins — convention is entirely community-established.

**Sample scope.** 23-repo bin-wrapper sub-sample discovered via GitHub code search on `CLAUDE_PLUGIN_ROOT path:bin`. Non-exhaustive (pagination capped at the API level) but patterns cluster cleanly.

#### Runtime resolution

How the wrapper discovers the plugin install path to locate bundled scripts.

| Path | Docs | Adoption |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}` with script-relative fallback | | 14/23 |
| `${CLAUDE_PLUGIN_ROOT}` required, no fallback | | 3/23 |
| Script-relative only (`$(cd "$(dirname "$0")/.." && pwd)`) | | 3/23 |
| Reads pointer file written by SessionStart hook | | 1/23 |
| User-PATH first, then plugin-managed, then download | | 1/23 |
| Standalone — no plugin-root resolution | | 1/23 |

Docs state `${CLAUDE_PLUGIN_ROOT}` is exported to hook and MCP subprocesses but do not address bin invocation. Community-observed reality: `CLAUDE_PLUGIN_ROOT` is set when Claude Code invokes a bin via the Bash tool but not when the binary is run directly by the user or by a sibling wrapper. The env-var-with-fallback pattern dominates because it works in both contexts.

Canonical form:

```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
```

#### Shebang

| Shebang | Adoption |
|---|---|
| `#!/usr/bin/env bash` | 12/23 |
| `#!/bin/bash` | 4/23 |
| `#!/usr/bin/env python3` | 3/23 |
| `#!/usr/bin/env node` | 3/23 |
| `#!/usr/bin/env -S uv run --script` (PEP 723 inline metadata) | 1/23 (3 files) |
| `#!/bin/sh` or `#!/usr/bin/env sh` | 2/23 |
| `#!/usr/bin/env bun` | 1/23 |

`env bash` dominates. `uv run --script` with PEP 723 inline metadata is the only pattern that declares per-script dependencies inline — sidesteps venv activation entirely for small scripts.

POSIX `/bin/sh` (777genius/claude-notifications-go, Chachamaru127/claude-code-harness) is sometimes deliberate — 777genius's wrapper header comment explicitly cites Debian/Ubuntu's `/bin/sh` = `dash` distinction to avoid bashisms in the hot path. Chachamaru127's harness shim makes the same choice for portability. Both repos use bash for heavier one-shot work (install scripts, release workflows) and POSIX `sh` for hook-fire hot paths where startup cost matters.

#### Venv handling (Python wrappers)

Across 8 Python-consuming wrappers in the sample.

| Path | Adoption |
|---|---|
| No venv — `python3` direct, assume system interpreter has deps | 4/8 |
| `uv run --script` with PEP 723 inline deps | 1/8 (3 files) |
| Explicit `source $VENV/bin/activate` then exec | 1/8 |
| SessionStart writes interpreter path to pointer file; wrapper reads and exec's | 1/8 |
| pip-install-at-first-run (no venv isolation) | 1/8 |

Direct `exec "$VENV/bin/python"` is preferable to `source activate` — no shell fork, no env side effects, `sys.prefix` resolves correctly. The SessionStart-writes-pointer pattern (anthril/ppc-manager) is the most robust option when the venv lives in `${CLAUDE_PLUGIN_DATA}` and the wrapper must locate it without hardcoding the path.

#### Platform support

| Path | Adoption |
|---|---|
| Single nix script assumed portable | 17/23 |
| Explicit POSIX (`#!/bin/sh` for BusyBox/macOS compatibility) | 1/23 |
| Bash + `.cmd` Windows pair | 2/23 |
| Bash + `.ps1` PowerShell pair | 1/23 |
| OS-detecting runtime logic | 2/23 |

Most authors ship nix-only. Windows-pair adoption is ~17%.

#### Pitfalls

**`${CLAUDE_PLUGIN_ROOT}` fallback is load-bearing.** Not optional. Wrappers that require the env var break when invoked from the user's shell, from a sibling wrapper, or during local dev without a plugin cache.

**`bin/` files need `chmod +x` before commit.** Docs call out the executable bit only in the hooks troubleshooting section, not in the `bin/` description — but the same requirement applies. Four of twenty sampled `bin/` files were committed as mode 100644 (non-executable) and only work when invoked with an explicit interpreter (`bash path/to/file`). If the file is expected to be invoked as a bare command on PATH, the git mode must be 100755.

**`source .venv/bin/activate` in a bin wrapper is an anti-pattern.** Direct `exec "$VENV/bin/python"` is cheaper, has no shell-state side effects, and works identically.

**`--plugin-dir` does not prepend the dev checkout to PATH.** `claude --plugin-dir <local-checkout>` loads plugin modules from the checkout (MCP tools and skill content reflect the dev tree) but does not prepend the checkout's `bin/` to PATH ahead of marketplace-cache bin directories. Bash-invoked binaries resolve to stale cached versions. Workaround: keep the marketplace install current so cache and checkout align. `--plugin-dir` alone is not a reliable dev-iteration path when tests shell out to plugin binaries.

### User configuration

Collect per-user settings (API keys, preferences, tokens) from `plugin.json`'s `userConfig` field. Claude Code prompts on plugin enable; values land in `settings.json` — or in the system keychain for sensitive fields.

Applicability: plugins with per-user settings. Docs prescribe `sensitive: true` for anything that shouldn't land in plaintext `settings.json`.

#### Schema richness

Docs show `description` + `sensitive` as the minimal example; real plugins use richer JSON-schema-like shape with `type`, `title`, `default`, enum constraints. ~14/54 repos declare non-trivial `userConfig`. Across that set, typed schemas (`type`, `title`, `default`, sometimes enum/default) are universal when the field count exceeds ~3 — tokens-only configs stay minimal; configs with multiple user-meaningful parameters consistently adopt the typed form.

#### File-convention user config (bypasses `userConfig`)

~6/54 repos deliberately sidestep `userConfig` in favor of filesystem convention: config files in the user's workspace or home directory that the plugin reads directly at runtime.

| Path | Repos | Rationale observed |
|---|---|---|
| `~/<plugin>/settings.json` in user home | ShaheerKhawaja/ProductionOS | Survives plugin updates; cross-tool shareable |
| Project-local `<plugin>.config.yaml` or `.env.local` | Lykhoyda, skullninja/coco-workflow (`.coco/config.yaml`), BrandCast-Signage (`root.config.json` in consumer project) | Per-project config; not tied to plugin install |
| OS keychain directly (not via `sensitive: true`) | CodeAlive-AI/codealive-skills | Cross-agent secret sharing (Keychain/Secret Service/Credential Manager) |
| `.claude/<plugin>.local.md.example` files | anthropics/financial-services-plugins | Gitignored markdown examples read by skill prose |

Motivations observed: (1) persist-across-plugin-updates (userConfig values in `settings.json` survive updates, but file-convention paths under the plugin dir do not), (2) cross-tool sharing (one config readable by Claude Code, Codex, Cursor simultaneously), (3) secret distribution (OS keychain is often already the plugin's only credential source), (4) per-project vs per-user separation (userConfig is per-user only).

**Pitfall — file-convention bypasses Claude Code's sensitive-value routing.** Secrets stored in plaintext config files are visible on disk with normal user permissions. If the secret belongs in the keychain, use `sensitive: true` — don't invent a file-convention workaround.

#### Pitfalls

**Describing a value as "secret" in the `description` without setting `sensitive: true`.** Observed in damionrashford/trader-os (7 fields across 3 plugins — `CDP_WEBHOOK_SECRET`, `TRADING_ALERTS_SECRET`, `POLYMARKET_WEBHOOK_SECRET`, and four others — all have "Secret" in their `description` but none set `sensitive: true`) and ChanMeng666/claude-code-audio-hooks (`webhook_url` unmarked despite typically carrying Slack/Discord webhook secrets). Result: values land in `settings.json` as plaintext. ★ Docs prescribe `sensitive: true` to route values to the system keychain — authors appear to lose track of the flag when adding multiple secrets in bulk.

**Keychain quota is ~2 KB shared with OAuth tokens.** ★ Plugin-reference explicitly calls out the shared limit: *"Keychain storage is shared with OAuth tokens and has an approximately 2 KB total limit, so keep sensitive values small."* Plugins declaring many sensitive values or large values risk overflow — other plugins' tokens evicted silently.

**Plugin-root `settings.json` is limited to 2 keys.** ☆ Docs describe a plugin-root `settings.json` for `agent` and `subagentStatusLine` only. 0/21 adopt it in the sample; the 2-key constraint makes it unsuitable as a plugin-wide settings file. Don't treat it as one.

#### Sensitive-value correctness split

Across the 14 `userConfig` adopters in the sample, `sensitive: true` application splits three ways:

| Pattern | Repos | Remediation |
|---|---|---|
| Correct — `sensitive: true` on every secret field | SkinnnyJay (all 3), BULDEE (`sentry_token`, others correctly not flagged), includeHasan (5/8), Arcanon-hub (`api_token`), NoelClay (`semantic_scholar_api_key`) | — |
| Anti-pattern — "Secret" in description but no `sensitive: true` | damionrashford (7 fields across 3 plugins — `CDP_WEBHOOK_SECRET`, `TRADING_ALERTS_SECRET`, `POLYMARKET_WEBHOOK_SECRET`, others), ChanMeng666 (`webhook_url` unmarked) | Add `sensitive: true`; prose doesn't route values to the keychain |
| Declared-but-unconsumed — `sensitive: true` set, but no `.mcp.json` `${user_config.KEY}` substitution wires the value through | Arcanon-hub (`api_token` declared; worker reads from a separate credential chain) | Either wire the substitution or remove the unused declaration; the declaration without consumption is a validator gap no CI catches |

The three failure modes have different remediations — they are not variants of "some authors forget the flag." Treating them as one blurs the signal.

#### Env-var bridging

Two mechanisms bridge `userConfig` values into child-process environments (hooks, MCP servers, CLI wrappers):

- **`${user_config.KEY}` substitution** in `.mcp.json` `env:` blocks. Claude Code expands the reference at server-launch time, binding the stored (plaintext or keychain-backed) value into the environment the server sees. Observed in anthril, damionrashford, Arcanon-hub, includeHasan, BULDEE, SkinnnyJay.
- **`CLAUDE_PLUGIN_OPTION_<KEY>`** env var. Claude Code exports each `userConfig` key as an environment variable with this prefix, available to any child process. Observed in BULDEE's `agent-ddd-verifier.sh`, damionrashford's hook scripts, jxw1102, includeHasan.

The two mechanisms coexist — `${user_config.KEY}` for declarative server config, `CLAUDE_PLUGIN_OPTION_<KEY>` for ambient access from arbitrary scripts. Both are widely used but underdocumented in the plugin reference; verify against current docs when adopting.

#### Alternative — OS keychain direct use (cross-boundary hazards)

**CodeAlive-AI/codealive-skills** stores credentials directly in the OS keychain via platform CLIs — `security` on macOS, `secret-tool` on Linux, `cmdkey` on Windows — bypassing `userConfig` entirely. Deliberate choice: the same credential is accessible to Codex, Cursor, and other agents on the same machine, not siloed per plugin.

The cross-boundary subcase is a concrete pitfall for Windows-targeting plugins. When Claude Code runs inside WSL but the credential lives in Windows Credential Manager, the SessionStart hook can't read the value directly — bash cannot cross the WSL boundary to Credential Manager APIs. CodeAlive-AI works around this by probing existence via `cmd.exe /c cmdkey /list:codealive-api-key` (returns present/absent, not the value), then writing a sentinel string `"windows-credential-store"` that signals "credential exists; defer the actual read to Python runtime via `powershell.exe`." Clever but fragile — every consumer of the credential must know to handle the sentinel.

#### Additional Pitfalls

**Declared-but-unconsumed `userConfig` is silent.** No CI validator checks that fields declared in `userConfig` are actually referenced somewhere (via `${user_config.KEY}` or `CLAUDE_PLUGIN_OPTION_*`). Arcanon-hub exemplifies the pattern: the field exists in `plugin.json`, but the value is ignored at runtime because the substitution was never wired. Users see a config prompt, fill it out, and the value does nothing. Add a lint that cross-references `userConfig` keys against `.mcp.json`, hooks, and source files.

**WSL keychain boundary breaks naive direct-use.** Plugins that store credentials in Windows Credential Manager and expect bash hooks to read them will fail silently under WSL. If the plugin targets WSL users, either use `userConfig` + `sensitive: true` (which Claude Code routes to the keychain internally) or adopt CodeAlive-AI's sentinel-pass-through with explicit PowerShell read at the consumption site.

### Tool-use enforcement

Gate or modify tool use based on plugin-defined policy — code-quality gates, scope restrictions, destructive-action guards, audit trails.

Applicability: plugins shipping invariants users must not violate. Uses PreToolUse and PostToolUse hooks.

#### Handler output

Handlers communicate via two channels: plain text on stderr (shown in the UI as a human message) and structured JSON on stdout (parsed for `hookSpecificOutput`, `systemMessage`, context injection). Exit code 2 signals a blocking failure.

#### Failure posture

Per-hook, not plugin-wide:

- **Fail-open** — default to allow on unexpected error. Appropriate for SessionStart (can't block the session), cosmetic hooks, exploratory handlers. Keeps Claude Code usable when the plugin has bugs.
- **Fail-closed** — default to deny. Appropriate for safety gates (security policy, destructive-action guards) where a silent pass is worse than a blocked-but-visible message.

Explicit conventions observed in 2/21 repos: BULDEE/ai-craftsman-superpowers' `post-write-check.sh` emits stderr summary + stdout JSON with a fail-open trap; Kanevry/session-orchestrator's `enforce-scope.mjs` uses centralized `emitAllow/emitDeny/emitWarn` helpers with a fail-closed REQ-01 top-level try/catch.

#### Pitfalls

**JSON-only-to-stdout produces silent blocks.** BULDEE's CHANGELOG documents this anti-pattern directly: pure-JSON stdout with a blocking exit code surfaces "No stderr output" in the UI, leaving users with no indication of why a tool call was blocked. Corrective pattern: emit a human-readable summary on stderr alongside the structured JSON.

**Bare `exit 1` on unexpected error crashes every tool call.** Without a top-level try/catch that emits a structured response on crash, a misbehaving handler turns into a permanent tool-call block until the user disables the plugin.

**Non-`command` hook types untested in community.** ☆ Docs list four hook types: `command` (shell), `http` (POST JSON), `prompt` (LLM evaluates `$ARGUMENTS`), `agent` (agentic verifier). Sample adoption: 21/21 use `command` exclusively. First-time adopters of `http`/`prompt`/`agent` absorb the full cost of discovering edge cases — expect undocumented behavior.

**`additionalDirectories` in permissions accepts paths, not globs.** `..` is portable because it resolves against the active project at runtime.

### Agent delegation patterns

Skills and agents delegate work to subagents through Claude Code's subagent-invocation mechanism. Beyond the baseline "spawn one agent, return its result," three sub-patterns recur in repos that ship agents (~20/54 of the sample). Denominator for adoption counts below is repos that ship agents, not the full sample.

#### Hook-enforced scope walls

Agents declare tool scope in frontmatter; PreToolUse / PostToolUse / SubagentStop hooks enforce it at runtime. **AgentBuildersApp/eight-eyes** is the reference implementation: 8 role-specific agents (skeptic, security, performance, accessibility, docs, implementer, verifier, reviewer) each with different tool scope, a structured-result-block contract (`COLLAB_RESULT_JSON_BEGIN` … `COLLAB_RESULT_JSON_END` that SubagentStop parses), and blind-review enforced by SubagentStart context-shaping (skeptic literally can't see implementer's summary). BULDEE uses a similar shape at smaller scale. Observed in 3/20.

The pattern matters because tool scope declared in agent frontmatter is advisory — the runtime binding happens in the hooks. A plugin that claims isolation without the hook enforcement is making a claim the runtime doesn't verify.

#### Skill composition in agents (`skills:` frontmatter array)

Agents invoke skills as sub-routines via a `skills:` array in frontmatter. Claude Code loads each named skill's procedure into the agent's context at agent start.

- **CodeAlive-AI/codealive-skills** — `agents/codealive-context-explorer.md` uses `skills: [codealive-context-engine]` with `model: haiku`. The skill composition plus model downgrade is cost-aware: offload iterative searches to a cheaper model so the caller's expensive-model conversation stays short.
- **damionrashford/trader-os** — `quant-analyst` agent declares `skills: [quant-math, position-sizing, bayesian-updating, time-series]`, pulling four analytical sub-routines into the agent's context as invocable primitives.
- **BULDEE/ai-craftsman-superpowers** — `team-lead.md` declares agent-orchestration tools (`TeamCreate`, `TaskCreate`, `TaskList`, `TaskUpdate`, `SendMessage`) in `allowedTools`; these are not in the public plugin reference.

3+/20 of agent-shipping repos.

#### Non-canonical frontmatter fields (worktree / background / effort)

Multiple agents declare frontmatter fields that are partially or entirely absent from Claude Code's public plugin reference: `isolation: worktree`, `background: true`, `effort: medium|high|xhigh`, `maxTurns`, `stakes: low|medium|high`, `subagent_type: <plugin>:<name>`. `isolation: worktree` alone is observed in 7/20 agent-shipping repos (AgentBuildersApp, BULDEE, REPOZY, damionrashford, NoelClay, Lykhoyda, skullninja). Several of these fields are enforced by the plugin's own hooks rather than by Claude Code — the frontmatter becomes a declaration consumed by the plugin's own machinery, not a Claude Code directive.

#### Pitfalls

**Undocumented frontmatter fields without hook enforcement are cargo cult.** Authors see `isolation: worktree` in a reference implementation and adopt it without the matching PreToolUse/PostToolUse hook that would actually enforce per-role isolation. The field quietly does nothing; the agent runs with full tool scope. Before adopting a non-canonical frontmatter field, verify against the reference repo's hooks whether the field is runtime-backed.

**`skills:` array is an implicit dependency.** Listing `skills: [foo]` on an agent means the agent's context won't be coherent unless the named skill is installed and loads correctly. No validator in the current ecosystem checks that referenced skills exist — a missing skill produces runtime surprises rather than install-time errors.

**`subagent_type` namespacing is not a community convention.** ShaheerKhawaja uses `subagent_type: <plugin>:<name>`; 0 other repos adopt it. Agents named via the plugin-qualified form won't resolve for users of other marketplaces.

### Session context loading

Inject persistent context into the session at start or on user prompt — load knowledge bases, restore working memory, set project-level instructions.

Applicability: plugins that have persistent context to surface. Uses SessionStart for one-shot context at session boot; UserPromptSubmit for per-turn context manipulation.

Primary mechanism: stdout JSON with `hookSpecificOutput.additionalContext` field. Docs document the structure; few sampled repos use it as the primary purpose of a hook.

SessionStart sub-event matchers distinguish `startup` (fresh session), `clear` (user cleared context), `compact` (auto-compact restart). Context-loading plugins typically scope to `startup` + `clear` and skip `compact` to avoid doubling context.

REPOZY/superpowers-optimized is the clearest observed reference — uses `"matcher": "startup|clear|compact"` on SessionStart with sub-event-specific behavior.

#### Pitfalls

**Context loaded on every SessionStart sub-event triples the load.** Scope the matcher to the sub-events that actually need the context.

**`additionalContext` cannot block.** Unlike tool-gating hooks, context hooks have no exit-2 path — they inject or don't. Failures are silent unless the hook also emits on stderr.

### Live monitoring and notifications

Stream background state to the user as notifications — market prices, job status, long-running builds. Uses `monitors/monitors.json`, introduced in Claude Code v2.1.105+.

Applicability: plugins that produce continuous event streams. Sampled observation: 2/54 ship monitors — damionrashford/trader-os (5 monitors: price-watch, order-status, news-watch, balance-watch, tx-status) and Chachamaru127/claude-code-harness (1 monitor: harness-session-monitor) — each emitting one plain-text line per event.

#### Alternative — GitHub Actions cron as scheduler substitute

~5/54 repos route periodic tasks through GitHub Actions `schedule:` cron rather than `monitors.json`. Observed: BaseInfinity/sdlc-wizard (weekly-update, monthly-research, weekly-api-update — 3 "shepherd" workflows that open tracking issues), IgorGanapolsky/ThumbGate (~20 autonomous cron workflows driving daily-revenue-loop, instagram-autopilot, self-healing-auto-fix), robertnowell/marketing-pipeline (daily cron posting across 5 platforms), anthropics/claude-plugins-official (weekly bump-plugin-shas), Vortiago (weekly codeql scan), 777genius (rotate-stripe-webhook-secret).

Trade-offs: durable scheduling without requiring a running Claude Code session or plugin monitor; survives session-end. But repo-owner-only (users can't customize cadence) and doesn't stream notifications back to Claude — surfaces state by opening GitHub Issues or PRs instead. Appropriate when the periodic task's audience is the maintainer, not the user. In contrast, `monitors.json` is appropriate when the user needs real-time in-session notifications.

#### Lifecycle scope

| Path | Docs | Adoption |
|---|---|---|
| `when: always` — start at session boot, run until session end | ☆ | 2/54 |
| `when: on-skill-invoke:<skill-name>` — start on skill use | ☆ | 0/54 |
| No monitors | | 52/54 |

#### Pitfalls

**Version floor silences monitors on older Claude Code.** Pre-v2.1.105 installs silently skip the file; users never see monitor output and get no error. Declare the version requirement in `plugin.json` `engines` or README.

**Stdout is the only communication channel.** Monitor processes emit one notification per stdout line — no structured JSON, no context injection. Design output as user-facing human text.

### Plugin-to-plugin dependencies

Declare that one plugin requires another, with optional semver constraints. Introduced in Claude Code v2.1.110+.

Applicability: multi-plugin marketplaces where plugins share functionality. Effectively 0/21 verified adoption in sampled repos; feature is too new to have percolated. damionrashford/trader-os mentions its `trading-core` shared layer is depended on by sibling plugins in description text, but explicit `dependencies` arrays in `plugin.json` were not verified.

Declaration: `dependencies: [{ name, version, marketplace? }]` in `plugin.json`. Resolution uses the `{plugin-name}--v{version}` git tag convention — separate tag namespace from the plain `v{version}` used for marketplace-wide releases.

#### Prose/installer-encoded dependencies (pre-schema alternative)

Three repos ship multi-plugin marketplaces where one plugin is functionally depended on by siblings, expressed in prose or installer code rather than declared in manifest. These predate Claude Code v2.1.110 or target older hosts — schema-supported enforcement is deliberately skipped, not forgotten:

- **damionrashford/trader-os** — README architecture diagram and CLAUDE.md both describe `trading-core` as "shared quant layer the other plugins consume." Users who install `polymarket` without `trading-core` get broken scripts; nothing in manifest-land warns them. CLAUDE.md tells contributors to "Consume trading-core's math + journal from your scripts (don't re-implement Kelly)" but doesn't wire the `dependencies` field.
- **BrandCast-Signage/root** — `mcp-root-board` vs `mcp-local-rag` ownership-based install split documented in CHANGELOG 2.3.0's "Why" section, not in manifest. Split rationale: first-party vs third-party install location, lifecycle coupling.
- **stellarlinkco/myclaude** — The npx installer encodes inter-module dependencies programmatically (`WRAPPER_REQUIRED_MODULES = new Set(['do', 'omo'])`, `WRAPPER_REQUIRED_SKILLS = new Set(['dev'])` in `cli.js`): "if you select `do` or `omo`, also run `install.sh` for the `codeagent-wrapper` binary." Implicit module dependency baked into the installer rather than declared in `config.json`.

#### Flat-by-convention (deliberate alternative)

**anthropics/knowledge-work-plugins** takes the opposite stance: plugins are intentionally flat and independent. Cross-plugin interactions handled by convention — `sales` and `marketing` both connect to HubSpot via their own `.mcp.json`, each plugin standing alone with its own integration configs. This is a valid alternative for marketplaces where cross-plugin coupling would add more complexity than value.

#### Pitfalls

**Dual tag namespace is easy to misconfigure.** Dependency resolution looks for `{plugin-name}--v{version}` tags at the source marketplace repo. Plugins tagged only with plain `v{version}` will not resolve as dependencies. If your marketplace uses plugin-to-plugin dependencies, decide up front whether to maintain both tag forms or only the dependency-specific form.

**Documentation-only dependencies install happy but run broken.** When a plugin functionally depends on a sibling but doesn't declare it, the install succeeds cleanly; the breakage surfaces at runtime when an agent hits a missing helper. If you're going to skip the `dependencies` field intentionally, at least have SessionStart verify the sibling's presence and emit a corrective message.

### Project-level tooling layout

Where operations tied to the repository's own development infrastructure live — test runners, release scripting, manifest validators, cross-plugin system discovery, one-time setup. These are distinct from plugin-general capabilities: they serve maintainers of *this* repo, not downstream consumers of the plugins.

| Path | Docs | Adoption |
|---|---|---|
| Project root (`bin/`, `scripts/`, `tools/`, `Makefile`) | | Universal when present |
| Packaged inside a plugin's bin/framework and invoked via a plugin CLI | | 0/54 |

Docs silent. Community convention is universal: if a repo has project-level tooling, it lives at project root. **0/54 sampled repos package project-level orchestration inside a plugin's binary and invoke it as `<plugin>-run <verb>`.** When a wrapper exists, it lives at project root; when there's no wrapper, CI or the developer invokes the underlying tool (`pytest`, `npm test`, `go test`, `cargo test`, `bun test`) directly.

Observed project-level tooling homes:

- `scripts/test.sh` — thin bash wrapper around direct test-runner invocation. Observed in 2/30 repos with CI (BULDEE, Kanevry equivalents).
- `tests/run-tests.sh` — heavier bash orchestrator with subdir dispatch. Observed in 1/30 (BULDEE, ~20KB).
- `bin/<project-tool>` — bash entry dispatching to a project-level module (e.g. `tools/`). Observed in a minority of repos with sophisticated tooling needs.
- `Makefile` targets — `make test`, `make release`. Common in polyglot repos.
- Direct CLI invocation from CI — no wrapper; workflow YAML runs `pytest tests/` or equivalent.

#### Pitfalls

**Packaging project-level orchestration inside a plugin's binary.** If a plugin's `bin/<plugin>-run` grows subcommands like `tests` that discover and orchestrate project-wide state (project suite + per-plugin suites), the plugin ships project-local infrastructure to every downstream consumer. The plugin cache carries code those users never invoke; project-level operations become conceptually downstream of a specific plugin; and other plugins in the same repo cannot access the same orchestration without depending on the first plugin being installed. Project-level tooling belongs at project root — not inside any plugin.

**Plugin `init` auto-wiring downstream project settings.** A plugin's install/init routine should not modify the downstream project's git config (e.g., `core.hookspath`), shell environment, or `.claude/` files outside the plugin's declared scope. Those decisions are explicit per project and belong in project-level setup scripts (`bin/<project-tool> setup`, `scripts/setup.sh`, `Makefile install`). A plugin that auto-wires on install imposes project conventions on every repository where it gets installed, which is invasive and hard to audit.

### Testing and CI

Run tests on push/PR; keep test artifacts out of user plugin caches.

Applicable to repos with runnable tests. 8 repos have no Python tests and are excluded from testing-location and pytest-config tables.

#### Tests location

| Path | Docs | Adoption |
|---|---|---|
| `tests/` at repo root only | | 8/10 |
| `tests/` at repo root with per-plugin subdirs (`tests/plugins/<name>/`) | | 1/10 |
| `tests/` inside plugin directory | | 1/10 |

Community majority is tests at repo root. Tests inside the plugin directory is an anti-pattern at scale because there is no `.claudeignore` — tests ship to every user's plugin cache.

#### Pytest configuration location

| Path | Docs | Adoption |
|---|---|---|
| `[tool.pytest.ini_options]` in `pyproject.toml` | | 6/10 |
| No explicit config | | 4/10 |

Docs silent. Community convention is `pyproject.toml`. Dedicated `pytest.ini` is a widely-known pytest option but was not observed in any sampled repo.

#### Python dependency manifest format

Applicable to repos with Python deps. 11 repos have no Python deps and are excluded.

| Path | Docs | Adoption |
|---|---|---|
| `pyproject.toml` | | 6/7 |
| `requirements.txt` | | 1/7 |

Docs silent on manifest format. Install mechanism is what docs prescribe (see **Dependency installation**).

#### CI trigger surface

Applicable to repos with `.github/workflows/`. 3 repos have no workflows.

| Path | Adoption |
|---|---|
| `push` to default branch + `pull_request` | 13/15 |
| `push` to any branch + `pull_request` | 2/15 |
| `push` to `release/*` only | 1/15 |
| `pull_request` only (no push trigger) | 2/15 |
| `schedule` (weekly cron) for SHA bumps or maintenance | 3/15 |
| `workflow_dispatch` for benchmarks, ad-hoc runs | 6/15 |
| `tags: ['v*']` for release automation | 6/15 |

Near-universal combination is `push: [branches: [main]]` + `pull_request: [branches: [main]]`. Multiple triggers combine — counts above are non-exclusive.

#### What CI actually does

| Path | Adoption |
|---|---|
| Pytest (or unittest) alone | 3/13 |
| Pytest + linting (ruff/pyright/mypy) | 2/13 |
| Custom shell validators (no pytest) | 2/13 |
| Node `npm test` + custom validators | 3/13 |
| JSON-schema manifest validation only | 2/13 |
| `claude plugin validate` CLI invocation | 0/30 |

**Docs vs adoption conflict.** ★ Docs recommend `claude plugin validate` as the validation command. 0/30 repos with any CI wire it in. Every repo doing marketplace validation rolled its own schema check. Hypothesis: `claude plugin validate` requires a working Claude Code CLI install on the runner plus an authenticated context it lacks in CI — friction that pushes authors toward schema-based alternatives that need no auth.

#### Matrix strategies

| Path | Adoption |
|---|---|
| No matrix — single OS, single runtime | 6/13 |
| Python-version matrix only | 1/13 |
| OS × Python matrix | 2/13 |
| OS × Node matrix | 1/13 |
| OS × Node × package-manager matrix | 1/13 |

Plugin-testing marketplaces gravitate to OS × Python when Python runtime behavior matters (hook subprocess environment, venv setup). Single-runtime CI is the norm for projects using CI primarily as a trust signal.

#### Action pinning

| Path | Adoption |
|---|---|
| Tag-pinning (`@v4`, `@v6`) | 11/15 |
| SHA-pinning with trailing tag comment | 4/15 |

Tag-pinning is the default. SHA-pinning concentrates in more mature pipelines — supply-chain discipline, not a conventional default.

#### Caching

| Path | Adoption |
|---|---|
| No explicit cache | 4/10 |
| Built-in setup-action cache (`setup-node cache: 'npm'`, `setup-uv enable-cache: true`) | 3/10 |
| Standalone `actions/cache` with `hashFiles('**/*.lock')` keys | 3/10 |

When caching is present, built-in setup-action caching precedes standalone `actions/cache`. Standalone cache appears when a matrix demands per-PM keys.

#### Test runner invocation

| Path | Adoption |
|---|---|
| Direct `pytest` or `python -m pytest` | 4/10 |
| `python -m unittest discover` | 2/10 |
| `uv run pytest` | 1/10 |
| Bash wrapper (`scripts/test.sh`) | 2/10 |
| `npm test` / node-script | 3/10 |

Direct `pytest` is the community norm. The `scripts/test.sh` wrapper pattern (used by this project) is rare; appears when CI also exercises bash-based validation.

#### Fixture discipline

Fixture-level conventions observed across repos that ship Python test suites. Denominator: repos with pytest or unittest adoption (~4/13 sampled; extrapolating to ~10-15/54 overall — Python test adoption is thinner than the narrative suggests, as many "test-rich" repos ship shell-script suites or vitest).

**Real backends over mocks.** 0/5 sampled Python test suites use `unittest.mock`. Every fixture goes after a real backend — SQLite in-memory (Cairn, CronusL), real Docker compose stack (Vortiago), real CLI subprocess invocation (SkinnnyJay's `claude_runner` and `codex_runner`, AgentBuildersApp's real `git` and hook scripts), real git-init'd tempdirs (AgentBuildersApp's `setUp` per test). Strong consistency signal: the ecosystem tests integration end-to-end, not isolated units with mocked seams. Aligns with the broader testing discipline that catches integration breakage where mocks hide it.

**Fixture scope discipline.** Session scope for expensive setup (Vortiago's Docker stack, SkinnnyJay's seeded vault, Cairn's session-metrics accumulator); function scope for per-test isolation (Cairn's `integration_count`, CronusL's `tmp_project_dir`, Vortiago's `mcp_session`); module scope unused across all 4 conftest-using repos. Session+function two-tier is the observed pattern.

**Opt-in real-subprocess gates.** Tests that spawn real CLIs or real agents cost tokens, take seconds to run, and may require external resources. Two gating mechanisms observed:

- **Environment variable gate** — SkinnnyJay's `RUN_CLAUDE_TESTS` / `RUN_CODEX_SKILL_EVALS` env vars control whether real `claude` / `codex` CLIs are invoked.
- **pytest marker + CLI flag** — this project's `pytest.mark.agent` paired with `--run-agent` on the pytest command line.

Same intent, different mechanism. 2/5 of sampled real-backend test suites use an explicit opt-in gate; others run real-backend tests unconditionally.

**Fixture-discipline Pitfalls:**

- **Silent pass on mock-only tests.** When a test suite mocks its primary dependency (git, DB, MCP server), the happy-path assertion can pass while real integration is broken. Authors who mock should explicitly note what integration is not covered.
- **Unconditional real-subprocess tests burn tokens on every CI run.** Without an opt-in gate, real-agent tests fire on every push — expensive and slow. Add a marker (`pytest.mark.agent`) or env-var gate (`RUN_<X>_TESTS`) so default CI stays fast.

Out of scope for this pattern doc (future-wave material): `conftest.py` structural templates (shape varies too much across the 4 sampled repos), worktree-isolated test fixtures (unique to this project — no shared convention), and `tests/fixtures/` directory conventions (3 repos have fixture dirs, all with different layouts).

#### Pitfalls

**No `.claudeignore` exists.** Plugin cache carries the entire `plugins/<name>/` directory. Dev/prod separation happens only via repo layout discipline — tests at repo root, not inside plugin dirs.

**`CLAUDE_CODE_PLUGIN_SEED_DIR` affects CI plugin state.** Tests that mutate global `~/.claude/plugins` state may conflict with pre-seeded plugin caches in container images. Isolate test environments explicitly.

### Release automation

Turn a version tag into a GitHub release (and optionally a published artifact). Applicable to repos that release. 6/18 primary-sample repos have release-automation workflows.

#### Release trigger

| Path | Adoption |
|---|---|
| `push: tags: ['v*']` | 5/6 |
| `push: tags` + `release: [published]` + `workflow_dispatch` | 1/6 |

Community norm is tag push as the trigger, no manual entry points. Multi-trigger shapes exist for idempotent retry.

#### Automation shape

| Path | Adoption |
|---|---|
| Skill-zip build + draft GitHub release | 2/6 (Anthropic life-sciences, healthcare — identical) |
| Tag-sanity checks + create GitHub release (no artifacts) | 1/6 |
| Tag-sanity checks + npm publish (`--provenance`) + release | 2/6 |
| Platform binary build + attach to release | 1/6 |
| PyPI trusted publishing (OIDC) + MCP registry publish | 1/6 |

All use either `softprops/action-gh-release@v*` or `gh release create`. No sampled repo uses `release-drafter`, `release-please`, or `semantic-release`.

#### Tag-sanity gates

Checks performed before publishing.

| Path | Adoption |
|---|---|
| No gate — accept any `v*` tag push | 3/6 |
| Verify tag is on `main` branch | 2/6 |
| Verify tag matches `package.json`/`pyproject.toml` version | 2/6 |
| Verify tag format matches `^v\d+\.\d+\.\d+$` regex | 1/6 |

Deep gates (verify-on-main + verify-version + format regex) protect the Clean Break discipline — a release tag cannot ship unless version metadata is in sync with the tag itself. Anthropic-owned release workflows do no gating whatsoever.

#### GitHub release creation

| Path | Adoption |
|---|---|
| `softprops/action-gh-release@v1-v3` with `generate_release_notes: true` | 3/6 |
| `gh release create --generate-notes` | 3/6 |
| `draft: true` on the release | 2/6 |
| CHANGELOG.md parsing (awk) for notes body | 1/6 |

GitHub's `generate_release_notes` is the universal notes source. No repo uses a dedicated changelog generator (`release-please`, `semantic-release`, `git-cliff`). CHANGELOG files in the Features are therefore hand-maintained — only Chachamaru/claude-code-harness threads CHANGELOG content through its release workflow.

#### Pitfalls

**`GITHUB_TOKEN` cannot create PRs under some org policies.** Anthropic's SHA-bump automation uses a dedicated GitHub App token. Repos adopting scheduled SHA-bump PRs need a non-default token.

**Draft release plus auto-generated notes without manual curation.** Appropriate when no human reviews zip contents. If the release is auto-published, don't mark it draft — it will sit unpublished.

### Marketplace validation

Verify the marketplace manifest and plugin manifests conform to expected schemas before a push or release.

Applicability: all repos that ship a marketplace, though few automate validation.

| Path | Docs | Adoption |
|---|---|---|
| Dedicated validator script (bun+TS, python+json, node+custom) on PR | | ~8/54 |
| Inside a fan-out CI as one job among many | | ~5/54 |
| No marketplace-specific validation | | ~41/54 |
| `claude plugin validate` CLI invocation | ★ (command recommended) | 0/54 |

**Docs vs adoption conflict.** Anthropic's own `claude-plugins-official` uses bun + plain TypeScript (`validate-marketplace.ts`, ~65 lines, no zod or other schema library — manual shape checks), not the CLI. Anthropic's docs recommend the CLI; Anthropic's own engineering doesn't use it in CI. **0/54 sampled repos invoke `claude plugin validate` in CI** — stronger evidence than the narrower primary-sample count suggested. Plausible explanation: CLI requires a working Claude Code install on the runner plus auth; schema-based alternatives run with zero install. The CLI appears to be used only manually by plugin authors during local development — documented practice, not an enforced one.

When choosing a validation approach: schema-based checks run in any CI environment without Claude Code installed; `claude plugin validate` catches semantic issues the schema misses but requires install + auth in CI.

### Documentation

Orient users, contributors, and future maintainers. Applicability universal.

#### Documents at repo root

| Document | Docs | Adoption |
|---|---|---|
| `README.md` | | 18/18 |
| `CHANGELOG.md` | ★ | 9/18 |
| `architecture.md` | | 2/18 |
| `CLAUDE.md` (agent procedures) | | ~22/54 (substantially matured since the 18-repo snapshot; now common for active plugins) |
| `LICENSE` | | Near-universal |
| Community health files (`CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`) | | Rare — observed as a bundle in thoughtful community repos (BULDEE) |

#### Per-plugin documents

| Document | Adoption |
|---|---|
| `README.md` per plugin | 12/18 |
| `architecture.md` per plugin | Rare |

#### CHANGELOG format

★ Docs recommend a CHANGELOG but don't prescribe format. Across ~27/54 repos that ship a CHANGELOG:

| Format | Count | Example |
|---|---|---|
| Keep-a-Changelog explicit (headers, link to keepachangelog.com) | ~17/27 | BULDEE, Kanevry, SkinnnyJay |
| Custom format | ~8/27 | affaan-m (per-release sub-sections) |
| Keep-a-Changelog-loose (dated sections, no Added/Changed discipline) | ~2/27 | |

[Keep a Changelog](https://keepachangelog.com/) is the dominant community convention: `## [version] — date` sections with `### Added`, `### Changed`, `### Fixed`, `### Removed` sub-headings. **BULDEE/ai-craftsman-superpowers** exemplifies the full discipline (41 KB, every version from v1.2.1 onward, fix/change narratives reference ADRs).

#### Release-notes source

For repos with `release.yml`, where the release body comes from (cross-reference to *Release automation* → GitHub release creation):

| Source | Adoption (N=15) | Notes |
|---|---|---|
| `gh release create --generate-notes` | ~8/15 | Auto-generated from commits/PRs |
| `softprops/action-gh-release` with `generate_release_notes: true` | ~6/15 | Often with draft curation |
| CHANGELOG.md awk-extraction | 1/15 | **Chachamaru127/claude-code-harness** — only sampled repo threading CHANGELOG content through release automation |
| Custom body (hand-maintained, appended to generated notes) | 1/15 | **Vortiago/mcp-outline** — install-command stanza hand-maintained |

GitHub's `generate_release_notes` is the path of least resistance — it captures commit subjects but loses CHANGELOG author intent. No sampled repo uses `release-please`, `semantic-release`, or `git-cliff`.

#### Novel — CHANGELOG as runtime-consumed artifact

**BaseInfinity/sdlc-wizard**'s `/update-wizard` skill fetches `CHANGELOG.md` via WebFetch at runtime and diffs against the installed version stamp. The CHANGELOG is consumed by the plugin itself, not just by human readers — promoting it from "human docs" to "agent-readable contract." Implications:

- Format discipline matters more when a skill has to parse the file reliably.
- The CHANGELOG becomes part of the install/update UX, not just a retroactive record.

1/54 — one-off, but illustrative of what CHANGELOG can carry when treated as data rather than prose.

#### Pitfalls

**Non-obvious `bin/` requirements docs.** Docs mention `chmod +x` for executability in the hooks troubleshooting section, not in the `bin/` description. Authors encountering the `bin/` docs for the first time may commit non-executable files.

**CHANGELOG ↔ `plugin.json` version drift.** Observed in anthril and ShaheerKhawaja — CHANGELOG top entry references a version older than or different from `plugin.json`'s current value. Release automation that threads the version into both (Chachamaru's awk-extraction pattern) is one remediation; cross-verifying as a CI gate is another.

**`--generate-notes` silently replaces CHANGELOG narrative.** When release automation uses `--generate-notes`, the release body is drawn from commit subjects and PR titles — the CHANGELOG author's curated narrative never reaches the release page. Authors who maintain a rich CHANGELOG expecting it to appear in releases will find the release page shows a bulleted commit log instead. Either parse CHANGELOG explicitly (awk / `release-drafter`) or accept that the CHANGELOG is a separate artifact from release notes.

**Custom body stanzas drift.** Vortiago's install-command snippet is appended after `--generate-notes`; every version bump requires manual edits. Hand-maintained release-body templates should be treated as code and reviewed on release.

## Checklist for a new marketplace repo

1. Create `.claude-plugin/marketplace.json` with a single plugin entry whose `source` is a relative path.
2. Create the first plugin under `plugins/<plugin>/.claude-plugin/plugin.json` with `name` and `version`.
3. Initialize `tests/` at repo root.
4. Put pytest configuration in `pyproject.toml` under `[tool.pytest.ini_options]`.
5. Add `scripts/test.sh` delegating to the test runner.
6. Add `scripts/release.sh` for tag cuts (optional).
7. Add `.github/workflows/ci.yml` running pytest on push/PR.
8. Add `.github/workflows/release.yml` triggered on `v*` tag push (optional — see **Release automation** for tag-sanity gate patterns).
9. Add `.github/workflows/validate.yml` for manifest linting (optional).
10. Write `README.md`, `CHANGELOG.md`, `LICENSE`, and (optionally) `architecture.md` and `CLAUDE.md`.
11. Tag the first stable release (`v0.1.0`). Users install stable via `/plugin marketplace add <owner>/<repo>@v0.1.0`.
12. Verify by installing from both the default branch and the tagged ref on a clean machine; confirm the plugin cache contains only intended files.

## References

Three samples inform this pattern. Repos appearing in multiple samples are noted.

### Primary sample (18)

Used for purposes covering publishing, source binding, channel distribution, version control, plugin-component registration, testing, release automation, marketplace validation, documentation.

**Anthropic-owned (6):**

- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) — official curated catalog; `url`+`sha` aggregator pattern
- [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) — community catalog; mixed `url`+`sha` and `git-subdir`+`ref`
- [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) — relative sources; contains the one observed nested partner marketplace
- [anthropics/financial-services-plugins](https://github.com/anthropics/financial-services-plugins) — relative sources
- [anthropics/life-sciences](https://github.com/anthropics/life-sciences) — relative sources; `strict: false` skill carving; semver tags on main
- [anthropics/healthcare](https://github.com/anthropics/healthcare) — relative sources; `strict: false` skill carving; semver tags on main

**Community (12):**

- [AgentBuildersApp/eight-eyes](https://github.com/AgentBuildersApp/eight-eyes) — single plugin; pre-release tag suffix; drift between plugin.json and marketplace version
- [BULDEE/ai-craftsman-superpowers](https://github.com/BULDEE/ai-craftsman-superpowers) — 30 semver tags; ci.yml; 14-event hooks config; reference for enforcement hooks and community health files
- [BaseInfinity/sdlc-wizard](https://github.com/BaseInfinity/sdlc-wizard) — 11 tags; 8 workflows including deep-gated `release.yml`
- [Chachamaru127/claude-code-harness](https://github.com/Chachamaru127/claude-code-harness) — only sampled repo using `release/*` branches for release cuts
- [CodeAlive-AI/codealive-skills](https://github.com/CodeAlive-AI/codealive-skills) — 10 tags; pytest with coverage in CI; SHA-pinned actions
- [CronusL-1141/AI-company](https://github.com/CronusL-1141/AI-company) — 6 tags; `master` default; 12-event hooks config; appears in primary and dep-management samples
- [Kanevry/session-orchestrator](https://github.com/Kanevry/session-orchestrator) — pre-release tag suffixes; reference for fail-closed enforcement pattern
- [Vortiago/mcp-outline](https://github.com/Vortiago/mcp-outline) — 18 tags; most sophisticated release pipeline (OIDC PyPI + MCP registry)
- [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) — per-plugin nested tests precedent; reusable workflows
- [IgorGanapolsky/ThumbGate](https://github.com/IgorGanapolsky/ThumbGate) — `npm` source type (outlier)
- [REPOZY/superpowers-optimized](https://github.com/REPOZY/superpowers-optimized) — only sampled repo with a `dev` branch; SessionStart sub-event matchers
- [HiH-DimaN/idea-to-deploy](https://github.com/HiH-DimaN/idea-to-deploy) — `github` source type (outlier); uses `$schema` reference

### Dependency-management sample (20)

Used for the **Dependency installation** purpose. Filtered for plugins with real runtime dep management.

- [CronusL-1141/AI-company](https://github.com/CronusL-1141/AI-company) — Python venv, `diff -q` (also in primary sample)
- [anthril/official-claude-plugins](https://github.com/anthril/official-claude-plugins) — Python venv, stamp file + `diff -q`; pointer-file bin pattern
- [Arcanon-hub/arcanon](https://github.com/Arcanon-hub/arcanon) — Node/npm, sentinel `diff -q`; installs into ROOT (cites ESM)
- [ekadetov/llm-wiki](https://github.com/ekadetov/llm-wiki) — Node/npm, version file + `diff -q`
- [marioGusmao/mg-plugins](https://github.com/marioGusmao/mg-plugins) — Node/npm, `diff -q` + Node ABI tracking
- [thecodeartificerX/codetographer](https://github.com/thecodeartificerX/codetographer) — Node/npm, copy-then-install
- [tretuttle/AI-Stuff](https://github.com/tretuttle/AI-Stuff) — Node + Playwright Chromium, sha256 + install marker
- [NoelClay/academic-research-mcp-plugin](https://github.com/NoelClay/academic-research-mcp-plugin) — Python venv + Node, `diff -q` both
- [123jimin-vibe/plugin-prompt-engineer](https://github.com/123jimin-vibe/plugin-prompt-engineer) — Python venv, version file
- [includeHasan/prospect-studio](https://github.com/includeHasan/prospect-studio) — Node/npm, sha256; installs into ROOT (cites ESM)
- [damionrashford/trader-os](https://github.com/damionrashford/trader-os) — Node via bun/npm, `diff -q` (cites docs URL in comment); also monitors reference implementation
- [Chulf58/FORGE](https://github.com/Chulf58/FORGE) — Node, mtime vs lockfile; installs into ROOT
- [smcady/Cairn](https://github.com/smcady/Cairn) — Python venv, `diff -q`
- [JordanCoin/pdf-to-text](https://github.com/JordanCoin/pdf-to-text) — WASM binary download, version file
- [ZhuBit/cowork-semantic-search](https://github.com/ZhuBit/cowork-semantic-search) — Python venv, sha256
- [raphaelchristi/harness-evolver](https://github.com/raphaelchristi/harness-evolver) — Python venv, existence-only (no manifest diff)
- [brunoborges/ghx](https://github.com/brunoborges/ghx) — Go binaries into DATA, existence-only
- [jxw1102/flipper-claude-buddy](https://github.com/jxw1102/flipper-claude-buddy) — Python venv, md5 hash
- [BrandCast-Signage/root](https://github.com/BrandCast-Signage/root) — Node/npm, mixed: third-party into `~/.root-framework`, plugin's own into DATA
- [Lykhoyda/rn-dev-agent](https://github.com/Lykhoyda/rn-dev-agent) — Node/npm into DATA + symlink back to ROOT, version stamp

### Bin-wrapper sub-sample (23)

Used for the **Bin-wrapped CLI distribution** purpose. Discovered via GitHub code search on `CLAUDE_PLUGIN_ROOT path:bin`. Non-exhaustive — GitHub code-search pagination caps results.

- [anthril/official-claude-plugins (ppc-manager)](https://github.com/anthril/official-claude-plugins) — Python shim pair + pointer-file pattern
- [damionrashford/trader-os](https://github.com/damionrashford/trader-os) — PEP 723 `uv run --script` shebang across 3 plugins
- [brunoborges/ghx](https://github.com/brunoborges/ghx) — Bash wrapper + lazy Go binary download
- [Lykhoyda/rn-dev-agent](https://github.com/Lykhoyda/rn-dev-agent) — Bash scripts as git symlinks into `scripts/`
- [JordanCoin/pdf-to-text](https://github.com/JordanCoin/pdf-to-text) — Bash, ROOT + DATA fallback
- [SkinnnyJay/wiki-llm](https://github.com/SkinnnyJay/wiki-llm) — Shell wrapper → `python3` direct
- [mdproctor/cc-praxis](https://github.com/mdproctor/cc-praxis) — Bash wrapper
- [ChanMeng666/claude-code-audio-hooks](https://github.com/ChanMeng666/claude-code-audio-hooks) — Standalone `python3` script
- [Emasoft/token-reporter-plugin](https://github.com/Emasoft/token-reporter-plugin) — Python wrapper, v2.1.91+ reference
- [K-dash/typemux-cc](https://github.com/K-dash/typemux-cc) — Committed native binary + bash wrapper
- [heliohq/ship](https://github.com/heliohq/ship) — Plugin-root location printer
- [iVintik/codeharness](https://github.com/iVintik/codeharness) — Bash → node
- [hwuiwon/autotune](https://github.com/hwuiwon/autotune) — Bash main CLI + statusLine
- [stellarlinkco/myclaude](https://github.com/stellarlinkco/myclaude) — Node CLI self-installer
- [ShaheerKhawaja/ProductionOS](https://github.com/ShaheerKhawaja/ProductionOS) — Bash with ROOT fallback
- [a3lem/my-claude-plugins](https://github.com/a3lem/my-claude-plugins) — Standalone `python3`
- [777genius/claude-notifications-go](https://github.com/777genius/claude-notifications-go) — POSIX `sh` + lazy Go download (OS/arch detect)
- [robertnowell/marketing-pipeline](https://github.com/robertnowell/marketing-pipeline) — Bash with explicit `source activate`
- [SankaiAI/ats-optimized-resume-agent-skill](https://github.com/SankaiAI/ats-optimized-resume-agent-skill) — Bash + `.cmd` pair
- [jmylchreest/aide](https://github.com/jmylchreest/aide) — `env bun` shebang over Go binary
- [Chulf58/FORGE](https://github.com/Chulf58/FORGE) — Node `forge.js` + `.cmd` pair
- [lukasmalkmus/moneymoney](https://github.com/lukasmalkmus/moneymoney) — User-PATH-first resolution with lazy download fallback
- [skullninja/coco-workflow](https://github.com/skullninja/coco-workflow) — Minimal script-relative bash

**Sample gaps disclosed.** GitHub code-search APIs cap results and pagination is unreliable. Bin-wrapper sub-sample seeds on `CLAUDE_PLUGIN_ROOT path:bin` — misses repos that use only script-relative resolution. Primary-sample community repos are 12 of ~24 that survived filters out of the first 400 probed of 1,491 unique plugin-source repos listed in `anthropics/claude-plugins-community`. Distributions above are valid for the samples; the global population may differ.
