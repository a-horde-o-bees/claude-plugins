---
name: needs-map
description: Walk components through the unmet-concern audit — identify the failure modes each contribution prevents, wire addressing edges with mechanism rationales, and prune or sharpen components that cannot point at a specific unmet sub-need.
argument-hint: "[<component-id> | <layer>]"
allowed-tools:
  - AskUserQuestion
  - Read
  - Bash(ocd-run needs-map*)
  - Bash(ocd-run needs_map*)
  - Bash(ocd-run navigator*)
  - Bash(grep *)
  - mcp__plugin_ocd_navigator__*
---

# /needs-map

Walk components through the unmet-concern audit — identify the failure modes each contribution prevents, wire addressing edges with mechanism rationales, and prune or sharpen components that cannot point at a specific unmet sub-need. Read ARCHITECTURE.md for data model and design rationale before driving the workflow on an unfamiliar database.

## Process Model

A needs-map audit answers one question per component: *is this component justified by a specific unmet sub-need?* The workflow is evaluation, not catalog-fitting — each component is tested against the existing model state, and refinements, re-writes, or removals are proposed in response to what the component cannot point at.

Progress is driven by `.claude/ocd/needs-map/state.md` — the worklist holding current layer, current component, and open items. When a layer's items are all evaluated and validated, the layer is removed from state.md. A session picks up where the last one left off.

Wiring is never autonomous. Every `address` and `depend` edge is proposed to the user in the Proposal Format below and wired only after confirmation. The user's role is to catch what the agent would have missed.

## Rules

- Read the source artifact before reasoning about a component — use `where`, navigator, or grep. Reasoning from the description alone is how mis-wirings happen
- Surface description corrections to the user rather than editing autonomously — mid-evaluation rewording can invalidate prior addressing edges
- Propose a component's addressing edges in the same step as the component itself — orphans pollute the view and attract speculative wirings later
- Run a duplication scan (`how <need-id>`) before every addressing proposal; include the findings in the Proposal Format
- Multi-edge addressing is valid — a component can address several sub-needs. Don't collapse to one "primary" need when each edge stands on its own
- Don't reject an edge because another component addresses the same need. Two components can address the same sub-concern through different mechanisms; rejection rationales like "X is the better vehicle" should re-trigger the duplication check
- Never address a root need directly — the CLI enforces this; when a component's best fit is a root, refine the root into sub-needs first
- Validate components when identity is settled (purpose clear, distinct from others), not when addressing is complete. Coverage and validation are independent

## Workflow

1. {target} = $ARGUMENTS

2. Read: `${CLAUDE_PLUGIN_ROOT}/systems/needs_map/ARCHITECTURE.md` — data model and discipline background
3. Read: `.claude/ocd/needs-map/state.md` — worklist state, current layer, outstanding items

> Target resolution — the argument selects what to evaluate. Without one, resume from state.md.

4. If {target} is empty:
    1. {target} = next pending component or layer named in state.md
    2. If state.md names no pending items: Exit to user: audit appears complete; review `ocd-run needs-map addresses --orphans` and `ocd-run needs-map addresses --gaps` before closing
5. Else if {target} matches a component id (`c` followed by digits):
    1. {component} = {target}
6. Else:
    1. Interpret {target} as a layer name or scope hint — present the components that layer contains, confirm with user before proceeding

> Evaluation loop — per component, through the full cycle. Stop at user confirmation gates.

7. For each {component} in the evaluation scope:

    ### Read the source

    1. bash: `ocd-run needs-map where {component}` — surface recorded paths
    2. If paths are recorded: Read each one
    3. Else: ask the user for a path or use navigator to locate the artifact
    4. If the component's description seems thin or ambiguous after reading the source: surface a suggested correction to the user — old text, proposed change, rationale. Wait for confirmation before editing

    ### Identify concerns

    5. For each distinct concern the component's mechanism contributes to:
        1. Name the failure mode the component prevents, the friction it closes, or the capability it enables — specific enough that "is this unmet?" is answerable
        2. bash: `ocd-run needs-map needs` — scan the need tree for the deepest existing sub-need that captures the concern
        3. If no existing sub-need is specific enough:
            1. Draft a refinement: new sub-need description that names the concern in third person, mechanism-free, per the Writing Guidelines below
            2. Propose the refinement to the user; wait for confirmation
            3. On confirmation: bash: `ocd-run needs-map refine <parent> "<description>"`

    ### Duplication scan

    6. For each candidate sub-need:
        1. bash: `ocd-run needs-map how <need-id>` — surface existing addressers and their rationales
        2. Note where the candidate mechanism overlaps an existing one; treat overlap as a precision lens — is either need's description as precise as it could be given the distinct mechanisms?

    ### Propose edges

    7. Present one proposal per component using the Proposal Format. Include:
        - Component shown once at the top in `[id] description` form
        - Recommended edges — each with `[id] description` and a standalone rationale (no contrast, no cross-edge locators)
        - Considered and rejected edges — each with `[id] description` and a rejection reason
        - Duplication scan section — note any overlap surfaced by `how`
    8. Wait for per-edge user confirmation

    ### Wire and verify

    9. For each confirmed edge:
        1. bash: `ocd-run needs-map address {component} <need-id> "<rationale>"`
    10. For each dependency edge needed on this component:
        1. Propose separately via the Proposal Format (same structure)
        2. On confirmation: bash: `ocd-run needs-map depend {component} <dep>`
    11. Verify the claims against the implementation:
        - Functional components (tools, MCP servers, scripts) — exercise the mechanism; confirm the claim matches reality
        - Descriptive components (rules, conventions, principles) — verify file-level conformance *and* composition patterns across the project
    12. If verification fails: surface to the user — (a) implementation bug to fix, (b) convention/description gap to fill, (c) wrong claim to revise — and wait for direction

    ### Validate and advance

    13. If identity is settled (purpose clear, not subsumed by another component): bash: `ocd-run needs-map validate {component}`
    14. bash: `ocd-run needs-map summary` — show coverage update
    15. If the unmet test failed for this component — every plausible attachment already addressed through the same mechanism — surface to the user. The right next step is to remove the component from the project

8. If a layer's items are all evaluated and validated: update `.claude/ocd/needs-map/state.md` to remove the layer from the worklist

### Proposal Format

Each proposal covers one component or one dependency wiring. Never bundle multiple components in one proposal — it forces context-switching and obscures which rationale belongs to which pair.

```
[c8] <component description>

Recommended:

- [n3] <need description>
  Rationale: <specific mechanism this component contributes — describes the
  edge in isolation, not in contrast with other addressers>

Considered and rejected:

- [n11] <need description>
  Reason: <why this edge doesn't hold — e.g. the effect is downstream of
  another component's mechanism, or the concern is already subsumed>

Duplication scan:
- n3 — addressed by c5 (rationale: ...) — overlap is complementary because ...
- n11 — no addressers
```

No name-style headings ("## c6 — Epistemic Humility") — headings reintroduce the named-object failure the opaque-id design prevents.

### Writing Guidelines

Apply when proposing descriptions, rationales, or refinements.

**Needs.** Business concerns, not technical requirements. Name what goes wrong when the concern is unmet — third person, mechanism-free. Test: "what would have had to go wrong for this to be needed?" and "if I remove everything addressing this need, does something specific go *wrong* (preventative) or just *not exist* (enabling)?" Strip trailing "so X" / "to X" clauses that bind to one consequence. Sub-needs follow the same rules as roots.

**Components.** Name the role and architectural shape — the kind of contribution the component makes. Survives refactoring: a rename, storage migration, or verb change should not invalidate the description. Don't enumerate function names, tool names, or parameters.

**Rationales.** Specific mechanism by which one component addresses one need. Because needs are mechanism-free, the rationale carries the full *how*. Stand-alone: readable without knowing about any other edge. No contrast ("different mechanism from cX"), no comparative locators ("producer-side / consumer-side") — prefer concrete descriptions.

### Evaluation Checks

Apply these before wiring any rule or convention-style component:

**Router vs destination.** When a rule routes the agent toward a tool, the rule's contribution is the *routing* — encoding the decision. The capability at the destination is a property of the destination component. If a rationale describes properties of another component rather than what the rule itself does, the edge is mis-attributed — drop or reframe.

**Override vs description.** Rules override default agent behavior. A rule that *describes* default behavior is vestigial — it has no failure to prevent. Before proposing any edges for a rule, ask "is this an override or a description?" If a description, halt the proposal, log a project-level action item to remove the entry, and move on.

### Report

- Components evaluated and validated
- Edges wired (addressing, dependency)
- Coverage delta — before/after from `summary`
- Items surfaced to the user (description corrections, verification failures, removal candidates)
