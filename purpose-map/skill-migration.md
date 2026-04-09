# Skill Migration

Planning document for migrating the purpose-map evaluation workflow from agent-driven (following the protocol in `CLAUDE.md` manually) to skill-driven (a skill that automates the protocol).

## Why

The protocol in `CLAUDE.md` is the *what to do*. As we've evolved it through use, it's become substantial: read source, propose descriptions, scan for duplication, present proposals in a specific format, wire confirmed edges, validate when identity is settled, update state.md as layers complete. Following it manually each session means re-loading the procedure into context every time. A skill encodes the procedure once, surfaces it where the agent reaches for it, and replaces derivation with execution — c14 (Pit of Success) applied to the evaluation workflow itself.

## What the skill does

For each component being evaluated:

1. Read `state.md` to know the current target (which layer, which component)
2. Run `where <component>` to get the source-location path
3. Read the artifact with the `Read` tool
4. If the description seems too thin or ambiguous, propose a correction to the user before proceeding (per *Description integrity*)
5. Identify candidate addressing edges
6. For each candidate, run `how <need-id>` for the duplication scan
7. Present the proposal in *Relationship proposal format* (id+description, *Recommended* group, *Considered and rejected* group, *Duplication scan* section)
8. Wait for user confirmation per edge
9. Wire confirmed edges with `address <component> <need> "<rationale>"`
10. Run `summary` to show coverage update
11. If component identity is settled, run `validate <component>`
12. Update `state.md` when a layer's items are all evaluated and validated (remove the layer per the worklist guidance)

## Key considerations for the skill author

- **Not autonomous.** The protocol has substantial alignment moments — proposal verification, description integrity, duplication scan review. The skill must be deliberate about pausing for user input vs proceeding. Wiring is never silent.
- **`state.md` is the worklist input.** The skill can take `--target <layer>` or `--target <component-id>` to know what to evaluate, defaulting to the next pending layer in `state.md`.
- **Duplication scan via `how <need-id>`.** This is the workhorse query — runs before each addressing proposal to surface existing addressers and their rationales for the user to compare against the proposed mechanism.
- **Validation timing.** Validate when identity is settled (purpose clear, distinct from others), not when addressing is complete. Coverage and validation are independent per *Validation criteria*.
- **Format compliance.** The skill produces output in the *Relationship proposal format*: `[id] description` only (no name-style headings), *Recommended* group, *Considered and rejected* group, *Duplication scan* section.
- **Source of truth is `CLAUDE.md`.** The skill follows the protocol; it does not duplicate it. As the protocol evolves, the skill adapts automatically by reading from `CLAUDE.md`.
- **Rationale is where mechanism lives.** Per the simplified model, needs are mechanism-free business concerns; the addressing edge rationale is where component-specific implementation gets named.

## Open questions

- **Where does the skill live?** Probably in OCD plugin (`plugins/ocd/skills/evaluate-purpose/SKILL.md`) — purpose-map evaluation is part of OCD's discipline of structural alignment.
- **Naming.** Per object_action convention, candidates: `evaluate-purpose`, `purpose-evaluate`, `evaluate-component`. Fit with OCD's existing skill naming pattern.
- **Single skill or split?** One skill for the full evaluation loop, or split into smaller skills (`propose-edges`, `validate-component`, `next-target`)? Single skill is probably right — the workflow is one coherent loop driven by user confirmation at each step.
- **What about Layer 3+ components that don't yet exist in the db?** The skill should handle "add components for this layer first, then evaluate" as the entry path for new layers.

## What this file is

A planning document, not a design spec. Captures insights from the session where we evolved the protocol so they don't get lost between sessions. When we're ready to build the skill, this file is the starting point. Update it as the skill takes shape; remove it once the skill is built and these considerations are encoded in the skill itself.
