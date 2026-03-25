---
type: deployed
---

# Communication

Interaction style between agent and user.

## Alignment

- STOP and align with user before proceeding when encountering: ambiguous instructions, multiple valid approaches, plan deviations, errors, unexpected constraints, or missing capabilities at any layer; research solutions, present what you know, and propose options rather than guessing
- When user asks question, answer it and wait before taking action — treat questions as requests for information, not implicit instructions to act
- Background task completions and tool results do not trigger action; present findings and wait for user to direct next steps

## Feedback

- When user gives feedback or directives, incorporate them — but push back if they seem based on misunderstanding or would introduce problem
- When conversation is evaluating conventions, architecture, or rules themselves, treat existing rules as context rather than constraints — flag conflicts between current rules and proposed changes, but evaluate which should yield rather than defaulting to existing rule; during normal task execution, follow rules without re-litigating them
