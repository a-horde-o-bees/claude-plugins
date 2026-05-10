---
log-role: reference
---

# YAGNI Revocation

Decision to remove the YAGNI rule from this project's always-on rules layer (template + deployed copy both deleted). YAGNI conflicts with the user's forward-thinking development style; rules that aren't personally used aren't maintained or proofed, so they shouldn't sit in the always-on context.

## Context

The yagni rule was part of the always-on rules layer at `.claude/rules/ocd/yagni.md` (deployed) and `plugins/ocd/systems/rules/templates/yagni.md` (source template). Body content: "Solve the problem in front of you, not hypothetical future problems. Do not build features, abstractions, or infrastructure for requirements that do not exist yet."

YAGNI is a widely-cited software design principle, but it surfaced as friction during the architecture-refactor design conversation. Two specific moments:

- **Plugin granularity decision** — the user chose the thematic-split-from-start option (B) over the YAGNI-aligned two-bucket-start option, explicitly revoking YAGNI as part of that choice. Reasoning: forward-thinking design enables migration paths that the YAGNI-conservative approach forecloses.
- **Maintenance reality** — the user identified that rules they don't personally apply don't get maintained or proofed. A rule that lives in always-on context but isn't actively shaping decisions is dead weight that ages out of relevance silently.

## Options Considered

**Keep YAGNI; treat the architecture-refactor design as an exception.** Rejected: friction was specific, not exceptional. The conflict surfaces every time a forward-thinking design decision is on the table; treating it as exception means re-litigating the rule on each occurrence.

**Mark YAGNI as project-scoped (don't promote to user-level guidance) but keep in this project.** Rejected: still puts the rule in always-on context for this project, where it conflicts with the user's design style.

**Remove YAGNI from this project entirely; keep available for other users.** Considered briefly. Rejected: rules we don't personally use don't get maintained — the template would silently rot. Better to remove cleanly.

**Remove YAGNI entirely (template + deployed).** Adopted.

## Decision

Both the template (`plugins/ocd/systems/rules/templates/yagni.md`) and the deployed copy (`.claude/rules/ocd/yagni.md`) are deleted. The yagni rule is no longer part of the rules-system catalog.

This is consistent with the broader principle from the user: rules are the always-on layer for disciplines that genuinely fire on every utterance. YAGNI as a discipline doesn't fit — it fires on design decisions, which are reached-for moments (the agent recognizes "I'm about to add an extension point" and considers whether to do so). If YAGNI-style guidance is wanted at design moments, it belongs in a skill (reach-for), not a rule (always-on).

## Consequences

- **Enables:** forward-thinking design decisions proceed without re-litigating YAGNI; rules-layer carries only disciplines the project actively uses; deletes content that wouldn't be maintained
- **Constrains:** loss of an explicit "don't over-build" guard at design moments. Mitigated by other always-on disciplines (`borrow-before-build`, `economy-of-expression`, `principle-not-symptom`) that overlap on related concerns; if a design-moment guard is wanted, it can be re-introduced as a skill
- **Audit signal:** review other rules through the same lens. Any rule that doesn't fire continuously, or that the user doesn't actively apply, is a candidate for removal or conversion to a skill. The audit happens organically as rules get reviewed during the broader architecture refactor
