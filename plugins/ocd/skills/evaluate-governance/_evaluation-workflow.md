# Governance Evaluation Workflow

Agent workflow for evaluating governance files in root-first dependency order. The orchestrator may hand you the chain one level at a time or all at once; each file joins your context in the order given, and the experience of reading each file is itself the check for whether a future agent could follow it.

## Reading Disposition

You start with no prior context beyond this file. Each governance file joins your context in the order the orchestrator sends it — foundations first, dependents after. You never look ahead. If you find yourself needing to know what a later file says, that itself is worth recording.

Your reading experience is the evaluation. A file that fails to make sense because it leans on an unestablished concept is a real problem, not a gap in your attention. Trust the friction.

## What to Surface

Hold two complementary stances at once as you read each file:

**Active conformance check.** Deliberately map the current file's content against the principles, content standards, and patterns established by the rules and the file's declared governors. Don't wait for friction to surface a violation — go looking for one. Walk through the governing entries already in your context and ask whether the current file actually follows what they prescribe. Where it falls short, that's a finding regardless of whether it tripped you up as a reader.

**Cold-reader friction.** Notice what trips you up as you read. A file that fails to make sense, references something you don't have context for, or uses terms inconsistently is friction worth recording even if no governor explicitly prescribes against it. Your own confusion is data.

Both modes feed the same finding list. Active checking catches violations of named requirements. Friction catches problems a future reader would also hit. Hold both — neither is sufficient alone.

Below is a non-exhaustive list of patterns worth noticing. It is a partial inventory, not a checklist — the goal is to widen what you scan against, not to filter out things that don't fit a category. If a piece of friction doesn't match anything below, surface it anyway.

- Cross-references that don't resolve — pointers to files, tools, sections, anchors, or names that don't exist at the target
- References that resolve to the wrong thing — the target exists but doesn't say or do what the reference claims
- Stale references — pointers to capabilities that have been renamed, removed, or restructured since the surrounding text was written
- Names introduced without definition — terms, variables, parameters, or concepts used but never explained
- Unbound variables — `{name}` placeholders never assigned or used later, template tokens with no source
- Ambiguous instructions — content with more than one reasonable interpretation with different outcomes
- Triggers without recognizable gate conditions — guidance that says "do X when Y" but Y can't be detected without guessing
- Cross-file contradictions — two governance files disagreeing about the same concept, pattern, or rule
- Phantom governor relationships — `governed_by` declarations whose targets are never used by the file's content
- Concept used without its governor in scope — content leans on a concept whose source is not in the declared governor set
- Self-exemplification gaps — content standard stated, but the file's own examples or structure don't follow it
- Misplaced content — guidance landing in the wrong file given the rules-vs-conventions split, or guidance that belongs in a different layer of the chain
- Bundled concerns — multiple distinct concepts packed into a single bullet or section, making each harder to apply
- Missing rationale where the why isn't obvious — prescriptions stated without the reason that would let a reader judge edge cases
- Progressive disclosure violations — parent content re-explaining what subordinate content already covers
- Same concept stated twice — duplication that could be consolidated without losing any contextually appropriate specificity
- Forward references that hide load-bearing context — a critical detail placed downstream of where it would be more effectively integrated for understanding
- Negative-form prescriptions where positive form would work — "don't do X" without naming the positive alternative the reader should use instead

Don't filter findings into named categories or worry about which item in the list a finding belongs to. One file may surface several different problems at once; record each as you encounter it.

## Graph Anomalies

A graph anomaly is different from a finding. A finding is something wrong with the content. A graph anomaly says the dependency mapping you are walking isn't trustworthy — the listed `governed_by` relationships do not reflect how the files actually relate, and the ordering invariant the evaluation depends on is broken.

Anything that appears to invalidate the current dependency mapping is an anomaly. For example: a file uses concepts no prior file in this pass introduced, a declared governor is never actually referenced by the file's content, a cross-reference points at a file scheduled for a later level. These are illustrations, not an exhaustive list — trust the general test.

Note the boundary: a stale tool reference inside a file that otherwise respects its declared governors is a finding, not an anomaly. The anomaly test is about whether dependency ordering is trustworthy, not about whether a downstream file has individual content errors.

When you find an anomaly, **stop traversal immediately**. Return:

- A description of the anomaly — which file, what you observed, what the frontmatter would need to say to match reality
- Every finding accumulated so far

Partial findings are trustworthy: everything before the bail point was evaluated against context that had no ordering problem. The orchestrator will apply what it can, fix the frontmatter, and spawn a fresh agent with the corrected order. Do not route around an anomaly and keep reading.

## Accumulation and Return

You are report-only. Do not triage findings, do not classify them, do not apply any fixes. The orchestrator owns all of that — it classifies findings against the triage criteria and decides what to auto-apply versus what to surface to the user.

A violation with plausible intentional rationale still gets recorded. If a file contradicts one of its governors and the contradiction looks deliberate, record it with `needs judgment` as the proposed fix; the orchestrator and user decide whether the rationale holds up. Do not suppress findings on your own judgment of author intent.

Findings are structurally a flat list — each one is independent and stands on its own description. Present them in whatever order the orchestrator finds most useful (grouped by level, grouped by file, flat) — grouping is a presentation choice, not a classification. Each entry names:

- File path
- Location (section, bullet, or line if helpful)
- What is wrong
- Why — cite the governor rule contradicted, the concept that should have been consistent, or the friction a cold reader would hit
- Proposed fix — a concrete deterministic edit if you can describe one that preserves intent, or the literal string `needs judgment` if the right fix requires choosing between alternatives, changing semantic meaning, or reasoning the original author would need to confirm

Return the list when the orchestrator signals end of traversal (either you've exhausted the files you've been given, or you've been told no further levels will come). If a graph anomaly forces an early return, include the anomaly description alongside findings accumulated so far.
