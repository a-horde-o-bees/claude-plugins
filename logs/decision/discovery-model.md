---
log-role: reference
---

# Discovery Model

Decisions governing the discovery system — the trigger-routed context-loading model that subsumes how rules, conventions, skills, MCPs, and other plugin contributions enter agent context. Substrate replaces the broken `convention_gate` path-glob mechanism.

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

- **Enables:** ~93% reduction in always-on context cost (from ~30K rule auto-load to ~1.5K runtime trigger router); plugins truly invisible until opted in
- **Constrains:** every artifact-triggered piece must be explicitly trigger-routed; can't rely on global auto-load behavior
- **Audit signal:** if a rule never fires its cognitive trigger across many sessions, it's miscategorized — it's actually artifact-triggered and should move to a convention
- **Migration cost:** 5 of 26 OCD rules ARE artifact-triggered and move to conventions (`markdown`, `principle-not-symptom`, `trigger-specificity`, `tool-positioning`, `agent-first-interfaces`)

## Substrate shape — four artifacts at three layers

### Context

Once the cognitive/artifact line was set, the question became how to mechanically deliver the artifact-triggered content without reintroducing the bloat the cognitive/artifact split was meant to remove.

### Options Considered

**Comprehensive router with purpose-in-row** — single always-on rule with table including trigger, purpose, and path columns. Rejected: scales poorly (50+ conventions = ~3K always-on; Memory-filling problem reappears at scale).

**Per-trigger pool files** — agent reads pool files on first trigger fire; pools aggregate purposes for that trigger. Rejected as primary mechanism: the per-pool cost on each fire scales with engagement; bash-call-per-trigger pattern adds tool-call output to conversation each turn.

**Per-system trigger-router stubs that mechanically merge** — each system carries its own stub; install merges into a single deployed router; uninstall strips out. Stubs are auto-generated path-and-purpose pointers. Adopted.

### Decision

Four artifacts at three layers:

| Layer | Artifact | Always-on? | Purpose |
|-------|----------|------------|---------|
| Layer 1 (runtime) | `<scope>/rules/discovery-triggers.md` | Yes (~1.5K) | Trigger prose → stub references |
| Layer 1 (bookkeeping) | `<scope>/discovery/manifest.md` | No | Index (system→ID), Dependencies (file→IDs); install/uninstall mechanics only |
| Layer 2 | `<scope>/discovery/<id>-<n>.md` | No | Stub: H1 source path + purpose body; loaded when row's trigger fires |
| Layer 3 | `<scope>/conventions/<plugin>/<name>.md` | No | Source content; loaded when stub purpose says it's worth it |
| Sidecar | `<scope>/dependencies/<name>.md` | No | Shared content (e.g., PFN); loaded by sources via `requires:` frontmatter |

### Consequences

- **Enables:** clear separation between always-on cost (just the trigger router) and on-demand content (everything else); manifest stays out of runtime context; stubs are tiny (~100 tokens) so first-fire cost is negligible
- **Constrains:** each system must author a `discovery-triggers.md` source stub; install machinery must be implemented
- **Multi-plugin coexistence:** systems own their stubs by `<id>` prefix; no cross-plugin coordination for ownership
- **Cross-plugin trigger sharing:** systems contributing to the same conceptual trigger must use exact-match prose to merge; otherwise rows duplicate. Acceptable trade-off; canonical-prose registry can come later if needed

## Trigger-as-prose recognition cue

### Context

Initial designs separated a short-token trigger key (e.g., `markdown`, `governance-authoring`) from a prose situation column. The prose was for cognitive recognition; the token was for merge mechanics.

### Options Considered

**Two columns: short-token key + prose situation** — token is the merge key; prose is the recognition cue. Rejected: the token is redundant; prose already names the situation; merge can use exact-prose match.

**Single column: rich prose IS the trigger** — each row's trigger cell carries an articulated natural-language description; merge uses exact-prose match. Adopted.

### Decision

The deployed trigger router has two columns: Trigger (rich prose) and Stubs. Trigger prose serves dual roles:

- Cognitive recognition cue — the agent matches its current moment against the prose
- Merge join key — exact-prose match across systems contributing to the same row

System authors write trigger prose that's articulated enough for sharp recognition while keeping the same wording for shared concepts.

### Consequences

- **Enables:** sharper recognition (prose carries full intent and rationale, supporting future refinement); fewer columns; no token-vs-prose drift to maintain
- **Constrains:** plugins coordinating on a shared trigger must use canonical prose; may need a registry over time
- **Discipline:** trigger prose follows `trigger-specificity` — each trigger names a single mechanism; bundled mechanisms become separate triggers

## Dependencies inferred from source frontmatter

### Context

Some sources reference shared content (e.g., PFN). The substrate needs to track which sources need which dependencies, deploy them when first needed, and clean up when no longer needed.

### Options Considered

**System author lists dependencies in `discovery-triggers.md` stub** — Dependencies section in the system stub alongside Triggers. Rejected: redundant with source-level frontmatter; couples routing to dependency tracking.

**Source files declare `requires:` in their own frontmatter; install infers dependencies by scanning sources** — each source is the truth about its own dependencies; manifest tracks reference counts. Adopted.

### Decision

Source files declare `requires: [<dep-name>, ...]` in YAML frontmatter. At install:

1. Scan the system's source files for `requires:` declarations
2. For each declared dependency, deploy `plugins/<plugin>/dependencies/<name>.md` to `<scope>/dependencies/<name>.md` if not already present
3. Append the system's `<id>` to the manifest's Dependencies "Used by" list

At uninstall, remove the system's `<id>` from each "Used by"; if "Used by" becomes empty, delete the dependency content too.

### Consequences

- **Enables:** dependencies declared at source level (single source of truth); reference-counted cleanup; PFN moves out of always-on rules into on-demand `dependencies/`
- **Constrains:** sources must keep `requires:` accurate; install machinery must scan all sources, not just the trigger stub
- **PFN's dual role:** parsing-side relevance handled by `requires:`; authoring-side relevance (agent producing PFN-structured output) may need a separate cognitive trigger or stay as always-on rule. Open question, deferred until concrete

## Index-based stub naming

### Context

Stub files need names. Two options: semantic (`discovery/ocd/conventions/markdown.md`) or index-based (`discovery/A-1.md`).

### Options Considered

**Semantic naming** — readable file paths, no Index needed. Rejected: longer router rows when stub references appear in trigger router; cross-plugin path-conflict avoidance needs handling.

**Index-based naming** — short opaque names; semantic content lives inside the stub (H1 source path + purpose body); manifest carries the `<id> → <plugin>/<system>` mapping. Adopted.

### Decision

Stubs are named `<id>-<n>.md` where `<id>` is a single letter assigned per installed system (alphabetical by `<plugin>/<system>` ordering) and `<n>` is the file's index within that system. Mapping lives in `<scope>/discovery/manifest.md` ## Index, used by install/uninstall mechanics, not loaded at runtime.

### Consequences

- **Enables:** ultra-compact router (3-character stub references vs ~30 chars for full paths); deterministic ID assignment; uniform stub directory regardless of plugin or system
- **Constrains:** stub names aren't human-readable on disk; debugging requires consulting manifest
- **Cross-system insertion:** if a new system installs alphabetically before existing ones, ID assignments may shift; sync-router handles renumbering at install/uninstall time

## Manifest separated from runtime

### Context

Initial designs included Index and Dependencies sections in the trigger router itself. The agent-facing always-on file would carry all bookkeeping.

### Options Considered

**Single file with all sections (Triggers, Dependencies, Index)** — agent reads the whole thing always-on. Rejected: bookkeeping isn't needed at runtime and bloats the always-on cost.

**Manifest split out** — runtime router has Triggers only; bookkeeping lives in `<scope>/discovery/manifest.md` outside `rules/` so it's not auto-loaded. Adopted.

### Decision

`<scope>/rules/discovery-triggers.md` carries only the `## Triggers` section (the agent-facing always-on cost). `<scope>/discovery/manifest.md` holds `## Index` and `## Dependencies` for install/uninstall mechanics. The manifest is read by the install/uninstall CLI; it is never auto-loaded by the agent.

### Consequences

- **Enables:** minimal always-on footprint; bookkeeping doesn't pay for itself in every session
- **Constrains:** install/uninstall must read both files; manifest must stay in sync with runtime router (sync-router enforces this)

## Generalization beyond conventions

### Context

The substrate was initially motivated by conventions migration. The same pattern (cognitive recognition → stub gate → source content) applies to any context contribution that costs more in always-on form than in trigger-routed form.

### Decision

The discovery model is the universal context-loading kernel. Applies to:

- **Conventions** (first concrete case): artifact-triggered file format guidance; replaces broken `includes`/`excludes`
- **Skills** (future): always-on metadata becomes trigger-routed; relevant skill bodies discovered on cognitive recognition
- **MCPs** (future): tool descriptions move from always-on into discoverable docs; the MCP server stays a service called after the doc loads
- **Rules that fail the cognitive-trigger test** (future): currently auto-loaded rules that are actually artifact-triggered get migrated
- **Navigator's file maps, PDF generation flow, log routing, etc.** (future): each gets re-evaluated; what's currently always-on becomes trigger-routed when its trigger doesn't fire universally

### Consequences

- **Enables:** "huge hidden toolbox" — extensive plugin functionality at near-zero always-on cost; pay-for-engagement scaling
- **Constrains:** each migration is its own focused pass with its own design considerations
- **Long-term:** the substrate may become a Claude Code-native primitive; for now, OCD provides the reference implementation
