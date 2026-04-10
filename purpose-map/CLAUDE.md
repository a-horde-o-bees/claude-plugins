# Purpose Map

purpose-map answers one question: **is this component justified by a specific unmet need?** Use it before adding anything to the project, and use it to audit what's already there. A component is justified when it points at a sub-concern that no existing component addresses through any mechanism. A component that can't make that pointer isn't justified — remove it, merge it, or rewrite it until it can.

For the test to mean anything, needs must be specific enough that *unmet* is a real state. Saturation at the root level (every component plausibly addressing the top-level concern) makes the test unfalsifiable. The model resists this by structuring needs as a tree, refining root concerns into sharper sub-needs as discovery requires, and forbidding components from attaching to root needs at all — every addressing edge must land on a refined sub-need where the unmet test is actually answerable.

Self-contained in this folder — database, CLI, and documentation. No dependencies outside this directory.

## Files in this folder

- **`purpose_map.py`** — implementation. The CLI and the only thing that touches the database.
- **`purpose-map.db`** — SQLite database. The live state of the model.
- **`CLAUDE.md`** (this file) — **operational reference**. The "how to use the tool": data model, schema, CLI, evaluation protocol, design principles for using the model. Stable across evaluation passes — only changes when the tool itself changes. Read on entry to any session.
- **`architecture.md`** — **design rationale**. The "why the tool is shaped this way": the problem it solves, the structural and methodological decisions that make it work, alternatives that don't, and how the techniques reinforce each other. Stable across evaluation passes — only changes when the methodology itself evolves. Read when context on *why* is needed; CLAUDE.md is enough for *how*.
- **`state.md`** — **resumption state**. The "where we are in the current evaluation pass": current data snapshot, scope and boundaries of the in-progress work, outstanding questions, next steps. Mutates session-to-session as the work advances. Read after CLAUDE.md to pick up where the last session left off.

Keep these cleanly separated:
- If something is *how to use the tool*, it goes in CLAUDE.md.
- If something is *why the tool is shaped this way*, it goes in architecture.md.
- If something is *the current status of the work*, it goes in state.md.

When in doubt about CLAUDE.md vs architecture.md: if the agent needs it to *do* the next operational step, CLAUDE.md. If it explains *why that step exists*, architecture.md.

When in doubt about CLAUDE.md/architecture.md vs state.md: would a brand-new evaluation pass on a different project still need this? If yes, CLAUDE.md or architecture.md. If no, state.md.

## Data Model

SQLite database (`purpose-map.db`) with two entity types connected by four relationship types, plus per-component source-location references.

### Entity Types

- **Needs** — problems to solve (the "why"), organized as a tree via `parent_id`. Root needs (parent_id NULL) are project-level business concerns; refined sub-needs are added under parents as discovery requires more specificity.
- **Components** — structural units (the "how"). Anything that exists and can address needs.

### Identifiers

Entities use **auto-generated short ids**: `c1`, `c2`, ... for components and `n1`, `n2`, ... for needs. Ids are opaque handles assigned at insertion and never reused. Do not derive meaning from the id — the description is the load-bearing meaning.

All displays render entries as `[id] description` so the id is always paired with its purpose. Reasoning from a name alone is impossible because there is no name. This is intentional — descriptive names invite pattern-matching against a stale mental model, which leads to wrong wirings.

A consequence: descriptions must be **clear and complete** because they are the only meaning the entity carries. If a description seems too thin or ambiguous during evaluation, **surface a suggested correction to the user** with the old text, proposed change, and rationale — do not edit descriptions autonomously. See *Description integrity* in the operational notes below for the reasons.

### Relationship Types

Two independent graphs over the entity types. Each answers a different question.

**depends_on** (component → component) — Structural DAG. "This component needs that component to exist." If the dependency were removed, the dependent would need to be re-engineered or would cease to exist. Multiple dependencies per component allowed.

- Rules depend on a plugin for deployment
- Plugins depend on the marketplace for delivery
- Answers: **what must exist for this to work?**

**addresses** (component → refined need) — Capability claim, with rationale. A claim that this component contributes to addressing a specific sub-concern. Partial contribution is fine — many components can address the same sub-need through different mechanisms described in their rationales. The rationale is where component-specific implementation lives.

Wiring rules (enforced by the CLI):

- A component cannot address a root need (must attach at depth ≥ 1)
- A component cannot address both a need and any ancestor of that need
- A component cannot address both a need and any descendant of that need
- Attach at the most specific sub-need where the component's mechanism actually applies — go as narrow as the contribution warrants, no narrower
- Cross-branch addressing is allowed: a component may address sibling nodes, multiple branches, or multiple trees if its mechanism genuinely spans them

The "no root, no ancestor, no descendant" rules force every addressing edge to land at the level of specificity where "is this unmet?" has a meaningful answer, and prevent the same component from claiming the same concern at multiple levels of granularity.

Answers: **how is this specific sub-concern being handled?**

### Project-implicit ownership

Needs are project-implicit: the data structure lives within a project, so all needs belong to the project by definition. There is no separate ownership graph. Components are connected to needs only through `addresses`.

This is intentional. The project owns its concerns; components contribute mechanisms for addressing them. A component is not "accountable for" a concern — it just has something to offer toward the concern. The contribution is captured by the addressing edge and described in its rationale.

### Source-Location Paths

Components can record one or more **paths** pointing at where the real artifact lives. These are non-authoritative pointers — they tell a future reader where to look without claiming the location is permanently stable.

- A component can have zero, one, or many paths
- Paths can be files, directories, or `file#anchor` (markdown heading anchors)
- Conceptual components (`project`, `marketplace`) legitimately have no paths
- Paths are **true at creation**; if they break after a refactor, retrace by purpose using navigator or by content using grep, then update with `add-path`/`remove-path`. No automatic validation — refactor resilience is intentional manual rectification, not silent auto-healing.

### Validation Status

Components and needs can be validated or unvalidated.

- Validated = confirmed as a real, distinct contribution to the model — its identity is settled
- Unvalidated = identity still under question (might not belong, might overlap with another, might need to be split or rephrased), shown with `?` prefix in displays

Validation is informational, not functional. Validated entities can still gain new addressing edges as later layers are evaluated — validation does not freeze the model. See *Validation criteria* below for when to validate each entity type.

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
| `refine <parent-id> <description>` | Add a child need under an existing parent (the primary way to extend the tree during evaluation) |
| `set-need <id> <description>` | Update description |
| `set-parent <need-id> <parent-id\|root>` | Re-parent a need; use `root` to make it a root |
| `remove-need <id>` | Remove a need; refused if it has children — re-parent or remove them first |

### Dependency edges

| Command | Purpose |
|---------|---------|
| `depend <component> <dependency>` | Component depends on another |
| `undepend <component> <dependency>` | Remove dependency |

### Addressing edges

| Command | Purpose |
|---------|---------|
| `address <component> <need> <rationale>` | Component addresses a need, with rationale describing the specific mechanism |
| `unaddress <component> <need>` | Remove addressing edge |
| `set-rationale <component> <need> <rationale>` | Update rationale on an existing addressing edge |

### Path references

| Command | Purpose |
|---------|---------|
| `add-path <component> <path>` | Record a source-location path (file, directory, or `file#anchor`) |
| `remove-path <component> <path>` | Remove a recorded path |

### Validation commands

| Command | Purpose |
|---------|---------|
| `validate <id>` | Validate a component or need (mark as confirmed) |
| `invalidate <id>` | Invalidate a component or need (remove validation marker) |

### Analysis commands

| Command | Purpose |
|---------|---------|
| `dependencies [comp] [--verify]` | Structural tree of components from `depends_on` edges only; optional validation-chain check |
| `needs [root-id]` | Tree view of needs with coverage markers (full tree or rooted at given need) |
| `addresses [id] [--gaps] [--orphans]` | Addressing graph for a need or component; `--gaps` lists leaf needs with no addressers; `--orphans` lists components addressing nothing |
| `where <component>` | Recorded source-location paths for a component; the bridge from a db entry to the real artifact |
| `why <component>` | What needs does this component address (with rationales) |
| `how <need>` | What addresses this need (with rationales) |
| `compare <component-a> <component-b>` | Side-by-side addressing comparison: common needs (both address, with each rationale shown) and each-only needs. Used to evaluate whether two components are doing overlapping work through the same or different mechanisms |
| `summary` | High-level counts and gap status |

### Coverage status legend

| Marker | Meaning |
|--------|---------|
| `✓` covered | Has direct addressers OR a descendant is addressed |
| `✗` gap | Non-root leaf with no addressers — actionable: needs a component |
| `○` unrefined | Root with no children — actionable: needs refinement before any component can address it |
| (space) abstract | Interior or root with children but no addressed descendants yet |

## Questions the Model Answers

### Justification — why does this exist?

`why <component>` shows what the component addresses. Every component should address something. `addresses --orphans` finds components that address nothing — candidates for removal or unjustified existence.

### Gaps — where is the actionable work?

`addresses --gaps` shows needs with no addressers. These are the concrete unmet concerns.

### How is this need addressed?

`how <need>` shows the need's direct addressers with their rationales. Each rationale describes the specific mechanism that component contributes.

### Impact — what happens if I remove this?

`why <component>` shows what it addresses. If those needs have other addressers (check with `how <need>`), removal is safe. If it's the only addresser of a need, removal opens a gap.

### Foundation — can I trust what this builds on?

`dependencies --verify` checks the structural dependency chain. All ancestors must be validated before this component's evaluation is trustworthy.

## Operational Protocol

Evaluation is **live invention**, not catalog-fitting. The model starts with project-level needs and grows by inventing components in response to discovered unmet sub-needs. For each component-add, the test is: *what specific unmet sub-need does this address?* If the test can't be answered against an existing or proposed sub-need, the component isn't justified — focus elsewhere or remove the component from the project entirely.

The discipline this enforces:

- **Refinement is reactive, not anticipatory.** Don't pre-decompose the need tree. Refine when adding a component reveals an existing parent is too broad to attach to with the right specificity.
- **Every component must justify itself by attaching to ≥1 unmet sub-need.** A component that claims only what other components already address through the same mechanism isn't justified.
- **Some current components may not survive re-evaluation.** If a component can't make the unmet pointer, the right move is to remove it from the project, not to fudge an attachment. The model exists to surface this.

### Evaluating a component

1. **Read the source artifact.** Use `where`, navigator, or grep to find the real file/code. **Don't reason from the description alone** — read what's actually there.
2. **Identify the specific concern(s) the component contributes to.** Not "what broad need does this fit," but "what specific sub-concern does this component's mechanism actually solve?" Be concrete: name the failure mode it prevents, the friction it closes, the work it eliminates.
3. **Locate the most-specific applicable need in the existing tree.** Use `needs` to scan the tree. For each candidate concern from step 2, find the deepest existing sub-need that captures it.
4. **If no existing sub-need is specific enough, refine.** Run `refine <parent-id> <description>` to add a child sub-need under the most relevant parent. Description-quality rules from *Writing needs* still apply: business-level, mechanism-free, single concern. If you find yourself wanting to name a mechanism, the refinement isn't ready — sharpen the concern.
5. **Run the duplication scan.** `how <sub-need-id>` shows existing addressers. Compare your proposed mechanism against what's already there. If your component would contribute through a mechanism another component already provides, that's a duplication signal — either the components should merge, or one should be removed, or the proposed component isn't justified.
6. **Propose the addressing edge(s) to the user** using *Relationship proposal format*. Show the sub-need, the rationale (the specific mechanism this component contributes), and any refinements required. Wait for confirmation per edge.
7. **Wire confirmed edges** with `address <component> <sub-need> "<rationale>"`. The CLI enforces: cannot address roots, cannot address an ancestor of an already-addressed need, cannot address a descendant of an already-addressed need.
8. **Verify component claims against the implementation before validating.** Verification depends on the kind of component:
    - **Functional components** (tools, MCP servers, scripts) — run the function, call the tool, exercise the mechanism. Confirm the claim matches reality.
    - **Descriptive components** (rules, conventions, principles) — read the implementation the component governs and verify the description captures both *file-level conformance* (does the implementation follow the convention's per-file rules?) **and** *composition patterns* (does the convention capture how files relate to each other across the project?). The composition check is critical for conventions that govern multi-file systems — verifying individual files in isolation misses architectural patterns the convention should describe. The audit gap shows up later when downstream consumers (other agents, future evaluators) follow the convention literally and produce structurally inconsistent implementations.
    - If verification fails, the discrepancy is one of: (a) an implementation bug to fix, (b) a convention/description gap to fill, or (c) a wrong claim to revise.
    - Verification happens before validation because validation should not lock in claims that don't hold.
9. **Validate the component** once its identity is confirmed — distinct contribution to the model, clear purpose, attached to at least one unmet sub-need that no other component addresses through the same mechanism. For components with functional claims, validation also requires empirical verification has succeeded. See *Validation criteria*.
10. **If the unmet test fails** — every plausible attachment point either has no fit, or is already addressed through the same mechanism by another component — the component isn't justified. Surface this to the user with the analysis. The right next step is to remove the component from the project (not from the model).

### Foundations-up evaluation order during live invention

Add components in dependency order. Most foundational first: project containers, then the components they depend on, then the components those depend on. Each addition tests itself against the existing model state, which only contains foundations validated in earlier steps. This prevents the failure mode of justifying components against future-promised attachments.

### Foundations-up evaluation order

Work from foundations to structure, not depth-first. Each layer depends on the layers below being settled — both structurally (the dependency chain) and conceptually (abstract concerns first, concrete mechanisms last). Both axes point the same direction: project needs settle first, then design principles, then the components that address them. Each layer builds on the certainty of the layers below.

Containers can be validated with `validate <id>` whenever their identity (role and scope) is settled — they do not have to wait for descendants. Conflating container validation with descendant completeness mixes identity with progress; the worklist tracks progress, validation tracks identity.

Run `dependencies <component> --verify` to check the structural dependency chain for unvalidated ancestors. It is informational — useful when you want to confirm the chain below a component is fully validated, not a gating check on whether you're allowed to validate something.

### Validation criteria

Validation captures *identity*, not *coverage*. A validated entity is confirmed as a real, distinct contribution to the model — it belongs at the level where it sits, with a clear purpose. An unvalidated entity is one whose identity is still under question (might not belong, might overlap with another, might need to be split or rephrased).

Validation is informational, not functional. Validated entities can still gain new addressing edges as later layers are evaluated — validation does not freeze the model. The `?` prefix on unvalidated entities asks "is this real and right?", not "is this still going to change?"

**Needs** validate when their purpose is clear and they pass the *Writing needs* guidance — single business concern, third person, no embedded mechanisms or consequences, no decomposition into technical requirements. Coverage status (whether addressers exist) does not affect the validation decision.

**Components** validate when the component is identified as a distinct, genuine contribution to the model — purpose is clear and not subsumed by another component. Addressing-edge completeness does not affect the validation decision; new edges can be wired later as consumers are evaluated.

**Containers** validate when the container's role and scope are confirmed — "this layer holds these kinds of things, with this identity." Children do not need to be fully evaluated first. Conflating container validation with descendant completeness mixes identity with progress; the worklist tracks progress, validation tracks identity.

**Commands.** Use `validate <id>` to mark a need or component as validated, and `invalidate <id>` to revert. Both work on either entity type.

### Description integrity

Do not edit descriptions autonomously during evaluation. Surface a suggested correction to the user instead, with the old text, proposed change, and rationale. After the user confirms, run `set-need <id> "..."` for needs or `set-component <id> "..."` for components.

Two reasons:
- **Mid-evaluation rewording can invalidate prior addressing edges** that were correct under the older meaning. The user has the broader perspective to judge whether to sharpen, hold the broader meaning, split into multiple entities, or leave it alone.
- **An agent focused on the current wiring will tend to over-sharpen** toward that one relationship, narrowing a deliberately-broad need into something it wasn't meant to be. The right move when a component's concern is sharper than an existing need is to surface the gap and propose a new sibling need to the user, not to rewrite the existing one.

### Writing component descriptions

Component descriptions name the role and architectural shape — what the component is and what kind of contribution it makes. They survive refactoring: a rename, a storage migration, or a verb change should not invalidate the description.

- **Role and shape, not API surface.** Name what the component does and how it's structured (MCP server, SQLite-backed, skill package). Don't enumerate function names, tool names, parameters, or file formats — those are implementation details visible in the source artifact itself (reachable via `where`).
- **Architectural properties over implementation details.** "SQLite-backed with separate project and user databases" survives; "stash_add, stash_review, stash_remove, stash_promote" doesn't.
- **Server instructions content is worth naming** — it encodes the agent-facing decision framework, which is a durable design choice even when tool names change.

### Writing needs

Need descriptions are the entity (see *Identifiers*) — they must carry the full meaning without relying on a name.

**Business concerns, not technical requirements.** Need descriptions name the concern broadly — what we want to accomplish, not how to accomplish it. Decomposing a business concern into a technical requirement (e.g., "address this concern *via X mechanism*") prematurely binds the concern to one implementation, removing flexibility for refactoring. The whole point of an AI-led system is that the agent picks the mechanism; the model shouldn't pre-bind it. If a description names a specific mechanism, encoding strategy, file format, or tool, it has slipped from concern into requirement — strip the technical specifics and keep the business intent.

**Mechanisms and consequences out, constitutive parts in.** A description names the concern itself. Phrases that name *one of several* ways to address the concern (mechanism) or *one of several* outcomes of failing it (consequence) get stripped — they pick a single instance from a broader picture and quietly narrow the need. Phrases that are *constitutive* — the asymmetry, framing, or definition that makes the concern exist as itself — get kept. Test: "if I removed this phrase, would the concern still exist as itself?" Yes → mechanism or consequence, drop. No → constitutive, keep.

**Test by inversion: "what would have had to go wrong for this to be needed?"** When proposing or refining a need that a component will address, work backward from the component to the failure mode it prevents. The need should name that failure mode in third person ("Prevent the agent from X"), not the mechanism that prevents it ("Verify X before acting"). Trigger bullets and case-specific bullets in a principle typically enumerate the specific instances of the underlying failure — the unified failure mode across them is the constitutive concern. This complements the constitutive-vs-mechanism rule: failure modes are constitutive (the concern is preventing them); the actions that prevent them are mechanism-flavored and belong in the addressing-edge rationale, not in the need text.

**Common red flag: "so X" / "to X" tails.** A trailing clause that names a specific outcome of addressing the concern is almost always picking one consequence among many. If the concern has multiple downstream effects, the description should name none of them and let each addresser describe in its rationale the specific consequences its mechanism targets.

**Third person.** "Reduce X", "Prevent Y", "Allow Z" — never "Allow me", "I may not see". First person sneaks in when the writer is talking to themselves; the description should read the same way to anyone.

**Refine when discovery requires it; don't pre-decompose.** Needs form a tree via `parent_id`. Roots are project-level concerns and cannot be addressed directly — every addressing edge must land on a refined sub-need. When adding a component reveals that the most-specific existing sub-need is still too broad to capture what the component actually contributes, run `refine <parent> <description>` to add a sharper child. Refinement is reactive — it happens at the moment a component requires it, not in anticipation of components that might later need it. Pre-decomposing the tree before discovery pre-binds it to imagined future needs and re-introduces the saturation failure mode the tree is meant to prevent.

**Sub-needs follow the same writing rules as roots.** Refined children are *business sub-concerns at finer grain*, not technical requirements. Same rules apply: no embedded mechanisms, no consequences, third person, single concern. If a refinement names a specific implementation choice, file format, or tool, it has slipped from concern into requirement — strip the mechanism and re-state the concern.

**Test against neighbors by mechanism, not name.** When two needs sound overlapping by their names, check the mechanisms. If each names a different concern with a different remedy, they are distinct. If the concerns collapse into one, merge them. This applies at every level of the tree.

**Cut verbose phrasing.** Every word earns its place. Long "rather than" tails that re-explain the goal can usually be deleted; "from within any X" can usually become "across X". If a phrase doesn't change the meaning when removed, remove it.

### Writing rationales

A rationale is the reasoning for one addressing edge — the specific mechanism by which this component addresses this need. Rationales are where component-specific implementation lives. They describe their relationship in isolation; cross-edge comparison is a reading-time operation, not a writing-time one.

Because needs are intentionally mechanism-free (see *Writing needs*), the rationale carries the full description of *how* this component contributes. This is the right place for "encoded as a rule", "blocked at runtime by a hook", "captured into a friction queue", "verified by reading the file" — anything that names a specific implementation choice.

- **Mechanism, not restatement.** Don't say "c8 addresses n3 because n3 is about avoiding reinvention." That just paraphrases the edge's existence. Say *how* the component addresses the need — what action, structure, or discipline it contributes that handles the need.
- **No contrast.** Don't write "different mechanism from cX" or "pairs with cY" or "distinct from cZ's angle." When the reader wants to compare edges that share an endpoint, they read all the relevant rationales together. If you need contrast to make your mechanism description clear, the description isn't precise enough — sharpen it instead.
- **Avoid comparative locators.** "Producer-side / consumer-side", "upstream / downstream", "structural / behavioral" all imply a contrast partner. They're fine if the partner doesn't need to be named to understand them, but prefer concrete mechanism descriptions when possible ("operates at build time" rather than "producer-side").
- **Stand-alone test.** Read your rationale with the rest of the database hidden. If it makes sense without knowing about any other edge, it's good. If it depends on the reader having just read another rationale, trim it.

### Router vs destination

When a rule routes the agent toward a tool or mechanism, the rule's contribution is the *routing* — encoding the decision, publishing the reach, closing the agent-instinct vs system-capability gap. The capability at the destination (token efficiency, verification quality, indexed lookup, accuracy, etc.) is a property of the destination component, not of the rule that points at it. A rationale must describe what *this component* does, not what *some other component it points at* does.

If your rationale describes properties of a component the rule depends on rather than what the rule itself does, the edge is mis-attributed. Either drop it (the property belongs to the destination, which will claim the need when its own evaluation reaches it) or reframe the rationale to claim only the routing effect. Track expected future reclamations in `state.md` so they aren't lost.

**Test:** what produces the claimed effect — your rule's own behavior, or some other component's properties? If the rule itself, the edge is correct. If another component, the edge belongs there.

### Override vs description

Rules exist to override default agent behavior. A rule that *describes* default behavior — telling the agent to do what it would already do without instruction — is vestigial: it has no failure to prevent because the failure can't occur. Such a rule (or rule bullet) should be removed from the project, not wired as an addressing edge in the model.

Common origin: a rule was written when the system had friction with some default behavior; the friction was later fixed at the system level (hook, tool, runtime); the rule entry was reversed to describe the new default rather than removed entirely. The vestigial entry takes up context that could be used for actual overrides.

**Test:** if the failure mode the rule prevents *cannot occur* in the current system (because the system's default behavior already produces the right outcome), the rule is describing a default and should be flagged for removal. Surface to the user with the analysis so the project can drop the entry. Do not wire an addressing edge for such a rule — there's nothing to address.

**When to apply:** before proposing the addressing edge for any rule (especially Layer C rules), ask "is this an override or a description of default behavior?" If a description, halt the wiring proposal, add a project-level action item to remove the entry, and move on. The model should only contain components that produce real effects.

### Relationship proposal format

Wiring is not autonomous. Every relationship proposed during evaluation — `depend`, `address` — is presented to the user for confirmation before being wired. Reasoning from ids alone is impossible by design (see *Identifiers*); the proposal must show full descriptions so the user can evaluate the pairing on its merits without recalling what an id refers to.

**Format.** Each proposal covers one component, shown once at the top in `[id] description` form. Proposed addressing edges appear underneath in two groups:

- **Recommended** — edges to wire. Each entry lists the need in `[id] description` form followed by a one-paragraph rationale.
- **Considered and rejected** — edges deliberately not proposed. Each entry lists the need in `[id] description` form followed by the reason for rejection. Full descriptions are required, not just ids — without the description the user can't evaluate the reason against the actual need.

**Batch by component, not across components.** A single proposal covers one component. The user evaluates that component's full contribution at once and confirms or revises. Never bundle multiple components into a single proposal — it forces the user to context-switch between unrelated decisions and obscures which rationale belongs to which pair.

**No name-style headings on proposals.** A proposal block contains only `[id] description` pairs, never a separate name, label, or summary heading for the component being evaluated. Headings like "## c6 — Epistemic Humility" reintroduce the named-object failure mode that the no-name design (see *Identifiers*) exists to prevent — the eye lands on the label and skips the description, and the rationale gets evaluated against a mental shorthand instead of the actual statement.

**Surface duplication, don't suppress it.** Before proposing addressing edges, run `how <need-id>` for each candidate need to see all existing addressers and their rationales. Use this to (a) notice components that the new edge might overlap with, and (b) compare your proposed mechanism against the existing ones.

The proposal then includes the standard *Recommended* and *Considered and rejected* groups *plus* a brief **Duplication scan** noting any existing addressers whose mechanism overlaps with the proposed mechanism. The edge is still formed when the relationship is accurate — multi-edge addressing is valid and expected. The duplication scan exists to make overlap *visible* so the user can decide whether it's complementary (defense in depth, distinct mechanisms at different layers) or redundant (same mechanism, two implementations) and choose what to do.

This interacts with two existing rules:

- **"Don't reject because another addresser exists"** (see *Operational notes*) prevents *missing* edges by reflexively rejecting valid additions.
- **"Surface duplication"** prevents *invisible* duplication by making the scan part of the proposal.

Both rules result in the edge being formed when the relationship is accurate. They differ only in what the proposal output makes visible: the first ensures the edge is not blocked; the second ensures any overlap is named for the user to evaluate.

**Component-add duplication scan.** When proposing a *new component* (not just a new edge), search existing components for similar purpose first. Use `dependencies <parent>` to list components in the target layer (e.g., `dependencies c4` for rule-layer components), then read each description. For plugin components, also check whether the proposed contribution overlaps with already-validated components in adjacent layers. If a candidate overlaps significantly, the proposal should explicitly note the overlap and either: revise the new description to make the distinction clear, fold the new contribution into an existing component, or split the existing one to make room. If two existing components are themselves potentially overlapping, run `compare <component-a> <component-b>` to see their addressing edges side-by-side.

After the user confirms a component's proposal, wire its edges and re-run `summary` to show the coverage update before moving to the next component.

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

### Operational notes

- The two graphs (`depends_on` and `addresses`) are independent: a component can depend on one thing and address yet another. Don't assume they align.
- **Multi-edge addressing is valid and expected.** A component can address several sub-needs when each edge holds up on its own — don't artificially narrow to a single "primary" need.
- **Don't reject an edge because another component already addresses the same need.** `addresses` is many-to-many. Two components can address the same sub-need through different mechanisms. Each mechanism is its own contribution. Test the candidate edge on its own merits. Rejection rationales like "X is the better vehicle" should trigger a check: is the candidate's mechanism actually the same as X's, or just aimed at the same concern from a different angle?
- **Address at the most-specific applicable sub-need.** If your component's mechanism only applies to one specific sub-concern, address that sub-concern, not its parent. The CLI rejects ancestor + descendant combinations on the same component to enforce this. If you want to claim a broader concern, the answer is to address the broader sub-need *instead of* the narrower one, not in addition to it.
- **Read the source, not the summary.** The db description is a one-line gist. Use `where <component>` to find the real artifact and read it before evaluating.
- **Don't add needs speculatively.** Refine only when a component you're adding actually requires a sharper sub-concern than exists. Speculative refinement is the same anti-pattern as speculative decomposition.
- When adding a new component, propose its initial addressing edges in the same step so floating components don't pollute the orphan view.

### Tree display conventions

- `◈` — components
- `☆` — root needs (parent_id NULL)
- `◇` — non-root needs (refined sub-needs)
- `?` prefix — unvalidated (identity still under question)
- No prefix — validated (identity confirmed)
- `✓` — covered (need has direct addressers or addressed descendants)
- `✗` — gap (non-root leaf with no addressers — needs a component)
- `○` — unrefined (root with no children — needs refinement before addressing)
- (space) — abstract (interior or root with children but no addressed descendants yet)
- Tree characters (`├──`, `└──`, `│`) show descent
