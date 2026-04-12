---
tags: ["system:auto_approval"]
---

# auto_approval handles for/while/until loops but not if/case/function control flow

## Purpose

`split_compound_command` tracks `for`/`while`/`until` ↔ `done` nesting depth so loops are preserved as single blocks when mixed with sibling statements. Nested loops unfold via recursion.

Not handled: `if ... fi`, `case ... esac`, `() { ... }` function definitions, `{ ... }` command groups. If a loop body or top-level command contains these, the split falls through to naive `;` splitting and produces fragments that won't match allow patterns. The agent gets prompted to approve the original command.

Out of scope for the initial loop fix. Log so if the user notices recurring prompts on conditional shell code, the fix path is clear: extend the depth-tracking in `split_compound_command` to include these constructs (same pattern — keywords at command-start position open/close depth).
