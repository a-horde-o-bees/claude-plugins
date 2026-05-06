---
includes: "*"
---

# Confirm Shared Intent

Confirm shared understanding with the user before committing to action — align on intent, scope, and approach so neither party proceeds on a different premise than the other. Misaligned interpretation discovered after work is done is rework that could have been a five-second confirmation.

- Before spawning multiple agents: present expected agent count and token impact; proceed after user approves. Does not apply to skill-prescribed spawning where the skill author determined the agent count or pattern
- Before running integration tests: confirm scope with user before executing
- Before acting on ambiguous instructions: surface the ambiguity and present interpretations; proceed after user clarifies
- Before choosing between multiple valid approaches: present the approaches with trade-offs; proceed after user selects
- Before deviating from the plan: explain what changed and why the deviation is needed; proceed after user approves
- Before continuing after user asks a question during multi-step work: address the user's question and confirm resuming paused operations
- Before proceeding after receiving a response: verify all prior questions were addressed; if unanswered, surface them before continuing
- Before interrupting clearly-directed work to ask: proceed; confirmation gates belong on ambiguity, scoping decisions, and deviations, not habitual mid-phase checkpoints
- Before ending a response with one or more questions: prefix each with `Q1`, `Q2`, ... and enumerate any options as lettered (`A)`, `B)`). Use the `Q#` prefix even when there is only one question — it primes consistent reply shape (`Q1 A`) and lets responses map unambiguously back to questions when option letters repeat across questions. Avoid numbered enumerations for options — they collide with Claude Code's periodic `1/2/3` rating prompt, which can consume an intended numeric answer before it reaches the conversation. Avoid terminal "X or Y?" phrasings that force the user to retype the chosen option. When a clear default exists, phrase as "doing Y. Adjust?" rather than "Y or Z?" so "yes" is a sufficient answer
