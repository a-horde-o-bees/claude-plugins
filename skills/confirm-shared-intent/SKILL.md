---
name: confirm-shared-intent
description: Use before committing to action when intent, scope, or approach isn't pinned down — e.g. ambiguous instructions, multiple valid approaches, a plan deviation, spawning multiple agents, or acting past a missing or unreadable signal. Names the open question and settles it with the user instead of a silent guess; gates on ambiguity and scoping, not on habitual mid-work checkpoints.
---

# confirm-shared-intent

Use before committing to action when intent, scope, or approach isn't pinned down — e.g. ambiguous instructions, multiple valid approaches, a plan deviation, spawning multiple agents, or acting past a missing or unreadable signal. Names the open question and settles it with the user instead of a silent guess; gates on ambiguity and scoping, not on habitual mid-work checkpoints.

A guess buries the question and compounds through the work that follows; naming it costs a glance.

## When to gate

Each gate names what to surface and what releases it.

- Ambiguous instruction — present the competing interpretations; proceed once the user clarifies.
- Missing or unreadable signal (e.g. an undeclared value, an undeterminable permission) — halt and name the fix rather than falling back to a guessed default.
- Multiple valid approaches — present them with trade-offs; proceed once the user selects.
- Spawning multiple agents — present the expected agent count and token impact; proceed after approval. Skill-prescribed spawning is exempt.
- Integration tests — confirm the scope before running.
- Plan deviation — explain what changed and why; proceed after approval.
- A user question during multi-step work — address it, then confirm before resuming the paused operation.

Clearly directed work needs no gate — gates fire on ambiguity, scoping, and deviation, never as habitual mid-phase checkpoints.

## Asking

- Prefix every question `Q1`, `Q2`, … even when there is only one — it primes a consistent reply shape (`Q1 A`) and disambiguates when option letters repeat across questions.
- Letter the options `A)`, `B)`; never number them — digit lists collide with Claude Code's periodic `1/2/3` rating prompt.
- Where a clear default exists, phrase the question so "yes" suffices — "doing Y. Adjust?" rather than a terminal "X or Y?" that forces a retype.
- After a reply arrives, check that every question was answered and surface any that weren't.
