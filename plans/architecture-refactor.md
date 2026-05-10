# Architecture refactor

Pivot to a skills-as-atomic-unit architecture. Plugins become packaging conveniences for marketplace surface; the actual content is skills in a standard mainstream folder format. A new meta-plugin (`progressive-composer`) provides the missing ergonomic layer for individual skill management — track repos, install selectively, refactor third-party skills into our progressive-disclosure shape. Rules-system retains the always-on discipline library; conventions migrate to opt-in categorical skills; MCP servers benched until a context-cost case justifies their reactivation.

What survives from prior architectural work: the `bin/ocd-path` and `bin/ocd-run` self-update layer (committed as `c16433f`), the state-location convention (`logs/decision/state-location.md`), and the manifest-diff self-update mechanism (`logs/decision/ocd-run-self-update.md`).

## Goal

Reduce always-on context cost while making our skills mainstream-discoverable on aggregators (skillsmp.com, anthropic-style marketplaces, etc.) and individually installable for users who want only specific capabilities. Every skill is a folder following the universal `<skill-name>/SKILL.md` format. Plugin packaging is one of two parallel distribution paths: marketplace-surface (`/plugin install`) and individual-skill-surface (progressive-composer + direct `~/.claude/skills/` clone).

## Architecture

### Three-mechanism content delivery

**Rules system — always-on discipline library.** Curated behavioral disciplines that fire on every utterance (honesty, principle-not-symptom, fix-foundations-not-symptoms, etc.). Deployed to `<scope>/.claude/rules/<plugin>/<system>/`. Project opts into specific rules at install. New behavioral content defaults to skills, not rules — rules are the always-on layer for disciplines that genuinely cannot be reach-for. See `logs/decision/skill-architecture.md` for the categorization tests.

**Skills — reach-for capabilities.** Procedural workflows, tool bridges, behavioral guides, conventions. Standard mainstream `<skill-name>/SKILL.md` folder format. Frontmatter `description` does double-duty: discoverable on marketplaces AND cognitive-trigger-precise. Body shape: triggers + command topography; deeper procedural content reached via `Call: _<component>.md` or bash `Call: !` `<plugin>-run <verb>` ``. Flat layout — `_<verb>.md` and `_<component>.md` siblings of SKILL.md; underscore prefix signals "called only, never opened directly." See `logs/decision/skill-authoring.md`.

**Dependencies — shared content.** Single canonical copy at `<scope>/.claude/dependencies/<name>.md`. Sources declare `requires: [<name>, ...]` in frontmatter. Skill body asserts dependency presence at top; bails with corrective message if missing. Lifecycle: install on first need, leave-on-uninstall (no refcount machinery; user-decided artifacts).

### Distribution model — hybrid

**Plugin packaging (marketplace surface).** N thematic plugins from one source repo, each bundling a curated set of skills. Users installing via `/plugin install <bundle>@<marketplace>` get the bundle atomically. Mirrors anthropics/skills (17 skills across 3 plugins). This is the discovery path most Claude Code users will reach for.

**Standalone skill installation (individual surface).** Skills work at runtime when copied directly to `~/.claude/skills/<skill>/SKILL.md` or `<scope>/.claude/skills/<skill>/SKILL.md` per the documented `Where skills live` table. progressive-composer is the ergonomic layer for this path: track repos/marketplaces, clone unmodified, install selectively, refactor on demand. See `logs/decision/progressive-composer.md`.

Both paths materialize from the same source repo. Plugin manifests bundle subsets; skill folders are independently portable.

### Source repo layout — anthropic-style

```
<repo-root>/
├── .claude-plugin/
│   └── marketplace.json          # defines N thematic plugin bundles
├── skills/                        # all skills as folders (one per skill)
│   ├── <skill-name-1>/
│   │   ├── SKILL.md
│   │   ├── _<verb>.md             # internal verb workflows (called only)
│   │   ├── _<component>.md        # internal reusable sub-procedures
│   │   ├── README.md              # optional, when substantial
│   │   └── ARCHITECTURE.md        # optional, when substantial
│   ├── <skill-name-2>/
│   └── ...
├── dependencies/                  # cross-skill shared content (PFN, etc.)
└── README.md
```

### Plugin compartmentalization

Thematic plugin buckets — multiple plugins from this single source repo, organized by domain. Migrate skills out of `ocd` plugin one at a time as each refactor completes. New plugins fork off naturally as content shape locks. The source repo stays one unit; plugin manifests carve it as packaging convenience. See `logs/decision/plugin-compartmentalization.md`.

### progressive-composer plugin

New meta-plugin. Scope:

- Track external repos and marketplaces (config file: tracked sources, last-sync timestamps, sync mode per skill)
- Clone unmodified to a managed cache (preserves source author's work; license respect)
- Install selected skills to scope `.claude/skills/`
- Sync at session start for source-tracking skills (auto-update); intelligent recheck for reimplemented (refactored) skills
- Refactor third-party skills into progressive-disclosure shape on demand
- Personal-track via branch — user can maintain own customizations as a branch of the core plugin, usable across machines

Fills the ergonomic gap the official Claude Code distribution doesn't provide: anthropic's marketplace surface is plugin-grained only; individual skill install is a manual `git clone + cp` operation today. See `logs/decision/progressive-composer.md`.

### Hook scoping — Pattern B for installer skills

Per [Hooks doc](https://code.claude.com/docs/en/hooks):

- **Pattern A** — skill frontmatter declares `hooks:`. Lifecycle-scoped to skill activation; cleaned up when skill finishes. Useful for skill-internal observation.
- **Pattern B** — skill body deploys hook config to `<scope>/.claude/settings.json` on invocation. Persistent. Continues firing regardless of skill activation. Used for installer skills (e.g., permissions).

Permissions becomes a standalone Pattern B skill — its body, on invocation, modifies settings.json to install the enforcement hooks. No plugin packaging required for hook continuity. See `logs/decision/hook-scoping.md`.

### MCP benching

Existing MCP servers (transcripts, navigator) move to bash-CLI-only via their existing `ocd-run <system> <verb>` interfaces. MCP servers cost always-on tool definitions even when unused; bash CLIs cost zero until invoked. Reactivate MCPs when a context-cost case demonstrates they're worth the always-on overhead. See `logs/decision/mcp-benching.md`.

### YAGNI revocation

The yagni rule is removed (template + deployed copy). YAGNI conflicts with the user's forward-thinking development style; rules we don't personally use don't get maintained or proofed. See `logs/decision/yagni-revocation.md`.

### What dies

- Discovery substrate (`triggers.md` per-system routing files) — folded into SKILL.md frontmatter description + body
- CLAUDE.md operational refs at system level — body subsumes; SKILL.md is the entrypoint
- Workflows/components folder distinction — flatten to `_<verb>.md` + `_<component>.md` siblings of SKILL.md
- install.md/uninstall.md handlers — plugin install IS the install for non-installer skills; Pattern B for installers
- Tagline frontmatter — description does both general-purpose discovery and cognitive-trigger work
- Setup system — mostly dissolves; permissions becomes its own Pattern B skill; remaining setup verbs absorbed into progressive-composer or removed
- includes/excludes path-glob mechanism — already gone; replaced by frontmatter-description triggering
- Conventions deployment directory — conventions become categorical skills (opt-in, project-shape-changing)
- YAGNI rule — removed
- Self-described location discipline — scoped to wrap/shim mode in progressive-composer only; not a general improvement

### What survives

- `bin/ocd-path` — useful when progressive-composer wraps third-party skills with a shim that resolves cache paths
- `bin/ocd-run` self-update — manifest-diff before exec; transparent plugin upgrades
- State location convention — bin-mediated state to plugin data dir; user-edited artifacts in project tree
- Dependencies layer — simplified (leave-on-uninstall, no refcount; `<scope>/.claude/dependencies/` location since they're Claude Code framework infrastructure)
- Rules system — always-on discipline library
- MCP servers themselves (benched, not deleted) — reactivate when justified

## Phases

### Phase A — Decisions and plan (this commit)

Captured in:

- `plans/architecture-refactor.md` (this file)
- `logs/decision/skill-architecture.md` — distribution model, atomic skills, rules-retains, conventions-as-skills
- `logs/decision/skill-authoring.md` — folder format, body shape, flat layout, frontmatter discipline (extends prior decision log)
- `logs/decision/progressive-composer.md` — meta-plugin scope
- `logs/decision/plugin-compartmentalization.md` — thematic split, plugins as packaging
- `logs/decision/hook-scoping.md` — Pattern A vs B
- `logs/decision/mcp-benching.md` — context cost
- `logs/decision/yagni-revocation.md` — design philosophy

Surviving from prior architectural work (no changes):

- `logs/decision/state-location.md`
- `logs/decision/ocd-run-self-update.md`

### Phase B — Build progressive-composer plugin

> Foundational meta-plugin. Built before migrating any of our content because it's the install path we'll use on ourselves.

1. Scaffold `progressive-composer/` source tree following the anthropic-style repo layout
2. Implement repo/marketplace tracking — config file storing tracked sources, last-sync timestamps, sync mode per skill (synced vs reimplemented)
3. Implement clone-unmodified pipeline — `git clone` to managed cache; preserve LICENSE and metadata
4. Implement individual skill install — copy `<source>/skills/<skill>/` to `<scope>/.claude/skills/<skill>/`
5. Implement session-start sync for source-tracking skills — diff cache against source, refresh on drift
6. Implement intelligent recheck for reimplemented skills — diff cache against last-known-source, surface to user
7. Implement refactor command — operates on a skill folder, produces a progressive-disclosure-shaped variant

### Phase C — Convert one ocd system to validate the format

> Pilot conversion before broadly migrating. Pick a small system without MCP server dependency to firm the new authoring shape.

1. Choose pilot system (likely `log` — moderate complexity, no MCP, well-understood verbs)
2. Author SKILL.md with mainstream-conformant frontmatter (description does discovery + cognitive trigger work)
3. Write body as triggers + command topography
4. Extract verbs to `_<verb>.md` siblings; sub-procedures to `_<component>.md`
5. Verify parity — pilot system produces equivalent output to current system
6. Refine authoring conventions in `skill-authoring.md` decision log if friction surfaces

### Phase D — Migrate transcripts and navigator off MCP

> Bench MCP. Bash CLI becomes the canonical interface.

1. Remove MCP server registration from `plugin.json` for transcripts and navigator
2. Author SKILL.md for each, bridging to existing `ocd-run <system> <verb>` bash CLIs
3. Verify functional parity — same operations reachable, no regression
4. Measure context cost — confirm always-on token reduction

### Phase E — Convert remaining ocd systems to skill format

> Each system migrates as its own focused commit. Order: skill-only systems first (smaller surface), code-bearing systems after.

Pending migrations: refactor, conventions, log (if not pilot), needs_map, sandbox, retrospective, git, check, pdf. Plus convert `init-project-skill` plan into actual skill (`plans/init-project-skill.md` carries scope).

For each:

- Move from `plugins/ocd/systems/<sys>/` to `plugins/<plugin>/skills/<sys>/` (or new plugin if compartmentalization splits this skill out)
- Author SKILL.md per format conventions
- Extract verbs and components to `_<name>.md` siblings
- Update marketplace.json plugin manifests to include the migrated skill in the appropriate bundle
- Remove dead artifacts (CLAUDE.md operational ref, workflows/, components/ folder structure)
- PFN sweep on the migrated skill's procedural content (`plans/pfn-sweep.md` lands per-system, not as a separate pass)

### Phase F — Permissions to Pattern B

1. Author permissions skill that, on invocation, deploys hook config to `<scope>/.claude/settings.json`
2. Verify hook continuity — hooks fire on every Bash call regardless of permissions skill activation
3. Remove permissions from setup system; setup loses one of its reasons to exist
4. Possibly: setup system fully dissolves once all its verbs are absorbed elsewhere

### Phase G — Plugin compartmentalization

> Thematic split materializes as marketplace.json evolves.

1. Audit current ocd skills by domain — identify natural thematic clusters (rules, workflows, navigation, conventions, etc.)
2. Define plugin manifests in marketplace.json — each bundle includes its cluster's skills
3. Migrate ocd plugin to be one of N thematic plugins (its scope shrinks as systems move out)
4. Document the split in plugin manifests; users can install bundles independently

### Phase H — Conventions migration

> Conventions become categorical skills — opt-in, project-shape-changing. The user understands installing them accepts shape influence; rules are too strong for this content class.

1. Cluster current conventions (system-structure, claude-md, plans-md, tasks-md, plugin-system, etc.) into thematic skill groupings
2. Author one skill per cluster; body indexes the conventions in that cluster, reaches them via `_<convention>.md` files or inline
3. Remove the deployed `<scope>/.claude/conventions/` directory; convention bodies move into skill bodies
4. Update install flow (now via progressive-composer) to surface conventions-skills as opt-in additions

### Phase I — Decision log review

> User-committed cleanup pass.

1. Review each `logs/decision/*.md` against final implementation
2. Slim decision logs that were comprehensive scaffolding to essential rationale + final shape
3. Remove options-considered branches that are no longer relevant

## Open questions

- **Hook lifecycle empirical verification** — "active" in the Hooks doc is not precisely defined. Pattern A may turn out to fire only during invocation, or whenever the skill is loaded for discovery. Test before any Pattern A skill ships hooks expecting always-on behavior.
- **Multi-skill disambiguation rule** — when conversation context surfaces multiple parallel skill opportunities, agent should show the user the candidates and let them pick. Becomes a new always-on rule when authored.
- **Dev-mode trigger-recording** — instrumentation hook that records skill-trigger evaluations to a log for usage analysis. Mechanism (hook? settings flag?) deferred.
- **Spawn agents without rules** — research item. Selective rule exclusion for subagent contexts. Future task.
- **In-the-wild comparison** — compare each ocd skill (post-refactor) to existing equivalents on aggregators; improve or retire candidates per the user's "use what's already there" disposition.
- **progressive-composer refactor mode** — when it produces a refactored variant of a third-party skill, how is that tracked relative to source? Branch-based? Separate repo? Resolve during Phase B implementation.
- **Permissions Pattern B against subagent contexts** — does the deployed settings.json hook fire in spawned subagent contexts the same way it fires in the main agent? Verify before relying on it.
- **Corpus research prompt** — drafted earlier; on hold per user direction until new corpus questions surface.

## State

Phase A in progress (this commit). Phase B is next pickup.

What's already committed from prior architectural work that survives:

- `plugins/ocd/bin/ocd-path` (`c16433f`) — useful for progressive-composer's refactor mode if it produces wrapping shims for third-party skills
- `plugins/ocd/bin/ocd-run` self-update (`c16433f`) — transparent plugin upgrades; preserved
- Permissions allowlist for `ocd-path` (`9fb1b5e`, unpushed) — clean checkpoint cycle should push it before Phase B begins

Doc rot scope: `plugins/ocd/README.md` and `plugins/ocd/ARCHITECTURE.md` describe pre-refactor mechanisms (convention-gate hook, includes/excludes). Holistic rewrite when Phase E or G completes — not chip-by-chip during the migration. Same for project-root `ARCHITECTURE.md` if it references defunct mechanisms.
