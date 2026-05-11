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

## Hyphenated folder names per agentskills.io spec

### Context

The [agentskills.io specification](https://agentskills.io/specification) and the [Claude Code skills doc](https://code.claude.com/docs/en/skills) require skill names to match `[a-z0-9-]+` — lowercase alphanumerics and hyphens only. The `name` field must match the parent directory name.

The current `plugins/ocd/systems/` tree uses underscored folder names for multi-word systems (`needs_map`, `progressive_composer`), driven by a self-imposed constraint: the folders are imported as Python packages by `bin/ocd-run` via `runpy.run_module("systems.<name>")`, and Python identifiers cannot contain hyphens.

Corpus research surveyed `anthropics/skills` (17 skills) and four community repos (~330+ skills total). Every skill folder is hyphenated. None violate the spec rule. The Python-import constraint is universally resolved by *not importing the skill folder*: Python lives in a child directory (`scripts/`, `core/`, `lib/`) which carries its own underscore-friendly name, while the parent stays hyphenated and is only ever a filesystem location.

### Options Considered

**Keep underscored folders, prioritize Python-import ergonomics.** Rejected: violates the agentskills.io spec; diverges from every surveyed skill in the wild; would fail the official `skills-ref validate` tool; readers familiar with skills don't recognize the shape.

**Hyphenate folders, decouple Python package from folder name (`needs-map/lib/needs_map/`).** Rejected: spec-compliant but retains the bespoke wrapper-dispatcher layer that has no community precedent; readers still encounter an unfamiliar shape.

**Hyphenate folders, move Python into `scripts/` per community pattern.** Adopted.

### Decision

Every skill folder is hyphenated. Multi-word skills follow the community pattern: `slack-formatting/`, `progressive-skill-composer/`, `needs-map/`. The folder name matches the SKILL.md frontmatter `name` field (the spec mandates this).

Python implementation moves into a child directory (`scripts/` is the dominant convention in `anthropics/skills`; `core/` and `lib/` appear in some community repos). The child directory uses an underscore-friendly name and is the importable Python package. The skill folder itself is never imported — it is only ever a filesystem path.

### Consequences

- **Enables:** spec compliance; mainstream-conformant folder names; recognition by `skills-ref validate`; alignment with every surveyed skill
- **Constrains:** any tooling that walks `plugins/<plugin>/skills/` must accept hyphens in folder names; existing ocd `systems/<sys>/` underscored folders need migration during Phase E of the architecture refactor

## Python lives in `scripts/`, invoked relative to skill root

### Context

With folders hyphenated, the question becomes how the Python implementation is laid out and invoked. Corpus research found a uniform community pattern across `anthropics/skills` and surveyed third-party repos.

### Decision

Python implementation lives at `<skill>/scripts/` as a Python package (with `__init__.py` when intra-script imports are needed) or as flat scripts (when each script stands alone). SKILL.md invokes scripts with relative paths, with cwd at the skill root:

```
python scripts/<verb>.py <args>
python -m scripts.<module> <args>          # when scripts/ is a package
uv run scripts/<verb>.py <args>            # when deps are needed (PEP 723)
```

Companion subdirectories follow the same naming flexibility — `core/`, `lib/`, `helpers/` — chosen by the skill author when `scripts/` doesn't fit. The constraint is consistent: the Python package lives one level below the skill folder, never IS the skill folder.

The `_<verb>.md` workflow files (per *Flat layout*) sit alongside `scripts/` and SKILL.md at the skill root, not inside `scripts/`. Markdown workflows and Python implementation are sibling concerns — neither nests the other.

### Consequences

- **Enables:** Python imports work from inside the skill via `from scripts.foo import bar`; mainstream pattern recognized by every reader familiar with skills; trivial to invoke (`cd <skill> && python scripts/...`)
- **Constrains:** SKILL.md procedures must establish cwd at the skill root before invoking scripts; tools that resolve paths from outside the skill folder (e.g., from a project root) need to anchor on the skill folder explicitly

## Dependencies via `uv run`, no plugin-level venv dispatcher

### Context

The current `bin/<plugin>-run` dispatcher resolves a plugin venv (per `logs/decision/ocd-run-self-update.md`) and execs into `runpy.run_module`. It supports manifest-diff self-update, multi-mode venv discovery (Claude Code cache, --plugin-dir, dev checkout), and PATH-accessible bare-name invocation.

Corpus research found zero community skills using a wrapper-dispatcher layer. The dominant pattern for skills with deps is PEP 723 inline-script declarations consumed by `uv run`:

```python
# /// script
# dependencies = ["openpyxl>=3.1"]
# ///

import openpyxl
...
```

`uv run` resolves and caches dependencies per-invocation transparently. No plugin-managed venv. No discovery layer. No self-update on manifest drift — `uv` handles that internally. The same `uv run` invocation works for stdlib-only scripts (no deps to resolve, just runs Python).

### Options Considered

**Retain `<plugin>-run` for venv self-update; coexist with community pattern.** Rejected: the dispatcher is the foundation our existing pattern is built on; keeping it for some skills and not others creates two parallel mechanisms. Mainstream conformance means the wrapper layer goes for new skills.

**Adopt `uv run` uniformly; deprecate `<plugin>-run` for new skills.** Adopted.

**Branch invocation by dep state — `python3` for stdlib, `uv run` only when deps declared.** Rejected. Two invocation forms across one skill family creates surface area for drift: SKILL.md examples, agent-side recall, and tests all encode the form. A script that starts stdlib-only and later adds a single dep would force every consumer to update their invocation. Uniform `uv run` removes the branching entirely; the cost — `uv` as a prerequisite even for stdlib-only scripts — is the same `uv` that the community ecosystem already standardizes on.

### Decision

All scripts invoke via `uv run`, regardless of dep state:

```
uv run -m scripts.<verb> <args>
```

Cwd is the skill folder. Module-mode (`-m`) suits skills with multiple verbs sharing helpers via package imports (`from scripts._paths import ...`). Single-script skills with no inter-script imports may use `uv run scripts/<verb>.py <args>` instead — both forms are mainstream-conformant; module-mode is the default for our authoring.

`uv` is a soft prerequisite for every skill we ship. Skills declare this in their `## Requirements` section (per *Dependencies declared via `requires:` with body-top assertion*) so the bail-out message points users at the `uv` install instructions when missing.

When a script adds a third-party dependency, the author adds a PEP 723 directive at the top of that script. The invocation form does not change. Existing consumers' workflows do not change.

The existing `bin/ocd-run` and `bin/ocd-path` survive only as long as the ocd plugin's underscored `systems/<sys>/` folders survive. Phase E of the architecture refactor migrates ocd to the community pattern; at the end of that phase, `bin/<plugin>-run` deletes from the ocd plugin entirely.

`progressive-skill-composer` ships under the new pattern from day one — no `bin/`, no `run.py`, no vendored `tools/` package. It pilots the community shape that ocd will eventually match.

### Consequences

- **Enables:** mainstream-conformant invocation; per-invocation dep resolution via `uv` (more robust than manifest-diff self-update because `uv` handles version drift, lockfiles, and isolation natively); no plugin-level venv to manage; skills are independently portable to any of the four locations Claude Code loads from without dispatcher infrastructure; uniform invocation across all scripts means SKILL.md examples and tests don't fork by dep state
- **Constrains:** users without `uv` installed cannot run any of our skills until they install it (acceptable — `uv` is the ecosystem's standard tool for Python dep management and ships as a small static binary); stdlib-only scripts pay a small `uv` startup cost per invocation (~tens of ms) compared to bare `python3`, which is acceptable in exchange for uniform invocation; the `<plugin>-run` self-update mechanism (`logs/decision/ocd-run-self-update.md`) becomes legacy infrastructure scoped to ocd's pre-migration state; `tools/environment.py` propagation across plugins (per `.githooks/pre-commit`) is no longer needed once skills carry their own minimal env-resolution helpers in `scripts/`
- **Migration:** `logs/decision/ocd-run-self-update.md` should carry a supersession note pointing here; ocd's `bin/ocd-run`, `bin/ocd-path`, `run.py`, `tools/environment.py`, `tools/errors.py`, and the `.githooks/pre-commit` propagation rules retire when Phase E completes

