# Governance Audit Workflow

Agent workflow for auditing governance files in root-first dependency order. Each call receives one level's files; accumulated context from prior calls stays in scope so later levels can be checked against concepts established earlier.

### Variables

- {level-files} — paths of governance files in the current level to audit

## Process

1. For each {file} in {level-files}:
    1. Read: {file}
    2. Audit {file} holding both stances at once — see Audit Stances:
        - Active conformance check against governors already in context
        - Cold-reader friction encountered while reading
    3. Scan {file} against Patterns to Scan — the list widens attention, it does not filter; record friction that matches nothing in the list the same as any other finding
    4. For each finding: record per Finding Format
2. Return the findings recorded during this call

## Reading Disposition

You start with no prior context beyond this file and the files handed to you. Each governance file joins your context in the order given — foundations first, dependents after. You never look ahead. Needing to know what a later file says is itself worth recording.

Your reading experience is the audit. A file that fails to make sense because it leans on an unestablished concept is a real finding, not a gap in your attention. Trust the friction.

You are report-only — no triage, no classification, no fixes. Classification and application happen after you return. A violation with plausible intentional rationale still gets recorded, with `needs judgment` as the proposed fix. Do not suppress findings on your own read of author intent.

## Audit Stances

Both stances run in parallel against every file and feed the same finding list. Neither is sufficient alone — active checking catches violations of named requirements; friction catches problems a future reader would also hit.

**Active conformance check** — deliberately map the file's content against the principles, content standards, and patterns prescribed by the rules and by the file's declared governors. Walk through each governing entry already in your context and ask whether the current file follows what it prescribes. Shortfalls are findings regardless of whether they tripped you up as a reader.

**Cold-reader friction** — notice what trips you up as you read. A file that fails to make sense, references something you don't have context for, or uses terms inconsistently is friction worth recording even if no governor explicitly prescribes against it. Your own confusion is data.

## Patterns to Scan

Non-exhaustive inventory of patterns worth noticing. Partial inventory, not a checklist — the goal is to widen what you scan against, not filter out things that don't fit a category.

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
- Dependency-mapping misalignments — a file using concepts no prior file introduced, a declared governor never referenced by the file's content, a cross-reference pointing to a later level; correction requires intent decisions, so record with `needs judgment` as the proposed fix

## Finding Format

Findings are a flat list — each stands on its own description. Present in whatever grouping is most useful for the return (by level, by file, flat); grouping is a presentation choice, not a classification.

Each entry names:

- **File path**
- **Location** — section, bullet, or line if helpful
- **What is wrong**
- **Why** — cite the governor rule contradicted, the concept that should have been consistent, or the friction a cold reader would hit
- **Proposed fix** — a concrete deterministic edit when one preserves intent, or the literal string `needs judgment` when the right fix requires choosing between alternatives, changing semantic meaning, or reasoning the original author would need to confirm
