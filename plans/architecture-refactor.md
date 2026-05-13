# Architecture refactor

Skills-as-atomic-unit architecture with hybrid distribution. Each capability is a folder following the universal `<skill-name>/SKILL.md` format. Two distribution channels deliver them: marketplace plugin install (`/plugin install <plugin>@<marketplace>`) for users who want bundles, and individual user-scope install (`npx skills add ...`) for users who want one skill at a time. This project uses the npx channel for its own consumption while preserving plugin install as a first-class downstream option.

## Goal

Reduce always-on context cost while making skills mainstream-discoverable on aggregators and individually installable. Plugins remain a packaging convenience for marketplace bundles; the source-of-truth content is skill folders. Domain-based plugin bucketing (Phase G) replaces the monolithic `ocd` plugin with thematic bundles.

## Architecture

### Three-mechanism content delivery

**Rules system — always-on discipline library.** Curated behavioral disciplines that fire on every utterance (honesty, principled-pushback, trigger-specificity, etc.). Deployed to `<scope>/.claude/rules/dependencies/` (flat). Project opts into specific rules via the `rules` skill. New behavioral content defaults to skills, not rules — rules are the always-on layer for disciplines that genuinely cannot be reach-for.

**Skills — reach-for capabilities.** Procedural workflows, tool bridges, behavioral guides. Standard mainstream `<skill-name>/SKILL.md` folder format — folder names hyphenated per agentskills.io spec. Frontmatter `description` does double-duty: discoverable on marketplaces AND cognitive-trigger-precise. Body shape: triggers + command topography; deeper procedural content reached via `Call: _<component>.md` or `uv run -m scripts.<verb> <args>` invocation. Flat layout — `_<verb>.md` and `_<component>.md` siblings of SKILL.md; underscore prefix signals "called only, never opened directly." Python implementation lives in `<skill>/scripts/`.

**Dependencies — shared content.** Single canonical copy at `<scope>/.claude/dependencies/<name>.md`. Sources declare deps in a `## Dependencies` body section using `[[name]]` wikilinks. Discovery is filesystem-based: skill workflow finds the deployed file at session-fire time; auto-deploys from skill-bundled seed at `<skill-base>/_dependencies/<name>.md` on first miss. Two access patterns share the same root files:

1. **Skill-declared deps** — the active skill's workflow lists its deps; they auto-load when the skill fires.
2. **Situational user load** — a planned skill (Phase H) lets the user pull a convention into context on demand for any task, regardless of which skill is active.

### Distribution model — hybrid (both channels first-class)

**Plugin packaging (marketplace surface).** N thematic plugins from this source repo, each bundling a curated set of skills. Users installing via `/plugin install <plugin>@<marketplace>` get the bundle atomically. Plugin manifests in `.claude-plugin/marketplace.json` carve the repo into packaging units. Mirrors anthropics/skills (multiple plugins per repo).

**Individual skill installation (npx surface).** Each skill folder is independently portable. Users (and this project itself) install via `npx skills add <owner>/<repo> --skill <name> -g`, which symlinks the skill folder into `~/.claude/skills/<name>/`. Per the discovery convention, the skill appears in the agent's `<available_skills>` registry mid-session — no restart required. This is the path this project uses for its own consumption per `.claude/installed-skills.json`.

Both materialize from the same source repo. The npx path benefits from Claude Code's user-scope discovery without depending on plugin install correctness (currently affected by harness regression [#15178](https://github.com/anthropics/claude-code/issues/15178)).

### Source repo layout

```
<repo-root>/
├── .claude-plugin/
│   └── marketplace.json          # defines N thematic plugin bundles
├── plugins/                       # domain-organized plugin packages
│   ├── <domain>/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json
│   │   └── skills/                # skill folders (one per skill, hyphenated)
│   │       └── <skill-name>/
│   │           ├── SKILL.md
│   │           ├── composition.md  # present only for composed skills
│   │           ├── _<verb>.md      # internal verb workflows
│   │           ├── _<component>.md # internal sub-procedures
│   │           ├── scripts/        # python implementation
│   │           └── _dependencies/  # bundled seeds for runtime resolution
│   └── ...
├── shared/                        # cross-skill canonicals (deps, scripts)
└── README.md
```

`composition.md` is the marker for composed skills (built via `skill-composer`) — it travels with the skill regardless of which domain plugin holds it. No separate "composed-skills" bucket; composition is a *how it was made* attribute, not a *what domain* attribute.

### Plugin compartmentalization

Domain-based plugin bucketing. Migrate skills out of the legacy `ocd` plugin into domain plugins as Phase G executes. Active proposal:

- `plugins/git/` — version-control operations (currently `plugins/ocd/skills/git/`)
- `plugins/discipline/` — `rebuild`, `rules` (currently `plugins/ocd/skills/{rebuild,rules}/`)
- `plugins/skill-authoring/` — `skill-creator`, `skill-composer` (unchanged)
- Future domains as new skills land (e.g., `python` for `claude-python` composition)

The `ocd` plugin retires once its skills move out. The `composed-skills` plugin retires alongside the bucket concept. The source repo stays one unit; plugin manifests carve it as packaging convenience.

### skill-authoring plugin

Meta-plugin for skill authoring discipline. Two skills:

| Skill | Purpose |
|---|---|
| `skill-creator` | Author a new skill from scratch via dialogue + scaffolding |
| `skill-composer` | Author a new skill from one or more exemplar source skills with drift tracking against pinned commits |

Both apply PFN + progressive-disclosure + description-authoring + workflow-vs-script disciplines inline. Composer's drift tracking lives in each composition's `composition.md`. Direct install of unmodified upstream skills is covered by `npx skills add`; skill-authoring focuses on the authoring + composition layer.

### Hook scoping — Pattern B for installer skills

Per [Hooks doc](https://code.claude.com/docs/en/hooks):

- **Pattern A** — skill frontmatter declares `hooks:`. Lifecycle-scoped to skill activation.
- **Pattern B** — skill body deploys hook config to `<scope>/.claude/settings.json` on invocation. Persistent.

Permissions becomes a standalone Pattern B skill (Phase F).

### MCP benching

Existing MCP servers (transcripts, navigator) move to bash-CLI-only via their existing `ocd-run <system> <verb>` interfaces (Phase D). MCP servers cost always-on tool definitions even when unused; bash CLIs cost zero until invoked. Reactivate MCPs when a context-cost case demonstrates they're worth the always-on overhead.

### What dies

- `bin/<plugin>-run` dispatcher pattern (`bin/ocd-run`, `bin/ocd-path`) — community pattern is direct `uv run -m scripts.<verb>` invocation
- `plugins/<plugin>/run.py` module loader — same fate as the dispatcher
- Underscored skill folder names (`needs_map`, etc.) — agentskills.io spec mandates `[a-z0-9-]+`
- The `composed-skills` plugin bucket — composition history travels via `composition.md`, location organizes by domain
- Discovery substrate (`triggers.md`, `CLAUDE.md` operational refs at system level) — folded into SKILL.md
- The `convention_gate` hook + `.claude/conventions/` deployment directory — conventions become situationally-loaded dep files
- Tagline frontmatter — description does both general-purpose discovery and cognitive-trigger work
- `includes/excludes` path-glob mechanism — replaced by frontmatter-description triggering

### What survives

- State location convention — plugin data dir for cache and per-project state keyed on path-hash
- Dependencies layer — leave-on-uninstall, no refcount
- Rules system — always-on discipline library
- MCP servers themselves (benched, not deleted) — reactivate when justified
- Plugin install path — preserved as a first-class downstream distribution channel

## Phases

### Phase A — Decisions and plan ✓ done

Captured in `plans/architecture-refactor.md` (this file) and the relevant `logs/decision/*.md`.

### Phase B — Build skill-authoring plugin ✓ shipped

skill-authoring landed with `skill-composer` + `skill-creator`. Final design (after several pivots captured in `logs/decision/progressive-skill-composer.md`):

- Hyphenated folder names; `scripts/` Python package; uniform `uv run -m scripts.<verb>` invocation
- Compose verb workflow with `composition.md` as alignment doc + pinned source provenance
- `--destination <user|project|path>` accepts any path including custom bundle locations
- skill-composer focuses on composition + drift tracking; `npx skills add` covers unmodified upstream install

The skill-authoring *plugin install* path is no longer used by this project (we run the skills via npx at user scope) but remains available for downstream consumers.

### Phase C — Pilot conversion ✓ done

`git` skill migrated from `plugins/ocd/systems/git/` to `plugins/ocd/skills/git/` (2026-05-12); validated the post-refactor authoring shape end-to-end including the AIA-cluster dependency pattern.

### Phase D — Transcripts and navigator off MCP — pending

Both systems still in `plugins/ocd-old/systems/`. Migrate each to skill format bridging the existing `ocd-run <system> <verb>` bash CLI; remove MCP server registration to recover always-on context cost.

### Phase E — Convert remaining ocd-old systems to skill format — in progress

Pending systems with `SKILL.md` in `plugins/ocd-old/systems/`: transcripts, needs-map, check, pdf, sandbox, log, navigator, setup, retrospective, refactor.

For each:

- Move to `plugins/<domain>/skills/<skill-name>/` (hyphenated); domain bucket per Phase G layout
- Author SKILL.md per format conventions
- Extract verbs and components to `_<name>.md` siblings
- Move Python implementation into `skills/<skill-name>/scripts/`; replace `ocd-run <sys> <verb>` invocations with `uv run -m scripts.<verb>`
- Update marketplace.json to include the migrated skill in the appropriate plugin bundle
- PFN sweep on the migrated skill's procedural content

When the last system migrates, the dispatcher infrastructure retires:

- Delete `plugins/ocd-old/bin/ocd-run`, `bin/ocd-path`, `run.py`
- Delete `plugins/ocd-old/dependencies/environment.py`, `errors.py` (or inline what scripts still need)
- Strip propagation rules from `.githooks/pre-commit` for the deleted shared files
- Revoke `ocd-run`/`ocd-path` allowlist entries in `.claude/settings.json`

### Phase F — Permissions to Pattern B — pending

1. Author permissions skill that, on invocation, deploys hook config to `<scope>/.claude/settings.json`
2. Verify hook continuity — hooks fire on every Bash call regardless of permissions skill activation
3. Remove permissions from setup system; setup loses one of its reasons to exist
4. Possibly: setup system fully dissolves once all its verbs are absorbed elsewhere

### Phase G — Plugin compartmentalization — active next

1. Define domain plugin layout — `plugins/git/`, `plugins/discipline/`, `plugins/skill-authoring/` (kept), plus future domain plugins as new skills land
2. Move `plugins/ocd/skills/git/` to the `git` domain plugin
3. Move `plugins/ocd/skills/{rebuild,rules}/` to the `discipline` domain plugin
4. Update `marketplace.json` to list the new domain plugins
5. Retire `plugins/ocd/` and `plugins/composed-skills/` plugin shells
6. Update `.claude/installed-skills.json` manifest entries' `plugin` fields to match new domain plugins so version-tracking continues
7. Update any cross-references in docs and skill workflows

### Phase H — Conventions as situational-load skill — pending

Conventions stay as dependency files (`<scope>/.claude/dependencies/<name>.md`). A new user-facing skill lets the user call a convention into context on demand for any task. Same root files; two access patterns:

- **Skill-declared deps** — skill's workflow lists deps that auto-load when the skill fires (existing pattern)
- **User-driven on-demand load** — new skill takes a convention name and loads it into context regardless of which skill is active (this phase)

Pre-work done: `convention_gate` hook removed; `.claude/conventions/` directory wiped from this project; canonicals remain at `plugins/ocd-old/systems/conventions/templates/` as source-of-truth pending migration.

### Phase I — Decision log review — active this session

Walking `logs/decision/*.md` against final implementation. Per the survey:

- ESSENTIAL (8): keep as-is — blueprint, database, framework, mcp, navigator, principles, skill-architecture, skill-authoring
- SLIM (6): trim options-considered scaffolding, drop resolved-context preludes — check, log, mcp-benching, ocd-run-self-update, progressive-skill-composer (large; possibly deferred), sandbox
- REFRAME (4): update framing to reflect post-pivot reality — hook-scoping, pdf, plugin-compartmentalization, state-location
- OBSOLETE (1): delete — yagni-revocation (one-time rule-removal record; no ongoing rationale; covered in skill-architecture.md)

## AIA cluster — agent-instruction-authoring

Shared dependencies governing how agent-facing instructions are authored. Current members in `shared/_dependencies/`:

- `process-flow-notation.md` — workflow notation spec
- `trigger-specificity.md` — single-mechanism + right-level (principle, not symptom)
- `description-authoring.md`, `concise-prose.md`, `file-decomposition.md`, `progressive-disclosure.md` (and others) — see `.claude/rules/dependencies/` for the current always-on set

Access patterns (Phase H formalizes the on-demand path):

1. **Skill-declared** — skills list deps in their `## Dependencies` body section using `[[name]]` wikilinks; deps auto-resolve and load when the skill fires
2. **On-demand** — user calls a convention into context for a given task via a planned Phase H skill; same root files, different access path

## Stopgap: manual rules deployment

Until the rules-skill rebuild ships full coverage, this project deploys the always-on rules set manually via the `rules` skill's `install` verb. The current deployed set lives in `.claude/rules/dependencies/` (flat); see `plugins/ocd/skills/rules/_dependencies/` and `shared/_dependencies/` for the source canonicals.

## Open questions

- **Hook lifecycle empirical verification** — Pattern A may fire only during skill invocation, or whenever the skill is loaded for discovery. Test before any Pattern A skill ships hooks expecting always-on behavior.
- **Multi-skill disambiguation rule** — when conversation context surfaces multiple parallel skill opportunities, agent should show the user candidates and let them pick. New always-on rule when authored.
- **Permissions Pattern B against subagent contexts** — does the deployed settings.json hook fire in spawned subagent contexts the same way as in the main agent? Verify before relying on it.
- **Domain plugin naming** — `git`, `discipline`, `skill-authoring` is the current proposal; finalize during Phase G start.

## State

Phases A, B, C complete. Phase E in progress (git migrated; 10 systems remain in `ocd-old`). Phase G next-up (domain reorg + composed-skills strip). Phase I active this session. Phases D, F, H pending.

Pre-refactor artifacts surviving as legacy infrastructure: `plugins/ocd-old/bin/ocd-run`, `bin/ocd-path`, `run.py`, `dependencies/environment.py`, the permissions allowlist for `ocd-path` and `ocd-run`. All retire when Phase E completes.
