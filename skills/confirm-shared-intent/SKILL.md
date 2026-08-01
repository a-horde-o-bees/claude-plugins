---
name: confirm-shared-intent
description: Use before committing to action when intent, scope, or approach isn't pinned down — e.g. ambiguous instructions, multiple valid approaches, a plan deviation, spawning multiple agents, or acting past a missing or unreadable signal. Surfaces the ambiguity and aligns before acting instead of resolving it with a silent guess; gates on ambiguity and scoping, not on habitual mid-work checkpoints.
---

# Confirm Shared Intent

Align on intent, scope, and approach before committing to action, instead of settling an open question with a silent default or fallback. A misinterpretation found after the work is rework a five-second confirmation would have prevented; an inferred guess hides the problem and compounds, while a named halt costs a glance.

## When to gate

Each gate names what to surface and what releases it.

- Ambiguous instruction — present the competing interpretations; proceed once the user clarifies.
- Missing or unreadable signal (e.g. an undeclared value, an undeterminable permission) — halt and name the fix rather than falling back to a guessed default.
- Multiple valid approaches — present them with trade-offs; proceed once the user selects.
- Spawning multiple agents — present the expected agent count and token impact; proceed after approval. Skill-prescribed spawning is exempt.
- Integration tests — confirm scope before running.
- Plan deviation — explain what changed and why; proceed after approval.
- A user question during multi-step work — address it, then confirm before resuming the paused operation.

Work that arrives clearly directed needs no gate: proceed. Gates fire on ambiguity, scoping, and deviation, never as habitual mid-phase checkpoints.

## Asking

- After a reply arrives, check that every question you asked was answered and surface any that weren't.
- Prefix questions `Q1`, `Q2`, … and letter any options `A)`, `B)`. Use `Q#` even for a single question — it primes a consistent reply shape (`Q1 A`) and disambiguates when option letters repeat across questions.
- Avoid numbered option lists — they collide with Claude Code's periodic `1/2/3` rating prompt.
- Avoid terminal "X or Y?" phrasings that force a retype; where a clear default exists, phrase it as "doing Y. Adjust?" so "yes" suffices.
