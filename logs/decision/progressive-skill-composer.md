---
log-role: reference
---

# Progressive Composer

Decisions governing the meta-plugin that composes new skills from one or more exemplar sources, with our authoring discipline (PFN + progressive disclosure) baked into the output. Drift tracking against pinned upstream commits. Self-contained skill folders for cross-machine portability.

## Meta-plugin scope and rationale

### Context

The skills-as-atomic-unit architecture (see `skill-architecture.md`) prompted a meta-plugin to fill ergonomic gaps in the Claude Code skill ecosystem. Initial scope included track/install/sync verbs alongside compose, on the premise that no first-class tool existed for individual skill management.

Mid-Phase B research surveyed the broader ecosystem (Vercel's `npx skills`, `agent-skills-cli`, `ccpi`, multiple aggregators including skillsmp.com, agentskills.in, skills.sh) and revealed the install surface is well-covered. Vercel's `npx skills` is npm-distributed, polished, Vercel-backed; it sparse-symlinks individual skills from any GitHub repo into `~/.claude/skills/`. Competing on installation duplicates Vercel.

Two niches remain genuinely unoccupied:

1. **Composition** — synthesizing a new skill from multiple exemplar sources against a user-articulated goal, with the recipe + provenance persisted alongside the output. No surveyed tool composes; existing tools install or generate from scratch (e.g., Anthropic's `skill-creator` plugin) but don't take exemplars as inputs.
2. **Per-skill upstream drift tracking** — `npx skills` symlinks (auto-fresh) but doesn't surface drift against pinned snapshots; `ccpi` is plugin-level; nothing is per-skill drift-aware.

### Options Considered

**Bundle install + compose into one plugin.** Earlier framing. Rejected after research: install is a crowded space (Vercel, Karanjot, ccpi); our only value-add over Vercel is composition.md drift tracking — useful but secondary to the headline composition story. Bundling dilutes the plugin's pitch and forces competition with Vercel.

**Compose-only meta-plugin with PFN + progressive-disclosure baked into output.** Adopted. Sharper scope, matches the unoccupied niches, complementary to Vercel rather than competing.

### Decision

`progressive-skill-composer` is a compose-only meta-plugin. Scope:

| Capability | Behavior |
|---|---|
| Compose new skills | Workflow-driven dialogue collects skill name + exemplar sources + goal; `compose new` opens the workflow, agent drives the conversation, sources are embedded via per-skill sparse-checkout into the deployed skill folder. |
| Authoring discipline baked in | `compose build` materializes composition.md into a deployed SKILL.md + `_<verb>.md` workflow files + `scripts/` package skeleton, all structured per progressive-disclosure (frontmatter + body triggers + verb topography pointing at Call: refs) with PFN notation in workflow files. The agent's subsequent refinement via Edit tool fleshes out specifics; the layered structure is non-negotiable. |
| Drift tracking against pinned upstream | composition.md frontmatter pins each source's `(url, ref, commit)`. `compose list --drift` and `compose refine`'s entry use `git ls-remote <url> <ref>` (non-mutating) to compare upstream HEAD to pinned commit. User decides whether to update via `compose update-sources`. |
| Cross-machine portability | Self-contained skill folders. `git init` `<scope>/.claude/skills/<name>/` and push to whatever remote you want; clone elsewhere to bring the composition (recipe + embedded sources + output) along. No plugin-level sync verbs. |

What progressive-skill-composer does NOT do (covered by Vercel's `npx skills`):

- Direct install of upstream skills kept as-is — use `npx skills add <repo> --skill <name>`
- Symlink-based auto-fresh upstream tracking — `npx skills` symlinks; updates flow through automatically. progressive-skill-composer's drift tracking is for compositions where pinning is the point.

### Consequences

- **Enables:** unique value in the ecosystem (composition + drift tracking are unoccupied territory); sharper plugin pitch; complementary to Vercel rather than competing; output skills automatically conform to PFN + progressive-disclosure discipline (a value-add over generic compose tools)
- **Constrains:** users wanting straight install reach for `npx skills`, not us — README must point at it explicitly to avoid confusion; we can't claim "manage all your skills" since Vercel covers half that surface. We can claim "design new skills from exemplars with discipline."
- **Discovery surface:** `/plugin install progressive-skill-composer` for users wanting the compose toolchain; the plugin's own SKILL.md frontmatter description leads with composition value (NOT installation, which is Vercel's space)
- **Migration:** the prior in-flight install/uninstall verbs and `type: install|composed` discriminator are dropped; composition.md schema simplifies (no type field; all entries are compositions)

## Distribution model — both paths from one source

### Context

With progressive-skill-composer providing individual-skill install, the question is whether we keep plugin packaging at all, or go standalone-only.

### Options Considered

**Standalone-only — drop plugin packaging.** Rejected: official `/plugin install` UX is the discovery path most users reach for; abandoning it loses marketplace-surface visibility entirely.

**Plugin-only — drop standalone install path.** Rejected: defeats the meta-plugin's value; users wanting individual skills can't get them.

**Both paths from the same source.** Adopted. Plugin manifests bundle subsets of skills; skill folders are independently portable. Same source content materializes to both paths.

### Decision

The source repo ships:

- `.claude-plugin/marketplace.json` defining N thematic plugin bundles (marketplace surface for `/plugin install` users)
- `skills/<skill>/` folders that are independently portable (standalone surface for progressive-skill-composer / direct `~/.claude/skills/` clone)

Users pick their preferred consumption path:

- `/plugin install <bundle>@<marketplace>` for atomic bundle install
- progressive-skill-composer for individual-skill control with refactoring and source tracking
- Manual `git clone + cp` for users who want neither

### Consequences

- **Enables:** broadest reach across user types; aggregators like skillsmp can index our skills the same way they index any standard-format skill folder
- **Constrains:** marketplace.json must stay accurate as skills move between bundles or new bundles form; both surfaces share the same authoring discipline (the standard format works in both)

## Compose verb — workflow-driven, self-contained skill folders

### Context

Earlier framings treated compose as a sequence of single-shot CLI operations (`compose new`, `compose refine`, `compose build`, `compose recheck`) each producing or consuming a separate working spec at `<scope>/.claude/progressive-skill-composer-a-horde-o-bees/compositions/<output>.md`. Implementation surfaced two problems with that model:

- **Workflow shape was wrong.** Compose isn't a pipeline of discrete steps; it's a building dialogue. The user might add a source, discuss it, refine the goal, change their mind on a source, build, then return weeks later to incorporate upstream changes. Forcing each cognitive moment into its own CLI verb fragmented the experience and made the agent's role (driving dialogue) compete with the script's role (recording state).
- **Storage was over-distributed.** A composition's recipe (working spec), exemplar sources (cache directory), and deployed output (skill folder) lived in three different filesystem locations. Cross-machine portability required syncing all three; sharing a composed skill required bundling them. The composition wasn't a self-contained artifact.

User's clarified vision:

- **`compose new --scope` opens a workflow**, not a single-shot operation. The agent collects the skill name, exemplar sources, and goal articulation through dialogue. Sub-operations (adding sources, fetching them, etc.) are workflow steps the agent invokes — not user-typed verbs.
- **The composed skill folder is the unit of everything**. composition.md (the recipe), `sources/` (embedded exemplars), and SKILL.md + scripts/ (the deployed skill) all live inside one folder under `<scope>/.claude/skills/<name>/`. Cross-machine portability is automatic: the skill folder carries its own state.
- **Sparse-checkout per-skill, not shared-cache.** Each composed skill embeds the exact source skills it depends on at pinned commits, fetched via `git clone --filter=blob:none --sparse` + `git sparse-checkout set <skill-path>`. Multi-version is the default — if two compositions need different refs of the same upstream repo, each gets its own pinned snapshot. No cache management, no version-key derivation, no orphan detection across compositions.
- **Drift detection is non-mutating.** `git ls-remote <url> <ref>` returns the current SHA at HEAD without touching any local clone. `compose list --drift` and `compose refine`'s entry both run this against each source and compare to the pinned commit in composition.md. The pin only advances when the user runs the refine/rebuild workflow and explicitly accepts the upstream changes.

### Options Considered

**Single-shot CLI verbs each producing one stage of the composition.** Rejected: composition is a dialogue; fragmenting it into discrete verbs forced the agent and the script to compete for orchestration, and persistent state lived in three filesystem locations.

**Working area separate from deployed skill folder.** Rejected: required syncing two locations across machines; sharing a composed skill required bundling the spec separately from the deployed output. Self-contained skill folders are simpler.

**Shared cache directory for source clones, indexed by URL+ref.** Rejected: introduced cache management complexity (orphan detection, key derivation, GC) for no real-world benefit. Per-skill sparse-checkouts cost a few MB extra disk per composition and eliminate the cache layer entirely.

**Workflow-driven verbs with self-contained skill folders and per-skill sparse-checkout.** Adopted.

### Decision

Compose is a workflow whose entry points are `compose new` (start) and `compose refine` (re-enter), both orchestration verbs that print state + guidance to drive agent dialogue. `compose build` is the terminal materialize step. `compose list` is the cross-composition status overview. Sub-operations live as agent-internal scripts (not user-facing verbs); the agent invokes them during the workflow.

User-facing verbs:

| Verb | Behavior |
|---|---|
| `compose new --scope <user\|project>` | Open a new-composition workflow. No name, no sources upfront. Script outputs orchestration: agent collects name + goal via dialogue, writes initial composition.md via Write tool using documented templates, calls `compose add-source` for each chosen exemplar, drives goal-articulation dialogue, and eventually invokes `compose build`. |
| `compose refine <name> --scope <user\|project>` | Re-enter an existing composition. Script reads composition.md, runs `git ls-remote` per source for drift detection, prints status report (pinned commit vs upstream HEAD per source) plus orchestration guidance. Agent surfaces drift to user, asks whether to update each drifted source via `compose update-sources`, then drives the refinement dialogue. |
| `compose build <name> --scope <user\|project> [--force]` | Materialize composition.md into the deployed skill — generate SKILL.md from goal + source-mapping + exemplar embeds, advance pinned commits to current `sources/` content. Refuses to overwrite an existing SKILL.md without `--force`. |
| `compose list [--scope <both\|user\|project>] [--drift]` | Walk `<scope>/.claude/skills/*/composition.md` and print one line per composition with name, source count, last-build timestamp, build status. With `--drift`, runs `git ls-remote` per source per composition and reports drift in the output. |

Agent-internal sub-ops (invoked during compose workflows; not surfaced as user-facing verbs):

| Sub-op | Behavior |
|---|---|
| `compose add-source <name> <url>:<skill>[@<ref>] --scope` | Sparse-checkout the named skill folder from upstream into `<scope>/.claude/skills/<name>/sources/<source-slug>/`; append source entry to composition.md frontmatter with `url`, `skill`, `ref`, `commit` fields. |
| `compose remove-source <name> <source-slug> --scope` | Delete `sources/<source-slug>/`; remove corresponding entry from composition.md frontmatter. |
| `compose update-sources <name> [--source <slug>] --scope` | Re-sparse-checkout source(s) at current upstream HEAD; advance `commit` field in composition.md. Without `--source`, updates every source. |
| `compose purge-sources <name> --scope` | Delete the `sources/` subfolder when finalized. composition.md `commit` pins remain — future `compose refine` auto-rehydrates by re-running `compose add-source` against the pinned commits. |

### Storage layout

Each composed skill folder is self-contained:

```
<scope>/.claude/skills/<name>/
├── SKILL.md                      # generated by compose build; PFN-structured body
├── composition.md                # frontmatter (sources + pins) + body (goal, source mapping, refinements)
├── sources/                      # embedded exemplars during active development; purgeable after build
│   ├── <source-slug-a>/          # sparse-checkout of upstream skill folder at pinned commit
│   │   ├── SKILL.md
│   │   └── ... (whatever upstream's skill folder contains)
│   └── <source-slug-b>/
├── _<verb>.md                    # workflow files authored per PFN — generated as scaffolds during build
└── scripts/                      # composition's own Python package skeleton
    └── __init__.py
```

`sources/` is present during active development with sparse-checkouts of each exemplar. composition.md body articulates Goal, Source mapping, and accumulated Design refinements. After build, `sources/` may be optionally purged via `compose purge-sources` (commits remain pinned in composition.md; refine auto-rehydrates by re-running `compose add-source` against pinned commits).

Cache directory and source registry are gone — no `~/.claude/plugins/data/progressive-skill-composer-a-horde-o-bees/cache/` or `sources.json`. The plugin data dir holds nothing user-facing; transient state is per-skill and self-contained.

### composition.md schema

```markdown
---
spec_version: 1
name: <skill-name>
description: <one-line, populated during compose new dialogue>
scope: user                 # OR project
sources:
  - url: https://github.com/anthropics/skills.git
    skill: slack-formatting
    ref: main                                       # branch / tag / refs/heads/<x>
    commit: abc123def...                            # pinned at last build
goal_summary: <one-line, populated during compose new dialogue>
last_build: 2026-05-10T14:00:00Z                    # ISO-8601 UTC; null before first build
build_status: built                                 # draft | built
---

# Goal

<articulated through compose new dialogue; refined through compose refine>

## Source mapping

### <source-slug>:<skill>

<which aspects of this exemplar inform the output: keep verbatim, adapt, reject>

## Design refinements

<dated entries appended during compose refine sessions; previous entries preserved unless superseded>
```

No `type` discriminator — every composition.md describes a composition. For users wanting direct install of an unmodified upstream skill, Vercel's `npx skills add <repo> --skill <name>` is the recommended path; progressive-skill-composer doesn't bundle that capability.

### Workflow shape — agent-driven dialogue

**`compose new --scope <user|project>`** opens a new-composition workflow:

1. Script outputs orchestration guidance with documented composition.md templates and section conventions
2. Agent prompts user: "What should this skill enable Claude to do? When should it fire? What name should it have?"
3. Once a name is chosen, agent uses Write tool to create `<scope>/.claude/skills/<name>/composition.md` with frontmatter scaffold (name, scope, empty sources list, draft status) and body section headers
4. Agent prompts user about exemplar sources; for each, invokes `compose add-source <name> <url>:<skill>[@<ref>] --scope` which sparse-checks the source into `<skill>/sources/<source-slug>/` and appends to composition.md frontmatter
5. Agent reads each source's SKILL.md and supporting files from the embedded `sources/<source-slug>/` paths to drive dialogue
6. Agent walks user through goal articulation and per-source mapping, editing composition.md body via Edit tool
7. When user is ready to materialize: agent invokes `compose build <name> --scope`

**`compose refine <name> --scope <user|project>`** re-enters an existing composition:

1. Script reads composition.md, runs `git ls-remote <url> <ref>` per source, compares each returned SHA to the pinned `commit` field
2. Script prints drift status report (per source: in-sync vs drifted from `<old>` to `<new>`) plus orchestration guidance
3. Agent surfaces drift to user as the opening of the refine session — "Since last build, `<source>:<skill>` changed from `<old>` to `<new>`"
4. Agent asks user whether to update each drifted source; for each yes, invokes `compose update-sources <name> --source <slug> --scope` which re-sparse-checks at current upstream HEAD and advances the `commit` field
5. Agent re-reads any updated `sources/<slug>/` content for the dialogue
6. Agent prompts targeted refinement questions and updates composition.md body via Edit tool
7. Agent appends a dated entry to `## Design refinements` summarizing what changed in this session

**`compose build <name> --scope <user|project>`**:

1. Script reads composition.md
2. Generates SKILL.md from `name + goal + source mapping`, drawing on embedded `sources/<source-slug>/` content as exemplar references. Body follows progressive-disclosure shape (frontmatter description + Triggers section + Verb topography pointing at `_<verb>.md` files)
3. Generates stub `_<verb>.md` workflow files using PFN notation when verbs are enumerated in the composition's source mapping section. The agent fills in details via Edit tool after build
4. Generates `scripts/__init__.py` package skeleton
5. Updates composition.md frontmatter: `last_build` (now), `build_status: built`
6. Refuses to overwrite an existing SKILL.md without `--force`

### Drift detection — non-mutating

`compose list --drift` and `compose refine`'s entry use `git ls-remote <url> <ref>` to return the current SHA at upstream's named ref without touching any local clone. The pinned `commit` in composition.md is compared to that SHA; mismatch surfaces as drift.

Branch-awareness comes for free from the ref. composition.md records `(url, ref, commit)`; ls-remote returns the SHA at `ref`'s HEAD. Other branches changing on the same repo never produce false drift — exactly the right semantic for "did MY tracked content change?"

To show *what* changed (not just that it changed), the script can sparse-check the upstream skill folder at HEAD into a temp dir, diff against the embedded `sources/<slug>/`, then discard. This is the deeper drift-inspection path; default `--drift` reports just the SHA mismatch.

### "Compositions of compositions" guidance

A user could in principle add a previously-composed skill as a source for a new composition. We document this is not recommended — the source's transitive recipe history would entangle with the new composition's goal articulation, producing confusing provenance. The script doesn't enforce this; the recommendation lives in SKILL.md and this decision log. If real-world usage warrants enforcement, we add a validation gate later.

### Consequences

- **Enables:** workflow-driven dialogue as the primary UX (agent orchestrates; script records); fully self-contained skill folders (recipe + exemplars + output in one location); cross-machine portability without separate sync (skill folder = unit of git-tracking); non-mutating drift detection via `git ls-remote`; multi-version handling without cache complexity (each composition pins its own snapshot); PFN + progressive-disclosure baked into compose build output (output skills automatically conform to our authoring discipline)
- **Constrains:** disk usage scales with #compositions × source size (mitigated by `compose purge-sources` after finalization; source skills are typically small); spec format is a contract enforced by build/refine logic (`spec_version` field provides migration affordance); user-facing verbs are minimal but each carries workflow weight (agents must understand the workflow to drive it correctly — encoded in `_compose_new.md` and `_compose_refine.md`); users wanting unmodified upstream installs use Vercel's `npx skills` rather than this plugin
- **Migration of in-flight code:** `sources.json`, shared cache, `track`/`untrack`/`sync` verbs, separate compositions/ working area, `installed.json` registries — all removed. install/uninstall verbs and `type: install|composed` discriminator dropped (redundant with Vercel's `npx skills` for the install case). composition.md schema simplified — every entry is a composition; no type field. The redesign lands as a single all-in-one commit reshaping the plugin around the compose-only model.
- **Open:** sparse-checkout fallback strategy if upstream removes the named skill folder (currently raises; user gets corrective error); whether `compose purge-sources` should be tied to a `compose finalize` lifecycle marker; spec format versioning for future schema evolution; whether build should generate `_<verb>.md` stubs from a verbs frontmatter field or only from agent-driven Source mapping content

See `plans/architecture-refactor.md` Phase B for the implementation order.
