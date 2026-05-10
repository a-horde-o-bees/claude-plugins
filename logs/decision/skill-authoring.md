---
log-role: reference
---

# Skill Authoring

Decisions governing how skills are structured — shared content, multi-workflow organization, and agent-context isolation.

## Extract shared skill components to files

### Context

Skills with multiple workflows share content blocks (evaluation protocols, criteria catalogs, instruction sets). These blocks are passed to spawned agents as part of their instructions. Agents that receive content they do not need (coordinating agents seeing evaluation constraints, evaluation agents seeing triage criteria) can be confused by conflicting instructions or waste context on irrelevant material.

### Options Considered

**Inline `## Components` section in SKILL.md** — components defined as subsections, referenced by name in workflows. Orchestrator extracts and bundles referenced components when dispatching to agents. Disqualified: orchestrator pre-reads and inlines content, agents receive everything bundled in their prompt, coordinating agents see evaluation instructions they should not act on (caused a real conflict where recursion constraint told coordinating agent not to spawn subagents while its own instructions told it to).

**Extracted `_{name}.md` files alongside SKILL.md** — components as separate files in skill directory. Workflow steps include explicit `Read _file.md` instructions. Each agent reads only files it needs at execution time.

### Decision

Extract components to `_{name}.md` files. Underscore prefix signals internal (consistent with `_{purpose}.py` pattern for internal Python modules). Workflows include explicit read steps. Orchestrator does not pre-read component files — workflow steps dictate when files are read and by whom.

For multi-agent workflows: coordinating agents pass file read instructions to subagents without reading the files themselves. This prevents coordinating agents from being influenced by content meant for evaluation or execution agents.

### Consequences

- **Enables:** precisely scoped agent context; coordinating agents never see conflicting instructions; SKILL.md stays focused on routing and workflow structure; component files can grow without bloating SKILL.md (500-line convention limit applies to SKILL.md, not total)
- **Constrains:** more files per skill directory; workflows must include explicit read steps; component file paths are relative to skill directory
- **Trade-off:** single-workflow components can stay as workflow subsections per convention; extraction is for content shared across 2+ workflows or content that must be isolated from certain agents

## Mainstream `<skill-name>/SKILL.md` folder format

### Context

The architecture refactor (see `skill-architecture.md`) moves to skills as the atomic unit of distribution. Skill aggregators (skillsmp.com and similar) and the official Claude Code marketplace both index `<skill-name>/SKILL.md` as the canonical layout. Authoring discipline must conform on the discoverable surface.

### Options Considered

**OCD-specific layout — invent our own structure.** Rejected: sacrifices mainstream discoverability; aggregators wouldn't index our skills correctly; users coming from elsewhere wouldn't recognize the format.

**Mainstream conformance on discoverable surface; extend on body conventions (invisible to discovery).** Adopted.

### Decision

Every skill is a folder named after the skill, containing `SKILL.md` as the entry point. Companion files in the same folder follow established patterns from anthropics/skills and similar repos: `README.md` (when substantive), `ARCHITECTURE.md` (when substantive), `LICENSE.txt` (when applicable), supporting markdown files (with naming convention determined by the body shape — see *Flat layout*), `scripts/` for executable helpers, `assets/` for static assets.

Frontmatter discipline: only `description` is universally required. `allowed-tools` declares tool access where relevant. Other fields (tags, version, hooks) are optional and used per the standard semantics. Never invent OCD-specific frontmatter fields that displace discoverable ones.

Body conventions extend mainstream — invisible to discovery layers, so we can author them without breaking compatibility. See *Body shape* and *Flat layout* below.

### Consequences

- **Enables:** mainstream discoverability via aggregators; users coming from other ecosystems recognize the format immediately; skill folders are independently portable to any of the four locations Claude Code loads from
- **Constrains:** discovery-surface fields can't be repurposed for OCD-specific semantics; every skill must work as a standalone folder, not assume sibling files outside its own directory
- **Migration:** `plugins/ocd/systems/<sys>/` reorganizes to `plugins/<plugin>/skills/<sys>/`; SKILL.md becomes the entry point; auxiliary system files relocate to skill-folder siblings

## Frontmatter description does discovery and cognitive trigger work

### Context

The prior architecture used a separate `triggers.md` routing layer to encode cognitive moments → skill invocations. That created a parallel routing mechanism alongside Claude Code's native frontmatter-description-based skill discovery. With the substrate dissolved (see `skill-architecture.md`), the description field has to carry both general-purpose discovery copy AND cognitive-trigger precision.

### Options Considered

**Two fields — separate description (discovery) and trigger (cognitive recognition).** Rejected: invents an OCD-specific frontmatter field that mainstream consumers won't parse; fragments authoring; the work the trigger field would do can be folded into the description with the right phrasing.

**Description does double-duty.** Adopted.

### Decision

The frontmatter `description` field is authored to be simultaneously general-purpose-discoverable AND cognitive-trigger-precise. Anthropic's pattern is the model: "Use when X situation arises. Provides Y by Z." The "Use when X" portion serves as the cognitive trigger; the "Provides Y by Z" portion serves discovery copy.

Authoring discipline:

- Lead with the cognitive moment (when this should fire) — first sentence
- Follow with the capability summary (what this provides) — second sentence
- Keep concise — descriptions display in marketplace listings and aggregator UIs; long descriptions get truncated
- Avoid OCD-jargon that would confuse a mainstream reader; if domain-specific, frame the moment generically enough for cross-context recognition

The description must be enough that the agent reads it, recognizes whether the conversation context matches, and decides to read the body for triggers and topography. Don't bloat the description with comprehensive trigger lists — the body holds those.

### Consequences

- **Enables:** mainstream discoverability AND sharp cognitive triggering in a single field; one authoring discipline; no parallel routing mechanism
- **Constrains:** description authoring is harder — must serve two purposes well; tradeoff between brevity (discovery) and precision (triggering); requires research/calibration on what mainstream descriptions look like (corpus prompt drafted earlier covers this)
- **Tagline frontmatter dies:** a separate `tagline:` field was used in the prior model for terse summaries. Subsumed by the description — no separate field needed

## Body subsumes the operational reference (CLAUDE.md collapse)

### Context

The prior architecture had a system-level `CLAUDE.md` operational reference reached via `Call: !` `<plugin>-path <system>` `` from the deployed shim. This put a "deeper ref" tier between the shim body and the verb workflows. Most systems' content didn't justify the tier — the shim body was thin (one Call:), and CLAUDE.md was where the meaningful content lived.

### Options Considered

**Keep two layers — thin shim + deeper CLAUDE.md operational ref.** Rejected: extra hop adds no value when the body could carry the topography directly; weakens progressive disclosure (one more layer to traverse before reaching meaningful content).

**Shim body subsumes the operational reference.** Adopted.

### Decision

The system-level `CLAUDE.md` operational reference dies. The deployed `SKILL.md` body carries triggers + command topography directly. Verb workflows reached via `_<verb>.md` siblings; sub-procedures via `_<component>.md` siblings.

Effect on the bin layer:

- `ocd-run` self-update: still relevant (manifest diff, transparent plugin upgrades)
- `ocd-path`: role narrows. No longer used by every shim to resolve cache CLAUDE.md. Still useful when progressive-composer wraps third-party skills with a path-resolving shim — keeps the bin available for that mode

### Consequences

- **Enables:** tighter progressive disclosure (frontmatter description → body → reached files, no middle layer); fewer files per system; SKILL.md body is the meaningful content rather than a redirect
- **Constrains:** body content must be substantive enough to serve as the operational reference, not just a routing surface; for systems that genuinely need a deeper reference, that content lives in `_<component>.md` siblings or in `ARCHITECTURE.md`

## Flat layout — verbs and components as siblings

### Context

The prior model distinguished `workflows/<verb>.md` (top-level entry points for verbs) from `components/_<name>.md` (reusable sub-procedures). The user identified the line as blurry — workflows can call workflows, components can call components, the distinction was structural without behavioral payoff. Plus: shorter `Call:` paths matter at every reference site.

### Options Considered

**Keep `workflows/` and `components/` folders.** Rejected: longer paths in every Call: reference; the role distinction is encoded in naming convention (underscore prefix) so the folder split is redundant.

**Flatten — verbs and components as siblings of SKILL.md.** Adopted.

### Decision

Skill folder layout is flat:

```
<skill-name>/
├── SKILL.md           # entry point
├── _<verb>.md         # verb workflows (called only, never opened directly)
├── _<component>.md    # reusable sub-procedures (called only)
├── README.md          # optional
└── ARCHITECTURE.md    # optional
```

All called-only files use the underscore prefix. Verbs are component files (the underscore says "called by something else"); the only entry point is SKILL.md itself. SKILL.md body invokes verbs via `Call: _<verb>.md`; verbs invoke sub-procedures via `Call: _<component>.md`. Relative paths default — the agent resolves Call: refs against the file currently being read.

### Consequences

- **Enables:** shorter Call: paths at every reference site; one authoring location to scan; underscore convention does the role-encoding work that folders previously did
- **Constrains:** large skills with many verbs/components produce a flat directory; mitigated by skill scoping (a skill with too many components is probably two skills); README.md and ARCHITECTURE.md sit alongside the underscore-prefixed files but are visually separable
- **Naming discipline:** never put an entry point inside a skill folder without the underscore (the underscore signals "internal, called only"); never reference an underscore-prefixed file from outside the skill folder (cross-skill calls go through the other skill's SKILL.md)

## Body shape — triggers and command topography

### Context

With CLAUDE.md collapsed and the body carrying the operational content, the question is what the body should contain. Options range from "minimal triggers + a single Call:" to "full procedure inlined."

### Options Considered

**Inline full procedure in SKILL.md body.** Rejected: bloats the body that loads on every invocation; defeats progressive disclosure (component files exist for this reason).

**Body is just triggers — every action reaches into a `_<verb>.md`.** Rejected: forces a Call: hop for trivial operations; loses the natural place for command topography (the surface map of "what this skill can do").

**Body is triggers + command topography — entry-level overview that points into deeper files for specifics.** Adopted.

### Decision

SKILL.md body shape:

- **Triggers section** — articulated cognitive moments (sharper than the frontmatter description) and what each routes to. Used by the agent after the frontmatter has surfaced the skill; the body's triggers refine the recognition.
- **Command topography** — surface map of verbs and entry points the skill provides. Each pointed at a `_<verb>.md` workflow or a bash invocation (`Call: !` `<plugin>-run <verb>` ``). Treats the body as a navigation hub.
- **Optional inline** — short content that doesn't warrant a separate file (e.g., a quick reference table, a short discipline statement for a behavioral skill). Behavioral skills with no procedures may have body content that IS the discipline elaboration; procedural skills point at `_<verb>.md` files.

The body should answer: "Should the agent go deeper, and if so, where?" Not: "How does the skill execute end-to-end?" That's what the verb workflows are for.

### Consequences

- **Enables:** progressive disclosure layered into the skill itself — frontmatter (always-on) → body (on invocation) → verb workflows (on Call:); body is the navigation surface, not the implementation
- **Constrains:** body length must stay tight — long bodies defeat the lazy-load benefit of `_<verb>.md` extraction; behavioral skills with no procedures need to consciously decide what their body holds (discipline statement, examples, principles?)
- **Open:** corpus research on mainstream skill body conventions can refine these specifics — what section headers are common, what length norms are typical, when do bodies inline content vs reach via Call:

## Self-described location scoped to wrap mode

### Context

During the design conversation, the question came up of whether SKILL.md should self-describe its location at the top so Call: refs know they're relative. The user concluded this is only necessary when the skill is invoked non-normally (e.g., wrapped by another skill that's the actual entry point). For native skill invocations, the agent already has the path context.

### Decision

Self-described location is not a general SKILL.md authoring requirement. It's scoped to progressive-composer's wrap-mode — when progressive-composer creates a shim that points at a different skill, the shim states the wrapped skill's location so Call: refs in the wrapped content resolve correctly. Native skill authoring uses relative paths from the file currently being read; the agent's path context handles the rest.

### Consequences

- **Enables:** simpler authoring discipline for native skills — no required preamble; Call: paths just work relative to the current file
- **Constrains:** progressive-composer's wrap-mode needs to handle path resolution correctly when it inserts a shim layer between caller and wrapped content; designed-in during Phase B implementation

## Dependencies declared via `requires:` with body-top assertion

### Context

Skills sometimes depend on shared content (PFN, dependency-management conventions, etc.) or on other skills/rules being installed at scope. Two needs: declarative dependency specification (so install machinery can deploy required deps); runtime assertion (so the skill bails clearly if deps aren't installed when invoked).

### Options Considered

**No dependency mechanism — skills work standalone with all content inlined.** Rejected: defeats the dependencies layer (PFN duplication across N skills); no mechanism for cross-skill prerequisites.

**Frontmatter `requires:` + body-top assertion check.** Adopted.

### Decision

Skill frontmatter declares `requires: [<dep-or-skill>, ...]`. At install time, dependency content gets deployed to `<scope>/.claude/dependencies/<name>.md` (per the dependencies layer's lifecycle). At invocation time, the SKILL.md body opens with an assertion check — verifies required deps/skills are installed at scope, bails with a corrective message naming what's missing if not.

The assertion lives in body content (not frontmatter) so the agent reading the body sees it before reaching the meaningful content. Pattern:

```markdown
## Requirements

- <plugin>-rules system (any scope)
- /<plugin>-honesty skill installed

If any of the above are missing, stop. Tell user what's missing and how to install.
```

For cross-system or cross-plugin requirements, `requires:` lists the canonical name; the assertion looks across user and project scope to determine presence.

### Consequences

- **Enables:** declarative deps for install machinery; clear runtime failure mode when deps missing; cross-skill prerequisites without coupling skills tightly
- **Constrains:** authoring discipline must keep `requires:` and the body-top assertion in sync; the assertion is agent-readable text, not a deterministic check (agent-faithful execution required); future tightening could move assertion to a deterministic check via bin tool if needed

