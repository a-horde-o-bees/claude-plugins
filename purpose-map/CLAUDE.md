# Purpose Map

Decision-making tool for validating why things exist and choosing what to build. Self-contained in this folder — database, CLI, and documentation. No dependencies outside this directory.

## Files in this folder

- **`purpose_map.py`** — implementation. The CLI and the only thing that touches the database.
- **`purpose-map.db`** — SQLite database. The live state of the model.
- **`CLAUDE.md`** (this file) — **operational reference**. The "how to use the tool": data model, schema, CLI, evaluation protocol, design principles for using the model. Stable across evaluation passes — only changes when the tool itself changes. Read on entry to any session.
- **`state.md`** — **resumption state**. The "where we are in the current evaluation pass": current data snapshot, scope and boundaries of the in-progress work, outstanding questions, next steps. Mutates session-to-session as the work advances. Read after CLAUDE.md to pick up where the last session left off.

Keep these cleanly separated. If something is *how to use the tool*, it goes in CLAUDE.md. If something is *the current status of the work*, it goes in state.md. When in doubt: would a brand-new evaluation pass on a different project still need this? If yes, CLAUDE.md. If no, state.md.

## Data Model

SQLite database (`purpose-map.db`) with two entity types connected by four relationship types, plus per-component source-location references.

### Entity Types

- **Needs** — problems to solve (the "why").
- **Components** — structural units (the "how"). Anything that exists and can address needs.

### Identifiers

Entities use **auto-generated short ids**: `c1`, `c2`, ... for components and `n1`, `n2`, ... for needs. Ids are opaque handles assigned at insertion and never reused. Do not derive meaning from the id — the description is the load-bearing meaning.

All displays render entries as `[id] description` so the id is always paired with its purpose. Reasoning from a name alone is impossible because there is no name. This is intentional — descriptive names invite pattern-matching against a stale mental model, which leads to wrong wirings.

A consequence: descriptions must be **clear and complete** because they are the only meaning the entity carries. If a description seems too thin or ambiguous during evaluation, **surface a suggested correction to the user** with the old text, proposed change, and rationale — do not edit descriptions autonomously. See *Description integrity* in the operational notes below for the reasons.

### Relationship Types

Four independent graphs over the same entity types. Each answers a different question.

**depends_on** (component → component) — Structural DAG. "This component needs that component to exist." If the dependency were removed, the dependent would need to be re-engineered or would cease to exist. Multiple dependencies per component allowed.

- Rules depend on a plugin for deployment
- Plugins depend on the marketplace for delivery
- Answers: **what must exist for this to work?**

**refines** (need → need) — Need decomposition DAG. "This need is a sharper, more specific version of that one." A child need refines a parent need; addressing the child contributes to addressing the parent. Multiple parents allowed (same child can refine more than one parent).

- `recover-after-context-clear` refines `avoid-progress-loss`
- `enforce-conventions` refines `prevent-mistakes`
- Answers: **how does this need decompose into more specific concerns?**

**owns** (component → need) — Single-owner allocation. A design decision about which component is accountable for a need. Each need has **exactly one owner** — enforced at the schema level. If two components both care about the same concern, the second creates a refinement and owns *that*.

- The project owns root needs
- A plugin owns the focused sub-needs (refinements) it is accountable for
- Answers: **who is accountable for this?**

**addresses** (component → need) — Capability claim. A claim that this component contributes to addressing a need. Partial contribution is fine — many components can address the same need, each handling part of it. Addressing edges cross structural boundaries freely.

- A design principle addresses a project need
- A skill addresses a specific refinement
- Answers: **how is this need being handled?**

### Ownership vs Addressing

`owns` and `addresses` answer different questions and must not be conflated. A component **owns** a need only when removing the component would also remove the concern itself. Plugins are mechanisms that *address* project concerns, not the parties accountable for those concerns. The project as a whole owns the broad concerns; plugins own only refinements that are genuinely plugin-specific (the concern would not exist without the plugin's mechanism).

When deciding whether a plugin should own something, ask: *"If this plugin disappeared, would this concern disappear too, or would the project still need to find another way to handle it?"* If the latter, the plugin should `address` the need, not `own` it.

### Layered Need Specificity

Needs decompose by structural layer. **Project root needs** name broad concerns owned by the project as a whole. **Plugin refinements** name sharper sub-concerns that exist *because* a particular plugin's mechanism makes them exist — owned by the plugin per the disappearance test above.

The grain of a need should match the grain of the components that address it:

- **Project-general components** (e.g., design principles, the marketplace) address project-level needs directly. Their mechanism is general, not tied to any one plugin.
- **Plugin-specific components** (e.g., rules, conventions, tools, skills inside a plugin) address plugin refinements primarily. Their mechanism *is* the plugin's mechanism, and the refinement names exactly that sub-concern.

When a plugin-specific component is forced to address a project-level need directly, that's a signal the refinement layer is missing — the component is bridging a generalization gap that should be made explicit as a refined need owned by the plugin.

Coverage propagates upward through refinements: addressing a refinement contributes to addressing its parent. A plugin can fully cover its own refinements while a project-level need still shows as "partial" because other plugins haven't carved their own refinements yet.

### Source-Location Paths

Components can record one or more **paths** pointing at where the real artifact lives. These are non-authoritative pointers — they tell a future reader where to look without claiming the location is permanently stable.

- A component can have zero, one, or many paths
- Paths can be files, directories, or `file#anchor` (markdown heading anchors)
- Conceptual components (`project`, `marketplace`) legitimately have no paths
- Paths are **true at creation**; if they break after a refactor, retrace by purpose using navigator or by content using grep, then update with `add-path`/`remove-path`. No automatic validation — refactor resilience is intentional manual rectification, not silent auto-healing.

### Lock Status

Components and needs can be locked or unlocked.

- Locked = confirmed, foundational, not under question
- Unlocked = under evaluation, shown with `?` prefix in displays

## Schema

```sql
components       (id, description, locked)
needs            (id, description, locked)
depends_on       (component_id → dependency_id)
refines          (need_id → refined_need_id)        -- child → parent
owns             (component_id → need_id UNIQUE)    -- single owner per need
addresses        (component_id → need_id)           -- many-to-many
component_paths  (component_id → path)              -- source-location pointers
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
| `add-need <description>` | Create a need (id auto-assigned: `n{n}`) |
| `set-need <id> <description>` | Update description |
| `remove-need <id>` | Remove need and its edges |

### Dependency edges

| Command | Purpose |
|---------|---------|
| `depend <component> <dependency>` | Component depends on another |
| `undepend <component> <dependency>` | Remove dependency |

### Refinement edges

| Command | Purpose |
|---------|---------|
| `refine <child-need> <parent-need>` | Child need refines parent need |
| `unrefine <child-need> <parent-need>` | Remove refinement |

### Ownership edges

| Command | Purpose |
|---------|---------|
| `own <component> <need>` | Component owns a need (single owner; rejected if already owned) |
| `disown <component> <need>` | Remove ownership |

### Addressing edges

| Command | Purpose |
|---------|---------|
| `address <component> <need>` | Component addresses a need (partial contribution is fine) |
| `unaddress <component> <need>` | Remove addressing edge |

### Path references

| Command | Purpose |
|---------|---------|
| `add-path <component> <path>` | Record a source-location path (file, directory, or `file#anchor`) |
| `remove-path <component> <path>` | Remove a recorded path |

### Lock commands

| Command | Purpose |
|---------|---------|
| `lock <id>` | Lock a component or need |
| `unlock <id>` | Unlock a component or need |

### Analysis commands

Three primary views, one per non-trivial graph, plus two cross-graph traversals and a summary.

| Command | Purpose |
|---------|---------|
| `dependencies [comp] [--verify]` | Structural tree of components from `depends_on` edges only; optional lock-chain check |
| `ownership [comp]` | For each owner, show owned needs and how each is addressed (covered / partial / gap) including coverage propagated through refinements |
| `addresses [id] [--gaps] [--orphans]` | Addressing graph for a need or component; `--gaps` lists leaf needs nothing addresses; `--orphans` lists components addressing nothing |
| `where <component>` | Recorded source-location paths for a component; the bridge from a db entry to the real artifact |
| `why <component>` | Upward trace: what does this component address, what needs are those, what parent needs do they refine, and who owns the chain |
| `how <need>` | Downward trace: direct addressers + refinement subtree (recursively), with leaf gaps marked |
| `summary` | Counts, root needs (top of refinement chains), and per-root addressing status |

### Coverage status legend

| Marker | Meaning |
|--------|---------|
| `✓` covered | Direct addressers exist, OR every refinement is covered |
| `~` partial | Some refinements covered, some are gaps |
| `✗` gap | No direct addressers and no covered refinements (or no refinements at all) |

A "leaf gap" is a need with no refinements and no addressers — the actionable kind. Parent needs can show as gaps too, but the fix is usually to address one of their refinements (or add refinements first).

## Questions the Model Answers

### Justification — why does this exist?

`why <component>` traces upward from the component through its addressing edges, then up the refinement chain to the owning component. Every component should address something. `addresses --orphans` finds components that address nothing — candidates for removal or unjustified existence.

### Coverage — is this owner doing its job?

`ownership <comp>` shows which of a component's owned needs are addressed (directly or via refinements) and which remain gaps. Coverage propagates upward through refinements: a parent need is "covered" when its refinements are covered.

### Gaps — where is the actionable work?

`addresses --gaps` shows leaf needs (no refinements) with no addressers. These are the concrete unmet problems. Parent needs that are gaps because their refinements are gaps surface here too — through the leaves where the work actually has to land.

### How does a need decompose?

`how <need>` walks down through direct addressers and refinements recursively, showing the full sub-tree with gap markers. This is the primary view for "what does it take to satisfy this need?"

### Impact — what happens if I remove this?

`why <component>` shows what it addresses. If those needs have other addressers (check with `how <need>`), removal is safe. If it's the only addresser of a leaf need, removal opens a gap.

### Foundation — can I trust what this builds on?

`dependencies --verify` checks the structural dependency chain. All ancestors must be locked before this component's evaluation is trustworthy.

## Operational Protocol

Evaluation is **holistic**, not gap-driven. For any component, ask "what does this address?" — wiring every genuinely-fitting addressing edge — rather than "what hole can this fill?"

### Evaluating a component

1. `where <component>` — get the recorded source-location path so you can read the real artifact
2. Read the actual deployed artifact (rule file, skill, tool) to ground the evaluation in reality. **Don't reason from the db description alone** — it's a summary, not the source of truth.
3. If a need's or component's description seems too thin, ambiguous, or like it's conflating multiple concerns, **surface a suggested correction to the user with the old description, the proposed change, and the reason** — do not edit it autonomously. See *Description integrity* below.
4. Ask: what needs does this component address? **All genuinely-fitting needs, not just one "primary" need.** Many components address multiple needs in different ways — wire every addressing edge that holds up under "would removing this component weaken handling of this need?"
5. If the closest existing need is broader than what the component actually addresses, the right move is usually to **refine** — propose the child need and the refinement edge to the user; after confirmation, `add-need`, `refine <child> <parent>`, and address the child. Refinements preserve the parent's broader meaning and add specificity without disturbing existing edges.
6. Propose each addressing edge to the user using *Relationship proposal format* (see below); wire `address <component> <need>` only after the user confirms each pair
7. Run `ownership <owner>` to check coverage propagation
8. If covered and the component's purpose is fully expressed by its addressing edges, `lock <component>`
9. If not covered or the picture feels incomplete, leave unlocked and return after more components are wired

### Inside-out evaluation order

Work from leaves to root. Evaluate the innermost components (those with no further dependents) first, then lock containers as their children complete. `--verify` enforces this lock order through the dependency chain.

**Verify chicken-and-egg for container components:** when a layer of leaves depends on container components (e.g., principles depend on a `design-principles` aggregator that depends on `rules` that depends on `ocd`), `--verify` will fail on the leaves because the containers can't be locked until their children are locked. This is expected. Bypass `--verify` for leaves that depend on pure container components — the dependency chain is sound by inspection. Lock containers from innermost to outermost once their children are all locked.

### Adding plugin-level refinements

Plugin refinements (see *Layered Need Specificity*) are added when a plugin has a mechanism that produces a sharper sub-concern than its parent project need — verified by the disappearance test in *Ownership vs Addressing*. Two patterns for *when* during evaluation:

1. **Bulk sketch at the project→plugin boundary.** Before evaluating a plugin's components (rules, conventions, tools, skills), sketch the obvious refinements its mechanism produces. Validate each against the disappearance test and the *Writing needs* guidance, propose to user, then `add-need` + `refine` + `own`. This makes the plugin's accountability landscape visible up front.
2. **Incremental during component evaluation.** As a component is being evaluated, if its mechanism doesn't fit any existing need at the right grain — and the rationale is doing too much bridging work to make the addressing edge sound — propose a refinement at that point. Add the refinement first, then address it.

Use both. Bulk-sketch the obvious refinements at the boundary so the structure is visible; let the rest emerge as evaluation surfaces them. Avoid trying to enumerate every conceivable refinement in advance — that produces speculative needs that pollute the gap views.

A refinement is valid only if it passes both filters:

- **Disappearance test** — remove the plugin and the refinement evaporates as a distinct concern (not just "would be addressed differently"; it would not *exist* as a concern).
- **Writing needs guidance** — the refinement description embeds the plugin-specific mechanism (which is what makes it a refinement), but otherwise follows the same standards as any other need.

A refinement that just paraphrases its parent and "happens to be done by" the plugin is not a refinement — it's the parent in disguise. The plugin should `address` the parent in that case, not `own` a fake refinement.

### Description integrity

Do not edit descriptions autonomously during evaluation. Surface a suggested correction to the user instead, with the old text, proposed change, and rationale.

Two reasons:
- **Mid-evaluation rewording can invalidate prior addressing edges** that were correct under the older meaning. The user has the broader perspective to judge whether to sharpen, hold the broader meaning, split into multiple entities, or leave it alone.
- **An agent focused on the current wiring will tend to over-sharpen** toward that one relationship, narrowing a deliberately-broad parent into something it wasn't meant to be. The right move when a component's concern is sharper than the parent need is `refine` (add a child), not `set-need` (rewrite the parent).

### Writing needs

Need descriptions are the entity (see *Identifiers*) — they must carry the full meaning without relying on a name. The following guidance applies to all needs, with the first rule splitting by level.

**Stay ungrounded at the project level.** Project-owned needs name concerns broadly — no domain lists, no example failure modes, no embedded mechanisms. Grounding goes in refinements that exist *because* a specific domain or mechanism matters; the parent stays broad enough to admit any future refinement that fits. Refinements relax this because their job is to sharpen toward a specific angle.

**Mechanisms and consequences out, constitutive parts in.** A description names the concern itself. Phrases that name *one of several* ways to address the concern (mechanism) or *one of several* outcomes of failing it (consequence) get stripped — they pick a single instance from a broader picture and quietly narrow the need. Phrases that are *constitutive* — the asymmetry, framing, or definition that makes the concern exist as itself — get kept. Test: "if I removed this phrase, would the concern still exist as itself?" Yes → mechanism or consequence, drop. No → constitutive, keep.

**Common red flag: "so X" / "to X" tails.** A trailing clause that names a specific outcome of addressing the concern is almost always picking one consequence among many. If the concern has multiple downstream effects, the description should name none of them and let each addresser describe in its rationale the specific consequences its mechanism targets.

**Third person.** "Reduce X", "Prevent Y", "Allow Z" — never "Allow me", "I may not see". First person sneaks in when the writer is talking to themselves; the description should read the same way to anyone.

**Test against neighbors by mechanism, not name.** When two needs sound overlapping by their names, check the mechanisms. If each names a different mechanism for the same harm, they are distinct (interpersonal alignment and epistemic verification both reduce wrong-action waste, but through different remedies and at different phases). If the mechanisms collapse to one, merge the needs or refine one out of the other.

**Cut verbose phrasing.** Every word earns its place. Long "rather than" tails that re-explain the goal can usually be deleted; "from within any X" can usually become "across X". If a phrase doesn't change the meaning when removed, remove it.

### Writing rationales

A rationale is the reasoning for one edge — the mechanism by which this component addresses this need (or why this child refines this parent, etc.). Rationales describe their relationship in isolation; cross-edge comparison is a reading-time operation, not a writing-time one.

- **No contrast.** Don't write "different mechanism from cX" or "pairs with cY" or "distinct from cZ's angle." When the reader wants to compare edges that share an endpoint, they read all the relevant rationales together. If you need contrast to make your mechanism description clear, the description isn't precise enough — sharpen it instead.
- **Mechanism, not restatement.** Don't say "c8 addresses n3 because n3 is about avoiding reinvention." That just paraphrases the edge's existence. Say *how* the component addresses the need — what action, structure, or discipline it contributes that handles the need.
- **Avoid comparative locators.** "Producer-side / consumer-side", "upstream / downstream", "structural / behavioral" all imply a contrast partner. They're fine if the partner doesn't need to be named to understand them, but prefer concrete mechanism descriptions when possible ("operates at build time" rather than "producer-side").
- **Stand-alone test.** Read your rationale with the rest of the database hidden. If it makes sense without knowing about any other edge, it's good. If it depends on the reader having just read another rationale, trim it.

### Relationship proposal format

Wiring is not autonomous. Every relationship proposed during evaluation — `depend`, `refine`, `own`, `address` — is presented to the user for confirmation before being wired. Reasoning from ids alone is impossible by design (see *Identifiers*); the proposal must show full descriptions so the user can evaluate the pairing on its merits without recalling what an id refers to.

**Format.** Each proposal covers one component, shown once at the top in `[id] description` form. Proposed addressing edges appear underneath in two groups:

- **Recommended** — edges to wire. Each entry lists the need in `[id] description` form followed by a one-paragraph rationale.
- **Considered and rejected** — edges deliberately not proposed. Each entry lists the need in `[id] description` form followed by the reason for rejection. Full descriptions are required, not just ids — without the description the user can't evaluate the reason against the actual need.

**Batch by component, not across components.** A single proposal covers one component. The user evaluates that component's full contribution at once and confirms or revises. Never bundle multiple components into a single proposal — it forces the user to context-switch between unrelated decisions and obscures which rationale belongs to which pair.

**No name-style headings on proposals.** A proposal block contains only `[id] description` pairs, never a separate name, label, or summary heading for the component being evaluated. Headings like "## c6 — Epistemic Humility" reintroduce the named-object failure mode that the no-name design (see *Identifiers*) exists to prevent — the eye lands on the label and skips the description, and the rationale gets evaluated against a mental shorthand instead of the actual statement.

After the user confirms a component's proposal, wire its edges and re-run `ownership <owner>` to show the coverage update before moving to the next component.

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

### Single-ownership guidance

Each need has exactly one owner — enforced at the schema level. If two components both seem to own the same need, that's a signal to **refine**: create a child need that captures the second component's specific concern and let it own the refinement, leaving the original ownership intact.

### Operational notes

- The four graphs are independent: a component can depend on one thing, own a different need, address yet another, and that need can refine still another. Don't assume they align.
- **Multi-edge addressing is valid and expected.** A component can address several needs when each edge holds up on its own — don't artificially narrow to a single "primary" need.
- **Don't reject an edge because another component already addresses the same need.** `addresses` is many-to-many. Two components can address the same need through different mechanisms — producer-side vs consumer-side, structural vs behavioral, upstream vs downstream. Each mechanism is its own contribution. Test the candidate edge on its own merits, not on whether someone else has "taken" that need. Rejection rationales like "X already owns this" or "X is the better vehicle" should trigger a check: is the candidate's mechanism actually the same as X's, or just aimed at the same need from a different angle?
- **Read the source, not the summary.** The db description is a one-line gist. Use `where <component>` to find the real artifact and read it before evaluating.
- Don't populate intermediate needs speculatively — only add refinements when the evaluation actually needs them to make addressing clearer.
- When adding a new need or component, propose its initial edges in the same step so floating entities don't pollute the gap/orphan views.

### Tree display conventions

- `◈` — components
- `◇` — needs
- `?` prefix — unlocked, under evaluation
- No prefix — locked, confirmed
- Tree characters (`├──`, `└──`, `│`) show descent
