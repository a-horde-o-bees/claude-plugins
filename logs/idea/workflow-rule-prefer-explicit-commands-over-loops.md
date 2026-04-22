# workflow-rule-prefer-explicit-commands-over-loops

## Purpose

Capture a rule for the agent-workflow conventions: prefer explicit straight-line Bash commands over `for`/`while` loops and variable expansion when bundling multiple invocations of the same tool, because the `simple_expansion` permission gate cannot statically match expanded commands against allow patterns.

## Context

Claude Code's permission system evaluates bash commands against the user's allow/deny configuration. Static commands (no variables, no command substitution) can be matched character-by-character against patterns and auto-approved. Commands containing variable expansion (`$d`, `${VAR}`, `$(cmd)`, etc.) cannot be statically matched — their expanded form isn't knowable until runtime, so the gate falls back to asking the user.

This is correct behavior for security reasons (expansion is the vector for "cp $SRC $DEST" silently becoming "cp /etc/passwd remote:/"), but it interrupts flow when the agent writes convenience loops over trusted tools with hardcoded iteration lists.

## Proposed rule (for agent-workflow conventions)

- Prefer explicit straight-line commands over `for`/`while` loops, variable expansion, and command substitution when bundling multiple invocations of the same tool
- For a small, known iteration count (≤5), write each invocation explicitly, or send them as parallel Bash tool calls in a single message
- For a dynamic or large iteration count, a loop is legitimate — the interruption cost is less than the explicit-list cost
- Command substitution (`$(…)`) inside a tool invocation has the same effect as variable expansion — prefer separate calls when possible
- This rule governs agent output, not project scripts — project scripts can use whatever shell patterns make sense

## Why this matters

The friction isn't that the gate is wrong — the gate is right. The friction is that the agent default-writes loops because they're shorter, which trips a gate that wasn't meant for internal tools with hardcoded inputs. Codifying the preference pushes the agent toward the bash pattern that matches the permission system's strengths.

## Origin

Surfaced during a job-search session where PDF regeneration across multiple application folders was written as a `for d in folder1 folder2; do cmd $d; done` loop. The hardcoded folder list made the loop equivalent to two explicit calls, but the `simple_expansion` gate still fired. Rewriting as two explicit Bash calls would auto-approve.

## Next steps if pursued

- Add to `plugins/ocd/systems/rules/templates/workflow.md` (or wherever bash/command-execution conventions live)
- Cross-reference from permission-system documentation so users understand the interaction
- Consider whether this generalizes beyond `simple_expansion` to other command-level gates (allowed-tools restrictions, path-pattern allow rules, etc.)
