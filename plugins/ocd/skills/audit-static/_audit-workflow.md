# Audit Workflow

Agent workflow for auditing a target's file set in a single holistic pass.

### Variables

- {scope} — `scope_analyze` result with structure `{files: [{path, governance: [convention paths], references: [paths], referenced_by: [paths]}], governance_index, total_files}`. The `files` array is the file set to audit; each file's `governance` list names the conventions that govern it.

## Reading Disposition

You start with no prior context beyond this file and the {scope}. Read each file in {scope}.files in the order given. For each file, also read its matched governance files (named in the file's `governance` list) before reading the file itself, so you have the standards in context when you read.

Your reading experience is the audit. Hold four concerns simultaneously as you read — not as separate passes, but as complementary stances that feed the same finding list:

**Conformity.** Deliberately map each file's content against its matched governance conventions. Walk through each governing entry already in your context and ask whether the file actually follows what it prescribes. Where it falls short, that's a finding regardless of whether it tripped you up as a reader.

**Efficacy.** Can a downstream consumer use this file correctly from cold? For executable workflow files (skills, components, CLI scripts), trace the execution flow: verify every variable is assigned before use, every condition is reachable, every cross-reference resolves, every CLI command is complete and correct. For descriptive files (rules, conventions, docs), check that the file's claims are coherent and self-contained. Issues are gaps between intent and behavior.

**Quality.** Does the file follow structural best practices for its kind? Look for encapsulation gaps, unclear structure, content that should be extracted, unjustified indirection, incomplete commands, missing error paths, and scattered responsibility.

**Prior Art.** Does the approach mirror established patterns for this type of artifact? Are there standard solutions the file reinvents without justification? If the approach deviates from common patterns, is the deviation justified by constraints?

## What to Surface

Below is a non-exhaustive inventory of patterns worth noticing. It is a partial inventory, not a checklist — the goal is to widen what you scan against, not to filter out things that don't fit a category. If a piece of friction doesn't match anything below, surface it anyway.

### Conformity

- Content that contradicts what a matched governance convention prescribes
- Missing required sections or fields documented in governance
- Structure that doesn't follow prescribed patterns
- Self-exemplification gaps — convention stated but the file's own content doesn't follow it

### Efficacy

- Unbound or unassigned variables — referenced but never assigned, or assigned in unreachable branch
- PFN notation errors — If/Else if chain violations, missing colon suffixes, incorrect indentation semantics
- Missing flow control — unreachable steps, branches with no assignment before consumption, missing Else in chains that require it
- Conditions that don't match stated intent — condition text contradicts what surrounding steps expect
- Cross-references to nonexistent targets — step numbers, section names, file paths, CLI commands that don't exist
- Referenced files missing from the file set
- Ambiguity that could produce different outcomes under different execution
- Redundancy that could drift out of sync between source and restated location
- Simplification opportunities where fewer steps could achieve same outcome

### Quality

- Workflow not self-contained — consumer would need to reference sections outside the executable block to execute
- Routing or dispatch that doesn't clearly map every input case — ambiguous fallthrough
- Content that should be extracted to a component file — file approaching size limits or carrying detail a spawned agent doesn't need
- Unjustified delegation — inline execution could achieve the same result
- Incomplete CLI commands — missing interpreter, path, module, or required flags
- Missing error path handling — failure cases with no explicit handling
- Unnecessary indirection — pass-through steps that add no value
- Scattered responsibility — operations that should be single calls assembled as multi-step sequences

### Prior Art

- Structure that doesn't follow standard patterns for this artifact type without justification
- Reinvented infrastructure that existing tools already provide
- Deviations from established patterns without documented constraints or requirements

## Accumulation and Return

You are report-only. Do not triage findings, do not classify them, do not apply any fixes. Classification and application happen after you return — your job is to audit and report.

A violation with plausible intentional rationale still gets recorded. If a file contradicts one of its conventions and the contradiction looks deliberate, record it with `needs judgment` as the proposed fix. Do not suppress findings on your own judgment of author intent.

Findings are a flat list — each entry is independent and stands on its own description. Each entry names:

- File path
- Location (section, bullet, or line if helpful)
- What is wrong
- Why — cite the governance convention contradicted, the PFN rule violated, or the friction a cold reader would hit
- Proposed fix — a concrete deterministic edit if you can describe one that preserves intent, or the literal string `needs judgment` if the right fix requires choosing between alternatives, changing semantic meaning, or reasoning the original author would need to confirm

Return the list when you have read and audited every file in the scope.
