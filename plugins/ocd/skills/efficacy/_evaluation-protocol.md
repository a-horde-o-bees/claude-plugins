# Evaluation Protocol

Constraints and steps for evaluating agents. Evaluating agents must not execute changes or spawn further agents.

Do NOT execute any changes. Do NOT spawn sub-agents. When task instructions reference spawning agents, describe what agents you would spawn, what prompts you would give them, and what you would expect back — but do not actually invoke them.

## Steps

1. Read target content provided by orchestrator
2. Comprehend — for each condition, guard, and constraint, articulate what it protects against and why it is structured that way; for each variable, trace its lifecycle (assignment, consumption, purpose)
3. Trace — reason through execution as process flow; numbered steps for sequence, indented bullets for conditionals, `async` prefix for parallel work; include citations inline as `(section:step)` or `(line N)` for target content, `(file:line)` for files read from disk; do not write verbose prose — process flow IS step-by-step walkthrough; maintain consistent depth across all phases
4. Verify — compare comprehension against implementation; issues are gaps between intent and behavior, not opportunities to reword working logic
5. Report findings

## Report Format

1. Files read and why, in order
2. Overall assessment — could you complete this task confidently with available documentation?
3. Issues found — classify each as Defect or Observation; for each issue:
  1. Classification — Defect or Observation
  2. What issue is — complete thought, not category label
  3. Where it occurs — file, section, line, or step reference
  4. What intent is preserved — what the current implementation protects against
  5. Recommended action — fix must preserve stated intent; if intent is unclear, flag as Observation
