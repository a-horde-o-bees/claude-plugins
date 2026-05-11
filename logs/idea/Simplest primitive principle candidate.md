# "Simplest primitive that solves the problem" — principle candidate

Candidate for a new design principle covering the discipline of choosing the smallest mechanism that satisfies the problem in front of us, plus the next obvious extension. Distinct from the YAGNI rule that was revoked in `logs/decision/yagni-revocation.md` — YAGNI was anti-future, this is anti-overengineering for the *current* scope.

## What this would cover

A repeated friction pattern in design conversations: the agent proposes a mechanism, the user pushes back toward a simpler primitive that solves the same problem with less ongoing cost. Several recent examples:

- **Hash-based cache invalidation → column-projection diff.** Proposed: per-row source-content hashes + normalizer-version stamps + auto-detected function-source-hash drift. User push: a generic `diff_rows(old, new, key_cols, compare_cols)` utility is sufficient at our scale and removes all the provenance bookkeeping. Adopted. (Captured in `monaco-lock-company--erp-migration/logs/decision/per-row-diff-vs-source-hash.md`.)
- **Calendar-projected timelines → hour estimates only.** Proposed: a milestone table with both effort hours and calendar weeks. User push: calendar projections read ominously in client-facing docs; hours alone convey the information. Removed.
- **Multi-paragraph "transparency" breakdowns → tight tables.** Proposed: prose explaining how time split between Monaco-direct work and tooling adjacent to it. User push: the breakdown surfaces information the client shouldn't be paying attention to and dilutes the signal. Removed.

In each case, the simpler primitive was the right call by the same logic: extra mechanism carries ongoing cost (more rows to maintain, more numbers to defend, more nuance for the reader to interpret), and the simpler form satisfies the current problem with room to extend later if the need actually materializes.

## Why this is distinct from YAGNI

`logs/decision/yagni-revocation.md` removed YAGNI as a project rule because YAGNI conflicts with forward-thinking design — building extension points for anticipated future work is part of the user's design style and is preserved deliberately.

The "simplest primitive" principle is different: it operates within the *current* problem's scope, not against future extensions. The hash-vs-diff example is the cleanest illustration — choosing the diff isn't refusing to think ahead, it's recognizing that hashing doesn't pay off for the current scale and the additive future case (adding hashes alongside the diff) is purely additive if scale changes. The diff is the smallest primitive that solves now and doesn't foreclose later.

Compare to YAGNI's framing: "don't build features for hypothetical futures." Compare to this principle: "choose the smallest mechanism that satisfies the current problem and the next obvious extension." YAGNI is anti-future; this is anti-overengineering.

## Shape if promoted to a principle

Working title: **Choose the simplest primitive.** Trigger: when proposing a design with multiple candidate mechanisms, prefer the smallest one that satisfies the current problem and doesn't foreclose the obvious next extension. The ongoing cost of an oversized mechanism (provenance columns, version stamps, extra dimensions in a table, calendar projections that need maintenance) is what makes it the wrong call, not the upfront authoring cost.

Worth distinguishing from related principles already documented:
- **Capture Rationale** is about preserving why-decisions-were-made; this is about which decisions to make.
- **Economy of Expression** is about wording; this is about mechanism.
- **YAGNI (revoked)** was about not building for hypothetical futures; this is about not overbuilding for the current problem.

## When to promote

If a third or fourth supporting example shows up in the next few sessions, this is probably principle-worthy. Until then, this idea log holds the candidate and its evidence so a future retrospective can decide whether the pattern is durable.
