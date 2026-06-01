# Architecture refactor

Skills-as-atomic-unit architecture with hybrid distribution and first-class plugin-deps composition. Each capability is a self-contained `<skill-name>/SKILL.md` folder. Plugins bundle cohesive skill sets and compose via Claude Code's 2026 plugin-deps mechanism (semver-pinned, declared in `plugin.json`). Two distribution channels deliver them: marketplace plugin install for bundles, `npx skills add` for individual skills.

Grounded in `logs/research/ai-coding-tool-survey/consolidated.md` (shapes #2 plugin marketplace with deps, #10 skills as units, #16 skill/rule distribution via package registry) and the 2026-05-19 community survey of multi-skill composition patterns.

## Goal

Reduce always-on context cost while making skills mainstream-discoverable and individually installable. Plugins are cohesive packaging units composing via plugin-deps — not bundles of everything-and-the-kitchen-sink. Skills are the atomic unit and source of truth.

## Architecture

### Skills as the atomic unit

Each skill is fully self-contained in `<skill-name>/SKILL.md`:

- Standard `name`, `description`, `argument-hint`, `allowed-tools` frontmatter per `agentskills.io` spec
- Body shape: process flow; components reached via `Call: _<component>.md`; scripts invoked via `cd <THIS-FILE-DIR> && python3 -m scripts <verb>`
- Flat layout — `_<verb>.md` and `_<component>.md` siblings of SKILL.md; underscore prefix signals "called only, never opened directly"
- Python implementation in `<skill>/scripts/`; vendor minimal helpers inline rather than introduce cross-skill shared modules

No shared content files across skills. No `## Dependencies` declarative blocks. No resolver script. Cross-skill references happen by prose invocation: `/skill-name` or namespace-qualified `/plugin:skill-name` when disambiguation matters.

Grounded in Anthropic's own `anthropics/skills` repo pattern — each skill self-contained; where genuine reuse exists (the `claude-api` skill's `shared/`), it sits *inside* one skill, not across them.

### Plugin composition via plugin-deps

Claude Code shipped [first-class plugin dependencies](https://code.claude.com/docs/en/plugin-dependencies) in 2026:

- Plugins declare deps on other plugins in `.claude-plugin/plugin.json` with semver pins via `{plugin-name}--v{version}` git tags
- `claude plugin disable` refuses if another enabled plugin depends on it
- Cross-marketplace deps via `allowCrossMarketplaceDependenciesOn`

A consuming plugin (e.g., `git`) declares `dependencies` on the bundles its skills invoke (e.g., `writing`, `communication`). Users installing `git` automatically get the dep bundles. Cross-skill invocation resolves through the global skill registry; namespace-qualified form (`/writing:concise-prose`) guarantees the source when name collisions exist.

This supersedes the prior `## Dependencies` + `_read_deps.py` + pre-commit-propagation machinery — that solved the same problem at the file level before Anthropic shipped it at the plugin level.

### Distribution model — hybrid (both channels first-class)

**Plugin packaging.** N cohesive plugins from this source repo. `.claude-plugin/marketplace.json` lists them. Users installing via `/plugin install <plugin>@<marketplace>` get the bundle plus its declared deps atomically.

**Individual skill installation.** Each skill folder is independently portable. Users install via `npx skills add <owner>/<repo> --skill <name> -a claude-code -g`, which lands at `~/.claude/skills/<name>/` (use `-a claude-code` — the default lands at `~/.agents/skills/` which Claude Code doesn't scan). Personal-scope and plugin-scope live in different namespaces; no collision.

This project consumes its own skills via the npx path per `.claude/installed-skills.json`.

### Source repo layout

```
<repo-root>/
├── .claude-plugin/
│   └── marketplace.json          # defines the plugins below
├── plugins/
│   ├── <plugin-name>/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       # name, version, dependencies: [...]
│   │   └── skills/
│   │       └── <skill-name>/
│   │           ├── SKILL.md
│   │           ├── _<verb>.md       # internal verbs
│   │           ├── _<component>.md  # internal sub-procedures
│   │           ├── composition.md   # present only for composed skills
│   │           └── scripts/         # python implementation
│   └── ...
└── README.md
```

`composition.md` is the marker for composed skills built via `skill-composer` — travels with the skill. No separate "composed-skills" bucket.

### Plugin inventory

Each plugin is a cohesive bundle. Plugin-deps wire cross-plugin needs.

| Plugin | Purpose | Skills |
|---|---|---|
| `git/` | Version-control discipline | git (verbs: commit, checkpoint, ci, push, release), checkpoint |
| `transcripts/` | Transcript querying | transcripts (9 verbs) |
| `writing/` | Prose/artifact authoring discipline | concise-prose, description-authoring, markdown-authoring, process-flow-notation, reauthor, rule-authoring |
| `communication/` | Agent⇄user interaction discipline | honesty, principled-pushback, confirm-shared-intent |
| `testing/` | Testing discipline | test-authoring, test-driven-development, test-maintenance, testing-decisions |
| `design/` | Engineering design discipline | agent-first-interfaces, borrow-before-build, clean-break, composability, fix-foundations-not-symptoms, graceful-degradation, structure-as-documentation, workflow-vs-script, file-decomposition, progressive-disclosure |
| `pdf-plus/` | One-shot markdown→PDF rendering | pdf-plus |
| `skill-authoring/` | Skill creation + maintenance | skill-creator, skill-composer, rules |
| `permissions/` (pending — #20) | Hook-based permission management | permissions |
| `navigator/` (future) | Project navigation (post-MCP) | navigator |

### Naming framing

Discipline skills invoke as `apply /<skill-name>` — e.g., "apply /concise-prose when writing the commit message." Names stay specific; truncating to short adjectives loses information (tested via "be /X" framing, abandoned in favor of "apply /X").

Renames executed during Phase G:

- `concise` → `concise-prose` (specificity; the skill is about prose, not just brevity)
- `markdown` → `markdown-authoring` (parallels `description-authoring`)
- `rebuild` → `reauthor` (verb-form noun; clearer authoring framing than reconstruction connotation)

`process-flow-notation` promoted from a shared dep file to its own skill in `writing/`, with scope narrowed to control-flow-bearing workflows (conditionals, loops, variable binding, sub-routine calls, error handling, nested indented blocks). Plain numbered markdown lists don't need PFN.

### Rules skill

The `rules` skill (in `skill-authoring/`) elevates a skill to always-on guidance by appending a prose directive to CLAUDE.md:

- `/rules add <skill>` — append a `Read /<skill>` (or similar) directive between sentinel comments for idempotent edit
- `/rules remove <skill>` — strip the directive
- `/rules list` — show current always-on directives

The skill body stays at its canonical location; only the directive lives in CLAUDE.md. Simple; refine as use exposes friction.

### Hook scoping

- **Pattern A** — skill frontmatter declares `hooks:`. Lifecycle-scoped to skill activation.
- **Pattern B** — skill body deploys hook config to `<scope>/.claude/settings.json` on invocation. Persistent.

The `permissions/` plugin is Pattern B by definition.

### MCP benching

Existing MCP servers move to bash CLI via per-skill `python3 -m scripts <verb>` invocation (Phase D). MCP servers cost always-on tool definitions even when unused; bash CLIs cost zero until invoked. Reactivate MCP only when an always-on case justifies the overhead.

### What dies

- `bin/<plugin>-run` dispatchers (`bin/ocd-run`, `bin/ocd-path`)
- `plugins/<plugin>/run.py` module loader
- `composed-skills` plugin bucket
- `convention_gate` hook + `.claude/conventions/` deployment directory
- Tagline frontmatter — `description` does both discovery and trigger work
- `includes/excludes` path-glob mechanism — replaced by frontmatter-description triggering
- `## Dependencies` body sections + `[[wikilink]]` resolution
- `_read_deps.py` and pre-commit propagation tooling
- `shared/_dependencies/` directory at repo root
- `markdown-dependency-resolution` skill
- Three-mechanism content delivery model (rules + skills + deps) — skills-only is the architecture
- `plugins/ocd/` and `plugins/ocd-old/` shells once skills disperse to new plugin homes

### What survives

- Skills-as-folder format (`SKILL.md` + siblings + `scripts/`)
- Plugin install path — first-class downstream distribution
- `composition.md` marker for composed skills
- MCP servers themselves (benched, not deleted) — reactivate when justified
- State location convention — plugin data dir for cache; per-project state keyed on path-hash

## Phases

### Phase A — Decisions and plan ✓ done

Captured in this file and `logs/decision/*.md`.

### Phase B — skill-authoring plugin ✓ done

Shipped with `skill-creator` + `skill-composer`. Final design in `logs/decision/progressive-skill-composer.md`. Gains `rules` skill in Phase G.

### Phase C — Pilot conversion ✓ done

`git` skill migrated 2026-05-12. Validated post-refactor authoring shape end-to-end.

### Phase D — Transcripts and navigator off MCP — partially done

- Transcripts CLI-from-MCP migration ✓ done 2026-05-19. Moved to `plugins/transcripts/` in Phase G. Storage-location move and content hash-reference table tracked as a separate workstream in `plans/transcripts.md` (the CLI migration completed the MCP exit but left those two pieces unfinished).
- Navigator pending. Same CLI-from-MCP migration pattern; navigator's storage-location move parallels transcripts' and should follow the pattern that `plans/transcripts.md` lands (top-level path under `~/.claude/`).

### Phase E — Convert remaining ocd-old systems — in progress

8 systems remain in `plugins/ocd-old/systems/`: needs-map, check, pdf, sandbox, log, navigator, setup, refactor. `retrospective` migrated 2026-05-21 to `plugins/memory/skills/retrospective/`.

For each:

- Author SKILL.md per format conventions; move to `plugins/<target-plugin>/skills/<skill-name>/`
- Extract verbs and components to `_<name>.md` siblings
- Move Python into `scripts/`; replace `ocd-run` invocations with `python3 -m scripts.<verb>`
- Vendor minimal dependencies inline (transcripts migration pattern); no cross-skill shared modules
- Update marketplace.json for the plugin home

When the last system migrates:

- Delete `plugins/ocd-old/bin/ocd-run`, `bin/ocd-path`, `run.py`
- Delete `plugins/ocd-old/dependencies/environment.py`, `errors.py`
- Strip propagation rules from `.githooks/pre-commit`
- Revoke `ocd-run`/`ocd-path` allowlist entries in `.claude/settings.json`

### Phase F — Permissions plugin — pending

1. Author `plugins/permissions/` with a Pattern B skill that deploys hook config on invocation
2. Verify hook continuity across sessions and subagent contexts
3. Remove permissions verbs from `setup` system
4. `setup` dissolves once all verbs absorb elsewhere

### Phase G — Plugin compartmentalization — mostly complete (2026-05-19)

Architecture finalized + execution landed in one session. 9 of 10 sub-tasks done; #20 (permissions plugin authoring) is the remaining lift.

Plugin layout finalized per inventory above. Sub-tasks:

1. Create `plugins/{writing,communication,testing,design}/` shells with `plugin.json` and `skills/` directories
2. Move the 21 discipline skills from `.claude/skills/` to their target plugin's `skills/` directory
3. Apply renames: `concise` → `concise-prose`, `markdown` → `markdown-authoring`
4. Move `plugins/ocd/skills/git/` to `plugins/git/`
5. Move `plugins/ocd/skills/transcripts/` to `plugins/transcripts/`
6. Move `plugins/ocd/skills/rules/` to `plugins/skill-authoring/skills/rules/`; refactor to CLAUDE.md-directive deployment model
7. Author `plugins/permissions/` (Phase F overlaps here)
8. Declare initial cross-plugin deps in each `plugin.json`:
   - `git/` → `["writing", "communication"]` (checkpoint composes commit messages applying writing + communication discipline)
   - `skill-authoring/` → `["writing", "communication"]`
   - Other deps as workflows surface them
9. Update `marketplace.json` to list the new plugins
10. Retire `plugins/ocd/` and `plugins/composed-skills/` shells
11. Delete `markdown-dependency-resolution` skill
12. Delete `shared/_dependencies/` and `_read_deps.py`; strip propagation rules from `.githooks/pre-commit`
13. Update `.claude/installed-skills.json` `plugin` fields
14. Update cross-references in docs and skill workflows

### Phase H — RETIRED

Original "conventions as situational-load skill" no longer applies. Under skills-only architecture, `/skill-name` invocation IS the situational-load mechanism. The `rules` skill covers the user-driven always-on promotion path.

### Phase I — Decision log review — active

Walking `logs/decision/*.md` against final implementation. Per the survey:

- ESSENTIAL (8): keep as-is — blueprint, database, framework, mcp, navigator, principles, skill-architecture, skill-authoring
- SLIM (6): trim options-considered scaffolding — check, log, mcp-benching, ocd-run-self-update, progressive-skill-composer, sandbox
- REFRAME (4): update framing post-pivot — hook-scoping, pdf, plugin-compartmentalization, state-location
- OBSOLETE (1): delete — yagni-revocation

18 of 19 logs reviewed per TASKS.md; one remains.

## Open questions

- **Plugin-dep version pinning conventions** — how strict do we pin (caret? exact?). Sketch a release-tag discipline alongside the first cross-plugin dep we declare.
- **Hook lifecycle empirical verification** — Pattern A may fire only during skill invocation, or whenever the skill is loaded for discovery. Test before any Pattern A skill ships hooks expecting always-on behavior.
- **Multi-skill disambiguation** — when conversation context surfaces multiple parallel skill opportunities, agent should show the user candidates and let them pick. Currently captured in `rule-authoring` authoring guidance.
- **Permissions Pattern B in subagent contexts** — does the deployed `settings.json` hook fire in spawned subagent contexts the same way as in the main agent? Verify before relying on it.
- **`/rules` directive wording** — exact text appended to CLAUDE.md (`Read /<skill>` vs `Always apply /<skill> when ...` vs `@<absolute-path-to-SKILL.md>` import syntax). Defer until first implementation surfaces what the model actually responds to.
- **Default deps for tooling plugins** — most tooling plugins (git, transcripts, navigator) arguably benefit from `writing` + `communication`. Decide per-plugin during Phase G execution, or set a default convention for tooling plugins.
- **Name-collision behavior on short alias** — when two plugins ship the same skill name, the namespaced form (`plugin:name`) always disambiguates but the short `/name` alias resolution is undocumented (open Anthropic issue [#50486](https://github.com/anthropics/claude-code/issues/50486)). Audit our marketplace for name overlap before publishing.

## State

Phases A, B, C complete. Phase D partial — transcripts CLI-from-MCP done 2026-05-19 (state-location + content extraction tracked in `plans/transcripts.md`), navigator pending. Phase E in progress (9 systems remain). Phase G in progress (architecture finalized this session, execution next). Phase F pending. Phase H retired. Phase I active.

Pre-pivot infrastructure surviving as legacy: `plugins/ocd-old/bin/ocd-run`, `bin/ocd-path`, `run.py`, `dependencies/environment.py`, the permissions allowlist. All retire when Phase E completes.
