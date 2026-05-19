---
name: agent-first-interfaces
description:
---

# Agent-First Interfaces

The primary consumer of every tool, output, and error message is an agent. Design for machine consumption: complete context in the interface itself, structured output for parsing, corrective errors for self-correction, and workflow hints for sequencing. An agent encountering any interface for the first time should use it correctly from the interface alone — no external documentation, no trial and error, no user assistance.

- Help text answers — when to call, what output looks like, how to interpret results, what to call next, when to stop
- Error messages include corrective guidance, not just failure description
- Output is structured and consistent — predictable markers, no decorative formatting
- Tool descriptions state their purpose in terms an agent can match to a task
- Instructions reference files by path, not by name — an agent should never need to search for a file
- References to skills use the form by which the skill is invoked in its current install context — bare `/<skill>` for npx-direct installs (skill at `~/.claude/skills/<name>/` or `<project>/.claude/skills/<name>/`), `/<plugin>:<skill>` for plugin-bundled installs. Match the project's delivery model when authoring references in skill bodies or agent-emitted content; do not re-qualify a bare reference with a plugin prefix based on training defaults. The CLI router handles user-typed input either way
- Instructions handed to agents are position-independent — the reader executes from the instructions alone without needing to know whether it is the top-level agent, a spawned subagent, or four levels deep in a delegation chain; terms like "orchestrator" or "caller" force the reader to infer its role rather than just act
