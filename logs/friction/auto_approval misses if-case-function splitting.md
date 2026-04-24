---
tags: ["system:auto_approval"]
---

# auto_approval misses if-case-function splitting

## Purpose

`split_compound_command` tracks `for`/`while`/`until` ↔ `done` nesting depth so loops are preserved as single blocks when mixed with sibling statements. Nested loops unfold via recursion.

Not handled: `if ... fi`, `case ... esac`, `() { ... }` function definitions, `{ ... }` command groups. If a loop body or top-level command contains these, the split falls through to naive `;` splitting and produces fragments that won't match allow patterns. The agent gets prompted to approve the original command.

Out of scope for the initial loop fix. Log so if the user notices recurring prompts on conditional shell code, the fix path is clear: extend the depth-tracking in `split_compound_command` to include these constructs (same pattern — keywords at command-start position open/close depth).

## 2026-04-24 — assignment-from-command-substitution breaks the AST parser

Observed shape — `SIBLING=$(ocd-run sandbox sibling-path pdf); echo "path: $SIBLING"; git -C /home/dev/projects/claude-plugins rev-parse --abbrev-ref HEAD; test -e "$SIBLING" && echo "EXISTS" || echo "clear"` prompts with `Unhandled node type: string` rather than auto-approving. Individually, every one of those commands matches the allowlist (`ocd-run`, `git`, `test`, `echo`). The failure is in the AST parse step, not allowlist matching — the parser hits `VAR=$(cmd)` + chained siblings and returns a node class the splitter doesn't have a case for.

Distinct failure mode from the `if/case/function` depth gap above — that one silently fragments and mis-matches; this one surfaces a parser error and falls through to manual prompt.

### Fix approach — pre-parse normalization pass

Before handing the command to the AST splitter, run a lightweight string-level normalizer that replaces syntactic constructs the parser doesn't handle with equivalent placeholders the parser can digest. The normalizer preserves enough structure that the downstream allowlist check still sees all the real commands.

- **`VAR=$(inner)` assignment** — replace with a placeholder assignment (`VAR=_PLACEHOLDER_`) **and** emit the `inner` command as a separate segment for classification. Net effect: classifier sees the inner command's actual name to match against the allowlist; the outer chain parses cleanly.
- **Similarly for `VAR=\`inner\`` backtick substitution** — same transformation as `$(…)`.
- **`VAR=literal`** — assignment with a non-substituted value is already safe; leave untouched.

Safety: **do not execute the inner command at classification time.** Record it as a sibling segment to be classified by the existing allowlist; if the inner command isn't allowed, the whole compound gets prompted (correct behavior).

Out-of-scope for this friction log, but candidate follow-ups for the same normalization layer:

- Inline `$(…)` inside arguments (not just in assignments) — same lift-out-and-classify treatment
- Process substitution `<(…)` / `>(…)` — similar pattern, lift the inner
- Pipe targets `cmd1 | cmd2` — ensure both cmd1 and cmd2 are classified, not just the first
- Redirection targets that are themselves commands (`> $(…)`) — rare but matches the same shape

Alternative rejected: resolving `$(…)` by running the inner command at classification time. That would side-effect the classifier (runs real commands before the user approved them) — violates the auto-approval contract and introduces a trust-of-classifier problem.
