# Evaluation State

For the data model, CLI, and operational protocol, see `CLAUDE.md` in this folder. This file holds only what's needed to resume the evaluation pass from where it was last left.

## Status

Layer 1 (design principles) and partial Layer 4 (workflow + friction rules, with sub-components for the workflow children) are complete: 22 design principles wired and validated, plus c30/c31 with their children (c36-c41) wired and validated. All 19 project needs are validated and covered (100%). `c5` design-principles aggregator is validated; `c3` ocd and `c4` rules will be validated once their identity (role and scope) is settled — see *Validation criteria* in `CLAUDE.md`.

Use `summary` and `dependencies` for live counts and structure.

## Scope and Boundaries

This evaluation is in service of cutting a stable v1 of the ocd plugin and making `claude-plugins` publicly consumable. Scope is intentionally bounded so v1 can ship.

**In scope (must reach validation before v1):**

- 22 design principles (Layer 1, complete)
- ocd rule files: workflow + children, friction (complete); process-flow-notation, system-documentation, navigator (pending)
- ocd conventions
- ocd tools: navigator MCP server, navigator CLI, hooks
- ocd skills: init, status, navigator, evaluate-skill, evaluate-governance, evaluate-documentation, commit, push, pdf

**Deferred to post-v1 (continue on `dev` branch after v1 is cut):**

- `c24` blueprint plugin and its entire component tree (MCP server, skills, supporting infrastructure)
- `c25` adhd plugin — placeholder in db, no `plugins/adhd/` directory on disk yet; nothing to evaluate until the plugin actually exists

**Not yet evaluated:**

Any component outside the in-scope list above has not been examined through purpose-map. Absence of address edges for these components is not a claim that they don't address needs — only that they have not yet been examined. Per the Epistemic Humility design principle: claims are bounded by evidence; what hasn't been observed is "not yet found," not "not present." Future readers and future-Aaron should treat any unevaluated component as carrying no purpose-map verdict, positive or negative.

## Worklist

Layers to evaluate, foundations-up. Process each per the protocol in `CLAUDE.md`. Validation status and component existence are tracked in the db, not here — these bullets are starting-point inventories. Remove a layer from this list once every item in it is added, evaluated, and validated.

### Layer 2 — OCD container chain

`c5` design-principles is validated. `c4` rules and `c3` ocd remain unvalidated — validate when their role and scope are settled per *Validation criteria* in `CLAUDE.md`.

### Layer 3 — OCD rules

Already added and partially evaluated: workflow (c30 + c36-c41), friction (c31). Pending: process-flow-notation (c32), system-documentation (c33), navigator (c34).

### Layer 4 — OCD conventions

Enumerate from `plugins/ocd/conventions/`, add to db, then evaluate.

### Layer 5 — OCD tools

Add to db then evaluate: navigator MCP server, navigator CLI, navigator hooks.

### Layer 6 — OCD skills

Add to db then evaluate: init, status, navigator, evaluate-skill, evaluate-governance, evaluate-documentation, commit, push, pdf.

### Deferred (post-v1, dev branch)

- `c24` blueprint and entire subtree
- `c25` adhd (no plugin directory yet)

## Key Files

- `purpose-map/CLAUDE.md` — model documentation, CLI reference, and operational protocol
- `purpose-map/purpose_map.py` — implementation
- `purpose-map/purpose-map.db` — live database
- `plugins/ocd/rules/ocd-design-principles.md` — authoritative text for the design principles
- `plugins/ocd/rules/*.md` — OCD rule files
- `plugins/ocd/conventions/*.md` — OCD conventions
