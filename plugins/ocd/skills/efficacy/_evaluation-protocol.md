# Evaluation Protocol

Steps and constraints for evaluating agents. Includes recursion constraint — evaluating agents must not execute changes or spawn further agents.

Do NOT execute any changes. Do NOT spawn sub-agents or use Task tool. When task instructions reference spawning agents, describe what agents you would spawn, what prompts you would give them, and what you would expect back — but do not actually invoke them.

1. Read target content provided by orchestrator
2. Trace — reason through execution, write each step as process flow using numbered steps for sequence, indented bullets for conditionals (If X: action), and `async` prefix for parallel work; include citations inline as `(section:step)` or `(line N)` for target content, `(file:line)` for additional files read from disk; do not write verbose prose — process flow IS step-by-step walkthrough; maintain consistent depth across all phases
3. List each file you read and why, in order
4. Overall assessment — could you complete this task confidently with available documentation?
5. Issues found — for each issue, describe:
  1. What issue is — complete thought, not category label
  2. Where it occurs — file, section, line, or step reference
  3. Recommended action to fix

Look for: assumptions, inferences, gaps, waste, automation opportunities, simplification, redundancy, overengineering, and artifacts. These are examples, not exhaustive — report any issue regardless of category.
