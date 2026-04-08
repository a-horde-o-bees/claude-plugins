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

Two independent graphs over the entity types. Each answers a different question.

**depends_on** (component → component) — Structural DAG. "This component needs that component to exist." If the dependency were removed, the dependent would need to be re-engineered or would cease to exist. Multiple dependencies per component allowed.

- Rules depend on a plugin for deployment
- Plugins depend on the marketplace for delivery
- Answers: **what must exist for this to work?**

**addresses** (component → need) — Capability claim, with rationale. A claim that this component contributes to addressing a need. Partial contribution is fine — many components can address the same need, each through a different mechanism described in its rationale. The rationale is where component-specific implementation lives.

- A design principle addresses a project concern broadly
- A rule addresses the same concern with a specific encoded mechanism
- Both edges are valid; the rationales describe what each contributes
- Answers: **how is this need being handled?**

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
needs            (id, description, validated)
depends_on       (component_id → dependency_id)
addresses        (component_id → need_id, rationale) -- many-to-many
component_paths  (component_id → path)               -- source-location pointers
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
| `addresses [id] [--gaps] [--orphans]` | Addressing graph for a need or component; `--gaps` lists needs with no addressers; `--orphans` lists components addressing nothing |
| `where <component>` | Recorded source-location paths for a component; the bridge from a db entry to the real artifact |
| `why <component>` | What needs does this component address (with rationales) |
| `how <need>` | What addresses this need (with rationales) |
| `compare <component-a> <component-b>` | Side-by-side addressing comparison: common needs (both address, with each rationale shown) and each-only needs. Used to evaluate whether two components are doing overlapping work through the same or different mechanisms |
| `summary` | Counts and per-need addressing status |

### Coverage status legend

| Marker | Meaning |
|--------|---------|
| `✓` covered | At least one direct addresser |
| `✗` gap | No direct addressers — actionable concern |

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

Evaluation is **holistic**, not gap-driven. For any component, ask "what does this address?" — wiring every genuinely-fitting addressing edge — rather than "what hole can this fill?"

### Evaluating a component

1. `where <component>` — get the recorded source-location path so you can read the real artifact
2. Read the actual deployed artifact (rule file, skill, tool) with the `Read` tool to ground the evaluation in reality. **Don't reason from the db description alone** — it's a summary, not the source of truth.
3. If a need's or component's description seems too thin, ambiguous, or like it's conflating multiple concerns, **surface a suggested correction to the user with the old description, the proposed change, and the reason** — do not edit it autonomously. After the user confirms, run `set-need <id> "..."` or `set-component <id> "..."`. See *Description integrity* below.
4. Identify candidate addressing edges: what needs does this component address? **All genuinely-fitting needs, not just one "primary" need.** For each candidate, run `how <need-id>` to see existing addressers and their rationales — this surfaces overlap that should be noted in the proposal (see *Surface duplication, don't suppress it* below).
5. Propose each addressing edge to the user using *Relationship proposal format* (see below), including the neighborhood scan from step 4. Wire confirmed edges with `address <component> <need> "<rationale>"` only after the user confirms each pair. The rationale is where component-specific mechanism lives — describe *how* this component addresses the need, not *what* the need is.
6. Run `summary` to check coverage status and gaps.
7. Run `validate <component>` once its identity is confirmed — distinct contribution to the model, clear purpose, not subsumed by another component. Coverage of its addressing edges does not need to be complete; new edges can be wired later as consumers are evaluated. See *Validation criteria*.
8. Leave unvalidated when the component's identity is still under question — uncertain whether it belongs, might overlap with another, might need to be split or rephrased. (Use `invalidate <id>` to revert a previous validation.)

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

### Writing needs

Need descriptions are the entity (see *Identifiers*) — they must carry the full meaning without relying on a name.

**Business concerns, not technical requirements.** Need descriptions name the concern broadly — what we want to accomplish, not how to accomplish it. Decomposing a business concern into a technical requirement (e.g., "address this concern *via X mechanism*") prematurely binds the concern to one implementation, removing flexibility for refactoring. The whole point of an AI-led system is that the agent picks the mechanism; the model shouldn't pre-bind it. If a description names a specific mechanism, encoding strategy, file format, or tool, it has slipped from concern into requirement — strip the technical specifics and keep the business intent.

**Mechanisms and consequences out, constitutive parts in.** A description names the concern itself. Phrases that name *one of several* ways to address the concern (mechanism) or *one of several* outcomes of failing it (consequence) get stripped — they pick a single instance from a broader picture and quietly narrow the need. Phrases that are *constitutive* — the asymmetry, framing, or definition that makes the concern exist as itself — get kept. Test: "if I removed this phrase, would the concern still exist as itself?" Yes → mechanism or consequence, drop. No → constitutive, keep.

**Common red flag: "so X" / "to X" tails.** A trailing clause that names a specific outcome of addressing the concern is almost always picking one consequence among many. If the concern has multiple downstream effects, the description should name none of them and let each addresser describe in its rationale the specific consequences its mechanism targets.

**Third person.** "Reduce X", "Prevent Y", "Allow Z" — never "Allow me", "I may not see". First person sneaks in when the writer is talking to themselves; the description should read the same way to anyone.

**Decompose by splitting, not by parent/child.** When a concern feels too broad and benefits from being split into more specific concerns, create new sibling needs at the same level rather than introducing a parent/child relationship. Sibling needs are independently addressable and the relationship between related concerns lives in their descriptions, not in a structural link.

**Test against neighbors by mechanism, not name.** When two needs sound overlapping by their names, check the mechanisms. If each names a different concern with a different remedy, they are distinct. If the concerns collapse into one, merge them.

**Cut verbose phrasing.** Every word earns its place. Long "rather than" tails that re-explain the goal can usually be deleted; "from within any X" can usually become "across X". If a phrase doesn't change the meaning when removed, remove it.

### Writing rationales

A rationale is the reasoning for one addressing edge — the specific mechanism by which this component addresses this need. Rationales are where component-specific implementation lives. They describe their relationship in isolation; cross-edge comparison is a reading-time operation, not a writing-time one.

Because needs are intentionally mechanism-free (see *Writing needs*), the rationale carries the full description of *how* this component contributes. This is the right place for "encoded as a rule", "blocked at runtime by a hook", "captured into a friction queue", "verified by reading the file" — anything that names a specific implementation choice.

- **Mechanism, not restatement.** Don't say "c8 addresses n3 because n3 is about avoiding reinvention." That just paraphrases the edge's existence. Say *how* the component addresses the need — what action, structure, or discipline it contributes that handles the need.
- **No contrast.** Don't write "different mechanism from cX" or "pairs with cY" or "distinct from cZ's angle." When the reader wants to compare edges that share an endpoint, they read all the relevant rationales together. If you need contrast to make your mechanism description clear, the description isn't precise enough — sharpen it instead.
- **Avoid comparative locators.** "Producer-side / consumer-side", "upstream / downstream", "structural / behavioral" all imply a contrast partner. They're fine if the partner doesn't need to be named to understand them, but prefer concrete mechanism descriptions when possible ("operates at build time" rather than "producer-side").
- **Stand-alone test.** Read your rationale with the rest of the database hidden. If it makes sense without knowing about any other edge, it's good. If it depends on the reader having just read another rationale, trim it.

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
- **Multi-edge addressing is valid and expected.** A component can address several needs when each edge holds up on its own — don't artificially narrow to a single "primary" need.
- **Don't reject an edge because another component already addresses the same need.** `addresses` is many-to-many. Two components can address the same need through different mechanisms. Each mechanism is its own contribution. Test the candidate edge on its own merits, not on whether someone else has "taken" that need. Rejection rationales like "X is the better vehicle" should trigger a check: is the candidate's mechanism actually the same as X's, or just aimed at the same need from a different angle?
- **Read the source, not the summary.** The db description is a one-line gist. Use `where <component>` to find the real artifact and read it before evaluating.
- Don't add needs speculatively — only add a need when it names a real concern that's missing from the model.
- When adding a new component, propose its initial addressing edges in the same step so floating components don't pollute the orphan view.

### Tree display conventions

- `◈` — components
- `◇` — needs
- `?` prefix — unvalidated (identity still under question)
- No prefix — validated (identity confirmed)
- Tree characters (`├──`, `└──`, `│`) show descent
