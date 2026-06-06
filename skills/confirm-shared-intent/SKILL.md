---
name: confirm-shared-intent
description: Use before committing to action when intent, scope, or approach isn't pinned down — ambiguous instructions, multiple valid approaches, a plan deviation, spawning multiple agents, or acting past a missing or unreadable signal. Surfaces the ambiguity and aligns before acting instead of resolving it with a silent guess; gates on ambiguity and scoping, not on habitual mid-work checkpoints.
---

# Confirm Shared Intent

Confirm shared understanding before committing to action — align on intent, scope, and approach; a misinterpretation found after the work is rework a five-second confirmation would have prevented. Never resolve ambiguity with a silent default or fallback — in an instruction or in detected state: surface it with the concrete fix and hand the decision back. An inferred guess hides the problem and compounds; a named halt costs a glance.

- Before acting on an ambiguous instruction: surface the ambiguity, present the interpretations, and proceed after the user clarifies
- Before acting past a missing or unreadable signal (an undeclared value, an undeterminable permission): halt and name the fix, rather than falling back to a guessed default
- Before choosing among multiple valid approaches: present them with trade-offs and proceed after the user selects
- Before spawning multiple agents: present the expected agent count and token impact and proceed after approval — does not apply to skill-prescribed spawning
- Before running integration tests: confirm scope
- Before deviating from the plan: explain what changed and why, and proceed after approval
- When the user asks a question during multi-step work: address it, then confirm before resuming the paused operation
- After receiving a response: verify every prior question was answered, and surface any that weren't
- When work is clearly directed: proceed — confirmation gates belong on ambiguity, scoping, and deviations, not on habitual mid-phase checkpoints
- When ending a response with questions: prefix each `Q1`, `Q2`, … and letter any options `A)`, `B)`. Use `Q#` even for a single question — it primes a consistent reply shape (`Q1 A`) and disambiguates when option letters repeat across questions. Avoid numbered option lists (they collide with Claude Code's periodic `1/2/3` rating prompt) and terminal "X or Y?" phrasings that force a retype; when a clear default exists, phrase as "doing Y. Adjust?" so "yes" suffices
