# Promote goal-first alignment to design principle

When the user signals design intent (e.g. "let's save this idea," "let's start designing X"), settle the goal/purpose statement first as a distinct, explicit step before introducing any "how" content. Iterate on the purpose alone until confirmed.

This pattern repeats across design sessions and reduces context churn — getting on the same page at the highest level first prevents walking back assumptions that contaminate later detail. Worth elevating from per-session practice to an explicit design principle in `.claude/rules/ocd/design-principles.md`.

The principle would sit alongside existing principles like *Confirm Shared Intent*. Where Confirm Shared Intent fires throughout work (before spawning agents, before deviating from plans), goal-first fires specifically at the design-conversation entry point.

**Validated this session:** the user explicitly said "Let's save this idea. Let's start with clearly defining the goal... Then we can clarify it before adding anything that would help answer 'how'." The four iterations on the agent-workspace purpose statement before any "how" content was discussed converged faster than mixing the two would have.

**Sketch of principle wording** (for principle author to refine):

> When the user signals design intent, settle the goal/purpose statement first — as a distinct, explicit step — before introducing any "how" content. Iterate on the purpose alone until the user confirms it's accurate. Mixing goal and implementation in the same conversation either locks in premature implementation choices or leaves the goal unsettled, both of which cause rework.

**How to apply:** draft a concise purpose statement (per the Purpose Statement principle — scope + role, no internal mechanics). Surface assumptions baked in. Ask narrow clarifying questions only where the answer materially shapes the goal. Iterate to settled. Only then move to "how."
