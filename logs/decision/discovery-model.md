---
log-role: reference
---

# Discovery Model

Decisions governing the discovery substrate — the trigger-routed registry that maps cognitive moments to actions (content loads or skill invocations). The substrate is half of a two-mechanism architecture; see `shim-model.md` for the parallel mechanism that handles the deployment of systems with code. The substrate replaces the broken `convention_gate` path-glob mechanism for content; together with the shim model it replaces always-on plugin-skill auto-discovery for systems.

## Cognitive vs artifact triggers

### Context

The original `convention_gate` hook used `includes`/`excludes` frontmatter on convention files to match files-being-edited to applicable conventions. Two failure modes drove the redesign:

- **Memory-filling problem** (`logs/problem/Memory-filling rules auto-load even when irrelevant to project domain.md`) — rules with `includes: "*"` auto-loaded into every project regardless of whether the work was plugin-development-shaped. A non-plugin project paid ~26.6K tokens of OCD rule overhead per session
- **Convention re-delivery** (`logs/idea/Convention-gate re-delivery measurement via total token exposure.md`) — even path-scoped conventions delivered per-Edit instead of caching once per session, scaling cost with operation count rather than amortizing

### Options Considered

**Path-glob matching with smarter caching** — fix the existing mechanism's per-fire delivery and rule scope, keep the model. Rejected: the rule auto-load floor is the dominant cost; smarter caching doesn't address always-on overhead for rules.

**Hide everything until cognitive trigger** — agents recognize moments and explicitly load relevant content; nothing auto-loads beyond a small router. Adopted.

### Decision

The rule/convention distinction is by *trigger source*:

- **Cognitive triggers** — agent recognizes the moment from its own intent ("I'm about to claim a number," "I'm refactoring," "I'm spawning agents"). Rule must be in context for the agent to even consider firing. → Always-on rule.
- **Artifact triggers** — agent recognizes the moment from a specific situation involving an artifact ("editing markdown content," "designing a tool surface"). Guidance is dormant until the artifact's situation matches. → Convention reachable via discovery substrate.

Concrete tests:

1. Can an agent recognize the moment without a specific file in context? If yes → rule.
2. Does the guidance only become relevant when a specific artifact-shaped situation applies? If yes → convention reachable via discovery.

When both apply, the failure mode picks: missing rule → wrong action; missing convention → malformed file. Match the failure to the file type.

### Consequences

- **Enables:** substantial reduction in always-on context cost; plugins truly invisible until opted in
- **Constrains:** every artifact-triggered piece must be explicitly trigger-routed; can't rely on global auto-load behavior
- **Audit signal:** if a rule never fires its cognitive trigger across many sessions, it's miscategorized — it's actually artifact-triggered and should move to a convention
- **Migration cost:** 5 of 26 OCD rules ARE artifact-triggered and move to conventions (`markdown`, `principle-not-symptom`, `trigger-specificity`, `tool-positioning`, `agent-first-interfaces`)

## Substrate shape — per-system routing files

### Context

Once the cognitive/artifact line was set, the question became how to mechanically deliver artifact-triggered content and surface skill invocations to agent intent matching, without reintroducing the always-on bloat the cognitive/artifact split was meant to remove.

### Options Considered

**Comprehensive router with purpose-in-row** — single always-on rule with table including trigger, purpose, and path columns. Rejected: scales poorly (50+ entries = ~3K always-on; Memory-filling problem reappears at scale).

**Per-trigger pool files** — agent reads pool files on first trigger fire; pools aggregate purposes for that trigger. Rejected: per-pool cost on each fire scales with engagement; bash-call-per-trigger pattern adds tool-call output to conversation each turn.

**Centralized trigger router with merged stubs** — each system carries a source stub; install merges trigger rows into a single deployed router file; stubs at index-based paths. Earlier-adopted; rejected on further refinement: merge logic, ID assignment, stub-file indirection, exact-prose match for cross-system shared triggers all paid ongoing complexity tax for marginal token savings.

**Per-system routing files co-located with system rules** — each installed system deploys its own `triggers.md` file at `<scope>/.claude/rules/<plugin>/<system>/triggers.md`, alongside any system-bundled rules. The system's handler decides the file's shape — most are static templates listing triggers → skill invocations; conventions is dynamic, generating a triggers section plus an indexed purposes section based on which conventions opted in. Adopted.

### Decision

The substrate's runtime artifacts at scope:

| Artifact | Always-on? | Purpose |
|---|---|---|
| `<scope>/.claude/rules/<plugin>/<system>/triggers.md` | Yes | Per-system routing — trigger prose mapped to targets (content stubs or skill invocations with args) |
| `<scope>/.claude/conventions/<plugin>/<name>.md` | No | Convention bodies; loaded when the routing file's purpose entry convinces the agent |
| `<scope>/.claude/dependencies/<name>.md` | No | Shared content loaded by sources via `requires:` frontmatter |
| `<scope>/.claude/dependencies/_manifest.md` | No | Install/uninstall bookkeeping — `content_hash + used_by` per dependency |

Each system implements an `install_triggers(scope, args)` method (or equivalent dispatch) that knows how to build and deploy its `triggers.md`. Setup install calls the system's handler; setup uninstall is `rm` of the file. No central merge logic.

For most systems, the handler deploys a static template — a triggers table mapping trigger prose to skill invocations. Example for the log system:

```markdown
# Log discovery

## Triggers

| Trigger | Targets |
|---|---|
| When friction in a workflow surfaces — gap between expected and actual | Skill: /ocd-log friction |
| When a non-obvious choice was made with alternatives considered | Skill: /ocd-log decision |
| When a defect in an artifact is observed | Skill: /ocd-log problem |
| When a future-work or improvement suggestion arises | Skill: /ocd-log idea |
```

For the conventions system, the handler is dynamic — at install time it reads the user's opted-in conventions, extracts each one's H1 + first paragraph (purpose statement), and assembles a `triggers.md` with both a triggers section and an indexed purposes section:

```markdown
# Conventions discovery

## Triggers

| Trigger | Targets |
|---|---|
| When editing markdown content | [1] |
| When designing a tool surface | [2] |

## Purposes

[1] markdown.md — Base content standards for all markdown files...
[2] agent-first-interfaces.md — Tool design for agent consumption...
```

The agent reads the always-on triggers section, matches its moment to a row, follows the index to the purposes section, and based on the inline purpose statement decides whether to load the full body at `<scope>/.claude/conventions/<plugin>/<name>.md`.

### Consequences

- **Enables:** install/uninstall mechanics simplify dramatically (no row merging, no ID assignment, no stub-file indirection); each system owns its routing format; uninstall is file deletion; per-system customization (static vs dynamic) handled by per-system handlers
- **Constrains:** always-on cost increases vs the merged-router optimum — each installed system's `triggers.md` loads (~0.5-2K each); for ~10 systems averaging ~1K, ~10K always-on. Pay-for-what-you-install: 3 systems = ~3K, 5 = ~5K. Still well under the ~26K original baseline
- **Cross-plugin trigger coordination:** if two systems trigger on the same conceptual moment, both rows appear in their respective files; agent sees both and decides. No merge, no canonical-prose registry needed
- **Manifest co-location:** dependency bookkeeping moves to `<scope>/.claude/dependencies/_manifest.md` — alongside the dep files it tracks; not auto-loaded (filename convention or directory placement keeps it out of memory)

## Trigger targets — content stubs and skill invocations

### Context

Earlier substrate designs targeted only content. Once the shim model was specified, a unified routing layer that surfaces skill invocations alongside content loads became the natural shape — the substrate became the agent's curated cognitive-moment-to-action registry, where actions can be either kind.

### Decision

Trigger rows in `triggers.md` files map trigger prose to targets. Two target types:

| Target type | Example | Resolves to | Use case |
|---|---|---|---|
| Content reference | `[1]` (index into purposes section) | Inlined purpose statement → `<scope>/.claude/conventions/<plugin>/<name>.md` body if loaded | Convention/rule content loads as additional context |
| Skill invocation | `Skill: /ocd-log friction` | Slash command (with args) the agent invokes; shim resolves cache CLAUDE.md via `Call: !`<plugin>-path <system>`` | Agent runs the system's skill |

Skill invocation targets carry verb-and-args because the agent's intent matching at the trigger level is more granular than the SKILL.md's single `description` field can capture. A system with verb-routed dispatch (e.g., `/ocd-log <type>`) registers separate trigger rows for each cognitive moment the system serves:

- "When friction in a workflow surfaces" → `Skill: /ocd-log friction`
- "When a non-obvious choice was made" → `Skill: /ocd-log decision`

Claude Code's native skill awareness (description matching) still operates as a coarse always-on safety net. The substrate provides the curated, sharp routing the system author designed for; both can fire on the same moment without conflict.

### Consequences

- **Enables:** verb-level granularity in routing (one skill, multiple distinct cognitive moments mapped to specific verbs); substrate doubles as cognitive-moment-to-precise-action map; system author owns the trigger prose for each entry point
- **Constrains:** system authors must enumerate the meaningful moment + verb-args combinations as separate trigger rows; skill invocation rendering via `$ARGUMENTS` substitution must work end-to-end (Claude Code's documented behavior; verified for non-expansion args)

## Trigger prose as recognition cue

### Context

Initial designs separated a short-token trigger key (e.g., `markdown`, `governance-authoring`) from a prose situation column. The prose was for cognitive recognition; the token was for merge mechanics.

### Options Considered

**Two columns: short-token key + prose situation** — token enables programmatic referencing; prose is the recognition cue. Rejected: under per-system routing files, no merge mechanism justifies the token; prose alone names the situation.

**Single column: rich prose IS the trigger** — each row's trigger cell carries an articulated natural-language description. Adopted.

### Decision

`triggers.md` files have two columns: Trigger (rich prose) and Targets. Trigger prose serves a single role — cognitive recognition cue the agent matches its current moment against. System authors write trigger prose articulated enough for sharp recognition.

### Consequences

- **Enables:** sharper recognition (prose carries full intent and rationale, supporting future refinement); fewer columns; no token-vs-prose drift
- **Discipline:** trigger prose follows `trigger-specificity` — each trigger names a single mechanism; bundled mechanisms become separate triggers

## Dependencies inferred from source frontmatter

### Context

Some sources reference shared content (e.g., PFN). The substrate needs to track which sources need which dependencies, deploy them when first needed, and clean up when no longer needed.

### Options Considered

**System author lists dependencies in the routing file** — Dependencies section in `triggers.md` alongside Triggers. Rejected: redundant with source-level frontmatter; couples routing to dependency tracking.

**Source files declare `requires:` in their own frontmatter; install infers dependencies by scanning sources** — each source is the truth about its own dependencies; manifest tracks reference counts. Adopted.

### Decision

Source files declare `requires: [<dep-name>, ...]` in YAML frontmatter. At install:

1. Scan the system's source files for `requires:` declarations
2. For each declared dependency, deploy `plugins/<plugin>/dependencies/<name>.md` to `<scope>/.claude/dependencies/<name>.md` if not already present (see *Dependency versioning model* for conflict handling)
3. Append the system's name to the dependency's `used_by` list in `<scope>/.claude/dependencies/_manifest.md`

At uninstall, remove the system's name from each `used_by`; if `used_by` becomes empty, delete the dependency content too.

### Consequences

- **Enables:** dependencies declared at source level (single source of truth); reference-counted cleanup; PFN moves out of always-on rules into on-demand `dependencies/`
- **Constrains:** sources must keep `requires:` accurate; install machinery must scan all sources, not just the routing file
- **PFN's dual role:** parsing-side relevance handled by `requires:`; authoring-side relevance (agent producing PFN-structured output) may need a separate cognitive trigger or stay as always-on rule. Open question, deferred until concrete

## Dependency versioning model — apt-style

### Context

Multiple plugins (or multiple systems within a plugin) may ship a dependency with the same `<name>`. The substrate needs a rule for what happens when a second installer encounters a name already deployed at scope, especially when the source content differs from what's already there. The user-facing goal is "load the dependency once for all dependents, but only after a trigger fires" — divergent copies per dependent defeat the token-cost objective.

### Options Considered

**apt/brew model — single instance, refcounted, hash-conflict-fails** — one physical file at `<scope>/.claude/dependencies/<name>.md`; manifest stores `name → {content_hash, used_by}`; install with matching hash appends to `used_by`, mismatch errors. Adopted.

**pnpm model — content-addressable, dedupe by hash, multiple versions allowed** — files live at `<scope>/.claude/dependencies/<name>-<sha>.md`; identical content shares a file, divergent content coexists. Rejected: defeats the load-once goal when versions diverge; adds resolution complexity for a problem not yet observed.

**Cargo/Maven model — explicit version field with constraint resolution** — sources declare `requires: <name>@>=X.Y`; install resolves all constraints, picks highest compatible. Rejected as premature: requires version metadata on every dep plus a resolver, with no concrete divergence pressure today.

**Canonical-source model (Go-style)** — owner plugin ships the canonical copy; other plugins requiring it declare a cross-plugin dep instead of bundling. Rejected for now: requires a cross-plugin ordering protocol that doesn't exist; revisit if the ecosystem grows beyond ocd.

### Decision

`<scope>/.claude/dependencies/_manifest.md` records each dependency with two fields: `content_hash` (sha256 of the deployed file's bytes) and `used_by` (list of installed system names).

At install, for each dependency declared by the system being installed:

1. Compute the source file's sha256
2. Look up `<name>` in the deployed manifest:
    - **Not present** — copy source to `<scope>/.claude/dependencies/<name>.md`; create manifest entry `{content_hash: <sha>, used_by: [<system>]}`
    - **Present, hash matches** — append `<system>` to `used_by`; do not rewrite the deployed file
    - **Present, hash mismatches** — error with corrective guidance: name the dependency, the deployed hash, the systems currently using it, the conflicting source's hash and origin, and the resolution path (reconcile upstream so all shippers carry the same content, or install only one of the conflicting plugins)

At uninstall, remove the system's name from each `used_by`; when `used_by` becomes empty, delete the deployed file and the manifest entry.

### Consequences

- **Enables:** one load per scope per session regardless of dependent count; divergent shipments surface at install rather than silently masking; refcounting matches the apt rdepends model
- **Constrains:** plugins coordinating on a shared dependency name must keep content byte-identical; backward-incompatible evolution of a dep requires either renaming or coordinated lockstep updates across all shippers
- **Migration path:** if backward-incompatible evolution becomes a real pressure, escalate to pnpm-style hash-suffixed coexistence or Cargo-style version constraints; for now the simpler model is sufficient
- **Hash field discipline:** the manifest hash is computed from the deployed file's bytes after any normalization the install applies (e.g., line endings); install and uninstall must use the same bytes to compute and verify

## Substrate role within the two-mechanism architecture

### Context

The substrate was initially motivated by conventions migration. Once the shim model was specified, the substrate's role expanded — it became the runtime intent-routing layer surfacing both content loads and skill invocations to agent recognition.

### Decision

Two-mechanism architecture:

- **Discovery substrate** (this document) — runtime intent-routing layer. Per-system `triggers.md` files at `<scope>/.claude/rules/<plugin>/<system>/`. Targets are content references (loaded via the conventions/dependencies layout) or skill invocations (with verb-and-args).
- **Shim model** (`shim-model.md`) — system-deployment infrastructure. Per-system `SKILL.md` shims at `<scope>/.claude/skills/<plugin>-<system>/`. The shim's body resolves to a cached CLAUDE.md via `Call: !`<plugin>-path <system>`` — invocation-time cache resolution. Skills the substrate routes to dispatch through these shims.

Substrate scope:

- **Conventions** (first concrete case): artifact-triggered file format guidance; replaces broken `includes`/`excludes`
- **Rules that fail the cognitive-trigger test**: currently auto-loaded rules that are actually artifact-triggered get migrated to conventions reachable via the substrate
- **Skill invocations**: each system's `triggers.md` registers cognitive moments mapped to its skill verbs
- **Dependencies** (e.g., PFN): shared content loaded by sources via `requires:` frontmatter

Out of substrate scope:

- Universal rules (always-on memory, full content at scope)
- System-bundled rules (always-on memory once system is installed)
- Skill DEPLOYMENT (handled by shim model; substrate just routes to the deployed skills)

### Consequences

- **Enables:** unified intent → action map for the agent; skill invocations get verb-level routing precision the SKILL.md `description` field can't carry alone; clean separation between substrate routing and shim deployment
- **Constrains:** each system migration is its own focused pass; the substrate is purpose-scoped to runtime routing, not generalized further
- **Long-term:** the substrate may become a Claude Code-native primitive; for now, OCD provides the reference implementation alongside the shim model
