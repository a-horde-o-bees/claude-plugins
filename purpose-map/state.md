# Evaluation State

For the data model, CLI, and operational protocol, see `CLAUDE.md` in this folder. This file holds only what's needed to resume the evaluation pass from where it was last left.

## Current Data State

Run `summary` to see live counts. At last save:

Ids are assigned in **depth-first order from project**, so reading them sequentially walks the structural chain. `c1` is project; `c2` is marketplace; `c3-c5` is the OCD container chain; `c6-c23` are the 18 design principles in alphabetical order by description; `c24` is blueprint; `c25` is adhd. For needs, refinements are contiguous with their parent (e.g. `n8` follow-best-practices → `n9` encode-best-practices → `n10` source-best-practices).

- 25 components (2 locked: `c1` project, `c2` marketplace)
- 17 needs (13 root-level locked + 2 unlocked refinements of `n8` follow-best-practices: `n9` encode-best-practices and `n10` source-best-practices + 2 unlocked needs from the prior context-conflation split: `n7` preserve-context-clarity and `n15` reduce-token-waste)
- 24 dependency edges forming the structural chain c1 project → c2 marketplace → {c3 ocd, c24 blueprint, c25 adhd} → c4 rules → c5 design-principles → 18 principles (c6–c23)
- 2 refinement edges: `n9` encode-best-practices and `n10` source-best-practices both refine `n8` follow-best-practices
- 17 ownership edges:
  - `c1` project owns all 15 broad concerns
  - `c3` ocd owns `n9` encode-best-practices (the encode-via-rules angle exists only because OCD does that)
  - `c24` blueprint owns `n10` source-best-practices (the source-via-research angle exists only because blueprint does that)
  - `c25` adhd owns nothing — no adhd-specific sub-concerns identified yet
- 1 addressing edge: `c2` marketplace → `n1` portable-tools

15 leaf gaps. Design principles have no addressing edges yet.

## Scope and Boundaries

This evaluation is being done in service of cutting a stable v1 of the ocd plugin and making `claude-plugins` publicly consumable. Scope is intentionally bounded so v1 can ship.

**In scope (must reach lock before v1):**

- 18 design principles (innermost layer, already in db)
- 7 ocd rule files: agent-authoring, communication, workflow, friction, process-flow-notation, system-documentation, navigator (need to be added as components)
- ocd conventions (need to be added as components)
- ocd tools: navigator MCP server, navigator CLI, hooks (need to be added as components)
- ocd skills: init, status, navigator, evaluate-skill, evaluate-governance, evaluate-documentation, commit, push, pdf (need to be added as components)

**Deferred to post-v1 (continue on `dev` branch after v1 is cut):**

- `c24` blueprint plugin and its entire component tree (MCP server, skills, supporting infrastructure)
- `c25` adhd plugin — placeholder in db, no `plugins/adhd/` directory on disk yet; nothing to evaluate until the plugin actually exists

**Not yet evaluated:**

Any component outside the in-scope list above has not been examined through purpose-map. Absence of address edges for these components is not a claim that they don't address needs — only that they have not yet been examined. Per the Epistemic Humility design principle: claims are bounded by evidence; what hasn't been observed is "not yet found," not "not present." Future readers and future-Aaron should treat any unevaluated component as carrying no purpose-map verdict, positive or negative.

## Outstanding Questions

1. **Resumability — OCD or ADHD?** Resumability structurally depends on design-principles. It currently addresses nothing. Should it address `avoid-progress-loss` directly, or should ADHD own a refinement (e.g., `recover-after-context-clear`) and resumability address that?

2. **Missing principle for active pushback?** Epistemic Humility bounds claims to evidence, but pushback is about the agent actively preventing harm. Is there a missing principle component, or is pushback a responsibility of the communication rule (implementation, not principle)?

3. **Missing principle for systematic feedback capture?** Fix Foundations addresses root causes but nothing says "notice and record problems as they happen." The friction detection rule implements this. What principle justifies it?

4. **Missing principle for mutual comprehension?** Measure Twice verifies before acting, but doesn't specifically address building shared understanding between user and agent. The communication rule's alignment triggers implement this. Is there a principle underneath?

## Worklist

Layers to evaluate, inside-out. Process each per the protocol in `CLAUDE.md`. Lock status and component existence are tracked in the db, not here — these bullets are starting-point inventories. Remove a layer from this list once every item in it is added, evaluated, and locked.

### Layer 1 — Design principles (c6–c23)

Already in db. Evaluate per the protocol.

### Layer 2 — OCD container chain

Lock `c5` design-principles, then `c4` rules, then `c3` ocd as their children complete.

### Layer 3 — Plugin refinements

Sketch OCD and blueprint plugin refinements per *Adding plugin-level refinements* in CLAUDE.md. Each refinement passes the disappearance test, refines a project need, and is owned by its plugin. Add the obvious ones upfront so plugin accountability is visible before evaluating Layer 4+ components; let further refinements emerge incrementally as those layers surface them.

### Layer 4 — OCD rules

Add to db then evaluate: communication, workflow, friction, process-flow-notation, system-documentation, navigator. (Verify whether `agent-authoring` is still applicable before adding.)

### Layer 5 — OCD conventions

Enumerate from `.claude/conventions/`, add to db, then evaluate.

### Layer 6 — OCD tools

Add to db then evaluate: navigator MCP server, navigator CLI, navigator hooks.

### Layer 7 — OCD skills

Add to db then evaluate: init, status, navigator, evaluate-skill, evaluate-governance, evaluate-documentation, commit, push, pdf.

### Deferred (post-v1, dev branch)

- `c24` blueprint and entire subtree
- `c25` adhd (no plugin directory yet)

## Key Files

- `purpose-map/CLAUDE.md` — model documentation, CLI reference, and operational protocol
- `purpose-map/purpose_map.py` — implementation
- `purpose-map/purpose-map.db` — live database
- `.claude/rules/ocd-design-principles.md` — authoritative text for the 18 principles being evaluated
- `.claude/rules/ocd-*.md` — the other OCD rule files that will be evaluated next
