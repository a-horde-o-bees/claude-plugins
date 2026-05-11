---
tagline: Minimize agent count for ad-hoc work; follow skill-prescribed counts as-is
---

# Agent Spawning

Each spawned subagent independently loads context and rediscovers the project, multiplying token cost. Default to a single agent processing tasks sequentially within one context. Skill-prescribed agent spawning has already weighed the cost at design time — follow the prescription without second-guessing the count.

- Before spawning multiple agents for ad-hoc work: prefer a single agent processing tasks sequentially; reach for parallel agents only when their work is genuinely independent and the context isolation is worth the per-agent context-load cost
- When a skill prescribes a specific agent shape (count, parallelism, isolation): follow it; the skill author already evaluated the trade-off
- Before delegating bulk work to a subagent to escape context: ask whether a script or direct tool call would do the same job for zero agent tokens
