# needs-map Architecture

Design rationale for the needs-map evaluation method: what it does, what problems it solves, the structural and methodological decisions that make it work, and the alternatives that don't.

## Purpose

needs-map is a tool for answering one question: **is this component justified by a specific unmet concern?** It exists to make that question falsifiable rather than a matter of opinion. A component is justified when it points at a sub-concern that no existing component addresses through any mechanism. A component that can't make that pointer isn't justified — remove it, merge it, or rewrite it until it can.

The tool is the audit; the project is what gets audited. The model captures what should change; the changes happen in the project itself.

## The Problem

Project decisions accumulate over time: rules, conventions, principles, tools, hooks, skills, schemas. Each was added for a reason. Over time, the reasons get lost — the artifact remains but its justification fades. The natural questions become hard to answer:

- What does this rule do for the project that nothing else does?
- Are these two principles really distinct or do they overlap?
- If we removed this tool, would anything actually break?
- When we add a new component, does it contribute something the project lacks, or does it duplicate what's already there?

Without a structured way to answer these questions, projects accumulate components that serve no clear purpose, components that duplicate each other through subtly different mechanisms, and components whose justification has quietly evaporated. The agent or human maintaining the project can't tell the difference between a load-bearing component and a vestigial one.

The hard part is that "is this component needed?" can't be answered by inspecting the component alone. Reading the component tells you *what it does*, not *whether it should exist*. Justification requires a separate axis — concerns the project has — and a way to check whether the component meaningfully contributes to those concerns through a mechanism nothing else provides.

needs-map provides that axis and that check.

## Data Model

Two entity types connected by three edge types, plus per-component source-location references.

### Schema

```sql
components       (id, description, validated)
needs            (id, parent_id, description, validated)  -- parent_id NULL for roots
depends_on       (component_id → dependency_id)
addresses        (component_id → need_id, rationale)      -- many-to-many; need must not be a root
component_paths  (component_id → path)                    -- source-location pointers
```

### Entities

**Needs** are the "why" — problems to solve, organized as a tree via `parent_id`. Root needs are project-level business concerns; refined sub-needs appear beneath as discovery requires. Components cannot address roots directly.

**Components** are the "how" — structural units that address needs. Anything that exists and can contribute a mechanism: rules, conventions, principles, tools, MCP servers, scripts.

Both entity types use auto-generated short ids (`c1`, `n1`) assigned at insertion. Descriptions carry the load-bearing meaning; names are deliberately absent.

### Relationships

**depends_on** (component → component) is the structural DAG. "What must exist for this to work." If the dependency were removed, the dependent would be re-engineered or cease to exist.

**addresses** (component → refined need) is a capability claim with a rationale describing the specific mechanism. Because needs are mechanism-free, the rationale carries the full description of *how* — "encoded as a rule," "blocked at runtime by a hook," "captured into a friction queue." Rationales describe their edge in isolation; cross-edge comparison is a reading-time operation.

**component_paths** are non-authoritative source-location pointers. A component can have zero, one, or many paths, and each may be a file, a directory, `file#anchor`, or a glob pattern. Paths are true at creation; if they break after a refactor, retrace by purpose using navigator or by content using grep, then update.

### Wiring Rules

Enforced at insertion:

- A component cannot address a root need — must attach at depth ≥ 1
- A component cannot address both a need and any ancestor of that need
- A component cannot address both a need and any descendant of that need

The first rule prevents the saturation failure. The second and third prevent claiming the same concern at multiple levels of granularity. Together they force every addressing edge to land where the component's mechanism actually applies — and where the unmet test can fire meaningfully.

### Validation

Components and needs can be validated (`validate <id>`) or unvalidated (the `?` prefix in displays). Validation captures identity, not coverage — validated entities can still gain new addressing edges as later components arrive. The question is "is this real and right?", not "is this still going to change?"

## Structural Decisions

The following decisions shape what the model can and cannot express. Each is load-bearing; removing any one undermines the others.

**Two independent graphs over the same entities.** `depends_on` and `addresses` answer different questions and must not conflate. A component can depend on one thing and address something else entirely. Conflating them collapses two distinct claims ("what must exist for this" and "what contribution this makes") and makes it impossible to reason about either cleanly.

**Needs organized as a tree.** A flat list of broad concerns produces saturation: every component plausibly addresses the broad concern, "covered" becomes trivially true, and the model loses its discriminating power. Refinement creates the level of specificity at which "is this unmet?" has a meaningful answer. The tree exists so refinement can happen only where discovery requires it.

**Needs and rationales carry different content.** The need names the failure mode being prevented in third person ("Prevent the agent from acting on unverified system assumptions"). The rationale on the addressing edge names the specific mechanism this component contributes ("Encodes verify-before-act guidance with case-specific trigger bullets, so a verification gate fires at moments the agent would otherwise commit to action on unverified assumptions"). The need is what; the rationale is how. Keeping mechanisms out of needs is what makes multi-edge addressing meaningful — two components can address the same need through different mechanisms, with each rationale describing its own distinct contribution. If mechanism leaks into the need, the need collapses around the first mechanism that addresses it and other mechanisms get pushed away artificially.

**Opaque ids, no names.** Components are `c1`, `c2`, ...; needs are `n1`, `n2`, ... Names invite pattern-matching against a stale mental model — the eye lands on the label and skips the description, and reasoning happens against a familiar shorthand instead of the actual statement. Opaque ids force the reader to engage with the description on its merits.

**Components defined by contribution, not structure.** A path-only component — file exists, no addressing edges — is structurally fine but fails the unmet test. The model surfaces these as orphans precisely so they can be removed. Letting components exist on file existence alone collapses justification into completeness-of-mapping.

## Methodological Techniques

The techniques below make the structural decisions work as intended. Each responds to a failure mode observed when the structure is used without it.

**Failure-mode framing.** When deriving a need that a component will address, the question is not "what concern does this component touch?" but "what would have had to go wrong for this component to be needed?" This inversion forces the need to name a *concrete failure*, not a *generic concern*. Concerns are vague and saturate easily; failures are testable. For principles and rules with case-specific bullets, bullets often enumerate specific instances of the underlying failure — the unified failure mode across all bullets is the constitutive concern.

**Reactive refinement.** The need tree grows only when adding a component requires a sharper sub-need than what exists. Pre-decomposing produces speculative branches that don't match real component contributions when those components arrive. The discipline is reactive: a component arrives, the existing tree is too broad to attach with the right specificity, refinement creates exactly the sub-need that component needs. No more, no less.

**Cluster-based processing.** Related components are processed in proximity. Earlier components' framings inform later ones — the failure-mode pattern stabilizes within a cluster, and parallel structures across closely-related components become visible. Without clusters, each component is a fresh start, and patterns that should be obvious get rediscovered each time.

**Per-component user confirmation.** Each component is proposed in full — description, paths, addressing edges, rationales, dependencies — and confirmed before any wiring happens. The cycle is slow on purpose. Batch processing introduces drift: rationales start to look formulaic, edge cases get missed, mechanism details slip into need wording. Per-component confirmation creates the friction that catches these failures before they accumulate. The user's role isn't to do the work; it's to catch what the agent would have missed.

## Alternatives Considered

**Classification — fitting components into pre-existing categories.** Broad categories saturate: every component plausibly fits "reduce cognitive load" or "minimize friction." "Covered" becomes trivially true; the model can no longer discriminate good fit from bad. The test ("does this fit the category?") doesn't compare against what's already addressing the category.

**Mechanism-flavored need wording — needs phrased as "do X" or "ensure Y".** Pre-binds the need to one specific mechanism. When a second component addresses the same underlying concern through a different mechanism, the model can't capture both cleanly: either create near-duplicate needs with slightly different mechanism wording (two needs that should be one), or collapse them together (multi-edge addressing becomes meaningless).

**Anticipatory need decomposition.** Imagined sub-needs don't match actual component contributions. Pre-decomposed branches stay empty; new components require fresh refinements anyway. Worse, imagined sub-needs influence component framing in distorted ways — the agent tries to fit the component to the imagined sub-need rather than identifying its actual contribution.

**Components defined by path existence.** The unjustified-component test never fires. A component with a path but no addressing edges is structurally fine, so the model doesn't surface it as a problem. The model captures what exists rather than what's *justified*.

**Single-graph models.** Collapsing dependency and addressing into one edge type tangles structural and capability claims. "X depends on Y to function" and "X contributes to handling Y" are different statements; the single-graph model can't distinguish them.

## The Combination Effect

The structural decisions and methodological techniques reinforce each other. Removing any one undermines several others:

- **Wiring rules need failure-mode framing.** Without failure-mode framing, the agent attaches components to the broadest plausible need that satisfies the wiring rules — meeting the letter of the structural constraints without producing meaningful justification. The failure-mode lens forces the agent to identify the *specific* concern, which forces attachment at the most specific applicable level.
- **Failure-mode framing needs the need/rationale split.** Without the split, the failure mode and the mechanism collapse together in the need wording. The need becomes "verify state before acting" instead of "prevent acting on unverified state," opening the door for mechanism-flavored framing.
- **Reactive refinement needs the wiring rules.** Without specificity-forcing rules, refinement never gets triggered. The agent attaches everything to the broadest plausible need; the tree stays shallow; refinement (if it happens at all) becomes anticipatory decomposition rather than reactive sharpening.
- **Cluster-based processing needs per-component confirmation.** Without per-component confirmation, batch processing within a cluster accumulates drift — rationales look formulaic across the batch, parallel patterns get over-applied, framings that worked for one component get misapplied to the next.
- **Opaque ids reinforce the need/rationale split and failure-mode framing both.** Names anchor reasoning against a familiar shorthand instead of the actual statement. Failure-mode framing relies on engaging with the actual statement; the need/rationale split relies on the description being the load-bearing meaning.

The combination is what makes the unmet test fire reliably. Each technique alone is insufficient or undermined by the others' absence; together they make "is this component justified?" a question with a real answer.
