# Architecture refactor

Pivot to a skills-as-atomic-unit architecture. Plugins become packaging conveniences for marketplace surface; the actual content is skills in a standard mainstream folder format. A new meta-plugin (`progressive-skill-composer`) provides the missing ergonomic layer for individual skill management — track repos, install selectively, refactor third-party skills into our progressive-disclosure shape. Rules-system retains the always-on discipline library; conventions migrate to opt-in categorical skills; MCP servers benched until a context-cost case justifies their reactivation.

What survives from prior architectural work: the `bin/ocd-path` and `bin/ocd-run` self-update layer (committed as `c16433f`), the state-location convention (`logs/decision/state-location.md`), and the manifest-diff self-update mechanism (`logs/decision/ocd-run-self-update.md`).

## Goal

Reduce always-on context cost while making our skills mainstream-discoverable on aggregators (skillsmp.com, anthropic-style marketplaces, etc.) and individually installable for users who want only specific capabilities. Every skill is a folder following the universal `<skill-name>/SKILL.md` format. Plugin packaging is one of two parallel distribution paths: marketplace-surface (`/plugin install`) and individual-skill-surface (progressive-skill-composer + direct `~/.claude/skills/` clone).

## Architecture

### Three-mechanism content delivery

**Rules system — always-on discipline library.** Curated behavioral disciplines that fire on every utterance (honesty, principle-not-symptom, fix-foundations-not-symptoms, etc.). Deployed to `<scope>/.claude/rules/<plugin>/<system>/`. Project opts into specific rules at install. New behavioral content defaults to skills, not rules — rules are the always-on layer for disciplines that genuinely cannot be reach-for. See `logs/decision/skill-architecture.md` for the categorization tests.

**Skills — reach-for capabilities.** Procedural workflows, tool bridges, behavioral guides, conventions. Standard mainstream `<skill-name>/SKILL.md` folder format — folder names hyphenated per agentskills.io spec. Frontmatter `description` does double-duty: discoverable on marketplaces AND cognitive-trigger-precise. Body shape: triggers + command topography; deeper procedural content reached via `Call: _<component>.md` or uniform `uv run -m scripts.<verb> <args>` invocation (PEP 723 inline-script directives carry any third-party deps). Flat layout — `_<verb>.md` and `_<component>.md` siblings of SKILL.md; underscore prefix signals "called only, never opened directly." Python implementation lives in `<skill>/scripts/` (or `core/`, `lib/` per author choice), never in the skill folder itself. See `logs/decision/skill-authoring.md`.

**Dependencies — shared content.** Single canonical copy at `<scope>/.claude/dependencies/<name>.md`. Sources declare `requires: [<name>, ...]` in frontmatter. Skill body asserts dependency presence at top; bails with corrective message if missing. Lifecycle: install on first need, leave-on-uninstall (no refcount machinery; user-decided artifacts).

### Distribution model — hybrid

**Plugin packaging (marketplace surface).** N thematic plugins from one source repo, each bundling a curated set of skills. Users installing via `/plugin install <bundle>@<marketplace>` get the bundle atomically. Mirrors anthropics/skills (17 skills across 3 plugins). This is the discovery path most Claude Code users will reach for.

**Standalone skill installation (individual surface).** Skills work at runtime when copied directly to `~/.claude/skills/<skill>/SKILL.md` or `<scope>/.claude/skills/<skill>/SKILL.md` per the documented `Where skills live` table. progressive-skill-composer is the ergonomic layer for this path: track repos/marketplaces, clone unmodified, install selectively, refactor on demand. See `logs/decision/progressive-skill-composer.md`.

Both paths materialize from the same source repo. Plugin manifests bundle subsets; skill folders are independently portable.

### Source repo layout — anthropic-style

```
<repo-root>/
├── .claude-plugin/
│   └── marketplace.json          # defines N thematic plugin bundles
├── skills/                        # all skills as folders (one per skill, hyphenated)
│   ├── <skill-name-1>/            # e.g. progressive-skill-composer, slack-formatting
│   │   ├── SKILL.md
│   │   ├── _<verb>.md             # internal verb workflows (called only)
│   │   ├── _<component>.md        # internal reusable sub-procedures
│   │   ├── scripts/               # python implementation (importable package)
│   │   │   ├── __init__.py
│   │   │   └── <verb>.py
│   │   ├── README.md              # optional, when substantial
│   │   └── ARCHITECTURE.md        # optional, when substantial
│   ├── <skill-name-2>/
│   └── ...
├── dependencies/                  # cross-skill shared content (PFN, etc.)
└── README.md
```

All skills invoke uniformly via `uv run -m scripts.<verb> <args>` regardless of dep state. Stdlib-only skills run unchanged; skills with third-party deps add PEP 723 inline-script directives at the top of the relevant `scripts/*.py` files and `uv run` resolves them transparently. No plugin-level `bin/<plugin>-run` dispatcher, no plugin-level venv — `uv` is a soft prerequisite for every skill we ship. See `logs/decision/skill-authoring.md` § *Dependencies via `uv run`*.

### Plugin compartmentalization

Thematic plugin buckets — multiple plugins from this single source repo, organized by domain. Migrate skills out of `ocd` plugin one at a time as each refactor completes. New plugins fork off naturally as content shape locks. The source repo stays one unit; plugin manifests carve it as packaging convenience. See `logs/decision/plugin-compartmentalization.md`.

### progressive-skill-composer plugin

New meta-plugin. Scope:

- Track external repos and marketplaces (config file: tracked sources, last-sync timestamps, sync mode per skill)
- Clone unmodified to a managed cache (preserves source author's work; license respect)
- Install selected skills to scope `.claude/skills/`
- Sync at session start for source-tracking skills (auto-update); intelligent recheck for reimplemented (refactored) skills
- Refactor third-party skills into progressive-disclosure shape on demand
- Personal-track via branch — user can maintain own customizations as a branch of the core plugin, usable across machines

Fills the ergonomic gap the official Claude Code distribution doesn't provide: anthropic's marketplace surface is plugin-grained only; individual skill install is a manual `git clone + cp` operation today. See `logs/decision/progressive-skill-composer.md`.

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
- Setup system — mostly dissolves; permissions becomes its own Pattern B skill; remaining setup verbs absorbed into progressive-skill-composer or removed
- includes/excludes path-glob mechanism — already gone; replaced by frontmatter-description triggering
- Conventions deployment directory — conventions become categorical skills (opt-in, project-shape-changing)
- YAGNI rule — removed
- Self-described location discipline — supplanted by mainstream invocation; no wrap-mode dispatcher, so no preamble required (see `logs/decision/skill-authoring.md` § *Dependencies via `uv run`*)
- `bin/<plugin>-run` dispatcher pattern (`bin/ocd-run`, `bin/ocd-path`) — community pattern is direct `uv run -m scripts.<verb>` invocation; the dispatcher layer retires when ocd's underscored `systems/<sys>/` migrate during Phase E
- `plugins/<plugin>/run.py` module loader — same fate; module loading was a function of the dispatcher, gone with it
- Underscored skill folder names (`needs_map`, etc.) — agentskills.io spec mandates `[a-z0-9-]+`; every folder hyphenates during Phase E
- Vendored `dependencies/environment.py` and `dependencies/errors.py` propagation across plugins (`.githooks/pre-commit`) — once the dispatcher and `runpy.run_module` chain is gone, env/error helpers either inline into the few scripts that need them or stay scoped to one plugin without cross-plugin propagation

### What survives

- State location convention — plugin data dir for cache and per-project state keyed on path-hash; the location story is unchanged, only the dispatcher that mediates writes goes away. progressive-skill-composer's scripts write directly to data dir without a wrapper layer
- Dependencies layer — simplified (leave-on-uninstall, no refcount; `<scope>/.claude/dependencies/` location since they're Claude Code framework infrastructure)
- Rules system — always-on discipline library
- MCP servers themselves (benched, not deleted) — reactivate when justified

## Phases

### Phase A — Decisions and plan (this commit)

Captured in:

- `plans/architecture-refactor.md` (this file)
- `logs/decision/skill-architecture.md` — distribution model, atomic skills, rules-retains, conventions-as-skills
- `logs/decision/skill-authoring.md` — folder format, body shape, flat layout, frontmatter discipline (extends prior decision log)
- `logs/decision/progressive-skill-composer.md` — meta-plugin scope
- `logs/decision/plugin-compartmentalization.md` — thematic split, plugins as packaging
- `logs/decision/hook-scoping.md` — Pattern A vs B
- `logs/decision/mcp-benching.md` — context cost
- `logs/decision/yagni-revocation.md` — design philosophy

Surviving from prior architectural work (no changes):

- `logs/decision/state-location.md`
- `logs/decision/ocd-run-self-update.md`

### Phase B — Build progressive-skill-composer plugin

> Foundational meta-plugin. Built before migrating any of our content because it's the install path we'll use on ourselves. Pilots the community-pattern shape that ocd will eventually match — hyphenated folder, `scripts/` Python package, no dispatcher.

**Status.** Shipping. Plugin landed as `progressive-skill-composer@a-horde-o-bees` (was originally `progressive-composer`; renamed for ecosystem-coherent naming alongside other `skill-composer` variants). Test suite: 55 plugin tests, 985 project-wide. Cached version advances per commit via pre-commit auto-bump.

**Design pivots after Phase A.** The locked design went through several iterations during implementation; each is captured in detail in `logs/decision/progressive-skill-composer.md`:

1. **Pivot 1 — community-pattern conformance.** Corpus research (~330 skills) showed `bin/<plugin>-run` dispatchers + underscored folders violate the agentskills.io spec. Adopted hyphenated folders, `scripts/` package, uniform `uv run -m scripts.<verb>` invocation.
2. **Pivot 2 — compose vision.** Reframed `refactor` (1:1) into `compose` (many-to-one with persistent design intent).
3. **Pivot 3 — workflow-driven, self-contained skill folders.** Collapsed the separate sources registry / shared cache / working-area design into a single self-contained skill folder model.
4. **Pivot 4 — compose-only, drop install.** Vercel's `npx skills` covers individual install; we don't compete. Composition + drift tracking is our unique value.
5. **Pivot 5 — composition.md as alignment doc.** Dropped `scope`, `goal_summary`, `last_build`, `build_status` fields; restructured body to `# Goal` / `## Surface` / `## Sources` with no historical journal. The skill files are the implementation; composition.md tracks design intent only.
6. **Pivot 6 — `--destination` rename + path form.** `--scope` accepted only `user|project`; renamed to `--destination` accepting any path. Unlocks compositions at custom locations (especially `plugins/composed-skills/skills/` for shareable bundles in this monorepo).
7. **Plugin rename — progressive-composer → progressive-skill-composer.** Positions the plugin alongside ecosystem `skill-composer` variants while the `progressive` prefix names our authoring discipline (PFN + progressive disclosure).

**Current verb surface:**

| Verb | Behavior |
|---|---|
| `compose new --destination <user\|project\|path>` | Script emits resolved state (scope + target path); agent reads `_compose_new.md` and drives dialogue to collect name, intent, Surface, sources |
| `compose refine <name> --destination <user\|project\|path>` | Script emits drift report; agent reads `_compose_refine.md` and drives refinement of design intent |
| `compose build <name> --destination <user\|project\|path> [--force]` | Initial materialization of SKILL.md + `scripts/__init__.py`. Overwrite gate uses filesystem (SKILL.md presence), not a frontmatter flag. Build is one-shot scaffolding, not regeneration; refinement happens directly on SKILL.md afterward |
| `compose list [--destination <user\|project\|path>] [--drift]` | Walks composition.md files at the requested destination(s); reports `deployed` (SKILL.md present) or `draft` per composition |

Agent-internal sub-ops: `compose add-source`, `compose remove-source`, `compose update-sources`, `compose purge-sources`.

**Adjacent infrastructure.**

- `composed-skills` plugin shell (`plugins/composed-skills/`) — pure-packaging bundle where shareable compositions land. Plugin manifest declares `"skills": ["./skills/"]` for auto-discovery. Marketplace entry installable today as `composed-skills@a-horde-o-bees`.
- `plans/composed-skills-workflow.md` — documents the maintainer flow of composing into the bundle, downstream install via `npx skills` or `/plugin install`, and open threads (e.g., `/checkpoint` integration).

**Out of scope (covered elsewhere in the ecosystem):**

- Direct install of unmodified upstream skills — Vercel's `npx skills add <repo> --skill <name>` handles this. README points users at it explicitly.
- Symlink-based auto-fresh upstream tracking — `npx skills` symlinks; updates flow automatically. progressive-skill-composer's drift tracking is for compositions where pinning is the point.

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

> Each system migrates as its own focused commit. Order: skill-only systems first (smaller surface), code-bearing systems after. Migration also hyphenates folder names per the community pattern adopted in `logs/decision/skill-authoring.md`.

Pending migrations: refactor, conventions, log (if not pilot), needs-map, sandbox, retrospective, git, check, pdf.

For each:

- Move from `plugins/ocd/systems/<sys>/` to `plugins/<plugin>/skills/<skill-name>/` (hyphenated; e.g. `needs_map` → `needs-map`); new plugin if compartmentalization splits this skill out
- Author SKILL.md per format conventions
- Extract verbs and components to `_<name>.md` siblings
- Move Python implementation from the old `systems/<sys>/` package layout into `skills/<skill-name>/scripts/`. Replace `ocd-run <sys> <verb>` invocations in markdown with `uv run -m scripts.<verb>` (PEP 723 inline-script directives carry deps where present)
- Update marketplace.json plugin manifests to include the migrated skill in the appropriate bundle
- Remove dead artifacts (CLAUDE.md operational ref, workflows/, components/ folder structure)
- PFN sweep on the migrated skill's procedural content (`plans/pfn-sweep.md` lands per-system, not as a separate pass)

When the last system migrates out of `plugins/ocd/systems/`, the dispatcher infrastructure retires:

- Delete `plugins/ocd-old/bin/ocd-run`, `plugins/ocd-old/bin/ocd-path`, `plugins/ocd-old/run.py`
- Delete `plugins/ocd-old/dependencies/environment.py` and `plugins/ocd-old/dependencies/errors.py` (or inline what scripts still need)
- Strip the propagation rules from `.githooks/pre-commit` for the now-deleted shared files
- Revoke any `ocd-run` and `ocd-path` allowlist entries in `.claude/settings.json`

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

Pre-work already done: `convention_gate` hook removed; `.claude/conventions/` directory wiped from this project (canonicals remain at `plugins/ocd-old/systems/conventions/templates/` as source-of-truth). See "Stopgap: manual rules deployment" above.

1. Cluster current conventions (system-structure, claude-md, plans-md, tasks-md, plugin-system, etc.) into thematic skill groupings
2. Author one skill per cluster; body indexes the conventions in that cluster, reaches them via `_<convention>.md` files or inline
3. Update install flow (now via progressive-skill-composer) to surface conventions-skills as opt-in additions

### Phase I — Decision log review

> User-committed cleanup pass.

1. Review each `logs/decision/*.md` against final implementation
2. Slim decision logs that were comprehensive scaffolding to essential rationale + final shape
3. Remove options-considered branches that are no longer relevant

## Stopgap: manual rules deployment

Until the rules-skill rebuild ships and proper agent-instruction-authoring (AIA) skill bundles its dependencies, this project deploys a minimized always-on rules set manually into `.claude/rules/ocd/`.

**Deployment criterion (current set: 18 files):**

- Substantively revised via concise-output (V8) convergence in this refactor: agent-first-interfaces, borrow-before-build, clean-break, composability, confirm-shared-intent, fix-foundations-not-symptoms, graceful-degradation, honesty, markdown, principled-pushback, purpose-statement, testing, file-decomposition
- Newly authored: concise-output, structure-as-documentation, trigger-specificity (merged from `principle-not-symptom` + the prior `trigger-specificity` — see "AIA cluster" below)
- Foundational shared deps as always-on stopgap: process-flow-notation, dependency-resolution (file-decomposition and trigger-specificity also count, listed above)

Frontmatter-strip-only canonicals (body untouched, e.g., capture-rationale, idempotency, separation-of-concerns) live source-only in `plugins/ocd-old/systems/rules/templates/`. They re-deploy when bundled into the appropriate skill.

**Wiped from deployment in this stopgap:**

- `.claude/rules/ocd/systems/` (log, navigator, refactor system rules) — not actively leveraged during the refactor
- `.claude/conventions/` (full directory) — convention_gate hook was defunct and is removed from `plugins/ocd-old/hooks/hooks.json`; the script `plugins/ocd-old/hooks/convention_gate.py` is deleted
- `.claude/rules/ocd/workflow.md` — split per commit `815ebae` into `working-directory.md` (canonical) + `agent-spawning.md` (canonical) + `components/hook-registered-files.md`; "Push Blocking" dropped as defunct
- `.claude/rules/ocd/system-docs.md` — subsumed by `system-structure.md` convention per commit `40cc819`

## AIA cluster — agent-instruction-authoring

The shared dependencies governing how agent-facing instructions are authored cluster under the working name `agent-instruction-authoring`. Members so far:

- `shared/dependencies/process-flow-notation.md` — the workflow notation spec
- `shared/dependencies/trigger-specificity.md` — single-mechanism + right-level (principle, not symptom) — merged from former `principle-not-symptom.md` and `trigger-specificity.md` rules; convergence ran 3 iterations of concise-output

The eventual AIA-cluster skills (rules, progressive-skill-composer, etc.) will declare these as deps via SKILL.md frontmatter and `_deps.py` will resolve them at invocation time. Until those skills exist, the deps deploy as always-on rules in this project for working continuity.

Open question: does `shared/dependencies/purpose-statement.md` join the cluster? Defer until first AIA skill is built.

## Open questions

- **Hook lifecycle empirical verification** — "active" in the Hooks doc is not precisely defined. Pattern A may turn out to fire only during invocation, or whenever the skill is loaded for discovery. Test before any Pattern A skill ships hooks expecting always-on behavior.
- **Multi-skill disambiguation rule** — when conversation context surfaces multiple parallel skill opportunities, agent should show the user the candidates and let them pick. Becomes a new always-on rule when authored.
- **Dev-mode trigger-recording** — instrumentation hook that records skill-trigger evaluations to a log for usage analysis. Mechanism (hook? settings flag?) deferred.
- **Spawn agents without rules** — research item. Selective rule exclusion for subagent contexts. Future task.
- **In-the-wild comparison** — compare each ocd skill (post-refactor) to existing equivalents on aggregators; improve or retire candidates per the user's "use what's already there" disposition.
- **Permissions Pattern B against subagent contexts** — does the deployed settings.json hook fire in spawned subagent contexts the same way it fires in the main agent? Verify before relying on it.
- **Corpus research prompt** — drafted earlier; on hold per user direction until new corpus questions surface.

## State

Phase A landed in commit `da37142`. Phase B is shipping — `progressive-skill-composer@a-horde-o-bees` is on the marketplace (cached at v0.0.7+, advancing per commit via auto-bump); `composed-skills@a-horde-o-bees` scaffold landed in commit `5180fd7` as the third-destination bridge for shareable compositions. 985 tests pass project-wide; 55 of them on progressive-skill-composer.

Next concrete step: compose `claude-python` into `plugins/composed-skills/skills/` as the first end-to-end exercise of the new workflow. Five exemplar sources identified (`affaan-m/everything-claude-code:python-patterns` + `python-testing`, `laurigates/claude-plugins:uv-run`, `sickn33/antigravity-awesome-skills:python-packaging` + `python-pro`).

Pivot decisions captured in `logs/decision/progressive-skill-composer.md`:

- *Compose verb — workflow-driven, self-contained skill folders* (pivot 3)
- *Meta-plugin scope and rationale* (pivot 4 — compose-only)
- *composition.md as alignment doc, not blueprint* (pivot 5)
- *Destination forms — user, project, or any path* (pivot 6)
- *composed-skills bundle as the third destination* (the bundle)
- *Skill name — progressive-skill-composer* (rename)

The decision to drop `bin/<plugin>-run` and adopt the community pattern arrived during Phase B kickoff after corpus research surveyed `anthropics/skills` and ~330 community skills. Captured in `logs/decision/skill-authoring.md` § *Hyphenated folder names per agentskills.io spec*, *Python lives in `scripts/`*, and *Dependencies via `uv run`*. The earlier `ocd-run-self-update.md` decision is superseded for new skills (kept as the canonical record of what the legacy ocd dispatcher does until Phase E retires it).

Pre-refactor artifacts surviving as legacy infrastructure scoped to ocd's pre-migration state: `plugins/ocd-old/bin/ocd-run`, `plugins/ocd-old/bin/ocd-path`, `plugins/ocd-old/run.py`, `plugins/ocd-old/dependencies/environment.py`, the permissions allowlist for `ocd-path` and `ocd-run`. All retire when Phase E completes the ocd migration.

Doc rot scope: `plugins/ocd/README.md` and `plugins/ocd/ARCHITECTURE.md` describe pre-refactor mechanisms (convention-gate hook, includes/excludes). Holistic rewrite when Phase E or G completes — not chip-by-chip during the migration. Same for project-root `ARCHITECTURE.md` if it references defunct mechanisms.

Mid-refactor turn state (uncommitted at time of writing): the rules slimming campaign processed most rule canonicals via concise-output (V8) convergence; `principle-not-symptom.md` merged into `trigger-specificity.md` and the merged form moved to `shared/dependencies/`; `economy-of-expression.md` renamed to `concise-output.md`; `convention-as-documentation.md` renamed/restructured to `structure-as-documentation.md`; orphan deployed-only `workflow.md` and `system-docs.md` wiped (intent confirmed in commits `815ebae`, `40cc819`); `.claude/rules/ocd/` reduced to 18 always-on files; `.claude/rules/ocd/systems/` and `.claude/conventions/` wiped; `convention_gate` hook removed. See "Stopgap: manual rules deployment" and "AIA cluster" sections above for criterion and member list.
