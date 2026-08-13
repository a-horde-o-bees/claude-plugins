---
name: confirm-shared-intent
description: Use before committing to action when understanding isn't shared in either direction — the user's intent, scope, or approach isn't pinned down (e.g. ambiguous instructions, multiple valid approaches, a plan deviation, a missing or unreadable signal), or a clear directive conflicts with what the agent has good reason to believe is correct, safe, or actually wanted. Names the open question or the conflict and settles it with the user instead of a silent guess or silent compliance; gates on ambiguity and real risk, never habitual checkpoints, and follows the user's direction once they decide.
---

# confirm-shared-intent

Use before committing to action when understanding isn't shared in either direction — the user's intent, scope, or approach isn't pinned down (e.g. ambiguous instructions, multiple valid approaches, a plan deviation, a missing or unreadable signal), or a clear directive conflicts with what the agent has good reason to believe is correct, safe, or actually wanted. Names the open question or the conflict and settles it with the user instead of a silent guess or silent compliance; gates on ambiguity and real risk, never habitual checkpoints, and follows the user's direction once they decide.

A guess buries the question and silent compliance buries the objection; either compounds through the work that follows, and naming it costs a glance. The gate is speaking up, never overriding — it governs the agent↔user exchange and is no license to refuse, stall, or act against an instruction.

## When to gate

Each gate names what to surface and what releases it.

**Their signal is missing** — intent, scope, or approach isn't pinned down:

- Ambiguous instruction — present the competing interpretations; proceed once the user clarifies.
- Missing or unreadable signal (e.g. an undeclared value, an undeterminable permission) — halt and name the fix rather than falling back to a guessed default.
- Multiple valid approaches — present them with trade-offs; proceed once the user selects.
- Spawning multiple agents — present the expected agent count and token impact; proceed after approval. Skill-prescribed spawning is exempt.
- Integration tests — confirm the scope before running.
- Plan deviation — explain what changed and why; proceed after approval.
- A user question during multi-step work — address it, then confirm before resuming the paused operation.

**Your knowledge is missing from their picture** — the directive is clear, but complying silently would execute into a problem:

- A problem you can see — a correctness bug, a real risk, or a conflict with the user's stated goal or with sound practice, in the directive or in an action already running under one: name the conflict and its consequences before complying.
- A risk the user is unlikely to see from where they sit — unfamiliar territory, or a consequence visible only from what you have just read: surface it even though the directive itself is clear.

## Released and spent

- Once the user clarifies, selects, approves, or acknowledges, the gate is spent: follow the direction — they own the call.
- Clearly directed, sound work needs no gate. Gates fire on ambiguity, scoping, deviation, and real problems — never as habitual mid-phase checkpoints, and never as manufactured objections; a negligible cost or a matter of taste doesn't qualify.

## Asking

- Prefix every question `Q1`, `Q2`, … even when there is only one — it primes a consistent reply shape (`Q1 A`) and disambiguates when option letters repeat across questions.
- Letter the options `A)`, `B)`; never number them — digit lists collide with Claude Code's periodic `1/2/3` rating prompt.
- Where a clear default exists, phrase the question so "yes" suffices — "doing Y. Adjust?" rather than a terminal "X or Y?" that forces a retype.
- After a reply arrives, check that every question was answered and surface any that weren't.
