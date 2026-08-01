# DECISIONS

Why context-mechanics is a user-invoked reference rather than an agent-loadable discipline.

## Model invocation is disabled — construction knowledge, not runtime discipline

**Decision.** `disable-model-invocation: true`, and no skill body references this skill invocably: context-mechanics is never loaded into an authoring pass — not by dispatch, not as a flatten side-effect — and is invoked only by the user. The deliberate, recorded exception to the suite's unused-frontmatter-fields rule.

**Forces.** The file is the evidence base behind the authoring disciplines, not a discipline itself. Every rule it grounds is already self-contained in the skill that carries it, so loading it during an invocation adds the whole citation base to working context — and to every flattened fan-out payload — without adding an applicable rule.

**Rejected.**

- *Model-invocable, with slashed references from the governed skills*: invites consultative loads mid-authoring and inlines the whole file into every flattened payload.
- *Unslashed mentions in the governed skills*: keeps the invitation one edit from returning; the governance relationship is recorded here instead, where it is owned.
- *Deleting the skill*: the grounding is real and re-consulted when triggers misfire; it loses its dispatch surface, not its home.
