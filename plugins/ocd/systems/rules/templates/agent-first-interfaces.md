---
includes: "*"
---

# Agent-First Interfaces

The primary consumer of every tool, output, and error message is an agent. Design for machine consumption: complete context in the interface itself, structured output for parsing, corrective errors for self-correction, and workflow hints for sequencing. An agent encountering any interface for the first time should be able to use it correctly from the interface alone — no external documentation, no trial and error, no user assistance.

- Help text answers — when to call, what output looks like, how to interpret results, what to call next, when to stop
- Error messages include corrective guidance, not just failure description
- Output is structured and consistent — predictable markers, no decorative formatting
- Tool descriptions state their purpose in terms an agent can match to a task
- Instructions reference files by path, not by name — an agent should never need to search for a file
- References to plugin skills use the qualified `/plugin:skill` form in every context — PFN `skill:` invocations, emitted strings, documentation, agent output, user-facing messages. Unqualified forms rely on the CLI router's namespacing fallback, which does not apply in other contexts (e.g., Skill tool, emitted strings, agent-produced docs). Qualified form is unambiguous everywhere and cannot collide across installed plugins. User-typed input at the CLI is not bound by this rule — the CLI router handles it — but anything the agent authors or emits qualifies
- Instructions handed to agents are position-independent — the reader executes from the instructions alone without needing to know whether it is the top-level agent, a spawned subagent, or four levels deep in a delegation chain; terms like "orchestrator" or "caller" in handed-down content force the reader to infer its role rather than just act
