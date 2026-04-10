# Purpose Map

purpose-map answers one question: **is this component justified by a specific unmet need?** Use it before adding anything to the project, and use it to audit what's already there. A component is justified when it points at a sub-concern that no existing component addresses through any mechanism. A component that can't make that pointer isn't justified — remove it, merge it, or rewrite it until it can.

For the test to mean anything, needs must be specific enough that *unmet* is a real state. The model resists saturation by structuring needs as a tree, refining root concerns into sharper sub-needs as discovery requires, and forbidding components from attaching to root needs — every addressing edge must land on a refined sub-need where the unmet test is actually answerable.

Addressing edges map components to needs they directly address through their primary mechanism — not to downstream consequences of that mechanism. A governance evaluation skill that checks conformity, followability, and coherence directly addresses the need for governance quality evaluation. It also *consequently* improves conformity and reduces agent-system friction, but those are effects of catching quality issues, not the component's primary contribution. Wiring edges to every consequence dilutes the model into completeness-of-mapping rather than justification, making "is this unmet?" harder to answer — the same saturation failure the tree structure exists to prevent.

Self-contained in this folder — database, CLI, and documentation. No dependencies outside this directory.

## Files

- **`purpose_map.py`** — implementation. The CLI and the only thing that touches the database.
- **`purpose-map.db`** — SQLite database. The live state of the model.
- **`CLAUDE.md`** (this file) — **operational reference**. Data model, CLI, evaluation protocol, writing guidelines. Stable across evaluation passes — changes only when the tool itself changes. Read on entry to any session.
- **`architecture.md`** — **design rationale**. The problem, the structural decisions, the alternatives. Stable across evaluation passes — changes only when the methodology evolves. Read when context on *why* is needed.
- **`state.md`** — **resumption state**. Current progress, scope, outstanding items. Mutates session-to-session. Read after CLAUDE.md to pick up where the last session left off.

Routing: if the agent needs it to *do* the next step, CLAUDE.md. If it explains *why that step exists*, architecture.md. If it's specific to the current evaluation pass, state.md.

## Data Model

SQLite database (`purpose-map.db`) with two entity types connected by four relationship types, plus per-component source-location references.

### Entities

- **Needs** — problems to solve (the "why"), organized as a tree via `parent_id`. Root needs (parent_id NULL) are project-level business concerns; refined sub-needs are added under parents as discovery requires more specificity.
- **Components** — structural units (the "how"). Anything that exists and can address needs.

### Identifiers

Entities use **auto-generated short ids**: `c1`, `c2`, ... for components and `n1`, `n2`, ... for needs. Ids are opaque handles assigned at insertion and never reused. Do not derive meaning from the id — the description is the load-bearing meaning.

All displays render entries as `[id] description` so the id is always paired with its purpose. There are no names — descriptive names invite pattern-matching against a stale mental model, which leads to wrong wirings.

Descriptions must be **clear and complete** because they are the only meaning the entity carries. If a description seems thin or ambiguous during evaluation, **surface a suggested correction to the user** — do not edit descriptions autonomously. See *Description integrity* for the reasons.

### Relationships

Two independent graphs over the entity types. A component can depend on one thing and address another — don't assume they align.

**depends_on** (component → component) — Structural DAG. "This component needs that component to exist." If the dependency were removed, the dependent would need to be re-engineered or would cease to exist. Answers: **what must exist for this to work?**

**addresses** (component → refined need) — Capability claim with rationale. A claim that this component contributes to addressing a specific sub-concern through a specific mechanism described in the rationale. Partial contribution is fine — many components can address the same sub-need through different mechanisms. The project owns its concerns; components are not "accountable for" them — they contribute mechanisms, captured in the addressing edge's rationale.

Wiring rules (enforced by the CLI):

- Cannot address a root need (must attach at depth ≥ 1)
- Cannot address both a need and any ancestor of that need
- Cannot address both a need and any descendant of that need
- Attach at the most specific sub-need where the component's mechanism applies — go as narrow as the contribution warrants, no narrower. To claim a broader concern, address the broader sub-need *instead of* the narrower one, not in addition to it
- Cross-branch addressing is allowed: a component may address multiple branches or trees if its mechanism genuinely spans them

These rules force every edge to land where "is this unmet?" has a meaningful answer, and prevent claiming the same concern at multiple granularity levels.

### Source-Location Paths

Components can record one or more **paths** pointing at where the real artifact lives. These are non-authoritative pointers — they tell a future reader where to look without claiming the location is permanently stable.

- A component can have zero, one, or many paths
- Paths can be files, directories, `file#anchor` (markdown heading anchors), or glob patterns (e.g. `skills/friction/*`)
- Conceptual components (`project`, `marketplace`) legitimately have no paths
- Paths are **true at creation**; if they break after a refactor, retrace by purpose using navigator or by content using grep, then update with `add-path`/`remove-path`

**Cohesive vs parallel collections.** When a component spans multiple files, the path strategy depends on how the files relate:

- **Cohesive collection → glob pattern** (e.g. `skills/friction/*`). The files interact to produce a single greater function. Removing any one file would break the others. The component is the collection; individual files don't independently justify against different needs. An MCP server's skill package (`__init__.py` + `_db.py`) is cohesive — the facade is useless without the backend, and vice versa.
- **Parallel collection → individual paths or anchors** (e.g. `file#section-a`, `file#section-b`). Each file or section serves independent needs side-by-side. Removing one doesn't break the others. Design principles within a rule file are parallel — each addresses its own set of needs through its own discipline.

**Decision test:** could you remove one part without the others needing to change? If no, the parts are cohesive — glob them as one component. If yes, the parts are parallel — each earns its own component with its own path.

Glob coverage doesn't hide files from scrutiny. If a file within a globbed component seems questionable, examine the component's addressing edges: which of its needs does this file serve? If none, either the file is vestigial or there's a missing need.

### Validation

Components and needs can be validated (`validate <id>`) or unvalidated (`invalidate <id>`). Validated = identity settled; unvalidated (shown with `?` prefix) = identity still under question. Validation is informational — validated entities can still gain new addressing edges. See *Validation criteria* for when to validate each entity type.

## Schema

```sql
components       (id, description, validated)
needs            (id, parent_id, description, validated)  -- parent_id NULL for roots
depends_on       (component_id → dependency_id)
addresses        (component_id → need_id, rationale)      -- many-to-many; need must not be a root
component_paths  (component_id → path)                    -- source-location pointers
```

## CLI

```
python3 purpose-map/purpose_map.py <command> [args...]
```

### Component commands

| Command | Purpose |
|---------|---------|
| `add-component <description>` | Create a component (id auto-assigned: `c{n}`) |
| `set-component <id> <description>` | Update description |
| `remove-component <id>` | Remove component and its edges |

### Need commands

| Command | Purpose |
|---------|---------|
| `add-need <description>` | Create a root need (id auto-assigned: `n{n}`); rare after initial bootstrap |
| `refine <parent-id> <description>` | Add a child need under an existing parent |
| `set-need <id> <description>` | Update description |
| `set-parent <need-id> <parent-id\|root>` | Re-parent a need; use `root` to make it a root |
| `remove-need <id>` | Remove a need; refused if it has children — re-parent or remove them first |

### Edge commands

| Command | Purpose |
|---------|---------|
| `depend <component> <dependency>` | Component depends on another |
| `undepend <component> <dependency>` | Remove dependency |
| `address <component> <need> <rationale>` | Component addresses a need, with rationale describing the specific mechanism |
| `unaddress <component> <need>` | Remove addressing edge |
| `set-rationale <component> <need> <rationale>` | Update rationale on an existing addressing edge |

### Path and validation commands

| Command | Purpose |
|---------|---------|
| `add-path <component> <path>` | Record a source-location path (file, directory, glob, or `file#anchor`) |
| `remove-path <component> <path>` | Remove a recorded path |
| `validate <id>` | Mark a component or need as validated |
| `invalidate <id>` | Revert validation |

### Analysis commands

| Command | Purpose |
|---------|---------|
| `dependencies [comp] [--verify]` | Structural tree from `depends_on` edges; `--verify` checks for unvalidated ancestors |
| `needs [root-id]` | Tree view of needs with coverage markers |
| `addresses [id] [--gaps] [--orphans]` | Addressing graph; `--gaps` lists unaddressed leaf needs; `--orphans` lists components addressing nothing |
| `where <component>` | Source-location paths for a component |
| `why <component>` | What needs this component addresses, with rationales |
| `how <need>` | What components address this need, with rationales |
| `compare <comp-a> <comp-b>` | Side-by-side addressing comparison: common needs and each-only needs |
| `summary` | Counts and gap status |
| `uncovered` | Project files not attached to any component |

### Output conventions

**Tree symbols:**

| Symbol | Meaning |
|--------|---------|
| `◈` | Component |
| `☆` | Root need (parent_id NULL) |
| `◇` | Refined sub-need |
| `?` prefix | Unvalidated (identity under question) |

**Coverage markers** (on `needs` output):

| Marker | Meaning |
|--------|---------|
| `✓` | Covered — has direct addressers or an addressed descendant |
| `✗` | Gap — leaf with no addressers (actionable) |
| `○` | Unrefined — root with no children (needs refinement before addressing) |
| (space) | Abstract — interior node with children but no addressed descendants yet |

**Coverage exclusions** (`uncovered` filters these before matching against component paths):

| Exclusion | Mechanism | Rationale |
|-----------|-----------|-----------|
| `.gitignore`'d files | `git ls-files` only returns tracked files | Generated files are not source artifacts |
| `tests/` directories | Manual filter: path contains `tests/` segment | Test implementations are derivative, not independent components |
| `test_*.py` files | Manual filter: filename prefix | Same — test files outside `tests/` |
| `conftest.py` files | Manual filter: exact filename | Test infrastructure, excluded from tracking. Test *infrastructure* (runners, configs) can still be claimed as components via explicit paths |

Bare directory paths (without `*`) mark containers in `uncovered` but do not suppress children. Glob patterns and exact paths suppress matching files.

## Querying the Model

**Justification — why does this exist?** `why <component>` shows what it addresses. `addresses --orphans` finds components addressing nothing — candidates for removal.

**Gaps — where is the actionable work?** `addresses --gaps` lists unaddressed leaf needs.

**How is this need addressed?** `how <need>` shows addressers with their rationales.

**Impact — what if I remove this?** `why <component>` shows its edges. If those needs have other addressers (`how <need>`), removal is safe. If it's the sole addresser, removal opens a gap.

**Foundation — can I trust what this builds on?** `dependencies <comp> --verify` checks for unvalidated ancestors.

## Evaluation Protocol

Evaluation is **live invention**, not catalog-fitting. The model starts with project-level needs and grows by inventing components in response to discovered unmet sub-needs. For each component-add, the test is: *what specific unmet sub-need does this address?*

The discipline:

- **Refinement is reactive, not anticipatory.** Don't pre-decompose the need tree. Refine when adding a component reveals an existing parent is too broad.
- **Every component must justify itself** by attaching to ≥1 unmet sub-need. A component that claims only what others already address through the same mechanism isn't justified.
- **Components may not survive re-evaluation.** If a component can't make the unmet pointer, remove it from the project. The model exists to surface this.

### Evaluation order

Add components in dependency order — most foundational first. Each addition tests itself against the existing model state, which only contains foundations validated in earlier steps. This prevents justifying components against future-promised attachments.

Work from foundations to structure, not depth-first. Each layer depends on the layers below being settled — both structurally (dependency chain) and conceptually (abstract concerns first, concrete mechanisms last). Project needs settle first, then design principles, then the components that address them.

Use `dependencies <component> --verify` to check for unvalidated ancestors — informational, not a gate on whether you're allowed to validate.

### Evaluating a component

1. **Read the source artifact.** Use `where`, navigator, or grep to find the real file/code. **Don't reason from the description alone** — read what's actually there.
2. **Identify the specific concern(s) the component contributes to.** Not "what broad need does this fit," but "what specific sub-concern does this component's mechanism actually solve?" Name the failure mode it prevents, the friction it closes, the work it eliminates.
3. **Locate the most-specific applicable need in the existing tree.** Use `needs` to scan. For each concern from step 2, find the deepest existing sub-need that captures it.
4. **If no existing sub-need is specific enough, refine.** Run `refine <parent-id> <description>`. Writing rules from *Needs* still apply. If you find yourself wanting to name a mechanism, the refinement isn't ready — sharpen the concern.
5. **Run the duplication scan.** `how <sub-need-id>` shows existing addressers. If your component would contribute through a mechanism another already provides, that's a duplication signal — merge, remove, or conclude it isn't justified. When the scan surfaces mechanism differences, use the contrast as a precision lens: is the target need description as precise as it could be given the distinct mechanisms? Are the *other* needs exposed in the scan — the needs addressed by the other components that appeared — as precise as they could be? The contrast is bidirectional; it informs every need it touches, not just the one being wired.
6. **Propose the addressing edge(s) to the user** using *Proposal format*. Include the sub-need, the rationale, and any refinements required. Propose initial edges in the same step as the component so orphans don't pollute the view. Wait for confirmation.
7. **Wire confirmed edges** with `address <component> <sub-need> "<rationale>"`.
8. **Verify claims against the implementation before validating:**
    - **Functional components** (tools, MCP servers, scripts) — exercise the mechanism. Confirm the claim matches reality.
    - **Descriptive components** (rules, conventions, principles) — verify *file-level conformance* (does the implementation follow per-file rules?) **and** *composition patterns* (does the convention capture how files relate across the project?). Verifying individual files in isolation misses architectural patterns.
    - If verification fails: (a) implementation bug to fix, (b) convention/description gap to fill, or (c) wrong claim to revise.
9. **Validate the component** once identity is confirmed. See *Validation criteria*.
10. **If the unmet test fails** — every plausible attachment either has no fit or is already addressed through the same mechanism — surface this to the user. The right next step is to remove the component from the project.

After the user confirms a component's proposal, wire its edges and re-run `summary` to show the coverage update before moving to the next component.

### Validation criteria

Validation captures *identity*, not *coverage*. Validated entities can still gain new addressing edges — validation does not freeze the model. The `?` prefix asks "is this real and right?", not "is this still going to change?"

**Needs** validate when purpose is clear and they pass *Needs* writing guidance — single business concern, third person, no embedded mechanisms.

**Components** validate when identified as a distinct, genuine contribution — purpose is clear, not subsumed by another. Addressing-edge completeness does not affect the decision.

**Containers** validate when role and scope are confirmed. Children do not need to be fully evaluated first — conflating container validation with descendant completeness mixes identity with progress. The worklist tracks progress; validation tracks identity.

### Component granularity

A multi-section file (like a rule file with several principles) is a container — an extension of its delivery mechanism — not a component itself. The file is the vehicle; each section earns its own component if it addresses distinct needs. Only purpose statements (file headings, structural preamble) remain as non-component content.

The delivery mechanism component (e.g. c3 for rules) claims the directory path. Individual sections use `file#anchor` paths. The file doesn't need its own component because it has no mechanism beyond what the delivery component provides.

This applies to files that bundle parallel sections: rule files, convention files, configuration files with independent sections. It does not apply to cohesive files — those are covered by the glob pattern guidance in *Source-Location Paths*.

### Evaluation checks

**Router vs destination.** When a rule routes the agent toward a tool, the rule's contribution is the *routing* — encoding the decision, closing the agent-instinct vs system-capability gap. The capability at the destination is a property of the destination component, not the rule. If a rationale describes properties of another component rather than what the rule itself does, the edge is mis-attributed — either drop it or reframe to claim only the routing effect. Track expected reclamations in `state.md`.

Test: what produces the claimed effect — this component's own behavior, or some other component's properties?

**Override vs description.** Rules override default agent behavior. A rule that *describes* default behavior is vestigial — it has no failure to prevent. Before proposing addressing edges for any rule, ask "is this an override or a description of default behavior?" If a description, halt the proposal, add a project-level action item to remove the entry, and move on.

Test: if the failure mode the rule prevents *cannot occur* in the current system (because the default already produces the right outcome), the rule is vestigial.

## Writing Guidelines

### Description integrity

Do not edit descriptions autonomously during evaluation. Surface a suggested correction to the user with the old text, proposed change, and rationale. Two reasons:

- **Mid-evaluation rewording can invalidate prior addressing edges** that were correct under the older meaning. The user has the broader perspective to judge whether to sharpen, hold the broader meaning, split, or leave it alone.
- **An agent focused on the current wiring will tend to over-sharpen** toward that one relationship, narrowing a deliberately-broad need. The right move when a component's concern is sharper than an existing need is to propose a new sibling need, not rewrite the existing one.

### Component descriptions

Component descriptions name the role and architectural shape — what the component is and what kind of contribution it makes. They survive refactoring: a rename, a storage migration, or a verb change should not invalidate the description.

- **Role and shape, not API surface.** Name what the component does and how it's structured (MCP server, SQLite-backed, skill package). Don't enumerate function names, tool names, or parameters.
- **Architectural properties over implementation details.** "SQLite-backed with separate project and user databases" survives; "stash_add, stash_review, stash_remove" doesn't.
- **Server instructions content is worth naming** — it encodes the agent-facing decision framework, a durable design choice even when tool names change.

### Needs

Need descriptions are the entity (see *Identifiers*) — they must carry the full meaning without relying on a name.

**Business concerns, not technical requirements.** Name what we want to accomplish, not how. Decomposing a concern into a technical requirement prematurely binds it to one implementation. If a description names a specific mechanism, encoding strategy, file format, or tool, it has slipped from concern into requirement — strip the technical specifics.

**Mechanisms and consequences out, constitutive parts in.** Phrases that name *one of several* ways to address the concern (mechanism) or *one of several* outcomes of failing it (consequence) get stripped — they narrow the need. Phrases that are *constitutive* — the framing that makes the concern exist as itself — get kept. Test: "if I removed this phrase, would the concern still exist as itself?" Yes → drop. No → keep.

**Test by inversion: "what would have had to go wrong for this to be needed?"** Work backward from the component to the failure mode it prevents. The need should name that failure mode in third person ("Prevent the agent from X"), not the mechanism that prevents it ("Verify X before acting"). Trigger bullets in a principle typically enumerate specific instances of the underlying failure — the unified failure mode is the constitutive concern.

**Preventative vs enabling framing.** Test: "If we remove everything addressing this need, does something specific go *wrong*, or does something just *not exist*?" Goes wrong → preventative ("Prevent the agent from breaking path assumptions"). Doesn't exist → enabling ("Allow the user to centrally examine plugin state", "Automate project governance deployment", "Ensure commits capture coherent topics"). The inversion test is a sharpening technique for preventative needs; don't force preventative framing when the concern doesn't have a natural failure mode.

**Common red flag: "so X" / "to X" tails.** A trailing clause that names a specific outcome is almost always picking one consequence among many. If the concern has multiple downstream effects, name none and let each addresser describe the specific consequences its mechanism targets.

**Third person.** "Reduce X", "Prevent Y", "Allow Z" — never "Allow me", "I may not see".

**Refine when discovery requires it; don't pre-decompose.** Refinement is reactive — it happens at the moment a component requires it, not in anticipation. Pre-decomposing re-introduces the saturation failure mode the tree is meant to prevent.

**Sub-needs follow the same writing rules as roots.** Refined children are business sub-concerns at finer grain, not technical requirements.

**Test against neighbors by mechanism, not name.** When two needs sound overlapping, check the mechanisms. If each names a different concern with a different remedy, they are distinct. If they collapse into one, merge them.

**Cut verbose phrasing.** Every word earns its place. Long "rather than" tails can usually be deleted; "from within any X" can become "across X". If removing a phrase doesn't change meaning, remove it.

### Rationales

A rationale describes the specific mechanism by which one component addresses one need. Because needs are mechanism-free, the rationale carries the full description of *how* — "encoded as a rule", "blocked at runtime by a hook", "captured into a friction queue." Rationales describe their relationship in isolation; cross-edge comparison is a reading-time operation.

- **Mechanism, not restatement.** Don't paraphrase the edge's existence. Say *how* the component addresses the need.
- **No contrast.** Don't write "different mechanism from cX" or "pairs with cY." If you need contrast to make a description clear, sharpen the description instead.
- **Avoid comparative locators.** "Producer-side / consumer-side" implies a contrast partner. Prefer concrete descriptions ("operates at build time").
- **Stand-alone test.** If the rationale makes sense without knowing about any other edge, it's good.

## Proposal Format

Wiring is not autonomous. Every `depend` and `address` is presented to the user for confirmation. The proposal must show full descriptions — reasoning from ids alone is impossible by design.

**Format.** Each proposal covers one component, shown once at the top in `[id] description` form. Addressing edges appear in two groups:

- **Recommended** — edges to wire. Each: need in `[id] description` form + one-paragraph rationale.
- **Considered and rejected** — edges not proposed. Each: need in `[id] description` form + rejection reason. Full descriptions required.

**One component per proposal.** Never bundle multiple components — it forces context-switching and obscures which rationale belongs to which pair.

**No name-style headings.** Never label a proposal "## c6 — Epistemic Humility" — headings reintroduce the named-object failure the no-name design prevents.

**Surface duplication.** Before proposing edges, run `how <need-id>` for each candidate need. Include a **Duplication scan** noting any existing addressers whose mechanism overlaps with the proposed one. The edge is still formed when the relationship is accurate — multi-edge addressing is valid. The scan makes overlap visible so the user can judge whether it's complementary or redundant.

**Component-add duplication scan.** When proposing a *new component*, search existing components for similar purpose first. Use `dependencies <parent>` to list components in the target layer. If overlap is significant, note it and either revise the description, fold into an existing component, or split. Use `compare <a> <b>` for side-by-side edge comparison.

Example:

```
[c8] Check what exists before building new because existing implementations
     are tested and maintained

Recommended:

- [n3] Avoid reinventing solutions to problems that have already been solved
  Rationale: direct hit — c8 is the upstream discipline that prevents the
  duplication n3 names.

Considered and rejected:

- [n11] Reduce cognitive load for both user and agent so attention stays on
       work that genuinely needs human or agent judgment
  Reason: reusing existing code does reduce what the agent has to understand,
  but cognitive load reduction is a downstream effect; c8's mechanism is
  supply-side (don't make new), not consumption-side (organize what exists).
```

## Operational Notes

- **Multi-edge addressing is valid and expected.** A component can address several sub-needs when each edge holds up on its own — don't artificially narrow to a single "primary" need.
- **Don't reject an edge because another component already addresses the same need.** Two components can address the same sub-need through different mechanisms. Rejection rationales like "X is the better vehicle" should trigger a check: is the candidate's mechanism actually the same, or just aimed at the same concern from a different angle?
- **Don't add needs speculatively.** Refine only when a component you're adding requires a sharper sub-concern than exists.
