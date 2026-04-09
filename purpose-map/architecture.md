# purpose-map Architecture

Design rationale for the purpose-map evaluation method: what it does, what problems it solves, the structural and methodological decisions that make it work, and the alternatives that don't.

## Purpose

purpose-map is a tool for answering one question: **is this component justified by a specific unmet concern?** It exists to make that question falsifiable rather than a matter of opinion. A component is justified when it points at a sub-concern that no existing component addresses through any mechanism. A component that can't make that pointer isn't justified — remove it, merge it, or rewrite it until it can.

The tool is the audit; the project is what gets audited. The model captures what should change; the changes happen in the project itself.

## The Problem

Project decisions accumulate over time: rules, conventions, principles, tools, hooks, skills, schemas. Each was added for a reason. Over time, the reasons get lost — the artifact remains but its justification fades. The natural questions become hard to answer:

- What does this rule do for the project that nothing else does?
- Are these two principles really distinct or do they overlap?
- If we removed this tool, would anything actually break?
- When we add a new component, does it contribute something the project lacks, or does it duplicate what's already there?

Without a structured way to answer these questions, projects accumulate components that serve no clear purpose, components that duplicate each other through subtly different mechanisms, and components whose justification has quietly evaporated. The agent (or human) maintaining the project can't tell the difference between a load-bearing component and a vestigial one.

The hard part is that "is this component needed?" can't be answered by inspecting the component alone. Reading the component tells you *what it does*, not *whether it should exist*. Justification requires a separate axis — concerns the project has — and a way to check whether the component meaningfully contributes to those concerns through a mechanism nothing else provides.

purpose-map provides that axis and that check.

## The Current Method

The method has two layers: structural decisions (the model's shape) and methodological techniques (how the model gets operated). Both are load-bearing. Removing either undermines the other.

### Structural decisions

**Two independent graphs over the same entities.** Components and needs are connected by two relationship types that answer different questions:

- `depends_on` (component → component) — structural DAG. "What must exist for this to work." If the dependency were removed, the dependent would be re-engineered or cease to exist.
- `addresses` (component → need) — capability claim. "How is this concern handled." A claim that this component contributes to addressing a specific sub-concern through a specific mechanism.

These graphs are independent on purpose. A component can depend on one thing and address something else entirely. Conflating them collapses two distinct claims into one — "what must exist for this" and "what contribution this makes" — and makes it impossible to reason about either cleanly.

**Needs are organized as a tree.** Roots are project-level concerns at the broadest level. Children are refined sub-concerns added under parents. The tree exists because a flat list of broad concerns produces saturation: every component plausibly addresses the broad concern, "covered" becomes trivially true, and the model loses its discriminating power. Refinement creates the level of specificity at which "is this unmet?" has a meaningful answer.

**Wiring rules force specificity.** The CLI enforces three rules on every addressing edge:

- A component cannot address a root need — must attach at depth ≥ 1
- A component cannot address both a need and any ancestor of that need
- A component cannot address both a need and any descendant of that need

The first rule prevents the saturation failure. The second and third prevent a component from claiming the same concern at multiple levels of granularity. Together they force every addressing edge to land at the level where the component's mechanism actually applies — and where the unmet test can fire meaningfully.

**Needs and rationales carry different content.** The need names the *failure mode being prevented* in third person ("Prevent the agent from acting on unverified system assumptions"). The rationale on the addressing edge names the *specific mechanism* this component contributes ("Encodes verify-before-act guidance with case-specific trigger bullets, so a verification gate fires at moments the agent would otherwise commit to action on unverified assumptions"). The need is what; the rationale is how. Keeping mechanisms out of needs is what makes multi-edge addressing meaningful — two components can address the same need through different mechanisms, with each rationale describing its own distinct contribution. If mechanism leaks into the need, the need collapses around the first mechanism that addresses it and other mechanisms get pushed away artificially.

**Validation marks identity, not coverage.** A validated entity is one whose identity is settled — purpose is clear, it contributes something the model didn't already capture, it isn't subsumed by another entity. Validation does *not* mean "fully addressed" or "frozen." A validated component can still gain new addressing edges as later components arrive. A validated need can still be addressed by multiple components through multiple mechanisms. Validation answers "is this real and right?" not "is this still going to change?"

**Entities use opaque ids, not names.** Components are `c1`, `c2`, ...; needs are `n1`, `n2`, ... Names are deliberately absent. The description is the load-bearing meaning. Names invite pattern-matching against a stale mental model — the eye lands on the label and skips the description, and reasoning happens against a familiar shorthand instead of the actual statement. Opaque ids force the reader to engage with the description on its merits.

### Methodological techniques

**Failure-mode framing as the entry point.** When deriving a need that a component will address, the question is not "what concern does this component touch?" but "what would have had to go wrong for this component to be needed?" This inversion forces the need to name a *concrete failure*, not a *generic concern*. Concerns are vague and saturate easily; failures are testable. The need wording "Reduce cognitive load" admits any component that vaguely touches cognitive load. The need wording "Prevent the agent from spending judgment on operations that are deterministic" admits only components whose mechanism specifically addresses that failure.

For principles and rules with case-specific bullets, the bullets often enumerate the specific failure modes the principle prevents. The unified failure mode across all bullets is the constitutive concern. The failure-mode lens uses the bullets as evidence to derive the need, then strips them out of the need wording (they belong in the rationale).

**Reactive refinement, not anticipatory decomposition.** Refining the need tree happens *only* when adding a component requires a sharper sub-need than the existing tree provides. Pre-decomposing the tree before components arrive produces speculative branches that don't match real component contributions when those components are eventually added. The discipline is reactive: a component arrives, the existing tree is too broad to attach with the right specificity, refinement creates exactly the sub-need that component needs. No more, no less.

**Cluster-based processing.** Related components are processed in proximity rather than at random. Earlier components' framings inform later ones — the failure-mode pattern stabilizes within a cluster, and parallel structures across closely-related components become visible (e.g., multiple components whose failures are all "agent inferring X with different X"). Without clusters, each component is a fresh start, and patterns that should be obvious get rediscovered each time.

**Per-component user confirmation.** Each component is proposed in full — description, paths, addressing edges, rationales, dependencies — and confirmed before any wiring happens. The cycle is slow on purpose. Batch processing introduces drift: rationales start to look formulaic, edge cases get missed, mechanism details slip into need wording. Per-component confirmation creates the friction that catches these failures before they accumulate. The user's role isn't to do the work; it's to catch what the agent would have missed.

## Alternatives Considered and What They Failed At

These approaches all have legitimate uses elsewhere. The notes below describe what fails when they're applied to needs analysis at scale.

**Classification — fitting components into pre-existing categories.** Start with a fixed set of broad concerns. Try to fit each component under one or more of them. Sounds clean and looks structured. The failure: broad categories saturate. Every component plausibly fits "reduce cognitive load" or "minimize friction." "Covered" becomes trivially true; the model can no longer discriminate good fit from bad. Worse, the categories don't tell you anything about whether a *new* component contributes something the *existing* components don't — because the test ("does this fit the category?") doesn't compare against what's already addressing the category.

**Mechanism-flavored need wording — needs phrased as "do X" or "ensure Y".** Write needs as actions: "Verify state before acting," "Bound claims to evidence," "Reduce parsing overhead by giving content predictable structure." This pre-binds the need to one specific mechanism — the one named in the wording. The failure: when a second component addresses the same underlying concern through a *different* mechanism, the model can't capture both cleanly. Either you create a near-duplicate need with slightly different mechanism wording (and now the model has two needs that should be one), or you collapse them together and lose the distinction (and now multi-edge addressing becomes meaningless because the two mechanisms get described as the same thing).

**Anticipatory need decomposition — pre-building the need tree before components arrive.** Decompose the broad concerns into sub-concerns up front, based on what *seems* like the right shape. The failure: imagined sub-needs don't match actual component contributions when the components are eventually added. The pre-decomposed branches stay empty; new components require fresh refinements anyway because the imagined decomposition was wrong. Worse, the imagined sub-needs influence component framing in distorted ways — the agent tries to fit the component to the imagined sub-need rather than identifying the component's actual contribution.

**Components defined by structure rather than contribution.** Let components exist as long as they have a path to a real artifact. The component is "real" because the file exists. The failure: the unjustified-component test never fires. A component with a path but no addressing edges is structurally fine, so the model doesn't surface it as a problem. The model captures what exists rather than what's *justified*, and the value of the audit collapses.

**Single-graph models — collapsing dependency and addressing into one relation.** Model components and concerns in a single edge type. "Component X relates to concern Y." The failure: structural claims and capability claims tangle. "X depends on Y to function" and "X contributes to handling Y" are different statements about different relationships, but the single-graph model can't distinguish them. Reasoning about dependency chains gets mixed up with reasoning about coverage; removing a dependency looks the same as removing an addresser.

## The Combination Effect

The structural decisions and methodological techniques reinforce each other. None of them does the work alone. Removing any one of them undermines several others:

- **Wiring rules need failure-mode framing.** Without failure-mode framing, the agent might attach a component to the broadest plausible need that satisfies the wiring rules — meeting the letter of the structural constraints without producing meaningful justification. The failure-mode lens forces the agent to identify the *specific* concern, which forces the attachment to the most specific applicable level, which is what the wiring rules were trying to enforce in the first place.

- **Failure-mode framing needs the need/rationale split.** Without the split, the failure mode and the mechanism collapse together in the need wording. The need becomes "verify state before acting" instead of "prevent acting on unverified state," and the door opens for mechanism-flavored framing that pre-binds the need to one approach.

- **Reactive refinement needs the wiring rules.** Without specificity-forcing rules, refinement never gets triggered. The agent attaches everything to the broadest plausible need; the tree stays shallow; refinement happens (if at all) as anticipatory decomposition rather than reactive sharpening. The rules create the friction that triggers refinement at the moment a component genuinely requires it.

- **Cluster-based processing needs per-component confirmation.** Without per-component confirmation, batch processing within a cluster accumulates drift — rationales start to look formulaic across the batch, parallel patterns get over-applied, framings that worked for one component get misapplied to the next. Per-component confirmation creates the pause that catches drift before it propagates.

- **Opaque ids reinforce the need/rationale split and the failure-mode framing both.** Without opaque ids, names anchor reasoning. The reader sees "Tool Positioning" and reasons about what they think Tool Positioning means rather than the actual description. Failure-mode framing relies on engaging with the actual statement; the need/rationale split relies on the description being the load-bearing meaning. Names undermine both.

The combination is what makes the unmet test fire reliably. Each technique alone is insufficient or undermined by the others' absence; together they make "is this component justified?" a question with a real answer.

## Beyond the Current Scope

The methodology this tool encodes — failure-mode framing, need/rationale split, reactive refinement, override-vs-description check, router-vs-destination check — has potential applicability beyond component auditing. The same analytical framework could serve as a migration tool (validating whether content should move, stay, or be removed when restructuring), or as a middle-stage analysis component for any process that needs to evaluate "what does this actually contribute that's valuable?" The framework is zoomable across granularity levels (file → section → bullet) and the core questions don't depend on the specific component-graph implementation. The current tool is one application of the methodology; the methodology itself is the more reusable artifact.

This is a forward-looking note rather than a current direction. Captured here so the broader applicability isn't lost as the tool evolves.
